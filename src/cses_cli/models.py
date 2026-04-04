"""Data models for CSES CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Problem:
    """A CSES problem."""

    task_id: int
    title: str
    category: str
    url: str


@dataclass
class TestCase:
    """A single test case for a problem."""

    id: int
    task_id: int
    case_num: int
    input: str
    expected: str
    is_edge: bool = False


class Verdict(Enum):
    """Possible verdicts for a test run."""

    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG ANSWER"
    RUNTIME_ERROR = "RUNTIME ERROR"
    TIME_LIMIT_EXCEEDED = "TIME LIMIT EXCEEDED"


@dataclass
class RunResult:
    """Result of running user code against a single test case."""

    test_case: TestCase
    verdict: Verdict
    actual_output: str = ""
    stderr: str = ""
    elapsed_seconds: float = 0.0
    return_code: int = 0
