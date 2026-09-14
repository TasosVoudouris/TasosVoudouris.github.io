---
title: "From Secret Sharing to Secure Multiparty Computation: Arithmetic Circuits, Threat Models, and Communication"
description: "Build the conceptual bridge from linear secret sharing to MPC, separating local linear operations from interactive multiplication and making the adversary, leakage, communication, and circuit model explicit."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Secret Sharing"
  - "Cryptographic Engineering"
tags:
  - "secure-multiparty-computation"
  - "arithmetic-circuits"
  - "secret-sharing"
  - "communication-complexity"
  - "semi-honest"
  - "malicious-security"
difficulty: "Intermediate"
status: "Reviewed"
series: "Secure Multiparty Computation"
seriesOrder: 1
draft: false
---
Secret sharing answers a storage/distribution question. MPC answers a computation question.

That difference is easy to blur because many MPC protocols represent private values **as secret shares**. The recovered archive repeatedly crossed that boundary without stating when interaction or a stronger security mechanism became necessary. This series makes the boundary explicit.

## 1. The MPC goal

Parties $P_1,\ldots,P_n$ hold private inputs

$$
x_1,\ldots,x_n
$$

and want to compute

$$
y=F(x_1,\ldots,x_n)
$$

while revealing no more than the intended output and whatever leakage is allowed by the protocol's security model.

The phrase "secure computation" is incomplete unless we say:

- which parties can be corrupted;
- whether corrupt parties follow the protocol;
- whether they can collude;
- what outputs are revealed and to whom;
- whether abort is allowed;
- whether preprocessing is trusted or distributed.

## 2. Passive versus active adversaries

A **semi-honest** (honest-but-curious) party follows the protocol but inspects its transcript.

A **malicious** party may:

- send malformed shares;
- substitute values;
- use inconsistent messages for different recipients;
- bias preprocessing;
- abort after learning partial information.

Many recovered toy scripts are meaningful only in the passive setting. Calling them "SPDZ" or "malicious-secure MPC" would therefore be incorrect.

## 3. Arithmetic circuits

Secret-sharing MPC often evaluates an arithmetic circuit over a finite field.

The circuit has gates such as:

$$
z=x+y,
$$

$$
z=xy,
$$

and multiplication by public constants.

Linear gates are usually cheap because secret sharing is linear.

Nonlinear gates are where communication and preprocessing enter.

## 4. Local linear operations

For additive shares

$$
x=\sum_i x_i,
$$

$$
y=\sum_i y_i,
$$

parties can locally compute

$$
z_i=x_i+y_i.
$$

Then

$$
\sum_i z_i=x+y.
$$

Likewise, for public $a$:

$$
[ax]_i=a[x]_i.
$$

No communication is required.

Shamir shares provide analogous linearity through polynomial addition.

## 5. Why private multiplication is interactive

If additive parties locally multiply their shares,

$$
x_i y_i,
$$

the sum is generally **not** $xy$ because the cross terms are missing.

If Shamir parties multiply evaluations, the product is correct as a polynomial evaluation but the degree grows.

So multiplication forces the protocol to do something extra:

- communicate;
- consume correlated randomness;
- reduce degree;
- invoke OT/HE;
- or use another multiplication subprotocol.

## 6. Circuit depth versus local CPU time

In ordinary software we often optimize operation count. In MPC we also care about:

- total communication volume;
- number of interactive rounds;
- WAN latency;
- preprocessing cost;
- number of openings;
- number of multiplication gates;
- bit-decomposition/comparison cost.

Two algebraically equivalent expressions can have very different MPC costs.

## 7. Secret sharing is not encryption

Several recovered ML notes repeatedly say the parties "train on encrypted data." The code actually uses secret shares.

These are related privacy mechanisms but not interchangeable terms.

With encryption, one typically has a ciphertext under a cryptographic key. With secret sharing, no individual share needs to be a ciphertext at all; privacy follows from the joint distribution of shares and the adversary threshold.

This distinction becomes important when comparing MPC with homomorphic encryption.

## 8. The preprocessing model

Many practical MPC protocols split work into:

### Offline phase

Before private inputs are known, generate correlated randomness such as multiplication triples.

### Online phase

Use those correlations so private-input computation needs only lightweight arithmetic and a small number of openings.

This is the conceptual structure behind Beaver triples and SPDZ.

## 9. What this series will build

We proceed in layers:

1. Beaver triples for private multiplication;
2. authenticated secret sharing and global MAC invariants;
3. SPDZ online protocol anatomy;
4. malicious-security checks and preprocessing boundaries;
5. vector/tensor batching and fixed-point arithmetic;
6. private machine-learning examples and their caveats.

The point is not to reproduce a production MPC framework in a blog. It is to make the security invariant visible at every layer.

## 10. Takeaway

$$
\boxed{\text{secret sharing is a representation; MPC is an interactive protocol for computing on that representation.}}
$$

Once that distinction is clear, Beaver triples, SPDZ MACs, truncation, OT-based preprocessing, and private-ML engineering fit into one coherent picture.
