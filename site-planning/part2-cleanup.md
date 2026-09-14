# Part 2 cleanup and canonicalization — v6.3

`Part2.zip` was treated as a migration source, not as a directory to copy into the active site. The archive contains **235 original files** across DKG/FROST references, PRNG/stream-cipher teaching material, authenticated-encryption notebooks, oblivious-transfer notes/code, a small KEM/PQC research set, and a large adversarial-ML teaching repository.

Every original file is accounted for in `site-planning/part2-source-ledger.csv` with its SHA-256 hash, disposition, canonical destination, and cleanup rationale. The exact incoming ZIP is retained only in the FULL master at `.local-reference-library/source-batches/Part2.zip` and is ignored by Git.

## Canonical additions

### Randomness & Stream Ciphers

A new seven-part ordered path replaces scattered PRNG notebooks/Markdown:

1. **Pseudorandom Generators and Stream Ciphers: From Deterministic Expansion to Secure Keystreams**
2. **Linear Congruential Generators: Periods, Parameter Recovery, and Why Statistical Quality Is Not Security**
3. **Linear Feedback Shift Registers: Finite-Field Recurrences, Periods, and State Recovery**
4. **The Geffe Generator: How Correlation Breaks a Nonlinear Combination of LFSRs**
5. **RC4: Biases, FMS-Style Attacks, and Why the Cipher Is Obsolete**
6. **ChaCha20: ARX Design, Quarter Rounds, and a Modern Stream Cipher**
7. **Dual_EC_DRBG: A Backdoored Generator and a Lasting Design Lesson**

The old notes were not copied verbatim. Important corrections include:

- LCG parameter recovery now uses the correct recurrence indexing and states the modular-inverse condition explicitly.
- An LFSR's **all-zero state**, not the output bit zero, is the absorbing state.
- The maximal period `2^m - 1` is stated only under the primitive-polynomial/nonzero-state conditions.
- Linear complexity and recurrence recovery are separated from vague statistical randomness claims.
- The Geffe generator's `3/4` correlations are derived explicitly; period claims are no longer stated as an unconditional product.
- RC4/FMS is presented in its historical protocol context rather than as a generic theorem about every `IV || secret` construction.
- ChaCha20 uses the RFC 8439 variant and is distinguished from the ChaCha20-Poly1305 AEAD construction.
- Dual_EC_DRBG is treated historically and as a lesson in parameter transparency/state compromise, not as a current CSPRNG recommendation.

Companion code lives in `experiments/randomness-stream-ciphers/` and includes fixed checks for LCG recovery, LFSR/Geffe correlation behavior, a historical RC4 vector, and an RFC 8439 ChaCha20 block vector.

### Oblivious Transfer

A new three-part ordered path replaces mixed Sage/Markdown/prototype files:

1. **Rabin Oblivious Transfer: Square Roots, Factoring, and a 1/2 Success Probability**
2. **1-out-of-2 Oblivious Transfer from Trapdoor Permutations**
3. **Modern Oblivious Transfer: Base OT, Naor–Pinkas Context, and OT Extension**

The recovered folder labeled “Naor–Pinkas scheme” is **not** published as a Naor–Pinkas implementation. Its code combines RSA/polynomial machinery in a way that does not faithfully identify the standard construction. It remains available only in the exact source archive, while the site article gives the correct conceptual placement of Naor–Pinkas-style OT and OT extension.

Companion educational checks live in `experiments/oblivious-transfer/`.

### Threshold Cryptography Engineering

**ChillDKG: Practical DKG Design for FROST, Backups, Blame, and Taproot Safety** was added as Part 24 of the threshold-engineering path. It is deliberately labeled **Research Note**. The third-party reference repository is not copied into active experiments; its own documentation warns that the reference implementation is for tests/research rather than production/side-channel-safe deployment.

### Post-quantum research note

**QFESTA: Quaternion-Accelerated Isogeny-Based Key Encapsulation After the SIDH Breaks** was added as a standalone **Research Note**. The recovered SageMath archive is retained only in the raw Part 2 source batch. The article does not present QFESTA as a NIST-standardized KEM and does not treat proof-of-concept timings as universal performance claims.

### Authenticated encryption

Unique GCM/GHASH material from the recovered notebooks was merged into the existing canonical **Authenticated Encryption and AEAD** article. In particular, the article now explains why nonce reuse in GCM is not merely a confidentiality failure: the repeated counter-derived mask allows differences of tags to expose algebraic equations in the GHASH key `H`, which is the basis of the classic “forbidden attack” family.

No duplicate GCM article was created.

## Deliberately not imported into the active site

### Adversarial machine learning

The large adversarial-ML tutorial, MNIST data, figures, pretrained model, paper, and third-party machine-learning-book archive are useful research/teaching material but are not part of the current CryptoCave cryptography knowledge-base scope. They remain recoverable from the exact Part 2 archive and are classified as **out-of-scope reference-only** rather than inflating the public site.

### Older DKG repository

The separate P2P DKG repository/PDF is superseded by the much stronger canonical VSS → DKG → FROST sequence. It is retained only for provenance.

### Duplicate linear-cryptanalysis notebook

The actual linear-cryptanalysis notebook in the misleadingly named folder is superseded by the reviewed Matsui article and its test suite already present in CryptoCave.

### Kyber gate-count PDF

The single Kyber-512 gate-count analysis is retained as a future PQC reference. One cost-model document is not elevated into a canonical CryptoCave conclusion.

## Source accounting

The source ledger records:

- **235** original files;
- **22** integrated/reworked source files;
- **25** exact byte-duplicate entries within Part 2;
- **25** sources superseded by stronger canonical material;
- **36** reference-only/source-bundle files;
- **104** out-of-scope reference-only files;
- **5** mislabeled OT source files retained only for provenance;
- **18** generated cache/checkpoint artifacts discarded from canonical content.

Unclassified source files: **0**.
