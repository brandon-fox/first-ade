"""Negative guardrail acceptance tests: all violations MUST exit 2 with [ADE-AX-XX]."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from first_ade.cli.main import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _init_fixture_repo(tmp_path: Path, with_scope: bool = True) -> Path:
    """Create an isolated git repository with First-ADE v0.1 self-hosting contract."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@first-ade.dev"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CI"], cwd=tmp_path, check=True, capture_output=True)

    shutil.copytree(REPO_ROOT / ".first-ade", tmp_path / ".first-ade")
    shutil.copy2(REPO_ROOT / ".importlinter", tmp_path / ".importlinter")
    if not with_scope and (tmp_path / ".first-ade" / "scope.yaml").exists():
        (tmp_path / ".first-ade" / "scope.yaml").unlink()
    elif with_scope:
        (tmp_path / ".first-ade" / "scope.yaml").write_text(
            'version: "0.1"\ntask: "fixture"\nallowed_paths:\n  - "src/**"\n  - "tests/**"\n',
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
    (tmp_path / "src" / "first_ade" / "adapters" / "helper.py").write_text("ADAPTER_VAL = 2\n", encoding="utf-8")
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok(): assert True\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_negative_agent_tamper_axioms(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / ".first-ade" / "axioms.yaml").write_text(
        (repo / ".first-ade" / "axioms.yaml").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-01]" in res.output


def test_negative_outside_scope_allowed_paths(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path, with_scope=True)
    (repo / "README_ROGUE.md").write_text("rogue edit\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-SCOPE]" in res.output


def test_negative_rename_into_protected_path(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / "tests" / "guardrails").mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "mv", "tests/test_ok.py", "tests/guardrails/test_ok.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-01]" in res.output


def test_negative_domain_imports_adapters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / "src" / "first_ade" / "domain" / "bad_import.py").write_text(
        "from first_ade.adapters.helper import ADAPTER_VAL\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(repo / "src"))
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-02]" in res.output


def test_negative_guard_edit_without_paired_test(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / "src" / "first_ade" / "domain" / "guards.py").write_text("VALUE = 2\n", encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-03]" in res.output


def test_negative_ast_grep_shell_true(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / "src" / "first_ade" / "adapters" / "unsafe.py").write_text(
        'import subprocess\nsubprocess.run("echo hi", shell=True)\n',
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-04]" in res.output


def test_negative_malformed_hook_stdin(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    runner = CliRunner()
    res = runner.invoke(main, ["hook", "--repo-root", str(repo)], input="{not-json")
    assert res.exit_code == 2
    assert "Malformed stdin JSON" in res.output


def test_negative_missing_cue_binary_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_fixture_repo(tmp_path)
    monkeypatch.setattr("first_ade.adapters.cue_adapter.find_binary", lambda _: None)
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-CUE]" in res.output


def test_negative_first_ade_agent_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / ".first-ade" / "axioms.yaml").write_text(
        (repo / ".first-ade" / "axioms.yaml").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("FIRST_ADE_AGENT", "1")
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-AX-01]" in res.output


def test_negative_rename_out_of_allowed_paths(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path, with_scope=True)
    subprocess.run(
        ["git", "mv", "src/first_ade/adapters/helper.py", "rogue_outside.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert "[ADE-SCOPE]" in res.output


def test_negative_ast_grep_eval_and_exec(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / "src" / "first_ade" / "adapters" / "unsafe_dyn.py").write_text(
        'x = eval("1 + 1")\nexec("y = 2")\n',
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(main, ["check", "--mode", "human", "--repo-root", str(repo)])
    assert res.exit_code == 2
    assert res.output.count("[ADE-AX-04]") >= 2


def test_negative_stop_hook_blocks_dirty_repo(tmp_path: Path) -> None:
    repo = _init_fixture_repo(tmp_path)
    (repo / ".first-ade" / "axioms.yaml").write_text(
        (repo / ".first-ade" / "axioms.yaml").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(main, ["hook", "--repo-root", str(repo)], input='{"hook_event_name": "Stop"}')
    assert res.exit_code == 2
    assert "[ADE-AX-01]" in res.output


def test_negative_sarif_dual_surface_parity(tmp_path: Path) -> None:
    import gzip
    import json

    repo = _init_fixture_repo(tmp_path)
    (repo / ".first-ade" / "axioms.yaml").write_text(
        (repo / ".first-ade" / "axioms.yaml").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    sarif_file = tmp_path / "results.sarif"
    receipt_file = tmp_path / "receipt.md"
    runner = CliRunner()

    term_res = runner.invoke(main, ["check", "--mode", "agent", "--repo-root", str(repo)])
    sarif_res = runner.invoke(
        main,
        [
            "check",
            "--mode",
            "agent",
            "--format",
            "sarif",
            "--output",
            str(sarif_file),
            "--receipt",
            str(receipt_file),
            "--repo-root",
            str(repo),
        ],
    )
    assert term_res.exit_code == 2
    assert sarif_res.exit_code == 2

    sarif = json.loads(sarif_file.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    assert sarif["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
    results = sarif["runs"][0]["results"]
    assert len(results) >= 1
    assert any(r["ruleId"] == "ADE-AX-01" for r in results)
    for r in results:
        assert r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        assert r["partialFingerprints"]["primaryLocationLineHash"]
    assert len(gzip.compress(sarif_file.read_bytes())) <= 10 * 1024 * 1024
    assert "First-ADE Run Receipt (FAIL)" in receipt_file.read_text(encoding="utf-8")
