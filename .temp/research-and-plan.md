# CSES-CLI: Technical Research & Implementation Plan

> A local CLI/TUI tool to run Python solutions against CSES problem set test cases offline.

---

## 1. Problem Summary

You want to solve CSES problems locally without relying on the slow online judge. The tool should:

- Accept a Python file + problem ID
- Run the code against locally-stored test cases
- Show results in a rich, interactive TUI (like lazygit)
- Support 258 problems across 12 categories (from the updated ~400-problem CSES set)

---

## 2. Scope: Which Problems to Include

The CSES Problem Set has been updated and now contains **~400 problems** across 16+ categories (up from 300). From this expanded set, **12 categories are included (258 problems)**:

| Category                | # Problems | Include? |
|-------------------------|-----------|----------|
| Introductory Problems   | 24        | ✅ Yes    |
| Sorting and Searching   | 35        | ✅ Yes    |
| Dynamic Programming     | 23        | ✅ Yes    |
| Graph Algorithms        | 36        | ✅ Yes    |
| Range Queries           | 25        | ✅ Yes    |
| Tree Algorithms         | 16        | ✅ Yes    |
| Advanced Techniques     | 25        | ✅ Yes    |
| Sliding Window Problems | 11        | ✅ Yes    |
| Interactive Problems    | 6         | ✅ Yes    |
| Bitwise Operations      | 11        | ✅ Yes    |
| Advanced Graph Problems | 28        | ✅ Yes    |
| Counting Problems       | 18        | ✅ Yes    |
| **Total Included**      | **258**   |          |
| Mathematics             | 37        | ❌ No     |
| String Algorithms       | 21        | ❌ No     |
| Geometry                | 16        | ❌ No     |
| Construction Problems   | 8         | ❌ No     |

> Source: https://cses.fi/problemset/ (updated site with ~400 problems)

Each problem has a unique CSES task ID (e.g. `1068` for "Weird Algorithm"). This ID is the key users will use.

---

## 3. Technology Decisions

### 3.1 Language & Framework: **Python**

**Recommendation: Build the entire CLI in Python.**

Rationale:
- User solutions are in Python — same ecosystem, zero context-switching
- **Textual** (Python TUI framework) is the best fit for the lazygit-like interactive experience
- **Typer** provides modern CLI routing with auto-completion and help
- Python's `subprocess` module handles running user code natively
- Python's `sqlite3` is built-in — no external DB drivers needed
- Easy to distribute via `pip install`

### 3.2 Key Dependencies

| Package        | Purpose                                        | Version  |
|----------------|------------------------------------------------|----------|
| `typer[all]`   | CLI framework (commands, args, shell completion)| ≥0.12    |
| `textual`      | TUI framework (panels, tables, key bindings)   | ≥0.80    |
| `rich`         | Terminal formatting (included with Textual)     | ≥13.0    |
| `sqlite3`      | Test case storage (Python stdlib)              | built-in |

No heavy dependencies. Total install footprint: ~15-20 MB.

### 3.3 Test Case Storage: **SQLite**

**Recommendation: Single SQLite database file shipped with the repo.**

Why SQLite over JSON/CSV:
- **Queryable**: Fetch test cases by problem ID instantly
- **Compact**: Single file, easy to git-push
- **Indexed**: Fast lookups even with thousands of test cases
- **Atomic**: No partial-read issues

**Estimated size:**
- ~258 problems × 25 test cases avg × ~3 KB per case = **~19 MB**
- With metadata + indexes + overhead: **~30-40 MB**
- Target budget: **≤ 50-60 MB** — plenty of room for comprehensive test coverage
- Well within git-friendly range (GitHub allows up to 100 MB per file)

Schema:
```sql
CREATE TABLE problems (
    task_id    INTEGER PRIMARY KEY,  -- CSES task ID (e.g. 1068)
    title      TEXT NOT NULL,
    category   TEXT NOT NULL,
    url        TEXT NOT NULL
);

CREATE TABLE test_cases (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES problems(task_id),
    case_num   INTEGER NOT NULL,     -- 1, 2, 3...
    input      TEXT NOT NULL,
    expected   TEXT NOT NULL,
    is_edge    BOOLEAN DEFAULT 0,    -- marks edge case tests
    UNIQUE(task_id, case_num)
);

CREATE INDEX idx_test_cases_task ON test_cases(task_id);
```

---

## 4. Test Case Generation Strategy

### 4.1 The Challenge

CSES doesn't publicly provide test case files. Scraping is against their ToS. So test cases must be **generated**.

### 4.2 Approach: AI-Assisted Generation + Verified Reference Solutions

**Three-tier strategy:**

1. **Tier 1 — Sample cases from problem statements** (2-3 per problem)
   - Every CSES problem page includes sample input/output
   - These can be manually curated or parsed from problem descriptions
   - Serves as the basic sanity check

2. **Tier 2 — Algorithmically generated cases** (13-17 per problem)
   - Write a Python generator script per problem category
   - Generates random valid inputs within the problem's constraints
   - Uses a **verified reference solution** to compute expected output
   - Categories of generated cases:
     - **Minimum input** (n=1, edge boundaries) — 2-3 cases
     - **Small random** (n=5-20, for quick debugging) — 3-4 cases
     - **Medium random** (n=100-1000, correctness check) — 5-6 cases
     - **Boundary/edge cases** (all same values, sorted, reverse-sorted, max values) — 3-4 cases
   - NOT generating MLE-sized inputs (you don't need stress tests, just correctness)

3. **Tier 3 — AI-assisted edge case generation** (2-3 per problem)
   - Use an LLM to identify tricky edge cases specific to each problem
   - E.g. for "Weird Algorithm": input = 1, input = 2^30, etc.

### 4.3 Size Budget Per Problem

| Case Type       | Count | Avg Size | Subtotal |
|-----------------|-------|----------|----------|
| Sample          | 2-3   | ~0.5 KB  | ~1.5 KB  |
| Random small    | 5-6   | ~1 KB    | ~6 KB    |
| Random medium   | 8-10  | ~4 KB    | ~40 KB   |
| Edge cases      | 5-6   | ~2 KB    | ~12 KB   |
| **Total**       | **20-25** | —    | **~60 KB** |

**258 problems × ~60 KB = ~15.5 MB** raw data → **~30-45 MB** in SQLite with indexes.

This is well within the 50-60 MB budget, with room to add more cases later if needed.

### 4.4 Reference Solutions

For generating expected output, you need verified reference solutions. Options:
- Use well-known community solutions (many CSES solution repos on GitHub)
- Write your own reference solutions for each included problem
- Use a hybrid: community-verified solutions + manual verification for edge cases

**Recommendation:** Use a build-time script that:
1. Takes a generator script + reference solution per problem
2. Generates N random inputs
3. Runs reference solution to get expected outputs
4. Inserts into SQLite DB
5. Ships the DB file in the repo

---

## 5. Input/Output Handling Design

### 5.1 How CSES Input Works

CSES problems read from **stdin** (file-style input). The user's Python code should read from `sys.stdin` or `input()` as normal.

### 5.2 How the CLI Runs User Code

```python
import subprocess

result = subprocess.run(
    ["python3", user_code_path],
    input=test_case_input,       # fed via stdin
    capture_output=True,
    text=True,
    timeout=5.0                  # 5 seconds per test case
)

stdout = result.stdout           # → this is the "answer"
stderr = result.stderr           # → this is "debug output" (prints)
return_code = result.returncode  # → nonzero = runtime error
```

### 5.3 The `main()` Convention

You mentioned wanting a `main()` function. Two approaches:

**Option A — Direct execution (Recommended):**
User writes a normal Python script that reads from stdin and prints to stdout. No wrapper needed.

```python
# user's solution.py
n = int(input())
arr = list(map(int, input().split()))
print(sum(arr))
```

The CLI just runs `python3 solution.py` with stdin piped in. This is the standard competitive programming convention and requires zero magic.

**Option B — main() wrapper:**
If you want to enforce a `main()` function, the CLI can dynamically import the user's module and call `main()`, redirecting stdin/stdout. This adds complexity and is less standard.

**Recommendation: Option A.** It's simpler, standard, and exactly how CSES works online.

### 5.4 Output Comparison

```python
def compare_output(actual: str, expected: str) -> bool:
    # Strip trailing whitespace/newlines, compare line by line
    actual_lines = actual.strip().splitlines()
    expected_lines = expected.strip().splitlines()
    return actual_lines == expected_lines
```

Handles the common "trailing newline" problem that frustrates competitive programmers.

---

## 6. CLI Commands & UX Design

### 6.1 Installation & Invocation

```bash
pip install cses-cli       # or: pip install -e . (dev mode)
cses <command>             # main entry point
```

### 6.2 Commands

#### `cses run <code_path> <problem_id>`
Quick-run mode. Runs against the first sample test case and prints result.

```
$ cses run solution.py 1068

  Problem: Weird Algorithm (#1068)
  Test Case 1: ✅ Passed (0.03s)
  
  Input:  3
  Output: 3 10 5 16 8 4 2 1
```

#### `cses test <code_path> <problem_id>`
Full test mode. Runs against ALL test cases, then shows interactive explorer.

**Phase 1 — Summary:**
```
$ cses test solution.py 1068

  Problem: Weird Algorithm (#1068)
  
  Results: 12/14 passed ✅  |  2 failed ❌  |  0.42s total
  
  [Press ENTER to explore results, or Q to quit]
```

**Phase 2 — Interactive Explorer (TUI):**
```
┌─ Test Cases ──────────┬─ Details ─────────────────────────┐
│ ❌ Case 7  (0.05s)    │  Input:                           │
│ ❌ Case 12 (TLE)      │  1000000000                       │
│ ✅ Case 1  (0.02s)    │                                   │
│ ✅ Case 2  (0.01s)    │  Expected Output:                 │
│ ✅ Case 3  (0.03s)    │  ... 4 2 1                        │
│ ✅ Case 4  (0.02s)    │                                   │
│ ✅ Case 5  (0.01s)    │  Your Output:                     │
│ ✅ Case 6  (0.03s)    │  ... 4 2 1 0                      │
│ ✅ Case 8  (0.02s)    │                                   │
│ ✅ Case 9  (0.01s)    │  Debug (stderr):                  │
│ ✅ Case 10 (0.02s)    │  n=1000000000, steps=224          │
│ ✅ Case 11 (0.02s)    │                                   │
│ ✅ Case 13 (0.01s)    │  Verdict: ❌ WRONG ANSWER         │
│ ✅ Case 14 (0.03s)    │  (output differs at line 1)       │
└───────────────────────┴───────────────────────────────────┘
 [↑↓] Navigate  [q] Quit  [r] Re-run
```

Key features:
- **Failed cases sorted to top** (red)
- **Passed cases below** (green)
- Left panel: case list with status + time
- Right panel: input, expected output, actual output, stderr debug
- Keyboard navigation (arrow keys, j/k)
- Re-run without leaving the TUI

#### `cses invoke`
Full-screen TUI dashboard (lazygit-style). Stretch goal — implement after `run` and `test` work.

```
┌─ Categories ────────────┬─ Problems ───────────────────────────────┐
│ > Introductory (24)     │  #1068  Weird Algorithm       ✅ Solved  │
│   Sorting (35)          │  #1083  Missing Number        ⬜ Todo    │
│   DP (23)               │  #1069  Repetitions           ⬜ Todo    │
│   Graph (36)            │  #1094  Increasing Array      ❌ Failed  │
│   Range (25)            │  ...                                     │
│   Tree (16)             │                                          │
│   Advanced (25)         │                                          │
│   Sliding Window (11)   │                                          │
│   Interactive (6)       │                                          │
│   Bitwise (11)          │                                          │
│   Adv. Graph (28)       │                                          │
│   Counting (18)         │                                          │
└─────────────────────────┴──────────────────────────────────────────┘
 [↑↓] Navigate  [Enter] Select  [t] Test  [r] Run  [q] Quit
```

### 6.3 Keybindings (consistent across views)

| Key       | Action                    |
|-----------|---------------------------|
| `↑/↓/j/k`| Navigate list             |
| `Enter`   | Select / Drill down       |
| `r`       | Re-run current            |
| `q/Esc`   | Back / Quit               |
| `Tab`     | Switch panels             |
| `?`       | Help                      |

---

## 7. Project Structure

```
cses-cli/
├── pyproject.toml              # Package config (pip installable)
├── README.md
├── data/
│   ├── cses.db                 # SQLite DB with problems + test cases
│   └── problems.json           # Problem metadata (backup/reference)
├── src/
│   └── cses_cli/
│       ├── __init__.py
│       ├── cli.py              # Typer CLI entry point (run, test, invoke)
│       ├── runner.py           # Subprocess execution engine
│       ├── judge.py            # Output comparison logic
│       ├── db.py               # SQLite data access layer
│       ├── models.py           # Dataclasses (Problem, TestCase, Result)
│       ├── tui/
│       │   ├── __init__.py
│       │   ├── app.py          # Main Textual App
│       │   ├── test_explorer.py # Test result explorer view
│       │   ├── dashboard.py    # Full invoke dashboard
│       │   └── widgets.py      # Custom widgets (case list, detail panel)
│       └── utils.py            # Helpers (formatting, time, etc.)
├── generators/                 # Test case generation scripts
│   ├── generate_all.py         # Master generator runner
│   ├── reference_solutions/    # Verified solutions per problem
│   └── generators/             # Input generator per problem/category
├── tests/                      # pytest tests for the CLI itself
│   ├── test_runner.py
│   ├── test_judge.py
│   └── test_db.py
└── .temp/                      # Scratch/dev files
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Core engine, no TUI)
1. Set up project structure with `pyproject.toml`
2. Build `db.py` — SQLite schema + data access
3. Build `models.py` — dataclasses for Problem, TestCase, RunResult
4. Build `runner.py` — subprocess execution with timeout
5. Build `judge.py` — output comparison
6. Build `cli.py` — Typer with `cses run` command
7. Seed DB with ~5 sample problems + hand-written test cases for testing
8. **Milestone: `cses run solution.py 1068` works end-to-end**

### Phase 2: Full Test Mode
1. Implement `cses test` — runs all cases, prints summary
2. Build basic TUI test explorer (Textual)
   - Left panel: test case list (red/green, sorted by status)
   - Right panel: input/output/expected detail
   - Keyboard navigation
3. **Milestone: `cses test solution.py 1068` shows interactive results**

### Phase 3: Test Case Generation
1. Build generator framework (`generators/`)
2. Write/curate reference solutions for included problems
3. Write input generators per category (Introductory, Sorting, DP, Graph, Range, Tree, Advanced, Sliding Window, Interactive, Bitwise, Advanced Graph, Counting)
4. Run generators → populate SQLite DB
5. Validate DB integrity and size (~30-45 MB target)
6. **Milestone: Full DB with 258 problems × 20-25 test cases each**

### Phase 4: Dashboard TUI (`cses invoke`)
1. Build category browser
2. Build problem list with solve status tracking
3. Integrate test running from within the dashboard
4. Add progress tracking (solved/attempted per category)
5. **Milestone: Full lazygit-like experience**

### Phase 5: Polish & Distribution
1. Shell completion (Typer provides this)
2. Config file support (`~/.cses-cli/config.toml`)
3. `pip install cses-cli` packaging
4. README with usage docs
5. GitHub release

---

## 9. Key Design Decisions Summary

| Decision                  | Choice                | Rationale                              |
|---------------------------|-----------------------|----------------------------------------|
| Language                  | Python                | Same as user solutions, best TUI libs  |
| CLI framework             | Typer                 | Modern, type-hint based, auto-complete |
| TUI framework             | Textual               | Best Python TUI, CSS layouts, async    |
| Storage                   | SQLite                | Compact, queryable, git-friendly       |
| Input handling            | stdin via subprocess   | Standard CP convention, no magic       |
| Output comparison         | Line-by-line stripped  | Handles trailing whitespace            |
| Test case source          | Generated + samples    | CSES doesn't share test data           |
| DB size target            | ≤ 50 MB             | Git-pushable, fits your budget        |
| Problems included         | 258 (12 categories)  | From updated ~400-problem CSES set    |

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test case correctness | High — wrong expected output = false failures | Use verified reference solutions; allow user to flag/skip cases |
| Test case generation at scale | Medium — 258 problems is a lot of generators | Group by category; many problems share generator patterns (e.g. all "array" problems) |
| Large DB file | Low — estimates show < 50 MB | Keep inputs moderate (no stress-test sized); budget allows ~60 KB/problem |
| Textual learning curve | Low | Well-documented; many examples available |
| Python subprocess overhead | Low — 5s timeout is generous | User code runs once per test case; parallel execution possible later |

---

## 11. Future Expansion Ideas

- **Multi-language support**: Run C++, Java, Rust solutions (change subprocess command)
- **Problem statement viewer**: Show the problem description within the TUI
- **Solution templates**: Auto-generate boilerplate for a problem
- **Timing benchmarks**: Compare your solution time against reference
- **Difficulty ratings**: Show community difficulty per problem
- **Sync with CSES**: Check your online solve status
