"""Input generators for CSES problems.

Each generator function is named gen_TASKID(size="medium") where size is one of:
  "minimum" - n=1-2, smallest valid inputs
  "small"   - n=3-15, for quick debugging
  "medium"  - n=50-500, correctness check
  "edge"    - boundary cases (all same, sorted, reverse-sorted, max values)

All generators return a valid input string for the corresponding CSES problem.
Input sizes are kept moderate (max ~500-1000 for arrays, ~100 for grids).
"""

import random
import string


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _sz(size, minimum=1, small=10, medium=200, edge=500):
    """Map size category to a concrete value."""
    if size == "minimum":
        return random.randint(1, minimum)
    if size == "small":
        return random.randint(minimum + 1, small)
    if size == "medium":
        return random.randint(small + 1, medium)
    return random.randint(medium + 1, edge)  # edge


def _random_array(n, lo=1, hi=10**9):
    return [random.randint(lo, hi) for _ in range(n)]


def _random_permutation(n):
    p = list(range(1, n + 1))
    random.shuffle(p)
    return p


def _random_string(n, alphabet="abcdefghijklmnopqrstuvwxyz"):
    return "".join(random.choice(alphabet) for _ in range(n))


def _edge_case_array(n, lo=1, hi=10**9):
    """Generate edge-case arrays: all same, sorted, reverse-sorted, or max values."""
    choice = random.choice(["all_same", "sorted", "reverse", "max_vals"])
    if choice == "all_same":
        return [random.randint(lo, hi)] * n
    if choice == "sorted":
        return sorted(_random_array(n, lo, hi))
    if choice == "reverse":
        return sorted(_random_array(n, lo, hi), reverse=True)
    return [hi] * n


def _random_tree(n, weighted=False, weight_range=(1, 10**9)):
    """Generate a random tree with n nodes (1-indexed). Returns edge list."""
    edges = []
    for i in range(2, n + 1):
        p = random.randint(1, i - 1)
        if weighted:
            w = random.randint(*weight_range)
            edges.append((p, i, w))
        else:
            edges.append((p, i))
    random.shuffle(edges)
    return edges


def _tree_parent_array(n):
    """Return list of parents for nodes 2..n (node 1 is root)."""
    return [random.randint(1, i - 1) for i in range(2, n + 1)]


def _random_graph(n, m, directed=False, weighted=False, weight_range=(1, 10**9)):
    """Generate random graph. No self-loops, no duplicate edges."""
    edges = set()
    attempts = 0
    while len(edges) < m and attempts < m * 20:
        u, v = random.randint(1, n), random.randint(1, n)
        if u == v:
            attempts += 1
            continue
        key = (u, v) if directed else (min(u, v), max(u, v))
        edges.add(key)
        attempts += 1
    result = []
    for e in edges:
        if weighted:
            result.append((*e, random.randint(*weight_range)))
        else:
            result.append(e)
    random.shuffle(result)
    return result


def _random_connected_graph(n, m, directed=False, weighted=False,
                            weight_range=(1, 10**9)):
    """Connected graph: spanning tree + random extra edges."""
    m = max(m, n - 1)
    tree = set()
    for i in range(2, n + 1):
        u, v = random.randint(1, i - 1), i
        key = (u, v) if directed else (min(u, v), max(u, v))
        tree.add(key)
    edges = set(tree)
    attempts = 0
    while len(edges) < m and attempts < m * 20:
        u, v = random.randint(1, n), random.randint(1, n)
        if u == v:
            attempts += 1
            continue
        key = (u, v) if directed else (min(u, v), max(u, v))
        edges.add(key)
        attempts += 1
    result = []
    for e in edges:
        if weighted:
            result.append((*e, random.randint(*weight_range)))
        else:
            result.append(e)
    random.shuffle(result)
    return result


def _random_dag(n, m):
    """Random DAG: edges go from smaller to larger node index."""
    edges = set()
    attempts = 0
    while len(edges) < m and attempts < m * 20:
        u = random.randint(1, n - 1)
        v = random.randint(u + 1, n)
        edges.add((u, v))
        attempts += 1
    result = list(edges)
    random.shuffle(result)
    return result


def _random_dag_weighted(n, m, weight_range=(1, 10**9)):
    """Random weighted DAG."""
    raw = _random_dag(n, m)
    return [(u, v, random.randint(*weight_range)) for u, v in raw]


def _random_grid(n, m, wall_prob=0.3):
    """Generate n×m grid of '.' and '#'."""
    rows = []
    for _ in range(n):
        rows.append("".join("#" if random.random() < wall_prob else "."
                            for _ in range(m)))
    return rows


def _place_char(grid, char):
    """Place char at a random '.' cell. Modifies grid in-place, returns success."""
    free = [(r, c) for r in range(len(grid)) for c in range(len(grid[0]))
            if grid[r][c] == "."]
    if not free:
        return False
    r, c = random.choice(free)
    grid[r] = grid[r][:c] + char + grid[r][c + 1:]
    return True


def _eulerian_undirected(n, target_m=None):
    """Connected undirected graph where all vertices have even degree."""
    if target_m is None:
        target_m = max(n, 2 * n)
    perm = list(range(1, n + 1))
    random.shuffle(perm)
    edges = []
    # Hamiltonian cycle ensures connectivity + all degree 2
    for i in range(n):
        edges.append((perm[i], perm[(i + 1) % n]))
    # Add small cycles (each cycle preserves even degree)
    while len(edges) < target_m and n >= 3:
        k = random.randint(3, min(n, 6))
        cycle = random.sample(range(1, n + 1), k)
        for i in range(k):
            edges.append((cycle[i], cycle[(i + 1) % k]))
    return edges


def _directed_eulerian_path(n, target_m=None):
    """Directed graph with Eulerian path from 1 to n."""
    if target_m is None:
        target_m = max(n, 2 * n)
    edges = []
    # Path 1→2→...→n
    for i in range(1, n):
        edges.append((i, i + 1))
    # Add directed cycles (preserves in/out balance at every node)
    while len(edges) < target_m and n >= 2:
        k = random.randint(2, min(n, 5))
        cycle = random.sample(range(1, n + 1), k)
        for i in range(k):
            edges.append((cycle[i], cycle[(i + 1) % k]))
    return edges


def _fmt(edges):
    """Format edge list as newline-separated strings."""
    return "\n".join(" ".join(str(x) for x in e) for e in edges)


def _arr(a):
    """Format list as space-separated string."""
    return " ".join(map(str, a))


# ═══════════════════════════════════════════════════════════════════════════════
# INTRODUCTORY PROBLEMS
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1068(size="medium"):
    """Weird Algorithm: just n."""
    n = _sz(size, 2, 100, 10000, 100000)
    return str(n)


def gen_1083(size="medium"):
    """Missing Number: permutation of 1..n with one removed."""
    n = _sz(size, 2, 15, 200, 500)
    missing = random.randint(1, n)
    nums = [x for x in range(1, n + 1) if x != missing]
    random.shuffle(nums)
    return f"{n}\n{_arr(nums)}"


def gen_1069(size="medium"):
    """Repetitions: DNA string."""
    n = _sz(size, 1, 15, 200, 500)
    s = _random_string(n, "ACGT")
    if size == "edge":
        # Edge: long run of same char
        c = random.choice("ACGT")
        run = c * (n // 2)
        rest = _random_string(n - len(run), "ACGT")
        s = run + rest
    return s


def gen_1094(size="medium"):
    """Increasing Array: n integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _edge_case_array(n) if size == "edge" else _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1070(size="medium"):
    """Permutations: just n."""
    n = _sz(size, 1, 15, 200, 1000)
    return str(n)


def gen_1071(size="medium"):
    """Number Spiral: t queries of (y, x)."""
    t = _sz(size, 1, 10, 50, 100)
    lines = [str(t)]
    for _ in range(t):
        y = random.randint(1, 10**9)
        x = random.randint(1, 10**9)
        lines.append(f"{y} {x}")
    return "\n".join(lines)


def gen_1072(size="medium"):
    """Two Knights: just n."""
    n = _sz(size, 1, 15, 200, 1000)
    return str(n)


def gen_1092(size="medium"):
    """Two Sets: just n."""
    n = _sz(size, 1, 15, 200, 500)
    return str(n)


def gen_1617(size="medium"):
    """Bit Strings: just n."""
    n = _sz(size, 1, 100, 10000, 1000000)
    return str(n)


def gen_1618(size="medium"):
    """Trailing Zeros: just n."""
    n = _sz(size, 1, 100, 10000, 1000000)
    return str(n)


def gen_1754(size="medium"):
    """Coin Piles: t test cases of (a, b)."""
    t = _sz(size, 1, 10, 50, 100)
    lines = [str(t)]
    for _ in range(t):
        a = random.randint(0, 10**9)
        b = random.randint(0, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1755(size="medium"):
    """Palindrome Reorder: string of lowercase letters."""
    n = _sz(size, 1, 15, 200, 500)
    if size == "edge":
        # Guarantee palindrome is possible: at most 1 odd-frequency char
        chars = []
        for _ in range(n // 2):
            c = random.choice(string.ascii_lowercase)
            chars.extend([c, c])
        if n % 2:
            chars.append(random.choice(string.ascii_lowercase))
        random.shuffle(chars)
        return "".join(chars)
    return _random_string(n)


def gen_2205(size="medium"):
    """Gray Code: just n (keep small, output is 2^n lines)."""
    n = _sz(size, 1, 4, 10, 16)
    return str(n)


def gen_2165(size="medium"):
    """Tower of Hanoi: just n (output is 2^n - 1 moves)."""
    n = _sz(size, 1, 4, 10, 16)
    return str(n)


def gen_1622(size="medium"):
    """Creating Strings: short string (output is all permutations)."""
    n = _sz(size, 1, 3, 6, 8)
    return _random_string(n)


def gen_1623(size="medium"):
    """Apple Division: n weights, n ≤ 20."""
    n = _sz(size, 1, 5, 15, 20)
    arr = _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1624(size="medium"):
    """Chessboard and Queens: 8×8 grid with some '*'."""
    grid = []
    block_prob = 0.1 if size != "edge" else 0.3
    for _ in range(8):
        row = "".join("*" if random.random() < block_prob else "." for _ in range(8))
        grid.append(row)
    return "\n".join(grid)


def gen_2431(size="medium"):
    """Digit Queries: q queries for positions in 123456789101112..."""
    q = _sz(size, 1, 10, 50, 100)
    lines = [str(q)]
    for _ in range(q):
        k = random.randint(1, 10**18)
        lines.append(str(k))
    return "\n".join(lines)


def gen_1743(size="medium"):
    """String Reorder: string that can be reordered to avoid adjacent duplicates."""
    n = _sz(size, 1, 15, 200, 500)
    # No single char appears more than ceil(n/2) times
    max_freq = (n + 1) // 2
    chars = []
    remaining = n
    used = []
    for c in string.ascii_lowercase:
        if remaining <= 0:
            break
        cnt = random.randint(1, min(max_freq, remaining))
        chars.extend([c] * cnt)
        remaining -= cnt
    while len(chars) < n:
        chars.append(random.choice(string.ascii_lowercase))
    chars = chars[:n]
    random.shuffle(chars)
    return "".join(chars)


def gen_1625(size="medium"):
    """Grid Paths: 48-char string of UDLR?."""
    dirs = "UDLR"
    if size == "minimum":
        # Mostly fixed directions to keep solver fast
        fixed_count = 40
    elif size == "edge":
        fixed_count = 30
    else:
        fixed_count = {"small": 35, "medium": 20}.get(size, 25)
    path = list("?" * 48)
    positions = random.sample(range(48), min(fixed_count, 48))
    for p in positions:
        path[p] = random.choice(dirs)
    return "".join(path)


# ═══════════════════════════════════════════════════════════════════════════════
# SORTING AND SEARCHING
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1621(size="medium"):
    """Distinct Numbers: n integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1084(size="medium"):
    """Apartments: n applicants, m apartments, tolerance k."""
    n = _sz(size, 1, 15, 200, 500)
    m = _sz(size, 1, 15, 200, 500)
    k = random.randint(0, 10**5)
    desired = _random_array(n, 1, 10**9)
    apts = _random_array(m, 1, 10**9)
    return f"{n} {m} {k}\n{_arr(desired)}\n{_arr(apts)}"


def gen_1090(size="medium"):
    """Ferris Wheel: n children with weights, max weight x."""
    n = _sz(size, 1, 15, 200, 500)
    x = random.randint(2, 10**9)
    weights = _random_array(n, 1, x)
    return f"{n} {x}\n{_arr(weights)}"


def gen_1091(size="medium"):
    """Concert Tickets: n tickets, m customers."""
    n = _sz(size, 1, 15, 200, 500)
    m = _sz(size, 1, 15, 200, 500)
    prices = _random_array(n, 1, 10**9)
    max_prices = _random_array(m, 1, 10**9)
    return f"{n} {m}\n{_arr(prices)}\n{_arr(max_prices)}"


def gen_1619(size="medium"):
    """Restaurant Customers: n customers with (arrive, leave)."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a + 1, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1629(size="medium"):
    """Movie Festival: n movies with (start, end)."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a + 1, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1640(size="medium"):
    """Sum of Two Values: n values, target x."""
    n = _sz(size, 2, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    if random.random() < 0.5 and n >= 2:
        # Ensure a solution exists
        i, j = random.sample(range(n), 2)
        x = arr[i] + arr[j]
    else:
        x = random.randint(2, 2 * 10**9)
    return f"{n} {x}\n{_arr(arr)}"


def gen_1643(size="medium"):
    """Maximum Subarray Sum: n integers (can be negative)."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, -(10**9), 10**9)
    if size == "edge":
        arr = _edge_case_array(n, -(10**9), 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1074(size="medium"):
    """Stick Lengths: n positive integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _edge_case_array(n) if size == "edge" else _random_array(n)
    return f"{n}\n{_arr(arr)}"


def gen_2183(size="medium"):
    """Missing Coin Sum: n positive integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    if size == "edge":
        # Powers of 2 or all 1s
        choice = random.choice(["powers", "ones"])
        if choice == "powers":
            arr = [2**i for i in range(min(n, 30))]
            arr.extend([1] * (n - len(arr)))
        else:
            arr = [1] * n
    return f"{n}\n{_arr(arr)}"


def gen_2216(size="medium"):
    """Collecting Numbers: permutation of 1..n."""
    n = _sz(size, 1, 15, 200, 500)
    perm = _random_permutation(n)
    return f"{n}\n{_arr(perm)}"


def gen_2217(size="medium"):
    """Collecting Numbers II: permutation + m swap queries."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = _sz(size, 1, 15, 200, 500)
    perm = _random_permutation(n)
    lines = [f"{n} {m}", _arr(perm)]
    for _ in range(m):
        a = random.randint(1, n)
        b = random.randint(1, n)
        while b == a:
            b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1141(size="medium"):
    """Playlist: n song IDs."""
    n = _sz(size, 1, 15, 200, 500)
    k = max(1, n // 2)  # range of song IDs
    arr = [random.randint(1, k) for _ in range(n)]
    return f"{n}\n{_arr(arr)}"


def gen_1073(size="medium"):
    """Towers: n cube sizes."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _edge_case_array(n, 1, 10**9) if size == "edge" else _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1163(size="medium"):
    """Traffic Lights: street length x, n positions."""
    n = _sz(size, 1, 15, 200, 500)
    x = random.randint(n + 2, max(n + 3, 10**9))
    positions = random.sample(range(1, x), n)
    return f"{x} {n}\n{_arr(positions)}"


def gen_3420(size="medium"):
    """Distinct Values Subarrays: n values."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, max(1, n // 2))
    return f"{n}\n{_arr(arr)}"


def gen_3421(size="medium"):
    """Distinct Values Subsequences: n values."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, max(1, n // 2))
    return f"{n}\n{_arr(arr)}"


def gen_2162(size="medium"):
    """Josephus Problem I: just n."""
    n = _sz(size, 1, 15, 200, 500)
    return str(n)


def gen_2163(size="medium"):
    """Josephus Problem II: n and k."""
    n = _sz(size, 1, 15, 200, 500)
    k = random.randint(1, n)
    return f"{n} {k}"


def gen_2168(size="medium"):
    """Nested Ranges Check: n ranges."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a + 1, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_2169(size="medium"):
    """Nested Ranges Count: n ranges."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a + 1, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1164(size="medium"):
    """Room Allocation: n customers with (arrive, leave)."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1620(size="medium"):
    """Factory Machines: n machines, target t products."""
    n = _sz(size, 1, 15, 200, 500)
    t = random.randint(1, 10**9)
    times = _random_array(n, 1, 10**9)
    return f"{n} {t}\n{_arr(times)}"


def gen_1630(size="medium"):
    """Tasks and Deadlines: n tasks with (duration, deadline)."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        d = random.randint(1, 10**6)
        dl = random.randint(d, 2 * 10**6)
        lines.append(f"{d} {dl}")
    return "\n".join(lines)


def gen_1631(size="medium"):
    """Reading Books: n book reading times."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1641(size="medium"):
    """Sum of Three Values: n values, target x."""
    n = _sz(size, 3, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    if random.random() < 0.5 and n >= 3:
        i, j, k = random.sample(range(n), 3)
        x = arr[i] + arr[j] + arr[k]
    else:
        x = random.randint(3, 3 * 10**9)
    return f"{n} {x}\n{_arr(arr)}"


def gen_1642(size="medium"):
    """Sum of Four Values: n values, target x."""
    n = _sz(size, 4, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    if random.random() < 0.5 and n >= 4:
        idx = random.sample(range(n), 4)
        x = sum(arr[i] for i in idx)
    else:
        x = random.randint(4, 4 * 10**9)
    return f"{n} {x}\n{_arr(arr)}"


def gen_1645(size="medium"):
    """Nearest Smaller Values: n positive integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _edge_case_array(n) if size == "edge" else _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1660(size="medium"):
    """Subarray Sums I: n positive integers, target x."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**6)
    x = random.randint(1, sum(arr))
    return f"{n} {x}\n{_arr(arr)}"


def gen_1661(size="medium"):
    """Subarray Sums II: n integers (can be negative), target x."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, -(10**6), 10**6)
    x = random.randint(-(10**7), 10**7)
    return f"{n} {x}\n{_arr(arr)}"


def gen_1662(size="medium"):
    """Subarray Divisibility: n integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, -(10**9), 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_2428(size="medium"):
    """Distinct Values Subarrays II: n integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, max(1, n // 2))
    return f"{n}\n{_arr(arr)}"


def gen_1085(size="medium"):
    """Array Division: n integers, k parts."""
    n = _sz(size, 1, 15, 200, 500)
    k = random.randint(1, n)
    arr = _random_array(n, 1, 10**9)
    return f"{n} {k}\n{_arr(arr)}"


def gen_1632(size="medium"):
    """Movie Festival II: n movies, k members."""
    n = _sz(size, 1, 15, 200, 500)
    k = random.randint(1, max(1, n // 5))
    lines = [f"{n} {k}"]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a + 1, 10**9)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1644(size="medium"):
    """Maximum Subarray Sum II: n integers, min length a, max length b."""
    n = _sz(size, 1, 15, 200, 500)
    a = random.randint(1, n)
    b = random.randint(a, n)
    arr = _random_array(n, -(10**9), 10**9)
    return f"{n} {a} {b}\n{_arr(arr)}"


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC PROGRAMMING
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1633(size="medium"):
    """Dice Combinations: just n."""
    n = _sz(size, 1, 100, 10000, 1000000)
    return str(n)


def gen_1634(size="medium"):
    """Minimizing Coins: n coin values, target sum x."""
    n = _sz(size, 1, 10, 50, 100)
    x = _sz(size, 1, 100, 10000, 100000)
    coins = sorted(set(_random_array(n, 1, min(x, 10**6))))
    n = len(coins)
    return f"{n} {x}\n{_arr(coins)}"


def gen_1635(size="medium"):
    """Coin Combinations I: same format as Minimizing Coins."""
    return gen_1634(size)


def gen_1636(size="medium"):
    """Coin Combinations II: same format as Minimizing Coins."""
    return gen_1634(size)


def gen_1637(size="medium"):
    """Removing Digits: just n."""
    n = _sz(size, 1, 100, 10000, 1000000)
    return str(n)


def gen_1638(size="medium"):
    """Grid Paths I: n×n grid with '.' and '*'. Top-left and bottom-right clear."""
    n = _sz(size, 1, 5, 50, 100)
    grid = _random_grid(n, n, wall_prob=0.2)
    # Ensure start and end are open
    grid[0] = "." + grid[0][1:]
    grid[-1] = grid[-1][:-1] + "."
    return f"{n}\n" + "\n".join(grid)


def gen_1158(size="medium"):
    """Book Shop: n books with (price, pages), budget x."""
    n = _sz(size, 1, 15, 200, 500)
    x = random.randint(n, 10**5)
    prices = _random_array(n, 1, x)
    pages = _random_array(n, 1, 10**9)
    return f"{n} {x}\n{_arr(prices)}\n{_arr(pages)}"


def gen_1746(size="medium"):
    """Array Description: n values (some 0), max value m."""
    n = _sz(size, 1, 15, 200, 500)
    m = random.randint(1, 100)
    arr = []
    for _ in range(n):
        if random.random() < 0.3:
            arr.append(0)  # unknown
        else:
            arr.append(random.randint(1, m))
    return f"{n} {m}\n{_arr(arr)}"


def gen_2413(size="medium"):
    """Counting Towers: t test cases of n."""
    t = _sz(size, 1, 10, 50, 100)
    lines = [str(t)]
    for _ in range(t):
        n = random.randint(1, 10**6)
        lines.append(str(n))
    return "\n".join(lines)


def gen_1639(size="medium"):
    """Edit Distance: two strings."""
    n1 = _sz(size, 1, 10, 200, 500)
    n2 = _sz(size, 1, 10, 200, 500)
    return f"{_random_string(n1)}\n{_random_string(n2)}"


def gen_3403(size="medium"):
    """Longest Common Subsequence: two strings."""
    n1 = _sz(size, 1, 10, 200, 500)
    n2 = _sz(size, 1, 10, 200, 500)
    return f"{_random_string(n1)}\n{_random_string(n2)}"


def gen_1744(size="medium"):
    """Rectangle Cutting: a × b dimensions."""
    a = _sz(size, 1, 10, 200, 500)
    b = _sz(size, 1, 10, 200, 500)
    return f"{a} {b}"


def gen_1745(size="medium"):
    """Money Sums: n coin values."""
    n = _sz(size, 1, 15, 100, 200)
    coins = _random_array(n, 1, 1000)
    return f"{n}\n{_arr(coins)}"


def gen_1097(size="medium"):
    """Removal Game: n values in a row."""
    n = _sz(size, 1, 15, 200, 500)
    if n % 2 != 0:
        n += 1  # n must be even
    arr = _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1093(size="medium"):
    """Two Sets II: just n."""
    n = _sz(size, 1, 15, 200, 500)
    return str(n)


def gen_1145(size="medium"):
    """Increasing Subsequence: n integers."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _edge_case_array(n) if size == "edge" else _random_array(n, 1, 10**9)
    return f"{n}\n{_arr(arr)}"


def gen_1140(size="medium"):
    """Projects: n projects with (start, end, reward)."""
    n = _sz(size, 1, 15, 200, 500)
    lines = [str(n)]
    for _ in range(n):
        a = random.randint(1, 10**9 - 1)
        b = random.randint(a, 10**9)
        r = random.randint(1, 10**9)
        lines.append(f"{a} {b} {r}")
    return "\n".join(lines)


def gen_1653(size="medium"):
    """Elevator Rides: n people with weights, capacity x. n ≤ 20."""
    n = _sz(size, 1, 5, 15, 20)
    x = random.randint(1, 10**9)
    weights = _random_array(n, 1, x)
    return f"{n} {x}\n{_arr(weights)}"


def gen_2181(size="medium"):
    """Counting Tilings: n × m grid (both ≤ 10)."""
    n = _sz(size, 1, 3, 7, 10)
    m = _sz(size, 1, 3, 7, 10)
    return f"{n} {m}"


def gen_2220(size="medium"):
    """Counting Numbers: a and b."""
    a = random.randint(1, 10**18 // 2)
    b = random.randint(a, 10**18)
    if size == "minimum":
        a, b = 1, random.randint(1, 10)
    elif size == "small":
        a = random.randint(1, 100)
        b = random.randint(a, 1000)
    return f"{a} {b}"


def gen_1748(size="medium"):
    """Increasing Subsequence II: n integers in range 1..k."""
    n = _sz(size, 1, 15, 200, 500)
    k = random.randint(1, max(1, n))
    arr = _random_array(n, 1, k)
    return f"{n} {k}\n{_arr(arr)}"


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH ALGORITHMS
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1192(size="medium"):
    """Counting Rooms: n×m grid of '.' and '#'."""
    n = _sz(size, 1, 10, 50, 100)
    m = _sz(size, 1, 10, 50, 100)
    grid = _random_grid(n, m)
    return f"{n} {m}\n" + "\n".join(grid)


def gen_1193(size="medium"):
    """Labyrinth: n×m grid with 'A' (start) and 'B' (end)."""
    n = _sz(size, 2, 10, 50, 100)
    m = _sz(size, 2, 10, 50, 100)
    grid = _random_grid(n, m, wall_prob=0.25)
    _place_char(grid, "A")
    _place_char(grid, "B")
    return f"{n} {m}\n" + "\n".join(grid)


def gen_1666(size="medium"):
    """Building Roads: n nodes, m edges."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(0, min(n * (n - 1) // 2, 3 * n))
    edges = _random_graph(n, m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1667(size="medium"):
    """Message Route: n nodes, m edges (undirected)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    edges = _random_connected_graph(n, m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1668(size="medium"):
    """Building Teams: n nodes, m edges (bipartite sometimes)."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(1, min(n * (n - 1) // 2, 3 * n))
    if random.random() < 0.6:
        # Bipartite graph
        split = max(1, n // 2)
        edges = set()
        attempts = 0
        while len(edges) < m and attempts < m * 20:
            u = random.randint(1, split)
            v = random.randint(split + 1, n)
            edges.add((min(u, v), max(u, v)))
            attempts += 1
        edges = list(edges)
    else:
        edges = _random_graph(n, m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1669(size="medium"):
    """Round Trip: n nodes, m undirected edges (with cycles)."""
    n = _sz(size, 3, 15, 200, 500)
    n = max(3, n)
    m = random.randint(n, min(n * (n - 1) // 2, 3 * n))
    edges = _random_connected_graph(n, m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1194(size="medium"):
    """Monsters: n×m grid with '.', '#', 'A', and 'M'."""
    n = _sz(size, 2, 10, 50, 100)
    m = _sz(size, 2, 10, 50, 100)
    grid = _random_grid(n, m, wall_prob=0.2)
    _place_char(grid, "A")
    num_monsters = random.randint(1, max(1, min(n * m // 10, 20)))
    for _ in range(num_monsters):
        _place_char(grid, "M")
    return f"{n} {m}\n" + "\n".join(grid)


def gen_1671(size="medium"):
    """Shortest Routes I: n nodes, m directed weighted edges (Dijkstra)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(1, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1672(size="medium"):
    """Shortest Routes II: n nodes, m edges, q queries (Floyd-Warshall)."""
    n = _sz(size, 2, 10, 100, 500)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    q = _sz(size, 1, 10, 50, 100)
    edges = _random_connected_graph(n, m, weighted=True, weight_range=(1, 10**6))
    m = len(edges)
    lines = [f"{n} {m} {q}", _fmt(edges)]
    for _ in range(q):
        a = random.randint(1, n)
        b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1673(size="medium"):
    """High Score: n nodes, m directed weighted edges (can be negative)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(-10**9, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1195(size="medium"):
    """Flight Discount: n nodes, m directed weighted edges."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(1, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1197(size="medium"):
    """Cycle Finding: n nodes, m directed weighted edges."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(n, min(n * (n - 1), 3 * n))
    edges = _random_graph(n, m, directed=True, weighted=True,
                          weight_range=(-10**9, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1196(size="medium"):
    """Flight Routes: n nodes, m directed weighted edges, k shortest paths."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    k = random.randint(1, min(10, n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(1, 10**9))
    m = len(edges)
    return f"{n} {m} {k}\n{_fmt(edges)}"


def gen_1678(size="medium"):
    """Round Trip II: n nodes, m directed edges."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(n, min(n * (n - 1), 3 * n))
    edges = _random_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1679(size="medium"):
    """Course Schedule: n nodes, m directed edges (DAG sometimes)."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(1, min(n * (n - 1) // 2, 3 * n))
    if random.random() < 0.7:
        edges = _random_dag(n, m)
    else:
        edges = _random_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1680(size="medium"):
    """Longest Flight Route: n nodes, m directed edges (DAG from 1 to n)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    edges = _random_dag(n, m)
    # Ensure edge from 1 and edge to n exist
    has_from_1 = any(u == 1 for u, v in edges)
    has_to_n = any(v == n for u, v in edges)
    if not has_from_1 and n > 1:
        edges.append((1, random.randint(2, n)))
    if not has_to_n and n > 1:
        edges.append((random.randint(1, n - 1), n))
    edges = list(set(edges))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1681(size="medium"):
    """Game Routes: n nodes, m directed edges (DAG)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    edges = _random_dag(n, m)
    # Ensure reachability from 1 to n
    has_from_1 = any(u == 1 for u, v in edges)
    has_to_n = any(v == n for u, v in edges)
    if not has_from_1 and n > 1:
        edges.append((1, random.randint(2, n)))
    if not has_to_n and n > 1:
        edges.append((random.randint(1, n - 1), n))
    edges = list(set(edges))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1202(size="medium"):
    """Investigation: n nodes, m directed weighted edges (Dijkstra variants)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(1, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1750(size="medium"):
    """Planets Queries I: functional graph, q queries (x, k)."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 10, 50, 100)
    successors = [random.randint(1, n) for _ in range(n)]
    lines = [f"{n} {q}", _arr(successors)]
    for _ in range(q):
        x = random.randint(1, n)
        k = random.randint(0, 10**9)
        lines.append(f"{x} {k}")
    return "\n".join(lines)


def gen_1160(size="medium"):
    """Planets Queries II: functional graph, q queries (a, b)."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 10, 50, 100)
    successors = [random.randint(1, n) for _ in range(n)]
    lines = [f"{n} {q}", _arr(successors)]
    for _ in range(q):
        a = random.randint(1, n)
        b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1751(size="medium"):
    """Planets Cycles: functional graph."""
    n = _sz(size, 2, 15, 200, 500)
    successors = [random.randint(1, n) for _ in range(n)]
    return f"{n}\n{_arr(successors)}"


def gen_1675(size="medium"):
    """Road Reparation: n nodes, m weighted undirected edges (MST)."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    edges = _random_connected_graph(n, m, weighted=True, weight_range=(1, 10**9))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1676(size="medium"):
    """Road Construction: n nodes, m edges added one by one."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = _sz(size, 1, 15, 200, 500)
    lines = [f"{n} {m}"]
    for _ in range(m):
        u = random.randint(1, n)
        v = random.randint(1, n)
        while v == u:
            v = random.randint(1, n)
        lines.append(f"{u} {v}")
    return "\n".join(lines)


def gen_1682(size="medium"):
    """Flight Routes Check: n nodes, m directed edges."""
    n = _sz(size, 2, 15, 200, 500)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1683(size="medium"):
    """Planets and Kingdoms (SCC): n nodes, m directed edges."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(n, min(n * (n - 1), 3 * n))
    edges = _random_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1684(size="medium"):
    """Giant Pizza (2-SAT): m toppings, n wishes (2-SAT clauses)."""
    m_toppings = _sz(size, 1, 10, 100, 500)
    n_clauses = _sz(size, 1, 15, 200, 500)
    lines = [f"{n_clauses} {m_toppings}"]
    for _ in range(n_clauses):
        sign1 = random.choice(["+", "-"])
        var1 = random.randint(1, m_toppings)
        sign2 = random.choice(["+", "-"])
        var2 = random.randint(1, m_toppings)
        lines.append(f"{sign1} {var1} {sign2} {var2}")
    return "\n".join(lines)


def gen_1686(size="medium"):
    """Coin Collector: n nodes with coins, m directed edges."""
    n = _sz(size, 2, 15, 200, 500)
    n = max(2, n)
    m = random.randint(n, min(n * (n - 1), 3 * n))
    coins = _random_array(n, 1, 10**9)
    edges = _random_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_arr(coins)}\n{_fmt(edges)}"


def gen_1691(size="medium"):
    """Mail Delivery: undirected Eulerian circuit."""
    n = _sz(size, 2, 10, 50, 100)
    target_m = _sz(size, 3, 15, 100, 200)
    edges = _eulerian_undirected(n, target_m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1692(size="medium"):
    """De Bruijn Sequence: just n."""
    n = _sz(size, 1, 5, 10, 15)
    return str(n)


def gen_1693(size="medium"):
    """Teleporters Path: directed Eulerian path from 1 to n."""
    n = _sz(size, 2, 10, 50, 100)
    target_m = _sz(size, 3, 15, 100, 200)
    edges = _directed_eulerian_path(n, target_m)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1690(size="medium"):
    """Hamiltonian Flights: n nodes (≤20), m directed edges."""
    n = _sz(size, 2, 5, 12, 20)
    n = max(2, n)
    max_m = n * (n - 1)
    m = random.randint(n, min(max_m, 4 * n))
    edges = _random_graph(n, m, directed=True)
    # Ensure at least one edge from 1 and one edge to n
    has_from_1 = any(u == 1 for u, v in edges)
    has_to_n = any(v == n for u, v in edges)
    if not has_from_1 and n > 1:
        edges.append((1, random.randint(2, n)))
    if not has_to_n and n > 1:
        edges.append((random.randint(1, n - 1), n))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1689(size="medium"):
    """Knight's Tour: n (board size) and starting position (x, y)."""
    n = 8
    x = random.randint(1, n)
    y = random.randint(1, n)
    return f"{n} {x} {y}"


def gen_1694(size="medium"):
    """Download Speed (Max Flow): n nodes, m directed weighted edges."""
    n = _sz(size, 2, 10, 50, 100)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True, weighted=True,
                                    weight_range=(1, 10**6))
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1695(size="medium"):
    """Police Chase (Min Cut): n nodes, m undirected edges."""
    n = _sz(size, 2, 10, 50, 100)
    m = random.randint(n - 1, min(n * (n - 1) // 2, 3 * n))
    edges = _random_connected_graph(n, m, weighted=False)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


def gen_1696(size="medium"):
    """School Dance (Bipartite Matching): n boys, m girls, k pairs."""
    n = _sz(size, 1, 10, 100, 200)
    m = _sz(size, 1, 10, 100, 200)
    k = random.randint(1, min(n * m, 3 * max(n, m)))
    pairs = set()
    attempts = 0
    while len(pairs) < k and attempts < k * 20:
        a = random.randint(1, n)
        b = random.randint(1, m)
        pairs.add((a, b))
        attempts += 1
    k = len(pairs)
    lines = [f"{n} {m} {k}"]
    for a, b in pairs:
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1711(size="medium"):
    """Distinct Routes: n nodes, m directed edges."""
    n = _sz(size, 2, 10, 50, 100)
    m = random.randint(n - 1, min(n * (n - 1), 3 * n))
    edges = _random_connected_graph(n, m, directed=True)
    m = len(edges)
    return f"{n} {m}\n{_fmt(edges)}"


# ═══════════════════════════════════════════════════════════════════════════════
# RANGE QUERIES
# ═══════════════════════════════════════════════════════════════════════════════


def _range_queries(n, q):
    """Generate q range queries [a, b] with 1 ≤ a ≤ b ≤ n."""
    queries = []
    for _ in range(q):
        a = random.randint(1, n)
        b = random.randint(a, n)
        queries.append(f"{a} {b}")
    return queries


def gen_1646(size="medium"):
    """Static Range Sum Queries: n values, q range queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    queries = _range_queries(n, q)
    return f"{n} {q}\n{_arr(arr)}\n" + "\n".join(queries)


def gen_1647(size="medium"):
    """Static Range Minimum Queries: n values, q range queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    queries = _range_queries(n, q)
    return f"{n} {q}\n{_arr(arr)}\n" + "\n".join(queries)


def gen_1648(size="medium"):
    """Dynamic Range Sum Queries: n values, q queries (update or range sum)."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    lines = [f"{n} {q}", _arr(arr)]
    for _ in range(q):
        if random.random() < 0.5:
            k = random.randint(1, n)
            u = random.randint(1, 10**9)
            lines.append(f"1 {k} {u}")
        else:
            a = random.randint(1, n)
            b = random.randint(a, n)
            lines.append(f"2 {a} {b}")
    return "\n".join(lines)


def gen_1649(size="medium"):
    """Dynamic Range Minimum Queries: n values, q queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    lines = [f"{n} {q}", _arr(arr)]
    for _ in range(q):
        if random.random() < 0.5:
            k = random.randint(1, n)
            u = random.randint(1, 10**9)
            lines.append(f"1 {k} {u}")
        else:
            a = random.randint(1, n)
            b = random.randint(a, n)
            lines.append(f"2 {a} {b}")
    return "\n".join(lines)


def gen_1650(size="medium"):
    """Range Xor Queries: n values, q range queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    queries = _range_queries(n, q)
    return f"{n} {q}\n{_arr(arr)}\n" + "\n".join(queries)


def gen_1651(size="medium"):
    """Range Update Queries: n values, q queries (range add or point query)."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    lines = [f"{n} {q}", _arr(arr)]
    for _ in range(q):
        if random.random() < 0.5:
            a = random.randint(1, n)
            b = random.randint(a, n)
            u = random.randint(1, 10**6)
            lines.append(f"1 {a} {b} {u}")
        else:
            k = random.randint(1, n)
            lines.append(f"2 {k}")
    return "\n".join(lines)


def gen_1652(size="medium"):
    """Forest Queries: n×n grid, q rectangle queries."""
    n = _sz(size, 1, 10, 50, 100)
    q = _sz(size, 1, 10, 50, 100)
    grid = []
    for _ in range(n):
        grid.append("".join(random.choice(".*") for _ in range(n)))
    lines = [f"{n} {q}"] + grid
    for _ in range(q):
        y1 = random.randint(1, n)
        x1 = random.randint(1, n)
        y2 = random.randint(y1, n)
        x2 = random.randint(x1, n)
        lines.append(f"{y1} {x1} {y2} {x2}")
    return "\n".join(lines)


def gen_2166(size="medium"):
    """Range Updates and Sums: n values, q queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**6)
    lines = [f"{n} {q}", _arr(arr)]
    for _ in range(q):
        t = random.randint(1, 3)
        if t <= 2:
            a = random.randint(1, n)
            b = random.randint(a, n)
            x = random.randint(1, 10**6)
            lines.append(f"{t} {a} {b} {x}")
        else:
            a = random.randint(1, n)
            b = random.randint(a, n)
            lines.append(f"3 {a} {b}")
    return "\n".join(lines)


def gen_2206(size="medium"):
    """Pizzeria Queries: n values, q queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**6)
    lines = [f"{n} {q}", _arr(arr)]
    for _ in range(q):
        if random.random() < 0.5:
            k = random.randint(1, n)
            x = random.randint(1, 10**6)
            lines.append(f"1 {k} {x}")
        else:
            k = random.randint(1, n)
            lines.append(f"2 {k}")
    return "\n".join(lines)


def gen_1143(size="medium"):
    """Hotel Queries: n hotels, m groups."""
    n = _sz(size, 1, 15, 200, 500)
    m = _sz(size, 1, 15, 200, 500)
    rooms = _random_array(n, 1, 10**6)
    groups = _random_array(m, 1, 10**6)
    return f"{n} {m}\n{_arr(rooms)}\n{_arr(groups)}"


def gen_1749(size="medium"):
    """List Removals: n values, then n removal positions."""
    n = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, 10**9)
    positions = [random.randint(1, n - i) for i in range(n)]
    return f"{n}\n{_arr(arr)}\n{_arr(positions)}"


def gen_1144(size="medium"):
    """Salary Queries: n salaries, q queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    salaries = _random_array(n, 1, 10**6)
    lines = [f"{n} {q}", _arr(salaries)]
    for _ in range(q):
        if random.random() < 0.4:
            k = random.randint(1, n)
            x = random.randint(1, 10**6)
            lines.append(f"! {k} {x}")
        else:
            a = random.randint(1, 10**6)
            b = random.randint(a, 10**6)
            lines.append(f"? {a} {b}")
    return "\n".join(lines)


def gen_2184(size="medium"):
    """Distinct Values Queries: n values, q range queries."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    arr = _random_array(n, 1, max(1, n // 2))
    queries = _range_queries(n, q)
    return f"{n} {q}\n{_arr(arr)}\n" + "\n".join(queries)


# ═══════════════════════════════════════════════════════════════════════════════
# TREE ALGORITHMS
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1674(size="medium"):
    """Subordinates: tree via parent array (bosses for employees 2..n)."""
    n = _sz(size, 1, 15, 200, 500)
    if n == 1:
        return "1\n"
    parents = _tree_parent_array(n)
    return f"{n}\n{_arr(parents)}"


def gen_1130(size="medium"):
    """Tree Matching: n nodes, n-1 edges."""
    n = _sz(size, 2, 15, 200, 500)
    edges = _random_tree(n)
    return f"{n}\n{_fmt(edges)}"


def gen_1131(size="medium"):
    """Tree Diameter: n nodes, n-1 edges."""
    n = _sz(size, 2, 15, 200, 500)
    edges = _random_tree(n)
    return f"{n}\n{_fmt(edges)}"


def gen_1132(size="medium"):
    """Tree Distances I: n nodes, n-1 edges."""
    n = _sz(size, 2, 15, 200, 500)
    edges = _random_tree(n)
    return f"{n}\n{_fmt(edges)}"


def gen_1133(size="medium"):
    """Tree Distances II: n nodes, n-1 edges."""
    n = _sz(size, 2, 15, 200, 500)
    edges = _random_tree(n)
    return f"{n}\n{_fmt(edges)}"


def gen_1687(size="medium"):
    """Company Queries I: tree + ancestor queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    parents = _tree_parent_array(n)
    lines = [f"{n} {q}", _arr(parents)]
    for _ in range(q):
        x = random.randint(1, n)
        k = random.randint(1, n)
        lines.append(f"{x} {k}")
    return "\n".join(lines)


def gen_1688(size="medium"):
    """Company Queries II: tree + LCA queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    parents = _tree_parent_array(n)
    lines = [f"{n} {q}", _arr(parents)]
    for _ in range(q):
        a = random.randint(1, n)
        b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1135(size="medium"):
    """Distance Queries: tree + q distance queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    edges = _random_tree(n)
    lines = [f"{n} {q}", _fmt(edges)]
    for _ in range(q):
        a = random.randint(1, n)
        b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1136(size="medium"):
    """Counting Paths: tree + m paths."""
    n = _sz(size, 2, 15, 200, 500)
    m = _sz(size, 1, 15, 200, 500)
    edges = _random_tree(n)
    lines = [f"{n} {m}", _fmt(edges)]
    for _ in range(m):
        a = random.randint(1, n)
        b = random.randint(1, n)
        lines.append(f"{a} {b}")
    return "\n".join(lines)


def gen_1137(size="medium"):
    """Subtree Queries: tree with values + queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    values = _random_array(n, 1, 10**9)
    edges = _random_tree(n)
    lines = [f"{n} {q}", _arr(values), _fmt(edges)]
    for _ in range(q):
        if random.random() < 0.4:
            s = random.randint(1, n)
            x = random.randint(1, 10**9)
            lines.append(f"1 {s} {x}")
        else:
            s = random.randint(1, n)
            lines.append(f"2 {s}")
    return "\n".join(lines)


def gen_1138(size="medium"):
    """Path Queries: tree with values + queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    values = _random_array(n, 1, 10**9)
    edges = _random_tree(n)
    lines = [f"{n} {q}", _arr(values), _fmt(edges)]
    for _ in range(q):
        if random.random() < 0.4:
            s = random.randint(1, n)
            x = random.randint(1, 10**9)
            lines.append(f"1 {s} {x}")
        else:
            a = random.randint(1, n)
            b = random.randint(1, n)
            lines.append(f"2 {a} {b}")
    return "\n".join(lines)


def gen_2134(size="medium"):
    """Path Queries II: tree with values + path max/update queries."""
    n = _sz(size, 2, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    values = _random_array(n, 1, 10**9)
    edges = _random_tree(n)
    lines = [f"{n} {q}", _arr(values), _fmt(edges)]
    for _ in range(q):
        if random.random() < 0.4:
            s = random.randint(1, n)
            x = random.randint(1, 10**9)
            lines.append(f"1 {s} {x}")
        else:
            a = random.randint(1, n)
            b = random.randint(1, n)
            lines.append(f"2 {a} {b}")
    return "\n".join(lines)


def gen_1139(size="medium"):
    """Distinct Colors: tree with colors."""
    n = _sz(size, 2, 15, 200, 500)
    colors = _random_array(n, 1, max(1, n // 2))
    edges = _random_tree(n)
    return f"{n}\n{_arr(colors)}\n{_fmt(edges)}"


def gen_2079(size="medium"):
    """Finding a Centroid: tree."""
    n = _sz(size, 2, 15, 200, 500)
    edges = _random_tree(n)
    return f"{n}\n{_fmt(edges)}"


def gen_2080(size="medium"):
    """Fixed-Length Paths I: tree, path length k."""
    n = _sz(size, 2, 15, 200, 500)
    k = random.randint(1, max(1, n // 2))
    edges = _random_tree(n)
    return f"{n} {k}\n{_fmt(edges)}"


def gen_2081(size="medium"):
    """Fixed-Length Paths II: tree, path length range [k1, k2]."""
    n = _sz(size, 2, 15, 200, 500)
    k1 = random.randint(1, max(1, n // 3))
    k2 = random.randint(k1, max(k1, n // 2))
    edges = _random_tree(n)
    return f"{n} {k1} {k2}\n{_fmt(edges)}"


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDING WINDOW
# ═══════════════════════════════════════════════════════════════════════════════


def _sliding_window_input(size, allow_negative=False):
    """Generate sliding window input: n k, then n values."""
    n = _sz(size, 1, 15, 200, 500)
    k = random.randint(1, n)
    lo = -(10**9) if allow_negative else 1
    arr = _edge_case_array(n, lo, 10**9) if size == "edge" else _random_array(n, lo, 10**9)
    return f"{n} {k}\n{_arr(arr)}"


def gen_3220(size="medium"):
    """Sliding Window Minimum."""
    return _sliding_window_input(size)


def gen_3221(size="medium"):
    """Sliding Window Maximum."""
    return _sliding_window_input(size)


def gen_3222(size="medium"):
    """Sliding Window Median."""
    return _sliding_window_input(size)


def gen_3223(size="medium"):
    """Sliding Window Cost."""
    return _sliding_window_input(size)


def gen_3224(size="medium"):
    """Sliding Window Sum."""
    return _sliding_window_input(size, allow_negative=True)


def gen_3225(size="medium"):
    """Sliding Window: variant."""
    return _sliding_window_input(size)


def gen_3226(size="medium"):
    """Sliding Window: variant."""
    return _sliding_window_input(size)


def gen_3227(size="medium"):
    """Sliding Window: variant."""
    return _sliding_window_input(size)


# ═══════════════════════════════════════════════════════════════════════════════
# BITWISE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def gen_1655(size="medium"):
    """Bit Inversions: bit string + q flip positions."""
    n = _sz(size, 1, 15, 200, 500)
    q = _sz(size, 1, 15, 200, 500)
    bits = "".join(random.choice("01") for _ in range(n))
    positions = _random_array(q, 1, n)
    return f"{bits}\n{q}\n{_arr(positions)}"


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

GENERATORS = {
    # Introductory Problems
    1068: gen_1068, 1083: gen_1083, 1069: gen_1069, 1094: gen_1094,
    1070: gen_1070, 1071: gen_1071, 1072: gen_1072, 1092: gen_1092,
    1617: gen_1617, 1618: gen_1618, 1754: gen_1754, 1755: gen_1755,
    2205: gen_2205, 2165: gen_2165, 1622: gen_1622, 1623: gen_1623,
    1624: gen_1624, 2431: gen_2431, 1743: gen_1743, 1625: gen_1625,
    # Sorting and Searching
    1621: gen_1621, 1084: gen_1084, 1090: gen_1090, 1091: gen_1091,
    1619: gen_1619, 1629: gen_1629, 1640: gen_1640, 1643: gen_1643,
    1074: gen_1074, 2183: gen_2183, 2216: gen_2216, 2217: gen_2217,
    1141: gen_1141, 1073: gen_1073, 1163: gen_1163, 3420: gen_3420,
    3421: gen_3421, 2162: gen_2162, 2163: gen_2163, 2168: gen_2168,
    2169: gen_2169, 1164: gen_1164, 1620: gen_1620, 1630: gen_1630,
    1631: gen_1631, 1641: gen_1641, 1642: gen_1642, 1645: gen_1645,
    1660: gen_1660, 1661: gen_1661, 1662: gen_1662, 2428: gen_2428,
    1085: gen_1085, 1632: gen_1632, 1644: gen_1644,
    # Dynamic Programming
    1633: gen_1633, 1634: gen_1634, 1635: gen_1635, 1636: gen_1636,
    1637: gen_1637, 1638: gen_1638, 1158: gen_1158, 1746: gen_1746,
    2413: gen_2413, 1639: gen_1639, 3403: gen_3403, 1744: gen_1744,
    1745: gen_1745, 1097: gen_1097, 1093: gen_1093, 1145: gen_1145,
    1140: gen_1140, 1653: gen_1653, 2181: gen_2181, 2220: gen_2220,
    1748: gen_1748,
    # Graph Algorithms
    1192: gen_1192, 1193: gen_1193, 1666: gen_1666, 1667: gen_1667,
    1668: gen_1668, 1669: gen_1669, 1194: gen_1194, 1671: gen_1671,
    1672: gen_1672, 1673: gen_1673, 1195: gen_1195, 1197: gen_1197,
    1196: gen_1196, 1678: gen_1678, 1679: gen_1679, 1680: gen_1680,
    1681: gen_1681, 1202: gen_1202, 1750: gen_1750, 1160: gen_1160,
    1751: gen_1751, 1675: gen_1675, 1676: gen_1676, 1682: gen_1682,
    1683: gen_1683, 1684: gen_1684, 1686: gen_1686, 1691: gen_1691,
    1692: gen_1692, 1693: gen_1693, 1690: gen_1690, 1689: gen_1689,
    1694: gen_1694, 1695: gen_1695, 1696: gen_1696, 1711: gen_1711,
    # Range Queries
    1646: gen_1646, 1647: gen_1647, 1648: gen_1648, 1649: gen_1649,
    1650: gen_1650, 1651: gen_1651, 1652: gen_1652, 2166: gen_2166,
    2206: gen_2206, 1143: gen_1143, 1749: gen_1749, 1144: gen_1144,
    2184: gen_2184,
    # Tree Algorithms
    1674: gen_1674, 1130: gen_1130, 1131: gen_1131, 1132: gen_1132,
    1133: gen_1133, 1687: gen_1687, 1688: gen_1688, 1135: gen_1135,
    1136: gen_1136, 1137: gen_1137, 1138: gen_1138, 2134: gen_2134,
    1139: gen_1139, 2079: gen_2079, 2080: gen_2080, 2081: gen_2081,
    # Sliding Window
    3220: gen_3220, 3221: gen_3221, 3222: gen_3222, 3223: gen_3223,
    3224: gen_3224, 3225: gen_3225, 3226: gen_3226, 3227: gen_3227,
    # Bitwise Operations
    1655: gen_1655,
}


def generate(task_id, size="medium"):
    """Generate input for the given CSES task ID."""
    gen = GENERATORS.get(task_id)
    if gen is None:
        raise ValueError(f"No generator for task {task_id}")
    return gen(size)
