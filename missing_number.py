# CSES 1083 - Missing Number
# Given n and n-1 distinct numbers from 1..n, find the missing one.

import sys

data = sys.stdin.read().split()
n = int(data[0])
nums = list(map(int, data[1:]))
print(n * (n + 1) // 2 - sum(nums))
