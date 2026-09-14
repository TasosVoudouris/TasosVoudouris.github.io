---
title: "DGHV: Fully Homomorphic Encryption over the Integers"
description: "Walk through the van Dijk–Gentry–Halevi–Vaikuntanathan integer construction, approximate-GCD intuition, bounded evaluation, and the bootstrapping route from SHE to FHE."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Mathematical Foundations"
tags:
  - "dghv"
  - "fhe"
  - "approximate-gcd"
  - "bootstrapping"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 9
sourcePath: "experiments/homomorphic"
status: "Research Note"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.

## Fully Homomorphic Encryption over the Integers

We begin with a somewhat homomorphic encryption (SHE) scheme over the integers, as a foundation toward constructing a fully homomorphic encryption (FHE) system. Our reference is the foundational work by van Dijk, Gentry, Halevi, and Vaikuntanathan, available at [ePrint 2009/616](https://eprint.iacr.org/2009/616.pdf).

### Symmetric (Secret-Key) Version

The DGHV scheme is a symmetric encryption scheme defined over the integers. The core idea is to represent a bit $m \in \{0,1\}$ as an integer whose residue modulo a secret key has the same parity as the bit. The security of the scheme relies on hiding this residue within a large integer.

* **Key Generation:**
  The secret key $p$ is an odd integer of $\eta$ bits.

* **Encryption:**
  To encrypt a bit $m$, choose:

  * A large random integer $q$,
  * A small random integer $r$ with $|r| < 2^\rho$,

  and compute the ciphertext:

  $$
  E(m) = pq + 2r + m.
  $$

  The ciphertext is a noisy multiple of $p$ hiding the bit $m$ in its parity.

* **Decryption:**
  Given a ciphertext $c$, decryption proceeds via:

  $$
  D(c) = (c \bmod p) \bmod 2.
  $$

  Since $c \bmod p \approx 2r + m$, decryption works correctly when the noise $2r < p$.

This basic construction supports limited homomorphic operations:

* **Addition:**
  Given two ciphertexts $c_1 = pq_1 + 2r_1 + m_1$ and $c_2 = pq_2 + 2r_2 + m_2$, their sum yields:

  $$
  c_1 + c_2 = p(q_1 + q_2) + 2(r_1 + r_2) + (m_1 + m_2).
  $$

  Decryption will correctly output $m_1 + m_2 \bmod 2$, as long as $2(r_1 + r_2) < p$.

* **Multiplication:**
  Multiplying two ciphertexts yields:

  $$
  c_1 \cdot c_2 = pq' + 4r_1r_2 + 2r_1m_2 + 2r_2m_1 + m_1m_2,
  $$

  where $q'$ is a combination of the original $q_i$ and $p$. Decryption will output $m_1 \cdot m_2$ correctly, provided the resulting noise is still smaller than $p$.

The multiplication operation causes faster noise growth—approximately quadratic in the input noise—so the scheme is initially only somewhat homomorphic. The number of possible homomorphic operations is limited by the growth of noise relative to $p$.

An implementation in SageMath is provided in the GitHub repository:
[https://github.com/coron/fhe](https://github.com/coron/fhe)

This code supports the full DGHV scheme, as described in Coron, Naccache, and Tibouchi (Eurocrypt 2012):
*"Public-key Compression and Modulus Switching for Fully Homomorphic Encryption over the Integers."*
([ePrint 2011/440](https://eprint.iacr.org/2011/440))

### Correctness of the Scheme

The correctness of decryption relies on the fact that:

$$
D(E(m)) = (pq + 2r + m \bmod p) \bmod 2 = (2r + m) \bmod 2 = m,
$$

provided that $2r < p$. This condition ensures that the decryption remains unaffected by modular reduction.

For addition:

$$
\begin{aligned}
D(c_1 + c_2) &= (pq_1 + pq_2 + 2r_1 + 2r_2 + m_1 + m_2 \bmod p) \bmod 2 \\
&= (2r_1 + 2r_2 + m_1 + m_2) \bmod 2 = m_1 + m_2 \bmod 2,
\end{aligned}
$$

again assuming $2r_1 + 2r_2 < p$.

For multiplication:

$$
\begin{aligned}
D(c_1 \cdot c_2) &= ((pq_1 + 2r_1 + m_1)(pq_2 + 2r_2 + m_2) \bmod p) \bmod 2 \\
&= (4r_1r_2 + 2r_1m_2 + 2r_2m_1 + m_1m_2) \bmod 2 = m_1m_2,
\end{aligned}
$$

again under the constraint that the noise term remains bounded.

Note that noise grows linearly with addition and multiplicatively with multiplication, which fundamentally limits the homomorphic capacity unless the noise can be reduced.

### Public-Key Variant

The scheme can be converted into a public-key encryption system. The security assumption is based on the hardness of the **approximate GCD problem**: given many integers $x_i = q_i p + 2r_i$, with $r_i$ small, recover $p$.

The public key consists of $\tau$ integers $x_1, \dots, x_\tau$, each being an encryption of 0. The encryption of a bit $m \in \{0,1\}$ proceeds as:

$$
c = m + 2r + 2 \cdot \sum_{i \in S} x_i \bmod x_0,
$$

where $x_0$ is the largest $x_i$ and $S \subseteq \{1, \dots, \tau\}$ is a random subset. Decryption proceeds as before.

### Security Considerations

The security of the scheme is based on the intractability of the approximate integer GCD problem. Intuitively, if $p$ is unknown and the $x_i$ are only approximately divisible by $p$, recovering $p$ becomes computationally hard.

Parameters:

* $\eta$: bit-length of the secret key $p$,
* $\gamma$: bit-length of the public key elements $x_i$,
* $\tau$: number of public key encryptions of 0,
* $\rho$: noise bit-length in the public key,
* $\rho'$: encryption noise.

These must be chosen carefully to avoid known lattice attacks, while ensuring sufficient capacity for homomorphic operations.

### Function Evaluation Bounds

Let $f$ be a multivariate function to be evaluated homomorphically. If $\|\vec f\|$ is the $\ell_1$ norm of the coefficient vector and $d = \deg(f)$, then correct evaluation is possible under the constraint:

$$
d \leq \frac{\eta - 4 - \log_2 \|\vec f\|}{\rho' + 2}.
$$

This arises from ensuring the noise does not exceed $2^{\eta - 4}$, a bound required for correctness of homomorphic decryption. The derivation uses the fact that each multiplication roughly squares the noise and each coefficient adds to the bound linearly.

### Towards FHE and Bootstrapping

To move from SHE to FHE, it is necessary to reduce the noise in a ciphertext. Gentry introduced the technique of **bootstrapping**, where the scheme homomorphically evaluates its own decryption circuit, applied to a ciphertext and encrypted secret key. This yields a new ciphertext of the same message but with reduced noise.

The challenge is that the decryption function itself is not low-depth. Therefore, it must be “squashed” or restructured into a circuit of sufficiently low depth that the scheme can evaluate. This transformation is critical to making the scheme bootstrappable and thus fully homomorphic.

In the DGHV scheme, squashing and bootstrapping require additional encrypted information about the secret key to be included in the public key. While this allows for ciphertext refreshing, it introduces new assumptions about the hardness of recovering $p$ given auxiliary information.

### Improving Efficiency

The original DGHV scheme suffers from inefficiencies:

* The public key size is large (often >10 GB),
* Ciphertext size increases significantly with each multiplication.

To address this, follow-up work proposed key compression techniques. Rather than publishing the entire $x_i$, one can publish pseudorandom values $X_i$ along with small correction terms $d_i$, such that $x_i = X_i - d_i$ is small modulo $p$. Only the $d_i$ and the PRNG seed need be stored, drastically reducing key size.

Further optimizations include modulus switching and parameter tuning to reduce ciphertext expansion and improve practical efficiency.

### Batching and Vectorized FHE

Later schemes (e.g., [Eurocrypt 2013](https://www.iacr.org/archive/eurocrypt2013/78810313/78810313.pdf)) extended the DGHV scheme to support **batching**, where multiple plaintext bits are packed into a single ciphertext, allowing SIMD-style operations.
