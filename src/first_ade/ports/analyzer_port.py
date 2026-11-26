"""External static analyzer port interfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from first_ade.domain.models import AstGuardConfig, BoundaryGuardConfig, Violation


class CuePort(Protocol):
    """Interface for CUE schema validation."""

    def validate(self, repo_root: Path, schema_path: Path, data_path: Path) -> list[Violation]:
        """Validate a YAML file against a CUE schema."""
        ...


class BoundaryAnalyzerPort(Protocol):
    """Interface for architectural import boundary checking."""

    def check_boundaries(self, repo_root: Path, config: BoundaryGuardConfig) -> list[Violation]:
        """Run boundary analysis and return any violations."""
        ...


class AstAnalyzerPort(Protocol):
    """Interface for AST-level static hygiene rules."""

    def scan(self, repo_root: Path, config: AstGuardConfig) -> list[Violation]:
        """Run AST scan and return normalized violations."""
        ...
