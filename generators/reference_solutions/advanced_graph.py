"""Reference solutions for CSES Advanced Graph problems."""

from __future__ import annotations

import sys
from collections import deque, defaultdict
from heapq import heappush, heappop

sys.setrecursionlimit(300000)


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1134 - Prüfer Code
# ---------------------------------------------------------------------------
def _solve_1134(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0].strip())
    second_line = lines[1].strip()
    parts = second_line.split()

    if len(parts) == n - 2 and n > 2:
        # Prüfer sequence → tree: decode
        code = list(map(int, parts))
        degree = [1] * (n + 1)
        for v in code:
            degree[v] += 1
        ptr = 1
        while degree[ptr] != 1:
            ptr += 1
        leaf = ptr
        edges = []
        for v in code:
            edges.append((leaf, v))
            degree[v] -= 1
            if degree[v] == 1 and v < ptr:
                leaf = v
            else:
                ptr += 1
                while ptr <= n and degree[ptr] != 1:
                    ptr += 1
                leaf = ptr
        edges.append((leaf, n))
        out = []
        for u, v in edges:
            out.append(f"{u} {v}")
        return "\n".join(out)
    else:
        # Tree → Prüfer sequence: encode. Edges on separate lines.
        if n == 2:
            return ""
        adj = [[] for _ in range(n + 1)]
        degree = [0] * (n + 1)
        for i in range(n - 1):
            u, v = map(int, lines[1 + i].split())
            adj[u].append(v)
            adj[v].append(u)
            degree[u] += 1
            degree[v] += 1

        code = []
        ptr = 1
        while degree[ptr] != 1:
            ptr += 1
        leaf = ptr

        for _ in range(n - 2):
            neighbor = None
            for v in adj[leaf]:
                if degree[v] > 0:
                    neighbor = v
                    break
            code.append(neighbor)
            degree[leaf] = 0
            degree[neighbor] -= 1
            if degree[neighbor] == 1 and neighbor < ptr:
                leaf = neighbor
            else:
                ptr += 1
                while ptr <= n and degree[ptr] != 1:
                    ptr += 1
                leaf = ptr

        return " ".join(map(str, code))


# ---------------------------------------------------------------------------
# 1702 - Tree Traversals
# ---------------------------------------------------------------------------
def _solve_1702(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    preorder = list(map(int, lines[1].split()))
    inorder = list(map(int, lines[2].split()))

    # Build index for inorder
    in_idx = {}
    for i, v in enumerate(inorder):
        in_idx[v] = i

    # Reconstruct and output postorder
    result = []

    def build(pre_start, pre_end, in_start, in_end):
        if pre_start > pre_end:
            return
        root = preorder[pre_start]
        root_in = in_idx[root]
        left_size = root_in - in_start
        build(pre_start + 1, pre_start + left_size, in_start, root_in - 1)
        build(pre_start + left_size + 1, pre_end, root_in + 1, in_end)
        result.append(root)

    build(0, n - 1, 0, n - 1)
    return " ".join(map(str, result))


# ---------------------------------------------------------------------------
# 1757 - Course Schedule II (lexicographically smallest topological order)
# ---------------------------------------------------------------------------
def _solve_1757(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    in_deg = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        in_deg[b] += 1

    # Use min-heap for lexicographically smallest order
    heap = []
    for i in range(1, n + 1):
        if in_deg[i] == 0:
            heappush(heap, i)
    order = []
    while heap:
        u = heappop(heap)
        order.append(u)
        for v in adj[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                heappush(heap, v)
    return " ".join(map(str, order))


# ---------------------------------------------------------------------------
# 1756 - Acyclic Graph Edges
# ---------------------------------------------------------------------------
def _solve_1756(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    edges = []
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        edges.append((u, v))
        adj[u].append((v, i))
        adj[v].append((u, i))

    # DFS to assign directions: tree edges go parent→child, back edges go child→ancestor
    # This ensures a DAG (all edges point "downward" in DFS tree)
    visited = [False] * (n + 1)
    tin = [0] * (n + 1)
    timer = [0]
    result = [None] * m

    for start in range(1, n + 1):
        if visited[start]:
            continue
        stack = [(start, -1)]
        visited[start] = True
        timer[0] += 1
        tin[start] = timer[0]
        while stack:
            u, parent_edge = stack.pop()
            for v, idx in adj[u]:
                if result[idx] is not None:
                    continue
                if not visited[v]:
                    visited[v] = True
                    timer[0] += 1
                    tin[v] = timer[0]
                    result[idx] = (u, v)
                    stack.append((v, idx))
                else:
                    # Back/cross edge: orient from later to earlier discovery
                    if tin[u] > tin[v]:
                        result[idx] = (u, v)
                    else:
                        result[idx] = (v, u)

    out = []
    for u, v in result:
        out.append(f"{u} {v}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1707 - Graph Girth (shortest cycle)
# ---------------------------------------------------------------------------
def _solve_1707(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        adj[u].append(v)
        adj[v].append(u)

    best = float('inf')
    for start in range(1, n + 1):
        dist = [-1] * (n + 1)
        dist[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            if dist[u] + 1 >= best:
                break
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
                elif dist[v] >= dist[u]:
                    # Found a cycle of length dist[u] + dist[v] + 1
                    best = min(best, dist[u] + dist[v] + 1)
    return str(best if best < float('inf') else -1)


# ---------------------------------------------------------------------------
# 1677 - Network Breakdown (reverse DSU)
# ---------------------------------------------------------------------------
def _solve_1677(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    edges = []
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        edges.append((u, v))

    # Read removal order
    removal_order = list(map(int, lines[1 + m].split()))
    # removal_order[i] is the 1-indexed edge removed at step i+1

    # Reverse: add edges in reverse removal order
    parent = list(range(n + 1))
    size = [1] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return 0
        if size[a] < size[b]:
            a, b = b, a
        parent[b] = a
        size[a] += size[b]
        return 1

    # Process in reverse
    results = []
    components = n
    for i in range(m - 1, -1, -1):
        results.append(components)
        edge_idx = removal_order[i] - 1
        u, v = edges[edge_idx]
        if union(u, v):
            components -= 1

    results.reverse()
    return "\n".join(map(str, results))


# ---------------------------------------------------------------------------
# 1700 - Tree Isomorphism I (rooted tree isomorphism)
# ---------------------------------------------------------------------------
def _solve_1700(input_data: str) -> str:
    lines = input_data.split("\n")
    idx = 0
    t = int(lines[idx])
    idx += 1
    results = []

    for _ in range(t):
        n = int(lines[idx])
        idx += 1

        # Tree 1
        children1 = [[] for _ in range(n + 1)]
        for i in range(2, n + 1):
            p = int(lines[idx].split()[i - 2]) if i == 2 else 0
            pass
        # Actually, the input is: for each tree, first line is n,
        # then n-1 lines each with parent of node 2, 3, ..., n
        # Wait, let me re-read the problem format.
        # "The input is: first line n. Then one line with n-1 integers: the parent of each node 2, 3, ..., n."
        parents1 = list(map(int, lines[idx].split()))
        idx += 1
        children1 = [[] for _ in range(n + 1)]
        for i in range(len(parents1)):
            children1[parents1[i]].append(i + 2)

        # Tree 2
        parents2 = list(map(int, lines[idx].split()))
        idx += 1
        children2 = [[] for _ in range(n + 1)]
        for i in range(len(parents2)):
            children2[parents2[i]].append(i + 2)

        # Hash each tree rooted at 1
        label_map = {}
        label_counter = [0]

        def get_label(child_labels):
            key = tuple(sorted(child_labels))
            if key not in label_map:
                label_map[key] = label_counter[0]
                label_counter[0] += 1
            return label_map[key]

        def tree_hash(children, root):
            # Iterative post-order
            labels = [0] * (n + 1)
            stack = [(root, False)]
            while stack:
                node, processed = stack.pop()
                if processed:
                    cl = [labels[c] for c in children[node]]
                    labels[node] = get_label(cl)
                else:
                    stack.append((node, True))
                    for c in children[node]:
                        stack.append((c, False))
            return labels[root]

        label_map.clear()
        label_counter[0] = 0
        h1 = tree_hash(children1, 1)
        h2 = tree_hash(children2, 1)
        results.append("YES" if h1 == h2 else "NO")

    return "\n".join(results)


# ---------------------------------------------------------------------------
# 1701 - Tree Isomorphism II (unrooted tree isomorphism)
# ---------------------------------------------------------------------------
def _solve_1701(input_data: str) -> str:
    lines = input_data.split("\n")
    idx = 0
    t = int(lines[idx])
    idx += 1
    results = []

    for _ in range(t):
        n = int(lines[idx])
        idx += 1

        def read_tree():
            nonlocal idx
            adj = [[] for _ in range(n + 1)]
            for i in range(n - 1):
                u, v = map(int, lines[idx].split())
                idx += 1
                adj[u].append(v)
                adj[v].append(u)
            return adj

        adj1 = read_tree()
        adj2 = read_tree()

        if n == 1:
            results.append("YES")
            continue

        def find_centroids(adj):
            degree = [0] * (n + 1)
            for u in range(1, n + 1):
                degree[u] = len(adj[u])
            leaves = deque()
            for u in range(1, n + 1):
                if degree[u] <= 1:
                    leaves.append(u)
            remaining = n
            while remaining > 2:
                new_leaves = deque()
                remaining -= len(leaves)
                while leaves:
                    u = leaves.popleft()
                    for v in adj[u]:
                        degree[v] -= 1
                        if degree[v] == 1:
                            new_leaves.append(v)
                leaves = new_leaves
            return list(leaves)

        def canonical_hash(adj, root):
            label_map = {}
            label_counter = [0]

            def get_label(child_labels):
                key = tuple(sorted(child_labels))
                if key not in label_map:
                    label_map[key] = label_counter[0]
                    label_counter[0] += 1
                return label_map[key]

            # Iterative hash
            parent = [0] * (n + 1)
            labels = [0] * (n + 1)
            visited = [False] * (n + 1)
            order = []
            stack = [root]
            visited[root] = True
            while stack:
                u = stack.pop()
                order.append(u)
                for v in adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        parent[v] = u
                        stack.append(v)
            for u in reversed(order):
                cl = []
                for v in adj[u]:
                    if v != parent[u]:
                        cl.append(labels[v])
                labels[u] = get_label(cl)
            return labels[root], label_map

        c1 = find_centroids(adj1)
        c2 = find_centroids(adj2)

        if len(c1) != len(c2):
            results.append("NO")
            continue

        hashes1 = set()
        for root in c1:
            h, _ = canonical_hash(adj1, root)
            hashes1.add(h)

        found = False
        for root in c2:
            h, _ = canonical_hash(adj2, root)
            if h in hashes1:
                found = True
                break

        results.append("YES" if found else "NO")

    return "\n".join(results)


# ---------------------------------------------------------------------------
# 1704 - Network Renovation
# ---------------------------------------------------------------------------
def _solve_1704(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = map(int, lines[1 + i].split())
        adj[u].append((v, i))
        adj[v].append((u, i))

    if m == n - 1:
        # It's already a tree, answer = ceil(leaves / 2)
        # where leaves = nodes with degree 1 (except when n == 2)
        if n == 1:
            return "0"
        if n == 2:
            return "1\n1 2"
        leaves = [i for i in range(1, n + 1) if len(adj[i]) == 1]
        k = (len(leaves) + 1) // 2
        out = [str(k)]
        for i in range(k):
            a = leaves[i]
            b = leaves[(i + len(leaves) // 2) % len(leaves)] if i + len(leaves) // 2 < len(leaves) else leaves[len(leaves) - 1 - i + (len(leaves) + 1) // 2 - 1] if False else leaves[i + len(leaves) // 2]
            out.append(f"{a} {b}")
        return "\n".join(out)

    # Find bridges, build bridge tree
    disc = [0] * (n + 1)
    low = [0] * (n + 1)
    timer = [1]
    is_bridge = [False] * m
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
                if stack:
                    p, pe, pi = stack[-1]
                    low[p] = min(low[p], low[u])
                    if low[u] > disc[p]:
                        is_bridge[adj[p][pi - 1][1]] = True

    # Find 2-edge-connected components
    comp = [0] * (n + 1)
    comp_id = 0
    visited2 = [False] * (n + 1)
    for start in range(1, n + 1):
        if visited2[start]:
            continue
        comp_id += 1
        stack = [start]
        visited2[start] = True
        while stack:
            u = stack.pop()
            comp[u] = comp_id
            for v, eidx in adj[u]:
                if not visited2[v] and not is_bridge[eidx]:
                    visited2[v] = True
                    stack.append(v)

    # Build bridge tree
    bridge_adj = [[] for _ in range(comp_id + 1)]
    for eidx in range(m):
        if is_bridge[eidx]:
            u, v = map(int, lines[1 + eidx].split())
            cu, cv = comp[u], comp[v]
            bridge_adj[cu].append(cv)
            bridge_adj[cv].append(cu)

    # Count leaves of bridge tree
    if comp_id <= 1:
        return "0"
    leaves = [i for i in range(1, comp_id + 1) if len(bridge_adj[i]) == 1]
    if not leaves:
        return "0"
    k = (len(leaves) + 1) // 2

    # For the actual edges to add, we need to pair leaves optimally.
    # Find a DFS ordering of the bridge tree and pair leaves that are roughly opposite.
    # First, find any leaf ordering via DFS
    leaf_order = []
    vis = [False] * (comp_id + 1)
    start = leaves[0]
    dfs_stack = [start]
    vis[start] = True
    while dfs_stack:
        u = dfs_stack.pop()
        if len(bridge_adj[u]) <= 1 or u == start:
            if u in set(leaves):
                leaf_order.append(u)
        for v in bridge_adj[u]:
            if not vis[v]:
                vis[v] = True
                dfs_stack.append(v)

    # Ensure we have all leaves
    if len(leaf_order) != len(leaves):
        leaf_order = leaves

    # Map component back to any representative node
    comp_rep = [0] * (comp_id + 1)
    for i in range(1, n + 1):
        comp_rep[comp[i]] = i

    out = [str(k)]
    half = len(leaf_order) // 2
    for i in range(k):
        a_comp = leaf_order[i]
        b_comp = leaf_order[i + half]
        out.append(f"{comp_rep[a_comp]} {comp_rep[b_comp]}")
    return "\n".join(out)


SOLUTIONS = {
    1134: _solve_1134,
    1702: _solve_1702,
    1757: _solve_1757,
    1756: _solve_1756,
    1707: _solve_1707,
    1677: _solve_1677,
    1700: _solve_1700,
    1701: _solve_1701,
}
