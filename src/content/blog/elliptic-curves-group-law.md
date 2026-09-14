---
title: "Elliptic Curve Mathematics II: Weierstrass Curves and the Group Law"
description: "A detailed introduction to elliptic curves, Weierstrass form, geometric point addition, point doubling, inverses, and the group law."
pubDate: "2025-05-25"
updatedDate: '2026-09-12'
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
series: "Elliptic Curve Mathematics"
seriesOrder: 2
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
Elliptic curves are central objects in number theory and modern cryptography. In this section, we introduce their algebraic definition, explore their geometry, and describe how a group structure emerges from their points.

## General Form and Simplified Weierstrass Equation

The general Weierstrass form of an elliptic curve over a field (typically of characteristic not equal to 2 or 3) is given by:

$$
y^2 + a_1xy + a_3y = x^3 + a_2x^2 + a_4x + a_6
$$

Through an appropriate change of variables, this can be simplified to the **short Weierstrass form**:

$$
y^2 = x^3 + ax + b
$$

This simplified form is widely used in both theory and applications. For the curve to be **non-singular**, it must satisfy the condition:

$$
\Delta = 16(4a^3 + 27b^2) \neq 0
$$

which guarantees that the curve has no cusps or self-intersections.

## Visualizing Elliptic Curves

Elliptic curves defined over the real numbers $\mathbb{R}$ can be visualized by plotting the solution set of the equation $y^2 = x^3 + ax + b$ in the plane. For example, using Python:

```python
import numpy as np
import matplotlib.pyplot as plt

a = -3
b = 5
y, x = np.ogrid[-5:5:100j, -5:5:100j]
plt.contour(x.ravel(), y.ravel(), pow(y, 2) - pow(x, 3) - x * a - b, [0])
plt.grid()
plt.show()
```

This allows us to experiment with different values of $a$ and $b$ to observe how the shape of the curve changes.

## Group Law on Elliptic Curves

One of the most remarkable properties of elliptic curves is that their points form an abelian group under a geometric addition operation. Specifically, let:

* $E: y^2 = x^3 + ax + b$ be an elliptic curve,
* $P, Q \in E$ be points on the curve,
* and $\mathcal{O}$ be the *point at infinity*, which acts as the group identity element.

### Geometric Construction of Point Addition

The group law is defined by the following geometric rules:

* Given two points $P$ and $Q$, draw the line $L$ through them.
* This line will intersect the curve at a third point $R$ (counting multiplicity).
* Reflect $R$ over the x-axis to obtain $P + Q = -R$.

In coordinates, if $P = (x_1, y_1)$, $Q = (x_2, y_2)$, then the point $R = (x_3, y_3) = P + Q$ is computed as follows:

### Case 1: $P \neq Q$

$$
\lambda = \frac{y_2 - y_1}{x_2 - x_1}, \quad
x_3 = \lambda^2 - x_1 - x_2, \quad
y_3 = \lambda(x_1 - x_3) - y_1
$$

### Case 2: $P = Q$ (Point Doubling)

$$
\lambda = \frac{3x_1^2 + a}{2y_1}, \quad
x_3 = \lambda^2 - 2x_1, \quad
y_3 = \lambda(x_1 - x_3) - y_1
$$

### Case 3: $P = -Q$

If the line through $P$ and $Q$ is vertical, then $P + Q = \mathcal{O}$, the identity element.

## The Point at Infinity and Identity Element

The point $\mathcal{O}$ is a special idealized point that lies on every vertical line. It serves as the **neutral element** of the group, meaning:

$$
P + \mathcal{O} = \mathcal{O} + P = P \quad \text{for all } P \in E
$$

Each point $P = (x, y)$ has an inverse $-P = (x, -y)$, reflecting it across the x-axis.

**Proprieties**:
- $P + \mathcal{O} = \mathcal{O} + P + P $
- $ P + (-P) = \mathcal{O}$
- $P + Q = Q + P$
- $(P + Q) + R = P + (Q + R)$

Therefore points on E form an *abelian group*. Refresh the Group theory if you dont remember the definitions.


```python
def elliptic_sum(P1, P2):
    """Let a point P = (x, y); let O = (0, np.inf)"""
    x_1, y_1 = P1
    x_2, y_2 = P2
    if y_1 == np.inf:
        return P2
    elif y_2 == np.inf:
        return P1
    elif x_1 == x_2 and y_1 == -y_2:
        return (0, np.inf)  # this is O
    else:
        lam = (y_2 - y_1) / (x_2 - x_1) if P1 != P2 else (3 * (x_1**2) + a) / (2 * y_1)  # the slope
        x_3 = lam**2 - x_1 - x_2
        y_3 = lam * (x_1 - x_3) - y_1
        return (x_3, y_3)
```

In the `src/ecpy.py` we have some illustrative examples. 

---

## Visualizing Elliptic Curves in Projective Space

To deepen our geometric understanding of elliptic curves, it's helpful to move from the affine plane to *projective space*, which naturally handles the behavior of curves "at infinity" and provides a complete algebraic framework.

### Projective Space: Motivation and Construction

Let us begin with the Euclidean plane $\mathbb{R}^2 = \{(x, y) \mid x, y \in \mathbb{R} \}$, which we now want to "embed" in a higher-dimensional setting. The projective plane $\mathbb{RP}^2$ is defined as:

$$
\mathbb{RP}^2 = \left\{ (x : y : z) \in \mathbb{R}^3 \setminus \{(0 : 0 : 0)\} \right\} \big/ \sim
$$

where $(x : y : z) \sim (\lambda x : \lambda y : \lambda z)$ for any non-zero $\lambda \in \mathbb{R}$.

In other words, each point in projective space represents a line through the origin in $\mathbb{R}^3$. Any two points on the same line are considered equivalent under this relation. This gives us a consistent way to reason about directions and "points at infinity" in the plane.

<div style="text-align:center">
  <img src="/images/ready/elliptic-curves-group-law/projection.PNG" width="500"/><br/>
  <em>All points on the same line through the origin are equivalent in projective space.</em>
</div>

### Affine Plane as a Slice

We can recover the usual affine plane $\mathbb{R}^2$ by choosing the **affine slice** $z = 1$. Every equivalence class has a unique representative of the form $(x : y : 1)$, identifying affine coordinates with projective ones.

On the other hand, the points with $z = 0$ correspond to **points at infinity**. These are not part of the affine plane but are captured naturally by projective geometry.

<div style="text-align:center">
  <img src="/images/ready/elliptic-curves-group-law/affine.PNG" width="250"/><br/>
  <em>The affine plane sits inside projective space as a slice z = 1, and the "line at infinity" lies at  z =0 .</em>
</div>


### Homogenizing the Elliptic Curve Equation

Elliptic curves are commonly given in the affine Weierstrass form:

$$
y^2 = x^3 + ax + b
$$

To move to projective space, we *homogenize* this equation so that all terms are of degree 3:

$$
y^2 z = x^3 + a x z^2 + b z^3
$$

This extended equation defines the curve in $\mathbb{P}^2$. Let's analyze what happens in special cases:

* **Affine plane $z = 1$**: We recover the original affine equation.
* **Points at infinity $z = 0$**: We get $x^3 = 0 \Rightarrow x = 0$, and $y$ can be any value. All such points are equivalent to the projective point $(0 : 1 : 0)$, which we interpret as the **point at infinity** $\mathcal{O}$ on the elliptic curve.

<div style="text-align:center">
  <img src="/images/ready/elliptic-curves-group-law/2Dplane.PNG" width="600"/><br/>
  <em>The affine elliptic curve embedded into projective space, with O = (0 : 1 : 0) as the identity element of the group law.</em>
</div>


* Projective space allows us to compactify the affine plane and include "points at infinity."
* Homogenization of equations ensures a well-defined curve in projective coordinates.
* The point $\mathcal{O} = (0 : 1 : 0)$ plays the role of the **identity element** in the group structure of the elliptic curve.
* These ideas set the stage for a deeper algebraic understanding of elliptic curves, especially when defining operations such as point addition, scalar multiplication, and group laws over finite fields or number fields.

<div style="text-align:center">
  <img src="/images/ready/elliptic-curves-group-law/proplane.PNG" width="250"/><br/>
</div>

A complete, class-based implementation of the elliptic curve group law in Python is available in the file [`src/fullec.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/ready-material/elliptic-curves/src/fullec.py), which includes methods for point addition, doubling, and identity handling over the affine plane.
