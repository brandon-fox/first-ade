# First-ADE v0.1 Deterministic Invariant Control Plane

* Status: accepted
* Deciders: Brandon Fox
* Date: 2026-11-25

Technical Story: Introduce the thin, zero-LLM deterministic invariant control plane (`first-ade`) under `src/first_ade/` with hexagonal boundaries (`domain/`, `ports/`, `adapters/`, `cli/`) and `import-linter` dependency.

## Context and Problem Statement

Coding agents require fast (`< 5,000 ms`), deterministic guardrails across local hooks and GitHub Actions without context-window bloat. Adding `first-ade` alongside `ade-compliance` in `pyproject.toml` and `src/first_ade/` introduces `import-linter` as a runtime dependency and requires an ADR under Postulate Π.3.1.

## Decision Drivers

*   **Zero-LLM Determinism**: Enforce `.first-ade/axioms.yaml` and `.first-ade/scope.yaml` via CUE, `import-linter`, `ast-grep`, and git diff guards.
*   **Hexagonal Domain Purity**: Keep `first_ade.domain` and `first_ade.ports` free of `adapters` and `cli` imports.
*   **Clean-Core Licensing**: Only permit permissive OSS dependencies (`import-linter` is BSD).

## Considered Options

*   **Option 1**: Add `src/first_ade/` and `import-linter` to `pyproject.toml` with full `first-ade` CLI and two-sided guardrail tests.
*   **Option 2**: Keep `first-ade` in a separate repository.

## Decision Outcome

Chosen option: "Option 1", enabling immediate self-hosting and dual-surface parity within `First-ADE/first-ade`.

### Positive Consequences

*   `first-ade check` and `first-ade hook` run deterministically in `< 500 ms` locally and in GitHub Actions.
*   Zero copyleft dependencies introduced.

### Negative Consequences

*   `pyproject.toml` adds `import-linter` and `grimp` to runtime dependencies.

## Pros and Cons of the Options

### Option 1: Co-locate `first_ade` in `First-ADE/first-ade`

*   Good, because both `ade-compliance` and `first-ade` share the repository and CI pipelines.
*   Bad, because `first_ade` modules must satisfy existing `ade-compliance` traceability and test-file conventions.

### Option 2: Separate repository

*   Good, because `ade-compliance` rules would not apply.
*   Bad, because it fragments the First-ADE v0.1 MVP codebase.
