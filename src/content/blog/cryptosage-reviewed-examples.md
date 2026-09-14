---
title: "CryptoSage: Reviewed SageMath Cryptography Examples"
description: "A curated map of the reviewed SageMath examples for integer-factorization systems, elliptic-curve encryption and signatures, key agreement, pairings, and supporting conversion/KDF helpers."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Cryptographic Engineering"
  - "Public-Key Cryptography"
  - "Elliptic-Curve Cryptography"
tags:
  - "sagemath"
  - "cryptosage"
  - "ecdsa"
  - "ecmqv"
  - "pairings"
  - "rsa"
  - "paillier"
difficulty: "Intermediate"
sourcePath: "experiments/cryptosage"
status: "Reviewed"
draft: false
---
This package reorganizes the supplied `cryptosage-master` archive into a
topic-based educational collection. It contains commented SageMath examples,
small executable demonstrations, and Markdown pages prepared for later use in
the CryptoCave documentation site.

> [!CAUTION]
> These programs are for study, experimentation, and algorithm tracing. They
> are not production cryptographic software. Several examples intentionally use
> the legacy `secp192r1` curve or SHA-1 to remain close to the supplied material.

## Project structure

| Path | Purpose |
| --- | --- |
| `docs/` | GitHub- and Docusaurus-compatible explanatory pages |
| `src/foundations/` | Hashing, encoding, KDF, padding, and point helpers |
| `src/integer_factorization/` | RSA key generation and Paillier encryption |
| `src/elliptic_curves/` | EC parameters, keys, signatures, and encryption |
| `src/key_agreement/` | ECMQV and an STS-inspired key-confirmation study |
| `src/pairings/` | Small Miller-function/pairing demonstration |
| `examples/` | Entry points that load dependencies in the right order |
| `tests/` | SageMath assertions for the executable demonstrations |
| `archive/incomplete/` | Preserved incomplete material that must not be run |

The complete old-to-new mapping is recorded in
[`ORIGINAL_FILE_MAP.md`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptosage/ORIGINAL_FILE_MAP.md). Review decisions and precise
corrections are recorded in [`REVIEW_NOTES.md`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptosage/REVIEW_NOTES.md).

## Requirements

- SageMath 10.x or a recent SageMath release using Python 3.
- PyCryptodome for the ECIES and PSEC demonstrations.

Install the optional Python dependency inside SageMath:

```bash
sage -pip install pycryptodome
```

## Run the examples

Run commands from the project root because SageMath resolves `load(...)` paths
from the current working directory:

```bash
sage examples/rsa_keygen_demo.sage
sage examples/paillier_demo.sage
sage examples/ecdsa_demo.sage
sage examples/eckcdsa_demo.sage
sage examples/ecies_demo.sage
sage examples/psec_demo.sage
sage examples/ecmqv_demo.sage
sage examples/sts_key_confirmation_demo.sage
sage examples/pairing_demo.sage
```

Run the assertion-based checks with:

```bash
sage tests/run_all.sage
```

## Documentation

Start with [`docs/index.md`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptosage/docs/index.md). The pages explain the mathematical
purpose of each program, identify its inputs and outputs, reproduce selected
code fragments, and distinguish executable demonstrations from legacy material.

For CryptoCave, a practical integration layout is:

```text
CryptoCave/
├── docs/public-key-cryptography/sagemath/   # copy this package's docs
└── code/sagemath/cryptosage/                # copy src, examples, and tests
```

Adjust links after integration if the code is hosted outside the documentation
tree.

## Provenance and publication

The supplied archive did not contain a license file. See [`NOTICE.md`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptosage/NOTICE.md)
before publishing or relicensing this material. The reorganization and review
do not establish ownership of the original source.


## Security status

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
