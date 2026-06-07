from __future__ import annotations

import hashlib
import re

from .types import CandidateClaim, DocumentChunk


CLAIM_SIGNAL_RE = re.compile(
    r"\b("
    r"can|supports?|provides?|allows?|enables?|implements?|detects?|estimates?|predicts?|"
    r"achieved|achieves|accuracy|mae|rmse|f1|loss|latency|validated|evaluated|tested|"
    r"separates?|pipeline|modules?|components?|contracts?|interfaces?|"
    r"generalizes?|generalises?|transfers?|real-world|production|robust|"
    r"license|licensed|copyright|rights?|permission|grant|redistribut(?:e|ed|ion)?|"
    r"released?|required|requires?|must|should|policy|standard|"
    r"not|does not|limited to|out of scope|not intended to|reviewable|maintainable|usable"
    r")\b",
    re.IGNORECASE,
)
METRIC_RE = re.compile(
    r"(\b\d+(?:\.\d+)?\s*(?:%|m|ms|s|fps|mae|rmse|f1|accuracy|loss)\b|"
    r"\b(?:mae|rmse|f1|accuracy|loss|latency)\b)",
    re.IGNORECASE,
)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
LEADING_MARKER_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
MARKDOWN_EXTENSIONS = (".md", ".txt")
NON_CLAIM_CODE_RE = re.compile(
    r"^\s*(raise|return|except|if|elif|else|for|while|with|try|def|class|import|from)\b",
    re.IGNORECASE,
)
ASSIGNMENT_RE = re.compile(r"^\s*[a-zA-Z_][\w.]*\s*=")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


def extract_claims(chunks: list[DocumentChunk]) -> list[CandidateClaim]:
    candidates: list[tuple[str, str, str, str, int, int, str]] = []
    seen: set[str] = set()

    for chunk in chunks:
        if not chunk.extract_claims:
            continue
        for text, start_line, end_line in _candidate_texts(chunk):
            normalized = _normalize_claim(text)
            if normalized in seen or not _looks_like_claim(text):
                continue
            seen.add(normalized)
            location = _source_location(chunk, start_line, end_line)
            candidates.append(
                (
                    text,
                    chunk.path,
                    location,
                    chunk.chunk_id,
                    start_line,
                    end_line,
                    chunk.source_role,
                )
            )

    claims: list[CandidateClaim] = []
    for index, (
        text,
        path,
        location,
        chunk_id,
        start_line,
        end_line,
        source_role,
    ) in enumerate(candidates, start=1):
        stable = hashlib.sha256(f"{path}:{start_line}:{text}".encode("utf-8")).hexdigest()[:8]
        claims.append(
            CandidateClaim(
                claim_id=f"claim_{index:03d}_{stable}",
                claim_text=text,
                source_file=path,
                source_location=location,
                source_chunk_id=chunk_id,
                start_line=start_line,
                end_line=end_line,
                source_role=source_role,
            )
        )
    return claims


def _candidate_texts(chunk: DocumentChunk) -> list[tuple[str, int, int]]:
    if chunk.path.lower().endswith(MARKDOWN_EXTENSIONS):
        return _markdown_candidate_texts(chunk)
    return _line_candidate_texts(chunk)


def _markdown_candidate_texts(chunk: DocumentChunk) -> list[tuple[str, int, int]]:
    items: list[tuple[str, int, int]] = []
    in_fence = False
    block_lines: list[str] = []
    block_start = chunk.start_line
    block_end = chunk.start_line

    def flush_block() -> None:
        nonlocal block_lines, block_start, block_end
        if not block_lines:
            return
        text = _clean_markdown_block(block_lines)
        _append_sentences(items, text, block_start, block_end, chunk.path)
        block_lines = []

    for offset, raw_line in enumerate(chunk.text.splitlines()):
        line_no = chunk.start_line + offset
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            flush_block()
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            flush_block()
            continue
        if stripped.startswith("#"):
            flush_block()
            heading = stripped.lstrip("#").strip()
            if _is_heading_claim(heading):
                _append_sentences(items, heading, line_no, line_no, chunk.path)
            continue
        if _is_table_line(stripped):
            flush_block()
            continue
        if LEADING_MARKER_RE.match(stripped):
            flush_block()
            block_start = line_no
            block_end = line_no
            block_lines = [stripped]
            continue
        if not block_lines:
            block_start = line_no
            block_lines = [stripped]
        else:
            block_lines.append(stripped)
        block_end = line_no
    flush_block()
    return items


def _line_candidate_texts(chunk: DocumentChunk) -> list[tuple[str, int, int]]:
    items: list[tuple[str, int, int]] = []
    in_fence = False
    for offset, raw_line in enumerate(chunk.text.splitlines()):
        line_no = chunk.start_line + offset
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        stripped = LEADING_MARKER_RE.sub("", stripped).strip()
        _append_sentences(items, stripped, line_no, line_no, chunk.path)
    return items


def _append_sentences(
    items: list[tuple[str, int, int]],
    text: str,
    start_line: int,
    end_line: int,
    source_file: str,
) -> None:
    if not text or text.endswith(":"):
        return
    for sentence in SENTENCE_SPLIT_RE.split(text):
        sentence = sentence.strip()
        if 12 <= len(sentence) <= 500 and _looks_like_claim(sentence, source_file):
            items.append((sentence, start_line, end_line))


def _looks_like_claim(text: str, source_file: str = "") -> bool:
    lowered = text.lower()
    if lowered.startswith(("install ", "run ", "pip ", "python ", "usage:", "example:")):
        return False
    if _is_table_line(text) or _is_non_claim_code_line(text, source_file):
        return False
    if _is_incomplete_fragment(text):
        return False
    if _is_heading_noise(text):
        return False
    if len(text.split()) < 4 and not METRIC_RE.search(text):
        return False
    return bool(CLAIM_SIGNAL_RE.search(text) or METRIC_RE.search(text))


def _normalize_claim(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def _source_location(chunk: DocumentChunk, start_line: int, end_line: int) -> str:
    heading = " > ".join(chunk.heading_path) if chunk.heading_path else "unheaded"
    if start_line == end_line:
        return f"section: {heading}; line {start_line}"
    return f"section: {heading}; lines {start_line}-{end_line}"


def _clean_markdown_block(lines: list[str]) -> str:
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        stripped = LEADING_MARKER_RE.sub("", stripped).strip()
        stripped = stripped.lstrip(">").strip()
        if stripped:
            cleaned.append(stripped)
    return re.sub(r"\s+", " ", " ".join(cleaned)).strip()


def _is_table_line(text: str) -> bool:
    stripped = text.strip()
    if TABLE_SEPARATOR_RE.fullmatch(stripped):
        return True
    if "|" not in stripped:
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if len(cells) < 2:
        return False
    if not (stripped.startswith("|") or stripped.endswith("|")):
        return False
    return not any(CLAIM_SIGNAL_RE.search(cell) or METRIC_RE.search(cell) for cell in cells)


def _is_heading_claim(text: str) -> bool:
    if _is_heading_noise(text):
        return False
    return bool(CLAIM_SIGNAL_RE.search(text) or METRIC_RE.search(text))


def _is_heading_noise(text: str) -> bool:
    stripped = text.strip()
    if stripped.endswith(":"):
        return True
    if re.search(r"[.!?]$", stripped):
        return False
    words = stripped.split()
    if len(words) <= 7 and not re.search(
        r"\b(achieved|achieves|is|are|was|were|does|can|supports?|provides?)\b",
        stripped,
        re.IGNORECASE,
    ):
        return True
    return False


def _is_incomplete_fragment(text: str) -> bool:
    lowered = text.lower().strip("`*_ ")
    return bool(
        re.search(r"\b(the|a|an|and|or|of|to|for|with|in|under|into|from|by)$", lowered)
        or re.search(r"^\s*[)\]},]\s*,?\s*$", text)
    )


def _is_non_claim_code_line(text: str, source_file: str) -> bool:
    if source_file.lower().endswith(MARKDOWN_EXTENSIONS):
        return False
    if NON_CLAIM_CODE_RE.search(text):
        return True
    if ASSIGNMENT_RE.search(text) and not METRIC_RE.search(text):
        return True
    return bool(re.search(r"\b(noqa|traceback|valueerror|runtimeerror|filenotfounderror|assertionerror)\b", text.lower()))
