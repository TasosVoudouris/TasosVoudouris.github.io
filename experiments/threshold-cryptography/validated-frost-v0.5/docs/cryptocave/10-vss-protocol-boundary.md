# Broadcast, Complaints, and the Protocol Boundary

The Feldman equation answers one question: “Is my share consistent with this
commitment vector?” A complete VSS protocol must also ensure that honest parties
agree on which commitment vector and which dealer outcome they accepted.

## One commitment vector for everyone

If the dealer privately sends one vector $C$ to Alice and another vector $C'$ to
Bob, both parties may accept locally while referring to different polynomials.
A reliable broadcast abstraction prevents this equivocation by guaranteeing
that honest recipients deliver the same value or agree that delivery failed.

In a practical authenticated network, a first experimental approximation can
bind the commitment vector to a transcript containing

```text
protocol_id || version || session_id || dealer_id
|| threshold || participant_ids || group_parameters
|| coefficient_commitments
```

Every protocol message must also bind its sender, receiver, round, and counter.
A signed transport message and a cryptographic coefficient commitment solve
different problems; both are necessary.

## Complaints

When participant $P_i$ receives a share that fails verification, it emits a
complaint referring to the session, dealer, participant identifier, and public
commitment digest. A protocol must then decide among outcomes such as:

- the dealer privately retransmits a valid share;
- the dealer publicly reveals a disputed share, which may affect privacy;
- other parties verify evidence of misbehavior;
- the dealer is disqualified after a threshold or pattern of complaints;
- the session aborts when availability or consistency can no longer be assured.

Rules must also handle false complaints by malicious participants. Simply
counting unauthenticated strings saying “invalid” is not a complaint protocol.

## Reconstruction policy

The Version 0.2 Feldman API offers two local reconstruction policies:

- permissive mode rejects invalid shares and reconstructs if at least $\tau$
  verified shares remain;
- strict mode aborts if any supplied share fails verification.

The permissive mode is useful for explaining filtering. A real application
must define who collects shares, how duplicate identities are prevented, how
accepted shares are authenticated, and whether a rejected participant can be
replaced.

## Feldman VSS versus robust decoding

Feldman verification checks a share against commitments. Reed–Solomon decoding
uses redundancy to locate errors in a received codeword. These mechanisms are
complementary:

| Mechanism | Public commitments required? | Can identify an invalid labelled share? | Main assumption |
|---|---:|---:|---|
| Feldman verification | Yes | Yes, against the agreed vector | Discrete-log binding and common commitments |
| Redundant interpolation check | No | Detects inconsistency but may not locate it | Enough extra shares |
| Robust RS decoding | No | Yes, within the distance bound | $n\geq\tau+2e+s$ |

Later protocols may use both verification and robust reconstruction.

## Why participant signing keys were removed from the core

The original `generate_keys()` function created an unrelated signing key for
each participant, but those keys were never used in the Feldman equation. VSS
coefficient commitments are derived from the dealer's polynomial coefficients,
not from independently generated participant private keys.

Version 0.3 now adds an offline state model with transcript digests, complaint
records, responses, qualification, and abort. The digest is not signed, and the
in-memory board is not a real reliable-broadcast protocol. Participant
authentication should later be a separate transport/session layer with an
explicit identity model, rather than unused key generation inside the algebraic
module.

Next: [Audit of the original VSS experiments](11-original-vss-code-audit.md),
then [Pedersen VSS](12-pedersen-vss.md).
