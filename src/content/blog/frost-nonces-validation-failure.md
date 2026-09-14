---
title: "FROST Nonces, Validation, Replay Boundaries, and Failure"
description: "Analyze nonce-reuse catastrophe, single-use nonce state, commitment tracking, session/counter/context binding, input validation, and identifiable abort behavior."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Threshold Cryptography"
  - "Implementation Security"
  - "Cryptographic Engineering"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
  - "frost"
  - "rfc-9591"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 24
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Most of the dangerous complexity in threshold Schnorr signing is not the final
sum $z=\sum z_i$. It is managing one-time state and ensuring that every signer
computes against the same authorized package.

## Learning goals

This chapter explains:

- why nonce reuse reveals a key share;
- what Version 0.5 deletes and when;
- how sessions and counters are bound;
- why hashes do not authenticate senders;
- how message validation prevents a signing oracle;
- which failures identify a participant; and
- which failures only cause abort.

## Why nonce reuse is catastrophic

Suppose signer $i$ reuses the same effective nonce

$$
k_i=d_i+\rho_i e_i
$$

in two response equations:

$$
z_i=k_i+\lambda_i x_i c,
$$

$$
z_i'=k_i+\lambda_i' x_i c'.
$$

Subtracting eliminates the nonce:

$$
z_i-z_i'=x_i(\lambda_i c-\lambda_i'c')\pmod q.
$$

If the denominator is nonzero, an observer obtains

$$
x_i=(z_i-z_i')(
\lambda_i c-\lambda_i'c')^{-1}\pmod q.
$$

Learning one share may not immediately reveal the group secret, but it reduces
the corruption threshold and permanently compromises that participant. Enough
recovered shares recover $x$.

The two-nonce FROST construction does not make reuse safe. Both secret nonces
are one-time values.

## Version 0.5 nonce lifecycle

| Event | Local state |
|---|---|
| Before round one | No nonce pair |
| `signer.commit()` | Store $(d_i,e_i)$ under public `nonce_id` |
| Package validation | State remains private and pending |
| Application policy rejects | Delete the matching pair; abort |
| `signer.sign()` accepts | Remove pair before returning $z_i$ |
| Coordinator later aborts | Used pairs remain deleted |
| Coordination helper fails early | Delete any still-unused pairs |
| Second call with same package | Raise `NonceReuseError` |

Python cannot guarantee physical memory zeroization. Removing an object from a
dictionary is a logical lifecycle guarantee, not proof that bytes disappeared
from RAM, swap, crash dumps, traces, or interpreter copies.

## Fresh randomness

Normal `commit()` uses `secrets.token_bytes(32)`. It then mixes those bytes with
the encoded private key share through $H_3$, matching the RFC nonce-generation
shape.

Seeded `random.Random` appears only in examples and tests. It makes output
reproducible and therefore makes nonces predictable. Copying those seeds into
an application would be a key-compromise bug.

Real systems also need:

- a reviewed operating-system CSPRNG;
- failure handling if randomness is unavailable;
- protection against virtual-machine snapshot rollback;
- protection against cloned signer state;
- per-device nonce separation; and
- durable evidence that commitments were never reused.

## Coordinator-side commitment tracking

RFC 9591 permits a coordinator to track prior public nonce commitments as an
additional hedge. `FrostCoordinator` stores

```text
(participant_id, D_i, E_i)
```

for every issued package and rejects reuse within that coordinator object.

This is not durable. Restarting the process loses the set, and a second
coordinator object has an independent set. Production state would need atomic,
persistent, rollback-resistant storage tied to one group key and signer
identity.

## Session, counter, and context binding

`FrostSigningPackage.message_to_sign()` frames:

- a protocol/version label;
- suite identifier;
- `session_id`;
- monotonic application `counter`;
- `application_context`;
- group-information digest;
- selected signer identifiers; and
- raw payload.

That envelope becomes the exact FROST `msg`. The signature therefore changes
when any bound field changes, subject to the obvious insecurity and high
collision rate of the toy field.

### Why both session and counter?

The session ID names one workflow. The counter expresses ordering or uniqueness
inside an application policy. Neither is useful if callers freely repeat values.
A real service must define who allocates counters, where they persist, and how
concurrent requests are serialized.

### Why bind the DKG digest?

Two groups can coincidentally have the same small public key in a toy group, or
an application can accidentally load shares and verification keys from
different ceremonies. Binding the complete public `FrostGroupInfo` digest
prevents the package from silently switching group configuration.

### Why bind the signer set?

FROST's binding-factor computation already incorporates the complete commitment
list. Version 0.5 additionally includes selected identifiers in the application
envelope so a higher-level verifier can define the signature's application
meaning in terms of that exact subset.

This is an application profile choice. The final signature verifies over the
envelope, not over the raw payload alone.

## Message validation

Cryptographic code cannot decide whether a request is legitimate. Before
producing a signature share, each participant should validate the actual
application object.

Examples include:

- transaction syntax, network, amount, destination, and policy limits;
- software-release artifact digest, version, branch, and approval ticket;
- authentication challenge origin, audience, expiry, and user intent;
- model-release identity, evaluation result, and authorization; or
- medical workflow purpose, consent, patient/data scope, and permitted result.

Signing only a caller-supplied digest can hide malicious structured content
from the participant. If policy needs the raw object, the signer must receive
and parse the raw object, reproduce any digest, and compare it before signing.

`message_validator` is a teaching hook for this decision. It is not a complete
authorization system.

## Input validation layers

### Group information

- prime group and scalar moduli;
- scalar order divides $p-1$;
- generator lies in the subgroup and is non-identity;
- public key and all verification shares are valid non-identity elements;
- participant identifiers are sorted, distinct, nonzero, and below $q$;
- threshold is between one and participant count; and
- DKG digest is exactly 32 bytes in hexadecimal form.

### Round-one commitment

- correct public dataclass type;
- selected participant is configured;
- $D_i$ and $E_i$ are non-identity subgroup elements;
- identifier has a canonical scalar encoding; and
- public commitment has not appeared previously at that coordinator.

### Round-two package

- expected protocol and version;
- nonempty session and application context;
- counter at least one;
- message is bytes;
- group-info digest matches;
- signer count is in $[t,n]$;
- commitments are sorted and participants are unique and known;
- signer's own exact commitment appears;
- local session/counter match; and
- application validator approves.

### Signature share

- exactly one response per selected signer;
- response is a canonical scalar in $[0,q)$;
- package digest matches; and
- the individual verification equation holds.

### Final signature

- $R$ and $Y$ are valid non-identity elements;
- $z$ is canonical; and
- $g^z=RY^c$ over the exact signed envelope.

## Failure matrix

| Failure | Detected by | Version 0.5 action | Participant blame? |
|---|---|---|---|
| Unknown/duplicate commitment ID | Coordinator/signers | Abort before signing | Input source only |
| Changed signer's commitment | Signer | Abort; do not create $z_i$ | Coordinator/package path |
| Wrong DKG/group digest | Signer | Abort | Configuration/package path |
| Disallowed application message | Signer policy | Delete nonce; abort | No protocol fault implied |
| Missing response | Coordinator/application timeout | Abort | Only with authenticated identity and timeout policy |
| Noncanonical $z_i$ | Coordinator | Abort | Yes, with authenticated channel |
| Failed partial equation | Coordinator | Abort and identify ID | Yes, with authenticated channel |
| Failed final equation | Coordinator | Abort | Investigate shares and configuration |
| Reused deleted nonce | Signer | Raise `NonceReuseError` | Local state-management fault |
| Reused public commitment | Coordinator | Raise `NonceReuseError` | Signer or rollback fault |

## Identifiers are not authentication

A `participant_id` is a Shamir interpolation coordinate. An attacker can write
the integer `2` into a message. Attribution requires an authenticated channel
or signed protocol message that binds the transport identity to participant 2.

Similarly, SHA-256 transcript digests provide integrity identifiers only after
all parties agree on the bytes. They do not prove who created or accepted the
transcript.

## Abort and retry rules

After any selected signer has returned a response, its nonce pair is gone. A
retry must start a new round one with fresh pairs, a new session/counter policy,
and a new commitment list. Reusing successful responses in another package is
invalid.

Version 0.5 closes a package on the first aggregation attempt. It does not
replace a failed signer inside the package. A new subset must begin a new
signing operation.

## Side channels and process isolation

The code uses Python integers, modular exponentiation, garbage collection, and
ordinary memory. These operations are not guaranteed constant time or securely
erasable. All signer objects and the coordinator also execute in one process,
so the demonstration has no compromise isolation.

A real threshold design needs separate trust domains. Merely creating five
objects on one computer does not distribute trust.
