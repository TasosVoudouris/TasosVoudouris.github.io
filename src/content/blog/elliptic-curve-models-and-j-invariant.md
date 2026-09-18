---
title: "Elliptic Curve Mathematics VII: Models, Isomorphisms, and the j-Invariant"
description: "How different equations can represent the same elliptic curve: changes of variables, isomorphisms over base fields and algebraic closures, twists, the j-invariant, and Montgomery models for efficient arithmetic."
pubDate: "2025-05-25"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Mathematical Foundations"
  - "Algebraic Geometry"

tags:
  - "elliptic-curves"
  - "j-invariant"
  - "isomorphisms"
  - "quadratic-twists"
  - "montgomery-curves"
  - "curve-models"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 7
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

An elliptic curve is an abstract algebraic curve.

A Weierstrass equation is only one way of **representing** it.

This distinction becomes increasingly important as we move toward cryptography.

Two equations that look completely different may describe isomorphic elliptic curves.

Conversely, two curves may have the same \(j\)-invariant and therefore become isomorphic over an algebraic closure while remaining non-isomorphic over the original base field.

And sometimes we deliberately replace the usual Weierstrass equation by another model — such as a **Montgomery curve** — because that model exposes arithmetic better suited to implementation.

The central hierarchy is therefore

$$
\boxed{
\text{equation}
\neq
\text{curve model}
\neq
\text{isomorphism class}.
}
$$

The invariant that organizes elliptic curves over an algebraic closure is

$$
\boxed{
j(E).
}
$$

---

## Table of Contents

- [1. One elliptic curve, many equations](#1-one-elliptic-curve-many-equations)
- [2. Changes of variables in Weierstrass form](#2-changes-of-variables-in-weierstrass-form)
- [3. Isomorphisms over a field](#3-isomorphisms-over-a-field)
- [4. Isomorphism over (K) versus over (\overline K)](#4-isomorphism-over-k-versus-over-overline-k)
- [5. The (j)-invariant](#5-the-j-invariant)
- [6. Why (j) is invariant](#6-why-j-is-invariant)
- [7. What the (j)-invariant classifies](#7-what-the-j-invariant-classifies)
- [8. Special values (j=0) and (j=1728)](#8-special-values-j0-and-j1728)
- [9. Constructing a curve from a prescribed (j)](#9-constructing-a-curve-from-a-prescribed-j)
- [10. Twists: same (j), different curve over (K)](#10-twists-same-j-different-curve-over-k)
- [11. (j)-invariants over finite fields](#11-j-invariants-over-finite-fields)
- [12. Why different curve models exist](#12-why-different-curve-models-exist)
- [13. Montgomery curves](#13-montgomery-curves)
- [14. Montgomery group law](#14-montgomery-group-law)
- [15. Montgomery (x)-coordinate arithmetic](#15-montgomery-x-coordinate-arithmetic)
- [16. Differential addition and the Montgomery ladder](#16-differential-addition-and-the-montgomery-ladder)
- [17. Curve25519 as a concrete example](#17-curve25519-as-a-concrete-example)
- [18. Montgomery (j)-invariant](#18-montgomery-j-invariant)
- [19. Montgomery to short Weierstrass form](#19-montgomery-to-short-weierstrass-form)
- [20. When can a Weierstrass curve have Montgomery form?](#20-when-can-a-weierstrass-curve-have-montgomery-form)
- [21. Isomorphism is not the same as isogeny](#21-isomorphism-is-not-the-same-as-isogeny)
- [22. Choosing a model in cryptography](#22-choosing-a-model-in-cryptography)
- [23. Companion implementation](#23-companion-implementation)
- [24. The bigger picture](#24-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="many-equations"></a>

## 1. One elliptic curve, many equations

Until now we have usually written an elliptic curve as

$$
E:
y^2=x^3+ax+b.
$$

It is easy to begin thinking that the pair

$$
(a,b)
$$

*is* the elliptic curve.

It is not.

The equation is a **model** of the underlying curve.

Changing coordinates may produce another equation describing the same algebraic object.

The analogy with linear algebra is useful:

> A vector space does not change because we replace one basis by another.

Likewise, an elliptic curve does not fundamentally change merely because its coordinates are replaced.

Thus we distinguish

$$
\boxed{
\text{elliptic curve}
}
$$

from

$$
\boxed{
\text{chosen equation representing the curve}.
}
$$

---

<a id="changes-of-variables"></a>

## 2. Changes of variables in Weierstrass form

The general Weierstrass equation is

$$
y^2+a_1xy+a_3y
=
x^3+a_2x^2+a_4x+a_6.
$$

A change of Weierstrass coordinates has the form

$$
x=u^2x'+r,
$$

$$
y=u^3y'+su^2x'+t,
$$

with

$$
u\neq0.
$$

Such a transformation preserves the distinguished point at infinity and sends a Weierstrass equation to another Weierstrass equation.

When

$$
\operatorname{char}(K)\neq2,3,
$$

we may work in short Weierstrass form

$$
E:
y^2=x^3+ax+b.
$$

Consider the simpler scaling

$$
x=u^2x',
\qquad
y=u^3y'.
$$

Substitution gives

$$
u^6y'^2
=
u^6x'^3
+
au^2x'
+
b.
$$

Dividing by \(u^6\),

$$
y'^2
=
x'^3
+
\frac{a}{u^4}x'
+
\frac{b}{u^6}.
$$

Thus

$$
E:
y^2=x^3+ax+b
$$

is isomorphic to

$$
E':
y^2=x^3+a'x+b'
$$

with

$$
\boxed{
a'=\frac{a}{u^4},
\qquad
b'=\frac{b}{u^6}.
}
$$

Depending on the direction in which the substitution is written, one also frequently sees

$$
a'=u^4a,
\qquad
b'=u^6b.
$$

These statements express the same scaling relation.

---

<a id="isomorphisms-over-field"></a>

## 3. Isomorphisms over a field

Let

$$
E_1/K
$$

and

$$
E_2/K
$$

be elliptic curves.

An isomorphism over \(K\),

$$
\phi:E_1\longrightarrow E_2,
$$

is an algebraic map defined over \(K\), possessing an algebraic inverse defined over \(K\), and satisfying

$$
\phi(\mathcal O_{E_1})
=
\mathcal O_{E_2}.
$$

Because elliptic curves are algebraic groups, an isomorphism preserving the identity also preserves addition:

$$
\boxed{
\phi(P+Q)
=
\phi(P)+\phi(Q).
}
$$

Therefore isomorphic models describe the same group structure.

But one must always specify **over which field** the isomorphism exists.

---

<a id="base-vs-closure"></a>

## 4. Isomorphism over \(K\) versus over \(\overline K\)

Suppose two elliptic curves are defined over \(K\).

They may fail to be isomorphic over \(K\), yet become isomorphic after extending the field to its algebraic closure

$$
\overline K.
$$

Thus we distinguish

$$
\boxed{
E_1\cong_K E_2
}
$$

from

$$
\boxed{
E_1\cong_{\overline K}E_2.
}
$$

The second relation is weaker.

For example, an isomorphism might require an element such as

$$
\sqrt d
$$

that does not belong to \(K\).

Once we extend \(K\) so that \(\sqrt d\) exists, the transformation becomes available.

This phenomenon is the basis of the theory of **twists**.

---

<a id="j-invariant"></a>

## 5. The \(j\)-invariant

For a short Weierstrass curve

$$
E:
y^2=x^3+ax+b
$$

with

$$
4a^3+27b^2\neq0,
$$

the \(j\)-invariant is

$$
\boxed{
j(E)
=
1728
\frac{4a^3}
{4a^3+27b^2}.
}
$$

Using the discriminant

$$
\Delta=-16(4a^3+27b^2),
$$

this may equivalently be related to the classical Weierstrass invariants.

The crucial property is that \(j(E)\) is unchanged by elliptic-curve isomorphism.

---

### Example

Consider

$$
E:
y^2=x^3+x-1.
$$

Then

$$
a=1,
\qquad
b=-1.
$$

Hence

$$
4a^3=4
$$

and

$$
27b^2=27.
$$

Therefore

$$
j(E)
=
1728\frac4{31}
=
\boxed{
\frac{6912}{31}.
}
$$

The original Sage material computes exactly this value.

A minimal SageMath experiment is:

```python
E = EllipticCurve([1, -1])

print(E)
print(E.j_invariant())
```

---

<a id="why-j-invariant"></a>

## 6. Why \(j\) is invariant

Under

$$
x=u^2x',
\qquad
y=u^3y',
$$

we found

$$
a'=\frac{a}{u^4},
\qquad
b'=\frac{b}{u^6}.
$$

Therefore

$$
4a'^3
=
\frac{4a^3}{u^{12}},
$$

and

$$
27b'^2
=
\frac{27b^2}{u^{12}}.
$$

Thus

$$
\frac{4a'^3}
{4a'^3+27b'^2}
=
\frac{4a^3/u^{12}}
{(4a^3+27b^2)/u^{12}}.
$$

The common factor cancels:

$$
=
\frac{4a^3}
{4a^3+27b^2}.
$$

Hence

$$
\boxed{
j(E')=j(E).
}
$$

So \(j\) survives the coordinate change.

This is exactly what an invariant should do.

---

<a id="j-classification"></a>

## 7. What the \(j\)-invariant classifies

The fundamental theorem is:

$$
\boxed{
E_1
\cong_{\overline K}
E_2
\iff
j(E_1)=j(E_2).
}
$$

Thus, over an algebraic closure, the \(j\)-invariant completely determines the isomorphism class of an elliptic curve.

Very roughly,

$$
\boxed{
j
\longleftrightarrow
\text{geometric elliptic-curve isomorphism class}.
}
$$

This is why \(j\) appears naturally in the **moduli theory** of elliptic curves.

But one must keep the word *geometric* in mind.

Two curves with the same \(j\)-invariant may still fail to be isomorphic over the original field \(K\).

---

<a id="special-j"></a>

## 8. Special values \(j=0\) and \(j=1728\)

Two \(j\)-values occur as exceptional cases throughout elliptic-curve theory.

### \(j=0\)

If

$$
a=0,
$$

then

$$
E:
y^2=x^3+b,
\qquad
b\neq0,
$$

has

$$
\boxed{
j=0.
}
$$

For example,

$$
y^2=x^3+1.
$$

---

### \(j=1728\)

If

$$
b=0,
$$

then

$$
E:
y^2=x^3+ax,
\qquad
a\neq0,
$$

has

$$
\boxed{
j=1728.
}
$$

For example,

$$
y^2=x^3-x.
$$

---

### Why are these values special?

Generic elliptic curves have only the obvious automorphisms

$$
\pm1
$$

over an algebraic closure.

Curves with

$$
j=0
$$

or

$$
j=1728
$$

have additional automorphisms.

They therefore possess extra symmetry.

This is why these values repeatedly require special handling.

---

<a id="curve-from-j"></a>

## 9. Constructing a curve from a prescribed \(j\)

For

$$
j\neq0,1728,
$$

one possible model with the desired \(j\)-invariant is

$$
\boxed{
E_j:
y^2
=
x^3
-
3j(j-1728)x
-
2j(j-1728)^2.
}
$$

Substitution into the \(j\)-formula recovers the prescribed value.

This shows that \(j\) is not merely something computed *from* a curve.

It can also be used to select a representative of a geometric isomorphism class.

In SageMath, the original source used:

```python
EllipticCurve_from_j(6912 / 31)
```

The special cases

$$
j=0
$$

and

$$
j=1728
$$

must be handled separately because the formula above degenerates.

---

<a id="twists"></a>

## 10. Twists: same \(j\), different curve over \(K\)

Consider

$$
E:
y^2=x^3+ax+b.
$$

For a nonzero

$$
d\in K,
$$

a quadratic twist can be written as

$$
\boxed{
E^{(d)}:
y^2=x^3+d^2ax+d^3b.
}
$$

Its \(j\)-invariant is unchanged:

$$
\boxed{
j(E^{(d)})
=
j(E).
}
$$

Over a field containing

$$
\sqrt d,
$$

the two curves become isomorphic.

But if \(d\) is not a square in \(K\), they need not be isomorphic over \(K\).

So

$$
\boxed{
\text{same }j
\not\Rightarrow
K\text{-isomorphic}.
}
$$

The precise statement is

$$
\boxed{
\text{same }j
\Rightarrow
\overline K\text{-isomorphic}.
}
$$

---

<a id="j-finite-fields"></a>

## 11. \(j\)-invariants over finite fields

Exactly the same distinction appears over

$$
\mathbb F_q.
$$

Curves with the same \(j\)-invariant become isomorphic over

$$
\overline{\mathbb F}_q,
$$

but need not be isomorphic over

$$
\mathbb F_q.
$$

Quadratic twists provide the standard example.

For odd \(q\), if \(E'\) is the nontrivial quadratic twist of \(E\), then

$$
\boxed{
\#E(\mathbb F_q)
+
\#E'(\mathbb F_q)
=
2(q+1).
}
$$

If

$$
\#E(\mathbb F_q)
=
q+1-t,
$$

then

$$
\boxed{
\#E'(\mathbb F_q)
=
q+1+t.
}
$$

Thus the Frobenius trace changes sign:

$$
\boxed{
t\longmapsto -t.
}
$$

This connects the current chapter directly with the Frobenius theory from Chapter VI.

---

<a id="why-models"></a>

## 12. Why different curve models exist

If Weierstrass equations already describe elliptic curves generally, why introduce alternative models?

Because algebraically equivalent descriptions can behave very differently computationally.

Different models can offer:

* faster addition formulas;
* faster doubling;
* fewer exceptional cases;
* unified formulas;
* \(x\)-coordinate-only arithmetic;
* convenient projective coordinates;
* more regular constant-time algorithms.

Important models include:

* short Weierstrass;
* Montgomery;
* Edwards;
* twisted Edwards;
* Hessian models.

So a cryptographic implementation does not choose a model merely for aesthetics.

The model determines which arithmetic structure is easiest to exploit safely and efficiently.

---

<a id="montgomery-curves"></a>

## 13. Montgomery curves

A **Montgomery curve** over a field \(K\) has equation

$$
\boxed{
M_{A,B}:
By^2=x^3+Ax^2+x
}
$$

with

$$
\boxed{
B(A^2-4)\neq0.
}
$$

This condition guarantees nonsingularity.

The projective equation is

$$
\boxed{
BY^2Z
=
X^3+AX^2Z+XZ^2.
}
$$

Its point at infinity is

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

---

### A built-in point of order \(2\)

Set

$$
x=0.
$$

Then

$$
By^2=0.
$$

Since \(B\neq0\),

$$
y=0.
$$

Therefore

$$
(0,0)\in M_{A,B}.
$$

But

$$
-(0,0)=(0,0).
$$

Hence

$$
\boxed{
[2](0,0)=\mathcal O.
}
$$

Every Montgomery curve therefore contains a rational point of order \(2\).

This already places a restriction on which elliptic curves can admit Montgomery form over a particular base field.

---

<a id="montgomery-group-law"></a>

## 14. Montgomery group law

Let

$$
P=(x_P,y_P),
\qquad
Q=(x_Q,y_Q)
$$

lie on

$$
By^2=x^3+Ax^2+x.
$$

For

$$
P\neq Q,
\qquad
P\neq -Q,
$$

the slope is

$$
\lambda
=
\frac{y_Q-y_P}
{x_Q-x_P}.
$$

Then

$$
\boxed{
x_{P+Q}
=
B\lambda^2-A-x_P-x_Q
}
$$

and

$$
\boxed{
y_{P+Q}
=
\lambda(x_P-x_{P+Q})-y_P.
}
$$

For doubling,

$$
\boxed{
\lambda
=
\frac{
3x_P^2+2Ax_P+1
}{
2By_P
}.
}
$$

The formulas arise from exactly the same chord-and-tangent geometry as ordinary Weierstrass addition.

The model has changed.

The underlying group law has not.

---

<a id="x-coordinate-arithmetic"></a>

## 15. Montgomery \(x\)-coordinate arithmetic

The real computational advantage of Montgomery form is its support for efficient arithmetic without explicitly maintaining \(y\)-coordinates.

Suppose we know

$$
x(P),
\qquad
x(Q),
\qquad
x(P-Q).
$$

Then we can compute

$$
\boxed{
x(P+Q).
}
$$

This is called **differential addition**:

$$
\boxed{
\operatorname{xADD}.
}
$$

Likewise,

$$
x(P)
$$

is sufficient to compute

$$
x([2]P).
$$

This is

$$
\boxed{
\operatorname{xDBL}.
}
$$

Thus:

$$
\boxed{
x(P),x(Q),x(P-Q)
\rightarrow
x(P+Q)
}
$$

and

$$
\boxed{
x(P)
\rightarrow
x(2P).
}
$$

Why is this possible?

Because

$$
P
$$

and

$$
-P
$$

have the same \(x\)-coordinate.

So \(x\)-only arithmetic naturally operates on the quotient

$$
E/\{\pm1\}.
$$

This quotient is commonly called the **Kummer line** of the elliptic curve.

---

<a id="montgomery-ladder"></a>

## 16. Differential addition and the Montgomery ladder

Differential addition becomes especially useful for scalar multiplication.

The Montgomery ladder maintains two related multiples of the same point.

Conceptually,

$$
R_0=[k]P,
$$

$$
R_1=[k+1]P.
$$

Their difference is always

$$
R_1-R_0=P.
$$

Since \(x(P)\) is known, the ladder always has the differential information required by \(\operatorname{xADD}\).

A ladder step performs combinations of

$$
\operatorname{xDBL}
$$

and

$$
\operatorname{xADD}.
$$

Conceptually:

$$
(R_0,R_1)
\rightarrow
(2R_0,R_0+R_1)
$$

or the complementary update depending on the scalar bit.

This regular structure is valuable for constant-time implementations.

The objective is not that the model somehow eliminates side channels automatically.

Rather, Montgomery arithmetic makes a regular implementation strategy particularly natural.

---

<a id="curve25519"></a>

## 17. Curve25519 as a concrete example

One of the most important Montgomery curves in modern cryptography is **Curve25519**.

Its field is

$$
\mathbb F_p
$$

with

$$
\boxed{
p=2^{255}-19.
}
$$

The Montgomery equation is

$$
\boxed{
y^2=x^3+486662x^2+x.
}
$$

Thus

$$
A=486662,
\qquad
B=1.
$$

A standard base \(u\)-coordinate is

$$
\boxed{
u=9.
}
$$

The X25519 function performs scalar multiplication using the Montgomery coordinate and ladder-style arithmetic.

The protocol does not generally need to expose a complete affine pair

$$
(x,y).
$$

This is a useful real-world lesson:

$$
\boxed{
\text{cryptographic interface}
\neq
\text{full mathematical point representation}.
}
$$

The underlying object remains an elliptic curve.

The exposed computational representation is deliberately narrower.

---

<a id="montgomery-j"></a>

## 18. Montgomery \(j\)-invariant

For

$$
M_{A,B}:
By^2=x^3+Ax^2+x,
$$

the \(j\)-invariant is

$$
\boxed{
j(M_{A,B})
=
256
\frac{(A^2-3)^3}
{A^2-4}.
}
$$

Notice that \(B\) does not appear.

Over an algebraic closure, \(B\) can be absorbed by rescaling \(y\).

Therefore the geometric isomorphism class depends on \(A\), while \(B\) may affect whether a particular isomorphism is defined over the base field.

Once again:

$$
\boxed{
K\text{-isomorphism}
\neq
\overline K\text{-isomorphism}.
}
$$

---

<a id="montgomery-to-weierstrass"></a>

## 19. Montgomery to short Weierstrass form

Assume

$$
\operatorname{char}(K)\neq2,3.
$$

Start with

$$
By^2=x^3+Ax^2+x.
$$

Define

$$
\boxed{
t
=
\frac{x}{B}
+
\frac{A}{3B},
}
$$

and

$$
\boxed{
v=\frac{y}{B}.
}
$$

Then the curve becomes

$$
v^2=t^3+at+b
$$

with

$$
\boxed{
a=
\frac{3-A^2}
{3B^2},
}
$$

and

$$
\boxed{
b=
\frac{2A^3-9A}
{27B^3}.
}
$$

Thus every nonsingular Montgomery curve can be expressed in short Weierstrass form when these divisions are valid.

This is another concrete example of two very different-looking equations representing the same elliptic curve.

---

<a id="weierstrass-to-montgomery"></a>

## 20. When can a Weierstrass curve have Montgomery form?

The reverse direction is more restrictive.

Let

$$
E:
y^2=x^3+ax+b
$$

over a field \(K\) of characteristic different from \(2\) and \(3\).

For \(E\) to admit a Montgomery model over \(K\), we need a root

$$
\boxed{
\alpha\in K
}
$$

of

$$
x^3+ax+b.
$$

Then

$$
(\alpha,0)
$$

is a \(K\)-rational point of order \(2\).

We additionally require

$$
\boxed{
3\alpha^2+a
}
$$

to be a square in \(K\).

Suppose

$$
s^2
=
3\alpha^2+a.
$$

Then an appropriate translation and scaling can send

$$
(\alpha,0)
$$

to the distinguished Montgomery \(2\)-torsion point

$$
(0,0)
$$

while normalizing the coefficient of the linear term.

Thus a useful criterion is:

$$
\boxed{
\begin{aligned}
&x^3+ax+b
\text{ has a root }\alpha\in K,
\\
&3\alpha^2+a
\text{ is a square in }K.
\end{aligned}
}
$$

A \(K\)-rational point of order \(4\) provides an important sufficient condition, but rational \(4\)-torsion should not be stated as the general necessary-and-sufficient criterion.

---

<a id="isomorphism-vs-isogeny"></a>

## 21. Isomorphism is not the same as isogeny

An **isomorphism**

$$
\phi:E_1\rightarrow E_2
$$

has an algebraic inverse.

It preserves the entire curve structure.

Conceptually, it is a change of coordinates.

An **isogeny**

$$
\phi:E_1\rightarrow E_2
$$

is a nonconstant morphism satisfying

$$
\phi(\mathcal O)=\mathcal O,
$$

but it need not possess an inverse morphism.

Its kernel can contain several points.

An isomorphism is precisely a degree-\(1\) isogeny.

Thus

$$
\boxed{
\text{isomorphism}
\Rightarrow
\text{isogeny},
}
$$

but not conversely.

Two isomorphic elliptic curves have the same \(j\)-invariant.

Two merely isogenous curves may have different \(j\)-invariants.

This distinction becomes central when we later study isogenies and endomorphism rings.

---

<a id="choosing-model"></a>

## 22. Choosing a model in cryptography

Different models expose different arithmetic.

### Short Weierstrass

Useful because it is:

* general;
* familiar;
* mathematically standard;
* widely deployed.

---

### Montgomery

Useful for:

* differential addition;
* \(x\)-coordinate arithmetic;
* Montgomery ladder scalar multiplication;
* regular implementation structure.

---

### Edwards and twisted Edwards

These will be treated separately.

Their main attractions include:

* highly symmetric equations;
* unified addition formulas;
* complete addition formulas under suitable conditions;
* efficient full-point arithmetic.

Therefore model selection is not merely aesthetic.

It influences the algorithms used for actual scalar multiplication.

---

<a id="companion-implementation"></a>

## 23. Companion implementation

The original CryptoCave material includes a complete implementation of Montgomery-curve arithmetic.

The implementation is located at:

[`src/montgomery.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/montgomery.py)

Repository path:

```text
experiments/ready-material/elliptic-curves/src/montgomery.py
```

This companion implementation should be read together with the mathematical sections above.

In particular, it can be used to inspect how the abstract formulas translate into executable operations for:

* Montgomery curve representation;
* point handling;
* point addition;
* point doubling;
* scalar multiplication;
* model-specific arithmetic.

The preferred learning path is therefore:

$$
\boxed{
\text{equation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{derive the group formulas}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{understand }x\text{-only arithmetic}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{inspect the implementation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{test the formulas computationally}.
}
$$

The implementation is not a replacement for the mathematical derivation.

It is the executable version of that derivation.

---

<a id="bigger-picture"></a>

## 24. The bigger picture

The previous chapters usually treated an elliptic curve through one particular equation.

We can now separate the conceptual layers.

### Equation

For example,

$$
y^2=x^3+ax+b.
$$

This is a coordinate description.

---

### Curve model

Examples include:

$$
\text{Weierstrass},
\qquad
\text{Montgomery},
\qquad
\text{Edwards}.
$$

These models expose different arithmetic properties.

---

### Isomorphism over the base field

Two equations may already describe the same curve over

$$
K.
$$

---

### Geometric isomorphism

Two curves may become isomorphic only after extending to

$$
\overline K.
$$

The \(j\)-invariant classifies this geometric layer:

$$
\boxed{
E_1\cong_{\overline K}E_2
\iff
j(E_1)=j(E_2).
}
$$

---

### Twists

Curves may therefore satisfy

$$
j(E_1)=j(E_2)
$$

while still being different over the base field.

Twists encode this distinction.

---

### Computational model

Finally, cryptography asks:

> Which representation makes the operations we actually need efficient and robust?

That gives the complete hierarchy:

$$
\boxed{
\text{abstract elliptic curve}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isomorphism class}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{chosen curve model}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{coordinate representation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{implementation}.
}
$$

The implementation link is therefore not an appendix disconnected from the theory.

It is the final layer of the same mathematical story.

That connection —

$$
\boxed{
\text{theory}
\rightarrow
\text{representation}
\rightarrow
\text{algorithm}
\rightarrow
\text{code}
}
$$

— is exactly what we want to preserve throughout the CryptoCave series.

---

## Further reading

Useful references include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Peter L. Montgomery, **Speeding the Pollard and Elliptic Curve Methods of Factorization**.
* Daniel J. Bernstein, **Curve25519: New Diffie-Hellman Speed Records**.
* Craig Costello and Benjamin Smith, work on Montgomery curves and efficient arithmetic.
* RFC 7748, **Elliptic Curves for Security**.
* Darrel Hankerson, Alfred Menezes, and Scott Vanstone, **Guide to Elliptic Curve Cryptography**.

---

The next chapter naturally turns to **Edwards and twisted Edwards curves**.

That will let us compare:

$$
\boxed{
\text{Weierstrass}
}
$$

$$
\boxed{
\text{Montgomery}
}
$$

$$
\boxed{
\text{Edwards}.
}
$$

We will study:

* Edwards equations;
* twisted Edwards models;
* unified and complete addition laws;
* birational equivalence with Montgomery curves;
* edwards25519;
* the relationship between Curve25519/X25519 and Edwards25519/Ed25519;
* why different protocols may use closely related curves but expose completely different arithmetic interfaces.

This continues the central theme:

$$
\boxed{
\text{same mathematics, different representation, different computational advantages}.
}
$$
