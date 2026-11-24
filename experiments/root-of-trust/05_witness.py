"""Root of Trust, part 05: notes, checkpoints, witnesses.

The formats and protocol that real transparency logs use today (Go's checksum
database, Sigsum, Sigstore, modern CT logs), written from the C2SP specs:

  * signed notes       c2sp.org/signed-note        text + signature lines
  * checkpoints        c2sp.org/tlog-checkpoint    origin, size, root hash
  * cosignatures       c2sp.org/tlog-cosignature   cosignature/v1, Ed25519
  * witnesses          c2sp.org/tlog-witness       add-checkpoint and its checks

Then a log that tries Part 04's split view against a set of witnesses, the
quorum arithmetic that decides when it can succeed, and the freshness that
timestamps buy.

Run:  python 05_witness.py        (needs: pip install cryptography)
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import pathlib
import struct
import sys
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("merkle04", HERE / "04_merkle.py")
mk = importlib.util.module_from_spec(_spec)
sys.modules["merkle04"] = mk
_spec.loader.exec_module(mk)

EM_DASH = "—"  # the signature line marker. Literally U+2014, by the spec.


def raw(pub: Ed25519PublicKey) -> bytes:
    return pub.public_bytes(Encoding.Raw, PublicFormat.Raw)


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


# --------------------------------------------------------------------------- signed notes

def key_id(name: str, sig_type: int, pub: bytes) -> bytes:
    """SHA-256(key name || 0x0A || signature type || public key)[:4]"""
    return hashlib.sha256(name.encode() + b"\n" + bytes([sig_type]) + pub).digest()[:4]


@dataclass
class Verifier:
    """A key a client trusts for notes. sig_type 0x01: plain Ed25519 note signature;
    0x04: a timestamped cosignature/v1 (the message gets a header, see cosign())."""
    name: str
    pub: Ed25519PublicKey
    sig_type: int = 0x01

    @property
    def kid(self) -> bytes:
        return key_id(self.name, self.sig_type, raw(self.pub))

    def vkey(self) -> str:
        """<name>+hex(key ID)+base64(signature type || public key)"""
        return f"{self.name}+{self.kid.hex()}+{b64(bytes([self.sig_type]) + raw(self.pub))}"

    @classmethod
    def parse(cls, vkey: str) -> "Verifier":
        name, kid_hex, material = vkey.split("+", 2)  # base64 may contain "+"; names may not
        blob = base64.b64decode(material)
        v = cls(name, Ed25519PublicKey.from_public_bytes(blob[1:]), blob[0])
        if v.kid.hex() != kid_hex:
            raise ValueError("key ID does not match the key")
        return v

    def check(self, text: str, sig: bytes) -> bool:
        """sig is the decoded signature value, key ID already stripped."""
        try:
            if self.sig_type == 0x01:
                self.pub.verify(sig, text.encode())
                return True
            if self.sig_type == 0x04:
                (ts,) = struct.unpack(">Q", sig[:8])
                self.pub.verify(sig[8:], cosigned_message(text, ts))
                return True
        except InvalidSignature:
            return False
        return False


def sign_note(text: str, name: str, sk: Ed25519PrivateKey) -> str:
    """A note is text ending in a newline, a blank line, then signature lines."""
    assert text.endswith("\n") and name and " " not in name and "+" not in name
    sig = key_id(name, 0x01, raw(sk.public_key())) + sk.sign(text.encode())
    return f"{text}\n{EM_DASH} {name} {b64(sig)}\n"


def split_note(note: str) -> tuple[str, list[tuple[str, bytes, bytes]]]:
    """Return the text and (name, key ID, signature) for each signature line.
    The text ends at the LAST blank line: the text itself may contain blank lines."""
    i = note.rstrip("\n").rfind("\n\n")
    if i < 0:
        raise ValueError("no blank line before the signatures")
    text, sigs = note[: i + 1], note[i + 2 :]
    out = []
    for line in sigs.splitlines():
        if not line.startswith(EM_DASH + " "):
            raise ValueError(f"bad signature line: {line!r}")
        name, value = line[2:].rsplit(" ", 1)
        blob = base64.b64decode(value)
        out.append((name, blob[:4], blob[4:]))
    return text, out


def open_note(note: str, verifiers: list[Verifier]) -> tuple[str, list[Verifier]]:
    """The spec's rules: ignore unknown keys; a known key MUST verify; at least one must."""
    text, sigs = split_note(note)
    known = {(v.name, v.kid): v for v in verifiers}
    good = []
    for name, kid, sig in sigs:
        v = known.get((name, kid))
        if v is None:
            continue  # unknown key, even if the name or the ID alone matches: ignore
        if not v.check(text, sig):
            raise ValueError(f"signature from known key {name} does not verify")
        good.append(v)
    if not good:
        raise ValueError("no signature from a known key")
    return text, good


# --------------------------------------------------------------------------- checkpoints

def checkpoint_body(origin: str, size: int, root: bytes) -> str:
    """origin line, tree size in decimal, root hash in base64. Each line ends in a newline."""
    return f"{origin}\n{size}\n{b64(root)}\n"


def parse_checkpoint(text: str) -> tuple[str, int, bytes]:
    lines = text.split("\n")
    return lines[0], int(lines[1]), base64.b64decode(lines[2])


# --------------------------------------------------------------------------- cosignatures

def cosigned_message(checkpoint_text: str, timestamp: int) -> bytes:
    """c2sp.org/tlog-cosignature: two header lines, then the whole checkpoint body."""
    return f"cosignature/v1\ntime {timestamp}\n".encode() + checkpoint_text.encode()


def cosign(checkpoint_text: str, name: str, sk: Ed25519PrivateKey, timestamp: int) -> str:
    """Signature line value: key ID (4) || u64 timestamp (8) || Ed25519 signature (64)."""
    kid = key_id(name, 0x04, raw(sk.public_key()))
    sig = sk.sign(cosigned_message(checkpoint_text, timestamp))
    return f"{EM_DASH} {name} {b64(kid + struct.pack('>Q', timestamp) + sig)}\n"


# --------------------------------------------------------------------------- the witness

class WitnessError(Exception):
    def __init__(self, status: int, why: str):
        super().__init__(f"{status} {why}")
        self.status = status


@dataclass
class Witness:
    """c2sp.org/tlog-witness, the add-checkpoint checks in the order the spec lists them.
    State: for each log, the latest checkpoint it cosigned. Nothing else."""
    name: str
    sk: Ed25519PrivateKey
    logs: dict  # origin -> Verifier of the log's key
    state: dict = field(default_factory=dict)  # origin -> (size, root)
    honest: bool = True

    @property
    def verifier(self) -> Verifier:
        return Verifier(self.name, self.sk.public_key(), 0x04)

    def add_checkpoint(self, old: int, proof: list[bytes], note: str, now: int) -> str:
        text, _ = split_note(note)
        origin, size, root = parse_checkpoint(text)
        if origin not in self.logs:
            raise WitnessError(404, "unknown log")
        try:
            open_note(note, [self.logs[origin]])
        except ValueError:
            raise WitnessError(403, "not signed by the log")
        if not self.honest:  # a compromised witness signs whatever it is shown
            return cosign(text, self.name, self.sk, now)
        if old > size:
            raise WitnessError(400, "old size is larger than the checkpoint")
        have_size, have_root = self.state.get(origin, (0, mk.sha256(b"")))
        if old != have_size:
            raise WitnessError(409, f"{have_size}")  # body: the size the witness has
        if size == 0 and root != mk.sha256(b""):
            raise WitnessError(422, "empty tree with a non-empty root")
        if old == 0 and proof:
            raise WitnessError(422, "proof from the empty tree must be empty")
        if old == size and root != have_root:
            raise WitnessError(422, "same size, different root: a fork")
        if 0 < old < size and not mk.verify_consistency(old, size, have_root, root, proof):
            raise WitnessError(422, "consistency proof does not verify")
        self.state[origin] = (size, root)  # persist BEFORE answering
        return cosign(text, self.name, self.sk, now)


# --------------------------------------------------------------------------- the log

@dataclass
class Log:
    origin: str
    sk: Ed25519PrivateKey
    entries: list = field(default_factory=list)

    @property
    def verifier(self) -> Verifier:
        return Verifier(self.origin, self.sk.public_key(), 0x01)

    def checkpoint(self, entries=None) -> str:
        es = self.entries if entries is None else entries
        return sign_note(checkpoint_body(self.origin, len(es), mk.mth(es)), self.origin, self.sk)

    def witness(self, w: Witness, entries=None, now: int = 0, old: int | None = None) -> str:
        """Ask a witness to cosign; on 409, retry once from the size the witness reports."""
        es = self.entries if entries is None else entries
        note = self.checkpoint(es)
        old = w.state.get(self.origin, (0, b""))[0] if old is None else old
        try:
            return w.add_checkpoint(old, mk.proof(old, es) if 0 < old < len(es) else [], note, now)
        except WitnessError as e:
            if e.status != 409:
                raise
            old = int(str(e).split()[1])
            return w.add_checkpoint(old, mk.proof(old, es) if 0 < old < len(es) else [], note, now)


# --------------------------------------------------------------------------- the client

def client_accepts(note_with_cosigs: str, log: Verifier, witnesses: list[Verifier], k: int,
                   now: int | None = None, max_age: int | None = None) -> tuple[bool, str]:
    """Trust a checkpoint only if the log signed it and at least k known witnesses cosigned it,
    and (optionally) if enough of those cosignatures are recent."""
    text, sigs = split_note(note_with_cosigs)
    try:
        open_note(note_with_cosigs, [log])
    except ValueError as e:
        return False, f"log signature: {e}"
    known = {(w.name, w.kid): w for w in witnesses}
    good = 0
    for name, kid, sig in sigs:
        w = known.get((name, kid))
        if w and w.check(text, sig):
            ts = struct.unpack(">Q", sig[:8])[0]
            if max_age is None or now - ts <= max_age:
                good += 1
    return (good >= k), f"{good} of {len(witnesses)} witnesses (need {k})"


# --------------------------------------------------------------------------- the story

def key(label: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(f"root-of-trust part 05: {label}".encode()).digest())


SPEC_VKEY = "example.com/foo+530d903a+AekyeRrm56hApGFkyQR4ZCbV54Id2LKaANYcrnKv3U2k"
SPEC_NOTE = ("This is an example message.\n\n"
             f"{EM_DASH} example.com/foo Uw2QOkn8srV1yJGh2VYRlL1Tnagv1YEq6TfXppzi2ONncAlTgK7Ztg1ERYNZXsYjOBH3mFXmRKuwHjG1Yu72IneyaQM=\n")
SPEC_COSIG = ("jWbPPwAAAABkGFDLEZMHwSRaJNiIDoe9DYn/zXcrtPHeolMI5OWXEhZCB9dlrDJsX3b2oyin1nPZ"
              "qhf5nNo0xUe+mbIUBkBIfZ+qnA==")


def world(n_witnesses: int = 3, dishonest: int = 0):
    log = Log("example.com/log", key("log"))
    ws = [Witness(f"witness-{c}.example", key(f"witness {c}"), {log.origin: log.verifier})
          for c in "abcdefg"[:n_witnesses]]
    for w in ws[:dishonest]:
        w.honest = False
    return log, ws


def scenarios() -> list[tuple[str, str]]:
    out = []
    certs = [f"cert {i}".encode() for i in range(2000)]
    rogue = b"rogue cert for example.com"

    # 1. Normal life: the log grows, the witnesses check each step and cosign.
    log, ws = world()
    for step in (100, 250, 1000):
        log.entries = certs[:step]
        lines = [log.witness(w, now=1000 + step) for w in ws]
    note = log.checkpoint() + "".join(lines)
    ok, why = client_accepts(note, log.verifier, [w.verifier for w in ws], k=2)
    out.append(("1. log grows 100 -> 250 -> 1000, 3 witnesses", f"{'ACCEPT' if ok else 'REJECT'}: {why}"))

    # 2. The split view of Part 04: fork after entry 1000. Every witness already holds 1000.
    #    The fork must extend from what they hold, so it must contain the same first 1000 entries.
    main = certs[:1500]
    fork = certs[:1000] + [rogue] + certs[1000:1499]
    for w in ws:
        log.witness(w, main, now=3000)          # the world sees the main branch at 1500
    refused = []
    for w in ws:
        try:
            log.witness(w, fork, now=3001)      # now try to get the fork (also size 1500) cosigned
        except WitnessError as e:
            refused.append(e.status)
    out.append(("2. split view: fork at 1500 after main at 1500", f"every witness refuses: {refused} (same size, different root)"))

    # 3. A bigger fork: does a larger size help? It must be consistent with main at 1500, and isn't.
    bigger = fork + certs[1499:1800]
    refused = []
    for w in ws:
        try:
            log.witness(w, bigger, now=3002)
        except WitnessError as e:
            refused.append(e.status)
    out.append(("3. split view: fork grown to 1800", f"every witness refuses: {refused} (no consistency proof exists)"))

    # 4. The log partitions the witnesses: main to a and b, fork to c. Client needs 2 of 3.
    log, ws = world()
    log.entries = certs[:1000]
    for w in ws:
        log.witness(w, now=100)
    main = certs[:1500]
    fork = certs[:1000] + [rogue] + certs[1000:1499]
    main_note = log.checkpoint(main) + "".join(log.witness(w, main, now=200) for w in ws[:2])
    fork_note = log.checkpoint(fork) + log.witness(ws[2], fork, now=200)
    vs = [w.verifier for w in ws]
    ok_m, why_m = client_accepts(main_note, log.verifier, vs, k=2)
    ok_f, why_f = client_accepts(fork_note, log.verifier, vs, k=2)
    out.append(("4. witnesses partitioned 2 | 1, client needs 2 of 3",
                f"main {'ACCEPT' if ok_m else 'REJECT'} ({why_m}); fork {'ACCEPT' if ok_f else 'REJECT'} ({why_f})"))

    # 5. Same, but one witness is compromised and cosigns both branches.
    log, ws = world(dishonest=1)
    log.entries = certs[:1000]
    for w in ws:
        log.witness(w, now=100)
    main_note = log.checkpoint(main) + "".join(log.witness(w, main, now=200) for w in (ws[0], ws[1]))
    fork_note = log.checkpoint(fork) + "".join(log.witness(w, fork, now=200) for w in (ws[0], ws[2]))
    vs = [w.verifier for w in ws]
    ok_m, _ = client_accepts(main_note, log.verifier, vs, k=2)
    ok_f, _ = client_accepts(fork_note, log.verifier, vs, k=2)
    out.append(("5. one witness compromised, client needs 2 of 3",
                f"main {'ACCEPT' if ok_m else 'REJECT'}, fork {'ACCEPT' if ok_f else 'REJECT'}: both pass, the quorum was too small"))

    # 6. Same attack, client needs 3 of 3.
    ok_m, _ = client_accepts(main_note, log.verifier, vs, k=3)
    ok_f, _ = client_accepts(fork_note, log.verifier, vs, k=3)
    out.append(("6. same, client needs 3 of 3",
                f"main {'ACCEPT' if ok_m else 'REJECT'}, fork {'ACCEPT' if ok_f else 'REJECT'}: safe, but one silent witness now blocks everyone"))

    # 7. Freeze: the log keeps serving an old, honestly cosigned checkpoint to one victim.
    log, ws = world()
    log.entries = certs[:1000]
    old_note = log.checkpoint() + "".join(log.witness(w, now=1_000) for w in ws)
    vs = [w.verifier for w in ws]
    ok_a, _ = client_accepts(old_note, log.verifier, vs, k=2, now=1_000 + 30 * 86400)
    ok_b, why_b = client_accepts(old_note, log.verifier, vs, k=2, now=1_000 + 30 * 86400, max_age=86400)
    out.append(("7. freeze: a month-old checkpoint, no age limit", f"{'ACCEPT' if ok_a else 'REJECT'}"))
    out.append(("8. freeze: same, cosignatures must be < 1 day old", f"{'ACCEPT' if ok_b else 'REJECT'}: {why_b}"))
    return out


def quorum_table(n: int = 5) -> list[tuple[int, int, bool]]:
    """Can a log get two conflicting checkpoints each cosigned by k of n witnesses, when f of
    them are compromised? Honest witnesses cosign at most one branch; compromised ones sign both.
    Brute force over every way of splitting the honest witnesses between the branches."""
    rows = []
    for f in range(n + 1):
        h = n - f
        for k in range(1, n + 1):
            possible = any(f + a >= k and f + (h - a) >= k for a in range(h + 1))
            assert possible == (2 * k <= n + f)  # the closed form the article derives
            rows.append((f, k, possible))
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # signature lines contain an em dash (U+2014)
    print("== the signed-note spec's own example ==")
    v = Verifier.parse(SPEC_VKEY)
    text, good = open_note(SPEC_NOTE, [v])
    print(f"  vkey parses, key ID {v.kid.hex()} matches; note verifies: {text!r} signed by {good[0].name}")
    blob = base64.b64decode(SPEC_COSIG)
    print(f"  the cosignature spec's example line: {len(blob)} bytes = key ID {blob[:4].hex()}"
          f" | timestamp {struct.unpack('>Q', blob[4:12])[0]} | signature {len(blob[12:])} bytes")

    print("\n== a checkpoint, signed by the log and cosigned by three witnesses ==")
    log, ws = world()
    log.entries = [f"cert {i}".encode() for i in range(1000)]
    note = log.checkpoint() + "".join(log.witness(w, now=1_763_650_000) for w in ws)
    print("  " + note.replace("\n", "\n  ").rstrip())
    print(f"  ({len(note.encode())} bytes)")
    print("  log vkey:    ", log.verifier.vkey())
    print("  witness vkey:", ws[0].verifier.vkey())

    print("\n== the witness checks, one bad request each ==")
    w = ws[0]
    good_note = log.checkpoint()
    stranger = Log("other.example/log", key("other"))
    attempts = [
        ("unknown log", lambda: w.add_checkpoint(0, [], stranger.checkpoint(), 0)),
        ("signed by the wrong key", lambda: w.add_checkpoint(1000, [], sign_note(split_note(good_note)[0], log.origin, key("impostor")), 0)),
        ("old size > new size", lambda: w.add_checkpoint(5000, [], good_note, 0)),
        ("old size the witness never saw", lambda: w.add_checkpoint(400, [], good_note, 0)),
        ("same size, different root", lambda: w.add_checkpoint(1000, [], log.checkpoint(log.entries[:999] + [b"x"]), 0)),
        ("bad consistency proof", lambda: w.add_checkpoint(1000, [b"\0" * 32] * 11, log.checkpoint(log.entries + [b"y"]), 0)),
    ]
    for label, call in attempts:
        try:
            call()
            print(f"  {label:32s} -> accepted?!")
        except WitnessError as e:
            print(f"  {label:32s} -> {e}")

    print("\n== split views against witnesses ==")
    for label, verdict in scenarios():
        print(f"  {label:50s} {verdict}")

    print("\n== quorum: can two conflicting checkpoints both reach k of 5 cosignatures? ==")
    rows = quorum_table(5)
    print("  compromised  " + "  ".join(f"k={k}" for k in range(1, 6)))
    for f in range(0, 4):
        cells = ["fork" if p else " -  " for (ff, k, p) in rows if ff == f]
        print(f"  f = {f}        " + "  ".join(cells))
    print("  a fork is possible exactly when 2k <= n + f")

    print("\n== the bill: a checkpoint with cosignatures ==")
    for alg, sig, extra in (("Ed25519", 64, 8), ("ML-DSA-44", 2420, 8)):
        per = len(f"{EM_DASH} witness-a.example ".encode()) + len(b64(bytes(4 + extra + sig))) + 1
        print(f"  {alg:10s} one cosignature line: {per:>5,} bytes   three: {3 * per:>6,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
