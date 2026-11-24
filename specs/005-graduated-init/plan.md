# Implementation Plan: Graduated `ade-compliance init` Wizard

**Branch**: `005-graduated-init` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

## Summary
Add an `init` subcommand to `src/ade_compliance/cli.py` backed by a lightweight `InitService` that inspects repository state (greenfield vs. brownfield, existing SDD directories, git hooks) and generates `.ade-compliance.yml` with graduated strictness defaults.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: `click`, `pyyaml`, `pydantic`  
**Storage**: Filesystem (`.ade-compliance.yml`, `.git/hooks/pre-commit`)  
**Testing**: `pytest` (isolated `tmp_path` fixtures, no external network calls)  
**Performance Goals**: `<200ms` execution time

## Constitution Check
- **Spec Governance (II)**: This `spec.md` + `plan.md` precede implementation.
- **Deterministic Verification (III)**: All filesystem and git-detection logic tested in `tmp_path` unit tests before implementation.
- **Traceable Rationale (IV)**: Aligns with [ADR-0003](../../docs/decisions/0003-harden-default-quality-gate-strictness-to-enforce.md) by keeping `enforce` as the greenfield default while offering `warn` for brownfield onboarding.

## Project Structure
```text
src/ade_compliance/
├── cli.py                # Add `init` Click command
└── services/
    └── init_service.py   # Repo inspection & config/hook scaffolding (inherits BaseService)

tests/unit/
└── test_init_service.py  # Greenfield, brownfield, --force, and hook tests
```
