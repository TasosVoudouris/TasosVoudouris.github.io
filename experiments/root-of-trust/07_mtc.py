"""Root of Trust, part 07: Merkle Tree Certificates.

A toy Merkle Tree CA, written from draft-ietf-plants-merkle-tree-certs-07:

  * an issuance log of MTCLogEntry values (§5.2), whose leaves hash TBSCertificate
    data with the subject public key REPLACED by its hash;
  * the CA, as a cosigner, and two witnesses sign subtrees of the log with
    ML-DSA-44 over the CosignedSubtree structure (§5.3.1);
  * standalone certificates: an X.509 certificate whose signatureValue is an
    MTCProof (an inclusion proof to a subtree, plus cosignatures) (§6.2, §6.3);
  * landmark-relative certificates: the same, with NO signatures, valid for
    relying parties that already trust the landmark subtree (§6.4);
  * a relying party that rebuilds the log entry from the certificate and
    verifies both kinds (§7.2).

Everything is checked against Part 04's Merkle tree, the draft's own encoding
example for the issuer name, and an independent X.509 parser.

Run:  python 07_mtc.py         (needs: pip install "cryptography>=46")
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import struct
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric import mldsa

import der

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("merkle04", HERE / "04_merkle.py")
mk = importlib.util.module_from_spec(_spec)
sys.modules["merkle04"] = mk
_spec.loader.exec_module(mk)

sha256 = mk.sha256


def u16(n): return n.to_bytes(2, "big")
def u48(n): return n.to_bytes(6, "big")
def u64(n): return n.to_bytes(8, "big")
def vec8(b): return len(b).to_bytes(1, "big") + b
def vec16(b): return len(b).to_bytes(2, "big") + b
def vec24(b): return len(b).to_bytes(3, "big") + b


def bit_width(n: int) -> int:
    """Smallest number of bits needed to represent n (0 for n = 0)."""
    return n.bit_length()


def bit_ceil(n: int) -> int:
    """Smallest power of two greater than or equal to n."""
    return 1 if n <= 1 else 1 << (n - 1).bit_length()


# --------------------------------------------------------------------------- subtrees (§4)

def valid_subtree(start: int, end: int) -> bool:
    """[start, end) is a subtree if start is a multiple of BIT_CEIL(end - start)."""
    return 0 <= start <= end and start % bit_ceil(end - start) == 0


def covering_subtrees(start: int, end: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """§4.5: two subtrees that together cover [start, end). The left may begin before start."""
    if end - start <= 1:
        return (start, end), (end, end)
    last = end - 1
    split = bit_width(start ^ last) - 1          # most significant bit where start and last differ
    mid = last & ~((1 << split) - 1)             # last with its low `split` bits cleared
    low = start & ((1 << split) - 1)
    zeros = [b for b in range(split) if not (low >> b) & 1]
    left_split = (max(zeros) + 1) if zeros else 0
    left_start = start & ~((1 << left_split) - 1)
    return (left_start, mid), (mid, end)


# --------------------------------------------------------------------------- names and IDs

DOC_ARC = (32473,)              # RFC 5612's arc for documentation examples
CA_ID = DOC_ARC + (1,)
WITNESS_IDS = [DOC_ARC + (2,), DOC_ARC + (3,)]
LOG_NUMBER = 1
ID_ALG_MTC_PROOF = "1.3.6.1.5.5.7.6.67"
ID_RDNA_TRUST_ANCHOR_ID = "1.3.6.1.5.5.7.25.3"


def relative_oid(arcs) -> bytes:
    """Contents of a RELATIVE-OID: every arc in base 128, high bit = more bytes follow."""
    out = bytearray()
    for arc in arcs:
        groups = [arc & 0x7F]
        arc >>= 7
        while arc:
            groups.append(0x80 | (arc & 0x7F))
            arc >>= 7
        out += bytes(reversed(groups))
    return bytes(out)


def trust_anchor_name(arcs) -> bytes:
    """The issuer: one RDN, one attribute, id-rdna-trustAnchorID = RELATIVE-OID (§6.2)."""
    value = der.tlv(0x0D, relative_oid(arcs))
    return der.sequence(der.set_of(der.sequence(der.oid(ID_RDNA_TRUST_ANCHOR_ID), value)))


def origin(arcs) -> str:
    return "oid/1.3.6.1.4.1." + ".".join(map(str, arcs))


LOG_ID = CA_ID + (0, LOG_NUMBER)
LOG_ORIGIN = origin(LOG_ID)


# --------------------------------------------------------------------------- log entries (§5.2)

def null_entry() -> bytes:
    return vec16(b"") + u16(0)


def tbs_log_entry(issuer: bytes, validity: bytes, subject: bytes, spki: bytes, extensions: bytes) -> bytes:
    """The CONTENTS octets of a DER TBSCertificateLogEntry: like a TBSCertificate, but no serial,
    no signature algorithm, and the subject public key replaced by its algorithm and its hash."""
    alg = _first_child(spki)
    return (der.explicit(0, der.integer(2))         # version v3
            + issuer + validity + subject
            + alg                                   # subjectPublicKeyAlgorithm
            + der.octet_string(sha256(spki))        # subjectPublicKeyInfoHash
            + extensions)                           # already wrapped in [3]


def mtc_log_entry(tbs_entry_contents: bytes) -> bytes:
    """MTCLogEntry: extensions<0..2^16-1>, type (uint16), then the entry data."""
    return vec16(b"") + u16(1) + tbs_entry_contents


def _first_child(tlv_bytes: bytes) -> bytes:
    _, hdr, _, _ = der.read(tlv_bytes, 0)
    _, h2, n2, _ = der.read(tlv_bytes, hdr)
    return tlv_bytes[hdr : hdr + h2 + n2]


def _children(tlv_bytes: bytes) -> list[bytes]:
    _, hdr, n, _ = der.read(tlv_bytes, 0)
    out, pos = [], hdr
    while pos < hdr + n:
        _, h2, n2, _ = der.read(tlv_bytes, pos)
        out.append(tlv_bytes[pos : pos + h2 + n2])
        pos += h2 + n2
    return out


# --------------------------------------------------------------------------- cosigning (§5.3)

def cosigned_subtree(cosigner_arcs, start: int, end: int, subtree_hash: bytes, timestamp: int = 0) -> bytes:
    """The message a cosigner signs. In certificates the timestamp is zero."""
    return (b"subtree/v1\n\0"
            + vec8(origin(cosigner_arcs).encode())
            + u64(timestamp)
            + vec8(LOG_ORIGIN.encode())
            + u64(start) + u64(end)
            + subtree_hash)


@dataclass
class Cosigner:
    arcs: tuple
    sk: mldsa.MLDSA44PrivateKey
    mirror: list = field(default_factory=list)   # a witness keeps its own copy of the entries
    honest: bool = True

    @property
    def id_bytes(self) -> bytes:
        return relative_oid(self.arcs)

    def sign_subtree(self, start: int, end: int, claimed: bytes) -> bytes:
        if self.honest and mk.mth(self.mirror[start:end]) != claimed:
            raise ValueError(f"{origin(self.arcs)}: subtree [{start}, {end}) does not match my view of the log")
        return self.sk.sign(cosigned_subtree(self.arcs, start, end, claimed))


# --------------------------------------------------------------------------- certificates (§6)

def mtc_proof(start: int, end: int, proof: list[bytes], sigs: list[tuple[bytes, bytes]]) -> bytes:
    """MTCProof. Cosignatures sorted by cosigner ID: shorter first, then lexicographically."""
    sigs = sorted(sigs, key=lambda s: (len(s[0]), s[0]))
    body = b"".join(vec8(cid) + vec16(sig) for cid, sig in sigs)
    return vec16(b"") + u48(start) + u48(end) + vec16(b"".join(proof)) + vec24(body)


def parse_mtc_proof(b: bytes) -> dict:
    pos = 0
    (n,) = struct.unpack(">H", b[pos : pos + 2]); pos += 2 + n          # extensions (empty here)
    start = int.from_bytes(b[pos : pos + 6], "big"); pos += 6
    end = int.from_bytes(b[pos : pos + 6], "big"); pos += 6
    (n,) = struct.unpack(">H", b[pos : pos + 2]); pos += 2
    proof = [b[pos + i : pos + i + 32] for i in range(0, n, 32)]; pos += n
    total = int.from_bytes(b[pos : pos + 3], "big"); pos += 3
    sigs, endpos = [], pos + total
    while pos < endpos:
        ln = b[pos]; cid = b[pos + 1 : pos + 1 + ln]; pos += 1 + ln
        (sl,) = struct.unpack(">H", b[pos : pos + 2]); sigs.append((cid, b[pos + 2 : pos + 2 + sl])); pos += 2 + sl
    if pos != len(b):
        raise ValueError("trailing data after MTCProof")
    if sigs != sorted(sigs, key=lambda s: (len(s[0]), s[0])) or len({c for c, _ in sigs}) != len(sigs):
        raise ValueError("cosignatures not sorted or not unique")
    return {"start": start, "end": end, "proof": proof, "sigs": sigs}


def build_certificate(index: int, issuer, validity, subject, spki, extensions, proof_bytes: bytes) -> bytes:
    alg = der.sequence(der.oid(ID_ALG_MTC_PROOF))          # parameters absent
    tbs = der.sequence(der.explicit(0, der.integer(2)),
                       der.integer((LOG_NUMBER << 48) | index),
                       alg, issuer, validity, subject, spki, extensions)
    return der.sequence(tbs, alg, der.bit_string(proof_bytes))


# --------------------------------------------------------------------------- the CA

def key(label: str) -> mldsa.MLDSA44PrivateKey:
    return mldsa.MLDSA44PrivateKey.from_seed_bytes(sha256(f"root-of-trust part 07: {label}".encode()))


@dataclass
class Request:
    name: str
    key: mldsa.MLDSA44PrivateKey


class MerkleTreeCA:
    def __init__(self, witnesses_honest=(True, True)):
        self.entries: list[bytes] = [null_entry()]       # our toy log starts with a null entry
        self.pending: list[tuple[int, tuple]] = []
        self.ca = Cosigner(CA_ID, key("ca cosigner"))
        self.witnesses = [Cosigner(a, key(f"witness {a[-1]}"), honest=h) for a, h in zip(WITNESS_IDS, witnesses_honest)]
        self.checkpoint = 1
        self.landmarks = [0]                              # landmark zero has tree size zero

    def fields(self, req: Request, not_before: datetime):
        issuer = trust_anchor_name(CA_ID)
        validity = der.sequence(der.time(not_before), der.time(not_before + timedelta(days=7) - timedelta(seconds=1)))
        subject = der.sequence(der.set_of(der.sequence(der.oid("2.5.4.3"), der.utf8_string(req.name))))
        spki = req.key.public_key().public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)
        san = der.sequence(der.oid("2.5.29.17"), der.octet_string(der.sequence(der.implicit_primitive(2, req.name.encode()))))
        eku = der.sequence(der.oid("2.5.29.37"), der.octet_string(der.sequence(der.oid("1.3.6.1.5.5.7.3.1"))))
        extensions = der.explicit(3, der.sequence(san, eku))
        return issuer, validity, subject, spki, extensions

    def add(self, req: Request, when: datetime) -> int:
        """Validate (here: trust), then LOG FIRST: the entry exists before any certificate does."""
        f = self.fields(req, when)
        self.entries.append(mtc_log_entry(tbs_log_entry(*f)))
        index = len(self.entries) - 1
        self.pending.append((index, f))
        return index

    def issue_standalone(self) -> dict[int, bytes]:
        """§6.3: cover the new entries with two subtrees, have them cosigned, build certificates."""
        start, end = self.checkpoint, len(self.entries)
        for c in [self.ca, *self.witnesses]:
            c.mirror = list(self.entries)                  # every cosigner checks against its own copy
        subtrees = [s for s in covering_subtrees(start, end) if s[0] < s[1]]
        sigs = {}
        for s in subtrees:
            h = mk.mth(self.entries[s[0] : s[1]])
            sigs[s] = [(c.id_bytes, c.sign_subtree(*s, h)) for c in [self.ca, *self.witnesses]]
        certs = {}
        for index, f in self.pending:
            s = next(t for t in subtrees if t[0] <= index < t[1])
            p = mk.path(index - s[0], self.entries[s[0] : s[1]])
            certs[index] = build_certificate(index, *f, mtc_proof(*s, p, sigs[s]))
        self.checkpoint = end
        return certs

    def add_landmark(self) -> list[tuple[int, int]]:
        """§6.4.1: a landmark's subtrees cover [previous landmark, this landmark)."""
        prev, size = self.landmarks[-1], len(self.entries)
        self.landmarks.append(size)
        return [s for s in covering_subtrees(prev, size) if s[0] < s[1]]

    def landmark_relative(self, index: int, f) -> bytes:
        prev = max(l for l in self.landmarks if l <= index)
        size = min(l for l in self.landmarks if l > index)
        s = next(t for t in covering_subtrees(prev, size) if t[0] <= index < t[1])
        p = mk.path(index - s[0], self.entries[s[0] : s[1]])
        return build_certificate(index, *f, mtc_proof(*s, p, []))   # no signatures at all


# --------------------------------------------------------------------------- the relying party (§7.2)

@dataclass
class RelyingParty:
    cosigners: dict                                  # cosigner ID bytes -> (name, public key)
    ca_id: bytes
    witness_quorum: int = 1
    trusted_subtrees: dict = field(default_factory=dict)   # (start, end) -> hash, from landmarks

    def verify(self, cert: bytes) -> str:
        c = x509.load_der_x509_certificate(cert)     # an independent X.509 parser must accept it
        assert c.signature_algorithm_oid.dotted_string == ID_ALG_MTC_PROOF
        tbs, alg, _ = _children(cert)
        proof = proof_of(cert)
        version, serial, sig_alg, issuer, validity, subject, spki, exts = _children(tbs)
        if sig_alg != alg:
            raise ValueError("signature algorithm fields differ")
        s = c.serial_number
        index, log_number = s & ((1 << 48) - 1), s >> 48
        if log_number == 0:
            raise ValueError("log number zero")
        entry = mtc_log_entry(tbs_log_entry(issuer, validity, subject, spki, exts))
        start, end = proof["start"], proof["end"]
        if not (valid_subtree(start, end) and start <= index < end):
            raise ValueError("index not in a valid subtree")
        got = _evaluate(mk.leaf_hash(entry), index - start, end - start, proof["proof"])
        if (start, end) in self.trusted_subtrees:
            if self.trusted_subtrees[(start, end)] != got:
                raise ValueError("does not match the trusted landmark subtree")
            return f"ACCEPT: entry {index} in landmark subtree [{start}, {end}), no signature checked"
        ok_ca, ok_w = False, 0
        for cid, sig in proof["sigs"]:
            if cid not in self.cosigners:
                continue                                   # unknown cosigners are ignored
            name, pub = self.cosigners[cid]
            pub.verify(sig, cosigned_subtree(name, start, end, got))
            if cid == self.ca_id:
                ok_ca = True
            else:
                ok_w += 1
        if not ok_ca:
            raise ValueError("no valid CA cosignature")
        if ok_w < self.witness_quorum:
            raise ValueError(f"only {ok_w} witness cosignature(s), need {self.witness_quorum}")
        return f"ACCEPT: entry {index} in subtree [{start}, {end}), CA + {ok_w} witness cosignature(s)"


def proof_of(cert: bytes) -> dict:
    sigval = _children(cert)[2]
    _, h, n, _ = der.read(sigval, 0)
    return parse_mtc_proof(sigval[h + 1 : h + n])      # skip the BIT STRING's unused-bits byte


def _evaluate(leaf: bytes, index: int, size: int, proof: list[bytes]) -> bytes:
    """RFC 9162 §2.1.3.2, but returning the computed root instead of comparing it (§4.3)."""
    fn, sn, r = index, size - 1, leaf
    for p in proof:
        if sn == 0:
            raise ValueError("proof too long")
        if fn & 1 or fn == sn:
            r = mk.node_hash(p, r)
            if not fn & 1:
                while fn and not fn & 1:
                    fn, sn = fn >> 1, sn >> 1
        else:
            r = mk.node_hash(r, p)
        fn, sn = fn >> 1, sn >> 1
    if sn != 0:
        raise ValueError("proof too short")
    return r


# --------------------------------------------------------------------------- report

def x509_mldsa_leaf(req: Request, when: datetime) -> bytes:
    """The same leaf as a classic X.509 certificate signed by an ML-DSA-44 CA, with two
    ML-DSA-44 SCTs: the thing an MTC replaces. Built with the library; SCTs as raw bytes."""
    from cryptography.x509.oid import NameOID
    ca = key("classic CA")
    sct = b"\x00" + bytes(32) + bytes(8) + b"\x00\x00" + b"\x09\x04" + vec16(bytes(2420))
    scts = vec16(vec16(sct) + vec16(sct))
    b = (x509.CertificateBuilder()
         .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, req.name)]))
         .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Toy CA M1")]))
         .serial_number(1 << 100).not_valid_before(when).not_valid_after(when + timedelta(days=7))
         .public_key(req.key.public_key())
         .add_extension(x509.SubjectAlternativeName([x509.DNSName(req.name)]), False)
         .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), False)
         .add_extension(x509.UnrecognizedExtension(x509.oid.ExtensionOID.PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS,
                                                   der.octet_string(scts)), False))
    return b.sign(ca, None).public_bytes(ser.Encoding.DER)


def x509_mldsa_intermediate(when: datetime) -> bytes:
    """The intermediate a classic chain also sends: an ML-DSA-44 CA key, signed by an ML-DSA-44 root."""
    from cryptography.x509.oid import NameOID
    b = (x509.CertificateBuilder()
         .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Toy CA M1")]))
         .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Toy Root M")]))
         .serial_number(1 << 90).not_valid_before(when).not_valid_after(when + timedelta(days=365 * 5))
         .public_key(key("classic CA").public_key())
         .add_extension(x509.BasicConstraints(ca=True, path_length=0), True))
    return b.sign(key("classic root"), None).public_bytes(ser.Encoding.DER)


def handshake_auth(cert_ders: list[bytes], cv_sig: int = 2420) -> int:
    """Part 02's framing: Certificate message + CertificateVerify."""
    return 4 + 1 + 3 + sum(3 + len(c) + 2 for c in cert_ders) + 4 + 2 + 2 + cv_sig


# --------------------------------------------------------------------------- the draft's test vectors (Appendix C)

APPENDIX_C = {"C.1.1 subtree hashes": "b82806ad4265bb151c1119c0f4db437bb4d1a1f887b3a7fba1cd4ebf552e3e81",
              "C.1.4 covering subtrees": "7fd9c8b926e9d2b5cf831560e8ce295a5ef97ad5c5ede4ea0dea28a8c8fc8bb0"}


def appendix_c1(which: str, max_end: int = 130) -> str:
    """Leaves d[i] = the single byte i; every [start, end) with 0 <= start <= end <= 130,
    one text line per output, all lines fed into one running SHA-256."""
    d = [bytes([i]) for i in range(max_end + 1)]
    h = hashlib.sha256()
    for end in range(max_end + 1):
        for start in range(end + 1):
            if which.startswith("C.1.1") and valid_subtree(start, end):
                h.update(f"[{start}, {end}) {mk.mth(d[start:end]).hex()}\n".encode())
            elif which.startswith("C.1.4"):
                (a, b), (c, e) = covering_subtrees(start, end)
                h.update(f"[{a}, {b}) [{c}, {e})\n".encode())
    return h.hexdigest()


def main() -> int:
    when = datetime(2026, 11, 22, tzinfo=timezone.utc)
    print("== encodings checked against the draft ==")
    attr = der.tlv(0x0D, relative_oid(CA_ID))
    print(f"  CA ID 32473.1 as an issuer attribute value: {attr.hex()}  (draft: 0d0481fd5901)")
    assert attr.hex() == "0d0481fd5901"
    print(f"  log origin: {LOG_ORIGIN}")
    bad = [(a, b) for a in range(0, 260) for b in range(a + 1, 261)
           if not all(valid_subtree(*s) for s in covering_subtrees(a, b))
           or set(range(a, b)) - set().union(*(range(*s) for s in covering_subtrees(a, b)))
           or covering_subtrees(a, b)[1][1] != b
           or any(s[1] - s[0] > bit_ceil(b - a) for s in covering_subtrees(a, b))]
    print(f"  covering subtrees for every 0 <= start < end <= 260: valid, covering, right ends at end,"
          f" sizes <= BIT_CEIL: {'all ok' if not bad else bad[:3]}")
    for name, want in APPENDIX_C.items():
        got = appendix_c1(name)
        print(f"  draft Appendix {name}: {got[:16]}...  {'matches' if got == want else 'MISMATCH'}")
        assert got == want

    print("\n== issuance: the CA logs first, then cosigns, then builds certificates ==")
    ca = MerkleTreeCA()
    for i in range(1, 1000):
        ca.entries.append(mtc_log_entry(f"earlier entry {i}".encode()))
    ca.checkpoint = 1000
    reqs = [Request(f"site{i}.example", key(f"site {i}")) for i in range(37)]
    idx = [ca.add(r, when) for r in reqs]
    subtrees = [s for s in covering_subtrees(1000, len(ca.entries)) if s[0] < s[1]]
    print(f"  37 new entries [1000, {len(ca.entries)}) covered by subtrees {subtrees}")
    certs = ca.issue_standalone()
    print(f"  each subtree cosigned by the CA and 2 witnesses (ML-DSA-44), {len(certs)} certificates built")

    rp = RelyingParty({c.id_bytes: (c.arcs, c.sk.public_key()) for c in [ca.ca, *ca.witnesses]},
                      ca_id=ca.ca.id_bytes, witness_quorum=1)
    target = idx[5]
    cert = certs[target]
    print("\n== a standalone certificate ==")
    print("  " + rp.verify(cert))
    c = x509.load_der_x509_certificate(cert)
    print(f"  parsed by `cryptography`: serial {c.serial_number:#x} = (log 1 << 48) | {target},"
          f" algorithm {c.signature_algorithm_oid.dotted_string}")
    try:
        c.issuer
        print("  `cryptography` also decoded the issuer")
    except ValueError:
        print("  `cryptography` refuses to decode the issuer: its attribute value is a RELATIVE-OID (tag 0x0D),"
              " which today's X.509 stacks do not expect. MTC needs parser updates, not only new trust stores.")
    p = proof_of(cert)
    print(f"  {len(cert):,} bytes: MTCProof subtree [{p['start']}, {p['end']}), {len(p['proof'])} proof hashes,"
          f" {len(p['sigs'])} cosignatures")
    entry = ca.entries[target]
    print(f"  its log entry: {len(entry)} bytes (the public key is a 32-byte hash, and there is no signature)")

    print("\n== attacks on the relying party ==")
    tampered = cert.replace(b"site5.example", b"site6.example", 1)
    for label, blob, party in (
        ("certificate for another name", tampered, rp),
        ("no witness, quorum 1", build_certificate(target, *ca.fields(reqs[5], when),
                                                   mtc_proof(p["start"], p["end"], p["proof"], [s for s in p["sigs"] if s[0] == ca.ca.id_bytes])), rp),
        ("same certificate, policy quorum 2", cert, RelyingParty(rp.cosigners, rp.ca_id, witness_quorum=2)),
    ):
        try:
            print(f"  {label:32s} -> {party.verify(blob)}")
        except Exception as e:
            why = str(e) or "the proof now leads to a subtree hash nobody cosigned"
            print(f"  {label:32s} -> REJECT: {type(e).__name__}: {why}")
    lying = MerkleTreeCA()
    i0 = lying.add(reqs[0], when)
    w = lying.witnesses[0]
    w.mirror = list(lying.entries)                       # the witness fetched the log...
    lying.entries[i0] = mtc_log_entry(b"swapped after the witness looked")   # ...then the CA swapped an entry
    try:
        w.sign_subtree(i0, i0 + 1, mk.mth(lying.entries[i0 : i0 + 1]))
    except ValueError as e:
        print(f"  {'CA swaps an entry, asks witness':32s} -> witness refuses: {e}")

    print("\n== a landmark-relative certificate: no signatures ==")
    lm = ca.add_landmark()
    trusted = {s: mk.mth(ca.entries[s[0] : s[1]]) for s in lm}   # predistributed after checking cosignatures
    rp2 = RelyingParty(rp.cosigners, rp.ca_id, trusted_subtrees=trusted)
    lr = ca.landmark_relative(target, ca.fields(reqs[5], when))
    print(f"  landmark 1 at tree size {ca.landmarks[-1]}, subtrees {lm}")
    print("  " + rp2.verify(lr))
    q = proof_of(lr)
    print(f"  {len(lr):,} bytes: subtree [{q['start']}, {q['end']}), {len(q['proof'])} proof hashes, 0 signatures")
    try:
        rp.verify(lr)
    except Exception as e:
        print(f"  the same certificate, relying party without the landmark -> REJECT: {e}")

    print("\n== the handshake bill (Part 02's framing; CertificateVerify is ML-DSA-44 in every row) ==")
    classic = x509_mldsa_leaf(reqs[5], when)
    inter = x509_mldsa_intermediate(when)
    rows = [
        ("X.509 + 2 SCTs + intermediate, ML-DSA-44", handshake_auth([classic, inter])),
        ("X.509 + 2 SCTs, leaf only (intermediate cached)", handshake_auth([classic])),
        ("MTC standalone: CA + 2 witnesses", handshake_auth([cert])),
        ("MTC standalone: CA + 1 witness",
         handshake_auth([build_certificate(target, *ca.fields(reqs[5], when),
                                           mtc_proof(p["start"], p["end"], p["proof"], p["sigs"][:2]))])),
        ("MTC landmark-relative", handshake_auth([lr])),
    ]
    for label, n in rows:
        print(f"  {label:48s} {n:>7,} B   server flight ~{n + 1367:>7,} B")
    print(f"  (classic leaf {len(classic):,} B, intermediate {len(inter):,} B; MTC standalone {len(cert):,} B;"
          f" landmark-relative {len(lr):,} B)")
    sa, lrn = handshake_auth([cert]) + (12 - 5) * 32, handshake_auth([lr]) + (23 - 10) * 32
    print(f"  at the draft's §6.5 scale (12 hashes standalone, 23 landmark-relative):"
          f" standalone {sa:,} B, landmark-relative {lrn:,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
