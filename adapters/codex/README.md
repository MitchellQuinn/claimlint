# Codex Adapter

This adapter makes ClaimLint discoverable to Codex-style agents without changing the ClaimLint workflow or CLI.

The canonical workflow remains `workflows/claim_audit.yml`.
The shared runtime contract remains `docs/runtime_contract.md`.
The claim record schema remains `schemas/claim_record.schema.json`.

## Personal skill install

For a user-wide Codex skill, copy `skills/claimlint` to your personal Codex skills directory:

```cmd
mkdir "%USERPROFILE%\.agents\skills\claimlint"
xcopy /E /I /Y "C:\Development\claimlint\skills\claimlint" "%USERPROFILE%\.agents\skills\claimlint"
```

Or copy the folder manually in Explorer:

- from: `C:\Development\claimlint\skills\claimlint`
- to: `C:\Users\Mitch\.agents\skills\claimlint`

Restart Codex or start a new Codex thread after copying the skill.

## Repo skill install

From the repository root, install the repo-scoped Codex skill:

```bash
./adapters/codex/install.sh
```

On Windows PowerShell:

```powershell
.\adapters\codex\install.ps1
```

If PowerShell blocks unsigned scripts, either run the script with a one-time process bypass:

```powershell
powershell -ExecutionPolicy Bypass -File .\adapters\codex\install.ps1
```

Or install the skill manually:

```powershell
New-Item -ItemType Directory -Force -Path .\.agents\skills\claimlint
Copy-Item -Path .\skills\claimlint\* -Destination .\.agents\skills\claimlint -Recurse -Force
```

The install scripts copy `skills/claimlint` to `.agents/skills/claimlint`, which is the Codex repo-skill discovery location. They do not install Python dependencies or alter the ClaimLint runtime.

## Audit command

Codex must run local audits with the shared CLI:

```bash
claimlint audit --repo /path/to/repository --manifest /path/to/input_manifest.yml
```

Do not pass `--out` unless the user explicitly requests a different output root. The CLI default writes audit artifacts under `./output`.

For Git URLs, Codex should use the controlled remote materialization wrapper:

```bash
claimlint audit-remote https://github.com/org/repo
```

Before running a remote audit, ask the user to confirm the temporary clone root and output root. Defaults are `~/.claimlint/<repo-name>/worktrees` and `~/.claimlint/<repo-name>/runs`. Pass confirmed paths with `--work-root` and `--out`, or pass `--yes` only when the user accepts the defaults. Do not clone into an ad hoc directory.

For arbitrary Git URLs without a user-supplied manifest path, omit `--manifest`; ClaimLint will generate a starter manifest inside the temporary clone. If the user supplies a manifest path and it is missing, ask whether to rerun with `--generate-manifest`. Generated manifests are starter corpus selections written inside the temporary clone; they are not claims of exhaustive repository coverage.

## Optional plugin package

`adapters/codex/plugin/claimlint` contains a local Codex plugin package that bundles the same ClaimLint skill. This is packaging only; the canonical workflow and runtime contract remain in the ClaimLint repository.

## Verification

Use `adapters/codex/VERIFY.md` for the Codex smoke-test procedure. The adapter remains untested until an end-to-end Codex run has verified that the CLI produces:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Status: untested. Do not claim Codex compatibility until an end-to-end Codex adapter run has been verified.
