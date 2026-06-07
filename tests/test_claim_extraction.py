from pathlib import Path

from clipboard_raccoon.classify_claims import classify_claims
from clipboard_raccoon.extract_claims import extract_claims
from clipboard_raccoon.ingest_markdown import ingest_files
from clipboard_raccoon.manifest import load_manifest


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

