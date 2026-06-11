# Environment

ClaimLint v0.1 runs as a local Python CLI.

## Python Runtime

- Python requirement: Python 3.11 or newer, as declared by `pyproject.toml`.
- Runtime dependencies: `PyYAML` for manifest parsing and `jsonschema` for output schema validation.
- Development test dependency: `pytest`.
- The package entry point is `claimlint`, which dispatches to `claimlint.cli:main`.

## Local Filesystem Operation

ClaimLint v0.1 is a local filesystem-only auditor. The CLI reads the repository path and manifest path supplied to `claimlint audit`, loads only manifest-selected files, and writes audit artifacts under the configured output root. When `--out` is omitted, the runtime contract default is `output`.

The implementation does not perform broad repository crawling outside manifest-selected files. Manifest include and exclude rules are the configuration boundary for the audit corpus.

## Network, API, and Model Dependencies

ClaimLint v0.1 has no required network, hosted API, or model service dependency. The default audit path uses deterministic local code for ingestion, claim extraction, classification, evidence retrieval, judgement, rendering, schema validation, and run-manifest creation.

`claimlint audit-remote` requires a local `git` executable. Network access is needed only when the explicit repository URL requires it, such as `https://github.com/org/repo`. Local Git repository paths can be used without network access.

The repository contains a model backend abstraction for future work, but v0.1 does not require a hosted model API, a local open-weight model backend, API credentials, fine tuning, or external inference services.

## External Environment Limitations

ClaimLint v0.1 performs static repository artifact review. It can verify the presence and consistency of selected files, configuration, source code, tests, documentation, and example output, but it does not verify external deployment state, service availability, credentials, hardware, camera or sensor behavior, production traffic, or human operational processes.

Claims that depend on those external environment conditions require separate human review or external test evidence outside the static audit.
