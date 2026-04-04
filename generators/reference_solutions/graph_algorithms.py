"""Reference solutions for CSES Graph Algorithms problems."""
import sys
from collections import deque, defaultdict
import heapq


# ---------------------------------------------------------------------------
# 1192 - Counting Rooms
# ---------------------------------------------------------------------------
def solve_1192(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    grid = [list(lines[i + 1]) for i in range(n)]
    visited = [[False] * m for _ in range(n)]
    count = 0
    for i in range(n):
        for j in range(m):
            if grid[i][j] == '.' and not visited[i][j]:
                count += 1
                queue = deque()
                queue.append((i, j))
                visited[i][j] = True
                while queue:
                    r, c = queue.popleft()
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < m and not visited[nr][nc] and grid[nr][nc] == '.':
                            visited[nr][nc] = True
                            queue.append((nr, nc))
    return str(count)


# ---------------------------------------------------------------------------
# 1193 - Labyrinth
# ---------------------------------------------------------------------------
def solve_1193(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    grid = [lines[i + 1] for i in range(n)]
    start = end = None
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'A':
                start = (i, j)
            elif grid[i][j] == 'B':
                end = (i, j)
    if start is None or end is None:
        return "NO"

    dist = [[-1] * m for _ in range(n)]
    parent = [[None] * m for _ in range(n)]
    dist[start[0]][start[1]] = 0
    queue = deque([start])
    dirs = {'L': (0, -1), 'R': (0, 1), 'U': (-1, 0), 'D': (1, 0)}
    dir_list = [('L', 0, -1), ('R', 0, 1), ('U', -1, 0), ('D', 1, 0)]

    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            break
        for ch, dr, dc in dir_list:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and dist[nr][nc] == -1 and grid[nr][nc] != '#':
                dist[nr][nc] = dist[r][c] + 1
                parent[nr][nc] = (r, c, ch)
                queue.append((nr, nc))

    if dist[end[0]][end[1]] == -1:
        return "NO"

    path = []
    r, c = end
    while (r, c) != start:
        pr, pc, ch = parent[r][c]
        path.append(ch)
        r, c = pr, pc
    path.reverse()
    return "YES\n" + str(len(path)) + "\n" + ''.join(path)


# ---------------------------------------------------------------------------
# 1666 - Building Roads
# ---------------------------------------------------------------------------
def solve_1666(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
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

    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        union(a, b)

    roots = set()
    for i in range(1, n + 1):
        roots.add(find(i))
    roots = list(roots)
    result = [str(len(roots) - 1)]
    for i in range(1, len(roots)):
        result.append(f"{roots[0]} {roots[i]}")
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1667 - Message Route
# ---------------------------------------------------------------------------
def solve_1667(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        adj[b].append(a)

    dist = [-1] * (n + 1)
    prev = [0] * (n + 1)
    dist[1] = 0
    queue = deque([1])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                prev[v] = u
                queue.append(v)

    if dist[n] == -1:
        return "IMPOSSIBLE"

    path = []
    cur = n
    while cur != 0:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return str(len(path)) + "\n" + ' '.join(map(str, path))


# ---------------------------------------------------------------------------
# 1668 - Building Teams
# ---------------------------------------------------------------------------
def solve_1668(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        adj[b].append(a)

    color = [0] * (n + 1)
    for start in range(1, n + 1):
        if color[start] != 0:
            continue
        color[start] = 1
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == 0:
                    color[v] = 3 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return "IMPOSSIBLE"
    return ' '.join(str(color[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1669 - Round Trip (undirected cycle)
# ---------------------------------------------------------------------------
def solve_1669(input_data: str) -> str:
    sys.setrecursionlimit(200000)
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        adj[b].append(a)

    visited = [False] * (n + 1)
    parent = [0] * (n + 1)
    cycle_start = -1
    cycle_end = -1

    def dfs(u, p):
        nonlocal cycle_start, cycle_end
        visited[u] = True
        for v in adj[u]:
            if v == p:
                # skip the edge we came from, but only once
                p = -1
                continue
            if visited[v]:
                cycle_start = v
                cycle_end = u
                return True
            parent[v] = u
            if dfs(v, u):
                return True
        return False

    # Use iterative DFS to avoid stack overflow
    # We'll use an iterative approach instead
    visited = [False] * (n + 1)
    parent = [0] * (n + 1)
    cycle_start = -1
    cycle_end = -1

    def iterative_find_cycle():
        nonlocal cycle_start, cycle_end
        for s in range(1, n + 1):
            if visited[s]:
                continue
            # stack: (node, parent, adj_index)
            stack = [(s, -1, 0)]
            visited[s] = True
            parent[s] = 0
            while stack:
                u, p, idx = stack[-1]
                if idx < len(adj[u]):
                    stack[-1] = (u, p, idx + 1)
                    v = adj[u][idx]
                    if v == p:
                        # Update p to -1 so we only skip the first back-edge
                        stack[-1] = (u, -1, idx + 1)
                        continue
                    if visited[v]:
                        cycle_start = v
                        cycle_end = u
                        return True
                    visited[v] = True
                    parent[v] = u
                    stack.append((v, u, 0))
                else:
                    stack.pop()
        return False

    if not iterative_find_cycle():
        return "IMPOSSIBLE"

    path = []
    cur = cycle_end
    while cur != cycle_start:
        path.append(cur)
        cur = parent[cur]
    path.append(cycle_start)
    path.reverse()
    path.append(cycle_start)
    return str(len(path)) + "\n" + ' '.join(map(str, path))


# ---------------------------------------------------------------------------
# 1194 - Monsters
# ---------------------------------------------------------------------------
def solve_1194(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    grid = [lines[i + 1] for i in range(n)]

    start = None
    monsters = []
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'A':
                start = (i, j)
            elif grid[i][j] == 'M':
                monsters.append((i, j))

    if start is None:
        return "NO"

    INF = float('inf')
    # BFS from all monsters
    mdist = [[INF] * m for _ in range(n)]
    queue = deque()
    for mi, mj in monsters:
        mdist[mi][mj] = 0
        queue.append((mi, mj))
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and mdist[nr][nc] == INF and grid[nr][nc] != '#':
                mdist[nr][nc] = mdist[r][c] + 1
                queue.append((nr, nc))

    # BFS from A
    adist = [[INF] * m for _ in range(n)]
    prev = [[None] * m for _ in range(n)]
    adist[start[0]][start[1]] = 0
    queue = deque([start])
    dir_map = {(0, -1): 'L', (0, 1): 'R', (-1, 0): 'U', (1, 0): 'D'}

    while queue:
        r, c = queue.popleft()
        if r == 0 or r == n - 1 or c == 0 or c == m - 1:
            # reached border
            if adist[r][c] < mdist[r][c]:
                path = []
                cr, cc = r, c
                while (cr, cc) != start:
                    pr, pc, ch = prev[cr][cc]
                    path.append(ch)
                    cr, cc = pr, pc
                path.reverse()
                return "YES\n" + str(len(path)) + "\n" + ''.join(path)
        for (dr, dc), ch in dir_map.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and adist[nr][nc] == INF and grid[nr][nc] != '#':
                nd = adist[r][c] + 1
                if nd < mdist[nr][nc]:
                    adist[nr][nc] = nd
                    prev[nr][nc] = (r, c, ch)
                    queue.append((nr, nc))

    return "NO"


# ---------------------------------------------------------------------------
# 1671 - Shortest Routes I (Dijkstra)
# ---------------------------------------------------------------------------
def solve_1671(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        adj[a].append((b, c))

    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[1] = 0
    heap = [(0, 1)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return ' '.join(str(dist[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1672 - Shortest Routes II (Floyd-Warshall)
# ---------------------------------------------------------------------------
def solve_1672(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m, q = map(int, lines[0].split())
    INF = float('inf')
    dist = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dist[i][i] = 0
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        if c < dist[a][b]:
            dist[a][b] = c
            dist[b][a] = c

    for k in range(1, n + 1):
        dk = dist[k]
        for i in range(1, n + 1):
            dik = dist[i][k]
            if dik == INF:
                continue
            di = dist[i]
            for j in range(1, n + 1):
                nd = dik + dk[j]
                if nd < di[j]:
                    di[j] = nd

    result = []
    for i in range(q):
        a, b = map(int, lines[1 + m + i].split())
        d = dist[a][b]
        result.append(str(d) if d != INF else "-1")
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1673 - High Score (longest path 1->n, detect positive cycles)
# ---------------------------------------------------------------------------
def solve_1673(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    edges = []
    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        edges.append((a, b, c))
        adj[a].append(b)
        radj[b].append(a)

    # Find nodes reachable from 1
    reach_from_1 = [False] * (n + 1)
    queue = deque([1])
    reach_from_1[1] = True
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if not reach_from_1[v]:
                reach_from_1[v] = True
                queue.append(v)

    # Find nodes that can reach n (BFS on reverse graph)
    reach_to_n = [False] * (n + 1)
    queue = deque([n])
    reach_to_n[n] = True
    while queue:
        u = queue.popleft()
        for v in radj[u]:
            if not reach_to_n[v]:
                reach_to_n[v] = True
                queue.append(v)

    if not reach_from_1[n]:
        return "-1"

    # Bellman-Ford for longest path (negate weights for shortest path)
    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[1] = 0
    for _ in range(n - 1):
        for a, b, c in edges:
            if dist[a] != INF and dist[a] + (-c) < dist[b]:
                dist[b] = dist[a] + (-c)

    # Check for negative cycles on paths from 1 to n
    for a, b, c in edges:
        if dist[a] != INF and dist[a] + (-c) < dist[b]:
            # Node b is on a negative cycle (in negated graph = positive cycle)
            if reach_from_1[a] and reach_to_n[b]:
                return "-1"

    return str(-dist[n])


# ---------------------------------------------------------------------------
# 1195 - Flight Discount (Dijkstra with state)
# ---------------------------------------------------------------------------
def solve_1195(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        adj[a].append((b, c))

    INF = float('inf')
    # dist[node][used_discount]
    dist = [[INF, INF] for _ in range(n + 1)]
    dist[1][0] = 0
    heap = [(0, 1, 0)]  # (cost, node, used_discount)
    while heap:
        d, u, used = heapq.heappop(heap)
        if d > dist[u][used]:
            continue
        for v, w in adj[u]:
            # Don't use discount
            nd = d + w
            if nd < dist[v][used]:
                dist[v][used] = nd
                heapq.heappush(heap, (nd, v, used))
            # Use discount
            if used == 0:
                nd2 = d + w // 2
                if nd2 < dist[v][1]:
                    dist[v][1] = nd2
                    heapq.heappush(heap, (nd2, v, 1))
    return str(min(dist[n][0], dist[n][1]))


# ---------------------------------------------------------------------------
# 1197 - Cycle Finding (negative cycle in directed graph)
# ---------------------------------------------------------------------------
def solve_1197(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    edges = []
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        edges.append((a, b, c))

    INF = float('inf')
    dist = [0] * (n + 1)  # Initialize all to 0 to detect any negative cycle
    prev = [0] * (n + 1)
    last_relaxed = -1

    for iteration in range(n):
        last_relaxed = -1
        for a, b, c in edges:
            if dist[a] + c < dist[b]:
                dist[b] = dist[a] + c
                prev[b] = a
                last_relaxed = b

    if last_relaxed == -1:
        return "NO"

    # Trace back n steps to ensure we're in the cycle
    x = last_relaxed
    for _ in range(n):
        x = prev[x]

    # Now x is in the cycle, trace it
    cycle = []
    cur = x
    while True:
        cycle.append(cur)
        cur = prev[cur]
        if cur == x:
            break
    cycle.append(x)
    cycle.reverse()
    return "YES\n" + ' '.join(map(str, cycle))


# ---------------------------------------------------------------------------
# 1196 - Flight Routes (k shortest paths)
# ---------------------------------------------------------------------------
def solve_1196(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m, k = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        adj[a].append((b, c))

    count = [0] * (n + 1)
    results = []
    heap = [(0, 1)]
    while heap and count[n] < k:
        d, u = heapq.heappop(heap)
        count[u] += 1
        if count[u] > k:
            continue
        if u == n:
            results.append(d)
            if len(results) == k:
                break
            continue
        for v, w in adj[u]:
            if count[v] < k:
                heapq.heappush(heap, (d + w, v))

    return ' '.join(map(str, results))


# ---------------------------------------------------------------------------
# 1678 - Round Trip II (directed cycle)
# ---------------------------------------------------------------------------
def solve_1678(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)

    # Iterative DFS with coloring: 0=white, 1=gray, 2=black
    color = [0] * (n + 1)
    parent = [0] * (n + 1)

    for s in range(1, n + 1):
        if color[s] != 0:
            continue
        stack = [(s, 0)]
        color[s] = 1
        while stack:
            u, idx = stack[-1]
            if idx < len(adj[u]):
                stack[-1] = (u, idx + 1)
                v = adj[u][idx]
                if color[v] == 1:
                    # Found cycle: v -> ... -> u -> v
                    cycle = [v]
                    cur = u
                    while cur != v:
                        cycle.append(cur)
                        # find parent on stack
                        cur = parent[cur]
                    cycle.append(v)
                    cycle.reverse()
                    return str(len(cycle)) + "\n" + ' '.join(map(str, cycle))
                elif color[v] == 0:
                    color[v] = 1
                    parent[v] = u
                    stack.append((v, 0))
            else:
                color[u] = 2
                stack.pop()

    return "IMPOSSIBLE"


# ---------------------------------------------------------------------------
# 1679 - Course Schedule (topological sort)
# ---------------------------------------------------------------------------
def solve_1679(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        indeg[b] += 1

    queue = deque()
    for i in range(1, n + 1):
        if indeg[i] == 0:
            queue.append(i)

    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)

    if len(order) != n:
        return "IMPOSSIBLE"
    return ' '.join(map(str, order))


# ---------------------------------------------------------------------------
# 1680 - Longest Flight Route (longest path in DAG from 1 to n)
# ---------------------------------------------------------------------------
def solve_1680(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        radj[b].append(a)
        indeg[b] += 1

    # Topological sort (Kahn's)
    queue = deque()
    for i in range(1, n + 1):
        if indeg[i] == 0:
            queue.append(i)
    topo = []
    in_deg_copy = indeg[:]
    while queue:
        u = queue.popleft()
        topo.append(u)
        for v in adj[u]:
            in_deg_copy[v] -= 1
            if in_deg_copy[v] == 0:
                queue.append(v)

    # DP for longest path from 1
    dist = [-1] * (n + 1)
    dist[1] = 0
    prev = [0] * (n + 1)
    for u in topo:
        if dist[u] == -1:
            continue
        for v in adj[u]:
            if dist[u] + 1 > dist[v]:
                dist[v] = dist[u] + 1
                prev[v] = u

    if dist[n] == -1:
        return "IMPOSSIBLE"

    path = []
    cur = n
    while cur != 0:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return str(len(path)) + "\n" + ' '.join(map(str, path))


# ---------------------------------------------------------------------------
# 1681 - Game Routes (count paths 1->n in DAG)
# ---------------------------------------------------------------------------
def solve_1681(input_data: str) -> str:
    MOD = 10**9 + 7
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        indeg[b] += 1

    queue = deque()
    for i in range(1, n + 1):
        if indeg[i] == 0:
            queue.append(i)
    topo = []
    in_deg_copy = indeg[:]
    while queue:
        u = queue.popleft()
        topo.append(u)
        for v in adj[u]:
            in_deg_copy[v] -= 1
            if in_deg_copy[v] == 0:
                queue.append(v)

    dp = [0] * (n + 1)
    dp[1] = 1
    for u in topo:
        if dp[u] == 0:
            continue
        for v in adj[u]:
            dp[v] = (dp[v] + dp[u]) % MOD

    return str(dp[n])


# ---------------------------------------------------------------------------
# 1202 - Investigation (Dijkstra: dist, #paths, min edges, max edges)
# ---------------------------------------------------------------------------
def solve_1202(input_data: str) -> str:
    MOD = 10**9 + 7
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        adj[a].append((b, c))

    INF = float('inf')
    dist = [INF] * (n + 1)
    cnt = [0] * (n + 1)
    min_e = [INF] * (n + 1)
    max_e = [0] * (n + 1)
    dist[1] = 0
    cnt[1] = 1
    min_e[1] = 0
    max_e[1] = 0
    heap = [(0, 1)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                cnt[v] = cnt[u]
                min_e[v] = min_e[u] + 1
                max_e[v] = max_e[u] + 1
                heapq.heappush(heap, (nd, v))
            elif nd == dist[v]:
                cnt[v] = (cnt[v] + cnt[u]) % MOD
                min_e[v] = min(min_e[v], min_e[u] + 1)
                max_e[v] = max(max_e[v], max_e[u] + 1)

    return f"{dist[n]} {cnt[n] % MOD} {min_e[n]} {max_e[n]}"


# ---------------------------------------------------------------------------
# 1750 - Planets Queries I (binary lifting on functional graph)
# ---------------------------------------------------------------------------
def solve_1750(input_data: str) -> str:
    lines = input_data.split('\n')
    n, q = map(int, lines[0].split())
    t = list(map(int, lines[1].split()))

    LOG = 30
    up = [[0] * (n + 1) for _ in range(LOG)]
    for i in range(1, n + 1):
        up[0][i] = t[i - 1]
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]

    result = []
    for i in range(q):
        x, k = map(int, lines[2 + i].split())
        cur = x
        for j in range(LOG):
            if k & (1 << j):
                cur = up[j][cur]
        result.append(str(cur))
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1160 - Planets Queries II (functional graph, min steps a->b)
# ---------------------------------------------------------------------------
def solve_1160(input_data: str) -> str:
    lines = input_data.split('\n')
    n, q = map(int, lines[0].split())
    succ = [0] * (n + 1)
    vals = list(map(int, lines[1].split()))
    for i in range(n):
        succ[i + 1] = vals[i]

    # Find cycles: each node is in exactly one "rho" shape
    # We need to find for each node: which cycle it belongs to, distance to cycle,
    # position in cycle, cycle length.

    # Step 1: Find all cycles
    visited = [0] * (n + 1)  # 0=unvisited, 1=in progress, 2=done
    in_cycle = [False] * (n + 1)
    cycle_id = [0] * (n + 1)
    cycle_pos = [0] * (n + 1)
    cycle_len = [0] * (n + 1)
    dist_to_cycle = [0] * (n + 1)
    cycle_entry = [0] * (n + 1)  # which cycle node this tail enters

    num_cycles = 0
    cycles = []  # list of lists

    for s in range(1, n + 1):
        if visited[s] != 0:
            continue
        path = []
        cur = s
        while visited[cur] == 0:
            visited[cur] = 1
            path.append(cur)
            cur = succ[cur]

        if visited[cur] == 1:
            # Found a new cycle
            num_cycles += 1
            cid = num_cycles
            cycle = []
            idx = 0
            # Find where cur is in path
            start_idx = 0
            for pi in range(len(path)):
                if path[pi] == cur:
                    start_idx = pi
                    break
            for pi in range(start_idx, len(path)):
                node = path[pi]
                in_cycle[node] = True
                cycle_id[node] = cid
                cycle_pos[node] = idx
                visited[node] = 2
                cycle.append(node)
                idx += 1
            cl = len(cycle)
            for node in cycle:
                cycle_len[node] = cl
            cycles.append(cycle)
            # Nodes before start_idx are tails
            for pi in range(start_idx):
                visited[path[pi]] = 2
        else:
            # cur is already processed (visited[cur] == 2)
            for node in path:
                visited[node] = 2

    # Step 2: For tail nodes, find distance to cycle and cycle_entry
    # Process tails: for each node not in cycle, follow until we reach a cycle node
    # Use iterative approach
    for s in range(1, n + 1):
        if in_cycle[s]:
            dist_to_cycle[s] = 0
            cycle_entry[s] = s
            continue
        # Follow chain until we hit a node with known distance
        chain = []
        cur = s
        while not in_cycle[cur] and dist_to_cycle[cur] == 0 and cur != succ[cur] and cycle_id[cur] == 0:
            chain.append(cur)
            cur = succ[cur]
            if cur == s:
                break  # shouldn't happen since we identified all cycles

    # Actually, let's redo this more carefully
    # Reset
    dist_to_cycle = [-1] * (n + 1)
    for s in range(1, n + 1):
        if in_cycle[s]:
            dist_to_cycle[s] = 0
            cycle_entry[s] = s

    for s in range(1, n + 1):
        if dist_to_cycle[s] != -1:
            continue
        chain = []
        cur = s
        while dist_to_cycle[cur] == -1:
            chain.append(cur)
            cur = succ[cur]
        # cur now has known dist_to_cycle
        d = dist_to_cycle[cur]
        ce = cycle_entry[cur] if in_cycle[cur] or d >= 0 else cur
        if in_cycle[cur]:
            ce = cur
        else:
            ce = cycle_entry[cur]
        cid = cycle_id[ce] if in_cycle[ce] else cycle_id[cycle_entry[cur]] if dist_to_cycle[cur] >= 0 else 0

        for i in range(len(chain) - 1, -1, -1):
            d += 1
            node = chain[i]
            dist_to_cycle[node] = d
            cycle_entry[node] = ce
            cycle_id[node] = cycle_id[ce]

    # Binary lifting for following successor
    LOG = 30
    up = [[0] * (n + 1) for _ in range(LOG)]
    for i in range(1, n + 1):
        up[0][i] = succ[i]
    for j in range(1, LOG):
        for i in range(1, n + 1):
            up[j][i] = up[j - 1][up[j - 1][i]]

    def lift(x, k):
        cur = x
        for j in range(LOG):
            if k & (1 << j):
                cur = up[j][cur]
        return cur

    result = []
    for i in range(q):
        a, b = map(int, lines[2 + i].split())
        if a == b:
            result.append("0")
            continue

        # Case 1: b is on the tail from a (a can reach b by following successor)
        da = dist_to_cycle[a]
        db = dist_to_cycle[b]

        if not in_cycle[a] and not in_cycle[b]:
            # Both on tails
            if cycle_id[a] != cycle_id[b]:
                result.append("-1")
                continue
            if cycle_entry[a] == cycle_entry[b]:
                # Same tail
                if da > db:
                    # a might reach b by going da-db steps
                    steps = da - db
                    if lift(a, steps) == b:
                        result.append(str(steps))
                    else:
                        result.append("-1")
                else:
                    result.append("-1")
            else:
                # Different tails going to same cycle
                # a must go through cycle to reach b? b is on a different tail, unreachable
                # Actually if a's tail passes through b... no, tails are trees
                # a goes to cycle_entry[a], can it then reach b? b is on a tail,
                # only way to reach b is if a is an ancestor of b in the tail tree
                # Check if a can reach b directly
                if da > db:
                    steps = da - db
                    if lift(a, steps) == b:
                        result.append(str(steps))
                        continue
                result.append("-1")
                continue
        elif not in_cycle[a] and in_cycle[b]:
            # a on tail, b on cycle
            if cycle_id[a] != cycle_id[b]:
                result.append("-1")
                continue
            # a goes to cycle_entry[a] in da steps, then around cycle to b
            ea = cycle_entry[a]
            steps_to_cycle = da
            # From ea to b on cycle
            cl = cycle_len[b]
            pos_ea = cycle_pos[ea]
            pos_b = cycle_pos[b]
            steps_on_cycle = (pos_b - pos_ea) % cl
            result.append(str(steps_to_cycle + steps_on_cycle))
        elif in_cycle[a] and not in_cycle[b]:
            # a on cycle, b on tail: can't reach tail from cycle
            result.append("-1")
        else:
            # Both on cycle
            if cycle_id[a] != cycle_id[b]:
                result.append("-1")
                continue
            cl = cycle_len[a]
            pos_a = cycle_pos[a]
            pos_b = cycle_pos[b]
            steps = (pos_b - pos_a) % cl
            result.append(str(steps))

    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1751 - Planets Cycles
# ---------------------------------------------------------------------------
def solve_1751(input_data: str) -> str:
    lines = input_data.split('\n')
    n = int(lines[0])
    succ = [0] * (n + 1)
    vals = list(map(int, lines[1].split()))
    for i in range(n):
        succ[i + 1] = vals[i]

    ans = [0] * (n + 1)
    # States: 0=unvisited, -1=being visited, >0=done
    state = [0] * (n + 1)

    for s in range(1, n + 1):
        if state[s] != 0:
            continue
        path = []
        cur = s
        while state[cur] == 0:
            state[cur] = -1
            path.append(cur)
            cur = succ[cur]

        if state[cur] == -1:
            # Found cycle, cur is in the cycle
            # Find cycle length
            cycle_start_idx = 0
            for pi in range(len(path)):
                if path[pi] == cur:
                    cycle_start_idx = pi
                    break
            cycle_length = len(path) - cycle_start_idx
            # Set answer for cycle nodes
            for pi in range(cycle_start_idx, len(path)):
                ans[path[pi]] = cycle_length
                state[path[pi]] = 1
            # Set answer for tail nodes
            for pi in range(cycle_start_idx - 1, -1, -1):
                ans[path[pi]] = ans[succ[path[pi]]] + 1
                state[path[pi]] = 1
        else:
            # cur already processed
            for pi in range(len(path) - 1, -1, -1):
                ans[path[pi]] = ans[succ[path[pi]]] + 1
                state[path[pi]] = 1

    return ' '.join(str(ans[i]) for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 1675 - Road Reparation (MST, Kruskal's)
# ---------------------------------------------------------------------------
def solve_1675(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    edges = []
    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        edges.append((c, a, b))
    edges.sort()

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
            return False
        if rank[a] < rank[b]:
            a, b = b, a
        parent[b] = a
        if rank[a] == rank[b]:
            rank[a] += 1
        return True

    total = 0
    edges_used = 0
    for c, a, b in edges:
        if union(a, b):
            total += c
            edges_used += 1
            if edges_used == n - 1:
                break

    if edges_used < n - 1:
        return "IMPOSSIBLE"
    return str(total)


# ---------------------------------------------------------------------------
# 1676 - Road Construction (Union-Find, online)
# ---------------------------------------------------------------------------
def solve_1676(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    parent = list(range(n + 1))
    sz = [1] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    num_components = n
    max_size = 1
    result = []
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        ra, rb = find(a), find(b)
        if ra != rb:
            num_components -= 1
            if sz[ra] < sz[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            sz[ra] += sz[rb]
            if sz[ra] > max_size:
                max_size = sz[ra]
        result.append(f"{num_components} {max_size}")
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1682 - Flight Routes Check (strongly connected check)
# ---------------------------------------------------------------------------
def solve_1682(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        radj[b].append(a)

    # BFS from 1 on original graph
    visited = [False] * (n + 1)
    queue = deque([1])
    visited[1] = True
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
    for i in range(1, n + 1):
        if not visited[i]:
            return f"NO\n{1} {i}"

    # BFS from 1 on reversed graph
    visited2 = [False] * (n + 1)
    queue = deque([1])
    visited2[1] = True
    while queue:
        u = queue.popleft()
        for v in radj[u]:
            if not visited2[v]:
                visited2[v] = True
                queue.append(v)
    for i in range(1, n + 1):
        if not visited2[i]:
            return f"NO\n{i} {1}"

    return "YES"


# ---------------------------------------------------------------------------
# 1683 - Planets and Kingdoms (SCCs - Kosaraju's)
# ---------------------------------------------------------------------------
def solve_1683(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        radj[b].append(a)

    # Kosaraju's algorithm
    visited = [False] * (n + 1)
    order = []

    # Iterative DFS for finish order
    for s in range(1, n + 1):
        if visited[s]:
            continue
        stack = [(s, 0)]
        visited[s] = True
        while stack:
            u, idx = stack[-1]
            if idx < len(adj[u]):
                stack[-1] = (u, idx + 1)
                v = adj[u][idx]
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)
                stack.pop()

    # Second pass on reversed graph
    comp = [0] * (n + 1)
    visited = [False] * (n + 1)
    num_comp = 0
    for s in reversed(order):
        if visited[s]:
            continue
        num_comp += 1
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            comp[u] = num_comp
            for v in radj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

    result = [str(num_comp)]
    result.append(' '.join(str(comp[i]) for i in range(1, n + 1)))
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1684 - Giant Pizza (2-SAT)
# ---------------------------------------------------------------------------
def solve_1684(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    # n clauses, m variables (toppings)
    # Each clause: sign1 var1 sign2 var2
    # Variable x: true literal = 2*x, false literal = 2*x+1
    # For 2-SAT: (a OR b) => (!a => b) and (!b => a)

    def var_lit(sign, x):
        # sign '+' means true, '-' means false
        if sign == '+':
            return 2 * x
        else:
            return 2 * x + 1

    def neg(lit):
        return lit ^ 1

    num_nodes = 2 * (m + 1)
    adj = [[] for _ in range(num_nodes)]
    radj = [[] for _ in range(num_nodes)]

    for i in range(n):
        parts = lines[1 + i].split()
        s1, x1_str, s2, x2_str = parts[0], parts[1], parts[2], parts[3]
        x1, x2 = int(x1_str), int(x2_str)
        a = var_lit(s1, x1)
        b = var_lit(s2, x2)
        # (a OR b) => (!a => b) and (!b => a)
        adj[neg(a)].append(b)
        adj[neg(b)].append(a)
        radj[b].append(neg(a))
        radj[a].append(neg(b))

    # Kosaraju's SCC
    visited = [False] * num_nodes
    order = []
    for s in range(2, num_nodes):
        if visited[s]:
            continue
        stack = [(s, 0)]
        visited[s] = True
        while stack:
            u, idx = stack[-1]
            if idx < len(adj[u]):
                stack[-1] = (u, idx + 1)
                v = adj[u][idx]
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)
                stack.pop()

    comp = [0] * num_nodes
    visited = [False] * num_nodes
    num_comp = 0
    for s in reversed(order):
        if visited[s]:
            continue
        num_comp += 1
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            comp[u] = num_comp
            for v in radj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

    # Check satisfiability
    for x in range(1, m + 1):
        if comp[2 * x] == comp[2 * x + 1]:
            return "IMPOSSIBLE"

    # Extract assignment: variable is true if comp[true_lit] > comp[false_lit]
    # (in Kosaraju's, later SCC number = earlier in topological order)
    result = []
    for x in range(1, m + 1):
        if comp[2 * x] > comp[2 * x + 1]:
            result.append('+')
        else:
            result.append('-')

    return ' '.join(result)


# ---------------------------------------------------------------------------
# 1686 - Coin Collector (SCC condensation + longest path in DAG)
# ---------------------------------------------------------------------------
def solve_1686(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    coins = [0] * (n + 1)
    vals = list(map(int, lines[1].split()))
    for i in range(n):
        coins[i + 1] = vals[i]

    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = map(int, lines[2 + i].split())
        adj[a].append(b)
        radj[b].append(a)

    # Kosaraju's SCC
    visited = [False] * (n + 1)
    order = []
    for s in range(1, n + 1):
        if visited[s]:
            continue
        stack = [(s, 0)]
        visited[s] = True
        while stack:
            u, idx = stack[-1]
            if idx < len(adj[u]):
                stack[-1] = (u, idx + 1)
                v = adj[u][idx]
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)
                stack.pop()

    comp = [0] * (n + 1)
    visited = [False] * (n + 1)
    num_comp = 0
    for s in reversed(order):
        if visited[s]:
            continue
        num_comp += 1
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            comp[u] = num_comp
            for v in radj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

    # Build condensed DAG
    scc_coins = [0] * (num_comp + 1)
    for i in range(1, n + 1):
        scc_coins[comp[i]] += coins[i]

    scc_adj = [set() for _ in range(num_comp + 1)]
    for u in range(1, n + 1):
        for v in adj[u]:
            if comp[u] != comp[v]:
                scc_adj[comp[u]].add(comp[v])

    # Topological sort of condensed graph (Kahn's)
    indeg = [0] * (num_comp + 1)
    for u in range(1, num_comp + 1):
        for v in scc_adj[u]:
            indeg[v] += 1

    queue = deque()
    for i in range(1, num_comp + 1):
        if indeg[i] == 0:
            queue.append(i)

    topo = []
    while queue:
        u = queue.popleft()
        topo.append(u)
        for v in scc_adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)

    # DP longest path
    dp = [0] * (num_comp + 1)
    for u in topo:
        dp[u] = max(dp[u], scc_coins[u])
        for v in scc_adj[u]:
            dp[v] = max(dp[v], dp[u] + scc_coins[v])

    return str(max(dp[1:num_comp + 1]))


# ---------------------------------------------------------------------------
# 1691 - Mail Delivery (Eulerian circuit, undirected)
# ---------------------------------------------------------------------------
def solve_1691(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())

    if m == 0:
        if n == 1:
            return "1"
        return "IMPOSSIBLE"

    # Build adjacency list with edge indices for efficient removal
    adj = [[] for _ in range(n + 1)]
    degree = [0] * (n + 1)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append([b, i, len(adj[b])])
        adj[b].append([a, i, len(adj[a]) - 1])
        # Fix cross-references
        adj[a][-1][2] = len(adj[b]) - 1
        degree[a] += 1
        degree[b] += 1

    # Check all degrees are even
    for i in range(1, n + 1):
        if degree[i] % 2 != 0:
            return "IMPOSSIBLE"

    # Check connectivity (only among vertices with edges)
    vertices_with_edges = [i for i in range(1, n + 1) if degree[i] > 0]
    if not vertices_with_edges:
        return "1"

    visited = [False] * (n + 1)
    queue = deque([vertices_with_edges[0]])
    visited[vertices_with_edges[0]] = True
    while queue:
        u = queue.popleft()
        for entry in adj[u]:
            v = entry[0]
            if not visited[v]:
                visited[v] = True
                queue.append(v)
    for v in vertices_with_edges:
        if not visited[v]:
            return "IMPOSSIBLE"

    # Hierholzer's algorithm
    used_edge = [False] * m
    ptr = [0] * (n + 1)
    circuit = []
    stack = [1]
    while stack:
        u = stack[-1]
        while ptr[u] < len(adj[u]) and used_edge[adj[u][ptr[u]][1]]:
            ptr[u] += 1
        if ptr[u] < len(adj[u]):
            entry = adj[u][ptr[u]]
            v, eidx, _ = entry
            used_edge[eidx] = True
            ptr[u] += 1
            stack.append(v)
        else:
            circuit.append(u)
            stack.pop()

    if len(circuit) != m + 1:
        return "IMPOSSIBLE"

    circuit.reverse()
    return ' '.join(map(str, circuit))


# ---------------------------------------------------------------------------
# 1692 - De Bruijn Sequence
# ---------------------------------------------------------------------------
def solve_1692(input_data: str) -> str:
    n = int(input_data.strip())
    if n == 1:
        return "01"

    # Build De Bruijn graph: nodes are (n-1)-bit strings, edges are n-bit strings
    # Eulerian circuit on this graph gives De Bruijn sequence
    num_nodes = 1 << (n - 1)
    mask = num_nodes - 1

    # Each node u has edges to (u<<1)&mask | 0 and (u<<1)&mask | 1
    # Hierholzer's
    ptr = [0] * num_nodes
    circuit = []
    stack = [0]

    while stack:
        u = stack[-1]
        if ptr[u] < 2:
            bit = ptr[u]
            ptr[u] += 1
            v = ((u << 1) | bit) & mask
            stack.append(v)
        else:
            circuit.append(stack.pop())

    circuit.reverse()
    # The sequence is formed by taking the last bit of each edge
    # circuit has num_edges+1 = 2^n + 1 nodes
    # Each transition from circuit[i] to circuit[i+1] gives a bit
    result = []
    for i in range(len(circuit) - 1):
        result.append(str(circuit[i + 1] & 1))

    return ''.join(result)


# ---------------------------------------------------------------------------
# 1693 - Teleporters Path (Eulerian path in directed graph, 1 to n)
# ---------------------------------------------------------------------------
def solve_1693(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())

    adj = [[] for _ in range(n + 1)]
    in_deg = [0] * (n + 1)
    out_deg = [0] * (n + 1)

    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)
        out_deg[a] += 1
        in_deg[b] += 1

    # For Eulerian path from 1 to n:
    # out_deg[1] = in_deg[1] + 1
    # in_deg[n] = out_deg[n] + 1
    # all others: in_deg = out_deg
    ok = True
    if out_deg[1] != in_deg[1] + 1:
        ok = False
    if in_deg[n] != out_deg[n] + 1:
        ok = False
    for i in range(1, n + 1):
        if i == 1 or i == n:
            continue
        if in_deg[i] != out_deg[i]:
            ok = False
            break

    if not ok:
        return "IMPOSSIBLE"

    # Hierholzer's from node 1
    ptr = [0] * (n + 1)
    circuit = []
    stack = [1]

    while stack:
        u = stack[-1]
        if ptr[u] < len(adj[u]):
            v = adj[u][ptr[u]]
            ptr[u] += 1
            stack.append(v)
        else:
            circuit.append(u)
            stack.pop()

    circuit.reverse()

    if len(circuit) != m + 1 or circuit[-1] != n:
        return "IMPOSSIBLE"

    return ' '.join(map(str, circuit))


# ---------------------------------------------------------------------------
# 1690 - Hamiltonian Flights (bitmask DP, 1 to n)
# ---------------------------------------------------------------------------
def solve_1690(input_data: str) -> str:
    MOD = 10**9 + 7
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())
    # Edges: directed a->b
    # adj_in[v] = list of u such that u->v
    adj_in = [[] for _ in range(n)]
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        a -= 1
        b -= 1
        adj_in[b].append(a)

    # dp[mask][i] = number of ways to visit exactly the nodes in mask, ending at i
    full = (1 << n) - 1
    dp = [[0] * n for _ in range(1 << n)]
    dp[1][0] = 1  # Start at node 0 (city 1), mask = {0}

    for mask in range(1, 1 << n):
        for v in range(n):
            if not (mask & (1 << v)):
                continue
            if dp[mask][v] == 0:
                continue
            # This is a "push" DP variant - but let's do pull
            pass

    # Redo with pull
    dp = [[0] * n for _ in range(1 << n)]
    dp[1][0] = 1

    for mask in range(1, 1 << n):
        for v in range(n):
            if not (mask & (1 << v)):
                continue
            # v must be the last node visited, pull from predecessors
            if v == 0 and mask == 1:
                continue  # base case already set
            if v == 0 and mask != 1:
                continue  # node 0 should only be first
            prev_mask = mask ^ (1 << v)
            if prev_mask == 0:
                continue
            for u in adj_in[v]:
                if prev_mask & (1 << u):
                    dp[mask][v] = (dp[mask][v] + dp[prev_mask][u]) % MOD

    return str(dp[full][n - 1])


# ---------------------------------------------------------------------------
# 1689 - Knight's Tour (Warnsdorff's heuristic)
# ---------------------------------------------------------------------------
def solve_1689(input_data: str) -> str:
    lines = input_data.split('\n')
    n = int(lines[0].split()[0])
    # Starting position (1-indexed)
    parts = lines[0].split()
    x0, y0 = int(parts[1]), int(parts[2])

    board = [[0] * (n + 1) for _ in range(n + 1)]
    moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
             (1, -2), (1, 2), (2, -1), (2, 1)]

    def count_moves(r, c):
        cnt = 0
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 1 <= nr <= n and 1 <= nc <= n and board[nr][nc] == 0:
                cnt += 1
        return cnt

    def solve_tour(r, c):
        board[r][c] = 1
        path = [(r, c)]
        total = n * n

        for step in range(2, total + 1):
            # Find next move using Warnsdorff's heuristic
            best = None
            best_count = 9
            for dr, dc in moves:
                nr, nc = r + dr, c + dc
                if 1 <= nr <= n and 1 <= nc <= n and board[nr][nc] == 0:
                    cnt = count_moves(nr, nc)
                    if cnt < best_count:
                        best_count = cnt
                        best = (nr, nc)
                    elif cnt == best_count and best is not None:
                        # Tie-break: prefer position closer to corner for better coverage
                        pass

            if best is None:
                return None  # Failed
            r, c = best
            board[r][c] = step
            path.append((r, c))

        return path

    # Try Warnsdorff's
    path = solve_tour(y0, x0)

    if path is None:
        # Fallback: try with backtracking for small n
        for row in range(1, n + 1):
            for col in range(1, n + 1):
                board[row][col] = 0

        def backtrack(r, c, step):
            if step == n * n:
                return True
            candidates = []
            for dr, dc in moves:
                nr, nc = r + dr, c + dc
                if 1 <= nr <= n and 1 <= nc <= n and board[nr][nc] == 0:
                    cnt = count_moves(nr, nc)
                    candidates.append((cnt, nr, nc))
            candidates.sort()
            for _, nr, nc in candidates:
                board[nr][nc] = step + 1
                if backtrack(nr, nc, step + 1):
                    return True
                board[nr][nc] = 0
            return False

        board[y0][x0] = 1
        backtrack(y0, x0, 1)

    # Output the board
    result = []
    for row in range(1, n + 1):
        result.append(' '.join(str(board[row][col]) for col in range(1, n + 1)))
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1694 - Download Speed (Max flow - Dinic's algorithm)
# ---------------------------------------------------------------------------
def solve_1694(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())

    # Dinic's max flow
    head = [-1] * (n + 1)
    to = []
    cap = []
    nxt = []
    edge_cnt = 0

    def add_edge(u, v, c):
        nonlocal edge_cnt
        to.append(v)
        cap.append(c)
        nxt.append(head[u])
        head[u] = edge_cnt
        edge_cnt += 1

        to.append(u)
        cap.append(0)
        nxt.append(head[v])
        head[v] = edge_cnt
        edge_cnt += 1

    for i in range(m):
        a, b, c = map(int, lines[1 + i].split())
        add_edge(a, b, c)

    source, sink = 1, n

    def bfs():
        level = [-1] * (n + 1)
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            e = head[u]
            while e != -1:
                v = to[e]
                if level[v] == -1 and cap[e] > 0:
                    level[v] = level[u] + 1
                    queue.append(v)
                e = nxt[e]
        return level[sink] != -1, level

    def dfs(u, pushed, level, iter_):
        if u == sink:
            return pushed
        while iter_[u] != -1:
            e = iter_[u]
            v = to[e]
            if level[v] == level[u] + 1 and cap[e] > 0:
                d = dfs(v, min(pushed, cap[e]), level, iter_)
                if d > 0:
                    cap[e] -= d
                    cap[e ^ 1] += d
                    return d
            iter_[u] = nxt[iter_[u]] if iter_[u] != -1 else -1
            # Actually we should advance iter_[u]
            break
        return 0

    # Proper iterative Dinic's DFS
    def dinic_dfs(level):
        iter_ = head[:]
        total = 0
        while True:
            # Find augmenting path using iterative DFS
            stack = [(source, float('inf'))]
            path_edges = []
            found = False
            # Reset iter for blocking flow
            flow = blocking_flow(level, iter_)
            total += flow
            if flow == 0:
                break
        return total

    def blocking_flow(level, iter_):
        total = 0
        while True:
            # Iterative DFS
            stack = [source]
            edge_stack = []
            visited_in_path = set()
            found = False

            # Simple iterative approach
            path = []
            path_edges_list = []
            cur = source
            pushed_total = 0

            while True:
                if cur == sink:
                    # Find bottleneck
                    bottleneck = float('inf')
                    for e_idx in path_edges_list:
                        bottleneck = min(bottleneck, cap[e_idx])
                    # Update
                    for e_idx in path_edges_list:
                        cap[e_idx] -= bottleneck
                        cap[e_idx ^ 1] += bottleneck
                    pushed_total += bottleneck
                    # Retreat to the node just before bottleneck edge
                    # Find first saturated edge
                    retreat_to = 0
                    for pi, e_idx in enumerate(path_edges_list):
                        if cap[e_idx] == 0:
                            retreat_to = pi
                            break
                    path = path[:retreat_to]
                    path_edges_list = path_edges_list[:retreat_to]
                    if not path:
                        cur = source
                    else:
                        cur = to[path_edges_list[-1]]
                    continue

                # Try to advance
                advanced = False
                while iter_[cur] != -1:
                    e = iter_[cur]
                    v = to[e]
                    if level[v] == level[cur] + 1 and cap[e] > 0:
                        path.append(cur)
                        path_edges_list.append(e)
                        cur = v
                        advanced = True
                        break
                    iter_[cur] = nxt[e]
                if not advanced:
                    if cur == source:
                        break
                    # Retreat
                    level[cur] = -1  # Remove from level graph
                    if path:
                        cur = path.pop()
                        path_edges_list.pop()
                    else:
                        break

            return pushed_total

    # Rewrite Dinic's properly
    max_flow = 0
    while True:
        found, level = bfs()
        if not found:
            break
        iter_ = head[:]
        flow = blocking_flow(level, iter_)
        max_flow += flow

    return str(max_flow)


# ---------------------------------------------------------------------------
# 1695 - Police Chase (min cut in undirected graph)
# ---------------------------------------------------------------------------
def solve_1695(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())

    # Build flow network (same as Dinic's)
    head = [-1] * (n + 1)
    to = []
    cap = []
    nxt = []
    edge_cnt = 0

    def add_edge(u, v, c):
        nonlocal edge_cnt
        to.append(v)
        cap.append(c)
        nxt.append(head[u])
        head[u] = edge_cnt
        edge_cnt += 1

        to.append(u)
        cap.append(0)
        nxt.append(head[v])
        head[v] = edge_cnt
        edge_cnt += 1

    original_edges = []
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        original_edges.append((a, b))
        add_edge(a, b, 1)
        add_edge(b, a, 1)

    source, sink = 1, n

    def bfs():
        level = [-1] * (n + 1)
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            e = head[u]
            while e != -1:
                v = to[e]
                if level[v] == -1 and cap[e] > 0:
                    level[v] = level[u] + 1
                    queue.append(v)
                e = nxt[e]
        return level[sink] != -1, level

    def blocking_flow(level, iter_):
        pushed_total = 0
        while True:
            path = []
            path_edges_list = []
            cur = source

            while True:
                if cur == sink:
                    bottleneck = float('inf')
                    for e_idx in path_edges_list:
                        bottleneck = min(bottleneck, cap[e_idx])
                    for e_idx in path_edges_list:
                        cap[e_idx] -= bottleneck
                        cap[e_idx ^ 1] += bottleneck
                    pushed_total += bottleneck
                    retreat_to = 0
                    for pi, e_idx in enumerate(path_edges_list):
                        if cap[e_idx] == 0:
                            retreat_to = pi
                            break
                    path = path[:retreat_to]
                    path_edges_list = path_edges_list[:retreat_to]
                    cur = source if not path else to[path_edges_list[-1]]
                    continue

                advanced = False
                while iter_[cur] != -1:
                    e = iter_[cur]
                    v = to[e]
                    if level[v] == level[cur] + 1 and cap[e] > 0:
                        path.append(cur)
                        path_edges_list.append(e)
                        cur = v
                        advanced = True
                        break
                    iter_[cur] = nxt[e]
                if not advanced:
                    if cur == source:
                        break
                    level[cur] = -1
                    if path:
                        cur = path.pop()
                        path_edges_list.pop()
                    else:
                        break
            return pushed_total

    max_flow = 0
    while True:
        found, level = bfs()
        if not found:
            break
        iter_ = head[:]
        max_flow += blocking_flow(level, iter_)

    # Find min cut: BFS from source on residual graph
    reachable = [False] * (n + 1)
    queue = deque([source])
    reachable[source] = True
    while queue:
        u = queue.popleft()
        e = head[u]
        while e != -1:
            v = to[e]
            if not reachable[v] and cap[e] > 0:
                reachable[v] = True
                queue.append(v)
            e = nxt[e]

    cut_edges = []
    for a, b in original_edges:
        if (reachable[a] and not reachable[b]) or (reachable[b] and not reachable[a]):
            cut_edges.append((a, b))

    result = [str(len(cut_edges))]
    for a, b in cut_edges:
        result.append(f"{a} {b}")
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1696 - School Dance (maximum bipartite matching)
# ---------------------------------------------------------------------------
def solve_1696(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m, k = map(int, lines[0].split())
    # n boys, m girls, k pairs
    adj = [[] for _ in range(n + 1)]
    for i in range(k):
        a, b = map(int, lines[1 + i].split())
        adj[a].append(b)

    match_girl = [0] * (m + 1)  # which boy is matched to girl j
    match_boy = [0] * (n + 1)   # which girl is matched to boy i

    def try_kuhn(u, visited):
        for v in adj[u]:
            if visited[v]:
                continue
            visited[v] = True
            if match_girl[v] == 0 or try_kuhn(match_girl[v], visited):
                match_girl[v] = u
                match_boy[u] = v
                return True
        return False

    matching = 0
    for i in range(1, n + 1):
        visited = [False] * (m + 1)
        if try_kuhn(i, visited):
            matching += 1

    result = [str(matching)]
    for i in range(1, n + 1):
        if match_boy[i] != 0:
            result.append(f"{i} {match_boy[i]}")
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# 1711 - Distinct Routes (edge-disjoint paths via max flow)
# ---------------------------------------------------------------------------
def solve_1711(input_data: str) -> str:
    lines = input_data.split('\n')
    n, m = map(int, lines[0].split())

    head = [-1] * (n + 1)
    to = []
    cap = []
    nxt = []
    edge_cnt = 0

    def add_edge(u, v, c):
        nonlocal edge_cnt
        to.append(v)
        cap.append(c)
        nxt.append(head[u])
        head[u] = edge_cnt
        edge_cnt += 1

        to.append(u)
        cap.append(0)
        nxt.append(head[v])
        head[v] = edge_cnt
        edge_cnt += 1

    edge_info = []  # (from, to) for each forward edge (even indices)
    for i in range(m):
        a, b = map(int, lines[1 + i].split())
        edge_info.append((a, b))
        add_edge(a, b, 1)

    source, sink = 1, n

    def bfs():
        level = [-1] * (n + 1)
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            e = head[u]
            while e != -1:
                v = to[e]
                if level[v] == -1 and cap[e] > 0:
                    level[v] = level[u] + 1
                    queue.append(v)
                e = nxt[e]
        return level[sink] != -1, level

    def blocking_flow(level, iter_):
        pushed_total = 0
        while True:
            path = []
            path_edges_list = []
            cur = source

            while True:
                if cur == sink:
                    bottleneck = float('inf')
                    for e_idx in path_edges_list:
                        bottleneck = min(bottleneck, cap[e_idx])
                    for e_idx in path_edges_list:
                        cap[e_idx] -= bottleneck
                        cap[e_idx ^ 1] += bottleneck
                    pushed_total += bottleneck
                    retreat_to = 0
                    for pi, e_idx in enumerate(path_edges_list):
                        if cap[e_idx] == 0:
                            retreat_to = pi
                            break
                    path = path[:retreat_to]
                    path_edges_list = path_edges_list[:retreat_to]
                    cur = source if not path else to[path_edges_list[-1]]
                    continue

                advanced = False
                while iter_[cur] != -1:
                    e = iter_[cur]
                    v = to[e]
                    if level[v] == level[cur] + 1 and cap[e] > 0:
                        path.append(cur)
                        path_edges_list.append(e)
                        cur = v
                        advanced = True
                        break
                    iter_[cur] = nxt[e]
                if not advanced:
                    if cur == source:
                        break
                    level[cur] = -1
                    if path:
                        cur = path.pop()
                        path_edges_list.pop()
                    else:
                        break
            return pushed_total

    max_flow = 0
    while True:
        found, level = bfs()
        if not found:
            break
        iter_ = head[:]
        max_flow += blocking_flow(level, iter_)

    # Trace paths: for each forward edge (even index), if cap==0, it's used
    # Build adjacency from used edges
    used_adj = defaultdict(list)
    for i in range(0, edge_cnt, 2):
        if cap[i] == 0:  # forward edge was used
            u, v = to[i ^ 1], to[i]  # to[i^1] = source of forward edge
            used_adj[u].append(v)

    paths = []
    for _ in range(max_flow):
        path = [source]
        cur = source
        while cur != sink:
            v = used_adj[cur].pop()
            path.append(v)
            cur = v
        paths.append(path)

    result = [str(max_flow)]
    for path in paths:
        result.append(str(len(path)))
        result.append(' '.join(map(str, path)))
    return '\n'.join(result)


# ---------------------------------------------------------------------------
# Solution dispatch table
# ---------------------------------------------------------------------------
SOLUTIONS = {
    1192: solve_1192,
    1193: solve_1193,
    1666: solve_1666,
    1667: solve_1667,
    1668: solve_1668,
    1669: solve_1669,
    1194: solve_1194,
    1671: solve_1671,
    1672: solve_1672,
    1673: solve_1673,
    1195: solve_1195,
    1197: solve_1197,
    1196: solve_1196,
    1678: solve_1678,
    1679: solve_1679,
    1680: solve_1680,
    1681: solve_1681,
    1202: solve_1202,
    1750: solve_1750,
    1160: solve_1160,
    1751: solve_1751,
    1675: solve_1675,
    1676: solve_1676,
    1682: solve_1682,
    1683: solve_1683,
    1684: solve_1684,
    1686: solve_1686,
    1691: solve_1691,
    1692: solve_1692,
    1693: solve_1693,
    1690: solve_1690,
    1689: solve_1689,
    1694: solve_1694,
    1695: solve_1695,
    1696: solve_1696,
    1711: solve_1711,
}


def solve(task_id: int, input_data: str) -> str | None:
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)
