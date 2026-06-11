# Codex Adapter Verification

This procedure verifies that Codex can discover the ClaimLint skill and run the shared CLI without redefining the workflow.

## Personal skill install

To test ClaimLint as a user-wide Codex skill, copy the skill folder with `cmd.exe`:

```cmd
mkdir "%USERPROFILE%\.agents\skills\claimlint"
xcopy /E /I /Y "C:\Development\claimlint\skills\claimlint" "%USERPROFILE%\.agents\skills\claimlint"
```

Or copy the folder manually in Explorer:

- from: `C:\Development\claimlint\skills\claimlint`
- to: `C:\Users\Mitch\.agents\skills\claimlint`

Restart Codex or start a new Codex thread after copying the skill.

## Preconditions

- ClaimLint is installed or available in the active Python environment.
- The repository is opened at the ClaimLint root.
- The Codex adapter skill has been installed as a personal skill or with `adapters/codex/install.sh` or `adapters/codex/install.ps1`.

If PowerShell blocks `install.ps1` because it is unsigned, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\adapters\codex\install.ps1
```

Or install the skill manually:

```powershell
New-Item -ItemType Directory -Force -Path .\.agents\skills\claimlint
Copy-Item -Path .\skills\claimlint\* -Destination .\.agents\skills\claimlint -Recurse -Force
```

## Codex smoke prompt

Ask Codex:

```text
Use the ClaimLint skill to audit tests/fixtures/small_repo with manifest tests/fixtures/small_repo/input_manifest.yml. Do not pass --out. Verify the required output files under ./output.
```

The expected CLI command shape is:

```bash
claimlint audit --repo tests/fixtures/small_repo --manifest tests/fixtures/small_repo/input_manifest.yml
```

Codex must not pass `--out` for this smoke test.

## Remote smoke prompt

For a remote materialization smoke test, ask Codex to use `claimlint audit-remote` with a Git URL and an explicit manifest. Codex should ask you to confirm temporary clone and output roots before running the command.

Expected command shape after you accept defaults:

```bash
claimlint audit-remote https://github.com/org/repo --yes
```

Expected behavior:

- clone under `~/.claimlint/<repo-name>/worktrees`
- write reports under `~/.claimlint/<repo-name>/runs`
- write `materialization.json` with clone/output provenance
- write `input_manifest.yml` as a snapshot of the manifest used
- delete the temporary worktree unless `--keep-worktree` is requested

If the user supplies a manifest path and the remote repository does not contain it, Codex should ask before using:

```bash
claimlint audit-remote https://github.com/org/repo --generate-manifest --yes
```

When no manifest is supplied, ClaimLint generates a starter manifest automatically. The generated manifest should be recorded in `materialization.json` with `generated_manifest: true`.

## Required evidence

Record the timestamped output directory under `./output` and confirm these files exist:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Also confirm `run_manifest.json` reports:

- `tool_name`: `claimlint`
- `workflow_id`: `claimlint.claim-audit`
- `repo_path`: `.`
- `manifest_path`: `input_manifest.yml`

## Status update rule

Only update `adapters/status.yml` from `untested` after the Codex smoke prompt succeeds end to end in an actual Codex session. A direct CLI test is useful implementation evidence, but it is not adapter compatibility evidence by itself.
