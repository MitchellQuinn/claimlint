# Architecture

ClaimLint v0.1 is organized around four separate layers.

## Workflow contract

`workflows/claim_audit.yml` is the canonical, agent-agnostic workflow. It names the stages, inputs, outputs, schemas, and non-goals.

## Runtime contract

`docs/runtime_contract.md` defines the shared CLI surface and required output files. Humans, agents, CI, and future local runners use the same command shape.

`claimlint audit` is the workflow runtime for existing local repositories. `claimlint audit-remote` is a materialization wrapper that clones an explicit Git repository into a controlled temporary worktree, delegates to the same audit runtime, writes outputs to a controlled output root, and cleans up the clone by default.

## Agent adapters

`adapters/` contains system-specific discovery and installation notes. Adapter files point to the workflow and runtime contract. They must not redefine the workflow or invent a different CLI.

## Implementation

`src/claimlint/` implements the runtime contract with deterministic ingestion, extraction, retrieval, judgement, schema validation, and rendering.

## v0.1 backend stance

v0.1 includes a model backend abstraction but does not depend on hosted or local model inference. The default backend is heuristic and deterministic.
