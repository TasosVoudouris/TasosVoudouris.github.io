# Review Notes

This revision preserves the original sequence of topics, examples, diagrams,
and the public helper names where practical. The following technical and
presentation issues were corrected before packaging.

## Mathematical corrections

- Distinguished linear functions from affine functions.
- Defined one consistent zero-based, MSB-first bit convention.
- Replaced ambiguous “approximately zero” wording with an explicit probability,
  bias, and correlation relation.
- Documented the exact centered-match-count convention used by the LAT.
- Added the factor-of-two conversions among LAT entries, Walsh coefficients,
  normalized correlation, and bias.
- Explained that a negative bias is useful and changes the decision sign.
- Corrected the keyed S-box relation for `Y = S(X XOR K)`.
- Added transpose-based mask propagation through the linear layer.
- Corrected the direction and names of internal variables around S-boxes.
- Corrected the spelling and domain assumptions of the piling-up lemma.
- Separated a fixed intermediate-mask trail from the complete linear hull.
- Replaced the exact-looking `N = 1 / epsilon^2` claim with a complexity scale
  whose constant depends on the statistical decision problem.
- Clarified that Algorithm 1 yields a key parity and Algorithm 2 ranks guessed
  outer-round subkeys.

## Code corrections

- Removed unnecessary NumPy and PyCryptodome dependencies.
- Added validation for S-boxes, P-boxes, masks, words, and paired data.
- Added a true inverse P-box and used it in SPN decryption.
- Made leading-zero S-box chunks explicit in block operations.
- Ranked Algorithm 2 candidates by `abs(T0 - T1)`, not only by the signed
  maximum.
- Corrected the SPN partial decryption to guess the second and fourth nibbles of
  the final whitening key before applying the inverse S-box layer.
- Corrected the ground-truth extraction for those non-contiguous nibbles.
- Changed the toy SPN master key to the 32-bit size actually consumed by its key
  schedule.
- Replaced duplicate random 4-bit samples with the complete 16-value codebook.
- Used distinct 16-bit plaintexts and a deterministic seed in the larger attack.
- Preserved `matsui1`, `matsui2`, `matsui2_big`, and the formerly misspelled
  `pilling_up_lemma` as compatibility entry points while documenting the new
  preferred functions.

## Documentation corrections

- Rebuilt all local links using exact, case-sensitive filenames.
- Removed notebook-only `attachment:` image references.
- Converted all formulas and code fences to GitHub-compatible Markdown.
- Added a table of contents, scope, attack model, limitations, advanced topics,
  ethical-use note, reproducibility instructions, and primary references.
- Added a compact executable notebook that imports the tested module instead of
  maintaining divergent copies of every function.

## Verification performed

- `python -m unittest -v test.py`: 14 tests pass.
- Every code cell in `Linear Cryptanalysis.ipynb` executes in order.
- `README.md` and `Linear Cryptanalysis.md` pass `markdownlint-cli2`.
- All local Markdown links and all seven image references resolve.
- The deterministic 8,192-pair SPN attack ranks actual packed subkey `0x6F`
  first.
