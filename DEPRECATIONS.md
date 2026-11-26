# Deprecations & Removed Legacy Components

First-ADE v0.1 replaces the legacy `ade-compliance` prototype with a thin, zero-LLM deterministic invariant control plane (`first-ade`).

| Legacy Artifact | Status | Replacement in First-ADE v0.1 |
| :--- | :--- | :--- |
| `src/ade_compliance/` (`ade-compliance` CLI, FastAPI server, SQLAlchemy/Alembic DB, Prometheus metrics, Tree-sitter heuristics) | **Deprecated & Removed** | `src/first_ade/` (`first-ade check` & `first-ade hook`) backed by `cue`, `import-linter`, and `ast-grep` |
| `cli/remediate.py` & `cli/pyproject.toml` | **Deprecated & Removed** | Deterministic `exit 2` stderr diagnostics (`[ADE-AX-XX] file:line — reason — fix hint`) |
| `web-portal/` | **Deprecated & Removed** | GitHub Code Scanning SARIF 2.1.0 + PR Run Receipts |
| `specs/`, `.specify/`, `.kiro/`, `.windsurf/`, `.agent/`, `.gemini/` | **Deprecated & Removed** | Declarative `.first-ade/axioms.yaml`, `.first-ade/scope.yaml`, and closed-world CUE schemas (`.first-ade/schemas/*.cue`) |
| `examples/`, `templates/`, `run-checks.ps1`, `.ade-compliance.yml`, `alembic.ini` | **Deprecated & Removed** | `.lefthook.yml`, `.pre-commit-config.yaml`, and `uv run first-ade check` |
| Legacy `.github/workflows/*` (19 overlapping workflows) | **Deprecated & Removed** | Single `.github/workflows/ci.yml` + `commit-message-linter.yml` |
| 112-line prose `CLAUDE.md` / `GEMINI.md` | **Deprecated & Replaced** | 6-line (`< 500` token) minimal pointer in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` |

See [ADR-0012](docs/decisions/0012-deprecate-legacy-ade-compliance-and-slim-to-v0-1-mvp.md) for the architectural decision record.
