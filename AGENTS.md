# ClaimLint agent instructions

ClaimLint has strict layer separation:

1. Workflow contract
2. Runtime contract
3. Agent adapters
4. Implementation

Do not collapse these layers.

The canonical workflow is `workflows/claim_audit.yml`.

The shared runtime contract is `docs/runtime_contract.md`.

The implementation under `src/claimlint/` must satisfy those contracts.

Agent adapters under `adapters/` must not redefine the workflow or CLI.

Do not claim adapter compatibility unless tested.

Do not build out-of-scope features for v0.1:
- UI
- GitHub bot
- automatic PR writer
- arbitrary repo crawler
- local model backend
- fine-tuning loop
- complex autonomous orchestration

Before finishing implementation work, run tests and ensure the CLI produces:
- claims.jsonl
- claims_report.md
- remediation_tasks.md
- evidence_packet.md
- run_manifest.json

