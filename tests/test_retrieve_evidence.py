from pathlib import Path

from claimlint.classify_claims import classify_claims
from claimlint.extract_claims import extract_claims
from claimlint.ingest_markdown import ingest_files
from claimlint.manifest import load_manifest
from claimlint.retrieve_evidence import retrieve_evidence


FIXTURE = Path(__file__).parent / "fixtures" / "small_repo"


def _classified_and_chunks():
    selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
    chunks = ingest_files(FIXTURE, selection.input_files)
    claims = extract_claims(chunks)
    return classify_claims(claims), chunks


def test_metric_claim_retrieves_metric_json_fixture():
    classified, chunks = _classified_and_chunks()
    metric_claim = next(item for item in classified if item.claim_type == "metric_claim")
    evidence = retrieve_evidence(metric_claim, chunks)
    assert any(item["path"] == "metrics/validation_metrics.json" for item in evidence)


def test_runtime_claim_retrieves_technical_notes_fixture():
    classified, chunks = _classified_and_chunks()
    runtime_claim = next(item for item in classified if item.claim_type == "runtime_claim")
    evidence = retrieve_evidence(runtime_claim, chunks)
    assert any(item["path"] == "docs/technical_notes.md" for item in evidence)


def test_evidence_path_always_exists():
    classified, chunks = _classified_and_chunks()
    for item in classified:
        for evidence in retrieve_evidence(item, chunks):
            assert (FIXTURE / evidence["path"]).exists()

