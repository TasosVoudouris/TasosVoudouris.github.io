"""Packed ramp secret sharing, reconstructed from the original ``fft.py``."""

from __future__ import annotations

import secrets
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

if __package__:
    from .field import decode_signed, require_prime
    from .polynomial import (
        evaluate,
        interpolate,
        interpolate_coefficients,
        matrix_rank,
    )
    from .shamir import Share
else:
    from field import decode_signed, require_prime
    from polynomial import evaluate, interpolate, interpolate_coefficients, matrix_rank
    from shamir import Share


class RandomSource(Protocol):
    def randrange(self, stop: int) -> int: ...


class PackedRampScheme:
    """Pack several secrets into evaluations of one random polynomial.

    One public anchor, ``k`` secret evaluations, and ``t`` random evaluations
    define a polynomial of degree at most ``k+t``.  Any ``k+t`` output shares,
    together with the public anchor, reconstruct all packed secrets.  Any at
    most ``t`` output shares reveal no information about them.
    """

    def __init__(
        self,
        modulus: int,
        secret_points: Sequence[int],
        randomness_points: Sequence[int],
        share_points: Sequence[int],
        anchor_point: int,
        rng: RandomSource | None = None,
    ) -> None:
        require_prime(modulus)
        if not secret_points:
            raise ValueError("at least one secret point is required")
        if not randomness_points:
            raise ValueError("at least one randomness point is required")

        all_points = [
            anchor_point,
            *secret_points,
            *randomness_points,
            *share_points,
        ]
        normalised = [point % modulus for point in all_points]
        if len(set(normalised)) != len(normalised):
            raise ValueError("anchor, secret, randomness, and share points must be distinct")

        self.modulus = modulus
        self.anchor_point = anchor_point % modulus
        self.secret_points = tuple(point % modulus for point in secret_points)
        self.randomness_points = tuple(
            point % modulus for point in randomness_points
        )
        self.share_points = tuple(point % modulus for point in share_points)
        self.num_secrets = len(self.secret_points)
        self.privacy_threshold = len(self.randomness_points)
        self.degree_bound = self.num_secrets + self.privacy_threshold
        self.reconstruction_threshold = self.degree_bound
        self.rng = rng if rng is not None else secrets.SystemRandom()

        if len(self.share_points) < self.reconstruction_threshold:
            raise ValueError("not enough share points for reconstruction")

    @classmethod
    def original_parameters(
        cls, rng: RandomSource | None = None
    ) -> "PackedRampScheme":
        """Return the exact algebraic point layout used in ``legacy/fft.py``."""

        modulus = 433
        omega_2 = 354  # primitive eighth root of unity
        omega_3 = 150  # primitive ninth root of unity
        return cls(
            modulus=modulus,
            anchor_point=1,
            secret_points=[pow(omega_2, exponent, modulus) for exponent in range(1, 4)],
            randomness_points=[
                pow(omega_2, exponent, modulus) for exponent in range(4, 8)
            ],
            share_points=[
                pow(omega_3, exponent, modulus) for exponent in range(1, 9)
            ],
            rng=rng,
        )

    def share(self, secrets_to_share: Sequence[int]) -> "PackedSharing":
        """Pack exactly ``num_secrets`` values into one sharing."""

        if len(secrets_to_share) != self.num_secrets:
            raise ValueError(f"expected exactly {self.num_secrets} secrets")

        random_values = [
            self.rng.randrange(self.modulus)
            for _ in range(self.privacy_threshold)
        ]
        constraints = [(self.anchor_point, 0)]
        constraints += [
            (point, value % self.modulus)
            for point, value in zip(self.secret_points, secrets_to_share)
        ]
        constraints += list(zip(self.randomness_points, random_values))

        polynomial = interpolate_coefficients(constraints, self.modulus)
        shares = tuple(
            Share(point, evaluate(polynomial, point, self.modulus))
            for point in self.share_points
        )
        return PackedSharing(self, shares)

    def reconstruct_field_elements(self, shares: Iterable[Share]) -> list[int]:
        """Reconstruct all secrets from any sufficient valid share subset."""

        selected = self._validate_shares(shares)
        required = self.reconstruction_threshold
        if len(selected) < required:
            raise ValueError(
                f"need at least {required} packed shares; received {len(selected)}"
            )

        basis = [Share(self.anchor_point, 0), *selected[:required]]
        points = [(share.x, share.y) for share in basis]

        # An eighth share is redundant for the original parameters, so use it
        # as a consistency check instead of silently ignoring it.
        for share in selected[required:]:
            if interpolate(points, share.x, self.modulus) != share.y:
                raise ValueError("the supplied packed shares are inconsistent")

        return [
            interpolate(points, point, self.modulus) for point in self.secret_points
        ]

    def reconstruct(self, shares: Iterable[Share]) -> list[int]:
        """Reconstruct packed values using centered integer decoding."""

        return [
            decode_signed(value, self.modulus)
            for value in self.reconstruct_field_elements(shares)
        ]

    def coalition_leakage_dimension(self, share_ids: Sequence[int]) -> int:
        """Return how many independent field relations the coalition learns.

        Zero means perfect privacy for that coalition.  For the original
        parameters, coalition sizes 4, 5, 6, and 7 reveal respectively 0, 1, 2,
        and 3 independent relations about the three packed secrets.
        """

        selected_ids = [identifier % self.modulus for identifier in share_ids]
        if len(set(selected_ids)) != len(selected_ids):
            raise ValueError("coalition identifiers must be distinct")
        if any(identifier not in self.share_points for identifier in selected_ids):
            raise ValueError("coalition contains an unknown share identifier")

        constraint_points = [
            self.anchor_point,
            *self.secret_points,
            *self.randomness_points,
        ]
        rows: list[list[int]] = []
        for share_id in selected_ids:
            # Each output share is a linear combination of the constraint values.
            row = [
                interpolate(
                    [
                        (point, 1 if index == column else 0)
                        for index, point in enumerate(constraint_points)
                    ],
                    share_id,
                    self.modulus,
                )
                for column in range(len(constraint_points))
            ]
            rows.append(row)

        # Drop the public anchor column.  Split remaining columns into secrets
        # and random masks.  Observed secret information is rank([S|R])-rank(R).
        secret_start = 1
        random_start = 1 + self.num_secrets
        full = [row[secret_start:] for row in rows]
        masks = [row[random_start:] for row in rows]
        return matrix_rank(full, self.modulus) - matrix_rank(masks, self.modulus)

    def _validate_shares(self, shares: Iterable[Share]) -> list[Share]:
        selected = list(shares)
        if not selected:
            raise ValueError("at least one packed share is required")
        if any(not isinstance(share, Share) for share in selected):
            raise TypeError("every item must be a Share")
        ids = [share.x % self.modulus for share in selected]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate packed-share identifiers are not allowed")
        if any(identifier not in self.share_points for identifier in ids):
            raise ValueError("a packed share has an unknown identifier")
        return sorted(
            (Share(share.x % self.modulus, share.y % self.modulus) for share in selected),
            key=lambda share: share.x,
        )


@dataclass(frozen=True)
class PackedSharing:
    scheme: PackedRampScheme
    shares: tuple[Share, ...]

    def subset(self, share_ids: Sequence[int]) -> tuple[Share, ...]:
        wanted = set(share_ids)
        selected = tuple(share for share in self.shares if share.x in wanted)
        if len(selected) != len(wanted):
            raise ValueError("one or more packed-share identifiers were not found")
        return selected

    def reveal(self, shares: Iterable[Share] | None = None) -> list[int]:
        selected = self.shares if shares is None else shares
        return self.scheme.reconstruct(selected)


def demo() -> None:
    """Run the corrected three-secret ramp-sharing example."""

    scheme = PackedRampScheme.original_parameters(random.Random(5))
    sharing = scheme.share([10, 20, 30])
    print("Packed secrets: [10, 20, 30]")
    print("Output shares:", sharing.shares)
    print("Privacy threshold:", scheme.privacy_threshold)
    print("Reconstruction threshold:", scheme.reconstruction_threshold)
    print("Recovered from seven shares:", sharing.reveal(sharing.shares[:7]))


if __name__ == "__main__":
    demo()
