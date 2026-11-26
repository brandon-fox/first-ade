"""Positive guardrail acceptance tests: clean diffs MUST exit 0 with 0 warnings."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from click.testing import CliRunner

from first_ade.cli.main import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _init_clean_repo(tmp_path: Path, with_scope: bool = True) -> Path:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@first-ade.dev"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CI"], cwd=tmp_path, check=True, capture_output=True)

    shutil.copytree(REPO_ROOT / ".first-ade", tmp_path / ".first-ade")
    shutil.copy2(REPO_ROOT / ".importlinter", tmp_path / ".importlinter")
    if not with_scope and (tmp_path / ".first-ade" / "scope.yaml").exists():
        (tmp_path / ".first-ade" / "scope.yaml").unlink()
    elif with_scope:
        (tmp_path / ".first-ade" / "scope.yaml").write_text(
            'version: "0.1"\ntask: "clean-feature"\nallowed_paths:\n  - "src/**"\n  - "tests/**"\n',
            encoding="utf-8",
        )

    (tmp_path / "src" / "first_ade" / "domain").mkdir(parents=True)
    (tmp_path / "src" / "first_ade" / "ports").mkdir(parents=True)
    (tmp_path / "src" / "first_ade" / "adapters").mkdir(parents=True)
    (tmp_path / "src" / "first_ade" / "cli").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True)

    for pkg in (
        "src/first_ade/__init__.py",
        "src/first_ade/domain/__init__.py",
        "src/first_ade/ports/__init__.py",
        "src/first_ade/adapters/__init__.py",
        "src/first_ade/cli/__init__.py",
    ):
        (tmp_path / pkg).write_text('"""pkg"""\n', encoding="utf-8")

    (tmp_path / "src" / "first_ade" / "domain" / "guards.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok(): assert True\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_positive_clean_feature_with_paired_test(tmp_path: Path) -> None:
    repo = _init_clean_repo(tmp_path, with_scope=True)
    (repo / "src" / "first_ade" / "domain" / "guards.py").write_text("VALUE = 42\n", encoding="utf-8")
    (repo / "tests" / "test_ok.py").write_text("def test_ok(): assert 42 == 42\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 0, res.output
    assert "warning:" not in res.output


def test_positive_small_unscoped_bugfix(tmp_path: Path) -> None:
    repo = _init_clean_repo(tmp_path, with_scope=False)
    (repo / "src" / "first_ade" / "adapters" / "fix.py").write_text("FIXED = True\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 0, res.output
    assert "warning:" not in res.output


def test_positive_human_mode_axioms_update_with_test(tmp_path: Path) -> None:
    repo = _init_clean_repo(tmp_path, with_scope=False)
    axioms_file = repo / ".first-ade" / "axioms.yaml"
    updated = axioms_file.read_text(encoding="utf-8").replace(
        "unscoped_max_files: 3", "unscoped_max_files: 4"
    )
    axioms_file.write_text(updated, encoding="utf-8")
    (repo / "tests" / "test_ok.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 0, res.output
    assert "warning:" not in res.output


def test_positive_unscoped_over_3_files_emits_warning_not_block(tmp_path: Path) -> None:
    repo = _init_clean_repo(tmp_path, with_scope=False)
    for idx in range(4):
        (repo / "src" / "first_ade" / "adapters" / f"f{idx}.py").write_text(f"X = {idx}\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 0, res.output
    assert "warning:" in res.output
    assert "[ADE-SCOPE]" in res.output


def test_positive_stop_hook_clean_repo(tmp_path: Path) -> None:
    repo = _init_clean_repo(tmp_path, with_scope=False)
    runner = CliRunner()
    res = runner.invoke(main, ["hook", "--repo-root", str(repo)], input='{"hook_event_name": "Stop"}')
    assert res.exit_code == 0, res.output
