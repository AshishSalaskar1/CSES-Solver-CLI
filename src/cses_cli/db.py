"""SQLite data access layer for CSES CLI."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from cses_cli.models import Problem, TestCase


def _default_db_path() -> Path:
    """Resolve the default database path."""
    # Try relative to package source (development mode)
    pkg_dir = Path(__file__).resolve().parent
    candidates = [
        pkg_dir.parent.parent / "data" / "cses.db",  # src layout: src/cses_cli/../../data/
        pkg_dir.parent / "data" / "cses.db",          # flat layout
        Path.cwd() / "data" / "cses.db",              # current directory
    ]
    for p in candidates:
        if p.exists():
            return p
    # Default to the first candidate (will be created on init)
    return candidates[0]


DB_PATH = _default_db_path()

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS problems (
    task_id    INTEGER PRIMARY KEY,
    title      TEXT NOT NULL,
    category   TEXT NOT NULL,
    url        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_cases (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES problems(task_id),
    case_num   INTEGER NOT NULL,
    input      TEXT NOT NULL,
    expected   TEXT NOT NULL,
    is_edge    BOOLEAN DEFAULT 0,
    UNIQUE(task_id, case_num)
);

CREATE INDEX IF NOT EXISTS idx_test_cases_task ON test_cases(task_id);
"""


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open a connection to the CSES database."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Create tables if they don't exist."""
    conn = get_connection(db_path)
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    conn.close()


def get_problem(task_id: int, db_path: Optional[Path] = None) -> Optional[Problem]:
    """Fetch a problem by its CSES task ID."""
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT task_id, title, category, url FROM problems WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return Problem(
        task_id=row["task_id"],
        title=row["title"],
        category=row["category"],
        url=row["url"],
    )


def get_test_cases(task_id: int, db_path: Optional[Path] = None) -> list[TestCase]:
    """Fetch all test cases for a given problem, ordered by case number."""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT id, task_id, case_num, input, expected, is_edge "
        "FROM test_cases WHERE task_id = ? ORDER BY case_num",
        (task_id,),
    ).fetchall()
    conn.close()
    return [
        TestCase(
            id=r["id"],
            task_id=r["task_id"],
            case_num=r["case_num"],
            input=r["input"],
            expected=r["expected"],
            is_edge=bool(r["is_edge"]),
        )
        for r in rows
    ]


def get_categories(db_path: Optional[Path] = None) -> list[str]:
    """Get all distinct categories."""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT DISTINCT category FROM problems ORDER BY category"
    ).fetchall()
    conn.close()
    return [r["category"] for r in rows]


def get_problems_by_category(
    category: str, db_path: Optional[Path] = None
) -> list[Problem]:
    """Fetch all problems in a category."""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT task_id, title, category, url FROM problems WHERE category = ? ORDER BY task_id",
        (category,),
    ).fetchall()
    conn.close()
    return [
        Problem(
            task_id=r["task_id"],
            title=r["title"],
            category=r["category"],
            url=r["url"],
        )
        for r in rows
    ]


def insert_problem(problem: Problem, db_path: Optional[Path] = None) -> None:
    """Insert or replace a problem."""
    conn = get_connection(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO problems (task_id, title, category, url) VALUES (?, ?, ?, ?)",
        (problem.task_id, problem.title, problem.category, problem.url),
    )
    conn.commit()
    conn.close()


def insert_test_case(test_case: TestCase, db_path: Optional[Path] = None) -> None:
    """Insert or replace a test case."""
    conn = get_connection(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO test_cases (task_id, case_num, input, expected, is_edge) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            test_case.task_id,
            test_case.case_num,
            test_case.input,
            test_case.expected,
            int(test_case.is_edge),
        ),
    )
    conn.commit()
    conn.close()
