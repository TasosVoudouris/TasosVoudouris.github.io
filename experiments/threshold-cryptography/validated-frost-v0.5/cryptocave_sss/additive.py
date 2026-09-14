"""Simple N-out-of-N additive secret sharing."""

from __future__ import annotations

import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from random import Random
from typing import Protocol

if __package__:
    from .field import decode_signed, encode_signed, require_prime
else:
    from field import decode_signed, encode_signed, require_prime


class RandomSource(Protocol):
    def randrange(self, stop: int) -> int: ...


def _random_source(rng: RandomSource | None) -> RandomSource:
    # SystemRandom obtains randomness from the operating system.
    return rng if rng is not None else secrets.SystemRandom()


def additive_share(
    secret: int,
    num_parties: int,
    modulus: int,
    rng: RandomSource | None = None,
) -> list[int]:
    """Split ``secret`` into ``num_parties`` additive shares.

    Every strict subset of the shares is compatible with every possible secret.
    All shares are needed for reconstruction.
    """

    require_prime(modulus)
    if num_parties < 2:
        raise ValueError("additive sharing needs at least two parties")

    source = _random_source(rng)
    encoded_secret = encode_signed(secret, modulus)
    shares = [source.randrange(modulus) for _ in range(num_parties - 1)]
    shares.append((encoded_secret - sum(shares)) % modulus)
    return shares


def additive_reconstruct(shares: Sequence[int], modulus: int) -> int:
    """Reconstruct the field element represented by additive shares."""

    require_prime(modulus)
    if not shares:
        raise ValueError("at least one share is required")
    return sum(shares) % modulus


def explain_missing_share(
    known_shares: Sequence[int], guessed_secret: int, modulus: int
) -> int:
    """Construct the missing share that makes ``guessed_secret`` possible.

    This is the same privacy demonstration found in the original ``sss.py``.
    """

    return (encode_signed(guessed_secret, modulus) - sum(known_shares)) % modulus


@dataclass(frozen=True)
class AdditiveSecret:
    """A thin wrapper that keeps the original operator-based learning style."""

    shares: tuple[int, ...]
    modulus: int

    @classmethod
    def from_secret(
        cls,
        secret: int,
        num_parties: int,
        modulus: int,
        rng: RandomSource | None = None,
    ) -> "AdditiveSecret":
        return cls(tuple(additive_share(secret, num_parties, modulus, rng)), modulus)

    def reveal_field_element(self) -> int:
        return additive_reconstruct(self.shares, self.modulus)

    def reveal(self) -> int:
        return decode_signed(self.reveal_field_element(), self.modulus)

    def _check_compatible(self, other: "AdditiveSecret") -> None:
        if self.modulus != other.modulus:
            raise ValueError("the two sharings use different fields")
        if len(self.shares) != len(other.shares):
            raise ValueError("the two sharings use different party counts")

    def __add__(self, other: "AdditiveSecret") -> "AdditiveSecret":
        self._check_compatible(other)
        values = tuple(
            (left + right) % self.modulus
            for left, right in zip(self.shares, other.shares)
        )
        return AdditiveSecret(values, self.modulus)

    def __sub__(self, other: "AdditiveSecret") -> "AdditiveSecret":
        self._check_compatible(other)
        values = tuple(
            (left - right) % self.modulus
            for left, right in zip(self.shares, other.shares)
        )
        return AdditiveSecret(values, self.modulus)

    def scale(self, public_scalar: int) -> "AdditiveSecret":
        values = tuple(
            public_scalar * share % self.modulus for share in self.shares
        )
        return AdditiveSecret(values, self.modulus)

    def __repr__(self) -> str:
        return f"AdditiveSecret(num_parties={len(self.shares)}, modulus={self.modulus})"


def deterministic_rng(seed: int) -> Random:
    """Return a deterministic RNG for examples and tests only."""

    return Random(seed)


def demo() -> None:
    """Share and reconstruct one value when this module is run directly."""

    shared = AdditiveSecret.from_secret(5, 4, 41, Random(1))
    print("Secret: 5")
    print("Four additive shares:", list(shared.shares))
    print("Reconstructed secret:", shared.reveal())


if __name__ == "__main__":
    demo()
