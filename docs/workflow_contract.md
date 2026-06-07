# Workflow Contract

The canonical workflow source is `workflows/claim_audit.yml`.

The workflow audits selected technical repository documentation and artifacts for evidence-bounded claims. It is agent-agnostic and contains no Codex-specific, Claude-specific, OpenAI-specific, Anthropic-specific, or model-specific assumptions.

## Inputs

- `repo_path`: local repository folder to audit.
- `input_manifest`: YAML manifest listing files or globs to include in the audit corpus, including `source_role`, `extract_claims`, and `use_as_evidence` controls.

## Outputs

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

## Stages

1. Ingest files from the manifest.
2. Extract candidate claim statements only from manifest entries where `extract_claims` is true.
3. Classify claim types.
4. Define required evidence.
5. Retrieve candidate evidence.
6. Judge support.
7. Identify missing evidence.
8. Identify artifact gaps.
9. Generate remediation.
10. Render outputs.

## Non-goals

The workflow is not a GitHub bot, automatic pull request writer, exhaustive crawler, legal/compliance certification, fine-tuning loop, or general AI auditor claim.
