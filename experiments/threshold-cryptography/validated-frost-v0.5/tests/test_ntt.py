import unittest
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.ntt import inverse_ntt, ntt


class NttTests(unittest.TestCase):
    def test_order_eight_round_trip(self):
        values = list(range(8))
        self.assertEqual(inverse_ntt(ntt(values, 354, 433), 354, 433), values)

    def test_order_nine_round_trip(self):
        values = list(range(9))
        self.assertEqual(inverse_ntt(ntt(values, 150, 433), 150, 433), values)


if __name__ == "__main__":
    unittest.main()
