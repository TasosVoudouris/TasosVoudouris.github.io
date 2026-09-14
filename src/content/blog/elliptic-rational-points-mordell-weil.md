---
title: "Elliptic Curve Mathematics IV: Rational Points, Heights, Descent, and the Mordell–Weil Theorem"
description: "Rational points on cubic curves, finite generation, heights, descent, rank, and why elliptic curves over Q have both arithmetic structure and unresolved complexity."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Algebraic Geometry"
- "Elliptic Curve Theory"
- "Number Theory"
tags:
- "rational-points"
- "mordell-weil"
- "heights"
- "descent"
- "rank"
difficulty: "Advanced"
status: "Reference"
series: "Elliptic Curve Mathematics"
seriesOrder: 4
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---
Over $\mathbb Q$, an elliptic curve has an abelian group of rational points
$$
E(\mathbb Q).
$$
The remarkable fact is that this infinite arithmetic object is finitely generated.

## 1. From conics to cubics

A conic with one rational point can be parametrized by lines through that point. A cubic behaves differently: a line intersects it in three points, and knowing two rational intersections produces a third.

That geometry is exactly what produces the elliptic-curve group law.

## 2. Mordell–Weil theorem

For an elliptic curve $E$ over a number field $K$,
$$
E(K)
$$
is a finitely generated abelian group.

Over $\mathbb Q$,
$$
E(\mathbb Q)\cong E(\mathbb Q)_{\mathrm{tors}}\oplus\mathbb Z^r.
$$
The integer $r$ is the **rank**.

Finite generation does not mean that finding generators is easy.

## 3. Naive height

For a rational number $x=a/b$ in lowest terms, define a multiplicative height
$$
H(x)=\max(|a|,|b|)
$$
and logarithmic height
$$
h(x)=\log H(x).
$$

For a point $P=(x,y)$, the height of the $x$-coordinate gives a first measure of arithmetic complexity.

## 4. Canonical height

The Néron–Tate canonical height
$$
\hat h(P)
$$
corrects the naive height so that multiplication behaves quadratically:
$$
\hat h([n]P)=n^2\hat h(P).
$$

It vanishes exactly on torsion points and behaves like a positive-definite quadratic form on the free part of $E(\mathbb Q)$.

## 5. Descent

A descent studies the quotient
$$
E(\mathbb Q)/mE(\mathbb Q)
$$
for a small integer $m$, often $2$.

If this quotient can be bounded and heights satisfy suitable growth/finite-search properties, one can prove finite generation and obtain information about the rank.

The uploaded notes correctly emphasized the intuition of infinite descent, but the canonical statement should not suggest that “doubling always makes points simply larger” in a naive coordinate sense. Height functions are the controlled measure that makes the argument work.

## 6. Torsion and rank

The torsion subgroup is finite and can often be determined explicitly. The free rank is subtler and is tied to some of the deepest open questions in arithmetic geometry, including the Birch and Swinnerton-Dyer conjecture.

## 7. Why this matters even in a cryptography site

Cryptographic elliptic curves are usually considered over finite fields, not over $\mathbb Q$. But the rational-point theory explains where the group law comes from, why heights and descent exist, and how elliptic curves sit inside arithmetic geometry rather than being merely fast finite groups.
