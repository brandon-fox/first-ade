# Filter anyio CallSpec2 pytest 10 warning and warn on unsigned PR commits

* Status: accepted
* Deciders: Brandon Fox
* Date: 2026-11-24

Technical Story: PR #181 (`009-ci-pr-signing-and-local-fix`) addresses two friction points: local `pytest` failures caused by `anyio`'s `CallSpec2` `PytestRemovedIn10Warning` under `filterwarnings = ["error"]` in `pyproject.toml`, and GitHub Actions workflow blocks on unsigned intermediate PR commits even though squash/merge commits on `main` are signed.

## Context and Problem Statement

The project enforces `filterwarnings = ["error"]` in `pyproject.toml`, which turns `anyio`'s `PytestRemovedIn10Warning` on `CallSpec2` into a hard local test failure under newer `pytest` releases. Meanwhile, `.github/workflows/main.yml` and `.github/workflows/compliance-and-security.yml` previously exited with status 1 on any unsigned commit during `pull_request` and `merge_group` runs, blocking PR validation before an author or automated squash merge signs the final commit on `main`. How should we restore reliable local test runs and avoid blocking PR checks on intermediate unsigned commits without weakening `main` branch signature enforcement?

## Decision Drivers

*   **Local test reliability**: `pytest` must pass cleanly under `filterwarnings = ["error"]` without masking unrelated warnings.
*   **Main branch integrity**: Direct pushes and merged commits on `main` must still fail CI if unsigned or invalidly signed.
*   **PR workflow ergonomics**: `pull_request` and `merge_group` workflows should surface unsigned commits visibly via GitHub Actions annotations instead of blocking early iteration.

## Considered Options

*   **Option 1**: Filter `ignore:.*CallSpec2.*:pytest.PytestRemovedIn10Warning` in `pyproject.toml`, and emit `::warning::` for unsigned commits on `pull_request` or `merge_group` events while keeping hard failure on `main` pushes in `main.yml` and `compliance-and-security.yml`.
*   **Option 2**: Remove `filterwarnings = ["error"]` globally from `pyproject.toml` and disable commit signature checks on all branches.
*   **Option 3**: Pin `pytest` to an older major version and require every intermediate PR commit to be signed before CI runs.

## Decision Outcome

Chosen option: "Option 1", because it targets only the known upstream `anyio` `CallSpec2` deprecation warning while preserving strict warning-as-error checks, and it warns on unsigned PR/merge_group commits without relaxing mandatory signature verification on `main`.

### Positive Consequences

*   Local and CI `pytest` runs succeed without suppressing unrelated warnings.
*   Unsigned commits in PRs trigger visible `::warning::` annotations in GitHub Actions while `main` retains strict signature enforcement.

### Negative Consequences

*   The `CallSpec2` filter will need to be removed once `anyio` updates its `pytest` plugin for pytest 10 compatibility.
*   PR authors must still ensure the final commit merged into `main` is cryptographically signed.

## Pros and Cons of the Options

### Option 1: Targeted warning filter and PR warning annotation

*   Good, because it preserves `filterwarnings = ["error"]` for project code.
*   Good, because `main` signature enforcement remains strict.
*   Bad, because it adds one temporary filter entry to `pyproject.toml`.

### Option 2: Relax global warning and signature enforcement

*   Good, because it requires no event-specific CI logic.
*   Bad, because it weakens warning hygiene and violates commit signature policy on `main`.

### Option 3: Pin pytest and block all unsigned PR commits

*   Good, because it avoids any warning filter or conditional CI branch.
*   Bad, because it holds back dependency updates and breaks automated or web-authored PR branches prior to signed merge.
