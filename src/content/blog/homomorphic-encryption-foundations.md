---
title: "Homomorphic Encryption: Concepts, Correctness, Noise, and Bootstrapping"
description: "A structured introduction to computation on ciphertexts: correctness, compactness, PHE/SHE/leveled/FHE taxonomy, arithmetic circuits, noise growth, relinearization, modulus switching, bootstrapping, and security boundaries."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
tags:
  - "homomorphic-encryption"
  - "fhe"
  - "bootstrapping"
  - "noise"
  - "circuits"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 1
sourcePath: "experiments/homomorphic"
status: "Research Note"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.


## Outsourcing Storage and Computation

Let $A$ be a client (e.g., a company) that wishes to store sensitive data in the cloud $C$. To preserve confidentiality, $A$ encrypts the data before uploading it to $C$.

However, $A$ also wants to perform computations on the encrypted data *without decrypting it locally*. The goal is to allow the cloud to evaluate a function $f$ on encrypted inputs and return an encrypted result—**without ever learning the plaintexts**.

<div align="center">
  <img src="/images/homomorphic/homo1.png" alt="Homomorphic Computation Outsourcing"/>
</div>

### Solution: Homomorphic Encryption (HE)

HE enables computations directly on encrypted data. The cloud can return encrypted results that, once decrypted, yield the output as if the function had been applied directly to the plaintexts.

---

Homomorphic Encryption (HE) is a cryptographic primitive that enables computation on encrypted data without requiring decryption. This property allows for meaningful data processing while preserving the confidentiality of the underlying plaintexts. At first glance, this may seem contradictory: under classical encryption schemes such as AES, any computation on encrypted data necessitates prior decryption, thereby exposing the plaintext and violating privacy. Homomorphic encryption circumvents this limitation by allowing certain algebraic operations to be performed directly on ciphertexts, yielding encrypted outputs that, once decrypted, match the result of applying the same operations to the original plaintexts.

The realization of such a powerful construct is non-trivial. It took more than three decades of research for the first plausible construction to emerge, proposed by Craig Gentry in 2009. Gentry's work demonstrated that fully homomorphic encryption (FHE) was theoretically possible, although the original scheme was impractical for real-world use. Since then, substantial progress has been made toward practical implementations, with schemes such as BGV (Brakerski–Gentry–Vaikuntanathan, 2011), BFV (Brakerski–Fan–Vercauteren, 2012), CKKS (Cheon–Kim–Kim–Song, 2016), FHEW, TFHE, and GSW (Gentry–Sahai–Waters, 2013) significantly improving efficiency and applicability.

A distinguishing feature of any homomorphic encryption scheme is the inclusion of an *evaluation algorithm* in addition to the standard encryption, decryption, and key generation procedures. This algorithm enables computations to be carried out directly on ciphertexts. Consider the following setting: an individual, Alice, possesses sensitive data $x$ (e.g., medical history). A third party, such as a company, has a proprietary model $F$ (e.g., a trained machine learning function) that can produce valuable predictions when applied to such data. Neither party is willing to share their respective inputs—Alice does not wish to reveal her data, and the company does not wish to disclose its model.

Homomorphic encryption offers a solution: Alice encrypts her data under the public key $pk$ and sends the resulting ciphertext $C$ to the company. The company then evaluates the function $F$ homomorphically on $C$, obtaining an encrypted result $C'$ corresponding to $F(x)$. Crucially, this computation is carried out without access to Alice’s secret key $sk$. Alice can then use her secret key to decrypt $C'$, thereby obtaining $F(x)$ while preserving the confidentiality of both the data and the model.

This functionality is formally captured by the following definition:


## Formal Definition

Let $\textsf{HE} = (\textsf{KeyGen}, \textsf{Encrypt}, \textsf{Decrypt}, \textsf{Evaluate})$ be a tuple of efficient algorithms:

* $(\mathsf{sk}, \mathsf{pk}) \leftarrow \textsf{KeyGen}(1^\lambda, 1^d)$
  Generates a secret key $\mathsf{sk}$ and public key $\mathsf{pk}$ given a security parameter $\lambda$ and a functionality parameter $d$ (e.g., polynomial degree or multiplicative depth).

* $c_i \leftarrow \textsf{Encrypt}(\mathsf{pk}, m_i)$
  Encrypts a plaintext message $m_i$, producing a fresh ciphertext $c_i$.

* $c^* \leftarrow \textsf{Evaluate}(\mathsf{pk}, f, c_1, \ldots, c_n)$
  Applies the evaluation algorithm to the ciphertexts $c_1, \ldots, c_n$ and the function description $f$, resulting in a new ciphertext $c^*$ that encrypts $f(m_1, \ldots, m_n)$.

* $m^* = \textsf{Decrypt}(\mathsf{sk}, c^*)$
  Decrypts the evaluated ciphertext $c^*$ using the secret key $\mathsf{sk}$, yielding the final result $m^* = f(m_1, \ldots, m_n)$.

This structure enables non-interactive and privacy-preserving computation over encrypted data, making HE a foundational tool for secure outsourced computation, privacy-preserving machine learning, and encrypted database queries.


<div align="center">
  <img src="/images/homomorphic/connection.png" alt="All in one"/>
</div>

---

## Correctness

A homomorphic encryption scheme is *correct* if:

$$
\textsf{Decrypt}(\mathsf{sk}, \textsf{Evaluate}(\mathsf{pk}, f, \textsf{Encrypt}(\mathsf{pk}, m_1), \ldots, \textsf{Encrypt}(\mathsf{pk}, m_n))) = f(m_1, \ldots, m_n)
$$

---

## Classification of Homomorphic Encryption

| Type                   | Description                                                                       |
| ---------------------- | --------------------------------------------------------------------------------- |
| **PHE** (Partially HE) | Supports *only one* operation (either addition **or** multiplication).            |
| **SHE** (Somewhat HE)  | Supports a *bounded number* of both operations (e.g., circuits of limited depth). |
| **LHE** (Leveled HE)   | Supports functions up to a pre-declared depth $d$, depending on parameters.       |
| **FHE** (Fully HE)     | Supports *arbitrary depth* circuits — unlimited additions and multiplications.    |

---



---

## Circuits and Boolean Logic in Homomorphic Encryption

Homomorphic Encryption (HE) schemes enable the evaluation of arithmetic or Boolean circuits over encrypted data. In the Boolean case, operations on bits are interpreted as follows:

* **Addition** corresponds to the bitwise XOR operation:

  $$
  a \oplus b = a + b \mod 2
  $$
* **Multiplication** corresponds to the bitwise AND operation:

  $$
  a \cdot b
  $$

This means that an HE scheme allows one to compute the encryption of a sum or product of messages by performing operations directly on the ciphertexts. For example, given two ciphertexts

$$
c_1 = \textsf{Encrypt}(pk, m_1), \quad c_2 = \textsf{Encrypt}(pk, m_2),
$$

it is possible to compute a new ciphertext $c_{\text{add}}$ such that

$$
\textsf{Decrypt}(sk, c_{\text{add}}) = m_1 + m_2.
$$

<div align="center">
  <img src="/images/homomorphic/actions1.png" alt="Homomorphic Addition"/>
</div>

Similarly, a ciphertext $c_{\text{mul}}$ representing the product $m_1 \cdot m_2$ can be computed directly from $c_1$ and $c_2$, without accessing the secret key:

$$
\textsf{Decrypt}(sk, c_{\text{mul}}) = m_1 \cdot m_2.
$$

<div align="center">
  <img src="/images/homomorphic/actions2.png" alt="Homomorphic Multiplication"/>
</div>

There exist classical encryption schemes that are homomorphic with respect to **a single operation**. These are referred to as **partially homomorphic encryption** (PHE) schemes. Two canonical examples are:

* **RSA Encryption**:
  The RSA encryption function

  $$
  \textsf{Enc}_{e, N}^{\text{RSA}}(m) := m^e \mod N
  $$

  is multiplicatively homomorphic. That is,

  $$
  \textsf{Enc}(m_1) \cdot \textsf{Enc}(m_2) \mod N = \textsf{Enc}(m_1 \cdot m_2).
  $$

* **ElGamal Encryption**:
  Given public parameters $(g, h = g^x)$, the ElGamal encryption of a message $m$ is

  $$
  \textsf{Enc}_{g,h}^{\text{EG}}(m) = (g^r, h^r \cdot m),
  $$

  where $r$ is randomly chosen. The scheme satisfies:

  $$
  \textsf{Enc}(m_1) \cdot \textsf{Enc}(m_2) = (g^{r_1 + r_2}, h^{r_1 + r_2} \cdot m_1 \cdot m_2),
  $$

  preserving multiplicativity under component-wise multiplication.

Modern HE schemes extend this idea to support **both** homomorphic addition and multiplication. However, these are typically limited to operations expressible by arithmetic circuits composed solely of addition and multiplication gates. The evaluation algorithm $\textsf{Eval}$ is defined only over such circuits, and more complex operations must be expressed in terms of these primitives.

For instance, consider the arithmetic circuit representation of the function

$$
F(m_1, m_2, m_3, m_4) = m_1 \cdot m_2 \cdot m_4 + m_3 \cdot m_4.
$$

This functionality can be evaluated homomorphically by any HE scheme that supports the required multiplicative depth.

To bridge the arithmetic and Boolean worlds, it is important to observe that every Boolean function can be represented using only **NAND gates**, due to their functional completeness. Specifically, the NAND operation is defined as:

$$
\text{nand}(a, b) = 1 + a \cdot b \mod 2.
$$

This observation is significant because an HE scheme that can homomorphically evaluate both addition and multiplication over bits (i.e., XOR and AND) can in principle evaluate any Boolean circuit. The use of NAND as a basis highlights that HE, when applied to bit-level representations, is sufficient to achieve universal computation in the encrypted domain.

---

## Security Notions

* **Semantic Security (IND-CPA):**
  Ciphertexts hide all partial information about plaintexts, even against chosen-plaintext attacks.
* **Strong Homomorphism:**
  Evaluated ciphertexts should be *indistinguishable* from fresh ciphertexts—same distribution.
* **Compactness:**
  The size and decryption time of ciphertexts do **not** depend on the complexity of function $f$.
* **Circuit Privacy:**
  The evaluated ciphertext should not reveal *which* function $f$ was applied—only the output.

---

## Multi-Hop HE

An HE scheme is *multi-hop* if its output ciphertext can be used as input for another evaluation:

$$
c^{(1)} = \textsf{Evaluate}(f_1, c_1, \ldots), \quad c^{(2)} = \textsf{Evaluate}(f_2, c^{(1)}, \ldots)
$$

---

## From Secret-Key to Public-Key HE

According to \[Rothblum, 2010], **any compact, multi-hop secret-key FHE** can be transformed into a **compact, multi-hop public-key FHE** scheme.

<div align="center">
  <img src="/images/homomorphic/homo2.png" alt="From Secret-Key to Public-Key FHE"/>
</div>

---

## Noise in HE

Encrypted ciphertexts are randomized via **noise**:

$$
c \leftarrow \textsf{Encrypt}(\mathsf{pk}, m; r)
$$

Every operation increases the noise:

* **Addition** → small increase in noise
* **Multiplication** → large (often multiplicative) increase

If the noise exceeds a threshold, **decryption fails**. Hence, naive schemes can only support *bounded-depth* circuits.


<div align="center">
  <img src="/images/homomorphic/noise.png" alt="Noisy"/>
</div>

---

## Bootstrapping (Gentry, 2009)

**Bootstrapping** is a noise-reduction technique:

1. Encrypt $c$ again: $\textsf{Encrypt}(pk, c)$
2. Homomorphically evaluate the decryption circuit
3. Output: a *fresh* ciphertext with reduced noise

Requirements:

* Scheme can evaluate its own decryption circuit and a NAND gate

Bootstrapping allows turning SHE into FHE.

<div align="center">
  <img src="/images/homomorphic/homo4.png" alt="Bootstrapping Illustration"/>
</div>

---

## Leveled HE and Noise Budget

In **leveled HE**, ciphertexts have a *noise level* $l \in [0, L]$ for some max depth $L$. For two ciphertexts $c_1, c_2$:

* **Addition:** $\max(\text{level}(c_1), \text{level}(c_2))$
* **Multiplication:** $\max(\text{level}(c_1), \text{level}(c_2)) + 1$

If level exceeds $L$, decryption fails. This gives control over computation depth **without bootstrapping**, as long as the circuit depth is known in advance.

Optimizing circuit structure reduces depth:


<div align="center">
  <img src="/images/homomorphic/homo5.png" alt="Circuit Depth Optimization"/>
</div>

---

## 📈 Improvements in HE

* **Linear Noise Growth** in second-gen HE schemes (vs. exponential in Gentry’s original).
* **Modulus Switching**: Change the ciphertext modulus to reduce noise.
* **Batching** and **Packing**: Encrypt multiple messages in a single ciphertext.
* **HE over Integers / Lattices**: Operations over rings like $\mathbb{Z}_q$, RLWE-based schemes.

> ⚠ Bootstrapping is still computationally expensive, so many practical schemes remain SHE or LHE.

---
