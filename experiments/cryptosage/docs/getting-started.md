---
sidebar_position: 2
---

# Getting started

SageMath extends Python with finite fields, modular rings, elliptic curves,
factorization, and exact arithmetic. A `.sage` file is first processed by the
Sage preparser and then executed by Python, so it should be launched with
`sage`, not directly with `python`.

## Installation and dependency

Install a current SageMath release from the
[official SageMath site](https://www.sagemath.org/). ECIES and PSEC also use
PyCryptodome:

```bash
sage -pip install pycryptodome
```

## Running a demonstration

Open a terminal in the package root and run:

```bash
sage examples/ecdsa_demo.sage
```

The root directory matters because the examples use explicit paths such as:

```python
load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/elliptic_curves/ecdsa.sage")
```

Run all assertion-based checks with:

```bash
sage tests/run_all.sage
```

## Scope

The goal is reproducible understanding, not a stable cryptographic API. Keys,
nonces, and ciphertexts are created inside demonstrations; serialization is
minimal; no side-channel protections are claimed; and legacy algorithms remain
only where they are part of the supplied educational material.
