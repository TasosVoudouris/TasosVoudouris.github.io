---
title: "Shamir's Secret Sharing: Lagrange Interpolation and Perfect Privacy"
description: "Derive Shamir secret sharing from polynomial interpolation, reconstruct a threshold secret with Lagrange coefficients, and prove information-theoretic privacy."
pubDate: "2025-05-20"
updatedDate: "2026-09-12"
topics:
- "Secret Sharing"
- "Threshold Cryptography"
- "Mathematical Foundations"
- "MPC"
tags:
- "shamir-secret-sharing"
- "lagrange-interpolation"
- "threshold"
- "finite-fields"
- "perfect-privacy"
difficulty: "Intermediate"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 2
sourcePath: "experiments/threshold-cryptography/shamir"
draft: false
---
Shamir's Secret Sharing (SSS), introduced by Adi Shamir in 1979, replaces the all-or-nothing structure of additive sharing with a configurable threshold. A dealer distributes $n$ shares so that **any $t$ shares reconstruct the secret**, while every coalition of fewer than $t$ shares has no information about it.

The construction is one of the cleanest examples of algebra becoming a cryptographic primitive: the secret is the value of a random polynomial at zero, and reconstruction is simply polynomial interpolation over a finite field.

## 1. Lagrange Interpolation over a Field

Let $\mathbb{F}$ be a field (e.g., $\mathbb{Z}_p$ for prime $p$). Given $t$ distinct points $(x_0, y_0), \ldots, (x_{t-1}, y_{t-1}) \in \mathbb{F}^2$, there exists a unique polynomial $f(x) \in \mathbb{F}[x]$ of degree at most $t-1$ such that:

$$
f(x_i) = y_i \quad \text{for all } i = 0, \ldots, t-1.
$$

This polynomial can be constructed via **Lagrange interpolation**:

$$
f(x) = \sum_{j=0}^{t-1} y_j \cdot \ell_j(x),
$$

where $\ell_j(x)$ are the Lagrange basis polynomials:

$$
\ell_j(x) = \prod_{\substack{0 \leq m < t \\ m \neq j}} \frac{x - x_m}{x_j - x_m}.
$$

These basis polynomials satisfy the Kronecker delta property:

$$
\ell_j(x_i) =
\begin{cases}
1 & \text{if } i = j, \\
0 & \text{if } i \neq j.
\end{cases}
$$

Thus, the interpolation polynomial $f(x)$ satisfies:

* $f(x_j) = y_j$ for all $j$,
* Uniqueness: No other polynomial of degree less than $t$ agrees with these values at the specified points.

### Remark

This interpolation technique extends naturally to finite fields $\mathbb{F} = \mathbb{Z}_p$, making it suitable for cryptographic applications.

## 2. Shamir’s Secret Sharing Scheme

### Setup

Let:

* $p$ be a prime number,
* $\mathbb{F} = \mathbb{Z}_p$ be the finite field,
* $m \in \mathbb{F}$ be the secret,
* $t$ be the reconstruction threshold,
* $n \geq t$ be the number of participants.

### Sharing Phase

1. The dealer selects a random polynomial $f(x) \in \mathbb{F}[x]$ of degree $t-1$, with:

   $$
   f(x) = a_0 + a_1x + a_2x^2 + \cdots + a_{t-1}x^{t-1},
   $$

   where $a_0 = m$ and $a_1, \ldots, a_{t-1} \in \mathbb{F}$ are sampled uniformly at random.

2. The dealer computes shares:

   $$
   \text{Share}_i = (x_i, f(x_i)) \in \mathbb{F}^2, \quad \text{for } i = 1, \ldots, n,
   $$

   where $x_i \in \mathbb{F} \setminus \{0\}$ are distinct and public.

Each party $i$ receives share $(x_i, f(x_i))$.

### Reconstruction Phase

Given any subset of $t$ shares $\{(x_j, f(x_j))\}_{j=1}^t$, the participants can interpolate the unique degree-$t-1$ polynomial $f(x)$ using Lagrange interpolation. The secret is then recovered as:

$$
m = f(0) = \sum_{j=1}^{t} f(x_j) \cdot \lambda_j,
$$

where

$$
\lambda_j = \prod_{\substack{1 \leq k \leq t \\ k \neq j}} \frac{x_k}{x_k - x_j}
$$

are the Lagrange coefficients evaluated at $x = 0$.

### Efficient Evaluation

To recover only the secret $f(0)$ (not the entire polynomial), the following direct formula can be used:

$$
f(0) = \sum_{j=0}^{t-1} f(x_j) \cdot \prod_{\substack{0 \leq m < t \\ m \neq j}} \frac{x_m}{x_m - x_j}.
$$

## 3. Security Analysis

### Information-Theoretic Security

Let $\mathcal{S} = \{(x_i, y_i)\}_{i=1}^{t-1}$ be any set of $t-1$ shares. We want to show that:

> For every $m \in \mathbb{F}$, the distribution of $\mathcal{S}$ is uniform and independent of $m$.

This is established as follows:

* Fix $x_1, \ldots, x_{t-1} \in \mathbb{F} \setminus \{0\}$, all distinct.
* The secret $m \in \mathbb{F}$ is embedded as the constant coefficient $a_0$ of the polynomial.
* For each possible $m$, the dealer samples the remaining coefficients $a_1, \ldots, a_{t-1} \in \mathbb{F}$ uniformly and independently.
* The map:

  $$
  \phi: \mathbb{F}^{t-1} \to \mathbb{F}^{t-1}, \quad (a_1, \ldots, a_{t-1}) \mapsto \left(f(x_1), \ldots, f(x_{t-1})\right)
  $$

  is an **injective linear map** because the Vandermonde matrix formed by evaluating monomials at distinct $x_i$'s is invertible in $\mathbb{F}$.
* Hence, the distribution of $(f(x_1), \ldots, f(x_{t-1}))$ is uniform over $\mathbb{F}^{t-1}$, independent of $m$.

### Conclusion

Shamir's scheme provides **information-theoretic privacy**: any coalition of fewer than $t$ participants obtains no information about the secret. More precisely, for all $m_1,m_2\in\mathbb{F}$, the distribution of any fixed set of fewer than $t$ shares is identical under secret $m_1$ and secret $m_2$. This statement assumes the non-constant coefficients are sampled uniformly and independently.

## What Shamir Sharing Does Not Provide by Itself

Basic SSS gives privacy and threshold reconstruction, but it does **not** by itself tell a participant whether the dealer distributed mutually consistent shares. A malicious dealer can send values that do not lie on one common degree-$(t-1)$ polynomial. That gap motivates **verifiable secret sharing (VSS)** and, later in this series, distributed key generation.

It also does not automatically provide robustness against corrupted shares. Robust reconstruction requires additional mechanisms such as commitments, consistency checks, or error-correcting decoding; we return to that problem in the Gao-decoding article.
