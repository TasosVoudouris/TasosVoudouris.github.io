"""Checks for part 03: the nine verdicts the article quotes."""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("ct03", HERE / "03_ct_toy.py")
ct = importlib.util.module_from_spec(spec)
sys.modules["ct03"] = ct
spec.loader.exec_module(ct)

EXPECTED = [
    ("ACCEPT", "nothing"),   # 1 honest
    ("ACCEPT", "nothing"),   # 2 rogue, no CT: silent success, the DigiNotar world
    ("REJECT", "nothing"),   # 3 rogue, CT browser, no SCTs
    ("ACCEPT", "ALERT"),     # 4 rogue, logged: accepted but detected
    ("REJECT", "ALERT"),     # 5 one operator only
    ("REJECT", "ALERT"),     # 6 forged SCT
    ("ACCEPT", "ALERT"),     # 7 one dishonest log is not enough
    ("ACCEPT", "nothing"),   # 8 every SCT-issuing log lies: the gap Merkle proofs close
    ("REJECT", "nothing"),   # 9 distrust keyed on SCT time defeats backdating
]


class Verdicts(unittest.TestCase):
    def test_all_nine(self):
        got = ct.scenarios()
        self.assertEqual(len(got), 9)
        for (label, verdict, why, seen), (want_v, want_seen) in zip(got, EXPECTED):
            self.assertEqual(verdict, want_v, label)
            self.assertTrue(seen.startswith(want_seen), label)

    def test_unknown_log_counts_for_nothing(self):
        _, inter_sk, roots, inter, logs = ct.world()
        leaf = ct.issue("Toy Issuing CA", inter_sk, "example.com", ct.key("example.com").public_key(), 47, False)
        rogue_log = ct.Log("shadow", "Mallory Inc", ct.key("shadow"))
        scts = [logs["argon"].submit(leaf, ct.NOW), rogue_log.submit(leaf, ct.NOW)]
        ok, why = ct.Browser(roots, ct.known(logs)).check([leaf, inter], scts, "example.com")
        self.assertFalse(ok)
        self.assertIn("only 1 valid SCT", why)

    def test_honest_log_publishes_by_the_deadline(self):
        _, inter_sk, _, _, logs = ct.world()
        leaf = ct.issue("Toy Issuing CA", inter_sk, "example.com", ct.key("example.com").public_key(), 47, False)
        log = logs["oak"]
        log.submit(leaf, ct.NOW)
        log.tick(ct.NOW + ct.MMD - 1)
        self.assertEqual(log.published, [])
        log.tick(ct.NOW + ct.MMD)
        self.assertEqual(log.published, [leaf])


if __name__ == "__main__":
    unittest.main()
