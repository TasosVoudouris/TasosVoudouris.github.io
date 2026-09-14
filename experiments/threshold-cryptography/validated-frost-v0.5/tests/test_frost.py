import hashlib
import json
import random
import sys
import unittest
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import (
    FrostAbortError,
    FrostCoordinator,
    FrostGroupInfo,
    FrostSignature,
    FrostSignatureShare,
    FrostSigner,
    MessageRejectedError,
    NonceCommitment,
    NonceReuseError,
    ToyFROSTSuite,
    compute_binding_factors,
    compute_challenge,
    compute_group_commitment,
    derive_interpolating_value,
    encode_group_commitment_list,
    run_frost_signing,
    verify_schnorr_signature,
)
from cryptocave_sss.shamir import ShamirScheme


class FrostVersion05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dkg = MultiDealerDKG.educational(session_id="frost-tests-dkg")
        packages = [
            dkg.create_dealer_package(
                participant_id,
                rng=random.Random(500 + participant_id),
            )
            for participant_id in dkg.shamir.participant_ids
        ]
        cls.dkg_result = dkg.run(packages)
        cls.group_info = FrostGroupInfo.from_dkg(cls.dkg_result)

    @staticmethod
    def byte_source(seed):
        return random.Random(seed).randbytes

    def signers(self, participant_ids, validators=None):
        validators = validators or {}
        return [
            FrostSigner.from_dkg(
                self.dkg_result,
                participant_id,
                validators.get(participant_id),
            )
            for participant_id in participant_ids
        ]

    def honest_run(
        self,
        participant_ids=(1, 2, 3),
        *,
        label="honest",
        counter=1,
        context="CryptoCave test transaction",
        message=b"approve educational transaction",
    ):
        # In a real group an identity aggregate commitment is negligible.  It
        # occurs with probability 1/41 here, so retry with fresh teaching bytes.
        for attempt in range(100):
            coordinator = FrostCoordinator(self.group_info)
            signers = self.signers(participant_ids)
            sources = {
                participant_id: self.byte_source(
                    10_000 + 100 * attempt + participant_id
                )
                for participant_id in participant_ids
            }
            try:
                run = run_frost_signing(
                    coordinator,
                    signers,
                    session_id=f"{label}-{attempt}",
                    counter=counter,
                    application_context=context,
                    message=message,
                    random_byte_sources=sources,
                )
                return coordinator, signers, run
            except ValueError as error:
                if "non-identity subgroup element" not in str(error):
                    raise
        self.fail("could not obtain a non-identity aggregate commitment")

    def prepared_round(
        self,
        participant_ids=(1, 2, 3),
        *,
        label="prepared",
        validators=None,
    ):
        for attempt in range(100):
            coordinator = FrostCoordinator(self.group_info)
            signers = self.signers(participant_ids, validators)
            commitments = [
                signer.commit(
                    f"{label}-{attempt}",
                    1,
                    self.byte_source(20_000 + 100 * attempt + signer.participant_id),
                )
                for signer in signers
            ]
            try:
                package = coordinator.create_signing_package(
                    session_id=f"{label}-{attempt}",
                    counter=1,
                    application_context="CryptoCave prepared-round test",
                    message=b"prepared message",
                    commitments=commitments,
                )
                return coordinator, signers, package
            except ValueError as error:
                for signer, commitment in zip(signers, commitments):
                    signer.discard_nonce(commitment.nonce_id)
                if "non-identity subgroup element" not in str(error):
                    raise
        self.fail("could not obtain a non-identity aggregate commitment")

    def test_group_info_is_derived_from_dkg_commitments(self):
        self.assertEqual(
            self.group_info.group_public_key,
            self.dkg_result.value_commitments.values[0],
        )
        for participant_id in self.group_info.participant_ids:
            self.assertEqual(
                self.group_info.verifying_share_for(participant_id),
                self.dkg_result.value_commitments.expected_share_commitment(
                    participant_id
                ),
            )

    def test_honest_three_of_five_signing_verifies(self):
        _, signers, run = self.honest_run(label="three-of-five")
        self.assertTrue(run.result.transcript.final_verified)
        self.assertTrue(all(item.accepted for item in run.result.share_verifications))
        self.assertEqual(run.package.participant_ids, (1, 2, 3))
        self.assertTrue(all(signer.pending_nonce_count == 0 for signer in signers))

    def test_every_threshold_subset_can_sign(self):
        for subset in combinations(self.group_info.participant_ids, 3):
            with self.subTest(subset=subset):
                _, _, run = self.honest_run(
                    subset,
                    label="subset-" + "-".join(map(str, subset)),
                )
                self.assertTrue(run.result.transcript.final_verified)

    def test_four_and_five_signer_sets_can_sign(self):
        for participant_ids in ((1, 2, 3, 4), (1, 2, 3, 4, 5)):
            with self.subTest(participant_ids=participant_ids):
                _, _, run = self.honest_run(
                    participant_ids,
                    label=f"size-{len(participant_ids)}",
                )
                self.assertTrue(run.result.transcript.final_verified)

    def test_unsorted_signer_input_becomes_a_canonical_package(self):
        _, _, run = self.honest_run((5, 2, 4), label="unsorted")
        self.assertEqual(run.package.participant_ids, (2, 4, 5))

    def test_lagrange_coefficients_reproduce_a_degree_two_constant(self):
        q = self.group_info.suite.scalar_modulus
        identifiers = (1, 3, 5)
        polynomial_values = {
            x: (7 + 9 * x + 4 * x * x) % q for x in identifiers
        }
        reconstructed = sum(
            derive_interpolating_value(identifiers, x, q) * polynomial_values[x]
            for x in identifiers
        ) % q
        self.assertEqual(reconstructed, 7)

    def test_lagrange_helper_rejects_missing_duplicate_and_zero_ids(self):
        q = self.group_info.suite.scalar_modulus
        with self.assertRaises(ValueError):
            derive_interpolating_value((1, 2, 3), 4, q)
        with self.assertRaises(ValueError):
            derive_interpolating_value((1, 1, 3), 1, q)
        with self.assertRaises(ValueError):
            derive_interpolating_value((0, 2, 3), 2, q)

    def test_binding_factors_cover_exactly_the_selected_signers(self):
        _, _, package = self.prepared_round(label="binding-coverage")
        factors = compute_binding_factors(self.group_info, package)
        self.assertEqual(tuple(identifier for identifier, _ in factors), (1, 2, 3))

    def test_binding_factors_bind_the_message(self):
        _, _, package = self.prepared_round(label="binding-message")
        changed = replace(package, message=b"different prepared message")
        self.assertNotEqual(
            compute_binding_factors(self.group_info, package),
            compute_binding_factors(self.group_info, changed),
        )

    def test_binding_factors_bind_the_commitment_list(self):
        _, _, package = self.prepared_round(label="binding-commitments")
        first = package.commitments[0]
        changed_first = replace(
            first,
            hiding=(
                first.hiding
                * self.group_info.suite.generator
                % self.group_info.suite.group_modulus
            ),
        )
        if changed_first.hiding == 1:
            changed_first = replace(
                first,
                hiding=(
                    first.hiding
                    * pow(self.group_info.suite.generator, 2, self.group_info.suite.group_modulus)
                    % self.group_info.suite.group_modulus
                ),
            )
        changed = replace(
            package,
            commitments=(changed_first, *package.commitments[1:]),
        )
        self.assertNotEqual(
            compute_binding_factors(self.group_info, package),
            compute_binding_factors(self.group_info, changed),
        )

    def test_commitment_list_encoding_is_exact_concatenation(self):
        _, _, package = self.prepared_round(label="commitment-encoding")
        suite = self.group_info.suite
        expected = b"".join(
            suite.serialize_scalar(item.participant_id)
            + suite.serialize_element(item.hiding)
            + suite.serialize_element(item.binding)
            for item in package.commitments
        )
        self.assertEqual(
            encode_group_commitment_list(package.commitments, suite),
            expected,
        )

    def test_group_commitment_matches_the_product_equation(self):
        _, _, package = self.prepared_round(label="group-commitment")
        suite = self.group_info.suite
        factors = dict(compute_binding_factors(self.group_info, package))
        expected = 1
        for item in package.commitments:
            expected = (
                expected
                * item.hiding
                * pow(item.binding, factors[item.participant_id], suite.group_modulus)
                % suite.group_modulus
            )
        self.assertEqual(
            compute_group_commitment(self.group_info, package),
            expected,
        )

    def test_challenge_binds_R_public_key_and_signed_message(self):
        _, _, package = self.prepared_round(label="challenge")
        group_commitment = compute_group_commitment(self.group_info, package)
        suite = self.group_info.suite
        expected = suite.h2(
            suite.serialize_element(group_commitment)
            + suite.serialize_element(self.group_info.group_public_key)
            + package.message_to_sign(suite)
        )
        self.assertEqual(
            compute_challenge(self.group_info, package, group_commitment),
            expected,
        )

    def test_every_partial_signature_is_checked_before_aggregation(self):
        coordinator, signers, package = self.prepared_round(label="partials")
        shares = tuple(signer.sign(package) for signer in signers)
        checks = tuple(
            coordinator.verify_signature_share(package, share) for share in shares
        )
        self.assertTrue(all(check.accepted for check in checks))
        result = coordinator.aggregate(package, shares)
        self.assertEqual(result.share_verifications, checks)

    def test_final_signature_passes_the_ordinary_schnorr_verifier(self):
        _, _, run = self.honest_run(label="ordinary-verifier")
        suite = self.group_info.suite
        self.assertTrue(
            verify_schnorr_signature(
                run.package.message_to_sign(suite),
                run.result.signature,
                self.group_info.group_public_key,
                suite,
            )
        )

    def test_raw_payload_is_not_the_bound_application_envelope(self):
        _, _, run = self.honest_run(label="raw-payload")
        self.assertFalse(
            verify_schnorr_signature(
                run.package.message,
                run.result.signature,
                self.group_info.group_public_key,
                self.group_info.suite,
            )
        )

    def test_changed_message_session_counter_context_or_signer_set_fails(self):
        coordinator, _, run = self.honest_run(label="envelope-binding")
        alternatives = [
            replace(run.package, message=b"changed"),
            replace(run.package, session_id="changed-session"),
            replace(run.package, counter=2),
            # q=41 makes challenge collisions visible, so this fixed alternate
            # was selected to exercise a non-colliding context change.
            replace(run.package, application_context="wrong-purpose"),
        ]
        fourth = replace(run.package.commitments[2], participant_id=4)
        alternatives.append(
            replace(
                run.package,
                commitments=(
                    run.package.commitments[0],
                    run.package.commitments[1],
                    fourth,
                ),
            )
        )
        for package in alternatives:
            with self.subTest(package=package):
                self.assertFalse(coordinator.verify_final(package, run.result.signature))

    def test_tampered_final_response_fails(self):
        coordinator, _, run = self.honest_run(label="tampered-z")
        q = self.group_info.suite.scalar_modulus
        changed = replace(
            run.result.signature,
            response=(run.result.signature.response + 1) % q,
        )
        self.assertFalse(coordinator.verify_final(run.package, changed))

    def test_tampered_final_commitment_fails(self):
        coordinator, _, run = self.honest_run(label="tampered-R")
        suite = self.group_info.suite
        changed_element = (
            run.result.signature.group_commitment * suite.generator
        ) % suite.group_modulus
        if changed_element == 1:
            changed_element = (
                run.result.signature.group_commitment
                * pow(suite.generator, 2, suite.group_modulus)
            ) % suite.group_modulus
        changed = replace(run.result.signature, group_commitment=changed_element)
        self.assertFalse(coordinator.verify_final(run.package, changed))

    def test_tampered_partial_share_causes_identifiable_abort(self):
        coordinator, signers, package = self.prepared_round(label="bad-partial")
        shares = [signer.sign(package) for signer in signers]
        shares[1] = replace(
            shares[1],
            value=(shares[1].value + 1) % self.group_info.suite.scalar_modulus,
        )
        check = coordinator.verify_signature_share(package, shares[1])
        self.assertFalse(check.accepted)
        with self.assertRaisesRegex(FrostAbortError, r"\(2,\)"):
            coordinator.aggregate(package, shares)

    def test_partial_share_bound_to_other_package_is_rejected(self):
        coordinator, signers, package = self.prepared_round(label="wrong-package")
        share = signers[0].sign(package)
        changed = replace(share, package_digest="00" * 32)
        check = coordinator.verify_signature_share(package, changed)
        self.assertFalse(check.accepted)
        self.assertIn("another package", check.reason)

    def test_missing_duplicate_and_extra_signature_shares_abort(self):
        modes = ("missing", "duplicate", "extra")
        for mode in modes:
            with self.subTest(mode=mode):
                coordinator, signers, package = self.prepared_round(
                    label=f"share-set-{mode}"
                )
                shares = [signer.sign(package) for signer in signers]
                if mode == "missing":
                    supplied = shares[:-1]
                elif mode == "duplicate":
                    supplied = [shares[0], shares[0], shares[2]]
                else:
                    supplied = [
                        *shares,
                        FrostSignatureShare(4, 0, package.digest),
                    ]
                with self.assertRaises(FrostAbortError):
                    coordinator.aggregate(package, supplied)

    def test_nonce_state_is_single_use_and_deleted_after_sign(self):
        _, signers, package = self.prepared_round(label="nonce-single-use")
        signer = signers[0]
        signer.sign(package)
        self.assertEqual(signer.pending_nonce_count, 0)
        with self.assertRaises(NonceReuseError):
            signer.sign(package)

    def test_signer_rejects_changed_own_commitment(self):
        _, signers, package = self.prepared_round(label="changed-own-commitment")
        first = package.commitments[0]
        suite = self.group_info.suite
        changed_hiding = first.hiding * suite.generator % suite.group_modulus
        if changed_hiding == 1:
            changed_hiding = (
                first.hiding * pow(suite.generator, 2, suite.group_modulus)
            ) % suite.group_modulus
        changed_first = replace(first, hiding=changed_hiding)
        changed_package = replace(
            package,
            commitments=(changed_first, *package.commitments[1:]),
        )
        with self.assertRaisesRegex(FrostAbortError, "changed"):
            signers[0].sign(changed_package)

    def test_signer_rejects_different_session_or_counter(self):
        for field, value in (("session_id", "other-session"), ("counter", 2)):
            with self.subTest(field=field):
                _, signers, package = self.prepared_round(label=f"wrong-{field}")
                changed = replace(package, **{field: value})
                with self.assertRaisesRegex(FrostAbortError, "another session"):
                    signers[0].sign(changed)

    def test_unselected_signer_cannot_create_a_share(self):
        _, signers, package = self.prepared_round(label="unselected")
        outsider = FrostSigner.from_dkg(self.dkg_result, 4)
        with self.assertRaisesRegex(FrostAbortError, "not selected"):
            outsider.sign(package)
        self.assertEqual(signers[0].pending_nonce_count, 1)

    def test_message_policy_rejects_and_burns_the_nonce(self):
        def raises(_package):
            raise RuntimeError("simulated parser failure")

        validators = (
            lambda package: package.message.startswith(b"allowed:"),
            raises,
        )
        for index, validator in enumerate(validators):
            with self.subTest(index=index):
                _, signers, package = self.prepared_round(
                    label=f"message-policy-{index}",
                    validators={1: validator},
                )
                with self.assertRaises(MessageRejectedError):
                    signers[0].sign(package)
                self.assertEqual(signers[0].pending_nonce_count, 0)

    def test_group_info_mismatch_is_rejected(self):
        other_dkg = MultiDealerDKG.educational(session_id="other-frost-dkg")
        other_packages = [
            other_dkg.create_dealer_package(
                participant_id,
                rng=random.Random(500 + participant_id),
            )
            for participant_id in other_dkg.shamir.participant_ids
        ]
        other_result = other_dkg.run(other_packages)
        other_coordinator = FrostCoordinator.from_dkg(other_result)

        _, signers, original_package = self.prepared_round(label="group-mismatch")
        other_package = replace(
            original_package,
            group_info_digest=other_coordinator.group_info.digest,
        )
        with self.assertRaisesRegex(FrostAbortError, "different group"):
            signers[0].sign(other_package)

    def test_too_few_signers_are_rejected(self):
        coordinator = FrostCoordinator(self.group_info)
        signers = self.signers((1, 2))
        commitments = [
            signer.commit("too-few", 1, self.byte_source(30_000 + signer.participant_id))
            for signer in signers
        ]
        with self.assertRaisesRegex(FrostAbortError, "between threshold"):
            coordinator.create_signing_package(
                session_id="too-few",
                counter=1,
                application_context="threshold test",
                message=b"message",
                commitments=commitments,
            )

    def test_duplicate_and_unknown_commitment_participants_are_rejected(self):
        coordinator, _, package = self.prepared_round(label="bad-commitment-ids")
        first, second, third = package.commitments
        duplicate = replace(second, participant_id=first.participant_id)
        with self.assertRaises(ValueError):
            coordinator.create_signing_package(
                session_id="duplicate-ids",
                counter=1,
                application_context="identifier test",
                message=b"message",
                commitments=(first, duplicate, third),
            )
        unknown = replace(third, participant_id=6)
        with self.assertRaisesRegex(FrostAbortError, "unknown"):
            coordinator.create_signing_package(
                session_id="unknown-id",
                counter=1,
                application_context="identifier test",
                message=b"message",
                commitments=(first, second, unknown),
            )

    def test_invalid_group_elements_are_rejected_before_signing(self):
        coordinator, _, package = self.prepared_round(label="bad-element")
        invalid = replace(package.commitments[0], hiding=82)
        with self.assertRaisesRegex(ValueError, "non-identity"):
            coordinator.create_signing_package(
                session_id="bad-element-new",
                counter=1,
                application_context="element validation",
                message=b"message",
                commitments=(invalid, *package.commitments[1:]),
            )

    def test_coordinator_tracks_and_rejects_reused_commitments(self):
        coordinator, _, package = self.prepared_round(label="coordinator-reuse")
        with self.assertRaises(NonceReuseError):
            coordinator.create_signing_package(
                session_id="coordinator-reuse-second",
                counter=2,
                application_context="reuse detection",
                message=b"different message",
                commitments=package.commitments,
            )

    def test_coordinator_closes_a_package_after_aggregation(self):
        coordinator, signers, package = self.prepared_round(label="closed-package")
        shares = tuple(signer.sign(package) for signer in signers)
        coordinator.aggregate(package, shares)
        with self.assertRaisesRegex(FrostAbortError, "already closed"):
            coordinator.aggregate(package, shares)

    def test_coordinator_rejects_a_package_it_did_not_issue(self):
        _, signers, package = self.prepared_round(label="not-issued")
        shares = tuple(signer.sign(package) for signer in signers)
        fresh = FrostCoordinator(self.group_info)
        with self.assertRaisesRegex(FrostAbortError, "did not issue"):
            fresh.aggregate(package, shares)

    def test_wrong_length_random_source_is_rejected(self):
        signer = self.signers((1,))[0]
        with self.assertRaisesRegex(ValueError, "exactly 32 bytes"):
            signer.commit("bad-random-source", 1, lambda size: b"short")

    def test_suite_rejects_identity_public_keys_and_verifying_shares(self):
        with self.assertRaisesRegex(ValueError, "group public key"):
            replace(self.group_info, group_public_key=1)
        changed = list(self.group_info.verifying_shares)
        changed[0] = replace(changed[0], element=1)
        with self.assertRaisesRegex(ValueError, "verifying shares"):
            replace(self.group_info, verifying_shares=tuple(changed))

    def test_signature_encoding_is_R_then_z_with_fixed_width(self):
        _, _, run = self.honest_run(label="encoding")
        suite = self.group_info.suite
        encoded = run.result.signature.encode(suite)
        self.assertEqual(len(encoded), suite.element_size + suite.scalar_size)
        self.assertEqual(
            encoded,
            suite.serialize_element(run.result.signature.group_commitment)
            + suite.serialize_scalar(run.result.signature.response),
        )

    def test_public_transcript_contains_no_private_key_or_nonce_scalars(self):
        _, _, run = self.honest_run(label="public-transcript")
        public = run.result.transcript.as_public_dict()
        encoded = json.dumps(public, sort_keys=True)
        self.assertNotIn("secret_share", encoded)
        self.assertNotIn("signing_share", encoded)
        self.assertNotIn("hiding_nonce", encoded)
        self.assertNotIn("binding_nonce", encoded)
        self.assertEqual(len(run.result.transcript.digest), 64)

    def test_normal_signing_never_reconstructs_the_group_secret(self):
        with patch.object(
            ShamirScheme,
            "reconstruct_field_element",
            side_effect=AssertionError("FROST must not reconstruct"),
        ), patch.object(
            ShamirScheme,
            "reconstruct",
            side_effect=AssertionError("FROST must not reconstruct"),
        ):
            _, _, run = self.honest_run(label="no-reconstruction")
        self.assertTrue(run.result.transcript.final_verified)

    def test_reproducible_teaching_inputs_produce_the_same_signature(self):
        def one_run():
            coordinator = FrostCoordinator(self.group_info)
            signers = self.signers((1, 2, 3))
            return run_frost_signing(
                coordinator,
                signers,
                session_id="reproducible-session",
                counter=1,
                application_context="reproducibility test",
                message=b"same payload",
                random_byte_sources={
                    participant_id: self.byte_source(40_000 + participant_id)
                    for participant_id in (1, 2, 3)
                },
            )

        first = one_run()
        second = one_run()
        self.assertEqual(first.package, second.package)
        self.assertEqual(first.result.signature, second.result.signature)
        self.assertEqual(first.result.transcript.digest, second.result.transcript.digest)

    def test_domain_separated_message_and_commitment_hashes_differ(self):
        suite = self.group_info.suite
        self.assertNotEqual(suite.h4(b"same input"), suite.h5(b"same input"))

    def test_noncanonical_signature_values_fail_without_exception(self):
        _, _, run = self.honest_run(label="noncanonical-signature")
        suite = self.group_info.suite
        self.assertFalse(
            verify_schnorr_signature(
                run.package.message_to_sign(suite),
                FrostSignature(run.result.signature.group_commitment, suite.scalar_modulus),
                self.group_info.group_public_key,
                suite,
            )
        )

    def test_application_envelope_commits_to_the_dkg_group_digest(self):
        _, _, package = self.prepared_round(label="dkg-envelope")
        signed_message = package.message_to_sign(self.group_info.suite)
        self.assertIn(bytes.fromhex(self.group_info.digest), signed_message)
        self.assertEqual(
            hashlib.sha256(signed_message).hexdigest(),
            hashlib.sha256(package.message_to_sign(self.group_info.suite)).hexdigest(),
        )

    def test_toy_suite_is_explicitly_not_an_rfc_named_ciphersuite(self):
        self.assertEqual(
            self.group_info.suite.context_string,
            b"CryptoCave-FROST-toy-SHA256-v1",
        )
        self.assertNotIn(
            self.group_info.suite.context_string,
            {
                b"FROST-RISTRETTO255-SHA512-v1",
                b"FROST-P256-SHA256-v1",
                b"FROST-secp256k1-SHA256-v1",
            },
        )


if __name__ == "__main__":
    unittest.main()
