"""import-linter adapter for ADE-AX-02 Hexagonal Domain Purity."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from first_ade.adapters.config_loader import find_binary
from first_ade.domain.models import BoundaryGuardConfig, Violation


class SubprocessImportLinterAdapter:
    """Runs import-linter against .importlinter contracts."""

    def check_boundaries(self, repo_root: Path, config: BoundaryGuardConfig) -> list[Violation]:
        if not config.enabled:
            return []

        config_path = repo_root / config.config
        if not config_path.is_file():
            return [
                Violation(
                    axiom_id=config.id,
                    file=config.config,
                    line=1,
                    reason=f"Missing import-linter config '{config.config}'",
                    fix_hint="Create .importlinter defining hexagonal domain purity contracts.",
                )
            ]

        lint_bin = find_binary(["lint-imports"])
        if lint_bin:
            cmd = [lint_bin, "--config", str(config_path)]
        else:
            # Fallback to current Python environment's importlinter module
            probe = subprocess.run(
                [sys.executable, "-c", "import importlinter"],
                capture_output=True,
                text=True,
            )
            if probe.returncode != 0:
                return [
                    Violation(
                        axiom_id=config.id,
                        file=config.config,
                        line=1,
                        reason="Required 'import-linter' tool not installed in active environment",
                        fix_hint="Install with `uv add import-linter` or `pip install import-linter`.",
                    )
                ]
            cmd = [sys.executable, "-m", "importlinter.cli", "--config", str(config_path)]

        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            output = (proc.stdout + "\n" + proc.stderr).strip()
            summary = next(
                (ln.strip() for ln in output.splitlines() if "BROKEN" in ln or "->" in ln),
                "Hexagonal import boundary violated",
            )
            return [
                Violation(
                    axiom_id=config.id,
                    file=config.config,
                    line=1,
                    reason=summary,
                    fix_hint="Remove imports from adapters/ or cli/ inside domain/ or ports/.",
                )
            ]
        return []
