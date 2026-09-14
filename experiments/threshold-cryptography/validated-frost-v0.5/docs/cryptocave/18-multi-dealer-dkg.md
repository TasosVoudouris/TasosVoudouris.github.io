# The Version 0.4 multi-dealer construction

`cryptocave_sss/dkg.py` composes the corrected Shamir, Pedersen, Feldman, and VSS
session modules without hiding their boundaries.

## 1. Common parameters

The 3-out-of-5 lesson uses

$$
q=41,\qquad p=83,\qquad g=4,\qquad h=59.
$$

Every secret polynomial, blinding polynomial, share, and exponent is in
$\mathbb F_{41}$. Both public commitment vectors lie in the order-41 subgroup
of $\mathbb Z_{83}^{*}$.

These parameters make exhaustive tests possible. They provide no real security.

## 2. Dealer package

Dealer $P_i$ independently samples two degree-at-most-$(\tau-1)$ polynomials:

$$
f_i(X)=\sum_{k=0}^{\tau-1}a_{i,k}X^k,
\qquad
r_i(X)=\sum_{k=0}^{\tau-1}b_{i,k}X^k.
$$

Every coefficient, including $a_{i,0}$ and $b_{i,0}$, is random. This differs
from ordinary VSS, where the dealer is given a pre-existing secret.

The dealer prepares two commitment vectors:

$$
C_{i,k}=g^{a_{i,k}}h^{b_{i,k}}
$$

and

$$
A_{i,k}=g^{a_{i,k}}.
$$

The `DKGDealerPackage` stores both for the single-process simulation. Their
logical publication is staged: $C_{i,k}$ belongs to hidden qualification, while
$A_{i,k}$ is checked only after the common qualified set has been fixed.

The raw coefficients are not stored in the package. `create_dealer_package()`
uses them to calculate shares and commitments, then lets the local variables go
out of scope.

## 3. Hidden qualification round

Each package creates a separate Version 0.3 `VSSSession` with a domain-separated
sub-session identifier:

```text
global-session-id / dealer-i
```

Participant $P_j$ receives

$$
s_{i,j}=f_i(j),
\qquad
t_{i,j}=r_i(j),
$$

and checks

$$
g^{s_{i,j}}h^{t_{i,j}}
\stackrel{?}{=}
\prod_{k=0}^{\tau-1}C_{i,k}^{j^k}.
$$

A valid private replacement may resolve a complaint. An unresolved complaint
excludes that dealer before the qualified set is agreed.

## 4. Common qualification

Let $Q$ contain the dealers whose Pedersen sessions qualified. Every participant
view must equal exactly this sorted tuple. Missing participants, duplicated
dealers, unknown dealers, or a different tuple cause global abort.

The default local policy also requires at least $\tau$ qualified dealers. This
is a project policy chosen to avoid continuing a 3-out-of-5 lesson after most
dealer sessions have failed. It is not a theorem that DKG always requires
$|Q|\geq\tau$.

## 5. Public-key extraction round

After $Q$ is fixed, every $i\in Q$ exposes the vector $A_{i,k}$. Each recipient
secret component is checked again:

$$
g^{s_{i,j}}
\stackrel{?}{=}
\prod_{k=0}^{\tau-1}A_{i,k}^{j^k}.
$$

This links the public-key contribution to the same secret shares accepted in the
hidden Pedersen phase. Version 0.4 aborts if this equation fails for any already
qualified dealer. It does not silently remove that dealer after seeing the
public vector.

The complete GJKR protocol describes a public-reconstruction recovery for this
case. Implementing it safely requires additional broadcast, complaint evidence,
and fault-bound logic, so it is outside this version.

## 6. Local share aggregation

Each participant adds the private pairs received from $Q$:

$$
x_j=\sum_{i\in Q}s_{i,j}\pmod q,
\qquad
\rho_j=\sum_{i\in Q}t_{i,j}\pmod q.
$$

`DKGParticipantShare` records $(j,x_j,\rho_j)$ and the exact source-dealer tuple
$Q$. That source binding prevents a key share derived from one qualified set
from being confused with a share derived from another.

## 7. Commitment aggregation

Homomorphism gives

$$
C_k=\prod_{i\in Q}C_{i,k}
=g^{\sum_i a_{i,k}}h^{\sum_i b_{i,k}},
$$

and

$$
A_k=\prod_{i\in Q}A_{i,k}
=g^{\sum_i a_{i,k}}.
$$

The final pair $(x_j,\rho_j)$ must satisfy the aggregate Pedersen equation, and
$x_j$ must independently satisfy the aggregate value equation. Version 0.4
verifies all final shares under both vectors before returning a result.

## 8. Code map

| Protocol object | Version 0.4 class |
|---|---|
| Dealer's two vectors | `DKGDealerCommitments` |
| Dealer's complete local output | `DKGDealerPackage` |
| One dealer decision | `DealerOutcome` |
| Final participant key share | `DKGParticipantShare` |
| Dual final verification | `DKGShareVerification` |
| Public DKG record | `DKGTranscript` |
| Successful distributed state | `DKGResult` |
| Offline coordinator | `MultiDealerDKG` |

## 9. Minimal flow

```python
dkg = MultiDealerDKG.educational(session_id="lesson-dkg")
packages = [
    dkg.create_dealer_package(i)
    for i in dkg.shamir.participant_ids
]
result = dkg.run(packages)

assert all(item.accepted for item in result.verify_all())
```

This path obtains a public key and distributed key shares without calling a
reconstruction method.

Next: [Qualification, public-key derivation, and audit](19-dkg-qualification-and-public-key.md).
