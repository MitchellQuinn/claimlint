# Adapter Contract

Adapters explain how a particular agent system discovers and uses ClaimLint.

Adapters must point to:

- `workflows/claim_audit.yml`
- `docs/runtime_contract.md`
- `schemas/claim_record.schema.json`

Adapters must not redefine the workflow, create separate CLI commands, claim compatibility that has not been tested, or add backend-specific tuning as source of truth.

