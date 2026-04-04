"""Reference solutions for CSES Tree Algorithms problems."""

from __future__ import annotations

import sys
from collections import deque, defaultdict

sys.setrecursionlimit(300000)


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


def _parse_tree(lines, n, start_line=1):
    """Parse a tree from edge list. Returns adjacency list (1-indexed)."""
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        u, v = map(int, lines[start_line + i].split())
        adj[u].append(v)
        adj[v].append(u)
    return adj


# ---------------------------------------------------------------------------
# 1674 - Subordinates
# ---------------------------------------------------------------------------
def _solve_1674(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    if n == 1:
        return "0"
    boss = list(map(int, lines[1].split()))  # boss of employees 2, 3, ..., n
    children = [[] for _ in range(n + 1)]
    for i in range(2, n + 1):
        children[boss[i - 2]].append(i)
    sub = [0] * (n + 1)
    # Iterative DFS
    stack = [(1, False)]
    while stack:
        node, processed = stack.pop()
        if processed:
            s = 0
            for c in children[node]:
                s += sub[c] + 1
            sub[node] = s
        else:
            stack.append((node, True))
            for c in children[node]:
                stack.append((c, False))
    return " ".join(str(sub[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1130 - Tree Matching
# ---------------------------------------------------------------------------
def _solve_1130(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    if n == 1:
        return "0"
    adj = _parse_tree(lines, n)
    # dp[v][0] = max matching in subtree of v, v not matched to any child
    # dp[v][1] = max matching in subtree of v, v matched to one child
    dp0 = [0] * (n + 1)
    dp1 = [0] * (n + 1)
    parent = [0] * (n + 1)
    order = []
    visited = [False] * (n + 1)
    stack = [1]
    visited[1] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)
    for u in reversed(order):
        s = 0
        for v in adj[u]:
            if v == parent[u]:
                continue
            s += max(dp0[v], dp1[v])
        dp0[u] = s
        best1 = 0
        for v in adj[u]:
            if v == parent[u]:
                continue
            # Match u with v: 1 + sum of max(dp0[w], dp1[w]) for w != v children + dp0[v]
            gain = 1 + dp0[v] - max(dp0[v], dp1[v])
            best1 = max(best1, gain)
        dp1[u] = s + best1
    return str(max(dp0[1], dp1[1]))


# ---------------------------------------------------------------------------
# 1131 - Tree Diameter
# ---------------------------------------------------------------------------
def _solve_1131(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    if n == 1:
        return "0"
    adj = _parse_tree(lines, n)

    def bfs(start):
        dist = [-1] * (n + 1)
        dist[start] = 0
        q = deque([start])
        farthest = start
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
                    if dist[v] > dist[farthest]:
                        farthest = v
        return farthest, dist

    u, _ = bfs(1)
    v, dist = bfs(u)
    return str(dist[v])


# ---------------------------------------------------------------------------
# 1132 - Tree Distances I
# ---------------------------------------------------------------------------
def _solve_1132(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    if n == 1:
        return "0"
    adj = _parse_tree(lines, n)

    def bfs(start):
        dist = [-1] * (n + 1)
        dist[start] = 0
        q = deque([start])
        farthest = start
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
                    if dist[v] > dist[farthest]:
                        farthest = v
        return farthest, dist

    u, _ = bfs(1)
    v, dist_u = bfs(u)
    _, dist_v = bfs(v)
    return " ".join(str(max(dist_u[i], dist_v[i])) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1133 - Tree Distances II
# ---------------------------------------------------------------------------
def _solve_1133(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    if n == 1:
        return "0"
    adj = _parse_tree(lines, n)
    sub_size = [1] * (n + 1)
    dist_sum = [0] * (n + 1)
    parent = [0] * (n + 1)
    order = []
    visited = [False] * (n + 1)
    stack = [1]
    visited[1] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)
    # First pass: compute subtree sizes and dist_sum for root
    for u in reversed(order):
        for v in adj[u]:
            if v == parent[u]:
                continue
            sub_size[u] += sub_size[v]
            dist_sum[u] += dist_sum[v] + sub_size[v]
    # Second pass: re-root
    ans = [0] * (n + 1)
    ans[1] = dist_sum[1]
    for u in order:
        for v in adj[u]:
            if v == parent[u]:
                continue
            # ans[v] = ans[u] - sub_size[v] + (n - sub_size[v])
            ans[v] = ans[u] - sub_size[v] + (n - sub_size[v])
    return "\n".join(str(ans[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1687 - Company Queries I (k-th ancestor via binary lifting)
# ---------------------------------------------------------------------------
def _solve_1687(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    boss = list(map(int, lines[1].split()))
    LOG = 20
    up = [[0] * (n + 1) for _ in range(LOG)]
    for i in range(2, n + 1):
        up[0][i] = boss[i - 2]
    up[0][1] = 0
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]
    out = []
    for i in range(q):
        x, k = map(int, lines[2 + i].split())
        cur = x
        for j in range(LOG):
            if k & (1 << j):
                cur = up[j][cur]
        out.append(str(cur if cur != 0 else -1))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1688 - Company Queries II (LCA via binary lifting)
# ---------------------------------------------------------------------------
def _solve_1688(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    boss = list(map(int, lines[1].split()))
    LOG = 20
    up = [[0] * (n + 1) for _ in range(LOG)]
    depth = [0] * (n + 1)
    children = [[] for _ in range(n + 1)]
    for i in range(2, n + 1):
        up[0][i] = boss[i - 2]
        children[boss[i - 2]].append(i)
    # BFS to compute depths
    queue = deque([1])
    visited = [False] * (n + 1)
    visited[1] = True
    while queue:
        u = queue.popleft()
        for v in children[u]:
            if not visited[v]:
                visited[v] = True
                depth[v] = depth[u] + 1
                queue.append(v)
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        for j in range(LOG):
            if diff & (1 << j):
                a = up[j][a]
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        return up[0][a]

    out = []
    for i in range(q):
        a, b = map(int, lines[2 + i].split())
        out.append(str(lca(a, b)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1135 - Distance Queries
# ---------------------------------------------------------------------------
def _solve_1135(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    adj = _parse_tree(lines, n)
    LOG = 20
    up = [[0] * (n + 1) for _ in range(LOG)]
    depth = [0] * (n + 1)
    visited = [False] * (n + 1)
    visited[1] = True
    stack = [1]
    order = []
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                up[0][v] = u
                depth[v] = depth[u] + 1
                stack.append(v)
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        for j in range(LOG):
            if diff & (1 << j):
                a = up[j][a]
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        return up[0][a]

    out = []
    for i in range(q):
        a, b = map(int, lines[n + i].split())
        l = lca(a, b)
        out.append(str(depth[a] + depth[b] - 2 * depth[l]))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1136 - Counting Paths
# ---------------------------------------------------------------------------
def _solve_1136(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = _parse_tree(lines, n)
    LOG = 20
    up = [[0] * (n + 1) for _ in range(LOG)]
    depth = [0] * (n + 1)
    visited = [False] * (n + 1)
    visited[1] = True
    stack = [1]
    order = []
    parent = [0] * (n + 1)
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                up[0][v] = u
                parent[v] = u
                depth[v] = depth[u] + 1
                stack.append(v)
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        for j in range(LOG):
            if diff & (1 << j):
                a = up[j][a]
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        return up[0][a]

    diff = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[n + i].split())
        l = lca(a, b)
        diff[a] += 1
        diff[b] += 1
        diff[l] -= 1
        if parent[l]:
            diff[parent[l]] -= 1

    # Compute subtree sums in reverse BFS order
    sub = [0] * (n + 1)
    for u in reversed(order):
        sub[u] += diff[u]
        if parent[u]:
            sub[parent[u]] += sub[u]

    # Result for each edge (parent[v], v) is sub[v]
    # But we need result for each node 1..n
    # Actually the problem asks for each node, how many paths pass through it.
    # Wait, re-read: "for each node, calculate the number of paths that go through it"
    # Wait, actually: "for each node, count the number of paths containing it"
    # Using the difference array on nodes: diff[a]++, diff[b]++, diff[lca]--, diff[parent[lca]]--
    # Then subtree sum gives the answer for each node.
    return " ".join(str(sub[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1137 - Subtree Queries (Euler tour + BIT)
# ---------------------------------------------------------------------------
def _solve_1137(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    vals = list(map(int, lines[1].split()))
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        u, v = map(int, lines[2 + i].split())
        adj[u].append(v)
        adj[v].append(u)

    # Euler tour
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    timer = [0]
    visited = [False] * (n + 1)
    visited[1] = True
    # Iterative Euler tour
    stack = [(1, False)]
    parent_arr = [0] * (n + 1)
    while stack:
        u, leaving = stack.pop()
        if leaving:
            tout[u] = timer[0]
            continue
        timer[0] += 1
        tin[u] = timer[0]
        stack.append((u, True))
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent_arr[v] = u
                stack.append((v, False))

    # BIT
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

    for i in range(1, n + 1):
        update(tin[i], vals[i - 1])

    out = []
    for i in range(q):
        parts = lines[1 + n + i].split()
        if parts[0] == '1':
            s, x = int(parts[1]), int(parts[2])
            update(tin[s], x - vals[s - 1])
            vals[s - 1] = x
        else:
            s = int(parts[1])
            out.append(str(query(tout[s]) - query(tin[s] - 1)))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1138 - Path Queries
# ---------------------------------------------------------------------------
def _solve_1138(input_data: str) -> str:
    lines = input_data.split("\n")
    n, q = map(int, lines[0].split())
    vals = list(map(int, lines[1].split()))
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        u, v = map(int, lines[2 + i].split())
        adj[u].append(v)
        adj[v].append(u)

    # Euler tour
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    timer = [0]
    visited = [False] * (n + 1)
    visited[1] = True
    stack = [(1, False)]
    while stack:
        u, leaving = stack.pop()
        if leaving:
            tout[u] = timer[0]
            continue
        timer[0] += 1
        tin[u] = timer[0]
        stack.append((u, True))
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                stack.append((v, False))

    # BIT: update tin[s] with +val, tout[s]+1 with -val (but tout is already 1 past)
    # Actually: path sum from root to node v = sum of vals[u] for all ancestors u of v (including v)
    # Using Euler tour: if we set BIT[tin[u]] += val[u] and BIT[tout[u]+1] -= val[u],
    # then BIT.prefix(tin[v]) = sum of values on path from root to v.
    # Wait, let me think again. tout[u] should be the last time in the subtree.
    # With the standard Euler tour: tin[u] is entry time, tout[u] is the max entry time in subtree.
    # If we add val at tin[u] and subtract at tout[u]+1, then prefix(tin[v]) gives path sum.

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

    for i in range(1, n + 1):
        update(tin[i], vals[i - 1])
        if tout[i] + 1 <= n:
            update(tout[i] + 1, -vals[i - 1])

    out = []
    for i in range(q):
        parts = lines[1 + n + i].split()
        if parts[0] == '1':
            s, x = int(parts[1]), int(parts[2])
            delta = x - vals[s - 1]
            vals[s - 1] = x
            update(tin[s], delta)
            if tout[s] + 1 <= n:
                update(tout[s] + 1, -delta)
        else:
            s = int(parts[1])
            out.append(str(query(tin[s])))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2079 - Finding a Centroid
# ---------------------------------------------------------------------------
def _solve_2079(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    adj = _parse_tree(lines, n)

    sub_size = [1] * (n + 1)
    parent = [0] * (n + 1)
    visited = [False] * (n + 1)
    visited[1] = True
    order = []
    stack = [1]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)
    for u in reversed(order):
        for v in adj[u]:
            if v != parent[u]:
                sub_size[u] += sub_size[v]

    for u in range(1, n + 1):
        max_sub = n - sub_size[u]  # "parent" subtree
        for v in adj[u]:
            if v != parent[u]:
                max_sub = max(max_sub, sub_size[v])
        if max_sub <= n // 2:
            return str(u)
    return str(1)


# ---------------------------------------------------------------------------
# 1139 - Distinct Colors (small-to-large merging / DSU on tree)
# ---------------------------------------------------------------------------
def _solve_1139(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    colors = list(map(int, lines[1].split()))
    adj = _parse_tree(lines, n, start_line=2)

    parent = [0] * (n + 1)
    visited = [False] * (n + 1)
    visited[1] = True
    order = []
    stack = [1]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)

    # Small-to-large merging
    color_sets = [None] * (n + 1)
    ans = [0] * (n + 1)

    for u in reversed(order):
        s = {colors[u - 1]}
        for v in adj[u]:
            if v == parent[u]:
                continue
            if len(color_sets[v]) > len(s):
                s, color_sets[v] = color_sets[v], s
            s.update(color_sets[v])
            color_sets[v] = None  # free memory
        ans[u] = len(s)
        color_sets[u] = s

    return " ".join(str(ans[i]) for i in range(1, n + 1))


SOLUTIONS = {
    1674: _solve_1674,
    1130: _solve_1130,
    1131: _solve_1131,
    1132: _solve_1132,
    1133: _solve_1133,
    1687: _solve_1687,
    1688: _solve_1688,
    1135: _solve_1135,
    1136: _solve_1136,
    1137: _solve_1137,
    1138: _solve_1138,
    2079: _solve_2079,
    1139: _solve_1139,
}
