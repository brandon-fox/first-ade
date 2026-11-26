"""ast-grep adapter for ADE-AX-04 Execution Safety Hygiene."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from first_ade.adapters.config_loader import find_binary
from first_ade.domain.models import AstGuardConfig, Violation
from first_ade.domain.paths import normalize_repo_path


class SubprocessAstGrepAdapter:
    """Runs ast-grep (or sg) with YAML rules and normalizes findings."""

    def scan(self, repo_root: Path, config: AstGuardConfig) -> list[Violation]:
        if not config.enabled:
            return []

        sg_bin = find_binary(["ast-grep", "sg"])
        if not sg_bin:
            return [
                Violation(
                    axiom_id=config.id,
                    file=config.rules_dir,
                    line=1,
                    reason="Required 'ast-grep' (sg) binary not found on PATH",
                    fix_hint=(
                        "Install ast-grep (e.g., `winget install ast-grep.ast-grep` "
                        "or `pip install ast-grep-cli`)."
                    ),
                )
            ]

        rules_dir = repo_root / config.rules_dir
        if not rules_dir.is_dir():
            return []

        rule_files = sorted(rules_dir.glob("*.yml")) + sorted(rules_dir.glob("*.yaml"))
        targets = [str(repo_root / t) for t in config.target_paths if (repo_root / t).exists()]
        if not targets or not rule_files:
            return []

        violations: list[Violation] = []
        for rule_file in rule_files:
            proc = subprocess.run(
                [sg_bin, "scan", "--rule", str(rule_file), "--json=compact", *targets],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            stdout = proc.stdout.strip()
            if not stdout:
                continue
            try:
                matches = json.loads(stdout)
            except json.JSONDecodeError:
                continue
            if not isinstance(matches, list):
                continue
            for m in matches:
                if not isinstance(m, dict):
                    continue
                raw_file = str(m.get("file", "unknown"))
                norm_file = normalize_repo_path(raw_file, repo_root)
                start_line = 1
                rng = m.get("range", {})
                if isinstance(rng, dict):
                    start = rng.get("start", {})
                    if isinstance(start, dict) and isinstance(start.get("line"), int):
                        start_line = start["line"] + 1
                msg = str(m.get("message") or f"AST rule '{m.get('ruleId', 'unknown')}' matched")
                violations.append(
                    Violation(
                        axiom_id=config.id,
                        file=norm_file,
                        line=start_line,
                        reason=msg,
                        fix_hint="Replace unsafe dynamic/shell pattern with safe explicit API.",
                    )
                )
        return violations
