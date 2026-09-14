"""Toy 1-out-of-2 OT from an RSA trapdoor permutation (EGL-style illustration)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RSAKey:
    n: int
    e: int
    d: int


def make_toy_key() -> RSAKey:
    p, q, e = 499, 547, 65537
    phi = (p - 1) * (q - 1)
    return RSAKey(p * q, e, pow(e, -1, phi))


def receiver_request(key: RSAKey, x0: int, x1: int, choice: int, k: int) -> int:
    x = (x0, x1)[choice]
    return (x + pow(k, key.e, key.n)) % key.n


def sender_response(key: RSAKey, x0: int, x1: int, v: int, m0: int, m1: int) -> tuple[int, int]:
    k0 = pow((v - x0) % key.n, key.d, key.n)
    k1 = pow((v - x1) % key.n, key.d, key.n)
    return ((m0 + k0) % key.n, (m1 + k1) % key.n)


def receiver_open(key: RSAKey, masked: tuple[int, int], choice: int, k: int) -> int:
    return (masked[choice] - k) % key.n
