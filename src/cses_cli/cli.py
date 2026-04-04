"""Typer CLI entry point for CSES CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cses_cli import db, judge, runner, utils
from cses_cli.models import Verdict

app = typer.Typer(
    name="cses",
    help="Run Python solutions against CSES problem test cases offline.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def run(
    code_path: Path = typer.Argument(..., help="Path to your Python solution file"),
    problem_id: int = typer.Argument(..., help="CSES problem/task ID (e.g. 1068)"),
    timeout: float = typer.Option(5.0, "--timeout", "-t", help="Timeout per test case in seconds"),
) -> None:
    """Quick-run: execute against the first test case and show the result."""
    _validate_code_path(code_path)

    problem = db.get_problem(problem_id)
    if problem is None:
        console.print(f"[red]Error:[/red] Problem #{problem_id} not found in database.")
        raise typer.Exit(1)

    test_cases = db.get_test_cases(problem_id)
    if not test_cases:
        console.print(f"[red]Error:[/red] No test cases found for problem #{problem_id}.")
        raise typer.Exit(1)

    tc = test_cases[0]
    console.print()
    console.print(f"  [bold]Problem:[/bold] {problem.title} (#{problem.task_id})")
    console.print()

    result = runner.run_solution(code_path, tc, timeout=timeout)
    result = judge.judge(result)

    icon = utils.verdict_icon(result.verdict.value)
    style = utils.verdict_style(result.verdict.value)
    console.print(f"  Test Case {tc.case_num}: {icon} [{style}]{result.verdict.value}[/{style}] ({utils.format_time(result.elapsed_seconds)})")
    console.print()

    console.print(f"  [dim]Input:[/dim]    {_truncate(tc.input)}")
    console.print(f"  [dim]Expected:[/dim] {_truncate(tc.expected)}")
    console.print(f"  [dim]Output:[/dim]   {_truncate(result.actual_output)}")

    if result.stderr.strip():
        console.print(f"  [dim]Debug:[/dim]    {_truncate(result.stderr)}")
    console.print()

    console.print(f"  [dim]Press Esc to run all test cases, or Enter to quit[/dim]")

    import sys as _sys, tty, termios
    fd = _sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = _sys.stdin.read(1)
            if ch == '\r' or ch == '\n':
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                console.print()
                return
            if ch == '\x1b':
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                break
            if ch == '\x03':
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                console.print()
                return
    except (KeyboardInterrupt, EOFError):
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return

    # Run all test cases and launch TUI
    console.print(f"\n  [dim]Running all {len(test_cases)} test cases...[/dim]")
    all_results = []
    for tc_item in test_cases:
        r = runner.run_solution(code_path, tc_item, timeout=timeout)
        r = judge.judge(r)
        all_results.append(r)

    passed = sum(1 for r in all_results if r.verdict == Verdict.ACCEPTED)
    failed = len(all_results) - passed
    total_time = sum(r.elapsed_seconds for r in all_results)
    summary_style = "green" if failed == 0 else "red"
    summary_text = f"{passed}/{len(all_results)} passed ✅" if failed == 0 else f"{passed}/{len(all_results)} passed ✅  |  {failed} failed ❌"
    console.print(f"  Results: [{summary_style}]{summary_text}[/{summary_style}]  |  {utils.format_time(total_time)} total\n")

    from cses_cli.tui.test_explorer import TestExplorerApp
    tui_app = TestExplorerApp(problem=problem, results=all_results, code_path=code_path, timeout=timeout)
    tui_app.run()


@app.command()
def invoke() -> None:
    """Launch the full-screen dashboard TUI (lazygit-style)."""
    from cses_cli.tui.dashboard import DashboardApp

    dashboard = DashboardApp()
    result = dashboard.run()

    if result and isinstance(result, tuple) and result[0] == "test":
        _, task_id, code_path = result
        console.print(f"\n  Running: cses test {code_path} {task_id}\n")
        import subprocess as sp
        sp.run(["cses", "test", str(code_path), str(task_id)])


@app.command()
def test(
    code_path: Path = typer.Argument(..., help="Path to your Python solution file"),
    problem_id: int = typer.Argument(..., help="CSES problem/task ID (e.g. 1068)"),
    timeout: float = typer.Option(5.0, "--timeout", "-t", help="Timeout per test case in seconds"),
    no_tui: bool = typer.Option(False, "--no-tui", help="Skip TUI explorer, just print summary"),
) -> None:
    """Full test: run against ALL test cases, then explore results interactively."""
    _validate_code_path(code_path)

    problem = db.get_problem(problem_id)
    if problem is None:
        console.print(f"[red]Error:[/red] Problem #{problem_id} not found in database.")
        raise typer.Exit(1)

    test_cases = db.get_test_cases(problem_id)
    if not test_cases:
        console.print(f"[red]Error:[/red] No test cases found for problem #{problem_id}.")
        raise typer.Exit(1)

    console.print()
    console.print(f"  [bold]Problem:[/bold] {problem.title} (#{problem.task_id})")
    console.print(f"  [dim]Running {len(test_cases)} test cases...[/dim]")
    console.print()

    results = []
    for tc in test_cases:
        result = runner.run_solution(code_path, tc, timeout=timeout)
        result = judge.judge(result)
        results.append(result)

    passed = sum(1 for r in results if r.verdict == Verdict.ACCEPTED)
    failed = len(results) - passed
    total_time = sum(r.elapsed_seconds for r in results)

    if failed == 0:
        summary_style = "green"
        summary_text = f"{passed}/{len(results)} passed ✅"
    else:
        summary_style = "red"
        summary_text = f"{passed}/{len(results)} passed ✅  |  {failed} failed ❌"

    console.print(f"  Results: [{summary_style}]{summary_text}[/{summary_style}]  |  {utils.format_time(total_time)} total")
    console.print()

    if no_tui:
        _print_results_table(results)
        return

    if failed > 0:
        console.print("  [dim]Press Esc to explore results, or Enter to quit[/dim]")
    else:
        console.print("  [dim]All tests passed! Press Esc to explore details, or Enter to quit[/dim]")

    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':  # Enter → quit
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                console.print()
                return
            if ch == '\x1b':  # Esc → open TUI
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                break
            if ch == '\x03':  # Ctrl+C
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                console.print()
                return
    except (KeyboardInterrupt, EOFError):
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return

    from cses_cli.tui.test_explorer import TestExplorerApp

    tui_app = TestExplorerApp(problem=problem, results=results, code_path=code_path, timeout=timeout)
    tui_app.run()


@app.command()
def seed() -> None:
    """Seed/reset the database with all 258 problems and sample test cases."""
    from cses_cli.seed import seed as do_seed
    do_seed()


@app.command()
def generate(
    category: str = typer.Option(None, "--category", "-c", help="Generate for a specific category only"),
    num_cases: int = typer.Option(20, "--cases", "-n", help="Number of test cases per problem"),
) -> None:
    """Generate test cases using reference solutions."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from generators.generate_all import generate_all

    categories = [category] if category else None
    console.print("[bold]Generating test cases...[/bold]")
    results = generate_all(categories=categories, num_cases=num_cases)
    total = sum(results.values())
    console.print(f"\n[green]Done![/green] Generated {total} test cases across {len(results)} categories.")


@app.command()
def info(
    problem_id: int = typer.Argument(..., help="CSES problem/task ID"),
) -> None:
    """Show information about a problem."""
    problem = db.get_problem(problem_id)
    if problem is None:
        console.print(f"[red]Error:[/red] Problem #{problem_id} not found in database.")
        raise typer.Exit(1)

    test_cases = db.get_test_cases(problem_id)
    console.print()
    console.print(f"  [bold]{problem.title}[/bold] (#{problem.task_id})")
    console.print(f"  [dim]Category:[/dim] {problem.category}")
    console.print(f"  [dim]URL:[/dim]      {problem.url}")
    console.print(f"  [dim]Test cases:[/dim] {len(test_cases)}")
    console.print()


@app.command(name="list")
def list_problems(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
) -> None:
    """List all available problems."""
    from cses_cli.problems_data import CATEGORY_ORDER

    if category:
        problems = db.get_problems_by_category(category)
        if not problems:
            console.print(f"[red]Error:[/red] No problems found for category '{category}'.")
            raise typer.Exit(1)
        table = Table(title=category, show_header=True, header_style="bold")
        table.add_column("ID", justify="right", width=6)
        table.add_column("Title", width=40)
        table.add_column("Tests", justify="right", width=6)
        for p in problems:
            tc_count = len(db.get_test_cases(p.task_id))
            tests_str = str(tc_count) if tc_count > 0 else "[dim]—[/dim]"
            table.add_row(str(p.task_id), p.title, tests_str)
        console.print(table)
    else:
        for cat in CATEGORY_ORDER:
            problems = db.get_problems_by_category(cat)
            if not problems:
                continue
            with_tests = sum(1 for p in problems if len(db.get_test_cases(p.task_id)) > 0)
            console.print(f"  [bold]{cat}[/bold] — {len(problems)} problems ({with_tests} with test cases)")
        console.print()


def _validate_code_path(code_path: Path) -> None:
    """Validate that the code file exists and is a Python file."""
    if not code_path.exists():
        console.print(f"[red]Error:[/red] File not found: {code_path}")
        raise typer.Exit(1)
    if code_path.suffix != ".py":
        console.print(f"[yellow]Warning:[/yellow] {code_path} doesn't have a .py extension.")


def _truncate(text: str, max_len: int = 80) -> str:
    """Truncate text for single-line display."""
    text = text.strip().replace("\n", " ↵ ")
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _print_results_table(results: list) -> None:
    """Print a simple results table (no-TUI mode)."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Case", justify="right", width=6)
    table.add_column("Verdict", width=20)
    table.add_column("Time", justify="right", width=8)

    sorted_results = sorted(results, key=lambda r: (r.verdict == Verdict.ACCEPTED, r.test_case.case_num))
    for r in sorted_results:
        icon = utils.verdict_icon(r.verdict.value)
        style = utils.verdict_style(r.verdict.value)
        table.add_row(
            str(r.test_case.case_num),
            f"[{style}]{icon} {r.verdict.value}[/{style}]",
            utils.format_time(r.elapsed_seconds),
        )

    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
