---
title: "Pseudorandom Generators and Stream Ciphers: From Deterministic Expansion to Secure Keystreams"
description: "Build the security vocabulary for PRGs, CSPRNGs, keystream generators, stream ciphers, and nonce discipline before studying linear generators and modern ChaCha20."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Randomness & Entropy"
  - "Symmetric Cryptography"
  - "Cryptography Fundamentals"
  - "Cryptographic Engineering"
tags:
  - "prg"
  - "csprng"
  - "stream-cipher"
  - "keystream"
  - "nonce"
  - "pseudorandomness"
difficulty: "Introductory"
series: "Randomness & Stream Ciphers"
seriesOrder: 1
status: "Reviewed"
draft: false
---
A cryptographic random generator is usually **deterministic once its internal state is fixed**. The security goal is not to produce metaphysically random bits; it is to produce outputs that an efficient adversary cannot distinguish from the appropriate random distribution or predict well enough to violate the surrounding protocol.

The [randomness primer](/blog/randomness-entropy-csprngs/) discusses entropy sources, operating-system randomness, and CSPRNG seeding. This series starts one layer lower: how deterministic generators and stream ciphers are constructed, how linear structure becomes exploitable, and why modern designs look very different from LCGs, LFSRs, and RC4.

## PRG model

A pseudorandom generator expands a shorter seed into a longer string:

$$
G:\{0,1\}^{s}\rightarrow\{0,1\}^{\ell},\qquad \ell>s.
$$

Because the range of $G$ contains at most $2^s$ strings, its output cannot be information-theoretically uniform over $\{0,1\}^{\ell}$. Security is computational: no efficient distinguisher should separate $G(U_s)$ from $U_\ell$ with meaningful advantage.

This immediately separates two ideas that were mixed in several of the old notes:

- **statistical-looking output** is not enough;
- passing frequency or autocorrelation tests is not a proof of cryptographic pseudorandomness;
- a generator can pass many statistical tests while remaining fully predictable from a small amount of state information.

## CSPRNG versus ordinary PRNG

An ordinary simulation PRNG may optimize for speed, period, reproducibility, or statistical quality. A **cryptographically secure PRNG** additionally needs resistance to state recovery and output prediction under the threat model of the application.

A practical CSPRNG is better thought of as a stateful construction

$$
(S_i,\text{input}_i)\longmapsto(S_{i+1},\text{output}_i),
$$

with explicit rules for seeding, reseeding, state compromise, and domain separation. The operating system normally provides this layer; applications should not invent it from LCGs, timestamps, or ad-hoc hashes.

## From a generator to a stream cipher

The idealized stream-cipher equation is

$$
C=P\oplus KS,
$$

where $KS$ is a keystream derived from a secret key and, in modern designs, a nonce/counter context.

A useful abstraction is

$$
KS=G(K,N,\text{counter}),
$$

where $K$ is secret and $N$ is normally public but must satisfy the construction's uniqueness requirements.

Decryption is the same XOR operation:

$$
P=C\oplus KS.
$$

The algebra is intentionally simple. Security therefore lives almost entirely in the keystream generator and in **never repeating the same keystream under different plaintexts**.

## Keystream reuse is structural failure

If the same keystream encrypts two plaintexts,

$$
C_1=P_1\oplus KS,\qquad C_2=P_2\oplus KS,
$$

then

$$
C_1\oplus C_2=P_1\oplus P_2.
$$

The keystream disappears. This is the same failure studied in [One-Time Pads, Stream Ciphers, and the Catastrophe of Key/Nonce Reuse](/blog/otp-stream-cipher-key-reuse/).

For a nonce-based stream cipher, a nonce is generally **not a secret**. Its security role is usually to keep the generated keystream distinct under a fixed key. The exact contract is construction-specific.

## Next-bit unpredictability

A useful intuition for a secure generator is that observing previous output should not make the next output bit predictably easier than guessing. This intuition can be formalized and is tightly connected to pseudorandomness for standard PRG definitions.

The next chapters deliberately study generators that fail this goal:

1. an LCG leaks its affine recurrence;
2. an LFSR exposes linear equations over $\mathbb F_2$;
3. combining LFSRs badly can leave exploitable correlations;
4. RC4 has structural keystream biases;
5. ChaCha20 shows the modern ARX approach;
6. Dual_EC_DRBG demonstrates that a generator can have respectable-looking mathematics and still fail catastrophically because of parameter trust.

## What a statistical test can and cannot say

Suppose a bitstream has approximately equal zeros and ones. That rules out an extremely bad generator that outputs only zeros. It does **not** rule out

$$
s_{i+1}=a s_i+c\pmod m,
$$

or any other efficiently recoverable recurrence.

Cryptographic evaluation therefore asks stronger questions:

- Can internal state be recovered?
- Can future output be predicted?
- Does partial state compromise expose past output?
- Are there correlations, biases, or short cycles?
- Are seeds and nonces handled correctly?
- Does the design have a meaningful security argument against an explicit adversary?

Those questions are the organizing principle for the rest of the series.

## References

- NIST SP 800-90A Rev. 1, *Recommendation for Random Number Generation Using Deterministic Random Bit Generators*.
- RFC 8439, *ChaCha20 and Poly1305 for IETF Protocols*.
- Goldreich, *Foundations of Cryptography*, for computational indistinguishability and pseudorandomness.
