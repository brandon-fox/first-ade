"""Pure domain guard evaluators: TamperGuard, ScopeGuard, CouplingGuard."""

from __future__ import annotations

from first_ade.domain.models import (
    AxiomsConfig,
    FileChange,
    Mode,
    ScopeConfig,
    Violation,
)
from first_ade.domain.paths import matches_any_glob, normalize_repo_path


def _all_paths_for_change(change: FileChange) -> list[str]:
    """Return both destination and source (for renames/copies) normalized paths."""
    paths = [normalize_repo_path(change.path)]
    if change.old_path:
        old_norm = normalize_repo_path(change.old_path)
        if old_norm and old_norm not in paths:
            paths.append(old_norm)
    return [p for p in paths if p]


def evaluate_tamper_guard(
    changes: list[FileChange],
    axioms: AxiomsConfig,
    mode: Mode,
) -> list[Violation]:
    """ADE-AX-01: Block agent modifications to constitutional/guardrail files."""
    if mode != Mode.AGENT or not axioms.tamper_guard.enabled:
        return []

    violations: list[Violation] = []
    protected = axioms.tamper_guard.protected_paths
    for change in changes:
        for path in _all_paths_for_change(change):
            if matches_any_glob(path, protected):
                violations.append(
                    Violation(
                        axiom_id=axioms.tamper_guard.id,
                        file=path,
                        line=1,
                        reason=f"Agent mode cannot modify protected guardrail path '{path}'",
                        fix_hint=(
                            "Revert changes to protected constitutional files or "
                            "request human review in --mode human."
                        ),
                    )
                )
    return violations


def evaluate_scope_guard(
    changes: list[FileChange],
    axioms: AxiomsConfig,
    scope: ScopeConfig | None,
) -> tuple[list[Violation], list[str]]:
    """Evaluate per-task scope boundaries or unscoped file-count threshold."""
    if not changes:
        return [], []

    if scope is None:
        unique_files = {normalize_repo_path(c.path) for c in changes if normalize_repo_path(c.path)}
        if len(unique_files) > axioms.unscoped_max_files:
            return [], [
                f"[ADE-SCOPE] Unscoped diff modifies {len(unique_files)} files "
                f"(> {axioms.unscoped_max_files}); consider adding .first-ade/scope.yaml."
            ]
        return [], []

    violations: list[Violation] = []
    for change in changes:
        for path in _all_paths_for_change(change):
            if scope.forbidden_paths and matches_any_glob(path, scope.forbidden_paths):
                violations.append(
                    Violation(
                        axiom_id="ADE-SCOPE",
                        file=path,
                        line=1,
                        reason=f"Path '{path}' is explicitly forbidden by .first-ade/scope.yaml",
                        fix_hint="Revert the forbidden file modification or update scope.yaml with human approval.",
                    )
                )
            elif scope.allowed_paths and not matches_any_glob(path, scope.allowed_paths):
                violations.append(
                    Violation(
                        axiom_id="ADE-SCOPE",
                        file=path,
                        line=1,
                        reason=f"Path '{path}' is outside allowed_paths in .first-ade/scope.yaml",
                        fix_hint="Revert out-of-scope edits or expand allowed_paths in .first-ade/scope.yaml.",
                    )
                )
    return violations, []


def evaluate_coupling_guard(
    changes: list[FileChange],
    axioms: AxiomsConfig,
) -> list[Violation]:
    """ADE-AX-03: Enforce IfThisThenThat paired file edits in the same diff."""
    if not axioms.coupling_guard.enabled or not changes:
        return []

    all_changed: list[str] = []
    for change in changes:
        all_changed.extend(_all_paths_for_change(change))

    violations: list[Violation] = []
    for rule in axioms.coupling_guard.rules:
        triggered_files = [p for p in all_changed if matches_any_glob(p, rule.if_changed)]
        if not triggered_files:
            continue
        has_paired = any(matches_any_glob(p, rule.then_require) for p in all_changed)
        if not has_paired:
            violations.append(
                Violation(
                    axiom_id=axioms.coupling_guard.id,
                    file=triggered_files[0],
                    line=1,
                    reason=(
                        f"Coupling rule '{rule.name}' triggered by '{triggered_files[0]}' "
                        f"without paired change matching {list(rule.then_require)}"
                    ),
                    fix_hint=f"Add or update a paired file matching {list(rule.then_require)} in the same diff.",
                )
            )
    return violations
