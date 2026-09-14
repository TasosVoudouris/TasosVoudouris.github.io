"""Toy Fiat-Shamir transform applied to a Schnorr proof of knowledge.

NOT FOR PRODUCTION. Uses tiny parameters. The transcript hash includes a domain
separator, the statement, and the prover commitment so that challenge binding is
explicit in the example.
"""
import hashlib
from dataclasses import dataclass

P = 23
Q = 11
G = 2
DOMAIN = b"CryptoCave/SchnorrPoK/v1"

@dataclass(frozen=True)
class Proof:
    t: int
    z: int


def H_to_challenge(y: int, t: int) -> int:
    h = hashlib.sha256()
    h.update(DOMAIN)
    h.update(y.to_bytes(2, "big"))
    h.update(t.to_bytes(2, "big"))
    return int.from_bytes(h.digest(), "big") % Q


def prove(secret: int, nonce: int) -> tuple[int, Proof]:
    y = pow(G, secret % Q, P)
    t = pow(G, nonce % Q, P)
    c = H_to_challenge(y, t)
    z = (nonce + c * secret) % Q
    return y, Proof(t=t, z=z)


def verify(y: int, proof: Proof) -> bool:
    c = H_to_challenge(y, proof.t)
    return pow(G, proof.z, P) == (proof.t * pow(y, c, P)) % P


def self_test() -> None:
    y, proof = prove(secret=6, nonce=4)
    assert verify(y, proof)
    assert not verify(pow(G, 5, P), proof)
    assert not verify(y, Proof(t=proof.t, z=(proof.z + 1) % Q))
    print("Fiat-Shamir Schnorr toy proof: PASS")
    print("statement/transcript binding checks: PASS")


if __name__ == "__main__":
    self_test()
