---
title: "Lattices & Lattice-Based Cryptography V: q-Ary Lattices, SIS, and Ajtai's Short Relations"
description: "q-ary lattices, the Short Integer Solution problem, inhomogeneous SIS, Ajtai-style hashing, collision resistance, and the worst-case-to-average-case perspective."
pubDate: "2025-05-29"
updatedDate: "2026-09-13"
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
The Short Integer Solution problem (SIS) is one of the foundational average-case problems of lattice cryptography. It starts from ordinary modular linear algebra and adds one requirement that changes the problem completely: the solution must be **short over the integers**.

## 1. A q-ary lattice

Let

$$
A\in\mathbb Z_q^{n\times m}.
$$

The associated integer kernel is

$$
\Lambda_q^\perp(A)
=
\{z\in\mathbb Z^m:Az\equiv0\pmod q\}.
$$

It is a full-rank lattice in $\mathbb R^m$ and contains $q\mathbb Z^m$.

![A q-ary lattice](/images/blog/lattices/qary.png)

If $A$ has full row rank modulo $q$, then

$$
[\mathbb Z^m:\Lambda_q^\perp(A)]=q^n,
\qquad
\det\Lambda_q^\perp(A)=q^n.
$$

A related lattice is

$$
\Lambda_q(A^T)
=
\{A^Ts+qz:s\in\mathbb Z^n,\ z\in\mathbb Z^m\}.
$$

For the usual full-rank setting,

$$
q\bigl(\Lambda_q^\perp(A)\bigr)^*=\Lambda_q(A^T).
$$

So the two common q-ary constructions are scaled duals, not literally the same lattice.

## 2. SIS

The problem $\operatorname{SIS}_{n,m,q,\beta}$ is:

> Given uniformly random $A\in\mathbb Z_q^{n\times m}$, find a nonzero $z\in\mathbb Z^m$ such that
>
> $$
> Az\equiv0\pmod q,
> \qquad
> \|z\|\le\beta.
> $$

The choice of norm is part of the parameterization; $\ell_2$ and $\ell_\infty$ versions both occur in the literature.

Without the shortness requirement, modular linear algebra quickly gives kernel vectors. The cryptographic content is the requirement that the integer representative be unusually small.

The condition $\beta<q$ also rules out the trivial vector

$$
(q,0,\dots,0),
$$

which always lies in the modular kernel.

## 3. Why the number of columns matters

The matrix has $m$ columns but only $n$ rows. Roughly speaking, more columns create more possible short integer relations. Cryptographic parameter selection balances two competing requirements:

- enough columns that a suitably short relation exists;
- parameters large enough that finding one remains computationally difficult.

The pigeonhole principle already hints at the phenomenon. The map

$$
f_A:\{0,1\}^m\rightarrow\mathbb Z_q^n,
\qquad
f_A(x)=Ax\bmod q
$$

has $2^m$ inputs and at most $q^n$ outputs. If $2^m>q^n$, collisions must exist.

## 4. Collisions become SIS vectors

Suppose

$$
f_A(x)=f_A(y)
$$

for distinct $x,y\in\{0,1\}^m$. Then

$$
z=x-y\in\{-1,0,1\}^m
$$

satisfies

$$
Az\equiv0\pmod q.
$$

Thus a collision gives a very short SIS solution.

![Ajtai-style modular compression](/images/blog/lattices/ajtaioneway.png)

This observation is the conceptual bridge from modular compression functions to collision-resistant hashing from lattice assumptions.

## 5. Ajtai's worst-case/average-case insight

Ajtai's foundational result showed that solving certain random modular short-relation instances on average can be related to solving approximate lattice problems in the worst case.

The exact approximation factors and admissible ranges depend on the particular SIS theorem and parameter regime. It is therefore misleading to summarize SIS as simply “the same hardness as SVP.” The stronger and more interesting statement is that **average-case SIS can inherit hardness from worst-case problems on arbitrary lattices**, such as suitable approximate forms of SIVP and GapSVP.

That worst-case-to-average-case structure is one of the reasons lattice cryptography is conceptually different from many older public-key systems.

## 6. Inhomogeneous SIS

Given a target syndrome $u\in\mathbb Z_q^n$, define

$$
\Lambda_{q,u}^\perp(A)
=
\{z\in\mathbb Z^m:Az\equiv u\pmod q\}.
$$

If one solution $t$ exists, then

$$
\Lambda_{q,u}^\perp(A)=t+\Lambda_q^\perp(A).
$$

![A syndrome defines a q-ary lattice coset](/images/blog/lattices/syndrome.png)

The **Inhomogeneous SIS (ISIS)** problem asks for a short element in such a coset. Geometrically, it is a short-vector-in-a-coset problem and is closely related to bounded-distance and closest-vector viewpoints.

## 7. SIS as a cryptographic primitive

SIS-style relations appear in:

- collision-resistant hashing;
- commitment schemes;
- identification and signature constructions;
- zero-knowledge protocols;
- trapdoor constructions over q-ary lattices.

The important mental model is simple:

$$
\text{modular linear relation}
+
\text{shortness constraint}
\Longrightarrow
\text{lattice problem}.
$$

The next chapter turns the picture around. Instead of searching for a short modular relation, **Learning With Errors** hides a secret inside noisy modular linear equations.
