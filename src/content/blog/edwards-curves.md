---
title: "Elliptic Curve Mathematics IX: Edwards and Twisted Edwards Curves"
description: "A detailed introduction to Edwards models, their group law, notable points, and birational connections with Weierstrass and Montgomery forms."
pubDate: "2025-05-25"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Mathematical Foundations"
tags:
- "edwards-curves"
- "twisted-edwards"
- "montgomery-curves"
- "birational-equivalence"
difficulty: "Advanced"
series: "Elliptic Curve Mathematics"
seriesOrder: 9
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
After exploring *Montgomery curves* and their efficient arithmetic properties, we now turn our attention to another important family of elliptic curves: *Edwards curves*. These curves offer unified and efficient addition formulas, making them particularly attractive for cryptographic applications. In this section, we will introduce the Edwards form, examine its group law, and explore its advantages in secure and fast computations on elliptic curves.

## The Unit Circle and Motivating Idea

To understand Edwards curves intuitively, we begin with the unit circle defined by the equation:

$$
y^2 + x^2 = 1
$$

This equation naturally corresponds to the trigonometric identity for addition of angles. By substituting $(x, y) = (\sin \alpha, \cos \alpha)$, we can derive an addition law that mimics angle addition:

$$
\begin{aligned}
\sin(\alpha_1 + \alpha_2)
&= \sin \alpha_1 \cos \alpha_2 + \cos \alpha_1 \sin \alpha_2, \\
\cos(\alpha_1 + \alpha_2)
&= \cos \alpha_1 \cos \alpha_2 - \sin \alpha_1 \sin \alpha_2.
\end{aligned}
$$

This leads to the group law:

$$
(x_1,y_1), (x_2,y_2) \mapsto (x_1y_2 + y_1x_2, y_1y_2 - x_1x_2)
$$


<p align="center">
  <img src="/images/ready/edwards-curves/edwardcurve.PNG" alt="Edwards curve addition via rotation and reflection">
</p>


The diagram above illustrates the symmetry of the Edwards curve. Given a point $(x, y)$, the image shows how basic additions with elements like $(0, \pm1), (\pm1, 0)$ result in rotations and reflections. These four special points $(0, \pm1), (\pm1, 0)$ form a cyclic group of order 4 and act as fundamental symmetries of the curve.


### From Original to Standard Form

The *original form* of Edwards curves was given by:

$$
\textbf{Original Form:} \quad x^2 + y^2 = c^2(1 + x^2 y^2)
$$

This formulation is valid over certain finite fields but has limited general applicability. To overcome these limitations, Bernstein and Lange introduced a simplified and more widely usable form, now known as the *standard Edwards curve*.

Let $K$ be a field with characteristic not equal to 2, i.e., $\text{char}(K) \neq 2$, and let $d \in K \setminus \{0,1\}$. Then the *standard Edwards curve* over $K$ is defined by:

$$
\boxed{x^2 + y^2 = 1 + d x^2 y^2}
$$

Here, the parameter $d$ must be *nonzero and not equal to 1*, and in practice, it's often chosen to be a *non-square* in $\mathbb{F}_p$. This ensures that the addition law on the curve is *complete*, meaning that the group operation is defined for all input pairs without exception—an important property for cryptographic robustness.


## Group Law on Edwards Curves

Given points $(x_1, y_1)$ and $(x_2, y_2)$, define addition as:

$$
(x_{1},y_{1})+(x_{2},y_{2}) = \left(\frac{x_{1}y_{2}+x_{2}y_{1}}{1+dx_{1}x_{2}y_{1}y_{2}}, \frac{y_{1}y_{2}-x_{1}x_{2}}{1-dx_{1}x_{2}y_{1}y_{2}}\right)
$$

* *Identity element:* $(0, 1)$
* *Negation:* $(x, y) \mapsto (-x, y)$
* Doubling can be done using the same formula.

Due to symmetry in the equation, if $(x, y)$ is a point, then so are $(\pm x, \pm y)$ and $(\pm y, \pm x)$.

### Notable Points

The points $\{(0, 1), (0, -1), (1, 0), (-1, 0)\}$ always lie on the curve and form a cyclic subgroup of order 4.

> Every Edwards curve is birationally equivalent to an elliptic curve in Weierstrass form. However, a necessary condition for Edwards form is that the curve must admit a point of order 4.

## Birational Equivalence with Weierstrass and Montgomery Forms

### From Edwards to Weierstrass

Let $E_d$ be an Edwards curve defined by:

$$
x^2 + y^2 = 1 + d x^2 y^2
$$

and let $E$ be a Weierstrass curve over the same field.

A classical transformation maps $E_d$ to the Weierstrass curve:

$$
v^2 = u^3 + 2(d + 1)u^2 + (d - 1)^2 u
$$

The birational maps are:

* *Forward map* (Edwards $\to$ Weierstrass):

$$
(x, y) \mapsto \left( u, v \right) = \left( \frac{A}{x^2}, \frac{-2A}{x^3} \right), \quad A = 2y - (2dy + d + 1)x^2 + 2
$$

* *Inverse map* (Weierstrass $\to$ Edwards):

$$
(u, v) \mapsto \left( x, y \right) = \left( \frac{-2u}{v}, \frac{v^2 - (2 + 2d)u^2 - 2u^3}{4du^2 - v^2} \right)
$$

These expressions provide an explicit rational isomorphism, assuming the denominators are defined over the field.

An alternative standard transformation used in cryptographic settings maps $E_d$ to the Weierstrass curve:

$$
\frac{1}{e} v^2 = u^3 + \left( \frac{4}{e} - 2 \right) u^2 + u, \quad \text{where } e = 1 - d
$$

With:

* Forward map:

$$
(x, y) \mapsto \left( \frac{1 + y}{1 - y}, \frac{2(1 + y)}{x(1 - y)} \right)
$$

* Inverse map:

$$
(u, v) \mapsto \left( \frac{2u}{v}, \frac{u - 1}{u + 1} \right)
$$

Both maps are correct and used depending on the construction and desired normalization of the Weierstrass form. They differ in their algebraic rearrangement and implicit curve parameters.

## Twisted Edwards Curves

Twisted Edwards curves generalize Edwards curves and remove the constraint of requiring a point of order 4. This generality allows a larger class of elliptic curves to be expressed in a uniform format.


Let $K$ be a field with $\text{char}(K) \neq 2$. A twisted Edwards curve is given by:

$$
\boxed{ax^2 + y^2 = 1 + dx^2y^2}, \quad a \neq d \neq 0
$$

* When $a = 1$, we recover the standard Edwards curve.

### Group Law

Given points $(x_1, y_1)$ and $(x_2, y_2)$, their sum is:

$$
(x_{1},y_{1})+(x_{2},y_{2}) = \left( \frac{x_{1}y_{2}+x_{2}y_{1}}{1+dx_{1}x_{2}y_{1}y_{2}}, \frac{y_{1}y_{2}-ax_{1}x_{2}}{1-dx_{1}x_{2}y_{1}y_{2}} \right)
$$

* *Identity:* $(0, 1)$
* *Negation:* $(x, y) \mapsto (-x, y)$

### j-invariant

The $j$-invariant of a twisted Edwards curve is:

$$
\frac{16(a^2 + 14ad + d^2)^3}{ad(a - d)^4}
$$


### From Twisted Edwards to Montgomery

Let a twisted Edwards curve be defined by:

$$
a x^2 + y^2 = 1 + d x^2 y^2, \quad a \neq d \neq 0
$$

Then it is birationally equivalent to a Montgomery curve of the form:

$$
M_{A,B}: \quad By^2 = x^3 + Ax^2 + x
$$

The conversion between the two is:

* *Twisted Edwards to Montgomery*:

$$
(x, y) \mapsto \left( \frac{1 + y}{1 - y}, \frac{1 + y}{x(1 - y)} \right)
$$

$$
A = \frac{2(a + d)}{a - d}, \quad B = \frac{4}{a - d}
$$

* *Montgomery to Twisted Edwards*:

$$
(u, v) \mapsto \left( \frac{u}{v}, \frac{u - 1}{u + 1} \right)
$$

$$
a = \frac{A + 2}{B}, \quad d = \frac{A - 2}{B}
$$

This equivalence is fundamental in modern elliptic curve cryptography: many implementations use Montgomery form for fast scalar multiplication (e.g., X25519), while internally relying on twisted Edwards forms for completeness and unified arithmetic.


A full implementantion of Edward curves can be found in `src/edwards.sage`.
