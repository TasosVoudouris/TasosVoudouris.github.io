---
title: 'The handshake bill'
description: 'Where certificates travel in a TLS 1.3 handshake and what every byte costs. Real chains with real SCTs, live handshakes through OpenSSL, the Certificate message encoded by hand and matched byte for byte, and the moment post-quantum signatures push the server past the first round trip.'
part: 2
pubDate: 2026-11-19
tags:
  - tls
  - certificates
  - certificate-transparency
  - post-quantum
  - ml-dsa
  - ml-kem
companion: experiments/root-of-trust
---

Part 00 ended with a back-of-the-envelope bill: a leaf public key and three signatures, 224 bytes with Ed25519 and 8,572 bytes with ML-DSA-44. Part 01 showed what one of those certificates really is, byte by byte. This part puts the certificates where they actually live, inside a **TLS 1.3 handshake**, and measures the whole bill instead of estimating it.

No estimates means real handshakes. The companion script builds three realistic certificate chains (root, intermediate, leaf, with two real Certificate Transparency receipts in the leaf), runs actual TLS 1.3 handshakes between a client and a server through OpenSSL, and captures every handshake message as it is written. Next to that, it encodes the same messages by hand from the RFC. The two agree **byte for byte**, for every chain and every configuration, so every number below is both measured and explained.

By the end you should be able to:

1. draw a TLS 1.3 handshake from memory and point to the two messages that carry authentication;
2. read the Certificate message's framing and say what each length prefix covers;
3. count the signatures and public keys a browser receives for one site, and say who made each one and when;
4. explain why a few extra kilobytes can cost a whole round trip, over TCP and over QUIC;
5. say which proposed fixes help (and how much), and which bytes no fix inside today's design can remove.

The code is in [`experiments/root-of-trust/`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust): `02_handshake.py` and its tests, `test_02_handshake.py`.

## One round trip

A TLS 1.3 handshake (RFC 8446, republished with clarifications as RFC 9846) does two jobs in one round trip: it agrees on fresh keys, and it proves to the client that it is talking to the right server.

<figure class="plate">
<img src="/images/root/02-handshake.svg" alt="Sequence diagram. Client sends ClientHello with key shares. Server answers in one flight: ServerHello with its key share, then encrypted EncryptedExtensions, Certificate, CertificateVerify and Finished. Certificate and CertificateVerify are highlighted as the authentication bytes. Client answers with Finished, then application data flows both ways." width="1000" height="700" loading="lazy" />
<figcaption>The full TLS 1.3 handshake. The highlighted messages are what this part is about.</figcaption>
</figure>

Step by step:

**ClientHello.** The client lists what it supports (cipher suites, signature algorithms, groups for key exchange) and, to save a round trip, already sends **key shares**: its half of a key exchange for the group it guesses the server will pick.

**ServerHello.** The server picks the parameters and sends its own key share. From this moment both sides can compute a shared secret, so **everything after ServerHello is encrypted** (the braces `{ }` in the figure). An eavesdropper sees that a handshake happened, but not which certificates were sent.

**EncryptedExtensions.** Small: the rest of the server's choices that do not need to be in the clear, like the application protocol.

**Certificate.** The server's certificate chain. This is where Parts 00 and 01 live.

**CertificateVerify.** A signature, made right now with the leaf certificate's private key, over a hash of everything said so far. The certificate says "this key belongs to example.com"; this signature proves "and I hold that key". Without it, anyone could replay a public certificate.

**Finished.** A MAC over the whole transcript with a key derived from the shared secret, so both sides know nobody tampered with any message.

The server sends ServerHello through Finished as **one flight**, without waiting for anything. That is the whole point of TLS 1.3's design, and it is also the source of the problem in this part. The client checks everything, sends its own Finished, and can send its first request together with it.

## Two migrations, one already done

Post-quantum TLS has two separate halves, and they are moving at very different speeds.

**Key exchange is already post-quantum** for most of the web. Browsers and servers use a *hybrid*, X25519MLKEM768: a classical X25519 exchange and an ML-KEM-768 encapsulation together, so the connection is safe if either one holds. The reason for hurrying is *harvest now, decrypt later*: traffic recorded today could be decrypted by a future quantum computer, so the key exchange must be quantum-safe before such a computer exists. More than half of the human web traffic that Cloudflare sees already uses it; the share passed 50% in late 2025.

The OpenSSL 3.5 in our experiment uses it by default, so we can see the cost directly from the captured messages:

| | X25519 only | X25519MLKEM768 (hybrid) |
|---|---:|---:|
| client key share | 32 B | 1,216 B (1,184 ML-KEM + 32 X25519) |
| ClientHello total | 232 B | 1,466 B |
| server key share | 32 B | 1,120 B (1,088 ML-KEM ciphertext + 32) |
| ServerHello total | 122 B | 1,210 B |

By default OpenSSL sends **two** key shares, the hybrid one and a plain X25519 one, so that a server that does not speak ML-KEM yet can still finish in one round trip. That is the extra 32 bytes in the ClientHello.

**Authentication is not post-quantum yet.** Signatures only need to be unforgeable at the moment they are checked: a quantum computer built in 2035 cannot go back and fake a handshake from 2026. So there is less urgency, but much more work, because changing signatures means changing every CA, every certificate, every log, and every client's trust store. And, as we will now measure, the bytes are far worse.

## The Certificate message, by hand

RFC 8446 §4.4.2 defines the message in TLS's own notation:

```text
struct {
    opaque cert_data<1..2^24-1>;
    Extension extensions<0..2^16-1>;
} CertificateEntry;

struct {
    opaque certificate_request_context<0..2^8-1>;
    CertificateEntry certificate_list<0..2^24-1>;
} Certificate;
```

TLS's encoding is much simpler than DER. There are no tags: the structure is fixed by the specification, and the only thing on the wire is the data plus **length prefixes**. `<0..2^8-1>` means "a byte string preceded by a 1-byte length", `<0..2^16-1>` a 2-byte length, `<1..2^24-1>` a 3-byte length; the prefix is always just wide enough for the maximum. Every handshake message also gets a 4-byte header: one byte of message type (11 for Certificate) and a 3-byte length.

So the whole encoder is a few lines:

```python
def vec8(b):  return u8(len(b)) + b
def vec16(b): return u16(len(b)) + b
def vec24(b): return u24(len(b)) + b

def certificate_message(chain_der):
    entries = b"".join(vec24(cert) + vec16(b"") for cert in chain_der)
    return u8(11) + vec24(vec8(b"") + vec24(entries))
```

<figure class="plate">
<img src="/images/root/02-certificate-message.svg" alt="The ML-DSA-44 Certificate message, 13,374 bytes: header 0b 00 34 3a, empty context 00, list length 00 34 36, then 00 23 96 and the 9,110-byte leaf, 00 00 for no extensions, then 00 10 96 and the 4,246-byte intermediate and 00 00. The root, 4,066 bytes, is not sent." width="1000" height="470" loading="lazy" />
<figcaption>The ML-DSA-44 chain as it went over the wire. Eighteen bytes of framing, the rest is certificates.</figcaption>
</figure>

Three things in this message are worth pausing on.

**The order is fixed.** The leaf comes first, then each certificate that certifies the one before it. The client builds the path from there.

**The root is not sent.** The client already holds the roots it trusts; a root the server sends proves nothing, because anyone can make a self-signed certificate. Sending it would only waste bytes (4,066 of them, in the ML-DSA-44 case).

**Each entry has an extensions block.** It is empty here, but this is where a server can attach an OCSP response or SCTs delivered through TLS instead of inside the certificate. We put our SCTs inside the leaf, as most of the web does, so the blocks stay empty.

The script captures the Certificate message that OpenSSL actually sends (through the `ssl` module's message callback, a private but long-standing hook) and compares it to `certificate_message()`. For all three chains, with and without the intermediate, they are **identical**. The framing costs exactly $4 + 1 + 3 + 2 \times (3 + 2) = 18$ bytes; everything else is the certificates themselves.

## CertificateVerify: the signature made right now

```text
struct {
    SignatureScheme algorithm;
    opaque signature<0..2^16-1>;
} CertificateVerify;
```

Four bytes of header, two bytes naming the algorithm, two bytes of length, and the signature. The algorithm codes we see are `0x0403` (ecdsa_secp256r1_sha256) for the classical chain and `0x0904` / `0x0905` (mldsa44 / mldsa65) for the post-quantum ones; the ML-DSA values come from the IETF draft that specifies ML-DSA in TLS 1.3, which also fixes the context string to empty and rules out the pre-hashed variant.

What is signed is not the transcript hash alone (§4.4.3), but:

```text
64 bytes of 0x20 (spaces)
|| "TLS 1.3, server CertificateVerify"
|| 0x00
|| Transcript-Hash(ClientHello ... Certificate)
```

The 64 spaces and the context string are there so that a TLS 1.3 server signature can never be mistaken for a signature from another protocol (or another TLS version, or the client side) over the same bytes. It is the same idea as Part 01's repeated `signatureAlgorithm`: say exactly what the signature means, inside what is signed.

This signature is different in kind from the others in the handshake: it is made **online**, for every single connection, with a key that sits on the server. Every other signature in the chain was made **offline**, once, by a CA or a log, and is replayed to every client. Keep that distinction in mind: it is exactly the line along which Merkle Tree Certificates later cut.

## Five signatures and two keys

Now count everything a browser receives to trust one site.

<figure class="plate">
<img src="/images/root/02-signatures.svg" alt="The root, already in the client, signs the intermediate (signature 1). The intermediate signs the leaf (2). Two CT logs each sign an SCT embedded in the leaf (3 and 4). The leaf key signs the handshake in CertificateVerify (5). With ML-DSA-44: 2 public keys of 1,312 bytes and 5 signatures of 2,420 bytes, 14,724 bytes in total." width="1000" height="640" loading="lazy" />
<figcaption>Every signature and public key on the wire, and who made it.</figcaption>
</figure>

| # | signature | made by | when | sent in |
|---|---|---|---|---|
| 1 | on the intermediate certificate | the root CA | once, years ago | Certificate |
| 2 | on the leaf certificate | the intermediate CA | at issuance | Certificate |
| 3 | SCT from log A | a CT log | at issuance | inside the leaf |
| 4 | SCT from log B | another CT log | at issuance | inside the leaf |
| 5 | CertificateVerify | the server, with the leaf key | every connection | CertificateVerify |

Plus two public keys: the intermediate's (to check signature 2) and the leaf's (to check signature 5). The root's key is already in the client.

Cloudflare's 2021 study counted the same set plus one more, a stapled OCSP response; our toy server does not staple one, so we count five.

### Building real SCTs

An SCT ("signed certificate timestamp") is a CT log's promise to publish a certificate. Part 03 explains why browsers demand them; here we only need their bytes. To make them real rather than placeholders, the script follows RFC 6962 exactly:

1. The CA builds the leaf **without** the SCT extension. This is the *precertificate* TBS.
2. Each log signs a small TLS-encoded structure (RFC 6962 §3.2): version, signature type, timestamp, entry type `precert_entry`, the SHA-256 of the issuer's public key, the precertificate TBS, and an empty extensions field.
3. The CA adds the two SCTs to the leaf as one extension (OID `1.3.6.1.4.1.11129.2.4.2`) and signs the final certificate.

```python
def sct_signed_data(timestamp, issuer_spki, precert_tbs):
    return (u8(0) + u8(0)                         # v1, certificate_timestamp
            + struct.pack(">Q", timestamp)
            + u16(1)                              # precert_entry
            + hashlib.sha256(issuer_spki).digest()
            + vec24(precert_tbs)
            + vec16(b""))
```

A browser checking an SCT reverses step 3: it takes the final leaf, removes the SCT extension, and checks that the log signed what is left. The script does exactly that, using the `cryptography` library's independent `tbs_precertificate_bytes` to strip the extension, and both SCTs verify in all three chains.

Note the double wrapping, a detail from Part 01's world meeting TLS's: the SCT list is TLS-encoded (length-prefixed, no tags), and that blob goes inside a DER OCTET STRING, which in turn goes inside the extension's own OCTET STRING envelope.

<div class="warning">

RFC 6962 signs SCTs with TLS 1.2's `SignatureAndHashAlgorithm`, which has no code point for ML-DSA. For the post-quantum chains the script borrows TLS 1.3's `0x0904` and `0x0905` as a stand-in. The two bytes are made up; the sizes, which are what this part measures, are not.

</div>

## The bill, measured

Here are the three chains. The classical one has the shape of a common modern ECDSA chain: a P-384 root and intermediate, a P-256 leaf, and logs with P-256 keys. The two post-quantum chains use ML-DSA everywhere. Every certificate carries a realistic set of extensions: key identifiers, AIA, a policy, CRL distribution points on the intermediate, and the SCTs on the leaf.

| certificate | classical | ML-DSA-44 | ML-DSA-65 |
|---|---:|---:|---:|
| leaf | 845 B | 9,110 B | 12,417 B |
| intermediate | 711 B | 4,246 B | 5,775 B |
| root (not sent) | 532 B | 4,066 B | 5,595 B |

And here is everything the server sends to authenticate (the Certificate message plus CertificateVerify), split by what each byte is:

| | classical | ML-DSA-44 | ML-DSA-65 |
|---|---:|---:|---:|
| public keys (2) | 162 | 2,624 | 3,904 |
| CA signatures (2) | 205 | 4,840 | 6,618 |
| SCT signatures (2) | 142 | 4,840 | 6,618 |
| handshake signature (1) | 70 | 2,420 | 3,309 |
| everything else | 1,073 | 1,078 | 1,078 |
| **total** | **1,652** | **15,802** | **21,527** |

Look at the last row before the total. Names, dates, extensions, OIDs, SCT metadata, TLS framing: **1,073 bytes classical, 1,078 post-quantum.** Exactly Part 01's lesson, scaled up to a whole handshake: the structure does not care what algorithm it carries. Everything that grew is cryptography. Classical ECDSA keys and signatures are 579 bytes of a 1,652-byte bill; ML-DSA-44's are 14,724 bytes of 15,802.

(ECDSA signatures are DER-encoded integers whose length wobbles by a byte or two from one signature to the next; the certificates here are built with deterministic ECDSA so the numbers repeat, but OpenSSL's live CertificateVerify is anywhere from 78 to 80 bytes.)

## Bytes on the wire

The Certificate message is not the whole flight. Here is the classical server's first flight with hybrid key exchange, message by message, measured:

| message | plaintext | on the wire |
|---|---:|---:|
| ServerHello | 1,210 | 1,215 |
| ChangeCipherSpec | 1 | 6 |
| EncryptedExtensions | 6 | 28 |
| Certificate | 1,574 | 1,596 |
| CertificateVerify | 79 | 101 |
| Finished | 52 | 74 |
| **total** | | **3,020** |

The record layer adds a 5-byte header to every record, and every encrypted record also carries 1 byte of inner content type and a 16-byte AEAD tag (RFC 8446 §5.2): 22 bytes each. A record holds at most 16,384 bytes of plaintext, so a large Certificate message is split into several records, each paying the 22 bytes again. The ChangeCipherSpec is a fake: a 1-byte record that does nothing in TLS 1.3, sent only because some middleboxes break connections that do not look like TLS 1.2 (Appendix D.4).

The script predicts every server flight from the plaintext messages with these rules, and the prediction equals the measured bytes in every case. Now all twelve configurations:

| chain | sent | key exchange | ClientHello | server flight |
|---|---|---|---:|---:|
| classical | leaf + intermediate | X25519 | 232 | 1,953 |
| classical | leaf + intermediate | hybrid | 1,466 | 3,020 |
| classical | leaf only | X25519 | 232 | 1,238 |
| classical | leaf only | hybrid | 1,466 | 2,304 |
| ML-DSA-44 | leaf + intermediate | X25519 | 232 | 16,103 |
| ML-DSA-44 | leaf + intermediate | hybrid | 1,466 | **17,169** |
| ML-DSA-44 | leaf only | X25519 | 232 | 11,852 |
| ML-DSA-44 | leaf only | hybrid | 1,466 | 12,918 |
| ML-DSA-65 | leaf + intermediate | X25519 | 232 | 21,850 |
| ML-DSA-65 | leaf + intermediate | hybrid | 1,466 | **22,916** |
| ML-DSA-65 | leaf only | X25519 | 232 | 16,048 |
| ML-DSA-65 | leaf only | hybrid | 1,466 | 17,114 |

Post-quantum key exchange costs about a kilobyte each way. Post-quantum signatures cost **fourteen**. A browser's real ClientHello is larger than OpenSSL's minimal one (more extensions, GREASE values, sometimes an encrypted ClientHello), but the server flight barely depends on it.

## Why bytes turn into time

A few extra kilobytes over a fast link take microseconds to transmit. The cost is elsewhere: in how much a server is *allowed* to send before it hears back from the client.

**TCP.** A new TCP connection does not know how fast the path is, so it starts with a small **congestion window**: the amount of unacknowledged data it may have in flight. RFC 6928 set the standard initial window to 10 segments, which with a typical 1,460-byte segment is about **14,600 bytes**. The server sends that much, then must wait for the client's acknowledgements before it sends more. If the handshake flight is bigger than the window, the rest waits a full round trip.

<figure class="plate">
<img src="/images/root/02-round-trips.svg" alt="Two timelines. Left, flight fits: ClientHello, the whole server flight, then Finished and request, one round trip. Right, flight too big: ClientHello, ten segments, the server waits for the client's ACK, then the rest, then Finished and request: two round trips." width="1000" height="560" loading="lazy" />
<figcaption>Overflowing the first window does not cost a few microseconds; it costs a whole round trip.</figcaption>
</figure>

**QUIC** (HTTP/3) is stricter. Before a QUIC server has confirmed that the client's address is real, it may send at most **three times** as many bytes as it has received (RFC 9000 §8.1), so that nobody can use a spoofed ClientHello to aim a big response at a victim. The client must pad its first datagrams to at least 1,200 bytes (§14.1). A small ClientHello fits in one datagram, giving the server a budget of about 3,600 bytes; the 1,466-byte hybrid ClientHello needs two, so about 7,200. (The script's QUIC numbers are this rough rule: real packet overheads shift them by a few dozen bytes.)

<figure class="plate">
<img src="/images/root/02-flights.svg" alt="Bars to scale: classical 3,020 bytes, ML-DSA-44 leaf only 12,918, ML-DSA-44 full chain 17,169, ML-DSA-65 full chain 22,916. A line at about 7,200 bytes marks the QUIC budget, one at about 14,600 the TCP initial window. Only the classical flight is under both." width="1000" height="560" loading="lazy" />
<figcaption>Measured server flights (hybrid key exchange) against the two limits.</figcaption>
</figure>

The classical handshake fits under both limits with room to spare. **The full ML-DSA-44 chain overflows the TCP window**, and every post-quantum configuration overflows QUIC's budget. Note that the hybrid key exchange, which is already deployed, helps a little on QUIC: its big ClientHello buys the server a bigger budget.

This is not only theory. In 2021 Cloudflare ran a large experiment, adding dummy bytes to real certificate chains on real connections. Two findings stood out: above about **10 kB** of added data, failures from clients and middleboxes rose steeply, and below about **9 kB** the handshake slowed by roughly **15%**. Cloudflare called that workable but far from ideal, since a slowdown people notice is a reason to put off deploying post-quantum certificates. Chrome is stricter still and set **10%** as its maximum acceptable regression in handshake time, and reported that post-quantum key agreement had already used up part of that budget, about 4% in its measurements.

Our ML-DSA-44 chain adds about 14 kB over the classical one. It is past the cliff.

## What does not help: compression

TLS can compress the Certificate message (RFC 8879, with zlib, brotli or zstd), and for today's chains it works well: names, OIDs and extensions are repetitive. The script compresses each Certificate message with zlib at its highest level:

| chain | Certificate | compressed | saved |
|---|---:|---:|---:|
| classical | 1,574 | 1,171 | 25.6% |
| ML-DSA-44 | 13,374 | about 12,940 | about 3% |
| ML-DSA-65 | 18,210 | about 17,815 | about 2% |

The classical row is exact on every run. The post-quantum rows move by a few dozen bytes from run to run, because ML-DSA mixes fresh randomness into every signature: the sizes never change, but the bytes do, and so does what zlib happens to find in them. Either way the saving in bytes is roughly the same in all three cases, about 400: compression removes the redundancy in the structure and nothing else. Public keys and signatures are designed to be indistinguishable from random bytes, and random bytes do not compress. A compressor cannot make a signature smaller; only not sending it can.

## What helps, partly: do not send what the client has

The intermediate certificate is the same for millions of sites, and browsers already ship lists of the intermediates in the public trust stores. If the client has it, the server need not send it. The script tests exactly this, with the intermediate placed next to the root in the client's store:

- classical: 1,652 → **936** bytes of authentication;
- ML-DSA-44: 15,802 → **11,551** (server flight 12,918: **fits** in the TCP window);
- ML-DSA-65: 21,527 → **15,747** (server flight 17,114: still does not fit).

The IETF has a draft along these lines, *Abridged Compression for WebPKI Certificates*, which defines a compression scheme with a shared dictionary of all intermediates and roots in the major browsers' root stores (taken from the CCADB). For today's chains its author reports roughly 75% savings, against roughly 25% for generic compression. Since it is only compression, it changes no trust decisions.

It is a real gain, and it removes one key and one signature. But look at what remains with ML-DSA-44: the leaf's public key, the CA's signature on the leaf, two SCT signatures, and the CertificateVerify signature. That is $1312 + 4 \times 2420 = 11{,}000$ bytes that no compression and no dictionary can remove, because they are different for every certificate. It is still over QUIC's budget, and with ML-DSA-65 it is still over TCP's window. Within today's design, that is the floor.

## The floor, and the way through it

Split the remaining bytes by kind:

- **The CertificateVerify signature and the leaf key** (3,732 bytes with ML-DSA-44) prove that *this server, right now*, holds the key. Any design needs that proof; at most it can use a different primitive (some proposals use a KEM instead of a signature for this step).
- **The CA's signature and the two SCTs** (7,260 bytes) prove facts that were settled once, at issuance: that a CA vouched for the binding, and that the binding was logged in public. They are the same for every connection, yet every connection pays for them in full.

That second group is exactly the 7,260 bytes the Merkle Tree Certificates draft names in its introduction. Its idea, which the rest of this series builds up to, is to stop sending offline signatures one certificate at a time: the CA logs certificates in a Merkle tree, signs the tree rarely, and each certificate carries a few hundred bytes of hashes instead of three signatures.

Before we can get there we need to know why the SCTs exist at all. A CA's signature should be enough, so why does the web demand two more? Because CAs have lied. That is [Part 03](/root/03-when-authorities-lie/).

## Try it

From the `experiments\root-of-trust` folder, with `cryptography` 46 or newer:

```text
python 02_handshake.py
python -m unittest test_02_handshake
```

The byte model (chains, SCTs, the authentication bill, compression) runs everywhere. The live handshakes need a Python whose `ssl` module is linked against OpenSSL 3.5 or newer, because that is the first OpenSSL release with ML-DSA and ML-KEM in TLS. Check yours with:

```text
python -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

If it is older, the script says so and skips the live part, and the tests skip the live checks. Exercises:

1. Change the classical leaf to P-384. Which rows of the bill change, and by how much?
2. Remove the two SCTs from the ML-DSA-44 leaf. Does the full chain fit in the TCP window now?
3. Build a *mixed* chain: ML-DSA-44 everywhere except the CertificateVerify key. What does that save, and why can it not work in a real handshake? (Hint: whose key signs CertificateVerify?)
4. Make the QUIC estimate honest: look up the size of a QUIC Initial packet header and redo `quic_budget()`.

## Reader checkpoint

<details>
<summary><strong>1.</strong> Which two messages of the server's flight carry the authentication, and what does each one prove?</summary>

Certificate proves that a trusted CA (and two logs) bound the leaf public key to the name. CertificateVerify proves that the server holds the matching private key now, by signing the transcript of this very handshake.

</details>

<details>
<summary><strong>2.</strong> Why does the server not send the root certificate?</summary>

The client trusts only roots it already has. A root sent by the server could be anyone's self-signed certificate, so it would prove nothing and only cost bytes.

</details>

<details>
<summary><strong>3.</strong> Which of the five signatures are made online, and which offline? Why does that matter?</summary>

Only CertificateVerify is online, made for each connection by the server. The two CA signatures and the two SCTs are offline, made once and replayed to every client. Offline facts can be proved in other ways (for example with a Merkle tree proof), but the online proof of key possession cannot be dropped.

</details>

<details>
<summary><strong>4.</strong> Certificate compression saves 25.6% on the classical chain and about 3% on ML-DSA-44, but roughly the same number of bytes. Why?</summary>

It compresses the repetitive structure (names, OIDs, extensions), which is the same size in every chain. Keys and signatures look random and do not compress, and in the ML-DSA chain they are almost all of the bytes.

</details>

<details>
<summary><strong>5.</strong> A server's flight is 17,169 bytes over TCP. What happens, concretely?</summary>

With an initial window of 10 segments (about 14,600 bytes) the server sends the first part, then waits for the client's acknowledgements, which take a round trip, before it sends the rest. The handshake completes one round trip later than it would if the flight fit.

</details>

<details>
<summary><strong>6.</strong> Even with the intermediate omitted, about 11,000 bytes of ML-DSA-44 remain. Which ones, and which of them do Merkle Tree Certificates aim to remove?</summary>

The leaf key and four signatures: the CA's on the leaf, two SCTs, and CertificateVerify. MTCs target the three offline signatures (7,260 bytes), replacing them with an inclusion proof. The leaf key and the CertificateVerify signature stay.

</details>

## References

- RFC 8446, *The Transport Layer Security (TLS) Protocol Version 1.3*, and its revision RFC 9846: handshake (§2, §4), Certificate (§4.4.2), CertificateVerify (§4.4.3), record protection (§5.2), middlebox compatibility (Appendix D.4).
- [draft-ietf-tls-mldsa](https://datatracker.ietf.org/doc/draft-ietf-tls-mldsa/), *Use of ML-DSA in TLS 1.3*: SignatureScheme values mldsa44 (0x0904), mldsa65 (0x0905), mldsa87 (0x0906).
- draft-ietf-tls-ecdhe-mlkem: the hybrid X25519MLKEM768 group.
- RFC 6962, *Certificate Transparency*: SCT structure and the precertificate signature input (§3.2), the X.509 extension (§3.3).
- RFC 6928, *Increasing TCP's Initial Window*.
- RFC 9000, *QUIC*: address validation and the anti-amplification limit (§8.1), minimum Initial datagram size (§14.1).
- RFC 8879, *TLS Certificate Compression*.
- [draft-ietf-tls-cert-abridge](https://datatracker.ietf.org/doc/draft-ietf-tls-cert-abridge/), *Abridged Compression for WebPKI Certificates*.
- B. Westerbaan, [*Sizing Up Post-Quantum Signatures*](https://blog.cloudflare.com/sizing-up-post-quantum-signatures/), Cloudflare, 2021; and [*A look at the latest post-quantum signature standardization candidates*](https://blog.cloudflare.com/another-look-at-pq-signatures/), Cloudflare, 2024: the 2021 experiment's results and Chrome's 10% target.
- [Cloudflare Radar, post-quantum encryption](https://radar.cloudflare.com/post-quantum): current adoption of hybrid key exchange.
- FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA): key, ciphertext and signature sizes.
