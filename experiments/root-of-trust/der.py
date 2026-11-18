"""A minimal DER encoder and annotated decoder, written from scratch.

Root of Trust, part 01. Enough of ASN.1 DER (ITU-T X.690) to build and read
an X.509 certificate by hand. Teaching code: real software should use a
mature ASN.1 library.
"""

from __future__ import annotations

from datetime import datetime, timezone

# ----------------------------------------------------------------- encoding


def length(n: int) -> bytes:
    """Definite length, shortest form (X.690 §8.1.3, §10.1)."""
    if n < 0x80:
        return bytes([n])  # short form: one byte, 0..127
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body  # long form: 0x80 + count, then the count bytes


def tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + length(len(value)) + value


def sequence(*items: bytes) -> bytes:
    return tlv(0x30, b"".join(items))


def set_of(*items: bytes) -> bytes:
    # DER sorts the elements of a SET OF by their encodings (X.690 §11.6).
    return tlv(0x31, b"".join(sorted(items)))


def boolean(v: bool) -> bytes:
    return tlv(0x01, b"\xff" if v else b"\x00")  # DER: TRUE is exactly 0xFF


def integer(v: int) -> bytes:
    """Two's complement, minimal length (X.690 §8.3)."""
    n = (v.bit_length() + 8) // 8  # one spare bit for the sign
    raw = v.to_bytes(n, "big", signed=True)
    while len(raw) > 1 and ((raw[0] == 0x00 and raw[1] < 0x80) or (raw[0] == 0xFF and raw[1] >= 0x80)):
        raw = raw[1:]  # drop redundant sign bytes
    return tlv(0x02, raw)


def oid(dotted: str) -> bytes:
    """Object identifier: first two arcs as 40*a+b, then base-128 (X.690 §8.19)."""
    arcs = [int(a) for a in dotted.split(".")]
    out = bytearray()
    for arc in [40 * arcs[0] + arcs[1], *arcs[2:]]:
        groups = [arc & 0x7F]
        arc >>= 7
        while arc:
            groups.append(0x80 | (arc & 0x7F))  # high bit set: "more bytes follow"
            arc >>= 7
        out += bytes(reversed(groups))
    return tlv(0x06, bytes(out))


def bit_string(data: bytes, unused_bits: int = 0) -> bytes:
    return tlv(0x03, bytes([unused_bits]) + data)


def octet_string(data: bytes) -> bytes:
    return tlv(0x04, data)


def utf8_string(s: str) -> bytes:
    return tlv(0x0C, s.encode("utf-8"))


def time(t: datetime) -> bytes:
    """RFC 5280 §4.1.2.5: UTCTime up to 2049, GeneralizedTime from 2050."""
    t = t.astimezone(timezone.utc)
    if t.year < 2050:
        return tlv(0x17, t.strftime("%y%m%d%H%M%SZ").encode())
    return tlv(0x18, t.strftime("%Y%m%d%H%M%SZ").encode())


def explicit(n: int, inner: bytes) -> bytes:
    """[n] EXPLICIT: a constructed context tag wrapping a complete TLV."""
    return tlv(0xA0 | n, inner)


def implicit_primitive(n: int, value: bytes) -> bytes:
    """[n] IMPLICIT on a primitive type: the tag is replaced, the value kept."""
    return tlv(0x80 | n, value)


# ----------------------------------------------------------------- decoding

UNIVERSAL = {
    0x01: "BOOLEAN", 0x02: "INTEGER", 0x03: "BIT STRING", 0x04: "OCTET STRING",
    0x05: "NULL", 0x06: "OBJECT IDENTIFIER", 0x0C: "UTF8String", 0x13: "PrintableString",
    0x16: "IA5String", 0x17: "UTCTime", 0x18: "GeneralizedTime", 0x30: "SEQUENCE", 0x31: "SET",
}


def tag_name(tag: int) -> str:
    cls = tag >> 6
    if cls == 0:
        return UNIVERSAL.get(tag, f"universal {tag & 0x1F}")
    kind = "" if tag & 0x20 == 0 else " (constructed)"
    return f"[{tag & 0x1F}]{kind}" if cls == 2 else f"class {cls} tag {tag & 0x1F}"


def read(buf: bytes, pos: int) -> tuple[int, int, int, int]:
    """Return (tag, header_len, value_len, end) of the TLV at pos, strictly DER."""
    tag = buf[pos]
    if tag & 0x1F == 0x1F:
        raise ValueError("multi-byte tags are not used in X.509")
    first = buf[pos + 1]
    if first < 0x80:
        n, hdr = first, 2
    else:
        k = first & 0x7F
        if k == 0 or k > 4:
            raise ValueError("indefinite or oversized length")
        n = int.from_bytes(buf[pos + 2 : pos + 2 + k], "big")
        if n < 0x80 or buf[pos + 2] == 0:
            raise ValueError("non-minimal length: not DER")
        hdr = 2 + k
    end = pos + hdr + n
    if end > len(buf):
        raise ValueError("value runs past the end")
    return tag, hdr, n, end


def decode_oid(value: bytes) -> str:
    arcs, cur = [], 0
    for b in value:
        cur = (cur << 7) | (b & 0x7F)
        if not b & 0x80:
            arcs.append(cur)
            cur = 0
    first = arcs[0]
    a = min(first // 40, 2)
    return ".".join(str(x) for x in [a, first - 40 * a, *arcs[1:]])


def walk(buf: bytes, start: int = 0, end: int | None = None, depth: int = 0, names=None):
    """Yield (offset, depth, tag, header_len, value_len, label) for every TLV."""
    end = len(buf) if end is None else end
    pos = start
    while pos < end:
        tag, hdr, n, nxt = read(buf, pos)
        value = buf[pos + hdr : nxt]
        label = tag_name(tag)
        if tag == 0x06:
            o = decode_oid(value)
            label += f" {o}" + (f" ({names[o]})" if names and o in names else "")
        elif tag in (0x0C, 0x13, 0x16, 0x17, 0x18) or tag == 0x82:
            label += f" '{value.decode()}'"
        elif tag == 0x02:
            label += f" {int.from_bytes(value, 'big', signed=True)}" if n <= 8 else f" ({n} bytes)"
        elif tag == 0x01:
            label += " TRUE" if value == b"\xff" else " FALSE"
        yield pos, depth, tag, hdr, n, label
        constructed = tag & 0x20
        # Extensions hide DER inside OCTET STRING; descend into it as well.
        if constructed or (tag == 0x04 and n and value[0] in (0x30, 0x03)):
            yield from walk(buf, pos + hdr, nxt, depth + 1, names)
        pos = nxt


def dump(buf: bytes, names=None, width: int = 44) -> str:
    """One line per TLV: offset, header + first value bytes (indented by depth), meaning."""
    lines = []
    for off, depth, tag, hdr, n, label in walk(buf, names=names):
        room = (width - 2 * depth) // 3  # bytes that fit in the hex column
        shown = hdr if tag & 0x20 else min(hdr + n, room)
        hexs = buf[off : off + shown].hex(" ")
        if shown < hdr + n and not tag & 0x20:
            hexs = buf[off : off + shown - 1].hex(" ") + " .."
        lines.append(f"{off:4d}  {'  ' * depth}{hexs:<{width - 2 * depth}}  {label}")
    return "\n".join(lines)
