# Feature Specification: Pluggable SDD Providers & DDD `DomainBoundaryEngine`

**Feature Branch**: `006-sdd-ddd-adapters`  
**Created**: 2026-11-24  
**Status**: Draft (Proposed)  
**Input**: Product strategy alignment — support pluggable SDD spec providers (`speckit`, `openspec`, `bmad`, `conductor`) and add a fast-heuristic `DomainBoundaryEngine` to enforce DDD bounded-context import rules.

## User Scenarios & Testing

### User Story 1 - Pluggable SDD Spec Discovery (Priority: P1)
As a developer using OpenSpec, BMAD, or Gemini Conductor, I want `SpecEngine` to recognize my tool's specification layout via `.ade-compliance.yml` so I can use First ADE without migrating my spec directory structure.

**Why this priority**: Unlocks immediate adoption across existing SDD ecosystems without workflow lock-in.

**Independent Test**: Configure `spec_providers: [openspec]` in `.ade-compliance.yml` inside a repo with `openspec/specs/auth/spec.md` and verify `ade-compliance check-spec` passes.

**Acceptance Scenarios**:
1. **Given** `spec_providers` includes `openspec`, **When** `SpecEngine.check()` runs, **Then** it discovers `openspec/specs/**/*.md` and `openspec/changes/**/proposal.md`.
2. **Given** `spec_providers` includes `bmad` or `conductor`, **When** `SpecEngine.check()` runs, **Then** it discovers their respective spec/story artifacts (`docs/stories/**/*.md`, `conductor/**/*.md`).
3. **Given** no `spec_providers` is configured, **When** `SpecEngine.check()` runs, **Then** it defaults to `speckit` (`specs/**/*.md`, `spec.md`).

---

### User Story 2 - DDD Bounded Context Import Enforcement (Priority: P1)
As an architect practicing Domain-Driven Design, I want `DomainBoundaryEngine` to block forbidden cross-context imports (e.g., `billing/domain` importing `auth/infrastructure`) in under 500ms so architectural boundaries stay intact under AI-assisted coding.

**Why this priority**: Enforces `Σ.4` (Emergent Complexity) and Constitution Principle V (one-way dependencies) with fast AST heuristics.

**Independent Test**: Add a `domain_boundaries` rule in `.ade-compliance.yml`, introduce a forbidden cross-context import in a test Python file, and verify `DomainBoundaryEngine` emits a violation citing `Σ.4`.

**Acceptance Scenarios**:
1. **Given** a bounded context rule `forbid_imports` in `.ade-compliance.yml`, **When** a Python/TS file imports a forbidden module, **Then** `DomainBoundaryEngine` flags a violation with file, line, and target module.
2. **Given** imports respect declared layer/context boundaries, **When** `DomainBoundaryEngine.check()` runs, **Then** zero violations are returned.

---

### Edge Cases
- Unknown `spec_providers` entry: fail fast at config parse time with a clear `ConfigError`.
- Relative vs. absolute imports in Python/TS: normalize module paths before evaluating `domain_boundaries` rules.

## Requirements

### Functional Requirements
- **FR-001**: `Config` MUST support `engines.spec.providers` (list of `speckit | openspec | bmad | conductor`, default `["speckit"]`).
- **FR-002**: `SpecEngine` MUST resolve glob patterns per configured provider in `<100ms`.
- **FR-003**: System MUST provide `DomainBoundaryEngine` inheriting from `BaseEngine`, configurable via `engines.domain_boundary` and `domain_boundaries` rules in `.ade-compliance.yml`.
- **FR-004**: `DomainBoundaryEngine` MUST use fast AST/tree-sitter import extraction (`<500ms` total) without executing project code.
