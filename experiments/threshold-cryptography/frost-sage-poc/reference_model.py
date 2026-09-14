"""Dependency-free reference model for the audited FROST SageMath proof of concept.

This is NOT an RFC 9591 wire-compatible implementation. It exists to validate
and explain the algebra exercised by the collaborator's SageMath proof of
concept with explicit scalar reduction, subset signing, share verification,
and final aggregate-signature verification.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
from typing import Iterable

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)
INF = None


def inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def point_add(a, b):
    if a is INF:
        return b
    if b is INF:
        return a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return INF
    if a == b:
        if y1 == 0:
            return INF
        slope = (3 * x1 * x1) * inv(2 * y1, P) % P
    else:
        slope = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


def point_mul(k: int, p=G):
    k %= Q
    out = INF
    cur = p
    while k:
        if k & 1:
            out = point_add(out, cur)
        cur = point_add(cur, cur)
        k >>= 1
    return out


def point_sum(points: Iterable):
    out = INF
    for p in points:
        out = point_add(out, p)
    return out


def enc_point(p) -> bytes:
    if p is INF:
        raise ValueError("identity point cannot be encoded")
    x, y = p
    return bytes([2 | (y & 1)]) + x.to_bytes(32, "big")


def enc_scalar(x: int) -> bytes:
    return (x % Q).to_bytes(32, "big")


def h_scalar(domain: bytes, *parts: bytes) -> int:
    h = hashlib.sha256()
    h.update(len(domain).to_bytes(2, "big"))
    h.update(domain)
    for part in parts:
        h.update(len(part).to_bytes(8, "big"))
        h.update(part)
    return int.from_bytes(h.digest(), "big") % Q


def lagrange_at_zero(i: int, signer_ids: list[int]) -> int:
    num = 1
    den = 1
    for j in signer_ids:
        if j == i:
            continue
        num = (num * j) % Q
        den = (den * (j - i)) % Q
    return num * inv(den, Q) % Q


def eval_poly(coeffs: list[int], x: int) -> int:
    acc = 0
    power = 1
    for c in coeffs:
        acc = (acc + c * power) % Q
        power = power * x % Q
    return acc


@dataclass
class Dealer:
    identifier: int
    coeffs: list[int]

    @property
    def commitments(self):
        return [point_mul(c) for c in self.coeffs]

    def share_for(self, participant_id: int) -> int:
        return eval_poly(self.coeffs, participant_id)


@dataclass
class Signer:
    identifier: int
    sk_share: int
    pk_share: tuple[int, int]
    nonce_pairs: list[tuple[int, int]]


class ReferenceFrost:
    def __init__(self, threshold: int, participants: int, seed: int = 0xF09A):
        if not (2 <= threshold <= participants):
            raise ValueError("require 2 <= threshold <= participants")
        self.t = threshold
        self.n = participants
        self.rng = random.Random(seed)
        self.dealers: list[Dealer] = []
        self.signers: dict[int, Signer] = {}
        self.group_key = INF

    def scalar(self) -> int:
        return self.rng.randrange(1, Q)

    def dkg(self):
        self.dealers = []
        for i in range(1, self.n + 1):
            coeffs = [self.scalar() for _ in range(self.t)]
            self.dealers.append(Dealer(i, coeffs))

        # Every receiver verifies every Feldman share against the dealer vector.
        received: dict[int, list[int]] = {i: [] for i in range(1, self.n + 1)}
        for dealer in self.dealers:
            commitments = dealer.commitments
            for receiver in range(1, self.n + 1):
                share = dealer.share_for(receiver)
                expected = point_sum(
                    point_mul(pow(receiver, k, Q), commitments[k])
                    for k in range(self.t)
                )
                if point_mul(share) != expected:
                    raise AssertionError("Feldman share verification failed")
                received[receiver].append(share)

        self.group_key = point_sum(d.commitments[0] for d in self.dealers)
        if self.group_key is INF:
            raise AssertionError("identity group key")

        self.signers.clear()
        for i in range(1, self.n + 1):
            sk = sum(received[i]) % Q
            self.signers[i] = Signer(i, sk, point_mul(sk), [])

        # Cross-check that any threshold subset interpolates the aggregate secret.
        aggregate_secret = sum(d.coeffs[0] for d in self.dealers) % Q
        ids = list(range(1, self.t + 1))
        reconstructed = sum(
            lagrange_at_zero(i, ids) * self.signers[i].sk_share for i in ids
        ) % Q
        if reconstructed != aggregate_secret:
            raise AssertionError("threshold interpolation did not recover group secret")
        if point_mul(aggregate_secret) != self.group_key:
            raise AssertionError("group public key mismatch")

    def preprocess(self, count: int):
        for signer in self.signers.values():
            signer.nonce_pairs = [(self.scalar(), self.scalar()) for _ in range(count)]

    @staticmethod
    def encode_commitment_list(commitments: list[tuple[int, tuple, tuple]]) -> bytes:
        out = bytearray()
        for identifier, D, E in sorted(commitments):
            out += enc_scalar(identifier)
            out += enc_point(D)
            out += enc_point(E)
        return bytes(out)

    def binding_factor(self, identifier: int, message: bytes, encoded_list: bytes) -> int:
        return h_scalar(
            b"CryptoCave/FROST/rho",
            enc_point(self.group_key),
            hashlib.sha256(message).digest(),
            hashlib.sha256(encoded_list).digest(),
            enc_scalar(identifier),
        )

    def challenge(self, R, message: bytes) -> int:
        return h_scalar(
            b"CryptoCave/FROST/chal", enc_point(R), enc_point(self.group_key), message
        )

    def sign(self, message: bytes, signer_ids: list[int]):
        signer_ids = sorted(signer_ids)
        if len(signer_ids) < self.t:
            raise ValueError("not enough signers")
        if len(set(signer_ids)) != len(signer_ids):
            raise ValueError("duplicate signer")

        commitments = []
        private_nonces = {}
        for i in signer_ids:
            signer = self.signers[i]
            if not signer.nonce_pairs:
                raise ValueError(f"signer {i} has no preprocessed nonce pair")
            d, e = signer.nonce_pairs.pop(0)  # consume exactly once
            private_nonces[i] = (d, e)
            commitments.append((i, point_mul(d), point_mul(e)))

        encoded = self.encode_commitment_list(commitments)
        rho = {
            i: self.binding_factor(i, message, encoded)
            for i, _, _ in commitments
        }
        Ri = {
            i: point_add(D, point_mul(rho[i], E))
            for i, D, E in commitments
        }
        R = point_sum(Ri.values())
        if R is INF:
            raise AssertionError("identity group commitment")
        c = self.challenge(R, message)

        shares = {}
        for i in signer_ids:
            d, e = private_nonces[i]
            lam = lagrange_at_zero(i, signer_ids)
            z_i = (d + e * rho[i] + lam * self.signers[i].sk_share * c) % Q
            shares[i] = z_i
            lhs = point_mul(z_i)
            rhs = point_add(Ri[i], point_mul((c * lam) % Q, self.signers[i].pk_share))
            if lhs != rhs:
                raise AssertionError(f"signature share {i} failed verification")

        z = sum(shares.values()) % Q
        if point_mul(z) != point_add(R, point_mul(c, self.group_key)):
            raise AssertionError("final aggregate signature failed verification")
        return R, z


def main():
    frost = ReferenceFrost(threshold=4, participants=5)
    frost.dkg()
    frost.preprocess(8)

    subsets = [
        [1, 2, 3, 4],
        [1, 2, 4, 5],
        [1, 3, 4, 5],
        [2, 3, 4, 5],
        [1, 2, 3, 4, 5],
    ]
    for round_no, ids in enumerate(subsets, 1):
        R, z = frost.sign(f"message-{round_no}".encode(), ids)
        print(f"PASS round={round_no} signers={ids} R.x={R[0]:064x} z={z:064x}")

    # Prove that threshold enforcement is real, not merely a comment.
    try:
        frost.sign(b"too-few", [1, 2, 3])
    except ValueError as exc:
        print(f"PASS rejected 3-of-5 attempt: {exc}")
    else:
        raise AssertionError("3-of-5 signing should have been rejected for t=4")


if __name__ == "__main__":
    main()
