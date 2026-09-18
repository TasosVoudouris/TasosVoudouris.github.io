---
title: "The Chinese Remainder Theorem: Reconstructing One Number From Several Modular Worlds"
description: "How several modular views can determine one integer uniquely—and why the same theorem appears in RSA acceleration, subgroup attacks, and cryptographic reconstruction."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Number Theory"
  - "Public-Key Cryptography"
tags:
  - "chinese-remainder-theorem"
  - "crt"
  - "modular-arithmetic"
  - "rsa"
  - "number-theory"
  - "cryptography-from-zero"
difficulty: "Introductory"
series: "Cryptography From Zero"
seriesOrder: 11
draft: false
---

We have already used the Chinese Remainder Theorem twice in this series.

That bothered me a little.

We used it inside CRT-RSA.

We used it again to combine residues leaked by a small-subgroup attack.

And both times I essentially said:

> CRT reconstructs the answer.

But why?

What does it actually mean to know one number only through several modular views?

This is exactly the kind of result I do not want to leave as a black box.

So this article steps away from attacks for a moment and asks one clean question:

> If I know how an integer behaves modulo several coprime numbers, how much of that integer can I reconstruct?

The answer is remarkably strong.

Several independent modular views determine one unique residue modulo the product of the moduli.

![Chinese Remainder Theorem reconstruction](/images/blog/10-crt-reconstruction.svg)

*Several independent modular views can identify one residue modulo the product of the moduli.*

---

## A first reconstruction by inspection

Suppose an unknown integer $x$ satisfies

$$
x\equiv2\pmod3,
$$

$$
x\equiv3\pmod5,
$$

and

$$
x\equiv2\pmod7.
$$

At first, these look like three independent pieces of information.

The first congruence says that $x$ belongs to the sequence

$$
2,5,8,11,14,17,20,23,\ldots
$$

The second gives

$$
3,8,13,18,23,28,\ldots
$$

and the third gives

$$
2,9,16,23,30,\ldots
$$

The number

$$
23
$$

appears in all three.

Indeed,

$$
23\bmod3=2,
$$

$$
23\bmod5=3,
$$

and

$$
23\bmod7=2.
$$

So $23$ is a solution.

But it is not the only integer solution.

The product of the moduli is

$$
3\cdot5\cdot7=105.
$$

If we add $105$, none of the remainders change:

$$
23+105=128.
$$

Likewise,

$$
23+2\cdot105,
$$

$$
23-105,
$$

and every number of the form

$$
23+k\cdot105
$$

for $k\in\mathbb Z$ satisfies the same three congruences.

So the correct conclusion is

$$
\boxed{
x\equiv23\pmod{105}.
}
$$

This is the first important idea:

> The Chinese Remainder Theorem does not normally recover one absolute integer. It recovers one unique **residue class** modulo the product of the moduli.

If we additionally know that

$$
0\le x<105,
$$

then $23$ becomes the unique integer in that range.

---

## Why does reconstruction work?

The standard Chinese Remainder Theorem says the following.

Let

$$
n_1,n_2,\ldots,n_k
$$

be pairwise coprime positive integers.

Consider the system

$$
x\equiv a_1\pmod{n_1},
$$

$$
x\equiv a_2\pmod{n_2},
$$

$$
\vdots
$$

$$
x\equiv a_k\pmod{n_k}.
$$

Then there exists a solution, and that solution is unique modulo

$$
N=n_1n_2\cdots n_k.
$$

The phrase **pairwise coprime** is essential:

$$
\gcd(n_i,n_j)=1
\qquad
\text{for }i\neq j.
$$

For our example,

$$
3,\qquad5,\qquad7
$$

are pairwise coprime, so the clean version of the theorem applies.

Set

$$
N=3\cdot5\cdot7=105.
$$

Now define

$$
N_i=\frac{N}{n_i}.
$$

Thus,

$$
N_1=\frac{105}{3}=35,
$$

$$
N_2=\frac{105}{5}=21,
$$

and

$$
N_3=\frac{105}{7}=15.
$$

These values have a very useful property.

Consider $N_1=35$.

Because

$$
35=5\cdot7,
$$

we have

$$
35\equiv0\pmod5
$$

and

$$
35\equiv0\pmod7.
$$

But modulo $3$,

$$
35\equiv2\pmod3.
$$

What we would really like is a number that behaves like

$$
1\pmod3
$$

while remaining

$$
0\pmod5
$$

and

$$
0\pmod7.
$$

So we multiply $35$ by its modular inverse modulo $3$.

Because

$$
35\equiv2\pmod3
$$

and

$$
2^{-1}\equiv2\pmod3,
$$

we choose

$$
y_1=2.
$$

Then

$$
N_1y_1=35\cdot2=70
$$

satisfies

$$
70\equiv1\pmod3,
$$

$$
70\equiv0\pmod5,
$$

and

$$
70\equiv0\pmod7.
$$

It behaves like a modular selector.

The same idea works for every modulus.

For

$$
N_2=21,
$$

we have

$$
21\equiv1\pmod5,
$$

so

$$
y_2=1.
$$

For

$$
N_3=15,
$$

we have

$$
15\equiv1\pmod7,
$$

so

$$
y_3=1.
$$

### Why do these inverses always exist?

This is exactly where pairwise coprimality enters the construction.

Since

$$
N_i
=
\prod_{j\neq i}n_j,
$$

and every $n_j$ is coprime to $n_i$,

$$
\gcd(N_i,n_i)=1.
$$

Therefore $N_i$ has a multiplicative inverse modulo $n_i$.

So we may define

$$
y_i
=
N_i^{-1}\pmod{n_i}.
$$

Now every product

$$
N_i y_i
$$

satisfies

$$
N_i y_i\equiv1\pmod{n_i}
$$

while, for every $j\neq i$,

$$
N_i y_i\equiv0\pmod{n_j}.
$$

That is the mechanism behind the reconstruction.

---

## Constructing the solution

Once we have these modular selectors, the solution is

$$
x
=
\sum_{i=1}^{k}
a_iN_i y_i
\pmod N.
$$

For our example,

$$
a_1=2,
\qquad
a_2=3,
\qquad
a_3=2.
$$

Therefore,

$$
x
=
2\cdot35\cdot2
+
3\cdot21\cdot1
+
2\cdot15\cdot1.
$$

Compute:

$$
x
=
140+63+30
=
233.
$$

Now reduce modulo

$$
N=105:
$$

$$
233\bmod105=23.
$$

Therefore,

$$
\boxed{
x\equiv23\pmod{105}.
}
$$

The construction works because each term contributes exactly where it is supposed to contribute.

The first term is active modulo $3$ and disappears modulo $5$ and $7$.

The second is active modulo $5$ and disappears modulo $3$ and $7$.

The third is active modulo $7$ and disappears modulo $3$ and $5$.

Then we add the three independent components.

I find this a much more useful way to remember CRT than simply memorizing the final formula.

CRT is essentially a form of **modular basis construction**.

---

## Why is the solution unique?

Existence is only half of the theorem.

Why is the solution unique modulo

$$
N=n_1n_2\cdots n_k?
$$

Suppose $x$ and $y$ both satisfy all the same congruences.

Then for every $i$,

$$
x\equiv y\pmod{n_i}.
$$

Therefore,

$$
n_i\mid(x-y)
$$

for every $i$.

Because the moduli are pairwise coprime, their product also divides the difference:

$$
n_1n_2\cdots n_k
\mid
(x-y).
$$

Thus,

$$
N\mid(x-y),
$$

which means

$$
x\equiv y\pmod N.
$$

So although infinitely many integers satisfy the system, they all belong to the same residue class modulo $N$.

That is precisely the uniqueness promised by CRT.

---

## The theorem in Python

The code mirrors the mathematics almost line by line:

```python
from math import prod


def crt(residues, moduli):
    N = prod(moduli)

    x = 0

    for a_i, n_i in zip(residues, moduli):
        N_i = N // n_i
        y_i = pow(N_i, -1, n_i)

        x += a_i * N_i * y_i

    return x % N
```

Now compute:

```python
x = crt(
    residues=[2, 3, 2],
    moduli=[3, 5, 7],
)

print(x)
```

Output:

```text
23
```

And verify the original congruences:

```python
assert x % 3 == 2
assert x % 5 == 3
assert x % 7 == 2
```

The line

```python
pow(N_i, -1, n_i)
```

computes

$$
N_i^{-1}\pmod{n_i}.
$$

Once again, the implementation is mostly the theorem written in executable form.

For our educational implementation, we are assuming that the moduli are pairwise coprime.

A more defensive implementation should check that assumption explicitly.

For example:

```python
from math import gcd, prod


def crt(residues, moduli):
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")

    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError("moduli must be pairwise coprime")

    N = prod(moduli)
    x = 0

    for a_i, n_i in zip(residues, moduli):
        N_i = N // n_i
        y_i = pow(N_i, -1, n_i)

        x += a_i * N_i * y_i

    return x % N
```

The additional code is not part of the theorem itself.

It simply makes the assumptions explicit.

---

## Why cryptography keeps finding CRT useful

The theorem is much more than a textbook number-theory exercise.

It appears repeatedly because cryptography constantly moves between:

$$
\text{one large arithmetic object}
$$

and

$$
\text{several smaller modular views}.
$$

### RSA correctness and acceleration

Let

$$
N=pq.
$$

Instead of performing one large private RSA exponentiation modulo $N$, an implementation can work separately modulo $p$ and $q$.

In practice, CRT-RSA commonly uses reduced exponents such as

$$
d_P=d\bmod(p-1)
$$

and

$$
d_Q=d\bmod(q-1),
$$

then computes

$$
S_p=M^{d_P}\bmod p,
$$

$$
S_q=M^{d_Q}\bmod q.
$$

CRT reconstructs the unique value

$$
S\bmod N
$$

satisfying

$$
S\equiv S_p\pmod p
$$

and

$$
S\equiv S_q\pmod q.
$$

So CRT gives RSA two useful perspectives.

It acts as a **correctness lens**:

```text
correct modulo p
+
correct modulo q
        ↓
correct modulo pq
```

and as an **implementation optimization**:

```text
one large exponentiation modulo N
        ↓
two smaller exponentiations
        ↓
CRT recombination
```

The same structure that accelerates RSA was also what made the previous CRT-RSA fault attack possible when one modular branch became corrupted.

### Small-subgroup leakage

Earlier, our small-subgroup attack revealed

$$
d\equiv2\pmod3,
$$

$$
d\equiv3\pmod4,
$$

and

$$
d\equiv2\pmod5.
$$

Each leak looked tiny.

CRT combined them into

$$
d\equiv47\pmod{60}.
$$

Because the secret was known to satisfy

$$
0\le d<53,
$$

that residue identified

$$
d=47.
$$

This is almost the inverse perspective from RSA.

RSA intentionally decomposes one computation into smaller modular computations and then recombines them.

The attacker collects several small modular leaks and then recombines them into information about one larger secret.

Same theorem.

Completely different cryptographic role.

---

## The mental model

The picture I find most useful is:

```text
              one value x
                  │
       +----------+----------+
       │          │          │
       ▼          ▼          ▼

    x mod n₁   x mod n₂   x mod n₃

       │          │          │
       +----------+----------+
                  │
                 CRT
                  │
                  ▼

       x modulo n₁n₂n₃
```

We can read this diagram in both directions.

Going downward:

```text
local modular information
        ↓
global reconstruction
```

Going upward:

```text
one large arithmetic problem
        ↓
several smaller modular problems
```

That second viewpoint explains why CRT appears naturally in efficient arithmetic.

The first explains why modular leakage can become surprisingly powerful.

---

## What if the moduli are not coprime?

The clean version of CRT assumes pairwise-coprime moduli.

If the moduli share factors, reconstruction becomes more subtle.

For example, consider

$$
x\equiv1\pmod4
$$

and

$$
x\equiv2\pmod6.
$$

Since

$$
\gcd(4,6)=2,
$$

any common solution would need the two residues to agree modulo $2$.

But

$$
1\equiv1\pmod2
$$

while

$$
2\equiv0\pmod2.
$$

They disagree.

Therefore no solution exists.

More generally, for two congruences

$$
x\equiv a\pmod m
$$

and

$$
x\equiv b\pmod n,
$$

a solution exists exactly when

$$
a\equiv b\pmod{\gcd(m,n)}.
$$

Equivalently,

$$
\gcd(m,n)\mid(a-b).
$$

If the compatibility condition holds, a generalized CRT reconstructs a unique solution modulo

$$
\operatorname{lcm}(m,n).
$$

We do not need the full generalized construction yet.

For now, the important distinction is:

```text
pairwise coprime moduli
        ↓
solution always exists
and is unique modulo the product
```

whereas:

```text
non-coprime moduli
        ↓
compatibility must be checked first
```

---

## Practice

Try these before moving on.

### Exercise 1

Solve:

$$
x\equiv1\pmod3,
$$

$$
x\equiv4\pmod5.
$$

Your answer should be a residue class modulo

$$
15.
$$

### Exercise 2

Solve:

$$
x\equiv2\pmod3,
$$

$$
x\equiv3\pmod4,
$$

$$
x\equiv2\pmod5.
$$

Then compare your answer with the secret recovered in the small-subgroup article.

### Exercise 3

Consider:

$$
x\equiv2\pmod6,
$$

$$
x\equiv5\pmod9.
$$

The moduli are not coprime because

$$
\gcd(6,9)=3.
$$

Before trying to reconstruct $x$, check:

$$
2\bmod3
$$

and

$$
5\bmod3.
$$

Are the congruences compatible?

If so, find the solution modulo

$$
\operatorname{lcm}(6,9)=18.
$$

### Reader checkpoint

You should now be able to explain:

1. Why CRT returns a residue class rather than one absolute integer.
2. Why pairwise coprimality guarantees the inverses $N_i^{-1}$ exist.
3. Why each $N_i y_i$ behaves like a modular selector.
4. Why the final solution is unique modulo the product.
5. Why CRT makes RSA private operations faster.
6. Why CRT can also combine leaked modular information.
7. What must be checked when the moduli are not coprime.

If those points are clear, then CRT is no longer a formula to memorize.

It is a reconstruction mechanism.

---

## Where we are now

We now have a fairly complete first number-theoretic chain:

```text
division
    ↓
GCD
    ↓
Bézout
    ↓
modular inverse
    ↓
modular arithmetic
    ↓
groups
    ↓
exponentiation
    ↓
Chinese Remainder Theorem
```

And almost every one of these ideas has already reappeared inside a cryptographic mechanism or attack.

The GCD became a factor-recovery tool.

Modular inverses became necessary for RSA and group arithmetic.

Group order determined whether Diffie-Hellman was secure.

Subgroup structure created a key-recovery attack.

CRT accelerated RSA, enabled reconstruction, and exposed the algebra behind the previous fault attack.

That is exactly the progression we want in **Cryptography From Zero**:

$$
\boxed{
\text{foundation}
\rightarrow
\text{implementation}
\rightarrow
\text{cryptographic use}
\rightarrow
\text{failure mode}
}
$$

The next missing foundation is another object we have already relied on repeatedly:

**prime numbers themselves.**

Why does arithmetic modulo a prime behave so cleanly?

Why does every nonzero element modulo a prime have an inverse?

How do we test whether a candidate containing hundreds or thousands of bits is prime without trying every possible divisor?

And why does RSA key generation depend so heavily on getting this step right?

**Next: Prime Numbers for Cryptographers — From Trial Division to Miller–Rabin.**