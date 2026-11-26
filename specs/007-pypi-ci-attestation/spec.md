# Feature Specification: PyPI Distribution & Signed CI Attestation Artifacts

**Feature Branch**: `007-pypi-ci-attestation`  
**Created**: 2026-11-24  
**Status**: Draft (Proposed)  
**Input**: Product strategy alignment — publish `ade-compliance` to PyPI (`uvx ade-compliance`) for solo/small teams and emit signed JSON attestation artifacts in CI for PR verification.

## User Scenarios & Testing

### User Story 1 - Zero-Install `uvx` / PyPI Execution (Priority: P1)
As a solo developer or small team, I want to run `uvx ade-compliance check-all src/` without cloning the First ADE repository so I can adopt compliance gates in seconds.

**Why this priority**: Removes the #1 adoption barrier (local source build) for Track 1 CLI/CI users.

**Independent Test**: Build wheel/sdist with `uv build`, install into a clean isolated venv, and verify `ade-compliance --help` and `ade-compliance check-all` execute with zero missing-package or migration-path errors.

**Acceptance Scenarios**:
1. **Given** `ade-compliance` is installed from wheel, **When** `ade-compliance check-all` runs, **Then** bundled Alembic migrations and default templates resolve via package resources (`importlib.resources`).
2. **Given** a GitHub Actions workflow runs `uvx ade-compliance check-all`, **When** checks complete, **Then** exit code reflects compliance status (`0` pass, non-zero fail).

---

### User Story 2 - Signed JSON CI Attestation Artifacts (Priority: P1)
As a team using ephemeral GitHub Actions runners, I want `ade-compliance check-all --attest-out ade-attestation.json` to emit a deterministic, SHA-256 hash-chained (and optionally HMAC/SSH-signed) JSON attestation artifact so PR compliance proof survives ephemeral CI runners without requiring a hosted database.

**Why this priority**: Solves the ephemeral SQLite audit-log gap identified in adverse research.

**Independent Test**: Run `ade-compliance check-all --attest-out out.json` on a sample repo, then run `ade-compliance verify-attestation out.json` and confirm integrity passes (and fails if tampered).

**Acceptance Scenarios**:
1. **Given** a compliance run completes in CI, **When** `--attest-out` is specified, **Then** a schema-versioned JSON artifact is written containing commit SHA, engine results, violation summary, and SHA-256 integrity digest.
2. **Given** an attestation JSON is modified post-run, **When** `verify-attestation` runs, **Then** it exits non-zero and reports a digest mismatch.

---

### Edge Cases
- Wheel packaging must include `alembic.ini` / `migrations/` so `run_migrations()` works outside the source checkout.
- Missing git metadata in detached CI environments: gracefully fall back to `GITHUB_SHA` env var or `"unknown"`.

## Requirements

### Functional Requirements
- **FR-001**: `pyproject.toml` MUST package `ade_compliance` including `migrations/` and default templates as valid wheel package data.
- **FR-002**: CLI MUST support `--attest-out <path>` on `check-all` to emit a deterministic JSON attestation artifact.
- **FR-003**: CLI MUST provide `verify-attestation <path>` to validate the artifact's SHA-256 digest (and optional signature).
- **FR-004**: Repository MUST include a GitHub Actions release workflow publishing tagged releases to PyPI via Trusted Publishing (OIDC).
