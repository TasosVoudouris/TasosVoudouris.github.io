"""Create and verify one ECDSA signature."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/key_generation.sage")
load("src/elliptic_curves/ecdsa.sage")

public_key, private_key = ec_keygen()
message = b"hello"
r, s = ecdsa_sign(private_key, message)

print("Curve:", "prime192v1 / secp192r1 (legacy)")
print("Public key:", public_key.xy())
print("Message:", message)
print("Signature (r, s):", (r, s))
print("Verification result:", ecdsa_verify(public_key, message, r, s))

