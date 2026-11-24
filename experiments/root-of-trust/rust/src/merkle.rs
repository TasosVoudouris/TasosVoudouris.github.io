//! Merkle trees as in RFC 9162 §2.1, ported from Part 04 (`04_merkle.py`).
//!
//! Leaves are byte strings. A leaf hashes as SHA-256(0x00 || leaf) and an inner
//! node as SHA-256(0x01 || left || right), so a leaf can never be mistaken for a node.

use crate::{sha256, Hash};

pub fn leaf_hash(leaf: &[u8]) -> Hash {
    let mut b = Vec::with_capacity(leaf.len() + 1);
    b.push(0x00);
    b.extend_from_slice(leaf);
    sha256(&b)
}

pub fn node_hash(left: &Hash, right: &Hash) -> Hash {
    let mut b = [0u8; 65];
    b[0] = 0x01;
    b[1..33].copy_from_slice(left);
    b[33..].copy_from_slice(right);
    sha256(&b)
}

/// Largest power of two strictly smaller than n (n >= 2): where MTH splits a tree.
pub fn split(n: u64) -> u64 {
    debug_assert!(n >= 2);
    1u64 << (63 - (n - 1).leading_zeros())
}

/// MTH(D[n]): the Merkle Tree Hash. The empty tree hashes to SHA-256 of nothing.
pub fn mth(d: &[Vec<u8>]) -> Hash {
    match d.len() {
        0 => sha256(b""),
        1 => leaf_hash(&d[0]),
        n => {
            let k = split(n as u64) as usize;
            node_hash(&mth(&d[..k]), &mth(&d[k..]))
        }
    }
}

/// PATH(m, D[n]): the inclusion proof for leaf m, from the leaf up.
pub fn inclusion_proof(m: usize, d: &[Vec<u8>]) -> Vec<Hash> {
    let n = d.len();
    if n <= 1 {
        return vec![];
    }
    let k = split(n as u64) as usize;
    let mut p;
    if m < k {
        p = inclusion_proof(m, &d[..k]);
        p.push(mth(&d[k..]));
    } else {
        p = inclusion_proof(m - k, &d[k..]);
        p.push(mth(&d[..k]));
    }
    p
}

/// PROOF(m, D[n]): the consistency proof that the first m leaves are a prefix of all n.
pub fn consistency_proof(m: usize, d: &[Vec<u8>]) -> Vec<Hash> {
    if m == 0 || m == d.len() {
        return vec![];
    }
    subproof(m, d, true)
}

fn subproof(m: usize, d: &[Vec<u8>], b: bool) -> Vec<Hash> {
    let n = d.len();
    if m == n {
        return if b { vec![] } else { vec![mth(d)] };
    }
    let k = split(n as u64) as usize;
    let mut p;
    if m <= k {
        p = subproof(m, &d[..k], b);
        p.push(mth(&d[k..]));
    } else {
        p = subproof(m - k, &d[k..], false);
        p.push(mth(&d[..k]));
    }
    p
}

/// RFC 9162 §2.1.3.2, returning the root the proof leads to instead of comparing it.
/// MTC calls this "evaluating" an inclusion proof (draft -07 §4.3).
pub fn evaluate_inclusion(leaf: &Hash, index: u64, size: u64, proof: &[Hash]) -> Option<Hash> {
    if index >= size {
        return None;
    }
    let (mut fn_, mut sn) = (index, size - 1);
    let mut r = *leaf;
    for p in proof {
        if sn == 0 {
            return None; // proof too long
        }
        if fn_ & 1 == 1 || fn_ == sn {
            r = node_hash(p, &r);
            if fn_ & 1 == 0 {
                while fn_ & 1 == 0 && fn_ != 0 {
                    fn_ >>= 1;
                    sn >>= 1;
                }
            }
        } else {
            r = node_hash(&r, p);
        }
        fn_ >>= 1;
        sn >>= 1;
    }
    if sn != 0 {
        return None; // proof too short
    }
    Some(r)
}

pub fn verify_inclusion(leaf: &Hash, index: u64, size: u64, proof: &[Hash], root: &Hash) -> bool {
    evaluate_inclusion(leaf, index, size, proof).as_ref() == Some(root)
}

/// RFC 9162 §2.1.4.2: is the tree of size m with hash `old` a prefix of the tree of size n with hash `new`?
pub fn verify_consistency(m: u64, n: u64, old: &Hash, new: &Hash, proof: &[Hash]) -> bool {
    if m == 0 || m > n {
        return false;
    }
    if m == n {
        return proof.is_empty() && old == new;
    }
    let mut path: Vec<Hash> = Vec::with_capacity(proof.len() + 1);
    if m.is_power_of_two() {
        path.push(*old); // the old tree is itself a node: start from it
    }
    path.extend_from_slice(proof);
    if path.is_empty() {
        return false;
    }
    let (mut fn_, mut sn) = (m - 1, n - 1);
    while fn_ & 1 == 1 {
        fn_ >>= 1;
        sn >>= 1;
    }
    let (mut fr, mut sr) = (path[0], path[0]);
    for c in &path[1..] {
        if sn == 0 {
            return false;
        }
        if fn_ & 1 == 1 || fn_ == sn {
            fr = node_hash(c, &fr);
            sr = node_hash(c, &sr);
            while fn_ & 1 == 0 && fn_ != 0 {
                fn_ >>= 1;
                sn >>= 1;
            }
        } else {
            sr = node_hash(&sr, c);
        }
        fn_ >>= 1;
        sn >>= 1;
    }
    sn == 0 && &fr == old && &sr == new
}
