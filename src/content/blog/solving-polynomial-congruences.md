---
title: "Solving Polynomial Congruences I"
description: "A detailed reference on linear and polynomial congruences, Diophantine equations, modular inverses, prime-power decomposition, Hensel lifting, and CRT reconstruction."
pubDate: "2025-04-27"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Cryptographic Engineering"
tags:
  - "polynomial-congruences"
  - "extended-euclidean-algorithm"
  - "hensel-lifting"
  - "modular-inverses"
difficulty: "Advanced"
series: "Elementary Number Theory Reference"
seriesOrder: 8
sourcePath: "experiments/ready-material/primes"
draft: false
---

Up to this point, modular arithmetic has mostly been used to compare integers, compute inverses, reconstruct residues, and reason about finite groups.

We now turn modular arithmetic into an equation-solving tool.

Our central problem is:

$$
\boxed{
f(x)\equiv0\pmod m,
}
$$

where

$$
f(x)\in\mathbb Z[x].
$$

Even the simplest case,

$$
ax\equiv b\pmod m,
$$

already brings together several ideas developed earlier:

$$
\gcd,
\qquad
\text{Bézout identities},
\qquad
\text{modular inverses},
\qquad
\text{Diophantine equations}.
$$

For higher-degree polynomials, the structure becomes richer.

We will see that a composite modulus can often be decomposed into prime powers:

$$
m
=
\prod_i p_i^{\alpha_i},
$$

that polynomial roots can be studied separately modulo each prime power, and that the Chinese Remainder Theorem can then reconstruct the global solutions.

The key new tool is **Hensel lifting**:

$$
\boxed{
\text{root modulo }p
\longrightarrow
\text{root modulo }p^2
\longrightarrow
\text{root modulo }p^3
\longrightarrow\cdots
}
$$

This gives us one of the first clear examples of local modular information being refined systematically to higher precision.

---

## Table of Contents

- [Polynomial congruences](#polynomial-congruences)
- [Linear congruences](#linear-congruences)
- [Why the GCD condition appears](#why-the-gcd-condition-appears)
- [Solving $ax\equiv b\pmod m$](#solving-axbmodmaxequiv-bpmod-maxbmodm)
- [The unit case](#the-unit-case)
- [Connection with Diophantine equations](#connection-with-diophantine-equations)
- [All solutions of a linear Diophantine equation](#all-solutions-of-a-linear-diophantine-equation)
- [Extended Euclid and modular inverses](#extended-euclid-and-modular-inverses)
- [A reusable linear-congruence solver](#a-reusable-linear-congruence-solver)
- [Higher-degree polynomial congruences](#higher-degree-polynomial-congruences)
- [Decomposition into prime powers](#decomposition-into-prime-powers)
- [Lifting roots modulo prime powers](#lifting-roots-modulo-prime-powers)
- [Hensel's lemma](#hensels-lemma)
- [The lifting tree](#the-lifting-tree)
- [Example I: lifting a cubic modulo $27$](#example-i-lifting-a-cubic-modulo-272727)
- [Example II: Hensel lifting plus CRT](#example-ii-hensel-lifting-plus-crt)
- [Counting the global roots](#counting-the-global-roots)
- [CRT reconstruction](#crt-reconstruction)
- [Python implementation](#python-implementation)
- [Polynomial derivative](#polynomial-derivative)
- [One Hensel lifting step](#one-hensel-lifting-step)
- [Lifting all roots](#lifting-all-roots)
- [Second example computationally](#second-example-computationally)
- [Combining all roots with CRT](#combining-all-roots-with-crt)
- [Simple roots versus singular roots](#simple-roots-versus-singular-roots)
- [A small singular example](#a-small-singular-example)
- [Why CRT and Hensel fit together](#why-crt-and-hensel-fit-together)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [An important conceptual distinction](#an-important-conceptual-distinction)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Where this leads](#where-this-leads)

---

## Polynomial congruences

Let

$$
f(x)
=
a_dx^d+a_{d-1}x^{d-1}
+\cdots+a_1x+a_0
$$

be a polynomial with integer coefficients.

We want to solve:

$$
\boxed{
f(x)\equiv0\pmod m.
}
$$

Because congruence is compatible with addition and multiplication,

$$
a\equiv b\pmod m
$$

implies:

$$
f(a)\equiv f(b)\pmod m.
$$

Therefore the value of $f(x)\bmod m$ depends only on the residue class of $x$.

So solving:

$$
f(x)\equiv0\pmod m
$$

means finding the elements:

$$
[x]_m\in\mathbb Z_m
$$

for which $f$ evaluates to zero.

Since $\mathbb Z_m$ contains only $m$ residue classes, there are finitely many possible roots modulo $m$.

A direct brute-force solution is always theoretically possible:

```python
def roots_mod_bruteforce(f, modulus):
    return [
        x
        for x in range(modulus)
        if f(x) % modulus == 0
    ]
```

But for large moduli, brute force is usually the wrong approach.

We want to exploit arithmetic structure.

---

## Linear congruences

The simplest polynomial congruence is:

$$
\boxed{
ax\equiv b\pmod m.
}
$$

This means:

$$
m\mid(ax-b).
$$

Equivalently, there exists:

$$
y\in\mathbb Z
$$

such that:

$$
ax-my=b.
$$

So solving a linear congruence is equivalent to solving a linear Diophantine equation.

The fundamental solvability criterion is:

$$
\boxed{
ax\equiv b\pmod m
\text{ has a solution}
\iff
\gcd(a,m)\mid b.
}
$$

If:

$$
g=\gcd(a,m)
$$

and:

$$
g\mid b,
$$

then there are exactly:

$$
\boxed{
g
}
$$

incongruent solutions modulo $m$.

---

## Why the GCD condition appears

Suppose:

$$
ax\equiv b\pmod m.
$$

Then:

$$
ax-my=b
$$

for some $y$.

Any common divisor of $a$ and $m$ divides both terms:

$$
ax
$$

and:

$$
my.
$$

Therefore it must divide their difference:

$$
b.
$$

So:

$$
\gcd(a,m)\mid b
$$

is necessary.

Conversely, suppose:

$$
g=\gcd(a,m)
$$

and:

$$
g\mid b.
$$

Bézout's identity gives integers $u,v$ satisfying:

$$
au+mv=g.
$$

Write:

$$
b=gc.
$$

Multiplying the Bézout identity by $c$:

$$
a(uc)+m(vc)=b.
$$

Hence:

$$
a(uc)\equiv b\pmod m.
$$

So:

$$
x=uc
$$

provides a solution.

Thus the condition is also sufficient.

---

## Solving $ax\equiv b\pmod m$

Consider:

$$
34x\equiv60\pmod{98}.
$$

Compute:

$$
\gcd(34,98)=2.
$$

Since:

$$
2\mid60,
$$

solutions exist.

Divide the entire congruence by $2$, including the modulus:

$$
17x\equiv30\pmod{49}.
$$

Now:

$$
\gcd(17,49)=1,
$$

so $17$ has an inverse modulo $49$.

In fact:

$$
17^{-1}
\equiv26
\pmod{49},
$$

because:

$$
17\cdot26
=
442
\equiv1
\pmod{49}.
$$

Therefore:

$$
x
\equiv
30\cdot26
\pmod{49}.
$$

Since:

$$
780\bmod49=45,
$$

we obtain:

$$
x\equiv45\pmod{49}.
$$

But remember: the original modulus was $98$, and:

$$
g=\gcd(34,98)=2.
$$

Therefore there must be exactly two incongruent solutions modulo $98$.

They are:

$$
45
$$

and:

$$
45+49=94.
$$

Hence:

$$
\boxed{
x\equiv45,\;94\pmod{98}.
}
$$

Check:

$$
34\cdot45
\equiv60\pmod{98},
$$

and:

$$
34\cdot94
\equiv60\pmod{98}.
$$

---

## The unit case

If:

$$
\gcd(a,m)=1,
$$

then $a$ belongs to:

$$
\mathbb Z_m^\times.
$$

So $a$ has a unique multiplicative inverse:

$$
a^{-1}\pmod m.
$$

The equation:

$$
ax\equiv b\pmod m
$$

then has the unique solution:

$$
\boxed{
x
\equiv
a^{-1}b
\pmod m.
}
$$

This is modular division.

We are not literally dividing by $a$.

We are multiplying by its inverse.

---

## Connection with Diophantine equations

A **linear Diophantine equation** has the form:

$$
ax+by=c
$$

with:

$$
a,b,c\in\mathbb Z,
$$

and seeks integer solutions:

$$
(x,y)\in\mathbb Z^2.
$$

The equation has integer solutions exactly when:

$$
\boxed{
\gcd(a,b)\mid c.
}
$$

This is the same criterion we just encountered for linear congruences.

That is not a coincidence.

The congruence:

$$
ax\equiv c\pmod b
$$

is equivalent to:

$$
ax-by=c.
$$

So linear congruence solving and linear Diophantine solving are two views of the same arithmetic problem.

---

## All solutions of a linear Diophantine equation

Suppose:

$$
ax+by=c
$$

has one solution:

$$
(x_0,y_0).
$$

Let:

$$
g=\gcd(a,b).
$$

Then every integer solution is:

$$
\boxed{
x
=
x_0+\frac bg t,
}
$$

$$
\boxed{
y
=
y_0-\frac ag t,
}
$$

where:

$$
t\in\mathbb Z.
$$

For example, consider:

$$
1337x+137y=1.
$$

From the Extended Euclidean Algorithm:

$$
1
=
1337(-54)
+
137(527).
$$

So one solution is:

$$
x_0=-54,
\qquad
y_0=527.
$$

Because:

$$
\gcd(1337,137)=1,
$$

the full family is:

$$
\boxed{
x=-54+137t,
}
$$

$$
\boxed{
y=527-1337t,
}
$$

for:

$$
t\in\mathbb Z.
$$

---

## Extended Euclid and modular inverses

We already developed the Extended Euclidean Algorithm earlier in the series.

Its importance here can be summarized by:

$$
\boxed{
\operatorname{xgcd}(a,b)
\longrightarrow
(g,x,y)
}
$$

such that:

$$
g=ax+by
=
\gcd(a,b).
$$

If:

$$
g=1,
$$

then:

$$
ax+by=1.
$$

Reducing modulo $b$:

$$
ax\equiv1\pmod b.
$$

Therefore:

$$
\boxed{
a^{-1}\equiv x\pmod b.
}
$$

### Example: inverse of $130$ modulo $61$

The Euclidean algorithm gives:

$$
\begin{aligned}
130 &=2\cdot61+8,\\
61 &=7\cdot8+5,\\
8 &=1\cdot5+3,\\
5 &=1\cdot3+2,\\
3 &=1\cdot2+1.
\end{aligned}
$$

Back-substitution yields:

$$
1
=
23\cdot130
-
49\cdot61.
$$

Reducing modulo $61$:

$$
23\cdot130
\equiv1\pmod{61}.
$$

Hence:

$$
\boxed{
130^{-1}
\equiv23
\pmod{61}.
}
$$

---

## A reusable linear-congruence solver

We can implement the theorem directly.

```python
from math import gcd


def solve_linear_congruence(a, b, m):
    """
    Solve a*x ≡ b (mod m).

    Returns all incongruent solutions
    modulo m.
    """
    if m <= 0:
        raise ValueError(
            "modulus must be positive"
        )

    g = gcd(a, m)

    if b % g != 0:
        return []

    a_reduced = a // g
    b_reduced = b // g
    m_reduced = m // g

    inverse = pow(
        a_reduced,
        -1,
        m_reduced,
    )

    x0 = (
        inverse * b_reduced
    ) % m_reduced

    return [
        (x0 + k * m_reduced) % m
        for k in range(g)
    ]
```

For our example:

```python
solutions = solve_linear_congruence(
    34,
    60,
    98,
)

print(solutions)
```

we obtain:

```text
[45, 94]
```

We can verify:

```python
for x in solutions:
    assert (34 * x - 60) % 98 == 0
```

The implementation mirrors the theorem exactly.

---

## Higher-degree polynomial congruences

We now return to:

$$
f(x)\equiv0\pmod m.
$$

For degree greater than one, there is no single universal inverse operation analogous to:

$$
x\equiv a^{-1}b.
$$

The structure depends strongly on:

- the polynomial,
- the modulus,
- its prime factorization,
- whether roots are simple or repeated modulo the relevant primes.

The first major simplification comes from factoring the modulus.

Suppose:

$$
m
=
p_1^{\alpha_1}
p_2^{\alpha_2}
\cdots
p_r^{\alpha_r},
$$

where the $p_i$ are distinct primes.

The prime powers:

$$
p_i^{\alpha_i}
$$

are pairwise coprime.

Therefore CRT applies.

---

## Decomposition into prime powers

Solving:

$$
f(x)\equiv0\pmod m
$$

is equivalent to simultaneously solving:

$$
f(x)\equiv0
\pmod{p_1^{\alpha_1}},
$$

$$
f(x)\equiv0
\pmod{p_2^{\alpha_2}},
$$

$$
\vdots
$$

$$
f(x)\equiv0
\pmod{p_r^{\alpha_r}}.
$$

Once one root has been selected modulo each prime power:

$$
x
\equiv
c_i
\pmod{p_i^{\alpha_i}},
$$

CRT reconstructs exactly one residue class modulo:

$$
m.
$$

If the number of roots modulo each prime power is:

$$
N_1,N_2,\ldots,N_r,
$$

then the total number of roots modulo $m$ is:

$$
\boxed{
N_1N_2\cdots N_r.
}
$$

Why?

Each independent choice of one local root from every prime-power component determines exactly one global CRT solution.

So we obtain the general strategy:

```text
factor the modulus
        ↓
solve modulo each prime power
        ↓
choose combinations of local roots
        ↓
CRT
        ↓
all global roots
```

The difficult step has therefore been reduced to:

$$
\boxed{
\text{solve modulo }p^\alpha.
}
$$

This is where Hensel lifting enters.

---

## Lifting roots modulo prime powers

Suppose:

$$
f(a)\equiv0\pmod{p^k}.
$$

So $a$ is already a root modulo $p^k$.

We want to find roots modulo:

$$
p^{k+1}
$$

that reduce to $a$ modulo $p^k$.

Every such candidate has the form:

$$
\boxed{
x
=
a+t p^k,
}
$$

where:

$$
t\in\{0,1,\ldots,p-1\}.
$$

Expand $f$ around $a$:

$$
f(a+t p^k).
$$

For a polynomial with integer coefficients:

$$
f(a+t p^k)
\equiv
f(a)
+
t p^k f'(a)
\pmod{p^{k+1}}.
$$

Why do higher-order terms disappear?

They contain at least:

$$
p^{2k}.
$$

Since:

$$
k\ge1,
$$

we have:

$$
2k\ge k+1.
$$

Therefore those terms vanish modulo:

$$
p^{k+1}.
$$

Now write:

$$
f(a)=p^k c.
$$

Then:

$$
f(a+t p^k)
\equiv
p^k
\left(
c+t f'(a)
\right)
\pmod{p^{k+1}}.
$$

For this expression to vanish modulo $p^{k+1}$, we need:

$$
\boxed{
c+t f'(a)
\equiv0\pmod p.
}
$$

Equivalently:

$$
\boxed{
f'(a)t
\equiv
-\frac{f(a)}{p^k}
\pmod p.
}
$$

So one nonlinear lifting problem has become a **linear congruence modulo $p$**.

That is the central mechanism.

---

## Hensel's lemma

The previous calculation gives the standard one-step Hensel picture.

Let:

$$
f(x)\in\mathbb Z[x]
$$

and suppose:

$$
f(a)\equiv0\pmod{p^k}.
$$

We seek:

$$
\widetilde a
\equiv a
\pmod{p^k}
$$

satisfying:

$$
f(\widetilde a)
\equiv0
\pmod{p^{k+1}}.
$$

Write:

$$
\widetilde a
=
a+t p^k.
$$

Then $t$ must solve:

$$
f'(a)t
\equiv
-\frac{f(a)}{p^k}
\pmod p.
$$

This creates three cases.

### Case 1 — Simple root

If:

$$
f'(a)\not\equiv0\pmod p,
$$

then $f'(a)$ is invertible modulo $p$.

Therefore there is exactly one:

$$
t\pmod p.
$$

Hence $a$ has a **unique lift** modulo $p^{k+1}$.

This is the most familiar form of Hensel's lemma.

A simple root modulo $p$ lifts uniquely to roots modulo:

$$
p^2,p^3,p^4,\ldots
$$

### Case 2 — Singular root that branches

If:

$$
f'(a)\equiv0\pmod p
$$

and:

$$
\frac{f(a)}{p^k}
\equiv0\pmod p,
$$

then the lifting equation becomes:

$$
0\cdot t\equiv0\pmod p.
$$

Every:

$$
t\in\mathbb Z_p
$$

works.

So the root has:

$$
\boxed{
p
}
$$

different lifts modulo $p^{k+1}$.

### Case 3 — Singular root that dies

If:

$$
f'(a)\equiv0\pmod p
$$

but:

$$
\frac{f(a)}{p^k}
\not\equiv0\pmod p,
$$

then we would need:

$$
0\cdot t
\equiv
c
\pmod p
$$

for some:

$$
c\neq0.
$$

That is impossible.

So:

$$
\boxed{
\text{no lift exists}.
}
$$

---

## The lifting tree

This gives a useful mental model.

A root modulo $p^k$ may:

```text
have exactly one child
```

if the derivative is nonzero modulo $p$,

```text
have p children
```

in the singular branching case,

or:

```text
have no children
```

if the singular root cannot be lifted.

So roots modulo successive prime powers form a branching tree:

$$
\text{roots mod }p
\rightarrow
\text{roots mod }p^2
\rightarrow
\text{roots mod }p^3
\rightarrow\cdots
$$

For **simple roots**, the tree has exactly one path.

For singular roots, it can branch or terminate.

This distinction is one of the most important ideas in Hensel lifting.

---

## Example I: lifting a cubic modulo $27$

Solve:

$$
f(x)
=
x^3-4x^2+5x-6
\equiv0
\pmod{27}.
$$

Since:

$$
27=3^3,
$$

we begin modulo $3$.

### Root modulo $3$

Reduce:

$$
f(x)
\equiv
x^3+2x^2+2x
\pmod3.
$$

Check:

$$
x=0,1,2.
$$

We obtain:

$$
f(0)\equiv0\pmod3,
$$

while:

$$
f(1)\not\equiv0\pmod3
$$

and:

$$
f(2)\not\equiv0\pmod3.
$$

Therefore the only root is:

$$
a_1=0.
$$

The derivative is:

$$
f'(x)
=
3x^2-8x+5.
$$

At $a_1=0$:

$$
f'(0)=5\equiv2\pmod3.
$$

This is nonzero.

Therefore the root is simple and must lift uniquely.

---

### Lift from modulo $3$ to modulo $9$

Write:

$$
x
=
0+3t.
$$

Since:

$$
f(0)=-6,
$$

we have:

$$
\frac{f(0)}3=-2.
$$

The lifting equation is:

$$
f'(0)t
\equiv
-\frac{f(0)}3
\pmod3.
$$

Thus:

$$
5t
\equiv
2
\pmod3.
$$

Reducing:

$$
2t\equiv2\pmod3.
$$

Therefore:

$$
t\equiv1\pmod3.
$$

Hence:

$$
x
=
0+3(1)
=
3
\pmod9.
$$

So:

$$
\boxed{
x\equiv3\pmod9.
}
$$

---

### Lift from modulo $9$ to modulo $27$

Now:

$$
a_2=3.
$$

Compute:

$$
f(3)=0.
$$

So:

$$
\frac{f(3)}9=0.
$$

Also:

$$
f'(3)
=
27-24+5
=
8.
$$

The lifting equation becomes:

$$
8t
\equiv0
\pmod3.
$$

Since:

$$
8\equiv2\pmod3,
$$

the inverse exists, giving:

$$
t\equiv0\pmod3.
$$

Therefore:

$$
x
=
3+9(0)
=
3
\pmod{27}.
$$

Hence the unique final solution is:

$$
\boxed{
x\equiv3\pmod{27}.
}
$$

Direct verification:

$$
3^3
-
4(3^2)
+
5(3)
-
6
=
0.
$$

---

## Example II: Hensel lifting plus CRT

Now solve:

$$
\boxed{
x^2+3x+17
\equiv0
\pmod{315}.
}
$$

Factor the modulus:

$$
315
=
3^2\cdot5\cdot7.
$$

Therefore we solve independently modulo:

$$
9,
\qquad
5,
\qquad
7.
$$

Then CRT combines the local roots.

Let:

$$
f(x)
=
x^2+3x+17.
$$

---

### Roots modulo $9$

First solve modulo $3$:

$$
x^2+3x+17
\equiv
x^2+2
\equiv0
\pmod3.
$$

So:

$$
x^2\equiv1\pmod3.
$$

The roots are:

$$
x\equiv1,2\pmod3.
$$

Now lift each one to modulo $9$.

The derivative is:

$$
f'(x)=2x+3.
$$

At $x=1$:

$$
f'(1)=5\equiv2\pmod3,
$$

so the root is simple and lifts uniquely.

The resulting root modulo $9$ is:

$$
x\equiv4\pmod9.
$$

At $x=2$:

$$
f'(2)=7\equiv1\pmod3,
$$

so this root also lifts uniquely.

The resulting root is:

$$
x\equiv2\pmod9.
$$

Thus:

$$
\boxed{
x\equiv2,4\pmod9.
}
$$

---

### Roots modulo $5$

Reduce:

$$
x^2+3x+17
\equiv
x^2+3x+2
\pmod5.
$$

Factor:

$$
x^2+3x+2
=
(x+1)(x+2).
$$

Therefore:

$$
x\equiv-1,-2\pmod5.
$$

So:

$$
\boxed{
x\equiv4,3\pmod5.
}
$$

---

### Roots modulo $7$

Reduce:

$$
x^2+3x+17
\equiv
x^2+3x+3
\pmod7.
$$

Direct evaluation gives:

$$
f(1)\equiv0\pmod7
$$

and:

$$
f(3)\equiv0\pmod7.
$$

Therefore:

$$
\boxed{
x\equiv1,3\pmod7.
}
$$

---

## Counting the global roots

We have:

$$
2
$$

roots modulo $9$,

$$
2
$$

roots modulo $5$,

and:

$$
2
$$

roots modulo $7$.

Since:

$$
9,5,7
$$

are pairwise coprime, every combination determines one distinct root modulo $315$.

Therefore the total number of solutions is:

$$
\boxed{
2\cdot2\cdot2=8.
}
$$

This allows us to predict the answer count **before performing any CRT reconstruction**.

---

## CRT reconstruction

The eight combinations are:

| Mod $9$ | Mod $5$ | Mod $7$ | Root mod $315$ |
| ---: | ---: | ---: | ---: |
| $2$ | $3$ | $1$ | $218$ |
| $2$ | $3$ | $3$ | $38$ |
| $2$ | $4$ | $1$ | $29$ |
| $2$ | $4$ | $3$ | $164$ |
| $4$ | $3$ | $1$ | $148$ |
| $4$ | $3$ | $3$ | $283$ |
| $4$ | $4$ | $1$ | $274$ |
| $4$ | $4$ | $3$ | $94$ |

So the complete solution set modulo $315$ is:

$$
\boxed{
\{
29,
38,
94,
148,
164,
218,
274,
283
\}.
}
$$

Every value satisfies:

$$
x^2+3x+17
\equiv0
\pmod{315}.
$$

This example captures the complete strategy:

$$
\boxed{
\text{factor}
\rightarrow
\text{solve locally}
\rightarrow
\text{lift}
\rightarrow
\text{combine with CRT}.
}
$$

---

## Python implementation

We can make this process executable without hiding the mathematics.

### Polynomial evaluation

Using Horner's method:

```python
def poly_eval(coeffs, x):
    """
    coeffs are ordered from
    highest degree to constant term.
    """
    value = 0

    for coefficient in coeffs:
        value = value * x + coefficient

    return value
```

For:

$$
f(x)
=
x^3-4x^2+5x-6,
$$

use:

```python
f = [1, -4, 5, -6]

assert poly_eval(f, 3) == 0
```

---

## Polynomial derivative

```python
def poly_derivative(coeffs):
    degree = len(coeffs) - 1

    return [
        coeffs[i] * (degree - i)
        for i in range(degree)
    ]
```

Example:

```python
f = [1, -4, 5, -6]

df = poly_derivative(f)

print(df)
```

gives:

```text
[3, -8, 5]
```

corresponding to:

$$
f'(x)
=
3x^2-8x+5.
$$

---

## One Hensel lifting step

An especially transparent implementation simply tests the $p$ possible lifts.

If $a$ is a root modulo:

$$
p^k,
$$

then every possible lift has the form:

$$
a+t p^k
$$

for:

$$
t=0,\ldots,p-1.
$$

```python
def hensel_lift_step(
    coeffs,
    root,
    p,
    k,
):
    modulus = p**k
    next_modulus = p ** (k + 1)

    if poly_eval(coeffs, root) % modulus != 0:
        raise ValueError(
            "root is not valid modulo p^k"
        )

    lifts = []

    for t in range(p):
        candidate = root + t * modulus
        candidate %= next_modulus

        if (
            poly_eval(coeffs, candidate)
            % next_modulus
            == 0
        ):
            lifts.append(candidate)

    return sorted(set(lifts))
```

This implementation handles all three cases automatically:

```text
0 lifts
1 lift
p lifts
```

and therefore also handles singular roots.

---

## Lifting all roots

We can now solve modulo $p^\alpha$:

```python
def roots_mod_prime_power(
    coeffs,
    p,
    alpha,
):
    if alpha < 1:
        raise ValueError(
            "alpha must be positive"
        )

    roots = [
        x
        for x in range(p)
        if poly_eval(coeffs, x) % p == 0
    ]

    for k in range(1, alpha):
        new_roots = []

        for root in roots:
            new_roots.extend(
                hensel_lift_step(
                    coeffs,
                    root,
                    p,
                    k,
                )
            )

        roots = sorted(set(new_roots))

    modulus = p**alpha

    return roots, modulus
```

For the cubic example:

```python
f = [1, -4, 5, -6]

roots, modulus = roots_mod_prime_power(
    f,
    p=3,
    alpha=3,
)

print(roots)
print(modulus)
```

we obtain:

```text
[3]
27
```

So:

$$
x\equiv3\pmod{27}.
$$

---

## Second example computationally

For:

$$
f(x)
=
x^2+3x+17,
$$

use:

```python
f = [1, 3, 17]
```

Modulo $9$:

```python
roots_9, _ = roots_mod_prime_power(
    f,
    p=3,
    alpha=2,
)

print(roots_9)
```

returns:

```text
[2, 4]
```

Modulo $5$:

```python
roots_5 = [
    x
    for x in range(5)
    if poly_eval(f, x) % 5 == 0
]

print(roots_5)
```

returns:

```text
[3, 4]
```

Modulo $7$:

```python
roots_7 = [
    x
    for x in range(7)
    if poly_eval(f, x) % 7 == 0
]

print(roots_7)
```

returns:

```text
[1, 3]
```

Thus we already know:

```python
len(roots_9) * len(roots_5) * len(roots_7)
```

is:

```text
8
```

before doing CRT.

---

## Combining all roots with CRT

Using a standard pairwise-coprime CRT routine:

```python
from itertools import product


def crt(residues, moduli):
    M = 1

    for modulus in moduli:
        M *= modulus

    x = 0

    for residue, modulus in zip(
        residues,
        moduli,
    ):
        M_i = M // modulus
        inverse = pow(
            M_i,
            -1,
            modulus,
        )

        x += residue * M_i * inverse

    return x % M
```

we can reconstruct every combination:

```python
all_roots = []

for local_roots in product(
    roots_9,
    roots_5,
    roots_7,
):
    root = crt(
        local_roots,
        [9, 5, 7],
    )

    all_roots.append(root)

all_roots = sorted(set(all_roots))

print(all_roots)
```

Output:

```text
[29, 38, 94, 148, 164, 218, 274, 283]
```

Now verify the defining invariant:

```python
for root in all_roots:
    assert (
        poly_eval(f, root) % 315
        == 0
    )
```

This is exactly how the mathematical decomposition should be reflected in code.

---

## Simple roots versus singular roots

This distinction deserves emphasis.

Suppose:

$$
f(a)\equiv0\pmod p.
$$

If:

$$
f'(a)\not\equiv0\pmod p,
$$

then $a$ is called a **simple root modulo $p$**.

Such a root lifts uniquely through every power:

$$
p,
p^2,
p^3,\ldots
$$

This is the clean Hensel case.

If instead:

$$
f'(a)\equiv0\pmod p,
$$

the root is **singular**.

Then the behavior can change dramatically.

The root may:

- disappear at the next power,
- produce $p$ descendants,
- continue branching at later levels.

So the derivative is not a decorative calculus object.

It controls the local arithmetic geometry of the root.

---

## A small singular example

Consider:

$$
f(x)=x^2
$$

modulo $2$.

We have:

$$
f(0)\equiv0\pmod2.
$$

But:

$$
f'(x)=2x,
$$

so:

$$
f'(0)\equiv0\pmod2.
$$

This is a singular root.

Now lift to modulo $4$.

Candidates reducing to $0\pmod2$ are:

$$
0
$$

and:

$$
2.
$$

Both satisfy:

$$
x^2\equiv0\pmod4.
$$

Thus one root modulo $2$ branches into two roots modulo $4$.

This behavior would be impossible in the simple-root case.

---

## Why CRT and Hensel fit together

CRT and Hensel lifting solve different parts of the same problem.

CRT decomposes across **different primes**:

$$
m
=
p_1^{\alpha_1}
\cdots
p_r^{\alpha_r}.
$$

Hensel lifting moves **vertically through powers of one prime**:

$$
p
\rightarrow
p^2
\rightarrow
p^3
\rightarrow\cdots.
$$

So the complete structure looks like:

```text
                modulus m
                    |
        +-----------+-----------+
        |           |           |
      p1^a1       p2^a2       pr^ar
        |           |           |
    Hensel       Hensel       Hensel
        |           |           |
   local roots  local roots  local roots
        \           |           /
         \          |          /
          +---------+---------+
                    |
                   CRT
                    |
              global roots
```

This is one of the most reusable patterns in computational number theory.

---

## Why this matters in cryptography

Polynomial congruences occur in many places in cryptography, although the exact algebraic setting varies.

### RSA and modular equations

RSA arithmetic takes place modulo:

$$
N=pq.
$$

CRT decomposes computations into arithmetic modulo $p$ and $q$, then reconstructs modulo $N$.

Questions about roots modulo composite integers also connect closely to factorization-based cryptography.

### Square roots modulo composites

For:

$$
N=pq
$$

with distinct odd primes, a quadratic residue typically has roots determined independently modulo $p$ and modulo $q$.

CRT combines the choices.

This is the arithmetic structure behind several factoring-related constructions and assumptions.

### Prime powers

Prime-power rings:

$$
\mathbb Z/p^k\mathbb Z
$$

appear naturally in computational number theory and in more advanced algebraic constructions.

Hensel lifting lets us transfer local solutions from:

$$
\mathbb F_p
$$

to higher powers of $p$.

### Polynomial rings

Modern cryptography increasingly performs arithmetic not only with integers but with polynomial quotient rings such as:

$$
\mathbb Z_q[x]/(f(x)).
$$

The specific algorithms differ from the single-variable integer congruences studied here, but the general lessons remain valuable:

- reduce modulo algebraic constraints,
- understand invertibility,
- factor structures when possible,
- reconstruct from local information,
- treat roots and multiplicities carefully.

### Elliptic curves

Elliptic curves require solving polynomial equations over finite fields.

For example:

$$
y^2
=
x^3+ax+b
\pmod p.
$$

This is not a Hensel-lifting problem in ordinary ECC usage, but understanding roots and polynomial equations over modular systems is part of the mathematical preparation needed to reason about such curves.

---

## An important conceptual distinction

There are several different kinds of equations in number theory:

### Integer Diophantine equation

$$
f(x_1,\ldots,x_n)=0
$$

with solutions sought in:

$$
\mathbb Z.
$$

### Polynomial congruence

$$
f(x)
\equiv0
\pmod m.
$$

Solutions are residue classes modulo $m$.

### Polynomial equation over a finite field

$$
f(x)=0
$$

with:

$$
x\in\mathbb F_p.
$$

### $p$-adic lifting problem

Start from a solution modulo $p^k$ and refine it to increasing powers:

$$
p^k
\rightarrow
p^{k+1}.
$$

These problems interact, but they are not interchangeable.

Keeping the ambient arithmetic structure explicit prevents many common mistakes.

---

## Practice and checkpoint

### Exercise 1 — Linear congruence

Solve:

$$
18x
\equiv30
\pmod{42}.
$$

First compute:

$$
\gcd(18,42).
$$

How many solutions should exist modulo $42$?

Find all of them.

### Exercise 2 — No solution

Determine whether:

$$
12x
\equiv5
\pmod{18}
$$

has a solution.

Explain your answer using the GCD criterion.

### Exercise 3 — Diophantine connection

Rewrite:

$$
17x
\equiv30
\pmod{49}
$$

as a linear Diophantine equation.

Find one integer pair:

$$
(x,y)
$$

satisfying it.

### Exercise 4 — Modular inverse

Compute:

$$
37^{-1}
\pmod{101}
$$

using the Extended Euclidean Algorithm.

Verify the result with:

```python
pow(37, -1, 101)
```

### Exercise 5 — Polynomial roots

Find every solution of:

$$
x^2
\equiv1
\pmod8.
$$

How many roots are there?

Compare this with the prime-modulus case.

### Exercise 6 — Simple Hensel lift

Solve:

$$
x^2-2
\equiv0
\pmod7.
$$

For each root, compute:

$$
f'(x)=2x.
$$

Determine which roots are simple.

Then lift them to solutions modulo:

$$
49.
$$

### Exercise 7 — Singular lifting

Study:

$$
x^2
\equiv0
\pmod{2^k}
$$

for:

$$
k=1,2,3,4.
$$

Observe how the root structure changes.

### Exercise 8 — CRT root counting

Suppose a polynomial has:

$$
3
$$

roots modulo $8$,

$$
2
$$

roots modulo $5$,

and:

$$
4
$$

roots modulo $7$.

Assuming the local root sets are correct, how many roots does it have modulo:

$$
8\cdot5\cdot7?
$$

Explain why.

### Exercise 9 — Verify the $315$ example

For every:

$$
x
\in
\{
29,
38,
94,
148,
164,
218,
274,
283
\},
$$

verify:

$$
x^2+3x+17
\equiv0
\pmod{315}.
$$

Then reduce every root separately modulo:

$$
9,
5,
7.
$$

Identify the local-root combination that generated it.

### Reader checkpoint

You should now be able to explain:

1. What it means to solve
   $$
   f(x)\equiv0\pmod m.
   $$

2. Why
   $$
   ax\equiv b\pmod m
   $$
   is solvable exactly when
   $$
   \gcd(a,m)\mid b.
   $$

3. Why there are exactly
   $$
   \gcd(a,m)
   $$
   solutions when a linear congruence is solvable.

4. How a linear congruence becomes a Diophantine equation.

5. Why modular division requires an inverse.

6. Why polynomial congruences modulo a composite modulus can be decomposed into prime-power problems.

7. How CRT reconstructs the global roots.

8. Why the number of global roots is the product of the numbers of local roots.

9. Why a lift from $p^k$ to $p^{k+1}$ has the form
   $$
   a+t p^k.
   $$

10. How the Hensel lifting equation
    $$
    f'(a)t
    \equiv
    -\frac{f(a)}{p^k}
    \pmod p
    $$
    arises.

11. Why
    $$
    f'(a)\not\equiv0\pmod p
    $$
    implies a unique lift.

12. Why singular roots can branch or disappear.

13. How Hensel lifting and CRT complement each other.

If these ideas are clear, then modular equations are no longer just isolated congruence exercises.

They form a structured computational problem that can be decomposed, lifted, and reconstructed.

---

## References and further reading

**Kenneth H. Rosen**,  
*Elementary Number Theory and Its Applications.*

A clear introduction to linear congruences, Diophantine equations, modular inverses, and the Chinese Remainder Theorem.

**Ivan Niven, Herbert S. Zuckerman, and Hugh L. Montgomery**,  
*An Introduction to the Theory of Numbers.*

A classical reference for congruences and elementary number-theoretic equation solving.

**Kenneth Ireland and Michael Rosen**,  
*A Classical Introduction to Modern Number Theory.*

Useful for the transition from elementary congruences to deeper local and algebraic number theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Particularly valuable for translating modular equation solving into efficient computational algorithms.

**Fernando Q. Gouvêa**,  
*p-adic Numbers: An Introduction.*

A natural next reference for understanding why Hensel lifting is much more than an isolated modular trick.

---

## Where this leads

We have now combined several tools developed throughout the entire reference series:

$$
\gcd
\rightarrow
\text{Bézout}
\rightarrow
\text{modular inverse}
\rightarrow
\text{linear congruence},
$$

then:

$$
\text{factorization of }m
\rightarrow
\text{prime powers},
$$

then:

$$
\text{roots mod }p
\rightarrow
\text{Hensel lifting}
\rightarrow
\text{roots mod }p^k,
$$

and finally:

$$
\text{local roots}
\rightarrow
\text{CRT}
\rightarrow
\text{global roots}.
$$

The broader lesson is one that will appear repeatedly later in algebra and cryptography:

$$
\boxed{
\text{decompose}
\rightarrow
\text{solve locally}
\rightarrow
\text{lift}
\rightarrow
\text{reconstruct}.
}
$$

From here, the natural direction is toward deeper nonlinear congruences, quadratic equations, residue symbols, finite fields, and the richer polynomial structures that appear throughout modern cryptography.
