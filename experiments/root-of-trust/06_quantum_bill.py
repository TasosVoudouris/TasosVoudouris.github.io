"""Root of Trust, part 06: the quantum bill.

Every byte of Part 02's handshake, re-priced for every post-quantum signature we
can actually run:

  1. measure each scheme: public key, signature, signing and verifying time.
     Classical and ML-DSA through `cryptography`; everything else through liboqs
     (pip install liboqs-python), if present. Without liboqs the script falls back
     to sizes measured with liboqs 0.16.0, which the specs fix anyway.
  2. price the handshake by ROLE: who sends a public key, who signs online,
     who signs offline. The model reproduces Part 02's measured bills exactly.
  3. search every assignment of schemes to roles for the smallest bill, under
     explicit constraints (signing speed, standardization status).

Run:  python 06_quantum_bill.py   (needs: pip install cryptography; optional: liboqs-python)
"""
from __future__ import annotations

import itertools
import os
import statistics
import sys
import time
import warnings
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, mldsa, padding, rsa


@dataclass
class Scheme:
    name: str
    family: str
    status: str        # "classical", "FIPS", "draft FIPS", "round 3", ...
    level: int         # NIST security category (0 for classical: broken by a quantum computer)
    pk: int            # bytes of public key as carried in a certificate
    sig: float         # bytes of signature (mean, for variable-length Falcon)
    sign_ms: float = float("nan")
    verify_ms: float = float("nan")
    measured: str = "table"


# Sizes measured with liboqs 0.16.0 and cryptography 50 (2026-11-22). Fixed by the specs, except
# Falcon's compressed signatures, whose length varies; we give the mean over a few thousand.
# Timings in this table are from the author's machine and only shown if nothing is measured locally.
CATALOG = [
    # name                      family          status         lvl  pk       sig      sign ms   verify ms
    ("Ed25519",                 "elliptic",     "classical",   0,   32,      64,      0.03,     0.08),
    ("ECDSA P-256",             "elliptic",     "classical",   0,   65,      71,      0.03,     0.09),
    ("RSA-2048",                "factoring",    "classical",   0,   270,     256,     1.0,      0.03),
    ("ML-DSA-44",               "lattice",      "FIPS 204",    2,   1312,    2420,    0.074,    0.036),
    ("ML-DSA-65",               "lattice",      "FIPS 204",    3,   1952,    3309,    0.119,    0.032),
    ("ML-DSA-87",               "lattice",      "FIPS 204",    5,   2592,    4627,    0.106,    0.086),
    ("Falcon-512",              "lattice",      "draft FIPS 206", 1, 897,    655.1,   0.209,    0.042),
    ("Falcon-1024",             "lattice",      "draft FIPS 206", 5, 1793,   1270.5,  0.431,    0.078),
    ("SLH-DSA-SHA2-128s",       "hash",         "FIPS 205",    1,   32,      7856,    530.7,    0.488),
    ("SLH-DSA-SHA2-128f",       "hash",         "FIPS 205",    1,   32,      17088,   23.66,    2.154),
    ("MAYO-1",                  "multivariate", "round 3",     1,   1420,    454,     0.221,    0.091),
    ("MAYO-2",                  "multivariate", "round 3",     1,   4912,    186,     0.112,    0.027),
    ("SNOVA-24-5-4",            "multivariate", "round 3",     1,   1016,    248,     0.442,    0.097),
    ("UOV-Ip-pkc",              "multivariate", "round 3",     1,   43576,   128,     0.03,     0.05),
    ("UOV-Is",                  "multivariate", "round 3",     1,   412160,  96,      0.032,    0.065),
    ("MQOM-L1-short",           "MPC-in-the-head", "round 3",  1,   60,      2916,    1.857,    1.808),
]

OQS_NAMES = {
    "ML-DSA-44": "ML-DSA-44", "ML-DSA-65": "ML-DSA-65", "ML-DSA-87": "ML-DSA-87",
    "Falcon-512": "Falcon-512", "Falcon-1024": "Falcon-1024",
    "SLH-DSA-SHA2-128s": "SLH_DSA_PURE_SHA2_128S", "SLH-DSA-SHA2-128f": "SLH_DSA_PURE_SHA2_128F",
    "MAYO-1": "MAYO-1", "MAYO-2": "MAYO-2", "SNOVA-24-5-4": "SNOVA_24_5_4",
    "UOV-Ip-pkc": "OV-Ip-pkc", "UOV-Is": "OV-Is", "MQOM-L1-short": "mqom2_cat1_gf16_short_r5",
}


# --------------------------------------------------------------------------- measuring

def _time(fn, budget: float = 0.4, at_least: int = 3) -> float:
    """Median milliseconds per call, running for about `budget` seconds."""
    samples, start = [], time.perf_counter()
    while len(samples) < at_least or time.perf_counter() - start < budget:
        t = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t) * 1000)
        if len(samples) > 20000:
            break
    return statistics.median(samples)


def measure_classical_and_mldsa() -> dict[str, tuple]:
    out = {}
    msg = os.urandom(64)
    k = ed25519.Ed25519PrivateKey.generate()
    s = k.sign(msg)
    out["Ed25519"] = (32, 64, _time(lambda: k.sign(msg)), _time(lambda: k.public_key().verify(s, msg)))
    k = ec.generate_private_key(ec.SECP256R1())
    sigs = [len(k.sign(os.urandom(64), ec.ECDSA(hashes.SHA256()))) for _ in range(500)]
    s = k.sign(msg, ec.ECDSA(hashes.SHA256()))
    out["ECDSA P-256"] = (65, statistics.mean(sigs), _time(lambda: k.sign(msg, ec.ECDSA(hashes.SHA256()))),
                          _time(lambda: k.public_key().verify(s, msg, ec.ECDSA(hashes.SHA256()))))
    k = rsa.generate_private_key(65537, 2048)
    pad = padding.PKCS1v15()
    s = k.sign(msg, pad, hashes.SHA256())
    out["RSA-2048"] = (270, 256, _time(lambda: k.sign(msg, pad, hashes.SHA256())),
                       _time(lambda: k.public_key().verify(s, msg, pad, hashes.SHA256())))
    for name, cls, pk in (("ML-DSA-44", mldsa.MLDSA44PrivateKey, 1312), ("ML-DSA-65", mldsa.MLDSA65PrivateKey, 1952),
                          ("ML-DSA-87", mldsa.MLDSA87PrivateKey, 2592)):
        k = cls.generate()
        s = k.sign(msg)
        out[name] = (pk, len(s), _time(lambda: k.sign(msg)), _time(lambda: k.public_key().verify(s, msg)))
    return out


def measure_oqs() -> tuple[dict[str, tuple], str | None]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import oqs  # noqa: F401
    except Exception:
        return {}, None
    import oqs
    out = {}
    for name, mech in OQS_NAMES.items():
        if mech not in oqs.get_enabled_sig_mechanisms():
            continue  # ML-DSA too: with liboqs present, every PQ timing comes from one library
        with oqs.Signature(mech) as s:
            pk = s.generate_keypair()
            lens = [len(s.sign(os.urandom(64))) for _ in range(200 if "SLH" not in mech else 2)]
            msg = os.urandom(64)
            sig = s.sign(msg)
            budget = 1.0 if "SLH" in mech else 0.3
            out[name] = (len(pk), statistics.mean(lens), _time(lambda: s.sign(msg), budget, 2),
                         _time(lambda: s.verify(msg, sig, pk)))
    return out, oqs.oqs_version()


def catalog(measure: bool = True) -> tuple[list[Scheme], str]:
    local, note = {}, "sizes and timings from the table (author's machine)"
    if measure:
        local.update(measure_classical_and_mldsa())
        oqs_part, version = measure_oqs()
        local.update(oqs_part)
        note = (f"measured here: cryptography + liboqs {version}" if version
                else "measured here: cryptography only; * = no liboqs, size and time from the table")
    out = []
    for name, fam, status, lvl, pk, sig, s_ms, v_ms in CATALOG:
        if name in local:
            pk2, sig2, s2, v2 = local[name]
            assert pk2 == pk and abs(sig2 - sig) < 8, f"{name}: measured {pk2}/{sig2}, table {pk}/{sig}"
            out.append(Scheme(name, fam, status, lvl, pk, sig2 if "Falcon" in name or "ECDSA" in name else sig, s2, v2, "here"))
        else:
            out.append(Scheme(name, fam, status, lvl, pk, sig, s_ms, v_ms, "table"))  # author's timings
    return out, note


# --------------------------------------------------------------------------- the bill, by role

STRUCTURE = 1078       # Part 02: names, dates, extensions, SCT metadata, TLS framing (ML-DSA chains)
OTHER_FLIGHT = 1367    # Part 02: ServerHello (hybrid), EE, Finished, CCS, record headers and tags
TCP_WINDOW = 14600     # RFC 6928: 10 segments of 1460 bytes
QUIC_BUDGET = 7200     # 3 x two 1200-byte client datagrams (the hybrid ClientHello needs two)


@dataclass
class Assignment:
    leaf: Scheme    # its public key travels; it signs CertificateVerify ONLINE, per connection
    inter: Scheme   # its public key travels; it signs the leaf (offline, at issuance)
    root: Scheme    # its key stays in the client; it signs the intermediate (offline, rarely)
    log: Scheme     # its keys stay in the client; two logs sign SCTs (offline, per certificate)
    send_intermediate: bool = True

    def parts(self) -> dict[str, float]:
        p = {
            "leaf public key": self.leaf.pk,
            "CertificateVerify": self.leaf.sig,
            "leaf certificate signature": self.inter.sig,
            "2 SCTs": 2 * self.log.sig,
        }
        if self.send_intermediate:
            p["intermediate public key"] = self.inter.pk
            p["intermediate certificate signature"] = self.root.sig
        p["structure"] = STRUCTURE
        return p

    @property
    def auth(self) -> int:
        return round(sum(self.parts().values()))

    @property
    def flight(self) -> int:
        records = -(-(self.auth - 600) // 16384)  # the Certificate message: one record per 16 KiB
        return self.auth + OTHER_FLIGHT + 22 * (records - 1)

    def label(self) -> str:
        roles = [("leaf", self.leaf), ("CA", self.inter), ("root", self.root), ("logs", self.log)]
        if not self.send_intermediate:
            roles = [r for r in roles if r[0] != "root"]  # the root signs nothing that is sent
        if len({x.name for _, x in roles}) == 1:
            return f"{roles[0][1].name} everywhere"
        return " / ".join(f"{role} {x.name}" for role, x in roles)


def best(schemes: list[Scheme], allowed, online_ms: float = 5.0, issuance_ms: float = 50.0,
         send_intermediate: bool = True, min_level: int = 1, stored_pk_max: int = 10**9,
         leaf_allowed=lambda s: True) -> Assignment:
    """Smallest bill over every assignment of schemes to roles, under explicit constraints:
    online_ms:     the leaf signs every handshake, so it must sign fast;
    issuance_ms:   the intermediate and the logs sign every certificate issued;
    stored_pk_max: root and log keys live in every client, so their size is not free either.
    Ties are broken by the order of the catalog, so the result is the same on every machine."""
    pool = [s for s in schemes if allowed(s) and s.level >= min_level]
    fast = lambda s, limit: not (s.sign_ms > limit)  # unknown timings (nan) count as fast enough
    stored = lambda s: s.pk <= stored_pk_max
    found = None
    for leaf, inter, root, log in itertools.product(pool, repeat=4):
        if not (leaf_allowed(leaf) and fast(leaf, online_ms) and fast(inter, issuance_ms) and fast(log, issuance_ms)):
            continue
        if not (stored(root) and stored(log) and (send_intermediate or stored(inter))):
            continue
        if not send_intermediate:
            root = inter  # unused: keep the label honest
        a = Assignment(leaf, inter, root, log, send_intermediate)
        if found is None or a.auth < found.auth:
            found = a
    return found


# --------------------------------------------------------------------------- report

def fmt(x: float) -> str:
    return f"{x:,.0f}"


def main(measure: bool = True) -> int:
    schemes, note = catalog(measure)
    by = {s.name: s for s in schemes}
    print(f"== the menu ({note}) ==")
    print(f"  {'scheme':20s} {'status':15s} {'cat':>3s} {'public key':>11s} {'signature':>10s} {'pk+sig':>8s} {'sign ms':>9s} {'verify ms':>9s}")
    for s in schemes:
        cat = "-" if s.level == 0 else str(s.level)
        star = "*" if (s.measured == "table" and measure) else " "
        sm = f"{s.sign_ms:8.3f}{star}"
        vm = f"{s.verify_ms:8.3f}{star}"
        print(f"  {s.name:20s} {s.status:15s} {cat:>3s} {fmt(s.pk):>11s} {fmt(s.sig):>10s} {fmt(s.pk + s.sig):>8s} {sm} {vm}")

    print("\n== the model against Part 02's measured bills ==")
    for name, measured in (("ML-DSA-44", 15802), ("ML-DSA-65", 21527)):
        s = by[name]
        a = Assignment(s, s, s, s)
        print(f"  {name} everywhere: model {fmt(a.auth)} B, Part 02 measured {fmt(measured)} B,"
              f" flight {fmt(a.flight)} B (Part 02: {'17,169' if name.endswith('44') else '22,916'})")

    print("\n== one scheme for every role ==")
    print(f"  {'scheme':20s} {'auth bytes':>10s} {'flight':>8s}  {'TCP 14,600':>10s}  {'QUIC ~7,200':>11s}")
    for s in schemes:
        if s.level == 0 and s.name != "ECDSA P-256":
            continue
        a = Assignment(s, s, s, s)
        print(f"  {s.name:20s} {fmt(a.auth):>10s} {fmt(a.flight):>8s}  {'fits' if a.flight <= TCP_WINDOW else 'NO':>10s}"
              f"  {'fits' if a.flight <= QUIC_BUDGET else 'NO':>11s}")

    print("\n== mixing schemes by role (smallest bill under the constraints) ==")
    fips = lambda s: s.status.startswith("FIPS")
    standards = lambda s: s.status.startswith("FIPS") or s.status.startswith("draft FIPS")
    anything = lambda s: s.level >= 1
    no_falcon_online = lambda s: not s.name.startswith("Falcon")
    rows = [
        ("final FIPS only (ML-DSA, SLH-DSA)", best(schemes, fips)),
        ("+ draft FIPS 206 (Falcon)", best(schemes, standards)),
        ("+ draft, but no Falcon for the online leaf", best(schemes, standards, leaf_allowed=no_falcon_online)),
        ("+ round-3 candidates", best(schemes, anything)),
        ("+ round-3, stored keys at most 64 KB", best(schemes, anything, stored_pk_max=65536)),
    ]
    for label, a in rows:
        print(f"  {label:44s} {fmt(a.auth):>7s} B  flight {fmt(a.flight):>6s}   {a.label()}")
    mixed = rows[2][1]

    print("\n== the same, when the client already has the intermediate ==")
    for label, kw in (("final FIPS only", dict(allowed=fips)), ("+ draft FIPS 206", dict(allowed=standards)),
                      ("+ round-3, stored keys at most 64 KB", dict(allowed=anything, stored_pk_max=65536))):
        a = best(schemes, send_intermediate=False, **kw)
        print(f"  {label:44s} {fmt(a.auth):>7s} B  flight {fmt(a.flight):>6s}   {a.label()}")

    print("\n== where the bytes go in three bills ==")
    picks = [Assignment(*(by["ML-DSA-44"],) * 4), mixed, rows[4][1]]
    keys = ["leaf public key", "CertificateVerify", "leaf certificate signature", "2 SCTs",
            "intermediate public key", "intermediate certificate signature", "structure"]
    print(f"  {'':36s}" + "".join(f"{x:>14s}" for x in ("ML-DSA-44", "ML-DSA+Falcon", "round 3")))
    for k in keys:
        print(f"  {k:36s}" + "".join(f"{fmt(a.parts().get(k, 0)):>14s}" for a in picks))
    print(f"  {'total':36s}" + "".join(f"{fmt(a.auth):>14s}" for a in picks))

    print("\n== hybrids: ML-DSA-44 + ECDSA P-256 in every role (composite keys and signatures) ==")
    m, e = by["ML-DSA-44"], by["ECDSA P-256"]
    hy = Scheme("composite", "lattice+EC", "draft", 2, m.pk + e.pk, m.sig + e.sig)
    a = Assignment(hy, hy, hy, hy)
    print(f"  {fmt(a.auth)} B, +{fmt(a.auth - Assignment(m, m, m, m).auth)} B over pure ML-DSA-44, flight {fmt(a.flight)} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(measure="--table" not in sys.argv))
