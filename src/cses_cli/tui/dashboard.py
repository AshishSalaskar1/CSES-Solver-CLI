"""Full-screen Textual TUI dashboard for `cses invoke` — lazygit-style."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)
from textual import on, work

from cses_cli import db
from cses_cli.models import Problem

# Canonical display order --------------------------------------------------

CATEGORY_ORDER: list[str] = [
    "Introductory Problems",
    "Sorting and Searching",
    "Dynamic Programming",
    "Graph Algorithms",
    "Range Queries",
    "Tree Algorithms",
    "Advanced Techniques",
    "Sliding Window Problems",
    "Interactive Problems",
    "Bitwise Operations",
    "Advanced Graph Problems",
    "Counting Problems",
]

# Short labels for the narrow left panel -----------------------------------

_SHORT: dict[str, str] = {
    "Introductory Problems": "Introductory",
    "Sorting and Searching": "Sorting",
    "Dynamic Programming": "DP",
    "Graph Algorithms": "Graph",
    "Range Queries": "Range",
    "Tree Algorithms": "Tree",
    "Advanced Techniques": "Advanced",
    "Sliding Window Problems": "Sliding Window",
    "Interactive Problems": "Interactive",
    "Bitwise Operations": "Bitwise",
    "Advanced Graph Problems": "Adv. Graph",
    "Counting Problems": "Counting",
}


# ── Helpers ───────────────────────────────────────────────────────────────


def _load_categories() -> list[tuple[str, list[Problem]]]:
    """Return [(category, [Problem, …]), …] in CATEGORY_ORDER."""
    all_cats: set[str] = set(db.get_categories())
    ordered: list[str] = [c for c in CATEGORY_ORDER if c in all_cats]
    # Append any categories present in DB but missing from the hardcoded list.
    ordered += sorted(all_cats - set(ordered))

    result: list[tuple[str, list[Problem]]] = []
    for cat in ordered:
        problems = db.get_problems_by_category(cat)
        result.append((cat, problems))
    return result


# ── Custom widgets ────────────────────────────────────────────────────────


class CategoryItem(ListItem):
    """A single row in the category panel."""

    def __init__(self, category: str, count: int) -> None:
        super().__init__()
        self.category = category
        self.count = count

    def compose(self) -> ComposeResult:
        short = _SHORT.get(self.category, self.category)
        yield Label(f"{short} ({self.count})", classes="cat-label")


class ProblemItem(ListItem):
    """A single row in the problem panel."""

    def __init__(self, problem: Problem) -> None:
        super().__init__()
        self.problem = problem

    def compose(self) -> ComposeResult:
        yield Label(
            f"  #{self.problem.task_id:<6} {self.problem.title}",
            classes="prob-label",
        )


class FilePromptScreen(ModalScreen[str | None]):
    """Modal that asks the user for a solution file path."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    FilePromptScreen {
        align: center middle;
    }
    #prompt-box {
        width: 64;
        height: auto;
        max-height: 9;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
    }
    #prompt-box Label {
        width: 100%;
        margin-bottom: 1;
    }
    #prompt-box Input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-box"):
            yield Label("Path to solution file:")
            yield Input(placeholder="e.g. solution.cpp", id="file-input")

    def on_mount(self) -> None:
        self.query_one("#file-input", Input).focus()

    @on(Input.Submitted, "#file-input")
    def _on_submit(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Main app ──────────────────────────────────────────────────────────────


class DashboardApp(App[tuple[str, ...] | None]):
    """CSES Problem Set dashboard – lazygit-style two-panel TUI."""

    TITLE = "CSES Problem Set"

    CSS = """
    /* ── layout ─────────────────────────────────────────────── */
    #main {
        height: 1fr;
    }

    #cat-panel {
        width: 30;
        min-width: 26;
        border: solid $accent;
        border-title-color: $text;
        height: 100%;
    }

    #prob-panel {
        width: 1fr;
        border: solid $accent;
        border-title-color: $text;
        height: 100%;
    }

    /* ── list views ─────────────────────────────────────────── */
    ListView {
        height: 1fr;
        scrollbar-size: 1 1;
    }

    ListView > ListItem {
        height: 1;
        padding: 0 1;
    }

    ListView:focus > ListItem.--highlight {
        background: $accent;
        color: $text;
    }

    ListView > ListItem.--highlight {
        background: $accent 40%;
    }

    .cat-label, .prob-label {
        width: 100%;
        height: 1;
    }

    /* ── empty state ────────────────────────────────────────── */
    #empty-msg {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "quit", "Quit", show=False),
        Binding("tab", "switch_panel", "Switch panel", show=True),
        Binding("shift+tab", "switch_panel", "Switch panel", show=False),
        Binding("t", "test_problem", "Test", show=True),
        Binding("question_mark", "help", "Help", show=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._data: list[tuple[str, list[Problem]]] = []
        self._active_panel: str = "cat"  # "cat" | "prob"

    # ── compose ───────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            with Vertical(id="cat-panel") as cat:
                cat.border_title = "Categories"
                yield ListView(id="cat-list")
            with Vertical(id="prob-panel") as prob:
                prob.border_title = "Problems"
                yield ListView(id="prob-list")
                yield Static("Select a category", id="empty-msg")
        yield Footer()

    # ── lifecycle ─────────────────────────────────────────────

    def on_mount(self) -> None:
        self._data = _load_categories()
        cat_lv = self.query_one("#cat-list", ListView)
        for category, problems in self._data:
            cat_lv.append(CategoryItem(category, len(problems)))
        cat_lv.focus()

        # Auto-select first category if available.
        if self._data:
            self.set_timer(0.05, self._select_first_category)

    def _select_first_category(self) -> None:
        cat_lv = self.query_one("#cat-list", ListView)
        if cat_lv.index is None and len(cat_lv) > 0:
            cat_lv.index = 0
        self._refresh_problems()

    # ── panel switching ───────────────────────────────────────

    def action_switch_panel(self) -> None:
        if self._active_panel == "cat":
            prob_lv = self.query_one("#prob-list", ListView)
            if len(prob_lv) > 0:
                self._active_panel = "prob"
                prob_lv.focus()
        else:
            self._active_panel = "cat"
            self.query_one("#cat-list", ListView).focus()

    # ── vim-style j/k ─────────────────────────────────────────

    def action_cursor_down(self) -> None:
        lv = self._focused_list()
        if lv is not None and lv.index is not None and lv.index < len(lv) - 1:
            lv.index += 1

    def action_cursor_up(self) -> None:
        lv = self._focused_list()
        if lv is not None and lv.index is not None and lv.index > 0:
            lv.index -= 1

    def _focused_list(self) -> ListView | None:
        focused = self.focused
        if isinstance(focused, ListView):
            return focused
        return None

    # ── category selection ────────────────────────────────────

    @on(ListView.Highlighted, "#cat-list")
    def _on_category_highlighted(self, event: ListView.Highlighted) -> None:
        self._refresh_problems()

    @on(ListView.Selected, "#cat-list")
    def _on_category_selected(self, event: ListView.Selected) -> None:
        self._refresh_problems()
        # Jump focus to problem list if it has items.
        prob_lv = self.query_one("#prob-list", ListView)
        if len(prob_lv) > 0:
            self._active_panel = "prob"
            prob_lv.index = 0
            prob_lv.focus()

    def _refresh_problems(self) -> None:
        cat_lv = self.query_one("#cat-list", ListView)
        prob_lv = self.query_one("#prob-list", ListView)
        empty = self.query_one("#empty-msg", Static)

        idx = cat_lv.index
        if idx is None or idx >= len(self._data):
            prob_lv.clear()
            empty.display = True
            empty.update("Select a category")
            return

        _category, problems = self._data[idx]
        prob_lv.clear()
        if not problems:
            empty.display = True
            empty.update("No problems in this category")
            return

        empty.display = False
        for p in problems:
            prob_lv.append(ProblemItem(p))

        # Update panel border title with count.
        panel = self.query_one("#prob-panel", Vertical)
        panel.border_title = f"Problems ({len(problems)})"

    # ── testing ───────────────────────────────────────────────

    def action_test_problem(self) -> None:
        prob_lv = self.query_one("#prob-list", ListView)
        if prob_lv.index is None or len(prob_lv) == 0:
            self.notify("No problem selected", severity="warning")
            return
        item = prob_lv.children[prob_lv.index]
        if not isinstance(item, ProblemItem):
            return
        self._prompt_for_file(item.problem)

    @work
    async def _prompt_for_file(self, problem: Problem) -> None:
        code_path = await self.push_screen_wait(FilePromptScreen())
        if code_path:
            self.exit(result=("test", str(problem.task_id), code_path))
        else:
            self.notify("Test cancelled", severity="information")

    # ── help ──────────────────────────────────────────────────

    def action_help(self) -> None:
        self.notify(
            "[b]↑/↓ or j/k[/b]  Navigate\n"
            "[b]Enter[/b]       Select category\n"
            "[b]Tab[/b]         Switch panel\n"
            "[b]t[/b]           Test problem\n"
            "[b]q / Esc[/b]     Quit\n"
            "[b]?[/b]           This help",
            title="Keybindings",
            timeout=8,
        )


# Allow standalone testing: python -m cses_cli.tui.dashboard
if __name__ == "__main__":
    app = DashboardApp()
    result = app.run()
    if result and result[0] == "test":
        _, task_id, code_path = result
        print(f"cses test {code_path} {task_id}")
