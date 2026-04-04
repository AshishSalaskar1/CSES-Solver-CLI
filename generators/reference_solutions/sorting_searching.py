"""Reference solutions for CSES Sorting and Searching problems."""

from __future__ import annotations

import sys
from bisect import bisect_left, bisect_right, insort
from collections import defaultdict
from heapq import heappush, heappop


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1621 - Distinct Numbers
# ---------------------------------------------------------------------------
def _solve_1621(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    return str(len(set(arr)))


# ---------------------------------------------------------------------------
# 1084 - Apartments
# ---------------------------------------------------------------------------
def _solve_1084(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m, k = map(int, lines[0].split())
    a = sorted(map(int, lines[1].split()))
    b = sorted(map(int, lines[2].split()))
    i = j = count = 0
    while i < n and j < m:
        if a[i] < b[j] - k:
            i += 1
        elif a[i] > b[j] + k:
            j += 1
        else:
            count += 1
            i += 1
            j += 1
    return str(count)


# ---------------------------------------------------------------------------
# 1090 - Ferris Wheel
# ---------------------------------------------------------------------------
def _solve_1090(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    w = sorted(map(int, lines[1].split()))
    lo, hi = 0, n - 1
    gondolas = 0
    while lo <= hi:
        if lo == hi:
            gondolas += 1
            break
        if w[lo] + w[hi] <= x:
            lo += 1
        hi -= 1
        gondolas += 1
    return str(gondolas)


# ---------------------------------------------------------------------------
# 1091 - Concert Tickets
# ---------------------------------------------------------------------------
def _solve_1091(input_data: str) -> str:
    lines = input_data.split("\n")
    _n, m = map(int, lines[0].split())
    tickets = list(map(int, lines[1].split()))
    customers = list(map(int, lines[2].split()))
    # Use a sorted list with bisect
    sorted_tickets = sorted(tickets)
    out = []
    for max_price in customers:
        idx = bisect_right(sorted_tickets, max_price) - 1
        if idx < 0:
            out.append("-1")
        else:
            out.append(str(sorted_tickets[idx]))
            sorted_tickets.pop(idx)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1619 - Restaurant Customers
# ---------------------------------------------------------------------------
def _solve_1619(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    events = []
    for i in range(1, n + 1):
        a, b = map(int, lines[i].split())
        events.append((a, 1))
        events.append((b, -1))
    events.sort(key=lambda e: (e[0], e[1]))
    cur = best = 0
    for _, typ in events:
        cur += typ
        if cur > best:
            best = cur
    return str(best)


# ---------------------------------------------------------------------------
# 1629 - Movie Festival
# ---------------------------------------------------------------------------
def _solve_1629(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    movies = []
    for i in range(1, n + 1):
        a, b = map(int, lines[i].split())
        movies.append((b, a))
    movies.sort()
    count = 0
    last_end = -1
    for end, start in movies:
        if start >= last_end:
            count += 1
            last_end = end
    return str(count)


# ---------------------------------------------------------------------------
# 1640 - Sum of Two Values
# ---------------------------------------------------------------------------
def _solve_1640(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    seen: dict[int, int] = {}
    for i, v in enumerate(arr):
        comp = x - v
        if comp in seen:
            return f"{seen[comp] + 1} {i + 1}"
        seen[v] = i
    return "IMPOSSIBLE"


# ---------------------------------------------------------------------------
# 1643 - Maximum Subarray Sum
# ---------------------------------------------------------------------------
def _solve_1643(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    best = cur = arr[0]
    for v in arr[1:]:
        cur = max(v, cur + v)
        if cur > best:
            best = cur
    return str(best)


# ---------------------------------------------------------------------------
# 1074 - Stick Lengths
# ---------------------------------------------------------------------------
def _solve_1074(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = sorted(map(int, lines[1].split()))
    median = arr[n // 2]
    return str(sum(abs(v - median) for v in arr))


# ---------------------------------------------------------------------------
# 2183 - Missing Coin Sum
# ---------------------------------------------------------------------------
def _solve_2183(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    arr = sorted(map(int, lines[1].split()))
    smallest = 1
    for v in arr:
        if v > smallest:
            break
        smallest += v
    return str(smallest)


# ---------------------------------------------------------------------------
# 2216 - Collecting Numbers
# ---------------------------------------------------------------------------
def _solve_2216(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    pos = [0] * (n + 1)
    for i, v in enumerate(arr):
        pos[v] = i
    rounds = 1
    for v in range(2, n + 1):
        if pos[v] < pos[v - 1]:
            rounds += 1
    return str(rounds)


# ---------------------------------------------------------------------------
# 2217 - Collecting Numbers II
# ---------------------------------------------------------------------------
def _solve_2217(input_data: str) -> str:
    lines = input_data.split("\n")
    n, m = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    pos = [0] * (n + 1)  # pos[value] = index in arr
    for i, v in enumerate(arr):
        pos[v] = i

    # Compute initial rounds
    rounds = 1
    for v in range(2, n + 1):
        if pos[v] < pos[v - 1]:
            rounds += 1

    out = []
    for i in range(2, 2 + m):
        a, b = map(int, lines[i].split())
        a -= 1  # convert to 0-indexed
        b -= 1
        va, vb = arr[a], arr[b]

        # For each value v in {va, vb}, check the pair (v-1, v) and (v, v+1).
        # Before swap: count inversions for affected pairs.
        # After swap: recount.
        affected = set()
        for v in (va, vb):
            if v > 1:
                affected.add(v)
            if v < n:
                affected.add(v + 1)

        # Subtract old contributions
        for v in affected:
            if pos[v] < pos[v - 1]:
                rounds -= 1

        # Perform the swap
        arr[a], arr[b] = arr[b], arr[a]
        pos[va], pos[vb] = pos[vb], pos[va]

        # Add new contributions
        for v in affected:
            if pos[v] < pos[v - 1]:
                rounds += 1

        out.append(str(rounds))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 1141 - Playlist
# ---------------------------------------------------------------------------
def _solve_1141(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    last_seen: dict[int, int] = {}
    best = 0
    left = 0
    for right in range(n):
        v = arr[right]
        if v in last_seen and last_seen[v] >= left:
            left = last_seen[v] + 1
        last_seen[v] = right
        length = right - left + 1
        if length > best:
            best = length
    return str(best)


# ---------------------------------------------------------------------------
# 1073 - Towers
# ---------------------------------------------------------------------------
def _solve_1073(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    # Greedy: place each cube on the tower whose top is the smallest value
    # strictly greater than the cube. Maintain sorted list of tower tops.
    tops: list[int] = []
    for cube in arr:
        idx = bisect_right(tops, cube)
        if idx < len(tops):
            tops.pop(idx)
            insort(tops, cube)
        else:
            insort(tops, cube)
    return str(len(tops))


# ---------------------------------------------------------------------------
# 1163 - Traffic Lights
# ---------------------------------------------------------------------------
def _solve_1163(input_data: str) -> str:
    lines = input_data.split("\n")
    x, n = map(int, lines[0].split())
    positions = list(map(int, lines[1].split()))

    # Sorted list of light positions + sorted list of gaps for O(log n) max
    lights: list[int] = [0, x]
    gaps: list[int] = [x]
    out = []
    for p in positions:
        idx = bisect_left(lights, p)
        left = lights[idx - 1]
        right = lights[idx]
        old_gap = right - left

        rm_idx = bisect_left(gaps, old_gap)
        gaps.pop(rm_idx)

        g1 = p - left
        g2 = right - p
        insort(gaps, g1)
        insort(gaps, g2)
        insort(lights, p)

        out.append(str(gaps[-1]))
    return " ".join(out)


# ---------------------------------------------------------------------------
# 3420 - Distinct Values Subarrays (a.k.a. "Number of Subarrays with All
#        Distinct Values")
#   Count the number of subarrays where every element is distinct.
# ---------------------------------------------------------------------------
def _solve_3420(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    last: dict[int, int] = {}
    left = 0
    count = 0
    for right in range(n):
        v = arr[right]
        if v in last and last[v] >= left:
            left = last[v] + 1
        last[v] = right
        count += right - left + 1
    return str(count)


# ---------------------------------------------------------------------------
# 3421 - Distinct Values Subsequences
#   Count the number of distinct subsequences (by value, not index).
#   dp approach: dp[i] = 2*dp[i-1] - dp[last[arr[i]]-1] (removing duplicates)
# ---------------------------------------------------------------------------
def _solve_3421(input_data: str) -> str:
    MOD = 10**9 + 7
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    # dp[i] = number of distinct non-empty subsequences considering first i elements
    # Actually let's track total (including empty) then subtract 1.
    # f(0) = 1 (empty subsequence)
    # f(i) = 2*f(i-1) - f(last_occurrence_of_arr[i] - 1)
    # where last_occurrence stores the previous index (1-based) of arr[i], or 0 if first time
    last: dict[int, int] = {}
    dp = [0] * (n + 1)
    dp[0] = 1  # empty subsequence
    for i in range(1, n + 1):
        v = arr[i - 1]
        dp[i] = (2 * dp[i - 1]) % MOD
        if v in last:
            dp[i] = (dp[i] - dp[last[v] - 1]) % MOD
        last[v] = i
    # dp[n] includes the empty subsequence, subtract 1
    return str((dp[n] - 1) % MOD)


# ---------------------------------------------------------------------------
# 2162 - Josephus Problem I (every 2nd person eliminated)
# ---------------------------------------------------------------------------
def _solve_2162(input_data: str) -> str:
    n = int(input_data.strip())
    circle = list(range(1, n + 1))
    idx = 1  # start by removing 2nd person (0-indexed: index 1)
    out = []
    while circle:
        idx = idx % len(circle)
        out.append(str(circle.pop(idx)))
        if circle:
            idx = idx % len(circle)
            # next removal is 2 steps from current idx
            # after pop, the element at idx is already the next one,
            # so we advance by 1 more to skip one person
            idx = (idx + 1) % len(circle) if circle else 0
    return " ".join(out)


# ---------------------------------------------------------------------------
# 2163 - Josephus Problem II (every k-th person eliminated)
#   Using a BIT (Fenwick tree) for O(n log^2 n) simulation.
# ---------------------------------------------------------------------------
def _solve_2163(input_data: str) -> str:
    n, k = map(int, input_data.strip().split())

    # BIT to track active people: bit stores 1 for active, 0 for removed
    tree = [0] * (n + 1)

    def update(i: int, delta: int) -> None:
        while i <= n:
            tree[i] += delta
            i += i & (-i)

    def query(i: int) -> int:
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & (-i)
        return s

    def find_kth(k_val: int) -> int:
        """Find the k-th active person (1-indexed)."""
        pos = 0
        bit_mask = 1
        while bit_mask <= n:
            bit_mask <<= 1
        bit_mask >>= 1
        while bit_mask > 0:
            next_pos = pos + bit_mask
            if next_pos <= n and tree[next_pos] < k_val:
                k_val -= tree[next_pos]
                pos = next_pos
            bit_mask >>= 1
        return pos + 1

    for i in range(1, n + 1):
        update(i, 1)

    out = []
    remaining = n
    start = 0  # 0-indexed starting position for next count
    for _ in range(n):
        cur_rank = (start + k - 1) % remaining
        person = find_kth(cur_rank + 1)
        out.append(str(person))
        update(person, -1)
        remaining -= 1
        if remaining > 0:
            start = cur_rank % remaining
    return " ".join(out)


# ---------------------------------------------------------------------------
# 2168 - Nested Ranges Check
# ---------------------------------------------------------------------------
def _solve_2168(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    ranges = []
    for i in range(1, n + 1):
        l, r = map(int, lines[i].split())
        ranges.append((l, r, i - 1))

    contains = [0] * n  # does range i contain some other range?
    contained = [0] * n  # is range i contained by some other range?

    # Sort by left ascending, then right descending
    sorted_ranges = sorted(ranges, key=lambda t: (t[0], -t[1]))

    # "contained by" sweep: left to right
    max_r = -1
    for l, r, idx in sorted_ranges:
        if r <= max_r:
            contained[idx] = 1
        if r > max_r:
            max_r = r

    # "contains" sweep: right to left
    min_r = float("inf")
    for l, r, idx in reversed(sorted_ranges):
        if r >= min_r:
            contains[idx] = 1
        if r < min_r:
            min_r = r

    # Fix for duplicate ranges: if (l,r) appears more than once, every
    # copy both contains and is contained by the other copies.
    from collections import Counter
    rc = Counter((l, r) for l, r, _ in ranges)
    for l, r, idx in ranges:
        if rc[(l, r)] > 1:
            contains[idx] = 1
            contained[idx] = 1

    line1 = " ".join(str(contains[i]) for i in range(n))
    line2 = " ".join(str(contained[i]) for i in range(n))
    return line1 + "\n" + line2


# ---------------------------------------------------------------------------
# 2169 - Nested Ranges Count
# ---------------------------------------------------------------------------
def _solve_2169(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    ranges = []
    for i in range(1, n + 1):
        l, r = map(int, lines[i].split())
        ranges.append((l, r, i - 1))

    # Coordinate compress the right endpoints
    rights = sorted(set(r for _, r, _ in ranges))
    compress = {v: i + 1 for i, v in enumerate(rights)}
    m = len(rights)

    # BIT for counting
    bit = [0] * (m + 2)

    def bit_update(i: int, delta: int = 1) -> None:
        while i <= m:
            bit[i] += delta
            i += i & (-i)

    def bit_query(i: int) -> int:
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    contains_count = [0] * n
    contained_count = [0] * n

    sorted_ranges = sorted(ranges, key=lambda t: (t[0], -t[1]))

    # Count duplicates of each (l, r) pair
    from collections import Counter
    rc = Counter((l, r) for l, r, _ in ranges)

    # "contained_by" count: process groups left to right.
    # For each group with same (l, r), all members have the same count.
    bit = [0] * (m + 2)
    i = 0
    while i < len(sorted_ranges):
        j = i
        while (j < len(sorted_ranges)
               and sorted_ranges[j][0] == sorted_ranges[i][0]
               and sorted_ranges[j][1] == sorted_ranges[i][1]):
            j += 1
        group_size = j - i
        cr = compress[sorted_ranges[i][1]]
        count = i - bit_query(cr - 1) + (group_size - 1)
        for k in range(i, j):
            contained_count[sorted_ranges[k][2]] = count
        for _ in range(group_size):
            bit_update(cr)
        i = j

    # "contains" count: process groups right to left.
    bit = [0] * (m + 2)
    i = len(sorted_ranges) - 1
    while i >= 0:
        j = i
        while (j >= 0
               and sorted_ranges[j][0] == sorted_ranges[i][0]
               and sorted_ranges[j][1] == sorted_ranges[i][1]):
            j -= 1
        group_size = i - j
        cr = compress[sorted_ranges[i][1]]
        count = bit_query(cr) + (group_size - 1)
        for k in range(j + 1, i + 1):
            contains_count[sorted_ranges[k][2]] = count
        for _ in range(group_size):
            bit_update(cr)
        i = j

    line1 = " ".join(str(contains_count[i]) for i in range(n))
    line2 = " ".join(str(contained_count[i]) for i in range(n))
    return line1 + "\n" + line2


# ---------------------------------------------------------------------------
# 1164 - Room Allocation
# ---------------------------------------------------------------------------
def _solve_1164(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    customers = []
    for i in range(1, n + 1):
        a, b = map(int, lines[i].split())
        customers.append((a, b, i - 1))

    # Sort by arrival time, then by departure
    sorted_customers = sorted(customers, key=lambda t: (t[0], t[1]))
    # Min-heap: (leave_time, room_id)
    heap: list[tuple[int, int]] = []
    room_assignment = [0] * n
    next_room = 1

    for arrive, leave, orig_idx in sorted_customers:
        if heap and heap[0][0] < arrive:
            freed_leave, freed_room = heappop(heap)
            room_assignment[orig_idx] = freed_room
            heappush(heap, (leave, freed_room))
        else:
            room_assignment[orig_idx] = next_room
            heappush(heap, (leave, next_room))
            next_room += 1

    num_rooms = next_room - 1
    assignments = " ".join(str(room_assignment[i]) for i in range(n))
    return f"{num_rooms}\n{assignments}"


# ---------------------------------------------------------------------------
# 1620 - Factory Machines
# ---------------------------------------------------------------------------
def _solve_1620(input_data: str) -> str:
    lines = input_data.split("\n")
    n, t = map(int, lines[0].split())
    machines = list(map(int, lines[1].split()))

    def can_make(time: int) -> bool:
        total = 0
        for m in machines:
            total += time // m
            if total >= t:
                return True
        return False

    lo, hi = 0, min(machines) * t
    while lo < hi:
        mid = (lo + hi) // 2
        if can_make(mid):
            hi = mid
        else:
            lo = mid + 1
    return str(lo)


# ---------------------------------------------------------------------------
# 1630 - Tasks and Deadlines
# ---------------------------------------------------------------------------
def _solve_1630(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    tasks = []
    for i in range(1, n + 1):
        a, d = map(int, lines[i].split())
        tasks.append((a, d))
    # Sort by duration ascending
    tasks.sort()
    time = 0
    reward = 0
    for dur, deadline in tasks:
        time += dur
        reward += deadline - time
    return str(reward)


# ---------------------------------------------------------------------------
# 1631 - Reading Books
# ---------------------------------------------------------------------------
def _solve_1631(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    total = sum(arr)
    mx = max(arr)
    rest = total - mx
    if mx > rest:
        return str(2 * mx)
    else:
        return str(total)


# ---------------------------------------------------------------------------
# 1641 - Sum of Three Values
# ---------------------------------------------------------------------------
def _solve_1641(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    indexed = sorted(range(n), key=lambda i: arr[i])
    for i in range(n - 2):
        target = x - arr[indexed[i]]
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = arr[indexed[lo]] + arr[indexed[hi]]
            if s == target:
                result = sorted([indexed[i] + 1, indexed[lo] + 1, indexed[hi] + 1])
                return " ".join(map(str, result))
            elif s < target:
                lo += 1
            else:
                hi -= 1
    return "IMPOSSIBLE"


# ---------------------------------------------------------------------------
# 1642 - Sum of Four Values
# ---------------------------------------------------------------------------
def _solve_1642(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    # Store pairs (sum, i, j) and use a dict
    pair_sums: dict[int, list[tuple[int, int]]] = {}
    for i in range(n):
        for j in range(i + 1, n):
            s = arr[i] + arr[j]
            comp = x - s
            if comp in pair_sums:
                for pi, pj in pair_sums[comp]:
                    if pi != i and pi != j and pj != i and pj != j:
                        result = sorted([pi + 1, pj + 1, i + 1, j + 1])
                        return " ".join(map(str, result))
            # Add this pair to dict after checking to avoid using same pair
        # Add all pairs ending at j=current after the inner loop
        # Actually, to avoid issues, we add pairs (i, j) to the dict AFTER
        # we've checked all j for a given i. This way when we check (i2, j2),
        # all stored pairs (i1, j1) have j1 < i2, guaranteeing distinct indices.
        # Wait, that doesn't work because we need j1 < i2.
        # Better approach: add pairs as we go but with i < j, and when we check
        # complement, only use pairs where the max index < current min index.
        # Simplest correct approach: iterate i, then for each i iterate j > i,
        # check complement in previously stored pairs (which are all (a,b) with b < i).
        pass

    # Re-implement more carefully
    pair_sums2: dict[int, tuple[int, int]] = {}
    for i in range(n):
        for j in range(i + 1, n):
            s = arr[i] + arr[j]
            comp = x - s
            if comp in pair_sums2:
                pi, pj = pair_sums2[comp]
                if pi != i and pi != j and pj != i and pj != j:
                    result = sorted([pi + 1, pj + 1, i + 1, j + 1])
                    return " ".join(map(str, result))
        # After processing all j for this i, add all pairs (prev, i) where prev < i
        for prev in range(i):
            s = arr[prev] + arr[i]
            if s not in pair_sums2:
                pair_sums2[s] = (prev, i)
    return "IMPOSSIBLE"


# ---------------------------------------------------------------------------
# 1645 - Nearest Smaller Values
# ---------------------------------------------------------------------------
def _solve_1645(input_data: str) -> str:
    lines = input_data.split("\n")
    _n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    stack: list[tuple[int, int]] = []  # (value, 1-based index)
    out = []
    for i, v in enumerate(arr):
        while stack and stack[-1][0] >= v:
            stack.pop()
        if stack:
            out.append(str(stack[-1][1]))
        else:
            out.append("0")
        stack.append((v, i + 1))
    return " ".join(out)


# ---------------------------------------------------------------------------
# 1660 - Subarray Sums I (positive values)
# ---------------------------------------------------------------------------
def _solve_1660(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    count = 0
    cur_sum = 0
    left = 0
    for right in range(n):
        cur_sum += arr[right]
        while cur_sum > x and left <= right:
            cur_sum -= arr[left]
            left += 1
        if cur_sum == x:
            count += 1
    return str(count)


# ---------------------------------------------------------------------------
# 1661 - Subarray Sums II (values can be negative)
# ---------------------------------------------------------------------------
def _solve_1661(input_data: str) -> str:
    lines = input_data.split("\n")
    n, x = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))
    prefix = 0
    freq: dict[int, int] = defaultdict(int)
    freq[0] = 1
    count = 0
    for v in arr:
        prefix += v
        count += freq[prefix - x]
        freq[prefix] += 1
    return str(count)


# ---------------------------------------------------------------------------
# 1662 - Subarray Divisibility
# ---------------------------------------------------------------------------
def _solve_1662(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    prefix = 0
    freq: dict[int, int] = defaultdict(int)
    freq[0] = 1
    count = 0
    for v in arr:
        prefix += v
        r = prefix % n
        count += freq[r]
        freq[r] += 1
    return str(count)


# ---------------------------------------------------------------------------
# 2428 - Distinct Values Subarrays II (a.k.a. "Array Description" variant
#        or "Distinct Values Queries" — count total distinct values across
#        all subarrays)
#   For each position i (0-indexed), contribution = (i - last[val] ) * (n - i)
#   where last[val] is the previous occurrence of arr[i] (or -1 if first).
# ---------------------------------------------------------------------------
def _solve_2428(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    arr = list(map(int, lines[1].split()))
    last: dict[int, int] = {}
    total = 0
    for i in range(n):
        v = arr[i]
        prev = last.get(v, -1)
        total += (i - prev) * (n - i)
        last[v] = i
    return str(total)


# ---------------------------------------------------------------------------
# 1085 - Array Division
# ---------------------------------------------------------------------------
def _solve_1085(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))

    def feasible(max_sum: int) -> bool:
        parts = 1
        cur = 0
        for v in arr:
            if v > max_sum:
                return False
            if cur + v > max_sum:
                parts += 1
                cur = v
                if parts > k:
                    return False
            else:
                cur += v
        return True

    lo, hi = max(arr), sum(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return str(lo)


# ---------------------------------------------------------------------------
# 1632 - Movie Festival II
# ---------------------------------------------------------------------------
def _solve_1632(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    movies = []
    for i in range(1, n + 1):
        a, b = map(int, lines[i].split())
        movies.append((b, a))  # sort by end time
    movies.sort()

    # members: sorted list of "last end times" for each member
    members: list[int] = [0] * k  # all members initially free at time 0
    count = 0
    for end, start in movies:
        # Find the member who finished latest but still at or before start
        idx = bisect_right(members, start) - 1
        if idx >= 0:
            count += 1
            members.pop(idx)
            insort(members, end)
    return str(count)


# ---------------------------------------------------------------------------
# 1644 - Maximum Subarray Sum II
#   Find maximum subarray sum with length between a and b.
#   Use prefix sums and a deque to maintain the minimum prefix sum in window.
# ---------------------------------------------------------------------------
def _solve_1644(input_data: str) -> str:
    from collections import deque

    lines = input_data.split("\n")
    n, a, b = map(int, lines[0].split())
    arr = list(map(int, lines[1].split()))

    # prefix[i] = sum of arr[0..i-1]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]

    # For subarray [l, r] (0-indexed, inclusive) with a <= r-l+1 <= b:
    # sum = prefix[r+1] - prefix[l]
    # We want to maximize prefix[r+1] - prefix[l]
    # where r+1 - b <= l <= r+1 - a, and l >= 0.
    # For each r (from a-1 to n-1), we look at j = r+1, and need
    # min prefix[l] for l in [j-b, j-a].
    # Use a deque to maintain min prefix in sliding window.

    best = -float("inf")
    dq: deque[int] = deque()  # indices into prefix array

    for j in range(a, n + 1):
        # Add prefix[j - a] to the deque (the new candidate for minimum)
        new_l = j - a
        while dq and prefix[dq[-1]] >= prefix[new_l]:
            dq.pop()
        dq.append(new_l)

        # Remove indices that are out of window [j-b, j-a]
        while dq[0] < j - b:
            dq.popleft()

        val = prefix[j] - prefix[dq[0]]
        if val > best:
            best = val

    return str(best)


# ---------------------------------------------------------------------------
# Solution dispatch table
# ---------------------------------------------------------------------------
SOLUTIONS: dict[int, callable] = {
    1621: _solve_1621,
    1084: _solve_1084,
    1090: _solve_1090,
    1091: _solve_1091,
    1619: _solve_1619,
    1629: _solve_1629,
    1640: _solve_1640,
    1643: _solve_1643,
    1074: _solve_1074,
    2183: _solve_2183,
    2216: _solve_2216,
    2217: _solve_2217,
    1141: _solve_1141,
    1073: _solve_1073,
    1163: _solve_1163,
    3420: _solve_3420,
    3421: _solve_3421,
    2162: _solve_2162,
    2163: _solve_2163,
    2168: _solve_2168,
    2169: _solve_2169,
    1164: _solve_1164,
    1620: _solve_1620,
    1630: _solve_1630,
    1631: _solve_1631,
    1641: _solve_1641,
    1642: _solve_1642,
    1645: _solve_1645,
    1660: _solve_1660,
    1661: _solve_1661,
    1662: _solve_1662,
    2428: _solve_2428,
    1085: _solve_1085,
    1632: _solve_1632,
    1644: _solve_1644,
}
