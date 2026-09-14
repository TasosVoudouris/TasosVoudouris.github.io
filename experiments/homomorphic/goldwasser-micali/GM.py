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
