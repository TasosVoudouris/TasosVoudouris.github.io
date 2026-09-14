---
title: "Benaloh: Additively Homomorphic Encryption with a Larger Message Space"
description: "Extend Goldwasser–Micali from bits to messages modulo r, derive key-generation constraints, encryption/decryption, and the additive homomorphism."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Number Theory"
tags:
  - "benaloh"
  - "higher-residuosity"
  - "additive-homomorphism"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 3
sourcePath: "experiments/homomorphic"
status: "Experimental"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.

## **Benaloh Cryptosystem – Cryptographic Report**

The **Benaloh cryptosystem** is a **probabilistic public-key encryption scheme** that supports **homomorphic addition** over a small message space. It extends the Goldwasser–Micali cryptosystem by allowing encryption of larger blocks.

### **Key Generation**

* Choose large primes $p$ and $q$, such that:

  * $r \mid (p-1)$
  * $\gcd(r, \frac{p-1}{r}) = 1$
  * $\gcd(r, q-1) = 1$
* Set $n = p \cdot q$ and $\phi(n) = (p-1)(q-1)$
* Choose $y \in \mathbb{Z}_n^*$ such that for all prime divisors $r_i$ of $r$:
  $y^{\phi(n)/r_i} \not\equiv 1 \mod n$
* Public key: $(y, r, n)$
* Private key: $(x = y^{\phi(n)/r} \mod n, p, q)$

### **Encryption**

* Message $m \in \mathbb{Z}_r$
* Random $u \in \mathbb{Z}_n^*$
* Ciphertext:

  $$
  c = y^m \cdot u^r \mod n
  $$

### **Decryption**

* Compute $a = c^{\phi(n)/r} \mod n$
* Recover $m$ by solving $x^m \equiv a \mod n$

### **Homomorphic Property**

* $\text{Enc}(m_1) \cdot \text{Enc}(m_2) \equiv \text{Enc}(m_1 + m_2) \mod n$

---

## Annotated Python Implementation

```python
from math import gcd
import random
import sympy

# Prime parameters (must satisfy Benaloh conditions)
p = 10007
q = 191

assert sympy.isprime(p)
assert sympy.isprime(q)

n = p * q                  # RSA modulus
phi = (p - 1) * (q - 1)    # Euler's totient function

# Select block size r such that:
# r | (p-1), gcd(r, (p-1)/r) = 1, gcd(r, q-1) = 1
def generate_block_size():
    while True:
        r = random.randint(2, n)
        if ( (p - 1) % r == 0
             and gcd(r, (p - 1) // r) == 1
             and gcd(r, q - 1) == 1 ):
            break
    return r

# Key generation
def generate_keys():
    while True:
        r = generate_block_size()

        y = random.randint(2, n)
        if gcd(y, n) != 1:
            continue

        # Ensure decryption correctness (Fousse et al., 2011)
        decryption_guaranteed = True
        for prime_factor in sympy.factorint(r).keys():
            if pow(y, phi // prime_factor, n) == 1:
                decryption_guaranteed = False
                break
        if not decryption_guaranteed:
            continue

        x = pow(y, phi // r, n)
        if x != 1:
            break

    return r, x, y

# Generate Benaloh key pair
r, x, y = generate_keys()
print("Public key:", (y, r, n))
print("Private key:", (p, q, phi, x))

##### ENCRYPTION #####
m = 17
if m >= r:
    print(f"Warning: message {m} not in Z_{r}. Reducing...")
    m %= r
print("Plaintext:", m)

# Select random u coprime to n
while True:
    u = random.randint(1, n)
    if gcd(u, n) == 1:
        break

# Benaloh encryption: c = y^m * u^r mod n
def encrypt(m, u):
    return (pow(y, m, n) * pow(u, r, n)) % n

c = encrypt(m, u)
assert gcd(c, n) == 1
print("Ciphertext:", c)

##### DECRYPTION #####
# Recover m by solving x^m = a mod n
def decrypt(c):
    a = pow(c, phi // r, n)
    md = 0
    while True:
        if pow(x, md, n) == a:
            break
        md += 1
    return md

m_prime = decrypt(c)
print("Decrypted plaintext:", m_prime)
assert m_prime == m

##### HOMOMORPHIC TEST #####
# Test additive homomorphism: Dec(Enc(m1)*Enc(m2)) = m1 + m2 mod r

m1, m2 = 10 % r, 17 % r
u1, u2 = random.randint(1, n), random.randint(1, n)
c1, c2 = encrypt(m1, u1), encrypt(m2, u2)

# Homomorphic property:
assert (c1 * c2) % n == encrypt((m1 + m2) % r, (u1 * u2) % n)
assert decrypt((c1 * c2) % n) == (m1 + m2) % r
```

---
