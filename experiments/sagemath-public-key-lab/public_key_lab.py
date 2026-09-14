"""Dependency-free toy public-key lab distilled from old Sage exercises.

The goal is to expose the algebra and implementation pitfalls, not to provide secure cryptography.
"""
from math import gcd


def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def rsa_toy():
    p, q = 1009, 1013
    n = p * q
    lam = (p - 1) * (q - 1) // gcd(p - 1, q - 1)
    e = 65537
    d = pow(e, -1, lam)
    m = 123456
    c = pow(m, e, n)
    assert pow(c, d, n) == m

    # CRT decryption.
    mp = pow(c, d % (p - 1), p)
    mq = pow(c, d % (q - 1), q)
    qinv = pow(q, -1, p)
    mcrt = (mq + q * (((mp - mq) * qinv) % p)) % n
    assert mcrt == m
    return n, e, d


def common_modulus_attack():
    p, q = 37, 43
    n = p * q
    e1, e2 = 17, 5
    m = 123
    c1, c2 = pow(m, e1, n), pow(m, e2, n)
    g, a, b = egcd(e1, e2)
    assert g == 1

    def signed_pow(c, exponent):
        if exponent >= 0:
            return pow(c, exponent, n)
        return pow(pow(c, -1, n), -exponent, n)

    recovered = (signed_pow(c1, a) * signed_pow(c2, b)) % n
    assert recovered == m
    return recovered


def dh_toy():
    # Tiny safe-prime subgroup for demonstration only.
    p = 23
    q = 11
    g = 2  # order 11 modulo 23
    assert pow(g, q, p) == 1 and g != 1
    a, b = 6, 7
    A, B = pow(g, a, p), pow(g, b, p)
    s1, s2 = pow(B, a, p), pow(A, b, p)
    assert s1 == s2
    return s1


def elgamal_toy():
    p = 467
    g = 2
    x = 127
    y = pow(g, x, p)
    m = 123
    k = 53
    c1 = pow(g, k, p)
    c2 = (m * pow(y, k, p)) % p
    recovered = (c2 * pow(pow(c1, x, p), -1, p)) % p
    assert recovered == m
    return c1, c2


def textbook_rsa_signature_forgery_demo():
    # Existential forgery against the *textbook* scheme: choose s, define m=s^e mod n.
    n, e = 9797, 131
    s = 65
    m = pow(s, e, n)
    assert pow(s, e, n) == m
    return m, s


def self_test():
    rsa_toy()
    assert common_modulus_attack() == 123
    dh_toy()
    elgamal_toy()
    textbook_rsa_signature_forgery_demo()
    print("PASS: RSA/CRT, common-modulus, DH, ElGamal, and textbook-signature toy checks")


if __name__ == "__main__":
    self_test()
