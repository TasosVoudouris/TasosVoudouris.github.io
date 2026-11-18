---
title: 'A certificate, byte by byte'
description: 'Part 00 drew a certificate as a signed card. This part takes a real one apart: 342 bytes of ASN.1 DER, every tag, every length, every field, built by hand in Python and checked byte for byte against a real library and OpenSSL. Then the same certificate with ML-DSA-44, at 4,002 bytes.'
part: 1
pubDate: 2026-11-18
tags:
  - x509
  - asn1
  - der
  - certificates
  - post-quantum
  - ml-dsa
companion: experiments/root-of-trust
---

In Part 00 a certificate was a card: a name, a key, some dates, and a signature at the bottom. That picture is right, and it hides almost everything that matters when you write code that reads one. Real certificates are binary. They are written in a notation from the 1980s called **ASN.1**, encoded with a strict set of rules called **DER**, and every byte is there for a reason.

This part takes one real certificate apart, all 342 bytes of it. Not a screenshot of a certificate viewer: the actual bytes, at their actual offsets. We will build it twice, once by hand with an encoder written from scratch and once with a production library, and check that the two are identical. Then we will ask an independent tool, OpenSSL, to read it back. At the end we swap Ed25519 for the post-quantum ML-DSA-44 and watch the same certificate grow to 4,002 bytes.

By the end you should be able to:

1. read a hex dump of any X.509 certificate and say where each field starts and ends;
2. explain the tag, length and value of every element, including the odd ones (`A0`, `A3`, `82`, the stray `00` before a serial number, the `07` in front of a key usage);
3. say exactly which bytes a CA signs, and why the signature algorithm appears twice;
4. explain why the encoding has to be *strict*, with two real attacks that happened because it was not;
5. account for every one of the 4,002 bytes of the post-quantum version.

Everything here is reproducible. The companion code is [`experiments/root-of-trust/`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust): `der.py` (the encoder), `01_certificate.py` (the certificate), and `test_01_certificate.py`, which checks every offset and size quoted in this article.

## The certificate on the table

Here is what our certificate *says*, in words:

> The toy CA called **Root of Trust Toy CA** states that the Ed25519 public key `18 27 25 5e …` belongs to **example.com** and **www.example.com**, from 18 November 2026 to 3 January 2027. The key may be used for digital signatures, for TLS server authentication only, and it may **not** be used to issue other certificates. Serial number `af df f3 19 …`. Signed, the CA.

And here is what it *is*. Every byte, sixteen per row, offsets in hex on the left:

```text
0000  30 82 01 52 30 82 01 04 a0 03 02 01 02 02 11 00
0010  af df f3 19 2f 17 c9 9d 73 3a f5 dd 7a 92 0d 7d
0020  30 05 06 03 2b 65 70 30 1f 31 1d 30 1b 06 03 55
0030  04 03 0c 14 52 6f 6f 74 20 6f 66 20 54 72 75 73
0040  74 20 54 6f 79 20 43 41 30 1e 17 0d 32 36 31 31
0050  31 38 30 30 30 30 30 30 5a 17 0d 32 37 30 31 30
0060  33 32 33 35 39 35 39 5a 30 16 31 14 30 12 06 03
0070  55 04 03 0c 0b 65 78 61 6d 70 6c 65 2e 63 6f 6d
0080  30 2a 30 05 06 03 2b 65 70 03 21 00 18 27 25 5e
0090  84 27 2e 08 b4 a6 ad 24 39 d7 bd 57 6f b4 0c ef
00a0  5e 4b 86 6e fb 25 1f d1 bc 7b 73 2c a3 5e 30 5c
00b0  30 27 06 03 55 1d 11 04 20 30 1e 82 0b 65 78 61
00c0  6d 70 6c 65 2e 63 6f 6d 82 0f 77 77 77 2e 65 78
00d0  61 6d 70 6c 65 2e 63 6f 6d 30 0c 06 03 55 1d 13
00e0  01 01 ff 04 02 30 00 30 0e 06 03 55 1d 0f 01 01
00f0  ff 04 04 03 02 07 80 30 13 06 03 55 1d 25 04 0c
0100  30 0a 06 08 2b 06 01 05 05 07 03 01 30 05 06 03
0110  2b 65 70 03 41 00 33 ea 60 ac 76 8e a9 f4 7b 63
0120  15 b6 27 9d 29 a8 ca 96 90 75 f5 31 39 a3 9e fa
0130  dd 8b 61 5a 78 5d 9d 2f 9c e8 7f b4 6d 1f 8f b9
0140  4a fc bd e7 50 1c fe 49 dd 8f 6b e9 79 2c 4e c9
0150  3e e0 9f a5 6f 0b
```

Even without knowing anything, you can already spot things. The ASCII of `Root of Trust Toy CA` sits at `0x34`. Three times, at `0x22`, `0x84` and `0x10e`, the same five bytes `06 03 2b 65 70` appear. The text `261118000000Z` (a date) is at `0x4c`. Near the end, after `03 41 00`, comes a 64-byte blob with no visible structure: the signature. By the end of this part every other byte will be just as readable.

The keys come from fixed seeds, so if you run `python 01_certificate.py` you get exactly these bytes. Ed25519 signatures are deterministic, so even the signature is reproducible.

<div class="note">

The certificate is deliberately small: one name in the issuer, one in the subject, four extensions, a 32-byte key. A real certificate from a public CA carries more (key identifiers, a link to the issuer, revocation information, policies, and the Certificate Transparency receipts from Part 00) and usually lands somewhere between one and two kilobytes. Everything it adds is built from exactly the pieces in this part.

</div>

## ASN.1 and DER: a grammar and a spelling

Two different things hide behind the word "ASN.1", and keeping them apart makes everything easier.

**ASN.1** (Abstract Syntax Notation One, ITU-T X.680) is a *schema language*. It describes the shape of data, like a C struct or a Protocol Buffers message, without saying anything about bytes. RFC 5280 defines the certificate in it. The top level is three lines:

```text
Certificate  ::=  SEQUENCE  {
     tbsCertificate       TBSCertificate,
     signatureAlgorithm   AlgorithmIdentifier,
     signatureValue       BIT STRING  }
```

and the signed part, the `TBSCertificate` ("to be signed"), is:

```text
TBSCertificate  ::=  SEQUENCE  {
     version         [0]  EXPLICIT Version DEFAULT v1,
     serialNumber         CertificateSerialNumber,
     signature            AlgorithmIdentifier,
     issuer               Name,
     validity             Validity,
     subject              Name,
     subjectPublicKeyInfo SubjectPublicKeyInfo,
     issuerUniqueID  [1]  IMPLICIT UniqueIdentifier OPTIONAL,
     subjectUniqueID [2]  IMPLICIT UniqueIdentifier OPTIONAL,
     extensions      [3]  EXPLICIT Extensions OPTIONAL }
```

Keep this definition open; the rest of the article is a walk down it.

**Encoding rules** turn values of an ASN.1 type into bytes. There are several families, defined in ITU-T X.690 and its siblings: **BER** (Basic Encoding Rules), **DER** (Distinguished Encoding Rules), **CER**, **PER** (packed, used in mobile telephony), **XER** (XML). X.509 certificates use **DER**.

The difference between BER and DER is the heart of this part, so here it is in one sentence: **BER allows many byte strings for the same value; DER allows exactly one.** In BER you may write a length in more bytes than needed, write TRUE as any nonzero byte, leave a length open and close it later, list the members of a SET in any order. DER forbids all of that. Every value has one canonical encoding.

Why insist on that? Because a signature is over *bytes*, not over *values*. If two different byte strings meant the same certificate, a verifier that decoded and re-encoded would check the signature against different bytes than the CA signed, and worse, two parsers could disagree about what a single byte string means. The section on [strictness](#why-der-is-strict) shows both failures happening in the real world.

## Tag, length, value

Every DER element, without exception, has the same three parts:

- **T**ag: one byte (for everything in X.509) saying what kind of thing this is;
- **L**ength: how many bytes of value follow;
- **V**alue: the content. For a *constructed* type like SEQUENCE, the value is simply more TLVs, one after another.

<figure class="plate">
<img src="/images/root/01-tlv.svg" alt="The bytes 30, 82 01 52 and 338 bytes of content labelled T, L and V. Below, the tag byte 0x30 split into bits 00, 1, 10000: universal class, constructed, number 16 SEQUENCE. And 0xA3 split into 10, 1, 00011: context-specific, constructed, number 3." width="1000" height="560" loading="lazy" />
<figcaption>Tag, length, value. The tag byte is itself three small fields.</figcaption>
</figure>

### The tag byte

The tag is not an arbitrary number; it packs three fields into eight bits:

| bits | field | meaning |
|---|---|---|
| 8–7 | class | `00` universal (defined by ASN.1 itself), `01` application, `10` context-specific (defined by the surrounding structure), `11` private |
| 6 | P/C | `0` primitive (the value is raw bytes), `1` constructed (the value is more TLVs) |
| 5–1 | number | which type within the class; `11111` means "the number continues in the following bytes", which X.509 never needs |

So `0x30 = 0011 0000` is class universal, constructed, number 16, which ASN.1 assigns to SEQUENCE. A SEQUENCE always contains TLVs, so it is always constructed, which is why you never see `0x10` in a certificate. The same reasoning gives `0x31` for SET (number 17, constructed).

The universal tags that appear in our certificate:

| tag | number | type | used for |
|---|---|---|---|
| `01` | 1 | BOOLEAN | the *critical* flag of an extension |
| `02` | 2 | INTEGER | version, serial number |
| `03` | 3 | BIT STRING | public key, signature, key usage |
| `04` | 4 | OCTET STRING | the envelope around each extension |
| `06` | 6 | OBJECT IDENTIFIER | algorithms, attribute types, extension types |
| `0C` | 12 | UTF8String | the common names |
| `17` | 23 | UTCTime | validity dates |
| `30` | 16 + constructed | SEQUENCE | almost every structure |
| `31` | 17 + constructed | SET | one level inside a Name |

The other two tags in the certificate are *context-specific*: `A0`, `A3` and `82`. `0xA3 = 1010 0011` is context-specific (`10`), constructed (`1`), number 3, which ASN.1 writes as `[3]`. Its meaning depends entirely on where it appears. Inside a TBSCertificate, `[3]` means "extensions follow", because the schema above says `extensions [3] EXPLICIT Extensions`. Inside a SubjectAltName, as we will see, `[2]` means "a DNS name". Context-specific tags exist for exactly this: to tell optional fields apart when a plain type tag would be ambiguous.

### The length

<figure class="plate">
<img src="/images/root/01-lengths.svg" alt="Short form: the byte 05 with top bit 0 means length 5. Long form: 82 01 52, where 82 has top bit 1 and says two length bytes follow, and 0x0152 = 338. DER always uses the shortest form; 81 05 is legal BER but not DER, and the indefinite length 80 is banned." width="1000" height="470" loading="lazy" />
<figcaption>Two forms for the length. DER picks the shortest one, always.</figcaption>
</figure>

If the value is shorter than 128 bytes, the length is one byte holding the number: `05` means five. If it is 128 or more, the first length byte has its top bit set and its low seven bits say *how many* length bytes follow; those bytes are the length, big-endian. `82 01 52` reads "two length bytes follow: `0x0152` = 338".

DER adds two rules (X.690 §10.1): the length must use the **shortest** possible form, so `81 05` (long form for a value that fits the short form) is invalid, and the **indefinite** form `80`, where the value is closed later by `00 00`, is not allowed at all. A strict reader rejects both. Ours does, and the test file checks it.

### The first eight bytes

With just that, we can read the start of the file:

```text
30 82 01 52     SEQUENCE, length 338     ← Certificate, offsets 0 .. 341
30 82 01 04     SEQUENCE, length 260     ← TBSCertificate, offsets 4 .. 267
```

Check the arithmetic. The outer header is 4 bytes and the value 338 bytes: 4 + 338 = 342, the size of the file. The TBSCertificate header is also 4 bytes and its value 260 bytes, so it spans 264 bytes, from offset 4 to offset 267. Then the outer SEQUENCE continues with two more elements: the signature algorithm (7 bytes, at 268) and the signature (67 bytes, at 275). 4 + 264 + 7 + 67 = 342. Nothing is left over, nothing is missing.

<figure class="plate">
<img src="/images/root/01-nesting.svg" alt="The certificate as nested boxes. The outer Certificate, 342 bytes at offset 0, holds tbsCertificate (264 bytes at offset 4, marked as the signed part), signatureAlgorithm (7 bytes at 268) and signatureValue (67 bytes at 275). Inside tbsCertificate: version 5 bytes at 8, serialNumber 19 at 13, signature 7 at 32, issuer 33 at 39, validity 32 at 72, subject 24 at 104, subjectPublicKeyInfo 44 at 128, extensions 96 at 172." width="1000" height="740" loading="lazy" />
<figcaption>The whole certificate. Every field with its offset and its size, header included. The red box is what the CA signs.</figcaption>
</figure>

## The signed part, field by field

### version: `A0 03 02 01 02`

```text
   8  a0 03            [0] (constructed), length 3
  10    02 01 02       INTEGER 2
```

The schema says `version [0] EXPLICIT Version DEFAULT v1`. Three words, three lessons.

**`[0] EXPLICIT`.** EXPLICIT tagging means *wrap*: the context tag `[0]` becomes a constructed TLV whose value is the complete, normal encoding of the inner type. So we get `A0` (context-specific, constructed, number 0), length 3, and inside it a full INTEGER TLV `02 01 02`. The alternative, IMPLICIT, *replaces* the inner tag instead of wrapping it; we meet it in the SubjectAltName.

**`Version`.** `Version ::= INTEGER { v1(0), v2(1), v3(2) }`. Version 3 is encoded as the integer **2**. Every X.509v3 certificate you have ever seen says `02` here. OpenSSL prints it as `Version: 3 (0x2)`, which looks like a typo and is not.

**`DEFAULT v1`.** DER says that a field equal to its DEFAULT value must be **left out** (X.690 §11.5). A version 1 certificate therefore has no `A0` element at all; the first thing in its TBSCertificate is the serial number. Version 3 is not the default, so it is written. Extensions only exist in v3, so any certificate with extensions has these five bytes.

### serialNumber: the mysterious `00`

```text
  13  02 11 00 af df f3 19 2f 17 c9 9d 73 3a f5 dd 7a 92 0d 7d
```

Tag `02` (INTEGER), length `0x11` = 17. But we chose a 16-byte serial number. Where does the 17th byte, that leading `00`, come from?

ASN.1 INTEGERs are **signed**, in two's complement, big-endian (X.690 §8.3). The first byte of our serial is `0xAF = 1010 1111`; its top bit is 1. Written as-is, `af df f3 …` would be a *negative* number. RFC 5280 §4.1.2.2 says the serial number MUST be a positive integer, so the encoder adds a `00` byte in front to keep the sign bit clear. We set the top bit of the serial on purpose in `01_certificate.py` so that you would see this.

The minimality rule applies to integers too: no redundant leading `00` (or, for negatives, `FF`) bytes. So:

| value | DER | why |
|---|---|---|
| 0 | `02 01 00` | at least one byte |
| 2 | `02 01 02` | |
| 127 | `02 01 7F` | top bit clear: fits |
| 128 | `02 02 00 80` | `80` alone would be −128 |
| 256 | `02 02 01 00` | |

Our encoder does exactly this; it computes one byte more than the bit length needs, then strips bytes while they are redundant:

```python
def integer(v: int) -> bytes:
    """Two's complement, minimal length (X.690 §8.3)."""
    n = (v.bit_length() + 8) // 8  # one spare bit for the sign
    raw = v.to_bytes(n, "big", signed=True)
    while len(raw) > 1 and ((raw[0] == 0x00 and raw[1] < 0x80) or (raw[0] == 0xFF and raw[1] >= 0x80)):
        raw = raw[1:]  # drop redundant sign bytes
    return tlv(0x02, raw)
```

Two more rules concern the serial. RFC 5280 limits it to 20 octets, so the largest legal serial is a 20-byte INTEGER, which with the sign byte is the 160-bit range. And the CA/Browser Forum Baseline Requirements (§7.1) require public CAs to put **at least 64 bits of CSPRNG output** into it. That rule is a lesson from history: in 2008 researchers used an MD5 collision to create a rogue CA certificate, and predictable serial numbers were part of what made the attack practical. Random serials make the CA's output unpredictable to the person requesting the certificate, which kills that whole class of chosen-prefix attacks even if the hash is weak.

<div class="warning">

Many real certificates have serials whose first byte is `0x80` or more, so their INTEGER carries this extra `00`. Code that reads "the serial number" as "the value bytes" will sometimes get 17 bytes and sometimes 16 for the same kind of serial. Always decode INTEGERs as integers, never as raw byte strings.

</div>

### signature: the algorithm, the first time

```text
  32  30 05                  SEQUENCE
  34    06 03 2b 65 70       OBJECT IDENTIFIER 1.3.101.112 (ed25519)
```

This field is confusingly named `signature`, but it holds only the *name* of the signature algorithm, as an `AlgorithmIdentifier`:

```text
AlgorithmIdentifier  ::=  SEQUENCE  {
     algorithm               OBJECT IDENTIFIER,
     parameters              ANY DEFINED BY algorithm OPTIONAL  }
```

For Ed25519, RFC 8410 §3 says the parameters MUST be **absent**. Not `NULL`, absent. So the SEQUENCE holds only the OID. (RSA, for historical reasons, uses an explicit `NULL`, `05 00`, which is why RSA certificates have two more bytes here. Absent and NULL are different encodings, so code must follow each algorithm's rule exactly.)

That leaves the **object identifier** itself. An OID is a path in a global tree of names, written in dots: `1.3.101.112` means arc 1 (ISO), then 3 (identified organisation), then 101 (Thawte, which donated the arc), then 112 (Ed25519). Encoding it takes two tricks:

<figure class="plate">
<img src="/images/root/01-oid.svg" alt="1.3.101.112 encodes as 2B 65 70: the first two arcs fold into 40 times 1 plus 3 = 43 = 0x2B, then 101 = 0x65 and 112 = 0x70. The arc 840 needs two base-128 digits: 6 and 72, written 0x86 (top bit set, more follows) and 0x48 (top bit clear, last). ML-DSA-44's OID 2.16.840.1.101.3.4.3.17 encodes as 60 86 48 01 65 03 04 03 11." width="1000" height="560" loading="lazy" />
<figcaption>Object identifiers: fold the first two arcs, then write each arc in base 128.</figcaption>
</figure>

1. **The first two arcs fold into one byte**: $40 \cdot a + b$. The first arc is only ever 0, 1 or 2, so this is reversible. For 1.3, $40 \cdot 1 + 3 = 43 = \texttt{0x2B}$. That is why almost every OID you will ever see in a certificate begins with `2B` (1.3), `55` (2.5, the X.500 directory: `2·40 + 5 = 85 = 0x55`) or `60` (2.16, countries: `2·40 + 16 = 96 = 0x60`).
2. **Every other arc is written in base 128**, most significant digit first, with the top bit of each byte meaning "more digits follow". 101 and 112 are below 128, so they are single bytes `65` and `70`. But 840 (the country code for the US, inside the ML-DSA OID) is $6 \cdot 128 + 72$, so it becomes two bytes: `0x80 | 6 = 0x86`, then `72 = 0x48`.

Put together, Ed25519 is `06 03 2B 65 70`. The same rule makes `55 04 03` (2.5.4.3, commonName) and `55 1D 11` (2.5.29.17, subjectAltName), which you can now find by eye in the hex dump. The encoder:

```python
def oid(dotted: str) -> bytes:
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
```

### issuer and subject: SEQUENCE OF SET OF

```text
  39  30 1f                                SEQUENCE           Name
  41    31 1d                              SET                RelativeDistinguishedName
  43      30 1b                            SEQUENCE           AttributeTypeAndValue
  45        06 03 55 04 03                 OBJECT IDENTIFIER  2.5.4.3 (commonName)
  50        0c 14 52 6f 6f 74 20 6f 66 …   UTF8String         'Root of Trust Toy CA'
```

A name in X.509 is not a string. It is a list of sets of (type, value) pairs, inherited from the X.500 directory that was supposed to hold every person and organisation in the world:

```text
Name ::= SEQUENCE OF RelativeDistinguishedName
RelativeDistinguishedName ::= SET OF AttributeTypeAndValue
AttributeTypeAndValue ::= SEQUENCE { type OBJECT IDENTIFIER, value ANY }
```

The outer SEQUENCE is the path from the top of the directory down (country, organisation, common name, …). Each step is a SET because one step may need several attributes at once; in practice it almost always holds exactly one. Our issuer is the shortest legal useful name: one step, one attribute, `CN = Root of Trust Toy CA`, encoded as UTF8String (tag `0C`), 20 bytes. The subject at offset 104 has the same shape with `CN = example.com`.

Two things about names matter for security.

**Chaining is by name.** When a verifier builds a chain, it looks for a certificate whose *subject* equals this certificate's *issuer*. Part 00's toy code compared strings; real code compares these structures, with rules in RFC 5280 §7.1 about case and whitespace. The bytes of our issuer (offsets 39 to 71) are exactly the bytes of the toy CA certificate's subject, which `01_certificate.py --write` also creates so that OpenSSL can verify the chain.

**The subject name is no longer what browsers check.** Look at the hex dump again: `example.com` appears three times, once in the subject and twice in the SubjectAltName extension further down. Browsers match the site name against the **SubjectAltName only**. Chrome stopped accepting a matching common name in 2017, and RFC 9525 (2023), the current rules for checking service identity, removed it from the standard. The CN is now mostly decoration, kept for compatibility.

### validity: two clocks and a 2050 problem

```text
  72  30 1e                                    SEQUENCE
  74    17 0d 32 36 31 31 31 38 30 30 30 30 30 30 5a    UTCTime '261118000000Z'
  89    17 0d 32 37 30 31 30 33 32 33 35 39 35 39 5a    UTCTime '270103235959Z'
```

Validity is two times, `notBefore` and `notAfter`. Their value bytes are plain ASCII: `32 36 31 31 31 38 …` is the text `261118000000Z`, which reads `YY MM DD hh mm ss Z`, 18 November 2026 at midnight, UTC. The `Z` (Zulu time) is mandatory, and so are the seconds (RFC 5280 §4.1.2.5.1).

`UTCTime` (tag `17`) has a two-digit year. RFC 5280 fixes the interpretation: `YY ≥ 50` means 19YY, `YY < 50` means 20YY. Dates in 2050 or later must use `GeneralizedTime` (tag `18`, four-digit year), and dates before 2050 must use `UTCTime`. A certificate valid until 2051 therefore mixes both types in one SEQUENCE. Our encoder implements the switch, and the tests check both sides of it.

Our certificate is valid for 47 days (the last second is 23:59:59 on day 47). That is not a random choice: the CA/Browser Forum has voted to shrink the maximum lifetime of public TLS certificates in steps, down to 47 days by 2029. Shorter lifetimes mean more certificates issued, more log entries, more signatures. Keep that in mind when we reach Merkle Tree Certificates, whose whole design assumes certificates that live briefly.

### subjectPublicKeyInfo: the key, inside a BIT STRING

```text
 128  30 2a                         SEQUENCE           SubjectPublicKeyInfo
 130    30 05                       SEQUENCE           AlgorithmIdentifier
 132      06 03 2b 65 70            OBJECT IDENTIFIER  1.3.101.112 (ed25519)
 137    03 21 00 18 27 25 5e …      BIT STRING         33 bytes: 00 + the 32-byte key
```

```text
SubjectPublicKeyInfo  ::=  SEQUENCE  {
     algorithm            AlgorithmIdentifier,
     subjectPublicKey     BIT STRING  }
```

This is the field the whole certificate exists for. It names the algorithm again (the *subject's* key algorithm this time, which may differ from the CA's signing algorithm) and then holds the key.

The key is a BIT STRING, and BIT STRINGs have one quirk: the first value byte says how many bits at the **end** of the last byte are unused padding, because a bit string's length need not be a multiple of eight. A key is always whole bytes, so that byte is `00`. Hence `03 21 00`: BIT STRING, length 33, zero unused bits, then the 32 bytes of the Ed25519 public key (RFC 8410 §4).

Why is a key a *bit* string at all? History: when X.509 was written, some keys were defined as bit strings. Today the convention is that the BIT STRING's bytes are the key in its own algorithm-specific format. The `00` byte is pure tax: one byte per key, one per signature.

The whole SubjectPublicKeyInfo is 44 bytes: 2 header + 7 algorithm + 35 key. Keep this number; in the post-quantum version it becomes 1,334.

### extensions: a box inside a box

```text
 172  a3 5e        [3] (constructed), length 94
 174    30 5c      SEQUENCE, length 92: the list of extensions
```

The `[3] EXPLICIT` wrapper says "extensions follow", and inside it is a SEQUENCE of `Extension`:

```text
Extension  ::=  SEQUENCE  {
     extnID      OBJECT IDENTIFIER,
     critical    BOOLEAN DEFAULT FALSE,
     extnValue   OCTET STRING  }
```

Two design choices hide in these three lines, and both are about what to do with an extension you have never heard of.

**The value is wrapped in an OCTET STRING.** Every extension's real content is DER-encoded *first*, and the resulting bytes are then put inside an OCTET STRING (tag `04`). A parser that does not know an extension can therefore skip it cleanly: it reads the OID, sees an OCTET STRING of some length, and moves on, without understanding a single byte inside. That is why OpenSSL's `asn1parse` (below) prints these as `[HEX DUMP]` unless you ask it to look inside. Our decoder peeks into OCTET STRINGs that start with a SEQUENCE or a BIT STRING so you can see both layers.

**The critical flag.** RFC 5280 §4.2: a verifier that meets a **critical** extension it does not recognise MUST reject the certificate. A non-critical one it may ignore. Critical means "if you do not understand this, you do not understand this certificate". And because the field is `DEFAULT FALSE`, DER omits it entirely for non-critical extensions; you only ever see `01 01 FF` (BOOLEAN TRUE, and TRUE in DER is exactly `FF`).

Our four extensions, in order.

**subjectAltName** (2.5.29.17), offset 176, not critical:

```text
 176  30 27
 178    06 03 55 1d 11                 OID 2.5.29.17 (subjectAltName)
 183    04 20                          OCTET STRING, 32 bytes, containing:
 185      30 1e                        SEQUENCE  (GeneralNames)
 187        82 0b 65 78 61 6d 70 6c 65 2e 63 6f 6d           [2] 'example.com'
 200        82 0f 77 77 77 2e 65 78 61 6d 70 6c 65 2e 63 6f 6d  [2] 'www.example.com'
```

`GeneralName` is a CHOICE of name kinds, each with its own context tag: `[1]` email, `[2]` DNS name, `[6]` URI, `[7]` IP address, and so on. Here the tagging is **IMPLICIT**: the context tag *replaces* the inner type's tag instead of wrapping it. A `dNSName` is an IA5String (tag `16`), but in a GeneralName it appears as `82`: context-specific (`10`), primitive (`0`), number 2. No inner `16` tag; the bytes after `82 0b` are directly the 11 ASCII characters. Compare with `A0 03 02 01 02` for the version, where EXPLICIT kept the inner INTEGER's tag. IMPLICIT saves two bytes per name and costs you the ability to tell the type from the bytes alone; you need the schema.

**basicConstraints** (2.5.29.19), offset 217, **critical**:

```text
 217  30 0c
 219    06 03 55 1d 13                 OID 2.5.29.19 (basicConstraints)
 224    01 01 ff                       critical: TRUE
 227    04 02 30 00                    OCTET STRING containing an EMPTY SEQUENCE
```

```text
BasicConstraints ::= SEQUENCE {
     cA                      BOOLEAN DEFAULT FALSE,
     pathLenConstraint       INTEGER (0..MAX) OPTIONAL }
```

This is the `is_ca` flag from Part 00, and its encoding is the best DER puzzle in the certificate. Our leaf is *not* a CA, so `cA` is FALSE, which is its DEFAULT, so DER omits it. `pathLenConstraint` only makes sense for CAs, so it is absent too. The SEQUENCE has nothing left: `30 00`. An empty sequence that means "this certificate may not sign other certificates". (The toy CA certificate's version says `30 06 01 01 FF 02 01 00`: cA TRUE, path length 0.)

It looks like nothing, and it is one of the most important byte pairs in the file. In 2002 Moxie Marlinspike showed that Internet Explorer did not check basicConstraints at all: any ordinary site certificate could sign a certificate for *any other site*, and IE accepted the chain. Case 6 of Part 00's toy, with no misbehaving CA needed.

**keyUsage** (2.5.29.15), offset 231, critical:

```text
 241    04 04 03 02 07 80              OCTET STRING containing BIT STRING: 7 unused bits, 1000 0000
```

`KeyUsage` is a BIT STRING with *named bits*: bit 0 is `digitalSignature`, bit 1 `nonRepudiation`, bit 2 `keyEncipherment`, …, bit 5 `keyCertSign`, bit 6 `cRLSign`. Bit 0 is the **most significant** bit of the first byte. We set only `digitalSignature`, so the bits are `1`, which as a byte is `1000 0000 = 0x80`. DER requires trailing zero bits of a named bit list to be removed (X.690 §11.2.2), so the bit string is exactly one bit long, and the "unused bits" byte says the last **7** bits of `0x80` are padding. Hence `03 02 07 80`. A key usage of `digitalSignature + keyEncipherment` would be `03 02 05 A0`.

**extKeyUsage** (2.5.29.37), offset 247, not critical: a SEQUENCE OF purpose OIDs, here only `1.3.6.1.5.5.7.3.1`, *id-kp-serverAuth*: this key may authenticate TLS servers. The OID is a tour of the internet's history in eight bytes: `2B` (1.3: ISO, identified organisation), `06` (US Department of Defense), `01` (internet), `05` (security), `05` (mechanisms), `07` (PKIX), `03` (key purposes), `01` (server authentication).

## Outside the signed part

```text
 268  30 05                    SEQUENCE           signatureAlgorithm
 270    06 03 2b 65 70         OBJECT IDENTIFIER  1.3.101.112 (ed25519)
 275  03 41 00 33 ea 60 …      BIT STRING         65 bytes: 00 + 64-byte signature
```

After the TBSCertificate come the last two fields: the signature algorithm, **again**, and the signature as a BIT STRING (`03 41 00`: length 65, no unused bits, then 64 bytes of Ed25519 signature).

### Why the algorithm appears twice

RFC 5280 §4.1.1.2 requires the outer `signatureAlgorithm` to be identical to the `signature` field inside the TBSCertificate. Why have both? The outer one is convenient (a verifier can read it without parsing the TBS), but it is **not signed**; anyone can change it. The inner one *is* signed, so the CA's choice of algorithm is protected by the very signature it describes. Without it, an attacker could try to make the verifier check the signature under a different, weaker algorithm than the CA used. A careful verifier checks that the two copies match.

### Exactly which bytes are signed

The CA signs the TBSCertificate: **all 264 bytes from offset 4 to offset 267, including its own `30 82 01 04` header**. Not the decoded fields, not a re-encoding: those exact bytes. Ed25519 signs the message directly (no separate hash step as with RSA or ECDSA), so in `01_certificate.py` the signing line is literally:

```python
signature = CA_KEY.sign(tbs)  # Ed25519 signs the TBS bytes directly
```

This has a consequence that has bitten many implementations: **a verifier must check the signature against the bytes it received, never against its own re-encoding of what it parsed.** If a parser accepted a slightly non-DER input (say, a long-form length where a short one fits) and the verifier re-encoded it canonically before checking, the signature would fail on a genuine certificate. Or, worse, a parser that "fixes" bad encodings could make two different byte strings look like the same certificate. Libraries expose the original bytes for this reason (`tbs_certificate_bytes` in Python's `cryptography`).

## Why DER is strict

It is tempting to see DER's rules (shortest lengths, `FF` for TRUE, sorted sets, no defaults) as pedantry. They are not. Every time a widely used parser was *lenient*, someone turned the gap between "what the CA signed" and "what the verifier understood" into an attack. Two examples.

**Null bytes in names (2009).** At Black Hat 2009 Moxie Marlinspike, and independently Dan Kaminsky, showed certificates with a common name like `www.paypal.com\0.thoughtcrime.org`. In DER the name is a length-prefixed string; a NUL byte is just a character. The CA saw a name ending in `thoughtcrime.org`, verified that the requester controlled that domain, and signed. But client code that copied the name into a C string stopped at the `\0` and saw only `www.paypal.com`. The certificate was perfectly valid DER; the bug was a parser that treated a TLV value as something it was not. This is the TLV lesson in its purest form: **the length says where a value ends, not a terminator.**

**BERserk (2014).** RSA PKCS#1 v1.5 signatures contain a small DER structure, `DigestInfo`, that names the hash function and holds the digest. In 2006 Daniel Bleichenbacher showed that verifiers that did not check this structure strictly could be fooled into accepting forged signatures when the public exponent is small (e = 3). In 2014 Intel Security's research team found a variant in Mozilla's NSS library (CVE-2014-1568), nicknamed *BERserk*: NSS parsed the DigestInfo with BER-style flexibility, in particular the long-form lengths that DER forbids, which let an attacker hide garbage bytes and forge RSA signatures, including on certificates. A strict DER parser that rejects non-minimal lengths shuts that door.

Both attacks share a shape: the signer and the verifier interpreted the same bytes differently, and the attacker lived in the difference. DER's one-value-one-encoding rule exists to make that difference impossible, *if* parsers enforce it. That is why the decoder in `der.py` raises an error on non-minimal and indefinite lengths instead of quietly accepting them:

```python
        n = int.from_bytes(buf[pos + 2 : pos + 2 + k], "big")
        if n < 0x80 or buf[pos + 2] == 0:
            raise ValueError("non-minimal length: not DER")
```

## Build it yourself

All the encoding functions above live in `der.py`, about 180 lines including the decoder. With them, the whole TBSCertificate is one function that reads almost like the ASN.1 schema:

```python
def tbs_certificate(spki: bytes, sig_alg: bytes) -> bytes:
    extensions = der.sequence(
        extension(OID["subjectAltName"], der.sequence(
            der.implicit_primitive(2, SITE.encode()),          # dNSName [2] IA5String
            der.implicit_primitive(2, f"www.{SITE}".encode()),
        )),
        extension(OID["basicConstraints"], der.sequence(), critical=True),  # cA DEFAULT FALSE
        extension(OID["keyUsage"], der.bit_string(b"\x80", unused_bits=7), critical=True),
        extension(OID["extKeyUsage"], der.sequence(der.oid(OID["serverAuth"]))),
    )
    return der.sequence(
        der.explicit(0, der.integer(2)),   # version v3 (encoded as 2)
        der.integer(SERIAL),
        sig_alg,                           # signature algorithm (inside the signed part)
        name(CA_NAME),                     # issuer
        der.sequence(der.time(NOT_BEFORE), der.time(NOT_AFTER)),  # validity
        name(SITE),                        # subject
        spki,                              # subjectPublicKeyInfo
        der.explicit(3, extensions),
    )
```

where `extension()` leaves out the critical flag when it is false and wraps the value in an OCTET STRING, exactly as described above. The full certificate is then three lines:

```python
alg = der.sequence(der.oid(OID["ed25519"]))  # parameters absent (RFC 8410 §3)
spki = der.sequence(alg, der.bit_string(public_key_bytes))
tbs = tbs_certificate(spki, alg)
cert = der.sequence(tbs, alg, der.bit_string(CA_KEY.sign(tbs)))
```

The script then builds the same certificate a second way, with the `cryptography` library's `CertificateBuilder`, which uses its own, independent encoder (written in Rust). The first lines of its output:

```text
by hand : 342 bytes, sha256 c166748882c03e4f
library : 342 bytes, sha256 c166748882c03e4f
identical: True
signature verifies with the CA key; signed part = 264 bytes, starting at offset 4
```

Byte for byte the same. This is a strong check, and it is only possible *because* of DER: two independent encoders given the same values must produce the same bytes, since there is only one correct answer. With BER the comparison would be meaningless. Then comes the annotated dump that this whole article quoted from, generated by `der.dump()`:

```text
   0  30 82 01 52                                   SEQUENCE
   4    30 82 01 04                                 SEQUENCE
   8      a0 03                                     [0] (constructed)
  10        02 01 02                                INTEGER 2
  13      02 11 00 af df f3 19 2f 17 c9 9d 73 ..    INTEGER (17 bytes)
  32      30 05                                     SEQUENCE
  34        06 03 2b 65 70                          OBJECT IDENTIFIER 1.3.101.112 (ed25519)
  39      30 1f                                     SEQUENCE
  41        31 1d                                   SET
  43          30 1b                                 SEQUENCE
  45            06 03 55 04 03                      OBJECT IDENTIFIER 2.5.4.3 (commonName)
  50            0c 14 52 6f 6f 74 20 6f 66 20 ..    UTF8String 'Root of Trust Toy CA'
  72      30 1e                                     SEQUENCE
  74        17 0d 32 36 31 31 31 38 30 30 30 ..     UTCTime '261118000000Z'
  89        17 0d 32 37 30 31 30 33 32 33 35 ..     UTCTime '270103235959Z'
 104      30 16                                     SEQUENCE
 106        31 14                                   SET
 108          30 12                                 SEQUENCE
 110            06 03 55 04 03                      OBJECT IDENTIFIER 2.5.4.3 (commonName)
 115            0c 0b 65 78 61 6d 70 6c 65 2e ..    UTF8String 'example.com'
 128      30 2a                                     SEQUENCE
 130        30 05                                   SEQUENCE
 132          06 03 2b 65 70                        OBJECT IDENTIFIER 1.3.101.112 (ed25519)
 137        03 21 00 18 27 25 5e 84 27 2e 08 ..     BIT STRING
 172      a3 5e                                     [3] (constructed)
 174        30 5c                                   SEQUENCE
 176          30 27                                 SEQUENCE
 178            06 03 55 1d 11                      OBJECT IDENTIFIER 2.5.29.17 (subjectAltName)
 183            04 20 30 1e 82 0b 65 78 61 6d ..    OCTET STRING
 185              30 1e                             SEQUENCE
 187                82 0b 65 78 61 6d 70 6c 65 ..   [2] 'example.com'
 200                82 0f 77 77 77 2e 65 78 61 ..   [2] 'www.example.com'
 217          30 0c                                 SEQUENCE
 219            06 03 55 1d 13                      OBJECT IDENTIFIER 2.5.29.19 (basicConstraints)
 224            01 01 ff                            BOOLEAN TRUE
 227            04 02 30 00                         OCTET STRING
 229              30 00                             SEQUENCE
 231          30 0e                                 SEQUENCE
 233            06 03 55 1d 0f                      OBJECT IDENTIFIER 2.5.29.15 (keyUsage)
 238            01 01 ff                            BOOLEAN TRUE
 241            04 04 03 02 07 80                   OCTET STRING
 243              03 02 07 80                       BIT STRING
 247          30 13                                 SEQUENCE
 249            06 03 55 1d 25                      OBJECT IDENTIFIER 2.5.29.37 (extKeyUsage)
 254            04 0c 30 0a 06 08 2b 06 01 05 ..    OCTET STRING
 256              30 0a                             SEQUENCE
 258                06 08 2b 06 01 05 05 07 03 01   OBJECT IDENTIFIER 1.3.6.1.5.5.7.3.1 (serverAuth)
 268    30 05                                       SEQUENCE
 270      06 03 2b 65 70                            OBJECT IDENTIFIER 1.3.101.112 (ed25519)
 275    03 41 00 33 ea 60 ac 76 8e a9 f4 7b 63 ..   BIT STRING
```

Indentation is nesting depth. Read the offset column against the nested-boxes figure above: every number matches.

## Check it with a tool you did not write

Agreement between our encoder and one library is good. A third opinion from a completely different code base is better. With `python 01_certificate.py --write` the script saves the certificate as `01_example_ed25519.der` (and the toy CA as `01_example_ca.der`). OpenSSL can read it:

```text
openssl asn1parse -inform DER -in 01_example_ed25519.der -i
```

```text
    0:d=0  hl=4 l= 338 cons: SEQUENCE
    4:d=1  hl=4 l= 260 cons:  SEQUENCE
    8:d=2  hl=2 l=   3 cons:   cont [ 0 ]
   10:d=3  hl=2 l=   1 prim:    INTEGER           :02
   13:d=2  hl=2 l=  17 prim:   INTEGER           :AFDFF3192F17C99D733AF5DD7A920D7D
   32:d=2  hl=2 l=   5 cons:   SEQUENCE
   34:d=3  hl=2 l=   3 prim:    OBJECT            :ED25519
   39:d=2  hl=2 l=  31 cons:   SEQUENCE
   41:d=3  hl=2 l=  29 cons:    SET
   43:d=4  hl=2 l=  27 cons:     SEQUENCE
   45:d=5  hl=2 l=   3 prim:      OBJECT            :commonName
   50:d=5  hl=2 l=  20 prim:      UTF8STRING        :Root of Trust Toy CA
   72:d=2  hl=2 l=  30 cons:   SEQUENCE
   74:d=3  hl=2 l=  13 prim:    UTCTIME           :261118000000Z
   89:d=3  hl=2 l=  13 prim:    UTCTIME           :270103235959Z
  104:d=2  hl=2 l=  22 cons:   SEQUENCE
  106:d=3  hl=2 l=  20 cons:    SET
  108:d=4  hl=2 l=  18 cons:     SEQUENCE
  110:d=5  hl=2 l=   3 prim:      OBJECT            :commonName
  115:d=5  hl=2 l=  11 prim:      UTF8STRING        :example.com
  128:d=2  hl=2 l=  42 cons:   SEQUENCE
  130:d=3  hl=2 l=   5 cons:    SEQUENCE
  132:d=4  hl=2 l=   3 prim:     OBJECT            :ED25519
  137:d=3  hl=2 l=  33 prim:    BIT STRING
  172:d=2  hl=2 l=  94 cons:   cont [ 3 ]
  174:d=3  hl=2 l=  92 cons:    SEQUENCE
  176:d=4  hl=2 l=  39 cons:     SEQUENCE
  178:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Subject Alternative Name
  183:d=5  hl=2 l=  32 prim:      OCTET STRING      [HEX DUMP]:301E820B6578616D706C652E636F6D820F7777772E6578616D706C652E636F6D
  217:d=4  hl=2 l=  12 cons:     SEQUENCE
  219:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Basic Constraints
  224:d=5  hl=2 l=   1 prim:      BOOLEAN           :255
  227:d=5  hl=2 l=   2 prim:      OCTET STRING      [HEX DUMP]:3000
  231:d=4  hl=2 l=  14 cons:     SEQUENCE
  233:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Key Usage
  238:d=5  hl=2 l=   1 prim:      BOOLEAN           :255
  241:d=5  hl=2 l=   4 prim:      OCTET STRING      [HEX DUMP]:03020780
  247:d=4  hl=2 l=  19 cons:     SEQUENCE
  249:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Extended Key Usage
  254:d=5  hl=2 l=  12 prim:      OCTET STRING      [HEX DUMP]:300A06082B06010505070301
  268:d=1  hl=2 l=   5 cons:  SEQUENCE
  270:d=2  hl=2 l=   3 prim:   OBJECT            :ED25519
  275:d=1  hl=2 l=  65 prim:  BIT STRING
```

Read the columns as `offset : depth  header-length  value-length`. Same offsets, same depths, same lengths. Note the three details we predicted: the version prints as `:02`, the critical flags as `BOOLEAN :255` (that is `0xFF`), and every extension value as an opaque `[HEX DUMP]`, the OCTET STRING envelope doing its job. To look inside one, give OpenSSL its offset: `-strparse 183` parses the SubjectAltName's contents.

The human-readable view, `openssl x509 -inform DER -in 01_example_ed25519.der -noout -text`, decodes the same fields into the familiar form (`Version: 3 (0x2)`, `X509v3 Basic Constraints: critical CA:FALSE`, `TLS Web Server Authentication`, …). And with the toy CA as the trust anchor, OpenSSL verifies the signature and checks the certificate is fit for a TLS server:

```text
openssl verify -purpose sslserver -CAfile ca.pem example.pem
example.pem: OK
```

(The `.pem` files are the same certificates in base64 text; `openssl x509 -inform DER -in 01_example_ca.der -out ca.pem` converts them. PEM is nothing but the DER bytes, base64-encoded, between `-----BEGIN CERTIFICATE-----` lines.)

<div class="note">

Add `-x509_strict` and OpenSSL refuses, with *"Missing Authority Key Identifier"*. That is correct. RFC 5280 §4.2.1.1 says certificates from a conforming CA MUST carry an Authority Key Identifier, a hash-like handle of the issuer's key that helps chain building when names are ambiguous, and CA certificates MUST carry the matching Subject Key Identifier. Our toy leaves both out to keep the dump readable. A real CA would add about 30 bytes for the first, which you could now encode by hand: `[0] IMPLICIT KeyIdentifier` inside a SEQUENCE, inside an OCTET STRING.

</div>

## The same certificate, post-quantum

Now the question this series is really about. Take the same certificate (same names, same dates, same serial, same extensions) and replace Ed25519 with **ML-DSA-44**, the smallest parameter set of the lattice signature standardised in FIPS 204. Only two things change in the code: the algorithm identifier and the keys.

The algorithm identifier is the OID `2.16.840.1.101.3.4.3.17` (NIST's arc for signature algorithms, assigned to ML-DSA-44), again with **absent** parameters, as RFC 9881 specifies. Its encoding, which you can now verify by hand from the OID figure: `06 09 60 86 48 01 65 03 04 03 11`. Nine value bytes against Ed25519's three.

The script builds it with the same `tbs_certificate()` function, signs it with ML-DSA-44 (in its pure form, over the TBS bytes, as RFC 9881 requires), then asks the library to parse the result and verify the signature. It passes. The top-level layout, from our decoder:

```text
   0  30 82 0f 9e           SEQUENCE, length 3998     Certificate: 4002 bytes
   4    30 82 06 14         SEQUENCE, length 1556     TBSCertificate: 1560 bytes
 134      30 82 05 32       SEQUENCE, length 1330     SubjectPublicKeyInfo: 1334 bytes
 151        03 82 05 21 00  BIT STRING, length 1313   00 + 1312-byte public key
1468      a3 5e             [3] extensions            unchanged: 96 bytes
1564    30 0b               SEQUENCE                  signatureAlgorithm: 13 bytes
1577    03 82 09 75 00      BIT STRING, length 2421   00 + 2420-byte signature
```

Everything to the left of the key is the same certificate. The extensions are byte-identical (look: `a3 5e` again, 96 bytes). But the public key is now 1,312 bytes and the signature 2,420, the sizes FIPS 204 fixes for ML-DSA-44, and every length that contains them has moved into long form.

<figure class="plate">
<img src="/images/root/01-sizes.svg" alt="Two bars drawn to scale. Ed25519: 246 bytes of structure, 32 of key, 64 of signature, 342 total. ML-DSA-44: 270 bytes of structure, 1312 of key, 2420 of signature, 4002 total." width="1000" height="430" loading="lazy" />
<figcaption>Drawn to scale. The skeleton is the same size; the cryptography is not.</figcaption>
</figure>

Account for every byte:

| | Ed25519 | ML-DSA-44 |
|---|---:|---:|
| public key | 32 | 1,312 |
| signature | 64 | 2,420 |
| everything else (ASN.1 structure, names, dates, extensions) | 246 | 270 |
| **total** | **342** | **4,002** |

Where do the 24 extra bytes of structure come from? From things this article has explained one by one:

- the algorithm OID appears **three times** (inner signature field, SubjectPublicKeyInfo, outer signatureAlgorithm), and each copy is 6 bytes longer (9 value bytes instead of 3): **18 bytes**;
- three lengths cross the 128 and 256 boundaries and need the long form with two length bytes: the SubjectPublicKeyInfo (`30 2a` becomes `30 82 05 32`), the key's BIT STRING (`03 21` becomes `03 82 05 21`) and the signature's BIT STRING (`03 41` becomes `03 82 09 75`). Two extra bytes each: **6 bytes**.

18 + 6 = 24. The outer and TBS SEQUENCEs already used the long form in the small certificate, so their headers do not grow. The test file asserts all of these numbers.

The lesson is the one Part 00 announced, now measured to the byte: **X.509 itself is not the problem.** Its skeleton grows by 7%. The post-quantum cost is the key and the signature, and a certificate carries one of each. 96 bytes of cryptography became 3,732. And this is one certificate. A TLS handshake sends a chain, the chain's signatures, and the Certificate Transparency receipts, each signature paying the same 2,420 bytes. Part 02 counts the whole handshake.

<div class="note">

Unlike Ed25519, ML-DSA as used by the library is *hedged*: it mixes fresh randomness into each signature by default, so the signature bytes differ on every run. The size never changes; FIPS 204 signatures have a fixed length for each parameter set. That is why the article quotes the Ed25519 bytes but only the ML-DSA sizes.

</div>

## Try it

On Windows, from the `experiments\root-of-trust` folder (Python 3.10 or newer, `pip install "cryptography>=46"`):

```text
python 01_certificate.py --write
python -m unittest test_01_certificate
```

The first prints everything quoted in this article and writes the three `.der` files. The second runs eight checks: the encoder against known encodings, the strict reader against bad lengths, the byte-for-byte match with the library, every offset quoted above, and the ML-DSA sizes. If you have OpenSSL (Git for Windows ships one in `C:\Program Files\Git\usr\bin`):

```text
openssl asn1parse -inform DER -in 01_example_ed25519.der -i
openssl asn1parse -inform DER -in 01_example_mldsa44.der -i
```

Good exercises, roughly in order of difficulty:

1. Change the site to `bank.example` and predict, before running, which offsets move and by how much.
2. Make the serial number positive *without* the top bit set and confirm the INTEGER shrinks to 16 bytes and every later offset moves by one.
3. Add `keyEncipherment` to the key usage and work out the new BIT STRING by hand before checking it.
4. Feed `der.read()` the bytes `30 81 05` followed by five more bytes. That is valid BER for a 5-byte SEQUENCE. What does our reader say, and why is that the right answer?
5. Add an Authority Key Identifier to the leaf until `openssl verify -x509_strict` accepts it.

## Reader checkpoint

<details>
<summary><strong>1.</strong> The certificate starts with <code>30 82 01 52</code>. Without reading further, how long is the file?</summary>

`30` is a SEQUENCE. `82` says two length bytes follow; `01 52` is 338. With the 4-byte header, the file is 342 bytes.

</details>

<details>
<summary><strong>2.</strong> Why does the serial number's INTEGER have 17 value bytes when the serial is 16 bytes long?</summary>

INTEGERs are two's complement. The serial's first byte `0xAF` has its top bit set, so on its own it would read as negative. A `00` sign byte is added to keep it positive, as RFC 5280 requires.

</details>

<details>
<summary><strong>3.</strong> The basicConstraints extension of a leaf contains <code>30 00</code>. Where did <code>cA = FALSE</code> go?</summary>

`cA` is `BOOLEAN DEFAULT FALSE`, and DER requires fields equal to their default to be omitted. `pathLenConstraint` is optional and absent. Nothing is left, so the SEQUENCE is empty.

</details>

<details>
<summary><strong>4.</strong> What is the difference between <code>A0 03 02 01 02</code> and <code>82 0b 65 78 …</code> in how they use context tags?</summary>

The first is EXPLICIT: `[0]` is a constructed wrapper around a complete INTEGER TLV. The second is IMPLICIT: `[2]` replaces the IA5String's own tag, and the value bytes follow directly. You can only decode the second if you know the schema.

</details>

<details>
<summary><strong>5.</strong> Which bytes does the CA sign, and why must a verifier not re-encode them before checking?</summary>

The TBSCertificate, offsets 4 to 267, header included. A verifier must use the received bytes because a signature is over bytes, not values; if parsing was lenient and re-encoding canonical, a verifier could check different bytes from the ones signed, and two parsers could disagree about one certificate.

</details>

<details>
<summary><strong>6.</strong> The ML-DSA-44 certificate has 24 more bytes of non-cryptographic structure than the Ed25519 one. Account for all 24.</summary>

The algorithm OID appears three times and is 6 bytes longer each time (18), and three lengths (SubjectPublicKeyInfo, key BIT STRING, signature BIT STRING) move from one length byte to the three-byte long form (2 extra bytes each, 6).

</details>

## References

- ITU-T X.680, *ASN.1: Specification of basic notation*, and **X.690**, *ASN.1 encoding rules: BER, CER and DER*: TLV structure (§8.1), INTEGER (§8.3), OBJECT IDENTIFIER (§8.19), DER restrictions (§10, §11), DEFAULT omission (§11.5), named bit lists (§11.2.2), SET OF ordering (§11.6).
- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile*: certificate structure (§4.1), serial numbers (§4.1.2.2), validity and the 2050 rule (§4.1.2.5), extensions and criticality (§4.2), basicConstraints (§4.2.1.9), keyUsage (§4.2.1.3), name comparison (§7.1).
- RFC 8410, *Algorithm Identifiers for Ed25519, Ed448, X25519, and X448*: absent parameters (§3), public keys (§4).
- RFC 9881, *Algorithm Identifiers for the Module-Lattice-Based Digital Signature Algorithm (ML-DSA)* in X.509.
- FIPS 204, *Module-Lattice-Based Digital Signature Standard*: ML-DSA-44 public key 1,312 bytes, signature 2,420 bytes.
- RFC 9525, *Service Identity in TLS*: identifiers are checked against subjectAltName, not the common name.
- CA/Browser Forum, *Baseline Requirements for TLS Server Certificates*: serial number entropy (§7.1) and the schedule of maximum certificate lifetimes.
- M. Marlinspike, *More Tricks for Defeating SSL in Practice*, Black Hat USA 2009 (null-prefix certificates), and his 2002 advisory on Internet Explorer's missing basicConstraints check.
- D. Bleichenbacher, RSA signature forgery for e = 3, CRYPTO 2006 rump session; and [CERT VU#772676](https://kb.cert.org/vuls/id/772676) / [Mozilla bug 1069405](https://bugzilla.mozilla.org/show_bug.cgi?id=1069405), CVE-2014-1568, *BERserk*.
- A. Sotirov, M. Stevens et al., *MD5 considered harmful today: creating a rogue CA certificate*, 2008.
