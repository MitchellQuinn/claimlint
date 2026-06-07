---
name: claimlint
description: Audit technical repository claims against repository evidence using structured claim records, support verdicts, missing evidence, artifact gaps, and remediation outputs.
---

# ClaimLint

Use this skill when asked to audit repository claims, README claims, technical writeups, model cards, metric claims, incident reports, or evidence packets.

ClaimLint turns repository claims into structured, checkable evidence objects.

## Source of truth

The canonical workflow is:

- `workflows/claim_audit.yml`

The runtime contract is:

- `docs/runtime_contract.md`

The output schema is:

- `schemas/claim_record.schema.json`

Supporting docs:

- `docs/workflow_contract.md`
- `docs/claim_taxonomy.md`
- `docs/verdict_rules.md`

Do not treat this skill file as the workflow source. This skill explains how to apply the workflow.

## How to use

If the CLI is available, run:

```bash
claimlint audit \
  --repo /path/to/repository \
  --manifest /path/to/input_manifest.yml \
  --out /path/to/output_dir
```

If the CLI is not available, perform the workflow manually and emit outputs matching the same schema and file names.

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

## Core safety rule

Do not mark claims as supported merely because they sound plausible.

A claim may be historically plausible but not independently verifiable from released repository artifacts. In that case, record found evidence, missing evidence, and artifact gaps separately.

## Non-goals

Do not present the audit as legal, compliance, safety, or scientific certification.
Do not imply exhaustive repository auditing.
Do not silently modify the target repository.
Do not claim compatibility with an adapter unless tested.

