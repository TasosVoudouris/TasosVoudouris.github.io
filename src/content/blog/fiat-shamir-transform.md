---
title: "The Fiat–Shamir Transform: From Public-Coin Interaction to Non-Interactive Arguments"
description: "Derive the Fiat–Shamir transform from a Sigma protocol, then study transcript hashing, domain separation, statement binding, the random-oracle model, and the implementation mistakes that destroy soundness."
pubDate: "2025-02-25"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Hash Functions"
  - "Cryptographic Engineering"
tags:
  - "fiat-shamir"
  - "random-oracle"
  - "transcript"
  - "domain-separation"
  - "non-interactive"
  - "sigma-protocol"
difficulty: "Advanced"
status: "Validated"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 3
sourcePath: "experiments/zero-knowledge/fiat-shamir"
draft: false
---
Interactive public-coin proofs obtain security from verifier randomness that the prover cannot predict before committing to its first message. The **Fiat–Shamir transform** replaces that verifier message with a hash of the transcript.

For the Schnorr Sigma protocol, instead of receiving a random $c$ from the verifier, the prover computes

$$
c=H(\text{domain}\,\|\,\text{statement}\,\|\,t\,\|\,\text{context}).
$$

The prover then sends $(t,z)$, where

$$
z=r+cx\pmod q.
$$

The verifier recomputes $c$ from exactly the same transcript bytes and checks

$$
g^z=t y^c.
$$

Interaction has disappeared, but the security model has changed.

## 1. Why hashing can replace a random challenge

In the interactive protocol, the prover must choose $t$ before seeing $c$. If the hash function is modeled as a random oracle, then a prover that has committed to $t$ cannot freely choose the resulting challenge.

The transform therefore tries to preserve the "commit first, challenge later" logic using deterministic public hashing.

This is a **compiler idea**, not a magical property of SHA-256. Security proofs for Fiat–Shamir depend on the underlying protocol, the hash/oracle model, the statement being proven, and the exact security notion.

## 2. What must be hashed

A dangerous implementation pattern is

```text
c = H(t)
```

when the real security context contains much more information.

A robust transcript normally binds at least:

- protocol/domain identifier;
- version or parameter set;
- public statement;
- prover commitment(s);
- prior transcript messages;
- relevant public keys or session context;
- an unambiguous encoding of lengths/types.

If the statement is omitted, a proof may be replayable or malleable across statements. If protocol separation is omitted, the same hash transcript may be interpreted by two different protocols.

## 3. Domain separation is part of the protocol

Use an explicit tag such as

```text
CryptoCave/SchnorrPoK/v1
```

rather than assuming that "nobody else will hash the same bytes."

Domain separation prevents accidental cross-protocol challenge reuse and makes transcript definitions auditable.

The companion implementation includes such a tag and hashes the public statement together with the commitment.

## 4. Serialization must be canonical

Cryptographic transcript hashing is byte-level protocol design. The values

```text
(1, 23)
```

must not collide with a different tuple because of ambiguous string concatenation.

Production systems therefore require canonical encodings with fixed-width fields, length prefixes, or a formally specified transcript API.

This is also why simply translating mathematical pseudocode into `str(value)` calls is risky.

## 5. Fiat–Shamir does not repair a bad interactive protocol

If the original protocol lacks the needed soundness/knowledge property, hashing the challenge does not manufacture it.

Likewise, Fiat–Shamir does not automatically add zero knowledge. The non-interactive protocol must still preserve the appropriate privacy definition, often requiring prover randomization or masking beyond the challenge transform itself.

## 6. Random-oracle reasoning versus the standard model

The classical transform is commonly analyzed by treating the hash as a **random oracle**: an ideal random function that all parties can query.

A real hash function is a deterministic algorithm, not a literal random oracle. The random-oracle model is therefore an idealized proof framework.

There is no unrestricted theorem saying that replacing verifier randomness with any collision-resistant hash makes every public-coin proof secure in the standard model.

That qualification matters because modern SNARKs and STARKs use Fiat–Shamir extensively to derive multiple challenges from long transcripts.

## 7. Rewinding, programmability, and extraction

In an interactive Sigma protocol, special-soundness extraction can conceptually rewind a prover and ask a second challenge for the same first message.

In the Fiat–Shamir setting, the challenge is determined by a hash query. Security proofs need techniques that reason about or program the random oracle so that two related transcripts can be obtained or otherwise show knowledge soundness.

The proof details depend heavily on the protocol. This is one reason "Fiat–Shamirized" should not be treated as a complete security argument by itself.

## 8. Quantum caveat

When adversaries can query the random oracle in quantum superposition, the classical random-oracle proof does not transfer automatically. Security in the **quantum random-oracle model (QROM)** requires dedicated analysis.

This does not mean Fiat–Shamir is unusable in post-quantum protocols. It means the proof theorem must match the adversary model.

## 9. Nonce reuse remains catastrophic

For Schnorr-style transcripts,

$$
z=r+cx.
$$

If the same nonce $r$ is reused for different challenges, the secret is recovered:

$$
x=(z_1-z_2)(c_1-c_2)^{-1}\pmod q.
$$

Fiat–Shamir removes the verifier network message; it does not remove the need for safe prover randomness or deterministic nonce-generation discipline.

## 10. Modern transcript systems

Large proof systems derive many challenges:

$$
\beta,\gamma,\alpha,\zeta,v,u,\ldots
$$

A good transcript abstraction absorbs every prior commitment/evaluation in a specified order and derives each challenge with explicit domain separation. Changing message order changes the protocol.

This becomes central in PLONK and in non-interactive STARKs.

### Companion experiment

```bash
python experiments/zero-knowledge/fiat-shamir/schnorr_fiat_shamir.py
```

The toy implementation demonstrates statement binding, transcript hashing, successful verification, and rejection after statement/response tampering.

### Historical reference

A. Fiat and A. Shamir, *How to Prove Yourself: Practical Solutions to Identification and Signature Problems*, CRYPTO 1986.
