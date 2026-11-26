# implements: FR-001
# traces_to: Π.3.1
"""Fail-closed Claude Code PreToolUse / Stop hook handler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from first_ade.adapters.config_loader import load_axioms_config, load_scope_config
from first_ade.cli.runner import run_checks
from first_ade.domain.guards import evaluate_scope_guard, evaluate_tamper_guard
from first_ade.domain.models import FileChange, Mode
from first_ade.domain.paths import normalize_repo_path

MAX_STDERR_CHARS = 4000


def _extract_target_paths(payload: dict[str, Any], repo_root: Path) -> list[str]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
    raw_paths: list[str] = []
    for key in ("file_path", "path", "target_file", "notebook_path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            raw_paths.append(val)
    paths_val = tool_input.get("paths")
    if isinstance(paths_val, list):
        for item in paths_val:
            if isinstance(item, str) and item.strip():
                raw_paths.append(item)
    return [normalize_repo_path(p, repo_root) for p in raw_paths if normalize_repo_path(p, repo_root)]


def process_hook_stdin(raw_stdin: str, repo_root: Path) -> tuple[int, str]:
    """Process hook stdin JSON and return (exit_code, stderr_message).

    Fails closed (exit 2) on empty, truncated, or malformed JSON.
    """
    if not raw_stdin or not raw_stdin.strip():
        return 2, "[ADE-HOOK] Empty stdin payload; failing closed (exit 2)."

    try:
        payload = json.loads(raw_stdin)
    except json.JSONDecodeError as exc:
        return 2, f"[ADE-HOOK] Malformed stdin JSON ({exc.msg}); failing closed (exit 2)."

    if not isinstance(payload, dict):
        return 2, "[ADE-HOOK] Expected JSON object on stdin; failing closed (exit 2)."

    event = str(payload.get("hook_event_name", "")).strip()
    if event == "PreToolUse" or (not event and isinstance(payload.get("tool_input"), dict)):
        target_paths = _extract_target_paths(payload, repo_root)
        if not target_paths:
            return 0, ""
        axioms = load_axioms_config(repo_root)
        scope = load_scope_config(repo_root)
        changes = [FileChange(status="M", path=p) for p in target_paths]
        violations = evaluate_tamper_guard(changes, axioms, Mode.AGENT)
        scope_v, _ = evaluate_scope_guard(changes, axioms, scope)
        violations.extend(scope_v)
        if violations:
            msg = "\n".join(v.format_terminal() for v in violations)
            return 2, msg[:MAX_STDERR_CHARS]
        return 0, ""

    # Default / Stop event: run full agent check
    result = run_checks(repo_root=repo_root, mode=Mode.AGENT)
    if not result.ok:
        msg = "\n".join(v.format_terminal() for v in result.violations)
        if len(msg) > MAX_STDERR_CHARS:
            msg = msg[: MAX_STDERR_CHARS - 20] + "\n... (truncated)"
        return 2, msg
    return 0, ""
