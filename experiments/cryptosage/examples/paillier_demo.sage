"""Encrypt, decrypt, and homomorphically add two small integers."""

load("src/integer_factorization/paillier.sage")

public_key, private_key = paillier_keygen(prime_bits=256)
message_1 = Integer(randint(0, 1000))
message_2 = Integer(randint(0, 1000))
ciphertext_1 = paillier_encrypt(message_1, public_key)
ciphertext_2 = paillier_encrypt(message_2, public_key)
ciphertext_sum = paillier_ciphertext_add(
    ciphertext_1, ciphertext_2, public_key
)

print("Message 1:", message_1)
print("Decryption 1:", paillier_decrypt(ciphertext_1, public_key, private_key))
print("Message 2:", message_2)
print("Decryption 2:", paillier_decrypt(ciphertext_2, public_key, private_key))
print("Expected modular sum:", (message_1 + message_2) % public_key[0])
print("Decrypted homomorphic sum:", paillier_decrypt(
    ciphertext_sum, public_key, private_key
))

