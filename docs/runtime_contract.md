# Runtime Contract

The CLI is the shared runtime surface.

## Local audit

```bash
claimlint audit \
  --repo /path/to/repository \
  --manifest /path/to/input_manifest.yml \
  [--out /path/to/output_root]
```

`--out` is optional and defaults to `output`. The command must create the output root if it does not exist and write required outputs to a timestamped child directory named `<repo-folder>-YYYYMMDD-HHMMZ`.

## Remote audit materialization

`audit-remote` is a materialization wrapper around the same audit workflow. It clones an explicit Git repository into a controlled temporary worktree, runs `claimlint audit` against the clone, writes outputs to a controlled output root, and deletes the temporary worktree by default.

```bash
claimlint audit-remote https://github.com/org/repo \
  [--manifest input_manifest.yml] \
  [--generate-manifest] \
  [--ref branch-or-tag] \
  [--work-root /path/to/temporary/worktrees] \
  [--out /path/to/output_root] \
  [--keep-worktree] \
  [--yes]
```

If `--manifest` is omitted, ClaimLint writes a starter manifest to `.claimlint/input_manifest.yml` inside the temporary clone. Relative manifest paths are resolved inside the cloned repository. Absolute manifest paths are treated as external manifests supplied by the user.

If `--manifest` is supplied and the manifest is missing, ClaimLint fails by default to avoid masking a typo. If `--manifest` is supplied with `--generate-manifest` and the repo-relative manifest is missing, ClaimLint writes the starter manifest at that repo-relative path. Generated manifests are starter corpus selections, not exhaustive crawls.

If `--work-root` or `--out` is omitted in an interactive terminal, the CLI prompts with default suggestions under `~/.claimlint/<repo-name>/worktrees` and `~/.claimlint/<repo-name>/runs`. In non-interactive execution or with `--yes`, those defaults are used without prompting.

`audit-remote` writes the same required outputs as `audit`. It may also write `materialization.json` beside those outputs to record the Git URL, ref, clone directory, output root, and cleanup behavior. It also snapshots the manifest used for the run as `input_manifest.yml` beside the reports because the cloned worktree may be deleted.

## Required outputs

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Optional debug output may be written under `debug/`.

The required five output files must exist even if no auditable claims are found.

## Runtime behaviour

The `audit` command loads and validates the input manifest, reads manifest-selected files, chunks supported files, extracts candidate claims only from entries where `extract_claims` is true, classifies them, defines required evidence, retrieves evidence only from chunks where `use_as_evidence` is true, judges support, records missing evidence and artifact gaps, renders outputs, and saves run metadata.

The `audit-remote` command does not redefine the workflow. It materializes a user-specified Git repository and delegates to the same local audit runtime. It uses an explicit manifest when supplied, otherwise generates a starter manifest inside the temporary clone. It does not crawl arbitrary repository contents outside the manifest or silently keep cloned repositories after a successful run.

## Exit codes

- `0`: audit completed successfully
- `1`: invalid arguments or missing paths
- `2`: manifest validation failed
- `3`: schema validation failed
- `4`: runtime error

A successful audit with zero claims exits `0`.
