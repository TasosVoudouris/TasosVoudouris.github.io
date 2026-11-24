"""Checks for part 09: tile paths, layout, the writer, the client, tampering, the measurements."""
import importlib.util
import pathlib
import random
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("m09", HERE / "09_tiles.py")
m9 = importlib.util.module_from_spec(spec)
sys.modules["m09"] = m9
spec.loader.exec_module(m9)
mk, m8 = m9.mk, m9.m8


def make_log(n, seed=1):
    rnd = random.Random(seed)
    log = m9.TiledLog()
    while len(log.entries) < n:
        k = min(rnd.randint(1, 700), n - len(log.entries))
        log.append([f"e{len(log.entries) + i}".encode() * rnd.randint(1, 4) for i in range(k)])
        log.publish()
    return log


class Paths(unittest.TestCase):
    def test_spec_and_tessera_examples(self):
        self.assertEqual(m9.tile_path(0, 1234067, 8), "tile/0/x001/x234/067.p/8")
        self.assertEqual(m9.entries_path(1234067, 8), "tile/entries/x001/x234/067.p/8")
        self.assertEqual(m9.tile_path(0, 1234067), "tile/0/x001/x234/067")
        self.assertEqual(m9.node_to_tile(8, 123456789), (1, 482253, 0, 21))

    def test_n_path(self):
        self.assertEqual(m9.n_path(0), "000")
        self.assertEqual(m9.n_path(999), "999")
        self.assertEqual(m9.n_path(1000), "x001/000")
        self.assertEqual(m9.n_path(10**9), "x001/x000/x000/000")

    def test_parse_roundtrip_and_rejects(self):
        for level, idx, w in ((0, 0, 256), (3, 1234567890, 17), (63, 5, 255)):
            p = m9.tile_path(level, idx, w)
            self.assertEqual(m9.parse_tile_path(p), (str(level), idx, w))
        for bad in ("tile/00/000", "tile/0/01", "tile/0/x01/000", "tile/0/000.p/0", "tile/0/000.p/256",
                    "tile/0/000.p/08", "tile/64/000", "tile/0/x000/001"):
            with self.assertRaises(ValueError, msg=bad):
                m9.parse_tile_path(bad)

    def test_layout_spec_example(self):
        lay = m9.layout(70000)
        self.assertEqual(sum(1 for l, _, w in lay if l == 0 and w == 256), 273)
        self.assertIn((0, 273, 112), lay)
        self.assertIn((1, 0, 256), lay)
        self.assertIn((1, 1, 17), lay)
        self.assertIn((2, 0, 1), lay)
        self.assertEqual(len(lay), 277)
        self.assertEqual(m9.layout(0), [])
        self.assertEqual(m9.layout(256), [(0, 0, 256), (1, 0, 1)])


class LogAndClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = make_log(9000)

    def client(self, files=None):
        c = m9.TileClient(m9.FetchCounter(files or self.log.files), self.log.verifier)
        c.update()
        return c

    def test_root_and_files(self):
        self.assertEqual(self.log.range_hash(0, 9000), mk.mth(self.log.entries))
        for level, index, width in m9.layout(9000):
            self.assertEqual(len(self.log.files[m9.tile_path(level, index, width)]), 32 * width)

    def test_full_tiles_immutable(self):
        with self.assertRaises(AssertionError):
            self.log._put(m9.tile_path(0, 0), bytes(8192), False)

    def test_proofs_equal_part04(self):
        c = self.client()
        e = self.log.entries
        for i in (0, 1, 255, 256, 4097, 8999):
            self.assertEqual(c.inclusion(i, 0, 9000), mk.path(i, e))
            self.assertEqual(c.entry(i), e[i])
        for m in (1, 255, 256, 1000, 4096, 8191, 8999):
            self.assertEqual(c.consistency(m, 9000), mk.proof(m, e))

    def test_subtree_proofs_equal_part08(self):
        c = self.client()
        e = self.log.entries
        for s in ((0, 8192), (8192, 8960), (4096, 6144), (8960, 9000), (8999, 9000)):
            self.assertEqual(c.subtree_proof(*s, 9000), m8.subtree_proof(*s, e))
            self.assertEqual(c.range_hash(*s), mk.mth(e[s[0]:s[1]]))

    def test_tampering(self):
        bad = dict(self.log.files)
        p = m9.tile_path(0, 3)
        bad[p] = bytes(32) + bad[p][32:]
        with self.assertRaises(ValueError):
            self.client(bad).inclusion(3 * 256 + 9, 0, 9000)
        bad = dict(self.log.files)
        edge = m9.tile_path(0, 9000 // 256, 9000 % 256)
        bad[edge] = bytes(32) + bad[edge][32:]
        with self.assertRaises(ValueError):
            self.client(bad)                                 # right edge checked against the root
        bad = dict(self.log.files)
        p = m9.entries_path(2)
        bad[p] = bad[p][:-1]
        with self.assertRaises(ValueError):
            self.client(bad).entry(2 * 256)
        bad = dict(self.log.files)
        bad[p] = bytes(2) + bad[p][2:]                       # a zero length prefix changes the framing
        with self.assertRaises(ValueError):
            self.client(bad).entry(2 * 256 + 5)

    def test_old_checkpoint_still_served(self):
        log = m9.TiledLog()
        log.append([b"a%d" % i for i in range(300)])
        old_note = log.publish()
        log.append([b"b%d" % i for i in range(300)])
        log.publish()
        files = dict(log.files)
        files["checkpoint"] = old_note.encode()              # a client still on the older checkpoint
        c = m9.TileClient(m9.FetchCounter(files), log.verifier)
        self.assertEqual(c.update()[0], 300)
        self.assertEqual(c.inclusion(299, 0, 300), mk.path(299, log.entries[:300]))


class Measurements(unittest.TestCase):
    def test_monitor_cost(self):
        self.assertGreater(m9.monitor_cost(10), 10)
        self.assertLess(m9.monitor_cost(3000), 1.05)
        for per in (10, 75, 200, 3000):
            self.assertLess(m9.monitor_cost(per, skip_partials=True), m9.monitor_cost(per))
        self.assertAlmostEqual(m9.monitor_cost(256), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
