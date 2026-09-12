---
title: "The Chinese Remainder Theorem: Reconstructing One Number From Several Modular Worlds"
description: "How several modular views can determine one integer uniquely—and why the same theorem appears in RSA acceleration, subgroup attacks, and cryptographic reconstruction."
pubDate: "2026-09-08"
category: "Number Theory"
tags:
  - chinese-remainder-theorem
  - crt
  - modular-arithmetic
  - rsa
  - number-theory
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

We have already used the Chinese Remainder Theorem twice in this series.

That bothered me a little.

We used it inside CRT-RSA.

We used it again to combine the residues leaked by a small-subgroup attack.

And both times I essentially said:

> CRT reconstructs the answer.

But why?

What does it really mean to know one number only through several modular views?

This is exactly the kind of thing I do not want to leave as a black box.

So this post steps away from attacks for a moment and asks one clean question:

> If I know how an integer looks modulo several coprime numbers, can I recover the original integer?

The answer is yes—up to one larger modulus.

![Chinese Remainder Theorem reconstruction](/images/blog/10-crt-reconstruction.svg)

*Several independent modular views can identify one residue modulo the product of the moduli.*

---

Suppose some unknown integer $x$ satisfies:

$$
x\equiv2\pmod3,
$$

$$
x\equiv3\pmod5,
$$

and:

$$
x\equiv2\pmod7.
$$

At first this looks like three separate pieces of information.

Modulo $3$, $x$ belongs to:

$$
2,5,8,11,14,17,20,23,\ldots
$$

Modulo $5$, it belongs to:

$$
3,8,13,18,23,28,\ldots
$$

Modulo $7$, it belongs to:

$$
2,9,16,23,30,\ldots
$$

And suddenly the same number appears:

$$
23.
$$

Check:

$$
23\bmod3=2,
$$

$$
23\bmod5=3,
$$

$$
23\bmod7=2.
$$

So:

$$
x=23
$$

is one solution.

But it is not the only integer solution.

If we add:

$$
3\cdot5\cdot7=105,
$$

nothing changes in any of the three congruences.

Therefore:

$$
23+105=128
$$

also works.

So does:

$$
23+2\cdot105.
$$

And:

$$
23-105.
$$

The real answer is:

$$
\boxed{
x\equiv23\pmod{105}.
}
$$

That is the first important idea:

> CRT does not usually recover one absolute integer. It recovers one residue class modulo the product.

---

## Why does the reconstruction work?

The standard CRT says that if the moduli:

$$
n_1,n_2,\ldots,n_k
$$

are pairwise coprime, then the system:

$$
x\equiv a_i\pmod{n_i}
$$

has a unique solution modulo:

$$
N=n_1n_2\cdots n_k.
$$

The word **pairwise coprime** matters.

For our example:

$$
3,\quad5,\quad7
$$

share no common factors.

Now let:

$$
N=3\cdot5\cdot7=105.
$$

We build three numbers:

$$
N_1=\frac{105}{3}=35,
$$

$$
N_2=\frac{105}{5}=21,
$$

$$
N_3=\frac{105}{7}=15.
$$

Each $N_i$ has a useful property.

For example, $35$ is divisible by both $5$ and $7$.

So:

$$
35\equiv0\pmod5
$$

and:

$$
35\equiv0\pmod7.
$$

But modulo $3$:

$$
35\equiv2\pmod3.
$$

We would like to turn that $2$ into a $1$.

So we multiply by the inverse of $35$ modulo $3$.

Because:

$$
35\equiv2\pmod3
$$

and:

$$
2^{-1}\equiv2\pmod3,
$$

we use:

$$
y_1=2.
$$

Then:

$$
35\cdot2
$$

behaves like:

$$
1\pmod3
$$

but still like:

$$
0\pmod5
$$

and:

$$
0\pmod7.
$$

This is almost like constructing a modular selector.

It says:

```text
keep the mod-3 component
erase the mod-5 component
erase the mod-7 component
```

Do the same for the other moduli.

For $N_2=21$:

$$
21\equiv1\pmod5,
$$

so:

$$
y_2=1.
$$

For $N_3=15$:

$$
15\equiv1\pmod7,
$$

so:

$$
y_3=1.
$$

Now assemble:

$$
x
=
a_1N_1y_1
+
a_2N_2y_2
+
a_3N_3y_3.
$$

Substitute:

$$
x
=
2\cdot35\cdot2
+
3\cdot21\cdot1
+
2\cdot15\cdot1.
$$

So:

$$
x=140+63+30=233.
$$

Reduce modulo $105$:

$$
233\bmod105=23.
$$

Therefore:

$$
\boxed{
x\equiv23\pmod{105}.
}
$$

That is the constructive CRT formula.

---

The part I find most satisfying is that each term has been engineered to behave like a switch.

The first term contributes the desired value modulo $3$ but disappears modulo $5$ and $7$.

The second term contributes modulo $5$ but disappears modulo $3$ and $7$.

The third contributes modulo $7$ but disappears modulo $3$ and $5$.

Then we add the pieces.

So CRT is not magic reconstruction.

It is **modular basis construction**.

---

A direct Python implementation mirrors the mathematics:

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

Now:

```python
x = crt(
    residues=[2, 3, 2],
    moduli=[3, 5, 7],
)

print(x)
```

returns:

```text
23
```

And we can test the invariants:

```python
assert x % 3 == 2
assert x % 5 == 3
assert x % 7 == 2
```

Again, the code is mostly the theorem written in executable form.

---

## Why cryptography keeps finding CRT useful

This is where the theorem becomes much more than a number-theory exercise.

### 1. RSA correctness and acceleration

For:

$$
N=pq,
$$

RSA arithmetic can be studied separately modulo:

$$
p
$$

and:

$$
q.
$$

If two values agree modulo both secret primes, CRT tells us they agree modulo:

$$
N=pq.
$$

That is why CRT is a clean way to prove RSA correctness.

It is also an implementation optimization.

Instead of computing one large private exponentiation modulo $N$, an RSA implementation can compute separately modulo $p$ and $q$ and reconstruct the result.

In the older RSA notes I had written this as:

$$
m_1=c^{d_P}\bmod p,
$$

$$
m_2=c^{d_Q}\bmod q,
$$

then recombine.

So CRT plays two roles:

```text
proof / correctness lens
and
implementation optimization
```

That dual role is worth remembering.

### 2. Small-subgroup attacks

In Blog 07, the attacker learned:

$$
d\equiv2\pmod3,
$$

$$
d\equiv3\pmod4,
$$

$$
d\equiv2\pmod5.
$$

Those look like tiny fragments of the secret.

But CRT combines them into:

$$
d\equiv47\pmod{60}.
$$

So enough small modular leaks can reconstruct one much larger secret.

That is almost the inverse use of the RSA story.

RSA uses CRT intentionally to combine trustworthy partial computations.

The attacker uses CRT to combine leaked partial information.

Same theorem.

Completely different role.

---

This gives me a mental model I like:

```text
one hidden integer x
      ↓
many modular projections

x mod n₁
x mod n₂
x mod n₃
      ↓
CRT
      ↓
one residue modulo n₁n₂n₃
```

You can read that diagram in either direction.

Going downward:

```text
local modular information
→ global reconstruction
```

Going upward:

```text
one large problem
→ several smaller modular problems
```

That second viewpoint is exactly why CRT appears so naturally in efficient arithmetic.

---

There is one caveat I do not want to hide.

The clean theorem above assumes the moduli are pairwise coprime.

If they are not, reconstruction is more subtle.

For example:

$$
x\equiv1\pmod4
$$

and:

$$
x\equiv2\pmod6
$$

cannot both hold, because the two congruences disagree modulo:

$$
\gcd(4,6)=2.
$$

A generalized CRT exists, but the compatibility condition matters.

We do not need the full generalized theorem yet.

For now:

> pairwise coprime moduli give the cleanest reconstruction story.

---

Try these before moving on:

1. Solve:

$$
x\equiv1\pmod3,
$$

$$
x\equiv4\pmod5.
$$

2. Solve:

$$
x\equiv2\pmod3,
$$

$$
x\equiv3\pmod4,
$$

$$
x\equiv2\pmod5.
$$

3. Verify that your second answer reproduces the secret from Blog 07.

4. For the system:

$$
x\equiv2\pmod6,
$$

$$
x\equiv5\pmod9,
$$

ask first whether the congruences are compatible before trying to reconstruct anything.

---

We now have a fairly complete first number-theory chain:

```text
division
→ GCD
→ Bézout
→ inverse
→ modular arithmetic
→ groups
→ exponentiation
→ CRT
```

And every one of those ideas has already reappeared inside a real cryptographic mechanism or attack.

That is exactly the progression I wanted.

The next missing foundation is another object we have been using without really studying:

**prime numbers themselves.**

Why do primes make modular arithmetic behave so cleanly?

How do we test whether a large candidate is probably prime without trying every divisor?

And why does RSA key generation depend on getting this step right?

**Next:** *Prime Numbers for Cryptographers: From Trial Division to Miller–Rabin.*
