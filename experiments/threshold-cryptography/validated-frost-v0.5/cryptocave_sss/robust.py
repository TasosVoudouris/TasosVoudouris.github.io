"""Educational consistency checking and small-scale robust reconstruction."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations
import random

if __package__:
    from .field import decode_signed
    from .polynomial import interpolate
    from .shamir import Share, ShamirScheme
else:
    from field import decode_signed
    from polynomial import interpolate
    from shamir import Share, ShamirScheme


@dataclass(frozen=True)
class RobustResult:
    """Result of bounded-error reconstruction."""

    secret: int
    field_element: int
    supporting_shares: tuple[Share, ...]
    rejected_shares: tuple[Share, ...]


def check_consistency(
    scheme: ShamirScheme,
    shares: Iterable[Share],
    degree_bound: int | None = None,
) -> bool:
    """Check whether all provided shares lie on one bounded-degree polynomial.

    At least one redundant share is needed to detect inconsistency.  With only
    ``degree_bound + 1`` shares, a polynomial always exists.
    """

    selected = scheme.validate_shares(shares)
    bound = scheme.degree if degree_bound is None else degree_bound
    required = bound + 1
    if len(selected) < required:
        raise ValueError(f"need at least {required} shares")

    basis = selected[:required]
    basis_points = [(share.x, share.y) for share in basis]
    return all(
        interpolate(basis_points, share.x, scheme.modulus) == share.y
        for share in selected
    )


def robust_reconstruct(
    scheme: ShamirScheme,
    shares: Iterable[Share],
    max_errors: int,
    degree_bound: int | None = None,
) -> RobustResult:
    """Correct a small bounded number of erroneous shares by subset voting.

    The condition ``n >= k + 2e`` is enforced, where ``k = degree + 1`` and
    ``e`` is ``max_errors``.  This exhaustive implementation is deliberately
    simple and suitable only for small educational examples.  A scalable
    implementation would use a Reed--Solomon decoder such as Berlekamp--Welch.
    """

    if max_errors < 0:
        raise ValueError("max_errors cannot be negative")

    selected = scheme.validate_shares(shares)
    bound = scheme.degree if degree_bound is None else degree_bound
    required = bound + 1
    if len(selected) < required + 2 * max_errors:
        raise ValueError(
            "insufficient redundancy: require n >= degree + 1 + 2*max_errors"
        )

    candidates: dict[tuple[int, tuple[int, ...]], tuple[Share, ...]] = {}

    for basis in combinations(selected, required):
        points = [(share.x, share.y) for share in basis]
        support = tuple(
            share
            for share in selected
            if interpolate(points, share.x, scheme.modulus) == share.y
        )
        if len(support) < len(selected) - max_errors:
            continue

        predictions = tuple(
            interpolate(points, share.x, scheme.modulus) for share in selected
        )
        secret = interpolate(points, 0, scheme.modulus)
        candidates[(secret, predictions)] = support

    if not candidates:
        raise ValueError("shares exceed the requested error bound")

    # Choose the unique polynomial with the greatest number of supporting shares.
    support_sizes = Counter(len(support) for support in candidates.values())
    best_size = max(support_sizes)
    best = [item for item in candidates.items() if len(item[1]) == best_size]
    if len(best) != 1:
        raise ValueError("the supplied shares do not determine a unique result")

    (field_element, _), supporting = best[0]
    supporting_set = set(supporting)
    rejected = tuple(share for share in selected if share not in supporting_set)
    secret = decode_signed(field_element, scheme.modulus)
    return RobustResult(secret, field_element, supporting, rejected)


def demo() -> None:
    """Correct one changed share in a small example."""

    scheme = ShamirScheme(41, 7, 4, rng=random.Random(3))
    sharing = scheme.share(12)
    received = list(sharing.shares)
    received[2] = Share(received[2].x, (received[2].y + 1) % 41)
    result = robust_reconstruct(scheme, received, max_errors=1)
    print("Received shares:", received)
    print("Recovered secret:", result.secret)
    print("Rejected participant IDs:", [share.x for share in result.rejected_shares])


if __name__ == "__main__":
    demo()
