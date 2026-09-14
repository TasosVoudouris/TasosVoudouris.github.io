---
title: "QFESTA: Quaternion-Accelerated Isogeny-Based Key Encapsulation After the SIDH Breaks"
description: "A research note on QFESTA, its relationship to FESTA and post-SIDH isogeny research, the SageMath proof-of-concept in the recovered archive, and why it should be treated as research rather than a deployed PQC standard."
pubDate: "2025-03-21"
updatedDate: "2026-09-12"
topics:
  - "Post-Quantum Cryptography"
  - "Elliptic-Curve Cryptography"
  - "Cryptographic Engineering"
tags:
  - "qfesta"
  - "festa"
  - "isogenies"
  - "kem"
  - "post-quantum"
  - "quaternion-algebras"
difficulty: "Advanced"
status: "Research Note"
draft: false
---
The Part 2 archive contains a SageMath proof-of-concept labeled **QFESTA**. This material belongs in CryptoCave, but not under a generic "KEMS" dump and not as if it were a standardized replacement for ML-KEM.

QFESTA is an **isogeny-based key-encapsulation/encryption research construction** developed in the post-SIDH/SIKE landscape. Its main intellectual interest is that techniques related to the attacks that destroyed SIDH can be repurposed constructively inside new isogeny-based systems.

## Context: after SIDH/SIKE

SIDH/SIKE suffered devastating key-recovery attacks based on higher-dimensional isogeny techniques. That did not end all isogeny research; it changed which structures can reasonably be trusted.

FESTA explored a different direction: use supersingular-torsion machinery and the new higher-dimensional techniques as part of a trapdoor construction rather than exposing exactly the SIDH structure that had become vulnerable.

QFESTA then improves the computational side using quaternion-algebra techniques.

## What the recovered code says

The supplied `QFESTA-SageMath` archive describes itself as a proof-of-concept implementation of

> Quaternion Fast Encapsulation from Supersingular Torsion Attacks.

It reuses components from FESTA and theta/isogeny codebases and supports benchmark runs at several nominal security levels.

The example bundled with the archive reports, for one 128-bit-security parameter run, values on the order of:

- public key: 247 bytes;
- ciphertext: 494 bytes;
- key generation, encapsulation, and decapsulation taking seconds in SageMath.

Those numbers are **implementation-example measurements**, not universal performance guarantees and not a standards profile.

## Why quaternion algebras appear

Supersingular isogeny problems have a deep correspondence with quaternion orders and ideals. QFESTA uses quaternion-algebra algorithms to make operations that were expensive in the original FESTA parameter generation/construction substantially more efficient.

The important conceptual bridge is

```text
supersingular curves / isogenies
        ↕
quaternion-algebra structure
        ↓
more efficient algorithms for the trapdoor construction
```

This is one reason isogeny-based cryptography remains mathematically interesting even after SIKE's failure.

## Security status

QFESTA should be treated as **research cryptography**:

- it is not one of the standardized NIST PQC algorithms;
- the recovered implementation is a SageMath proof of concept;
- isogeny-based proposals require continued specialized cryptanalysis;
- implementation validation and constant-time behavior are separate from the mathematical construction.

The archive also contains an analysis document about Kyber-512 "gate" counts. I have kept that as source/reference material rather than turning one controversial cost-model argument into a canonical CryptoCave conclusion.

## Why this is a standalone research note

CryptoCave does not yet have a mature ordered post-quantum series comparable to the RSA or threshold tracks. Forcing QFESTA into a one-item "KEM series" would create a misleading taxonomy.

For now it sits under:

- Post-Quantum Cryptography;
- Elliptic-Curve Cryptography;
- Cryptographic Engineering.

When the future PQC track is built, this note can move into an isogeny-based-research branch alongside the historical SIKE break and modern signature/encryption directions.

## References

- Nakagawa and Onuki, *QFESTA: Efficient Algorithms and Parameters for FESTA Using Quaternion Algebras*, CRYPTO 2024.
- Basso, Maino, Pope, *FESTA: Fast Encryption from Supersingular Torsion Attacks*.
- The recovered `QFESTA-SageMath` proof-of-concept archive, retained in the Part 2 source batch.
