import pytest

from claimlint.schemas import SchemaValidationError, validate_claim_record


def valid_claim_record():
    return {
        "claim_id": "claim_001",
        "claim_text": "The selected model achieved 0.015856 m synthetic validation MAE.",
        "claim_type": "metric_claim",
        "claim_domain": "model_performance",
        "claim_importance": "high",
        "review_action": "keep_evidence_linked",
        "extraction_quality": "auditable_claim",
        "claim_surface_status": "high_claim_surface",
        "source_file": "README.md",
        "source_role": "claim_source",
        "source_location": "section: Results",
        "is_auditable_claim": True,
        "verification_mode": "artifact_presence_review",
        "requires_external_environment": False,
        "required_evidence": ["metric file or report"],
        "found_evidence": [
            {
                "path": "metrics/validation_metrics.json",
                "location": "metric: synthetic_validation_mae",
                "summary": "Reports a synthetic validation MAE matching the README claim.",
                "strength": "strong",
                "evidence_type": "metric",
            }
        ],
        "missing_evidence": [],
        "artifact_gaps": [],
        "verdict": "supported",
        "confidence": "high",
        "risk": "The selected corpus contains strong matching evidence.",
        "recommended_remediation": [],
    }


def test_valid_example_claim_passes():
    validate_claim_record(valid_claim_record())


def test_missing_required_field_fails():
    record = valid_claim_record()
    del record["claim_text"]
    with pytest.raises(SchemaValidationError):
        validate_claim_record(record)


def test_invalid_verdict_fails():
    record = valid_claim_record()
    record["verdict"] = "plausible"
    with pytest.raises(SchemaValidationError):
        validate_claim_record(record)


def test_invalid_verification_mode_fails():
    record = valid_claim_record()
    record["verification_mode"] = "quick_metric_check"
    with pytest.raises(SchemaValidationError):
        validate_claim_record(record)


def test_boundary_statement_record_passes():
    record = valid_claim_record()
    record["claim_id"] = "claim_boundary"
    record["claim_text"] = "Do not silently modify the target repository."
    record["claim_type"] = "bounded_non_claim"
    record["claim_domain"] = "other"
    record["claim_importance"] = "low"
    record["review_action"] = "keep_as_boundary_note"
    record["extraction_quality"] = "boundary_statement"
    record["claim_surface_status"] = "low_claim_surface"
    record["is_auditable_claim"] = False
    record["verification_mode"] = "not_verifiable_from_available_material"
    record["required_evidence"] = []
    record["found_evidence"] = []
    record["verdict"] = "ambiguous"
    record["confidence"] = "low"
    validate_claim_record(record)
