"""Root of Trust, part 08: subtree consistency and landmarks.

Part 07 handed the relying party its landmark subtrees and said "trust these".
This part builds what stands behind that sentence, from
draft-ietf-plants-merkle-tree-certs-07:

  * subtree consistency proofs (§4.4): generating and verifying them, checked
    against the draft's examples and its Appendix C.1.2 and C.1.3 test vectors;
  * cosigned checkpoints: a CosignedSubtree [0, n) with a nonzero timestamp (§5.3);
  * landmarks with expirations (§6.4.1, §6.4.2), and a week of hourly landmarks;
  * an update service that validates landmarks before shipping them (§7.4),
    with the draft's own example of a lagging cosigner;
  * attacks: a forged landmark subtree, a forked log, too many landmarks;
  * how stale a client can be and still get the small certificate.

Run:  python 08_landmarks.py        (needs: pip install "cryptography>=46")
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import pathlib
import random
import sys
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("mtc07", HERE / "07_mtc.py")
m7 = importlib.util.module_from_spec(_spec)
sys.modules["mtc07"] = m7
_spec.loader.exec_module(m7)
mk = m7.mk                                   # Part 04: mth, path, proof, verify_consistency, node_hash

EMPTY_HASH = hashlib.sha256(b"").digest()    # MTH of the empty list


# --------------------------------------------------------------------------- subtree consistency proofs (§4.4)

def _k(n: int) -> int:
    """Largest power of two strictly smaller than n (n >= 2)."""
    return 1 << ((n - 1).bit_length() - 1)


def subtree_proof(start: int, end: int, d: list[bytes]) -> list[bytes]:
    """§4.4.1 SUBTREE_PROOF(start, end, D_n): proves MTH(D[start:end]) is a node of the tree MTH(D_n)."""
    return _subtree_subproof(start, end, d, True)


def _subtree_subproof(start: int, end: int, d: list[bytes], b: bool) -> list[bytes]:
    n = len(d)
    if start == end:
        return []                                   # the empty subtree: an empty proof
    if start == 0 and end == n:
        return [] if b else [mk.mth(d)]             # b: the verifier already knows this hash
    k = _k(n)
    if end <= k:                                    # entirely in the left half
        return _subtree_subproof(start, end, d[:k], b) + [mk.mth(d[k:])]
    if k <= start:                                  # entirely in the right half
        return _subtree_subproof(start - k, end - k, d[k:], b) + [mk.mth(d[:k])]
    # straddles k: only possible with start == 0 (a valid subtree), like a consistency proof
    return _subtree_subproof(0, end - k, d[k:], False) + [mk.mth(d[:k])]


def verify_subtree_consistency(n: int, start: int, end: int, proof: list[bytes],
                               node: bytes, root: bytes, trace: list | None = None) -> bool:
    """§4.4.3: is `node` the hash of [start, end) in the tree of size n whose hash is `root`?

    Two running hashes: fr rebuilds the subtree (from the parts of the proof inside it),
    sr rebuilds the whole tree. fn, sn, tn are the positions of start, end - 1 and n - 1,
    shifted up one level at a time."""
    if not (m7.valid_subtree(start, end) and end <= n):
        return False
    if start == end:
        return not proof and node == EMPTY_HASH
    fn, sn, tn = start, end - 1, n - 1
    if sn == tn:                                     # the subtree is on the right edge
        while fn != sn:
            fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
    else:                                            # climb while end - 1 is a right child
        while fn != sn and sn & 1:
            fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
    proof = list(proof)
    if fn == sn:                                     # the subtree is one node: start from its hash
        fr = sr = node
    else:                                            # a partial subtree: its right part comes first
        if not proof:
            return False
        fr = sr = proof.pop(0)
    if trace is not None:
        trace.append(("start", fn, sn, tn, None))
    for c in proof:
        if tn == 0:
            return False                             # proof too long
        if sn & 1 or sn == tn:                       # c is a left sibling
            if fn < sn:
                fr = mk.node_hash(c, fr)             # still inside the subtree
            sr = mk.node_hash(c, sr)
            step = "left"
            while not sn & 1:
                fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
        else:                                        # c is a right sibling: outside the subtree
            sr = mk.node_hash(sr, c)
            step = "right"
        fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
        if trace is not None:
            trace.append((step, fn, sn, tn, c))
    return tn == 0 and fr == node and sr == root


def subtree_inclusion(start: int, end: int, index: int, d: list[bytes]) -> list[bytes]:
    """§4.3.1: Part 04's path, inside the subtree."""
    return mk.path(index - start, d[start:end])


# --------------------------------------------------------------------------- the draft's vectors (Appendix C.1.2, C.1.3)

APPENDIX_C = {"C.1.2 subtree inclusion proofs": "ac2a8f989e44d99e399db448050ff5f19757df53cfb716aa81015d3955d8163f",
              "C.1.3 subtree consistency proofs": "10fa99b37bf9bf9ffa26b412fbd98bd75363256d0b75d61bc4538b9c9c5a0a74"}


def appendix_c1(which: str, max_n: int = 130) -> str:
    d = [bytes([i]) for i in range(max_n + 1)]
    h = hashlib.sha256()
    if which.startswith("C.1.2"):
        for end in range(max_n + 1):
            for start in range(end + 1):
                if m7.valid_subtree(start, end):
                    for index in range(start, end):
                        line = f"{index} [{start}, {end})" + "".join(" " + p.hex() for p in subtree_inclusion(start, end, index, d))
                        h.update((line + "\n").encode())
    else:
        for n in range(max_n + 1):
            for end in range(n + 1):
                for start in range(end + 1):
                    if m7.valid_subtree(start, end):
                        line = f"[{start}, {end}) {n}" + "".join(" " + p.hex() for p in subtree_proof(start, end, d[:n]))
                        h.update((line + "\n").encode())
    return h.hexdigest()


# --------------------------------------------------------------------------- a log with landmarks (§5.3, §6.4)

HOUR = 3600
LIFETIME = 7 * 24 * HOUR                       # max_cert_lifetime in the draft's example


@dataclass
class Landmark:
    number: int
    tree_size: int
    expiration: int                            # seconds; must cover every entry below tree_size


@dataclass
class LandmarkCA:
    """A CA whose log grows over time and which allocates landmarks as in §6.4.2."""
    entries: list = field(default_factory=lambda: [m7.null_entry()])
    landmarks: list = field(default_factory=lambda: [Landmark(0, 0, 0)])   # landmark zero: never active
    cosigners: list = field(default_factory=list)                          # m7.Cosigner, CA first

    def __post_init__(self):
        if not self.cosigners:
            self.cosigners = [m7.Cosigner(m7.CA_ID, m7.key("ca cosigner"))] + [
                m7.Cosigner(a, m7.key(f"witness {a[-1]}")) for a in m7.WITNESS_IDS]

    def grow(self, k: int, tag: str = "") -> None:
        base = len(self.entries)
        self.entries += [m7.mtc_log_entry(f"certificate {base + i} {tag}".encode()) for i in range(k)]

    def allocate_landmark(self, now: int) -> Landmark | None:
        """§6.4.2: at most once per interval, append a landmark if the tree grew."""
        if len(self.entries) == self.landmarks[-1].tree_size:
            return None
        lm = Landmark(len(self.landmarks), len(self.entries), now + LIFETIME)
        self.landmarks.append(lm)
        return lm

    def subtrees(self, lm: Landmark) -> list[tuple[int, int]]:
        prev = self.landmarks[lm.number - 1].tree_size
        return [s for s in m7.covering_subtrees(prev, lm.tree_size) if s[0] < s[1]]

    def active(self, now: int) -> list[Landmark]:
        return [l for l in self.landmarks[1:] if l.expiration > now]


def cosign_checkpoint(c: m7.Cosigner, n: int, root: bytes, timestamp: int) -> bytes:
    """§5.3: a cosignature with a nonzero timestamp is a checkpoint, [0, n) of the cosigner's view."""
    assert timestamp != 0
    if c.honest and mk.mth(c.mirror[:n]) != root:
        raise ValueError(f"{m7.origin(c.arcs)}: checkpoint {n} does not match my view")
    return c.sk.sign(m7.cosigned_subtree(c.arcs, 0, n, root, timestamp))


# --------------------------------------------------------------------------- the update service (§7.4)

@dataclass
class Bundle:
    """What the CA (or anyone) hands the update service for one log."""
    landmarks: list                            # Landmark, oldest first
    subtrees: dict                             # landmark number -> [((start, end), hash), ...]
    reference: tuple                           # (n, root)
    cosigs: dict                               # cosigner id -> (n_c, root_c, timestamp, signature, proof from reference to n_c)
    sub_proofs: dict                           # (start, end) -> subtree consistency proof against the reference


def make_bundle(ca: LandmarkCA, now: int, reference_size: int | None = None) -> Bundle:
    n = reference_size or len(ca.entries)
    root = mk.mth(ca.entries[:n])
    act = ca.active(now)
    subs = {l.number: [(s, mk.mth(ca.entries[s[0]:s[1]])) for s in ca.subtrees(l)] for l in act}
    proofs = {s: subtree_proof(*s, ca.entries[:n]) for l in act for s, _ in subs[l.number] if s[1] <= n}
    cosigs = {}
    for c in ca.cosigners:
        seen = len(c.mirror)                  # each cosigner signs the largest tree it has checked
        if seen < n:
            continue                          # this cosigner has not seen the reference yet
        r = mk.mth(c.mirror[:seen])
        cosigs[c.id_bytes] = (seen, r, now, cosign_checkpoint(c, seen, r, now), mk.proof(n, ca.entries[:seen]))
    return Bundle(act, subs, (n, root), cosigs, proofs)


@dataclass
class UpdateService:
    """Validates landmarks for relying parties, then ships the trusted subtrees."""
    cosigners: dict                            # id -> (arcs, public key)
    ca_id: bytes
    witness_quorum: int = 1
    max_landmarks: int = 200                   # "some upper bound" per CA (§7.4)

    def checkpoint_ok(self, b: Bundle) -> tuple[bool, str]:
        n, root = b.reference
        ok_ca, ok_w = False, 0
        for cid, (n_c, root_c, ts, sig, prf) in b.cosigs.items():
            if cid not in self.cosigners:
                continue
            arcs, pub = self.cosigners[cid]
            try:
                pub.verify(sig, m7.cosigned_subtree(arcs, 0, n_c, root_c, ts))
            except Exception:
                continue
            if not mk.verify_consistency(n, n_c, root, root_c, prf):   # RFC 9162 §2.1.4
                continue
            ok_ca |= cid == self.ca_id
            ok_w += cid != self.ca_id
        if not ok_ca:
            return False, "no valid CA cosignature on a checkpoint containing the reference"
        if ok_w < self.witness_quorum:
            return False, f"only {ok_w} witness(es) vouch for the reference, need {self.witness_quorum}"
        return True, f"reference checkpoint {n} vouched for by the CA and {ok_w} witness(es)"

    def validate(self, b: Bundle) -> tuple[list, list[str]]:
        """Returns the trusted subtrees ((start, end), hash) and a log of decisions."""
        notes = []
        ok, why = self.checkpoint_ok(b)
        notes.append(why)
        if not ok:
            return [], notes + ["nothing trusted"]
        n, root = b.reference
        kept = []
        for lm in b.landmarks:                                     # oldest first
            good = lm.tree_size <= n and all(
                verify_subtree_consistency(n, s[0], s[1], b.sub_proofs.get(s, []), h, root)
                for s, h in b.subtrees[lm.number])
            if not good:
                why = "beyond the reference checkpoint" if lm.tree_size > n else "subtree inconsistent with the checkpoint"
                rest = [l.number for l in b.landmarks if l.number >= lm.number]
                notes.append(f"landmark {lm.number} (size {lm.tree_size}): {why}; discard landmarks {rest[0]}..{rest[-1]}")
                break                                              # §7.4: and every newer one
            kept.append(lm)
        if len(kept) > self.max_landmarks:
            notes.append(f"{len(kept)} landmarks exceed the cap of {self.max_landmarks}: keep the oldest")
            kept = kept[: self.max_landmarks]                      # §7.4: discard the newest
        trusted = [(s, h) for lm in kept for s, h in b.subtrees[lm.number]]
        span = f"{kept[0].number}..{kept[-1].number}" if kept else "none"
        notes.append(f"trusted: landmarks {span} ({len(kept)}) -> {len(trusted)} subtrees, {32 * len(trusted):,} bytes")
        return trusted, notes


# --------------------------------------------------------------------------- how stale can a client be?

def lr_share(staleness_h: float, delay_h: float = 1.0, renew_frac: float = 0.75,
             lifetime_h: float = 168, interval_h: float = 1.0, trials: int = 20000, seed: int = 8) -> float:
    """Fraction of handshakes that can use a landmark-relative certificate.

    The server renews every renew_frac * lifetime and keeps every unexpired certificate
    (§10.4). A certificate issued at t becomes landmark-relative at the next landmark,
    and reaches clients delay_h later. A client whose last update was staleness_h ago
    holds every landmark up to then. It gets the small certificate if some unexpired
    certificate's landmark is one it holds."""
    rnd = random.Random(seed)
    period = renew_frac * lifetime_h
    hits = 0
    for _ in range(trials):
        phase = rnd.uniform(0, period)                 # time since the latest renewal
        client_has = -staleness_h                      # client holds landmarks published up to now - staleness
        ok = False
        for i in range(int(lifetime_h / period) + 2):
            t = -phase - i * period                     # issuance times, newest first
            if t + lifetime_h <= 0:
                break                                   # expired
            ready = math.ceil(t / interval_h) * interval_h + delay_h
            if ready <= client_has:
                ok = True
                break
        hits += ok
    return hits / trials


def expected_auth(share: float, small: int = 4296, big: int = 11417) -> float:
    """Part 07's handshake sizes: landmark-relative versus standalone (CA + 2 witnesses)."""
    return share * small + (1 - share) * big


# --------------------------------------------------------------------------- report

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    d14 = [bytes([i]) for i in range(14)]
    name = {mk.mth(d14[a:b]): f"D[{a}:{b}]" for a in range(14) for b in range(a + 1, 15) if m7.valid_subtree(a, b)}

    print("== subtree consistency proofs: the draft's examples (tree of size 14) ==")
    for s in ((4, 8), (8, 13)):
        p = subtree_proof(*s, d14)
        print(f"  [{s[0]}, {s[1]}): proof = {', '.join(name.get(h, h.hex()[:8]) for h in p)}")
    print("  (draft §4.4.2: [4, 8) -> D[0:4], D[8:14];  [8, 13) -> entries 12 and 13, D[8:12], D[0:8])")
    for start, end in ((0, 6), (5, 6)):
        same = subtree_proof(start, end, d14) == (mk.proof(end, d14) if start == 0 else mk.path(start, d14))
        print(f"  [{start}, {end}) equals Part 04's {'consistency proof' if start == 0 else 'inclusion path'}: {same}")

    print("\n== verifying [8, 13) in the tree of size 14, step by step ==")
    tr = []
    ok = verify_subtree_consistency(14, 8, 13, subtree_proof(8, 13, d14), mk.mth(d14[8:13]), mk.mth(d14), tr)
    for step, fn, sn, tn, c in tr:
        what = "first proof hash seeds fr and sr" if step == "start" else \
            f"{name.get(c, c.hex()[:8]):8s} is a {'LEFT ' if step == 'left' else 'RIGHT'} sibling"
        print(f"  {what:40s} then fn={fn:>2} ({fn:04b}) sn={sn:>2} ({sn:04b}) tn={tn:>2} ({tn:04b})")
    print(f"  fr == hash of [8, 13), sr == root, tn == 0: {ok}")

    print("\n== the draft's test vectors, and an exhaustive check ==")
    for nm, want in APPENDIX_C.items():
        got = appendix_c1(nm)
        print(f"  draft Appendix {nm}: {got[:16]}...  {'matches' if got == want else 'MISMATCH'}")
        assert got == want
    d = [bytes([i]) for i in range(64)]
    good = cases = bad_caught = total = longest = 0
    for n in range(1, 65):
        root = mk.mth(d[:n])
        for end in range(1, n + 1):
            for start in range(end):
                if not m7.valid_subtree(start, end):
                    continue
                p = subtree_proof(start, end, d[:n])
                node = mk.mth(d[start:end])
                longest = max(longest, len(p))
                cases += 1
                good += verify_subtree_consistency(n, start, end, p, node, root)
                for i in range(len(p)):                       # flip one byte of each proof hash
                    q = list(p); q[i] = bytes([q[i][0] ^ 1]) + q[i][1:]
                    bad_caught += not verify_subtree_consistency(n, start, end, q, node, root)
                    total += 1
                bad_caught += not verify_subtree_consistency(n, start, end, p, mk.mth(d[start:end - 1] or [b"x"]), root)
                total += 1
    print(f"  every valid subtree of every tree up to 64 entries: {good} of {cases} proofs verify, longest {longest} hashes")
    print(f"  {bad_caught} of {total} tampered proofs or wrong subtree hashes rejected")

    print("\n== a week of hourly landmarks (§6.4.2), 7-day certificates ==")
    rnd = random.Random(7)
    ca = LandmarkCA()
    counts = []
    for hour in range(1, 24 * 9 + 1):
        ca.grow(rnd.randint(20, 60))
        ca.allocate_landmark(hour * HOUR)
        counts.append(len(ca.active(hour * HOUR)))
    act = ca.active(24 * 9 * HOUR)
    subs = sum(len(ca.subtrees(l)) for l in act)
    bound = math.ceil(LIFETIME / HOUR) + 1
    print(f"  after 9 days: {len(ca.entries):,} entries, {len(ca.landmarks) - 1} landmarks allocated, {len(act)} active")
    print(f"  draft bound: ceil(168 h / 1 h) + 1 = {bound} active landmarks, {2 * bound} subtrees, {64 * bound:,} bytes")
    print(f"  this log: {len(act)} active landmarks, {subs} subtrees, {32 * subs:,} bytes of relying-party state")

    print("\n== the update service validates a bundle (§7.4) ==")
    for c in ca.cosigners:
        c.mirror = list(ca.entries)
    svc = UpdateService({c.id_bytes: (c.arcs, c.sk.public_key()) for c in ca.cosigners}, ca.cosigners[0].id_bytes)
    bundle = make_bundle(ca, 24 * 9 * HOUR)
    trusted, notes = svc.validate(bundle)
    for line in notes:
        print("  " + line)
    hashes = sum(len(p) for p in bundle.sub_proofs.values())
    print(f"  the service checked {len(bundle.sub_proofs)} subtree consistency proofs, {hashes:,} hashes"
          f" ({32 * hashes:,} bytes), longest {max(len(p) for p in bundle.sub_proofs.values())};"
          f" plus {len(bundle.cosigs)} checkpoint cosignatures. A client that trusts the service needs only the result.")

    print("\n== the draft's example: landmarks at 200, 300, 400, 500; cosigners have only checked 350 ==")
    small = LandmarkCA()
    for i, size in enumerate((200, 300, 400, 500), 1):
        small.grow(size - len(small.entries))
        small.allocate_landmark(i * HOUR)
    small.cosigners[0].mirror = list(small.entries)               # the CA's own cosigner sees everything
    for c in small.cosigners[1:]:
        c.mirror = list(small.entries[:350])                       # the witnesses have only checked 350
    svc2 = UpdateService({c.id_bytes: (c.arcs, c.sk.public_key()) for c in small.cosigners}, small.cosigners[0].id_bytes)
    for line in svc2.validate(make_bundle(small, 5 * HOUR, reference_size=500))[1]:
        print("  reference 500: " + line)
    for line in svc2.validate(make_bundle(small, 5 * HOUR, reference_size=350))[1]:
        print("  reference 350: " + line)

    print("\n== attacks on the update service ==")
    forged = make_bundle(small, 5 * HOUR, reference_size=350)
    s, h = forged.subtrees[2][0]
    forged.subtrees[2][0] = (s, bytes(32))                         # the CA ships a fake hash for landmark 2
    print("  forged landmark 2 hash  -> " + svc2.validate(forged)[1][1])
    fork = LandmarkCA()
    fork.grow(499)
    for c in fork.cosigners:
        c.mirror = list(fork.entries)
    fork.entries[123] = m7.mtc_log_entry(b"rewritten history")      # the CA rewrites an old entry
    try:
        cosign_checkpoint(fork.cosigners[1], 500, mk.mth(fork.entries), 9 * HOUR)
    except ValueError as e:
        print(f"  forked log             -> witness refuses: {e}")
    svc3 = UpdateService(svc.cosigners, svc.ca_id, max_landmarks=100)
    print("  cap of 100 landmarks    -> " + svc3.validate(make_bundle(ca, 24 * 9 * HOUR))[1][-2])

    print("\n== how stale can a client be? (renew at 75% of 7 days, keep both certificates, 1 h distribution delay) ==")
    for s in (0, 12, 24, 40, 48, 72, 96, 120, 144, 168):
        sh = lr_share(s)
        print(f"  client last updated {s:>3} h ago: landmark-relative in {sh:6.1%} of handshakes,"
              f" expected authentication {expected_auth(sh):>7,.0f} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
