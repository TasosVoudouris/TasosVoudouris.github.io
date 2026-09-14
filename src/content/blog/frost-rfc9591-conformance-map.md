---
title: "RFC 9591 FROST Conformance and Deviation Map"
description: "Map the educational implementation against RFC 9591, distinguish structurally faithful protocol behavior from toy ciphersuite choices, and identify requirements for standards-compatible engineering."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Threshold Cryptography"
  - "Formal Verification"
  - "Cryptographic Engineering"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
  - "frost"
  - "rfc-9591"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 25
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Version 0.5 is deliberately precise about what “follows FROST” means. Its
rounds and equations track RFC 9591, while its ciphersuite and deployment do
not meet RFC interoperability or production requirements.

## Summary verdict

> **Protocol-shaped and equation-correct educational model; not an RFC 9591
> implementation, not wire-compatible, and not production secure.**

This language should remain beside every download or website page that exposes
the code.

## Detailed map

| RFC 9591 area | Version 0.5 status | Exact implementation or deviation |
|---|---|---|
| Prime-order group | Structurally present | Order-41 subgroup of $\mathbb{Z}_{83}^*$; trivially breakable |
| Named ciphersuite | **Not implemented** | Custom `CryptoCave-FROST-toy-SHA256-v1` |
| Group notation | Equivalent | Multiplicative instead of RFC additive notation |
| Participant identifiers | Implemented | Distinct nonzero scalars, sorted, each below $q$ |
| Shamir signing shares | Implemented | Consumes Version 0.4 `DKGResult` |
| Group public key $Y$ | Implemented | DKG aggregate constant value commitment |
| Verification shares $Y_i$ | Implemented | Evaluate aggregate value-commitment vector at $i$ |
| Key generation | External to signing | Educational multi-dealer DKG, not RFC trusted-dealer appendix |
| 32 fresh nonce bytes | Implemented by default | `secrets.token_bytes(32)` |
| Nonce hedging with secret share | Implemented | $H_3(\text{random}\|\operatorname{enc}(x_i))$ |
| Two nonces and commitments | Implemented | $(d_i,e_i)$ and $(D_i,E_i)$ |
| Nonzero nonce retry | Toy-only deviation | Avoids common identity commitments when $q=41$ |
| Nonce single use/deletion | Logically implemented | Local state removed; Python cannot ensure physical erasure |
| Coordinator commitment tracking | In-memory hedge | Lost on restart; no durable ledger |
| Sorted commitment list | Implemented | Coordinator canonicalizes; signer validates |
| RFC commitment-list tuple | Implemented in toy encoding | `enc(i) || enc(D_i) || enc(E_i)`; `nonce_id` excluded |
| $H_1$ binding factors | Equation implemented | Group key, $H_4(m)$, $H_5(L)$, and identifier |
| $H_2$ challenge | Equation implemented | `enc(R) || enc(Y) || m` |
| $H_3,H_4,H_5$ roles | Implemented | RFC labels and custom toy SHA-256 reduction |
| Hash-to-scalar method | **Not RFC suite compatible** | SHA-256 integer reduced modulo 41 |
| Scalar encoding | Canonical locally | Fixed-width big-endian; not named-suite encoding |
| Element encoding | Canonical locally | Fixed-width modular integer; not curve-point encoding |
| Deserialize network inputs | No wire protocol | Python values validated directly |
| Lagrange coefficient | Implemented | $\prod_{j\ne i}j/(j-i)$ at zero |
| Signature share equation | Implemented | $z_i=d_i+e_i\rho_i+\lambda_ix_ic$ |
| Partial verification | Implemented | Every response checked before aggregation |
| Aggregate response | Implemented | $z=\sum_i z_i$ |
| Final signature | Implemented | Toy `(R,z)` Schnorr signature |
| Ordinary verification | Implemented | $g^z=RY^c$ |
| Signature encoding shape | Implemented locally | `enc(R) || enc(z)` with one-byte toy fields |
| RFC test vectors | **Cannot pass** | Wrong group, hashes, and encodings |
| Message prehash | Not used | Framed application envelope is supplied directly as `msg` |
| Application input validation | Hook implemented | Optional `message_validator` callback |
| Reliable delivery | Not implemented | One local process and direct method calls |
| Authenticated channel | Not implemented | Integer participant IDs do not authenticate senders |
| Identifiable abort | Local equation evidence | Attribution is not trustworthy without authenticated transport |
| Robustness | Not implemented | Matches RFC exclusion; no ROAST wrapper |
| Constant-time operations | **Not implemented** | Pure Python integers and exponentiation |
| Secure erasure | **Not implemented** | Logical reference deletion only |
| Post-quantum security | Not provided | Schnorr relies on discrete-log hardness |

## Why the toy suite cannot be called RFC-compliant

RFC ciphersuite requirements include:

1. near-uniform scalar outputs for $H_1$, $H_2$, and $H_3$;
2. per-suite domain separation;
3. a prime-order group with strict canonical deserialization; and
4. specified canonical signature encoding.

The toy construction illustrates each interface, but it is not registered or
specified as a real ciphersuite. Its one-byte encodings, modular group, and
hash reduction do not match any RFC 9591 suite. The tiny order makes challenge
collisions and zero values common rather than negligible.

Therefore:

- signatures do not interoperate with ristretto255, Ed25519, Ed448, P-256, or
  secp256k1 FROST software;
- RFC test vectors are inapplicable;
- no RFC security proof applies to this implementation; and
- passing all local tests demonstrates internal consistency only.

## Application envelope profile

The core RFC accepts arbitrary bytes as `msg`. Version 0.5 defines those bytes
as a CryptoCave-specific framed envelope. This is a higher-level application
profile, not a change to the response equation.

Benefits for the lesson:

- session and replay fields are visible;
- DKG configuration is bound;
- purpose/context confusion is demonstrated;
- selected signers are part of application meaning; and
- the raw payload remains available for signer policy validation.

Cost:

- a verifier must reproduce this envelope exactly;
- the final signature is not a signature over the raw payload alone; and
- this framing is not standardized outside the project.

A later real implementation must either standardize and version the application
envelope or adopt an existing protocol's canonical signing format.

## RFC requirement vocabulary

Documentation should reserve uppercase `MUST`, `MUST NOT`, `SHOULD`, and similar
terms for quoting or accurately paraphrasing RFC requirements. Local design
choices should use ordinary language unless CryptoCave publishes its own
normative specification.

## What a standards-compatible next implementation requires

At minimum:

1. select an RFC 9591 named ciphersuite, preferably the recommended
   ristretto255/SHA-512 suite unless interoperability requires another;
2. use a maintained, reviewed implementation of group arithmetic and FROST;
3. validate against the RFC's published test vectors;
4. define the exact DKG-to-FROST key-package format;
5. isolate each signer into a separate trust domain;
6. add authenticated, reliable protocol messages with canonical serialization;
7. persist session counters and nonce/commitment use atomically;
8. perform application message parsing and authorization at every signer;
9. protect secrets with constant-time code and hardened storage; and
10. obtain independent design and implementation review.

Replacing only `p=83` with a larger integer is not sufficient.

## Verification evidence in this release

Version 0.5 tests:

- all ten 3-of-5 subsets;
- 4-of-5 and 5-of-5 signer sets;
- exact commitment-list encoding;
- binding-factor, group-commitment, challenge, interpolation, and partial-share
  equations;
- ordinary Schnorr verification;
- final binding to message/session/counter/context/group/signer set;
- nonce deletion and reuse rejection;
- malformed elements, identifiers, packages, and responses;
- coordinator commitment tracking and package closure;
- application message rejection;
- deterministic teaching reproduction; and
- absence of Shamir reconstruction in normal signing.

These tests are regression evidence, not a cryptographic proof or external
audit.

## Authoritative reference

Use the RFC Editor copy as the canonical link:

- [RFC 9591: The Flexible Round-Optimized Schnorr Threshold (FROST) Protocol
  for Two-Round Schnorr Signatures](https://www.rfc-editor.org/rfc/rfc9591.html)
