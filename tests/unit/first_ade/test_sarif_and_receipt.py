"""Unit tests for OASIS SARIF 2.1.0 normalizer and Run Receipt generator."""

from __future__ import annotations

import gzip
import json

from first_ade.domain.models import CheckResult, Violation
from first_ade.domain.receipt import render_run_receipt
from first_ade.domain.sarif import (
    MAX_SARIF_GZIP_BYTES,
    MAX_SARIF_RESULTS,
    SARIF_SCHEMA_URL,
    build_sarif_report,
    normalize_external_sarif,
)


def test_normalize_external_sarif_fills_missing_fields() -> None:
    raw = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "ast-grep"}},
                "results": [
                    {
                        "ruleId": "no-eval",
                        "message": {"text": "Avoid eval()"},
                        "locations": [
                            {"physicalLocation": {"artifactLocation": {"uri": r"src\first_ade\bad.py"}}}
                        ],
                    }
                ],
            }
        ],
    }
    violations = normalize_external_sarif(raw)
    assert len(violations) == 1
    assert violations[0].axiom_id == "no-eval"
    assert violations[0].file == "src/first_ade/bad.py"
    assert violations[0].line == 1


def test_build_sarif_report_valid_schema_and_limits() -> None:
    violations = [
        Violation("ADE-AX-04", "src/a.py", 10, "eval used", "remove eval", severity="warning"),
        Violation("ADE-AX-01", ".first-ade/axioms.yaml", 1, "tamper", "revert", severity="error"),
    ]
    sarif = build_sarif_report(violations)
    assert sarif["$schema"] == SARIF_SCHEMA_URL
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    assert len(run["tool"]["driver"]["rules"]) == 2
    results = run["results"]
    assert len(results) == 2
    # Sorted by severity: error before warning
    assert results[0]["ruleId"] == "ADE-AX-01"
    assert results[0]["partialFingerprints"]["primaryLocationLineHash"]
    assert results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == ".first-ade/axioms.yaml"

    compressed = gzip.compress(json.dumps(sarif).encode("utf-8"))
    assert len(compressed) <= MAX_SARIF_GZIP_BYTES
    assert len(results) <= MAX_SARIF_RESULTS


def test_render_run_receipt() -> None:
    res = CheckResult(
        violations=[],
        warnings=["[ADE-SCOPE] warning"],
        passed_axioms=["ADE-AX-01", "ADE-AX-02"],
        failed_axioms=[],
        waived_axioms=[],
        elapsed_ms=42.5,
    )
    md = render_run_receipt(res)
    assert "First-ADE Run Receipt (PASS)" in md
    assert "ADE-AX-01" in md
    assert "42.5 ms" in md
