---
sidebar_position: 9
---

# Security and implementation status

## Status labels

| Label | Meaning |
| --- | --- |
| Executable demonstration | Intended to run under current SageMath and covered by assertions |
| Educational study | Mathematically illustrative but not standards-complete |
| Legacy | Uses an old curve, hash, construction, or parameter set |
| Archived incomplete | Preserved for analysis and intentionally not executable |

## Important limitations

- The programs are not constant-time and make no side-channel claim.
- Random sampling uses SageMath demonstration primitives, not a documented
  production DRBG interface.
- `secp192r1` and SHA-1 are retained only for compatibility with the supplied
  examples.
- ECIES and PSEC are educational compositions rather than certified protocol
  implementations.
- ECMQV needs standards-specific validation, identities, certificates, and
  transcript rules before operational use.
- The STS-inspired file provides key confirmation but no peer authentication.
- The pairing example uses deliberately tiny, insecure parameters.
- The RFC 5091 draft is non-runnable and receives no conformance claim.

## Before adding this material to CryptoCave

Run `sage tests/run_all.sage` in a current SageMath environment, confirm the
upstream license, keep the warnings visible, and link each documentation page to
the exact reviewed source revision. Any future production-oriented example
should be added beside these studies rather than silently changing their
historical assumptions.
