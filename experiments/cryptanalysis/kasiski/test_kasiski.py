"""Regression tests for the Kasiski/Vigenere teaching module.

Run with:

    python -m unittest -v test_kasiski.py
"""

import unittest
from pathlib import Path

DATA_FILE = Path(__file__).with_name("input-1-50.txt")

from kasiski import (
    ENGLISH_IC,
    RANDOM_IC,
    all_distances_from_positions,
    average_column_ic,
    best_shift_for_column,
    break_vigenere,
    clean_text,
    factor_score,
    find_repeated_ngrams_positions,
    friedman_period_estimate,
    index_of_coincidence,
    kasiski_distances,
    minimal_repeating_unit,
    rank_periods,
    recover_key,
    split_columns,
    vigenere_decrypt,
    vigenere_encrypt,
)


class VigenereTests(unittest.TestCase):
    def test_normalization(self) -> None:
        self.assertEqual(clean_text("Attack at dawn! 123"), "ATTACKATDAWN")

    def test_known_answer(self) -> None:
        ciphertext = vigenere_encrypt("ATTACK AT DAWN", "LEMON")
        self.assertEqual(ciphertext, "LXFOPVEFRNHR")
        self.assertEqual(vigenere_decrypt(ciphertext, "LEMON"), "ATTACKATDAWN")

    def test_preserve_nonletters(self) -> None:
        ciphertext = vigenere_encrypt(
            "ATTACK AT DAWN", "LEMON", preserve_nonletters=True
        )
        self.assertEqual(ciphertext, "LXFOPV EF RNHR")
        self.assertEqual(
            vigenere_decrypt(ciphertext, "LEMON", preserve_nonletters=True),
            "ATTACK AT DAWN",
        )

    def test_empty_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vigenere_encrypt("MESSAGE", "123")


class KasiskiTests(unittest.TestCase):
    def test_overlapping_ngram_positions(self) -> None:
        repeated = find_repeated_ngrams_positions("ABCABCABC", 3)
        self.assertEqual(repeated["ABC"], [0, 3, 6])
        self.assertEqual(repeated["BCA"], [1, 4])
        self.assertEqual(repeated["CAB"], [2, 5])

    def test_consecutive_and_all_pair_distances(self) -> None:
        positions = [2, 7, 17]
        self.assertEqual(all_distances_from_positions(positions), [5, 10])
        self.assertEqual(
            all_distances_from_positions(positions, consecutive_only=False),
            [5, 15, 10],
        )

    def test_factor_votes_include_all_bounded_divisors(self) -> None:
        votes = factor_score([12], max_period=12)
        self.assertEqual(
            {period for period, count in votes.items() if count},
            {2, 3, 4, 6, 12},
        )

    def test_kasiski_distances_are_positive(self) -> None:
        _, distances = kasiski_distances("ABCABCABCXYZXYZ", 3, 4)
        self.assertTrue(distances)
        self.assertTrue(all(distance > 0 for distance in distances))


class CoincidenceTests(unittest.TestCase):
    def test_extreme_ic_values(self) -> None:
        self.assertEqual(index_of_coincidence("AAAA"), 1.0)
        self.assertEqual(index_of_coincidence("ABCD"), 0.0)
        self.assertAlmostEqual(RANDOM_IC, 1 / 26)
        self.assertAlmostEqual(ENGLISH_IC, 0.0654966995)

    def test_column_split(self) -> None:
        self.assertEqual(split_columns("ABCDEFGHIJ", 3), ["ADGJ", "BEH", "CFI"])

    def test_true_period_has_language_like_column_ic(self) -> None:
        plaintext = clean_text(DATA_FILE.read_text(encoding="utf-8"))
        ciphertext = vigenere_encrypt(plaintext, "MOUSE")
        self.assertGreater(average_column_ic(ciphertext, 5), 0.06)
        self.assertLess(average_column_ic(ciphertext, 4), 0.05)

    def test_friedman_estimate_is_only_approximate(self) -> None:
        plaintext = clean_text(DATA_FILE.read_text(encoding="utf-8"))
        ciphertext = vigenere_encrypt(plaintext, "MOUSE")
        estimate = friedman_period_estimate(ciphertext)
        self.assertGreater(estimate, 2)
        self.assertLess(estimate, 12)


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plaintext = clean_text(
            DATA_FILE.read_text(encoding="utf-8")
        )
        cls.ciphertext = vigenere_encrypt(cls.plaintext, "MOUSE")

    def test_combined_ranking_selects_fundamental_period(self) -> None:
        ranking = rank_periods(self.ciphertext, max_period=20)
        self.assertEqual(ranking[0].period, 5)
        self.assertIn(10, [row.period for row in ranking[:4]])
        self.assertIn(15, [row.period for row in ranking[:4]])

    def test_caesar_shift_recovery(self) -> None:
        single_shift = vigenere_encrypt(self.plaintext, "D")
        self.assertEqual(best_shift_for_column(single_shift), 3)

    def test_key_recovery(self) -> None:
        self.assertEqual(recover_key(self.ciphertext, 5), "MOUSE")
        self.assertEqual(
            recover_key(self.ciphertext, 10, reduce_repeated=True),
            "MOUSE",
        )

    def test_minimal_repeating_unit(self) -> None:
        self.assertEqual(minimal_repeating_unit("MOUSEMOUSE"), "MOUSE")
        self.assertEqual(minimal_repeating_unit("LEMON"), "LEMON")

    def test_end_to_end_break(self) -> None:
        result = break_vigenere(self.ciphertext, max_period=20)
        self.assertEqual(result.period, 5)
        self.assertEqual(result.key, "MOUSE")
        self.assertEqual(result.plaintext, self.plaintext)


if __name__ == "__main__":
    unittest.main(verbosity=2)
