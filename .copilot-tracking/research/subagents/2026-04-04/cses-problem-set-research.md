# CSES Problem Set Research

## Research Topics

1. Complete list of categories, problem counts, and totals
2. In-scope categories (excluding Mathematics, String Algorithms, Geometry, Construction Problems, Additional Problems)
3. Problem I/O format analysis
4. Test case characteristics
5. Test case scraping/download availability

---

## 1. Problem Set Structure

**Source**: https://cses.fi/problemset/ and https://cses.fi/problemset/text/2433

The CSES Problem Set is maintained by Antti Laaksonen at the University of Helsinki. The introduction page states: "The current collection has **400 problems**."

### URL Pattern

- Problem list: `https://cses.fi/problemset/list`
- Individual problem task page: `https://cses.fi/problemset/task/{ID}`
- Problem statistics: `https://cses.fi/problemset/stats/{ID}`
- Introduction text: `https://cses.fi/problemset/text/2433`

### Problem ID Numbering Scheme

- IDs are **not sequential within categories** -- they are assigned globally across all CSES content (courses, contests, problem set).
- IDs are **not contiguous** -- there are gaps between consecutive problems.
- Observed range: **1068** (Weird Algorithm, first problem) to **3430** (Lines and Queries II).
- IDs appear to be auto-incrementing integers assigned when a problem is created on the CSES platform.
- Newer categories (Sliding Window, Interactive, Bitwise Operations, Counting Problems, Advanced Graph Problems) tend to have higher IDs (3100-3430 range).

### All Categories with Problem Counts

| # | Category | Problem Count |
|---|----------|--------------|
| 1 | Introductory Problems | 24 |
| 2 | Sorting and Searching | 35 |
| 3 | Dynamic Programming | 23 |
| 4 | Graph Algorithms | 36 |
| 5 | Range Queries | 25 |
| 6 | Tree Algorithms | 16 |
| 7 | Mathematics | 37 |
| 8 | String Algorithms | 21 |
| 9 | Geometry | 16 |
| 10 | Advanced Techniques | 25 |
| 11 | Sliding Window Problems | 11 |
| 12 | Interactive Problems | 6 |
| 13 | Bitwise Operations | 11 |
| 14 | Construction Problems | 8 |
| 15 | Advanced Graph Problems | 28 |
| 16 | Counting Problems | 18 |
| 17 | Additional Problems I | 30 |
| 18 | Additional Problems II | 30 |
| | **TOTAL** | **400** |

---

## 2. In-Scope Categories

**Excluded**: Mathematics (37), String Algorithms (21), Geometry (16), Construction Problems (8), Additional Problems I (30), Additional Problems II (30) = **142 excluded**.

**In-scope**: 400 - 142 = **258 problems** across **12 categories**.

| # | Category | Problem Count |
|---|----------|--------------|
| 1 | Introductory Problems | 24 |
| 2 | Sorting and Searching | 35 |
| 3 | Dynamic Programming | 23 |
| 4 | Graph Algorithms | 36 |
| 5 | Range Queries | 25 |
| 6 | Tree Algorithms | 16 |
| 7 | Advanced Techniques | 25 |
| 8 | Sliding Window Problems | 11 |
| 9 | Interactive Problems | 6 |
| 10 | Bitwise Operations | 11 |
| 11 | Advanced Graph Problems | 28 |
| 12 | Counting Problems | 18 |
| | **IN-SCOPE TOTAL** | **258** |

---

## 3. Problem I/O Format Analysis

### General I/O Model

From the Introduction page (https://cses.fi/problemset/text/2433):

> "In all problems you should read input from **standard input** and write output to **standard output**."

There is no file-based I/O. All problems use stdin/stdout exclusively.

### Problem Page Structure

Every problem page follows a consistent format with these sections:

1. **Title** -- problem name
2. **Metadata** -- Time limit (typically 1.00 s) and Memory limit (typically 512 MB)
3. **Problem statement** -- description of the task
4. **Input** -- describes the input format
5. **Output** -- describes the expected output format
6. **Constraints** -- bullet-pointed list of variable bounds
7. **Example** -- one example with labeled Input and Output blocks

### I/O Format Patterns Observed

#### Pattern A: Single Value In, Single/Multi Value Out (Simplest)

**Weird Algorithm (1068)** -- Introductory:

```text
Input:
3

Output:
3 10 5 16 8 4 2 1
```

- First line: single integer n
- Output: space-separated sequence on one line

**Repetitions (1069)** -- Introductory:

```text
Input:
ATTCGGGA

Output:
3
```

- First line: a string
- Output: single integer

#### Pattern B: Size Header + Array (Very Common)

**Increasing Array (1094)** -- Introductory:

```text
Input:
5
3 2 5 1 7

Output:
5
```

- First line: integer n (array size)
- Second line: n space-separated integers
- Output: single integer

#### Pattern C: Multiple Parameters + Queries (Range/Query Problems)

**Static Range Sum Queries (1646)** -- Range Queries:

```text
Input:
8 4
3 2 4 5 1 1 5 3
2 4
5 6
1 8
3 3

Output:
11
2
24
4
```

- First line: n and q (size and query count)
- Second line: array values
- Following q lines: query parameters
- Output: one result per query, each on its own line

#### Pattern D: Grid/Map Input

**Counting Rooms (1192)** -- Graph Algorithms:

```text
Input:
5 8
########
#..#...#
####.#.#
#..#...#
########

Output:
3
```

- First line: n and m (grid dimensions)
- Following n lines: grid rows as character strings
- Output: single integer

#### Pattern E: Interactive Problems

**Hidden Integer (3112)** -- Interactive Problems:

```text
? 3
YES
? 6
YES
? 7
NO
! 7
```

- No traditional input section
- Uses "Interaction" section instead of "Input/Output"
- Prints queries prefixed with `?`, reads responses
- Prints answer prefixed with `!`
- Must flush output after each line
- Has a query limit (e.g., 30 questions)

### Key I/O Conventions

- **Input delimiter**: values on the same line are space-separated
- **Line-per-result**: when multiple outputs are expected, each goes on its own line
- **1-indexed**: array/range indices in problems are typically 1-indexed
- **No trailing spaces required**: standard competitive programming conventions
- **No extra output**: only print what is asked for

---

## 4. Test Case Characteristics

### Typical Constraint Ranges

Based on analysis of multiple problems:

| Constraint Type | Typical Range | Examples |
|----------------|---------------|----------|
| Array size n | 1 to 2×10^5 | Increasing Array, Sorting problems |
| Grid size n×m | 1 to 1000 | Counting Rooms |
| Single integer n | 1 to 10^6 or 10^9 | Weird Algorithm, Hidden Integer |
| Value range x_i | 1 to 10^9 | Most problems |
| Query count q | 1 to 2×10^5 | Range query problems |
| String length | 1 to 10^6 | Repetitions |

### Test Case Types (General Competitive Programming Knowledge)

CSES problems typically include:

1. **Example test case** -- the one shown on the problem page (always the first test)
2. **Small edge cases** -- minimum values (n=1), boundary conditions
3. **Medium random cases** -- moderate-sized random inputs
4. **Large stress tests** -- inputs at or near the maximum constraint size (tests TLE for inefficient solutions)
5. **Special/corner cases** -- all same values, sorted input, reverse sorted, etc.
6. **Anti-hack cases** -- cases added through the "hacking" feature by other users

### Test Case Visibility

- **Test cases are HIDDEN** during solving -- you only see the example from the problem statement.
- **After solving**: the "hacking" feature becomes available (see section 5).
- **Submission verdict** shows per-test-case results: for each test case you see ACCEPTED or the failure type (WRONG ANSWER, TIME LIMIT EXCEEDED, etc.) but NOT the actual test data.
- **Time limit**: typically 1.00 s (sometimes 2.00 s for harder problems).
- **Memory limit**: typically 512 MB.

---

## 5. Test Case Scraping/Download Availability

### No Public API

CSES does **not** provide a public API for accessing problems, test cases, or submissions programmatically. All interaction is through the web interface or CLI tools that scrape the web interface.

### Hacking Feature (Post-Solve Access)

From the Introduction page:

> "After solving a problem, you can view the solutions by other users and try to hack them by giving a test case where the solution fails. Then, the new test case can be added to the test data and all submissions will be regraded."

This means:

- **After you solve a problem**, you gain access to other users' solutions.
- You can submit new test cases ("hacking") to break other solutions.
- Successful hack test cases get **added to the official test data**.
- However, this does NOT mean you can download the full test case set -- you can only submit new ones.

### Existing CLI Tools

#### Official: `csesfi/cses-cli` (Rust, MIT License)

- GitHub: https://github.com/csesfi/cses-cli
- Built by University of Helsinki students (Software Engineering Project, Summer 2021)
- 6 stars, actively maintained (last update 3 months ago, v0.1.4)
- **Key commands**:
  - `login` -- authenticate via browser link
  - `list -c <course>` -- list tasks in a course/contest
  - `view -t <task_id>` -- display problem statement
  - `submit <file> -t <task_id>` -- submit solution
  - `submissions -t <task_id>` -- list past submissions
  - `template -t <task_id>` -- download code template
  - **`examples -t <task_id>`** -- **downloads example inputs and outputs** (the ones shown on the problem page)
- Does NOT download hidden test cases
- Works with courses and contests, not just the problem set

#### Community: `ketankr9/cses-cli` (Go, Apache-2.0)

- GitHub: https://github.com/ketankr9/cses-cli
- 11 stars, last updated 5 years ago
- **Key commands**:
  - `login` -- authenticate with username/password
  - `list` -- list problems with solve status
  - `show <id>` -- display problem statement in terminal
  - `solve <id>` -- open editor with problem + code stub
  - `submit <file>` -- submit solution with auto GitHub commit
- Does NOT download test cases
- Supports C++, Java, Python, Node.js

#### Other Tools

- `MostafaGalal1/Secpar` (Python) -- scrapes code submissions (not test cases) from Codeforces, CSES, and Vjudge into a GitHub repo.
- `RealA10N/cptk` -- competitive programming toolkit supporting CSES among others.

### Known Test Case Repositories

**No public repository containing CSES test cases was found.** GitHub searches for "CSES test cases", "CSES test data", and "CSES testcases" returned zero relevant repositories.

Multiple solution repositories exist (e.g., `mrsac7/CSES-Solutions` with 406 stars) but these contain only solution code, not test data.

### Summary: Test Case Accessibility

| Method | Available? | Details |
|--------|-----------|---------|
| Public API | No | CSES has no API |
| Download test cases | No | Test data is hidden |
| Example I/O from problem page | Yes | 1 example per problem, scrapable from HTML |
| Example I/O via CLI | Yes | `csesfi/cses-cli examples` command |
| Full test data after solving | No | Only hacking (submitting new tests) is available |
| Third-party test case repos | No | None found |
| Generate test cases locally | Possible | Would need custom generators per problem |

---

## 6. Complete In-Scope Problem Listing

### Introductory Problems (24)

| ID | Problem Name |
|----|-------------|
| 1068 | Weird Algorithm |
| 1083 | Missing Number |
| 1069 | Repetitions |
| 1094 | Increasing Array |
| 1070 | Permutations |
| 1071 | Number Spiral |
| 1072 | Two Knights |
| 1092 | Two Sets |
| 1617 | Bit Strings |
| 1618 | Trailing Zeros |
| 1754 | Coin Piles |
| 1755 | Palindrome Reorder |
| 2205 | Gray Code |
| 2165 | Tower of Hanoi |
| 1622 | Creating Strings |
| 1623 | Apple Division |
| 1624 | Chessboard and Queens |
| 3399 | Raab Game I |
| 3419 | Mex Grid Construction |
| 3217 | Knight Moves Grid |
| 3311 | Grid Coloring I |
| 2431 | Digit Queries |
| 1743 | String Reorder |
| 1625 | Grid Path Description |

### Sorting and Searching (35)

| ID | Problem Name |
|----|-------------|
| 1621 | Distinct Numbers |
| 1084 | Apartments |
| 1090 | Ferris Wheel |
| 1091 | Concert Tickets |
| 1619 | Restaurant Customers |
| 1629 | Movie Festival |
| 1640 | Sum of Two Values |
| 1643 | Maximum Subarray Sum |
| 1074 | Stick Lengths |
| 2183 | Missing Coin Sum |
| 2216 | Collecting Numbers |
| 2217 | Collecting Numbers II |
| 1141 | Playlist |
| 1073 | Towers |
| 1163 | Traffic Lights |
| 3420 | Distinct Values Subarrays |
| 3421 | Distinct Values Subsequences |
| 2162 | Josephus Problem I |
| 2163 | Josephus Problem II |
| 2168 | Nested Ranges Check |
| 2169 | Nested Ranges Count |
| 1164 | Room Allocation |
| 1620 | Factory Machines |
| 1630 | Tasks and Deadlines |
| 1631 | Reading Books |
| 1641 | Sum of Three Values |
| 1642 | Sum of Four Values |
| 1645 | Nearest Smaller Values |
| 1660 | Subarray Sums I |
| 1661 | Subarray Sums II |
| 1662 | Subarray Divisibility |
| 2428 | Distinct Values Subarrays II |
| 1085 | Array Division |
| 1632 | Movie Festival II |
| 1644 | Maximum Subarray Sum II |

### Dynamic Programming (23)

| ID | Problem Name |
|----|-------------|
| 1633 | Dice Combinations |
| 1634 | Minimizing Coins |
| 1635 | Coin Combinations I |
| 1636 | Coin Combinations II |
| 1637 | Removing Digits |
| 1638 | Grid Paths I |
| 1158 | Book Shop |
| 1746 | Array Description |
| 2413 | Counting Towers |
| 1639 | Edit Distance |
| 3403 | Longest Common Subsequence |
| 1744 | Rectangle Cutting |
| 3359 | Minimal Grid Path |
| 1745 | Money Sums |
| 1097 | Removal Game |
| 1093 | Two Sets II |
| 3314 | Mountain Range |
| 1145 | Increasing Subsequence |
| 1140 | Projects |
| 1653 | Elevator Rides |
| 2181 | Counting Tilings |
| 2220 | Counting Numbers |
| 1748 | Increasing Subsequence II |

### Graph Algorithms (36)

| ID | Problem Name |
|----|-------------|
| 1192 | Counting Rooms |
| 1193 | Labyrinth |
| 1666 | Building Roads |
| 1667 | Message Route |
| 1668 | Building Teams |
| 1669 | Round Trip |
| 1194 | Monsters |
| 1671 | Shortest Routes I |
| 1672 | Shortest Routes II |
| 1673 | High Score |
| 1195 | Flight Discount |
| 1197 | Cycle Finding |
| 1196 | Flight Routes |
| 1678 | Round Trip II |
| 1679 | Course Schedule |
| 1680 | Longest Flight Route |
| 1681 | Game Routes |
| 1202 | Investigation |
| 1750 | Planets Queries I |
| 1160 | Planets Queries II |
| 1751 | Planets Cycles |
| 1675 | Road Reparation |
| 1676 | Road Construction |
| 1682 | Flight Routes Check |
| 1683 | Planets and Kingdoms |
| 1684 | Giant Pizza |
| 1686 | Coin Collector |
| 1691 | Mail Delivery |
| 1692 | De Bruijn Sequence |
| 1693 | Teleporters Path |
| 1690 | Hamiltonian Flights |
| 1689 | Knight's Tour |
| 1694 | Download Speed |
| 1695 | Police Chase |
| 1696 | School Dance |
| 1711 | Distinct Routes |

### Range Queries (25)

| ID | Problem Name |
|----|-------------|
| 1646 | Static Range Sum Queries |
| 1647 | Static Range Minimum Queries |
| 1648 | Dynamic Range Sum Queries |
| 1649 | Dynamic Range Minimum Queries |
| 1650 | Range Xor Queries |
| 1651 | Range Update Queries |
| 1652 | Forest Queries |
| 1143 | Hotel Queries |
| 1749 | List Removals |
| 1144 | Salary Queries |
| 2166 | Prefix Sum Queries |
| 2206 | Pizzeria Queries |
| 3304 | Visible Buildings Queries |
| 3163 | Range Interval Queries |
| 1190 | Subarray Sum Queries |
| 3226 | Subarray Sum Queries II |
| 1734 | Distinct Values Queries |
| 3356 | Distinct Values Queries II |
| 2416 | Increasing Array Queries |
| 1664 | Movie Festival Queries |
| 1739 | Forest Queries II |
| 1735 | Range Updates and Sums |
| 1736 | Polynomial Queries |
| 1737 | Range Queries and Copies |
| 2184 | Missing Coin Sum Queries |

### Tree Algorithms (16)

| ID | Problem Name |
|----|-------------|
| 1674 | Subordinates |
| 1130 | Tree Matching |
| 1131 | Tree Diameter |
| 1132 | Tree Distances I |
| 1133 | Tree Distances II |
| 1687 | Company Queries I |
| 1688 | Company Queries II |
| 1135 | Distance Queries |
| 1136 | Counting Paths |
| 1137 | Subtree Queries |
| 1138 | Path Queries |
| 2134 | Path Queries II |
| 1139 | Distinct Colors |
| 2079 | Finding a Centroid |
| 2080 | Fixed-Length Paths I |
| 2081 | Fixed-Length Paths II |

### Advanced Techniques (25)

| ID | Problem Name |
|----|-------------|
| 1628 | Meet in the Middle |
| 2136 | Hamming Distance |
| 3360 | Corner Subgrid Check |
| 2137 | Corner Subgrid Count |
| 2138 | Reachable Nodes |
| 2143 | Reachability Queries |
| 2072 | Cut and Paste |
| 2073 | Substring Reversals |
| 2074 | Reversals and Sums |
| 2076 | Necessary Roads |
| 2077 | Necessary Cities |
| 2078 | Eulerian Subgraphs |
| 2084 | Monster Game I |
| 2085 | Monster Game II |
| 2086 | Subarray Squares |
| 2087 | Houses and Schools |
| 2088 | Knuth Division |
| 2111 | Apples and Bananas |
| 2112 | One Bit Positions |
| 2113 | Signal Processing |
| 2101 | New Roads Queries |
| 2133 | Dynamic Connectivity |
| 2121 | Parcel Delivery |
| 2129 | Task Assignment |
| 2130 | Distinct Routes II |

### Sliding Window Problems (11)

| ID | Problem Name |
|----|-------------|
| 3220 | Sliding Window Sum |
| 3221 | Sliding Window Minimum |
| 3426 | Sliding Window Xor |
| 3405 | Sliding Window Or |
| 3222 | Sliding Window Distinct Values |
| 3224 | Sliding Window Mode |
| 3219 | Sliding Window Mex |
| 1076 | Sliding Window Median |
| 1077 | Sliding Window Cost |
| 3223 | Sliding Window Inversions |
| 3227 | Sliding Window Advertisement |

### Interactive Problems (6)

| ID | Problem Name |
|----|-------------|
| 3112 | Hidden Integer |
| 3139 | Hidden Permutation |
| 3305 | K-th Highest Score |
| 3228 | Permuted Binary Strings |
| 3273 | Colored Chairs |
| 3140 | Inversion Sorting |

### Bitwise Operations (11)

| ID | Problem Name |
|----|-------------|
| 1146 | Counting Bits |
| 1655 | Maximum Xor Subarray |
| 3191 | Maximum Xor Subset |
| 3211 | Number of Subset Xors |
| 3192 | K Subset Xors |
| 3233 | All Subarray Xors |
| 2419 | Xor Pyramid Peak |
| 3194 | Xor Pyramid Diagonal |
| 3195 | Xor Pyramid Row |
| 1654 | SOS Bit Problem |
| 3141 | And Subset Count |

### Advanced Graph Problems (28)

| ID | Problem Name |
|----|-------------|
| 3303 | Nearest Shops |
| 1134 | Prüfer Code |
| 1702 | Tree Traversals |
| 1757 | Course Schedule II |
| 1756 | Acyclic Graph Edges |
| 2177 | Strongly Connected Edges |
| 2179 | Even Outdegree Edges |
| 1707 | Graph Girth |
| 3357 | Fixed Length Walk Queries |
| 3111 | Transfer Speeds Sum |
| 3407 | MST Edge Check |
| 3408 | MST Edge Set Check |
| 3409 | MST Edge Cost |
| 1677 | Network Breakdown |
| 3114 | Tree Coin Collecting I |
| 3149 | Tree Coin Collecting II |
| 1700 | Tree Isomorphism I |
| 1701 | Tree Isomorphism II |
| 1699 | Flight Route Requests |
| 1703 | Critical Cities |
| 1203 | Visiting Cities |
| 3308 | Graph Coloring |
| 3158 | Bus Companies |
| 3358 | Split into Two Paths |
| 1704 | Network Renovation |
| 1705 | Forbidden Cities |
| 1752 | Creating Offices |
| 1685 | New Flight Routes |

### Counting Problems (18)

| ID | Problem Name |
|----|-------------|
| 3413 | Filled Subgrid Count I |
| 3414 | Filled Subgrid Count II |
| 3415 | All Letter Subgrid Count I |
| 3416 | All Letter Subgrid Count II |
| 3417 | Border Subgrid Count I |
| 3418 | Border Subgrid Count II |
| 3400 | Raab Game II |
| 1080 | Empty String |
| 2229 | Permutation Inversions |
| 2176 | Counting Bishops |
| 2228 | Counting Sequences |
| 1078 | Grid Paths II |
| 1075 | Counting Permutations |
| 2429 | Grid Completion |
| 2421 | Counting Reorders |
| 3232 | Tournament Graph Distribution |
| 3157 | Collecting Numbers Distribution |
| 2415 | Functional Graph Distribution |

---

## 7. Supported Languages

From https://cses.fi/howto/:

| Language | Compiler/Runtime | Flags/Options |
|----------|-----------------|---------------|
| C | gcc 13.3.0 | -std=c99 -O2 -Wall |
| C++ | g++ 13.3.0 | -std=c++11/17/20 -O2 -Wall |
| Java | Java 11.0.29 | -- |
| Python2 | CPython 2.7.18 / PyPy 2.7.18 | -- |
| Python3 | CPython 3.12.3 / PyPy 3.9.18 | -- |
| Rust | rustc 1.75.0 | --edition=2018/2021 -C opt-level=3 |
| Haskell | GHC 9.2.8 | -O2 -Wall |
| Node.js | Node.js 18.19.1 | -- |
| Pascal | FPC 3.2.2 | -O2 |
| Ruby | ruby 3.2.3 | -- |
| Scala | Scala 2.11.12 | -- |
| Assembly | NASM 2.16.01 | -- |

Source code size limit: 128 kB.

---

## 8. References

- CSES Problem Set main page: https://cses.fi/problemset/
- CSES Introduction: https://cses.fi/problemset/text/2433
- CSES How To (languages): https://cses.fi/howto/
- Official CLI: https://github.com/csesfi/cses-cli (Rust, MIT, UHelsinki)
- Community CLI: https://github.com/ketankr9/cses-cli (Go, Apache-2.0)
- Top solutions repo: https://github.com/mrsac7/CSES-Solutions (406 stars)
- License: Creative Commons BY-NC-SA 4.0
