import math
import random
from Crypto.Util.number import getPrime, inverse
from math import lcm

# Parameter: s = 2 means expansion factor for larger plaintext space Z_{n^2}
s = 2 

# Key Generation
p = getPrime(16)
q = getPrime(16)

n = p * q
ns = pow(n, s)
ns1 = pow(n, s + 1)

g = n + 1

lam = lcm(p - 1, q - 1)

# Compute L(g^λ mod n^{s+1}) = (g^λ - 1) // n
L_g_lam = (pow(g, lam, ns1) - 1) // n
mu = inverse(L_g_lam, ns)

print(f"Public key: (n = {n}, g = {g})")
print(f"Private key: (λ = {lam}, μ = {mu})")

# Encryption
def generate_random():
    while True:
        r = random.randint(2, n - 1)
        if math.gcd(r, n) == 1:
            return r

def encrypt(m, r):
    return (pow(g, m, ns1) * pow(r, ns, ns1)) % ns1

# L-function
def L(u):
    return (u - 1) // n

# Decryption
def decrypt_DJ(c):
    # --- Step 1: recover m0 = m mod n ---
    u1 = pow(c, lam, n**3)
    l1 = (u1 - 1) // n
    m0 = (l1 * mu) % n

    # --- Step 2: strip off m0, recover m1 ---
    # compute g^{-m0} mod n^3
    g_inv_m0 = pow(g, -m0, n**3)
    c2 = (c * g_inv_m0) % (n**3)

    u2 = pow(c2, lam, n**3)
    l2 = (u2 - 1) // n
    m1 = (l2 * mu) % n

    return m0 + m1 * n


# --- Test Encryption / Decryption ---
m = 17
r = generate_random()
c = encrypt(m, r)
m_prime = decrypt_DJ(c)

print(f"Original message: {m}")
print(f"Decrypted message: {m_prime}")
assert m_prime == m

# --- Homomorphic test ---
m1, m2 = 17, 22
r1, r2 = generate_random(), generate_random()

c1 = encrypt(m1, r1)
c2 = encrypt(m2, r2)

c_add = (c1 * c2) % ns1
m_add = decrypt_DJ(c_add)

print(f"Homomorphic test: {m1} + {m2} = {m_add}")
assert m_add == m1 + m2
