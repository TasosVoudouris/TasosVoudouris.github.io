---
title: 'Merkle Tree Certificates'
description: 'The design that removes signatures instead of shrinking them. A toy Merkle Tree CA written from draft-ietf-plants-merkle-tree-certs-07 and checked against its encoding example and Appendix C test vectors: log entries that hash the public key, subtrees and how to cover a batch with two of them, cosigned subtrees, the MTCProof inside an X.509 certificate, a relying party that rebuilds the log entry, landmarks, and the handshake bill for every variant.'
part: 7
pubDate: 2026-11-22
tags:
  - merkle-tree-certificates
  - post-quantum
  - transparency-logs
  - x509
  - tls
companion: experiments/root-of-trust
---

Part 06 ended with an inventory. Even the best choice of post-quantum signatures leaves the handshake carrying five signatures and two public keys. Two of those items do real work at connection time: the leaf's public key and its CertificateVerify signature prove that the server holds the key **now**. The other three signatures, the CA's signature on the certificate and the two SCTs, prove facts that were settled once, at issuance: a CA vouched for this binding of name and key, and two logs promised to publish it.

Parts 04 and 05 built machinery that proves facts of that kind without a signature per certificate: a Merkle tree whose state is signed rarely, witnesses who cosign that state after checking it, and inclusion proofs of a few hundred bytes. Merkle Tree Certificates (MTC) put the two together. The CA itself runs a log. Every certificate is an entry in it. And the certificate proves its own legitimacy with an inclusion proof plus a few cosignatures on a part of the tree, or, for up to date clients, with an inclusion proof alone.

This part implements the design from the current IETF draft, [draft-ietf-plants-merkle-tree-certs-07](https://www.ietf.org/archive/id/draft-ietf-plants-merkle-tree-certs-07.html) (October 2026, PLANTS working group; authors Benjamin, O'Brien, Westerbaan, Valenta and Valsorda), as a toy CA and a toy relying party, and then prices every variant with Part 02's handshake framing. It is the most detailed part of the series so far, because the draft is precise and the details are where the savings come from.

By the end you should be able to:

1. draw the issuance flow and say why the log entry exists **before** the certificate;
2. build an MTC log entry from a certificate by hand, and say what it leaves out and why the browser can rebuild it;
3. decide whether an interval of the log is a subtree, and cover any batch of entries with two subtrees, bit by bit;
4. read an MTCProof byte by byte, and say what each cosignature signs;
5. explain landmarks, landmark-relative certificates, and why a bigger subtree gives a smaller certificate;
6. price the handshake for each variant and say honestly where the savings come from.

The code is [`experiments/root-of-trust/07_mtc.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_07_mtc.py`. It uses Part 04's Merkle tree and Part 01's DER encoder, and ML-DSA-44 from `cryptography` for every signature. Section numbers below (§) refer to draft -07. The draft is a working document and details may change before it becomes an RFC.

## The idea in one picture

<img src="/images/root/07-flow.svg" alt="The subscriber asks the CA. The CA validates the request, appends an entry to its own log, and signs subtrees of the log as a cosigner. Witnesses fetch the entries, check the subtree and cosign it. Only then does the CA build the certificate: TBSCertificate, inclusion proof to a subtree, cosignatures. The server sends it in the TLS handshake; the browser rebuilds the entry and checks proof and cosignatures. Landmarks reach the browser through an update channel." width="1000" height="640" loading="lazy" />

In Certificate Transparency (Part 03), the CA signs a certificate, then submits it to independent logs, which return signed promises (SCTs) to include it later. The log is bolted on after the fact, and every certificate carries three signatures from three parties to prove it happened.

In MTC the order is reversed (§3):

1. The CA validates the request as it always has.
2. The CA **appends** an entry describing the certificate to its own **issuance log**. Each CA has its own tree; there is no shared log of all CAs.
3. The CA periodically signs the state of the log, and signs **subtrees** covering the newly added entries. Here the CA acts as a **cosigner**, with a key used for nothing else. Other cosigners, **witnesses** in the sense of Part 05, fetch the same entries, check that the subtree really is part of the log they have seen grow consistently, and add their own cosignatures.
4. Only now can the certificate exist: it is the TBSCertificate, an inclusion proof from its entry to a subtree, and the cosignatures on that subtree. This is a **standalone certificate** (§6.3).
5. Later, some subtrees become **landmarks**, distributed ahead of time to browsers. A certificate that proves inclusion in a landmark subtree needs **no signatures at all**: a **landmark-relative certificate** (§6.4).

The participants have draft names. The **authenticating party** is the server presenting the certificate, the **relying party** is the browser checking it, the **cosigners** are the CA's own cosigner plus witnesses (and optionally mirrors, which keep copies of the log). Everything below is one of these roles doing one step of that list.

## Names first: trust anchor IDs

MTC identifies the CA, its logs and its cosigners by **trust anchor IDs**: object identifiers written relative to a fixed arc. The draft's examples use 32473, the arc RFC 5612 reserves for documentation, and so does the code:

| thing | ID | where it appears |
|---|---|---|
| CA | `32473.1` | the certificate's issuer name; the CA's own cosigner |
| issuance log number 1 | `32473.1.0.1` | the log origin, inside every cosigned message |
| witness A, witness B | `32473.2`, `32473.3` | cosignatures in the MTCProof |

A log ID is the CA ID followed by `0` and a log number from 1 to 65,535, and a log may hold up to 2<sup>48</sup> − 1 entries. Where a text name is needed, in signed notes and cosigned messages, an ID becomes an origin string with the prefix `oid/1.3.6.1.4.1.`, so the log above is `oid/1.3.6.1.4.1.32473.1.0.1`.

In binary, an ID is a DER **RELATIVE-OID**: each arc in base 128, seven bits per byte, the top bit set on every byte except an arc's last. Work out 32473.1 by hand:

```text
32473 = 1·128² + 125·128 + 89      ->  0x81  0xFD  0x59   (top bits 1, 1, 0)
1                                  ->  0x01
RELATIVE-OID tag 0x0D, length 4    ->  0d 04 81 fd 59 01
```

That is exactly the draft's example value for the issuer attribute, and the first line the script prints:

```text
== encodings checked against the draft ==
  CA ID 32473.1 as an issuer attribute value: 0d0481fd5901  (draft: 0d0481fd5901)
  log origin: oid/1.3.6.1.4.1.32473.1.0.1
```

The issuer of an MTC is a distinguished name with one attribute, of type id-rdna-trustAnchorID (1.3.6.1.5.5.7.25.3), whose value is that RELATIVE-OID (§6.2). This is the first deployment surprise the code found. The Python `cryptography` library parses the certificate, serial and algorithm without complaint, but refuses to decode the issuer:

```text
  `cryptography` refuses to decode the issuer: its attribute value is a RELATIVE-OID (tag 0x0D),
  which today's X.509 stacks do not expect. MTC needs parser updates, not only new trust stores.
```

Nothing is wrong with the certificate. Name attribute values have in practice always been strings, and parsers were written for strings. A relying party that wants MTC needs a parser change, which is a reminder that "it is still X.509" does not mean "existing code accepts it".

## The log entry

<img src="/images/root/07-entry.svg" alt="Left, the TBSCertificate fields and their sizes in the toy: version 5, serial 9, signature algorithm 12, issuer 22, validity 32, subject 26, subject public key info 1,334, extensions 51. The serial and signature algorithm are not logged. Right, the TBSCertificateLogEntry: version, issuer, validity, subject, the public key's algorithm (13 bytes) and its SHA-256 hash (34 bytes), extensions. The log entry is 187 bytes." width="1000" height="620" loading="lazy" />

What exactly goes into the tree? Not the certificate. The leaf is an **MTCLogEntry** (§5.2), shown here simplified:

```text
struct {
    Extension      extensions<0..2^16-1>;   // 2-byte length, empty today
    MTCLogEntryType type;                   // uint16: null_entry(0), tbs_cert_entry(1)
    select (type) {
        case null_entry:     Empty;
        case tbs_cert_entry: opaque tbs_cert_entry_data[N];
    };
} MTCLogEntry;
```

The data is the **contents octets** (the DER value without its outer tag and length) of a `TBSCertificateLogEntry`, an ASN.1 structure that mirrors the TBSCertificate with three differences:

1. **No serial number.** The serial of an MTC is the entry's position in the log, `(log_number << 48) | index`. Logging it would be logging the index inside the entry at that index.
2. **No signature algorithm.** In an MTC that field always names the proof algorithm, so it carries no information.
3. **No public key.** The SubjectPublicKeyInfo is replaced by two fields: `subjectPublicKeyAlgorithm`, the key's AlgorithmIdentifier, and `subjectPublicKeyInfoHash`, the SHA-256 of the whole DER SubjectPublicKeyInfo.

The third difference matters most for post-quantum keys. In the toy, the subject key is ML-DSA-44, 1,312 bytes of key in a 1,334-byte SubjectPublicKeyInfo. In the log it costs 13 + 34 bytes. The script prints the result:

```text
  its log entry: 187 bytes (the public key is a 32-byte hash, and there is no signature)
```

The draft caps an entry at 65,535 bytes. Hashing the key keeps every entry small whatever the subscriber's algorithm is, so the log, its mirrors and its witnesses store and serve a few hundred bytes per certificate, and nobody needs the key itself to audit what the CA issued: the hash commits to it, and the full key travels in the certificate, where the server needs it anyway to be checked against its CertificateVerify.

The first four bytes of every certificate entry are therefore fixed:

```text
00 00     extensions: length 0
00 01     type: tbs_cert_entry
...       contents of the TBSCertificateLogEntry DER
```

and the leaf hash is Part 04's, `SHA-256(0x00 || MTCLogEntry)`. The test `test_log_entry_hides_the_key` checks that the full SubjectPublicKeyInfo does not occur in the entry, that its hash does, and that the prefix is `00 00 00 01`.

Two remarks. First, the type field also allows a **null entry**, which carries no certificate; the draft lets any index hold one. The toy log starts with a null entry at index 0, so no toy certificate has index zero. Second, and this is the important property, the browser can rebuild the entry. Everything in it is either in the certificate (issuer, validity, subject, extensions) or computable from it (the key's algorithm and hash). That is what lets a certificate prove its own inclusion: the relying party recomputes the leaf, and only needs the path.

## Subtrees

In Part 04, inclusion proofs went from a leaf to the root of the whole tree. MTC proves inclusion in a **subtree**: a contiguous range `[start, end)` of entries that is itself a node of the tree (§4). The CA cannot sign a new root every time a certificate is added, but it can sign the subtree covering the latest batch, and that signature never needs to change.

**Which ranges are subtrees?** Part 04 split a tree of size n at the largest power of two smaller than n, and the nodes that split produces are exactly the ranges that satisfy one rule (§4.1):

> `[start, end)` is a valid subtree if `start` is a multiple of `BIT_CEIL(end − start)`,

where BIT_CEIL(n) is the smallest power of two at least n. Some examples from this part:

| range | size | BIT_CEIL | start a multiple? | valid |
|---|---|---|---|---|
| `[992, 1024)` | 32 | 32 | 992 = 31 · 32 | yes |
| `[1024, 1037)` | 13 | 16 | 1024 = 64 · 16 | yes |
| `[0, 1024)` | 1024 | 1024 | 0 | yes |
| `[1000, 1037)` | 37 | 64 | 1000 = 15 · 64 + 40 | **no** |

Notice that `[1024, 1037)` is valid even though 13 is not a power of two: it is a node on the right edge of a tree that is still growing, the same "unbalanced right spine" Part 04 drew for trees whose size is not a power of two.

**Covering a batch.** The last row is the realistic case: the CA has just added entries 1,000 to 1,036, and that range is not a node. §4.5 gives an algorithm for the **two** subtrees that cover any range, where the left one may start a little early. Run it by hand on `[1000, 1037)`:

```text
start = 1000 = 0b011_1110_1000
last  = 1036 = 0b100_0000_1100        (end - 1)

split = highest bit where start and last differ          = bit 10
mid   = last with its low 10 bits cleared                = 1024

low 10 bits of start:  11 1110 1000
highest ZERO bit among them                               = bit 4
left_split = 4 + 1 = 5
left_start = start with its low 5 bits cleared            = 992

covering subtrees: [992, 1024) and [1024, 1037)
```

The idea: `mid` is the point where the binary trees containing `start` and `last` part ways, so `[mid, end)` is a node on the right. On the left, the entries from `start` up to `mid` would need many small nodes; instead, round `start` down just far enough that `[left_start, mid)` is one node. Entries 992 to 999 were in an earlier batch, which is harmless: their certificates already exist, and they just happen to be provable in this subtree too.

Three properties make this a good design, and the script checks all of them for every range with end at most 260: both outputs are valid subtrees, together they cover the range, the right one ends exactly at `end`, and neither is larger than BIT_CEIL of the range size, so a batch of n entries never needs a proof longer than about log<sub>2</sub> n hashes.

```text
  covering subtrees for every 0 <= start < end <= 260: valid, covering, right ends at end, sizes <= BIT_CEIL: all ok
  draft Appendix C.1.1 subtree hashes: b82806ad4265bb15...  matches
  draft Appendix C.1.4 covering subtrees: 7fd9c8b926e9d2b5...  matches
```

The last two lines are the draft's own test vectors (Appendix C.1). For a tree whose leaves are the single bytes 0x00, 0x01, ..., the draft feeds one text line per result into a running SHA-256, for every `0 ≤ start ≤ end ≤ 130`: for C.1.1 the line `[start, end) HASH` for every valid subtree, for C.1.4 the line `[left_start, left_end) [right_start, right_end)` for every range. Both final hashes match. The tests also check the large examples of Appendix C.2: subtree validity near 2<sup>47</sup>, 2<sup>48</sup>, 2<sup>63</sup> and 2<sup>64</sup>, and covering ranges such as `[0x500000000000, 0xd00000000000)`, whose subtrees are `[0x400000000000, 0x800000000000)` and `[0x800000000000, 0xd00000000000)`.

**Subtree inclusion proofs** (§4.3) are Part 04's inclusion proofs, applied inside the subtree: the leaf index becomes `index − start` and the tree size `end − start`. One change in how they are used: instead of comparing the result to a known root, the verifier **evaluates** the proof and returns the hash it arrives at. The code's `_evaluate` is RFC 9162's verification loop with the final comparison removed. The relying party then asks a separate question: is that hash something I trust? A proof for a subtree of size n has at most ⌈log<sub>2</sub> n⌉ hashes: five for `[992, 1024)`, ten for `[0, 1024)`.

Part 04 found that its proof checker accepted a proof for the wrong tree size if the caller passed the wrong size, because nothing bound the size. Here the size is bound: `start` and `end` are inside the cosigned message, so a proof evaluated with any other range produces a hash nobody signed.

## Cosigning a subtree

What does a cosigner actually sign? A **CosignedSubtree** message (§5.3.1):

```text
"subtree/v1\n\0"            12 bytes, a fixed label
cosigner_name<1..255>       e.g. "oid/1.3.6.1.4.1.32473.2"
uint64 timestamp            zero in certificates
log_origin<1..255>          "oid/1.3.6.1.4.1.32473.1.0.1"
uint64 start
uint64 end
subtree_hash[32]
```

It names the signer, the log, the exact range and its hash. The construction is compatible with the C2SP tlog-cosignature format from Part 05, so a witness that already cosigns checkpoints can cosign subtrees with the same machinery. The draft does not mandate an algorithm; the toy uses ML-DSA-44, so every cosignature is 2,420 bytes.

Before signing, a cosigner must convince itself the subtree is real: that it is part of a log it has seen grow consistently, the same split view question as Part 05. The toy witness keeps its own copy of the entries and refuses if the claimed hash differs. The attack section of the script swaps an entry after a witness fetched the log, then asks for a cosignature:

```text
  CA swaps an entry, asks witness  -> witness refuses: oid/1.3.6.1.4.1.32473.2: subtree [1, 2) does not match my view of the log
```

The CA is also a cosigner, under its CA ID, and the draft says a CA cosigner key must not be used to sign TBSCertificate structures directly. That separation keeps an MTC CA key from ever producing an ordinary X.509 signature that a classic relying party might accept.

The whole issuance step in the script:

```text
== issuance: the CA logs first, then cosigns, then builds certificates ==
  37 new entries [1000, 1037) covered by subtrees [(992, 1024), (1024, 1037)]
  each subtree cosigned by the CA and 2 witnesses (ML-DSA-44), 37 certificates built
```

Six signatures cover 37 certificates. In the real proposal, a checkpoint every couple of seconds makes each batch thousands of certificates, and the signing load per certificate becomes negligible.

## The certificate

An MTC is an ordinary-looking X.509 certificate (§6.2):

| field | value in the toy |
|---|---|
| version | v3 |
| serialNumber | `(1 << 48) \| 1005` = 0x10000000003ED: log 1, entry 1,005 |
| signature (algorithm) | id-alg-mtcProof, 1.3.6.1.5.5.7.6.67, parameters absent |
| issuer | trustAnchorID = 32473.1 |
| validity, subject, subjectPublicKeyInfo, extensions | as in any certificate |
| signatureAlgorithm | id-alg-mtcProof again |
| signatureValue | a BIT STRING containing an **MTCProof** |

The signature is not a signature. The BIT STRING holds:

```text
struct {
    Extension   extensions<0..2^16-1>;       //  2 bytes when empty
    uint48      start;                       //  6
    uint48      end;                         //  6
    opaque      inclusion_proof<0..2^16-1>;  //  2 + 32 per hash
    Cosignature signatures<0..2^24-1>;       //  3 + the cosignatures
} MTCProof;

struct {
    TrustAnchorID cosigner_id;               //  1 + the binary relative OID
    opaque        signature<0..2^16-1>;      //  2 + the signature
} Cosignature;
```

Cosignatures are sorted, shorter IDs first and then lexicographically, and IDs must be unique. The parser rejects unsorted lists, duplicates, and any byte after the end of the structure.

<img src="/images/root/07-proof.svg" alt="A standalone certificate of 8,976 bytes: TBSCertificate 1,495 bytes, of which the public key is 1,334, and a 7,465-byte signatureValue holding the MTCProof. The MTCProof breaks down into 179 bytes of extensions, start, end, five proof hashes and length, and three cosignatures of 2,427 bytes each from the CA and two witnesses. A landmark-relative certificate keeps the same TBSCertificate and an MTCProof of 339 bytes." width="1000" height="600" loading="lazy" />

Byte for byte, the standalone certificate for entry 1,005:

```text
outer SEQUENCE header                         4
TBSCertificate                            1,495   (1,334 of them the subject key)
signatureAlgorithm                           12
signatureValue: BIT STRING header + 0x00      5
  MTCProof
    extensions                                2
    start, end                               12
    inclusion proof: 2 + 5 × 32             162
    signatures length                         3
    3 × (1 + 4 + 2 + 2,420)               7,281
total                                     8,976
```

The Merkle machinery costs 179 bytes. The three ML-DSA-44 cosignatures cost 7,281. Keep that ratio in mind for the bill.

## Verifying it

The relying party's procedure (§7.2), in the order the code does it:

1. Check that both algorithm fields are id-alg-mtcProof, and parse the MTCProof with no trailing data.
2. Split the serial into `log_number = serial >> 48` (must not be zero) and `index`, the low 48 bits. The serial is also where revocation applies: the draft revokes by **ranges of indices** (§7.5), which is far more compact than lists of serials.
3. **Rebuild the log entry** from the TBSCertificate, replacing the public key by its algorithm and hash, and compute its leaf hash.
4. Check that `[start, end)` is a valid subtree containing `index`, and **evaluate** the inclusion proof to get a subtree hash.
5. If that subtree is one the relying party already trusts (a landmark), compare the hashes and stop.
6. Otherwise, verify cosignatures on the CosignedSubtree for that range and hash, with timestamp zero, and apply policy.

The policy (§7.3) is the relying party's to set. The draft recommends requiring the CA's own cosigner and a quorum of other cosigners. In Part 05's terms: the CA promises the entry is in its log, and witnesses promise they saw the same log, so a CA that shows one subtree to the browser and another to the world needs witnesses to lie with it.

The script's attacks:

```text
== a standalone certificate ==
  ACCEPT: entry 1005 in subtree [992, 1024), CA + 2 witness cosignature(s)

== attacks on the relying party ==
  certificate for another name     -> REJECT: InvalidSignature: the proof now leads to a subtree hash nobody cosigned
  no witness, quorum 1             -> REJECT: ValueError: only 0 witness cosignature(s), need 1
  same certificate, policy quorum 2 -> ACCEPT: entry 1005 in subtree [992, 1024), CA + 2 witness cosignature(s)
  CA swaps an entry, asks witness  -> witness refuses: ...
```

The first line is the whole security argument in miniature. Changing one byte of the subject changes the rebuilt entry, so the leaf hash, so the evaluated subtree hash, and no cosigner ever signed that hash. There is no signature over the certificate itself; there does not need to be.

## Landmarks

<img src="/images/root/07-landmarks.svg" alt="Top, the whole log to tree size 1,037, covered by landmark subtree [0, 1024), whose hash the browser already holds. Bottom, a zoom on entries 960 to 1,040: the new batch 1,000 to 1,037 is covered by standalone subtrees [992, 1024) and [1024, 1037), cosigned right away. Entry 1,005 lies in both [992, 1024) and the landmark subtree [0, 1024). Standalone: 5 hashes and 3 cosignatures, 7,465 bytes. Landmark-relative: 10 hashes and no signatures, 344 bytes." width="1000" height="600" loading="lazy" />

Cosignatures are what cost the bytes, and they exist only to tell the relying party "this subtree hash is real". If the browser already knew the hash, they would be unnecessary. That is a **landmark** (§6.4).

Periodically, the CA designates its current tree size as a landmark. Landmark zero is tree size zero, and landmark L covers the entries between the previous landmark and its own size, with the two covering subtrees of that range. Those **landmark subtrees** are predistributed to relying parties as trusted subtrees (§7.4), through some update channel. The draft deliberately does not prescribe the channel, and mentions Chromium's component updater and Firefox Remote Settings as examples.

The browser does not take them on faith. Before trusting a landmark it must check that the subtrees are consistent with checkpoints that enough cosigners have signed: a reference checkpoint at least as large as the landmark, cosignatures or consistency proofs from the cosigners, and a subtree consistency proof for each subtree. If one landmark fails, the browser can drop it and every newer one in that log, keeping the older ones. That consistency machinery is the subject of Part 08.

How much state is that? The draft works an example (§6.4.2): with a maximum certificate lifetime of 7 days and a landmark every hour, at most ⌈168 / 1⌉ + 1 = 169 landmarks are active, so 338 subtrees, so 338 × 32 = **10,816 bytes** per CA. A browser can hold that for every CA it trusts.

A **landmark-relative certificate** is the same certificate with a different MTCProof: an inclusion proof to the landmark subtree containing the entry, and an empty signature list (§6.4.4). Anyone holding a standalone certificate can build it, by fetching the landmark and the proof hashes from the log. In the toy, landmark 1 is at tree size 1,037, covered by `[0, 1024)` and `[1024, 1037)`:

```text
== a landmark-relative certificate: no signatures ==
  landmark 1 at tree size 1037, subtrees [(0, 1024), (1024, 1037)]
  ACCEPT: entry 1005 in landmark subtree [0, 1024), no signature checked
  1,855 bytes: subtree [0, 1024), 10 proof hashes, 0 signatures
  the same certificate, relying party without the landmark -> REJECT: no valid CA cosignature
```

The proof is **longer** (ten hashes against five, because the subtree is 32 times bigger) and the certificate is almost **five times smaller**, because three 2,420-byte signatures are gone. The MTCProof is 339 bytes. Of the 1,855, most is the subscriber's own public key.

The price is time and freshness. A landmark-relative certificate cannot exist until the next landmark includes the entry, and it is only useful to a browser that has received that landmark. The draft is explicit that these certificates only work in a sufficiently up to date relying party, and that the server should also have a standalone certificate as a fallback.

## Choosing in TLS

So a server holds two certificates for the same key, and must send the right one (§8). This rides on TLS trust anchor negotiation: a landmark-relative certificate is identified by a trust anchor ID derived from the CA ID and the landmark, and a client signals which landmarks it holds. The server should not send a landmark-relative certificate unless the client signalled that it can verify it, and should prefer it when it can. A browser fresh out of an update gets the small certificate; one that has been offline for a week gets the standalone one, and still connects.

## The bill

<img src="/images/root/07-bill.svg" alt="Authentication bytes in the TLS handshake with ML-DSA-44 everywhere: X.509 with two SCTs and an intermediate 15,271; the same without the intermediate 11,353; MTC standalone with the CA and two witnesses 11,417; with the CA and one witness 8,990; landmark-relative 4,296." width="1000" height="560" loading="lazy" />

Now price it with Part 02's framing: the Certificate message plus a CertificateVerify, which is an ML-DSA-44 signature (2,420 bytes) in every row, because the server must still prove possession of its key. The classic rows use the same subject and key, a lean ML-DSA-44 CA and two ML-DSA-44 SCTs.

```text
== the handshake bill (Part 02's framing; CertificateVerify is ML-DSA-44 in every row) ==
  X.509 + 2 SCTs + intermediate, ML-DSA-44          15,271 B   server flight ~ 16,638 B
  X.509 + 2 SCTs, leaf only (intermediate cached)   11,353 B   server flight ~ 12,720 B
  MTC standalone: CA + 2 witnesses                  11,417 B   server flight ~ 12,784 B
  MTC standalone: CA + 1 witness                     8,990 B   server flight ~ 10,357 B
  MTC landmark-relative                              4,296 B   server flight ~  5,663 B
  (classic leaf 8,912 B, intermediate 3,913 B; MTC standalone 8,976 B; landmark-relative 1,855 B)
  at the draft's §6.5 scale (12 hashes standalone, 23 landmark-relative): standalone 11,641 B, landmark-relative 4,712 B
```

The toy's certificates are leaner than the real ones of Part 02, whose ML-DSA chain came to 15,802 bytes, so compare rows within this table rather than with Part 02's absolute numbers. Read the table honestly:

**A standalone MTC is not much smaller than a classic leaf.** With the CA and two witnesses, it carries three ML-DSA-44 signatures, exactly as many as a classic certificate with two SCTs, and lands within 64 bytes of it. What it does remove is the **intermediate certificate**: the CA's key and the root's signature on it, 3,913 bytes in the toy, because the browser trusts the CA's cosigner key directly. Against a classic chain that sends its intermediate, a standalone MTC saves about 3.9 KB. Against a client that already caches intermediates, it saves nothing. Require one witness instead of two and it saves another 2.4 KB, at a cost in trust.

**The landmark-relative certificate is the real win.** 4,296 bytes of authentication against 15,271: about 28 percent. Its server flight, around 5.7 KB, fits the roughly 7.2 KB budget for a QUIC server's first flight from Part 06, and comfortably inside TCP's 14,600-byte initial window. The classic chain with an intermediate does not even fit the TCP window. At the scale the draft estimates (§6.5: a checkpoint every 2 seconds gives subtrees of about 3,000 certificates and 12 proof hashes; a landmark every hour gives subtrees of about 5.4 million certificates and 23 hashes, or 736 bytes) the conclusions stand: 11,641 against 4,712 bytes.

The draft makes the same point in its own terms. Its introduction counts 7,260 bytes of authentication overhead for two SCTs and the signature on the leaf certificate with ML-DSA-44, and its size section notes that 736 bytes of landmark proof are much smaller than one ML-DSA-44 signature and nearly ten times smaller than the three that post-quantum SCTs require. Part 06's limit was that no signature choice removes items. Landmarks remove three.

What is left in the landmark-relative handshake is the irreducible part: the server's public key (1,312 bytes for ML-DSA-44), its CertificateVerify signature (2,420), a few hundred bytes of names and structure, and the proof. Shrinking those further is again a question of signature schemes, and Part 06's menu applies to the leaf alone.

## What changes besides size

**Transparency is built in.** Every certificate is in its CA's log before it exists, so there is no window between issuance and logging, and no SCT to forge or to fail to honour. Monitoring changes shape: instead of many shared CT logs, each CA has its own logs, and witnesses and mirrors keep the CA honest.

**Revocation by range.** Since serials are log positions, a relying party can revoke "entries 5,000,000 to 5,000,999 of log 1" in a few bytes (§7.5). A bad batch is one range.

**Short lifetimes are cheap.** The sizing example assumes 7-day certificates. Renewal is just another log entry; the draft estimates about 5.4 million certificates per hour for one large CA under that assumption, which the log absorbs as a few thousand entries per checkpoint.

**New dependencies.** Browsers need landmark distribution and must verify landmark consistency before trusting them; servers must hold and choose between two certificates; X.509 parsers must accept the new issuer encoding; CAs must run logs that witnesses can follow. None of this is small, which is why the design keeps the standalone certificate as a path that works everywhere the trust anchor is known.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 07_mtc.py
python -m unittest test_07_mtc
```

The first prints everything quoted in this article. The ML-DSA signatures are randomized, but their sizes are fixed, so every number should match. The tests check the draft's encoding example and Appendix C vectors, the covering subtrees, every certificate of the batch, the rejections, and every size in the bill.

Exercises:

1. Run `covering_subtrees` by hand on `[5, 13)` and `[64, 65)`, then check with the code. Why does a single entry get the pair `[start, start + 1)` and the empty `[end, end)`?
2. Make the CA's batch 3,000 entries, as at real scale. How many proof hashes does a standalone certificate need, and how does the certificate size change?
3. Add a third witness and a policy that requires the CA plus any two of three. What does each extra cosignature cost, and what does Part 05's quorum rule say about how many witnesses a split view must corrupt?
4. Give the relying party a landmark whose subtree hash is wrong (as `test_landmark_relative` does) and follow which step rejects it. Then think about why §7.4 requires checking landmarks against cosigned checkpoints before trusting them.
5. Replace ML-DSA-44 for the cosigners by a scheme from Part 06's menu with small signatures and large keys (cosigner keys sit in the browser, like CT log keys). Rerun the bill for standalone certificates.
6. Revoke a range of indices in the relying party, and make it reject certificate 1,005 while still accepting 1,006.

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why can the log entry leave out the public key, and how does the browser still check it?</summary>

The entry stores the SHA-256 of the SubjectPublicKeyInfo, which commits to the key. The browser gets the full key in the certificate, hashes it, rebuilds the entry, and checks the inclusion proof; any other key gives another hash, another leaf, and a proof to a subtree nobody signed.

</details>

<details>
<summary><strong>2.</strong> Is [24, 32) a subtree? [24, 40)? [32, 45)?</summary>

[24, 32): size 8, BIT_CEIL 8, 24 is a multiple of 8, yes. [24, 40): size 16, 24 is not a multiple of 16, no. [32, 45): size 13, BIT_CEIL 16, 32 is a multiple of 16, yes.

</details>

<details>
<summary><strong>3.</strong> Why can the left covering subtree start before the batch, and why is that harmless?</summary>

Rounding the start down makes the left range a single node, so the proof stays short. The extra entries belong to earlier batches whose certificates already exist; proving them in one more subtree changes nothing about them.

</details>

<details>
<summary><strong>4.</strong> What does a cosigner sign, and why are start and end inside it?</summary>

A CosignedSubtree: a fixed label, its own name, a timestamp (zero in certificates), the log origin, start, end and the subtree hash. Binding the range means a proof evaluated over any other range yields a message nobody signed, which closes the wrong-size gap Part 04 found.

</details>

<details>
<summary><strong>5.</strong> A landmark-relative proof has more hashes than the standalone one, yet the certificate is five times smaller. Why?</summary>

Landmark subtrees are much larger, so the path is longer, by about 32 bytes per doubling. But the browser already trusts the landmark's hash, so the three 2,420-byte cosignatures are unnecessary. Hashes are cheap; post-quantum signatures are not.

</details>

<details>
<summary><strong>6.</strong> Against which classic deployment does a standalone MTC save almost nothing, and what does it still remove?</summary>

Against a classic leaf whose intermediate the client already caches: both carry three ML-DSA-44 signatures, and the sizes are within 64 bytes. It still removes the intermediate certificate (3.9 KB in the toy) for clients that would otherwise receive it, and it builds logging into issuance.

</details>

## What comes next

This part trusted landmarks it was handed and checked cosignatures on subtrees it was shown. [Part 08](/root/08-landmarks-you-can-check/) opens that box: subtree consistency proofs, how a browser verifies that a landmark belongs to the log every witness saw, how many landmarks to keep, and what happens to a client that falls behind.

## References

- D. Benjamin, D. O'Brien, B. E. Westerbaan, L. Valenta and F. Valsorda, [*Merkle Tree Certificates*](https://www.ietf.org/archive/id/draft-ietf-plants-merkle-tree-certs-07.html), draft-ietf-plants-merkle-tree-certs-07, IETF PLANTS working group, October 2026. Sections 3 to 8 and Appendix C are the basis of this part.
- B. Laurie, E. Messeri and R. Stradling, RFC 9162, *Certificate Transparency Version 2.0*, 2021: the inclusion proof verification that MTC evaluates.
- [C2SP tlog-cosignature](https://c2sp.org/tlog-cosignature) and [tlog-witness](https://c2sp.org/tlog-witness): the cosignature format MTC's CosignedSubtree is compatible with (see Part 05).
- RFC 5612, *Enterprise Number for Documentation Use*: the arc 32473 used in all examples.
- NIST, FIPS 204, *Module-Lattice-Based Digital Signature Standard*, August 2024: ML-DSA-44, used for every signature here.
