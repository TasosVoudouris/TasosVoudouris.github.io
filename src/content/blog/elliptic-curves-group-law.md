---
title: "Elliptic Curve Mathematics II: Weierstrass Curves and the Group Law"
description: "A detailed introduction to the elliptic-curve group law: secants, tangents, inverses, point addition, doubling, exceptional cases, associativity, and computational formulas."
pubDate: "2025-05-25"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Mathematical Foundations"
  - "Public-Key Cryptography"

tags:
  - "elliptic-curves"
  - "group-law"
  - "weierstrass"
  - "point-addition"

difficulty: "Intermediate"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 2
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

The previous chapter established the geometric object:

$$
E:
y^2=x^3+ax+b,
$$

together with its projective point at infinity

$$
\mathcal O=(0:1:0),
$$

under the nonsingularity condition

$$
\Delta=-16(4a^3+27b^2)\neq0.
$$

We now ask the question that makes elliptic curves exceptional:

> How can points on a cubic curve be **added**?

The answer begins with a remarkably simple geometric observation.

A line intersects a smooth cubic in three points, counting multiplicity.

From that fact we obtain:

$$
\boxed{
\text{secants}
\rightarrow
\text{point addition}
}
$$

and

$$
\boxed{
\text{tangents}
\rightarrow
\text{point doubling}.
}
$$

The resulting operation turns the points of an elliptic curve into an **abelian group**.

---

## Table of Contents

- [1. Weierstrass form revisited](#1-weierstrass-form-revisited)
- [2. Why a group law should exist](#2-why-a-group-law-should-exist)
- [3. Negating a point](#3-negating-a-point)
- [4. Geometric point addition](#4-geometric-point-addition)
- [5. Deriving the addition formulas](#5-deriving-the-addition-formulas)
- [Point doubling](#point-doubling)
- [7. Deriving the doubling formulas](#7-deriving-the-doubling-formulas)
- [8. Vertical lines and exceptional cases](#8-vertical-lines-and-exceptional-cases)
- [9. The point at infinity](#9-the-point-at-infinity)
- [10. Why the group is abelian](#10-why-the-group-is-abelian)
- [11. Why associativity is difficult](#11-why-associativity-is-difficult)
- [12. A complete numerical example](#12-a-complete-numerical-example)
- [Projective interpretation](#projective-interpretation)
- [14. A simple Python implementation](#14-a-simple-python-implementation)
- [15. From addition to scalar multiplication](#15-from-addition-to-scalar-multiplication)
- [16. The bigger picture](#16-the-bigger-picture)
- [Further reading](#further-reading)

---

## 1. Weierstrass form revisited

The general Weierstrass equation over a field $K$ is

$$
y^2+a_1xy+a_3y
=
x^3+a_2x^2+a_4x+a_6.
$$

When

$$
\operatorname{char}(K)\neq2,3,
$$

a suitable change of variables transforms this into short Weierstrass form:

$$
\boxed{
E:
y^2=x^3+ax+b.
}
$$

The curve must satisfy

$$
\boxed{
4a^3+27b^2\neq0
}
$$

or equivalently

$$
\Delta\neq0.
$$

This guarantees that the cubic is nonsingular.

For the rest of this chapter we assume short Weierstrass form and characteristic different from $2$ and $3$.

---

<a id="why-group-law"></a>

## 2. Why a group law should exist

Let

$$
P,Q\in E.
$$

Draw the line passing through $P$ and $Q$.

Because a line has degree $1$ and the elliptic curve has degree $3$, Bézout's theorem tells us that the line and the cubic meet in three points over an algebraic closure, counting multiplicity.

So if two intersections are known,

$$
P
\quad\text{and}\quad
Q,
$$

there is a third intersection

$$
R.
$$

This gives us a natural geometric operation.

But we do not define

$$
P+Q=R.
$$

Instead, we reflect $R$ across the $x$-axis.

If

$$
R=(x_R,y_R),
$$

then

$$
-R=(x_R,-y_R).
$$

The elliptic-curve sum is

$$
\boxed{
P+Q=-R.
}
$$

Thus:

1. draw the line through $P$ and $Q$;
2. find its third intersection with $E$;
3. reflect that point across the $x$-axis.

That reflected point is $P+Q$.

---

<a id="point-negation"></a>

## 3. Negating a point

The short Weierstrass equation is

$$
y^2=x^3+ax+b.
$$

If

$$
P=(x,y)
$$

lies on the curve, then

$$
y^2=x^3+ax+b.
$$

But

$$
(-y)^2=y^2.
$$

Therefore,

$$
(x,-y)
$$

also lies on the curve.

So the inverse of $P$ is

$$
\boxed{
-P=(x,-y).
}
$$

Geometrically, negation is reflection across the $x$-axis.

Therefore,

$$
P+(-P)=\mathcal O.
$$

This already explains one of the group axioms.

---

<a id="geometric-addition"></a>

## 4. Geometric point addition

Let

$$
P=(x_1,y_1)
$$

and

$$
Q=(x_2,y_2),
$$

with

$$
P\neq Q
$$

and

$$
x_1\neq x_2.
$$

The line through $P$ and $Q$ has slope

$$
\boxed{
\lambda
=
\frac{y_2-y_1}{x_2-x_1}.
}
$$

Its equation can be written as

$$
y
=
\lambda(x-x_1)+y_1.
$$

Equivalently,

$$
y=\lambda x+\nu,
$$

where

$$
\nu=y_1-\lambda x_1.
$$

This line intersects the elliptic curve in three points.

Two are $P$ and $Q$.

Let the third be

$$
R=(x_R,y_R).
$$

Then

$$
P+Q=-R.
$$

If we write

$$
P+Q=(x_3,y_3),
$$

then

$$
x_3=x_R
$$

and

$$
y_3=-y_R.
$$

---

<a id="addition-formulas"></a>

## 5. Deriving the addition formulas

Substitute

$$
y=\lambda x+\nu
$$

into

$$
y^2=x^3+ax+b.
$$

We obtain

$$
(\lambda x+\nu)^2
=
x^3+ax+b.
$$

Expanding,

$$
\lambda^2x^2
+
2\lambda\nu x
+
\nu^2
=
x^3+ax+b.
$$

Move everything to one side:

$$
x^3
-
\lambda^2x^2
+
(a-2\lambda\nu)x
+
(b-\nu^2)
=
0.
$$

The roots of this cubic equation are exactly the three $x$-coordinates

$$
x_1,
\qquad
x_2,
\qquad
x_R.
$$

By Vieta's formula,

$$
x_1+x_2+x_R=\lambda^2.
$$

Therefore,

$$
x_R
=
\lambda^2-x_1-x_2.
$$

Since reflection does not change the $x$-coordinate,

$$
\boxed{
x_3
=
\lambda^2-x_1-x_2.
}
$$

Now the third intersection lies on the line, so

$$
y_R
=
\lambda(x_R-x_1)+y_1.
$$

Reflecting gives

$$
y_3=-y_R.
$$

Therefore,

$$
y_3
=
-\lambda(x_3-x_1)-y_1.
$$

Equivalently,

$$
\boxed{
y_3
=
\lambda(x_1-x_3)-y_1.
}
$$

So for distinct points,

$$
\boxed{
\lambda
=
\frac{y_2-y_1}{x_2-x_1}
}
$$

and

$$
\boxed{
x_3=\lambda^2-x_1-x_2,
}
$$

$$
\boxed{
y_3=\lambda(x_1-x_3)-y_1.
}
$$

These formulas are not arbitrary algebra.

They are simply the coordinate form of the secant construction.

---

<a id="point-doubling"></a>

## Point doubling

What happens if

$$
P=Q?
$$

There is no unique secant line through two distinct points anymore.

Instead, we take the **tangent line** to the curve at $P$.

This corresponds to the line intersecting the cubic twice at $P$, counting multiplicity, and once more at another point $R$.

Then

$$
\boxed{
2P=P+P=-R.
}
$$

The geometry therefore remains exactly the same.

The only difference is how we compute the slope.

---

<a id="doubling-formulas"></a>

## 7. Deriving the doubling formulas

Start from

$$
y^2=x^3+ax+b.
$$

Differentiate implicitly with respect to $x$:

$$
2y\frac{dy}{dx}
=
3x^2+a.
$$

Therefore,

$$
\frac{dy}{dx}
=
\frac{3x^2+a}{2y}.
$$

At

$$
P=(x_1,y_1),
$$

the tangent slope is

$$
\boxed{
\lambda
=
\frac{3x_1^2+a}{2y_1}.
}
$$

The remaining coordinate formulas are the same as before, except now

$$
x_1=x_2.
$$

Therefore,

$$
\boxed{
x_3
=
\lambda^2-2x_1
}
$$

and

$$
\boxed{
y_3
=
\lambda(x_1-x_3)-y_1.
}
$$

Hence the complete doubling formula is

$$
\boxed{
\lambda
=
\frac{3x_1^2+a}{2y_1},
\qquad
x_3
=
\lambda^2-2x_1,
\qquad
y_3
=
\lambda(x_1-x_3)-y_1.
}
$$

---

<a id="exceptional-cases"></a>

## 8. Vertical lines and exceptional cases

The formulas contain divisions.

Therefore we must understand when the denominators vanish.

### Case 1: $P=-Q$

Suppose

$$
P=(x,y)
$$

and

$$
Q=(x,-y).
$$

Then

$$
x_1=x_2
$$

but

$$
P\neq Q.
$$

The line through them is vertical.

Projectively, the third intersection is

$$
\mathcal O.
$$

Therefore,

$$
\boxed{
P+(-P)=\mathcal O.
}
$$

---

### Case 2: Doubling a point with $y=0$

Suppose

$$
P=(x,0).
$$

Then

$$
P=-P.
$$

Therefore,

$$
P+P
=
P+(-P)
=
\mathcal O.
$$

So

$$
\boxed{
2P=\mathcal O.
}
$$

Such a point has order $2$.

Notice that the doubling slope formula also detects this special case because its denominator is

$$
2y=0.
$$

---

### Case 3: Adding the identity

By definition,

$$
\boxed{
P+\mathcal O
=
\mathcal O+P
=
P.
}
$$

And

$$
\boxed{
\mathcal O+\mathcal O
=
\mathcal O.
}
$$

These cases complete the operation globally.

---

<a id="point-at-infinity"></a>

## 9. The point at infinity

The previous chapter showed that the projective closure

$$
Y^2Z
=
X^3+aXZ^2+bZ^3
$$

contains the unique point

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

It is tempting to think of $\mathcal O$ as merely a convenient symbol.

It is not.

It is a genuine projective point on the curve.

Every affine vertical line has projective equation

$$
X-x_0Z=0.
$$

Setting

$$
Z=0
$$

forces

$$
X=0.
$$

Therefore the vertical line passes through

$$
(0:1:0)=\mathcal O.
$$

So if

$$
P=(x,y)
$$

and

$$
-P=(x,-y),
$$

the vertical line contains precisely the three cubic intersections

$$
P,
\qquad
-P,
\qquad
\mathcal O,
$$

counting multiplicity.

Thus

$$
P+(-P)=\mathcal O
$$

is not an arbitrary exception.

It follows from exactly the same three-intersection geometry as ordinary point addition.

---

<a id="abelian-group"></a>

## 10. Why the group is abelian

The points of $E$, together with $\mathcal O$, form an abelian group.

Let us examine the group axioms.

### Closure

For

$$
P,Q\in E,
$$

the geometric construction produces another point

$$
P+Q\in E.
$$

---

### Identity

$$
\boxed{
P+\mathcal O=P.
}
$$

---

### Inverses

For

$$
P=(x,y),
$$

$$
\boxed{
-P=(x,-y)
}
$$

and

$$
\boxed{
P+(-P)=\mathcal O.
}
$$

---

### Commutativity

The line through $P$ and $Q$ is the same line as the line through $Q$ and $P$.

Therefore the third intersection is identical.

Hence,

$$
\boxed{
P+Q=Q+P.
}
$$

Commutativity is therefore geometrically immediate.

---

### Associativity

We also require

$$
\boxed{
(P+Q)+R
=
P+(Q+R).
}
$$

This property is much deeper.

It is not visually obvious from the secant-and-tangent construction.

---

<a id="associativity"></a>

## 11. Why associativity is difficult

The geometric picture makes identity, inverses, and commutativity almost immediate.

Associativity is different.

Trying to prove directly that

$$
(P+Q)+R
=
P+(Q+R)
$$

using the coordinate formulas leads to a long rational-function calculation.

Such a proof is possible, but it hides the real mathematics.

A deeper explanation comes from divisor theory.

For an elliptic curve $E$, consider degree-zero divisor classes

$$
\operatorname{Pic}^0(E).
$$

This set already forms an abelian group.

A point

$$
P\in E
$$

can be associated with the divisor class

$$
[P-\mathcal O].
$$

For an elliptic curve, the map

$$
\boxed{
P
\longmapsto
[P-\mathcal O]
}
$$

identifies $E$ with its degree-zero Picard group.

Now suppose a line intersects the cubic at

$$
P,
\qquad
Q,
\qquad
R.
$$

The geometry of divisors implies

$$
[P-\mathcal O]
+
[Q-\mathcal O]
+
[R-\mathcal O]
=
0.
$$

Therefore,

$$
[P-\mathcal O]
+
[Q-\mathcal O]
=
-[R-\mathcal O].
$$

This is exactly the geometric rule

$$
P+Q=-R.
$$

Because divisor-class addition is associative, elliptic-curve addition is associative.

So the real reason

$$
(P+Q)+R
=
P+(Q+R)
$$

is not simply a lucky property of the coordinate formulas.

It comes from the deeper algebraic structure of the curve.

For an introductory treatment, it is enough to remember:

$$
\boxed{
\text{secant/tangent geometry defines the law;}
}
$$

$$
\boxed{
\text{divisor theory explains why it is associative.}
}
$$

---

<a id="numerical-example"></a>

## 12. A complete numerical example

Consider

$$
E:
y^2=x^3-2x+4
$$

over the real numbers.

So

$$
a=-2,
\qquad
b=4.
$$

Take

$$
P=(0,2)
$$

and

$$
Q=(1,\sqrt3).
$$

Check $P$:

$$
2^2=4
$$

and

$$
0^3-2(0)+4=4.
$$

So $P\in E$.

For $Q$,

$$
(\sqrt3)^2=3
$$

and

$$
1^3-2(1)+4=3.
$$

Thus

$$
Q\in E.
$$

The slope is

$$
\lambda
=
\frac{\sqrt3-2}{1-0}
=
\sqrt3-2.
$$

Then

$$
x_3
=
(\sqrt3-2)^2-0-1.
$$

Since

$$
(\sqrt3-2)^2
=
7-4\sqrt3,
$$

we obtain

$$
x_3
=
6-4\sqrt3.
$$

Now

$$
y_3
=
\lambda(x_1-x_3)-y_1.
$$

Thus

$$
y_3
=
(\sqrt3-2)(-6+4\sqrt3)-2.
$$

After simplification,

$$
y_3
=
16\sqrt3-28.
$$

Therefore,

$$
\boxed{
P+Q
=
(6-4\sqrt3,\;16\sqrt3-28).
}
$$

The arithmetic may look messy over $\mathbb R$, but the same algebra works over finite fields.

There, division simply becomes multiplication by a modular inverse.

---

<a id="projective-interpretation"></a>

## Projective interpretation

Chapter I developed projective space in detail.

Here we only need to recall why it matters for the group law.

The affine curve

$$
y^2=x^3+ax+b
$$

becomes

$$
Y^2Z
=
X^3+aXZ^2+bZ^3.
$$

The unique point at infinity is

$$
\mathcal O=(0:1:0).
$$

The affine plane appears as the slice

$$
Z=1.
$$

The line

$$
Z=0
$$

is the line at infinity.

<div style="text-align:center">

<img src="/images/ready/elliptic-curves-group-law/projection.PNG" width="500"/><br/>

<em>Projective points represent one-dimensional lines through the origin.</em>

</div>

The affine chart can be visualized as a slice of projective space:

<div style="text-align:center">

<img src="/images/ready/elliptic-curves-group-law/affine.PNG" width="250"/><br/>

<em>The affine plane is the chart $Z=1$; points with $Z=0$ form the line at infinity.</em>

</div>

For the elliptic curve, only one point of that line belongs to the cubic:

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

<div style="text-align:center">

<img src="/images/ready/elliptic-curves-group-law/2Dplane.PNG" width="600"/><br/>

<em>The affine elliptic curve together with its projective identity point $\mathcal O$.</em>

</div>

This projective completion is what makes the group law uniform.

Without it, the statement

$$
P+(-P)=\mathcal O
$$

would appear to introduce an artificial exception.

Projectively, it is simply another line-cubic intersection.

---

<a id="python-implementation"></a>

## 14. A simple Python implementation

The following implementation illustrates the group law over the real numbers.

It is intentionally simple.

```python
import math

O = None


def elliptic_add(P, Q, a):
    """
    Add two points on the short Weierstrass curve

        y^2 = x^3 + a*x + b

    over the real numbers.

    The parameter b is not needed by the addition formulas themselves.
    The point at infinity is represented by None.
    """

    if P is O:
        return Q

    if Q is O:
        return P

    x1, y1 = P
    x2, y2 = Q

    # P + (-P) = O
    if x1 == x2 and y1 == -y2:
        return O

    # Point doubling
    if P == Q:
        if y1 == 0:
            return O

        lam = (3 * x1**2 + a) / (2 * y1)

    # Distinct-point addition
    else:
        lam = (y2 - y1) / (x2 - x1)

    x3 = lam**2 - x1 - x2
    y3 = lam * (x1 - x3) - y1

    return (x3, y3)
```

This code represents

$$
\mathcal O
$$

with Python's

```python
None
```

rather than pretending that the point at infinity has affine coordinates such as

```text
(0, infinity).
```

That distinction is mathematically cleaner.

The point

$$
\mathcal O
$$

does **not** have ordinary affine coordinates.

---

### Important: finite fields require different arithmetic

The formulas remain the same over

$$
\mathbb F_p,
$$

but ordinary division must be replaced by multiplication by a modular inverse.

For example,

$$
\frac{y_2-y_1}{x_2-x_1}
$$

means

$$
(y_2-y_1)(x_2-x_1)^{-1}
\pmod p.
$$

So the mathematical group law is unchanged, but the arithmetic domain changes.

This distinction becomes crucial when we move from curve visualization to actual elliptic-curve cryptography.

---

### Complete implementation

A more complete class-based implementation is available at:

[`src/fullec.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/ready-material/elliptic-curves/src/fullec.py)

It includes:

* point representation;
* identity handling;
* point addition;
* point doubling;
* curve-membership checks;
* the basic infrastructure required for scalar multiplication.

---

<a id="scalar-multiplication"></a>

## 15. From addition to scalar multiplication

Once point addition exists, we can repeatedly add a point to itself.

Define

$$
2P=P+P,
$$

$$
3P=P+P+P,
$$

and generally

$$
\boxed{
[n]P
=
\underbrace{
P+\cdots+P
}_{n\text{ times}}.
}
$$

This operation is called **scalar multiplication**.

It is the central computational operation in elliptic-curve cryptography.

But computing

$$
[n]P
$$

by literally performing $n-1$ additions would be extremely inefficient.

Instead, we exploit the binary representation of $n$.

For example,

$$
13=8+4+1.
$$

Therefore,

$$
13P
=
8P+4P+P.
$$

The multiples

$$
2P,
\qquad
4P,
\qquad
8P
$$

can be obtained by repeated doubling.

This leads to the **double-and-add algorithm**, the elliptic-curve analogue of square-and-multiply modular exponentiation.

Its complexity is approximately

$$
O(\log n)
$$

group operations rather than

$$
O(n).
$$

This operation will become central once we move to finite fields.

---

<a id="bigger-picture"></a>

## 16. The bigger picture

We can now trace the complete construction.

Start with a nonsingular cubic:

$$
\boxed{
E:
y^2=x^3+ax+b.
}
$$

Its projective completion provides

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

A line through two curve points meets the cubic a third time:

$$
\boxed{
P,Q
\rightarrow
R.
}
$$

Reflection gives

$$
\boxed{
P+Q=-R.
}
$$

When

$$
P=Q,
$$

replace the secant by the tangent:

$$
\boxed{
P
\rightarrow
2P.
}
$$

The inverse is

$$
\boxed{
-(x,y)=(x,-y).
}
$$

Vertical lines give

$$
\boxed{
P+(-P)=\mathcal O.
}
$$

The resulting structure satisfies

$$
\boxed{
P+\mathcal O=P,
}
$$

$$
\boxed{
P+(-P)=\mathcal O,
}
$$

$$
\boxed{
P+Q=Q+P,
}
$$

and

$$
\boxed{
(P+Q)+R=P+(Q+R).
}
$$

Therefore,

$$
\boxed{
E(K)
\text{ is an abelian group}.
}
$$

This is the first major transition in elliptic-curve mathematics:

$$
\boxed{
\text{geometry}
\longrightarrow
\text{algebra}.
}
$$

A smooth cubic is no longer merely a collection of points.

Its points can be calculated with.

And repeated addition gives the operation

$$
[n]P
$$

that ultimately becomes the computational foundation of elliptic-curve cryptography.

---

## Further reading

Useful references for this chapter include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Darrel Hankerson, Alfred Menezes, and Scott Vanstone, **Guide to Elliptic Curve Cryptography**.
* Ian Blake, Gadiel Seroussi, and Nigel Smart, **Elliptic Curves in Cryptography**.
* Jeffrey Hoffstein, Jill Pipher, and Joseph H. Silverman, **An Introduction to Mathematical Cryptography**.

---

The next chapter moves from curves over the real numbers to the setting that matters directly for cryptography:

$$
\boxed{
E(\mathbb F_p).
}
$$

The geometric formulas remain almost unchanged.

But the underlying world changes completely.

There is no continuous curve to draw.

There is only a finite set of points satisfying

$$
y^2\equiv x^3+ax+b\pmod p.
$$

We will study:

* finite-field arithmetic;
* modular inverses;
* quadratic residues;
* counting points;
* the structure of $E(\mathbb F_p)$;
* Hasse's theorem;
* point orders and subgroups.

That is where elliptic curves begin to move from algebraic geometry toward cryptography.
