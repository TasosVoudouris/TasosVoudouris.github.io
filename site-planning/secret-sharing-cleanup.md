# Secret Sharing / MPC cleanup — v6.10

Source batch: `Secret Sharing(1).zip`

Archive SHA-256:

```text
4bbda46c0435e3fc44118c7b04f1efee965d5bcf0df1dd735aade8c60c30fadc
```

## Source accounting

The original ZIP contains **1,278 files**. Every file has a SHA-256-backed row in `secret-sharing-source-ledger.csv`; **0 files are unclassified**.

Disposition summary:

| Disposition | Files |
|---|---:|
| discarded generated virtual environment | 1,098 |
| integrated / reworked | 60 |
| superseded by stronger canonical material | 36 |
| discarded Python bytecode/cache | 34 |
| reference-only source | 30 |
| paper/PDF reference omitted | 9 |
| generated Sage-to-Python artifact omitted | 8 |
| nested source/archive ZIP omitted | 3 |

The raw ZIP, PDFs, nested repositories, bundled virtual environment, bytecode and caches are **not** included in the compact master.

## Canonical architecture decision

This batch is too broad to become one monolithic "Secret Sharing" article dump. It is divided by cryptographic role.

### Existing series strengthened: Secret Sharing & Polynomial Tools

The series is now ordered as:

1. Additive Secret Sharing
2. Shamir's Secret Sharing
3. Arithmetic on Shamir Shares: degree growth and reduction
4. Finite-Field Polynomial Interpolation
5. Beyond Basic Shamir: ramp sharing, proactive refresh, access structures, conversion
6. Packed Secret Sharing
7. Polynomial Splitting and Roots of Unity
8. NTT Engineering for Secret Sharing
9. FFT-Based Packed Secret Sharing
10. Robust Secret Sharing / Gao Decoding

The old notes repeatedly conflated the polynomial degree `T` with the reconstruction threshold. Canonical terminology now uses threshold `t` and degree `t-1`.

### New series: Secure Multiparty Computation

1. From Secret Sharing to MPC
2. Beaver Triples and Offline/Online Preprocessing
3. Authenticated Secret Sharing and the SPDZ MAC Invariant
4. SPDZ Protocol Anatomy
5. SPDZ Security and Engineering Boundaries
6. Vectorized MPC and Private Machine Learning

This prevents Beaver/SPDZ/tensor material from being presented as merely an "upgrade of Shamir".

### Existing canonical destinations retained

- Feldman/Pedersen VSS, complaints, DKG → `Threshold Cryptography Engineering`.
- KZG / IPA polynomial commitments → `Zero-Knowledge Proof Systems` / `Polynomial Commitments` topic.
- BLS/partial-signature material → existing threshold-signature/distributed-randomness articles.
- interpolation benchmarks → existing interpolation article and companion code.

A new standalone research note, `commitment-toy-code-audit.md`, records the useful code-audit lessons from the Pedersen/KZG/IPA experiments without treating them as canonical implementations.

## Main technical corrections

### Shamir multiplication

The source correctly computes pointwise products of Shamir shares but overclaims the result as reusable MPC multiplication. If `f` and `g` have degree `d`, then `fg` can have degree `2d`. A reusable MPC multiplication gate needs degree reduction/resharing or a preprocessing mechanism such as Beaver triples.

### Threshold off-by-one

Several scripts use `T` random nonconstant coefficients, creating a degree-`T` polynomial, while prose calls `T` the threshold. Such a polynomial requires `T+1` shares for interpolation. Canonical code uses `threshold - 1` random coefficients.

### Ramp/proactive sharing

The old upgrade note mixes correct ideas with loose parameter descriptions. Canonical text separates privacy threshold from reconstruction threshold and explains that proactive security requires a distributed refresh/security model; a central zero-sharing generator only demonstrates the algebra.

### "SPDZ" naming

The recovered two-party additive-sharing + Beaver-triple toy is **not SPDZ**. It models passive preprocessing MPC. SPDZ additionally requires authenticated secret shares under a hidden global MAC key, authenticated openings/MAC checks, and malicious-secure preprocessing validation.

### Private ML terminology

Secret-shared values are not ciphertexts. The recovered private-ML notes mix normal Keras layers with secure-computation sketches. They are retained as cost-model/architecture research notes, not as end-to-end secure CNN training code.

### Tensor triples

Element-wise `np.multiply(a, b)` triples implement Hadamard products. They do not automatically implement matrix multiplication, dot products, convolution, or arbitrary tensor layers. The correlation must match the bilinear operation used by the circuit.

### KZG / Pedersen audit

- The Sage "KZG" experiment defines its supposed pairing as field multiplication; this is **not a cryptographic bilinear pairing** and therefore is not KZG.
- A Pedersen vector helper reuses `random_points[vector_len - 1]` for blinding instead of the extra independent generator, creating a generator-indexing error.
- Naive hash-an-x-coordinate-and-increment point generation is not a standard hash-to-curve construction.
- The BLS12-381 pairing experiment is much closer to KZG algebra but remains an unaudited local-trapdoor prototype, as its own source warns.

## NTT audit

The recovered `Super NTT` package includes a q=12289 iterative and recursive implementation plus tests.

Core test run:

```text
15 passed
38 subtests passed
```

covering iterative NTT/INTT, recursive NTT/INTT, polynomial arithmetic, and utilities.

`test_vectors.py` fails during collection because importing the vector-generation script immediately writes to a relative `../test_vectors/` path that does not exist in the extracted environment. This is a packaging/import-side-effect defect, not evidence that the NTT arithmetic is wrong.

The canonical repository therefore uses a small independent dependency-free NTT companion and documents the recovered test result rather than copying the entire source package.

## New companion code

```text
experiments/secret-sharing/shamir-arithmetic/
experiments/secret-sharing/ntt-engineering/
experiments/mpc/beaver-triples/
experiments/mpc/spdz-mac-toy/
experiments/mpc/run_all.py
```

These companions intentionally expose protocol assumptions. The trusted resharing and triple/MAC dealer simulations are educational invariants, not production distributed protocols.

## Compact-master policy

The v6.10 canonical master contains no source-batch ZIP, PDF library, virtual environment, `.pyc`, `__pycache__`, generated Sage translations, `node_modules`, `dist`, or `.astro` cache.
