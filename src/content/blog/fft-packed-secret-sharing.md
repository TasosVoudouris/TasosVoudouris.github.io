---
title: "FFT-Based Packed Secret Sharing over Finite Fields"
description: "Implement packed secret sharing on radix-2 and radix-3 roots-of-unity domains and connect finite-field FFTs to efficient MPC encoding and reconstruction."
pubDate: "2025-05-17"
updatedDate: "2026-09-12"
topics:
- "Secret Sharing"
- "MPC"
- "Mathematical Foundations"
- "Cryptographic Engineering"
tags:
- "packed-secret-sharing"
- "fft"
- "ntt"
- "roots-of-unity"
- "finite-fields"
- "mpc"
difficulty: "Advanced"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 9
sourcePath: "experiments/threshold-cryptography/fft-packed-sharing"
draft: false
---
This article takes the packed-sharing construction from the previous section and replaces generic interpolation with structured finite-field transforms. The implementation deliberately uses separate radix-2 and radix-3 domains: one domain encodes the secret/randomness vector, while another domain carries the party shares.

The result is a useful worked example of how the same FFT ideas used in polynomial arithmetic can become a protocol-engineering tool in MPC.

## 1. Introduction

This report presents a complete implementation of **packed secret sharing** based on the **Fast Fourier Transform (FFT)** over finite fields. The construction leverages number-theoretic transforms, specifically radix-2 and radix-3 FFTs, for efficient polynomial evaluation and interpolation. It is suitable for secure multiparty computation (MPC) and other privacy-preserving cryptographic protocols.

## 2. Mathematical Foundations

### 2.1 Finite Fields and Roots of Unity

Let $\mathbb{F}_q$ be a finite field of prime order $q$, such that $q \equiv 1 \pmod{n}$. Then, $\mathbb{F}_q$ contains a **primitive $n$-th root of unity**, denoted $\omega \in \mathbb{F}_q$, satisfying:

$$
\omega^n = 1 \quad \text{and} \quad \omega^k \ne 1 \quad \text{for all } 1 \le k < n.
$$

This root enables the application of the **Discrete Fourier Transform (DFT)** over $\mathbb{F}_q$, defined for a vector $a = (a_0, a_1, \dots, a_{n-1})$ by:

$$
\hat{a}_j = \sum_{i=0}^{n-1} a_i \cdot \omega^{ij} \mod q.
$$

### 2.2 FFT over $\mathbb{F}_q$

To efficiently compute the DFT, we implement the **Cooley-Tukey FFT algorithm** for both radix-2 and radix-3 factorizations of $n$, assuming $n = 2^k$ or $n = 3^k$.

The radix-2 FFT recursively evaluates the polynomial by splitting it into even and odd terms:

$$
A(x) = A_{\text{even}}(x^2) + x A_{\text{odd}}(x^2).
$$

Similarly, radix-3 FFT decomposes as:

$$
A(x) = A_0(x^3) + x A_1(x^3) + x^2 A_2(x^3).
$$

Both transforms are invertible over $\mathbb{F}_q$ by using $\omega^{-1}$ and scaling the result by $n^{-1} \mod q$.

---

## 3. Cryptographic Construction

### 3.1 Packed Secret Sharing Scheme

Given:

* Number of secrets: $K$
* Privacy threshold: $T$
* Total number of shares: $N = ORDER3 - 1$

We use a polynomial with **degree strictly below `ORDER2`** to encode both secrets and randomness:

* The secrets occupy the first $K$ slots.
* The remaining $T$ slots are filled with random field elements to ensure $T$-privacy.

### 3.2 Share Generation

Let $f(x) \in \mathbb{F}_q[x]$ be the encoding polynomial constructed as follows:

1. Construct the **evaluation vector**:

   $$
   \texttt{small\_values} = [0] \parallel s_1 \parallel \dots \parallel s_K \parallel r_1 \parallel \dots \parallel r_T,
   $$

   where $r_i \in_R \mathbb{F}_q$ are random values for privacy.

2. Compute the coefficients of the polynomial via **inverse radix-2 FFT**:

   $$
   \texttt{small\_coeffs} = \texttt{fft2\_backward(small\_values)}.
   $$

3. Pad the coefficient vector to match the required FFT size:

   $$
   \texttt{large\_coeffs} = \texttt{small\_coeffs} \parallel [0]^{ORDER3 - ORDER2}.
   $$

4. Generate the shares by evaluating the polynomial at $ORDER3$ roots of unity (except the 0-th root):

   $$
   \texttt{shares} = \texttt{fft3\_forward(large\_coeffs)}[1:].
   $$

### 3.3 Reconstruction

To reconstruct the original secrets from $N$ shares:

1. Reconstruct the full evaluation vector:

   $$
   \texttt{large\_values} = [0] \parallel \texttt{shares}.
   $$

2. Apply **inverse radix-3 FFT** to retrieve the polynomial coefficients:

   $$
   \texttt{large\_coeffs} = \texttt{fft3\_backward(large\_values)}.
   $$

3. Truncate to obtain the original low-degree polynomial:

   $$
   \texttt{small\_coeffs} = \texttt{large\_coeffs}[:ORDER2].
   $$

4. Use **radix-2 FFT** to recover the secret evaluations:

   $$
   \texttt{small\_values} = \texttt{fft2\_forward(small\_coeffs)}.
   $$

5. Extract the secrets:

   $$
   [s_1, \dots, s_K] = \texttt{small\_values}[1:K+1].
   $$

---

## 4. Security and Correctness

### 4.1 Privacy

The $T$ independently sampled field elements provide the masking dimension used for **$T$-privacy** in this construction: up to $T$ share evaluations are statistically independent of the packed secrets, assuming the secret/randomness/share evaluation domains are disjoint and the corresponding interpolation map has full rank.

### 4.2 Correctness

Correctness follows from the fact that:

* The FFT is a bijection over $\mathbb{F}_q^n$ under a primitive $n$-th root of unity.
* The inverse FFT yields the original polynomial coefficients.
* Evaluation and interpolation over disjoint sets of roots ensures non-interference between secrets and shares.

---

## 5. Implementation Summary

* Modular arithmetic over $\mathbb{F}_q$ with $q$ generated to support both $2^k$ and $3^k$ roots of unity.
* Forward and inverse FFT routines for radix-2 and radix-3 implementations.
* Correct padding and alignment of vectors for efficient evaluation and reconstruction.
* Integration of the FFT pipeline into a packed secret sharing scheme, enabling efficient encoding of multiple secrets per polynomial.

---

## 6. Applications

This FFT-based packed secret sharing scheme enables:

* Efficient secure multiparty computation (MPC) protocols.
* Secret sharing with vectorized secrets.
* Homomorphic evaluation on shared data using field arithmetic.

When a suitable roots-of-unity domain exists, FFT-based evaluation and interpolation reduce transform cost to quasi-linear $O(n\log n)$ field operations. That advantage is structural: it does not apply to arbitrary evaluation points without additional machinery.
