# Security Boundaries and Development Roadmap

Version 0.1 established a correct passive algebraic baseline. Version 0.2 added
Feldman coefficient commitments. Version 0.3 added Pedersen commitments and an
offline session state machine. Version 0.4 composes those sessions into an
offline multi-dealer DKG. The project is still not a threshold-
authentication system, a malicious-secure MPC engine, or a private medical-
imaging pipeline. Version 0.5 adds an equation-level two-round FROST signing
model without changing that production boundary.

The safest route forward is incremental: every new security claim must appear
as a separate layer with its own threat model, tests, and comparison against a
maintained implementation.

## Version 0.2 — Feldman verification layer (completed)

The Shamir module remains unchanged. The dealer commits to polynomial
coefficients, and each participant verifies that its share matches the public
commitments. Tests cover honest distributions, every threshold coalition, all
field secrets, changed shares, changed commitments, invalid identifiers,
duplicate identifiers, strict aborts, and reconstruction from accepted shares.

The Version 0.2 boundary remains useful for comparison: it assumes one common
commitment vector and represents complaints only as rejected verification
results.

## Version 0.3 — Pedersen VSS and protocol state (completed)

Pedersen VSS is a separate construction with a secret polynomial and a blinding
polynomial. Tests distinguish information-theoretic hiding from the binding
failure caused by the known generator relation in the tiny teaching group.

The offline session model adds transcript identifiers, a consistent-broadcast
abstraction, participant statuses, complaint records, private dealer responses,
strict qualification, and abort. It deliberately does not add authenticated
messages or claim real reliable broadcast.

## Version 0.4 — Distributed key state (completed)

Every party acts as a dealer, distributes a Pedersen VSS sharing, and contributes
to one fixed qualified set. A separate value-commitment round extracts the
public-key information from the same secret polynomials. Participant key shares
and both commitment vectors aggregate homomorphically. The resulting public key
is known, but normal execution never reconstructs the private scalar.

The coordinator, agreement views, tiny group, and late-failure abort are
explicitly educational. The complete GJKR public-reconstruction recovery,
cryptographic identities, authenticated channels, canonical message encoding,
counters, timeouts, and real agreement/broadcast remain deferred.

## Version 0.5 — Educational FROST signing (completed)

Version 0.5 implements a small equation-level FROST model anchored to RFC 9591.
Tests cover every threshold signer subset, invalid commitments, bound messages,
wrong sessions and counters, missing signers, malformed shares, ordinary final
verification, and—most importantly—nonce non-reuse.

The signed application transcript should bind at least

```text
protocol || version || suite || session_id || counter
|| application_context || DKG_group_digest || participant_set || message
```

The output verifies under one group public key using the toy suite's ordinary
Schnorr verifier. No normal signing process reconstructs the group private key.
The order-41 suite is deliberately not an RFC ciphersuite or production system.

## Version 0.6 — Standard-suite and process-boundary study

Keep the Version 0.5 equation notebook unchanged. Add a separate adapter based
on a maintained RFC 9591 implementation, verify official vectors, serialize
round messages canonically, isolate signers into separate processes, authenticate
local channels, and persist nonce/session state. This is the right boundary
before a threshold authentication application.

Share refresh should remain a separate lifecycle layer: qualified dealers share
random zero-constant polynomials, participants update their shares, the public
key remains unchanged, and obsolete shares must be erased.

## Version 0.7 — Threshold BLS

Return to BLS only after DKG and partial-signature aggregation are understood.
Use the BLS scalar field, standard hash-to-curve, correct group types and
identities, one shared private key, Lagrange aggregation in the exponent, and
verification under the corresponding group public key.

Keep three demonstrations visibly separate:

1. reconstruction of a backed-up key followed by ordinary BLS;
2. aggregate BLS under independent public keys;
3. genuine threshold BLS under one distributed key.

## Version 0.8 — MPC and private machine learning

Retain `NeuralNetwork.py` and `NeuralNetwork2.py` as plaintext baselines. First
implement a small linear classifier over shared field values. Then reproduce
the same computation in MP-SPDZ rather than attempting to turn the old SPDZ
sketches into a security-critical framework.

For homomorphic inference, begin with single-key CKKS and a small public medical
benchmark. Only after accuracy and approximation error are understood should
the experiment use threshold CKKS decryption. OpenFHE provides multiparty BGV,
BFV, and CKKS examples that can act as reference behavior.

A practical initial pipeline is:

```text
public training or fixed trained model
            ↓
small public biomedical test image
            ↓
encrypted or shared feature vector
            ↓
linear / low-degree polynomial inference
            ↓
threshold-authorized result release
```

Encrypting an image, splitting an image, sharing model weights, hiding labels,
and distributing a decryption key are different privacy designs. Before each
experiment, specify who owns the data, who owns the model, who performs the
computation, which parties may collude, and exactly what the final result reveals.

Medical benchmarks are research tools, not clinical systems. Real scans require
governance, lawful processing, access control, auditability, secure deletion,
and clinical validation in addition to cryptography.

## Rule for every future version

The original notebook remains untouched. New functionality enters the active
package only after its terminology, threat model, success cases, failure cases,
and external reference implementation are documented. This preserves the simple
learning path without allowing an exploratory script to acquire a stronger
security label than it deserves.
