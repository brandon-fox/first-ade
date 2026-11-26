"""Unit tests for POSIX path normalization, glob matching, and git adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path

from first_ade.adapters.git_adapter import EMPTY_TREE_HASH, SubprocessGitAdapter, parse_name_status_lines
from first_ade.domain.paths import matches_glob, normalize_repo_path


def test_normalize_repo_path_windows_and_traversal() -> None:
    assert normalize_repo_path(r".\.first-ade\..\.first-ade\axioms.yaml") == ".first-ade/axioms.yaml"
    assert normalize_repo_path("src\\first_ade\\domain\\guards.py") == "src/first_ade/domain/guards.py"
    assert normalize_repo_path("./tests/guardrails/test_neg.py") == "tests/guardrails/test_neg.py"


def test_matches_glob_recursive() -> None:
    assert matches_glob(".first-ade/axioms.yaml", ".first-ade/**")
    assert matches_glob(".first-ade/schemas/axioms.cue", ".first-ade/schemas/**")
    assert matches_glob("tests/guardrails/test_neg.py", "tests/**")
    assert not matches_glob("src/first_ade/cli/main.py", "src/first_ade/domain/**")


def test_parse_name_status_renames() -> None:
    raw = "R100\tsrc/old_name.py\t.first-ade/axioms.yaml\nM\tsrc/first_ade/domain/guards.py\n"
    changes = parse_name_status_lines(raw)
    assert len(changes) == 2
    assert changes[0].status == "R100"
    assert changes[0].old_path == "src/old_name.py"
    assert changes[0].path == ".first-ade/axioms.yaml"
    assert changes[1].status == "M"
    assert changes[1].path == "src/first_ade/domain/guards.py"


def test_git_adapter_missing_origin_main_fallback(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)

    f1 = tmp_path / "README.md"
    f1.write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    adapter = SubprocessGitAdapter()
    changes, notes = adapter.get_changed_files(tmp_path, base_ref="origin/main")
    assert any(EMPTY_TREE_HASH in n for n in notes)
    assert any(c.path == "README.md" for c in changes)
