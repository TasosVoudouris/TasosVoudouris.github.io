---
title: "Goldwasser–Micali: XOR-Homomorphic Public-Key Encryption"
description: "Study probabilistic bit encryption under the quadratic residuosity assumption and see why multiplying ciphertexts implements XOR of plaintext bits."
pubDate: "2025-05-29"
updatedDate: "2026-09-12"
topics:
  - "Homomorphic Encryption"
  - "Public-Key Cryptography"
  - "Number Theory"
tags:
  - "goldwasser-micali"
  - "quadratic-residuosity"
  - "xor-homomorphic"
difficulty: "Intermediate"
series: "Homomorphic Encryption"
seriesOrder: 2
sourcePath: "experiments/homomorphic"
status: "Research Note"
draft: false
---
> **Status note.** This chapter is retained as a detailed research/learning reference. The companion code is educational and is not treated as a production cryptographic implementation.

**Report on the Goldwasser–Micali Cryptosystem**

The Goldwasser–Micali (GM) scheme is a foundational probabilistic public-key encryption system that encodes each bit of a plaintext independently, achieving semantic security under the Quadratic Residuosity Assumption (QRA). Its principal features are:

1. **Key Generation**
   1.1. Choose two large primes $p,q$ and let $n=pq$.
   1.2. Select a quadratic non‐residue $x\in\mathbb Z_n^*$ such that $\bigl(\tfrac{x}{p}\bigr)=\bigl(\tfrac{x}{q}\bigr)=-1$.
   1.3. Public key: $(n, x)$. Private key: $(p,q)$.

2. **Encryption**
   To encrypt a bit $b\in\{0,1\}$:

   * Pick a random $r\in\mathbb Z_n^*$.
   * Compute

     $$
       c \;=\; r^2\;x^b\;\bmod n.
     $$
   * For a multi‐bit message, encrypt each bit separately, yielding a ciphertext vector.

3. **Decryption**
   Given $c$, compute the Legendre symbols modulo $p$ and $q$:

   $$
     \left(\tfrac{c}{p}\right)
     \quad\text{and}\quad
     \left(\tfrac{c}{q}\right).
   $$

   If both are $+1$, the bit is 0; if both are $-1$, the bit is 1.

4. **Homomorphic XOR**
   Because

   $$
     c_1 = r_1^2\,x^{b_1},\quad
     c_2=r_2^2\,x^{b_2}
     \quad\Longrightarrow\quad
     c_1\cdot c_2 = (r_1r_2)^2\,x^{b_1+b_2},
   $$

   multiplication of ciphertexts corresponds to XOR of plaintext bits (addition mod 2).

5. **Security**
   Semantic security rests on the hardness of distinguishing quadratic residues from non‐residues modulo a composite $n$ when the factorization is unknown (the Quadratic Residuosity Assumption).

---

```python
import random
import math
from Crypto.Util.number import getPrime
from sympy import jacobi_symbol

# --- Key Generation ---
# Generate two distinct 16-bit primes and compute modulus n
p = getPrime(16)
q = getPrime(16)
n = p * q
print(f"[KeyGen] Primes p={p}, q={q} -> modulus n={n}")

# Find a quadratic non‐residue x mod n: jacobi_symbol(x,p)=jacobi_symbol(x,q)=-1
while True:
    x = random.randint(2, n-1)
    if (math.gcd(x, n) == 1
        and jacobi_symbol(x, p) == -1
        and jacobi_symbol(x, q) == -1):
        break
print(f"[KeyGen] Selected non‐residue x={x}\n")

# --- Encryption of a single bit ---
def encrypt_bit(b: int, r: int) -> int:
    """
    Encrypt one bit b in {0,1} under modulus n using randomness r:
        c = r^2 * x^b mod n
    """
    return (pow(r, 2, n) * pow(x, b, n)) % n

# Generate random r ∈ Z_n^*
def generate_random() -> int:
    """
    Return r such that gcd(r,n)=1.
    """
    while True:
        r = random.randint(2, n-1)
        if math.gcd(r, n) == 1:
            return r

# Encrypt a multi‐bit integer by bit-wise encryption
def encrypt(m: int) -> list[int]:
    """
    Encrypt integer m by its binary bits.
    Returns list of ciphertexts for each bit.
    """
    m_bin = bin(m)[2:]
    print(f"[Encrypt] Plaintext m={m} -> bits {m_bin}")
    ciphertext = []
    for i, bit_char in enumerate(m_bin):
        b = int(bit_char)
        r = generate_random()
        c = encrypt_bit(b, r)
        ciphertext.append(c)
        print(f"  [Encrypt] bit {i}: {b}, r={r} -> c={c}")
    print()
    return ciphertext

# --- Decryption ---
def decrypt(c_list: list[int]) -> int:
    """
    Recover plaintext integer from list of bit-ciphertexts.
    Uses the Legendre symbol test modulo p and q.
    """
    bits = []
    for i, c in enumerate(c_list):
        # Compute Legendre symbol via Euler's criterion
        res_p = pow(c % p, (p-1)//2, p)
        res_q = pow(c % q, (q-1)//2, q)
        # Both +1 => bit 0; both p-1,q-1 (i.e. -1 mod p/q) => bit 1
        if res_p == 1 and res_q == 1:
            bit = '0'
        else:
            bit = '1'
        bits.append(bit)
        print(f"[Decrypt] c[{i}]={c}: (c|p)={res_p}, (c|q)={res_q} -> bit={bit}")
    m_bin = ''.join(bits)
    m = int(m_bin, 2)
    print(f"[Decrypt] Recovered bits {m_bin} -> m={m}\n")
    return m

# --- Example Usage ---
m = 17
c = encrypt(m)
m_dec = decrypt(c)
assert m_dec == m, "Decryption failed"

# --- Homomorphic XOR Test ---
print("[HomoTest] Verifying homomorphic XOR property")
for b1, b2 in [(0,0),(0,1),(1,0),(1,1)]:
    r1, r2 = generate_random(), generate_random()
    c1, c2 = encrypt_bit(b1, r1), encrypt_bit(b2, r2)
    c_prod = (c1 * c2) % n
    b_xor = b1 ^ b2
    dec = decrypt([c_prod])
    print(f"  {b1} XOR {b2} = {b_xor}, decrypted {(dec)}")
    assert dec == b_xor
print("\n[HomoTest] All XOR tests passed.")
```

**Implementation notes**

* Each major phase (key generation, encryption, decryption, homomorphic test) prints a clear header.
* Per‐bit operations log input bit, randomness, and resulting ciphertext or recovered bit.
* Final assertions guarantee correctness and report success.
