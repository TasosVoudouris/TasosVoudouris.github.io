"""Educational Schnorr Sigma protocol over a tiny subgroup.

NOT FOR PRODUCTION. Parameters are intentionally tiny so the algebra is visible.
Demonstrates completeness and special-soundness extraction from two accepting
transcripts with the same commitment and distinct challenges.
"""
from dataclasses import dataclass
from random import Random

P = 23
Q = 11
G = 2  # order 11 modulo 23

@dataclass(frozen=True)
class Transcript:
    t: int
    c: int
    z: int


def public_key(secret: int) -> int:
    return pow(G, secret % Q, P)


def commit(nonce: int) -> int:
    return pow(G, nonce % Q, P)


def respond(nonce: int, challenge: int, secret: int) -> int:
    return (nonce + challenge * secret) % Q


def verify(y: int, tr: Transcript) -> bool:
    lhs = pow(G, tr.z, P)
    rhs = (tr.t * pow(y, tr.c, P)) % P
    return lhs == rhs


def inv_mod(a: int, m: int) -> int:
    return pow(a % m, -1, m)


def extract_secret(a: Transcript, b: Transcript) -> int:
    if a.t != b.t or a.c == b.c:
        raise ValueError("need same commitment and distinct challenges")
    # z1-z2 = (c1-c2) x mod q
    return ((a.z - b.z) * inv_mod(a.c - b.c, Q)) % Q


def self_test() -> None:
    rng = Random(7)
    x = 6
    y = public_key(x)
    r = rng.randrange(Q)
    t = commit(r)
    tr1 = Transcript(t=t, c=3, z=respond(r, 3, x))
    tr2 = Transcript(t=t, c=8, z=respond(r, 8, x))
    assert verify(y, tr1)
    assert verify(y, tr2)
    assert extract_secret(tr1, tr2) == x
    print("Schnorr Sigma protocol: PASS")
    print("special-soundness extractor: PASS")


if __name__ == "__main__":
    self_test()
