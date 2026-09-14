"""Toy exponential-ElGamal tally.

This demonstrates only homomorphic aggregation. It does NOT implement ballot-validity
proofs, DKG, threshold decryption, coercion resistance, eligibility, or a secure election.
"""
from __future__ import annotations
import secrets

P = 23
Q = 11
G = 2


def keygen():
    x = secrets.randbelow(Q - 1) + 1
    return x, pow(G, x, P)


def encrypt_bit(pk: int, bit: int):
    if bit not in (0, 1):
        raise ValueError("this toy encoder accepts only bits")
    r = secrets.randbelow(Q - 1) + 1
    return pow(G, r, P), (pow(pk, r, P) * pow(G, bit, P)) % P


def combine(ciphertexts):
    c1 = 1
    c2 = 1
    for a, b in ciphertexts:
        c1 = c1 * a % P
        c2 = c2 * b % P
    return c1, c2


def decrypt_group_element(sk: int, ct):
    c1, c2 = ct
    shared = pow(c1, sk, P)
    return c2 * pow(shared, -1, P) % P


def decode_small_tally(element: int, maximum: int):
    cur = 1
    for total in range(maximum + 1):
        if cur == element:
            return total
        cur = cur * G % P
    raise ValueError("tally outside decoding range")


def demo():
    sk, pk = keygen()
    votes = [1, 0, 1, 1, 0]
    aggregate = combine(encrypt_bit(pk, v) for v in votes)
    encoded = decrypt_group_element(sk, aggregate)
    assert decode_small_tally(encoded, len(votes)) == sum(votes)
    print("toy homomorphic tally recovered", sum(votes), "yes votes")


if __name__ == "__main__":
    demo()
