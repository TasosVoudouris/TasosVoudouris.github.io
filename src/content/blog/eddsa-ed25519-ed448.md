---
title: "Digital Signatures VII: EdDSA — Ed25519, Ed448, Deterministic Nonces, and Encoding Discipline"
description: "How EdDSA differs from ECDSA despite both using elliptic curves, with the Ed25519/Ed448 signing structure, deterministic nonce derivation, encodings, and modern standardization context."
pubDate: "2025-05-08"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Elliptic-Curve Cryptography"
  - "Public-Key Cryptography"
  - "Implementation Security"
tags:
  - "eddsa"
  - "ed25519"
  - "ed448"
  - "rfc8032"
difficulty: "Intermediate"
series: "Digital Signatures"
seriesOrder: 7
status: "Reviewed"
draft: false
---
EdDSA is an elliptic-curve signature family, but it should not be described as "ECDSA on an Edwards curve." The signing equation, key expansion, nonce derivation, point encoding, and verification rules are different.

RFC 8032 specifies two major instances: Ed25519 and Ed448. FIPS 186-5 also includes EdDSA as an approved digital-signature family, with NIST SP 800-186 specifying the relevant Edwards-curve domain parameters.

## High-level structure

At a conceptual level, an EdDSA private input is hashed/expanded to derive signing material. A scalar component determines the public key

$$
A=aB,
$$

where $B$ is the base point.

For a message $M$, the signer derives a nonce scalar deterministically from secret prefix material and the message, computes

$$
R=rB,
$$

then derives a challenge from the encoded commitment, public key, and message. The response has the Schnorr-like form

$$
S=r+ka\pmod L.
$$

Verification checks a corresponding group relation.

The exact hashing, pruning/clamping, encoding, cofactor handling, and domain parameters are scheme-specific and must be taken from the standard rather than improvised from this summary.

## Deterministic signing

The older Part1 `EdDSA.py` demonstrated Edwards-curve arithmetic but was not an implementation of RFC 8032. It derived values with ad-hoc SHA-256 operations and omitted standardized encoding and scalar processing.

That file is useful as an Edwards-group exercise, but calling it "Ed25519 signing" would be incorrect. The canonical CryptoCave reference therefore preserves the mathematics while explicitly separating it from the standardized algorithm.

## Ed25519 and Ed448

RFC 8032 defines recommended parameter sets for Ed25519 and Ed448. They differ in field size, curve parameters, hash/XOF choices, encodings, and performance/security targets.

They should be treated as named algorithms, not as generic templates where parameters can be swapped casually.

## Why complete formulas matter

Edwards curves are attractive partly because suitable models admit complete or highly regular addition formulas, reducing exceptional cases in point arithmetic. That can simplify implementations and help reduce classes of implementation mistakes, although constant-time coding and side-channel engineering remain separate requirements.

## Prehash and context variants

RFC 8032 defines variants including prehash modes and context handling for some instances. Applications must choose the variant intentionally; a signature under one mode is not simply interchangeable with another.

## Public-key and signature parsing

Modern signature failures often occur at the encoding boundary. Implementations must follow the standard's point decoding, scalar range, and canonical-encoding rules. Accepting non-canonical or malformed encodings can create interoperability or security problems even when the underlying curve equation is correct.

## Quantum context

Like ECDSA and Schnorr, EdDSA is based on elliptic-curve discrete logarithms and is not designed to resist a sufficiently large cryptographically relevant quantum computer. That is a separate migration problem from the classical implementation issues discussed here.

## References

- RFC 8032, **Edwards-Curve Digital Signature Algorithm (EdDSA)**.
- NIST FIPS 186-5, **Digital Signature Standard**.
- NIST SP 800-186, **Elliptic Curve Domain Parameters**.
