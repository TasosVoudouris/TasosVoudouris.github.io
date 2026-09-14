"""A small, readable implementation of Shamir secret sharing.

The class follows the style of the original ``shamir.py`` while correcting its
most important ambiguity: ``threshold`` is the number of shares required for
reconstruction, whereas ``degree_bound`` is one less than the threshold.
"""

from __future__ import annotations

import secrets
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

if __package__:
    from .field import decode_signed, encode_signed, require_prime
    from .polynomial import evaluate, interpolate
else:
    from field import decode_signed, encode_signed, require_prime
    from polynomial import evaluate, interpolate


class RandomSource(Protocol):
    def randrange(self, stop: int) -> int: ...


@dataclass(frozen=True, order=True)
class Share:
    """One Shamir share ``(x, y)``."""

    x: int
    y: int


class ShamirScheme:
    """Parameters and operations for one Shamir sharing domain."""

    def __init__(
        self,
        modulus: int,
        num_parties: int,
        threshold: int,
        participant_ids: Sequence[int] | None = None,
        rng: RandomSource | None = None,
    ) -> None:
        require_prime(modulus)
        if not 2 <= threshold <= num_parties:
            raise ValueError("require 2 <= threshold <= num_parties")
        if num_parties >= modulus:
            raise ValueError("num_parties must be smaller than the field modulus")

        ids = list(participant_ids or range(1, num_parties + 1))
        if len(ids) != num_parties:
            raise ValueError("participant_ids must contain num_parties entries")
        ids = [identifier % modulus for identifier in ids]
        if 0 in ids:
            raise ValueError("participant identifiers must be nonzero")
        if len(set(ids)) != len(ids):
            raise ValueError("participant identifiers must be distinct")

        self.modulus = modulus
        self.num_parties = num_parties
        self.threshold = threshold
        self.degree = threshold - 1
        self.participant_ids = tuple(ids)
        self.rng = rng if rng is not None else secrets.SystemRandom()

    def sample_polynomial(self, secret: int) -> list[int]:
        """Sample a polynomial whose constant coefficient is ``secret``."""

        constant = encode_signed(secret, self.modulus)
        random_coefficients = [
            self.rng.randrange(self.modulus) for _ in range(self.degree)
        ]
        return [constant, *random_coefficients]

    def share(self, secret: int) -> "Sharing":
        """Create one share for every configured participant."""

        polynomial = self.sample_polynomial(secret)
        shares = tuple(
            Share(x, evaluate(polynomial, x, self.modulus))
            for x in self.participant_ids
        )
        return Sharing(self, shares, self.degree)

    def reconstruct_field_element(
        self,
        shares: Iterable[Share],
        degree_bound: int | None = None,
    ) -> int:
        """Reconstruct the constant term from enough explicitly labelled shares."""

        selected = self.validate_shares(shares)
        bound = self.degree if degree_bound is None else degree_bound
        required = bound + 1
        if len(selected) < required:
            raise ValueError(
                f"need at least {required} shares for degree bound {bound}; "
                f"received {len(selected)}"
            )
        points = [(share.x, share.y) for share in selected[:required]]

        # Redundant shares let us detect inconsistency.  With exactly
        # ``required`` shares no such check is possible: those shares always
        # define some polynomial of the permitted degree.
        for share in selected[required:]:
            expected = interpolate(points, share.x, self.modulus)
            if expected != share.y:
                raise ValueError("the supplied shares are not mutually consistent")

        return interpolate(points, 0, self.modulus)

    def reconstruct(
        self,
        shares: Iterable[Share],
        degree_bound: int | None = None,
    ) -> int:
        """Reconstruct and decode the secret as a centered integer."""

        value = self.reconstruct_field_element(shares, degree_bound)
        return decode_signed(value, self.modulus)

    def validate_shares(self, shares: Iterable[Share]) -> list[Share]:
        """Validate labels and return shares sorted by participant identifier."""

        selected = list(shares)
        if not selected:
            raise ValueError("at least one share is required")
        if any(not isinstance(share, Share) for share in selected):
            raise TypeError("every item must be a Share")

        x_values = [share.x % self.modulus for share in selected]
        if len(set(x_values)) != len(x_values):
            raise ValueError("duplicate participant identifiers are not allowed")
        if any(x not in self.participant_ids for x in x_values):
            raise ValueError("a share has an unknown participant identifier")

        return sorted(
            (Share(share.x % self.modulus, share.y % self.modulus) for share in selected),
            key=lambda share: share.x,
        )


@dataclass(frozen=True)
class Sharing:
    """A shared field element and its current polynomial degree bound."""

    scheme: ShamirScheme
    shares: tuple[Share, ...]
    degree_bound: int

    @property
    def reconstruction_threshold(self) -> int:
        return self.degree_bound + 1

    def subset(self, participant_ids: Sequence[int]) -> tuple[Share, ...]:
        """Select shares by their explicit participant identifiers."""

        wanted = set(participant_ids)
        selected = tuple(share for share in self.shares if share.x in wanted)
        if len(selected) != len(wanted):
            raise ValueError("one or more participant identifiers were not found")
        return selected

    def reveal_field_element(self, shares: Iterable[Share] | None = None) -> int:
        selected = self.shares if shares is None else shares
        return self.scheme.reconstruct_field_element(selected, self.degree_bound)

    def reveal(self, shares: Iterable[Share] | None = None) -> int:
        selected = self.shares if shares is None else shares
        return self.scheme.reconstruct(selected, self.degree_bound)

    def _check_compatible(self, other: "Sharing") -> None:
        same_parameters = (
            self.scheme.modulus == other.scheme.modulus
            and self.scheme.participant_ids == other.scheme.participant_ids
        )
        if not same_parameters:
            raise ValueError("the two sharings use incompatible schemes")
        if tuple(share.x for share in self.shares) != tuple(
            share.x for share in other.shares
        ):
            raise ValueError("the two sharings do not contain the same participants")

    def __add__(self, other: "Sharing") -> "Sharing":
        self._check_compatible(other)
        values = tuple(
            Share(left.x, (left.y + right.y) % self.scheme.modulus)
            for left, right in zip(self.shares, other.shares)
        )
        return Sharing(self.scheme, values, max(self.degree_bound, other.degree_bound))

    def __sub__(self, other: "Sharing") -> "Sharing":
        self._check_compatible(other)
        values = tuple(
            Share(left.x, (left.y - right.y) % self.scheme.modulus)
            for left, right in zip(self.shares, other.shares)
        )
        return Sharing(self.scheme, values, max(self.degree_bound, other.degree_bound))

    def scale(self, public_scalar: int) -> "Sharing":
        """Multiply every share by a public scalar without increasing degree."""

        values = tuple(
            Share(share.x, public_scalar * share.y % self.scheme.modulus)
            for share in self.shares
        )
        return Sharing(self.scheme, values, self.degree_bound)

    def add_public(self, public_value: int) -> "Sharing":
        """Add a public constant to the shared polynomial."""

        encoded = public_value % self.scheme.modulus
        values = tuple(
            Share(share.x, (share.y + encoded) % self.scheme.modulus)
            for share in self.shares
        )
        return Sharing(self.scheme, values, self.degree_bound)

    def pointwise_multiply(self, other: "Sharing") -> "Sharing":
        """Multiply corresponding shares and record the resulting degree growth.

        This is mathematically correct, but it is not a complete MPC
        multiplication protocol.  If the inputs have degree ``d``, the product
        may have degree ``2d`` and therefore needs ``2d + 1`` shares to open.
        """

        self._check_compatible(other)
        new_degree = self.degree_bound + other.degree_bound
        values = tuple(
            Share(left.x, left.y * right.y % self.scheme.modulus)
            for left, right in zip(self.shares, other.shares)
        )
        return Sharing(self.scheme, values, new_degree)

    def __mul__(self, other: "Sharing") -> "Sharing":
        return self.pointwise_multiply(other)

    def __repr__(self) -> str:
        return (
            "Sharing("
            f"num_shares={len(self.shares)}, "
            f"degree_bound={self.degree_bound}, "
            f"modulus={self.scheme.modulus})"
        )


def demo() -> None:
    """Run the corrected five-out-of-ten example directly."""

    scheme = ShamirScheme(41, 10, 5, rng=random.Random(2))
    sharing = scheme.share(17)
    chosen = sharing.shares[:5]
    print("Secret: 17")
    print("Polynomial degree:", sharing.degree_bound)
    print("Reconstruction threshold:", sharing.reconstruction_threshold)
    print("First five labelled shares:", chosen)
    print("Reconstructed secret:", sharing.reveal(chosen))


if __name__ == "__main__":
    demo()
