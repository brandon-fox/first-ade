"""Compact Markdown Run Receipt generator for PR checks."""

from __future__ import annotations

from first_ade.domain.models import CheckResult


def render_run_receipt(result: CheckResult) -> str:
    """Render a concise Markdown summary of passed, failed, and waived axioms."""
    status = "PASS" if result.ok else "FAIL"
    lines = [
        f"## First-ADE Run Receipt ({status})",
        "",
        f"- **Elapsed:** `{result.elapsed_ms:.1f} ms`",
        f"- **Passed Axioms:** {', '.join(result.passed_axioms) if result.passed_axioms else 'none'}",
        f"- **Failed Axioms:** {', '.join(result.failed_axioms) if result.failed_axioms else 'none'}",
        f"- **Waived Axioms:** {', '.join(result.waived_axioms) if result.waived_axioms else 'none'}",
    ]
    if result.warnings:
        lines.append("")
        lines.append("### Warnings")
        for w in result.warnings:
            lines.append(f"- {w}")
    if result.violations:
        lines.append("")
        lines.append("### Violations")
        for v in result.violations[:25]:
            lines.append(f"- `{v.format_terminal()}`")
        if len(result.violations) > 25:
            lines.append(f"- ... and {len(result.violations) - 25} more")
    if result.notes:
        lines.append("")
        lines.append("### Notes")
        for n in result.notes:
            lines.append(f"- {n}")
    return "\n".join(lines) + "\n"
