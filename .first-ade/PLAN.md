# First-ADE v0.1 Running MVP — Architectural Plan

## 1. Discovered Organization & Workspace State

Inspected `https://github.com/First-ADE` (`gh repo list First-ADE`):
- `First-ADE/first-ade` (Public, MIT, `main` default, active worktree `first_ade_v01_mvp`): Contains existing `ade-compliance` Python package (`src/ade_compliance/`), `pyproject.toml`, `.pre-commit-config.yaml`, `CLAUDE.md`, `GEMINI.md`, and `.github/workflows/`.
- `First-ADE/.github` (Public, `main` default, active worktree `first_ade_v01_mvp`): Org-wide reusable workflows (`ade-verify.yml`, `verify.yml`, `main-guardian.yml`).
- `First-ADE/Constitution-MCP` (Private) & `First-ADE/first-ade-obsidian-vault` (Private): Out of v0.1 MVP scope.

## 2. Resolved Environment Assumptions (`foxgaming`, Windows 11)

- **Python / Package Manager**: Python 3.13/3.14 via `uv 0.9.28`. `pyproject.toml` will register `first-ade = "first_ade.cli.main:main"` alongside `ade-compliance` and add `import-linter` (BSD) as a runtime dependency.
- **External Analyzers**:
  - `cue` `v0.17.1` installed via `winget` (`CueLang.Cue`).
  - `ast-grep` `v0.51.3` installed via `winget` (`ast-grep.ast-grep`, exposes `sg` on Windows; `first-ade` probes `["ast-grep", "sg"]`).
  - `lefthook` `v2.2.3` installed via `winget` (`evilmartians.lefthook`).
  - Missing active binary at runtime **fails closed (`exit 2`)** with explicit install hint.
- **Path & Diff Normalization**: All file paths, globs, and `git diff --name-status -M` outputs are normalized to POSIX `/` in pure Python (`PurePosixPath` / `os.path.normpath` + `..` collapse) — zero shell `sed`/`grep`/`awk`.
- **Base Ref Fallback**: If `origin/main` is absent (shallow/single-commit repo), `first-ade` falls back to `HEAD~1`, then Git empty tree `4b825dc642cb6eb9a060e54bf8d69288fbee4904`.

## 3. Target File Tree

### `First-ADE/first-ade` (`first_ade_v01_mvp` branch)
```text
.first-ade/
  PLAN.md
  axioms.yaml                  # Self-hosting v0.1 constitution (ADE-AX-01..04)
  scope.yaml                   # Active task scope for v0.1 MVP build
  schemas/
    axioms.cue                 # Closed-world CUE schema for axioms.yaml
    scope.cue                  # Closed-world CUE schema for scope.yaml
  rules/
    execution_safety.yml       # ast-grep rules banning shell=True, eval(, exec(
AGENTS.md                      # <= 12-line minimal agent pointer (< 500 tokens)
CLAUDE.md                      # Minimal pointer synced with AGENTS.md
.importlinter                  # Hexagonal architecture contract (ADE-AX-02)
.lefthook.yml                  # Local pre-commit hook running first-ade check --staged
.pre-commit-config.yaml        # Updated with local first-ade hook
.coderabbit.yaml               # Advisory-only AI review & slop filter
sonar-project.properties       # SonarQube Cloud OSS config
.github/
  ISSUE_TEMPLATE/
    constitutional-amendment.yml
  workflows/
    ci.yml                     # first-ade SARIF upload + pytest + license check + CodeQL
src/first_ade/
  __init__.py
  domain/                      # Pure models, invariants, SARIF normalizer (0 adapter/cli imports)
    __init__.py
    models.py
    paths.py
    guards.py
    sarif.py
    receipt.py
  ports/                       # Protocol interfaces for git & external analyzers
    __init__.py
    git_port.py
    analyzer_port.py
  adapters/                    # Subprocess adapters (git, cue, import-linter, ast-grep)
    __init__.py
    git_adapter.py
    cue_adapter.py
    import_linter_adapter.py
    ast_grep_adapter.py
  cli/                         # Click CLI (`check`, `hook`) + stdin-JSON fail-closed handler
    __init__.py
    main.py
    hook.py
tests/
  unit/first_ade/
    test_paths_and_git.py
    test_sarif_and_receipt.py
    test_hook_unit.py
  guardrails/
    test_negative_guardrails.py
    test_positive_guardrails.py
```

### `First-ADE/.github` (`first_ade_v01_mvp` branch)
- `.github/workflows/first-ade-check.yml`: Reusable workflow calling `first-ade check --base origin/main --format sarif`.

## 4. Explicit v0.1 Deferrals

No custom ADE-SL/Tree-sitter parsers, Lean 4, Z3, Pact V4, gRPC sidecars, self-hosted SonarQube/Forgejo, gVisor, or multi-file prose spec templates.
