---
title: "Digital Signatures VI: Schnorr Signatures — Linear Verification, Tagged Hashes, and Multisignature Structure"
description: "A clean derivation of Schnorr signatures, why the verification equation is linear, and how modern profiles such as BIP 340 add x-only keys, tagged hashes, and deterministic nonce hardening."
pubDate: "2025-05-25"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Public-Key Cryptography"
  - "Elliptic-Curve Cryptography"
  - "Threshold Cryptography"
tags:
  - "schnorr"
  - "bip340"
  - "multisignatures"
  - "threshold-signatures"
difficulty: "Intermediate"
series: "Digital Signatures"
seriesOrder: 6
status: "Validated"
sourcePath: "experiments/digital-signatures"
draft: false
---
Schnorr signatures expose one of the cleanest signature equations in public-key cryptography. Their algebra is simple enough to derive on one page, yet that same linearity makes them a natural foundation for multisignatures, threshold signatures, adaptor signatures, and protocols such as FROST.

## Group setup

Let $G$ generate a prime-order group of order $q$. The signer chooses a private scalar

$$
x\in\mathbb{Z}_q
$$

and publishes

$$
Y=xG.
$$

## Signing

Choose a nonce

$$
k\in\mathbb{Z}_q,
$$

compute

$$
R=kG,
$$

and derive a challenge

$$
e=H(R\,\|\,Y\,\|\,m).
$$

Then compute

$$
s=k+ex\pmod q.
$$

The signature is conceptually $(R,s)$.

## Verification

The verifier recomputes $e$ and checks

$$
sG \stackrel{?}{=} R+eY.
$$

Correctness follows immediately:

$$
sG=(k+ex)G=kG+e(xG)=R+eY.
$$

That linear relation is the feature that makes Schnorr so composable.

## Why the challenge hashes the transcript

The challenge must bind the commitment $R$, public key $Y$, message, and protocol context according to the selected scheme. Leaving fields out can create replay, substitution, or rogue-key problems in composed protocols.

This is why a real signature profile defines exact byte encodings and hash domains rather than merely saying "hash the message."

## BIP 340 as a concrete modern profile

Bitcoin's BIP 340 defines 64-byte Schnorr signatures over secp256k1. It makes several engineering choices that are not visible in the generic equation:

- x-only public keys,
- a deterministic parity convention,
- tagged hashes for domain separation,
- a hardened nonce derivation that can mix auxiliary randomness,
- exact byte encodings and test vectors.

Those choices turn a mathematical scheme into an interoperable protocol format.

## Multisignatures are not "just add signatures"

Because the verification equation is linear, it is tempting to aggregate public keys and nonces by simple addition. A naive construction is vulnerable to rogue-key and nonce-manipulation problems.

Secure multisignature protocols add coefficient derivation, key aggregation rules, transcript binding, and nonce commitments. Threshold Schnorr protocols go further by replacing the single private scalar with distributed shares and interpolation weights.

The Threshold Cryptography Engineering series studies that transition in detail.

## Nonce reuse is still catastrophic

From

$$
s=k+ex\pmod q,
$$

if the same $k$ is reused for challenges $e_1\ne e_2$,

$$
s_1-s_2=(e_1-e_2)x\pmod q,
$$

so

$$
x=(s_1-s_2)(e_1-e_2)^{-1}\pmod q.
$$

Schnorr's simple algebra makes both its elegance and its failure modes extremely clear.

## Companion experiment

The companion `schnorr_toy.py` uses a deliberately small subgroup so the signing and verification equation can be traced directly. It is for algebraic understanding only.

## References

- Claus Schnorr, **Efficient Identification and Signatures for Smart Cards**, 1991.
- Bitcoin Improvement Proposal 340, **Schnorr Signatures for secp256k1**.
- RFC 9591, **FROST**, for a standardized threshold Schnorr protocol.
