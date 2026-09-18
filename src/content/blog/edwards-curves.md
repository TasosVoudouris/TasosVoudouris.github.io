---
title: "Elliptic Curve Mathematics IX: Edwards and Twisted Edwards Curves"
description: "A detailed introduction to Edwards and twisted Edwards models, their symmetric group law, completeness conditions, special points, extended coordinates, and birational connections with Montgomery and Weierstrass curves."
pubDate: "2025-05-25"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Mathematical Foundations"
  - "Cryptographic Engineering"

tags:
  - "edwards-curves"
  - "twisted-edwards"
  - "montgomery-curves"
  - "birational-equivalence"
  - "complete-addition"
  - "ed25519"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 9
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

The previous chapter developed Montgomery curves around one central computational idea:

$$
\boxed{
\text{discard the sign of a point and perform efficient }x\text{-only arithmetic}.
}
$$

Edwards curves take a different approach.

Instead of optimizing primarily for differential scalar multiplication, they expose an extremely symmetric **full-point addition law**.

This symmetry leads to:

* compact formulas;
* unified addition and doubling;
* complete formulas under suitable parameter conditions;
* efficient projective and extended-coordinate arithmetic.

The two models therefore emphasize different operations:

$$
\boxed{
\text{Montgomery}
\rightarrow
x\text{-only scalar multiplication}
}
$$

while

$$
\boxed{
\text{Edwards}
\rightarrow
\text{efficient full-point arithmetic}.
}
$$

The remarkable fact is that these models are often birationally related.

So what looks like a different curve equation may actually be another computational representation of the same underlying elliptic-curve geometry.

---

## Table of Contents

- [1. The unit circle as motivation](#1-the-unit-circle-as-motivation)
- [2. From circle addition to Edwards addition](#2-from-circle-addition-to-edwards-addition)
- [3. Standard Edwards curves](#3-standard-edwards-curves)
- [4. Special points and symmetry](#4-special-points-and-symmetry)
- [5. Edwards group law](#5-edwards-group-law)
- [6. Identity, inverses, and doubling](#6-identity-inverses-and-doubling)
- [7. When are the formulas complete?](#7-when-are-the-formulas-complete)
- [8. Why completeness matters](#8-why-completeness-matters)
- [9. Twisted Edwards curves](#9-twisted-edwards-curves)
- [10. Twisted Edwards group law](#10-twisted-edwards-group-law)
- [11. Completeness for twisted Edwards curves](#11-completeness-for-twisted-edwards-curves)
- [12. The twisted Edwards (j)-invariant](#12-the-twisted-edwards-j-invariant)
- [13. Projective and extended coordinates](#13-projective-and-extended-coordinates)
- [14. Why extended coordinates are useful](#14-why-extended-coordinates-are-useful)
- [15. Edwards to Montgomery](#15-edwards-to-montgomery)
- [16. Montgomery to twisted Edwards](#16-montgomery-to-twisted-edwards)
- [17. From Edwards to Weierstrass](#17-from-edwards-to-weierstrass)
- [18. Which curves admit Edwards form?](#18-which-curves-admit-edwards-form)
- [19. edwards25519](#19-edwards25519)
- [20. Curve25519, X25519, and Ed25519](#20-curve25519-x25519-and-ed25519)
- [21. Symmetry versus x-only arithmetic](#21-symmetry-versus-x-only-arithmetic)
- [22. Companion implementation](#22-companion-implementation)
- [23. The bigger picture](#23-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="unit-circle"></a>

## 1. The unit circle as motivation

The simplest geometric motivation comes from the unit circle

$$
\boxed{
x^2+y^2=1.
}
$$

Over the real numbers, write

$$
x=\sin\alpha,
\qquad
y=\cos\alpha.
$$

Then

$$
(\sin\alpha)^2+(\cos\alpha)^2=1.
$$

Now consider two points corresponding to angles

$$
\alpha_1
\qquad\text{and}\qquad
\alpha_2.
$$

The angle-addition identities say

$$
\sin(\alpha_1+\alpha_2)
=
\sin\alpha_1\cos\alpha_2
+
\cos\alpha_1\sin\alpha_2,
$$

and

$$
\cos(\alpha_1+\alpha_2)
=
\cos\alpha_1\cos\alpha_2
-
\sin\alpha_1\sin\alpha_2.
$$

Thus if

$$
P_1=(x_1,y_1)
$$

and

$$
P_2=(x_2,y_2),
$$

we obtain

$$
\boxed{
P_1+P_2
=
(
x_1y_2+y_1x_2,\;
y_1y_2-x_1x_2
).
}
$$

This is exactly the addition law for angles written algebraically.

That remarkable symmetry inspired the Edwards model.

---

<a id="circle-addition"></a>

## 2. From circle addition to Edwards addition

The ordinary circle does not by itself give the general elliptic-curve family we want.

Edwards' idea is to deform the equation while preserving a similarly symmetric addition structure.

One classical form is

$$
x^2+y^2
=
c^2(1+x^2y^2),
$$

with suitable nonzero \(c\).

After rescaling coordinates, this motivates the more familiar normalized form

$$
\boxed{
x^2+y^2
=
1+dx^2y^2.
}
$$

The parameter

$$
d
$$

controls the deformation away from the circle.

When

$$
d=0,
$$

we recover

$$
x^2+y^2=1.
$$

For elliptic-curve use, however, we require

$$
\boxed{
d\neq0,1.
}
$$

The case \(d=1\) is singular.

---

<a id="standard-edwards"></a>

## 3. Standard Edwards curves

Let \(K\) be a field satisfying

$$
\operatorname{char}(K)\neq2.
$$

A standard Edwards curve is

$$
\boxed{
E_d:
x^2+y^2
=
1+dx^2y^2
}
$$

with

$$
\boxed{
d\in K\setminus\{0,1\}.
}
$$

The equation is strikingly symmetric in \(x\) and \(y\).

If

$$
(x,y)\in E_d,
$$

then the equation immediately implies that points such as

$$
(-x,y),
\qquad
(x,-y),
$$

and

$$
(y,x)
$$

also satisfy closely related symmetries.

This high degree of symmetry is one reason the model supports elegant arithmetic.

---

<a id="special-points"></a>

## 4. Special points and symmetry

Four points always lie on a standard Edwards curve:

$$
\boxed{
(0,1),
\quad
(1,0),
\quad
(0,-1),
\quad
(-1,0).
}
$$

Check:

$$
0^2+1^2=1
$$

and

$$
1+d(0)^2(1)^2=1.
$$

Similarly for the other three.

The identity is

$$
\boxed{
\mathcal O=(0,1).
}
$$

The point

$$
(0,-1)
$$

has order \(2\).

Indeed,

$$
-(0,-1)=(0,-1).
$$

The two points

$$
(1,0)
$$

and

$$
(-1,0)
$$

have order \(4\).

For example,

$$
[2](1,0)=(0,-1),
$$

and hence

$$
[4](1,0)=(0,1).
$$

Thus

$$
\boxed{
\{
(0,1),
(1,0),
(0,-1),
(-1,0)
\}
}
$$

forms a cyclic subgroup of order \(4\).

This built-in \(4\)-torsion is a characteristic feature of standard Edwards form.

---

<p align="center">

<img src="/images/ready/edwards-curves/edwardcurve.PNG" alt="Symmetries and special points on an Edwards curve">

</p>

The diagram illustrates how these special points correspond to natural symmetries of the Edwards equation.

---

<a id="edwards-group-law"></a>

## 5. Edwards group law

Let

$$
P_1=(x_1,y_1),
\qquad
P_2=(x_2,y_2)
$$

lie on

$$
x^2+y^2
=
1+dx^2y^2.
$$

The Edwards addition law is

$$
\boxed{
x_3
=
\frac{
x_1y_2+x_2y_1
}{
1+dx_1x_2y_1y_2
},
}
$$

and

$$
\boxed{
y_3
=
\frac{
y_1y_2-x_1x_2
}{
1-dx_1x_2y_1y_2
}.
}
$$

Then

$$
\boxed{
P_1+P_2=(x_3,y_3).
}
$$

Compare this with short Weierstrass addition.

There is:

* no secant slope \(\lambda\);
* no separate doubling slope;
* much more symmetry between the inputs.

This is one of the main attractions of Edwards form.

---

<a id="identity-inverses"></a>

## 6. Identity, inverses, and doubling

The identity is

$$
\boxed{
\mathcal O=(0,1).
}
$$

Indeed,

$$
(x,y)+(0,1)
$$

gives

$$
x_3
=
\frac{x}{1}=x
$$

and

$$
y_3
=
\frac{y}{1}=y.
$$

So

$$
\boxed{
P+\mathcal O=P.
}
$$

---

### Negation

The inverse is

$$
\boxed{
-(x,y)=(-x,y).
}
$$

This is different from short Weierstrass form, where

$$
-(x,y)=(x,-y).
$$

Substituting \(P\) and \(-P\) into the addition formulas gives

$$
P+(-P)=(0,1).
$$

---

### Doubling

The same addition formula can be used with

$$
P_1=P_2=P.
$$

Thus:

$$
\boxed{
\text{addition and doubling share the same algebraic law}.
}
$$

This is one meaning of a **unified** addition formula.

But unified and complete are not the same concept.

---

<a id="complete-formulas"></a>

## 7. When are the formulas complete?

The affine formulas contain denominators

$$
1+dx_1x_2y_1y_2
$$

and

$$
1-dx_1x_2y_1y_2.
$$

If either denominator vanishes, the affine expression fails.

So the key question is:

> Can these denominators vanish for valid curve points?

For standard Edwards curves over a field of characteristic not \(2\), a particularly important condition is:

$$
\boxed{
d
\text{ is a nonsquare in }K.
}
$$

Under this condition, the Edwards addition law is complete on \(K\)-rational points.

That means the same formulas work for every pair of \(K\)-rational points.

No exceptional addition case is required.

This is stronger than merely saying the same formula handles addition and doubling.

---

### Unified versus complete

These terms should be separated carefully.

**Unified formula** means:

$$
\boxed{
\text{the same formula can represent addition and doubling}.
}
$$

**Complete formula** means:

$$
\boxed{
\text{the formula is defined for every valid input pair}.
}
$$

A formula may be unified without being complete.

This distinction matters greatly in implementation.

---

<a id="why-completeness"></a>

## 8. Why completeness matters

Traditional affine Weierstrass arithmetic has exceptional situations:

* \(P=Q\);
* \(P=-Q\);
* vertical lines;
* \(y=0\);
* the identity point.

A software implementation must detect or structurally avoid such cases.

Complete Edwards formulas can eliminate an entire class of exceptional branches.

This can simplify:

* implementation logic;
* formal verification;
* constant-operation arithmetic;
* resistance to exceptional-case bugs.

But completeness should not be confused with automatic side-channel security.

An implementation still has to consider:

* field arithmetic;
* memory access;
* scalar recoding;
* conditional operations;
* compiler behavior.

The mathematical advantage is that the **group formula itself** does not require exceptional input handling under the completeness conditions.

---

<a id="twisted-edwards"></a>

## 9. Twisted Edwards curves

Standard Edwards form does not cover every elliptic curve.

A more general model is the **twisted Edwards curve**

$$
\boxed{
E_{a,d}:
ax^2+y^2
=
1+dx^2y^2,
}
$$

where

$$
\boxed{
a,d\neq0,
\qquad
a\neq d.
}
$$

When

$$
a=1,
$$

we recover standard Edwards form:

$$
x^2+y^2
=
1+dx^2y^2.
$$

Twisted Edwards curves enlarge the family of elliptic curves that can be represented in Edwards-like coordinates.

In particular, the rational \(4\)-torsion requirement associated with standard Edwards form is relaxed.

The connection is instead closely tied to Montgomery models and rational \(2\)-torsion.

---

<a id="twisted-group-law"></a>

## 10. Twisted Edwards group law

For

$$
P_1=(x_1,y_1),
\qquad
P_2=(x_2,y_2),
$$

on

$$
ax^2+y^2
=
1+dx^2y^2,
$$

define

$$
\boxed{
x_3
=
\frac{
x_1y_2+x_2y_1
}{
1+dx_1x_2y_1y_2
},
}
$$

and

$$
\boxed{
y_3
=
\frac{
y_1y_2-a x_1x_2
}{
1-dx_1x_2y_1y_2
}.
}
$$

Then

$$
P_1+P_2=(x_3,y_3).
$$

The identity remains

$$
\boxed{
(0,1),
}
$$

and negation remains

$$
\boxed{
-(x,y)=(-x,y).
}
$$

Again, the same basic formula handles doubling by setting

$$
P_1=P_2.
$$

---

<a id="twisted-completeness"></a>

## 11. Completeness for twisted Edwards curves

For twisted Edwards curves, an important complete setting is:

$$
\boxed{
a
\text{ is a square in }K
}
$$

and

$$
\boxed{
d
\text{ is a nonsquare in }K.
}
$$

Under these conditions, the standard twisted-Edwards addition formulas are complete for \(K\)-rational points.

This is the parameter shape used by edwards25519.

There,

$$
a=-1
$$

is a square in the chosen field, while

$$
d
$$

is selected as a nonsquare.

This is not accidental.

The parameter choice is aligned with the arithmetic properties needed for efficient complete formulas.

---

<a id="twisted-j"></a>

## 12. The twisted Edwards \(j\)-invariant

For

$$
E_{a,d}:
ax^2+y^2=1+dx^2y^2,
$$

the \(j\)-invariant is

$$
\boxed{
j(E_{a,d})
=
16
\frac{
(a^2+14ad+d^2)^3
}{
ad(a-d)^4
}.
}
$$

This once again demonstrates that the raw parameters

$$
a,d
$$

are model parameters.

The geometric isomorphism class is governed by the corresponding invariant.

Different twisted Edwards equations may therefore describe geometrically isomorphic elliptic curves.

---

<a id="extended-coordinates"></a>

## 13. Projective and extended coordinates

The affine Edwards formulas contain division.

Real implementations avoid repeated field inversions by moving to projective coordinates.

A common representation is

$$
\boxed{
(X:Y:Z)
}
$$

with

$$
x=\frac XZ,
\qquad
y=\frac YZ.
$$

For twisted Edwards arithmetic, an especially useful representation introduces an additional coordinate \(T\):

$$
\boxed{
(X:Y:Z:T).
}
$$

The coordinates satisfy

$$
\boxed{
XY=ZT.
}
$$

Equivalently,

$$
T=\frac{XY}{Z}.
$$

For an affine point

$$
(x,y),
$$

one simple representative is

$$
\boxed{
(X:Y:Z:T)
=
(x:y:1:xy).
}
$$

These are commonly called **extended Edwards coordinates**.

---

<a id="why-extended"></a>

## 14. Why extended coordinates are useful

The extra coordinate

$$
T
$$

may initially look redundant.

But Edwards addition repeatedly needs the product

$$
xy.
$$

By maintaining \(T\), that product does not have to be recomputed from scratch during every operation.

This enables very efficient addition formulas.

For example, for the important case

$$
a=-1,
$$

complete extended-coordinate formulas can be written using a compact sequence of:

* additions;
* subtractions;
* multiplications;
* doublings.

No field inversion is required inside the main group operation.

The final affine recovery is postponed until needed.

This is analogous in spirit to the \(X:Z\) strategy from Montgomery arithmetic:

$$
\boxed{
\text{avoid inversions during the main computation}.
}
$$

But unlike Montgomery x-only arithmetic, Edwards extended coordinates retain the **full group point**.

---

<a id="edwards-to-montgomery"></a>

## 15. Edwards to Montgomery

Let

$$
E_{a,d}:
ax^2+y^2
=
1+dx^2y^2
$$

with

$$
a\neq d.
$$

Define Montgomery coordinates

$$
\boxed{
u=\frac{1+y}{1-y},
}
$$

$$
\boxed{
v=
\frac{1+y}{x(1-y)}.
}
$$

Then the corresponding Montgomery curve has the form

$$
\boxed{
Bv^2
=
u^3+Au^2+u,
}
$$

with

$$
\boxed{
A
=
\frac{2(a+d)}{a-d},
}
$$

$$
\boxed{
B
=
\frac4{a-d}.
}
$$

Thus the two models are **birationally equivalent**.

The maps are rational and invertible away from a finite collection of exceptional points where denominators vanish.

This is why we say birational rather than claiming that the affine coordinate charts are literally identical everywhere.

---

<a id="montgomery-to-edwards"></a>

## 16. Montgomery to twisted Edwards

Conversely, start with

$$
M_{A,B}:
Bv^2
=
u^3+Au^2+u.
$$

Define

$$
\boxed{
x=\frac uv,
}
$$

and

$$
\boxed{
y=\frac{u-1}{u+1}.
}
$$

The corresponding twisted Edwards parameters are

$$
\boxed{
a=\frac{A+2}{B},
}
$$

and

$$
\boxed{
d=\frac{A-2}{B}.
}
$$

Thus:

$$
\boxed{
\text{Montgomery}
\longleftrightarrow
\text{twisted Edwards}
}
$$

under the appropriate nonsingularity assumptions.

This relationship explains why the same underlying elliptic-curve mathematics can support two very different arithmetic interfaces.

---

<a id="edwards-to-weierstrass"></a>

## 17. From Edwards to Weierstrass

Because a twisted Edwards curve can be converted to a Montgomery model, and Montgomery curves can be converted to Weierstrass form, we obtain the conceptual chain

$$
\boxed{
\text{twisted Edwards}
\longrightarrow
\text{Montgomery}
\longrightarrow
\text{Weierstrass}.
}
$$

This is preferable pedagogically to memorizing several unrelated direct coordinate transformations.

From Chapter VIII,

$$
Bv^2
=
u^3+Au^2+u
$$

can be transformed, when

$$
\operatorname{char}(K)\neq2,3,
$$

into short Weierstrass form

$$
Y^2=X^3+\alpha X+\beta.
$$

Thus all three models belong to the same general elliptic-curve world:

$$
\boxed{
\text{Weierstrass}
\leftrightarrow
\text{Montgomery}
\leftrightarrow
\text{twisted Edwards}.
}
$$

But the existence of these models over the **same base field** depends on arithmetic conditions.

---

<a id="which-curves"></a>

## 18. Which curves admit Edwards form?

Not every elliptic curve over a field \(K\) can be written in standard Edwards form over \(K\).

Standard Edwards form naturally contains the rational point

$$
(1,0)
$$

of order \(4\).

Thus a curve birationally equivalent over \(K\) to a standard Edwards curve must support the required rational \(4\)-torsion structure.

Twisted Edwards form is more general.

Its relationship with Montgomery form means that the important structural requirement is closer to the existence of suitable rational \(2\)-torsion and the corresponding Montgomery representation.

So the progression is:

$$
\boxed{
\text{standard Edwards}
\subsetneq
\text{twisted Edwards}
}
$$

at the level of representable elliptic curves over a fixed field.

Twisting the Edwards coefficient \(a\) enlarges the class of curves that admit an Edwards-style model.

---

<a id="edwards25519"></a>

## 19. edwards25519

A major real-world example is **edwards25519**.

It is defined over

$$
\mathbb F_p
$$

with

$$
\boxed{
p=2^{255}-19.
}
$$

Its twisted Edwards equation is

$$
\boxed{
-x^2+y^2
=
1+dx^2y^2
}
$$

with

$$
\boxed{
a=-1
}
$$

and

$$
\boxed{
d
=
-\frac{121665}{121666}
\pmod p.
}
$$

The prime-order subgroup has order

$$
\boxed{
L
=
2^{252}
+
27742317777372353535851937790883648493.
}
$$

The full curve group has cofactor

$$
\boxed{
8.
}
$$

The standard base point has

$$
\boxed{
y=\frac45
}
$$

in \(\mathbb F_p\), together with the specified corresponding \(x\)-coordinate.

These are the parameters underlying Ed25519.

---

### Why this parameter choice is interesting

For edwards25519:

$$
a=-1
$$

and

$$
d
$$

satisfy the field conditions required for the complete twisted-Edwards addition formulas used in Ed25519 implementations.

RFC 8032 therefore represents points using extended coordinates

$$
(X,Y,Z,T)
$$

and uses complete addition formulas for valid curve points.

This is a real standardized use of the mathematics developed in this chapter.

---

<a id="curve25519-ed25519"></a>

## 20. Curve25519, X25519, and Ed25519

An important conceptual distinction is needed here.

**Curve25519** refers to the underlying elliptic-curve setting historically associated with the Montgomery model

$$
v^2
=
u^3+486662u^2+u.
$$

The related twisted Edwards model is edwards25519.

The two representations are birationally equivalent over the field.

But the protocols **X25519** and **Ed25519** do very different things.

---

### X25519

X25519 is designed for Diffie–Hellman-style scalar multiplication.

It naturally uses:

$$
\boxed{
\text{Montgomery }u\text{-coordinates}
}
$$

and the

$$
\boxed{
\text{Montgomery ladder}.
}
$$

It does not generally need full point addition.

---

### Ed25519

Ed25519 is a digital-signature scheme.

It needs full group elements and operations such as

$$
R+[k]A.
$$

The twisted Edwards representation provides efficient full-point addition.

Thus:

$$
\boxed{
\text{X25519}
\rightarrow
\text{Montgomery arithmetic},
}
$$

while

$$
\boxed{
\text{Ed25519}
\rightarrow
\text{twisted Edwards arithmetic}.
}
$$

The relation between the curves does **not** mean the protocols are interchangeable.

They expose different representations because they solve different cryptographic problems.

---

<a id="model-comparison"></a>

## 21. Symmetry versus x-only arithmetic

We can now compare the two models directly.

| Property                  | Montgomery                   | Twisted Edwards                             |
| ------------------------- | ---------------------------- | ------------------------------------------- |
| Typical equation          | \(By^2=x^3+Ax^2+x\)          | \(ax^2+y^2=1+dx^2y^2\)                      |
| Identity                  | \(\mathcal O\)               | \((0,1)\)                                   |
| Negation                  | \((x,-y)\)                   | \((-x,y)\)                                  |
| Main strength             | x-only scalar multiplication | full-point addition                         |
| Differential addition     | Excellent                    | not the main design goal                    |
| Unified addition/doubling | Not the principal feature    | Yes                                         |
| Complete formulas         | Model-dependent formulas     | Available under suitable \(a,d\) conditions |
| Common coordinates        | \(X:Z\)                      | \(X:Y:Z:T\)                                 |
| Typical modern example    | X25519                       | Ed25519                                     |

Neither model is simply “better”.

They expose different structure.

For Diffie–Hellman:

$$
\boxed{
x\text{-only arithmetic}
}
$$

is often exactly what we want.

For signatures:

$$
\boxed{
\text{efficient full group arithmetic}
}
$$

is usually more natural.

The representation follows the operation.

---

<a id="companion-implementation"></a>

## 22. Companion implementation

The CryptoCave material includes a Sage implementation of Edwards-curve arithmetic:

[`src/edwards.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/edwards.sage)

Repository path:

```text
experiments/ready-material/elliptic-curves/src/edwards.sage
```

This implementation should be read together with the mathematical derivations in this chapter.

Useful questions to check while studying the code include:

1. Which Edwards model is implemented: standard or twisted?
2. How is the identity

   $$
   (0,1)
   $$

   represented?
3. Is negation implemented as

   $$
   (-x,y)?
   $$
4. Does the implementation use affine or projective coordinates?
5. Are the completeness assumptions on \(d\), or on \(a,d\), documented?
6. Is doubling implemented separately or through the unified addition law?
7. Are denominators explicitly inverted?
8. Does the code check curve membership?
9. How are exceptional points handled?
10. Can the implementation be related directly to the Montgomery transformations from Chapter VIII?

The desired learning path is

$$
\boxed{
\text{Edwards equation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{derive addition law}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{study completeness}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{move to projective/extended coordinates}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{inspect executable implementation}.
}
$$

As throughout CryptoCave, the code is the executable counterpart of the mathematics rather than a replacement for it.

---

<a id="bigger-picture"></a>

## 23. The bigger picture

The last three chapters now fit together naturally.

### Chapter VII

We separated the abstract elliptic curve from its coordinate model:

$$
\boxed{
\text{curve}
\neq
\text{equation}.
}
$$

The \(j\)-invariant classified geometric isomorphism classes.

---

### Chapter VIII

Montgomery form exploited the identification

$$
P\sim-P
$$

to move to the Kummer line and perform

$$
\boxed{
x\text{-only scalar multiplication}.
}
$$

This produced:

$$
\operatorname{xDBL},
\qquad
\operatorname{xADD},
\qquad
\text{Montgomery ladder}.
$$

---

### Chapter IX

Edwards form takes a different route.

Its highly symmetric equation gives:

$$
\boxed{
\text{unified full-point addition}
}
$$

and, under suitable arithmetic conditions,

$$
\boxed{
\text{complete addition formulas}.
}
$$

Twisted Edwards curves broaden the model and connect directly to Montgomery form:

$$
\boxed{
ax^2+y^2=1+dx^2y^2
}
$$

$$
\Updownarrow
$$

$$
\boxed{
Bv^2=u^3+Au^2+u.
}
$$

Thus one underlying elliptic-curve setting can support two very different computational interfaces:

$$
\boxed{
\text{Montgomery}
\rightarrow
\text{x-only arithmetic},
}
$$

$$
\boxed{
\text{Edwards}
\rightarrow
\text{full-point arithmetic}.
}
$$

That distinction is visible in real cryptography:

$$
\boxed{
\text{X25519}
\rightarrow
\text{Montgomery ladder},
}
$$

while

$$
\boxed{
\text{Ed25519}
\rightarrow
\text{twisted Edwards addition}.
}
$$

The deeper lesson is the same one that has been developing throughout this part of the series:

$$
\boxed{
\text{the mathematical representation should match the operation we need}.
}
$$

A curve model is not merely a different way to draw the same object.

It determines which algebraic symmetries become computationally visible.

And those visible symmetries can dramatically change the efficiency, simplicity, and robustness of the resulting implementation.

---

## Further reading

Useful references for this chapter include:

* Harold Edwards, **A Normal Form for Elliptic Curves**.
* Daniel J. Bernstein and Tanja Lange, **Faster Addition and Doubling on Elliptic Curves**.
* Hisil, Wong, Carter, and Dawson, **Twisted Edwards Curves Revisited**.
* RFC 8032, **Edwards-Curve Digital Signature Algorithm (EdDSA)**.
* RFC 7748, **Elliptic Curves for Security**.
* Daniel J. Bernstein et al., work on Ed25519.
* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.

---

The next chapter can now move naturally to **coordinate systems and implementation arithmetic** across elliptic-curve models.

We have already encountered:

$$
(x,y),
$$

$$
(X:Y:Z),
$$

$$
(X:Z),
$$

and

$$
(X:Y:Z:T).
$$

The next mathematical question is:

> Why do projective, Jacobian, extended Edwards, and mixed coordinates change performance so dramatically even though they represent the same points?

That would let us study:

* affine versus projective arithmetic;
* inversion versus multiplication cost;
* Jacobian coordinates;
* mixed addition;
* extended Edwards coordinates;
* batch inversion;
* coordinate normalization;
* operation-count models.

That is the natural bridge from curve models to serious elliptic-curve implementation mathematics.
