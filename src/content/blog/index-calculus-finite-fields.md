---
title: "Discrete Logarithms V: Index Calculus in Finite Fields"
description: "Why finite-field DLPs admit subexponential index-calculus attacks: factor bases, smooth relations, linear algebra, and individual logarithms."
pubDate: "2025-05-21"
updatedDate: '2026-09-13'
topics:
- "Discrete Logarithms"
- "Number Theory"
- "Finite Fields"
- "Cryptanalysis"
tags:
- "index-calculus"
- "discrete-logarithm"
- "factor-base"
- "smoothness"
- "finite-fields"
difficulty: "Advanced"
status: "Reference"
series: "Discrete Logarithm Algorithms"
seriesOrder: 5
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
Generic DLP algorithms such as baby-step giant-step and Pollard rho use only the group operation. In multiplicative finite fields, additional arithmetic structure allows a different strategy: **index calculus**.

## 1. Problem

Let $g$ generate a large subgroup of $\mathbb F_p^\times$. Given
$$
h=g^x,
$$
recover $x$ modulo the group order.

Index calculus works by expressing many field elements as products of small primes or other chosen factor-base elements.

## 2. Factor base

Choose
$$
\mathcal B=\{q_1,\dots,q_m\}
$$
of small primes. A residue $y$ is $\mathcal B$-smooth if an integer representative factors completely over this set:
$$
y=\prod_i q_i^{e_i}.
$$

Smoothness is the scarce resource that drives the algorithm.

## 3. Relation collection

Choose random exponents $k$ and compute
$$
g^k\bmod p.
$$
If the result is factor-base smooth,
$$
g^k\equiv\prod_i q_i^{e_i}\pmod p.
$$
Taking discrete logarithms formally gives the linear relation
$$
k\equiv\sum_i e_i\log_g(q_i)\pmod{p-1}.
$$

Collect enough independent relations to solve for the unknown factor-base logarithms.

## 4. Linear algebra modulo the group order

The relation matrix is solved modulo the relevant subgroup order. If the modulus is composite, careless Gaussian elimination can fail because a pivot may be noninvertible. Implementations typically factor the order or solve modulo prime powers and recombine.

This is one reason a toy implementation that simply calls a generic matrix inverse modulo $p-1$ can be mathematically fragile.

## 5. Individual logarithm

Once the factor-base logs are known, randomize the target:
$$
hg^r.
$$
When this becomes smooth,
$$
hg^r=\prod_iq_i^{e_i},
$$
so
$$
x+r\equiv\sum_ie_i\log_g(q_i)
$$
and hence
$$
x\equiv\sum_ie_i\log_g(q_i)-r.
$$

## 6. Why this differs from ECDLP

The multiplicative group of a finite field has a representation in which elements factor into small algebraic objects. Generic elliptic-curve groups do not provide an analogous notion of factor-base smoothness that yields the same subexponential attack.

This structural difference is a major reason elliptic curves achieve comparable classical security with much smaller group sizes than traditional finite-field DLP systems.

## 7. Algorithmic descendants

Modern finite-field DLP algorithms refine the same philosophy through function fields and number fields. For small characteristic, specialized index-calculus techniques can be even faster; for large prime fields, number-field-sieve methods dominate at cryptographic sizes.
