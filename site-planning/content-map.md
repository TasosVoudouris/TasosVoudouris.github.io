# CryptoCave canonical content map — v6.12

This is the current architecture after the v6 consolidation and the dedicated Secret Sharing / MPC cleanup and the Ross-PQC / historical SageMath audit. Historical planning maps remain under `site-planning/history/` for provenance only.

## Navigation model

- **Library** — canonical site-wide map.
- **Series** — ordered reading paths.
- **Topics** — cross-cutting scientific areas.
- **Tags** — fine-grained algorithms, attacks, standards, and implementation concepts.
- **Articles** — flat chronological/browse view.

## Ordered series

| Series | Articles | Purpose |
|---|---:|---|
| Cryptography Primer | 4 | Orientation, bit/encoding tools, Python/SageMath, randomness |
| Cryptography From Zero | 13 | Beginner-first executable path through arithmetic, DH, CRT, primality, and RSA |
| Classical Cryptanalysis | 4 | Frequency analysis, audited classical-cipher/Sage exercises, Kasiski/Vigenère, OTP and keystream reuse |
| Elementary Number Theory Reference | 9 | Divisibility, modular arithmetic, CRT, modular groups, primes, and primality |
| Abstract Algebra Foundations | 7 | Groups, quotients, rings, fields, polynomial rings, modules, affine varieties |
| Finite Fields & Polynomial Arithmetic | 4 | Finite-field construction, Frobenius/trace/norm, irreducibility, root/factor algorithms |
| Computational Number Theory | 7 | Arithmetic functions, primes, Gaussian integers, characters/sums, forms and factorization |
| Linear Algebra Foundations | 2 | Vectors, matrices, linear maps, orthogonality, Gram–Schmidt, determinants, volume |
| Lattices & Lattice-Based Cryptography | 11 | Geometry, hard lattice problems, reduction, 2D NTRU analogy, SIS/LWE, NTRU, toy LLL recovery, PQC, cryptanalysis |
| Symmetric Cryptography | 6 | SPNs, DES, AES, modes, AEAD, linear cryptanalysis |
| Hash Functions & MACs | 8 | Hash security, SHA-2/SHA-3, MACs, algebraic hashes |
| Randomness & Stream Ciphers | 7 | PRGs, LCG/LFSR, RC4, ChaCha20, Dual_EC_DRBG |
| Discrete Logarithm Algorithms | 5 | DLP/ECDLP, BSGS, Pohlig–Hellman, Pollard rho, index calculus |
| Diffie–Hellman & ElGamal | 4 | DH, subgroup structure, attacks/validation, ElGamal |
| Elliptic Curve Mathematics | 13 | Cubics, group law, rational points, torsion, pairings, Schoof, isogenies |
| Elliptic Curve Cryptanalysis | 3 | Singular curves, MOV, Smart |
| Digital Signatures | 7 | Security models, RSA/PSS, DSA, ECDSA, Schnorr, EdDSA |
| Secret Sharing & Polynomial Tools | 10 | Additive/Shamir sharing, arithmetic, ramp/proactive variants, interpolation, packing, NTT, robust reconstruction |
| Secure Multiparty Computation | 6 | Beaver triples, authenticated shares, SPDZ, malicious-security boundaries, vector/private-ML engineering |
| Threshold Cryptography Engineering | 28 | VSS, DKG, Schnorr/BIP340, threshold ECDSA/TinySig, FROST, randomness, ChillDKG |
| Oblivious Transfer | 3 | Rabin OT, 1-out-of-2 OT, modern OT extension |
| Homomorphic Encryption | 11 | Classical PHE, Paillier family, SHE/FHE, DGHV, BGV, BFV |
| Zero-Knowledge Proof Systems | 13 | ZK foundations, Sigma/Fiat–Shamir, arithmetization, PCS, SNARKs, STARKs, FRI, recursion |
| RSA Deep Dives | 14 | Structured RSA cryptanalysis through ROCA and factorization-friendly primes |

There are **199 ordered-series articles** across **24 series**.

## Secret-sharing and MPC dependency rule

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
authenticated secret sharing
    ↓
SPDZ online arithmetic / MAC checks
    ↓
malicious-security engineering
    ↓
vectorized/private-ML case studies
```

The boundary is deliberate: secret sharing is a representation; MPC is an interactive protocol for computing on that representation. VSS/DKG remain in **Threshold Cryptography Engineering**, while KZG/IPA remain in **Zero-Knowledge Proof Systems / Polynomial Commitments**.


## Ross-course / SageMath audit rule

The 2022 Ross-course archive is integrated into the existing lattice path rather than becoming a duplicate post-quantum series. Its unique progression is preserved as:

```text
LLL foundations
    ↓
exact 2D Gaussian reduction
    ↓
one-dimensional NTRU analogy
    ↓
q-ary lattices / SIS / LWE
    ↓
Ring/Module-LWE
    ↓
NTRU
    ↓
explicit NTRU public lattice + LLL recovery
    ↓
modern standardized lattice PQC
```

Historical SageMath coursework is published only after code-audit cleanup. Classical material lives inside **Classical Cryptanalysis**; the cross-cutting public-key workbook remains a standalone engineering/reference article rather than duplicating RSA, DH, ElGamal, ECDH, and signature theory across their primary series.

## Standalone references / research notes

- **Attribute-Based Encryption: KP-ABE, CP-ABE, Access Policies, and Pairing-Based Design**
- **Auditing Toy Polynomial Commitments: Pedersen Coefficients, Fake Pairings, and KZG Pitfalls**
- **CryptoSage: Reviewed SageMath Cryptography Examples**
- **Homomorphic ElGamal Voting: What the Toy Prototype Shows—and What a Secure Election Still Needs**
- **NTRU Structured Gram–Schmidt: Symplectic and Isometric Shortcuts**
- **QFESTA: Quaternion-Accelerated Isogeny-Based Key Encapsulation After the SIDH Breaks**
- **The RSA Cryptosystem: Extended Reference**
- **SageMath Public-Key Cryptography Lab: Auditing RSA/CRT, Diffie–Hellman, ElGamal, ECDH, and Textbook Signatures**
- **Why Algebra Matters in Cryptography**

That gives **208 published articles total**.

## Topic taxonomy

### Foundations
Cryptography Fundamentals; Classical Cryptography; Mathematical Foundations; Abstract Algebra; Finite Fields; Linear Algebra; Lattice Theory; Algebraic Geometry; Elliptic Curve Theory; Number Theory; Discrete Logarithms.

### Core Cryptography
Public-Key Cryptography; Digital Signatures; Key Exchange; Elliptic-Curve Cryptography; Symmetric Cryptography; Hash Functions.

### Security Analysis
Cryptanalysis; Implementation Security; Lattice Methods.

### Engineering & Assurance
Cryptographic Engineering; Randomness & Entropy; Formal Verification.

### Modern Cryptography
Zero-Knowledge Proofs; Polynomial Commitments; MPC; Secret Sharing; Threshold Cryptography; Homomorphic Encryption; Post-Quantum Cryptography.

## Source-batch decisions

- `Part1.zip` → `site-planning/part1-source-ledger.csv`
- `Part2.zip` → `site-planning/part2-source-ledger.csv`
- `Mathematics.zip` → `site-planning/mathematics-source-ledger.csv`
- `Lattices.zip` → `site-planning/lattices-source-ledger.csv`
- `ZKPs.zip` → `site-planning/zkps-source-ledger.csv`
- `Threshold Python.zip` → `site-planning/threshold-python-source-ledger.csv`
- `Secret Sharing(1).zip` → `site-planning/secret-sharing-source-ledger.csv`
- Ross PQC + Random SageMath batch → `site-planning/pqc-sagemath-source-ledger.csv`

Raw incoming ZIPs, paper/PDF libraries, bundled virtual environments, generated caches, model checkpoints, and copied third-party repositories are excluded from the compact canonical master. Provenance is preserved by per-file SHA-256 ledgers and cleanup notes.

## Canonical source policy

1. Published prose: `src/content/blog/`.
2. Executable/reviewed companion material: `experiments/`.
3. Source provenance and selected non-public notes: `research-notes/`.
4. Current architecture and file-by-file decisions: `site-planning/`.
5. Large papers, raw batch ZIPs, generated artifacts, virtual environments, checkpoints, and third-party repository snapshots are excluded from the downloadable master.
6. Never duplicate an article merely because another source file exists; merge unique information into the canonical destination and record provenance.

