# From DKG output to a threshold signature

Version 0.4 ended with a distributed secret that normal code never
reconstructed. Version 0.5 gives that secret its first operational use: a
threshold of participants can jointly create a Schnorr signature while every
participant keeps only its own DKG share.

> **Learning implementation only.** The code follows the two-round FROST data
> flow, but it uses an order-41 teaching group and is not an RFC 9591
> ciphersuite. It must not protect real keys, accounts, transactions, models,
> medical data, or authentication systems.

## Learning goals

After this chapter you should be able to explain:

- which Version 0.4 values become FROST group information;
- why the public verification share $Y_i$ is different from the private share
  $x_i$;
- how a subset signs without reconstructing $x$;
- why threshold signing is preferable to reconstruct-then-sign;
- which responsibilities belong to the coordinator and which belong to each
  signer; and
- why this local simulation is still far from a deployed signing service.

## Prerequisites

Read these pages first:

1. [Shamir secret sharing](03-shamir-secret-sharing.md)
2. [Feldman VSS](09-feldman-vss.md)
3. [From VSS to DKG](17-from-vss-to-dkg.md)
4. [The multi-dealer construction](18-multi-dealer-dkg.md)
5. [DKG qualification and public-key derivation](19-dkg-qualification-and-public-key.md)

## The Version 0.4 output

Let the scalar field be $\mathbb{F}_q$ and let $g$ generate a group of order
$q$. The DKG produces a degree-$(t-1)$ polynomial

$$
f(X)=a_0+a_1X+\cdots+a_{t-1}X^{t-1}.
$$

The secret signing key exists mathematically as

$$
x=f(0)=a_0,
$$

but normal DKG execution does not compute it. Participant $P_i$ receives the
private scalar

$$
x_i=f(i).
$$

The aggregate value-commitment vector is

$$
A_k=g^{a_k},\qquad 0\leq k<t.
$$

It exposes two forms of public key material:

$$
Y=A_0=g^x
$$

and, for every participant identifier $i$,

$$
Y_i=\prod_{k=0}^{t-1}A_k^{i^k}=g^{f(i)}=g^{x_i}.
$$

`FrostGroupInfo.from_dkg()` derives exactly these values. It does not inspect a
reconstructed group secret.

| DKG value | FROST name | Visibility | Purpose |
|---|---|---|---|
| `participant_share.secret_share` | $x_i$ / `sk_i` | Private to signer $i$ | Create that signer's response scalar |
| `value_commitments.expected_share_commitment(i)` | $Y_i$ / `PK_i` | Public | Verify signer $i$'s response |
| `result.public_key` | $Y$ / `PK` | Public | Verify the final Schnorr signature |
| `result.shamir.threshold` | $t$ | Public | Minimum signer count |
| participant identifiers | $i\in\mathbb{F}_q^*$ | Public | Lagrange interpolation labels |
| DKG transcript digest | group identifier | Public | Prevent mixing shares from another DKG view |

## Why reconstruct-then-sign is the wrong design

A tempting shortcut is:

1. collect $t$ shares;
2. interpolate $x$;
3. run an ordinary signature algorithm with $x$; and
4. delete $x$.

That shortcut creates a machine, process, or memory region containing the
complete signing key. Compromising that location defeats the threshold. It
also makes secure deletion and audit much harder.

FROST instead uses interpolation inside the signature equation. Signer $i$
multiplies its share by a public Lagrange coefficient $\lambda_i$ and returns
only a response share $z_i$. Summing the responses has the same algebraic
effect as using $x$, but no participant computes $x$.

Version 0.5 enforces this design with a test that replaces both Shamir
reconstruction methods with exceptions during the complete signing path.

## Roles

### Coordinator

The coordinator:

- chooses a signer subset containing at least $t$ participants;
- collects round-one nonce commitments;
- constructs one canonical signing package;
- distributes that same package to the selected signers;
- receives one signature share from every selected signer;
- validates every response equation;
- aggregates valid responses; and
- verifies the final signature under $Y$ before releasing it.

The coordinator does not receive $x_i$ or the private nonce scalars. RFC 9591
does not require it to hold private information.

### Signer

Signer $i$:

- holds $x_i$ and the common public group information;
- generates two fresh secret nonces for round one;
- publishes only their two group commitments;
- validates the complete round-two package and application payload;
- creates $z_i$;
- permanently deletes the nonce pair; and
- sends $z_i$ to the coordinator.

## The Version 0.5 object flow

```text
DKGResult
  -> FrostGroupInfo              public Y, Y_i, threshold, IDs, DKG digest
  -> FrostSigner                 one private x_i plus local nonce state
  -> NonceCommitment             public (i, D_i, E_i)
  -> FrostSigningPackage         message plus sorted commitment list
  -> FrostSignatureShare         public (i, z_i)
  -> FrostSigningResult          (R, z), checks, public transcript
```

The public transcript contains commitments, binding factors, challenge,
signature shares, and final signature. It deliberately omits key shares and
private nonces.

## Minimal transition from DKG to signing

```python
coordinator = FrostCoordinator.from_dkg(dkg_result)
signers = [
    FrostSigner.from_dkg(dkg_result, participant_id)
    for participant_id in (1, 3, 5)
]
```

Every constructor checks that:

- the DKG shares still verify;
- $Y$ and every $Y_i$ are valid non-identity subgroup elements;
- identifiers are distinct nonzero scalars smaller than $q$;
- the threshold is valid; and
- each private share satisfies $g^{x_i}=Y_i$.

The group secret is neither an input nor an output.

## Threat model at this layer

The mathematical FROST security model allows a malicious coordinator and fewer
than $t$ corrupted participants under its stated assumptions. This Version 0.5
code does **not** inherit that security result because its ciphersuite, network,
storage, language runtime, and DKG are educational.

Within the local model, the code demonstrates:

- correct honest signing for every 3-of-5 subset;
- validation and canonical ordering of public inputs;
- detection of an invalid $z_i$ with a participant identifier;
- final ordinary Schnorr verification;
- terminal nonce use; and
- binding to one DKG, session, counter, context, signer set, and payload.

It does not provide process isolation, authenticated transport, durable replay
state, constant-time operations, secure memory, or a standardized curve.

## Next reading

Continue with [Schnorr algebra and threshold interpolation](23-schnorr-and-threshold-interpolation.md),
then [the two-round FROST protocol](24-rfc9591-frost-protocol.md).

## Primary reference

D. Connolly, C. Komlo, I. Goldberg, and C. A. Wood, “The Flexible
Round-Optimized Schnorr Threshold (FROST) Protocol for Two-Round Schnorr
Signatures,” [RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html), 2024.
