---
title: "Elliptic Curve Cryptanalysis I: Singular-Curve DLP Reductions"
description: "A technical study of singular cubic curves and the algebraic reductions that can collapse a curve-based discrete logarithm problem when the curve is not genuinely elliptic."
pubDate: "2025-05-27"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Discrete Logarithms"
- "Cryptanalysis"
tags:
- "singular-curves"
- "dlp"
- "invalid-curve"
- "cuspidal-curve"
difficulty: "Advanced"
series: "Elliptic Curve Cryptanalysis"
seriesOrder: 1
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
The *Discrete Logarithm Problem* (DLP) on elliptic curves is widely believed to be hard, forming the security foundation for elliptic curve cryptography. However, this hardness critically depends on the *non-singularity* of the curve. If a curve becomes *singular*, its group structure may degenerate or simplify to a more elementary group, such as the additive group of a finite field, where the DLP is easy to solve.

Our goal is to explore how and why the DLP becomes solvable on *singular curves*, particularly those with a *cusp*. But first, some mathematical background.


<div align="center">

<img src="/images/ready/singular-curve-dlp-reduction/singularcusp.PNG" alt="Singular cubic with a cusp" width="400"/>

<p><em>Figure: A singular cubic with a cusp.</em></p>

</div>

## Singular Cubic Curves

Let us consider a general cubic curve of the form:

$$
C: y^2 = x^3 + ax^2 + bx + c
$$

The discriminant $D$ of this curve is given by:

$$
D = -4a^3c + a^2b^2 + 18abc - 4b^3 - 27c^2
$$

This expression determines whether the curve is singular or not.

> A curve is said to be *singular* if it contains at least one point $S$ where both partial derivatives vanish:
>
>$$
>\frac{\partial f}{\partial x}(S) = \frac{\partial f}{\partial y}(S) = 0
>$$
>

For cubic curves, the discriminant condition $D = 0$ implies that such a point exists.

Note that, a cubic curve can have *at most one singular point*. This follows from Bézout’s theorem: a line intersects a cubic curve in *at most three* points (counting multiplicities), and a second singular point would force an intersection of multiplicity four with some line.


## Singular Curves over Finite Fields

When working modulo a prime $p$, we reduce the curve coefficients $a, b, c \mod p$. The curve becomes *singular over $\mathbb{F}_p$* if:

$$
D \equiv 0 \mod p
$$

We denote by $C(\mathbb{F}_p)$ the set of all $\mathbb{F}_p$-rational points on the curve, and by $C_{\text{ns}}(\mathbb{F}_p)$ the subset of *non-singular points*. The attack applies to this non-singular locus of a singular curve.


## Cuspidal Singularities and Group Structure


Let's look at the following example. Consider the cuspidal curve:

$$
C: y^2 = x^3
$$

This curve has a triple root at $x = 0$, and the unique singular point is $S = (0, 0)$. Since every line through $(0, 0)$ intersects the curve with multiplicity at least two, and lines through two other points cannot pass through $S$, the usual geometric construction of point addition is invalid at the cusp.

Be careful however. Despite the singularity, we can still define a group law on the non-singular points $C_{\text{ns}}(\mathbb{F}_p)$, and it turns out to be isomorphic to the *additive group* $\mathbb{F}_p^+$. This is the crux of the attack: *mapping the elliptic curve DLP to a DLP in $\mathbb{F}_p$, which is trivial*.


## Explicit Isomorphism to $\mathbb{F}_p^+$

We define the map:

$$
\phi: C_{\text{ns}}(\mathbb{F}_p) \to \mathbb{F}_p, \quad (x, y) \mapsto \frac{x}{y}, \quad \mathcal{O} \mapsto 0
$$

This map is an isomorphism of groups. 
We briefly outline the proof of why this is true. 


Let $t = \frac{x}{y}$. Then from the equation $y^2 = x^3$, we substitute $x = \frac{1}{t^2}$, which implies $y = \frac{1}{t^3}$. This gives a rational parametrization:

$$
(x(t), y(t)) = \left( \frac{1}{t^2}, \frac{1}{t^3} \right)
$$

for all $t \neq 0$, and the point at infinity $\mathcal{O}$ corresponds to $t = 0$.

Now consider two points $P_1, P_2 \in C_{\text{ns}}(\mathbb{F}_p)$ with parameters $t_1, t_2$. Using the explicit addition law on the curve:

$$
t_3 = t_1 + t_2
$$

This follows by substituting $x_i = 1/t_i^2$, $y_i = 1/t_i^3$, computing the slope $\lambda$, and simplifying the formulas for $x_3$ and $y_3$.

Hence, addition of points on the curve corresponds to addition in $\mathbb{F}_p$, completing the isomorphism:

$$
(C_{\text{ns}}(\mathbb{F}_p), +) \simeq (\mathbb{F}_p, +)
$$


Now we return to our discrete log problem. Let $Q = kP \in C_{\text{ns}}(\mathbb{F}_p)$. Under the isomorphism $\phi$, we have:

$$
\phi(Q) = \phi(kP) = k \cdot \phi(P)
$$

Since this is now a DLP in $\mathbb{F}_p^+$, solving for $k$ reduces to a simple linear inversion:

$$
k = \frac{\phi(Q)}{\phi(P)} \mod p
$$

provided $\phi(P) \neq 0$, which holds generically.
A full implementantion in SageMath is provided in `src/singularcurve.sage`. 

So one thing that we should remember always is *verifying that the curve discriminant satisfies $D \not\equiv 0 \mod p$*. It is a fundamental requirement during key generation and throughout protocol implementation. Such safeguards are essential to uphold the security guarantees that elliptic curve cryptography is designed to provide.
