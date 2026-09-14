from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime, inverse
import random

# Generate ElGamal public parameters
def gen_params():
    # Generate a large safe prime p (1024-bit)
    p = getPrime(1024)
    # Choose a small generator g (commonly g = 2 is used)
    g = 2
    return g, p

# Generate ElGamal key pair
def gen_keys(g, p):
    # Choose a private key a ∈ [1, p-1]
    a = random.randint(1, p-1)
    # Compute public key A = g^a mod p
    return pow(g, a, p), a

# Encrypt a plaintext integer message m using recipient's public key A
def elg_encryption(m, A, g, p):
    # Choose random ephemeral key k ∈ [1, p-1]
    k = random.randint(1, p-1)
    # Compute c1 = g^k mod p
    c1 = pow(g, k, p)
    # Compute c2 = m * A^k mod p
    c2 = (m * pow(A, k, p)) % p
    # Return ciphertext (c1, c2)
    return c1, c2

# Decrypt ciphertext (c1, c2) using private key a
def elg_decryption(c1, c2, a, p):
    # Compute s = c1^a mod p
    s = pow(c1, a, p)
    # Compute s^(-1) mod p using modular inverse
    x = inverse(s, p)
    # Recover plaintext: m = c2 * s^(-1) mod p
    m_decr = (x * c2) % p
    return m_decr

# === Example usage ===

# Generate public parameters
g, p = gen_params()

# Generate public/private key pair for recipient
A, a = gen_keys(g, p)

# Encode plaintext message to integer
m = bytes_to_long(b'Taher El Gamal the best')

# Encrypt message using recipient's public key
c1, c2 = elg_encryption(m, A, g, p)

# Decrypt the ciphertext using private key
m_decr = elg_decryption(c1, c2, a, p)

# Verify decryption correctness and print result
assert m_decr == m  # Should output: True
print(long_to_bytes(m_decr))  # Should output: b'Taher El Gamal the best'
