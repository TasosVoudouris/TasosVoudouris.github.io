"""Checks for part 10: which commit protocols fork, which get stuck, and why."""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("m10", HERE / "10_never_fork.py")
m10 = importlib.util.module_from_spec(spec)
sys.modules["m10"] = m10
spec.loader.exec_module(m10)

SEEDS = range(6)


def runs(protocol, scenario, immutable=False):
    return [m10.run(protocol, scenario, s, immutable=immutable) for s in SEEDS]


class Protocols(unittest.TestCase):
    def test_no_fault_is_safe_everywhere(self):
        for p in m10.PROTOCOLS:
            r = m10.run(p, "none", 0)
            self.assertEqual((r["outcome"], r["visible_forks"], r["signed_forks"], r["lost"]), ("ok", 0, 0, 0), p)
            self.assertEqual(r["world"].visible[-1][0], len(r["world"].acked))

    def test_naive_forks_on_a_crash(self):
        self.assertTrue(all(r["visible_forks"] for r in runs("naive", "crash:tiles")))

    def test_lock_protocols_never_fork_on_crashes(self):
        for p in ("sunlight", "staged", "lock first"):
            for step in m10.PROTOCOLS[p]:
                for r in runs(p, f"crash:{step}"):
                    self.assertEqual(r["signed_forks"], 0, (p, step))
                    self.assertEqual(r["lost"], 0, (p, step))

    def test_sunlight_and_staged_recover_by_themselves(self):
        for p in ("sunlight", "staged"):
            for step in m10.PROTOCOLS[p]:
                for r in runs(p, f"crash:{step}"):
                    self.assertEqual(r["outcome"], "ok", (p, step))

    def test_lock_first_gets_stuck(self):
        self.assertTrue(all(r["outcome"].startswith("stuck") for r in runs("lock first", "crash:tiles")))

    def test_conditional_writes(self):
        stuck = [r for r in runs("sunlight", "crash:lock", immutable=True) if r["outcome"].startswith("stuck")]
        self.assertTrue(stuck)                                     # Sunlight issue #12
        self.assertTrue(all(r["signed_forks"] == 0 for r in stuck))
        for step in m10.PROTOCOLS["staged"]:
            for r in runs("staged", f"crash:{step}", immutable=True):
                self.assertEqual(r["outcome"], "ok", step)

    def test_rollback_and_twin(self):
        for sc in ("rollback", "twin"):
            for r in runs("tiles first", sc):
                self.assertGreater(r["visible_forks"], 0, sc)
            for p in ("sunlight", "staged", "lock first"):
                for r in runs(p, sc):
                    self.assertTrue(r["outcome"].startswith("stuck"), (p, sc))
                    self.assertEqual(r["signed_forks"], 0, (p, sc))

    def test_reused_key(self):
        self.assertEqual(m10.reused_key("tiles first")["forked"], 1)
        r = m10.reused_key("sunlight")
        self.assertEqual((r["forked"], r["stuck"]), (0, 1))

    def test_forks_referee(self):
        w = m10.World(m10.Store(), m10.Lock())
        self.assertEqual(w.forks([(2, b"", (b"a", b"b")), (3, b"", (b"a", b"b", b"c"))]), 0)
        self.assertEqual(w.forks([(2, b"", (b"a", b"b")), (3, b"", (b"a", b"x", b"c"))]), 1)
        self.assertEqual(w.forks([(2, b"", (b"a", b"b")), (2, b"", (b"a", b"c"))]), 1)


if __name__ == "__main__":
    unittest.main()
