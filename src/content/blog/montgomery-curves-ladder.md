---
title: "Elliptic Curve Mathematics VIII: Montgomery Curves, x-Only Arithmetic, and the Montgomery Ladder"
description: "A detailed study of Montgomery-form elliptic curves: projective x-coordinate arithmetic, differential addition, xDBL/xADD formulas, the Montgomery ladder, implementation regularity, and relations with Weierstrass and Edwards models."
pubDate: "2025-03-19"
updatedDate: "2026-09-17"

topics:
  - "Mathematical Foundations"
  - "Elliptic Curve Theory"
  - "Cryptographic Engineering"

tags:
  - "montgomery-curves"
  - "montgomery-ladder"
  - "x-only-arithmetic"
  - "differential-addition"
  - "curve-models"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 8
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

The previous chapter introduced Montgomery curves as one possible model of an elliptic curve.

We now study why that model became so important computationally.

A Montgomery curve over a field \(K\) of characteristic different from \(2\) has the form

$$
\boxed{
M_{A,B}:
By^2=x^3+Ax^2+x,
}
$$

where

$$
\boxed{
B(A^2-4)\neq0.
}
$$

The model is not important merely because its equation looks different from short Weierstrass form.

Its real advantage is that scalar multiplication can be performed using essentially only the \(x\)-coordinate.

This leads to:

$$
\boxed{
\text{xDBL}
}
$$

for doubling,

$$
\boxed{
\text{xADD}
}
$$

for differential addition,

and ultimately the

$$
\boxed{
\text{Montgomery ladder}.
}
$$

These ideas form the mathematical foundation of constructions such as X25519.

---

## Table of Contents

- [1. Montgomery curves](#1-montgomery-curves)
- [2. Basic geometric structure](#2-basic-geometric-structure)
- [3. Why the (x)-coordinate is special](#3-why-the-x-coordinate-is-special)
- [4. The Kummer-line viewpoint](#4-the-kummer-line-viewpoint)
- [5. Projective (X:Z) coordinates](#5-projective-xz-coordinates)
- [6. Deriving (x(2P))](#6-deriving-x2p)
- [7. Projective xDBL formulas](#7-projective-xdbl-formulas)
- [8. The (A_${24}) optimization](#8-the-a_24-optimization)
- [9. Differential addition](#9-differential-addition)
- [10. Projective xADD formulas](#10-projective-xadd-formulas)
- [11. Why xADD needs (P-Q)](#11-why-xadd-needs-p-q)
- [12. Combined xDBLADD](#12-combined-xdbladd)
- [13. The Montgomery ladder invariant](#13-the-montgomery-ladder-invariant)
- [14. One ladder step](#14-one-ladder-step)
- [15. Why the ladder is efficient](#15-why-the-ladder-is-efficient)
- [16. Constant-time considerations](#16-constant-time-considerations)
- [17. Recovering an affine coordinate](#17-recovering-an-affine-coordinate)
- [18. Curve25519 and X25519](#18-curve25519-and-x25519)
- [19. The Montgomery (j)-invariant](#19-the-montgomery-j-invariant)
- [20. Relation to Weierstrass form](#20-relation-to-weierstrass-form)
- [21. Relation to twisted Edwards curves](#21-relation-to-twisted-edwards-curves)
- [22. What x-only arithmetic loses](#22-what-x-only-arithmetic-loses)
- [23. Companion implementation](#23-companion-implementation)
- [24. The bigger picture](#24-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="montgomery-curves"></a>

## 1. Montgomery curves

A Montgomery curve is written

$$
M_{A,B}:
By^2=x^3+Ax^2+x.
$$

We require

$$
B\neq0
$$

and

$$
A^2\neq4.
$$

Equivalently,

$$
\boxed{
B(A^2-4)\neq0.
}
$$

These conditions ensure nonsingularity.

The projective closure is

$$
\boxed{
BY^2Z
=
X^3+AX^2Z+XZ^2.
}
$$

As with Weierstrass curves, the unique point at infinity is

$$
\boxed{
\mathcal O=(0:1:0).
}
$$

---

### A built-in \(2\)-torsion point

Set

$$
x=0.
$$

Then

$$
By^2=0.
$$

Since

$$
B\neq0,
$$

we obtain

$$
y=0.
$$

Thus

$$
\boxed{
T=(0,0)
}
$$

lies on every Montgomery curve.

Since

$$
-T=(0,-0)=T,
$$

we have

$$
\boxed{
[2]T=\mathcal O.
}
$$

So Montgomery form naturally exposes a rational point of order \(2\).

---

<a id="basic-structure"></a>

## 2. Basic geometric structure

Negation is the usual reflection

$$
\boxed{
-(x,y)=(x,-y).
}
$$

For distinct affine points

$$
P=(x_P,y_P),
\qquad
Q=(x_Q,y_Q),
$$

the secant slope is

$$
\lambda
=
\frac{y_Q-y_P}{x_Q-x_P}.
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

Thus ordinary affine addition works exactly as expected.

But this is not why Montgomery curves are computationally exceptional.

The real advantage appears when we stop computing \(y\).

---

<a id="x-coordinate-special"></a>

## 3. Why the \(x\)-coordinate is special

For every point

$$
P=(x,y),
$$

its inverse is

$$
-P=(x,-y).
$$

Therefore,

$$
\boxed{
x(P)=x(-P).
}
$$

So the \(x\)-coordinate forgets the sign of a point.

The map

$$
P\longmapsto x(P)
$$

therefore identifies

$$
P
$$

and

$$
-P.
$$

Instead of working with the whole elliptic-curve group, we can sometimes work with the quotient

$$
\boxed{
E/\{\pm1\}.
}
$$

This quotient retains enough information for scalar multiplication when only the final \(x\)-coordinate is needed.

That is exactly the setting used by Montgomery \(x\)-coordinate arithmetic.

---

<a id="kummer-line"></a>

## 4. The Kummer-line viewpoint

For an elliptic curve, the quotient

$$
E/\{\pm1\}
$$

is represented by a projective line

$$
\mathbb P^1.
$$

This is often called the **Kummer line**.

A finite affine point is represented by its \(x\)-coordinate.

The point at infinity maps to the projective point at infinity of the \(x\)-line.

Thus:

$$
\boxed{
P
\sim
-P
}
$$

on the Kummer line.

This immediately explains an important limitation.

Given only

$$
x(P)
$$

and

$$
x(Q),
$$

we cannot in general determine whether the original group operation should use

$$
P+Q
$$

or

$$
P-Q.
$$

The sign information has been discarded.

Montgomery arithmetic solves this using **differential addition**.

---

<a id="projective-xz"></a>

## 5. Projective \(X:Z\) coordinates

Instead of representing an \(x\)-coordinate as a field element

$$
x,
$$

represent it projectively as

$$
\boxed{
(X:Z),
}
$$

where

$$
x=\frac XZ
$$

whenever

$$
Z\neq0.
$$

The pairs

$$
(X:Z)
$$

and

$$
(\lambda X:\lambda Z)
$$

represent the same coordinate for every nonzero \(\lambda\).

For example,

$$
x=5
$$

can be represented as

$$
(5:1),
$$

but also as

$$
(10:2).
$$

The point at infinity on the \(x\)-line is represented by

$$
\boxed{
(1:0).
}
$$

---

### Why projective coordinates help

Affine arithmetic repeatedly requires inversions.

For example,

$$
x=\frac XZ
$$

would require computing

$$
Z^{-1}.
$$

Field inversion is substantially more expensive than multiplication or squaring in many implementations.

Projective arithmetic postpones the inversion until the end.

The main scalar-multiplication loop therefore uses only operations such as:

* addition;
* subtraction;
* multiplication;
* squaring.

This is one of the central engineering advantages of the Montgomery ladder.

---

<a id="derive-xdbl"></a>

## 6. Deriving \(x(2P)\)

Let

$$
P=(x,y)
$$

on

$$
By^2=x^3+Ax^2+x.
$$

The tangent slope is

$$
\lambda
=
\frac{3x^2+2Ax+1}{2By}.
$$

The doubled \(x\)-coordinate is

$$
x(2P)
=
B\lambda^2-A-2x.
$$

After substituting the curve equation

$$
By^2=x(x^2+Ax+1)
$$

and simplifying, we obtain the classical Montgomery doubling formula:

$$
\boxed{
x(2P)
=
\frac{(x^2-1)^2}
{4x(x^2+Ax+1)}.
}
$$

This expression depends only on

$$
x(P).
$$

The \(y\)-coordinate has disappeared.

That is the key observation behind xDBL.

---

<a id="xdbl"></a>

## 7. Projective xDBL formulas

Write

$$
x(P)=\frac XZ.
$$

Substitute into the affine doubling expression.

A homogeneous representation for

$$
x(2P)
=
\frac{X_2}{Z_2}
$$

is

$$
\boxed{
X_2
=
(X^2-Z^2)^2,
}
$$

$$
\boxed{
Z_2
=
4XZ
\left(
X^2+AXZ+Z^2
\right).
}
$$

Therefore:

$$
\boxed{
(X:Z)
\overset{\operatorname{xDBL}}{\longmapsto}
(X_2:Z_2).
}
$$

No field inversion is required.

---

<a id="a24"></a>

## 8. The \(A_{24}\) optimization

The doubling formulas can be rearranged into an implementation-friendly form.

Define

$$
U=X+Z,
$$

$$
V=X-Z.
$$

Then

$$
U^2=(X+Z)^2,
$$

$$
V^2=(X-Z)^2.
$$

Let

$$
E=U^2-V^2.
$$

Since

$$
E=4XZ,
$$

we can write

$$
X_2=U^2V^2.
$$

For \(Z_2\), define

$$
\boxed{
A_{24}^{-}
=
\frac{A-2}{4}.
}
$$

Then

$$
\boxed{
Z_2
=
E
\left(
U^2+A_{24}^{-}E
\right).
}
$$

An equivalent convention uses

$$
\boxed{
A_{24}^{+}
=
\frac{A+2}{4},
}
$$

giving

$$
\boxed{
Z_2
=
E
\left(
V^2+A_{24}^{+}E
\right).
}
$$

These formulas are algebraically equivalent.

This is an important implementation detail because literature and software may define \(A_{24}\) differently.

So seeing either

$$
\frac{A-2}{4}
$$

or

$$
\frac{A+2}{4}
$$

does not automatically mean one implementation is wrong.

The accompanying formula determines the convention.

---

<a id="differential-addition"></a>

## 9. Differential addition

Suppose we know

$$
x(P),
\qquad
x(Q),
$$

but not the corresponding \(y\)-coordinates.

As discussed earlier, this is not enough to determine

$$
x(P+Q)
$$

unambiguously.

But suppose we additionally know

$$
\boxed{
x(P-Q).
}
$$

Then the ambiguity disappears.

We can compute

$$
\boxed{
x(P+Q).
}
$$

This operation is called **differential addition**.

Symbolically,

$$
\boxed{
x(P),x(Q),x(P-Q)
\longrightarrow
x(P+Q).
}
$$

In Montgomery arithmetic it is called

$$
\boxed{
\operatorname{xADD}.
}
$$

This is not ordinary point addition.

It is a pseudo-operation on the Kummer line.

---

<a id="xadd"></a>

## 10. Projective xADD formulas

Let

$$
x(P)=(X_P:Z_P),
$$

$$
x(Q)=(X_Q:Z_Q),
$$

and suppose the known difference is

$$
x(P-Q)=(X_D:Z_D).
$$

Define

$$
A_P=X_P+Z_P,
$$

$$
B_P=X_P-Z_P,
$$

$$
A_Q=X_Q+Z_Q,
$$

$$
B_Q=X_Q-Z_Q.
$$

Now compute

$$
DA=B_QA_P,
$$

and

$$
CB=A_QB_P.
$$

Then a projective representation of \(x(P+Q)\) is

$$
\boxed{
X_{P+Q}
=
Z_D(DA+CB)^2,
}
$$

$$
\boxed{
Z_{P+Q}
=
X_D(DA-CB)^2.
}
$$

Thus

$$
\boxed{
\operatorname{xADD}
\left(
x(P),
x(Q),
x(P-Q)
\right)
=
x(P+Q).
}
$$

Again:

* no \(y\)-coordinate;
* no inversion;
* only field additions, subtractions, multiplications, and squarings.

---

<a id="why-difference"></a>

## 11. Why xADD needs \(P-Q\)

Why is the difference required?

Because

$$
x(Q)=x(-Q).
$$

Suppose we know only

$$
x(P)
$$

and

$$
x(Q).
$$

The coordinate data cannot distinguish \(Q\) from \(-Q\).

But

$$
P+Q
$$

and

$$
P-Q
$$

usually have different \(x\)-coordinates.

Therefore the operation

$$
(x(P),x(Q))
\longmapsto
x(P+Q)
$$

is not intrinsically well defined.

Providing

$$
x(P-Q)
$$

resolves the missing sign information indirectly.

This explains the word **differential** in differential addition.

The known difference supplies the extra relation needed to recover the sum.

---

<a id="xdbladd"></a>

## 12. Combined xDBLADD

In a Montgomery ladder we frequently need to compute simultaneously:

$$
x(2P)
$$

and

$$
x(P+Q).
$$

The two operations reuse several intermediate quantities.

For

$$
P=(X_P:Z_P)
$$

and

$$
Q=(X_Q:Z_Q),
$$

we already need

$$
X_P+Z_P,
\qquad
X_P-Z_P.
$$

These same values participate in both xDBL and xADD.

Implementations therefore often combine the operations into a single

$$
\boxed{
\operatorname{xDBLADD}
}
$$

routine.

Conceptually,

$$
\boxed{
(P,Q,P-Q)
\longrightarrow
(2P,P+Q).
}
$$

The mathematical benefit is modest.

The implementation benefit is substantial:

* intermediate values are reused;
* fewer field operations may be required;
* the ladder step becomes highly regular.

---

<a id="ladder-invariant"></a>

## 13. The Montgomery ladder invariant

Suppose we wish to compute

$$
[n]P.
$$

During the ladder, maintain two points:

$$
\boxed{
R_0=[k]P,
}
$$

$$
\boxed{
R_1=[k+1]P.
}
$$

Their difference is always

$$
R_1-R_0=P.
$$

Therefore,

$$
\boxed{
x(R_1-R_0)=x(P)
}
$$

is known throughout the entire computation.

That means differential addition is always available.

This is the key invariant of the Montgomery ladder:

$$
\boxed{
R_1-R_0=P.
}
$$

The entire algorithm is built around preserving it.

---

<a id="ladder-step"></a>

## 14. One ladder step

Suppose the current state is

$$
(R_0,R_1)
=
([k]P,[k+1]P).
$$

There are two possible next states.

### Next scalar bit is \(0\)

We need

$$
[2k]P
$$

and

$$
[2k+1]P.
$$

Therefore,

$$
\boxed{
(R_0,R_1)
\longmapsto
(2R_0,R_0+R_1).
}
$$

---

### Next scalar bit is \(1\)

We need

$$
[2k+1]P
$$

and

$$
[2k+2]P.
$$

Therefore,

$$
\boxed{
(R_0,R_1)
\longmapsto
(R_0+R_1,2R_1).
}
$$

In both cases we compute:

* one doubling;
* one differential addition.

The difference between the two registers remains

$$
P.
$$

This is exactly what the next iteration requires.

---

<a id="ladder-efficiency"></a>

## 15. Why the ladder is efficient

Suppose the scalar \(n\) has bit length

$$
\ell.
$$

The Montgomery ladder processes approximately one bit per iteration.

Each iteration performs essentially:

$$
\boxed{
1\times \operatorname{xDBL}
+
1\times \operatorname{xADD}.
}
$$

Therefore scalar multiplication requires

$$
O(\log n)
$$

ladder steps.

But the advantage is not merely asymptotic complexity.

Ordinary double-and-add might perform:

* one doubling for every bit;
* an addition only when the bit equals \(1\).

That creates a visibly different operation pattern depending on the secret scalar.

The Montgomery ladder instead follows a much more regular pattern:

$$
\boxed{
\text{one doubling + one differential addition per bit}.
}
$$

This regularity is extremely useful for cryptographic engineering.

---

<a id="constant-time"></a>

## 16. Constant-time considerations

A common oversimplification is:

> “The Montgomery ladder is constant time.”

That statement is too strong.

The ladder has a **regular mathematical operation structure**.

A constant-time implementation still requires care.

Among other things, one must consider:

* scalar-bit handling;
* conditional swaps;
* field multiplication;
* field squaring;
* modular reduction;
* memory accesses;
* carry propagation;
* inversion;
* compiler transformations;
* microarchitectural behavior.

A ladder implementation often uses a conditional swap operation

$$
\operatorname{cswap}
$$

to exchange the two projective states according to a scalar bit without ordinary secret-dependent branching.

Conceptually:

$$
\boxed{
\text{secret bit}
\rightarrow
\text{conditional swap}
\rightarrow
\text{same arithmetic sequence}.
}
$$

But even a branchless source-code implementation is not automatically secure on every architecture or compiler.

The correct lesson is:

$$
\boxed{
\text{Montgomery ladder}
\Rightarrow
\text{regular structure favorable to constant-time implementation},
}
$$

not

$$
\boxed{
\text{Montgomery ladder}
\Rightarrow
\text{automatic side-channel security}.
}
$$

---

<a id="affine-recovery"></a>

## 17. Recovering an affine coordinate

After the ladder finishes, suppose the result is represented as

$$
(X:Z).
$$

To recover the affine coordinate,

$$
x=\frac XZ.
$$

Over a finite field,

$$
\boxed{
x=XZ^{-1}.
}
$$

Thus one inversion is performed at the end.

Over a prime field \(\mathbb F_p\), Fermat's little theorem gives

$$
Z^{-1}
=
Z^{p-2}
\pmod p
$$

for

$$
Z\neq0.
$$

So the overall strategy is:

$$
\boxed{
\text{many projective ladder steps}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{no inversion in the main loop}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{one final inversion}.
}
$$

This is often far more efficient than repeatedly returning to affine coordinates.

---

<a id="curve25519"></a>

## 18. Curve25519 and X25519

The most famous modern Montgomery example is Curve25519.

It is defined over

$$
\mathbb F_p
$$

where

$$
\boxed{
p=2^{255}-19.
}
$$

Its Montgomery equation is

$$
\boxed{
v^2
=
u^3+486662u^2+u.
}
$$

Thus

$$
A=486662,
\qquad
B=1.
$$

For the RFC 7748 ladder convention,

$$
\boxed{
A_{24}
=
\frac{A-2}{4}
=
121665.
}
$$

A standard base coordinate is

$$
\boxed{
u=9.
}
$$

The X25519 operation takes:

* a scalar;
* a Montgomery \(u\)-coordinate;

and returns another \(u\)-coordinate.

It therefore matches exactly the arithmetic developed in this chapter:

$$
\boxed{
\text{scalar}
+
u(P)
\longrightarrow
u([n]P).
}
$$

Importantly, X25519 is more than the abstract ladder.

Its standardized definition also specifies details such as:

* scalar decoding;
* scalar-bit modification;
* coordinate encoding;
* field interpretation;
* byte ordering.

So, as with the lattice standards studied elsewhere in CryptoCave:

$$
\boxed{
\text{mathematical primitive}
\neq
\text{complete standardized interface}.
}
$$

---

<a id="montgomery-j"></a>

## 19. The Montgomery \(j\)-invariant

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

Notice that \(B\) disappears.

This reflects the fact that over an algebraic closure, \(B\) can be absorbed through a \(y\)-coordinate rescaling.

Thus the raw parameter \(A\) is not itself the invariant.

The actual geometric invariant is

$$
\boxed{
j.
}
$$

Different \(A\)-values or coordinate conventions can therefore require more care than simply comparing raw parameters.

---

<a id="weierstrass-relation"></a>

## 20. Relation to Weierstrass form

Assume

$$
\operatorname{char}(K)\neq2,3.
$$

Starting from

$$
By^2=x^3+Ax^2+x,
$$

define

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

Then the equation becomes

$$
v^2=t^3+at+b
$$

with

$$
\boxed{
a
=
\frac{3-A^2}{3B^2},
}
$$

$$
\boxed{
b
=
\frac{2A^3-9A}{27B^3}.
}
$$

So the Montgomery equation is not a fundamentally different type of genus-one object.

It is another model of an elliptic curve.

The distinction is computational:

$$
\boxed{
\text{Weierstrass}
\rightarrow
\text{general full-point arithmetic},
}
$$

whereas

$$
\boxed{
\text{Montgomery}
\rightarrow
\text{particularly efficient }x\text{-only arithmetic}.
}
$$

---

<a id="edwards-relation"></a>

## 21. Relation to twisted Edwards curves

A twisted Edwards curve has equation

$$
\boxed{
E_{a,d}:
ax^2+y^2
=
1+dx^2y^2,
}
$$

with suitable nonzero and distinct parameters.

Under appropriate parameter conditions, twisted Edwards and Montgomery models are birationally equivalent.

A standard transformation from twisted Edwards coordinates to Montgomery coordinates is

$$
\boxed{
u
=
\frac{1+y}{1-y},
}
$$

$$
\boxed{
v
=
\frac{1+y}{(1-y)x}.
}
$$

The corresponding Montgomery parameters are

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
\frac{4}{a-d}.
}
$$

Conversely,

$$
\boxed{
x=\frac uv,
}
$$

$$
\boxed{
y=\frac{u-1}{u+1},
}
$$

away from the exceptional points where the denominators vanish.

Thus one abstract elliptic curve may admit both:

$$
\boxed{
\text{Montgomery coordinates}
}
$$

and

$$
\boxed{
\text{twisted Edwards coordinates}.
}
$$

Each exposes different computational strengths.

Montgomery form is especially attractive for

$$
x\text{-only scalar multiplication}.
$$

Twisted Edwards form is especially attractive for

$$
\text{full-point addition}.
$$

This is one of the reasons closely related curves appear in different forms in modern protocols.

---

<a id="x-only-limitations"></a>

## 22. What x-only arithmetic loses

The efficiency of x-only arithmetic comes from deliberately forgetting information.

Since

$$
x(P)=x(-P),
$$

the representation cannot distinguish

$$
P
$$

from

$$
-P.
$$

Consequently, the \(x\)-line is not itself the elliptic-curve group.

In particular, we do not have a general operation

$$
x(P),x(Q)
\longrightarrow
x(P+Q)
$$

without additional information.

This is why xADD requires the difference.

Likewise, if an application requires:

* arbitrary full-point addition;
* signatures;
* point serialization including sign information;
* direct manipulation of group elements;

then a full point representation or another model may be more natural.

So Montgomery x-only arithmetic is highly specialized.

Its power comes from matching the computational problem exactly.

For Diffie–Hellman-style scalar multiplication, that specialization is extremely valuable.

---

<a id="companion-implementation"></a>

## 23. Companion implementation

The CryptoCave source collection includes a complete Montgomery-curve implementation:

[`src/montgomery.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/montgomery.py)

Repository path:

```text
experiments/ready-material/elliptic-curves/src/montgomery.py
```

This implementation should be studied together with the mathematical development in this chapter.

In particular, compare the code against the conceptual pipeline:

$$
\boxed{
M_{A,B}
}
$$

$$
\Downarrow
$$

$$
\boxed{
(X:Z)\text{ representation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\operatorname{xDBL}
}
$$

$$
\boxed{
\operatorname{xADD}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Montgomery ladder}
}
$$

$$
\Downarrow
$$

$$
\boxed{
[n]P.
}
$$

When reviewing the implementation, useful questions include:

1. How is the point at infinity represented?
2. Does the implementation distinguish full points from x-only coordinates?
3. Which \(A_{24}\) convention is used?
4. Are inversions avoided inside scalar-multiplication loops?
5. How are exceptional values handled?
6. Does the scalar loop have a regular operation pattern?
7. Are conditional swaps implemented without obvious secret-dependent branches?
8. Are the mathematical assumptions of the code clearly separated from protocol-specific behavior?

The implementation is the executable counterpart of the formulas in this chapter.

---

<a id="bigger-picture"></a>

## 24. The bigger picture

The central progression of Montgomery arithmetic is now visible.

Start with the curve

$$
\boxed{
By^2=x^3+Ax^2+x.
}
$$

Negation satisfies

$$
\boxed{
(x,y)\mapsto(x,-y),
}
$$

so

$$
\boxed{
x(P)=x(-P).
}
$$

Therefore we can pass to

$$
\boxed{
E/\{\pm1\}
\cong
\mathbb P^1.
}
$$

Represent the coordinate projectively:

$$
\boxed{
x=(X:Z).
}
$$

Then derive:

$$
\boxed{
\operatorname{xDBL}:
x(P)\rightarrow x(2P),
}
$$

and

$$
\boxed{
\operatorname{xADD}:
x(P),x(Q),x(P-Q)
\rightarrow
x(P+Q).
}
$$

Now maintain

$$
\boxed{
(R_0,R_1)
=
([k]P,[k+1]P).
}
$$

Since

$$
R_1-R_0=P,
$$

the required difference is always known.

Therefore every scalar bit can use the same conceptual pair of operations:

$$
\boxed{
\operatorname{xDBL}
+
\operatorname{xADD}.
}
$$

This gives the Montgomery ladder.

The full chain is

$$
\boxed{
\text{Montgomery model}
}
$$

$$
\Downarrow
$$

$$
\boxed{
P\sim-P
}
$$

$$
\Downarrow
$$

$$
\boxed{
x\text{-only representation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{projective }(X:Z)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\operatorname{xDBL}/\operatorname{xADD}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Montgomery ladder}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{efficient scalar multiplication}.
}
$$

This is a particularly elegant example of mathematical structure shaping cryptographic engineering.

The efficiency does not come from an unrelated implementation trick.

It comes directly from the symmetry

$$
P\leftrightarrow -P
$$

of the elliptic curve.

That symmetry allows us to discard a coordinate, move to the Kummer line, and perform scalar multiplication using a remarkably small arithmetic interface.

The deeper lesson is therefore:

$$
\boxed{
\text{good cryptographic engineering often begins by choosing the right mathematical representation}.
}
$$

---

## Further reading

Useful references for this chapter include:

* Peter L. Montgomery, **Speeding the Pollard and Elliptic Curve Methods of Factorization**.
* Craig Costello and Benjamin Smith, **Montgomery Curves and Their Arithmetic: The Case of Large Characteristic Fields**.
* Daniel J. Bernstein, **Curve25519: New Diffie-Hellman Speed Records**.
* RFC 7748, **Elliptic Curves for Security**.
* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.

---

The next chapter naturally turns to **Edwards and twisted Edwards curves**.

There the emphasis changes from

$$
\boxed{
x\text{-only differential arithmetic}
}
$$

to

$$
\boxed{
\text{efficient full-point addition}.
}
$$

That will let us compare, in detail:

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
\text{twisted Edwards}.
}
$$

We can then understand mathematically why the same broad curve family can appear through interfaces such as X25519 and Ed25519 while using very different coordinate systems and arithmetic strategies.
