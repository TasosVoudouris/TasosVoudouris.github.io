"""Encrypt and decrypt a byte string with the ECIES-style demonstration."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/key_generation.sage")
load("src/elliptic_curves/ecies.sage")

public_key, private_key = ec_keygen()
message = b"hello from CryptoSage"
ephemeral_point, encrypted_body, tag = ecies_encrypt(public_key, message)
recovered = ecies_decrypt(
    ephemeral_point, encrypted_body, tag, private_key
)

print("Plaintext:", message)
print("Ciphertext length:", len(encrypted_body), "bytes")
print("Authentication tag length:", len(tag), "bytes")
print("Recovered plaintext:", recovered)
print("Round trip successful:", recovered == message)

