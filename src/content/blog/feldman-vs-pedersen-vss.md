---
title: "Feldman vs. Pedersen VSS"
description: "Compare the leakage, hiding, binding, verification, and implementation tradeoffs of Feldman and Pedersen verifiable secret sharing."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Secret Sharing"
  - "Threshold Cryptography"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 5
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Feldman and Pedersen VSS share the same Shamir polynomial and the same basic
verification purpose, but their commitments expose different information and
rely on different assumptions.

## Construction summary

| Property | Feldman | Pedersen |
|---|---|---|
| Secret polynomial | $f(X)=\sum a_jX^j$ | $f(X)=\sum a_jX^j$ |
| Extra polynomial | None | $r(X)=\sum b_jX^j$ |
| Commitment | $A_j=g^{a_j}$ | $C_j=g^{a_j}h^{b_j}$ |
| Private data sent to party $i$ | $f(x_i)$ | $(f(x_i),r(x_i))$ |
| Verification left side | $g^{f(x_i)}$ | $g^{f(x_i)}h^{r(x_i)}$ |
| Constant commitment | $g^s$ | $g^sh^{b_0}$ |
| Hides low-entropy secret? | No | Yes, when $b_0$ is uniform |
| Exposes equality of repeated secrets? | Yes | No, except negligible/random collision |
| Binding basis | Discrete-log hardness | Discrete-log hardness and unknown $\log_g(h)$ |
| Extra private share bandwidth | None | One field element per participant |
| Extra setup concern | Valid order-$q$ generator | Valid generators with no known relation |

## What both constructions guarantee locally

Assume a participant receives a share and one fixed public commitment vector.
If verification succeeds, the share is consistent with some polynomial encoded
by that vector, subject to the relevant binding assumption. If at least
$\tau$ accepted shares come from one degree-at-most-$(\tau-1)$ polynomial,
Shamir interpolation recovers its constant term.

Neither equation alone guarantees that every participant saw the same vector.
Neither authenticates the dealer. Neither defines what the group should do when
a verification fails.

## Why Feldman remains useful

Feldman is the simpler teaching construction. One polynomial, one share value,
and one generator make its algebra easy to trace. It is also useful when the
committed value is already uniformly random, such as some internally generated
key material, and public equality leakage is acceptable within the complete
protocol design.

It is unsafe to describe Feldman commitments as confidential. Given a candidate
$m$, anyone can test whether $g^m=A_0$. Passwords, class labels, pixels,
diagnoses, and small counters are therefore especially unsuitable direct
inputs.

## Why Pedersen is the Version 0.3 default

Pedersen removes that commitment leakage without changing the Shamir secret
polynomial. The extra polynomial masks every public coefficient commitment, and
reconstruction still interpolates only the secret components.

The tradeoff is additional private data and a stronger setup obligation. If a
party knows $\log_g(h)$, it can equivocate between different openings. A code
review that checks only primality and subgroup membership cannot establish that
nobody knows this relation.

## Same secret, independent distributions

For Feldman:

$$
A_0^{(1)}=g^s=A_0^{(2)}.
$$

For Pedersen:

$$
C_0^{(1)}=g^sh^{b_0^{(1)}},
\qquad
C_0^{(2)}=g^sh^{b_0^{(2)}}.
$$

The independent blinding constants make the two Pedersen values independent
uniform group elements. They may coincide with probability $1/q$, but equality
does not reveal that the underlying secrets are equal. In the tiny group that
random collision probability is visibly large; in a production group it is
negligible.

## Version 0.3 code comparison

```python
feldman_distribution = feldman.share(17)
pedersen_distribution = pedersen.share(17)

feldman_result = feldman.verify_share(
    feldman_distribution.sharing.shares[0],
    feldman_distribution.commitments,
)

pedersen_result = pedersen.verify_share(
    pedersen_distribution.shares[0],
    pedersen_distribution.commitments,
)
```

The explicit class names prevent accidentally passing a Feldman `Share` to a
Pedersen verifier or discarding the Pedersen blinding component.

## Decision rule for this learning project

- Use `feldman.py` to understand coefficient commitments and demonstrate
  low-entropy leakage.
- Use `pedersen.py` for the next protocol lessons, while retaining the prominent
  toy-parameter warning.
- Use neither module in production. A real protocol should select a maintained,
  audited implementation and standardized group/encoding rules.

Next: [VSS sessions, transcripts, and broadcast](/series/threshold-cryptography-engineering/).
