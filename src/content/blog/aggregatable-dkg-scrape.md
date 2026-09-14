---
title: "Aggregatable DKG and SCRAPE-Style PVSS: A Scalability Research Note"
description: "Study how publicly verifiable secret sharing and transcript aggregation can reduce DKG communication while preserving public consistency checks."
pubDate: "2025-05-20"
updatedDate: "2026-09-12"
topics:
- "Threshold Cryptography"
- "Secret Sharing"
- "MPC"
- "Cryptographic Engineering"
tags:
- "aggregatable-dkg"
- "scrape"
- "pvss"
- "dkg"
- "public-verifiability"
- "distributed-systems"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 15
draft: false
---
The previous article used a classic parallel-VSS pattern: every participant behaves as a dealer, distributes private shares, publishes commitments, and participates in complaint handling. That design is easy to reason about, but its all-to-all communication becomes expensive when the committee grows.

This research note studies the idea behind **aggregatable distributed key generation**: make each dealer's sharing transcript publicly verifiable and design the transcript representation so that many valid contributions can be combined efficiently.

The notes in this article describe a **SCRAPE-style PVSS / aggregatable-DKG direction**. Exact resilience bounds, gossip rules, and termination conditions depend on the concrete protocol being implemented; they should be taken from that protocol's security proof rather than generalized from the high-level pattern.

## 1. Why Publicly Verifiable Secret Sharing?

Ordinary VSS lets the recipients verify that their own shares are consistent. **Publicly Verifiable Secret Sharing (PVSS)** goes further: an external observer can verify, from public data, that a dealer distributed a valid sharing, while the actual share intended for party $P_i$ remains recoverable only by $P_i$.

Conceptually, a PVSS transcript contains:

- commitments to the secret-sharing polynomial,
- encrypted or otherwise recipient-bound share material,
- proofs that the encrypted shares correspond to the committed polynomial,
- enough public information for anyone to verify consistency.

That changes the scaling story because verification no longer has to depend entirely on pairwise complaint rounds.

## 2. SCRAPE-Style PVSS

SCRAPE ("Scalable Randomness Attested by Public Entities") is a useful reference point for scalable publicly verifiable sharing. At a high level, the dealer creates a sharing and public proof material that allows the network to test whether the sharing lies in the appropriate Reed-Solomon/codeword structure.

The important architectural properties are:

1. **Public verifiability** - verification does not require access to the plaintext secret.
2. **Recipient privacy** - each party learns only its own share.
3. **Compact verification logic** - the verifier checks algebraic consistency rather than replaying an interactive complaint procedure.
4. **Composability of transcripts** - when the underlying representation is homomorphic, valid contributions can be combined.

The exact algebra used by a specific SCRAPE/PVSS instantiation matters; "PVSS" is a family of constructions rather than one fixed wire format.

## 3. From One PVSS Transcript to a DKG

Suppose each participant $P_i$ publishes a valid transcript $\tau_i$ for a secret contribution $s_i$. If the sharing and commitment mechanisms are homomorphic, an aggregate transcript can represent

$$
s = \sum_i s_i
$$

without revealing the individual $s_i$ values.

At the share level, party $P_j$ obtains

$$
s_j = \sum_i s_{i,j},
$$

and at the public-key level, multiplicative commitments combine as

$$
Y = \prod_i Y_i
= g^{\sum_i s_i}.
$$

This is the same algebraic idea as the classic parallel-VSS DKG, but the verification interface is now public and designed for aggregation.

## 4. Transcript Validity

An aggregatable transcript must make several facts checkable:

- each included dealer contribution is individually valid;
- ciphertext/share commitments are consistent with the polynomial commitment;
- the aggregation operation preserves validity;
- a dealer is not counted twice;
- all honest participants derive the same aggregate dealer set;
- the public key corresponds to the same aggregate that generated the secret shares.

A practical transcript therefore needs explicit participant identifiers or a bitmap/set representation, commitment material, proof objects, and a deterministic aggregation rule.

## 5. Signatures of Knowledge and Proof of Possession

Whenever public keys or commitment elements are accepted from arbitrary participants, the protocol must defend against malformed-key and rogue-key behavior.

A common technique is a **proof or signature of knowledge** showing that a participant knows the discrete logarithm corresponding to a published group element. The exact proof statement must be bound to the participant identity and transcript context.

This is conceptually similar to the proof-of-possession requirement that appears in some BLS aggregation deployments: algebraic aggregation is powerful, but it also creates new ways for maliciously chosen public keys to cancel or absorb honest contributions if registration is underspecified.

## 6. Aggregation Is Not Consensus

It is useful to separate two problems:

**Cryptographic aggregation** answers:

> If these transcripts are valid, can they be combined into one valid transcript/key?

**Agreement/consensus** answers:

> Which set of transcripts will all honest parties use?

A DKG protocol needs both. Gossip can reduce communication, but the mechanism that makes honest parties converge on the same final participant set is part of the protocol's distributed-systems proof. It should not be replaced by an arbitrary local tie-break rule.

## 7. Complexity

The motivation for aggregatable DKG is to avoid naive quadratic dissemination and verification where possible. Whether a concrete construction reaches $O(n\log n)$, $O(n\log^2 n)$, or another bound depends on:

- the PVSS proof size,
- how transcripts are disseminated,
- whether proofs batch,
- the network model,
- the probability of faults,
- the cost assigned to group operations versus transmitted bytes.

For that reason, the companion research code and any benchmark should report **both computation and communication**, and should state the exact protocol variant being measured.

## 8. Faults and Recovery

PVSS can make recovery easier because a party may be able to obtain an encrypted share from public transcript data and decrypt it after rejoining. That does not automatically solve every recovery problem:

- the party still needs its decryption key;
- the transcript must remain available and authenticated;
- adaptive corruption may change the security argument;
- stale transcripts must not be mixed across epochs;
- resharing/proactive refresh needs separate protocol logic.

## 9. Why This Matters

The progression is now:

$$
\text{SSS}
\rightarrow
\text{VSS}
\rightarrow
\text{PVSS}
\rightarrow
\text{DKG}
\rightarrow
\text{aggregatable DKG}.
$$

Each step removes or weakens a trust/communication bottleneck, but each step also adds proof obligations. The main engineering lesson is that scalability cannot be analyzed independently of the adversary model.

### Further Reading

- P. Feldman, *A Practical Scheme for Non-interactive Verifiable Secret Sharing*.
- I. Cascudo and B. David, *SCRAPE: Scalable Randomness Attested by Public Entities*.
- Classic and modern DKG literature on bias resistance, public verifiability, and communication-efficient threshold key generation.
