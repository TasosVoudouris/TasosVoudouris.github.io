# CryptoCave master consolidation — v6

Source batch: `Διάφορα για Cryptocave.zip`.

## Canonical rule

1. **Site articles (`src/content/blog/`) are the canonical written reference.**
2. **`experiments/` contains companion code and validated teaching packages.**
3. **`research-notes/` contains review/audit/history that should not clutter the learning paths.**
4. **`.local-reference-library/` holds large/private third-party papers and personal research-source files. It is ignored by Git and is not deployed.**
5. Exact duplicates in the private paper library are stored once; aliases are recorded in `references/homomorphic-private-library-catalog.csv`.
6. Every file from the uploaded miscellaneous archive is represented in `master-source-ledger.csv` with a SHA-256 digest and disposition.

## Major cleanup decisions

- The two old Docusaurus CryptoCave snapshots are superseded by the Astro site.
- Threshold versions v0.1–v0.4 are superseded by reviewed v0.5; v0.5 code/tests and its unique engineering chapters are canonical.
- Hashes/MACs becomes its own full series instead of one article inside the symmetric series.
- Symmetric cryptography now ends with the reviewed Matsui linear-cryptanalysis lab.
- Kasiski becomes a standalone classical-cryptanalysis reference.
- Homomorphic material becomes an ordered series; code is explicitly marked experimental/research unless validated.
- CryptoSage is retained as a reviewed companion-code library with one site overview, not fragmented into tiny duplicate posts.
- Older RSA prose is superseded by the RSA Deep Dives; its small reviewed executable examples are retained under `experiments/rsa/reference-basics/`.
- Large homomorphic papers and personal research files remain in the one master folder but are excluded from GitHub by `.gitignore`.

## New ordered series

- Symmetric Cryptography
- Hash Functions & MACs
- Secret Sharing & Polynomial Tools
- Threshold Cryptography Engineering
- Homomorphic Encryption

Existing CryptoCave From Zero, number theory, DLP, DH/ElGamal, elliptic curves, and RSA paths remain intact.
