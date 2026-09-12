---
title: "Multiplicative Groups, Orders, and Generators: The Structure Behind Diffie-Hellman"
description: "From invertible residues to cyclic groups: why element order and generators matter, and how repeated modular multiplication becomes the algebraic engine behind Diffie-Hellman."
pubDate: "2026-09-08"
category: "Mathematical Foundations"
tags:
  - groups
  - cyclic-groups
  - generators
  - element-order
  - diffie-hellman
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

In the previous post, we separated the residues modulo $n$ into two very different kinds:

- those that have multiplicative inverses,
- and those that do not.

The invertible ones are called **units**.

For example,

$$
\mathbb Z_{20}^{\times}
=
\{1,3,7,9,11,13,17,19\}.
$$

When I first learned this, I mostly treated that set as a useful list.

Later I realized that this list is doing something much more interesting.

If I multiply two elements from it modulo $20$, I stay inside the same set.

There is an identity, namely $1$.

Every element has an inverse.

And multiplication is associative.

So these residues are not just "the good numbers modulo $20$."

They form a **group**.

That sounds like a small change in language, but it is the point where modular arithmetic starts becoming the algebraic machinery behind Diffie-Hellman, elliptic curves, signatures, and eventually much more.

![Orders and generators inside the multiplicative group modulo 7](/images/blog/04-orders-generators-mod7.svg)

*In $\mathbb F_7^\times$, the element $2$ only reaches a subgroup of three elements, while $3$ visits every non-zero residue before returning to $1$.*

---

## What a group is really buying us

A group is a set together with an operation that behaves predictably.

For our multiplicative example, we need four things:

1. multiplying two elements keeps us inside the set;
2. there is an identity element;
3. every element has an inverse;
4. multiplication is associative.

For

$$
\mathbb Z_n^\times,
$$

the operation is multiplication modulo $n$.

The identity is

$$
1.
$$

And because we kept only the units, inverses exist by definition.

For example, modulo $20$,

$$
3\cdot7\equiv1\pmod{20},
$$

so $7$ is the inverse of $3$.

The part I find useful is that once we know we are inside a group, we can stop reasoning about isolated numbers and start reasoning about **structure**.

How large is the group?

What happens if we repeatedly multiply one element by itself?

How many different elements can it reach?

Those questions lead directly to **order** and **generators**.

---

The size of

$$
\mathbb Z_n^\times
$$

is given by Euler's phi function:

$$
|\mathbb Z_n^\times|=\varphi(n).
$$

For example,

$$
\varphi(20)=8.
$$

When the modulus is prime, things become especially clean.

For a prime $p$,

$$
\mathbb F_p^\times
=
\{1,2,\ldots,p-1\},
$$

so:

$$
|\mathbb F_p^\times|=p-1.
$$

Take $p=7$.

Then:

$$
\mathbb F_7^\times
=
\{1,2,3,4,5,6\}.
$$

The group has six elements.

But that does **not** mean that every element needs six powers before it comes back to $1$.

That was an important distinction for me.

---

## The order of an element

Take $2$ modulo $7$.

Compute its powers:

$$
2^1\equiv2\pmod7,
$$

$$
2^2\equiv4\pmod7,
$$

$$
2^3\equiv1\pmod7.
$$

We have returned to the identity after three steps.

So the **multiplicative order** of $2$ modulo $7$ is:

$$
\operatorname{ord}_7(2)=3.
$$

The order of an element $g$ is the smallest positive integer $k$ such that:

$$
g^k\equiv1\pmod n.
$$

The powers of $2$ therefore generate only:

$$
\langle2\rangle
=
\{1,2,4\}.
$$

That set is a **subgroup** of the full multiplicative group.

Now try $3$:

$$
3^1\equiv3,
$$

$$
3^2\equiv2,
$$

$$
3^3\equiv6,
$$

$$
3^4\equiv4,
$$

$$
3^5\equiv5,
$$

$$
3^6\equiv1
\pmod7.
$$

This time every non-zero residue appears before we return to $1$.

So:

$$
\operatorname{ord}_7(3)=6.
$$

Because the full group also has six elements,

$$
\langle3\rangle=\mathbb F_7^\times.
$$

We call $3$ a **generator** of the group.

Or equivalently, the group is cyclic and $3$ generates it.

In Python, the experiment is almost embarrassingly simple:

```python
def powers_mod(g, p):
    value = 1

    for exponent in range(1, p):
        value = (value * g) % p
        print(exponent, value)
```

Run it with:

```python
powers_mod(2, 7)
powers_mod(3, 7)
```

and the difference becomes visible immediately.

This is one reason I like implementing the tiny version first.

A definition such as "generator of a cyclic group" can feel abstract.

But printing

```text
1 → 3 → 2 → 6 → 4 → 5 → 1
```

makes it concrete.

---

## Why the order matters more than I originally thought

Suppose we work with some public element $g$.

If:

$$
\operatorname{ord}(g)=3,
$$

then repeated exponentiation can only produce three different group elements.

No matter how enormous the exponent is, we are still trapped inside that tiny subgroup.

For example, with $g=2$ modulo $7$:

$$
2^1,2^2,2^3,2^4,\ldots
$$

just cycles through:

$$
2,4,1,2,4,1,\ldots
$$

So choosing a large secret exponent does not magically create a large search space if the element itself has small order.

That is a subtle point that becomes very important in cryptography:

> The size of the modulus is not the same thing as the size of the subgroup in which the protocol actually operates.

If $g$ has order $q$, then:

$$
g^{x+q}=g^x.
$$

So exponents are effectively interpreted modulo $q$.

Not modulo the field modulus $p$.

For the full multiplicative group $\mathbb F_p^\times$, a generator has order $p-1$.

But real cryptographic protocols often deliberately work inside a large **prime-order subgroup**

$$
G=\langle g\rangle
$$

with:

$$
|G|=q.
$$

We will come back to why this matters when we study small-subgroup attacks and real parameter selection.

For now, the mental model I want is:

```text
modulus p
   does not by itself tell me
the order of g
   which determines
the subgroup <g>
   which determines
which values exponentiation can actually reach
```

---

## Now Diffie-Hellman is almost visible

Suppose Alice and Bob agree on a cyclic group

$$
G=\langle g\rangle
$$

with large order $q$.

Alice secretly chooses:

$$
a\in\mathbb Z_q
$$

and publishes:

$$
A=g^a.
$$

Bob chooses:

$$
b\in\mathbb Z_q
$$

and publishes:

$$
B=g^b.
$$

We are not going to finish the protocol in this article.

But look at what we already understand.

The public values are produced by **repeated group multiplication**, written compactly as exponentiation.

The secrets are exponents.

The possible public values live inside the subgroup generated by $g$.

And because powers repeat according to the order of $g$, the group order is part of the security story.

That entire setup is already present before we even discuss the shared key.

> **Paper connection — where public-key cryptography changed direction.**  
> In 1976, Whitfield Diffie and Martin Hellman published *New Directions in Cryptography* in IEEE Transactions on Information Theory. The paper introduced the public-key viewpoint and the key-agreement idea now associated with Diffie-Hellman.  
> DOI: [10.1109/TIT.1976.1055638](https://doi.org/10.1109/TIT.1976.1055638)

What I like about reading that paper after learning the group language is that expressions such as

$$
g^a
$$

stop looking like arbitrary number-theory tricks.

They are simply group exponentiation.

And that same abstraction survives when the representation changes.

Later, in elliptic curves, we will replace:

$$
g^a
$$

with:

$$
[a]P.
$$

Different notation.

Different underlying object.

Very similar group idea.

---

Run the companion chapter:

```powershell
python chapters/04_multiplicative_groups/demo.py
```

and especially:

```powershell
python chapters/04_multiplicative_groups/experiments.py
```

The experiment checks several prime fields and prints:

```text
element
order
generator?
```

Try $p=7$ by hand first.

You should find:

$$
\operatorname{ord}_7(1)=1,
$$

$$
\operatorname{ord}_7(2)=3,
$$

and generators including:

$$
3,\;5.
$$

Then ask yourself:

1. Why does every order divide the size of the group?
2. Why does a generator need order exactly $p-1$ in $\mathbb F_p^\times$?
3. If $g$ has order $q$, why do $g^x$ and $g^{x+q}$ coincide?
4. Why would a tiny subgroup be a bad place to hide a secret exponent?

We will answer the security version of those questions soon.

For the next post, however, we finally have enough machinery to build our first complete public-key protocol from scratch.

We will choose tiny public parameters, let Alice and Bob exchange values, compute the same shared secret independently—and then immediately brute-force the toy version.

**Next:** *Diffie-Hellman From Scratch: Build It, Share a Secret, Then Break the Toy Version.*
