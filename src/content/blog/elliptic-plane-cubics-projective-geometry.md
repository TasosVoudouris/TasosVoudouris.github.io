---
title: "Elliptic Curve Mathematics I: Plane Cubics, Projective Closure, and Nonsingularity"
description: "Why elliptic curves are smooth projective cubic curves: affine and projective models, homogenization, the point at infinity, singularities, discriminants, and the geometric setting for the group law."
pubDate: "2025-03-19"
updatedDate: "2026-09-17"

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
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 1
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

An elliptic curve is not merely a real graph with a characteristic symmetric shape.

That picture is useful for intuition, but it is not the mathematical definition.

An **elliptic curve over a field \(K\)** is a smooth projective curve of genus one together with a distinguished \(K\)-rational point.

Symbolically, we should think of an elliptic curve as

$$
\boxed{
(E,\mathcal O)
}
$$

where

* \(E\) is a smooth projective genus-one curve;
* \(\mathcal O\in E(K)\) is a distinguished rational point.

The point \(\mathcal O\) will later become the identity element of the elliptic-curve group.

For most explicit calculations, elliptic curves are represented by **Weierstrass equations**.

This chapter builds the geometric foundation behind that representation.

---

## Contents

- [1. What an elliptic curve actually is](#1-what-an-elliptic-curve-actually-is)
- [2. Affine plane cubics](#2-affine-plane-cubics)
- [3. Weierstrass equations](#3-weierstrass-equations)
- [4. From affine to projective space](#4-from-affine-to-projective-space)
- [5. Homogenizing the cubic](#5-homogenizing-the-cubic)
- [6. The point at infinity](#6-the-point-at-infinity)
- [7. Singular and nonsingular points](#7-singular-and-nonsingular-points)
- [8. Deriving the discriminant condition](#8-deriving-the-discriminant-condition)
- [9. What happens at infinity?](#9-what-happens-at-infinity)
- [10. Why singular cubics are fundamentally different](#10-why-singular-cubics-are-fundamentally-different)
- [11. Lines, tangents, and Bézout’s theorem](#11-lines-tangents-and-bézouts-theorem)
- [12. Intersection multiplicity](#12-intersection-multiplicity)
- [13. Why projective geometry is necessary](#13-why-projective-geometry-is-necessary)
- [14. From geometry to the future group law](#14-from-geometry-to-the-future-group-law)
- [The central picture](#the-central-picture)
- [Further reading](#further-reading)

---

## 1. What an elliptic curve actually is

The standard definition is:

> An elliptic curve over a field \(K\) is a smooth projective algebraic curve of genus one together with a distinguished \(K\)-rational point.

Every word matters.

### Curve

The object is one-dimensional in the sense of algebraic geometry.

### Projective

The curve is completed by adding the appropriate points at infinity.

### Smooth

It has no singularities such as cusps or nodes.

### Genus one

Topologically, over the complex numbers, the curve has the shape of a torus.

### Distinguished rational point

We choose

$$
\mathcal O\in E(K).
$$

This point allows the curve to acquire a group structure.

A subtle but important distinction follows.

A smooth projective curve of genus one **without a \(K\)-rational point** is a genus-one curve, but it is not yet an elliptic curve over \(K\).

The rational base point is part of the definition.

---

## 2. Affine plane cubics

An affine plane algebraic curve is defined by a polynomial equation

$$
F(x,y)=0.
$$

A **plane cubic** is one for which

$$
\deg F=3.
$$

For example,

$$
y^2=x^3-x+1
$$

is a plane cubic because the highest total degree appearing is \(3\).

Over the real numbers we can draw such curves and obtain the familiar shapes often associated with elliptic curves.

But cryptography frequently works over finite fields such as

$$
\mathbb F_p.
$$

There, there is no smooth real graph.

Instead, the curve is simply the finite set

$$
E(\mathbb F_p)
=
\left\{
(x,y)\in\mathbb F_p^2:
F(x,y)=0
\right\}
$$

together with its point at infinity.

So the geometry must be defined algebraically rather than visually.

---

## 3. Weierstrass equations

A general Weierstrass equation has the form

$$
y^2+a_1xy+a_3y
=
x^3+a_2x^2+a_4x+a_6.
$$

The coefficients lie in the base field \(K\).

When

$$
\operatorname{char}(K)\neq2,3,
$$

a change of variables allows us to simplify this to **short Weierstrass form**:

$$
\boxed{
E:
y^2=x^3+ax+b.
}
$$

This is the form most often used when introducing elliptic curves.

The restriction

$$
\operatorname{char}(K)\neq2,3
$$

matters.

In characteristics \(2\) and \(3\), the transformations used to eliminate certain terms require division by \(2\) or \(3\), which is impossible when those elements vanish in the field.

Therefore the long Weierstrass equation is the more general model.

For the rest of this chapter, unless stated otherwise, we work with

$$
\operatorname{char}(K)\neq2,3
$$

and

$$
E:
y^2=x^3+ax+b.
$$

---

## 4. From affine to projective space

The affine plane

$$
\mathbb A^2
$$

contains ordinary coordinates

$$
(x,y).
$$

But affine geometry does not naturally contain points at infinity.

To complete the curve, we move to the projective plane

$$
\mathbb P^2.
$$

A projective point is written

$$
(X:Y:Z).
$$

The coordinates are defined only up to nonzero scalar multiplication:

$$
(X:Y:Z)
=
(\lambda X:\lambda Y:\lambda Z)
$$

for every

$$
\lambda\neq0.
$$

Thus

$$
(1:2:3)
=
(2:4:6).
$$

The affine plane sits inside projective space as the chart

$$
Z\neq0.
$$

If

$$
Z\neq0,
$$

we can divide by \(Z\) and write

$$
x=\frac{X}{Z},
\qquad
y=\frac{Y}{Z}.
$$

The affine point

$$
(x,y)
$$

therefore corresponds to

$$
(x:y:1).
$$

The new points arise when

$$
Z=0.
$$

These are the **points at infinity**.

---

## 5. Homogenizing the cubic

Start with

$$
y^2=x^3+ax+b.
$$

Substitute

$$
x=\frac XZ,
\qquad
y=\frac YZ.
$$

Then

$$
\left(\frac YZ\right)^2
=
\left(\frac XZ\right)^3
+
a\frac XZ
+
b.
$$

Multiply by \(Z^3\):

$$
Y^2Z
=
X^3
+
aXZ^2
+
bZ^3.
$$

Thus the projective equation is

$$
\boxed{
Y^2Z
=
X^3+aXZ^2+bZ^3.
}
$$

Equivalently, define the homogeneous cubic polynomial

$$
F(X,Y,Z)
=
Y^2Z-X^3-aXZ^2-bZ^3.
$$

Then the projective curve is

$$
E:
F(X,Y,Z)=0.
$$

Every term now has total degree \(3\):

$$
\deg(Y^2Z)=3,
$$

$$
\deg(X^3)=3,
$$

$$
\deg(XZ^2)=3,
$$

$$
\deg(Z^3)=3.
$$

That is exactly what homogenization accomplishes.

---

## 6. The point at infinity

To find the points missing from the affine picture, set

$$
Z=0.
$$

Then

$$
Y^2Z
=
X^3+aXZ^2+bZ^3
$$

becomes

$$
0=X^3.
$$

Therefore,

$$
X=0.
$$

A projective point cannot have all coordinates equal to zero, so

$$
Y\neq0.
$$

By projective scaling,

$$
(0:Y:0)
=
(0:1:0).
$$

Thus there is exactly one point at infinity:

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

This point is defined over the base field.

It becomes the distinguished rational point in the standard Weierstrass model.

Later we will define

$$
P+\mathcal O=P
$$

for every point \(P\in E\).

So \(\mathcal O\) is not an artificial bookkeeping device.

It is the identity element required to complete the group law.

---

## 7. Singular and nonsingular points

Now we need the smoothness condition.

Consider a projective plane curve

$$
F(X,Y,Z)=0.
$$

A point

$$
P=(X:Y:Z)
$$

on the curve is **singular** if

$$
F(P)=0
$$

and every first partial derivative vanishes:

$$
F_X(P)=0,
$$

$$
F_Y(P)=0,
$$

$$
F_Z(P)=0.
$$

If no such point exists, the curve is nonsingular or smooth.

For our Weierstrass cubic,

$$
F(X,Y,Z)
=
Y^2Z-X^3-aXZ^2-bZ^3.
$$

The partial derivatives are

$$
F_X
=
-3X^2-aZ^2,
$$

$$
F_Y
=
2YZ,
$$

and

$$
F_Z
=
Y^2-2aXZ-3bZ^2.
$$

A singular point would therefore need to satisfy all four equations simultaneously:

$$
F=0,
\qquad
F_X=0,
\qquad
F_Y=0,
\qquad
F_Z=0.
$$

---

## 8. Deriving the discriminant condition

The standard condition

$$
4a^3+27b^2\neq0
$$

does not appear magically.

We can derive it directly.

Work first in the affine chart

$$
Z=1.
$$

The curve is

$$
F(x,y)
=
y^2-x^3-ax-b.
$$

Its partial derivatives are

$$
F_x
=
-3x^2-a
$$

and

$$
F_y
=
2y.
$$

At a singular point we require

$$
F_y=0.
$$

Since

$$
\operatorname{char}(K)\neq2,
$$

this implies

$$
y=0.
$$

We also require

$$
F_x=0,
$$

so

$$
3x^2+a=0.
$$

And because the point lies on the curve,

$$
x^3+ax+b=0.
$$

Therefore \(x\) must simultaneously satisfy

$$
3x^2+a=0
$$

and

$$
x^3+ax+b=0.
$$

In other words, the cubic polynomial

$$
f(x)=x^3+ax+b
$$

must have a repeated root.

A polynomial has a repeated root exactly when it shares a root with its derivative

$$
f'(x)=3x^2+a.
$$

Equivalently,

$$
\gcd(f,f')\neq1.
$$

The discriminant of

$$
x^3+ax+b
$$

is

$$
-4a^3-27b^2.
$$

For the elliptic curve equation, a conventional discriminant is

$$
\boxed{
\Delta
=
-16(4a^3+27b^2).
}
$$

Thus the curve is nonsingular precisely when

$$
\boxed{
\Delta\neq0.
}
$$

Equivalently,

$$
\boxed{
4a^3+27b^2\neq0.
}
$$

This is not merely a parameter check.

It says exactly that the cubic polynomial on the right-hand side has no repeated root.

---

## 9. What happens at infinity?

We should also verify that

$$
\mathcal O=(0:1:0)
$$

is not singular.

Recall

$$
F_Z
=
Y^2-2aXZ-3bZ^2.
$$

At

$$
\mathcal O=(0:1:0),
$$

we obtain

$$
F_Z(\mathcal O)
=
1.
$$

Therefore,

$$
F_Z(\mathcal O)\neq0.
$$

So

$$
\boxed{
\mathcal O
\text{ is always nonsingular in the short Weierstrass model}.
}
$$

Thus any singularity must occur in the affine part of the curve.

That is why the discriminant calculation above captures the complete smoothness condition.

---

## 10. Why singular cubics are fundamentally different

Consider

$$
y^2=x^3.
$$

Here

$$
a=0,
\qquad
b=0,
$$

so

$$
\Delta=0.
$$

At

$$
(0,0),
$$

we have

$$
F(0,0)=0,
$$

$$
F_x(0,0)=0,
$$

and

$$
F_y(0,0)=0.
$$

The curve has a **cusp**.

Another cubic may instead have a **node**, where two local branches cross.

These are not cosmetic defects.

They change the algebraic structure of the curve.

A smooth cubic has genus one.

A singular cubic effectively loses genus after normalization and behaves much more like a rational curve.

In suitable cases, the group on the nonsingular points of a singular cubic becomes closely related to simpler algebraic groups such as

$$
(K,+)
$$

or

$$
K^\times.
$$

Thus the condition

$$
\Delta\neq0
$$

marks a genuine structural boundary.

It is not merely a cryptographic recommendation added after the mathematics.

Smoothness is part of what makes the object an elliptic curve.

---

## 11. Lines, tangents, and Bézout's theorem

Why do cubic curves naturally acquire a group law?

The geometric clue comes from intersections with lines.

A line has degree

$$
1.
$$

A cubic has degree

$$
3.
$$

Bézout's theorem tells us, under the appropriate hypotheses and over an algebraic closure, that two projective plane curves of degrees \(m\) and \(n\) intersect in

$$
mn
$$

points counting intersection multiplicities.

For a line and a cubic:

$$
1\cdot3=3.
$$

Therefore a line intersects a cubic in exactly three points, counting multiplicity.

Suppose a line passes through two points

$$
P,Q\in E.
$$

Then there is a third intersection point

$$
R.
$$

This is the geometric starting point of elliptic-curve addition.

Very roughly,

$$
P+Q
$$

will be obtained from this third intersection after applying the natural reflection symmetry of the Weierstrass equation.

We will derive that carefully in the next chapter.

---

## 12. Intersection multiplicity

What happens if

$$
P=Q?
$$

Then there are not two distinct points through which to draw a secant line.

Instead, we use the tangent line at \(P\).

The tangent touches the curve with intersection multiplicity at least two at \(P\).

So Bézout still counts

$$
P+P+R
$$

as three intersections when multiplicities are included.

This is the geometric origin of **point doubling**.

Similarly, special cases can produce an intersection multiplicity of three at one point.

Thus the group law is not based merely on a visual rule.

It is rooted in algebraic intersection theory.

---

## 13. Why projective geometry is necessary

Suppose we work only in affine coordinates.

Take two points having the same \(x\)-coordinate:

$$
P=(x,y)
$$

and

$$
-P=(x,-y).
$$

The line through them is vertical:

$$
x=\text{constant}.
$$

In the affine plane, this line appears to intersect the curve only at those two points.

But Bézout predicts a third intersection.

Where did it go?

It lies at infinity.

The vertical line also passes through

$$
\mathcal O=(0:1:0).
$$

Thus projectively,

$$
P,
\qquad
-P,
\qquad
\mathcal O
$$

are the three intersections.

This immediately motivates

$$
P+(-P)=\mathcal O.
$$

So the inverse of

$$
P=(x,y)
$$

in short Weierstrass form becomes

$$
\boxed{
-P=(x,-y).
}
$$

And the identity is

$$
\boxed{
\mathcal O.
}
$$

Without projective geometry, these cases appear to require arbitrary exceptions.

With projective geometry, they are part of the same intersection rule.

---

## 14. From geometry to the future group law

We can now see why each ingredient in the definition matters.

Start with an affine cubic:

$$
y^2=x^3+ax+b.
$$

Projectivize it:

$$
Y^2Z
=
X^3+aXZ^2+bZ^3.
$$

This introduces the unique point at infinity:

$$
\mathcal O=(0:1:0).
$$

Require

$$
\Delta\neq0
$$

so that the curve is smooth.

Now a projective line meets the cubic in three points counting multiplicity.

Therefore:

$$
\boxed{
\text{two points}
\rightarrow
\text{line}
\rightarrow
\text{third intersection}.
}
$$

When the two points coincide:

$$
\boxed{
\text{one point twice}
\rightarrow
\text{tangent}
\rightarrow
\text{third intersection}.
}
$$

When the line is vertical:

$$
\boxed{
P,\,-P,\mathcal O
}
$$

are the three intersections.

All of the future group-law rules are already hiding inside this geometry.

---

## The central picture

We can summarize the entire chapter as

$$
\boxed{
y^2=x^3+ax+b
}
$$

$$
\Downarrow
\quad
\text{homogenize}
$$

$$
\boxed{
Y^2Z=X^3+aXZ^2+bZ^3
}
$$

$$
\Downarrow
$$

$$
\boxed{
\mathcal O=(0:1:0)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\Delta=-16(4a^3+27b^2)\neq0
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{smooth projective cubic}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{genus one + rational base point}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{elliptic curve}.
}
$$

And once the curve is smooth and projective, Bézout gives the geometric mechanism from which addition emerges:

$$
\boxed{
\text{line}
+
\text{cubic}
\Rightarrow
3\text{ intersections counting multiplicity}.
}
$$

That is where the elliptic-curve group law begins.

---

## Further reading

Useful references for the material in this chapter include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Ian Blake, Gadiel Seroussi, and Nigel Smart, **Elliptic Curves in Cryptography**.
* Darrel Hankerson, Alfred Menezes, and Scott Vanstone, **Guide to Elliptic Curve Cryptography**.
* Jeffrey Hoffstein, Jill Pipher, and Joseph H. Silverman, **An Introduction to Mathematical Cryptography**.

---

The next chapter will turn the geometry into an actual algebraic operation.

Starting from two points

$$
P,Q\in E,
$$

we will derive the secant-and-tangent group law, obtain the explicit addition and doubling formulas, explain inverses and exceptional cases, and then ask the deeper question:

> **why is this operation actually associative?**

That is where a smooth cubic stops being merely a geometric curve and becomes an algebraic group.
