---
title: "Linear Algebra Foundations I: Vectors, Matrices, Linear Maps, and Vector Spaces"
description: "The rigorous linear-algebra foundation needed before lattices: systems, vectors, vector spaces, span, linear independence, bases, coordinates, rank, kernels, images, and linear maps."
pubDate: "2025-03-19"
updatedDate: "2026-09-16"
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

Linear algebra turns systems of equations into structure.

A matrix is not merely a rectangular table of numbers. It can represent:

- a system of equations;
- a linear transformation;
- a change of coordinates;
- a collection of vectors;
- a geometric transformation.

The language connecting all of these viewpoints is the language of **vector spaces**.

For lattice theory, this foundation is essential because a lattice lives simultaneously in two worlds:

\[
\boxed{
\text{real linear geometry}
}
\]

and

\[
\boxed{
\text{integer arithmetic}.
}
\]

A lattice basis looks superficially like an ordinary vector-space basis, but the allowed coefficients are different.

In a real vector space:

\[
c_i\in\mathbb R.
\]

In a lattice:

\[
z_i\in\mathbb Z.
\]

That small change produces a fundamentally different object.

This article builds the linear-algebra layer first.

---

## Table of Contents

- [Linear systems and matrices](#linear-systems-and-matrices)
- [Vectors, inner products, and geometry](#vectors-inner-products-and-geometry)
- [Vector spaces and subspaces](#vector-spaces-and-subspaces)
- [Span, independence, basis, and coordinates](#span-independence-basis-and-coordinates)
- [Linear maps and matrix representations](#linear-maps-and-matrix-representations)
- [Rank, kernel, image, and rank-nullity](#rank-kernel-image-and-rank-nullity)
- [From linear algebra to lattices](#from-linear-algebra-to-lattices)
- [A complete worked example](#a-complete-worked-example)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Linear systems and matrices

Consider a system of linear equations:

\[
\begin{aligned}
a_{11}x_1+\cdots+a_{1n}x_n &= b_1,\\
a_{21}x_1+\cdots+a_{2n}x_n &= b_2,\\
&\vdots\\
a_{m1}x_1+\cdots+a_{mn}x_n &= b_m.
\end{aligned}
\]

This can be written compactly as:

\[
\boxed{
Ax=b,
}
\]

where:

\[
A\in F^{m\times n},
\]

\[
x\in F^n,
\]

and:

\[
b\in F^m.
\]

Here \(F\) is a field such as:

\[
\mathbb Q,
\qquad
\mathbb R,
\qquad
\mathbb C,
\qquad
\mathbb F_p.
\]

---

### Matrix-vector multiplication

Let the columns of \(A\) be:

\[
a_1,\ldots,a_n.
\]

Then:

\[
Ax
=
x_1a_1+\cdots+x_na_n.
\]

So the equation:

\[
Ax=b
\]

can be interpreted as asking:

> Can \(b\) be expressed as a linear combination of the columns of \(A\)?

Thus:

\[
\boxed{
Ax=b
\text{ is solvable}
\iff
b\in\operatorname{span}(a_1,\ldots,a_n).
}
\]

This is the first bridge from systems of equations to vector spaces.

---

### Elementary row operations

Gaussian elimination uses three elementary row operations:

1. swap two rows;
2. multiply a row by a nonzero scalar;
3. add a scalar multiple of one row to another.

These operations preserve the solution set of:

\[
Ax=b.
\]

Algebraically, each row operation corresponds to multiplication by an invertible elementary matrix.

Thus row reduction does not randomly modify the problem.

It replaces the system by an equivalent one.

---

### Row-echelon form

After elimination, a matrix can be placed into **row-echelon form** or **reduced row-echelon form**.

The leading nonzero entries identify the **pivot positions**.

The number of pivots is:

\[
\boxed{
\operatorname{rank}(A).
}
\]

This number will later acquire several equivalent interpretations.

---

### Example

Consider:

\[
A=
\begin{pmatrix}
1&2&1\\
2&4&2\\
1&1&0
\end{pmatrix}.
\]

Subtract twice the first row from the second:

\[
R_2\leftarrow R_2-2R_1.
\]

Then:

\[
\begin{pmatrix}
1&2&1\\
0&0&0\\
1&1&0
\end{pmatrix}.
\]

Now:

\[
R_3\leftarrow R_3-R_1,
\]

giving:

\[
\begin{pmatrix}
1&2&1\\
0&0&0\\
0&-1&-1
\end{pmatrix}.
\]

There are two pivot rows.

Therefore:

\[
\boxed{
\operatorname{rank}(A)=2.
}
\]

---

### Homogeneous systems

The homogeneous system:

\[
\boxed{
Ax=0
}
\]

is especially important.

Its solution set is called the **nullspace** or **kernel** of \(A\):

\[
\boxed{
\ker A
=
\{
x\in F^n:
Ax=0
\}.
}
\]

Unlike a general solution set:

\[
Ax=b,
\]

the kernel is always a vector subspace.

---

### Structure of a consistent system

Suppose:

\[
Ax=b
\]

has one solution:

\[
x_0.
\]

Then every other solution has the form:

\[
\boxed{
x=x_0+z,
\qquad
z\in\ker A.
}
\]

Indeed:

\[
A(x_0+z)
=
Ax_0+Az
=
b+0
=
b.
\]

Conversely, if \(x\) and \(x_0\) are both solutions:

\[
A(x-x_0)=0.
\]

Thus:

\[
x-x_0\in\ker A.
\]

So a consistent linear system has solution set:

\[
\boxed{
x_0+\ker A.
}
\]

Geometrically, this is an affine translate of a vector subspace.

---

## Vectors, inner products, and geometry

A vector in:

\[
F^n
\]

has the form:

\[
x=
(x_1,\ldots,x_n).
\]

Vector addition is coordinatewise:

\[
\boxed{
x+y
=
(x_1+y_1,\ldots,x_n+y_n).
}
\]

Scalar multiplication is:

\[
\boxed{
cx
=
(cx_1,\ldots,cx_n).
}
\]

These two operations provide the basic algebraic structure of a vector space.

---

### Euclidean geometry

When:

\[
F=\mathbb R,
\]

we can equip:

\[
\mathbb R^n
\]

with the standard Euclidean inner product:

\[
\boxed{
\langle x,y\rangle
=
\sum_{i=1}^{n}
x_i y_i.
}
\]

The associated Euclidean norm is:

\[
\boxed{
\|x\|_2
=
\sqrt{
\langle x,x\rangle
}
=
\sqrt{
\sum_{i=1}^{n}x_i^2
}.
}
\]

This gives a notion of length.

---

### Orthogonality

Two vectors are orthogonal if:

\[
\boxed{
\langle x,y\rangle=0.
}
\]

For example:

\[
x=(1,1)
\]

and:

\[
y=(1,-1)
\]

satisfy:

\[
\langle x,y\rangle
=
1-1
=
0.
\]

Thus:

\[
x\perp y.
\]

---

### Angle

For nonzero real vectors:

\[
x,y\in\mathbb R^n,
\]

the angle \(\theta\) between them satisfies:

\[
\boxed{
\cos\theta
=
\frac{
\langle x,y\rangle
}{
\|x\|_2\|y\|_2
}.
}
\]

So the inner product simultaneously controls:

- length;
- distance;
- angle;
- orthogonality.

These geometric notions will become central in lattice reduction.

---

### Distance

The Euclidean distance between:

\[
x
\]

and:

\[
y
\]

is:

\[
\boxed{
d(x,y)
=
\|x-y\|_2.
}
\]

Later, lattice problems will ask questions such as:

\[
\text{Which lattice vector is closest to a target?}
\]

and:

\[
\text{Which nonzero lattice vector is shortest?}
\]

Those questions require precisely this geometric layer.

---

### Algebra versus geometry

It is useful to separate two structures.

A vector space needs only:

\[
\boxed{
\text{addition}
+
\text{scalar multiplication}.
}
\]

An inner-product space has additional geometric structure:

\[
\boxed{
\text{vector space}
+
\text{inner product}.
}
\]

Not every vector space comes with a canonical notion of angle or length.

For lattice theory inside:

\[
\mathbb R^n,
\]

the Euclidean inner product usually provides that geometry.

---

## Vector spaces and subspaces

Let:

\[
F
\]

be a field.

A vector space \(V\) over \(F\) consists of:

- an abelian group \((V,+)\);
- scalar multiplication:
  \[
  F\times V\rightarrow V;
  \]
- the standard distributive and compatibility axioms.

The field \(F\) determines which scalars are allowed.

This is important.

The same additive set can behave differently depending on its scalar domain.

---

### Standard examples

The most familiar example is:

\[
\boxed{
F^n.
}
\]

But vectors need not be coordinate tuples.

Other vector spaces include:

\[
\boxed{
F[x]_{\le d},
}
\]

the polynomials of degree at most \(d\);

\[
\boxed{
M_{m\times n}(F),
}
\]

the \(m\times n\) matrices over \(F\);

and many spaces of functions.

The elements are called **vectors** because of their algebraic behavior, not because they necessarily look like arrows.

---

### Polynomial example

Consider:

\[
V
=
\{
a+bx+cx^2:
a,b,c\in\mathbb R
\}.
\]

This is a vector space over:

\[
\mathbb R.
\]

A natural basis is:

\[
\boxed{
1,x,x^2.
}
\]

The polynomial:

\[
3-2x+5x^2
\]

then has coordinate vector:

\[
\boxed{
(3,-2,5).
}
\]

So coordinate vectors are not the vectors themselves.

They are representations relative to a chosen basis.

---

### Subspaces

A subset:

\[
W\subseteq V
\]

is a vector subspace if it is itself a vector space under the inherited operations.

A convenient subspace test is:

\[
\boxed{
u,v\in W,
\quad
a,b\in F
\Longrightarrow
au+bv\in W.
}
\]

In particular, every subspace contains:

\[
0.
\]

---

### Example

Consider:

\[
W=
\{
(x,y,z)\in\mathbb R^3:
x+y+z=0
\}.
\]

If:

\[
u,v\in W,
\]

then:

\[
u_1+u_2+u_3=0
\]

and:

\[
v_1+v_2+v_3=0.
\]

For:

\[
a,b\in\mathbb R,
\]

the coordinate sum of:

\[
au+bv
\]

is:

\[
a(0)+b(0)=0.
\]

Therefore:

\[
W
\]

is a subspace.

In fact:

\[
W
=
\ker
\begin{pmatrix}
1&1&1
\end{pmatrix}.
\]

This anticipates an important principle:

\[
\boxed{
\text{kernels of linear maps are subspaces}.
}
\]

---

## Span, independence, basis, and coordinates

Let:

\[
v_1,\ldots,v_k\in V.
\]

A **linear combination** of these vectors is:

\[
\boxed{
c_1v_1+\cdots+c_kv_k,
\qquad
c_i\in F.
}
\]

---

### Span

The span is:

\[
\boxed{
\operatorname{span}
(v_1,\ldots,v_k)
=
\left\{
\sum_{i=1}^{k}
c_i v_i:
c_i\in F
\right\}.
}
\]

It is the smallest subspace containing:

\[
v_1,\ldots,v_k.
\]

---

### Example

Let:

\[
v_1=
\begin{pmatrix}
1\\
0\\
1
\end{pmatrix},
\qquad
v_2=
\begin{pmatrix}
0\\
1\\
1
\end{pmatrix}.
\]

Then:

\[
av_1+bv_2
=
\begin{pmatrix}
a\\
b\\
a+b
\end{pmatrix}.
\]

Therefore:

\[
\operatorname{span}(v_1,v_2)
=
\left\{
\begin{pmatrix}
a\\
b\\
a+b
\end{pmatrix}
:
a,b\in\mathbb R
\right\}.
\]

This is a plane through the origin in:

\[
\mathbb R^3.
\]

---

### Linear independence

Vectors:

\[
v_1,\ldots,v_k
\]

are **linearly independent** if:

\[
\boxed{
c_1v_1+\cdots+c_kv_k=0
}
\]

implies:

\[
\boxed{
c_1=\cdots=c_k=0.
}
\]

If a nontrivial coefficient choice produces zero, the vectors are linearly dependent.

---

### Example of dependence

Let:

\[
v_1=
\begin{pmatrix}
1\\
2
\end{pmatrix},
\qquad
v_2=
\begin{pmatrix}
2\\
4
\end{pmatrix}.
\]

Then:

\[
v_2=2v_1.
\]

Therefore:

\[
2v_1-v_2=0
\]

is a nontrivial relation.

So the pair is linearly dependent.

---

### Basis

A **basis** of \(V\) is a collection:

\[
\boxed{
B=(v_1,\ldots,v_n)
}
\]

that is simultaneously:

- linearly independent;
- spanning.

Thus every:

\[
v\in V
\]

can be written as:

\[
\boxed{
v
=
c_1v_1+\cdots+c_nv_n.
}
\]

And because the basis vectors are independent, these coefficients are unique.

---

### Why uniqueness follows

Suppose:

\[
v
=
\sum_i c_i v_i
\]

and also:

\[
v
=
\sum_i d_i v_i.
\]

Subtract:

\[
0
=
\sum_i
(c_i-d_i)v_i.
\]

Since the basis is linearly independent:

\[
c_i-d_i=0
\]

for every \(i\).

Hence:

\[
\boxed{
c_i=d_i.
}
\]

---

### Coordinates

Relative to the basis:

\[
B=(v_1,\ldots,v_n),
\]

define:

\[
\boxed{
[v]_B
=
\begin{pmatrix}
c_1\\
\vdots\\
c_n
\end{pmatrix}.
}
\]

This is the coordinate vector of \(v\) in the basis \(B\).

The vector \(v\) is an abstract element of \(V\).

The column:

\[
[v]_B
\]

depends on the chosen basis.

Changing the basis changes the coordinates without changing the underlying vector.

---

### Dimension

All bases of a finite-dimensional vector space contain the same number of vectors.

That number is:

\[
\boxed{
\dim_F V.
}
\]

For example:

\[
\dim_F F^n=n.
\]

Also:

\[
\dim_F F[x]_{\le d}
=
d+1.
\]

And:

\[
\dim_F M_{m\times n}(F)
=
mn.
\]

---

## Linear maps and matrix representations

Let:

\[
V,W
\]

be vector spaces over the same field \(F\).

A map:

\[
T:V\rightarrow W
\]

is **linear** if:

\[
\boxed{
T(av+bw)
=
aT(v)+bT(w)
}
\]

for all:

\[
v,w\in V
\]

and:

\[
a,b\in F.
\]

Equivalent conditions are:

\[
T(v+w)=T(v)+T(w)
\]

and:

\[
T(av)=aT(v).
\]

---

### Immediate consequences

Every linear map satisfies:

\[
\boxed{
T(0)=0.
}
\]

Indeed:

\[
T(0)
=
T(0+0)
=
T(0)+T(0),
\]

so:

\[
T(0)=0.
\]

This gives a quick way to detect some nonlinear maps.

A map sending:

\[
0
\]

to a nonzero vector cannot be linear.

---

### Matrix maps

Every matrix:

\[
A\in F^{m\times n}
\]

defines a linear map:

\[
\boxed{
T_A:F^n\rightarrow F^m
}
\]

by:

\[
\boxed{
T_A(x)=Ax.
}
\]

Linearity follows from matrix arithmetic:

\[
A(ax+by)
=
aAx+bAy.
\]

So matrices are concrete representations of linear transformations.

---

### From a linear map to a matrix

Conversely, suppose:

\[
T:V\rightarrow W
\]

is linear.

Choose bases:

\[
B=(v_1,\ldots,v_n)
\]

for \(V\), and:

\[
C=(w_1,\ldots,w_m)
\]

for \(W\).

The matrix of \(T\) relative to these bases is formed from the coordinate vectors:

\[
[T(v_1)]_C,
\ldots,
[T(v_n)]_C.
\]

Thus:

\[
\boxed{
[T(v)]_C
=
[T]_{C\leftarrow B}
[v]_B.
}
\]

The matrix depends on the selected bases.

The linear map itself does not.

This distinction becomes very important later when we change lattice bases.

---

### Example

Define:

\[
T:\mathbb R^2\rightarrow\mathbb R^2
\]

by:

\[
T(x,y)
=
(2x+y,x-y).
\]

Using the standard basis:

\[
e_1=(1,0),
\qquad
e_2=(0,1),
\]

we have:

\[
T(e_1)
=
(2,1),
\]

and:

\[
T(e_2)
=
(1,-1).
\]

Therefore:

\[
\boxed{
[T]
=
\begin{pmatrix}
2&1\\
1&-1
\end{pmatrix}.
}
\]

And:

\[
T(x,y)
=
\begin{pmatrix}
2&1\\
1&-1
\end{pmatrix}
\begin{pmatrix}
x\\
y
\end{pmatrix}.
\]

---

## Rank, kernel, image, and rank-nullity

Given:

\[
T:V\rightarrow W,
\]

two subspaces capture much of the map's structure.

The **kernel** is:

\[
\boxed{
\ker T
=
\{
v\in V:
T(v)=0
\}.
}
\]

The **image** is:

\[
\boxed{
\operatorname{im}T
=
\{
T(v):
v\in V
\}.
}
\]

---

### Kernel

The kernel measures which directions collapse to zero.

If:

\[
\ker T=\{0\},
\]

then:

\[
T
\]

is injective.

Indeed, if:

\[
T(v)=T(w),
\]

then:

\[
T(v-w)=0.
\]

So:

\[
v-w\in\ker T.
\]

If the kernel is trivial:

\[
v=w.
\]

Thus:

\[
\boxed{
T\text{ injective}
\iff
\ker T=\{0\}.
}
\]

---

### Image

The image measures which vectors in \(W\) are actually reached.

The map is surjective if:

\[
\boxed{
\operatorname{im}T=W.
}
\]

---

### Rank

The rank of \(T\) is:

\[
\boxed{
\operatorname{rank}(T)
=
\dim\operatorname{im}T.
}
\]

For a matrix:

\[
A,
\]

this agrees with:

- the number of pivots;
- the dimension of the column space;
- the dimension of the row space.

Therefore:

\[
\boxed{
\text{row rank}
=
\text{column rank}.
}
\]

---

### Rank-nullity theorem

If:

\[
V
\]

is finite-dimensional, then:

\[
\boxed{
\dim V
=
\dim\ker T
+
\dim\operatorname{im}T.
}
\]

Equivalently:

\[
\boxed{
\dim V
=
\operatorname{nullity}(T)
+
\operatorname{rank}(T).
}
\]

This is the **Rank-Nullity Theorem**.

---

### Matrix version

For:

\[
A\in F^{m\times n},
\]

the associated map has domain:

\[
F^n.
\]

Therefore:

\[
\boxed{
n
=
\operatorname{nullity}(A)
+
\operatorname{rank}(A).
}
\]

---

### Example

Consider:

\[
A=
\begin{pmatrix}
1&2&3\\
2&4&6
\end{pmatrix}.
\]

The second row is twice the first, so:

\[
\operatorname{rank}(A)=1.
\]

Since the domain is:

\[
\mathbb R^3,
\]

rank-nullity gives:

\[
3
=
\dim\ker A+1.
\]

Hence:

\[
\boxed{
\dim\ker A=2.
}
\]

We obtained the dimension of the solution space without explicitly solving the entire system.

---

### The algebraic connection

This is the vector-space version of a much broader pattern already seen in abstract algebra:

\[
\boxed{
\text{object}
\rightarrow
\ker T
\rightarrow
\operatorname{im}T.
}
\]

For groups we had the First Isomorphism Theorem.

For vector spaces we have:

\[
\boxed{
V/\ker T
\cong
\operatorname{im}T.
}
\]

Taking dimensions gives:

\[
\dim V-\dim\ker T
=
\dim\operatorname{im}T,
\]

which is exactly rank-nullity.

So rank-nullity is not an isolated matrix identity.

It is the dimension-counting shadow of the quotient/kernel philosophy of algebra.

---

## From linear algebra to lattices

We now have the ordinary vector-space picture.

Let:

\[
b_1,\ldots,b_k
\in
\mathbb R^n
\]

be linearly independent.

Their real span is:

\[
\boxed{
\operatorname{span}_{\mathbb R}
(b_1,\ldots,b_k)
=
\left\{
\sum_{i=1}^{k}
c_i b_i:
c_i\in\mathbb R
\right\}.
}
\]

This is a continuous \(k\)-dimensional subspace.

A lattice generated by the same vectors is:

\[
\boxed{
L
=
\left\{
\sum_{i=1}^{k}
z_i b_i:
z_i\in\mathbb Z
\right\}.
}
\]

The only visible change is:

\[
\mathbb R
\longrightarrow
\mathbb Z.
\]

But the mathematical consequences are enormous.

---

### A simple example

Take:

\[
b_1=
\begin{pmatrix}
1\\
0
\end{pmatrix},
\qquad
b_2=
\begin{pmatrix}
0\\
1
\end{pmatrix}.
\]

Their real span is:

\[
\operatorname{span}_{\mathbb R}(b_1,b_2)
=
\mathbb R^2.
\]

Every point:

\[
(x,y)\in\mathbb R^2
\]

is allowed.

Their integer span is:

\[
\operatorname{span}_{\mathbb Z}(b_1,b_2)
=
\mathbb Z^2.
\]

Now only discrete points:

\[
(m,n),
\qquad
m,n\in\mathbb Z,
\]

are allowed.

Thus:

\[
\boxed{
\mathbb R^2
}
\]

is continuous, while:

\[
\boxed{
\mathbb Z^2
}
\]

is discrete.

---

### Why division by two matters

In a real vector space, if:

\[
v\in V,
\]

then:

\[
\frac12v\in V.
\]

This follows because:

\[
\frac12\in\mathbb R.
\]

But suppose:

\[
L=\mathbb Z v.
\]

Then:

\[
L
=
\{
zv:
z\in\mathbb Z
\}.
\]

In general:

\[
\frac12v\notin L.
\]

So lattices are not vector spaces over:

\[
\mathbb R
\]

or:

\[
\mathbb Q.
\]

They are naturally:

\[
\boxed{
\mathbb Z\text{-modules}.
}
\]

This is exactly the bridge to the module theory developed in the Abstract Algebra Foundations series.

---

### Vector-space basis versus lattice basis

Suppose:

\[
B=(b_1,\ldots,b_n)
\]

is a basis of:

\[
\mathbb R^n.
\]

Then replacing:

\[
b_1
\]

by:

\[
2b_1
\]

still produces a real vector-space basis.

Indeed:

\[
\frac12
\]

is an allowed scalar.

But the corresponding integer spans are different:

\[
\mathbb Zb_1+\cdots+\mathbb Zb_n
\]

and:

\[
2\mathbb Zb_1+\mathbb Zb_2+\cdots+\mathbb Zb_n.
\]

The second lattice contains only even multiples in the \(b_1\) direction.

So:

\[
\boxed{
\text{same real span}
\not\Rightarrow
\text{same lattice}.
}
\]

This is the fundamental distinction to carry into lattice theory.

---

### Basis matrices

If:

\[
b_1,\ldots,b_k
\in\mathbb R^n,
\]

we can place them as columns of a matrix:

\[
\boxed{
B=
\begin{pmatrix}
|&&|\\
b_1&\cdots&b_k\\
|&&|
\end{pmatrix}.
}
\]

Then the real span is:

\[
\boxed{
\{
Bx:
x\in\mathbb R^k
\},
}
\]

while the lattice is:

\[
\boxed{
L(B)
=
\{
Bz:
z\in\mathbb Z^k
\}.
}
\]

This compact notation will be central in the next article.

---

### Two levels of structure

A lattice therefore carries two interacting structures.

Its ambient geometry comes from:

\[
\boxed{
\mathbb R^n
}
\]

with:

- inner products;
- lengths;
- angles;
- orthogonality.

Its arithmetic comes from:

\[
\boxed{
\mathbb Z^k
}
\]

with:

- integer coefficients;
- divisibility;
- discrete structure;
- restricted basis transformations.

This is why lattice theory cannot be reduced to ordinary linear algebra.

It is:

\[
\boxed{
\text{linear algebra}
+
\text{integer arithmetic}.
}
\]

---

## A complete worked example

Consider:

\[
v_1=
\begin{pmatrix}
1\\
1\\
0
\end{pmatrix},
\qquad
v_2=
\begin{pmatrix}
1\\
0\\
1
\end{pmatrix}.
\]

Form the matrix:

\[
A=
\begin{pmatrix}
1&1\\
1&0\\
0&1
\end{pmatrix}.
\]

---

### Independence

Suppose:

\[
c_1v_1+c_2v_2=0.
\]

Then:

\[
\begin{pmatrix}
c_1+c_2\\
c_1\\
c_2
\end{pmatrix}
=
\begin{pmatrix}
0\\
0\\
0
\end{pmatrix}.
\]

Therefore:

\[
c_1=0
\]

and:

\[
c_2=0.
\]

So:

\[
\boxed{
v_1,v_2
\text{ are linearly independent}.
}
\]

---

### Span

Their real span is:

\[
\left\{
\begin{pmatrix}
a+b\\
a\\
b
\end{pmatrix}
:
a,b\in\mathbb R
\right\}.
\]

The coordinates satisfy:

\[
x_1=x_2+x_3.
\]

Thus the span is the plane:

\[
\boxed{
x_1-x_2-x_3=0.
}
\]

Its dimension is:

\[
2.
\]

---

### Rank

Since the two columns are independent:

\[
\boxed{
\operatorname{rank}(A)=2.
}
\]

---

### Associated lattice

Now restrict the coefficients to integers:

\[
\boxed{
L
=
\{
z_1v_1+z_2v_2:
z_1,z_2\in\mathbb Z
\}.
}
\]

Equivalently:

\[
L
=
\left\{
\begin{pmatrix}
z_1+z_2\\
z_1\\
z_2
\end{pmatrix}
:
z_1,z_2\in\mathbb Z
\right\}.
\]

The real span is still the same plane.

But the lattice consists only of discrete integer combinations inside that plane.

So:

\[
\boxed{
\operatorname{span}_{\mathbb R}(L)
}
\]

is continuous, whereas:

\[
\boxed{
L
}
\]

itself is discrete.

That distinction is exactly where lattice theory begins.

---

## The structural picture

The article started with:

\[
\boxed{
Ax=b.
}
\]

The columns of \(A\) turned this into a spanning problem:

\[
b\in\operatorname{span}
(a_1,\ldots,a_n).
\]

This led to vector spaces and bases:

\[
\boxed{
v
=
\sum_i c_i v_i.
}
\]

Linear maps then generalized matrix multiplication:

\[
\boxed{
T:V\rightarrow W.
}
\]

Their two central subspaces are:

\[
\boxed{
\ker T
}
\]

and:

\[
\boxed{
\operatorname{im}T.
}
\]

Rank-nullity connects them:

\[
\boxed{
\dim V
=
\dim\ker T
+
\dim\operatorname{im}T.
}
\]

Finally, replacing:

\[
c_i\in\mathbb R
\]

with:

\[
z_i\in\mathbb Z
\]

changes a continuous vector space into a discrete lattice:

\[
\boxed{
L(B)
=
\{
Bz:
z\in\mathbb Z^k
\}.
}
\]

So the conceptual chain is:

\[
\boxed{
\text{systems}
\rightarrow
\text{vectors}
\rightarrow
\text{vector spaces}
\rightarrow
\text{bases}
\rightarrow
\text{linear maps}
\rightarrow
\text{rank}
\rightarrow
\text{lattices}.
}
\]

---

## Practice and checkpoint

### Exercise 1 — Matrix form

Write the system:

\[
\begin{aligned}
2x+y-z&=3,\\
x+3y+2z&=7
\end{aligned}
\]

as:

\[
Ax=b.
\]

Identify the columns of \(A\).

---

### Exercise 2 — Span

Determine whether:

\[
\begin{pmatrix}
3\\
5
\end{pmatrix}
\]

belongs to:

\[
\operatorname{span}
\left(
\begin{pmatrix}
1\\
1
\end{pmatrix},
\begin{pmatrix}
1\\
2
\end{pmatrix}
\right).
\]

---

### Exercise 3 — Inner product

Let:

\[
x=(1,2,-1),
\]

\[
y=(2,-1,0).
\]

Compute:

\[
\langle x,y\rangle,
\]

\[
\|x\|_2,
\]

and:

\[
\|y\|_2.
\]

Are the vectors orthogonal?

---

### Exercise 4 — Subspace test

Determine whether:

\[
W=
\{
(x,y)\in\mathbb R^2:
x+y=1
\}
\]

is a vector subspace.

What simple condition fails?

---

### Exercise 5 — Linear independence

Determine whether:

\[
(1,0,1),
\qquad
(0,1,1),
\qquad
(1,1,2)
\]

are linearly independent.

---

### Exercise 6 — Basis coordinates

Let:

\[
B=
\left(
\begin{pmatrix}
1\\
1
\end{pmatrix},
\begin{pmatrix}
1\\
-1
\end{pmatrix}
\right).
\]

Find:

\[
[v]_B
\]

for:

\[
v=
\begin{pmatrix}
4\\
2
\end{pmatrix}.
\]

---

### Exercise 7 — Matrix of a linear map

Let:

\[
T(x,y)
=
(x+2y,3x-y).
\]

Find its matrix relative to the standard basis.

---

### Exercise 8 — Kernel and image

For:

\[
A=
\begin{pmatrix}
1&2&3\\
2&4&6
\end{pmatrix},
\]

compute:

\[
\operatorname{rank}(A).
\]

Then use rank-nullity to determine:

\[
\dim\ker A.
\]

---

### Exercise 9 — Solution structure

Suppose:

\[
Ax=b
\]

has solution:

\[
x_0.
\]

Prove that every solution is of the form:

\[
x_0+z
\]

with:

\[
z\in\ker A.
\]

---

### Exercise 10 — Real span versus integer span

Let:

\[
v=
\begin{pmatrix}
2\\
0
\end{pmatrix}.
\]

Compare:

\[
\operatorname{span}_{\mathbb R}(v)
\]

with:

\[
\operatorname{span}_{\mathbb Z}(v).
\]

Is:

\[
(1,0)
\]

contained in either set?

---

### Exercise 11 — Different lattice

Compare the two bases:

\[
B_1=
\left(
\begin{pmatrix}
1\\
0
\end{pmatrix},
\begin{pmatrix}
0\\
1
\end{pmatrix}
\right)
\]

and:

\[
B_2=
\left(
\begin{pmatrix}
2\\
0
\end{pmatrix},
\begin{pmatrix}
0\\
1
\end{pmatrix}
\right).
\]

Do they span the same real vector space?

Do they generate the same lattice?

Explain the difference.

---

### Reader checkpoint

You should now be able to explain:

1. How a system of linear equations becomes:
   \[
   Ax=b.
   \]
2. Why:
   \[
   Ax=b
   \]
   is a column-span problem.
3. Why elementary row operations preserve the solution set.
4. What matrix rank measures.
5. What the kernel of a homogeneous system is.
6. Why a consistent solution set has the form:
   \[
   x_0+\ker A.
   \]
7. How vectors are added and scaled.
8. What the Euclidean inner product measures.
9. How norm, distance, and orthogonality arise from an inner product.
10. What a vector space over a field is.
11. What a vector subspace is.
12. What span means.
13. What linear independence means.
14. Why a basis gives unique coordinates.
15. What dimension means.
16. What a linear map is.
17. How a matrix represents a linear map once bases are chosen.
18. Why the matrix representation depends on the basis.
19. What the kernel and image of a linear map are.
20. Why:
    \[
    T\text{ injective}
    \iff
    \ker T=\{0\}.
    \]
21. What rank-nullity says.
22. Why row rank equals column rank.
23. Why:
    \[
    V/\ker T
    \cong
    \operatorname{im}T
    \]
    is the structural origin of rank-nullity.
24. Why:
    \[
    \operatorname{span}_{\mathbb R}
    \]
    and:
    \[
    \operatorname{span}_{\mathbb Z}
    \]
    are fundamentally different.
25. Why two bases can span the same real space while generating different lattices.
26. Why lattice theory combines:
    \[
    \text{real geometry}
    \]
    with:
    \[
    \text{integer arithmetic}.
    \]

Linear algebra gives us the continuous geometry.

The next step is to impose discreteness.

---

## References and further reading

**Gilbert Strang**,  
*Introduction to Linear Algebra.*

A highly intuitive route from systems of equations to vector spaces, bases, orthogonality, and linear transformations.

**Sheldon Axler**,  
*Linear Algebra Done Right.*

A more structural treatment emphasizing vector spaces and linear maps rather than matrix manipulation alone.

**Steven Roman**,  
*Advanced Linear Algebra.*

A useful deeper reference for linear maps, quotient spaces, duality, and structural linear algebra.

**David C. Lay, Steven R. Lay, and Judi J. McDonald**,  
*Linear Algebra and Its Applications.*

A computationally oriented introduction with extensive treatment of row reduction, matrix representations, and applications.

**Daniele Micciancio and Shafi Goldwasser**,  
*Complexity of Lattice Problems: A Cryptographic Perspective.*

A natural next reference once ordinary vector-space structure is replaced by discrete integer lattices.

---

## Next

Linear algebra gives us:

\[
\boxed{
\operatorname{span}_{\mathbb R}
(b_1,\ldots,b_k).
}
\]

Lattice theory changes the coefficient domain:

\[
\boxed{
\mathbb R
\longrightarrow
\mathbb Z.
}
\]

Instead of:

\[
\sum_i c_i b_i,
\qquad
c_i\in\mathbb R,
\]

we consider:

\[
\boxed{
\sum_i z_i b_i,
\qquad
z_i\in\mathbb Z.
}
\]

That produces a discrete geometric object.

The second and final article of this short foundation series will develop the additional linear-algebra machinery needed to understand that geometry: basis matrices, Gram matrices, orthogonalization, projections, determinants, volumes, and the effect of changing a basis.
