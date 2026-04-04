"""Output comparison logic for judging solutions."""

from __future__ import annotations

from cses_cli.models import RunResult, Verdict


def compare_output(actual: str, expected: str) -> bool:
    """Compare actual output to expected output.

    Strips trailing whitespace/newlines and compares line by line.
    This handles the common trailing-newline issue in competitive programming.
    """
    actual_lines = actual.strip().splitlines()
    expected_lines = expected.strip().splitlines()
    return actual_lines == expected_lines


def judge(result: RunResult) -> RunResult:
    """Apply the final verdict to a RunResult.

    If the runner already assigned TLE or RE, keep that verdict.
    Otherwise, compare output to determine ACCEPTED vs WRONG_ANSWER.
    """
    if result.verdict in (Verdict.TIME_LIMIT_EXCEEDED, Verdict.RUNTIME_ERROR):
        return result

    if compare_output(result.actual_output, result.test_case.expected):
        result.verdict = Verdict.ACCEPTED
    else:
        result.verdict = Verdict.WRONG_ANSWER

    return result
