import json
import re
from pathlib import Path

from claimlint.cli import main
from claimlint.schemas import validate_claim_record


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
    out_root = tmp_path / "output-root"
    exit_code = main(
        ["audit", "--repo", str(repo), "--manifest", str(repo / "input_manifest.yml"), "--out", str(out_root)]
    )
    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    with (out / "claims.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            validate_claim_record(record)
            assert {
                "claim_domain",
                "claim_importance",
                "review_action",
                "extraction_quality",
                "source_role",
                "is_auditable_claim",
            } <= set(record)
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool_name"] == "claimlint"
    assert manifest["workflow_id"] == "claimlint.claim-audit"
    assert "verdict_counts" in manifest
    assert {
        "source_role",
        "extract_claims",
        "use_as_evidence",
    } <= set(manifest["input_files"][0])
    assert manifest["repo_path"] == "."
    assert manifest["manifest_path"] == "input_manifest.yml"
    _assert_posix_relative_paths(manifest)
    report = (out / "claims_report.md").read_text(encoding="utf-8")
    assert "- Repository: ." in report
    assert "- Manifest: input_manifest.yml" in report
    headings = [
        "## Executive Summary",
        "## Verdict Summary",
        "## Domain Summary",
        "## Priority Findings",
        "## High-Importance Claims Requiring Action",
        "## Claims Grouped by Domain",
        "## Full Claim Listing",
    ]
    positions = [report.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_cli_audit_defaults_to_output_root(tmp_path, monkeypatch):
    repo = FIXTURES / "low_claim_repo"
    monkeypatch.chdir(tmp_path)
    exit_code = main(["audit", "--repo", str(repo), "--manifest", str(repo / "input_manifest.yml")])
    assert exit_code == 0
    out = _single_timestamped_output_dir(tmp_path / "output", repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()


def test_low_claim_repo_writes_no_claim_outputs(tmp_path):
    repo = FIXTURES / "low_claim_repo"
    out_root = tmp_path / "output-root"
    exit_code = main(
        ["audit", "--repo", str(repo), "--manifest", str(repo / "input_manifest.yml"), "--out", str(out_root)]
    )
    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["repository_claim_surface_status"] in {
        "no_auditable_claims_found",
        "low_claim_surface",
    }
    report = (out / "claims_report.md").read_text(encoding="utf-8")
    assert "No substantial auditable repository claims were found" in report


def _assert_posix_relative_paths(manifest):
    path_values = [
        manifest["repo_path"],
        manifest["manifest_path"],
        manifest["output_dir"],
        manifest["command_args"]["repo"],
        manifest["command_args"]["manifest"],
        manifest["command_args"]["out"],
        *manifest["outputs"].values(),
        *(input_file["path"] for input_file in manifest["input_files"]),
    ]
    for value in path_values:
        assert "\\" not in value
        assert not value.startswith("/")
        assert not re.match(r"^[A-Za-z]:/", value)


def _single_timestamped_output_dir(out_root: Path, repo_name: str) -> Path:
    output_dirs = list(out_root.glob(f"{repo_name}-*"))
    assert len(output_dirs) == 1
    out = output_dirs[0]
    assert out.is_dir()
    assert re.fullmatch(rf"{re.escape(repo_name)}-\d{{8}}-\d{{4}}Z", out.name)
    return out
