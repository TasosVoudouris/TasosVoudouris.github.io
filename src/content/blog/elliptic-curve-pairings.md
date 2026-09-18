---
title: "Elliptic Curve Mathematics XI: Divisors, Weil Pairing, and Tate Pairing"
description: "A mathematical introduction to divisors, Miller functions, bilinear pairings, the Weil and reduced Tate pairings, embedding degree, and their role in pairing-based elliptic-curve cryptography."
pubDate: "2025-05-25"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Mathematical Foundations"
  - "Public-Key Cryptography"

tags:
  - "pairings"
  - "weil-pairing"
  - "tate-pairing"
  - "embedding-degree"
  - "torsion"
  - "miller-algorithm"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 11
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

The previous chapters developed several ingredients that now come together naturally:

* torsion groups \(E[r]\);
* divisors and principal divisors;
* rational functions on elliptic curves;
* Frobenius;
* finite fields and extension fields;
* division polynomials.

We are now ready to study **bilinear pairings**.

Pairings associate two elliptic-curve points with an element of a multiplicative finite-field subgroup:

$$
\boxed{
e:
G_1\times G_2
\longrightarrow
G_T.
}
$$

In the classical elliptic-curve setting,

$$
G_1,\;G_2
$$

are usually groups derived from \(r\)-torsion points, while

$$
G_T
$$

is a subgroup of

$$
\mathbb F_{q^k}^{\times}.
$$

The fundamental examples are:

$$
\boxed{
\text{Weil pairing}
}
$$

and

$$
\boxed{
\text{Tate pairing}.
}
$$

Their mathematical definitions come from divisors and rational functions.

Their efficient computation comes from **Miller's algorithm**.

And the extension degree

$$
k
$$

that places the target roots of unity inside

$$
\mathbb F_{q^k}
$$

is the **embedding degree**.

The complete progression is therefore

$$
\boxed{
\text{torsion}
\rightarrow
\text{divisors}
\rightarrow
\text{Miller functions}
\rightarrow
\text{pairings}
\rightarrow
\text{finite-field target group}.
}
$$

---

## Table of Contents

- [1. Why pairings appear](#1-why-pairings-appear)
- [Torsion refresher](#torsion-refresher)
- [Roots of unity](#roots-of-unity)
- [4. What bilinearity means here](#4-what-bilinearity-means-here)
- [5. Divisors revisited](#5-divisors-revisited)
- [6. Evaluating functions on divisors](#6-evaluating-functions-on-divisors)
- [Miller functions](#miller-functions)
- [8. Line functions and the group law](#8-line-functions-and-the-group-law)
- [9. The Miller recurrence](#9-the-miller-recurrence)
- [10. Miller’s algorithm](#10-millers-algorithm)
- [11. The Weil pairing](#11-the-weil-pairing)
- [12. Properties of the Weil pairing](#12-properties-of-the-weil-pairing)
- [13. A determinant-like interpretation](#13-a-determinant-like-interpretation)
- [14. The Tate pairing](#14-the-tate-pairing)
- [15. The reduced Tate pairing](#15-the-reduced-tate-pairing)
- [16. Why final exponentiation works](#16-why-final-exponentiation-works)
- [17. Weil versus Tate](#17-weil-versus-tate)
- [Embedding degree](#embedding-degree)
- [19. Frobenius and pairing groups](#19-frobenius-and-pairing-groups)
- [20. Pairing-friendly curves](#20-pairing-friendly-curves)
- [Security implications](#security-implications)
- [22. Cryptographic applications](#22-cryptographic-applications)
- [Companion implementation](#companion-implementation)
- [24. The bigger picture](#24-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="why-pairings"></a>

## 1. Why pairings appear

An ordinary elliptic-curve operation stays inside the curve group:

$$
P,Q
\longmapsto
P+Q.
$$

A pairing does something fundamentally different.

It takes elliptic-curve points and produces an element of another group:

$$
\boxed{
e(P,Q)\in G_T.
}
$$

Typically,

$$
G_T
\subseteq
\mathbb F_{q^k}^{\times}.
$$

The remarkable property is that scalar multiplication in the curve groups becomes exponentiation in the target group.

For integers \(a,b\),

$$
\boxed{
e([a]P,[b]Q)
=
e(P,Q)^{ab}.
}
$$

This identity creates an algebraic bridge between:

$$
\boxed{
\text{elliptic-curve additive groups}
}
$$

and

$$
\boxed{
\text{finite-field multiplicative groups}.
}
$$

That bridge is precisely what makes pairings useful — and also what makes their parameter selection security-sensitive.

---

<a id="torsion-refresher"></a>

## Torsion refresher

Let \(E/K\) be an elliptic curve and let

$$
r\geq1.
$$

The geometric \(r\)-torsion subgroup is

$$
\boxed{
E[r]
=
\{
P\in E(\overline K):
[r]P=\mathcal O
\}.
}
$$

Assume

$$
\gcd(r,\operatorname{char}K)=1.
$$

Then

$$
\boxed{
E[r]
\cong
(\mathbb Z/r\mathbb Z)^2.
}
$$

Therefore

$$
\boxed{
\#E[r]=r^2.
}
$$

If \(r\) is prime, \(E[r]\) can be regarded as a two-dimensional vector space over

$$
\mathbb F_r.
$$

Choose a basis

$$
P_1,P_2.
$$

Then every torsion point can be written uniquely as

$$
\boxed{
P=[a]P_1+[b]P_2,
}
$$

where

$$
a,b\in\mathbb Z/r\mathbb Z.
$$

As always, geometric torsion should be distinguished from rational torsion:

$$
\boxed{
E(K)[r]
=
E[r]\cap E(K).
}
$$

Not every \(r\)-torsion point need be defined over the original field.

---

<a id="roots-of-unity"></a>

## Roots of unity

The target of the Weil pairing is the group of \(r\)-th roots of unity:

$$
\boxed{
\mu_r
=
\{
z\in\overline K^\times:
z^r=1
\}.
}
$$

If

$$
\gcd(r,\operatorname{char}K)=1,
$$

then over a field containing all such roots,

$$
\mu_r
$$

is cyclic of order \(r\).

Suppose we work over

$$
\mathbb F_{q^k}.
$$

Its multiplicative group has order

$$
q^k-1.
$$

Therefore

$$
\mu_r
\subseteq
\mathbb F_{q^k}^{\times}
$$

exactly when

$$
\boxed{
r\mid(q^k-1).
}
$$

This observation will lead directly to the embedding degree.

---

<a id="bilinearity"></a>

## 4. What bilinearity means here

In linear algebra, a bilinear map satisfies linearity in each argument.

Elliptic-curve groups use additive notation, while the target group uses multiplicative notation.

So bilinearity becomes

$$
\boxed{
e(P_1+P_2,Q)
=
e(P_1,Q)e(P_2,Q),
}
$$

and

$$
\boxed{
e(P,Q_1+Q_2)
=
e(P,Q_1)e(P,Q_2).
}
$$

Repeated addition immediately gives

$$
\boxed{
e([a]P,[b]Q)
=
e(P,Q)^{ab}.
}
$$

In particular,

$$
e([a]P,Q)
=
e(P,Q)^a
$$

and

$$
e(P,[b]Q)
=
e(P,Q)^b.
$$

This is the defining computational feature of a bilinear pairing.

---

### Non-degeneracy

A useful pairing must not collapse everything to the identity.

Informally,

$$
\boxed{
P\neq\mathcal O
}
$$

should imply that some \(Q\) exists such that

$$
e(P,Q)\neq1.
$$

For a pairing on \(r\)-torsion, non-degeneracy means that no nonzero point pairs trivially with every possible point.

---

<a id="divisors"></a>

## 5. Divisors revisited

We already encountered divisors when proving associativity.

A divisor on \(E\) is a formal finite integer combination of points:

$$
\boxed{
D
=
\sum_P n_P[P].
}
$$

Its degree is

$$
\boxed{
\deg D
=
\sum_Pn_P.
}
$$

A rational function

$$
f\in K(E)^\times
$$

has divisor

$$
\boxed{
\operatorname{div}(f)
=
\sum_P
\operatorname{ord}_P(f)[P].
}
$$

Zeros contribute positive multiplicities.

Poles contribute negative multiplicities.

Every principal divisor has degree zero:

$$
\boxed{
\deg\operatorname{div}(f)=0.
}
$$

Pairings rely heavily on functions whose divisors encode multiples of elliptic-curve points.

---

<a id="function-evaluation"></a>

## 6. Evaluating functions on divisors

Suppose

$$
D
=
\sum_i n_i[P_i]
$$

and the support of \(D\) avoids the zeros and poles of a rational function \(f\).

Define

$$
\boxed{
f(D)
=
\prod_i
f(P_i)^{n_i}.
}
$$

For example, if

$$
D
=
[P]-[Q],
$$

then

$$
\boxed{
f(D)
=
\frac{f(P)}{f(Q)}.
}
$$

This simple-looking construction is fundamental.

Pairings are built by evaluating carefully chosen rational functions on carefully chosen divisors.

---

<a id="miller-functions"></a>

## Miller functions

Fix

$$
P\in E.
$$

For a positive integer \(n\), define a rational function

$$
f_{n,P}
$$

whose divisor satisfies

$$
\boxed{
\operatorname{div}(f_{n,P})
=
n[P]-[nP]-(n-1)[\mathcal O].
}
$$

When

$$
P\in E[r],
$$

we have

$$
[r]P=\mathcal O.
$$

Therefore

$$
\boxed{
\operatorname{div}(f_{r,P})
=
r[P]-r[\mathcal O].
}
$$

This is exactly the kind of function needed to define the Weil and Tate pairings.

The function itself is only determined up to multiplication by a nonzero constant.

Fortunately, the pairing constructions remove this ambiguity.

---

<a id="line-functions"></a>

## 8. Line functions and the group law

Take points

$$
P,Q\in E.
$$

Let

$$
\ell_{P,Q}
$$

be the line through \(P\) and \(Q\), using the tangent when

$$
P=Q.
$$

This line intersects the elliptic curve at

$$
P,
\quad
Q,
\quad
-(P+Q).
$$

Its divisor is therefore

$$
\boxed{
\operatorname{div}(\ell_{P,Q})
=
[P]+[Q]+[-(P+Q)]-3[\mathcal O].
}
$$

Now consider the vertical line

$$
v_{P+Q}
$$

through

$$
P+Q
$$

and

$$
-(P+Q).
$$

Its divisor is

$$
\boxed{
\operatorname{div}(v_{P+Q})
=
[P+Q]+[-(P+Q)]-2[\mathcal O].
}
$$

Define

$$
\boxed{
g_{P,Q}
=
\frac{\ell_{P,Q}}{v_{P+Q}}.
}
$$

Then

$$
\boxed{
\operatorname{div}(g_{P,Q})
=
[P]+[Q]-[P+Q]-[\mathcal O].
}
$$

This function is one of the fundamental building blocks of Miller's algorithm.

Notice how directly it comes from the geometric group law.

---

<a id="miller-recurrence"></a>

## 9. The Miller recurrence

The functions \(f_{n,P}\) satisfy a useful recurrence.

Suppose we know

$$
f_{m,P}
$$

and

$$
f_{n,P}.
$$

Then

$$
\boxed{
f_{m+n,P}
=
f_{m,P}
f_{n,P}
g_{[m]P,[n]P}
}
$$

up to a nonzero multiplicative constant.

Why?

Add the divisors:

$$
\operatorname{div}(f_{m,P})
+
\operatorname{div}(f_{n,P})
+
\operatorname{div}(g_{[m]P,[n]P}).
$$

The intermediate point terms cancel, leaving exactly

$$
(m+n)[P]
-
[(m+n)P]
-
(m+n-1)[\mathcal O].
$$

That is

$$
\operatorname{div}(f_{m+n,P}).
$$

This gives an elliptic-curve analogue of exponentiation recurrences.

---

<a id="miller-algorithm"></a>

## 10. Miller's algorithm

Suppose we want to evaluate

$$
f_{r,P}(Q).
$$

Computing \(f_{r,P}\) directly from its divisor would be inefficient.

Instead, Miller's algorithm uses the binary expansion of \(r\).

This is conceptually analogous to double-and-add scalar multiplication.

Maintain:

$$
T=[m]P
$$

and a field element representing

$$
f_{m,P}(Q).
$$

For a doubling step,

$$
m\longrightarrow2m,
$$

use

$$
\boxed{
f_{2m,P}
=
f_{m,P}^2
g_{T,T}.
}
$$

For an addition step,

$$
m\longrightarrow m+1,
$$

use

$$
\boxed{
f_{m+1,P}
=
f_{m,P}
g_{T,P}.
}
$$

Evaluating these functions at \(Q\) while following the bits of \(r\) yields

$$
f_{r,P}(Q)
$$

without explicitly constructing a huge rational function.

Thus:

$$
\boxed{
\text{Miller loop}
\approx
\text{double-and-add for rational functions}.
}
$$

This analogy is extremely useful.

---

<a id="weil-pairing"></a>

## 11. The Weil pairing

Let

$$
r\geq1
$$

with

$$
\gcd(r,\operatorname{char}K)=1.
$$

The Weil pairing is

$$
\boxed{
e_r:
E[r]\times E[r]
\longrightarrow
\mu_r.
}
$$

Take

$$
P,Q\in E[r].
$$

Choose degree-zero divisors

$$
D_P\sim[P]-[\mathcal O]
$$

and

$$
D_Q\sim[Q]-[\mathcal O]
$$

with disjoint supports.

Choose rational functions

$$
f_P,
\qquad
f_Q
$$

such that

$$
\operatorname{div}(f_P)=rD_P
$$

and

$$
\operatorname{div}(f_Q)=rD_Q.
$$

Then the Weil pairing can be expressed as

$$
\boxed{
e_r(P,Q)
=
\frac{
f_P(D_Q)
}{
f_Q(D_P)
}.
}
$$

The construction is independent of the admissible choices and produces an \(r\)-th root of unity.

This definition shows why divisors are the natural language of pairings.

---

<a id="weil-properties"></a>

## 12. Properties of the Weil pairing

The Weil pairing has several fundamental properties.

### Bilinearity

$$
\boxed{
e_r(P_1+P_2,Q)
=
e_r(P_1,Q)e_r(P_2,Q).
}
$$

Similarly,

$$
\boxed{
e_r(P,Q_1+Q_2)
=
e_r(P,Q_1)e_r(P,Q_2).
}
$$

Therefore,

$$
\boxed{
e_r([a]P,[b]Q)
=
e_r(P,Q)^{ab}.
}
$$

---

### Alternating property

For every

$$
P\in E[r],
$$

$$
\boxed{
e_r(P,P)=1.
}
$$

Consequently,

$$
\boxed{
e_r(P,Q)
=
e_r(Q,P)^{-1}.
}
$$

---

### Non-degeneracy

If

$$
P\neq\mathcal O,
$$

then there exists

$$
Q\in E[r]
$$

such that

$$
\boxed{
e_r(P,Q)\neq1.
}
$$

---

### Values are \(r\)-th roots of unity

$$
\boxed{
e_r(P,Q)^r=1.
}
$$

Thus

$$
e_r(P,Q)\in\mu_r.
$$

---

<a id="determinant-interpretation"></a>

## 13. A determinant-like interpretation

The alternating behavior has a beautiful linear-algebra analogue.

Let

$$
P_1,P_2
$$

be a basis for

$$
E[r].
$$

Suppose

$$
e_r(P_1,P_2)=\zeta,
$$

where

$$
\zeta
$$

is a primitive \(r\)-th root of unity.

Write

$$
P=[a]P_1+[b]P_2
$$

and

$$
Q=[c]P_1+[d]P_2.
$$

By bilinearity and alternation,

$$
\boxed{
e_r(P,Q)
=
\zeta^{ad-bc}.
}
$$

The exponent

$$
ad-bc
$$

is exactly the determinant

$$
\det
\begin{pmatrix}
a&b\\
c&d
\end{pmatrix}.
$$

So the Weil pairing behaves much like a multiplicative determinant pairing.

This provides an excellent intuition for both:

$$
\boxed{
\text{bilinearity}
}
$$

and

$$
\boxed{
\text{alternation}.
}
$$

---

<a id="tate-pairing"></a>

## 14. The Tate pairing

The Tate pairing is closely related to the Weil pairing but is organized differently and is particularly convenient computationally.

Let

$$
K=\mathbb F_{q^k},
$$

and suppose

$$
r\mid(q^k-1)
$$

with

$$
\gcd(r,q)=1.
$$

One form of the Tate pairing is

$$
\boxed{
T_r:
E(K)[r]
\times
E(K)/rE(K)
\longrightarrow
K^\times/(K^\times)^r.
}
$$

Take

$$
P\in E(K)[r].
$$

Choose the Miller function

$$
f_{r,P}
$$

satisfying

$$
\operatorname{div}(f_{r,P})
=
r[P]-r[\mathcal O].
$$

For a divisor

$$
D_Q\sim[Q]-[\mathcal O]
$$

with support disjoint from the zeros and poles of \(f_{r,P}\), define

$$
\boxed{
T_r(P,\overline Q)
=
f_{r,P}(D_Q)
\pmod{(K^\times)^r}.
}
$$

The output is initially not a unique field element.

It is an equivalence class modulo \(r\)-th powers.

That is why the target is

$$
K^\times/(K^\times)^r.
$$

---

<a id="reduced-tate"></a>

## 15. The reduced Tate pairing

Cryptographic implementations normally use the **reduced Tate pairing**.

Since

$$
r\mid(q^k-1),
$$

define

$$
\boxed{
\widetilde T_r(P,Q)
=
f_{r,P}(D_Q)^{
\frac{q^k-1}{r}
}.
}
$$

For common choices of divisors and coordinates this is often written informally as

$$
\boxed{
\widetilde T_r(P,Q)
=
f_{r,P}(Q)^{
\frac{q^k-1}{r}
}.
}
$$

The exponentiation

$$
\boxed{
\frac{q^k-1}{r}
}
$$

is called the **final exponentiation**.

The result lies in

$$
\boxed{
\mu_r.
}
$$

So the reduced pairing has the familiar cryptographic shape

$$
\boxed{
\widetilde T_r:
G_1\times G_2
\longrightarrow
\mu_r.
}
$$

The precise definitions of \(G_1\) and \(G_2\) depend on the pairing construction and curve setting.

---

<a id="final-exponentiation"></a>

## 16. Why final exponentiation works

Before final exponentiation, the Tate pairing is defined only modulo \(r\)-th powers.

Suppose two representatives differ by

$$
z^r.
$$

After exponentiation,

$$
(z^r)^{
(q^k-1)/r
}
=
z^{q^k-1}.
$$

For

$$
z\in\mathbb F_{q^k}^{\times},
$$

we have

$$
z^{q^k-1}=1.
$$

So the ambiguity disappears.

At the same time, the result satisfies

$$
\left(
f_{r,P}(Q)^{
(q^k-1)/r
}
\right)^r
=
f_{r,P}(Q)^{q^k-1}
=
1.
$$

Therefore the result belongs to

$$
\mu_r.
$$

So final exponentiation performs two tasks:

$$
\boxed{
\text{remove the }r\text{-th-power ambiguity}
}
$$

and

$$
\boxed{
\text{project the output into }\mu_r.
}
$$

---

<a id="weil-vs-tate"></a>

## 17. Weil versus Tate

The two pairings share the same basic mathematical ingredients:

* torsion points;
* divisors;
* rational functions;
* Miller evaluation.

But their computational forms differ.

| Property                 | Weil pairing               | Reduced Tate pairing            |
| ------------------------ | -------------------------- | ------------------------------- |
| Typical domain           | \(E[r]\times E[r]\)        | suitable \(G_1\times G_2\)      |
| Target                   | \(\mu_r\)                  | \(\mu_r\) after reduction       |
| Bilinear                 | Yes                        | Yes                             |
| Non-degenerate           | Yes                        | On suitable quotient/subgroups  |
| Alternating              | Yes                        | Not generally                   |
| Miller evaluations       | Traditionally two          | Typically one                   |
| Final exponentiation     | Not the defining step      | Essential                       |
| Common cryptographic use | More theoretical/classical | Often computationally preferred |

The Tate pairing is often computationally attractive because its standard implementation requires one Miller-function evaluation followed by final exponentiation.

---

<a id="embedding-degree"></a>

## Embedding degree

Let

$$
E/\mathbb F_q
$$

contain a subgroup of prime order

$$
r
$$

with

$$
r\nmid q.
$$

The **embedding degree** with respect to \(r\) is

$$
\boxed{
k
=
\min
\{
k\geq1:
r\mid(q^k-1)
\}.
}
$$

Equivalently,

$$
\boxed{
k
=
\operatorname{ord}_r(q),
}
$$

the multiplicative order of \(q\) modulo \(r\).

This means

$$
\boxed{
\mu_r
\subseteq
\mathbb F_{q^k}^{\times}.
}
$$

That is the fundamental reason \(k\) matters for pairings.

The target group of the pairing lives naturally inside

$$
\mathbb F_{q^k}^{\times}.
$$

---

### An important distinction

The embedding degree should **not** be defined simply as

> the smallest extension containing all points of \(E[r]\).

The two statements are related in common pairing settings, but they are conceptually different.

The standard embedding-degree condition is

$$
\boxed{
r\mid(q^k-1).
}
$$

It concerns the \(r\)-th roots of unity and therefore the multiplicative target group.

This is the definition we will use throughout CryptoCave.

---

### Small example

Suppose

$$
q=11
$$

and

$$
r=5.
$$

Compute powers of \(11\) modulo \(5\):

$$
11\equiv1\pmod5.
$$

Thus

$$
k=1.
$$

So

$$
\mu_5
\subseteq
\mathbb F_{11}^{\times}.
$$

Now suppose instead that

$$
q=7,
\qquad
r=5.
$$

Then

$$
7\equiv2\pmod5,
$$

$$
2^2\equiv4\pmod5,
$$

$$
2^3\equiv3\pmod5,
$$

$$
2^4\equiv1\pmod5.
$$

Hence

$$
\boxed{
k=4.
}
$$

The target \(5\)-th roots of unity first appear in

$$
\mathbb F_{7^4}^{\times}.
$$

---

<a id="frobenius-pairing-groups"></a>

## 19. Frobenius and pairing groups

Frobenius again plays a central role.

Let

$$
\pi
$$

denote the \(q\)-power Frobenius.

On \(r\)-torsion,

$$
E[r],
$$

its characteristic equation is

$$
\boxed{
\pi^2-t\pi+[q]=0
\pmod r.
}
$$

If

$$
r\mid\#E(\mathbb F_q),
$$

then

$$
t\equiv q+1\pmod r.
$$

Therefore

$$
X^2-tX+q
$$

factors modulo \(r\) as

$$
\boxed{
(X-1)(X-q).
}
$$

This naturally produces two Frobenius eigenspaces.

One is associated with eigenvalue

$$
1,
$$

corresponding to \(r\)-torsion rational over the base field.

The other is associated with eigenvalue

$$
q.
$$

This decomposition is one of the reasons modern pairing constructions naturally distinguish two source groups

$$
G_1
$$

and

$$
G_2.
$$

So Frobenius, which first appeared in point counting, returns again in pairing theory.

---

<a id="pairing-friendly"></a>

## 20. Pairing-friendly curves

For ordinary elliptic-curve cryptography, a very small embedding degree can be undesirable because it allows discrete logarithms on the curve subgroup to be related to discrete logarithms in a relatively small extension field.

Pairing-based cryptography deliberately chooses curves for which this map is useful.

Such curves are called **pairing-friendly curves**.

The design problem is therefore a balancing act.

We want:

$$
\boxed{
r
\text{ large enough for curve-group security}
}
$$

and

$$
\boxed{
q^k
\text{ large enough for finite-field security},
}
$$

while keeping

$$
k
$$

small enough that arithmetic in

$$
\mathbb F_{q^k}
$$

remains practical.

This is a different parameter-selection problem from ordinary ECDH or ECDSA curves.

---

<a id="security-implications"></a>

## Security implications

Pairings create a bridge

$$
\boxed{
E[r]
\longrightarrow
\mu_r
\subseteq
\mathbb F_{q^k}^{\times}.
}
$$

Because of bilinearity,

$$
e([a]P,Q)
=
e(P,Q)^a.
$$

Therefore an elliptic-curve discrete logarithm can, under suitable conditions, be transported into a finite-field discrete-logarithm problem.

This observation underlies the classical **MOV** and related pairing-based reductions.

Thus embedding degree has opposite interpretations depending on the application.

### Ordinary ECC

A very small \(k\) may be dangerous.

### Pairing-based cryptography

A deliberately controlled \(k\) is required so that the pairing is efficiently computable while the target-field DLP remains secure.

So a property that can weaken one elliptic-curve system becomes an intentional feature in another.

---

<a id="applications"></a>

## 22. Cryptographic applications

Bilinear pairings enabled several cryptographic constructions that are difficult to obtain using ordinary elliptic-curve operations alone.

Historically and practically important examples include:

* identity-based encryption;
* short signatures;
* aggregate signatures;
* tripartite key-agreement constructions;
* pairing-based zero-knowledge systems;
* polynomial-commitment constructions.

The crucial algebraic resource is

$$
\boxed{
e([a]P,[b]Q)
=
e(P,Q)^{ab}.
}
$$

This allows multiplicative relationships between hidden scalars to be checked through public group elements.

But the applications are only the final layer.

The mathematical foundation remains:

$$
\boxed{
\text{divisors}
+
\text{torsion}
+
\text{rational functions}.
}
$$

---

<a id="companion-implementation"></a>

## Companion implementation

The CryptoCave source material contains a Sage implementation of elliptic-curve pairings:

[`src/pairings.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/pairings.sage)

Repository path:

```text
experiments/ready-material/elliptic-curves/src/pairings.sage
```

This implementation should be read together with the mathematical construction in this chapter.

A useful review sequence is:

$$
\boxed{
\text{divisors}
}
$$

$$
\Downarrow
$$

$$
\boxed{
g_{P,Q}
}
$$

$$
\Downarrow
$$

$$
\boxed{
f_{r,P}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Miller loop}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Weil / Tate evaluation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{final exponentiation}.
}
$$

When studying the code, useful questions include:

1. How are the line functions

   $$
   \ell_{P,Q}
   $$

   represented?

2. Where is the vertical-line denominator

   $$
   v_{P+Q}
   $$

   handled?

3. Does the implementation explicitly construct

   $$
   g_{P,Q}
   =
   \ell_{P,Q}/v_{P+Q}?
   $$

4. How does the Miller loop follow the bits of \(r\)?

5. Is the pairing implemented over

   $$
   \mathbb F_q
   $$

   or an extension

   $$
   \mathbb F_{q^k}?
   $$

6. How is the embedding degree determined?

7. Does the Tate implementation apply

   $$
   \boxed{
   (q^k-1)/r
   }
   $$

   as final exponentiation?

8. Does the implementation verify bilinearity numerically?

For example, a useful test is

$$
e([a]P,[b]Q)
\stackrel{?}{=}
e(P,Q)^{ab}.
$$

9. For the Weil pairing, does it verify

   $$
   e(P,P)=1?
   $$

10. Does the code clearly distinguish educational formulas from optimized production pairing arithmetic?

As with the other CryptoCave implementations, the goal is to make the mathematical construction executable and inspectable.

---

<a id="bigger-picture"></a>

## 24. The bigger picture

This chapter closes a long chain of ideas developed throughout the elliptic-curve series.

We began with a smooth projective cubic:

$$
\boxed{
E.
}
$$

The group law gave

$$
\boxed{
P+Q.
}
$$

Torsion gave

$$
\boxed{
E[r].
}
$$

Divisor theory gave a language for points, zeros, and poles:

$$
\boxed{
D=\sum n_P[P].
}
$$

Line functions gave

$$
\boxed{
\operatorname{div}(g_{P,Q})
=
[P]+[Q]-[P+Q]-[\mathcal O].
}
$$

From those functions we built Miller functions:

$$
\boxed{
\operatorname{div}(f_{r,P})
=
r[P]-r[\mathcal O].
}
$$

Miller's algorithm evaluates those functions efficiently.

The Weil pairing then gives

$$
\boxed{
e_r:
E[r]\times E[r]
\rightarrow
\mu_r.
}
$$

The reduced Tate pairing gives another computationally useful route:

$$
\boxed{
\widetilde T_r(P,Q)
=
f_{r,P}(Q)^{
(q^k-1)/r
}.
}
$$

The embedding degree determines the extension field containing the target roots of unity:

$$
\boxed{
k
=
\operatorname{ord}_r(q).
}
$$

So the complete progression is

$$
\boxed{
\text{elliptic-curve geometry}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{torsion}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{divisors}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{rational functions}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Miller algorithm}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{bilinear pairing}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\mathbb F_{q^k}^{\times}.
}
$$

This is one of the most striking constructions in elliptic-curve mathematics.

A geometric intersection law on a cubic curve eventually produces a bilinear map into a multiplicative finite-field group.

And every stage of that progression matters:

$$
\boxed{
\text{geometry}
\rightarrow
\text{algebra}
\rightarrow
\text{arithmetic}
\rightarrow
\text{algorithm}
\rightarrow
\text{cryptography}.
}
$$

---

## Further reading

Useful references for this chapter include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Alfred Menezes, Tatsuaki Okamoto, and Scott Vanstone, work on the MOV reduction.
* Victor Miller, foundational work on pairing computation and Miller's algorithm.
* Steven Galbraith, **Mathematics of Public Key Cryptography**.
* Ben Lynn, notes on elliptic-curve pairings.
* Dan Boneh and Matthew Franklin, work on identity-based encryption from the Weil pairing.
* Dan Boneh, Ben Lynn, and Hovav Shacham, work on short signatures.

---

The next natural chapter is now **isogenies and endomorphism rings**.

We have already met several endomorphisms:

$$
[n],
$$

and

$$
\pi
=
\text{Frobenius}.
$$

We have also repeatedly studied their kernels.

The next step is therefore to understand:

* what an isogeny actually is;
* how kernels determine separable isogenies;
* Vélu's formulas;
* dual isogenies;
* degrees;
* endomorphism rings;
* ordinary versus supersingular endomorphism structure;
* isogeny graphs;
* how \(j\)-invariants move through those graphs.

That would naturally open the next major mathematical part of the elliptic-curve series.
