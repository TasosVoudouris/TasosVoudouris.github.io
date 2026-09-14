"""Encrypt and decrypt a byte string with the PSEC-style demonstration."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/key_generation.sage")
load("src/elliptic_curves/psec.sage")

public_key, private_key = ec_keygen()
message = b"hello from the PSEC study"
ephemeral_point, encrypted_body, masked_seed, tag = psec_encrypt(
    public_key, message
)
recovered = psec_decrypt(
    ephemeral_point,
    encrypted_body,
    masked_seed,
    tag,
    private_key,
)

print("Plaintext:", message)
print("Masked seed bits:", Integer(masked_seed).nbits())
print("Recovered plaintext:", recovered)
print("Round trip successful:", recovered == message)

