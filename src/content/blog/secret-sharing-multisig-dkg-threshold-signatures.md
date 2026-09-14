---
title: "Secret Sharing, Multisignatures, BLS Aggregation, DKG, and Threshold Signatures Compared"
description: "Separate five commonly conflated multi-party cryptographic primitives by key structure, message relation, output object, trust model, and composition."
pubDate: "2025-05-21"
updatedDate: "2026-09-12"
topics:
- "Threshold Cryptography"
- "Secret Sharing"
- "Public-Key Cryptography"
- "MPC"
tags:
- "multisignature"
- "bls"
- "aggregate-signatures"
- "dkg"
- "threshold-signatures"
- "secret-sharing"
difficulty: "Intermediate"
series: "Threshold Cryptography Engineering"
seriesOrder: 14
draft: false
---
The words **secret sharing**, **multisignature**, **aggregate signature**, **distributed key generation**, and **threshold signature** are often placed next to each other because all of them involve several parties. They are not interchangeable.

The cleanest way to distinguish them is to ask two questions:

1. **What object is distributed?** A secret, a public key, or signing authority?
2. **What does the verifier finally see?** Several signatures, one aggregate signature, or one ordinary-looking threshold signature?

This article compares the constructions at that level before we use them together in larger threshold systems.

## 1. Shamir Secret Sharing

Shamir Secret Sharing (SSS) is a **data-distribution primitive**. A dealer encodes a secret $s$ as the constant term of a random polynomial and gives one polynomial evaluation to each participant.

For a reconstruction threshold $t$:

- any $t$ valid shares reconstruct $s$;
- fewer than $t$ shares reveal no information about $s$;
- basic SSS does not authenticate shares or prove that the dealer behaved correctly.

SSS by itself does **not** create signatures. It is a building block that can be used to distribute a private key or other sensitive state.

## 2. Multisignatures

A multisignature protocol lets several independent signers jointly authorize the **same message**.

The signers normally retain distinct private keys. A modern multisignature scheme may produce a **single compact signature** under an aggregated public key, as in Schnorr-family constructions such as MuSig-style protocols.

That means "multisig" should not be equated with "a list of $n$ signatures." Some multisignature systems are compact; others are not.

A multisignature also differs from a threshold signature: in a $t$-of-$n$ threshold system, any authorized subset of size $t$ may be able to sign under one long-term group public key, whereas many multisignature schemes are designed around a fixed signer set participating in the joint signing protocol.

## 3. Aggregate Signatures

An aggregate-signature scheme combines signatures that may come from **different public keys and, depending on the construction, different messages**.

BLS signatures are the standard example. If

$$
\sigma_i = H(m_i)^{x_i},
$$

then signatures can be multiplied in the pairing group to form an aggregate

$$
\sigma = \prod_i \sigma_i.
$$

Verification checks a corresponding pairing equation.

Aggregation is not automatically threshold signing. In ordinary BLS aggregation, every signer has an independent private key. **Threshold BLS** is a separate construction in which shares of one private key generate signature shares that interpolate into one BLS signature.

### Rogue-key caveat

Naive public-key aggregation can be vulnerable to rogue-key attacks. Real systems therefore need an appropriate registration model, proof of possession, or an aggregation construction whose security proof accounts for maliciously chosen keys.

## 4. Distributed Key Generation

DKG is a **setup protocol**. Its purpose is to generate a group secret key in shared form without allowing any one participant to choose or learn the complete secret.

After a DKG:

- participant $P_i$ holds a private share $s_i$;
- the system has one group public key $Y$;
- the full private key $s$ is ideally never reconstructed;
- the shares can feed a threshold signature or threshold-decryption protocol.

DKG therefore answers a different question from multisignatures or aggregation: it creates the distributed key material on which a threshold primitive can operate.

## 5. Threshold Signatures

A threshold signature scheme lets an authorized subset of participants produce **one valid signature under one group public key**, while no single participant holds the complete signing key.

A typical signing flow is:

1. the parties already hold shares from a trusted sharing or DKG;
2. an authorized subset runs the signing protocol;
3. each party produces a partial signing contribution;
4. the contributions are checked and combined;
5. the verifier sees one final signature.

Depending on the underlying signature scheme, the threshold protocol may need nonce-generation subprotocols, zero-knowledge proofs, consistency checks, preprocessing, or robust complaint handling.

Threshold versions exist for schemes such as BLS, Schnorr/EdDSA-style signatures, and ECDSA, but their protocol complexity differs substantially.

## 6. Side-by-Side Comparison

| Primitive | Long-term key structure | Typical message relation | Final verifier object | Trusted dealer inherently required? | Main purpose |
| --- | --- | --- | --- | --- | --- |
| Shamir secret sharing | One secret split into shares | N/A | Reconstructed secret/value | Basic form uses a dealer | Private data distribution |
| Multisignature | Independent signer keys | Usually same message | Often one compact joint signature, scheme-dependent | No | Joint authorization |
| Aggregate signature | Independent signer keys | Same or distinct messages, scheme-dependent | One aggregate signature | No | Compress many signatures |
| DKG | One secret key generated directly in shares | N/A | One group public key + private shares | No | Dealerless key setup |
| Threshold signature | One private key represented by shares | One message per signing execution | One group signature | No if combined with DKG | $t$-of-$n$ signing |

## 7. How the Pieces Compose

These primitives often appear in one stack:

$$
\text{DKG}
\rightarrow
\text{shared private key}
\rightarrow
\text{threshold signature}
\rightarrow
\text{single public signature}.
$$

A different system may use:

$$
\text{independent keys}
\rightarrow
\text{multisignature/aggregation}
\rightarrow
\text{single compact authorization object}.
$$

The two architectures solve related operational problems, but their trust assumptions and failure modes are different.

## 8. BLS as an Example of the Distinction

BLS is useful because it supports several related constructions:

- ordinary BLS signatures,
- aggregate BLS signatures from independent keys,
- BLS multisignatures on the same message,
- threshold BLS signatures from shares of one secret key.

The algebra looks similar because group elements multiply cleanly, but the **security model is not the same**. Public-key registration, proof of possession, signer-set binding, threshold interpolation, and DKG all belong to different layers of the system.

## 9. Security Questions to Ask

Before calling a design "threshold" or "distributed," check:

- Can one party ever reconstruct the full long-term secret?
- Who chooses the group public key?
- What happens if a dealer is malicious?
- Can a signer choose a rogue public key?
- Are partial signatures individually verifiable?
- Is the protocol secure against malicious or only semi-honest participants?
- What synchrony or broadcast assumptions are required?
- Does the final object verify exactly like a standard signature?

Those questions are more informative than the label attached to the scheme.

## 10. Takeaway

Secret sharing distributes **information**. DKG distributes **key generation**. Threshold signatures distribute **signing authority**. Multisignatures coordinate **independent signers**, and aggregate signatures compress **multiple signatures**.

They can be combined, but none of them should be treated as a synonym for the others.
