"""Create and verify an EC-KCDSA-style signature."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/eckcdsa.sage")

public_key, private_key = eckcdsa_keygen()
message = b"hello"
certificate_data = b"educational-certificate-context"
r, s = eckcdsa_sign(private_key, message, certificate_data)

print("Public key convention: Q = d^(-1)P")
print("Public key:", public_key.xy())
print("Signature (r, s):", (r, s))
print("Verification result:", eckcdsa_verify(
    public_key, message, r, s, certificate_data
))

