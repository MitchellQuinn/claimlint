# Claude Code Adapter

This adapter installs the ClaimLint skill for Claude Code-style agents.

The canonical workflow remains `workflows/claim_audit.yml`.
The shared runtime contract remains `docs/runtime_contract.md`.

Run audits with the shared CLI:

```bash
claimlint audit --repo /path/to/repository --manifest /path/to/input_manifest.yml
```

Status: untested. Do not claim Claude Code compatibility until an end-to-end adapter run has been verified.
