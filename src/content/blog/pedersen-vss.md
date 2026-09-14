---
title: "Pedersen Verifiable Secret Sharing"
description: "Develop Pedersen VSS with hiding commitments, verification equations, binding assumptions, implementation mapping, and the limits of local share verification."
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
seriesOrder: 4
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Feldman VSS lets every participant test whether a received Shamir share agrees
with one committed polynomial. Its coefficient commitments are
$A_j=g^{a_j}$, so the constant commitment is $A_0=g^s$. That value is not
hiding: equal secrets give equal $A_0$, and a low-entropy secret can be guessed
by computing candidate commitments.

Pedersen VSS keeps the verification structure while adding an independent
blinding polynomial. This chapter derives the construction used in
`cryptocave_sss/pedersen.py`, explains its guarantees, and states exactly why
the tiny parameters are not secure.

## 1. Algebraic setting

Let $G$ be a cyclic group of prime order $q$. Choose distinct generators
$g,h\in G$. The Shamir field and the group scalar field must be the same
$\mathbb F_q$.

Pedersen commitments to a pair $(m,r)\in\mathbb F_q^2$ are

$$
\operatorname{Com}(m;r)=g^m h^r.
$$

The semicolon is a reminder that $m$ is the committed message and $r$ is fresh
blinding randomness. Both are exponents modulo $q$.

Two setup facts matter:

1. $g$ and $h$ must lie in the same order-$q$ group.
2. No participant should know $\alpha=\log_g(h)$.

The second fact is essential for binding. Merely checking that both elements
have the right order is not enough.

## 2. Dealer construction

For a $\tau$-out-of-$n$ sharing, the dealer samples two independent
degree-at-most-$(\tau-1)$ polynomials:

$$
f(X)=a_0+a_1X+\cdots+a_{\tau-1}X^{\tau-1},
$$

$$
r(X)=b_0+b_1X+\cdots+b_{\tau-1}X^{\tau-1}.
$$

The secret is $a_0=s$. Every $a_j$ for $j>0$ is uniform in $\mathbb F_q$, and
every $b_j$, including $b_0$, is uniform and independent.

The dealer broadcasts one commitment per coefficient pair:

$$
C_j=g^{a_j}h^{b_j}
\qquad (0\leq j<\tau).
$$

Participant $i$, whose nonzero public identifier is $x_i$, privately receives

$$
s_i=f(x_i),
\qquad
t_i=r(x_i).
$$

The value $s_i$ is the ordinary Shamir share. The value $t_i$ is the
corresponding blinding share. Both are needed for verification, but only the
$s_i$ values are interpolated to reconstruct the secret.

## 3. Verification equation

Participant $i$ checks

$$
g^{s_i}h^{t_i}
\stackrel{?}{=}
\prod_{j=0}^{\tau-1}C_j^{x_i^j}.
$$

For an honest share, expand the right-hand side:

$$
\begin{aligned}
\prod_{j=0}^{\tau-1}C_j^{x_i^j}
&=\prod_{j=0}^{\tau-1}
   \left(g^{a_j}h^{b_j}\right)^{x_i^j}\\
&=g^{\sum_j a_jx_i^j}
  h^{\sum_j b_jx_i^j}\\
&=g^{f(x_i)}h^{r(x_i)}\\
&=g^{s_i}h^{t_i}.
\end{aligned}
$$

This is the same homomorphic coefficient-evaluation idea as Feldman, applied to
two polynomials at once.

## 4. What is hidden

Consider the constant commitment

$$
C_0=g^s h^{b_0}.
$$

For any fixed secret $s$, if $b_0$ is uniform in $\mathbb F_q$, then $h^{b_0}$
ranges uniformly over $G$. Multiplication by the fixed element $g^s$ only
permutes the group. Therefore $C_0$ has the same distribution for every
possible $s$.

The same reasoning applies independently to every coefficient commitment
$C_j$. This is information-theoretic hiding at the commitment level: even an
unbounded observer cannot distinguish the committed coefficient from the
commitment alone, provided the blinding coefficient is uniform and private.

Version 0.3 tests this directly in the toy group. For each fixed secret, all 41
possible blinding values produce all 41 subgroup elements, and the resulting
set is identical for different secrets.

Hiding does not mean that participants may publish their two share components.
A private share pair is still secret protocol data.

## 5. What makes a commitment binding

Suppose an attacker knows $h=g^\alpha$. Then

$$
g^m h^r = g^{m+\alpha r}.
$$

For any nonzero change $\Delta$, the attacker can construct another opening

$$
m'=m+\Delta,
\qquad
r'=r-\Delta\alpha^{-1},
$$

and obtain the same commitment:

$$
g^{m'}h^{r'}=g^m h^r.
$$

Consequently, Pedersen commitments are computationally binding only when
finding the relation between $g$ and $h$ is infeasible and nobody received that
relation as a setup trapdoor.

For a real implementation, parameter generation should use a reviewed group
and a standard, domain-separated hash-to-group or ceremony procedure. It should
not select a secret exponent $\alpha$ and then publish $h=g^\alpha$ while one
party retains $\alpha$.

## 6. Why the Version 0.3 group is deliberately insecure

The directly inspectable example uses

$$
p=83,\qquad q=41,\qquad g=4,\qquad h=59.
$$

Both $g$ and $h$ have order 41 modulo 83, but

$$
h=g^{17}\pmod{83}.
$$

The relation is public in the lesson and would be trivial to recover by trying
at most 41 exponents anyway. The file `pedersen_toy_trapdoor_demo.py` constructs
two different openings of the same commitment. This is not a defect hidden by
the code; it demonstrates why correct group membership and secure generator
setup are separate requirements.

## 7. Implementation map

| Mathematical object | Version 0.3 object |
|---|---|
| $(p,q,g,h)$ | `PedersenParameters` |
| $(s_i,t_i)$ | `PedersenShare` |
| $(C_0,\ldots,C_{\tau-1})$ | `PedersenCommitments` |
| Dealer output | `PedersenDistribution` |
| Verification decision | `PedersenShareVerification` |
| Accepted and rejected sets | `PedersenVerificationReport` |
| Verify then interpolate | `reconstruct_verified()` |

`PedersenVSS.share(secret)` samples both polynomials once. It does not sample a
new polynomial for each participant. `reconstruct_verified()` discards rejected
share pairs and converts accepted secret components into the explicit
`Share(x,y)` labels used by the corrected Shamir implementation.

## 8. Minimal code path

```python
import random

from cryptocave_sss.pedersen import PedersenVSS

vss = PedersenVSS.educational(rng=random.Random(7))
distribution = vss.share(17)

report = vss.verify_shares(
    distribution.shares,
    distribution.commitments,
)
assert report.all_accepted

result = vss.reconstruct_verified(
    distribution.subset([1, 3, 5]),
    distribution.commitments,
)
assert result.secret == 17
```

The seeded generator is for repeatable documentation. The default constructor
uses operating-system randomness.

## 9. What local verification does not solve

The equation proves consistency only relative to the commitment vector seen by
that participant. A malicious dealer may still send different commitment
vectors to different participants unless a broadcast or agreement mechanism
prevents equivocation. Participants also need authenticated session identities,
message origins, complaint rules, timeouts, and a common qualification result.

Those protocol states are introduced in Version 0.3 as an offline model in
`vss_session.py`; they are not claimed to be a deployed distributed protocol.

Next: [Feldman and Pedersen compared](/series/threshold-cryptography-engineering/).
