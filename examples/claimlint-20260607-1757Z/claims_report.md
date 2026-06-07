# ClaimLint Claims Report

## Executive Summary

- Repository: .
- Manifest: examples/claimlint-self-audit/claimlint-github-manifest.yml
- Workflow version: 0.1.0
- Run timestamp: 2026-06-07T17:57:32+00:00
- Claim count: 17
- Auditable claim count: 8
- Repository claim surface status: high_claim_surface
- High-importance claims: 1
- Claims requiring action: 0
- Boundary/non-goal statements: 7
- Suppressed reference or low-quality records: 2

Static repository review only unless otherwise stated. Smoke tests are not metric reproduction, and external hardware/environment claims may require human review.

Rights, licensing, dataset redistribution, and artifact distribution claims are separated from technical, scientific, and model-performance claims by `claim_domain`.

## Verdict Summary

| Verdict | Count |
| --- | ---: |
| ambiguous | 9 |
| supported | 8 |

## Domain Summary

| Domain | Count | Auditable | High Importance | Requiring Action | Suppressed/Reference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Artifact Distribution | 1 | 1 | 1 | 0 | 0 |
| Runtime Behavior | 3 | 3 | 0 | 0 | 0 |
| Architecture | 2 | 2 | 0 | 0 | 0 |
| Process and Traceability | 1 | 0 | 0 | 0 | 1 |
| Other | 10 | 2 | 0 | 0 | 1 |

## Priority Findings

No priority findings outside auditable claim-source records.

## High-Importance Claims Requiring Action

| Claim | Domain | Verdict | Action | Source |
| --- | --- | --- | --- | --- |
| None | - | - | - | - |

## Claims Grouped by Domain

### Artifact Distribution

- claim_009_40f9ffe3 | Artifact Distribution | high | supported | keep_evidence_linked | A README metric claim may be `partially_supported` when a matching metric file exists, but an evaluation command or released checkpoint h...

### Runtime Behavior

- claim_001_d363eafb | Runtime Behavior | medium | supported | no_action | The canonical audit behavior is defined in `workflows/claim_audit.yml` and executed through the shared runtime contract in `docs/runtime_...
- claim_014_86626d3e | Runtime Behavior | medium | supported | no_action | Adapter files point to the workflow and runtime contract.
- claim_016_3a3d5688 | Runtime Behavior | medium | supported | no_action | `src/claimlint/` implements the runtime contract with deterministic ingestion, extraction, retrieval, judgement, schema validation, and r...

### Architecture

- claim_002_396d080e | Architecture | medium | supported | no_action | Output quality is expected to vary; the current goal is to demonstrate the workflow contract and evidence-bounded report structure.
- claim_012_c7c85a6d | Architecture | medium | supported | no_action | ClaimLint v0.1 is organized around four separate layers.

### Process and Traceability

No audit-ready claims in this domain.
- 1 suppressed reference or low-quality record(s) in this domain are listed separately or in the Full Claim Listing.

### Other

- claim_004_d332528a | Other | low | supported | no_action | Classifies claim types and required evidence.
- claim_013_b0f67530 | Other | low | supported | no_action | `docs/runtime_contract.md` defines the shared CLI surface and required output files.
- 1 suppressed reference or low-quality record(s) in this domain are listed separately or in the Full Claim Listing.
- 7 boundary or non-goal statement(s) in this domain are listed separately.

## Boundary / Non-Goal Statements

- claim_003_b8f6fe28 | README.md | It does not decide whether a project is good; it records what the selected repository evidence can and cannot support.
- claim_005_e2e54dc2 | README.md | What v0.1 does not do
- claim_006_c7426df8 | README.md | It is not a legal, compliance, scientific, or safety certification tool.
- claim_007_1d60c5c4 | README.md | It does not run a GitHub bot, write pull requests, crawl arbitrary repositories outside the manifest, use a hosted model API, run local open-weight models, f...
- claim_008_ab3ef756 | README.md | Adapters point to that workflow and the shared runtime contract; they do not redefine either one.
- claim_015_bd36cda5 | docs/architecture.md | They must not redefine the workflow or invent a different CLI.
- claim_017_286c1bfe | docs/architecture.md | v0.1 includes a model backend abstraction but does not depend on hosted or local model inference.

## Suppressed Reference Records

- claim_010_96982355 | claim_source | roadmap_statement | Future work may add evaluated local backends, richer retrieval, benchmark evaluation, and LoRA-related experiments.
- claim_011_565d435d | claim_source | roadmap_statement | Those are not part of v0.1.

## Full Claim Listing

### claim_001_d363eafb

- Claim: The canonical audit behavior is defined in `workflows/claim_audit.yml` and executed through the shared runtime contract in `docs/runtime_contract.md`.
- Source: README.md (section: ClaimLint; line 5)
- Source role: claim_source
- Auditable claim: True
- Type: runtime_claim
- Domain: Runtime Behavior
- Importance: medium
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: high_claim_surface
- Verification mode: artifact_presence_review
- Verdict: supported
- Confidence: high

Found evidence:
- examples/claimlint-self-audit/smoke_test.md (section: ClaimLint Self-Audit Smoke Test; lines 1-4): Candidate evidence from examples/claimlint-self-audit/smoke_test.md, lines 1-4, matched terms: audit, behavior, canonical, claim, contract, defined, docs, executed. Strength: strong. Source role: reference_only.
- examples/claimlint-self-audit/claimlint-github-manifest.yml (section: line range; lines 1-80): Candidate evidence from examples/claimlint-self-audit/claimlint-github-manifest.yml, lines 1-80, matched terms: audit, claim, contract, docs, environment, implementation, md, notes. Strength: strong. Source role: reference_only.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: audit, claim, contract, docs, example, md, output, runtime. Strength: contradictory. Source role: runtime_contract.
- README.md (section: ClaimLint > Architecture; lines 47-57): Candidate evidence from README.md, lines 47-57, matched terms: audit, canonical, claim, contract, docs, implementation, md, runtime. Strength: strong. Source role: claim_source.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: audit, behavior, canonical, claim, configuration, contract, docs, environment. Strength: contradictory. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_002_396d080e

- Claim: Output quality is expected to vary; the current goal is to demonstrate the workflow contract and evidence-bounded report structure.
- Source: README.md (section: ClaimLint; line 9)
- Source role: claim_source
- Auditable claim: True
- Type: architecture_claim
- Domain: Architecture
- Importance: medium
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: medium_claim_surface
- Verification mode: documentation_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: architecture, bounded, contract, contracts, documentation, evidence, files, output. Strength: contradictory. Source role: reference_only.
- docs/claim_taxonomy.md (section: Claim Taxonomy > Report metadata; lines 68-76): Candidate evidence from docs/claim_taxonomy.md, lines 68-76, matched terms: bounded, contract, evidence, output, quality, report, source, workflow. Strength: strong. Source role: reference_only.
- src/claimlint/judge_support.py (section: line range; lines 321-400): Candidate evidence from src/claimlint/judge_support.py, lines 321-400, matched terms: architecture, contract, documentation, evidence, files, goal, interfaces, output. Strength: contradictory. Source role: source_code.
- src/claimlint/classify_claims.py (section: line range; lines 1-80): Candidate evidence from src/claimlint/classify_claims.py, lines 1-80, matched terms: architecture, bounded, contracts, documentation, evidence, files, interfaces, module. Strength: strong. Source role: source_code.
- src/claimlint/judge_support.py (section: line range; lines 81-160): Candidate evidence from src/claimlint/judge_support.py, lines 81-160, matched terms: architecture, contract, contracts, documentation, evidence, files, goal, interfaces. Strength: contradictory. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_003_b8f6fe28

- Claim: It does not decide whether a project is good; it records what the selected repository evidence can and cannot support.
- Source: README.md (section: ClaimLint > What it solves; line 13)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- src/claimlint/judge_support.py (section: line range; lines 321-400): Candidate evidence from src/claimlint/judge_support.py, lines 321-400, matched terms: does, evidence, not, project, repository, selected, support, what. Strength: contradictory. Source role: source_code.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: does, evidence, not, records, repository, selected, support, whether. Strength: contradictory. Source role: reference_only.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: does, evidence, not, records, repository, selected, whether. Strength: contradictory. Source role: runtime_contract.
- workflows/claim_audit.yml (section: line range; lines 1-80): Candidate evidence from workflows/claim_audit.yml, lines 1-80, matched terms: cannot, evidence, not, repository, selected, support, what. Strength: contradictory. Source role: workflow_contract.
- docs/environment.md (section: Environment > External Environment Limitations; lines 24-28): Candidate evidence from docs/environment.md, lines 24-28, matched terms: can, does, evidence, not, repository, selected. Strength: contradictory. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_004_d332528a

- Claim: Classifies claim types and required evidence.
- Source: README.md (section: ClaimLint > What v0.1 does; line 20)
- Source role: claim_source
- Auditable claim: True
- Type: other_claim
- Domain: Other
- Importance: low
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: low_claim_surface
- Verification mode: documentation_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: artifact, claim, classifies, documentation, evidence, required, types. Strength: contradictory. Source role: reference_only.
- src/claimlint/classify_claims.py (section: line range; lines 1-80): Candidate evidence from src/claimlint/classify_claims.py, lines 1-80, matched terms: artifact, claim, direct, documentation, evidence, required, supporting, types. Strength: strong. Source role: source_code.
- src/claimlint/judge_support.py (section: line range; lines 81-160): Candidate evidence from src/claimlint/judge_support.py, lines 81-160, matched terms: artifact, claim, direct, documentation, evidence, required, supporting, types. Strength: contradictory. Source role: source_code.
- workflows/claim_audit.yml (section: line range; lines 1-80): Candidate evidence from workflows/claim_audit.yml, lines 1-80, matched terms: artifact, claim, documentation, evidence, required, supporting, types. Strength: contradictory. Source role: workflow_contract.
- docs/workflow_contract.md (section: Workflow Contract > Stages; lines 24-36): Candidate evidence from docs/workflow_contract.md, lines 24-36, matched terms: artifact, claim, evidence, required, types. Strength: strong. Source role: workflow_contract.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_005_e2e54dc2

- Claim: What v0.1 does not do
- Source: README.md (section: ClaimLint > What v0.1 does not do; line 25)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: do, does, not, v0.1. Strength: contradictory. Source role: reference_only.
- README.md (section: ClaimLint > What it solves; lines 11-14): Candidate evidence from README.md, lines 11-14, matched terms: does, not, what. Strength: contradictory. Source role: claim_source.
- README.md (section: ClaimLint > What v0.1 does; lines 15-24): Candidate evidence from README.md, lines 15-24, matched terms: does, v0.1, what. Strength: strong. Source role: claim_source.
- docs/architecture.md (section: Architecture > v0.1 backend stance; lines 21-24): Candidate evidence from docs/architecture.md, lines 21-24, matched terms: does, not, v0.1. Strength: contradictory. Source role: claim_source.
- docs/environment.md (section: Environment > Local Filesystem Operation; lines 12-17): Candidate evidence from docs/environment.md, lines 12-17, matched terms: does, not, v0.1. Strength: contradictory. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_006_c7426df8

- Claim: It is not a legal, compliance, scientific, or safety certification tool.
- Source: README.md (section: ClaimLint > What v0.1 does not do; line 27)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/workflow_contract.md (section: Workflow Contract > Non-goals; lines 37-39): Candidate evidence from docs/workflow_contract.md, lines 37-39, matched terms: certification, compliance, legal, not. Strength: strong. Source role: workflow_contract.
- workflows/claim_audit.yml (section: line range; lines 1-80): Candidate evidence from workflows/claim_audit.yml, lines 1-80, matched terms: certification, compliance, legal, not. Strength: contradictory. Source role: workflow_contract.
- docs/claim_taxonomy.md (section: Claim Taxonomy > Claim domains; lines 55-67): Candidate evidence from docs/claim_taxonomy.md, lines 55-67, matched terms: not, scientific. Strength: moderate. Source role: reference_only.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: not, tool. Strength: contradictory. Source role: reference_only.
- src/claimlint/judge_support.py (section: line range; lines 321-400): Candidate evidence from src/claimlint/judge_support.py, lines 321-400, matched terms: not, safety. Strength: contradictory. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_007_1d60c5c4

- Claim: It does not run a GitHub bot, write pull requests, crawl arbitrary repositories outside the manifest, use a hosted model API, run local open-weight models, fine-tune models, or claim exhaustive repository auditing.
- Source: README.md (section: ClaimLint > What v0.1 does not do; line 27)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- workflows/claim_audit.yml (section: line range; lines 1-80): Candidate evidence from workflows/claim_audit.yml, lines 1-80, matched terms: arbitrary, bot, claim, fine, github, local, manifest, model. Strength: contradictory. Source role: workflow_contract.
- docs/environment.md (section: Environment > Network, API, and Model Dependencies; lines 18-23): Candidate evidence from docs/environment.md, lines 18-23, matched terms: api, claim, does, fine, hosted, local, manifest, model. Strength: contradictory. Source role: reference_only.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: api, claim, does, local, manifest, model, not, repository. Strength: contradictory. Source role: reference_only.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: auditing, claim, does, manifest, not, outside, repository, run. Strength: contradictory. Source role: runtime_contract.
- src/claimlint/render_report.py (section: line range; lines 81-160): Candidate evidence from src/claimlint/render_report.py, lines 81-160, matched terms: claim, manifest, model, not, open, repository, run, write. Strength: contradictory. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_008_ab3ef756

- Claim: Adapters point to that workflow and the shared runtime contract; they do not redefine either one.
- Source: README.md (section: ClaimLint > Architecture; line 56)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: adapters, contract, do, either, not, one, point, redefine. Strength: contradictory. Source role: reference_only.
- docs/architecture.md (section: Architecture > Agent adapters; lines 13-16): Candidate evidence from docs/architecture.md, lines 13-16, matched terms: adapters, contract, not, point, redefine, runtime, they, workflow. Strength: strong. Source role: claim_source.
- docs/adapter_contract.md (section: Adapter Contract; lines 1-12): Candidate evidence from docs/adapter_contract.md, lines 1-12, matched terms: adapters, contract, not, point, redefine, runtime, workflow. Strength: strong. Source role: adapter_contract.
- README.md (section: ClaimLint; lines 1-10): Candidate evidence from README.md, lines 1-10, matched terms: adapters, contract, point, runtime, shared, workflow. Strength: strong. Source role: claim_source.
- adapters/claude-code/README.md (section: Claude Code Adapter; lines 1-14): Candidate evidence from adapters/claude-code/README.md, lines 1-14, matched terms: contract, do, not, runtime, shared, workflow. Strength: strong. Source role: adapter_contract.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_009_40f9ffe3

- Claim: A README metric claim may be `partially_supported` when a matching metric file exists, but an evaluation command or released checkpoint hash is missing.
- Source: README.md (section: ClaimLint > Verdict Example; line 64)
- Source role: claim_source
- Auditable claim: True
- Type: other_claim
- Domain: Artifact Distribution
- Importance: high
- Review action: keep_evidence_linked
- Extraction quality: auditable_claim
- Claim surface status: low_claim_surface
- Verification mode: documentation_review
- Verdict: supported
- Confidence: high

Found evidence:
- src/claimlint/judge_support.py (section: line range; lines 321-400): Candidate evidence from src/claimlint/judge_support.py, lines 321-400, matched terms: artifact, checkpoint, claim, command, documentation, evaluation, exists, file. Strength: contradictory. Source role: source_code.
- src/claimlint/judge_support.py (section: line range; lines 81-160): Candidate evidence from src/claimlint/judge_support.py, lines 81-160, matched terms: artifact, checkpoint, claim, command, direct, documentation, evaluation, file. Strength: contradictory. Source role: source_code.
- docs/verdict_rules.md (section: Verdict Rules > partially_supported; lines 7-12): Candidate evidence from docs/verdict_rules.md, lines 7-12, matched terms: checkpoint, command, evaluation, file, metric, missing, partially, released. Strength: strong. Source role: reference_only.
- src/claimlint/judge_support.py (section: line range; lines 161-240): Candidate evidence from src/claimlint/judge_support.py, lines 161-240, matched terms: artifact, checkpoint, claim, documentation, evaluation, exists, hash, metric. Strength: strong. Source role: source_code.
- src/claimlint/classify_claims.py (section: line range; lines 1-80): Candidate evidence from src/claimlint/classify_claims.py, lines 1-80, matched terms: artifact, checkpoint, claim, direct, documentation, evaluation, file, hash. Strength: strong. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_010_96982355

- Claim: Future work may add evaluated local backends, richer retrieval, benchmark evaluation, and LoRA-related experiments.
- Source: README.md (section: ClaimLint > Future Stages; line 68)
- Source role: claim_source
- Auditable claim: False
- Type: process_claim
- Domain: Process and Traceability
- Importance: low
- Review action: ignore_low_quality_extraction
- Extraction quality: roadmap_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- tests/test_claim_extraction.py (section: line range; lines 81-160): Candidate evidence from tests/test_claim_extraction.py, lines 81-160, matched terms: add, backends, evaluated, future, local, may, retrieval, richer. Strength: strong. Source role: test_fixture.
- src/claimlint/render_report.py (section: line range; lines 401-480): Candidate evidence from src/claimlint/render_report.py, lines 401-480, matched terms: add, related. Strength: contradictory. Source role: source_code.
- src/claimlint/render_report.py (section: line range; lines 561-605): Candidate evidence from src/claimlint/render_report.py, lines 561-605, matched terms: add, related. Strength: moderate. Source role: source_code.
- docs/environment.md (section: Environment > Network, API, and Model Dependencies; lines 18-23): Candidate evidence from docs/environment.md, lines 18-23, matched terms: future, local, retrieval, work. Strength: contradictory. Source role: reference_only.
- src/claimlint/classify_claims.py (section: line range; lines 401-480): Candidate evidence from src/claimlint/classify_claims.py, lines 401-480, matched terms: add, future, may, work. Strength: moderate. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a future or roadmap statement and is not evidence that the feature already exists.

Recommended remediation:
- Keep this as roadmap context unless the wording claims the feature already exists.

### claim_011_565d435d

- Claim: Those are not part of v0.1.
- Source: README.md (section: ClaimLint > Future Stages; line 68)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: ignore_low_quality_extraction
- Extraction quality: roadmap_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/environment.md (section: Environment > External Environment Limitations; lines 24-28): Candidate evidence from docs/environment.md, lines 24-28, matched terms: not, those, v0.1. Strength: contradictory. Source role: reference_only.
- README.md (section: ClaimLint > What it solves; lines 11-14): Candidate evidence from README.md, lines 11-14, matched terms: not, those. Strength: contradictory. Source role: claim_source.
- README.md (section: ClaimLint > What v0.1 does not do; lines 25-28): Candidate evidence from README.md, lines 25-28, matched terms: not, v0.1. Strength: contradictory. Source role: claim_source.
- docs/architecture.md (section: Architecture > v0.1 backend stance; lines 21-24): Candidate evidence from docs/architecture.md, lines 21-24, matched terms: not, v0.1. Strength: contradictory. Source role: claim_source.
- docs/environment.md (section: Environment > Local Filesystem Operation; lines 12-17): Candidate evidence from docs/environment.md, lines 12-17, matched terms: not, v0.1. Strength: contradictory. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a future or roadmap statement and is not evidence that the feature already exists.

Recommended remediation:
- Keep this as roadmap context unless the wording claims the feature already exists.

### claim_012_c7c85a6d

- Claim: ClaimLint v0.1 is organized around four separate layers.
- Source: docs/architecture.md (section: Architecture; line 3)
- Source role: claim_source
- Auditable claim: True
- Type: architecture_claim
- Domain: Architecture
- Importance: medium
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: medium_claim_surface
- Verification mode: documentation_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: architecture, claimlint, contracts, documentation, evidence, files, separate, source. Strength: contradictory. Source role: reference_only.
- docs/environment.md (section: Environment > External Environment Limitations; lines 24-28): Candidate evidence from docs/environment.md, lines 24-28, matched terms: claimlint, documentation, evidence, files, separate, source, v0.1. Strength: contradictory. Source role: reference_only.
- README.md (section: ClaimLint > Architecture; lines 47-57): Candidate evidence from README.md, lines 47-57, matched terms: architecture, claimlint, four, layers, separate. Strength: strong. Source role: claim_source.
- tests/test_ingest_markdown.py (section: line range; lines 1-80): Candidate evidence from tests/test_ingest_markdown.py, lines 1-80, matched terms: architecture, claimlint, documentation, evidence, files, layers, separate, source. Strength: strong. Source role: test_fixture.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: claimlint, evidence, files, source, v0.1. Strength: contradictory. Source role: runtime_contract.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_013_b0f67530

- Claim: `docs/runtime_contract.md` defines the shared CLI surface and required output files.
- Source: docs/architecture.md (section: Architecture > Runtime contract; line 11)
- Source role: claim_source
- Auditable claim: True
- Type: other_claim
- Domain: Other
- Importance: low
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: low_claim_surface
- Verification mode: documentation_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: artifact, cli, contract, defines, docs, documentation, files, md. Strength: contradictory. Source role: reference_only.
- examples/claimlint-self-audit/smoke_test.md (section: ClaimLint Self-Audit Smoke Test; lines 1-4): Candidate evidence from examples/claimlint-self-audit/smoke_test.md, lines 1-4, matched terms: cli, contract, docs, md, output, required, runtime, shared. Strength: strong. Source role: reference_only.
- README.md (section: ClaimLint; lines 1-10): Candidate evidence from README.md, lines 1-10, matched terms: artifact, cli, contract, docs, documentation, md, output, runtime. Strength: strong. Source role: claim_source.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: cli, contract, docs, files, md, output, runtime. Strength: contradictory. Source role: runtime_contract.
- docs/runtime_contract.md (section: Runtime Contract; lines 1-13): Candidate evidence from docs/runtime_contract.md, lines 1-13, matched terms: cli, contract, output, required, runtime, shared, surface. Strength: contradictory. Source role: runtime_contract.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_014_86626d3e

- Claim: Adapter files point to the workflow and runtime contract.
- Source: docs/architecture.md (section: Architecture > Agent adapters; line 15)
- Source role: claim_source
- Auditable claim: True
- Type: runtime_claim
- Domain: Runtime Behavior
- Importance: medium
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: high_claim_surface
- Verification mode: artifact_presence_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: adapter, configuration, contract, environment, files, implementation, notes, output. Strength: contradictory. Source role: reference_only.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: adapter, contract, example, files, output, runtime, test, workflow. Strength: contradictory. Source role: runtime_contract.
- examples/claimlint-self-audit/claimlint-github-manifest.yml (section: line range; lines 1-80): Candidate evidence from examples/claimlint-self-audit/claimlint-github-manifest.yml, lines 1-80, matched terms: adapter, contract, environment, implementation, notes, runtime, smoke, test. Strength: strong. Source role: reference_only.
- docs/claim_taxonomy.md (section: Claim Taxonomy > Report metadata; lines 68-76): Candidate evidence from docs/claim_taxonomy.md, lines 68-76, matched terms: adapter, contract, example, output, point, runtime, test, workflow. Strength: strong. Source role: reference_only.
- src/claimlint/manifest.py (section: line range; lines 1-80): Candidate evidence from src/claimlint/manifest.py, lines 1-80, matched terms: adapter, contract, example, files, output, runtime, test, workflow. Strength: contradictory. Source role: source_code.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_015_bd36cda5

- Claim: They must not redefine the workflow or invent a different CLI.
- Source: docs/architecture.md (section: Architecture > Agent adapters; line 15)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/adapter_contract.md (section: Adapter Contract; lines 1-12): Candidate evidence from docs/adapter_contract.md, lines 1-12, matched terms: cli, must, not, redefine, workflow. Strength: strong. Source role: adapter_contract.
- README.md (section: ClaimLint > Architecture; lines 47-57): Candidate evidence from README.md, lines 47-57, matched terms: not, redefine, they, workflow. Strength: strong. Source role: claim_source.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: cli, not, redefine, workflow. Strength: contradictory. Source role: reference_only.
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: cli, not, they, workflow. Strength: contradictory. Source role: runtime_contract.
- adapters/claude-code/README.md (section: Claude Code Adapter; lines 1-14): Candidate evidence from adapters/claude-code/README.md, lines 1-14, matched terms: cli, not, workflow. Strength: moderate. Source role: adapter_contract.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.

### claim_016_3a3d5688

- Claim: `src/claimlint/` implements the runtime contract with deterministic ingestion, extraction, retrieval, judgement, schema validation, and rendering.
- Source: docs/architecture.md (section: Architecture > Implementation; line 19)
- Source role: claim_source
- Auditable claim: True
- Type: runtime_claim
- Domain: Runtime Behavior
- Importance: medium
- Review action: no_action
- Extraction quality: auditable_claim
- Claim surface status: high_claim_surface
- Verification mode: artifact_presence_review
- Verdict: supported
- Confidence: high

Found evidence:
- docs/manifest_contract.md (section: Manifest Contract; lines 1-52): Candidate evidence from docs/manifest_contract.md, lines 1-52, matched terms: claimlint, contract, example, extraction, output, retrieval, runtime, schema. Strength: contradictory. Source role: runtime_contract.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: claimlint, configuration, contract, deterministic, environment, extraction, implementation, notes. Strength: contradictory. Source role: reference_only.
- docs/environment.md (section: Environment > Network, API, and Model Dependencies; lines 18-23): Candidate evidence from docs/environment.md, lines 18-23, matched terms: claimlint, deterministic, environment, extraction, ingestion, judgement, rendering, retrieval. Strength: contradictory. Source role: reference_only.
- examples/claimlint-self-audit/claimlint-github-manifest.yml (section: line range; lines 81-129): Candidate evidence from examples/claimlint-self-audit/claimlint-github-manifest.yml, lines 81-129, matched terms: claimlint, contract, output, schema, smoke, src, test. Strength: strong. Source role: reference_only.
- examples/claimlint-self-audit/claimlint-github-manifest.yml (section: line range; lines 1-80): Candidate evidence from examples/claimlint-self-audit/claimlint-github-manifest.yml, lines 1-80, matched terms: claimlint, contract, environment, implementation, notes, runtime, smoke, test. Strength: moderate. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: The selected corpus contains strong matching evidence and no major missing evidence was identified.

Recommended remediation:
- None.

### claim_017_286c1bfe

- Claim: v0.1 includes a model backend abstraction but does not depend on hosted or local model inference.
- Source: docs/architecture.md (section: Architecture > v0.1 backend stance; line 23)
- Source role: claim_source
- Auditable claim: False
- Type: bounded_non_claim
- Domain: Other
- Importance: low
- Review action: keep_as_boundary_note
- Extraction quality: boundary_statement
- Claim surface status: low_claim_surface
- Verification mode: not_verifiable_from_available_material
- Verdict: ambiguous
- Confidence: low

Found evidence:
- docs/environment.md (section: Environment > Network, API, and Model Dependencies; lines 18-23): Candidate evidence from docs/environment.md, lines 18-23, matched terms: abstraction, backend, does, hosted, inference, local, model, not. Strength: contradictory. Source role: reference_only.
- docs/implementation_map.md (section: Implementation Map; lines 1-23): Candidate evidence from docs/implementation_map.md, lines 1-23, matched terms: abstraction, backend, does, inference, local, model, not, v0.1. Strength: contradictory. Source role: reference_only.
- README.md (section: ClaimLint > What v0.1 does not do; lines 25-28): Candidate evidence from README.md, lines 25-28, matched terms: does, hosted, local, model, not, v0.1. Strength: contradictory. Source role: claim_source.
- adapters/status.yml (section: line range; lines 1-12): Candidate evidence from adapters/status.yml, lines 1-12, matched terms: backend, local, model, not. Strength: moderate. Source role: adapter_contract.
- docs/environment.md (section: Environment > Local Filesystem Operation; lines 12-17): Candidate evidence from docs/environment.md, lines 12-17, matched terms: does, local, not, v0.1. Strength: contradictory. Source role: reference_only.

Missing evidence:
- None identified.

Artifact gaps:
- None identified.

Risk: This is a boundary, safety, or non-goal statement and is retained as context rather than audited as an implementation claim.

Recommended remediation:
- Keep this as a boundary or non-goal note; do not audit it as an implementation claim.
