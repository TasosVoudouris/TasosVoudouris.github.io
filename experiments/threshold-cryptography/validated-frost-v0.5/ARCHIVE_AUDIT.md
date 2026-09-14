# Uploaded VSS archive audit

The uploaded `VSS example.zip` was inspected before Versions 0.2–0.5 were built.

## What was reusable

`Feldman.py` and `vss.py` contain the right core idea:

```text
commit to every polynomial coefficient
        ↓
give participant i the private value f(i)
        ↓
check share * G against the committed polynomial at i
```

This equation became the basis of `cryptocave_sss/feldman.py`.

## What required correction

| Area | Finding | Validated project action |
|---|---|---|
| Dealer state | `main.py` and `server.py` create fresh polynomials for different participants/requests | One `FeldmanDistribution` owns one polynomial, all shares, and one commitment vector |
| Reconstruction | Symbolic `evalf()` or ordinary `/` introduces floating arithmetic | Exact modular Lagrange interpolation from Version 0.1 |
| Randomness | `random.randint()` is used for cryptographic coefficients | Operating-system randomness by default; seeds only in tests/examples |
| Keys | Independent participant signing keys are generated but unused | Removed from Feldman algebra; authentication deferred to the protocol layer |
| Pedersen | One file is empty and another branch is unvalidated | Reimplemented independently in Version 0.3 with explicit parameters, blinding polynomial, verification reports, and tests |
| BLS | Partial signatures are added without Lagrange weights | Classified as invalid and excluded from active code |
| KZG | Coefficients are committed separately and a commitment is reused as its proof | Classified as invalid and deferred |
| MQTT | Private shares are published inside public parameters | Network experiment excluded |
| TLS | Client verification is disabled; included certificate is expired | Network experiment and credentials excluded |

## Sensitive and third-party material

The archive contains a private key. It is not included in the deliverable and
must be treated as compromised. The associated local certificate expired in
2025 and is also excluded. Do not publish or reuse either file.

The archive also contains a nested third-party source tree without a clear
license file in the supplied copy, plus screenshots and a PDF. These are not
redistributed in Version 0.5.

Selected offline source scripts are preserved under `legacy/` only for
comparison. They are not imported, executed, or presented as validated code.
