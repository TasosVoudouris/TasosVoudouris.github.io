"""Root of Trust, part 04: Merkle trees from zero.

The Merkle tree of Certificate Transparency, built from its definitions:

  * MTH(D[n])        the tree hash          (RFC 6962 §2.1, same in RFC 9162 §2.1.1)
  * PATH(m, D[n])    an inclusion proof     (RFC 6962 §2.1.1)
  * PROOF(m, D[n])   a consistency proof    (RFC 6962 §2.1.2)

and the two verifiers a client actually runs, written from RFC 9162 §2.1.3.2 and
§2.1.4.2. The generators follow the recursive definitions; the verifiers are the
iterative bit-twiddling algorithms. They share no code, so checking one against the
other for every tree size and every index is a real test.

Then: the published test vectors, a second-preimage attack on a tree WITHOUT the
0x00 / 0x01 prefixes, proof sizes, and Part 03's dishonest logs meeting proofs.

Run:  python 04_merkle.py         (needs: pip install cryptography, for the log part)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


# --------------------------------------------------------------------------- the tree

def leaf_hash(d: bytes) -> bytes:
    return sha256(b"\x00" + d)


def node_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b"\x01" + left + right)


def split(n: int) -> int:
    """The largest power of two strictly smaller than n (n > 1)."""
    return 1 << ((n - 1).bit_length() - 1)


def mth(d: list[bytes]) -> bytes:
    """Merkle Tree Hash. The empty tree hashes to SHA-256 of nothing."""
    n = len(d)
    if n == 0:
        return sha256(b"")
    if n == 1:
        return leaf_hash(d[0])
    k = split(n)
    return node_hash(mth(d[:k]), mth(d[k:]))


def path(m: int, d: list[bytes]) -> list[bytes]:
    """Inclusion proof for leaf m: the sibling hashes from the leaf up to the root."""
    n = len(d)
    if n <= 1:
        return []
    k = split(n)
    if m < k:
        return path(m, d[:k]) + [mth(d[k:])]
    return path(m - k, d[k:]) + [mth(d[:k])]


def proof(m: int, d: list[bytes]) -> list[bytes]:
    """Consistency proof that the first m leaves are a prefix of all n."""
    return [] if m == len(d) or m == 0 else _subproof(m, d, True)


def _subproof(m: int, d: list[bytes], b: bool) -> list[bytes]:
    n = len(d)
    if m == n:
        # The verifier already knows MTH(D[0:m]) when b is true (it is the old root).
        return [] if b else [mth(d)]
    k = split(n)
    if m <= k:
        return _subproof(m, d[:k], b) + [mth(d[k:])]
    return _subproof(m - k, d[k:], False) + [mth(d[:k])]


# --------------------------------------------------------------------------- the verifiers

def verify_inclusion(leaf: bytes, index: int, size: int, proof_: list[bytes], root: bytes) -> bool:
    """RFC 9162 §2.1.3.2. `leaf` is the leaf hash, not the data."""
    if index >= size:
        return False
    fn, sn, r = index, size - 1, leaf
    for p in proof_:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            r = node_hash(p, r)
            if not fn & 1:
                while fn and not fn & 1:
                    fn, sn = fn >> 1, sn >> 1
        else:
            r = node_hash(r, p)
        fn, sn = fn >> 1, sn >> 1
    return sn == 0 and r == root


def verify_consistency(first: int, second: int, first_root: bytes, second_root: bytes, proof_: list[bytes]) -> bool:
    """RFC 9162 §2.1.4.2."""
    if first > second:
        return False
    if first == second:
        return not proof_ and first_root == second_root
    if first == 0:
        return not proof_  # the empty tree is a prefix of everything
    if not proof_:
        return False
    if first & (first - 1) == 0:  # first is a power of two: the old root is a node of the new tree
        proof_ = [first_root] + list(proof_)
    fn, sn = first - 1, second - 1
    while fn & 1:
        fn, sn = fn >> 1, sn >> 1
    fr = sr = proof_[0]
    for c in proof_[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr, sr = node_hash(c, fr), node_hash(c, sr)
            if not fn & 1:
                while fn and not fn & 1:
                    fn, sn = fn >> 1, sn >> 1
        else:
            sr = node_hash(sr, c)
        fn, sn = fn >> 1, sn >> 1
    return sn == 0 and fr == first_root and sr == second_root


def proof_len(m: int, n: int, b: bool = True) -> int:
    """Length of PROOF(m, D[n]) without computing any hash: it depends only on m and n."""
    if m == n:
        return 0 if b else 1
    k = split(n)
    return proof_len(m, k, b) + 1 if m <= k else proof_len(m - k, n - k, False) + 1


def worst_consistency(n: int) -> int:
    return max((proof_len(m, n) for m in range(1, n)), default=0)


# --------------------------------------------------------------------------- known answers

# The leaves used by the Certificate Transparency test suites, and the tree hash after
# each prefix. Our MTH must reproduce every one of them.
TEST_LEAVES = [bytes.fromhex(h) for h in (
    "", "00", "10", "2021", "3031", "40414243", "5051525354555657", "606162636465666768696a6b6c6d6e6f")]
TEST_ROOTS = [bytes.fromhex(h) for h in (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d",
    "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125",
    "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77",
    "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7",
    "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4",
    "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef",
    "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c",
    "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328")]


def rfc6962_example() -> dict[str, list[str]]:
    """RFC 6962 §2.1.3 names the nodes of the 7-leaf tree a..l. Rebuild the names and
    express our proofs in them, to compare with the examples printed in the RFC."""
    d = [f"d{i}".encode() for i in range(7)]
    names = {}
    for i, x in zip(range(6), "abcdef"):
        names[leaf_hash(d[i])] = x
    names[leaf_hash(d[6])] = "j"  # d6 has no sibling: its leaf hash is node j
    g, h = node_hash(leaf_hash(d[0]), leaf_hash(d[1])), node_hash(leaf_hash(d[2]), leaf_hash(d[3]))
    i = node_hash(leaf_hash(d[4]), leaf_hash(d[5]))
    names.update({g: "g", h: "h", i: "i", node_hash(g, h): "k", node_hash(i, leaf_hash(d[6])): "l"})
    show = lambda hs: [names[x] for x in hs]
    return {
        "PATH(0)": show(path(0, d)), "PATH(3)": show(path(3, d)),
        "PATH(4)": show(path(4, d)), "PATH(6)": show(path(6, d)),
        "PROOF(3)": show(proof(3, d)), "PROOF(4)": show(proof(4, d)), "PROOF(6)": show(proof(6, d)),
    }


# --------------------------------------------------------------------------- why the prefixes

def naive_root(hashes: list[bytes]) -> bytes:
    """A Merkle tree with NO domain separation: leaves and nodes hashed the same way."""
    if len(hashes) == 1:
        return hashes[0]
    k = split(len(hashes))
    return sha256(naive_root(hashes[:k]) + naive_root(hashes[k:]))


def second_preimage_demo() -> dict:
    """Without prefixes, an inner node can pose as a leaf: a different list, the same root."""
    d = [b"cert for alice", b"cert for bob", b"cert for carol", b"cert for dave"]
    honest = naive_root([sha256(x) for x in d])
    a, b = sha256(d[0]) + sha256(d[1]), sha256(d[2]) + sha256(d[3])  # two 64-byte "entries"
    forged = naive_root([sha256(a), sha256(b)])
    fixed_honest = mth(d)
    fixed_forged = mth([a, b])
    return {"naive_equal": honest == forged, "rfc6962_equal": fixed_honest == fixed_forged,
            "fake_entry": a.hex()}


# --------------------------------------------------------------------------- a log that can be checked

@dataclass
class TreeHead:
    size: int
    root: bytes
    timestamp: int
    signature: bytes = b""

    def signed_bytes(self) -> bytes:
        return b"sth" + self.size.to_bytes(8, "big") + self.timestamp.to_bytes(8, "big") + self.root


@dataclass
class MerkleLog:
    """Part 03's log, now with a Merkle tree, signed tree heads and proofs.
    A dishonest log may skip entries, rewrite history, or keep a second tree for some audiences."""
    sk: object
    entries: list = field(default_factory=list)
    shadow: list | None = None  # a second, different tree: a split view

    def append(self, entry: bytes, *, also_in_shadow: bool = True, only_in_shadow: bool = False) -> None:
        if not only_in_shadow:
            self.entries.append(entry)
        if self.shadow is not None and (also_in_shadow or only_in_shadow):
            self.shadow.append(entry)

    def head(self, timestamp: int, view: str = "main") -> TreeHead:
        es = self.entries if view == "main" else self.shadow
        h = TreeHead(len(es), mth(es), timestamp)
        h.signature = self.sk.sign(h.signed_bytes())
        return h

    def inclusion(self, entry: bytes, size: int, view: str = "main"):
        es = (self.entries if view == "main" else self.shadow)[:size]
        if entry not in es:
            return None
        i = es.index(entry)
        return i, path(i, es)

    def consistency(self, old: int, new: int, view: str = "main") -> list[bytes]:
        es = (self.entries if view == "main" else self.shadow)[:new]
        return proof(old, es)


def log_scenarios() -> list[tuple[str, str]]:
    """Part 03's broken promises, against a log that must answer with proofs."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    sk = Ed25519PrivateKey.from_private_bytes(sha256(b"root-of-trust part 04: log"))
    pub = sk.public_key()
    filler = [f"cert {i}".encode() for i in range(1000)]
    rogue = b"rogue cert for example.com, Mallory's key"
    out = []

    def head_ok(h: TreeHead) -> bool:
        pub.verify(h.signature, h.signed_bytes())
        return True

    # A. Honest log: the rogue certificate is in the tree and the proof shows it.
    log = MerkleLog(sk)
    for x in filler[:500]:
        log.append(x)
    log.append(rogue)
    for x in filler[500:]:
        log.append(x)
    h = log.head(1)
    i, p = log.inclusion(rogue, h.size)
    ok = head_ok(h) and verify_inclusion(leaf_hash(rogue), i, h.size, p, h.root)
    out.append(("A. honest log, browser asks for a proof",
                f"proof of {len(p)} hashes verifies: entry {i} of {h.size}, the monitor will see it" if ok else "??"))

    # B. Part 03's scenario 8: the log signed an SCT but never added the entry.
    log = MerkleLog(sk)
    for x in filler:
        log.append(x)
    h = log.head(2)
    got = log.inclusion(rogue, h.size)
    out.append(("B. log skipped the entry (scenario 8)",
                "no proof exists; signed SCT + signed head past the deadline = evidence against the log"
                if got is None and head_ok(h) else "??"))

    # C. The log included it, a monitor saw head #1, then the log rewrote history to remove it.
    log = MerkleLog(sk)
    for x in filler[:600]:
        log.append(x)
    log.append(rogue)
    old = log.head(3)
    log.entries.remove(rogue)
    for x in filler[600:]:
        log.append(x)
    new = log.head(4)
    p = log.consistency(old.size, new.size)
    ok = verify_consistency(old.size, new.size, old.root, new.root, p)
    out.append(("C. log rewrote history after a monitor saw it",
                "consistency proof fails: two signed heads that cannot both be true" if not ok else "??"))

    # D. Split view: the monitor is served one tree, the victim's browser another.
    log = MerkleLog(sk, shadow=[])
    for x in filler:
        log.append(x)
    log.append(rogue, only_in_shadow=True)
    for_monitor, for_victim = log.head(5), log.head(5, view="shadow")
    i, p = log.inclusion(rogue, for_victim.size, view="shadow")
    victim_ok = verify_inclusion(leaf_hash(rogue), i, for_victim.size, p, for_victim.root)
    monitor_sees = rogue in log.entries
    out.append(("D. split view: two trees, two audiences",
                "victim's proof verifies, monitor's tree is clean: nobody alone can tell (Part 05)"
                if victim_ok and not monitor_sees and for_monitor.root != for_victim.root else "??"))
    return out


# --------------------------------------------------------------------------- report

def main() -> int:
    print("== test vectors (CT's reference leaves) ==")
    for n, want in enumerate(TEST_ROOTS):
        got = mth(TEST_LEAVES[:n])
        print(f"  MTH of first {n} leaves: {got.hex()[:16]}..  {'ok' if got == want else 'MISMATCH'}")
        assert got == want

    print("\n== RFC 6962 §2.1.3 examples, 7-leaf tree, nodes named as in the RFC ==")
    for k, v in rfc6962_example().items():
        print(f"  {k:9s} = [{', '.join(v)}]")

    print("\n== generators against verifiers, every size 1..64, every index, every prefix ==")
    checked = 0
    for n in range(1, 65):
        d = [f"entry {i}".encode() for i in range(n)]
        root = mth(d)
        for m in range(n):
            assert verify_inclusion(leaf_hash(d[m]), m, n, path(m, d), root)
            checked += 1
            if n > 1:  # a wrong index must fail
                assert not verify_inclusion(leaf_hash(d[m]), (m + 1) % n, n, path(m, d), root)
        for m in range(0, n + 1):
            assert verify_consistency(m, n, mth(d[:m]), root, proof(m, d))
            checked += 1
    print(f"  {checked:,} proofs generated and verified")

    flips = 0
    d = [f"entry {i}".encode() for i in range(37)]
    root = mth(d)
    for m in range(37):
        p = path(m, d)
        for j in range(len(p)):
            for bit in range(0, 256, 17):
                bad = list(p)
                bad[j] = (int.from_bytes(bad[j], "big") ^ (1 << bit)).to_bytes(32, "big")
                assert not verify_inclusion(leaf_hash(d[m]), m, 37, bad, root)
                flips += 1
    print(f"  {flips:,} single-bit corruptions of inclusion proofs, all rejected")

    print("\n== why the 0x00 / 0x01 prefixes ==")
    r = second_preimage_demo()
    print(f"  no prefixes: 4 certificates and 2 fake 64-byte entries give the same root? {r['naive_equal']}")
    print(f"  RFC 6962   : same attack, same root?                                     {r['rfc6962_equal']}")

    print("\n== proof sizes (32-byte SHA-256 hashes) ==")
    exact = all(worst_consistency(n) == (n - 1).bit_length() + 1 for n in range(4, 2049))
    print(f"  worst consistency proof = ceil(log2 n) + 1 hashes for every n in 4..2048: {exact}")
    print(f"  {'entries':>17s} {'inclusion':>10s} {'bytes':>7s} {'worst consistency':>18s} {'bytes':>7s}")
    for e in (8, 1_000, 1_000_000, 1_000_000_000, 2**40):
        inc = (e - 1).bit_length()
        print(f"  {e:>17,} {inc:>10} {inc * 32:>7,} {inc + 1:>18} {(inc + 1) * 32:>7,}")
    d = [f"e{i}".encode() for i in range(1000)]
    print(f"  measured, n=1000: inclusion {len(path(637, d))} hashes, consistency 600->1000 {len(proof(600, d))} hashes")

    print("\n== Part 03's dishonest logs, now with a Merkle tree ==")
    for label, verdict in log_scenarios():
        print(f"  {label:46s} {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
