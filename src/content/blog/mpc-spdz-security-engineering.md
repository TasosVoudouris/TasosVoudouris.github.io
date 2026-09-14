---
title: "SPDZ Security and Engineering Boundaries: Sacrifice, MASCOT, Truncation, and Abort"
description: "Audit the gap between a working arithmetic-MPC toy and a production SPDZ-family deployment: triple validation, malicious behavior, fixed-point truncation, OT preprocessing, transcript binding, and failure handling."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Cryptographic Engineering"
tags:
  - "spdz"
  - "mascot"
  - "sacrifice"
  - "truncation"
  - "fixed-point"
  - "abort"
  - "ot-extension"
difficulty: "Advanced"
status: "Reviewed"
series: "Secure Multiparty Computation"
seriesOrder: 5
draft: false
---
A toy can get every field equation right and still be far from a secure MPC system.

The recovered archive is a good example: it contains algebraically useful demos, but also code labelled `fullSPDZprotocol.py` that implements only a fragment of additive sharing. This chapter lists the missing boundaries explicitly.

## 1. Triple generation versus triple validation

A Beaver triple must satisfy

$$
c=ab.
$$

In a passive trusted-dealer simulation we simply sample $a,b$ and compute $c$.

Under a malicious preprocessing adversary, that relation must be checked without revealing the triple values. SPDZ-family systems use consistency mechanisms such as **sacrifice**, where some correlations are consumed to verify others.

The exact optimized protocol varies by generation, but the principle is constant:

> offline randomness is part of the trusted computing base unless it is itself cryptographically verified.

## 2. MASCOT changes preprocessing, not the Beaver identity

The recovered notes correctly point toward MASCOT and oblivious transfer.

OT-based preprocessing can generate multiplication correlations without the heavy homomorphic-encryption route of early SPDZ designs.

But MASCOT is not "SPDZ without triples." It is a way to produce the authenticated correlations required by the same style of online arithmetic.

This links directly to the separate Oblivious Transfer series.

## 3. Fixed-point arithmetic is a protocol problem

Machine-learning demos need real-valued arithmetic, but finite-field MPC computes integers modulo a prime.

A common encoding is

$$
\widetilde x=\lfloor 2^f x\rceil.
$$

Multiplication produces scale

$$
2^{2f},
$$

so the protocol must securely truncate/rescale back to $2^f$.

This is not the same as ordinary public integer division. A careless truncation can leak low bits, introduce bias, or fail around signed representatives and wraparound.

The old notes contain a masking-based truncation sketch. It is educational, but its security depends on bounds, mask distribution, field size, and adversary model that the code does not enforce.

## 4. Comparisons and nonlinear functions

Operations such as

- comparison;
- ReLU;
- max pooling;
- division;
- reciprocal;
- square root;
- softmax

are not cheap arithmetic-field gates.

A private-ML architecture must either implement secure subprotocols for them or replace/approximate them with MPC-friendly arithmetic.

Simply writing a Keras `Activation('softmax')` layer does not make softmax secure.

## 5. Randomness and session separation

Python's `random` module appears throughout the recovered experiments. That is fine for deterministic teaching demos but not for cryptographic preprocessing.

A real implementation needs:

- cryptographic randomness;
- explicit session IDs;
- domain-separated transcripts;
- one-time consumption of triples/nonces;
- replay protection;
- persistent state rules.

These are the same engineering concerns we saw in FROST and DKG.

## 6. Abort is part of correctness

If a MAC check fails, a triple is invalid, a party sends malformed data, or an expected message is missing, the protocol cannot simply print an error and continue.

A security proof normally defines what honest parties output in each failure case. Often the correct result is **abort**.

Production code therefore needs a state machine, not only arithmetic helper functions.

## 7. Network semantics

A local object such as

```python
PrivateValue(share0, share1)
```

stores both parties' shares in one process. That is ideal for simulation because we can inspect invariants.

It is not the distributed execution model.

The real protocol has separate processes with separate local states. A correct network port must preserve which party is allowed to see which share and which messages are public.

## 8. Malicious security does not mean fairness

Even an actively secure computation can allow a corrupt party to abort at strategic points, depending on the functionality and protocol guarantees.

Security properties such as privacy, correctness, guaranteed output delivery, robustness, and fairness are distinct.

Using the single word "secure" hides these differences.

## 9. Engineering checklist

Before calling an MPC implementation production-ready, ask:

- What is the exact corruption threshold?
- Passive or malicious adversary?
- Are channels authenticated?
- How are triples generated and validated?
- How are MAC keys established?
- How are openings checked?
- How are field elements canonically encoded?
- How is fixed-point overflow prevented?
- Are random values cryptographically sampled?
- Can preprocessing objects be reused accidentally?
- How are sessions/transcripts identified?
- What causes abort?

## 10. Takeaway

The recovered source is most valuable when treated as a sequence of **protocol skeletons**, not as a finished SPDZ implementation.

The corrected interpretation is:

$$
\boxed{\text{good arithmetic intuition} \ne \text{complete maliciously secure MPC system}.}
$$
