"""Educational ECDSA nonce-reuse demonstration on secp256k1.

This file intentionally implements only the algebra needed to show why reusing
an ECDSA nonce reveals the long-term private key. It is not production crypto.
"""
from __future__ import annotations

import hashlib
import secrets

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)


def inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        lam = (3 * x1 * x1 + A) * inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return x3, y3


def mul(k: int, point=G):
    result = None
    addend = point
    while k:
        if k & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        k >>= 1
    return result


def h(msg: bytes) -> int:
    return int.from_bytes(hashlib.sha256(msg).digest(), "big") % N


def sign_with_nonce(d: int, msg: bytes, k: int):
    r_point = mul(k)
    assert r_point is not None
    r = r_point[0] % N
    if r == 0:
        raise ValueError("invalid nonce produced r=0")
    s = (inv(k, N) * (h(msg) + r * d)) % N
    if s == 0:
        raise ValueError("invalid nonce produced s=0")
    return r, s


def verify(q, msg: bytes, sig) -> bool:
    r, s = sig
    if not (1 <= r < N and 1 <= s < N):
        return False
    w = inv(s, N)
    point = add(mul(h(msg) * w % N), mul(r * w % N, q))
    return point is not None and point[0] % N == r


def recover_from_reused_nonce(msg1: bytes, sig1, msg2: bytes, sig2):
    r1, s1 = sig1
    r2, s2 = sig2
    if r1 != r2:
        raise ValueError("the signatures do not expose a reused nonce")
    k = ((h(msg1) - h(msg2)) * inv(s1 - s2, N)) % N
    d = ((s1 * k - h(msg1)) * inv(r1, N)) % N
    return k, d


def demo() -> None:
    d = secrets.randbelow(N - 1) + 1
    q = mul(d)
    k = secrets.randbelow(N - 1) + 1
    m1 = b"first message"
    m2 = b"second message"
    sig1 = sign_with_nonce(d, m1, k)
    sig2 = sign_with_nonce(d, m2, k)
    assert verify(q, m1, sig1)
    assert verify(q, m2, sig2)
    recovered_k, recovered_d = recover_from_reused_nonce(m1, sig1, m2, sig2)
    assert recovered_k == k
    assert recovered_d == d
    print("ECDSA nonce-reuse demo: recovered nonce and private key correctly")


if __name__ == "__main__":
    demo()
