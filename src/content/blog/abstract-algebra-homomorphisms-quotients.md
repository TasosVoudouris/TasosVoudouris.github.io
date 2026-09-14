---
title: "Abstract Algebra II: Homomorphisms, Kernels, Cosets, Normal Subgroups, and Quotient Groups"
description: "How structure-preserving maps lead to kernels, images, cosets, normality, quotient groups, and the first isomorphism theorem."
pubDate: "2025-03-19"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Abstract Algebra"
tags:
- "homomorphisms"
- "kernels"
- "cosets"
- "normal-subgroups"
- "quotient-groups"
- "isomorphism-theorems"
difficulty: "Intermediate"
status: "Reference"
series: "Abstract Algebra Foundations"
seriesOrder: 2
sourcePath: "experiments/mathematics/abstract-algebra"
draft: false
---
Once a group has been defined, the natural question is how two groups can be compared. A **homomorphism** is a map that preserves the group operation, and its kernel and image reveal exactly what structure is collapsed and what survives.

## 1. Group homomorphisms

A map $\varphi:G\to H$ is a homomorphism if
$$
\varphi(xy)=\varphi(x)\varphi(y)
$$
for all $x,y\in G$.

It follows automatically that
$$
\varphi(e_G)=e_H,
\qquad
\varphi(x^{-1})=\varphi(x)^{-1}.
$$

A bijective homomorphism is an **isomorphism**. If one exists, the groups are structurally the same even if their elements have very different descriptions.

## 2. Kernel and image

The kernel is
$$
\ker\varphi=\{g\in G:\varphi(g)=e_H\},
$$
and the image is
$$
\operatorname{im}\varphi=\{\varphi(g):g\in G\}.
$$

The kernel measures non-injectivity:
$$
\varphi\text{ is injective}\iff \ker\varphi=\{e_G\}.
$$

The image is always a subgroup of $H$, while the kernel is a special kind of subgroup of $G$: it is **normal**.

## 3. Cosets

For $H\le G$ and $g\in G$, the left and right cosets are
$$
gH=\{gh:h\in H\},\qquad Hg=\{hg:h\in H\}.
$$

Cosets partition $G$. Every coset has the same cardinality as $H$, which yields Lagrange's theorem for finite groups:
$$
|G|=[G:H]\,|H|.
$$
The integer $[G:H]$ is the **index** of $H$ in $G$.

## 4. Normal subgroups

A subgroup $N\le G$ is **normal**, written $N\trianglelefteq G$, if
$$
gN=Ng\qquad\text{for all }g\in G.
$$
Equivalently,
$$
gNg^{-1}=N.
$$

Normality is exactly what is required for multiplication of cosets to be well-defined.

## 5. Quotient groups

If $N\trianglelefteq G$, define
$$
G/N=\{gN:g\in G\}
$$
with
$$
(gN)(hN)=(gh)N.
$$

A quotient group deliberately identifies every element of $N$ with the identity. The construction is not merely notation: it is the universal way to collapse a normal subgroup while preserving a group operation.

## 6. First isomorphism theorem

For a homomorphism $\varphi:G\to H$,
$$
G/\ker\varphi\cong\operatorname{im}\varphi.
$$

This theorem is one of the most reusable structural statements in algebra. It says that once the information lost by $\varphi$ has been factored out, what remains is precisely the image.

## 7. A modular example

Consider
$$
\varphi:\mathbb Z\to\mathbb Z/n\mathbb Z,
\qquad
\varphi(k)=k\bmod n.
$$
Then
$$
\ker\varphi=n\mathbb Z,
$$
and therefore
$$
\mathbb Z/n\mathbb Z\cong \mathbb Z/(n\mathbb Z).
$$
This simple example contains the entire quotient-group idea in a familiar setting.

## 8. Why this matters later

Quotients and homomorphisms reappear in polynomial quotient rings, finite-field construction, elliptic-curve isogenies, module theory, and many cryptographic protocols. They are not optional abstraction: they are the language that makes those constructions precise.
