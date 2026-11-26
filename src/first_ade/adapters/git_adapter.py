# implements: FR-001
# traces_to: Π.3.1
"""Git subprocess adapter implementing GitPort."""

from __future__ import annotations

import subprocess
from pathlib import Path

from first_ade.domain.models import FileChange
from first_ade.domain.paths import normalize_repo_path


def get_empty_tree_hash(repo_root: Path) -> str:
    """Compute the repository's empty tree object hash dynamically via Git."""
    proc = _run_git(repo_root, ["hash-object", "-t", "tree", "/dev/null"])
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(f"Failed to compute empty tree hash: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _ref_exists(repo_root: Path, ref: str) -> bool:
    proc = _run_git(repo_root, ["rev-parse", "--verify", "--quiet", ref])
    return proc.returncode == 0


def parse_name_status_lines(output: str, repo_root: Path | None = None) -> list[FileChange]:
    """Parse `git diff --name-status -M` output into normalized FileChange objects."""
    changes: list[FileChange] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if (status.startswith("R") or status.startswith("C")) and len(parts) >= 3:
            old_path = normalize_repo_path(parts[1], repo_root)
            new_path = normalize_repo_path(parts[2], repo_root)
            changes.append(FileChange(status=status, path=new_path, old_path=old_path))
        elif len(parts) >= 2:
            path = normalize_repo_path(parts[1], repo_root)
            changes.append(FileChange(status=status, path=path))
    return changes


class SubprocessGitAdapter:
    """Git adapter using `git diff --name-status -M` with base-ref fallback."""

    def get_changed_files(
        self,
        repo_root: Path,
        staged: bool = False,
        base_ref: str | None = None,
    ) -> tuple[list[FileChange], list[str]]:
        notes: list[str] = []
        if staged:
            proc = _run_git(repo_root, ["diff", "--cached", "--name-status", "-M"])
            if proc.returncode != 0:
                raise RuntimeError(f"git diff --cached failed: {proc.stderr.strip()}")
            return parse_name_status_lines(proc.stdout, repo_root), notes

        resolved_ref = base_ref or "HEAD"
        if not _ref_exists(repo_root, resolved_ref):
            if _ref_exists(repo_root, "HEAD~1"):
                notes.append(f"Base ref '{resolved_ref}' not found; fell back to 'HEAD~1'.")
                resolved_ref = "HEAD~1"
            else:
                empty_tree = get_empty_tree_hash(repo_root)
                notes.append(
                    f"Base ref '{resolved_ref}' and 'HEAD~1' not found; fell back to empty tree '{empty_tree}'."
                )
                resolved_ref = empty_tree

        diff_args = ["diff", "--name-status", "-M", resolved_ref]
        proc = _run_git(repo_root, diff_args)
        if proc.returncode != 0:
            raise RuntimeError(f"git diff failed: {proc.stderr.strip()}")
        changes = parse_name_status_lines(proc.stdout, repo_root)

        # Include untracked non-ignored files so newly created files are also checked
        untracked = _run_git(repo_root, ["ls-files", "--others", "--exclude-standard"])
        if untracked.returncode == 0:
            seen = {c.path for c in changes}
            for raw in untracked.stdout.splitlines():
                norm = normalize_repo_path(raw, repo_root)
                if norm and norm not in seen:
                    changes.append(FileChange(status="A", path=norm))
                    seen.add(norm)

        return changes, notes
