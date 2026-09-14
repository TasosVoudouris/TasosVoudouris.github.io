---
title: "Digital Signatures II: RSA Signatures — From Textbook Exponentiation to RSASSA-PSS"
description: "Why textbook RSA is not a secure signature scheme, how multiplicative structure creates forgeries, and how modern RSA signatures use standardized encodings such as RSASSA-PSS."
pubDate: "2025-03-05"
updatedDate: "2026-09-12"
topics:
  - "Digital Signatures"
  - "Public-Key Cryptography"
  - "Cryptanalysis"
  - "Implementation Security"
tags:
  - "rsa"
  - "rsa-signatures"
  - "pss"
  - "pkcs1"
  - "forgery"
difficulty: "Intermediate"
series: "Digital Signatures"
seriesOrder: 2
status: "Reviewed"
draft: false
---
The RSA trapdoor permutation is symmetric-looking algebraically:

$$
(m^e)^d \equiv m \pmod N.
$$

That tempts people to describe an RSA signature as "encrypting a hash with the private key." The phrase hides the most important part of the design: **the encoded message being exponentiated must have a secure signature-specific structure**.

## The textbook construction

Let the public key be $(N,e)$ and the private exponent be $d$. A raw textbook signature would be

$$
s = m^d \bmod N,
$$

with verification

$$
s^e \bmod N \stackrel{?}{=} m.
$$

The equation is correct, but the scheme is not secure.

## Multiplicative structure creates algebraic forgeries

RSA satisfies

$$
(m_1m_2)^d \equiv m_1^d m_2^d \pmod N.
$$

So raw signatures inherit multiplicative malleability. If an adversary obtains signatures $s_1$ and $s_2$ on suitable representatives $m_1$ and $m_2$, then

$$
s_1s_2 \bmod N
$$

verifies as a raw signature on

$$
m_1m_2 \bmod N.
$$

The problem is not the RSA key pair. The problem is treating the bare permutation as a complete signature construction.

## Hashing alone is still not the full answer

Replacing $m$ with $H(m)$ removes some obvious algebraic choices, but a deployed RSA signature still needs a precise encoding format. The verifier must know how the hash algorithm, digest, salt, padding, and modulus length are represented.

Modern RSA standards therefore define complete schemes rather than the raw equation.

## RSASSA-PSS

RSASSA-PSS uses a probabilistic encoding before the RSA private operation. Conceptually:

$$
M \xrightarrow{H,\,\text{salt},\,\text{MGF}} EM \xrightarrow{\text{RSA private op}} S.
$$

Verification applies the public RSA operation, recovers the encoded message, and validates the PSS structure.

PSS is important because the encoding is part of the security argument. The salt means the same message can produce different valid signatures, while the mask-generation and consistency checks force the representative into a structured form.

RFC 8017 specifies RSASSA-PSS in detail. FIPS 186-5 references RSA signature generation through PKCS #1 and imposes additional requirements for approved use.

## PKCS #1 v1.5 signatures

RSASSA-PKCS1-v1_5 is older and deterministic. It is still widely deployed and standardized, but new designs often prefer PSS where ecosystem compatibility permits it.

The key lesson is the same: **neither scheme is "raw RSA."** Both define an encoded message that is then processed by the RSA primitive.

## Separate signing and encryption keys

A practical key-management rule is to avoid casually reusing one RSA key pair for unrelated purposes. FIPS 186-5 explicitly treats RSA digital-signature keys as signature keys rather than generic RSA trapdoors for arbitrary use.

Protocol separation reduces the chance that an oracle in one subsystem becomes useful against another.

## Private-key files are not automatically protected

The old CryptoCave notes called PEM handling an "RSA attack." That terminology is misleading.

PEM is an encoding/container convention. A PEM file may hold a public key, certificate, or private key. If an unencrypted private-key file is stolen, the security failure is **key compromise**, not a new mathematical attack on RSA.

The real engineering questions are therefore:

- is the private key encrypted at rest when appropriate,
- who can read the file,
- is the password/KDF policy adequate,
- can the key be extracted from the runtime environment,
- is the key stored in hardware or software,
- are backups protected.

## What to test in an implementation

A correct RSA signature implementation should reject malformed encodings rather than simply comparing a recovered integer with a digest. It should also validate signature length and range, bind the intended hash function, and use a library implementation of the standardized scheme.

## Relationship to the RSA Deep Dives

The RSA Deep Dive series studies encryption and key-generation failures such as common-modulus reuse, Håstad, Coppersmith, padding oracles, and ROCA. This article focuses specifically on the signature side: raw RSA algebra is not a signature standard, and secure encoding is non-negotiable.

## References

- RFC 8017, **PKCS #1: RSA Cryptography Specifications Version 2.2**, especially RSASSA-PSS.
- NIST FIPS 186-5, **Digital Signature Standard**.
