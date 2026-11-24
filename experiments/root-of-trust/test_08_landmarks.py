"""Checks for part 08: subtree consistency proofs, the draft's vectors, landmark validation, staleness."""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("m08", HERE / "08_landmarks.py")
m8 = importlib.util.module_from_spec(spec)
sys.modules["m08"] = m8
spec.loader.exec_module(m8)
mk, m7 = m8.mk, m8.m7
HOUR = m8.HOUR


class Proofs(unittest.TestCase):
    d14 = [bytes([i]) for i in range(14)]

    def h(self, a, b):
        return mk.mth(self.d14[a:b])

    def test_draft_examples(self):
        self.assertEqual(m8.subtree_proof(4, 8, self.d14), [self.h(0, 4), self.h(8, 14)])
        self.assertEqual(m8.subtree_proof(8, 13, self.d14), [self.h(12, 13), self.h(13, 14), self.h(8, 12), self.h(0, 8)])

    def test_special_cases(self):
        d = [bytes([i]) for i in range(40)]
        for n in range(1, 41):
            for end in range(1, n + 1):
                self.assertEqual(m8.subtree_proof(0, end, d[:n]), mk.proof(end, d[:n]))
            for i in range(n):
                self.assertEqual(m8.subtree_proof(i, i + 1, d[:n]), mk.path(i, d[:n]))

    def test_appendix_c(self):
        for name, want in m8.APPENDIX_C.items():
            self.assertEqual(m8.appendix_c1(name), want, name)

    def test_verify_exhaustive(self):
        d = [bytes([i]) for i in range(41)]
        for n in range(1, 41):
            root = mk.mth(d[:n])
            for end in range(n + 1):
                for start in range(end + 1):
                    if not m7.valid_subtree(start, end):
                        continue
                    p = m8.subtree_proof(start, end, d[:n])
                    node = mk.mth(d[start:end])
                    self.assertTrue(m8.verify_subtree_consistency(n, start, end, p, node, root), (n, start, end))
                    if p:
                        self.assertFalse(m8.verify_subtree_consistency(n, start, end, p[:-1], node, root))
                        self.assertFalse(m8.verify_subtree_consistency(n, start, end, p + [p[0]], node, root))
                    if end > start:
                        self.assertFalse(m8.verify_subtree_consistency(n, start, end, p, root if node != root else bytes(32), root))
                        self.assertFalse(m8.verify_subtree_consistency(n + 1, start, end, p, node, mk.mth(d[: n + 1])))

    def test_invalid_subtree_rejected(self):
        self.assertFalse(m8.verify_subtree_consistency(14, 3, 6, [], b"", b""))

    def test_trace(self):
        tr = []
        self.assertTrue(m8.verify_subtree_consistency(14, 8, 13, m8.subtree_proof(8, 13, self.d14),
                                                      self.h(8, 13), self.h(0, 14), tr))
        self.assertEqual([t[0] for t in tr], ["start", "right", "left", "left"])


class Landmarks(unittest.TestCase):
    def service(self, ca, **kw):
        return m8.UpdateService({c.id_bytes: (c.arcs, c.sk.public_key()) for c in ca.cosigners},
                                ca.cosigners[0].id_bytes, **kw)

    def draft_example(self):
        ca = m8.LandmarkCA()
        for i, size in enumerate((200, 300, 400, 500), 1):
            ca.grow(size - len(ca.entries))
            ca.allocate_landmark(i * HOUR)
        ca.cosigners[0].mirror = list(ca.entries)
        for c in ca.cosigners[1:]:
            c.mirror = list(ca.entries[:350])
        return ca

    def test_allocation(self):
        ca = m8.LandmarkCA()
        ca.grow(10)
        self.assertIsNotNone(ca.allocate_landmark(HOUR))
        self.assertIsNone(ca.allocate_landmark(2 * HOUR))          # no growth, no landmark
        sizes = [l.tree_size for l in ca.landmarks]
        self.assertEqual(sizes, sorted(set(sizes)))

    def test_week_bound(self):
        ca = m8.LandmarkCA()
        for hour in range(1, 24 * 9 + 1):
            ca.grow(5)
            ca.allocate_landmark(hour * HOUR)
            self.assertLessEqual(len(ca.active(hour * HOUR)), 169)
        self.assertTrue(all(len(ca.subtrees(l)) <= 2 for l in ca.landmarks[1:]))

    def test_draft_example_350(self):
        ca = self.draft_example()
        svc = self.service(ca)
        trusted, notes = svc.validate(m8.make_bundle(ca, 5 * HOUR, reference_size=500))
        self.assertEqual(trusted, [])
        trusted, notes = svc.validate(m8.make_bundle(ca, 5 * HOUR, reference_size=350))
        kept = {s for s, _ in trusted}
        self.assertEqual(kept, {s for l in ca.landmarks[1:3] for s in ca.subtrees(l)})

    def test_forged_landmark_discards_newer(self):
        ca = self.draft_example()
        for c in ca.cosigners:
            c.mirror = list(ca.entries)
        b = m8.make_bundle(ca, 5 * HOUR)
        s, _ = b.subtrees[2][0]
        b.subtrees[2][0] = (s, bytes(32))
        trusted, _ = self.service(ca).validate(b)
        self.assertEqual({x for x, _ in trusted}, set(ca.subtrees(ca.landmarks[1])))

    def test_witness_refuses_fork(self):
        ca = m8.LandmarkCA()
        ca.grow(99)
        w = ca.cosigners[1]
        w.mirror = list(ca.entries)
        ca.entries[10] = m7.mtc_log_entry(b"rewritten")
        with self.assertRaises(ValueError):
            m8.cosign_checkpoint(w, 100, mk.mth(ca.entries), 1)

    def test_cap_keeps_oldest(self):
        ca = m8.LandmarkCA()
        for hour in range(1, 30):
            ca.grow(7)
            ca.allocate_landmark(hour * HOUR)
        for c in ca.cosigners:
            c.mirror = list(ca.entries)
        trusted, _ = self.service(ca, max_landmarks=10).validate(m8.make_bundle(ca, 30 * HOUR))
        self.assertEqual({s for s, _ in trusted}, {s for l in ca.landmarks[1:11] for s in ca.subtrees(l)})

    def test_trusted_subtree_verifies_an_entry(self):
        ca = self.draft_example()
        for c in ca.cosigners:
            c.mirror = list(ca.entries)
        trusted, _ = self.service(ca).validate(m8.make_bundle(ca, 5 * HOUR))
        (start, end), h = trusted[3]
        idx = start + 1
        got = m7._evaluate(mk.leaf_hash(ca.entries[idx]), idx - start, end - start,
                           m8.subtree_inclusion(start, end, idx, ca.entries))
        self.assertEqual(got, h)


class Staleness(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(m8.lr_share(0), 1.0)
        self.assertEqual(m8.lr_share(40), 1.0)                    # 168 - 126 = 42 h of overlap, minus the delays
        self.assertEqual(m8.lr_share(168), 0.0)
        vals = [m8.lr_share(s, trials=4000) for s in range(40, 170, 16)]
        self.assertEqual(vals, sorted(vals, reverse=True))
        self.assertAlmostEqual(m8.lr_share(96, trials=20000), (168 - 96 - 1.5) / 126, delta=0.02)

    def test_expected_auth(self):
        self.assertEqual(m8.expected_auth(1.0), 4296)
        self.assertEqual(m8.expected_auth(0.0), 11417)


if __name__ == "__main__":
    unittest.main()
