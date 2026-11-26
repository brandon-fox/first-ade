# implements: FR-001
# traces_to: Π.3.1
"""Binary lookup helper and YAML config loader."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import yaml

from first_ade.domain.models import (
    AstGuardConfig,
    AxiomsConfig,
    BoundaryGuardConfig,
    CouplingGuardConfig,
    CouplingRule,
    ScopeConfig,
    TamperGuardConfig,
    Waiver,
)


def find_binary(candidates: list[str]) -> str | None:
    """Locate an executable on PATH or Windows WinGet directories."""
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found

    if os.name == "nt":
        winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet"
        winget_links = winget_root / "Links"
        if winget_links.is_dir():
            for name in candidates:
                exe = winget_links / f"{name}.exe"
                if exe.is_file():
                    return str(exe)
        winget_pkgs = winget_root / "Packages"
        if winget_pkgs.is_dir():
            for name in candidates:
                for exe in winget_pkgs.glob(f"*/{name}.exe"):
                    if exe.is_file():
                        return str(exe)
    return None


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_axioms_config(repo_root: Path) -> AxiomsConfig:
    """Load .first-ade/axioms.yaml into domain models."""
    axioms_path = repo_root / ".first-ade" / "axioms.yaml"
    if not axioms_path.is_file():
        raise FileNotFoundError(f"Missing required axioms contract: {axioms_path}")
    raw = _load_yaml_dict(axioms_path)

    tg = raw.get("tamper_guard", {})
    bg = raw.get("boundary_guard", {})
    cg = raw.get("coupling_guard", {})
    ag = raw.get("ast_guard", {})

    rules = tuple(
        CouplingRule(
            name=str(r["name"]),
            if_changed=tuple(str(p) for p in r.get("if_changed", [])),
            then_require=tuple(str(p) for p in r.get("then_require", [])),
        )
        for r in cg.get("rules", [])
    )

    return AxiomsConfig(
        version=str(raw.get("version", "0.1")),
        project=str(raw.get("project", repo_root.name)),
        unscoped_max_files=int(raw.get("unscoped_max_files", 3)),
        tamper_guard=TamperGuardConfig(
            id=str(tg.get("id", "ADE-AX-01")),
            enabled=bool(tg.get("enabled", True)),
            protected_paths=tuple(str(p) for p in tg.get("protected_paths", [])),
        ),
        boundary_guard=BoundaryGuardConfig(
            id=str(bg.get("id", "ADE-AX-02")),
            enabled=bool(bg.get("enabled", True)),
            engine=str(bg.get("engine", "import-linter")),
            config=str(bg.get("config", ".importlinter")),
        ),
        coupling_guard=CouplingGuardConfig(
            id=str(cg.get("id", "ADE-AX-03")),
            enabled=bool(cg.get("enabled", True)),
            rules=rules,
        ),
        ast_guard=AstGuardConfig(
            id=str(ag.get("id", "ADE-AX-04")),
            enabled=bool(ag.get("enabled", True)),
            engine=str(ag.get("engine", "ast-grep")),
            rules_dir=str(ag.get("rules_dir", ".first-ade/rules")),
            target_paths=tuple(str(p) for p in ag.get("target_paths", ["src/first_ade"])),
        ),
    )


def load_scope_config(repo_root: Path) -> ScopeConfig | None:
    """Load .first-ade/scope.yaml if present, else return None."""
    scope_path = repo_root / ".first-ade" / "scope.yaml"
    if not scope_path.is_file():
        return None
    raw = _load_yaml_dict(scope_path)
    waivers = tuple(
        Waiver(
            axiom_id=str(w["axiom_id"]),
            reason=str(w["reason"]),
            approved_by=str(w["approved_by"]),
        )
        for w in raw.get("waivers", [])
    )
    return ScopeConfig(
        version=str(raw.get("version", "0.1")),
        task=str(raw.get("task", "unnamed")),
        allowed_paths=tuple(str(p) for p in raw.get("allowed_paths", [])),
        forbidden_paths=tuple(str(p) for p in raw.get("forbidden_paths", [])),
        waivers=waivers,
    )
