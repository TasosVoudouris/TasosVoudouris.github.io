---
title: "Digital Signatures V: ECDSA Nonce Reuse, Bias, and Verification Failures"
description: "Why ECDSA's per-signature nonce is effectively secret-key material, how nonce reuse recovers the private key, and which validation mistakes belong to the surrounding protocol rather than the core equation."
pubDate: "2025-03-19"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Cryptanalysis"
  - "Implementation Security"
  - "Elliptic-Curve Cryptography"
tags:
  - "ecdsa"
  - "nonce-reuse"
  - "biased-nonce"
  - "rfc6979"
  - "curve-validation"
difficulty: "Advanced"
series: "Digital Signatures"
seriesOrder: 5
status: "Validated"
sourcePath: "experiments/digital-signatures"
draft: false
---
ECDSA has a striking implementation property: one ephemeral scalar $k$ is used for one signature, but a failure in that one scalar can reveal the permanent private key $d$.

That makes nonce generation part of the security boundary of the signing key.

## Start from the signing equation

For a message digest integer $z$,

$$
s=k^{-1}(z+rd)\pmod n.
$$

Multiply by $k$:

$$
sk\equiv z+rd\pmod n.
$$

Therefore, if $k$ is known,

$$
d\equiv (sk-z)r^{-1}\pmod n.
$$

One leaked nonce is enough.

## Reusing a nonce on two messages

Suppose the same nonce $k$ signs two different digests $z_1$ and $z_2$. Because $R=kG$ is the same, both signatures have the same $r$:

$$
s_1=k^{-1}(z_1+rd)\pmod n,
$$

$$
s_2=k^{-1}(z_2+rd)\pmod n.
$$

Subtract:

$$
s_1-s_2=k^{-1}(z_1-z_2)\pmod n.
$$

Hence

$$
k=(z_1-z_2)(s_1-s_2)^{-1}\pmod n.
$$

Once $k$ is recovered,

$$
d=(s_1k-z_1)r^{-1}\pmod n.
$$

This is not a theoretical edge case. It is a direct algebraic key-recovery formula.

## Companion experiment

`experiments/digital-signatures/ecdsa_nonce_reuse_demo.py` signs two messages on secp256k1 with the same deliberately reused nonce, verifies both signatures, recovers $k$, and then recovers the long-term private key.

The script is educational and intentionally not constant-time, but the recovery algebra is the real ECDSA equation.

## Bias is also dangerous

Full nonce reuse is the easiest failure to explain, but partial information about many nonces can also be dangerous. If nonce generation leaks bits, has statistical bias, or follows a predictably narrow distribution, the resulting equations can be transformed into hidden-number/lattice problems.

That connects signature implementation failures to the lattice methods studied elsewhere in CryptoCave.

The safe engineering conclusion is stronger than "do not reuse $k$": the nonce-generation procedure must follow the signature specification and must not leak useful information through software, hardware, timing, faults, or side channels.

## Deterministic ECDSA

RFC 6979 derives $k$ deterministically from the private key and message hash using HMAC-based state. This removes dependence on fresh external entropy for every signature while preserving compatibility with standard ECDSA verification.

Deterministic generation does not make the entire signer side-channel resistant. If an attacker can observe secret-dependent computation, recover internal state, or fault the signer, other attacks remain possible.

## Public-key validation and "curve" vulnerabilities

The recovered Part1 notebooks also grouped certificate/curve validation issues under ECDSA vulnerabilities. That material needs a distinction:

- nonce failures attack the signature-generation equation directly;
- invalid-curve or malformed-point attacks target protocol or key-validation behavior;
- certificate-validation failures can substitute or misinterpret public keys without breaking ECDSA algebra.

A clean reference should not call all of those the same attack.

## Signature validation

An ECDSA verifier should enforce the scheme's range and public-key requirements. At minimum the signature scalars must satisfy

$$
1\le r,s\le n-1,
$$

and the public point must be a valid point in the expected subgroup/domain parameters.

Exact requirements depend on the standard profile and key encoding.

## Malleability and low-s conventions

For ordinary ECDSA, if $(r,s)$ verifies, $(r,n-s)$ also verifies. Some protocols impose a low-$s$ convention to choose one canonical representative. This is primarily a protocol/canonicalization rule rather than a repair to the core unforgeability equation.

## References

- RFC 6979, **Deterministic Usage of DSA and ECDSA**.
- NIST FIPS 186-5, **Digital Signature Standard**.
