# Security boundary for Version 0.5

This repository is an educational implementation. It is deliberately readable,
but it is not hardened, interoperable, audited, or proven cryptographic
software.

Do not use it for real private keys, signatures, authentication, financial
assets, software releases, models, personal information, medical data, or
production infrastructure.

## What Version 0.5 implements

- the Version 0.1–0.4 mathematical, VSS, session, and DKG layers;
- public FROST group information derived from one verified DKG result;
- a two-round threshold Schnorr signing model following RFC 9591's equations;
- two one-time secret nonces and two public commitments per signer;
- fresh operating-system random bytes by default;
- RFC-shaped nonce hedging with the private key share;
- ascending, distinct signer commitment lists;
- group-key/message/commitment/identifier binding factors;
- Lagrange-weighted signature shares;
- exact matching of a signer's local commitment, session, and counter;
- optional application message-policy validation;
- logical deletion of nonce state after use or policy rejection;
- in-memory coordinator tracking of previously issued commitments;
- individual signature-share verification;
- aggregate ordinary Schnorr verification under the DKG public key;
- a bound application envelope and canonical public transcript; and
- a tested invariant that normal signing never reconstructs the group secret.

These properties hold only inside the documented single-process toy model.

## Standards boundary

RFC 9591 is an Informational RFC produced by the Crypto Forum Research Group.
Version 0.5 follows its two-round data flow and algebra, but does not implement a
named RFC ciphersuite.

The custom suite uses:

```text
context: CryptoCave-FROST-toy-SHA256-v1
group:   order-41 subgroup modulo 83
scalar:  one-byte big-endian integer
element: one-byte modular integer
hash:    SHA-256 reduced modulo 41
```

It cannot interoperate with RFC ristretto255, Ed25519, Ed448, P-256, or
secp256k1 suites and cannot pass their test vectors. No RFC security result
applies to this custom suite.

## Tiny-group warning

The group has only 41 possible scalars. Discrete logarithms, key shares, nonces,
and challenges can be exhaustively enumerated. Hash collisions and zero
challenges are common. The code retries zero nonce scalars because identity
commitments would otherwise appear frequently in this teaching group.

The equations can be correct while the parameters provide no security.

## DKG boundary

Signing shares originate from Version 0.4's centralized offline multi-dealer
simulation. That construction is inspired by DKG staging but is not a complete
or proven GJKR implementation. It lacks real reliable broadcast, Byzantine
agreement, authenticated confidential delivery, full public-reconstruction
recovery, and adversarial output guarantees.

Threshold signing does not upgrade the security of its key-generation layer.

## Nonce boundary

RFC-style Schnorr nonces must never be reused. Reuse can reveal a participant's
private key share.

Version 0.5:

- removes a nonce record from the signer after one response;
- refuses a second use through `NonceReuseError`;
- discards unused state after a convenience-run failure;
- burns state when application policy rejects an issued package; and
- lets one coordinator object reject a repeated public commitment.

However:

- dictionary removal is not physical memory erasure;
- Python may copy or retain integer objects;
- commitment history is volatile and process-local;
- restart, rollback, cloning, concurrency, or another coordinator bypasses that
  volatile history; and
- seeded example/test randomness is intentionally predictable.

A real signer needs atomic durable nonce state, rollback resistance, isolated
storage, and a reviewed CSPRNG.

## Centralized simulation

All signers and the coordinator can run inside one Python process. Separate
objects do not create separate trust domains. A process compromise can read all
private shares and nonce state.

There is no networking, transport authentication, reliable delivery, timeout,
concurrency, or participant identity. Integer participant labels are Shamir
coordinates, not authenticated people or machines.

## Transcript and application-envelope boundary

The application envelope binds:

- protocol and toy-suite labels;
- session identifier and counter;
- application context;
- group-information/DKG digest;
- selected signer identifiers; and
- raw payload.

The public transcript also binds commitments, factors, challenge, responses, and
the final signature. Its SHA-256 digest is an integrity identifier only. It is
not a participant signature, receipt, authorization record, or non-repudiation
proof.

The final Schnorr signature is over the bound envelope, not the raw payload
alone.

## Application message validation

The optional `message_validator` callback demonstrates RFC 9591's recommendation
that signers validate application inputs. It is not a complete policy engine.

Real deployments need deterministic parsers, authenticated request context,
origin/audience checks, limits, expiry, replay rules, human intent, consent,
audit, and failure policy. Signing a well-formed object does not imply that the
object is authorized.

## Side channels and secret handling

Python big integers, modular exponentiation, hashing wrappers, comparisons,
allocation, and garbage collection are not guaranteed constant time. The code
does not use locked memory, hardened key stores, hardware security modules,
process isolation, or secure deletion.

RFC 9591's side-channel guidance requires value-independent group and scalar
operations. Version 0.5 does not meet that deployment requirement.

## Identifiable abort is not robustness

An invalid signature share can be associated with its participant identifier in
the local input. Real blame additionally requires authenticated transport.

FROST does not itself provide robustness: a selected signer can refuse to reply
and force abort. Version 0.5 has no ROAST wrapper, participant replacement,
asynchronous liveness, or automatic retry. A retry requires new nonce
commitments and a new package.

## Still not provided

- an RFC 9591 named ciphersuite or standard encodings;
- official RFC test-vector compatibility;
- production discrete-log or collision security;
- a proven DKG or distributed signing network;
- durable counters, replay cache, or nonce ledger;
- authenticated identities, channels, or protocol messages;
- constant-time operations, secure erasure, or hardened secret storage;
- robustness, proactive refresh, resharing, recovery, or mobile-adversary
  protection;
- post-quantum security;
- production threshold authentication;
- threshold encryption, homomorphic encryption, or private machine learning;
- external audit, formal proof, certification, or operational incident plan.

## Normal and audit reconstruction

Normal `MultiDealerDKG.run()` and every Version 0.5 signing function avoid
Shamir reconstruction. Tests replace both reconstruction methods with
exceptions during normal signing.

Version 0.4 retains an explicitly named `audit_reconstruct_field_element()`
teaching helper. Calling it materializes the group secret and must never be part
of a threshold signing or production workflow.

## Safe next step

Keep this module as the equation notebook. A separate later implementation
should use a maintained RFC 9591 library and named ciphersuite, official vectors,
isolated signer processes, authenticated serialized messages, and durable atomic
nonce/session state before adding threshold authentication.

Threshold encryption and homomorphic private-ML experiments require separate
schemes, keys, threat models, and maintained libraries. Never use FROST key
shares as encryption or HE shares.

See [Chapter 28](docs/cryptocave/28-version-05-security-boundary.md) for the
expanded readiness checklist.
