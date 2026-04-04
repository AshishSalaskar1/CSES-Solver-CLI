"""Reference solutions for CSES Introductory Problems."""

from __future__ import annotations

from collections import Counter
from itertools import permutations
import heapq


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id.

    Returns the expected output as a string, or None if no
    reference solution is available for the given task_id.
    """
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1068 - Weird Algorithm
# ---------------------------------------------------------------------------
def _solve_1068(input_data: str) -> str:
    n = int(input_data.strip())
    result = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = n * 3 + 1
        result.append(n)
    return " ".join(map(str, result))


# ---------------------------------------------------------------------------
# 1083 - Missing Number
# ---------------------------------------------------------------------------
def _solve_1083(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    nums = list(map(int, lines[1].split()))
    return str(n * (n + 1) // 2 - sum(nums))


# ---------------------------------------------------------------------------
# 1069 - Repetitions
# ---------------------------------------------------------------------------
def _solve_1069(input_data: str) -> str:
    s = input_data.strip()
    best = cur = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 1
    return str(best)


# ---------------------------------------------------------------------------
# 1094 - Increasing Array
# ---------------------------------------------------------------------------
def _solve_1094(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    a = list(map(int, lines[1].split()))
    total = 0
    prev = a[0]
    for v in a[1:]:
        if v < prev:
            total += prev - v
        else:
            prev = v
    return str(total)


# ---------------------------------------------------------------------------
# 1070 - Permutations  (Beautiful permutation)
# ---------------------------------------------------------------------------
def _solve_1070(input_data: str) -> str:
    n = int(input_data.strip())
    if n == 1:
        return "1"
    if n <= 3:
        return "NO SOLUTION"
    # Evens first, then odds — guarantees |adj diff| >= 2
    result = list(range(2, n + 1, 2)) + list(range(1, n + 1, 2))
    return " ".join(map(str, result))


# ---------------------------------------------------------------------------
# 1071 - Number Spiral
# ---------------------------------------------------------------------------
def _solve_1071(input_data: str) -> str:
    lines = input_data.split("\n")
    t = int(lines[0])
    out = []
    for i in range(1, t + 1):
        y, x = map(int, lines[i].split())
        k = max(y, x)
        base = (k - 1) * (k - 1)
        if k & 1:  # odd diagonal: right along row k, then up column k
            val = base + x if y == k else base + k + (k - y)
        else:       # even diagonal: down column k, then left along row k
            val = base + y if x == k else base + k + (k - x)
        out.append(str(val))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1072 - Two Knights
# ---------------------------------------------------------------------------
def _solve_1072(input_data: str) -> str:
    n = int(input_data.strip())
    out = []
    for k in range(1, n + 1):
        total = k * k * (k * k - 1) // 2
        # Each 2x3 rect has 2 attacking pairs; count of 2x3 + 3x2 rects:
        attacking = 4 * (k - 1) * (k - 2)
        out.append(str(total - attacking))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1092 - Two Sets
# ---------------------------------------------------------------------------
def _solve_1092(input_data: str) -> str:
    n = int(input_data.strip())
    total = n * (n + 1) // 2
    if total % 2 != 0:
        return "NO"
    target = total // 2
    set1: list[int] = []
    set2: list[int] = []
    for i in range(n, 0, -1):
        if i <= target:
            set1.append(i)
            target -= i
        else:
            set2.append(i)
    lines = ["YES"]
    lines.append(str(len(set1)))
    lines.append(" ".join(map(str, set1)))
    lines.append(str(len(set2)))
    lines.append(" ".join(map(str, set2)))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 1617 - Bit Strings
# ---------------------------------------------------------------------------
def _solve_1617(input_data: str) -> str:
    n = int(input_data.strip())
    return str(pow(2, n, 10**9 + 7))


# ---------------------------------------------------------------------------
# 1618 - Trailing Zeros
# ---------------------------------------------------------------------------
def _solve_1618(input_data: str) -> str:
    n = int(input_data.strip())
    count = 0
    power = 5
    while power <= n:
        count += n // power
        power *= 5
    return str(count)


# ---------------------------------------------------------------------------
# 1754 - Coin Piles
# ---------------------------------------------------------------------------
def _solve_1754(input_data: str) -> str:
    lines = input_data.split("\n")
    t = int(lines[0])
    out = []
    for i in range(1, t + 1):
        a, b = map(int, lines[i].split())
        if (a + b) % 3 == 0 and min(a, b) * 2 >= max(a, b):
            out.append("YES")
        else:
            out.append("NO")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1755 - Palindrome Reorder
# ---------------------------------------------------------------------------
def _solve_1755(input_data: str) -> str:
    s = input_data.strip()
    counts = Counter(s)
    odd_count = sum(1 for cnt in counts.values() if cnt % 2 == 1)
    if odd_count > 1:
        return "NO SOLUTION"
    half = []
    middle = ""
    for c in sorted(counts):
        cnt = counts[c]
        half.append(c * (cnt // 2))
        if cnt % 2 == 1:
            middle = c
    left = "".join(half)
    return left + middle + left[::-1]


# ---------------------------------------------------------------------------
# 2205 - Gray Code
# ---------------------------------------------------------------------------
def _solve_2205(input_data: str) -> str:
    n = int(input_data.strip())
    fmt = f"0{n}b"
    return "\n".join(format(i ^ (i >> 1), fmt) for i in range(1 << n))


# ---------------------------------------------------------------------------
# 2165 - Tower of Hanoi
# ---------------------------------------------------------------------------
def _solve_2165(input_data: str) -> str:
    n = int(input_data.strip())
    moves: list[str] = []

    def hanoi(disks: int, src: int, dst: int, aux: int) -> None:
        if disks == 0:
            return
        hanoi(disks - 1, src, aux, dst)
        moves.append(f"{src} {dst}")
        hanoi(disks - 1, aux, dst, src)

    hanoi(n, 1, 3, 2)
    return str(len(moves)) + "\n" + "\n".join(moves)


# ---------------------------------------------------------------------------
# 1622 - Creating Strings
# ---------------------------------------------------------------------------
def _solve_1622(input_data: str) -> str:
    s = input_data.strip()
    perms = sorted(set("".join(p) for p in permutations(s)))
    return str(len(perms)) + "\n" + "\n".join(perms)


# ---------------------------------------------------------------------------
# 1623 - Apple Division
# ---------------------------------------------------------------------------
def _solve_1623(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    w = list(map(int, lines[1].split()))
    total = sum(w)
    best = total
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += w[i]
        diff = abs(total - 2 * s)
        if diff < best:
            best = diff
    return str(best)


# ---------------------------------------------------------------------------
# 1624 - Chessboard and Queens
# ---------------------------------------------------------------------------
def _solve_1624(input_data: str) -> str:
    board = input_data.split("\n")
    count = 0
    cols = [False] * 8
    diag1 = [False] * 15   # row + col
    diag2 = [False] * 15   # row - col + 7

    def backtrack(row: int) -> None:
        nonlocal count
        if row == 8:
            count += 1
            return
        for col in range(8):
            if board[row][col] == '*':
                continue
            if cols[col] or diag1[row + col] or diag2[row - col + 7]:
                continue
            cols[col] = diag1[row + col] = diag2[row - col + 7] = True
            backtrack(row + 1)
            cols[col] = diag1[row + col] = diag2[row - col + 7] = False

    backtrack(0)
    return str(count)


# ---------------------------------------------------------------------------
# 2431 - Digit Queries
# ---------------------------------------------------------------------------
def _solve_2431(input_data: str) -> str:
    lines = input_data.split("\n")
    q = int(lines[0])
    out = []
    for i in range(1, q + 1):
        k = int(lines[i])
        digits = 1
        count = 9
        start = 1
        while k > digits * count:
            k -= digits * count
            digits += 1
            count *= 10
            start *= 10
        num = start + (k - 1) // digits
        digit_idx = (k - 1) % digits
        out.append(str(num)[digit_idx])
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1743 - String Reorder
# ---------------------------------------------------------------------------
def _solve_1743(input_data: str) -> str:
    s = input_data.strip()
    n = len(s)
    counts = Counter(s)
    if max(counts.values()) > (n + 1) // 2:
        return "-1"
    # Greedy: always pick the most-frequent char different from last placed
    heap = [(-cnt, ch) for ch, cnt in counts.items()]
    heapq.heapify(heap)
    result: list[str] = []
    while heap:
        cnt, ch = heapq.heappop(heap)
        if result and result[-1] == ch:
            if not heap:
                return "-1"
            cnt2, ch2 = heapq.heappop(heap)
            result.append(ch2)
            cnt2 += 1  # used one (counts are negative)
            if cnt2 < 0:
                heapq.heappush(heap, (cnt2, ch2))
            heapq.heappush(heap, (cnt, ch))
        else:
            result.append(ch)
            cnt += 1
            if cnt < 0:
                heapq.heappush(heap, (cnt, ch))
    return "".join(result)


# ---------------------------------------------------------------------------
# 1625 - Grid Paths
# ---------------------------------------------------------------------------
def _solve_1625(input_data: str) -> str:
    desc = input_data.strip()
    N = 7
    DR = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
    DC = {'U': 0, 'D': 0, 'L': -1, 'R': 1}
    ALL_DIRS = "UDLR"

    visited = [[False] * N for _ in range(N)]
    count = 0

    def _free(r: int, c: int) -> bool:
        return 0 <= r < N and 0 <= c < N and not visited[r][c]

    def dfs(step: int, r: int, c: int) -> None:
        nonlocal count
        if r == 6 and c == 0:
            if step == 48:
                count += 1
            return
        if step == 48:
            return

        # Pruning: if opposite neighbours are both free but the
        # perpendicular pair are both blocked, we would split the
        # unvisited region — prune immediately.
        u = _free(r - 1, c)
        d = _free(r + 1, c)
        le = _free(r, c - 1)
        ri = _free(r, c + 1)
        if u and d and not le and not ri:
            return
        if le and ri and not u and not d:
            return

        moves = desc[step] if desc[step] != '?' else ALL_DIRS
        for m in moves:
            nr, nc = r + DR[m], c + DC[m]
            if _free(nr, nc):
                visited[nr][nc] = True
                dfs(step + 1, nr, nc)
                visited[nr][nc] = False

    visited[0][0] = True
    dfs(0, 0, 0)
    return str(count)


# ---------------------------------------------------------------------------
# Newer problems — exact specifications unavailable, return None
# ---------------------------------------------------------------------------
def _not_available(input_data: str) -> None:
    return None


# ---------------------------------------------------------------------------
# Solution dispatch table
# ---------------------------------------------------------------------------
SOLUTIONS: dict[int, callable] = {
    1068: _solve_1068,  # Weird Algorithm
    1083: _solve_1083,  # Missing Number
    1069: _solve_1069,  # Repetitions
    1094: _solve_1094,  # Increasing Array
    1070: _solve_1070,  # Permutations
    1071: _solve_1071,  # Number Spiral
    1072: _solve_1072,  # Two Knights
    1092: _solve_1092,  # Two Sets
    1617: _solve_1617,  # Bit Strings
    1618: _solve_1618,  # Trailing Zeros
    1754: _solve_1754,  # Coin Piles
    1755: _solve_1755,  # Palindrome Reorder
    2205: _solve_2205,  # Gray Code
    2165: _solve_2165,  # Tower of Hanoi
    1622: _solve_1622,  # Creating Strings
    1623: _solve_1623,  # Apple Division
    1624: _solve_1624,  # Chessboard and Queens
    2431: _solve_2431,  # Digit Queries
    1743: _solve_1743,  # String Reorder
    1625: _solve_1625,  # Grid Paths
    # Newer problems — solutions not available
    3399: _not_available,  # Raab Game I
    3419: _not_available,  # Mex Grid Construction
    3217: _not_available,  # Knight Moves Grid
    3311: _not_available,  # Grid Coloring I
}
