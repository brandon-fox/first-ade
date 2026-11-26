"""Pure-Python POSIX path normalization and glob matching."""

from __future__ import annotations

import os
import posixpath
import re
from functools import lru_cache
from pathlib import Path


def normalize_repo_path(raw_path: str, repo_root: Path | None = None) -> str:
    """Normalize a file path to a clean POSIX relative path.

    Handles Windows backslashes, leading './', redundant '//', '..' traversal,
    and symlinks (when repo_root is provided and the path exists).
    """
    cleaned = raw_path.strip().replace("\\", "/")
    if not cleaned:
        return ""

    if repo_root is not None:
        root_resolved = repo_root.resolve()
        candidate = Path(cleaned)
        if not candidate.is_absolute():
            candidate = root_resolved / candidate
        try:
            resolved = candidate.resolve()
            rel = resolved.relative_to(root_resolved)
            return rel.as_posix()
        except ValueError:
            # Path escapes repo_root or is on another drive; normalize lexically.
            pass

        # If raw_path was absolute inside repo_root (e.g. symlink target or non-existent)
        if os.path.isabs(raw_path):
            try:
                rel = Path(os.path.normpath(raw_path)).relative_to(root_resolved)
                return rel.as_posix()
            except ValueError:
                pass

    normed = posixpath.normpath(cleaned)
    if normed == ".":
        return ""
    while normed.startswith("./"):
        normed = normed[2:]
    return normed


@lru_cache(maxsize=512)
def _compile_glob(pattern: str) -> re.Pattern[str]:
    """Compile a POSIX glob pattern supporting '**', '*', and '?' into regex."""
    norm_pat = normalize_repo_path(pattern)
    parts: list[str] = ["^"]
    i = 0
    n = len(norm_pat)
    while i < n:
        if norm_pat[i : i + 3] == "**/":
            parts.append("(?:.+/)?")
            i += 3
        elif norm_pat[i : i + 2] == "**":
            parts.append(".*")
            i += 2
        elif norm_pat[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif norm_pat[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(norm_pat[i]))
            i += 1
    parts.append("$")
    return re.compile("".join(parts))


def matches_glob(path: str, pattern: str) -> bool:
    """Return True if normalized POSIX path matches the glob pattern."""
    norm_path = normalize_repo_path(path)
    if not norm_path:
        return False
    return bool(_compile_glob(pattern).match(norm_path))


def matches_any_glob(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    """Return True if normalized path matches at least one glob pattern."""
    return any(matches_glob(path, pat) for pat in patterns)
