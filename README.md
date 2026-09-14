# CryptoCave

CryptoCave is the canonical repository for my cryptography and mathematical-foundations notes, ordered learning paths, cryptanalysis deep dives, reviewed teaching implementations, experiments, and research notes.

Production site: `https://tasosvoudouris.github.io`

GitHub repository: `https://github.com/TasosVoudouris/TasosVoudouris.github.io`

## One canonical master

Use this repository as the single working CryptoCave tree. The current v6.11 master contains **208 published articles**, **24 ordered series**, and **30 topic areas**.

The consolidation process does not copy every source file into the active site. Incoming batches are deduplicated and classified; only the strongest canonical prose, useful figures, selected companion implementations, and provenance records survive in the working repository.

The human-facing site map is:

```text
/library/
```

The current architecture is documented in:

```text
site-planning/content-map.md
site-planning/validation.md
```

## Repository layers

```text
src/content/blog/    Canonical publishable articles
experiments/         Companion code, notebooks, tests, reviewed examples
research-notes/      Provenance, audits, selected non-public notes
references/          Small catalogs/reference metadata when useful
site-planning/       Current architecture, validation, cleanup notes, migration ledgers
```

From v6.5 onward the downloadable master is deliberately **compact**. Bulky paper/PDF libraries, raw incoming ZIPs, model checkpoints, generated artifacts, and copied third-party repositories are not rebundled by default. Per-batch cleanup notes and SHA-256 migration ledgers preserve the decisions without making the working master hundreds of megabytes.

## Ordered series

The site currently exposes these reading paths:

1. **Cryptography Primer**
2. **Cryptography From Zero**
3. **Classical Cryptanalysis**
4. **Elementary Number Theory Reference**
5. **Abstract Algebra Foundations**
6. **Finite Fields & Polynomial Arithmetic**
7. **Computational Number Theory**
8. **Linear Algebra Foundations**
9. **Lattices & Lattice-Based Cryptography**
10. **Symmetric Cryptography**
11. **Hash Functions & MACs**
12. **Randomness & Stream Ciphers**
13. **Discrete Logarithm Algorithms**
14. **Diffie–Hellman & ElGamal**
15. **Elliptic Curve Mathematics**
16. **Elliptic Curve Cryptanalysis**
17. **Digital Signatures**
18. **Secret Sharing & Polynomial Tools**
19. **Secure Multiparty Computation**
20. **Threshold Cryptography Engineering**
21. **Oblivious Transfer**
22. **Homomorphic Encryption**
23. **Zero-Knowledge Proof Systems**
24. **RSA Deep Dives**

**Series** define reading order; **Topics** provide cross-cutting scientific classification; **Tags** are the fine-grained technical index.

### Lattice architecture

The former mixed `Linear Algebra & Lattices` track has been deliberately split:

```text
Linear Algebra Foundations
        ↓
Lattices & Lattice-Based Cryptography
        ↓
geometry / SVP-CVP-BDD
        ↓
LLL / Babai / BKZ
        ↓
2D Gaussian reduction / integer-NTRU bridge
        ↓
q-ary lattices / SIS
        ↓
LWE
        ↓
Ring-LWE / Module-LWE
        ↓
NTRU
        ↓
toy NTRU lattice + LLL recovery
        ↓
ML-KEM / ML-DSA
        ↓
lattice cryptanalysis
```

BFV remains in **Homomorphic Encryption**, where it belongs, and links back to Ring-LWE rather than duplicating the prerequisite theory.




### Historical SageMath audit layer

The recovered Ross-course and miscellaneous SageMath material is no longer carried as raw notebooks. Its useful content is represented by four audited canonical pieces:

```text
2D Gaussian reduction / integer-NTRU analogy
        ↓
polynomial NTRU public lattice / LLL recovery

classical SageMath lab audit
        ↓
RSA/CRT/DH/ElGamal/ECDH public-key lab audit
```

The canonical articles explicitly separate correct algebra from old notebook bugs, Sage/Python syntax traps, obsolete parameter generation, and security-model overclaims. The file-by-file provenance record is `site-planning/pqc-sagemath-source-ledger.csv`.

### Secret-sharing and MPC architecture

The Secret Sharing cleanup now separates representation from computation:

```text
Additive sharing
    ↓
Shamir sharing
    ↓
share arithmetic / degree growth
    ↓
interpolation + ramp/proactive variants
    ↓
packed sharing / roots of unity / NTT
    ↓
robust reconstruction
    ↓
Secure Multiparty Computation
    ↓
Beaver triples
    ↓
authenticated sharing / SPDZ MAC invariant
    ↓
SPDZ online arithmetic and checks
    ↓
malicious-security engineering
    ↓
vectorized/private-ML research notes
```

This is deliberate: **secret sharing is a representation; MPC is an interactive protocol for computing on that representation**. VSS/DKG stay in Threshold Cryptography Engineering, and KZG/IPA stay with Zero-Knowledge / Polynomial Commitments.

The recovered q=12289 NTT package was audited rather than copied wholesale: its core iterative/recursive/polynomial/utility tests pass **15 tests + 38 subtests**; an additional vector test has an import-time fixture-generation path bug. The canonical repository keeps an independent small NTT companion plus the audit record.

### Threshold-signature architecture

The Threshold Cryptography Engineering path now deliberately places the real Schnorr/JavaScript debugging case between generic Schnorr algebra and the later threshold-ECDSA/FROST material. It also includes a line-by-line audit of a collaborator's working SageMath FROST proof of concept immediately after the RFC 9591 protocol chapter:

```text
VSS / DKG
    ↓
threshold signing concepts
    ↓
Schnorr linear interpolation
    ↓
our distributed BIP340/Schnorr debugging case
    ↓
Why threshold ECDSA is hard
    ↓
TinySig masked-factor / preprocessing deep dive
    ↓
FROST / RFC 9591
    ↓
security boundaries / randomness / ChillDKG
```

The new distributed-Schnorr case study preserves our original TypeScript snapshot, three architecture sketches, a corrected current-Noble implementation, and a dependency-free secp256k1 reference model that reproduces the old ~50% aggregate-nonce parity failure.

The TinySig chapter separately records the historical debugging case: the recovered local snapshot mixed an incomplete package checkout, legacy source, bytecode, and a separate WebSocket/FastAPI network experiment. CryptoCave retains only a clean explanatory layer plus small diagnostic/algebra companions.

### Zero-knowledge architecture

The ZK material is organized as one dependency-aware path rather than separate protocol dumps:

```text
Zero-Knowledge Foundations
        ↓
Sigma protocols / identification
        ↓
Fiat–Shamir transcripts
        ↓
Commitments / Merkle / IOPs
        ↓
R1CS
        ↓
QAP / Pinocchio
        ↓
Polynomial commitments (KZG / IPA)
        ↓
Groth16 / PLONK
        ↓
STARK / AIR → FRI
        ↓
Recursion / Halo
        ↓
proof-system design map
```

A separate **Polynomial Commitments** topic connects KZG/IPA/FRI material across the site without duplicating it into another ordered series.

## Review status

Some articles carry an explicit frontmatter status:

- `Validated` — companion implementation/tests were executed during consolidation.
- `Reviewed` — editorial/technical review exists, but an external runtime such as SageMath may not have been available locally.
- `Research Note` — valuable detailed material retained for study but not presented as a fully revalidated implementation.
- `Experimental` — educational/exploratory implementation; not production cryptography.
- no explicit status — ordinary CryptoCave article; not a separate conformance or implementation claim.

## Clean extraction rule

Do **not** extract a new CryptoCave archive over an older working directory. ZIP extraction overwrites matching files but does not remove obsolete Markdown, so stale content can survive and fail the current schema.

For each upgrade, extract into a new/empty folder (or rename the old one first). The repository runs a content preflight before `npm run dev` and `npm run build`:

```bash
npm run check:content
```

A clean v6.11 master reports:

```text
CryptoCave content preflight: OK (208 articles, 24 series, 30 topics).
```

## Local development

Node.js 24 is recommended and matches the GitHub Pages workflow. Node.js 22.19+ is accepted.

```bash
npm ci
npm run dev
```

Astro normally starts at `http://localhost:4321`.

Before pushing:

```bash
npm run build
npm run preview
```

Git branch: `main`

Configured origin:

```text
https://github.com/TasosVoudouris/TasosVoudouris.github.io.git
```

GitHub Pages deployment is handled by `.github/workflows/deploy.yml`.

## Scientific companion material

Major companion areas include:

```text
experiments/mathematics/
experiments/lattices/
experiments/zero-knowledge/
experiments/rsa/
experiments/hash-functions/
experiments/randomness-stream-ciphers/
experiments/oblivious-transfer/
experiments/cryptanalysis/
experiments/threshold-cryptography/
experiments/secret-sharing/
experiments/mpc/
experiments/homomorphic/
experiments/digital-signatures/
experiments/classical-cryptanalysis/
experiments/elgamal-voting/
experiments/cryptosage/
experiments/ready-material/
```

Articles may use `sourcePath` in frontmatter; the site turns it into a direct link to the corresponding GitHub folder.

## Consolidated source batches

Each cleanup batch has a human-readable report plus an exact SHA-256-backed file ledger:

```text
site-planning/part1-cleanup.md
site-planning/part1-source-ledger.csv

site-planning/part2-cleanup.md
site-planning/part2-source-ledger.csv

site-planning/mathematics-cleanup.md
site-planning/mathematics-source-ledger.csv

site-planning/lattices-cleanup.md
site-planning/lattices-source-ledger.csv

site-planning/zkps-cleanup.md
site-planning/zkps-source-ledger.csv

site-planning/threshold-python-cleanup.md
site-planning/threshold-python-source-ledger.csv

site-planning/secret-sharing-cleanup.md
site-planning/secret-sharing-source-ledger.csv
```

The Threshold Python batch contains **241 source files**, all fully classified with zero unclassified entries. Its canonical result is two new threshold-ECDSA/TinySig chapters plus a small diagnostic/algebra companion layer; raw third-party repositories, PDFs, bytecode, and embedded Git history are excluded.

The Secret Sharing/MPC batch contains **1,278 source files**, all classified with zero unclassified entries. Most of its apparent size was a bundled Python virtual environment (1,098 files). Canonical output is a strengthened 10-part secret-sharing track, a new 6-part Secure Multiparty Computation series, selected tested companion code, and one polynomial-commitment code-audit research note.

Raw batch archives and paper libraries are intentionally **not** included in the compact master. Keep original source ZIPs externally only if you want an independent archival copy.

## Content schema

The schema lives in `src/content.config.ts`. Typical article frontmatter is:

```yaml
title: Example Article
description: A precise one-sentence description.
pubDate: "2026-09-13"
topics:
  - Cryptanalysis
tags:
  - example
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 1
sourcePath: experiments/rsa/example
status: Validated
draft: false
```

Drafts are excluded from public routes, indexes, series/topic/tag pages, and RSS.
