//! Merkle Tree Certificate encodings, ported from Part 07 (`07_mtc.py`),
//! draft-ietf-plants-merkle-tree-certs-07 §5 and §6, and the relying party's check
//! of a landmark-relative certificate (§7.2), which needs no signature at all.

use crate::der;
use crate::merkle::{evaluate_inclusion, leaf_hash};
use crate::subtree::valid_subtree;
use crate::{sha256, Hash};

/// DER of the OID 1.3.6.1.5.5.7.6.67, id-alg-mtcProof, as an AlgorithmIdentifier with absent parameters.
pub const ALG_MTC_PROOF: [u8; 12] = [0x30, 0x0A, 0x06, 0x08, 0x2B, 0x06, 0x01, 0x05, 0x05, 0x07, 0x06, 0x43];

/// Contents of a RELATIVE-OID: each arc in base 128, high bit set on every byte but an arc's last.
pub fn relative_oid(arcs: &[u64]) -> Vec<u8> {
    let mut out = vec![];
    for &arc in arcs {
        let mut groups = vec![(arc & 0x7F) as u8];
        let mut a = arc >> 7;
        while a != 0 {
            groups.push(0x80 | (a & 0x7F) as u8);
            a >>= 7;
        }
        groups.reverse();
        out.extend(groups);
    }
    out
}

/// "oid/1.3.6.1.4.1." + the dotted ID: how logs and cosigners are named in signed messages.
pub fn origin(arcs: &[u64]) -> String {
    let dotted: Vec<String> = arcs.iter().map(|a| a.to_string()).collect();
    format!("oid/1.3.6.1.4.1.{}", dotted.join("."))
}

fn vec8(b: &[u8]) -> Vec<u8> {
    let mut v = vec![b.len() as u8];
    v.extend_from_slice(b);
    v
}

/// §5.3.1: the message a cosigner signs. In certificates the timestamp is zero;
/// a nonzero timestamp with start 0 is a checkpoint.
pub fn cosigned_subtree(cosigner: &[u64], log_origin: &str, start: u64, end: u64, hash: &Hash, timestamp: u64) -> Vec<u8> {
    let mut m = b"subtree/v1\n\0".to_vec();
    m.extend(vec8(origin(cosigner).as_bytes()));
    m.extend(timestamp.to_be_bytes());
    m.extend(vec8(log_origin.as_bytes()));
    m.extend(start.to_be_bytes());
    m.extend(end.to_be_bytes());
    m.extend_from_slice(hash);
    m
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MtcProof {
    pub start: u64,
    pub end: u64,
    pub proof: Vec<Hash>,
    /// (cosigner ID as relative-OID contents, signature)
    pub signatures: Vec<(Vec<u8>, Vec<u8>)>,
}

impl MtcProof {
    /// §6.1 encoding; signatures sorted by ID, shorter first, then bytewise.
    pub fn encode(&self) -> Vec<u8> {
        let mut sigs = self.signatures.clone();
        sigs.sort_by(|a, b| (a.0.len(), &a.0).cmp(&(b.0.len(), &b.0)));
        let mut body = vec![];
        for (id, sig) in &sigs {
            body.extend(vec8(id));
            body.extend((sig.len() as u16).to_be_bytes());
            body.extend(sig);
        }
        let mut out = vec![0, 0]; // no extensions
        out.extend(&self.start.to_be_bytes()[2..]); // uint48
        out.extend(&self.end.to_be_bytes()[2..]);
        out.extend(((self.proof.len() * 32) as u16).to_be_bytes());
        for h in &self.proof {
            out.extend_from_slice(h);
        }
        out.extend(&(body.len() as u32).to_be_bytes()[1..]); // uint24
        out.extend(body);
        out
    }

    /// Strict parse: no trailing bytes, whole hashes, sorted and unique cosigner IDs.
    pub fn parse(b: &[u8]) -> Result<Self, String> {
        let mut r = Reader { b, pos: 0 };
        let ext = r.take_len(2)?;
        let _ = ext; // extensions are skipped: none are defined yet
        let start = r.uint(6)?;
        let end = r.uint(6)?;
        let proof_bytes = r.take_len(2)?;
        if proof_bytes.len() % 32 != 0 {
            return Err("inclusion proof is not whole hashes".into());
        }
        let proof = proof_bytes.chunks(32).map(|c| c.try_into().unwrap()).collect();
        let sig_bytes = r.take_len(3)?;
        if r.pos != b.len() {
            return Err("trailing data after the MTCProof".into());
        }
        let mut s = Reader { b: sig_bytes, pos: 0 };
        let mut signatures: Vec<(Vec<u8>, Vec<u8>)> = vec![];
        while s.pos < sig_bytes.len() {
            let id = s.take_len(1)?.to_vec();
            if id.is_empty() {
                return Err("empty cosigner ID".into());
            }
            let sig = s.take_len(2)?.to_vec();
            if let Some((prev, _)) = signatures.last() {
                if (prev.len(), prev) >= (id.len(), &id) {
                    return Err("cosignatures not sorted or not unique".into());
                }
            }
            signatures.push((id, sig));
        }
        Ok(MtcProof { start, end, proof, signatures })
    }
}

struct Reader<'a> {
    b: &'a [u8],
    pos: usize,
}

impl<'a> Reader<'a> {
    fn take(&mut self, n: usize) -> Result<&'a [u8], String> {
        let out = self.b.get(self.pos..self.pos + n).ok_or("truncated MTCProof")?;
        self.pos += n;
        Ok(out)
    }
    fn uint(&mut self, n: usize) -> Result<u64, String> {
        Ok(self.take(n)?.iter().fold(0u64, |a, &x| (a << 8) | x as u64))
    }
    fn take_len(&mut self, n: usize) -> Result<&'a [u8], String> {
        let len = self.uint(n)? as usize;
        self.take(len)
    }
}

/// §5.2: rebuild the MTCLogEntry from a TBSCertificate, as the relying party must:
/// no serial, no signature algorithm, and the public key replaced by its algorithm and hash.
pub fn log_entry_from_tbs(tbs: &[u8]) -> Result<Vec<u8>, String> {
    let f = der::children(tbs)?;
    if f.len() < 7 || f[0][0] != 0xA0 {
        return Err("unexpected TBSCertificate shape".into());
    }
    let (version, issuer, validity, subject, spki) = (f[0], f[3], f[4], f[5], f[6]);
    let alg = der::children(spki)?.first().copied().ok_or("empty SubjectPublicKeyInfo")?;
    let mut entry = vec![0, 0, 0, 1]; // no extensions; type tbs_cert_entry
    entry.extend_from_slice(version);
    entry.extend_from_slice(issuer);
    entry.extend_from_slice(validity);
    entry.extend_from_slice(subject);
    entry.extend_from_slice(alg);
    entry.extend(der::tlv(0x04, &sha256(spki)));
    for extra in &f[7..] {
        entry.extend_from_slice(extra); // issuerUniqueID, subjectUniqueID, extensions, if present
    }
    if entry.len() > 65535 {
        return Err("log entry too large".into());
    }
    Ok(entry)
}

/// What the relying party learns from a landmark-relative certificate it accepts.
#[derive(Debug, PartialEq, Eq)]
pub struct Accepted {
    pub log_number: u64,
    pub index: u64,
    pub subtree: (u64, u64),
}

/// §7.2 for a certificate whose subtree is a trusted landmark subtree. No signature is checked:
/// the evaluated inclusion proof must land exactly on a hash the relying party already trusts.
pub fn verify_landmark_relative(cert: &[u8], trusted: &[((u64, u64), Hash)]) -> Result<Accepted, String> {
    let top = der::children(cert)?;
    if top.len() != 3 {
        return Err("a certificate has three parts".into());
    }
    let (tbs, alg, sig_value) = (top[0], top[1], top[2]);
    if alg != ALG_MTC_PROOF {
        return Err("signatureAlgorithm is not id-alg-mtcProof".into());
    }
    let f = der::children(tbs)?;
    if f.len() < 7 || f[2] != ALG_MTC_PROOF {
        return Err("TBSCertificate signature field is not id-alg-mtcProof".into());
    }
    let serial = der::value(f[1])?;
    if serial.is_empty() || serial.len() > 9 || (serial.len() == 9 && serial[0] != 0) || serial[0] & 0x80 != 0 {
        return Err("serial out of range".into());
    }
    let serial = serial.iter().fold(0u64, |a, &b| (a << 8) | b as u64);
    let (log_number, index) = (serial >> 48, serial & ((1 << 48) - 1));
    if log_number == 0 {
        return Err("log number zero".into());
    }
    let bits = der::value(sig_value)?;
    if sig_value[0] != 0x03 || bits.first() != Some(&0) {
        return Err("signatureValue is not a whole-byte BIT STRING".into());
    }
    let p = MtcProof::parse(&bits[1..])?;
    if !(valid_subtree(p.start, p.end) && p.start <= index && index < p.end) {
        return Err("index not in a valid subtree".into());
    }
    let leaf = leaf_hash(&log_entry_from_tbs(tbs)?);
    let got = evaluate_inclusion(&leaf, index - p.start, p.end - p.start, &p.proof).ok_or("malformed inclusion proof")?;
    match trusted.iter().find(|(s, _)| *s == (p.start, p.end)) {
        Some((_, h)) if *h == got => Ok(Accepted { log_number, index, subtree: (p.start, p.end) }),
        Some(_) => Err("does not match the trusted landmark subtree".into()),
        None => Err("not a trusted landmark subtree: cosignatures would be needed".into()),
    }
}
