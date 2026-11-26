# Tasks: Pluggable SDD Providers & DDD `DomainBoundaryEngine`

**Input**: Design documents from `/specs/006-sdd-ddd-adapters/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required)

## Phase 1: Tests First (TDD)
- [ ] T001 [US1] [FR-001] Write unit tests for `engines.spec.providers` config parsing and invalid provider `ConfigError` in `tests/unit/test_spec_providers.py`
- [ ] T002 [US1] [FR-002] Write unit tests for `SpecEngine` glob resolution across `speckit`, `openspec`, `bmad`, and `conductor` in `tests/unit/test_spec_providers.py`
- [ ] T003 [US2] [FR-003] Write unit tests for `DomainBoundaryEngine` config and `forbid_imports` violation reporting in `tests/unit/test_domain_boundary_engine.py`

## Phase 2: Implementation
- [ ] T004 [US1] [FR-001] [FR-002] Extend `Config` and `SpecEngine` with `PROVIDER_GLOBS` registry in `src/ade_compliance/config.py` and `src/ade_compliance/engines/spec_engine.py`
- [ ] T005 [US2] [FR-003] [FR-004] Implement AST/tree-sitter `DomainBoundaryEngine` inheriting `BaseEngine` in `src/ade_compliance/engines/domain_boundary_engine.py`
