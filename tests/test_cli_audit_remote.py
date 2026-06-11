import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from claimlint.cli import main


FIXTURES = Path(__file__).parent / "fixtures"
REQUIRED_OUTPUTS = [
    "claims.jsonl",
    "claims_report.md",
    "remediation_tasks.md",
    "evidence_packet.md",
    "run_manifest.json",
]


def test_audit_remote_clones_audits_and_cleans_worktree(tmp_path):
    source_repo = _make_git_repo(tmp_path, "remote-small-repo")
    work_root = tmp_path / "worktrees"
    out_root = tmp_path / "runs"

    exit_code = main(
        [
            "audit-remote",
            str(source_repo),
            "--manifest",
            "input_manifest.yml",
            "--work-root",
            str(work_root),
            "--out",
            str(out_root),
            "--yes",
        ]
    )

    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, source_repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    materialization = json.loads((out / "materialization.json").read_text(encoding="utf-8"))
    assert materialization["repo_url"] == str(source_repo)
    assert materialization["repo_name"] == source_repo.name
    assert materialization["output_root"] == str(out_root)
    assert materialization["keep_worktree"] is False
    assert materialization["cleaned_up"] is True
    assert (out / "input_manifest.yml").exists()
    assert materialization["manifest_snapshot"] == str(out / "input_manifest.yml")
    assert not Path(materialization["worktree_dir"]).exists()
    assert not any(work_root.iterdir())

    run_manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert run_manifest["command_args"]["command"] == "audit-remote"
    assert run_manifest["command_args"]["repo_url"] == str(source_repo)
    assert run_manifest["repo_path"] == "."
    assert run_manifest["manifest_path"] == "input_manifest.yml"


def test_audit_remote_can_keep_worktree(tmp_path):
    source_repo = _make_git_repo(tmp_path, "kept-small-repo")
    work_root = tmp_path / "worktrees"
    out_root = tmp_path / "runs"

    exit_code = main(
        [
            "audit-remote",
            str(source_repo),
            "--manifest",
            "input_manifest.yml",
            "--work-root",
            str(work_root),
            "--out",
            str(out_root),
            "--keep-worktree",
            "--yes",
        ]
    )

    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, source_repo.name)
    materialization = json.loads((out / "materialization.json").read_text(encoding="utf-8"))
    assert materialization["keep_worktree"] is True
    assert materialization["cleaned_up"] is False
    assert Path(materialization["worktree_dir"]).is_dir()
    assert Path(materialization["clone_dir"]).is_dir()


def test_audit_remote_generates_starter_manifest_when_no_manifest_is_supplied(tmp_path):
    source_repo = _make_git_repo(tmp_path, "auto-generated-manifest-repo", include_manifest=False)
    work_root = tmp_path / "worktrees"
    out_root = tmp_path / "runs"

    exit_code = main(
        [
            "audit-remote",
            str(source_repo),
            "--work-root",
            str(work_root),
            "--out",
            str(out_root),
            "--yes",
        ]
    )

    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, source_repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    materialization = json.loads((out / "materialization.json").read_text(encoding="utf-8"))
    assert materialization["generated_manifest"] is True
    assert (out / "input_manifest.yml").exists()
    assert materialization["manifest"].replace("\\", "/").endswith(
        "/.claimlint/input_manifest.yml"
    )
    assert materialization["cleaned_up"] is True
    assert not Path(materialization["worktree_dir"]).exists()


def test_audit_remote_missing_explicit_manifest_fails_without_generate_flag(tmp_path):
    source_repo = _make_git_repo(tmp_path, "missing-explicit-manifest-repo", include_manifest=False)
    work_root = tmp_path / "worktrees"
    out_root = tmp_path / "runs"

    exit_code = main(
        [
            "audit-remote",
            str(source_repo),
            "--manifest",
            "input_manifest.yml",
            "--work-root",
            str(work_root),
            "--out",
            str(out_root),
            "--yes",
        ]
    )

    assert exit_code == 1
    assert not out_root.exists()
    assert not any(work_root.iterdir())


def test_audit_remote_can_generate_starter_manifest(tmp_path):
    source_repo = _make_git_repo(tmp_path, "generated-manifest-repo", include_manifest=False)
    work_root = tmp_path / "worktrees"
    out_root = tmp_path / "runs"

    exit_code = main(
        [
            "audit-remote",
            str(source_repo),
            "--manifest",
            "input_manifest.yml",
            "--generate-manifest",
            "--work-root",
            str(work_root),
            "--out",
            str(out_root),
            "--yes",
        ]
    )

    assert exit_code == 0
    out = _single_timestamped_output_dir(out_root, source_repo.name)
    for filename in REQUIRED_OUTPUTS:
        assert (out / filename).exists()
    materialization = json.loads((out / "materialization.json").read_text(encoding="utf-8"))
    assert materialization["generated_manifest"] is True
    assert (out / "input_manifest.yml").exists()
    assert materialization["manifest"].replace("\\", "/").endswith(
        "/input_manifest.yml"
    )
    assert "README*.md" in (out / "input_manifest.yml").read_text(encoding="utf-8")
    assert materialization["cleaned_up"] is True
    assert not Path(materialization["worktree_dir"]).exists()


def _make_git_repo(tmp_path: Path, name: str, *, include_manifest: bool = True) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git is required for audit-remote tests")

    repo = tmp_path / name
    shutil.copytree(FIXTURES / "small_repo", repo)
    if not include_manifest:
        (repo / "input_manifest.yml").unlink()
    _git(repo, "init")
    _git(repo, "add", "-f", ".")
    _git(
        repo,
        "-c",
        "user.name=ClaimLint Test",
        "-c",
        "user.email=claimlint@example.invalid",
        "commit",
        "-m",
        "initial fixture",
    )
    return repo


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _single_timestamped_output_dir(out_root: Path, repo_name: str) -> Path:
    output_dirs = list(out_root.glob(f"{repo_name}-*"))
    assert len(output_dirs) == 1
    out = output_dirs[0]
    assert out.is_dir()
    assert re.fullmatch(rf"{re.escape(repo_name)}-\d{{8}}-\d{{4}}Z", out.name)
    return out
