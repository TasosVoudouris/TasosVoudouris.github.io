---
title: "Elliptic Curve Mathematics III: Why the Group Law Is Associative"
description: "A careful explanation of the hardest group axiom for elliptic curves, from chord-and-tangent geometry to divisors and the Picard group."
pubDate: "2025-05-21"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Algebraic Geometry"
- "Elliptic Curve Theory"
- "Abstract Algebra"
tags:
- "elliptic-curves"
- "associativity"
- "group-law"
- "divisors"
- "picard-group"
difficulty: "Advanced"
status: "Reference"
series: "Elliptic Curve Mathematics"
seriesOrder: 3
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---
The chord-and-tangent rule makes closure, identity, and inverses visually plausible. Associativity is different:
$$
(P+Q)+R=P+(Q+R)
$$
is not obvious from the picture, and a direct coordinate expansion becomes unpleasant very quickly.

## 1. The geometric definition

Fix the point at infinity $\mathcal O$. For points $P$ and $Q$, let the line through them meet the cubic at a third point $R$. Reflect $R$ across the $x$-axis in short Weierstrass form; the result is $P+Q$.

Equivalently, one can express the collinearity relation as
$$
P+Q+R=\mathcal O
$$
whenever $P,Q,R$ lie on a line, counting tangent intersections with multiplicity.

## 2. Why brute-force algebra is possible but unsatisfying

One can substitute the rational addition formulas repeatedly and prove associativity by simplifying both sides. This works on coordinate patches after many exceptional cases are handled, but it hides the reason associativity is true.

The old Sage experiment is therefore retained as symbolic evidence, not as the conceptual proof.

## 3. Divisors

A divisor on a curve is a formal integer combination of points:
$$
D=\sum_P n_P[P].
$$
A rational function $f$ has a divisor
$$
\operatorname{div}(f)=\sum_P \operatorname{ord}_P(f)[P]
$$
recording zeros and poles.

Principal divisors are those arising from rational functions.

## 4. Picard group viewpoint

Degree-zero divisors modulo principal divisors form
$$
\operatorname{Pic}^0(E).
$$
For an elliptic curve with base point $\mathcal O$, the map
$$
P\longmapsto [P]-[\mathcal O]
$$
identifies $E$ with $\operatorname{Pic}^0(E)$.

But $\operatorname{Pic}^0(E)$ is a group by construction: addition is addition of divisor classes. Associativity therefore comes for free from the abelian-group structure of divisor classes.

## 5. Recovering the chord-and-tangent law

If a line intersects $E$ at $P,Q,R$, the line function has a divisor relation that implies
$$
[P]+[Q]+[R]-3[\mathcal O]
$$
is principal. Hence in $\operatorname{Pic}^0(E)$,
$$
([P]-[\mathcal O])+([Q]-[\mathcal O])=-([R]-[\mathcal O]).
$$
This is exactly the geometric addition rule.

## 6. The main lesson

The group law is not an arbitrary formula imposed on a cubic. It is the concrete manifestation of a natural algebraic-geometric group, and associativity is inherited from that deeper structure.
