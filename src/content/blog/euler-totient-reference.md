---
title: "Euler's Totient Function and Element Orders"
description: "A focused reference on Euler's totient function, the group of units modulo n, multiplicative orders, factorization formulas, Euler's theorem, and computational examples."
pubDate: "2025-04-25"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "euler-phi"
  - "totient"
  - "group-order"
  - "element-order"
  - "number-theory"
difficulty: "Intermediate"
series: "Elementary Number Theory Reference"
seriesOrder: 5
draft: false
---

In the previous references, we separated the full ring

\[
\mathbb Z_n
\]

from the elements that are actually invertible under multiplication.

Those invertible residue classes form the **group of units**

\[
\mathbb Z_n^\times
=
\{
[a]_n :
\gcd(a,n)=1
\}.
\]

Euler's totient function tells us exactly how large that group is.

If

\[
\varphi(n)
\]

denotes Euler's totient function, then

\[
\boxed{
\varphi(n)
=
|\mathbb Z_n^\times|.
}
\]

That single equation already connects elementary number theory with finite-group structure.

But there is another quantity we also need to distinguish carefully.

The group itself has an order:

\[
|\mathbb Z_n^\times|
=
\varphi(n),
\]

while each individual unit

\[
a\in\mathbb Z_n^\times
\]

has its own **multiplicative order**:

\[
\operatorname{ord}_n(a).
\]

These are related, but they are not the same thing.

Understanding that distinction leads naturally to Euler's theorem, Fermat's little theorem, cyclic subgroups, generators, RSA, and much of finite-group cryptography.

---

## Table of Contents

- [Euler’s totient function](#eulers-totient-function)
- [The group of units](#the-group-of-units)
- [Order of an element](#order-of-an-element)
- [Group order versus element order](#group-order-versus-element-order)
- [Computing the totient](#computing-the-totient)
- [Prime-factorization formula](#prime-factorization-formula)
- [Euler’s theorem](#eulers-theorem)
- [A connection to Carmichael’s function](#a-connection-to-carmichaels-function)
- [Computational examples](#computational-examples)
- [SageMath](#sagemath)
- [Python with SymPy](#python-with-sympy)
- [A few deeper facts](#a-few-deeper-facts)
- [Open problems around the totient](#open-problems-around-the-totient)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Where this leads](#where-this-leads)

---

## Euler's totient function

For a positive integer \(n\), Euler's totient function

\[
\varphi(n)
\]

counts the residue classes modulo \(n\) that are relatively prime to \(n\).

Equivalently,

\[
\boxed{
\varphi(n)
=
\#\{
a:
1\le a\le n,
\ \gcd(a,n)=1
\}.
}
\]

For \(n>1\), we can equally count:

\[
1\le a<n.
\]

The special value

\[
\varphi(1)=1
\]

is taken by convention.

### Small examples

| \(n\) | Integers coprime to \(n\) | \(\varphi(n)\) |
| ---: | --- | ---: |
| \(1\) | \(1\) | \(1\) |
| \(2\) | \(1\) | \(1\) |
| \(5\) | \(1,2,3,4\) | \(4\) |
| \(10\) | \(1,3,7,9\) | \(4\) |
| \(12\) | \(1,5,7,11\) | \(4\) |
| \(13\) | \(1,2,\ldots,12\) | \(12\) |
| \(14\) | \(1,3,5,9,11,13\) | \(6\) |

If \(p\) is prime, then every nonzero residue modulo \(p\) is coprime to \(p\).

Therefore,

\[
\boxed{
\varphi(p)=p-1.
}
\]

For example,

\[
\varphi(13)=12.
\]

---

## The group of units

Recall that an element

\[
[a]_n\in\mathbb Z_n
\]

has a multiplicative inverse if and only if

\[
\gcd(a,n)=1.
\]

The set of all invertible residue classes is

\[
\mathbb Z_n^\times
=
\{
[a]_n:
\gcd(a,n)=1
\}.
\]

This set forms a group under multiplication modulo \(n\).

Thus:

\[
\boxed{
|\mathbb Z_n^\times|
=
\varphi(n).
}
\]

For example,

\[
\mathbb Z_{10}^\times
=
\{
[1],[3],[7],[9]
\}.
\]

Therefore,

\[
|\mathbb Z_{10}^\times|
=
4
=
\varphi(10).
\]

This gives Euler's function a structural interpretation.

It is not merely counting numbers that happen to be coprime to \(n\).

It is measuring the size of a finite multiplicative group.

---

## Order of an element

Let

\[
a\in\mathbb Z_n^\times.
\]

The **multiplicative order** of \(a\) modulo \(n\), written

\[
\operatorname{ord}_n(a),
\]

is the smallest positive integer \(m\) satisfying

\[
\boxed{
a^m\equiv1\pmod n.
}
\]

For example, consider

\[
a=3
\]

modulo \(10\).

Compute successive powers:

\[
3^1\equiv3\pmod{10},
\]

\[
3^2\equiv9\pmod{10},
\]

\[
3^3\equiv7\pmod{10},
\]

and

\[
3^4\equiv1\pmod{10}.
\]

No smaller positive exponent produced \(1\), so

\[
\boxed{
\operatorname{ord}_{10}(3)=4.
}
\]

The powers cycle:

\[
3
\rightarrow
9
\rightarrow
7
\rightarrow
1
\rightarrow
3
\rightarrow\cdots
\]

### Why must an order exist?

Because

\[
a\in\mathbb Z_n^\times,
\]

all powers of \(a\) remain inside the finite group

\[
\mathbb Z_n^\times.
\]

Consider:

\[
1,a,a^2,a^3,\ldots
\]

There are only finitely many possible group elements, so eventually two powers must coincide:

\[
a^i=a^j
\]

for some

\[
i<j.
\]

Because \(a\) is invertible, we can multiply by \(a^{-i}\):

\[
a^{j-i}=1.
\]

Therefore some positive exponent returns us to the identity.

The smallest such exponent is

\[
\operatorname{ord}_n(a).
\]

---

## Group order versus element order

This distinction is fundamental.

The **group order** is

\[
|\mathbb Z_n^\times|
=
\varphi(n).
\]

The **element order** is

\[
\operatorname{ord}_n(a).
\]

By Lagrange's theorem,

\[
\boxed{
\operatorname{ord}_n(a)
\mid
\varphi(n)
}
\]

for every

\[
a\in\mathbb Z_n^\times.
\]

For our previous example,

\[
\varphi(10)=4
\]

and

\[
\operatorname{ord}_{10}(3)=4.
\]

So \(3\) has the maximum possible order in this group.

Indeed,

\[
\langle3\rangle
=
\mathbb Z_{10}^\times.
\]

In that case, \(3\) is a generator of the multiplicative group.

But an element does not always have order equal to the entire group order.

For example:

\[
3^2
=
9
\equiv-1\pmod{10},
\]

so \(3\) has order \(4\), whereas

\[
9^2
=
81
\equiv1\pmod{10},
\]

giving

\[
\operatorname{ord}_{10}(9)=2.
\]

Both elements belong to the same group, but their individual orders differ.

### The group need not even be cyclic

Consider

\[
\mathbb Z_8^\times
=
\{
1,3,5,7
\}.
\]

Its group order is

\[
\varphi(8)=4.
\]

But:

\[
3^2\equiv1\pmod8,
\]

\[
5^2\equiv1\pmod8,
\]

and

\[
7^2\equiv1\pmod8.
\]

Every nonidentity element has order \(2\).

Therefore no element has order \(4\), and

\[
\mathbb Z_8^\times
\]

is not cyclic.

So:

\[
\boxed{
\text{group order}
\neq
\text{element order}
}
\]

and even more importantly:

\[
\boxed{
|G|=m
\not\Rightarrow
\text{there exists an element of order }m.
}
\]

This distinction becomes central when we later discuss generators and cryptographic groups.

---

## Computing the totient

The definition of \(\varphi(n)\) gives a direct algorithm:

```text
count the integers coprime to n
```

but the arithmetic structure of \(n\) gives us much faster formulas.

### Prime modulus

If \(p\) is prime,

\[
\boxed{
\varphi(p)=p-1.
}
\]

Every integer

\[
1,2,\ldots,p-1
\]

is coprime to \(p\).

### Prime powers

For a prime \(p\),

\[
\varphi(p^k)
=
p^k-p^{k-1}.
\]

Why?

Among the

\[
p^k
\]

residue classes, precisely

\[
p^{k-1}
\]

are divisible by \(p\), namely:

\[
0,p,2p,\ldots,(p^{k-1}-1)p.
\]

Those are exactly the classes that are not coprime to \(p^k\).

Therefore,

\[
\boxed{
\varphi(p^k)
=
p^{k-1}(p-1).
}
\]

### Multiplicativity

Euler's totient function is **multiplicative**:

if

\[
\gcd(m,n)=1,
\]

then

\[
\boxed{
\varphi(mn)
=
\varphi(m)\varphi(n).
}
\]

The coprimality condition matters.

The function is multiplicative, but it is **not completely multiplicative**.

For example,

\[
\varphi(4)
=
2,
\]

whereas

\[
\varphi(2)\varphi(2)
=
1.
\]

So we cannot simply write

\[
\varphi(mn)=\varphi(m)\varphi(n)
\]

without checking

\[
\gcd(m,n)=1.
\]

The Chinese Remainder Theorem gives a structural explanation for multiplicativity.

When

\[
\gcd(m,n)=1,
\]

the multiplicative group modulo \(mn\) decomposes as

\[
\mathbb Z_{mn}^{\times}
\cong
\mathbb Z_m^\times
\times
\mathbb Z_n^\times.
\]

Taking cardinalities gives:

\[
\varphi(mn)
=
\varphi(m)\varphi(n).
\]

---

## Prime-factorization formula

Suppose

\[
n
=
\prod_{i=1}^{r}
p_i^{\alpha_i}
\]

is the prime factorization of \(n\).

Using the prime-power formula together with multiplicativity:

\[
\varphi(n)
=
\prod_{i=1}^{r}
p_i^{\alpha_i-1}(p_i-1).
\]

Equivalently,

\[
\boxed{
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right).
}
\]

The product runs over the **distinct prime divisors** of \(n\).

### Example: \(\varphi(360)\)

Factor:

\[
360
=
2^3\cdot3^2\cdot5.
\]

Therefore,

\[
\begin{aligned}
\varphi(360)
&=
360
\left(1-\frac12\right)
\left(1-\frac13\right)
\left(1-\frac15\right)\\
&=
360
\cdot
\frac12
\cdot
\frac23
\cdot
\frac45\\
&=
96.
\end{aligned}
\]

Thus:

\[
\boxed{
\varphi(360)=96.
}
\]

### A larger example

Take:

\[
304920
=
2^3
\cdot
3^2
\cdot
5
\cdot
7
\cdot
11^2.
\]

Then:

\[
\begin{aligned}
\varphi(304920)
&=
304920
\left(1-\frac12\right)
\left(1-\frac13\right)
\left(1-\frac15\right)
\left(1-\frac17\right)
\left(1-\frac1{11}\right)\\
&=
304920
\cdot
\frac12
\cdot
\frac23
\cdot
\frac45
\cdot
\frac67
\cdot
\frac{10}{11}\\
&=
63360.
\end{aligned}
\]

Therefore,

\[
\boxed{
\varphi(304920)=63360.
}
\]

---

## Euler's theorem

We now have:

\[
|\mathbb Z_n^\times|
=
\varphi(n).
\]

Take any element

\[
a\in\mathbb Z_n^\times.
\]

By Lagrange's theorem,

\[
\operatorname{ord}_n(a)
\mid
\varphi(n).
\]

So there exists an integer \(k\) such that

\[
\varphi(n)
=
k\operatorname{ord}_n(a).
\]

Since

\[
a^{\operatorname{ord}_n(a)}
\equiv1\pmod n,
\]

we get:

\[
a^{\varphi(n)}
=
\left(
a^{\operatorname{ord}_n(a)}
\right)^k
\equiv
1^k
\equiv
1
\pmod n.
\]

Therefore:

\[
\boxed{
a^{\varphi(n)}
\equiv1
\pmod n
\qquad
\text{whenever }
\gcd(a,n)=1.
}
\]

This is **Euler's theorem**.

The theorem is therefore not an isolated exponentiation trick.

It follows directly from the finite-group structure of

\[
\mathbb Z_n^\times.
\]

### Fermat's little theorem as a special case

If \(p\) is prime,

\[
\varphi(p)=p-1.
\]

So Euler's theorem becomes:

\[
a^{p-1}
\equiv1
\pmod p
\]

for every

\[
a\not\equiv0\pmod p.
\]

That is Fermat's little theorem.

The progression is:

\[
\boxed{
\mathbb Z_n^\times
\rightarrow
\varphi(n)
\rightarrow
\text{element orders}
\rightarrow
\text{Euler's theorem}
\rightarrow
\text{Fermat's little theorem}.
}
\]

---

## A connection to Carmichael's function

Euler's theorem guarantees:

\[
a^{\varphi(n)}
\equiv1\pmod n
\]

for every unit \(a\).

But \(\varphi(n)\) is not always the smallest exponent that works simultaneously for every element.

The **Carmichael function**

\[
\lambda(n)
\]

captures this more precisely.

It is the exponent of the finite group

\[
\mathbb Z_n^\times,
\]

which means:

\[
\boxed{
\lambda(n)
=
\operatorname{lcm}
\{
\operatorname{ord}_n(a):
a\in\mathbb Z_n^\times
\}.
}
\]

Consequently,

\[
a^{\lambda(n)}
\equiv1\pmod n
\]

for every unit \(a\), and generally

\[
\lambda(n)\mid\varphi(n).
\]

This explains why the RSA relation is more precisely written using

\[
\lambda(N)
\]

rather than necessarily \(\varphi(N)\).

For two distinct odd primes,

\[
N=pq,
\]

we have:

\[
\lambda(N)
=
\operatorname{lcm}(p-1,q-1).
\]

So the distinction is:

```text
φ(n)
    = number of units modulo n

λ(n)
    = common exponent controlling
      all unit orders modulo n
```

Both functions describe the same multiplicative group from different perspectives.

---

## Computational examples

### A naive implementation

The definition can be translated directly into Python:

```python
from math import gcd


def phi_naive(n):
    if n < 1:
        raise ValueError("n must be positive")

    return sum(
        1
        for a in range(1, n + 1)
        if gcd(a, n) == 1
    )
```

Examples:

```python
assert phi_naive(1) == 1
assert phi_naive(5) == 4
assert phi_naive(10) == 4
assert phi_naive(12) == 4
assert phi_naive(14) == 6
```

This implementation is transparent, but inefficient for large \(n\).

It checks every candidate individually.

### Computing from known prime factors

If the distinct prime factors of \(n\) are known, we can use:

\[
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right).
\]

An integer-only implementation is:

```python
def phi_from_prime_factors(n, prime_factors):
    result = n

    for p in prime_factors:
        result -= result // p

    return result
```

For:

```python
n = 360

phi = phi_from_prime_factors(
    n,
    prime_factors=[2, 3, 5],
)

print(phi)

assert phi == 96
```

### Computing element orders

For small educational examples:

```python
from math import gcd


def multiplicative_order(a, n):
    if gcd(a, n) != 1:
        raise ValueError(
            "a must be invertible modulo n"
        )

    value = 1

    for k in range(1, phi_naive(n) + 1):
        value = (value * a) % n

        if value == 1:
            return k

    raise RuntimeError("order not found")
```

Then:

```python
assert multiplicative_order(3, 10) == 4
assert multiplicative_order(9, 10) == 2
```

The upper bound

\[
\varphi(n)
\]

works because the element order must divide the group order.

For serious computation, we would use more efficient algorithms and exploit the factorization of the relevant group order.

---

## SageMath

SageMath exposes the arithmetic directly.

```python
euler_phi(360)
```

returns:

```text
96
```

For the multiplicative order:

```python
R = Integers(10)

a = R(3)

print(a.multiplicative_order())
```

Output:

```text
4
```

We can inspect the powers:

```python
[
    a**i
    for i in range(1, 9)
]
```

which visibly exposes the periodicity.

SageMath is particularly convenient here because `R(3)` is represented as an element of the modular ring rather than as an ordinary unstructured integer.

---

## Python with SymPy

SymPy provides Euler's totient directly:

```python
from sympy.functions.combinatorial.numbers import totient

print(totient(360))
```

Output:

```text
96
```

For exploratory mathematics, built-in computer-algebra functions are normally preferable to repeatedly implementing the naive count.

The value of the naive implementation is educational:

\[
\text{definition}
\rightarrow
\text{algorithm}.
\]

The value of the optimized implementation is practical:

\[
\text{arithmetic structure}
\rightarrow
\text{efficient computation}.
\]

---

## A few deeper facts

Euler's totient function looks elementary, but its global behavior quickly leads into analytic number theory.

### Parity

For every

\[
n>2,
\]

we have:

\[
\boxed{
\varphi(n)\text{ is even}.
}
\]

One way to see this is that if

\[
a\in\mathbb Z_n^\times,
\]

then

\[
-a\in\mathbb Z_n^\times.
\]

For \(n>2\), a unit cannot satisfy

\[
a\equiv-a\pmod n
\]

unless special trivial conditions occur, so units pair naturally as

\[
a
\longleftrightarrow
-a.
\]

Hence their number is even.

### Average behavior

The summatory totient function satisfies the asymptotic relation

\[
\boxed{
\sum_{k\le x}\varphi(k)
\sim
\frac{3}{\pi^2}x^2.
}
\]

Consequently, the average of the first \(n\) values is asymptotically

\[
\frac1n
\sum_{k=1}^{n}
\varphi(k)
\sim
\frac{3}{\pi^2}n.
\]

This is an interesting example of the constant

\[
\frac{6}{\pi^2}
\]

that appears in coprimality problems entering the analysis indirectly, while the summatory totient constant is

\[
\frac{3}{\pi^2}.
\]

### Dirichlet generating function

For

\[
\operatorname{Re}(s)>2,
\]

Euler's totient function satisfies:

\[
\boxed{
\sum_{n=1}^{\infty}
\frac{\varphi(n)}{n^s}
=
\frac{\zeta(s-1)}{\zeta(s)}.
}
\]

This connects an elementary counting function to the Riemann zeta function and the analytic structure of multiplicative arithmetic functions.

We do not need these analytic results for introductory cryptography, but they are useful reminders that even familiar arithmetic functions lead very quickly into deeper number theory.

---

## Open problems around the totient

Euler's totient function also appears in several classical open problems.

### Carmichael's totient-function conjecture

Carmichael's conjecture asks whether a value of the totient function can ever occur **exactly once**.

Equivalently, it conjectures that for every positive integer \(n\), there exists some

\[
m\neq n
\]

such that

\[
\varphi(m)=\varphi(n).
\]

No counterexample is known.

The problem remains open.

Computational and theoretical work has shown that any counterexample would have to be extraordinarily large.

This problem should not be confused with **Carmichael numbers** or with the **Carmichael function**

\[
\lambda(n).
\]

They are related historically by name, but they are different mathematical objects.

### Lehmer's totient problem

For every prime \(p\),

\[
\varphi(p)=p-1.
\]

Therefore:

\[
\varphi(p)\mid(p-1).
\]

Lehmer asked whether a composite integer

\[
n>1
\]

could also satisfy:

\[
\boxed{
\varphi(n)\mid(n-1).
}
\]

No such composite integer is currently known.

Any hypothetical example would have to satisfy strong arithmetic restrictions, but the problem remains open.

These questions are not necessary for using Euler's function in cryptography.

They are included because they show how much mathematical structure can hide behind a function with such a simple definition.

---

## Why this matters in cryptography

The main cryptographic connection is not simply that RSA contains the symbol \(\varphi\).

It is that Euler's function describes the size of the multiplicative group in which many classical cryptographic computations live.

### RSA

For

\[
N=pq
\]

with distinct primes,

\[
\varphi(N)
=
(p-1)(q-1).
\]

Textbook RSA is often introduced by choosing \(e\) so that

\[
\gcd(e,\varphi(N))=1
\]

and then computing:

\[
d
\equiv
e^{-1}
\pmod{\varphi(N)}.
\]

A more precise modern formulation uses:

\[
\lambda(N)
=
\operatorname{lcm}(p-1,q-1),
\]

but the totient remains essential for understanding the multiplicative structure of the modulus.

### Diffie-Hellman

In finite-field Diffie-Hellman, we care not only about the size of an ambient multiplicative group but also about the order of the particular subgroup generated by \(g\).

This is exactly why the distinction

\[
|G|
\]

versus

\[
\operatorname{ord}(g)
\]

matters cryptographically.

### Small-subgroup attacks

If an attacker can force a secret exponentiation into an element \(T\) of small order

\[
s,
\]

then

\[
T^d
=
T^{d\bmod s}.
\]

The attack therefore depends directly on **element order**.

So a concept that looks like pure group theory becomes an implementation-security boundary.

### Primality testing

For prime \(p\),

\[
\varphi(p)=p-1,
\]

and Euler's theorem becomes Fermat's little theorem:

\[
a^{p-1}\equiv1\pmod p.
\]

That relation lies behind Fermat tests and helps motivate stronger tests such as Miller-Rabin.

---

## Practice and checkpoint

### Exercise 1 — Compute small totients

Compute:

\[
\varphi(8),
\qquad
\varphi(15),
\qquad
\varphi(20).
\]

Do it first by listing the units, then verify using the prime-factorization formula.

### Exercise 2 — Prime powers

Use:

\[
\varphi(p^k)
=
p^{k-1}(p-1)
\]

to calculate:

\[
\varphi(2^{10}),
\]

and

\[
\varphi(7^4).
\]

### Exercise 3 — Multiplicativity

Compute:

\[
\varphi(35)
\]

in two ways:

1. directly from the prime-factorization formula;
2. from
   \[
   \varphi(5)\varphi(7).
   \]

Why is this legal?

Now ask whether the same argument applies directly to:

\[
\varphi(12)
=
\varphi(3)\varphi(4).
\]

### Exercise 4 — Element order

Compute the successive powers of \(2\) modulo \(7\):

\[
2^1,2^2,2^3,\ldots
\]

and determine:

\[
\operatorname{ord}_7(2).
\]

Verify that:

\[
\operatorname{ord}_7(2)
\mid
\varphi(7).
\]

### Exercise 5 — Different orders in one group

List all elements of:

\[
\mathbb Z_{10}^{\times}.
\]

Determine the order of each one.

Which elements generate the whole group?

### Exercise 6 — A noncyclic example

Study:

\[
\mathbb Z_8^\times.
\]

Verify that:

\[
|\mathbb Z_8^\times|
=
4,
\]

but no element has order \(4\).

What does this tell you about the difference between group order and element order?

### Exercise 7 — Euler's theorem

Choose:

\[
a=7,
\qquad
n=20.
\]

First verify:

\[
\gcd(7,20)=1.
\]

Then compute:

\[
\varphi(20)
\]

and verify:

\[
7^{\varphi(20)}
\equiv1\pmod{20}.
\]

### Reader checkpoint

You should now be able to explain:

1. What Euler's totient function counts.
2. Why
   \[
   \varphi(n)=|\mathbb Z_n^\times|.
   \]
3. Why
   \[
   \varphi(p)=p-1
   \]
   for prime \(p\).
4. Why
   \[
   \varphi(p^k)=p^k-p^{k-1}.
   \]
5. What it means for \(\varphi\) to be multiplicative.
6. Why multiplicative does not mean completely multiplicative.
7. What
   \[
   \operatorname{ord}_n(a)
   \]
   means.
8. Why an element order must divide the group order.
9. Why a group of order \(m\) need not contain an element of order \(m\).
10. How Euler's theorem follows from finite-group structure.
11. How Fermat's little theorem appears as the prime-modulus case.
12. Why \(\lambda(n)\) can be smaller than \(\varphi(n)\).
13. Why element order matters directly in Diffie-Hellman and subgroup attacks.

If those distinctions are clear, then Euler's function is no longer merely a formula for counting coprime integers.

It is a way of measuring and understanding the multiplicative structure of modular arithmetic.

---

## References and further reading

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical reference for Euler's function, multiplicative arithmetic functions, orders, and elementary number theory.

**Tom M. Apostol**,  
*Introduction to Analytic Number Theory.*

Particularly useful for the arithmetic and analytic properties of Euler's totient function.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

A strong bridge between finite groups, computational number theory, and cryptographic applications.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Useful for seeing how group orders, element orders, Euler's theorem, and related number theory appear inside concrete cryptographic systems.

**R. D. Carmichael**,  
*On Euler's \(\phi\)-Function*, 1922.

A historical reference associated with the conjecture concerning repeated values of the totient function.

**D. H. Lehmer**,  
*On Euler's Totient Function*, 1932.

The classical source of what is now known as Lehmer's totient problem.

---

## Where this leads

We now have several layers of structure:

\[
\mathbb Z_n
\supset
\mathbb Z_n^\times,
\]

\[
|\mathbb Z_n^\times|
=
\varphi(n),
\]

and for every unit \(a\),

\[
\operatorname{ord}_n(a)
\mid
\varphi(n).
\]

From that one picture emerge:

\[
a^{\varphi(n)}
\equiv1\pmod n,
\]

Euler's theorem,

\[
a^{p-1}
\equiv1\pmod p,
\]

Fermat's little theorem,

and the questions of:

- which elements generate a group,
- when multiplicative groups are cyclic,
- how large a subgroup is,
- how powers repeat,
- why subgroup order matters cryptographically.

So the natural continuation is to study **cyclic groups, generators, multiplicative orders, Euler's theorem, Fermat's little theorem, and primitive roots** in greater depth.
