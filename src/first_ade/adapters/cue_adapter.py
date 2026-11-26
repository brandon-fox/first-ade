"""CUE schema validation adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path

from first_ade.adapters.config_loader import find_binary
from first_ade.domain.models import Violation
from first_ade.domain.paths import normalize_repo_path


class SubprocessCueAdapter:
    """Validates YAML files against closed-world CUE schemas."""

    def validate(self, repo_root: Path, schema_path: Path, data_path: Path) -> list[Violation]:
        if not data_path.is_file():
            return []
        rel_data = normalize_repo_path(str(data_path.relative_to(repo_root)))
        cue_bin = find_binary(["cue"])
        if not cue_bin:
            return [
                Violation(
                    axiom_id="ADE-CUE",
                    file=rel_data,
                    line=1,
                    reason="Required 'cue' binary not found on PATH",
                    fix_hint="Install CUE (e.g., `winget install CueLang.Cue` or `brew install cuelang/tap/cue`).",
                )
            ]

        proc = subprocess.run(
            [cue_bin, "vet", "-c", str(schema_path), str(data_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            raw_err = (proc.stderr or proc.stdout).strip()
            err_msg = raw_err.splitlines()[0] if raw_err else "CUE validation failed"
            rel_schema = normalize_repo_path(str(schema_path.relative_to(repo_root)))
            return [
                Violation(
                    axiom_id="ADE-CUE",
                    file=rel_data,
                    line=1,
                    reason=f"Schema validation failed: {err_msg}",
                    fix_hint=f"Fix {rel_data} to conform to {rel_schema}.",
                )
            ]
        return []
