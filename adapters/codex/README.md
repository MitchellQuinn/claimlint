# Codex Adapter

This adapter installs the ClaimLint skill for Codex-style agents.

The canonical workflow remains `workflows/claim_audit.yml`.
The shared runtime contract remains `docs/runtime_contract.md`.

Run audits with the shared CLI:

```bash
clipboard-raccoon audit --repo /path/to/repository --manifest /path/to/input_manifest.yml --out /path/to/output_dir
```

Status: untested. Do not claim Codex compatibility until an end-to-end adapter run has been verified.

