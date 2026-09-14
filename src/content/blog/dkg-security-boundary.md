---
title: "DKG Security Boundary: What the Educational Construction Does Not Claim"
description: "Document coordinator, parameter, transport, distributed-agreement, and implementation limits before moving from DKG output to threshold signing."
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
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 13
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Version 0.4 demonstrates how qualified VSS contributions become a distributed
private key and a public key. Its equations and state transitions are tested,
but its execution environment does not match a distributed adversarial network.

## Implemented learning properties

| Area | Version 0.4 behavior |
|---|---|
| Dealer independence | Every participant samples a separate random contribution |
| Hidden qualification | One Pedersen VSS session per dealer |
| Qualification | One exact dealer tuple must be shared by every simulated view |
| Public-key extraction | Secret shares are checked against a second value vector |
| Aggregation | Shares add in $\mathbb F_q$; commitments multiply in the group |
| Public key | $Y=A_0=\prod_{i\in Q}g^{a_{i,0}}$ |
| Final verification | Every key share is checked under both aggregate vectors |
| Normal secrecy flow | No Shamir reconstruction method is called by `run()` |
| Audit | All threshold coalitions can validate $Y=g^x$ explicitly |
| Failure | Bad hidden dealer exclusion; late extraction conflict and view conflict abort |

## Not a complete GJKR implementation

The code is influenced by the hidden-qualification and public-key-extraction
structure described by Gennaro, Jarecki, Krawczyk, and Rabin. It omits their
network model, reliable broadcasts, adversarial proof, fault-bound reasoning,
and public reconstruction after a valid extraction complaint. It therefore must
not be called “GJKR-secure DKG.”

The paper also distinguishes full uniform-output DKG security from the weaker
property that the adversary cannot calculate the output secret. Version 0.4 has
no proof of either property in its centralized simulator model.

## Central coordinator limitation

`MultiDealerDKG` has a global view of:

- all dealer packages;
- every participant's private delivery;
- all complaints and replacements;
- every proposed qualified-set view.

A real participant has only its own local state and authenticated public
messages. Replacing this coordinator with sockets would not automatically yield
a correct protocol; it would remove the trusted shared view on which the current
state checks depend.

## Parameter and implementation limitations

The order-41 group is exhaustible and the Pedersen generator relation is known.
Python arithmetic is not constant-time. There is no standard curve, point
encoding, domain-separated hash-to-group, proof of possession, memory locking,
or secret erasure. Deterministic `random.Random` seeds appear only for repeatable
tests and examples.

Normal creation defaults to operating-system randomness, but all dealers still
run inside one process. A deployed DKG requires independent processes and random
sources so one compromise does not expose every contribution.

## Missing distributed-system properties

Version 0.4 has no:

- cryptographic identities or authenticated message envelopes;
- confidential dealer-to-participant channels;
- replay counters, round numbers, deadlines, retransmission, or persistence;
- Byzantine reliable broadcast or consensus;
- proof that all honest parties terminate with one result;
- defense against selective abort across repeated sessions;
- durable key-share storage, backup, recovery, or rotation.

## Not yet threshold signing

The DKG result has the algebraic shape needed by a discrete-log threshold system:
private Shamir shares and one public group element. It does not implement FROST.

FROST signing additionally requires one-time nonces, nonce commitments, binding
factors, Lagrange coefficients for the selected signer set, authenticated signing
packages, domain separation, and strict nonce non-reuse. RFC 9591 specifies the
two-round signing protocol, but key generation is outside this Version 0.4
lesson. See [RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html).

## Recommended Version 0.5 scope

The next version should build an equation-level threshold Schnorr/FROST learning
model on top of `DKGResult`, while preserving these constraints:

1. the group secret is never reconstructed;
2. each signing attempt uses fresh one-time nonces;
3. the signer set and DKG transcript are bound into the signing package;
4. partial signatures are verified before aggregation;
5. the final signature verifies under the ordinary group public key;
6. wrong-session, wrong-signer-set, changed-message, invalid-share, and nonce-
   reuse cases are tested;
7. the implementation remains clearly separated from RFC-compliant production
   FROST.

Share refresh and proactive lifecycle management should follow as their own
layer rather than being hidden inside signing code.
