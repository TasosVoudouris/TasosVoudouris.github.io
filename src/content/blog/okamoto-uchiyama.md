---
title: "Okamoto–Uchiyama: Additively Homomorphic Encryption modulo p"
description: "Develop the p²q modulus structure, encryption, L-function decryption, additive homomorphism, and security intuition of the Okamoto–Uchiyama cryptosystem."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Number Theory"
tags:
  - "okamoto-uchiyama"
  - "additive-homomorphism"
  - "composite-modulus"
difficulty: "Advanced"
series: "Homomorphic Encryption"
seriesOrder: 7
sourcePath: "experiments/homomorphic"
status: "Experimental"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.

**Report on the Okamoto–Uchiyama Cryptosystem**

The Okamoto–Uchiyama (OU) cryptosystem is a public‐key scheme that supports additive homomorphism over a small plaintext space $\mathbb Z_p$. It is based on the difficulty of factoring a modulus of the form $n=p^2q$. Decryption exploits the subgroup structure of $\mathbb Z_{p^2}^*$.

---

### 1. Scheme Definition

1. **Setup**
   1.1. Choose distinct large primes $p,q$.
   1.2. Compute

   $$
     n \;=\; p^2\,q\,,
     \quad
     n_p\;=\;p^2\,.
   $$

   1.3. Select $g\in\mathbb Z_n^*$ satisfying

   $$
     g^{p-1}\not\equiv1\pmod{p^2}
   \quad\text{(Fermat’s little theorem test)}.
   $$

   1.4. Compute

   $$
     h \;=\; g^n \bmod n.
   $$

   **Public key**: $(n,\,g,\,h)$.
   **Private key**: $(p,\,q)$.

2. **Encryption**
   To encrypt $m\in\{0,1,\dots,p-1\}$:
   2.1. Choose random $r\in\{1,\dots,n-1\}$.
   2.2. Compute

   $$
     c \;=\; g^m\;h^r\;\bmod n.
   $$

3. **Decryption**
   Define the function

   $$
     L_p(u) \;=\;\frac{u-1}{p}\quad
     \bigl(u\equiv1\pmod{p^2}\bigr).
   $$

   Given ciphertext $c$:
   3.1. Compute

   $$
     a \;=\; L_p\bigl(c^{\,p-1}\bmod p^2\bigr),
     \quad
     b \;=\; L_p\bigl(g^{\,p-1}\bmod p^2\bigr).
   $$

   3.2. Recover

   $$
     m \;=\;a\,\bigl(b^{-1}\bmod p\bigr)\;\bmod p.
   $$

4. **Homomorphic Property**

   $$
     \text{Enc}(m_1)\cdot\text{Enc}(m_2)
     \;\equiv\;\text{Enc}(m_1+m_2\!\!\mod p)
     \pmod n.
   $$

5. **Security**
   Semantic security reduces to the hardness of factoring $p^2q$. The subgroup attack in $\mathbb Z_{p^2}^*$ is prevented by the choice of $g$ such that its order modulo $p^2$ is divisible by $p$.

---

```python
import random
import math
from Crypto.Util.number import getPrime

# --- Key Generation ---
# 1. Generate two 16-bit primes p, q
p = getPrime(16)
q = getPrime(16)
# 2. Compute composite modulus n = p^2 * q
n = p*p*q
print(f"[KeyGen] Primes: p = {p}, q = {q}")
print(f"[KeyGen] Modulus: n = p^2·q = {n}")

# 3. Select generator g ∈ (1, n) such that g^(p-1) mod p^2 != 1
while True:
    g = random.randint(2, n-1)
    if pow(g, p-1, p*p) != 1:
        break
# 4. Compute h = g^n mod n
h = pow(g, n, n)
print(f"[KeyGen] Generator: g = {g}")
print(f"[KeyGen] Auxiliary h = g^n mod n = {h}\n")

# Public key = (n, g, h)
# Private key = (p, q)

# --- Encryption ---
def encrypt(m: int, r: int) -> int:
    """
    Encrypt message m ∈ Z_p with randomness r:
      c = g^m · h^r mod n
    """
    return (pow(g, m, n) * pow(h, r, n)) % n

# Example plaintext
m = 17 % p
# Randomness r ∈ {1, …, n-1}
r = random.randint(1, n-1)
c = encrypt(m, r)
print(f"[Encrypt] Plaintext m = {m}")
print(f"[Encrypt] Randomness r = {r}")
print(f"[Encrypt] Ciphertext c = {c}\n")

# --- Decryption ---
def L_p(u: int) -> int:
    """
    L-function for modulus p^2:
      L_p(u) = (u - 1) // p,  for u ≡ 1 mod p^2
    """
    assert u % p == 1
    return (u - 1) // p

def decrypt(c: int) -> int:
    """
    Decrypt ciphertext c:
      a = L_p(c^(p-1) mod p^2)
      b = L_p(g^(p-1) mod p^2)
      m = a * b^{-1} mod p
    """
    a = L_p(pow(c, p-1, p*p))
    b = L_p(pow(g, p-1, p*p))
    m_rec = (a * pow(b, -1, p)) % p
    print(f"[Decrypt] a = {a}, b = {b}")
    print(f"[Decrypt] Recovered m = {m_rec}\n")
    return m_rec

m_prime = decrypt(c)
assert m_prime == m, "Decryption failed"

# --- Homomorphic Addition Test ---
m1, m2 = 17, 23
r1 = random.randint(1, n-1)
r2 = random.randint(1, n-1)
c1 = encrypt(m1 % p, r1)
c2 = encrypt(m2 % p, r2)
c_sum = (c1 * c2) % n
m_sum = decrypt(c_sum)

print(f"[HomoTest] m1 = {m1}, m2 = {m2}")
print(f"[HomoTest] Decrypted sum = {m_sum}, Expected = {(m1 + m2) % p}")
assert m_sum == (m1 + m2) % p
print("[HomoTest] Homomorphic addition successful.")
```

**Implementation notes**

* **$KeyGen$** logs prime generation, modulus construction, and generator selection.
* **$Encrypt$** displays the plaintext, chosen randomness, and resulting ciphertext.
* **$Decrypt$** shows intermediate $a,b$ values from the $L_p$ function and the recovered plaintext.
* **$HomoTest$** verifies that multiplication of ciphertexts yields the encryption of the sum modulo $p$.
