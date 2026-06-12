# Codex Adapter Smoke Verification

## 2026-06-12 Local Audit Smoke

This smoke run verifies that Codex can apply the ClaimLint adapter instructions and run the shared CLI without redefining the workflow.

Environment:

- Codex session workspace: `C:\Development\claimlint`
- Verification procedure: `adapters/codex/VERIFY.md`
- Runtime: ClaimLint editable install in the repository virtual environment

Command run by Codex:

```powershell
.\.venv\Scripts\claimlint.exe audit --repo tests\fixtures\small_repo --manifest tests\fixtures\small_repo\input_manifest.yml
```

Equivalent shared CLI shape:

```bash
claimlint audit --repo tests/fixtures/small_repo --manifest tests/fixtures/small_repo/input_manifest.yml
```

No `--out` argument was passed.

Output directory:

```text
output/small_repo-20260612-1223Z
```

Required outputs verified:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Run manifest fields verified:

- `tool_name`: `claimlint`
- `workflow_id`: `claimlint.claim-audit`
- `repo_path`: `.`
- `manifest_path`: `input_manifest.yml`

Result: passed.

Scope note: this records the Codex local-audit adapter smoke. Remote materialization behavior is covered by CLI tests in `tests/test_cli_audit_remote.py`; do not describe a Codex GUI remote smoke unless one is separately recorded.
