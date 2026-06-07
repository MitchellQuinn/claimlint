from __future__ import annotations

import os
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .types import InputFile


WORKFLOW_ID = "claimlint.claim-audit"
WORKFLOW_VERSION = "0.1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_run_manifest(
    *,
    started_at: str,
    completed_at: str,
    repo_path: str | Path,
    manifest_path: str | Path,
    output_dir: str | Path,
    command_args: dict[str, Any],
    input_files: list[InputFile],
    manifest_warnings: list[str],
    claim_records: list[dict],
    outputs: dict[str, str],
) -> dict[str, Any]:
    verdict_counts = dict(Counter(record["verdict"] for record in claim_records))
    repo = Path(repo_path).resolve()
    return {
        "tool_name": "claimlint",
        "tool_version": __version__,
        "workflow_id": WORKFLOW_ID,
        "workflow_version": WORKFLOW_VERSION,
        "started_at": started_at,
        "completed_at": completed_at,
        "repo_path": _repo_relative_posix(repo, repo),
        "manifest_path": _repo_relative_posix(repo, manifest_path),
        "output_dir": _repo_relative_posix(repo, output_dir),
        "command_args": _normalize_command_args(repo, command_args),
        "input_files": [asdict(input_file) for input_file in input_files],
        "manifest_warnings": manifest_warnings,
        "claim_count": len(claim_records),
        "verdict_counts": verdict_counts,
        "repository_claim_surface_status": repository_claim_surface_status(claim_records),
        "schemas": {
            "claim_record": "schemas/claim_record.schema.json",
            "run_manifest": "schemas/run_manifest.schema.json",
            "audit_summary": "schemas/audit_summary.schema.json",
        },
        "adapter_status": load_adapter_status(),
        "outputs": {
            key: _repo_relative_posix(repo, path)
            for key, path in outputs.items()
        },
    }


def repository_claim_surface_status(claim_records: list[dict]) -> str:
    if not claim_records:
        return "no_auditable_claims_found"
    statuses = [record["claim_surface_status"] for record in claim_records]
    if "requires_external_environment" in statuses:
        return "requires_external_environment"
    if "high_claim_surface" in statuses:
        return "high_claim_surface"
    if "medium_claim_surface" in statuses:
        return "medium_claim_surface"
    return "low_claim_surface"


def load_adapter_status() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[2] / "adapters" / "status.yml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _normalize_command_args(repo: Path, command_args: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(command_args)
    for key in ("repo", "manifest", "out"):
        if key in normalized:
            normalized[key] = _repo_relative_posix(repo, normalized[key])
    return normalized


def _repo_relative_posix(repo: Path, path: str | Path) -> str:
    target = Path(path).resolve()
    if target == repo:
        return "."
    try:
        rel_path = target.relative_to(repo)
    except ValueError:
        try:
            return Path(os.path.relpath(target, repo)).as_posix()
        except ValueError:
            return target.as_posix()
    return rel_path.as_posix()
