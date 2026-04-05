"""Subprocess execution engine for running user solutions."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from cses_cli.models import RunResult, TestCase, Verdict

DEFAULT_TIMEOUT = 5.0


def run_solution(
    code_path: Path,
    test_case: TestCase,
    timeout: float = DEFAULT_TIMEOUT,
    python_cmd: str = "python3",
) -> RunResult:
    """Run a user's Python solution against a single test case.

    The solution is executed as `python3 <code_path>` with the test case
    input piped to stdin. Returns a RunResult with verdict, output, and timing.
    """
    start = time.perf_counter()

    harness_path = Path(__file__).parent / "harness.py"

    try:
        result = subprocess.run(
            [python_cmd, str(harness_path), str(code_path)],
            input=test_case.input,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - start

        if result.returncode != 0:
            return RunResult(
                test_case=test_case,
                verdict=Verdict.RUNTIME_ERROR,
                actual_output=result.stdout,
                stderr=result.stderr,
                elapsed_seconds=elapsed,
                return_code=result.returncode,
            )

        return RunResult(
            test_case=test_case,
            verdict=Verdict.ACCEPTED,  # placeholder — judge decides final verdict
            actual_output=result.stdout,
            stderr=result.stderr,
            elapsed_seconds=elapsed,
            return_code=result.returncode,
        )

    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return RunResult(
            test_case=test_case,
            verdict=Verdict.TIME_LIMIT_EXCEEDED,
            elapsed_seconds=elapsed,
        )
