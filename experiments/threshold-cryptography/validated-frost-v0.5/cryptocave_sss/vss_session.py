"""An offline protocol-state model for one Pedersen VSS session.

This module teaches the order of a VSS exchange: publish one commitment
vector, deliver private shares, verify, complain, answer, and qualify or abort.
It is intentionally not a network protocol and does not provide transport
authentication, reliable broadcast, signatures, persistence, or concurrency.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from enum import Enum

if __package__:
    from .pedersen import (
        PedersenCommitments,
        PedersenShare,
        PedersenShareVerification,
        PedersenVSS,
        PedersenVerifiedReconstruction,
    )
else:
    from pedersen import (
        PedersenCommitments,
        PedersenShare,
        PedersenShareVerification,
        PedersenVSS,
        PedersenVerifiedReconstruction,
    )


def _digest(public_object: object) -> str:
    """Hash a canonical JSON representation for transcript binding."""

    encoded = json.dumps(
        public_object,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class SessionState(str, Enum):
    CREATED = "created"
    COMMITMENTS_BROADCAST = "commitments-broadcast"
    SHARES_DISTRIBUTED = "shares-distributed"
    COMPLAINTS_OPEN = "complaints-open"
    VERIFIED = "verified"
    QUALIFIED = "qualified"
    ABORTED = "aborted"


class ParticipantStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLAINED = "complained"
    RESOLVED = "resolved"


class BroadcastEquivocationError(ValueError):
    """Raised when a dealer publishes two commitment vectors for one session."""


@dataclass(frozen=True)
class SessionTranscript:
    """The public values that identify and bind one educational session."""

    protocol: str
    version: str
    session_id: str
    dealer_id: str
    participant_ids: tuple[int, ...]
    threshold: int
    group_modulus: int
    scalar_modulus: int
    value_generator: int
    blinding_generator: int
    commitments: tuple[int, ...]

    def as_public_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "session_id": self.session_id,
            "dealer_id": self.dealer_id,
            "participant_ids": list(self.participant_ids),
            "threshold": self.threshold,
            "group_modulus": self.group_modulus,
            "scalar_modulus": self.scalar_modulus,
            "value_generator": self.value_generator,
            "blinding_generator": self.blinding_generator,
            "commitments": list(self.commitments),
        }

    @property
    def digest(self) -> str:
        """Return the SHA-256 identifier for this exact public transcript."""

        return _digest(self.as_public_dict())


@dataclass(frozen=True)
class Complaint:
    """A public complaint reference that does not contain the private share."""

    session_id: str
    participant_id: int
    transcript_digest: str
    reason: str

    @property
    def complaint_id(self) -> str:
        return _digest(
            {
                "session_id": self.session_id,
                "participant_id": self.participant_id,
                "transcript_digest": self.transcript_digest,
                "reason": self.reason,
            }
        )


@dataclass(frozen=True)
class DealerResponse:
    """The local result of privately replacing one complained-about share."""

    session_id: str
    participant_id: int
    transcript_digest: str
    accepted: bool
    reason: str


class ReliableCommitmentBoard:
    """A tiny in-memory model of consistent commitment broadcast.

    It records the first vector under ``(session_id, dealer_id)``.  Publishing
    the same vector again is idempotent; publishing a different vector raises
    an equivocation error.  Real reliable broadcast is a distributed protocol,
    not this dictionary.
    """

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], PedersenCommitments] = {}

    def publish(
        self,
        session_id: str,
        dealer_id: str,
        commitments: PedersenCommitments,
    ) -> PedersenCommitments:
        key = (session_id, dealer_id)
        previous = self._records.get(key)
        if previous is None:
            self._records[key] = commitments
            return commitments
        if previous != commitments:
            raise BroadcastEquivocationError(
                "dealer published different commitments for the same session"
            )
        return previous


class VSSSession:
    """A simple, single-process state machine for one Pedersen VSS exchange."""

    def __init__(
        self,
        vss: PedersenVSS,
        session_id: str,
        dealer_id: str = "dealer",
        board: ReliableCommitmentBoard | None = None,
    ) -> None:
        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if not dealer_id.strip():
            raise ValueError("dealer_id must not be empty")

        self.vss = vss
        self.session_id = session_id
        self.dealer_id = dealer_id
        self.board = board if board is not None else ReliableCommitmentBoard()
        self.state = SessionState.CREATED
        self.transcript: SessionTranscript | None = None
        self.commitments: PedersenCommitments | None = None
        self.received_shares: dict[int, PedersenShare] = {}
        self.statuses = {
            participant_id: ParticipantStatus.PENDING
            for participant_id in self.vss.shamir.participant_ids
        }
        self.active_complaints: dict[int, Complaint] = {}
        self.complaint_log: list[Complaint] = []
        self.responses: list[DealerResponse] = []

    def _require_not_finished(self) -> None:
        if self.state in (SessionState.QUALIFIED, SessionState.ABORTED):
            raise ValueError(f"session is already {self.state.value}")

    def broadcast_commitments(
        self,
        commitments: PedersenCommitments,
    ) -> SessionTranscript:
        """Record one common public commitment vector for the session."""

        self._require_not_finished()
        if self.state not in (
            SessionState.CREATED,
            SessionState.COMMITMENTS_BROADCAST,
        ):
            raise ValueError("commitments must be broadcast before private shares")
        if commitments.parameters != self.vss.parameters:
            raise ValueError("wrong commitment parameters")
        if commitments.degree_bound != self.vss.shamir.degree:
            raise ValueError("wrong commitment count")

        try:
            common = self.board.publish(
                self.session_id,
                self.dealer_id,
                commitments,
            )
        except BroadcastEquivocationError:
            self.state = SessionState.ABORTED
            raise

        parameters = self.vss.parameters
        transcript = SessionTranscript(
            protocol="CryptoCave-Pedersen-VSS",
            version="0.3",
            session_id=self.session_id,
            dealer_id=self.dealer_id,
            participant_ids=self.vss.shamir.participant_ids,
            threshold=self.vss.shamir.threshold,
            group_modulus=parameters.group_modulus,
            scalar_modulus=parameters.scalar_modulus,
            value_generator=parameters.value_generator,
            blinding_generator=parameters.blinding_generator,
            commitments=common.values,
        )
        self.commitments = common
        self.transcript = transcript
        self.state = SessionState.COMMITMENTS_BROADCAST
        return transcript

    def distribute_shares(self, shares: tuple[PedersenShare, ...] | list[PedersenShare]) -> None:
        """Deliver exactly one private share pair to each local participant."""

        self._require_not_finished()
        if self.state != SessionState.COMMITMENTS_BROADCAST:
            raise ValueError("broadcast commitments before distributing shares")
        if any(not isinstance(share, PedersenShare) for share in shares):
            raise TypeError("every item must be a PedersenShare")

        received = {share.x: share for share in shares}
        if len(received) != len(shares):
            raise ValueError("duplicate participant identifiers are not allowed")
        expected = set(self.vss.shamir.participant_ids)
        if set(received) != expected:
            raise ValueError("provide exactly one share for every participant")

        self.received_shares = received
        self.statuses = {
            participant_id: ParticipantStatus.PENDING
            for participant_id in self.vss.shamir.participant_ids
        }
        self.state = SessionState.SHARES_DISTRIBUTED

    def _require_verification_context(self) -> tuple[PedersenCommitments, SessionTranscript]:
        if self.commitments is None or self.transcript is None:
            raise ValueError("the public transcript has not been created")
        if self.state not in (
            SessionState.SHARES_DISTRIBUTED,
            SessionState.COMPLAINTS_OPEN,
        ):
            raise ValueError("shares are not ready for participant verification")
        return self.commitments, self.transcript

    def verify_participant(self, participant_id: int) -> PedersenShareVerification:
        """Verify one received share and open a complaint when it fails."""

        commitments, transcript = self._require_verification_context()
        if participant_id not in self.statuses:
            raise ValueError("unknown participant identifier")

        share = self.received_shares[participant_id]
        result = self.vss.verify_share(share, commitments)
        if result.accepted:
            self.statuses[participant_id] = ParticipantStatus.ACCEPTED
            self.active_complaints.pop(participant_id, None)
        else:
            complaint = Complaint(
                session_id=self.session_id,
                participant_id=participant_id,
                transcript_digest=transcript.digest,
                reason=result.reason,
            )
            if participant_id not in self.active_complaints:
                self.complaint_log.append(complaint)
            self.active_complaints[participant_id] = complaint
            self.statuses[participant_id] = ParticipantStatus.COMPLAINED

        self._refresh_verification_state()
        return result

    def verify_all(self) -> tuple[PedersenShareVerification, ...]:
        """Run every participant's local verification step."""

        self._require_verification_context()
        results = tuple(
            self.verify_participant(participant_id)
            for participant_id in self.vss.shamir.participant_ids
        )
        return results

    def _refresh_verification_state(self) -> None:
        if self.active_complaints:
            self.state = SessionState.COMPLAINTS_OPEN
        elif any(status == ParticipantStatus.PENDING for status in self.statuses.values()):
            self.state = SessionState.SHARES_DISTRIBUTED
        else:
            self.state = SessionState.VERIFIED

    def submit_complaint(self, complaint: Complaint) -> None:
        """Validate and record an externally constructed complaint reference."""

        commitments, transcript = self._require_verification_context()
        if complaint.session_id != self.session_id:
            raise ValueError("complaint belongs to a different session")
        if complaint.transcript_digest != transcript.digest:
            raise ValueError("complaint is bound to a different transcript")
        if complaint.participant_id not in self.statuses:
            raise ValueError("complaint names an unknown participant")

        share = self.received_shares[complaint.participant_id]
        result = self.vss.verify_share(share, commitments)
        if result.accepted:
            raise ValueError("an honest share does not justify this local complaint")
        if complaint.reason != result.reason:
            raise ValueError("complaint reason does not match local verification")

        if complaint.participant_id not in self.active_complaints:
            self.complaint_log.append(complaint)
        self.active_complaints[complaint.participant_id] = complaint
        self.statuses[complaint.participant_id] = ParticipantStatus.COMPLAINED
        self.state = SessionState.COMPLAINTS_OPEN

    def dealer_respond(
        self,
        participant_id: int,
        corrected_share: PedersenShare,
    ) -> DealerResponse:
        """Privately replace one disputed share and verify the replacement."""

        if self.state != SessionState.COMPLAINTS_OPEN:
            raise ValueError("there is no open complaint phase")
        if participant_id not in self.active_complaints:
            raise ValueError("participant has no active complaint")
        if corrected_share.x != participant_id:
            raise ValueError("corrected share has the wrong participant identifier")
        if self.commitments is None or self.transcript is None:
            raise ValueError("the public transcript has not been created")

        verification = self.vss.verify_share(corrected_share, self.commitments)
        response = DealerResponse(
            session_id=self.session_id,
            participant_id=participant_id,
            transcript_digest=self.transcript.digest,
            accepted=verification.accepted,
            reason=verification.reason,
        )
        self.responses.append(response)

        if verification.accepted:
            self.received_shares[participant_id] = corrected_share
            self.statuses[participant_id] = ParticipantStatus.RESOLVED
            del self.active_complaints[participant_id]
        self._refresh_verification_state()
        return response

    def finalize(self) -> SessionState:
        """Qualify an entirely verified dealer or abort on unresolved complaints."""

        if self.state == SessionState.VERIFIED:
            self.state = SessionState.QUALIFIED
            return self.state
        if self.state == SessionState.COMPLAINTS_OPEN:
            self.state = SessionState.ABORTED
            return self.state
        if self.state in (SessionState.QUALIFIED, SessionState.ABORTED):
            return self.state
        raise ValueError("verify every participant before finalizing the session")

    def reconstruct(
        self,
        participant_ids: tuple[int, ...] | list[int],
    ) -> PedersenVerifiedReconstruction:
        """Reconstruct only after qualification and only from verified shares."""

        if self.state != SessionState.QUALIFIED:
            raise ValueError("session must be qualified before reconstruction")
        if self.commitments is None:
            raise ValueError("commitments are unavailable")

        try:
            shares = tuple(self.received_shares[identifier] for identifier in participant_ids)
        except KeyError as error:
            raise ValueError("unknown participant identifier") from error
        return self.vss.reconstruct_verified(
            shares,
            self.commitments,
            require_all_valid=True,
        )

    def public_record(self) -> dict[str, object]:
        """Return public audit data without any secret or blinding share."""

        return {
            "session_id": self.session_id,
            "dealer_id": self.dealer_id,
            "state": self.state.value,
            "transcript_digest": self.transcript.digest if self.transcript else None,
            "participant_statuses": {
                str(identifier): status.value
                for identifier, status in self.statuses.items()
            },
            "complaint_ids": [complaint.complaint_id for complaint in self.complaint_log],
            "responses": [
                {
                    "participant_id": response.participant_id,
                    "accepted": response.accepted,
                    "reason": response.reason,
                }
                for response in self.responses
            ],
        }


def demo() -> None:
    """Run one complete honest session."""

    vss = PedersenVSS.educational(rng=random.Random(40))
    distribution = vss.share(17)
    session = VSSSession(vss, session_id="lesson-001")

    transcript = session.broadcast_commitments(distribution.commitments)
    session.distribute_shares(list(distribution.shares))
    session.verify_all()
    session.finalize()
    opened = session.reconstruct([1, 2, 3])

    print("Transcript digest:", transcript.digest)
    print("Final state:", session.state.value)
    print("Reconstructed secret:", opened.secret)


if __name__ == "__main__":
    demo()
