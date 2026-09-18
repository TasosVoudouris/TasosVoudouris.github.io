---
title: "Groups and Modular Group Structures"
description: "A reference on groups, subgroups, modular additive and multiplicative groups, cyclic groups, generators, roots, quadratic residues, Legendre and Jacobi symbols, and the Carmichael function."
pubDate: "2025-05-05"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
tags:
  - "groups"
  - "subgroups"
  - "zn"
  - "units"
  - "cyclic-groups"
  - "quadratic-residues"
  - "euler-theorem"
  - "fermat-little-theorem"
difficulty: "Intermediate"
series: "Elementary Number Theory Reference"
seriesOrder: 4
sourcePath: "experiments/ready-material/groups"
draft: false
---

The previous references developed modular arithmetic primarily as arithmetic on residue classes.

We now change perspective.

Instead of asking only how to compute

$$
a+b\pmod n
$$

or

$$
ab\pmod n,
$$

we ask:

> What algebraic structure do these operations create?

That question leads directly to **groups**.

Groups give us a language for discussing:

- invertible elements,
- repeated operations,
- element orders,
- cyclic behavior,
- generators,
- exponent reduction,
- roots,
- quadratic residues,
- and many of the finite structures used in cryptography.

The same language will later describe Diffie-Hellman groups, elliptic-curve groups, finite fields, subgroup attacks, and discrete-logarithm assumptions.

This article is therefore a bridge:

$$
\boxed{
\text{modular arithmetic}
\rightarrow
\text{group structure}
\rightarrow
\text{cryptographic algebra}.
}
$$

---

## Table of Contents

- [Groups](#groups)
- [Subgroups and normal subgroups](#subgroups-and-normal-subgroups)
- [The additive group $\mathbb Z_n$](#the-additive-group-znmathbb-z_nzn)
- [The multiplicative group of units](#the-multiplicative-group-of-units)
- [Euler's theorem and Fermat's little theorem](#eulers-theorem-and-fermats-little-theorem)
- [Fermat's little theorem](#fermats-little-theorem)
- [Cyclic groups and generators](#cyclic-groups-and-generators)
- [Element order and subgroup structure](#element-order-and-subgroup-structure)
- [When is $\mathbb Z_n^\times$ cyclic?](#when-is-znmathbb-z_ntimeszn-cyclic)
- [Testing whether an element is a generator](#testing-whether-an-element-is-a-generator)
- [Roots in prime fields](#roots-in-prime-fields)
- [Square roots when $p\equiv3\pmod4$](#square-roots-when-p3mod4pequiv3pmod4p3mod4)
- [The general odd-prime case](#the-general-odd-prime-case)
- [Quadratic residues](#quadratic-residues)
- [Quadratic residues form a subgroup](#quadratic-residues-form-a-subgroup)
- [Composite moduli](#composite-moduli)
- [Legendre and Jacobi symbols](#legendre-and-jacobi-symbols)
- [Quadratic reciprocity](#quadratic-reciprocity)
- [Jacobi symbol](#jacobi-symbol)
- [Carmichael numbers](#carmichael-numbers)
- [Korselt's criterion](#korselts-criterion)
- [The Carmichael function](#the-carmichael-function)
- [Computing $\lambda(n)$](#computing-λnlambdanλn)
- [Carmichael numbers through $\lambda(n)$](#carmichael-numbers-through-λnlambdanλn)
- [Computational examples](#computational-examples)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Groups

Let $G$ be a nonempty set equipped with a binary operation

$$
\cdot:G\times G\rightarrow G.
$$

The pair

$$
(G,\cdot)
$$

is a **group** if the following properties hold.

### Associativity

For all

$$
a,b,c\in G,
$$

we require

$$
(ab)c=a(bc).
$$

### Identity

There exists an element

$$
e\in G
$$

such that

$$
ae=ea=a
$$

for every $a\in G$.

### Inverses

For every

$$
a\in G,
$$

there exists an element

$$
a^{-1}\in G
$$

such that

$$
aa^{-1}
=
a^{-1}a
=
e.
$$

Because the operation is defined as

$$
G\times G\rightarrow G,
$$

closure is already built into the statement that it is a binary operation on $G$.

It is nevertheless common in introductory definitions to list closure explicitly:

$$
a,b\in G
\Longrightarrow
ab\in G.
$$

### Abelian groups

If in addition

$$
ab=ba
$$

for every

$$
a,b\in G,
$$

then $G$ is called an **abelian group**.

Many modular groups used in elementary number theory are abelian.

Not every group encountered in mathematics or cryptography is.

---

## Subgroups and normal subgroups

Let $G$ be a group.

A subset

$$
H\subseteq G
$$

is a **subgroup**, written

$$
H\le G,
$$

if $H$ itself forms a group under the same operation.

A useful subgroup criterion is:

$$
\boxed{
H\neq\varnothing
\quad\text{and}\quad
ab^{-1}\in H
\text{ for all }a,b\in H.
}
$$

Equivalently, we can check:

- the identity belongs to $H$,
- $H$ is closed under the group operation,
- every element of $H$ has its inverse in $H$.

Every group contains at least:

$$
\{e\}
$$

and

$$
G
$$

itself as subgroups.

### Normal subgroups

A subgroup

$$
N\le G
$$

is **normal**, written

$$
N\trianglelefteq G,
$$

when:

$$
gNg^{-1}=N
$$

for every

$$
g\in G.
$$

Equivalently,

$$
gng^{-1}\in N
$$

for every $g\in G$ and $n\in N$.

Normal subgroups allow us to construct quotient groups

$$
G/N.
$$

For the modular groups studied in this article, there is an important simplification:

> Every subgroup of an abelian group is normal.

Indeed, if the operation is commutative,

$$
gng^{-1}
=
ngg^{-1}
=
n.
$$

So normality becomes automatic.

We retain the definition because it becomes important later when group structure becomes more general.

---

## The additive group $\mathbb Z_n$

Consider the residue classes modulo $n$:

$$
\mathbb Z_n
=
\{
[0]_n,[1]_n,\ldots,[n-1]_n
\}.
$$

Under addition modulo $n$,

$$
(\mathbb Z_n,+)
$$

forms an abelian group.

The identity is

$$
[0]_n.
$$

The inverse of

$$
[a]_n
$$

is

$$
[-a]_n.
$$

For example, modulo $7$:

$$
[3]_7+[4]_7=[0]_7.
$$

So:

$$
-[3]_7=[4]_7.
$$

### $\mathbb Z_n$ is cyclic under addition

Every element can be generated by repeatedly adding

$$
[1]_n.
$$

Indeed,

$$
[0]_n,
[1]_n,
[2]_n,
\ldots,
[n-1]_n
$$

are exactly the successive multiples of $[1]_n$.

Therefore:

$$
\boxed{
(\mathbb Z_n,+)
=
\langle[1]_n\rangle.
}
$$

So the additive group modulo $n$ is always cyclic.

Its order is:

$$
|\mathbb Z_n|=n.
$$

---

## The multiplicative group of units

Multiplication behaves differently.

The full set

$$
\mathbb Z_n
$$

is generally **not** a group under multiplication because not every element has a multiplicative inverse.

The invertible elements form:

$$
\boxed{
\mathbb Z_n^\times
=
\{
[a]_n:
\gcd(a,n)=1
\}.
}
$$

This is the **group of units modulo $n$**.

Its operation is multiplication modulo $n$.

The identity is:

$$
[1]_n.
$$

Every element has a modular inverse by construction.

The number of elements is Euler's totient:

$$
\boxed{
|\mathbb Z_n^\times|
=
\varphi(n).
}
$$

We will study $\varphi(n)$ in detail in the next reference article.

### Example: modulo $10$

The elements coprime to $10$ are:

$$
1,3,7,9.
$$

Therefore:

$$
\mathbb Z_{10}^{\times}
=
\{
[1],[3],[7],[9]
\}.
$$

And:

$$
|\mathbb Z_{10}^{\times}|
=
4.
$$

Indeed:

$$
\varphi(10)=4.
$$

### Prime modulus

If $p$ is prime, then every nonzero residue is coprime to $p$.

Therefore:

$$
\boxed{
\mathbb Z_p^\times
=
\{
[1],[2],\ldots,[p-1]
\}.
}
$$

Its order is:

$$
|\mathbb Z_p^\times|
=
p-1.
$$

Since $\mathbb Z_p$ is a field when $p$ is prime, this multiplicative group is also commonly written:

$$
\mathbb F_p^\times.
$$

---

## Euler's theorem and Fermat's little theorem

The finite-group viewpoint makes classical number-theoretic exponentiation results much easier to understand.

### Euler's theorem

If

$$
\gcd(a,n)=1,
$$

then $a$ belongs to:

$$
\mathbb Z_n^\times.
$$

Since:

$$
|\mathbb Z_n^\times|
=
\varphi(n),
$$

Lagrange's theorem implies:

$$
\boxed{
a^{\varphi(n)}
\equiv1\pmod n.
}
$$

This is **Euler's theorem**.

The coprimality assumption is essential.

The theorem is a statement about the units modulo $n$, not arbitrary elements of $\mathbb Z_n$.

### Exponent reduction

Suppose:

$$
a\in\mathbb Z_n^\times
$$

and:

$$
r\equiv s\pmod{\varphi(n)}.
$$

Then:

$$
r-s=k\varphi(n)
$$

for some integer $k$.

Using Euler's theorem:

$$
a^{r-s}
=
a^{k\varphi(n)}
\equiv1\pmod n,
$$

and therefore, with the usual care about nonnegative exponents,

$$
a^r\equiv a^s\pmod n.
$$

So exponent reduction modulo $\varphi(n)$ is justified **for units**.

It is not a universal rule for arbitrary bases modulo a composite $n$.

Even more precisely, exponent reduction can often be performed modulo the element order:

$$
\operatorname{ord}_n(a),
$$

which may be much smaller than $\varphi(n)$.

---

## Fermat's little theorem

Let $p$ be prime.

Then:

$$
\varphi(p)=p-1.
$$

Euler's theorem therefore becomes:

$$
\boxed{
a^{p-1}
\equiv1\pmod p
}
$$

for every:

$$
a\not\equiv0\pmod p.
$$

This is **Fermat's little theorem**.

Multiplying by $a$ gives the equivalent form:

$$
\boxed{
a^p\equiv a\pmod p
}
$$

for every integer $a$.

This second form also includes:

$$
a\equiv0\pmod p.
$$

So we should distinguish the two statements carefully:

$$
a^{p-1}\equiv1\pmod p
$$

requires:

$$
p\nmid a,
$$

whereas:

$$
a^p\equiv a\pmod p
$$

holds for all integers $a$.

---

## Cyclic groups and generators

A group $G$ is **cyclic** if there exists some element

$$
g\in G
$$

such that every element of $G$ is a power of $g$.

We write:

$$
\boxed{
G=\langle g\rangle.
}
$$

The element $g$ is called a **generator**.

If:

$$
|G|=m,
$$

then a generator produces:

$$
G
=
\{
e,g,g^2,\ldots,g^{m-1}
\}.
$$

and:

$$
g^m=e.
$$

### Example: $\mathbb Z_{7}^{\times}$

Because $7$ is prime,

$$
|\mathbb Z_7^\times|
=
6.
$$

Take:

$$
g=3.
$$

Its powers are:

$$
3^1\equiv3\pmod7,
$$

$$
3^2\equiv2\pmod7,
$$

$$
3^3\equiv6\pmod7,
$$

$$
3^4\equiv4\pmod7,
$$

$$
3^5\equiv5\pmod7,
$$

$$
3^6\equiv1\pmod7.
$$

We encountered every nonzero residue:

$$
1,2,3,4,5,6.
$$

Therefore:

$$
\boxed{
\mathbb Z_7^\times
=
\langle3\rangle.
}
$$

So $3$ is a generator.

---

## Element order and subgroup structure

For:

$$
a\in G,
$$

the **order of $a$** is the smallest positive integer $t$ satisfying:

$$
a^t=e.
$$

For multiplication modulo $n$:

$$
\boxed{
\operatorname{ord}_n(a)
=
\min
\{
t>0:
a^t\equiv1\pmod n
\}.
}
$$

The powers of $a$ generate a cyclic subgroup:

$$
\langle a\rangle.
$$

Its size is exactly:

$$
|\langle a\rangle|
=
\operatorname{ord}_n(a).
$$

By Lagrange's theorem:

$$
\boxed{
\operatorname{ord}_n(a)
\mid
|\mathbb Z_n^\times|
=
\varphi(n).
}
$$

This is one of the most important distinctions in finite-group cryptography:

$$
\boxed{
\text{order of the ambient group}
\neq
\text{order of a particular element}.
}
$$

If:

$$
\operatorname{ord}_n(g)
=
\varphi(n),
$$

then $g$ generates the entire multiplicative group.

---

## When is $\mathbb Z_n^\times$ cyclic?

Unlike the additive group $\mathbb Z_n$, the multiplicative group of units is not always cyclic.

For $n>1$,

$$
\mathbb Z_n^\times
$$

is cyclic precisely when:

$$
\boxed{
n\in
\{
2,\,
4,\,
p^k,\,
2p^k
\},
}
$$

where $p$ is an odd prime and $k\ge1$.

In particular, when $p$ is prime:

$$
\boxed{
\mathbb Z_p^\times
\text{ is cyclic}.
}
$$

A generator of

$$
\mathbb Z_p^\times
$$

is traditionally called a **primitive root modulo $p$**.

### Number of generators

Suppose a cyclic group $G$ has order $m$ and:

$$
G=\langle g\rangle.
$$

Then:

$$
g^i
$$

is also a generator exactly when:

$$
\gcd(i,m)=1.
$$

Therefore a cyclic group of order $m$ has:

$$
\boxed{
\varphi(m)
}
$$

generators.

For:

$$
\mathbb Z_p^\times,
$$

where the group order is $p-1$, the number of primitive roots is:

$$
\varphi(p-1).
$$

---

## Testing whether an element is a generator

Suppose $G$ is cyclic with known order:

$$
|G|=m.
$$

Let the distinct prime divisors of $m$ be:

$$
q_1,\ldots,q_r.
$$

Then $g$ has order $m$ if and only if:

$$
\boxed{
g^{m/q_i}\neq e
}
$$

for every prime divisor $q_i\mid m$.

For:

$$
\mathbb Z_p^\times,
$$

we know:

$$
m=p-1.
$$

So $g$ is a primitive root modulo $p$ exactly when:

$$
g^{(p-1)/q}
\not\equiv1\pmod p
$$

for every prime divisor:

$$
q\mid(p-1).
$$

This gives a practical generator test once the factorization of $p-1$ is known.

---

## Roots in prime fields

Now consider:

$$
\mathbb F_p^\times
$$

for prime $p$.

Suppose we want to solve:

$$
x^e=a.
$$

Equivalently:

$$
x^e\equiv a\pmod p.
$$

The exponentiation map:

$$
x\longmapsto x^e
$$

behaves especially cleanly when:

$$
\gcd(e,p-1)=1.
$$

In that case $e$ has an inverse modulo $p-1$.

Let:

$$
d
\equiv
e^{-1}
\pmod{p-1}.
$$

Then:

$$
ed
=
1+k(p-1)
$$

for some integer $k$.

For nonzero $a$,

$$
\left(a^d\right)^e
=
a^{de}
=
a^{1+k(p-1)}.
$$

Using Fermat's little theorem:

$$
a^{p-1}\equiv1\pmod p,
$$

we obtain:

$$
a^{de}
\equiv
a
\pmod p.
$$

Therefore:

$$
\boxed{
x=a^d
}
$$

is the unique $e$-th root of $a$ in $\mathbb F_p^\times$.

So exponent inversion is really group-order arithmetic.

---

## Square roots when $p\equiv3\pmod4$

Suppose $p$ is an odd prime satisfying:

$$
p\equiv3\pmod4.
$$

Let $a$ be a **quadratic residue modulo $p$**.

Then a square root is:

$$
\boxed{
x
\equiv
a^{(p+1)/4}
\pmod p.
}
$$

Why?

Since $a$ is a quadratic residue, Euler's criterion gives:

$$
a^{(p-1)/2}
\equiv1\pmod p.
$$

Therefore:

$$
\begin{aligned}
x^2
&=
a^{(p+1)/2}\\
&=
a^{(p-1)/2}a\\
&\equiv
a
\pmod p.
\end{aligned}
$$

The quadratic-residue assumption is essential.

The formula is not a universal square-root formula for arbitrary $a$.

### Example

Take:

$$
p=11,
\qquad
a=9.
$$

Since:

$$
11\equiv3\pmod4,
$$

compute:

$$
x
=
9^{(11+1)/4}
=
9^3
\pmod{11}.
$$

This gives:

$$
x=3.
$$

Indeed:

$$
3^2\equiv9\pmod{11}.
$$

The second root is:

$$
-3\equiv8\pmod{11}.
$$

And:

$$
8^2\equiv9\pmod{11}.
$$

---

## The general odd-prime case

When:

$$
p\equiv1\pmod4,
$$

the previous shortcut does not apply directly.

A standard general algorithm for extracting square roots modulo odd primes is **Tonelli-Shanks**.

Given an odd prime $p$ and a known quadratic residue $a$, Tonelli-Shanks computes:

$$
x^2\equiv a\pmod p.
$$

We do not need its full derivation in this reference article.

The important structural lesson is that square-root extraction depends on the multiplicative structure of:

$$
\mathbb F_p^\times.
$$

---

## Quadratic residues

Let $n>1$.

Among the units modulo $n$, define the set of quadratic residues:

$$
Q_n
=
\{
x^2\bmod n:
x\in\mathbb Z_n^\times
\}.
$$

An element:

$$
a\in\mathbb Z_n^\times
$$

is a **quadratic residue modulo $n$** if:

$$
x^2\equiv a\pmod n
$$

has a solution.

Otherwise, $a$ is a **quadratic non-residue among the units**.

### Odd prime modulus

Let $p$ be an odd prime.

Then:

$$
|\mathbb Z_p^\times|
=
p-1.
$$

Exactly half of the nonzero elements are quadratic residues:

$$
\boxed{
|Q_p|
=
\frac{p-1}{2}.
}
$$

The other half are non-residues.

Every nonzero quadratic residue has exactly two square roots:

$$
x
$$

and:

$$
-x.
$$

They are distinct because $p$ is odd.

### Example modulo $11$

The nonzero squares are:

$$
1^2\equiv1,
$$

$$
2^2\equiv4,
$$

$$
3^2\equiv9,
$$

$$
4^2\equiv5,
$$

$$
5^2\equiv3
\pmod{11}.
$$

The remaining squares repeat these values.

Thus:

$$
\boxed{
Q_{11}
=
\{
1,3,4,5,9
\}.
}
$$

There are:

$$
\frac{11-1}{2}=5
$$

of them.

---

## Quadratic residues form a subgroup

For odd prime $p$,

$$
Q_p
$$

forms a subgroup of:

$$
\mathbb F_p^\times.
$$

Its index is $2$.

That means:

$$
[\mathbb F_p^\times:Q_p]=2.
$$

The familiar multiplication rules follow:

```text
QR × QR = QR

QR × NR = NR

NR × NR = QR
```

These are not arbitrary mnemonic rules.

They arise because a subgroup of index $2$ divides the group into exactly two cosets.

This becomes especially clear once we introduce the Legendre symbol.

---

## Composite moduli

Now let:

$$
n=pq
$$

for two distinct odd primes.

By CRT:

$$
\mathbb Z_n^\times
\cong
\mathbb Z_p^\times
\times
\mathbb Z_q^\times.
$$

Therefore:

$$
\varphi(n)
=
(p-1)(q-1).
$$

For a unit to be a quadratic residue modulo $n$, it must be a quadratic residue modulo both $p$ and $q$.

Hence:

$$
\boxed{
|Q_n|
=
\frac{(p-1)(q-1)}{4}.
}
$$

Every unit quadratic residue has four square roots modulo $pq$:

$$
2\text{ choices modulo }p
\times
2\text{ choices modulo }q.
$$

CRT combines these into:

$$
2^2=4
$$

distinct roots modulo $n$.

More generally, if:

$$
n
=
p_1^{e_1}\cdots p_k^{e_k}
$$

is a product of powers of distinct odd primes, then a unit quadratic residue has:

$$
\boxed{
2^k
}
$$

square roots modulo $n$.

This root multiplicity is a consequence of CRT decomposition.

The cryptographic **quadratic residuosity problem**, however, is not difficult merely because several roots exist. Its hardness concerns deciding whether certain elements are quadratic residues modulo appropriately structured composite moduli when the factorization is hidden.

---

## Legendre and Jacobi symbols

Quadratic residuosity occurs so frequently that number theory provides compact symbols for reasoning about it.

### Legendre symbol

Let $p$ be an odd prime.

The **Legendre symbol**

$$
\left(\frac ap\right)
$$

is defined by:

$$
\boxed{
\left(\frac ap\right)
=
\begin{cases}
0,
&
p\mid a,\\[4pt]
1,
&
a\not\equiv0\pmod p
\text{ and }a\text{ is a quadratic residue},\\[4pt]
-1,
&
a\text{ is a quadratic non-residue}.
\end{cases}
}
$$

### Euler's criterion

For:

$$
p\nmid a,
$$

Euler's criterion states:

$$
\boxed{
a^{(p-1)/2}
\equiv
\left(\frac ap\right)
\pmod p.
}
$$

The right-hand side is interpreted modulo $p$, so:

$$
-1
$$

corresponds to:

$$
p-1.
$$

Thus one modular exponentiation can distinguish a residue from a non-residue modulo a prime.

### Multiplicativity

The Legendre symbol satisfies:

$$
\boxed{
\left(\frac{ab}{p}\right)
=
\left(\frac ap\right)
\left(\frac bp\right).
}
$$

This exactly reflects the:

```text
QR × QR
QR × NR
NR × NR
```

multiplication pattern.

### Special values

For odd prime $p$:

$$
\boxed{
\left(\frac{-1}{p}\right)
=
(-1)^{(p-1)/2}.
}
$$

Thus:

$$
\left(\frac{-1}{p}\right)=1
\iff
p\equiv1\pmod4.
$$

Also:

$$
\boxed{
\left(\frac2p\right)
=
(-1)^{(p^2-1)/8}.
}
$$

Therefore:

$$
\left(\frac2p\right)=1
$$

exactly when:

$$
p\equiv\pm1\pmod8.
$$

---

## Quadratic reciprocity

For distinct odd primes $p$ and $q$:

$$
\boxed{
\left(\frac pq\right)
\left(\frac qp\right)
=
(-1)^{
\frac{p-1}{2}
\frac{q-1}{2}
}.
}
$$

Equivalently, if at least one of $p$ or $q$ is congruent to $1\pmod4$,

$$
\left(\frac pq\right)
=
\left(\frac qp\right).
$$

If both satisfy:

$$
p\equiv q\equiv3\pmod4,
$$

then:

$$
\left(\frac pq\right)
=
-
\left(\frac qp\right).
$$

Quadratic reciprocity is one of the central theorems of elementary number theory.

Here we record it primarily because it leads naturally to efficient computation of residue symbols.

---

## Jacobi symbol

Let $n$ be an odd positive integer with prime factorization:

$$
n
=
\prod_{i=1}^{k}
p_i^{e_i}.
$$

The **Jacobi symbol** is defined as:

$$
\boxed{
\left(\frac an\right)
=
\prod_{i=1}^{k}
\left(\frac{a}{p_i}\right)^{e_i}.
}
$$

For prime denominator $n=p$, the Jacobi symbol is simply the Legendre symbol.

For composite $n$, however, there is an important difference.

> A Jacobi symbol of $1$ does **not** imply that $a$ is a quadratic residue modulo $n$.

### Example

Take:

$$
a=2,
\qquad
n=15.
$$

Since:

$$
15=3\cdot5,
$$

we have:

$$
\left(\frac2{15}\right)
=
\left(\frac23\right)
\left(\frac25\right).
$$

Now:

$$
\left(\frac23\right)=-1
$$

and:

$$
\left(\frac25\right)=-1.
$$

Therefore:

$$
\boxed{
\left(\frac2{15}\right)=1.
}
$$

Yet $2$ is **not** a square modulo $15$.

So:

$$
\boxed{
\text{Jacobi}=1
\not\Rightarrow
\text{quadratic residue}
}
$$

when the modulus is composite.

This distinction becomes important in quadratic-residuosity-based cryptography and primality testing.

---

## Carmichael numbers

Fermat's little theorem tells us that if $p$ is prime and:

$$
\gcd(a,p)=1,
$$

then:

$$
a^{p-1}\equiv1\pmod p.
$$

It is tempting to reverse this logic and use it as a primality test.

Unfortunately, some composite integers imitate this behavior extremely well.

A **Carmichael number** is a composite integer $n$ satisfying:

$$
\boxed{
a^{n-1}
\equiv1
\pmod n
}
$$

for every:

$$
\gcd(a,n)=1.
$$

So Carmichael numbers are Fermat pseudoprimes to **every base coprime to the modulus**.

The smallest example is:

$$
\boxed{
561=3\cdot11\cdot17.
}
$$

Despite being composite:

$$
a^{560}
\equiv1
\pmod{561}
$$

for every:

$$
\gcd(a,561)=1.
$$

---

## Korselt's criterion

A composite integer $n$ is a Carmichael number if and only if:

1. $n$ is square-free;
2. for every prime divisor $p\mid n$,

$$
\boxed{
p-1\mid n-1.
}
$$

For:

$$
561=3\cdot11\cdot17,
$$

the number is square-free.

Also:

$$
3-1=2\mid560,
$$

$$
11-1=10\mid560,
$$

and:

$$
17-1=16\mid560.
$$

Therefore $561$ satisfies Korselt's criterion.

Every Carmichael number is the product of at least three distinct primes.

This explains why naive Fermat primality testing is insufficient and motivates stronger tests such as Miller-Rabin.

---

## The Carmichael function

Euler's theorem gives the universal exponent:

$$
\varphi(n)
$$

for the unit group:

$$
a^{\varphi(n)}
\equiv1\pmod n.
$$

But $\varphi(n)$ is not always the smallest positive exponent that works for **every** unit.

The **Carmichael function**

$$
\lambda(n)
$$

is defined as the smallest positive integer such that:

$$
\boxed{
a^{\lambda(n)}
\equiv1\pmod n
}
$$

for every:

$$
a\in\mathbb Z_n^\times.
$$

Equivalently:

$$
\lambda(n)
$$

is the **exponent** of the finite group:

$$
\mathbb Z_n^\times.
$$

Therefore:

$$
\boxed{
\lambda(n)
=
\operatorname{lcm}
\{
\operatorname{ord}_n(a):
a\in\mathbb Z_n^\times
\}.
}
$$

This gives the useful chain:

$$
\boxed{
\operatorname{ord}_n(a)
\mid
\lambda(n)
\mid
\varphi(n).
}
$$

---

## Computing $\lambda(n)$

If:

$$
n
=
\prod_i
p_i^{\alpha_i},
$$

then:

$$
\boxed{
\lambda(n)
=
\operatorname{lcm}
\left(
\lambda(p_1^{\alpha_1}),
\ldots,
\lambda(p_k^{\alpha_k})
\right).
}
$$

For odd prime powers:

$$
\lambda(p^\alpha)
=
\varphi(p^\alpha)
=
p^{\alpha-1}(p-1).
$$

For powers of two:

$$
\lambda(2)=1,
$$

$$
\lambda(4)=2,
$$

and for:

$$
\alpha\ge3,
$$

$$
\boxed{
\lambda(2^\alpha)
=
2^{\alpha-2}
=
\frac12\varphi(2^\alpha).
}
$$

### Example: $n=15$

Since:

$$
15=3\cdot5,
$$

we get:

$$
\lambda(3)=2,
$$

and:

$$
\lambda(5)=4.
$$

Therefore:

$$
\lambda(15)
=
\operatorname{lcm}(2,4)
=
4.
$$

But:

$$
\varphi(15)=8.
$$

So:

$$
\boxed{
\lambda(15)=4<8=\varphi(15).
}
$$

Euler's theorem guarantees:

$$
a^8\equiv1\pmod{15},
$$

but in fact the stronger statement:

$$
a^4\equiv1\pmod{15}
$$

already holds for every unit.

This is why $\lambda(n)$ gives a more precise universal exponent.

---

## Carmichael numbers through $\lambda(n)$

The Carmichael function also gives a clean view of Carmichael numbers.

A composite $n$ is Carmichael when:

$$
a^{n-1}
\equiv1\pmod n
$$

for every unit.

That means the exponent of the unit group must divide $n-1$:

$$
\boxed{
\lambda(n)\mid n-1.
}
$$

For $561$:

$$
\lambda(561)
=
\operatorname{lcm}
(
2,10,16
)
=
80.
$$

And:

$$
80\mid560.
$$

Therefore every unit satisfies:

$$
a^{80}\equiv1\pmod{561},
$$

and hence:

$$
a^{560}
=
(a^{80})^7
\equiv1\pmod{561}.
$$

This gives a group-theoretic explanation for the Fermat-like behavior of $561$.

---

## Computational examples

### Additive group

In SageMath:

```python
R = Integers(10)

for a in R:
    print(a)
```

The additive structure contains all ten residue classes.

The element:

```python
R(1)
```

generates the additive group.

### Multiplicative order

```python
R = Integers(10)

a = R(3)

print(
    a.multiplicative_order()
)
```

Output:

```text
4
```

Indeed:

```python
[
    a**i
    for i in range(1, 5)
]
```

cycles through the complete unit group.

### Generator test modulo a prime

For a prime $p$, a simple SageMath generator test is:

```python
def is_generator_mod_prime(g, p):
    if not is_prime(p):
        raise ValueError(
            "p must be prime"
        )

    order = p - 1

    for q, _ in factor(order):
        q = int(q)

        if pow(
            int(g),
            order // q,
            int(p),
        ) == 1:
            return False

    return True
```

For:

```python
p = 17
```

we can test:

```python
for g in range(1, p):
    if is_generator_mod_prime(g, p):
        print(g)
```

Every returned value has order:

$$
16.
$$

### Primitive root

SageMath can also compute one directly:

```python
p = 17

g = primitive_root(p)

print(g)
```

Then:

```python
[
    pow(g, i, p)
    for i in range(1, p)
]
```

runs through every nonzero residue modulo $17$.

The library call is convenient.

The generator criterion explains why it works.

---

## Why this matters in cryptography

Groups provide the language behind a large fraction of public-key cryptography.

### Diffie-Hellman

A typical finite-group Diffie-Hellman setting chooses a cyclic group:

$$
G=\langle g\rangle
$$

of known large order $q$.

Secret exponents live modulo $q$.

Public values have the form:

$$
g^a.
$$

The security problem asks whether recovering $a$ from:

$$
g^a
$$

is computationally difficult.

### Element order matters

It is not sufficient for the ambient structure to be large.

The chosen element must also lie in the intended subgroup and have the intended order.

If an attacker can force computations into a small subgroup generated by an element $T$ of order $s$, then:

$$
T^d
=
T^{d\bmod s}.
$$

That is the mathematical core of small-subgroup attacks.

### RSA

RSA uses the multiplicative structure of:

$$
\mathbb Z_N^\times.
$$

Euler's theorem explains one form of the exponent cycle.

The Carmichael function gives the more precise universal exponent:

$$
\lambda(N).
$$

This is why modern RSA key relations are naturally expressed as:

$$
ed\equiv1\pmod{\lambda(N)}.
$$

### Quadratic residuosity

Quadratic residues, Legendre symbols, Jacobi symbols, and square-root structure appear in:

- primality testing,
- residuosity assumptions,
- probabilistic encryption constructions,
- integer-factorization-related cryptography.

The common theme is that cryptographic security frequently depends not merely on arithmetic modulo $n$, but on the **structure of particular groups and subgroups inside that arithmetic**.

---

## Practice and checkpoint

### Exercise 1 — Additive group

Show that:

$$
(\mathbb Z_8,+)
$$

is cyclic.

Which elements generate the full additive group?

Hint: determine the additive order of each residue.

### Exercise 2 — Units

List:

$$
\mathbb Z_{15}^{\times}.
$$

Verify that every listed element is coprime to $15$.

How many elements are there?

### Exercise 3 — Element orders

Compute the order of each element of:

$$
\mathbb Z_{10}^{\times}
=
\{1,3,7,9\}.
$$

Which elements generate the whole group?

### Exercise 4 — Noncyclic unit group

Study:

$$
\mathbb Z_8^\times
=
\{1,3,5,7\}.
$$

Verify:

$$
3^2\equiv5^2\equiv7^2\equiv1\pmod8.
$$

Why can this group not be cyclic?

### Exercise 5 — Primitive root

Find the powers of $3$ modulo $7$.

Verify:

$$
\operatorname{ord}_7(3)=6.
$$

Why does that prove that $3$ is a generator?

### Exercise 6 — Square roots

Find both square roots of:

$$
9\pmod{11}.
$$

Verify them directly.

### Exercise 7 — Quadratic residues

List all nonzero quadratic residues modulo $13$.

Confirm that there are:

$$
\frac{13-1}{2}=6.
$$

### Exercise 8 — Legendre symbol

Evaluate:

$$
\left(\frac{-1}{11}\right)
$$

without listing squares.

Then verify the result by direct computation.

### Exercise 9 — Jacobi warning

Verify:

$$
\left(\frac2{15}\right)=1.
$$

Then enumerate the squares modulo $15$ and confirm that $2$ is not a quadratic residue.

### Exercise 10 — Carmichael number

Verify Korselt's criterion for:

$$
561=3\cdot11\cdot17.
$$

Then compute:

$$
\lambda(561).
$$

Explain why:

$$
\lambda(561)\mid560
$$

forces every unit to pass the Fermat exponent $560$.

### Reader checkpoint

You should now be able to explain:

1. The four group axioms.
2. What a subgroup is.
3. Why every subgroup of an abelian group is normal.
4. Why
   $$
   (\mathbb Z_n,+)
   $$
   is always cyclic.
5. Why the full
   $$
   \mathbb Z_n
   $$
   is generally not a multiplicative group.
6. Why
   $$
   \mathbb Z_n^\times
   $$
   contains exactly the invertible residues.
7. The difference between group order and element order.
8. What it means for an element to generate a cyclic group.
9. Why
   $$
   \operatorname{ord}_n(a)\mid\varphi(n).
   $$
10. Why exponent reduction modulo $\varphi(n)$ requires a unit.
11. How Fermat's little theorem arises from Euler's theorem.
12. When the formula
    $$
    a^{(p+1)/4}
    $$
    gives a square root.
13. Why exactly half of
    $$
    \mathbb F_p^\times
    $$
    are quadratic residues.
14. Why Jacobi symbol $1$ does not necessarily imply quadratic residuosity.
15. What a Carmichael number is.
16. What
    $$
    \lambda(n)
    $$
    measures.
17. Why
    $$
    \operatorname{ord}_n(a)
    \mid
    \lambda(n)
    \mid
    \varphi(n).
    $$

If these distinctions are clear, then the modular arithmetic developed earlier has now become genuine finite-group theory.

---

## References and further reading

**Joseph A. Gallian**,  
*Contemporary Abstract Algebra.*

A particularly accessible introduction to groups, cyclic groups, subgroups, orders, and generators.

**David S. Dummit and Richard M. Foote**,  
*Abstract Algebra.*

A deeper reference for group structure, quotient groups, homomorphisms, and finite algebraic systems.

**Kenneth H. Rosen**,  
*Elementary Number Theory and Its Applications.*

Useful for multiplicative groups, primitive roots, quadratic residues, and classical modular number theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Especially valuable for connecting finite groups and number-theoretic structure with efficient algorithms.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Connects group structure, orders, finite fields, modular exponentiation, and quadratic residues directly to cryptographic constructions.

---

## Next

We have repeatedly used one quantity without yet studying it systematically:

$$
\varphi(n).
$$

We know that:

$$
|\mathbb Z_n^\times|
=
\varphi(n),
$$

and that:

$$
\operatorname{ord}_n(a)
\mid
\varphi(n).
$$

We have also seen:

$$
a^{\varphi(n)}
\equiv1\pmod n
$$

for units.

The next reference article therefore studies exactly what this function measures, how to compute it from the factorization of $n$, why it is multiplicative, and how group order and element order interact.

**Next: Euler's Totient Function and Element Orders.**
