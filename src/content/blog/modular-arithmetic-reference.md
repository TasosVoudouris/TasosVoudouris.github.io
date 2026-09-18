---
title: "Number Theory Reference II: Modular Arithmetic"
description: "A detailed reference on congruences, residues, residue classes, modular computation, units, multiplicative inverses, and the arithmetic structure used throughout cryptography."
pubDate: "2025-04-26"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "modular-arithmetic"
  - "congruences"
  - "residues"
  - "units"
  - "inverses"
difficulty: "Introductory"
series: "Elementary Number Theory Reference"
seriesOrder: 2
draft: false
---

In Part I, we developed the arithmetic machinery of the integers:

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

The final step already contained the beginning of modular arithmetic.

If

\[
\gcd(a,n)=1,
\]

then Bézout tells us that there exist integers \(x,y\) such that

\[
ax+ny=1.
\]

Reducing the equation modulo \(n\) gives

\[
ax\equiv1\pmod n.
\]

So \(x\) behaves like a multiplicative inverse of \(a\).

This article develops the arithmetic system in which that statement lives.

We will distinguish a remainder from a congruence, construct residue classes, define the ring

\[
\mathbb Z/n\mathbb Z,
\]

identify its invertible elements, explain exactly when modular division is legal, and connect these ideas to efficient modular computation.

These concepts appear almost everywhere in classical cryptography.

---

## Table of Contents

- [Congruence modulo (n)](#congruence-modulo-n)
- [Residues and residue classes](#residues-and-residue-classes)
- [Complete residue systems](#complete-residue-systems)
- [The structure of (\mathbb Z_n)](#the-structure-of-mathbb-z_n)
- [Arithmetic with congruences](#arithmetic-with-congruences)
- [Reduction during computation](#reduction-during-computation)
- [Cancellation and modular division](#cancellation-and-modular-division)
- [Units and modular inverses](#units-and-modular-inverses)
- [Example: (137^${-1}\pmod${1337})](#example-137-1pmod1337)
- [The group of units](#the-group-of-units)
- [Efficient modular exponentiation](#efficient-modular-exponentiation)
- [Python and SageMath](#python-and-sagemath)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Congruence modulo \(n\)

Let

\[
a,b\in\mathbb Z
\]

and let

\[
n\in\mathbb Z,
\qquad
n>0.
\]

We say that \(a\) is **congruent to \(b\) modulo \(n\)** when

\[
n\mid(a-b).
\]

We write

\[
\boxed{
a\equiv b\pmod n.
}
\]

Equivalently, there exists an integer \(k\) such that

\[
a-b=kn.
\]

For example,

\[
23\equiv3\pmod5
\]

because

\[
23-3=20=4\cdot5.
\]

Likewise,

\[
-7\equiv3\pmod5
\]

because

\[
-7-3=-10=-2\cdot5.
\]

So modulo \(5\),

\[
\ldots,-7,-2,3,8,13,\ldots
\]

all represent the same modular value.

### Congruence is not the same thing as `%`

In Python:

```python
23 % 5
```

returns:

```text
3
```

This computes the **least nonnegative remainder** for the positive modulus \(5\).

Mathematically, we may write:

\[
23\bmod5=3.
\]

But the statement

\[
23\equiv3\pmod5
\]

expresses something different.

The first is an operation:

\[
23\bmod5
\longrightarrow
3.
\]

The second is a relation:

\[
23
\sim
3
\]

because their difference is divisible by \(5\).

This distinction is worth keeping precise:

\[
\boxed{
a\bmod n
\text{ produces a representative}
}
\]

whereas

\[
\boxed{
a\equiv b\pmod n
\text{ says that }a\text{ and }b
\text{ belong to the same residue class}.
}
\]

---

## Residues and residue classes

The Division Algorithm tells us that every integer \(a\) can be written uniquely as

\[
a=qn+r,
\qquad
0\le r<n.
\]

Therefore,

\[
a-r=qn,
\]

so

\[
a\equiv r\pmod n.
\]

Thus every integer is congruent modulo \(n\) to exactly one value in

\[
\{0,1,2,\ldots,n-1\}.
\]

This unique value is the **least nonnegative residue** of \(a\) modulo \(n\).

For example,

\[
-17\bmod5=3
\]

because

\[
-17\equiv3\pmod5.
\]

### Residue classes

Instead of thinking only about one representative, we can collect every integer congruent to \(a\).

The residue class of \(a\) modulo \(n\) is

\[
[a]_n
=
\{
x\in\mathbb Z:
x\equiv a\pmod n
\}.
\]

For example, modulo \(4\):

\[
[0]_4
=
\{\ldots,-8,-4,0,4,8,\ldots\},
\]

\[
[1]_4
=
\{\ldots,-7,-3,1,5,9,\ldots\},
\]

\[
[2]_4
=
\{\ldots,-6,-2,2,6,10,\ldots\},
\]

and

\[
[3]_4
=
\{\ldots,-5,-1,3,7,11,\ldots\}.
\]

Every integer belongs to exactly one of these four classes.

That is because congruence modulo \(n\) is an **equivalence relation**.

It is reflexive:

\[
a\equiv a\pmod n.
\]

It is symmetric:

\[
a\equiv b\pmod n
\quad\Longrightarrow\quad
b\equiv a\pmod n.
\]

And it is transitive:

\[
a\equiv b\pmod n
\quad\text{and}\quad
b\equiv c\pmod n
\quad\Longrightarrow\quad
a\equiv c\pmod n.
\]

The equivalence classes partition \(\mathbb Z\).

---

## Complete residue systems

A set

\[
\{a_0,a_1,\ldots,a_{n-1}\}
\]

is a **complete residue system modulo \(n\)** if every residue class modulo \(n\) is represented exactly once.

The most familiar complete residue system is

\[
\{0,1,\ldots,n-1\}.
\]

But the representatives do not need to lie in that range.

For example,

\[
\{-12,-4,11,13,22,82,91\}
\]

forms a complete residue system modulo \(7\).

Indeed,

\[
\begin{aligned}
-12 &\equiv2\pmod7,\\
-4  &\equiv3\pmod7,\\
11  &\equiv4\pmod7,\\
13  &\equiv6\pmod7,\\
22  &\equiv1\pmod7,\\
82  &\equiv5\pmod7,\\
91  &\equiv0\pmod7.
\end{aligned}
\]

Every class

\[
[0]_7,[1]_7,\ldots,[6]_7
\]

appears exactly once.

---

## The structure of \(\mathbb Z_n\)

The set of residue classes modulo \(n\) is commonly written

\[
\mathbb Z/n\mathbb Z.
\]

In cryptographic and computational writing, the shorter notation

\[
\mathbb Z_n
\]

is also widely used.

Thus:

\[
\boxed{
\mathbb Z_n
=
\{
[0]_n,
[1]_n,
\ldots,
[n-1]_n
\}.
}
\]

There are exactly \(n\) residue classes.

Two classes are equal exactly when their representatives are congruent:

\[
[a]_n=[b]_n
\iff
a\equiv b\pmod n.
\]

### Addition

Define:

\[
[a]_n+[b]_n
=
[a+b]_n.
\]

For example, in \(\mathbb Z_7\),

\[
[5]_7+[6]_7
=
[11]_7
=
[4]_7.
\]

### Multiplication

Similarly,

\[
[a]_n[b]_n
=
[ab]_n.
\]

For example,

\[
[5]_7[3]_7
=
[15]_7
=
[1]_7.
\]

These operations are **well-defined**.

That means the result does not depend on which representative of the residue class we choose.

If

\[
a\equiv a'\pmod n
\]

and

\[
b\equiv b'\pmod n,
\]

then

\[
a+b\equiv a'+b'\pmod n
\]

and

\[
ab\equiv a'b'\pmod n.
\]

Therefore the arithmetic genuinely belongs to the equivalence classes themselves.

### Ring structure

With addition and multiplication modulo \(n\),

\[
\mathbb Z_n
\]

forms a **commutative ring with identity**.

The additive identity is

\[
[0]_n,
\]

and the multiplicative identity is

\[
[1]_n.
\]

But something important depends on \(n\).

If \(n\) is composite, not every nonzero element has a multiplicative inverse.

For example, in

\[
\mathbb Z_{15},
\]

the element

\[
[5]_{15}
\]

has no multiplicative inverse because

\[
\gcd(5,15)=5.
\]

By contrast, if \(p\) is prime, then every nonzero element of

\[
\mathbb Z_p
\]

is invertible.

In that case,

\[
\mathbb Z_p
\]

is a **field**.

We will study that distinction in greater depth later, but it is already one of the most important structural facts in cryptography.

---

## Arithmetic with congruences

Congruences behave much like ordinary equalities under addition and multiplication.

Suppose

\[
a\equiv b\pmod n
\]

and

\[
c\equiv d\pmod n.
\]

Then:

\[
a+c
\equiv
b+d
\pmod n.
\]

Likewise,

\[
a-c
\equiv
b-d
\pmod n.
\]

And:

\[
ac
\equiv
bd
\pmod n.
\]

For every nonnegative integer \(k\),

\[
a^k
\equiv
b^k
\pmod n.
\]

Thus:

\[
\boxed{
a\equiv b\pmod n
\Longrightarrow
f(a)\equiv f(b)\pmod n
}
\]

for expressions \(f\) constructed from addition and multiplication with integer coefficients.

This is why we are allowed to replace numbers by smaller congruent representatives during modular computations.

### Example

Suppose we want

\[
38\cdot47\pmod{13}.
\]

Reduce first:

\[
38\equiv12\pmod{13},
\]

and

\[
47\equiv8\pmod{13}.
\]

Therefore,

\[
38\cdot47
\equiv
12\cdot8
=
96
\equiv5
\pmod{13}.
\]

We never needed to preserve the original integers.

Only their residue classes mattered.

---

## Reduction during computation

One of the most practically useful properties of modular arithmetic is that reduction can happen after every arithmetic step.

For example:

```python
((17 + 38) * (105 - 193)) % 13
```

produces the same result as:

```python
(
    ((17 % 13) + (38 % 13))
    *
    ((105 % 13) - (193 % 13))
) % 13
```

Why?

Because:

\[
17
\equiv
17\bmod13
\pmod{13},
\]

and similarly for every other operand.

Addition, subtraction, and multiplication preserve congruence.

This prevents intermediate values from growing unnecessarily.

The advantage becomes especially important in exponentiation.

Suppose we want

\[
3^{999}\bmod1000.
\]

A simple educational loop is:

```python
result = 1

for _ in range(999):
    result = (result * 3) % 1000

print(result)
```

Every intermediate value remains below \(1000\).

This is already far better than carrying the complete integer \(3^{999}\) through the computation.

But we can do much better still.

Rather than performing \(999\) multiplications, binary exponentiation uses the bits of the exponent and requires only \(O(\log 999)\) squaring/multiplication steps.

We will return to that shortly.

---

## Cancellation and modular division

This is one of the places where modular arithmetic differs subtly from ordinary arithmetic.

Suppose

\[
ac\equiv bc\pmod n.
\]

Can we cancel \(c\) and conclude

\[
a\equiv b\pmod n?
\]

Not always.

### A counterexample

Consider modulo \(6\):

\[
2\cdot1
\equiv
2\cdot4
\pmod6.
\]

Indeed,

\[
2\equiv8\pmod6.
\]

But:

\[
1\not\equiv4\pmod6.
\]

So cancellation of the factor \(2\) failed.

Why?

Because

\[
\gcd(2,6)=2\neq1.
\]

The factor \(2\) is not invertible modulo \(6\).

### When cancellation is valid

If

\[
\gcd(c,n)=1,
\]

then \(c\) has a multiplicative inverse modulo \(n\).

Suppose:

\[
ac\equiv bc\pmod n.
\]

Multiply both sides by

\[
c^{-1}.
\]

Then:

\[
c^{-1}ac
\equiv
c^{-1}bc
\pmod n,
\]

so:

\[
\boxed{
a\equiv b\pmod n.
}
\]

Thus cancellation is valid when the factor being cancelled is a **unit**.

This gives the correct interpretation of modular division.

Writing informally

\[
\frac{a}{c}\pmod n
\]

means:

\[
a c^{-1}\pmod n,
\]

and this operation only makes sense when \(c^{-1}\) exists.

So:

\[
\boxed{
\text{division modulo }n
=
\text{multiplication by an inverse}.
}
\]

This distinction becomes crucial in RSA, elliptic curves, finite fields, secret sharing, and essentially every algebraic cryptographic construction.

---

## Units and modular inverses

Let

\[
a\in\mathbb Z
\]

and

\[
n>1.
\]

A **multiplicative inverse** of \(a\) modulo \(n\) is an integer \(x\) satisfying

\[
ax\equiv1\pmod n.
\]

If it exists, we write

\[
x\equiv a^{-1}\pmod n.
\]

This does **not** mean the real-number reciprocal

\[
\frac1a.
\]

It means an element of the modular arithmetic system satisfying the multiplicative identity relation.

### Existence criterion

The fundamental theorem is:

\[
\boxed{
a^{-1}\pmod n
\text{ exists}
\iff
\gcd(a,n)=1.
}
\]

This condition is both necessary and sufficient.

### Why Bézout gives the inverse

Suppose

\[
\gcd(a,n)=1.
\]

Bézout's identity guarantees integers \(u,v\) satisfying

\[
au+nv=1.
\]

Reduce modulo \(n\):

\[
au+nv
\equiv
1
\pmod n.
\]

Since

\[
nv\equiv0\pmod n,
\]

we obtain

\[
au\equiv1\pmod n.
\]

Therefore,

\[
\boxed{
u\equiv a^{-1}\pmod n.
}
\]

This is why the Extended Euclidean Algorithm computes modular inverses.

### Why the condition is necessary

Suppose instead that an inverse \(x\) exists:

\[
ax\equiv1\pmod n.
\]

Then for some integer \(k\),

\[
ax-kn=1.
\]

So \(1\) is an integer linear combination of \(a\) and \(n\).

Every common divisor of \(a\) and \(n\) must therefore divide \(1\).

Hence,

\[
\gcd(a,n)=1.
\]

So the equivalence really goes both ways.

---

## Example: \(137^{-1}\pmod{1337}\)

We want to solve

\[
137x\equiv1\pmod{1337}.
\]

From the Extended Euclidean Algorithm developed in Part I:

\[
1
=
1337(-54)
+
137(527).
\]

Reduce modulo \(1337\):

\[
137(527)
\equiv
1
\pmod{1337}.
\]

Therefore,

\[
\boxed{
137^{-1}\equiv527\pmod{1337}.
}
\]

Check:

\[
137\cdot527
=
72199.
\]

And:

\[
72199\bmod1337=1.
\]

In Python:

```python
inverse = pow(137, -1, 1337)

print(inverse)  # 527

assert (137 * inverse) % 1337 == 1
```

This is the exact computational meaning of the modular inverse.

---

## The group of units

The invertible residue classes modulo \(n\) form an important subset of \(\mathbb Z_n\).

Define:

\[
\mathbb Z_n^\times
=
\{
[a]_n:
\gcd(a,n)=1
\}.
\]

This is called the **group of units modulo \(n\)**.

For example, modulo \(10\),

\[
\mathbb Z_{10}
=
\{
[0],[1],[2],[3],[4],
[5],[6],[7],[8],[9]
\}.
\]

Only the classes represented by integers coprime to \(10\) are invertible:

\[
\boxed{
\mathbb Z_{10}^{\times}
=
\{
[1],[3],[7],[9]
\}.
}
\]

Check:

\[
3\cdot7
=
21
\equiv1\pmod{10},
\]

so:

\[
3^{-1}\equiv7\pmod{10}.
\]

Likewise:

\[
9^2=81\equiv1\pmod{10},
\]

so \(9\) is its own inverse.

The units form a group under multiplication modulo \(n\).

This object,

\[
\mathbb Z_n^\times,
\]

will become central when we study:

- Euler's theorem,
- RSA,
- finite-group cryptography,
- multiplicative orders,
- generators.

The number of units modulo \(n\) is given by Euler's totient function:

\[
\varphi(n)
=
|\mathbb Z_n^\times|.
\]

That will be developed in a later reference article.

---

## Efficient modular exponentiation

Expressions of the form

\[
a^e\bmod n
\]

appear constantly in cryptography.

RSA computes modular powers.

Diffie-Hellman computes modular powers.

Primality tests compute modular powers.

So efficiency matters.

There are three conceptually different approaches worth distinguishing.

### Full exponentiation followed by reduction

We could write:

```python
result = (base ** exponent) % modulus
```

This is mathematically correct.

But it first constructs the potentially enormous integer

\[
\text{base}^{\text{exponent}}
\]

and only then reduces it.

For large cryptographic exponents, this is not the right computational model.

### Repeated multiplication with reduction

A better educational version is:

```python
def powmod_repeated(base, exponent, modulus):
    result = 1

    for _ in range(exponent):
        result = (result * base) % modulus

    return result
```

Intermediate values remain bounded by the modulus.

But the algorithm still performs

\[
O(e)
\]

multiplications.

If \(e\) is a 2048-bit integer, that is completely impractical.

### Binary exponentiation

The correct algorithmic idea is **exponentiation by squaring**, also called binary exponentiation.

The exponent is processed through its binary representation.

For example,

\[
13=(1101)_2
=
8+4+1.
\]

So:

\[
a^{13}
=
a^8a^4a.
\]

The required powers can be generated by repeated squaring:

\[
a,
\quad
a^2,
\quad
a^4,
\quad
a^8,
\ldots
\]

This reduces the operation count to

\[
O(\log e).
\]

A simple right-to-left implementation is:

```python
def powmod_binary(base, exponent, modulus):
    result = 1
    base %= modulus

    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus

        base = (base * base) % modulus
        exponent >>= 1

    return result
```

Check:

```python
assert powmod_binary(3, 999, 1000) == pow(3, 999, 1000)
```

In normal Python code, use the optimized built-in operation:

```python
pow(base, exponent, modulus)
```

For example:

```python
result = pow(3, 999, 1000)

print(result)
```

The important computational lesson is:

\[
\boxed{
\text{three-argument } \operatorname{pow}
\text{ performs modular exponentiation efficiently}.
}
\]

It should generally be preferred to:

```python
(base ** exponent) % modulus
```

for large modular powers.

One cryptographic warning is also worth recording:

> Efficient does not automatically mean constant-time.

Python's ordinary big-integer operations are useful for mathematical experimentation, but should not be treated as a guarantee of production side-channel resistance.

That is a separate implementation-security problem.

---

## Python and SageMath

The basic modular operations are already available directly in Python.

### Least nonnegative remainder

```python
print(23 % 5)   # 3
print(-17 % 5)  # 3
```

### Modular exponentiation

```python
print(
    pow(3, 999, 1000)
)
```

### Modular inverse

Modern Python supports:

```python
inverse = pow(
    137,
    -1,
    1337,
)

print(inverse)  # 527
```

If the inverse does not exist:

```python
pow(6, -1, 15)
```

raises an error because

\[
\gcd(6,15)=3.
\]

### GCD check

```python
from math import gcd

a = 137
n = 1337

assert gcd(a, n) == 1

inverse = pow(a, -1, n)

assert (a * inverse) % n == 1
```

### SageMath

SageMath provides natural modular objects.

For example:

```python
R = Integers(17)

a = R(5)
b = R(9)

print(a + b)
print(a * b)
print(a**-1)
```

The value:

```python
R(5)
```

is not merely an ordinary Python integer.

It is an element of the ring

\[
\mathbb Z_{17}.
\]

That distinction becomes increasingly valuable as our mathematical objects become more sophisticated.

---

## Why this matters in cryptography

This article contains several ideas that later appear as actual cryptographic operations.

RSA requires:

\[
d
=
e^{-1}
\pmod{\lambda(N)}.
\]

Diffie-Hellman works with repeated multiplication and exponentiation inside finite groups.

Elliptic-curve arithmetic performs division by multiplying with finite-field inverses.

Shamir secret sharing reconstructs polynomials using divisions inside a finite field.

ECDSA contains expressions such as

\[
k^{-1}\pmod n.
\]

The Chinese Remainder Theorem works by constructing modular inverses.

Even many attacks depend on understanding exactly which modular operations are legal.

The central progression is:

\[
\boxed{
\text{congruence}
\rightarrow
\text{residue class}
\rightarrow
\text{ring}
\rightarrow
\text{unit}
\rightarrow
\text{inverse}
\rightarrow
\text{group arithmetic}.
}
\]

That progression is one of the main mathematical roads into cryptography.

---

## Practice and checkpoint

### Exercise 1 — Congruence

Determine whether each statement is true:

\[
38\equiv3\pmod5,
\]

\[
-12\equiv2\pmod7,
\]

\[
41\equiv5\pmod9.
\]

For each one, verify whether the modulus divides the difference.

### Exercise 2 — Least nonnegative residues

Find:

\[
37\bmod8,
\]

\[
-37\bmod8,
\]

and

\[
1234\bmod17.
\]

Verify the results using Python.

### Exercise 3 — Residue classes

Write the four residue classes modulo \(4\).

Then determine which class contains:

\[
123.
\]

### Exercise 4 — Complete residue system

Determine whether

\[
\{2,5,8,11,14\}
\]

is a complete residue system modulo \(5\).

Do not look only at the number of elements.

Reduce each value modulo \(5\).

### Exercise 5 — Units

Find every element of

\[
\mathbb Z_{12}^{\times}.
\]

Hint:

\[
[a]_{12}
\]

is invertible exactly when

\[
\gcd(a,12)=1.
\]

### Exercise 6 — Modular inverses

Compute:

\[
7^{-1}\pmod{26}.
\]

Then verify:

\[
7x\equiv1\pmod{26}.
\]

Try the same question for:

\[
6^{-1}\pmod{15}.
\]

Explain why the second inverse does not exist.

### Exercise 7 — Cancellation

Consider:

\[
4x\equiv4y\pmod{10}.
\]

Can you always conclude:

\[
x\equiv y\pmod{10}?
\]

What goes wrong?

Now replace \(4\) with \(3\).

Why does cancellation become valid?

### Exercise 8 — Modular exponentiation

Compute:

\[
7^{12345}\bmod65537
\]

using:

```python
pow(7, 12345, 65537)
```

Then implement binary modular exponentiation yourself and verify that both methods agree.

### Reader checkpoint

You should now be able to explain:

1. What
   \[
   a\equiv b\pmod n
   \]
   means in terms of divisibility.

2. The difference between
   \[
   a\bmod n
   \]
   and
   \[
   a\equiv b\pmod n.
   \]

3. What a residue class is.

4. Why there are exactly \(n\) residue classes modulo \(n\).

5. Why addition and multiplication of residue classes are well-defined.

6. Why \(\mathbb Z_n\) is a ring.

7. Why not every nonzero element of \(\mathbb Z_n\) is necessarily invertible.

8. Why
   \[
   a^{-1}\pmod n
   \]
   exists exactly when
   \[
   \gcd(a,n)=1.
   \]

9. Why modular division means multiplication by an inverse.

10. Why cancellation can fail when the cancelled factor is not a unit.

11. What
    \[
    \mathbb Z_n^\times
    \]
    represents.

12. Why binary modular exponentiation is fundamentally better than repeated multiplication for large exponents.

If these distinctions are clear, we are ready to study the multiplicative structure of modular arithmetic much more deeply.

---

## References and further reading

**Kenneth H. Rosen**,  
*Elementary Number Theory and Its Applications.*

A clear reference for congruences, residue classes, modular inverses, and elementary modular arithmetic.

**Ivan Niven, Herbert S. Zuckerman, and Hugh L. Montgomery**,  
*An Introduction to the Theory of Numbers.*

A classical treatment of congruences and elementary number-theoretic structure.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Particularly useful for connecting the abstract mathematics to efficient computation.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

The early mathematical chapters show how congruences, inverses, modular exponentiation, and multiplicative groups enter concrete cryptographic systems.

---

## Next

We now understand arithmetic in

\[
\mathbb Z_n.
\]

But multiplication reveals a smaller and even more important object inside it:

\[
\mathbb Z_n^\times.
\]

This is the set of invertible residue classes.

Its size is

\[
\varphi(n),
\]

its elements form a group, and their powers eventually repeat.

That leads naturally to:

- Euler's totient function,
- multiplicative order,
- Euler's theorem,
- Fermat's little theorem,
- cyclic subgroups,
- generators.

Those ideas form the bridge from modular arithmetic to the group structures used directly in public-key cryptography.

**Next: Number Theory Reference III — Euler's Totient Function, Units, Orders, and Modular Exponentiation.**
