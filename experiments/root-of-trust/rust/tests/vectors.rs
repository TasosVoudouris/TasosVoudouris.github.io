//! Every Rust function against the bytes the Python reference froze in
//! ../vectors/root-of-trust-vectors.json (written by 11_vectors.py).

use rot_mtc::merkle::*;
use rot_mtc::mtc::*;
use rot_mtc::note::*;
use rot_mtc::subtree::*;
use rot_mtc::tiles::*;
use rot_mtc::{sha256, Hash};
use serde_json::Value;
use std::sync::OnceLock;

fn v() -> &'static Value {
    static V: OnceLock<Value> = OnceLock::new();
    V.get_or_init(|| {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../vectors/root-of-trust-vectors.json");
        serde_json::from_str(&std::fs::read_to_string(path).expect("run python 11_vectors.py first")).unwrap()
    })
}

fn h(x: &Value) -> Hash {
    hex::decode(x.as_str().unwrap()).unwrap().try_into().unwrap()
}
fn hs(x: &Value) -> Vec<Hash> {
    x.as_array().unwrap().iter().map(h).collect()
}
fn u(x: &Value) -> u64 {
    x.as_u64().unwrap()
}
fn leaves(n: usize) -> Vec<Vec<u8>> {
    (0..n).map(|i| vec![i as u8]).collect()
}

#[test]
fn merkle_tree_hashes_and_proofs() {
    let m = &v()["merkle"];
    let d = leaves(20);
    let roots: Vec<Hash> = m["tree_hash"].as_array().unwrap().iter().map(|t| h(&t["hash"])).collect();
    for (n, root) in roots.iter().enumerate() {
        assert_eq!(&mth(&d[..n]), root, "MTH of {n} leaves");
    }
    for t in m["inclusion"].as_array().unwrap() {
        let (n, i) = (u(&t["n"]) as usize, u(&t["index"]) as usize);
        let p = hs(&t["proof"]);
        assert_eq!(inclusion_proof(i, &d[..n]), p);
        assert!(verify_inclusion(&leaf_hash(&d[i]), i as u64, n as u64, &p, &roots[n]));
        assert!(!verify_inclusion(&leaf_hash(&d[i]), n as u64, n as u64, &p, &roots[n]));
        // Not asserted: that the same proof fails for size n + 1. Sometimes it passes, which is
        // Part 04's lesson: an inclusion proof does not bind the tree size; the signed checkpoint does.
    }
    for t in m["consistency"].as_array().unwrap() {
        let (mm, n) = (u(&t["m"]) as usize, u(&t["n"]) as usize);
        let p = hs(&t["proof"]);
        assert_eq!(consistency_proof(mm, &d[..n]), p);
        assert!(verify_consistency(mm as u64, n as u64, &roots[mm], &roots[n], &p), "{mm} -> {n}");
        if mm < n {
            assert!(!verify_consistency(mm as u64, n as u64, &roots[mm], &roots[n - 1], &p));
        }
    }
}

#[test]
fn subtree_validity_and_covering() {
    let s = &v()["subtrees"];
    for t in s["valid"].as_array().unwrap() {
        assert_eq!(valid_subtree(u(&t["start"]), u(&t["end"])), t["valid"].as_bool().unwrap(), "{t}");
    }
    for t in s["covering"].as_array().unwrap() {
        let pair = |x: &Value| (u(&x[0]), u(&x[1]));
        let got = covering_subtrees(u(&t["start"]), u(&t["end"]));
        assert_eq!(got, (pair(&t["left"]), pair(&t["right"])), "{t}");
    }
}

#[test]
fn subtree_consistency_proofs() {
    let s = &v()["subtrees"];
    let d = leaves(20);
    for t in s["consistency"].as_array().unwrap() {
        let (n, a, b) = (u(&t["n"]) as usize, u(&t["start"]) as usize, u(&t["end"]) as usize);
        let p = hs(&t["proof"]);
        assert_eq!(subtree_proof(a, b, &d[..n]), p, "[{a}, {b}) in {n}");
        let (node, root) = (mth(&d[a..b]), mth(&d[..n]));
        assert!(verify_subtree_consistency(n as u64, a as u64, b as u64, &p, &node, &root));
        assert!(!verify_subtree_consistency(n as u64, a as u64, b as u64, &p, &root, &node) || node == root);
        for i in 0..p.len() {
            let mut q = p.clone();
            q[i][0] ^= 1;
            assert!(!verify_subtree_consistency(n as u64, a as u64, b as u64, &q, &node, &root));
        }
    }
    let d14 = leaves(14);
    for t in s["consistency_examples"].as_array().unwrap() {
        let (a, b) = (u(&t["start"]) as usize, u(&t["end"]) as usize);
        assert_eq!(subtree_proof(a, b, &d14), hs(&t["proof"]));
    }
}

fn running(lines: impl Iterator<Item = String>) -> String {
    let mut all = String::new();
    for l in lines {
        all.push_str(&l);
        all.push('\n');
    }
    hex::encode(sha256(all.as_bytes()))
}

fn joined(p: &[Hash]) -> String {
    p.iter().map(|x| format!(" {}", hex::encode(x))).collect()
}

#[test]
fn draft_appendix_c() {
    let c = &v()["subtrees"]["appendix_c"];
    let d = leaves(131);
    let ranges = || (0..=130u64).flat_map(|e| (0..=e).map(move |s| (s, e)));
    let c11 = running(ranges().filter(|&(s, e)| valid_subtree(s, e)).map(|(s, e)| {
        format!("[{s}, {e}) {}", hex::encode(mth(&d[s as usize..e as usize])))
    }));
    assert_eq!(c11, c["C.1.1"].as_str().unwrap());
    let c12 = running(ranges().filter(|&(s, e)| valid_subtree(s, e)).flat_map(|(s, e)| {
        let d = &d;
        (s..e).map(move |i| format!("{i} [{s}, {e}){}", joined(&inclusion_proof((i - s) as usize, &d[s as usize..e as usize]))))
    }));
    assert_eq!(c12, c["C.1.2"].as_str().unwrap());
    let c13 = running((0..=130usize).flat_map(|n| {
        let d = &d;
        (0..=n).flat_map(move |e| (0..=e).filter(move |&s| valid_subtree(s as u64, e as u64)).map(move |s| {
            format!("[{s}, {e}) {n}{}", joined(&subtree_proof(s, e, &d[..n])))
        }))
    }));
    assert_eq!(c13, c["C.1.3"].as_str().unwrap());
    let c14 = running(ranges().map(|(s, e)| {
        let ((a, b), (x, y)) = covering_subtrees(s, e);
        format!("[{a}, {b}) [{x}, {y})")
    }));
    assert_eq!(c14, c["C.1.4"].as_str().unwrap());
}

#[test]
fn tile_paths_and_layout() {
    let t = &v()["tiles"];
    for p in t["paths"].as_array().unwrap() {
        let (l, i, w) = (u(&p["level"]) as u8, u(&p["index"]), u(&p["width"]));
        let path = tile_path(l, i, w);
        assert_eq!(path, p["path"].as_str().unwrap());
        assert_eq!(parse_tile_path(&path), Ok((Kind::Level(l), i, w)));
    }
    for p in t["entries_paths"].as_array().unwrap() {
        assert_eq!(entries_path(u(&p["index"]), u(&p["width"])), p["path"].as_str().unwrap());
    }
    for bad in t["bad_paths"].as_array().unwrap() {
        assert!(parse_tile_path(bad.as_str().unwrap()).is_err(), "{bad}");
    }
    for l in t["layouts"].as_array().unwrap() {
        let got = layout(u(&l["size"]));
        assert_eq!(got.len() as u64, u(&l["count"]));
        let tail: Vec<(u8, u64, u64)> = l["tiles"]
            .as_array()
            .unwrap()
            .iter()
            .map(|x| (u(&x[0]) as u8, u(&x[1]), u(&x[2])))
            .collect();
        assert_eq!(&got[got.len() - tail.len()..], &tail[..]);
    }
    for n in t["node_to_tile"].as_array().unwrap() {
        let want = &n["tile"];
        let got = node_to_tile(u(&n["level"]) as u32, u(&n["index"]));
        assert_eq!(got, (u(&want[0]) as u32, u(&want[1]), u(&want[2]) as u32, u(&want[3])));
    }
}

#[test]
fn mtc_encodings() {
    let m = &v()["mtc"];
    for r in m["relative_oid"].as_array().unwrap() {
        let arcs: Vec<u64> = r["arcs"].as_array().unwrap().iter().map(u).collect();
        assert_eq!(hex::encode(rot_mtc::der::tlv(0x0D, &relative_oid(&arcs))), r["der"].as_str().unwrap());
    }
    let log_origin = m["origins"]["log"].as_str().unwrap();
    assert_eq!(origin(&[32473, 1, 0, 1]), log_origin);
    for key in ["cosigned_subtree", "checkpoint_cosignature"] {
        let c = &m[key];
        let arcs: Vec<u64> = c["cosigner"].as_array().unwrap().iter().map(u).collect();
        let msg = cosigned_subtree(&arcs, log_origin, u(&c["start"]), u(&c["end"]), &h(&c["hash"]), u(&c["timestamp"]));
        assert_eq!(hex::encode(msg), c["message"].as_str().unwrap(), "{key}");
    }
    let p = &m["mtc_proof"];
    let sigs: Vec<(Vec<u8>, Vec<u8>)> = p["signatures_unsorted"]
        .as_array()
        .unwrap()
        .iter()
        .map(|s| (hex::decode(s["cosigner_id"].as_str().unwrap()).unwrap(), hex::decode(s["signature"].as_str().unwrap()).unwrap()))
        .collect();
    let proof = MtcProof { start: u(&p["start"]), end: u(&p["end"]), proof: hs(&p["proof"]), signatures: sigs };
    let bytes = proof.encode();
    assert_eq!(hex::encode(&bytes), p["bytes"].as_str().unwrap());
    let back = MtcProof::parse(&bytes).unwrap();
    assert_eq!((back.start, back.end, back.proof.len(), back.signatures.len()), (992, 1024, 2, 3));
    let mut trailing = bytes.clone();
    trailing.push(0);
    assert!(MtcProof::parse(&trailing).is_err());
    let s = &m["serial"];
    assert_eq!(u(&s["serial"]) >> 48, u(&s["log_number"]));
    assert_eq!(u(&s["serial"]) & ((1 << 48) - 1), u(&s["index"]));
}

#[test]
fn landmark_relative_certificate_end_to_end() {
    let c = &v()["mtc"]["landmark_relative_certificate"];
    let cert = hex::decode(c["der"].as_str().unwrap()).unwrap();
    let tbs = rot_mtc::der::children(&cert).unwrap()[0].to_vec();
    let entry = log_entry_from_tbs(&tbs).unwrap();
    assert_eq!(hex::encode(&entry), c["log_entry"].as_str().unwrap(), "rebuilt log entry");
    assert_eq!(leaf_hash(&entry), h(&c["leaf_hash"]));
    let sub = (u(&c["start"]), u(&c["end"]));
    let trusted = [(sub, h(&c["trusted_subtree_hash"]))];
    let ok = verify_landmark_relative(&cert, &trusted).unwrap();
    assert_eq!(ok, Accepted { log_number: 1, index: u(&c["index"]), subtree: sub });
    // a wrong landmark hash, a missing landmark, one flipped byte of the subject: all rejected
    assert!(verify_landmark_relative(&cert, &[(sub, [0u8; 32])]).is_err());
    assert!(verify_landmark_relative(&cert, &[]).is_err());
    let pos = cert.windows(13).position(|w| w == b"site5.example").unwrap();
    let mut forged = cert.clone();
    forged[pos + 4] = b'6';
    assert!(verify_landmark_relative(&forged, &trusted).is_err());
}

#[test]
fn checkpoint_body_and_key_id() {
    let n = &v()["notes"];
    let cb = &n["checkpoint_body"];
    let body = checkpoint_body(cb["origin"].as_str().unwrap(), u(&cb["size"]), &h(&cb["root"]));
    assert_eq!(body, cb["text"].as_str().unwrap());
    let k = &n["key_id"];
    let pk = hex::decode(k["public_key"].as_str().unwrap()).unwrap();
    let id = key_id(k["name"].as_str().unwrap(), u(&k["type"]) as u8, &pk);
    assert_eq!(hex::encode(id), k["key_id"].as_str().unwrap());
}
