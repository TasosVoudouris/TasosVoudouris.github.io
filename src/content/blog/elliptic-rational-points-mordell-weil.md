---
title: "Elliptic Curve Mathematics IV: Rational Points, Heights, Descent, and the Mordell–Weil Theorem"
description: "Rational points on elliptic curves, finite generation, naive and canonical heights, descent, torsion, rank, Selmer groups, and the arithmetic meaning of the Mordell–Weil theorem."
pubDate: "2025-03-19"
updatedDate: "2026-09-17"

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
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 4
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

So far, we have treated an elliptic curve mainly as a geometric object carrying an abelian group law.

Over the rational numbers, a new question appears:

> What can we say about the rational points themselves?

For an elliptic curve

$$
E/\mathbb Q,
$$

the rational points form a group

$$
E(\mathbb Q).
$$

This group may be finite.

It may be infinite.

There may be rational points with enormous numerators and denominators.

Yet one of the central theorems of arithmetic geometry says that this apparently complicated infinite object has a surprisingly rigid structure:

$$
\boxed{
E(\mathbb Q)
\text{ is finitely generated}.
}
$$

Equivalently,

$$
\boxed{
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
}
$$

The finite group

$$
E(\mathbb Q)_{\mathrm{tors}}
$$

contains the torsion points.

The integer

$$
r
$$

is the **rank**.

This chapter explains why finite generation is plausible, why ordinary coordinates are not enough to prove it, and how **descent and height functions** reveal the arithmetic structure of $E(\mathbb Q)$.

---

## Table of Contents

- [1. From conics to cubics](#1-from-conics-to-cubics)
- [2. Rational points form a group](#2-rational-points-form-a-group)
- [3. The Mordell–Weil theorem](#3-the-mordellweil-theorem)
- [4. Torsion and the free part](#4-torsion-and-the-free-part)
- [5. Why finite generation is not obvious](#5-why-finite-generation-is-not-obvious)
- [6. Measuring arithmetic size](#6-measuring-arithmetic-size)
- [Naive height](#naive-height)
- [8. Why naive height is not quite enough](#8-why-naive-height-is-not-quite-enough)
- [Canonical height](#canonical-height)
- [10. Canonical height as a quadratic form](#10-canonical-height-as-a-quadratic-form)
- [11. The weak Mordell–Weil theorem](#11-the-weak-mordellweil-theorem)
- [Descent](#descent)
- [13. How descent and heights prove finite generation](#13-how-descent-and-heights-prove-finite-generation)
- [14. A small rational example](#14-a-small-rational-example)
- [15. Selmer groups and practical descent](#15-selmer-groups-and-practical-descent)
- [Rank](#rank)
- [17. Torsion over $\mathbb Q$](#17-torsion-over-qmathbb-qq)
- [18. Birch and Swinnerton-Dyer](#18-birch-and-swinnerton-dyer)
- [19. Why this matters for cryptography](#19-why-this-matters-for-cryptography)
- [20. The bigger picture](#20-the-bigger-picture)
- [Further reading](#further-reading)

---

## 1. From conics to cubics

Before elliptic curves, consider a conic.

Suppose a conic

$$
C
$$

contains one rational point

$$
P\in C(\mathbb Q).
$$

Draw every line of rational slope through $P$.

Each such line intersects the conic one more time.

Because the defining equations have rational coefficients, that second intersection is rational.

This gives a rational parametrization of the conic.

A familiar example is the unit circle

$$
x^2+y^2=1.
$$

Starting from the rational point

$$
(-1,0),
$$

lines of rational slope generate all rational points on the circle.

So once one rational point is known, the entire conic can essentially be parametrized.

---

### Cubics behave differently

Now consider a nonsingular cubic.

A line meets it in **three** points.

If two intersection points are rational, then the third is rational as well.

This is the geometric origin of the elliptic-curve group law:

$$
P,Q\in E(\mathbb Q)
\quad\Longrightarrow\quad
P+Q\in E(\mathbb Q).
$$

But unlike a conic, a nonsingular cubic cannot generally be rationally parametrized by a single parameter.

This difference is profound.

A conic is essentially a genus-zero object.

An elliptic curve has genus one.

Instead of parametrization, we obtain a finitely generated abelian group.

---

<a id="rational-points-group"></a>

## 2. Rational points form a group

Let

$$
E:
y^2=x^3+ax+b
$$

with

$$
a,b\in\mathbb Q
$$

and

$$
\Delta\neq0.
$$

The rational points are

$$
E(\mathbb Q)
=
\left\{
(x,y)\in\mathbb Q^2:
y^2=x^3+ax+b
\right\}
\cup
\{\mathcal O\}.
$$

The addition formulas from Chapter II involve only rational operations.

For distinct points,

$$
\lambda
=
\frac{y_2-y_1}{x_2-x_1}.
$$

If all coordinates are rational, then

$$
\lambda\in\mathbb Q.
$$

Consequently,

$$
x_3
=
\lambda^2-x_1-x_2
$$

and

$$
y_3
=
\lambda(x_1-x_3)-y_1
$$

are also rational.

Thus

$$
\boxed{
P,Q\in E(\mathbb Q)
\Longrightarrow
P+Q\in E(\mathbb Q).
}
$$

So the geometric group law restricts naturally to rational points.

---

<a id="mordell-weil"></a>

## 3. The Mordell–Weil theorem

The central theorem is more general than the rational case.

Let $K$ be a number field and let

$$
E/K
$$

be an elliptic curve.

Then:

$$
\boxed{
E(K)
\text{ is a finitely generated abelian group}.
}
$$

This is the **Mordell–Weil theorem**.

Over

$$
K=\mathbb Q,
$$

the structure theorem for finitely generated abelian groups gives

$$
\boxed{
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
}
$$

The two components behave very differently.

---

### Torsion part

A point $P$ is torsion if

$$
[n]P=\mathcal O
$$

for some

$$
n\geq1.
$$

All torsion points form the finite subgroup

$$
E(\mathbb Q)_{\mathrm{tors}}.
$$

---

### Free part

The factor

$$
\mathbb Z^r
$$

contains points of infinite order.

The integer

$$
\boxed{
r=\operatorname{rank}E(\mathbb Q)
}
$$

is called the Mordell–Weil rank.

So every rational point can be expressed as

$$
\boxed{
P
=
T+n_1P_1+\cdots+n_rP_r,
}
$$

where

$$
T\in E(\mathbb Q)_{\mathrm{tors}}
$$

and

$$
n_i\in\mathbb Z.
$$

The points

$$
P_1,\ldots,P_r
$$

generate the free part.

---

<a id="torsion-rank"></a>

## 4. Torsion and the free part

The decomposition

$$
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r
$$

immediately gives three qualitatively different possibilities.

### Rank zero

If

$$
r=0,
$$

then

$$
E(\mathbb Q)
=
E(\mathbb Q)_{\mathrm{tors}}
$$

and the rational-point group is finite.

---

### Positive rank

If

$$
r>0,
$$

then $E(\mathbb Q)$ is infinite.

For example, if $P$ has infinite order,

$$
P,\;2P,\;3P,\;4P,\ldots
$$

are infinitely many distinct rational points.

---

### Large rank

A curve can contain several independent infinite-order points.

If

$$
P_1,\ldots,P_r
$$

are independent, then all combinations

$$
n_1P_1+\cdots+n_rP_r
$$

occur.

The group therefore behaves like an $r$-dimensional integer lattice, together with a finite torsion component.

This analogy becomes even stronger once we introduce canonical heights.

---

<a id="finite-generation-not-obvious"></a>

## 5. Why finite generation is not obvious

The equation

$$
y^2=x^3+ax+b
$$

places no obvious upper bound on the numerator or denominator of a rational point.

A rational $x$-coordinate may have the form

$$
x=\frac uv
$$

with

$$
|u|,
|v|
$$

enormous.

And if one rational point of infinite order exists, repeatedly adding it creates infinitely many more rational points.

So why should finitely many points generate all of them?

The proof requires two distinct ideas.

First:

$$
\boxed{
E(\mathbb Q)/mE(\mathbb Q)
\text{ is finite}
}
$$

for a suitable integer $m\geq2$.

This is the **weak Mordell–Weil theorem**.

Second, we need a notion of size that behaves predictably under multiplication by $m$.

That is the role of **heights**.

The proof architecture is therefore

$$
\boxed{
\text{weak Mordell–Weil}
+
\text{height theory}
\Longrightarrow
\text{Mordell–Weil}.
}
$$

---

<a id="arithmetic-size"></a>

## 6. Measuring arithmetic size

Geometry gives us notions such as Euclidean distance.

Arithmetic geometry needs an analogue measuring the complexity of rational numbers.

Consider

$$
x=\frac ab
$$

written in lowest terms:

$$
\gcd(a,b)=1.
$$

Two rational numbers may have similar real magnitude but vastly different arithmetic complexity.

For example,

$$
\frac12
$$

and

$$
\frac{1000001}{2000003}
$$

are both close to $0.5$.

But the second requires much larger integers to describe.

Heights measure this arithmetic complexity.

---

<a id="naive-height"></a>

## Naive height

For

$$
x=\frac ab
$$

in lowest terms, define the multiplicative height

$$
\boxed{
H(x)
=
\max\{|a|,|b|\}.
}
$$

The logarithmic height is

$$
\boxed{
h(x)
=
\log H(x).
}
$$

For example,

$$
x=\frac{17}{23}
$$

has

$$
H(x)=23
$$

and

$$
h(x)=\log23.
$$

For an elliptic-curve point

$$
P=(x(P),y(P)),
$$

a first measure of arithmetic complexity is

$$
h_x(P)=h(x(P)).
$$

The point at infinity may be assigned height zero by convention for this discussion.

---

### Why logarithms?

Multiplicative arithmetic growth becomes additive after taking logarithms.

If numerator and denominator sizes are squared, then approximately

$$
h(x^2)\approx2h(x).
$$

This makes logarithmic heights much easier to use in arithmetic arguments.

---

<a id="naive-height-limitations"></a>

## 8. Why naive height is not quite enough

One might hope that doubling always causes

$$
h_x(2P)
$$

to be exactly

$$
4h_x(P).
$$

But the actual coordinate formulas contain:

* additions;
* cancellations;
* numerators and denominators;
* curve-dependent constants.

So one obtains only an approximate relation of the form

$$
\boxed{
h_x([2]P)
=
4h_x(P)+O(1).
}
$$

More generally,

$$
h_x([n]P)
$$

behaves roughly quadratically in $n$, but not exactly.

This bounded error is enough to suggest a better definition.

We would like a corrected height satisfying

$$
\boxed{
\hat h([n]P)
=
n^2\hat h(P)
}
$$

exactly.

That corrected quantity is the canonical height.

---

<a id="canonical-height"></a>

## Canonical height

The **Néron–Tate canonical height** is obtained by averaging away the bounded errors in the naive height.

With a standard normalization,

$$
\boxed{
\hat h(P)
=
\frac12
\lim_{n\rightarrow\infty}
\frac{
h_x([2^n]P)
}{
4^n
}.
}
$$

Different books may absorb the factor $1/2$ into the normalization of the underlying height, but the essential properties are the same.

The key relation is

$$
\boxed{
\hat h([n]P)
=
n^2\hat h(P).
}
$$

Thus

$$
\hat h(2P)=4\hat h(P),
$$

$$
\hat h(3P)=9\hat h(P),
$$

and generally

$$
\hat h(nP)=n^2\hat h(P).
$$

This exact quadratic behavior is what the naive coordinate height was missing.

---

### Canonical and naive heights remain close

The correction does not radically change the notion of arithmetic size.

For a fixed elliptic curve,

$$
\boxed{
\hat h(P)
=
\frac12h_x(P)+O(1)
}
$$

under the same conventional normalization.

Thus a point has large canonical height precisely when its rational coordinates are arithmetically complicated.

The canonical height is a refined version of the naive height, not an unrelated quantity.

---

<a id="quadratic-form"></a>

## 10. Canonical height as a quadratic form

The canonical height behaves like a quadratic form.

It satisfies the parallelogram identity

$$
\boxed{
\hat h(P+Q)
+
\hat h(P-Q)
=
2\hat h(P)
+
2\hat h(Q).
}
$$

This allows us to define a bilinear pairing:

$$
\boxed{
\langle P,Q\rangle
=
\frac12
\left(
\hat h(P+Q)
-
\hat h(P)
-
\hat h(Q)
\right).
}
$$

This is the **Néron–Tate height pairing**.

On the free part of the Mordell–Weil group, it behaves like an inner product.

If

$$
P_1,\ldots,P_r
$$

generate the free part, then we can form the matrix

$$
\left(
\langle P_i,P_j\rangle
\right)_{i,j}.
$$

This is the height-pairing matrix.

Its determinant is closely related to the **regulator** of the elliptic curve.

So the free part

$$
\mathbb Z^r
$$

really does acquire a Euclidean-lattice-like geometry.

---

### Torsion points

An especially important property is

$$
\boxed{
\hat h(P)=0
\iff
P
\text{ is torsion}.
}
$$

Why is one direction immediate?

If $P$ has order $m$,

$$
[m]P=\mathcal O.
$$

Then

$$
0
=
\hat h(\mathcal O)
=
\hat h([m]P)
=
m^2\hat h(P).
$$

Therefore,

$$
\hat h(P)=0.
$$

The converse requires deeper height theory but is also true.

So canonical height perfectly separates:

$$
\boxed{
\text{torsion}
\leftrightarrow
\hat h=0
}
$$

from

$$
\boxed{
\text{infinite order}
\leftrightarrow
\hat h>0.
}
$$

---

<a id="weak-mordell-weil"></a>

## 11. The weak Mordell–Weil theorem

The first major algebraic ingredient in Mordell–Weil is:

$$
\boxed{
E(K)/mE(K)
\text{ is finite}
}
$$

for every number field $K$ and every integer

$$
m\geq2.
$$

For the rational case and $m=2$,

$$
\boxed{
E(\mathbb Q)/2E(\mathbb Q)
\text{ is finite}.
}
$$

This is called the **weak Mordell–Weil theorem**.

Notice what it says.

It does **not** yet say that

$$
E(\mathbb Q)
$$

is finitely generated.

It says there are only finitely many equivalence classes modulo doubling.

Thus we may choose finitely many representatives

$$
Q_1,\ldots,Q_t
$$

such that every rational point $P$ can be written as

$$
\boxed{
P
=
Q_i+2P'
}
$$

for some $i$ and some

$$
P'\in E(\mathbb Q).
$$

This is exactly the form needed for descent.

---

<a id="descent"></a>

## Descent

Suppose

$$
E(\mathbb Q)/2E(\mathbb Q)
$$

has finitely many representatives

$$
Q_1,\ldots,Q_t.
$$

Given an arbitrary point $P$, write

$$
P
=
Q_i+2P_1.
$$

Now solve for the height of $P_1$.

Since canonical height is quadratic,

$$
\hat h(2P_1)=4\hat h(P_1).
$$

And because

$$
2P_1=P-Q_i,
$$

we obtain

$$
4\hat h(P_1)
=
\hat h(P-Q_i).
$$

Using the quadratic-form properties of $\hat h$, this is controlled by the height of $P$ plus constants depending only on the finite set of $Q_i$.

The key effect is:

$$
\boxed{
\hat h(P_1)
\approx
\frac14\hat h(P).
}
$$

So replacing $P$ by an appropriate “half-point modulo a representative” reduces its arithmetic size substantially.

This can be repeated:

$$
P
=
Q_{i_0}
+
2P_1,
$$

$$
P_1
=
Q_{i_1}
+
2P_2,
$$

$$
P_2
=
Q_{i_2}
+
2P_3,
$$

and so on.

This is the arithmetic meaning of **descent**.

---

### Not ordinary coordinate shrinking

The original intuition that “doubling makes points bigger” is directionally useful but mathematically dangerous.

The rational coordinates themselves may undergo cancellations.

A doubled point can even have a smaller-looking numerator or denominator in an isolated example.

The controlled statement concerns the canonical height:

$$
\boxed{
\hat h(2P)=4\hat h(P).
}
$$

It is this quadratic size function that makes descent rigorous.

---

<a id="finite-generation-proof"></a>

## 13. How descent and heights prove finite generation

We can now see the structure of the proof.

### Step 1: finite quotient

Weak Mordell–Weil gives

$$
E(\mathbb Q)/2E(\mathbb Q)
$$

finite.

Choose representatives

$$
Q_1,\ldots,Q_t.
$$

---

### Step 2: descent

For every point $P$,

$$
P=Q_i+2P_1.
$$

The height of $P_1$ is roughly one quarter of the height of $P$.

---

### Step 3: repeat

If $P_1$ is still large, write

$$
P_1=Q_j+2P_2.
$$

Then

$$
\hat h(P_2)
$$

is smaller again.

Eventually we descend to a point whose height is bounded by some constant depending only on the curve and the chosen coset representatives.

---

### Step 4: bounded height gives finitely many rational points

A fundamental finiteness property of heights — a form of **Northcott's theorem** — says that over a fixed number field there are only finitely many algebraic points of bounded degree and bounded height.

In particular, there are only finitely many rational points of bounded height.

Call that finite set

$$
S.
$$

---

### Step 5: generate everything

Every rational point can therefore be reconstructed from:

* one of the finitely many quotient representatives $Q_i$;
* finitely many bounded-height points from $S$;
* repeated doubling.

Hence finitely many rational points generate all of $E(\mathbb Q)$.

Therefore,

$$
\boxed{
E(\mathbb Q)
\text{ is finitely generated}.
}
$$

This is the heart of the Mordell–Weil proof strategy.

---

<a id="rational-example"></a>

## 14. A small rational example

Consider

$$
E:
y^2=x^3-2.
$$

The point

$$
P=(3,5)
$$

lies on the curve because

$$
5^2=25
$$

and

$$
3^3-2=25.
$$

Let us double $P$.

The tangent slope is

$$
\lambda
=
\frac{3x_P^2}{2y_P}
=
\frac{27}{10}.
$$

Therefore,

$$
x(2P)
=
\lambda^2-2x_P
$$

gives

$$
x(2P)
=
\frac{729}{100}-6
=
\frac{129}{100}.
$$

Then

$$
y(2P)
=
\lambda
\left(
3-\frac{129}{100}
\right)
-5.
$$

Hence

$$
y(2P)
=
-\frac{383}{1000}.
$$

So

$$
\boxed{
2P
=
\left(
\frac{129}{100},
-\frac{383}{1000}
\right).
}
$$

Notice what happened.

We began with tiny integral coordinates:

$$
(3,5).
$$

One doubling already produced denominators

$$
100
$$

and

$$
1000.
$$

This illustrates how quickly arithmetic complexity can grow.

But one should not infer a theorem merely from coordinate growth in examples.

The rigorous measurement is the canonical height:

$$
\hat h(2P)=4\hat h(P).
$$

That is the quantity descent controls.

---

<a id="selmer-groups"></a>

## 15. Selmer groups and practical descent

The phrase “perform a $2$-descent” usually means something more concrete than merely studying

$$
E(\mathbb Q)/2E(\mathbb Q).
$$

One constructs a finite computable group called the **$2$-Selmer group**:

$$
\operatorname{Sel}_2(E/\mathbb Q).
$$

There is an exact sequence

$$
\boxed{
0
\longrightarrow
E(\mathbb Q)/2E(\mathbb Q)
\longrightarrow
\operatorname{Sel}_2(E/\mathbb Q)
\longrightarrow
\Sha(E/\mathbb Q)[2]
\longrightarrow
0.
}
$$

Here

$$
\Sha(E/\mathbb Q)
$$

is the **Tate–Shafarevich group**.

This sequence explains several important facts.

First,

$$
E(\mathbb Q)/2E(\mathbb Q)
$$

embeds into a finite group that can often be computed.

Therefore the Selmer group provides an upper bound on the rank.

Second, the gap between the Selmer group and the actual rational points is measured by

$$
\Sha(E/\mathbb Q)[2].
$$

This is one reason descent can give a rank bound without immediately producing all generators.

---

### Why local information enters

Selmer groups are built by examining whether certain associated equations have solutions over:

$$
\mathbb R
$$

and over the $p$-adic fields

$$
\mathbb Q_p.
$$

So one studies a global rational-point problem using many local fields.

This local-to-global viewpoint is one of the central themes of arithmetic geometry.

---

<a id="rank"></a>

## Rank

Recall

$$
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
$$

The integer

$$
r
$$

measures the number of independent rational points of infinite order.

### Rank zero

$$
r=0
$$

means all rational points are torsion.

---

### Rank one

There is one independent point

$$
P.
$$

Ignoring torsion, every rational point has the form

$$
[n]P.
$$

---

### Rank two

There are independent points

$$
P_1,P_2,
$$

and rational points look like

$$
n_1P_1+n_2P_2+T.
$$

---

### Higher rank

The free subgroup resembles

$$
\mathbb Z^r.
$$

Through the canonical height pairing, it behaves geometrically like a Euclidean lattice of rank $r$.

Thus a remarkable second lattice-like structure appears inside elliptic-curve arithmetic:

$$
\boxed{
E(\mathbb Q)/E(\mathbb Q)_{\mathrm{tors}}
\cong
\mathbb Z^r.
}
$$

This should not be confused with the Euclidean lattices used in lattice-based cryptography.

But the analogy is mathematically useful.

---

<a id="torsion-over-q"></a>

## 17. Torsion over $\mathbb Q$

The torsion subgroup is not arbitrary.

Over the rational numbers, Mazur's theorem completely classifies the possibilities.

The torsion subgroup must be one of:

$$
\boxed{
\mathbb Z/n\mathbb Z,
\qquad
1\leq n\leq10
\text{ or }
n=12,
}
$$

or

$$
\boxed{
\mathbb Z/2\mathbb Z
\oplus
\mathbb Z/2n\mathbb Z,
\qquad
1\leq n\leq4.
}
$$

So only finitely many abstract torsion structures can occur over $\mathbb Q$.

This is remarkably rigid.

The free rank, by contrast, is much more mysterious.

There is no comparably simple classification.

---

<a id="bsd"></a>

## 18. Birch and Swinnerton-Dyer

The rank is connected to one of the deepest conjectures in modern number theory.

Associated with an elliptic curve is an analytic function

$$
L(E,s).
$$

The **Birch and Swinnerton-Dyer conjecture** predicts, among other things, that

$$
\boxed{
\operatorname{rank}E(\mathbb Q)
=
\operatorname{ord}_{s=1}L(E,s).
}
$$

The left-hand side is algebraic:

$$
\text{independent rational points}.
$$

The right-hand side is analytic:

$$
\text{order of vanishing of an }L\text{-function}.
$$

Thus BSD proposes an extraordinary bridge:

$$
\boxed{
\text{rational points}
\longleftrightarrow
\text{analytic behavior of }L(E,s).
}
$$

The refined conjecture goes much further and relates the leading coefficient at $s=1$ to quantities including:

* the regulator;
* the torsion subgroup;
* local Tamagawa numbers;
* real periods;
* the Tate–Shafarevich group.

So the canonical height pairing introduced earlier is not merely a proof device.

Through the regulator, it appears directly in one of the deepest conjectural formulas in arithmetic geometry.

---

<a id="cryptography-connection"></a>

## 19. Why this matters for cryptography

Most cryptographic elliptic curves are not studied over

$$
\mathbb Q.
$$

They are studied over finite fields:

$$
\mathbb F_p
$$

or

$$
\mathbb F_{2^m}.
$$

Then

$$
E(\mathbb F_q)
$$

is itself finite, so Mordell–Weil finite generation is not needed to prove finiteness.

Why study rational points at all on a cryptography site?

Because the theory explains where elliptic curves really belong mathematically.

The finite-field group used in cryptography is one manifestation of a much broader arithmetic object.

Concepts such as:

* rational points;
* reduction modulo primes;
* torsion;
* isogenies;
* local fields;
* global fields;
* heights;
* Frobenius;
* $L$-functions;

are all interconnected.

More importantly, it prevents a distorted picture in which an elliptic curve is merely:

$$
\boxed{
\text{a formula for fast point multiplication}.
}
$$

It is instead an algebraic curve carrying extraordinarily rich arithmetic structure.

---

<a id="bigger-picture"></a>

## 20. The bigger picture

The first four chapters now form a natural progression.

### Chapter I — the geometric object

$$
\boxed{
\text{smooth projective genus-one curve}
+
\mathcal O.
}
$$

---

### Chapter II — the group law

$$
\boxed{
\text{lines and tangents}
\rightarrow
\text{point addition}.
}
$$

---

### Chapter III — why addition is associative

$$
\boxed{
E
\cong
\operatorname{Pic}^0(E).
}
$$

---

### Chapter IV — arithmetic structure over $\mathbb Q$

$$
\boxed{
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
}
$$

The logical structure behind Mordell–Weil is:

$$
\boxed{
E(\mathbb Q)/mE(\mathbb Q)
\text{ finite}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{descent}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\hat h([m]P)=m^2\hat h(P)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{reduce to bounded height}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{only finitely many bounded-height rational points}
}
$$

$$
\Downarrow
$$

$$
\boxed{
E(\mathbb Q)
\text{ finitely generated}.
}
$$

This is one of the remarkable achievements of arithmetic geometry.

An equation as simple-looking as

$$
y^2=x^3+ax+b
$$

contains an infinite arithmetic universe.

Yet that universe is constrained strongly enough that a finite set of rational points generates all the others.

And still, even after Mordell–Weil tells us that finitely many generators exist, determining the rank and finding those generators can be extraordinarily difficult.

That combination —

$$
\boxed{
\text{rigid global structure}
+
\text{deep computational complexity}
}
$$

— is one of the reasons elliptic curves sit at the center of modern number theory.

---

## Further reading

For the material in this chapter:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Joseph H. Silverman and John Tate, **Rational Points on Elliptic Curves**.
* J. W. S. Cassels, **Lectures on Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* André Weil, foundational work on abelian varieties and rational points.
* Barry Mazur, work on rational torsion of elliptic curves.
* John Tate, work on heights, descent, and arithmetic geometry.

---

The next chapter naturally changes the base field.

Instead of

$$
E(\mathbb Q),
$$

we move to

$$
\boxed{
E(\mathbb F_p).
}
$$

Now the group itself is finite.

The questions become:

* How many points are there?
* Why is the count near $p+1$?
* What is the Frobenius endomorphism?
* What does Hasse's bound mean?
* What are point orders and cofactors?
* When is $E(\mathbb F_p)$ cyclic?
* How do we choose a cryptographic subgroup?

That is the point where the arithmetic theory begins to connect directly with practical elliptic-curve cryptography.
