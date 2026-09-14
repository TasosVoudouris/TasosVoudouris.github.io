---
title: "Linear Algebra Foundations I: Vectors, Matrices, Linear Maps, and Vector Spaces"
description: "The minimum rigorous linear algebra needed before lattices: systems, matrices, vector spaces, linear independence, span, basis, rank, and linear maps."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Linear Algebra"
tags:
- "vectors"
- "matrices"
- "vector-spaces"
- "linear-maps"
- "basis"
- "rank"
difficulty: "Introductory"
status: "Reference"
series: "Linear Algebra Foundations"
seriesOrder: 1
sourcePath: "experiments/mathematics/linear-algebra-lattices"
draft: false
---
Linear algebra turns systems of equations into geometry. Lattice theory then adds an arithmetic restriction: coefficients are forced to be integers rather than arbitrary real or rational scalars.

## 1. Linear systems and matrices

A system
$$
Ax=b
$$
packages many linear equations into a matrix $A$, unknown vector $x$, and target vector $b$.

Elementary row operations preserve the solution set and lead to row-echelon or reduced row-echelon form. The number of pivots is the rank.

## 2. Vectors

For $x=(x_1,\ldots,x_n)$ and $y=(y_1,\ldots,y_n)$,
$$
x+y=(x_1+y_1,\ldots,x_n+y_n),
$$
and for a scalar $c$,
$$
cx=(cx_1,\ldots,cx_n).
$$

The Euclidean inner product is
$$
\langle x,y\rangle=\sum_{i=1}^n x_i y_i,
$$
with norm
$$
\|x\|_2=\sqrt{\langle x,x\rangle}.
$$

Orthogonality means $\langle x,y\rangle=0$.

## 3. Vector spaces

A vector space $V$ over a field $F$ is an abelian group under addition together with scalar multiplication by $F$ satisfying the usual distributive and compatibility laws.

Examples include
$$
F^n,
$$
polynomials of degree at most $d$, matrices of fixed dimensions, and function spaces.

## 4. Span and linear independence

Given vectors $v_1,\dots,v_k$,
$$
\operatorname{span}(v_1,\dots,v_k)
=\left\{\sum_i c_i v_i:c_i\in F\right\}.
$$

They are linearly independent if
$$
\sum_i c_i v_i=0
$$
implies every $c_i=0$.

A **basis** is a linearly independent spanning set. Every vector has a unique coordinate representation in a basis.

## 5. Dimension and rank

All bases of a finite-dimensional vector space have the same number of elements, the dimension.

For a matrix $A$, the row rank and column rank coincide. This common rank measures the dimension of the image of the associated linear map.

## 6. Linear maps

A map $T:V\to W$ is linear if
$$
T(av+bw)=aT(v)+bT(w).
$$

The rank-nullity theorem says
$$
\dim V=\dim\ker T+\dim\operatorname{im}T.
$$

This is the vector-space analogue of the kernel/image philosophy from abstract algebra.

## 7. Why this is only the first layer

A lattice basis is not merely a vector-space basis. Over $\mathbb R$, multiplying a basis vector by $1/2$ is harmless; over a $\mathbb Z$-module, it may leave the lattice. Lattice geometry therefore combines real linear algebra with discrete arithmetic.
