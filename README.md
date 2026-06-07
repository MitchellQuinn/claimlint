# ClaimLint

ClaimLint is an agentic audit workflow for turning repository claims into structured, checkable evidence objects.

The canonical audit behavior is defined in `workflows/claim_audit.yml` and executed through the shared runtime contract in `docs/runtime_contract.md`. The CLI implementation runs that workflow over a manifest-selected corpus; agent adapters under `adapters/` are thin entry points that point agents at the same workflow rather than redefining it.

v0.1 is a small, deterministic repository claim auditor. It reads selected repository documentation and artifacts, extracts explicit claims, searches the selected corpus for evidence, records missing evidence and artifact gaps, and renders JSONL plus Markdown outputs.

Current status: v0.1 proof of concept. Output quality is expected to vary; the current goal is to demonstrate the workflow contract and evidence-bounded report structure.

## What it solves

Technical repositories often make claims about capabilities, metrics, runtime behaviour, architecture, or reviewability without linking those claims to inspectable artifacts. ClaimLint makes that gap explicit. It does not decide whether a project is good; it records what the selected repository evidence can and cannot support.

## What v0.1 does

- Loads a manifest-selected corpus.
- Chunks Markdown and text-like artifacts with traceable line ranges.
- Extracts candidate claims with conservative heuristics.
- Classifies claim types and required evidence.
- Retrieves candidate evidence using token overlap.
- Assigns evidence-bounded verdicts.
- Writes remediation and evidence summaries.

## What v0.1 does not do

It is not a legal, compliance, scientific, or safety certification tool. It does not run a GitHub bot, write pull requests, crawl arbitrary repositories outside the manifest, use a hosted model API, run local open-weight models, fine-tune models, or claim exhaustive repository auditing.

## CLI

```bash
claimlint audit \
  --repo /path/to/repository \
  --manifest /path/to/input_manifest.yml
```

`--out` is optional and defaults to `output`. Each audit writes to a timestamped folder under the output root, such as `output/bounded-monocular-perception-20260607-1718Z`.

Required outputs:

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

## Architecture

ClaimLint keeps four layers separate:

1. Workflow contract: `workflows/claim_audit.yml`
2. Runtime contract: `docs/runtime_contract.md`
3. Agent adapters: `adapters/`
4. Implementation: `src/claimlint/`

The workflow file is the canonical description of the audit. Adapters point to that workflow and the shared runtime contract; they do not redefine either one.

## Adapter Status

The initial Codex and Claude Code adapter files are present but untested. See `adapters/status.yml`.

## Verdict Example

A README metric claim may be `partially_supported` when a matching metric file exists, but an evaluation command or released checkpoint hash is missing. ClaimLint records found evidence, missing evidence, artifact gaps, risk, and recommended remediation separately.

## Future Stages

Future work may add evaluated local backends, richer retrieval, benchmark evaluation, and LoRA-related experiments. Those are not part of v0.1.
