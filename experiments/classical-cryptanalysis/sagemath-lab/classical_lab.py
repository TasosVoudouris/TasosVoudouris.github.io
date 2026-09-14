"""Cleaned versions of selected classical-cryptography exercises from old Sage worksheets.

Dependency-free Python; educational only.
"""
from math import gcd

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def text_to_nums(s):
    return [ord(c) - 65 for c in s.upper() if c.isalpha()]


def nums_to_text(xs):
    return "".join(chr((x % 26) + 65) for x in xs)


def shift_encrypt(msg, k):
    return nums_to_text(x + k for x in text_to_nums(msg))


def shift_decrypt(ct, k):
    return nums_to_text(x - k for x in text_to_nums(ct))


def affine_encrypt(msg, a, b):
    if gcd(a, 26) != 1:
        raise ValueError("a must be invertible modulo 26")
    return nums_to_text(a * x + b for x in text_to_nums(msg))


def affine_decrypt(ct, a, b):
    ai = pow(a, -1, 26)
    return nums_to_text(ai * (x - b) for x in text_to_nums(ct))


def compose_affine(a1, b1, a2, b2):
    # E2(E1(x)) = a2(a1 x + b1)+b2.
    return (a2 * a1) % 26, (a2 * b1 + b2) % 26


def inv2x2_mod(K, m=26):
    a, b = K[0]
    c, d = K[1]
    det = (a * d - b * c) % m
    if gcd(det, m) != 1:
        raise ValueError("Hill key matrix is not invertible modulo 26")
    di = pow(det, -1, m)
    return [[d * di % m, -b * di % m], [-c * di % m, a * di % m]]


def hill_apply(block, K, m=26):
    x, y = block
    return [(K[0][0] * x + K[0][1] * y) % m,
            (K[1][0] * x + K[1][1] * y) % m]


def hill_encrypt(msg, K):
    xs = text_to_nums(msg)
    if len(xs) % 2:
        xs.append(ord('X') - 65)
    out = []
    for i in range(0, len(xs), 2):
        out.extend(hill_apply(xs[i:i+2], K))
    return nums_to_text(out)


def hill_decrypt(ct, K):
    Ki = inv2x2_mod(K)
    xs = text_to_nums(ct)
    out = []
    for i in range(0, len(xs), 2):
        out.extend(hill_apply(xs[i:i+2], Ki))
    return nums_to_text(out)


def self_test():
    assert shift_decrypt(shift_encrypt("ALICE", 13), 13) == "ALICE"

    assert affine_decrypt(affine_encrypt("CRYPTO", 5, 8), 5, 8) == "CRYPTO"

    # Important correction to the old worksheet: 3x+5 followed by 11x+7
    # is 7x+10 mod 26, not 20x+10.
    a3, b3 = compose_affine(3, 5, 11, 7)
    assert (a3, b3) == (7, 10)
    assert affine_encrypt(affine_encrypt("K", 3, 5), 11, 7) == affine_encrypt("K", a3, b3)

    K = [[3, 3], [2, 5]]
    ct = hill_encrypt("HELP", K)
    assert hill_decrypt(ct, K) == "HELP"

    print("PASS: shift, affine composition, and Hill-cipher checks")


if __name__ == "__main__":
    self_test()
