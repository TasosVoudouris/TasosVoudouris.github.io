# Lattices batch cleanup — v6.5

This document records how `Lattices.zip` was consolidated into the canonical CryptoCave repository on 2026-09-13.

## Source accounting

- Original archive entries: **165**.
- Migration-ledger rows: **165**.
- Unclassified entries: **0**.
- Uploaded archive SHA-256: `31b57b588208a187d03a1e889623537caf93993c0e38ad07171b7a23d44e0bd3`.
- Raw ZIP and paper/PDF files are **not bundled** in the canonical downloadable master. Provenance is retained through hashes, the source ledger, cleanup notes, and the user's original source archive.

Disposition totals:

- integrated/reworked: **9**;
- integrated assets: **35**;
- integrated code: **1**;
- integrated conceptually: **1**;
- superseded by clean companion implementations: **11**;
- superseded by stronger canonical work: **2**;
- superseded assets: **3**;
- reference-only: **13**;
- third-party reference-only: **32**;
- historical reference-only: **1**;
- out-of-scope reference material: **47**;
- excluded papers/PDFs: **5**;
- discarded large experimental data: **5**.

The file-by-file record is `site-planning/lattices-source-ledger.csv`.

## Canonical architecture decision

The batch is substantial enough to justify its own ordered path. The previous mixed `Linear Algebra & Lattices` path has therefore been split into:

1. **Linear Algebra Foundations** — vectors, matrices, linear maps, Gram–Schmidt, determinants, orthogonality, and volume;
2. **Lattices & Lattice-Based Cryptography** — discrete lattice geometry through modern lattice-based post-quantum cryptography and cryptanalysis.

The canonical lattice sequence is:

1. Integer Lattices, Bases, Determinants, and Duals
2. Hard Lattice Problems: SVP, CVP, BDD, SIVP, and Geometric Bounds
3. Lattice Reduction: LLL, Babai, and the Road to BKZ
4. q-ary Lattices, SIS, and Short Modular Relations
5. Learning With Errors: Search/Decision LWE, Encryption, and Attack Surfaces
6. Ring-LWE and Module-LWE: Structured Lattices for Efficient Cryptography
7. NTRU: Polynomial Arithmetic, Lattice Geometry, and Decryption
8. Modern Lattice-Based PQC: ML-KEM, ML-DSA, and the Module-Lattice Design Pattern
9. Lattice Cryptanalysis: Hidden Numbers, Coppersmith, Partial Leakage, and LWE Attacks

A separate standalone research note retains the useful structured NTRU Gram–Schmidt material without presenting it as a general theorem or production attack implementation.

## Homomorphic-encryption placement

The BFV material belongs to the **Homomorphic Encryption** path, not to the main lattice sequence. It is now Part XI of that series and links back to the Ring-LWE prerequisites. This avoids repeating the same ring/module-LWE theory in two places.

## Technical corrections

The canonical articles correct several recurring simplifications or errors in the source material:

- BDD is stated as a promise problem with an explicit decoding radius; uniqueness is guaranteed below half the first minimum.
- Minkowski bounds are stated with the appropriate determinant and Euclidean-ball volume factors rather than an incorrect simplified expression.
- The standard q-ary primal and dual-style lattices are described using the correct **scaled-dual** relationship rather than being called identical ordinary duals.
- SIS hardness is described through parameterized worst-case/average-case reductions rather than as simply “the same problem as SVP.”
- LWE is not described as literally equivalent to SVP/CVP; the canonical text distinguishes search/decision forms, average-case instances, and the relevant worst-case lattice reductions and parameter regimes.
- Ring-LWE is motivated by cyclotomic/negacyclic structure; `x^n + 1` is not claimed to be irreducible modulo every selected modulus.
- Efficient modular polynomial multiplication is described using NTT-style transforms rather than a floating-point FFT abstraction.
- NTRU's common scaling conventions are distinguished explicitly instead of mixing `h = p g f^{-1}` with `h = g f^{-1}` formulations.
- Small brute-force demonstrations are labeled as toy illustrations, not security estimates.
- BFV intuition is separated from exact scheme variants: ciphertext multiplication grows the ciphertext dimension and practical BFV requires the scheme-specific scale/noise-management and relinearization machinery.

## Code policy

Only compact educational companions that improve the canonical articles are retained:

- `experiments/lattices/sis/`
- `experiments/lattices/lwe/`
- `experiments/lattices/ring-lwe/`
- `experiments/lattices/ntru/`
- `experiments/lattices/ntru-gsd/`
- `experiments/homomorphic/bfv/`

Third-party attack repositories, course snapshots, large precomputed matrices, model/checkpoint data, PDFs, and nested archives are not copied into the active repository. Existing stronger CryptoCave articles remain canonical for Coppersmith, RSA partial exposure, ECDSA nonce leakage, and related attacks.
