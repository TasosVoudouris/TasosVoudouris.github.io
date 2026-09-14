---
title: "Digital Signatures I: Security Goals, Hash-Then-Sign, and What Can Go Wrong"
description: "A detailed foundation for digital signatures: authenticity, integrity, EUF-CMA security, hashing, encoding, verification, and the difference between a signature primitive and a complete protocol."
pubDate: "2025-03-05"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
tags:
  - "digital-signatures"
  - "euf-cma"
  - "hash-then-sign"
  - "public-key"
difficulty: "Introductory"
series: "Digital Signatures"
seriesOrder: 1
status: "Reviewed"
draft: false
---
A digital signature is not simply "encryption with the private key." That shortcut is especially misleading when moving from textbook RSA to modern signature schemes such as ECDSA, EdDSA, and Schnorr. A signature scheme is its own cryptographic primitive with its own algorithms, encodings, randomness requirements, and security definition.

The goal of this series is to build the subject in that order: first the security model, then concrete families, and finally the implementation failures that repeatedly turn correct mathematics into broken systems.

## The three algorithms

A public-key signature scheme consists of three algorithms:

1. **Key generation** produces a secret signing key $sk$ and a public verification key $pk$.
2. **Signing** computes a signature $\sigma \leftarrow \operatorname{Sign}_{sk}(m)$.
3. **Verification** outputs accept or reject from $\operatorname{Verify}_{pk}(m,\sigma)$.

Correctness requires that honestly generated signatures verify:

$$
\Pr[\operatorname{Verify}_{pk}(m,\operatorname{Sign}_{sk}(m))=1] \approx 1.
$$

That is only correctness. Security asks whether an adversary who sees signatures on messages of its choice can create a new valid signature.

## The central security goal: unforgeability

The standard conceptual target is **existential unforgeability under chosen-message attack** (EUF-CMA). Informally, an adversary may ask for signatures on messages it chooses. It wins if it later outputs a valid signature for a message that it did not previously ask the signer to sign.

This distinction matters because signatures are usually deployed behind APIs, protocols, certificates, package managers, blockchains, or update systems where an attacker can often obtain many legitimate signatures.

A scheme that only resists a passive attacker is not enough.

## Why signatures usually hash the message

Most practical schemes do not perform their core algebra directly on an arbitrary-length message. Instead they sign a digest or an encoding derived from the message:

$$
h = H(m).
$$

Hashing gives a fixed-size input and separates the message format from the algebraic domain. But the exact encoding is part of the signature scheme. "Hash and then do some modular exponentiation" is not a complete specification.

The hash function and the signature encoding must prevent structural ambiguity and must be used exactly as specified by the scheme.

## Signatures do not provide confidentiality

A signature is normally public. Anyone with the public key should be able to verify it. Therefore a signature gives no secrecy to the signed message.

When a protocol needs both confidentiality and authenticity, it must compose encryption and authentication carefully. For symmetric systems this leads naturally to AEAD. For public-key systems it often leads to authenticated key exchange plus symmetric AEAD rather than trying to make one primitive do every job.

## Domain separation and protocol context

A subtle failure occurs when the same signing key is used across different protocols and the signed byte strings are ambiguous. Robust protocols therefore bind context into what is signed. A conceptual transcript may look like

$$
\operatorname{encode}(\text{protocol-id},\text{version},\text{role},\text{message}).
$$

Modern designs often use explicit domain-separation strings or tagged hashes. The important engineering rule is that the signer and verifier must agree on exactly the same byte-level representation.

## Randomness is sometimes part of the secret state

Some signature families require a fresh per-signature nonce $k$. In DSA and ECDSA, revealing, reusing, or even slightly biasing $k$ can reveal the long-term private key.

That failure mode is so important that it deserves its own article later in this series. Deterministic nonce derivation, such as the method in RFC 6979 for ECDSA, removes one class of random-number-generator failure while leaving key generation dependent on secure randomness.

Other schemes, such as EdDSA, define deterministic signing behavior as part of the construction.

## Verification is an attack surface too

A verifier must do more than check one final equation. Depending on the scheme it may need to validate:

- signature ranges,
- public-key encodings,
- curve points and subgroup membership,
- algorithm identifiers,
- hash and parameter choices,
- canonical encodings,
- protocol context.

Skipping validation can turn mathematically correct verification formulas into acceptance bugs or cross-protocol attacks.

## Signature malleability

A signature can sometimes have more than one valid representation for the same message and key. Whether that is acceptable depends on the protocol. Transaction systems, consensus protocols, and transcript hashes may require a canonical representation even when the underlying mathematical scheme accepts multiple valid signatures.

This is a good example of the difference between a signature primitive and the system around it.

## What this series will distinguish

The recovered CryptoCave notes had several signature families mixed together. The cleaned organization separates them by algebra and by modern status:

- RSA signatures are integer-factorization based and need a signature encoding such as PSS.
- ElGamal and historical DSA use finite-field discrete logarithms.
- ECDSA transfers the DSA-style equation to elliptic-curve groups.
- Schnorr uses a simpler linear verification relation and is the foundation for many modern multisignature and threshold constructions.
- EdDSA is an Edwards-curve signature family with deterministic nonce derivation and standardized encodings.

## Engineering rule

Do not implement a production signature system from the equations in these articles. The equations are for understanding and controlled experiments. Real deployments should use reviewed libraries and a named standard profile, including its key encoding, hashing, randomness, validation, and serialization rules.

## References

- NIST, **FIPS 186-5: Digital Signature Standard**, 2023.
- NIST, **SP 800-186: Recommendations for Discrete Logarithm-Based Cryptography: Elliptic Curve Domain Parameters**, 2023.
- RFC 8017, **PKCS #1 v2.2: RSA Cryptography Specifications**.
- RFC 6979, **Deterministic Usage of DSA and ECDSA**.
- RFC 8032, **Edwards-Curve Digital Signature Algorithm (EdDSA)**.
