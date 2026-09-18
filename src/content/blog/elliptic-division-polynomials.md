---
title: "Elliptic Curve Mathematics X: Division Polynomials and n-Torsion"
description: "Division polynomials, their recurrences and degree growth, torsion-point detection, explicit multiplication-by-n formulas, and their role in Schoof-style point counting."
pubDate: "2025-05-21"
updatedDate: "2026-09-17"

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
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 10
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

Division polynomials turn the multiplication map

$$
[n]:E\longrightarrow E
$$

into explicit algebra.

They encode:

* the coordinates of \([n]P\);
* the locations of \(n\)-torsion points;
* the algebraic structure of division points;
* the symbolic action of Frobenius on torsion.

This makes them an important bridge between several topics already developed in this series.

From Chapter V:

$$
\boxed{
E[n]
=
\ker[n].
}
$$

From Chapter VI:

$$
\boxed{
\text{Schoof studies Frobenius on }E[\ell].
}
$$

Division polynomials connect these statements computationally:

$$
\boxed{
[n]P
}
$$

$$
\Downarrow
$$

$$
\boxed{
\psi_n,\phi_n,\omega_n
}
$$

$$
\Downarrow
$$

$$
\boxed{
E[n]
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{symbolic torsion arithmetic}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Schoof-style point counting}.
}
$$

---

## Table of Contents

- [1. Setup and notation](#1-setup-and-notation)
- [2. Why multiplication-by-(n) should have polynomial structure](#2-why-multiplication-by-n-should-have-polynomial-structure)
- [3. The first division polynomials](#3-the-first-division-polynomials)
- [4. Recursive definition](#4-recursive-definition)
- [5. Odd and even division polynomials](#5-odd-and-even-division-polynomials)
- [6. The torsion criterion](#6-the-torsion-criterion)
- [7. Why the roots encode torsion](#7-why-the-roots-encode-torsion)
- [Degree growth](#degree-growth)
- [9. Counting torsion through polynomial degree](#9-counting-torsion-through-polynomial-degree)
- [10. Multiplication polynomials (\phi_n) and (\omega_n)](#10-multiplication-polynomials-phi_n-and-omega_n)
- [11. Explicit coordinates of (\[n\]P)](#11-explicit-coordinates-of-np)
- [12. Recovering the doubling formula](#12-recovering-the-doubling-formula)
- [13. A (3)-torsion example](#13-a-3-torsion-example)
- [14. Division points versus torsion points](#14-division-points-versus-torsion-points)
- [15. Characteristic-(p) caveat](#15-characteristic-p-caveat)
- [16. Why symbolic expressions become expensive](#16-why-symbolic-expressions-become-expensive)
- [17. Division polynomials inside Schoof’s algorithm](#17-division-polynomials-inside-schoofs-algorithm)
- [18. Frobenius modulo (\psi_\ell)](#18-frobenius-modulo-psi_ell)
- [Implementation strategy](#implementation-strategy)
- [20. Companion Sage implementation](#20-companion-sage-implementation)
- [21. The bigger picture](#21-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="setup"></a>

## 1. Setup and notation

Consider the short Weierstrass curve

$$
\boxed{
E:
y^2=x^3+Ax+B
}
$$

over a field \(K\) satisfying

$$
\operatorname{char}(K)\neq2,3.
$$

We also assume

$$
\Delta
=
-16(4A^3+27B^2)
\neq0.
$$

Thus \(E\) is nonsingular.

The multiplication-by-\(n\) map is

$$
[n]:
E\rightarrow E,
$$

defined by

$$
P\longmapsto[n]P.
$$

For a nonzero integer \(n\), this map has degree

$$
\boxed{
\deg[n]=n^2.
}
$$

When

$$
\operatorname{char}(K)\nmid n,
$$

the map is separable and its geometric kernel has exactly

$$
n^2
$$

points:

$$
\boxed{
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2.
}
$$

Division polynomials provide explicit equations for these points.

---

<a id="why-polynomials"></a>

## 2. Why multiplication-by-\(n\) should have polynomial structure

The elliptic-curve group law is rational.

For example,

$$
x(P+Q)
$$

and

$$
y(P+Q)
$$

are rational functions in the coordinates of \(P\) and \(Q\).

Therefore repeated addition implies that

$$
x([n]P)
$$

and

$$
y([n]P)
$$

must also be rational functions of

$$
x(P)
\quad\text{and}\quad
y(P).
$$

Division polynomials package these rational functions into a structured recursive family.

Instead of repeatedly expanding point-addition formulas, we construct polynomials

$$
\psi_n,
\qquad
\phi_n,
\qquad
\omega_n
$$

such that

$$
[n]P
$$

can be recovered directly.

This is the central idea.

---

<a id="first-polynomials"></a>

## 3. The first division polynomials

The standard sequence begins with

$$
\boxed{
\psi_0=0,
}
$$

$$
\boxed{
\psi_1=1,
}
$$

and

$$
\boxed{
\psi_2=2y.
}
$$

The first nontrivial polynomial purely in \(x\) is

$$
\boxed{
\psi_3
=
3x^4
+
6Ax^2
+
12Bx
-
A^2.
}
$$

The next term is

$$
\boxed{
\psi_4
=
4y
\left(
x^6
+
5Ax^4
+
20Bx^3
-
5A^2x^2
-
4ABx
-
8B^2
-
A^3
\right).
}
$$

Already a pattern appears:

$$
\psi_1,\psi_3,\ldots
$$

depend only on \(x\),

while

$$
\psi_2,\psi_4,\ldots
$$

contain a factor of \(y\).

This pattern persists.

---

<a id="recurrences"></a>

## 4. Recursive definition

The higher division polynomials are generated recursively.

For \(m\geq2\),

$$
\boxed{
\psi_{2m+1}
=
\psi_{m+2}\psi_m^3
-
\psi_{m-1}\psi_{m+1}^3.
}
$$

For \(m\geq2\),

$$
\boxed{
\psi_{2m}
=
\frac{\psi_m}{\psi_2}
\left(
\psi_{m+2}\psi_{m-1}^2
-
\psi_{m-2}\psi_{m+1}^2
\right).
}
$$

Since

$$
\psi_2=2y,
$$

the second recurrence is often written as

$$
\boxed{
\psi_{2m}
=
\frac{\psi_m}{2y}
\left(
\psi_{m+2}\psi_{m-1}^2
-
\psi_{m-2}\psi_{m+1}^2
\right).
}
$$

Although this expression appears to involve division by \(y\), the recurrence produces a valid polynomial function in the coordinate ring of the elliptic curve.

The even-index terms naturally retain one factor of \(2y\).

---

<a id="odd-even"></a>

## 5. Odd and even division polynomials

For odd \(n\),

$$
\boxed{
\psi_n\in K[x].
}
$$

For even \(n\),

$$
\boxed{
\psi_n
=
2y\,f_n(x)
}
$$

for some polynomial

$$
f_n(x)\in K[x].
$$

So division polynomials technically live in the coordinate ring

$$
K[x,y]/
\left(
y^2-x^3-Ax-B
\right),
$$

rather than all lying independently in \(K[x]\).

This distinction matters in implementations.

For odd primes

$$
\ell\neq\operatorname{char}(K),
$$

which are particularly important in Schoof's algorithm,

$$
\psi_\ell
$$

is a polynomial purely in \(x\).

That makes symbolic \(\ell\)-torsion arithmetic especially convenient.

---

<a id="torsion-criterion"></a>

## 6. The torsion criterion

Let

$$
P\neq\mathcal O.
$$

Assume

$$
\operatorname{char}(K)\nmid n.
$$

Then

$$
\boxed{
[n]P=\mathcal O
\iff
\psi_n(P)=0.
}
$$

Thus the nontrivial \(n\)-torsion points are precisely the zeros of the corresponding division polynomial.

Equivalently,

$$
\boxed{
E[n]\setminus\{\mathcal O\}
=
\{
P:
\psi_n(P)=0
\}.
}
$$

For odd \(n\),

$$
\psi_n(x)=0
$$

directly determines the possible \(x\)-coordinates of nonzero \(n\)-torsion points.

---

<a id="why-torsion-roots"></a>

## 7. Why the roots encode torsion

Later we will see that

$$
x([n]P)
=
\frac{\phi_n(P)}
{\psi_n(P)^2}.
$$

Suppose

$$
\psi_n(P)=0.
$$

Then the rational expression for

$$
[n]P
$$

develops a pole.

Geometrically, a pole in the affine \(x\)-coordinate means the resulting point is the point at infinity:

$$
[n]P=\mathcal O.
$$

So the denominator

$$
\psi_n(P)^2
$$

detects exactly when multiplication by \(n\) sends a point to the identity.

This is why the name **division polynomial** is natural.

Its roots describe the points divisible into the kernel of \([n]\).

---

<a id="degree-growth"></a>

## Degree growth

The degrees grow quadratically.

For odd \(n\),

$$
\boxed{
\deg_x\psi_n
=
\frac{n^2-1}{2}.
}
$$

For even \(n\), write

$$
\psi_n=2y\,f_n(x).
$$

Then

$$
\boxed{
\deg_x f_n
=
\frac{n^2-4}{2}.
}
$$

Examples:

$$
\deg\psi_3
=
\frac{9-1}{2}
=
4,
$$

which agrees with

$$
\psi_3
=
3x^4+\cdots.
$$

For \(n=5\),

$$
\deg\psi_5
=
\frac{25-1}{2}
=
12.
$$

For \(n=101\),

$$
\deg\psi_{101}
=
\frac{101^2-1}{2}
=
5100.
$$

So symbolic expressions become large very quickly.

---

<a id="torsion-count"></a>

## 9. Counting torsion through polynomial degree

Suppose \(n\) is odd and

$$
\operatorname{char}(K)\nmid n.
$$

We know

$$
\#E[n]=n^2.
$$

One of these points is

$$
\mathcal O.
$$

So there are

$$
n^2-1
$$

nonzero torsion points.

But points occur in inverse pairs:

$$
P
\quad\text{and}\quad
-P.
$$

They have the same \(x\)-coordinate:

$$
x(P)=x(-P).
$$

Therefore the number of distinct \(x\)-coordinates is

$$
\frac{n^2-1}{2}.
$$

And that is exactly

$$
\boxed{
\deg\psi_n.
}
$$

So the degree formula has a direct geometric explanation:

$$
\boxed{
\text{roots of }\psi_n
\leftrightarrow
\{\pm P\}
\text{ pairs in }E[n].
}
$$

This is an elegant connection between:

* polynomial degree;
* torsion cardinality;
* the symmetry \(P\leftrightarrow-P\).

---

<a id="multiplication-polynomials"></a>

## 10. Multiplication polynomials \(\phi_n\) and \(\omega_n\)

The division polynomial \(\psi_n\) gives the denominator of the multiplication formulas.

Define

$$
\boxed{
\phi_n
=
x\psi_n^2
-
\psi_{n+1}\psi_{n-1}.
}
$$

A second polynomial function is

$$
\boxed{
\omega_n
=
\frac{
\psi_{n+2}\psi_{n-1}^2
-
\psi_{n-2}\psi_{n+1}^2
}{
4y
}.
}
$$

Together,

$$
\psi_n,
\qquad
\phi_n,
\qquad
\omega_n
$$

encode the multiplication-by-\(n\) map.

These are sometimes collectively called the multiplication polynomials.

---

<a id="multiplication-coordinates"></a>

## 11. Explicit coordinates of \([n]P\)

Let

$$
P=(x,y)
$$

with

$$
[n]P\neq\mathcal O.
$$

Then

$$
\boxed{
x([n]P)
=
\frac{\phi_n(P)}
{\psi_n(P)^2},
}
$$

and

$$
\boxed{
y([n]P)
=
\frac{\omega_n(P)}
{\psi_n(P)^3}.
}
$$

Thus

$$
\boxed{
[n](x,y)
=
\left(
\frac{\phi_n}{\psi_n^2},
\frac{\omega_n}{\psi_n^3}
\right).
}
$$

This is an important conceptual result.

Repeated point addition has been compressed into rational functions built from recursively generated polynomials.

---

<a id="doubling-example"></a>

## 12. Recovering the doubling formula

The \(n=2\) case provides an excellent consistency check.

We know

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
3x^4+6Ax^2+12Bx-A^2.
$$

Now

$$
\phi_2
=
x\psi_2^2
-
\psi_3\psi_1.
$$

Therefore,

$$
\phi_2
=
4xy^2
-
\psi_3.
$$

Using

$$
y^2=x^3+Ax+B,
$$

we obtain

$$
4xy^2
=
4x^4+4Ax^2+4Bx.
$$

Subtracting \(\psi_3\),

$$
\phi_2
=
x^4
-
2Ax^2
-
8Bx
+
A^2.
$$

Hence

$$
\boxed{
x(2P)
=
\frac{
x^4-2Ax^2-8Bx+A^2
}{
4y^2
}.
}
$$

Now compare with the ordinary tangent formula

$$
\lambda
=
\frac{3x^2+A}{2y},
$$

$$
x(2P)
=
\lambda^2-2x.
$$

Substitution and simplification produce exactly the same rational expression.

So the division-polynomial machinery is not introducing a different multiplication law.

It is encoding the same elliptic-curve arithmetic algebraically.

---

<a id="three-torsion"></a>

## 13. A \(3\)-torsion example

For \(n=3\),

$$
\boxed{
\psi_3(x)
=
3x^4
+
6Ax^2
+
12Bx
-
A^2.
}
$$

Therefore a nonzero point \(P\) satisfies

$$
[3]P=\mathcal O
$$

exactly when

$$
\boxed{
3x(P)^4
+
6Ax(P)^2
+
12Bx(P)
-
A^2
=
0.
}
$$

Consider

$$
E:
y^2=x^3+1.
$$

Then

$$
A=0,
\qquad
B=1.
$$

So

$$
\psi_3(x)
=
3x^4+12x.
$$

Factor:

$$
\psi_3(x)
=
3x(x^3+4).
$$

Thus

$$
x=0
$$

is one possible \(3\)-torsion \(x\)-coordinate.

Indeed,

$$
(0,1)
$$

lies on the curve, and as we saw in Chapter V,

$$
\boxed{
[3](0,1)=\mathcal O.
}
$$

So the division polynomial recovers the torsion point algebraically.

---

<a id="division-points"></a>

## 14. Division points versus torsion points

Torsion asks:

$$
\boxed{
[n]P=\mathcal O.
}
$$

A more general division problem asks:

$$
\boxed{
[n]Q=P.
}
$$

If one solution

$$
Q_0
$$

exists over an algebraic closure, then every solution is

$$
\boxed{
Q_0+T,
\qquad
T\in E[n].
}
$$

Indeed,

$$
[n](Q_0+T)
=
[n]Q_0+[n]T
=
P+\mathcal O
=
P.
$$

Thus the solutions form a coset

$$
\boxed{
Q_0+E[n].
}
$$

When

$$
\operatorname{char}(K)\nmid n,
$$

there are generically

$$
n^2
$$

geometric division points above \(P\).

So \(n\)-torsion describes the ambiguity in division by \(n\).

---

<a id="characteristic-p"></a>

## 15. Characteristic-\(p\) caveat

The clean picture above assumes

$$
\boxed{
\operatorname{char}(K)\nmid n.
}
$$

If

$$
p=\operatorname{char}(K)
$$

divides \(n\), the multiplication map may become inseparable.

In particular, the familiar statement

$$
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2
$$

no longer holds for geometric points.

For \(p\)-torsion we saw in Chapter V:

### Ordinary curves

$$
\boxed{
E[p](\overline K)
\cong
\mathbb Z/p\mathbb Z
}
$$

as a group of geometric points.

### Supersingular curves

$$
\boxed{
E[p](\overline K)
=
\{\mathcal O\}.
}
$$

The scheme-theoretic kernel of \([p]\) is richer than the set of geometric points.

Division polynomials therefore require extra care when the characteristic divides the index.

For Schoof, this problem is avoided by using primes

$$
\boxed{
\ell\neq p.
}
$$

---

<a id="symbolic-cost"></a>

## 16. Why symbolic expressions become expensive

The recurrence relations are elegant, but naive symbolic expansion is expensive.

The reason is already visible from

$$
\deg\psi_n
=
O(n^2).
$$

As \(n\) grows:

* polynomial degree grows quadratically;
* coefficient expressions grow;
* multiplication becomes expensive;
* intermediate expressions can become much larger than the final result.

A naive implementation that repeatedly expands every polynomial from scratch quickly becomes impractical.

Serious implementations therefore use techniques such as:

* memoization;
* modular polynomial arithmetic;
* fast multiplication;
* quotient-ring reduction;
* subproduct reuse;
* avoiding unnecessary explicit expansion.

This distinction is important:

$$
\boxed{
\text{mathematical recurrence}
\neq
\text{efficient implementation strategy}.
}
$$

The recurrence tells us what the polynomial is.

It does not tell us the best way to compute with it.

---

<a id="schoof-connection"></a>

## 17. Division polynomials inside Schoof's algorithm

Recall from Chapter VI that

$$
\#E(\mathbb F_q)
=
q+1-t,
$$

where \(t\) is the trace of Frobenius.

Schoof computes

$$
t\bmod\ell
$$

for several small primes

$$
\ell\neq p.
$$

The key object is

$$
E[\ell].
$$

Because

$$
\ell\neq p,
$$

we have

$$
\boxed{
E[\ell]
\cong
(\mathbb Z/\ell\mathbb Z)^2.
}
$$

But explicitly constructing every \(\ell\)-torsion point would be inefficient.

Instead, use

$$
\boxed{
\psi_\ell(x).
}
$$

Its roots represent the \(x\)-coordinates of the nonzero \(\ell\)-torsion points.

So Schoof can reason about a **generic \(\ell\)-torsion point symbolically**.

This is the crucial role of division polynomials.

---

<a id="frobenius-mod-psi"></a>

## 18. Frobenius modulo \(\psi_\ell\)

Let

$$
\pi
$$

denote the Frobenius endomorphism.

It satisfies

$$
\boxed{
\pi^2-t\pi+[q]=0.
}
$$

Restrict this identity to

$$
E[\ell].
$$

Since multiplication by integers on \(E[\ell]\) depends only on those integers modulo \(\ell\), determining the correct relation reveals

$$
t\bmod\ell.
$$

Instead of storing every torsion point separately, we work symbolically modulo the division polynomial.

One may use a quotient coordinate algebra such as

$$
\boxed{
\mathbb F_q[x,y]
/
\left(
y^2-x^3-Ax-B,\;
\psi_\ell(x)
\right).
}
$$

Within this algebra,

$$
\psi_\ell(x)=0
$$

is imposed automatically.

So the symbolic point behaves like a generic nontrivial element of

$$
E[\ell].
$$

Then one compares Frobenius expressions corresponding to

$$
\pi^2(P)+[q]P
$$

and

$$
[t]\pi(P)
$$

to determine the residue

$$
t\bmod\ell.
$$

Repeating for enough small primes and applying the Chinese Remainder Theorem reconstructs \(t\).

Thus:

$$
\boxed{
\psi_\ell
}
$$

is the algebraic representation layer that makes torsion usable inside Schoof's point-counting algorithm.

---

<a id="implementation-strategy"></a>

## Implementation strategy

A reference implementation of division polynomials should not simply be judged by whether it prints the correct symbolic expression.

A useful implementation should test several mathematical properties.

### Initial values

Check

$$
\psi_0=0,
\qquad
\psi_1=1,
\qquad
\psi_2=2y.
$$

---

### Known \(\psi_3\)

Verify

$$
\psi_3
=
3x^4+6Ax^2+12Bx-A^2.
$$

---

### Parity structure

Confirm:

$$
n\text{ odd}
\Rightarrow
\psi_n\in K[x],
$$

while

$$
n\text{ even}
\Rightarrow
2y\mid\psi_n.
$$

---

### Degree tests

For odd \(n\),

$$
\deg\psi_n
=
\frac{n^2-1}{2}.
$$

For even \(n\),

$$
\deg\frac{\psi_n}{2y}
=
\frac{n^2-4}{2}.
$$

---

### Torsion checks

For a known torsion point \(P\), verify

$$
\psi_n(P)=0
$$

exactly when

$$
[n]P=\mathcal O.
$$

---

### Multiplication checks

Compare

$$
\frac{\phi_n(P)}{\psi_n(P)^2}
$$

against the \(x\)-coordinate obtained from ordinary scalar multiplication.

Likewise compare

$$
\frac{\omega_n(P)}{\psi_n(P)^3}
$$

with the computed \(y\)-coordinate.

These tests connect the symbolic recurrence directly to the group law.

---

<a id="companion-implementation"></a>

## 20. Companion Sage implementation

The retained CryptoCave material includes a Sage reference implementation that:

* constructs division polynomials recursively;
* evaluates them on elliptic-curve points;
* checks torsion relations;
* cross-checks the polynomial formulas against scalar multiplication.

The implementation belongs under:

[`experiments/mathematics/elliptic-curves/`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/mathematics/elliptic-curves)

The original chapter material does not identify the exact Sage filename, so the directory is linked here rather than inventing a file path.

This implementation should be treated as **reference and educational code**.

It is intended to expose the mathematics:

$$
\boxed{
\text{recurrence}
\rightarrow
\psi_n
\rightarrow
\phi_n,\omega_n
\rightarrow
[n]P.
}
$$

It is not intended to reproduce the optimized polynomial arithmetic of production point-counting libraries.

When reviewing the script, useful questions include:

1. Are previously computed \(\psi_i\) values cached?
2. Are even and odd recurrences handled separately?
3. Does the code reduce using

   $$
   y^2=x^3+Ax+B?
   $$
4. Does it verify the degree formulas?
5. Does it test known torsion points?
6. Does it compare polynomial multiplication formulas with Sage's native scalar multiplication?
7. Does it avoid rebuilding the same large symbolic expressions unnecessarily?
8. Can computations be reduced modulo another polynomial such as

   $$
   \psi_\ell
   $$

   instead of fully expanding everything?

These are exactly the questions that separate a mathematical demonstration from an efficient symbolic implementation.

---

<a id="bigger-picture"></a>

## 21. The bigger picture

Division polynomials connect several chapters of elliptic-curve mathematics.

Start with the multiplication map:

$$
\boxed{
[n]:E\rightarrow E.
}
$$

Its kernel is

$$
\boxed{
E[n].
}
$$

Division polynomials encode this kernel:

$$
\boxed{
[n]P=\mathcal O
\iff
\psi_n(P)=0.
}
$$

The complete multiplication map is encoded by

$$
\boxed{
\psi_n,
\phi_n,
\omega_n.
}
$$

Specifically,

$$
\boxed{
[n](x,y)
=
\left(
\frac{\phi_n}{\psi_n^2},
\frac{\omega_n}{\psi_n^3}
\right).
}
$$

For odd \(n\),

$$
\boxed{
\deg\psi_n
=
\frac{n^2-1}{2},
}
$$

which reflects the fact that

$$
P
\quad\text{and}\quad
-P
$$

share one \(x\)-coordinate.

For a small prime

$$
\ell\neq p,
$$

the same polynomial

$$
\psi_\ell
$$

provides a symbolic description of

$$
E[\ell].
$$

Frobenius acts on this torsion space:

$$
\boxed{
\pi^2-t\pi+[q]=0.
}
$$

Therefore:

$$
\boxed{
\text{division polynomials}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\ell\text{-torsion}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Frobenius action}
}
$$

$$
\Downarrow
$$

$$
\boxed{
t\bmod\ell
}
$$

$$
\Downarrow
$$

$$
\boxed{
t
}
$$

$$
\Downarrow
$$

$$
\boxed{
\#E(\mathbb F_q)=q+1-t.
}
$$

This is why division polynomials should not be viewed as an isolated collection of complicated recurrence formulas.

They are an explicit algebraic representation of the multiplication map.

And that representation is powerful enough to connect:

$$
\boxed{
\text{point arithmetic}
}
$$

to

$$
\boxed{
\text{torsion geometry}
}
$$

to

$$
\boxed{
\text{finite-field point counting}.
}
$$

Few constructions show the unity of elliptic-curve mathematics more clearly.

---

## Further reading

Useful references for this chapter include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* René Schoof, work on polynomial-time point counting over finite fields.
* J. H. Silverman and J. Tate, **Rational Points on Elliptic Curves**.
* Darrel Hankerson, Alfred Menezes, and Scott Vanstone, **Guide to Elliptic Curve Cryptography**.

---

The next chapter can now move naturally from multiplication polynomials to another fundamental structure:

$$
\boxed{
\text{endomorphisms and isogenies}.
}
$$

We have already encountered one endomorphism repeatedly:

$$
\boxed{
\pi
=
\text{Frobenius}.
}
$$

And we have seen kernels such as

$$
E[n].
$$

The next natural questions are:

* What is an elliptic-curve endomorphism?
* What is an isogeny?
* How does a finite subgroup define an isogeny?
* What are separable and inseparable isogenies?
* What is the endomorphism ring?
* Why do ordinary and supersingular curves have different endomorphism structures?
* How do \(j\)-invariants move along isogeny graphs?

That would take the machinery developed so far and open the next major part of elliptic-curve mathematics.
