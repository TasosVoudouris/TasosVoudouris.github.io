---
title: "Abstract Algebra I: Groups, Subgroups, Cyclic Structure, and Element Order"
description: "A rigorous foundation for groups, subgroups, cyclic groups, generators, element order, and the recurring algebraic examples used throughout cryptography."
pubDate: "2025-03-19"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Abstract Algebra"
tags:
  - "groups"
  - "subgroups"
  - "cyclic-groups"
  - "element-order"
  - "generators"
difficulty: "Introductory"
status: "Reference"
series: "Abstract Algebra Foundations"
seriesOrder: 1
sourcePath: "experiments/mathematics/abstract-algebra"
draft: false
---

A group is one of the first algebraic structures in which an operation can be performed consistently, has a neutral element, and can always be undone.

That compact collection of properties is enough to formalize many objects that appear repeatedly throughout mathematics and cryptography:

- integers under addition,
- invertible residues under modular multiplication,
- permutations under composition,
- matrices under multiplication,
- points on elliptic curves under the elliptic-curve group law.

The purpose of this article is not merely to memorize the four group axioms.

We want to understand what those axioms immediately force, how subgroups arise, why cyclic groups are especially simple, and why the **order of an element** becomes an important structural quantity later in finite-group cryptography.

The main progression is:

\[
\boxed{
\text{group}
\rightarrow
\text{subgroup}
\rightarrow
\text{generated subgroup}
\rightarrow
\text{cyclic group}
\rightarrow
\text{element order}.
}
\]

---

## 1. Groups

Let \(G\) be a nonempty set and let

\[
\star:G\times G\rightarrow G
\]

be a binary operation.

The pair

\[
(G,\star)
\]

is called a **group** if the following properties hold for every

\[
a,b,c\in G.
\]

### Closure

The result of combining two elements remains in the set:

\[
a\star b\in G.
\]

Strictly speaking, closure is already encoded in the statement that

\[
\star:G\times G\rightarrow G
\]

is a binary operation on \(G\), but it is useful to keep the property explicit when first learning the definition.

### Associativity

\[
(a\star b)\star c
=
a\star(b\star c).
\]

Associativity tells us that expressions such as

\[
a\star b\star c
\]

do not require us to specify parentheses.

It does **not** say that the order of the elements may be changed.

### Identity

There exists an element

\[
e\in G
\]

such that:

\[
\boxed{
e\star a
=
a\star e
=
a
}
\]

for every \(a\in G\).

The identity leaves every element unchanged.

A common transcription error is to write:

\[
e\star a=e,
\]

which is not the group identity property.

### Inverses

For every:

\[
a\in G,
\]

there exists an element:

\[
a^{-1}\in G
\]

such that:

\[
a\star a^{-1}
=
a^{-1}\star a
=
e.
\]

The inverse undoes the effect of \(a\).

---

## 2. Abelian and nonabelian groups

A group \(G\) is **abelian** if:

\[
a\star b
=
b\star a
\]

for every:

\[
a,b\in G.
\]

Commutativity is an additional property.

It is **not** one of the group axioms.

This distinction becomes important very quickly.

For example:

\[
(\mathbb Z,+)
\]

is abelian because:

\[
a+b=b+a.
\]

But permutation groups such as:

\[
S_3
\]

are generally nonabelian:

\[
\sigma\tau
\neq
\tau\sigma.
\]

So associativity and commutativity should never be confused:

\[
\boxed{
(ab)c=a(bc)
}
\]

does not imply:

\[
\boxed{
ab=ba.
}
\]

---

## 3. Multiplicative and additive notation

Group theory uses two common notational conventions.

### Multiplicative notation

We write:

\[
ab
\]

instead of:

\[
a\star b.
\]

The identity is:

\[
e,
\]

the inverse of \(a\) is:

\[
a^{-1},
\]

and repeated multiplication gives:

\[
a^n.
\]

### Additive notation

For naturally additive groups, we write:

\[
a+b.
\]

The identity is:

\[
0,
\]

the inverse of \(a\) is:

\[
-a,
\]

and repeated addition gives:

\[
na.
\]

For example:

\[
3a
=
a+a+a.
\]

The underlying theory is the same.

Only the notation changes.

---

## 4. First consequences of the group axioms

Several familiar properties are consequences of the axioms.

They do not need to be assumed separately.

### The identity is unique

Suppose \(e\) and \(e'\) are both identity elements.

Then:

\[
e
=
e\star e'
=
e'.
\]

Therefore the identity is unique.

So it makes sense to speak of **the** identity element.

---

### Inverses are unique

Suppose \(b\) and \(c\) are both inverses of \(a\).

Then:

\[
ab=e
\]

and:

\[
ac=e.
\]

Now:

\[
\begin{aligned}
b
&=
b e\\
&=
b(ac)\\
&=
(ba)c\\
&=
ec\\
&=
c.
\end{aligned}
\]

Therefore every group element has exactly one inverse.

---

### The inverse of an inverse

Since:

\[
aa^{-1}=e,
\]

the element \(a\) is the inverse of \(a^{-1}\).

Thus:

\[
\boxed{
(a^{-1})^{-1}=a.
}
\]

---

### Inverse of a product

For two elements \(a,b\in G\):

\[
\boxed{
(ab)^{-1}
=
b^{-1}a^{-1}.
}
\]

The order is reversed.

Indeed:

\[
(ab)(b^{-1}a^{-1})
=
a(bb^{-1})a^{-1}
=
aea^{-1}
=
e.
\]

Likewise:

\[
(b^{-1}a^{-1})(ab)=e.
\]

This reversal matters particularly in nonabelian groups.

---

## 5. Cancellation

Groups satisfy both left and right cancellation.

If:

\[
ax=ay,
\]

multiply both sides on the left by \(a^{-1}\):

\[
a^{-1}ax
=
a^{-1}ay.
\]

Therefore:

\[
x=y.
\]

Likewise:

\[
xa=ya
\]

implies:

\[
x=y.
\]

Thus:

\[
\boxed{
ax=ay
\Longrightarrow
x=y
}
\]

and:

\[
\boxed{
xa=ya
\Longrightarrow
x=y.
}
\]

Cancellation follows from the existence of inverses.

It is not an independent axiom.

---

## 6. Solving elementary group equations

The group axioms allow us to solve equations abstractly.

Suppose:

\[
ax=b.
\]

Multiply on the left by \(a^{-1}\):

\[
x
=
a^{-1}b.
\]

Similarly, if:

\[
xa=b,
\]

then:

\[
x
=
ba^{-1}.
\]

Notice the difference.

In a nonabelian group:

\[
a^{-1}b
\]

and:

\[
ba^{-1}
\]

need not be equal.

This is one of the first places where preserving multiplication order becomes essential.

---

## 7. Core examples

### Integers under addition

\[
(\mathbb Z,+)
\]

is an infinite abelian group.

The identity is:

\[
0,
\]

and the inverse of:

\[
a
\]

is:

\[
-a.
\]

For example:

\[
7+(-7)=0.
\]

---

### Integers modulo \(n\) under addition

\[
(\mathbb Z_n,+)
\]

is a finite abelian group.

Its elements are:

\[
[0]_n,[1]_n,\ldots,[n-1]_n.
\]

The identity is:

\[
[0]_n.
\]

The inverse of:

\[
[a]_n
\]

is:

\[
[-a]_n.
\]

Its group order is:

\[
\boxed{
|\mathbb Z_n|=n.
}
\]

---

### Units modulo \(n\)

The nonzero residues modulo a composite integer do **not** generally form a group under multiplication.

For example, modulo \(8\):

\[
2
\]

has no multiplicative inverse.

The correct multiplicative group is:

\[
\boxed{
(\mathbb Z/n\mathbb Z)^\times
=
\{
[a]_n:
\gcd(a,n)=1
\}.
}
\]

These are precisely the invertible residue classes.

Its order is:

\[
\left|
(\mathbb Z/n\mathbb Z)^\times
\right|
=
\varphi(n).
\]

---

### Nonzero residues modulo a prime

When \(p\) is prime, every nonzero residue is invertible.

Therefore:

\[
\boxed{
\mathbb F_p^\times
=
\{
1,2,\ldots,p-1
\}
}
\]

forms an abelian group under multiplication modulo \(p\).

Its order is:

\[
\boxed{
|\mathbb F_p^\times|
=
p-1.
}
\]

This group appears constantly in classical public-key cryptography.

---

### Permutations

A permutation of a finite set is a bijection from the set to itself.

The permutations of:

\[
\{1,\ldots,n\}
\]

form the **symmetric group**:

\[
S_n.
\]

The group operation is function composition.

For:

\[
n\ge3,
\]

the group is nonabelian.

For example, in \(S_3\), let:

\[
\sigma=(12)
\]

and:

\[
\tau=(23).
\]

Then generally:

\[
\sigma\tau
\neq
\tau\sigma.
\]

Permutation groups are among the clearest examples showing that the order of multiplication can matter.

---

## 8. Subgroups

Let \(G\) be a group.

A subset:

\[
H\subseteq G
\]

is a **subgroup** if \(H\) itself forms a group under the operation inherited from \(G\).

We write:

\[
\boxed{
H\le G.
}
\]

Every group contains at least two obvious subgroups:

\[
\{e\}
\]

and:

\[
G.
\]

The first is called the **trivial subgroup**.

---

## 9. The subgroup test

Checking every group axiom from scratch is often unnecessary.

A particularly useful criterion is:

> A nonempty subset \(H\subseteq G\) is a subgroup if
>
> \[
> xy^{-1}\in H
> \]
>
> for every \(x,y\in H\).

### Why does this work?

Because \(H\neq\varnothing\), choose:

\[
x\in H.
\]

Then:

\[
xx^{-1}
=
e
\in H.
\]

So the identity belongs to \(H\).

Now take:

\[
x=e
\]

and any:

\[
y\in H.
\]

Then:

\[
ey^{-1}
=
y^{-1}
\in H.
\]

So inverses belong to \(H\).

Finally, because:

\[
y^{-1}\in H,
\]

the subgroup criterion applied to \(x\) and \(y^{-1}\) gives:

\[
x(y^{-1})^{-1}
=
xy
\in H.
\]

Therefore \(H\) is closed under multiplication.

Associativity is inherited from \(G\).

Hence \(H\) is a group.

---

## 10. Example of a subgroup

Consider:

\[
(\mathbb Z,+).
\]

The even integers:

\[
2\mathbb Z
=
\{
\ldots,-4,-2,0,2,4,\ldots
\}
\]

form a subgroup.

Indeed, for:

\[
2a,2b\in2\mathbb Z,
\]

we have:

\[
2a-2b
=
2(a-b)
\in2\mathbb Z.
\]

So:

\[
\boxed{
2\mathbb Z\le\mathbb Z.
}
\]

More generally:

\[
n\mathbb Z
\le
\mathbb Z
\]

for every integer \(n\).

---

## 11. Generated subgroups

Take an element:

\[
g\in G.
\]

The **subgroup generated by \(g\)** is:

\[
\boxed{
\langle g\rangle
=
\{
g^k:
k\in\mathbb Z
\}.
}
\]

In additive notation:

\[
\boxed{
\langle g\rangle
=
\{
kg:
k\in\mathbb Z
\}.
}
\]

This is the smallest subgroup of \(G\) containing \(g\).

Indeed, every subgroup containing \(g\) must also contain:

\[
g^{-1},
g^2,
g^{-2},
g^3,\ldots
\]

and therefore must contain all of:

\[
\langle g\rangle.
\]

---

## 12. Cyclic groups

A group \(G\) is **cyclic** if there exists:

\[
g\in G
\]

such that:

\[
\boxed{
G=\langle g\rangle.
}
\]

Such an element is called a **generator** of \(G\).

### Example: \(\mathbb Z\)

Under addition:

\[
\mathbb Z
=
\langle1\rangle.
\]

Also:

\[
\mathbb Z
=
\langle-1\rangle.
\]

So \((\mathbb Z,+)\) is an infinite cyclic group.

---

### Example: \(\mathbb Z_n\)

Under addition:

\[
\mathbb Z_n
=
\langle[1]_n\rangle.
\]

Therefore every additive group:

\[
(\mathbb Z_n,+)
\]

is cyclic.

But \([1]_n\) is not necessarily the only generator.

For example, in:

\[
\mathbb Z_8,
\]

both:

\[
[1]_8
\]

and:

\[
[3]_8
\]

generate the entire group.

---

## 13. Every cyclic group is abelian

Suppose:

\[
G=\langle g\rangle.
\]

Every element has the form:

\[
g^a
\]

for some integer \(a\).

Take:

\[
x=g^a,
\qquad
y=g^b.
\]

Then:

\[
xy
=
g^ag^b
=
g^{a+b}.
\]

But:

\[
a+b=b+a,
\]

so:

\[
g^{a+b}
=
g^{b+a}
=
g^bg^a
=
yx.
\]

Therefore:

\[
\boxed{
\text{every cyclic group is abelian}.
}
\]

The converse is false.

An abelian group need not be cyclic.

For example:

\[
\mathbb Z_2\times\mathbb Z_2
\]

is abelian but not cyclic.

---

## 14. Element order

Let:

\[
g\in G.
\]

If there exists a positive integer \(m\) such that:

\[
g^m=e,
\]

then the **order of \(g\)** is the smallest such positive integer.

We write:

\[
\boxed{
\operatorname{ord}(g)
=
m.
}
\]

If no such positive integer exists, \(g\) has **infinite order**.

### Example

In:

\[
\mathbb Z_7^\times,
\]

consider:

\[
g=2.
\]

Then:

\[
2^1\equiv2\pmod7,
\]

\[
2^2\equiv4\pmod7,
\]

\[
2^3\equiv1\pmod7.
\]

Therefore:

\[
\boxed{
\operatorname{ord}_7(2)=3.
}
\]

The generated subgroup is:

\[
\langle2\rangle
=
\{1,2,4\}.
\]

So:

\[
|\langle2\rangle|
=
3.
\]

In general:

\[
\boxed{
|\langle g\rangle|
=
\operatorname{ord}(g)
}
\]

whenever \(g\) has finite order.

---

## 15. Group order versus element order

These two quantities should be kept distinct.

The **order of the group** is:

\[
|G|.
\]

The **order of an element** is:

\[
\operatorname{ord}(g).
\]

For example:

\[
|\mathbb Z_7^\times|
=
6,
\]

but:

\[
\operatorname{ord}_7(2)
=
3.
\]

So an element may generate only a proper subgroup of the ambient group.

This distinction is fundamental in cryptography.

A large group is not sufficient by itself.

We frequently care about the order of the **specific subgroup generated by the selected base point or generator**.

---

## 16. Lagrange's theorem

One of the central theorems of finite group theory states:

\[
\boxed{
H\le G
\Longrightarrow
|H|\mid|G|
}
\]

when \(G\) is finite.

This is **Lagrange's theorem**.

Its proof will become more natural once we introduce cosets.

For now, the important consequence is immediate.

Since:

\[
\langle g\rangle
\le G,
\]

we obtain:

\[
|\langle g\rangle|
\mid
|G|.
\]

But:

\[
|\langle g\rangle|
=
\operatorname{ord}(g).
\]

Therefore:

\[
\boxed{
\operatorname{ord}(g)
\mid
|G|.
}
\]

This is one of the most frequently used consequences of Lagrange's theorem.

---

## 17. Consequence for powers

Suppose \(g\) has finite order:

\[
m.
\]

Then:

\[
g^m=e.
\]

If:

\[
r\equiv s\pmod m,
\]

then:

\[
r-s=km
\]

for some integer \(k\).

Therefore:

\[
g^r
=
g^{s+km}
=
g^s(g^m)^k
=
g^s.
\]

Thus:

\[
\boxed{
r\equiv s
\pmod{\operatorname{ord}(g)}
\Longrightarrow
g^r=g^s.
}
\]

So exponents may be reduced modulo the **element order**.

This is more precise than reducing them merely modulo the order of the entire ambient group.

---

## 18. Order of a power

Suppose \(g\) has finite order:

\[
n.
\]

What is the order of:

\[
g^k?
\]

The answer is:

\[
\boxed{
\operatorname{ord}(g^k)
=
\frac{n}{\gcd(n,k)}.
}
\]

### Derivation

We seek the smallest positive \(m\) satisfying:

\[
(g^k)^m=e.
\]

That means:

\[
g^{km}=e.
\]

Since \(g\) has order \(n\):

\[
n\mid km.
\]

Let:

\[
d=\gcd(n,k).
\]

Write:

\[
n=dn',
\qquad
k=dk',
\]

with:

\[
\gcd(n',k')=1.
\]

Then:

\[
dn'
\mid
dk'm
\]

is equivalent to:

\[
n'\mid k'm.
\]

Since:

\[
\gcd(n',k')=1,
\]

we must have:

\[
n'\mid m.
\]

The smallest possible positive value is:

\[
m=n'.
\]

Therefore:

\[
\operatorname{ord}(g^k)
=
n'
=
\frac{n}{d}
=
\frac{n}{\gcd(n,k)}.
\]

---

## 19. Which powers are generators?

Suppose:

\[
G=\langle g\rangle
\]

is cyclic of order:

\[
n.
\]

The element:

\[
g^k
\]

is also a generator exactly when:

\[
\operatorname{ord}(g^k)=n.
\]

Using:

\[
\operatorname{ord}(g^k)
=
\frac{n}{\gcd(n,k)},
\]

this happens exactly when:

\[
\gcd(n,k)=1.
\]

Therefore:

\[
\boxed{
g^k
\text{ generates }G
\iff
\gcd(k,n)=1.
}
\]

Consequently, a cyclic group of order \(n\) has exactly:

\[
\boxed{
\varphi(n)
}
\]

generators.

This is an important bridge between elementary number theory and abstract group theory.

---

## 20. Subgroups of cyclic groups

Cyclic groups have an especially simple subgroup structure.

Let:

\[
G=\langle g\rangle
\]

have finite order:

\[
n.
\]

For every divisor:

\[
d\mid n,
\]

there exists exactly one subgroup of order \(d\).

It can be written as:

\[
\boxed{
\left\langle
g^{n/d}
\right\rangle.
}
\]

For example, suppose:

\[
|G|=12.
\]

The divisors are:

\[
1,2,3,4,6,12.
\]

So \(G\) has one subgroup of each of those orders.

This complete correspondence between subgroup orders and divisors of \(n\) is one reason cyclic groups are so easy to analyze.

---

## 21. Example: a cyclic modular group

Consider:

\[
\mathbb Z_7^\times.
\]

Its elements are:

\[
\{1,2,3,4,5,6\}.
\]

Its order is:

\[
6.
\]

Take:

\[
g=3.
\]

Compute:

\[
3^1\equiv3,
\]

\[
3^2\equiv2,
\]

\[
3^3\equiv6,
\]

\[
3^4\equiv4,
\]

\[
3^5\equiv5,
\]

\[
3^6\equiv1
\pmod7.
\]

So:

\[
\operatorname{ord}_7(3)=6.
\]

Therefore:

\[
\boxed{
\mathbb Z_7^\times
=
\langle3\rangle.
}
\]

Thus \(3\) is a generator.

Now consider:

\[
3^2=2.
\]

The order formula gives:

\[
\operatorname{ord}(3^2)
=
\frac6{\gcd(6,2)}
=
3.
\]

Indeed:

\[
\langle2\rangle
=
\{1,2,4\}.
\]

---

## 22. A noncyclic example

Consider:

\[
\mathbb Z_8^\times
=
\{1,3,5,7\}.
\]

The group has order:

\[
4.
\]

But:

\[
3^2\equiv1\pmod8,
\]

\[
5^2\equiv1\pmod8,
\]

and:

\[
7^2\equiv1\pmod8.
\]

So every nonidentity element has order:

\[
2.
\]

No element has order \(4\).

Therefore:

\[
\boxed{
\mathbb Z_8^\times
\text{ is not cyclic}.
}
\]

This demonstrates an important point:

\[
|G|=n
\]

does **not** imply that \(G\) contains an element of order \(n\).

If such an element exists, then and only then is the group cyclic.

---

## 23. A small computational experiment

For finite modular examples, we can inspect element orders directly.

```python
from math import gcd


def multiplicative_order(a, n):
    if gcd(a, n) != 1:
        raise ValueError(
            "a must be a unit modulo n"
        )

    x = 1

    for k in range(1, n + 1):
        x = (x * a) % n

        if x == 1:
            return k

    raise RuntimeError(
        "order was not found"
    )
```

Now:

```python
print(
    multiplicative_order(
        3,
        7,
    )
)
```

returns:

```text
6
```

while:

```python
print(
    multiplicative_order(
        2,
        7,
    )
)
```

returns:

```text
3
```

For small examples, this directly exposes the distinction between:

\[
|G|
\]

and:

\[
\operatorname{ord}(g).
\]

---

## 24. Why groups matter in cryptography

Group theory is not merely convenient notation for cryptography.

Many cryptographic assumptions are explicitly statements about computations inside groups.

### Diffie-Hellman

A typical Diffie-Hellman setting chooses:

\[
G=\langle g\rangle
\]

with large order:

\[
q.
\]

A secret exponent:

\[
a
\]

produces a public element:

\[
g^a.
\]

The discrete-logarithm problem asks whether one can efficiently recover \(a\) from:

\[
g
\]

and:

\[
g^a.
\]

So the security assumption is formulated directly in terms of a cyclic group and a generator.

---

### Subgroup order

Suppose the intended group has a large order but an implementation accepts an element lying in a small subgroup.

Then exponentiation may reveal information only modulo that small subgroup order.

This is the algebraic foundation of small-subgroup attacks.

So the distinction:

\[
\boxed{
|G|
\quad\text{versus}\quad
\operatorname{ord}(g)
}
\]

is operationally important.

---

### Elliptic curves

Points on an elliptic curve form an abelian group.

The operation is usually written additively:

\[
P+Q.
\]

Repeated addition gives:

\[
[k]P.
\]

The order of a point \(P\) is the smallest positive integer \(n\) satisfying:

\[
[n]P=\mathcal O,
\]

where \(\mathcal O\) is the identity point.

Again, cryptographic parameters care not only about the size of the curve group but about the order of the selected subgroup.

---

### Permutation and symmetry groups

Other areas of mathematics and cryptography work with nonabelian groups.

Permutation groups provide the canonical finite example.

They remind us that properties that seem automatic in modular multiplication — especially commutativity — are not consequences of the group axioms.

---

## 25. What we have not introduced yet

There are several important ideas that naturally follow from this article but are intentionally postponed:

- cosets,
- normal subgroups,
- quotient groups,
- homomorphisms,
- kernels,
- images,
- isomorphisms.

These concepts are tightly connected.

For example, the proof of Lagrange's theorem is most naturally expressed through cosets, while normal subgroups arise precisely because they allow cosets to inherit a group operation.

Rather than introduce all of them superficially here, we will develop them together in the next part.

---

## Practice and checkpoint

### Exercise 1 — Verify the group axioms

Show that:

\[
(\mathbb Z_6,+)
\]

is a group.

Identify:

- the identity;
- the inverse of every element;
- whether the group is abelian.

---

### Exercise 2 — Failure of group structure

Consider:

\[
\{1,2,3,4,5\}
\]

under multiplication modulo \(6\).

Explain why this is **not** a group.

Which elements fail to have inverses?

Now identify:

\[
(\mathbb Z/6\mathbb Z)^\times.
\]

---

### Exercise 3 — Subgroup test

Show that:

\[
3\mathbb Z
\]

is a subgroup of:

\[
(\mathbb Z,+).
\]

Use the one-step subgroup criterion:

\[
x-y\in3\mathbb Z.
\]

---

### Exercise 4 — Element order

Compute the order of every element in:

\[
\mathbb Z_7^\times.
\]

Which elements generate the full group?

---

### Exercise 5 — Order of a power

Suppose:

\[
\operatorname{ord}(g)=18.
\]

Compute:

\[
\operatorname{ord}(g^2),
\]

\[
\operatorname{ord}(g^3),
\]

\[
\operatorname{ord}(g^6),
\]

and:

\[
\operatorname{ord}(g^7).
\]

Use:

\[
\operatorname{ord}(g^k)
=
\frac{18}{\gcd(18,k)}.
\]

---

### Exercise 6 — Generators

Let:

\[
G=\langle g\rangle
\]

have order:

\[
12.
\]

Which powers:

\[
g^k,
\qquad
0\le k<12,
\]

generate \(G\)?

Verify that their number is:

\[
\varphi(12).
\]

---

### Exercise 7 — Subgroups of a cyclic group

Suppose:

\[
G=\langle g\rangle
\]

has order \(24\).

List all possible subgroup orders.

For each divisor:

\[
d\mid24,
\]

write a generator of the unique subgroup of order \(d\).

---

### Exercise 8 — Noncyclic group

Show that:

\[
\mathbb Z_8^\times
\]

has order \(4\), but no element has order \(4\).

Why does this prove that the group is not cyclic?

---

## Reader checkpoint

You should now be able to explain:

1. The four group axioms.
2. The difference between associativity and commutativity.
3. What an abelian group is.
4. Why the identity is unique.
5. Why each inverse is unique.
6. Why
   \[
   (ab)^{-1}=b^{-1}a^{-1}.
   \]
7. Why cancellation holds in every group.
8. What a subgroup is.
9. How the subgroup test
   \[
   xy^{-1}\in H
   \]
   works.
10. What
    \[
    \langle g\rangle
    \]
    means.
11. What makes a group cyclic.
12. Why every cyclic group is abelian.
13. The difference between group order and element order.
14. Why
    \[
    |\langle g\rangle|
    =
    \operatorname{ord}(g).
    \]
15. Why
    \[
    \operatorname{ord}(g)\mid|G|
    \]
    in a finite group.
16. Why
    \[
    \operatorname{ord}(g^k)
    =
    \frac{\operatorname{ord}(g)}
    {\gcd(\operatorname{ord}(g),k)}.
    \]
17. When a power of a generator is again a generator.
18. Why a cyclic group of order \(n\) has
    \[
    \varphi(n)
    \]
    generators.
19. Why every divisor of the order of a finite cyclic group corresponds to a unique subgroup.
20. Why subgroup order is directly relevant to finite-group cryptography.

If these ideas are clear, we have the basic internal structure of a group.

The next question is how different groups — and different parts of the same group — are related to one another.

---

## References and further reading

**Joseph A. Gallian**,  
*Contemporary Abstract Algebra.*

A very accessible introduction to groups, cyclic groups, subgroups, element orders, and generators.

**David S. Dummit and Richard M. Foote**,  
*Abstract Algebra.*

A deeper and more systematic reference for group theory and the algebraic structures developed later in this series.

**Michael Artin**,  
*Algebra.*

A conceptual treatment of groups, symmetries, transformations, and algebraic structure.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

Particularly useful for connecting abstract group structure to finite groups used computationally.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Useful for seeing cyclic groups, subgroup orders, generators, and discrete logarithms in concrete cryptographic settings.

---

## Next

So far we have studied what happens **inside** one group:

\[
G.
\]

We have elements, generated subgroups, cyclic structure, and element orders.

The next step is to study structure-preserving maps:

\[
\varphi:G\rightarrow H.
\]

Such maps reveal which parts of \(G\) collapse to the identity, which elements survive in the image, and when two apparently different groups have exactly the same algebraic structure.

That naturally introduces:

\[
\text{homomorphisms},
\quad
\text{kernels},
\quad
\text{images},
\quad
\text{cosets},
\quad
\text{normal subgroups},
\quad
\text{quotient groups}.
\]

**Next: Abstract Algebra II — Homomorphisms, Cosets, Normal Subgroups, and Quotient Groups.**