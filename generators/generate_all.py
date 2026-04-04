"""Test case generator framework for CSES CLI.

This module provides the infrastructure to generate test cases for all CSES
problems using reference solutions and random input generators.
"""

from __future__ import annotations

import importlib
import random
import signal
import sys
from pathlib import Path
from typing import Callable, Optional

from cses_cli.db import get_connection, init_db
from cses_cli.models import Problem, TestCase
from cses_cli.problems_data import ALL_PROBLEMS

GENERATORS_DIR = Path(__file__).resolve().parent
REF_SOLUTIONS_DIR = GENERATORS_DIR / "reference_solutions"

# Timeout per individual test case solve (seconds)
SOLVE_TIMEOUT = 10

# Maps category name → module name in reference_solutions/
CATEGORY_MODULES = {
    "Introductory Problems": "introductory",
    "Sorting and Searching": "sorting_searching",
    "Dynamic Programming": "dynamic_programming",
    "Graph Algorithms": "graph_algorithms",
    "Range Queries": "range_queries",
    "Tree Algorithms": "tree_algorithms",
    "Advanced Techniques": "advanced_techniques",
    "Sliding Window Problems": "sliding_window",
    "Interactive Problems": "interactive",
    "Bitwise Operations": "bitwise_operations",
    "Advanced Graph Problems": "advanced_graph",
    "Counting Problems": "counting",
}


class _SolveTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise _SolveTimeout()


def _solve_with_timeout(solver, task_id, input_data, timeout=SOLVE_TIMEOUT):
    """Run a solver with a timeout to avoid hanging on slow problems."""
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)
    try:
        result = solver(task_id, input_data)
        signal.alarm(0)
        return result
    except _SolveTimeout:
        return None
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)


def load_reference_solver(category: str) -> Optional[Callable[[int, str], Optional[str]]]:
    """Load the reference solution module for a category."""
    module_name = CATEGORY_MODULES.get(category)
    if module_name is None:
        return None
    try:
        mod = importlib.import_module(f"generators.reference_solutions.{module_name}")
        return mod.solve
    except (ImportError, AttributeError):
        return None


def get_input_generator(task_id: int) -> Optional[Callable[..., str]]:
    """Get the input generator function for a specific problem."""
    try:
        mod = importlib.import_module("generators.input_generators")
        gen_fn = getattr(mod, f"gen_{task_id}", None)
        return gen_fn
    except ImportError:
        return None


def generate_test_cases(
    task_id: int,
    category: str,
    num_cases: int = 20,
    db_path: Optional[Path] = None,
) -> int:
    """Generate test cases for a single problem.

    Returns the number of test cases successfully generated.
    """
    solver = load_reference_solver(category)
    if solver is None:
        return 0

    gen_fn = get_input_generator(task_id)
    if gen_fn is None:
        return 0

    conn = get_connection(db_path)
    generated = 0
    consecutive_timeouts = 0

    for case_num in range(1, num_cases + 1):
        try:
            if case_num <= 3:
                input_data = gen_fn(size="minimum")
            elif case_num <= 6:
                input_data = gen_fn(size="small")
            elif case_num <= 14:
                input_data = gen_fn(size="medium")
            else:
                input_data = gen_fn(size="edge")

            expected = _solve_with_timeout(solver, task_id, input_data)
            if expected is None:
                consecutive_timeouts += 1
                if consecutive_timeouts >= 3:
                    # Skip this problem if solver is too slow
                    break
                continue

            consecutive_timeouts = 0
            conn.execute(
                "INSERT OR REPLACE INTO test_cases "
                "(task_id, case_num, input, expected, is_edge) VALUES (?, ?, ?, ?, ?)",
                (task_id, case_num, input_data, expected + "\n" if not expected.endswith("\n") else expected, int(case_num > 14)),
            )
            generated += 1
        except Exception as e:
            print(f"  Warning: task {task_id} case {case_num}: {e}", file=sys.stderr)
            consecutive_timeouts += 1
            if consecutive_timeouts >= 3:
                break
            continue

    conn.commit()
    conn.close()
    return generated


def generate_all(
    categories: Optional[list[str]] = None,
    num_cases: int = 20,
    db_path: Optional[Path] = None,
) -> dict[str, int]:
    """Generate test cases for all problems in the specified categories.

    Returns a dict of category → total cases generated.
    """
    init_db(db_path)

    from collections import defaultdict
    problems_by_cat: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for task_id, title, category, url in ALL_PROBLEMS:
        if categories is None or category in categories:
            problems_by_cat[category].append((task_id, title))

    results: dict[str, int] = {}

    for category, problems in problems_by_cat.items():
        cat_total = 0
        solver = load_reference_solver(category)
        if solver is None:
            print(f"  [{category}] No reference solution module found, skipping.")
            results[category] = 0
            continue

        for task_id, title in problems:
            count = generate_test_cases(task_id, category, num_cases, db_path)
            if count > 0:
                print(f"  [{category}] #{task_id} {title}: {count} cases")
                cat_total += count

        results[category] = cat_total
        print(f"  [{category}] Total: {cat_total} cases")

    return results
