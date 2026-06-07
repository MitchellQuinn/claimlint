# Runtime Contract Reference

Run:

```bash
claimlint audit --repo /path/to/repository --manifest /path/to/input_manifest.yml
```

`--out` is optional and defaults to `output`. Required outputs are written under a timestamped child directory named `<repo-folder>-YYYYMMDD-HHMMZ`.

Required outputs: `claims.jsonl`, `claims_report.md`, `remediation_tasks.md`, `evidence_packet.md`, and `run_manifest.json`.
