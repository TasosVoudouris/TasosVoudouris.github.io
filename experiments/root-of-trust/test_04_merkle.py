"""Checks for part 04: test vectors, the RFC's worked examples, proofs, attacks."""
import importlib.util
import pathlib
import random
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("mk04", HERE / "04_merkle.py")
mk = importlib.util.module_from_spec(spec)
sys.modules["mk04"] = mk
spec.loader.exec_module(mk)


class Tree(unittest.TestCase):
    def test_vectors(self):
        for n, want in enumerate(mk.TEST_ROOTS):
            self.assertEqual(mk.mth(mk.TEST_LEAVES[:n]), want, n)

    def test_split(self):
        self.assertEqual([mk.split(n) for n in range(2, 10)], [1, 2, 2, 4, 4, 4, 4, 8])

    def test_rfc_examples(self):
        self.assertEqual(mk.rfc6962_example(), {
            "PATH(0)": ["b", "h", "l"], "PATH(3)": ["c", "g", "l"],
            "PATH(4)": ["f", "j", "k"], "PATH(6)": ["i", "k"],
            "PROOF(3)": ["c", "d", "g", "l"], "PROOF(4)": ["l"], "PROOF(6)": ["i", "j", "k"],
        })


class Proofs(unittest.TestCase):
    def test_exhaustive_small(self):
        for n in range(1, 40):
            d = [f"x{i}".encode() for i in range(n)]
            root = mk.mth(d)
            for m in range(n):
                self.assertTrue(mk.verify_inclusion(mk.leaf_hash(d[m]), m, n, mk.path(m, d), root))
                self.assertEqual(len(mk.path(m, d)), len(mk.path(m, d)))
            for m in range(n + 1):
                self.assertTrue(mk.verify_consistency(m, n, mk.mth(d[:m]), root, mk.proof(m, d)))

    def test_random_large(self):
        rng = random.Random(4)
        d = [rng.randbytes(20) for _ in range(3000)]
        root = mk.mth(d)
        for _ in range(30):
            m = rng.randrange(3000)
            self.assertTrue(mk.verify_inclusion(mk.leaf_hash(d[m]), m, 3000, mk.path(m, d), root))
            k = rng.randrange(1, 3000)
            self.assertTrue(mk.verify_consistency(k, 3000, mk.mth(d[:k]), root, mk.proof(k, d)))

    def test_rejections(self):
        d = [f"x{i}".encode() for i in range(13)]
        root, p = mk.mth(d), mk.path(5, d)
        self.assertFalse(mk.verify_inclusion(mk.leaf_hash(b"not there"), 5, 13, p, root))
        self.assertFalse(mk.verify_inclusion(mk.leaf_hash(d[5]), 5, 13, p[:-1], root))  # too short
        self.assertFalse(mk.verify_inclusion(mk.leaf_hash(d[5]), 5, 13, p + [root], root))  # too long
        self.assertFalse(mk.verify_inclusion(mk.leaf_hash(d[5]), 5, 8, p, root))  # size with another shape
        # A size with the same shape along this leaf's path passes! The proof binds the leaf to
        # the root; only the log's signature over (size, root) binds the size. Part 04 explains.
        self.assertTrue(mk.verify_inclusion(mk.leaf_hash(d[5]), 5, 12, p, root))
        self.assertFalse(mk.verify_inclusion(mk.leaf_hash(d[5]), 13, 13, p, root))  # index out of range
        changed = d[:3] + [b"rewritten"] + d[4:]
        self.assertFalse(mk.verify_consistency(7, 13, mk.mth(d[:7]), mk.mth(changed), mk.proof(7, changed)))
        self.assertFalse(mk.verify_consistency(7, 13, mk.mth(d[:7]), root, []))

    def test_sizes(self):
        d = [f"e{i}".encode() for i in range(1000)]
        self.assertEqual(len(mk.path(637, d)), 10)
        self.assertEqual(len(mk.proof(600, d)), 8)
        for n in range(4, 600):
            self.assertEqual(mk.worst_consistency(n), (n - 1).bit_length() + 1)


class Attacks(unittest.TestCase):
    def test_second_preimage(self):
        r = mk.second_preimage_demo()
        self.assertTrue(r["naive_equal"])
        self.assertFalse(r["rfc6962_equal"])

    def test_log_scenarios(self):
        verdicts = [v for _, v in mk.log_scenarios()]
        self.assertEqual(len(verdicts), 4)
        self.assertNotIn("??", " ".join(verdicts))


if __name__ == "__main__":
    unittest.main()
