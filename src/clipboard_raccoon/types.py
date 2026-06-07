from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InputFile:
    path: str
    role: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    path: str
    role: str
    heading_path: list[str]
    start_line: int
    end_line: int
    text: str
    sha256: str


@dataclass(frozen=True)
class CandidateClaim:
    claim_id: str
    claim_text: str
    source_file: str
    source_location: str
    source_chunk_id: str
    start_line: int | None
    end_line: int | None


@dataclass(frozen=True)
class ClassifiedClaim:
    claim: CandidateClaim
    claim_type: str
    claim_domain: str
    claim_importance: str
    extraction_quality: str
    claim_surface_status: str
    required_evidence: list[str]
    requires_external_environment: bool


@dataclass(frozen=True)
class ManifestSelection:
    input_files: list[InputFile]
    warnings: list[str]
