---
title: "FROST and RFC 9591: The Two-Round Threshold Schnorr Protocol"
description: "Walk through RFC 9591’s two-round FROST signing flow, ciphersuite roles, nonce generation, commitment encoding, binding factors, group commitments, challenges, and signature shares."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Threshold Cryptography"
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
  - "frost"
  - "rfc-9591"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 21
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
[RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html) is the standards anchor
for Version 0.5. It is an Informational RFC representing Crypto Forum Research
Group consensus, not an IETF Standards Track specification. This distinction
does not weaken its value as the precise protocol reference, but documentation
should not call it an Internet Standard.

This chapter follows the RFC's structure and names. The next chapter maps each
operation to the Python code.

## Scope and assumptions

FROST produces Schnorr signatures after at least `MIN_PARTICIPANTS` out of
`MAX_PARTICIPANTS` signers cooperate. It assumes:

- a prime-order group and a cryptographic hash function;
- a securely generated Shamir sharing of the signing key;
- distinct nonzero scalar participant identifiers;
- common group information $(Y,Y_1,\ldots,Y_n)$;
- reliable delivery for liveness;
- authenticated communication when participants must be blamed; and
- application validation of messages before signing.

Key generation is outside the RFC's main signing protocol. The RFC includes a
trusted-dealer appendix, while Version 0.5 consumes the Version 0.4 educational
DKG output.

## Ciphersuite operations

A complete FROST ciphersuite defines:

- a prime-order group $G$ and generator;
- scalar and element serialization/deserialization;
- random scalar generation;
- domain-separated functions $H_1,H_2,H_3,H_4,H_5$;
- signature verification; and
- canonical signature encoding.

The RFC recommends FROST(ristretto255, SHA-512) and also specifies Ed25519,
Ed448, P-256, and secp256k1 suites. Version 0.5 implements none of those suites;
it uses `CryptoCave-FROST-toy-SHA256-v1` solely to expose the equations.

### Hash roles

| Function | Output | Role |
|---|---|---|
| $H_1$ | Scalar | Binding factor $\rho_i$ |
| $H_2$ | Scalar | Schnorr challenge $c$ |
| $H_3$ | Scalar | Nonce derivation from fresh randomness and key share |
| $H_4$ | Fixed bytes | Hash the message for binding-factor input |
| $H_5$ | Fixed bytes | Hash the encoded commitment list |

Per-suite context strings and the labels `rho`, `chal`, `nonce`, `msg`, and
`com` domain-separate these uses.

## Helper 1: nonce generation

RFC 9591 derives a nonce by sampling 32 fresh random bytes and hashing them
together with the encoded secret signing share:

$$
r\leftarrow H_3(\operatorname{random\_bytes}(32)\|
\operatorname{enc}(x_i)).
$$

Mixing the key share hedges against a defective random-number generator, but it
does not make deterministic or repeated randomness acceptable. Fresh randomness
is still mandatory.

Each FROST commitment operation invokes nonce generation twice to produce a
hiding nonce $d_i$ and binding nonce $e_i$.

## Helper 2: interpolation value

For selected identifiers $S$ and $i\in S$:

$$
\lambda_i^S=
\prod_{j\in S,\,j\ne i}\frac{j}{j-i}\pmod q.
$$

The helper rejects an absent identifier or any duplicate identifier.

## Helper 3: canonical commitment-list encoding

The public round-one list consists of tuples

$$
(i,D_i,E_i).
$$

It must be sorted in ascending identifier order. The RFC encoding is the exact
concatenation

$$
\operatorname{enc}(i)\|
\operatorname{enc}(D_i)\|
\operatorname{enc}(E_i)
$$

for every list entry in that order. Canonical order matters because every
signer must hash the same bytes.

Version 0.5 adds a public `nonce_id` for local state lookup, but intentionally
excludes it from this RFC-style tuple encoding.

## Helper 4: binding factors

First calculate

$$
P=\operatorname{enc}(Y)\|H_4(m)\|
H_5(\operatorname{enc\_commitment\_list}(L)).
$$

Then, for each selected participant,

$$
\rho_i=H_1(P\|\operatorname{enc}(i)).
$$

Thus $\rho_i$ binds:

- the group public key;
- exact message;
- complete ordered commitment list; and
- participant identifier.

## Helper 5: group commitment

In additive RFC notation:

$$
R=\sum_{i\in S}(D_i+\rho_i E_i).
$$

In CryptoCave's multiplicative notation:

$$
R=\prod_{i\in S}D_iE_i^{\rho_i}.
$$

## Helper 6: challenge

The challenge is

$$
c=H_2(\operatorname{enc}(R)\|\operatorname{enc}(Y)\|m).
$$

FROST does not automatically prehash messages. If an application prehashes,
the RFC recommends a separate domain-separated construction at a security
level appropriate for the selected ciphersuite.

## Round one: commitment

Each selected signer runs:

1. $d_i\leftarrow\operatorname{nonce\_generate}(x_i)$;
2. $e_i\leftarrow\operatorname{nonce\_generate}(x_i)$;
3. $D_i=g^{d_i}$;
4. $E_i=g^{e_i}$; and
5. send $(i,D_i,E_i)$ to the coordinator.

The pair $(d_i,e_i)$ stays secret and persists only until round two. The
commitments are public.

## Coordinator package

The coordinator chooses at least $t$ participants and sends each selected
signer:

- the exact message; and
- the complete sorted commitment list for that signing operation.

All selected signers must receive the same logical data. A signer checks that
its identifier and exact commitments appear in the list.

## Round two: signature-share generation

Signer $i$ computes:

1. all binding factors;
2. $R$;
3. $\lambda_i^S$;
4. $c$; and
5. $z_i=d_i+e_i\rho_i+\lambda_i^Sx_ic\pmod q$.

It returns $z_i$ and deletes the nonce pair and corresponding local commitment
state. The pair must never be used in another signing operation.

## Aggregation

The coordinator validates each response as a canonical scalar and computes

$$
z=\sum_{i\in S}z_i\pmod q.
$$

The final signature is $(R,z)$. Before publication, the coordinator should
verify it using the selected ciphersuite's ordinary signature verifier.

Version 0.5 additionally verifies every individual response before summing it.
This costs more group operations on an honest run but makes the teaching audit
and blame path explicit.

## Individual response verification

The check in additive RFC notation is

$$
[z_i]g
\stackrel{?}{=}
D_i+[\rho_i]E_i+[c\lambda_i]Y_i.
$$

CryptoCave checks the equivalent multiplicative equation

$$
g^{z_i}
\stackrel{?}{=}
D_iE_i^{\rho_i}Y_i^{c\lambda_i}.
$$

A failed equation identifies which supplied participant response was invalid,
assuming the transport authenticated that participant.

## Identifiable abort is not robustness

FROST can identify an invalid response, but it does not force an uncooperative
participant to respond and does not complete around every failure. A malicious
selected signer can cause denial of service.

The RFC explicitly says FROST is not robust. ROAST is a separate wrapper design
for robust asynchronous Schnorr threshold signing. Version 0.5 implements
neither ROAST nor participant replacement during an active package.

## Input validation checklist

Before producing $z_i$, a signer should establish:

- the group/ciphersuite configuration is the expected one;
- the DKG/group-information digest matches;
- the package has at least $t$ and at most $n$ entries;
- every identifier is known, distinct, nonzero, and canonically ordered;
- every group element is valid and non-identity;
- its own identifier and exact $(D_i,E_i)$ appear;
- its local nonce record has the same session and counter;
- the application context is permitted; and
- the raw application payload is valid and authorized.

Cryptographic validity is not application authorization. A well-formed
transaction may still be forbidden, and a correctly hashed medical-model
request may still lack consent.

## Security properties and exclusions in the RFC

Under its ciphersuite and key-generation assumptions, RFC 9591 describes
EUF-CMA security with a malicious coordinator and up to $t-1$ corrupted
participants. The RFC does not aim to provide:

- post-quantum security;
- robustness by itself;
- algorithm-downgrade prevention; or
- metadata protection.

Deployment code must also mitigate side channels with constant-time group and
scalar operations. Pure Python big-integer arithmetic does not meet that
requirement.

## Primary sources

- D. Connolly, C. Komlo, I. Goldberg, and C. A. Wood,
  [RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html), 2024.
- C. Komlo and I. Goldberg, “FROST: Flexible Round-Optimized Schnorr Threshold
  Signatures,” [IACR ePrint 2020/852](https://eprint.iacr.org/2020/852), 2020.
