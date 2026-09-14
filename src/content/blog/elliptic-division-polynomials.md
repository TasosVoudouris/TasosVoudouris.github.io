---
title: "Elliptic Curve Mathematics X: Division Polynomials and n-Torsion"
description: "Division polynomials, recurrences, torsion-point detection, scalar multiplication formulas, and their role in Schoof-style point counting."
pubDate: "2025-05-21"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Elliptic Curve Theory"
- "Finite Fields"
tags:
- "division-polynomials"
- "torsion"
- "schoof"
- "elliptic-curves"
- "polynomial-recurrences"
difficulty: "Advanced"
status: "Reference"
series: "Elliptic Curve Mathematics"
seriesOrder: 10
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---
Division polynomials package the multiplication-by-$n$ map on an elliptic curve into explicit polynomials. They are the algebraic bridge between point arithmetic and torsion coordinates.

Consider
$$
E:y^2=x^3+Ax+B
$$
over a field of characteristic not $2$ or $3$.

## 1. First division polynomials

The standard sequence begins
$$
\psi_0=0,
\qquad
\psi_1=1,
\qquad
\psi_2=2y,
$$
$$
\psi_3=3x^4+6Ax^2+12Bx-A^2,
$$
with higher terms defined recursively.

Odd-index $\psi_n$ are polynomials in $x$; even-index terms contain a factor of $y$.

## 2. Torsion criterion

For $P\ne\mathcal O$ and suitable characteristic assumptions,
$$
[n]P=\mathcal O
\iff
\psi_n(P)=0.
$$

Thus the roots of division polynomials encode the $x$-coordinates of nontrivial $n$-torsion points.

## 3. Multiplication formulas

Define
$$
\phi_n=x\psi_n^2-\psi_{n+1}\psi_{n-1}.
$$
Then the $x$-coordinate of $[n]P$ is
$$
x([n]P)=\frac{\phi_n(P)}{\psi_n(P)^2}
$$
when the denominator is nonzero.

A corresponding polynomial $\omega_n$ gives the $y$-coordinate.

## 4. Degree growth

The degree of $\psi_n$ grows quadratically in $n$. Roughly, for odd $n$,
$$
\deg_x\psi_n=\frac{n^2-1}{2}.
$$
This matters algorithmically: symbolic division-polynomial arithmetic becomes expensive quickly.

## 5. Schoof connection

Schoof's algorithm works modulo $\ell$-division polynomials so that computations are performed on the $\ell$-torsion symbolically. It compares Frobenius actions and recovers the trace modulo many small primes $\ell$.

Division polynomials are therefore not an isolated identity collection; they are the representation layer that makes polynomial-time point counting possible.

## 6. Implementation note

The retained Sage script computes division polynomials by recurrence and cross-checks scalar-multiplication relations. It is reference code rather than a production implementation; serious point-counting libraries use optimized polynomial arithmetic and avoid rebuilding large expressions unnecessarily.
