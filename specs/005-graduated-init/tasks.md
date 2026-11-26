# Tasks: Graduated `ade-compliance init` Wizard

**Input**: Design documents from `/specs/005-graduated-init/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required)

## Phase 1: Tests First (TDD)
- [ ] T001 [US1] [FR-002] Write unit tests for greenfield vs. brownfield repository detection in `tests/unit/test_init_service.py`
- [ ] T002 [US1] [FR-003] Write unit tests for SDD layout auto-detection (`.specify/`, `openspec/`, `docs/stories/`, `.gemini/`) in `tests/unit/test_init_service.py`
- [ ] T003 [US2] [FR-001] Write CLI tests for `ade-compliance init` flags (`--yes`, `--strictness`, `--install-hooks`, `--force`) in `tests/unit/test_init_cli.py`

## Phase 2: Implementation
- [ ] T004 [US1] [FR-004] Implement `InitService` inheriting `BaseService` with `enforce` (greenfield) and `warn` (brownfield) defaults in `src/ade_compliance/services/init_service.py`
- [ ] T005 [US2] [FR-001] Wire `init` subcommand and hook installation into `src/ade_compliance/cli.py`
