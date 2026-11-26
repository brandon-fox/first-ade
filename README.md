# First-ADE v0.1

A thin, zero-LLM deterministic invariant control plane (`first-ade`) that binds declarative YAML/CUE repository invariants (`.first-ade/axioms.yaml`) and per-task boundaries (`.first-ade/scope.yaml`) to proven static/diff engines (`cue`, `import-linter`, `ast-grep`, `pytest`) across local agent hooks and GitHub Actions.

## Quickstart

```powershell
uv sync --extra dev
uv run first-ade check --base origin/main
```

### CLI Commands

- `first-ade check [--staged | --base <ref>] [--mode human|agent] [--format terminal|json|sarif] [--output <path>] [--receipt <path>]`
  - Exit `0`: all invariants passed
  - Exit `2`: invariant violation or missing active analyzer binary (fail-closed)
  - Exit `1`: internal configuration error
- `first-ade hook`: Claude Code `PreToolUse` / `Stop` stdin-JSON hook (fail-closed `exit 2` on invalid JSON or violation)

## Self-Hosting Axioms (`.first-ade/axioms.yaml`)

| Axiom | Guard | Enforcement |
| :--- | :--- | :--- |
| **ADE-AX-01** | Tamper Sovereignty | Blocks agent-mode edits/renames touching `.first-ade/axioms.yaml`, `.first-ade/schemas/**`, `.github/workflows/**`, `.lefthook.yml`, `.pre-commit-config.yaml`, `tests/guardrails/**` |
| **ADE-AX-02** | Hexagonal Domain Purity | Enforces via `import-linter` that `first_ade.domain` and `first_ade.ports` have zero imports from `first_ade.adapters` or `first_ade.cli` |
| **ADE-AX-03** | Paired Test Coupling | Requires edits to `src/first_ade/domain/**`, `src/first_ade/guards/**`, or `.first-ade/schemas/**` to include a paired edit under `tests/**` |
| **ADE-AX-04** | Execution Safety Hygiene | Enforces via `ast-grep` zero `shell=True`, `eval(`, or `exec(` in `src/first_ade/**` |
