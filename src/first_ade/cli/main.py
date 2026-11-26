"""Click CLI entrypoint for `first-ade`."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from first_ade.cli.hook import process_hook_stdin
from first_ade.cli.runner import run_checks
from first_ade.domain.models import Mode
from first_ade.domain.receipt import render_run_receipt
from first_ade.domain.sarif import build_sarif_report


def _resolve_mode(mode_opt: str | None) -> Mode:
    if mode_opt:
        return Mode(mode_opt.lower())
    if os.environ.get("FIRST_ADE_AGENT", "").strip() in ("1", "true", "TRUE", "yes"):
        return Mode.AGENT
    return Mode.HUMAN


@click.group()
def main() -> None:
    """First-ADE v0.1 deterministic invariant control plane."""


@main.command("check")
@click.option("--staged", is_flag=True, help="Check staged git changes only.")
@click.option("--base", "base_ref", default=None, help="Base git ref to diff against (e.g. origin/main).")
@click.option(
    "--mode",
    "mode_opt",
    type=click.Choice(["human", "agent"], case_sensitive=False),
    default=None,
    help="Execution mode (defaults to agent if FIRST_ADE_AGENT=1, else human).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["terminal", "json", "sarif"], case_sensitive=False),
    default="terminal",
    help="Output format.",
)
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option("--receipt", "receipt_path", type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option("--repo-root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def check_cmd(
    staged: bool,
    base_ref: str | None,
    mode_opt: str | None,
    output_format: str,
    output_path: Path | None,
    receipt_path: Path | None,
    repo_root: Path,
) -> None:
    """Run deterministic invariant checks against the repository."""
    try:
        mode = _resolve_mode(mode_opt)
        result = run_checks(repo_root=repo_root.resolve(), staged=staged, base_ref=base_ref, mode=mode)
    except Exception as exc:
        click.echo(f"[ADE-CONFIG] Internal configuration error: {exc}", err=True)
        sys.exit(1)

    if output_format == "sarif":
        payload = json.dumps(build_sarif_report(result.violations), indent=2)
    elif output_format == "json":
        payload = json.dumps(
            {
                "ok": result.ok,
                "elapsed_ms": round(result.elapsed_ms, 2),
                "passed_axioms": result.passed_axioms,
                "failed_axioms": result.failed_axioms,
                "waived_axioms": result.waived_axioms,
                "warnings": result.warnings,
                "notes": result.notes,
                "violations": [
                    {
                        "axiom_id": v.axiom_id,
                        "file": v.file,
                        "line": v.line,
                        "reason": v.reason,
                        "fix_hint": v.fix_hint,
                        "severity": v.severity,
                    }
                    for v in result.violations
                ],
            },
            indent=2,
        )
    else:
        lines: list[str] = []
        for note in result.notes:
            lines.append(f"note: {note}")
        for warn in result.warnings:
            lines.append(f"warning: {warn}")
        if result.ok:
            lines.append(
                f"First-ADE PASS ({len(result.passed_axioms)} axioms passed in {result.elapsed_ms:.1f} ms)"
            )
        else:
            for v in result.violations:
                lines.append(v.format_terminal())
        payload = "\n".join(lines)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    elif not result.ok and output_format == "terminal":
        click.echo(payload, err=True)
    else:
        click.echo(payload)

    if receipt_path is not None:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(render_run_receipt(result), encoding="utf-8")

    sys.exit(0 if result.ok else 2)


@main.command("hook")
@click.option("--repo-root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def hook_cmd(repo_root: Path) -> None:
    """Claude Code PreToolUse / Stop hook reading JSON from stdin (fail-closed exit 2)."""
    try:
        raw_stdin = sys.stdin.read()
        code, stderr_msg = process_hook_stdin(raw_stdin, repo_root.resolve())
    except Exception as exc:
        click.echo(f"[ADE-HOOK] Internal hook failure: {exc}", err=True)
        sys.exit(2)

    if stderr_msg:
        click.echo(stderr_msg, err=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
