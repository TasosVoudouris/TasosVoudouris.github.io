---
title: "Computational Number Theory IV: Dirichlet Characters and Gauss Sums"
description: "Dirichlet and finite-field characters, additive characters, orthogonality, Gauss sums, quadratic Gauss sums, Fourier structure, and computational verification."
pubDate: "2025-05-24"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Finite Fields"
tags:
  - "dirichlet-characters"
  - "multiplicative-characters"
  - "gauss-sums"
  - "quadratic-character"
  - "roots-of-unity"
difficulty: "Advanced"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 4
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

Gauss sums sit at an important meeting point between two different structures of a finite field.

The multiplicative group:

\[
\mathbb F_q^\times
\]

has multiplicative characters.

The additive group:

\[
(\mathbb F_q,+)
\]

has additive characters.

A Gauss sum combines the two:

\[
\boxed{
G(\chi,\psi)
=
\sum_{x\in\mathbb F_q^\times}
\chi(x)\psi(x).
}
\]

So one finite sum simultaneously sees:

\[
\boxed{
\text{multiplicative structure}
}
\]

and:

\[
\boxed{
\text{additive Fourier structure}.
}
\]

This is why Gauss sums appear throughout:

- quadratic reciprocity,
- finite-field harmonic analysis,
- exponential-sum estimates,
- coding theory,
- algebraic curves,
- point counting,
- character sums,
- and later Jacobi sums.

The conceptual progression is:

\[
\boxed{
\text{Dirichlet characters}
\rightarrow
\text{finite-field characters}
\rightarrow
\text{additive characters}
\rightarrow
\text{orthogonality}
\rightarrow
\text{Gauss sums}.
}
\]

---

## Table of Contents

- [Dirichlet and multiplicative characters](#dirichlet-and-multiplicative-characters)
- [Additive characters and orthogonality](#additive-characters-and-orthogonality)
- [Gauss sums](#gauss-sums)
- [(q-1)](#q-1)
- [The quadratic Gauss sum](#the-quadratic-gauss-sum)
- [\zeta_5](#zeta_5)
- [\zeta_5^2](#zeta_52)
- [(
\zeta_5+\zeta_5^4
)](#zeta_5zeta_54)
- [e^${2\pi i/3}](#e2pi-i3)
- [The finite Fourier viewpoint](#the-finite-fourier-viewpoint)
- [Computational verification](#computational-verification)
- [Why Gauss sums matter](#why-gauss-sums-matter)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Dirichlet and multiplicative characters

A **Dirichlet character modulo \(m\)** is an arithmetic function:

\[
\chi:\mathbb Z\rightarrow\mathbb C
\]

that is periodic modulo \(m\), completely multiplicative, and satisfies:

\[
\chi(n)=0
\]

whenever:

\[
\gcd(n,m)>1.
\]

Restricted to the units modulo \(m\), it is a group homomorphism:

\[
\boxed{
\chi:
(\mathbb Z/m\mathbb Z)^\times
\rightarrow
\mathbb C^\times.
}
\]

Since:

\[
(\mathbb Z/m\mathbb Z)^\times
\]

is finite, the nonzero values of \(\chi\) are roots of unity.

---

### Prime modulus

When:

\[
m=p
\]

is prime:

\[
(\mathbb Z/p\mathbb Z)^\times
=
\mathbb F_p^\times.
\]

So a Dirichlet character modulo \(p\) can be viewed as a multiplicative character:

\[
\boxed{
\chi:
\mathbb F_p^\times
\rightarrow
\mathbb C^\times,
}
\]

extended by:

\[
\chi(0)=0.
\]

This is the setting most directly connected with classical Gauss sums.

---

### Multiplicative characters over \(\mathbb F_q\)

More generally, let:

\[
\mathbb F_q
\]

be any finite field.

A **multiplicative character** is a group homomorphism:

\[
\boxed{
\chi:
\mathbb F_q^\times
\rightarrow
\mathbb C^\times.
}
\]

Therefore:

\[
\chi(xy)
=
\chi(x)\chi(y).
\]

Because:

\[
\mathbb F_q^\times
\]

is cyclic of order:

\[
q-1,
\]

every character is determined by its value on a generator.

Let:

\[
g
\]

generate:

\[
\mathbb F_q^\times.
\]

If:

\[
\zeta_{q-1}
=
e^{2\pi i/(q-1)},
\]

then characters have the form:

\[
\boxed{
\chi_k(g^j)
=
\zeta_{q-1}^{kj}
}
\]

for:

\[
k=0,1,\ldots,q-2.
\]

Thus the multiplicative character group is itself cyclic:

\[
\boxed{
\widehat{\mathbb F_q^\times}
\cong
\mathbb Z/(q-1)\mathbb Z.
}
\]

---

### The trivial character

The character:

\[
\chi_0(x)=1
\]

for every:

\[
x\in\mathbb F_q^\times
\]

is called the **trivial character**.

When multiplicative characters are extended to the whole field for character-sum calculations, the usual convention is:

\[
\chi(0)=0.
\]

The trivial and nontrivial cases often behave differently in sums, so they must be distinguished explicitly.

---

### The quadratic character

For an odd prime:

\[
p,
\]

the most important example is the Legendre symbol:

\[
\boxed{
\chi(a)
=
\left(
\frac ap
\right).
}
\]

For:

\[
a\not\equiv0\pmod p,
\]

we have:

\[
\chi(a)
=
\begin{cases}
1,
&
a\text{ is a quadratic residue mod }p,
\\[4pt]
-1,
&
a\text{ is a quadratic nonresidue mod }p.
\end{cases}
\]

And:

\[
\chi(0)=0.
\]

The character is multiplicative:

\[
\boxed{
\left(
\frac{ab}{p}
\right)
=
\left(
\frac ap
\right)
\left(
\frac bp
\right).
}
\]

Euler's criterion gives the equivalent expression:

\[
\boxed{
\left(
\frac ap
\right)
\equiv
a^{(p-1)/2}
\pmod p.
}
\]

---

### Example modulo \(5\)

The nonzero squares modulo \(5\) are:

\[
1^2\equiv1,
\]

\[
2^2\equiv4,
\]

\[
3^2\equiv4,
\]

\[
4^2\equiv1.
\]

So:

\[
1,4
\]

are quadratic residues, while:

\[
2,3
\]

are nonresidues.

Therefore:

\[
\chi(1)=1,
\]

\[
\chi(2)=-1,
\]

\[
\chi(3)=-1,
\]

\[
\chi(4)=1.
\]

---

## Additive characters and orthogonality

Multiplicative characters describe:

\[
\mathbb F_q^\times.
\]

To interact with the additive structure of the field, we need **additive characters**.

An additive character is a homomorphism:

\[
\boxed{
\psi:
(\mathbb F_q,+)
\rightarrow
\mathbb C^\times
}
\]

satisfying:

\[
\psi(x+y)
=
\psi(x)\psi(y).
\]

---

### Prime fields

For:

\[
\mathbb F_p,
\]

define:

\[
\boxed{
\psi_a(x)
=
e^{2\pi i ax/p}
}
\]

for:

\[
a\in\mathbb F_p.
\]

The case:

\[
a=0
\]

gives the trivial additive character:

\[
\psi_0(x)=1.
\]

For:

\[
a\neq0,
\]

the character is nontrivial.

The standard choice is:

\[
\boxed{
\psi(x)
=
e^{2\pi i x/p}.
}
\]

---

### Extension fields

Let:

\[
q=p^n.
\]

We cannot directly interpret an arbitrary:

\[
x\in\mathbb F_q
\]

as an integer modulo \(p\).

Instead we use the field trace:

\[
\operatorname{Tr}_{\mathbb F_q/\mathbb F_p}(x)
\in
\mathbb F_p.
\]

The canonical additive character is:

\[
\boxed{
\psi(x)
=
\exp
\left(
\frac{2\pi i}{p}
\operatorname{Tr}_{\mathbb F_q/\mathbb F_p}(x)
\right).
}
\]

More generally:

\[
\boxed{
\psi_a(x)
=
\exp
\left(
\frac{2\pi i}{p}
\operatorname{Tr}(ax)
\right)
}
\]

for:

\[
a\in\mathbb F_q.
\]

Every additive character of:

\[
\mathbb F_q
\]

arises this way.

---

### Additive orthogonality

Let:

\[
\psi
\]

be a nontrivial additive character.

Then:

\[
\boxed{
\sum_{x\in\mathbb F_q}
\psi(x)
=
0.
}
\]

To see why, choose:

\[
a\in\mathbb F_q
\]

with:

\[
\psi(a)\neq1.
\]

Then:

\[
\sum_x\psi(x)
=
\sum_x\psi(x+a).
\]

But:

\[
\psi(x+a)
=
\psi(x)\psi(a).
\]

Therefore:

\[
S
=
\psi(a)S.
\]

Since:

\[
\psi(a)\neq1,
\]

we obtain:

\[
\boxed{
S=0.
}
\]

---

### Multiplicative orthogonality

If:

\[
\chi
\]

is a nontrivial multiplicative character, then:

\[
\boxed{
\sum_{x\in\mathbb F_q^\times}
\chi(x)
=
0.
}
\]

The proof is analogous.

Choose:

\[
a
\]

with:

\[
\chi(a)\neq1.
\]

Multiplication by \(a\) permutes:

\[
\mathbb F_q^\times.
\]

Therefore:

\[
S
=
\sum_x\chi(ax)
=
\chi(a)S,
\]

forcing:

\[
S=0.
\]

These two cancellation identities are the basic algebraic mechanism behind character sums.

---

## Gauss sums

Let:

\[
\chi
\]

be a multiplicative character of:

\[
\mathbb F_q^\times
\]

and let:

\[
\psi
\]

be a nontrivial additive character of:

\[
\mathbb F_q.
\]

The associated **Gauss sum** is:

\[
\boxed{
G(\chi,\psi)
=
\sum_{x\in\mathbb F_q^\times}
\chi(x)\psi(x).
}
\]

If \(\chi(0)=0\), we may equivalently write:

\[
\boxed{
G(\chi,\psi)
=
\sum_{x\in\mathbb F_q}
\chi(x)\psi(x).
}
\]

When the additive character is understood, we often abbreviate:

\[
G(\chi).
\]

---

### Trivial multiplicative character

If:

\[
\chi=\chi_0
\]

is trivial and \(\psi\) is nontrivial, then:

\[
G(\chi_0,\psi)
=
\sum_{x\neq0}\psi(x).
\]

Since:

\[
\sum_{x\in\mathbb F_q}\psi(x)=0,
\]

we have:

\[
\boxed{
G(\chi_0,\psi)=-1.
}
\]

So the famous square-root magnitude theorem concerns **nontrivial multiplicative characters**.

---

### Scaling the additive character

Let:

\[
a\in\mathbb F_q^\times
\]

and define:

\[
\psi_a(x)=\psi(ax).
\]

Then:

\[
G(\chi,\psi_a)
=
\sum_{x\neq0}
\chi(x)\psi(ax).
\]

Substitute:

\[
y=ax.
\]

Then:

\[
x=a^{-1}y.
\]

Therefore:

\[
\chi(x)
=
\chi(a)^{-1}\chi(y).
\]

Hence:

\[
\boxed{
G(\chi,\psi_a)
=
\chi(a)^{-1}
G(\chi,\psi).
}
\]

Changing the additive frequency changes only the phase through a multiplicative-character value.

---

### Magnitude of a nontrivial Gauss sum

Suppose both:

\[
\chi
\]

and:

\[
\psi
\]

are nontrivial.

Then:

\[
\boxed{
|G(\chi,\psi)|
=
\sqrt q.
}
\]

This is one of the fundamental rigidity results for finite-field character sums.

---

### Proof of the magnitude

Write:

\[
G
=
\sum_{x\neq0}
\chi(x)\psi(x).
\]

Then:

\[
|G|^2
=
G\overline G.
\]

Since character values are roots of unity:

\[
\overline{\chi(y)}
=
\chi(y)^{-1}.
\]

And for additive characters:

\[
\overline{\psi(y)}
=
\psi(-y).
\]

Therefore:

\[
|G|^2
=
\sum_{x,y\neq0}
\chi(x)
\chi(y)^{-1}
\psi(x-y).
\]

Set:

\[
x=ty.
\]

Then:

\[
\chi(x)\chi(y)^{-1}
=
\chi(t).
\]

So:

\[
|G|^2
=
\sum_{t\neq0}
\chi(t)
\sum_{y\neq0}
\psi(
y(t-1)
).
\]

If:

\[
t=1,
\]

then:

\[
\sum_{y\neq0}\psi(0)
=
q-1.
\]

If:

\[
t\neq1,
\]

multiplication by:

\[
t-1
\]

permutes:

\[
\mathbb F_q^\times.
\]

Hence:

\[
\sum_{y\neq0}
\psi(
y(t-1)
)
=
\sum_{u\neq0}\psi(u)
=
-1.
\]

Thus:

\[
|G|^2
=
(q-1)
-
\sum_{t\neq1}
\chi(t).
\]

Since \(\chi\) is nontrivial:

\[
\sum_{t\neq0}\chi(t)=0.
\]

Therefore:

\[
\sum_{t\neq1}\chi(t)
=
-1.
\]

Hence:

\[
|G|^2
=
q.
\]

So:

\[
\boxed{
|G(\chi,\psi)|=\sqrt q.
}
\]

The phase depends on arithmetic structure.

The magnitude does not.

---

## The quadratic Gauss sum

The classical example occurs over:

\[
\mathbb F_p
\]

for an odd prime \(p\).

Let:

\[
\chi(x)
=
\left(
\frac{x}{p}
\right)
\]

be the quadratic character and:

\[
\psi(x)
=
e^{2\pi i x/p}.
\]

Then:

\[
\boxed{
G_p
=
\sum_{x=1}^{p-1}
\left(
\frac{x}{p}
\right)
e^{2\pi i x/p}.
}
\]

This is the classical quadratic Gauss sum.

---

### Squaring the Gauss sum

A fundamental identity is:

\[
\boxed{
G_p^2
=
\left(
\frac{-1}{p}
\right)p.
}
\]

Recall:

\[
\left(
\frac{-1}{p}
\right)
=
(-1)^{(p-1)/2}.
\]

Therefore:

\[
G_p^2
=
\begin{cases}
p,
&
p\equiv1\pmod4,
\\[4pt]
-p,
&
p\equiv3\pmod4.
\end{cases}
\]

So:

\[
|G_p|=\sqrt p.
\]

---

### Real versus imaginary

If:

\[
p\equiv1\pmod4,
\]

then:

\[
G_p^2=p,
\]

so the Gauss sum is real.

If:

\[
p\equiv3\pmod4,
\]

then:

\[
G_p^2=-p,
\]

so it is purely imaginary.

For the standard additive character:

\[
e^{2\pi i x/p},
\]

the classical evaluation is:

\[
\boxed{
G_p
=
\begin{cases}
\sqrt p,
&
p\equiv1\pmod4,
\\[6pt]
i\sqrt p,
&
p\equiv3\pmod4.
\end{cases}
}
\]

The exact phase depends on the normalization of the additive character.

---

### Example: \(p=5\)

The quadratic character values are:

\[
\chi(1)=1,
\]

\[
\chi(2)=-1,
\]

\[
\chi(3)=-1,
\]

\[
\chi(4)=1.
\]

Let:

\[
\zeta_5=e^{2\pi i/5}.
\]

Then:

\[
G_5
=
\zeta_5
-
\zeta_5^2
-
\zeta_5^3
+
\zeta_5^4.
\]

Grouping conjugates:

\[
G_5
=
(
\zeta_5+\zeta_5^4
)
-
(
\zeta_5^2+\zeta_5^3
).
\]

This evaluates to:

\[
\boxed{
G_5=\sqrt5.
}
\]

Consequently:

\[
G_5^2=5,
\]

as predicted because:

\[
5\equiv1\pmod4.
\]

---

### Example: \(p=3\)

For:

\[
p=3,
\]

we have:

\[
\chi(1)=1,
\qquad
\chi(2)=-1.
\]

Thus:

\[
G_3
=
e^{2\pi i/3}
-
e^{4\pi i/3}.
\]

Therefore:

\[
\boxed{
G_3=i\sqrt3.
}
\]

And:

\[
G_3^2=-3.
\]

Since:

\[
3\equiv3\pmod4,
\]

this again matches:

\[
G_p^2
=
\chi(-1)p.
\]

---

## The finite Fourier viewpoint

Gauss sums are not isolated tricks.

They are Fourier transforms.

Let:

\[
f:\mathbb F_q\rightarrow\mathbb C.
\]

The finite additive Fourier transform may be written schematically as:

\[
\boxed{
\widehat f(a)
=
\sum_{x\in\mathbb F_q}
f(x)\psi_a(x).
}
\]

Now choose:

\[
f(x)=\chi(x),
\]

where \(\chi\) is a multiplicative character extended by:

\[
\chi(0)=0.
\]

Then:

\[
\widehat\chi(a)
=
\sum_x
\chi(x)\psi_a(x).
\]

For:

\[
a\neq0,
\]

the scaling identity gives:

\[
\boxed{
\widehat\chi(a)
=
\chi(a)^{-1}
G(\chi,\psi).
}
\]

So the Fourier transform of a nontrivial multiplicative character is essentially another copy of that character, multiplied by one scalar Gauss sum.

This is a remarkably rigid phenomenon.

---

### Two incompatible-looking structures

The additive group:

\[
(\mathbb F_q,+)
\]

and multiplicative group:

\[
\mathbb F_q^\times
\]

are very different algebraic objects.

Yet the Gauss sum:

\[
\sum_x\chi(x)\psi(x)
\]

forces them to interact.

That is the deeper reason roots of unity appear everywhere in this subject.

The multiplicative character contributes one family of phases.

The additive character contributes another.

Their correlation produces arithmetic information.

---

### Character orthogonality as Fourier cancellation

The identity:

\[
\sum_x\psi(x)=0
\]

for nontrivial \(\psi\) is exactly a finite Fourier cancellation phenomenon.

Likewise:

\[
\sum_{x\neq0}\chi(x)=0
\]

says that a nontrivial character averages to zero over its group.

Gauss sums measure what happens when these two oscillatory structures are multiplied rather than considered separately.

---

### Geometric interpretation

A character sum is a sum of complex numbers lying on the unit circle.

Without cancellation, a sum of \(q\) such terms could have magnitude of order:

\[
q.
\]

But for a nontrivial Gauss sum:

\[
\boxed{
|G|=\sqrt q.
}
\]

So there is strong cancellation.

The square-root scale is a recurring theme throughout analytic and algebraic number theory.

It reappears in more sophisticated character sums and ultimately in bounds connected with algebraic curves over finite fields.

---

![Gauss and Jacobi sum computation](/images/mathematics/gauss-jacobi-plot.png)

---

## Computational verification

Gauss sums are excellent examples of objects that can be explored numerically while retaining exact algebraic identities.

But one must distinguish:

\[
\boxed{
\text{numerical verification}
}
\]

from:

\[
\boxed{
\text{exact proof}.
}
\]

---

### Computing the Legendre symbol

For an odd prime \(p\), Euler's criterion can compute the quadratic character.

```python
def legendre_symbol(
    a: int,
    p: int,
) -> int:
    a %= p

    if a == 0:
        return 0

    value = pow(
        a,
        (p - 1) // 2,
        p,
    )

    if value == 1:
        return 1

    if value == p - 1:
        return -1

    raise ArithmeticError(
        "unexpected Euler-criterion value"
    )
```

---

### Numerical quadratic Gauss sum

Using Python complex arithmetic:

```python
import cmath
import math


def quadratic_gauss_sum(
    p: int,
) -> complex:
    total = 0j

    for x in range(1, p):
        chi = legendre_symbol(
            x,
            p,
        )

        psi = cmath.exp(
            2j
            * math.pi
            * x
            / p
        )

        total += chi * psi

    return total
```

For:

```python
for p in [3, 5, 7, 11, 13]:
    G = quadratic_gauss_sum(p)

    print(
        p,
        G,
        abs(G),
        math.sqrt(p),
    )
```

we should observe numerically:

\[
\boxed{
|G|\approx\sqrt p.
}
\]

For:

\[
p\equiv1\pmod4,
\]

the result should be approximately real.

For:

\[
p\equiv3\pmod4,
\]

it should be approximately purely imaginary.

---

### Floating-point error

A numerical computation may return something such as:

```text
2.2360679774997894 - 2.2e-16j
```

instead of exactly:

\[
\sqrt5.
\]

The tiny imaginary part is not arithmetic structure.

It is floating-point error.

Therefore a numerical experiment should test with tolerances:

```python
G = quadratic_gauss_sum(5)

assert abs(
    abs(G) - math.sqrt(5)
) < 1e-10
```

rather than expecting exact equality of floating-point values.

---

### Exact computation in SageMath

Sage can perform the same computation inside a cyclotomic field.

For a prime \(p\):

```python
p = 5

K.<zeta> = CyclotomicField(p)

G = sum(
    kronecker(a, p) * zeta^a
    for a in range(1, p)
)

print(G)
print(G^2)
```

For:

\[
p=5,
\]

the exact result satisfies:

\[
\boxed{
G^2=5.
}
\]

For:

\[
p=7,
\]

it satisfies:

\[
\boxed{
G^2=-7.
}
\]

This avoids replacing an exact root-of-unity identity with floating-point approximation.

---

### Extension-field experiment

For:

\[
q=p^n,
\]

the additive character must use the trace:

\[
\psi(x)
=
\exp
\left(
\frac{2\pi i}{p}
\operatorname{Tr}(x)
\right).
\]

A computational implementation therefore needs:

```text
finite-field arithmetic
        +
field trace
        +
multiplicative character
        +
root-of-unity evaluation
```

The finite-field machinery developed earlier in CryptoCave is therefore directly reused here.

---

### What should be tested

A useful computational test suite can verify:

\[
\sum_{x\neq0}\chi(x)=0
\]

for nontrivial \(\chi\),

\[
\sum_x\psi(x)=0
\]

for nontrivial \(\psi\),

and:

\[
|G(\chi,\psi)|^2=q.
\]

For quadratic characters over prime fields, it can additionally verify:

\[
\boxed{
G_p^2
=
\chi(-1)p.
}
\]

These tests validate an implementation against the mathematics.

They do not replace the proofs.

---

## Why Gauss sums matter

Gauss sums matter because they translate between algebraic structures that normally look unrelated.

They connect:

\[
\boxed{
\text{multiplicative characters}
}
\]

with:

\[
\boxed{
\text{additive characters}.
}
\]

That interaction appears repeatedly throughout number theory.

---

### Quadratic reciprocity

Quadratic Gauss sums provide one of the classical routes to quadratic reciprocity.

The phase:

\[
G_p^2
=
\left(
\frac{-1}{p}
\right)p
\]

already detects the distinction:

\[
p\equiv1\pmod4
\]

versus:

\[
p\equiv3\pmod4.
\]

So the same congruence phenomenon that controlled prime splitting in:

\[
\mathbb Z[i]
\]

reappears through character sums.

---

### Exponential sums

Many number-theoretic problems reduce to estimating sums of oscillatory terms:

\[
\sum_x
\chi(x)\psi(f(x)).
\]

The trivial bound from counting terms may be of size:

\[
q.
\]

But arithmetic cancellation can reduce the true magnitude toward a square-root scale.

Understanding such cancellation is one of the central themes of modern number theory.

---

### Coding theory

Character sums appear when counting field elements satisfying trace, norm, and polynomial constraints.

Such counts can determine:

- code weights,
- correlation distributions,
- sequence properties,
- combinatorial structures over finite fields.

---

### Algebraic curves

For curves over:

\[
\mathbb F_q,
\]

point-counting problems often reduce to sums involving multiplicative characters.

For example, consider:

\[
y^2=f(x)
\]

over an odd finite field.

For each \(x\), the number of \(y\)-solutions is controlled by the quadratic character of:

\[
f(x).
\]

Schematically:

\[
\#E(\mathbb F_q)
\]

can therefore involve sums of the form:

\[
\boxed{
\sum_{x\in\mathbb F_q}
\chi(f(x)).
}
\]

This is one route from character sums to elliptic-curve point counting.

---

### From Gauss sums to Jacobi sums

Gauss sums mix:

\[
\text{multiplicative}
\]

and:

\[
\text{additive}
\]

characters.

The next natural object instead correlates multiplicative characters directly.

A **Jacobi sum** has the form:

\[
\boxed{
J(\chi,\lambda)
=
\sum_{x\in\mathbb F_q}
\chi(x)
\lambda(1-x).
}
\]

These sums are intimately connected with Gauss sums.

Under suitable nontriviality conditions:

\[
\boxed{
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}.
}
\]

That identity will become one of the main structural tools in the next article.

---

## The structural picture

We began with multiplicative characters:

\[
\boxed{
\chi:
\mathbb F_q^\times
\rightarrow
\mathbb C^\times.
}
\]

Then additive characters:

\[
\boxed{
\psi:
\mathbb F_q
\rightarrow
\mathbb C^\times.
}
\]

Each family individually satisfies orthogonality:

\[
\sum_{x\neq0}\chi(x)=0,
\]

and:

\[
\sum_x\psi(x)=0
\]

for nontrivial characters.

Gauss sums combine them:

\[
\boxed{
G(\chi,\psi)
=
\sum_x
\chi(x)\psi(x).
}
\]

For nontrivial \(\chi\) and \(\psi\):

\[
\boxed{
|G(\chi,\psi)|=\sqrt q.
}
\]

For the quadratic character over:

\[
\mathbb F_p,
\]

the stronger identity is:

\[
\boxed{
G_p^2
=
\left(
\frac{-1}{p}
\right)p.
}
\]

So:

\[
\boxed{
\text{characters}
\rightarrow
\text{orthogonality}
\rightarrow
\text{Fourier cancellation}
\rightarrow
\text{arithmetic information}.
}
\]

That is the essential mechanism behind Gauss sums.

---

## Practice and checkpoint

### Exercise 1 — Quadratic character

For:

\[
p=7,
\]

compute:

\[
\left(
\frac ap
\right)
\]

for:

\[
a=1,\ldots,6.
\]

Identify the quadratic residues and nonresidues.

---

### Exercise 2 — Multiplicativity

Using your values modulo \(7\), verify on several examples that:

\[
\left(
\frac{ab}{7}
\right)
=
\left(
\frac a7
\right)
\left(
\frac b7
\right).
\]

---

### Exercise 3 — Multiplicative orthogonality

For the quadratic character modulo \(7\), verify:

\[
\sum_{x=1}^{6}
\left(
\frac x7
\right)
=
0.
\]

---

### Exercise 4 — Additive orthogonality

Let:

\[
\zeta_5=e^{2\pi i/5}.
\]

Verify:

\[
1+\zeta_5+\zeta_5^2+\zeta_5^3+\zeta_5^4=0.
\]

Interpret this as an additive-character orthogonality relation.

---

### Exercise 5 — Quadratic Gauss sum modulo \(5\)

Compute:

\[
G_5
=
\sum_{x=1}^{4}
\left(
\frac x5
\right)
e^{2\pi ix/5}.
\]

Verify:

\[
G_5=\sqrt5.
\]

---

### Exercise 6 — Quadratic Gauss sum modulo \(3\)

Compute:

\[
G_3.
\]

Verify:

\[
G_3=i\sqrt3.
\]

---

### Exercise 7 — Magnitude theorem

Starting from:

\[
G
=
\sum_{x\neq0}
\chi(x)\psi(x),
\]

derive:

\[
|G|^2=q
\]

using the substitution:

\[
x=ty.
\]

Identify exactly where multiplicative and additive orthogonality enter the proof.

---

### Exercise 8 — Scaling

Let:

\[
\psi_a(x)=\psi(ax).
\]

Prove:

\[
G(\chi,\psi_a)
=
\chi(a)^{-1}
G(\chi,\psi)
\]

for:

\[
a\neq0.
\]

---

### Exercise 9 — Trace character

Let:

\[
\mathbb F_{p^n}/\mathbb F_p.
\]

Explain why:

\[
\psi(x)
=
\exp
\left(
\frac{2\pi i}{p}
\operatorname{Tr}(x)
\right)
\]

satisfies:

\[
\psi(x+y)
=
\psi(x)\psi(y).
\]

---

### Exercise 10 — Fourier viewpoint

Suppose:

\[
f(x)=\chi(x)
\]

for a nontrivial multiplicative character.

Show that for:

\[
a\neq0,
\]

its additive Fourier transform satisfies:

\[
\widehat f(a)
=
\chi(a)^{-1}G(\chi).
\]

What does this say about the Fourier spectrum of a multiplicative character?

---

### Exercise 11 — Numerical versus exact arithmetic

Compute:

\[
G_5
\]

using ordinary floating-point complex arithmetic.

Then compute it in a cyclotomic field.

Why might the first produce a tiny nonzero imaginary part even though the exact answer is real?

---

### Exercise 12 — Curve connection

Let:

\[
\chi
\]

be the quadratic character over an odd finite field.

Explain why the number of solutions:

\[
y
\]

to:

\[
y^2=a
\]

is:

\[
1+\chi(a)
\]

when \(\chi(0)=0\).

Use this observation to explain why quadratic-character sums naturally appear when counting points on curves:

\[
y^2=f(x).
\]

---

### Reader checkpoint

You should now be able to explain:

1. What a Dirichlet character modulo \(m\) is.
2. How prime-modulus Dirichlet characters become multiplicative characters of:
   \[
   \mathbb F_p^\times.
   \]
3. Why multiplicative-character values are roots of unity.
4. What the trivial multiplicative character is.
5. Why the Legendre symbol is a quadratic character.
6. What an additive character is.
7. How additive characters of:
   \[
   \mathbb F_p
   \]
   are built from roots of unity.
8. Why extension-field additive characters require the field trace.
9. Why nontrivial additive characters sum to zero.
10. Why nontrivial multiplicative characters sum to zero.
11. What a Gauss sum is.
12. Why:
    \[
    G(\chi_0,\psi)=-1
    \]
    for the trivial multiplicative character and nontrivial additive character.
13. Why changing:
    \[
    \psi(x)
    \]
    to:
    \[
    \psi(ax)
    \]
    changes a Gauss sum by a character factor.
14. Why:
    \[
    |G(\chi,\psi)|=\sqrt q
    \]
    for nontrivial characters.
15. Why quadratic Gauss sums satisfy:
    
    \[
    G_p^2
    =
    \left(
    \frac{-1}{p}
    \right)p.
    \]
    
16. Why the quadratic Gauss sum is real for:
    \[
    p\equiv1\pmod4
    \]
    and imaginary for:
    \[
    p\equiv3\pmod4.
    \]
17. How Gauss sums are Fourier transforms of multiplicative characters.
18. Why square-root cancellation is significant.
19. Why numerical root-of-unity calculations should not be confused with exact identities.
20. Why cyclotomic-field arithmetic is useful for exact verification.
21. How character sums appear in finite-field point counting.
22. Why Jacobi sums are the natural next object.

Gauss sums show that arithmetic structure can be encoded as oscillation.

Multiplicative information becomes a pattern of roots of unity, and Fourier cancellation exposes properties that are difficult to see directly from residues alone.

---

## References and further reading

**Kenneth Ireland and Michael Rosen**,  
*A Classical Introduction to Modern Number Theory.*

An excellent reference for characters, Gauss sums, Jacobi sums, quadratic reciprocity, and cyclotomic methods.

**Harold Davenport**,  
*Multiplicative Number Theory.*

A classical source for Dirichlet characters, character sums, and their role in analytic number theory.

**Bruce C. Berndt, Ronald J. Evans, and Kenneth S. Williams**,  
*Gauss and Jacobi Sums.*

A specialized and comprehensive reference for the theory of Gauss and Jacobi sums.

**Rudolf Lidl and Harald Niederreiter**,  
*Finite Fields.*

A standard reference for finite-field characters, trace maps, Gauss sums, and finite-field applications.

**Henryk Iwaniec and Emmanuel Kowalski**,  
*Analytic Number Theory.*

A deeper modern treatment of character sums, exponential sums, and analytic methods.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Useful for connecting finite-field arithmetic and computational algebra with the theoretical structures used here.

---

## Next

Part III showed that prime splitting in:

\[
\mathbb Z[i]
\]

is controlled by congruence and quadratic-residue information.

Part IV has encoded residue information into multiplicative characters and then combined it with additive Fourier structure through:

\[
\boxed{
G(\chi,\psi).
}
\]

The next step removes the additive character and correlates multiplicative characters directly:

\[
\boxed{
J(\chi,\lambda)
=
\sum_{x\in\mathbb F_q}
\chi(x)\lambda(1-x).
}
\]

These **Jacobi sums** are closely related to Gauss sums through identities such as:

\[
\boxed{
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}
}
\]

under the appropriate nontriviality assumptions.

They also lead naturally from character theory toward:

\[
\boxed{
\text{cyclotomy}
}
\]

and:

\[
\boxed{
\text{point counting over finite fields}.
}
\]
