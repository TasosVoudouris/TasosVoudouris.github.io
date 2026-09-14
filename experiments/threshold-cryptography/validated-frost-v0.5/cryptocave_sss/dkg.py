"""A small offline multi-dealer DKG simulator for Version 0.4.

Every participant contributes a random Shamir polynomial.  The contribution is
first qualified through the Version 0.3 Pedersen VSS session, then checked
against a Feldman-style value commitment vector for the same polynomial.  Only
dealers in one common qualified set are aggregated.

The module teaches DKG data flow and failure states.  It is not an implementation
of the proven GJKR protocol, reliable broadcast, or production key generation.
"""

from __future__ import annotations

import hashlib
import json
import random
import secrets
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum

if __package__:
    from .feldman import FeldmanCommitments, FeldmanParameters, FeldmanVSS
    from .pedersen import (
        PedersenCommitments,
        PedersenDistribution,
        PedersenParameters,
        PedersenShare,
        PedersenVSS,
    )
    from .shamir import RandomSource, Share, ShamirScheme
    from .vss_session import (
        ReliableCommitmentBoard,
        SessionState,
        VSSSession,
    )
else:
    from feldman import FeldmanCommitments, FeldmanParameters, FeldmanVSS
    from pedersen import (
        PedersenCommitments,
        PedersenDistribution,
        PedersenParameters,
        PedersenShare,
        PedersenVSS,
    )
    from shamir import RandomSource, Share, ShamirScheme
    from vss_session import ReliableCommitmentBoard, SessionState, VSSSession


def _digest(public_object: object) -> str:
    """Hash canonical public transcript data."""

    encoded = json.dumps(
        public_object,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class DKGState(str, Enum):
    CREATED = "created"
    VSS_ROUND = "vss-round"
    EXTRACTION_ROUND = "extraction-round"
    QUALIFICATION = "qualification"
    COMPLETE = "complete"
    ABORTED = "aborted"


class DKGAbortError(ValueError):
    """Raised when the educational DKG cannot produce a common result."""


class QualificationDisagreementError(DKGAbortError):
    """Raised when participant views of the qualified set differ."""


@dataclass(frozen=True)
class DKGDealerCommitments:
    """The two public commitment vectors for one dealer polynomial."""

    pedersen: PedersenCommitments
    value: FeldmanCommitments

    def __post_init__(self) -> None:
        pedersen_parameters = self.pedersen.parameters
        value_parameters = self.value.parameters
        same_group = (
            pedersen_parameters.group_modulus == value_parameters.group_modulus
            and pedersen_parameters.scalar_modulus
            == value_parameters.scalar_modulus
            and pedersen_parameters.value_generator
            == value_parameters.generator
        )
        if not same_group:
            raise ValueError("Pedersen and value commitments use different groups")
        if self.pedersen.degree_bound != self.value.degree_bound:
            raise ValueError("dealer commitment vectors have different degrees")

    @property
    def public_key_contribution(self) -> int:
        """Return ``g^z_i`` for this dealer's random constant ``z_i``."""

        return self.value.public_secret_commitment


@dataclass(frozen=True)
class DKGDealerPackage:
    """One dealer's private deliveries and staged public commitments."""

    dealer_id: int
    distribution: PedersenDistribution
    commitments: DKGDealerCommitments

    def __post_init__(self) -> None:
        if self.distribution.commitments != self.commitments.pedersen:
            raise ValueError("distribution and Pedersen commitments do not match")
        if self.distribution.scheme.degree != self.commitments.value.degree_bound:
            raise ValueError("distribution and value commitments have different degrees")


@dataclass(frozen=True)
class DealerOutcome:
    """Public qualification result for one dealer."""

    dealer_id: int
    vss_state: SessionState
    pedersen_qualified: bool
    value_commitments_accepted: bool
    qualified: bool
    reason: str
    vss_transcript_digest: str | None


@dataclass(frozen=True, order=True)
class DKGParticipantShare:
    """One participant's aggregate secret and blinding key shares."""

    participant_id: int
    secret_share: int
    blinding_share: int
    source_dealers: tuple[int, ...]

    def pedersen_component(self) -> PedersenShare:
        return PedersenShare(
            self.participant_id,
            self.secret_share,
            self.blinding_share,
        )

    def secret_component(self) -> Share:
        return Share(self.participant_id, self.secret_share)


@dataclass(frozen=True)
class DKGShareVerification:
    """Verification under both aggregate commitment vectors."""

    share: DKGParticipantShare
    pedersen_accepted: bool
    value_accepted: bool
    accepted: bool
    reason: str


@dataclass(frozen=True)
class DKGDealerRecord:
    """Public transcript entry for one dealer."""

    dealer_id: int
    vss_transcript_digest: str | None
    pedersen_commitments: tuple[int, ...]
    value_commitments: tuple[int, ...]
    qualified: bool
    reason: str

    def as_public_dict(self) -> dict[str, object]:
        return {
            "dealer_id": self.dealer_id,
            "vss_transcript_digest": self.vss_transcript_digest,
            "pedersen_commitments": list(self.pedersen_commitments),
            "value_commitments": list(self.value_commitments),
            "qualified": self.qualified,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DKGTranscript:
    """Canonical public output of the complete offline DKG simulation."""

    protocol: str
    version: str
    session_id: str
    participant_ids: tuple[int, ...]
    threshold: int
    minimum_qualified_dealers: int
    qualified_dealers: tuple[int, ...]
    dealer_records: tuple[DKGDealerRecord, ...]
    aggregate_pedersen_commitments: tuple[int, ...]
    aggregate_value_commitments: tuple[int, ...]
    public_key: int

    def as_public_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "session_id": self.session_id,
            "participant_ids": list(self.participant_ids),
            "threshold": self.threshold,
            "minimum_qualified_dealers": self.minimum_qualified_dealers,
            "qualified_dealers": list(self.qualified_dealers),
            "dealer_records": [
                record.as_public_dict() for record in self.dealer_records
            ],
            "aggregate_pedersen_commitments": list(
                self.aggregate_pedersen_commitments
            ),
            "aggregate_value_commitments": list(
                self.aggregate_value_commitments
            ),
            "public_key": self.public_key,
        }

    @property
    def digest(self) -> str:
        return _digest(self.as_public_dict())


@dataclass(frozen=True)
class DKGResult:
    """Distributed key shares, public key, and their public audit transcript."""

    shamir: ShamirScheme
    pedersen_parameters: PedersenParameters
    value_parameters: FeldmanParameters
    qualified_dealers: tuple[int, ...]
    participant_shares: tuple[DKGParticipantShare, ...]
    pedersen_commitments: PedersenCommitments
    value_commitments: FeldmanCommitments
    public_key: int
    transcript: DKGTranscript

    def __post_init__(self) -> None:
        if self.public_key != self.value_commitments.public_secret_commitment:
            raise ValueError("public key must equal the aggregate constant commitment")
        if self.qualified_dealers != self.transcript.qualified_dealers:
            raise ValueError("result and transcript qualified sets differ")
        if self.public_key != self.transcript.public_key:
            raise ValueError("result and transcript public keys differ")
        if (
            self.pedersen_commitments.values
            != self.transcript.aggregate_pedersen_commitments
        ):
            raise ValueError("result and transcript Pedersen vectors differ")
        if (
            self.value_commitments.values
            != self.transcript.aggregate_value_commitments
        ):
            raise ValueError("result and transcript value vectors differ")
        if tuple(
            share.participant_id for share in self.participant_shares
        ) != self.shamir.participant_ids:
            raise ValueError("result must contain one ordered share per participant")

    def share_for(self, participant_id: int) -> DKGParticipantShare:
        """Return one participant's final key share."""

        for share in self.participant_shares:
            if share.participant_id == participant_id:
                return share
        raise ValueError("unknown participant identifier")

    def verify_share(self, share: DKGParticipantShare) -> DKGShareVerification:
        """Verify one final share under both aggregate commitment vectors."""

        pedersen = PedersenVSS(self.shamir, self.pedersen_parameters)
        feldman = FeldmanVSS(self.shamir, self.value_parameters)
        pedersen_result = pedersen.verify_share(
            share.pedersen_component(),
            self.pedersen_commitments,
        )
        value_result = feldman.verify_share(
            share.secret_component(),
            self.value_commitments,
        )
        sources_accepted = share.source_dealers == self.qualified_dealers
        accepted = (
            pedersen_result.accepted
            and value_result.accepted
            and sources_accepted
        )
        if not sources_accepted:
            reason = "aggregate share is bound to a different qualified set"
        elif accepted:
            reason = "aggregate share matches both commitment vectors"
        elif not pedersen_result.accepted and not value_result.accepted:
            reason = "aggregate share fails both commitment vectors"
        elif not pedersen_result.accepted:
            reason = "aggregate share fails Pedersen verification"
        else:
            reason = "aggregate secret component fails value verification"
        return DKGShareVerification(
            share,
            pedersen_result.accepted,
            value_result.accepted,
            accepted,
            reason,
        )

    def verify_all(self) -> tuple[DKGShareVerification, ...]:
        return tuple(self.verify_share(share) for share in self.participant_shares)

    def audit_reconstruct_field_element(
        self,
        participant_ids: Sequence[int],
    ) -> int:
        """Reconstruct only for a teaching audit, never for normal DKG use."""

        selected = [self.share_for(identifier) for identifier in participant_ids]
        if not all(self.verify_share(share).accepted for share in selected):
            raise ValueError("audit selection contains an invalid key share")
        return self.shamir.reconstruct_field_element(
            share.secret_component() for share in selected
        )

    def audit_public_key_matches(self, participant_ids: Sequence[int]) -> bool:
        """Check ``public_key == g^x`` after explicit audit reconstruction."""

        secret = self.audit_reconstruct_field_element(participant_ids)
        return self.value_parameters.commit(secret) == self.public_key


class MultiDealerDKG:
    """Coordinate several Version 0.3 VSS sessions in one local process."""

    def __init__(
        self,
        shamir: ShamirScheme,
        pedersen_parameters: PedersenParameters,
        session_id: str,
        minimum_qualified_dealers: int | None = None,
    ) -> None:
        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if shamir.modulus != pedersen_parameters.scalar_modulus:
            raise ValueError("Shamir and Pedersen scalar fields must match")

        minimum = (
            shamir.threshold
            if minimum_qualified_dealers is None
            else minimum_qualified_dealers
        )
        if not 1 <= minimum <= shamir.num_parties:
            raise ValueError("minimum qualified dealers must be between 1 and n")

        self.shamir = shamir
        self.pedersen_parameters = pedersen_parameters
        self.value_parameters = FeldmanParameters(
            group_modulus=pedersen_parameters.group_modulus,
            scalar_modulus=pedersen_parameters.scalar_modulus,
            generator=pedersen_parameters.value_generator,
        )
        self.session_id = session_id
        self.minimum_qualified_dealers = minimum
        self.board = ReliableCommitmentBoard()
        self.state = DKGState.CREATED
        self.dealer_sessions: dict[int, VSSSession] = {}
        self.outcomes: tuple[DealerOutcome, ...] = ()
        self.computed_qualified_dealers: tuple[int, ...] = ()
        self.qualification_views: dict[int, tuple[int, ...]] = {}

    @classmethod
    def educational(
        cls,
        session_id: str = "dkg-lesson-001",
        num_parties: int = 5,
        threshold: int = 3,
        minimum_qualified_dealers: int | None = None,
    ) -> "MultiDealerDKG":
        parameters = PedersenParameters.educational()
        shamir = ShamirScheme(
            modulus=parameters.scalar_modulus,
            num_parties=num_parties,
            threshold=threshold,
        )
        return cls(
            shamir,
            parameters,
            session_id,
            minimum_qualified_dealers,
        )

    def create_dealer_package(
        self,
        dealer_id: int,
        rng: RandomSource | None = None,
    ) -> DKGDealerPackage:
        """Sample one independent random dealer contribution."""

        if dealer_id not in self.shamir.participant_ids:
            raise ValueError("dealer must be a configured participant")
        source = rng if rng is not None else secrets.SystemRandom()
        q = self.shamir.modulus
        secret_coefficients = [
            source.randrange(q) for _ in range(self.shamir.threshold)
        ]
        blinding_coefficients = [
            source.randrange(q) for _ in range(self.shamir.threshold)
        ]

        dealer_shamir = ShamirScheme(
            modulus=q,
            num_parties=self.shamir.num_parties,
            threshold=self.shamir.threshold,
            participant_ids=self.shamir.participant_ids,
            # The explicit coefficients have already been sampled.  Retaining a
            # deterministic teaching generator inside the returned scheme would
            # unnecessarily retain its state.
            rng=secrets.SystemRandom(),
        )
        pedersen = PedersenVSS(dealer_shamir, self.pedersen_parameters)
        distribution = pedersen.share_from_coefficients(
            secret_coefficients,
            blinding_coefficients,
        )
        value_commitments = FeldmanCommitments(
            self.value_parameters,
            tuple(
                self.value_parameters.commit(coefficient)
                for coefficient in secret_coefficients
            ),
        )
        commitments = DKGDealerCommitments(
            distribution.commitments,
            value_commitments,
        )
        return DKGDealerPackage(dealer_id, distribution, commitments)

    def _validate_packages(
        self,
        packages: Iterable[DKGDealerPackage],
    ) -> tuple[DKGDealerPackage, ...]:
        selected = list(packages)
        if any(not isinstance(package, DKGDealerPackage) for package in selected):
            raise TypeError("every item must be a DKGDealerPackage")
        dealer_ids = [package.dealer_id for package in selected]
        if len(set(dealer_ids)) != len(dealer_ids):
            raise ValueError("duplicate dealer identifiers are not allowed")
        if set(dealer_ids) != set(self.shamir.participant_ids):
            raise ValueError("provide exactly one dealer package per participant")

        for package in selected:
            scheme = package.distribution.scheme
            same_scheme = (
                scheme.modulus == self.shamir.modulus
                and scheme.threshold == self.shamir.threshold
                and scheme.participant_ids == self.shamir.participant_ids
            )
            if not same_scheme:
                raise ValueError("dealer package uses incompatible Shamir parameters")
            if package.commitments.pedersen.parameters != self.pedersen_parameters:
                raise ValueError("dealer package uses incompatible Pedersen parameters")
            if package.commitments.value.parameters != self.value_parameters:
                raise ValueError("dealer package uses incompatible value parameters")
        return tuple(sorted(selected, key=lambda package: package.dealer_id))

    def _run_dealer(
        self,
        package: DKGDealerPackage,
        received_shares: Sequence[PedersenShare],
        dealer_responses: Mapping[tuple[int, int], PedersenShare],
        used_responses: set[tuple[int, int]],
    ) -> tuple[DealerOutcome, dict[int, PedersenShare]]:
        vss = PedersenVSS(
            package.distribution.scheme,
            self.pedersen_parameters,
        )
        session = VSSSession(
            vss,
            session_id=f"{self.session_id}/dealer-{package.dealer_id}",
            dealer_id=f"participant-{package.dealer_id}",
            board=self.board,
        )
        self.dealer_sessions[package.dealer_id] = session

        transcript_digest: str | None = None
        try:
            transcript = session.broadcast_commitments(
                package.commitments.pedersen
            )
            transcript_digest = transcript.digest
            session.distribute_shares(list(received_shares))
            session.verify_all()
            for participant_id in tuple(session.active_complaints):
                replacement = dealer_responses.get(
                    (package.dealer_id, participant_id)
                )
                if replacement is not None:
                    session.dealer_respond(participant_id, replacement)
                    used_responses.add((package.dealer_id, participant_id))
            vss_state = session.finalize()
        except ValueError as error:
            session.state = SessionState.ABORTED
            outcome = DealerOutcome(
                package.dealer_id,
                session.state,
                False,
                False,
                False,
                f"Pedersen session failed: {error}",
                transcript_digest,
            )
            return outcome, {}

        if vss_state != SessionState.QUALIFIED:
            outcome = DealerOutcome(
                package.dealer_id,
                vss_state,
                False,
                False,
                False,
                "unresolved Pedersen complaint",
                transcript_digest,
            )
            return outcome, {}

        outcome = DealerOutcome(
            package.dealer_id,
            vss_state,
            True,
            False,
            True,
            "dealer passed hidden qualification; value round is pending",
            transcript_digest,
        )
        return outcome, dict(session.received_shares)

    def _value_commitments_match(
        self,
        package: DKGDealerPackage,
        received_shares: Mapping[int, PedersenShare],
    ) -> bool:
        """Check the public-key extraction vector against qualified shares."""

        feldman = FeldmanVSS(
            package.distribution.scheme,
            self.value_parameters,
        )
        report = feldman.verify_shares(
            (
                Share(share.x, share.value)
                for share in received_shares.values()
            ),
            package.commitments.value,
        )
        return report.all_accepted

    def _agree_qualified_set(
        self,
        computed: tuple[int, ...],
        views: Mapping[int, Sequence[int]] | None,
    ) -> None:
        if views is None:
            normalised = {
                participant_id: computed
                for participant_id in self.shamir.participant_ids
            }
        else:
            if set(views) != set(self.shamir.participant_ids):
                raise QualificationDisagreementError(
                    "qualification views must include every participant"
                )
            normalised = {}
            for participant_id, view in views.items():
                candidate = tuple(sorted(view))
                if len(set(candidate)) != len(candidate):
                    raise QualificationDisagreementError(
                        "a qualification view contains duplicate dealers"
                    )
                if any(
                    dealer_id not in self.shamir.participant_ids
                    for dealer_id in candidate
                ):
                    raise QualificationDisagreementError(
                        "a qualification view contains an unknown dealer"
                    )
                normalised[participant_id] = candidate

        if any(view != computed for view in normalised.values()):
            raise QualificationDisagreementError(
                "participants did not agree on the computed qualified set"
            )
        self.qualification_views = normalised

    def _aggregate(
        self,
        packages: tuple[DKGDealerPackage, ...],
        qualified_shares: Mapping[int, Mapping[int, PedersenShare]],
    ) -> DKGResult:
        q = self.shamir.modulus
        p = self.pedersen_parameters.group_modulus
        qualified = self.computed_qualified_dealers
        package_by_id = {package.dealer_id: package for package in packages}

        participant_shares = tuple(
            DKGParticipantShare(
                participant_id,
                sum(
                    qualified_shares[dealer_id][participant_id].value
                    for dealer_id in qualified
                )
                % q,
                sum(
                    qualified_shares[dealer_id][participant_id].blinding
                    for dealer_id in qualified
                )
                % q,
                qualified,
            )
            for participant_id in self.shamir.participant_ids
        )

        aggregate_pedersen = PedersenCommitments(
            self.pedersen_parameters,
            tuple(
                self._product_mod(
                    (
                        package_by_id[dealer_id].commitments.pedersen.values[index]
                        for dealer_id in qualified
                    ),
                    p,
                )
                for index in range(self.shamir.threshold)
            ),
        )
        aggregate_value = FeldmanCommitments(
            self.value_parameters,
            tuple(
                self._product_mod(
                    (
                        package_by_id[dealer_id].commitments.value.values[index]
                        for dealer_id in qualified
                    ),
                    p,
                )
                for index in range(self.shamir.threshold)
            ),
        )
        public_key = aggregate_value.public_secret_commitment

        outcomes_by_id = {outcome.dealer_id: outcome for outcome in self.outcomes}
        dealer_records = tuple(
            DKGDealerRecord(
                package.dealer_id,
                outcomes_by_id[package.dealer_id].vss_transcript_digest,
                package.commitments.pedersen.values,
                package.commitments.value.values,
                outcomes_by_id[package.dealer_id].qualified,
                outcomes_by_id[package.dealer_id].reason,
            )
            for package in packages
        )
        transcript = DKGTranscript(
            protocol="CryptoCave-Multi-Dealer-DKG",
            version="0.4",
            session_id=self.session_id,
            participant_ids=self.shamir.participant_ids,
            threshold=self.shamir.threshold,
            minimum_qualified_dealers=self.minimum_qualified_dealers,
            qualified_dealers=qualified,
            dealer_records=dealer_records,
            aggregate_pedersen_commitments=aggregate_pedersen.values,
            aggregate_value_commitments=aggregate_value.values,
            public_key=public_key,
        )
        result = DKGResult(
            self.shamir,
            self.pedersen_parameters,
            self.value_parameters,
            qualified,
            participant_shares,
            aggregate_pedersen,
            aggregate_value,
            public_key,
            transcript,
        )
        if not all(verification.accepted for verification in result.verify_all()):
            raise DKGAbortError("internal aggregate-share verification failed")
        return result

    @staticmethod
    def _product_mod(values: Iterable[int], modulus: int) -> int:
        result = 1
        for value in values:
            result = result * value % modulus
        return result

    def run(
        self,
        packages: Iterable[DKGDealerPackage],
        received_overrides: Mapping[int, Sequence[PedersenShare]] | None = None,
        dealer_responses: Mapping[tuple[int, int], PedersenShare] | None = None,
        qualification_views: Mapping[int, Sequence[int]] | None = None,
    ) -> DKGResult:
        """Run qualification, agreement, and aggregation exactly once."""

        if self.state != DKGState.CREATED:
            raise ValueError("a DKG coordinator can be run only once")
        try:
            selected = self._validate_packages(packages)
            overrides = received_overrides or {}
            responses = dealer_responses or {}
            used_responses: set[tuple[int, int]] = set()
            if any(dealer_id not in self.shamir.participant_ids for dealer_id in overrides):
                raise ValueError("received override names an unknown dealer")
            if any(
                dealer_id not in self.shamir.participant_ids
                or participant_id not in self.shamir.participant_ids
                for dealer_id, participant_id in responses
            ):
                raise ValueError("dealer response names an unknown identifier")

            self.state = DKGState.VSS_ROUND
            outcomes: list[DealerOutcome] = []
            qualified_shares: dict[int, dict[int, PedersenShare]] = {}
            for package in selected:
                received = overrides.get(
                    package.dealer_id,
                    package.distribution.shares,
                )
                outcome, final_shares = self._run_dealer(
                    package,
                    received,
                    responses,
                    used_responses,
                )
                outcomes.append(outcome)
                if outcome.qualified:
                    qualified_shares[package.dealer_id] = final_shares

            if set(responses) != used_responses:
                raise ValueError("dealer response has no matching active complaint")

            self.outcomes = tuple(outcomes)
            computed = tuple(
                outcome.dealer_id for outcome in outcomes if outcome.qualified
            )
            self.computed_qualified_dealers = computed
            if len(computed) < self.minimum_qualified_dealers:
                raise DKGAbortError(
                    "too few qualified dealers for the configured policy"
                )

            self.state = DKGState.QUALIFICATION
            self._agree_qualified_set(computed, qualification_views)

            # The qualified set is now fixed.  A failure in the later public-key
            # extraction round must not silently remove a contribution after
            # its hidden Pedersen commitment has been accepted.  The complete
            # GJKR protocol has a public-reconstruction recovery path; this
            # smaller lesson aborts instead.
            self.state = DKGState.EXTRACTION_ROUND
            package_by_id = {
                package.dealer_id: package for package in selected
            }
            final_outcomes = list(outcomes)
            for dealer_id in computed:
                package = package_by_id[dealer_id]
                accepted = self._value_commitments_match(
                    package,
                    qualified_shares[dealer_id],
                )
                position = next(
                    index
                    for index, outcome in enumerate(final_outcomes)
                    if outcome.dealer_id == dealer_id
                )
                if not accepted:
                    final_outcomes[position] = replace(
                        final_outcomes[position],
                        value_commitments_accepted=False,
                        reason=(
                            "qualified dealer failed the public-key "
                            "extraction round"
                        ),
                    )
                    self.outcomes = tuple(final_outcomes)
                    raise DKGAbortError(
                        "a qualified dealer failed public-key extraction"
                    )
                final_outcomes[position] = replace(
                    final_outcomes[position],
                    value_commitments_accepted=True,
                    reason="dealer passed both commitment rounds",
                )

            self.outcomes = tuple(final_outcomes)
            result = self._aggregate(selected, qualified_shares)
            self.state = DKGState.COMPLETE
            return result
        except (TypeError, ValueError):
            self.state = DKGState.ABORTED
            raise


def demo() -> None:
    """Run an honest 3-out-of-5 DKG without reconstructing the secret."""

    dkg = MultiDealerDKG.educational(session_id="dkg-module-demo")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(100 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]
    result = dkg.run(packages)

    print("Qualified dealers:", result.qualified_dealers)
    print("Group public key:", result.public_key)
    print("Transcript digest:", result.transcript.digest)
    print("All final key shares verify:", all(
        verification.accepted for verification in result.verify_all()
    ))
    print("The group secret was not reconstructed during the DKG run.")


if __name__ == "__main__":
    demo()
