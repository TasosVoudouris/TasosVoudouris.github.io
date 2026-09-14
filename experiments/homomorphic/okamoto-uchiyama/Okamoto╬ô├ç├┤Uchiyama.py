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

# Public key  = (n, g, h)
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
