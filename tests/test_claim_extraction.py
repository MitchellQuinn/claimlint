from pathlib import Path

from clipboard_raccoon.classify_claims import classify_claim, classify_claims
from clipboard_raccoon.extract_claims import extract_claims
from clipboard_raccoon.ingest_markdown import ingest_files
from clipboard_raccoon.manifest import load_manifest
from clipboard_raccoon.types import CandidateClaim, DocumentChunk


FIXTURES = Path(__file__).parent / "fixtures"


def _claims_for(repo_name):
    repo = FIXTURES / repo_name
    selection = load_manifest(repo, repo / "input_manifest.yml")
    chunks = ingest_files(repo, selection.input_files)
    return extract_claims(chunks)


def test_metric_claim_extracted_from_fixture_readme():
    claims = _claims_for("small_repo")
    assert any("0.015856" in claim.claim_text for claim in claims)


def test_bounded_non_claim_recognised_correctly():
    claims = _claims_for("small_repo")
    classified = classify_claims(claims)
    assert any(item.claim_type == "bounded_non_claim" for item in classified)


def test_low_claim_repo_produces_zero_or_near_zero_claims():
    claims = _claims_for("low_claim_repo")
    assert len(claims) <= 1


def test_markdown_wrapped_statement_is_extracted_as_complete_claim():
    chunk = DocumentChunk(
        chunk_id="chunk_test",
        path="COPYRIGHT.md",
        role="notices",
        heading_path=["Copyright Notice"],
        start_line=1,
        end_line=3,
        text="# Copyright Notice\nThis repository does not grant any rights in the\nMIMII dataset.",
        sha256="abc",
    )
    claims = extract_claims([chunk])
    assert any("rights in the MIMII dataset" in claim.claim_text for claim in claims)
    assert not any(claim.claim_text.endswith("in the") for claim in claims)


def test_heading_and_table_header_noise_is_suppressed():
    chunk = DocumentChunk(
        chunk_id="chunk_test",
        path="README.md",
        role="documentation",
        heading_path=["Spec"],
        start_line=1,
        end_line=4,
        text="# Processing Pipeline (Audio -> Surface)\n\n| Metric | Value |\n| --- | --- |",
        sha256="abc",
    )
    assert extract_claims([chunk]) == []


def test_bounded_non_claim_domains_are_not_collapsed():
    examples = {
        "licensing_rights": "This repository is intentionally published without an open-source license.",
        "dataset_redistribution": "The MIMII dataset is not redistributed in this repository.",
        "generalisation_scope": "This is not a general-purpose industrial anomaly detection system.",
        "documentation_policy": "Export notebooks must include a run_manifest.json file.",
    }
    for expected_domain, text in examples.items():
        claim = CandidateClaim(
            claim_id=f"claim_{expected_domain}",
            claim_text=text,
            source_file="README.md",
            source_location="section: test; line 1",
            source_chunk_id="chunk_test",
            start_line=1,
            end_line=1,
        )
        assert classify_claim(claim).claim_domain == expected_domain
