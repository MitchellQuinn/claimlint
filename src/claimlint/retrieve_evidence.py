from __future__ import annotations

import re
from collections import Counter

from .types import ClassifiedClaim, DocumentChunk


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "with",
    "by",
    "from",
    "this",
    "that",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "it",
    "on",
    "at",
    "if",
    "but",
}
TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")


def retrieve_evidence(
    classified_claim: ClassifiedClaim,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[dict]:
    claim = classified_claim.claim
    query_tokens = tokenize(
        claim.claim_text + " " + " ".join(classified_claim.required_evidence)
    )
    claim_tokens = tokenize(claim.claim_text)
    scored: list[tuple[float, DocumentChunk, list[str]]] = []

    for chunk in chunks:
        if not chunk.use_as_evidence:
            continue
        if chunk.chunk_id == claim.source_chunk_id:
            continue
        chunk_tokens = tokenize(chunk.text + " " + " ".join(chunk.heading_path))
        if not chunk_tokens:
            continue
        overlap = sorted(set(query_tokens) & set(chunk_tokens))
        claim_overlap = set(claim_tokens) & set(chunk_tokens)
        if not overlap and not claim_overlap:
            continue
        score = _score(
            classified_claim.claim_type,
            chunk,
            query_tokens,
            claim_tokens,
            chunk_tokens,
        )
        if score > 0:
            scored.append((score, chunk, overlap))

    scored.sort(key=lambda item: (-item[0], item[1].path, item[1].start_line))
    return [
        _evidence_object(score, chunk, matched_terms)
        for score, chunk, matched_terms in scored[:top_k]
    ]


def tokenize(text: str) -> list[str]:
    normalized = text.lower().replace("_", " ").replace("-", " ")
    tokens = TOKEN_RE.findall(normalized)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def _score(
    claim_type: str,
    chunk: DocumentChunk,
    query_tokens: list[str],
    claim_tokens: list[str],
    chunk_tokens: list[str],
) -> float:
    query_counter = Counter(query_tokens)
    chunk_counter = Counter(chunk_tokens)
    query_overlap = sum(min(count, chunk_counter[token]) for token, count in query_counter.items())
    claim_overlap = len(set(claim_tokens) & set(chunk_tokens))
    query_denominator = max(1, len(set(query_tokens)))
    claim_denominator = max(1, len(set(claim_tokens)))
    score = (query_overlap / query_denominator * 0.35) + (
        claim_overlap / claim_denominator * 0.65
    )
    score += _role_boost(claim_type, chunk)
    return round(min(score, 1.0), 4)


def _role_boost(claim_type: str, chunk: DocumentChunk) -> float:
    role = chunk.role.lower()
    path = chunk.path.lower()
    boost = 0.0
    if claim_type == "metric_claim" and (
        "metric" in role or "/metrics/" in f"/{path}" or path.endswith(".json")
    ):
        boost += 0.25
    if claim_type == "runtime_claim" and any(term in role or term in path for term in ["config", "trace", "runtime"]):
        boost += 0.15
    if claim_type == "architecture_claim" and any(term in role or term in path for term in ["doc", "src", "architecture"]):
        boost += 0.12
    if claim_type == "process_claim" and any(term in role or term in path for term in ["incident", "report", "trace"]):
        boost += 0.15
    if claim_type == "capability_claim" and path.endswith((".py", ".md")):
        boost += 0.08
    return boost


def _evidence_object(score: float, chunk: DocumentChunk, matched_terms: list[str]) -> dict:
    matched = ", ".join(matched_terms[:8]) or "overlapping terms"
    location = _location(chunk)
    return {
        "path": chunk.path,
        "source_role": chunk.source_role,
        "location": location,
        "summary": f"Candidate evidence from {chunk.path}, lines {chunk.start_line}-{chunk.end_line}, matched terms: {matched}.",
        "strength": _strength(score, chunk.text),
        "evidence_type": _evidence_type(chunk),
        "snippet": _snippet(chunk.text),
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "score": score,
    }


def _strength(score: float, text: str) -> str:
    lowered = text.lower()
    if re.search(r"\b(does not|not supported|unsupported|failed|cannot|no evidence)\b", lowered):
        return "contradictory"
    if score >= 0.45:
        return "strong"
    if score >= 0.25:
        return "moderate"
    if score > 0:
        return "weak"
    return "unclear"


def _evidence_type(chunk: DocumentChunk) -> str:
    role = chunk.role.lower()
    path = chunk.path.lower()
    if "metric" in role or "/metrics/" in f"/{path}" or path.endswith(".csv"):
        return "metric"
    if "config" in role or path.endswith((".yml", ".yaml", ".toml")):
        return "config"
    if "incident" in role:
        return "incident_report"
    if "trace" in role or "trace" in path:
        return "trace"
    if path.endswith(".py") or "src/" in path:
        return "implementation"
    if "test" in role or "/tests/" in f"/{path}":
        return "test"
    if "model" in path and any(term in path for term in ["checkpoint", "ckpt", "weights"]):
        return "model_artifact"
    if path.endswith(".json") and "manifest" in path:
        return "manifest"
    if path.endswith((".md", ".txt")):
        return "documentation"
    return "other"


def _location(chunk: DocumentChunk) -> str:
    heading = " > ".join(chunk.heading_path) if chunk.heading_path else "line range"
    return f"section: {heading}; lines {chunk.start_line}-{chunk.end_line}"


def _snippet(text: str, max_chars: int = 320) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
