---
title: "Birthday Attacks on Hash Functions"
description: "Derive birthday collision probabilities, understand the square-root security bound, and reproduce collision experiments without confusing collision resistance with preimage resistance."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
  - "Mathematical Foundations"
tags:
  - "birthday-bound"
  - "collisions"
  - "probability"
  - "hash-functions"
difficulty: "Intermediate"
series: "Hash Functions & MACs"
seriesOrder: 3
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. Why the paradox is relevant

In a group of people, “someone shares *your* birthday” is a fixed-target event. “Some pair shares a birthday” lets every pair become a candidate match. The second event grows much faster because (q) samples create (q(q-1)/2) pairs.

Hash cryptanalysis has the same distinction:

- **Preimage/second-preimage style:** match one prescribed (n)-bit digest; generic work is about (2^n).
- **Collision style:** find any two messages with the same digest; generic work is about (2^{n/2}).

This is not a contradiction. The collision attacker receives far more freedom in selecting a successful pair.

## 2. Exact probability

Sample (q) values independently and uniformly with replacement from a set of size (N). For (0\le q\le N), the probability that all values are distinct is

\[
\Pr[\text{no collision}]
=\frac{N}{N}\frac{N-1}{N}\frac{N-2}{N}\cdots\frac{N-q+1}{N}
=\prod_{i=0}^{q-1}\left(1-\frac{i}{N}\right).
\]

Therefore,

\[
\Pr[\text{at least one collision}]
=1-\prod_{i=0}^{q-1}\left(1-\frac{i}{N}\right).
\]

If (q>N), the probability is exactly one by the pigeonhole principle.

For birthdays, (N=365) when leap days and seasonal effects are ignored. At (q=23), the idealized probability is just over (50\%\). The assumptions are imperfect for human birthdays but accurately model an ideal uniform hash output.

## 3. The approximation and its range

For (q\ll N), use (\ln(1-x)\approx-x):

\[
\begin{aligned}
\ln\Pr[\text{no collision}]
&=\sum_{i=0}^{q-1}\ln\left(1-\frac{i}{N}\right)\\
&\approx-\sum_{i=0}^{q-1}\frac{i}{N}
=-\frac{q(q-1)}{2N}.
\end{aligned}
\]

Exponentiating gives

\[
\Pr[\text{collision}]\approx
1-\exp\left(-\frac{q(q-1)}{2N}\right).
\]

The approximation explains the square root. To reach a target probability (p), solve

\[
q\approx\sqrt{2N\ln\frac{1}{1-p}}.
\]

For (p=1/2),

\[
q_{50}\approx\sqrt{2N\ln2}\approx1.1774\sqrt N.
\]

Three constants should not be confused:

| Quantity | Approximate number of samples |
|---|---:|
| Collision probability at (q=\sqrt N) | (1-e^{-1/2}\approx39.3\%\) |
| (50\%\) collision probability | (1.1774\sqrt N) |
| Expected samples until first collision | (\sqrt{\pi N/2}\approx1.2533\sqrt N) |

For an (n)-bit hash, (N=2^n), so all three scale as (2^{n/2}).

## 4. Expected number of colliding pairs

Let (I_{ij}) indicate whether samples (i) and (j) match. Each pair matches with probability (1/N). Linearity of expectation gives

\[
\mathbb E\left[\sum_{i<j}I_{ij}\right]
=\binom q2\frac1N
=\frac{q(q-1)}{2N}.
\]

When this expected count is small, it is also close to the collision probability. When it becomes large, it is no longer itself a probability and can exceed one; the exponential expression is the better approximation for “at least one.”

## 5. The correct collision algorithm

A basic birthday attack stores the first message observed for each digest:

```text
seen = empty map
for each candidate message m:
    y = truncated_hash(m)
    if y is already in seen and seen[y] != m:
        return seen[y], m
    seen[y] = m
```

This costs (O(2^{n/2})) expected hash evaluations and memory entries for an ideal (n)-bit digest.

By contrast, this tempting experiment is **not** a birthday-table attack:

```text
repeat:
    choose fresh m1 and m2
    test whether H(m1) == H(m2)
```

Each isolated pair matches with probability (2^{-n}), so the expected work is (2^n). Creating many candidate values only helps when the algorithm compares them across trials, either by storing them, sorting them, or using a memory-reducing collision-search method.

## 6. Time, memory, and parallelism

- A hash table gives simple (O(q)) expected lookup time and (O(q)) storage.
- Sorting (q) `(digest, message)` pairs replaces hash-table lookup with (O(q\log q)) sorting and sequential comparison.
- Pollard-rho-style methods can reduce memory dramatically for suitable iteration functions, while retaining square-root-scale time under ideal assumptions.
- Parallel machines reduce wall-clock time, but total work and coordination still matter. Security strength is not measured only by the number of sequential loop iterations in one script.
- Multi-target and multi-user settings create more opportunities. A system-wide bound should count all relevant outputs and attacker queries, not just one object in isolation.

## 7. Truncation examples

For an ideal (n)-bit output, the approximate samples needed for a (50\%\) collision chance are:

| Output (n) | (q_{50}\approx1.1774\cdot2^{n/2}) | Interpretation |
|---:|---:|---|
| 16 | (3.01\times10^2) | Classroom demonstration |
| 32 | (7.72\times10^4) | Easy on ordinary hardware |
| 64 | (5.06\times10^9) | Substantial but not a modern collision-security level |
| 128 | (2.17\times10^{19}) | About 64 bits of collision strength |
| 256 | (4.01\times10^{38}) | About 128 bits of collision strength |

These values assume an ideal output. A structural attack may do better; environmental constraints may make even the generic number impractical.

## 8. Reproducible Python lab

Run:

```bash
python code/birthday_collision.py
```

The implementation in [`birthday_collision.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/birthday_collision.py):

- keeps the leftmost (n) bits without losing leading zeroes;
- uses counter-encoded messages, so the first collision is reproducible;
- stores digest-to-message mappings, implementing the actual birthday attack;
- computes exact probabilities with `log1p`/`expm1` to improve numerical stability;
- includes the exact (q(q-1)) factor in the approximation;
- limits demonstrations to at most 24 output bits to prevent accidental long runs.

Example output for 16 bits:

```text
16-bit collision after 311 evaluations
m1 = 0000000000000128
m2 = 0000000000000136
digest = bb58
approximate samples for 50% probability: 301.4
```

One deterministic run need not stop exactly at the expectation. Probability statements describe the distribution across experiments.

## 9. What a birthday attack does not prove

- It does not invert a prescribed full digest.
- A toy collision in 16 truncated bits is not a collision in full SHA-256.
- It does not give meaningful semantic control over both colliding messages; practical exploitability may require chosen-prefix or format-aware techniques.
- It does not by itself forge HMAC. MAC security depends on the keyed construction, tag length, queries, and underlying assumptions.

## 10. Design consequences

1. If (s) bits of classical collision security are required, an idealized digest generally needs at least (2s) output bits.
2. Do not truncate identifiers or commitment hashes without analyzing system-wide collision risk.
3. Do not treat randomly generated identifiers and adversarially chosen hash outputs as identical threat models.
4. Count the lifetime number of records and users when bounding accidental collisions.
5. Use an authentication primitive when an active attacker can change both a message and its digest.

Previous: [Hash Security Properties](/blog/hash-security-properties/).

Next: [Merkle–Damgård and SHA-256](/blog/merkle-damgard-sha256/).
