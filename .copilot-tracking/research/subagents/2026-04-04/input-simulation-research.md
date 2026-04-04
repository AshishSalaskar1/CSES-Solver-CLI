# Input Simulation Research for Python CP Test Runner

## Research Topics

1. Subprocess-based execution
2. Import-based (in-process) execution
3. The `main()` function contract
4. Separating answer output from debug output
5. How existing CP testing tools handle execution
6. Input reading patterns in Python CP
7. Timeout and resource management

---

## 1. Subprocess-Based Execution

### Core Pattern

The proven approach from `oj` (online-judge-tools) uses `subprocess.Popen` directly:

```python
proc = subprocess.Popen(
    command,
    stdin=stdin,           # file object or subprocess.PIPE
    stdout=subprocess.PIPE,
    stderr=sys.stderr,     # or subprocess.PIPE to capture
    preexec_fn=preexec_fn  # os.setsid for process group management
)
answer, _ = proc.communicate(input=input_data, timeout=timeout)
```

### Key Implementation Details from `oj`

- **stdin**: Opens the test input file with `open(path, 'rb')` and passes the file object directly as `stdin=inf` to `Popen`. Alternative: use `stdin=subprocess.PIPE` and pass data via `communicate(input=data)`.
- **stdout**: Always `subprocess.PIPE` — captured via `communicate()` as bytes.
- **stderr**: `sys.stderr` (passed through to terminal) — this is how oj lets debug prints show in the console.
- **Timeout**: Uses `proc.communicate(timeout=timeout)`. On `TimeoutExpired`, the process needs explicit killing.
- **Timing**: `time.perf_counter()` before/after the communicate call.
- **Memory**: Measured via GNU time (`/usr/bin/time -f '%M'`) which reports max RSS in KB. On Linux, parse the output file.

### `subprocess.run` vs `subprocess.Popen`

`subprocess.run` is a convenience wrapper but less flexible. Key differences:

- `run(timeout=...)` automatically kills the child and waits on `TimeoutExpired`, but you lose the ability to capture partial output easily.
- `Popen` + `communicate` gives more control over the lifecycle.
- `run` with `capture_output=True` sets `stdout=PIPE, stderr=PIPE` automatically.

**Recommendation**: Use `subprocess.run` for simplicity. It handles most cases:

```python
result = subprocess.run(
    [sys.executable, solution_path],
    input=test_input,       # str or bytes
    capture_output=True,
    timeout=time_limit,
    text=True               # work with strings
)
# result.stdout = answer
# result.stderr = debug output
# result.returncode = 0 for success
```

### Process Group Killing (Zombie Prevention)

From `oj`:

```python
preexec_fn = None
if os.name == 'posix':
    preexec_fn = os.setsid

proc = subprocess.Popen(command, ..., preexec_fn=preexec_fn)
try:
    answer, _ = proc.communicate(timeout=timeout)
except subprocess.TimeoutExpired:
    if preexec_fn is not None:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    else:
        proc.terminate()
```

Modern Python 3.11+ alternative: use `process_group=0` parameter to `Popen` instead of `preexec_fn=os.setsid`. This is safer in threaded contexts.

**Note**: `preexec_fn` is NOT SAFE with threads (per Python docs). Since our CLI is single-threaded, this is fine — but `start_new_session=True` is the modern equivalent:

```python
proc = subprocess.Popen(command, ..., start_new_session=True)
# then: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
```

### Pros and Cons

**Pros**:

- Full isolation — user code cannot crash the runner
- Real timeout enforcement (OS-level process kill)
- Memory isolation
- stderr/stdout separation is natural
- Works with all input reading patterns (`input()`, `sys.stdin.readline`, etc.)

**Cons**:

- Subprocess spawn overhead (~50-150ms per test case)
- Harder to inject debug utilities into user namespace
- Need to handle Python interpreter path correctly

---

## 2. Import-Based (In-Process) Execution

### Core Pattern

```python
import io
import sys

# Mock stdin
sys.stdin = io.StringIO(test_input)

# Capture stdout
captured = io.StringIO()
sys.stdout = captured

# Run user code
try:
    user_module.main()
finally:
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__

output = captured.getvalue()
```

### Important Considerations

- **`io.StringIO`** works with `input()` and `sys.stdin.readline()` correctly — it supports the full `TextIOBase` interface including `readline()`, iteration, etc.
- Both `input()` (which calls `sys.stdin.readline()`) and `for line in sys.stdin` work with StringIO.
- The pattern `input = sys.stdin.readline` also works since `StringIO.readline` has the same interface.
- **Thread safety**: `StringIO` is not thread-safe per Python docs, but fine for single-threaded execution.

### Timeout Implementation for In-Process

Signal-based (POSIX only):

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Time limit exceeded")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(time_limit_seconds)  # integer seconds only
try:
    user_module.main()
finally:
    signal.alarm(0)  # cancel
```

Limitations:

- `signal.alarm` only supports integer seconds (not sub-second precision).
- For sub-second, use `signal.setitimer(signal.ITIMER_REAL, timeout)` with `signal.SIGALRM`.
- Only works in the main thread.
- User code doing C extensions may not be interruptible.

### Pros and Cons

**Pros**:

- Fast — no subprocess overhead
- Can inject helpers (like `debug()`) into user namespace
- Easier to capture fine-grained output separation

**Cons**:

- User code can crash the runner (segfault, infinite memory, monkey-patching)
- No real memory isolation
- Signal-based timeout is fragile (C extensions, blocked syscalls)
- Must manually save/restore sys.stdin, sys.stdout, sys.stderr
- Concurrent test execution is problematic (shared global state)
- If user code calls `os._exit()`, the runner dies

**Recommendation**: Subprocess is strongly preferred for robustness. In-process is only suitable as an optional "fast mode" for trusted code.

---

## 3. The `main()` Function Contract

### How Existing CP Tools Handle This

All major CP testing tools (`oj`, `cf-tool`, `cpbooster`, `cptk`) treat the solution as a **standalone executable** that reads from stdin and writes to stdout. None of them impose a `main()` function contract.

- `oj`: Runs `python3 main.py` as a shell command via `subprocess.Popen`. User code is the entire file.
- `cf-tool`: Same approach — runs a configured command (`python3 %full%`). The file is the unit.
- `cpbooster`: Same — configurable run command per language.

### Contract Options Analysis

#### Option A: `main()` reads stdin, prints to stdout (standard CP style)

```python
def main():
    n = int(input())
    a = list(map(int, input().split()))
    print(max(a))
```

- **Most natural for CP programmers** — this is exactly how CSES/Codeforces solutions are written.
- Compatible with both subprocess and in-process execution.
- The `main()` wrapper helps with import-based testing (can call `main()` directly).
- The file can still work standalone with `if __name__ == "__main__": main()`.

#### Option B: `main()` takes input parameter, returns output

```python
def main(input_str: str) -> str:
    lines = input_str.strip().split('\n')
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    return str(max(a))
```

- **Unnatural for CP** — forces manual line parsing, loses `input()` convenience.
- Not how anyone writes CSES solutions.
- Would require users to learn a custom API.

#### Option C: `main()` reads stdin, returns answer string

```python
def main() -> str:
    n = int(input())
    a = list(map(int, input().split()))
    return str(max(a))
```

- Enables separation: return value = answer, `print()` calls = debug.
- **Unnatural** — real CP solutions use `print()` for output.
- Would not work when submitted to CSES as-is.

### Recommendation

**Option A is the clear winner.**

The contract should be:

1. User writes solution with a `main()` function.
2. `main()` uses `input()` / `print()` normally (standard CP style).
3. The file includes `if __name__ == "__main__": main()`.
4. The CLI runs the file as a subprocess: `python3 solution.py < input.txt`.
5. All stdout = answer output. Debug output goes to stderr via `print(..., file=sys.stderr)`.

This means the solution file is simultaneously:

- Runnable standalone: `python3 solution.py < input.txt`
- Submittable to CSES directly (with or without the `main()` wrapper)
- Testable by the CLI

---

## 4. Separating Answer Output from Debug Output

### The Industry Standard: All stdout Is the Answer

Every major CP tool treats **all stdout as the answer**. None attempt to separate "debug prints" from "answer prints" within stdout.

- `oj`: stdout = answer, stderr goes to terminal.
- `cf-tool`: stdout = answer, stderr goes to `os.Stderr`.
- `cpbooster`: Same pattern.

### Practical Approaches for Debug Separation

#### Approach 1: stderr Convention (Recommended)

The user convention:

```python
import sys

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    n = int(input())
    debug(f"n = {n}")  # visible in terminal, not checked
    print(n * 2)       # this is the answer
```

The CLI captures:

- `stdout` → compared against expected output
- `stderr` → displayed to user as debug info (optional)

**This is the standard practice in competitive programming.** CSES and other judges ignore stderr.

#### Approach 2: Injected `debug()` Function

The CLI could inject a `debug()` function by wrapping the execution:

```python
# Prepend to user's file or inject via import
import sys
def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
```

But this adds complexity. Better to document the convention and optionally provide a template.

#### Approach 3: Return-Value Separation (Option C contract)

Only possible with the non-standard `main() -> str` contract. Not recommended.

#### Approach 4: Simply Don't Separate

All stdout is the answer. If the user prints debug info to stdout, it goes into the comparison and causes WA. This is how real judges work.

### Recommendation

**Use stderr convention (Approach 1)**:

- `stdout` = answer (captured, compared)
- `stderr` = debug output (captured separately, shown to user)
- The CLI should capture both and display stderr in a "Debug Output" section
- Provide a template with a `debug()` helper

Implementation:

```python
result = subprocess.run(
    [sys.executable, solution_path],
    input=test_input,
    capture_output=True,  # captures both stdout and stderr
    timeout=time_limit,
    text=True
)
answer = result.stdout
debug_output = result.stderr
```

---

## 5. How Existing CP Testing Tools Handle Execution

### `oj` (online-judge-tools) — Python, 1.1k stars

**Architecture**: Subprocess-based. Runs the solution as a shell command.

**Execution** (`utils.exec_command`):

- `subprocess.Popen(command, stdin=file_obj, stdout=PIPE, stderr=sys.stderr)`
- `proc.communicate(timeout=timeout)` for output capture
- Returns `{'answer': bytes, 'elapsed': float, 'memory': Optional[float]}`

**Timeout**: via `communicate(timeout=...)`. On expiry, uses `os.killpg` (process group) or `proc.terminate`.

**Memory**: Measured externally via GNU time (`/usr/bin/time -f '%M'`), reported in KB (converted to MB).

**Comparison**: Multiple modes — exact match, CRLF-insensitive, ignore-spaces, floating-point tolerance, custom judge command.

**Key design**: All stdout is the answer. stderr passes through to console.

### `cf-tool` (xalanq/cf-tool) — Go, popular Codeforces tool

**Architecture**: Subprocess-based. Runs configured command.

**Execution** (`cmd/test.go judge()`):

- `exec.Command(cmds[0], cmds[1:]...)` with `stdin=file`, `stdout=buffer`, `stderr=os.Stderr`
- Memory tracked in background goroutine using `gopsutil/process` (RSS polling)
- Timing via `cmd.ProcessState.UserTime()`

**Comparison**: Trims whitespace per line, string equality. Shows diff on failure.

**Key design**: Runs solution as a command. Test input/output stored as `in1.txt`/`ans1.txt`.

### `cpbooster` — TypeScript, 168 stars

**Architecture**: Subprocess-based (Node.js `child_process`).

**Key features**: Configurable run commands per language. Supports AC/WA/TLE/RTE/CE verdicts. Debug mode with `-d` flag. Memory tracking via GNU time (same approach as oj).

### `cptk` (RealA10N/cptk) — Python, 4 stars

Supports multiple judges including Kattis. Uses subprocess execution with configurable commands.

### No CSES-Specific CLI Tools Found

No dedicated CSES testing CLI tools exist on GitHub. `tyora` (madeddie/tyora) interacts with mooc.fi CSES instance for course submissions but does not do local testing.

---

## 6. Input Reading Patterns in Python CP

### Pattern 1: Built-in `input()`

```python
n = int(input())
a = list(map(int, input().split()))
```

- `input()` calls `sys.stdin.readline()` and strips trailing newline.
- **Works with both** subprocess (stdin pipe) and in-process (`io.StringIO` mock).
- This is the most common pattern for CSES Python solutions.

### Pattern 2: Fast `sys.stdin.readline`

```python
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))
```

- Overrides `input` at module level. Common optimization for performance.
- **Subprocess**: Works perfectly — `sys.stdin` is the pipe.
- **In-process**: Works if `sys.stdin` is replaced with `io.StringIO` before the module is loaded. The `input = sys.stdin.readline` binding captures the current `sys.stdin` at import time, so `sys.stdin` must be mocked **before** importing the user module.
  - **Caveat**: If the user does `input = sys.stdin.readline` at module scope (outside `main()`), and you mock `sys.stdin` after import, the binding points to the old stdin. If inside `main()`, the binding captures the mocked stdin.
  - **This is why subprocess is safer** — no binding timing issues.

### Pattern 3: Read all at once

```python
import sys
data = sys.stdin.read().split()
idx = 0

def rd():
    global idx
    idx += 1
    return data[idx - 1]
```

- Fast for large inputs. Reads everything in one syscall.
- **Subprocess**: Works fine.
- **In-process**: Works with `io.StringIO` since `StringIO.read()` works correctly.

### Pattern 4: `sys.stdin` iterator

```python
import sys
for line in sys.stdin:
    process(line)
```

- **Subprocess**: Works.
- **In-process**: Works — `io.StringIO` is iterable.

### Compatibility Matrix

| Pattern | Subprocess | In-Process (StringIO) | Notes |
|---|---|---|---|
| `input()` | Works | Works | Most common |
| `input = sys.stdin.readline` (in `main()`) | Works | Works | Binding captured after mock |
| `input = sys.stdin.readline` (module scope) | Works | **Issue** | Binding captured before mock |
| `sys.stdin.read()` | Works | Works |  |
| `for line in sys.stdin` | Works | Works |  |

**Conclusion**: Subprocess approach has no compatibility issues. In-process approach has a subtle bug with module-level `sys.stdin.readline` rebinding.

---

## 7. Timeout and Resource Management

### Timeout with `subprocess.run`

```python
try:
    result = subprocess.run(
        [sys.executable, solution_path],
        input=test_input,
        capture_output=True,
        timeout=time_limit,
        text=True
    )
except subprocess.TimeoutExpired as e:
    # e.stdout may contain partial output (often None with run())
    # e.stderr may contain partial debug output
    status = "TLE"
```

**Behavior**: `subprocess.run` with `timeout` will:

1. Call `communicate(timeout=timeout)` internally.
2. On expiry, kill the child process and wait for it.
3. Re-raise `TimeoutExpired` after cleanup.

### Timeout with `Popen` (More Control)

```python
import subprocess, signal, os, time

begin = time.perf_counter()
proc = subprocess.Popen(
    [sys.executable, solution_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    start_new_session=True  # modern alternative to preexec_fn=os.setsid
)
try:
    stdout, stderr = proc.communicate(
        input=test_input.encode(),
        timeout=time_limit
    )
except subprocess.TimeoutExpired:
    # Kill the entire process group to prevent zombies
    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    stdout, stderr = proc.communicate()  # collect any remaining output
    elapsed = time.perf_counter() - begin
    # status = TLE
```

### Memory Tracking on Linux

#### Option 1: GNU time (used by `oj` and `cpbooster`)

```bash
/usr/bin/time -f '%M' -o /tmp/mem.txt python3 solution.py < input.txt
```

`%M` = maximum resident set size in KB. Parse the output file.

**Integration**:

```python
import tempfile
with tempfile.NamedTemporaryFile(delete=True, mode='r') as memfile:
    command = ['/usr/bin/time', '-f', '%M', '-o', memfile.name, '--',
               sys.executable, solution_path]
    proc = subprocess.Popen(command, ...)
    # ... run and wait ...
    memory_kb = int(memfile.read().strip())
    memory_mb = memory_kb / 1024
```

#### Option 2: `resource` module (after process completes)

```python
import resource
# Only measures the CURRENT process and children, not a subprocess
# Use resource.getrusage(resource.RUSAGE_CHILDREN) after wait()
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
memory_kb = usage.ru_maxrss  # KB on Linux, bytes on macOS
```

**Caveat**: `RUSAGE_CHILDREN` reports cumulative max RSS across all children, not per-child. If running tests sequentially, this is the max across all tests run so far (not resettable).

#### Option 3: `/proc/[pid]/status` polling (cf-tool approach)

Poll `VmRSS` from `/proc/[pid]/status` during execution. More accurate but requires a background thread. This is what `cf-tool` does via gopsutil.

**Recommendation**: GNU time is the simplest and most reliable approach. `resource.RUSAGE_CHILDREN` is a simpler fallback but less precise.

### Execution Time Measurement

```python
import time
start = time.perf_counter()
# ... run subprocess ...
elapsed = time.perf_counter() - start
```

`time.perf_counter()` provides the highest resolution wall-clock timer. For process CPU time, check `proc.ProcessState.UserTime()` equivalent — not directly available in Python subprocess but can be approximated via `resource.getrusage(RUSAGE_CHILDREN).ru_utime`.

### Handling TLE Gracefully

```python
def run_test(solution_path, test_input, time_limit):
    try:
        result = subprocess.run(
            [sys.executable, solution_path],
            input=test_input,
            capture_output=True,
            timeout=time_limit,
            text=True
        )
        if result.returncode != 0:
            return {"status": "RE", "stderr": result.stderr}
        return {
            "status": "OK",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"status": "TLE"}
```

---

## Recommended Approach Summary

### Architecture Decision: Subprocess

Use **subprocess execution** as the primary (and only) approach. Reasons:

1. All major CP tools use subprocess — it is the proven pattern.
2. Full process isolation protects the CLI from user code crashes.
3. Real timeout enforcement via OS-level process kill.
4. No subtle bugs with `sys.stdin` rebinding.
5. Natural stderr/stdout separation.
6. No need for `main()` function — can run files that use top-level code too.

### The Contract

1. User writes a Python file (e.g., `solution.py`).
2. Solution uses `input()` / `print()` for I/O (standard CP style).
3. A `main()` function is recommended but not strictly required by the runner.
4. The CLI runs: `python3 solution.py < input.txt` and captures stdout.
5. Debug output convention: `print(..., file=sys.stderr)`.

### Core Implementation Skeleton

```python
import subprocess
import sys
import time

def run_solution(solution_path, test_input, time_limit=2.0):
    """Run a CP solution against test input.

    Returns dict with keys: status, stdout, stderr, elapsed, returncode
    """
    start = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, str(solution_path)],
            input=test_input,
            capture_output=True,
            timeout=time_limit,
            text=True,
        )
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            return {
                "status": "RE",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "elapsed": elapsed,
                "returncode": result.returncode,
            }
        return {
            "status": "OK",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed": elapsed,
            "returncode": 0,
        }
    except subprocess.TimeoutExpired as e:
        elapsed = time.perf_counter() - start
        return {
            "status": "TLE",
            "stdout": (e.stdout or "").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""),
            "stderr": (e.stderr or "").decode() if isinstance(e.stderr, bytes) else (e.stderr or ""),
            "elapsed": elapsed,
            "returncode": None,
        }
```

### Comparison Logic

After execution, compare `result["stdout"]` with expected output. Comparison modes from oj:

- **Exact match** (default for competitive programming)
- **Whitespace-insensitive**: strip trailing whitespace per line, ignore trailing newlines
- **Float tolerance**: for problems with floating-point answers

The simplest and most useful default is whitespace-insensitive comparison:

```python
def compare_output(actual, expected):
    """Compare outputs ignoring trailing whitespace and blank lines."""
    actual_lines = actual.rstrip().splitlines()
    expected_lines = expected.rstrip().splitlines()
    if len(actual_lines) != len(expected_lines):
        return False
    return all(
        a.rstrip() == e.rstrip()
        for a, e in zip(actual_lines, expected_lines)
    )
```

---

## Follow-On Questions

1. Should the CLI discover the Python interpreter path automatically or use a configured `python3`?
   - Recommendation: Use `sys.executable` (the same Python running the CLI) by default, with a config override.

2. Should test cases be stored as separate `.in`/`.out` files (like oj) or in a structured format (JSON/YAML)?
   - See existing CSES problem scraping code for the actual format in use.

3. Should the CLI support running non-Python solutions (C++, Java) via configurable commands?
   - The subprocess approach makes this trivial to add later.

---

## Key References

- `oj` source: `onlinejudge_command/utils.py` — `exec_command()` function
- `oj` source: `onlinejudge_command/subcommand/test.py` — test orchestration
- `cf-tool` source: `cmd/test.go` — `judge()` function
- Python docs: `subprocess` module — Popen, run, communicate, TimeoutExpired
- Python docs: `io.StringIO` — in-memory text stream
- Python docs: `signal` module — SIGALRM for in-process timeout
