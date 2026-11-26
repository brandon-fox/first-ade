# Deprecate Legacy ADE Compliance and Slim to v0.1 MVP

* Status: accepted
* Deciders: Brandon Fox
* Date: 2026-11-25

Technical Story: Remove the superseded `ade-compliance` server/DB prototype, legacy workflows, and multi-file prose spec templates so `First-ADE/first-ade` ships cleanly as the First-ADE v0.1 deterministic control plane.

## Context and Problem Statement

The repository carried the legacy `ade-compliance` FastAPI/SQLAlchemy/Alembic/Tree-sitter prototype alongside 19 overlapping GitHub Actions workflows, `web-portal/`, `cli/remediate.py`, and multi-file prose `specs/`/`.specify/` templates. Those artifacts added 12 unnecessary runtime dependencies, bloated agent context files, and conflicted with First-ADE v0.1 CI.

## Decision Outcome

Deprecate and remove all legacy `ade-compliance` code, tests, workflows, and multi-file prose spec templates, reducing runtime dependencies to `click`, `pyyaml`, and `import-linter`, and documenting all replacements in `DEPRECATIONS.md`.
