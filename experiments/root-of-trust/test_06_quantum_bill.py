"""Checks for part 06: the model reproduces Part 02, and the optimizer's answers are stable."""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("qb06", HERE / "06_quantum_bill.py")
qb = importlib.util.module_from_spec(spec)
sys.modules["qb06"] = qb
spec.loader.exec_module(qb)

SCHEMES, _ = qb.catalog(measure=False)  # the fixed table: same answer on every machine
BY = {s.name: s for s in SCHEMES}
FIPS = lambda s: s.status.startswith("FIPS")
STD = lambda s: s.status.startswith("FIPS") or s.status.startswith("draft FIPS")
ANY = lambda s: s.level >= 1


class Model(unittest.TestCase):
    def test_reproduces_part02(self):
        for name, auth, flight in (("ML-DSA-44", 15802, 17169), ("ML-DSA-65", 21527, 22916)):
            s = BY[name]
            a = qb.Assignment(s, s, s, s)
            self.assertEqual((a.auth, a.flight), (auth, flight))

    def test_roles(self):
        m = BY["ML-DSA-44"]
        lean = qb.Assignment(m, m, m, m, send_intermediate=False)
        self.assertEqual(lean.auth, 15802 - 1312 - 2420)  # no intermediate key, no root signature

    def test_sizes_are_the_specs(self):
        self.assertEqual((BY["ML-DSA-44"].pk, BY["ML-DSA-44"].sig), (1312, 2420))
        self.assertEqual((BY["SLH-DSA-SHA2-128s"].pk, BY["SLH-DSA-SHA2-128s"].sig), (32, 7856))
        self.assertEqual((BY["Falcon-512"].pk, round(BY["Falcon-512"].sig)), (897, 655))


class Optimizer(unittest.TestCase):
    def test_fips_only(self):
        a = qb.best(SCHEMES, FIPS)
        self.assertEqual(a.label(), "ML-DSA-44 everywhere")
        self.assertEqual(a.auth, 15802)

    def test_slh_dsa_never_signs_online(self):
        a = qb.best(SCHEMES, lambda s: s.name.startswith("SLH"))
        self.assertIsNone(a)  # 128s is too slow for any signing role, 128f too slow for the leaf

    def test_with_falcon(self):
        self.assertEqual(qb.best(SCHEMES, STD).label(), "Falcon-512 everywhere")
        a = qb.best(SCHEMES, STD, leaf_allowed=lambda s: not s.name.startswith("Falcon"))
        self.assertEqual(a.leaf.name, "ML-DSA-44")
        self.assertEqual(a.inter.name, "Falcon-512")

    def test_candidates(self):
        a = qb.best(SCHEMES, ANY, stored_pk_max=65536)
        self.assertEqual((a.root.name, a.log.name), ("UOV-Ip-pkc", "UOV-Ip-pkc"))
        self.assertLess(a.flight, qb.QUIC_BUDGET)


if __name__ == "__main__":
    unittest.main()
