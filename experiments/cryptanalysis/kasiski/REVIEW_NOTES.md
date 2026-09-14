# Review Notes

This revision preserves the original sequence—alphabet, Vigenère encryption,
Kasiski examination, frequency analysis, and decryption—while unifying the
notebook and standalone script around one tested implementation.

## Theory corrections

- Distinguished a written key length from its shortest fundamental period.
- Explained why a repeated ciphertext n-gram supplies divisibility evidence but
  does not prove the period.
- Added accidental-repeat analysis and the approximate random collision count.
- Explained that nested and overlapping n-gram observations are dependent.
- Added complete IC definitions, baselines, and the average-column method.
- Explained why IC often ranks multiples of the true period highly.
- Added the Friedman period estimate as an approximate cross-check.
- Replaced single-statistic certainty with an inspectable combined ranking.
- Added chi-squared recovery over all 26 shifts and limitations of monograms.
- Added applicability boundaries for Beaufort, autokey, running-key systems,
  one-time pads, and modern encryption.

## Code corrections

- Corrected `range(len(ciphertext) - seq_len)` so the final n-gram window is not
  omitted.
- Replaced incomplete square-root factor enumeration with exact bounded divisor
  testing, including large complementary factors and the candidate equal to the
  spacing.
- Replaced the notebook's plaintext-derived most-common-letter shortcut, which
  leaked information unavailable to a ciphertext-only attacker.
- Prevented raw maximum IC from reporting a nonminimal harmonic period.
- Reduced exactly repeated recovered keys to their shortest unit.
- Added empty-key, malformed-input, and candidate-range validation.
- Generalized formatting preservation beyond spaces while ensuring nonletters
  do not consume key positions.
- Added a `__main__` guard so importing the module has no demonstration side
  effects.
- Made the bundled input path robust relative to the script location.
- Corrected spelling and documentation for “Vigenère,” “frequency,” and key
  types while retaining the old `vigener_*` aliases for compatibility.
- Added evidence dataclasses and retained full candidate rankings.

## Verification performed

- `python -m unittest -v test_kasiski.py`: 17 tests pass.
- The notebook's code cells execute sequentially.
- The known `ATTACK AT DAWN` / `LEMON` vector passes.
- The bundled sample selects period `5`, recovers `MOUSE`, and decrypts exactly.
- Every local Markdown link resolves.
- All Markdown files pass `markdownlint-cli2`.
