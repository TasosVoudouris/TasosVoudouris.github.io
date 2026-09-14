"""A readable educational implementation of Pedersen VSS.

Pedersen commitments add a random blinding polynomial to Feldman's basic
coefficient-commitment idea.  A participant receives two private values:

* ``value = f(x)`` from the secret polynomial; and
* ``blinding = r(x)`` from an independent random polynomial.

The participant checks both values against public commitments.  The tiny
default group makes the arithmetic easy to inspect, but it is not secure.
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

if __package__:
    from .field import is_prime
    from .polynomial import evaluate
    from .shamir import RandomSource, Share, ShamirScheme
else:
    from field import is_prime
    from polynomial import evaluate
    from shamir import RandomSource, Share, ShamirScheme


@dataclass(frozen=True)
class PedersenParameters:
    """Public parameters for commitments ``g^value * h^blinding``.

    Both generators must have prime order ``scalar_modulus``.  Binding relies
    on no participant knowing ``log_g(h)``.  That requirement cannot be secure
    in this deliberately tiny demonstration group, where discrete logarithms
    can be found by exhaustive search.
    """

    group_modulus: int
    scalar_modulus: int
    value_generator: int
    blinding_generator: int

    def __post_init__(self) -> None:
        if not is_prime(self.group_modulus):
            raise ValueError("group_modulus must be prime")
        if not is_prime(self.scalar_modulus):
            raise ValueError("scalar_modulus must be prime")
        if (self.group_modulus - 1) % self.scalar_modulus != 0:
            raise ValueError("scalar_modulus must divide group_modulus - 1")

        g = self.value_generator % self.group_modulus
        h = self.blinding_generator % self.group_modulus
        for name, generator in (("value_generator", g), ("blinding_generator", h)):
            if generator in (0, 1):
                raise ValueError(f"{name} must be a non-identity group element")
            if pow(generator, self.scalar_modulus, self.group_modulus) != 1:
                raise ValueError(f"{name} is not in the requested subgroup")
        if g == h:
            raise ValueError("the two generators must be distinct")

        # Since q is prime, every non-identity element whose q-th power is one
        # has order exactly q.
        object.__setattr__(self, "value_generator", g)
        object.__setattr__(self, "blinding_generator", h)

    @classmethod
    def educational(cls) -> "PedersenParameters":
        """Return two generators of the order-41 subgroup modulo 83."""

        return cls(
            group_modulus=83,
            scalar_modulus=41,
            value_generator=4,
            blinding_generator=59,
        )

    def commit(self, value: int, blinding: int) -> int:
        """Compute a Pedersen commitment to one scalar pair."""

        q = self.scalar_modulus
        p = self.group_modulus
        return (
            pow(self.value_generator, value % q, p)
            * pow(self.blinding_generator, blinding % q, p)
            % p
        )

    def is_subgroup_element(self, element: int) -> bool:
        """Return whether ``element`` lies in the commitment subgroup."""

        element %= self.group_modulus
        return (
            element != 0
            and pow(element, self.scalar_modulus, self.group_modulus) == 1
        )


@dataclass(frozen=True, order=True)
class PedersenShare:
    """One private share pair labelled by participant identifier ``x``."""

    x: int
    value: int
    blinding: int

    def secret_component(self) -> Share:
        """Return the Shamir component used during reconstruction."""

        return Share(self.x, self.value)


@dataclass(frozen=True)
class PedersenCommitments:
    """Public coefficient commitments ``C_j = g^a_j h^b_j``."""

    parameters: PedersenParameters
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("at least one coefficient commitment is required")
        normalised = tuple(
            value % self.parameters.group_modulus for value in self.values
        )
        if not all(
            self.parameters.is_subgroup_element(value) for value in normalised
        ):
            raise ValueError("every commitment must be a valid subgroup element")
        object.__setattr__(self, "values", normalised)

    @property
    def degree_bound(self) -> int:
        return len(self.values) - 1

    @property
    def blinded_secret_commitment(self) -> int:
        """Return ``C_0 = g^secret h^b_0``."""

        return self.values[0]

    def expected_share_commitment(self, participant_id: int) -> int:
        """Compute ``product(C_j^(x^j))`` for participant ``x``."""

        q = self.parameters.scalar_modulus
        p = self.parameters.group_modulus
        x = participant_id % q
        result = 1
        for degree, commitment in enumerate(self.values):
            exponent = pow(x, degree, q)
            result = result * pow(commitment, exponent, p) % p
        return result


@dataclass(frozen=True)
class PedersenShareVerification:
    """The verification result for one private share pair."""

    share: PedersenShare
    accepted: bool
    reason: str


@dataclass(frozen=True)
class PedersenVerificationReport:
    """Accepted and rejected Pedersen shares under one commitment vector."""

    results: tuple[PedersenShareVerification, ...]

    @property
    def accepted(self) -> tuple[PedersenShare, ...]:
        return tuple(result.share for result in self.results if result.accepted)

    @property
    def rejected(self) -> tuple[PedersenShare, ...]:
        return tuple(result.share for result in self.results if not result.accepted)

    @property
    def all_accepted(self) -> bool:
        return all(result.accepted for result in self.results)


@dataclass(frozen=True)
class PedersenVerifiedReconstruction:
    """A reconstructed secret and the preceding verification report."""

    secret: int
    report: PedersenVerificationReport


@dataclass(frozen=True)
class PedersenDistribution:
    """Private share pairs and their one public commitment vector."""

    scheme: ShamirScheme
    shares: tuple[PedersenShare, ...]
    commitments: PedersenCommitments

    def __post_init__(self) -> None:
        if self.scheme.modulus != self.commitments.parameters.scalar_modulus:
            raise ValueError("Shamir field and commitment subgroup order must match")
        if self.scheme.degree != self.commitments.degree_bound:
            raise ValueError("sharing and commitment degree bounds must match")
        if tuple(share.x for share in self.shares) != self.scheme.participant_ids:
            raise ValueError("distribution must contain one ordered share per participant")

    def subset(self, participant_ids: Sequence[int]) -> tuple[PedersenShare, ...]:
        """Select private share pairs by participant identifier."""

        wanted = set(participant_ids)
        selected = tuple(share for share in self.shares if share.x in wanted)
        if len(selected) != len(wanted):
            raise ValueError("one or more participant identifiers were not found")
        return selected


class PedersenVSS:
    """Pedersen verification layered on the Version 0.1 Shamir scheme."""

    def __init__(
        self,
        shamir: ShamirScheme,
        parameters: PedersenParameters,
    ) -> None:
        if shamir.modulus != parameters.scalar_modulus:
            raise ValueError(
                "the Shamir modulus must equal the commitment subgroup order"
            )
        self.shamir = shamir
        self.parameters = parameters

    @classmethod
    def educational(
        cls,
        num_parties: int = 5,
        threshold: int = 3,
        rng: RandomSource | None = None,
    ) -> "PedersenVSS":
        """Construct the directly inspectable Version 0.3 parameter set."""

        parameters = PedersenParameters.educational()
        shamir = ShamirScheme(
            modulus=parameters.scalar_modulus,
            num_parties=num_parties,
            threshold=threshold,
            rng=rng,
        )
        return cls(shamir, parameters)

    def share(self, secret: int) -> PedersenDistribution:
        """Create secret and blinding polynomials, shares, and commitments."""

        secret_coefficients = self.shamir.sample_polynomial(secret)
        blinding_coefficients = [
            self.shamir.rng.randrange(self.shamir.modulus)
            for _ in range(self.shamir.threshold)
        ]

        return self.share_from_coefficients(
            secret_coefficients,
            blinding_coefficients,
        )

    def share_from_coefficients(
        self,
        secret_coefficients: Sequence[int],
        blinding_coefficients: Sequence[int],
    ) -> PedersenDistribution:
        """Distribute two explicit coefficient vectors.

        Version 0.4 uses this small extension for its DKG lesson: each simulated
        dealer samples its own random contribution polynomial, constructs both
        commitment layers, and then discards the coefficients.  Ordinary users
        should normally call :meth:`share` instead.
        """

        if len(secret_coefficients) != self.shamir.threshold:
            raise ValueError("secret polynomial must contain threshold coefficients")
        if len(blinding_coefficients) != self.shamir.threshold:
            raise ValueError("blinding polynomial must contain threshold coefficients")

        secret_coefficients = tuple(
            coefficient % self.shamir.modulus
            for coefficient in secret_coefficients
        )
        blinding_coefficients = tuple(
            coefficient % self.shamir.modulus
            for coefficient in blinding_coefficients
        )

        shares = tuple(
            PedersenShare(
                x=x,
                value=evaluate(secret_coefficients, x, self.shamir.modulus),
                blinding=evaluate(blinding_coefficients, x, self.shamir.modulus),
            )
            for x in self.shamir.participant_ids
        )
        commitments = PedersenCommitments(
            self.parameters,
            tuple(
                self.parameters.commit(value, blinding)
                for value, blinding in zip(
                    secret_coefficients,
                    blinding_coefficients,
                )
            ),
        )
        return PedersenDistribution(self.shamir, shares, commitments)

    def verify_share(
        self,
        share: PedersenShare,
        commitments: PedersenCommitments,
    ) -> PedersenShareVerification:
        """Verify both private components against the public commitments."""

        if commitments.parameters != self.parameters:
            return PedersenShareVerification(
                share,
                False,
                "wrong commitment parameters",
            )
        if commitments.degree_bound != self.shamir.degree:
            return PedersenShareVerification(share, False, "wrong commitment count")
        if share.x % self.shamir.modulus not in self.shamir.participant_ids:
            return PedersenShareVerification(
                share,
                False,
                "unknown participant identifier",
            )

        left = self.parameters.commit(share.value, share.blinding)
        right = commitments.expected_share_commitment(share.x)
        if left == right:
            return PedersenShareVerification(
                share,
                True,
                "share pair matches commitments",
            )
        return PedersenShareVerification(
            share,
            False,
            "share pair does not match commitments",
        )

    def verify_shares(
        self,
        shares: Iterable[PedersenShare],
        commitments: PedersenCommitments,
    ) -> PedersenVerificationReport:
        """Verify several shares and reject duplicate participant labels."""

        selected = list(shares)
        if not selected:
            raise ValueError("at least one share is required")
        if any(not isinstance(share, PedersenShare) for share in selected):
            raise TypeError("every item must be a PedersenShare")

        identifiers = [share.x % self.shamir.modulus for share in selected]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("duplicate participant identifiers are not allowed")

        return PedersenVerificationReport(
            tuple(self.verify_share(share, commitments) for share in selected)
        )

    def reconstruct_verified(
        self,
        shares: Iterable[PedersenShare],
        commitments: PedersenCommitments,
        require_all_valid: bool = False,
    ) -> PedersenVerifiedReconstruction:
        """Verify share pairs and reconstruct from accepted secret components."""

        report = self.verify_shares(shares, commitments)
        if require_all_valid and not report.all_accepted:
            raise ValueError("one or more shares failed Pedersen verification")
        if len(report.accepted) < self.shamir.threshold:
            raise ValueError("not enough verified shares to reconstruct")

        secret = self.shamir.reconstruct(
            share.secret_component() for share in report.accepted
        )
        return PedersenVerifiedReconstruction(secret, report)


def demo() -> None:
    """Run an honest Pedersen distribution and a tampering attempt."""

    vss = PedersenVSS.educational(rng=random.Random(30))
    distribution = vss.share(17)

    print("Secret: 17")
    print("Public blinded commitments:", distribution.commitments.values)
    for share in distribution.shares:
        result = vss.verify_share(share, distribution.commitments)
        print(f"participant {share.x}: accepted={result.accepted}")

    first = distribution.shares[0]
    changed = PedersenShare(first.x, first.value + 1, first.blinding)
    result = vss.verify_share(changed, distribution.commitments)
    print("Changed first value accepted?", result.accepted)

    reconstructed = vss.reconstruct_verified(
        distribution.shares[:3],
        distribution.commitments,
    )
    print("Reconstructed from three verified shares:", reconstructed.secret)


if __name__ == "__main__":
    demo()
