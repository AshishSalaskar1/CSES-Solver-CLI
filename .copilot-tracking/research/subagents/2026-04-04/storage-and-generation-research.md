# Test Case Storage Formats & Generation Strategies for CSES CLI

**Research Status:** Complete
**Date:** 2026-04-04

## Research Questions

1. What storage format best balances compactness, git-friendliness, and read performance for ~258 problems × ~10 test cases?
2. How should test cases be generated for competitive programming problems when official test data is unavailable?
3. What is the realistic total size estimate for the test case dataset?

---

## Part 1: Storage Format Comparison

### Typical CSES Constraints (from problem pages)

| Category | Typical n | Typical Value Range | Example |
|---|---|---|---|
| Introductory | ≤10⁶ | ≤10⁶ - 10⁹ | Weird Algorithm: n ≤ 10⁶ |
| Array/Sorting | ≤2×10⁵ | ≤10⁹ | Maximum Subarray Sum |
| DP | ≤10⁶ | varies | Dice Combinations: n ≤ 10⁶ |
| Graph | ≤10³×10³ grid or n,m ≤ 10⁵ | - | Counting Rooms: 1000×1000 grid |
| Tree | ≤2×10⁵ | - | Standard tree problems |

### Test Case Size Profiles

Based on CSES constraint analysis:

- **Small cases** (50%): 10–100 bytes input. Single integers, small arrays (n ≤ 10), edge cases.
- **Medium cases** (40%): 100 bytes – 10 KB input. Arrays of 100–10,000 elements, small graphs.
- **Large-but-reasonable cases** (10%): 10 KB – 100 KB input. Arrays of ~50,000 elements, moderate graphs. NOT stress-test/max-constraint level.

Average test case size estimate (input + output):

- Small: ~50 bytes input + ~20 bytes output = ~70 bytes
- Medium: ~2 KB input + ~500 bytes output = ~2.5 KB
- Large: ~30 KB input + ~5 KB output = ~35 KB

### Option A: SQLite Database (Single File)

**Schema:**

```sql
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    cses_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER REFERENCES problems(id),
    case_number INTEGER NOT NULL,
    input TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    case_type TEXT DEFAULT 'generated',  -- 'edge', 'random', 'corner', 'stress'
    UNIQUE(problem_id, case_number)
);
```

**Pros:**

- Single file, trivially distributable.
- SQL queries enable flexible test case selection (by type, problem category, etc.).
- SQLite reads blobs ≤100 KB faster than filesystem reads (SQLite official benchmarks: 35% faster for 10 KB blobs).
- Atomic writes — no partial-update risk.
- 20% less disk space than equivalent flat files (no filesystem block padding).
- Excellent for programmatic access from CLI tool.

**Cons:**

- Binary file: git cannot produce meaningful diffs.
- Every change to any test case creates a full new binary snapshot in git history.
- No way for contributors to review test case changes in PRs.
- git clone size grows linearly with number of updates (each commit stores a new snapshot of the entire DB).

**Size Estimate:**

- Raw data: ~25 MB (see Part 3 calculations below).
- SQLite overhead: ~5–10% → ~27 MB.
- In git: grows by ~27 MB per significant update.

### Option B: Compressed JSON/MessagePack

**Sub-options:**

| Format | Human Readable | Size vs JSON | Ecosystem |
|---|---|---|---|
| JSON | Yes | 1.0x (baseline) | Universal |
| MessagePack | No | ~0.5-0.7x of JSON | Good, all major languages |
| CBOR | No | ~0.5-0.7x of JSON | Good, RFC standard |

**Compression ratios for numeric/text test data (typical CP data):**

CP test data is highly compressible (repetitive numeric patterns, newlines, spaces):

| Compression | Ratio (text data) | Speed |
|---|---|---|
| gzip -6 | ~5:1 to 8:1 | Moderate |
| zstd -3 | ~5:1 to 8:1 | 3-5x faster than gzip |
| zstd -19 | ~8:1 to 12:1 | Slow compression, fast decompression |

**Layout options:**

1. **One big file** (`test_cases.json.zst`): Simple, but no granular git diffs. Same problem as SQLite.
2. **One file per problem** (`1068.json.zst`): Better git behavior. Only changed problems create diffs. But 258 compressed files add overhead.
3. **One file per problem, uncompressed JSON**: Best git behavior (text diffs work). Larger size but still manageable.

**Pros:**

- MessagePack/CBOR: compact binary, fast serialization.
- Per-problem files give granular git diffs (for JSON).
- zstd compression yields excellent ratios (5-8x for numeric text).

**Cons:**

- Binary formats (MessagePack, CBOR) lose git diff capability.
- Compressed files are binary in git.
- JSON per-problem files are human-readable but larger.
- Requires deserialization library.

**Size Estimate (uncompressed JSON, per-problem files):**

- Raw test data: ~25 MB.
- JSON overhead (keys, brackets, quotes): ~30% → ~32 MB total.
- With gzip/zstd: ~4–6 MB total.

### Option C: Flat File Structure

Standard competitive programming judge format:

```
tests/
  1068/           # Weird Algorithm (by CSES task ID)
    1.in
    1.out
    2.in
    2.out
    ...
  1083/           # Missing Number
    1.in
    1.out
    ...
```

**Pros:**

- Industry standard format. Used by Codeforces/Polygon, DMOJ, Kattis, and virtually all CP judges.
- Perfect git behavior: text diffs work on every file. PRs clearly show what changed.
- Easy to inspect, debug, and manually edit test cases.
- No serialization/deserialization needed — just read files.
- Each test case is independently accessible.
- Partial updates only change affected files in git history.

**Cons:**

- Many small files: 258 problems × 10 cases × 2 files = ~5,160 files. Git handles this fine (Linux kernel has 70,000+ files).
- Filesystem block allocation wastes space for tiny files (4 KB block size means a 50-byte file uses 4 KB on disk). However, git pack files compress these efficiently.
- No metadata unless using a sidecar file (problem name, category, case type).
- Directory traversal needed to enumerate test cases.

**Size Estimate:**

- Raw data on disk: ~25 MB of actual content, but ~80-100 MB of allocated filesystem blocks (for thousands of tiny files).
- In git repository (packed): git uses zlib compression + delta encoding, so the packed repo would be **~4-8 MB**. This is the relevant metric since we distribute via git clone.
- git clone size stays small because text files delta-compress extremely well across versions.

### Option D: SQLite with zstd-Compressed BLOBs

**Schema:**

```sql
CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    case_number INTEGER NOT NULL,
    input_zstd BLOB NOT NULL,      -- zstd-compressed input
    output_zstd BLOB NOT NULL,     -- zstd-compressed output
    case_type TEXT DEFAULT 'generated',
    UNIQUE(problem_id, case_number)
);
```

**Pros:**

- Smallest possible single-file size.
- zstd dictionary mode could compress similar test cases very efficiently.
- Fast read with memory-mapped I/O.

**Cons:**

- All the git problems of Option A, compounded.
- Additional complexity: need zstd library at read time.
- Marginal size savings over plain SQLite (test case text is already small; SQLite pages already use zlib internally with some configurations).
- Over-engineered for the data sizes involved.

**Size Estimate:**

- ~3-5 MB for the database file.
- Same git behavior problems as Option A.

### Storage Format Comparison Matrix

| Criterion | A: SQLite | B: JSON/file | B: MsgPack | C: Flat Files | D: SQLite+zstd |
|---|---|---|---|---|---|
| Git diff support | None | Good (JSON) | None | Excellent | None |
| PR reviewability | None | Good (JSON) | None | Excellent | None |
| Git clone size | ~27 MB | ~32 MB / ~5 MB | ~18 MB | ~25 MB raw, **~5 MB packed** | ~4 MB |
| Git history growth | High (full file per commit) | Low (per-problem) | Medium | **Very low** (per-file deltas) | High |
| Read performance | Excellent | Good | Good | Good | Good |
| Write simplicity | Moderate (SQL) | Simple | Moderate | **Simplest** | Complex |
| Human inspectable | No (binary) | Yes (JSON) | No | **Yes** | No |
| Tooling required | sqlite3 | json lib | msgpack lib | **None (filesystem)** | sqlite3 + zstd |
| Industry standard | No | No | No | **Yes** | No |
| Metadata support | Built-in (SQL) | Built-in (JSON fields) | Built-in | Needs sidecar file | Built-in |

### Recommendation: Hybrid — Option C (Flat Files) + Metadata Sidecar

**Primary recommendation: Option C (Flat File Structure) with a JSON metadata index.**

```
testcases/
  index.json              # Problem metadata + test case metadata
  1068/                   # Weird Algorithm
    1.in
    1.out
    2.in
    2.out
    ...
    meta.json             # Per-problem: case types, descriptions
  1083/                   # Missing Number
    ...
```

**Rationale:**

1. **Git-friendliness is the decisive factor.** The test cases must be stored in a git repo, updated iteratively, and reviewed in PRs. Only flat files and uncompressed JSON provide meaningful diffs.
2. **Industry standard.** This is how Polygon, Codeforces, Kattis, DMOJ, and essentially all CP judges store test data. Any competitive programmer will recognize the format.
3. **Git pack compression is highly effective on text files.** The ~25 MB raw content compresses to ~5 MB in git pack files, comparable to explicitly compressed formats.
4. **Simplest implementation.** Reading a test case is just `open("testcases/1068/1.in").read()`. No libraries needed.
5. **Incremental updates are cheap.** Changing one test case only affects one file in git history.

The `meta.json` sidecar per problem handles metadata:

```json
{
  "cses_id": 1068,
  "name": "Weird Algorithm",
  "category": "Introductory Problems",
  "cases": [
    {"num": 1, "type": "edge", "desc": "n=1 (minimum)"},
    {"num": 2, "type": "edge", "desc": "n=2 (even minimum)"},
    {"num": 3, "type": "sample", "desc": "sample from problem (n=3)"},
    {"num": 4, "type": "random", "desc": "random small n"},
    {"num": 5, "type": "random", "desc": "random medium n"},
    {"num": 6, "type": "boundary", "desc": "n=1000000 (max constraint)"}
  ]
}
```

**Alternative consideration:** If repo size becomes an issue later, the flat files can always be gzipped per-problem as a post-step, or the repo could use GitHub Releases for the test data tarball. But for ~5 MB packed, this is not needed.

---

## Part 2: Test Case Generation Strategy

### Common Edge Cases for CP Problems

#### Universal edge cases (apply to almost all problems):

1. **Minimum input**: smallest valid n (usually 1).
2. **Maximum input**: largest valid n within reason (NOT stress-test level — cap at ~50,000 for arrays, ~500 for grids).
3. **Single element**: n=1 for array/sequence problems.
4. **Two elements**: n=2, exercises off-by-one errors.
5. **All same values**: array of identical elements.
6. **Sorted ascending / descending**: tests algorithms that degrade on sorted input.
7. **Alternating pattern**: e.g., [1, -1, 1, -1, ...].

#### Category-specific edge cases:

| Category | Key Edge Cases |
|---|---|
| **Introductory** | min/max values, powers of 2, boundary values, zero-result cases |
| **Array/Sorting** | sorted, reverse-sorted, all equal, single element, two elements, negative values, mix of pos/neg, duplicates |
| **Graph** | single node, disconnected graph, complete graph, tree (n-1 edges), cycle, self-loops (if allowed), bipartite/non-bipartite |
| **DP** | n=0 or n=1, all weights=0, exact capacity match, impossible cases |
| **Tree** | single node, chain (degenerate tree), star graph, balanced binary tree |
| **String** | empty (if allowed), single char, all same chars, palindrome, all distinct |
| **Math** | n=0, n=1, primes, powers of 2, large primes, modular arithmetic edge cases |
| **Geometry** | collinear points, duplicate points, single point, horizontal/vertical lines |

### Test Cases Per Problem Type

| Problem Category | Recommended Count | Breakdown |
|---|---|---|
| Introductory / simple I/O | 5–8 | 1 sample + 2-3 edge + 2-3 random |
| Array/Sorting | 8–12 | 1 sample + 3-4 edge + 3-4 random + 1-2 medium-large |
| Graph problems | 10–15 | 1 sample + 3-4 edge (graph structures) + 3-4 random + 2-3 medium-large |
| DP problems | 8–12 | 1 sample + 3-4 edge + 2-3 random + 1-2 medium |
| String problems | 8–12 | 1 sample + 3 edge (empty/single/same) + 3-4 random + 1-2 medium |
| Math problems | 6–10 | 1 sample + 3-4 edge (0,1,prime,power) + 2-3 random |
| Tree problems | 10–12 | 1 sample + 3-4 edge (chain/star/balanced) + 3-4 random + 1-2 medium |
| Geometry | 8–10 | 1 sample + 3-4 edge (collinear/duplicate) + 3-4 random |
| Interactive | 5–8 | Limited by nature; test basic protocol + edge cases |

**Average across all 258 problems: ~10 test cases per problem, ~2,580 total test cases.**

### Generation Approaches

#### Approach 1: Per-Problem Generator Specifications (Recommended)

Define a generator specification per problem in a structured format:

```python
# generators/1068_weird_algorithm.py
def generate_cases():
    cases = []
    # Edge cases
    cases.append({"input": "1\n", "type": "edge", "desc": "minimum n"})
    cases.append({"input": "2\n", "type": "edge", "desc": "even minimum"})
    cases.append({"input": "3\n", "type": "sample", "desc": "sample case"})

    # Random cases
    import random
    for i in range(3):
        n = random.randint(4, 1000)
        cases.append({"input": f"{n}\n", "type": "random", "desc": f"random n={n}"})

    # Boundary
    cases.append({"input": "999999\n", "type": "boundary", "desc": "near-max"})
    cases.append({"input": "1000000\n", "type": "boundary", "desc": "max constraint"})

    return cases
```

**Pros:** Reproducible, customizable, version-controlled generators.
**Cons:** Writing 258 generators is labor-intensive.

#### Approach 2: LLM-Assisted Generation (Practical for bulk)

Use an LLM (Copilot / GPT / Claude) to generate test case generators for each problem:

1. Feed the problem statement + constraints to the LLM.
2. Ask it to produce a Python generator script.
3. Review and validate the generator output.
4. Run the generator to produce test cases.
5. Validate outputs using a known-correct solution (brute force).

**Pros:** Dramatically reduces manual effort. LLMs understand CP problem patterns well.
**Cons:** Requires validation. LLMs may miss subtle edge cases. Need review per problem.

**This is the practical approach for 258 problems.** Manually writing all generators is infeasible; LLM-assisted generation with human review is the sweet spot.

#### Approach 3: Template-Based Generators

Create reusable generator templates by problem pattern:

```python
# templates/single_integer.py — for problems that take a single integer input
def generate(n_min, n_max, num_random=3):
    cases = [n_min, n_min+1, n_max, n_max-1]
    cases += [random.randint(n_min, n_max) for _ in range(num_random)]
    return cases

# templates/array_integer.py — for problems taking an array of integers
def generate(n_min, n_max, val_min, val_max, ...):
    ...
```

Templates for common input patterns:

| Template | Applies To | CSES Examples |
|---|---|---|
| Single integer | ~30 problems | Weird Algorithm, Trailing Zeros |
| Array of integers | ~60 problems | Maximum Subarray Sum, Distinct Numbers |
| Two integers + array | ~20 problems | Various DP/sorting problems |
| Grid (n×m) | ~15 problems | Counting Rooms, Grid Paths |
| Graph (n, m, edges) | ~40 problems | Building Roads, Shortest Routes |
| Tree (n, edges) | ~15 problems | Subordinates, Tree Diameter |
| String | ~15 problems | String Matching, Finding Borders |
| Multiple queries | ~20 problems | Range queries, various |
| Special format | ~43 problems | Problem-specific |

#### Approach 4: testlib.h Style (Reference, Not Recommended)

testlib.h (by Mike Mirzayanov, used by Codeforces/Polygon) is the gold standard for CP test generation in C++. It provides:

- Deterministic random generation with seed control.
- Validator framework for ensuring generated inputs are valid.
- Checker framework for comparing outputs.

However, testlib.h requires C++ compilation and is overkill for a Python-based CLI tool. The *patterns* from testlib are valuable:

- Seed-based reproducibility.
- Separate generator, validator, and checker per problem.
- Command-line parameters for test case variants.

**Recommendation: Adopt testlib patterns in Python generators**, not the C++ library itself.

#### Approach 5: Pre-generate All vs. Generate on Demand

| Aspect | Pre-generate All | Generate on Demand |
|---|---|---|
| Distribution | Ship with repo | Ship generators only |
| Repo size | ~5 MB (packed) | ~500 KB (generators only) |
| User experience | Instant test runs | First run has generation delay |
| Reproducibility | Exact same tests for everyone | Depends on seed control |
| Correctness | Validated once at generation time | Must validate at generation time |
| Offline use | Full offline support | Needs correct solution to generate outputs |

**Recommendation: Pre-generate all test cases and ship in the repo.**

- 5 MB is trivially small for a git repo.
- Consistent testing experience for all users (same test cases = same results).
- No need for users to have a correct solution to generate expected outputs.
- Generators can also be shipped for users who want to regenerate or add cases.

### Correctness Validation Strategy

This is the hardest part. Expected outputs must be correct.

#### Strategy 1: Known-Correct Reference Solutions

For each problem, maintain a verified-correct solution (brute force or known-correct implementation):

```
solutions/
  1068_weird_algorithm.py    # Reference solution
  1083_missing_number.py
  ...
```

Generation workflow:

1. Generator produces input files.
2. Reference solution processes each input, producing expected output.
3. Store both input and output.

**Challenge:** Need 258 correct solutions. This is the biggest bottleneck.

**Mitigation:** Many CSES solutions are available in public GitHub repos, editorials, and competitive programming resources. These can be verified against the CSES sample cases before using as reference solutions.

#### Strategy 2: Cross-Validation with Online Judge

Submit the reference solution to CSES itself to verify it passes all official test cases. Then trust its output for generated inputs.

**Limitation:** CSES has rate limits and requires an account. Not automatable at scale.

#### Strategy 3: Multi-Solution Cross-Check

Generate outputs from multiple independent solutions (e.g., Python brute force + C++ optimized). If they agree, the output is likely correct.

**Recommended Combined Strategy:**

1. Source or write reference solutions (LLM-assisted).
2. Verify each reference solution against the problem's sample case(s) from the CSES website.
3. Generate inputs using per-problem generators.
4. Run reference solution on generated inputs to produce expected outputs.
5. For problems with multiple valid outputs, note this in metadata and use checker functions instead of exact match.

---

## Part 3: Size Estimation

### Calculation

**Parameters:**

- 258 problems.
- Average 10 test cases per problem = 2,580 test cases.
- Distribution: 50% small, 40% medium, 10% large-but-reasonable.

**Per test case (input + output):**

| Size Class | % | Count | Avg Input | Avg Output | Avg Total | Subtotal |
|---|---|---|---|---|---|---|
| Small | 50% | 1,290 | 50 B | 20 B | 70 B | 88 KB |
| Medium | 40% | 1,032 | 2 KB | 500 B | 2.5 KB | 2.5 MB |
| Large | 10% | 258 | 30 KB | 5 KB | 35 KB | 8.8 MB |
| **Total** | | **2,580** | | | | **~11.4 MB** |

**Adding metadata files (~500 bytes each, per problem):**

- 258 × 500 B = ~126 KB. Negligible.

**Total raw data: ~11.5 MB**

### Storage Format Size Comparison

| Format | Raw on Disk | In Git (packed/cloned) | Notes |
|---|---|---|---|
| Flat files (Option C) | ~11.5 MB content, ~20-30 MB with FS block overhead | **~3-5 MB** | Git zlib + delta compression excels on text |
| SQLite (Option A) | ~12-13 MB | ~12-13 MB per version | Binary, no delta compression in git |
| JSON per-problem (Option B) | ~15 MB (JSON overhead) | ~4-6 MB | Text, good git compression |
| Compressed JSON (Option B+gzip) | ~2-3 MB | ~2-3 MB per version | Binary, no git deltas |
| SQLite + zstd (Option D) | ~2-3 MB | ~2-3 MB per version | Binary, no git deltas |

### Git Repository Impact

For Option C (flat files), conservative estimates:

- **Initial clone: ~5 MB.** Well within GitHub's norms.
- **After 10 updates touching 10% of cases each: ~6-7 MB.** Git delta compression handles text changes efficiently.
- **After 100 updates: ~15-20 MB.** Still very manageable.

For comparison: SQLite (Option A) after 10 full updates = ~130 MB clone. After 100 = ~1.3 GB. This is why flat files win for git repos.

### Conclusion on Size

**11.5 MB raw content / ~5 MB git-packed is entirely reasonable for 258 problems.** This is far smaller than most npm `node_modules`, smaller than a typical Docker image, and well within GitHub's recommendations (< 1 GB for repos, < 5 GB strongly recommended).

---

## Research Gaps & Follow-On Questions

1. **Multiple-valid-output problems**: Some CSES problems (e.g., construction problems, permutation problems) have multiple valid answers. These need checker functions rather than exact output matching. How many of the 258 problems have multiple valid outputs? (Estimated: ~30-50.)

2. **Interactive problems**: The CSES problem set includes ~6 interactive problems. These cannot use standard stdin/stdout test cases. They require a simulated interactor. Should these be excluded from the initial test case set?

3. **Reference solution sourcing**: Where to efficiently source 258 verified-correct solutions? Community repos (GitHub search for "cses solutions") could bootstrap this. Legal/licensing considerations for using community solutions as reference generators.

4. **Large output problems**: Some problems (e.g., Weird Algorithm with n=1,000,000) produce very large outputs (millions of numbers). Should output size be capped, or should these be included as-is? Recommendation: Include them; they compress well.

5. **Floating-point output**: Some problems (geometry, probability) produce floating-point outputs. These need approximate comparison (epsilon-based). The metadata should flag these.

6. **Seed control for reproducibility**: If generators use randomness, should seeds be fixed and recorded? (Yes — the generator should use a deterministic seed per problem so anyone can regenerate identical test cases.)
