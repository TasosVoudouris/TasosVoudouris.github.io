---
title: "Chinese Remainder Theorem: Reference and Implementation"
description: "A theorem-to-code reference for the Chinese Remainder Theorem, including constructive reconstruction, uniqueness, generalized compatibility, RSA connections, and Python implementations."
pubDate: "2025-04-23"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Cryptographic Engineering"
tags:
  - "crt"
  - "chinese-remainder-theorem"
  - "modular-arithmetic"
  - "python"
difficulty: "Intermediate"
series: "Elementary Number Theory Reference"
seriesOrder: 3
draft: false
---

> "We have a number of things, but we do not know exactly how many.  
> If we count them by threes we have two left over.  
> If we count them by fives we have three left over.  
> If we count them by sevens we have two left over.  
> How many things are there?"
>
> — *Sunzi Suanjing*

The Chinese Remainder Theorem is one of the most useful reconstruction results in elementary number theory.

It answers a deceptively simple question:

> If we know the remainder of an unknown integer modulo several different moduli, can we reconstruct the integer?

When the moduli are pairwise coprime, the answer is remarkably clean.

A system such as

$$
x\equiv a_1\pmod{m_1},
$$

$$
x\equiv a_2\pmod{m_2},
$$

$$
\vdots
$$

$$
x\equiv a_k\pmod{m_k}
$$

determines one unique residue class modulo

$$
M=m_1m_2\cdots m_k.
$$

So CRT provides a bridge between:

$$
\text{many local modular views}
$$

and

$$
\text{one global residue}.
$$

This same structure appears in RSA acceleration, fault attacks, residue-number representations, modular computation, polynomial rings, and modern cryptographic engineering.

---

## Table of Contents

- [A preliminary congruence result](#a-preliminary-congruence-result)
- [Chinese Remainder Theorem](#chinese-remainder-theorem)
- [Why the solution is unique](#why-the-solution-is-unique)
- [Constructive CRT](#constructive-crt)
- [A complete example](#a-complete-example)
- [Direct Python implementation](#direct-python-implementation)
- [Incremental reconstruction](#incremental-reconstruction)
- [A useful special case](#a-useful-special-case)
- [What if the moduli are not coprime?](#what-if-the-moduli-are-not-coprime)
- [Cryptographic applications](#cryptographic-applications)
- [SageMath](#sagemath)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Where this leads](#where-this-leads)

---

## A preliminary congruence result

Before CRT, it is useful to remember how a single linear congruence behaves.

Consider

$$
ax\equiv b\pmod n.
$$

Let

$$
d=\gcd(a,n).
$$

Then the congruence has a solution if and only if

$$
d\mid b.
$$

When this condition holds, there are exactly $d$ incongruent solutions modulo $n$.

Thus:

$$
\boxed{
ax\equiv b\pmod n
\text{ is solvable}
\iff
\gcd(a,n)\mid b.
}
$$

The particularly important case is:

$$
\gcd(a,n)=1.
$$

Then $a$ is invertible modulo $n$, and the congruence has exactly one solution modulo $n$:

$$
x
\equiv
a^{-1}b
\pmod n.
$$

This inverse-based reconstruction is exactly what we will use inside CRT.

---

## Chinese Remainder Theorem

Let

$$
m_1,m_2,\ldots,m_k
$$

be pairwise coprime positive integers:

$$
\gcd(m_i,m_j)=1
\qquad
\text{for }i\neq j.
$$

Let

$$
a_1,a_2,\ldots,a_k
\in\mathbb Z.
$$

Then the simultaneous system

$$
\begin{aligned}
x &\equiv a_1 \pmod{m_1},\\
x &\equiv a_2 \pmod{m_2},\\
&\vdots\\
x &\equiv a_k \pmod{m_k}
\end{aligned}
$$

has a solution.

Moreover, that solution is unique modulo

$$
\boxed{
M
=
m_1m_2\cdots m_k.
}
$$

So there is exactly one residue class

$$
[x]_M
$$

satisfying all of the congruences simultaneously.

The theorem does **not** normally identify one absolute integer.

It identifies:

$$
\boxed{
x\pmod M.
}
$$

If one solution is $x_0$, then every integer solution has the form

$$
x=x_0+tM,
\qquad
t\in\mathbb Z.
$$

---

## Why the solution is unique

Suppose two integers $x$ and $y$ both satisfy all of the congruences.

Then:

$$
x\equiv y\pmod{m_i}
$$

for every $i$.

Therefore:

$$
m_i\mid(x-y)
$$

for every modulus.

Because the moduli are pairwise coprime,

$$
m_1m_2\cdots m_k
\mid
(x-y).
$$

Hence:

$$
M\mid(x-y).
$$

Equivalently,

$$
\boxed{
x\equiv y\pmod M.
}
$$

So the solution is unique modulo the product.

This is the uniqueness half of CRT.

The more interesting part computationally is how to actually construct that solution.

---

## Constructive CRT

Let

$$
M
=
\prod_{i=1}^{k}m_i.
$$

For each modulus define

$$
M_i
=
\frac{M}{m_i}.
$$

Because all moduli are pairwise coprime,

$$
\gcd(M_i,m_i)=1.
$$

Therefore $M_i$ has an inverse modulo $m_i$.

Define:

$$
y_i
=
M_i^{-1}\pmod{m_i}.
$$

Then:

$$
M_i y_i
\equiv1\pmod{m_i}.
$$

But for every $j\neq i$,

$$
m_j\mid M_i,
$$

so:

$$
M_i y_i
\equiv0\pmod{m_j}.
$$

Thus each term

$$
M_i y_i
$$

acts like a modular selector:

```text
mod mi  → 1

mod mj  → 0
          for every j ≠ i
```

Now multiply each selector by the required residue $a_i$:

$$
a_iM_i y_i.
$$

Finally add them:

$$
\boxed{
x
\equiv
\sum_{i=1}^{k}
a_iM_i y_i
\pmod M.
}
$$

That is the standard constructive CRT formula.

The theorem therefore does not merely guarantee that a solution exists.

It gives us an explicit reconstruction algorithm.

---

## A complete example

Find $x$ satisfying:

$$
\begin{aligned}
x &\equiv5\pmod{13},\\
x &\equiv8\pmod{17},\\
x &\equiv15\pmod{29}.
\end{aligned}
$$

The moduli are pairwise coprime, so CRT applies.

First compute:

$$
M
=
13\cdot17\cdot29
=
6409.
$$

Now:

$$
M_1
=
\frac{6409}{13}
=
493,
$$

$$
M_2
=
\frac{6409}{17}
=
377,
$$

and

$$
M_3
=
\frac{6409}{29}
=
221.
$$

We now compute the inverses.

### First selector

Modulo $13$,

$$
493\equiv12\pmod{13}.
$$

Since:

$$
12\cdot12
=
144
\equiv1\pmod{13},
$$

we have:

$$
y_1=12.
$$

### Second selector

Modulo $17$,

$$
377\equiv3\pmod{17}.
$$

Since:

$$
3\cdot6
=
18
\equiv1\pmod{17},
$$

we obtain:

$$
y_2=6.
$$

### Third selector

Modulo $29$,

$$
221\equiv18\pmod{29}.
$$

And:

$$
18\cdot21
=
378
\equiv1\pmod{29}.
$$

Therefore:

$$
y_3=21.
$$

The reconstruction data can be summarized as:

| $i$ | $a_i$ | $m_i$ | $M_i$ | $y_i=M_i^{-1}\pmod{m_i}$ | $a_iM_i y_i$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | 13 | 493 | 12 | 29580 |
| 2 | 8 | 17 | 377 | 6 | 18096 |
| 3 | 15 | 29 | 221 | 21 | 69615 |

Now add:

$$
x
\equiv
29580+18096+69615
\pmod{6409}.
$$

So:

$$
x
\equiv
117291
\pmod{6409}.
$$

Reducing:

$$
117291\bmod6409
=
1929.
$$

Therefore:

$$
\boxed{
x\equiv1929\pmod{6409}.
}
$$

Verify:

$$
1929\bmod13=5,
$$

$$
1929\bmod17=8,
$$

and:

$$
1929\bmod29=15.
$$

Everything matches.

---

## Direct Python implementation

The constructive proof translates almost directly into code.

```python
from math import prod


def crt(residues, moduli):
    if len(residues) != len(moduli):
        raise ValueError(
            "residues and moduli must have the same length"
        )

    M = prod(moduli)

    x = 0

    for a_i, m_i in zip(residues, moduli):
        M_i = M // m_i
        y_i = pow(M_i, -1, m_i)

        x += a_i * M_i * y_i

    return x % M, M
```

Now:

```python
solution, modulus = crt(
    residues=[2, 3, 2],
    moduli=[3, 5, 7],
)

print(solution)
print(modulus)
```

returns:

```text
23
105
```

So:

$$
x\equiv23\pmod{105}.
$$

For our larger example:

```python
solution, modulus = crt(
    residues=[5, 8, 15],
    moduli=[13, 17, 29],
)

print(solution)
print(modulus)
```

returns:

```text
1929
6409
```

We should verify the result explicitly:

```python
assert solution % 13 == 5
assert solution % 17 == 8
assert solution % 29 == 15
```

### Making the assumptions explicit

The direct implementation assumes pairwise-coprime moduli.

A defensive educational implementation can check this:

```python
from math import gcd, prod


def crt_pairwise_coprime(residues, moduli):
    if len(residues) != len(moduli):
        raise ValueError(
            "residues and moduli must have the same length"
        )

    if not moduli:
        raise ValueError(
            "at least one congruence is required"
        )

    for i in range(len(moduli)):
        if moduli[i] <= 0:
            raise ValueError(
                "moduli must be positive"
            )

        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(
                    "moduli must be pairwise coprime"
                )

    M = prod(moduli)
    x = 0

    for a_i, m_i in zip(residues, moduli):
        M_i = M // m_i
        y_i = pow(M_i, -1, m_i)

        x += a_i * M_i * y_i

    return x % M, M
```

Now the assumptions made by the theorem are also visible in the implementation.

---

## Incremental reconstruction

There is another useful way to implement CRT.

Instead of constructing every selector at once, we can combine congruences one at a time.

Suppose we already know:

$$
x\equiv a\pmod m.
$$

Then every possible solution has the form:

$$
x=a+mt.
$$

Now suppose we also require:

$$
x\equiv b\pmod n.
$$

Substitute:

$$
a+mt
\equiv
b
\pmod n.
$$

Therefore:

$$
mt
\equiv
b-a
\pmod n.
$$

If:

$$
\gcd(m,n)=1,
$$

then $m$ has an inverse modulo $n$, so:

$$
t
\equiv
(b-a)m^{-1}
\pmod n.
$$

Once $t$ is known, the two congruences become one congruence modulo:

$$
mn.
$$

That gives an incremental implementation:

```python
from math import gcd


def crt_incremental(residues, moduli):
    if len(residues) != len(moduli):
        raise ValueError(
            "residues and moduli must have the same length"
        )

    x = 0
    M = 1

    for residue, modulus in zip(
        residues,
        moduli,
    ):
        if gcd(M, modulus) != 1:
            raise ValueError(
                "moduli must be pairwise coprime"
            )

        correction = (
            (residue - x)
            *
            pow(M, -1, modulus)
        ) % modulus

        x += M * correction
        M *= modulus

        x %= M

    return x, M
```

For example:

```python
print(
    crt_incremental(
        [2, 3, 2],
        [3, 5, 7],
    )
)
```

returns:

```text
(23, 105)
```

And:

```python
print(
    crt_incremental(
        [5, 8, 15],
        [13, 17, 29],
    )
)
```

returns:

```text
(1929, 6409)
```

The two implementations correspond to two different views of the theorem:

```text
direct CRT
    ↓
construct modular basis selectors
```

versus:

```text
incremental CRT
    ↓
merge one congruence at a time
```

Both express the same mathematics.

---

## A useful special case

Suppose:

$$
\gcd(n_1,n_2)=1
$$

and:

$$
x\equiv a\pmod{n_1},
$$

$$
x\equiv a\pmod{n_2}.
$$

Then:

$$
n_1\mid(x-a)
$$

and:

$$
n_2\mid(x-a).
$$

Because $n_1$ and $n_2$ are coprime,

$$
n_1n_2\mid(x-a).
$$

Therefore:

$$
\boxed{
x\equiv a\pmod{n_1n_2}.
}
$$

This small result appears frequently when proving that two modular computations together determine a result modulo a product.

For example, it is exactly the reasoning used when we say:

```text
correct modulo p
+
correct modulo q
        ↓
correct modulo pq
```

in RSA.

---

## What if the moduli are not coprime?

Pairwise coprimality gives the cleanest version of CRT, but it is not the most general one.

Consider:

$$
x\equiv a\pmod m,
$$

$$
x\equiv b\pmod n.
$$

Let:

$$
d=\gcd(m,n).
$$

A solution exists if and only if:

$$
\boxed{
a\equiv b\pmod d.
}
$$

Equivalently:

$$
d\mid(a-b).
$$

If this compatibility condition holds, the solution is unique modulo:

$$
\boxed{
\operatorname{lcm}(m,n).
}
$$

### Compatible example

Consider:

$$
x\equiv2\pmod6,
$$

$$
x\equiv5\pmod9.
$$

Since:

$$
\gcd(6,9)=3,
$$

check the residues modulo $3$:

$$
2\equiv2\pmod3,
$$

and:

$$
5\equiv2\pmod3.
$$

They are compatible.

Indeed,

$$
x=14
$$

satisfies:

$$
14\equiv2\pmod6
$$

and:

$$
14\equiv5\pmod9.
$$

The combined solution is unique modulo:

$$
\operatorname{lcm}(6,9)=18.
$$

Therefore:

$$
\boxed{
x\equiv14\pmod{18}.
}
$$

### Incompatible example

Now consider:

$$
x\equiv1\pmod4,
$$

$$
x\equiv2\pmod6.
$$

Here:

$$
\gcd(4,6)=2.
$$

But:

$$
1\not\equiv2\pmod2.
$$

So the system has no solution.

This generalized viewpoint is useful because it shows that pairwise coprimality is not arbitrary.

It guarantees compatibility automatically and makes every required inverse exist.

---

## Cryptographic applications

CRT appears repeatedly in cryptography because cryptographic arithmetic often moves between:

$$
\text{one large arithmetic object}
$$

and:

$$
\text{several smaller modular components}.
$$

### RSA

Let:

$$
N=pq.
$$

Instead of computing a private operation directly modulo $N$, CRT-RSA computes independently modulo:

$$
p
$$

and:

$$
q.
$$

For a private exponent $d$, one typically derives:

$$
d_P=d\bmod(p-1),
$$

$$
d_Q=d\bmod(q-1),
$$

and computes:

$$
S_p=M^{d_P}\bmod p,
$$

$$
S_q=M^{d_Q}\bmod q.
$$

CRT then reconstructs the unique:

$$
S\bmod N
$$

satisfying both congruences.

The result is significantly faster than one large private exponentiation modulo $N$.

### CRT-RSA fault attacks

The same decomposition creates an important implementation-security lesson.

If a faulty RSA computation remains correct modulo $q$ but becomes incorrect modulo $p$, then the correct and faulty results satisfy:

$$
S\equiv\widetilde S\pmod q.
$$

Therefore:

$$
q\mid(S-\widetilde S).
$$

A GCD can then reveal the hidden factor:

$$
\gcd(S-\widetilde S,N)=q
$$

in the useful fault case.

Thus the same CRT structure provides both:

```text
performance optimization
```

and:

```text
fault-attack surface
```

depending on implementation behavior.

### Combining leaked residues

Suppose a reused secret exponent $d$ leaks:

$$
d\bmod3,
$$

$$
d\bmod4,
$$

and:

$$
d\bmod5.
$$

Because:

$$
3,4,5
$$

are pairwise coprime, CRT combines them into one residue modulo:

$$
60.
$$

Small pieces of modular information can therefore become a much larger piece of information about the secret.

### Residue-number representations

Large integers can be represented by several smaller residues:

$$
x
\longmapsto
(
x\bmod m_1,
x\bmod m_2,\ldots
).
$$

Arithmetic can then be carried out independently in the smaller modular components.

CRT reconstructs the global value when required.

This viewpoint appears in high-performance arithmetic and cryptographic engineering.

### Polynomial and ring CRT

CRT is not restricted to ordinary integers.

Analogous decomposition theorems exist for polynomial rings and more general algebraic rings.

These decompositions are important in computational algebra and also appear in modern lattice-based and homomorphic-encryption implementations, where arithmetic is often split across several moduli.

So the broader idea is:

$$
\boxed{
\text{decompose}
\rightarrow
\text{compute locally}
\rightarrow
\text{reconstruct}.
}
$$

---

## SageMath

SageMath provides CRT directly.

For two congruences:

```python
crt(
    2,
    3,
    3,
    5,
)
```

and for lists of residues and moduli, depending on the SageMath interface being used, CRT utilities can reconstruct simultaneous systems directly.

For example, the mathematical target:

```text
x ≡ 2 mod 3
x ≡ 3 mod 5
x ≡ 2 mod 7
```

should return the representative:

```text
23
```

corresponding to:

$$
x\equiv23\pmod{105}.
$$

For learning, however, the custom implementation remains valuable because it exposes exactly where:

- the product $M$,
- the partial products $M_i$,
- and the modular inverses $M_i^{-1}$

enter the construction.

---

## Practice and checkpoint

### Exercise 1 — The classical system

Solve:

$$
x\equiv2\pmod3,
$$

$$
x\equiv3\pmod5,
$$

$$
x\equiv2\pmod7.
$$

Construct the $M_i$ and $y_i$ values explicitly.

### Exercise 2 — Two moduli

Solve:

$$
x\equiv4\pmod7,
$$

$$
x\equiv9\pmod{11}.
$$

Give the final answer modulo:

$$
77.
$$

### Exercise 3 — Verify reconstruction

For:

$$
x\equiv1929\pmod{6409},
$$

verify all three original congruences:

$$
x\equiv5\pmod{13},
$$

$$
x\equiv8\pmod{17},
$$

$$
x\equiv15\pmod{29}.
$$

### Exercise 4 — Generalized CRT

Determine whether:

$$
x\equiv4\pmod6,
$$

$$
x\equiv10\pmod{14}
$$

is compatible.

Start by computing:

$$
\gcd(6,14).
$$

If a solution exists, determine its modulus.

### Exercise 5 — No solution

Explain why:

$$
x\equiv1\pmod6,
$$

$$
x\equiv2\pmod9
$$

has no solution.

### Exercise 6 — Implementation invariants

For your Python implementation, verify that:

```python
solution % modulus_i == residue_i % modulus_i
```

for every input congruence.

Do not merely trust the reconstructed number.

Test the theorem's defining invariants.

### Reader checkpoint

You should now be able to explain:

1. What CRT reconstructs.
2. Why the answer is a residue class rather than one absolute integer.
3. Why pairwise coprimality matters.
4. Why each
   $$
   M_i^{-1}\pmod{m_i}
   $$
   exists.
5. Why
   $$
   M_i y_i
   $$
   behaves like a modular selector.
6. Why the reconstructed solution is unique modulo
   $$
   M=\prod_i m_i.
   $$
7. How incremental CRT reconstruction works.
8. What compatibility condition replaces pairwise coprimality in the generalized theorem.
9. Why RSA benefits from CRT.
10. Why the same CRT decomposition creates an important fault-attack surface.
11. How several small modular leaks can be combined into larger information.

At that point CRT should no longer feel like a mysterious reconstruction formula.

It becomes a general arithmetic pattern:

$$
\boxed{
\text{local information}
\longleftrightarrow
\text{global structure}.
}
$$

---

## References and further reading

**Kenneth H. Rosen**,  
*Elementary Number Theory and Its Applications.*

A clear introductory reference for systems of congruences and the Chinese Remainder Theorem.

**Ivan Niven, Herbert S. Zuckerman, and Hugh L. Montgomery**,  
*An Introduction to the Theory of Numbers.*

A classical treatment of elementary congruence theory and CRT.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Particularly useful for computational treatments of modular arithmetic and reconstruction.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Useful for connecting CRT with RSA and practical cryptographic arithmetic.

---

## Where this leads

CRT gives us a particularly powerful view of modular arithmetic:

$$
\text{large modulus}
\longleftrightarrow
\text{several smaller moduli}.
$$

That idea will return repeatedly.

In RSA:

$$
N=pq
$$

is decomposed into arithmetic modulo $p$ and $q$.

In attacks, several leaked residues can be reconstructed into information about one secret.

In modern arithmetic implementations, large computations can be distributed across several smaller modular channels.

And in more advanced algebra, CRT reappears for polynomial rings and quotient-ring decompositions.

The theorem is therefore not merely a trick for solving simultaneous congruences.

It is one of the fundamental decomposition and reconstruction principles of computational number theory.
