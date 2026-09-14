---
title: "Distributed Randomness Beacons: DKG, Threshold BLS, and Public Verifiability"
description: "Build the conceptual path from threshold key generation to publicly verifiable randomness, with emphasis on unpredictability, bias resistance, uniqueness, and liveness."
pubDate: "2025-05-21"
updatedDate: "2026-09-12"
topics:
- "Randomness & Entropy"
- "Threshold Cryptography"
- "Public-Key Cryptography"
- "Cryptographic Engineering"
tags:
- "distributed-randomness"
- "randomness-beacon"
- "threshold-bls"
- "drand"
- "dkg"
- "public-verifiability"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 27
draft: false
---
Some applications need more than local randomness. A lottery, committee election, consensus protocol, or public sortition may require a random value that is:

- unpredictable before the designated round,
- publicly verifiable afterward,
- difficult for one participant to bias,
- available even if some participants fail.

That is the purpose of a **distributed randomness beacon**.

## 1. From Local Randomness to Public Randomness

A local CSPRNG can produce excellent random bits for one machine, but external observers cannot automatically verify how those bits were chosen.

A public beacon instead produces an output

$$
R_r
$$

for round $r$ together with evidence that anyone can verify.

Typical security goals include:

- **unpredictability** before enough honest protocol contributions exist;
- **bias resistance / unbiasability** so that an adversary cannot choose among many candidate outputs;
- **public verifiability** of the final result;
- **liveness** despite some offline or malicious parties;
- **consistency** so honest observers agree on the same round output.

## 2. Why "Everyone Sends a Random Number" Is Not Enough

A naive protocol might ask every participant to publish a random value and XOR them.

That can work under strong commit-then-reveal assumptions, but a last mover who sees the other contributions before choosing whether to reveal may gain influence over the final output.

Distributed randomness therefore needs protocol structure that prevents **selective abort** and **last-revealer bias** from becoming a choice over the beacon output.

## 3. Threshold Cryptography as the Core Tool

A common beacon architecture uses a $(t,n)$ threshold signature scheme.

During setup, the parties obtain shares of one signing key:

$$
s_1,\ldots,s_n,
$$

with public key $Y$.

For beacon round $r$, every participant signs the same deterministic round message, for example

$$
m_r = H(\text{domain}\parallel r\parallel R_{r-1}).
$$

Once enough valid signature shares are available, they combine into one group signature $\sigma_r$.

The beacon output is derived as

$$
R_r = H'(\sigma_r).
$$

If the threshold signature is **unique** for a fixed public key and message, the combiner does not get to choose among many valid final signatures. That uniqueness is an important source of bias resistance.

## 4. DKG Removes the Trusted Setup

A threshold beacon is much less compelling if one setup server generated the signing key and distributed the shares.

This is why a DKG appears before the beacon starts:

$$
\text{DKG}
\rightarrow
\text{shared signing key}
\rightarrow
\text{threshold signature each round}
\rightarrow
\text{hash to beacon output}.
$$

The DKG ensures that no single participant starts with the whole private signing key.

## 5. Threshold BLS as a Natural Beacon Primitive

BLS signatures are particularly attractive for beacon designs because signature shares and the final signature have clean algebraic structure.

Let the group secret be $x$ and the public key be

$$
Y=g^x.
$$

A BLS signature on message $m$ is conceptually

$$
\sigma = H(m)^x.
$$

If $x$ is Shamir-shared, participant $P_i$ can compute a partial signature

$$
\sigma_i = H(m)^{x_i}.
$$

For an authorized index set $S$, the shares combine using Lagrange coefficients $\lambda_i$:

$$
\sigma
=
\prod_{i\in S}\sigma_i^{\lambda_i}
=
H(m)^x.
$$

The final signature verifies under the ordinary group public key.

This is the bridge from secret sharing to publicly verifiable randomness: the threshold signature is both a cryptographic authorization object and an unpredictable round value before the threshold is reached.

## 6. What the Corruption Threshold Means

It is too simplistic to say "if fewer than $t$ parties are corrupt, the result is random; otherwise it is not."

The exact statement depends on the beacon and threshold-signature security model.

Typically:

- a coalition below the signing threshold cannot compute the next threshold signature by itself;
- malicious parties may withhold shares and attack **liveness**;
- if enough parties collude to meet the threshold early, they may learn the next beacon value before the public does;
- adaptive corruption, network scheduling, and DKG security can change the bound;
- uniqueness prevents a combiner from choosing among multiple final signatures, but it does not by itself solve every availability problem.

Threshold selection is therefore a joint security-and-liveness decision.

## 7. Chaining Rounds

Many beacons include the previous output in the next message:

$$
m_r = H(r\parallel R_{r-1}).
$$

This creates an auditable sequence. An observer can verify:

1. the round identifier,
2. the threshold signature,
3. the hash-derived output,
4. the link to the previous round.

A chain does not eliminate the need for secure setup, but it makes equivocation and history inspection easier to reason about.

## 8. drand-Style Architecture

A drand-style network illustrates the overall design:

1. a committee runs a DKG;
2. each node receives one threshold signing share;
3. at every round, nodes sign the round message;
4. enough shares are collected and combined;
5. the final threshold signature is published;
6. anyone verifies the signature and derives the randomness.

The verifier does not need to trust the combiner. The proof is the signature itself.

## 9. Why This Is Different from a VRF

A verifiable random function (VRF) lets **one secret-key holder** compute a pseudorandom output with a proof.

A distributed randomness beacon uses **multiple parties** so that no one participant controls the secret key or release of the output.

Threshold VRFs and distributed VRF constructions blur this boundary, but the trust model remains the important distinction.

## 10. Failure Modes

A production beacon must analyze:

- DKG failure or biased key generation;
- insufficient online participants;
- denial of service against share collection;
- adaptive corruption;
- weak domain separation between rounds/applications;
- replay of old signature shares;
- inconsistent committee membership;
- incorrect BLS public-key validation or proof-of-possession rules;
- dependence on a single aggregator or relay.

The randomness value may be compact, but the protocol producing it is a distributed system.

## 11. Where Distributed Randomness Is Useful

Public randomness beacons can support:

- committee or leader election,
- lotteries and auditable draws,
- randomized consensus roles,
- public sortition,
- protocol challenges,
- delayed unpredictability for decentralized applications.

The beacon should not be treated as a substitute for every local CSPRNG. It solves the narrower problem of **shared, auditable randomness with a distributed trust model**.

## 12. Final Connection

The full path developed in this series is now visible:

$$
\text{additive sharing}
\rightarrow
\text{Shamir}
\rightarrow
\text{packed/robust sharing}
\rightarrow
\text{VSS}
\rightarrow
\text{DKG}
\rightarrow
\text{threshold signatures}
\rightarrow
\text{distributed randomness}.
$$

What began as polynomial interpolation becomes a mechanism for removing a trusted dealer and, eventually, for producing public randomness that an entire network can verify.
