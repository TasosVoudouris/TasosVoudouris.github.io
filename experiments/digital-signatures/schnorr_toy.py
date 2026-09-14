"""Small-group Schnorr signature demonstration.

Uses deliberately tiny parameters so every step can be inspected. Not secure.
"""
from __future__ import annotations
import hashlib
import secrets

# q | p-1, and g has order q modulo p.
P = 10007
Q = 5003
G = 2
assert pow(G, Q, P) == 1 and G != 1


def H(r: int, y: int, msg: bytes) -> int:
    blob = r.to_bytes(2, "big") + y.to_bytes(2, "big") + msg
    return int.from_bytes(hashlib.sha256(blob).digest(), "big") % Q


def keygen():
    x = secrets.randbelow(Q - 1) + 1
    y = pow(G, x, P)
    return x, y


def sign(x: int, y: int, msg: bytes, nonce: int | None = None):
    k = nonce if nonce is not None else secrets.randbelow(Q - 1) + 1
    if not (1 <= k < Q):
        raise ValueError("nonce must be in 1..q-1")
    r = pow(G, k, P)
    e = H(r, y, msg)
    s = (k + e * x) % Q
    return r, s


def verify(y: int, msg: bytes, sig) -> bool:
    r, s = sig
    if not (1 <= r < P and 0 <= s < Q):
        return False
    e = H(r, y, msg)
    return pow(G, s, P) == (r * pow(y, e, P)) % P


def demo():
    x, y = keygen()
    msg = b"CryptoCave"
    sig = sign(x, y, msg)
    assert verify(y, msg, sig)
    assert not verify(y, b"CryptoCave!", sig)
    print("toy Schnorr demo: valid signature accepted, modified message rejected")


if __name__ == "__main__":
    demo()
