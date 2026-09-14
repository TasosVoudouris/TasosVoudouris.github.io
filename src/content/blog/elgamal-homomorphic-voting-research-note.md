---
title: "Homomorphic ElGamal Voting: What the Toy Prototype Shows—and What a Secure Election Still Needs"
description: "A research note that salvages the useful algebra from an old ElGamal voting prototype while separating homomorphic tallying from ballot proofs, DKG, threshold decryption, robustness, eligibility, and coercion resistance."
pubDate: "2025-06-03"
updatedDate: "2026-09-12"
topics:
  - "Public-Key Cryptography"
  - "Zero-Knowledge Proofs"
  - "Threshold Cryptography"
  - "Cryptographic Engineering"
tags:
  - "elgamal"
  - "e-voting"
  - "homomorphic-tally"
  - "zero-knowledge"
  - "distributed-decryption"
difficulty: "Advanced"
status: "Research Note"
sourcePath: "experiments/elgamal-voting"
draft: false
---
Part1 contained an ambitious prototype described as a "secure voting system" combining ElGamal, distributed keys, zero-knowledge proofs, and homomorphic tallying. The mathematical direction is useful, but the implementation and the original security claims were much stronger than the code justified.

The cleaned CryptoCave version therefore keeps the good idea and removes the false confidence.

## Exponential ElGamal for additive tallies

Let $G=\langle g\rangle$ be a prime-order group and let the election public key be

$$
h=g^x.
$$

Encode a small vote $v$ as $g^v$. With fresh randomness $r$, encrypt

$$
C=(g^r,\;h^r g^v).
$$

Multiplying ciphertexts component-wise gives

$$
\prod_i C_i
=
\left(g^{\sum r_i},\;h^{\sum r_i}g^{\sum v_i}\right),
$$

which is an encryption of the **sum of the votes in the exponent**.

After decryption, the tally authority obtains $g^{\sum v_i}$ and can decode the small bounded tally by searching the allowed range.

This homomorphic relation is real and useful.

## What homomorphic tallying does not prove

It does not prove that each ciphertext encrypts an allowed ballot. A malicious participant might encrypt $g^{100}$ instead of $g^0$ or $g^1$ and distort the tally.

A real protocol therefore needs a zero-knowledge proof that each ciphertext encodes a valid choice without revealing which choice.

## Distributed keys are another protocol

The old prototype called its setup "Pedersen DKG," but its code effectively published independently generated public-key shares and multiplied them. That is not by itself a complete robust DKG protocol.

A real distributed-key setup must define share distribution, verifiability, complaints, qualification, malicious-dealer handling, transcript binding, and participant consistency. Those issues are treated separately in the Threshold Cryptography Engineering series.

## Distributed decryption needs proofs

If several trustees contribute partial decryptions, each share should be accompanied by a proof that it is consistent with the trustee's public key/share. Otherwise one malformed share can corrupt the result.

Chaum–Pedersen-style equality-of-discrete-log proofs are a common building block for this purpose.

## Fiat–Shamir is not a fixed challenge

The recovered code used a hard-coded value as a placeholder "beacon" for a non-interactive proof challenge. That destroys the intended soundness argument. A Fiat–Shamir transform derives the challenge from a cryptographic hash of a domain-separated transcript; it is not an arbitrary public constant.

This is one of the concrete corrections that motivated rewriting the article rather than publishing the prototype unchanged.

## A secure election needs much more

End-to-end verifiable voting is a systems problem. Beyond encryption and proofs, a practical design may need:

- voter eligibility and duplicate-vote prevention,
- a public append-only bulletin board,
- ballot privacy and unlinkability,
- robust trustee thresholds rather than "everyone must remain online",
- verifiable mix/tally procedures,
- coercion and receipt-freeness analysis,
- dispute resolution and audit rules,
- precise election semantics.

No small Python prototype should claim all of those properties by default.

## Companion experiment

The cleaned `homomorphic_tally_toy.py` demonstrates only the safe mathematical claim: exponential ElGamal ciphertexts can be multiplied so that bounded plaintext exponents add. It deliberately omits ZK proofs, DKG, threshold decryption, and real-election claims.

## Research context

The old notes referenced the Cramer–Gennaro–Schoenmakers line of work on secure elections and proof techniques. That literature is the right direction for a formal treatment; the CryptoCave toy is now labeled as a research bridge rather than a finished protocol.
