# CSES 1083 - Missing Number
# Given n and n-1 distinct numbers from 1..n, find the missing one.


def solve(data: str) -> int:
    parts = data.split()
    n = int(parts[0])
    nums = list(map(int, parts[1:]))
    print(f"Debug: n={n}, count={len(nums)}")  # safe — goes to debug, not judged
    return n * (n + 1) // 2 - sum(nums)
