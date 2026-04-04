"""Reference solutions for CSES Interactive problems.

Interactive problems cannot be solved in batch mode (they require
back-and-forth communication with a judge), so no solutions are provided.
"""

from __future__ import annotations


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


SOLUTIONS: dict[int, object] = {}
