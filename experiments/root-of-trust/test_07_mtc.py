"""Checks for part 07: the draft's encodings and test vectors, issuance, both certificate kinds, rejections, sizes."""
import importlib.util
import pathlib
import sys
import unittest
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("m07", HERE / "07_mtc.py")
m7 = importlib.util.module_from_spec(spec)
sys.modules["m07"] = m7
spec.loader.exec_module(m7)

WHEN = datetime(2026, 11, 22, tzinfo=timezone.utc)


def world(n=37, earlier=1000):
    ca = m7.MerkleTreeCA()
    for i in range(1, earlier):
        ca.entries.append(m7.mtc_log_entry(f"earlier entry {i}".encode()))
    ca.checkpoint = earlier
    reqs = [m7.Request(f"site{i}.example", m7.key(f"site {i}")) for i in range(n)]
    idx = [ca.add(r, WHEN) for r in reqs]
    certs = ca.issue_standalone()
    rp = m7.RelyingParty({c.id_bytes: (c.arcs, c.sk.public_key()) for c in [ca.ca, *ca.witnesses]},
                         ca_id=ca.ca.id_bytes, witness_quorum=1)
    return ca, reqs, idx, certs, rp


class DraftVectors(unittest.TestCase):
    def test_issuer_encoding(self):
        self.assertEqual(m7.der.tlv(0x0D, m7.relative_oid((32473, 1))).hex(), "0d0481fd5901")

    def test_appendix_c1(self):
        for name, want in m7.APPENDIX_C.items():
            self.assertEqual(m7.appendix_c1(name), want, name)

    def test_appendix_c21_validity(self):
        p = 2
        valid = [(0, p**47 + 1), (0, p**48 - 1), (0, p**62 + 1), (0, p**63 - 1), (0, p**63 + 1), (0, p**64 - 1)]
        invalid = [(p**46, p**47 + 1), (p**46, p**48 - 1), (p**61, p**62 + 1),
                   (p**61, p**63 - 1), (p**62, p**63 + 1), (p**62, p**64 - 1)]
        for s in valid:
            self.assertTrue(m7.valid_subtree(*s), s)
        for s in invalid:
            self.assertFalse(m7.valid_subtree(*s), s)

    def test_appendix_c24_covering(self):
        cases = [
            (0x0, 0x800000000000, (0x0, 0x400000000000), (0x400000000000, 0x800000000000)),
            (0x500000000000, 0xd00000000000, (0x400000000000, 0x800000000000), (0x800000000000, 0xd00000000000)),
            (0x7fffffffffff, 0x800000000001, (0x7fffffffffff, 0x800000000000), (0x800000000000, 0x800000000001)),
            (0xfffffffffffe, 0xffffffffffff, (0xfffffffffffe, 0xffffffffffff), (0xffffffffffff, 0xffffffffffff)),
            (0xffffffffffff, 0xffffffffffff, (0xffffffffffff, 0xffffffffffff), (0xffffffffffff, 0xffffffffffff)),
            (0x2800000000000000, 0x6800000000000000, (0x2000000000000000, 0x4000000000000000),
             (0x4000000000000000, 0x6800000000000000)),
            (0x5000000000000000, 0xd000000000000000, (0x4000000000000000, 0x8000000000000000),
             (0x8000000000000000, 0xd000000000000000)),
            (0xfffffffffffffffe, 0xffffffffffffffff, (0xfffffffffffffffe, 0xffffffffffffffff),
             (0xffffffffffffffff, 0xffffffffffffffff)),
        ]
        for start, end, left, right in cases:
            self.assertEqual(m7.covering_subtrees(start, end), (left, right), hex(start))


class Subtrees(unittest.TestCase):
    def test_covering_properties(self):
        for a in range(0, 130):
            for b in range(a + 1, 131):
                (l0, l1), (r0, r1) = m7.covering_subtrees(a, b)
                self.assertTrue(m7.valid_subtree(l0, l1) and m7.valid_subtree(r0, r1))
                self.assertTrue(l0 <= a and l1 == r0 and r1 == b)
                self.assertLessEqual(max(l1 - l0, r1 - r0), m7.bit_ceil(b - a))

    def test_batch_in_the_article(self):
        self.assertEqual(m7.covering_subtrees(1000, 1037), ((992, 1024), (1024, 1037)))


class Certificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ca, cls.reqs, cls.idx, cls.certs, cls.rp = world()
        cls.cert = cls.certs[cls.idx[5]]

    def test_every_certificate_verifies(self):
        self.assertEqual(len(self.certs), 37)
        for c in self.certs.values():
            self.assertTrue(self.rp.verify(c).startswith("ACCEPT"))

    def test_structure(self):
        p = m7.proof_of(self.cert)
        self.assertEqual((p["start"], p["end"], len(p["proof"]), len(p["sigs"])), (992, 1024, 5, 3))
        c = m7.x509.load_der_x509_certificate(self.cert)
        self.assertEqual(c.serial_number, (1 << 48) | 1005)
        self.assertEqual(c.signature_algorithm_oid.dotted_string, "1.3.6.1.5.5.7.6.67")
        with self.assertRaises(ValueError):
            c.issuer                              # RELATIVE-OID: the library cannot decode it yet

    def test_log_entry_hides_the_key(self):
        entry = self.ca.entries[self.idx[5]]
        spki = self.ca.fields(self.reqs[5], WHEN)[3]
        self.assertNotIn(spki, entry)
        self.assertIn(m7.sha256(spki), entry)
        self.assertEqual(entry[:4], b"\x00\x00\x00\x01")    # no extensions, tbs_cert_entry
        self.assertLess(len(entry), 256)

    def test_rejections(self):
        with self.assertRaises(Exception):
            self.rp.verify(self.cert.replace(b"site5.example", b"site6.example", 1))
        p = m7.proof_of(self.cert)
        f = self.ca.fields(self.reqs[5], WHEN)
        ca_only = m7.build_certificate(1005, *f, m7.mtc_proof(p["start"], p["end"], p["proof"], p["sigs"][:1]))
        with self.assertRaisesRegex(ValueError, "witness"):
            self.rp.verify(ca_only)
        no_ca = m7.build_certificate(1005, *f, m7.mtc_proof(p["start"], p["end"], p["proof"], p["sigs"][1:]))
        with self.assertRaisesRegex(ValueError, "CA cosignature"):
            self.rp.verify(no_ca)
        strict = m7.RelyingParty(self.rp.cosigners, self.rp.ca_id, witness_quorum=3)
        with self.assertRaises(ValueError):
            strict.verify(self.cert)

    def test_mtcproof_parsing_is_strict(self):
        raw = m7.proof_of(self.cert)
        b = m7.mtc_proof(raw["start"], raw["end"], raw["proof"], raw["sigs"])
        with self.assertRaises(ValueError):
            m7.parse_mtc_proof(b + b"\x00")

    def test_witness_refuses_a_swapped_entry(self):
        ca = m7.MerkleTreeCA()
        i = ca.add(self.reqs[0], WHEN)
        w = ca.witnesses[0]
        w.mirror = list(ca.entries)
        ca.entries[i] = m7.mtc_log_entry(b"swapped")
        with self.assertRaises(ValueError):
            w.sign_subtree(i, i + 1, m7.mk.mth(ca.entries[i : i + 1]))

    def test_landmark_relative(self):
        ca, reqs, idx, certs, rp = world()
        lm = ca.add_landmark()
        self.assertEqual(lm, [(0, 1024), (1024, 1037)])
        trusted = {s: m7.mk.mth(ca.entries[s[0] : s[1]]) for s in lm}
        rp2 = m7.RelyingParty(rp.cosigners, rp.ca_id, trusted_subtrees=trusted)
        lr = ca.landmark_relative(idx[5], ca.fields(reqs[5], WHEN))
        self.assertIn("landmark", rp2.verify(lr))
        q = m7.proof_of(lr)
        self.assertEqual((q["start"], q["end"], len(q["proof"]), q["sigs"]), (0, 1024, 10, []))
        with self.assertRaises(ValueError):
            rp.verify(lr)                         # without the landmark there is nothing to check against
        forged = {s: bytes(32) for s in lm}
        with self.assertRaises(ValueError):
            m7.RelyingParty(rp.cosigners, rp.ca_id, trusted_subtrees=forged).verify(lr)


class Sizes(unittest.TestCase):
    def test_bill_rows(self):
        ca, reqs, idx, certs, rp = world()
        cert = certs[idx[5]]
        lm = ca.add_landmark()
        lr = ca.landmark_relative(idx[5], ca.fields(reqs[5], WHEN))
        classic = m7.x509_mldsa_leaf(reqs[5], WHEN)
        self.assertEqual(len(cert), 8976)
        self.assertEqual(len(lr), 1855)
        self.assertEqual(len(classic), 8912)
        self.assertEqual(m7.handshake_auth([cert]), 11417)
        self.assertEqual(m7.handshake_auth([lr]), 4296)
        self.assertEqual(m7.handshake_auth([classic]), 11353)
        self.assertEqual(m7.handshake_auth([classic, m7.x509_mldsa_intermediate(WHEN)]), 15271)
        # what the landmark removes: three cosignatures of 1 + 4 + 2 + 2,420 bytes; what it adds: 5 more hashes
        self.assertEqual(len(cert) - len(lr), 3 * (1 + 4 + 2 + 2420) - 5 * 32)


if __name__ == "__main__":
    unittest.main()
