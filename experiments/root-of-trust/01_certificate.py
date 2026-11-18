"""Root of Trust, part 01: build an X.509 certificate by hand, byte by byte.

1. Encode a complete certificate with our own DER encoder (der.py).
2. Build the same certificate with the `cryptography` library.
3. Check that the two are identical, byte for byte.
4. Print an annotated dump, then build the same certificate with ML-DSA-44.

Keys come from fixed seeds so every run prints the same bytes.
Run:  python 01_certificate.py           (needs cryptography >= 46)
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

import der

# --- fixed inputs ------------------------------------------------------------

def seed(label: str) -> bytes:
    return hashlib.sha256(f"root-of-trust part 01: {label}".encode()).digest()


CA_KEY = Ed25519PrivateKey.from_private_bytes(seed("CA"))
LEAF_KEY = Ed25519PrivateKey.from_private_bytes(seed("leaf"))
CA_NAME = "Root of Trust Toy CA"
SITE = "example.com"
SERIAL = int.from_bytes(seed("serial")[:16], "big") | (1 << 127)  # top bit set on purpose
NOT_BEFORE = datetime(2026, 11, 18, 0, 0, 0, tzinfo=timezone.utc)
NOT_AFTER = datetime(2027, 1, 3, 23, 59, 59, tzinfo=timezone.utc)

OID = {
    "ed25519": "1.3.101.112",                 # RFC 8410
    "ml-dsa-44": "2.16.840.1.101.3.4.3.17",   # RFC 9881
    "commonName": "2.5.4.3",
    "subjectAltName": "2.5.29.17",
    "basicConstraints": "2.5.29.19",
    "keyUsage": "2.5.29.15",
    "extKeyUsage": "2.5.29.37",
    "serverAuth": "1.3.6.1.5.5.7.3.1",
}
NAMES = {v: k for k, v in OID.items()}


# --- 1. by hand --------------------------------------------------------------

def name(cn: str) -> bytes:
    # Name ::= SEQUENCE OF RelativeDistinguishedName
    # RelativeDistinguishedName ::= SET OF AttributeTypeAndValue
    return der.sequence(der.set_of(der.sequence(der.oid(OID["commonName"]), der.utf8_string(cn))))


def extension(oid: str, value: bytes, critical: bool = False) -> bytes:
    parts = [der.oid(oid)]
    if critical:                        # critical BOOLEAN DEFAULT FALSE: omit when FALSE
        parts.append(der.boolean(True))
    parts.append(der.octet_string(value))  # the extension's own DER, wrapped
    return der.sequence(*parts)


def tbs_certificate(spki: bytes, sig_alg: bytes) -> bytes:
    extensions = der.sequence(
        extension(OID["subjectAltName"], der.sequence(
            der.implicit_primitive(2, SITE.encode()),          # dNSName [2] IA5String
            der.implicit_primitive(2, f"www.{SITE}".encode()),
        )),
        extension(OID["basicConstraints"], der.sequence(), critical=True),  # cA DEFAULT FALSE
        extension(OID["keyUsage"], der.bit_string(b"\x80", unused_bits=7), critical=True),
        extension(OID["extKeyUsage"], der.sequence(der.oid(OID["serverAuth"]))),
    )
    return der.sequence(
        der.explicit(0, der.integer(2)),   # version v3 (encoded as 2)
        der.integer(SERIAL),
        sig_alg,                           # signature algorithm (inside the signed part)
        name(CA_NAME),                     # issuer
        der.sequence(der.time(NOT_BEFORE), der.time(NOT_AFTER)),  # validity
        name(SITE),                        # subject
        spki,                              # subjectPublicKeyInfo
        der.explicit(3, extensions),
    )


def by_hand() -> tuple[bytes, bytes]:
    alg = der.sequence(der.oid(OID["ed25519"]))  # parameters absent (RFC 8410 §3)
    pub = LEAF_KEY.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    spki = der.sequence(alg, der.bit_string(pub))
    tbs = tbs_certificate(spki, alg)
    signature = CA_KEY.sign(tbs)  # Ed25519 signs the TBS bytes directly
    return der.sequence(tbs, alg, der.bit_string(signature)), tbs


# --- 2. with the library -----------------------------------------------------

def by_library() -> bytes:
    cert = (
        x509.CertificateBuilder()
        .serial_number(SERIAL)
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, CA_NAME)]))
        .not_valid_before(NOT_BEFORE)
        .not_valid_after(NOT_AFTER)
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, SITE)]))
        .public_key(LEAF_KEY.public_key())
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(SITE), x509.DNSName(f"www.{SITE}")]), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
                          data_encipherment=False, key_agreement=False, key_cert_sign=False,
                          crl_sign=False, encipher_only=False, decipher_only=False),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(CA_KEY, algorithm=None)
    )
    return cert.public_bytes(Encoding.DER)


# --- 4. the same certificate with ML-DSA-44 ------------------------------------

def ml_dsa_version() -> bytes:
    from cryptography.hazmat.primitives.asymmetric import mldsa

    ca = mldsa.MLDSA44PrivateKey.from_seed_bytes(seed("ML-DSA CA"))
    leaf = mldsa.MLDSA44PrivateKey.from_seed_bytes(seed("ML-DSA leaf"))
    alg = der.sequence(der.oid(OID["ml-dsa-44"]))  # parameters absent (RFC 9881)
    spki = der.sequence(alg, der.bit_string(leaf.public_key().public_bytes_raw()))
    tbs = tbs_certificate(spki, alg)
    cert = der.sequence(tbs, alg, der.bit_string(ca.sign(tbs)))
    # Independent check: the library parses our bytes and verifies the signature.
    parsed = x509.load_der_x509_certificate(cert)
    ca.public_key().verify(parsed.signature, parsed.tbs_certificate_bytes)
    return cert


def ca_certificate() -> bytes:
    """A self-signed root for the toy CA, so OpenSSL can verify the chain."""
    n = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, CA_NAME)])
    cert = (
        x509.CertificateBuilder()
        .serial_number(1)
        .issuer_name(n)
        .subject_name(n)
        .not_valid_before(datetime(2026, 1, 1, tzinfo=timezone.utc))
        .not_valid_after(datetime(2036, 1, 1, tzinfo=timezone.utc))
        .public_key(CA_KEY.public_key())
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(digital_signature=False, content_commitment=False, key_encipherment=False,
                          data_encipherment=False, key_agreement=False, key_cert_sign=True,
                          crl_sign=True, encipher_only=False, decipher_only=False),
            critical=True,
        )
        .sign(CA_KEY, algorithm=None)
    )
    return cert.public_bytes(Encoding.DER)


def main() -> int:
    mine, tbs = by_hand()
    theirs = by_library()
    print(f"by hand : {len(mine)} bytes, sha256 {hashlib.sha256(mine).hexdigest()[:16]}")
    print(f"library : {len(theirs)} bytes, sha256 {hashlib.sha256(theirs).hexdigest()[:16]}")
    print("identical:", mine == theirs)
    if mine != theirs:
        return 1

    cert = x509.load_der_x509_certificate(mine)
    CA_KEY.public_key().verify(cert.signature, cert.tbs_certificate_bytes)
    print("signature verifies with the CA key; signed part =", len(tbs), "bytes, starting at offset",
          mine.index(tbs))
    print()
    print(der.dump(mine, names=NAMES))
    print()

    pq = ml_dsa_version()
    print(f"same certificate with ML-DSA-44: {len(pq)} bytes (Ed25519 version: {len(mine)} bytes)")
    if "--write" in sys.argv:
        open("01_example_ed25519.der", "wb").write(mine)
        open("01_example_mldsa44.der", "wb").write(pq)
        open("01_example_ca.der", "wb").write(ca_certificate())
        print("wrote 01_example_ed25519.der, 01_example_mldsa44.der, 01_example_ca.der")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
