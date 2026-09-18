---
title: "Abstract Algebra IV: Fields, Algebraic Extensions, Splitting Fields, and Automorphisms"
description: "A rigorous path from fields to algebraic elements, finite extensions, splitting fields, algebraic closure, automorphisms, separability, and perfect fields."
pubDate: "2025-03-19"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Abstract Algebra"
  - "Finite Fields"
tags:
  - "fields"
  - "field-extensions"
  - "algebraic-elements"
  - "splitting-fields"
  - "automorphisms"
  - "perfect-fields"
difficulty: "Intermediate"
status: "Reference"
series: "Abstract Algebra Foundations"
seriesOrder: 4
sourcePath: "experiments/mathematics/abstract-algebra"
draft: false
---

Fields are the setting in which addition, subtraction, multiplication, and division by nonzero elements are all available.

They are therefore the natural algebraic environment for:

- linear algebra,
- polynomial equations,
- finite-field arithmetic,
- elliptic curves,
- coding theory,
- and many cryptographic constructions.

But the real power of field theory appears when one field is enlarged.

A polynomial may fail to have a root in \(F\), yet acquire one in a larger field \(E\).

That immediately leads to the central questions of this article:

> How do we enlarge a field in a controlled way?

> How large is the resulting extension?

> When does a polynomial split completely?

> Which symmetries of the enlarged field preserve the original field?

These questions lead naturally to:

\[
\boxed{
\text{field extensions}
\rightarrow
\text{algebraic elements}
\rightarrow
\text{minimal polynomials}
\rightarrow
\text{splitting fields}
\rightarrow
\text{automorphisms}.
}
\]

---

## 1. Fields and field extensions

A **field** \(F\) is a commutative ring with:

\[
1\neq0
\]

such that every nonzero element has a multiplicative inverse.

Equivalently,

\[
(F,+)
\]

is an abelian group, and:

\[
(F^\times,\cdot)
\]

is also an abelian group, where:

\[
F^\times
=
F\setminus\{0\}.
\]

Standard examples include:

\[
\mathbb Q,
\qquad
\mathbb R,
\qquad
\mathbb C,
\qquad
\mathbb F_p
\]

for prime \(p\).

Unlike a general ring, a field has no nonzero zero divisors.

Indeed, if:

\[
ab=0
\]

and:

\[
a\neq0,
\]

then multiplying by \(a^{-1}\) gives:

\[
b=0.
\]

Thus every field is an integral domain.

---

### Extension fields

Suppose:

\[
F\subseteq E
\]

and the addition and multiplication of \(F\) agree with those inherited from \(E\).

Then \(E\) is an **extension field** of \(F\), and we write:

\[
\boxed{
E/F.
}
\]

The important observation is that \(E\) is automatically a vector space over \(F\).

The dimension of that vector space is called the **degree of the extension**:

\[
\boxed{
[E:F]
=
\dim_F E.
}
\]

If:

\[
[E:F]<\infty,
\]

we call \(E/F\) a **finite extension**.

---

### Example: \(\mathbb Q(\sqrt2)\)

Consider:

\[
\mathbb Q(\sqrt2)
=
\{
a+b\sqrt2:
a,b\in\mathbb Q
\}.
\]

Every element can be written uniquely as:

\[
a\cdot1+b\cdot\sqrt2.
\]

Thus:

\[
\{1,\sqrt2\}
\]

is a basis over \(\mathbb Q\).

Therefore:

\[
\boxed{
[\mathbb Q(\sqrt2):\mathbb Q]
=
2.
}
\]

This is our first example of creating a larger field by adjoining a new algebraic element.

---

## 2. Algebraic elements and minimal polynomials

Let:

\[
E/F
\]

be a field extension and let:

\[
\alpha\in E.
\]

The element \(\alpha\) is **algebraic over \(F\)** if there exists a nonzero polynomial:

\[
f(x)\in F[x]
\]

such that:

\[
\boxed{
f(\alpha)=0.
}
\]

If no such polynomial exists, then \(\alpha\) is called **transcendental over \(F\)**.

For example:

\[
\sqrt2
\]

is algebraic over \(\mathbb Q\) because:

\[
x^2-2
\]

vanishes at \(\sqrt2\).

By contrast, numbers such as:

\[
\pi
\]

and:

\[
e
\]

are transcendental over \(\mathbb Q\).

---

### Minimal polynomial

Suppose \(\alpha\) is algebraic over \(F\).

Among all nonzero polynomials in \(F[x]\) satisfying:

\[
f(\alpha)=0,
\]

there is a unique monic irreducible polynomial of smallest degree.

This is the **minimal polynomial** of \(\alpha\) over \(F\):

\[
\boxed{
m_{\alpha,F}(x).
}
\]

When the base field is clear, we often write simply:

\[
m_\alpha(x).
\]

For:

\[
\alpha=\sqrt2
\]

over \(\mathbb Q\),

\[
\boxed{
m_\alpha(x)
=
x^2-2.
}
\]

---

### Why irreducibility matters

Suppose the minimal polynomial factored:

\[
m_\alpha(x)
=
g(x)h(x)
\]

with both \(g\) and \(h\) of smaller positive degree.

Then:

\[
0
=
m_\alpha(\alpha)
=
g(\alpha)h(\alpha).
\]

Because \(E\) is a field and therefore has no zero divisors:

\[
g(\alpha)=0
\]

or:

\[
h(\alpha)=0.
\]

But then a polynomial of smaller degree would vanish at \(\alpha\), contradicting minimality.

Therefore the minimal polynomial must be irreducible.

---

## 3. Simple extensions and the quotient construction

The smallest field containing \(F\) and an element \(\alpha\) is written:

\[
\boxed{
F(\alpha).
}
\]

This is called a **simple extension**.

If \(\alpha\) is algebraic over \(F\), then one of the most important results in elementary field theory is:

\[
\boxed{
F(\alpha)
\cong
F[x]/(m_\alpha(x)).
}
\]

This connects field extensions directly to the quotient-ring machinery developed in the previous article.

---

### Why the quotient appears

Consider the evaluation homomorphism:

\[
\operatorname{ev}_\alpha:
F[x]
\rightarrow
E
\]

defined by:

\[
f(x)
\longmapsto
f(\alpha).
\]

Its image is:

\[
F[\alpha].
\]

When \(\alpha\) is algebraic over \(F\),

\[
F[\alpha]=F(\alpha).
\]

Its kernel consists of all polynomials that vanish at \(\alpha\).

Since the minimal polynomial generates this kernel:

\[
\ker(\operatorname{ev}_\alpha)
=
(m_\alpha(x)).
\]

The First Isomorphism Theorem for rings gives:

\[
\boxed{
F[x]/(m_\alpha)
\cong
F(\alpha).
}
\]

So adjoining an algebraic element is literally a quotient-ring construction.

---

### Degree of a simple algebraic extension

If:

\[
\deg m_\alpha=d,
\]

then every element of \(F(\alpha)\) has a unique representation:

\[
a_0
+
a_1\alpha
+
\cdots
+
a_{d-1}\alpha^{d-1},
\]

with:

\[
a_i\in F.
\]

Therefore:

\[
\boxed{
[F(\alpha):F]
=
\deg m_\alpha.
}
\]

For:

\[
\alpha=\sqrt2,
\]

we have:

\[
\deg(x^2-2)=2,
\]

hence:

\[
[\mathbb Q(\sqrt2):\mathbb Q]=2.
\]

---

### Finite extensions are algebraic

If:

\[
[E:F]<\infty,
\]

then every:

\[
\alpha\in E
\]

is algebraic over \(F\).

To see why, suppose:

\[
[E:F]=n.
\]

Then the \(n+1\) elements:

\[
1,
\alpha,
\alpha^2,
\ldots,
\alpha^n
\]

belong to an \(n\)-dimensional vector space over \(F\).

Therefore they are linearly dependent.

So there exist coefficients:

\[
a_0,\ldots,a_n\in F,
\]

not all zero, such that:

\[
a_0
+
a_1\alpha
+
\cdots
+
a_n\alpha^n
=
0.
\]

Thus \(\alpha\) satisfies a nonzero polynomial over \(F\).

Therefore:

\[
\boxed{
\text{finite extension}
\Longrightarrow
\text{algebraic extension}.
}
\]

The converse is false.

An algebraic extension may have infinite degree.

---

## 4. Towers of fields

Suppose:

\[
K\subseteq F\subseteq E.
\]

Then \(E\) is an extension of \(F\), and \(F\) is an extension of \(K\).

If the relevant dimensions are finite, the **Tower Law** states:

\[
\boxed{
[E:K]
=
[E:F][F:K].
}
\]

This is simply the multiplicativity of vector-space dimensions across successive field extensions.

---

### Example

Consider:

\[
\mathbb Q
\subseteq
\mathbb Q(\sqrt2)
\subseteq
\mathbb Q(\sqrt2,\sqrt3).
\]

We know:

\[
[\mathbb Q(\sqrt2):\mathbb Q]
=
2.
\]

Also:

\[
\sqrt3
\notin
\mathbb Q(\sqrt2),
\]

so adjoining \(\sqrt3\) gives another degree-\(2\) extension:

\[
[
\mathbb Q(\sqrt2,\sqrt3)
:
\mathbb Q(\sqrt2)
]
=
2.
\]

Therefore:

\[
\boxed{
[
\mathbb Q(\sqrt2,\sqrt3)
:
\mathbb Q
]
=
4.
}
\]

A basis is:

\[
\{
1,
\sqrt2,
\sqrt3,
\sqrt6
\}.
\]

The Tower Law is one of the fundamental tools for controlling the size of more complicated extensions.

---

## 5. Splitting fields and algebraic closure

Suppose:

\[
f(x)\in F[x].
\]

A field \(E\supseteq F\) is a **splitting field** of \(f\) over \(F\) if:

1. \(f\) factors completely into linear factors in \(E[x]\);
2. \(E\) is generated over \(F\) by the roots of \(f\).

So if:

\[
f(x)
=
c
(x-\alpha_1)
\cdots
(x-\alpha_n)
\]

inside \(E[x]\), then:

\[
E
=
F(\alpha_1,\ldots,\alpha_n).
\]

The second condition ensures that the extension contains nothing unnecessary.

---

### One root is not always enough

Consider:

\[
f(x)
=
x^2-2.
\]

Its roots are:

\[
\pm\sqrt2.
\]

Once we adjoin:

\[
\sqrt2,
\]

we automatically obtain:

\[
-\sqrt2.
\]

Therefore:

\[
\boxed{
\mathbb Q(\sqrt2)
}
\]

is the splitting field of \(x^2-2\) over \(\mathbb Q\).

---

Now consider:

\[
f(x)
=
x^3-2.
\]

One root is:

\[
\alpha
=
\sqrt[3]{2}.
\]

But the other roots are:

\[
\omega\alpha
\]

and:

\[
\omega^2\alpha,
\]

where:

\[
\omega
=
e^{2\pi i/3}
\]

satisfies:

\[
\omega^2+\omega+1=0.
\]

The field:

\[
\mathbb Q(\sqrt[3]2)
\]

contains the real cube root but not the nonreal roots.

Therefore it is **not** the splitting field.

We need:

\[
\boxed{
\mathbb Q(\sqrt[3]2,\omega).
}
\]

This distinction is fundamental:

\[
\boxed{
\text{contains a root}
\neq
\text{contains all roots}.
}
\]

---

### Algebraically closed fields

A field \(F\) is **algebraically closed** if every nonconstant polynomial:

\[
f(x)\in F[x]
\]

has a root in \(F\).

Equivalently, every nonconstant polynomial splits completely into linear factors over \(F\).

The most familiar example is:

\[
\boxed{
\mathbb C.
}
\]

The Fundamental Theorem of Algebra states that every nonconstant polynomial over \(\mathbb C\) has a complex root.

Thus:

\[
\mathbb C
\]

is algebraically closed.

---

### Algebraic closure

An **algebraic closure** of \(F\) is an algebraic extension:

\[
\overline F/F
\]

such that:

\[
\overline F
\]

is algebraically closed.

For example:

\[
\boxed{
\overline{\mathbb R}
=
\mathbb C.
}
\]

More precisely, \(\mathbb C\) is an algebraic closure of \(\mathbb R\).

An algebraic closure exists for every field and is unique up to an isomorphism that fixes the base field \(F\).

But it is not canonically unique as a concrete set.

---

## 6. Field automorphisms and the beginning of Galois theory

Let:

\[
E/F
\]

be a field extension.

An **automorphism** of \(E\) is a bijective field homomorphism:

\[
\sigma:E\rightarrow E.
\]

If:

\[
\sigma(a)=a
\]

for every:

\[
a\in F,
\]

then we say that \(\sigma\) **fixes \(F\) pointwise**.

The set of all such automorphisms is:

\[
\boxed{
\operatorname{Aut}(E/F).
}
\]

Under composition, this set forms a group.

This is the first appearance of the basic object that later becomes the **Galois group**.

---

### Example: \(\mathbb Q(\sqrt2)/\mathbb Q\)

Every automorphism fixing \(\mathbb Q\) must send:

\[
\sqrt2
\]

to another root of its minimal polynomial:

\[
x^2-2.
\]

Therefore:

\[
\sqrt2
\mapsto
\sqrt2
\]

or:

\[
\sqrt2
\mapsto
-\sqrt2.
\]

This gives two automorphisms.

The identity:

\[
\sigma_1(a+b\sqrt2)
=
a+b\sqrt2,
\]

and conjugation:

\[
\sigma_2(a+b\sqrt2)
=
a-b\sqrt2.
\]

Thus:

\[
\boxed{
|\operatorname{Aut}(
\mathbb Q(\sqrt2)/\mathbb Q
)|
=
2.
}
\]

The two automorphisms form a group isomorphic to:

\[
\mathbb Z_2.
\]

---

### Why roots determine automorphisms

Suppose:

\[
E=F(\alpha)
\]

and \(\sigma\) fixes \(F\).

If:

\[
m_\alpha(\alpha)=0,
\]

then:

\[
\sigma(
m_\alpha(\alpha)
)
=
0.
\]

Because \(\sigma\) fixes the coefficients of \(m_\alpha\):

\[
m_\alpha(
\sigma(\alpha)
)
=
0.
\]

Therefore:

\[
\boxed{
\sigma(\alpha)
}
\]

must also be a root of the minimal polynomial of \(\alpha\).

This is the fundamental connection between:

\[
\text{field automorphisms}
\]

and:

\[
\text{permutations of polynomial roots}.
\]

It is the idea from which Galois theory develops.

---

## 7. Separability and perfect fields

A polynomial:

\[
f(x)\in F[x]
\]

is **separable** if it has no repeated roots in a splitting field.

For an irreducible polynomial, this means all of its roots are distinct.

Repeated roots are detected by the derivative.

A polynomial \(f\) has a repeated root precisely when:

\[
f
\]

and:

\[
f'
\]

have a nontrivial common factor.

For an irreducible polynomial, inseparability can therefore occur only when:

\[
f'(x)=0.
\]

---

### Characteristic zero

If:

\[
\operatorname{char}(F)=0,
\]

an irreducible nonconstant polynomial cannot have zero derivative.

Therefore every irreducible polynomial over \(F\) is separable.

Hence:

\[
\boxed{
\text{every field of characteristic }0
\text{ is perfect}.
}
\]

In particular:

\[
\mathbb Q,
\qquad
\mathbb R,
\qquad
\mathbb C
\]

are perfect.

---

### Characteristic \(p\)

In characteristic \(p\), something special can happen.

For example:

\[
\frac{d}{dx}
x^p
=
px^{p-1}
=
0.
\]

More generally:

\[
f'(x)=0
\]

in characteristic \(p\) precisely when all nonzero exponents appearing in \(f\) are divisible by \(p\).

Such polynomials are related to expressions of the form:

\[
g(x^p).
\]

This is the source of inseparability phenomena.

---

### Perfect fields

A field \(F\) is **perfect** if every irreducible polynomial over \(F\) is separable.

Equivalently, every algebraic extension of \(F\) is separable.

Thus:

\[
\boxed{
\operatorname{char}(F)=0
\Longrightarrow
F\text{ perfect}.
}
\]

And an especially important result is:

\[
\boxed{
\text{every finite field is perfect}.
}
\]

---

### Why finite fields are perfect

Let:

\[
F
\]

be a finite field of characteristic \(p\).

Consider the Frobenius map:

\[
\boxed{
\operatorname{Fr}:F\rightarrow F,
\qquad
x\mapsto x^p.
}
\]

In characteristic \(p\):

\[
(a+b)^p
=
a^p+b^p,
\]

so Frobenius is a field homomorphism.

It is injective because:

\[
x^p=y^p
\]

implies:

\[
(x-y)^p=0,
\]

hence:

\[
x=y.
\]

But an injective map from a finite set to itself is automatically surjective.

Therefore Frobenius is an automorphism.

So every element of \(F\) has a \(p\)-th root inside \(F\), preventing the inseparability obstruction that can occur in general characteristic-\(p\) fields.

Hence every finite field is perfect.

---

## 8. Finite fields and cryptographic relevance

Field theory becomes concrete very quickly in cryptography.

### Prime fields

For prime \(p\):

\[
\boxed{
\mathbb F_p
=
\mathbb Z/p\mathbb Z.
}
\]

This is the basic field used in many discrete-logarithm and elliptic-curve constructions.

---

### Extension fields

If:

\[
f(x)\in\mathbb F_p[x]
\]

is irreducible of degree \(m\), then:

\[
\boxed{
\mathbb F_p[x]/(f(x))
}
\]

is a field with:

\[
p^m
\]

elements.

Thus:

\[
\boxed{
\mathbb F_{p^m}
\cong
\mathbb F_p[x]/(f(x)).
}
\]

This connects:

\[
\text{irreducible polynomials}
\]

with:

\[
\text{finite-field construction}.
\]

---

### Example: \(\mathbb F_4\)

Take:

\[
f(x)
=
x^2+x+1
\]

over:

\[
\mathbb F_2.
\]

Since \(f\) has no root in \(\mathbb F_2\), it is irreducible.

Therefore:

\[
\mathbb F_2[x]/(x^2+x+1)
\]

is a field with:

\[
2^2=4
\]

elements.

If \(\alpha\) denotes the coset of \(x\), then:

\[
\alpha^2+\alpha+1=0.
\]

Hence:

\[
\boxed{
\alpha^2=\alpha+1.
}
\]

The field elements are:

\[
0,
\quad
1,
\quad
\alpha,
\quad
\alpha+1.
\]

This is the same quotient-field construction from Part III, now interpreted as a genuine field extension:

\[
\boxed{
[\mathbb F_4:\mathbb F_2]=2.
}
\]

---

### Frobenius in finite fields

For:

\[
\mathbb F_{p^m},
\]

the Frobenius automorphism is:

\[
\boxed{
x\mapsto x^p.
}
\]

Repeated application gives:

\[
x,
\quad
x^p,
\quad
x^{p^2},
\quad
\ldots
\]

and eventually:

\[
x^{p^m}=x.
\]

This automorphism is one of the most important structural maps in finite-field theory.

It appears in:

- finite-field arithmetic,
- irreducibility theory,
- field embeddings,
- trace and norm maps,
- elliptic curves,
- pairing-based cryptography.

We will not develop those constructions fully here, but this is the algebraic structure from which they arise.

---

## The structural picture

The main ideas of the article fit into one chain.

Start with a field:

\[
F.
\]

Adjoin an algebraic element:

\[
\alpha.
\]

Its behavior is controlled by:

\[
m_\alpha(x).
\]

Then:

\[
\boxed{
F(\alpha)
\cong
F[x]/(m_\alpha).
}
\]

The degree is:

\[
\boxed{
[F(\alpha):F]
=
\deg m_\alpha.
}
\]

Adjoin enough roots of a polynomial and we obtain its splitting field:

\[
E.
\]

Then study the symmetries preserving \(F\):

\[
\boxed{
\operatorname{Aut}(E/F).
}
\]

Thus:

\[
\boxed{
\text{polynomials}
\rightarrow
\text{roots}
\rightarrow
\text{extensions}
\rightarrow
\text{automorphisms}.
}
\]

That is the conceptual bridge from elementary field theory to Galois theory.

---

## Practice and checkpoint

### Exercise 1 — Extension degree

Show that:

\[
\mathbb Q(\sqrt5)
=
\{
a+b\sqrt5:
a,b\in\mathbb Q
\}.
\]

Find a basis over:

\[
\mathbb Q.
\]

Determine:

\[
[\mathbb Q(\sqrt5):\mathbb Q].
\]

---

### Exercise 2 — Minimal polynomial

Find the minimal polynomial over \(\mathbb Q\) of:

\[
\sqrt3.
\]

What about:

\[
1+\sqrt3?
\]

---

### Exercise 3 — Quotient construction

Let:

\[
\alpha^2=2.
\]

Show explicitly why:

\[
\mathbb Q[x]/(x^2-2)
\cong
\mathbb Q(\sqrt2).
\]

What does the coset of \(x\) correspond to?

---

### Exercise 4 — Tower Law

Given:

\[
\mathbb Q
\subseteq
\mathbb Q(\sqrt2)
\subseteq
\mathbb Q(\sqrt2,\sqrt3),
\]

compute all three extension degrees and verify:

\[
[E:K]
=
[E:F][F:K].
\]

---

### Exercise 5 — Splitting field

Determine the splitting field over \(\mathbb Q\) of:

\[
x^2+1.
\]

Now compare it with:

\[
x^3-2.
\]

Why is adjoining one real root sufficient in the first relevant quadratic examples but not for \(x^3-2\)?

---

### Exercise 6 — Automorphisms

List all automorphisms of:

\[
\mathbb Q(\sqrt5)
\]

that fix \(\mathbb Q\).

What can happen to \(\sqrt5\)?

---

### Exercise 7 — Finite field

Show that:

\[
x^2+x+1
\]

is irreducible over:

\[
\mathbb F_2.
\]

Construct:

\[
\mathbb F_4
=
\mathbb F_2[x]/(x^2+x+1).
\]

Compute:

\[
\alpha^2,
\qquad
\alpha^3.
\]

---

### Exercise 8 — Frobenius

Inside:

\[
\mathbb F_4,
\]

compute:

\[
x\mapsto x^2
\]

for every element.

Verify that this map permutes the field elements and fixes:

\[
\mathbb F_2.
\]

---

### Reader checkpoint

You should now be able to explain:

1. What makes a commutative ring a field.
2. What a field extension \(E/F\) is.
3. Why \(E\) is a vector space over \(F\).
4. What:
   \[
   [E:F]
   \]
   measures.
5. The difference between algebraic and transcendental elements.
6. What a minimal polynomial is.
7. Why a minimal polynomial is irreducible.
8. Why:
   
   \[
   [F(\alpha):F]
   =
   \deg m_\alpha.
   \]
   
9.  Why:
   \[
   F(\alpha)
   \cong
   F[x]/(m_\alpha).
   \]
10. Why every finite extension is algebraic.
11. What the Tower Law states.
12. The difference between adjoining one root and constructing a splitting field.
13. What an algebraic closure is.
14. What:
   \[
   \operatorname{Aut}(E/F)
   \]
   means.
15. Why an automorphism fixing \(F\) sends an algebraic element to another root of its minimal polynomial.
16. What separability means.
17. What a perfect field is.
18. Why every characteristic-zero field is perfect.
19. Why every finite field is perfect.
20. Why Frobenius is fundamental in finite-field extensions.

At this point, field extensions should no longer look like arbitrary enlargements of a number system.

They are controlled algebraic constructions whose size, roots, and symmetries can be studied systematically.

---

## References and further reading

**David S. Dummit and Richard M. Foote**,  
*Abstract Algebra.*

A comprehensive reference for field extensions, minimal polynomials, splitting fields, separability, and Galois theory.

**Joseph A. Gallian**,  
*Contemporary Abstract Algebra.*

A particularly accessible introduction to field extensions and algebraic elements.

**Michael Artin**,  
*Algebra.*

Provides a structural treatment of fields, extensions, automorphisms, and the transition toward Galois theory.

**Ian Stewart**,  
*Galois Theory.*

A readable introduction to the relationship between polynomial roots, field extensions, and automorphism groups.

**Rudolf Lidl and Harald Niederreiter**,  
*Finite Fields.*

A standard reference for the theory and computation of finite fields.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Especially useful for finite-field arithmetic, irreducible polynomials, extension construction, and computational applications.

---

## Where this leads

We now have a sequence of increasingly rich algebraic structures:

\[
\text{groups}
\rightarrow
\text{rings}
\rightarrow
\text{fields}.
\]

And within field theory we have developed:

\[
F
\subseteq
F(\alpha)
\subseteq
E,
\]

where \(E\) may be a splitting field.

The roots of polynomials are no longer isolated solutions.

They live inside field extensions and may be permuted by automorphisms that preserve the base field.

That is the key observation behind the next major step:

\[
\boxed{
\text{polynomial roots}
\longleftrightarrow
\text{field symmetries}.
}
\]

This correspondence is the starting point of **Galois theory**.