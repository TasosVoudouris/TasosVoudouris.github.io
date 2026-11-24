//! MTC subtrees, ported from Parts 07 and 08 (draft-ietf-plants-merkle-tree-certs-07 §4).
//!
//! A subtree is a range [start, end) of the log. It is valid, a node of the tree, when
//! start is a multiple of BIT_CEIL(end - start).

use crate::merkle::{mth, node_hash, split};
use crate::Hash;

/// Smallest power of two >= n (BIT_CEIL(0) = 1). Returns None if it does not fit in a u64.
pub fn bit_ceil(n: u64) -> Option<u64> {
    if n <= 1 {
        Some(1)
    } else {
        n.checked_next_power_of_two()
    }
}

/// §4.1. Ranges up to 2^64 - 1 are allowed; sizes above 2^63 can never be valid
/// (their BIT_CEIL would be 2^64), except that [0, 2^64 - 1) is checked by the same rule.
pub fn valid_subtree(start: u64, end: u64) -> bool {
    if start > end {
        return false;
    }
    match bit_ceil(end - start) {
        Some(c) => start.is_multiple_of(c),
        None => start == 0, // BIT_CEIL = 2^64: only a start of 0 is a multiple
    }
}

/// §4.5.1: the two valid subtrees that cover [start, end). The left one may start early.
pub fn covering_subtrees(start: u64, end: u64) -> ((u64, u64), (u64, u64)) {
    assert!(start <= end);
    if end - start <= 1 {
        return ((start, end), (end, end));
    }
    let last = end - 1;
    let split_bit = 63 - (start ^ last).leading_zeros(); // most significant differing bit
    let mid = last & !((1u64 << split_bit) - 1);
    // most significant zero bit of start below split_bit
    let low = start & ((1u64 << split_bit) - 1);
    let zeros = !low & ((1u64 << split_bit) - 1);
    let left_split = if zeros == 0 { 0 } else { 64 - zeros.leading_zeros() };
    let left_start = if left_split == 0 { start } else { start & !((1u64 << left_split) - 1) };
    ((left_start, mid), (mid, end))
}

/// §4.4.1 SUBTREE_PROOF(start, end, D_n).
pub fn subtree_proof(start: usize, end: usize, d: &[Vec<u8>]) -> Vec<Hash> {
    subproof(start, end, d, true)
}

fn subproof(start: usize, end: usize, d: &[Vec<u8>], b: bool) -> Vec<Hash> {
    let n = d.len();
    if start == end {
        return vec![];
    }
    if start == 0 && end == n {
        return if b { vec![] } else { vec![mth(d)] };
    }
    let k = split(n as u64) as usize;
    let mut p;
    if end <= k {
        p = subproof(start, end, &d[..k], b);
        p.push(mth(&d[k..]));
    } else if k <= start {
        p = subproof(start - k, end - k, &d[k..], b);
        p.push(mth(&d[..k]));
    } else {
        p = subproof(0, end - k, &d[k..], false);
        p.push(mth(&d[..k]));
    }
    p
}

/// §4.4.3: is `node` the hash of [start, end) in the tree of size n with hash `root`?
pub fn verify_subtree_consistency(n: u64, start: u64, end: u64, proof: &[Hash], node: &Hash, root: &Hash) -> bool {
    if !(valid_subtree(start, end) && end <= n) {
        return false;
    }
    if start == end {
        return proof.is_empty() && node == &crate::sha256(b"");
    }
    let (mut fn_, mut sn, mut tn) = (start, end - 1, n - 1);
    if sn == tn {
        while fn_ != sn {
            fn_ >>= 1;
            sn >>= 1;
            tn >>= 1;
        }
    } else {
        while fn_ != sn && sn & 1 == 1 {
            fn_ >>= 1;
            sn >>= 1;
            tn >>= 1;
        }
    }
    let mut rest = proof;
    let (mut fr, mut sr);
    if fn_ == sn {
        fr = *node;
        sr = *node;
    } else {
        let Some((first, tail)) = proof.split_first() else { return false };
        fr = *first;
        sr = *first;
        rest = tail;
    }
    for c in rest {
        if tn == 0 {
            return false;
        }
        if sn & 1 == 1 || sn == tn {
            if fn_ < sn {
                fr = node_hash(c, &fr);
            }
            sr = node_hash(c, &sr);
            while sn & 1 == 0 {
                fn_ >>= 1;
                sn >>= 1;
                tn >>= 1;
            }
        } else {
            sr = node_hash(&sr, c);
        }
        fn_ >>= 1;
        sn >>= 1;
        tn >>= 1;
    }
    tn == 0 && &fr == node && &sr == root
}
