---
title: "Lattices & Lattice-Based Cryptography IV: Gaussian Reduction in Two Dimensions and the Integer NTRU Analogy"
description: "A worked bridge from exact two-dimensional lattice reduction to the central NTRU idea: a small secret satisfies a public modular relation, becomes a short vector in a public lattice, and is recovered in the toy setting by Gaussian reduction."
pubDate: "2022-06-21"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Linear Algebra"
  - "Lattice Theory"
  - "Lattice Methods"
  - "Post-Quantum Cryptography"
tags:
  - "gaussian-reduction"
  - "two-dimensional-lattices"
  - "ntru"
  - "short-vectors"
  - "ross-course"
difficulty: "Intermediate"
status: "Validated"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 4
sourcePath: "experiments/lattices/ross-course"
draft: false
---

The easiest place to see the basic geometry behind lattice cryptography is not a several-hundred-dimensional structured lattice.

It is:

\[
\boxed{
\text{dimension }2.
}
\]

In two dimensions we can:

- draw the lattice;
- inspect the basis;
- execute reduction exactly;
- identify shortest vectors;
- watch a hidden modular relation become visible geometrically.

A recovered set of exercises from an earlier post-quantum cryptography course followed exactly this progression:

\[
\boxed{
\text{2D lattice reduction}
\rightarrow
\text{scalar NTRU-like relation}
\rightarrow
\text{public lattice}
\rightarrow
\text{short secret vector}.
}
\]

The original material was primarily computational.

Here we reconstruct the mathematical argument from first principles.

The goal is **not** to model a production NTRU scheme exactly.

It is to isolate one of the central ideas behind NTRU-style lattice geometry:

\[
\boxed{
\text{a public modular relation can define a lattice containing secret small coefficients}.
}
\]

In dimension two, classical Gaussian—or Gauss–Lagrange—reduction is strong enough to recover that short vector directly.

![From a public two-dimensional lattice to the short NTRU-like secret vector](/images/blog/lattices/gaussian-2d-ntru.svg)

---

## Table of Contents

- [Gaussian reduction in dimension two](#gaussian-reduction-in-dimension-two)
- [A complete two-dimensional reduction example](#a-complete-two-dimensional-reduction-example)
- [104\cdot23](#104cdot23)
- [The scalar NTRU-like toy system](#the-scalar-ntru-like-toy-system)
- [From the public congruence to a lattice](#from-the-public-congruence-to-a-lattice)
- [\[
f
\begin${pmatrix}
1\
h
\end${pmatrix}](#fbeginpmatrix1hendpmatrix)
- [Recovering the secret by Gaussian reduction](#recovering-the-secret-by-gaussian-reduction)
- [From the scalar toy to polynomial NTRU](#from-the-scalar-toy-to-polynomial-ntru)
- [What this experiment actually teaches](#what-this-experiment-actually-teaches)
- [Companion implementation](#companion-implementation)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [\[
f
\begin${pmatrix}
1\
h
\end${pmatrix}](#fbeginpmatrix1hendpmatrix-1)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Gaussian reduction in dimension two

Let:

\[
b_1,b_2\in\mathbb R^2
\]

be linearly independent lattice vectors.

With the column convention used throughout this series, write:

\[
B=
\begin{pmatrix}
|&|\\
b_1&b_2\\
|&|
\end{pmatrix}.
\]

The generated lattice is:

\[
\boxed{
L(B)
=
B\mathbb Z^2
=
\{
z_1b_1+z_2b_2:
z_1,z_2\in\mathbb Z
\}.
}
\]

The basis is not unique.

If:

\[
U\in GL_2(\mathbb Z),
\]

then:

\[
\boxed{
L(BU)=L(B).
}
\]

So lattice reduction is allowed to replace the basis while preserving the lattice exactly.

---

### The two-dimensional reduction step

Assume:

\[
\|b_1\|_2
\le
\|b_2\|_2.
\]

Project \(b_2\) onto the direction of \(b_1\):

\[
\frac{
\langle b_1,b_2\rangle
}{
\langle b_1,b_1\rangle
}.
\]

Choose the nearest integer:

\[
\boxed{
\mu
=
\left\lfloor
\frac{
\langle b_1,b_2\rangle
}{
\|b_1\|_2^2
}
\right\rceil.
}
\]

Then perform:

\[
\boxed{
b_2
\leftarrow
b_2-\mu b_1.
}
\]

Because:

\[
\mu\in\mathbb Z,
\]

this is a unimodular basis operation.

For example, the corresponding right-multiplication matrix is:

\[
U=
\begin{pmatrix}
1&-\mu\\
0&1
\end{pmatrix},
\]

with:

\[
\det U=1.
\]

Therefore:

\[
\boxed{
\text{the lattice does not change}.
}
\]

---

### Why nearest-integer subtraction helps

After the update:

\[
b_2'
=
b_2-\mu b_1,
\]

the new projection coefficient is:

\[
\frac{
\langle b_1,b_2'\rangle
}{
\|b_1\|^2
}
=
\frac{
\langle b_1,b_2\rangle
}{
\|b_1\|^2
}
-\mu.
\]

By nearest-integer rounding:

\[
\boxed{
\left|
\frac{
\langle b_1,b_2'\rangle
}{
\|b_1\|^2
}
\right|
\le
\frac12.
}
\]

Thus the component of \(b_2\) parallel to \(b_1\) has been reduced as much as possible using an integer multiple.

---

### Reduced condition

A standard two-dimensional reduced basis satisfies:

\[
\boxed{
\|b_1\|
\le
\|b_2\|
}
\]

and:

\[
\boxed{
|\langle b_1,b_2\rangle|
\le
\frac12
\|b_1\|^2.
}
\]

Equivalently:

\[
\left|
\frac{
\langle b_1,b_2\rangle
}{
\|b_1\|^2
}
\right|
\le
\frac12.
\]

If the reduction step produces:

\[
\|b_2\|<\|b_1\|,
\]

swap the vectors and continue.

So the algorithm has the Euclidean-algorithm-like structure:

\[
\boxed{
\text{nearest integer subtraction}
\rightarrow
\text{swap}
\rightarrow
\text{repeat}.
}
\]

---

### Why dimension two is special

In two dimensions, this reduction is extremely strong.

For a Gauss-reduced basis:

\[
(b_1,b_2),
\]

the first vector:

\[
\boxed{
b_1
}
\]

is a shortest nonzero lattice vector.

To see the basic reason, consider:

\[
v=mb_1+nb_2.
\]

If:

\[
n=0,
\]

then:

\[
\|v\|
=
|m|\|b_1\|
\ge
\|b_1\|.
\]

If:

\[
n\neq0,
\]

the reduced geometry prevents the second direction from cancelling enough of \(b_1\) to produce a vector shorter than \(b_1\).

Thus in dimension two:

\[
\boxed{
\text{basis reduction and exact shortest-vector geometry are tightly connected}.
}
\]

That property does not scale cleanly to high dimension.

---

### Connection with LLL

The previous article introduced:

\[
\mu_{i,j}
=
\frac{
\langle b_i,b_j^*\rangle
}{
\langle b_j^*,b_j^*\rangle
}.
\]

In dimension two:

\[
b_1^*=b_1,
\]

so:

\[
\mu_{2,1}
=
\frac{
\langle b_2,b_1\rangle
}{
\|b_1\|^2
}.
\]

Gaussian reduction therefore performs precisely the kind of nearest-integer size reduction that appears inside LLL.

This makes Gauss reduction the cleanest low-dimensional precursor to modern lattice reduction.

---

## A complete two-dimensional reduction example

The recovered worksheet example begins with:

\[
\boxed{
b_1=(104,62),
}
\]

and:

\[
\boxed{
b_2=(74,23).
}
\]

Their squared lengths are:

\[
\|b_1\|^2
=
104^2+62^2
=
14660,
\]

and:

\[
\|b_2\|^2
=
74^2+23^2
=
6005.
\]

So first reorder them:

\[
b_1=(74,23),
\]

\[
b_2=(104,62).
\]

---

### First reduction step

Compute:

\[
\langle b_1,b_2\rangle
=
74\cdot104+23\cdot62.
\]

Thus:

\[
\langle b_1,b_2\rangle
=
9122.
\]

Hence:

\[
\mu
=
\left\lfloor
\frac{9122}{6005}
\right\rceil
=
2.
\]

Replace:

\[
b_2
\leftarrow
b_2-2b_1.
\]

Then:

\[
b_2
=
(104,62)-2(74,23).
\]

Therefore:

\[
\boxed{
b_2=(-44,16).
}
\]

Its squared norm is:

\[
(-44)^2+16^2
=
2192.
\]

Since:

\[
2192<6005,
\]

swap again.

Now:

\[
b_1=(-44,16),
\]

\[
b_2=(74,23).
\]

---

### Second reduction step

Compute:

\[
\langle b_1,b_2\rangle
=
(-44)(74)+(16)(23).
\]

So:

\[
\langle b_1,b_2\rangle
=
-2888.
\]

And:

\[
\|b_1\|^2
=
2192.
\]

Therefore:

\[
\mu
=
\left\lfloor
\frac{-2888}{2192}
\right\rceil
=
-1.
\]

Hence:

\[
b_2
\leftarrow
b_2+b_1.
\]

Thus:

\[
\boxed{
b_2=(30,39).
}
\]

Now:

\[
\|b_2\|^2
=
30^2+39^2
=
2421.
\]

The basis has become:

\[
\boxed{
(-44,16),
\qquad
(30,39).
}
\]

---

### Check that the lattice is unchanged

The original determinant is:

\[
\det
\begin{pmatrix}
104&74\\
62&23
\end{pmatrix}
=
104\cdot23
-
74\cdot62.
\]

Therefore:

\[
\det B
=
-2196.
\]

The reduced basis gives:

\[
\det
\begin{pmatrix}
-44&30\\
16&39
\end{pmatrix}
=
(-44)(39)-30(16).
\]

Thus:

\[
\det B'
=
-2196.
\]

So:

\[
\boxed{
|\det B|
=
|\det B'|
=
2196.
}
\]

The geometry changed dramatically.

The lattice did not.

---

### Exact implementation

Because all operations are integral, two-dimensional reduction can be implemented without floating point.

```python
def dot(u, v):
    return sum(
        x * y
        for x, y in zip(u, v)
    )


def norm_sq(v):
    return dot(v, v)


def nearest_quotient(
    numerator: int,
    denominator: int,
) -> int:
    q, r = divmod(
        numerator,
        denominator,
    )

    if 2 * r > denominator:
        return q + 1

    if 2 * r < denominator:
        return q

    # Either nearest integer is valid
    # in the exact half-way case.
    return q + 1


def gauss_reduce(b1, b2):
    b1 = list(b1)
    b2 = list(b2)

    while True:
        if norm_sq(b2) < norm_sq(b1):
            b1, b2 = b2, b1

        mu = nearest_quotient(
            dot(b1, b2),
            norm_sq(b1),
        )

        if mu == 0:
            return b1, b2

        b2 = [
            x - mu * y
            for x, y in zip(
                b2,
                b1,
            )
        ]
```

Running:

```python
gauss_reduce(
    (104, 62),
    (74, 23),
)
```

returns:

```text
([-44, 16], [30, 39])
```

up to harmless choices of sign and ordering.

---

## The scalar NTRU-like toy system

We now construct a deliberately tiny analogue of the modular relation that appears in NTRU-style systems.

This is **not a production cryptosystem**.

It removes the polynomial ring and keeps only the essential scalar relation.

Choose small integers:

\[
f,
\qquad
g,
\]

and a much larger modulus:

\[
q.
\]

Require:

\[
\boxed{
\gcd(f,q)=1.
}
\]

Therefore:

\[
f^{-1}\pmod q
\]

exists.

Publish:

\[
\boxed{
h
\equiv
f^{-1}g
\pmod q.
}
\]

The private information is:

\[
(f,g).
\]

The public information is:

\[
(q,h).
\]

---

### Concrete parameters

Use:

\[
\boxed{
q=122430513841,
}
\]

\[
\boxed{
f=231231,
}
\]

\[
\boxed{
g=195698.
}
\]

Then:

\[
\boxed{
h=39245579300.
}
\]

By construction:

\[
\boxed{
fh\equiv g\pmod q.
}
\]

This means exactly that there exists:

\[
u\in\mathbb Z
\]

such that:

\[
\boxed{
fh=g+uq.
}
\]

For these values:

\[
\boxed{
u=74122.
}
\]

So:

\[
fh
=
g+74122q.
\]

This integer equation will become the lattice embedding.

---

### A toy encryption rule

Let:

\[
m
\]

be a small message and:

\[
r
\]

a small random integer.

Define:

\[
\boxed{
c
=
rh+m
\pmod q.
}
\]

For:

\[
m=123456,
\]

and:

\[
r=101010,
\]

we obtain:

\[
\boxed{
c=18357558717.
}
\]

---

### Why decryption works

Multiply by:

\[
f.
\]

Then:

\[
fc
\equiv
frh+fm
\pmod q.
\]

Because:

\[
fh\equiv g\pmod q,
\]

we get:

\[
\boxed{
fc
\equiv
rg+fm
\pmod q.
}
\]

For the concrete parameters:

\[
rg+fm
=
48314309316.
\]

And:

\[
\frac q2
=
61215256920.5.
\]

Therefore:

\[
\boxed{
|rg+fm|
<
\frac q2.
}
\]

So if the residue \(fc\bmod q\) is interpreted using the centered interval:

\[
\left(
-\frac q2,
\frac q2
\right],
\]

there is no modular wrap-around ambiguity.

The integer value recovered is exactly:

\[
\boxed{
rg+fm.
}
\]

---

### Remove the random term

Reduce this integer modulo:

\[
g.
\]

Since:

\[
rg
\equiv0
\pmod g,
\]

we obtain:

\[
rg+fm
\equiv
fm
\pmod g.
\]

Now:

\[
\gcd(f,g)=1,
\]

so:

\[
f^{-1}\pmod g
\]

exists.

Therefore:

\[
\boxed{
m
\equiv
f^{-1}(rg+fm)
\pmod g.
}
\]

For our parameters:

\[
f^{-1}
\equiv
193495
\pmod g.
\]

The computation returns:

\[
\boxed{
m\equiv123456\pmod{195698}.
}
\]

Because the message was chosen in the representative range:

\[
0\le m<g,
\]

we recover the actual integer:

\[
\boxed{
m=123456.
}
\]

---

### The two correctness conditions

The toy construction therefore relies on two separate conditions.

First, **no wrap-around**:

\[
\boxed{
|rg+fm|
<
\frac q2
}
\]

when centered representatives are used.

Second, **unique message representation**:

\[
\boxed{
0\le m<g.
}
\]

Without the first, reduction modulo \(q\) loses the desired integer value.

Without the second, the final computation determines only:

\[
m\bmod g.
\]

This is already a useful preview of real lattice cryptography:

\[
\boxed{
\text{correctness depends on controlling the size of an error-like quantity}.
}
\]

---

## From the public congruence to a lattice

The attacker knows:

\[
q
\]

and:

\[
h.
\]

Consider the two public vectors:

\[
\boxed{
b_1=
\begin{pmatrix}
1\\
h
\end{pmatrix},
}
\]

and:

\[
\boxed{
b_2=
\begin{pmatrix}
0\\
q
\end{pmatrix}.
}
\]

Their basis matrix is:

\[
\boxed{
B=
\begin{pmatrix}
1&0\\
h&q
\end{pmatrix}.
}
\]

The corresponding public lattice is:

\[
\boxed{
L_h
=
L(B).
}
\]

Every vector has the form:

\[
a
\begin{pmatrix}
1\\
h
\end{pmatrix}
+
b
\begin{pmatrix}
0\\
q
\end{pmatrix}
=
\begin{pmatrix}
a\\
ah+bq
\end{pmatrix}
\]

for:

\[
a,b\in\mathbb Z.
\]

Thus:

\[
\boxed{
L_h
=
\left\{
(a,b'):
b'\equiv ah\pmod q
\right\}.
}
\]

The lattice is simply the integer solution set of the public modular relation:

\[
\boxed{
y\equiv hx\pmod q.
}
\]

---

### Why the secret belongs to the lattice

Recall:

\[
fh=g+uq.
\]

Then:

\[
g
=
fh-uq.
\]

So choose:

\[
a=f,
\]

and:

\[
b=-u.
\]

We obtain:

\[
f
\begin{pmatrix}
1\\
h
\end{pmatrix}
-
u
\begin{pmatrix}
0\\
q
\end{pmatrix}
=
\begin{pmatrix}
f\\
fh-uq
\end{pmatrix}.
\]

Therefore:

\[
\boxed{
\begin{pmatrix}
f\\
g
\end{pmatrix}
\in
L_h.
}
\]

This is the key geometric transformation:

\[
\boxed{
fh\equiv g\pmod q
}
\]

becomes:

\[
\boxed{
(f,g)\in L_h.
}
\]

A modular relation has become lattice membership.

---

### The determinant of the public lattice

The public basis is triangular:

\[
B=
\begin{pmatrix}
1&0\\
h&q
\end{pmatrix}.
\]

Therefore:

\[
\boxed{
\det(L_h)
=
|\det B|
=
q.
}
\]

For this example:

\[
\boxed{
\det(L_h)
=
122430513841.
}
\]

The natural two-dimensional length scale is therefore roughly:

\[
\sqrt q.
\]

Numerically:

\[
\boxed{
\sqrt q
\approx349900.72.
}
\]

---

### How short is the secret?

The secret vector has norm:

\[
\|(f,g)\|_2
=
\sqrt{
f^2+g^2
}.
\]

Numerically:

\[
\boxed{
\|(f,g)\|_2
\approx302928.18.
}
\]

So:

\[
\frac{
\|(f,g)\|
}{
\sqrt q
}
\approx
0.866.
\]

This observation is important.

The secret is **enormously shorter than the supplied public basis vectors**:

\[
(1,h),
\qquad
(0,q),
\]

whose coordinates are of order:

\[
10^{10}
\quad\text{to}\quad
10^{11}.
\]

But intrinsically, the secret lies on the natural:

\[
\sqrt q
\]

scale expected for a two-dimensional lattice of determinant \(q\).

So the correct lesson is not merely:

> the secret is microscopically small compared with everything in the lattice.

Rather:

\[
\boxed{
\text{the public basis is extremely poor, while the lattice itself contains much shorter vectors}.
}
\]

And in dimension two, Gaussian reduction can expose them essentially exactly.

---

## Recovering the secret by Gaussian reduction

The attacker begins only with:

\[
q=122430513841
\]

and:

\[
h=39245579300.
\]

Construct the public basis:

\[
\boxed{
b_1=
(1,39245579300),
}
\]

\[
\boxed{
b_2=
(0,122430513841).
}
\]

No knowledge of \(f\) or \(g\) is used in this construction.

Now run exact Gaussian reduction.

The resulting reduced basis is:

\[
\boxed{
(-231231,-195698),
}
\]

and:

\[
\boxed{
(-368222,217835).
}
\]

The first vector is:

\[
\boxed{
-(f,g).
}
\]

Therefore:

\[
\boxed{
f=231231,
\qquad
g=195698
}
\]

are recovered up to the irrelevant global sign.

---

### Why sign does not matter

If:

\[
v\in L,
\]

then:

\[
-v\in L.
\]

Moreover:

\[
\|v\|=\|-v\|.
\]

Shortest-vector problems therefore naturally return:

\[
\pm v
\]

as equivalent geometric solutions.

In the toy system:

\[
(-f,-g)
\]

contains exactly the same secret relation as:

\[
(f,g).
\]

---

### The second reduced vector

The second reduced vector is:

\[
(-368222,217835).
\]

Its norm is larger than that of the recovered secret.

Because the final basis is Gauss reduced, the first vector represents an exact shortest-vector direction for this two-dimensional lattice.

Thus the recovery is not simply a lucky basis simplification.

It reflects the actual two-dimensional shortest-vector geometry.

---

### Determinant check

The public lattice determinant is:

\[
q.
\]

The reduced basis must therefore satisfy:

\[
\left|
\det
\begin{pmatrix}
-231231&-368222\\
-195698&217835
\end{pmatrix}
\right|
=
122430513841.
\]

This provides an immediate invariant check:

\[
\boxed{
\det(L_{\mathrm{before}})
=
\det(L_{\mathrm{after}}).
}
\]

The basis changed dramatically.

The lattice did not.

---

### Reproducible output

The companion implementation gives:

```text
integer-NTRU public h: 39245579300
recovered message: 123456

reduced public basis:
[[-231231, -195698], [-368222, 217835]]

PASS: Gaussian reduction exposes the short secret vector in the 2D toy.
```

The exact ordering or signs of the reduced vectors can depend on tie-breaking and basis conventions.

The invariant result is the same lattice and the same shortest-vector geometry.

---

## From the scalar toy to polynomial NTRU

The scalar experiment keeps only one coefficient.

Real NTRU-style constructions replace the integer arithmetic with arithmetic in a polynomial quotient ring.

A classical model uses:

\[
\boxed{
R
=
\mathbb Z[x]/(x^N-1),
}
\]

or a related quotient depending on the construction.

The private quantities become short polynomials:

\[
f(x),
\qquad
g(x).
\]

A core public relation has the form:

\[
\boxed{
h
\equiv
f^{-1}g
\pmod q
}
\]

inside the quotient ring, under one common normalization.

Equivalently:

\[
\boxed{
fh
\equiv
g
\pmod q.
}
\]

Some NTRU variants include additional small multipliers or use different public-key normalizations, so this equation should be understood as the structural relation needed for the lattice analogy rather than a universal specification of every NTRU scheme.

---

### Coefficient vectors

Write:

\[
f(x)
=
f_0+f_1x+\cdots+f_{N-1}x^{N-1}.
\]

Associate the vector:

\[
\boxed{
\mathbf f
=
(f_0,\ldots,f_{N-1})^T.
}
\]

Do the same for:

\[
g
\]

and:

\[
h.
\]

Multiplication by \(h\) modulo:

\[
x^N-1
\]

becomes a linear transformation represented by a circulant matrix:

\[
\boxed{
H.
}
\]

Thus:

\[
fh\equiv g\pmod q
\]

becomes:

\[
\boxed{
H\mathbf f
\equiv
\mathbf g
\pmod q.
}
\]

---

### The NTRU-style lattice

Define:

\[
\boxed{
L_h
=
\left\{
\begin{pmatrix}
\mathbf a\\
\mathbf b
\end{pmatrix}
\in
\mathbb Z^{2N}
:
\mathbf b
\equiv
H\mathbf a
\pmod q
\right\}.
}
\]

One column-basis representation is:

\[
\boxed{
B_h
=
\begin{pmatrix}
I_N&0\\
H&qI_N
\end{pmatrix}.
}
\]

Indeed, multiplying by:

\[
\begin{pmatrix}
\mathbf a\\
\mathbf z
\end{pmatrix}
\in
\mathbb Z^{2N}
\]

gives:

\[
\begin{pmatrix}
\mathbf a\\
H\mathbf a+q\mathbf z
\end{pmatrix}.
\]

Because:

\[
H\mathbf f
\equiv
\mathbf g
\pmod q,
\]

there exists:

\[
\mathbf u\in\mathbb Z^N
\]

such that:

\[
H\mathbf f
=
\mathbf g+q\mathbf u.
\]

Choosing:

\[
\mathbf z=-\mathbf u
\]

gives:

\[
\boxed{
\begin{pmatrix}
\mathbf f\\
\mathbf g
\end{pmatrix}
\in
L_h.
}
\]

This is the high-dimensional version of the scalar identity:

\[
\boxed{
(f,g)\in L_h.
}
\]

---

### Dimension and determinant

The scalar toy has:

\[
\boxed{
\dim L=2.
}
\]

The polynomial construction has dimension:

\[
\boxed{
2N.
}
\]

For the displayed block basis:

\[
B_h=
\begin{pmatrix}
I_N&0\\
H&qI_N
\end{pmatrix},
\]

we have:

\[
\boxed{
\det(L_h)=q^N.
}
\]

So the move from the toy to NTRU is not simply:

\[
\text{bigger integers}.
\]

It is:

\[
\boxed{
2
\longrightarrow
2N
}
\]

dimensions together with strong algebraic structure.

That is the decisive computational change.

---

### Why Gaussian reduction no longer applies

In dimension two, Gauss reduction gives exceptionally strong results.

For dimension:

\[
2N,
\]

there is no direct analogue with the same efficiency and exactness.

We instead rely on algorithms such as:

\[
\boxed{
\text{LLL}
}
\]

and:

\[
\boxed{
\text{BKZ}.
}
\]

These return reduced bases or short vectors with approximation behavior rather than solving arbitrary high-dimensional SVP exactly in polynomial time.

So:

\[
\boxed{
\text{same structural idea}
\neq
\text{same computational difficulty}.
}
\]

That distinction is the entire reason the toy example is educational rather than a break of modern NTRU.

---

## What this experiment actually teaches

The example contains several ideas that will reappear throughout lattice-based cryptography.

---

### Public equations can define lattices

We began with:

\[
\boxed{
fh\equiv g\pmod q.
}
\]

That became:

\[
\boxed{
(f,g)\in L_h.
}
\]

This pattern is extremely general:

\[
\boxed{
\text{modular linear relation}
\rightarrow
\text{lattice membership}.
}
\]

Later, SIS will use exactly this kind of transition.

---

### Small secrets become short vectors

The secret coefficients are deliberately sampled from a small range.

Therefore:

\[
(f,g)
\]

has relatively small Euclidean norm.

In polynomial NTRU, coefficient vectors:

\[
(\mathbf f,\mathbf g)
\]

play the analogous role.

So:

\[
\boxed{
\text{small coefficients}
\rightarrow
\text{short Euclidean vector}.
}
\]

---

### The public basis can hide the geometry

The public basis:

\[
(1,h),
\qquad
(0,q)
\]

is extremely long and skewed.

Nothing about its visible vector lengths immediately reveals:

\[
(f,g).
\]

Yet both bases describe the same lattice.

This is precisely why basis reduction matters:

\[
\boxed{
\text{bad basis}
\rightarrow
\text{same lattice}
\rightarrow
\text{better basis}.
}
\]

---

### Dimension is a security parameter

The toy lattice has dimension:

\[
2.
\]

Gaussian reduction can solve its reduction problem essentially exactly and extremely efficiently.

Real NTRU-style lattices have dimensions on the order of:

\[
2N.
\]

The security question is therefore not:

> Are the public integers large?

The important questions include:

- What is the lattice dimension?
- What is its determinant?
- How short is the secret relative to the lattice scale?
- What algebraic structure is present?
- What reduction quality is required?
- What is the cost of obtaining that reduction?

So:

\[
\boxed{
\text{large numbers alone do not create lattice hardness}.
}
\]

---

### Lattice construction is part of the cryptanalysis

Gaussian reduction only works because we first recognized the correct public lattice:

\[
L_h
=
\langle
(1,h),
(0,q)
\rangle.
\]

This is the same lesson seen in Coppersmith and Hidden Number Problem attacks.

A reduction algorithm is not a magic cryptanalytic black box.

The full process is:

\[
\boxed{
\text{identify algebraic relation}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{construct lattice}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{identify target geometry}
}
\]

\[
\downarrow
\]

\[
\boxed{
\text{apply reduction}.
}
\]

The first three steps often contain most of the mathematical insight.

---

## Companion implementation

The cleaned implementation is located at:

```text
experiments/lattices/ross-course/gaussian_integer_ntru.py
```

It contains:

- exact nearest-integer two-dimensional reduction;
- the original:
  \[
  (104,62),(74,23)
  \]
  reduction example;
- the scalar NTRU-like toy;
- encryption and decryption;
- explicit no-wrap correctness checks;
- construction of the public lattice;
- recovery of:
  \[
  \pm(f,g);
  \]
- determinant preservation checks.

Because the implementation uses exact integer arithmetic, the experiment does not depend on floating-point approximations.

---

## The structural picture

Two-dimensional reduction starts with:

\[
\boxed{
L(B)=B\mathbb Z^2.
}
\]

A nearest-integer operation:

\[
\boxed{
b_2
\leftarrow
b_2-
\left\lfloor
\frac{
\langle b_1,b_2\rangle
}{
\|b_1\|^2
}
\right\rceil
b_1
}
\]

preserves the lattice while improving its visible geometry.

In the toy NTRU-like system:

\[
\boxed{
h
\equiv
f^{-1}g
\pmod q.
}
\]

Therefore:

\[
\boxed{
fh\equiv g\pmod q.
}
\]

That public congruence defines:

\[
\boxed{
L_h
=
\left\{
(a,b):
b\equiv ah\pmod q
\right\}.
}
\]

The secret satisfies:

\[
\boxed{
(f,g)\in L_h.
}
\]

The public basis is:

\[
\boxed{
\begin{pmatrix}
1\\
h
\end{pmatrix},
\quad
\begin{pmatrix}
0\\
q
\end{pmatrix}.
}
\]

Its determinant is:

\[
\boxed{
q.
}
\]

Gaussian reduction reveals:

\[
\boxed{
\pm(f,g).
}
\]

The polynomial analogue replaces scalars by coefficient vectors:

\[
\boxed{
H\mathbf f
\equiv
\mathbf g
\pmod q,
}
\]

and produces a structured lattice in dimension:

\[
\boxed{
2N.
}
\]

So the complete conceptual bridge is:

\[
\boxed{
\text{public modular equation}
\rightarrow
\text{public lattice}
\rightarrow
\text{short secret vector}
\rightarrow
\text{basis reduction}.
}
\]

That is one of the central geometric ideas behind NTRU.

---

## Practice and checkpoint

### Exercise 1 — Unimodular reduction step

Show that:

\[
b_2
\leftarrow
b_2-\mu b_1,
\qquad
\mu\in\mathbb Z,
\]

corresponds to multiplication by a matrix in:

\[
GL_2(\mathbb Z).
\]

Why does this preserve the lattice?

---

### Exercise 2 — Worksheet reduction

Starting with:

\[
b_1=(104,62),
\qquad
b_2=(74,23),
\]

perform the Gaussian reduction steps by hand.

Verify the reduced basis:

\[
(-44,16),
\qquad
(30,39)
\]

up to signs and ordering.

---

### Exercise 3 — Determinant invariant

Compute the determinant of both the original and reduced bases from Exercise 2.

Verify:

\[
|\det B|
=
2196.
\]

---

### Exercise 4 — Public key relation

Using:

\[
q=122430513841,
\]

\[
f=231231,
\]

\[
g=195698,
\]

verify:

\[
h
=
f^{-1}g
\bmod q
=
39245579300.
\]

---

### Exercise 5 — Integer lifting

Compute:

\[
u
=
\frac{
fh-g
}{
q
}.
\]

Verify:

\[
\boxed{
u=74122.
}
\]

---

### Exercise 6 — Public lattice membership

Show explicitly that:

\[
f
\begin{pmatrix}
1\\
h
\end{pmatrix}
-
u
\begin{pmatrix}
0\\
q
\end{pmatrix}
=
\begin{pmatrix}
f\\
g
\end{pmatrix}.
\]

---

### Exercise 7 — Toy correctness

For:

\[
m=123456,
\qquad
r=101010,
\]

compute:

\[
c=rh+m\pmod q.
\]

Then verify:

\[
fc\bmod q
=
rg+fm.
\]

Why does this equality hold as an integer rather than merely modulo \(q\) for these parameters?

---

### Exercise 8 — Final message recovery

Verify:

\[
\gcd(f,g)=1.
\]

Find:

\[
f^{-1}\pmod g.
\]

Recover:

\[
m
\]

from:

\[
rg+fm.
\]

---

### Exercise 9 — Lattice scale

Compute:

\[
\sqrt q
\]

and:

\[
\sqrt{f^2+g^2}.
\]

Compare the two quantities.

Why is this more informative than merely comparing \(f\) and \(g\) with \(q\)?

---

### Exercise 10 — Reduced public basis

Run Gaussian reduction on:

\[
(1,h),
\qquad
(0,q).
\]

Verify that one result is:

\[
-(f,g).
\]

---

### Exercise 11 — Polynomial lift

Suppose:

\[
H\mathbf f
\equiv
\mathbf g
\pmod q.
\]

Show that:

\[
\begin{pmatrix}
\mathbf f\\
\mathbf g
\end{pmatrix}
\]

belongs to the lattice generated by:

\[
\begin{pmatrix}
I&0\\
H&qI
\end{pmatrix}.
\]

---

### Exercise 12 — Dimension

If:

\[
f,g\in
\mathbb Z[x]/(x^{N}-1)
\]

have \(N\) coefficients each, explain why the corresponding basic NTRU lattice lives in dimension:

\[
2N.
\]

Why is the jump from:

\[
2
\]

to:

\[
2N
\]

cryptographically significant?

---

### Reader checkpoint

You should now be able to explain:

1. What Gaussian or Gauss–Lagrange lattice reduction does in dimension two.
2. Why nearest-integer subtraction preserves the lattice.
3. Why swapping basis vectors also preserves the lattice.
4. What conditions characterize a two-dimensional reduced basis.
5. Why the first vector of a Gauss-reduced basis is a shortest vector.
6. How two-dimensional reduction relates to the Euclidean algorithm.
7. How it anticipates LLL size reduction.
8. Why:
   \[
   h=f^{-1}g\pmod q
   \]
   implies:
   \[
   fh=g+uq.
   \]
9. What correctness conditions the scalar encryption toy requires.
10. Why:
    \[
    |rg+fm|<q/2
    \]
    prevents centered modular wrap-around.
11. Why recovering:
    \[
    m\bmod g
    \]
    requires a message-range convention to recover \(m\) uniquely.
12. How:
    \[
    fh\equiv g\pmod q
    \]
    defines a public lattice.
13. Why:
    \[
    (f,g)
    \]
    belongs to that lattice.
14. Why the public lattice has determinant:
    \[
    q.
    \]
15. Why:
    \[
    \sqrt q
    \]
    is a natural two-dimensional length scale.
16. Why comparing the secret norm with the lattice determinant scale is more meaningful than merely comparing coefficients with \(q\).
17. Why Gaussian reduction recovers the toy secret.
18. Why this does not imply an efficient attack on high-dimensional NTRU.
19. How scalar multiplication becomes circulant polynomial multiplication.
20. Why polynomial NTRU produces a structured lattice of dimension roughly:
    \[
    2N.
    \]
21. Why LLL/BKZ replace Gaussian reduction in higher-dimensional experiments.
22. Why recognizing the correct lattice embedding is part of the cryptanalytic work.

The central lesson is:

\[
\boxed{
\text{small algebraic secrets can become short geometric vectors}.
}
\]

But whether those vectors can be recovered efficiently depends critically on:

\[
\boxed{
\text{dimension},
\quad
\text{determinant},
\quad
\text{structure},
\quad
\text{reduction cost}.
}
\]

---

## References and further reading

**Jeffrey Hoffstein, Jill Pipher, and Joseph H. Silverman**,  
*NTRU: A Ring-Based Public Key Cryptosystem.*

The foundational source for the NTRU construction and the polynomial arithmetic behind its lattice interpretation.

**Daniele Micciancio and Shafi Goldwasser**,  
*Complexity of Lattice Problems: A Cryptographic Perspective.*

A foundational reference for lattice geometry, basis reduction, shortest vectors, and cryptographic applications.

**Phong Q. Nguyen and Brigitte Vallée, editors**,  
*The LLL Algorithm: Survey and Applications.*

A broad reference for lattice reduction, including low-dimensional reduction and its progression toward LLL and stronger algorithms.

**Jeffrey Hoffstein, Jill Pipher, and Joseph H. Silverman**,  
*An Introduction to Mathematical Cryptography.*

Provides an accessible route into lattices, NTRU-style constructions, and their algebraic foundations.

**Phong Q. Nguyen and Jacques Stern**,  
*The Two Faces of Lattices in Cryptology.*

A useful conceptual reference for both constructive and cryptanalytic roles of lattices in cryptography.

---

## Next

This article used the smallest possible setting:

\[
\boxed{
\mathbb Z^2.
}
\]

The next step is to move from one modular relation:

\[
fh\equiv g\pmod q
\]

to systems of modular linear relations.

Given:

\[
A\in\mathbb Z_q^{m\times n},
\]

we will study lattices defined by conditions such as:

\[
\boxed{
Ax\equiv0\pmod q.
}
\]

These are **\(q\)-ary lattices**.

Inside them appears one of the foundational problems of lattice-based cryptography:

\[
\boxed{
\text{find a short nonzero }x
\text{ such that }
Ax\equiv0\pmod q.
}
\]

That is the **Short Integer Solution problem (SIS)**.

So the next article is:

**Lattices & Lattice-Based Cryptography V: q-Ary Lattices, SIS, and Ajtai's Short Relations.**
