"""TUI Test Explorer — interactive test result viewer using Textual."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from cses_cli import judge, runner, utils
from cses_cli.models import Problem, RunResult, Verdict


class CaseListItem(ListItem):
    """A single test case entry in the left panel."""

    def __init__(self, result: RunResult, index: int) -> None:
        super().__init__()
        self.result = result
        self.result_index = index

    def compose(self) -> ComposeResult:
        r = self.result
        icon = utils.verdict_icon(r.verdict.value)
        time_str = utils.format_time(r.elapsed_seconds)
        label = f"{icon} Case {r.test_case.case_num}  ({time_str})"
        yield Label(label)


class DetailPanel(Static):
    """Right panel showing details of the selected test case."""

    def update_result(self, result: Optional[RunResult]) -> None:
        if result is None:
            self.update("Select a test case to view details.")
            return

        tc = result.test_case
        lines: list[str] = []

        lines.append(f"[bold]Test Case {tc.case_num}[/bold]")
        if tc.is_edge:
            lines.append("[dim](edge case)[/dim]")
        lines.append("")

        lines.append("[bold cyan]Input:[/bold cyan]")
        input_display = tc.input.strip()
        if len(input_display) > 2000:
            input_display = input_display[:2000] + "\n[dim]... (truncated)[/dim]"
        lines.append(input_display)
        lines.append("")

        lines.append("[bold cyan]Expected Output:[/bold cyan]")
        expected_display = tc.expected.strip()
        if len(expected_display) > 2000:
            expected_display = expected_display[:2000] + "\n[dim]... (truncated)[/dim]"
        lines.append(expected_display)
        lines.append("")

        lines.append("[bold cyan]Your Output:[/bold cyan]")
        actual_display = result.actual_output.strip() if result.actual_output else "[dim](no output)[/dim]"
        if len(actual_display) > 2000:
            actual_display = actual_display[:2000] + "\n[dim]... (truncated)[/dim]"
        lines.append(actual_display)
        lines.append("")

        if result.stderr and result.stderr.strip():
            lines.append("[bold yellow]Debug (stderr):[/bold yellow]")
            stderr_display = result.stderr.strip()
            if len(stderr_display) > 1000:
                stderr_display = stderr_display[:1000] + "\n[dim]... (truncated)[/dim]"
            lines.append(stderr_display)
            lines.append("")

        icon = utils.verdict_icon(result.verdict.value)
        style = utils.verdict_style(result.verdict.value)
        lines.append(f"[bold]Verdict:[/bold] {icon} [{style}]{result.verdict.value}[/{style}]")
        lines.append(f"[dim]Time: {utils.format_time(result.elapsed_seconds)}[/dim]")

        if result.verdict == Verdict.WRONG_ANSWER:
            actual_lines = result.actual_output.strip().splitlines()
            expected_lines = tc.expected.strip().splitlines()
            diff_line = _find_first_diff(actual_lines, expected_lines)
            if diff_line is not None:
                lines.append(f"[dim](output differs at line {diff_line})[/dim]")

        self.update("\n".join(lines))


def _find_first_diff(actual_lines: list[str], expected_lines: list[str]) -> Optional[int]:
    """Find the first line number where actual and expected differ."""
    max_len = max(len(actual_lines), len(expected_lines))
    for i in range(max_len):
        a = actual_lines[i] if i < len(actual_lines) else None
        e = expected_lines[i] if i < len(expected_lines) else None
        if a != e:
            return i + 1
    return None


class TestExplorerApp(App):
    """Interactive TUI for exploring test results."""

    CSS = """
    #main-container {
        height: 1fr;
    }

    #case-list-container {
        width: 30;
        min-width: 25;
        border-right: solid $accent;
    }

    #case-list {
        height: 1fr;
    }

    #detail-container {
        width: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }

    #detail-panel {
        width: 1fr;
    }

    #summary-bar {
        height: 1;
        dock: top;
        padding: 0 1;
        background: $surface;
    }

    ListItem {
        height: 1;
        padding: 0 1;
    }

    ListItem.--highlight {
        background: $accent 30%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("r", "rerun", "Re-run"),
    ]

    def __init__(
        self,
        problem: Problem,
        results: list[RunResult],
        code_path: Path,
        timeout: float = 5.0,
    ) -> None:
        super().__init__()
        self.problem = problem
        self.code_path = code_path
        self.timeout = timeout
        # Sort: failures first, then by case number
        self.results = sorted(
            results,
            key=lambda r: (r.verdict == Verdict.ACCEPTED, r.test_case.case_num),
        )

    def compose(self) -> ComposeResult:
        passed = sum(1 for r in self.results if r.verdict == Verdict.ACCEPTED)
        total = len(self.results)
        failed = total - passed

        if failed == 0:
            summary = f" ✅ {self.problem.title} (#{self.problem.task_id}) — {passed}/{total} passed"
        else:
            summary = f" {self.problem.title} (#{self.problem.task_id}) — {passed}/{total} passed, {failed} failed"

        yield Header()
        yield Label(summary, id="summary-bar")
        with Horizontal(id="main-container"):
            with Vertical(id="case-list-container"):
                yield ListView(
                    *[CaseListItem(r, i) for i, r in enumerate(self.results)],
                    id="case-list",
                )
            with Vertical(id="detail-container"):
                yield DetailPanel(id="detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "CSES Test Explorer"
        self.sub_title = f"Problem #{self.problem.task_id}"
        # Select first item
        list_view = self.query_one("#case-list", ListView)
        if list_view.children:
            list_view.index = 0
            self._update_detail(0)

    @on(ListView.Highlighted, "#case-list")
    def on_case_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is not None and isinstance(event.item, CaseListItem):
            self._update_detail(event.item.result_index)

    def _update_detail(self, index: int) -> None:
        detail = self.query_one("#detail-panel", DetailPanel)
        if 0 <= index < len(self.results):
            detail.update_result(self.results[index])

    def action_rerun(self) -> None:
        """Re-run all test cases."""
        self.sub_title = "Re-running..."
        new_results = []
        for r in self.results:
            new_result = runner.run_solution(self.code_path, r.test_case, timeout=self.timeout)
            new_result = judge.judge(new_result)
            new_results.append(new_result)

        self.results = sorted(
            new_results,
            key=lambda r: (r.verdict == Verdict.ACCEPTED, r.test_case.case_num),
        )

        # Rebuild the list view
        list_view = self.query_one("#case-list", ListView)
        list_view.clear()
        for i, r in enumerate(self.results):
            list_view.append(CaseListItem(r, i))

        passed = sum(1 for r in self.results if r.verdict == Verdict.ACCEPTED)
        total = len(self.results)
        failed = total - passed
        self.sub_title = f"Problem #{self.problem.task_id}"

        summary_label = self.query_one("#summary-bar", Label)
        if failed == 0:
            summary_label.update(f" ✅ {self.problem.title} (#{self.problem.task_id}) — {passed}/{total} passed")
        else:
            summary_label.update(f" {self.problem.title} (#{self.problem.task_id}) — {passed}/{total} passed, {failed} failed")

        if list_view.children:
            list_view.index = 0
            self._update_detail(0)
