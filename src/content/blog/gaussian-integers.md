---
title: "Computational Number Theory III: Gaussian Integers, Norms, Units, and Euclidean Division"
description: "Arithmetic in Z[i]: conjugation, norm, units, divisibility, exact Euclidean division, Gaussian gcds, unique factorization, and the splitting behavior of rational primes."
pubDate: "2025-04-23"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Abstract Algebra"
tags:
  - "gaussian-integers"
  - "euclidean-domain"
  - "norm"
  - "sum-of-two-squares"
  - "prime-splitting"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 3
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

The ordinary integers form only one arithmetic universe.

A natural enlargement is obtained by adjoining a square root of $-1$:

$$
i^2=-1.
$$

This gives the ring of **Gaussian integers**:

$$
\boxed{
\mathbb Z[i]
=
\{
a+bi:
a,b\in\mathbb Z
\}.
}
$$

At first this looks like a simple two-dimensional version of $\mathbb Z$.

But something much deeper survives.

We still have:

- divisibility,
- units,
- primes,
- greatest common divisors,
- a Euclidean algorithm,
- unique factorization.

The crucial function making this possible is the norm:

$$
\boxed{
N(a+bi)=a^2+b^2.
}
$$

Geometrically, this is squared Euclidean distance from the origin.

Arithmetically, it is multiplicative.

That combination makes $\mathbb Z[i]$ one of the cleanest examples of geometry controlling arithmetic.

The central progression is:

$$
\boxed{
\text{Gaussian integer}
\rightarrow
\text{norm}
\rightarrow
\text{Euclidean division}
\rightarrow
\gcd
\rightarrow
\text{factorization}
\rightarrow
\text{prime splitting}.
}
$$

---

## Table of Contents

- [Gaussian integers, conjugation, and norm](#gaussian-integers-conjugation-and-norm)
- [Units, associates, and divisibility](#units-associates-and-divisibility)
- [Euclidean division in the complex plane](#euclidean-division-in-the-complex-plane)
- [Gaussian gcds and unique factorization](#gaussian-gcds-and-unique-factorization)
- [Gaussian primes and rational prime splitting](#gaussian-primes-and-rational-prime-splitting)
- [Sums of two squares and quadratic residues](#sums-of-two-squares-and-quadratic-residues)
- [Exact computational implementation](#exact-computational-implementation)
- [Geometry and arithmetic meet](#geometry-and-arithmetic-meet)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Gaussian integers, conjugation, and norm

A Gaussian integer has the form:

$$
z=a+bi,
\qquad
a,b\in\mathbb Z.
$$

Addition and multiplication are inherited from the complex numbers:

$$
(a+bi)+(c+di)
=
(a+c)+(b+d)i,
$$

and:

$$
(a+bi)(c+di)
=
(ac-bd)+(ad+bc)i.
$$

Because both coefficients remain integers:

$$
\mathbb Z[i]
$$

is closed under these operations.

It is therefore a commutative ring.

---

### Conjugation

For:

$$
z=a+bi,
$$

define the complex conjugate:

$$
\boxed{
\overline z=a-bi.
}
$$

Conjugation satisfies:

$$
\overline{z+w}
=
\overline z+\overline w
$$

and:

$$
\boxed{
\overline{zw}
=
\overline z\,\overline w.
}
$$

Also:

$$
\overline{\overline z}=z.
$$

---

### The norm

Define:

$$
\boxed{
N(z)
=
z\overline z.
}
$$

For:

$$
z=a+bi,
$$

we obtain:

$$
N(z)
=
(a+bi)(a-bi)
=
a^2+b^2.
$$

Therefore:

$$
\boxed{
N(a+bi)=a^2+b^2.
}
$$

The norm takes values in:

$$
\mathbb Z_{\ge0}.
$$

Moreover:

$$
N(z)=0
\iff
z=0.
$$

Geometrically:

$$
N(z)=|z|^2.
$$

So the norm is the **squared Euclidean length** of the corresponding lattice point.

---

### Multiplicativity of the norm

One of the central facts is:

$$
\boxed{
N(zw)
=
N(z)N(w).
}
$$

Indeed:

$$
\begin{aligned}
N(zw)
&=
zw\overline{zw}\\
&=
zw\overline z\,\overline w\\
&=
z\overline z\,w\overline w\\
&=
N(z)N(w).
\end{aligned}
$$

This converts multiplication inside:

$$
\mathbb Z[i]
$$

into multiplication of ordinary nonnegative integers.

That makes the norm a powerful arithmetic invariant.

---

### Norm and divisibility

If:

$$
\alpha\mid\beta
$$

in:

$$
\mathbb Z[i],
$$

then:

$$
\beta=\alpha\gamma
$$

for some:

$$
\gamma\in\mathbb Z[i].
$$

Taking norms:

$$
N(\beta)
=
N(\alpha)N(\gamma).
$$

Therefore:

$$
\boxed{
N(\alpha)\mid N(\beta)
}
$$

inside:

$$
\mathbb Z.
$$

The converse is not generally true.

Norm divisibility is therefore a necessary condition for Gaussian divisibility, not a sufficient one.

---

## Units, associates, and divisibility

An element:

$$
u\in\mathbb Z[i]
$$

is a unit if there exists:

$$
v\in\mathbb Z[i]
$$

such that:

$$
uv=1.
$$

Taking norms:

$$
N(u)N(v)=1.
$$

Since the norms are nonnegative integers:

$$
N(u)=1.
$$

Thus:

$$
a^2+b^2=1.
$$

The only integer solutions are:

$$
(\pm1,0),
\qquad
(0,\pm1).
$$

Therefore:

$$
\boxed{
\mathbb Z[i]^\times
=
\{
1,-1,i,-i
\}.
}
$$

---

### Associates

Two Gaussian integers:

$$
\alpha,
\beta
$$

are **associates** if:

$$
\alpha=u\beta
$$

for a unit:

$$
u\in\{1,-1,i,-i\}.
$$

Thus:

$$
z,
\quad
-z,
\quad
iz,
\quad
-iz
$$

all represent the same factor up to multiplication by a unit.

For example:

$$
2+i
$$

has associates:

$$
2+i,
$$

$$
-2-i,
$$

$$
-1+2i,
$$

$$
1-2i.
$$

All have the same norm:

$$
5.
$$

---

### Why gcds are unique only up to units

Suppose:

$$
d
$$

is a gcd of:

$$
\alpha,\beta.
$$

Then:

$$
id
$$

divides both as well.

Likewise:

$$
-d
$$

and:

$$
-id.
$$

Therefore Gaussian gcds are not naturally represented by one unique element.

Instead they are unique **up to multiplication by a unit**.

This is analogous to ordinary integer gcds being unique up to sign before we impose the convention:

$$
\gcd(a,b)>0.
$$

---

## Euclidean division in the complex plane

The crucial theorem is that Gaussian integers admit Euclidean division.

Let:

$$
\alpha,\beta\in\mathbb Z[i],
\qquad
\beta\neq0.
$$

We want:

$$
\boxed{
\alpha
=
q\beta+r
}
$$

with:

$$
q,r\in\mathbb Z[i]
$$

and:

$$
\boxed{
N(r)<N(\beta).
}
$$

---

### Divide in $\mathbb C$

Compute:

$$
\frac{\alpha}{\beta}.
$$

Using conjugation:

$$
\boxed{
\frac{\alpha}{\beta}
=
\frac{
\alpha\overline\beta
}{
N(\beta)
}.
}
$$

This is generally a complex number, not a Gaussian integer.

Write:

$$
\frac{\alpha}{\beta}
=
x+yi,
\qquad
x,y\in\mathbb R.
$$

Choose integers:

$$
m,n
$$

nearest to:

$$
x,y.
$$

Then define:

$$
\boxed{
q=m+ni.
}
$$

Geometrically, $q$ is a nearest point of the square lattice:

$$
\mathbb Z[i]
\subset\mathbb C.
$$

Finally:

$$
\boxed{
r=\alpha-q\beta.
}
$$

---

### Why the remainder gets smaller

Because $m$ and $n$ are nearest integers:

$$
|x-m|
\le
\frac12
$$

and:

$$
|y-n|
\le
\frac12.
$$

Hence:

$$
\left|
\frac{\alpha}{\beta}-q
\right|^2
\le
\frac14+\frac14
=
\frac12.
$$

But:

$$
r
=
\beta
\left(
\frac{\alpha}{\beta}-q
\right).
$$

Therefore:

$$
N(r)
=
N(\beta)
\left|
\frac{\alpha}{\beta}-q
\right|^2.
$$

So:

$$
N(r)
\le
\frac12N(\beta).
$$

Since:

$$
\beta\neq0,
$$

we obtain:

$$
\boxed{
N(r)<N(\beta).
}
$$

Thus:

$$
\boxed{
\mathbb Z[i]
\text{ is a Euclidean domain with Euclidean function }N.
}
$$

---

### Worked example

Let:

$$
\alpha=7+5i
$$

and:

$$
\beta=3+2i.
$$

First:

$$
N(\beta)
=
3^2+2^2
=
13.
$$

Now:

$$
\frac{\alpha}{\beta}
=
\frac{
(7+5i)(3-2i)
}{
13
}.
$$

The numerator is:

$$
(7+5i)(3-2i)
=
31+i.
$$

Therefore:

$$
\frac{\alpha}{\beta}
=
\frac{31}{13}
+
\frac1{13}i.
$$

Numerically:

$$
\frac{\alpha}{\beta}
\approx
2.3846+0.0769i.
$$

The nearest Gaussian integer is:

$$
q=2.
$$

Hence:

$$
r
=
(7+5i)-2(3+2i).
$$

So:

$$
\boxed{
r=1+i.
}
$$

Its norm is:

$$
N(r)=2.
$$

Since:

$$
2<13,
$$

the Euclidean condition holds:

$$
\boxed{
N(r)<N(\beta).
}
$$

Thus:

$$
\boxed{
7+5i
=
2(3+2i)+(1+i).
}
$$

---

## Gaussian gcds and unique factorization

Once Euclidean division exists, the Euclidean algorithm works almost exactly as over:

$$
\mathbb Z.
$$

Given:

$$
\alpha,\beta\in\mathbb Z[i],
\qquad
\beta\neq0,
$$

perform:

$$
\alpha
=
q_0\beta+r_1,
$$

then:

$$
\beta
=
q_1r_1+r_2,
$$

then:

$$
r_1
=
q_2r_2+r_3,
$$

and continue.

The norms strictly decrease:

$$
N(\beta)
>
N(r_1)
>
N(r_2)
>
\cdots.
$$

Since norms are nonnegative integers, the process terminates.

The last nonzero remainder is a gcd, up to multiplication by a unit.

---

### Bézout identity

The Extended Euclidean Algorithm also works in:

$$
\mathbb Z[i].
$$

Therefore there exist:

$$
x,y\in\mathbb Z[i]
$$

such that:

$$
\boxed{
\gcd(\alpha,\beta)
=
x\alpha+y\beta.
}
$$

Again, the gcd is understood up to multiplication by a Gaussian unit.

---

### Euclidean domain to unique factorization

We now obtain the standard implication chain:

$$
\boxed{
\text{Euclidean domain}
\Longrightarrow
\text{PID}
\Longrightarrow
\text{UFD}.
}
$$

Therefore:

$$
\boxed{
\mathbb Z[i]
\text{ is a unique factorization domain}.
}
$$

Every nonzero nonunit Gaussian integer can be factored into Gaussian primes.

The factorization is unique up to:

- order;
- multiplication of factors by units.

---

### Example: factoring $5$

Inside:

$$
\mathbb Z,
$$

the integer:

$$
5
$$

is prime.

But in:

$$
\mathbb Z[i],
$$

we have:

$$
\boxed{
5
=
(2+i)(2-i).
}
$$

Indeed:

$$
(2+i)(2-i)
=
4+1
=
5.
$$

Moreover:

$$
N(2+i)
=
5.
$$

Because $5$ is an ordinary rational prime, $2+i$ cannot factor nontrivially in $\mathbb Z[i]$.

Thus:

$$
2+i
$$

and:

$$
2-i
$$

are Gaussian primes.

So an integer prime need not remain prime after enlarging the ring.

This is the beginning of **prime splitting**.

---

## Gaussian primes and rational prime splitting

A Gaussian integer:

$$
\pi=a+bi
$$

is a **Gaussian prime** if it is a nonzero nonunit whose only divisors are units and associates.

There is a complete classification.

---

### Case 1 — Both coordinates are nonzero

Suppose:

$$
a\neq0,
\qquad
b\neq0.
$$

Then:

$$
\boxed{
a+bi
\text{ is Gaussian prime}
\iff
a^2+b^2
\text{ is an ordinary prime}.
}
$$

For example:

$$
2+i
$$

has:

$$
N(2+i)=5,
$$

so it is Gaussian prime.

Similarly:

$$
3+2i
$$

has:

$$
N(3+2i)=13,
$$

so it is Gaussian prime.

---

### Case 2 — One coordinate is zero

Suppose:

$$
\pi=p
$$

is an ordinary positive rational prime regarded as a Gaussian integer.

Then:

$$
\boxed{
p
\text{ remains Gaussian prime}
\iff
p\equiv3\pmod4.
}
$$

So:

$$
3,
\quad
7,
\quad
11,
\quad
19,
\ldots
$$

remain prime in:

$$
\mathbb Z[i].
$$

By contrast, primes congruent to $1\pmod4$ split.

---

### Rational prime splitting

Let:

$$
p
$$

be an ordinary rational prime.

There are three cases.

#### Split primes

If:

$$
\boxed{
p\equiv1\pmod4,
}
$$

then:

$$
p
$$

splits:

$$
\boxed{
p
=
\pi\overline\pi
}
$$

for a Gaussian prime:

$$
\pi=a+bi.
$$

Equivalently:

$$
\boxed{
p=a^2+b^2.
}
$$

Example:

$$
5
=
2^2+1^2
=
(2+i)(2-i).
$$

Also:

$$
13
=
3^2+2^2
=
(3+2i)(3-2i).
$$

---

#### Inert primes

If:

$$
\boxed{
p\equiv3\pmod4,
}
$$

then $p$ remains prime in:

$$
\mathbb Z[i].
$$

Such a prime is called **inert** in this extension.

For example:

$$
3,
\quad
7,
\quad
11
$$

do not acquire nontrivial Gaussian factorizations.

---

#### The prime $2$

The prime:

$$
2
$$

behaves differently.

We have:

$$
(1+i)^2
=
1+2i+i^2
=
2i.
$$

Therefore:

$$
\boxed{
2
=
-i(1+i)^2.
}
$$

Since multiplication by:

$$
-i
$$

changes only by a unit, $2$ is essentially the square of the Gaussian prime:

$$
1+i.
$$

Thus:

$$
\boxed{
2
\text{ ramifies in }\mathbb Z[i].
}
$$

---

### The three-way pattern

The complete behavior is:

$$
\boxed{
p\equiv1\pmod4
\Longrightarrow
p\text{ splits},
}
$$

$$
\boxed{
p\equiv3\pmod4
\Longrightarrow
p\text{ remains prime},
}
$$

and:

$$
\boxed{
2
\text{ ramifies}.
}
$$

This is one of the simplest examples of a general theme in algebraic number theory:

> prime numbers behave differently when arithmetic is extended to a larger ring.

---

## Sums of two squares and quadratic residues

The splitting criterion has several equivalent interpretations.

For an odd rational prime $p$:

$$
\boxed{
p\equiv1\pmod4
}
$$

is equivalent to:

$$
\boxed{
p=a^2+b^2
}
$$

for integers:

$$
a,b.
$$

It is also equivalent to:

$$
\boxed{
x^2\equiv-1\pmod p
}
$$

having a solution.

And this is equivalent to:

$$
\boxed{
-1
\text{ being a quadratic residue modulo }p.
}
$$

---

### Why splitting gives a sum of two squares

Suppose:

$$
p
=
\pi\overline\pi
$$

with:

$$
\pi=a+bi.
$$

Taking norms:

$$
N(\pi)
=
a^2+b^2.
$$

Since:

$$
N(p)=p^2
$$

and:

$$
N(\pi)N(\overline\pi)
=
N(\pi)^2,
$$

we obtain:

$$
N(\pi)=p.
$$

Therefore:

$$
\boxed{
p=a^2+b^2.
}
$$

---

### Why $-1$ appears

Suppose:

$$
p=a^2+b^2
$$

and:

$$
b\not\equiv0\pmod p.
$$

Then:

$$
a^2
\equiv
-b^2
\pmod p.
$$

Multiply by:

$$
b^{-2}.
$$

We obtain:

$$
\left(
ab^{-1}
\right)^2
\equiv
-1
\pmod p.
$$

Therefore:

$$
\boxed{
-1
\text{ is a quadratic residue mod }p.
}
$$

Euler's criterion gives:

$$
\left(
\frac{-1}{p}
\right)
=
(-1)^{(p-1)/2}.
$$

Hence:

$$
\boxed{
\left(
\frac{-1}{p}
\right)=1
\iff
p\equiv1\pmod4.
}
$$

So several apparently different statements collapse into one structure:

$$
\boxed{
p\equiv1\pmod4
}
$$

$$
\Updownarrow
$$

$$
\boxed{
x^2\equiv-1\pmod p
\text{ is solvable}
}
$$

$$
\Updownarrow
$$

$$
\boxed{
p=a^2+b^2
}
$$

$$
\Updownarrow
$$

$$
\boxed{
p
\text{ splits in }\mathbb Z[i].
}
$$

This is a powerful example of the same arithmetic fact appearing simultaneously as:

- a congruence condition;
- a representation theorem;
- a factorization statement in an extension ring.

---

### Computationally recovering a factor

Suppose:

$$
p\equiv1\pmod4.
$$

If we find:

$$
x^2\equiv-1\pmod p,
$$

then inside:

$$
\mathbb Z[i],
$$

we have:

$$
p\mid x^2+1.
$$

But:

$$
x^2+1
=
(x+i)(x-i).
$$

A Gaussian gcd such as:

$$
\boxed{
\gcd_{\mathbb Z[i]}(
p,
x+i
)
}
$$

can recover a nontrivial Gaussian factor:

$$
a+bi
$$

of norm:

$$
p.
$$

Thus the Euclidean algorithm in $\mathbb Z[i]$ can be used computationally to transform a modular square root of $-1$ into a representation:

$$
\boxed{
p=a^2+b^2.
}
$$

This is a particularly elegant interaction between modular arithmetic and Gaussian gcd computation.

---

## Exact computational implementation

Gaussian arithmetic can be implemented using integer pairs:

$$
a+bi
\longleftrightarrow
(a,b).
$$

For educational code, this avoids relying on complex floating-point arithmetic.

---

### Basic Gaussian arithmetic

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class GaussianInteger:
    a: int
    b: int = 0

    def __add__(
        self,
        other: "GaussianInteger",
    ) -> "GaussianInteger":
        return GaussianInteger(
            self.a + other.a,
            self.b + other.b,
        )

    def __sub__(
        self,
        other: "GaussianInteger",
    ) -> "GaussianInteger":
        return GaussianInteger(
            self.a - other.a,
            self.b - other.b,
        )

    def __neg__(
        self,
    ) -> "GaussianInteger":
        return GaussianInteger(
            -self.a,
            -self.b,
        )

    def __mul__(
        self,
        other: "GaussianInteger",
    ) -> "GaussianInteger":
        return GaussianInteger(
            self.a * other.a
            - self.b * other.b,
            self.a * other.b
            + self.b * other.a,
        )

    def conjugate(
        self,
    ) -> "GaussianInteger":
        return GaussianInteger(
            self.a,
            -self.b,
        )

    def norm(self) -> int:
        return (
            self.a * self.a
            + self.b * self.b
        )

    def is_zero(self) -> bool:
        return (
            self.a == 0
            and self.b == 0
        )
```

The arithmetic is exact.

No floating-point complex values are required.

---

### Exact nearest-integer rounding

For Euclidean division we need to round rational coordinates to nearest integers.

Using floating point is unnecessary and can become unsafe for very large values.

We can instead round an exact rational:

$$
\frac{a}{b}
$$

using integer arithmetic.

```python
def nearest_integer(
    numerator: int,
    denominator: int,
) -> int:
    if denominator <= 0:
        raise ValueError(
            "denominator must be positive"
        )

    q, r = divmod(
        numerator,
        denominator,
    )

    if 2 * r > denominator:
        return q + 1

    return q
```

When the value is exactly halfway between two integers, either nearest integer is valid for the Euclidean proof.

---

### Exact Gaussian Euclidean division

Let:

$$
\alpha=a+bi
$$

and:

$$
\beta=c+di.
$$

Then:

$$
\frac{\alpha}{\beta}
=
\frac{
(a+bi)(c-di)
}{
c^2+d^2
}.
$$

The real numerator is:

$$
ac+bd,
$$

and the imaginary numerator is:

$$
bc-ad.
$$

Therefore:

```python
def gaussian_divmod(
    alpha: GaussianInteger,
    beta: GaussianInteger,
) -> tuple[
    GaussianInteger,
    GaussianInteger,
]:
    if beta.is_zero():
        raise ZeroDivisionError(
            "division by zero"
        )

    denominator = beta.norm()

    real_numerator = (
        alpha.a * beta.a
        + alpha.b * beta.b
    )

    imag_numerator = (
        alpha.b * beta.a
        - alpha.a * beta.b
    )

    q = GaussianInteger(
        nearest_integer(
            real_numerator,
            denominator,
        ),
        nearest_integer(
            imag_numerator,
            denominator,
        ),
    )

    r = alpha - q * beta

    if not (
        r.is_zero()
        or r.norm() < beta.norm()
    ):
        raise ArithmeticError(
            "Euclidean remainder invariant failed"
        )

    return q, r
```

The explicit assertion checks the central mathematical invariant:

$$
\boxed{
r=0
\quad\text{or}\quad
N(r)<N(\beta).
}
$$

---

### Testing the worked example

```python
alpha = GaussianInteger(7, 5)
beta = GaussianInteger(3, 2)

q, r = gaussian_divmod(
    alpha,
    beta,
)

print(q)
print(r)
print(r.norm())
print(beta.norm())
```

We expect:

```text
q = 2 + 0i
r = 1 + 1i
N(r) = 2
N(beta) = 13
```

and therefore:

$$
\boxed{
7+5i
=
2(3+2i)
+
(1+i).
}
$$

---

### Gaussian Euclidean algorithm

The gcd routine is now almost identical to the integer version:

```python
def gaussian_gcd(
    a: GaussianInteger,
    b: GaussianInteger,
) -> GaussianInteger:
    while not b.is_zero():
        _, r = gaussian_divmod(
            a,
            b,
        )

        a, b = b, r

    return a
```

The output is a gcd up to multiplication by one of:

$$
1,-1,i,-i.
$$

So different correct implementations may return different associates.

For example:

$$
2+i,
$$

$$
-2-i,
$$

$$
-1+2i,
$$

or:

$$
1-2i
$$

may represent the same gcd class.

---

### Testing multiplicativity of the norm

```python
z = GaussianInteger(2, 3)
w = GaussianInteger(4, -1)

assert (
    (z * w).norm()
    ==
    z.norm() * w.norm()
)
```

This directly validates:

$$
\boxed{
N(zw)=N(z)N(w).
}
$$

---

### Testing Euclidean division systematically

For small Gaussian integers, we can test the invariant exhaustively:

```python
for a in range(-5, 6):
    for b in range(-5, 6):
        alpha = GaussianInteger(
            a,
            b,
        )

        for c in range(-5, 6):
            for d in range(-5, 6):
                beta = GaussianInteger(
                    c,
                    d,
                )

                if beta.is_zero():
                    continue

                q, r = gaussian_divmod(
                    alpha,
                    beta,
                )

                assert (
                    alpha
                    ==
                    q * beta + r
                )

                assert (
                    r.is_zero()
                    or
                    r.norm() < beta.norm()
                )
```

This is a good example of how computation should support mathematical reasoning.

The test does not prove the Euclidean theorem.

The proof came from nearest-lattice-point geometry.

The exhaustive test verifies that the implementation respects that theorem over the tested range.

---

## Geometry and arithmetic meet

The Gaussian integers sit inside:

$$
\mathbb C
$$

as the square lattice:

$$
\boxed{
\mathbb Z^2.
}
$$

The point:

$$
(a,b)
$$

corresponds to:

$$
a+bi.
$$

The norm:

$$
N(a+bi)
=
a^2+b^2
$$

is squared Euclidean distance.

Euclidean division asks us to compute:

$$
\frac{\alpha}{\beta}
$$

and replace it by a nearby lattice point:

$$
q\in\mathbb Z[i].
$$

So the arithmetic algorithm:

$$
\boxed{
\alpha=q\beta+r
}
$$

is generated by a geometric operation:

$$
\boxed{
\text{nearest lattice point}.
}
$$

That is why the Gaussian integers provide such a useful conceptual bridge between:

$$
\text{number theory},
$$

$$
\text{algebra},
$$

and:

$$
\text{lattice geometry}.
$$

---

## The structural picture

The entire article can be compressed into one chain.

Begin with:

$$
\boxed{
\mathbb Z[i].
}
$$

Conjugation gives:

$$
z\mapsto\overline z.
$$

Together they produce the norm:

$$
\boxed{
N(z)=z\overline z.
}
$$

The norm is multiplicative:

$$
N(zw)=N(z)N(w).
$$

It also provides Euclidean descent:

$$
\boxed{
N(r)<N(\beta).
}
$$

Therefore:

$$
\boxed{
\mathbb Z[i]
\text{ is Euclidean}.
}
$$

Hence:

$$
\boxed{
\mathbb Z[i]
\text{ is a PID}.
}
$$

Hence:

$$
\boxed{
\mathbb Z[i]
\text{ is a UFD}.
}
$$

Unique factorization then allows us to understand rational primes inside the larger ring:

$$
\boxed{
p\equiv1\pmod4
\Rightarrow
\text{split},
}
$$

$$
\boxed{
p\equiv3\pmod4
\Rightarrow
\text{inert},
}
$$

$$
\boxed{
2
\Rightarrow
\text{ramified}.
}
$$

And for odd primes:

$$
\boxed{
p\equiv1\pmod4
}
$$

$$
\Updownarrow
$$

$$
\boxed{
p=a^2+b^2
}
$$

$$
\Updownarrow
$$

$$
\boxed{
x^2\equiv-1\pmod p
\text{ is solvable}.
}
$$

This is an early example of a principle that becomes central in algebraic number theory:

$$
\boxed{
\text{congruence information}
\longleftrightarrow
\text{factorization in extension rings}.
}
$$

---

## Practice and checkpoint

### Exercise 1 — Conjugation and norm

For:

$$
z=4-7i,
$$

compute:

$$
\overline z
$$

and:

$$
N(z).
$$

Verify:

$$
z\overline z=N(z).
$$

---

### Exercise 2 — Norm multiplicativity

Let:

$$
z=2+i,
\qquad
w=1+3i.
$$

Compute:

$$
N(z),
\qquad
N(w),
\qquad
N(zw),
$$

and verify:

$$
N(zw)=N(z)N(w).
$$

---

### Exercise 3 — Units

Solve:

$$
a^2+b^2=1
$$

over:

$$
a,b\in\mathbb Z.
$$

Use the solutions to derive:

$$
\mathbb Z[i]^\times.
$$

---

### Exercise 4 — Associates

List all associates of:

$$
3+2i.
$$

Verify that they all have norm:

$$
13.
$$

---

### Exercise 5 — Euclidean division

Divide:

$$
7+5i
$$

by:

$$
3+2i.
$$

Find Gaussian integers $q,r$ satisfying:

$$
7+5i
=
q(3+2i)+r
$$

and verify:

$$
N(r)<13.
$$

---

### Exercise 6 — Gaussian factorization

Show:

$$
5
=
(2+i)(2-i).
$$

Explain why:

$$
2+i
$$

is Gaussian prime.

---

### Exercise 7 — Inert prime

Explain why:

$$
7
$$

remains prime in:

$$
\mathbb Z[i].
$$

Use:

$$
7\equiv3\pmod4.
$$

---

### Exercise 8 — Ramification

Verify:

$$
2=-i(1+i)^2.
$$

Why does multiplication by:

$$
-i
$$

not change the essential prime factorization?

---

### Exercise 9 — Sum of two squares

Write each splitting prime as a sum of two squares:

$$
5,
\qquad
13,
\qquad
17,
\qquad
29.
$$

Use the representations to produce Gaussian factorizations.

---

### Exercise 10 — Square root of $-1$

For:

$$
p=13,
$$

find:

$$
x
$$

such that:

$$
x^2\equiv-1\pmod{13}.
$$

Relate your answer to:

$$
13=3^2+2^2.
$$

---

### Exercise 11 — Prime classification

Determine whether each Gaussian integer is prime:

$$
3,
\qquad
5,
\qquad
2+i,
\qquad
4+i,
\qquad
3+2i.
$$

Use the Gaussian-prime classification rather than trial division.

---

### Exercise 12 — Computational invariant

Implement Gaussian Euclidean division.

For many small random inputs verify both:

$$
\alpha=q\beta+r
$$

and:

$$
N(r)<N(\beta).
$$

Why is this a validation of the implementation rather than a proof of the theorem?

---

### Reader checkpoint

You should now be able to explain:

1. What:
   $$
   \mathbb Z[i]
   $$
   is.
2. How Gaussian conjugation works.
3. Why:
   $$
   N(a+bi)=a^2+b^2.
   $$
4. Why the norm is multiplicative.
5. Why divisibility in:
   $$
   \mathbb Z[i]
   $$
   implies divisibility of norms.
6. Why:
   
   $$
   \mathbb Z[i]^\times
   =
   \{\pm1,\pm i\}.
   $$
   
7. What associates are.
8. Why Gaussian gcds are unique only up to units.
9.  How Euclidean division is performed by rounding:
   $$
   \alpha/\beta
   $$
   to a nearby Gaussian integer.
10. Why:
    $$
    N(r)<N(\beta).
    $$
11. Why:
    $$
    \mathbb Z[i]
    $$
    is a Euclidean domain.
12. Why Euclidean structure implies unique factorization.
13. What a Gaussian prime is.
14. How to classify Gaussian primes.
15. Why primes:
    $$
    p\equiv1\pmod4
    $$
    split.
16. Why primes:
    $$
    p\equiv3\pmod4
    $$
    remain prime.
17. Why:
    $$
    2
    $$
    ramifies.
18. Why splitting primes are exactly the odd primes representable as:
    $$
    a^2+b^2.
    $$
19. Why splitting is equivalent to solvability of:
    $$
    x^2\equiv-1\pmod p.
    $$
20. How Gaussian gcd computation can recover a representation:
    $$
    p=a^2+b^2.
    $$
21. Why exact integer arithmetic is preferable to floating-point division in an implementation of Gaussian Euclidean division.
22. How nearest-lattice-point geometry produces an arithmetic algorithm.

The Gaussian integers show that enlarging the integers does not necessarily destroy computational arithmetic.

In this case it reveals new arithmetic structure that was invisible inside:

$$
\mathbb Z
$$

alone.

---

## References and further reading

**Kenneth Ireland and Michael Rosen**,  
*A Classical Introduction to Modern Number Theory.*

A standard reference for Gaussian integers, quadratic residues, sums of two squares, and the transition toward algebraic number theory.

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical treatment of sums of two squares, primes, and related arithmetic.

**David A. Cox**,  
*Primes of the Form $x^2+ny^2$.*

An excellent deeper study of the relationship between prime representation, quadratic forms, and splitting in algebraic extensions.

**Ivan Niven, Herbert S. Zuckerman, and Hugh L. Montgomery**,  
*An Introduction to the Theory of Numbers.*

A useful reference for Gaussian integers and classical divisibility theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Useful for the computational perspective on Euclidean algorithms, modular arithmetic, and algebraic structures.

---

## Next

This article showed that the congruence class:

$$
p\bmod4
$$

can determine whether a prime splits in:

$$
\mathbb Z[i].
$$

That already suggests a deeper question:

> How can congruence information about integers be encoded systematically?

The next article introduces functions that do exactly that.

A **Dirichlet character** assigns algebraic values to residue classes modulo $q$ while preserving multiplication.

From those characters we obtain exponential sums such as:

$$
\boxed{
\tau(\chi)
=
\sum_{a\bmod q}
\chi(a)
e^{2\pi ia/q},
}
$$

the **Gauss sums**.

This takes us from arithmetic in one extension ring to the interaction between:

$$
\boxed{
\text{multiplicative residue structure}
}
$$

and:

$$
\boxed{
\text{additive Fourier structure}.
}
$$
