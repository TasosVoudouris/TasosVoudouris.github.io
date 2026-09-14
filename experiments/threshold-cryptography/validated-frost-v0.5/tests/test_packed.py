import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.packed import PackedRampScheme
from cryptocave_sss.shamir import Share


class PackedRampTests(unittest.TestCase):
    def setUp(self):
        self.scheme = PackedRampScheme.original_parameters(random.Random(500))

    def test_original_parameters_are_three_four_seven_eight(self):
        self.assertEqual(self.scheme.num_secrets, 3)
        self.assertEqual(self.scheme.privacy_threshold, 4)
        self.assertEqual(self.scheme.reconstruction_threshold, 7)
        self.assertEqual(len(self.scheme.share_points), 8)

    def test_any_seven_shares_reconstruct(self):
        sharing = self.scheme.share([1, 2, 3])
        for subset in combinations(sharing.shares, 7):
            self.assertEqual(sharing.reveal(subset), [1, 2, 3])

    def test_six_shares_do_not_reconstruct(self):
        sharing = self.scheme.share([1, 2, 3])
        with self.assertRaises(ValueError):
            sharing.reveal(sharing.shares[:6])

    def test_exact_coalition_leakage_dimensions(self):
        identifiers = self.scheme.share_points
        for size, expected_dimension in ((4, 0), (5, 1), (6, 2), (7, 3)):
            for coalition in combinations(identifiers, size):
                self.assertEqual(
                    self.scheme.coalition_leakage_dimension(coalition),
                    expected_dimension,
                )

    def test_redundant_eighth_share_detects_corruption(self):
        sharing = self.scheme.share([1, 2, 3])
        received = list(sharing.shares)
        received[-1] = Share(received[-1].x, (received[-1].y + 1) % 433)
        with self.assertRaises(ValueError):
            sharing.reveal(received)


if __name__ == "__main__":
    unittest.main()
