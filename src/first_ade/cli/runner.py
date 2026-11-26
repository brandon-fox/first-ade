"""Orchestration runner wiring domain guards and infrastructure adapters."""

from __future__ import annotations

import time
from pathlib import Path

from first_ade.adapters.ast_grep_adapter import SubprocessAstGrepAdapter
from first_ade.adapters.config_loader import load_axioms_config, load_scope_config
from first_ade.adapters.cue_adapter import SubprocessCueAdapter
from first_ade.adapters.git_adapter import SubprocessGitAdapter
from first_ade.adapters.import_linter_adapter import SubprocessImportLinterAdapter
from first_ade.domain.guards import (
    evaluate_coupling_guard,
    evaluate_scope_guard,
    evaluate_tamper_guard,
)
from first_ade.domain.models import CheckResult, Mode, Violation


def run_checks(
    repo_root: Path,
    staged: bool = False,
    base_ref: str | None = None,
    mode: Mode = Mode.HUMAN,
) -> CheckResult:
    """Execute all configured First-ADE deterministic guards."""
    t0 = time.perf_counter()
    axioms = load_axioms_config(repo_root)
    scope = load_scope_config(repo_root)

    cue_adapter = SubprocessCueAdapter()
    git_adapter = SubprocessGitAdapter()
    boundary_adapter = SubprocessImportLinterAdapter()
    ast_adapter = SubprocessAstGrepAdapter()

    all_violations: list[Violation] = []
    warnings: list[str] = []

    # 1. CUE Schema validation
    axioms_schema = repo_root / ".first-ade" / "schemas" / "axioms.cue"
    axioms_data = repo_root / ".first-ade" / "axioms.yaml"
    if axioms_schema.is_file():
        all_violations.extend(cue_adapter.validate(repo_root, axioms_schema, axioms_data))

    scope_schema = repo_root / ".first-ade" / "schemas" / "scope.cue"
    scope_data = repo_root / ".first-ade" / "scope.yaml"
    if scope_schema.is_file() and scope_data.is_file():
        all_violations.extend(cue_adapter.validate(repo_root, scope_schema, scope_data))

    # 2. Git diff changes
    changes, notes = git_adapter.get_changed_files(repo_root, staged=staged, base_ref=base_ref)

    # 3. Domain guards
    tamper_v = evaluate_tamper_guard(changes, axioms, mode)
    scope_v, scope_w = evaluate_scope_guard(changes, axioms, scope)
    coupling_v = evaluate_coupling_guard(changes, axioms)
    warnings.extend(scope_w)

    # 4. External static analyzers
    boundary_v = boundary_adapter.check_boundaries(repo_root, axioms.boundary_guard)
    ast_v = ast_adapter.scan(repo_root, axioms.ast_guard)

    raw_violations = all_violations + tamper_v + scope_v + coupling_v + boundary_v + ast_v

    # Apply explicit waivers from scope.yaml (ADE-AX-01 cannot be waived in agent mode)
    waived_ids = {w.axiom_id for w in scope.waivers} if scope else set()
    if mode == Mode.AGENT:
        waived_ids.discard(axioms.tamper_guard.id)

    final_violations: list[Violation] = []
    used_waivers: set[str] = set()
    for v in raw_violations:
        if v.axiom_id in waived_ids:
            used_waivers.add(v.axiom_id)
        else:
            final_violations.append(v)

    tracked_axioms = [
        axioms.tamper_guard.id,
        axioms.boundary_guard.id,
        axioms.coupling_guard.id,
        axioms.ast_guard.id,
    ]
    failed_set = {v.axiom_id for v in final_violations}
    passed = [ax for ax in tracked_axioms if ax not in failed_set and ax not in used_waivers]
    failed = sorted(failed_set)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return CheckResult(
        violations=final_violations,
        warnings=warnings,
        notes=notes,
        passed_axioms=passed,
        failed_axioms=failed,
        waived_axioms=sorted(used_waivers),
        elapsed_ms=elapsed_ms,
    )
