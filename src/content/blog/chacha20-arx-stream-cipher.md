---
title: "ChaCha20: ARX Design, Quarter Rounds, Counters, and Nonce Discipline"
description: "Build the RFC 8439 ChaCha20 block function from additions, rotations, and XORs, then connect counter/nonce rules to stream-cipher security and AEAD use."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Symmetric Cryptography"
  - "Cryptographic Engineering"
  - "Randomness & Entropy"
tags:
  - "chacha20"
  - "arx"
  - "rfc-8439"
  - "stream-cipher"
  - "nonce"
  - "quarter-round"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 6
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---
ChaCha20 represents a very different design philosophy from LCGs, LFSRs, and RC4. Its core operations are **addition, rotation, and XOR**—the ARX family—and its state transformation is intentionally built to diffuse differences rapidly without S-box table lookups.

RFC 8439 is the current IETF reference for the 256-bit-key, 96-bit-nonce variant used in Internet protocols.

## State layout

The block function operates on sixteen 32-bit words:

$$
\begin{bmatrix}
c_0&c_1&c_2&c_3\\
k_0&k_1&k_2&k_3\\
k_4&k_5&k_6&k_7\\
ctr&n_0&n_1&n_2
\end{bmatrix}.
$$

The first row encodes the constant string `expand 32-byte k`; the next two rows hold the 256-bit key; the final row contains a 32-bit block counter and 96-bit nonce.

## Quarter round

For words $(a,b,c,d)$, the quarter round is

```text
a += b; d ^= a; d <<<= 16
c += d; b ^= c; b <<<= 12
a += b; d ^= a; d <<<=  8
c += d; b ^= c; b <<<=  7
```

All additions are modulo $2^{32}$.

The mixture of arithmetic addition and XOR breaks the simple linear models that make LFSRs easy to reconstruct.

## Twenty rounds

ChaCha20 performs ten **double rounds**. Each double round contains:

1. four column quarter rounds;
2. four diagonal quarter rounds.

After twenty rounds, the transformed words are added to the original state word-by-word. The result is serialized little-endian into a 64-byte block.

## Stream encryption

For block counter $j$,

$$
KS_j=\operatorname{ChaCha20Block}(K,j,N).
$$

Plaintext bytes are XORed with the concatenated blocks.

This immediately gives the central engineering rule: under a fixed key, a nonce/counter combination must not repeat. Repetition recreates the same keystream and returns us to the XOR failure

$$
C_1\oplus C_2=P_1\oplus P_2.
$$

## Raw ChaCha20 versus ChaCha20-Poly1305

ChaCha20 alone provides encryption/keystream generation. It does **not** authenticate ciphertext or associated metadata.

RFC 8439 also specifies ChaCha20-Poly1305, which derives a one-time Poly1305 authentication key from ChaCha20 and provides an AEAD interface. That construction is discussed in [Authenticated Encryption and AEAD](/blog/authenticated-encryption-aead/).

The distinction matters: a strong stream cipher is not automatically an authenticated-encryption scheme.

## Why the old notebook needed updating

The recovered code referenced RFC 7539. RFC 8439 obsoletes RFC 7539 and incorporates its errata and clarifications. The algorithmic core remains recognizable, but the site should point readers at the current stable reference.

The older notes also mixed 64-bit and 96-bit nonce variants. This article follows the **IETF RFC 8439 construction**: 32-byte key, 12-byte nonce, 32-bit counter.

## Executable RFC test vector

The companion implementation contains only the block function and validates RFC 8439's Section 2.3.2 vector:

```bash
python experiments/randomness-stream-ciphers/test_chacha20.py
```

This makes the article's state layout, endianness, rotations, and round schedule executable rather than purely diagrammatic.

## Security lesson

ChaCha20 does not become secure merely because it is nonlinear. Its confidence comes from a deliberately designed permutation structure, extensive public cryptanalysis, explicit parameterization, and clear operational rules.

That is the opposite of "take a simple PRNG and XOR it with data."

## Reference

- RFC 8439, *ChaCha20 and Poly1305 for IETF Protocols*.
