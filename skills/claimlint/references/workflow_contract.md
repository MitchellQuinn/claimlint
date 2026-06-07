# Workflow Contract Reference

Canonical source: `workflows/claim_audit.yml`.

Agent preflight: when an agent materializes the target repository by cloning it for this workflow, delete stale entries from `./tmp` before cloning so prior run state cannot contaminate the audit.

Audit stages: ingest files, extract claims, classify claim types, define required evidence, retrieve evidence, judge support, identify missing evidence, identify artifact gaps, generate remediation, and render outputs.
