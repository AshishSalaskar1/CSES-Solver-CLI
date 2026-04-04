# TUI & CLI Framework Research for Competitive Programming Test Runner

**Date**: 2026-04-04
**Status**: Complete

## Research Questions

1. Which Python TUI framework best supports a lazygit-style split-panel interface?
2. Which CLI framework pairs best with the chosen TUI framework?
3. Can Textual + Typer work together for dual CLI/TUI modes?
4. What are the dependency footprints and installation sizes?
5. Are there competitive-programming-specific TUI tools to learn from?

## Requirements Recap

- Full-screen TUI: split panels, color-coded pass/fail, keyboard navigation, stats
- Simple CLI: `run` and `test` commands with formatted output
- Python-based, pip-installable, minimal dependencies
- Cross-platform (Linux primary, macOS secondary)
- Active maintenance, good docs

---

## TUI Frameworks

### Textual (Textualize)

- **GitHub**: 35.2k stars, 1.2k forks, 190 contributors
- **Latest release**: v8.2.2 (Apr 3, 2026) — 217 total releases
- **Python support**: 3.9+
- **License**: MIT
- **Platform**: Linux, macOS, Windows
- **Install**: `pip install textual` (optional `textual-dev` for devtools)
- **Dependencies**: Rich (its sister project), plus a few lightweight deps

**Feature assessment for our use case**:

- **Split panels**: Native support via `Horizontal`, `Vertical`, `HorizontalScroll`, `VerticalScroll` containers. CSS-like layout system with `dock`, `grid`, `fr` units. Trivial to build left-panel/right-panel layouts.
- **Color-coded items**: Full 24-bit color, theming system, rich markup support (`[green]PASS[/green]`). Inherits Rich's formatting.
- **Navigation**: Built-in keyboard binding system (`Binding` class), focus management, Tab/Shift-Tab navigation between widgets.
- **Stats display**: Header/Footer widgets can be docked. Static/Label widgets for status bars.
- **Key widgets**: `ListView`/`ListItem` (test case list), `DataTable` (tabular results), `RichLog` (streaming output), `Static`/`Label` (details display), `ProgressBar`, `Tree`, `TabbedContent`.
- **Testing**: Built-in `Pilot` testing framework for headless TUI testing.
- **Dev tools**: `textual-dev` provides live CSS reloading, dev console from a separate terminal.
- **Async**: Native async support; can run subprocesses without blocking UI.
- **Web serving**: `textual serve` can serve TUI apps in a browser (bonus feature).

**Learning curve**: Moderate. CSS-like styling is familiar to web developers. Compose pattern is intuitive. Excellent documentation with tutorials, how-to guides, and widget gallery.

**Verdict**: Best-in-class for our use case. Purpose-built for exactly this kind of application.

### Rich (Textualize)

- **GitHub**: 56k stars, 2.1k forks, 273 contributors
- **Latest release**: v14.3.3 (Feb 19, 2026) — 175 total releases
- **Python support**: 3.8+
- **License**: MIT
- **Platform**: Linux, macOS, Windows
- **Install**: `pip install rich`
- **Dependencies**: `markdown-it-py`, `pygments` (both lightweight)

**Feature assessment for our use case**:

- **Not a TUI framework** — Rich is a terminal *formatting* library. It renders rich text, tables, panels, trees, progress bars, syntax highlighting, and tracebacks.
- **Panels/Layout**: `Panel`, `Columns`, `Table`, `Layout` for static rendering. No interactive widgets or keyboard handling.
- **Colors**: Full markup system (`[bold green]text[/]`), 24-bit color, themes.
- **CLI output**: Perfect for the "simple CLI mode" — formatted test results, colored pass/fail, progress bars, tables.
- **Console protocol**: Extensible renderables for custom output.

**Relationship to Textual**: Rich is Textual's underlying rendering engine. Textual depends on Rich. Using both together is natural and expected.

**Verdict**: Essential for CLI mode output formatting. Comes free with Textual. Not sufficient alone for TUI mode.

### urwid

- **GitHub**: 3k stars, 331 forks, 137 contributors
- **Latest release**: v4.0.0 (Apr 2026) — 41 total releases
- **Python support**: 3.9+ and PyPy
- **License**: LGPL-2.1
- **Platform**: Linux, macOS, Cygwin; **limited Windows support** (Windows 10+ only, no Terminal widget, no non-socket file descriptors)
- **Install**: `pip install urwid`
- **Dependencies**: Minimal (pure Python core, optional extras for ZMQ/serial)

**Feature assessment for our use case**:

- **Split panels**: Possible via `Columns`, `Pile`, `Frame` widgets. More manual layout than Textual.
- **Widget library**: Edit boxes, buttons, checkboxes, radio buttons, list boxes, scrollable containers.
- **Event loops**: Supports Twisted, Glib, Tornado, asyncio, trio, ZeroMQ, or select-based.
- **Colors**: 24-bit (true color), 256-color, 88-color support.
- **API style**: Traditional widget-tree approach. More verbose than Textual. Callback-based.

**Learning curve**: Steep. Older API design, less intuitive than Textual. Documentation exists but is less polished.

**Verdict**: Capable but dated. LGPL-2.1 license is more restrictive. Significantly less developer-friendly than Textual. Limited Windows support.

### npyscreen

- **GitHub**: 502 stars, 111 forks, 6 contributors
- **Latest release**: v5.0.2 (Dec 2025) — 2 releases (first in 10 years)
- **Python support**: 3.x (dropped Python 2 in v5.0)
- **License**: Custom (view on GitHub)
- **Platform**: Unix-like only (ncurses dependency)
- **Install**: `pip install npyscreen`
- **Dependencies**: ncurses (stdlib on Unix)

**Feature assessment for our use case**:

- Built on top of ncurses (stdlib). Widget library includes text fields, buttons, checkboxes, trees, grids.
- **Effectively unmaintained**: 10-year gap between v4.x and v5.0. Only 6 contributors.
- No Windows support. No modern terminal features (no 24-bit color).
- v5.0 was mainly to fix Python 3.14 compatibility.

**Verdict**: Not recommended. Unmaintained, minimal community, no Windows support.

### prompt_toolkit

- **GitHub**: 10.4k stars, 773 forks, 222 contributors
- **Latest release**: v3.0.52 (Aug 2025) — 10 releases
- **Python support**: 3.10+ (recently updated)
- **License**: BSD-3-Clause
- **Platform**: Linux, macOS, Windows
- **Install**: `pip install prompt_toolkit`
- **Dependencies**: Pygments, wcwidth

**Feature assessment for our use case**:

- **Primary purpose**: Building interactive command-line prompts and REPLs (like `ptpython`, `ipython`).
- Syntax highlighting, multi-line editing, advanced completion, Vi/Emacs key bindings.
- **Full-screen apps**: Possible but not its primary strength. Has a `Layout` system with `HSplit`, `VSplit`, `Window`, `BufferControl`.
- **Not a widget toolkit**: No pre-built list views, data tables, or scrollable panels like Textual.
- Used by many projects: `ipython`, `pgcli`, `mycli`, `aws-shell`.

**Learning curve**: Moderate for prompts, steep for full-screen apps.

**Verdict**: Overkill for prompts (we don't need REPL features), underpowered for full TUI. Wrong tool for this job.

### blessed/blessings

- **GitHub**: 1.4k stars, 81 forks (blessed is a maintained fork of blessings)
- **Latest release**: v1.38 (Apr 2026) — 57 releases
- **Python support**: 3.7+
- **License**: MIT
- **Platform**: Linux, macOS, Windows (since Dec 2019)
- **Install**: `pip install blessed`
- **Dependencies**: wcwidth, jinxed (Windows only)

**Feature assessment for our use case**:

- **Low-level terminal library**: Provides `Terminal` object for colors, positioning, keyboard input, screen control.
- No widget system. No layout engine. You draw everything manually with cursor positioning.
- Excellent for simple formatting, terminal detection, key handling.
- Good foundation for building a TUI from scratch, but we'd be reimplementing what Textual provides.

**Verdict**: Too low-level. We'd spend most of our time building infrastructure that Textual provides out of the box.

### curses (stdlib)

- **Included with Python** (no install needed)
- **Platform**: Unix/Linux/macOS only. Windows requires `windows-curses` package.
- **License**: PSF (stdlib)

**Feature assessment for our use case**:

- Raw terminal control: windows, pads, character-level drawing.
- No widget system. Extremely verbose for anything beyond simple text.
- Maximum control but maximum effort.
- Unicode/color support varies by terminal.

**Verdict**: Not recommended unless zero-dependency is an absolute hard constraint. Learning curve is the steepest of all options.

---

## CLI Frameworks

### Click

- **GitHub**: 17.4k stars, 1.6k forks, 389 contributors
- **Latest release**: v8.3.2 (Apr 2026) — 25 releases
- **Python support**: 3.8+
- **License**: BSD-3-Clause
- **Install**: `pip install click`
- **Dependencies**: None (pure Python)

**Features**: Composable commands, automatic help generation, parameter types, file handling, environment variable support, lazy loading of subcommands, testing via `CliRunner`. The de facto standard for Python CLIs.

**Verdict**: Excellent, battle-tested. Foundation of Typer. Use directly if you prefer decorator-based API.

### Typer

- **GitHub**: 19.1k stars, 868 forks, 110 contributors
- **Latest release**: v0.24.1 (Feb 21, 2026) — 70 releases
- **Python support**: 3.10+ (dropped 3.9 recently)
- **License**: MIT
- **Install**: `pip install typer`
- **Dependencies**: Click, Rich, shellingham

**Features**: Type-hint-based CLI building on top of Click. Automatic `--help`, auto-completion for all shells (Bash, Zsh, Fish, PowerShell). Sub-commands via `app = typer.Typer()` + `@app.command()`. Rich-formatted error messages by default.

**Key advantage for our use case**: Typer already depends on Rich, and Rich is required by Textual. This means Typer + Textual share the Rich dependency — no extra bloat.

**Verdict**: Best choice for our CLI layer. Modern, type-safe, excellent DX, and naturally pairs with Textual/Rich.

### argparse

- **Included with Python** (stdlib)
- **License**: PSF

**Features**: Verbose but universal. No external dependencies. Manual help formatting. No auto-completion without third-party packages.

**Verdict**: Viable but significantly more boilerplate than Typer. No Rich integration by default.

### Fire (Google)

- **GitHub**: 28.2k stars, 1.5k forks, 67 contributors
- **Latest release**: v0.7.1 (Aug 2025) — 12 releases
- **Python support**: 3.7+
- **License**: Apache 2.0
- **Install**: `pip install fire`
- **Dependencies**: termcolor

**Features**: Auto-generates CLIs from any Python object (function, class, module, dict). Minimal code. Includes REPL mode, trace mode.

**Verdict**: Too magical for a structured CLI with specific subcommands and options. Less control over help text and parameter validation. Not a good fit.

---

## Integration Research

### Textual + Typer Compatibility

**Yes, they work together seamlessly.** The integration pattern is straightforward:

```python
import typer
from my_app.tui import TestRunnerApp  # Textual app

app = typer.Typer()

@app.command()
def test(problem: str, tui: bool = False):
    """Run tests for a problem."""
    if tui:
        # Launch full-screen TUI
        tui_app = TestRunnerApp(problem=problem)
        tui_app.run()
    else:
        # Simple CLI output using Rich
        run_tests_cli(problem)

@app.command()
def run(problem: str, test_case: int = 1):
    """Run a single test case."""
    run_single_test(problem, test_case)
```

**Why they pair well**:

1. **Shared dependency**: Typer depends on Rich. Textual depends on Rich. No duplicate dependencies.
2. **Complementary roles**: Typer handles CLI routing, argument parsing, help text, auto-completion. Textual handles the full-screen interactive mode.
3. **Same ecosystem**: Both maintained by active Python community members with strong Textualize connections.
4. **CLI output**: When not in TUI mode, `rich.console.Console` provides beautiful formatted output consistent with Typer's error formatting.

**Dependency chain**: `typer` → `click` + `rich` + `shellingham`. `textual` → `rich`. Total unique deps: `click`, `rich`, `shellingham`, `textual` (+ Rich's deps: `markdown-it-py`, `pygments`).

### lazygit-Style TUI in Python

A lazygit-style interface has these characteristics:

1. **Split panels**: Left panel (list), right panel (details/diff)
2. **Keyboard-driven**: j/k navigation, Enter to select, Tab to switch panels
3. **Color-coded status**: Green/red indicators
4. **Status bar**: Summary statistics at bottom
5. **No mouse required**: Full keyboard navigation

**Textual is the best framework for this pattern.** Here's why:

- `Horizontal` container splits screen into left/right panels
- `ListView` + `ListItem` for the test case list with color-coded labels
- `RichLog` or `Static` for the detail panel (showing input, expected output, actual output, diff)
- `Header` docked at top for problem title
- `Footer` docked at bottom for key bindings + stats (x/y passed)
- CSS `dock`, `width`, `height` control exact panel sizing
- `Binding` class for custom key bindings (j/k, Enter, Tab, q)
- Reactive properties for auto-updating stats

**Sketch of layout for our test runner**:

```
┌─────────────────────────────────────────────────┐
│ Header: Problem Name - 3/5 Passed                │
├──────────────┬──────────────────────────────────┤
│ Test Cases   │ Test Case #2 - FAIL              │
│              │                                   │
│ ✓ Test 1     │ Input:                            │
│ ✗ Test 2  ←  │ 5                                 │
│ ✓ Test 3     │ 1 2 3 4 5                         │
│ ✓ Test 4     │                                   │
│ ✗ Test 5     │ Expected Output:                  │
│              │ 15                                │
│              │                                   │
│              │ Actual Output:                    │
│              │ 10                                │
│              │                                   │
│              │ Time: 0.023s | Memory: 5.2 MB     │
├──────────────┴──────────────────────────────────┤
│ Footer: [j/k] Navigate [Enter] Re-run [q] Quit  │
└─────────────────────────────────────────────────┘
```

No other Python TUI framework can produce this layout as easily or with as polished a result as Textual.

### Competitive Programming TUI Tools

**Existing tools researched**:

1. **online-judge-tools (oj)** — 1.1k stars, Python, CLI-only
   - Downloads sample cases, tests code, submits to online judges (Codeforces, AtCoder, HackerRank, etc.)
   - Commands: `oj download`, `oj test -c "python3 main.py"`, `oj submit`
   - Output: Plain text with color codes (AC green, WA red), timing, memory
   - **No TUI mode** — purely sequential CLI output
   - Last release: v12.0.0 (May 2024) — appears lightly maintained
   - Uses argparse for CLI

2. **cf-tool (xalanq)** — Codeforces-specific, written in Go
   - Not Python-based
   - CLI-only with colored output

3. **competitive-companion (jmerle)** — Browser extension
   - Parses problem pages and sends test cases to local tools
   - Not a test runner

4. **atcoder-tools (kyuridenamida)** — AtCoder-specific
   - Python-based, CLI-only

5. **rujaion (fukatani)** — IDE for competitive programming with Rust
   - Not Python, not a TUI

**Key insight**: No existing competitive programming tool provides a TUI test runner. This is a gap in the ecosystem. The `oj` tool's CLI output format is a good reference for what information to display (verdict, timing, memory, input/expected/actual diff), but the interactive TUI approach would be novel.

---

## Comparison Matrix

### TUI Frameworks

| Framework | Stars | Last Release | Python | Split Panels | Widgets | Colors | KB Nav | Docs | License | Windows |
|-----------|-------|-------------|--------|-------------|---------|--------|--------|------|---------|---------|
| **Textual** | 35.2k | Apr 2026 | 3.9+ | Native (CSS) | 30+ built-in | 24-bit + themes | Native bindings | Excellent | MIT | Yes |
| Rich | 56k | Feb 2026 | 3.8+ | Static only | Renderables | 24-bit + markup | None | Excellent | MIT | Yes |
| urwid | 3k | Apr 2026 | 3.9+ | Manual (Columns) | 15+ basic | 24-bit | Callback-based | OK | LGPL-2.1 | Limited |
| npyscreen | 502 | Dec 2025 | 3.x | Manual | Basic set | 16-color | Form-based | Minimal | Custom | No |
| prompt_toolkit | 10.4k | Aug 2025 | 3.10+ | HSplit/VSplit | Minimal | ANSI | Yes | Good | BSD-3 | Yes |
| blessed | 1.4k | Apr 2026 | 3.7+ | Manual (draw) | None | 24-bit | Manual | Good | MIT | Yes |
| curses | stdlib | — | 3.x | Manual (draw) | None | Varies | Manual | stdlib docs | PSF | No* |

### CLI Frameworks

| Framework | Stars | Last Release | Python | Type Hints | Auto-complete | Rich Output | Subcommands | License |
|-----------|-------|-------------|--------|-----------|--------------|-------------|-------------|---------|
| **Typer** | 19.1k | Feb 2026 | 3.10+ | Native | All shells | Built-in (Rich) | Yes | MIT |
| Click | 17.4k | Apr 2026 | 3.8+ | No | Via plugins | No (manual) | Yes | BSD-3 |
| Fire | 28.2k | Aug 2025 | 3.7+ | No | Basic | No | Implicit | Apache 2.0 |
| argparse | stdlib | — | 3.x | No | No | No | Yes (manual) | PSF |

---

## Recommendations

### Primary Recommendation: Textual + Typer + Rich

**TUI Framework**: Textual (v8.2.2)
**CLI Framework**: Typer (v0.24.1)
**Output Formatting**: Rich (v14.3.3) — shared dependency, comes free

**Rationale**:

1. **Best feature match**: Textual provides every widget and layout primitive needed for the lazygit-style TUI (ListView, containers, key bindings, themes, docking).
2. **Minimal dependency overhead**: Typer already requires Rich. Textual requires Rich. The only additional packages beyond the Typer baseline are Textual itself and Click (which Typer already provides).
3. **Active maintenance**: All three projects had releases within the last 2 months. Textual has 217 releases and commits from yesterday.
4. **Excellent documentation**: Textual has comprehensive docs with widget gallery, layout how-tos, tutorials, and API reference.
5. **Cross-platform**: All three support Linux, macOS, and Windows.
6. **Testing**: Textual's `Pilot` framework enables headless TUI testing. Typer's `CliRunner` (from Click) enables CLI testing.
7. **Future-proof**: Textualize (the company behind Textual and Rich) is actively developing the ecosystem. Web serving capability is a bonus.

**Effective install**: `pip install textual typer`
This pulls in: textual, typer, click, rich, shellingham, markdown-it-py, pygments, mdurl, wcwidth — all lightweight pure-Python packages.

### Architecture Pattern

```
cses-cli/
├── cli.py          # Typer app: `test`, `run`, `submit` commands
├── tui/
│   ├── app.py      # Textual App subclass
│   ├── widgets.py  # Custom widgets (TestCaseList, TestDetail)
│   └── styles.css  # Textual CSS for layout
├── runner.py       # Test execution logic (shared by CLI and TUI)
└── models.py       # TestCase, TestResult data classes
```

- `cses test problem_name` → Rich-formatted CLI output
- `cses test problem_name --tui` or `cses tui problem_name` → Full-screen Textual app
- Shared `runner.py` ensures identical test execution logic in both modes.

### Alternative Recommendation (Minimal Dependencies)

If absolute minimal dependencies are required:

- **TUI**: Rich `Layout` + `Live` display (not truly interactive, but can render panels)
- **CLI**: Click (no Rich auto-integration, but zero-dep CLI)

This sacrifices the interactive TUI for a "live-updating dashboard" style. Not recommended unless dependency count is a hard constraint.

---

## Gaps and Follow-On Questions

### Answered through research
- Textual + Typer integration: confirmed compatible, shared Rich dependency
- lazygit-style TUI: Textual is the clear best choice
- Competitive programming TUI tools: none exist (opportunity for novelty)

### Gaps requiring further investigation
- **Exact installed size**: pip download sizes were not checked quantitatively. Estimate: ~5-10 MB total for textual + typer + all transitive deps.
- **Startup time**: Textual apps may have noticeable startup latency on first import. Should benchmark with a minimal app.
- **Subprocess integration in Textual**: Need to verify the best pattern for running compilation + execution as a subprocess inside a Textual `Worker` without blocking the UI.
- **Inline mode**: Textual supports "inline mode" (TUI within terminal output rather than full-screen). This could be useful for a semi-interactive mode between pure CLI and full TUI.

### Clarifying questions for user
- Is Windows support a hard requirement, or nice-to-have?
- Is there a constraint on the minimum Python version (3.9 vs 3.10+)?
- Should the TUI support mouse interaction, or keyboard-only?
