from py_ecc.optimized_bls12_381 import G1, G2, multiply, add, pairing, curve_order
from hashlib import sha256

# Hash function
def hash_to_G1(message):
    hash_value = sha256(message.encode()).digest()
    return multiply(G1, int.from_bytes(hash_value, 'big') % curve_order)

# Example parameters
secret = 1234567890  # Example secret
threshold = 2
n = 3  # Number of participants

# Generate shares using Shamir Secret Sharing
def generate_shares(secret, n, threshold):
    import random
    coeffs = [secret] + [random.randint(0, curve_order) for _ in range(threshold - 1)]
    shares = [(i, sum([coeffs[j] * i**j for j in range(threshold)]) % curve_order) for i in range(1, n+1)]
    return shares

def interpolate(shares, x=0):
    total = 0
    for i, (xi, yi) in enumerate(shares):
        basis = 1
        for j, (xj, _) in enumerate(shares):
            if i != j:
                basis *= (x - xj) * pow(xi - xj, -1, curve_order) % curve_order
        total += yi * basis % curve_order
    return total % curve_order

# Example shares generation
shares = generate_shares(secret, n, threshold)
print(f"Generated shares: {shares}")

# Participants hash a message to a point in G1
message = "Hello, BLS!"
H_m = hash_to_G1(message)

# Each participant creates their partial signature
partial_sigs = [(i, multiply(H_m, s)) for i, s in shares]

# Interpolation to combine signatures
def combine_signatures(partial_sigs):
    combined_sig = None
    for i, sig in partial_sigs:
        if combined_sig is None:
            combined_sig = sig
        else:
            combined_sig = add(combined_sig, sig)
    return combined_sig

combined_sig = combine_signatures([sig for _, sig in partial_sigs[:threshold]])
print(f"Combined signature: {combined_sig}")

# Verification
def verify(signature, message, pub_key):
    H_m = hash_to_G1(message)
    return pairing(signature, G2) == pairing(H_m, pub_key)

# Public key reconstruction
pub_key = multiply(G2, secret)
print(f"Public key: {pub_key}")

# Verify combined signature
is_valid = verify(combined_sig, message, pub_key)
print(f"Signature valid: {is_valid}")

