---
title: "Abstract Algebra VI: Modules over Rings — The Bridge from Vector Spaces to Lattices"
description: "Modules generalize vector spaces by allowing scalars from a ring rather than a field, providing the natural language for integer lattices, quotient modules, and polynomial-module constructions."
pubDate: "2025-04-23"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Abstract Algebra"
  - "Linear Algebra"
  - "Lattice Theory"
tags:
  - "modules"
  - "submodules"
  - "module-homomorphisms"
  - "free-modules"
  - "z-modules"
  - "lattices"
difficulty: "Intermediate"
status: "Reference"
series: "Abstract Algebra Foundations"
seriesOrder: 6
sourcePath: "experiments/mathematics/abstract-algebra"
draft: false
---

Vector spaces are built over fields.

That assumption is extremely powerful because every nonzero scalar can be divided by.

But many algebraic objects appearing in number theory and cryptography use scalars from rings rather than fields.

Examples include:

$$
\mathbb Z,
$$

polynomial rings such as:

$$
R[x],
$$

and quotient rings such as:

$$
\mathbb Z_q[x]/(f(x)).
$$

Once the scalars form only a ring, the correct structure is no longer a vector space.

It is a **module**.

Modules retain much of the language of linear algebra:

$$
\text{linear combinations},
\quad
\text{generators},
\quad
\text{kernels},
\quad
\text{images},
\quad
\text{quotients},
$$

but important vector-space properties may disappear.

This makes modules the natural bridge between:

$$
\boxed{
\text{abstract algebra}
\rightarrow
\text{linear algebra}
\rightarrow
\text{integer lattices}
\rightarrow
\text{module-based cryptography}.
}
$$

---

## Table of Contents

- [Modules over rings](#modules-over-rings)
- [Basic examples](#basic-examples)
- [Submodules, quotients, and homomorphisms](#submodules-quotients-and-homomorphisms)
- [Generated and free modules](#generated-and-free-modules)
- [What changes from vector spaces](#what-changes-from-vector-spaces)
- [Finitely generated modules over a PID](#finitely-generated-modules-over-a-pid)
- [7. Lattices as $\mathbb Z$-modules](#7-lattices-as-zmathbb-zz-modules)
- [Polynomial modules and cryptography](#polynomial-modules-and-cryptography)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Where this leaves us](#where-this-leaves-us)

---

## Modules over rings

Let $R$ be a ring with identity.

An **$R$-module** $M$ consists of an abelian group:

$$
(M,+)
$$

together with a scalar multiplication:

$$
R\times M\rightarrow M,
$$

written:

$$
(r,m)\mapsto rm,
$$

such that for all:

$$
r,s\in R
$$

and:

$$
x,y\in M,
$$

we have:

$$
\boxed{
r(x+y)
=
rx+ry,
}
$$

$$
\boxed{
(r+s)x
=
rx+sx,
}
$$

$$
\boxed{
(rs)x
=
r(sx),
}
$$

and:

$$
\boxed{
1_Rx=x.
}
$$

The definition should look almost identical to that of a vector space.

The crucial difference is the scalar set.

For a vector space, scalars come from a field:

$$
F.
$$

For a module, scalars come from a ring:

$$
R.
$$

That change has major consequences.

---

### Left and right modules

If $R$ is not commutative, scalar multiplication may act from the left or from the right.

A left module uses:

$$
R\times M\rightarrow M,
$$

while a right module uses:

$$
M\times R\rightarrow M.
$$

For commutative rings, this distinction is usually unnecessary.

Throughout this article, we mainly work with modules over commutative rings.

---

## Basic examples

Modules occur throughout algebra, often without being explicitly called modules.

### Vector spaces

Every vector space over a field $F$ is automatically an $F$-module.

Thus:

$$
\boxed{
\text{vector spaces are special cases of modules}.
}
$$

The theory of modules therefore genuinely generalizes linear algebra.

---

### Abelian groups as $\mathbb Z$-modules

Every abelian group:

$$
(A,+)
$$

has a natural $\mathbb Z$-module structure.

For:

$$
n\in\mathbb Z
$$

and:

$$
a\in A,
$$

define:

$$
na
$$

by repeated addition.

For positive $n$:

$$
na
=
\underbrace{
a+\cdots+a
}_{n\text{ times}},
$$

while:

$$
(-n)a
=
-(na).
$$

Therefore:

$$
\boxed{
\mathbb Z\text{-modules}
\Longleftrightarrow
\text{abelian groups}.
}
$$

This correspondence is fundamental.

The language of finitely generated abelian groups is therefore a special case of module theory.

---

### $\mathbb Z^n$

The set:

$$
\mathbb Z^n
$$

is a $\mathbb Z$-module under coordinatewise addition and integer scalar multiplication.

Its standard generators are:

$$
e_1,\ldots,e_n.
$$

Every vector:

$$
(z_1,\ldots,z_n)
$$

has the unique representation:

$$
z_1e_1+\cdots+z_ne_n.
$$

Therefore:

$$
\boxed{
\mathbb Z^n
}
$$

is a free $\mathbb Z$-module of rank $n$.

This will become the prototype for lattices.

---

### A ring as a module over itself

Every ring $R$ is naturally an $R$-module:

$$
{}_RR.
$$

Scalar multiplication is simply ring multiplication:

$$
r\cdot x=rx.
$$

Under this viewpoint, the submodules of $R$ are exactly the ideals of $R$ in the commutative setting.

So:

$$
\boxed{
\text{ideals are submodules of }R
\text{ viewed as an }R\text{-module}.
}
$$

This connects the previous ring-theory article directly with module theory.

---

### Polynomial modules

The product:

$$
R[x]^m
$$

is naturally an $R[x]$-module.

For:

$$
f(x)\in R[x]
$$

and:

$$
\mathbf v(x)
=
(v_1(x),\ldots,v_m(x)),
$$

scalar multiplication is:

$$
f(x)\mathbf v(x)
=
(
f(x)v_1(x),
\ldots,
f(x)v_m(x)
).
$$

This type of structure becomes especially important in module-based lattice cryptography.

---

## Submodules, quotients, and homomorphisms

The familiar structural constructions from groups and rings extend naturally to modules.

### Submodules

Let $M$ be an $R$-module.

A subset:

$$
N\subseteq M
$$

is an **$R$-submodule** if:

1. $N$ is an additive subgroup of $M$;
2. for every:
   $$
   r\in R
   $$
   and:
   $$
   n\in N,
   $$
   we have:
   $$
   rn\in N.
   $$

We write:

$$
\boxed{
N\le_R M.
}
$$

A convenient submodule test is:

$$
x,y\in N,
\quad
r\in R
\Longrightarrow
x+ry\in N.
$$

---

### Example

Inside:

$$
\mathbb Z^2,
$$

consider:

$$
N
=
\{
(2a,2b):
a,b\in\mathbb Z
\}.
$$

Then:

$$
N
=
2\mathbb Z\times2\mathbb Z.
$$

It is closed under addition, additive inverses, and multiplication by arbitrary integers.

Therefore:

$$
\boxed{
N\le_{\mathbb Z}\mathbb Z^2.
}
$$

---

### Quotient modules

If:

$$
N\le_R M,
$$

we can form the additive quotient:

$$
\boxed{
M/N.
}
$$

Its elements are cosets:

$$
m+N.
$$

Addition is:

$$
(m+N)+(m'+N)
=
(m+m')+N,
$$

while scalar multiplication is:

$$
\boxed{
r(m+N)
=
rm+N.
}
$$

The submodule condition guarantees that this scalar multiplication is well-defined.

So the quotient philosophy now appears for a third time:

$$
G/N,
\qquad
R/I,
\qquad
M/N.
$$

---

### Module homomorphisms

Let:

$$
M,N
$$

be $R$-modules.

A map:

$$
f:M\rightarrow N
$$

is an **$R$-module homomorphism**, or **$R$-linear map**, if:

$$
\boxed{
f(x+y)
=
f(x)+f(y)
}
$$

and:

$$
\boxed{
f(rx)
=
rf(x)
}
$$

for every:

$$
x,y\in M,
\qquad
r\in R.
$$

This is exactly the familiar definition of linearity from vector spaces, generalized to ring scalars.

---

### Kernel and image

Define:

$$
\ker f
=
\{
m\in M:
f(m)=0
\},
$$

and:

$$
\operatorname{im}f
=
\{
f(m):
m\in M
\}.
$$

Then:

$$
\boxed{
\ker f\le_R M
}
$$

and:

$$
\boxed{
\operatorname{im}f\le_R N.
}
$$

The First Isomorphism Theorem also survives:

$$
\boxed{
M/\ker f
\cong
\operatorname{im}f.
}
$$

So the same structural pattern has now appeared in three settings:

$$
\boxed{
\text{groups},
\quad
\text{rings},
\quad
\text{modules}.
}
$$

---

## Generated and free modules

Let:

$$
M
$$

be an $R$-module.

A set:

$$
S=\{m_1,\ldots,m_k\}
$$

**generates** $M$ if every element:

$$
m\in M
$$

can be written as:

$$
\boxed{
m
=
r_1m_1+\cdots+r_km_k
}
$$

for some:

$$
r_i\in R.
$$

We write:

$$
M
=
\langle
m_1,\ldots,m_k
\rangle_R.
$$

If a finite generating set exists, then $M$ is **finitely generated**.

---

### Free modules

An $R$-module $M$ is **free** if it has a basis:

$$
B=\{b_i\},
$$

meaning every element of $M$ can be expressed **uniquely** as a finite linear combination:

$$
\boxed{
m
=
\sum_i r_ib_i.
}
$$

This looks exactly like a vector-space basis.

For example:

$$
R^n
$$

is free with standard basis:

$$
e_1,\ldots,e_n.
$$

We therefore write:

$$
\boxed{
R^n
\text{ is a free }R\text{-module of rank }n.
}
$$

---

### Rank

For a finite-dimensional vector space, every basis has the same cardinality.

For free modules over many important rings, including integral domains, a corresponding invariant-basis-number property gives a well-defined rank.

Thus if:

$$
M\cong R^n,
$$

we write:

$$
\boxed{
\operatorname{rank}_R(M)=n.
}
$$

For:

$$
\mathbb Z^n,
$$

the rank is simply:

$$
n.
$$

But one must be more cautious with arbitrary modules than with vector spaces.

Not every module even has a basis.

---

## What changes from vector spaces

Modules resemble vector spaces, but several familiar linear-algebra facts no longer hold automatically.

The reason is simple:

$$
\boxed{
\text{nonzero ring elements need not be invertible}.
}
$$

That changes the structure profoundly.

---

### Not every module is free

Consider:

$$
\mathbb Z/n\mathbb Z
$$

as a $\mathbb Z$-module.

Suppose it were free.

A nonzero free $\mathbb Z$-module contains elements of infinite additive order.

But every element of:

$$
\mathbb Z/n\mathbb Z
$$

satisfies:

$$
n[a]=[0].
$$

Therefore:

$$
\boxed{
\mathbb Z/n\mathbb Z
}
$$

is not a free $\mathbb Z$-module for $n>1$.

This already shows a major difference from vector spaces.

---

### Torsion

Let $R$ be an integral domain and $M$ an $R$-module.

A nonzero element:

$$
m\in M
$$

is a **torsion element** if there exists:

$$
0\neq r\in R
$$

such that:

$$
\boxed{
rm=0.
}
$$

For a $\mathbb Z$-module, this means:

$$
nm=0
$$

for some nonzero integer $n$.

For example, every element of:

$$
\mathbb Z/6\mathbb Z
$$

is torsion.

By contrast:

$$
\mathbb Z^n
$$

is torsion-free.

---

### Why vector spaces do not have nonzero torsion

Suppose $V$ is a vector space over a field $F$ and:

$$
av=0
$$

with:

$$
a\neq0.
$$

Since $a$ has an inverse:

$$
a^{-1},
$$

we obtain:

$$
v
=
a^{-1}(av)
=
0.
$$

Therefore no nonzero vector can be annihilated by a nonzero scalar.

This argument fails for modules because $a^{-1}$ may not exist.

That is one of the cleanest ways to see why module theory is genuinely richer than linear algebra.

---

### Linear independence becomes subtler

A collection:

$$
m_1,\ldots,m_k
$$

is linearly independent over $R$ if:

$$
r_1m_1+\cdots+r_km_k=0
$$

implies:

$$
r_1=\cdots=r_k=0.
$$

The definition looks familiar.

But over arbitrary rings, several vector-space theorems about extending independent sets to bases or extracting bases from generating sets may fail.

So the word **basis** must be used more carefully in module theory.

---

## Finitely generated modules over a PID

Module theory becomes especially well behaved over a **principal ideal domain**.

Examples include:

$$
\mathbb Z
$$

and:

$$
F[x]
$$

when $F$ is a field.

A major theorem describes every finitely generated module over a PID.

In broad form, if $R$ is a PID and $M$ is finitely generated, then:

$$
\boxed{
M
\cong
R^r
\oplus
T,
}
$$

where:

$$
R^r
$$

is the free part and:

$$
T
$$

is a finite direct sum of torsion modules.

So a finitely generated module decomposes into:

```text
free structure
      +
torsion structure
```

---

### Specialization to abelian groups

Because:

$$
\mathbb Z\text{-modules}
=
\text{abelian groups},
$$

the theorem gives the structure theorem for finitely generated abelian groups.

Every finitely generated abelian group is isomorphic to:

$$
\boxed{
\mathbb Z^r
\oplus
\mathbb Z/n_1\mathbb Z
\oplus
\cdots
\oplus
\mathbb Z/n_t\mathbb Z
}
$$

with suitable divisibility conditions on the $n_i$.

The component:

$$
\mathbb Z^r
$$

is free.

The finite cyclic components form the torsion part.

This is one of the strongest examples of module theory turning an abstract class of objects into a complete structural classification.

---

### Submodules of free modules over a PID

Another useful fact is:

> Every submodule of a free module over a PID is itself free.

For example, if:

$$
L
\le_{\mathbb Z}
\mathbb Z^n,
$$

then:

$$
L
$$

is a free $\mathbb Z$-module.

This result is one of the algebraic reasons lattice bases exist naturally in integer lattice theory.

---

## 7. Lattices as $\mathbb Z$-modules

A Euclidean lattice provides one of the most important concrete examples of a free module.

Let:

$$
b_1,\ldots,b_m
\in
\mathbb R^n
$$

be linearly independent over $\mathbb R$.

The lattice generated by them is:

$$
\boxed{
L
=
\left\{
z_1b_1+\cdots+z_mb_m:
z_i\in\mathbb Z
\right\}.
}
$$

This is exactly the $\mathbb Z$-span:

$$
L
=
\langle
b_1,\ldots,b_m
\rangle_{\mathbb Z}.
$$

Therefore:

$$
\boxed{
L
\text{ is a free }\mathbb Z\text{-module of rank }m.
}
$$

If:

$$
m=n,
$$

then $L$ is a **full-rank lattice** in $\mathbb R^n$.

---

### Algebra and geometry coexist

A lattice has two simultaneous structures.

Algebraically:

$$
L
$$

is a free $\mathbb Z$-module.

Geometrically:

$$
L
\subseteq
\mathbb R^n.
$$

The coefficients:

$$
z_i
$$

are discrete integers.

But quantities such as:

- lengths,
- angles,
- orthogonality,
- volume,

are measured using the Euclidean geometry of:

$$
\mathbb R^n.
$$

This is why lattice theory naturally lies between:

$$
\boxed{
\text{abstract algebra}
}
$$

and:

$$
\boxed{
\text{Euclidean geometry}.
}
$$

---

### Matrix representation

Place the basis vectors into a matrix:

$$
B
=
\begin{bmatrix}
| & & |\\
b_1 & \cdots & b_m\\
| & & |
\end{bmatrix}.
$$

Then lattice vectors can be written as:

$$
\boxed{
Bz,
\qquad
z\in\mathbb Z^m.
}
$$

So:

$$
L
=
\{
Bz:
z\in\mathbb Z^m
\}.
$$

This is the form most commonly used computationally.

---

### A lattice has many bases

Suppose:

$$
B
$$

is a lattice basis.

Let:

$$
U\in\operatorname{GL}_m(\mathbb Z),
$$

meaning:

$$
U
$$

is an invertible integer matrix with:

$$
\det U=\pm1.
$$

Then:

$$
BU
$$

generates exactly the same lattice.

Thus:

$$
\boxed{
B
\quad\text{and}\quad
BU
}
$$

are different bases for the same $\mathbb Z$-module.

This is a central fact in lattice theory.

The lattice is the object.

A basis is only one representation of it.

---

### Example

Consider:

$$
B
=
\begin{pmatrix}
1&0\\
0&1
\end{pmatrix}.
$$

This generates:

$$
\mathbb Z^2.
$$

Now choose:

$$
U
=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix}.
$$

Since:

$$
\det U=1,
$$

the matrix is unimodular.

Then:

$$
BU
=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix}
$$

is another basis for exactly the same lattice:

$$
\mathbb Z^2.
$$

The coordinate representation changed.

The module did not.

---

## Polynomial modules and cryptography

The module viewpoint becomes especially important in modern lattice-based cryptography.

Let:

$$
R_q
=
\mathbb Z_q[x]/(f(x))
$$

be a polynomial quotient ring.

Then:

$$
\boxed{
R_q^k
}
$$

is a free $R_q$-module of rank $k$.

An element has the form:

$$
\mathbf a
=
(a_1,\ldots,a_k),
$$

where each:

$$
a_i\in R_q.
$$

Scalar multiplication by:

$$
r\in R_q
$$

is:

$$
r\mathbf a
=
(ra_1,\ldots,ra_k).
$$

This is not merely notation.

It gives the algebraic language behind **module lattices** and Module-LWE-style constructions.

---

### From ordinary lattices to module lattices

At the most basic level:

$$
\mathbb Z^n
$$

is a free module over:

$$
\mathbb Z.
$$

A structured polynomial object such as:

$$
R_q^k
$$

is a free module over:

$$
R_q.
$$

So one can view the progression schematically as:

$$
\boxed{
\mathbb Z^n
\rightarrow
R^k
\rightarrow
R_q^k.
}
$$

As the scalar ring gains structure, vectors inherit corresponding algebraic structure.

This can produce more compact representations and faster arithmetic, but it also means that the exact ring and module structure becomes part of the cryptographic design.

---

### Module-LWE viewpoint

In a simplified Module-LWE-style setting, one encounters objects such as:

$$
A\in R_q^{m\times k},
$$

$$
s\in R_q^k,
$$

and:

$$
e\in R_q^m.
$$

A typical relation has the form:

$$
\boxed{
b
=
As+e.
}
$$

This resembles ordinary linear algebra.

But the entries are not field elements or integers.

They are polynomial residue classes in:

$$
R_q.
$$

So the correct algebraic setting is module theory over a polynomial quotient ring.

---

### Why this intermediate abstraction matters

Without modules, one might jump directly from:

$$
\text{vectors}
$$

to:

$$
\text{module lattices}
$$

and treat the latter as a special cryptographic trick.

But the algebraic progression is systematic:

$$
\boxed{
\text{vector space over a field}
}
$$

becomes:

$$
\boxed{
\text{module over a ring}.
}
$$

Then:

$$
\mathbb Z\text{-modules}
$$

naturally describe integer-linear structure, while polynomial-ring modules describe structured higher-dimensional arithmetic.

Modules therefore provide the common language.

---

## The structural picture

At this stage we can connect several previous articles.

Groups gave us:

$$
(M,+).
$$

Rings gave us the scalar system:

$$
R.
$$

Modules combine them:

$$
\boxed{
R
\curvearrowright
M.
}
$$

The module has an additive group:

$$
(M,+),
$$

while elements of $R$ act as scalars.

If the scalar ring happens to be a field:

$$
R=F,
$$

then the module becomes a vector space.

If:

$$
R=\mathbb Z,
$$

then modules become abelian groups and free modules lead naturally to lattices.

If:

$$
R=R_q,
$$

then free modules such as:

$$
R_q^k
$$

provide the algebraic setting for structured lattice constructions.

So:

$$
\boxed{
\text{vector spaces}
\subset
\text{modules}
}
$$

and modules provide the bridge from classical linear algebra to many modern cryptographic structures.

---

## Practice and checkpoint

### Exercise 1 — Verify a module

Show that:

$$
\mathbb Z^2
$$

is a $\mathbb Z$-module.

Check the module axioms explicitly.

---

### Exercise 2 — Abelian group as module

Let:

$$
A=\mathbb Z/6\mathbb Z.
$$

Explain how integer scalar multiplication:

$$
n[a]
$$

is defined.

Verify:

$$
(n+m)[a]
=
n[a]+m[a].
$$

---

### Exercise 3 — Submodule

Consider:

$$
M=\mathbb Z^2
$$

and:

$$
N
=
\{
(2a,3b):
a,b\in\mathbb Z
\}.
$$

Show that:

$$
N\le_{\mathbb Z}M.
$$

---

### Exercise 4 — Nonfree module

Explain why:

$$
\mathbb Z/5\mathbb Z
$$

is not a free $\mathbb Z$-module.

What torsion relation does every element satisfy?

---

### Exercise 5 — Free module

Show that:

$$
\mathbb Z^3
$$

is free with basis:

$$
e_1,
e_2,
e_3.
$$

Why is the representation:

$$
z_1e_1+z_2e_2+z_3e_3
$$

unique?

---

### Exercise 6 — Module homomorphism

Define:

$$
f:\mathbb Z^2\rightarrow\mathbb Z
$$

by:

$$
f(x,y)
=
2x+3y.
$$

Show that $f$ is a $\mathbb Z$-module homomorphism.

Describe:

$$
\ker f.
$$

---

### Exercise 7 — Quotient module

Consider:

$$
2\mathbb Z
\le
\mathbb Z.
$$

Describe:

$$
\mathbb Z/2\mathbb Z
$$

as a quotient $\mathbb Z$-module.

What are its two cosets?

---

### Exercise 8 — Lattice basis

Let:

$$
b_1=
\begin{pmatrix}
2\\
0
\end{pmatrix},
\qquad
b_2=
\begin{pmatrix}
1\\
3
\end{pmatrix}.
$$

Describe:

$$
L
=
\{
z_1b_1+z_2b_2:
z_1,z_2\in\mathbb Z
\}.
$$

Write its basis matrix.

---

### Exercise 9 — Change of lattice basis

Let:

$$
U
=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix}.
$$

Verify:

$$
\det U=1.
$$

If $B$ is a basis matrix for a lattice, explain why:

$$
BU
$$

generates the same lattice.

---

### Exercise 10 — Polynomial module

Let:

$$
R
=
\mathbb F_2[x]/(x^2+x+1).
$$

Consider:

$$
R^2.
$$

For:

$$
r=x+1
$$

and:

$$
v=(x,1),
$$

compute:

$$
rv.
$$

Reduce all coordinates modulo:

$$
x^2+x+1.
$$

---

### Reader checkpoint

You should now be able to explain:

1. What an $R$-module is.
2. How modules generalize vector spaces.
3. Why the lack of scalar inverses changes the theory.
4. Why every vector space is a module.
5. Why every abelian group is a $\mathbb Z$-module.
6. Why:
   $$
   \mathbb Z^n
   $$
   is a free $\mathbb Z$-module.
7. What a submodule is.
8. How quotient modules are formed.
9. What an $R$-linear map preserves.
10. Why:
    $$
    M/\ker f
    \cong
    \operatorname{im}f.
    $$
11. What it means for a module to be generated.
12. What makes a module free.
13. Why not every module is free.
14. What torsion means.
15. Why ordinary vector spaces have no nonzero torsion.
16. What the free and torsion parts of a finitely generated module over a PID represent.
17. Why finitely generated abelian groups are a special case of module theory.
18. Why a Euclidean lattice is naturally a free $\mathbb Z$-module.
19. Why a lattice can have many different bases.
20. Why unimodular basis changes preserve a lattice.
21. Why:
    $$
    R_q^k
    $$
    is naturally a module over $R_q$.
22. Why module theory is the natural language connecting linear algebra to structured lattice cryptography.

If these ideas are clear, then modules should no longer look like an abstract generalization introduced merely for completeness.

They provide the algebraic framework in which vectors, integer lattices, polynomial structures, and ring-based linear algebra can all be treated uniformly.

---

## References and further reading

**David S. Dummit and Richard M. Foote**,  
*Abstract Algebra.*

A comprehensive reference for modules, free modules, finitely generated modules over PIDs, and structure theorems.

**Michael Artin**,  
*Algebra.*

A structural introduction to modules and their relationship with linear algebra and ring theory.

**Serge Lang**,  
*Algebra.*

A more advanced treatment of modules, tensor constructions, and general algebra.

**Thomas W. Hungerford**,  
*Algebra.*

A systematic treatment of module theory and modules over principal ideal domains.

**Daniele Micciancio and Shafi Goldwasser**,  
*Complexity of Lattice Problems: A Cryptographic Perspective.*

A standard reference for the mathematical and computational theory of lattices in cryptography.

**Chris Peikert**,  
*A Decade of Lattice Cryptography.*

A useful survey connecting lattice problems with modern cryptographic constructions and structured variants.

---

## Where this leaves us

The progression of the Abstract Algebra Foundations series is now:

$$
\text{groups}
\rightarrow
\text{homomorphisms and quotients}
\rightarrow
\text{rings and ideals}
\rightarrow
\text{fields and extensions}
\rightarrow
\text{polynomial rings}
\rightarrow
\text{modules}.
$$

Modules unify several of those ideas.

They combine:

$$
\boxed{
\text{an additive group}
}
$$

with:

$$
\boxed{
\text{scalar action by a ring}.
}
$$

That gives us the conceptual bridge from ordinary vector spaces to structures such as:

$$
\mathbb Z^n
$$

and:

$$
R_q^k.
$$

From this point, the remaining algebraic machinery can become more structural still: decompositions, bilinear constructions, tensor products, or whatever the final article in this foundation series develops.
