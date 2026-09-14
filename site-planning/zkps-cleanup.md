# ZKPs cleanup — CryptoCave v6.6

This report records the consolidation of `ZKPs.zip` into the compact v6.5 canonical master on 2026-09-14.

## Source accounting

- Original archive files: **51**.
- Ledger rows: **51**.
- Unclassified files: **0**.
- Source ZIP SHA-256: `77a221d76b73d5894f53f6108d3401d696e5d18ab2970380bc62de7787bfe266`.
- Raw ZIP: intentionally **not bundled** in the compact master.
- PDFs/papers: intentionally **not bundled**.

Disposition totals:

- integrated/reworked: **2**;
- integrated conceptually: **7**;
- reference-only conceptual source: **1**;
- reference-only with selected conceptual integration: **1**;
- superseded by cleaned canonical work: **12**;
- superseded duplicate archive: **1**;
- superseded source figures: **3**;
- excluded papers/PDFs: **8**;
- discarded generated Python cache: **14**;
- discarded repository metadata: **1**;
- out-of-scope reference-only: **1**.

The exact per-file record is `site-planning/zkps-source-ledger.csv`.

## Canonical result

The batch becomes one ordered **Zero-Knowledge Proof Systems** series with 13 parts:

1. Zero-Knowledge Foundations: Relations, Witnesses, Soundness, and Simulation
2. Sigma Protocols: Schnorr, Feige–Fiat–Shamir Identification, HVZK, and Special Soundness
3. The Fiat–Shamir Transform: From Public-Coin Interaction to Non-Interactive Arguments
4. Commitments, Merkle Trees, and Oracle Proofs
5. Arithmetization I: Arithmetic Circuits, Witnesses, and R1CS
6. Arithmetization II: From R1CS to QAPs and the Pinocchio Blueprint
7. Polynomial Commitments: KZG, IPA-Based Schemes, Openings, and Batching
8. Groth16: Pairing-Based Preprocessing zk-SNARKs from QAPs
9. PLONK: Gate Polynomials, Permutation Arguments, and Universal Structured Reference Strings
10. STARKs: Execution Traces, AIR, Composition Polynomials, and Transparency
11. FRI: Reed–Solomon Proximity, Folding, and Low-Degree Testing
12. Recursive Proofs: Composition, Accumulation, IPA Commitments, and Halo
13. SNARKs, STARKs, and the Zero-Knowledge Proof-System Design Space

A new cross-cutting **Polynomial Commitments** topic was added for KZG/IPA/FRI-related material.

## Canonical companion code

Rather than copying third-party repositories, v6.6 keeps a small dependency-free reviewed layer at:

```text
experiments/zero-knowledge/
├── sigma/
├── fiat-shamir/
├── r1cs/
├── qap/
├── merkle/
├── fri/
└── run_all.py
```

The experiments demonstrate only the precise concept claimed:

- Schnorr Sigma completeness and special-soundness extraction;
- domain-separated Fiat–Shamir transcript binding;
- finite-field R1CS satisfaction;
- R1CS-to-QAP interpolation and target-polynomial divisibility;
- Merkle commitment/opening verification;
- one algebraically correct FRI fold.

They are not presented as production SNARK/STARK implementations.

## Major editorial / cryptographic corrections

### Fiat–Shamir terminology

The source material blurred **Fiat–Shamir identification** (a concrete square-root identification family) with the **Fiat–Shamir transform** (a general public-coin-to-non-interactive compilation technique). The canonical series separates them.

### Multi-bit challenge soundness

The original multi-secret identification note stated a `2^-t` soundness error while using a `k`-bit challenge vector. The canonical article removes that unsupported simplification: soundness/knowledge error depends on the actual challenge space and protocol theorem.

### Multi-secret extraction

Two accepting transcripts with different multi-coordinate challenges do not automatically reveal every individual secret. The canonical text distinguishes one-dimensional Schnorr special soundness from vector-challenge extraction requirements.

### R1CS/QAP layering

R1CS and QAP are arithmetizations, not zero-knowledge proof systems by themselves. Soundness, succinctness, commitments, setup, and zero-knowledge randomization are identified as separate layers.

### Commitments do not automatically hide

A Merkle root provides hash-based binding/random-access authentication, not generic hiding. KZG/other polynomial commitments likewise require an explicit hiding/blinding mechanism when witness privacy is needed.

### FRI classification

FRI is treated correctly as a Reed–Solomon **interactive oracle proof of proximity** / low-degree testing engine. A FRI-based polynomial commitment additionally needs committed evaluation oracles, authentication and transcript machinery.

### STARK versus zk-STARK

`STARK` means scalable transparent argument of knowledge. Zero knowledge is an additional masking/randomization property. The old educational STARK sources are therefore not labeled complete zk-STARK implementations.

### PLONK privacy

One supplied PLONK educational repository explicitly omits the privacy-preserving components. The canonical PLONK article uses it only as a conceptual source and explains that selector/permutation correctness is not itself zero knowledge.

### Setup terminology

The canonical material distinguishes:

- circuit-specific structured setup (e.g. Groth16 preprocessing);
- universal/updatable structured SRS within a configured degree/capacity (classic KZG-backed PLONK);
- transparent setup (hash/oracle proof systems).

"Universal" is not described as unbounded.

### Recursion terminology

Recursive proof composition, aggregation, batch verification, accumulation, and folding are explicitly separated rather than treated as synonyms.

## Third-party and frontier material

The source batch contains repository snapshots such as `babySNARK`, `Pinocchio_SNARK_Py`, `plonkathon`, `zkSNARK-under-the-hood`, a large mixed `research-master`, and older STARK experiments. These are not copied into the canonical repository.

Useful concepts were synthesized into the reviewed articles. Experimental frontier code such as Circle-STARK/Binius material found inside the large research archive is deferred rather than promoted into the foundational curriculum without a dedicated review batch.

## Compact-source rule

v6.6 contains no source PDFs, no raw nested ZIPs, no copied third-party repository snapshots, and no `__pycache__`/`.pyc` artifacts from this batch. Provenance survives through this report and the SHA-256 ledger.
