import random
import sys
import unittest
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import (
    DKGAbortError,
    DKGDealerCommitments,
    DKGDealerPackage,
    DKGParticipantShare,
    DKGState,
    MultiDealerDKG,
    QualificationDisagreementError,
)
from cryptocave_sss.feldman import FeldmanCommitments
from cryptocave_sss.field import inverse
from cryptocave_sss.pedersen import PedersenShare
from cryptocave_sss.shamir import ShamirScheme


class MultiDealerDKGTests(unittest.TestCase):
    def make_dkg(self, session_id="dkg-test", minimum=None):
        return MultiDealerDKG.educational(
            session_id=session_id,
            minimum_qualified_dealers=minimum,
        )

    def make_packages(self, dkg, seed_offset=900):
        return [
            dkg.create_dealer_package(
                dealer_id,
                rng=random.Random(seed_offset + dealer_id),
            )
            for dealer_id in dkg.shamir.participant_ids
        ]

    def run_honest(self, session_id="dkg-honest", seed_offset=900):
        dkg = self.make_dkg(session_id)
        packages = self.make_packages(dkg, seed_offset)
        return dkg, packages, dkg.run(packages)

    def test_honest_dkg_completes(self):
        dkg, _, result = self.run_honest()
        self.assertEqual(dkg.state, DKGState.COMPLETE)
        self.assertEqual(result.qualified_dealers, (1, 2, 3, 4, 5))
        self.assertEqual(len(result.participant_shares), 5)
        self.assertEqual(len(result.transcript.digest), 64)

    def test_every_final_key_share_verifies_under_both_vectors(self):
        _, _, result = self.run_honest("dkg-share-check")
        verifications = result.verify_all()
        self.assertEqual(len(verifications), 5)
        self.assertTrue(all(item.pedersen_accepted for item in verifications))
        self.assertTrue(all(item.value_accepted for item in verifications))
        self.assertTrue(all(item.accepted for item in verifications))

    def test_every_threshold_subset_matches_the_public_key_in_audit(self):
        _, _, result = self.run_honest("dkg-audit")
        reconstructed = set()
        for subset in combinations((1, 2, 3, 4, 5), 3):
            secret = result.audit_reconstruct_field_element(subset)
            reconstructed.add(secret)
            self.assertTrue(result.audit_public_key_matches(subset))
        self.assertEqual(len(reconstructed), 1)

    def test_normal_run_never_invokes_shamir_reconstruction(self):
        dkg = self.make_dkg("dkg-no-reconstruct")
        packages = self.make_packages(dkg)
        with patch.object(
            ShamirScheme,
            "reconstruct_field_element",
            side_effect=AssertionError("normal DKG must not reconstruct"),
        ), patch.object(
            ShamirScheme,
            "reconstruct",
            side_effect=AssertionError("normal DKG must not reconstruct"),
        ):
            result = dkg.run(packages)
        self.assertEqual(result.public_key, result.value_commitments.values[0])

    def test_result_and_public_transcript_do_not_expose_group_secret(self):
        _, _, result = self.run_honest("dkg-no-secret-field")
        self.assertFalse(hasattr(result, "secret"))
        public = result.transcript.as_public_dict()
        self.assertNotIn("secret", public)
        self.assertNotIn("participant_shares", public)
        self.assertNotIn("blinding_shares", public)

    def test_public_key_is_product_of_qualified_contributions(self):
        _, packages, result = self.run_honest("dkg-public-product")
        expected = 1
        for package in packages:
            expected = (
                expected
                * package.commitments.public_key_contribution
                % result.value_parameters.group_modulus
            )
        self.assertEqual(result.public_key, expected)

    def test_aggregate_commitments_are_coefficientwise_products(self):
        _, packages, result = self.run_honest("dkg-vector-product")
        p = result.value_parameters.group_modulus
        for index in range(result.shamir.threshold):
            expected_pedersen = 1
            expected_value = 1
            for package in packages:
                expected_pedersen = (
                    expected_pedersen
                    * package.commitments.pedersen.values[index]
                    % p
                )
                expected_value = (
                    expected_value
                    * package.commitments.value.values[index]
                    % p
                )
            self.assertEqual(
                result.pedersen_commitments.values[index],
                expected_pedersen,
            )
            self.assertEqual(
                result.value_commitments.values[index],
                expected_value,
            )

    def test_one_bad_pedersen_delivery_disqualifies_only_its_dealer(self):
        dkg = self.make_dkg("dkg-bad-delivery")
        packages = self.make_packages(dkg)
        received = list(packages[1].distribution.shares)
        share = received[0]
        received[0] = PedersenShare(
            share.x,
            share.value + 1,
            share.blinding,
        )

        result = dkg.run(packages, received_overrides={2: received})
        self.assertEqual(result.qualified_dealers, (1, 3, 4, 5))
        self.assertTrue(all(item.accepted for item in result.verify_all()))
        outcome = dkg.outcomes[1]
        self.assertFalse(outcome.pedersen_qualified)
        self.assertFalse(outcome.qualified)

    def test_valid_dealer_response_repairs_a_bad_delivery(self):
        dkg = self.make_dkg("dkg-repaired-delivery")
        packages = self.make_packages(dkg)
        received = list(packages[1].distribution.shares)
        honest = received[0]
        received[0] = PedersenShare(
            honest.x,
            honest.value + 1,
            honest.blinding,
        )

        result = dkg.run(
            packages,
            received_overrides={2: received},
            dealer_responses={(2, 1): honest},
        )
        self.assertEqual(result.qualified_dealers, (1, 2, 3, 4, 5))
        self.assertTrue(dkg.outcomes[1].qualified)

    def test_mismatched_value_commitments_abort_after_qualification(self):
        dkg = self.make_dkg("dkg-bad-value-commitment")
        packages = self.make_packages(dkg)
        package = packages[2]
        values = list(package.commitments.value.values)
        values[1] = (
            values[1]
            * dkg.value_parameters.commit(1)
            % dkg.value_parameters.group_modulus
        )
        changed_value = FeldmanCommitments(
            dkg.value_parameters,
            tuple(values),
        )
        changed_commitments = DKGDealerCommitments(
            package.commitments.pedersen,
            changed_value,
        )
        packages[2] = DKGDealerPackage(
            package.dealer_id,
            package.distribution,
            changed_commitments,
        )

        with self.assertRaises(DKGAbortError):
            dkg.run(packages)
        self.assertEqual(dkg.state, DKGState.ABORTED)
        self.assertEqual(dkg.computed_qualified_dealers, (1, 2, 3, 4, 5))
        outcome = dkg.outcomes[2]
        self.assertTrue(outcome.pedersen_qualified)
        self.assertFalse(outcome.value_commitments_accepted)
        self.assertTrue(outcome.qualified)

    def test_known_relation_forgery_is_caught_by_value_round(self):
        dkg = self.make_dkg("dkg-known-relation")
        packages = self.make_packages(dkg)
        received = list(packages[0].distribution.shares)
        honest = received[0]

        # In the toy parameters h = g^17.  This pair change preserves the
        # Pedersen commitment, but it no longer matches g^f(x).
        received[0] = PedersenShare(
            honest.x,
            honest.value + 1,
            honest.blinding - inverse(17, 41),
        )
        with self.assertRaises(DKGAbortError):
            dkg.run(packages, received_overrides={1: received})

        self.assertEqual(dkg.state, DKGState.ABORTED)
        self.assertEqual(dkg.computed_qualified_dealers, (1, 2, 3, 4, 5))
        outcome = dkg.outcomes[0]
        self.assertTrue(outcome.pedersen_qualified)
        self.assertFalse(outcome.value_commitments_accepted)

    def test_conflicting_qualification_view_aborts_everything(self):
        dkg = self.make_dkg("dkg-view-conflict")
        packages = self.make_packages(dkg)
        views = {identifier: (1, 2, 3, 4, 5) for identifier in range(1, 6)}
        views[5] = (2, 3, 4, 5)

        with self.assertRaises(QualificationDisagreementError):
            dkg.run(packages, qualification_views=views)
        self.assertEqual(dkg.state, DKGState.ABORTED)

    def test_missing_duplicate_or_unknown_qualification_entries_abort(self):
        cases = [
            {identifier: (1, 2, 3, 4, 5) for identifier in range(1, 5)},
            {
                identifier: ((1, 1, 2, 3, 4, 5) if identifier == 1 else (1, 2, 3, 4, 5))
                for identifier in range(1, 6)
            },
            {
                identifier: ((1, 2, 3, 4, 6) if identifier == 1 else (1, 2, 3, 4, 5))
                for identifier in range(1, 6)
            },
        ]
        for index, views in enumerate(cases):
            with self.subTest(index=index):
                dkg = self.make_dkg(f"dkg-bad-view-{index}")
                packages = self.make_packages(dkg)
                with self.assertRaises(QualificationDisagreementError):
                    dkg.run(packages, qualification_views=views)
                self.assertEqual(dkg.state, DKGState.ABORTED)

    def test_too_few_qualified_dealers_aborts(self):
        dkg = self.make_dkg("dkg-too-few", minimum=3)
        packages = self.make_packages(dkg)
        overrides = {}
        for dealer_id in (1, 2, 3):
            received = list(packages[dealer_id - 1].distribution.shares)
            share = received[0]
            received[0] = PedersenShare(
                share.x,
                share.value + 1,
                share.blinding,
            )
            overrides[dealer_id] = received

        with self.assertRaises(DKGAbortError):
            dkg.run(packages, received_overrides=overrides)
        self.assertEqual(dkg.state, DKGState.ABORTED)
        self.assertEqual(dkg.computed_qualified_dealers, (4, 5))

    def test_exactly_one_package_per_participant_is_required(self):
        for mode in ("missing", "duplicate"):
            with self.subTest(mode=mode):
                dkg = self.make_dkg(f"dkg-package-{mode}")
                packages = self.make_packages(dkg)
                if mode == "missing":
                    selected = packages[:-1]
                else:
                    selected = [packages[0], *packages]
                with self.assertRaises(ValueError):
                    dkg.run(selected)
                self.assertEqual(dkg.state, DKGState.ABORTED)

    def test_unknown_overrides_and_responses_are_rejected(self):
        dkg = self.make_dkg("dkg-unknown-override")
        packages = self.make_packages(dkg)
        with self.assertRaises(ValueError):
            dkg.run(packages, received_overrides={6: []})

        dkg = self.make_dkg("dkg-unknown-response")
        packages = self.make_packages(dkg)
        share = packages[0].distribution.shares[0]
        with self.assertRaises(ValueError):
            dkg.run(packages, dealer_responses={(1, 6): share})

    def test_coordinator_runs_only_once(self):
        dkg, packages, _ = self.run_honest("dkg-once")
        with self.assertRaises(ValueError):
            dkg.run(packages)

    def test_transcript_digest_binds_session_and_qualified_set(self):
        first_dkg, _, first = self.run_honest("dkg-transcript-left", 950)
        second_dkg = self.make_dkg("dkg-transcript-right")
        second_packages = self.make_packages(second_dkg, 950)
        second = second_dkg.run(second_packages)
        self.assertEqual(first.public_key, second.public_key)
        self.assertNotEqual(first.transcript.digest, second.transcript.digest)

        third_dkg = self.make_dkg("dkg-transcript-left")
        third_packages = self.make_packages(third_dkg, 950)
        received = list(third_packages[0].distribution.shares)
        share = received[0]
        received[0] = PedersenShare(
            share.x,
            share.value + 1,
            share.blinding,
        )
        third = third_dkg.run(
            third_packages,
            received_overrides={1: received},
        )
        self.assertNotEqual(first.qualified_dealers, third.qualified_dealers)
        self.assertNotEqual(first.transcript.digest, third.transcript.digest)
        self.assertEqual(first_dkg.state, DKGState.COMPLETE)

    def test_changed_final_share_is_rejected(self):
        _, _, result = self.run_honest("dkg-final-tamper")
        honest = result.participant_shares[0]
        changed = replace(honest, secret_share=honest.secret_share + 1)
        verification = result.verify_share(changed)
        self.assertFalse(verification.accepted)
        self.assertFalse(verification.pedersen_accepted)
        self.assertFalse(verification.value_accepted)

    def test_final_share_is_bound_to_the_common_qualified_set(self):
        _, _, result = self.run_honest("dkg-final-source-set")
        honest = result.participant_shares[0]
        changed = replace(honest, source_dealers=(2, 3, 4, 5))
        verification = result.verify_share(changed)
        self.assertTrue(verification.pedersen_accepted)
        self.assertTrue(verification.value_accepted)
        self.assertFalse(verification.accepted)
        self.assertEqual(
            verification.reason,
            "aggregate share is bound to a different qualified set",
        )

    def test_response_without_active_complaint_is_rejected(self):
        dkg = self.make_dkg("dkg-unsolicited-response")
        packages = self.make_packages(dkg)
        honest = packages[0].distribution.shares[0]
        with self.assertRaises(ValueError):
            dkg.run(packages, dealer_responses={(1, 1): honest})
        self.assertEqual(dkg.state, DKGState.ABORTED)

    def test_audit_requires_threshold_distinct_known_participants(self):
        _, _, result = self.run_honest("dkg-audit-errors")
        with self.assertRaises(ValueError):
            result.audit_reconstruct_field_element([1, 2])
        with self.assertRaises(ValueError):
            result.audit_reconstruct_field_element([1, 1, 2])
        with self.assertRaises(ValueError):
            result.audit_reconstruct_field_element([1, 2, 6])

    def test_minimum_qualified_policy_is_validated(self):
        with self.assertRaises(ValueError):
            self.make_dkg("dkg-min-zero", minimum=0)
        with self.assertRaises(ValueError):
            self.make_dkg("dkg-min-six", minimum=6)

    def test_participant_shares_record_the_common_source_set(self):
        _, _, result = self.run_honest("dkg-share-sources")
        for share in result.participant_shares:
            self.assertEqual(share.source_dealers, result.qualified_dealers)


if __name__ == "__main__":
    unittest.main()
