# ClaimLint Evidence Packet

## Safely supported claims

- claim_001_d363eafb: The canonical audit behavior is defined in `workflows/claim_audit.yml` and executed through the shared runtime contract in `docs/runtime_contract.md`.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_002_396d080e: Output quality is expected to vary; the current goal is to demonstrate the workflow contract and evidence-bounded report structure.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_004_d332528a: Classifies claim types and required evidence.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_009_40f9ffe3: A README metric claim may be `partially_supported` when a matching metric file exists, but an evaluation command or released checkpoint hash is missing.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_012_c7c85a6d: ClaimLint v0.1 is organized around four separate layers.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_013_b0f67530: `docs/runtime_contract.md` defines the shared CLI surface and required output files.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_014_86626d3e: Adapter files point to the workflow and runtime contract.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.
- claim_016_3a3d5688: `src/claimlint/` implements the runtime contract with deterministic ingestion, extraction, retrieval, judgement, schema validation, and rendering.
  Verdict: supported. Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

## Partially supported claims with caveats

None.

## Claims requiring human/external review

None.

## Claims not supported by selected corpus

None.

## Overclaimed wording

None.

## Suggested README wording improvements

- Link claims directly to selected evidence artifacts where possible.
- Add caveats when metrics depend on missing checkpoints, protocols, or external environments.
- Remove or narrow claims that go beyond selected repository evidence.
