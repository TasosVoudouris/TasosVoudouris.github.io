---
title: "Sigma Protocols: Schnorr, Feige–Fiat–Shamir Identification, HVZK, and Special Soundness"
description: "Understand three-move public-coin proofs through Schnorr and square-root identification, including completeness, honest-verifier zero knowledge, special soundness, and the corrections needed for multi-secret Fiat–Shamir notes."
pubDate: "2025-02-24"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Public-Key Cryptography"
  - "Mathematical Foundations"
tags:
  - "sigma-protocol"
  - "schnorr"
  - "fiat-shamir-identification"
  - "special-soundness"
  - "hvzk"
  - "identification"
difficulty: "Intermediate"
status: "Validated"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 2
sourcePath: "experiments/zero-knowledge/sigma"
draft: false
---
A **Sigma protocol** is a three-move public-coin protocol with the characteristic shape

$$
P\to V:t,\qquad V\to P:c,\qquad P\to V:z.
$$

The first prover message $t$ is often called a commitment, though it is not necessarily a standalone cryptographic commitment scheme. The verifier then samples a random challenge $c$, and the prover answers with $z$.

The name comes from the shape of the three-message transcript and is now used for a broad family of proof-of-knowledge protocols.

## 1. Schnorr knowledge proof

Let $G=\langle g\rangle$ be a cyclic group of prime order $q$. The public statement is

$$
y=g^x,
$$

and the witness is the discrete logarithm $x\in\mathbb Z_q$.

The protocol is:

1. Prover samples $r\leftarrow\mathbb Z_q$ and sends
   $$t=g^r.$$
2. Verifier samples challenge $c\leftarrow\mathbb Z_q$.
3. Prover sends
   $$z=r+cx\pmod q.$$
4. Verifier checks
   $$g^z\stackrel?=t\,y^c.$$

Completeness follows immediately:

$$
g^z=g^{r+cx}=g^r(g^x)^c=t y^c.
$$

## 2. Special soundness

Suppose we obtain **two accepting transcripts with the same first message** $t$ but distinct challenges:

$$
(t,c_1,z_1),\qquad(t,c_2,z_2),\qquad c_1\neq c_2.
$$

Then

$$
z_1-z_2=(c_1-c_2)x\pmod q,
$$

so

$$
x=(z_1-z_2)(c_1-c_2)^{-1}\pmod q.
$$

This algebra is the archetype of **special soundness**. A prover able to answer two distinct challenges for the same commitment exposes the witness to an extractor.

The companion experiment implements exactly this extractor.

## 3. Honest-verifier zero knowledge

An honest verifier chooses $c$ uniformly. A simulator can therefore generate an accepting transcript without knowing $x$:

1. sample $c,z\leftarrow\mathbb Z_q$;
2. set
   $$t=g^z y^{-c}.$$

Then $g^z=t y^c$ by construction, and the simulated transcript has the same distribution as an honest execution.

This establishes HVZK. It does **not** automatically prove security against an arbitrarily malicious verifier.

## 4. Identification based on square roots

The uploaded notes contained a multi-secret square-root identification scheme over an RSA modulus. This family is historically connected to the Fiat–Shamir/Feige–Fiat–Shamir line of identification protocols, but several details needed correction before becoming canonical material.

At a high level, choose an RSA-like modulus $n=pq$ and secret square roots $s_i\in\mathbb Z_n^*$. Depending on the exact convention, public values may be defined using $s_i^2$ or their inverses. A round contains:

- a random square commitment derived from $r$;
- a challenge vector $a=(a_1,\ldots,a_k)$;
- a response combining $r$ with selected secret roots.

The verification equation checks the square of the response against the commitment and selected public values.

The **exact public-key convention matters**. One cannot freely mix formulas from variants that publish $s_i^2$ with formulas that publish $s_i^{-2}$.

## 5. Correction: the challenge size controls soundness

The original note claimed that repeating $t$ rounds gives cheating probability $2^{-t}$ while simultaneously using a $k$-bit challenge vector.

That statement is not generally correct.

If a protocol round presents one unpredictable bit, a basic special-soundness intuition often leads to a $1/2$ per-round cheating probability. If the challenge is chosen uniformly from a larger challenge space, the knowledge/soundness error depends on that space and on the exact protocol definition.

A $k$-bit challenge is not automatically equivalent to one bit repeated once.

## 6. Correction: two challenge vectors do not automatically reveal every secret

The original report also stated that two different challenge vectors for the same commitment allow one to "extract each $s_i$."

That is too strong. With multi-coordinate challenges, subtracting/dividing two accepting responses generally isolates a **combination** of secret values corresponding to the coordinates where the challenges differ. Extracting an entire vector requires the exact special-soundness theorem for that protocol and a sufficient set of accepting transcripts/challenge relations.

This is why extraction claims should be proved from the actual transcript algebra rather than asserted from analogy with one-dimensional Schnorr.

## 7. Fiat–Shamir identification is not the Fiat–Shamir transform

Two historically related ideas share the names Fiat and Shamir:

- **Fiat–Shamir identification**: a concrete identification/proof-of-knowledge family based on modular square roots;
- **the Fiat–Shamir transform**: a general technique that replaces public verifier challenges with transcript hashes to remove interaction in the random-oracle style model.

The next chapter is about the second idea.

## 8. Why Sigma protocols matter far beyond identification

The commit/challenge/response pattern is a conceptual ancestor of many modern systems. Even when the implementation later uses polynomial commitments, arithmetization, or oracle proofs, the same security intuition appears repeatedly:

- commit before seeing verifier randomness;
- bind later responses to that commitment;
- use challenge unpredictability to make cheating difficult;
- exploit multiple inconsistent responses for extraction or soundness arguments.

### Companion experiment

Run:

```bash
python experiments/zero-knowledge/sigma/schnorr_sigma.py
```

It checks completeness and explicitly recovers the Schnorr witness from two accepting transcripts sharing the same commitment.
