---
title: "Damgård–Jurik: Extending Paillier to Larger Plaintext Spaces"
description: "Explore the Damgård–Jurik generalization of Paillier over increasing powers of n, its additive homomorphism, ciphertext growth, and educational implementation considerations."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Number Theory"
tags:
  - "damgard-jurik"
  - "paillier"
  - "additive-homomorphism"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 5
sourcePath: "experiments/homomorphic"
status: "Experimental"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.


The Damgård–Jurik cryptosystem is an extension of the Paillier probabilistic public-key encryption scheme that supports encryption of messages in $\mathbb Z_{n^s}$ for any integer $s\ge1$. It preserves additive homomorphism while enlarging the plaintext space from $\mathbb Z_n$ to $\mathbb Z_{n^s}$. This report presents the scheme’s formal description, key algorithms, homomorphic properties, and security considerations, followed by a fully commented Python implementation.

---

## 1. Introduction

Damgård and Jurik (2001) generalized Paillier’s scheme to allow larger plaintext blocks by replacing the modulus $n^2$ with $n^{s+1}$. For $s=1$, it reduces to standard Paillier; for $s>1$, it enables encryption of integers up to $n^s-1$. Like Paillier, it is semantically secure under the Decisional Composite Residuosity Assumption (DCRA).

---

## 2. Notation and Parameters

* Let $p,q$ be distinct large primes and $n=pq$.
* Define the public exponent parameter $s\ge1$.
* Denote

  $$
    N = n,\quad N_s = n^s,\quad N_{s+1} = n^{s+1}.
  $$
* Select generator $g = N + 1\in\mathbb Z^*_{N_{s+1}}$.
* Compute $\lambda = \mathrm{lcm}(p-1,q-1)$.
* Define the function

  $$
    L(u)=\frac{u-1}{N}\quad
    (u\equiv1\pmod N).
  $$
* Compute $\mu = L\bigl(g^\lambda\bmod N_{s+1}\bigr)^{-1}\bmod N_s$.

**Public key**: $(N, s, g)$
**Private key**: $(\lambda, \mu)$

---

## 3. Key Generation

1. Generate primes $p,q$, compute $N=pq$.
2. Choose integer $s\ge1$.
3. Compute $\lambda=\mathrm{lcm}(p-1,q-1)$.
4. Set $g=N+1$.
5. Compute $L_g = L(g^\lambda \bmod N_{s+1})$.
6. Compute $\mu = L_g^{-1}\bmod N_s$.

---

## 4. Encryption

To encrypt $m\in\{0,1,\dots,N_s-1\}$:

1. Sample random $r\in\mathbb Z_N^*$.
2. Compute

   $$
     c \;=\; g^m \;\cdot\; r^{N_s}
     \;\bmod\; N_{s+1}.
   $$

---

## 5. Decryption

For $c\in\mathbb Z^*_{N_{s+1}}$, recover $m$ in two “base-$N$” digits $m_0,m_1$ when $s=2$ (generalizes similarly for larger $s$):

```python
def decrypt(c):
    # First digit m0 = m mod N
    u1 = pow(c, λ, N_{s+1})
    l1 = (u1 - 1)//N
    m0 = (l1 * μ) % N

    # Remove contribution of m0 to extract m1
    c2 = (c * pow(g, -m0, N_{s+1})) % N_{s+1}
    u2 = pow(c2, λ, N_{s+1})
    l2 = (u2 - 1)//N
    m1 = (l2 * μ) % N

    return m0 + m1 * N
```

For general $s$, one iterates this “digit extraction” $s$ times.

---

## 6. Homomorphic Properties

* **Addition**:

  $$
    \text{Enc}(m_1)\cdot \text{Enc}(m_2)
    \;\equiv\; \text{Enc}(m_1 + m_2)
    \pmod{N_{s+1}}.
  $$
* **Scalar multiplication**:

  $$
    \text{Enc}(m)^k
    \;\equiv\; \text{Enc}(k\,m)
    \pmod{N_{s+1}}.
  $$

---

## 7. Security Considerations

* **Semantic security** follows from the DCRA: distinguishing $N$th residues in $\mathbb Z^*_{N_{s+1}}$ is hard if factoring $n$ is infeasible.
* **Parameter choice**: $s$ should be small (e.g., 1–2) to keep decryption cost feasible. Larger $s$ increases ciphertext size ($\approx (s+1)\log n$ bits) and decryption complexity ($\mathcal O(s)$ exponentiations).

---

## 8. Python Implementation with Neat Inline Comments

```python
import math, random
from Crypto.Util.number import getPrime, inverse
from math import lcm

# --- Scheme Parameters ---
s = 2                              # expansion factor: plaintext in Z_{n^2}
p, q = getPrime(16), getPrime(16)  # generate two 16-bit primes
n = p * q
N_s = n**s
N_s1 = n**(s + 1)
g = n + 1                          # standard generator

# Compute private values
λ = lcm(p - 1, q - 1)
L_g = (pow(g, λ, N_s1) - 1) // n
μ = inverse(L_g, N_s)              # μ = L(g^λ)^{-1} mod n^s

# --- Public / Private Keys ---
# Public : (n, s, g)
# Private: (λ, μ)

def generate_random():
    """Return r in Z_n^*."""
    while True:
        r = random.randrange(2, n)
        if math.gcd(r, n) == 1:
            return r

def encrypt(m, r):
    """
    Encrypt message m < n^s.
    c = g^m * r^(n^s) mod n^(s+1)
    """
    return (pow(g, m, N_s1) * pow(r, N_s, N_s1)) % N_s1

def decrypt(c):
    """
    Two-step decryption for s=2:
      1) Recover least-significant digit m0 mod n.
      2) Strip m0 contribution, recover m1.
      Return m = m0 + m1 * n.
    """
    # Step 1: compute u1 = c^λ mod n^(s+1)
    u1 = pow(c, λ, N_s1)
    l1 = (u1 - 1) // n
    m0 = (l1 * μ) % n

    # Step 2: remove g^m0 factor, recover next digit m1
    c2 = (c * pow(g, -m0, N_s1)) % N_s1
    u2 = pow(c2, λ, N_s1)
    l2 = (u2 - 1) // n
    m1 = (l2 * μ) % n

    return m0 + m1 * n

# --- Example Test ---
m = 42
r = generate_random()
c = encrypt(m, r)
assert decrypt(c) == m, "Decryption failed"

# Homomorphic addition
m1, m2 = 10, 15
r1, r2 = generate_random(), generate_random()
c_sum = (encrypt(m1, r1) * encrypt(m2, r2)) % N_s1
assert decrypt(c_sum) == m1 + m2
```

---

**References**

* Damgård, I., & Jurik, M. (2001). A generalisation, a simplification and some applications of Paillier’s probabilistic public-key system. *PKC 2001*.
* Paillier, P. (1999). Public-key cryptosystems based on composite degree residuosity classes. *EUROCRYPT 1999*.
