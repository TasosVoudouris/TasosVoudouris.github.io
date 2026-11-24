//! Just enough DER to take a certificate apart, ported from Part 01 (`der.py`).
//! Strict: definite lengths only, minimal length encodings, single-byte tags.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Tlv {
    pub tag: u8,
    pub header: usize,
    pub len: usize,
}

impl Tlv {
    pub fn total(&self) -> usize {
        self.header + self.len
    }
}

pub fn read(buf: &[u8], pos: usize) -> Result<Tlv, String> {
    let tag = *buf.get(pos).ok_or("truncated tag")?;
    if tag & 0x1F == 0x1F {
        return Err("multi-byte tags are not used in X.509".into());
    }
    let first = *buf.get(pos + 1).ok_or("truncated length")?;
    let (len, header) = if first < 0x80 {
        (first as usize, 2)
    } else {
        let k = (first & 0x7F) as usize;
        if k == 0 || k > 4 {
            return Err("indefinite or oversized length".into());
        }
        let bytes = buf.get(pos + 2..pos + 2 + k).ok_or("truncated length")?;
        let n = bytes.iter().fold(0usize, |a, &b| (a << 8) | b as usize);
        if bytes[0] == 0 || n < 0x80 {
            return Err("non-minimal length".into());
        }
        (n, 2 + k)
    };
    if pos + header + len > buf.len() {
        return Err("value runs past the end".into());
    }
    Ok(Tlv { tag, header, len })
}

/// The complete TLVs inside a constructed TLV that starts at the beginning of `tlv`.
pub fn children(tlv: &[u8]) -> Result<Vec<&[u8]>, String> {
    let outer = read(tlv, 0)?;
    if outer.total() != tlv.len() {
        return Err("trailing data after the TLV".into());
    }
    let mut out = vec![];
    let mut pos = outer.header;
    while pos < outer.total() {
        let t = read(tlv, pos)?;
        out.push(&tlv[pos..pos + t.total()]);
        pos += t.total();
    }
    Ok(out)
}

/// The value bytes of a TLV.
pub fn value(tlv: &[u8]) -> Result<&[u8], String> {
    let t = read(tlv, 0)?;
    Ok(&tlv[t.header..t.total()])
}

/// Encode a TLV with a minimal length.
pub fn tlv(tag: u8, value: &[u8]) -> Vec<u8> {
    let mut out = vec![tag];
    let n = value.len();
    if n < 0x80 {
        out.push(n as u8);
    } else {
        let bytes: Vec<u8> = n.to_be_bytes().iter().copied().skip_while(|&b| b == 0).collect();
        out.push(0x80 | bytes.len() as u8);
        out.extend(bytes);
    }
    out.extend_from_slice(value);
    out
}
