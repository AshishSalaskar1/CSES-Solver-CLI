# CSES CLI

A CLI/TUI tool to run Python solutions against CSES problem set test cases offline.

> **258 problems** across 12 categories from [cses.fi/problemset](https://cses.fi/problemset/)

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Quick-run against first test case
cses run solution.py 1068

# Full test against all test cases + interactive TUI explorer
cses test solution.py 1068

# Full-screen dashboard (lazygit-style)
cses invoke
```

## Commands

| Command | Description |
|---------|-------------|
| `cses run <file> <id>` | Quick-run against the first test case |
| `cses test <file> <id>` | Run all test cases, show summary + TUI explorer |
| `cses invoke` | Launch full-screen dashboard TUI |
| `cses howto` | Show solution writing guide in terminal |
| `cses list` | List all problems by category |
| `cses info <id>` | Show problem details |
| `cses seed` | Re-seed/reset the problem database |
| `cses generate` | Generate test cases from reference solutions |

## Options

```bash
cses run solution.py 1068 --timeout 10    # Custom timeout (default: 5s)
cses test solution.py 1068 --no-tui       # Skip TUI, print table only
cses list --category "Dynamic Programming" # Filter by category
cses generate --category "Introductory Problems" --cases 25
```

## Writing Solutions

### Return-Value Mode (recommended)

Define a `solve(data)` function — only its return value is judged. `print()` calls become debug output (visible in the TUI under "Debug") and **won't affect your verdict**.

```python
def solve(data: str) -> int:
    # data = raw stdin string, e.g. "5\n2 3 1 5\n"
    parts = data.split()
    n = int(parts[0])
    nums = list(map(int, parts[1:]))
    
    print(f"debug: n={n}")  # safe! shown as debug output
    
    return n * (n + 1) // 2 - sum(nums)
```

**The `data` parameter** is the raw stdin string (exactly what `sys.stdin.read()` returns), including `\n` newline characters:
- `data.split()` → splits on all whitespace (spaces + newlines)  
- `data.strip().split('\n')` → splits into lines

**Return values:**
- `str`, `int`, `float` → converted to string
- `list`, `tuple` → each element on its own line
- `None` → empty output

### Legacy Mode (backward compatible)

No `solve()` function — everything printed to stdout is your answer. Existing solutions work without changes:

```python
n = int(input())
nums = list(map(int, input().split()))
print(n * (n + 1) // 2 - sum(nums))
```

> **Tip:** Run `cses howto` for a quick in-terminal guide on both modes.

## How It Works

1. **Write your solution** using a `solve()` function (recommended):
   ```python
   # solution.py
   def solve(data: str):
       n = int(data.strip())
       result = [n]
       while n != 1:
           n = n // 2 if n % 2 == 0 else n * 3 + 1
           result.append(n)
       return " ".join(map(str, result))
   ```

2. **Run it**: `cses test solution.py 1068`

3. **Explore results** in the interactive TUI:
   - Failed cases sorted to top (red), passed below (green)
   - See input, expected output, your output, and debug stderr
   - Press `r` to re-run, `q` to quit

## Test Case Explorer TUI

```
┌─ Test Cases ──────────┬─ Details ─────────────────────────┐
│ ❌ Case 7  (0.05s)    │  Input:                           │
│ ❌ Case 12 (TLE)      │  1000000000                       │
│ ✅ Case 1  (0.02s)    │                                   │
│ ✅ Case 2  (0.01s)    │  Expected Output:                 │
│ ✅ Case 3  (0.03s)    │  ... 4 2 1                        │
│ ...                    │                                   │
│                        │  Your Output:                     │
│                        │  ... 4 2 1 0                      │
│                        │                                   │
│                        │  Verdict: ❌ WRONG ANSWER         │
└────────────────────────┴───────────────────────────────────┘
 [↑↓] Navigate  [q] Quit  [r] Re-run
```

## Dashboard TUI (`cses invoke`)

```
┌─ Categories ────────────┬─ Problems ───────────────────────────────┐
│ > Introductory (24)     │  #1068  Weird Algorithm                  │
│   Sorting (35)          │  #1083  Missing Number                   │
│   DP (23)               │  #1069  Repetitions                      │
│   Graph (36)            │  #1094  Increasing Array                 │
│   Range (25)            │  ...                                     │
│   Tree (16)             │                                          │
│   Advanced (25)         │                                          │
│   Sliding Window (11)   │                                          │
│   ...                   │                                          │
└─────────────────────────┴──────────────────────────────────────────┘
 [↑↓] Navigate  [Tab] Switch panel  [t] Test  [q] Quit
```

## Categories Included (258 problems)

| Category | Problems |
|----------|----------|
| Introductory Problems | 24 |
| Sorting and Searching | 35 |
| Dynamic Programming | 23 |
| Graph Algorithms | 36 |
| Range Queries | 25 |
| Tree Algorithms | 16 |
| Advanced Techniques | 25 |
| Sliding Window Problems | 11 |
| Interactive Problems | 6 |
| Bitwise Operations | 11 |
| Advanced Graph Problems | 28 |
| Counting Problems | 18 |

## Configuration

Create `~/.cses-cli/config.toml` to customize defaults:

```toml
timeout = 5.0
python_command = "python3"
solutions_dir = "~/cses-solutions"
```

## Generating Test Cases

The tool comes with a generator framework. To regenerate or extend test cases:

```bash
cses generate                    # Generate for all categories
cses generate -c "Graph Algorithms" -n 25  # Specific category, 25 cases each
```

Test cases are generated using verified reference solutions + random input generators.

## Project Structure

```
cses-cli/
├── pyproject.toml              # Package config
├── data/cses.db                # SQLite DB (problems + test cases)
├── src/cses_cli/
│   ├── cli.py                  # Typer CLI commands
│   ├── runner.py               # Subprocess execution engine
│   ├── judge.py                # Output comparison
│   ├── db.py                   # SQLite data access
│   ├── models.py               # Data models
│   ├── config.py               # Configuration
│   ├── tui/
│   │   ├── test_explorer.py    # Test result TUI
│   │   └── dashboard.py        # Full dashboard TUI
│   └── utils.py                # Formatting helpers
└── generators/
    ├── generate_all.py         # Generator framework
    ├── input_generators.py     # Random input generators
    └── reference_solutions/    # Verified solutions per category
```
