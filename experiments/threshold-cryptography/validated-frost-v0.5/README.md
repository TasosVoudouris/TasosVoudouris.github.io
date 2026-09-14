# CryptoCave Threshold Cryptography — Version 0.5

Version 0.5 connects the Version 0.4 distributed key shares to a complete,
readable two-round threshold Schnorr/FROST signing lesson.

A threshold subset publishes one-time nonce commitments, validates one common
signing package, produces individually verifiable signature shares, and
aggregates them into an ordinary Schnorr signature under the DKG public key.
Normal signing never reconstructs the group secret.

> **Educational use only.** This project uses an intentionally tiny order-41
> group and a custom teaching ciphersuite. It is not RFC 9591 compatible,
> constant-time, distributed, audited, or production secure. Never use it for
> real keys, authentication, transactions, money, models, personal data,
> medical data, or infrastructure.

## Standards position

The round structure and equations follow
[RFC 9591](https://www.rfc-editor.org/rfc/rfc9591.html):

- two secret nonces and two public commitments per signer;
- one commitment round and one signature-share round;
- ascending participant commitment lists;
- domain-separated $H_1$–$H_5$ roles;
- signer-specific binding factors;
- Lagrange interpolation at zero;
- per-share verification; and
- ordinary final Schnorr verification.

The implementation does **not** use one of RFC 9591's named ciphersuites. Its
group, encodings, hash-to-scalar rule, storage, and local communication are
teaching substitutes. See the detailed
[conformance map](docs/cryptocave/27-rfc9591-conformance-map.md).

## What Version 0.5 adds

- `cryptocave_sss/frost.py` with one directly runnable implementation;
- public FROST group information derived from `DKGResult`;
- public verification shares $Y_i=g^{x_i}$ derived from DKG commitments;
- RFC-shaped fresh-randomness-plus-key-share nonce generation;
- strict one-time nonce state and explicit reuse errors;
- coordinator tracking of previously issued public commitments;
- canonical round-two signing packages;
- an application envelope binding protocol, suite, session, counter, purpose,
  DKG group, signer set, and raw payload;
- an optional per-signer application message-policy callback;
- RFC-style binding-factor and group-commitment calculations;
- threshold Schnorr response shares using public Lagrange coefficients;
- individual response verification before aggregation;
- final ordinary Schnorr verification under one group public key;
- canonical public signing transcripts with no private nonce/key-share fields;
- explicit two-round, convenience API, nonce reuse, bad-share, context-binding,
  and message-policy examples;
- 44 FROST-specific tests, bringing the full suite to 141; and
- seven detailed CryptoCave website chapters.

Versions 0.1–0.4 remain intact. Learners can study finite fields, Shamir,
Feldman, Pedersen, VSS sessions, DKG, and FROST as separate layers.

## Project structure

```text
CryptoCave-Threshold-Cryptography-v0.5/
├── cryptocave_sss/
│   ├── field.py
│   ├── shamir.py
│   ├── feldman.py
│   ├── pedersen.py
│   ├── vss_session.py
│   ├── dkg.py
│   ├── frost.py
│   └── ...
├── examples/
│   ├── frost_demo.py
│   ├── frost_simple_api_demo.py
│   ├── frost_nonce_reuse_demo.py
│   ├── frost_bad_share_demo.py
│   ├── frost_context_binding_demo.py
│   ├── frost_message_policy_demo.py
│   └── ...
├── tests/
│   ├── test_frost.py
│   └── ...
├── docs/cryptocave/
├── legacy/
├── SECURITY.md
├── VALIDATION.md
├── RUNNING_EACH_FILE.md
└── INTEGRATION.md
```

`legacy/` contains sanitized, quarantined provenance from the earlier VSS
archive. It is not part of the active implementation.

## Requirements

- Python 3.10 or newer
- no third-party dependency for the active code
- PowerShell, Command Prompt, or a terminal

## Quick start

Extract the ZIP, open PowerShell inside the project folder, and run:

```powershell
python .\cryptocave_sss\frost.py
python .\examples\frost_demo.py
python .\examples\frost_simple_api_demo.py
python .\tests\test_frost.py
python -m unittest discover -v
python .\examples\run_all.py
```

Expected complete-suite ending:

```text
Ran 141 tests
OK
```

## Minimal complete signing run

```python
from cryptocave_sss.frost import (
    FrostCoordinator,
    FrostSigner,
    run_frost_signing,
)

coordinator = FrostCoordinator.from_dkg(dkg_result)
signers = [
    FrostSigner.from_dkg(dkg_result, participant_id)
    for participant_id in (1, 3, 5)
]

run = run_frost_signing(
    coordinator,
    signers,
    session_id="release-signing-001",
    counter=1,
    application_context="CryptoCave release approval",
    message=b"approve artifact 7",
)

print(run.package.participant_ids)
print(run.result.signature)
print(run.result.transcript.final_verified)
```

Default nonce generation uses operating-system randomness. Seeded generators
in the repository are confined to reproducible examples and tests.

## The two rounds explicitly

```python
# Round 1: secret nonces remain inside each signer object.
commitments = [
    signer.commit("release-signing-001", counter=1)
    for signer in signers
]

# The coordinator creates one canonical package.
package = coordinator.create_signing_package(
    session_id="release-signing-001",
    counter=1,
    application_context="CryptoCave release approval",
    message=b"approve artifact 7",
    commitments=commitments,
)

# Round 2: every signer validates the same package and burns its nonce pair.
signature_shares = [signer.sign(package) for signer in signers]

# Every z_i is checked before the final z is calculated.
result = coordinator.aggregate(package, signature_shares)
```

Use this explicit form while learning. The convenience function preserves the
same package and result objects.

## Core equations

For selected signer identifiers $S$, the Lagrange coefficient is

$$
\lambda_i^S=
\prod_{j\in S,\,j\ne i}\frac{j}{j-i}\pmod q.
$$

Signer $i$ creates one-time commitments

$$
D_i=g^{d_i},\qquad E_i=g^{e_i}.
$$

After the full commitment list and message are fixed, it derives $\rho_i$. The
group commitment is

$$
R=\prod_{i\in S}D_iE_i^{\rho_i}.
$$

The challenge is

$$
c=H_2(\operatorname{enc}(R)\|\operatorname{enc}(Y)\|m).
$$

Signer $i$ returns

$$
z_i=d_i+e_i\rho_i+\lambda_i^Sx_ic\pmod q.
$$

The coordinator checks

$$
g^{z_i}\stackrel{?}{=}
D_iE_i^{\rho_i}Y_i^{c\lambda_i^S}.
$$

It aggregates

$$
z=\sum_{i\in S}z_i\pmod q
$$

and verifies the ordinary Schnorr equation

$$
g^z\stackrel{?}{=}RY^c.
$$

## Exact message being signed

The raw `message` is wrapped in an unambiguous, length-prefixed application
envelope containing:

1. CryptoCave protocol/version label;
2. toy suite context string;
3. session identifier;
4. counter;
5. application context/purpose;
6. complete public group-information digest;
7. selected participant identifiers; and
8. raw payload.

This envelope is the FROST `msg`. The final signature is therefore verified
with `package.message_to_sign(suite)`, not with the raw payload alone.

## Examples

| File | Lesson |
|---|---|
| `frost_demo.py` | Both rounds, individual checks, aggregation |
| `frost_simple_api_demo.py` | Small reproducible convenience API |
| `frost_nonce_reuse_demo.py` | Nonce deletion and second-use rejection |
| `frost_bad_share_demo.py` | Identify one failed partial equation and abort |
| `frost_context_binding_demo.py` | Exact signed envelope and changed-message failure |
| `frost_message_policy_demo.py` | Participant application-policy refusal |

Run older examples in order with `python .\examples\run_all.py`.

## Validation coverage

The 44 new tests cover:

- every 3-of-5 signer combination;
- 4-of-5 and 5-of-5 signing;
- unordered input canonicalization;
- interpolation, encoding, binding-factor, group-commitment, challenge, partial,
  and final equations;
- ordinary Schnorr verification;
- message/session/counter/context/DKG/signer-set binding;
- changed final and partial values;
- missing, duplicate, extra, unknown, and noncanonical inputs;
- signers absent from a package;
- message-policy rejection;
- nonce deletion, coordinator commitment tracking, and package closure;
- reproducible teaching output;
- absence of private nonces/shares from the public transcript; and
- complete signing while Shamir reconstruction functions are disabled.

See [VALIDATION.md](VALIDATION.md) for the complete record.

## Exact security boundary

Version 0.5 does not provide:

- an RFC named ciphersuite or RFC test-vector compatibility;
- meaningful discrete-log or collision security;
- a proven DKG or production FROST implementation;
- isolated signer processes or independent trust domains;
- authenticated/reliable networking or durable replay state;
- constant-time operations or secure erasure;
- robustness, share refresh, recovery, or proactive security;
- post-quantum security;
- threshold encryption, FHE, or private machine learning; or
- external audit or formal verification.

The complete boundary is documented in [SECURITY.md](SECURITY.md) and
[Chapter 28](docs/cryptocave/28-version-05-security-boundary.md).

## Recommended reading order for Version 0.5

1. [From DKG to threshold signatures](docs/cryptocave/22-from-dkg-to-threshold-signatures.md)
2. [Schnorr and threshold interpolation](docs/cryptocave/23-schnorr-and-threshold-interpolation.md)
3. [RFC 9591 FROST protocol](docs/cryptocave/24-rfc9591-frost-protocol.md)
4. [Version 0.5 code walkthrough](docs/cryptocave/25-version-05-code-walkthrough.md)
5. [Nonce, validation, and failure analysis](docs/cryptocave/26-nonces-validation-and-failure.md)
6. [RFC conformance map](docs/cryptocave/27-rfc9591-conformance-map.md)
7. [Version 0.5 security boundary](docs/cryptocave/28-version-05-security-boundary.md)

## Version progression

| Version | Main layer |
|---|---|
| 0.1 | Finite fields, polynomials, sharing, arithmetic, robust decoding, NTT |
| 0.2 | Feldman VSS and share verification |
| 0.3 | Pedersen VSS, session state, complaints, qualification, abort |
| 0.4 | Offline multi-dealer DKG and public-key derivation |
| 0.5 | Two-round educational threshold Schnorr/FROST signing |

## Next engineering boundary

A future Version 0.6 should keep this toy notebook intact and separately use a
maintained RFC 9591 implementation with official test vectors, serialized round
messages, isolated signers, authenticated local communication, and durable
nonce/session state. Threshold authentication can then be introduced as an
application layer. Threshold encryption and homomorphic private-ML experiments
should remain a separate key and protocol track.
