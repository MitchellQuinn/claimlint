import json
from pathlib import Path

from clipboard_raccoon.cli import main
from clipboard_raccoon.schemas import validate_claim_record


FIXTURES = Path(__file__).parent / "fixtures"
REQUIRED_OUTPUTS = [
    "claims.jsonl",
    "claims_report.md",
    "remediation_tasks.md",
    "evidence_packet.md",
    "run_manifest.json",
]


def test_cli_audit_writes_required_outputs(tmp_path):
    repo = FIXTURES / "small_repo"
    out = tmp_path / "run"
    exit_code = main(["audit", "--repo", str(repo), "--manifest", str(repo / "input_manifest.yml"), "--out", str(out)])
    assert exit_code == 0
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    with (out / "claims.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            validate_claim_record(json.loads(line))
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert "verdict_counts" in manifest


def test_low_claim_repo_writes_no_claim_outputs(tmp_path):
    repo = FIXTURES / "low_claim_repo"
    out = tmp_path / "run"
    exit_code = main(["audit", "--repo", str(repo), "--manifest", str(repo / "input_manifest.yml"), "--out", str(out)])
    assert exit_code == 0
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["repository_claim_surface_status"] in {
        "no_auditable_claims_found",
        "low_claim_surface",
    }
    report = (out / "claims_report.md").read_text(encoding="utf-8")
    assert "No substantial auditable repository claims were found" in report

