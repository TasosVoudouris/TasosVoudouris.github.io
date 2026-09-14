---
title: "Finite Fields I: From Prime Fields to Extension Fields"
description: "How finite fields are constructed, why their sizes are prime powers, and how irreducible polynomials turn quotient rings into extension fields."
pubDate: "2025-05-16"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Finite Fields"
- "Abstract Algebra"
tags:
- "finite-fields"
- "prime-fields"
- "extension-fields"
- "quotient-rings"
- "irreducible-polynomials"
difficulty: "Intermediate"
status: "Reference"
series: "Finite Fields & Polynomial Arithmetic"
seriesOrder: 1
sourcePath: "experiments/mathematics/finite-fields"
draft: false
---
Finite fields combine rigid algebraic structure with efficient computation. They appear in coding theory, elliptic curves, secret sharing, error correction, and essentially every algebraic cryptographic construction.

## 1. Prime fields

For a prime $p$, the residue ring
$$
\mathbb Z/p\mathbb Z
$$
is a field, denoted $\mathbb F_p$. Every nonzero element has a multiplicative inverse because
$$
\gcd(a,p)=1
$$
whenever $a\not\equiv0\pmod p$.

A composite modulus does **not** generally give a field. For example, in $\mathbb Z/15\mathbb Z$,
$$
3\cdot5=0,
$$
so nonzero zero divisors exist.

The companion Python implementation therefore checks that the modulus is prime instead of silently calling every $\mathbb Z/n\mathbb Z$ a field.

## 2. Why finite-field sizes are prime powers

Every finite field $F$ has characteristic $p$ for some prime $p$. Therefore it contains a copy of $\mathbb F_p$ and is a finite-dimensional vector space over that prime field.

If
$$
[F:\mathbb F_p]=n,
$$
then
$$
|F|=p^n.
$$

Conversely, for every prime power $q=p^n$, a field with exactly $q$ elements exists, and any two such fields are isomorphic. We therefore write **the** field $\mathbb F_q$, meaning unique up to isomorphism.

## 3. Constructing an extension field

Choose an irreducible polynomial
$$
f(x)\in\mathbb F_p[x]
$$
of degree $n$. Then
$$
\mathbb F_p[x]/(f(x))
$$
is a field with $p^n$ elements.

Let
$$
\alpha=x+(f).
$$
Then $f(\alpha)=0$, and every element has a unique representation
$$
a_0+a_1\alpha+\cdots+a_{n-1}\alpha^{n-1},
\qquad a_i\in\mathbb F_p.
$$

### Example: $\mathbb F_8$

Over $\mathbb F_2$, the polynomial
$$
f(x)=x^3+x+1
$$
has no root in $\mathbb F_2$, so as a cubic it is irreducible. Therefore
$$
\mathbb F_8\cong\mathbb F_2[x]/(x^3+x+1).
$$
Inside the quotient,
$$
\alpha^3=\alpha+1
$$
because subtraction and addition coincide in characteristic $2$.

## 4. Addition and multiplication

Addition is coefficientwise modulo $p$.

Multiplication proceeds in two stages:

1. multiply the representative polynomials;
2. reduce the result modulo the defining polynomial $f(x)$.

Thus extension-field arithmetic is literally polynomial arithmetic plus modular reduction.

## 5. The multiplicative group

The nonzero elements form
$$
\mathbb F_q^\times,
$$
a cyclic group of order $q-1$.

This gives
$$
a^{q-1}=1
$$
for every $a\ne0$, and
$$
a^q=a
$$
for every $a\in\mathbb F_q$.

The polynomial identity
$$
x^q-x=\prod_{a\in\mathbb F_q}(x-a)
$$
is one of the most useful finite-field facts. It drives irreducibility tests and factorization algorithms later in this series.

## 6. Implementation boundary

The companion `prime_field.py` deliberately implements only $\mathbb F_p$. Extension fields require a polynomial type and reduction modulo an irreducible polynomial; mixing those two abstraction levels into one short class is a common source of hidden bugs.
