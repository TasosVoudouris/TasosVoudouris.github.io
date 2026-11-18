"""Checks for part 01: the DER encoder and every number the article quotes."""
import importlib.util
import pathlib
import sys
import unittest
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import der  # noqa: E402

spec = importlib.util.spec_from_file_location("cert01", HERE / "01_certificate.py")
cert01 = importlib.util.module_from_spec(spec)
sys.modules["cert01"] = cert01
spec.loader.exec_module(cert01)


class Encoder(unittest.TestCase):
    def test_lengths(self):
        self.assertEqual(der.length(5), b"\x05")
        self.assertEqual(der.length(127), b"\x7f")
        self.assertEqual(der.length(128), b"\x81\x80")
        self.assertEqual(der.length(335), b"\x82\x01\x4f")
        self.assertEqual(der.length(2421), b"\x82\x09\x75")

    def test_integers(self):
        self.assertEqual(der.integer(0), bytes.fromhex("020100"))
        self.assertEqual(der.integer(2), bytes.fromhex("020102"))
        self.assertEqual(der.integer(127), bytes.fromhex("02017f"))
        self.assertEqual(der.integer(128), bytes.fromhex("02020080"))
        self.assertEqual(der.integer(256), bytes.fromhex("02020100"))

    def test_oids(self):
        self.assertEqual(der.oid("1.3.101.112"), bytes.fromhex("06032b6570"))
        self.assertEqual(der.oid("2.5.29.17"), bytes.fromhex("0603551d11"))
        self.assertEqual(der.oid("2.16.840.1.101.3.4.3.17"), bytes.fromhex("060960864801650304031" + "1"))
        for dotted in ("1.3.101.112", "2.5.4.3", "1.3.6.1.5.5.7.3.1", "2.16.840.1.101.3.4.3.17"):
            self.assertEqual(der.decode_oid(der.oid(dotted)[2:]), dotted)

    def test_small_types(self):
        self.assertEqual(der.boolean(True), bytes.fromhex("0101ff"))
        self.assertEqual(der.sequence(), bytes.fromhex("3000"))
        self.assertEqual(der.bit_string(b"\x80", 7), bytes.fromhex("03020780"))
        t = der.time(datetime(2026, 11, 18, tzinfo=timezone.utc))
        self.assertEqual(t, b"\x17\x0d261118000000Z")
        t = der.time(datetime(2050, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(t[0], 0x18)  # GeneralizedTime from 2050 on

    def test_strict_reader(self):
        with self.assertRaises(ValueError):
            der.read(bytes.fromhex("30 81 05") + bytes(5), 0)  # long form for a short length
        with self.assertRaises(ValueError):
            der.read(bytes.fromhex("30 80 00 00"), 0)  # indefinite length (BER only)


class Certificate(unittest.TestCase):
    def test_identical_to_library(self):
        mine, tbs = cert01.by_hand()
        self.assertEqual(mine, cert01.by_library())
        self.assertEqual(len(mine), 342)
        self.assertEqual(len(tbs), 264)
        self.assertEqual(mine[4 : 4 + 264], tbs)

    def test_offsets_quoted_in_article(self):
        mine, _ = cert01.by_hand()
        self.assertEqual(mine[:4], bytes.fromhex("30820152"))
        self.assertEqual(mine[4:8], bytes.fromhex("30820104"))
        self.assertEqual(mine[8:13], bytes.fromhex("a003020102"))
        self.assertEqual(mine[13:16], bytes.fromhex("021100"))
        self.assertEqual(mine[32:39], bytes.fromhex("300506032b6570"))
        self.assertEqual(mine[137:140], bytes.fromhex("032100"))
        self.assertEqual(mine[172:174], bytes.fromhex("a35e"))
        self.assertEqual(mine[224:231], bytes.fromhex("0101ff04023000"))
        self.assertEqual(mine[275:278], bytes.fromhex("034100"))

    def test_ml_dsa_sizes(self):
        pq = cert01.ml_dsa_version()
        self.assertEqual(len(pq), 4002)
        ed, _ = cert01.by_hand()
        # 32 B key + 64 B signature versus 1312 B key + 2420 B signature
        self.assertEqual(len(ed) - 32 - 64, 246)
        self.assertEqual(len(pq) - 1312 - 2420, 270)


if __name__ == "__main__":
    unittest.main()
