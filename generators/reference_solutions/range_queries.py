"""Reference solutions for CSES Range Queries problems."""

from __future__ import annotations

import sys
from math import log2


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1646 - Static Range Sum Queries
# ---------------------------------------------------------------------------
def _solve_1646(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + a[i]
    out = []
    for i in range(q):
        l, r = map(int, lines[2 + i].split())
        out.append(str(prefix[r] - prefix[l - 1]))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1647 - Static Range Minimum Queries
# ---------------------------------------------------------------------------
def _solve_1647(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    # Sparse table
    LOG = max(1, int(log2(n)) + 1) if n > 0 else 1
    sp = [a[:]]
    for j in range(1, LOG + 1):
        prev = sp[j - 1]
        cur = []
        length = 1 << j
        for i in range(n - length + 1):
            cur.append(min(prev[i], prev[i + (1 << (j - 1))]))
        sp.append(cur)
    # Precompute log2
    lg = [0] * (n + 1)
    for i in range(2, n + 1):
        lg[i] = lg[i // 2] + 1
    out = []
    for i in range(q):
        l, r = map(int, lines[2 + i].split())
        l -= 1
        r -= 1
        k = lg[r - l + 1]
        out.append(str(min(sp[k][l], sp[k][r - (1 << k) + 1])))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1648 - Dynamic Range Sum Queries (BIT / Fenwick Tree)
# ---------------------------------------------------------------------------
def _solve_1648(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    bit = [0] * (n + 1)

    def update(i, delta):
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    for i in range(n):
        update(i + 1, a[i])

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            k, u = int(parts[1]), int(parts[2])
            update(k, u - a[k - 1])
            a[k - 1] = u
        else:
            l, r = int(parts[1]), int(parts[2])
            out.append(str(query(r) - query(l - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1649 - Dynamic Range Minimum Queries (Segment Tree)
# ---------------------------------------------------------------------------
def _solve_1649(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Segment tree (1-indexed, size 2*N)
    N = 1
    while N < n:
        N <<= 1
    tree = [float('inf')] * (2 * N)
    for i in range(n):
        tree[N + i] = a[i]
    for i in range(N - 1, 0, -1):
        tree[i] = min(tree[2 * i], tree[2 * i + 1])

    def update(pos, val):
        pos += N
        tree[pos] = val
        pos >>= 1
        while pos >= 1:
            tree[pos] = min(tree[2 * pos], tree[2 * pos + 1])
            pos >>= 1

    def query_min(l, r):
        res = float('inf')
        l += N
        r += N + 1
        while l < r:
            if l & 1:
                res = min(res, tree[l])
                l += 1
            if r & 1:
                r -= 1
                res = min(res, tree[r])
            l >>= 1
            r >>= 1
        return res

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            k, u = int(parts[1]), int(parts[2])
            update(k - 1, u)
        else:
            l, r = int(parts[1]), int(parts[2])
            out.append(str(query_min(l - 1, r - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1650 - Range Xor Queries
# ---------------------------------------------------------------------------
def _solve_1650(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] ^ a[i]
    out = []
    for i in range(q):
        l, r = map(int, lines[2 + i].split())
        out.append(str(prefix[r] ^ prefix[l - 1]))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1651 - Range Update Queries
# ---------------------------------------------------------------------------
def _solve_1651(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    # BIT for range add, point query
    bit = [0] * (n + 2)

    def update(i, delta):
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            l, r, u = int(parts[1]), int(parts[2]), int(parts[3])
            update(l, u)
            update(r + 1, -u)
        else:
            k = int(parts[1])
            out.append(str(a[k - 1] + query(k)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1652 - Forest Queries (2D prefix sums)
# ---------------------------------------------------------------------------
def _solve_1652(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    grid = []
    for i in range(n):
        grid.append(lines[1 + i])
    # 2D prefix sums
    ps = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            ps[i][j] = (1 if grid[i - 1][j - 1] == '*' else 0) + ps[i - 1][j] + ps[i][j - 1] - ps[i - 1][j - 1]
    out = []
    for i in range(q):
        y1, x1, y2, x2 = map(int, lines[1 + n + i].split())
        val = ps[y2][x2] - ps[y1 - 1][x2] - ps[y2][x1 - 1] + ps[y1 - 1][x1 - 1]
        out.append(str(val))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1143 - Hotel Queries
# ---------------------------------------------------------------------------
def _solve_1143(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    h = list(map(int, lines[1].split()))
    groups = list(map(int, lines[2].split()))

    # Segment tree storing max of hotel rooms
    N = 1
    while N < n:
        N <<= 1
    tree = [0] * (2 * N)
    for i in range(n):
        tree[N + i] = h[i]
    for i in range(N - 1, 0, -1):
        tree[i] = max(tree[2 * i], tree[2 * i + 1])

    def find_and_update(node, lo, hi, val):
        if lo == hi:
            tree[node] -= val
            return lo + 1  # 1-indexed
        mid = (lo + hi) // 2
        if tree[2 * node] >= val:
            result = find_and_update(2 * node, lo, mid, val)
        else:
            result = find_and_update(2 * node + 1, mid + 1, hi, val)
        tree[node] = max(tree[2 * node], tree[2 * node + 1])
        return result

    out = []
    for g in groups:
        if tree[1] < g:
            out.append("0")
        else:
            out.append(str(find_and_update(1, 0, N - 1, g)))
    return " ".join(out)


# ---------------------------------------------------------------------------
# 1749 - List Removals
# ---------------------------------------------------------------------------
def _solve_1749(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    positions = list(map(int, lines[2].split()))

    # BIT to track positions: bit[i] = 1 if element i still exists
    bit = [0] * (n + 1)

    def update(i, delta):
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    # Find k-th existing element using binary search on BIT
    def find_kth(k):
        pos = 0
        r = 1
        while r <= n:
            r <<= 1
        r >>= 1
        while r > 0:
            if pos + r <= n and bit[pos + r] < k:
                k -= bit[pos + r]
                pos += r
            r >>= 1
        return pos + 1

    for i in range(1, n + 1):
        update(i, 1)

    out = []
    for p in positions:
        idx = find_kth(p)
        out.append(str(a[idx - 1]))
        update(idx, -1)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1144 - Salary Queries (Coordinate compression + BIT)
# ---------------------------------------------------------------------------
def _solve_1144(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Collect all salary values that appear (initial + updates + query bounds)
    queries = []
    all_vals = set(a)
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '!':
            queries.append(('!', int(parts[1]), int(parts[2])))
            all_vals.add(int(parts[2]))
        else:
            queries.append(('?', int(parts[1]), int(parts[2])))
            all_vals.add(int(parts[1]))
            all_vals.add(int(parts[2]))

    # Coordinate compression
    sorted_vals = sorted(all_vals)
    comp = {v: i + 1 for i, v in enumerate(sorted_vals)}
    m = len(sorted_vals)

    bit = [0] * (m + 1)

    def update(i, delta):
        while i <= m:
            bit[i] += delta
            i += i & (-i)

    def query_sum(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    # Initialize BIT
    for v in a:
        update(comp[v], 1)

    out = []
    for qr in queries:
        if qr[0] == '!':
            k, x = qr[1], qr[2]
            update(comp[a[k - 1]], -1)
            a[k - 1] = x
            update(comp[x], 1)
        else:
            lo, hi = qr[1], qr[2]
            clo = comp[lo]
            chi = comp[hi]
            out.append(str(query_sum(chi) - query_sum(clo - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2166 - Prefix Sum Queries
# ---------------------------------------------------------------------------
def _solve_2166(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Segment tree: each node stores (total_sum, max_prefix_sum) of its range
    # merge(left, right) = (left.sum + right.sum, max(left.max_prefix, left.sum + right.max_prefix))
    N = 1
    while N < n:
        N <<= 1
    # tree[i] = (total_sum, max_prefix_sum)
    tree = [(0, 0)] * (2 * N)
    for i in range(n):
        tree[N + i] = (a[i], a[i])
    for i in range(N - 1, 0, -1):
        ls, lp = tree[2 * i]
        rs, rp = tree[2 * i + 1]
        tree[i] = (ls + rs, max(lp, ls + rp))

    def update(pos, val):
        pos += N
        tree[pos] = (val, val)
        pos >>= 1
        while pos >= 1:
            ls, lp = tree[2 * pos]
            rs, rp = tree[2 * pos + 1]
            tree[pos] = (ls + rs, max(lp, ls + rp))
            pos >>= 1

    def query_range(l, r):
        # Returns (total_sum, max_prefix_sum) for range [l, r] (0-indexed)
        def go(node, node_l, node_r, ql, qr):
            if ql <= node_l and node_r <= qr:
                return tree[node]
            mid = (node_l + node_r) // 2
            if qr <= mid:
                return go(2 * node, node_l, mid, ql, qr)
            if ql > mid:
                return go(2 * node + 1, mid + 1, node_r, ql, qr)
            ls, lp = go(2 * node, node_l, mid, ql, mid)
            rs, rp = go(2 * node + 1, mid + 1, node_r, mid + 1, qr)
            return (ls + rs, max(lp, ls + rp))
        return go(1, 0, N - 1, l, r)

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            k, u = int(parts[1]), int(parts[2])
            a[k - 1] = u
            update(k - 1, u)
        else:
            l, r = int(parts[1]), int(parts[2])
            _, mp = query_range(l - 1, r - 1)
            out.append(str(max(0, mp)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1190 - Subarray Sum Queries
# ---------------------------------------------------------------------------
def _solve_1190(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Segment tree: each node stores (total, prefix_max, suffix_max, max_subarray)
    N = 1
    while N < n:
        N <<= 1

    # (total, prefix_max, suffix_max, best)
    ZERO = (0, 0, 0, 0)

    def make_leaf(val):
        v = max(0, val)
        return (val, v, v, v)

    def merge(a, b):
        total = a[0] + b[0]
        prefix_max = max(a[1], a[0] + b[1])
        suffix_max = max(b[2], b[0] + a[2])
        best = max(a[3], b[3], a[2] + b[1])
        return (total, max(0, prefix_max), max(0, suffix_max), max(0, best))

    tree = [ZERO] * (2 * N)
    for i in range(n):
        tree[N + i] = make_leaf(a[i])
    for i in range(N - 1, 0, -1):
        tree[i] = merge(tree[2 * i], tree[2 * i + 1])

    def update(pos, val):
        pos += N
        tree[pos] = make_leaf(val)
        pos >>= 1
        while pos >= 1:
            tree[pos] = merge(tree[2 * pos], tree[2 * pos + 1])
            pos >>= 1

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        k, x = int(parts[0]), int(parts[1])
        update(k - 1, x)
        out.append(str(tree[1][3]))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1734 - Distinct Values Queries (offline + BIT)
# ---------------------------------------------------------------------------
def _solve_1734(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    queries = []
    for i in range(q):
        l, r = map(int, lines[2 + i].split())
        queries.append((r, l, i))
    queries.sort()

    bit = [0] * (n + 1)

    def update(i, delta):
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def query_sum(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    last_seen = {}
    ans = [0] * q
    qi = 0
    for j in range(1, n + 1):
        val = a[j - 1]
        if val in last_seen:
            update(last_seen[val], -1)
        last_seen[val] = j
        update(j, 1)
        while qi < q and queries[qi][0] == j:
            r, l, idx = queries[qi]
            ans[idx] = query_sum(r) - query_sum(l - 1)
            qi += 1
    return "\n".join(map(str, ans))


# ---------------------------------------------------------------------------
# 1739 - Forest Queries II (2D BIT with updates)
# ---------------------------------------------------------------------------
def _solve_1739(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    grid = []
    for i in range(n):
        grid.append(lines[1 + i])

    bit2d = [[0] * (n + 1) for _ in range(n + 1)]

    def update2d(x, y, delta):
        i = x
        while i <= n:
            j = y
            while j <= n:
                bit2d[i][j] += delta
                j += j & (-j)
            i += i & (-i)

    def query2d(x, y):
        s = 0
        i = x
        while i > 0:
            j = y
            while j > 0:
                s += bit2d[i][j]
                j -= j & (-j)
            i -= i & (-i)
        return s

    def range_query(y1, x1, y2, x2):
        return query2d(y2, x2) - query2d(y1 - 1, x2) - query2d(y2, x1 - 1) + query2d(y1 - 1, x1 - 1)

    # Initialize
    state = [[False] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if grid[i - 1][j - 1] == '*':
                state[i][j] = True
                update2d(i, j, 1)

    out = []
    for i in range(q):
        parts = lines[1 + n + i].split()
        if parts[0] == '1':
            y, x = int(parts[1]), int(parts[2])
            if state[y][x]:
                update2d(y, x, -1)
                state[y][x] = False
            else:
                update2d(y, x, 1)
                state[y][x] = True
        else:
            y1, x1, y2, x2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
            out.append(str(range_query(y1, x1, y2, x2)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1735 - Range Updates and Sums (Lazy Segment Tree)
# ---------------------------------------------------------------------------
def _solve_1735(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Lazy segment tree with two lazy operations: set and add
    # "set" takes priority over "add" (if set is pending, add is cleared)
    N = 1
    while N < n:
        N <<= 1

    tree_sum = [0] * (2 * N)
    lazy_add = [0] * (2 * N)
    lazy_set = [None] * (2 * N)  # None means no pending set
    sz = [0] * (2 * N)

    for i in range(N):
        sz[N + i] = 1
    for i in range(N - 1, 0, -1):
        sz[i] = sz[2 * i] + sz[2 * i + 1]

    for i in range(n):
        tree_sum[N + i] = a[i]
    for i in range(N - 1, 0, -1):
        tree_sum[i] = tree_sum[2 * i] + tree_sum[2 * i + 1]

    def push_down(node):
        for child in (2 * node, 2 * node + 1):
            if lazy_set[node] is not None:
                lazy_set[child] = lazy_set[node]
                lazy_add[child] = 0
                tree_sum[child] = lazy_set[node] * sz[child]
            if lazy_add[node] != 0:
                if lazy_set[child] is not None:
                    lazy_set[child] += lazy_add[node]
                    tree_sum[child] = lazy_set[child] * sz[child]
                else:
                    lazy_add[child] += lazy_add[node]
                    tree_sum[child] += lazy_add[node] * sz[child]
        lazy_set[node] = None
        lazy_add[node] = 0

    def range_add(node, lo, hi, ql, qr, val):
        if ql <= lo and hi <= qr:
            lazy_add[node] += val
            tree_sum[node] += val * sz[node]
            return
        push_down(node)
        mid = (lo + hi) // 2
        if ql <= mid:
            range_add(2 * node, lo, mid, ql, qr, val)
        if qr > mid:
            range_add(2 * node + 1, mid + 1, hi, ql, qr, val)
        tree_sum[node] = tree_sum[2 * node] + tree_sum[2 * node + 1]

    def range_set(node, lo, hi, ql, qr, val):
        if ql <= lo and hi <= qr:
            lazy_set[node] = val
            lazy_add[node] = 0
            tree_sum[node] = val * sz[node]
            return
        push_down(node)
        mid = (lo + hi) // 2
        if ql <= mid:
            range_set(2 * node, lo, mid, ql, qr, val)
        if qr > mid:
            range_set(2 * node + 1, mid + 1, hi, ql, qr, val)
        tree_sum[node] = tree_sum[2 * node] + tree_sum[2 * node + 1]

    def range_query(node, lo, hi, ql, qr):
        if ql <= lo and hi <= qr:
            return tree_sum[node]
        push_down(node)
        mid = (lo + hi) // 2
        s = 0
        if ql <= mid:
            s += range_query(2 * node, lo, mid, ql, qr)
        if qr > mid:
            s += range_query(2 * node + 1, mid + 1, hi, ql, qr)
        return s

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        t = int(parts[0])
        if t == 1:
            l, r, x = int(parts[1]), int(parts[2]), int(parts[3])
            range_add(1, 0, N - 1, l - 1, r - 1, x)
        elif t == 2:
            l, r, x = int(parts[1]), int(parts[2]), int(parts[3])
            range_set(1, 0, N - 1, l - 1, r - 1, x)
        else:
            l, r = int(parts[1]), int(parts[2])
            out.append(str(range_query(1, 0, N - 1, l - 1, r - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1736 - Polynomial Queries
# ---------------------------------------------------------------------------
def _solve_1736(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # Adding 1, 2, 3, ..., (r-l+1) to positions l..r
    # = adding (i - l + 1) to position i for l <= i <= r
    # = adding i to each position minus adding (l-1) to each position
    # Two BITs: one for sum of coefficients of i, one for constant terms
    # Specifically, to add c*i + d to prefix sum at position i:
    # We use two BITs: B1 and B2
    # sum(1..x) = B1.query(x) * x + B2.query(x)
    # Actually let's use a different approach: two BITs for range-add and range-sum.

    # For polynomial queries: add 1,2,...,k to positions l..r where k = r-l+1
    # This is equivalent to: for position i in [l,r], add (i - l + 1)
    # We need range sum queries and "arithmetic progression" range updates.

    # Use two BITs for tracking: f(i) = c1*i + c0
    # sum(l..r) = sum of (a[i] + accumulated_f(i)) for i in l..r

    # BIT-based range update/range sum:
    # We maintain two BITs B1, B2 such that:
    # the sum prefix(x) = B1(x) * x - B2(x)
    # To add val to range [l, r]:
    #   B1: add val at l, add -val at r+1
    #   B2: add val*(l-1) at l, add -val*r at r+1

    # For arithmetic progression 1,2,...,k at [l,r]:
    # This equals adding i-l+1 to position i.
    # = adding i to [l,r] then subtracting (l-1) from [l,r]
    # Adding a constant c to [l,r] is a standard range add.
    # Adding i to [l,r] means for each position i in [l,r], add the value i.
    # For prefix sum approach:
    # sum of (i) for i in [l,r] = sum of i from l to r = (l+r)(r-l+1)/2

    # Let's use a more direct approach with two BIT pairs for linear functions.
    # Accumulated update at position i = A*i + B, where A, B are accumulated from BITs.

    # BIT pair approach:
    # bit_a: coefficient of i
    # bit_b: constant term
    # To add (i - l + 1) = i - (l-1) for positions in [l, r]:
    #   This is adding 1*i + (-(l-1)) for positions in [l, r].
    #   For bit_a: range add 1 on [l, r]
    #   For bit_b: range add -(l-1) on [l, r]
    # The value at position i from updates = bit_a_prefix(i) * i + bit_b_prefix(i)
    # where bit_a_prefix is the point-query of range-add BIT for bit_a.

    # Actually, we need:
    # 1. Point query of accumulated A coefficient at position i (from range add on bit_a)
    # 2. Point query of accumulated B constant at position i (from range add on bit_b)
    # 3. Range sum query of (a[i] + A_i * i + B_i) for i in [l, r]

    # This requires range-sum of (A_i * i + B_i) which is complex.

    # Simpler: use two BITs that support range-add and range-sum.

    # Let's think again. We have initial array a[1..n].
    # Updates: add 1, 2, ..., k to a[l], a[l+1], ..., a[r] where k = r-l+1.
    # Queries: sum a[l..r].

    # The update adds (i - l + 1) to position i for l <= i <= r.
    # We can split: add i to positions [l, r], and add (1 - l) to positions [l, r].

    # We need two "range-add, range-sum" structures:
    # S1: handles the constant range-adds (adding C to [l,r])
    # S2: handles "add i" to [l,r] — which is like adding a linearly-weighted update.

    # For S1, standard two-BIT approach works.
    # For S2, we need range_add_of_i, range_sum_of_i.

    # "Add i to each position in [l,r]" means the contribution to prefix_sum(x) is:
    # sum_{i=l}^{min(x,r)} i
    # This is harder.

    # Alternative: use 3 BITs.
    # net[i] = sum of all updates at position i = sum of (A_j * i^2 + B_j * i + C_j) contributions
    # Actually let me just use the standard approach for "polynomial range updates":

    # Using 3 BITs for quadratic prefix sums:
    # We want to support: for each update, add (i - l + 1) to position i in [l, r].
    # The prefix sum S(x) = sum_{i=1}^{x} f(i) where f(i) is the total updates at position i.
    # f(i) = a_i + (linear in i from updates)
    # S(x) will be at most quadratic in x after updates.

    # Approach: use difference-of-prefix-sum method.
    # Let's directly use the approach from competitive programming:

    # We maintain the original prefix sums and use BITs for the updates.
    # For "add 1, 2, ..., k to [l, r]" (k = r - l + 1):
    # add_to_prefix_sum at position i: val(i) = i - (l - 1) for i in [l, r]

    # We'll use three BITs b0, b1, b2 to represent:
    # prefix_update(x) = b2(x)*x^2 + b1(x)*x + b0(x)

    # Hmm, this is getting complex. Let me just use a simpler O(n*q) ... no, that's too slow.

    # Let me use the well-known technique: two BITs for "range add + range sum" (handles adding
    # a constant to a range), and for the linear part (adding i to [l,r]), decompose into
    # standard operations.

    # Better approach: two independent pairs of BITs.
    # Pair 1 (cnt): range add 1 to [l, r], range sum query → gives count of how many times
    #               each position is covered, and sum of counts.
    # Pair 2 (off): range add (1 - l) to [l, r], range sum query.
    # Total update at position i = cnt_point(i) * i + off_point(i)
    # And range sum = sum of (cnt_point(i) * i + off_point(i)) for i in [l, r]
    # = sum of cnt_point(i)*i + sum of off_point(i)
    # The second term is just off.range_sum(l, r).
    # The first is sum of cnt_point(i)*i which is NOT a standard range sum.

    # OK, let me just go with 3 BITs.
    # Define P(x) = sum_{i=1}^{x} total_added(i)
    # where total_added(i) = sum over all updates containing position i of (i - l_j + 1)
    # We express P(x) as a polynomial in x after each update.

    # For a single update "add 1,2,...,k to [l,r]":
    # P(x) increases by:
    #   if x < l: 0
    #   if l <= x <= r: sum_{i=l}^{x} (i - l + 1) = sum_{j=1}^{x-l+1} j = (x-l+1)(x-l+2)/2
    #   if x > r: sum_{i=l}^{r} (i - l + 1) = k(k+1)/2 where k = r - l + 1

    # (x-l+1)(x-l+2)/2 = (x^2 - (2l-3)x + (l-1)(l-2)) / 2

    # So we need to be able to add ax^2 + bx + c to a range of x and query prefix sums.
    # We'll use 3 BITs: one for x^2 coefficient, one for x, one for constant.
    # Actually we need range-update (add polynomial for x in [l, r]) and point-query of P(x).

    # Wait, P(x) is a prefix sum (cumulative). Let's think of it differently.

    # Let f(i) = total added to position i.
    # P(x) = sum_{i=1}^{x} f(i)
    # We want range_sum(l, r) = P(r) - P(l-1).

    # For each update at [l, r], f(i) += (i - l + 1) for l <= i <= r.
    # So f(i) gets a "linear in i" component.

    # Using BITs for range-linear-add, range-sum:
    # f(i) = sum of all linear pieces at i.
    # We store f as: for each update, we add a piecewise-linear to f.

    # Standard technique: to add (i - l + 1) for i in [l, r]:
    # = to add i for i in [l, r], and add (1-l) for i in [l, r].

    # Part 1: "add C to [l, r]" with range sum.
    # Standard 2-BIT approach: BIT1 (for range add), BIT2.
    # range_add(l, r, C): BIT1[l] += C, BIT1[r+1] -= C, BIT2[l] += C*(l-1), BIT2[r+1] -= C*r
    # prefix(x) = BIT1(x)*x - BIT2(x)
    # range_sum(l,r) = prefix(r) - prefix(l-1)

    # Part 2: "add i to position i for i in [l, r]" with range sum.
    # sum of "i-weight" over [L, R] after multiple such updates.
    # We need prefix_I(x) = sum_{i=1}^{x} g(i) where g(i) = number_of_times_position_i_is_in_an_"add_i"_update * i.
    # = sum_{i=1}^{x} cnt(i) * i, where cnt(i) = number of updates covering i.
    # prefix_I(x) = sum_{i=1}^{x} cnt(i) * i

    # cnt is maintained by range-add-1 to [l, r] for each update.
    # prefix_I(x) is sum of cnt(i)*i.

    # With a BIT for cnt (range-add, point-query): cnt(i) = BIT_cnt(i).
    # But sum of cnt(i)*i is not directly queryable.

    # We need additional BITs. Let D(i) = cnt(i) (difference array maintained by BIT).
    # cnt(i) = sum_{j=1}^{i} D(j) where D is the difference array.
    # Then sum_{i=1}^{x} cnt(i)*i = sum_{i=1}^{x} i * sum_{j=1}^{i} D(j)

    # This is getting complicated. Let me just use 3 BITs directly.

    # We want to support:
    # Operation: for each position i in [l, r], add (i - l + 1) to a[i].
    # Query: sum of a[l..r].

    # The prefix sum of updates P(x) = sum_{i=1}^{x} added(i).
    # After an update [l, r], added(i) = i - l + 1 for l <= i <= r.
    # P(x) for l <= x <= r: P(x) = sum_{i=l}^{x} (i-l+1) = sum_{j=1}^{x-l+1} j = (x-l+1)(x-l+2)/2

    # We'll use the "3 BIT" method. Define:
    # P(x) = (1/2) * B2(x) * x^2 + B1(x) * x + B0(x)
    # where B2, B1, B0 are BIT prefix sums.

    # For update [l, r] adding (i - l + 1):
    # For l <= x <= r: delta_P(x) = (x-l+1)(x-l+2)/2 = (x^2 + (3-2l)x + (l^2-3l+2))/2
    # For x > r: delta_P(x) = k(k+1)/2 (constant, where k = r-l+1)

    # So delta_P(x) = x^2/2 + (3-2l)/2 * x + (l^2-3l+2)/2  for l <= x <= r
    # and delta_P(x) = k(k+1)/2 for x > r

    # Using difference on the polynomial:
    # Add polynomial for x >= l, subtract for x >= r+1, add constant correction for x >= r+1.

    # Let me implement it:
    # For x >= l: add x^2/2 + (3-2l)/2 * x + (l^2-3l+2)/2
    # For x >= r+1: subtract x^2/2 + (3-2l)/2 * x + (l^2-3l+2)/2
    #               add k(k+1)/2

    # Using multiplied-by-2 to avoid fractions:
    # 2*P(x) = B2(x)*x^2 + B1(x)*x + B0(x)
    # For x >= l: add 1*x^2 + (3-2l)*x + (l^2-3l+2)
    # For x >= r+1: sub 1*x^2 + (3-2l)*x + (l^2-3l+2), add k(k+1)

    # BIT point update at position p means: for all x >= p, add to prefix.
    # B2[l] += 1, B2[r+1] -= 1
    # B1[l] += (3-2*l), B1[r+1] -= (3-2*l)
    # B0[l] += (l*l - 3*l + 2), B0[r+1] -= (l*l - 3*l + 2), B0[r+1] += k*(k+1)

    b2 = [0] * (n + 2)
    b1 = [0] * (n + 2)
    b0 = [0] * (n + 2)

    def bit_update(bit_arr, i, delta):
        while i <= n:
            bit_arr[i] += delta
            i += i & (-i)

    def bit_query(bit_arr, i):
        s = 0
        while i > 0:
            s += bit_arr[i]
            i -= i & (-i)
        return s

    # Original prefix sums
    orig_prefix = [0] * (n + 1)
    for i in range(n):
        orig_prefix[i + 1] = orig_prefix[i] + a[i]

    def add_update(l, r):
        k = r - l + 1
        # Coefficients for the polynomial (multiplied by 2)
        a2 = 1
        a1 = 3 - 2 * l
        a0 = l * l - 3 * l + 2

        bit_update(b2, l, a2)
        bit_update(b1, l, a1)
        bit_update(b0, l, a0)

        bit_update(b2, r + 1, -a2)
        bit_update(b1, r + 1, -a1)
        bit_update(b0, r + 1, -a0 + k * (k + 1))

    def prefix_sum_updates(x):
        if x <= 0:
            return 0
        v2 = bit_query(b2, x)
        v1 = bit_query(b1, x)
        v0 = bit_query(b0, x)
        return (v2 * x * x + v1 * x + v0) // 2

    def total_prefix(x):
        return orig_prefix[x] + prefix_sum_updates(x)

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            l, r = int(parts[1]), int(parts[2])
            add_update(l, r)
        else:
            l, r = int(parts[1]), int(parts[2])
            out.append(str(total_prefix(r) - total_prefix(l - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2206 - Pizzeria Queries
# ---------------------------------------------------------------------------
def _solve_2206(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # For each query of type 2 (at position k), answer min(a[j] + |k - j|) for all j.
    # = min(min(a[j] + k - j for j <= k), min(a[j] - k + j for j >= k))
    # = min(min((a[j] - j) + k for j <= k), min((a[j] + j) - k for j >= k))
    # So maintain two segment trees: one for (a[j] - j) → min + k, one for (a[j] + j) → min - k.

    N = 1
    while N < n:
        N <<= 1
    INF = float('inf')
    tree_minus = [INF] * (2 * N)  # a[j] - j (1-indexed j)
    tree_plus = [INF] * (2 * N)   # a[j] + j (1-indexed j)

    for i in range(n):
        tree_minus[N + i] = a[i] - (i + 1)
        tree_plus[N + i] = a[i] + (i + 1)
    for i in range(N - 1, 0, -1):
        tree_minus[i] = min(tree_minus[2 * i], tree_minus[2 * i + 1])
        tree_plus[i] = min(tree_plus[2 * i], tree_plus[2 * i + 1])

    def update(pos, val):
        # pos is 0-indexed
        j = pos + 1  # 1-indexed
        tree_minus[N + pos] = val - j
        tree_plus[N + pos] = val + j
        p = (N + pos) >> 1
        while p >= 1:
            tree_minus[p] = min(tree_minus[2 * p], tree_minus[2 * p + 1])
            tree_plus[p] = min(tree_plus[2 * p], tree_plus[2 * p + 1])
            p >>= 1

    def query_min_range(tree, l, r):
        res = INF
        l += N
        r += N + 1
        while l < r:
            if l & 1:
                res = min(res, tree[l])
                l += 1
            if r & 1:
                r -= 1
                res = min(res, tree[r])
            l >>= 1
            r >>= 1
        return res

    out = []
    for i in range(q):
        parts = lines[2 + i].split()
        if parts[0] == '1':
            k, x = int(parts[1]), int(parts[2])
            update(k - 1, x)
        else:
            k = int(parts[1])
            # min over [0, k-1] of tree_minus + k, min over [k-1, n-1] of tree_plus - k
            left_min = query_min_range(tree_minus, 0, k - 1) + k
            right_min = query_min_range(tree_plus, k - 1, n - 1) - k
            out.append(str(min(left_min, right_min)))
    return "\n".join(out)


SOLUTIONS = {
    1646: _solve_1646,
    1647: _solve_1647,
    1648: _solve_1648,
    1649: _solve_1649,
    1650: _solve_1650,
    1651: _solve_1651,
    1652: _solve_1652,
    1143: _solve_1143,
    1749: _solve_1749,
    1144: _solve_1144,
    2166: _solve_2166,
    2206: _solve_2206,
    1190: _solve_1190,
    1734: _solve_1734,
    1739: _solve_1739,
    1735: _solve_1735,
    1736: _solve_1736,
}
