# FROST SageMath Proof-of-Concept Audit

This directory preserves and audits the collaborator-provided `poc.sage` used
for the CryptoCave article **FROST in SageMath: A Working Proof of Concept,
Line by Line**.

## Files

- `original-poc.sage` — exact uploaded working proof of concept.
- `audited-poc.sage` — hardened educational rewrite preserving the same core
  protocol flow while fixing scalar normalization, threshold/subset handling,
  abort behavior, transcript framing, nonce consumption, and final signature
  verification. It is **not RFC 9591 wire-compatible** because it intentionally
  uses a simpler teaching hash-to-scalar construction instead of the RFC's
  ciphersuite-specific `H1`–`H5` definitions.
- `reference_model.py` — dependency-free secp256k1 reference model used during
  this audit. It validates arbitrary 4-of-5 signer subsets, individual signature
  shares, final aggregation, and rejection of a 3-of-5 signing attempt.

## What the original gets right

The core signing equation is the FROST equation:

```
z_i = d_i + rho_i * e_i + lambda_i * s_i * c
```

with public verification relation:

```
z_i * G = D_i + rho_i * E_i + lambda_i * c * Y_i
```

and final aggregation `z = sum(z_i)`.

## Main audit findings

The uploaded proof of concept runs for honest parties, but it is best described
as a FROST-like educational implementation rather than an RFC 9591 conformant
implementation. The most important issues are:

1. `H1`, `H2`, PoK challenges, signing shares, and the final `z` are not
   explicitly reduced to the scalar field.
2. Binding factors do not use the RFC 9591 transcript
   `PK || H4(msg) || H5(commitment_list) || identifier`.
3. The code verifies each signature share but never verifies the final aggregate
   Schnorr signature before returning it.
4. DKG/VSS verification failures only print a message and do not abort or
   qualify/disqualify participants.
5. `FROST(t, n, a)` stores instance parameters, but multiple methods use module
   globals `t`, `n`, `a`, and `q`; therefore a differently configured instance
   can silently execute with the wrong parameters.
6. The example sets `t=4`, `n=5`, but `a=n`, so the demo always signs 5-of-5 and
   never demonstrates the intended 4-of-5 threshold property.
7. Security-relevant checks use `assert`, which is not an appropriate protocol
   validation mechanism.
8. Nonce generation uses the Sage/Python random helper rather than the RFC 9591
   nonce-generation construction that hedges randomness with the signing share.
9. Commitment-list serialization uses decimal identifiers without canonical
   scalar encoding or framing.
10. Session/concurrency state is stored directly on signer objects and is not
    isolated by a signing-session identifier.

## Run the dependency-free audit model

```bash
python reference_model.py
```

Expected output contains several `PASS` lines for different 4-of-5 subsets and
one explicit rejection of a 3-of-5 attempt.

## Run the SageMath files

With SageMath and its Python environment available:

```bash
sage original-poc.sage
sage audited-poc.sage
```

The original also imports PyCryptodome (`Crypto.Hash` / `Crypto.Util.number`),
so that dependency must be available in the Sage Python environment. The
`audited-poc.sage` version uses only Python's standard-library `hashlib` and
`secrets` in addition to SageMath itself.
