import random
import sys
import unittest
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.pedersen import (
    PedersenCommitments,
    PedersenShare,
    PedersenVSS,
)
from cryptocave_sss.vss_session import (
    BroadcastEquivocationError,
    Complaint,
    ParticipantStatus,
    ReliableCommitmentBoard,
    SessionState,
    VSSSession,
)


class VSSSessionTests(unittest.TestCase):
    def setUp(self):
        self.vss = PedersenVSS.educational(rng=random.Random(800))
        self.distribution = self.vss.share(17)

    def make_session(self, session_id="session-001"):
        session = VSSSession(self.vss, session_id=session_id, dealer_id="alice")
        session.broadcast_commitments(self.distribution.commitments)
        session.distribute_shares(list(self.distribution.shares))
        return session

    def test_honest_session_qualifies_and_reconstructs(self):
        session = self.make_session()
        results = session.verify_all()
        self.assertTrue(all(result.accepted for result in results))
        self.assertEqual(session.state, SessionState.VERIFIED)
        self.assertEqual(session.finalize(), SessionState.QUALIFIED)
        self.assertEqual(session.reconstruct([1, 3, 5]).secret, 17)

    def test_bad_share_opens_complaint_and_valid_response_resolves_it(self):
        session = VSSSession(self.vss, session_id="session-repair")
        session.broadcast_commitments(self.distribution.commitments)
        received = list(self.distribution.shares)
        honest = received[1]
        received[1] = PedersenShare(
            honest.x,
            honest.value + 1,
            honest.blinding,
        )
        session.distribute_shares(received)

        session.verify_all()
        self.assertEqual(session.state, SessionState.COMPLAINTS_OPEN)
        self.assertEqual(session.statuses[2], ParticipantStatus.COMPLAINED)
        self.assertIn(2, session.active_complaints)

        response = session.dealer_respond(2, honest)
        self.assertTrue(response.accepted)
        self.assertEqual(session.statuses[2], ParticipantStatus.RESOLVED)
        self.assertEqual(session.state, SessionState.VERIFIED)
        self.assertEqual(session.finalize(), SessionState.QUALIFIED)
        self.assertEqual(session.reconstruct([2, 3, 4]).secret, 17)

    def test_invalid_response_leaves_complaint_open(self):
        session = self.make_session("session-invalid-response")
        honest = session.received_shares[1]
        session.received_shares[1] = PedersenShare(
            1,
            honest.value + 1,
            honest.blinding,
        )
        session.verify_all()

        invalid = PedersenShare(1, honest.value + 2, honest.blinding)
        response = session.dealer_respond(1, invalid)
        self.assertFalse(response.accepted)
        self.assertEqual(session.state, SessionState.COMPLAINTS_OPEN)
        self.assertEqual(session.statuses[1], ParticipantStatus.COMPLAINED)

    def test_unresolved_complaint_aborts(self):
        session = self.make_session("session-abort")
        honest = session.received_shares[3]
        session.received_shares[3] = PedersenShare(
            3,
            honest.value,
            honest.blinding + 1,
        )
        session.verify_all()
        self.assertEqual(session.finalize(), SessionState.ABORTED)
        with self.assertRaises(ValueError):
            session.reconstruct([1, 2, 3])

    def test_commitment_rebroadcast_is_idempotent(self):
        session = VSSSession(self.vss, session_id="session-repeat")
        first = session.broadcast_commitments(self.distribution.commitments)
        second = session.broadcast_commitments(self.distribution.commitments)
        self.assertEqual(first, second)
        self.assertEqual(session.state, SessionState.COMMITMENTS_BROADCAST)

    def test_commitment_equivocation_aborts(self):
        session = VSSSession(self.vss, session_id="session-equivocation")
        session.broadcast_commitments(self.distribution.commitments)
        values = list(self.distribution.commitments.values)
        values[0] = (
            values[0]
            * self.vss.parameters.commit(1, 0)
            % self.vss.parameters.group_modulus
        )
        different = PedersenCommitments(self.vss.parameters, tuple(values))

        with self.assertRaises(BroadcastEquivocationError):
            session.broadcast_commitments(different)
        self.assertEqual(session.state, SessionState.ABORTED)

    def test_shared_board_detects_equivocation_between_local_views(self):
        board = ReliableCommitmentBoard()
        first = VSSSession(
            self.vss,
            session_id="same-session",
            dealer_id="alice",
            board=board,
        )
        second = VSSSession(
            self.vss,
            session_id="same-session",
            dealer_id="alice",
            board=board,
        )
        first.broadcast_commitments(self.distribution.commitments)

        values = list(self.distribution.commitments.values)
        values[-1] = (
            values[-1]
            * self.vss.parameters.commit(1, 0)
            % self.vss.parameters.group_modulus
        )
        different = PedersenCommitments(self.vss.parameters, tuple(values))
        with self.assertRaises(BroadcastEquivocationError):
            second.broadcast_commitments(different)

    def test_transcript_digest_binds_session_and_commitments(self):
        left = VSSSession(self.vss, session_id="left")
        right = VSSSession(self.vss, session_id="right")
        left_digest = left.broadcast_commitments(self.distribution.commitments).digest
        right_digest = right.broadcast_commitments(self.distribution.commitments).digest
        self.assertNotEqual(left_digest, right_digest)

        other_distribution = PedersenVSS.educational(
            rng=random.Random(801)
        ).share(17)
        other = VSSSession(self.vss, session_id="left")
        other_digest = other.broadcast_commitments(
            other_distribution.commitments
        ).digest
        self.assertNotEqual(left_digest, other_digest)

    def test_replayed_complaint_from_another_session_is_rejected(self):
        source = self.make_session("source-session")
        honest = source.received_shares[1]
        source.received_shares[1] = PedersenShare(
            1,
            honest.value + 1,
            honest.blinding,
        )
        source.verify_all()
        complaint = source.complaint_log[0]

        target = self.make_session("target-session")
        target_honest = target.received_shares[1]
        target.received_shares[1] = PedersenShare(
            1,
            target_honest.value + 1,
            target_honest.blinding,
        )
        with self.assertRaises(ValueError):
            target.submit_complaint(complaint)

    def test_false_local_complaint_is_rejected(self):
        session = self.make_session("false-complaint")
        complaint = Complaint(
            session_id=session.session_id,
            participant_id=1,
            transcript_digest=session.transcript.digest,
            reason="share pair does not match commitments",
        )
        with self.assertRaises(ValueError):
            session.submit_complaint(complaint)

    def test_incomplete_or_out_of_order_operations_fail(self):
        session = VSSSession(self.vss, session_id="wrong-order")
        with self.assertRaises(ValueError):
            session.distribute_shares(list(self.distribution.shares))
        with self.assertRaises(ValueError):
            session.verify_all()
        session.broadcast_commitments(self.distribution.commitments)
        session.distribute_shares(list(self.distribution.shares))
        with self.assertRaises(ValueError):
            session.finalize()
        with self.assertRaises(ValueError):
            session.reconstruct([1, 2, 3])

    def test_distribution_requires_exact_participant_set(self):
        session = VSSSession(self.vss, session_id="missing-share")
        session.broadcast_commitments(self.distribution.commitments)
        with self.assertRaises(ValueError):
            session.distribute_shares(list(self.distribution.shares[:-1]))
        with self.assertRaises(ValueError):
            session.distribute_shares(
                [self.distribution.shares[0], *self.distribution.shares]
            )

    def test_public_record_contains_no_private_share_fields(self):
        session = self.make_session("public-record")
        session.verify_all()
        session.finalize()
        record = session.public_record()
        self.assertEqual(record["state"], "qualified")
        self.assertNotIn("received_shares", record)
        self.assertNotIn("secret", record)
        self.assertNotIn("blinding", record)


if __name__ == "__main__":
    unittest.main()
