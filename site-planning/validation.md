# Validation notes — CryptoCave canonical master v6.12

Validated on 2026-09-18 after the Secret Sharing/MPC consolidation, Ross-course / historical SageMath audit batch, and the Randomness + Discrete Logarithm series refresh.

## Secret Sharing source accounting

- Original archive files: **1,278**.
- Rows in `secret-sharing-source-ledger.csv`: **1,278**.
- Unclassified source files: **0**.
- Uploaded/source-bundle SHA-256: `4bbda46c0435e3fc44118c7b04f1efee965d5bcf0df1dd735aade8c60c30fadc`.
- Bundled virtual-environment files discarded: **1,098**.
- Python bytecode/cache files discarded: **34**.
- Generated Sage-to-Python translations discarded: **8**.
- Papers/PDFs omitted: **9**.
- Nested ZIP archives omitted: **3**.
- Integrated/reworked source files: **60**.
- Sources superseded by stronger canonical material: **36**.
- Other reference-only source files: **30**.

The human-readable summary is `site-planning/secret-sharing-cleanup.md`.

## Site-content checks

- Published Markdown articles: **208**.
- Ordered series: **24**.
- Topic areas: **30**.
- Series articles: **199**.
- Standalone references/research notes: **9**.
- Articles with companion `sourcePath`: **142**.
- Secret Sharing & Polynomial Tools series: **10 articles**.
- Secure Multiparty Computation series: **6 articles**.
- Threshold Cryptography Engineering series: **28 articles**.
- Article bodies empty: **0**.
- Unknown topic values: **0**.
- Unknown series values: **0**.
- Missing/invalid difficulty values: **0**.
- Invalid status values: **0**.
- Duplicate series positions: **0**.
- Zero-based/gapped series positions: **0**.
- Missing `sourcePath` targets: **0**.
- Missing local `/images/...` assets: **0** across **120** Markdown/HTML image references.
- Broken internal `/blog/.../` article links: **0**.
- Broken rendered local heading/TOC anchors: **0**.
- Duplicate article titles: **0**.
- Unbalanced Markdown code fences: **0**.

Canonical content preflight:

```text
CryptoCave content preflight: OK (208 articles, 24 series, 30 topics).
```


## Ross PQC / historical SageMath source accounting

- Ross-course archive files: **11**.
- Random-Sage archive files: **7**.
- Combined ledger rows: **18**.
- Unclassified source files: **0**.
- Ross-course archive SHA-256: `e70e985c9cc09373b8947dc73454f7e657e0cb4752c1fef246a09c43d5ec06ae`.
- Random-Sage archive SHA-256: `914246e2594137b1ca00addd2b44fe1ba0079f829f6df760bca8119ada302197`.
- Raw notebooks, `.sagews` state, and source ZIPs are not bundled in the compact master.

Canonical additions:

- **2** validated lattice/NTRU case-study articles;
- **1** validated classical-Sage audit article inside the Classical Cryptanalysis series;
- **1** validated standalone public-key Sage audit article;
- **4** compact dependency-free executable companions.

The full file-level record is `site-planning/pqc-sagemath-source-ledger.csv`.

## Ross / Sage executable checks

```text
2D Gaussian reduction + integer-NTRU short-vector recovery: PASS
N=7 toy NTRU public-lattice / LLL equivalent-key recovery: PASS
Classical shift/affine/Hill audit lab: PASS
RSA/CRT/common-modulus/DH/ElGamal/textbook-signature audit lab: PASS
```

Technical corrections recorded in the canonical articles include:

- substitution-vs-transposition terminology;
- the correct double-affine composition `(7,10)` for the recovered example;
- modular invertibility conditions for affine/Hill systems;
- the old DH generator's ignored `bits` parameter;
- full-group versus prime-order-subgroup distinctions;
- DH-derived multiplicative masking versus actual ElGamal ciphertext structure;
- signed Bézout exponents in the RSA common-modulus attack;
- textbook RSA signature forgery versus RSASSA-PSS;
- the difference between Sage's `^` exponentiation syntax and Python's XOR operator.

## Secret Sharing / MPC technical audit

### Shamir arithmetic

Canonical material now distinguishes:

- linear operations, which preserve sharing degree;
- pointwise multiplication, which produces a valid product sharing at increased degree;
- degree reduction/resharing, which is required before arbitrary continued MPC computation.

The old `T` parameter ambiguity is removed: threshold `t` corresponds to polynomial degree `t-1`.

### Beyond Shamir

Ramp sharing, proactive refresh, access structures and share conversion are separated by security role. Centralized zero-sharing refresh is described only as an algebraic toy, not as a complete proactive-security protocol.

### NTT source audit

The recovered q=12289 NTT package was tested directly before consolidation.

Core suite:

```text
15 passed
38 subtests passed
```

for iterative/recursive transforms, polynomial arithmetic and utilities.

`test_vectors.py` fails during collection because importing its vector-generation module writes immediately to a non-existent relative `../test_vectors/` path. This is classified as a packaging/import-side-effect defect, not an arithmetic failure.

The canonical repository includes an independent dependency-free F_97 radix-2 NTT/INTT companion instead of copying the full package.

### MPC / SPDZ cleanup

Recovered additive-sharing + Beaver-triple code is reclassified as passive preprocessing-model MPC, not full SPDZ.

Canonical SPDZ material now introduces:

- the global secret MAC key;
- authenticated value/MAC shares;
- authenticated openings;
- authenticated triples;
- preprocessing validation / sacrifice context;
- MAC checks;
- explicit abort/security boundaries.

### Private ML cleanup

The recovered neural-network material is treated as architecture/cost-model research rather than end-to-end secure training. Secret-shared data is not described as ciphertext, element-wise triples are not confused with matrix triples, and ordinary Keras layers are not presented as secure subprotocols.

### Commitment-code audit

The new standalone research note records that:

- coefficient-wise Pedersen commitments are not automatically a succinct KZG-style PCS;
- a recovered Pedersen helper reuses the wrong generator index for blinding;
- naive x-coordinate scanning is not standardized hash-to-curve;
- the Sage "KZG" toy uses field multiplication as its function `e`, so it is not a cryptographic pairing/KZG implementation;
- the BLS12-381 pairing experiment is closer to KZG algebra but remains an explicitly unaudited local-trapdoor prototype.

## New executable checks

```text
Beaver multiplication:                     100/100 PASS
SPDZ MAC invariant + Beaver multiplication: PASS
Tampered authenticated share:              rejected PASS
Shamir degree-growth / trusted reduction:   PASS
Independent radix-2 NTT / INTT:             PASS
```

Run together with:

```bash
python experiments/mpc/run_all.py
```

## Python syntax validation

All active Python files under `experiments/` pass syntax compilation:

```text
Python syntax compilation: 224/224 PASS
```

## Regression checks

Representative established suites were rerun after the Secret Sharing/MPC integration:

- Hash Functions & MACs: **9/9 tests pass** plus **11 subtests**.
- Kasiski/Vigenère cryptanalysis: **17/17 tests pass**.
- Matsui linear cryptanalysis: **14/14 tests pass**.
- RSA Håstad: **7/7 tests pass**.
- RSA Wiener: **8/8 tests pass**.
- RSA Coppersmith/LLL: **10/10 tests pass**.
- Threshold/FROST v0.5: **141/141 tests pass** plus **29 subtests**.


## v6.11 representative regression rerun

After the Ross/Sage integration, the following established suites were rerun from the repository root:

- Hash Functions & MACs: **9/9**, plus **11 subtests**.
- Kasiski/Vigenère: **17/17**.
- Matsui linear cryptanalysis: **14/14**.
- RSA Håstad: **7/7**.
- RSA Wiener: **8/8**.
- RSA Coppersmith/LLL: **10/10**.
- Threshold/FROST v0.5: **141/141**, plus **29 subtests**.

All four newly introduced executable companions also pass their self-tests.

## v6.12 pre-push repair pass

The 2026-09-18 release pass repaired integration defects introduced by the large mathematics/cryptography refresh without weakening the content schema:

- normalized malformed YAML frontmatter in **20** elliptic-curve/lattice articles;
- removed the stale nonexistent `experiments/ready-material/modes` source path;
- rebuilt clean H2-only tables of contents in **78** long-form articles using Astro's generated heading IDs;
- removed redundant hand-written Previous/Next article links from the refreshed Randomness and DLOG series, leaving `BlogPost.astro` as the canonical automatic series navigator;
- expanded `check-content.mjs` to validate raw-HTML local images, internal `/blog/.../` links, duplicate titles, and rendered local anchors;
- aligned the Astro content schema with the one-based series convention by requiring positive `seriesOrder` values;
- repaired two mojibake experiment filenames with ASCII-safe names;
- removed the undeclared `pycryptodome` dependency from the BSGS/Pohlig–Hellman teaching scripts and revalidated both scripts.

Release-pass checks:

```text
CryptoCave content preflight: OK (208 articles, 24 series, 30 topics).
Rendered local-anchor validation: 0 broken anchors.
Local image validation: 120/120 references resolve.
Python syntax compilation under experiments/: PASS.
Randomness companion scripts: 4/4 PASS.
BSGS standalone companion: PASS.
Pohlig–Hellman standalone companion: PASS, exhaustive x=0..335.
Pollard-rho / BSGS / brute-force EC comparison scripts: PASS.
Hash Functions & MACs: 9/9 PASS.
Kasiski/Vigenère: 17/17 PASS.
Matsui linear cryptanalysis: 14/14 PASS.
RSA Håstad/Wiener/Coppersmith: 7/7, 8/8, 10/10 PASS.
MPC dependency-free run_all: PASS.
Threshold/FROST v0.5: 141/141 + 29 subtests PASS.
Oblivious Transfer run_all: PASS.
Zero-Knowledge companion run_all: PASS.
```

The native Astro production build remains a local release gate because this review environment contains a Windows `node_modules` snapshot while running Linux, and its Node version is below the repository's declared `>=22.19.0` engine. Run the clean-install gate with Node 24 before push.

## Compact-source policy

The release archive is prepared with:

- **0 PDFs**;
- **0 raw source ZIPs**;
- **0 bundled virtual environments**;
- **0 Python bytecode/cache artifacts after cleanup**;
- no `node_modules`, `dist`, or `.astro` build cache.

The user's original source bundle remains external; provenance is represented by SHA-256 and per-file decisions in the cleanup ledger.

## Git checks

- Branch: `main`.
- Origin: `https://github.com/TasosVoudouris/TasosVoudouris.github.io.git`.

## Native Astro release gate

Static content/preflight and Python validation pass. This environment has Node 22.16 while the repository requires Node 22.19+ and recommends Node 24, so perform the native release gate locally in a **new/empty extraction**:

```bash
npm ci
npm run dev
npm run build
npm run preview
```

Do not overlay v6.12 onto an older CryptoCave folder.
