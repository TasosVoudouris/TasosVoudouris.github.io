"""Checks for part 05: the spec's test vector, the witness checks, the scenarios, the quorum rule."""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("w05", HERE / "05_witness.py")
w5 = importlib.util.module_from_spec(spec)
sys.modules["w05"] = w5
spec.loader.exec_module(w5)


class Formats(unittest.TestCase):
    def test_spec_vector(self):
        v = w5.Verifier.parse(w5.SPEC_VKEY)
        text, good = w5.open_note(w5.SPEC_NOTE, [v])
        self.assertEqual(text, "This is an example message.\n")
        tampered = w5.SPEC_NOTE.replace("example message", "exemplary message")
        with self.assertRaises(ValueError):
            w5.open_note(tampered, [v])

    def test_unknown_keys_are_ignored(self):
        log, _ = w5.world()
        note = log.checkpoint()
        other = w5.Verifier(log.origin, w5.key("someone else").public_key())  # same name, other key
        with self.assertRaises(ValueError):
            w5.open_note(note, [other])  # ignored, so no known signature at all
        self.assertTrue(w5.open_note(note, [other, log.verifier]))

    def test_vkey_roundtrip(self):
        log, ws = w5.world()
        for v in (log.verifier, ws[0].verifier):
            back = w5.Verifier.parse(v.vkey())
            self.assertEqual((back.name, back.kid, back.sig_type), (v.name, v.kid, v.sig_type))

    def test_cosignature_layout(self):
        log, ws = w5.world()
        log.entries = [b"a", b"b", b"c"]
        line = log.witness(ws[0], now=1234567)
        name, kid, sig = w5.split_note(log.checkpoint() + line)[1][1]
        self.assertEqual(kid, ws[0].verifier.kid)
        self.assertEqual(len(sig), 8 + 64)
        self.assertEqual(int.from_bytes(sig[:8], "big"), 1234567)


class Witnessing(unittest.TestCase):
    def test_status_codes(self):
        log, ws = w5.world()
        w = ws[0]
        log.entries = [f"c{i}".encode() for i in range(10)]
        log.witness(w)
        with self.assertRaises(w5.WitnessError) as e:
            w.add_checkpoint(3, [], log.checkpoint(), 0)
        self.assertEqual(e.exception.status, 409)
        with self.assertRaises(w5.WitnessError) as e:
            w.add_checkpoint(10, [], log.checkpoint(log.entries[:9] + [b"x"]), 0)
        self.assertEqual(e.exception.status, 422)
        self.assertEqual(w.state[log.origin][0], 10)  # a refused request changes nothing

    def test_scenarios(self):
        got = dict(w5.scenarios())
        self.assertTrue(got["1. log grows 100 -> 250 -> 1000, 3 witnesses"].startswith("ACCEPT"))
        self.assertIn("[422, 422, 422]", got["2. split view: fork at 1500 after main at 1500"])
        self.assertIn("[422, 422, 422]", got["3. split view: fork grown to 1800"])
        self.assertIn("main ACCEPT", got["4. witnesses partitioned 2 | 1, client needs 2 of 3"])
        self.assertIn("fork REJECT", got["4. witnesses partitioned 2 | 1, client needs 2 of 3"])
        self.assertIn("main ACCEPT, fork ACCEPT", got["5. one witness compromised, client needs 2 of 3"])
        self.assertIn("main REJECT, fork REJECT", got["6. same, client needs 3 of 3"])
        self.assertEqual(got["7. freeze: a month-old checkpoint, no age limit"], "ACCEPT")
        self.assertTrue(got["8. freeze: same, cosignatures must be < 1 day old"].startswith("REJECT"))

    def test_quorum_rule(self):
        for n in range(1, 9):
            for f, k, possible in w5.quorum_table(n):
                self.assertEqual(possible, 2 * k <= n + f)


if __name__ == "__main__":
    unittest.main()
