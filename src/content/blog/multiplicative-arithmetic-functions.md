---
title: "Computational Number Theory I: Multiplicative Functions and Dirichlet Convolution"
description: "Divisor functions, Euler phi, Möbius mu, prime-power evaluation, Dirichlet convolution, Möbius inversion, and the computational algebra of arithmetic functions."
pubDate: "2025-05-25"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "multiplicative-functions"
  - "dirichlet-convolution"
  - "mobius-function"
  - "euler-phi"
  - "divisor-functions"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 1
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

Arithmetic functions attach numerical information to positive integers.

Examples include:

\[
\tau(n),
\]

the number of positive divisors of \(n\),

\[
\sigma(n),
\]

the sum of its positive divisors,

\[
\varphi(n),
\]

the number of invertible residue classes modulo \(n\), and

\[
\mu(n),
\]

the Möbius function.

At first these may look like unrelated formulas.

They are not.

A large part of their structure comes from two ideas:

\[
\boxed{
\text{prime-power decomposition}
}
\]

and

\[
\boxed{
\text{Dirichlet convolution}.
}
\]

For a multiplicative arithmetic function, knowing its values on:

\[
p^e
\]

is enough to determine its value on every positive integer.

Dirichlet convolution then provides an algebraic operation that explains identities such as:

\[
\tau
=
\mathbf 1 * \mathbf 1,
\]

\[
\sigma
=
\mathbf 1 * \operatorname{id},
\]

and:

\[
\varphi
=
\operatorname{id} * \mu.
\]

This is the computational viewpoint of the article:

\[
\boxed{
\text{factorization}
\rightarrow
\text{prime powers}
\rightarrow
\text{multiplicative evaluation}
\rightarrow
\text{convolution identities}.
}
\]

---

## Table of Contents

- [Arithmetic and multiplicative functions](#arithmetic-and-multiplicative-functions)
- [Prime-power reduction](#prime-power-reduction)
- [The classical arithmetic functions](#the-classical-arithmetic-functions)
- [Dirichlet convolution](#dirichlet-convolution)
- [Möbius inversion](#möbius-inversion)
- [Computational evaluation](#computational-evaluation)
- [Why this matters in computational number theory](#why-this-matters-in-computational-number-theory)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Arithmetic and multiplicative functions

An **arithmetic function** is a function:

\[
\boxed{
f:\mathbb N\rightarrow\mathbb C.
}
\]

The codomain can be generalized, but complex-valued arithmetic functions are the classical setting.

Examples include:

\[
n\mapsto n,
\]

\[
n\mapsto \varphi(n),
\]

\[
n\mapsto \mu(n),
\]

and:

\[
n\mapsto \tau(n).
\]

---

### Multiplicative functions

An arithmetic function \(f\) is **multiplicative** if:

\[
f(1)=1
\]

and:

\[
\boxed{
f(ab)=f(a)f(b)
}
\]

whenever:

\[
\gcd(a,b)=1.
\]

The coprimality condition is essential.

Multiplicativity does **not** generally mean:

\[
f(ab)=f(a)f(b)
\]

for arbitrary \(a,b\).

---

### Completely multiplicative functions

A function is **completely multiplicative** if:

\[
\boxed{
f(ab)=f(a)f(b)
}
\]

for all positive integers:

\[
a,b.
\]

Thus:

\[
\boxed{
\text{completely multiplicative}
\Longrightarrow
\text{multiplicative}.
}
\]

The converse is false.

---

### Example: the identity function

Define:

\[
\operatorname{id}(n)=n.
\]

Then:

\[
\operatorname{id}(ab)
=
ab
=
\operatorname{id}(a)\operatorname{id}(b)
\]

for all \(a,b\).

Therefore:

\[
\boxed{
\operatorname{id}
\text{ is completely multiplicative}.
}
\]

---

### Example: Euler's totient

Euler's totient is multiplicative:

\[
\gcd(a,b)=1
\Longrightarrow
\varphi(ab)=\varphi(a)\varphi(b).
\]

But it is not completely multiplicative.

For example:

\[
\varphi(2)=1,
\]

so:

\[
\varphi(2)\varphi(2)=1.
\]

But:

\[
\varphi(4)=2.
\]

Therefore:

\[
\boxed{
\varphi(4)
\neq
\varphi(2)^2.
}
\]

---

## Prime-power reduction

Every positive integer has a unique prime factorization:

\[
\boxed{
n
=
\prod_{i=1}^{r}
p_i^{e_i}.
}
\]

The prime powers:

\[
p_i^{e_i}
\]

are pairwise coprime.

Therefore, if \(f\) is multiplicative:

\[
\boxed{
f(n)
=
\prod_{i=1}^{r}
f(p_i^{e_i}).
}
\]

This is one of the most important computational consequences of multiplicativity.

Instead of developing a separate algorithm for arbitrary \(n\), we need only understand:

\[
\boxed{
f(p^e).
}
\]

The factorization of \(n\) then assembles the final answer.

---

### Example

Let:

\[
n=360.
\]

Its prime factorization is:

\[
360
=
2^3\cdot3^2\cdot5.
\]

For a multiplicative function \(f\):

\[
f(360)
=
f(2^3)
f(3^2)
f(5).
\]

Thus one global arithmetic problem has been reduced to three local prime-power evaluations.

This pattern will recur throughout computational number theory.

---

## The classical arithmetic functions

Several of the most important arithmetic functions admit especially simple prime-power formulas.

### Number of divisors

Let:

\[
\tau(n)
\]

denote the number of positive divisors of \(n\).

For:

\[
p^e,
\]

the divisors are:

\[
1,p,p^2,\ldots,p^e.
\]

So:

\[
\boxed{
\tau(p^e)=e+1.
}
\]

Therefore, if:

\[
n
=
\prod_{i=1}^{r}
p_i^{e_i},
\]

then:

\[
\boxed{
\tau(n)
=
\prod_{i=1}^{r}
(e_i+1).
}
\]

---

### Example

For:

\[
360
=
2^3\cdot3^2\cdot5,
\]

we obtain:

\[
\tau(360)
=
(3+1)(2+1)(1+1).
\]

Hence:

\[
\boxed{
\tau(360)=24.
}
\]

---

### Sum of divisors

Let:

\[
\sigma(n)
=
\sum_{d\mid n}d.
\]

For a prime power:

\[
p^e,
\]

we have:

\[
\sigma(p^e)
=
1+p+\cdots+p^e.
\]

Using the geometric-series formula:

\[
\boxed{
\sigma(p^e)
=
\frac{p^{e+1}-1}{p-1}.
}
\]

Therefore:

\[
\boxed{
\sigma(n)
=
\prod_{i=1}^{r}
\frac{
p_i^{e_i+1}-1
}{
p_i-1
}.
}
\]

---

### Euler's totient

Euler's totient:

\[
\varphi(n)
\]

counts:

\[
\boxed{
\left|
(\mathbb Z/n\mathbb Z)^\times
\right|.
}
\]

For a prime power:

\[
p^e,
\]

the nonunits are exactly the multiples of \(p\).

There are:

\[
p^{e-1}
\]

such residue classes.

Therefore:

\[
\varphi(p^e)
=
p^e-p^{e-1}.
\]

Equivalently:

\[
\boxed{
\varphi(p^e)
=
p^{e-1}(p-1).
}
\]

Using multiplicativity:

\[
\boxed{
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right).
}
\]

---

### Möbius function

The Möbius function:

\[
\mu:\mathbb N\rightarrow\{-1,0,1\}
\]

is defined by:

\[
\boxed{
\mu(n)
=
\begin{cases}
1,
&
n=1,
\\[4pt]
0,
&
p^2\mid n
\text{ for some prime }p,
\\[4pt]
(-1)^r,
&
n
\text{ is a product of }r
\text{ distinct primes}.
\end{cases}
}
\]

Equivalently, on prime powers:

\[
\mu(p)=-1,
\]

while:

\[
\boxed{
\mu(p^e)=0
\qquad
(e\ge2).
}
\]

The function \(\mu\) is multiplicative but not completely multiplicative.

---

### Example

For:

\[
30=2\cdot3\cdot5,
\]

we have three distinct prime factors, so:

\[
\boxed{
\mu(30)=(-1)^3=-1.
}
\]

But:

\[
12=2^2\cdot3
\]

contains a squared prime factor.

Therefore:

\[
\boxed{
\mu(12)=0.
}
\]

---

### A compact prime-power table

| Function | \(f(p^e)\) |
| --- | --- |
| \(\tau\) | \(e+1\) |
| \(\sigma\) | \(\displaystyle \frac{p^{e+1}-1}{p-1}\) |
| \(\varphi\) | \(p^{e-1}(p-1)\) |
| \(\mu\) | \(-1\) if \(e=1\), \(0\) if \(e\ge2\) |

Once the factorization of \(n\) is known, these formulas make evaluation almost immediate.

---

## Dirichlet convolution

Arithmetic functions can themselves be combined algebraically.

For arithmetic functions \(f\) and \(g\), define their **Dirichlet convolution** by:

\[
\boxed{
(f*g)(n)
=
\sum_{d\mid n}
f(d)
g\left(\frac nd\right).
}
\]

The sum runs over the positive divisors of \(n\).

---

### Example

For:

\[
n=6,
\]

the divisors are:

\[
1,2,3,6.
\]

Therefore:

\[
\begin{aligned}
(f*g)(6)
&=
f(1)g(6)
+
f(2)g(3)\\
&\quad+
f(3)g(2)
+
f(6)g(1).
\end{aligned}
\]

The divisor pairs:

\[
(d,n/d)
\]

are exactly what drives the convolution.

---

### Algebraic properties

Dirichlet convolution is associative:

\[
\boxed{
(f*g)*h
=
f*(g*h).
}
\]

It is also commutative:

\[
\boxed{
f*g
=
g*f.
}
\]

Together with pointwise addition, arithmetic functions form a commutative ring under these operations.

---

### The convolution identity

Define:

\[
\varepsilon(n)
=
\begin{cases}
1,&n=1,\\
0,&n>1.
\end{cases}
\]

Then:

\[
\boxed{
f*\varepsilon
=
f.
}
\]

So:

\[
\varepsilon
\]

is the multiplicative identity for Dirichlet convolution.

---

### The constant-one function

Define:

\[
\mathbf 1(n)=1
\]

for every:

\[
n\ge1.
\]

Then:

\[
(\mathbf 1*f)(n)
=
\sum_{d\mid n}
f(d).
\]

Thus convolution with \(\mathbf 1\) performs a **divisor sum**.

That simple observation explains many classical identities.

---

### Divisor function as convolution

Consider:

\[
(\mathbf 1*\mathbf 1)(n).
\]

We obtain:

\[
(\mathbf 1*\mathbf 1)(n)
=
\sum_{d\mid n}1.
\]

But the sum contains one term for each divisor.

Therefore:

\[
\boxed{
\tau
=
\mathbf 1*\mathbf 1.
}
\]

---

### Sum-of-divisors function

Let:

\[
\operatorname{id}(n)=n.
\]

Then:

\[
(\mathbf 1*\operatorname{id})(n)
=
\sum_{d\mid n}
\operatorname{id}\left(\frac nd\right).
\]

Equivalently, after exchanging divisor pairs:

\[
=
\sum_{d\mid n}d.
\]

Therefore:

\[
\boxed{
\sigma
=
\mathbf 1*\operatorname{id}.
}
\]

---

### Euler's totient identity

A classical identity is:

\[
\boxed{
\sum_{d\mid n}
\varphi(d)
=
n.
}
\]

In convolution notation:

\[
\boxed{
\varphi*\mathbf 1
=
\operatorname{id}.
}
\]

This identity says that the integers:

\[
1,\ldots,n
\]

can be classified according to the value of their GCD with \(n\), producing totient-sized classes.

---

### Multiplicativity is preserved by convolution

Suppose:

\[
f
\]

and:

\[
g
\]

are multiplicative.

Then:

\[
\boxed{
f*g
}
\]

is also multiplicative.

To see the mechanism, let:

\[
\gcd(m,n)=1.
\]

Every divisor of:

\[
mn
\]

has a unique form:

\[
d=ab
\]

with:

\[
a\mid m,
\qquad
b\mid n.
\]

Therefore:

\[
\begin{aligned}
(f*g)(mn)
&=
\sum_{a\mid m}
\sum_{b\mid n}
f(ab)
g\left(
\frac ma
\frac nb
\right).
\end{aligned}
\]

By multiplicativity:

\[
f(ab)
=
f(a)f(b)
\]

and:

\[
g\left(
\frac ma
\frac nb
\right)
=
g\left(\frac ma\right)
g\left(\frac nb\right).
\]

So the double sum factors:

\[
(f*g)(mn)
=
(f*g)(m)(f*g)(n).
\]

Hence convolution preserves multiplicativity.

This explains why many functions defined through divisor sums inherit multiplicative structure.

---

## Möbius inversion

One of the most important identities involving the Möbius function is:

\[
\boxed{
\sum_{d\mid n}
\mu(d)
=
\begin{cases}
1,&n=1,\\
0,&n>1.
\end{cases}
}
\]

In convolution notation:

\[
\boxed{
\mathbf 1*\mu
=
\varepsilon.
}
\]

Therefore \(\mu\) is the Dirichlet-convolution inverse of the constant-one function.

---

### Proof from prime factorization

Suppose:

\[
n>1
\]

has:

\[
r
\]

distinct prime divisors.

Only squarefree divisors contribute to:

\[
\sum_{d\mid n}\mu(d),
\]

because all other divisors have Möbius value zero.

Choosing a squarefree divisor means selecting a subset of those \(r\) primes.

Therefore:

\[
\sum_{d\mid n}\mu(d)
=
\sum_{k=0}^{r}
\binom rk(-1)^k.
\]

By the binomial theorem:

\[
=
(1-1)^r.
\]

Since:

\[
r\ge1,
\]

we obtain:

\[
\boxed{
\sum_{d\mid n}\mu(d)=0.
}
\]

For \(n=1\):

\[
\mu(1)=1.
\]

Hence:

\[
\boxed{
\mathbf 1*\mu=\varepsilon.
}
\]

---

### Möbius inversion theorem

Suppose two arithmetic functions \(F\) and \(G\) satisfy:

\[
\boxed{
G(n)
=
\sum_{d\mid n}
F(d).
}
\]

In convolution notation:

\[
G
=
\mathbf 1*F.
\]

Convolve both sides with \(\mu\):

\[
\mu*G
=
\mu*\mathbf 1*F.
\]

Since:

\[
\mu*\mathbf 1
=
\varepsilon,
\]

we obtain:

\[
\mu*G
=
F.
\]

Therefore:

\[
\boxed{
F(n)
=
\sum_{d\mid n}
\mu(d)
G\left(\frac nd\right).
}
\]

This is the **Möbius inversion formula**.

An equivalent form is:

\[
\boxed{
F(n)
=
\sum_{d\mid n}
\mu\left(\frac nd\right)G(d).
}
\]

---

### Recovering Euler's totient

Recall:

\[
\sum_{d\mid n}\varphi(d)=n.
\]

Thus:

\[
\mathbf 1*\varphi
=
\operatorname{id}.
\]

Apply Möbius inversion:

\[
\boxed{
\varphi
=
\mu*\operatorname{id}.
}
\]

Because convolution is commutative:

\[
\boxed{
\varphi
=
\operatorname{id}*\mu.
}
\]

Explicitly:

\[
\varphi(n)
=
\sum_{d\mid n}
\mu(d)
\frac nd.
\]

Factor out \(n\):

\[
\boxed{
\varphi(n)
=
n
\sum_{d\mid n}
\frac{\mu(d)}{d}.
}
\]

From the multiplicative structure of the right-hand side we recover:

\[
\boxed{
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right).
}
\]

So Möbius inversion does not merely produce another formula.

It explains structurally why the totient formula has its familiar prime-product form.

---

### Dirichlet inverses more generally

An arithmetic function:

\[
f:\mathbb N\rightarrow\mathbb C
\]

has a Dirichlet inverse whenever:

\[
\boxed{
f(1)\neq0.
}
\]

That is, there exists \(f^{-1}\) such that:

\[
f*f^{-1}
=
\varepsilon.
\]

The values of the inverse can be computed recursively.

At:

\[
n=1,
\]

we need:

\[
f(1)f^{-1}(1)=1,
\]

so:

\[
f^{-1}(1)
=
\frac1{f(1)}.
\]

For:

\[
n>1,
\]

the convolution identity gives:

\[
\sum_{d\mid n}
f(d)
f^{-1}(n/d)
=
0.
\]

This determines the new value from smaller divisor arguments.

The Möbius function is simply the most famous example:

\[
\boxed{
\mu
=
\mathbf 1^{-1}.
}
\]

---

## Computational evaluation

The mathematics suggests a natural implementation strategy.

For one integer \(n\):

1. factor \(n\);
2. store the prime powers;
3. evaluate every multiplicative function from that same factorization.

Do **not** independently enumerate every divisor for each arithmetic function unless the divisors themselves are needed.

---

### Factor representation

For example:

\[
360
=
2^3\cdot3^2\cdot5
\]

can be stored as:

```python
{
    2: 3,
    3: 2,
    5: 1,
}
```

Then all four classical functions can reuse this representation.

---

### Educational factorization routine

For small inputs, a simple trial-division implementation is enough:

```python
def factor_integer(n: int) -> dict[int, int]:
    if n < 1:
        raise ValueError("n must be positive")

    factors: dict[int, int] = {}

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    p = 3

    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p

        p += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors
```

This is appropriate for learning and small examples.

It is not a cryptographic-scale factorization algorithm.

---

### Computing \(\tau(n)\)

```python
def tau_from_factorization(
    factors: dict[int, int],
) -> int:
    result = 1

    for exponent in factors.values():
        result *= exponent + 1

    return result
```

This implements:

\[
\tau(n)
=
\prod_p
(e_p+1).
\]

---

### Computing \(\sigma(n)\)

```python
def sigma_from_factorization(
    factors: dict[int, int],
) -> int:
    result = 1

    for p, e in factors.items():
        result *= (
            p ** (e + 1) - 1
        ) // (p - 1)

    return result
```

This directly evaluates:

\[
\sigma(p^e)
=
\frac{p^{e+1}-1}{p-1}.
\]

---

### Computing \(\varphi(n)\)

A convenient exact formula is:

```python
def phi_from_factorization(
    factors: dict[int, int],
) -> int:
    result = 1

    for p, e in factors.items():
        result *= (
            p ** (e - 1)
            * (p - 1)
        )

    return result
```

Alternatively, starting from \(n\):

```python
def phi(n: int) -> int:
    factors = factor_integer(n)
    result = n

    for p in factors:
        result -= result // p

    return result
```

The second implementation realizes:

\[
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right)
\]

without floating-point arithmetic.

---

### Computing \(\mu(n)\)

```python
def mu_from_factorization(
    factors: dict[int, int],
) -> int:
    for exponent in factors.values():
        if exponent > 1:
            return 0

    return (
        -1
        if len(factors) % 2
        else 1
    )
```

For:

\[
n=1,
\]

the factor dictionary is empty, so this correctly returns:

\[
1.
\]

---

### One factorization, many functions

We can now compute everything from one factorization:

```python
def arithmetic_data(n: int) -> dict:
    factors = factor_integer(n)

    return {
        "n": n,
        "factorization": factors,
        "tau": tau_from_factorization(
            factors
        ),
        "sigma": sigma_from_factorization(
            factors
        ),
        "phi": phi_from_factorization(
            factors
        ),
        "mu": mu_from_factorization(
            factors
        ),
    }


print(arithmetic_data(360))
```

The expected values are:

```text
factorization = {2: 3, 3: 2, 5: 1}
tau           = 24
sigma         = 1170
phi           = 96
mu            = 0
```

This illustrates the main computational principle:

\[
\boxed{
\text{factor once}
\rightarrow
\text{reuse everywhere}.
}
\]

---

### Computing a Dirichlet convolution directly

For small \(n\), a direct implementation is:

```python
from math import isqrt
from typing import Callable


ArithmeticFunction = Callable[[int], int]


def divisors(n: int) -> list[int]:
    result = []

    for d in range(1, isqrt(n) + 1):
        if n % d != 0:
            continue

        result.append(d)

        other = n // d

        if other != d:
            result.append(other)

    return sorted(result)


def dirichlet_convolution(
    f: ArithmeticFunction,
    g: ArithmeticFunction,
    n: int,
) -> int:
    return sum(
        f(d) * g(n // d)
        for d in divisors(n)
    )
```

For example:

```python
def one(n: int) -> int:
    return 1


def identity(n: int) -> int:
    return n


print(
    dirichlet_convolution(
        one,
        one,
        360,
    )
)

print(
    dirichlet_convolution(
        one,
        identity,
        360,
    )
)
```

These evaluate:

\[
(\mathbf 1*\mathbf 1)(360)
=
\tau(360)
=
24
\]

and:

\[
(\mathbf 1*\operatorname{id})(360)
=
\sigma(360)
=
1170.
\]

---

### Single input versus many inputs

There are two different computational settings.

#### One or a few integers

If we want:

\[
\varphi(n),
\quad
\tau(n),
\quad
\sigma(n),
\quad
\mu(n)
\]

for a single \(n\), factorization is a natural representation.

#### All values up to \(N\)

If instead we want:

\[
\varphi(1),\ldots,\varphi(N)
\]

or:

\[
\mu(1),\ldots,\mu(N),
\]

factoring every integer independently is wasteful.

A sieve-style algorithm can compute many values simultaneously.

For example, Euler's totient can be sieved:

```python
def phi_sieve(N: int) -> list[int]:
    phi = list(range(N + 1))

    for p in range(2, N + 1):
        if phi[p] != p:
            continue

        for multiple in range(
            p,
            N + 1,
            p,
        ):
            phi[multiple] -= (
                phi[multiple] // p
            )

    return phi
```

This represents an important distinction in computational number theory:

\[
\boxed{
\text{single-instance algorithms}
\neq
\text{batch algorithms}.
}
\]

The best representation depends on the computational task.

---

### The real cost: obtaining the factorization

Suppose:

\[
n
=
\prod_i p_i^{e_i}
\]

is already known.

Then evaluating:

\[
\tau(n),
\quad
\sigma(n),
\quad
\varphi(n),
\quad
\mu(n)
\]

from the factorization is cheap.

But if the factorization is **not** known, obtaining it may dominate the entire computation.

For a large semiprime:

\[
N=pq,
\]

knowing \(p\) and \(q\) makes:

\[
\varphi(N)
=
(p-1)(q-1)
\]

immediate.

Recovering \(p\) and \(q\) from \(N\) is a completely different computational problem.

Therefore formulas such as:

\[
\varphi(n)
=
n
\prod_{p\mid n}
\left(
1-\frac1p
\right)
\]

should not be interpreted as automatically efficient algorithms when the prime divisors are unknown.

That distinction is fundamental in cryptography.

---

## Why this matters in computational number theory

Arithmetic functions provide a bridge between:

\[
\boxed{
\text{prime factorization}
}
\]

and:

\[
\boxed{
\text{global arithmetic information}.
}
\]

They compress structural information about an integer into computable invariants.

---

### Divisor counting

The divisor function:

\[
\tau(n)
\]

describes the combinatorial structure of the exponent vector:

\[
(e_1,\ldots,e_r).
\]

---

### Divisor sums

The function:

\[
\sigma(n)
\]

appears in the theory of:

- perfect numbers,
- abundant and deficient numbers,
- modular forms,
- analytic number theory.

---

### Euler's totient

The function:

\[
\varphi(n)
\]

measures:

\[
\left|
(\mathbb Z/n\mathbb Z)^\times
\right|.
\]

It therefore connects arithmetic functions directly to finite multiplicative groups.

This is why it appears naturally in:

- Euler's theorem,
- RSA-style exponent arithmetic,
- group-order calculations,
- modular periodicity.

---

### Möbius inversion

The Möbius function is particularly important because it acts as an inverse to divisor summation.

If:

\[
G(n)
=
\sum_{d\mid n}
F(d),
\]

then Möbius inversion reconstructs:

\[
F.
\]

Schematically:

\[
\boxed{
F
\overset{\mathbf 1 *}{\longrightarrow}
G
\overset{\mu *}{\longrightarrow}
F.
}
\]

This principle appears throughout:

- divisor sums,
- counting primitive objects,
- inclusion-exclusion arguments,
- multiplicative number theory,
- analytic number theory.

---

### From finite identities to Dirichlet series

There is also a deeper analytic connection.

To an arithmetic function \(f\), one may associate a Dirichlet series:

\[
D_f(s)
=
\sum_{n=1}^{\infty}
\frac{f(n)}{n^s}.
\]

Under suitable convergence conditions, Dirichlet convolution corresponds to ordinary multiplication:

\[
\boxed{
D_{f*g}(s)
=
D_f(s)D_g(s).
}
\]

For example:

\[
D_{\mathbf 1}(s)
=
\zeta(s),
\]

while:

\[
\mathbf 1*\mu
=
\varepsilon
\]

corresponds formally to:

\[
\boxed{
D_\mu(s)
=
\frac1{\zeta(s)}.
}
\]

This is one reason Dirichlet convolution is not merely convenient notation.

It is the algebraic operation naturally compatible with Dirichlet generating functions.

That connection becomes increasingly important in analytic and computational number theory.

---

## The structural picture

The central objects of this article can be summarized by a small convolution dictionary:

\[
\boxed{
\tau
=
\mathbf 1*\mathbf 1
}
\]

\[
\boxed{
\sigma
=
\mathbf 1*\operatorname{id}
}
\]

\[
\boxed{
\mathbf 1*\mu
=
\varepsilon
}
\]

\[
\boxed{
\varphi*\mathbf 1
=
\operatorname{id}
}
\]

and therefore:

\[
\boxed{
\varphi
=
\operatorname{id}*\mu.
}
\]

At the computational level:

\[
\boxed{
n
=
\prod p_i^{e_i}
}
\]

turns multiplicative evaluation into:

\[
\boxed{
f(n)
=
\prod_i
f(p_i^{e_i}).
}
\]

So two decompositions are operating simultaneously:

\[
\boxed{
\text{integer}
\rightarrow
\text{prime powers}
}
\]

and:

\[
\boxed{
\text{arithmetic function}
\rightarrow
\text{Dirichlet-convolution structure}.
}
\]

These two viewpoints are among the basic organizing principles of computational multiplicative number theory.

---

## Practice and checkpoint

### Exercise 1 — Multiplicativity

Determine whether each function is multiplicative or completely multiplicative:

\[
\operatorname{id}(n)=n,
\]

\[
\varphi(n),
\]

\[
\mu(n).
\]

Give a counterexample when complete multiplicativity fails.

---

### Exercise 2 — Divisor count

Factor:

\[
756
\]

and compute:

\[
\tau(756).
\]

Do not enumerate its divisors individually.

---

### Exercise 3 — Sum of divisors

Using the prime factorization of:

\[
360,
\]

verify:

\[
\sigma(360)=1170.
\]

---

### Exercise 4 — Totient

Compute:

\[
\varphi(360)
\]

from its prime-power factorization.

Then verify:

\[
\varphi(360)=96.
\]

---

### Exercise 5 — Möbius values

Compute:

\[
\mu(30),
\qquad
\mu(42),
\qquad
\mu(60),
\qquad
\mu(210).
\]

Explain each answer from the prime factorization.

---

### Exercise 6 — Convolution

Show directly that:

\[
(\mathbf 1*\mathbf 1)(12)=6.
\]

Compare this with:

\[
\tau(12).
\]

---

### Exercise 7 — Totient divisor sum

Verify:

\[
\sum_{d\mid12}\varphi(d)=12.
\]

Then rewrite the identity using Dirichlet convolution.

---

### Exercise 8 — Möbius identity

Verify:

\[
\sum_{d\mid30}\mu(d)=0.
\]

Explain the cancellation using subsets of the prime divisors:

\[
2,3,5.
\]

---

### Exercise 9 — Möbius inversion

Suppose:

\[
G(n)
=
\sum_{d\mid n}
F(d).
\]

Use Möbius inversion to write \(F(n)\) explicitly in terms of \(G\).

Then apply the formula to:

\[
G(n)=n
\]

to recover a formula for:

\[
\varphi(n).
\]

---

### Exercise 10 — Computational strategy

Suppose the prime factorization of a \(1000\)-digit integer is already known.

Explain why computing:

\[
\tau(n),
\quad
\sigma(n),
\quad
\varphi(n),
\quad
\mu(n)
\]

can still be straightforward.

Now explain why the same statement does not imply that these values are automatically easy to obtain from an arbitrary unfactored \(1000\)-digit integer.

---

### Reader checkpoint

You should now be able to explain:

1. What an arithmetic function is.
2. The difference between multiplicative and completely multiplicative functions.
3. Why multiplicative functions reduce to prime-power evaluation.
4. Why:
   
   \[
   \tau(p^e)=e+1.
   \]

5. Why:

   \[
   \sigma(p^e)
   =
   \frac{p^{e+1}-1}{p-1}.
   \] 

6. Why:
   
   \[
   \varphi(p^e)
   =
   p^{e-1}(p-1).
   \]

7. How the Möbius function depends on squarefreeness.
8. What Dirichlet convolution is.
9.  Why it is associative and commutative.
10. What the convolution identity \(\varepsilon\) is.
11. Why:

    \[
    \tau
    =
    \mathbf 1*\mathbf 1.
    \]

12. Why:
    
    \[
    \sigma
    =
    \mathbf 1*\operatorname{id}.
    \]

13. Why:
    
    \[
    \mathbf 1*\mu
    =
    \varepsilon.
    \]

14. Why:
    
    \[
    \varphi*\mathbf 1
    =
    \operatorname{id}.
    \]

15. How Möbius inversion follows from convolution.
16. Why convolution preserves multiplicativity.
17. Why:
    
    \[
    \varphi
    =
    \operatorname{id}*\mu.
    \]
    
18. Why one known factorization can support many arithmetic-function evaluations.
19. Why factoring may nevertheless dominate the overall computational cost.
20. Why batch computation may require sieve methods rather than repeated individual factorization.
21. How Dirichlet convolution becomes multiplication of Dirichlet series.

If these ideas are clear, arithmetic functions should no longer appear as a disconnected catalogue of formulas.

They form an algebraic and computational system built around:

\[
\boxed{
\text{prime factorization}
}
\]

and:

\[
\boxed{
\text{divisor structure}.
}
\]

---

## References and further reading

**Tom M. Apostol**,  
*Introduction to Analytic Number Theory.*

A standard introduction to arithmetic functions, Möbius inversion, Dirichlet convolution, and multiplicative number theory.

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical reference for divisor functions, Euler's totient, the Möbius function, and multiplicative arithmetic.

**Hugh L. Montgomery and Robert C. Vaughan**,  
*Multiplicative Number Theory I: Classical Theory.*

A deeper treatment of multiplicative functions and their role in analytic number theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Especially useful for connecting arithmetic structure with concrete algorithms and computational complexity.

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

A computational reference for prime-related algorithms, factorization, and large-integer arithmetic.

---

## Next

This first article focused mainly on arithmetic information attached to individual integers:

\[
\tau(n),
\qquad
\sigma(n),
\qquad
\varphi(n),
\qquad
\mu(n).
\]

The next natural question is global.

Instead of asking:

\[
\text{What arithmetic structure does one integer have?}
\]

we ask:

\[
\boxed{
\text{How are the primes distributed among all integers?}
}
\]

That leads from multiplicative arithmetic functions to:

\[
\pi(x),
\]

the Prime Number Theorem, explicit prime-counting estimates, and the computational study of prime gaps.
