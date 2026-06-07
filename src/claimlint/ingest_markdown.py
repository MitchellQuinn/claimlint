from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .types import DocumentChunk, InputFile


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TEXT_LINE_CHUNK_SIZE = 80


def ingest_files(repo_path: str | Path, input_files: list[InputFile]) -> list[DocumentChunk]:
    repo = Path(repo_path).resolve()
    chunks: list[DocumentChunk] = []
    for input_file in input_files:
        path = repo / input_file.path
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() == ".md":
            chunks.extend(_chunk_markdown(input_file, text))
        else:
            chunks.extend(_chunk_by_line_range(input_file, text))
    return chunks


def _chunk_markdown(input_file: InputFile, text: str) -> list[DocumentChunk]:
    lines = text.splitlines()
    sections: list[tuple[int, int, list[str], list[str]]] = []
    heading_stack: list[tuple[int, str]] = []
    current_start = 1
    current_heading_path: list[str] = []
    current_lines: list[str] = []

    def flush(end_line: int) -> None:
        nonlocal current_lines, current_start, current_heading_path
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            sections.append((current_start, end_line, list(current_heading_path), list(current_lines)))
        current_lines = []

    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            flush(index - 1)
            level = len(match.group(1))
            title = match.group(2).strip()
            heading_stack = [(h_level, h_title) for h_level, h_title in heading_stack if h_level < level]
            heading_stack.append((level, title))
            current_heading_path = [h_title for _, h_title in heading_stack]
            current_start = index
            current_lines = [line]
            continue
        if not current_lines:
            current_start = index
            current_heading_path = [title for _, title in heading_stack]
        current_lines.append(line)

    flush(len(lines) or 1)
    return [_make_chunk(input_file, start, end, headings, chunk_lines) for start, end, headings, chunk_lines in sections]


def _chunk_by_line_range(input_file: InputFile, text: str) -> list[DocumentChunk]:
    lines = text.splitlines()
    if not lines:
        return []
    chunks: list[DocumentChunk] = []
    for start_index in range(0, len(lines), TEXT_LINE_CHUNK_SIZE):
        chunk_lines = lines[start_index : start_index + TEXT_LINE_CHUNK_SIZE]
        start_line = start_index + 1
        end_line = start_index + len(chunk_lines)
        chunks.append(_make_chunk(input_file, start_line, end_line, [], chunk_lines))
    return chunks


def _make_chunk(
    input_file: InputFile,
    start_line: int,
    end_line: int,
    heading_path: list[str],
    lines: list[str],
) -> DocumentChunk:
    text = "\n".join(lines).strip()
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    chunk_key = f"{input_file.path}:{start_line}:{end_line}:{text_hash}"
    chunk_id = f"chunk_{hashlib.sha256(chunk_key.encode('utf-8')).hexdigest()[:16]}"
    return DocumentChunk(
        chunk_id=chunk_id,
        path=input_file.path,
        role=input_file.role,
        heading_path=heading_path,
        start_line=start_line,
        end_line=end_line,
        text=text,
        sha256=text_hash,
    )

