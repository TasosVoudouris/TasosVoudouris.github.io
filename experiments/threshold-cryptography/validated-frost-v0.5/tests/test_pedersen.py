import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.field import inverse
from cryptocave_sss.pedersen import (
    PedersenCommitments,
    PedersenParameters,
    PedersenShare,
    PedersenVSS,
)


class PedersenVSSTests(unittest.TestCase):
    def setUp(self):
        self.vss = PedersenVSS.educational(rng=random.Random(700))
        self.distribution = self.vss.share(17)

    def test_educational_generators_have_order_41(self):
        parameters = self.vss.parameters
        self.assertEqual(parameters.group_modulus, 83)
        self.assertEqual(parameters.scalar_modulus, 41)
        self.assertEqual(pow(parameters.value_generator, 41, 83), 1)
        self.assertEqual(pow(parameters.blinding_generator, 41, 83), 1)
        self.assertNotEqual(parameters.value_generator, parameters.blinding_generator)

    def test_invalid_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            PedersenParameters(81, 41, 4, 59)
        with self.assertRaises(ValueError):
            PedersenParameters(83, 41, 1, 59)
        with self.assertRaises(ValueError):
            PedersenParameters(83, 41, 4, 1)
        with self.assertRaises(ValueError):
            PedersenParameters(83, 41, 4, 4)
        with self.assertRaises(ValueError):
            PedersenParameters(83, 41, 4, 2)

    def test_every_honest_share_verifies(self):
        report = self.vss.verify_shares(
            self.distribution.shares,
            self.distribution.commitments,
        )
        self.assertTrue(report.all_accepted)
        self.assertEqual(len(report.accepted), 5)
        self.assertEqual(report.rejected, ())

    def test_every_threshold_subset_verifies_and_reconstructs(self):
        subsets = 0
        for subset in combinations(self.distribution.shares, 3):
            result = self.vss.reconstruct_verified(
                subset,
                self.distribution.commitments,
            )
            self.assertEqual(result.secret, 17)
            self.assertTrue(result.report.all_accepted)
            subsets += 1
        self.assertEqual(subsets, 10)

    def test_every_field_secret_round_trips_for_every_threshold_subset(self):
        vss = PedersenVSS.educational(rng=random.Random(701))
        for secret in range(41):
            distribution = vss.share(secret)
            expected = secret if secret <= 20 else secret - 41
            for subset in combinations(distribution.shares, 3):
                result = vss.reconstruct_verified(
                    subset,
                    distribution.commitments,
                )
                self.assertEqual(result.secret, expected)

    def test_changing_only_secret_component_is_rejected(self):
        for share in self.distribution.shares:
            for change in range(1, 41):
                changed = PedersenShare(
                    share.x,
                    (share.value + change) % 41,
                    share.blinding,
                )
                result = self.vss.verify_share(
                    changed,
                    self.distribution.commitments,
                )
                self.assertFalse(result.accepted)

    def test_changing_only_blinding_component_is_rejected(self):
        for share in self.distribution.shares:
            for change in range(1, 41):
                changed = PedersenShare(
                    share.x,
                    share.value,
                    (share.blinding + change) % 41,
                )
                result = self.vss.verify_share(
                    changed,
                    self.distribution.commitments,
                )
                self.assertFalse(result.accepted)

    def test_unknown_participant_is_rejected(self):
        share = self.distribution.shares[0]
        changed = PedersenShare(6, share.value, share.blinding)
        result = self.vss.verify_share(changed, self.distribution.commitments)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "unknown participant identifier")

    def test_wrong_commitment_count_is_rejected(self):
        shortened = PedersenCommitments(
            self.vss.parameters,
            self.distribution.commitments.values[:-1],
        )
        result = self.vss.verify_share(self.distribution.shares[0], shortened)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "wrong commitment count")

    def test_changed_commitment_is_detected(self):
        values = list(self.distribution.commitments.values)
        values[1] = (
            values[1]
            * self.vss.parameters.commit(1, 0)
            % self.vss.parameters.group_modulus
        )
        changed = PedersenCommitments(self.vss.parameters, tuple(values))
        report = self.vss.verify_shares(self.distribution.shares, changed)
        self.assertFalse(report.all_accepted)

    def test_reconstruct_uses_verified_secret_components_only(self):
        received = list(self.distribution.shares)
        share = received[1]
        received[1] = PedersenShare(share.x, share.value + 1, share.blinding)
        result = self.vss.reconstruct_verified(
            received,
            self.distribution.commitments,
        )
        self.assertEqual(result.secret, 17)
        self.assertEqual(len(result.report.accepted), 4)
        self.assertEqual([share.x for share in result.report.rejected], [2])

    def test_strict_mode_rejects_any_invalid_share(self):
        received = list(self.distribution.shares)
        share = received[1]
        received[1] = PedersenShare(share.x, share.value + 1, share.blinding)
        with self.assertRaises(ValueError):
            self.vss.reconstruct_verified(
                received,
                self.distribution.commitments,
                require_all_valid=True,
            )

    def test_not_enough_verified_shares_fails(self):
        received = list(self.distribution.shares[:3])
        share = received[1]
        received[1] = PedersenShare(share.x, share.value + 1, share.blinding)
        with self.assertRaises(ValueError):
            self.vss.reconstruct_verified(received, self.distribution.commitments)

    def test_duplicate_participant_ids_are_rejected(self):
        first = self.distribution.shares[0]
        with self.assertRaises(ValueError):
            self.vss.verify_shares([first, first], self.distribution.commitments)

    def test_commitment_is_perfectly_hiding_in_the_mathematical_group(self):
        parameters = self.vss.parameters
        for secret in (0, 1, 17, 40):
            possible = {
                parameters.commit(secret, blinding)
                for blinding in range(parameters.scalar_modulus)
            }
            self.assertEqual(len(possible), parameters.scalar_modulus)

        left = {parameters.commit(3, b) for b in range(41)}
        right = {parameters.commit(29, b) for b in range(41)}
        self.assertEqual(left, right)

    def test_tiny_known_generator_relation_breaks_binding(self):
        # In the educational group h = g^17.  Anyone who learns this relation
        # can change both openings without changing the commitment.  Real
        # parameters must be generated so no participant knows log_g(h).
        parameters = self.vss.parameters
        relation = 17
        self.assertEqual(
            parameters.blinding_generator,
            pow(parameters.value_generator, relation, parameters.group_modulus),
        )
        value, blinding = 9, 12
        changed_value = value + 1
        changed_blinding = blinding - inverse(relation, 41)
        self.assertEqual(
            parameters.commit(value, blinding),
            parameters.commit(changed_value, changed_blinding),
        )

    def test_explicit_polynomials_support_the_dkg_lesson(self):
        vss = PedersenVSS.educational(rng=random.Random(702))
        distribution = vss.share_from_coefficients(
            [17, 2, 3],
            [5, 7, 11],
        )
        self.assertTrue(
            vss.verify_shares(
                distribution.shares,
                distribution.commitments,
            ).all_accepted
        )
        self.assertEqual(
            vss.reconstruct_verified(
                distribution.shares[:3],
                distribution.commitments,
            ).secret,
            17,
        )

    def test_explicit_polynomials_require_threshold_coefficients(self):
        vss = PedersenVSS.educational(rng=random.Random(703))
        with self.assertRaises(ValueError):
            vss.share_from_coefficients([17, 2], [5, 7, 11])
        with self.assertRaises(ValueError):
            vss.share_from_coefficients([17, 2, 3], [5, 7])


if __name__ == "__main__":
    unittest.main()
