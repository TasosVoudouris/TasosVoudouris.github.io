---
title: "Elliptic Curve Mathematics V: Torsion Points, Division by n, and the Nagell–Lutz Theorem"
description: "Finite-order points over algebraic closures, rational torsion, Nagell–Lutz over Q, and how torsion differs in characteristic p."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Elliptic Curve Theory"
- "Number Theory"
- "Abstract Algebra"
tags:
- "torsion-points"
- "nagell-lutz"
- "rational-torsion"
- "n-torsion"
- "elliptic-curves"
difficulty: "Advanced"
status: "Reference"
series: "Elliptic Curve Mathematics"
seriesOrder: 5
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---
For an elliptic curve $E$ and integer $n\ge1$, the $n$-torsion subgroup is
$$
E[n]=\{P\in E(\overline K):[n]P=\mathcal O\}.
$$
The algebraic closure in this definition matters.

## 1. Torsion over characteristic not dividing n

If
$$
\operatorname{char}K\nmid n,
$$
then over an algebraic closure,
$$
E[n]\cong (\mathbb Z/n\mathbb Z)^2.
$$

The uploaded note wrote this as a statement about $E(K)[n]$ for arbitrary $K$. That is too strong: the coordinates of all $n$-torsion points need not lie in the base field.

The rational subgroup is
$$
E(K)[n]=E[n]\cap E(K),
$$
which can be much smaller.

## 2. Characteristic p

When $p=\operatorname{char}K$ divides $n$, the structure changes. In particular, the $p$-torsion distinguishes ordinary and supersingular curves.

Over an algebraic closure of a field of characteristic $p$:

- an ordinary elliptic curve has $E[p](\overline K)\cong\mathbb Z/p\mathbb Z$ as a group of geometric points;
- a supersingular elliptic curve has no nontrivial geometric $p$-torsion points.

The full group-scheme story is richer, but this is the correct point-set statement for the present level.

## 3. Nagell–Lutz theorem

Let
$$
E:y^2=x^3+Ax+B
$$
with $A,B\in\mathbb Z$ and nonzero discriminant. If $P=(x,y)\in E(\mathbb Q)$ is a nontrivial torsion point, then
$$
x,y\in\mathbb Z,
$$
and either
$$
y=0
$$
or
$$
y^2\mid 4A^3+27B^2.
$$

This makes rational torsion searchable for integral short-Weierstrass models.

## 4. Rational torsion over Q

Mazur's theorem completely classifies the possible torsion subgroups of elliptic curves over $\mathbb Q$. The theorem is far deeper than Nagell–Lutz: it restricts the abstract group structures that can occur, not just coordinates of torsion points on one model.

## 5. Why torsion matters computationally

Torsion controls division polynomials, pairings, isogenies, subgroup structure over finite fields, and many parameter-selection questions. It is therefore better treated as core elliptic-curve mathematics than introduced only when a specific attack needs it.
