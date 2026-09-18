---
title: "Number Theory Reference I: Integers and Divisibility"
description: "A detailed reference on the integers, divisibility, Euclidean division, quotient and remainder conventions, GCD, LCM, the Euclidean algorithm, Bézout's identity, and executable examples."
pubDate: "2025-04-23"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "integers"
  - "divisibility"
  - "division-algorithm"
  - "gcd"
  - "euclidean-algorithm"
  - "number-theory"
difficulty: "Introductory"
series: "Elementary Number Theory Reference"
seriesOrder: 1
draft: false
---

Number theory begins with objects that look almost too familiar to deserve much attention:

\[
\ldots,-3,-2,-1,0,1,2,3,\ldots
\]

the integers.

But cryptography repeatedly asks much deeper questions about them.

Does one integer divide another?

What does a remainder really mean?

When does an inverse exist?

How can we compute the greatest common divisor of two enormous integers efficiently?

How can the equation

\[
ax+by=d
\]

tell us something about modular inverses, RSA, or finite groups?

This reference develops the first part of that chain carefully.

We begin with the integers and divisibility, move through Euclidean division, define the greatest common divisor and least common multiple, derive the Euclidean algorithm, and finish with the Extended Euclidean Algorithm and Bézout's identity.

These are elementary ideas, but they form a large part of the arithmetic machinery used throughout modern cryptography.

---

## Table of Contents

- [The integers](#the-integers)
- [Divisibility](#divisibility)
- [Euclidean division and remainders](#euclidean-division-and-remainders)
- [Greatest common divisor and least common multiple](#greatest-common-divisor-and-least-common-multiple)
- [The Euclidean algorithm](#the-euclidean-algorithm)
- [The Extended Euclidean Algorithm](#the-extended-euclidean-algorithm)
- [\[
\begin${aligned}
1
&=
2\cdot33](#beginaligned12cdot33)
- [13(104-3\cdot33)\
&=
41\cdot33](#13104-3cdot3341cdot33)
- [\[
\begin${aligned}
1
&=
41(137-104)](#beginaligned141137-104)
- [13\cdot104\
&=
41\cdot137](#13cdot10441cdot137)
- [\[
\begin${aligned}
1
&=
41\cdot137](#beginaligned141cdot137)
- [54(1337-9\cdot137)\
&=
527\cdot137](#541337-9cdot137527cdot137)
- [Python and SageMath implementations](#python-and-sagemath-implementations)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## The integers

The set of integers is

\[
\mathbb Z
=
\{\ldots,-3,-2,-1,0,1,2,3,\ldots\}.
\]

The integers extend the natural numbers by including zero and additive inverses.

If

\[
a\in\mathbb Z,
\]

then there also exists

\[
-a\in\mathbb Z
\]

such that

\[
a+(-a)=0.
\]

This gives us subtraction naturally:

\[
a-b
=
a+(-b).
\]

### Closure

The integers are closed under:

- addition,
- subtraction,
- multiplication.

Thus, for

\[
a,b\in\mathbb Z,
\]

we have

\[
a+b\in\mathbb Z,
\]

\[
a-b\in\mathbb Z,
\]

and

\[
ab\in\mathbb Z.
\]

Division is different.

For example,

\[
\frac{7}{2}\notin\mathbb Z.
\]

That simple observation leads directly to the notion of **divisibility**.

---

## Divisibility

Let

\[
a,b\in\mathbb Z.
\]

We say that \(a\) **divides** \(b\), written

\[
a\mid b,
\]

if there exists some integer

\[
k\in\mathbb Z
\]

such that

\[
b=ak.
\]

For example,

\[
5\mid15
\]

because

\[
15=5\cdot3.
\]

But

\[
5\nmid17
\]

because no integer \(k\) satisfies

\[
17=5k.
\]

When

\[
a\mid b,
\]

we may say that:

- \(a\) is a **divisor** or **factor** of \(b\),
- \(b\) is a **multiple** of \(a\).

### Basic properties

Let

\[
a,b,c,x,y\in\mathbb Z.
\]

Divisibility satisfies several useful properties.

First,

\[
a\mid a.
\]

Indeed,

\[
a=a\cdot1.
\]

If

\[
a\mid b
\]

and

\[
b\mid c,
\]

then

\[
a\mid c.
\]

To see this, write

\[
b=ak
\]

and

\[
c=b\ell.
\]

Then

\[
c=(ak)\ell=a(k\ell),
\]

and since

\[
k\ell\in\mathbb Z,
\]

we obtain

\[
a\mid c.
\]

Divisibility is also preserved under integer linear combinations.

If

\[
a\mid b
\]

and

\[
a\mid c,
\]

then for every

\[
x,y\in\mathbb Z,
\]

we have

\[
\boxed{
a\mid(bx+cy).
}
\]

Indeed, if

\[
b=ak
\qquad\text{and}\qquad
c=a\ell,
\]

then

\[
bx+cy
=
a(kx+\ell y).
\]

This small fact will become extremely important when we reach the GCD and Bézout's identity.

Finally, if

\[
a\mid b
\]

and

\[
b\mid a,
\]

then

\[
|a|=|b|,
\]

or equivalently,

\[
a=\pm b.
\]

### Even and odd integers

The language of divisibility immediately gives the standard definitions of parity.

An integer \(n\) is **even** exactly when

\[
2\mid n.
\]

So there exists some

\[
k\in\mathbb Z
\]

such that

\[
n=2k.
\]

An integer is **odd** exactly when it can be written as

\[
n=2k+1.
\]

The familiar decimal rule saying that an integer ending in

```text
0, 2, 4, 6, 8
```

is divisible by \(2\) is therefore only a convenient representation-level test for the deeper property

\[
2\mid n.
\]

---

## Euclidean division and remainders

One of the most important facts about the integers is the **Division Algorithm**, also called **Euclidean division**.

Let

\[
a\in\mathbb Z
\]

and let

\[
b\in\mathbb Z,
\qquad
b>0.
\]

Then there exist unique integers

\[
q,r\in\mathbb Z
\]

such that

\[
\boxed{
a=bq+r,
\qquad
0\le r<b.
}
\]

The integer \(q\) is the **quotient**.

The integer \(r\) is the **remainder**.

For example,

\[
17=5\cdot3+2.
\]

So dividing \(17\) by \(5\) gives

\[
q=3
\]

and

\[
r=2.
\]

### Negative integers

The remainder convention becomes particularly important when the dividend is negative.

Consider

\[
a=-17,
\qquad
b=5.
\]

We require

\[
0\le r<5.
\]

The correct Euclidean decomposition is

\[
-17
=
5(-4)+3.
\]

Thus,

\[
q=-4,
\qquad
r=3.
\]

Notice that

\[
-17=5(-3)-2
\]

is algebraically true, but

\[
r=-2
\]

does not satisfy our chosen remainder condition

\[
0\le r<5.
\]

The remainder convention removes this ambiguity.

### Quotient and floor

For positive divisor \(b\),

\[
q
=
\left\lfloor
\frac{a}{b}
\right\rfloor.
\]

Then

\[
r
=
a-b
\left\lfloor
\frac{a}{b}
\right\rfloor.
\]

So:

\[
\boxed{
a
=
b
\left\lfloor
\frac{a}{b}
\right\rfloor
+
r.
}
\]

Python follows this convention when the divisor is positive:

```python
a = -17
b = 5

q = a // b
r = a % b

print(q)  # -4
print(r)  # 3

assert a == b * q + r
assert 0 <= r < b
```

### Remainder notation versus congruence notation

There is a useful notational distinction here.

We may write the remainder as

\[
r=a\bmod b.
\]

For example,

\[
17\bmod5=2.
\]

Congruence notation expresses the corresponding equivalence relation:

\[
17\equiv2\pmod5.
\]

These statements are closely related, but

\[
a\bmod b
\]

is an operation producing a canonical remainder, whereas

\[
a\equiv r\pmod b
\]

is a relation between integers.

This distinction becomes important once modular arithmetic becomes a subject in its own right.

---

## Greatest common divisor and least common multiple

Divisibility naturally leads to the question:

> Which integers divide two numbers simultaneously?

Let

\[
a,b\in\mathbb Z.
\]

An integer \(c\) is a **common divisor** of \(a\) and \(b\) if

\[
c\mid a
\]

and

\[
c\mid b.
\]

### Greatest common divisor

For integers \(a\) and \(b\), not both zero, the **greatest common divisor**

\[
\gcd(a,b)
\]

is the unique positive integer \(d\) satisfying:

\[
d\mid a,
\]

\[
d\mid b,
\]

and every common divisor \(c\) of \(a\) and \(b\) also satisfies

\[
c\mid d.
\]

For example, the positive common divisors of \(48\) and \(18\) are

\[
1,2,3,6.
\]

Therefore,

\[
\gcd(48,18)=6.
\]

By convention,

\[
\gcd(a,0)=|a|
\]

and

\[
\gcd(0,0)=0.
\]

Two integers are called **coprime** or **relatively prime** when

\[
\gcd(a,b)=1.
\]

For example,

\[
\gcd(35,12)=1.
\]

This condition will later become central to modular inverses and RSA.

### Least common multiple

For nonzero integers \(a\) and \(b\), the **least common multiple**

\[
\operatorname{lcm}(a,b)
\]

is the smallest positive integer divisible by both:

\[
a\mid\operatorname{lcm}(a,b)
\]

and

\[
b\mid\operatorname{lcm}(a,b).
\]

If either argument is zero, we conventionally define

\[
\operatorname{lcm}(a,0)=0.
\]

The GCD and LCM satisfy the fundamental identity

\[
\boxed{
\gcd(a,b)\operatorname{lcm}(a,b)=|ab|
}
\]

for integers \(a,b\) not both zero.

Therefore,

\[
\operatorname{lcm}(a,b)
=
\frac{|ab|}{\gcd(a,b)}.
\]

For positive integers this simplifies to

\[
\operatorname{lcm}(a,b)
=
\frac{ab}{\gcd(a,b)}.
\]

For example,

\[
\gcd(12,18)=6,
\]

so

\[
\operatorname{lcm}(12,18)
=
\frac{12\cdot18}{6}
=
36.
\]

---

## The Euclidean algorithm

Finding all divisors of two integers and comparing them would be a poor way to compute a GCD for large inputs.

The Euclidean algorithm uses something much more powerful:

\[
\boxed{
\gcd(a,b)
=
\gcd(b,a\bmod b).
}
\]

Why is this true?

Suppose Euclidean division gives

\[
a=bq+r.
\]

Then

\[
r=a-bq.
\]

If some integer \(d\) divides both \(a\) and \(b\), then

\[
d\mid(a-bq),
\]

so

\[
d\mid r.
\]

Thus every common divisor of \(a\) and \(b\) is also a common divisor of \(b\) and \(r\).

Conversely, if

\[
d\mid b
\]

and

\[
d\mid r,
\]

then from

\[
a=bq+r
\]

we obtain

\[
d\mid a.
\]

Therefore the two pairs

\[
(a,b)
\]

and

\[
(b,r)
\]

have exactly the same common divisors.

Hence,

\[
\gcd(a,b)=\gcd(b,r).
\]

Since

\[
r=a\bmod b,
\]

we obtain the Euclidean step.

### Example: \(\gcd(1337,137)\)

Apply repeated Euclidean division:

\[
\begin{aligned}
1337 &= 137\cdot9 + 104,\\
137  &= 104\cdot1 + 33,\\
104  &= 33\cdot3 + 5,\\
33   &= 5\cdot6 + 3,\\
5    &= 3\cdot1 + 2,\\
3    &= 2\cdot1 + 1,\\
2    &= 1\cdot2 + 0.
\end{aligned}
\]

The last nonzero remainder is

\[
1.
\]

Therefore,

\[
\boxed{
\gcd(1337,137)=1.
}
\]

So \(1337\) and \(137\) are coprime.

The important point is that the algorithm rapidly reduces the size of the problem.

Instead of enumerating divisors, it repeatedly replaces

\[
(a,b)
\]

with

\[
(b,a\bmod b).
\]

The Euclidean algorithm runs in time polynomial in the bit length of its inputs; more concretely, it requires only \(O(\log \min(|a|,|b|))\) division steps.

This efficiency is one reason the GCD is so useful even for cryptographically large integers.

---

## The Extended Euclidean Algorithm

The ordinary Euclidean algorithm computes

\[
\gcd(a,b).
\]

The **Extended Euclidean Algorithm** gives us something more powerful.

It also finds integers

\[
x,y\in\mathbb Z
\]

such that

\[
\boxed{
\gcd(a,b)=ax+by.
}
\]

This is **Bézout's identity**, and \(x\) and \(y\) are called **Bézout coefficients**.

For our previous example,

\[
\gcd(1337,137)=1.
\]

So Bézout's identity guarantees integers \(x,y\) satisfying

\[
1337x+137y=1.
\]

The Euclidean algorithm already produced the equations we need.

Starting from

\[
1=3-2,
\]

substitute

\[
2=5-3:
\]

\[
1
=
3-(5-3)
=
2\cdot3-5.
\]

Now substitute

\[
3=33-6\cdot5:
\]

\[
1
=
2(33-6\cdot5)-5
=
2\cdot33-13\cdot5.
\]

Since

\[
5=104-3\cdot33,
\]

we obtain

\[
\begin{aligned}
1
&=
2\cdot33
-
13(104-3\cdot33)\\
&=
41\cdot33
-
13\cdot104.
\end{aligned}
\]

Now use

\[
33=137-104:
\]

\[
\begin{aligned}
1
&=
41(137-104)
-
13\cdot104\\
&=
41\cdot137
-
54\cdot104.
\end{aligned}
\]

Finally,

\[
104=1337-9\cdot137.
\]

Therefore,

\[
\begin{aligned}
1
&=
41\cdot137
-
54(1337-9\cdot137)\\
&=
527\cdot137
-
54\cdot1337.
\end{aligned}
\]

So:

\[
\boxed{
1
=
1337(-54)
+
137(527).
}
\]

The Bézout coefficients are therefore

\[
x=-54,
\qquad
y=527.
\]

Check:

\[
1337(-54)+137(527)=1.
\]

This identity is not merely a pleasant consequence of the Euclidean algorithm.

It will soon give us modular inverses.

If

\[
\gcd(a,n)=1,
\]

then Bézout tells us that

\[
ax+ny=1.
\]

Reducing modulo \(n\),

\[
ax\equiv1\pmod n.
\]

So \(x\) is a multiplicative inverse of \(a\) modulo \(n\).

That is the bridge from the Extended Euclidean Algorithm to modular arithmetic.

---

## Python and SageMath implementations

The mathematics maps almost directly into code.

### Recursive Euclidean algorithm

For nonnegative inputs:

```python
def gcd_recursive(a, b):
    if b == 0:
        return a

    return gcd_recursive(
        b,
        a % b,
    )
```

Example:

```python
assert gcd_recursive(48, 18) == 6
assert gcd_recursive(1337, 137) == 1
```

### Iterative Euclidean algorithm

The iterative version is usually more practical:

```python
def gcd_iterative(a, b):
    a = abs(a)
    b = abs(b)

    while b != 0:
        a, b = b, a % b

    return a
```

Now:

```python
assert gcd_iterative(48, 18) == 6
assert gcd_iterative(1337, 137) == 1
assert gcd_iterative(0, 15) == 15
assert gcd_iterative(15, 0) == 15
```

### Verbose Euclidean algorithm

For learning, it is useful to print every division step:

```python
def gcd_verbose(a, b):
    a = abs(a)
    b = abs(b)

    while b != 0:
        q = a // b
        r = a % b

        print(
            f"{a} = {b} * {q} + {r}"
        )

        a, b = b, r

    return a
```

Run:

```python
g = gcd_verbose(1337, 137)

print("gcd =", g)
```

and the program exposes exactly the same sequence we wrote mathematically.

### Extended Euclidean Algorithm

A compact recursive implementation is:

```python
def xgcd(a, b):
    if b == 0:
        return abs(a), 1 if a >= 0 else -1, 0

    g, x1, y1 = xgcd(b, a % b)

    x = y1
    y = x1 - (a // b) * y1

    return g, x, y
```

For our positive example:

```python
g, x, y = xgcd(1337, 137)

print(g)  # 1
print(x)  # -54
print(y)  # 527

assert g == 1
assert 1337 * x + 137 * y == g
```

The final assertion is the important part:

```python
assert 1337 * x + 137 * y == g
```

We are turning Bézout's identity into an executable invariant.

### Python standard library

Once we understand the algorithm, normal code usually uses the standard implementation:

```python
from math import gcd, lcm

print(gcd(1337, 137))
print(lcm(12, 18))
```

There is no reason to reimplement the Euclidean algorithm every time we need a GCD.

The purpose of implementing it ourselves is different:

> We want to understand the mathematics that the library call is compressing into one line.

### SageMath

SageMath provides the same objects directly:

```python
gcd(1337, 137)
```

and:

```python
xgcd(1337, 137)
```

The extended version returns values corresponding to

\[
(g,x,y)
\]

such that

\[
g=ax+by.
\]

This is a recurring pattern in computational mathematics.

We first construct an algorithm from first principles.

Later, we use optimized library implementations.

The abstraction is useful precisely because we understand what it represents.

---

## Why this matters in cryptography

Almost every concept in this article will reappear.

### Modular inverses

The condition

\[
\gcd(a,n)=1
\]

is exactly the condition that allows \(a\) to have a multiplicative inverse modulo \(n\).

Bézout's identity gives us the inverse constructively.

### RSA

RSA key generation requires conditions such as

\[
\gcd(e,\lambda(N))=1.
\]

The private exponent is then obtained as a modular inverse:

\[
d=e^{-1}\pmod{\lambda(N)}.
\]

So the Euclidean algorithm sits directly inside RSA key generation.

### Shared-prime RSA failures

If two RSA public moduli accidentally share a secret prime,

\[
N_1=pq_1,
\]

\[
N_2=pq_2,
\]

then

\[
\gcd(N_1,N_2)=p.
\]

One GCD factors both public keys.

### CRT fault attacks

Later, in a faulty CRT-RSA computation, we encounter expressions such as

\[
\gcd(S-\widetilde S,N),
\]

where the same elementary operation reveals a secret factor of the RSA modulus.

### Group arithmetic

Coprimality determines which residues belong to the multiplicative group

\[
\mathbb Z_n^\times.
\]

An integer \(a\) is invertible modulo \(n\) exactly when

\[
\gcd(a,n)=1.
\]

So the progression is already visible:

```text
divisibility
      ↓
GCD
      ↓
Bézout
      ↓
modular inverse
      ↓
multiplicative groups
      ↓
public-key cryptography
```

Elementary number theory does not sit outside cryptography.

It is part of its computational language.

---

## Practice and checkpoint

### Exercise 1 — Euclidean division

Write \(83\) in the form

\[
83=7q+r,
\qquad
0\le r<7.
\]

Then do the same for

\[
-83.
\]

Verify both using Python's:

```python
//
```

and:

```python
%
```

operators.

### Exercise 2 — Divisibility

Determine which statements are true:

\[
4\mid20,
\]

\[
6\mid20,
\]

\[
7\mid0,
\]

\[
0\mid7.
\]

For every true statement, exhibit the corresponding integer \(k\).

### Exercise 3 — GCD and LCM

Compute:

\[
\gcd(84,30)
\]

and then use

\[
\operatorname{lcm}(a,b)
=
\frac{|ab|}{\gcd(a,b)}
\]

to determine

\[
\operatorname{lcm}(84,30).
\]

Verify the result with Python.

### Exercise 4 — Euclidean algorithm

Compute

\[
\gcd(252,198)
\]

by hand using repeated Euclidean division.

Then compare your steps with:

```python
gcd_verbose(252, 198)
```

### Exercise 5 — Bézout coefficients

Use the Extended Euclidean Algorithm to find integers \(x\) and \(y\) satisfying

\[
252x+198y
=
\gcd(252,198).
\]

Verify the identity in Python.

### Reader checkpoint

You should now be able to explain:

1. What
   \[
   a\mid b
   \]
   actually means.

2. Why every integer \(a\) can be written uniquely as
   \[
   a=bq+r,
   \qquad
   0\le r<b
   \]
   when \(b>0\).

3. Why
   \[
   -17=5(-4)+3
   \]
   uses remainder \(3\), not \(-2\), under the Euclidean convention.

4. The difference between
   \[
   a\bmod n
   \]
   and
   \[
   a\equiv r\pmod n.
   \]

5. What \(\gcd(a,b)\) represents.

6. Why
   \[
   \gcd(a,b)
   =
   \gcd(b,a\bmod b).
   \]

7. What Bézout coefficients are.

8. Why
   \[
   \gcd(a,n)=1
   \]
   will soon imply that \(a\) has a modular inverse modulo \(n\).

If these ideas are clear, then the next step follows naturally.

---

## References and further reading

For a deeper treatment of the material in this reference:

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical and much deeper treatment of elementary number theory and its broader structure.

**Ivan Niven, Herbert S. Zuckerman, and Hugh L. Montgomery**,  
*An Introduction to the Theory of Numbers.*

A standard reference covering divisibility, congruences, primes, and related elementary number theory.

**Kenneth H. Rosen**,  
*Elementary Number Theory and Its Applications.*

A particularly accessible bridge between elementary theory and computational applications.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

The early chapters connect exactly these number-theoretic ideas to practical cryptography.

The value of these references is not that we need more complicated definitions of the GCD.

It is that they show how quickly elementary arithmetic grows into the algebraic machinery used throughout cryptography.

---

## Next

We have now built the chain

\[
\text{division}
\rightarrow
\text{divisibility}
\rightarrow
\gcd
\rightarrow
\text{Euclidean algorithm}
\rightarrow
\text{Bézout identity}.
\]

The next step is already hidden inside the final equation.

If

\[
\gcd(a,n)=1,
\]

then Bézout gives

\[
ax+ny=1.
\]

Reducing modulo \(n\),

\[
ax\equiv1\pmod n.
\]

So \(x\) is something new:

\[
\boxed{
x=a^{-1}\pmod n.
}
\]

That takes us from divisibility into **congruences and modular inverses**, where arithmetic begins behaving like the algebra used directly in cryptographic constructions.

**Next: Number Theory Reference II — Congruences, Modular Arithmetic, and Multiplicative Inverses.**
