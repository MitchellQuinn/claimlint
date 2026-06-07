from __future__ import annotations

import re

from .types import ClassifiedClaim


NON_AUDITABLE_EXTRACTION_QUALITIES = {
    "taxonomy_definition",
    "verdict_rule_definition",
    "schema_definition",
    "workflow_instruction",
    "runtime_instruction",
    "adapter_instruction",
    "heading_or_label",
    "heading_label",
    "table_header",
    "incomplete_fragment",
    "code_or_error_fragment",
    "code_or_config_fragment",
    "metric_data_point",
    "other_low_quality",
}


def build_claim_record(classified: ClassifiedClaim, found_evidence: list[dict]) -> dict:
    missing_evidence = _missing_evidence(classified, found_evidence)
    artifact_gaps = _artifact_gaps(classified, missing_evidence, found_evidence)
    verification_mode = _verification_mode(classified, found_evidence, missing_evidence)
    verdict = _verdict(classified, found_evidence, missing_evidence)
    confidence = _confidence(verdict, found_evidence, missing_evidence)
    remediation = _recommended_remediation(classified, missing_evidence, artifact_gaps, verdict)
    risk = _risk(verdict, classified, missing_evidence, artifact_gaps)
    review_action = _review_action(classified, verdict)
    claim = classified.claim

    return {
        "claim_id": claim.claim_id,
        "claim_text": claim.claim_text,
        "claim_type": classified.claim_type,
        "claim_domain": classified.claim_domain,
        "claim_importance": classified.claim_importance,
        "review_action": review_action,
        "extraction_quality": classified.extraction_quality,
        "claim_surface_status": classified.claim_surface_status,
        "source_file": claim.source_file,
        "source_role": claim.source_role,
        "source_location": claim.source_location,
        "is_auditable_claim": _is_auditable_claim(classified),
        "verification_mode": verification_mode,
        "requires_external_environment": classified.requires_external_environment,
        "required_evidence": classified.required_evidence,
        "found_evidence": found_evidence,
        "missing_evidence": missing_evidence,
        "artifact_gaps": artifact_gaps,
        "verdict": verdict,
        "confidence": confidence,
        "risk": risk,
        "recommended_remediation": remediation,
    }


def _missing_evidence(classified: ClassifiedClaim, found_evidence: list[dict]) -> list[dict]:
    missing: list[dict] = []
    for requirement in classified.required_evidence:
        if _requirement_is_covered(requirement, found_evidence):
            continue
        missing.append(
            {
                "requirement": requirement,
                "reason_missing": _missing_reason(requirement, classified.claim_type),
                "suggested_fix": _suggested_fix(requirement),
                "severity": _severity(requirement, classified.claim_type),
            }
        )
    return missing


def _requirement_is_covered(requirement: str, found_evidence: list[dict]) -> bool:
    req = requirement.lower()
    evidence_types = {str(evidence.get("evidence_type", "")) for evidence in found_evidence}
    haystack = " ".join(
        str(evidence.get("snippet", "")) + " " + str(evidence.get("summary", ""))
        for evidence in found_evidence
    ).lower()

    if "metric file" in req:
        return "metric" in evidence_types or re.search(r"\b(mae|rmse|accuracy|metric|loss|f1)\b", haystack) is not None
    if "evaluation protocol" in req:
        return re.search(r"\b(evaluation protocol|evaluate|evaluation command|validation protocol)\b", haystack) is not None
    if "dataset" in req or "split" in req:
        return re.search(r"\b(dataset|split|validation set|synthetic validation)\b", haystack) is not None
    if "config" in req or "configuration" in req:
        return "config" in evidence_types or re.search(r"\b(config|configuration|yaml|toml)\b", haystack) is not None
    if "model artifact" in req or "checkpoint" in req:
        return "model_artifact" in evidence_types or re.search(r"\b(checkpoint|checksum|sha256|weights|artifact)\b", haystack) is not None
    if "implementation" in req or "module files" in req or "source tree" in req:
        return "implementation" in evidence_types or re.search(r"\b(implementation|module|source|function|class)\b", haystack) is not None
    if "usage example" in req or "examples" in req:
        return re.search(r"\b(example|usage|demo)\b", haystack) is not None
    if "test" in req or "smoke test" in req or "demonstration" in req:
        return "test" in evidence_types or re.search(r"\b(test|pytest|smoke|demonstration|demo)\b", haystack) is not None
    if "rights" in req or "license" in req or "permissions" in req:
        return re.search(r"\b(rights?|license|licensed|copyright|permission|grant|open-source|all rights reserved)\b", haystack) is not None
    if "source attribution" in req:
        return re.search(r"\b(source|official record|doi|publisher|third-party notice|attribution|zenodo)\b", haystack) is not None
    if "redistribution" in req:
        return re.search(r"\b(redistribut|not redistributed|does not include|excludes?|distribution)\b", haystack) is not None
    if "repository contents matching distribution claim" in req:
        return re.search(r"\b(repository|does not include|excludes?|not redistributed|not released|not provided)\b", haystack) is not None
    if "artifact availability" in req:
        return re.search(r"\b(artifact|checkpoint|model weights?|released?|available|not provided|does not include)\b", haystack) is not None
    if "evidence boundary" in req or "scope/caveat" in req or "limitations" in req:
        return re.search(r"\b(scope|limited|limitation|caveat|not general|not intended|real-world|transfer)\b", haystack) is not None
    if "policy or standard" in req:
        return re.search(r"\b(policy|standard|required|must|should|instruction)\b", haystack) is not None
    if "required artifact" in req:
        return re.search(r"\b(required|required fields?|must include|artifact|manifest|output)\b", haystack) is not None
    if "scope of instruction" in req:
        return re.search(r"\b(scope|applies|standard|policy|instruction|documentation|notebook)\b", haystack) is not None
    if "boundaries" in req or "limiting" in req or "non-goals" in req or req in {"scope note", "clear limiting statement"}:
        return re.search(r"\b(limit|scope|non-goal|not intended|does not)\b", haystack) is not None
    if "trace" in req or "example output" in req:
        return "trace" in evidence_types or re.search(r"\b(trace|output|log|capture)\b", haystack) is not None
    if "environment" in req:
        return re.search(r"\b(environment|hardware|camera|deployment|credentials)\b", haystack) is not None
    if "architecture" in req or "interfaces" in req or "contracts" in req:
        return re.search(r"\b(architecture|interface|contract|pipeline|component)\b", haystack) is not None
    if "external validation" in req or "real-world" in req or "cross-domain" in req:
        return re.search(r"\b(real-world|external validation|cross-domain|field data|production evidence)\b", haystack) is not None
    if "incident" in req or "review notes" in req:
        return "incident_report" in evidence_types or re.search(r"\b(incident|review|investigated|analysis)\b", haystack) is not None
    if "commit history" in req:
        return re.search(r"\b(commit|linked artifact|change log)\b", haystack) is not None
    if "direct supporting" in req or "supporting artifact" in req:
        return bool(found_evidence)
    return bool(found_evidence)


def _artifact_gaps(
    classified: ClassifiedClaim,
    missing_evidence: list[dict],
    found_evidence: list[dict],
) -> list[dict]:
    gaps: list[dict] = []
    missing_text = " ".join(item["requirement"].lower() for item in missing_evidence)

    if classified.claim_type == "metric_claim" and "metric" in missing_text:
        gaps.append(
            {
                "artifact_type": "metrics_file",
                "description": "No metric file or report matching the metric claim was found in the selected corpus.",
                "impact": "The metric claim cannot be checked against repository artifacts.",
            }
        )
    if "checkpoint" in missing_text or "model artifact" in missing_text:
        gaps.append(
            {
                "artifact_type": "model_artifact",
                "description": "No released checkpoint artifact or checkpoint hash was found.",
                "impact": "Independent metric reproduction is blocked even when metric documentation exists.",
            }
        )
    if "evaluation protocol" in missing_text or "smoke test" in missing_text or "commit history" in missing_text:
        gaps.append(
            {
                "artifact_type": "reproduction_steps",
                "description": "Required reproduction or review steps are missing from the selected corpus.",
                "impact": "The claim can only be reviewed indirectly.",
            }
        )
    if "configuration" in missing_text or "config" in missing_text:
        gaps.append(
            {
                "artifact_type": "config",
                "description": "Relevant configuration evidence was not found.",
                "impact": "Runtime or evaluation conditions are underspecified.",
            }
        )
    if "trace" in missing_text or "example output" in missing_text:
        gaps.append(
            {
                "artifact_type": "trace",
                "description": "No trace or example output was found.",
                "impact": "Runtime behaviour is not demonstrated by selected artifacts.",
            }
        )
    if classified.requires_external_environment and "environment" in missing_text:
        gaps.append(
            {
                "artifact_type": "external_environment_notes",
                "description": "External environment requirements are not documented enough for static verification.",
                "impact": "The claim requires hardware, deployment state, credentials, or human review.",
            }
        )
    if classified.claim_type == "architecture_claim" and "architecture documentation" in missing_text:
        gaps.append(
            {
                "artifact_type": "architecture_doc",
                "description": "Architecture documentation was not found.",
                "impact": "Architecture claims are harder to verify from source evidence alone.",
            }
        )
    return _dedupe_gaps(gaps)


def _verification_mode(
    classified: ClassifiedClaim,
    found_evidence: list[dict],
    missing_evidence: list[dict],
) -> str:
    if not _is_auditable_claim(classified):
        return "not_verifiable_from_available_material"
    if classified.requires_external_environment:
        return "external_environment_required"
    if not found_evidence:
        return "not_verifiable_from_available_material"
    if classified.claim_type == "metric_claim":
        if any(evidence.get("evidence_type") == "metric" for evidence in found_evidence):
            return "artifact_presence_review"
        return "not_verifiable_from_available_material"
    if classified.claim_domain in {
        "licensing_rights",
        "dataset_redistribution",
        "artifact_distribution",
        "documentation_policy",
    }:
        return "documentation_review"
    if classified.claim_type in {"architecture_claim", "bounded_non_claim", "process_claim"}:
        return "documentation_review"
    if classified.claim_type == "runtime_claim":
        return "artifact_presence_review"
    if classified.claim_type == "capability_claim":
        return "artifact_presence_review" if any(
            evidence.get("evidence_type") in {"implementation", "test"}
            for evidence in found_evidence
        ) else "documentation_review"
    if classified.claim_type == "adoption_usability_claim":
        return "human_review_required" if missing_evidence else "documentation_review"
    return "documentation_review"


def _verdict(
    classified: ClassifiedClaim,
    found_evidence: list[dict],
    missing_evidence: list[dict],
) -> str:
    text = classified.claim.claim_text.lower()
    if not _is_auditable_claim(classified):
        return "ambiguous"
    if _is_ambiguous(text):
        return "ambiguous"
    if classified.requires_external_environment:
        return "needs_human_review"
    if _is_overclaimed(classified, found_evidence, missing_evidence):
        return "overclaimed"
    meaningful_evidence = [
        evidence
        for evidence in found_evidence
        if evidence.get("strength") in {"strong", "moderate", "weak"}
    ]
    if not meaningful_evidence:
        return "unsupported"
    severe_missing = [
        item
        for item in missing_evidence
        if item.get("severity") in {"blocking", "major"}
    ]
    if not severe_missing and any(evidence.get("strength") == "strong" for evidence in meaningful_evidence):
        return "supported"
    return "partially_supported"


def _confidence(verdict: str, found_evidence: list[dict], missing_evidence: list[dict]) -> str:
    if verdict == "supported" and any(e.get("strength") == "strong" for e in found_evidence):
        return "high"
    if verdict in {"partially_supported", "overclaimed"} and found_evidence:
        return "medium"
    if verdict == "unsupported" and not found_evidence:
        return "medium"
    if verdict == "ambiguous":
        return "low"
    if verdict == "needs_human_review":
        return "low"
    return "medium" if not missing_evidence else "low"


def _recommended_remediation(
    classified: ClassifiedClaim,
    missing_evidence: list[dict],
    artifact_gaps: list[dict],
    verdict: str,
) -> list[str]:
    if not _is_auditable_claim(classified):
        return ["Do not treat this reference or low-quality record as an auditable project claim."]

    remediation: list[str] = []
    for item in missing_evidence:
        suggested = item.get("suggested_fix")
        if suggested:
            remediation.append(str(suggested))
    for gap in artifact_gaps:
        remediation.append(f"Address artifact gap: {gap['description']}")
    if verdict == "overclaimed":
        remediation.append("Narrow the claim wording to match the selected repository evidence.")
    if verdict == "unsupported":
        remediation.append("Either add supporting evidence or remove the claim from audited documentation.")
    if verdict == "needs_human_review":
        remediation.append("Document the external environment needed to verify the claim.")
    if classified.claim_type == "metric_claim":
        remediation.append("Link metric claims directly to metric files, protocol, and reproduction artifacts.")
    return _dedupe_strings(remediation)


def _risk(
    verdict: str,
    classified: ClassifiedClaim,
    missing_evidence: list[dict],
    artifact_gaps: list[dict],
) -> str:
    if not _is_auditable_claim(classified):
        if classified.claim.source_role.lower() != "claim_source":
            return "This record comes from reference or contract material and is not an auditable project claim."
        return "This extraction is too fragmentary or artifact-like for priority review and is demoted to the full listing."
    if verdict == "supported":
        return "The selected corpus contains strong matching evidence and no major missing evidence was identified."
    if verdict == "partially_supported":
        missing = ", ".join(item["requirement"] for item in missing_evidence[:3]) or "some evidence"
        return f"The claim has relevant repository evidence, but verification is weakened by missing evidence: {missing}."
    if verdict == "unsupported":
        return "No meaningful supporting evidence was found in the selected corpus."
    if verdict == "ambiguous":
        return "The claim is too vague or underspecified to determine a precise evidence requirement."
    if verdict == "overclaimed":
        return "The available evidence does not support the breadth of the claim."
    if verdict == "needs_human_review":
        return "Static repository evidence is insufficient because verification depends on an external environment or human judgement."
    if artifact_gaps:
        return "Verification is limited by repository artifact gaps."
    return f"The {classified.claim_type} could not be fully judged from selected material."


def _missing_reason(requirement: str, claim_type: str) -> str:
    return f"No selected corpus artifact clearly covers required evidence item '{requirement}' for this {claim_type}."


def _suggested_fix(requirement: str) -> str:
    req = requirement.lower()
    if "checkpoint" in req or "model artifact" in req:
        return "Add a checkpoint link, checksum, or clear note explaining why the model artifact is unavailable."
    if "evaluation protocol" in req:
        return "Add the evaluation protocol or command used to produce the reported metric."
    if "metric" in req:
        return "Add or link a metric file/report that contains the claimed value."
    if "dataset" in req:
        return "Document the dataset and split used for the claim."
    if "config" in req:
        return "Add the relevant runtime, training, or evaluation configuration."
    if "trace" in req or "example output" in req:
        return "Add trace output, logs, or example output demonstrating the runtime behaviour."
    if "environment" in req:
        return "Document required hardware, services, credentials, or deployment conditions."
    if "rights" in req or "license" in req or "permissions" in req:
        return "Link the claim to the relevant rights, license, or permissions notice."
    if "redistribution" in req or "distribution claim" in req:
        return "Add a clear statement matching what is and is not redistributed in the repository."
    if "artifact availability" in req:
        return "State whether the referenced artifact is included, excluded, or available elsewhere."
    if "source attribution" in req:
        return "Add source attribution or a third-party notice for the referenced dataset or artifact."
    if "policy" in req or "standard" in req or "instruction" in req:
        return "Link the instruction to the policy or standard document that defines it."
    if "evidence boundary" in req or "limitations" in req or "scope/caveat" in req:
        return "Add a clear limitation or scope note that bounds the claim."
    if "architecture" in req or "interface" in req:
        return "Add architecture documentation or link the claim to source modules/interfaces."
    return f"Add evidence covering: {requirement}."


def _severity(requirement: str, claim_type: str) -> str:
    req = requirement.lower()
    if claim_type == "metric_claim" and any(term in req for term in ["metric", "evaluation protocol", "dataset"]):
        return "blocking"
    if any(term in req for term in ["rights", "license", "redistribution", "distribution claim"]):
        return "major"
    if any(term in req for term in ["checkpoint", "model artifact", "environment", "configuration", "trace"]):
        return "major"
    return "minor"


def _is_ambiguous(text: str) -> bool:
    return len(text.split()) < 5 or bool(re.fullmatch(r".*\b(good|better|useful|simple)\b\.?", text))


def _is_overclaimed(
    classified: ClassifiedClaim,
    found_evidence: list[dict],
    missing_evidence: list[dict],
) -> bool:
    if classified.claim_type != "generalisation_claim":
        return False
    if not found_evidence:
        return False
    missing_text = " ".join(item["requirement"].lower() for item in missing_evidence)
    return any(term in missing_text for term in ["external validation", "real-world data", "cross-domain"])


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _dedupe_gaps(gaps: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    result: list[dict] = []
    for gap in gaps:
        key = (gap["artifact_type"], gap["description"])
        if key not in seen:
            seen.add(key)
            result.append(gap)
    return result


def _review_action(classified: ClassifiedClaim, verdict: str) -> str:
    if not _is_auditable_claim(classified):
        return "ignore_low_quality_extraction"
    if verdict == "needs_human_review":
        return "human_review_required"
    if verdict == "overclaimed":
        return "narrow_or_remove_claim"
    if verdict == "unsupported":
        return "add_evidence_or_remove_claim"
    if verdict == "partially_supported":
        return "add_missing_evidence"
    if verdict == "ambiguous":
        return "clarify_claim_wording"
    if classified.claim_importance == "high":
        return "keep_evidence_linked"
    return "no_action"


def _is_auditable_claim(classified: ClassifiedClaim) -> bool:
    return (
        classified.claim.source_role.lower() == "claim_source"
        and classified.extraction_quality not in NON_AUDITABLE_EXTRACTION_QUALITIES
    )
