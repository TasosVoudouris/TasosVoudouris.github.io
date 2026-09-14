---
title: "Length-Extension Attacks"
description: "Understand why secret-prefix MACs built from Merkle–Damgård hashes are vulnerable, derive glue padding, reproduce the attack, and see why HMAC avoids this failure mode."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
  - "Implementation Security"
tags:
  - "length-extension"
  - "sha256"
  - "mac"
  - "hmac"
  - "merkle-damgard"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 5
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. The vulnerable construction

Suppose a server publishes a tag

\[
t=\operatorname{SHA256}(K\mathbin\|M)
\]

where (K) is a secret byte string and (M) is attacker-visible. This *secret-prefix hash* is an improvised MAC, not HMAC.

Because SHA-256 is Merkle–Damgård, its digest encodes the final eight-word chaining state. An attacker who knows (t) and the byte length of (K\|M) can continue the public compression function and compute a valid tag for

\[
K\mathbin\|M\mathbin\|P(K\mathbin\|M)\mathbin\|X,
\]

where (P(\cdot)) is the original SHA-256 padding and (X) is an attacker-chosen suffix.

The server hashes the forged message after prepending (K), reconstructs exactly the same padded prefix, and reaches the same internal state (t) before processing (X). The attacker never learns (K).

## 2. What information is required

The attacker needs:

- the original visible message (M);
- its valid secret-prefix tag (t);
- the chosen suffix (X);
- the hash algorithm and message encoding;
- the length of the hidden prefix (K), or a small range of plausible lengths;
- a verifier response that reveals which candidate was accepted, if the length is guessed online.

The secret bytes themselves are not needed. If the key length is unknown, the attacker can try candidates. Each guess creates different glue-padding bytes and a different tag.

## 3. Glue padding exactly

Let (L=|K|+|M|) be the original byte length. SHA-256 glue padding is

```text
80 || 00 ... 00 || big_endian_64(8L)
```

with enough zero bytes to make (L+|P|\equiv0\pmod{64}).

If a secret is 15 bytes and the visible message is 23 bytes, then (L=38). The padding is:

- one byte `80`;
- 17 zero bytes, bringing the pre-length field position to byte 56;
- the eight-byte encoding of (38\cdot8=304=0x130).

The processed prefix is now 64 bytes. To append (X), the attacker resumes SHA-256 from the published digest and sets the logical byte counter to 64 before hashing (X) and its final padding.

The forged message contains non-printable glue padding. A vulnerable parser must accept or ignore those bytes in a way that preserves the attacker's intended semantics. Cryptographic feasibility does not guarantee application-level exploitability.

## 4. Algebraic view

Write the padded original message as blocks (B_1,\ldots,B_r). The legitimate computation is

\[
h_i=f(h_{i-1},B_i),\qquad t=h_r.
\]

The public digest gives the attacker (h_r). Split (X\|P') into new blocks (C_1,\ldots,C_s), where (P') encodes the total extended length. The attacker computes

\[
h_{r+j}=f(h_{r+j-1},C_j)
\]

from the known starting state (h_r=t). The final (h_{r+s}) is the forged tag.

No compression-function inversion, collision, or key recovery occurs. The attacker is using the compression function exactly as specified, starting from an exposed internal state.

## 5. End-to-end lab

[`code/length_extension_demo.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/length_extension_demo.py) models a vulnerable server and an attacker. The server holds:

```python
server_secret = b"server-side-key"
original = b"comment=hello&role=user"
published_tag = hashlib.sha256(server_secret + original).digest()
```

The attack API accepts no secret bytes:

```python
candidate = forge_sha256_secret_prefix_mac(
    original=original,
    known_tag=published_tag,
    suffix=b"&role=admin",
    guessed_secret_length=guess,
)
```

For each guess, it:

1. calculates `sha256_padding(guess + len(original))`;
2. constructs `original || glue_padding || suffix`;
3. parses the known digest into eight 32-bit state words;
4. resumes the compression function after a block-aligned processed length;
5. pads according to the *extended* total length;
6. returns the forged message and tag.

The demo's local verifier accepts the candidate at the correct 15-byte guess and rejects the same forged tag when HMAC verification is used.

Run:

```bash
python code/length_extension_demo.py
```

## 6. Which hashes are affected?

Classic exposed-state Merkle–Damgård hashes are the usual targets, including MD5, SHA-1, SHA-256, and SHA-512 when used in an inappropriate prefix-MAC construction. Details such as digest truncation can change whether enough internal state is exposed. SHA-224 and SHA-384, for example, publish truncated states, so the direct attack is not identical.

SHA-3 uses a sponge construction and does not expose the entire 1600-bit internal state as its digest. It is not vulnerable to this same continuation attack. That does **not** make `SHA3-256(key || message)` a recommended MAC: use KMAC, HMAC with an approved hash where specified, or another standardized keyed construction.

BLAKE2 defines a native keyed mode. It should be invoked through that specified interface rather than mimicked by concatenating a secret.

## 7. Why common variations do or do not help

### `Hash(K || M)`

Vulnerable to length extension for affected hashes and encodings.

### `Hash(M || K)`

The direct continuation attack cannot append data *before* the unknown trailing key. That alone is not a general security proof, and ad hoc constructions should not replace a standardized MAC.

### `Hash(K || M || K)`

This blocks the simple public continuation path because the attacker does not know the final key material. It remains an unnecessary custom construction without the mature analysis and interoperability of HMAC.

### HMAC

For block size (B), normalized key (K_0), and hash (H):

\[
\operatorname{HMAC}_K(M)
=H\left((K_0\oplus\text{opad})\mathbin\|H((K_0\oplus\text{ipad})\mathbin\|M)\right).
\]

The published tag is the output of the *outer* hash. Even if an attacker conceptually extends that outer computation, the resulting bytes are not a legitimate HMAC evaluation because the outer input has a fixed structure containing the unseen, key-dependent pad and an inner digest. The construction's security analysis is deeper than this intuition, but the nested form explains why the secret-prefix continuation trick does not transfer.

## 8. Protocol-level defenses

1. Replace secret-prefix hashes with a standardized MAC.
2. Prefer authenticated encryption when both secrecy and integrity are required.
3. Authenticate a canonical, length-delimited representation of all security-relevant fields.
4. Include protocol name, direction, version, algorithm, and message type in the authenticated context when the protocol does not already provide separation.
5. Verify tags before acting on unauthenticated data.
6. Compare tags in constant time and return uniform errors.
7. Add nonces, sequence numbers, timestamps, or replay windows as required; a valid MAC alone does not prove freshness.
8. Rotate and separate keys according to the protocol, not by reusing one secret across hashing, encryption, and unrelated services.

## 9. Frequent misconceptions

- **“The padding length field prevents extension.”** It prevents an ambiguity needed by the classical collision reduction; it lets the attacker calculate the exact glue padding.
- **“The attacker must know the key.”** Only the key length must be known or guessed.
- **“This finds a SHA-256 collision.”** The original and forged messages have different digests under plain SHA-256; the attacker computes the correct new digest.
- **“Hiding the original message fixes it.”** Obscurity is not a MAC security model, and many protocols expose most or all of the authenticated data.
- **“Using SHA-512 automatically fixes it.”** SHA-512 has the same exposed-state iteration issue when misused as a secret-prefix MAC.

Primary algorithm definition: [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final). HMAC construction: [RFC 2104](https://www.rfc-editor.org/info/rfc2104).

Previous: [Merkle–Damgård and SHA-256](/blog/merkle-damgard-sha256/).

Next: [Sponge, Keccak, and SHA-3](/blog/sponge-keccak-sha3/).
