"""OASIS SARIF 2.1.0 normalizer and serializer."""

from __future__ import annotations

import gzip
import hashlib
import json
from typing import Any

from first_ade.domain.models import Violation
from first_ade.domain.paths import normalize_repo_path

SARIF_SCHEMA_URL = "https://json.schemastore.org/sarif-2.1.0.json"
MAX_SARIF_RESULTS = 5000
MAX_SARIF_GZIP_BYTES = 10 * 1024 * 1024  # 10 MB

_SEVERITY_ORDER = {"error": 0, "warning": 1, "note": 2, "none": 3}


def _fingerprint(rule_id: str, uri: str, line: int, message: str) -> str:
    payload = f"{rule_id}|{uri}|{line}|{message}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _severity_to_level(severity: str) -> str:
    sev = severity.lower()
    if sev in ("error", "warning", "note", "none"):
        return sev
    return "error"


def normalize_external_sarif(raw_sarif: dict[str, Any], default_axiom_id: str = "ADE-AX-04") -> list[Violation]:
    """Sanitize non-conforming external SARIF (e.g., ast-grep) into Violation objects."""
    violations: list[Violation] = []
    runs = raw_sarif.get("runs")
    if not isinstance(runs, list):
        return violations

    for run in runs:
        if not isinstance(run, dict):
            continue
        results = run.get("results") or []
        if not isinstance(results, list):
            continue
        for res in results:
            if not isinstance(res, dict):
                continue
            rule_id = str(res.get("ruleId") or default_axiom_id)
            level = str(res.get("level") or "error")
            msg_obj = res.get("message")
            message = (
                str(msg_obj.get("text") or "Static analysis violation")
                if isinstance(msg_obj, dict)
                else str(msg_obj or "Static analysis violation")
            )
            locations = res.get("locations") or []
            uri = "unknown"
            line = 1
            if isinstance(locations, list) and locations:
                loc0 = locations[0] if isinstance(locations[0], dict) else {}
                phys = loc0.get("physicalLocation") or {}
                if isinstance(phys, dict):
                    art = phys.get("artifactLocation") or {}
                    if isinstance(art, dict) and art.get("uri"):
                        uri = normalize_repo_path(str(art["uri"]))
                    reg = phys.get("region") or {}
                    if isinstance(reg, dict) and isinstance(reg.get("startLine"), int):
                        line = max(1, reg["startLine"])
            violations.append(
                Violation(
                    axiom_id=rule_id,
                    file=uri,
                    line=line,
                    reason=message,
                    fix_hint="Remediate the static analysis finding.",
                    severity=_severity_to_level(level),
                )
            )
    return violations


def build_sarif_report(violations: list[Violation], tool_version: str = "0.1.0") -> dict[str, Any]:
    """Build a valid OASIS SARIF 2.1.0 document, sorted by severity and capped at limits."""
    sorted_violations = sorted(
        violations,
        key=lambda v: (_SEVERITY_ORDER.get(v.severity.lower(), 0), v.axiom_id, v.file, v.line),
    )[:MAX_SARIF_RESULTS]

    rules_map: dict[str, dict[str, Any]] = {}
    sarif_results: list[dict[str, Any]] = []

    for v in sorted_violations:
        if v.axiom_id not in rules_map:
            rules_map[v.axiom_id] = {
                "id": v.axiom_id,
                "name": v.axiom_id,
                "shortDescription": {"text": f"First-ADE invariant {v.axiom_id}"},
                "defaultConfiguration": {"level": _severity_to_level(v.severity)},
            }
        uri = normalize_repo_path(v.file) or "repo"
        line = max(1, v.line)
        fp = _fingerprint(v.axiom_id, uri, line, v.reason)
        sarif_results.append(
            {
                "ruleId": v.axiom_id,
                "level": _severity_to_level(v.severity),
                "message": {"text": f"{v.reason} — {v.fix_hint}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri, "uriBaseId": "%SRCROOT%"},
                            "region": {"startLine": line},
                        }
                    }
                ],
                "partialFingerprints": {"primaryLocationLineHash": fp},
            }
        )

    doc: dict[str, Any] = {
        "$schema": SARIF_SCHEMA_URL,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "first-ade",
                        "version": tool_version,
                        "informationUri": "https://github.com/First-ADE/first-ade",
                        "rules": list(rules_map.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }

    # Enforce 10 MB gzip ceiling by trimming results if ever exceeded
    while len(gzip.compress(json.dumps(doc).encode("utf-8"))) > MAX_SARIF_GZIP_BYTES and doc["runs"][0]["results"]:
        half = max(1, len(doc["runs"][0]["results"]) // 2)
        doc["runs"][0]["results"] = doc["runs"][0]["results"][:half]

    return doc
