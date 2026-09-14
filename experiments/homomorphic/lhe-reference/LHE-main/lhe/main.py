from lhe import *


def main():
    sk1, pk1 = keygen_G1()
    sk2, pk2 = keygen_G2()
    print("Generated G1 keypair:")
    print("Secret key (sk1):", sk1)
    print("Public key (pk1):", pk1)
    print("Generated G2 keypair:")
    print("Secret key (sk2):", sk2)
    print("Public key (pk2):", pk2)

    # Test case 1
    ct1 = encrypt_G1(pk1, 3)
    print("Encrypted plaintext 3 to G1 ciphertext (ct1):", ct1)
    ct2 = encrypt_G2(pk2, 222)
    print("Encrypted plaintext 222 to G2 ciphertext (ct2):", ct2)

    ct3 = multiply_G1_G2(ct1, ct2)
    print("Result of homomorphic multiplication (ct3):", ct3)
    ct4 = add_GT(ct3, ct3)
    print("Result of homomorphic addition (ct4):", ct4)

    pt = decrypt_GT(sk1, sk2, ct3)
    print("Decrypted result of ct3:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

    pt = decrypt_GT(sk1, sk2, ct4)
    print("Decrypted result of ct4:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

    # Test case 2
    ct1 = encrypt_G1(pk1, 10)
    print("Encrypted plaintext 10 to G1 ciphertext (ct1):", ct1)
    ct2 = encrypt_G2(pk2, 5)
    print("Encrypted plaintext 5 to G2 ciphertext (ct2):", ct2)

    ct3 = multiply_G1_G2(ct1, ct2)
    print("Result of homomorphic multiplication (ct3):", ct3)
    ct4 = add_GT(ct3, ct3)
    print("Result of homomorphic addition (ct4):", ct4)

    pt = decrypt_GT(sk1, sk2, ct3)
    print("Decrypted result of ct3:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

    pt = decrypt_GT(sk1, sk2, ct4)
    print("Decrypted result of ct4:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

    # Test case 3
    ct1 = encrypt_G1(pk1, 7)
    print("Encrypted plaintext 7 to G1 ciphertext (ct1):", ct1)
    ct2 = encrypt_G2(pk2, 14)
    print("Encrypted plaintext 14 to G2 ciphertext (ct2):", ct2)

    ct3 = multiply_G1_G2(ct1, ct2)
    print("Result of homomorphic multiplication (ct3):", ct3)
    ct4 = add_GT(ct3, ct3)
    print("Result of homomorphic addition (ct4):", ct4)

    pt = decrypt_GT(sk1, sk2, ct3)
    print("Decrypted result of ct3:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

    pt = decrypt_GT(sk1, sk2, ct4)
    print("Decrypted result of ct4:")
    print("This may take a bit of time for large plaintexts...")
    print(pt)

main()