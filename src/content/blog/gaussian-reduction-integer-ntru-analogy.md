---
title: "Lattices & Lattice-Based Cryptography IV: Gaussian Reduction in Two Dimensions and the Integer NTRU Analogy"
description: "A worked bridge from exact two-dimensional lattice reduction to the central NTRU idea: a small secret becomes a short vector in a public lattice, and Gaussian reduction recovers it in the toy setting."
pubDate: "2022-06-21"
updatedDate: "2026-09-14"
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
The easiest place to understand lattice cryptography is not a 700-dimensional Module-LWE instance. It is a two-dimensional lattice where we can see every vector and execute the reduction algorithm by hand.

A recovered set of worksheets from a 2022 post-quantum cryptography course contained exactly this progression:

1. reduce a two-dimensional lattice with the classical Gaussian algorithm;
2. study a one-dimensional analogue of NTRU;
3. notice that the secret key is an unusually short public-lattice vector;
4. recover it using the same reduction idea.

That is an excellent conceptual bridge to NTRU and LWE, but the original worksheets were mostly executable fragments. This article rebuilds the argument from first principles and makes the hidden geometry explicit.

![From a public two-dimensional lattice to the short NTRU-like secret vector](/images/blog/lattices/gaussian-2d-ntru.svg)

## 1. A lattice in dimension two

Given linearly independent vectors

$$
b_1,b_2\in\mathbb Z^2,
$$

the lattice they generate is

$$
\mathcal L(b_1,b_2)
=
\{z_1b_1+z_2b_2:z_1,z_2\in\mathbb Z\}.
$$

The basis is not unique. If $U\in\mathrm{GL}_2(\mathbb Z)$ has determinant $\pm1$, then

$$
B'=UB
$$

generates the same lattice.

This is the central freedom exploited by lattice reduction: replace a bad, long, nearly parallel basis by a shorter and more orthogonal basis **without changing the lattice**.

## 2. Gaussian reduction

In dimension two there is a particularly clean reduction procedure.

Let $b_1,b_2$ be a basis. Reorder so that

$$
\|b_1\|\le \|b_2\|.
$$

Compute

$$
\mu
=
\left\lfloor
\frac{\langle b_1,b_2\rangle}{\langle b_1,b_1\rangle}
\right\rceil,
$$

where $\lfloor\cdot\rceil$ denotes nearest-integer rounding, and replace

$$
b_2\leftarrow b_2-\mu b_1.
$$

Repeat until $\mu=0$ after the length ordering.

The step is an integer unimodular basis transformation, so the lattice never changes.

### The recovered worksheet example

The original small example starts with

$$
b_1=(104,62),
\qquad
b_2=(74,23).
$$

Our cleaned companion implementation reduces this to

$$
(-44,16),
\qquad
(30,39).
$$

The exact signs or ordering are unimportant: lattice bases are non-unique. The important fact is that reduction replaced two fairly long vectors by a much shorter basis for the same lattice.

In dimension two, Gaussian reduction is strong enough to expose the shortest-vector geometry almost completely. In high dimensions we need algorithms such as LLL or BKZ and must accept approximation guarantees rather than this very clean picture.

## 3. A one-dimensional NTRU analogy

Now consider a deliberately tiny algebraic cryptosystem over integers modulo $q$.

Choose small secret integers $f$ and $g$ such that

$$
\gcd(f,q)=1.
$$

Publish

$$
\boxed{h=f^{-1}g\pmod q}.
$$

For the recovered course example:

$$
q=122430513841,
$$

$$
f=231231,
\qquad
g=195698,
$$

and therefore

$$
h=39245579300.
$$

The public relation is

$$
fh\equiv g\pmod q.
$$

Equivalently, for some integer $u$,

$$
fh=g+uq.
$$

That innocent congruence is already a lattice relation.

## 4. Toy encryption and decryption

Let the message be a small integer $m$ and choose a small random integer $r$.

Encrypt as

$$
\boxed{c=rh+m\pmod q}.
$$

In the worksheet:

$$
m=123456,
\qquad
r=101010.
$$

The ciphertext becomes

$$
c=18357558717.
$$

Multiply by the secret $f$:

$$
fc
\equiv
frh+fm
\equiv
rg+fm
\pmod q.
$$

The **correctness condition** that the short worksheet leaves implicit is important. The quantity

$$
rg+fm
$$

must remain small enough that the modular reduction modulo $q$ can be interpreted unambiguously as its intended integer representative. This is the same kind of "no wrap-around" or noise-bound condition that repeatedly appears in lattice encryption.

Once we have the intended value, reduce modulo $g$:

$$
fc\equiv fm\pmod g.
$$

If $f$ is also invertible modulo $g$, then

$$
\boxed{m\equiv f^{-1}(fc)\pmod g}.
$$

For the toy values the recovered message is exactly

$$
123456.
$$

## 5. Where is the lattice?

The attacker knows only $q$ and $h$.

Construct the public lattice

$$
\mathcal L
=
\left\langle
(1,h),(0,q)
\right\rangle.
$$

Any vector has the form

$$
a(1,h)+b(0,q)
=
(a,ah+bq).
$$

Because

$$
fh=g+uq,
$$

choose

$$
a=f,
\qquad
b=-u.
$$

Then

$$
f(1,h)-u(0,q)
=
(f,g).
$$

So

$$
\boxed{(f,g)\in\mathcal L}.
$$

This is the conceptual heart of NTRU-style cryptanalysis:

> the public key defines a lattice that contains the private key as a specially short vector.

The public basis vectors contain coordinates on the order of $q$, while $f$ and $g$ are only a few hundred thousand. The secret therefore sticks out geometrically.

## 6. Gaussian reduction recovers the secret

Start from the entirely public basis

$$
b_1=(1,39245579300),
$$

$$
b_2=(0,122430513841).
$$

Running exact two-dimensional Gaussian reduction produces

$$
(-231231,-195698)
$$

as one of the reduced basis vectors.

That is simply

$$
-(f,g).
$$

The sign is irrelevant, so the private key has been recovered.

Our clean-room companion program reproduces this result deterministically:

```text
integer-NTRU public h: 39245579300
recovered message: 123456
reduced public basis:
[[-231231, -195698], [-368222, 217835]]
PASS: Gaussian reduction exposes the short secret vector in the 2D toy.
```

## 7. Why this is not "breaking modern NTRU"

The demonstration is intentionally vulnerable.

Real NTRU replaces the integer relation with polynomial arithmetic in a quotient ring such as

$$
R=\mathbb Z[x]/(x^N-1)
$$

or a related ring, depending on the construction.

The secret becomes a pair of short polynomials

$$
(f,g),
$$

which corresponds to a short vector in a structured lattice of dimension approximately

$$
2N.
$$

The move from dimension $2$ to hundreds or thousands of dimensions is not cosmetic. It completely changes the attack cost.

Gaussian reduction solves the tiny two-dimensional case extremely well. High-dimensional lattice reduction is much more expensive and only approximate.

## 8. The exact analogy with NTRU

The toy uses

$$
h=f^{-1}g\pmod q.
$$

Polynomial NTRU uses the analogous relation

$$
h=f_q^{-1}g\pmod{(q,x^N-1)}
$$

under one common convention.

Thus

$$
fh\equiv g
\pmod{(q,x^N-1)}.
$$

The algebra is the same idea, but scalar multiplication becomes cyclic polynomial multiplication.

That relation becomes a block lattice involving a circulant matrix generated by $h$. The next NTRU attack lab will construct that lattice explicitly.

## 9. Security lesson

This simple example captures an unusually large fraction of lattice cryptography intuition:

1. a public algebraic relation defines a lattice;
2. the secret satisfies the relation;
3. secret coefficients are sampled to be small;
4. therefore the secret is a short lattice vector;
5. reduction algorithms try to expose unusually short vectors;
6. security comes from choosing dimensions and distributions where this search is computationally hard.

This is also why parameter selection cannot be separated from the underlying geometry.

A cryptosystem does not become secure merely because its equations use huge integers. What matters is the geometry of the public lattice and how distinguishable the secret vector is inside it.

## 10. Companion implementation

The cleaned implementation is in:

```text
experiments/lattices/ross-course/gaussian_integer_ntru.py
```

It contains:

- exact nearest-integer Gaussian reduction;
- the original $(104,62),(74,23)$ basis example;
- the integer NTRU-like encryption/decryption toy;
- reconstruction of the public lattice;
- automatic recovery of $\pm(f,g)$.

It is intentionally dependency-free so the geometry can be studied without SageMath.

## What to read next

The next lattice articles move back into higher dimensions:

- q-ary lattices and SIS;
- LWE;
- Ring/Module-LWE;
- polynomial NTRU;
- a complete toy NTRU/LLL recovery experiment.

The lesson to carry forward is simple:

> **NTRU is easiest to understand once you have seen the secret key physically emerge as a short vector from a public lattice.**
