"""Reference solutions for CSES Dynamic Programming problems."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from functools import lru_cache

MOD = 10**9 + 7


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
# 1633 - Dice Combinations
# ---------------------------------------------------------------------------
def _solve_1633(input_data: str) -> str:
    n = int(input_data.strip())
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(1, 7):
            if i >= j:
                dp[i] = (dp[i] + dp[i - j]) % MOD
    return str(dp[n])


# ---------------------------------------------------------------------------
# 1634 - Minimizing Coins
# ---------------------------------------------------------------------------
def _solve_1634(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    coins = list(map(int, lines[1].split()))
    INF = float("inf")
    dp = [INF] * (x + 1)
    dp[0] = 0
    for i in range(1, x + 1):
        for c in coins:
            if i >= c and dp[i - c] < INF:
                dp[i] = min(dp[i], dp[i - c] + 1)
    return str(dp[x] if dp[x] < INF else -1)


# ---------------------------------------------------------------------------
# 1635 - Coin Combinations I  (order matters)
# ---------------------------------------------------------------------------
def _solve_1635(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    coins = list(map(int, lines[1].split()))
    dp = [0] * (x + 1)
    dp[0] = 1
    for i in range(1, x + 1):
        for c in coins:
            if i >= c:
                dp[i] = (dp[i] + dp[i - c]) % MOD
    return str(dp[x])


# ---------------------------------------------------------------------------
# 1636 - Coin Combinations II  (order doesn't matter)
# ---------------------------------------------------------------------------
def _solve_1636(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    coins = list(map(int, lines[1].split()))
    dp = [0] * (x + 1)
    dp[0] = 1
    for c in coins:
        for i in range(c, x + 1):
            dp[i] = (dp[i] + dp[i - c]) % MOD
    return str(dp[x])


# ---------------------------------------------------------------------------
# 1637 - Removing Digits
# ---------------------------------------------------------------------------
def _solve_1637(input_data: str) -> str:
    n = int(input_data.strip())
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        best = n  # upper bound
        tmp = i
        while tmp > 0:
            d = tmp % 10
            if d > 0:
                best = min(best, dp[i - d] + 1)
            tmp //= 10
        dp[i] = best
    return str(dp[n])


# ---------------------------------------------------------------------------
# 1638 - Grid Paths  (n×n grid, right/down, obstacles)
# ---------------------------------------------------------------------------
def _solve_1638(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    grid = [lines[i + 1] for i in range(n)]
    if grid[0][0] == "*":
        return "0"
    dp = [[0] * n for _ in range(n)]
    dp[0][0] = 1
    for i in range(n):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            if grid[i][j] == "*":
                continue
            val = 0
            if i > 0:
                val += dp[i - 1][j]
            if j > 0:
                val += dp[i][j - 1]
            dp[i][j] = val % MOD
    return str(dp[n - 1][n - 1])


# ---------------------------------------------------------------------------
# 1158 - Book Shop  (0/1 knapsack)
# ---------------------------------------------------------------------------
def _solve_1158(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    prices = list(map(int, lines[1].split()))
    pages = list(map(int, lines[2].split()))
    dp = [0] * (x + 1)
    for i in range(n):
        h = prices[i]
        s = pages[i]
        for j in range(x, h - 1, -1):
            if dp[j - h] + s > dp[j]:
                dp[j] = dp[j - h] + s
    return str(dp[x])


# ---------------------------------------------------------------------------
# 1746 - Array Description
# ---------------------------------------------------------------------------
def _solve_1746(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    # dp[v] = ways where current position has value v  (1-indexed, 0 unused)
    dp = [0] * (m + 2)  # indices 0 .. m+1 as sentinels
    if a[0] != 0:
        dp[a[0]] = 1
    else:
        for v in range(1, m + 1):
            dp[v] = 1
    for i in range(1, n):
        ndp = [0] * (m + 2)
        if a[i] != 0:
            v = a[i]
            for dv in (v - 1, v, v + 1):
                if 1 <= dv <= m:
                    ndp[v] = (ndp[v] + dp[dv]) % MOD
        else:
            for v in range(1, m + 1):
                for dv in (v - 1, v, v + 1):
                    if 1 <= dv <= m:
                        ndp[v] = (ndp[v] + dp[dv]) % MOD
        dp = ndp
    return str(sum(dp[1 : m + 1]) % MOD)


# ---------------------------------------------------------------------------
# 2413 - Counting Towers
# ---------------------------------------------------------------------------
def _solve_2413(input_data: str) -> str:
    lines = input_data.split("\n")
    t = int(lines[0])
    queries = [int(lines[i + 1]) for i in range(t)]
    max_n = max(queries) if queries else 1
    # Two states per row:
    #   f[n] = ways where top row is two independent 1-wide columns
    #   g[n] = ways where top row is one 2-wide merged block
    # Recurrence:
    #   f[n] = 4*f[n-1] + g[n-1]
    #   g[n] = f[n-1] + 2*g[n-1]
    f = [0] * (max_n + 1)
    g = [0] * (max_n + 1)
    f[1] = 1
    g[1] = 1
    for i in range(2, max_n + 1):
        f[i] = (4 * f[i - 1] + g[i - 1]) % MOD
        g[i] = (f[i - 1] + 2 * g[i - 1]) % MOD
    results = []
    for q in queries:
        results.append(str((f[q] + g[q]) % MOD))
    return "\n".join(results)


# ---------------------------------------------------------------------------
# 1639 - Edit Distance
# ---------------------------------------------------------------------------
def _solve_1639(input_data: str) -> str:
    lines = input_data.split("\n")
    s = lines[0]
    t = lines[1]
    n, m = len(s), len(t)
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        ndp = [0] * (m + 1)
        ndp[0] = i
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                ndp[j] = dp[j - 1]
            else:
                ndp[j] = 1 + min(dp[j - 1], dp[j], ndp[j - 1])
        dp = ndp
    return str(dp[m])


# ---------------------------------------------------------------------------
# 3403 - Longest Common Subsequence
# ---------------------------------------------------------------------------
def _solve_3403(input_data: str) -> str:
    lines = input_data.split("\n")
    s = lines[0]
    t = lines[1]
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # Backtrack to recover the actual subsequence
    lcs: list[str] = []
    i, j = n, m
    while i > 0 and j > 0:
        if s[i - 1] == t[j - 1]:
            lcs.append(s[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(lcs))


# ---------------------------------------------------------------------------
# 1744 - Rectangle Cutting
# ---------------------------------------------------------------------------
def _solve_1744(input_data: str) -> str:
    a, b = map(int, input_data.strip().split())
    dp = [[0] * (b + 1) for _ in range(a + 1)]
    for i in range(1, a + 1):
        for j in range(1, b + 1):
            if i == j:
                dp[i][j] = 0
            else:
                best = i + j  # loose upper bound
                for k in range(1, i):
                    val = dp[k][j] + dp[i - k][j] + 1
                    if val < best:
                        best = val
                for k in range(1, j):
                    val = dp[i][k] + dp[i][j - k] + 1
                    if val < best:
                        best = val
                dp[i][j] = best
    return str(dp[a][b])


# ---------------------------------------------------------------------------
# 1745 - Money Sums
# ---------------------------------------------------------------------------
def _solve_1745(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    coins = list(map(int, lines[1].split()))
    # Bitset DP using Python arbitrary-precision int
    bits = 1  # bit 0 = sum 0 reachable
    for c in coins:
        bits |= bits << c
    total = sum(coins)
    sums = []
    for i in range(1, total + 1):
        if bits >> i & 1:
            sums.append(str(i))
    return str(len(sums)) + "\n" + " ".join(sums)


# ---------------------------------------------------------------------------
# 1097 - Removal Game
# ---------------------------------------------------------------------------
def _solve_1097(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    # dp[i][j] = max score-difference the current player can achieve on a[i..j]
    # Use two 1-D rows (current length and previous length) to save memory.
    # dp_prev[i] corresponds to intervals of length (l-1),
    # dp_cur[i]  corresponds to intervals of length l starting at i.
    dp_prev = list(a)  # length-1 intervals: dp[i][i] = a[i]
    for length in range(2, n + 1):
        dp_cur = [0] * (n - length + 1)
        for i in range(n - length + 1):
            j = i + length - 1
            # take left:  a[i] - dp[i+1][j]  (dp_prev at index i+1 if length-1)
            # take right: a[j] - dp[i][j-1]  (dp_prev at index i   if length-1)
            take_left = a[i] - dp_prev[i + 1]
            take_right = a[j] - dp_prev[i]
            dp_cur[i] = max(take_left, take_right)
        dp_prev = dp_cur
    total = sum(a)
    diff = dp_prev[0]
    return str((total + diff) // 2)


# ---------------------------------------------------------------------------
# 1093 - Two Sets II
# ---------------------------------------------------------------------------
def _solve_1093(input_data: str) -> str:
    n = int(input_data.strip())
    total = n * (n + 1) // 2
    if total % 2 == 1:
        return "0"
    target = total // 2
    dp = [0] * (target + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(target, i - 1, -1):
            dp[j] = (dp[j] + dp[j - i]) % MOD
    inv2 = pow(2, MOD - 2, MOD)
    return str(dp[target] * inv2 % MOD)


# ---------------------------------------------------------------------------
# 1145 - Increasing Subsequence  (LIS length, O(n log n))
# ---------------------------------------------------------------------------
def _solve_1145(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    tails: list[int] = []
    for x in a:
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return str(len(tails))


# ---------------------------------------------------------------------------
# 1140 - Projects
# ---------------------------------------------------------------------------
def _solve_1140(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    projects = []
    for i in range(1, n + 1):
        a_i, b_i, p_i = map(int, lines[i].split())
        projects.append((b_i, a_i, p_i))
    projects.sort()
    ends = [p[0] for p in projects]
    dp = [0] * (n + 1)
    for i in range(n):
        dp[i + 1] = dp[i]  # skip project i
        start_i = projects[i][1]
        # last project whose end < start_i
        j = bisect_right(ends, start_i - 1, 0, i)
        dp[i + 1] = max(dp[i + 1], projects[i][2] + dp[j])
    return str(dp[n])


# ---------------------------------------------------------------------------
# 1653 - Elevator Rides  (bitmask DP)
# ---------------------------------------------------------------------------
def _solve_1653(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    w = list(map(int, lines[1].split()))
    full = 1 << n
    # dp[mask] = (min_rides, min_weight_in_last_ride)
    INF_RIDES = n + 2
    dp_rides = [INF_RIDES] * full
    dp_weight = [0] * full
    dp_rides[0] = 1
    dp_weight[0] = 0
    for mask in range(full):
        cr, cw = dp_rides[mask], dp_weight[mask]
        if cr >= INF_RIDES:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            nmask = mask | (1 << i)
            if cw + w[i] <= x:
                nr, nw = cr, cw + w[i]
            else:
                nr, nw = cr + 1, w[i]
            if nr < dp_rides[nmask] or (
                nr == dp_rides[nmask] and nw < dp_weight[nmask]
            ):
                dp_rides[nmask] = nr
                dp_weight[nmask] = nw
    return str(dp_rides[full - 1])


# ---------------------------------------------------------------------------
# 2181 - Counting Tilings  (profile / broken-profile DP)
# ---------------------------------------------------------------------------
def _solve_2181(input_data: str) -> str:
    n, m = map(int, input_data.strip().split())
    if n * m % 2 == 1:
        return "0"
    # Use smaller dimension for bitmask
    if n > m:
        n, m = m, n
    # Process m columns; mask is n bits indicating which rows protrude
    # from previous column into current one via a horizontal domino.
    # Precompute all transitions: mask -> list of next_masks
    def build_transitions(rows: int) -> list[list[int]]:
        trans: list[list[int]] = [[] for _ in range(1 << rows)]
        def fill(row: int, in_mask: int, out_mask: int) -> None:
            if row == rows:
                trans[in_mask].append(out_mask)
                return
            if in_mask >> row & 1:
                # already filled by horizontal domino from prev column
                fill(row + 1, in_mask, out_mask)
            else:
                # horizontal domino into next column
                fill(row + 1, in_mask, out_mask | (1 << row))
                # vertical domino (fills this row and next row in same column)
                if row + 1 < rows and not (in_mask >> (row + 1) & 1):
                    fill(row + 2, in_mask, out_mask)
        for mask in range(1 << rows):
            fill(0, mask, 0)
        return trans

    transitions = build_transitions(n)
    dp = [0] * (1 << n)
    dp[0] = 1
    for _col in range(m):
        ndp = [0] * (1 << n)
        for mask in range(1 << n):
            if dp[mask] == 0:
                continue
            for nmask in transitions[mask]:
                ndp[nmask] = (ndp[nmask] + dp[mask]) % MOD
        dp = ndp
    return str(dp[0])


# ---------------------------------------------------------------------------
# 2220 - Counting Numbers  (digit DP, no two adjacent digits equal)
# ---------------------------------------------------------------------------
def _solve_2220(input_data: str) -> str:
    a, b = map(int, input_data.strip().split())

    def count_up_to(num: int) -> int:
        """Count integers in [0, num] with no two adjacent digits equal."""
        if num < 0:
            return 0
        s = str(num)
        length = len(s)

        @lru_cache(maxsize=None)
        def dp(pos: int, prev: int, tight: bool, started: bool) -> int:
            if pos == length:
                return 1
            limit = int(s[pos]) if tight else 9
            result = 0
            for d in range(0, limit + 1):
                ntight = tight and (d == limit)
                if not started and d == 0:
                    result += dp(pos + 1, prev, ntight, False)
                elif d != prev:
                    result += dp(pos + 1, d, ntight, True)
            return result

        ans = dp(0, -1, True, False)
        dp.cache_clear()
        return ans

    return str(count_up_to(b) - count_up_to(a - 1))


# ---------------------------------------------------------------------------
# 1748 - Increasing Subsequence II  (Fenwick tree + DP)
# ---------------------------------------------------------------------------
def _solve_1748(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    tree = [0] * (k + 1)

    def update(i: int, val: int) -> None:
        while i <= k:
            tree[i] = (tree[i] + val) % MOD
            i += i & (-i)

    def query(i: int) -> int:
        s = 0
        while i > 0:
            s = (s + tree[i]) % MOD
            i -= i & (-i)
        return s

    total = 0
    for x in a:
        cnt = (1 + query(x - 1)) % MOD
        update(x, cnt)
        total = (total + cnt) % MOD
    return str(total)


# ---------------------------------------------------------------------------
# Newer / uncertain problems — return None
# ---------------------------------------------------------------------------
def _not_available(input_data: str) -> None:
    return None


# ---------------------------------------------------------------------------
# Solution dispatch table
# ---------------------------------------------------------------------------
SOLUTIONS: dict[int, callable] = {
    1633: _solve_1633,  # Dice Combinations
    1634: _solve_1634,  # Minimizing Coins
    1635: _solve_1635,  # Coin Combinations I
    1636: _solve_1636,  # Coin Combinations II
    1637: _solve_1637,  # Removing Digits
    1638: _solve_1638,  # Grid Paths
    1158: _solve_1158,  # Book Shop
    1746: _solve_1746,  # Array Description
    2413: _solve_2413,  # Counting Towers
    1639: _solve_1639,  # Edit Distance
    3403: _solve_3403,  # Longest Common Subsequence
    1744: _solve_1744,  # Rectangle Cutting
    3359: _not_available,  # Minimal Grid Path (newer)
    1745: _solve_1745,  # Money Sums
    1097: _solve_1097,  # Removal Game
    1093: _solve_1093,  # Two Sets II
    3314: _not_available,  # Mountain Range (newer)
    1145: _solve_1145,  # Increasing Subsequence
    1140: _solve_1140,  # Projects
    1653: _solve_1653,  # Elevator Rides
    2181: _solve_2181,  # Counting Tilings
    2220: _solve_2220,  # Counting Numbers
    1748: _solve_1748,  # Increasing Subsequence II
}
