---
title: "Finite Fields II: Frobenius, Trace, Norm, and Subfields"
description: "The structural maps of finite-field extensions: Frobenius automorphisms, conjugates, trace, norm, fixed fields, subfields, and the cyclic Galois group."
pubDate: "2025-05-24"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Finite Fields"
  - "Abstract Algebra"
tags:
  - "frobenius"
  - "field-trace"
  - "field-norm"
  - "subfields"
  - "galois-groups"
difficulty: "Advanced"
status: "Reference"
series: "Finite Fields & Polynomial Arithmetic"
seriesOrder: 2
sourcePath: "experiments/mathematics/finite-fields"
draft: false
---

Finite fields are unusually explicit field extensions.

For a general field extension, automorphisms, conjugates, fixed fields, traces, and norms can be difficult to determine.

For finite fields, all of them are controlled by one map:

$$
\boxed{
x\longmapsto x^q.
}
$$

This is the **Frobenius automorphism**.

For the extension

$$
\mathbb F_{q^n}/\mathbb F_q,
$$

repeated Frobenius powers produce the conjugates of an element:

$$
x,
\quad
x^q,
\quad
x^{q^2},
\quad
\ldots
$$

and from those conjugates we obtain two fundamental maps:

$$
\boxed{
\operatorname{Tr}(x)
=
x+x^q+\cdots+x^{q^{n-1}}
}
$$

and

$$
\boxed{
N(x)
=
x\,x^q\cdots x^{q^{n-1}}.
}
$$

At the same time, powers of Frobenius describe every automorphism and every subfield.

So the central structure of the article is:

$$
\boxed{
\text{Frobenius}
\rightarrow
\text{conjugates}
\rightarrow
\text{trace and norm}
\rightarrow
\text{fixed fields}
\rightarrow
\text{subfields}.
}
$$

---

## Table of Contents

- [Frobenius and finite-field Galois groups](#frobenius-and-finite-field-galois-groups)
- [Frobenius conjugates and minimal polynomials](#frobenius-conjugates-and-minimal-polynomials)
- [The field trace](#the-field-trace)
- [The field norm](#the-field-norm)
- [Subfields and fixed fields](#subfields-and-fixed-fields)
- [Perfectness and separability](#perfectness-and-separability)
- [Why these maps matter computationally](#why-these-maps-matter-computationally)
- [A concrete example: $\mathbb F_4/\mathbb F_2$](#a-concrete-example-f4f2mathbb-f_4mathbb-f_2f4f2)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Frobenius and finite-field Galois groups

Let:

$$
q=p^m
$$

for a prime $p$, and consider the finite extension:

$$
\mathbb F_{q^n}/\mathbb F_q.
$$

Define:

$$
\boxed{
\varphi_q:
\mathbb F_{q^n}
\rightarrow
\mathbb F_{q^n},
\qquad
x\mapsto x^q.
}
$$

This is the **$q$-Frobenius automorphism**.

---

### Why Frobenius is a homomorphism

Because the field has characteristic $p$,

$$
(a+b)^p
=
a^p+b^p.
$$

Applying this repeatedly:

$$
(a+b)^q
=
a^q+b^q.
$$

Also:

$$
(ab)^q
=
a^qb^q.
$$

Therefore:

$$
\varphi_q(a+b)
=
\varphi_q(a)+\varphi_q(b),
$$

and:

$$
\varphi_q(ab)
=
\varphi_q(a)\varphi_q(b).
$$

So Frobenius is a field homomorphism.

Every field homomorphism is injective.

Since:

$$
\mathbb F_{q^n}
$$

is finite, injectivity implies surjectivity.

Hence:

$$
\boxed{
\varphi_q
\text{ is an automorphism}.
}
$$

---

### Frobenius fixes the base field

For every:

$$
a\in\mathbb F_q,
$$

we know:

$$
a^q=a.
$$

Therefore:

$$
\boxed{
\varphi_q(a)=a
\qquad
\forall a\in\mathbb F_q.
}
$$

Thus:

$$
\varphi_q
\in
\operatorname{Gal}
(
\mathbb F_{q^n}/\mathbb F_q
).
$$

---

### Repeated Frobenius

Applying the map $k$ times gives:

$$
\boxed{
\varphi_q^k(x)
=
x^{q^k}.
}
$$

Since every:

$$
x\in\mathbb F_{q^n}
$$

satisfies:

$$
x^{q^n}=x,
$$

we obtain:

$$
\boxed{
\varphi_q^n
=
\operatorname{id}.
}
$$

In fact, the powers:

$$
\operatorname{id},
\varphi_q,
\varphi_q^2,
\ldots,
\varphi_q^{n-1}
$$

are all the automorphisms fixing $\mathbb F_q$.

Therefore:

$$
\boxed{
\operatorname{Gal}
(
\mathbb F_{q^n}/\mathbb F_q
)
=
\langle\varphi_q\rangle
}
$$

and:

$$
\boxed{
\operatorname{Gal}
(
\mathbb F_{q^n}/\mathbb F_q
)
\cong
\mathbb Z/n\mathbb Z.
}
$$

So every finite-field extension is:

- finite;
- Galois;
- cyclic.

This exceptional regularity is one of the reasons finite fields are so tractable.

---

## Frobenius conjugates and minimal polynomials

Let:

$$
\alpha
\in
\mathbb F_{q^n}.
$$

Repeated Frobenius gives:

$$
\alpha,
\quad
\alpha^q,
\quad
\alpha^{q^2},
\quad
\ldots.
$$

These are the **Frobenius conjugates** of $\alpha$ over:

$$
\mathbb F_q.
$$

Eventually the sequence repeats.

Suppose $d$ is the smallest positive integer satisfying:

$$
\boxed{
\alpha^{q^d}=\alpha.
}
$$

Then:

$$
d\mid n.
$$

The distinct conjugates are:

$$
\boxed{
\alpha,
\alpha^q,
\ldots,
\alpha^{q^{d-1}}.
}
$$

---

### Minimal polynomial from the Frobenius orbit

The minimal polynomial of $\alpha$ over:

$$
\mathbb F_q
$$

is:

$$
\boxed{
m_\alpha(X)
=
\prod_{i=0}^{d-1}
\left(
X-\alpha^{q^i}
\right).
}
$$

It belongs to:

$$
\mathbb F_q[X].
$$

Its degree is:

$$
\boxed{
\deg m_\alpha=d.
}
$$

Therefore:

$$
\boxed{
[
\mathbb F_q(\alpha):
\mathbb F_q
]
=
d.
}
$$

This gives an important computational interpretation:

> The degree of the minimal polynomial is exactly the size of the Frobenius orbit.

---

### Example in $\mathbb F_8$

Let:

$$
\mathbb F_8
=
\mathbb F_2(\alpha)
$$

where:

$$
\alpha^3+\alpha+1=0.
$$

The Frobenius map over $\mathbb F_2$ is:

$$
x\mapsto x^2.
$$

The conjugates of $\alpha$ are:

$$
\alpha,
$$

$$
\alpha^2,
$$

and:

$$
\alpha^4.
$$

Since:

$$
\alpha^8=\alpha,
$$

the orbit closes after three elements.

Thus the minimal polynomial has degree:

$$
3.
$$

Indeed:

$$
\boxed{
m_\alpha(X)
=
X^3+X+1.
}
$$

This illustrates how the Frobenius orbit recovers the defining irreducible polynomial.

---

## The field trace

For:

$$
x\in\mathbb F_{q^n},
$$

the trace from $\mathbb F_{q^n}$ to $\mathbb F_q$ is:

$$
\boxed{
\operatorname{Tr}_{\mathbb F_{q^n}/\mathbb F_q}(x)
=
x+x^q+x^{q^2}
+\cdots+
x^{q^{n-1}}.
}
$$

Conceptually, the trace is the **sum of the Galois conjugates** of $x$, counted according to the full extension.

---

### Why the trace lies in the base field

Apply Frobenius:

$$
\begin{aligned}
\operatorname{Tr}(x)^q
&=
x^q+x^{q^2}
+\cdots+
x^{q^n}.
\end{aligned}
$$

But:

$$
x^{q^n}=x.
$$

So:

$$
\operatorname{Tr}(x)^q
=
\operatorname{Tr}(x).
$$

The elements fixed by:

$$
x\mapsto x^q
$$

are exactly:

$$
\mathbb F_q.
$$

Therefore:

$$
\boxed{
\operatorname{Tr}(x)
\in
\mathbb F_q.
}
$$

---

### Linearity

The trace is:

$$
\mathbb F_q\text{-linear}.
$$

Thus:

$$
\boxed{
\operatorname{Tr}(x+y)
=
\operatorname{Tr}(x)
+
\operatorname{Tr}(y)
}
$$

and for:

$$
a\in\mathbb F_q,
$$

$$
\boxed{
\operatorname{Tr}(ax)
=
a\operatorname{Tr}(x).
}
$$

More generally:

$$
\operatorname{Tr}(ax+by)
=
a\operatorname{Tr}(x)
+
b\operatorname{Tr}(y).
$$

So:

$$
\operatorname{Tr}:
\mathbb F_{q^n}
\rightarrow
\mathbb F_q
$$

is a linear transformation between vector spaces over $\mathbb F_q$.

---

### Trace of base-field elements

If:

$$
a\in\mathbb F_q,
$$

then:

$$
a^q=a.
$$

Therefore every term in the trace equals $a$:

$$
\operatorname{Tr}(a)
=
\underbrace{
a+\cdots+a
}_{n\text{ times}}.
$$

Hence:

$$
\boxed{
\operatorname{Tr}(a)
=
na.
}
$$

The integer $n$ is interpreted inside the characteristic-$p$ field.

Therefore it is possible that:

$$
\operatorname{Tr}(1)=0
$$

when:

$$
p\mid n.
$$

This does **not** imply that the entire trace map is zero.

---

### Surjectivity and kernel

For finite fields, the trace:

$$
\operatorname{Tr}_{\mathbb F_{q^n}/\mathbb F_q}
:
\mathbb F_{q^n}
\rightarrow
\mathbb F_q
$$

is surjective.

Since the domain has dimension $n$ over $\mathbb F_q$, while the codomain has dimension $1$, rank-nullity gives:

$$
\boxed{
\dim_{\mathbb F_q}
\ker(\operatorname{Tr})
=
n-1.
}
$$

Therefore:

$$
\boxed{
|
\ker(\operatorname{Tr})
|
=
q^{n-1}.
}
$$

So exactly:

$$
q^{n-1}
$$

elements have trace zero.

---

### Transitivity of trace

If:

$$
K\subseteq F\subseteq E
$$

are finite fields, then:

$$
\boxed{
\operatorname{Tr}_{E/K}
=
\operatorname{Tr}_{F/K}
\circ
\operatorname{Tr}_{E/F}.
}
$$

For example:

$$
\mathbb F_q
\subseteq
\mathbb F_{q^m}
\subseteq
\mathbb F_{q^{mn}}.
$$

Then:

$$
\operatorname{Tr}_{q^{mn}/q}
=
\operatorname{Tr}_{q^m/q}
\circ
\operatorname{Tr}_{q^{mn}/q^m}.
$$

This makes trace compatible with towers of field extensions.

---

## The field norm

The norm is the multiplicative analogue of the trace.

For:

$$
x\in\mathbb F_{q^n},
$$

define:

$$
\boxed{
N_{\mathbb F_{q^n}/\mathbb F_q}(x)
=
\prod_{i=0}^{n-1}
x^{q^i}.
}
$$

Thus:

$$
N(x)
=
x
\cdot
x^q
\cdot
x^{q^2}
\cdots
x^{q^{n-1}}.
$$

The exponents add:

$$
1+q+q^2+\cdots+q^{n-1}
=
\frac{q^n-1}{q-1}.
$$

Therefore:

$$
\boxed{
N(x)
=
x^{(q^n-1)/(q-1)}.
}
$$

---

### Why the norm lies in the base field

Apply Frobenius:

$$
N(x)^q.
$$

This cyclically permutes the factors:

$$
x,
x^q,
\ldots,
x^{q^{n-1}}.
$$

The product therefore remains unchanged:

$$
N(x)^q=N(x).
$$

Hence:

$$
\boxed{
N(x)\in\mathbb F_q.
}
$$

---

### Multiplicativity

For:

$$
x,y\in\mathbb F_{q^n},
$$

we have:

$$
\begin{aligned}
N(xy)
&=
\prod_{i=0}^{n-1}
(xy)^{q^i}\\
&=
\prod_{i=0}^{n-1}
x^{q^i}
\prod_{i=0}^{n-1}
y^{q^i}.
\end{aligned}
$$

Therefore:

$$
\boxed{
N(xy)
=
N(x)N(y).
}
$$

Thus:

$$
N:
\mathbb F_{q^n}^{\times}
\rightarrow
\mathbb F_q^\times
$$

is a group homomorphism.

---

### Norm of base-field elements

If:

$$
a\in\mathbb F_q,
$$

then every conjugate equals $a$.

So:

$$
\boxed{
N(a)
=
a^n.
}
$$

---

### Surjectivity and kernel

The multiplicative groups are cyclic:

$$
|\mathbb F_{q^n}^\times|
=
q^n-1
$$

and:

$$
|\mathbb F_q^\times|
=
q-1.
$$

The norm map:

$$
N:
\mathbb F_{q^n}^{\times}
\rightarrow
\mathbb F_q^\times
$$

is surjective.

Its kernel therefore has size:

$$
\boxed{
\frac{q^n-1}{q-1}.
}
$$

So:

$$
\boxed{
|
\ker N
|
=
1+q+\cdots+q^{n-1}.
}
$$

The kernel consists of exactly those nonzero elements satisfying:

$$
\boxed{
x^{(q^n-1)/(q-1)}
=
1.
}
$$

---

### Transitivity of norm

Norm also behaves well across towers:

$$
\boxed{
N_{E/K}
=
N_{F/K}
\circ
N_{E/F}.
}
$$

Thus both trace and norm respect intermediate field extensions.

---

### Trace versus norm

The two maps play complementary roles:

$$
\boxed{
\operatorname{Tr}(x)
=
\text{sum of conjugates}
}
$$

while:

$$
\boxed{
N(x)
=
\text{product of conjugates}.
}
$$

Trace interacts naturally with addition and linear algebra.

Norm interacts naturally with multiplication and multiplicative groups.

This is why the pair occurs repeatedly throughout algebra and number theory.

---

## Subfields and fixed fields

Finite fields have an exceptionally rigid subfield structure.

Let:

$$
\mathbb F_{p^n}
$$

be a finite field.

Then:

$$
\boxed{
\mathbb F_{p^d}
\subseteq
\mathbb F_{p^n}
\iff
d\mid n.
}
$$

Moreover, for each divisor:

$$
d\mid n,
$$

there is exactly one subfield of size:

$$
p^d.
$$

Thus the subfield lattice is controlled entirely by the divisor lattice of:

$$
n.
$$

---

### Example: $\mathbb F_{2^{12}}$

The divisors of $12$ are:

$$
1,2,3,4,6,12.
$$

Therefore the subfields are exactly:

$$
\mathbb F_2,
$$

$$
\mathbb F_{2^2},
$$

$$
\mathbb F_{2^3},
$$

$$
\mathbb F_{2^4},
$$

$$
\mathbb F_{2^6},
$$

and:

$$
\mathbb F_{2^{12}}.
$$

There is no subfield:

$$
\mathbb F_{2^5},
$$

because:

$$
5\nmid12.
$$

---

### Fixed-point description

The unique subfield:

$$
\mathbb F_{p^d}
$$

inside:

$$
\mathbb F_{p^n}
$$

for $d\mid n$ can be characterized as:

$$
\boxed{
\mathbb F_{p^d}
=
\{
x\in\mathbb F_{p^n}:
x^{p^d}=x
\}.
}
$$

These are exactly the roots in $\mathbb F_{p^n}$ of:

$$
x^{p^d}-x.
$$

---

### Frobenius fixed fields

Let:

$$
\varphi_p(x)=x^p.
$$

Then:

$$
\varphi_p^d(x)
=
x^{p^d}.
$$

So:

$$
\boxed{
\mathbb F_{p^d}
=
\operatorname{Fix}(\varphi_p^d)
}
$$

when:

$$
d\mid n.
$$

More generally:

$$
\boxed{
\operatorname{Fix}(\varphi_p^k)
=
\mathbb F_{p^{\gcd(n,k)}}.
}
$$

This gives an explicit form of the Galois correspondence.

---

### Galois correspondence

The full Galois group is:

$$
\operatorname{Gal}
(
\mathbb F_{p^n}/\mathbb F_p
)
=
\langle\varphi_p\rangle
$$

with order:

$$
n.
$$

For each divisor:

$$
d\mid n,
$$

the subgroup:

$$
\langle
\varphi_p^d
\rangle
$$

has order:

$$
\frac nd.
$$

Its fixed field is:

$$
\boxed{
\mathbb F_{p^d}.
}
$$

Thus:

$$
\boxed{
\text{subgroups of the Galois group}
\longleftrightarrow
\text{subfields}.
}
$$

Since the Galois group is cyclic, the correspondence is particularly transparent.

---

## Perfectness and separability

Every finite field is **perfect**.

This means every irreducible polynomial over a finite field is separable.

Equivalently, every finite algebraic extension is separable.

---

### Frobenius proof

Let:

$$
F
$$

be a finite field of characteristic $p$.

Consider:

$$
\varphi_p(x)=x^p.
$$

As before, Frobenius is injective.

Because $F$ is finite, it is therefore surjective.

Hence every:

$$
a\in F
$$

can be written as:

$$
a=b^p
$$

for some:

$$
b\in F.
$$

This surjectivity prevents the purely inseparable phenomenon that can arise in infinite fields of characteristic $p$.

Therefore:

$$
\boxed{
\text{every finite field is perfect}.
}
$$

---

### Why separability matters

Suppose:

$$
f(x)\in\mathbb F_q[x]
$$

is irreducible.

Since the field is perfect, all roots of $f$ in a splitting field are distinct.

If:

$$
\alpha
$$

is one root, then its conjugates are:

$$
\alpha,
\alpha^q,
\ldots,
\alpha^{q^{d-1}},
$$

where:

$$
d=\deg f.
$$

These are distinct.

Therefore:

$$
\boxed{
f(x)
=
\prod_{i=0}^{d-1}
\left(
x-\alpha^{q^i}
\right)
}
$$

inside:

$$
\mathbb F_{q^d}[x].
$$

So the Frobenius description of conjugates works cleanly precisely because finite fields are perfect.

---

## Why these maps matter computationally

Frobenius, trace, norm, and subfields are structural objects, but they are also computational tools.

### Frobenius powers

In a polynomial-basis representation:

$$
\mathbb F_{p^n}
=
\mathbb F_p[x]/(f),
$$

computing:

$$
a^p
$$

or:

$$
a^q
$$

may be substantially cheaper than arbitrary exponentiation, depending on the representation.

In normal bases, Frobenius can become especially simple: it acts as a cyclic shift of coordinates.

This is one reason normal bases are useful in hardware and finite-field implementations.

---

### Trace

Trace maps appear naturally in additive characters.

For example, for:

$$
\mathbb F_{p^n}/\mathbb F_p,
$$

the **absolute trace** is:

$$
\boxed{
\operatorname{Tr}(x)
=
x+x^p+\cdots+x^{p^{n-1}}.
}
$$

It maps into:

$$
\mathbb F_p.
$$

An additive character can then be defined by:

$$
\chi(x)
=
\exp
\left(
\frac{2\pi i}{p}
\operatorname{Tr}(x)
\right).
$$

Such characters appear in:

- Gauss sums,
- exponential sums,
- coding theory,
- finite-field Fourier analysis,
- pairing theory.

---

### Norm

The norm compresses multiplicative information from an extension field into its base field.

For:

$$
x\neq0,
$$

$$
N(x)
=
x^{(q^n-1)/(q-1)}.
$$

This connects multiplicative groups across extensions and appears naturally in:

- field-theoretic constructions,
- multiplicative character theory,
- algebraic number theory,
- some pairing and torus-based constructions.

---

### Subfield testing

To determine whether:

$$
x\in\mathbb F_{p^n}
$$

lies in the subfield:

$$
\mathbb F_{p^d},
$$

for:

$$
d\mid n,
$$

it is enough to test:

$$
\boxed{
x^{p^d}=x.
}
$$

This gives an efficient algebraic membership condition.

---

### Minimal polynomials

Given:

$$
\alpha\in\mathbb F_{q^n},
$$

we can repeatedly compute:

$$
\alpha,
\alpha^q,
\alpha^{q^2},
\ldots
$$

until the orbit closes.

If the orbit length is $d$, then:

$$
\boxed{
m_\alpha(X)
=
\prod_{i=0}^{d-1}
(
X-\alpha^{q^i}
).
}
$$

Thus Frobenius provides a direct algorithmic route from a field element to its minimal polynomial over the base field.

---

## A concrete example: $\mathbb F_4/\mathbb F_2$

Let:

$$
\mathbb F_4
=
\mathbb F_2(\alpha)
$$

where:

$$
\alpha^2+\alpha+1=0.
$$

Thus:

$$
\alpha^2=\alpha+1.
$$

The field elements are:

$$
0,
\quad
1,
\quad
\alpha,
\quad
\alpha+1.
$$

The Frobenius map is:

$$
\varphi_2(x)=x^2.
$$

We obtain:

$$
0^2=0,
$$

$$
1^2=1,
$$

$$
\alpha^2=\alpha+1,
$$

and:

$$
(\alpha+1)^2
=
\alpha^2+1
=
\alpha.
$$

So Frobenius exchanges:

$$
\alpha
\leftrightarrow
\alpha+1.
$$

Therefore:

$$
\operatorname{Gal}
(
\mathbb F_4/\mathbb F_2
)
=
\{
\operatorname{id},
\varphi_2
\}.
$$

---

### Trace in $\mathbb F_4/\mathbb F_2$

Since the degree is $2$:

$$
\operatorname{Tr}(x)
=
x+x^2.
$$

For:

$$
x=\alpha,
$$

$$
\operatorname{Tr}(\alpha)
=
\alpha+\alpha^2.
$$

Using:

$$
\alpha^2=\alpha+1,
$$

we obtain:

$$
\operatorname{Tr}(\alpha)
=
1.
$$

Similarly:

$$
\operatorname{Tr}(1)
=
1+1
=
0.
$$

Thus the trace map is not simply "multiply by the extension degree" on arbitrary extension elements.

That formula applies only to elements already lying in the base field.

---

### Norm in $\mathbb F_4/\mathbb F_2$

The norm is:

$$
N(x)=x^{1+2}=x^3.
$$

For every nonzero:

$$
x\in\mathbb F_4,
$$

we know:

$$
x^3=1.
$$

Therefore:

$$
\boxed{
N(x)=1
\qquad
\forall x\in\mathbb F_4^\times.
}
$$

This is expected because:

$$
\mathbb F_2^\times
=
\{1\}.
$$

---

## The structural picture

For:

$$
\mathbb F_{q^n}/\mathbb F_q,
$$

the entire article can be organized around:

$$
\boxed{
\varphi_q(x)=x^q.
}
$$

Its powers give:

$$
\operatorname{Gal}
(
\mathbb F_{q^n}/\mathbb F_q
)
=
\langle\varphi_q\rangle.
$$

The orbit of an element gives its conjugates:

$$
x,
x^q,
x^{q^2},
\ldots.
$$

Their sum gives:

$$
\boxed{
\operatorname{Tr}(x).
}
$$

Their product gives:

$$
\boxed{
N(x).
}
$$

Fixed points of suitable Frobenius powers give subfields:

$$
\boxed{
\operatorname{Fix}
(
\varphi_p^d
)
=
\mathbb F_{p^d}
}
$$

for:

$$
d\mid n.
$$

So one map controls:

$$
\boxed{
\text{automorphisms},
\quad
\text{conjugates},
\quad
\text{trace},
\quad
\text{norm},
\quad
\text{subfields}.
}
$$

That is the exceptional structural rigidity of finite fields.

---

## Practice and checkpoint

### Exercise 1 — Frobenius

Let:

$$
F=\mathbb F_{3^2}.
$$

What is the Frobenius automorphism over:

$$
\mathbb F_3?
$$

How many times must it be applied before returning to the identity?

---

### Exercise 2 — Galois group

Determine:

$$
\operatorname{Gal}
(
\mathbb F_{5^6}/\mathbb F_5
).
$$

What is its order?

Which element generates it?

---

### Exercise 3 — Relative Frobenius

Consider:

$$
\mathbb F_{2^{12}}/\mathbb F_{2^3}.
$$

What is the appropriate relative Frobenius map?

What is the extension degree?

What is the order of its Galois group?

---

### Exercise 4 — Trace

For:

$$
x\in\mathbb F_{q^3},
$$

write explicitly:

$$
\operatorname{Tr}_{q^3/q}(x).
$$

Verify directly that:

$$
\operatorname{Tr}(x)^q
=
\operatorname{Tr}(x).
$$

---

### Exercise 5 — Norm

For:

$$
x\in\mathbb F_{q^4},
$$

show that:

$$
N_{q^4/q}(x)
=
x^{1+q+q^2+q^3}.
$$

Rewrite the exponent as:

$$
\frac{q^4-1}{q-1}.
$$

---

### Exercise 6 — Trace kernel

How many elements of:

$$
\mathbb F_{q^n}
$$

have trace zero down to:

$$
\mathbb F_q?
$$

Explain the answer using linear algebra.

---

### Exercise 7 — Norm kernel

How many nonzero elements satisfy:

$$
N_{q^n/q}(x)=1?
$$

Explain using the First Isomorphism Theorem for groups.

---

### Exercise 8 — Subfields

List all subfields of:

$$
\mathbb F_{3^{12}}.
$$

Which extension degrees occur?

---

### Exercise 9 — Fixed points

Inside:

$$
\mathbb F_{2^6},
$$

solve conceptually:

$$
x^{2^2}=x.
$$

Which subfield is this solution set?

How many elements does it contain?

---

### Exercise 10 — Frobenius orbit

Suppose:

$$
\alpha\in\mathbb F_{2^{12}}
$$

has Frobenius orbit of size:

$$
4
$$

over:

$$
\mathbb F_2.
$$

What is the degree of its minimal polynomial over:

$$
\mathbb F_2?
$$

Which smallest subfield contains $\alpha$?

---

### Reader checkpoint

You should now be able to explain:

1. Why:
   $$
   x\mapsto x^q
   $$
   is an automorphism of:
   $$
   \mathbb F_{q^n}/\mathbb F_q.
   $$
2. Why:
   $$
   \varphi_q^n=\operatorname{id}.
   $$
3. Why:
   $$
   \operatorname{Gal}
   (
   \mathbb F_{q^n}/\mathbb F_q
   )
   \cong
   \mathbb Z/n\mathbb Z.
   $$
4. What Frobenius conjugates are.
5. Why the orbit size of an element equals the degree of its minimal polynomial over the base field.
6. How:
   $$
   \operatorname{Tr}(x)
   $$
   is computed.
7. Why trace lies in the base field.
8. Why trace is:
   $$
   \mathbb F_q\text{-linear}.
   $$
9. Why the finite-field trace is surjective.
10. Why:
    $$
    |\ker\operatorname{Tr}|
    =
    q^{n-1}.
    $$
11. How:
    $$
    N(x)
    $$
    is computed.
12. Why norm is multiplicative.
13. Why:
    $$
    N(x)
    =
    x^{(q^n-1)/(q-1)}.
    $$
14. Why the norm map is surjective on nonzero elements.
15. Why:
    $$
    |\ker N|
    =
    \frac{q^n-1}{q-1}.
    $$
16. Why:
    $$
    \mathbb F_{p^d}
    \subseteq
    \mathbb F_{p^n}
    \iff
    d\mid n.
    $$
17. Why there is a unique subfield for every divisor $d\mid n$.
18. How subfields arise as fixed fields of Frobenius powers.
19. Why every finite field is perfect.
20. Why trace and norm are compatible with towers of finite extensions.

If these ideas are clear, then finite-field extensions no longer look like arbitrary quotient constructions.

Their internal symmetries, subfields, additive structure, and multiplicative structure are all controlled by Frobenius.

---

## References and further reading

**Rudolf Lidl and Harald Niederreiter**,  
*Finite Fields.*

The standard comprehensive reference for Frobenius automorphisms, traces, norms, subfields, and finite-field extensions.

**Steven Roman**,  
*Field Theory.*

A useful reference for field extensions, traces, norms, separability, and Galois theory.

**David S. Dummit and Richard M. Foote**,  
*Abstract Algebra.*

Provides the general field-theoretic and Galois-theoretic framework behind these finite-field results.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Especially useful for computational finite-field representations and algorithms.

**Joachim von zur Gathen and Jürgen Gerhard**,  
*Modern Computer Algebra.*

A major reference for efficient finite-field and polynomial computation.

---

## Next

Part I showed how to construct:

$$
\boxed{
\mathbb F_{p^n}.
}
$$

Part II has now exposed the internal structure of finite extensions through:

$$
\boxed{
x\mapsto x^q.
}
$$

We can now move from structure to algorithms.

The next questions are computational:

$$
\text{How do we test irreducibility efficiently?}
$$

$$
\text{How do we factor polynomials over }\mathbb F_q?
$$

$$
\text{How do Frobenius powers help us separate irreducible factors?}
$$

Those questions lead directly to finite-field polynomial factorization and the algorithms built around the arithmetic developed so far.
