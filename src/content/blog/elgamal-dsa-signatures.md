---
title: "Digital Signatures III: ElGamal and DSA — Discrete-Log Signatures and the Nonce Equation"
description: "From the ElGamal signature idea to DSA, with the signing and verification equations, nonce requirements, correctness reasoning, and DSA's current legacy status."
pubDate: "2025-05-08"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Public-Key Cryptography"
  - "Discrete Logarithms"
  - "Cryptanalysis"
tags:
  - "elgamal-signature"
  - "dsa"
  - "nonce"
  - "discrete-logarithm"
difficulty: "Intermediate"
series: "Digital Signatures"
seriesOrder: 3
status: "Reviewed"
draft: false
---
The ElGamal signature family is historically important because it makes the core discrete-log signature pattern visible: a long-term secret key is combined with a fresh per-signature nonce, and verification reconstructs a group relation without learning either secret.

DSA can be understood as a standardized descendant of this idea operating in a prime-order subgroup.

## Finite-field setup

Choose primes $p$ and $q$ with

$$
q \mid p-1,
$$

and let $g$ generate a subgroup of order $q$ in $\mathbb{Z}_p^*$. The signer chooses

$$
x \in \{1,\ldots,q-1\}
$$

and publishes

$$
y=g^x \bmod p.
$$

The discrete logarithm problem protects $x$.

## DSA signing equation

Let $z$ be the message digest mapped to the required integer width. For each signature choose a fresh nonzero nonce

$$
k \in \mathbb{Z}_q^*.
$$

Then compute

$$
r=(g^k \bmod p)\bmod q,
$$

and

$$
s=k^{-1}(z+xr)\bmod q.
$$

If either $r=0$ or $s=0$, a new nonce is required.

The signature is $(r,s)$.

## Verification

The verifier computes

$$
w=s^{-1}\bmod q,
$$

$$
u_1=zw\bmod q,
\qquad
u_2=rw\bmod q,
$$

and finally

$$
v=((g^{u_1}y^{u_2}\bmod p)\bmod q).
$$

The signature is accepted when

$$
v=r.
$$

## Why the equation works

From signing,

$$
s=k^{-1}(z+xr) \pmod q,
$$

so

$$
s^{-1}(z+xr)\equiv k\pmod q.
$$

The verifier exponent is therefore

$$
u_1+xu_2 \equiv zw+xrw \equiv k \pmod q.
$$

Because $y=g^x$,

$$
g^{u_1}y^{u_2}=g^{u_1+xu_2}=g^k
$$

inside the subgroup, yielding the same $r$ value after reduction.

## The nonce is as sensitive as the private key

The equation for $s$ can be rearranged:

$$
x \equiv (sk-z)r^{-1}\pmod q.
$$

Therefore, anyone who learns $k$ from one signature can recover the long-term private key.

Even worse, if the same $k$ is reused on two different messages, the two equations can be subtracted to recover $k$, and then $x$.

This is the central implementation lesson that carries directly into ECDSA.

## Deterministic nonces

RFC 6979 defines a deterministic method for deriving the nonce from the secret key and message hash for DSA and ECDSA. The resulting signatures remain compatible with ordinary verification while avoiding dependence on fresh external randomness during each signature operation.

Key generation still needs secure randomness.

## DSA's modern status

DSA is historically useful and still worth studying because its equations explain ECDSA. It is not, however, a current choice for new U.S. federal signature generation.

FIPS 186-5 no longer approves DSA for generating new digital signatures; it retains DSA only for verification of legacy signatures. Current FIPS 186-5 signature-generation families are RSA, ECDSA, and EdDSA.

That distinction was missing from the older CryptoCave notes and is important in a modern reference.

## ElGamal signatures vs ElGamal encryption

ElGamal encryption and ElGamal signatures are related by their reliance on discrete-log groups, but they are different primitives with different equations. A system should not infer that because it has an ElGamal encryption implementation it automatically has a secure signature scheme.

## References

- Taher ElGamal, **A Public Key Cryptosystem and a Signature Scheme Based on Discrete Logarithms**, 1985.
- NIST FIPS 186-5, **Digital Signature Standard**, 2023.
- RFC 6979, **Deterministic Usage of DSA and ECDSA**.
