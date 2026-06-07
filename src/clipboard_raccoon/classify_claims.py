from __future__ import annotations

import re

from .types import CandidateClaim, ClassifiedClaim


REQUIRED_EVIDENCE: dict[str, list[str]] = {
    "capability_claim": [
        "implementation",
        "usage example",
        "test or demonstration",
        "documentation describing boundaries",
    ],
    "metric_claim": [
        "metric file or report",
        "evaluation protocol",
        "dataset/split description",
        "training or evaluation config",
        "model artifact or checkpoint hash if reproduction is claimed",
    ],
    "runtime_claim": [
        "runtime implementation",
        "configuration",
        "example output or trace",
        "smoke test",
        "environment notes",
    ],
    "architecture_claim": [
        "source tree evidence",
        "module files",
        "architecture documentation",
        "interfaces/contracts",
    ],
    "generalisation_claim": [
        "external validation",
        "real-world data",
        "cross-domain evaluation",
        "limitations/caveats",
    ],
    "bounded_non_claim": [
        "clear limiting statement",
        "scope note",
        "non-goals section",
    ],
    "process_claim": [
        "incident report",
        "review notes",
        "trace-backed analysis",
        "commit history or linked artifact",
    ],
    "adoption_usability_claim": [
        "setup instructions",
        "examples",
        "tests",
        "review guide",
        "documented workflow",
    ],
    "other_claim": [
        "direct supporting documentation",
        "supporting artifact",
    ],
}


def classify_claims(claims: list[CandidateClaim]) -> list[ClassifiedClaim]:
    return [classify_claim(claim) for claim in claims]


def classify_claim(claim: CandidateClaim) -> ClassifiedClaim:
    text = claim.claim_text.lower()
    claim_type = _claim_type(text)
    requires_external = _requires_external_environment(text)
    surface = _claim_surface_status(text, claim_type, requires_external)
    return ClassifiedClaim(
        claim=claim,
        claim_type=claim_type,
        claim_surface_status=surface,
        required_evidence=list(REQUIRED_EVIDENCE[claim_type]),
        requires_external_environment=requires_external,
    )


def _claim_type(text: str) -> str:
    if re.search(r"\b\d+(?:\.\d+)?\b", text) and re.search(
        r"\b(mae|rmse|f1|accuracy|loss|latency|%|fps|m|ms|s)\b", text
    ):
        return "metric_claim"
    if re.search(r"\b(mae|rmse|f1|accuracy|loss|latency)\b", text):
        return "metric_claim"
    if re.search(r"\b(generalizes?|generalises?|transfers?|real-world|production|robust)\b", text):
        return "generalisation_claim"
    if re.search(r"\b(not|does not|limited|non-goal|out of scope|not intended to)\b", text):
        return "bounded_non_claim"
    if re.search(r"\b(runtime|live|trace|deployment|runs|loads|service|hardware)\b", text):
        return "runtime_claim"
    if re.search(r"\b(architecture|pipeline|module|component|separates?|interface|contract)\b", text):
        return "architecture_claim"
    if re.search(r"\b(reviewed|investigated|evaluated|validated|tested)\b", text):
        return "process_claim"
    if re.search(r"\b(can|supports?|allows?|estimates?|detects?|predicts?|provides?|enables?|implements?)\b", text):
        return "capability_claim"
    if re.search(r"\b(usable|reviewable|maintainable|easy|simple)\b", text):
        return "adoption_usability_claim"
    return "other_claim"


def _requires_external_environment(text: str) -> bool:
    return bool(
        re.search(
            r"\b(hardware|camera|sensor|physical|deployment|deployed|production|credentials|external service|real-world)\b",
            text,
        )
    )


def _claim_surface_status(text: str, claim_type: str, requires_external: bool) -> str:
    if requires_external:
        return "requires_external_environment"
    if claim_type in {"metric_claim", "generalisation_claim", "runtime_claim"}:
        return "high_claim_surface"
    if claim_type == "capability_claim" and re.search(
        r"\b(can|supports?|estimates?|detects?|predicts?|implements?)\b", text
    ):
        return "high_claim_surface"
    if claim_type in {"architecture_claim", "process_claim"}:
        return "medium_claim_surface"
    if claim_type in {"adoption_usability_claim", "other_claim"}:
        return "low_claim_surface"
    return "medium_claim_surface"

