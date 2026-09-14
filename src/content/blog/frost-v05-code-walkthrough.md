---
title: "Educational FROST Implementation: Code Walkthrough"
description: "Trace the validated teaching implementation from DKG output through round one, package construction, context binding, round two, partial verification, aggregation, and final verification."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Threshold Cryptography"
  - "Cryptographic Engineering"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
  - "frost"
  - "rfc-9591"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 23
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
The implementation lives in `cryptocave_sss/frost.py`. It is intentionally one
readable module so the data path can be followed without a framework, network,
database, or third-party dependency.

## Learning goals

You should finish this page able to:

- trace an honest signing call from DKG output to final signature;
- distinguish public dataclasses from private signer state;
- locate each RFC equation in the code;
- run the low-level and convenience APIs; and
- understand every validation and abort boundary.

## Module map

| Code item | Responsibility |
|---|---|
| `ToyFROSTSuite` | Toy group operations, canonical encodings, $H_1$–$H_5$ |
| `FrostGroupInfo` | Public $Y$, $Y_i$, threshold, identifiers, DKG binding |
| `NonceCommitment` | Public round-one $(i,D_i,E_i)$ plus local lookup ID |
| `FrostSigningPackage` | Canonical round-two request and application envelope |
| `FrostSigner` | One private share and one-time nonce state |
| `FrostCoordinator` | Package creation, response verification, aggregation |
| `FrostSignatureShare` | Participant response $(i,z_i)$ |
| `FrostSignature` | Final ordinary Schnorr pair $(R,z)$ |
| `FrostSigningTranscript` | Public completed-session record |
| `run_frost_signing` | Small two-round convenience orchestration |

## 1. Create a DKG result

```python
dkg = MultiDealerDKG.educational(session_id="lesson-dkg")
packages = [
    dkg.create_dealer_package(i)
    for i in dkg.shamir.participant_ids
]
dkg_result = dkg.run(packages)
```

No seeded generator is supplied here, so dealer creation defaults to operating-
system randomness. Examples and tests pass seeded `random.Random` instances
only so their printed values repeat.

## 2. Derive common group information

```python
coordinator = FrostCoordinator.from_dkg(dkg_result)
signer_1 = FrostSigner.from_dkg(dkg_result, 1)
signer_3 = FrostSigner.from_dkg(dkg_result, 3)
signer_5 = FrostSigner.from_dkg(dkg_result, 5)
```

`FrostGroupInfo.from_dkg()` derives:

```text
suite
threshold
participant_ids
group_public_key Y
verifying_shares Y_i
dkg_transcript_digest
```

It checks every DKG share, computes $Y_i$ from the aggregate value commitment
vector, and rejects identity keys. Each signer also checks

$$
g^{x_i}=Y_i.
$$

The coordinator and signers compare the complete immutable group information,
not only $Y$.

## 3. Round one

```python
commitment_1 = signer_1.commit("signing-001", counter=1)
commitment_3 = signer_3.commit("signing-001", counter=1)
commitment_5 = signer_5.commit("signing-001", counter=1)
```

For each signer, `commit()`:

1. asks the byte source for 32 fresh bytes;
2. computes $d_i=H_3(\text{random}\|\operatorname{enc}(x_i))$;
3. repeats independently for $e_i$;
4. computes $D_i=g^{d_i}$ and $E_i=g^{e_i}$;
5. stores $(d_i,e_i)$ in `_pending_nonces`; and
6. returns only `NonceCommitment(i, D_i, E_i, nonce_id)`.

The default byte source is `secrets.token_bytes`. A caller-supplied source must
return exactly 32 bytes.

### Why nonzero retry appears

RFC ciphersuites map to enormous scalar fields, so sampling zero is negligible.
With $q=41$, it occurs frequently enough to break a demonstration because
$g^0$ is the identity and RFC element serialization rejects identity elements.
The toy suite retries when $H_3$ returns zero. This is an explicit accommodation
for the tiny group, not a claim of RFC wire compatibility.

## 4. Package construction

```python
package = coordinator.create_signing_package(
    session_id="signing-001",
    counter=1,
    application_context="CryptoCave release approval",
    message=b"approve artifact 7",
    commitments=(commitment_5, commitment_1, commitment_3),
)
```

The coordinator sorts the commitments into identifiers `(1, 3, 5)` and
validates:

- type and participant set;
- threshold and upper bounds;
- duplicates and unknown identifiers;
- subgroup membership and non-identity elements;
- prior use of the same public commitment; and
- whether the derived group commitment can be serialized.

The package's public digest covers the raw payload and every public field.

## 5. The application envelope

RFC 9591 signs an arbitrary byte string `msg`. Version 0.5 supplies a framed
application envelope as that byte string:

```text
protocol label
toy suite context string
session_id
counter
application_context
FrostGroupInfo digest
selected signer identifiers
raw application payload
```

Every variable-length field has an eight-byte length prefix. This avoids
ambiguous concatenations such as `(ab, c)` and `(a, bc)` producing the same
bytes.

The final signature therefore authenticates the envelope. To verify it with
the ordinary helper, use:

```python
signed_message = package.message_to_sign(coordinator.group_info.suite)
ok = verify_schnorr_signature(
    signed_message,
    signature,
    coordinator.group_info.group_public_key,
    coordinator.group_info.suite,
)
```

Passing only `package.message` is deliberately different and normally fails.

## 6. Binding factors and challenge

`compute_binding_factors()` implements

$$
\rho_i=H_1(
\operatorname{enc}(Y)\|H_4(m)\|H_5(\operatorname{enc}(L))\|
\operatorname{enc}(i)).
$$

`compute_group_commitment()` implements

$$
R=\prod_iD_iE_i^{\rho_i}.
$$

`compute_challenge()` implements

$$
c=H_2(\operatorname{enc}(R)\|\operatorname{enc}(Y)\|m).
$$

All signers and the coordinator call the same pure helper functions.

## 7. Round two

```python
share_1 = signer_1.sign(package)
share_3 = signer_3.sign(package)
share_5 = signer_5.sign(package)
```

Before accessing a private nonce, `sign()` checks:

- exact group-information digest;
- valid selected participant count;
- canonical commitment list;
- the signer is selected;
- the `nonce_id` exists locally;
- the package contains the signer's unchanged commitment;
- the local session and counter match; and
- the optional application message validator approves.

It then computes $\rho_i$, $R$, $c$, and $\lambda_i$. Immediately before
returning the response, it removes the nonce record from the local dictionary.

```python
z_i = (
    d_i
    + e_i * rho_i
    + lambda_i * x_i * challenge
) % q
```

A second `sign(package)` call raises `NonceReuseError` because the secret pair
no longer exists.

## 8. Application message validation

RFC 9591 recommends preventing signers from becoming arbitrary signing oracles.
Version 0.5 supports one small callback:

```python
def approves(package):
    return package.message.startswith(b"APPROVED:")

signer = FrostSigner.from_dkg(
    dkg_result,
    participant_id=1,
    message_validator=approves,
)
```

The callback should represent application-specific parsing, authorization,
limits, consent, or policy. Returning `False` raises `MessageRejectedError` and
deletes the nonce pair associated with the rejected package.

The callback interface is educational. A real policy engine needs authenticated
context, deterministic parsing, versioned schemas, user intent, and an audit
trail.

## 9. Partial verification

```python
check = coordinator.verify_signature_share(package, share_1)
```

The result records:

- `participant_id`;
- `accepted`;
- `left = g^z_i`;
- `right = D_i E_i^rho_i Y_i^(c lambda_i)`; and
- a reason string.

No private field is needed. An invalid response can be attributed only if the
channel proves who sent it; local integer identifiers are not identities.

## 10. Aggregation and final verification

```python
result = coordinator.aggregate(
    package,
    (share_1, share_3, share_5),
)
```

Aggregation requires exactly one response for every selected participant. It
rejects missing, duplicate, extra, wrong-package, unknown, noncanonical, or
equation-invalid responses. The package becomes closed on the first aggregation
attempt.

For valid shares:

```python
z = sum(share.value for share in shares) % q
signature = FrostSignature(R, z)
```

The coordinator calls the ordinary verifier before returning the result.

## 11. Public transcript

`FrostSigningTranscript` records:

- protocol/version;
- session/counter/context;
- group-info and package digests;
- raw-payload and signed-envelope digests;
- selected identifiers and public nonce commitments;
- binding factors;
- group commitment and challenge;
- public signature shares;
- final signature; and
- final-verification result.

It does not record $x_i$, $d_i$, or $e_i$. The transcript digest is an unsigned
identifier, not participant authentication or non-repudiation evidence.

## 12. Convenience API

```python
run = run_frost_signing(
    coordinator,
    signers,
    session_id="signing-001",
    counter=1,
    application_context="CryptoCave release approval",
    message=b"approve artifact 7",
)
```

This function performs both rounds and returns both `run.package` and
`run.result`. If any stage fails, it conservatively discards unused nonce state
from all selected signer objects.

Use `examples/frost_demo.py` to learn the two explicit rounds. Use
`examples/frost_simple_api_demo.py` only after that flow is clear.

## Direct commands

From the project root:

```powershell
python .\cryptocave_sss\frost.py
python .\examples\frost_demo.py
python .\examples\frost_simple_api_demo.py
python .\tests\test_frost.py
```

All active modules have no third-party dependency and require Python 3.10 or
newer.
