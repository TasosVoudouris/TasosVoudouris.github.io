"""Verification suite for the linear-cryptanalysis teaching module.

Run from this directory with:

    python -m unittest -v test.py
"""

import unittest

from matsui1 import (
    COMPANION_SBOX,
    PRESENT_SBOX,
    TOY_SPN_PBOX,
    TOY_SPN_SBOX,
    SPN,
    approximation_bias,
    approximation_correlation,
    bit_parity,
    count_matches,
    demo_spn_partial_attack,
    dot,
    estimate_data_complexity,
    extract_round_key_nibbles,
    get_bit_msb,
    inverse_pbox,
    inverse_sbox,
    linear_approximation_table,
    matsui1_details,
    matsui2,
    permute,
    piling_up_bias,
    propagate_mask_backwards,
    rank_key_guesses,
    sbox_linearity,
    sbox_nonlinearity,
    set_bit_msb,
    substitute,
    walsh_coefficient,
)


class BitHelperTests(unittest.TestCase):
    def test_parity_and_dot(self) -> None:
        self.assertEqual(bit_parity(0b1011), 1)
        self.assertEqual(bit_parity(0b1100), 0)
        self.assertEqual(dot(0b1011, 0b1001), 0)
        self.assertEqual(dot(0b1101, 0b1100), 0)

    def test_msb_first_bit_access(self) -> None:
        word = 0b01010
        self.assertEqual([get_bit_msb(word, i, 5) for i in range(5)], [0, 1, 0, 1, 0])
        self.assertEqual(set_bit_msb(word, 0, 5, 1), 0b11010)
        self.assertEqual(set_bit_msb(word, 3, 5, 0), 0b01000)


class LayerHelperTests(unittest.TestCase):
    def test_sbox_inverse_and_substitution(self) -> None:
        inverse = inverse_sbox(PRESENT_SBOX)
        for x in range(16):
            self.assertEqual(inverse[PRESENT_SBOX[x]], x)
        word = 0x0123
        encrypted = substitute(word, PRESENT_SBOX, 4, 4)
        self.assertEqual(substitute(encrypted, inverse, 4, 4), word)

    def test_pbox_inverse(self) -> None:
        inverse = inverse_pbox(TOY_SPN_PBOX)
        for x in (0, 1, 0x1234, 0x8001, 0xFFFF):
            self.assertEqual(permute(permute(x, TOY_SPN_PBOX, 16), inverse, 16), x)

    def test_mask_propagation_identity(self) -> None:
        for output_mask in (0, 1, 0x0505, 0x8001, 0xFFFF):
            input_mask = propagate_mask_backwards(output_mask, TOY_SPN_PBOX)
            for x in (0, 1, 0x1234, 0xA55A, 0xFFFF):
                self.assertEqual(
                    dot(permute(x, TOY_SPN_PBOX, 16), output_mask),
                    dot(x, input_mask),
                )


class LinearApproximationTests(unittest.TestCase):
    def test_present_lat_entries_and_conventions(self) -> None:
        lat = linear_approximation_table(PRESENT_SBOX, 4)
        self.assertEqual(lat[0][0], 8)
        self.assertEqual(lat[9][1], 4)
        self.assertEqual(lat[1][5], -4)
        self.assertEqual(count_matches(9, 1, PRESENT_SBOX, 4), 12)
        self.assertEqual(approximation_bias(9, 1, PRESENT_SBOX, 4), 0.25)
        self.assertEqual(approximation_correlation(9, 1, PRESENT_SBOX, 4), 0.5)
        self.assertEqual(walsh_coefficient(9, 1, PRESENT_SBOX, 4), 8)

    def test_companion_sbox_strong_negative_entry(self) -> None:
        lat = linear_approximation_table(COMPANION_SBOX, 4)
        self.assertEqual(lat[0x9][0x2], -6)
        self.assertEqual(lat[0xD][0xD], -6)
        self.assertEqual(approximation_bias(0xD, 0xD, COMPANION_SBOX, 4), -0.375)

    def test_linearity_and_nonlinearity(self) -> None:
        self.assertEqual(sbox_linearity(PRESENT_SBOX), 8)
        self.assertEqual(sbox_nonlinearity(PRESENT_SBOX), 4)
        self.assertEqual(sbox_linearity(COMPANION_SBOX), 12)
        self.assertEqual(sbox_nonlinearity(COMPANION_SBOX), 2)

    def test_piling_up_sign_and_magnitude(self) -> None:
        self.assertEqual(piling_up_bias([0.25, -0.25]), -0.125)
        self.assertEqual(piling_up_bias([-0.375, -0.375]), 0.28125)
        self.assertEqual(estimate_data_complexity(-1 / 32), 1024)


class MatsuiAlgorithmTests(unittest.TestCase):
    def test_algorithm_1_positive_and_negative_signs(self) -> None:
        key = 0xA
        messages = list(range(16))

        # Positive-bias PRESENT relation (9 -> 1).
        ciphertexts = [PRESENT_SBOX[m ^ key] for m in messages]
        positive = matsui1_details(messages, ciphertexts, 0x9, 0x1, +1)
        self.assertEqual(positive.key_parity, dot(key, 0x9))

        # Negative-bias PRESENT relation (1 -> 5); the decision is complemented.
        negative = matsui1_details(messages, ciphertexts, 0x1, 0x5, -1)
        self.assertEqual(negative.key_parity, dot(key, 0x1))

    def test_algorithm_2_uses_absolute_scores(self) -> None:
        keys = (0x3, 0xA, 0x5, 0xC)
        k0, k1, k2, final_key = keys
        messages = list(range(16))  # complete codebook: no duplicated evidence
        ciphertexts = [
            COMPANION_SBOX[
                COMPANION_SBOX[COMPANION_SBOX[m ^ k0] ^ k1] ^ k2
            ]
            ^ final_key
            for m in messages
        ]
        scores = matsui2(
            messages,
            ciphertexts,
            0xD,
            0xD,
            inverse_sbox(COMPANION_SBOX),
        )
        ranking = rank_key_guesses(scores)
        self.assertEqual(abs(scores[final_key]), max(map(abs, scores)))
        self.assertIn(final_key, ranking[:4])

    def test_partial_spn_attack_deterministic_example(self) -> None:
        best, actual, rank = demo_spn_partial_attack(8_192)
        self.assertEqual(best, actual)
        self.assertEqual(rank, 1)


class SPNTests(unittest.TestCase):
    def test_round_keys_and_target_nibbles(self) -> None:
        cipher = SPN(TOY_SPN_SBOX, TOY_SPN_PBOX)
        keys = cipher.key_schedule(0x3A94D63F)
        self.assertEqual(keys, [0x3A94, 0xA94D, 0x94D6, 0x4D63, 0xD63F])
        self.assertEqual(extract_round_key_nibbles(keys[-1], (8, 0)), 0x6F)

    def test_encrypt_decrypt_round_trip(self) -> None:
        cipher = SPN(TOY_SPN_SBOX, TOY_SPN_PBOX)
        key = 0x3A94D63F
        for message in (0, 1, 0x1234, 0xBEEF, 0xFFFF):
            self.assertEqual(cipher.decrypt(cipher.encrypt(message, key), key), message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
