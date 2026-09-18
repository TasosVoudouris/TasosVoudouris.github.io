---
title: "Computational Number Theory II: Prime Counting, the Prime Number Theorem, and Prime Gaps"
description: "A computational study of pi(x), x/log x, Li(x), prime density, error terms, prime gaps, and what asymptotic statements do—and do not—say at finite scales."
pubDate: "2025-05-25"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "prime-counting-function"
  - "prime-number-theorem"
  - "logarithmic-integral"
  - "prime-gaps"
  - "riemann-hypothesis"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 2
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

Prime numbers become progressively sparser as integers grow.

But "sparser" is only a qualitative statement.

To study prime distribution computationally, we need a function that measures how many primes have appeared up to a given scale.

That function is:

$$
\boxed{
\pi(x)
=
\#\{
p\le x:
p\text{ is prime}
\}.
}
$$

For example:

$$
\pi(10)=4,
$$

because:

$$
2,3,5,7
$$

are the four primes not exceeding $10$.

The central questions are then:

$$
\text{How quickly does }\pi(x)\text{ grow?}
$$

$$
\text{How accurately can we approximate it?}
$$

$$
\text{How far apart are consecutive primes?}
$$

and, computationally:

$$
\text{What can finite experiments actually tell us?}
$$

The key distinction throughout this article is:

$$
\boxed{
\text{computation observes},
\qquad
\text{heuristics predict},
\qquad
\text{theorems prove}.
}
$$

---

## Table of Contents

- [The prime-counting function](#the-prime-counting-function)
- [The Prime Number Theorem](#the-prime-number-theorem)
- [The logarithmic integral](#the-logarithmic-integral)
- [Error terms and the Riemann Hypothesis](#error-terms-and-the-riemann-hypothesis)
- [Prime gaps](#prime-gaps)
- [Computational experiments and misleading plots](#computational-experiments-and-misleading-plots)
- [Prime density and cryptographic prime generation](#prime-density-and-cryptographic-prime-generation)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## The prime-counting function

Define:

$$
\boxed{
\pi(x)
=
\#\{
p\le x:
p\text{ prime}
\}.
}
$$

The function is a staircase.

It increases by one exactly when $x$ passes a prime.

For example:

$$
\pi(2)=1,
$$

$$
\pi(10)=4,
$$

$$
\pi(100)=25,
$$

and:

$$
\pi(1000)=168.
$$

---

### Exact computation

For moderate bounds, the natural computational tool is a sieve.

The Sieve of Eratosthenes generates all primes up to:

$$
N
$$

and therefore allows us to compute:

$$
\pi(x)
$$

for every:

$$
x\le N.
$$

A simple implementation is:

```python
from math import isqrt


def primes_up_to(n: int) -> list[int]:
    if n < 2:
        return []

    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0] = 0
    is_prime[1] = 0

    for p in range(2, isqrt(n) + 1):
        if not is_prime[p]:
            continue

        start = p * p

        is_prime[start:n + 1:p] = (
            b"\x00"
            * (((n - start) // p) + 1)
        )

    return [
        n
        for n in range(2, len(is_prime))
        if is_prime[n]
    ]
```

Then:

```python
primes = primes_up_to(1_000_000)

print(len(primes))
```

returns:

```text
78498
```

because:

$$
\boxed{
\pi(10^6)=78\,498.
}
$$

---

### Counting without storing every prime

If only the number of primes is required, the sieve can instead maintain a Boolean array and count the surviving entries.

For very large $x$, however, storing all integers up to $x$ becomes expensive.

More sophisticated prime-counting algorithms can evaluate:

$$
\pi(x)
$$

without enumerating every prime up to $x$.

That distinction becomes important in serious computational number theory.

For the experiments in this article, however, an ordinary sieve is enough.

---

## The Prime Number Theorem

The central theorem describing the large-scale distribution of primes is the **Prime Number Theorem**:

$$
\boxed{
\pi(x)
\sim
\frac{x}{\log x}.
}
$$

Here:

$$
\log x
$$

means the natural logarithm.

The symbol:

$$
\sim
$$

has a precise asymptotic meaning:

$$
\boxed{
\lim_{x\rightarrow\infty}
\frac{
\pi(x)
}{
x/\log x
}
=
1.
}
$$

This is a ratio statement.

It does **not** say:

$$
\pi(x)
=
\frac{x}{\log x}.
$$

It does not even say that the absolute difference:

$$
\pi(x)-\frac{x}{\log x}
$$

tends to zero.

In fact, both terms grow without bound.

What tends to $1$ is their **ratio**.

---

### Relative rather than absolute accuracy

Suppose:

$$
A(x)\sim B(x).
$$

This means:

$$
\frac{A(x)}{B(x)}
\rightarrow1.
$$

Equivalently:

$$
A(x)
=
B(x)(1+o(1)).
$$

So the relative error tends to zero:

$$
\frac{
A(x)-B(x)
}{
B(x)
}
\rightarrow0.
$$

The absolute error may still become very large.

This distinction is essential whenever asymptotic notation is interpreted computationally.

---

### Prime density

Divide the Prime Number Theorem by $x$:

$$
\frac{\pi(x)}{x}
\sim
\frac1{\log x}.
$$

So among the integers up to a large $x$, the proportion that are prime is approximately:

$$
\boxed{
\frac1{\log x}.
}
$$

This motivates the informal statement:

> An integer near a large $x$ behaves as though it has probability roughly $1/\log x$ of being prime.

This is a useful heuristic interpretation.

It is not a probability theorem asserting independence between primality events.

Primes are constrained by divisibility and congruence conditions, so they are far from genuinely independent random samples.

---

### Expected spacing

If the local density of primes near $x$ is roughly:

$$
\frac1{\log x},
$$

then the corresponding average spacing is approximately:

$$
\boxed{
\log x.
}
$$

This is the first heuristic connection between the Prime Number Theorem and prime gaps.

It describes average scale, not individual gaps.

Individual gaps fluctuate substantially.

---

## The logarithmic integral

The approximation:

$$
\frac{x}{\log x}
$$

captures the first-order growth of:

$$
\pi(x).
$$

But a better approximation over many practical ranges is the **logarithmic integral**:

$$
\boxed{
\operatorname{Li}(x)
=
\int_2^x
\frac{dt}{\log t}.
}
$$

The reason is intuitive.

The approximate prime density is not constant between $2$ and $x$.

It changes gradually according to:

$$
\frac1{\log t}.
$$

Instead of using only the density at the endpoint $x$, the integral accumulates the varying density:

$$
\boxed{
\operatorname{Li}(x)
=
\int_2^x
\text{local density approximation}\,dt.
}
$$

---

### Numerical comparison

Consider several finite scales.

| $x$ | $\pi(x)$ | $x/\log x$ | $\operatorname{Li}(x)$ |
| ---: | ---: | ---: | ---: |
| $10$ | $4$ | $4.34$ | $6.17$ |
| $100$ | $25$ | $21.71$ | $30.13$ |
| $10^3$ | $168$ | $144.76$ | $177.61$ |
| $10^4$ | $1229$ | $1085.74$ | $1246.14$ |
| $10^5$ | $9592$ | $8685.89$ | $9629.81$ |
| $10^6$ | $78498$ | $72382.41$ | $78627.55$ |

At:

$$
x=10^6,
$$

we have:

$$
\pi(x)=78\,498,
$$

while:

$$
\frac{x}{\log x}
\approx
72\,382.41,
$$

and:

$$
\operatorname{Li}(x)
\approx
78\,627.55.
$$

At this scale, $\operatorname{Li}(x)$ is numerically much closer.

But this table is **experimental evidence at selected finite values**, not a proof of asymptotic superiority.

---

### Why $\operatorname{Li}(x)$ is still not exact

For many ranges:

$$
\operatorname{Li}(x)
>
\pi(x).
$$

It would be tempting to conclude that this inequality always holds.

That conclusion is false.

A theorem of Littlewood shows that:

$$
\boxed{
\pi(x)-\operatorname{Li}(x)
}
$$

changes sign infinitely often.

The first sign change is known to occur only at an extraordinarily large scale relative to ordinary numerical experiments.

This is an excellent warning about computational evidence:

$$
\boxed{
\text{a pattern surviving enormous finite ranges need not be universal}.
}
$$

---

## Error terms and the Riemann Hypothesis

The Prime Number Theorem gives:

$$
\pi(x)
\sim
\operatorname{Li}(x),
$$

but it is natural to ask how large the difference can be.

Define the error:

$$
\boxed{
E(x)
=
\pi(x)-\operatorname{Li}(x).
}
$$

Understanding $E(x)$ is deeply connected to the zeros of the Riemann zeta function.

---

### The Riemann zeta function

For:

$$
\operatorname{Re}(s)>1,
$$

the Riemann zeta function is:

$$
\boxed{
\zeta(s)
=
\sum_{n=1}^{\infty}
\frac1{n^s}.
}
$$

Euler discovered its product representation:

$$
\boxed{
\zeta(s)
=
\prod_p
\frac1{1-p^{-s}},
}
$$

where the product is over all primes.

This identity directly connects:

$$
\boxed{
\text{analytic behavior of }\zeta(s)
}
$$

with:

$$
\boxed{
\text{distribution of primes}.
}
$$

---

### The Riemann Hypothesis

The Riemann Hypothesis asserts that every nontrivial zero of:

$$
\zeta(s)
$$

has real part:

$$
\boxed{
\frac12.
}
$$

Its relevance to prime counting is that the locations of these zeros control oscillations in prime-distribution error terms.

---

### The conditional error bound

A classical theorem associated with von Koch states that the Riemann Hypothesis is equivalent to an error estimate of the form:

$$
\boxed{
\pi(x)
=
\operatorname{Li}(x)
+
O(
\sqrt{x}\log x
).
}
$$

The condition is essential.

We must **not** write this as an unconditional approximation.

Rather:

$$
\boxed{
\text{RH}
\quad\Longleftrightarrow\quad
\text{an error bound of this strength}.
}
$$

The Prime Number Theorem itself is unconditional.

The much sharper square-root-scale control is tied to the Riemann Hypothesis.

---

### What big-$O$ means here

Writing:

$$
E(x)
=
O(
\sqrt{x}\log x
)
$$

means that there exist constants:

$$
C>0,
\qquad
x_0,
$$

such that:

$$
|E(x)|
\le
C\sqrt{x}\log x
$$

for all:

$$
x\ge x_0.
$$

It does not mean:

$$
E(x)
=
\sqrt{x}\log x.
$$

Again, asymptotic notation describes a growth bound, not an exact formula.

---

### Weighted prime-counting functions

Analytic number theory often studies weighted versions of $\pi(x)$.

One important example is Chebyshev's function:

$$
\boxed{
\vartheta(x)
=
\sum_{p\le x}\log p.
}
$$

Another is:

$$
\boxed{
\psi(x)
=
\sum_{p^k\le x}
\log p.
}
$$

The Prime Number Theorem is equivalent to:

$$
\vartheta(x)\sim x
$$

and also to:

$$
\psi(x)\sim x.
$$

These weighted functions interact particularly cleanly with the zeta function and are therefore central in analytic proofs of results about prime distribution.

---

## Prime gaps

Let:

$$
p_1<p_2<p_3<\cdots
$$

be the sequence of prime numbers.

Define the $n$-th prime gap by:

$$
\boxed{
g_n
=
p_{n+1}-p_n.
}
$$

For example:

$$
2,3,5,7,11,13,\ldots
$$

gives gaps:

$$
1,2,2,4,2,\ldots
$$

Except for:

$$
3-2=1,
$$

every prime gap is even because every prime greater than $2$ is odd.

---

### Average gap near $x$

The Prime Number Theorem suggests approximately:

$$
\frac{x}{\log x}
$$

primes below $x$.

So the mean spacing is of order:

$$
\boxed{
\log x.
}
$$

But this is an average statement.

It does not mean:

$$
g_n\approx\log p_n
$$

for every $n$.

Some gaps are much smaller.

Others are much larger.

---

### Prime gaps are unbounded

Prime gaps can become arbitrarily large.

This has an elementary proof.

Choose:

$$
m\ge2
$$

and consider:

$$
N=(m+1)!.
$$

Then:

$$
N+2
$$

is divisible by $2$,

$$
N+3
$$

is divisible by $3$,

and in general:

$$
N+k
$$

is divisible by $k$ for:

$$
2\le k\le m+1.
$$

Thus:

$$
\boxed{
N+2,
N+3,
\ldots,
N+m+1
}
$$

are all composite.

Since $m$ can be arbitrarily large, arbitrarily long runs of composite numbers exist.

Therefore:

$$
\boxed{
\limsup_{n\to\infty}g_n=\infty.
}
$$

---

### Small gaps

Large gaps exist, but small gaps also occur frequently.

The most famous example is a gap of:

$$
2.
$$

Pairs such as:

$$
(3,5),
$$

$$
(5,7),
$$

$$
(11,13),
$$

$$
(17,19)
$$

are **twin primes**.

The Twin Prime Conjecture asks whether:

$$
\boxed{
g_n=2
}
$$

occurs infinitely often.

This remains much stronger than merely showing that some bounded gap occurs infinitely often.

Modern bounded-gap results prove that there exists a fixed finite bound $B$ such that infinitely many consecutive prime pairs have gap at most $B$.

That is a major theorem, but it does not establish the twin-prime case:

$$
B=2.
$$

---

### Heuristics for large gaps

A simple probabilistic model treats primality near $x$ as occurring with approximate density:

$$
\frac1{\log x}.
$$

Such models motivate predictions about prime gaps, including logarithmic and squared-logarithmic scales.

But these are heuristics.

Prime divisibility events contain arithmetic correlations that a naive random model does not capture exactly.

So one should distinguish carefully between:

$$
\boxed{
\text{PNT-derived average scale}
}
$$

and:

$$
\boxed{
\text{probabilistic models for individual or maximal gaps}.
}
$$

---

## Computational experiments and misleading plots

Prime counting and prime gaps are excellent subjects for experimentation because large datasets are easy to generate.

They are also excellent examples of how computational evidence can be misinterpreted.

---

### Computing prime gaps

Given an ordered list of primes:

```python
def prime_gaps(
    primes: list[int],
) -> list[int]:
    return [
        b - a
        for a, b in zip(
            primes,
            primes[1:],
        )
    ]
```

For example:

```python
primes = primes_up_to(1_000_000)
gaps = prime_gaps(primes)

print(max(gaps))
```

This lets us study:

- gap frequencies;
- mean gaps;
- maximal observed gaps;
- residue patterns;
- changes as the cutoff increases.

---

### A useful comparison experiment

For selected $x$, compare:

$$
\pi(x),
$$

$$
\frac{x}{\log x},
$$

and:

$$
\operatorname{Li}(x).
$$

One useful relative-error quantity is:

$$
\boxed{
\frac{
A(x)-\pi(x)
}{
\pi(x)
},
}
$$

where $A(x)$ is an approximation.

A plot of relative rather than absolute error can make asymptotic behavior much easier to interpret.

---

### Why raw plots can mislead

Suppose we plot:

$$
\pi(x)
$$

and:

$$
\frac{x}{\log x}
$$

on the same axes for large $x$.

Because both functions are large and close relative to their magnitude, the curves may visually overlap.

That does not mean the absolute error is small.

Conversely, plotting only:

$$
\pi(x)-\frac{x}{\log x}
$$

may make the approximation look poor because the absolute difference grows.

Both plots can be mathematically correct while emphasizing completely different notions of approximation.

So computational analysis should distinguish:

$$
\boxed{
\text{absolute error}
}
$$

from:

$$
\boxed{
\text{relative error}.
}
$$

---

### Gap histograms

A histogram of prime gaps up to:

$$
10^6
$$

may display visible peaks at certain even gaps, including multiples of:

$$
6.
$$

This reflects arithmetic congruence restrictions and local divisibility structure.

For example, every prime greater than $3$ satisfies:

$$
p\equiv\pm1\pmod6.
$$

But observing a peak in a finite histogram does not prove that the same gap dominates asymptotically.

The correct conclusion is:

> the finite data exhibit a strong arithmetic bias.

Not:

> we have discovered the limiting distribution of prime gaps.

---

### Finite evidence does not establish an asymptotic theorem

Suppose a property holds for every prime below:

$$
10^{12}.
$$

That may be impressive computational evidence.

But an asymptotic claim concerns:

$$
x\rightarrow\infty.
$$

No finite cutoff, however large, reaches infinity.

This distinction has repeatedly mattered in number theory.

The example:

$$
\pi(x)<\operatorname{Li}(x)
$$

is particularly instructive: enormous numerical ranges can support a pattern that eventually reverses.

Thus:

$$
\boxed{
\text{computation can discover patterns}
}
$$

and:

$$
\boxed{
\text{computation can test conjectures up to a bound},
}
$$

but:

$$
\boxed{
\text{finite verification alone does not prove an unbounded statement}.
}
$$

---

## Prime density and cryptographic prime generation

Prime density has a direct computational consequence in cryptography.

Suppose we want a random prime near some large number:

$$
x.
$$

The Prime Number Theorem suggests that a random integer of this size is prime with approximate probability:

$$
\boxed{
\frac1{\log x}.
}
$$

Therefore the expected number of random integer trials before finding a prime is roughly:

$$
\boxed{
\log x.
}
$$

---

### Restricting to odd candidates

For large primes, we obviously avoid even numbers.

Roughly half of all integers are odd.

Since almost every prime is odd, conditioning on odd candidates approximately doubles the prime density.

Thus a random odd integer near $x$ has heuristic prime probability:

$$
\boxed{
\frac{2}{\log x}.
}
$$

The expected number of odd candidates is therefore approximately:

$$
\boxed{
\frac{\log x}{2}.
}
$$

---

### Example: 2048-bit scale

A $2048$-bit integer has size roughly:

$$
x\approx2^{2048}.
$$

Therefore:

$$
\log x
\approx
2048\log2.
$$

Numerically:

$$
2048\log2
\approx
1419.6.
$$

So a uniformly sampled integer at this scale has heuristic prime probability approximately:

$$
\frac1{1419.6}.
$$

If we sample only odd candidates:

$$
\boxed{
\Pr[
\text{prime}\mid\text{odd}
]
\approx
\frac2{1419.6}
\approx
0.00141.
}
$$

So the expected number of odd candidates is roughly:

$$
\boxed{
710.
}
$$

This does **not** mean exactly 710 tests are required.

Prime generation is stochastic.

It means that the expected search scale is only on the order of hundreds of candidates, despite the enormous size of the integers.

---

### Sieving candidates first

Implementations can improve this further by rejecting candidates divisible by small primes.

For example, instead of sampling arbitrary odd integers, one may immediately reject numbers divisible by:

$$
3,5,7,11,\ldots
$$

before performing more expensive probable-prime tests.

Conditioning on having passed these small-prime filters increases the fraction of surviving candidates that are prime.

So practical prime generation follows a layered pattern:

```text
generate candidate
        ↓
force required structure
        ↓
small-prime filtering
        ↓
probable-prime testing
        ↓
optional stronger validation
```

The Prime Number Theorem explains why this search process is feasible in the first place.

---

## The structural picture

The central quantity is:

$$
\boxed{
\pi(x).
}
$$

The Prime Number Theorem says:

$$
\boxed{
\pi(x)
\sim
\frac{x}{\log x}.
}
$$

A refined approximation is:

$$
\boxed{
\operatorname{Li}(x).
}
$$

The difference:

$$
\pi(x)-\operatorname{Li}(x)
$$

connects prime counting to the zero structure of:

$$
\zeta(s),
$$

and the Riemann Hypothesis predicts strong control of that error.

Meanwhile, the density:

$$
\frac1{\log x}
$$

suggests an average prime spacing of:

$$
\log x.
$$

This leads naturally to prime gaps:

$$
\boxed{
g_n=p_{n+1}-p_n.
}
$$

The full picture is therefore:

$$
\boxed{
\text{count primes}
\rightarrow
\text{estimate density}
\rightarrow
\text{study error}
\rightarrow
\text{study spacing}.
}
$$

At every stage, one must distinguish:

$$
\boxed{
\text{exact data}
}
$$

from:

$$
\boxed{
\text{asymptotic theorem}
}
$$

from:

$$
\boxed{
\text{heuristic model}.
}
$$

That distinction is one of the most important habits in computational number theory.

---

## Practice and checkpoint

### Exercise 1 — Prime counting

Compute:

$$
\pi(10),
\qquad
\pi(100),
\qquad
\pi(1000).
$$

Compare each value with:

$$
\frac{x}{\log x}.
$$

---

### Exercise 2 — Relative error

For:

$$
x=10^6,
$$

use:

$$
\pi(x)=78\,498
$$

and compute the relative error of:

$$
\frac{x}{\log x}.
$$

Compare it with the relative error of:

$$
\operatorname{Li}(x).
$$

---

### Exercise 3 — Meaning of asymptotic equivalence

Explain why:

$$
\pi(x)
\sim
\frac{x}{\log x}
$$

does not imply:

$$
\pi(x)-\frac{x}{\log x}
\rightarrow0.
$$

---

### Exercise 4 — Prime density

Near:

$$
x=10^{12},
$$

estimate the heuristic probability that a randomly chosen integer is prime.

Then estimate the probability conditioned on the integer being odd.

---

### Exercise 5 — Average gap

Use the Prime Number Theorem to explain why the average prime spacing near $x$ should be on the order of:

$$
\log x.
$$

Why does this not determine any particular:

$$
g_n?
$$

---

### Exercise 6 — Unbounded gaps

Let:

$$
N=11!.
$$

Show that:

$$
N+2,
N+3,
\ldots,
N+11
$$

are all composite.

Explain how the construction generalizes.

---

### Exercise 7 — Twin primes

What does the Twin Prime Conjecture assert?

Explain the difference between proving infinitely many gaps of size:

$$
2
$$

and proving infinitely many prime gaps bounded by some unspecified fixed constant.

---

### Exercise 8 — Conditional error term

Explain the logical difference between:

$$
\pi(x)\sim\operatorname{Li}(x)
$$

and:

$$
\pi(x)
=
\operatorname{Li}(x)
+
O(
\sqrt{x}\log x
).
$$

Which statement is unconditional, and which is tied to the Riemann Hypothesis?

---

### Exercise 9 — Gap histogram

Generate all primes up to:

$$
10^6.
$$

Construct the sequence:

$$
g_n=p_{n+1}-p_n.
$$

Plot a histogram.

What patterns appear?

Which observations are data, and which would require a theorem before being stated asymptotically?

---

### Exercise 10 — Cryptographic scale

For a random $1024$-bit odd integer, estimate the expected number of candidates that must be tested before encountering a prime.

Use:

$$
\log(2^{1024})
=
1024\log2.
$$

---

### Reader checkpoint

You should now be able to explain:

1. What:
   $$
   \pi(x)
   $$
   counts.
2. How a sieve can compute $\pi(x)$ over a finite range.
3. What:
   $$
   \pi(x)\sim\frac{x}{\log x}
   $$
   means precisely.
4. Why asymptotic equivalence concerns relative rather than absolute error.
5. Why:
   $$
   1/\log x
   $$
   can be interpreted as an approximate local prime density.
6. Why that interpretation is heuristic rather than an independent-probability model.
7. Why:
   $$
   \operatorname{Li}(x)
   $$
   is a natural refinement of:
   $$
   x/\log x.
   $$
8. Why finite numerical superiority of $\operatorname{Li}(x)$ does not itself prove an asymptotic statement.
9. Why:
   $$
   \pi(x)-\operatorname{Li}(x)
   $$
   eventually changes sign.
10. How the Riemann zeta function is connected to primes through Euler's product.
11. What role the Riemann Hypothesis plays in prime-counting error estimates.
12. Why:
    $$
    O(\sqrt{x}\log x)
    $$
    must not be presented as an unconditional PNT error term.
13. What a prime gap is.
14. Why all prime gaps after the first are even.
15. Why prime gaps are unbounded.
16. Why the mean gap near $x$ is of scale:
    $$
    \log x.
    $$
17. What the Twin Prime Conjecture asks.
18. Why bounded-gap theorems do not by themselves prove the twin-prime conjecture.
19. Why a finite histogram cannot establish a limiting distribution.
20. Why absolute and relative-error plots can tell very different visual stories.
21. How prime density predicts the approximate cost of random prime generation.
22. Why sampling only odd candidates roughly doubles the prime density.

At this point, prime distribution should no longer look like a vague statement that "primes become rare."

It has become a quantitative computational problem involving:

$$
\boxed{
\text{counting},
\quad
\text{approximation},
\quad
\text{error},
\quad
\text{spacing}.
}
$$

---

## References and further reading

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical reference for the distribution of primes and the Prime Number Theorem.

**Tom M. Apostol**,  
*Introduction to Analytic Number Theory.*

A systematic introduction to prime counting, Chebyshev functions, arithmetic functions, and analytic number theory.

**Hugh L. Montgomery and Robert C. Vaughan**,  
*Multiplicative Number Theory I: Classical Theory.*

A deeper treatment of the Prime Number Theorem, zeta-function methods, and prime distribution.

**Harold M. Edwards**,  
*Riemann's Zeta Function.*

An accessible historical and mathematical route from the zeta function to the distribution of primes.

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

Particularly useful for computational prime generation, primality testing, prime counting, and large-scale experimentation.

**Andrew Granville**,  
*Harald Cramér and the Distribution of Prime Numbers.*

Useful for understanding probabilistic models of prime distribution and their limitations.

---

## Next

Part I studied arithmetic functions attached to individual integers.

Part II has moved to the global distribution of primes:

$$
\boxed{
\pi(x),
\qquad
\operatorname{Li}(x),
\qquad
g_n.
}
$$

The next article changes perspective again.

Instead of studying primes only inside:

$$
\mathbb Z,
$$

we enlarge the arithmetic universe to numbers of the form:

$$
\boxed{
a+bi,
\qquad
a,b\in\mathbb Z.
}
$$

There, ordinary primes may remain prime, split into factors, or behave exceptionally.

This leads to the arithmetic of the **Gaussian integers**:

$$
\mathbb Z[i].
$$
