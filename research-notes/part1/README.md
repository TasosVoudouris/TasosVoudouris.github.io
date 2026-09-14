# Part 1 provenance note

`Part1.zip` was integrated into the canonical CryptoCave master during the v6.2 cleanup pass.

The exact uploaded source archive is retained only in the FULL local master at:

```text
.local-reference-library/source-batches/Part1.zip
```

It is intentionally ignored by Git. The active site/repository contains only the cleaned canonical outputs.

See:

- `site-planning/part1-cleanup.md` for the human-readable decisions;
- `site-planning/part1-source-ledger.csv` for one SHA-256-backed row per original source file.

## Main outputs

- `src/content/blog/digital-signatures-foundations.md` through `eddsa-ed25519-ed448.md`
- `src/content/blog/classical-ciphers-frequency-analysis.md`
- `src/content/blog/otp-stream-cipher-key-reuse.md`
- `src/content/blog/authenticated-encryption-aead.md`
- `src/content/blog/26-rsa-factorization-structured-primes.md`
- `src/content/blog/attribute-based-encryption.md`
- `src/content/blog/elgamal-homomorphic-voting-research-note.md`
- `experiments/digital-signatures/`
- `experiments/classical-cryptanalysis/`
- `experiments/rsa/factorization-methods/`
- `experiments/elgamal-voting/`

## Editorial rule

The raw source was not copied wholesale. Existing stronger canonical articles remain authoritative; only unique value was merged, and technically misleading claims were corrected rather than preserved for historical fidelity.
