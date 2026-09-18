---
title: "Lattices & Lattice-Based Cryptography IX: Breaking Toy NTRU with LLL — From Public Key to a Short Secret Vector"
description: "A complete worked N=7 NTRU lattice attack: construct the public circulant matrix, prove that the secret lies in the lattice, run LLL, and recover an equivalent private key."
pubDate: "2022-06-21"
updatedDate: "2026-09-16"

topics:
  - "Lattice Theory"
  - "Lattice Methods"
  - "Post-Quantum Cryptography"
  - "Cryptanalysis"
  - "Public-Key Cryptography"

tags:
  - "ntru"
  - "lll"
  - "ntru-lattice"
  - "circulant-matrix"
  - "short-vector"
  - "ross-course"

difficulty: "Advanced"
status: "Validated"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 9
sourcePath: "experiments/lattices/ross-course"
draft: false
---

The previous NTRU chapter explained why an NTRU private key can be interpreted as a short vector inside a public structured lattice.

This chapter does not stop at that statement.

We work through a complete deliberately tiny instance:

$$
N=7,
\qquad
p=3,
\qquad
q=41,
$$

construct the public NTRU lattice explicitly, prove that the secret vector belongs to it, apply LLL, and recover an equivalent private key.

The point is not that LLL “breaks NTRU.”

It does not break properly parameterized modern NTRU systems.

The point is to make the geometry of a lattice attack completely visible:

$$
\boxed{
\text{public algebraic relation}
\rightarrow
\text{integer lattice}
\rightarrow
\text{unusually short secret vector}
\rightarrow
\text{lattice reduction}
\rightarrow
\text{equivalent secret}.
}
$$

The recovered course notebooks are especially valuable because they preserve this entire progression, while leaving several of the mathematical reasons implicit.

Here we fill in those gaps.

![Toy NTRU lattice construction and LLL recovery](/images/blog/lattices/ntru-lll-attack.svg)

---

## Contents

- [1. Toy parameters](#1-toy-parameters)
- [2. The private polynomials](#2-the-private-polynomials)
- [3. Constructing the public key](#3-constructing-the-public-key)
- [4. Lifting the modular relation to the integers](#4-lifting-the-modular-relation-to-the-integers)
- [5. Multiplication by (h) as a circulant matrix](#5-multiplication-by-h-as-a-circulant-matrix)
- [6. Constructing the public NTRU lattice](#6-constructing-the-public-ntru-lattice)
- [7. Proving that the private key lies in the lattice](#7-proving-that-the-private-key-lies-in-the-lattice)
- [8. Why the secret is unusually short](#8-why-the-secret-is-unusually-short)
- [9. What LLL actually does](#9-what-lll-actually-does)
- [10. Running LLL on the toy lattice](#10-running-lll-on-the-toy-lattice)
- [11. Recovering an equivalent private key](#11-recovering-an-equivalent-private-key)
- [12. Why equivalent keys are sufficient](#12-why-equivalent-keys-are-sufficient)
- [13. What the attack has actually accomplished](#13-what-the-attack-has-actually-accomplished)
- [14. Scaling from toys to real cryptanalysis](#14-scaling-from-toys-to-real-cryptanalysis)
- [15. Convention pitfalls](#15-convention-pitfalls)
- [16. The general lattice-attack pattern](#16-the-general-lattice-attack-pattern)
- [17. Companion implementation](#17-companion-implementation)
- [18. Final lesson](#18-final-lesson)

---

## 1. Toy parameters

We work with

$$
N=7,
\qquad
p=3,
\qquad
q=41.
$$

The polynomial ring is

$$
R=\mathbb Z[x]/(x^7-1).
$$

Therefore

$$
x^7=1.
$$

Every polynomial can be represented by exactly seven coefficients:

$$
a(x)
=
a_0+a_1x+\cdots+a_6x^6.
$$

We identify this polynomial with the coefficient vector

$$
(a_0,a_1,\ldots,a_6).
$$

Throughout this chapter, coefficients are ordered from the constant coefficient upward.

This convention matters.

For example,

$$
x^6-x^4+x^3+x^2-1
$$

corresponds to

$$
(-1,0,1,1,-1,0,1),
$$

not the reverse ordering.

---

## 2. The private polynomials

The private polynomial is

$$
f
=
x^6-x^4+x^3+x^2-1.
$$

Its coefficient vector is

$$
\boxed{
f=(-1,0,1,1,-1,0,1).
}
$$

The second small secret polynomial is

$$
g
=
x^6+x^4-x^2-x,
$$

with coefficient vector

$$
\boxed{
g=(0,-1,-1,0,1,0,1).
}
$$

Both are extremely small.

For \(f\),

$$
\|f\|_2^2
=
(-1)^2+1^2+1^2+(-1)^2+1^2
=
5.
$$

For \(g\),

$$
\|g\|_2^2
=
(-1)^2+(-1)^2+1^2+1^2
=
4.
$$

Therefore the concatenated private vector has squared norm

$$
\boxed{
\|(f,g)\|_2^2
=
5+4
=
9.
}
$$

Hence

$$
\boxed{
\|(f,g)\|_2=3.
}
$$

That number will become important once we compare the secret with the natural geometric scale of the public lattice.

The notebook also verifies that \(f\) is invertible in the required quotient rings modulo both

$$
p=3
$$

and

$$
q=41.
$$

---

## 3. Constructing the public key

The notebook uses the convention introduced in the previous chapter:

$$
\boxed{
h=f_q^{-1}g
\pmod{(q,x^7-1)}.
}
$$

Equivalently,

$$
h=g f_q^{-1}
\pmod q,
$$

because multiplication in this quotient ring is commutative.

The resulting public polynomial is

$$
h
=
20x^6
+
40x^5
+
2x^4
+
38x^3
+
8x^2
+
26x
+
30.
$$

Its coefficient vector is

$$
\boxed{
h=(30,26,8,38,2,40,20).
}
$$

Because

$$
h=f_q^{-1}g,
$$

multiplying by \(f\) gives

$$
fh
\equiv
g
\pmod{(41,x^7-1)}.
$$

Therefore,

$$
\boxed{
fh-g\equiv0\pmod{41}.
}
$$

This apparently simple modular relation is the complete reason the NTRU lattice contains the private key.

---

## 4. Lifting the modular relation to the integers

The equation

$$
fh\equiv g\pmod{41}
$$

means that every coefficient of

$$
fh-g
$$

is divisible by \(41\).

Instead of treating the coefficients of \(h\) only as residues in

$$
\mathbb Z_{41},
$$

lift them to the ordinary integers:

$$
h=(30,26,8,38,2,40,20).
$$

Now perform cyclic polynomial multiplication in

$$
\mathbb Z[x]/(x^7-1).
$$

For the given values,

$$
fh
=
40x
+
40x^2
+
42x^4
+
42x^6.
$$

Subtract

$$
g=x^6+x^4-x^2-x.
$$

We obtain

$$
fh-g
=
41x
+
41x^2
+
41x^4
+
41x^6.
$$

Therefore,

$$
\boxed{
fh-g
=
41
\left(
x+x^2+x^4+x^6
\right)
}
$$

inside

$$
\mathbb Z[x]/(x^7-1).
$$

Define

$$
u
=
x+x^2+x^4+x^6.
$$

Its coefficient vector is

$$
u=(0,1,1,0,1,0,1).
$$

Then

$$
\boxed{
fh-g=qu.
}
$$

Equivalently,

$$
\boxed{
fh-qu=g.
}
$$

We have now turned a modular congruence into an exact integer equation.

That is the key step required to build the lattice.

---

## 5. Multiplication by \(h\) as a circulant matrix

Multiplication by a fixed polynomial is a linear operation on coefficient vectors.

Because we work modulo

$$
x^7-1,
$$

multiplication is cyclic.

For

$$
h=(30,26,8,38,2,40,20),
$$

define the circulant matrix

$$
H=
\begin{pmatrix}
30&26&8&38&2&40&20\\
20&30&26&8&38&2&40\\
40&20&30&26&8&38&2\\
2&40&20&30&26&8&38\\
38&2&40&20&30&26&8\\
8&38&2&40&20&30&26\\
26&8&38&2&40&20&30
\end{pmatrix}.
$$

Under our row-vector convention,

$$
aH
$$

is the coefficient vector of

$$
a(x)h(x)
\pmod{x^7-1}.
$$

In particular,

$$
fH
=
(0,40,40,0,42,0,42).
$$

Meanwhile,

$$
g
=
(0,-1,-1,0,1,0,1).
$$

Subtracting gives

$$
fH-g
=
(0,41,41,0,41,0,41).
$$

Therefore,

$$
fH-g
=
41u,
$$

exactly matching the polynomial computation.

So

$$
\boxed{
fH-41u=g.
}
$$

This is now an ordinary integer linear-algebra equation.

---

## 6. Constructing the public NTRU lattice

Using the row-basis convention, define

$$
\boxed{
M_h=
\begin{pmatrix}
I&H\\
0&qI
\end{pmatrix}.
}
$$

Because

$$
N=7,
$$

this is a

$$
14\times14
$$

integer matrix.

Explicitly, it has the block structure

$$
M_h=
\begin{pmatrix}
I_7&H\\
0&41I_7
\end{pmatrix}.
$$

The lattice generated by its rows is

$$
\mathcal L(M_h)
=
\left\{
zM_h:
z\in\mathbb Z^{14}
\right\}.
$$

Write

$$
z=(a,b),
$$

with

$$
a,b\in\mathbb Z^7.
$$

Then

$$
(a,b)
M_h
=
(a,aH+qb).
$$

Therefore every vector in the lattice has the form

$$
\boxed{
(a,aH+qb).
}
$$

Equivalently, if we write a lattice vector as

$$
(v_1,v_2),
$$

then

$$
v_2
\equiv
v_1H
\pmod q.
$$

So we may also describe the lattice as

$$
\boxed{
\mathcal L_h
=
\left\{
(v_1,v_2)\in\mathbb Z^7\times\mathbb Z^7:
v_2\equiv v_1H\pmod{41}
\right\}.
}
$$

This is the public NTRU lattice.

Everything required to construct it is known from the public key.

---

## 7. Proving that the private key lies in the lattice

We already derived

$$
fH-41u=g.
$$

Choose

$$
a=f
$$

and

$$
b=-u.
$$

Then

$$
(a,b)M_h
=
(f,fH-41u).
$$

But

$$
fH-41u=g.
$$

Therefore,

$$
(f,-u)M_h
=
(f,g).
$$

Hence

$$
\boxed{
(f,g)\in\mathcal L(M_h).
}
$$

This is not a heuristic statement.

It is an exact algebraic proof.

The chain is

$$
h=f_q^{-1}g
$$

$$
\Downarrow
$$

$$
fh\equiv g\pmod q
$$

$$
\Downarrow
$$

$$
fH\equiv g\pmod q
$$

$$
\Downarrow
$$

$$
fH-g=qu
$$

$$
\Downarrow
$$

$$
(f,-u)M_h=(f,g)
$$

$$
\Downarrow
$$

$$
\boxed{
(f,g)\in\mathcal L_h.
}
$$

This is the rigorous meaning of the phrase:

> the NTRU private key is a short vector in the public NTRU lattice.

---

## 8. Why the secret is unusually short

The lattice has dimension

$$
d=14.
$$

Its basis is block upper triangular:

$$
M_h=
\begin{pmatrix}
I&H\\
0&41I
\end{pmatrix}.
$$

Therefore,

$$
\det(M_h)
=
\det(I)\det(41I).
$$

Hence,

$$
\boxed{
\det(\mathcal L_h)=41^7.
}
$$

Numerically,

$$
41^7
=
194754273881.
$$

This looks enormous, but determinant must be interpreted relative to dimension.

The determinant scale per dimension is

$$
\det(\mathcal L_h)^{1/14}
=
(41^7)^{1/14}
=
\sqrt{41}.
$$

Thus

$$
\boxed{
\det(\mathcal L_h)^{1/14}
=
\sqrt{41}
\approx6.40.
}
$$

The Gaussian heuristic suggests that the shortest vector of a random \(d\)-dimensional lattice of determinant \(D\) should have approximate length

$$
\lambda_{\mathrm{GH}}
\approx
\sqrt{\frac{d}{2\pi e}}
D^{1/d}.
$$

Here,

$$
d=14,
\qquad
D=41^7.
$$

Therefore,

$$
\lambda_{\mathrm{GH}}
\approx
\sqrt{\frac{14}{2\pi e}}\sqrt{41}.
$$

Numerically,

$$
\boxed{
\lambda_{\mathrm{GH}}
\approx5.8.
}
$$

But our private vector has length

$$
\boxed{
\|(f,g)\|_2=3.
}
$$

So the private key is dramatically shorter than the random-lattice heuristic scale.

This is exactly the geometric signal that lattice reduction attempts to expose.

There is, however, an important qualification:

$$
\mathcal L_h
$$

is not a random lattice.

It is a highly structured NTRU lattice.

The Gaussian heuristic therefore gives useful intuition, not a security proof.

---

## 9. What LLL actually does

Before running the attack, it is worth being precise about what LLL is trying to accomplish.

Suppose

$$
B=(b_1,\ldots,b_d)
$$

is a lattice basis.

A bad basis may consist of long, highly correlated vectors even when the lattice itself contains very short vectors.

LLL attempts to replace the basis by another basis of the same lattice with better geometric properties.

It relies on the Gram-Schmidt orthogonalization

$$
b_1^*,\ldots,b_d^*.
$$

Each basis vector can be expressed as

$$
b_i
=
b_i^*
+
\sum_{j<i}
\mu_{i,j}b_j^*.
$$

LLL repeatedly enforces two main conditions.

### Size reduction

The Gram-Schmidt coefficients are reduced so that typically

$$
|\mu_{i,j}|
\leq
\frac12.
$$

This prevents basis vectors from containing unnecessarily large projections onto earlier vectors.

### Lovász condition

For a reduction parameter

$$
\delta\in(1/4,1),
$$

LLL requires

$$
\delta
\|b_{i-1}^*\|^2
\leq
\|b_i^*\|^2
+
\mu_{i,i-1}^2
\|b_{i-1}^*\|^2.
$$

When this condition fails, neighboring basis vectors are swapped.

The repeated process tends to move shorter geometric directions toward the beginning of the basis.

---

### What LLL guarantees

LLL is polynomial-time.

It also provides approximation guarantees for the short vectors it returns.

But it does **not** solve exact SVP in general.

Its approximation factor grows exponentially with the lattice dimension.

So the interpretation should be

$$
\boxed{
\text{LLL finds reasonably short vectors efficiently}
}
$$

rather than

$$
\boxed{
\text{LLL always finds the shortest vector}.
}
$$

For a tiny \(14\)-dimensional NTRU lattice containing an exceptionally short secret, however, “reasonably short” is already enough.

---

## 10. Running LLL on the toy lattice

Now apply LLL to

$$
M_h.
$$

The reduced basis contains several unusually short vectors.

Importantly, LLL does **not** have to return the original vector

$$
(f,g)
$$

verbatim.

One short vector found by the recovered notebook is

$$
(\phi,\gamma),
$$

where

$$
\phi
=
-x^6-x^5+x^3-x^2+1
$$

and

$$
\gamma
=
x^5+x^4-x^2-1.
$$

Their coefficient vectors are

$$
\boxed{
\phi
=
(1,0,-1,1,0,-1,-1)
}
$$

and

$$
\boxed{
\gamma
=
(-1,0,-1,0,1,1,0).
}
$$

Calculate their norms:

$$
\|\phi\|_2^2
=
1+1+1+1+1
=
5,
$$

and

$$
\|\gamma\|_2^2
=
1+1+1+1
=
4.
$$

Therefore,

$$
\boxed{
\|(\phi,\gamma)\|_2^2=9
}
$$

and

$$
\boxed{
\|(\phi,\gamma)\|_2=3.
}
$$

This is exactly the same norm as the original private pair.

That is not an accident.

---

## 11. Recovering an equivalent private key

The notebook next multiplies both recovered polynomials by

$$
-x^4
$$

inside

$$
R=\mathbb Z[x]/(x^7-1).
$$

Because

$$
x^7=1,
$$

multiplication by \(x\) cyclically rotates coefficient vectors.

Multiplication by

$$
-x^4
$$

therefore performs:

1. a cyclic rotation by four positions;
2. a global sign change.

Apply it to \(\phi\):

$$
-x^4\phi
\equiv
f
\pmod{x^7-1}.
$$

Explicitly,

$$
-x^4\phi
=
x^6-x^4+x^3+x^2-1.
$$

That is precisely

$$
f.
$$

Similarly,

$$
-x^4\gamma
\equiv
g
\pmod{x^7-1}.
$$

Thus,

$$
\boxed{
-x^4(\phi,\gamma)=(f,g).
}
$$

The cleaned implementation reproduces the transformation exactly:

```text
short LLL vector:

[1, 0, -1, 1, 0, -1, -1, -1, 0, -1, 0, 1, 1, 0]

after multiplication by -x^4 mod (x^7-1):

f = [-1, 0, 1, 1, -1, 0, 1]

g = [0, -1, -1, 0, 1, 0, 1]

PASS: LLL recovers an NTRU-equivalent short secret pair.
```

So the attack has not merely found “some short vector.”

It has recovered a pair lying directly in the algebraic symmetry class of the original private key.

---

## 12. Why equivalent keys are sufficient

Why does multiplying both secret polynomials by the same monomial preserve the NTRU relation?

Suppose

$$
fh\equiv g\pmod q.
$$

Let

$$
u(x)
$$

be any invertible ring element.

Then

$$
u f h
\equiv
u g
\pmod q.
$$

Therefore,

$$
(uf,ug)
$$

satisfies exactly the same public relation.

In our example,

$$
u=-x^4.
$$

This is a unit because

$$
(-x^4)(-x^3)
=
x^7
\equiv1
\pmod{x^7-1}.
$$

Therefore,

$$
(-x^4)^{-1}
=
-x^3.
$$

Moreover, multiplying by a signed monomial merely permutes and negates coefficients.

Hence it preserves Euclidean norm:

$$
\|uf\|_2=\|f\|_2,
$$

and similarly for \(g\).

So

$$
(\phi,\gamma)
$$

and

$$
(f,g)
$$

represent geometrically equivalent short relations.

This illustrates an important cryptanalytic principle:

$$
\boxed{
\text{key recovery need not mean recovering the exact sampled representation}.
}
$$

If an attacker obtains another short pair satisfying the appropriate public relation and possessing the required invertibility or decryption properties, that may already be sufficient.

The exact criterion depends on the cryptosystem.

For this toy example, the recovered pair is even stronger: it is a signed cyclic rotation of the original private pair.

---

## 13. What the attack has actually accomplished

We can now state the attack precisely.

The adversary begins only with

$$
h.
$$

From \(h\), the adversary constructs

$$
H.
$$

From \(H\), construct

$$
M_h
=
\begin{pmatrix}
I&H\\
0&qI
\end{pmatrix}.
$$

The lattice is therefore completely public:

$$
\boxed{
h
\rightarrow
H
\rightarrow
M_h
\rightarrow
\mathcal L_h.
}
$$

The hidden private information satisfies

$$
(f,g)\in\mathcal L_h
$$

and has exceptionally small norm.

LLL transforms the poor public basis into a reduced basis containing short vectors.

Among those vectors appears

$$
(\phi,\gamma),
$$

which is related to the original key by

$$
(f,g)
=
-x^4(\phi,\gamma).
$$

So the complete attack pipeline is

$$
\boxed{
h
\rightarrow
H
\rightarrow
M_h
\rightarrow
\operatorname{LLL}(M_h)
\rightarrow
(\phi,\gamma)
\rightarrow
(f,g).
}
$$

This is a genuine lattice key-recovery attack on the deliberately tiny instance.

---

## 14. Scaling from toys to real cryptanalysis

Why does this work so easily?

Because everything has been made tiny.

The lattice dimension is only

$$
14.
$$

The modulus is only

$$
41.
$$

The secret norm is

$$
3.
$$

And the secret lies far below the rough random-lattice geometric scale.

In a real cryptanalytic setting, the attacker must deal with much larger dimensions and considerably more subtle geometry.

The relevant questions become quantitative.

### Lattice dimension

If the polynomial degree is \(N\), the basic NTRU lattice has dimension

$$
2N.
$$

Increasing \(N\) dramatically increases the cost of strong reduction.

---

### Determinant

The determinant

$$
q^N
$$

controls the overall density and geometric scale of the lattice.

---

### Secret length

The attacker compares the expected secret length with the lengths likely to become visible after reduction.

A useful ratio is conceptually

$$
\frac{\|s_{\text{target}}\|}
{\det(L)^{1/d}}.
$$

---

### Reduction quality

LLL is usually far too weak for cryptographic dimensions.

Attack analysis therefore considers stronger reduction methods, especially BKZ.

---

### BKZ block size

BKZ works with local blocks of dimension

$$
\beta.
$$

Increasing

$$
\beta
$$

improves the quality of the reduced basis but greatly increases attack cost.

---

### Post-reduction search

After reduction, attackers may use:

* enumeration;
* sieving;
* nearest-plane techniques;
* meet-in-the-middle methods;
* hybrid guessing;
* specialized structured attacks.

---

### Classical and quantum cost models

Concrete security estimates may differ depending on whether the attacker is modeled as classical or quantum.

Therefore real parameter selection requires much more than the slogan

$$
\text{SVP is hard}.
$$

It requires estimates of how good a reduced basis an attacker needs and how expensive obtaining that basis is expected to be.

---

## 15. Convention pitfalls

NTRU is particularly vulnerable to educational notation errors because several mathematically compatible conventions are common.

One convention defines

$$
h
=
pgf_q^{-1}
\pmod q
$$

and encrypts as

$$
e=rh+m.
$$

Another defines

$$
h
=
gf_q^{-1}
\pmod q
$$

and encrypts as

$$
e=prh+m.
$$

This notebook uses the second convention:

$$
\boxed{
h=gf_q^{-1}.
}
$$

Accordingly,

$$
\boxed{
fh\equiv g\pmod q.
}
$$

That is why the short lattice vector is naturally

$$
(f,g).
$$

Under the first convention,

$$
fh\equiv pg\pmod q,
$$

so the directly associated vector would instead involve

$$
(f,pg).
$$

The two conventions are not contradictory.

But they must not be mixed.

A typical broken toy implementation accidentally uses

$$
h=pgf_q^{-1}
$$

and also encrypts with

$$
prh+m.
$$

The factor \(p\) has then been inserted twice.

The decryption derivation no longer matches the intended scheme.

So whenever working with NTRU, first write down explicitly:

$$
\boxed{
\text{public-key convention}
+
\text{encryption convention}
+
\text{lattice convention}.
}
$$

Only then begin the algebra.

---

## 16. The general lattice-attack pattern

This toy NTRU experiment illustrates a pattern that appears throughout lattice cryptanalysis.

### Step 1: identify an algebraic relation

Here:

$$
fh-g\equiv0\pmod q.
$$

### Step 2: lift it to an integer equation

$$
fh-g=qu.
$$

### Step 3: encode the relation as a lattice

$$
(f,g)\in\mathcal L_h.
$$

### Step 4: arrange the geometry

The desired hidden object must become short relative to typical lattice vectors.

In other attacks, this may require additional coordinate scaling or embedding tricks.

### Step 5: reduce the basis

Use methods such as

$$
\text{LLL}
$$

or

$$
\text{BKZ}.
$$

### Step 6: search the reduced lattice

Look for vectors exhibiting the expected shortness or structure.

### Step 7: interpret the result algebraically

Convert the recovered integer vector back into the original problem.

For our example,

$$
(\phi,\gamma)
\rightarrow
-x^4(\phi,\gamma)
=
(f,g).
$$

This pattern appears in many other settings:

* Hidden Number Problem constructions;
* partial-key exposure;
* Coppersmith-style small-root lattices;
* approximate common-divisor problems;
* structured relation attacks;
* various cryptanalytic embeddings.

Their lattice bases may look completely different.

But the central design principle remains:

$$
\boxed{
\text{encode the hidden solution so that it becomes geometrically special}.
}
$$

---

## 17. Companion implementation

The cleaned experiment is located at

```text
experiments/lattices/ross-course/ntru_lll_attack.py
```

It is dependency-free and reconstructs the entire notebook calculation.

It contains:

* the exact toy parameters

$$
N=7,\quad p=3,\quad q=41;
$$

* the original private polynomials \(f\) and \(g\);
* the exact public polynomial \(h\);
* cyclic polynomial multiplication modulo \(x^7-1\);
* construction of the public circulant matrix \(H\);
* construction of the \(14\times14\) NTRU lattice basis;
* verification that

$$
(f,g)\in\mathcal L_h;
$$

* an educational exact-arithmetic LLL implementation;
* automatic detection of a short recovered pair;
* verification that the pair satisfies the NTRU relation;
* multiplication by

$$
-x^4
$$

to recover the original private polynomials.

Using exact rational arithmetic for the educational LLL implementation also avoids hiding numerical-rounding issues behind floating-point Gram-Schmidt calculations.

The experiment therefore reproduces the mathematical derivation rather than merely printing a hard-coded answer.

---

## 18. Final lesson

This tiny instance makes one of the most important ideas in lattice cryptography completely concrete.

The public key is a polynomial:

$$
h.
$$

But that polynomial also defines a linear transformation:

$$
H.
$$

That matrix defines a lattice:

$$
\mathcal L_h.
$$

The private polynomials satisfy

$$
fh\equiv g\pmod q.
$$

Therefore their coefficient vectors satisfy

$$
(f,g)\in\mathcal L_h.
$$

And because \(f\) and \(g\) are deliberately small,

$$
(f,g)
$$

is an unusually short vector.

So the complete chain is

$$
\boxed{
h
}
$$

$$
\Downarrow
$$

$$
\boxed{
fh\equiv g\pmod q
}
$$

$$
\Downarrow
$$

$$
\boxed{
fH-g=qu
}
$$

$$
\Downarrow
$$

$$
\boxed{
(f,g)\in\mathcal L_h
}
$$

$$
\Downarrow
$$

$$
\boxed{
\|(f,g)\|_2=3
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{LLL exposes an equivalent short vector}
}
$$

$$
\Downarrow
$$

$$
\boxed{
(\phi,\gamma)
\xrightarrow{\times(-x^4)}
(f,g).
}
$$

The legitimate user begins with knowledge of the short vector.

The attacker begins only with the public description of the lattice.

Lattice cryptanalysis asks whether the geometry of that public lattice reveals the hidden short structure efficiently enough.

For this toy instance, the answer is yes.

For cryptographic parameters, the entire security problem is to make the same geometric search computationally infeasible.

That is the real lesson of the experiment:

> **LLL does not magically “break NTRU.” It exposes, in a tiny controlled setting, exactly what a lattice attacker is trying to recover from the public geometry.**
