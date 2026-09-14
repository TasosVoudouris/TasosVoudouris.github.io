"""Toy additive secret sharing over a prime field.

Educational code: small parameters, no authentication or transport layer.
"""
from __future__ import annotations

from dataclasses import dataclass
import secrets


@dataclass
class AdditiveSharing:
    q: int
    shares: list[int]

    @classmethod
    def share(cls, secret: int, *, n: int, q: int) -> "AdditiveSharing":
        if n < 2:
            raise ValueError("n must be at least 2")
        if not 0 <= secret < q:
            raise ValueError("secret must be represented in F_q")

        parts = [secrets.randbelow(q) for _ in range(n - 1)]
        parts.append((secret - sum(parts)) % q)
        return cls(q=q, shares=parts)

    def reconstruct(self) -> int:
        return sum(self.shares) % self.q

    def __add__(self, other: "AdditiveSharing") -> "AdditiveSharing":
        self._check_compatible(other)
        return AdditiveSharing(
            q=self.q,
            shares=[(a + b) % self.q for a, b in zip(self.shares, other.shares)],
        )

    def __sub__(self, other: "AdditiveSharing") -> "AdditiveSharing":
        self._check_compatible(other)
        return AdditiveSharing(
            q=self.q,
            shares=[(a - b) % self.q for a, b in zip(self.shares, other.shares)],
        )

    def _check_compatible(self, other: "AdditiveSharing") -> None:
        if self.q != other.q or len(self.shares) != len(other.shares):
            raise ValueError("sharings must use the same field and participant count")


if __name__ == "__main__":
    q, n = 41, 5
    x_secret, y_secret = 17, 9

    x = AdditiveSharing.share(x_secret, n=n, q=q)
    y = AdditiveSharing.share(y_secret, n=n, q=q)

    assert x.reconstruct() == x_secret
    assert y.reconstruct() == y_secret
    assert (x + y).reconstruct() == (x_secret + y_secret) % q
    assert (x - y).reconstruct() == (x_secret - y_secret) % q

    print("x shares:", x.shares)
    print("y shares:", y.shares)
    print("additive sharing checks passed")
