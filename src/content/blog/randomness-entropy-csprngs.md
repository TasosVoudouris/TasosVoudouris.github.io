---
title: "Randomness in Cryptography: Entropy, CSPRNGs, and Operating-System Randomness"
description: "Distinguish entropy from pseudorandomness, explain OS CSPRNGs and entropy mixing, and identify the randomness properties cryptographic primitives actually require."
pubDate: "2025-05-21"
updatedDate: "2026-09-12"
topics:
- "Randomness & Entropy"
- "Cryptography Fundamentals"
- "Cryptographic Engineering"
tags:
- "entropy"
- "min-entropy"
- "csprng"
- "randomness"
- "operating-system"
- "nonce"
- "secrets"
difficulty: "Introductory"
series: "Cryptography Primer"
seriesOrder: 4
draft: false
---
Cryptography depends on values that an adversary cannot predict: private keys, nonces, IVs in schemes that require randomness, salts, challenges, blinding values, session identifiers, and protocol ephemeral secrets. When the randomness fails, mathematically sound cryptography can fail with it.

This article separates three ideas that are often mixed together:

1. **entropy** - uncertainty in a source,
2. **physical randomness** - measurements that inject fresh uncertainty into a system,
3. **cryptographically secure pseudorandomness** - deterministic expansion of a secret seed into a long unpredictable stream.

## 1. Randomness Is a Security Assumption

A random-looking value is not necessarily unpredictable.

For cryptography, the relevant question is usually not

> "Does this sequence pass a visual or statistical randomness test?"

but rather

> "Given everything the attacker knows, how well can the attacker predict the secret state or the next output?"

Statistical tests can detect some bad generators, but they do not prove cryptographic unpredictability.

## 2. Entropy: Shannon Entropy and Min-Entropy

For a discrete random variable $X$ with probabilities $p(x)$, Shannon entropy is

$$
H(X)=-\sum_x p(x)\log_2 p(x).
$$

It measures average information content.

Cryptographic extraction often cares more directly about **min-entropy**,

$$
H_\infty(X)=-\log_2\left(\max_x p(x)\right),
$$

because it captures the attacker's best single guess.

A fair eight-sided die has three bits of both Shannon entropy and min-entropy. A biased source may have less, but the amount is determined by the full probability distribution; it is not generally correct to say that "one biased bit means exactly one bit less entropy."

## 3. Physical Entropy Sources

Fresh entropy ultimately comes from phenomena that are difficult to predict precisely, such as:

- timing jitter,
- hardware random-number generators,
- oscillator noise,
- device and interrupt timing,
- dedicated physical sources such as avalanche or quantum noise.

The operating system collects measurements, conditions them, and uses them to seed or reseed its cryptographic random generator.

Raw physical measurements should not normally be consumed directly as cryptographic keys. They may be biased, correlated, or partially observable, so they are first processed by a conditioning/extraction mechanism.

## 4. Pseudorandomness

A CSPRNG is deterministic once its internal state is fixed. Given a secure seed, however, its outputs should be computationally indistinguishable from random to an efficient adversary who does not know that state.

That gives cryptography a powerful pattern:

$$
\text{small amount of high-quality entropy}
\rightarrow
\text{CSPRNG}
\rightarrow
\text{large amount of pseudorandom output}.
$$

The determinism is not a weakness; it is what makes the generator efficient and reproducible internally. The security requirement is that recovering or predicting the internal state remains infeasible.

## 5. Why Ordinary PRNGs Are Not Enough

The classic middle-square generator illustrates the problem. Starting from a seed, square it and take the middle digits as the next state. It can look irregular for a while but quickly falls into predictable cycles.

General-purpose generators such as the Mersenne Twister are far better statistically, yet they are still **not cryptographic generators**. Once enough output is observed, their internal state can be reconstructed and future outputs predicted.

For cryptographic code, use a cryptographic randomness API rather than a simulation-oriented PRNG.

In Python, for example:

```python
import secrets

key_material = secrets.token_bytes(32)
nonce = secrets.token_bytes(12)
uniform_field_element = secrets.randbelow(q)
```

The `secrets` module delegates to the operating system's cryptographic randomness facilities.

## 6. Operating-System Randomness

Modern operating systems maintain internal randomness state seeded from multiple sources and expose an API suitable for cryptographic applications.

On Linux, application code should normally use `getrandom()` or a high-level library that uses the kernel CSPRNG. Historical distinctions between `/dev/random` and `/dev/urandom` are often repeated without the modern kernel context; the important condition is that the kernel CSPRNG has been **properly initialized**.

Applications should not try to build their own entropy pool by concatenating timestamps, process identifiers, MAC addresses, or other low-entropy values.

## 7. Mixing Multiple Sources

Suppose several sources produce $x_1,\ldots,x_k$. A robust combiner tries to retain security when at least one source remains unknown to the attacker.

A simple conceptual model is

$$
s = H(\text{domain} \parallel x_1 \parallel \cdots \parallel x_k),
$$

where $H$ is used as a cryptographic conditioner.

The exact entropy of the result is not automatically the sum of the input entropies. Additivity requires independence assumptions, and correlated or adversarial sources need more careful extractor/combiner analysis.

The engineering objective is **hedging**: one weak source should not necessarily destroy the entire generator.

## 8. State Compromise, Forking, and Reseeding

A good system also asks what happens if the CSPRNG state is exposed.

Desirable properties include:

- **backtracking resistance**: learning the current state should not reveal old outputs;
- **prediction resistance / recovery**: after fresh entropy is mixed in, an attacker who knew an old state should lose the ability to predict new outputs;
- **fork safety**: cloned processes or virtual machines should not continue with identical random state indefinitely.

Reseeding is therefore not about a CSPRNG "running out of randomness." It is a defense against state compromise, implementation bugs, environmental failures, or conservative security engineering.

## 9. Randomness Requirements Differ by Primitive

Different values need different properties:

| Value | Typical requirement |
| --- | --- |
| Long-term private key | Uniform/unbiased secret generation |
| ECDSA/DSA nonce | Unique and unpredictable, or generated deterministically by a proven method |
| AES-GCM nonce | Uniqueness is critical; randomness is one way to achieve it |
| Password salt | Unique; secrecy is unnecessary |
| Challenge nonce | Freshness/unpredictability depending on protocol |
| One-time pad | Truly uniform key material as long as the message, used exactly once |

Calling every field "a random nonce" hides these distinctions.

## 10. Randomness Failures Become Cryptanalytic Failures

Weak randomness has caused real classes of failure:

- repeated signature nonces can expose signing keys;
- low-entropy key generation shrinks the attacker's search space;
- VM snapshots can clone generator state;
- deterministic session identifiers can enable impersonation;
- nonce reuse can catastrophically violate AEAD security.

The primitive may be implemented exactly as specified and still fail because the surrounding randomness contract was violated.

## 11. External Entropy and Lava-Lamp-Style Systems

Public demonstrations such as lava-lamp entropy systems are useful illustrations of **defense in depth**: a camera observes a difficult-to-model physical process, the measurements are conditioned, and the resulting material can be mixed with machine-local entropy.

The security does not come from "lava lamps are magical random generators." It comes from a carefully designed pipeline:

$$
\text{physical measurement}
\rightarrow
\text{conditioning}
\rightarrow
\text{authenticated delivery}
\rightarrow
\text{entropy mixing}
\rightarrow
\text{CSPRNG}.
$$

Each arrow has its own trust and bootstrap assumptions.

## 12. Practical Rule

For application code:

- use the operating-system CSPRNG through a reputable cryptographic library;
- do not invent a PRNG;
- distinguish uniqueness from unpredictability;
- use protocol-specified deterministic nonce generation where required;
- treat entropy initialization, VM cloning, and embedded-device startup as explicit security concerns;
- document what randomness each protocol value needs.

The next threshold-cryptography article asks a different question: not "how does one machine generate secure random bits?" but **"how can a network produce randomness that everyone can verify and no small coalition can predict or bias?"**
