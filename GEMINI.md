# First-ADE Agent Instructions

1. Run `uv run first-ade check --mode agent` before completing any task.
2. Respect `.first-ade/scope.yaml` (`allowed_paths`) and never modify protected files in `.first-ade/axioms.yaml` (`ADE-AX-01`).
3. If `first-ade` exits with code `2`, read `[ADE-AX-XX] file:line — reason — fix hint` on `stderr` and fix the violation.
4. Never bypass or weaken guardrail tests (`tests/guardrails/**`) or CI workflows.
