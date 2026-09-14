---
title: "The Paillier Cryptosystem"
description: "A concise introduction to Paillier public-key encryption and its additive homomorphic property, with key-generation and implementation notes."
pubDate: "2025-05-29"
updatedDate: '2026-09-12'
topics:
- "Public-Key Cryptography"
- "Homomorphic Encryption"
tags:
- "paillier"
- "homomorphic-encryption"
- "public-key-encryption"
difficulty: "Intermediate"
sourcePath: "experiments/ready-material/paillier"
series: "Homomorphic Encryption"
seriesOrder: 4
draft: false
---
The *Paillier cryptosystem* is a public-key cryptographic scheme notable for its additive homomorphic property. This feature allows certain computations to be performed directly on ciphertexts, yielding valid encrypted results without decryption. The system is based on the decisional composite residuosity assumption and provides semantic security under chosen plaintext attacks.

The core parameters of the Paillier cryptosystem consist of two large primes $p$ and $q$, whose product $n = pq$ defines the modulus. The system operates in the multiplicative group modulo $n^2$, denoted $\mathbb{Z}_{n^2}^*$, and achieves encryption randomness through the use of a blinding factor $r \in \mathbb{Z}_n^*$, ensuring probabilistic encryption.

#### Key generation

We proceed by selecting random primes $p$ and $q$, then computing $n = pq$, which serves as the public modulus. The value $\lambda = \text{lcm}(p-1, q-1)$ serves as a secret key component. A generator $g \in \mathbb{Z}_{n^2}^*$ is often chosen as $g = n + 1$, which simplifies certain computations. The value $\mu$, defined as the modular inverse of $L(g^\lambda \bmod n^2) \mod n$, is required for decryption. The function $L(u) = \frac{u - 1}{n}$ is used repeatedly in the decryption process.

#### Encryption 

The encryption of a message $m \in \mathbb{Z}_n$ is performed as follows: a random $r \in \mathbb{Z}_n^*$ is selected, and the ciphertext is computed using

$$
c = g^m \cdot r^n \bmod n^2.
$$

The randomness introduced by $r$ ensures semantic security: the same plaintext encrypted twice will yield different ciphertexts.

#### Decryption

The decryption is achieved using the private key components $\lambda$ and $\mu$. Specifically, given a ciphertext $c$, the plaintext $m$ is recovered by computing

$$
m = L(c^\lambda \bmod n^2) \cdot \mu \bmod n.
$$

This operation effectively removes the randomness and recovers the original message modulo $n$.

In addition to basic encryption and decryption, the Paillier cryptosystem supports *homomorphic operations*:

* **Homomorphic addition** of two encrypted values is accomplished by multiplying the ciphertexts:

  $$
  c_{\text{sum}} = c_1 \cdot c_2 \bmod n^2.
  $$

  This results in the encryption of $m_1 + m_2 \mod n$, assuming $c_1 = \text{Enc}(m_1)$ and $c_2 = \text{Enc}(m_2)$.

* **Homomorphic subtraction** follows the same principle, using the modular inverse of the second ciphertext:

  $$
  c_{\text{diff}} = c_1 \cdot c_2^{-1} \bmod n^2,
  $$

  which decrypts to $m_1 - m_2 \mod n$.

* **Scalar multiplication** is performed by exponentiating the ciphertext:

  $$
  c_{\text{mul}} = c^a \bmod n^2,
  $$

  where the result encrypts $a \cdot m \mod n$.

* **Linear combinations** of two encrypted values can be computed as:

  $$
  c = c_1^a \cdot c_2^b \cdot r^n \bmod n^2,
  $$

  which yields the encryption of $a \cdot m_1 + b \cdot m_2 \mod n$, again incorporating fresh randomness.

The implementations in Python and SageMath are in `src/pailier.sage , pailier.py` demonstrate each of these features clearly. Key generation uses 512-bit primes to produce a modulus of approximately 1024 bits. Messages are encrypted with fresh randomness in the SageMath code, and arithmetic operations are verified by decrypting the resulting ciphertexts. The correctness of the homomorphic addition, subtraction, and linear combination is verified by comparing with expected plaintext results. The Python code is just a naive coding example.

Importantly, due to its probabilistic encryption and homomorphic properties, the Paillier cryptosystem is well-suited for applications such as secure multiparty computation, electronic voting, and privacy-preserving data aggregation. One natural next step would be to enhance the system with *threshold decryption*, enabling decryption to be split among multiple parties, increasing robustness and trust distribution. Furthermore, combining Paillier with zero-knowledge proofs can enable verifiable computations without revealing intermediate data. These will be done in the future.
