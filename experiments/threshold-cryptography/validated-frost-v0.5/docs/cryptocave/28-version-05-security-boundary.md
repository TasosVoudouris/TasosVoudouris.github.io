# Version 0.5 security boundary and next engineering steps

Version 0.5 is an executable explanation of threshold Schnorr/FROST. It is not
a cryptographic product, authentication service, wallet, key-management system,
or medical-data security component.

## The shortest accurate statement

> Use this release to learn the protocol and test equations. Never use its toy
> keys or signatures to authorize anything real.

## What this release does correctly inside its model

- consumes verified Version 0.4 DKG shares;
- derives $Y$ and every $Y_i$ without reconstructing $x$;
- uses two RFC-shaped nonce scalars per signer;
- defaults to operating-system random bytes;
- commits before the message/package round;
- canonicalizes the signer commitment list;
- domain-separates the five hash roles;
- computes signer-specific binding factors;
- uses explicit Lagrange coefficients at zero;
- validates each signer's exact commitment and local session state;
- supports application message-policy checks;
- deletes a nonce pair after use or package rejection;
- validates every response equation before aggregation;
- emits and verifies an ordinary Schnorr equation;
- binds the application envelope to session, counter, context, DKG, signer set,
  and payload;
- records a canonical public transcript; and
- proves by test instrumentation that normal signing never invokes Shamir
  reconstruction.

## Why the cryptography is insecure

### Tiny group

The scalar field has 41 elements. An attacker can enumerate every secret key,
nonce, discrete logarithm, and hash output. A collision in a scalar challenge
occurs with probability around $1/41$, not a cryptographically negligible
probability.

### Nonstandard ciphersuite

The hash-to-scalar rules and one-byte encodings are not any RFC 9591 named
ciphersuite. No interoperability or standard test-vector claim is possible.

### Educational DKG

The key shares originate in Version 0.4's centralized, simplified multi-dealer
simulation. It omits a proven distributed network protocol and full GJKR
recovery.

### Pure Python secret arithmetic

Python integers, hashing wrappers, object allocation, modular exponentiation,
and equality checks are not designed to provide constant-time secret handling.
Garbage collection cannot guarantee secure erasure.

## Why the system model is insecure

### One process

All dealers, signers, shares, and coordinator objects can occupy the same
Python process. Compromising that process compromises every share. Threshold
security requires genuinely separate administrative or hardware trust domains.

### No authenticated transport

Method calls stand in for messages. There is no mutually authenticated channel,
protocol-message signature, replay cache, endpoint identity, or key rotation.

### No reliable distributed agreement

Every signer sees one Python package object. There is no network adversary,
equivocation-resistant broadcast, timeout, partition handling, or common-view
protocol.

### Volatile state

Nonce and commitment tracking lives in memory. Process restart, snapshot
rollback, cloning, or concurrent workers can defeat a volatile uniqueness
check.

### Unsigned transcript

A SHA-256 digest binds bytes but does not prove which participant saw, approved,
or sent them. The transcript is useful for deterministic comparison, not legal
or operational attribution.

### Minimal policy hook

`message_validator` is one Boolean callback. It does not authenticate a user,
parse a standardized transaction, obtain medical consent, enforce dual control,
or display human-readable intent.

## Security goals not provided

- production EUF-CMA assurance;
- RFC 9591 ciphersuite conformance;
- robustness or asynchronous liveness;
- post-quantum security;
- metadata confidentiality;
- side-channel resistance;
- secure memory or hardware-backed share isolation;
- proactive refresh or mobile-adversary resistance;
- share recovery or resharing;
- audit-log authenticity;
- compromise detection or incident recovery;
- certified randomness;
- production authentication; or
- encryption, threshold decryption, FHE, or private machine learning.

## FROST and authentication

A threshold signature can authenticate a challenge or protocol transcript only
after the application defines:

- who creates the challenge;
- origin and audience;
- expiry and replay behavior;
- canonical encoding;
- signer authorization policy;
- what the user or operator sees before approval;
- how the public key is registered and rotated; and
- what happens when a share holder is unavailable or compromised.

The Version 0.5 envelope demonstrates where these fields can be bound, but it
does not define a production authentication protocol.

## FROST is not threshold encryption

Schnorr/FROST shares and nonces cannot be repurposed to homomorphically encrypt
images, split cancer scans, or decrypt model results. Signatures authenticate;
they do not hide data.

The future private-ML direction needs a separate design with separate keys and
security definitions, for example:

- threshold decryption for a reviewed homomorphic-encryption scheme;
- explicit data-owner, compute-party, and result-recipient roles;
- leakage analysis for shapes, access patterns, metadata, and outputs;
- numeric-approximation and model-accuracy analysis;
- authenticated ciphertext and parameter validation;
- consent, governance, and clinical validation; and
- maintained HE/MPC libraries rather than new handwritten primitives.

Do not place patient or scan data into this repository's teaching code.

## Recommended next version boundary

The next step should strengthen one boundary rather than adding another novel
primitive. A sensible Version 0.6 learning scope is:

1. keep this toy module unchanged as the equation notebook;
2. add a separate adapter/example using a maintained RFC 9591 implementation;
3. run official RFC test vectors for the chosen suite;
4. define canonical serialized round messages;
5. simulate separate signer processes over authenticated local channels;
6. persist session and commitment-use records safely; and
7. model timeouts, terminal abort, and a fresh-session retry.

Only after that should the project introduce threshold authentication workflows
or share refresh. Threshold encryption and HE should remain a separate track.

## Production-readiness gate

Before any real deployment, all of these would need affirmative evidence:

| Gate | Version 0.5 |
|---|:---:|
| Standard ciphersuite and RFC vectors | No |
| Maintained reviewed cryptographic library | No |
| Independent signer trust domains | No |
| Authenticated reliable transport | No |
| Durable atomic nonce ledger | No |
| Constant-time secret operations | No |
| Secure key storage and erasure story | No |
| Reviewed application message schema/policy | No |
| Threat model and protocol proof matching deployment | No |
| Independent security audit | No |
| Incident, backup, recovery, and rotation procedures | No |

The correct production decision is therefore **do not deploy this code**.

## Review checklist for learners

Before changing Version 0.5, confirm that your edit preserves:

- distinct nonzero participant identifiers;
- exact threshold semantics;
- matching DKG and FROST scalar fields;
- sorted commitment lists;
- group-key inclusion in binding-factor input;
- separate $H_1$–$H_5$ domains;
- exact package/message validation before nonce use;
- one-time nonce state;
- individual response verification;
- ordinary final signature verification;
- no reconstruction in the normal path; and
- explicit toy/non-production warnings.

Run the complete suite after every change:

```powershell
python -m unittest discover -v
python .\examples\run_all.py
```

## References

- [RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html)
- C. Komlo and I. Goldberg,
  [FROST, IACR ePrint 2020/852](https://eprint.iacr.org/2020/852)
- T. Ruffing et al.,
  [ROAST, IACR ePrint 2022/550](https://eprint.iacr.org/2022/550)
