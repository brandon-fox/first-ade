"""Domain models for First-ADE invariants, diffs, and check results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    """Execution mode controlling TamperGuard enforcement."""

    HUMAN = "human"
    AGENT = "agent"


@dataclass(frozen=True)
class FileChange:
    """Normalized repository file change from git diff --name-status -M."""

    status: str
    path: str
    old_path: str | None = None


@dataclass(frozen=True)
class Violation:
    """A single deterministic invariant violation."""

    axiom_id: str
    file: str
    line: int
    reason: str
    fix_hint: str
    severity: str = "error"

    def format_terminal(self) -> str:
        """Render concise single-line terminal diagnostic."""
        return f"[{self.axiom_id}] {self.file}:{self.line} — {self.reason} — {self.fix_hint}"


@dataclass(frozen=True)
class TamperGuardConfig:
    """Configuration for ADE-AX-01 Tamper Sovereignty."""

    id: str = "ADE-AX-01"
    enabled: bool = True
    protected_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class BoundaryGuardConfig:
    """Configuration for ADE-AX-02 Hexagonal Domain Purity."""

    id: str = "ADE-AX-02"
    enabled: bool = True
    engine: str = "import-linter"
    config: str = ".importlinter"


@dataclass(frozen=True)
class CouplingRule:
    """IfThisThenThat file coupling rule."""

    name: str
    if_changed: tuple[str, ...]
    then_require: tuple[str, ...]


@dataclass(frozen=True)
class CouplingGuardConfig:
    """Configuration for ADE-AX-03 Paired Test Coupling."""

    id: str = "ADE-AX-03"
    enabled: bool = True
    rules: tuple[CouplingRule, ...] = ()


@dataclass(frozen=True)
class AstGuardConfig:
    """Configuration for ADE-AX-04 Execution Safety Hygiene."""

    id: str = "ADE-AX-04"
    enabled: bool = True
    engine: str = "ast-grep"
    rules_dir: str = ".first-ade/rules"
    target_paths: tuple[str, ...] = ("src/first_ade",)


@dataclass(frozen=True)
class AxiomsConfig:
    """Parsed .first-ade/axioms.yaml contract."""

    version: str
    project: str
    unscoped_max_files: int = 3
    tamper_guard: TamperGuardConfig = field(default_factory=TamperGuardConfig)
    boundary_guard: BoundaryGuardConfig = field(default_factory=BoundaryGuardConfig)
    coupling_guard: CouplingGuardConfig = field(default_factory=CouplingGuardConfig)
    ast_guard: AstGuardConfig = field(default_factory=AstGuardConfig)


@dataclass(frozen=True)
class Waiver:
    """Explicit human-approved waiver in scope.yaml."""

    axiom_id: str
    reason: str
    approved_by: str


@dataclass(frozen=True)
class ScopeConfig:
    """Parsed .first-ade/scope.yaml per-task boundary."""

    version: str
    task: str
    allowed_paths: tuple[str, ...] = ()
    forbidden_paths: tuple[str, ...] = ()
    waivers: tuple[Waiver, ...] = ()


@dataclass
class CheckResult:
    """Aggregated result of a First-ADE invariant check run."""

    violations: list[Violation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    passed_axioms: list[str] = field(default_factory=list)
    failed_axioms: list[str] = field(default_factory=list)
    waived_axioms: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0

    @property
    def ok(self) -> bool:
        """Return True when zero blocking violations exist."""
        return len(self.violations) == 0
