---
title: "Discrete Logarithms I: The DLP and ECDLP"
description: "An introduction to discrete logarithms in additive and multiplicative groups, including the elliptic-curve discrete logarithm problem and its cryptographic role."
pubDate: "2025-05-26"
updatedDate: '2026-09-12'
topics:
- "Discrete Logarithms"
- "Mathematical Foundations"
- "Public-Key Cryptography"
tags:
- "discrete-logarithm"
- "dlp"
- "ecdlp"
- "groups"
difficulty: "Intermediate"
series: "Discrete Logarithm Algorithms"
seriesOrder: 1
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
We now now turn to one of the two fundamental computational problems underpinning modern public-key cryptography: the *Discrete Logarithm Problem (DLP)*. Alongside the Integer Factorization Problem, the DLP forms the cryptographic backbone of numerous protocols, including Diffie–Hellman key exchange, ElGamal encryption, and many digital signature schemes.

Before we formally state the problem, let’s first review some essential mathematical structures used in its definition.

## Additive and Multiplicative Groups

* An **additive group** is a set equipped with an addition operation. For any element $a$, its **additive inverse** $x$ satisfies:

  $$
  a + x = 0
  $$

  where $0$ is the identity element of the group.

* A **multiplicative group** is a set equipped with a multiplication operation. For any element $a$, its **multiplicative inverse** $x$ satisfies:

  $$
  a \cdot x = 1
  $$

  where $1$ is the identity element of the group.

The most common group in classical cryptography is the **multiplicative group of integers modulo $n$**, denoted:

$$
(\mathbb{Z}/n\mathbb{Z})^\times
$$

This group consists of all integers between 1 and $n-1$ that are coprime to $n$, with multiplication modulo $n$ as the group operation.

* Example: The group $(\mathbb{Z}/15\mathbb{Z})^\times$ consists of the elements:

  $$
  \{1, 2, 4, 7, 8, 11, 13, 14\}
  $$

These are the integers less than 15 that are **coprime** to 15. Their multiplication modulo 15 forms a group of order 8.



* The **order** of a group is the number of elements it contains.

  * Example: $|(\mathbb{Z}/15\mathbb{Z})^\times| = 8$
  * The additive group $\mathbb{Z}/10\mathbb{Z}$ has order 10.

* When $n = p$ is a **prime**, the ring $\mathbb{Z}/p\mathbb{Z}$ becomes a **finite field**, often denoted:

  $$
  \mathbb{F}_p \quad \text{or} \quad \mathrm{GF}(p)
  $$

  The **multiplicative group** of $\mathbb{F}_p$, that is $\mathbb{F}_p^\times$, has order $p-1$ and is a **cyclic group**.

> In fact, $\mathbb{F}_p^\times \cong \mathbb{Z}/(p-1)\mathbb{Z}$, which means it behaves like modular integers under addition, but now applied to exponents.
>

Below is a simple SageMath example: 

```python
sage: n = 15
sage: M = Zmod(n)
sage: euler_phi(15) # order of the multiplicative group of the ring Z_{15}*
8
sage: for i in range(1, n):
....:     if gcd(i,n) == 1:
....:         # i is in the multiplicative group of the ring Z_{15}*
....:         order = M(i).multiplicative_order()
....:         print(f'the number {i} has order {order} because {i}^{order} = {pow(i,order,n)}')
....:
the number 1 has order 1 because 1^1 = 1
the number 2 has order 4 because 2^4 = 1
the number 4 has order 2 because 4^2 = 1
the number 7 has order 4 because 7^4 = 1
the number 8 has order 4 because 8^4 = 1
the number 11 has order 2 because 11^2 = 1
the number 13 has order 4 because 13^4 = 1
the number 14 has order 2 because 14^2 = 1
```

Notice that the order of all elements (1,2,4) divides the order of the group which is 8. This is due to Lagrange’s Theorem that we refresh below: 

> Let G be a group. The order of the elements of G always divides the order of G.
>

Another simple SageMath example: 

```python
sage: p = 19
sage: F = GF(p)
sage: F.order() # the order of the additive group of the field F_{19}
19
sage: for i in range(1, p):
....:     if gcd(i,p) == 1:
....:         # i is in the multiplicative group of the field F_{19}
....:         order = F(i).multiplicative_order()
....:         print(f'the number {i} has order {order} because {i}^{order} = {pow(i,order,p)}')
....:
the number 1 has order 1 because 1^1 = 1
the number 2 has order 18 because 2^18 = 1
the number 3 has order 18 because 3^18 = 1
the number 4 has order 9 because 4^9 = 1
the number 5 has order 9 because 5^9 = 1
the number 6 has order 9 because 6^9 = 1
the number 7 has order 3 because 7^3 = 1
the number 8 has order 6 because 8^6 = 1
the number 9 has order 9 because 9^9 = 1
the number 10 has order 18 because 10^18 = 1
the number 11 has order 3 because 11^3 = 1
the number 12 has order 6 because 12^6 = 1
the number 13 has order 18 because 13^18 = 1
the number 14 has order 18 because 14^18 = 1
the number 15 has order 18 because 15^18 = 1
the number 16 has order 9 because 16^9 = 1
the number 17 has order 9 because 17^9 = 1
the number 18 has order 2 because 18^2 = 1
```

A *field* is more than just a group: it supports two operations—addition and multiplication—with the following properties:

* It is an *additive group* under $+$,
* Its nonzero elements form a *multiplicative group* under $\cdot$,
* There exist identity elements for both operations (0 and 1),
* Every nonzero element has a multiplicative inverse.

Finite fields are the setting where the Discrete Logarithm Problem is usually defined.

Next, we’ll formally define the Discrete Logarithm Problem and explore why it’s believed to be hard—and thus so central to cryptography.


## Discrete Logarithm Problem

Alongside integer factorization, DLP underpins the security of a wide range of cryptographic protocols, including *Diffie–Hellman key exchange*, *ElGamal encryption*, and *DSA* signature.

Let $G$ be a finite **cyclic group**, written multiplicatively, and let $g \in G$ be a **generator** of the group. Then the **Discrete Logarithm Problem** is defined as:

> **Given**: $G$, a generator $g$, and an element $a \in G$ such that $a = g^x$
> **Find**: the integer $x \in \mathbb{Z}$ such that
>$$g^x \equiv a \mod n$$


This problem is believed to be computationally hard in general, especially when the group order is large and the group is well-chosen.

A simple example with a brute-force approach. Find $x$ such that:

$$
3^x \equiv 5 \pmod{11}
$$

Try successive powers of 3 modulo 11:

* $x = 0$: $3^0 \equiv 1$
* $x = 1$: $3^1 \equiv 3$
* $x = 2$: $3^2 \equiv 9$
* $x = 3$: $3^3 \equiv 27 \equiv 5 \mod{11}$

So, $x = 3$ is one solution.
But it's *not unique*, e.g., $x = 8$ also works:

$$
3^8 \equiv 6561 \equiv 5 \mod{11}
$$

> Note: In general, if the group is not cyclic or the base is not a generator, *some values might not have a solution at all*.



Remember that a group is *cyclic* if it can be generated by a single element $g$. That is:

$$
G = \langle g \rangle = \{g^0, g^1, \ldots, g^{n-1}\}
$$

* Such an element $g$ is called a *generator* or *primitive root* (in modular arithmetic).
* Let’s check if $3$ is a generator mod 11:

$$
\begin{aligned}
3^0 &\equiv 1 \mod{11} \\
3^1 &\equiv 3 \\
3^2 &\equiv 9 \\
3^3 &\equiv 5 \\
3^4 &\equiv 4 \\
3^5 &\equiv 1 \Rightarrow \text{Cycle repeats}
\end{aligned}
$$

* The powers of 3 modulo 11 only generate a subset:

  $$
  \{1, 3, 9, 5, 4\}
  $$

  So **3 is not** a generator.

Now try $g = 2$:

$$
\begin{aligned}
2^0 &\equiv 1 \\
2^1 &\equiv 2 \\
2^2 &\equiv 4 \\
2^3 &\equiv 8 \\
2^4 &\equiv 5 \\
2^5 &\equiv 10 \\
2^6 &\equiv 9 \\
2^7 &\equiv 7 \\
2^8 &\equiv 3 \\
2^9 &\equiv 6 \\
2^{10} &\equiv 1 \\
\end{aligned}
$$

* The powers of 2 modulo 11 generate all nonzero elements:

  $$
  \mathbb{Z}_{11}^\times = \{1, 2, 3, \ldots, 10\}
  $$

So, **2 is a generator** of $\mathbb{Z}_{11}^\times$.

> If the base $g$ is a generator, then **a solution always exists** for any $a \in G$, and the discrete log is **well-defined modulo the group order**.


The DLP (and its elliptic curve variant, *ECDLP*) provides the security basis for several important protocols as stated above. They rely on the assumption that computing discrete exponentiation $g^x \mod p$ is easy, but reversing it (i.e., solving for $x$) is *computationally hard* without special knowledge (e.g., a trapdoor).


## Elliptic Curve Discrete Logarithm Problem (ECDLP)

Let $E$ be an elliptic curve defined over a finite field $\mathbb{F}_q$, and let $P \in E(\mathbb{F}_q)$ be a point of prime order. The ECDLP is defined as follows:

> **Given:** Points $P, Q \in E(\mathbb{F}_q)$, where $Q = [n]P$,
> **Find:** The integer $n \in \mathbb{Z}$ such that $Q = [n]P$.

ECDLP generalizes the classical DLP to the additive group of points on an elliptic curve. It is currently believed to be significantly harder than the DLP in comparable finite fields, which allows elliptic curve cryptography (ECC) to use smaller key sizes while maintaining equivalent levels of security.


The ECDLP forms the security basis for:

* *ECDH (Elliptic Curve Diffie–Hellman)*
* *ECDSA (Elliptic Curve Digital Signature Algorithm)*
* *EdDSA (Edwards-curve Digital Signature Algorithm)*
* *ECIES (Elliptic Curve Integrated Encryption Scheme)*

Both DLP and ECDLP share a common conceptual foundation: solving for an unknown exponent given a group, a generator, and a group element. The key distinction lies in the nature of the group:

* *DLP*: Operates in a *multiplicative* cyclic group, typically $\mathbb{Z}_p^*$ or subgroups of $\mathbb{F}_{p^k}^*$.
* *ECDLP*: Operates in the *additive* group of points on an elliptic curve $E(\mathbb{F}_q)$.

Despite their similarity, ECDLP offers much stronger security-per-bit than classical DLP. For example, breaking the DLP in $\mathbb{Z}_p^*$ with a 3072-bit modulus requires roughly the same effort as solving the ECDLP on a 256-bit elliptic curve. Because of these differences in complexity, ECC has become the preferred approach in modern cryptographic implementations, especially where bandwidth, key size, and efficiency are critical (e.g., mobile devices, IoT). 

In the upcoming parts, we gonna delve into some fascinating methods of "solving" the DLP/ECDLP faster than a bruteforce approach. Stay tuned!
