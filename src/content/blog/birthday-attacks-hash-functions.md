---
title: "Birthday Attacks on Hash Functions"
description: "Derive exact and approximate collision probabilities, understand the square-root security bound, analyze time-memory tradeoffs and truncation risk, and reproduce collision experiments without confusing collisions with preimages."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
  - "Mathematical Foundations"
tags:
  - "birthday-bound"
  - "collisions"
  - "probability"
  - "hash-functions"
  - "truncation"
  - "generic-attacks"
difficulty: "Intermediate"
series: "Hash Functions & MACs"
seriesOrder: 3
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [Why the Birthday Bound Matters](#why-the-birthday-bound-matters)
- [Exact Collision Probability and Its Approximations](#exact-collision-probability-and-its-approximations)
- [\[
\ln
\Pr\[\text${no collision}\]
\approx](#lnprtextno-collisionapprox)
- [\[
\ln
\Pr\[\text${no collision}\]
\approx](#lnprtextno-collisionapprox-1)
- [From Probability to a Generic Collision Attack](#from-probability-to-a-generic-collision-attack)
- [Truncation, Multi-Target Settings, and System-Wide Risk](#truncation-multi-target-settings-and-system-wide-risk)
- [Reproducible Python Laboratory](#reproducible-python-laboratory)
- [What a Birthday Attack Does and Does Not Prove](#what-a-birthday-attack-does-and-does-not-prove)
- [Design Consequences and Conclusion](#design-consequences-and-conclusion)
- [References](#references)

---

## Why the Birthday Bound Matters

The birthday paradox is one of the most important probability effects in cryptography because it explains why **collision resistance is fundamentally weaker than preimage resistance for the same digest length**.

The classical birthday question is not:

> What is the probability that someone in the room shares *my* birthday?

That is a fixed-target problem.

The birthday question is:

> What is the probability that *some pair* of people in the room shares a birthday?

Every new person can match every previous person, so the number of candidate pairs grows quadratically.

With \(q\) people, the number of unordered pairs is

\[
\binom{q}{2}
=
\frac{q(q-1)}{2}.
\]

Hash collisions behave the same way.

For an \(n\)-bit digest, there are

\[
N=2^n
\]

possible outputs.

A preimage attacker must hit one prescribed digest:

\[
H(x)=y.
\]

A collision attacker may accept **any** pair

\[
x\neq x'
\]

for which

\[
H(x)=H(x').
\]

That additional freedom changes the generic work factor from approximately

\[
2^n
\]

to approximately

\[
2^{n/2}.
\]

This is the origin of the familiar statement:

\[
\boxed{
n\text{-bit hash}
\;\Rightarrow\;
\text{about }n/2\text{ bits of generic collision security}
}
\]

provided the hash behaves ideally and no structural cryptanalysis does better.

### Fixed target versus any pair

The distinction can be visualized as two search problems.

**Fixed target:**

```text
target digest y
      ^
      |
H(m1), H(m2), H(m3), ...
```

Every candidate is compared only against one prescribed value.

**Collision search:**

```text
H(m1) ----\
H(m2) -----+-- compare all previous values
H(m3) -----+
H(m4) -----+
...
```

Now every new digest can collide with every previous digest.

The number of opportunities grows like

\[
q^2.
\]

That is why the square root appears.

### The human birthday analogy

If birthdays were perfectly uniform over 365 days and leap days were ignored, then only 23 people are needed for the probability of at least one shared birthday to exceed 50%.

The surprising part is not that 23 is close to 365.

It is that:

\[
\binom{23}{2}=253
\]

different pairs are being tested simultaneously.

Hash collision search exploits exactly this combinatorial growth.

---

## Exact Collision Probability and Its Approximations

Suppose we sample \(q\) values independently and uniformly with replacement from an output set of size \(N\).

For a cryptographic hash model:

\[
N=2^n.
\]

We first calculate the probability that **no collision occurs**.

The first sample can be anything:

\[
\frac{N}{N}=1.
\]

The second must avoid the first value:

\[
\frac{N-1}{N}.
\]

The third must avoid two already-used values:

\[
\frac{N-2}{N}.
\]

Continuing:

\[
\Pr[\text{no collision}]
=
\frac{N}{N}
\frac{N-1}{N}
\frac{N-2}{N}
\cdots
\frac{N-q+1}{N}.
\]

Equivalently,

\[
\Pr[\text{no collision}]
=
\prod_{i=0}^{q-1}
\left(
1-\frac{i}{N}
\right).
\]

Therefore:

\[
\boxed{
\Pr[\text{collision}]
=
1-
\prod_{i=0}^{q-1}
\left(
1-\frac{i}{N}
\right)
}
\]

for

\[
0\le q\le N.
\]

If

\[
q>N,
\]

then the collision probability is exactly one by the pigeonhole principle.

### Exact human-birthday value

For:

\[
N=365,
\qquad
q=23,
\]

the idealized probability is approximately:

\[
0.5073.
\]

So 23 people already give just over a 50% chance of at least one shared birthday.

Human birthdays are not perfectly uniform in reality, but the model is an excellent analogy for ideal hash outputs.

### Deriving the exponential approximation

When:

\[
q\ll N,
\]

the ratios

\[
\frac{i}{N}
\]

are small.

Using:

\[
\ln(1-x)\approx -x,
\]

we obtain:

\[
\ln
\Pr[\text{no collision}]
=
\sum_{i=0}^{q-1}
\ln
\left(
1-\frac{i}{N}
\right).
\]

Approximate each term:

\[
\ln
\Pr[\text{no collision}]
\approx
-
\sum_{i=0}^{q-1}
\frac{i}{N}.
\]

Since:

\[
\sum_{i=0}^{q-1} i
=
\frac{q(q-1)}{2},
\]

we get:

\[
\ln
\Pr[\text{no collision}]
\approx
-
\frac{q(q-1)}{2N}.
\]

Exponentiating:

\[
\Pr[\text{no collision}]
\approx
\exp
\left(
-\frac{q(q-1)}{2N}
\right).
\]

Hence:

\[
\boxed{
\Pr[\text{collision}]
\approx
1-
\exp
\left(
-\frac{q(q-1)}{2N}
\right)
}
\]

This approximation is extremely useful because it can be inverted analytically.

### Samples required for a target probability

Let the desired collision probability be:

\[
p.
\]

Then:

\[
p
\approx
1-
\exp
\left(
-\frac{q(q-1)}{2N}
\right).
\]

Ignoring the small distinction between \(q^2\) and \(q(q-1)\) for large \(q\), solve:

\[
1-p
\approx
\exp
\left(
-\frac{q^2}{2N}
\right).
\]

Taking logarithms:

\[
\ln(1-p)
\approx
-\frac{q^2}{2N}.
\]

Therefore:

\[
\boxed{
q
\approx
\sqrt{
2N
\ln
\frac{1}{1-p}
}
}
\]

For:

\[
p=\frac12,
\]

we obtain:

\[
q_{50}
\approx
\sqrt{
2N\ln2
}.
\]

Thus:

\[
q_{50}
\approx
1.1774\sqrt{N}.
\]

For an \(n\)-bit hash:

\[
\boxed{
q_{50}
\approx
1.1774\cdot2^{n/2}
}
\]

### Three similar constants that should not be confused

There are three related but different quantities.

| Quantity | Approximate samples |
|---|---:|
| Collision probability at \(q=\sqrt N\) | \(1-e^{-1/2}\approx39.35\%\) |
| 50% collision probability | \(1.1774\sqrt N\) |
| Expected samples until first collision | \(\sqrt{\pi N/2}\approx1.2533\sqrt N\) |

All scale as:

\[
\Theta(\sqrt N),
\]

but they are not numerically identical.

### Expected number of colliding pairs

Define:

\[
I_{ij}
=
\begin{cases}
1,& X_i=X_j\\
0,& X_i\neq X_j
\end{cases}
\]

for every pair

\[
i<j.
\]

Since:

\[
\Pr[X_i=X_j]
=
\frac1N,
\]

we have:

\[
\mathbb{E}[I_{ij}]
=
\frac1N.
\]

There are:

\[
\binom q2
\]

pairs, so by linearity of expectation:

\[
\mathbb{E}
\left[
\sum_{i<j}I_{ij}
\right]
=
\binom q2\frac1N.
\]

Therefore:

\[
\boxed{
\mathbb{E}[\text{colliding pairs}]
=
\frac{q(q-1)}{2N}
}
\]

When this number is much smaller than one, it is numerically close to the probability of at least one collision.

But once the expected number exceeds one, it is no longer itself a probability.

For example, an expected number of 3.7 colliding pairs is meaningful.

A "370% collision probability" is not.

That is why the exponential formula is the more appropriate approximation for the event:

\[
\text{"at least one collision"}.
\]

### Numerically stable computation

Directly multiplying:

\[
\prod_i
\left(
1-\frac{i}{N}
\right)
\]

can lose precision when \(N\) is large.

A stable implementation accumulates logarithms:

```python
import math

def exact_collision_probability(q, N):
    if q <= 1:
        return 0.0

    if q > N:
        return 1.0

    log_no_collision = sum(
        math.log1p(-i / N)
        for i in range(q)
    )

    return -math.expm1(log_no_collision)
```

`log1p(x)` accurately evaluates:

\[
\ln(1+x)
\]

for small \(x\), and `expm1(x)` accurately evaluates:

\[
e^x-1.
\]

These details matter when a numerical experiment is intended to validate cryptographic probability estimates rather than merely illustrate syntax.

---

## From Probability to a Generic Collision Attack

The birthday bound becomes a cryptanalytic attack when we store and compare hash outputs across many candidate messages.

A basic collision search is:

```text
seen = empty map

for each candidate message m:
    y = H(m)

    if y already exists in seen:
        return seen[y], m

    seen[y] = m
```

For an ideal \(n\)-bit digest, the expected scale is:

\[
O(2^{n/2})
\]

hash computations and approximately the same number of stored table entries.

### Why a hash table works

Suppose we have already stored \(q\) distinct digest values.

The next candidate collides with one of them with probability approximately:

\[
\frac{q}{N}.
\]

As \(q\) grows, the chance of a match on each new trial grows.

At:

\[
q\approx\sqrt N,
\]

we have accumulated roughly:

\[
\frac{q(q-1)}{2}
\approx
\frac N2
\]

pairwise comparisons implicitly through the table.

That is the computational meaning of the birthday effect.

### A common incorrect experiment

Consider:

```text
repeat:
    choose fresh m1
    choose fresh m2

    if H(m1) == H(m2):
        return collision
```

This tests only **one independent pair** per loop.

Each pair matches with probability:

\[
2^{-n}.
\]

So the expected number of loops is:

\[
2^n.
\]

That is not a birthday attack.

The birthday speedup appears only when candidate outputs are compared across trials through:

- a table,
- sorting,
- a cycle-finding construction,
- or another data structure that preserves cross-trial comparison.

### Hash-table implementation

For a truncated teaching digest:

```python
import hashlib

def truncated_sha256(data, bits):
    assert bits % 8 == 0

    return hashlib.sha256(
        data
    ).digest()[:bits // 8]

def find_collision(bits):
    seen = {}
    i = 0

    while True:
        message = i.to_bytes(8, "big")
        digest = truncated_sha256(
            message,
            bits,
        )

        if digest in seen:
            return (
                seen[digest],
                message,
                digest,
                i + 1,
            )

        seen[digest] = message
        i += 1
```

This is a true birthday-table collision search.

### Time and memory

A direct hash-table attack uses:

\[
O(q)
\]

memory and roughly:

\[
O(q)
\]

expected lookup work.

At the birthday scale:

\[
q\approx2^{n/2}.
\]

So the idealized attack uses:

\[
O(2^{n/2})
\]

time and:

\[
O(2^{n/2})
\]

memory.

### Sorting instead of hashing

An alternative is:

1. generate \(q\) `(digest, message)` pairs;
2. sort them by digest;
3. scan adjacent entries for equal digests.

This uses:

\[
O(q\log q)
\]

comparison work for sorting.

It can be attractive when:

- sequential disk access is cheaper than a huge in-memory hash table,
- external sorting is available,
- deterministic ordering simplifies analysis.

### Memory-reduced collision search

Pollard-rho-style cycle finding can reduce memory substantially when the hash search is embedded into a suitable iterated mapping.

The generic idea is to define a function:

\[
f:\{0,1\}^n\rightarrow\{0,1\}^n
\]

derived from the hash and search for repeated states in the resulting functional graph.

Cycle-finding methods can achieve square-root-scale search with very small memory.

This does not mean every practical collision attack becomes a trivial constant-memory script.

The exact reduction from a hash collision problem to a functional graph must preserve enough information to recover distinct colliding inputs.

The important theoretical point is:

> the birthday bound is primarily a **time/work** phenomenon; the naive \(2^{n/2}\) memory requirement is not fundamental.

### Parallelism

Birthday search parallelizes, but the security discussion should count more than one machine's loop counter.

With \(P\) workers, wall-clock time may decrease, but practical performance depends on:

- how candidate spaces are partitioned,
- how collisions across workers are detected,
- communication cost,
- memory organization,
- total number of hash evaluations.

Cryptographic security strength is generally about **total attacker resources**, not only sequential wall-clock time on one CPU.

---

## Truncation, Multi-Target Settings, and System-Wide Risk

Digest truncation is where the birthday bound becomes an immediate engineering concern.

Suppose a secure \(n\)-bit hash is truncated to:

\[
t<n
\]

bits.

The effective collision space now contains only:

\[
2^t
\]

values.

Therefore the generic collision scale becomes:

\[
2^{t/2}.
\]

### 50% collision scale

Using:

\[
q_{50}
\approx
1.1774\cdot2^{t/2},
\]

we obtain:

| Output bits \(t\) | Approximate \(q_{50}\) | Generic collision strength |
|---:|---:|---:|
| 16 | \(3.01\times10^2\) | about 8 bits |
| 32 | \(7.72\times10^4\) | about 16 bits |
| 64 | \(5.06\times10^9\) | about 32 bits |
| 96 | \(3.31\times10^{14}\) | about 48 bits |
| 128 | \(2.17\times10^{19}\) | about 64 bits |
| 160 | \(1.42\times10^{24}\) | about 80 bits |
| 256 | \(4.01\times10^{38}\) | about 128 bits |

The important rule is:

\[
\boxed{
t\text{-bit digest}
\Rightarrow
\text{at most }t/2\text{ bits of generic collision security}
}
\]

### Truncating SHA-256

Suppose:

```python
digest = sha256(message)[:8]
```

where only 8 bytes are retained.

That is a:

\[
64\text{-bit digest}.
\]

Its ideal generic collision strength is therefore only:

\[
32\text{ bits}.
\]

The underlying SHA-256 primitive may still be perfectly healthy.

The application has deliberately reduced the collision security through truncation.

### Accidental collisions versus adversarial collisions

The same mathematics appears in two very different threat models.

**Accidental collision.**

Records receive random-looking identifiers or digests and nobody is maliciously searching for duplicates.

The question is:

\[
\Pr[\text{some accidental duplicate among }q\text{ records}].
\]

**Adversarial collision.**

An attacker actively chooses and evaluates messages until two digests collide.

The mathematical birthday scale may be similar, but the operational risk is different because the attacker can spend focused computation and choose inputs strategically.

Therefore:

> randomly generated identifiers and adversarially chosen hash commitments should not automatically use the same security policy simply because both involve \(n\)-bit strings.

### System-wide collision risk

Suppose a system stores \(q\) independent \(t\)-bit identifiers.

The approximate accidental collision probability is:

\[
p
\approx
1-
\exp
\left(
-\frac{q(q-1)}{2^{t+1}}
\right).
\]

This should be computed over the **lifetime system population**, not merely one process or one day.

If a system has:

- many users,
- many devices,
- replicated databases,
- long operational lifetime,

then the relevant \(q\) may be much larger than expected from a local component's perspective.

### Multi-user and multi-target effects

A security estimate can weaken when an attacker is happy to find a success against **any** member of a large population.

For example:

```text
one target:
    attack this exact digest

many targets:
    attack any one of one million digests
```

The second game gives the attacker more opportunities.

The exact bound depends on the primitive and attack model, but the engineering lesson is general:

> system-wide security should count all relevant targets and queries, not only the strength of one isolated object.

### Identifiers are not automatically commitments

A short digest may be perfectly adequate as:

- a local cache key,
- a non-adversarial deduplication hint,
- a compact database index,

while being inadequate as:

- an adversarial content commitment,
- a signature digest,
- a cryptographic certificate fingerprint,
- a consensus object identifier.

The intended security property determines the required output length.

---

## Reproducible Python Laboratory

The repository experiment:

[`birthday_collision.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/birthday_collision.py)

is designed to reproduce the birthday effect using truncated SHA-256.

The code should preserve four important properties:

1. retain exactly the requested number of output bits;
2. avoid accidentally dropping leading zeroes;
3. generate deterministic candidate messages for reproducibility;
4. compare candidate digests across trials.

### A compact implementation

```python
import hashlib
import math


def truncated_sha256(data, bits):
    if bits <= 0 or bits % 8 != 0:
        raise ValueError(
            "bits must be a positive multiple of 8"
        )

    return hashlib.sha256(
        data
    ).digest()[:bits // 8]


def find_collision(bits):
    seen = {}

    for i in range(1 << 32):
        message = i.to_bytes(8, "big")

        digest = truncated_sha256(
            message,
            bits,
        )

        if digest in seen:
            return (
                seen[digest],
                message,
                digest,
                i + 1,
            )

        seen[digest] = message

    raise RuntimeError("collision not found")


def q50(bits):
    N = 1 << bits

    return math.sqrt(
        2 * N * math.log(2)
    )
```

For 16 bits:

```python
m1, m2, digest, evaluations = (
    find_collision(16)
)

print(
    "m1 =",
    m1.hex(),
)

print(
    "m2 =",
    m2.hex(),
)

print(
    "digest =",
    digest.hex(),
)

print(
    "evaluations =",
    evaluations,
)

print(
    "q50 =",
    q50(16),
)
```

A deterministic counter sequence gives one concrete collision:

```text
m1 = 0000000000000039
m2 = 0000000000000102
digest = 82c2
evaluations = 259
```

The theoretical 50% point is:

```text
301.42
```

The experiment does not need to stop exactly at 301.

Probability describes the distribution over experiments.

A particular deterministic candidate sequence can collide earlier or later.

### Exact versus approximate probability

We can compare the exact and approximate formulas:

```python
def exact_collision_probability(q, bits):
    N = 1 << bits

    if q <= 1:
        return 0.0

    if q > N:
        return 1.0

    log_no_collision = sum(
        math.log1p(-i / N)
        for i in range(q)
    )

    return -math.expm1(
        log_no_collision
    )


def approximate_collision_probability(q, bits):
    N = 1 << bits

    return 1 - math.exp(
        -q * (q - 1) / (2 * N)
    )
```

For:

\[
q=301,
\qquad
n=16,
\]

both values are close to one half.

That is an excellent point to test the approximation numerically.

### Collision versus preimage in one experiment

Now use the same 16-bit truncated SHA-256 but fix a target:

```python
target = bytes.fromhex("1234")
```

Search:

```python
def find_preimage(target):
    for i in range(1 << 32):
        message = (
            b"preimage_"
            + str(i).encode()
        )

        if truncated_sha256(
            message,
            16,
        ) == target:
            return message, i + 1
```

One deterministic run finds:

```text
preimage_12650
```

after:

```text
12651
```

evaluations.

That run happened to hit earlier than the ideal expectation:

\[
2^{16}=65536.
\]

But it still illustrates the large gap from the collision experiment, which found a match after only a few hundred candidates.

The real comparison is asymptotic:

\[
\boxed{
\text{collision}\sim2^{n/2}
}
\]

versus:

\[
\boxed{
\text{fixed-target preimage}\sim2^n
}
\]

for the same \(n\)-bit output.

### Do not over-interpret one run

A single run is not a statistical study.

For experimental work, repeat the search over many:

- salts,
- prefixes,
- randomized candidate permutations,
- independent seeds.

Then record:

- median evaluations,
- mean evaluations,
- quantiles,
- variance,
- empirical collision probability at fixed \(q\).

That lets the experiment test the predicted distribution rather than merely produce one anecdotal collision.

---

## What a Birthday Attack Does and Does Not Prove

Birthday attacks are easy to misunderstand because they produce visually dramatic results: two different messages, one digest.

The scope of the result must remain precise.

### It does not invert a fixed digest

A birthday collision attack solves:

\[
H(x)=H(x')
\]

for attacker-chosen \(x,x'\).

It does not solve:

\[
H(x)=y
\]

for a prescribed \(y\).

The latter remains a preimage problem.

### A 16-bit truncated collision is not a full SHA-256 collision

Suppose:

\[
\operatorname{Trunc}_{16}
(
\operatorname{SHA256}(M)
)
=
\operatorname{Trunc}_{16}
(
\operatorname{SHA256}(M')
).
\]

This only proves equality of the first 16 bits.

The full 256-bit digests can still be completely different.

Therefore:

```text
"found collision in truncated SHA-256"
```

is correct.

```text
"broke SHA-256"
```

is not.

### Generic collision search gives little semantic control

A birthday-table attack may produce messages such as:

```text
0000000000000039
0000000000000102
```

That is enough to demonstrate collision complexity.

But a real protocol exploit may require the attacker to create two meaningful objects such as:

```text
contract A
contract B
```

or:

```text
certificate A
certificate B
```

that obey a file format and collide.

This motivates stronger cryptanalytic capabilities such as:

- differential collision construction,
- chosen-prefix collisions,
- format-aware collision engineering.

A generic birthday collision does not automatically provide that control.

### It does not automatically forge HMAC

HMAC is a keyed MAC construction.

An attacker cannot generally turn:

\[
H(M_1)=H(M_2)
\]

for an unkeyed toy hash experiment into an HMAC forgery.

MAC security depends on:

- secret keying,
- tag length,
- verification queries,
- construction-specific proofs and assumptions.

A short authentication tag may face guessing attacks, but that is a different game from an unkeyed birthday collision.

### It does not replace structural cryptanalysis

The birthday attack is generic.

It treats the hash as a black box.

If cryptanalysts exploit the internal structure of a named hash and produce collisions significantly faster than:

\[
2^{n/2},
\]

that is a stronger algorithm-specific result.

MD5 and SHA-1 are historically important precisely because structural cryptanalysis beats the generic ideal bound.

### Accidental collision analysis is not always adversarial security analysis

A UUID-like random identifier may be generated independently of an adversary.

A cryptographic commitment may be attacked by someone who can evaluate enormous numbers of chosen messages.

The same probability formulas help in both cases, but system design must model the actual adversary.

---

## Design Consequences and Conclusion

The birthday bound is more than a probability curiosity.

It directly constrains cryptographic parameter selection.

For an ideal \(n\)-bit hash:

\[
\text{generic collision work}
\sim
2^{n/2}.
\]

Therefore, if an application needs approximately \(s\) bits of classical collision security, a first-order requirement is:

\[
n\ge2s.
\]

For example:

\[
s=128
\]

suggests at least:

\[
n=256
\]

digest bits before considering truncation, multi-user effects, protocol structure, or algorithm-specific cryptanalysis.

The main engineering lessons are:

1. **Do not quote digest length as collision security.**  
   An \(n\)-bit output offers only about \(n/2\) bits of ideal generic collision strength.

2. **Do not truncate blindly.**  
   Retaining \(t\) bits reduces generic collision strength to about \(t/2\) bits.

3. **Count system-wide population.**  
   Accidental collision probability depends on the total number of relevant objects over the system lifetime.

4. **Separate accidental from adversarial models.**  
   A random identifier and an adversarial commitment may need different safety margins.

5. **Use the correct security game.**  
   Collision, preimage, second-preimage, and tag forgery are different problems.

6. **Do not confuse a toy collision with a break of the underlying full hash.**  
   Truncation experiments demonstrate probability, not structural cryptanalysis.

7. **Use authentication when an active attacker can replace both message and digest.**  
   A plain hash is not a MAC.

The square-root phenomenon can be summarized in one line:

\[
\boxed{
\binom{q}{2}
\approx
\frac{q^2}{2}
}
\]

candidate pairs are created from only \(q\) sampled hash outputs.

That quadratic growth is the entire source of the birthday advantage.

The next article can now move from **generic black-box probability** to **internal hash construction**: Merkle-Damgård iteration, compression functions, SHA-256 padding and message scheduling, and the structural reason length-extension attacks appear in some iterated hashes.

Previous: [Hash Security Properties](/blog/hash-security-properties/).

Next: [Merkle-Damgård and SHA-256](/blog/merkle-damgard-sha256/).

---

## References

1. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**.  
   https://doi.org/10.6028/NIST.FIPS.180-4

2. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, Chapter 9: Hash Functions and Data Integrity.

3. Jonathan Katz and Yehuda Lindell, **Introduction to Modern Cryptography**, chapters on hash functions and generic collision resistance.

4. Mihir Bellare and Phillip Rogaway, lecture notes and foundational treatments of collision-resistant hashing and birthday bounds.

5. Python Software Foundation, **`hashlib` — Secure hashes and message digests**.  
   https://docs.python.org/3/library/hashlib.html
