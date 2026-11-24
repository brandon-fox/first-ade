# Implementation Plan: Pluggable SDD Providers & DDD `DomainBoundaryEngine`

**Branch**: `006-sdd-ddd-adapters` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

## Summary
Extend `Config` and `SpecEngine` with a `PROVIDER_GLOBS` registry for Spec-Kit, OpenSpec, BMAD, and Conductor, and implement `DomainBoundaryEngine` using Python `ast` (and `tree-sitter` for JS/TS) to validate bounded-context and layered dependency rules.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: `pydantic`, `ast` (stdlib), `tree-sitter`  
**Storage**: N/A (stateless config + AST scan)  
**Testing**: `pytest` unit tests per provider and boundary rule  
**Performance Goals**: `<500ms` across typical staged changesets

## Constitution Check
- **Architectural Constraints (V)**: `DomainBoundaryEngine` inherits `BaseEngine` and has a single reason to change (import-graph boundary verification).
- **Deterministic Verification (III)**: Pure AST/filesystem checks with zero network or LLM calls.

## Project Structure
```text
src/ade_compliance/
├── config.py                          # Add `providers` & `DomainBoundaryRule` models
└── engines/
    ├── spec_engine.py                 # Provider-aware spec glob resolution
    └── domain_boundary_engine.py      # New BaseEngine subclass for DDD boundaries

tests/unit/
├── test_spec_providers.py
└── test_domain_boundary_engine.py
```
