# ClaimLint Self-Audit Smoke Test

This smoke test checks that the ClaimLint CLI can run against this repository with the self-audit manifest and produce the required output artifacts. For the README claim that the canonical audit behavior is defined in `workflows/claim_audit.yml` and executed through the shared runtime contract in `docs/runtime_contract.md`, this smoke test runs that CLI path against the self-audit manifest.

## Command

Run from the repository root:

```bash
claimlint audit --repo . --manifest examples/claimlint-self-audit/claimlint-github-manifest.yml
```

The command intentionally omits `--out` so the runtime contract default writes artifacts under `./output`.

## Expected Output Files

Each successful run writes a timestamped directory under `output/` containing:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

## Observed Successful Output

On 2026-06-07, running the command from the repository root completed with exit code `0` and wrote artifacts under `output/claimlint-20260607-1746Z`.

The observed run directory contained all required files:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

The observed `run_manifest.json` recorded `workflow_id` as `claimlint.claim-audit`, `workflow_version` as `0.1.0`, `repo_path` as `.`, `manifest_path` as `examples/claimlint-self-audit/claimlint-github-manifest.yml`, and `command_args.out` as `output`.

## Scope

This is a smoke test. It demonstrates that the configured self-audit command completes and writes the required artifacts. It is not a full correctness evaluation of every extracted claim, every evidence match, or every judgement.
