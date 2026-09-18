---
title: "Elliptic Curve Mathematics V: Torsion Points, Division by n, and the Nagell–Lutz Theorem"
description: "Finite-order points over algebraic closures, multiplication-by-n maps, division polynomials, rational torsion, Nagell–Lutz over Q, Mazur's theorem, and the special behavior of p-torsion in characteristic p."
pubDate: "2025-03-19"
updatedDate: "2026-09-17"

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
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 5
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

The previous chapter gave the Mordell–Weil decomposition

$$
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
$$

The free part measures the rank.

The finite part consists of points that eventually return to the identity under repeated addition.

These are the **torsion points**.

If

$$
[n]P=\mathcal O
$$

for some positive integer \(n\), then \(P\) has finite order.

Torsion appears throughout elliptic-curve mathematics:

* rational-point theory;
* division polynomials;
* isogenies;
* Galois representations;
* pairings;
* finite-field subgroup structure;
* cryptographic parameter selection.

But there is an important distinction that must be made from the beginning:

$$
\boxed{
E[n]
\neq
E(K)[n]
\text{ in general}.
}
$$

The first is naturally defined over an algebraic closure.

The second contains only the torsion points whose coordinates already lie in the base field \(K\).

---

## Table of Contents

- [1. Finite-order points](#1-finite-order-points)
- [2. The multiplication-by-(n) map](#2-the-multiplication-by-n-map)
- [3. The geometric (n)-torsion subgroup](#3-the-geometric-n-torsion-subgroup)
- [4. Rational torsion versus geometric torsion](#4-rational-torsion-versus-geometric-torsion)
- [5. Why (E\[n\]\cong(\mathbb Z/n\mathbb Z)^2)](#5-why-encongmathbb-znmathbb-z2)
- [6. Division by (n)](#6-division-by-n)
- [Division polynomials](#division-polynomials)
- [8. What changes in characteristic (p)](#8-what-changes-in-characteristic-p)
- [9. Ordinary and supersingular (p)-torsion](#9-ordinary-and-supersingular-p-torsion)
- [10. Rational torsion over (\mathbb Q)](#10-rational-torsion-over-mathbb-q)
- [11. The Nagell–Lutz theorem](#11-the-nagelllutz-theorem)
- [12. A worked Nagell–Lutz example](#12-a-worked-nagelllutz-example)
- [13. Mazur’s theorem](#13-mazurs-theorem)
- [14. Galois action on torsion](#14-galois-action-on-torsion)
- [15. Why torsion matters computationally](#15-why-torsion-matters-computationally)
- [16. The bigger picture](#16-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="finite-order-points"></a>

## 1. Finite-order points

Let \(E/K\) be an elliptic curve.

A point

$$
P\in E(\overline K)
$$

is a **torsion point** if there exists an integer

$$
n\geq1
$$

such that

$$
[n]P=\mathcal O.
$$

The smallest positive such \(n\) is called the **order** of \(P\).

We write

$$
\boxed{
\operatorname{ord}(P)=n.
}
$$

For example, if

$$
[2]P=\mathcal O
$$

and

$$
P\neq\mathcal O,
$$

then \(P\) has order \(2\).

If

$$
[5]P=\mathcal O
$$

but no smaller positive multiple vanishes, then \(P\) has order \(5\).

The full torsion subgroup is

$$
E(\overline K)_{\mathrm{tors}}
=
\bigcup_{n\geq1}E[n].
$$

---

<a id="multiplication-by-n"></a>

## 2. The multiplication-by-\(n\) map

Repeated addition defines a morphism

$$
[n]:
E\longrightarrow E
$$

by

$$
P\longmapsto[n]P.
$$

For positive \(n\),

$$
[n]P
=
\underbrace{
P+\cdots+P
}_{n\text{ times}}.
$$

For negative integers,

$$
[-n]P=-([n]P).
$$

And

$$
[0]P=\mathcal O.
$$

The \(n\)-torsion points are exactly the kernel:

$$
\boxed{
E[n]
=
\ker[n].
}
$$

Thus

$$
P\in E[n]
$$

if and only if

$$
[n]P=\mathcal O.
$$

The map \([n]\) has degree

$$
\boxed{
\deg[n]=n^2.
}
$$

This already hints that, when the map is separable, one should expect roughly \(n^2\) points in its kernel.

---

<a id="geometric-n-torsion"></a>

## 3. The geometric \(n\)-torsion subgroup

The standard definition is

$$
\boxed{
E[n]
=
\left\{
P\in E(\overline K):
[n]P=\mathcal O
\right\}.
}
$$

The algebraic closure

$$
\overline K
$$

is essential.

Why?

Because the equation

$$
[n]P=\mathcal O
$$

may have solutions whose coordinates lie in an extension field rather than in \(K\) itself.

So \(E[n]\) describes the **geometric torsion**.

The subgroup rational over \(K\) is instead

$$
\boxed{
E(K)[n]
=
E[n]\cap E(K).
}
$$

These groups can be very different.

---

<a id="rational-vs-geometric"></a>

## 4. Rational torsion versus geometric torsion

Suppose

$$
E/\mathbb Q.
$$

Even if

$$
E[5]
\cong
(\mathbb Z/5\mathbb Z)^2
$$

over

$$
\overline{\mathbb Q},
$$

this does not mean that all \(25\) points are rational.

Usually they are not.

Instead,

$$
E(\mathbb Q)[5]
$$

contains only those \(5\)-torsion points fixed by the arithmetic of the base field.

One may therefore have

$$
E[5](\overline{\mathbb Q})
\cong
(\mathbb Z/5\mathbb Z)^2
$$

while

$$
E(\mathbb Q)[5]
=
\{\mathcal O\}.
$$

The distinction is:

$$
\boxed{
\text{geometric existence}
\neq
\text{rational existence}.
}
$$

This theme appears repeatedly in arithmetic geometry.

---

<a id="torsion-structure"></a>

## 5. Why \(E[n]\cong(\mathbb Z/n\mathbb Z)^2\)

Assume

$$
\operatorname{char}(K)\nmid n.
$$

Then the multiplication map

$$
[n]:E\rightarrow E
$$

is separable.

Since

$$
\deg[n]=n^2,
$$

its kernel contains exactly

$$
n^2
$$

geometric points.

Moreover, every element of the kernel is killed by \(n\).

The resulting abstract group is

$$
\boxed{
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2.
}
$$

So one may choose two independent torsion points

$$
P,Q
$$

such that every \(n\)-torsion point is uniquely expressible as

$$
[a]P+[b]Q,
$$

with

$$
a,b\in\mathbb Z/n\mathbb Z.
$$

Thus \(E[n]\) behaves like a two-dimensional vector space when \(n\) is prime.

For example, if \(\ell\) is prime and

$$
\ell\neq\operatorname{char}(K),
$$

then

$$
\boxed{
E[\ell]
\cong
(\mathbb Z/\ell\mathbb Z)^2
}
$$

and can be regarded as a two-dimensional vector space over

$$
\mathbb F_\ell.
$$

---

### Example: \(2\)-torsion

For

$$
E:
y^2=x^3+ax+b,
$$

a nontrivial point satisfies

$$
[2]P=\mathcal O
$$

exactly when

$$
P=-P.
$$

But

$$
-(x,y)=(x,-y).
$$

Therefore

$$
P=-P
$$

requires

$$
y=0.
$$

So nontrivial \(2\)-torsion points correspond to roots of

$$
x^3+ax+b=0.
$$

Over an algebraic closure there are three roots when the curve is nonsingular.

Thus

$$
E[2]
=
\{
\mathcal O,
(\alpha_1,0),
(\alpha_2,0),
(\alpha_3,0)
\},
$$

which has four points:

$$
\boxed{
E[2]\cong
(\mathbb Z/2\mathbb Z)^2.
}
$$

But those roots need not lie in the base field.

Again:

$$
E[2]
$$

and

$$
E(K)[2]
$$

need not coincide.

---

<a id="division-by-n"></a>

## 6. Division by \(n\)

The notation

$$
[n]P
$$

means multiply the point by the integer \(n\).

The inverse question is:

> Given \(Q\), can we find \(P\) such that
>
> $$
> [n]P=Q?
> $$

This is called **division by \(n\)** on the elliptic curve.

Over an algebraically closed field, the map

$$
[n]:E\rightarrow E
$$

is surjective.

So such points exist.

But they are not unique.

If

$$
[n]P=Q
$$

and

$$
T\in E[n],
$$

then

$$
[n](P+T)
=
[n]P+[n]T
=
Q+\mathcal O
=
Q.
$$

Thus all solutions form a coset:

$$
\boxed{
P+E[n].
}
$$

When

$$
\operatorname{char}(K)\nmid n,
$$

there are \(n^2\) geometric preimages.

So division by \(n\) naturally produces the \(n\)-torsion subgroup.

---

<a id="division-polynomials"></a>

## Division polynomials

How can the coordinates of torsion points be found algebraically?

For a Weierstrass curve there are special polynomials called **division polynomials**:

$$
\psi_n.
$$

They encode multiplication-by-\(n\).

For a nontrivial affine point \(P\), under the usual hypotheses,

$$
\boxed{
[n]P=\mathcal O
\iff
\psi_n(P)=0.
}
$$

For odd \(n\), \(\psi_n\) is essentially a polynomial in \(x\) alone.

Its degree is

$$
\boxed{
\deg_x\psi_n
=
\frac{n^2-1}{2}
}
$$

for odd \(n\).

For even \(n\), after separating the factor involving \(y\), the relevant \(x\)-polynomial has degree

$$
\boxed{
\frac{n^2-4}{2}.
}
$$

The first few division polynomials include

$$
\psi_1=1,
$$

$$
\psi_2=2y,
$$

and

$$
\psi_3
=
3x^4
+
6ax^2
+
12bx
-
a^2
$$

for short Weierstrass form.

So \(3\)-torsion points can be detected by solving

$$
\psi_3(x)=0
$$

and recovering corresponding \(y\)-coordinates.

Division polynomials therefore convert the abstract condition

$$
[n]P=\mathcal O
$$

into explicit algebra.

---

<a id="characteristic-p"></a>

## 8. What changes in characteristic \(p\)

Everything above assumed

$$
\operatorname{char}(K)\nmid n.
$$

If the characteristic divides \(n\), the story changes.

Let

$$
\operatorname{char}(K)=p.
$$

The multiplication map

$$
[p]:E\rightarrow E
$$

still has degree

$$
p^2.
$$

But it is no longer fully separable.

Therefore one cannot conclude that its kernel contains \(p^2\) geometric points.

This is the essential reason the simple formula

$$
E[n]\cong(\mathbb Z/n\mathbb Z)^2
$$

fails when

$$
p\mid n.
$$

The missing information is hidden in nonreduced group-scheme structure.

For this series, however, we can first understand the ordinary geometric points.

---

<a id="ordinary-supersingular"></a>

## 9. Ordinary and supersingular \(p\)-torsion

Over an algebraic closure of a field of characteristic \(p\), elliptic curves split into two fundamentally different classes.

### Ordinary elliptic curves

For an ordinary elliptic curve,

$$
\boxed{
E[p](\overline K)
\cong
\mathbb Z/p\mathbb Z
}
$$

as a group of geometric points.

So there are \(p\) geometric \(p\)-torsion points.

---

### Supersingular elliptic curves

For a supersingular elliptic curve,

$$
\boxed{
E[p](\overline K)
=
\{\mathcal O\}.
}
$$

There are no nontrivial geometric \(p\)-torsion points.

Yet the multiplication map still has degree

$$
p^2.
$$

Where did that degree go?

The complete answer requires finite group schemes.

Very roughly, the kernel of \([p]\) has scheme-theoretic size \(p^2\), even though the number of ordinary geometric points can be much smaller.

This distinction is one of the first places where the point-set view of algebraic geometry becomes insufficient.

---

### Why ordinary versus supersingular matters

This classification affects:

* endomorphism rings;
* isogeny structure;
* Frobenius;
* pairings;
* point counting;
* cryptographic constructions.

So the behavior of \(p\)-torsion is not a technical curiosity.

It reflects a deep structural difference between elliptic curves in characteristic \(p\).

---

<a id="rational-torsion-q"></a>

## 10. Rational torsion over \(\mathbb Q\)

Return now to

$$
E/\mathbb Q.
$$

The Mordell–Weil theorem gives

$$
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
$$

The torsion subgroup is finite.

A natural computational question is:

> Given an explicit elliptic curve over \(\mathbb Q\), how can we find its rational torsion points?

One remarkably useful theorem is **Nagell–Lutz**.

It converts a priori rational coordinates into integral ones.

That turns an infinite rational search into a finite arithmetic search.

---

<a id="nagell-lutz"></a>

## 11. The Nagell–Lutz theorem

Let

$$
E:
y^2=x^3+Ax+B
$$

with

$$
A,B\in\mathbb Z
$$

and

$$
4A^3+27B^2\neq0.
$$

Suppose

$$
P=(x,y)\in E(\mathbb Q)
$$

is a nontrivial torsion point.

Then:

$$
\boxed{
x,y\in\mathbb Z.
}
$$

Moreover, either

$$
\boxed{
y=0
}
$$

or

$$
\boxed{
y^2
\mid
4A^3+27B^2.
}
$$

Since the elliptic-curve discriminant is

$$
\Delta
=
-16(4A^3+27B^2),
$$

one may equivalently view the theorem as strongly constraining \(y\) using the discriminant.

This is striking.

A torsion point was initially allowed to have arbitrary rational coordinates.

Nagell–Lutz says that on such an integral short-Weierstrass model, its coordinates must actually be integers.

---

### Why this gives a finite search

There are only finitely many integers \(y\) such that

$$
y^2
\mid
4A^3+27B^2.
$$

For each candidate \(y\), solve

$$
x^3+Ax+B=y^2
$$

for integral \(x\).

This produces a finite list of torsion candidates.

One must still determine the actual order of each candidate.

Nagell–Lutz gives a **necessary condition**, not a statement that every candidate is torsion.

---

<a id="nagell-lutz-example"></a>

## 12. A worked Nagell–Lutz example

Consider

$$
\boxed{
E:
y^2=x^3+1.
}
$$

Here

$$
A=0,
\qquad
B=1.
$$

Therefore,

$$
4A^3+27B^2=27.
$$

Nagell–Lutz says that a nontrivial rational torsion point must have

$$
x,y\in\mathbb Z
$$

and either

$$
y=0
$$

or

$$
y^2\mid27.
$$

The possible integral values are therefore

$$
y=0,\pm1,\pm3.
$$

Now solve

$$
x^3+1=y^2.
$$

### \(y=0\)

$$
x^3+1=0
$$

gives

$$
x=-1.
$$

So

$$
(-1,0)
$$

is a candidate.

Since its \(y\)-coordinate is zero,

$$
-(-1,0)=(-1,0),
$$

so

$$
2(-1,0)=\mathcal O.
$$

It has order \(2\).

---

### \(y=\pm1\)

Then

$$
x^3+1=1,
$$

so

$$
x=0.
$$

We obtain

$$
(0,1),
\qquad
(0,-1).
$$

Doubling

$$
P=(0,1)
$$

gives slope

$$
\lambda
=
\frac{3x^2}{2y}
=
0.
$$

Hence

$$
2P=(0,-1)=-P.
$$

Therefore,

$$
3P=\mathcal O.
$$

So

$$
(0,\pm1)
$$

are \(3\)-torsion points.

---

### \(y=\pm3\)

Then

$$
x^3+1=9,
$$

so

$$
x^3=8
$$

and

$$
x=2.
$$

This gives

$$
(2,3),
\qquad
(2,-3).
$$

In fact,

$$
(2,3)
$$

has order \(6\).

Thus

$$
E(\mathbb Q)_{\mathrm{tors}}
\cong
\mathbb Z/6\mathbb Z.
$$

The complete rational torsion subgroup is

$$
\boxed{
\{
\mathcal O,
(-1,0),
(0,\pm1),
(2,\pm3)
\}.
}
$$

This is an excellent example of Nagell–Lutz turning a rational torsion problem into a finite integral computation.

---

<a id="mazur"></a>

## 13. Mazur's theorem

Nagell–Lutz tells us something about the **coordinates** of torsion points on a particular integral model.

Mazur's theorem goes much deeper.

It classifies the possible abstract torsion groups of elliptic curves over

$$
\mathbb Q.
$$

For every elliptic curve over \(\mathbb Q\),

$$
E(\mathbb Q)_{\mathrm{tors}}
$$

must be one of the following.

### Cyclic groups

$$
\boxed{
\mathbb Z/n\mathbb Z
}
$$

for

$$
1\leq n\leq10
$$

or

$$
n=12.
$$

### Products

$$
\boxed{
\mathbb Z/2\mathbb Z
\oplus
\mathbb Z/2n\mathbb Z
}
$$

for

$$
1\leq n\leq4.
$$

So, for example, one can have

$$
\mathbb Z/5\mathbb Z,
$$

$$
\mathbb Z/10\mathbb Z,
$$

or

$$
\mathbb Z/2\mathbb Z
\oplus
\mathbb Z/8\mathbb Z.
$$

But one cannot have

$$
\mathbb Z/11\mathbb Z
$$

as the rational torsion subgroup of an elliptic curve over \(\mathbb Q\).

This is an astonishing global restriction.

---

### Nagell–Lutz versus Mazur

The two theorems solve very different problems.

Nagell–Lutz:

$$
\boxed{
\text{Where can the torsion points of this curve be?}
}
$$

Mazur:

$$
\boxed{
\text{Which rational torsion group structures can occur at all?}
}
$$

Nagell–Lutz is computational and curve-specific.

Mazur's theorem is structural and universal over \(\mathbb Q\).

---

<a id="galois-torsion"></a>

## 14. Galois action on torsion

There is another reason geometric torsion is important even when the points are not rational.

Let

$$
G_K
=
\operatorname{Gal}(\overline K/K)
$$

be the absolute Galois group.

Because the elliptic-curve equations are defined over \(K\), Galois automorphisms send torsion points to torsion points.

Thus \(G_K\) acts on

$$
E[n].
$$

When

$$
\operatorname{char}(K)\nmid n,
$$

we have

$$
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2.
$$

Choosing a basis gives a representation

$$
\boxed{
\rho_{E,n}:
G_K
\longrightarrow
\operatorname{GL}_2(\mathbb Z/n\mathbb Z).
}
$$

The \(K\)-rational \(n\)-torsion points are exactly the points fixed by this action:

$$
\boxed{
E(K)[n]
=
E[n]^{G_K}.
}
$$

This gives a much deeper interpretation of the difference between

$$
E[n]
$$

and

$$
E(K)[n].
$$

The geometric torsion exists.

The Galois action determines which of those points descend to the base field.

This viewpoint leads eventually to:

* Tate modules;
* \(\ell\)-adic Galois representations;
* the Weil pairing;
* isogeny theory;
* major results in arithmetic geometry.

---

<a id="computational-importance"></a>

## 15. Why torsion matters computationally

Torsion is not just a theoretical side topic.

It appears throughout elliptic-curve computation.

### Division polynomials

The coordinates of \(n\)-torsion points are encoded by

$$
\psi_n.
$$

---

### Point counting

The behavior of torsion over finite extensions contains information about

$$
\#E(\mathbb F_q).
$$

---

### Isogenies

If

$$
C\subseteq E
$$

is a finite subgroup, then under suitable conditions one can form a quotient elliptic curve

$$
E/C
$$

and an isogeny

$$
\phi:E\rightarrow E/C
$$

with kernel \(C\).

So torsion subgroups naturally become isogeny kernels.

---

### Pairings

Pairings such as the Weil and Tate pairings are defined using torsion points.

For example, when

$$
\gcd(n,\operatorname{char}K)=1,
$$

the Weil pairing has the form

$$
e_n:
E[n]\times E[n]
\rightarrow
\mu_n.
$$

Thus the rank-two structure

$$
E[n]\cong(\mathbb Z/n\mathbb Z)^2
$$

is essential.

---

### Cryptographic subgroup structure

Over a finite field,

$$
E(\mathbb F_q)
$$

is finite.

Cryptographic protocols normally operate inside a large prime-order subgroup.

The remaining factor is the **cofactor**.

Understanding torsion and subgroup structure is therefore directly relevant to:

* subgroup checks;
* cofactors;
* invalid-point behavior;
* small-subgroup issues;
* protocol validation.

---

<a id="bigger-picture"></a>

## 16. The bigger picture

The previous chapter decomposed

$$
E(\mathbb Q)
$$

as

$$
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
$$

This chapter has now unpacked the torsion part.

The central hierarchy is:

$$
\boxed{
[n]:E\rightarrow E
}
$$

$$
\Downarrow
$$

$$
\boxed{
E[n]=\ker[n]
}
$$

$$
\Downarrow
$$

when

$$
\operatorname{char}(K)\nmid n,
$$

$$
\boxed{
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2
}
$$

over the algebraic closure.

But arithmetic asks a second question:

$$
\boxed{
\text{which of these points are defined over }K?
}
$$

That produces

$$
\boxed{
E(K)[n]
=
E[n]\cap E(K).
}
$$

Over \(\mathbb Q\), rational torsion is extraordinarily constrained.

Nagell–Lutz says that on an integral short-Weierstrass model, rational torsion points have integral coordinates and satisfy strong discriminant divisibility conditions.

Mazur goes further and classifies every possible group structure:

$$
\boxed{
E(\mathbb Q)_{\mathrm{tors}}
\text{ belongs to a finite explicit list}.
}
$$

In characteristic \(p\), another layer appears:

$$
\boxed{
p\mid n
}
$$

causes the multiplication map to become inseparable.

Then the simple rank-two picture breaks.

For \(p\)-torsion:

$$
\boxed{
\text{ordinary}
\Rightarrow
E[p](\overline K)
\cong
\mathbb Z/p\mathbb Z,
}
$$

while

$$
\boxed{
\text{supersingular}
\Rightarrow
E[p](\overline K)
=
\{\mathcal O\}.
}
$$

So torsion connects several parts of elliptic-curve theory:

$$
\boxed{
\text{group law}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{multiplication maps}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{division points}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Galois structure}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isogenies, pairings, and finite-field arithmetic}.
}
$$

This is why torsion is better introduced as core elliptic-curve mathematics rather than only when a particular cryptographic construction or attack happens to require it.

---

## Further reading

For deeper treatments of torsion points and division:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Joseph H. Silverman and John Tate, **Rational Points on Elliptic Curves**.
* J. W. S. Cassels, **Lectures on Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Barry Mazur, **Modular Curves and the Eisenstein Ideal** and related work on rational isogenies and torsion.
* Serge Lang, **Elliptic Curves: Diophantine Analysis**.

---

The next chapter naturally moves from

$$
E(\mathbb Q)
$$

and geometric torsion to elliptic curves over finite fields:

$$
\boxed{
E(\mathbb F_q).
}
$$

There the entire group is finite.

The central questions become:

* How large is \(E(\mathbb F_q)\)?
* Why is the answer close to \(q+1\)?
* What is the Frobenius endomorphism?
* What does Hasse's bound mean?
* How are point orders related to the full group order?
* What is the cofactor?
* How do extension fields change the torsion that becomes rational?

Those questions lead directly into the finite-group mathematics underlying elliptic-curve cryptography.
