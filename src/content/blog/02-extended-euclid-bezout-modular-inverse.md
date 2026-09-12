---
title: "Extended Euclid, Bézout, and the First Modular Inverse"
description: "How the Euclidean algorithm turns from a GCD calculator into a machine for constructing modular inverses—and why this tiny step appears directly inside RSA."
pubDate: "2026-09-08"
category: "Number Theory"
tags:
  - number-theory
  - extended-euclid
  - bezout
  - modular-inverse
  - rsa
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

In the previous post, Euclid gave us something very useful:

$$
\gcd(a,b).
$$

But while going through this again, I realized that the number itself is only half of the story.

For example,

$$
\gcd(17,43)=1.
$$

Fine.

But what does that **1** actually buy us?

Why does cryptography care so much when two integers are coprime?

The answer is hidden inside the same Euclidean divisions we already computed.

If we keep a little more information instead of throwing it away, Euclid gives us not only the GCD, but integers $x$ and $y$ satisfying

$$
\boxed{
ax+by=\gcd(a,b).
}
$$

That is Bézout's identity.

And when the GCD is $1$, that equation quietly becomes a machine for constructing modular inverses.

That was one of those small connections that made the whole topic feel much less arbitrary to me.

---

## Euclid gives the GCD; Extended Euclid gives a certificate

Let us stay with one example:

$$
a=17,\qquad b=43.
$$

The ordinary Euclidean algorithm gives

$$
43=2\cdot17+9,
$$

$$
17=1\cdot9+8,
$$

$$
9=1\cdot8+1.
$$

So

$$
\gcd(17,43)=1.
$$

Normally we stop there.

The Extended Euclidean Algorithm asks one extra question:

> Can I rewrite that final $1$ using only the original numbers $17$ and $43$?

Start from the last non-zero remainder:

$$
1=9-8.
$$

But from the previous line,

$$
8=17-9.
$$

Substitute:

$$
1=9-(17-9)
$$

so

$$
1=2\cdot9-17.
$$

And because

$$
9=43-2\cdot17,
$$

substitute again:

$$
1=2(43-2\cdot17)-17.
$$

Therefore

$$
\boxed{
1=2\cdot43-5\cdot17.
}
$$

Or, in the order I usually prefer to read it,

$$
\boxed{
17(-5)+43(2)=1.
}
$$

So one possible pair of Bézout coefficients is

$$
x=-5,\qquad y=2.
$$

This equation is more than a proof that the GCD is 1.

It is a **certificate**.

Anyone can multiply the numbers and check it:

```python
a = 17
b = 43
x = -5
y = 2

assert a * x + b * y == 1
```

This is exactly the kind of thing I like in cryptographic code: a mathematical claim that can be checked immediately.

The implementation keeps track of those coefficients while Euclid runs:

```python
def extended_gcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        q = old_r // r

        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    return old_r, old_s, old_t
```

The important invariant is:

$$
r_i=s_i a+t_i b.
$$

In other words, every remainder is still being tracked as an integer combination of the original inputs.

So when the final non-zero remainder becomes the GCD, we already know how to express it in terms of $a$ and $b$.

---

## And suddenly we have an inverse

Now take the Bézout equation:

$$
17(-5)+43(2)=1.
$$

Reduce everything modulo $43$.

The term

$$
43(2)
$$

disappears because it is divisible by $43$.

So:

$$
17(-5)\equiv1\pmod{43}.
$$

That means:

$$
-5
$$

is an inverse of $17$ modulo $43$.

We usually write the positive representative:

$$
-5\equiv38\pmod{43}.
$$

Therefore

$$
\boxed{
17^{-1}\equiv38\pmod{43}.
}
$$

Check it:

```python
(17 * 38) % 43
```

returns

```text
1
```

This is the connection I do not want to memorize as a detached theorem:

$$
\gcd(a,n)=1
$$

is not some random condition we impose before computing an inverse.

It is exactly the condition that lets Bézout give us

$$
ax+ny=1.
$$

Reducing modulo $n$ leaves

$$
ax\equiv1\pmod n.
$$

So $x$ is the inverse.

The whole chain is:

```text
gcd(a,n) = 1
        ↓
Bézout
        ↓
ax + ny = 1
        ↓   mod n
ax ≡ 1
        ↓
x = a⁻¹ mod n
```

That is it.

A modular inverse is not a new mysterious object.

It falls directly out of Euclid.

---

## What if the GCD is not 1?

Now try

$$
6\pmod{15}.
$$

We have

$$
\gcd(6,15)=3.
$$

Bézout can give us a relation of the form

$$
6x+15y=3,
$$

but never

$$
6x+15y=1.
$$

Why?

Because every integer combination of 6 and 15 is divisible by 3.

So there cannot exist an $x$ such that

$$
6x\equiv1\pmod{15}.
$$

The inverse does not exist.

This is not Python failing.

It is not that we need a better library.

The mathematics says there is no answer.

That distinction matters a lot later, especially when we start working in structures where **not every non-zero element is invertible**.

In code, I want that failure to be explicit:

```python
def mod_inverse(a, modulus):
    g, x, _ = extended_gcd(a, modulus)

    if g != 1:
        raise ValueError("inverse does not exist")

    return x % modulus
```

So:

```python
mod_inverse(17, 43)
```

returns

```text
38
```

while:

```python
mod_inverse(6, 15)
```

should fail.

That failure itself contains mathematical information.

---

## The moment it becomes actual cryptographic machinery

This is where I think the topic changes character.

We are no longer studying inverses because number theory says they are interesting.

They become **key-generation operations**.

A standard RSA private exponent satisfies

$$
ed\equiv1\pmod{\lambda(n)}.
$$

So, conceptually,

$$
\boxed{
d=e^{-1}\pmod{\lambda(n)}.
}
$$

The public exponent $e$ must therefore be coprime with $\lambda(n)$.

That is exactly the same criterion we just proved.

The PKCS #1 RSA specification states both conditions: a valid public exponent satisfies

$$
\gcd(e,\lambda(n))=1,
$$

and the corresponding private exponent satisfies

$$
ed\equiv1\pmod{\lambda(n)}.
$$

If you want to see the standard rather than just take my word for it:

**Reference:** [RFC 8017 — PKCS #1 v2.2](https://www.rfc-editor.org/rfc/rfc8017)

A tiny toy example makes the connection visible.

Suppose later we construct an RSA example where

$$
\lambda(n)=30
$$

and choose

$$
e=7.
$$

Because

$$
\gcd(7,30)=1,
$$

the inverse exists.

Extended Euclid gives

$$
7(13)+30(-3)=1.
$$

Reduce modulo 30:

$$
7\cdot13\equiv1\pmod{30}.
$$

So:

$$
d=13.
$$

The private exponent has literally appeared as a Bézout coefficient.

That is the part I find worth slowing down for.

We started two posts ago with:

```python
a % b
```

and we have now reached an operation that constructs part of an RSA private key.

---

Run the companion chapter:

```powershell
python chapters/02_extended_euclid_bezout/demo.py
```

and then try the exercises yourself.

A few good checks are:

$$
11^{-1}\pmod{26},
$$

whether

$$
12^{-1}\pmod{26}
$$

exists at all, and Bézout coefficients for

$$
\gcd(252,105).
$$

Do not just ask Python for the answer.

For at least one of them, write the Euclidean divisions and substitute backwards by hand.

That is where the mechanism becomes much easier to remember.

---

The next question almost asks itself.

We can now compute an inverse modulo $n$.

But what exactly does it mean to say that two integers are "the same modulo $n$"?

Why are

$$
38
$$

and

$$
-5
$$

both valid representatives of the same inverse modulo $43$?

And when do the non-zero residues behave like a group—or even like a field?

That takes us into **modular arithmetic itself**, where we stop treating `%` as a Python operator and start treating congruence as a mathematical structure.

**Next:** *Modular Arithmetic From Zero: Congruence, Residues, Units, and Zero Divisors.*
