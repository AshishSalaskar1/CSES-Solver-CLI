"""Reference solutions for CSES Counting problems.

Most counting problems on CSES are very hard (combinatorics, inclusion-exclusion,
generating functions). Only a few solutions are included here.
"""

from __future__ import annotations

import sys

sys.setrecursionlimit(300000)

MOD = 10**9 + 7


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1080 - Empty String
# ---------------------------------------------------------------------------
def _solve_1080(input_data: str) -> str:
    s = input_data.strip()
    n = len(s)
    if n % 2 == 1:
        return "0"
    # Interval DP: dp[i][j] = number of ways to empty s[i..j]
    # Base: dp[i][i-1] = 1 (empty interval)
    # dp[i][j] = sum over k where s[i]==s[k] and k-i is odd:
    #            dp[i+1][k-1] * dp[k+1][j] * C(half_len - 1, (k-i-1)//2)
    # where half_len = (j - i + 1) // 2

    # Precompute factorials and inverse factorials
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n - 1, -1, -1):
        inv_fact[i] = inv_fact[i + 1] * (i + 1) % MOD

    def comb(a, b):
        if b < 0 or b > a:
            return 0
        return fact[a] * inv_fact[b] % MOD * inv_fact[a - b] % MOD

    dp = [[0] * n for _ in range(n)]
    # Base cases: dp[i][i-1] = 1 (empty), handled by checking i > j
    for length in range(0, n + 1, 2):
        if length == 0:
            continue
        for i in range(n - length + 1):
            j = i + length - 1
            half = length // 2
            # s[i] must be matched with some s[k] where k > i and (k - i) is odd
            for k in range(i + 1, j + 1, 2):
                if s[k] != s[i]:
                    continue
                left = dp[i + 1][k - 1] if k > i + 1 else 1
                right = dp[k + 1][j] if k < j else 1
                left_half = (k - i - 1) // 2
                ways = left * right % MOD * comb(half - 1, left_half) % MOD
                dp[i][j] = (dp[i][j] + ways) % MOD

    return str(dp[0][n - 1])


# ---------------------------------------------------------------------------
# 2176 - Counting Bishops
# ---------------------------------------------------------------------------
def _solve_2176(input_data: str) -> str:
    n, k = map(int, input_data.strip().split())
    if n == 1:
        return "1" if k <= 1 else "0"

    # Bishops on an n×n board: split into black and white diagonals.
    # Black squares form diagonals of lengths: for n×n board, the "/" diagonals
    # restricted to one color form two independent problems.

    # Number of "black" diagonals and "white" diagonals:
    # For an n×n board, diagonals going one way have lengths 1, 2, ..., n-1, n, n-1, ..., 2, 1
    # When restricted to one square color (say cells where (i+j) is even),
    # the anti-diagonals have certain lengths.

    # Actually, the standard approach:
    # Split the board into two independent sets based on (i+j) % 2.
    # For each set, the non-attacking bishops problem reduces to placing non-attacking
    # rooks on a "staircase" board.

    # Diagonal lengths for "black" squares (where (i+j) even):
    # For n even: diags have lengths 1, 1, 2, 2, 3, 3, ..., n/2-1, n/2-1, n/2
    # Actually let me compute directly.

    # Anti-diagonals (i+j = const) for cells where (i+j) is even:
    # i+j = 0: length 1 (just (0,0))
    # i+j = 2: length min(3, n) - max(0, 3-n) = ... depends on n
    # More precisely, for diagonal d (i+j = d), the number of cells is min(d+1, n, 2*n-1-d)
    # For the "even" diagonals (d even):

    def get_diag_lengths(n_val, parity):
        # parity 0 = even diagonals, 1 = odd diagonals
        lengths = []
        for d in range(0, 2 * n_val - 1):
            if d % 2 != parity:
                continue
            # Number of cells on diagonal i+j = d
            length = min(d + 1, n_val, 2 * n_val - 1 - d)
            if length > 0:
                lengths.append(length)
        return lengths

    black_diags = get_diag_lengths(n, 0)
    white_diags = get_diag_lengths(n, 1)

    # For each independent set, count ways to place j bishops on those diagonals
    # such that no two share a "/" diagonal (they're on different anti-diags by construction)
    # and no two share a "\" diagonal.
    # The "\" diagonal is i - j = const. Within each anti-diagonal (i+j = d),
    # cells have different i-j values, so they're on different "\" diags.
    # Between anti-diags of the same parity, cells could share "\" diags.

    # This is equivalent to placing non-attacking rooks on a board where:
    # rows = anti-diagonals of this color, columns = "\" diagonals intersecting them.
    # The profile of this board is given by the diagonal lengths.

    # Standard DP: dp[i][j] = ways to place j non-attacking bishops using first i diagonals
    # dp[i][j] = dp[i-1][j] + dp[i-1][j-1] * (len[i] - (j-1))
    # (The i-th diagonal has len[i] positions, j-1 already blocked by previous diagonals)

    def count_placements(diag_lens, max_k):
        m = len(diag_lens)
        # dp[j] = ways to place j bishops on the diagonals processed so far
        dp_arr = [0] * (max_k + 1)
        dp_arr[0] = 1
        for i in range(m):
            L = diag_lens[i]
            # Process in reverse to avoid counting twice
            new_dp = dp_arr[:]
            for j in range(1, max_k + 1):
                avail = L - (j - 1)
                if avail <= 0:
                    break
                new_dp[j] = (new_dp[j] + dp_arr[j - 1] * avail) % MOD
            dp_arr = new_dp
        return dp_arr

    black_ways = count_placements(black_diags, k)
    white_ways = count_placements(white_diags, k)

    # Total ways to place exactly k bishops = sum over j of black_ways[j] * white_ways[k-j]
    total = 0
    for j in range(k + 1):
        if j < len(black_ways) and (k - j) < len(white_ways):
            total = (total + black_ways[j] * white_ways[k - j]) % MOD
    return str(total)


# ---------------------------------------------------------------------------
# 1078 - Grid Paths II
# ---------------------------------------------------------------------------
def _solve_1078(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    grid = []
    for i in range(n):
        grid.append(lines[1 + i].strip())

    if grid[0][0] == '*' or grid[n - 1][m - 1] == '*':
        return "0"

    # Standard DP: dp[i][j] = number of paths from (0,0) to (i,j) avoiding traps
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = 1
    for i in range(n):
        for j in range(m):
            if grid[i][j] == '*':
                dp[i][j] = 0
                continue
            if i == 0 and j == 0:
                continue
            val = 0
            if i > 0:
                val += dp[i - 1][j]
            if j > 0:
                val += dp[i][j - 1]
            dp[i][j] = val % MOD
    return str(dp[n - 1][m - 1])


SOLUTIONS = {
    1080: _solve_1080,
    2176: _solve_2176,
    1078: _solve_1078,
}
