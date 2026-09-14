---
title: "RC4: KSA, PRGA, Keystream Biases, the FMS Attack, and Why the Cipher Is Obsolete"
description: "Study RC4 as a historical stream cipher: its permutation update, keystream generation, statistical biases, WEP/FMS failure mode, and formal deprecation in TLS."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Symmetric Cryptography"
  - "Cryptanalysis"
  - "Implementation Security"
  - "Randomness & Entropy"
tags:
  - "rc4"
  - "arc4"
  - "fms"
  - "wep"
  - "stream-cipher"
  - "keystream-bias"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 5
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---
RC4 is worth studying precisely because it is **simple enough to understand completely and broken enough to teach multiple lessons at once**.

It maintains a permutation $S$ of the bytes $0,\ldots,255$. A Key Scheduling Algorithm (KSA) mixes the secret key into that permutation; a Pseudo-Random Generation Algorithm (PRGA) then updates the permutation and emits one byte at a time.

RC4 is historical material, not a cipher to deploy.

## KSA

Initialize

$$
S[i]=i,\qquad 0\le i<256.
$$

Then iterate

$$
j\leftarrow(j+S[i]+K[i\bmod |K|])\bmod256
$$

and swap $S[i]$ with $S[j]$.

The result is a key-dependent permutation.

## PRGA

For every output byte:

$$
i\leftarrow(i+1)\bmod256,
$$

$$
j\leftarrow(j+S[i])\bmod256,
$$

swap $S[i],S[j]$, then output

$$
Z=S[(S[i]+S[j])\bmod256].
$$

Encryption is

$$
C_i=P_i\oplus Z_i.
$$

The structure is compact and fast in software, which helped make RC4 extremely popular.

## The problem is not one single attack

RC4 accumulated a long list of biases and related-key weaknesses. Its keystream is not distributed as an ideal random stream, especially in early bytes, and repeated encryptions under related key material can amplify these biases statistically.

This matters because many applications did not use RC4 as "one independent random key per message." They embedded public IV material into or alongside a long-term secret in ways that exposed related-key structure.

## WEP and FMS

The Fluhrer–Mantin–Shamir attack exploited weak-IV behavior in the way WEP constructed per-packet RC4 keys. Certain IV patterns leak statistical information about key bytes through early keystream output.

The important lesson is narrower than the old note's phrase "any implementation concatenating IV + secret is broken by FMS." FMS targets specific relationships between RC4's KSA and WEP-style related keys; one should not generalize the exact exploit to every conceivable concatenation scheme.

Nevertheless, the design lesson is broad: **key/nonce processing is part of a cipher system's security**, and a primitive cannot rescue a protocol that repeatedly exposes dangerous related-key structure.

## RC4 and TLS

RFC 7465 requires TLS clients and servers to never negotiate RC4 cipher suites. RC4 should therefore be treated as cryptanalytic history and compatibility archaeology, not as a reasonable modern option.

## Executable historical vector

The companion implementation is intentionally minimal and labeled historical. It validates the classic example

- key: `Key`
- plaintext: `Plaintext`
- ciphertext: `BBF316E8D940AF0AD3`

with

```bash
python experiments/randomness-stream-ciphers/test_rc4.py
```

Passing a test vector confirms implementation consistency, **not security**.

## What replaces RC4?

Modern protocol design uses well-studied constructions with explicit nonce and authentication semantics. For stream-cipher-based AEAD, ChaCha20-Poly1305 is the obvious next study point; raw ChaCha20 itself is the subject of the next chapter.

## References

- Fluhrer, Mantin, Shamir, *Weaknesses in the Key Scheduling Algorithm of RC4*.
- RFC 7465, *Prohibiting RC4 Cipher Suites*.
