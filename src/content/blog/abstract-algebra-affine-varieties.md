---
title: "Abstract Algebra VII: From Polynomial Ideals to Affine Varieties and Coordinate Rings"
description: "A first bridge from algebra to algebraic geometry: algebraic sets, vanishing ideals, coordinate rings, and why geometry can be studied through polynomial algebra."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Abstract Algebra"
- "Algebraic Geometry"
tags:
- "affine-varieties"
- "polynomial-ideals"
- "coordinate-rings"
- "algebraic-sets"
- "vanishing-ideals"
difficulty: "Advanced"
status: "Reference"
series: "Abstract Algebra Foundations"
seriesOrder: 7
sourcePath: "experiments/mathematics/abstract-algebra"
draft: false
---
Algebraic geometry begins with a reversal of viewpoint: instead of studying a polynomial only as a symbolic expression, study the geometric set where a collection of polynomials vanishes—and then recover algebra from that set.

This article is intentionally a first bridge, not a substitute for a full algebraic-geometry course.

## 1. Affine space

For a field $K$, affine $n$-space is
$$
\mathbb A^n(K)=K^n.
$$

A polynomial $f\in K[x_1,\dots,x_n]$ defines a subset
$$
V(f)=\{P\in K^n:f(P)=0\}.
$$
For a set of polynomials $S$,
$$
V(S)=\{P:f(P)=0\text{ for every }f\in S\}.
$$
Such sets are called **algebraic sets**.

## 2. Ideals control systems of equations

If $I=(f_1,\dots,f_m)$, then
$$
V(I)=V(f_1,\dots,f_m).
$$
Replacing generators by another generating set of the same ideal does not change the zero set. Thus the right algebraic object is the ideal, not a particular list of equations.

## 3. Vanishing ideals

Given a subset $X\subseteq K^n$, define
$$
I(X)=\{f\in K[x_1,\dots,x_n]:f(P)=0\text{ for all }P\in X\}.
$$
This is an ideal.

The operations
$$
I\mapsto V(I),\qquad X\mapsto I(X)
$$
form the algebra–geometry correspondence at the heart of affine algebraic geometry.

## 4. Coordinate rings

For an algebraic set $X=V(I)$, the **coordinate ring** is
$$
K[X]=K[x_1,\dots,x_n]/I(X).
$$

Two polynomials define the same function on $X$ exactly when their difference vanishes on $X$. The quotient ring records polynomial functions on the geometry without keeping redundant representatives.

## 5. The Nullstellensatz viewpoint

Over an algebraically closed field, Hilbert's Nullstellensatz says that
$$
I(V(I))=\sqrt I,
$$
where $\sqrt I$ is the radical of $I$.

The theorem is much deeper than the definitions above, but it explains why ideals and varieties mirror one another so closely.

## 6. Why projective geometry appears next

Affine plane curves can have awkward behavior “at infinity.” Passing to projective space adds the missing points in a controlled algebraic way. Elliptic curves are naturally smooth projective curves of genus one equipped with a rational base point, so projective geometry is not decoration—it is the setting in which the group law is globally well behaved.
