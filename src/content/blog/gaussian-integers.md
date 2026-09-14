---
title: "Computational Number Theory III: Gaussian Integers, Norms, Units, and Euclidean Division"
description: "Arithmetic in Z[i]: conjugation, norm, units, divisibility, Euclidean division, gcds, and the splitting behavior of rational primes."
pubDate: "2025-04-23"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Number Theory"
- "Abstract Algebra"
tags:
- "gaussian-integers"
- "euclidean-domain"
- "norm"
- "sum-of-two-squares"
- "prime-splitting"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 3
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
The Gaussian integers
$$
\mathbb Z[i]=\{a+bi:a,b\in\mathbb Z\}
$$
are the simplest example of enlarging the integers while preserving enough arithmetic structure for a Euclidean algorithm.

## 1. Conjugation and norm

For
$$
z=a+bi,
$$
define
$$
\overline z=a-bi
$$
and
$$
N(z)=z\overline z=a^2+b^2.
$$

The norm is multiplicative:
$$
N(zw)=N(z)N(w).
$$
This turns geometric length into arithmetic information.

## 2. Units

A unit must have norm $1$, so
$$
\mathbb Z[i]^\times=\{1,-1,i,-i\}.
$$
These four associates explain why gcds and factorizations are unique only up to multiplication by a unit.

## 3. Euclidean division

Given $\alpha,\beta\in\mathbb Z[i]$ with $\beta\ne0$, consider
$$
\frac{\alpha}{\beta}=\frac{\alpha\overline\beta}{N(\beta)}\in\mathbb C.
$$
Round the real and imaginary parts to the nearest integers to obtain $q\in\mathbb Z[i]$, and set
$$
r=\alpha-q\beta.
$$
Then one can choose $q$ so that
$$
N(r)<N(\beta).
$$
Therefore $\mathbb Z[i]$ is a Euclidean domain.

The original scratch implementation searched nearby floor/ceiling combinations but compared the wrong norms when choosing the quotient. The companion code now implements the standard nearest-lattice-point division and explicitly verifies the Euclidean remainder inequality.

## 4. gcd and unique factorization

Because $\mathbb Z[i]$ is Euclidean, it is a PID and hence a UFD. The Euclidean algorithm computes Gaussian gcds exactly as over $\mathbb Z$, with the norm as the descent measure.

## 5. Rational primes inside $\mathbb Z[i]$

An odd rational prime $p$ behaves according to $p\bmod4$:

- if $p\equiv1\pmod4$, it splits:
  $$p=\pi\overline\pi;$$
- if $p\equiv3\pmod4$, it remains prime in $\mathbb Z[i]$;
- $2$ ramifies:
  $$2=-i(1+i)^2.$$

The splitting case is equivalent to representing $p$ as a sum of two squares.

## 6. Geometry and arithmetic meet

The Gaussian integers form the square lattice in the complex plane. Their Euclidean algorithm is therefore literally a nearest-point geometric operation, making $\mathbb Z[i]$ a useful bridge between algebraic number theory and lattice geometry.
