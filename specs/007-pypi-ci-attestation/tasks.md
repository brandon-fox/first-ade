# Tasks: PyPI Distribution & Signed CI Attestation Artifacts

**Input**: Design documents from `/specs/007-pypi-ci-attestation/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required)

## Phase 1: Tests First (TDD)
- [ ] T001 [US1] [FR-001] Add wheel build and `importlib.resources` migration resolution smoke test in `tests/unit/test_packaging.py`
- [ ] T002 [US2] [FR-002] [FR-003] Write unit tests for canonical JSON attestation export and SHA-256 tamper verification in `tests/unit/test_attestation_artifact.py`

## Phase 2: Implementation
- [ ] T003 [US1] [FR-001] Configure `hatchling` package data for `migrations/` and templates in `pyproject.toml`
- [ ] T004 [US2] [FR-002] [FR-003] Implement `AttestationArtifactService` and `--attest-out` / `verify-attestation` CLI commands in `src/ade_compliance/services/attestation_artifact_service.py` and `src/ade_compliance/cli.py`
- [ ] T005 [US1] [FR-004] Add OIDC PyPI release workflow in `.github/workflows/release-pypi.yml`
