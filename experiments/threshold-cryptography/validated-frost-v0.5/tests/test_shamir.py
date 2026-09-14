import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.polynomial import evaluate, interpolate_coefficients
from cryptocave_sss.shamir import Share, ShamirScheme


class ShamirTests(unittest.TestCase):
    def setUp(self):
        self.scheme = ShamirScheme(41, 10, 5, rng=random.Random(200))

    def test_threshold_means_five_shares(self):
        self.assertEqual(self.scheme.threshold, 5)
        self.assertEqual(self.scheme.degree, 4)

    def test_every_five_share_subset_reconstructs(self):
        sharing = self.scheme.share(17)
        subsets_checked = 0
        for subset in combinations(sharing.shares, 5):
            self.assertEqual(sharing.reveal(subset), 17)
            subsets_checked += 1
        self.assertEqual(subsets_checked, 252)

    def test_four_shares_are_insufficient(self):
        sharing = self.scheme.share(17)
        with self.assertRaises(ValueError):
            sharing.reveal(sharing.shares[:4])

    def test_four_shares_are_compatible_with_every_secret(self):
        sharing = self.scheme.share(17)
        known = sharing.shares[:4]

        for guessed_secret in range(41):
            points = [(0, guessed_secret)] + [(share.x, share.y) for share in known]
            polynomial = interpolate_coefficients(points, 41)
            self.assertLessEqual(len(polynomial) - 1, 4)
            for share in known:
                self.assertEqual(evaluate(polynomial, share.x, 41), share.y)

    def test_signed_secret_and_linear_operations(self):
        x = self.scheme.share(-5)
        y = self.scheme.share(8)
        self.assertEqual(x.reveal(x.shares[:5]), -5)
        self.assertEqual((x + y).reveal((x + y).shares[:5]), 3)
        self.assertEqual((x - y).reveal((x - y).shares[:5]), -13)
        self.assertEqual(x.scale(2).reveal(x.scale(2).shares[:5]), -10)

    def test_labels_are_not_implicit_list_positions(self):
        sharing = self.scheme.share(9)
        reordered = tuple(reversed(sharing.shares[:5]))
        self.assertEqual(sharing.reveal(reordered), 9)

    def test_duplicate_identifiers_are_rejected(self):
        sharing = self.scheme.share(9)
        duplicate = [sharing.shares[0], Share(sharing.shares[0].x, 4), *sharing.shares[2:6]]
        with self.assertRaises(ValueError):
            sharing.reveal(duplicate)


if __name__ == "__main__":
    unittest.main()
