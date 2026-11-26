"""Unit tests for fail-closed hook stdin JSON handling."""

from __future__ import annotations

import json
from pathlib import Path

from first_ade.cli.hook import process_hook_stdin


def _write_minimal_contract(repo: Path) -> None:
    (repo / ".first-ade").mkdir(parents=True, exist_ok=True)
    (repo / ".first-ade" / "axioms.yaml").write_text(
        """version: "0.1"
project: "test"
unscoped_max_files: 3
tamper_guard:
  id: "ADE-AX-01"
  enabled: true
  protected_paths:
    - ".first-ade/axioms.yaml"
boundary_guard:
  id: "ADE-AX-02"
  enabled: false
  engine: "import-linter"
  config: ".importlinter"
coupling_guard:
  id: "ADE-AX-03"
  enabled: false
  rules: []
ast_guard:
  id: "ADE-AX-04"
  enabled: false
  engine: "ast-grep"
  rules_dir: ".first-ade/rules"
  target_paths: ["src"]
""",
        encoding="utf-8",
    )


def test_hook_empty_stdin_fails_closed() -> None:
    code, msg = process_hook_stdin("", Path("."))
    assert code == 2
    assert "Empty stdin" in msg


def test_hook_malformed_json_fails_closed() -> None:
    code, msg = process_hook_stdin("{bad json", Path("."))
    assert code == 2
    assert "Malformed stdin JSON" in msg


def test_hook_pretooluse_blocks_traversal_to_axioms(tmp_path: Path) -> None:
    _write_minimal_contract(tmp_path)
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_input": {"file_path": "./.first-ade/../.first-ade/axioms.yaml"},
        }
    )
    code, msg = process_hook_stdin(payload, tmp_path)
    assert code == 2
    assert "[ADE-AX-01]" in msg


def test_hook_pretooluse_allows_clean_file(tmp_path: Path) -> None:
    _write_minimal_contract(tmp_path)
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_input": {"file_path": "src/app.py"},
        }
    )
    code, msg = process_hook_stdin(payload, tmp_path)
    assert code == 0
    assert msg == ""
