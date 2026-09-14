import random
import sys
import unittest
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.additive import (
    AdditiveSecret,
    additive_reconstruct,
    additive_share,
    explain_missing_share,
)


class AdditiveSharingTests(unittest.TestCase):
    def setUp(self):
        self.modulus = 41
        self.rng = random.Random(100)

    def test_reconstruction(self):
        shares = additive_share(-5, 10, self.modulus, self.rng)
        self.assertEqual(additive_reconstruct(shares, self.modulus), 36)

    def test_every_secret_has_an_explanation(self):
        shares = additive_share(5, 10, self.modulus, self.rng)
        known = shares[:-1]
        for guessed_secret in range(self.modulus):
            missing = explain_missing_share(known, guessed_secret, self.modulus)
            self.assertEqual(
                additive_reconstruct([*known, missing], self.modulus), guessed_secret
            )

    def test_linear_operations(self):
        x = AdditiveSecret.from_secret(5, 4, self.modulus, self.rng)
        y = AdditiveSecret.from_secret(8, 4, self.modulus, self.rng)
        self.assertEqual((x + y).reveal(), 13)
        self.assertEqual((x - y).reveal(), -3)
        self.assertEqual(x.scale(3).reveal(), 15)


if __name__ == "__main__":
    unittest.main()
