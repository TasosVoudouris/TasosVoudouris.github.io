---
title: "Integers, Division, and GCD: Where Cryptography Quietly Starts"
description: "Why divisibility, remainders, and Euclid's algorithm are much more than elementary arithmetic—and how a tiny GCD can already expose a broken RSA key."
pubDate: "2026-09-08"
category: "Number Theory"
tags:
  - number-theory
  - gcd
  - euclidean-algorithm
  - rsa
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

One thing I keep noticing, both when I try to **teach cryptography** and when I try to learn a new part of it myself, is that the places where I get stuck are often not the "advanced" ones.

They are the lines that look too simple to question.

For example, in RSA we eventually write something like

$$
\gcd(e,\varphi(N))=1.
$$

I had seen conditions like this many times. It is very easy to read them, accept them, and move on.

But then the annoying—and useful—question appears:

> Why exactly do I need the GCD to be 1?  
> What does division have to do with a private key?  
> What actually breaks if it is not?

That is the spirit of this series.

So before RSA, elliptic curves, lattices, or ML-KEM, I want to start with something almost embarrassingly basic:

**integer division.**

Because from division we get remainders; from remainders we get Euclid; from Euclid we get the GCD; from the GCD we discover when inverses exist; and those inverses eventually appear everywhere.

![From integer division to cryptographic constructions](/images/blog/01-gcd-roadmap.svg)

*The point is not that every cryptosystem is "just GCD". The point is that very small arithmetic ideas keep reappearing inside much larger constructions.*

---

## Division is not just "getting a decimal answer"

Take two integers:

$$
17 \quad \text{and} \quad 5.
$$

Ordinary division gives

$$
17/5 = 3.4.
$$

But number theory asks a different question:

> How many complete copies of 5 fit inside 17, and what is left?

The answer is

$$
17 = 5\cdot3 + 2.
$$

We call:

$$
q=3
$$

the **quotient**, and

$$
r=2
$$

the **remainder**.

In general, for an integer $a$ and positive integer $b$, there are unique integers $q$ and $r$ such that

$$
\boxed{
a=bq+r,\qquad 0\le r<b.
}
$$

That is the **division algorithm**.

In Python:

```python
a = 17
b = 5

q = a // b
r = a % b

print(q)  # 3
print(r)  # 2

assert a == b * q + r
```

I like the last line more than it may first appear.

We are not merely printing an answer. We are checking that our program satisfies the mathematical relation

$$
a=bq+r.
$$

That habit—turning mathematical statements into executable invariants—is something we will keep throughout the whole project.

### Divisibility is just the zero-remainder case

We write

$$
d\mid n
$$

when $d$ divides $n$ exactly.

Formally, there must exist some integer $k$ such that

$$
n=dk.
$$

Computationally:

```python
def divides(d, n):
    return n % d == 0
```

For example,

$$
5\mid 60
$$

because

$$
60=5\cdot12,
$$

and Python confirms:

```python
assert 60 % 5 == 0
```

But

$$
7\nmid60
$$

because the remainder is not zero.

Already we have converted a mathematical definition into a one-line test.

---

## The GCD—and why Euclid's trick is not really a trick

Suppose we want the greatest positive integer dividing both 48 and 18.

The common divisors are

$$
1,2,3,6,
$$

so

$$
\gcd(48,18)=6.
$$

The first algorithm I would naturally write is almost embarrassingly simple:

```python
def gcd_naive(a, b):
    a = abs(a)
    b = abs(b)

    for d in range(min(a, b), 0, -1):
        if a % d == 0 and b % d == 0:
            return d
```

It works.

And I actually like starting here because we can **see the search**.

For $48$ and $18$, try 18, then 17, then 16, and so on until a common divisor appears.

But Euclid gives us something dramatically better:

$$
\boxed{
\gcd(a,b)=\gcd(b,a\bmod b).
}
$$

For $48$ and $18$:

$$
48=2\cdot18+12,
$$

so

$$
\gcd(48,18)=\gcd(18,12).
$$

Then

$$
18=1\cdot12+6,
$$

so

$$
\gcd(18,12)=\gcd(12,6).
$$

Finally,

$$
12=2\cdot6+0.
$$

The last non-zero remainder is

$$
\boxed{6}.
$$

Therefore

$$
\gcd(48,18)=6.
$$

The Python version is tiny:

```python
def gcd_euclid(a, b):
    while b != 0:
        a, b = b, a % b

    return abs(a)
```

When I first learned this, the part I did not want to simply memorize was:

> Why are we allowed to replace $(a,b)$ with $(b,a\bmod b)$?

Write the division relation as

$$
a=bq+r.
$$

Rearrange it:

$$
r=a-bq.
$$

Now suppose $d$ divides both $a$ and $b$.

Then $d$ also divides every integer combination of them, including

$$
a-bq=r.
$$

So every common divisor of $a$ and $b$ is also a common divisor of $b$ and $r$.

The argument also works backwards because

$$
a=bq+r.
$$

Therefore the two pairs have exactly the same common divisors.

That is the entire reason Euclid works.

Not magic. Not a programming trick.

Just divisibility.

---

## Where this suddenly becomes cryptography

This is the point where I personally stop seeing the GCD as a school exercise.

Later, when we work modulo $n$, an integer $a$ has a multiplicative inverse exactly when

$$
\gcd(a,n)=1.
$$

So the question

> Does $a^{-1}\pmod n$ exist?

is secretly asking

> Are $a$ and $n$ coprime?

That condition will appear in RSA key generation, modular equations, finite groups, elliptic-curve arithmetic, polynomial algorithms, and even when we build an inverse NTT much later in the series.

But there is an even more concrete security connection.

Imagine two RSA public moduli:

$$
N_1=pq
$$

and

$$
N_2=qr.
$$

They were supposed to use independent random primes, but both accidentally reused $q$.

Then:

$$
\gcd(N_1,N_2)=q.
$$

We have just recovered a secret prime factor using the same operation we implemented above.

A tiny example:

```python
from math import gcd

p = 11
q = 13
r = 17

N1 = p * q       # 143
N2 = q * r       # 221

shared = gcd(N1, N2)

print(shared)    # 13
```

And now:

$$
N_1/13=11,
$$

$$
N_2/13=17.
$$

Both moduli are factored.

This is not only a toy observation.

> **Paper connection — when GCD became a large-scale RSA diagnostic.**  
> Heninger, Durumeric, Wustrow, and Halderman's USENIX Security 2012 paper *Mining Your Ps and Qs: Detection of Widespread Weak Keys in Network Devices* analyzed more than 11 million distinct RSA moduli from TLS/SSH-related datasets and used efficient batch-GCD techniques to detect moduli sharing prime factors.  
> [Read the USENIX paper](https://www.usenix.org/conference/usenixsecurity12/technical-sessions/presentation/heninger)

This is one of those connections that I love in cryptography.

We begin with

$$
17=5\cdot3+2
$$

and somehow end up discussing the failure of real RSA key generation.

That is exactly why I do not want to skip the "easy" parts anymore.

---

## Let's keep the code simple and observable

Inside the companion repository, Chapter 01 contains both the deliberately slow version and Euclid's version.

Run:

```powershell
python chapters/01_integers_division_gcd/demo.py
```

You will see:

- division with remainder,
- divisibility tests,
- positive divisors,
- naive GCD,
- Euclidean GCD,
- coprime numbers below 20,
- a few edge cases.

There is also an experiment:

```powershell
python chapters/01_integers_division_gcd/experiments.py
```

The point is not to produce a serious benchmark yet.

The point is to build a habit:

```text
understand the definition
        ↓
write the obvious implementation
        ↓
observe its weakness
        ↓
find the better mathematics
        ↓
test both
```

That pattern will repeat throughout this series.

For example, try:

$$
\gcd(1337,137).
$$

Euclid gives:

$$
\begin{aligned}
1337 &= 137\cdot9+104\\
137  &= 104\cdot1+33\\
104  &= 33\cdot3+5\\
33   &= 5\cdot6+3\\
5    &= 3\cdot1+2\\
3    &= 2\cdot1+1\\
2    &= 1\cdot2+0.
\end{aligned}
$$

So

$$
\gcd(1337,137)=1.
$$

That word—**coprime**—is going to matter a lot.

Before moving on, try these yourself:

```text
gcd(252, 105)
gcd(0, 15)
gcd(-48, 18)
```

and find every integer

$$
1\le a<20
$$

for which

$$
\gcd(a,20)=1.
$$

Keep that final list.

Very soon we will discover that those numbers are precisely the elements that can be inverted modulo 20.

---

## The question I want to carry into the next post

At this point we know how to compute

$$
\gcd(a,b).
$$

But the GCD algorithm is hiding more information than just one number.

If

$$
\gcd(a,b)=1,
$$

can we actually find integers $x$ and $y$ such that

$$
ax+by=1?
$$

And if we can, why does that suddenly give us a modular inverse?

That is where the **Extended Euclidean Algorithm and Bézout's identity** enter.

And that is the moment this simple division process starts producing actual cryptographic machinery.

---

### Quick checkpoint

If you can explain these four statements in your own words, you are ready to continue:

1. $d\mid n$ means the remainder is zero.
2. $a=bq+r$ is the structure behind integer division.
3. Euclid works because $(a,b)$ and $(b,r)$ have the same common divisors.
4. $\gcd(a,n)=1$ will become the condition that lets us invert $a$ modulo $n$.

**Next:** *Extended Euclid, Bézout, and the First Modular Inverse.*
