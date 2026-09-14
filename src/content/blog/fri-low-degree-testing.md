---
title: "FRI: Reed–Solomon Proximity, Folding, and Low-Degree Testing"
description: "Derive the core FRI folding identity, connect polynomial degree to Reed–Solomon proximity, explain Merkle-authenticated oracle rounds and query soundness, and distinguish FRI from a standalone polynomial commitment."
pubDate: "2025-03-05"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Finite Fields"
tags:
  - "fri"
  - "reed-solomon"
  - "low-degree-test"
  - "iopp"
  - "folding"
  - "stark"
difficulty: "Advanced"
status: "Validated"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 11
sourcePath: "experiments/zero-knowledge/fri"
draft: false
---
FRI—**Fast Reed–Solomon Interactive Oracle Proof of Proximity**—solves one of the central problems in transparent polynomial proof systems:

> given oracle access to a large evaluation vector, convince the verifier that it is close to evaluations of a low-degree polynomial.

FRI is therefore a **low-degree proximity test**, not merely a Merkle tree and not, by itself, a complete STARK.

## 1. Polynomial evaluations as a Reed–Solomon codeword

Let $D\subset\mathbb F$ be an evaluation domain of size $N$.

For degree bound $d<N$, the Reed–Solomon code contains vectors

$$
(f(x))_{x\in D}
$$

for polynomials with

$$
\deg f<d.
$$

If a prover claims a vector is a low-degree evaluation table, the verifier wants to reject vectors that are far from every such codeword while reading only a small number of coordinates.

## 2. Why evaluating the whole polynomial defeats succinctness

The verifier could interpolate all $N$ values and inspect the degree directly, but then verification costs $\Theta(N)$ data access/work.

FRI instead recursively reduces the degree/domain while committing to each intermediate oracle.

## 3. Even/odd decomposition

Assume a domain where points naturally pair as $x$ and $-x$.

Any polynomial can be uniquely written

$$
f(X)=f_0(X^2)+Xf_1(X^2),
$$

where $f_0$ contains the even coefficients and $f_1$ the odd coefficients.

At a point $x$,

$$
f(x)=f_0(x^2)+x f_1(x^2),
$$

while

$$
f(-x)=f_0(x^2)-x f_1(x^2).
$$

Therefore

$$
f_0(x^2)=\frac{f(x)+f(-x)}{2}
$$

and

$$
f_1(x^2)=\frac{f(x)-f(-x)}{2x}.
$$

## 4. Random folding

The verifier samples a random challenge $\beta$ and defines a folded polynomial

$$
g(Y)=f_0(Y)+\beta f_1(Y).
$$

If $f$ has degree below roughly $d$, then $g$ has degree below roughly $d/2$.

For $Y=x^2$, the new evaluation can be computed from the pair $f(x),f(-x)$:

$$
g(x^2)
=
\frac{f(x)+f(-x)}{2}
+
\beta\frac{f(x)-f(-x)}{2x}.
$$

This is the algebraic heart of one FRI folding round.

## 5. Domain shrinks with the degree bound

Squaring maps the paired domain to a domain of half the size.

So each round approximately halves:

- the domain size;
- the claimed degree bound.

Repeated folding eventually reaches a tiny polynomial that the verifier can inspect directly.

## 6. Why the random challenge matters

If the prover could choose $\beta$, it might arrange cancellation that hides high-degree structure.

The prover must commit to the current oracle **before** learning the folding challenge.

In a Merkle/Fiat–Shamir implementation:

```text
Merkle root of current layer
    ↓
derive β from transcript
    ↓
compute folded layer
    ↓
commit folded layer
```

This ordering is part of the soundness argument.

## 7. Query phase

After all folding commitments are fixed, the verifier samples random query positions.

For each queried position, the prover opens the related values in consecutive FRI layers together with Merkle paths.

The verifier checks:

1. Merkle authentication;
2. each folding equation;
3. consistency of the index mapping between layers;
4. the final low-degree/base-case condition.

Only logarithmically many layers are traversed.

## 8. Proximity, not exact membership from one query

A single local check cannot prove exact low-degree membership.

FRI soundness is a probabilistic coding-theoretic statement: words sufficiently far from the relevant Reed–Solomon code are rejected with meaningful probability, amplified through queries/round structure.

Security parameters therefore depend on more than "number of FRI rounds." They include:

- code rate / blowup factor;
- query count;
- field/domain structure;
- challenge entropy;
- exact soundness theorem/variant.

## 9. FRI versus FFT

FRI folding resembles FFT-style divide-and-conquer algebra, but the goals differ.

An FFT evaluates/interpolates polynomials efficiently. FRI uses a related recursive structure to produce/check a **proof of proximity to low degree**.

Calling FRI "basically an FFT" misses the coding-theoretic soundness component.

## 10. FRI versus a polynomial commitment

KZG has a direct algebraic commitment/opening interface. FRI is an IOPP.

A practical FRI-based polynomial commitment layer additionally needs:

- a committed evaluation vector, usually via Merkle tree;
- authenticated query openings;
- transcript challenges;
- often batching/masking machinery.

So it is accurate to say "FRI-based polynomial commitment" while remembering that FRI itself is the low-degree testing engine.

## 11. DEEP-FRI

Later work introduced **DEEP-FRI**, which evaluates relations at points outside the original evaluation domain to improve soundness behavior while retaining the efficient folding structure.

This is a reminder that "FRI" names a protocol family with evolving soundness analyses, not one immutable ten-line algorithm.

### Companion experiment

```bash
python experiments/zero-knowledge/fri/fri_folding_toy.py
```

It verifies the even/odd decomposition and one correct folding step over $\mathbb F_{97}$. It deliberately does **not** claim to implement a full FRI prover/verifier.

### Primary reference

E. Ben-Sasson, I. Bentov, Y. Horesh, M. Riabzev, *Fast Reed–Solomon Interactive Oracle Proofs of Proximity*, 2017/2018.
