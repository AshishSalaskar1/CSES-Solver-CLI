"""Reference solutions for CSES Advanced Techniques problems."""

from __future__ import annotations

import sys
from collections import defaultdict

sys.setrecursionlimit(300000)


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1628 - Meet in the Middle
# ---------------------------------------------------------------------------
def _solve_1628(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    def gen_sums(arr):
        sums = defaultdict(int)
        m = len(arr)
        for mask in range(1 << m):
            s = 0
            for i in range(m):
                if mask & (1 << i):
                    s += arr[i]
            sums[s] += 1
        return sums

    half = n // 2
    left = a[:half]
    right = a[half:]
    left_sums = gen_sums(left)
    right_sums = gen_sums(right)

    count = 0
    for s, c in left_sums.items():
        need = x - s
        if need in right_sums:
            count += c * right_sums[need]
    return str(count)


# ---------------------------------------------------------------------------
# 2136 - Hamming Distance
# ---------------------------------------------------------------------------
def _solve_2136(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    strings = []
    for i in range(n):
        s = lines[1 + i].strip()
        # Convert to integer for fast XOR
        val = int(s, 2)
        strings.append(val)
    min_dist = k
    for i in range(n):
        for j in range(i + 1, n):
            d = bin(strings[i] ^ strings[j]).count('1')
            if d < min_dist:
                min_dist = d
    return str(min_dist)


# ---------------------------------------------------------------------------
# 2076 - Necessary Roads (Bridges)
# ---------------------------------------------------------------------------
def _solve_2076(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        adj[u].append((v, i))
        adj[v].append((u, i))

    disc = [0] * (n + 1)
    low = [0] * (n + 1)
    timer = [1]
    bridges = []

    # Iterative Tarjan's bridge finding
    # Stack stores (node, parent_edge_idx, adj_iterator_index)
    visited = [False] * (n + 1)
    for start in range(1, n + 1):
        if visited[start]:
            continue
        stack = [(start, -1, 0)]
        visited[start] = True
        disc[start] = low[start] = timer[0]
        timer[0] += 1
        while stack:
            u, parent_edge, idx = stack.pop()
            if idx < len(adj[u]):
                stack.append((u, parent_edge, idx + 1))
                v, edge_id = adj[u][idx]
                if edge_id == parent_edge:
                    continue
                if visited[v]:
                    low[u] = min(low[u], disc[v])
                else:
                    visited[v] = True
                    disc[v] = low[v] = timer[0]
                    timer[0] += 1
                    stack.append((v, edge_id, 0))
            else:
                # Finished processing u, update parent's low
                if stack:
                    p, pe, pi = stack[-1]
                    low[p] = min(low[p], low[u])
                    if low[u] > disc[p]:
                        bridges.append((min(p, u), max(p, u)))

    result = [str(len(bridges))]
    for u, v in bridges:
        result.append(f"{u} {v}")
    return "\n".join(result)


# ---------------------------------------------------------------------------
# 2077 - Necessary Cities (Articulation Points)
# ---------------------------------------------------------------------------
def _solve_2077(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        adj[u].append((v, i))
        adj[v].append((u, i))

    disc = [0] * (n + 1)
    low = [0] * (n + 1)
    timer = [1]
    is_ap = [False] * (n + 1)
    visited = [False] * (n + 1)

    for start in range(1, n + 1):
        if visited[start]:
            continue
        stack = [(start, -1, 0)]
        visited[start] = True
        disc[start] = low[start] = timer[0]
        timer[0] += 1
        child_count = defaultdict(int)  # count of DFS children per node

        while stack:
            u, parent_edge, idx = stack.pop()
            if idx < len(adj[u]):
                stack.append((u, parent_edge, idx + 1))
                v, edge_id = adj[u][idx]
                if edge_id == parent_edge:
                    continue
                if visited[v]:
                    low[u] = min(low[u], disc[v])
                else:
                    visited[v] = True
                    disc[v] = low[v] = timer[0]
                    timer[0] += 1
                    child_count[u] += 1
                    stack.append((v, edge_id, 0))
            else:
                if stack:
                    p, pe, pi = stack[-1]
                    low[p] = min(low[p], low[u])
                    # Check if p is an articulation point
                    # If p is root: it needs >= 2 DFS children
                    # If p is not root: low[u] >= disc[p]
                    parent_of_p = pe  # edge index
                    if parent_of_p == -1:
                        # p is root
                        if child_count[p] >= 2:
                            is_ap[p] = True
                    else:
                        if low[u] >= disc[p]:
                            is_ap[p] = True

    points = [i for i in range(1, n + 1) if is_ap[i]]
    result = [str(len(points))]
    if points:
        result.append(" ".join(map(str, points)))
    return "\n".join(result)


# ---------------------------------------------------------------------------
# 2078 - Eulerian Subgraphs
# ---------------------------------------------------------------------------
def _solve_2078(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    # Count connected components using DSU
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b
            return True
        return False

    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        union(u, v)

    # Count components that have at least one node
    components = len(set(find(i) for i in range(1, n + 1)))
    # Answer = 2^(m - n + components) mod 10^9 + 7
    MOD = 10**9 + 7
    exp = m - n + components
    return str(pow(2, exp, MOD))


# ---------------------------------------------------------------------------
# 2101 - New Roads Queries
# ---------------------------------------------------------------------------
def _solve_2101(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m, q = map(int, lines[0].split())

    edges = []
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        edges.append((u, v))

    queries = []
    for i in range(q):
        a, b = map(int, lines[1 + m + i].split())
        queries.append((a, b, i))

    # Binary search + offline DSU
    # For each query, binary search on the edge index where a and b become connected.
    # Use parallel binary search.
    ans = [0] * q
    lo = [0] * q
    hi = [m] * q  # answer is 1-indexed edge, or -1 if never connected

    for _ in range(20):  # enough iterations for binary search
        # Group queries by their mid
        buckets = defaultdict(list)
        for i in range(q):
            if lo[i] < hi[i]:
                mid = (lo[i] + hi[i]) // 2
                buckets[mid].append(i)

        if not buckets:
            break

        # Process all mids in order
        parent = list(range(n + 1))
        rank = [0] * (n + 1)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            a, b = find(a), find(b)
            if a == b:
                return
            if rank[a] < rank[b]:
                a, b = b, a
            parent[b] = a
            if rank[a] == rank[b]:
                rank[a] += 1

        sorted_mids = sorted(buckets.keys())
        edge_idx = 0
        for mid in sorted_mids:
            while edge_idx <= mid:
                u, v = edges[edge_idx]
                union(u, v)
                edge_idx += 1
            for qi in buckets[mid]:
                a, b = queries[qi][0], queries[qi][1]
                if find(a) == find(b):
                    hi[qi] = mid
                else:
                    lo[qi] = mid + 1

    # Now lo[i] is the answer (0-indexed edge), convert to 1-indexed
    for i in range(q):
        a, b = queries[i][0], queries[i][1]
        if lo[i] >= m:
            ans[i] = -1
        elif a == b:
            ans[i] = 0
        else:
            ans[i] = lo[i] + 1

    return "\n".join(map(str, ans))


SOLUTIONS = {
    1628: _solve_1628,
    2136: _solve_2136,
    2076: _solve_2076,
    2077: _solve_2077,
    2078: _solve_2078,
    2101: _solve_2101,
}
