<!-- markdownlint-disable-file -->
# Task Research: CSES CLI Tool

A local CLI/TUI tool for running Python solutions against CSES problem set test cases, with interactive result exploration and comprehensive test coverage.

## Task Implementation Requests

* Build a CLI/TUI tool that runs Python code files against CSES problem test cases locally
* Support commands: `invoke` (full-screen TUI), `run` (quick execution), `test` (full test suite with interactive explorer)
* Store test cases locally in a size-efficient format suitable for git
* Generate comprehensive but compact test cases for ~258 CSES problems (excluding Mathematics, String Algorithms, Geometry, Construction Problems, Additional Problems I & II)
* Handle CSES-style stdin/stdout simulation for Python solutions
* Show interactive test results with pass/fail stats, color-coded case navigation, and input/output comparison panels

## Scope and Success Criteria

* Scope: Technical feasibility research covering TUI framework selection, test case storage, input simulation, CLI architecture, and test case generation. Python-only support initially with future language extensibility.
* Assumptions:
  1. User writes Python solutions with a `main()` function that reads `input()` and uses `print()` (standard CP style)
  2. CSES test cases are NOT publicly available; must be generated
  3. Dataset must be git-friendly (~5 MB packed)
  4. 12 categories in scope (258 problems), 6 categories excluded (142 problems)
  5. No stress-test-level large inputs needed; focus on correctness coverage
  6. Interactive problems (6) may be deferred from initial scope
* Success Criteria:
  1. Identified optimal TUI framework for interactive terminal UI
  2. Determined test case storage format with size estimates
  3. Designed input simulation approach for Python solutions
  4. Estimated test case count and total dataset size
  5. Produced architecture recommendation with CLI command design
  6. Identified test case generation strategy and validation approach

## Outline

1. CSES Problem Set Analysis
2. TUI/CLI Framework Comparison
3. Test Case Storage Format
4. Test Case Generation Strategy
5. Input/Output Simulation Design
6. CLI Architecture and Command Design
7. Technical Scenarios and Alternatives
8. Selected Approach

## Potential Next Research

* Catalog which CSES problems have multiple valid outputs (need checker functions, not exact match)
* Benchmark Textual app startup time with a minimal split-panel prototype
* Survey community CSES solution repos for reference solution sourcing
* Prototype test case generators for 2-3 sample problems to validate the generation workflow
* Define the exact generator template API and directory structure
* Handling of interactive problems (interactor simulation)
* Floating-point output comparison strategy for applicable problems

## Research Executed

### Subagent Research Documents

* .copilot-tracking/research/subagents/2026-04-04/cses-problem-set-research.md
* .copilot-tracking/research/subagents/2026-04-04/tui-framework-research.md
* .copilot-tracking/research/subagents/2026-04-04/storage-and-generation-research.md
* .copilot-tracking/research/subagents/2026-04-04/input-simulation-research.md

### External Research

* CSES Problem Set: https://cses.fi/problemset/
  * 400 total problems across 18 categories
  * 258 in scope across 12 categories
  * URL pattern: `https://cses.fi/problemset/task/{ID}` (IDs are non-sequential, range 1068-3430)
  * All problems use stdin/stdout exclusively
  * Test cases are hidden; only 1 sample example is publicly visible per problem
  * No public API exists
  * Source: CSES website analysis
* Existing CLI tools:
  * `csesfi/cses-cli` (Rust, official) — can download sample I/O only, not hidden test cases
  * `online-judge-tools/oj` (Python, 1.1k stars) — subprocess-based test runner, closest analog to our tool
  * Source: GitHub repository analysis
* TUI framework ecosystem:
  * Textual: 35.2k stars, v8.2.2 (Apr 2026), MIT license
  * Rich: 56k stars, v14.3.3 (Feb 2026), dependency of Textual
  * Typer: 19.1k stars, v0.24.1 (Feb 2026), depends on Rich+Click
  * Source: GitHub/PyPI analysis

### Project Conventions

* No existing codebase — greenfield project
* Target: pip-installable Python package
* Primary platform: Linux (macOS secondary)

## Key Discoveries

### 1. CSES Problem Set Structure

**400 total problems** across 18 categories. After excluding Mathematics (37), String Algorithms (21), Geometry (16), Construction Problems (8), Additional Problems I (30), Additional Problems II (30):

**258 problems in scope across 12 categories:**

| Category                  | Count |
|---------------------------|-------|
| Introductory Problems     | 24    |
| Sorting and Searching     | 35    |
| Dynamic Programming       | 23    |
| Graph Algorithms          | 36    |
| Range Queries             | 25    |
| Tree Algorithms           | 16    |
| Advanced Techniques       | 25    |
| Sliding Window Problems   | 11    |
| Interactive Problems      | 6     |
| Bitwise Operations        | 11    |
| Advanced Graph Problems   | 28    |
| Counting Problems         | 18    |

Problem IDs are non-sequential integers (1068–3430). All use stdin/stdout. Typical constraints: arrays up to 2×10⁵, values up to 10⁹, grids up to 1000×1000. Time limits: 1-2 seconds. Memory limits: 512 MB.

### 2. Test Cases Are NOT Available

CSES test cases are **completely hidden**. No API, no download, no post-solve access to test data. The "hacking" feature only lets you *submit* new test cases, not download existing ones. This means **all test cases must be generated from scratch**.

### 3. TUI Framework Landscape

**Textual** is the only Python framework that natively supports lazygit-style split-panel TUI with `ListView`, CSS-like layout, key bindings, and 30+ built-in widgets. No other framework comes close. Combined with **Typer** (CLI routing) and **Rich** (formatting), they share dependencies and form a natural stack.

### 4. Storage: Flat Files Win for Git

Flat file structure (standard CP judge format: `{problem_id}/{n}.in`, `{n}.out`) provides excellent git behavior with text diffs, reviewable PRs, and efficient delta compression. ~11.5 MB raw content compresses to **~5 MB in git pack files**. SQLite would grow to ~130 MB after 10 updates due to binary file snapshots. After 100 updates: ~15-20 MB for flat files vs ~1.3 GB for SQLite.

### 5. Subprocess Execution Is the Standard

Every major CP testing tool (`oj`, `cf-tool`, `cpbooster`) uses subprocess execution. `subprocess.run([sys.executable, solution.py], input=test_data, capture_output=True, timeout=limit, text=True)` handles stdin feeding, stdout/stderr capture, and TLE enforcement in a single call. All stdout = answer, all stderr = debug output (industry standard).

### 6. Test Case Generation Strategy

~2,580 test cases needed (258 problems × ~10 avg). LLM-assisted generator scripts with reusable templates for common patterns (single-int, array, graph, tree, grid). Reference solutions validate expected outputs against CSES samples. Pre-generate all test cases and ship in the repo (~5 MB is trivially small).

### Complete Examples

#### CLI Usage Flow

```bash
# Quick run (single test case)
cses run solution.py 1068

# Full test suite with stats
cses test solution.py 1068
# → Shows: 8/10 passed, lists failing cases

# Interactive TUI explorer
cses invoke solution.py 1068
# → Full-screen split-panel with case navigation
```

#### TUI Layout

```
┌──────────────────────────────────────────────────────┐
│ CSES 1068: Weird Algorithm                  8/10 ✓   │
├───────────────┬──────────────────────────────────────┤
│ Test Cases    │ Test Case #3 — FAIL                  │
│               │                                      │
│  ✗ #3      ← │ Input:                               │
│  ✗ #7        │ 5                                    │
│  ✓ #1        │                                      │
│  ✓ #2        │ Expected Output:                     │
│  ✓ #4        │ 5 16 8 4 2 1                         │
│  ✓ #5        │                                      │
│  ✓ #6        │ Your Output:                         │
│  ✓ #8        │ 5 16 8 4 2                           │
│  ✓ #9        │                                      │
│  ✓ #10       │ Debug Output:                        │
│               │ processing n=5...                    │
├───────────────┴──────────────────────────────────────┤
│ [q]uit  [j/k] navigate  [Enter] select  [d] debug   │
└──────────────────────────────────────────────────────┘
```

#### Solution File Contract

```python
# solution.py — standard CP style, directly submittable to CSES
import sys

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    n = int(input())
    debug(f"n = {n}")  # goes to stderr, shown in debug panel
    result = []
    while n != 1:
        result.append(n)
        n = n // 2 if n % 2 == 0 else n * 3 + 1
    result.append(1)
    print(*result)      # goes to stdout, compared against expected

if __name__ == "__main__":
    main()
```

#### Test Case Storage Structure

```
testcases/
  index.json              # Global metadata index
  1068/                   # Weird Algorithm
    meta.json             # Problem metadata + case descriptions
    1.in                  # Test case inputs/outputs
    1.out
    2.in
    2.out
    ...
  1083/                   # Missing Number
    meta.json
    1.in
    1.out
    ...
```

#### meta.json Example

```json
{
  "cses_id": 1068,
  "name": "Weird Algorithm",
  "category": "Introductory Problems",
  "time_limit": 1.0,
  "cases": [
    {"num": 1, "type": "sample", "desc": "sample from problem (n=3)"},
    {"num": 2, "type": "edge", "desc": "minimum: n=1"},
    {"num": 3, "type": "edge", "desc": "n=2 (even minimum)"},
    {"num": 4, "type": "random", "desc": "random small n"},
    {"num": 5, "type": "random", "desc": "random medium n"},
    {"num": 6, "type": "boundary", "desc": "n=999999 (near-max)"}
  ]
}
```

### API and Schema Documentation

No formal API exists for CSES. The CLI tool will define its own data schema:

* `index.json`: maps problem IDs → names, categories, file paths
* `meta.json` per problem: case metadata (type, description, time limit)
* `.in`/`.out` files: raw text test data (stdin input / expected stdout output)

### Configuration Examples

```toml
# pyproject.toml (package configuration)
[project]
name = "cses-cli"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "textual>=0.80",
    "typer>=0.12",
]

[project.scripts]
cses = "cses_cli.main:app"
```

## Technical Scenarios

### Scenario 1: TUI Framework Selection

**Requirements:**

* Full-screen lazygit-style split panels (test list left, details right)
* Color-coded pass/fail indicators
* Keyboard navigation (j/k, Enter, Tab, q)
* Stats display (x/y passed)
* Must pair with a CLI framework for non-TUI commands

**Preferred Approach: Textual + Typer + Rich**

| Layer      | Framework     | Role                              |
|------------|---------------|-----------------------------------|
| TUI        | Textual 8.x   | Full-screen interactive interface  |
| CLI        | Typer 0.24.x  | Command routing, argument parsing  |
| Formatting | Rich 14.x     | CLI-mode output (shared dep)       |

Typer already depends on Rich. Textual depends on Rich. Combined install: `pip install textual typer` pulls Click, Rich, shellingham, and Textual.

```
Textual → Rich
Typer   → Click + Rich + shellingham
```

Integration pattern: Typer handles CLI routing. The `invoke` command launches `TestRunnerApp.run()` (Textual app). The `test` command shows Rich-formatted stats in CLI mode with an option to enter TUI deep-dive.

**Implementation Details:**

Textual provides: `Horizontal` container (left/right split), `ListView`+`ListItem` (test case list), `RichLog`/`Static` (detail panel), `Header`/`Footer` (stats + keybindings), `Binding` class (j/k/Enter/Tab/q), `Worker` (run subprocess without blocking UI), reactive properties for auto-updating stats.

#### Considered Alternatives

* **urwid**: Capable but dated API, LGPL-2.1 license, limited Windows support. ~3k stars vs Textual's 35k. More verbose for equivalent layouts.
* **prompt_toolkit**: Built for REPL/prompt interfaces, not TUI apps. No pre-built widgets (ListView, DataTable). Wrong tool for this job.
* **curses (stdlib)**: Maximum effort for minimum gain. No widgets, no CSS layout, no color markup. Would require building everything from scratch.
* **npyscreen**: Effectively unmaintained (10-year gap between releases). 502 stars, 6 contributors. Unix-only.
* **blessed**: Low-level terminal library. No widget system. We'd reimplement what Textual provides.

### Scenario 2: Test Case Storage Format

**Requirements:**

* Git-friendly (text diffs, PR reviewability, efficient delta compression)
* Compact (~5 MB git clone is acceptable)
* Easy to read/write programmatically
* Must support metadata (problem name, category, case type)

**Preferred Approach: Flat Files + JSON Metadata**

Standard CP judge directory structure: `testcases/{cses_id}/{n}.in` and `{n}.out` with `meta.json` per problem.

**Size estimates:**

| Metric                  | Value       |
|-------------------------|-------------|
| Total test cases        | ~2,580      |
| Raw data size           | ~11.5 MB    |
| Git clone size          | ~5 MB       |
| After 10 updates        | ~7 MB       |
| After 100 updates       | ~15-20 MB   |

#### Considered Alternatives

* **SQLite**: Single file, good read performance (35% faster for 10KB blobs). But binary in git — no diffs, no PR reviews. After 10 updates: ~130 MB clone vs ~7 MB for flat files. Decisive disqualification.
* **JSON per-problem files**: Better than SQLite for git, but JSON overhead (keys, brackets, quotes) adds ~30%. Requires deserialization library. Flat files are simpler.
* **MessagePack/CBOR**: Compact binary serialization, but loses git diff capability. No advantage over flat files given git's zlib compression.
* **SQLite + zstd BLOBs**: Over-engineered. ~3-5 MB file size is smaller, but all git problems of SQLite remain. Marginal savings don't justify complexity.

### Scenario 3: Solution Execution Model

**Requirements:**

* Feed test input via stdin, capture stdout as answer
* Capture stderr as debug output
* Enforce time limits (TLE handling)
* Support all common Python input patterns (`input()`, `sys.stdin.readline`, `sys.stdin.read()`)

**Preferred Approach: Subprocess Execution**

```python
result = subprocess.run(
    [sys.executable, solution_path],
    input=test_input,
    capture_output=True,
    timeout=time_limit,
    text=True,
)
answer = result.stdout        # compared against expected
debug_output = result.stderr  # shown to user
elapsed = measured_time       # TLE check
```

For TLE handling with process group cleanup:

```python
proc = subprocess.Popen(
    [sys.executable, solution_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    start_new_session=True,  # enables process group kill
)
try:
    stdout, stderr = proc.communicate(input=test_input.encode(), timeout=time_limit)
except subprocess.TimeoutExpired:
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
    # verdict: TLE
```

Memory tracking via GNU time (`/usr/bin/time -f '%M'`) reports max RSS in KB.

#### Considered Alternatives

* **In-process execution** (import + StringIO mock): Faster (no subprocess overhead), but user code can crash the runner, no real memory isolation, subtle bug with module-level `input = sys.stdin.readline` capturing old stdin before mock. Not recommended as primary mode.
* **main() returns answer** (function contract): Unnatural for CP — real solutions use `print()`. Would not be directly submittable to CSES. Forces custom API learning.

### Scenario 4: Test Case Generation

**Requirements:**

* Generate ~2,580 test cases for 258 problems
* Balance correctness coverage with compact size (no stress-test-level large inputs)
* Pre-generate and ship in repo (~5 MB)
* Validate expected outputs are correct

**Preferred Approach: LLM-Assisted Generators + Reference Solutions**

Generation pipeline:

```
1. Problem statement + constraints → LLM generates Python generator script
2. Reusable templates for common patterns (single-int, array, graph, tree, grid)
3. Generator scripts produce input files
4. Reference solutions (LLM-written, verified against CSES samples) produce expected outputs
5. Human reviews, stores in flat-file structure
6. All generators use deterministic seeds for reproducibility
```

Test case distribution per problem (~10 average):

| Case Type     | Count | Purpose                              |
|---------------|-------|--------------------------------------|
| Sample        | 1     | From CSES problem page               |
| Edge          | 3-4   | Min/max values, single element, etc.  |
| Random        | 3-4   | Medium-sized random valid inputs     |
| Boundary      | 1-2   | Near constraint limits (not max)     |

Generator template patterns:

| Template       | Applies to     | Example problems                  |
|----------------|----------------|-----------------------------------|
| Single integer | ~30 problems   | Weird Algorithm, Trailing Zeros   |
| Array          | ~60 problems   | Maximum Subarray Sum              |
| Graph (n,m)    | ~40 problems   | Building Roads, Shortest Routes   |
| Tree           | ~15 problems   | Subordinates, Tree Diameter       |
| Grid (n×m)     | ~15 problems   | Counting Rooms, Grid Paths        |
| Multi-query    | ~20 problems   | Range queries                     |
| Special        | ~78 problems   | Problem-specific formats          |

**Correctness validation:** Source or write reference solutions → verify against CSES sample I/O → run on generated inputs → store outputs. For problems with multiple valid outputs (~30-50 estimated), store checker functions instead of exact match.

#### Considered Alternatives

* **Scrape from CSES**: Not possible — test cases are hidden, no API.
* **Manual generator writing for all 258 problems**: Labor-intensive and infeasible. LLM-assisted generation with human review is the practical approach.
* **Generate on demand**: Ship only generators (~500 KB) instead of pre-generated data (~5 MB). Rejected because: inconsistent tests across users, first-run delay, needs correct solution at generation time.

### Scenario 5: CLI Architecture and Command Design

**Requirements:**

* Three modes: `invoke` (TUI), `run` (quick), `test` (full suite)
* Python-only initially, extensible to other languages
* pip-installable as a CLI tool

**Preferred Approach: Typer CLI + Textual TUI**

```
cses-cli/
  src/
    cses_cli/
      __init__.py
      main.py           # Typer app, CLI entry point
      runner.py          # Subprocess execution engine
      comparator.py      # Output comparison (exact, checker, float)
      testcases.py       # Test case loading from flat files
      tui/
        __init__.py
        app.py           # Textual TestRunnerApp
        widgets.py       # Custom widgets (CaseList, DetailPanel)
        styles.tcss      # Textual CSS styling
  testcases/             # Pre-generated test data (flat files)
    index.json
    1068/
      meta.json
      1.in, 1.out, ...
  generators/            # Optional: generator scripts
    templates/
    1068_weird_algorithm.py
  pyproject.toml
  README.md
```

CLI commands:

```python
import typer
app = typer.Typer()

@app.command()
def run(code: str, problem: int, case: int = 1):
    """Run solution against a single test case."""
    ...

@app.command()
def test(code: str, problem: int):
    """Run solution against all test cases, show stats."""
    ...

@app.command()
def invoke(code: str, problem: int):
    """Open full-screen TUI test explorer."""
    ...
```

#### Considered Alternatives

* **Click instead of Typer**: More boilerplate, no type-hint convenience, no auto-Rich integration. Typer is built on Click anyway.
* **argparse**: Stdlib but verbose. No Rich integration, no auto-completion, no subcommand ergonomics.
* **Monorepo with test data**: Keeping testcases in same repo vs separate data repo. Same repo is simpler for initial version; can split later if repo grows.
