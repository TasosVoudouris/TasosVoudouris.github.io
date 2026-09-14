---
title: 'RSA Deep Dive VIII: Franklin–Reiter From Zero — When Related Messages Share a Polynomial Root'
description: Two textbook RSA ciphertexts can reveal much more than two independent equations when their plaintexts satisfy a known algebraic relation. We derive the classical Franklin–Reiter related-message result, compute the polynomial GCD over Z_N[x], and explain the subtlety of doing Euclid over a composite-modulus coefficient ring.
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
tags:
- rsa
- franklin-reiter
- related-messages
- polynomial-gcd
- modular-polynomials
- algebraic-cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 8
draft: false
---
The last few RSA deep dives have all taken the same general shape.

We started with some extra structure:

- a small private exponent,
- a partially known plaintext,
- a partially known prime factor,

and turned that structure into algebra.

This time the messages themselves are not small.

Their **relationship** is known.

Suppose two plaintext representatives satisfy

$$
m_2=a m_1+b
\pmod N,
$$

where $a$ and $b$ are public.

Both are then encrypted with the same textbook RSA key.

For the classical Franklin–Reiter case, take

$$
e=3.
$$

Then

$$
c_1\equiv m_1^3\pmod N
$$

and

$$
c_2\equiv (a m_1+b)^3\pmod N.
$$

At first this looks like two ordinary RSA ciphertexts.

But mathematically they are two polynomial equations with the **same hidden root**.

That changes the problem completely.

![Franklin–Reiter: related RSA messages become a shared polynomial root](/images/blog/20-rsa-franklin-reiter.svg)

*Franklin–Reiter is not a lattice attack in its classical affine case. The central tool is the polynomial Euclidean algorithm over the RSA coefficient ring.*

If you want the relevant earlier posts first:

- [Modular Arithmetic From Zero](/blog/03-modular-arithmetic-units-zero-divisors/)
- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Coppersmith From Zero](/blog/17-rsa-coppersmith-from-zero/)
- [Partial Key Exposure From Zero](/blog/19-rsa-partial-key-exposure/)

---

## 1. Turn both ciphertexts into polynomials

Let the first message be

$$
m=m_1.
$$

Assume the second message is related by the known affine map

$$
m_2=a m+b.
$$

The ciphertext equations are

$$
c_1\equiv m^e\pmod N
$$

and

$$
c_2\equiv (am+b)^e\pmod N.
$$

Now introduce an indeterminate $X$ and define

$$
g_1(X)=X^e-c_1,
$$

$$
g_2(X)=(aX+b)^e-c_2.
$$

At the secret value $X=m$,

$$
g_1(m)\equiv0\pmod N
$$

and

$$
g_2(m)\equiv0\pmod N.
$$

So both polynomials have the same modular root.

Equivalently, in the polynomial ring

$$
\mathbb Z_N[X],
$$

both contain the factor

$$
X-m
$$

in the generic successful case.

This suggests a very old algorithm:

$$
\boxed{
\gcd(g_1,g_2).
}
$$

If the polynomial GCD is exactly

$$
X-m,
$$

then the plaintext representative appears immediately.

No factorization of $N$ is used.

No private exponent is used.

No lattice is required in this simplest case.

The information is already present in the shared algebraic root.

---

## 2. The simplest case can even be eliminated by hand

Before hiding anything inside a polynomial-GCD routine, take the particularly clean relation

$$
m_2=m+1.
$$

With

$$
e=3,
$$

we have

$$
c_1\equiv m^3\pmod N,
$$

$$
c_2\equiv(m+1)^3\pmod N.
$$

Subtract:

$$
c_2-c_1
\equiv
3m^2+3m+1
\pmod N.
$$

Therefore

$$
c_2-c_1-1
\equiv
3m(m+1)
\pmod N.
$$

For a valid textbook RSA exponent $e=3$, we require

$$
\gcd(3,\varphi(N))=1,
$$

which in the ordinary two-prime setting also ensures that $3$ is invertible modulo $N$.

Define

$$
t
=
\frac{c_2-c_1-1}{3}
\pmod N.
$$

Then

$$
t\equiv m^2+m\pmod N.
$$

Hence

$$
m^2\equiv t-m\pmod N.
$$

Multiply by $m$:

$$
m^3
\equiv
tm-m^2
\pmod N.
$$

Substitute the previous relation:

$$
m^3
\equiv
tm-(t-m)
=
m(t+1)-t
\pmod N.
$$

But

$$
m^3\equiv c_1\pmod N.
$$

So

$$
c_1
\equiv
m(t+1)-t
\pmod N.
$$

Therefore, whenever $t+1$ is invertible modulo $N$,

$$
\boxed{
m
\equiv
(c_1+t)(t+1)^{-1}
\pmod N.
}
$$

That is the attack for this special case written as elementary modular algebra.

The polynomial-GCD formulation is more general and much cleaner.

But this derivation shows exactly why the information exists.

---

## 3. A fully checked toy example

Reuse the same fixed educational RSA modulus from the earlier Coppersmith post:

$$
p=30\,011,
\qquad
q=35\,027.
$$

Then

$$
N=pq
=
1\,051\,195\,297.
$$

Take the toy plaintext

$$
m=12\,037.
$$

Let the second plaintext be

$$
m_2=m+1=12\,038.
$$

Use textbook exponent

$$
e=3.
$$

The two ciphertexts are

$$
c_1
=
12\,037^3\bmod N
=
100\,336\,930,
$$

and

$$
c_2
=
12\,038^3\bmod N
=
535\,041\,149.
$$

Now compute

$$
t
=
\frac{c_2-c_1-1}{3}.
$$

Numerically,

$$
t
=
\frac{
535\,041\,149
-
100\,336\,930
-
1
}{3}
=
144\,901\,406.
$$

And indeed

$$
12\,037^2+12\,037
=
144\,901\,406.
$$

Now

$$
c_1+t
=
245\,238\,336
$$

and

$$
t+1
=
144\,901\,407.
$$

The denominator is a unit modulo $N$, so

$$
m
\equiv
245\,238\,336
\cdot
144\,901\,407^{-1}
\pmod N.
$$

This gives

$$
\boxed{
m=12\,037.
}
$$

The related plaintext is then

$$
m_2=m+1=12\,038.
$$

Everything came from:

```text
N
e
c1
c2
known relation m2 = m1 + 1
```

The factorization was used only to construct the toy RSA instance, not in the recovery algebra.

---

## 4. Now express the same calculation as a polynomial GCD

Define

$$
g_1(X)
=
X^3-100\,336\,930.
$$

The second polynomial is

$$
g_2(X)
=
(X+1)^3-535\,041\,149.
$$

Expand it:

$$
g_2(X)
=
X^3+3X^2+3X+1-535\,041\,149.
$$

So:

$$
g_2(X)
=
X^3+3X^2+3X-535\,041\,148.
$$

All coefficients are interpreted modulo

$$
N=1\,051\,195\,297.
$$

The hidden value

$$
X=12\,037
$$

is a root of both.

Now run the polynomial Euclidean algorithm in

$$
\mathbb Z_N[X].
$$

For our fixed example it terminates with the monic GCD

$$
\boxed{
X-12\,037.
}
$$

Modulo $N$, its constant coefficient is

$$
-12\,037
\equiv
1\,051\,183\,260
\pmod N.
$$

So if the code returns the monic coefficient vector

```text
[1051183260, 1]
```

that is exactly

$$
X-12\,037.
$$

Recovering the common root is then just:

$$
m
\equiv
-1\,051\,183\,260
\pmod N
=
12\,037.
$$

That is the complete Franklin–Reiter mechanism in the classical affine case.

---

## 5. Polynomial Euclid is the same Euclid again

This is one of the connections I like most in the whole series.

At the beginning we used the Euclidean algorithm on integers:

$$
\gcd(a,b).
$$

Then Extended Euclid gave modular inverses.

Now Euclid returns again, but its inputs are polynomials.

For two polynomials $A(X)$ and $B(X)$:

$$
A(X)
=
Q(X)B(X)+R(X),
$$

where

$$
\deg R<\deg B.
$$

Then

$$
\gcd(A,B)
=
\gcd(B,R).
$$

Repeat until the remainder is zero.

The last non-zero remainder, normalized to monic form, is the polynomial GCD.

So the conceptual path is:

```text
integer Euclid
        ↓
modular inverses
        ↓
RSA key arithmetic
        ↓
polynomial Euclid
        ↓
related-message reconstruction
```

The algorithm did not change in spirit.

The algebraic object changed.

---

## 6. But $\mathbb Z_N$ is not a field

There is an important subtlety here.

If $N$ is composite, then

$$
\mathbb Z_N
$$

contains zero divisors.

Therefore

$$
\mathbb Z_N[X]
$$

is not a polynomial ring over a field.

In ordinary polynomial long division over a field, we divide by the leading coefficient of the divisor.

Over $\mathbb Z_N$, that step is valid only when the leading coefficient is a **unit** modulo $N$.

So if the current divisor has leading coefficient $\ell$, we need

$$
\gcd(\ell,N)=1
$$

to compute

$$
\ell^{-1}\pmod N.
$$

If instead

$$
1<\gcd(\ell,N)<N,
$$

then something mathematically interesting has happened:

the failed coefficient inversion itself has exposed a non-trivial divisor of $N$.

So a robust educational implementation should not pretend that polynomial GCD over $\mathbb Z_N[X]$ behaves exactly like polynomial GCD over

$$
\mathbb F_p[X].
$$

Our fixed toy instance is chosen so that every required leading coefficient is invertible and the Euclidean sequence works normally.

But the ring issue is real.

This reconnects directly to Blog 03:

> over a composite modulus, non-zero does not imply invertible.

That statement now affects an actual polynomial algorithm.

---

## 7. What Franklin–Reiter actually assumes

The clean classical setup is:

$$
m_2=am_1+b
\pmod N,
$$

with publicly known $a,b$.

Both messages are encrypted using:

- the same RSA modulus $N$,
- the same public exponent $e$,
- textbook deterministic RSA.

Then define

$$
g_1(X)=X^e-c_1,
$$

$$
g_2(X)=(aX+b)^e-c_2.
$$

Both share the root

$$
X=m_1.
$$

For the classical Franklin–Reiter case:

$$
e=3,
\qquad
\deg(m_2\text{ as a function of }m_1)=1.
$$

Generically, the polynomial GCD is linear:

$$
\gcd(g_1,g_2)=X-m_1.
$$

The 1996 Coppersmith–Franklin–Patarin–Reiter paper starts from exactly this setting and then generalizes:

- the exponent $e$,
- the degree of the relation,
- the number of related messages.

So I would separate the names carefully.

### Franklin–Reiter

The original elegant case:

```text
two messages
same RSA key
e = 3
known linear relation
polynomial gcd
```

### Coppersmith–Franklin–Patarin–Reiter

The broader EUROCRYPT '96 related-message framework:

```text
low exponent
known polynomial relations
possibly more messages
more general algebraic elimination
```

That historical distinction is worth preserving.

---

## 8. Franklin–Reiter is not the same as Håstad

These attacks are related because both exploit low-degree RSA structure.

But their information models are different.

### Håstad broadcast

Same or predictably related plaintext information appears under **different moduli**:

$$
c_i\equiv m^e\pmod{N_i}.
$$

CRT combines independent modular views.

### Franklin–Reiter

Related plaintexts appear under the **same modulus**:

$$
c_1\equiv m^e\pmod N,
$$

$$
c_2\equiv(am+b)^e\pmod N.
$$

The shared polynomial root is extracted algebraically.

So:

```text
Håstad:
many modular worlds
        ↓
CRT
        ↓
low-degree reconstruction

Franklin–Reiter:
one modular world
        ↓
two related polynomial equations
        ↓
polynomial GCD
```

This is a useful separation because “low exponent RSA attack” is otherwise too vague to mean anything.

---

## 9. And it is not Coppersmith either

The connection to Coppersmith is historical and conceptual, but the classical Franklin–Reiter calculation does not depend on a small root.

The secret message can be large.

What matters is that it is a **common root** of two known polynomials.

Compare:

### Coppersmith

$$
f(x_0)\equiv0\pmod N
$$

plus:

$$
|x_0|<X.
$$

Smallness is essential.

### Franklin–Reiter

$$
g_1(m)\equiv0\pmod N,
$$

$$
g_2(m)\equiv0\pmod N.
$$

The key information is not:

$$
|m|\text{ small}.
$$

It is:

$$
\boxed{
\text{the same unknown root satisfies two related equations}.
}
$$

So the right taxonomy is:

```text
Coppersmith
-> one polynomial
-> unusually small root

Franklin–Reiter
-> multiple related polynomials
-> shared root
-> polynomial gcd
```

Both are algebraic cryptanalysis.

But they exploit different information.

---

## 10. Why randomized encoding changes the problem

The equations above describe textbook RSA representatives directly.

Modern RSA encryption does not simply compute

$$
m^e\bmod N
$$

on a deterministic application message.

RSAES-OAEP first transforms the message using randomized encoding.

So two application messages with a simple relation like

$$
M_2=M_1+1
$$

do not normally become encoded representatives satisfying

$$
EM_2=EM_1+1.
$$

Instead, fresh randomness produces unrelated-looking encoded representatives before RSA exponentiation.

That destroys the specific algebraic relation required by this classical model.

The scientific lesson is the same one we have now seen repeatedly:

> the secure cryptosystem is not merely the trapdoor exponentiation map.

Encoding changes the mathematical object that reaches that map.

That is why textbook RSA is useful for studying the algebra but is not a modern encryption design.

---

## 11. The companion implementation

The companion script implements the polynomial arithmetic directly.

Polynomials are stored in low-to-high coefficient order:

```python
[a0, a1, a2, ...]
```

for

$$
a_0+a_1X+a_2X^2+\cdots.
$$

The script implements:

```text
normalization
addition / subtraction
multiplication
polynomial exponentiation
modular long division
monic normalization
Euclidean polynomial GCD
```

The crucial division step explicitly checks whether the divisor's leading coefficient is invertible modulo $N$.

If not, it reports the non-unit condition rather than silently pretending that $\mathbb Z_N$ is a field.

For the fixed toy example the script verifies:

$$
g_1(12\,037)\equiv0\pmod N,
$$

$$
g_2(12\,037)\equiv0\pmod N,
$$

and obtains:

$$
\gcd(g_1,g_2)
=
X-12\,037.
$$

It separately checks the hand-derived formula from Section 2.

So we get the same secret root in two ways:

```text
direct algebraic elimination
        =
polynomial Euclidean algorithm
```

That is the reproducibility check I wanted.

---

## 12. What I want to remember

The whole Franklin–Reiter idea fits into one diagram.

Start with:

$$
m_2=am_1+b.
$$

Encrypt both with textbook RSA:

$$
c_1=m_1^e\bmod N,
$$

$$
c_2=(am_1+b)^e\bmod N.
$$

Construct:

$$
g_1(X)=X^e-c_1,
$$

$$
g_2(X)=(aX+b)^e-c_2.
$$

Then:

$$
g_1(m_1)=g_2(m_1)=0
\pmod N.
$$

Therefore:

$$
X-m_1
$$

is a common factor.

Generically:

$$
\boxed{
\gcd(g_1,g_2)=X-m_1.
}
$$

And the message follows from the linear factor.

So the important chain is:

```text
known message relation
        ↓
shared modular root
        ↓
shared polynomial factor
        ↓
polynomial Euclid
        ↓
linear gcd
        ↓
message representative
```

No lattice.

No small-root bound.

Just algebraic dependence.

That is exactly why related-message structure deserves its own RSA deep dive.

---

## References

1. Matthew K. Franklin and Michael K. Reiter, **“A Linear Protocol Failure for RSA with Exponent Three”**, presented at the CRYPTO '95 Rump Session, August 1995.

2. Don Coppersmith, Matthew Franklin, Jacques Patarin, and Michael Reiter, **“Low-Exponent RSA with Related Messages”**, *Advances in Cryptology — EUROCRYPT '96*, LNCS 1070, pp. 1–9, 1996.  
   https://doi.org/10.1007/3-540-68339-9_1

3. Ronald L. Rivest, Adi Shamir, and Leonard Adleman, **“A Method for Obtaining Digital Signatures and Public-Key Cryptosystems”**, *Communications of the ACM*, 21(2), pp. 120–126, 1978.

---

At this point our RSA algebraic branch is becoming a map rather than a collection of isolated attacks:

```text
repeated plaintext
        -> Håstad / CRT

same modulus + different exponents
        -> common modulus / Bézout

small d
        -> Wiener
        -> Boneh–Durfee

small unknown component
        -> Coppersmith

partial factor information
        -> divisor small roots

related plaintexts
        -> Franklin–Reiter / polynomial GCD
```

The next natural RSA topic is closely related but slightly more subtle.

Instead of assuming a fixed known relation such as

$$
m_2=m_1+1,
$$

suppose RSA messages use **short random padding**, so the difference between two related representatives is unknown but small.

Then Franklin–Reiter alone is not enough.

Coppersmith returns.

**Next RSA Deep Dive:** *Short-Pad RSA From Zero — Combining Resultants, Franklin–Reiter, and Coppersmith.*
