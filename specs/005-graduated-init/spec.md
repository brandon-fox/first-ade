# Feature Specification: Graduated `ade-compliance init` Wizard

**Feature Branch**: `005-graduated-init`  
**Created**: 2026-11-24  
**Status**: Draft (Proposed)  
**Input**: Product strategy alignment — preserve `enforce` as the greenfield default (per ADR-0003) while providing a zero-friction `ade-compliance init` wizard that detects brownfield repositories and initializes them in `warn`/`audit` mode.

## User Scenarios & Testing

### User Story 1 - Brownfield Repository Auto-Detection (Priority: P1)
As a developer adopting First ADE on an existing repository, I want `ade-compliance init` to detect my existing codebase and initialize `.ade-compliance.yml` in `warn` or `audit` mode so that my commits are not blocked on day one.

**Why this priority**: Prevents immediate pre-commit fatigue and `--no-verify` bypasses on existing projects.

**Independent Test**: Run `ade-compliance init` in a temporary directory containing existing `src/` files without `specs/` and verify `.ade-compliance.yml` is generated with `strictness: warn` (or `audit`).

**Acceptance Scenarios**:
1. **Given** a repository with existing source files and no `.ade-compliance.yml`, **When** `ade-compliance init` runs, **Then** it detects brownfield status and writes `.ade-compliance.yml` with `global.strictness: warn`.
2. **Given** an empty/greenfield repository, **When** `ade-compliance init` runs, **Then** it preserves `global.strictness: enforce` per ADR-0003.

---

### User Story 2 - Interactive & Non-Interactive Hook Setup (Priority: P2)
As a solo builder or CI maintainer, I want `ade-compliance init --yes` to scaffold `.ade-compliance.yml` and optionally install the git pre-commit hook non-interactively so I can onboard in under 30 seconds.

**Independent Test**: Run `ade-compliance init --yes --install-hooks` and verify `.ade-compliance.yml` and `.git/hooks/pre-commit` exist and are executable.

**Acceptance Scenarios**:
1. **Given** `--yes` is passed, **When** `ade-compliance init` runs, **Then** it skips interactive prompts and applies detected defaults.
2. **Given** `.ade-compliance.yml` already exists, **When** `ade-compliance init` runs without `--force`, **Then** it exits safely without overwriting user configuration.

---

### Edge Cases
- Running outside a git repository: warn the user and skip git hook installation while still generating `.ade-compliance.yml`.
- Existing `.pre-commit-config.yaml`: append or print the `ade-compliance` hook snippet rather than clobbering existing hooks.

## Requirements

### Functional Requirements
- **FR-001**: CLI MUST expose `ade-compliance init` with `--yes`, `--strictness`, `--install-hooks`, and `--force` options.
- **FR-002**: System MUST detect brownfield vs. greenfield repositories by inspecting existing tracked/source files.
- **FR-003**: System MUST detect present SDD layouts (`.specify/`, `openspec/`, `docs/stories/`, `.gemini/`) and pre-populate `spec_providers` when available.
- **FR-004**: Greenfield initialization MUST default to `strictness: enforce` (ADR-0003); brownfield initialization MUST default to `strictness: warn`.
