# FROST SageMath proof-of-concept audit

This note records the editorial and technical decision for the collaborator-provided `poc.sage` integrated in v6.9.

## Canonical placement

The source becomes **Part 22** of `Threshold Cryptography Engineering`, immediately after the RFC 9591 protocol chapter and immediately before the larger validated FROST implementation walkthrough.

This ordering is intentional:

```text
Schnorr algebra
→ broken distributed Schnorr debugging
→ threshold-ECDSA/TinySig contrast
→ RFC 9591 FROST protocol
→ collaborator SageMath PoC audit
→ validated implementation walkthrough
→ nonce/replay/conformance/security-boundary articles
```

## Source preservation

The exact uploaded file is preserved as:

```text
experiments/threshold-cryptography/frost-sage-poc/original-poc.sage
```

The audit adds:

```text
experiments/threshold-cryptography/frost-sage-poc/audited-poc.sage
experiments/threshold-cryptography/frost-sage-poc/reference_model.py
experiments/threshold-cryptography/frost-sage-poc/README.md
```

## Audit verdict

The honest-path signing algebra is sound and explains why the program runs consistently. In particular, the implementation correctly captures:

- multi-dealer Shamir/Feldman-style key material;
- public verification shares;
- two FROST nonce commitments per signer;
- binding factors and aggregate commitment;
- interpolation coefficients at zero;
- `z_i = d_i + rho_i e_i + lambda_i s_i c`;
- public signature-share verification; and
- scalar-share aggregation.

The source is **not** classified as RFC 9591 conformant. Main deviations/issues:

1. hashes are not explicitly mapped/reduced to canonical scalar-field elements;
2. binding-factor transcript differs from RFC 9591 H1/H4/H5 construction;
3. final aggregate signature is not verified before return;
4. invalid DKG proofs/shares print errors but do not abort or qualify participants;
5. class constructor parameters coexist with hidden module globals;
6. `t=4,n=5` demo signs with all five parties and therefore does not demonstrate arbitrary 4-of-5 subsets;
7. security validation relies on `assert` in multiple places;
8. empty messages are accidentally rejected by truthiness testing;
9. commitment-list participant identifiers use variable-length decimal encodings;
10. nonce generation is an educational random-scalar sampler rather than the RFC 9591 nonce-generation construction;
11. session/concurrency state is stored directly on signer objects; and
12. the multi-dealer DKG front-end is extra protocol logic outside the RFC 9591 signing core.

## Independent validation

The dependency-free `reference_model.py` was executed successfully on secp256k1. It verified four distinct 4-of-5 signer subsets, a 5-of-5 signing session, every individual signature share, every final aggregate signature, and explicit rejection of a 3-of-5 signing attempt.

The original Sage file itself was not executed in this environment because SageMath is not installed here. The user reports that the original runs normally; the audit therefore distinguishes **observed historical execution** from **independently executed reference-model validation**.

The existing validated FROST v0.5 regression suite was rerun after integration:

```text
141 passed, 29 subtests passed
```
