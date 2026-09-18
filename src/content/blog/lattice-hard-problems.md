---
title: "Lattices & Lattice-Based Cryptography II: SVP, CVP, BDD, SIVP, and Minkowski's Theorems"
description: "The central computational problems in lattice theory, uniqueness in bounded-distance decoding, successive minima, GapSVP, Minkowski's theorems, and the Gaussian heuristic."
pubDate: "2025-05-29"
updatedDate: "2026-09-16"
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

A lattice may have infinitely many bases, but its geometric invariants do not depend on which basis happens to be given.

This creates one of the central tensions of computational lattice theory.

The input may be an awkward basis:

\[
B=(b_1,\ldots,b_n),
\]

while the object we want is intrinsic to the lattice:

- the shortest nonzero vector;
- the lattice point nearest to a target;
- the unique lattice point inside a sufficiently small decoding region;
- several linearly independent short vectors.

These lead to the canonical problems:

\[
\boxed{
\text{SVP},
\qquad
\text{CVP},
\qquad
\text{BDD},
\qquad
\text{SIVP}.
}
\]

At the same time, the geometry of numbers gives existence theorems.

Minkowski's theorems tell us that sufficiently short lattice vectors **must exist** as a function of:

\[
\det(L).
\]

They do not automatically tell us how to find them efficiently.

That distinction:

\[
\boxed{
\text{existence}
\neq
\text{efficient computation}
}
\]

is one of the fundamental themes of lattice-based cryptography.

---

## Table of Contents

- [Shortest and closest vectors](#shortest-and-closest-vectors)
- [Bounded-distance decoding](#bounded-distance-decoding)
- [Successive minima, SIVP, and GapSVP](#successive-minima-sivp-and-gapsvp)
- [Minkowski’s first theorem](#minkowskis-first-theorem)
- [Minkowski’s second theorem](#minkowskis-second-theorem)
- [The Gaussian heuristic](#the-gaussian-heuristic)
- [Why these problems matter in cryptography](#why-these-problems-matter-in-cryptography)
- [A complete geometric example](#a-complete-geometric-example)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Shortest and closest vectors

Let:

\[
L\subseteq\mathbb R^m
\]

be a rank-\(n\) lattice.

Its first successive minimum is:

\[
\boxed{
\lambda_1(L)
=
\min_{
v\in L\setminus\{0\}
}
\|v\|_2.
}
\]

Because a lattice is discrete, this minimum is attained.

---

### The Shortest Vector Problem

The **Shortest Vector Problem (SVP)** asks:

> Find a nonzero lattice vector having minimum Euclidean norm.

Formally, find:

\[
\boxed{
v\in L\setminus\{0\}
}
\]

such that:

\[
\boxed{
\|v\|_2
=
\lambda_1(L).
}
\]

![A shortest vector in a lattice](/images/blog/lattices/svpsolution.png)

The important point is that SVP concerns the lattice itself.

It does **not** ask for the shortest vector appearing in the supplied basis.

If:

\[
B=(b_1,\ldots,b_n),
\]

then certainly:

\[
\lambda_1(L)
\le
\min_i\|b_i\|_2,
\]

but the inequality can be strict.

A much shorter vector may be hidden inside an integer combination:

\[
z_1b_1+\cdots+z_nb_n.
\]

---

### Approximate SVP

Exact shortest-vector recovery is often stronger than what an algorithm or cryptographic reduction requires.

For an approximation factor:

\[
\gamma(n)\ge1,
\]

the problem:

\[
\gamma\text{-SVP}
\]

asks for:

\[
0\neq v\in L
\]

such that:

\[
\boxed{
\|v\|_2
\le
\gamma(n)\lambda_1(L).
}
\]

Thus:

\[
\gamma=1
\]

corresponds to exact SVP.

Increasing \(\gamma\) permits longer output vectors.

Approximation factors matter enormously in lattice cryptography: two results that both mention "SVP" may concern very different computational problems if their approximation factors differ.

---

### The Closest Vector Problem

SVP places the geometric reference point at the origin.

CVP introduces an arbitrary target.

For:

\[
t\in\mathbb R^m,
\]

define:

\[
\boxed{
\operatorname{dist}(t,L)
=
\min_{v\in L}
\|t-v\|_2.
}
\]

The **Closest Vector Problem (CVP)** asks for a lattice vector:

\[
v\in L
\]

satisfying:

\[
\boxed{
\|t-v\|_2
=
\operatorname{dist}(t,L).
}
\]

![Closest-vector geometry](/images/blog/lattices/cvpsolution.png)

If the target has a component orthogonal to:

\[
V_L=\operatorname{span}_{\mathbb R}(L),
\]

that component is shared by the distance to every lattice point.

So conceptually one may project the target into \(V_L\) and study the intrinsic problem there.

---

### Approximate CVP

The approximation version asks for:

\[
v\in L
\]

such that:

\[
\boxed{
\|t-v\|_2
\le
\gamma(n)
\operatorname{dist}(t,L).
}
\]

As with SVP, exact and approximate formulations must not be conflated.

---

### SVP and CVP are geometrically different

SVP asks:

\[
\boxed{
\text{How close does }L\setminus\{0\}
\text{ come to the origin?}
}
\]

CVP asks:

\[
\boxed{
\text{How close does }L
\text{ come to an arbitrary target }t?
}
\]

The problems share lattice geometry, but their computational structures are different.

---

### Packing radius

Since any two distinct lattice vectors:

\[
u,v\in L
\]

satisfy:

\[
u-v\in L\setminus\{0\},
\]

we have:

\[
\|u-v\|_2
\ge
\lambda_1(L).
\]

Therefore open balls of radius:

\[
\boxed{
r_{\mathrm{pack}}(L)
=
\frac{\lambda_1(L)}{2}
}
\]

centered at lattice points do not overlap.

This is the **packing radius**.

It is exactly the geometric scale that will define unique bounded-distance decoding.

---

## Bounded-distance decoding

The **Bounded-Distance Decoding problem (BDD)** is a promise version of CVP.

We are not given an arbitrary target.

Instead, we are promised that the target lies unusually close to a lattice point.

For a parameter:

\[
\alpha>0,
\]

an \(\alpha\)-BDD instance satisfies:

\[
\boxed{
\operatorname{dist}(t,L)
<
\alpha\lambda_1(L).
}
\]

The task is to recover the corresponding closest lattice vector.

---

### Why the threshold \(1/2\) matters

Suppose:

\[
\alpha<\frac12.
\]

Assume two distinct lattice vectors:

\[
u,v\in L
\]

both satisfy:

\[
\|t-u\|_2
<
\frac{\lambda_1(L)}{2}
\]

and:

\[
\|t-v\|_2
<
\frac{\lambda_1(L)}{2}.
\]

By the triangle inequality:

\[
\begin{aligned}
\|u-v\|_2
&\le
\|u-t\|_2
+
\|t-v\|_2
\\
&<
\lambda_1(L).
\end{aligned}
\]

But:

\[
u-v\in L\setminus\{0\},
\]

so by definition:

\[
\|u-v\|_2
\ge
\lambda_1(L).
\]

Contradiction.

Therefore:

\[
\boxed{
\operatorname{dist}(t,L)
<
\frac{\lambda_1(L)}{2}
}
\]

guarantees a **unique** closest lattice point.

---

### Geometric picture

The balls:

\[
B\left(
v,
\frac{\lambda_1(L)}{2}
\right),
\qquad
v\in L,
\]

are disjoint.

Thus if the target lies inside one of these balls, its associated lattice center is unambiguous.

![BDD as decoding near a lattice point](/images/blog/lattices/bdd.png)

This is why BDD is naturally interpreted as a decoding problem.

A lattice point:

\[
v
\]

is perturbed by an error:

\[
e,
\]

giving:

\[
\boxed{
t=v+e.
}
\]

If:

\[
\|e\|_2
<
\frac{\lambda_1(L)}{2},
\]

then \(v\) is the unique nearest lattice vector.

---

### CVP versus BDD

CVP makes no closeness promise:

\[
t
\]

may lie anywhere.

BDD gives additional information:

\[
\boxed{
t\text{ lies inside a small decoding region around some lattice point}.
}
\]

This promise can dramatically change the computational problem.

---

### BDD and LWE

BDD provides an important geometric lens for understanding lattice cryptography.

Very roughly, many lattice constructions involve:

\[
\boxed{
\text{structured linear information}
+
\text{small error}.
}
\]

After an appropriate lattice embedding or reduction, recovering the hidden structure may become related to decoding a nearby lattice point.

This connection is important in the theory of Learning With Errors.

However, an ordinary LWE instance should not be identified naively with an arbitrary Euclidean BDD instance.

The exact relationship depends on:

- the lattice representation;
- whether one uses the primal or dual viewpoint;
- the modulus;
- the error distribution;
- the reduction being considered.

We will build those connections explicitly when we reach LWE.

---

## Successive minima, SIVP, and GapSVP

The shortest vector measures only one direction.

To describe the geometry of an entire rank-\(n\) lattice, we use the **successive minima**.

Let:

\[
B_2^m
=
\{
x\in\mathbb R^m:
\|x\|_2\le1
\}.
\]

Define:

\[
\boxed{
\lambda_i(L)
=
\inf
\left\{
r>0:
\dim
\operatorname{span}_{\mathbb R}
\left(
L\cap rB_2^m
\right)
\ge i
\right\}.
}
\]

For a lattice the relevant minima are attained.

Thus \(\lambda_i(L)\) is the smallest radius containing at least:

\[
i
\]

linearly independent lattice vectors.

---

### The successive-minima profile

We always have:

\[
\boxed{
\lambda_1(L)
\le
\lambda_2(L)
\le
\cdots
\le
\lambda_n(L).
}
\]

The first minimum gives a shortest nonzero vector.

The final minimum:

\[
\lambda_n(L)
\]

gives the smallest radius within which one can find \(n\) linearly independent lattice vectors.

These vectors need not form a lattice basis.

They may generate a proper finite-index sublattice.

That distinction from Part I remains important.

---

### Example

For:

\[
L=\mathbb Z^2,
\]

we have:

\[
\lambda_1(L)=1
\]

because:

\[
(1,0)
\]

is a shortest nonzero vector.

We also have:

\[
\lambda_2(L)=1
\]

because:

\[
(1,0),
\qquad
(0,1)
\]

are linearly independent and both have norm \(1\).

Thus:

\[
\boxed{
\lambda_1(\mathbb Z^2)
=
\lambda_2(\mathbb Z^2)
=
1.
}
\]

---

### Shortest Independent Vectors Problem

The **Shortest Independent Vectors Problem (SIVP)** asks for \(n\) linearly independent lattice vectors:

\[
v_1,\ldots,v_n
\]

whose maximum length is as small as possible.

In approximation form, \(\gamma\)-SIVP asks for:

\[
\boxed{
v_1,\ldots,v_n\in L
}
\]

linearly independent and satisfying:

\[
\boxed{
\max_i\|v_i\|_2
\le
\gamma(n)\lambda_n(L).
}
\]

Again:

\[
\gamma=1
\]

is the exact version.

---

### Why SIVP differs from finding a short basis

SIVP asks only for linearly independent vectors.

It does not require:

\[
\mathbb Z v_1+\cdots+\mathbb Z v_n=L.
\]

Therefore an SIVP solution need not be a lattice basis.

This distinction becomes important whenever one passes between:

\[
\boxed{
\text{short independent vectors}
}
\]

and:

\[
\boxed{
\text{short generating bases}.
}
\]

---

### GapSVP

Many cryptographic hardness reductions use a decision problem rather than search SVP.

For:

\[
\gamma\ge1,
\]

the **Gap Shortest Vector Problem**, or \(\gamma\)-GapSVP, is a promise problem.

Given a lattice \(L\) and a threshold \(d>0\), distinguish between:

\[
\boxed{
\lambda_1(L)\le d
}
\]

and:

\[
\boxed{
\lambda_1(L)>\gamma d.
}
\]

Inputs satisfying neither condition are outside the promise.

Thus GapSVP does not ask us to output a vector.

It asks us to distinguish between two possible geometric regimes.

---

### Search versus decision

This gives an important taxonomy:

\[
\boxed{
\text{SVP}
=
\text{search}
}
\]

while:

\[
\boxed{
\text{GapSVP}
=
\text{decision under a promise}.
}
\]

Likewise, cryptographic reductions can depend on:

- approximate SVP;
- approximate SIVP;
- GapSVP;
- BDD;

with specific approximation parameters.

The exact statement of a reduction therefore matters.

It is not enough to say merely:

> "LWE reduces to a hard lattice problem."

The actual lattice problem and approximation regime must be specified.

---

## Minkowski's first theorem

The first major theorem of the geometry of numbers connects:

\[
\boxed{
\text{volume}
}
\]

with:

\[
\boxed{
\text{existence of lattice points}.
}
\]

Let:

\[
L\subseteq\mathbb R^n
\]

be a full-rank lattice.

Let:

\[
K\subseteq\mathbb R^n
\]

be:

- convex;
- centrally symmetric;
- measurable.

If:

\[
\boxed{
\operatorname{vol}(K)
>
2^n\det(L),
}
\]

then \(K\) contains a nonzero lattice point.

This is **Minkowski's First Theorem**.

---

### Why the theorem is remarkable

The theorem does not inspect the basis.

It does not enumerate lattice vectors.

It uses only:

\[
\boxed{
\operatorname{vol}(K)
}
\]

and:

\[
\boxed{
\det(L).
}
\]

If the body becomes large enough relative to the lattice covolume, a nonzero lattice point is forced to exist.

This is a pure existence result.

It does not automatically provide an efficient algorithm for locating that point.

---

### Applying Minkowski to an Euclidean ball

Let:

\[
B_2^n
=
\{
x\in\mathbb R^n:
\|x\|_2\le1
\}.
\]

Its volume is:

\[
\boxed{
V_n
=
\operatorname{vol}(B_2^n)
=
\frac{
\pi^{n/2}
}{
\Gamma(n/2+1)
}.
}
\]

A radius-\(r\) ball has volume:

\[
V_n r^n.
\]

If:

\[
V_n r^n
>
2^n\det(L),
\]

Minkowski guarantees a nonzero lattice vector of length at most \(r\).

Taking the limiting bound gives:

\[
\boxed{
\lambda_1(L)
\le
2
\left(
\frac{
\det(L)
}{
V_n
}
\right)^{1/n}.
}
\]

This is a rigorous upper bound.

---

### Asymptotic scale

Using Stirling's approximation:

\[
V_n^{1/n}
\sim
\sqrt{
\frac{
2\pi e
}{
n
}
},
\]

we obtain:

\[
\frac{2}{V_n^{1/n}}
\sim
\sqrt{
\frac{
2n
}{
\pi e
}
}.
\]

Therefore Minkowski gives the scale:

\[
\boxed{
\lambda_1(L)
=
O\left(
\sqrt n\,
\det(L)^{1/n}
\right).
}
\]

The quantity:

\[
\boxed{
\det(L)^{1/n}
}
\]

is therefore the natural length scale associated with the lattice covolume.

---

### Volume and lattice density

A lattice of smaller determinant has a smaller fundamental cell.

Geometrically, it is denser in its span.

![Volume and lattice density](/images/blog/lattices/volume.png)

Minkowski turns that intuitive density statement into a theorem:

\[
\boxed{
\text{sufficient density forces short nonzero vectors}.
}
\]

---

### Hermite-style normalization

It is often useful to remove the global scale of the lattice.

Define:

\[
\boxed{
\gamma(L)
=
\frac{
\lambda_1(L)^2
}{
\det(L)^{2/n}
}.
}
\]

This quantity is scale-invariant.

If the lattice is multiplied by:

\[
c,
\]

then:

\[
\lambda_1(cL)
=
|c|\lambda_1(L)
\]

and:

\[
\det(cL)
=
|c|^n\det(L).
\]

Therefore:

\[
\gamma(cL)=\gamma(L).
\]

The supremum of this quantity over rank-\(n\) lattices leads to the **Hermite constant**:

\[
\gamma_n.
\]

This gives another way to formulate the relationship between determinant and shortest-vector length.

---

## Minkowski's second theorem

The first theorem controls:

\[
\lambda_1(L).
\]

Minkowski's Second Theorem controls all successive minima simultaneously.

For the Euclidean unit ball:

\[
B_2^n,
\]

we have:

\[
\boxed{
\frac{2^n}{n!}
\det(L)
\le
V_n
\prod_{i=1}^{n}
\lambda_i(L)
\le
2^n
\det(L).
}
\]

Equivalently:

\[
\boxed{
\frac{
2^n
}{
n!V_n
}
\det(L)
\le
\prod_{i=1}^{n}
\lambda_i(L)
\le
\frac{
2^n
}{
V_n
}
\det(L).
}
\]

---

### What the theorem says

The determinant does not constrain only one short vector.

It constrains the product:

\[
\boxed{
\lambda_1(L)
\lambda_2(L)
\cdots
\lambda_n(L).
}
\]

So the full independent-vector geometry is tied to the covolume.

A lattice cannot arbitrarily make all successive minima simultaneously tiny or enormous relative to its determinant.

---

### Example: \(\mathbb Z^2\)

For:

\[
L=\mathbb Z^2,
\]

we know:

\[
\det(L)=1,
\]

and:

\[
\lambda_1(L)
=
\lambda_2(L)
=
1.
\]

Since:

\[
V_2=\pi,
\]

the middle expression is:

\[
V_2\lambda_1\lambda_2
=
\pi.
\]

Minkowski's second theorem gives:

\[
\frac{2^2}{2!}
\le
\pi
\le
2^2.
\]

That is:

\[
\boxed{
2\le\pi\le4.
}
\]

The theorem is satisfied.

---

### Example: a rectangular lattice

Consider:

\[
L=
2\mathbb Z
\times
5\mathbb Z.
\]

Then:

\[
\det(L)=10.
\]

The shortest independent coordinate vectors have lengths:

\[
2
\]

and:

\[
5.
\]

Thus:

\[
\lambda_1(L)=2,
\qquad
\lambda_2(L)=5.
\]

Their product is:

\[
10.
\]

Again the successive-minima scale reflects the covolume.

---

### Existence versus finding

Minkowski's theorems say that vectors satisfying certain length bounds exist.

They do not tell us:

\[
\boxed{
\text{how to find those vectors efficiently from an arbitrary basis}.
}
\]

This is one of the conceptual sources of lattice hardness.

A theorem may certify that a short vector must exist while the computational task of recovering it remains difficult.

---

## The Gaussian heuristic

Minkowski gives rigorous worst-case bounds.

Cryptanalytic estimates often need a prediction for what a **typical random-looking lattice** might look like.

That is where the Gaussian heuristic enters.

---

### Volume-per-lattice-point intuition

A lattice has approximately one point per volume:

\[
\det(L).
\]

So for a sufficiently regular large region \(S\), one expects roughly:

\[
\boxed{
\frac{
\operatorname{vol}(S)
}{
\det(L)
}
}
\]

lattice points.

Apply this intuition to a radius-\(r\) Euclidean ball:

\[
rB_2^n.
\]

Its volume is:

\[
V_n r^n.
\]

The heuristic says that the scale where one begins to expect a nonzero lattice point should satisfy approximately:

\[
\boxed{
\frac{
V_n r^n
}{
\det(L)
}
\approx
1.
}
\]

Solving:

\[
r
\approx
\left(
\frac{
\det(L)
}{
V_n
}
\right)^{1/n}.
\]

Thus:

\[
\boxed{
\lambda_1(L)
\approx
\frac{
\det(L)^{1/n}
}{
V_n^{1/n}
}.
}
\]

---

### High-dimensional approximation

Using:

\[
V_n^{1/n}
\sim
\sqrt{
\frac{
2\pi e
}{
n
}
},
\]

we obtain:

\[
\boxed{
\lambda_1(L)
\approx
\sqrt{
\frac{
n
}{
2\pi e
}
}
\det(L)^{1/n}.
}
\]

This is the familiar Gaussian-heuristic scale.

Small constant corrections can appear depending on whether one models:

- vectors individually;
- \(\pm v\) pairs;
- expected count one;
- median first-arrival behavior.

The important asymptotic scale is:

\[
\boxed{
\sqrt n\,
\det(L)^{1/n}.
}
\]

---

### Heuristic, not theorem

The Gaussian heuristic is **not** a universal theorem about arbitrary lattices.

Specially structured lattices may behave very differently.

For example, a lattice can contain an intentionally planted vector much shorter than the random-lattice prediction.

That situation is especially interesting cryptographically.

If a hidden vector has length:

\[
\|s\|
\]

far below:

\[
\sqrt{
\frac{
n
}{
2\pi e
}
}
\det(L)^{1/n},
\]

then reduction algorithms may have a chance of distinguishing or recovering it.

---

### Minkowski versus Gaussian heuristic

The distinction is worth making explicit.

Minkowski gives a theorem:

\[
\boxed{
\lambda_1(L)
\le
2
\left(
\frac{
\det(L)
}{
V_n
}
\right)^{1/n}.
}
\]

The Gaussian heuristic predicts:

\[
\boxed{
\lambda_1(L)
\approx
\left(
\frac{
\det(L)
}{
V_n
}
\right)^{1/n}
}
\]

for sufficiently random-looking lattices.

So asymptotically the rigorous Minkowski ball bound is roughly twice the Gaussian-heuristic scale.

That is a useful example of the difference between:

\[
\boxed{
\text{worst-case theorem}
}
\]

and:

\[
\boxed{
\text{typical-case heuristic}.
}
\]

---

## Why these problems matter in cryptography

SVP, CVP, BDD, SIVP, and GapSVP play different roles.

They should not be treated as interchangeable labels for "hard lattice problem."

| Problem | Core question | Typical cryptographic role |
| --- | --- | --- |
| SVP | find one shortest nonzero vector | short-secret and relation intuition; basis-reduction target |
| \(\gamma\)-SVP | find a vector within factor \(\gamma\) of shortest | approximation hardness and reduction analysis |
| CVP | find the lattice point closest to an arbitrary target | decoding and approximation problems |
| BDD | decode a target promised to lie unusually close to the lattice | unique decoding and LWE-related geometric formulations |
| SIVP | find \(n\) independent short vectors | worst-case foundation in several lattice reductions |
| GapSVP | distinguish short-vector regimes | decision problem appearing in hardness reductions |

---

### SIS and short relations

The Short Integer Solution problem eventually asks for a short integer vector satisfying a modular linear relation.

Through an associated \(q\)-ary lattice, this becomes a problem involving unusually short lattice vectors.

The exact relation is more structured than simply giving an arbitrary SVP instance, but shortest-vector geometry is central.

---

### LWE and decoding

Learning With Errors introduces small noise into modular linear equations.

Depending on the formulation and reduction, this can be connected to:

- BDD;
- dual lattices;
- Gaussian sampling;
- GapSVP;
- SIVP.

The precise theorem matters.

We should not compress all of these into the statement:

> "LWE is just CVP."

That is too crude.

---

### NTRU and short hidden vectors

NTRU constructions lead naturally to structured lattices containing short vectors associated with secret polynomial data.

A public basis can hide those vectors.

Basis reduction then attempts to expose unusually short combinations.

Again the relevant idea is:

\[
\boxed{
\text{intrinsic short vector}
}
\]

hidden behind:

\[
\boxed{
\text{an inconvenient basis}.
}
\]

---

### Worst-case to average-case reductions

One of the most remarkable features of lattice cryptography is the existence of reductions connecting certain average-case cryptographic problems to worst-case lattice problems.

Depending on the construction and parameter regime, the worst-case side may involve approximation versions of:

\[
\boxed{
\text{GapSVP}
}
\]

or:

\[
\boxed{
\text{SIVP}.
}
\]

The approximation factor, norm, lattice family, and reduction type are essential parts of the theorem.

They should never be silently omitted.

---

## A complete geometric example

Consider:

\[
L=
2\mathbb Z
\times
3\mathbb Z.
\]

A basis is:

\[
B=
\begin{pmatrix}
2&0\\
0&3
\end{pmatrix}.
\]

Its determinant is:

\[
\boxed{
\det(L)=6.
}
\]

---

### SVP

The nonzero vector:

\[
(2,0)
\]

has norm:

\[
2.
\]

No nonzero lattice vector is shorter.

Therefore:

\[
\boxed{
\lambda_1(L)=2.
}
\]

---

### Successive minima

To obtain two independent vectors, we may use:

\[
(2,0)
\]

and:

\[
(0,3).
\]

Thus:

\[
\boxed{
\lambda_2(L)=3.
}
\]

So:

\[
\lambda_1(L)\lambda_2(L)
=
6.
\]

---

### Packing radius

The packing radius is:

\[
\boxed{
r_{\mathrm{pack}}
=
1.
}
\]

Therefore a target lying at distance strictly less than \(1\) from a lattice point has a unique nearest lattice point.

---

### CVP example

Take:

\[
t=
\begin{pmatrix}
4.3\\
5.8
\end{pmatrix}.
\]

Nearby lattice points include:

\[
(4,6),
\]

\[
(4,3),
\]

\[
(6,6).
\]

For:

\[
(4,6),
\]

the displacement is:

\[
\begin{pmatrix}
0.3\\
-0.2
\end{pmatrix},
\]

with norm:

\[
\sqrt{
0.3^2+0.2^2
}
=
\sqrt{0.13}.
\]

So:

\[
(4,6)
\]

is the closest lattice vector.

Because:

\[
\sqrt{0.13}<1,
\]

this target also lies inside the unique-decoding radius.

Thus this particular CVP instance is also a BDD instance.

---

## The structural picture

The shortest-vector scale is:

\[
\boxed{
\lambda_1(L).
}
\]

It defines exact SVP:

\[
\boxed{
\|v\|=\lambda_1(L).
}
\]

Introducing a target gives CVP:

\[
\boxed{
\|t-v\|
=
\operatorname{dist}(t,L).
}
\]

Adding the promise:

\[
\boxed{
\operatorname{dist}(t,L)
<
\alpha\lambda_1(L)
}
\]

gives BDD.

For:

\[
\alpha<\frac12,
\]

the answer is unique.

The entire independent-vector geometry is captured by:

\[
\boxed{
\lambda_1(L),
\ldots,
\lambda_n(L).
}
\]

This leads to SIVP.

GapSVP converts shortest-vector geometry into a promise decision problem.

Minkowski then links these intrinsic lengths to:

\[
\boxed{
\det(L).
}
\]

The first theorem gives:

\[
\boxed{
\lambda_1(L)
\lesssim
\sqrt n\,
\det(L)^{1/n}
}
\]

as a rigorous asymptotic scale.

The second controls:

\[
\boxed{
\prod_i\lambda_i(L).
}
\]

Finally, the Gaussian heuristic predicts the typical scale:

\[
\boxed{
\lambda_1(L)
\approx
\sqrt{
\frac{n}{2\pi e}
}
\det(L)^{1/n}.
}
\]

So the conceptual chain is:

\[
\boxed{
\det(L)
\rightarrow
\text{geometric scale}
\rightarrow
\lambda_i(L)
\rightarrow
\text{computational problems}.
}
\]

---

## Practice and checkpoint

### Exercise 1 — SVP in \(\mathbb Z^2\)

For:

\[
L=\mathbb Z^2,
\]

compute:

\[
\lambda_1(L).
\]

List all vectors attaining this minimum.

---

### Exercise 2 — A scaled lattice

Let:

\[
L=
3\mathbb Z
\times
5\mathbb Z.
\]

Compute:

\[
\det(L),
\]

\[
\lambda_1(L),
\]

and:

\[
\lambda_2(L).
\]

---

### Exercise 3 — Approximate SVP

Suppose:

\[
\lambda_1(L)=10.
\]

What vector lengths are acceptable outputs for:

\[
2\text{-SVP}?
\]

What about:

\[
1.1\text{-SVP}?
\]

---

### Exercise 4 — CVP

For:

\[
L=\mathbb Z^2
\]

and:

\[
t=(2.4,3.7),
\]

find a closest lattice vector.

Compute:

\[
\operatorname{dist}(t,L).
\]

---

### Exercise 5 — Unique BDD

Suppose:

\[
\lambda_1(L)=8.
\]

What is the packing radius?

Why is a target at distance:

\[
3
\]

from a lattice point guaranteed to decode uniquely?

Would the same conclusion follow automatically at distance:

\[
5?
\]

---

### Exercise 6 — Successive minima

Explain why:

\[
\lambda_i(L)
\le
\lambda_{i+1}(L).
\]

Why does increasing \(i\) never decrease the required radius?

---

### Exercise 7 — SIVP versus basis

Explain why \(n\) vectors satisfying the exact SIVP condition need not generate the full lattice.

Construct or search for a small example where independent lattice vectors generate a proper sublattice.

---

### Exercise 8 — GapSVP

Explain the three regions for a \(\gamma\)-GapSVP instance:

\[
\lambda_1(L)\le d,
\]

\[
d<\lambda_1(L)\le\gamma d,
\]

and:

\[
\lambda_1(L)>\gamma d.
\]

Which region lies outside the promise?

---

### Exercise 9 — Minkowski's first theorem

For:

\[
L=\mathbb Z^2,
\]

we have:

\[
\det(L)=1.
\]

Use the Euclidean-ball form of Minkowski's theorem to derive an upper bound on:

\[
\lambda_1(L).
\]

Compare it with the exact value:

\[
1.
\]

---

### Exercise 10 — Minkowski's second theorem

For:

\[
L=
2\mathbb Z
\times
5\mathbb Z,
\]

verify the two-dimensional version of Minkowski's second theorem using:

\[
\lambda_1=2,
\qquad
\lambda_2=5,
\qquad
\det(L)=10.
\]

---

### Exercise 11 — Gaussian heuristic

Suppose a random-looking rank-\(n\) lattice has determinant:

\[
1.
\]

According to the Gaussian heuristic, what is the approximate asymptotic scale of:

\[
\lambda_1(L)?
\]

---

### Exercise 12 — Planted short vector

Suppose a lattice has a hidden vector of length far below the Gaussian-heuristic prediction.

Why might such a vector become interesting to a basis-reduction attack?

Why does the heuristic alone not guarantee that the vector can be efficiently recovered?

---

### Reader checkpoint

You should now be able to explain:

1. What:
   \[
   \lambda_1(L)
   \]
   measures.
2. What exact SVP asks for.
3. What:
   \[
   \gamma\text{-SVP}
   \]
   changes.
4. Why a shortest basis vector need not be a shortest lattice vector.
5. What CVP asks for.
6. How approximate CVP is defined.
7. What the lattice packing radius is.
8. Why:
   \[
   r_{\mathrm{pack}}=\lambda_1/2.
   \]
9. What BDD is.
10. Why:
    \[
    \alpha<1/2
    \]
    guarantees uniqueness.
11. What the successive minima:
    \[
    \lambda_i(L)
    \]
    measure.
12. What SIVP asks for.
13. Why an SIVP solution is not necessarily a lattice basis.
14. What GapSVP asks us to distinguish.
15. Why GapSVP is a promise problem.
16. The difference between search SVP and decision GapSVP.
17. What Minkowski's first theorem states.
18. Why convexity and central symmetry appear in the theorem.
19. How Minkowski yields a determinant-based bound on:
    \[
    \lambda_1(L).
    \]
20. Why:
    \[
    \det(L)^{1/n}
    \]
    is a natural lattice length scale.
21. What the Hermite invariant normalizes.
22. What Minkowski's second theorem says about:
    \[
    \prod_i\lambda_i(L).
    \]
23. Why Minkowski is an existence theorem rather than an efficient shortest-vector algorithm.
24. How the Gaussian heuristic is derived from expected point density.
25. Why:
    \[
    \lambda_1(L)
    \approx
    \sqrt{
    \frac{n}{2\pi e}
    }
    \det(L)^{1/n}
    \]
    is a heuristic rather than a theorem.
26. Why specially structured lattices may violate random-lattice intuition.
27. Why SVP, CVP, BDD, SIVP, and GapSVP must remain conceptually distinct.
28. Why LWE should not simply be described as "CVP with noise."
29. Why worst-case to average-case reductions must specify their actual lattice problem and approximation factor.

The most important distinction is:

\[
\boxed{
\text{Minkowski tells us that short vectors exist.}
}
\]

But cryptography is concerned with:

\[
\boxed{
\text{how difficult they are to find}.
}
\]

---

## References and further reading

**J. W. S. Cassels**,  
*An Introduction to the Geometry of Numbers.*

A classical reference for Minkowski's theorems, successive minima, lattice determinants, and convex-body methods.

**Peter M. Gruber and C. G. Lekkerkerker**,  
*Geometry of Numbers.*

A comprehensive treatment of the geometric theory behind Minkowski's results and lattice-point problems.

**Daniele Micciancio and Shafi Goldwasser**,  
*Complexity of Lattice Problems: A Cryptographic Perspective.*

A foundational reference for SVP, CVP, approximation problems, lattice complexity, and cryptographic applications.

**Daniele Micciancio and Oded Regev**,  
*Worst-Case to Average-Case Reductions Based on Gaussian Measures.*

A central reference for Gaussian methods and worst-case lattice reductions underlying modern lattice cryptography.

**Vadim Lyubashevsky and Daniele Micciancio**,  
*On Bounded Distance Decoding, Unique Shortest Vectors, and the Minimum Distance Problem.*

A useful reference for the computational relationships surrounding BDD and unique shortest-vector problems.

**Oded Regev**,  
*On Lattices, Learning with Errors, Random Linear Codes, and Cryptography.*

A foundational source for Learning With Errors and its connection with worst-case lattice problems.

---

## Next

We now know the intrinsic problems:

\[
\boxed{
\text{SVP},
\quad
\text{CVP},
\quad
\text{BDD},
\quad
\text{SIVP},
\quad
\text{GapSVP}.
}
\]

We also know that determinant and Minkowski theory constrain what short vectors must exist.

But none of this yet tells us how to make a poor input basis geometrically useful.

That is the role of **lattice basis reduction**.

The next article begins with the Gram–Schmidt coefficients developed in the Linear Algebra Foundations series and studies:

\[
\boxed{
\text{size reduction},
}
\]

\[
\boxed{
\text{LLL},
}
\]

\[
\boxed{
\text{Babai's nearest-plane method},
}
\]

and the progression toward stronger block reduction:

\[
\boxed{
\text{BKZ}.
}
\]

That is:

**Lattices & Lattice-Based Cryptography III: Lattice Reduction, LLL, Babai, and the Road to BKZ.**
