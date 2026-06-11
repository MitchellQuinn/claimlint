---
name: claimlint
description: Run ClaimLint audits for manifest-selected technical repository claims using the shared CLI, canonical workflow contract, and required evidence-bounded outputs.
---

# ClaimLint

Use this skill when asked to audit repository claims, README claims, technical writeups, model cards, metric claims, incident reports, or evidence packets with ClaimLint.

ClaimLint turns repository claims into structured, checkable evidence objects.

## Source of truth

The canonical workflow is:

- `workflows/claim_audit.yml`

The runtime contract is:

- `docs/runtime_contract.md`

The output schema is:

- `schemas/claim_record.schema.json`

Supporting docs:

- `docs/adapter_contract.md`
- `docs/manifest_contract.md`
- `docs/workflow_contract.md`
- `docs/claim_taxonomy.md`
- `docs/verdict_rules.md`

Do not treat this skill file as the workflow source. This skill explains how to apply the workflow.

## How to use

Before running an audit, read the canonical workflow and runtime contract.

For an existing local repository, use:

```bash
claimlint audit \
  --repo /path/to/repository \
  --manifest /path/to/input_manifest.yml
```

Do not pass `--out` unless the user explicitly requests a different output root. By default, ClaimLint writes timestamped audit artifacts under `./output`.

For an explicit Git repository URL, use the remote materialization wrapper:

```bash
claimlint audit-remote https://github.com/org/repo
```

If the user provides a Git URL, do not clone manually into an ad hoc directory. Ask the user to confirm the temporary clone root and output root, then pass those paths to `audit-remote` with `--work-root` and `--out`. If the user accepts defaults, use `--yes` so ClaimLint uses `~/.claimlint/<repo-name>/worktrees` and `~/.claimlint/<repo-name>/runs`.

For arbitrary Git URLs without a user-supplied manifest path, omit `--manifest`. ClaimLint will generate a starter manifest inside the temporary clone and snapshot it beside the reports. If the user supplies a manifest path and it is missing, ask whether to rerun with `--generate-manifest` because the missing path may be a typo. Do not crawl arbitrary repository contents outside the manifest or silently keep cloned repositories. Use `--keep-worktree` only when the user asks to retain the clone.

If the user does not provide a manifest path, use an unambiguous `input_manifest.yml` in the target repository. If more than one manifest is plausible, ask for the manifest path before auditing.

If the `claimlint` command is not available, install or activate the ClaimLint package in the current Python environment rather than inventing a separate execution path. In the ClaimLint repository during development, prefer the repo's existing virtual environment or editable install.

## Required behaviour

For each claim:

1. Extract the claim text from source material.
2. Classify the claim type.
3. Identify what evidence would be required.
4. Search the selected repository corpus for supporting or contradictory evidence.
5. Record found evidence.
6. Record missing evidence.
7. Record artifact gaps.
8. Assign a support verdict.
9. State risk and uncertainty.
10. Suggest remediation.

After the CLI exits successfully, verify that the newest timestamped output directory contains all required runtime-contract outputs:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Remote audits may also write `materialization.json` and an `input_manifest.yml` snapshot beside the required outputs.

Report the output directory and whether each required artifact exists. A successful audit with zero claims is still valid if all five files exist.

## Core safety rule

Do not mark claims as supported merely because they sound plausible.

A claim may be historically plausible but not independently verifiable from released repository artifacts. In that case, record found evidence, missing evidence, and artifact gaps separately.

## Adapter boundary

The Codex adapter discovers and applies ClaimLint. It must not redefine the workflow, create a separate CLI, tune a backend as source of truth, or claim Codex compatibility unless a Codex end-to-end run has been tested.

## Non-goals

Do not present the audit as legal, compliance, safety, or scientific certification.
Do not imply exhaustive repository auditing.
Do not silently modify the target repository.
Do not claim compatibility with an adapter unless tested.
