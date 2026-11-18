"""The six verdicts printed by 00_toy_chain.py, as assertions."""
import importlib.util
import io
import pathlib
import sys
import unittest
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("toy", HERE / "00_toy_chain.py")
toy = importlib.util.module_from_spec(spec)
sys.modules["toy"] = toy  # dataclasses need the module registered
spec.loader.exec_module(toy)


class ToyChain(unittest.TestCase):
    def test_verdicts(self):
        out = io.StringIO()
        with redirect_stdout(out):
            toy.main()
        verdicts = [line.split()[0] for line in out.getvalue().splitlines()[:6]]
        self.assertEqual(verdicts, ["ACCEPT", "REJECT", "REJECT", "REJECT", "ACCEPT", "ACCEPT"])
        self.assertIn("Ed25519 224 B   ML-DSA-44 8572 B", out.getvalue())

    def test_expired_and_non_ca(self):
        root = toy.Ed25519PrivateKey.generate()
        site = toy.Ed25519PrivateKey.generate()
        store = {"R": root.public_key()}
        old = toy.issue("R", root, "a.example", site.public_key(), -3, False)
        self.assertEqual(toy.verify_chain([old], store, "a.example")[0], False)
        leaf_as_issuer = toy.issue("R", root, "a.example", site.public_key(), 10, False)
        child = toy.issue("a.example", site, "b.example", site.public_key(), 10, False)
        ok, why = toy.verify_chain([child, leaf_as_issuer], store, "b.example")
        self.assertFalse(ok)
        self.assertIn("not allowed to issue", why)


if __name__ == "__main__":
    unittest.main()
