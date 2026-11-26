"""Git diff port interface."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from first_ade.domain.models import FileChange


class GitPort(Protocol):
    """Abstract interface for retrieving normalized repository changes."""

    def get_changed_files(
        self,
        repo_root: Path,
        staged: bool = False,
        base_ref: str | None = None,
    ) -> tuple[list[FileChange], list[str]]:
        """Return (changes, diagnostic_notes) for the target diff scope."""
        ...
