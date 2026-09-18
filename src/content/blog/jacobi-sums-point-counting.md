---
title: "Computational Number Theory V: Jacobi Sums, Cyclotomy, and Character-Based Point Counting"
description: "Jacobi sums, their relation to Gauss sums, cyclotomic classes, finite-field equation counting, and the use of character sums in point counting on algebraic curves."
pubDate: "2025-05-24"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Finite Fields"
  - "Elliptic Curve Theory"
tags:
  - "jacobi-sums"
  - "cyclotomy"
  - "character-sums"
  - "point-counting"
  - "finite-fields"
difficulty: "Advanced"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 5
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

Gauss sums combine a multiplicative character with an additive character.

Jacobi sums take a different approach.

They correlate **two multiplicative characters directly**:

$$
\boxed{
J(\chi,\lambda)
=
\sum_{x\in\mathbb F_q}
\chi(x)\lambda(1-x).
}
$$

At first this looks like a small variation on the character sums developed in the previous article.

It is much more than that.

Jacobi sums encode:

- correlations between multiplicative residue classes;
- cyclotomic structure;
- counts of solutions to finite-field equations;
- arithmetic of Fermat-type curves;
- information about Frobenius and point counts.

They therefore provide a natural bridge:

$$
\boxed{
\text{character theory}
\rightarrow
\text{cyclotomy}
\rightarrow
\text{finite-field geometry}.
}
$$

Throughout this article, multiplicative characters are extended to the whole field using the convention:

$$
\boxed{
\chi(0)=0.
}
$$

This convention matters whenever trivial characters or the values $x=0,1$ occur.

---

## Table of Contents

- [Jacobi sums](#jacobi-sums)
- [The relation with Gauss sums](#the-relation-with-gauss-sums)
- [Cyclotomic classes and character correlations](#cyclotomic-classes-and-character-correlations)
- [Counting finite-field equations with characters](#counting-finite-field-equations-with-characters)
- [Curves and Frobenius point counts](#curves-and-frobenius-point-counts)
- [Square-root cancellation and Weil bounds](#square-root-cancellation-and-weil-bounds)
- [Computational verification and the role of the archived worksheets](#computational-verification-and-the-role-of-the-archived-worksheets)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Jacobi sums

Let:

$$
\chi,\lambda:
\mathbb F_q^\times
\rightarrow
\mathbb C^\times
$$

be multiplicative characters.

Extend them to:

$$
\mathbb F_q
$$

by setting:

$$
\chi(0)=\lambda(0)=0.
$$

The **Jacobi sum** is:

$$
\boxed{
J(\chi,\lambda)
=
\sum_{x\in\mathbb F_q}
\chi(x)\lambda(1-x).
}
$$

The expression measures how often the multiplicative behavior of:

$$
x
$$

correlates with that of:

$$
1-x.
$$

Unlike a Gauss sum, no additive character appears explicitly.

Yet additive structure is still present through the relation:

$$
x+(1-x)=1.
$$

So Jacobi sums are still mixing addition and multiplication, but in a different way.

---

### Why the values $0$ and $1$ matter

At:

$$
x=0,
$$

the first factor is:

$$
\chi(0)=0.
$$

At:

$$
x=1,
$$

the second factor is:

$$
\lambda(0)=0.
$$

Thus, under our convention, both endpoint terms vanish.

This seems minor, but changing the extension convention changes formulas involving trivial characters.

Therefore character conventions should always be stated before identities are used.

---

### Symmetry

Substitute:

$$
y=1-x.
$$

Then:

$$
J(\chi,\lambda)
=
\sum_y
\chi(1-y)\lambda(y).
$$

Since multiplication in $\mathbb C$ is commutative:

$$
\boxed{
J(\chi,\lambda)
=
J(\lambda,\chi).
}
$$

So Jacobi sums are symmetric in their two characters.

---

### Trivial-character cases

Let:

$$
\varepsilon
$$

denote the trivial multiplicative character:

$$
\varepsilon(x)=1
\qquad
(x\neq0),
$$

extended by:

$$
\varepsilon(0)=0.
$$

If $\chi$ is nontrivial, then:

$$
\begin{aligned}
J(\chi,\varepsilon)
&=
\sum_x
\chi(x)\varepsilon(1-x).
\end{aligned}
$$

The factor:

$$
\varepsilon(1-x)
$$

removes the term $x=1$.

Therefore:

$$
J(\chi,\varepsilon)
=
\sum_{x\neq1}\chi(x).
$$

But:

$$
\sum_x\chi(x)=0
$$

for a nontrivial character.

Hence:

$$
\boxed{
J(\chi,\varepsilon)=-1.
}
$$

Likewise:

$$
\boxed{
J(\varepsilon,\chi)=-1.
}
$$

These exceptional cases are exactly why nontriviality assumptions must accompany the clean Gauss-sum identity.

---

### Inverse-character case

Suppose:

$$
\lambda=\chi^{-1}
$$

with $\chi$ nontrivial.

Then:

$$
\chi\lambda=\varepsilon.
$$

The standard quotient formula involving:

$$
G(\chi\lambda)
$$

cannot be applied in its ordinary nontrivial form.

Instead:

$$
\boxed{
J(\chi,\chi^{-1})
=
-\chi(-1).
}
$$

In particular:

$$
\boxed{
|J(\chi,\chi^{-1})|=1.
}
$$

This is very different from the generic square-root magnitude:

$$
\sqrt q.
$$

---

## The relation with Gauss sums

Let:

$$
\Psi
$$

be a fixed nontrivial additive character of:

$$
\mathbb F_q.
$$

Recall the Gauss sum:

$$
G(\chi)
=
\sum_{x\in\mathbb F_q}
\chi(x)\Psi(x).
$$

Suppose:

$$
\chi,
\qquad
\lambda,
\qquad
\chi\lambda
$$

are all nontrivial.

Then:

$$
\boxed{
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}.
}
$$

This is the fundamental bridge between Gauss sums and Jacobi sums.

---

### Derivation

Start with:

$$
G(\chi)G(\lambda).
$$

Expanding:

$$
G(\chi)G(\lambda)
=
\sum_{x,y\in\mathbb F_q}
\chi(x)\lambda(y)
\Psi(x+y).
$$

Group the terms according to:

$$
t=x+y.
$$

For:

$$
t\neq0,
$$

write:

$$
x=tu,
$$

and:

$$
y=t(1-u).
$$

Then:

$$
\chi(x)
=
\chi(t)\chi(u),
$$

and:

$$
\lambda(y)
=
\lambda(t)\lambda(1-u).
$$

Therefore:

$$
\chi(x)\lambda(y)
=
(\chi\lambda)(t)
\chi(u)\lambda(1-u).
$$

So the inner sum becomes:

$$
\sum_u
\chi(u)\lambda(1-u)
=
J(\chi,\lambda).
$$

Hence:

$$
G(\chi)G(\lambda)
=
J(\chi,\lambda)
\sum_{t\neq0}
(\chi\lambda)(t)\Psi(t).
$$

Because:

$$
\chi\lambda
$$

is nontrivial, the last sum is:

$$
G(\chi\lambda).
$$

Therefore:

$$
\boxed{
G(\chi)G(\lambda)
=
J(\chi,\lambda)
G(\chi\lambda).
}
$$

Solving for the Jacobi sum gives:

$$
\boxed{
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}.
}
$$

---

### Magnitude

From the previous article:

$$
|G(\chi)|=\sqrt q
$$

for every nontrivial multiplicative character.

Therefore, when:

$$
\chi,
\lambda,
\chi\lambda
$$

are all nontrivial:

$$
|J(\chi,\lambda)|
=
\frac{
\sqrt q\sqrt q
}{
\sqrt q
}.
$$

Hence:

$$
\boxed{
|J(\chi,\lambda)|=\sqrt q.
}
$$

So the same square-root cancellation that appears in Gauss sums reappears in Jacobi sums.

---

### Algebraic values

Character values are roots of unity.

Therefore Jacobi sums belong naturally to cyclotomic fields.

If the characters have order dividing:

$$
m,
$$

then their values lie in:

$$
\mathbb Q(\zeta_m),
$$

where:

$$
\zeta_m=e^{2\pi i/m}.
$$

Consequently:

$$
\boxed{
J(\chi,\lambda)
\in
\mathbb Z[\zeta_m]
}
$$

in the standard algebraic-integer setting.

This is where Jacobi sums begin to interact directly with cyclotomy.

---

## Cyclotomic classes and character correlations

Let:

$$
m\mid(q-1).
$$

Because:

$$
\mathbb F_q^\times
$$

is cyclic, choose a generator:

$$
g.
$$

The subgroup of $m$-th powers is:

$$
\boxed{
C_0
=
\langle g^m\rangle.
}
$$

Its cosets are:

$$
\boxed{
C_j
=
g^jC_0,
\qquad
j=0,\ldots,m-1.
}
$$

These are the **cyclotomic classes of order $m$**.

They partition:

$$
\mathbb F_q^\times.
$$

---

### Example: quadratic cyclotomy

For:

$$
m=2,
$$

there are two classes.

The first:

$$
C_0
$$

contains the quadratic residues.

The second:

$$
C_1
$$

contains the quadratic nonresidues.

The quadratic character records exactly which class an element belongs to:

$$
\chi(x)
=
\begin{cases}
1,&x\in C_0,\\
-1,&x\in C_1.
\end{cases}
$$

Thus the Legendre-symbol viewpoint is the first nontrivial example of cyclotomy.

---

### Higher-order characters

Let:

$$
\chi
$$

have exact order $m$.

Choose:

$$
\zeta_m=e^{2\pi i/m}
$$

and normalize:

$$
\chi(g)=\zeta_m.
$$

Then:

$$
x\in C_j
$$

implies:

$$
\boxed{
\chi(x)=\zeta_m^j.
}
$$

Characters therefore encode cyclotomic classes using roots of unity.

Instead of storing a class label:

$$
j,
$$

we store the Fourier-like value:

$$
\zeta_m^j.
$$

---

### Cyclotomic numbers

Classical cyclotomy studies counts such as:

$$
\boxed{
(i,j)
=
\#\{
x\in C_i:
x+1\in C_j
\}.
}
$$

These are called **cyclotomic numbers**.

They measure correlations between multiplicative classes after an additive shift.

Compare this with a Jacobi sum:

$$
J(\chi^a,\chi^b)
=
\sum_x
\chi^a(x)
\chi^b(1-x).
$$

The structural resemblance is not accidental.

Cyclotomic numbers count class intersections directly.

Jacobi sums encode those same correlations through roots of unity.

Schematically:

$$
\boxed{
\text{cyclotomic counts}
\quad
\longleftrightarrow
\quad
\text{Jacobi sums via finite Fourier transforms}.
}
$$

This explains why classical tables of cyclotomic numbers and modern character-sum computations often contain the same arithmetic information in different forms.

---

### Why this viewpoint is useful

Direct class counting is combinatorial.

Characters replace class-membership conditions with algebraic weights.

This often transforms a difficult-looking counting problem into a sum that can be manipulated algebraically.

That transition:

$$
\boxed{
\text{indicator function}
\rightarrow
\text{character expansion}
}
$$

is one of the recurring techniques of computational number theory.

---

## Counting finite-field equations with characters

Characters can detect whether an element belongs to a multiplicative power class.

This turns equations involving powers into character sums.

---

### Detecting $m$-th powers

Assume:

$$
m\mid(q-1)
$$

and let $\chi$ be a character of exact order $m$.

For:

$$
a\in\mathbb F_q^\times,
$$

the element $a$ is an $m$-th power exactly when:

$$
\chi(a)=1.
$$

The indicator function is:

$$
\boxed{
\mathbf 1_{(\mathbb F_q^\times)^m}(a)
=
\frac1m
\sum_{j=0}^{m-1}
\chi^j(a).
}
$$

Indeed, if:

$$
\chi(a)=1,
$$

the sum is:

$$
m.
$$

Otherwise it is a geometric sum of nontrivial $m$-th roots of unity and equals:

$$
0.
$$

This formula is for:

$$
a\neq0.
$$

The value $a=0$ must be treated separately under our convention:

$$
\chi(0)=0.
$$

---

### Number of $m$-th roots

Because:

$$
m\mid(q-1),
$$

a nonzero $m$-th power has exactly $m$ roots in:

$$
\mathbb F_q^\times.
$$

Therefore, for:

$$
a\neq0,
$$

$$
\boxed{
\#\{
y\in\mathbb F_q:
y^m=a
\}
=
\sum_{j=0}^{m-1}
\chi^j(a).
}
$$

For:

$$
a=0,
$$

there is exactly one solution:

$$
y=0.
$$

This small endpoint correction is important in exact counting formulas.

---

### Quadratic case

For odd $q$, let:

$$
\eta
$$

be the quadratic character.

Then:

$$
\boxed{
\#\{
y:
y^2=a
\}
=
1+\eta(a)
}
$$

for every:

$$
a\in\mathbb F_q,
$$

using:

$$
\eta(0)=0.
$$

Indeed:

- if $a=0$, there is one solution;
- if $a$ is a nonzero square, there are two;
- if $a$ is a nonsquare, there are none.

This tiny formula is extremely powerful.

---

### Counting a finite circle

Consider:

$$
x^2+y^2=1
$$

over an odd finite field:

$$
\mathbb F_q.
$$

For each fixed $x$, the number of possible $y$ is:

$$
1+\eta(1-x^2).
$$

Therefore:

$$
N
=
\sum_{x\in\mathbb F_q}
\left(
1+\eta(1-x^2)
\right).
$$

So:

$$
\boxed{
N
=
q
+
\sum_{x\in\mathbb F_q}
\eta(1-x^2).
}
$$

The character sum can be evaluated:

$$
\sum_x
\eta(1-x^2)
=
-\eta(-1).
$$

Hence:

$$
\boxed{
N
=
q-\eta(-1).
}
$$

Therefore:

$$
N=
\begin{cases}
q-1,
&
-1\text{ is a square in }\mathbb F_q,
\\[4pt]
q+1,
&
-1\text{ is a nonsquare}.
\end{cases}
$$

For a prime field:

$$
\mathbb F_p,
$$

this becomes:

$$
\boxed{
N=
\begin{cases}
p-1,
&
p\equiv1\pmod4,
\\[4pt]
p+1,
&
p\equiv3\pmod4.
\end{cases}
}
$$

A geometric counting problem has become a character-sum identity.

---

### Fermat-type equations

Now consider:

$$
x^m+y^m=1.
$$

Instead of enumerating all:

$$
q^2
$$

pairs $(x,y)$, we can express the number of $m$-th roots using characters.

This leads to sums involving terms such as:

$$
\chi^a(x)\chi^b(1-x),
$$

which are precisely Jacobi sums:

$$
\boxed{
J(\chi^a,\chi^b).
}
$$

Thus equations of the form:

$$
x^m+y^m=1
$$

naturally generate Jacobi sums.

This is the mathematical meaning behind the older computational experiments involving:

- finite circles;
- roots of unity;
- cyclotomic classes;
- Gauss sums;
- Jacobi sums.

They are all different manifestations of the same principle:

$$
\boxed{
\text{count solutions by replacing power conditions with characters}.
}
$$

---

## Curves and Frobenius point counts

Character sums become especially powerful when the finite-field equation defines an algebraic curve.

Consider a curve:

$$
C:
y^2=f(x)
$$

over an odd finite field:

$$
\mathbb F_q.
$$

For every $x$, the number of $y$-coordinates is:

$$
1+\eta(f(x)).
$$

Therefore the number of affine points is:

$$
\boxed{
\#C_{\mathrm{aff}}(\mathbb F_q)
=
q
+
\sum_{x\in\mathbb F_q}
\eta(f(x)).
}
$$

So point counting becomes character summation.

---

### Elliptic curves

Let:

$$
E:
y^2=x^3+Ax+B
$$

over:

$$
\mathbb F_q
$$

with odd characteristic and nonzero discriminant.

There is one projective point at infinity:

$$
\mathcal O.
$$

Therefore:

$$
\boxed{
\#E(\mathbb F_q)
=
q+1
+
\sum_{x\in\mathbb F_q}
\eta(
x^3+Ax+B
).
}
$$

By definition:

$$
\boxed{
\#E(\mathbb F_q)
=
q+1-t,
}
$$

where:

$$
t
$$

is the Frobenius trace.

Comparing the two formulas:

$$
\boxed{
t
=
-
\sum_{x\in\mathbb F_q}
\eta(
x^3+Ax+B
).
}
$$

Thus the Frobenius trace is itself encoded by a character sum.

---

### A small example

Consider:

$$
E:
y^2=x^3+x+1
$$

over:

$$
\mathbb F_5.
$$

For each:

$$
x=0,1,2,3,4,
$$

compute:

$$
f(x)=x^3+x+1.
$$

Modulo $5$:

$$
f(0)=1,
$$

$$
f(1)=3,
$$

$$
f(2)=1,
$$

$$
f(3)=1,
$$

$$
f(4)=4.
$$

The quadratic character modulo $5$ satisfies:

$$
\eta(1)=1,
\qquad
\eta(3)=-1,
\qquad
\eta(4)=1.
$$

Therefore:

$$
\sum_x\eta(f(x))
=
1-1+1+1+1
=
3.
$$

Hence:

$$
\#E(\mathbb F_5)
=
5+1+3
=
9.
$$

So:

$$
\boxed{
t
=
5+1-9
=
-3.
}
$$

Equivalently:

$$
t=-3
$$

follows directly from:

$$
t
=
-\sum_x\eta(f(x)).
$$

---

### Jacobi sums and special curves

For diagonal curves and Fermat-type curves, the character sums often organize naturally into Jacobi sums.

For example, curves related to:

$$
x^m+y^m=z^m
$$

over fields containing the relevant $m$-th roots of unity admit point-count formulas involving:

$$
J(\chi^a,\chi^b).
$$

At a deeper level, these Jacobi sums appear in the numerator of the zeta function of the curve.

So the progression is:

$$
\boxed{
\text{equation}
\rightarrow
\text{character decomposition}
\rightarrow
\text{Jacobi sums}
\rightarrow
\text{Frobenius information}.
}
$$

This is one of the clearest places where elementary-looking finite sums begin to encode arithmetic geometry.

---

### Special formulas versus general algorithms

Character-sum formulas can be extremely effective for specially structured curves.

But they should not be confused with general-purpose elliptic-curve point-counting algorithms.

For arbitrary elliptic curves, important algorithms include:

$$
\boxed{
\text{Schoof}
}
$$

and its practical extensions such as:

$$
\boxed{
\text{SEA}
}
$$

—the Schoof–Elkies–Atkin method.

These algorithms obtain Frobenius information through torsion and modular-polynomial techniques rather than merely evaluating a direct character sum over every field element.

So:

$$
\boxed{
\text{character-sum formula}
}
$$

and:

$$
\boxed{
\text{efficient general point-counting algorithm}
}
$$

are related goals but not the same computational method.

---

## Square-root cancellation and Weil bounds

A naive character sum over:

$$
q
$$

field elements could have magnitude as large as:

$$
q.
$$

But nontrivial algebraic structure frequently forces much stronger cancellation.

We already saw:

$$
|G(\chi)|=\sqrt q
$$

and, in the generic Jacobi-sum case:

$$
\boxed{
|J(\chi,\lambda)|=\sqrt q.
}
$$

This square-root scale is not an accident.

It belongs to a much larger phenomenon.

---

### Hasse's bound

For an elliptic curve:

$$
E/\mathbb F_q,
$$

write:

$$
\#E(\mathbb F_q)
=
q+1-t.
$$

Hasse's theorem states:

$$
\boxed{
|t|
\le
2\sqrt q.
}
$$

Equivalently:

$$
\boxed{
\left|
\#E(\mathbb F_q)
-
(q+1)
\right|
\le
2\sqrt q.
}
$$

For:

$$
y^2=f(x),
$$

where $f$ is the cubic defining an elliptic curve:

$$
t
=
-\sum_x\eta(f(x)).
$$

Thus Hasse's theorem becomes a deep cancellation statement about that quadratic character sum.

---

### Checking the previous example

For our curve over:

$$
\mathbb F_5,
$$

we found:

$$
t=-3.
$$

Hasse gives:

$$
|t|
\le
2\sqrt5.
$$

Numerically:

$$
2\sqrt5
\approx4.472.
$$

Indeed:

$$
3<4.472.
$$

So the computed point count:

$$
9
$$

lies inside the Hasse interval:

$$
5+1-2\sqrt5
\le
\#E(\mathbb F_5)
\le
5+1+2\sqrt5.
$$

---

### Higher genus

For a smooth projective curve $C$ of genus $g$:

$$
\boxed{
\left|
\#C(\mathbb F_q)
-
(q+1)
\right|
\le
2g\sqrt q.
}
$$

This is the curve case of the Weil bounds.

For:

$$
g=1,
$$

we recover Hasse's bound.

The error scale:

$$
\sqrt q
$$

is again the same structural scale already visible in Gauss and Jacobi sums.

---

### Why square-root cancellation matters

Suppose we have:

$$
S
=
\sum_{x\in\mathbb F_q}
u_x
$$

with:

$$
|u_x|\le1.
$$

The trivial estimate gives:

$$
|S|\le q.
$$

A bound of order:

$$
\sqrt q
$$

is dramatically smaller.

It says that the oscillating phases cancel almost completely.

This is one of the most important recurring themes in character-sum theory:

$$
\boxed{
\text{algebraic structure}
\rightarrow
\text{oscillation}
\rightarrow
\text{cancellation}.
}
$$

---

## Computational verification and the role of the archived worksheets

The archived material contains several computational experiments involving:

- roots of unity;
- multiplicative characters;
- Gauss sums;
- Jacobi sums;
- cyclotomic classes;
- correlation tables;
- finite-field circles;
- special elliptic curves.

These are useful experimental records.

But they are better understood as variations of a small number of common mathematical ideas rather than as separate theoretical topics.

---

### Computing a Jacobi sum

Suppose we already have a finite-field character implementation.

A direct algorithm is:

```python
def jacobi_sum(
    field,
    chi,
    lam,
):
    total = 0

    one = field.one()

    for x in field:
        total += (
            chi(x)
            * lam(one - x)
        )

    return total
```

The mathematical definition is almost literally executable:

$$
J(\chi,\lambda)
=
\sum_x
\chi(x)\lambda(1-x).
$$

---

### Numerical verification of the magnitude

If:

$$
\chi,
\lambda,
\chi\lambda
$$

are all nontrivial, we expect:

$$
\boxed{
|J(\chi,\lambda)|
=
\sqrt q.
}
$$

A floating-point test might use:

```python
J = jacobi_sum(
    field,
    chi,
    lam,
)

assert abs(
    abs(J) - sqrt(q)
) < tolerance
```

This is useful as an implementation check.

It is not an exact proof.

---

### Verify the Gauss–Jacobi identity

Given compatible Gauss-sum implementations, test:

```python
left = jacobi_sum(
    field,
    chi,
    lam,
)

right = (
    gauss_sum(field, chi, psi)
    * gauss_sum(field, lam, psi)
    / gauss_sum(
        field,
        chi * lam,
        psi,
    )
)
```

Then compare:

$$
\boxed{
J(\chi,\lambda)
}
$$

with:

$$
\boxed{
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}.
}
$$

This test should only run when:

$$
\chi,
\lambda,
\chi\lambda
$$

satisfy the required nontriviality conditions.

The implementation should enforce the theorem's hypotheses rather than silently applying the formula outside its valid domain.

---

### Exact cyclotomic arithmetic

When character values are represented numerically by complex roots of unity, identities may acquire tiny floating-point errors.

For example:

```text
-1.0000000000000002
+ 4.1e-16j
```

may mathematically mean exactly:

$$
-1.
$$

For exact experimentation, a computer algebra system can represent roots of unity in a cyclotomic field:

$$
\mathbb Q(\zeta_m).
$$

Then Jacobi sums can be manipulated as exact algebraic integers rather than approximate complex numbers.

This is preferable whenever the goal is to verify identities rather than only visualize their geometry.

---

### Point counting by brute force

For small fields, direct enumeration provides a useful reference implementation.

For:

$$
E:
y^2=f(x),
$$

one may count:

```python
count = 1  # point at infinity

for x in field:
    rhs = f(x)

    for y in field:
        if y * y == rhs:
            count += 1
```

This is intentionally inefficient:

$$
O(q^2).
$$

But for small fields it gives a ground truth against which a character-sum implementation can be tested.

---

### Point counting with the quadratic character

A much cleaner method is:

```python
count = q + 1

for x in field:
    count += quadratic_character(
        f(x)
    )
```

because:

$$
\boxed{
\#E(\mathbb F_q)
=
q+1
+
\sum_x
\eta(f(x)).
}
$$

This requires only:

$$
O(q)
$$

character evaluations rather than checking all $q^2$ pairs.

It is still not a modern large-field elliptic-curve point-counting algorithm, but it clearly demonstrates the computational value of the character viewpoint.

---

### What the old worksheets are actually teaching

The repeated experiments can therefore be consolidated into four conceptual operations:

$$
\boxed{
\text{classify multiplicative residue classes},
}
$$

$$
\boxed{
\text{encode them with characters},
}
$$

$$
\boxed{
\text{correlate them with Gauss/Jacobi sums},
}
$$

and:

$$
\boxed{
\text{convert character correlations into counts}.
}
$$

That is the durable mathematical content.

The individual plots and worksheets are computational evidence and provenance for this structure.

---

![Gauss and Jacobi sum computation](/images/mathematics/gauss-jacobi-plot.png)

---

## The structural picture

The article begins with:

$$
\boxed{
J(\chi,\lambda)
=
\sum_x
\chi(x)\lambda(1-x).
}
$$

When:

$$
\chi,
\lambda,
\chi\lambda
$$

are nontrivial:

$$
\boxed{
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}.
}
$$

Therefore:

$$
\boxed{
|J(\chi,\lambda)|
=
\sqrt q.
}
$$

Characters of order $m$ encode the cyclotomic classes:

$$
C_0,\ldots,C_{m-1}.
$$

Jacobi sums then encode correlations between those classes under additive shifts.

Those same character correlations count solutions to equations such as:

$$
x^m+y^m=1.
$$

For curves:

$$
y^2=f(x),
$$

we obtain:

$$
\boxed{
\#C_{\mathrm{aff}}(\mathbb F_q)
=
q
+
\sum_x
\eta(f(x)).
}
$$

For elliptic curves:

$$
\boxed{
\#E(\mathbb F_q)
=
q+1-t,
}
$$

with:

$$
\boxed{
t
=
-
\sum_x
\eta(f(x)).
}
$$

Finally:

$$
\boxed{
|t|\le2\sqrt q.
}
$$

So the complete chain is:

$$
\boxed{
\text{characters}
\rightarrow
\text{Jacobi sums}
\rightarrow
\text{cyclotomic correlations}
\rightarrow
\text{solution counts}
\rightarrow
\text{Frobenius traces}.
}
$$

This is one of the most important conceptual transitions in computational number theory: finite algebraic sums begin to encode geometric information.

---

## Practice and checkpoint

### Exercise 1 — A Jacobi sum

Let:

$$
\eta
$$

be the quadratic character over:

$$
\mathbb F_5.
$$

Compute:

$$
J(\eta,\eta)
=
\sum_{x\in\mathbb F_5}
\eta(x)\eta(1-x).
$$

Compare your answer with:

$$
-\eta(-1).
$$

---

### Exercise 2 — Exceptional case

Suppose:

$$
\lambda=\chi^{-1}.
$$

Why can we not directly use:

$$
J(\chi,\lambda)
=
\frac{
G(\chi)G(\lambda)
}{
G(\chi\lambda)
}
$$

with the ordinary nontrivial Gauss-sum magnitude theorem?

What does:

$$
\chi\lambda
$$

become?

---

### Exercise 3 — Generic magnitude

Assume:

$$
\chi,
\lambda,
\chi\lambda
$$

are all nontrivial.

Use:

$$
|G(\rho)|=\sqrt q
$$

to prove:

$$
|J(\chi,\lambda)|=\sqrt q.
$$

---

### Exercise 4 — Cyclotomic classes

Let:

$$
\mathbb F_{13}^\times
=
\langle g\rangle.
$$

For:

$$
m=3,
$$

describe the three cyclotomic classes:

$$
C_0,
C_1,
C_2.
$$

How many elements does each contain?

---

### Exercise 5 — Character indicator

Let $\chi$ have order $m$.

For:

$$
a\neq0,
$$

prove:

$$
\frac1m
\sum_{j=0}^{m-1}
\chi^j(a)
=
\begin{cases}
1,
&
a\text{ is an }m\text{-th power},
\\
0,
&
\text{otherwise}.
\end{cases}
$$

---

### Exercise 6 — Quadratic root count

Let:

$$
\eta
$$

be the quadratic character.

Verify:

$$
\#\{
y:y^2=a
\}
=
1+\eta(a)
$$

for:

- $a=0$;
- a nonzero square;
- a nonsquare.

---

### Exercise 7 — Finite circle

Over:

$$
\mathbb F_7,
$$

count the solutions of:

$$
x^2+y^2=1.
$$

Compare the direct count with:

$$
7-\eta(-1).
$$

---

### Exercise 8 — Elliptic-curve point count

For:

$$
E:
y^2=x^3+x+1
$$

over:

$$
\mathbb F_5,
$$

verify directly that:

$$
\#E(\mathbb F_5)=9.
$$

Then compute:

$$
t=5+1-9.
$$

Check Hasse's bound.

---

### Exercise 9 — Character sum and Frobenius trace

For:

$$
E:
y^2=f(x),
$$

derive:

$$
t
=
-\sum_x
\eta(f(x))
$$

from:

$$
\#E(\mathbb F_q)
=
q+1-t.
$$

---

### Exercise 10 — Hasse interval

For an elliptic curve over:

$$
\mathbb F_{101},
$$

determine the Hasse interval in which:

$$
\#E(\mathbb F_{101})
$$

must lie.

---

### Exercise 11 — Brute force versus characters

Compare the computational work of:

1. checking all:
   $$
   (x,y)\in\mathbb F_q^2;
   $$
2. evaluating:
   $$
   \eta(f(x))
   $$
   once for every $x$.

What are the respective naive operation counts as functions of $q$?

---

### Exercise 12 — Exact versus numerical Jacobi sums

Compute a Jacobi sum numerically using complex roots of unity.

Then compute the same object in an exact cyclotomic field.

What kinds of numerical artifacts disappear in the exact computation?

---

### Reader checkpoint

You should now be able to explain:

1. What a Jacobi sum is.
2. Why the extension convention at $0$ matters.
3. Why:
   $$
   J(\chi,\lambda)=J(\lambda,\chi).
   $$
4. Why:
   $$
   J(\chi,\varepsilon)=-1
   $$
   for nontrivial $\chi$.
5. Why:
   
   $$
   J(\chi,\chi^{-1})
   =
   -\chi(-1).
   $$

6. Under which hypotheses:
   
   $$
   J(\chi,\lambda)
   =
   \frac{
   G(\chi)G(\lambda)
   }{
   G(\chi\lambda)
   }.
   $$
   
7. Why generic nontrivial Jacobi sums have magnitude:
   $$
   \sqrt q.
   $$
8. What cyclotomic classes are.
9.  How multiplicative characters encode those classes.
10. What classical cyclotomic numbers count.
11. Why Jacobi sums encode cyclotomic correlations.
12. How characters detect $m$-th powers.
13. How power equations can be converted into character sums.
14. Why:
    $$
    \#\{y:y^2=a\}=1+\eta(a).
    $$
15. How to count:
    $$
    x^2+y^2=1
    $$
    with a quadratic character.
16. Why Jacobi sums arise naturally from Fermat-type equations.
17. How:
    $$
    y^2=f(x)
    $$
    leads to a quadratic-character sum.
18. Why the Frobenius trace of an elliptic curve can be expressed as a character sum.
19. What Hasse's bound states.
20. How Hasse's bound fits the broader theme of square-root cancellation.
21. Why character-sum formulas for special curves are not the same as general-purpose Schoof or SEA point counting.
22. Why exact cyclotomic arithmetic is preferable when verifying root-of-unity identities.

Jacobi sums make an important conceptual transition possible.

An expression built from roots of unity:

$$
\sum_x
\chi(x)\lambda(1-x)
$$

can ultimately tell us how many geometric points exist on a curve over a finite field.

That is a remarkable amount of arithmetic information encoded in a finite character correlation.

---

## References and further reading

**Kenneth Ireland and Michael Rosen**,  
*A Classical Introduction to Modern Number Theory.*

A standard source for cyclotomy, Gauss sums, Jacobi sums, and their arithmetic applications.

**Bruce C. Berndt, Ronald J. Evans, and Kenneth S. Williams**,  
*Gauss and Jacobi Sums.*

The specialized reference for explicit identities, evaluations, and the deeper arithmetic of character sums.

**Rudolf Lidl and Harald Niederreiter**,  
*Finite Fields.*

A comprehensive reference for multiplicative characters, cyclotomy, character sums, and finite-field equations.

**André Weil**,  
*On Some Exponential Sums.*

A foundational source for the deep connection between character sums and algebraic geometry over finite fields.

**Joseph H. Silverman**,  
*The Arithmetic of Elliptic Curves.*

A standard reference for elliptic curves, Frobenius, point counting, and the arithmetic-geometric framework behind Hasse's theorem.

**Lawrence C. Washington**,  
*Introduction to Cyclotomic Fields.*

A deeper route into roots of unity, cyclotomic fields, and their arithmetic structure.

---

## Next

The first five articles have now moved through several layers of computational number theory:

$$
\text{arithmetic functions}
$$

$$
\downarrow
$$

$$
\text{prime distribution}
$$

$$
\downarrow
$$

$$
\text{Gaussian integers}
$$

$$
\downarrow
$$

$$
\text{Gauss sums}
$$

$$
\downarrow
$$

$$
\text{Jacobi sums and point counting}.
$$

The next article returns from finite-field character sums to integral arithmetic, but with a much richer object than a single integer.

We study expressions of the form:

$$
\boxed{
ax^2+bxy+cy^2,
}
$$

the **binary quadratic forms**.

Their discriminants, equivalence classes, composition laws, and connections with ideals lead to another major idea:

$$
\boxed{
\text{the class group}.
}
$$

This provides a new way to study representation problems and norm equations, and opens the door toward the arithmetic of quadratic number fields.
