# Detailed, commented implementation of DGHV‐style homomorphic encryption in Python

import math
import random
from Crypto.Util.number import getPrime

# ---------------------
# --- Utility functions
# ---------------------

def randodd(n: int) -> int:
    """
    Generate a random n‐bit odd integer:
    - Create an (n−1)-bit random number, shift left by 1, then add 1.
    """
    return 2 * (2 ** (n - 2) + random.randint(0, 2 ** (n - 2)) - 1) + 1

def quot_near(a: int, b: int) -> int:
    """
    Compute the integer closest to a / b via:
        round(a / b) = floor((2a + b) / (2b))
    """
    return (2 * a + b) // (2 * b)

def mod_near(a: int, b: int) -> int:
    """
    Compute a mod b but return a representative in [−b/2, +b/2].
    This keeps "noise" small when decrypting.
    """
    return a - b * quot_near(a, b)

# --------------------------------------
# --- Secret‐key encryption (“encrypt_sk”)
# --------------------------------------

def encrypt_sk(m: int, p: int, gamma: int, eta: int, rho: int) -> int:
    """
    Secret‐key encryption (DGHV style):
     - Choose a small random integer r in [−2^rho, +2^rho].
     - Choose a large multiplier q in [1, 2^(gamma−eta−1)].
     - Ciphertext: c = p*q + 2*r + m.
    This ensures c ≡ m (mod 2), and noise=2r is small.
    """
    # q is large (hides m), r is small (noise)
    q = random.randint(1, 2 ** (gamma - eta - 1))
    r = random.randint(-(2**rho) + 1, 2**rho - 1)
    # Construct ciphertext so that c mod p ≈ 2r + m
    c = p * q + 2 * r + m
    return c

# --------------------------------------
# --- Public‐key generation (“generate_pk”)
# --------------------------------------

def generate_x(p: int, gamma: int, rho: int) -> int:
    """
    Sample one public‐key element:
     - Draw q as an odd (gamma−eta)-bit integer.
     - Draw r as a small noise term in [−2^rho, +2^rho].
     - Set x = p*q + r.
    Returns x >> p hides p under LWE assumption.
    """
    q = randodd(gamma - eta)
    r = random.randint(-(2**rho) + 1, 2**rho - 1)
    return p * q + r

def generate_pk(p: int, gamma: int, rho: int, tau: int) -> list[int]:
    """
    Build a list of tau public‐key elements:
     1. Sample tau many x_i = p*q_i + r_i.
     2. Sort descending so x0 is largest.
     3. Ensure x0 is odd and mod_near(x0, p) is even (for correct decrypt).
    """
    while True:
        xs = [generate_x(p, gamma, rho) for _ in range(tau)]
        xs.sort(reverse=True)
        # Condition: x0 % 2 == 1, and (x0 mod p) is even
        if xs[0] % 2 == 1 and mod_near(xs[0], p) % 2 == 0:
            return xs

# --------------------------------------
# --- Public‐key encryption (“encrypt_pk”)
# --------------------------------------

def encrypt_pk(m: int, xs: list[int], rho_: int) -> int:
    """
    Public‐key encryption:
     - xs[0] is the largest x0.
     - Choose a small noise r in [−2^rho_, +2^rho_].
     - Select a random subset of the remaining xs to mask m.
     - Sum those selected xs (mod x0).
     - Ciphertext: c = m + 2*r + 2*sum_selected (mod x0).
    This yields c mod 2 ≡ m, with noise kept small.
    """
    x0 = xs[0]
    # small noise
    r = random.randint(-(2**rho_) + 1, 2**rho_ - 1)
    # choose random subset of xs[1:]
    selected = [random.choice([True, False]) for _ in xs]
    # sum the chosen x_i's modulo x0
    sum_selected = sum(xi for xi, use in zip(xs, selected) if use) % x0
    # combine plaintext + noise + mask
    c = (m + 2 * r + 2 * sum_selected) % x0
    return c

# --------------------------------------
# --- Decryption (“decrypt”)
# --------------------------------------

def decrypt(c: int, p: int) -> int:
    """
    Decrypt ciphertext c using secret key p:
     1. Compute c mod p, choose representative in [−p/2, +p/2].
     2. Reduce mod 2: since c mod p = 2*r + m, this yields m.
    """
    return mod_near(c, p) % 2

# --------------------------------------
# --- Scheme parameters & demonstration
# --------------------------------------

# Security / noise parameters:
lam   = 42       # λ not used directly here
eta   = 988      # bit‐length of secret key p
rho   = 26       # noise bound for secret‐key encryption
rho_  = 42       # noise bound for public‐key encryption
gamma = 147456   # bit‐length of each public‐key integer
tau   = 158      # number of public‐key integers

# 1. Generate secret key p (η‐bit prime)
p = getPrime(eta)

# 2. Secret‐key encryptions of bits 0 and 1
c0 = encrypt_sk(0, p, gamma, eta, rho)
c1 = encrypt_sk(1, p, gamma, eta, rho)

# 3. Verify homomorphic operations under secret‐key scheme
assert decrypt(c0 + c0, p) == 0      # 0+0=0
assert decrypt(c0 + c1, p) == 1      # 0+1=1
assert decrypt(c1 + c1, p) == 0      # 1+1=0 (mod 2)

assert decrypt(c0 * c1, p) == 0      # 0*1=0
assert decrypt(c1 * c1, p) == 1      # 1*1=1

# 4. Generate public key and encrypt bits
xs = generate_pk(p, gamma, rho, tau)
c0_pk = encrypt_pk(0, xs, rho_)
c1_pk = encrypt_pk(1, xs, rho_)

# 5. Example polynomial evaluation on ciphertext:
#    f(c0, c1) = a0 * (c0 ** d) + a1 * c1  (mod x0)
a0, a1 = 10, 20
coef_norm = a0 + a1
d = 20  # polynomial degree ≤ noise‐budget

x0 = xs[0]
# modular exponentiation reduces noise growth
c0d = pow(c0_pk, d, x0)
# combine terms in ciphertext domain
c_combined = (a0 * c0d + a1 * c1_pk) % x0

# expected plaintext value = (a0*0^d + a1*1) mod 2 = a1 mod 2
expected = (a0 * 0**d + a1 * 1) % 2

# check decryption correctness
print("Degree bound ≈", (eta - 4 - math.log2(coef_norm)) / (rho_ + 2))
print("Decryption correct?", decrypt(c_combined, p) == expected)
