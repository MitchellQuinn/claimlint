from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "audit":
        parser.print_help(sys.stderr)
        return EXIT_INVALID_ARGUMENTS
    return audit(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claimlint")
    subparsers = parser.add_subparsers(dest="command")
    audit_parser = subparsers.add_parser("audit", help="Audit repository claims against selected evidence.")
    audit_parser.add_argument("--repo", required=True, help="Repository directory to audit.")
    audit_parser.add_argument("--manifest", required=True, help="Input manifest YAML path.")
    audit_parser.add_argument("--out", required=True, help="Output directory.")
    return parser


def audit(args: argparse.Namespace) -> int:
    started_at = utc_now()
    repo = Path(args.repo)
    manifest = Path(args.manifest)
    out_dir = Path(args.out)

    if not repo.exists() or not repo.is_dir():
        print(f"Invalid repository path: {repo}", file=sys.stderr)
        return EXIT_INVALID_ARGUMENTS
    if not manifest.exists() or not manifest.is_file():
        print(f"Invalid manifest path: {manifest}", file=sys.stderr)
        return EXIT_INVALID_ARGUMENTS

    try:
        selection = load_manifest(repo, manifest)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_MANIFEST_VALIDATION_FAILED

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
            command_args={"command": "audit", "repo": str(repo), "manifest": str(manifest), "out": str(out_dir)},
            input_files=selection.input_files,
            manifest_warnings=selection.warnings,
            claim_records=claim_records,
            outputs=output_paths,
        )
        validate_run_manifest(run_manifest)
        render_outputs(out_dir, claim_records, run_manifest)
        _write_debug(out_dir, chunks, candidates, retrieval_trace)
        return 0
    except SchemaValidationError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_SCHEMA_VALIDATION_FAILED
    except Exception as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


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
