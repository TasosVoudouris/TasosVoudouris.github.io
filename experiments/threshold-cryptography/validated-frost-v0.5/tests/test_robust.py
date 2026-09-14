import random
import sys
import unittest
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.robust import check_consistency, robust_reconstruct
from cryptocave_sss.shamir import Share, ShamirScheme


class RobustReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.scheme = ShamirScheme(41, 10, 5, rng=random.Random(400))
        self.sharing = self.scheme.share(12)

    @staticmethod
    def corrupt(share: Share, amount: int = 1) -> Share:
        return Share(share.x, (share.y + amount) % 41)

    def test_consistency_check_uses_redundancy(self):
        self.assertTrue(check_consistency(self.scheme, self.sharing.shares[:6]))
        bad = [*self.sharing.shares]
        bad[8] = self.corrupt(bad[8])
        self.assertFalse(check_consistency(self.scheme, bad))
        with self.assertRaises(ValueError):
            self.scheme.reconstruct(bad)

    def test_two_errors_can_be_corrected_with_ten_shares(self):
        received = [*self.sharing.shares]
        received[1] = self.corrupt(received[1], 3)
        received[7] = self.corrupt(received[7], 5)
        result = robust_reconstruct(self.scheme, received, max_errors=2)
        self.assertEqual(result.secret, 12)
        self.assertEqual(len(result.rejected_shares), 2)

    def test_correction_bound_is_enforced(self):
        with self.assertRaises(ValueError):
            robust_reconstruct(self.scheme, self.sharing.shares[:8], max_errors=2)

    def test_exactly_five_shares_cannot_detect_one_bad_share(self):
        received = [*self.sharing.shares[:5]]
        received[0] = self.corrupt(received[0])
        self.assertNotEqual(self.scheme.reconstruct(received), 12)


if __name__ == "__main__":
    unittest.main()
