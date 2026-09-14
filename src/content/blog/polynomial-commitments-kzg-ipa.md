---
title: "Polynomial Commitments: KZG, IPA-Based Schemes, Openings, and Batching"
description: "Study the polynomial-commitment interface modern proof systems need, derive KZG opening verification, contrast trusted structured reference strings with IPA-based commitments, and separate polynomial commitments from FRI."
pubDate: "2025-03-01"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Elliptic-Curve Cryptography"
tags:
  - "polynomial-commitment"
  - "kzg"
  - "ipa"
  - "pairings"
  - "batch-opening"
  - "structured-reference-string"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 7
draft: false
---
Once a proof system turns computation into polynomials, it needs a way to say:

> I committed to one polynomial $f(X)$, and at challenge point $z$ its value is $y$.

A **polynomial commitment scheme (PCS)** supplies this interface without revealing every coefficient or evaluation.

## 1. The abstract interface

A PCS has operations resembling:

```text
pp = Setup(max_degree)
C  = Commit(pp, f)
π  = Open(pp, f, z)
Verify(pp, C, z, y, π)
```

Desired properties include:

- **binding**: one commitment should not open inconsistently;
- **succinct openings**: the proof should be much smaller than the polynomial;
- **efficient verification**;
- often **batching** for many polynomials/points;
- optionally **hiding**, or a way to blind commitments when zero knowledge is needed.

A binding polynomial commitment does not automatically hide $f$.

## 2. KZG commitment idea

Kate–Zaverucha–Goldberg commitments use a structured reference string containing powers of a hidden scalar $\tau$.

For

$$
f(X)=\sum_{i=0}^{d} f_i X^i,
$$

an SRS contains encodings of

$$
1,\tau,\tau^2,\ldots,\tau^d.
$$

In multiplicative notation, the commitment is conceptually

$$
C=g^{f(\tau)}.
$$

The committer computes it without learning $\tau$ by multi-scalar multiplication over the SRS powers.

## 3. Opening at one point

To prove

$$
f(z)=y,
$$

define the quotient polynomial

$$
q(X)=\frac{f(X)-y}{X-z}.
$$

Because $f(z)=y$, the division has no remainder.

The opening proof commits to $q(\tau)$:

$$
\pi=g^{q(\tau)}.
$$

Then

$$
f(\tau)-y=q(\tau)(\tau-z).
$$

A pairing equation can check this multiplicative identity in the exponents without revealing $\tau$.

## 4. Why KZG is attractive

KZG offers very small commitments and opening proofs and efficient batching. This made it highly influential in pairing-based SNARKs and polynomial protocols.

The tradeoff is setup and assumptions:

- an SRS supports polynomials only up to a configured degree;
- the trapdoor $\tau$ must not remain known to an adversary;
- pairing-friendly elliptic-curve assumptions enter the security story.

An **updatable** ceremony can reduce trust: security can survive if at least one contributor honestly destroys its secret update.

## 5. Universal setup is not infinite setup

Systems such as PLONK can use a **universal** SRS that is not tied to one exact circuit. But "universal" still has parameter limits, typically a maximum supported polynomial degree/domain size and fixed curve/commitment parameters.

This is better described as *circuit-universal within a configured capacity*, not as a magical setup that supports arbitrary future computation without bounds.

## 6. IPA-based commitments

Another family replaces pairings with inner-product arguments over ordinary discrete-log groups.

Very roughly, the prover commits to a coefficient/vector representation and then recursively folds an inner-product relation. Proof communication can be logarithmic in vector length.

Advantages can include:

- no pairing-specific toxic-waste trapdoor;
- compatibility with ordinary prime-order curves;
- natural use in recursive systems such as Halo-style constructions.

Tradeoffs differ from KZG: verification and prover work have different constants/asymptotics, and the exact commitment construction matters.

## 7. Bulletproofs, IPA, and polynomial commitments are related but not identical words

An inner-product argument is a protocol primitive. Bulletproofs use inner-product arguments for compact range/arithmetic-circuit proofs. Halo develops IPA-based polynomial commitment machinery suitable for recursive proof composition.

It is therefore safer to say **IPA-based commitment/proof systems** than to use "Bulletproofs," "IPA," and "polynomial commitment" as interchangeable names.

## 8. Batching openings

Modern proof systems rarely open one polynomial once. They may need values such as

$$
f_1(z),f_2(z),\ldots,f_k(z)
$$

or the same polynomial at several related points.

Random linear combination challenges can aggregate claims. For example, with verifier challenge $v$,

$$
F(X)=f_1(X)+v f_2(X)+v^2 f_3(X)+\cdots.
$$

One opening of $F$ can bind many claimed evaluations, provided the transcript order and soundness analysis are correct.

## 9. Where FRI fits

FRI is often mentioned beside KZG and IPA because it underlies transparent polynomial-commitment constructions. But **FRI itself is an interactive oracle proof of proximity for Reed–Solomon codes**, not merely a group commitment with a `Commit/Open` interface.

A STARK-style polynomial commitment layer typically combines:

- low-degree extension/evaluation vectors;
- Merkle commitments;
- FRI low-degree proximity testing;
- authenticated query openings.

We study FRI separately after the STARK architecture is clear.

## 10. The proof-system interface is what matters

Different backends can support similar high-level operations while changing the trust and performance model dramatically.

| Backend idea | Main cryptographic basis | Setup flavor | Opening style |
|---|---|---|---|
| KZG | pairings / structured powers | structured SRS | constant-size pairing proof |
| IPA-based | discrete-log group + inner-product argument | transparent public generators / no toxic trapdoor in the KZG sense | logarithmic folding proof |
| FRI-based | hashes + Reed–Solomon proximity | transparent | Merkle-authenticated low-degree queries |

### Primary references

- A. Kate, G. M. Zaverucha, I. Goldberg, *Constant-Size Commitments to Polynomials and Their Applications*, ASIACRYPT 2010.
- B. Bünz et al., *Bulletproofs: Short Proofs for Confidential Transactions and More*, IEEE S&P 2018.
- S. Bowe, J. Grigg, D. Hopwood, *Recursive Proof Composition without a Trusted Setup (Halo)*, 2019.
