---
title: "Classical Cryptanalysis IV: One-Time Pads, Stream Ciphers, and the Catastrophe of Key/Nonce Reuse"
description: "Why the one-time pad is information-theoretically secure only under strict one-time use, and how stream-cipher keystream reuse exposes plaintext XORs, known-plaintext recovery, and crib-dragging structure."
pubDate: "2024-10-30"
updatedDate: "2026-09-12"
topics:
  - "Classical Cryptography"
  - "Symmetric Cryptography"
  - "Cryptanalysis"
  - "Implementation Security"
tags:
  - "one-time-pad"
  - "stream-cipher"
  - "nonce-reuse"
  - "crib-dragging"
  - "xor"
difficulty: "Introductory"
series: "Classical Cryptanalysis"
seriesOrder: 4
status: "Validated"
sourcePath: "experiments/classical-cryptanalysis"
draft: false
---
The one-time pad (OTP) is a rare cryptographic construction with information-theoretic secrecy. Its guarantee, however, depends on conditions that are easy to state and easy to violate.

For a message $M$ and uniformly random key $K$ of the same length,

$$
C=M\oplus K.
$$

Decryption is identical:

$$
M=C\oplus K.
$$

## Why one-time really means one-time

Suppose two messages are encrypted with the same pad or keystream:

$$
C_1=M_1\oplus K,
$$

$$
C_2=M_2\oplus K.
$$

XOR the ciphertexts:

$$
C_1\oplus C_2=M_1\oplus M_2.
$$

The key disappears.

The attacker does not immediately learn both messages, but it obtains a direct relation between them. Natural-language redundancy, file formats, protocol headers, or one known plaintext can then reveal much more.

## Known plaintext

If $M_1$ is known,

$$
M_2=(C_1\oplus C_2)\oplus M_1.
$$

Equivalently, the attacker can recover the reused keystream segment from one plaintext/ciphertext pair and apply it to the other ciphertext.

The companion experiment demonstrates exactly this relation.

## Crib dragging

When neither plaintext is fully known, an analyst can guess a plausible word or phrase—a *crib*—at different offsets in $M_1\oplus M_2$. Each guess implies a candidate fragment in the other plaintext. Plausible language fragments reinforce candidate positions.

This is not a magical break of XOR. It is exploitation of redundancy after key reuse removed the one-time-pad secrecy argument.

## Stream ciphers and nonces

Modern stream ciphers do not distribute a truly random pad as long as every message. Instead they derive a pseudorandom keystream from a secret key and nonce/counter.

The critical requirement becomes: **do not repeat the effective keystream under the same key**.

For modern AEAD constructions such as ChaCha20-Poly1305 or counter-based block-cipher modes, nonce reuse can be catastrophic in ways that affect both confidentiality and authentication.

The exact failure depends on the construction, which is why applications should follow a protocol or library API that specifies nonce generation rather than inventing one.

## From classical failure to modern engineering

This topic sits at the boundary between historical cryptanalysis and modern implementation security. The algebra is elementary, but the operational lesson is current: uniqueness constraints are part of the cryptographic contract.

## Companion experiment

`experiments/classical-cryptanalysis/otp_reuse.py` demonstrates that two ciphertexts under the same keystream expose $M_1\oplus M_2$ and that a known plaintext immediately reveals the other message.
