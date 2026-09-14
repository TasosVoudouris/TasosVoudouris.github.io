import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.mpc import beaver_multiply, generate_beaver_triple
from cryptocave_sss.shamir import ShamirScheme


class MultiplicationTests(unittest.TestCase):
    def setUp(self):
        self.scheme = ShamirScheme(41, 10, 5, rng=random.Random(300))

    def test_pointwise_product_has_degree_eight(self):
        x = self.scheme.share(7)
        y = self.scheme.share(6)
        product = x * y
        self.assertEqual(product.degree_bound, 8)
        self.assertEqual(product.reconstruction_threshold, 9)

        for subset in combinations(product.shares, 9):
            self.assertEqual(product.reveal_field_element(subset), 1)  # 42 mod 41

        with self.assertRaises(ValueError):
            product.reveal(product.shares[:5])

    def test_beaver_product_returns_to_degree_four(self):
        x = self.scheme.share(7)
        y = self.scheme.share(6)
        triple = generate_beaver_triple(self.scheme)
        product = beaver_multiply(x, y, triple)

        self.assertEqual(product.degree_bound, 4)
        for subset in combinations(product.shares, 5):
            self.assertEqual(product.reveal_field_element(subset), 1)


if __name__ == "__main__":
    unittest.main()
