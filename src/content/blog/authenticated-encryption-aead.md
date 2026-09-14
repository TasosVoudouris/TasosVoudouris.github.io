---
title: "Authenticated Encryption and AEAD: From Encrypt-then-MAC to GCM and ChaCha20-Poly1305"
description: "Why confidentiality without integrity is insufficient, how composition order matters, what AEAD authenticates, and how modern constructions such as AES-GCM and ChaCha20-Poly1305 should be used."
pubDate: "2025-02-28"
updatedDate: "2026-09-12"
topics:
  - "Symmetric Cryptography"
  - "Hash Functions"
  - "Implementation Security"
  - "Cryptographic Engineering"
tags:
  - "authenticated-encryption"
  - "aead"
  - "encrypt-then-mac"
  - "aes-gcm"
  - "chacha20-poly1305"
difficulty: "Intermediate"
series: "Symmetric Cryptography"
seriesOrder: 5
status: "Reviewed"
draft: false
---
Encryption alone answers a confidentiality question: can an unauthorized party learn the plaintext? Many real protocols need a second guarantee: can an attacker modify a ciphertext and cause the receiver to accept a forged plaintext or forged metadata?

**Authenticated encryption** combines confidentiality with integrity/authenticity. **Authenticated Encryption with Associated Data (AEAD)** additionally authenticates data that is intentionally left unencrypted.

## The AEAD interface

RFC 5116 models an AEAD algorithm with inputs conceptually equivalent to

$$
(K,N,P,A),
$$

where

- $K$ is the key,
- $N$ is a nonce,
- $P$ is plaintext,
- $A$ is associated authenticated data.

Encryption returns ciphertext plus authentication information. Decryption either returns the plaintext or fails authentication.

Associated data is useful for protocol headers, sequence numbers, algorithm identifiers, or routing metadata that must remain visible but must not be modifiable without detection.

## Why composition order matters

Older constructions often combined a conventional encryption mode and a MAC. Three generic compositions are commonly discussed:

- Encrypt-and-MAC,
- MAC-then-Encrypt,
- Encrypt-then-MAC.

Under suitable assumptions and key separation, Encrypt-then-MAC has a particularly clean composition story: the receiver authenticates the ciphertext before releasing plaintext.

But deployed protocols should normally use a standardized AEAD mode directly rather than reconstructing an ad-hoc composition from CBC and HMAC.

## Verify before acting on plaintext

An AEAD decryption API should conceptually behave atomically:

$$
\operatorname{Open}(K,N,C,A)\rightarrow P\ \text{or}\ \bot.
$$

Unauthenticated plaintext should not be processed as if it were trustworthy. Error behavior also matters: detailed parsing differences can become oracles, as the RSA and CBC-padding literature repeatedly demonstrates.

## AES-GCM

GCM combines counter-mode encryption with polynomial authentication over a binary field. NIST SP 800-38D specifies GCM and GMAC.

The crucial operational rule is nonce/IV management. Reusing a GCM nonce with the same key is a severe failure: counter-mode keystream reuse damages confidentiality, and the authentication structure can also be compromised.

A correct library API is therefore not enough if the application repeats nonces.

### GHASH and why nonce reuse also attacks authenticity

GCM's authentication component works over the binary field $\mathrm{GF}(2^{128})$. It derives the hash subkey

$$
H=E_K(0^{128})
$$

and evaluates a polynomial hash over the associated data, ciphertext blocks, and encoded lengths. The authentication tag can be viewed schematically as

$$
T=E_K(J_0)\oplus\operatorname{GHASH}_H(A,C).
$$

When the same nonce is reused under the same key, the same $J_0$ and therefore the same mask $E_K(J_0)$ reappear. Subtracting/XORing two tag equations cancels that mask and leaves algebraic relations in the unknown hash key $H$. Under favorable message structures and enough information, those relations can recover candidate authentication state and enable tag forgery. This family of failures is often described as the **GCM forbidden attack**.

So GCM nonce reuse is worse than ordinary CTR keystream reuse: it can damage both **confidentiality and authenticity**. The recovered Part 2 notebooks contained a useful Sage demonstration of this polynomial viewpoint; the canonical site keeps the mathematics here rather than another duplicate GCM implementation.

## ChaCha20-Poly1305

RFC 8439 specifies ChaCha20-Poly1305 as an AEAD construction with a 256-bit key and a 96-bit nonce. ChaCha20 provides the encryption stream; Poly1305 provides authentication using a one-time key derived from ChaCha20 for that nonce.

As with GCM, nonce uniqueness under a fixed key is part of the security contract.

## AAD is authenticated, not encrypted

If a protocol places a header in AAD, an eavesdropper can still read it. The guarantee is that an attacker should not be able to change the authenticated header without causing decryption to fail.

This distinction is frequently misunderstood in application code.

## Key separation

If encryption and MAC are composed manually, distinct derived keys should be used for the different primitives unless the construction specifically proves otherwise. AEAD algorithms already define their internal key use; application developers should not split or reuse subkeys ad hoc.

## Nonces are not always secrets

Most AEAD nonces are transmitted or derivable publicly. Their required property is normally uniqueness under the key, not secrecy. Confusing "nonce" with "secret random value" can lead to overcomplicated systems that still fail to enforce uniqueness.

The exact requirement is algorithm-specific, so the named AEAD specification remains authoritative.

## Where this belongs in CryptoCave

This article sits after block-cipher modes and before linear cryptanalysis. The Hash Functions & MACs series explains MAC constructions in depth; this chapter focuses on how confidentiality and authentication are combined into an encryption interface.

## References

- RFC 5116, **An Interface and Algorithms for Authenticated Encryption**.
- NIST SP 800-38D, **Galois/Counter Mode (GCM) and GMAC**.
- RFC 8439, **ChaCha20 and Poly1305 for IETF Protocols**.
