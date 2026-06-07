from claimlint.render_report import _claims_report


def _run_manifest():
    return {
        "repo_path": ".",
        "manifest_path": "input_manifest.yml",
        "workflow_version": "0.1.0",
        "started_at": "2026-06-07T00:00:00+00:00",
        "claim_count": 3,
        "repository_claim_surface_status": "medium_claim_surface",
        "verdict_counts": {},
    }


def _record(**overrides):
    record = {
        "claim_id": "claim_base",
        "claim_text": "The tool supports trace capture.",
        "claim_type": "runtime_claim",
        "claim_domain": "runtime_behavior",
        "claim_importance": "medium",
        "review_action": "add_missing_evidence",
        "extraction_quality": "auditable_claim",
        "claim_surface_status": "medium_claim_surface",
        "source_file": "README.md",
        "source_role": "claim_source",
        "source_location": "section: test; line 1",
        "is_auditable_claim": True,
        "verification_mode": "documentation_review",
        "requires_external_environment": False,
        "required_evidence": ["trace"],
        "found_evidence": [],
        "missing_evidence": [],
        "artifact_gaps": [],
        "verdict": "partially_supported",
        "confidence": "medium",
        "risk": "Needs more evidence.",
        "recommended_remediation": ["Add evidence."],
    }
    record.update(overrides)
    return record


def test_priority_findings_exclude_low_importance_and_suppressed_quality():
    records = [
        _record(
            claim_id="claim_medium",
            claim_importance="medium",
            claim_text="The runtime supports trace capture.",
        ),
        _record(
            claim_id="claim_low",
            claim_importance="low",
            claim_text="The documentation is easy to review.",
        ),
        _record(
            claim_id="claim_bounded",
            claim_importance="high",
            claim_text="This is not a general-purpose auditor.",
            extraction_quality="bounded_context",
            verdict="partially_supported",
        ),
    ]

    report = _claims_report(records, _run_manifest())
    priority_section = report.split("## Priority Findings", 1)[1].split(
        "## High-Importance Claims Requiring Action",
        1,
    )[0]
    high_importance_section = report.split(
        "## High-Importance Claims Requiring Action",
        1,
    )[1].split("## Claims Grouped by Domain", 1)[0]
    suppressed_section = report.split("## Suppressed Reference Records", 1)[1].split(
        "## Full Claim Listing",
        1,
    )[0]

    assert "claim_medium" in priority_section
    assert "claim_low" not in priority_section
    assert "claim_bounded" not in priority_section
    assert "claim_bounded" not in high_importance_section
    assert "claim_bounded" in suppressed_section
