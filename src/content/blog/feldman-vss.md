---
title: "Feldman Verifiable Secret Sharing"
description: "Derive Feldman commitments and the share-verification equation, explain the matching field/group orders, and make explicit what Feldman VSS reveals and guarantees."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Secret Sharing"
  - "Threshold Cryptography"
  - "Public-Key Cryptography"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 2
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Feldman VSS commits to every coefficient of the Shamir polynomial. Let
$\mathbb G=\langle g\rangle$ be a cyclic group of prime order $q$, and let the
Shamir polynomial be defined over $\mathbb F_q$:

$$
f(X)=\sum_{j=0}^{\tau-1}a_jX^j,
\qquad a_0=s.
$$

The dealer publishes

$$
C_j=g^{a_j}\in\mathbb G
$$

and privately sends $s_i=f(x_i)$ to participant $P_i$.

## Verification equation

Participant $P_i$ accepts its share when

$$
g^{s_i}
\stackrel{?}{=}
\prod_{j=0}^{\tau-1} C_j^{x_i^j}.
$$

Correctness follows immediately:

$$
\prod_{j=0}^{\tau-1} C_j^{x_i^j}
=
\prod_{j=0}^{\tau-1}(g^{a_j})^{x_i^j}
=
g^{\sum_{j=0}^{\tau-1}a_jx_i^j}
=
g^{f(x_i)}
=
g^{s_i}.
$$

Changing the share changes the left side while the right side remains bound to
the published commitments. Changing a commitment causes honest shares to fail
against the altered vector.

## The two moduli must match correctly

The Shamir coefficients and shares live in $\mathbb F_q$. Commitments live in a
group of order $q$, which may be represented inside arithmetic modulo a
different prime $p$. Thus:

$$
q\mid(p-1),
\qquad
\operatorname{ord}(g)=q.
$$

Version 0.2 uses the inspectable parameters

$$
q=41,
\qquad
p=83,
\qquad
g=4,
$$

for which $4^{41}\equiv1\pmod{83}$ and $4\neq1$. Because $41$ is prime, $g$
has order exactly $41$. These values are intentionally insecure and exist only
so every computation fits on screen.

The original secp256k1 code follows the same high-level equation: its curve
order supplies $q$, and scalar multiplication $a_jG$ is the additive-group
notation corresponding to $g^{a_j}$. Version 0.2 uses a small multiplicative
group to avoid third-party dependencies and make the equation transparent.

## Code correspondence

The coefficient commitments are created once:

```python
commitments = tuple(
    parameters.commit(coefficient)
    for coefficient in coefficients
)
```

Verification computes both sides independently:

```python
left = parameters.commit(share.y)
right = commitments.expected_share_commitment(share.x)
accepted = left == right
```

The dealer samples exactly one polynomial per distribution. All participants'
shares and the commitment vector refer to that same polynomial.

## What is public and what remains private

The following values are public:

- group parameters $(p,q,g)$;
- participant identifiers $x_i$;
- coefficient commitments $(C_0,\ldots,C_{\tau-1})$.

Each share $s_i$ is private to participant $P_i$. The secret and random
coefficients are not published.

## Feldman commitments are not hiding

The first commitment is

$$
C_0=g^{a_0}=g^s.
$$

It is the same for every sharing of the same secret. An observer can therefore
recognize repeated secrets. If the secret comes from a small dictionary, the
observer can compute $g^{s'}$ for every candidate and compare it with $C_0$.

With a large group and a uniformly random scalar, recovering the exponent is
intended to be hard under the discrete-log assumption. This does not make
Feldman suitable for passwords, binary diagnoses, pixel values, or other
low-entropy data. Pedersen VSS introduces blinding commitments to remove this
leakage.

Next: [Broadcast, complaints, and the protocol boundary](/series/threshold-cryptography-engineering/).
