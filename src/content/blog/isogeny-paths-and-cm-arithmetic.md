---
title: "Elliptic Curve Mathematics XIII: Isogenies, Modular Polynomials, and CM Arithmetic"
description: "Isogenies, kernels and duals, modular polynomials, isogeny graphs, complex multiplication, norm equations, class groups, quadratic forms, and computational exploration of isogeny paths."
pubDate: "2025-05-27"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Post-Quantum Cryptography"
  - "Mathematical Foundations"

tags:
  - "isogenies"
  - "modular-polynomials"
  - "complex-multiplication"
  - "cm"
  - "isogeny-graphs"
  - "endomorphism-rings"
  - "class-groups"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 13
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

The previous chapters repeatedly encountered special maps between points on an elliptic curve.

Scalar multiplication gave

$$
[n]:E\longrightarrow E.
$$

Frobenius gave

$$
\pi:E\longrightarrow E.
$$

Schoof's algorithm studied the action of Frobenius on torsion.

Pairings used multiplication maps, divisors, and extension-field structure.

We now arrive at the natural final topic of this series:

$$
\boxed{
\text{isogenies}.
}
$$

An isogeny is not simply a different equation for the same curve.

It is an algebraic group homomorphism between elliptic curves.

Its kernel, degree, separability, and interaction with endomorphism rings reveal a remarkable amount of arithmetic structure.

At the computational level, isogenies lead naturally to:

* modular polynomials;
* \(j\)-invariant neighborhoods;
* isogeny graphs;
* isogeny paths;
* complex multiplication;
* ideal class groups;
* binary quadratic forms;
* Hilbert class polynomials.

This final chapter therefore brings together many themes from the entire series:

$$
\boxed{
\text{geometry}
\rightarrow
\text{group theory}
\rightarrow
\text{endomorphisms}
\rightarrow
\text{number theory}
\rightarrow
\text{graphs and algorithms}.
}
$$

---

## Table of Contents

- [1. From isomorphisms to isogenies](#1-from-isomorphisms-to-isogenies)
- [2. Definition of an isogeny](#2-definition-of-an-isogeny)
- [3. Kernel, degree, and separability](#3-kernel-degree-and-separability)
- [4. Quotients and Vélu’s formulas](#4-quotients-and-vélus-formulas)
- [5. Dual isogenies](#5-dual-isogenies)
- [Endomorphism rings](#endomorphism-rings)
- [7. Isogenies and (j)-invariants](#7-isogenies-and-j-invariants)
- [8. Classical modular polynomials](#8-classical-modular-polynomials)
- [9. Computing isogeny neighbors](#9-computing-isogeny-neighbors)
- [Isogeny graphs](#isogeny-graphs)
- [Isogeny paths](#isogeny-paths)
- [12. Ordinary and supersingular graph structure](#12-ordinary-and-supersingular-graph-structure)
- [Complex multiplication](#complex-multiplication)
- [14. Imaginary quadratic orders and discriminants](#14-imaginary-quadratic-orders-and-discriminants)
- [15. Frobenius and the CM norm equation](#15-frobenius-and-the-cm-norm-equation)
- [Split primes](#split-primes)
- [17. Class numbers and ideal classes](#17-class-numbers-and-ideal-classes)
- [18. Binary quadratic forms](#18-binary-quadratic-forms)
- [Hilbert class polynomials](#hilbert-class-polynomials)
- [20. CM construction of elliptic curves](#20-cm-construction-of-elliptic-curves)
- [21. Mapping the mathematics to the Sage script](#21-mapping-the-mathematics-to-the-sage-script)
- [22. Core graph functions](#22-core-graph-functions)
- [23. Core CM arithmetic functions](#23-core-cm-arithmetic-functions)
- [Cryptographic context](#cryptographic-context)
- [Companion implementation](#companion-implementation)
- [Final synthesis](#final-synthesis)
- [27. Series conclusion: Elliptic Curve Mathematics I–XIII](#27-series-conclusion-elliptic-curve-mathematics-ixiii)
- [Companion implementations across the series](#companion-implementations-across-the-series)
- [Further reading](#further-reading)

---

<a id="from-isomorphisms"></a>

## 1. From isomorphisms to isogenies

Chapter VII distinguished an elliptic curve from the equation used to represent it.

An isomorphism

$$
\phi:E_1\longrightarrow E_2
$$

is an invertible algebraic map preserving the identity.

Thus an isomorphism merely changes the representation of the same elliptic-curve structure.

An isogeny is more general.

It may collapse several points of \(E_1\) to the same point of \(E_2\).

Its kernel may therefore be nontrivial.

The basic hierarchy is

$$
\boxed{
\text{isomorphism}
\subset
\text{isogeny}.
}
$$

Every elliptic-curve isomorphism is an isogeny of degree \(1\).

But most isogenies are not isomorphisms.

---

<a id="definition-isogeny"></a>

## 2. Definition of an isogeny

Let

$$
E_1,
E_2
$$

be elliptic curves over a field \(K\).

An **isogeny**

$$
\boxed{
\phi:E_1\longrightarrow E_2
}
$$

is a nonconstant morphism of algebraic curves satisfying

$$
\boxed{
\phi(\mathcal O_{E_1})
=
\mathcal O_{E_2}.
}
$$

Such a map automatically respects the group law:

$$
\boxed{
\phi(P+Q)
=
\phi(P)+\phi(Q).
}
$$

Thus

$$
\phi
$$

is simultaneously:

* an algebraic map;
* a morphism of curves;
* a group homomorphism.

This combination of geometry and algebra is what makes isogenies so useful.

---

### Example: multiplication by \(n\)

The map

$$
[n]:E\rightarrow E
$$

is itself an isogeny.

Its kernel is

$$
\boxed{
\ker[n]=E[n].
}
$$

Its degree is

$$
\boxed{
\deg[n]=n^2.
}
$$

So the multiplication maps studied throughout the series were already our first examples of isogenies.

---

### Example: Frobenius

Over a finite field,

$$
\pi(x,y)=(x^q,y^q)
$$

is also an isogeny.

Thus Schoof's algorithm was fundamentally studying an isogeny:

$$
\boxed{
\pi\in\operatorname{End}(E).
}
$$

---

<a id="kernel-degree"></a>

## 3. Kernel, degree, and separability

The kernel of an isogeny is

$$
\boxed{
\ker\phi
=
\{
P\in E_1(\overline K):
\phi(P)=\mathcal O
\}.
}
$$

For a separable isogeny,

$$
\boxed{
\deg\phi
=
\#\ker\phi.
}
$$

This makes finite subgroups central to isogeny theory.

For example, if

$$
G\subset E
$$

is a cyclic subgroup of order \(\ell\), then under suitable hypotheses there is a separable isogeny

$$
\boxed{
\phi:E\rightarrow E/G
}
$$

with

$$
\boxed{
\ker\phi=G
}
$$

and

$$
\boxed{
\deg\phi=\ell.
}
$$

Such an isogeny is called an

$$
\boxed{
\ell\text{-isogeny}.
}
$$

---

### Inseparable isogenies

In characteristic \(p\), not every isogeny is separable.

The Frobenius map is the standard example.

Therefore the general relation is

$$
\boxed{
\deg\phi
=
\deg_{\mathrm{sep}}\phi\,
\deg_{\mathrm{ins}}\phi.
}
$$

Only the separable degree is directly measured by the number of geometric kernel points.

This is the same phenomenon we encountered when studying \(p\)-torsion.

---

<a id="velu"></a>

## 4. Quotients and Vélu's formulas

Suppose

$$
E:
y^2=x^3+Ax+B
$$

and let

$$
G\subset E(\overline K)
$$

be a finite subgroup.

Abstract theory tells us that a quotient curve

$$
E/G
$$

exists.

But cryptographic and computational applications require explicit equations.

**Vélu's formulas** provide them.

Given the points of \(G\), Vélu's construction computes:

1. an equation for

   $$
   E'=E/G;
   $$

2. a rational map

   $$
   \phi:E\rightarrow E';
   $$

3. an isogeny satisfying

   $$
   \ker\phi=G.
   $$

Thus Vélu turns

$$
\boxed{
\text{finite subgroup}
}
$$

into

$$
\boxed{
\text{explicit isogeny}.
}
$$

Conceptually:

$$
\boxed{
G
\subset E
}
$$

$$
\Downarrow
$$

$$
\boxed{
E/G
}
$$

$$
\Downarrow
$$

$$
\boxed{
\phi:E\rightarrow E/G.
}
$$

This is one of the fundamental computational constructions in isogeny theory.

---

<a id="dual-isogeny"></a>

## 5. Dual isogenies

Every isogeny

$$
\phi:E_1\rightarrow E_2
$$

of degree \(m\) has a **dual isogeny**

$$
\boxed{
\widehat\phi:E_2\rightarrow E_1
}
$$

satisfying

$$
\boxed{
\widehat\phi\circ\phi=[m]_{E_1}
}
$$

and

$$
\boxed{
\phi\circ\widehat\phi=[m]_{E_2}.
}
$$

Thus

$$
\boxed{
\deg\widehat\phi
=
\deg\phi.
}
$$

The dual is not generally an inverse.

Instead, composing an isogeny with its dual gives multiplication by its degree.

This distinction is essential:

$$
\boxed{
\phi^{-1}
\text{ usually does not exist as a morphism,}
}
$$

while

$$
\boxed{
\widehat\phi
\text{ always exists.}
}
$$

---

<a id="endomorphism-rings"></a>

## Endomorphism rings

An isogeny from a curve to itself is an **endomorphism**.

The set

$$
\boxed{
\operatorname{End}(E)
}
$$

forms a ring.

Addition is defined pointwise:

$$
(\alpha+\beta)(P)
=
\alpha(P)+\beta(P),
$$

and multiplication is composition:

$$
\alpha\beta
=
\alpha\circ\beta.
$$

At minimum,

$$
\operatorname{End}(E)
$$

contains all multiplication maps

$$
[n].
$$

Therefore

$$
\boxed{
\mathbb Z
\subseteq
\operatorname{End}(E).
}
$$

For generic elliptic curves over characteristic zero,

$$
\operatorname{End}_{\overline K}(E)
\cong
\mathbb Z.
$$

But some curves have additional endomorphisms.

Those curves have **complex multiplication**.

Over finite fields, the endomorphism ring is richer still.

---

<a id="j-isogenies"></a>

## 7. Isogenies and \(j\)-invariants

An isomorphism preserves the \(j\)-invariant.

Therefore,

$$
E_1\cong E_2
$$

implies

$$
j(E_1)=j(E_2).
$$

But isogenous curves need not have equal \(j\)-invariants.

This gives a useful viewpoint.

Instead of representing an elliptic curve by a particular Weierstrass equation, represent its geometric isomorphism class by

$$
j(E).
$$

Then an isogeny becomes a relation between different \(j\)-values.

For fixed degree \(\ell\),

$$
\boxed{
j(E_1)
\longleftrightarrow
j(E_2)
}
$$

whenever an \(\ell\)-isogeny exists.

This leads directly to modular polynomials.

---

<a id="modular-polynomials"></a>

## 8. Classical modular polynomials

For a positive integer \(N\), the classical modular polynomial

$$
\boxed{
\Phi_N(X,Y)\in\mathbb Z[X,Y]
}
$$

encodes pairs of elliptic curves connected by a cyclic isogeny of degree \(N\).

For prime

$$
\ell,
$$

the central relation is

$$
\boxed{
\Phi_\ell(j(E_1),j(E_2))=0
}
$$

when the two geometric isomorphism classes are connected by a cyclic \(\ell\)-isogeny.

Thus

$$
\boxed{
\Phi_\ell
}
$$

turns an isogeny relation into a polynomial equation.

This is extremely powerful.

Rather than explicitly constructing all possible degree-\(\ell\) kernels, we can solve a polynomial equation in the \(j\)-invariant.

---

### Symmetry

The classical modular polynomial satisfies

$$
\boxed{
\Phi_\ell(X,Y)
=
\Phi_\ell(Y,X).
}
$$

This reflects duality.

If

$$
E_1\rightarrow E_2
$$

is an \(\ell\)-isogeny, then its dual gives an \(\ell\)-isogeny

$$
E_2\rightarrow E_1.
$$

So adjacency is naturally symmetric.

---

<a id="isogeny-neighbors"></a>

## 9. Computing isogeny neighbors

Suppose we know

$$
j=j(E).
$$

To find its \(\ell\)-isogenous neighbors, evaluate

$$
\boxed{
\Phi_\ell(X,j).
}
$$

Then solve

$$
\boxed{
\Phi_\ell(X,j)=0
}
$$

over the chosen field.

Each root

$$
j'
$$

gives a candidate neighboring geometric isomorphism class.

Thus:

$$
\boxed{
\operatorname{Nbr}_\ell(j)
=
\{
j':
\Phi_\ell(j',j)=0
\}.
}
$$

Over

$$
\mathbb F_q,
$$

roots that lie in \(\mathbb F_q\) correspond to \(j\)-invariants of neighboring curves defined over the base field, subject to the usual care concerning twists and multiplicities.

This is the computational principle used by the companion script.

---

<a id="isogeny-graphs"></a>

## Isogeny graphs

Fix:

* a finite field \(\mathbb F_q\);
* a prime \(\ell\neq\operatorname{char}\mathbb F_q\).

Construct a graph whose vertices are elliptic-curve isomorphism classes, usually represented by

$$
j\text{-invariants}.
$$

Connect two vertices when an \(\ell\)-isogeny exists.

Thus:

$$
\boxed{
V
=
\{j(E)\}
}
$$

and

$$
\boxed{
(j_1,j_2)\in E_{\mathrm{graph}}
\iff
\Phi_\ell(j_1,j_2)=0.
}
$$

The resulting object is the

$$
\boxed{
\ell\text{-isogeny graph}.
}
$$

The geometry of these graphs reflects deep arithmetic information about endomorphism rings.

---

<a id="isogeny-paths"></a>

## Isogeny paths

An isogeny path

$$
j_0,j_1,\ldots,j_n
$$

satisfies

$$
\boxed{
\Phi_\ell(j_i,j_{i+1})=0
}
$$

for every

$$
0\leq i<n.
$$

Thus each step represents an \(\ell\)-isogeny.

Composition produces an isogeny whose degree is, in the separable generic situation,

$$
\boxed{
\ell^n.
}
$$

Graphically:

$$
j_0
\rightarrow
j_1
\rightarrow
j_2
\rightarrow
\cdots
\rightarrow
j_n.
$$

Searching for such paths is one of the central computational problems in isogeny arithmetic.

---

### Avoiding immediate backtracking

Suppose

$$
j_{i-1}
\rightarrow
j_i
$$

is one step.

The dual isogeny generally provides an edge back to

$$
j_{i-1}.
$$

So a graph walk that is intended to move forward often excludes the immediately previous vertex.

That is the reason the implementation may accept a known previous root and remove it from the list of candidate neighbors.

---

<a id="ordinary-supersingular"></a>

## 12. Ordinary and supersingular graph structure

The structure of an isogeny graph depends strongly on whether the curves are ordinary or supersingular.

### Ordinary curves

Ordinary \(\ell\)-isogeny components often exhibit the famous **isogeny-volcano** structure.

Very roughly, one sees:

* a surface;
* descending edges;
* ascending edges;
* horizontal edges.

The levels encode information about conductors of endomorphism orders.

Thus graph position reflects arithmetic information about

$$
\operatorname{End}(E).
$$

---

### Supersingular curves

Supersingular isogeny graphs behave differently.

Over suitable finite fields, their endomorphism algebras are quaternionic rather than imaginary quadratic.

These graphs tend to be highly connected and have strong expansion properties.

This dramatically different arithmetic structure is one reason supersingular isogenies became important in post-quantum cryptographic research.

---

<a id="complex-multiplication"></a>

## Complex multiplication

An elliptic curve has **complex multiplication** when its geometric endomorphism ring is strictly larger than

$$
\mathbb Z.
$$

In characteristic zero, this means

$$
\boxed{
\operatorname{End}_{\overline K}(E)
\cong
\mathcal O
}
$$

for an order

$$
\mathcal O
$$

in an imaginary quadratic field

$$
\boxed{
K_D=\mathbb Q(\sqrt D),
\qquad
D<0.
}
$$

Thus CM connects elliptic curves with classical algebraic number theory.

The same objects appear on both sides:

$$
\boxed{
\text{endomorphisms of elliptic curves}
}
$$

and

$$
\boxed{
\text{ideals in imaginary quadratic orders}.
}
$$

This correspondence is one of the deepest structural bridges in elliptic-curve arithmetic.

---

<a id="quadratic-orders"></a>

## 14. Imaginary quadratic orders and discriminants

An imaginary quadratic order has a negative discriminant

$$
\boxed{
D<0,
}
$$

with

$$
D\equiv0
\quad\text{or}\quad
1
\pmod4.
$$

If \(D\) is a **fundamental discriminant**, then the order is the full ring of integers

$$
\mathcal O_K
$$

of the imaginary quadratic field.

For nonfundamental \(D\), we instead obtain a nonmaximal order

$$
\mathcal O_D
\subsetneq
\mathcal O_K.
$$

This distinction matters.

Therefore the phrase

> class number of the imaginary quadratic field

is strictly accurate only when the order is maximal.

More generally, we should speak of the

$$
\boxed{
\text{class number of the quadratic order }\mathcal O_D.
}
$$

---

<a id="norm-equation"></a>

## 15. Frobenius and the CM norm equation

Suppose

$$
E/\mathbb F_p
$$

has Frobenius trace

$$
t.
$$

Frobenius satisfies

$$
\pi^2-t\pi+p=0.
$$

Its discriminant is

$$
\boxed{
t^2-4p.
}
$$

For a CM order of discriminant

$$
D<0,
$$

one encounters the relation

$$
\boxed{
t^2-4p=v^2D.
}
$$

Equivalently,

$$
\boxed{
4p=t^2-v^2D.
}
$$

This is the **CM norm equation**.

It may be understood by writing an element of the quadratic order with trace \(t\) and norm \(p\).

Thus the equation connects:

$$
\boxed{
p
}
$$

$$
\boxed{
t
}
$$

$$
\boxed{
D
}
$$

and therefore connects finite-field Frobenius with imaginary quadratic arithmetic.

---

### Relation to Hasse

Because

$$
D<0,
$$

the norm equation gives

$$
t^2
=
4p+v^2D
<
4p
$$

when \(v\neq0\).

Hence

$$
|t|<2\sqrt p.
$$

So the CM equation is automatically compatible with Hasse's bound.

---

<a id="split-primes"></a>

## Split primes

Let

$$
K=\mathbb Q(\sqrt D)
$$

be an imaginary quadratic field.

A prime \(p\) can:

* split;
* remain inert;
* ramify.

For

$$
p\nmid D,
$$

splitting is controlled by whether \(D\) is a quadratic residue modulo \(p\).

When

$$
p
$$

splits,

$$
\boxed{
(p)
=
\mathfrak p\overline{\mathfrak p}.
}
$$

This produces ideals of norm \(p\).

Norm equations provide a computational route to primes compatible with a chosen CM discriminant.

The script's split-prime search therefore seeks primes satisfying conditions of the form

$$
\boxed{
4p=t^2-v^2D.
}
$$

In the CM construction setting, such equations characterize primes with the required splitting behavior in the relevant ring-class arithmetic.

---

<a id="class-number"></a>

## 17. Class numbers and ideal classes

Let

$$
\mathcal O_D
$$

be an imaginary quadratic order.

Its proper invertible fractional ideals form a group modulo principal ideals:

$$
\boxed{
\operatorname{Cl}(\mathcal O_D).
}
$$

This is the **ideal class group**.

Its cardinality is the class number:

$$
\boxed{
h(D)
=
\#\operatorname{Cl}(\mathcal O_D).
}
$$

For a fundamental discriminant, this agrees with the class number of the imaginary quadratic field.

The class number measures how far the order is from unique factorization at the ideal level.

But in CM elliptic-curve theory it also has a geometric interpretation.

Roughly speaking, it counts the different CM \(j\)-invariants associated with the order.

This is why class numbers naturally appear in algorithms that enumerate CM curves.

---

<a id="quadratic-forms"></a>

## 18. Binary quadratic forms

A binary quadratic form is

$$
\boxed{
Q(x,y)=ax^2+bxy+cy^2.
}
$$

Its discriminant is

$$
\boxed{
D=b^2-4ac.
}
$$

For

$$
D<0,
$$

positive-definite primitive quadratic forms of discriminant \(D\), modulo proper equivalence, correspond to ideal classes of the quadratic order

$$
\mathcal O_D.
$$

So there is a classical correspondence

$$
\boxed{
\text{quadratic forms}
\longleftrightarrow
\text{ideal classes}.
}
$$

A form

$$
(p,b,c)
$$

satisfying

$$
\boxed{
b^2-4pc=D
}
$$

can therefore represent arithmetic information associated with a prime \(p\).

This is the mathematical basis of the script's `prime_form` routine.

---

<a id="hilbert-class-polynomials"></a>

## Hilbert class polynomials

For a negative discriminant \(D\), define the class polynomial

$$
\boxed{
H_D(X)
=
\prod_{[E]}
(X-j(E)),
}
$$

where the product runs over the complex isomorphism classes of elliptic curves with CM by the relevant order.

For fundamental maximal-order CM, this is traditionally called a **Hilbert class polynomial**.

More generally, for nonmaximal orders one speaks of ring class polynomials.

Its degree is

$$
\boxed{
\deg H_D=h(D).
}
$$

Thus the class number determines how many CM \(j\)-invariants appear.

This polynomial gives a powerful route from algebraic number theory to explicit elliptic curves.

---

<a id="cm-construction"></a>

## 20. CM construction of elliptic curves

Suppose we want to construct an elliptic curve over

$$
\mathbb F_p
$$

with controlled Frobenius arithmetic.

Choose a negative discriminant \(D\) and solve

$$
\boxed{
4p=t^2-v^2D.
}
$$

Then compute the corresponding class polynomial

$$
H_D(X).
$$

Reduce it modulo \(p\).

Find a root

$$
j\in\mathbb F_p.
$$

Construct an elliptic curve with that \(j\)-invariant.

The possible curve orders are then

$$
\boxed{
p+1-t
}
$$

or

$$
\boxed{
p+1+t,
}
$$

with quadratic twisting interchanging the sign of the Frobenius trace.

So the CM construction pipeline is

$$
\boxed{
D
}
$$

$$
\Downarrow
$$

$$
\boxed{
4p=t^2-v^2D
}
$$

$$
\Downarrow
$$

$$
\boxed{
H_D(X)
}
$$

$$
\Downarrow
$$

$$
\boxed{
j\in\mathbb F_p
}
$$

$$
\Downarrow
$$

$$
\boxed{
E/\mathbb F_p
}
$$

$$
\Downarrow
$$

$$
\boxed{
\#E(\mathbb F_p)=p+1\mp t.
}
$$

This is one of the most elegant examples of explicit class-field-theoretic ideas feeding directly into elliptic-curve construction.

---

<a id="script-structure"></a>

## 21. Mapping the mathematics to the Sage script

The companion script combines two related but distinct computational themes.

### Isogeny-graph arithmetic

It uses modular polynomials to:

* find neighboring \(j\)-invariants;
* test adjacency;
* explore paths.

### CM arithmetic

It uses imaginary quadratic arithmetic to:

* solve norm equations;
* find suitable primes;
* compute class numbers;
* construct quadratic forms.

So conceptually the implementation has two layers:

$$
\boxed{
\text{modular-polynomial graph layer}
}
$$

and

$$
\boxed{
\text{CM arithmetic layer}.
}
$$

These should be understood separately before studying how they interact.

---

<a id="graph-functions"></a>

## 22. Core graph functions

### `expand_roots(r)`

The function expands a root list containing multiplicities into a flat list.

Conceptually,

$$
[(r_1,m_1),\ldots,(r_s,m_s)]
$$

becomes

$$
[
\underbrace{r_1,\ldots,r_1}_{m_1},
\ldots,
\underbrace{r_s,\ldots,r_s}_{m_s}
].
$$

This is primarily a utility routine.

Multiplicity matters because repeated roots may encode special graph behavior or automorphism-related degeneracies.

---

### `isogeny_nbrs(ell, j, xj=None)`

This computes roots of

$$
\boxed{
\Phi_\ell(X,j).
}
$$

Thus it finds candidate \(\ell\)-isogenous neighboring \(j\)-invariants.

Conceptually:

$$
\boxed{
j
\longrightarrow
\{
j':
\Phi_\ell(j',j)=0
\}.
}
$$

If `xj` is supplied, the corresponding root can be removed.

This is useful for avoiding immediate traversal back through the dual edge.

---

### `isogeny_is_nbr(ell, j1, j2)`

This evaluates

$$
\boxed{
\Phi_\ell(j_1,j_2).
}
$$

If the result is zero,

$$
j_1
$$

and

$$
j_2
$$

represent adjacent vertices in the corresponding modular-polynomial graph.

This is a direct adjacency test.

---

### `isogeny_path(ell, j0, j1, n)`

This searches for a sequence

$$
j_0
\rightarrow
j^{(1)}
\rightarrow
\cdots
\rightarrow
j_1
$$

of length \(n\), where every consecutive pair satisfies

$$
\Phi_\ell(j_i,j_{i+1})=0.
$$

This is a graph-search problem built directly from modular-polynomial arithmetic.

For small graphs and educational experiments this is an excellent way to visualize how isogeny composition becomes path traversal.

---

<a id="cm-functions"></a>

## 23. Core CM arithmetic functions

### `norm_equation(D, p)`

The routine seeks integer solutions of

$$
\boxed{
4p=t^2-v^2D.
}
$$

This is not merely an arbitrary Diophantine equation.

It represents the trace/norm relation of an imaginary-quadratic element associated with Frobenius.

When the appropriate CM hypotheses hold, a solution connects:

* the prime \(p\);
* the discriminant \(D\);
* the Frobenius trace \(t\);
* the conductor-related factor \(v\).

---

### `next_split_prime(D, t0)`

This searches for a prime \(p\) compatible with the selected discriminant through the CM norm relation.

Such primes are useful when constructing curves using class polynomials.

The computational idea is

$$
\boxed{
\text{choose CM discriminant}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{find compatible prime}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{construct CM curve over }\mathbb F_p.
}
$$

---

### `class_number(D)`

This computes

$$
\boxed{
h(D).
}
$$

More precisely, it measures the class number of the imaginary quadratic order of discriminant \(D\).

If \(D\) is fundamental, this is the class number of the maximal order of

$$
\mathbb Q(\sqrt D).
$$

The distinction should be retained in the implementation documentation.

---

### `prime_form(D, p)`

This seeks a form

$$
\boxed{
(p,b,c)
}
$$

such that

$$
\boxed{
b^2-4pc=D.
}
$$

Such a form has discriminant \(D\) and links prime representation with the quadratic-form/class-group description of the order.

This gives a concrete computational bridge:

$$
\boxed{
\text{prime}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{quadratic form}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{ideal class}.
}
$$

---

<a id="cryptographic-context"></a>

## Cryptographic context

Isogeny arithmetic has appeared in several cryptographic settings.

But an important historical distinction must now be made.

### SIDH and SIKE

SIDH and its KEM construction SIKE were based on supersingular isogenies together with auxiliary torsion-point information.

In 2022, powerful key-recovery attacks showed that the original SIDH structure was insecure.

Consequently, SIKE must be regarded as broken and should not be used as a cryptographic KEM.

Its historical importance remains substantial:

* it drove major progress in isogeny arithmetic;
* it motivated highly optimized isogeny software;
* its cryptanalysis produced new mathematics;
* it demonstrated the importance of understanding auxiliary torsion information.

But it should now be studied as a historical and research construction, not as a secure deployment candidate.

---

### Other isogeny-based directions

The failure of SIDH does **not** imply that every isogeny-based construction is broken.

Different approaches rely on different mathematical structures.

Examples studied in the literature include:

* CSIDH-style commutative class-group actions;
* CGL-style constructions;
* isogeny-based signatures;
* supersingular endomorphism and isogeny problems.

These do not inherit the SIDH attack merely because they also use isogenies.

Each construction requires its own security analysis.

---

### Why this chapter remains important

Regardless of the status of any particular protocol, the mathematics remains fundamental.

Modular polynomials and isogeny graphs are important in:

* SEA point counting;
* endomorphism-ring computation;
* CM methods;
* arithmetic geometry;
* explicit class field theory;
* post-quantum research.

So isogenies belong in a mathematical elliptic-curve series independently of any one cryptographic scheme.

---

<a id="companion-implementation"></a>

## Companion implementation

The CryptoCave source material includes the Sage implementation:

[`src/IsogenyPaths.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/IsogenyPaths.sage)

Repository path:

```text
experiments/ready-material/elliptic-curves/src/IsogenyPaths.sage
```

The implementation contains functionality for:

* modular-polynomial evaluation;
* isogeny-neighbor discovery;
* adjacency testing;
* isogeny-path exploration;
* CM norm equations;
* split-prime searches;
* class-number computation;
* quadratic-form construction.

A useful study path is:

$$
\boxed{
j(E)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\Phi_\ell(X,j(E))
}
$$

$$
\Downarrow
$$

$$
\boxed{
\ell\text{-isogenous neighbors}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isogeny graph}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{graph path}.
}
$$

For the CM side:

$$
\boxed{
D
}
$$

$$
\Downarrow
$$

$$
\boxed{
4p=t^2-v^2D
}
$$

$$
\Downarrow
$$

$$
\boxed{
h(D)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{ideal / quadratic-form arithmetic}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{CM elliptic curves}.
}
$$

When reviewing the script, useful questions include:

1. Which modular polynomials are hardcoded?
2. Are they interpreted over \(\mathbb Z\) and then reduced into the active field?
3. How are root multiplicities handled?
4. Does `isogeny_nbrs` return only roots in the base field?
5. How is immediate dual-edge backtracking avoided?
6. What search strategy is used by `isogeny_path`?
7. Does the norm-equation routine assume \(D\) is fundamental?
8. Does `class_number(D)` handle nonmaximal orders or only field discriminants?
9. How does `prime_form` select \(b\)?
10. Are all quadratic forms reduced to canonical representatives?
11. How do the CM functions relate to the modular-polynomial graph functions?
12. Which parts are educational reference code rather than scalable production algorithms?

As throughout this series, the implementation should be treated as an executable mathematical notebook rather than a black box.

---

<a id="final-synthesis"></a>

## Final synthesis

This chapter began with a map

$$
\boxed{
\phi:E_1\rightarrow E_2.
}
$$

Its kernel determines its structure.

For separable maps,

$$
\boxed{
\deg\phi=\#\ker\phi.
}
$$

A cyclic subgroup of order \(\ell\) gives an \(\ell\)-isogeny.

The resulting geometric relation can be compressed into one polynomial equation:

$$
\boxed{
\Phi_\ell(j_1,j_2)=0.
}
$$

Repeated relations produce a graph:

$$
\boxed{
j_0
\rightarrow
j_1
\rightarrow
\cdots
\rightarrow
j_n.
}
$$

But the graph is not merely combinatorial.

Its structure is controlled by endomorphism rings.

For CM curves these rings are imaginary quadratic orders:

$$
\boxed{
\operatorname{End}(E)
\sim
\mathcal O_D.
}
$$

That introduces:

$$
\boxed{
D,
\qquad
h(D),
\qquad
\operatorname{Cl}(\mathcal O_D).
}
$$

Frobenius then satisfies the norm relation

$$
\boxed{
4p=t^2-v^2D.
}
$$

Quadratic forms encode ideal classes:

$$
\boxed{
b^2-4ac=D.
}
$$

Class polynomials encode CM \(j\)-invariants:

$$
\boxed{
H_D(X).
}
$$

So the complete mathematical chain is

$$
\boxed{
\text{finite subgroup}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isogeny}
}
$$

$$
\Downarrow
$$

$$
\boxed{
j\text{-invariant relation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{modular polynomial}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isogeny graph}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{endomorphism ring}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{imaginary quadratic order}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{class group and CM arithmetic}.
}
$$

This is where algebraic geometry, number theory, finite fields, graph theory, and cryptography meet.

---

<a id="series-conclusion"></a>

## 27. Series conclusion: Elliptic Curve Mathematics I–XIII

We can now step back and see the complete path of this series.

### I — Plane Cubics, Projective Closure, and Nonsingularity

We began with

$$
y^2=x^3+ax+b.
$$

But we learned immediately that an elliptic curve is not merely an equation.

It is a smooth projective genus-one curve equipped with a distinguished point.

Projective closure introduced

$$
\mathcal O=(0:1:0),
$$

while the discriminant identified nonsingularity.

---

### II — The Group Law

Lines intersect a cubic three times.

That geometric fact produced

$$
\boxed{
P+Q.
}
$$

We derived explicit addition and doubling formulas and turned the geometric curve into an abelian group.

---

### III — Why the Group Law Is Associative

Coordinate algebra did not explain associativity conceptually.

Divisor classes did.

We identified

$$
\boxed{
E
\cong
\operatorname{Pic}^0(E),
}
$$

and the group law became the natural addition law of divisor classes.

---

### IV — Rational Points and Mordell–Weil

Over number fields,

$$
E(K)
$$

is finitely generated.

For

$$
K=\mathbb Q,
$$

$$
\boxed{
E(\mathbb Q)
\cong
E(\mathbb Q)_{\mathrm{tors}}
\oplus
\mathbb Z^r.
}
$$

Heights, descent, Selmer groups, and rank revealed the arithmetic complexity hidden inside rational points.

---

### V — Torsion Points and Division

We studied

$$
\boxed{
E[n]=\ker[n].
}
$$

Over characteristic not dividing \(n\),

$$
\boxed{
E[n]
\cong
(\mathbb Z/n\mathbb Z)^2.
}
$$

Nagell–Lutz and Mazur showed how surprisingly constrained rational torsion over \(\mathbb Q\) can be.

---

### VI — Finite Fields, Hasse, and Frobenius

Moving to

$$
E(\mathbb F_q)
$$

made the whole group finite.

We introduced

$$
\boxed{
\#E(\mathbb F_q)=q+1-t
}
$$

and

$$
\boxed{
|t|\leq2\sqrt q.
}
$$

The Frobenius endomorphism became one of the central objects of the entire theory.

---

### VII — Models, Isomorphisms, and the \(j\)-Invariant

We separated the abstract curve from its coordinate representation.

The \(j\)-invariant gave

$$
\boxed{
E_1\cong_{\overline K}E_2
\iff
j(E_1)=j(E_2).
}
$$

We also encountered twists and alternative models.

---

### VIII — Montgomery Curves

Montgomery form exploited

$$
P\sim-P
$$

and moved arithmetic to the Kummer line.

That led to

$$
\boxed{
\operatorname{xDBL},
\quad
\operatorname{xADD},
\quad
\text{Montgomery ladder}.
}
$$

Mathematical representation directly shaped cryptographic implementation.

---

### IX — Edwards Curves

Edwards and twisted Edwards models emphasized full-point arithmetic.

Symmetry gave unified addition formulas and, under appropriate parameter conditions, complete formulas.

The relation

$$
\boxed{
\text{Montgomery}
\longleftrightarrow
\text{twisted Edwards}
}
$$

showed how the same underlying geometry can support radically different computational interfaces.

---

### X — Division Polynomials

The map

$$
[n]
$$

became explicit polynomial algebra.

We obtained

$$
\boxed{
[n]P=\mathcal O
\iff
\psi_n(P)=0.
}
$$

The functions

$$
\psi_n,
\qquad
\phi_n,
\qquad
\omega_n
$$

encoded scalar multiplication symbolically.

---

### XI — Weil and Tate Pairings

Divisors and rational functions produced bilinear maps

$$
\boxed{
e:
G_1\times G_2
\rightarrow
G_T.
}
$$

Miller's algorithm made the construction computational.

The embedding degree connected elliptic-curve torsion to finite-field multiplicative groups.

---

### XII — Schoof's Algorithm

Frobenius, torsion, and division polynomials combined into deterministic polynomial-time point counting.

We computed

$$
t\bmod\ell
$$

on

$$
E[\ell]
$$

and reconstructed the exact trace through CRT and Hasse's bound.

---

### XIII — Isogenies and Complex Multiplication

Finally, finite subgroups became maps between curves.

Isogenies became edges.

\(j\)-invariants became vertices.

Modular polynomials encoded adjacency.

Endomorphism rings connected those graphs to imaginary quadratic orders and class groups.

The final chain is therefore much larger than where we began:

$$
\boxed{
y^2=x^3+ax+b
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{projective algebraic curve}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{abelian group}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{divisors and Picard group}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{rational points and heights}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{torsion}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{finite fields and Frobenius}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{curve models}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{division polynomials}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{pairings}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{point counting}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{isogenies and CM}.
}
$$

We started from a cubic equation.

We ended with:

* arithmetic geometry;
* algebraic groups;
* finite fields;
* number fields;
* class groups;
* graph structures;
* algorithms;
* cryptographic representations.

That is the real reason elliptic curves are so remarkable.

The same small equation

$$
\boxed{
y^2=x^3+ax+b
}
$$

opens the door to an enormous mathematical landscape.

And throughout the entire journey the recurring lesson has been the same:

$$
\boxed{
\text{never confuse the representation with the underlying structure}.
}
$$

The equation is only the beginning.

---

## Companion implementations across the series

Several chapters are accompanied by executable CryptoCave material, including:

* full elliptic-curve arithmetic;
* Montgomery arithmetic;
* Edwards arithmetic;
* division-polynomial experiments;
* pairing implementations;
* Schoof point counting;
* isogeny-path and CM arithmetic.

For this final chapter:

[`src/IsogenyPaths.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/ready-material/elliptic-curves/src/IsogenyPaths.sage)

The guiding philosophy of the entire series has therefore been:

$$
\boxed{
\text{definition}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{derivation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{structure}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{algorithm}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{implementation}.
}
$$

---

## Further reading

Useful references for this final chapter and the series as a whole include:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Joseph H. Silverman, **Advanced Topics in the Arithmetic of Elliptic Curves**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Steven D. Galbraith, **Mathematics of Public Key Cryptography**.
* Jacques Vélu, work on explicit isogeny formulas.
* David Kohel, work on endomorphism rings and isogeny volcanoes.
* Andrew V. Sutherland, work on modular polynomials, isogeny volcanoes, CM methods, and point counting.
* David Cox, **Primes of the Form \(x^2+ny^2\)**, for quadratic forms and complex multiplication.
* René Schoof, work on elliptic-curve point counting.
* Andrew V. Sutherland, **18.783 Elliptic Curves** lecture material.
* NIST IR 8545 for the historical status of SIKE and the fourth round of the NIST PQC process.

---

**End of the Elliptic Curve Mathematics series.**

$$
\boxed{
\text{I--XIII complete.}
}
$$
