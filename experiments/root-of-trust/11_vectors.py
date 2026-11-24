"""Root of Trust, part 11: from toy to QCERT.

The Python experiments of Parts 04 to 10 are the reference. This script freezes
what they compute into one JSON file of test vectors, so that an implementation
in another language (the Rust crate next to this file, and later the QCERT code)
can be checked against exactly the same bytes:

  * Merkle trees (Part 04): tree hashes, inclusion and consistency proofs
  * MTC subtrees (Parts 07, 08): validity, covering, subtree consistency proofs,
    and the draft's own Appendix C hashes (recomputed, so they double as a check)
  * tiles (Part 09): paths, layouts, node to tile mapping
  * MTC encodings (Part 07): relative OIDs, serials, CosignedSubtree messages,
    MTCProof bytes, a log entry, and a complete landmark-relative certificate
  * signed notes (Part 05): checkpoint bodies and key IDs

Everything in the file is deterministic: no randomized signature is included.

Run:  python 11_vectors.py              (writes vectors/root-of-trust-vectors.json)
      python 11_vectors.py --check      (regenerates in memory and compares with the file)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).parent
OUT = HERE / "vectors" / "root-of-trust-vectors.json"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m9 = _load("tiles09_v", "09_tiles.py")            # also loads 04, 05, 07, 08
mk, m5, m7, m8 = m9.mk, m9.m5, m9.m7, m9.m8

WHEN = datetime(2026, 11, 22, tzinfo=timezone.utc)
H = lambda b: b.hex()


def merkle() -> dict:
    d = [bytes([i]) for i in range(20)]
    return {
        "leaves": "leaf i is the single byte i, for i = 0 .. 19",
        "tree_hash": [{"n": n, "hash": H(mk.mth(d[:n]))} for n in range(21)],
        "inclusion": [{"n": n, "index": i, "proof": [H(p) for p in mk.path(i, d[:n])]}
                      for n in range(1, 21) for i in range(n)],
        "consistency": [{"m": m, "n": n, "proof": [H(p) for p in mk.proof(m, d[:n])]}
                        for n in range(1, 21) for m in range(1, n + 1)],
    }


def subtrees() -> dict:
    d14 = [bytes([i]) for i in range(14)]
    d = [bytes([i]) for i in range(20)]
    big = [(0x0, 0x800000000000), (0x500000000000, 0xd00000000000), (0x7fffffffffff, 0x800000000001),
           (0xfffffffffffe, 0xffffffffffff), (0xffffffffffff, 0xffffffffffff),
           (0x2800000000000000, 0x6800000000000000), (0x5000000000000000, 0xd000000000000000),
           (0xfffffffffffffffe, 0xffffffffffffffff), (1000, 1037), (0, 1037)]
    p = 2
    return {
        "valid": [{"start": s, "end": e, "valid": m7.valid_subtree(s, e)} for s, e in
                  [(0, p**47 + 1), (p**46, p**47 + 1), (0, p**63 + 1), (p**62, p**63 + 1), (0, p**64 - 1),
                   (p**62, p**64 - 1), (992, 1024), (1024, 1037), (1000, 1037), (24, 40), (32, 45)]],
        "covering": [{"start": s, "end": e, "left": list(m7.covering_subtrees(s, e)[0]),
                      "right": list(m7.covering_subtrees(s, e)[1])} for s, e in big],
        "consistency_examples": [{"n": 14, "start": s, "end": e, "proof": [H(x) for x in m8.subtree_proof(s, e, d14)]}
                                 for s, e in ((4, 8), (8, 13), (12, 14), (0, 6), (5, 6))],
        "consistency": [{"n": n, "start": s, "end": e, "proof": [H(x) for x in m8.subtree_proof(s, e, d[:n])]}
                        for n in range(1, 21) for e in range(1, n + 1) for s in range(e) if m7.valid_subtree(s, e)],
        "appendix_c": {
            "leaves": "leaf i is the single byte i; every 0 <= start <= end <= 130 (and n <= 130 for C.1.3)",
            "C.1.1": m7.APPENDIX_C["C.1.1 subtree hashes"],
            "C.1.2": m8.APPENDIX_C["C.1.2 subtree inclusion proofs"],
            "C.1.3": m8.APPENDIX_C["C.1.3 subtree consistency proofs"],
            "C.1.4": m7.APPENDIX_C["C.1.4 covering subtrees"],
            "line_formats": {
                "C.1.1": "[START, END) HASH\\n for every valid subtree",
                "C.1.2": "INDEX [START, END) P1 P2 ...\\n for every index of every valid subtree",
                "C.1.3": "[START, END) N P1 P2 ...\\n for every valid subtree of every tree size N",
                "C.1.4": "[LS, LE) [RS, RE)\\n for every range",
            },
        },
    }


def tiles() -> dict:
    return {
        "paths": [{"level": l, "index": i, "width": w, "path": m9.tile_path(l, i, w)}
                  for l, i, w in ((0, 1234067, 8), (0, 1234067, 256), (1, 0, 256), (2, 999, 256),
                                  (0, 1000, 256), (3, 10**9, 17))],
        "entries_paths": [{"index": 1234067, "width": 8, "path": m9.entries_path(1234067, 8)}],
        "bad_paths": ["tile/00/000", "tile/0/01", "tile/0/x01/000", "tile/0/000.p/0", "tile/0/000.p/256",
                      "tile/0/000.p/08", "tile/64/000", "tile/0/x000/001"],
        "layouts": [{"size": s, "tiles": [list(t) for t in m9.layout(s)][-6:], "count": len(m9.layout(s))}
                    for s in (1, 255, 256, 257, 65536, 70000)],
        "node_to_tile": [{"level": 8, "index": 123456789, "tile": list(m9.node_to_tile(8, 123456789))},
                         {"level": 3, "index": 100, "tile": list(m9.node_to_tile(3, 100))}],
    }


def mtc() -> dict:
    import test_07_mtc as t7                               # the same world Part 07's tests build
    ca, reqs, idx, certs, rp = t7.world()
    lm = ca.add_landmark()
    f = ca.fields(reqs[5], t7.WHEN)
    lr = ca.landmark_relative(idx[5], f)
    entry = ca.entries[idx[5]]
    q = m7.proof_of(lr)
    s, e = q["start"], q["end"]
    sigs = [(m7.relative_oid(a), bytes([i]) * 3) for i, a in enumerate([m7.WITNESS_IDS[1], m7.CA_ID, m7.WITNESS_IDS[0]])]
    proof_bytes = m7.mtc_proof(992, 1024, [bytes([7]) * 32, bytes([9]) * 32], sigs)
    return {
        "relative_oid": [{"arcs": list(a), "der": H(m7.der.tlv(0x0D, m7.relative_oid(a)))}
                         for a in (m7.CA_ID, m7.WITNESS_IDS[0], (1,), (128,), (16383, 16384))],
        "origins": {"log": m7.LOG_ORIGIN, "ca": m7.origin(m7.CA_ID)},
        "serial": {"log_number": 1, "index": 1005, "serial": (1 << 48) | 1005},
        "cosigned_subtree": {
            "cosigner": list(m7.WITNESS_IDS[0]), "start": 992, "end": 1024, "hash": "11" * 32, "timestamp": 0,
            "message": H(m7.cosigned_subtree(m7.WITNESS_IDS[0], 992, 1024, bytes([0x11]) * 32)),
        },
        "checkpoint_cosignature": {
            "cosigner": list(m7.CA_ID), "start": 0, "end": 1037, "hash": "22" * 32, "timestamp": 1764000000,
            "message": H(m7.cosigned_subtree(m7.CA_ID, 0, 1037, bytes([0x22]) * 32, 1764000000)),
        },
        "mtc_proof": {
            "start": 992, "end": 1024, "proof": ["07" * 32, "09" * 32],
            "signatures_unsorted": [{"cosigner_id": H(c), "signature": H(x)} for c, x in sigs],
            "bytes": H(proof_bytes),
            "note": "signatures sorted by cosigner ID, shorter first, then bytewise",
        },
        "landmark_relative_certificate": {
            "der": H(lr),
            "log_entry": H(entry),
            "leaf_hash": H(mk.leaf_hash(entry)),
            "index": idx[5],
            "start": s, "end": e,
            "proof": [H(x) for x in q["proof"]],
            "trusted_subtree_hash": H(mk.mth(ca.entries[s:e])),
            "landmark_subtrees": [list(t) for t in lm],
        },
    }


def notes() -> dict:
    v = m5.Verifier.parse(m5.SPEC_VKEY)
    return {
        "checkpoint_body": {"origin": "example.org/rot/09", "size": 70000, "root": "33" * 32,
                            "text": m5.checkpoint_body("example.org/rot/09", 70000, bytes([0x33]) * 32)},
        "key_id": {"vkey": m5.SPEC_VKEY, "name": v.name, "type": v.sig_type,
                   "public_key": H(m5.raw(v.pub)), "key_id": H(v.kid),
                   "rule": "SHA-256(name || 0x0A || type || public key)[:4]"},
    }


def build() -> dict:
    return {
        "about": "Root of Trust test vectors, generated by experiments/root-of-trust/11_vectors.py. "
                 "Hashes are SHA-256 in hex. Merkle trees follow RFC 9162; subtrees and MTC encodings follow "
                 "draft-ietf-plants-merkle-tree-certs-07; tiles follow C2SP tlog-tiles; notes follow C2SP signed-note.",
        "version": 1,
        "merkle": merkle(),
        "subtrees": subtrees(),
        "tiles": tiles(),
        "mtc": mtc(),
        "notes": notes(),
    }


def dump(v: dict) -> str:
    return json.dumps(v, indent=1, sort_keys=False) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    v = build()
    text = dump(v)
    if "--check" in sys.argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print(f"{OUT.name}: {'identical to a fresh run' if same else 'DIFFERS from a fresh run'}")
        return 0 if same else 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    counts = {
        "tree hashes": len(v["merkle"]["tree_hash"]),
        "inclusion proofs": len(v["merkle"]["inclusion"]),
        "consistency proofs": len(v["merkle"]["consistency"]),
        "subtree consistency proofs": len(v["subtrees"]["consistency"]),
        "covering cases": len(v["subtrees"]["covering"]),
        "tile paths": len(v["tiles"]["paths"]) + len(v["tiles"]["bad_paths"]),
    }
    print(f"wrote {OUT.relative_to(HERE)} ({OUT.stat().st_size:,} bytes)")
    for k, n in counts.items():
        print(f"  {n:>4} {k}")
    lr = v["mtc"]["landmark_relative_certificate"]
    print(f"  a landmark-relative certificate of {len(lr['der']) // 2:,} bytes, entry {lr['index']},"
          f" subtree [{lr['start']}, {lr['end']}), {len(lr['proof'])} proof hashes")
    print(f"  draft Appendix C hashes: {', '.join(k for k in v['subtrees']['appendix_c'] if k.startswith('C.'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
