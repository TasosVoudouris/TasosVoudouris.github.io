"""Generate an RSA key and print non-secret consistency information."""

load("src/integer_factorization/rsa_keygen.sage")

public_key, private_key = rsa_keygen(prime_bits=512)
print_rsa_key_summary(public_key, private_key)

