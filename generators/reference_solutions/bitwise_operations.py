"""Reference solutions for CSES Bitwise Operations problems."""

from __future__ import annotations


def solve(task_id: int, input_data: str) -> str | None:
    """Dispatch to the correct solver by task_id."""
    fn = SOLUTIONS.get(task_id)
    if fn is None:
        return None
    return fn(input_data)


# ---------------------------------------------------------------------------
# 1146 - Counting Bits
# ---------------------------------------------------------------------------
def _solve_1146(input_data: str) -> str:
    n = int(input_data.strip())
    # Count total 1-bits in 0, 1, 2, ..., n
    def count_bits_up_to(x):
        if x < 0:
            return 0
        total = 0
        # For each bit position b (0-indexed from LSB)
        # Full cycles of length 2^(b+1): each contributes 2^b ones
        # Plus remainder
        for b in range(64):
            if (1 << b) > x:
                break
            cycle = 1 << (b + 1)
            full_cycles = (x + 1) // cycle
            total += full_cycles * (1 << b)
            remainder = (x + 1) % cycle
            total += max(0, remainder - (1 << b))
        return total
    return str(count_bits_up_to(n))


# ---------------------------------------------------------------------------
# 1655 - Maximum Xor Subarray
# ---------------------------------------------------------------------------
def _solve_1655(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))

    # Build trie of prefix XORs, find max XOR pair
    class TrieNode:
        __slots__ = ['children']
        def __init__(self):
            self.children = [None, None]

    root = TrieNode()
    BITS = 30  # values up to 10^9 ~ 2^30

    def insert(val):
        node = root
        for i in range(BITS, -1, -1):
            bit = (val >> i) & 1
            if node.children[bit] is None:
                node.children[bit] = TrieNode()
            node = node.children[bit]

    def query(val):
        node = root
        result = 0
        for i in range(BITS, -1, -1):
            bit = (val >> i) & 1
            want = 1 - bit
            if node.children[want] is not None:
                result |= (1 << i)
                node = node.children[want]
            elif node.children[bit] is not None:
                node = node.children[bit]
            else:
                break
        return result

    prefix_xor = 0
    insert(0)
    ans = 0
    for v in a:
        prefix_xor ^= v
        ans = max(ans, query(prefix_xor))
        insert(prefix_xor)
    return str(ans)


# ---------------------------------------------------------------------------
# 3191 - Maximum Xor Subset
# ---------------------------------------------------------------------------
def _solve_3191(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    # Gaussian elimination to find max XOR of any subset
    basis = []
    for v in a:
        cur = v
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur > 0:
            basis.append(cur)
            # Keep basis sorted for greedy
            basis.sort(reverse=True)
    # Greedily compute max XOR
    result = 0
    for b in basis:
        result = max(result, result ^ b)
    return str(result)


# ---------------------------------------------------------------------------
# 3211 - Number of Subset Xors
# ---------------------------------------------------------------------------
def _solve_3211(input_data: str) -> str:
    lines = input_data.split("\n")
    n = int(lines[0])
    a = list(map(int, lines[1].split()))
    # Gaussian elimination: rank r => answer = 2^(n-r)
    basis = []
    for v in a:
        cur = v
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur > 0:
            basis.append(cur)
            basis.sort(reverse=True)
    r = len(basis)
    return str(1 << (n - r))


# ---------------------------------------------------------------------------
# 2419 - Xor Pyramid Peak
# ---------------------------------------------------------------------------
def _solve_2419(input_data: str) -> str:
    n = int(input_data.split("\n")[0])
    a = list(map(int, input_data.split("\n")[1].split()))
    # The top of the XOR pyramid: result = XOR of a[i] where C(n-1, i) is odd.
    # C(n-1, i) mod 2 is 1 iff (i & (n-1)) == i (Lucas' theorem).
    result = 0
    mask = n - 1
    for i in range(n):
        if (i & mask) == i:
            result ^= a[i]
    return str(result)


# ---------------------------------------------------------------------------
# 1654 - SOS Bit Problem (Sum over Subsets)
# ---------------------------------------------------------------------------
def _solve_1654(input_data: str) -> str:
    n = int(input_data.split("\n")[0])
    a = list(map(int, input_data.split("\n")[1].split()))
    # For each mask x, compute sum of a[s] for all s that are submasks of x.
    # Standard SOS DP in O(n * 2^n)... but here n can be up to 20.
    # a has 2^n values indexed 0..2^(n)-1
    dp = a[:]
    for i in range(n):
        for mask in range(1 << n):
            if mask & (1 << i):
                dp[mask] += dp[mask ^ (1 << i)]
    return "\n".join(map(str, dp))


# ---------------------------------------------------------------------------
# 3192 - K Subset Xors (k-th smallest XOR value)
# ---------------------------------------------------------------------------
def _solve_3192(input_data: str) -> str:
    lines = input_data.split("\n")
    first = lines[0].split()
    n, q = int(first[0]), int(first[1])
    a = list(map(int, lines[1].split()))

    # Gaussian elimination to get reduced basis
    BITS = 30
    basis = [0] * (BITS + 1)
    rank = 0
    for v in a:
        cur = v
        for i in range(BITS, -1, -1):
            if not (cur >> i & 1):
                continue
            if basis[i]:
                cur ^= basis[i]
            else:
                basis[i] = cur
                rank += 1
                break

    # Reduce basis to make it "canonical" (each basis vector has unique leading bit,
    # and all other basis vectors have 0 in that position)
    for i in range(BITS + 1):
        for j in range(i + 1, BITS + 1):
            if basis[j] >> i & 1:
                basis[j] ^= basis[i]

    # Collect non-zero basis elements sorted by bit position
    b = []
    for i in range(BITS + 1):
        if basis[i]:
            b.append(basis[i])

    # Number of distinct XOR values = 2^rank
    # If 0 is achievable (i.e., rank < n, there are linearly dependent elements),
    # then 0 is included, and k-th (1-indexed) maps directly.
    # If 0 is NOT achievable (rank == n, all independent), then k=1 maps to 0? No.
    # Actually: the set of achievable XOR values has size 2^rank.
    # 0 is always achievable (empty subset). Wait — but the problem says "subsets"
    # which may or may not include the empty subset.
    # Let me re-read: "k-th smallest XOR value achievable by some subset"
    # Empty subset gives 0, so 0 is always achievable.
    # But wait, if rank < n, the number of subsets giving each XOR value is 2^(n-rank).
    # The number of distinct XOR values is 2^rank.
    # With the reduced basis, k-th smallest (1-indexed, k=1 → 0) can be found
    # by treating k-1 in binary and XOR-ing corresponding basis elements.

    has_zero = (rank < n)  # multiple subsets map to 0 (including empty)
    # Actually 0 is always achievable via empty subset.
    # The question is whether to count it as the first value.

    out = []
    for qi in range(q):
        k = int(lines[2 + qi])
        # If rank < n, then 0 is achievable and is the 1st value
        # Total distinct values = 2^rank
        # k=1 → 0, k=2 → smallest non-zero, etc.
        # If rank == n, 0 is still achievable (empty subset), same thing.
        # So always: k=1 → 0.
        total = 1 << rank
        if k > total:
            out.append("-1")
            continue
        # k-1 in binary selects which basis elements to XOR
        idx = k - 1
        val = 0
        for j in range(len(b)):
            if idx >> j & 1:
                val ^= b[j]
        out.append(str(val))
    return "\n".join(out)


SOLUTIONS = {
    1146: _solve_1146,
    1655: _solve_1655,
    3191: _solve_3191,
    3211: _solve_3211,
    2419: _solve_2419,
    1654: _solve_1654,
    3192: _solve_3192,
}
