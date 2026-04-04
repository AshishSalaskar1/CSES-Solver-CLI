"""Seed the CSES database with all 258 problems and sample test cases."""

from __future__ import annotations

import sys
from pathlib import Path

from cses_cli.db import get_connection, init_db, insert_problem, insert_test_case
from cses_cli.models import Problem, TestCase
from cses_cli.problems_data import ALL_PROBLEMS

SAMPLE_DATA: list[dict] = [
    {
        "problem": Problem(
            task_id=1068,
            title="Weird Algorithm",
            category="Introductory Problems",
            url="https://cses.fi/problemset/task/1068",
        ),
        "cases": [
            {"input": "3\n", "expected": "3 10 5 16 8 4 2 1\n"},
            {"input": "1\n", "expected": "1\n"},
            {"input": "2\n", "expected": "2 1\n"},
            {"input": "4\n", "expected": "4 2 1\n"},
            {"input": "10\n", "expected": "10 5 16 8 4 2 1\n"},
            {"input": "7\n", "expected": "7 22 11 34 17 52 26 13 40 20 10 5 16 8 4 2 1\n"},
            {"input": "27\n", "expected": "27 82 41 124 62 31 94 47 142 71 214 107 322 161 484 242 121 364 182 91 274 137 412 206 103 310 155 466 233 700 350 175 526 263 790 395 1186 593 1780 890 445 1336 668 334 167 502 251 754 377 1132 566 283 850 425 1276 638 319 958 479 1438 719 2158 1079 3238 1619 4858 2429 7288 3644 1822 911 2734 1367 4102 2051 6154 3077 9232 4616 2308 1154 577 1732 866 433 1300 650 325 976 488 244 122 61 184 92 46 23 70 35 106 53 160 80 40 20 10 5 16 8 4 2 1\n"},
            {"input": "100\n", "expected": "100 50 25 76 38 19 58 29 88 44 22 11 34 17 52 26 13 40 20 10 5 16 8 4 2 1\n"},
        ],
    },
    {
        "problem": Problem(
            task_id=1083,
            title="Missing Number",
            category="Introductory Problems",
            url="https://cses.fi/problemset/task/1083",
        ),
        "cases": [
            {"input": "5\n2 3 1 5\n", "expected": "4\n"},
            {"input": "1\n", "expected": "1\n", "is_edge": True},
            {"input": "2\n1\n", "expected": "2\n"},
            {"input": "2\n2\n", "expected": "1\n"},
            {"input": "3\n1 3\n", "expected": "2\n"},
            {"input": "6\n2 6 1 4 5\n", "expected": "3\n"},
            {"input": "10\n1 2 3 4 5 6 7 8 9\n", "expected": "10\n", "is_edge": True},
            {"input": "10\n2 3 4 5 6 7 8 9 10\n", "expected": "1\n", "is_edge": True},
        ],
    },
    {
        "problem": Problem(
            task_id=1069,
            title="Repetitions",
            category="Introductory Problems",
            url="https://cses.fi/problemset/task/1069",
        ),
        "cases": [
            {"input": "ATTCGGGA\n", "expected": "3\n"},
            {"input": "A\n", "expected": "1\n", "is_edge": True},
            {"input": "AAAA\n", "expected": "4\n"},
            {"input": "ACGT\n", "expected": "1\n"},
            {"input": "AABBCCDD\n", "expected": "2\n"},
            {"input": "TTTTTTTTTTT\n", "expected": "11\n"},
            {"input": "GCGCGCGCGCG\n", "expected": "1\n"},
            {"input": "AACCCBBAAAA\n", "expected": "4\n"},
        ],
    },
    {
        "problem": Problem(
            task_id=1094,
            title="Increasing Array",
            category="Introductory Problems",
            url="https://cses.fi/problemset/task/1094",
        ),
        "cases": [
            {"input": "5\n3 2 5 1 7\n", "expected": "5\n"},
            {"input": "1\n5\n", "expected": "0\n", "is_edge": True},
            {"input": "3\n1 2 3\n", "expected": "0\n"},
            {"input": "3\n3 2 1\n", "expected": "3\n"},
            {"input": "4\n5 5 5 5\n", "expected": "0\n"},
            {"input": "5\n1 1 1 1 1\n", "expected": "0\n"},
            {"input": "6\n10 1 1 1 1 1\n", "expected": "45\n"},
            {"input": "4\n1 3 2 4\n", "expected": "1\n"},
        ],
    },
    {
        "problem": Problem(
            task_id=1070,
            title="Permutations",
            category="Introductory Problems",
            url="https://cses.fi/problemset/task/1070",
        ),
        "cases": [
            # n=1 → "1"
            {"input": "1\n", "expected": "1\n"},
            # n=2 → NO SOLUTION
            {"input": "2\n", "expected": "NO SOLUTION\n"},
            # n=3 → NO SOLUTION
            {"input": "3\n", "expected": "NO SOLUTION\n"},
            # n=4 → one valid permutation: "2 4 1 3"
            {"input": "4\n", "expected": "2 4 1 3\n"},
            # n=5 → one valid permutation: "2 4 1 3 5"
            {"input": "5\n", "expected": "2 4 1 3 5\n"},
            # n=8 → "2 4 6 8 1 3 5 7"
            {"input": "8\n", "expected": "2 4 6 8 1 3 5 7\n"},
        ],
    },
]


def seed(db_path: Path | None = None) -> None:
    """Populate the database with all 258 problems and sample test cases."""
    init_db(db_path)

    # Seed all 258 problem metadata
    for task_id, title, category, url in ALL_PROBLEMS:
        p = Problem(task_id=task_id, title=title, category=category, url=url)
        insert_problem(p, db_path)

    # Seed hand-written test cases for sample problems
    for entry in SAMPLE_DATA:
        problem: Problem = entry["problem"]
        for i, case in enumerate(entry["cases"], start=1):
            tc = TestCase(
                id=0,
                task_id=problem.task_id,
                case_num=i,
                input=case["input"],
                expected=case["expected"],
                is_edge=case.get("is_edge", False),
            )
            insert_test_case(tc, db_path)

    print(f"Seeded {len(ALL_PROBLEMS)} problems ({len(SAMPLE_DATA)} with test cases) into database.")


if __name__ == "__main__":
    seed()
