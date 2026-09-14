---
title: "Linear Algebra Foundations II: Gram–Schmidt, Orthogonal Projections, Determinants, and Volume"
description: "Orthogonalization, projection coefficients, QR intuition, determinants as volume scaling, and the invariants later reused in lattice theory."
pubDate: "2025-05-29"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Linear Algebra"
tags:
- "gram-schmidt"
- "orthogonalization"
- "determinants"
- "volume"
- "qr-decomposition"
difficulty: "Intermediate"
status: "Reference"
series: "Linear Algebra Foundations"
seriesOrder: 2
sourcePath: "experiments/mathematics/linear-algebra-lattices"
draft: false
---
Lattice reduction depends on a tension between two bases: the original integer basis and an orthogonalized real basis used to measure geometry. Gram–Schmidt is the mechanism that connects them.

## 1. Orthogonal projection

For nonzero $u$, the projection of $v$ onto the line spanned by $u$ is
$$
\operatorname{proj}_u(v)
=\frac{\langle v,u\rangle}{\langle u,u\rangle}u.
$$

The residual
$$
v-\operatorname{proj}_u(v)
$$
is orthogonal to $u$.

## 2. Gram–Schmidt orthogonalization

Given linearly independent vectors $b_1,\dots,b_n$, define
$$
b_1^*=b_1
$$
and
$$
b_i^*=b_i-\sum_{j<i}\mu_{i,j}b_j^*,
\qquad
\mu_{i,j}=\frac{\langle b_i,b_j^*\rangle}{\langle b_j^*,b_j^*\rangle}.
$$

The $b_i^*$ are mutually orthogonal and span the same successive subspaces as the original vectors.

The important warning for lattices is that $b_i^*$ need not lie in the lattice. They are geometric auxiliaries, not usually a new lattice basis.

## 3. Orthonormal bases and QR

Normalizing gives
$$
q_i=\frac{b_i^*}{\|b_i^*\|}.
$$
Collecting the $q_i$ as columns produces the orthogonal factor $Q$ in a QR decomposition
$$
A=QR.
$$

Numerical linear algebra normally uses more stable variants than naive classical Gram–Schmidt, but the exact formula is ideal for mathematical derivations.

## 4. Determinants

For a square matrix $B$, $|\det B|$ is the volume scaling factor of the corresponding linear transformation.

If the columns $b_1,\dots,b_n$ form a basis, then
$$
|\det B|
$$
is the volume of the fundamental parallelepiped
$$
\left\{\sum_i t_i b_i:0\le t_i<1\right\}.
$$

## 5. Determinant under basis change

If $U$ is unimodular,
$$
U\in GL_n(\mathbb Z),\qquad \det U=\pm1,
$$
then
$$
\det(BU)=\det(B)\det(U),
$$
so
$$
|\det(BU)|=|\det B|.
$$

This is why lattice determinant is independent of the chosen integer basis.

## 6. Gram determinant

For linearly independent vectors in $\mathbb R^m$, the squared volume is
$$
\det(B^TB).
$$
Thus
$$
\operatorname{vol}(b_1,\dots,b_n)=\sqrt{\det(B^TB)}.
$$

This form works even when the basis matrix is rectangular.
