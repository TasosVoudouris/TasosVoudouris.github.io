# Complaints, qualification, and abort

A failed VSS verification must change the protocol outcome. Printing `False`
and continuing would allow inconsistent shares to enter later DKG, refresh, or
threshold-signature computations.

Version 0.3 models a conservative workflow: every bad share opens a complaint,
the dealer may privately replace it, and any unresolved complaint causes abort
at finalization.

## 1. Participant statuses

| Status | Meaning |
|---|---|
| `pending` | The delivered share pair has not been checked |
| `accepted` | The original share pair matches the commitments |
| `complained` | The current pair fails verification |
| `resolved` | A private replacement matches the same commitments |

These statuses are distinct from the global session state. A session may be in
`complaints-open` while other participants are already accepted.

## 2. Complaint record

When participant $i$ fails verification, the public record contains:

$$
(\text{session id},\ i,\ \text{transcript digest},\ \text{reason}).
$$

It does not contain $(s_i,t_i)$. This avoids publishing private shares, but it
does not create publicly verifiable evidence. In Version 0.3, one central
Python object holds all local inputs and can recompute verification; a real
distributed participant cannot ask that trusted object to decide who lied.

A complete protocol must specify how complaints become evidence. Depending on
the VSS construction and threat model, that might involve authenticated
retransmission, publicly opening disputed values, encrypted shares with proofs,
or other verifiable-delivery techniques. Each choice has privacy, robustness,
and complexity consequences.

## 3. False complaints

`submit_complaint()` rejects a complaint if the locally stored share actually
verifies, if the reason is inconsistent, or if its session/transcript binding is
wrong. This is useful for testing state and replay behavior.

It is not a real defense against a remote malicious participant. The session
simulator has a privileged view of every share; distributed participants do not.
Therefore Version 0.3 does not claim public blame or Byzantine agreement.

## 4. Dealer response

`dealer_respond(i, corrected_share)` handles one active complaint:

1. The corrected share must still be labelled with participant $i$.
2. It is checked against the original, already broadcast commitment vector.
3. If valid, it replaces the bad local share and status becomes `resolved`.
4. If invalid, the complaint remains open.

The dealer cannot resolve a complaint by changing the commitments; that would
be commitment equivocation and causes abort. The response is described as
private because the replacement values are not written to the public record.

## 5. Qualification rule

Version 0.3 uses a strict educational rule:

$$
\text{qualify dealer}
\iff
\text{every participant is accepted or resolved}.
$$

Calling `finalize()` in state `verified` produces `qualified`. Calling it with
any open complaint produces `aborted`. Calling it before all participants have
been checked is an error.

This rule is intentionally simpler than many formal VSS protocols, which may
qualify a dealer based on thresholds, fault bounds, complaint counts, evidence,
timeouts, and a commonly agreed qualified set. Such rules must be taken from
the exact protocol being implemented; inventing a generic complaint threshold
would create an unproved construction.

## 6. Reconstruction after qualification

Only a qualified session permits reconstruction. The selected participant
identifiers are mapped to their final stored share pairs, every pair is verified
again in strict mode, and the Shamir secret components are interpolated.

This second verification is defensive programming. It detects accidental local
mutation between qualification and reconstruction; it is not a substitute for
authenticated storage in a real system.

## 7. Successful repair example

```python
received = list(distribution.shares)
honest = received[1]

# Simulate corruption of participant 2's secret component.
received[1] = PedersenShare(
    honest.x,
    honest.value + 1,
    honest.blinding,
)

session.distribute_shares(received)
session.verify_all()
assert session.state.value == "complaints-open"

response = session.dealer_respond(2, honest)
assert response.accepted
assert session.state.value == "verified"

session.finalize()
assert session.state.value == "qualified"
```

See `examples/vss_complaint_demo.py` for the full run.

## 8. Abort example

If the dealer gives no valid replacement, finalization is terminal:

```python
session.verify_all()
session.finalize()

assert session.state.value == "aborted"
```

Reconstruction then raises an error. This behavior is shown in
`examples/vss_abort_demo.py`.

## 9. Why this matters for DKG

Distributed key generation runs a VSS-like sharing from several dealers and
combines only qualified contributions. If different participants use different
qualified-dealer sets, they may derive incompatible public keys and shares.
The complaint and qualification layer therefore cannot be added casually after
the DKG mathematics; it is part of the protocol's correctness and security.

Version 0.3 stops before DKG so that these state transitions are visible and
tested independently.

Next: [Version 0.3 security boundary](16-version-03-security-boundary.md).
