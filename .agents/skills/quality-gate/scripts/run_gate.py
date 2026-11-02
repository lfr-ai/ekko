"""Run every declared quality-gate command and report a single pass/fail summary.

This is a thin orchestrator, not a reimplementation: every check it runs is the
project's own declared command (`Taskfile.yml` / `pyproject.toml`). It carries
zero hardcoded thresholds and adds nothing ruff/ty/pytest/pre-commit do not
already enforce — it exists only to give agents (and humans) one command that
runs the complete gate and reports which step, if any, failed.

Run standalone::

    uv run python .agents/skills/quality-gate/scripts/run_gate.py [--skip-tests] [--full]

Exit status is non-zero when any step fails. By default every step runs the
repository's fast tier (`task test`/`task check` exclude `slow`-marked tests
and Docker/network-dependent pre-commit hooks). Pass ``--full`` to run the
complete tier instead (`task test:all` + an added `check:slow` step) — the
same checks CI runs on every build.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_REPO_ROOT = Path(__file__).resolve().parents[4]

# Each step shells out to the repository's OWN declared task; the Taskfile is
# the single source of truth for the underlying command.
_GATE_STEPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("format", ("task", "format")),
    ("lint", ("task", "lint")),
    ("typecheck", ("task", "typecheck")),
    ("test", ("task", "test")),
    ("check", ("task", "check")),
)

# --full swaps the fast `test` step for the complete suite and appends the
# manual-stage pre-commit hooks (jscpd, dependency-audit, hadolint, lychee).
_FULL_TEST_STEP: tuple[str, tuple[str, ...]] = ("test", ("task", "test:all"))
_SLOW_CHECK_STEP: tuple[str, tuple[str, ...]] = ("check:slow", ("task", "check:slow"))


@dataclass(frozen=True, kw_only=True, slots=True)
class GateResult:
    """Outcome of one quality-gate step."""

    name: str
    command: tuple[str, ...]
    exit_code: int

    @property
    def passed(self) -> bool:
        """Whether this step exited successfully."""
        return self.exit_code == 0


def run_gate(steps: Sequence[tuple[str, tuple[str, ...]]]) -> list[GateResult]:
    """Run each declared step in order and stop at the first failure.

    Args:
        steps (Sequence[tuple[str, tuple[str, ...]]]): Step name and command
            pairs to execute, in order.

    Returns:
        list[GateResult]: One result per step attempted (stops early on the
            first failure so later steps are not attempted against a known-bad
            tree).
    """
    results: list[GateResult] = []
    for name, command in steps:
        # Command is a fixed tuple from _GATE_STEPS, never user/network input.
        completed = subprocess.run(command, cwd=_REPO_ROOT, check=False)  # noqa: S603
        results.append(
            GateResult(name=name, command=command, exit_code=completed.returncode)
        )
        if completed.returncode != 0:
            break
    return results


def _report(results: list[GateResult]) -> int:
    """Write a human-readable summary and compute the process exit code.

    Args:
        results (list[GateResult]): Results to report, in execution order.

    Returns:
        int: ``0`` when every step passed, otherwise ``1``.
    """
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        sys.stdout.write(f"[{status}] {result.name}: {' '.join(result.command)}\n")
    if all(result.passed for result in results):
        sys.stdout.write("quality-gate: all steps passed.\n")
        return 0
    sys.stderr.write("quality-gate: stopped at the first failing step.\n")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the quality gate and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments; pass
            ``--skip-tests`` to omit the `test` step, e.g. while iterating on
            non-test changes, or ``--full`` to run the complete (slow) tier
            instead of the default fast tier.

    Returns:
        int: ``0`` when every attempted step passed, otherwise ``1``.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    full = "--full" in args
    steps = tuple(
        _FULL_TEST_STEP if full and name == "test" else (name, command)
        for name, command in _GATE_STEPS
    )
    if full:
        steps = (*steps, _SLOW_CHECK_STEP)
    if "--skip-tests" in args:
        steps = tuple(step for step in steps if step[0] != "test")
    return _report(run_gate(steps))


if __name__ == "__main__":
    raise SystemExit(main())
