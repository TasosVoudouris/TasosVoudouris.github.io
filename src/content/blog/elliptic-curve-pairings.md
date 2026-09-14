---
title: "Elliptic Curve Mathematics XI: Divisors, Weil Pairing, and Tate Pairing"
description: "A mathematical introduction to torsion points, divisors, bilinear pairings, the Weil and Tate pairings, and embedding degree."
pubDate: "2025-05-25"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Mathematical Foundations"
- "Public-Key Cryptography"
tags:
- "pairings"
- "weil-pairing"
- "tate-pairing"
- "embedding-degree"
- "torsion"
difficulty: "Advanced"
series: "Elliptic Curve Mathematics"
seriesOrder: 11
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
After our first four parts—where we introduced the Weierstrass form, the $j$-invariant, curves over $\mathbb{Q}$ and $\mathbb{F}_p$, and special models (Montgomery and Edwards)—we have laid the groundwork for the true *cornerstone* of modern elliptic-curve cryptography: **pairings**.

In part, we will:

1. **Refresh our memory on torsion points**: Recall that for an elliptic curve $E$ over a field $K$, the $n$-torsion subgroup

   $$
     E[n] = \{\,P\in E(\overline{K}) : nP = \mathcal{O}\}
   $$

   is central to every pairing construction.

2. **Introduce divisors:** Unlike the division polynomials we saw earlier, **divisors** are formal sums of points on $E$.  They provide the language in which pairings—originally defined via functions on the curve—are most naturally stated.

3. **Define a bilinear pairing:** We will see that a pairing is a map

   $$
     e \colon E[n]\times E[n]\;\longrightarrow\;\mu_n,
   $$

   where $\mu_n\subset \overline{K}^\times$ is the group of $n$-th roots of unity, satisfying:

   * *Bilinearity:* $e(P+P',\,Q)=e(P,Q)\,e(P',Q)$ and similarly in the second argument.
   * *Non-degeneracy:*  If $e(P,Q)=1$ for all $Q\in E[n]$, then $P=\mathcal{O}$.
   * *Efficient computability:*  There exists an algorithm (e.g.\ Miller’s algorithm) running in time polynomial in $\log|K|$ and $\log n$.

4. **Survey the Weil and (reduced) Tate pairings:** We will outline how the classical *Weil pairing* and the more efficient *Tate pairing* arise from the divisor language, and why the Tate pairing—after a suitable final exponentiation—becomes non-degenerate.  Finally, we’ll touch on how these pairings enable powerful protocols such as identity-based encryption, short signatures, and three-party key agreement.

We will only *scratch the surface* of pairing theory, but it will give you the essential definitions, properties, and intuitions needed to delve deeper into pairing-based cryptography.


## Torsion Points

Let $E$ be an elliptic curve defined over a field $K$, and let $n$ be a positive integer. The group of $m$-torsion points on $E$ is defined as:

$$
E[n] = \{ P \in E \mid nP = \mathcal{O} \}
$$

* A point $P \in E$ satisfying $nP = \mathcal{O}$ is said to have order dividing $m$.
* If we require that $P$ has coordinates in a specific field $K$, we write $P \in E(K)[n]$.

**Theorem.** Let $E$ be an elliptic curve over a field $K$, and $n \in \mathbb{Z}_{>0}$. If the characteristic of $K$ does not divide $n$, then:

$$
E[n] \cong \mathbb{Z}/n\mathbb{Z} \times \mathbb{Z}/n\mathbb{Z}
$$

If $\text{char}(K) = p > 0$ and $p \mid n$, write $n = p^r m'$ with $\gcd(p, n') = 1$. Then:

$$
E[n] \cong \mathbb{Z}/n'\mathbb{Z} \times \mathbb{Z}/n'\mathbb{Z} \quad \text{or} \quad \mathbb{Z}/n\mathbb{Z} \times \mathbb{Z}/n'\mathbb{Z}
$$

**Remarks:**

* $E$ is called *ordinary* if $E[p] \cong \mathbb{Z}/p\mathbb{Z}$.
* $E$ is *supersingular* if $E[p] = \{\mathcal{O}\}$.
* If $E[p] \ne \{\mathcal{O}\}$, then $E[p^k] \cong \mathbb{Z}/p^k\mathbb{Z}$ for all $k > 0$.
* If $\gcd(n, \text{char}(K)) = 1$, then $|E[n]| = n^2$.



**Mordell–Weil Theorem:**
Let $K$ be a number field. Then the group $E(K)$ of $K$-rational points on $E$ is finitely generated:

$$
E(K) \cong E(K)_{\text{tors}} \times \mathbb{Z}^r
$$

for some integer $r \geq 0$.


## Divisors on Elliptic Curves

Let $f$ be a non-zero rational function on an elliptic curve $E$. The **divisor** of $f$ is a formal sum of points on $E$ with integer coefficients:

$$
\text{div}(f) = \sum_{P \in E} n_P [P]
$$

where $n_P$ records the order of vanishing (or pole) of $f$ at $P$.

* Zeros contribute positive coefficients.
* Poles contribute negative coefficients.
* The sum of the coefficients (i.e., the degree of the divisor) is zero for any rational function:

$$
\deg(\text{div}(f)) = 0
$$

Note: Coordinates of zeros and poles may lie in an extension field $\mathbb{F}_{p^k}$.


---

## Bilinear Pairings

In linear algebra, a bilinear pairing is a function $\beta: V \times V \to K$ satisfying linearity in each component. Examples include:

1. **Dot product** in $\mathbb{R}^n$:

$$
\beta(v, w) = v_1w_1 + v_2w_2 + \dots + v_nw_n
$$

This is bilinear since:

$$
\beta(a_1v_1 + a_2v_2, w) = a_1\beta(v_1, w) + a_2\beta(v_2, w), \quad \text{and similarly for the second argument.}
$$

2. **Determinant pairing** in $\mathbb{R}^2$:

$$
\delta(v, w) = \det \begin{bmatrix} v_1 & v_2 \\ w_1 & w_2 \end{bmatrix} = v_1w_2 - v_2w_1
$$

This is *alternating*, meaning $\delta(v, v) = 0$, and $\delta(v, w) = -\delta(w, v)$.

Pairings on elliptic curves generalize this concept. Instead of mapping to $\mathbb{R}$, we map to a finite field $K$, typically to the group of roots of unity $\mu_n \subseteq K^*$.

Let $\{P_1, P_2\}$ be a basis for $E[m] \cong \mathbb{Z}/n\mathbb{Z} \times \mathbb{Z}/n\mathbb{Z}$. Then any point $P \in E[m]$ can be expressed as:

$$
P = aP_1 + bP_2, \quad \text{with } a, b \in \mathbb{Z}/n\mathbb{Z}
$$

A group endomorphism $\alpha: E \to E$ maps torsion points to torsion points and is represented by a matrix in $\mathrm{Mat}_{2 \times 2}(\mathbb{Z}/n\mathbb{Z})$. Composition of endomorphisms corresponds to matrix multiplication.

## The Weil Pairing

Let $E$ be an elliptic curve over a field $K$, and let $m \in \mathbb{Z}_{>0}$ such that $\gcd(m, \text{char}(K)) = 1$. The **Weil pairing** is a map:

$$
e_m: E[m] \times E[m] \to \mu_m
$$

where $\mu_m = \{ x \in K^* \mid x^m = 1 \}$ is the group of $m$-th roots of unity.

### Properties:

1. *Bilinearity*:

   * $e_m(P_1 + P_2, Q) = e_m(P_1, Q) e_m(P_2, Q)$
   * $e_m(P, Q_1 + Q_2) = e_m(P, Q_1) e_m(P, Q_2)$
2. *Non-degeneracy*:

   * If $e_m(P, Q) = 1$ for all $Q \in E[m]$, then $P = \mathcal{O}$
3. *Alternating*:

   * $e_m(P, P) = 1$
   * $e_m(P, Q) = e_m(Q, P)^{-1}$

## The Tate Pairing

The **Tate pairing** is a bilinear map defined for elliptic curves over finite fields, commonly used in cryptography due to its efficient computation.

Let $E$ be an elliptic curve over $\mathbb{F}_q$, and let $m \mid (q - 1)$. Denote:

* $E(\mathbb{F}_q)[m] = \{ P \in E(\mathbb{F}_q) \mid mP = \mathcal{O} \}$
* $\mu_m = \{ x \in \mathbb{F}_q^* \mid x^m = 1 \}$

Let $P \in E(\mathbb{F}_q)[m]$, $Q \in E(\mathbb{F}_q)$, and choose $R \in E(\mathbb{F}_q)$ such that $mR = Q$. Then define:

$$
\tau_m(P, Q) = e_m(P, R - \phi_q(R))
$$

where $\phi_q$ is the Frobenius endomorphism.

This gives a well-defined, non-degenerate bilinear pairing:

$$
\tau_m: E(\mathbb{F}_q)[m] \times E(\mathbb{F}_q)/mE(\mathbb{F}_q) \to \mu_m
$$

## Embedding Degree

Let $E$ be an elliptic curve over $\mathbb{F}_p$ and let $m \geq 1$ with $p \nmid m$. The **embedding degree** $k$ is defined as the smallest positive integer such that:

$$
E(\mathbb{F}_{p^k})[m] \cong \mathbb{Z}/m\mathbb{Z} \times \mathbb{Z}/m\mathbb{Z}
$$

The embedding degree determines the minimal extension $\mathbb{F}_{p^k}$ over which all $m$-torsion points are defined, and into which the Weil or Tate pairing maps. This degree is fundamental for pairing-based cryptographic schemes, where the discrete logarithm problem is transferred from the elliptic curve to a finite field.

A full implementation of pairings can be found in `src/pairings.sage`.
