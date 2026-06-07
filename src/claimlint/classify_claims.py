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


BOUNDED_DOMAIN_EVIDENCE: dict[str, list[str]] = {
    "licensing_rights": [
        "rights or license notice",
        "source attribution",
        "scope of granted permissions",
    ],
    "dataset_redistribution": [
        "dataset attribution or source notice",
        "redistribution scope statement",
        "repository contents matching distribution claim",
    ],
    "artifact_distribution": [
        "artifact availability statement",
        "repository contents matching distribution claim",
        "scope note",
    ],
    "generalisation_scope": [
        "scope/caveat statement",
        "evidence boundary",
        "limitations section",
    ],
    "documentation_policy": [
        "policy or standard document",
        "required artifact description",
        "scope of instruction",
    ],
}

SUPPRESSED_EXTRACTION_QUALITIES = {
    "bounded_context",
    "policy_statement",
    "frontmatter_metadata",
    "roadmap_statement",
    "boundary_statement",
    "taxonomy_definition",
    "verdict_rule_definition",
    "schema_definition",
    "workflow_instruction",
    "runtime_instruction",
    "adapter_instruction",
    "heading_label",
    "table_header",
    "incomplete_fragment",
    "code_or_config_fragment",
}

LOW_QUALITY_EXTRACTIONS = {
    "heading_or_label",
    "heading_label",
    "table_header",
    "incomplete_fragment",
    "code_or_error_fragment",
    "code_or_config_fragment",
    "metric_data_point",
    "other_low_quality",
}
NON_AUDITABLE_EXTRACTION_QUALITIES = LOW_QUALITY_EXTRACTIONS | SUPPRESSED_EXTRACTION_QUALITIES


def classify_claims(claims: list[CandidateClaim]) -> list[ClassifiedClaim]:
    return [classify_claim(claim) for claim in claims]


def classify_claim(claim: CandidateClaim) -> ClassifiedClaim:
    text = claim.claim_text.lower()
    claim_type = _claim_type(text)
    requires_external = _requires_external_environment(text)
    extraction_quality = _extraction_quality(claim, claim_type)
    claim_domain = _claim_domain(text, claim_type, extraction_quality, claim.source_file)
    surface = _claim_surface_status(
        text,
        claim_type,
        requires_external,
        extraction_quality,
        claim.source_role,
    )
    claim_importance = _claim_importance(
        claim_type,
        claim_domain,
        extraction_quality,
        surface,
        claim.source_role,
    )
    return ClassifiedClaim(
        claim=claim,
        claim_type=claim_type,
        claim_domain=claim_domain,
        claim_importance=claim_importance,
        extraction_quality=extraction_quality,
        claim_surface_status=surface,
        required_evidence=_required_evidence(
            claim_type,
            claim_domain,
            extraction_quality,
            claim.source_role,
        ),
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
    if re.search(
        r"\b(not|does not|limited|non-goal|out of scope|not intended to|without an open-source license)\b",
        text,
    ):
        return "bounded_non_claim"
    if re.search(r"\b(runtime|live|trace|deployment|runs|loads|service|hardware)\b", text):
        return "runtime_claim"
    if re.search(r"\b(architecture|pipeline|modules?|components?|separates?|interface|contract)\b", text):
        return "architecture_claim"
    if re.search(r"\b(reviewed|investigated|evaluated|validated|tested)\b", text):
        return "process_claim"
    if re.search(r"\b(can|supports?|allows?|estimates?|detects?|predicts?|provides?|enables?|implements?)\b", text):
        return "capability_claim"
    if re.search(r"\b(usable|reviewable|maintainable|easy|simple)\b", text):
        return "adoption_usability_claim"
    return "other_claim"


def _claim_domain(
    text: str,
    claim_type: str,
    extraction_quality: str,
    source_file: str,
) -> str:
    source = source_file.lower()
    if _is_dataset_distribution_statement(text):
        return "dataset_redistribution"
    if _is_artifact_distribution_statement(text):
        return "artifact_distribution"
    if re.search(
        r"\b(license|licensed|copyright|rights?|permission|grant|all rights reserved|open-source)\b",
        text,
    ):
        return "licensing_rights"
    if _is_generalisation_or_scope_statement(text, claim_type):
        return "generalisation_scope"
    if _is_documentation_policy_statement(text, source):
        return "documentation_policy"
    if claim_type == "metric_claim":
        return "model_performance"
    if claim_type == "runtime_claim":
        return "runtime_behavior"
    if claim_type == "architecture_claim":
        return "architecture"
    if claim_type == "process_claim" or re.search(r"\b(traceability|incident|review|investigated)\b", text):
        return "process_traceability"
    if claim_type == "adoption_usability_claim":
        return "adoption_usability"
    if claim_type == "capability_claim":
        return "technical_capability"
    if extraction_quality == "policy_statement":
        return "documentation_policy"
    if re.search(
        r"\b(metric|accuracy|mae|rmse|f1|loss|validation|evaluation|training)\b",
        text,
    ):
        return "model_performance"
    return "other"


def _claim_importance(
    claim_type: str,
    claim_domain: str,
    extraction_quality: str,
    claim_surface_status: str,
    source_role: str,
) -> str:
    if source_role != "claim_source":
        return "low"
    if extraction_quality in NON_AUDITABLE_EXTRACTION_QUALITIES:
        return "low"
    if claim_surface_status == "requires_external_environment":
        return "high"
    if claim_domain in {
        "licensing_rights",
        "dataset_redistribution",
        "artifact_distribution",
        "model_performance",
        "generalisation_scope",
    }:
        return "high"
    if claim_type in {"runtime_claim", "architecture_claim", "process_claim"}:
        return "medium"
    if claim_domain == "documentation_policy":
        return "medium"
    if claim_type == "capability_claim" and claim_surface_status == "high_claim_surface":
        return "medium"
    return "low"


def _extraction_quality(claim: CandidateClaim, claim_type: str) -> str:
    text = claim.claim_text.strip()
    lowered = text.lower()
    source = claim.source_file.lower()

    source_quality = _source_role_extraction_quality(claim.source_role, source)
    if source_quality:
        return source_quality
    if _is_frontmatter_metadata(claim, source):
        return "frontmatter_metadata"
    if _is_roadmap_statement(lowered):
        return "roadmap_statement"
    if _is_boundary_statement(lowered):
        return "boundary_statement"
    if _is_table_header(text):
        return "table_header"
    if _is_code_or_error_fragment(text, source):
        return "code_or_config_fragment"
    if _is_metric_data_point(text, source):
        return "metric_data_point"
    if _is_incomplete_fragment(text):
        return "incomplete_fragment"
    if _is_heading_or_label(text):
        return "heading_label"
    if _is_documentation_policy_statement(lowered, source):
        return "policy_statement"
    if claim_type == "bounded_non_claim":
        if _is_generalisation_or_scope_statement(lowered, claim_type):
            return "caveat_or_scope_note"
        return "boundary_statement"
    return "auditable_claim"


def _source_role_extraction_quality(source_role: str, source_file: str) -> str | None:
    source_role = source_role.lower()
    source_file = source_file.lower()
    if source_role == "schema_reference":
        return "schema_definition"
    if source_role == "workflow_contract":
        return "workflow_instruction"
    if source_role == "runtime_contract":
        return "runtime_instruction"
    if source_role == "adapter_contract":
        return "adapter_instruction"
    if source_role == "reference_only":
        if "verdict" in source_file:
            return "verdict_rule_definition"
        if "taxonomy" in source_file:
            return "taxonomy_definition"
    return None


def _required_evidence(
    claim_type: str,
    claim_domain: str,
    extraction_quality: str,
    source_role: str,
) -> list[str]:
    if source_role != "claim_source":
        return []
    if extraction_quality in NON_AUDITABLE_EXTRACTION_QUALITIES:
        return []
    if claim_type == "bounded_non_claim" and claim_domain in BOUNDED_DOMAIN_EVIDENCE:
        return list(BOUNDED_DOMAIN_EVIDENCE[claim_domain])
    return list(REQUIRED_EVIDENCE[claim_type])


def _requires_external_environment(text: str) -> bool:
    return bool(
        re.search(
            r"\b(hardware|camera|sensor|physical|deployment|deployed|production|credentials|external service|real-world)\b",
            text,
        )
    )


def _claim_surface_status(
    text: str,
    claim_type: str,
    requires_external: bool,
    extraction_quality: str,
    source_role: str,
) -> str:
    if source_role != "claim_source":
        return "low_claim_surface"
    if extraction_quality in NON_AUDITABLE_EXTRACTION_QUALITIES:
        return "low_claim_surface"
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


def _is_dataset_distribution_statement(text: str) -> bool:
    return bool(
        re.search(r"\b(dataset|mimii|third-party audio|audio assets?|training data|source data)\b", text)
        and re.search(
            r"\b(redistribut(?:e|ed|es|ing|ion)?|distribut(?:e|ed|es|ing|ion)?|include|exclude|not released|not provided|does not include)\b",
            text,
        )
    )


def _is_artifact_distribution_statement(text: str) -> bool:
    return bool(
        re.search(
            r"\b(artifact|model weights?|checkpoint|tensor corpora?|shards?|manifest snapshots?|prediction exports?|notebook outputs?)\b",
            text,
        )
        and re.search(
            r"\b(redistribut(?:e|ed|es|ing|ion)?|distribut(?:e|ed|es|ing|ion)?|released?|provided|include|exclude|available)\b",
            text,
        )
    )


def _is_generalisation_or_scope_statement(text: str, claim_type: str) -> bool:
    return claim_type == "generalisation_claim" or bool(
        re.search(
            r"\b(generalizes?|generalises?|transfers?|real-world|production|robust|general-purpose|scope|limited|out of scope|not intended)\b",
            text,
        )
    )


def _is_documentation_policy_statement(text: str, source_file: str) -> bool:
    if re.search(r"\b(policy|standard|instruction|required fields?|must include|must provide|must be|should include)\b", text):
        return True
    return "standard" in source_file or "policy" in source_file


def _is_metric_data_point(text: str, source_file: str) -> bool:
    if not source_file.endswith((".json", ".csv")):
        return False
    return bool(
        re.search(r'^\s*"[^"]+"\s*:\s*-?\d+(?:\.\d+)?\s*,?\s*$', text)
        or re.search(r'^\s*"[^"]+"\s*:\s*\[\s*$', text)
        or re.search(r"^\s*-?\d+(?:\.\d+)?\s*,?\s*$", text)
    )


def _is_code_or_error_fragment(text: str, source_file: str) -> bool:
    if source_file.endswith((".md", ".txt")):
        return False
    return bool(
        re.search(
            r"^\s*(raise|return|except|if|elif|else|for|while|with|try|def|class|import|from)\b",
            text,
        )
        or re.search(r"\b(noqa|traceback|valueerror|runtimeerror|filenotfounderror|assertionerror)\b", text.lower())
        or re.search(r"^\s*[a-zA-Z_][\w.]*\s*=", text)
    )


def _is_incomplete_fragment(text: str) -> bool:
    lowered = text.lower().strip("`*_ ")
    return bool(
        len(text.split()) < 5
        or re.search(r"\b(the|a|an|and|or|of|to|for|with|in|under|into|from|by)$", lowered)
    )


def _is_heading_or_label(text: str) -> bool:
    if text.endswith(":"):
        return True
    if re.search(r"[.!?]$", text):
        return False
    words = text.split()
    if len(words) <= 7 and not re.search(r"\b(achieved|achieves|is|are|was|were|does|can|supports?|provides?)\b", text.lower()):
        return True
    return bool(re.fullmatch(r"[A-Z0-9_ ./()&:-]+", text) and len(words) <= 10)


def _is_table_header(text: str) -> bool:
    stripped = text.strip()
    if "|" not in stripped:
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return len(cells) >= 2 and all(cell and len(cell.split()) <= 4 for cell in cells)


def _is_frontmatter_metadata(claim: CandidateClaim, source_file: str) -> bool:
    if not source_file.endswith(".md"):
        return False
    if claim.start_line is None or claim.start_line > 8:
        return False
    text = claim.claim_text.strip().lower()
    if text.startswith("---") and re.search(r"\b(name|description|title|version|author|tags):", text):
        return True
    return bool(
        re.search(r"\b(name|description|title|version|author|tags):", text)
        and ("skill.md" in source_file or claim.start_line <= 3)
    )


def _is_roadmap_statement(text: str) -> bool:
    if re.search(r"\b(now|currently|already|implemented|available)\b", text):
        return False
    return bool(
        re.search(
            r"\b(future work|roadmap|planned|later stage|may add|might add|will add|could add|not part of v\d+(?:\.\d+)*)\b",
            text,
        )
    )


def _is_boundary_statement(text: str) -> bool:
    return bool(
        re.search(
            r"\b("
            r"do not|must not|should not|does not|not a|not an|not intended|not exhaustive|"
            r"out of scope|non-goals?|non-goal|without an open-source license|"
            r"silently modify|"
            r"do not claim|do not imply|do not present"
            r")\b",
            text,
        )
    )
