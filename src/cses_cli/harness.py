"""Execution harness for user solutions — supports return-value and legacy modes.

This script wraps the user's solution and auto-detects the execution mode:
- If the solution defines a `solve(data)` function → return-value mode
  (only the return value is judged; print() calls become debug output on stderr)
- If no `solve()` function → legacy mode (stdout is the answer, same as before)

Usage: python3 harness.py <solution_path>
"""

import importlib.util
import io
import os
import sys


def _format_result(result):
    """Format a solve() return value into a string for output."""
    if result is None:
        return ""
    if isinstance(result, (list, tuple)):
        return "\n".join(str(x) for x in result)
    return str(result)


def main():
    solution_path = sys.argv[1]

    # Read all input upfront before any module code can consume it
    input_data = sys.stdin.read()

    # Save real stdout via file descriptor duplication (survives sys.stdout replacement)
    real_stdout_fd = os.dup(1)
    real_stdout = os.fdopen(real_stdout_fd, "w")

    # Replace stdin with a StringIO so input() still works in legacy mode
    sys.stdin = io.StringIO(input_data)

    # Capture all print() calls into a buffer
    capture = io.StringIO()
    sys.stdout = capture

    # Load the user's solution module
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    solution_dir = os.path.dirname(os.path.abspath(solution_path))
    sys.path.insert(0, solution_dir)
    spec.loader.exec_module(module)

    if hasattr(module, "solve"):
        # RETURN-VALUE MODE: call solve(), judge only the return value
        result = module.solve(input_data)

        output = _format_result(result)
        if output:
            real_stdout.write(output)
            if not output.endswith("\n"):
                real_stdout.write("\n")

        # Route captured print() output to stderr (shown as debug in TUI)
        debug = capture.getvalue()
        if debug:
            sys.stderr.write(debug)
    else:
        # LEGACY MODE: captured stdout IS the answer
        real_stdout.write(capture.getvalue())

    real_stdout.flush()
    real_stdout.close()


if __name__ == "__main__":
    main()
