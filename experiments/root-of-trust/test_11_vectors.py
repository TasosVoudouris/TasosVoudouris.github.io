"""Checks for part 11: the vector file is reproducible and agrees with the Python reference."""
import importlib.util
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("m11", HERE / "11_vectors.py")
m11 = importlib.util.module_from_spec(spec)
sys.modules["m11"] = m11
spec.loader.exec_module(m11)
mk, m7, m8, m9 = m11.mk, m11.m7, m11.m8, m11.m9


class Vectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = json.loads(m11.OUT.read_text(encoding="utf-8"))

    def test_reproducible(self):
        self.assertEqual(m11.dump(m11.build()), m11.OUT.read_text(encoding="utf-8"))

    def test_proofs_verify(self):
        d = [bytes([i]) for i in range(20)]
        roots = [bytes.fromhex(t["hash"]) for t in self.v["merkle"]["tree_hash"]]
        for t in self.v["merkle"]["inclusion"]:
            p = [bytes.fromhex(x) for x in t["proof"]]
            self.assertTrue(mk.verify_inclusion(mk.leaf_hash(d[t["index"]]), t["index"], t["n"], p, roots[t["n"]]))
        for t in self.v["merkle"]["consistency"]:
            p = [bytes.fromhex(x) for x in t["proof"]]
            self.assertTrue(mk.verify_consistency(t["m"], t["n"], roots[t["m"]], roots[t["n"]], p))
        for t in self.v["subtrees"]["consistency"]:
            p = [bytes.fromhex(x) for x in t["proof"]]
            s, e, n = t["start"], t["end"], t["n"]
            self.assertTrue(m8.verify_subtree_consistency(n, s, e, p, mk.mth(d[s:e]), roots[n]))

    def test_appendix_c_matches_the_draft(self):
        c = self.v["subtrees"]["appendix_c"]
        self.assertEqual(c["C.1.1"], "b82806ad4265bb151c1119c0f4db437bb4d1a1f887b3a7fba1cd4ebf552e3e81")
        self.assertEqual(c["C.1.3"], "10fa99b37bf9bf9ffa26b412fbd98bd75363256d0b75d61bc4538b9c9c5a0a74")

    def test_landmark_certificate(self):
        c = self.v["mtc"]["landmark_relative_certificate"]
        cert = bytes.fromhex(c["der"])
        rp = m7.RelyingParty({}, b"", trusted_subtrees={(c["start"], c["end"]): bytes.fromhex(c["trusted_subtree_hash"])})
        self.assertIn("landmark", rp.verify(cert))
        self.assertEqual(len(cert), 1855)

    def test_no_randomness(self):
        text = m11.OUT.read_text(encoding="utf-8")
        self.assertNotIn("signature\": \"" + "00" * 2420, text)
        self.assertEqual(self.v["version"], 1)


if __name__ == "__main__":
    unittest.main()
