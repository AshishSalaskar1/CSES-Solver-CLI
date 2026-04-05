# Feature Plan: Return-Value Evaluation Mode (LeetCode-style)

## Problem

Currently, the CSES CLI judges solutions based on **everything printed to stdout**. This means any `print()` call — including debug prints — pollutes the output and causes wrong answers. For example:

```python
# missing_number.py (current)
print("Ashish")                        # ← this breaks the answer!
print(n * (n + 1) // 2 - sum(nums))
```

## Goal

Support a **return-value mode** (like LeetCode) where:
- Only the **return value** of a `solve()` function is evaluated
- `print()` calls become **debug output** (shown in TUI under "Debug") and don't affect the verdict
- Fully **backward compatible** — existing stdout-based solutions still work

## Current Architecture

```
runner.py                 judge.py
  │                         │
  ├─ subprocess.run()       ├─ compare_output(actual, expected)
  │   python3 solution.py   │   strips & compares line-by-line
  │   stdin ← test input    │
  │   stdout → actual_output│
  │   stderr → debug info   │
  └─────────────────────────┘
```

**Key files:**
- `src/cses_cli/runner.py` — runs `python3 <solution.py>`, captures stdout as the answer
- `src/cses_cli/judge.py` — compares `actual_output` vs `expected` (line-by-line)
- `src/cses_cli/models.py` — `RunResult.actual_output` holds stdout, `RunResult.stderr` holds stderr
- `src/cses_cli/tui/test_explorer.py` — displays stderr as "Debug (stderr)" in the detail panel

## Design: Harness-Based Auto-Detection

### Core Idea

Introduce a **harness script** (`harness.py`) that wraps the user's solution. Instead of running `python3 solution.py` directly, the runner invokes `python3 harness.py solution.py`. The harness:

1. Reads all of stdin upfront
2. Replaces `sys.stdout` with a capture buffer (so `print()` goes to a buffer, not real stdout)
3. Replaces `sys.stdin` with a `StringIO` of the input (so `input()` still works for legacy code)
4. Loads and executes the user's solution module
5. **Auto-detects the mode:**
   - If the module defines a `solve()` function → **return-value mode**
   - If not → **legacy stdout mode**

### Return-Value Mode Flow

```
User writes:                    Harness does:
┌──────────────────────┐       ┌────────────────────────────────────┐
│ def solve(data):     │       │ 1. Read stdin → input_data         │
│     print("debug!")  │  ──►  │ 2. Redirect stdout → capture buf   │
│     n = int(data)    │       │ 3. exec_module(solution)           │
│     return n + 1     │       │ 4. Detect solve() exists           │
│                      │       │ 5. Call solve(input_data)          │
└──────────────────────┘       │ 6. Write return value → real stdout│
                               │ 7. Write captured prints → stderr  │
                               └────────────────────────────────────┘

Result:
  stdout (actual_output) = "6\n"        ← only the return value (judged)
  stderr                 = "debug!\n"   ← print output (shown as debug)
```

### Legacy Mode Flow (backward compatible)

```
User writes:                    Harness does:
┌──────────────────────┐       ┌────────────────────────────────────┐
│ n = int(input())     │       │ 1. Read stdin → input_data         │
│ print(n + 1)         │  ──►  │ 2. Redirect stdout → capture buf   │
│                      │       │ 3. Replace stdin with StringIO     │
│                      │       │ 4. exec_module(solution)           │
│                      │       │ 5. No solve() found                │
│                      │       │ 6. Write captured stdout → real out│
└──────────────────────┘       └────────────────────────────────────┘

Result:
  stdout (actual_output) = "6\n"        ← same as today (judged)
  stderr                 = ""           ← no debug output
```

### What does `data` contain?

The `data` parameter is the **raw stdin string** — exactly what `sys.stdin.read()` would return. It's the full test case input as a single string, **including `\n` newline characters**.

**Example:** For Missing Number (problem 1083), a test case input looks like:
```
5
2 3 1 5
```

The `data` parameter would be: `"5\n2 3 1 5\n"`

So `data.split()` gives `['5', '2', '3', '1', '5']` (splits on all whitespace including `\n`), and `data.strip().split('\n')` gives `['5', '2 3 1 5']` (splits into lines).

This is the same string you'd get from `sys.stdin.read()` in a traditional solution — just passed as a parameter instead.

### New Solution Style Example

```python
# missing_number.py — return-value mode
def solve(data: str) -> int:
    # data = "5\n2 3 1 5\n" (raw stdin with newlines)
    parts = data.split()       # ['5', '2', '3', '1', '5']
    n = int(parts[0])
    nums = list(map(int, parts[1:]))

    print(f"Debug: n={n}, count={len(nums)}")  # ← safe! goes to stderr
    
    return n * (n + 1) // 2 - sum(nums)
```

Or if you prefer line-by-line parsing:
```python
def solve(data: str) -> int:
    lines = data.strip().split('\n')   # ['5', '2 3 1 5']
    n = int(lines[0])
    nums = list(map(int, lines[1].split()))
    return n * (n + 1) // 2 - sum(nums)
```

### Return Value Handling

| Return type      | Output behavior                        |
|------------------|----------------------------------------|
| `str`            | Written as-is                          |
| `int`, `float`   | Converted via `str()`                  |
| `list`, `tuple`  | Each element on its own line (`\n`-joined) |
| `None`           | Empty output (likely wrong answer)     |

## Implementation Plan

### TODO 1: Create `src/cses_cli/harness.py` (new file)

The harness script that wraps solution execution. Core logic:

```python
"""Execution harness for user solutions — supports return-value and legacy modes."""
import sys, os, io, importlib.util

def main():
    solution_path = sys.argv[1]
    
    # 1. Read all input upfront
    input_data = sys.stdin.read()
    
    # 2. Save real stdout via file descriptor duplication
    real_stdout_fd = os.dup(1)
    real_stdout = os.fdopen(real_stdout_fd, 'w')
    
    # 3. Replace stdin (so input() works in legacy mode)
    sys.stdin = io.StringIO(input_data)
    
    # 4. Capture stdout (print() goes here)
    capture = io.StringIO()
    sys.stdout = capture
    
    # 5. Load user module
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    solution_dir = os.path.dirname(os.path.abspath(solution_path))
    sys.path.insert(0, solution_dir)
    spec.loader.exec_module(module)
    
    # 6. Auto-detect mode
    if hasattr(module, 'solve'):
        # RETURN-VALUE MODE
        result = module.solve(input_data)
        
        # Format and write return value to real stdout
        if result is not None:
            if isinstance(result, (list, tuple)):
                output = '\n'.join(str(x) for x in result)
            else:
                output = str(result)
            real_stdout.write(output)
            if not output.endswith('\n'):
                real_stdout.write('\n')
        
        # Send captured prints to stderr (debug)
        debug = capture.getvalue()
        if debug:
            sys.stderr.write(debug)
    else:
        # LEGACY MODE — captured stdout IS the answer
        real_stdout.write(capture.getvalue())
    
    real_stdout.flush()
    real_stdout.close()

if __name__ == '__main__':
    main()
```

### TODO 2: Update `src/cses_cli/runner.py`

Change the subprocess command to invoke the harness:

```python
# Before:
[python_cmd, str(code_path)]

# After:
harness_path = Path(__file__).parent / "harness.py"
[python_cmd, str(harness_path), str(code_path)]
```

No other changes needed — `actual_output` (stdout) and `stderr` flow through the same way.

### TODO 3: Update `README.md`

Add a dedicated section documenting both solution styles:

- **"Writing Solutions"** section with two subsections:
  - **Return-value mode (recommended):** Define `def solve(data: str)`, explain what `data` contains (raw stdin with `\n`), show parsing patterns (`data.split()` vs `data.strip().split('\n')`), explain return value handling (str, int, list), explain that `print()` is safe for debugging
  - **Legacy stdout mode:** Existing `print()`-based style, explain it still works unchanged
- Show a side-by-side comparison of the two styles
- Document the `data` parameter nuance clearly (it's raw stdin, includes newlines)

### TODO 4: Add `cses howto` CLI command

Add a new CLI command `cses howto` (or `cses guide`) that prints a concise in-terminal guide explaining:

- The two solution modes and how auto-detection works
- The `solve(data)` convention: what `data` contains, parsing tips
- That `print()` is safe for debugging in return-value mode
- Return value handling (str, int, list/tuple)
- A quick example of each mode

This gives users instant help without leaving the terminal. Example output:

```
  📖 CSES CLI — Solution Guide

  RETURN-VALUE MODE (recommended)
  ──────────────────────────────
  Define a solve() function. Only its return value is judged.
  print() calls become debug output — they won't affect your answer.

    def solve(data: str):
        # data = raw stdin string, e.g. "5\n2 3 1 5\n"
        parts = data.split()
        n = int(parts[0])
        nums = list(map(int, parts[1:]))
        print(f"debug: n={n}")        # safe! shown as debug
        return n * (n + 1) // 2 - sum(nums)

  LEGACY MODE (backward compatible)
  ──────────────────────────────
  No solve() function — everything printed to stdout is your answer.

    n = int(input())
    nums = list(map(int, input().split()))
    print(n * (n + 1) // 2 - sum(nums))

  DATA PARAMETER
  ──────────────
  • data is the raw stdin string (same as sys.stdin.read())
  • Includes \n newline characters
  • data.split() → splits on all whitespace (ignores newlines)
  • data.strip().split('\n') → splits into lines

  RETURN VALUES
  ─────────────
  • str, int, float → converted to string
  • list, tuple → each element on its own line
  • None → empty output (likely wrong answer)
```

### TODO 5: Update `missing_number.py` example

Convert the example solution to demonstrate the new `solve()` pattern with a debug print.

## Design Decisions & Trade-offs

### Why auto-detection (no CLI flag)?
- Zero friction for the user — just define `solve()` and it works
- Fully backward compatible — no existing solution breaks
- A `--legacy` flag could be added later if needed, but auto-detect covers 99% of cases

### Why a harness script (not patching sys.stdout in runner.py)?
- The runner uses `subprocess.run()` — it can't modify the child process's sys.stdout
- A harness script runs in the same process as the solution, so it can intercept stdout
- Clean separation: runner manages subprocess lifecycle, harness manages I/O routing

### Why `os.dup(1)` for real stdout?
- `sys.stdout` can be replaced, but the underlying file descriptor 1 cannot
- `os.dup(1)` creates a copy of the real stdout fd before we redirect
- This guarantees the return value reaches the subprocess pipe, even if the user does something unusual with sys.stdout

### Why read stdin upfront?
- Prevents race between module-level `input()` calls and `solve(data)` parameter
- Makes stdin available to both legacy mode (via StringIO replacement) and return-value mode (via parameter)
- If the user reads stdin at module level AND defines `solve()`, solve() still receives the full input

### What about `input()` inside `solve()`?
- In return-value mode, `sys.stdin` is a StringIO with the full input, BUT module-level code may have already consumed it via `input()`
- Convention: if you define `solve(data)`, use the `data` parameter — don't use `input()` inside solve
- This is the same convention LeetCode uses

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| `solve()` returns `None` | Empty stdout → likely WRONG ANSWER |
| `solve()` raises exception | Propagates → non-zero exit → RUNTIME ERROR |
| `solve()` with no parameters | TypeError → RUNTIME ERROR (convention: solve takes 1 arg) |
| Module-level `sys.exit()` | Exits before solve() → no return value → empty output |
| Module has both prints AND `solve()` | Prints → stderr (debug), return value → stdout (judged) |
| No `solve()`, uses `print()` | Legacy mode — prints ARE the answer (backward compatible) |
| Solution imports other local files | Works — solution's directory is added to sys.path |

## Files Changed Summary

| File | Change |
|------|--------|
| `src/cses_cli/harness.py` | **NEW** — execution harness with auto-detection |
| `src/cses_cli/runner.py` | **MODIFIED** — invoke harness instead of solution directly |
| `README.md` | **MODIFIED** — add "Writing Solutions" section with both modes |
| `src/cses_cli/cli.py` | **MODIFIED** — add `cses howto` command with in-terminal guide |
| `missing_number.py` | **MODIFIED** — convert to `solve()` style as example |

## Testing Strategy

1. **Manual test (legacy mode):** Run existing solution without `solve()` → should work exactly as before
2. **Manual test (return-value mode):** Convert `missing_number.py` to `solve()` style with debug prints → prints should not affect verdict
3. **Unit tests (if added):** Test harness directly with mock solutions of both styles
