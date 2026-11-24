//! Root of Trust, part 11: the core of the series in Rust.
//!
//! Each module is a port of one Python experiment, checked against the JSON test
//! vectors that `11_vectors.py` freezes from it (see `tests/vectors.rs`):
//!
//! | module    | ported from                         | what it does                                        |
//! |-----------|-------------------------------------|-----------------------------------------------------|
//! | `merkle`  | `04_merkle.py`                      | RFC 9162 tree hash, inclusion and consistency proofs |
//! | `subtree` | `07_mtc.py`, `08_landmarks.py`      | MTC subtrees: validity, covering, consistency proofs |
//! | `tiles`   | `09_tiles.py`                       | C2SP tlog-tiles paths and layout                    |
//! | `der`     | `der.py`                            | just enough DER to take a certificate apart         |
//! | `mtc`     | `07_mtc.py`                         | MTC encodings and landmark-relative verification    |
//! | `note`    | `05_witness.py`                     | checkpoint bodies and signed-note key IDs           |
//!
//! Nothing here signs or verifies signatures: those come from a vetted library in
//! the real implementation. Everything here is hashing and parsing, which is where
//! the series found its bugs.

pub mod der;
pub mod merkle;
pub mod mtc;
pub mod note;
pub mod subtree;
pub mod tiles;

/// A SHA-256 hash. Every hash in this crate is one.
pub type Hash = [u8; 32];

/// SHA-256 of some bytes.
pub fn sha256(data: &[u8]) -> Hash {
    use sha2::{Digest, Sha256};
    let mut out = [0u8; 32];
    out.copy_from_slice(&Sha256::digest(data));
    out
}
