# Validation notes — CryptoCave organized v5

Validated on 2026-09-12 after integrating `rdy.zip` into the organized Astro CryptoCave repository.

## Content checks passed

- 76 published Markdown articles are present.
- 11 new site-native articles were created from `rdy.zip` plus its interpolation benchmark bundle.
- The existing robust Gao/Reed-Solomon article was moved into the new ordered threshold-cryptography series.
- Every article has non-empty body content.
- All frontmatter topic values exist in `src/data/topics.ts`.
- All frontmatter series values exist in `src/data/series.ts`.
- Series positions are unique within each series.
- The new **Secret Sharing & Threshold Cryptography** series contains 11 ordered articles.
- The general entropy/CSPRNG article is part of **Cryptography Primer** rather than the threshold series.
- Every absolute `/images/...` reference resolves to a file under `public/`.
- Every article `sourcePath` resolves to an existing repository path.
- Markdown code fences are balanced.
- The original `rdy.zip` source material is preserved under `research-notes/threshold-cryptography/original-rdy/`.

## Technical/editorial corrections

- Split the mixed `Randomness.md` source into local cryptographic randomness and distributed randomness beacon articles.
- Split the mixed `DKG.md` source into VSS/Pedersen-style DKG and aggregatable-DKG/SCRAPE research-note articles.
- Corrected packed-sharing point/domain wording and polynomial-degree statements.
- Distinguished single-target interpolation from full polynomial interpolation complexity.
- Corrected the conceptual distinctions among multisignatures, aggregate signatures, DKG, and threshold signatures.
- Replaced over-broad DKG resilience claims with protocol/model-specific wording.
- Distinguished Shannon entropy from min-entropy and corrected entropy-combination claims.
- Modernized operating-system CSPRNG guidance.
- Documented the missing `FFTonly` module in the recovered benchmark bundle instead of fabricating a dependency.

## Companion-code checks

The new companion area is:

```text
experiments/threshold-cryptography/
```

- Dependency-free educational implementations are provided for additive sharing, Shamir sharing, packed sharing, polynomial splitting, and FFT-packed sharing.
- All Python files in the new threshold-cryptography tree pass syntax compilation.
- `python experiments/threshold-cryptography/run_all.py` passes all dependency-free checks.
- SageMath interpolation benchmark code and original PDF/PNG plots are preserved as research material.
- The recovered Gao implementation is linked from the robust-secret-sharing article.

## Git checks

- Branch: `main`
- Origin: `https://github.com/TasosVoudouris/TasosVoudouris.github.io.git`

## Native Astro build limitation

A clean `npm ci` was attempted in the sandbox but did not complete before the environment timeout, so the native Astro production build could not be executed here. The final local release gate remains:

```bash
npm ci
npm run build
npm run preview
```

Run those commands on the local Windows development machine before pushing to GitHub.
