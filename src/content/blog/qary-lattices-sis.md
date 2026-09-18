---
title: "Lattices & Lattice-Based Cryptography V: q-Ary Lattices, SIS, and Ajtai's Short Relations"
description: "q-ary lattices, the Short Integer Solution problem, inhomogeneous SIS, Ajtai-style hashing, collision resistance, and the worst-case-to-average-case perspective."
pubDate: "2025-05-29"
updatedDate: "2026-09-16"

topics:
  - "Mathematical Foundations"
  - "Lattice Theory"
  - "Lattice Methods"
  - "Post-Quantum Cryptography"

tags:
  - "q-ary-lattices"
  - "sis"
  - "isis"
  - "ajtai"
  - "short-integer-solution"
  - "worst-case-reduction"

difficulty: "Advanced"
status: "Reviewed"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 5
sourcePath: "experiments/lattices/sis"
draft: false
---

The **Short Integer Solution problem (SIS)** is one of the foundational average-case problems of lattice-based cryptography.

At first sight, SIS looks like ordinary modular linear algebra:

$$
Az \equiv 0 \pmod q.
$$

But it adds one condition that changes the nature of the problem completely:

> the solution must be **short as an integer vector**.

That small requirement turns an easy modular kernel problem into a geometric search problem over a lattice.

## 1. A q-ary lattice

Let

$$
A\in\mathbb Z_q^{n\times m}.
$$

The associated integer kernel is

$$
\Lambda_q^\perp(A)
=
\left\{
z\in\mathbb Z^m :
Az\equiv 0\pmod q
\right\}.
$$

This is called a **q-ary lattice**.

It is a full-rank lattice in $\mathbb R^m$, because it always contains

$$
q\mathbb Z^m.
$$

Indeed, for every $z\in\mathbb Z^m$,

$$
A(qz)\equiv 0\pmod q.
$$

Therefore,

$$
q\mathbb Z^m
\subseteq
\Lambda_q^\perp(A)
\subseteq
\mathbb Z^m.
$$

![A q-ary lattice](/images/blog/lattices/qary.png)

Consider the homomorphism

$$
\phi_A:\mathbb Z^m\rightarrow\mathbb Z_q^n,
\qquad
\phi_A(z)=Az\bmod q.
$$

Its kernel is exactly

$$
\ker \phi_A=\Lambda_q^\perp(A).
$$

Therefore,

$$
[\mathbb Z^m:\Lambda_q^\perp(A)]
=
|\operatorname{im}\phi_A|.
$$

If $A$ defines a surjective map onto $\mathbb Z_q^n$, then

$$
|\operatorname{im}\phi_A|=q^n,
$$

and hence

$$
[\mathbb Z^m:\Lambda_q^\perp(A)]
=
q^n.
$$

Because $\mathbb Z^m$ has determinant $1$,

$$
\det\Lambda_q^\perp(A)=q^n.
$$

When $q$ is prime, surjectivity is equivalent to saying that $A$ has row rank $n$ over the field $\mathbb F_q$.

For composite $q$, it is better to state the surjectivity condition explicitly rather than rely on field-style rank terminology.

### The companion q-ary lattice

Another frequently used construction is

$$
\Lambda_q(A^T)
=
\left\{
A^Ts+qz :
s\in\mathbb Z^n,\;
z\in\mathbb Z^m
\right\}.
$$

The two q-ary lattices are related by duality:

$$
\left(\Lambda_q^\perp(A)\right)^*
=
\frac{1}{q}\Lambda_q(A^T),
$$

or equivalently,

$$
q\left(\Lambda_q^\perp(A)\right)^*
=
\Lambda_q(A^T).
$$

So these are not two names for the same lattice.

They are **scaled dual lattices**.

This distinction becomes particularly important when we move between SIS-style kernel problems and LWE-style dual viewpoints.

---

## 2. The Short Integer Solution problem

The problem

$$
\operatorname{SIS}_{n,m,q,\beta}
$$

asks:

> Given uniformly random
>
> $$
> A\leftarrow\mathbb Z_q^{n\times m},
> $$
>
> find a nonzero vector
>
> $$
> z\in\mathbb Z^m
> $$
>
> such that
>
> $$
> Az\equiv0\pmod q
> $$
>
> and
>
> $$
> \|z\|\leq\beta.
> $$

The norm is part of the parameterization.

Common choices include

$$
\|z\|_2
$$

and

$$
\|z\|_\infty.
$$

The essential point is that SIS does **not** merely ask us to find a modular kernel vector.

That part is easy.

Instead, it asks us to find one whose integer coordinates are unusually small.

### Why ordinary linear algebra is not enough

Suppose $m>n$, and for simplicity suppose $q$ is prime.

Linear algebra over $\mathbb F_q$ may easily produce some nonzero vector

$$
z_q\in\mathbb F_q^m
$$

such that

$$
Az_q=0.
$$

But when the coordinates of $z_q$ are lifted back to integers, they may have magnitude comparable to $q$.

For example, using centered representatives gives coordinates in approximately

$$
[-q/2,q/2].
$$

Such a vector is usually far too large to satisfy the SIS bound.

The difficult part is therefore not

$$
Az\equiv0\pmod q,
$$

but

$$
Az\equiv0\pmod q
\qquad\text{and}\qquad
z\text{ is short}.
$$

### Excluding trivial solutions

Because

$$
q e_i\in\Lambda_q^\perp(A)
$$

for every standard basis vector $e_i$, SIS would be trivial if vectors of length $q$ were allowed.

For example,

$$
(q,0,\ldots,0)
$$

always satisfies

$$
Az\equiv0\pmod q.
$$

A parameter condition such as

$$
\beta<q
$$

rules out these immediately available vectors.

---

## 3. A tiny SIS example

Take

$$
q=11
$$

and

$$
A=
\begin{pmatrix}
2 & 7 & 3
\end{pmatrix}.
$$

Consider

$$
z=
\begin{pmatrix}
2\\
1\\
0
\end{pmatrix}.
$$

Then

$$
Az
=
2\cdot2+7\cdot1+3\cdot0
=
11.
$$

Therefore,

$$
Az\equiv0\pmod{11}.
$$

Moreover,

$$
\|z\|_2=\sqrt{5}.
$$

So $z$ is a short integer relation among the columns of $A$.

The important word is **relation**.

SIS asks us to discover small integer coefficients

$$
z_1,\ldots,z_m
$$

such that

$$
z_1a_1+\cdots+z_ma_m
\equiv0\pmod q,
$$

where

$$
A=
\begin{pmatrix}
a_1 & \cdots & a_m
\end{pmatrix}.
$$

For realistic cryptographic dimensions, such relations may exist while remaining computationally difficult to find.

---

## 4. Why the number of columns matters

The matrix $A$ contains $m$ columns but only $n$ modular equations.

Increasing $m$ gives us more possible combinations of columns and therefore more opportunities for short relations.

Cryptographic parameter selection balances two requirements:

1. sufficiently short solutions should exist;
2. finding such a solution should remain computationally difficult.

A simple pigeonhole argument already reveals the basic phenomenon.

Consider

$$
f_A:\{0,1\}^m\rightarrow\mathbb Z_q^n
$$

defined by

$$
f_A(x)=Ax\bmod q.
$$

The domain contains

$$
2^m
$$

vectors.

The codomain contains at most

$$
q^n
$$

values.

Therefore, whenever

$$
2^m>q^n,
$$

or equivalently

$$
m>n\log_2q,
$$

there must exist distinct

$$
x,y\in\{0,1\}^m
$$

such that

$$
f_A(x)=f_A(y).
$$

The important distinction is:

> existence does not imply efficient findability.

The pigeonhole principle proves that collisions are somewhere in the domain.

It does not tell us how to find one efficiently.

---

## 5. Collisions become SIS vectors

Suppose an algorithm finds a collision

$$
f_A(x)=f_A(y)
$$

for distinct

$$
x,y\in\{0,1\}^m.
$$

Then

$$
Ax\equiv Ay\pmod q.
$$

Subtracting gives

$$
A(x-y)\equiv0\pmod q.
$$

Define

$$
z=x-y.
$$

Because $x\neq y$,

$$
z\neq0.
$$

And because $x$ and $y$ are binary vectors,

$$
z\in\{-1,0,1\}^m.
$$

Therefore,

$$
\|z\|_\infty\leq1
$$

and

$$
\|z\|_2\leq\sqrt m.
$$

A collision has therefore produced an extremely short SIS vector.

![Ajtai-style modular compression](/images/blog/lattices/ajtaioneway.png)

This gives the central reduction:

$$
\boxed{
\text{collision in }f_A
\Longrightarrow
\text{short nonzero solution of }Az\equiv0\pmod q
}
$$

Consequently, if the corresponding SIS problem is hard, then finding collisions in this function family is hard as well.

### Why this is a hash function

The input contains $m$ bits.

An element of $\mathbb Z_q^n$ can be represented using roughly

$$
n\log_2q
$$

bits.

Therefore, when

$$
m>n\log_2q,
$$

the function

$$
f_A(x)=Ax\bmod q
$$

compresses its input.

We therefore obtain the basic Ajtai-style picture:

$$
\boxed{
\text{modular linear map}
+
\text{compression}
+
\text{SIS hardness}
\Longrightarrow
\text{collision resistance}
}
$$

The full cryptographic theorem requires appropriate parameter choices, but the algebraic mechanism is exactly this simple.

---

## 6. Ajtai's worst-case-to-average-case insight

This is where SIS becomes substantially more interesting than merely another hard-looking computational problem.

The public matrix

$$
A\leftarrow\mathbb Z_q^{n\times m}
$$

is random.

So SIS is naturally an **average-case problem**.

An adversary receives a matrix sampled from a specified distribution and attempts to find a short relation.

Classical lattice problems such as SVP or SIVP, however, are usually formulated in the **worst case**:

> given an arbitrary lattice, solve the required geometric problem.

Ajtai's 1996 work introduced the remarkable connection between these two worlds.

Very informally:

$$
\boxed{
\text{efficient algorithm for suitable random short-relation instances}
}
$$

would imply

$$
\boxed{
\text{efficient algorithms for approximate lattice problems}
}
$$

on arbitrary lattices.

This was one of the foundational worst-case-to-average-case reductions in modern cryptography.

### What the result does not say

It would be misleading to summarize the result as

> “SIS is just SVP.”

It is not.

Nor should one say that solving a particular SIS instance is literally equivalent to solving exact SVP.

The actual statements depend on:

* the dimensions;
* the modulus $q$;
* the bound $\beta$;
* the number of columns $m$;
* the norm being used;
* the approximation factor of the worst-case lattice problem;
* the particular reduction theorem.

Modern SIS hardness results connect appropriate parameter regimes to approximate worst-case problems such as

$$
\operatorname{SIVP}_\gamma
$$

and

$$
\operatorname{GapSVP}_\gamma
$$

for approximation factors $\gamma$ determined by the parameters of the reduction.

Later work refined Ajtai's original reduction and substantially improved both the formulation and approximation factors.

The central conceptual statement remains:

$$
\boxed{
\text{average-case SIS hardness can be based on worst-case lattice hardness}
}
$$

rather than merely on the assumption that a particular randomly generated problem instance happens to be difficult.

That is one of the defining structural features of lattice-based cryptography.

---

## 7. Inhomogeneous SIS

SIS asks us to solve

$$
Az\equiv0\pmod q.
$$

A natural generalization replaces the zero syndrome with an arbitrary target

$$
u\in\mathbb Z_q^n.
$$

Define

$$
\Lambda_{q,u}^\perp(A)
=
\left\{
z\in\mathbb Z^m:
Az\equiv u\pmod q
\right\}.
$$

The **Inhomogeneous Short Integer Solution problem (ISIS)** asks us to find a short vector in this set:

$$
Az\equiv u\pmod q,
\qquad
\|z\|\leq\beta.
$$

There is an important geometric distinction here.

For

$$
u=0,
$$

we obtain the lattice

$$
\Lambda_q^\perp(A).
$$

But for

$$
u\neq0,
$$

the set

$$
\Lambda_{q,u}^\perp(A)
$$

is generally **not itself a lattice**, because it does not contain the origin.

Instead, it is an affine translate — a coset — of the homogeneous q-ary lattice.

Suppose $t$ is any vector satisfying

$$
At\equiv u\pmod q.
$$

Then every other solution satisfies

$$
A(z-t)\equiv0\pmod q.
$$

Therefore,

$$
z-t\in\Lambda_q^\perp(A),
$$

and hence

$$
\boxed{
\Lambda_{q,u}^\perp(A)
=
t+\Lambda_q^\perp(A)
}.
$$

![A syndrome defines a q-ary lattice coset](/images/blog/lattices/syndrome.png)

So SIS searches for a short nonzero point in a lattice, while ISIS searches for a short point in a **lattice coset**.

---

## 8. ISIS and the closest-vector viewpoint

The coset interpretation gives another useful geometric picture.

Suppose

$$
\Lambda=\Lambda_q^\perp(A)
$$

and

$$
\Lambda_{q,u}^\perp(A)=t+\Lambda.
$$

ISIS asks us to find

$$
z=t+x
$$

for some

$$
x\in\Lambda
$$

such that

$$
\|t+x\|
$$

is small.

Equivalently, we want a lattice point $x\in\Lambda$ close to

$$
-t.
$$

Thus finding the shortest representative of the coset can be viewed as a closest-vector problem:

$$
\min_{x\in\Lambda}\|x-(-t)\|.
$$

This explains the relationship between ISIS and **CVP-style geometry**.

However, one should distinguish this from the **Bounded Distance Decoding (BDD)** problem.

BDD additionally assumes that the target lies sufficiently close to a lattice point — usually close enough to guarantee uniqueness.

Therefore:

$$
\text{ISIS}
\longleftrightarrow
\text{short vector in a coset}
\longleftrightarrow
\text{CVP viewpoint},
$$

while a BDD interpretation requires an additional distance promise.

---

## 9. SIS as a cryptographic primitive

SIS and its structured variants appear throughout lattice cryptography.

Examples include:

* collision-resistant hash functions;
* commitment schemes;
* identification protocols;
* digital-signature constructions;
* zero-knowledge protocols;
* trapdoor functions;
* preimage sampling;
* lattice-based proof systems.

In modern schemes, one frequently encounters structured relatives such as

$$
\text{Ring-SIS}
$$

and

$$
\text{Module-SIS},
$$

which replace ordinary integer matrices by algebraic structures that permit much more compact and efficient implementations.

The underlying mental model, however, remains the same:

$$
\boxed{
\text{modular linear relation}
+
\text{shortness constraint}
\Longrightarrow
\text{lattice problem}
}
$$

For homogeneous SIS,

$$
Az\equiv0\pmod q.
$$

For inhomogeneous SIS,

$$
Az\equiv u\pmod q.
$$

And geometrically:

$$
\boxed{
\begin{aligned}
\text{SIS}
&\rightarrow
\text{short vector in }\Lambda_q^\perp(A),
\\[4pt]
\text{ISIS}
&\rightarrow
\text{short vector in }t+\Lambda_q^\perp(A).
\end{aligned}
}
$$

---

## 10. The bigger picture

The significance of SIS is not that modular equations are difficult.

They are not.

The significance is that modular equations secretly define high-dimensional integer lattices, and imposing a small-norm condition forces us to solve a geometric problem inside those lattices.

That gives the progression

$$
A
\longrightarrow
\Lambda_q^\perp(A)
\longrightarrow
Az\equiv0\pmod q
\longrightarrow
\|z\|\text{ small}.
$$

Ajtai's insight went one step further:

$$
\boxed{
\text{random modular short relations}
\Longleftrightarrow
\text{worst-case lattice hardness, through reductions}
}
$$

where the precise relationship depends on the theorem and parameter regime.

This worst-case-to-average-case connection is one of the deepest reasons lattices became such a powerful foundation for modern cryptography.

It allows extremely simple algebraic objects — random modular matrices — to inherit security guarantees connected to geometric problems over arbitrary lattices.

---

## Further reading

For the theoretical development behind this chapter, the most important references are:

* Miklós Ajtai, **“Generating Hard Instances of Lattice Problems,”** STOC 1996.
* Daniele Micciancio and Oded Regev, **“Worst-Case to Average-Case Reductions Based on Gaussian Measures,”** SIAM Journal on Computing, 2007.
* Craig Gentry, Chris Peikert, and Vinod Vaikuntanathan, **“Trapdoors for Hard Lattices and New Cryptographic Constructions,”** STOC 2008.
* Chris Peikert, **“A Decade of Lattice Cryptography,”** 2016.

---

The next chapter turns the picture around.

In SIS, we are given a random modular matrix and search for a short relation:

$$
Az\equiv0\pmod q.
$$

In **Learning With Errors (LWE)**, we instead observe noisy modular linear equations of the form

$$
b=A^Ts+e\pmod q
$$

and attempt to recover — or distinguish information about — the hidden secret $s$.

So the transition is:

$$
\boxed{
\text{SIS: find a short relation}
}
$$

versus

$$
\boxed{
\text{LWE: recover structure hidden by small noise}
}.
$$

These two viewpoints — **short relations** and **noisy equations** — form two of the central foundations of lattice-based cryptography.
