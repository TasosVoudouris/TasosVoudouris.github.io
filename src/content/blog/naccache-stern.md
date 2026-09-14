---
title: "Naccache–Stern: Higher Residuosity and Additive Homomorphism"
description: "Study the Naccache–Stern message representation, small-prime CRT structure, decryption through subgroup residues, and its additive homomorphic behavior."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Number Theory"
tags:
  - "naccache-stern"
  - "crt"
  - "higher-residuosity"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 6
sourcePath: "experiments/homomorphic"
status: "Experimental"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.

The Naccache–Stern public-key encryption scheme extends higher-residuosity ideas to a larger message space while preserving an additive homomorphism.

---

## 1. Overview

The Naccache–Stern (NS) scheme encrypts integers $m$ modulo

$$
\sigma = \prod_{i=1}^k p_i,
$$

where $\{p_1,\dots,p_k\}$ is a chosen set of small primes. It achieves semantic security under the intractability of factoring and discrete logarithms in $\mathbb Z_n^*$, and offers an additive homomorphism:

$$
\text{Enc}(m_1)\cdot \text{Enc}(m_2)\equiv \text{Enc}(m_1+m_2)\pmod n.
$$

---

## 2. Key Generation

1. **Small-prime set**: Fix $p_1,\dots,p_k$. Partition into two halves with products

   $$
   u=\prod_{i=1}^{k/2}p_i,
   \quad
   v=\prod_{i=k/2+1}^{k}p_i.
   $$
2. **Large primes**: Choose random primes $a,b$ and set

   $$
   p=2au+1,\quad q=2bv+1,
   $$

   repeating until both $p,q$ are prime.
3. **Modulus**: $n=pq$, $\varphi(n)=(p-1)(q-1)$.
4. **Generator**: Select $g\in\mathbb Z_n^*$ such that
   $\;g^{\varphi(n)/p_i}\not\equiv1\pmod n$ for each small $p_i$.
5. **Public key**: $(n,\{p_i\})$ and generator $g$.
   **Private key**: the factorization $(p,q)$.

---

## 3. Encryption

To encrypt $m\in\{0,\dots,\sigma-1\}$:

$$
c = g^m \bmod n.
$$

(Note: a random blinding factor can be introduced for IND-CPA security.)

---

## 4. Decryption

1. For each $p_i$, compute

   $$
   c_i = c^{\varphi(n)/p_i}\bmod n,
   $$

   which equals $\bigl(g^{\varphi(n)/p_i}\bigr)^m$.
2. Recover the residue $m_i\in\{0,\dots,p_i-1\}$ by brute-force discrete log in the order-$p_i$ subgroup.
3. Reconstruct $m$ from the system

   $$
   m \equiv m_i\pmod{p_i}\quad(i=1,\dots,k)
   $$

   using the Chinese Remainder Theorem.

---

## 5. Homomorphic Property

Multiplication of ciphertexts corresponds to addition of plaintexts modulo $\sigma$:

$$
c_1 = g^{m_1},\;c_2 = g^{m_2}
\;\Longrightarrow\;
c_1c_2 = g^{m_1+m_2}\pmod n.
$$

---

## 6. Security

* **Factoring** $n=pq$ is assumed hard.
* **Discrete logarithm** in the full group is hard; decryption only requires discrete logs in small subgroups of order $p_i$, which is efficient by design.
* **Semantic security** follows from the subgroup‐residuosity assumption in $\mathbb Z_n^*$.

**Reference:** Naccache, D., & Stern, J. (1998). A new public‐key cryptosystem based on higher residues. *Proceedings of Eurocrypt 1998*.
