---
title: "The ElGamal Cryptosystem"
description: "A compact construction of ElGamal encryption from the discrete-logarithm setting, including key generation, encryption, decryption, and implementation notes."
pubDate: "2025-05-27"
updatedDate: '2026-09-12'
topics:
- "Public-Key Cryptography"
- "Discrete Logarithms"
tags:
- "elgamal"
- "public-key-encryption"
- "dlp"
difficulty: "Intermediate"
series: "Diffie–Hellman & ElGamal"
seriesOrder: 4
sourcePath: "experiments/ready-material/elgamal"
draft: false
---
The ElGamal cryptosystem, introduced by Taher ElGamal in 1985, is an asymmetric encryption scheme whose security rests on the intractability of the discrete logarithm problem in a finite cyclic group. In its most common instantiation, one works in the multiplicative group $\mathbb{Z}_p^*$ of a large prime $p$, selecting a generator $g$ of a subgroup of prime order $q\mid p-1$. The fundamental assumption is that, given $g^a\bmod p$, it is computationally infeasible to recover the exponent $a$ when $p$ and $q$ are chosen to be sufficiently large; this one-way property underpins the scheme’s security.

To establish the necessary parameters, one begins by choosing a prime $p$ and a generator $g\in\mathbb{Z}_p^*$ whose order is a large prime $q$. An entity (commonly called Alice) then selects a secret exponent $a\in\{1,\dots,p-2\}$ and computes the public key component $A = g^a \bmod p$. The pair $(g,A,p)$ is published as the public key, while $a$ remains confidential. This key generation procedure ensures that the public parameters define a cyclic group of known prime order, providing a well-structured environment for both encryption and decryption.

When a sender (Bob) wishes to transmit a message $m\in\mathbb{Z}_p^*$ to Alice, he first samples a random ephemeral exponent $k\in\{1,\dots,p-2\}$. He then computes the values

$$
c_1 = g^k \bmod p,\quad
c_2 = m\cdot A^k \bmod p,
$$

and sends the ciphertext pair $(c_1,c_2)$ to Alice. The incorporation of the random value $k$ guarantees that encrypting the same plaintext twice will almost certainly yield different ciphertexts, thus providing semantic security against passive adversaries.

Upon receipt of $(c_1,c_2)$, Alice recovers the shared secret $s = c_1^a \bmod p$. She computes the modular inverse $s^{-1}$ and obtains the original message by evaluating

$$
m = c_2 \cdot s^{-1} \bmod p.
$$

The correctness of this decryption follows immediately from

$$
c_2 \cdot (c_1^a)^{-1}
= m \cdot A^k \cdot (g^{k})^{-a}
= m \cdot g^{ak} \cdot g^{-ak}
= m.
$$

Thus, ElGamal achieves reliable decryption while preserving the confidentiality of $m$ under the assumed hardness of computing $a$ from $g^a$.


| Phase               | Action                                                       |
| ------------------- | ------------------------------------------------------------ |
| **Setup**           | Choose large prime $p$, generator $g \in \mathbb{Z}_p^*$     |
| **KeyGen (Alice)**  | Select private key $a$, compute public key $A = g^a \mod p$  |
| **Encrypt (Bob)**   | Choose random $k$, compute $(c_1, c_2) = (g^k, m \cdot A^k)$ |
| **Decrypt (Alice)** | Recover message as $c_2 \cdot (c_1^a)^{-1} \mod p$           |


Below we present a simple numerical example for better understanding: 

#### (Alice) - Key Generation
1. Choose $p = 89$, $g = 3$
2. Private key: $a = 17$
3. Compute public key:

   $$
   A = g^a \mod p = 3^{17} \mod 89 = 6
   $$
4. Public key: $(g, A, p) = (3, 6, 89)$

#### (Bob) - Encryption

1. Message to encrypt: $m = 71$
2. Random ephemeral key: $k = 24$
3. Compute:

   * Shared secret: $s = A^k = 6^{24} \mod 89 = 67$
   * $c_1 = g^k = 3^{24} \mod 89 = 39$
   * $c_2 = m \cdot s = 71 \cdot 67 \mod 89 = 40$
4. Send ciphertext: $(c_1, c_2) = (39, 40)$

#### (Alice) - Decryption

1. Compute shared secret: $s = c_1^a = 39^{17} \mod 89 = 67$
2. Compute $s^{-1} \mod 89 = 67^{-1} \mod 89 = 4$
3. Recover message:

   $$
   m = c_2 \cdot s^{-1} \mod p = 40 \cdot 4 \mod 89 = 71
   $$

**Decryption successful.**

#### Security Considerations

In the ElGamal cryptosystem, careful attention must be given to the selection of both the private key $a$ and the ephemeral key $k$. These values must never be zero. Choosing $a = 0$ results in a public key value $A = g^0 = 1$, which is trivial and easily predictable, thereby compromising the confidentiality of the system. Similarly, selecting $k = 0$ leads to $c_1 = g^0 = 1$ and $c_2 = m \cdot A^0 = m$, meaning that the plaintext is exposed directly in the ciphertext. To preserve the intended security properties, both $a$ and $k$ must be chosen uniformly at random from the interval $\{1, \dots, p - 2\}$.

#### Security Properties

The ElGamal scheme offers semantic security under the assumption of a properly chosen ephemeral key $k$. Because the ciphertext includes randomness from $k$, encrypting the same message multiple times results in different ciphertexts, thwarting many passive eavesdropping strategies. However, this comes with a cost: the ciphertext consists of two group elements, effectively doubling the size of the message. In applications where bandwidth is constrained, this ciphertext expansion may be a consideration. On the positive side, the exponentiations $g^k$ and $A^k$ required for encryption can be precomputed and stored in advance, enhancing efficiency in resource-limited environments.

#### Vulnerabilities

The security of ElGamal is fundamentally tied to the hardness of the discrete logarithm problem (DLP) in the group $\mathbb{Z}_p^*$. If an adversary can solve the DLP in this group, the core security guarantees of the cryptosystem collapse. Specifically, if the exponent $a$ can be recovered from $A = g^a$, or if $k$ can be derived from $c_1 = g^k$, then the adversary can compute the shared secret and decrypt the ciphertext. Known attacks on the DLP, such as Pollard’s Rho algorithm, the Index Calculus method, or the Pohlig–Hellman algorithm, can be effective if the parameters $p$ and $q$ are not chosen with sufficient care. Thus, the proper selection of a prime $p$ and a subgroup of large prime order $q$ is essential to maintain the cryptographic strength of the ElGamal system.


Naive implementantions in Python/SageMath are provided in `ElGamal/src/`.
