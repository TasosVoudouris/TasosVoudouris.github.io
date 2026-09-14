---
title: "Packed Secret Sharing: Encoding Multiple Secrets in One Polynomial"
description: "Extend polynomial secret sharing from one scalar to a vector of secrets, derive privacy and reconstruction thresholds, and examine homomorphic degree growth."
pubDate: "2025-05-17"
updatedDate: "2026-09-12"
topics:
- "Secret Sharing"
- "MPC"
- "Mathematical Foundations"
- "Cryptographic Engineering"
tags:
- "packed-secret-sharing"
- "vector-secret-sharing"
- "polynomials"
- "lagrange"
- "homomorphic-operations"
difficulty: "Intermediate"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 6
sourcePath: "experiments/threshold-cryptography/packed-sharing"
draft: false
---
Packed secret sharing is the first place where the series moves from sharing **one scalar** to sharing a **vector of secrets** with one polynomial. The basic idea is still interpolation over a finite field, but the placement of secret values, random masks, and party shares is arranged so that several secrets travel together.

## 1. Introduction
Packed Secret Sharing is an extension of traditional secret sharing schemes that allows for the efficient encoding and distribution of multiple secrets within a single polynomial structure. This method enhances communication efficiency and is particularly useful in scenarios such as secure multiparty computation (MPC), where multiple secrets must be simultaneously shared and later reconstructed.

Unlike classical Shamir Secret Sharing, which encodes one secret as a distinguished polynomial value, packed secret sharing constrains one polynomial at several designated **secret points** so that multiple secrets are carried by the same polynomial. The implementation uses negative integer representatives for those field points, but that sign convention is only a convenient way to keep the secret, randomness, and share points disjoint. This report presents an overview of the construction, theoretical foundation, threshold guarantees, and practical limitations of packed secret sharing.

## 2. Theoretical Foundation
Let $\mathbb{F}_q$ be a finite field of prime order $q$, and let $K$ be the number of secrets to encode. The encoding process selects $K$ fixed, distinct field elements $\alpha_1,\dots,\alpha_K\in\mathbb{F}_q$ and chooses a polynomial $f\in\mathbb{F}_q[x]$ such that:

$$
f(\alpha_i) = s_i, \quad \text{for } i = 1, \dots, K
$$

To obtain privacy, choose another $T$ distinct field elements $\beta_1,\dots,\beta_T$ and assign independent uniform random values $r_1,\dots,r_T$. Interpolating the $K+T$ constraints produces a polynomial of degree at most $K+T-1$. The random constraints are what hide the packed secrets from small coalitions of share holders.

Once the polynomial is fixed, evaluate it at $N$ additional public, pairwise-distinct field elements $\gamma_1,\dots,\gamma_N$ that are disjoint from the secret and randomness points. Party $j$ receives the share $f(\gamma_j)$.

## 3. Reconstruction Threshold
Reconstruction of the original $K$ secrets requires knowledge of at least $K + T$ valid shares. This threshold arises from the need to interpolate a polynomial of degree $d = K + T - 1$, which uniquely determines the encoded secrets. The interpolation is performed using Lagrange interpolation over $\mathbb{F}_q$.

Thus, the scheme satisfies the following threshold properties:

* **Privacy threshold:** Under the stated packed construction, any set of at most $T$ shares is statistically independent of the $K$ packed secrets.
* **Reconstruction threshold:** Any $K + T$ or more shares suffice to reconstruct the secrets.

## 4. Homomorphic Operations
Packed secret sharing supports **component-wise homomorphic operations** on packed values. Let $f$ and $g$ be two polynomials representing two packed secret sharings:

* **Addition:** $f(x) + g(x)$ yields a polynomial sharing the component-wise sum of the secrets.
* **Multiplication:** $f(x) \cdot g(x)$ yields a polynomial whose evaluations correspond to the product of the secrets. However, this increases the degree of the underlying polynomial to $2(K + T) - 2$, and thus requires more shares for correct reconstruction.

This behavior under multiplication introduces the need for **degree reduction** or **resharing** in protocols that use multiple multiplications, to keep the reconstruction threshold bounded.

## 5. Limitations and Practical Considerations
* **Field size:** The field must contain enough distinct evaluation points for all secret, randomness, and share locations. Arithmetic is intentionally performed modulo $q$; application values that are not naturally field elements need an explicit encoding.
* **Evaluation points:** Secret, randomness, and share points must be pairwise distinct. Using negative representatives for one set and positive representatives for another is a coding convention, not a cryptographic requirement.
* **Interpolation cost:** A single evaluation from precomputed Lagrange weights can be linear in the number of shares, while recovering all coefficients or repeatedly interpolating naively can be quadratic. Structured evaluation domains allow FFT/NTT-style improvements, which we study later in this series.
* **No public verifiability:** The basic scheme is not verifiable. Without commitment schemes (e.g., Pedersen or KZG commitments), corrupted shares or malicious parties cannot be detected.
* **Multiplicative depth:** Each multiplication increases the degree of the polynomial. Hence, only a bounded number of homomorphic multiplications can be performed before reconstruction becomes impossible due to insufficient threshold.

## 6. Security Model
The scheme achieves **information-theoretic privacy** under the assumption that the $T$ masking values are sampled independently and uniformly from $\mathbb{F}_q$ and the evaluation points satisfy the required distinctness conditions. The exact privacy statement is a linear-algebra property of the corresponding evaluation map, not merely a consequence of using a large field.

## 7. Conclusion
Packed Secret Sharing provides an efficient mechanism to encode and distribute multiple secrets in a single sharing structure. Its threshold guarantees, coupled with support for homomorphic operations, make it a powerful primitive in modern cryptographic protocols such as secure multiparty computation and threshold cryptography. However, its use requires careful parameter selection and consideration of degree growth in arithmetic circuits.
