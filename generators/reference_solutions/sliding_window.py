"""Reference solutions for CSES Sliding Window problems."""

from __future__ import annotations

import sys
from collections import deque, defaultdict
from heapq import heappush, heappop


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 3220 - Sliding Window Sum
# ---------------------------------------------------------------------------
def _solve_3220(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    s = sum(a[:k])
    out = [s]
    for i in range(k, n):
        s += a[i] - a[i - k]
        out.append(s)
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 3221 - Sliding Window Minimum
# ---------------------------------------------------------------------------
def _solve_3221(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    dq = deque()  # stores indices, a[dq[0]] is current min
    out = []
    for i in range(n):
        while dq and a[dq[-1]] >= a[i]:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 3426 - Sliding Window Xor
# ---------------------------------------------------------------------------
def _solve_3426(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    xr = 0
    for i in range(k):
        xr ^= a[i]
    out = [xr]
    for i in range(k, n):
        xr ^= a[i] ^ a[i - k]
        out.append(xr)
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 3405 - Sliding Window Or
# ---------------------------------------------------------------------------
def _solve_3405(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    # Track bit counts for each of 30 bits
    bits = [0] * 30
    for i in range(k):
        v = a[i]
        for b in range(30):
            if v & (1 << b):
                bits[b] += 1
    def bits_to_or():
        r = 0
        for b in range(30):
            if bits[b] > 0:
                r |= (1 << b)
        return r
    out = [bits_to_or()]
    for i in range(k, n):
        # add a[i]
        v = a[i]
        for b in range(30):
            if v & (1 << b):
                bits[b] += 1
        # remove a[i-k]
        v = a[i - k]
        for b in range(30):
            if v & (1 << b):
                bits[b] -= 1
        out.append(bits_to_or())
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 3222 - Sliding Window Distinct Values
# ---------------------------------------------------------------------------
def _solve_3222(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    cnt = defaultdict(int)
    distinct = 0
    for i in range(k):
        if cnt[a[i]] == 0:
            distinct += 1
        cnt[a[i]] += 1
    out = [distinct]
    for i in range(k, n):
        # add a[i]
        if cnt[a[i]] == 0:
            distinct += 1
        cnt[a[i]] += 1
        # remove a[i-k]
        cnt[a[i - k]] -= 1
        if cnt[a[i - k]] == 0:
            distinct -= 1
        out.append(distinct)
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 3224 - Sliding Window Mode
# ---------------------------------------------------------------------------
def _solve_3224(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    cnt = defaultdict(int)
    max_freq = 0
    for i in range(k):
        cnt[a[i]] += 1
        if cnt[a[i]] > max_freq:
            max_freq = cnt[a[i]]
    out = [max_freq]
    for i in range(k, n):
        cnt[a[i]] += 1
        if cnt[a[i]] > max_freq:
            max_freq = cnt[a[i]]
        cnt[a[i - k]] -= 1
        # If we reduced the element that had max_freq, we might need to decrease
        # But we can only decrease by 1 and only if this was the only one at max_freq
        if cnt[a[i - k]] == max_freq - 1:
            # Check if any element still has max_freq
            # This is O(1) amortized if we keep a frequency-of-frequency count
            pass
        out.append(max_freq)
    # The above approach is broken for max_freq tracking on removal.
    # Let's redo with freq-of-freq.
    cnt2 = defaultdict(int)
    freq_count = defaultdict(int)  # freq_count[f] = number of distinct values with frequency f
    max_freq2 = 0
    out2 = []
    for i in range(n):
        # add a[i]
        old_f = cnt2[a[i]]
        cnt2[a[i]] += 1
        new_f = cnt2[a[i]]
        if old_f > 0:
            freq_count[old_f] -= 1
        freq_count[new_f] += 1
        if new_f > max_freq2:
            max_freq2 = new_f
        # remove a[i-k] if window is full
        if i >= k:
            old_f = cnt2[a[i - k]]
            cnt2[a[i - k]] -= 1
            new_f = cnt2[a[i - k]]
            freq_count[old_f] -= 1
            if new_f > 0:
                freq_count[new_f] += 1
            if old_f == max_freq2 and freq_count[old_f] == 0:
                max_freq2 -= 1
        if i >= k - 1:
            out2.append(max_freq2)
    return "\n".join(map(str, out2))


# ---------------------------------------------------------------------------
# 3219 - Sliding Window Mex
# ---------------------------------------------------------------------------
def _solve_3219(input_data: str) -> str:
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    cnt = defaultdict(int)
    # We need the minimum non-negative integer not in the window.
    # Use a sorted set of "zeros" — values with cnt == 0.
    # Actually, let's use a different approach: track counts and find mex.
    # Mex can be at most k (window size), so we only need to track values 0..k.
    # Use a set of missing values in range [0, k].
    missing = set(range(k + 1))
    for i in range(k):
        v = a[i]
        if v <= k:
            cnt[v] += 1
            if v in missing:
                missing.discard(v)
    out = [min(missing)]
    for i in range(k, n):
        # add a[i]
        v = a[i]
        if v <= k:
            cnt[v] += 1
            missing.discard(v)
        # remove a[i-k]
        v = a[i - k]
        if v <= k:
            cnt[v] -= 1
            if cnt[v] == 0:
                missing.add(v)
        out.append(min(missing))
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 1076 - Sliding Window Median
# ---------------------------------------------------------------------------
def _solve_1076(input_data: str) -> str:
    """Sliding window median using two heaps with lazy deletion."""
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    # low: max-heap (negate values), high: min-heap
    low = []   # max-heap (negated)
    high = []  # min-heap
    low_size = 0
    high_size = 0
    removed = defaultdict(int)

    def add(val):
        nonlocal low_size, high_size
        if low_size == 0 or val <= -low[0]:
            heappush(low, -val)
            low_size += 1
        else:
            heappush(high, val)
            high_size += 1

    def remove(val):
        nonlocal low_size, high_size
        removed[val] += 1
        if val <= -low[0]:
            low_size -= 1
        else:
            high_size -= 1

    def balance():
        nonlocal low_size, high_size
        # We want low_size to be ceil(k/2) when total is k
        # i.e., low_size - high_size == 0 or 1
        while low_size > high_size + 1:
            val = -low[0]
            heappush(high, val)
            heappop(low)
            low_size -= 1
            high_size += 1
            prune_top()
        while high_size > low_size:
            val = high[0]
            heappush(low, -val)
            heappop(high)
            high_size -= 1
            low_size += 1
            prune_top()

    def prune_top():
        while low and removed[-low[0]] > 0:
            removed[-low[0]] -= 1
            heappop(low)
        while high and removed[high[0]] > 0:
            removed[high[0]] -= 1
            heappop(high)

    out = []
    for i in range(n):
        add(a[i])
        balance()
        prune_top()
        if i >= k:
            remove(a[i - k])
            balance()
            prune_top()
        if i >= k - 1:
            out.append(-low[0])
    return "\n".join(map(str, out))


# ---------------------------------------------------------------------------
# 1077 - Sliding Window Cost
# ---------------------------------------------------------------------------
def _solve_1077(input_data: str) -> str:
    """Minimum cost to make all window elements equal (to median). Two heaps."""
    lines = input_data.split("\n")
    n, k = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))

    low = []   # max-heap (negated)
    high = []  # min-heap
    low_size = 0
    high_size = 0
    low_sum = 0
    high_sum = 0
    removed = defaultdict(int)

    def add(val):
        nonlocal low_size, high_size, low_sum, high_sum
        if low_size == 0 or val <= -low[0]:
            heappush(low, -val)
            low_size += 1
            low_sum += val
        else:
            heappush(high, val)
            high_size += 1
            high_sum += val

    def remove(val):
        nonlocal low_size, high_size, low_sum, high_sum
        removed[val] += 1
        if low and val <= -low[0]:
            low_size -= 1
            low_sum -= val
        else:
            high_size -= 1
            high_sum -= val

    def balance():
        nonlocal low_size, high_size, low_sum, high_sum
        while low_size > high_size + 1:
            val = -low[0]
            heappush(high, val)
            heappop(low)
            low_size -= 1
            high_size += 1
            low_sum -= val
            high_sum += val
            prune_top()
        while high_size > low_size:
            val = high[0]
            heappush(low, -val)
            heappop(high)
            high_size -= 1
            low_size += 1
            high_sum -= val
            low_sum += val
            prune_top()

    def prune_top():
        while low and removed[-low[0]] > 0:
            removed[-low[0]] -= 1
            heappop(low)
        while high and removed[high[0]] > 0:
            removed[high[0]] -= 1
            heappop(high)

    out = []
    for i in range(n):
        add(a[i])
        balance()
        prune_top()
        if i >= k:
            remove(a[i - k])
            balance()
            prune_top()
        if i >= k - 1:
            median = -low[0]
            # cost = sum |a[j] - median| for j in window
            # = median * low_size - low_sum + high_sum - median * high_size
            cost = median * low_size - low_sum + high_sum - median * high_size
            out.append(cost)
    return "\n".join(map(str, out))


SOLUTIONS = {
    3220: _solve_3220,
    3221: _solve_3221,
    3426: _solve_3426,
    3405: _solve_3405,
    3222: _solve_3222,
    3224: _solve_3224,
    3219: _solve_3219,
    1076: _solve_1076,
    1077: _solve_1077,
}
