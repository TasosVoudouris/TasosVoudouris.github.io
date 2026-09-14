---
title: "Lattices & Lattice-Based Cryptography II: SVP, CVP, BDD, SIVP, and Minkowski's Theorems"
description: "The central computational problems in lattice theory, the geometry behind them, uniqueness in bounded-distance decoding, and the Minkowski bounds that connect determinant to short vectors."
pubDate: "2025-05-29"
updatedDate: "2026-09-13"
topics:
- "Mathematical Foundations"
- "Lattice Theory"
- "Lattice Methods"
tags:
- "svp"
- "cvp"
- "bdd"
- "sivp"
- "minkowski"
- "successive-minima"
- "geometry-of-numbers"
difficulty: "Intermediate"
status: "Reviewed"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 2
draft: false
---
A lattice may have infinitely many bases, but its geometric invariants do not depend on which basis we happen to see. Cryptographic lattice problems exploit precisely this mismatch: the input basis can be awkward while the object we want—a short vector, a nearby lattice point, or a set of independent short vectors—is intrinsic to the lattice.

This chapter fixes the definitions that later appear in SIS, LWE, NTRU, Coppersmith-style cryptanalysis, and modern post-quantum constructions.

## 1. The shortest-vector problem

Let $L\subset\mathbb R^n$ be a full-rank lattice. Its first successive minimum is

$$
\lambda_1(L)=\min_{0\neq v\in L}\|v\|_2.
$$

The **Shortest Vector Problem (SVP)** asks for a nonzero $v\in L$ with

$$
\|v\|_2=\lambda_1(L).
$$

![A shortest vector in a lattice](/images/blog/lattices/svpsolution.png)

The approximation version, $\gamma$-SVP, asks for

$$
0\neq v\in L,
\qquad
\|v\|_2\le \gamma(n)\lambda_1(L).
$$

The distinction between exact and approximate SVP matters. Algorithms such as LLL are polynomial-time approximation algorithms; they do **not** solve exact SVP in polynomial time.

## 2. The closest-vector problem

Given a target $t\in\mathbb R^n$, define its distance from the lattice by

$$
\operatorname{dist}(t,L)=\min_{v\in L}\|t-v\|_2.
$$

The **Closest Vector Problem (CVP)** asks for a lattice vector $v$ attaining this minimum.

![Closest-vector geometry](/images/blog/lattices/cvpsolution.png)

Its approximation version asks for a vector satisfying

$$
\|t-v\|_2\le \gamma(n)\operatorname{dist}(t,L).
$$

CVP is the geometric pattern behind many decoding problems: a valid lattice point is perturbed by a small error, and the task is to recover the original point.

## 3. Bounded-distance decoding

The **Bounded-Distance Decoding (BDD)** problem is a promise version of CVP. We are promised that the target is unusually close to a lattice point.

For a parameter $\alpha>0$, the promise is typically written

$$
\operatorname{dist}(t,L)<\alpha\lambda_1(L).
$$

When $\alpha<1/2$, the nearest lattice vector is unique: two distinct lattice points are separated by at least $\lambda_1(L)$, so the radius-$\lambda_1/2$ balls around them cannot overlap.

![BDD as decoding near a lattice point](/images/blog/lattices/bdd.png)

This unique-decoding viewpoint is one of the cleanest geometric ways to think about Learning With Errors: a structured lattice point has been displaced by a small error vector.

## 4. Successive minima and SIVP

The $i$-th successive minimum is

$$
\lambda_i(L)
=
\inf\left\{r>0:
\dim\operatorname{span}(L\cap rB_2^n)\ge i
\right\}.
$$

Thus

$$
\lambda_1(L)\le\lambda_2(L)\le\cdots\le\lambda_n(L).
$$

The **Shortest Independent Vectors Problem (SIVP)** asks for $n$ linearly independent lattice vectors whose maximum norm is as small as possible, or within a chosen approximation factor of $\lambda_n(L)$.

SIVP is important in lattice cryptography because worst-case hardness reductions for average-case problems such as SIS and LWE are often stated in terms of approximate SIVP or GapSVP rather than exact SVP.

## 5. Minkowski's first theorem

Let $K\subset\mathbb R^n$ be convex, centrally symmetric, and measurable. If

$$
\operatorname{vol}(K)>2^n\det(L),
$$

then $K$ contains a nonzero lattice point.

This is **Minkowski's first theorem**. It converts volume into a statement about short vectors.

Taking $K$ to be an Euclidean ball gives an upper bound of the form

$$
\lambda_1(L)
\le
2\left(\frac{\det(L)}{\operatorname{vol}(B_2^n)}\right)^{1/n}.
$$

Using standard estimates for the $n$-ball volume yields the simpler asymptotic message

$$
\lambda_1(L)=O\!\left(\sqrt n\,\det(L)^{1/n}\right).
$$

![Volume and lattice density](/images/blog/lattices/volume.png)

The determinant therefore fixes a natural geometric scale. A lattice of small determinant is dense; a lattice of large determinant is sparse.

## 6. Minkowski's second theorem

Minkowski's second theorem controls the product of the successive minima. With $B_2^n$ the Euclidean unit ball,

$$
\frac{2^n}{n!}\det(L)
\le
\operatorname{vol}(B_2^n)
\prod_{i=1}^n\lambda_i(L)
\le
2^n\det(L).
$$

So the determinant does not merely constrain one short vector; it constrains the geometric scale of an entire independent set.

## 7. The Gaussian heuristic is a heuristic

For a sufficiently random-looking high-dimensional lattice, one often estimates the shortest-vector length by asking when a Euclidean ball should contain roughly one nonzero lattice point:

$$
\frac{\operatorname{vol}(rB_2^n)}{\det(L)}\approx 1.
$$

This gives the familiar estimate

$$
\lambda_1(L)\approx
\sqrt{\frac{n}{2\pi e}}\,\det(L)^{1/n}
$$

up to lower-order effects and convention-dependent constants.

This is the **Gaussian heuristic**, not a theorem. It is nevertheless extremely useful when estimating the quality required from lattice reduction or when comparing an unusually short hidden vector with the typical geometric scale of a lattice.

## 8. Why cryptography cares

These problems recur in different roles:

| Problem | Cryptographic interpretation |
|---|---|
| SVP / approximate SVP | find abnormally short relations or secret vectors |
| CVP | recover a lattice point near a target |
| BDD | decode when the error is promised small |
| SIVP | worst-case hardness foundation in lattice reductions |
| GapSVP | distinguish whether a lattice has very short vectors |

The next chapter studies **lattice reduction**. The crucial point is that a hard problem may be stated independently of the input basis, while algorithms such as LLL and BKZ try to transform that basis into one from which the geometry becomes easier to see.
