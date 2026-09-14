"""
RSA Deep Dive I — textbook RSA failure demo.

Educational toy only.

This demonstrates:
1. deterministic textbook RSA encryption;
2. multiplicative ciphertext malleability;
3. a textbook chosen-ciphertext recovery using a decryption oracle.

It does NOT implement OAEP and must not be used as production cryptography.
"""

from math import gcd


N = 3233
E = 17
D = 413


def encrypt_textbook(message: int) -> int:
    if not 0 <= message < N:
        raise ValueError("message representative must satisfy 0 <= m < N")
    return pow(message, E, N)


def decrypt_textbook(ciphertext: int) -> int:
    if not 0 <= ciphertext < N:
        raise ValueError("ciphertext representative must satisfy 0 <= c < N")
    return pow(ciphertext, D, N)


def heading(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


heading("1. Textbook RSA is deterministic")

message = 42

c1 = encrypt_textbook(message)
c2 = encrypt_textbook(message)

print("message =", message)
print("first ciphertext  =", c1)
print("second ciphertext =", c2)
print("same?", c1 == c2)

assert c1 == c2 == 2557


heading("2. Multiplicative malleability")

r = 2
assert gcd(r, N) == 1

r_to_e = pow(r, E, N)
modified = (c1 * r_to_e) % N

modified_plaintext = decrypt_textbook(modified)

print("target ciphertext =", c1)
print("multiplier r      =", r)
print("r^e mod N         =", r_to_e)
print("modified c'       =", modified)
print("decrypt(c')       =", modified_plaintext)
print("expected m*r      =", (message * r) % N)

assert r_to_e == 1752
assert modified == 2159
assert modified_plaintext == 84
assert modified_plaintext == (message * r) % N


heading("3. Textbook chosen-ciphertext recovery")

# Imagine an oracle refuses to decrypt the original target c1,
# but it decrypts the different ciphertext 'modified'.
oracle_reply = modified_plaintext

r_inverse = pow(r, -1, N)
recovered = (oracle_reply * r_inverse) % N

print("oracle returned m*r =", oracle_reply)
print("r^(-1) mod N        =", r_inverse)
print("recovered m          =", recovered)

assert r_inverse == 1617
assert recovered == message

print()
print("Recovered the original message without factoring N or recovering D.")
print("Lesson: the raw RSA primitive is not a secure encryption scheme.")
