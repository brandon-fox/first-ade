# Implementation Plan: PyPI Distribution & Signed CI Attestation Artifacts

**Branch**: `007-pypi-ci-attestation` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

## Summary
Configure `hatchling` package data in `pyproject.toml` for clean wheel/PyPI distribution (`uvx ade-compliance`), add `--attest-out` / `verify-attestation` commands in `cli.py` backed by an `AttestationArtifactService`, and add a `.github/workflows/release-pypi.yml` workflow.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: `hatchling`, `pydantic`, `cryptography`, `hashlib`  
**Storage**: Ephemeral JSON artifact (`ade-attestation.json`) + existing SQLite audit log  
**Testing**: `pytest` (wheel smoke test + digest tamper verification)

## Constitution Check
- **Deterministic Verification (III)**: Canonical JSON serialization (`sort_keys=True`) ensures reproducible SHA-256 digests.
- **Traceable Rationale (IV)**: Preserves tamper-proof audit guarantees in stateless CI environments.

## Project Structure
```text
pyproject.toml                                # Package data for migrations & templates
.github/workflows/release-pypi.yml            # OIDC PyPI publish on tag
src/ade_compliance/
├── cli.py                                    # --attest-out & verify-attestation
└── services/attestation_artifact_service.py  # Canonical digest & verification

tests/unit/
└── test_attestation_artifact.py
```
