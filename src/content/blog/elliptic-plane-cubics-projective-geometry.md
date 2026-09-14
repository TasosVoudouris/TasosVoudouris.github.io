---
title: "Elliptic Curve Mathematics I: Plane Cubics, Projective Closure, and Nonsingularity"
description: "Why elliptic curves are smooth projective cubic curves: homogenization, points at infinity, partial derivatives, discriminants, and the geometric setting for the group law."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Algebraic Geometry"
- "Elliptic Curve Theory"
tags:
- "plane-cubics"
- "projective-geometry"
- "weierstrass-form"
- "discriminant"
- "nonsingularity"
difficulty: "Intermediate"
status: "Reference"
series: "Elliptic Curve Mathematics"
seriesOrder: 1
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---
An elliptic curve is not merely a graph that happens to look symmetric. The mathematically robust object is a **smooth projective curve of genus one together with a distinguished rational point**. For most computational work, it is presented by a Weierstrass equation.

## 1. Affine plane cubics

A general affine cubic has equation
$$
F(x,y)=0
$$
where $F$ has total degree $3$.

Over a field of characteristic not equal to $2$ or $3$, a nonsingular elliptic curve can be written in short Weierstrass form
$$
E:y^2=x^3+ax+b.
$$

The affine picture omits the point at infinity needed to make the group law global.

## 2. Projective closure

Introduce homogeneous coordinates $(X:Y:Z)$ and replace
$$
x=X/Z,\qquad y=Y/Z.
$$
Homogenizing gives
$$
Y^2Z=X^3+aXZ^2+bZ^3.
$$

Setting $Z=0$ yields
$$
X=0,
$$
so the projective closure has the unique point
$$
\mathcal O=(0:1:0).
$$
This becomes the identity of the elliptic-curve group.

## 3. Nonsingularity

A projective point is singular when the defining polynomial and all first partial derivatives vanish there.

For short Weierstrass form, nonsingularity is equivalent to
$$
4a^3+27b^2\ne0.
$$
A conventional discriminant is
$$
\Delta=-16(4a^3+27b^2).
$$
The sign and scalar factor vary by convention; the essential condition is $\Delta\ne0$.

## 4. Why singular cubics are different

If the cubic has a node or cusp, its nonsingular points can often be parametrized by a simpler group such as the multiplicative or additive group. This changes the discrete-logarithm problem fundamentally.

That phenomenon belongs in the separate Elliptic Curve Cryptanalysis series. Here the lesson is purely geometric: **smoothness is part of the definition of an elliptic curve**, not a security parameter added afterward.

## 5. Lines and intersection multiplicity

Bézout's theorem predicts that a line and a cubic meet in three points over an algebraic closure, counting multiplicities.

This “third intersection point” is the geometric source of the group law. Tangency handles the repeated-intersection case used for doubling.

## 6. Why projective geometry matters

Without projective closure, vertical lines would appear to have only two affine intersections and the addition rule would need awkward exceptions. In projective space, all lines meet the cubic with the correct total multiplicity, and the point $\mathcal O$ closes the law naturally.
