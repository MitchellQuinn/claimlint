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


def extract_claims(chunks: list[DocumentChunk]) -> list[CandidateClaim]:
    candidates: list[tuple[str, str, str, str, int, int]] = []
    seen: set[str] = set()

    for chunk in chunks:
        for text, start_line, end_line in _candidate_texts(chunk):
            normalized = _normalize_claim(text)
            if normalized in seen or not _looks_like_claim(text):
                continue
            seen.add(normalized)
            location = _source_location(chunk, start_line, end_line)
            candidates.append((text, chunk.path, location, chunk.chunk_id, start_line, end_line))

    claims: list[CandidateClaim] = []
    for index, (text, path, location, chunk_id, start_line, end_line) in enumerate(candidates, start=1):
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
            )
        )
    return claims


def _candidate_texts(chunk: DocumentChunk) -> list[tuple[str, int, int]]:
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
            if not CLAIM_SIGNAL_RE.search(stripped) and not METRIC_RE.search(stripped):
                continue
            stripped = stripped.lstrip("#").strip()
        stripped = LEADING_MARKER_RE.sub("", stripped).strip()
        if not stripped or stripped.endswith(":"):
            continue
        for sentence in SENTENCE_SPLIT_RE.split(stripped):
            sentence = sentence.strip()
            if 12 <= len(sentence) <= 500:
                items.append((sentence, line_no, line_no))
    return items


def _looks_like_claim(text: str) -> bool:
    lowered = text.lower()
    if lowered.startswith(("install ", "run ", "pip ", "python ", "usage:", "example:")):
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

