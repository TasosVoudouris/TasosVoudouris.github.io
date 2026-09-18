import random
import math
from Crypto.Util.number import getPrime
from sympy.ntheory.modular import solve_congruence

# --- Parameters and Key Generation ---
prime_set = [3, 5, 7, 11, 13, 17]
k = len(prime_set)

# 1. Partition prime_set into two halves, compute u = ∏ first half, v = ∏ second half
u = 1
v = 1
for i, p_i in enumerate(prime_set):
    if i < k/2:
        u *= p_i
    else:
        v *= p_i

sigma = u * v  # total plaintext modulus

# 2. Choose large random 16-bit primes a, b
a = getPrime(16)
b = getPrime(16)

# 3. Construct p = 2 a u + 1, q = 2 b v + 1 and ensure they are prime
while True:
    p = 2 * a * u + 1
    q = 2 * b * v + 1
    if all([pow(2, p-1, p) == 1, pow(2, q-1, q) == 1]):
        # Miller–Rabin (via pow) gives probable-primality test
        break
    # regenerate a, b if necessary
    a = getPrime(16)
    b = getPrime(16)

n = p * q
phi = (p - 1) * (q - 1)

# 4. Select a base g whose order modulo n is divisible by every p_i
while True:
    g = random.randint(2, n-1)
    if all(pow(g, phi // p_i, n) != 1 for p_i in prime_set):
        break

print(f"[KeyGen] sigma={sigma}, n={n}, φ(n)={phi}")
print(f"[KeyGen] small primes={prime_set}")
print(f"[KeyGen] g={g}\n")

# --- Encryption (deterministic) ---
def encrypt(m: int) -> int:
    """
    Encrypt integer m ∈ [0, sigma-1] by exponentiation.
    WARNING: deterministic; for IND-CPA security add a random blinding factor.
    """
    assert 0 <= m < sigma
    c = pow(g, m, n)
    print(f"[Encrypt] m = {m} -> c = {c}")
    return c

# Example ciphertext
m_test = 202 % sigma
c_test = encrypt(m_test)
print()

# --- Decryption via CRT of small-subgroup logs ---
def decrypt(c: int) -> int:
    """
    Recover m by finding m mod each small prime p_i via subgroup discrete logs,
    then recombine with solve_congruence.
    """
    remainders = []
    for p_i in prime_set:
        # exponentiate to kill randomness (if any) and reduce to g^{m φ/p_i}
        c_i = pow(c, phi // p_i, n)
        # discrete log in subgroup of order p_i
        found = False
        for j in range(p_i):
            if c_i == pow(g, j * (phi // p_i), n):
                remainders.append(j)
                print(f"[Decrypt] m mod {p_i} = {j}")
                found = True
                break
        if not found:
            raise ValueError(f"Failed to find discrete log mod {p_i}")
    # solve CRT
    sol, mod = solve_congruence(*[(r, p_i) for r, p_i in zip(remainders, prime_set)])
    m = sol % sigma
    print(f"[Decrypt] Reconstructed m = {m} (mod {sigma})\n")
    return m

# Test decryption
assert decrypt(c_test) == m_test

# --- Homomorphic Test ---
print("[HomoTest] testing addition in exponent:")
m1, m2 = 100, 200
c1, c2 = encrypt(m1), encrypt(m2)
sum_c = (c1 * c2) % n
m_sum = decrypt(sum_c)
print(f"[HomoTest] m1+m2 = {m1+m2} -> decrypted {m_sum}")
assert m_sum == (m1+m2) % sigma
print("[HomoTest] success.")
