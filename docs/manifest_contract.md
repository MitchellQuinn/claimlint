# Manifest Contract

The input manifest selects the audit corpus. ClaimLint v0.1 does not perform broad repository crawling outside manifest-selected files.

Supported include entries:

- `path`: explicit repository-relative path.
- `glob`: repository-relative glob.
- `role`: corpus role used for retrieval boosts and reporting.
- `source_role`: source semantics used for extraction and reporting.
- `extract_claims`: whether this file may produce candidate claims.
- `use_as_evidence`: whether this file may be used as candidate evidence.

Suggested `source_role` values:

- `claim_source`
- `reference_only`
- `schema_reference`
- `workflow_contract`
- `runtime_contract`
- `adapter_contract`
- `example_output`
- `source_code`
- `test_fixture`

If `source_role` is omitted, it defaults to `claim_source` unless a legacy `role`
maps directly to a contract/reference role. If `extract_claims` is omitted, it
defaults to `true` for `claim_source` and `false` for other source roles.
`use_as_evidence` defaults to `true`.

Known reference and contract paths are protected when selected by broad globs:
`docs/claim_taxonomy.md` and `docs/verdict_rules.md` default to
`reference_only`, `schemas/**/*.json` defaults to `schema_reference`,
`workflows/**/*.yml` defaults to `workflow_contract`, and runtime/adapter
contract documents default to their matching contract roles. These protected
paths are not extracted from broad globs unless they are selected by an explicit
path entry for auditing.

Files with `extract_claims: false` are not candidate claim sources, but they may
still be chunked, indexed, and used as evidence when `use_as_evidence: true`.
Claims, chunks, run-manifest entries, and claim records preserve `source_role`.

Supported exclude entries:

- `glob`: repository-relative glob to ignore.

Supported limits:

- `max_file_bytes`
- `max_total_files`

Missing explicit paths are recorded as manifest warnings. If all selected inputs are missing or unsupported, the CLI exits with manifest validation failure.
