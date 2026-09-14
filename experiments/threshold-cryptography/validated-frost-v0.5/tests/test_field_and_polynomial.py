import unittest
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.field import decode_signed, encode_signed, inverse, is_prime
from cryptocave_sss.polynomial import (
    evaluate,
    interpolate,
    interpolate_coefficients,
)


class FieldAndPolynomialTests(unittest.TestCase):
    def test_prime_and_inverse(self):
        self.assertTrue(is_prime(41))
        self.assertFalse(is_prime(39))
        self.assertEqual(37 * inverse(37, 101) % 101, 1)

    def test_signed_encoding(self):
        self.assertEqual(encode_signed(-5, 41), 36)
        self.assertEqual(decode_signed(36, 41), -5)
        self.assertEqual(decode_signed(20, 41), 20)
        self.assertEqual(decode_signed(21, 41), -20)

    def test_horner_evaluation(self):
        # f(x) = 1 + 2x + 3x^2, so f(2) = 17.
        self.assertEqual(evaluate([1, 2, 3], 2, 101), 17)

    def test_interpolation(self):
        coefficients = [1, 2, 3]
        points = [(x, evaluate(coefficients, x, 101)) for x in (1, 2, 3)]
        self.assertEqual(interpolate(points, 0, 101), 1)
        self.assertEqual(interpolate_coefficients(points, 101), coefficients)

    def test_duplicate_points_are_rejected(self):
        with self.assertRaises(ValueError):
            interpolate([(1, 2), (1, 3)], 0, 41)


if __name__ == "__main__":
    unittest.main()
