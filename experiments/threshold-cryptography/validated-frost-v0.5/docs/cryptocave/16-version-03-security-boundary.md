# Version 0.3 security boundary and next steps

Version 0.3 is an executable cryptographic lesson. It implements correct
finite-field equations for the stated toy model and makes protocol failure
states explicit. It is not a secure VSS deployment.

## Implemented properties

| Area | What Version 0.3 establishes |
|---|---|
| Shamir | Exact labelled finite-field sharing and threshold interpolation |
| Feldman | Consistency with public, non-hiding coefficient commitments |
| Pedersen | Consistency with blinded coefficient commitments |
| Hiding lesson | Exhaustive confirmation of perfect commitment hiding in the toy group |
| Setup lesson | Explicit counterexample when $\log_g(h)$ is known |
| Transcript | Canonical binding of public session fields to a SHA-256 identifier |
| Broadcast model | Detection of two vectors through one shared in-memory board |
| Complaints | Explicit local records, responses, and unresolved-failure state |
| Finalization | Strict qualification or terminal abort |
| Reconstruction | Available only after qualification and repeated verification |

## Not implemented

### Production parameters

The order-41 group has no cryptographic hardness. Its generator relation is
known, which destroys Pedersen binding. There is no standard curve, hash-to-
group suite, point encoding, subgroup/cofactor API, or parameter ceremony.

### Distributed communication

There are no sockets, peer processes, authenticated channels, confidentiality,
timeouts, retransmission, message counters, durable logs, or concurrency. The
in-memory board is not Byzantine reliable broadcast or consensus.

### Identity and authentication

`dealer_id="alice"` is a string, not a cryptographic identity. The transcript
digest is unsigned. Anyone able to modify messages could forge, reorder, drop,
or replay them.

### Public complaint evidence

The session object has a privileged view of all private shares. Real
participants do not. The complaint record deliberately omits private values and
cannot by itself prove whether the dealer or participant lied.

### Malicious-secure threshold protocols

There is no distributed key generation, share refresh, resharing, share
recovery, proactive security, adaptive-corruption model, FROST nonce protocol,
threshold BLS proof, or threshold decryption. The Version 0.1 Beaver example
also assumes trusted preprocessing and is not malicious-secure MPC.

### Implementation hardening

Python big integers and control flow are not constant-time. Secrets are not
locked in memory or reliably erased. Inputs are not fuzzed at a serialization
boundary. There has been no external audit or formal proof of this code.

## Randomness rules

Normal constructors default to `secrets.SystemRandom`. Examples and tests pass
seeded `random.Random` objects to make output repeatable. Deterministic seeds
must never be used to generate real secret shares, nonces, keys, or blinding
values.

Uniform blinding is essential. Reusing a Pedersen blinding coefficient or
sampling it from a small biased set can restore equality or guessing leakage.

## Data handling rule

Do not use this repository with medical images, cancer scans, diagnoses,
biometrics, credentials, private keys, or personal data. Threshold encryption
and homomorphic inference require a complete design for encoding, leakage,
access control, key lifecycle, model privacy, integrity, availability, and
regulatory handling. Splitting an image into Shamir shares is not equivalent to
homomorphic encryption, and Pedersen commitments do not enable computation on
encrypted pixels.

## Version 0.4 scope implemented in the next chapters

Version 0.4 implements a **multi-dealer DKG simulation** built from the Version
0.3 session abstraction:

1. Every participant acts once as a Pedersen dealer.
2. Each dealer creates a separate session and transcript.
3. The simulation computes one common qualified-dealer set.
4. Each participant adds its accepted secret-share components.
5. Public coefficient commitments are combined consistently.
6. Tests cover one bad dealer, conflicting qualification views, and abort.

Chapters 17–21 explain the implementation and the additional GJKR security
boundary. It remains offline and educational.

## Steps after the DKG lesson

1. Add authenticated message envelopes, strict encodings, replay counters, and
   explicit protocol/domain separation.
2. Study a standardized threshold-signature protocol such as FROST, especially
   nonce generation, commitment binding, signer selection, and abort behavior.
3. Compare the lesson against a maintained implementation instead of turning
   this code directly into production software.
4. Treat threshold encryption and private machine-learning inference as
   separate research tracks with reviewed libraries and datasets containing no
   real patient information.

The safe purpose of Version 0.3 is understanding: each equation, state
transition, and failure should be visible enough to inspect before the project
moves to multi-dealer key generation.
