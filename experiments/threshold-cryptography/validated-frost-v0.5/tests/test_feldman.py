import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.feldman import (
    FeldmanCommitments,
    FeldmanParameters,
    FeldmanVSS,
)
from cryptocave_sss.shamir import Share


class FeldmanVSSTests(unittest.TestCase):
    def setUp(self):
        self.vss = FeldmanVSS.educational(rng=random.Random(600))
        self.distribution = self.vss.share(17)

    def test_educational_group_has_order_41(self):
        parameters = self.vss.parameters
        self.assertEqual(parameters.group_modulus, 83)
        self.assertEqual(parameters.scalar_modulus, 41)
        self.assertEqual(pow(parameters.generator, 41, 83), 1)
        self.assertNotEqual(parameters.generator, 1)

    def test_invalid_group_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            FeldmanParameters(81, 41, 4)
        with self.assertRaises(ValueError):
            FeldmanParameters(83, 41, 1)
        with self.assertRaises(ValueError):
            FeldmanParameters(83, 41, 2)

    def test_every_honest_share_verifies(self):
        report = self.vss.verify_shares(
            self.distribution.sharing.shares,
            self.distribution.commitments,
        )
        self.assertTrue(report.all_accepted)
        self.assertEqual(len(report.accepted), 5)
        self.assertEqual(report.rejected, ())

    def test_every_threshold_subset_verifies_and_reconstructs(self):
        subsets = 0
        for subset in combinations(self.distribution.sharing.shares, 3):
            result = self.vss.reconstruct_verified(
                subset,
                self.distribution.commitments,
            )
            self.assertEqual(result.secret, 17)
            self.assertTrue(result.report.all_accepted)
            subsets += 1
        self.assertEqual(subsets, 10)

    def test_every_possible_secret_round_trips(self):
        vss = FeldmanVSS.educational(rng=random.Random(601))
        for secret in range(41):
            distribution = vss.share(secret)
            expected = secret if secret <= 20 else secret - 41
            for subset in combinations(distribution.sharing.shares, 3):
                result = vss.reconstruct_verified(
                    subset,
                    distribution.commitments,
                )
                self.assertEqual(result.secret, expected)

    def test_changed_share_is_rejected(self):
        for share in self.distribution.sharing.shares:
            for change in range(1, 41):
                changed = Share(share.x, (share.y + change) % 41)
                result = self.vss.verify_share(
                    changed,
                    self.distribution.commitments,
                )
                self.assertFalse(result.accepted)

    def test_unknown_participant_is_rejected(self):
        share = self.distribution.sharing.shares[0]
        changed_id = Share(6, share.y)
        result = self.vss.verify_share(changed_id, self.distribution.commitments)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "unknown participant identifier")

    def test_changed_commitment_is_detected(self):
        for position in range(3):
            for change in range(1, 41):
                commitments = list(self.distribution.commitments.values)
                commitments[position] = (
                    commitments[position]
                    * self.vss.parameters.commit(change)
                ) % self.vss.parameters.group_modulus
                changed = FeldmanCommitments(
                    self.vss.parameters,
                    tuple(commitments),
                )

                report = self.vss.verify_shares(
                    self.distribution.sharing.shares,
                    changed,
                )
                self.assertFalse(report.all_accepted)
                self.assertEqual(len(report.rejected), 5)

    def test_wrong_commitment_count_is_rejected(self):
        shortened = FeldmanCommitments(
            self.vss.parameters,
            self.distribution.commitments.values[:-1],
        )
        result = self.vss.verify_share(
            self.distribution.sharing.shares[0],
            shortened,
        )
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "wrong commitment count")

    def test_reconstructs_from_valid_shares_and_reports_bad_share(self):
        received = list(self.distribution.sharing.shares)
        received[1] = Share(received[1].x, (received[1].y + 7) % 41)
        result = self.vss.reconstruct_verified(
            received,
            self.distribution.commitments,
        )
        self.assertEqual(result.secret, 17)
        self.assertEqual(len(result.report.accepted), 4)
        self.assertEqual([share.x for share in result.report.rejected], [2])

    def test_strict_mode_rejects_any_invalid_share(self):
        received = list(self.distribution.sharing.shares)
        received[1] = Share(received[1].x, (received[1].y + 7) % 41)
        with self.assertRaises(ValueError):
            self.vss.reconstruct_verified(
                received,
                self.distribution.commitments,
                require_all_valid=True,
            )

    def test_not_enough_verified_shares_fails(self):
        received = list(self.distribution.sharing.shares[:3])
        received[1] = Share(received[1].x, (received[1].y + 7) % 41)
        with self.assertRaises(ValueError):
            self.vss.reconstruct_verified(
                received,
                self.distribution.commitments,
            )

    def test_duplicate_participant_ids_are_rejected(self):
        first = self.distribution.sharing.shares[0]
        with self.assertRaises(ValueError):
            self.vss.verify_shares(
                [first, first],
                self.distribution.commitments,
            )

    def test_constant_commitment_reveals_secret_equality(self):
        left = FeldmanVSS.educational(rng=random.Random(602)).share(9)
        right = FeldmanVSS.educational(rng=random.Random(603)).share(9)
        other = FeldmanVSS.educational(rng=random.Random(604)).share(10)

        self.assertEqual(
            left.commitments.public_secret_commitment,
            right.commitments.public_secret_commitment,
        )
        self.assertNotEqual(
            left.commitments.public_secret_commitment,
            other.commitments.public_secret_commitment,
        )


if __name__ == "__main__":
    unittest.main()
