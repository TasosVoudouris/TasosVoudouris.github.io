"""Root of Trust, part 02: the handshake bill.

Builds three realistic certificate chains (root, intermediate, leaf with two
embedded SCTs) and measures what a TLS 1.3 server sends to authenticate itself:

  classical  ECDSA P-384 root and intermediate, ECDSA P-256 leaf and CT logs
  ml-dsa-44  every key and signature ML-DSA-44 (FIPS 204, category 2)
  ml-dsa-65  every key and signature ML-DSA-65 (FIPS 204, category 3)

Three independent views of the same bytes:

  1. a byte model: the TLS Certificate and CertificateVerify messages encoded
     by hand (RFC 8446 §4.4.2, §4.4.3), plus the record layer around them;
  2. a live handshake: Python's ssl module (OpenSSL 3.5 or newer is needed for
     ML-DSA and ML-KEM) on memory buffers, with every handshake message captured;
  3. the comparison: the hand-encoded Certificate message must equal the one
     OpenSSL sent, byte for byte, and the record model must equal the bytes
     on the wire.

Run:   python 02_handshake.py
Needs: pip install "cryptography>=46"   (for ML-DSA certificates)
"""
from __future__ import annotations

import hashlib
import ssl
import struct
import sys
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec, mldsa
from cryptography.x509.oid import ExtendedKeyUsageOID, ExtensionOID, NameOID

import der

# --------------------------------------------------------------------------- setup

def seed(label: str) -> bytes:
    return hashlib.sha256(f"root-of-trust part 02: {label}".encode()).digest()


def make_key(alg: str, label: str):
    """Deterministic keys, so every run builds the same certificates."""
    s = seed(label)
    if alg == "p256":
        return ec.derive_private_key(int.from_bytes(s, "big") >> 8, ec.SECP256R1())
    if alg == "p384":
        return ec.derive_private_key(int.from_bytes(s + seed(label + "/2")[:16], "big") >> 8, ec.SECP384R1())
    if alg == "mldsa44":
        return mldsa.MLDSA44PrivateKey.from_seed_bytes(s)
    if alg == "mldsa65":
        return mldsa.MLDSA65PrivateKey.from_seed_bytes(s)
    raise ValueError(alg)


PROFILES = {
    #             root       intermediate  leaf       CT logs
    "classical": ("p384",    "p384",       "p256",    "p256"),
    "ml-dsa-44": ("mldsa44", "mldsa44",    "mldsa44", "mldsa44"),
    "ml-dsa-65": ("mldsa65", "mldsa65",    "mldsa65", "mldsa65"),
}

UTC = timezone.utc
LEAF_FROM = datetime(2026, 11, 19, tzinfo=UTC)
LEAF_UNTIL = LEAF_FROM + timedelta(days=47, seconds=-1)
SCT_TIME_MS = int(LEAF_FROM.timestamp() * 1000) - 60_000  # logged a minute before issuance
SITE = "example.com"


def sign_cert(builder: x509.CertificateBuilder, key) -> x509.Certificate:
    if isinstance(key, ec.EllipticCurvePrivateKey):
        h = hashes.SHA384() if key.curve.key_size == 384 else hashes.SHA256()
        return builder.sign(key, h, ecdsa_deterministic=True)  # RFC 6979: same bytes every run
    return builder.sign(key, None)  # ML-DSA: pure mode, no separate hash (RFC 9881)


def spki(key) -> bytes:
    return key.public_key().public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)


def name(*cn_o_c: tuple[str, str]) -> x509.Name:
    oids = {"C": NameOID.COUNTRY_NAME, "O": NameOID.ORGANIZATION_NAME, "CN": NameOID.COMMON_NAME}
    return x509.Name([x509.NameAttribute(oids[k], v) for k, v in cn_o_c])


ROOT_NAME = name(("C", "GR"), ("O", "Root of Trust"), ("CN", "Root of Trust Toy Root X1"))
INTER_NAME = name(("C", "GR"), ("O", "Root of Trust"), ("CN", "Toy E1"))
DV_POLICY = x509.CertificatePolicies([x509.PolicyInformation(x509.ObjectIdentifier("2.23.140.1.2.1"), None)])


def aia(url: str) -> x509.AuthorityInformationAccess:
    return x509.AuthorityInformationAccess(
        [x509.AccessDescription(x509.oid.AuthorityInformationAccessOID.CA_ISSUERS, x509.UniformResourceIdentifier(url))]
    )


def ku(**on) -> x509.KeyUsage:
    names = ["digital_signature", "content_commitment", "key_encipherment", "data_encipherment",
             "key_agreement", "key_cert_sign", "crl_sign", "encipher_only", "decipher_only"]
    return x509.KeyUsage(**{n: on.get(n, False) for n in names})


# --------------------------------------------------------------------------- tiny TLS encoder

def u8(n: int) -> bytes: return n.to_bytes(1, "big")
def u16(n: int) -> bytes: return n.to_bytes(2, "big")
def u24(n: int) -> bytes: return n.to_bytes(3, "big")
def vec8(b: bytes) -> bytes: return u8(len(b)) + b
def vec16(b: bytes) -> bytes: return u16(len(b)) + b
def vec24(b: bytes) -> bytes: return u24(len(b)) + b


def handshake_msg(msg_type: int, body: bytes) -> bytes:
    """RFC 8446 §4: msg_type (1 byte) + uint24 length + body."""
    return u8(msg_type) + vec24(body)


def certificate_message(chain_der: list[bytes]) -> bytes:
    """RFC 8446 §4.4.2. Server side: empty request context, no per-entry extensions."""
    entries = b"".join(vec24(cert) + vec16(b"") for cert in chain_der)
    return handshake_msg(11, vec8(b"") + vec24(entries))


def certificate_verify_size(signature_len: int) -> int:
    """RFC 8446 §4.4.3: header 4 + SignatureScheme 2 + signature<0..2^16-1>."""
    return 4 + 2 + 2 + signature_len


MAX_RECORD = 2**14  # largest TLSInnerPlaintext content (RFC 8446 §5.1)


def encrypted_records(plaintext_len: int) -> int:
    """Wire bytes for a handshake message sent encrypted: each record adds a 5-byte header,
    1 byte of inner content type and a 16-byte AEAD tag (RFC 8446 §5.2)."""
    n = -(-plaintext_len // MAX_RECORD)
    return plaintext_len + n * (5 + 1 + 16)


# --------------------------------------------------------------------------- SCTs (RFC 6962)

# RFC 6962 signs with TLS 1.2 SignatureAndHashAlgorithm. There is no ML-DSA code point
# there; we reuse the TLS 1.3 SignatureScheme values (0x0904, 0x0905) as a stand-in.
# The size is what matters here and it does not depend on these two bytes.
SCT_ALG = {"p256": b"\x04\x03", "mldsa44": b"\x09\x04", "mldsa65": b"\x09\x05"}


def sct_signed_data(timestamp: int, issuer_spki: bytes, precert_tbs: bytes) -> bytes:
    """RFC 6962 §3.2, the digitally-signed struct for a precert_entry."""
    return (u8(0)                                    # sct_version v1
            + u8(0)                                  # signature_type certificate_timestamp
            + struct.pack(">Q", timestamp)
            + u16(1)                                 # entry_type precert_entry
            + hashlib.sha256(issuer_spki).digest()   # issuer_key_hash
            + vec24(precert_tbs)
            + vec16(b""))                            # CtExtensions


def log_sign(log_key, alg: str, data: bytes) -> bytes:
    if alg == "p256":
        return log_key.sign(data, ec.ECDSA(hashes.SHA256(), deterministic_signing=True))
    return log_key.sign(data)


def make_sct(log_key, alg: str, issuer_spki: bytes, precert_tbs: bytes) -> bytes:
    sig = log_sign(log_key, alg, sct_signed_data(SCT_TIME_MS, issuer_spki, precert_tbs))
    return (u8(0)                                    # sct_version v1
            + hashlib.sha256(spki(log_key)).digest() # LogID: hash of the log's public key
            + struct.pack(">Q", SCT_TIME_MS)
            + vec16(b"")                             # extensions
            + SCT_ALG[alg] + vec16(sig))             # digitally-signed


def parse_sct_list(blob: bytes) -> list[dict]:
    """Inverse of the above, for checking. blob = the TLS-encoded SignedCertificateTimestampList."""
    (total,) = struct.unpack(">H", blob[:2])
    assert total == len(blob) - 2
    out, pos = [], 2
    while pos < len(blob):
        (n,) = struct.unpack(">H", blob[pos : pos + 2])
        s = blob[pos + 2 : pos + 2 + n]
        (ts,) = struct.unpack(">Q", s[33:41])
        (siglen,) = struct.unpack(">H", s[45:47])
        out.append({"log_id": s[1:33], "timestamp": ts, "alg": s[43:45], "signature": s[47 : 47 + siglen], "size": n})
        assert 47 + siglen == n
        pos += 2 + n
    return out


# --------------------------------------------------------------------------- chains

@dataclass
class Chain:
    profile: str
    root: x509.Certificate
    inter: x509.Certificate
    leaf: x509.Certificate
    leaf_key: object
    log_keys: list
    precert_tbs: bytes
    sct_list: bytes  # TLS-encoded SignedCertificateTimestampList

    def pem(self, *certs: x509.Certificate) -> bytes:
        return b"".join(c.public_bytes(ser.Encoding.PEM) for c in certs)

    def der(self, *certs: x509.Certificate) -> list[bytes]:
        return [c.public_bytes(ser.Encoding.DER) for c in certs]


def build_chain(profile: str) -> Chain:
    a_root, a_inter, a_leaf, a_log = PROFILES[profile]
    root_key = make_key(a_root, f"{profile}/root")
    inter_key = make_key(a_inter, f"{profile}/intermediate")
    leaf_key = make_key(a_leaf, f"{profile}/leaf")
    log_keys = [make_key(a_log, f"{profile}/log-{i}") for i in (1, 2)]
    serial = lambda label: int.from_bytes(seed(f"{profile}/serial/{label}")[:16], "big") >> 1

    ski = lambda k: x509.SubjectKeyIdentifier.from_public_key(k.public_key())
    aki = lambda k: x509.AuthorityKeyIdentifier.from_issuer_public_key(k.public_key())

    root = sign_cert(
        x509.CertificateBuilder()
        .subject_name(ROOT_NAME).issuer_name(ROOT_NAME).serial_number(serial("root"))
        .not_valid_before(datetime(2026, 1, 1, tzinfo=UTC)).not_valid_after(datetime(2046, 1, 1, tzinfo=UTC))
        .public_key(root_key.public_key())
        .add_extension(ku(key_cert_sign=True, crl_sign=True), critical=True)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(ski(root_key), critical=False),
        root_key,
    )
    inter = sign_cert(
        x509.CertificateBuilder()
        .subject_name(INTER_NAME).issuer_name(ROOT_NAME).serial_number(serial("intermediate"))
        .not_valid_before(datetime(2026, 3, 1, tzinfo=UTC)).not_valid_after(datetime(2029, 3, 1, tzinfo=UTC))
        .public_key(inter_key.public_key())
        .add_extension(ku(digital_signature=True, key_cert_sign=True, crl_sign=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(ski(inter_key), critical=False)
        .add_extension(aki(root_key), critical=False)
        .add_extension(aia("http://x1.i.root-of-trust.example/"), critical=False)
        .add_extension(DV_POLICY, critical=False)
        .add_extension(x509.CRLDistributionPoints([x509.DistributionPoint(
            [x509.UniformResourceIdentifier("http://x1.c.root-of-trust.example/")], None, None, None)]), critical=False),
        root_key,
    )
    leaf_builder = (
        x509.CertificateBuilder()
        .subject_name(name(("CN", SITE))).issuer_name(INTER_NAME).serial_number(serial("leaf"))
        .not_valid_before(LEAF_FROM).not_valid_after(LEAF_UNTIL)
        .public_key(leaf_key.public_key())
        .add_extension(ku(digital_signature=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(aki(inter_key), critical=False)
        .add_extension(aia("http://e1.i.root-of-trust.example/"), critical=False)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(SITE), x509.DNSName(f"www.{SITE}")]), critical=False)
        .add_extension(DV_POLICY, critical=False)
    )
    # The CA first builds the leaf without SCTs (the "precertificate" TBS), asks two logs to
    # sign it, and then issues the real leaf with the SCT list appended as the last extension.
    precert_tbs = sign_cert(leaf_builder, inter_key).tbs_certificate_bytes
    sct_list = vec16(b"".join(vec16(make_sct(k, a_log, spki(inter_key), precert_tbs)) for k in log_keys))
    leaf = sign_cert(
        leaf_builder.add_extension(
            x509.UnrecognizedExtension(ExtensionOID.PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS, der.octet_string(sct_list)),
            critical=False,
        ),
        inter_key,
    )
    return Chain(profile, root, inter, leaf, leaf_key, log_keys, precert_tbs, sct_list)


def verify_scts(chain: Chain) -> int:
    """Check both SCT signatures over the leaf's precertificate TBS, as a browser would."""
    assert chain.leaf.tbs_precertificate_bytes == chain.precert_tbs  # library strips the SCT extension
    issuer_spki = chain.inter.public_key().public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)
    data = sct_signed_data(SCT_TIME_MS, issuer_spki, chain.leaf.tbs_precertificate_bytes)
    ok = 0
    for sct, key in zip(parse_sct_list(chain.sct_list), chain.log_keys):
        assert sct["log_id"] == hashlib.sha256(spki(key)).digest()
        pub = key.public_key()
        if isinstance(pub, ec.EllipticCurvePublicKey):
            pub.verify(sct["signature"], data, ec.ECDSA(hashes.SHA256()))
        else:
            pub.verify(sct["signature"], data)
        ok += 1
    return ok


# --------------------------------------------------------------------------- accounting

def cert_parts(cert: x509.Certificate) -> dict[str, int]:
    """Split one certificate into public key, CA signature, SCT signatures, everything else."""
    raw = cert.public_bytes(ser.Encoding.DER)
    pub = cert.public_key().public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)
    # SubjectPublicKeyInfo = SEQUENCE { AlgorithmIdentifier, BIT STRING }: take the BIT STRING
    _, hdr, _, _ = der.read(pub, 0)
    _, _, _, alg_end = der.read(pub, hdr)
    _, _, n, _ = der.read(pub, alg_end)
    key = n - 1  # minus the unused-bits byte
    sig = len(cert.signature)
    blob = _raw_sct_extension(raw)
    scts = sum(len(s["signature"]) for s in parse_sct_list(blob)) if blob else 0
    return {"total": len(raw), "key": key, "signature": sig, "sct_signatures": scts,
            "other": len(raw) - key - sig - scts}


def _raw_sct_extension(raw: bytes) -> bytes | None:
    """Find the SCT list with our own DER walker (the library may not parse ML-DSA SCTs)."""
    target = der.oid("1.3.6.1.4.1.11129.2.4.2")
    i = raw.find(target)
    if i < 0:
        return None
    pos = i + len(target)
    _, hdr, _, _ = der.read(raw, pos)          # outer OCTET STRING (extnValue)
    _, hdr2, n2, _ = der.read(raw, pos + hdr)  # inner OCTET STRING
    start = pos + hdr + hdr2
    return raw[start : start + n2]


@dataclass
class Bill:
    """What the server sends to authenticate, in the byte model."""
    chain: Chain
    send_intermediate: bool
    cert_msg: bytes = b""
    cv_sig: int = 0
    parts: dict = field(default_factory=dict)

    def __post_init__(self):
        certs = [self.chain.leaf] + ([self.chain.inter] if self.send_intermediate else [])
        self.cert_msg = certificate_message([c.public_bytes(ser.Encoding.DER) for c in certs])
        self.cv_sig = cv_signature_len(self.chain.leaf_key)
        p = [cert_parts(c) for c in certs]
        self.parts = {
            "public keys": sum(x["key"] for x in p),
            "CA signatures": sum(x["signature"] for x in p),
            "SCT signatures": sum(x["sct_signatures"] for x in p),
            "handshake signature": self.cv_sig,
            "everything else": sum(x["other"] for x in p) + (len(self.cert_msg) - sum(x["total"] for x in p))
                               + (certificate_verify_size(self.cv_sig) - self.cv_sig),
        }

    @property
    def auth_bytes(self) -> int:
        return len(self.cert_msg) + certificate_verify_size(self.cv_sig)


def cv_signature_len(key) -> int:
    """Signature length the leaf key produces. ECDSA's DER length varies by a byte or two."""
    if isinstance(key, ec.EllipticCurvePrivateKey):
        return len(key.sign(b"x" * 64, ec.ECDSA(hashes.SHA256(), deterministic_signing=True)))
    return len(key.sign(b"x"))


# --------------------------------------------------------------------------- live TLS 1.3

LIVE_OK = ssl.OPENSSL_VERSION_INFO >= (3, 5, 0)
GROUP_NAMES = {0x001D: "X25519", 0x0017: "secp256r1", 0x11EC: "X25519MLKEM768", 0x11EB: "SecP256r1MLKEM768"}
SCHEME_NAMES = {0x0403: "ecdsa_secp256r1_sha256", 0x0904: "mldsa44", 0x0905: "mldsa65", 0x0906: "mldsa87"}
MSG_NAMES = {1: "ClientHello", 2: "ServerHello", 8: "EncryptedExtensions", 11: "Certificate",
             15: "CertificateVerify", 20: "Finished", 4: "NewSessionTicket"}


def extensions_of(hello: bytes, server: bool) -> dict[int, bytes]:
    """Pull the extensions block out of a ClientHello or ServerHello handshake message."""
    p = 4 + 2 + 32                     # header, legacy_version, random
    p += 1 + hello[p]                  # legacy_session_id
    if server:
        p += 2 + 1                     # cipher_suite, compression
    else:
        p += 2 + int.from_bytes(hello[p : p + 2], "big")  # cipher_suites
        p += 1 + hello[p]              # compression methods
    end = p + 2 + int.from_bytes(hello[p : p + 2], "big")
    p += 2
    out = {}
    while p < end:
        t, n = int.from_bytes(hello[p : p + 2], "big"), int.from_bytes(hello[p + 2 : p + 4], "big")
        out[t] = hello[p + 4 : p + 4 + n]
        p += 4 + n
    return out


def key_shares(hello: bytes, server: bool) -> list[tuple[str, int]]:
    ks = extensions_of(hello, server)[51]  # key_share
    if server:
        return [(GROUP_NAMES.get(int.from_bytes(ks[:2], "big"), hex(int.from_bytes(ks[:2], "big"))),
                 int.from_bytes(ks[2:4], "big"))]
    out, p = [], 2
    while p < len(ks):
        g, n = int.from_bytes(ks[p : p + 2], "big"), int.from_bytes(ks[p + 2 : p + 4], "big")
        out.append((GROUP_NAMES.get(g, hex(g)), n))
        p += 4 + n
    return out


@dataclass
class Live:
    flights: list            # [(sender, wire bytes)] in order
    messages: dict           # (sender, name) -> list of handshake message bytes
    group: str
    scheme: str

    def first_server_flight(self) -> int:
        return next(n for who, n in self.flights if who == "server")


def live_handshake(chain: Chain, send_intermediate: bool, classical_kex: bool, workdir: str) -> Live:
    import os
    certs = (chain.leaf, chain.inter) if send_intermediate else (chain.leaf,)
    cert_file, key_file = os.path.join(workdir, "chain.pem"), os.path.join(workdir, "key.pem")
    with open(cert_file, "wb") as f:
        f.write(chain.pem(*certs))
    with open(key_file, "wb") as f:
        f.write(chain.leaf_key.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))

    server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server.minimum_version = ssl.TLSVersion.TLSv1_3
    server.load_cert_chain(cert_file, key_file)
    client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client.minimum_version = ssl.TLSVersion.TLSv1_3
    # A client that already knows the intermediate has it next to the root in its store.
    client.load_verify_locations(cadata=chain.pem(chain.root, *(() if send_intermediate else (chain.inter,))).decode())
    if classical_kex:
        client.set_ecdh_curve("X25519")  # otherwise OpenSSL 3.5 leads with X25519MLKEM768

    messages: dict = {}

    def capture(conn, direction, version, content_type, msg_type, data):
        if direction == "write" and content_type == ssl._TLSContentType.HANDSHAKE:
            who = "server" if conn.server_side else "client"
            messages.setdefault((who, MSG_NAMES.get(int(msg_type), str(msg_type))), []).append(bytes(data))

    server._msg_callback = capture
    client._msg_callback = capture

    c_in, c_out, s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO()
    c = client.wrap_bio(c_in, c_out, server_hostname=SITE)
    s = server.wrap_bio(s_in, s_out, server_side=True)
    flights = []
    for _ in range(4):
        for who, conn, out, peer_in in (("client", c, c_out, s_in), ("server", s, s_out, c_in)):
            try:
                conn.do_handshake()
            except ssl.SSLWantReadError:
                pass
            data = out.read()
            if data:
                flights.append((who, len(data)))
                peer_in.write(data)
    assert c.version() == "TLSv1.3"
    sh = messages[("server", "ServerHello")][0]
    cv = messages[("server", "CertificateVerify")][0]
    scheme = int.from_bytes(cv[4:6], "big")
    return Live(flights, messages, key_shares(sh, server=True)[0][0], SCHEME_NAMES.get(scheme, hex(scheme)))


def server_flight_model(live: Live) -> int:
    """Predict the server's first flight from its plaintext messages and the record rules."""
    m = live.messages
    sh = len(m[("server", "ServerHello")][0])
    total = 5 + sh   # ServerHello: one plaintext record
    total += 5 + 1   # the middlebox-compatibility ChangeCipherSpec (RFC 8446 §D.4)
    for name in ("EncryptedExtensions", "Certificate", "CertificateVerify", "Finished"):
        total += encrypted_records(len(m[("server", name)][0]))
    return total


# --------------------------------------------------------------------------- limits

TCP_INITCWND = 10 * 1460   # RFC 6928: ten segments; 1460 is a typical Ethernet MSS
QUIC_MIN_INITIAL = 1200    # RFC 9000 §14.1: client Initial datagrams are padded to at least this
QUIC_AMPLIFICATION = 3     # RFC 9000 §8.1: at most 3x the bytes received, before validation
QUIC_PACKET_OVERHEAD = 60  # rough: long header, packet number, CRYPTO frame header, AEAD tag


def quic_budget(client_hello_len: int) -> int:
    datagrams = -(-(client_hello_len + QUIC_PACKET_OVERHEAD) // QUIC_MIN_INITIAL)
    return QUIC_AMPLIFICATION * datagrams * QUIC_MIN_INITIAL


# --------------------------------------------------------------------------- report

def fmt(n: int) -> str:
    return f"{n:,}"


def main() -> int:
    import tempfile

    print(f"python {sys.version.split()[0]}, {ssl.OPENSSL_VERSION}")
    chains = {p: build_chain(p) for p in PROFILES}

    print("\n== the chains ==")
    for p, ch in chains.items():
        sizes = [len(c.public_bytes(ser.Encoding.DER)) for c in (ch.leaf, ch.inter, ch.root)]
        print(f"{p:10s} leaf {fmt(sizes[0]):>6} B   intermediate {fmt(sizes[1]):>6} B   root {fmt(sizes[2]):>6} B (not sent)"
              f"   SCTs verified: {verify_scts(ch)}")

    print("\n== where the authentication bytes go (byte model, full chain) ==")
    hdr = f"{'':22s}" + "".join(f"{p:>12s}" for p in PROFILES)
    print(hdr)
    bills = {p: Bill(ch, send_intermediate=True) for p, ch in chains.items()}
    for row in ["public keys", "CA signatures", "SCT signatures", "handshake signature", "everything else"]:
        print(f"{row:22s}" + "".join(f"{fmt(b.parts[row]):>12s}" for b in bills.values()))
    print(f"{'= Certificate + CV':22s}" + "".join(f"{fmt(b.auth_bytes):>12s}" for b in bills.values()))
    for p, b in bills.items():
        assert sum(b.parts.values()) == b.auth_bytes, p

    print("\n== same, when the client already has the intermediate ==")
    lean = {p: Bill(ch, send_intermediate=False) for p, ch in chains.items()}
    print(f"{'= Certificate + CV':22s}" + "".join(f"{fmt(b.auth_bytes):>12s}" for b in lean.values()))

    print("\n== certificate compression (RFC 8879), zlib level 9 on the Certificate message ==")
    for p, b in bills.items():
        z = len(zlib.compress(b.cert_msg, 9))
        print(f"{p:10s} {fmt(len(b.cert_msg)):>7} -> {fmt(z):>7} B   saved {100 * (1 - z / len(b.cert_msg)):4.1f} %")

    if not LIVE_OK:
        print(f"\n(live handshakes skipped: they need OpenSSL 3.5+, this Python has {ssl.OPENSSL_VERSION})")
        return 0

    print("\n== live TLS 1.3 handshakes (OpenSSL, memory buffers) ==")
    print(f"{'profile':10s} {'chain':12s} {'key exchange':15s} {'ClientHello':>11s} {'server flight':>13s}"
          f" {'Certificate':>11s} {'CertVerify':>10s}  fits 14,600 B?  QUIC budget")
    with tempfile.TemporaryDirectory() as tmp:
        for p, ch in chains.items():
            for send_inter in (True, False):
                for classical_kex in (True, False):
                    lv = live_handshake(ch, send_inter, classical_kex, tmp)
                    cert_msg = lv.messages[("server", "Certificate")][0]
                    model = Bill(ch, send_inter).cert_msg
                    assert cert_msg == model, "hand-encoded Certificate message differs from OpenSSL's"
                    assert lv.first_server_flight() == server_flight_model(lv), "record model is off"
                    ch_len = len(lv.messages[("client", "ClientHello")][0])
                    flight = lv.first_server_flight()
                    print(f"{p:10s} {'leaf + inter' if send_inter else 'leaf only':12s} {lv.group:15s}"
                          f" {fmt(ch_len):>11s} {fmt(flight):>13s} {fmt(len(cert_msg)):>11s}"
                          f" {fmt(len(lv.messages[('server', 'CertificateVerify')][0])):>10s}"
                          f"  {'yes' if flight <= TCP_INITCWND else 'NO':>14s}  {fmt(quic_budget(ch_len)):>11s}"
                          f"{'' if flight <= quic_budget(ch_len) else '  over'}")
        lv = live_handshake(chains["classical"], True, False, tmp)
        hello = lv.messages[("client", "ClientHello")][0]
        print("\nClientHello key shares (OpenSSL default):", key_shares(hello, server=False))
        print("ServerHello key share:", key_shares(lv.messages[("server", "ServerHello")][0], server=True))
        print("CertificateVerify scheme:", lv.scheme)
        print("server flight, message by message:")
        for name in ("ServerHello", "EncryptedExtensions", "Certificate", "CertificateVerify", "Finished"):
            n = len(lv.messages[("server", name)][0])
            wire = 5 + n if name == "ServerHello" else encrypted_records(n)
            print(f"   {name:20s} {fmt(n):>6} B plaintext   {fmt(wire):>6} B on the wire")
        print(f"   {'ChangeCipherSpec':20s} {'1':>6} B             {'6':>6} B on the wire")
        print("every hand-encoded Certificate message matched OpenSSL's byte for byte;"
              " every server flight matched the record model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
