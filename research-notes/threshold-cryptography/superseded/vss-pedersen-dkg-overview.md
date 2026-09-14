---
title: "From Verifiable Secret Sharing to Pedersen-Style DKG"
description: "Remove the trusted dealer step by step: Feldman VSS, parallel polynomial sharing, qualification, group public-key derivation, and the assumptions behind classic DKG."
pubDate: "2025-05-20"
updatedDate: "2026-09-12"
topics:
- "Threshold Cryptography"
- "Secret Sharing"
- "MPC"
- "Public-Key Cryptography"
tags:
- "vss"
- "feldman-vss"
- "distributed-key-generation"
- "dkg"
- "pedersen-dkg"
- "threshold-cryptography"
difficulty: "Advanced"
series: "Secret Sharing & Threshold Cryptography"
seriesOrder: 8
draft: false
---
A trusted dealer is convenient, but it is also a concentration of power. If one machine generates the long-term private key, then that machine can learn the entire secret, bias its generation, lose it, or become unavailable. Threshold cryptography tries to remove that single point of failure by ensuring that no participant ever needs to hold the complete private key.

The path from ordinary secret sharing to a dealerless key is:

$$
\text{secret sharing}
\;\longrightarrow\;
\text{verifiable secret sharing}
\;\longrightarrow\;
\text{distributed key generation}.
$$

This article develops that transition and then presents a classic **Pedersen-style DKG** based on parties running verifiable sharing in parallel.

## 1. Threshold Cryptography and the Dealer Problem

Suppose a private key $s$ is shared among $n$ participants. In a threshold signature or threshold-decryption protocol, participant $P_i$ uses only its share $s_i$ to compute a partial result. A combiner collects sufficiently many valid partial results and derives the final signature or decryption output.

The crucial point is that the full key need not be reconstructed during normal operation.

That still leaves a setup question:

> Who generated the original secret $s$?

If a single dealer chose $s$ and then shared it, the system has distributed **storage** but not distributed **key generation**. The dealer once knew the complete key.

## 2. From Shamir Sharing to Verifiable Secret Sharing

Basic Shamir sharing assumes that the dealer distributes evaluations of one degree-$t$ polynomial

$$
f(x)=a_0+a_1x+\cdots+a_t x^t,
$$

where the secret is $a_0=f(0)$.

A malicious dealer could instead send inconsistent values to different parties. To detect that behavior, a verifiable secret-sharing protocol publishes commitments to the polynomial.

A classic example is Feldman VSS. Let $\mathbb{G}$ be a group of prime order $q$ with generator $g$. The dealer publishes

$$
F_j=g^{a_j},\qquad j=0,\ldots,t.
$$

Party $P_i$, after receiving the private share $s_i=f(i)$, checks

$$
g^{s_i}
\stackrel{?}{=}
\prod_{j=0}^{t}F_j^{\,i^j}.
$$

The equality follows directly from the polynomial:

$$
g^{f(i)}
=
g^{\sum_j a_j i^j}
=
\prod_j g^{a_j i^j}.
$$

The commitments therefore bind the dealer to one polynomial, assuming the discrete-log problem is hard in $\mathbb{G}$.

### A subtle point about Feldman commitments

Feldman VSS provides public consistency checking, but its commitments are **not information-theoretically hiding**. In particular, $F_0=g^{a_0}$ exposes the public group element corresponding to the shared secret. That is often exactly what a DKG wants because it becomes a public key, but it is different from a hiding commitment.

## 3. Removing the Dealer

A DKG removes the distinguished dealer by having **every participant act as a dealer**.

For parties $P_1,\ldots,P_n$:

1. each $P_i$ samples its own random degree-$t$ polynomial $f_i$;
2. each $P_i$ verifiably shares evaluations of $f_i$ with the other parties;
3. invalid dealers are excluded according to the complaint/qualification rules;
4. every surviving dealer contributes to one aggregate polynomial

$$
F(x)=\sum_{i\in\mathcal{Q}} f_i(x),
$$

where $\mathcal{Q}$ is the qualified dealer set.

The distributed secret is

$$
s=F(0)=\sum_{i\in\mathcal{Q}} f_i(0),
$$

while party $P_j$ holds only

$$
s_j=F(j)=\sum_{i\in\mathcal{Q}} f_i(j).
$$

No honest party needs to reconstruct $s$.

## 4. Pedersen-Style Parallel VSS

For each dealer $P_i$, write

$$
f_i(x)=\sum_{k=0}^{t} a_{i,k}x^k.
$$

The dealer broadcasts commitments

$$
C_{i,k}=g^{a_{i,k}}
$$

and privately sends

$$
s_{i,j}=f_i(j)
$$

to participant $P_j$.

Participant $P_j$ verifies

$$
g^{s_{i,j}}
\stackrel{?}{=}
\prod_{k=0}^{t} C_{i,k}^{\,j^k}.
$$

If the check fails, the protocol enters a complaint procedure. The exact complaint, reveal, timeout, and disqualification rules are part of the DKG specification and must be analyzed together with the network model; they are not interchangeable implementation details.

After the qualified set $\mathcal{Q}$ is fixed, participant $P_j$ computes its final secret share

$$
s_j=\sum_{i\in\mathcal{Q}} s_{i,j}\pmod q.
$$

The corresponding group public key is

$$
Y=g^s
=\prod_{i\in\mathcal{Q}} g^{f_i(0)}
=\prod_{i\in\mathcal{Q}} C_{i,0}.
$$

This is the central DKG invariant: the parties obtain shares of a secret exponent that nobody had to construct in one place, while everyone can derive the same public key.

## 5. Reconstruction Versus Threshold Use

Because $F(x)$ has degree at most $t$, any $t+1$ valid evaluations reconstruct $F$ and therefore $s=F(0)$.

In a real threshold-signature or threshold-decryption system, however, reconstructing $s$ is normally **not** the operational goal. The parties instead use their $s_j$ values to compute partial signatures or decryptions. Reconstructing the long-term private key defeats much of the reason for using threshold cryptography in the first place.

## 6. Network and Adversary Assumptions

A DKG theorem is meaningful only together with its assumptions:

- How many parties may be Byzantine?
- Is the adversary static or adaptive?
- Is the network synchronous, partially synchronous, or asynchronous?
- Are channels authenticated?
- Are private channels available?
- Can an adversary rush after seeing honest messages?
- What happens when parties abort?

Classic complaint-based DKGs are commonly presented in a synchronous setting with a threshold below half of the participants. Other DKG constructions target different resilience bounds and communication models.

Therefore, a statement such as "$n\ge 2t+1$" should be read as a property of a particular protocol/security model, **not as a universal law of DKG**.

## 7. Bias and the Difference Between Correctness and Uniformity

There is another subtle issue: producing a consistent shared key is not automatically the same as proving that the resulting public key is distributed exactly as an honestly sampled random key.

Classic DKG constructions were refined in later work to address adversarial influence and bias in the generated key. This distinction matters whenever the security proof of the downstream signature or encryption scheme assumes a correctly distributed secret key.

The lesson is broader than DKG:

> "Nobody learns the secret" and "the secret has the right distribution" are separate properties.

## 8. State at the End of DKG

After a successful run:

| Object | Who knows it? | Purpose |
| --- | --- | --- |
| Group public key $Y=g^s$ | Everyone | Verification/encryption |
| Final share $s_j=F(j)$ | Only $P_j$ | Threshold computation |
| Full secret $s=F(0)$ | Ideally nobody | Long-term private key |
| Polynomial commitments | Public | Consistency/verification |
| Qualification transcript | Public or protocol-visible | Agreement on accepted dealers |

This is the architecture that later supports threshold signatures, threshold decryption, distributed randomness, and proactive key-management systems.

## 9. Where We Go Next

The parallel-VSS construction is conceptually clean, but naive all-to-all sharing and verification becomes expensive at large $n$. The next article studies **publicly verifiable and aggregatable sharing**, using SCRAPE-style PVSS as the bridge toward more scalable DKG designs.

### Further Reading

- A. Shamir, *How to Share a Secret* (1979).
- P. Feldman, *A Practical Scheme for Non-interactive Verifiable Secret Sharing* (1987).
- T. P. Pedersen, *A Threshold Cryptosystem without a Trusted Party* (1991).
- R. Gennaro, S. Jarecki, H. Krawczyk, and T. Rabin, *Secure Distributed Key Generation for Discrete-Log Based Cryptosystems* (1999).
