# Claim Taxonomy

## capability_claim

A statement about what the system can do.

Example: This system estimates vehicle distance from a fixed monocular camera.

## metric_claim

A statement involving numerical performance.

Example: The selected model achieved 0.015856 m synthetic validation MAE.

## runtime_claim

A statement about live or operational behaviour.

Example: The live runtime supports trace capture.

## architecture_claim

A statement about system structure.

Example: The system separates locator, foreground extraction, preprocessing, and model inference.

## generalisation_claim

A statement about transfer beyond the immediate evidence.

Example: The approach transfers to real camera footage.

## bounded_non_claim

A statement limiting what is being claimed.

Example: This is not a general-purpose monocular 3D vision system.

## process_claim

A statement about method or workflow.

Example: Failures were investigated through trace-backed incident analysis.

## adoption_usability_claim

A statement about reviewability, maintainability, or usability.

Example: The repository is reviewable by another engineer.

## other_claim

A claim-like statement that does not fit the above categories.

## Claim domains

Claim records also carry `claim_domain` so report generation can separate unlike claims that share a `claim_type`.

- `licensing_rights`: license, copyright, permissions, and rights statements.
- `dataset_redistribution`: dataset or third-party source-data redistribution statements.
- `artifact_distribution`: model weights, checkpoints, tensor corpora, manifests, prediction exports, or similar artifact availability statements.
- `model_performance`: metrics, evaluation, validation, training, or scientific/model-performance statements.
- `generalisation_scope`: transfer, real-world, production, robustness, limitations, and scope caveats.
- `technical_capability`, `runtime_behavior`, `architecture`, `documentation_policy`, `process_traceability`, `adoption_usability`, and `other`: implementation, runtime, structure, policy, process, usability, or fallback domains.

This distinction is especially important for `bounded_non_claim`: a rights limitation, a dataset redistribution limitation, a generalisation caveat, and a documentation policy instruction should not be reported as the same class of finding.

## Report metadata

Each claim record includes:

- `claim_importance`: `high`, `medium`, or `low`.
- `review_action`: the recommended review treatment, such as adding evidence, narrowing a claim, clarifying wording, human review, keeping evidence linked, no action, or ignoring a low-quality extraction.
- `source_role`: whether the source file is a claim source, reference material, schema, workflow contract, runtime contract, adapter contract, example output, source code, or test fixture.
- `is_auditable_claim`: whether the record should be treated as an auditable project claim for priority findings and remediation.
- `extraction_quality`: whether the extracted text is an audit-ready claim, bounded context, caveat/scope note, policy statement, metric data point, taxonomy definition, verdict-rule definition, schema definition, workflow instruction, runtime instruction, adapter instruction, heading label, table header, incomplete fragment, code/config fragment, or other low-quality extraction.
