"""Checks for part 02: every size the article quotes, and the live handshake (OpenSSL 3.5+)."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("hs02", HERE / "02_handshake.py")
hs = importlib.util.module_from_spec(spec)
sys.modules["hs02"] = hs
spec.loader.exec_module(hs)

CHAINS = {p: hs.build_chain(p) for p in hs.PROFILES}


class Model(unittest.TestCase):
    def test_tls_framing(self):
        self.assertEqual(hs.certificate_message([b"\x30\x00"]), bytes.fromhex("0b00000b 00 000007 000002 3000 0000"))
        self.assertEqual(hs.certificate_verify_size(2420), 2428)
        self.assertEqual(hs.encrypted_records(1574), 1574 + 22)
        self.assertEqual(hs.encrypted_records(18210), 18210 + 2 * 22)  # two records past 16,384

    def test_scts_verify(self):
        for ch in CHAINS.values():
            self.assertEqual(hs.verify_scts(ch), 2)

    def test_certificate_sizes(self):
        expect = {"classical": (845, 711), "ml-dsa-44": (9110, 4246), "ml-dsa-65": (12417, 5775)}
        for p, (leaf, inter) in expect.items():
            ch = CHAINS[p]
            self.assertEqual(len(ch.der(ch.leaf)[0]), leaf, p)
            self.assertEqual(len(ch.der(ch.inter)[0]), inter, p)

    def test_bill(self):
        b = hs.Bill(CHAINS["ml-dsa-44"], send_intermediate=True)
        self.assertEqual(b.parts["public keys"], 2 * 1312)
        self.assertEqual(b.parts["CA signatures"], 2 * 2420)
        self.assertEqual(b.parts["SCT signatures"], 2 * 2420)
        self.assertEqual(b.parts["handshake signature"], 2420)
        self.assertEqual(len(b.cert_msg), 13374)
        self.assertEqual(b.auth_bytes, 15802)
        self.assertEqual(sum(b.parts.values()), b.auth_bytes)
        self.assertEqual(hs.Bill(CHAINS["ml-dsa-44"], send_intermediate=False).auth_bytes, 11551)
        self.assertEqual(hs.Bill(CHAINS["ml-dsa-65"], send_intermediate=True).auth_bytes, 21527)
        self.assertEqual(len(hs.Bill(CHAINS["classical"], send_intermediate=True).cert_msg), 1574)


@unittest.skipUnless(hs.LIVE_OK, "live handshakes need OpenSSL 3.5+")
class LiveHandshake(unittest.TestCase):
    def run_one(self, profile, send_inter, classical_kex):
        with tempfile.TemporaryDirectory() as tmp:
            return hs.live_handshake(CHAINS[profile], send_inter, classical_kex, tmp)

    def test_model_matches_openssl(self):
        for p in hs.PROFILES:
            for send_inter in (True, False):
                lv = self.run_one(p, send_inter, classical_kex=False)
                self.assertEqual(lv.messages[("server", "Certificate")][0], hs.Bill(CHAINS[p], send_inter).cert_msg)
                self.assertEqual(lv.first_server_flight(), hs.server_flight_model(lv))

    def test_negotiation(self):
        lv = self.run_one("ml-dsa-44", True, classical_kex=False)
        self.assertEqual(lv.group, "X25519MLKEM768")
        self.assertEqual(lv.scheme, "mldsa44")
        self.assertEqual(self.run_one("classical", True, classical_kex=True).group, "X25519")

    def test_initial_window(self):
        self.assertLessEqual(self.run_one("classical", True, False).first_server_flight(), hs.TCP_INITCWND)
        self.assertGreater(self.run_one("ml-dsa-44", True, False).first_server_flight(), hs.TCP_INITCWND)
        self.assertLessEqual(self.run_one("ml-dsa-44", False, False).first_server_flight(), hs.TCP_INITCWND)


if __name__ == "__main__":
    unittest.main()
