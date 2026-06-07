# Runtime Contract

The CLI is the shared runtime surface.

```bash
claimlint audit \
  --repo /path/to/repository \
  --manifest /path/to/input_manifest.yml \
  --out /path/to/output_dir
```

The command must create the output directory if it does not exist.

## Required outputs

- `claims.jsonl`
- `claims_report.md`
- `remediation_tasks.md`
- `evidence_packet.md`
- `run_manifest.json`

Optional debug output may be written under `debug/`.

The required five output files must exist even if no auditable claims are found.

## Runtime behaviour

The CLI loads and validates the input manifest, reads manifest-selected files, chunks supported files, extracts candidate claims, classifies them, defines required evidence, retrieves evidence, judges support, records missing evidence and artifact gaps, renders outputs, and saves run metadata.

## Exit codes

- `0`: audit completed successfully
- `1`: invalid arguments or missing paths
- `2`: manifest validation failed
- `3`: schema validation failed
- `4`: runtime error

A successful audit with zero claims exits `0`.

