//! Checkpoint bodies and signed-note key IDs, ported from Part 05 (`05_witness.py`),
//! C2SP tlog-checkpoint and signed-note.

use crate::{sha256, Hash};

const B64: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/// Standard base64 with padding: the only encoding notes use.
pub fn base64(data: &[u8]) -> String {
    let mut out = String::new();
    for chunk in data.chunks(3) {
        let b = [chunk[0], *chunk.get(1).unwrap_or(&0), *chunk.get(2).unwrap_or(&0)];
        let n = (b[0] as u32) << 16 | (b[1] as u32) << 8 | b[2] as u32;
        for i in 0..4 {
            if i <= chunk.len() {
                out.push(B64[(n >> (18 - 6 * i) & 63) as usize] as char);
            } else {
                out.push('=');
            }
        }
    }
    out
}

/// origin, tree size in decimal, root hash in base64; every line ends with a newline.
pub fn checkpoint_body(origin: &str, size: u64, root: &Hash) -> String {
    format!("{origin}\n{size}\n{}\n", base64(root))
}

/// The 4-byte key ID that tags a signature line: SHA-256(name || 0x0A || type || public key)[:4].
pub fn key_id(name: &str, sig_type: u8, public_key: &[u8]) -> [u8; 4] {
    let mut b = name.as_bytes().to_vec();
    b.push(0x0A);
    b.push(sig_type);
    b.extend_from_slice(public_key);
    let h = sha256(&b);
    [h[0], h[1], h[2], h[3]]
}
