---
title: "Modular Arithmetic From Zero: When Numbers Wrap Around—and When Multiplication Gets Weird"
description: "Congruence, residue classes, units, and the first zero divisor: the point where modular arithmetic stops being just '%' and starts becoming algebra for cryptography."
pubDate: "2026-09-08"
category: "Number Theory"
tags:
  - modular-arithmetic
  - congruence
  - units
  - zero-divisors
  - finite-fields
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

For a long time, modular arithmetic looked to me like this:

```python
x % n
```

Take a number, divide by $n$, keep the remainder.

Useful, yes.

But not particularly mysterious.

Then you start seeing cryptographic formulas like

$$
g^x \pmod p,
$$

$$
m^e \pmod N,
$$

$$
a^{-1}\pmod n,
$$

and eventually whole structures such as

$$
\mathbb Z_q[x]/(x^n+1).
$$

At that point `%` is no longer enough as a mental model.

We are not merely **reducing numbers**.

We are changing what it means for two numbers to be considered the same.

And once I really started thinking in those terms, the jump from elementary arithmetic to rings, fields, elliptic curves, and later lattice cryptography felt much less abrupt.

![Prime versus composite modular arithmetic](/images/blog/03-prime-vs-composite-modulus.svg)

*Modulo a prime, every non-zero residue is invertible. Modulo a composite number, new phenomena appear—including non-zero values whose product becomes zero.*

---

## "The same modulo $n$" does not mean equal as integers

Take:

$$
17
$$

and:

$$
2.
$$

They are obviously different integers.

But:

$$
17-2=15,
$$

and $15$ is divisible by $5$.

So we write:

$$
\boxed{
17\equiv2\pmod5.
}
$$

The definition is:

$$
a\equiv b\pmod n
$$

if and only if

$$
n\mid(a-b).
$$

Another way to say the same thing is:

> $a$ and $b$ leave the same remainder when divided by $n$.

So modulo $5$,

$$
\ldots,-8,-3,2,7,12,17,22,\ldots
$$

all represent the same residue.

That is why, in the previous post,

$$
-5
$$

and

$$
38
$$

were both valid versions of the inverse of $17$ modulo $43$:

$$
-5\equiv38\pmod{43}.
$$

They differ by exactly $43$.

### From infinitely many integers to finitely many classes

Modulo $5$, every integer falls into one of only five possibilities:

$$
[0],[1],[2],[3],[4].
$$

Instead of carrying every integer around, we work with its **residue class**.

So:

$$
\mathbb Z/5\mathbb Z
$$

contains five classes.

Likewise:

$$
\mathbb Z/15\mathbb Z
$$

contains fifteen.

In code, we normally store a canonical representative:

```python
17 % 5
```

which returns:

```text
2
```

But mathematically the real object is not just the integer `2`.

It is the entire equivalence class

$$
[2].
$$

For most implementation work we can safely use representatives, as long as we remember what they stand for.

---

Arithmetic still works exactly as we would hope.

If

$$
a\equiv a'\pmod n
$$

and

$$
b\equiv b'\pmod n,
$$

then:

$$
a+b\equiv a'+b'\pmod n
$$

and:

$$
ab\equiv a'b'\pmod n.
$$

That gives us modular addition and multiplication:

```python
def mod_add(a, b, n):
    return (a + b) % n

def mod_mul(a, b, n):
    return (a * b) % n
```

For example:

$$
17+9=26\equiv6\pmod{20},
$$

so:

```python
(17 + 9) % 20
```

returns:

```text
6
```

Nothing strange yet.

The strange part begins when we ask which elements can be **divided by**.

---

## Some residues are units. Some are not.

In modular arithmetic, division means multiplication by an inverse.

So when I write:

$$
a^{-1}\pmod n,
$$

I am looking for some $b$ satisfying

$$
ab\equiv1\pmod n.
$$

An element with such an inverse is called a **unit**.

From the previous post we already know the exact criterion:

$$
\boxed{
a\text{ is invertible modulo }n
\iff
\gcd(a,n)=1.
}
$$

Take modulo $20$.

The residues coprime to 20 are:

$$
1,3,7,9,11,13,17,19.
$$

Those are precisely the units:

$$
\mathbb Z_{20}^{\times}
=
\{1,3,7,9,11,13,17,19\}.
$$

For example:

$$
3\cdot7=21\equiv1\pmod{20}.
$$

So:

$$
3^{-1}\equiv7\pmod{20}.
$$

But $4$ is different:

$$
\gcd(4,20)=4.
$$

There is no residue $x$ for which:

$$
4x\equiv1\pmod{20}.
$$

That already tells us something important:

> Non-zero does **not** automatically mean invertible.

And whether that statement is true depends on the modulus.

### Prime modulus: everything non-zero is invertible

Consider:

$$
\mathbb Z_7.
$$

Because $7$ is prime, every number

$$
1,2,3,4,5,6
$$

is coprime to $7$.

Therefore every non-zero element has an inverse.

For example:

$$
2^{-1}\equiv4\pmod7
$$

because:

$$
2\cdot4=8\equiv1\pmod7.
$$

Similarly:

$$
3^{-1}\equiv5\pmod7.
$$

This is one of the reasons prime moduli appear so often in cryptography.

Modulo a prime, we get a **field**:

$$
\boxed{\mathbb Z_p\text{ is a field when }p\text{ is prime}.}
$$

A field is an arithmetic world where every non-zero element can be divided by.

That is an incredibly useful guarantee.

---

## Then modulo 15 does something that feels wrong the first time

Now consider:

$$
\mathbb Z_{15}.
$$

Take:

$$
3
$$

and:

$$
5.
$$

Neither is zero modulo 15.

Yet:

$$
3\cdot5=15
$$

so:

$$
\boxed{
3\cdot5\equiv0\pmod{15}.
}
$$

Read that slowly:

$$
3\neq0,
$$

$$
5\neq0,
$$

but:

$$
3\cdot5=0
$$

inside $\mathbb Z_{15}$.

These are **zero divisors**.

This phenomenon cannot happen in a field.

And this was one of the first places where I felt that modular arithmetic had stopped being "clock arithmetic" and started becoming actual algebra.

It also explains why cancellation can suddenly become dangerous.

Suppose:

$$
3x\equiv3y\pmod{15}.
$$

Over ordinary integers we might instinctively cancel the $3$.

But modulo 15, $3$ is not invertible.

For example:

$$
3\cdot1=3
$$

and:

$$
3\cdot6=18\equiv3\pmod{15}.
$$

So:

$$
3\cdot1\equiv3\cdot6\pmod{15},
$$

while:

$$
1\not\equiv6\pmod{15}.
$$

Cancelling the $3$ would give a false conclusion.

The real issue is not that modular arithmetic is inconsistent.

The issue is that we tried to divide by something that has no inverse.

That distinction will matter again and again.

---

### Why I care about this cryptographically

A lot of cryptographic algorithms contain steps that, mathematically, are divisions.

They may not look like `/` in code.

They look like:

```text
compute inverse
multiply by inverse
solve linear equation
normalize a point
interpolate a polynomial
undo a transform
```

All of those operations silently depend on the relevant inverse actually existing.

So there is a major difference between doing arithmetic in:

$$
\mathbb Z_p
$$

for prime $p$, where every non-zero element is invertible, and arithmetic in:

$$
\mathbb Z_n
$$

for composite $n$, where zero divisors and non-units appear.

This distinction eventually reaches:

```text
RSA
finite fields
elliptic curves
Shamir secret sharing
CRT
polynomial quotient rings
NTT
threshold cryptography
lattice constructions
```

We will not force all of those topics into this post.

But I want to keep one mental warning from now on:

> Whenever a cryptographic derivation "divides" by something, ask whether that element is actually invertible in the structure we are working in.

That question catches a surprising number of mistakes.

---

Run the companion chapter:

```powershell
python chapters/03_modular_arithmetic/demo.py
```

It prints:

- modular addition/subtraction/multiplication,
- all units of $\mathbb Z_{20}$,
- the difference between $\mathbb Z_7$ and $\mathbb Z_{15}$,
- an explicit zero-divisor witness.

Then run:

```powershell
python chapters/03_modular_arithmetic/experiments.py
```

The experiment checks every non-zero residue and asks:

```text
gcd(a,n) = ?
inverse exists?
what is the inverse?
```

Compare the output for:

$$
n=7
$$

and:

$$
n=15.
$$

That table is a very small computational experiment, but it exposes the entire field-versus-ring distinction.

Before moving on, try to answer these without code:

1. Why are $17$ and $2$ the same modulo $5$?
2. Which residues modulo $10$ are units?
3. Why does $2^{-1}\pmod{10}$ not exist?
4. Find two non-zero zero divisors modulo $21$.
5. Why is cancelling a factor modulo a composite number potentially invalid?

---

At this point we have built:

$$
\text{division}
\rightarrow
\gcd
\rightarrow
\text{Bézout}
\rightarrow
\text{inverse}
\rightarrow
\text{modular arithmetic}.
$$

The next step is to stop looking at individual inverses and study the invertible residues **as a set with structure**.

Why do the units modulo $n$ form a group?

What is the order of an element?

Why can repeatedly multiplying one element eventually generate an entire set?

That is where Diffie-Hellman starts becoming visible in the distance.

**Next:** *Multiplicative Groups, Orders, and Generators: The Structure Behind Diffie-Hellman.*
