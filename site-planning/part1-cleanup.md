# Part 1 cleanup and migration map — v6.2

`Part1.zip` is treated as a **source batch**, not as a second site tree. The exact uploaded archive is retained in the FULL master at `.local-reference-library/source-batches/Part1.zip`; it is ignored by Git and excluded from the GitHub-ready package.

## Accounting

- Original source files in `Part1.zip`: **295**.
- Ledger rows in `part1-source-ledger.csv`: **295**.
- Unclassified source files: **0**.
- Active canonical site articles after Part 1 integration: **127**.
- Ordered series after integration: **14**.
- Topic areas after integration: **23**.

## Disposition summary

| Disposition | Files |
|---|---:|
| `archived_legacy_reference` | 76 |
| `archived_reference_only` | 1 |
| `archived_teaching_artifact` | 13 |
| `archived_third_party_reference` | 4 |
| `discarded_generated_artifact` | 1 |
| `integrated_rewritten` | 70 |
| `superseded_by_canonical` | 120 |
| `superseded_exact_duplicate` | 10 |

## Canonical additions from Part 1

### Digital Signatures

A new seven-part ordered series replaces the scattered signature notes, notebooks, and ad-hoc scripts:

1. Digital Signatures I — Security Goals, Hash-Then-Sign, and What Can Go Wrong
2. RSA Signatures — From Textbook Exponentiation to RSASSA-PSS
3. ElGamal and DSA — Discrete-Log Signatures and the Nonce Equation
4. ECDSA — From the Verification Equation to secp256k1
5. ECDSA Nonce Reuse, Bias, and Verification Failures
6. Schnorr Signatures — Linear Verification, Tagged Hashes, and Multisignature Structure
7. EdDSA — Ed25519, Ed448, Deterministic Nonces, and Encoding Discipline

The old `EdDSA.py` is not treated as an RFC 8032 implementation, and the old DSA material is presented with its current legacy-generation status rather than as a recommended modern signing choice.

### Classical Cryptanalysis

The useful teaching material is now one ordered path:

1. Caesar, Substitution, Vigenère, and Frequency Analysis
2. The Kasiski Examination: Cryptanalysis of the Vigenère Cipher
3. One-Time Pads, Stream Ciphers, and the Catastrophe of Key/Nonce Reuse

The previously reviewed Kasiski implementation remains canonical; duplicate ZIPs/notebooks are not republished.

### Symmetric cryptography

`Authenticated Encryption and AEAD: From Encrypt-then-MAC to GCM and ChaCha20-Poly1305` is inserted before Matsui in the Symmetric Cryptography sequence. The source PDF is not republished.

### RSA

Scattered RSA scripts/notebooks are mapped to the existing RSA Deep Dives. Unique factorization material is consolidated into **RSA Deep Dive XIII: Factorization When the Prime Structure Helps — Fermat, Pollard p−1, Williams p+1, and ECM**. The synthesis/attack-map article becomes Part XIV.

The old `PEMattack.md` is explicitly corrected: PEM is a serialization/container format; disclosure or mishandling of a private-key file is key-management compromise, not a mathematical attack on RSA.

### Standalone references / research notes

- **Attribute-Based Encryption: KP-ABE, CP-ABE, Access Policies, and Pairing-Based Design** — reference article; the old ABE repository remains local-only source material.
- **Homomorphic ElGamal Voting: What the Toy Prototype Shows—and What a Secure Election Still Needs** — research note. The old prototype is *not* presented as a secure voting system; only the useful homomorphic-tally algebra is retained in a clean toy experiment.

## What is intentionally not active

- duplicated Matsui/Kasiski packages;
- cloned third-party attack/teaching repositories;
- old RSA attack scripts already superseded by the RSA Deep Dives;
- lecture PDFs/PPTX and CTF exercises;
- generated `__pycache__`/`.pyc` artifacts;
- old ad-hoc signature implementations that do not match the relevant standards.

These remain recoverable from the exact Part 1 source ZIP in the FULL master, but they do not clutter the Git repository or public site.

## Rule for future parts

For each incoming batch: compare first, merge only unique value, keep one canonical article per concept, keep reusable reviewed code under `experiments/`, retain exact source batches locally for provenance, and record every source file in a batch ledger before the scattered original is considered safe to delete.
