from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from .classify_claims import classify_claims
from .extract_claims import extract_claims
from .ingest_markdown import ingest_files
from .judge_support import build_claim_record
from .manifest import ManifestError, load_manifest
from .render_report import REQUIRED_OUTPUTS, render_outputs
from .retrieve_evidence import retrieve_evidence
from .run_manifest import build_run_manifest, utc_now
from .schemas import SchemaValidationError, validate_claim_record, validate_run_manifest


EXIT_INVALID_ARGUMENTS = 1
EXIT_MANIFEST_VALIDATION_FAILED = 2
EXIT_SCHEMA_VALIDATION_FAILED = 3
EXIT_RUNTIME_ERROR = 4
DEFAULT_OUTPUT_ROOT = "output"
DEFAULT_REMOTE_ROOT = ".claimlint"


@dataclass
class AuditResult:
    exit_code: int
    output_dir: Path | None = None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "audit":
        return audit(args)
    if args.command == "audit-remote":
        return audit_remote(args)
    if args.command is None:
        parser.print_help(sys.stderr)
        return EXIT_INVALID_ARGUMENTS
    parser.print_help(sys.stderr)
    return EXIT_INVALID_ARGUMENTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claimlint")
    subparsers = parser.add_subparsers(dest="command")
    audit_parser = subparsers.add_parser("audit", help="Audit repository claims against selected evidence.")
    audit_parser.add_argument("--repo", required=True, help="Repository directory to audit.")
    audit_parser.add_argument("--manifest", required=True, help="Input manifest YAML path.")
    audit_parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT_ROOT,
        help="Output root directory for timestamped audit folders. Defaults to 'output'.",
    )
    remote_parser = subparsers.add_parser(
        "audit-remote",
        help="Clone an explicit Git repository, audit it, then clean up the temporary clone by default.",
    )
    remote_parser.add_argument("repo_url", help="Git repository URL or local Git repository path to audit.")
    remote_parser.add_argument(
        "--manifest",
        help="Manifest path. Relative paths are resolved inside the cloned repository.",
    )
    remote_parser.add_argument(
        "--generate-manifest",
        action="store_true",
        help="Create a temporary starter manifest inside the clone when the supplied repo-relative manifest is missing.",
    )
    remote_parser.add_argument("--ref", help="Branch, tag, or ref to clone.")
    remote_parser.add_argument(
        "--work-root",
        help="Root directory for temporary cloned worktrees. Defaults to ~/.claimlint/<repo>/worktrees.",
    )
    remote_parser.add_argument(
        "--out",
        help="Output root directory for audit artifacts. Defaults to ~/.claimlint/<repo>/runs.",
    )
    remote_parser.add_argument(
        "--keep-worktree",
        action="store_true",
        help="Keep the cloned worktree after the audit. By default it is deleted after the run.",
    )
    remote_parser.add_argument(
        "--yes",
        action="store_true",
        help="Use default work/output locations without interactive prompts.",
    )
    return parser


def audit(args: argparse.Namespace) -> int:
    command_args = {
        "command": "audit",
        "repo": str(args.repo),
        "manifest": str(args.manifest),
        "out": str(args.out),
    }
    return run_audit(
        repo=Path(args.repo),
        manifest=Path(args.manifest),
        out_root=Path(args.out),
        command_args=command_args,
    ).exit_code


def audit_remote(args: argparse.Namespace) -> int:
    started_at = utc_now()
    repo_name = _safe_folder_name(_infer_repo_name(args.repo_url))
    default_base = Path.home() / DEFAULT_REMOTE_ROOT / repo_name
    default_work_root = default_base / "worktrees"
    default_out_root = default_base / "runs"
    work_root = _choose_path(
        "Temporary clone root",
        cli_value=args.work_root,
        default=default_work_root,
        assume_yes=args.yes,
    )
    out_root = _choose_path(
        "Output root",
        cli_value=args.out,
        default=default_out_root,
        assume_yes=args.yes,
    )
    run_name = f"{repo_name}-{_minute_timestamp(started_at)}"
    work_run_dir = _unique_child_dir(work_root, run_name)
    clone_dir = work_run_dir / repo_name
    cleanup_done = False

    try:
        _clone_repository(args.repo_url, clone_dir, args.ref)
        manifest_result = _resolve_remote_manifest(
            clone_dir=clone_dir,
            manifest=args.manifest,
            generate_manifest=args.generate_manifest,
        )
        if manifest_result is None:
            return EXIT_INVALID_ARGUMENTS
        manifest, generated_manifest = manifest_result
        materialization = {
            "repo_url": args.repo_url,
            "ref": args.ref,
            "repo_name": repo_name,
            "work_root": str(work_root),
            "worktree_dir": str(work_run_dir),
            "clone_dir": str(clone_dir),
            "output_root": str(out_root),
            "manifest": str(manifest),
            "generated_manifest": generated_manifest,
            "keep_worktree": bool(args.keep_worktree),
            "started_at": started_at,
        }
        result = run_audit(
            repo=clone_dir,
            manifest=manifest,
            out_root=out_root,
            command_args={
                "command": "audit-remote",
                "repo_url": args.repo_url,
                "ref": args.ref,
                "repo": str(clone_dir),
                "manifest": str(manifest),
                "out": str(out_root),
                "work_root": str(work_root),
                "keep_worktree": bool(args.keep_worktree),
                "generate_manifest": bool(args.generate_manifest),
            },
        )
        if result.exit_code == 0 and result.output_dir is not None:
            manifest_snapshot = _write_manifest_snapshot(result.output_dir, manifest)
            materialization["manifest_snapshot"] = str(manifest_snapshot)
            if not args.keep_worktree:
                _cleanup_worktree(work_run_dir)
                cleanup_done = True
            _write_materialization(result.output_dir, materialization, cleaned_up=cleanup_done)
            print(f"Audit output: {result.output_dir}")
        return result.exit_code
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if isinstance(exc.stderr, str) else ""
        details = f": {stderr}" if stderr else ""
        print(f"Runtime error: git clone failed{details}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    except Exception as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    finally:
        if not args.keep_worktree and not cleanup_done:
            _cleanup_worktree(work_run_dir)


def run_audit(
    *,
    repo: Path,
    manifest: Path,
    out_root: Path,
    command_args: dict,
) -> AuditResult:
    started_at = utc_now()
    out_dir = _timestamped_output_dir(out_root, repo, started_at)

    if not repo.exists() or not repo.is_dir():
        print(f"Invalid repository path: {repo}", file=sys.stderr)
        return AuditResult(EXIT_INVALID_ARGUMENTS)
    if not manifest.exists() or not manifest.is_file():
        print(f"Invalid manifest path: {manifest}", file=sys.stderr)
        return AuditResult(EXIT_INVALID_ARGUMENTS)

    try:
        selection = load_manifest(repo, manifest)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return AuditResult(EXIT_MANIFEST_VALIDATION_FAILED)

    try:
        chunks = ingest_files(repo, selection.input_files)
        candidates = extract_claims(chunks)
        classified_claims = classify_claims(candidates)
        retrieval_trace: list[dict] = []
        claim_records: list[dict] = []

        for classified in classified_claims:
            found_evidence = retrieve_evidence(classified, chunks)
            retrieval_trace.append(
                {
                    "claim_id": classified.claim.claim_id,
                    "evidence_count": len(found_evidence),
                    "evidence_paths": [evidence["path"] for evidence in found_evidence],
                }
            )
            record = build_claim_record(classified, found_evidence)
            validate_claim_record(record)
            claim_records.append(record)

        completed_at = utc_now()
        output_paths = {
            key: str(out_dir / filename)
            for key, filename in REQUIRED_OUTPUTS.items()
        }
        run_manifest = build_run_manifest(
            started_at=started_at,
            completed_at=completed_at,
            repo_path=repo,
            manifest_path=manifest,
            output_dir=out_dir,
            command_args=command_args,
            input_files=selection.input_files,
            manifest_warnings=selection.warnings,
            claim_records=claim_records,
            outputs=output_paths,
        )
        validate_run_manifest(run_manifest)
        render_outputs(out_dir, claim_records, run_manifest)
        _write_debug(out_dir, chunks, candidates, retrieval_trace)
        return AuditResult(0, out_dir)
    except SchemaValidationError as exc:
        print(str(exc), file=sys.stderr)
        return AuditResult(EXIT_SCHEMA_VALIDATION_FAILED)
    except Exception as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return AuditResult(EXIT_RUNTIME_ERROR)


def _timestamped_output_dir(out_root: Path, repo: Path, started_at: str) -> Path:
    repo_name = _safe_folder_name(repo.resolve().name)
    timestamp = _minute_timestamp(started_at)
    return out_root / f"{repo_name}-{timestamp}"


def _safe_folder_name(name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    return safe_name or "repository"


def _infer_repo_name(repo_url: str) -> str:
    normalized = repo_url.rstrip("/\\")
    parsed = urlparse(normalized)
    path = parsed.path if parsed.scheme else normalized
    name = Path(path.replace("\\", "/")).name
    if name.endswith(".git"):
        name = name[:-4]
    return name or "repository"


def _choose_path(
    label: str,
    *,
    cli_value: str | None,
    default: Path,
    assume_yes: bool,
) -> Path:
    if cli_value:
        return Path(cli_value).expanduser()
    if assume_yes or not sys.stdin.isatty():
        print(f"Using default {label.lower()}: {default}")
        return default
    answer = input(f"{label} [{default}]: ").strip()
    return Path(answer).expanduser() if answer else default


def _unique_child_dir(parent: Path, preferred_name: str) -> Path:
    candidate = parent / preferred_name
    if not candidate.exists():
        return candidate
    index = 2
    while True:
        candidate = parent / f"{preferred_name}-{index}"
        if not candidate.exists():
            return candidate
        index += 1


def _clone_repository(repo_url: str, clone_dir: Path, ref: str | None) -> None:
    clone_dir.parent.mkdir(parents=True, exist_ok=True)
    command = ["git", "clone"]
    if ref:
        command.extend(["--branch", ref])
    command.extend([repo_url, str(clone_dir)])
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    subprocess.run(command, check=True, capture_output=True, text=True, env=env)


def _remote_manifest_path(clone_dir: Path, manifest: str) -> Path:
    manifest_path = Path(manifest).expanduser()
    if manifest_path.is_absolute():
        return manifest_path
    return clone_dir / manifest_path


def _resolve_remote_manifest(
    *,
    clone_dir: Path,
    manifest: str | None,
    generate_manifest: bool,
) -> tuple[Path, bool] | None:
    if manifest:
        manifest_path = _remote_manifest_path(clone_dir, manifest)
        if manifest_path.exists():
            return manifest_path, False
        if not generate_manifest:
            print(
                f"Invalid manifest path: {manifest}. Provide --manifest for a file in the repository, "
                "or pass --generate-manifest to create a temporary starter manifest.",
                file=sys.stderr,
            )
            return None
        if manifest_path.is_absolute() and not _is_within(clone_dir, manifest_path):
            print(
                "Generated manifests must be written inside the cloned repository. "
                "Use a repo-relative --manifest path with --generate-manifest.",
                file=sys.stderr,
            )
            return None
        _write_generated_manifest(manifest_path)
        return manifest_path, True

    manifest_path = clone_dir / ".claimlint" / "input_manifest.yml"
    _write_generated_manifest(manifest_path)
    return manifest_path, True


def _write_generated_manifest(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "version: 0.1",
                "",
                "include:",
                "  - glob: 'README*.md'",
                "    role: primary_readme",
                "    source_role: claim_source",
                "  - glob: 'docs/**/*.md'",
                "    role: documentation",
                "    source_role: claim_source",
                "  - glob: '*.md'",
                "    role: root_markdown",
                "    source_role: claim_source",
                "  - glob: 'src/**/*.py'",
                "    role: source_code",
                "    source_role: source_code",
                "    extract_claims: false",
                "  - glob: 'tests/**/*.py'",
                "    role: test_fixture",
                "    source_role: test_fixture",
                "    extract_claims: false",
                "  - glob: 'pyproject.toml'",
                "    role: config",
                "    source_role: reference_only",
                "    extract_claims: false",
                "  - glob: 'configs/**/*.yml'",
                "    role: config",
                "    source_role: reference_only",
                "    extract_claims: false",
                "  - glob: 'schemas/**/*.json'",
                "    role: schemas",
                "    source_role: schema_reference",
                "    extract_claims: false",
                "  - glob: 'workflows/**/*.yml'",
                "    role: workflow",
                "    source_role: workflow_contract",
                "    extract_claims: false",
                "",
                "exclude:",
                "  - glob: '.git/**'",
                "  - glob: '.claimlint/**'",
                "  - glob: '.venv/**'",
                "  - glob: 'node_modules/**'",
                "  - glob: 'output/**'",
                "  - glob: 'runs/**'",
                "  - glob: 'dist/**'",
                "  - glob: 'build/**'",
                "",
                "limits:",
                "  max_file_bytes: 500000",
                "  max_total_files: 200",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _is_within(parent: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _write_materialization(output_dir: Path, materialization: dict, *, cleaned_up: bool) -> None:
    payload = dict(materialization)
    payload["cleaned_up"] = cleaned_up
    (output_dir / "materialization.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_manifest_snapshot(output_dir: Path, manifest: Path) -> Path:
    snapshot = output_dir / "input_manifest.yml"
    shutil.copyfile(manifest, snapshot)
    return snapshot


def _cleanup_worktree(work_run_dir: Path) -> None:
    if not work_run_dir.exists():
        return
    shutil.rmtree(work_run_dir, onerror=_remove_readonly)


def _remove_readonly(func, path, exc_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _minute_timestamp(timestamp: str) -> str:
    started = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return started.astimezone(timezone.utc).strftime("%Y%m%d-%H%MZ")


def _write_debug(out_dir: Path, chunks: list, candidates: list, retrieval_trace: list[dict]) -> None:
    debug_dir = out_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(debug_dir / "chunks.jsonl", [asdict(chunk) for chunk in chunks])
    _write_jsonl(debug_dir / "candidate_claims.jsonl", [asdict(candidate) for candidate in candidates])
    _write_jsonl(debug_dir / "retrieval_trace.jsonl", retrieval_trace)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
