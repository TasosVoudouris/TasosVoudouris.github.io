"""Kasiski examination and a teaching Vigenere-cipher breaker.

The module follows the complete classical workflow:

1. normalize text and apply the repeating-key Vigenere cipher;
2. find repeated ciphertext n-grams and measure their spacings;
3. vote for period candidates using divisors of those spacings;
4. cross-check candidates with column-wise Index of Coincidence (IC);
5. recover each Caesar shift using chi-squared English-frequency scoring; and
6. decrypt and verify the result.

The implementation is intentionally readable and dependency-free.  It is for
education and authorized analysis of classical ciphers, not modern encryption.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_SIZE = len(ALPHABET)
A2I = {character: index for index, character in enumerate(ALPHABET)}
I2A = {index: character for index, character in enumerate(ALPHABET)}
RANDOM_IC = 1 / ALPHABET_SIZE

# Typical monogram probabilities for English.  They form a model, not a law:
# genre, names, abbreviations, and short columns can differ substantially.
ENGLISH_FREQUENCIES = {
    "A": 0.08167,
    "B": 0.01492,
    "C": 0.02782,
    "D": 0.04253,
    "E": 0.12702,
    "F": 0.02228,
    "G": 0.02015,
    "H": 0.06094,
    "I": 0.06966,
    "J": 0.00153,
    "K": 0.00772,
    "L": 0.04025,
    "M": 0.02406,
    "N": 0.06749,
    "O": 0.07507,
    "P": 0.01929,
    "Q": 0.00095,
    "R": 0.05987,
    "S": 0.06327,
    "T": 0.09056,
    "U": 0.02758,
    "V": 0.00978,
    "W": 0.02360,
    "X": 0.00150,
    "Y": 0.01974,
    "Z": 0.00074,
}
ENGLISH_IC = sum(probability * probability for probability in ENGLISH_FREQUENCIES.values())


@dataclass(frozen=True)
class PeriodEvidence:
    """Evidence used to rank one candidate Vigenere period."""

    period: int
    kasiski_votes: int
    average_ic: float
    kasiski_component: float
    ic_component: float
    combined_score: float


@dataclass(frozen=True)
class BreakResult:
    """Result of the end-to-end teaching attack."""

    period: int
    key: str
    plaintext: str
    period_ranking: tuple[PeriodEvidence, ...]
    distance_counts: tuple[tuple[int, int], ...]


# ---------------------------------------------------------------------------
# Text normalization and Vigenere arithmetic
# ---------------------------------------------------------------------------


def clean_text(text: str) -> str:
    """Return only ASCII letters A--Z, converted to uppercase.

    Positions reported by the cryptanalysis functions refer to this normalized
    stream, not to offsets in a formatted source document.
    """

    return re.sub(r"[^A-Z]", "", text.upper())


def _clean_key(key: str) -> str:
    normalized = clean_text(key)
    if not normalized:
        raise ValueError("key must contain at least one ASCII letter A--Z")
    return normalized


def _transform_vigenere(text: str, key: str, decrypt: bool, preserve_nonletters: bool) -> str:
    normalized_key = _clean_key(key)
    output: list[str] = []
    key_index = 0

    for character in text.upper():
        if character not in A2I:
            if preserve_nonletters:
                output.append(character)
            continue
        key_shift = A2I[normalized_key[key_index % len(normalized_key)]]
        value = A2I[character]
        transformed = (value - key_shift if decrypt else value + key_shift) % ALPHABET_SIZE
        output.append(I2A[transformed])
        key_index += 1

    return "".join(output)


def vigenere_encrypt(plaintext: str, key: str, *, preserve_nonletters: bool = False) -> str:
    """Encrypt with the repeating-key Vigenere convention ``C_i=P_i+K_i mod 26``."""

    return _transform_vigenere(plaintext, key, False, preserve_nonletters)


def vigenere_decrypt(ciphertext: str, key: str, *, preserve_nonletters: bool = False) -> str:
    """Decrypt with ``P_i=C_i-K_i mod 26``."""

    return _transform_vigenere(ciphertext, key, True, preserve_nonletters)


# Backward-compatible aliases for the spelling used in the original notebook.
vigener_encrypt = vigenere_encrypt
vigener_decrypt = vigenere_decrypt
text2message = clean_text


def _assert_alphabet(text: str) -> None:
    """Compatibility validator for the original notebook helpers."""

    if any(character not in A2I for character in text):
        raise ValueError("text must contain uppercase A--Z only")


def alphabet_sum(left: str, right: str) -> str:
    """Return one-letter addition modulo 26 (original notebook API)."""

    _assert_alphabet(left + right)
    if len(left) != 1 or len(right) != 1:
        raise ValueError("alphabet_sum expects two single letters")
    return I2A[(A2I[left] + A2I[right]) % ALPHABET_SIZE]


def alphabet_diff(left: str, right: str) -> str:
    """Return one-letter subtraction modulo 26 (original notebook API)."""

    _assert_alphabet(left + right)
    if len(left) != 1 or len(right) != 1:
        raise ValueError("alphabet_diff expects two single letters")
    return I2A[(A2I[left] - A2I[right]) % ALPHABET_SIZE]


def _vigener_encrypt(message: str, key: str) -> str:
    """Compatibility wrapper for the original internal encryption helper."""

    _assert_alphabet(message)
    _assert_alphabet(key)
    return vigenere_encrypt(message, key)


def print_enumerated(iterable: Iterable[object], label: str) -> None:
    """Print numbered values, truncating only their display representation."""

    print(f"{label}:")
    for index, item in enumerate(iterable, start=1):
        value = str(item)
        print(f"{index:>2}: {value if len(value) <= 100 else value[:80] + '...'}")


# ---------------------------------------------------------------------------
# Kasiski examination
# ---------------------------------------------------------------------------


def find_repeated_ngrams_positions(text: str, n: int) -> dict[str, list[int]]:
    """Map each repeated normalized n-gram to all of its start positions."""

    normalized = clean_text(text)
    if n <= 0:
        raise ValueError("n must be positive")
    if n > len(normalized):
        return {}

    positions: defaultdict[str, list[int]] = defaultdict(list)
    for start in range(len(normalized) - n + 1):
        positions[normalized[start : start + n]].append(start)
    return {
        ngram: starts
        for ngram, starts in positions.items()
        if len(starts) >= 2
    }


def all_distances_from_positions(
    positions: Sequence[int], *, consecutive_only: bool = True
) -> list[int]:
    """Return positive spacings among sorted occurrence positions.

    Consecutive spacings avoid giving a sequence with many occurrences
    quadratically more weight.  ``consecutive_only=False`` returns all pairs.
    """

    ordered = sorted(positions)
    if len(set(ordered)) != len(ordered):
        raise ValueError("positions must be distinct")
    if consecutive_only:
        return [right - left for left, right in zip(ordered, ordered[1:])]
    return [right - left for left, right in combinations(ordered, 2)]


def kasiski_distances(
    text: str,
    min_n: int = 3,
    max_n: int = 5,
    *,
    consecutive_only: bool = True,
) -> tuple[Counter[int], list[int]]:
    """Collect spacings for repeated n-grams with lengths ``min_n..max_n``.

    The returned counter records how often each distance occurs; the flat list
    is convenient for divisor voting.  Evidence from overlapping n-grams is
    correlated, which is why the output should be treated as a ranking signal
    rather than an exact probability.
    """

    if min_n <= 0 or max_n < min_n:
        raise ValueError("require 1 <= min_n <= max_n")
    normalized = clean_text(text)
    distances: list[int] = []
    for n in range(min_n, max_n + 1):
        repeated = find_repeated_ngrams_positions(normalized, n)
        for positions in repeated.values():
            distances.extend(
                all_distances_from_positions(
                    positions, consecutive_only=consecutive_only
                )
            )
    return Counter(distances), distances


def factor_score(
    distances: Iterable[int], max_period: int = 20, min_period: int = 2
) -> Counter[int]:
    """Vote for candidate periods that divide observed Kasiski spacings."""

    if min_period < 1 or max_period < min_period:
        raise ValueError("require 1 <= min_period <= max_period")
    votes: Counter[int] = Counter()
    for distance in distances:
        if distance <= 0:
            continue
        for candidate in range(min_period, max_period + 1):
            if distance % candidate == 0:
                votes[candidate] += 1
    return votes


def gcd_score(
    distances: Iterable[int], max_period: int = 20, min_period: int = 2
) -> Counter[int]:
    """Count pairwise spacing GCDs and their bounded divisors.

    This is supplementary evidence.  A single global GCD is often destroyed by
    one accidental repeat, while pairwise GCDs are more tolerant of outliers.
    """

    values = sorted({distance for distance in distances if distance > 0})
    gcds = [math.gcd(left, right) for left, right in combinations(values, 2)]
    return factor_score(gcds, max_period=max_period, min_period=min_period)


# Compatibility wrapper corresponding to the original notebook API.
def kasiski_examination(
    ciphertext: str,
    seq_len: int,
    max_key_len: int,
    *,
    verbose: bool = False,
) -> int:
    """Return the leading divisor-vote candidate for one n-gram length."""

    distance_counts, distances = kasiski_distances(
        ciphertext, min_n=seq_len, max_n=seq_len
    )
    votes = factor_score(distances, max_period=max_key_len)
    if not votes:
        raise ValueError("no repeated sequences produced a period candidate")
    if verbose:
        print("Repeated-distance counts:", distance_counts.most_common())
        print("Factor votes:", votes.most_common())
    return votes.most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Index of Coincidence and period ranking
# ---------------------------------------------------------------------------


def index_of_coincidence(text: str) -> float:
    """Return ``sum_i f_i(f_i-1) / (N(N-1))`` for normalized text."""

    normalized = clean_text(text)
    length = len(normalized)
    if length <= 1:
        return 0.0
    counts = Counter(normalized)
    numerator = sum(count * (count - 1) for count in counts.values())
    return numerator / (length * (length - 1))


def split_columns(text: str, period: int) -> list[str]:
    """Split a normalized stream into ``period`` interleaved Caesar columns."""

    normalized = clean_text(text)
    if period <= 0:
        raise ValueError("period must be positive")
    return [normalized[offset::period] for offset in range(period)]


def _freq(text: str) -> Counter[str]:
    """Compatibility wrapper returning normalized letter counts."""

    return Counter(clean_text(text))


def _blocks(ciphertext: str, key_len: int) -> list[str]:
    """Compatibility alias for splitting interleaved Vigenere columns."""

    return split_columns(ciphertext, key_len)


def average_column_ic(ciphertext: str, period: int, *, weighted: bool = False) -> float:
    """Return the mean IC after splitting into candidate-period columns.

    With ``weighted=True``, columns are weighted by their number of unordered
    character pairs.  The default arithmetic mean matches common classroom
    presentations and the original code.
    """

    columns = split_columns(ciphertext, period)
    if weighted:
        weights = [len(column) * (len(column) - 1) for column in columns]
        denominator = sum(weights)
        if denominator == 0:
            return 0.0
        weighted_sum = sum(
            index_of_coincidence(column) * weight
            for column, weight in zip(columns, weights)
        )
        return weighted_sum / denominator
    return sum(index_of_coincidence(column) for column in columns) / len(columns)


def best_period_by_ic(ciphertext: str, max_period: int = 20) -> list[tuple[int, float]]:
    """Rank candidate periods by descending average column IC."""

    if max_period <= 0:
        raise ValueError("max_period must be positive")
    ranking = [
        (period, average_column_ic(ciphertext, period))
        for period in range(1, max_period + 1)
    ]
    return sorted(ranking, key=lambda item: (-item[1], item[0]))


def friedman_period_estimate(ciphertext: str, language_ic: float = ENGLISH_IC) -> float:
    """Return Friedman's approximate repeating-key period estimate.

    The estimate is unstable when the denominator is near zero and is only a
    cross-check; it need not be an integer or equal the true period.
    """

    normalized = clean_text(ciphertext)
    length = len(normalized)
    if length <= 1:
        raise ValueError("at least two letters are required")
    observed_ic = index_of_coincidence(normalized)
    denominator = (length - 1) * observed_ic - RANDOM_IC * length + language_ic
    if denominator <= 0:
        return math.inf
    return (language_ic - RANDOM_IC) * length / denominator


def rank_periods(
    ciphertext: str,
    max_period: int = 20,
    min_n: int = 3,
    max_n: int = 5,
    *,
    kasiski_weight: float = 0.55,
) -> list[PeriodEvidence]:
    """Combine normalized Kasiski votes and column-IC evidence.

    Kasiski often favours divisors, while average IC often favours a true period
    *or one of its multiples*.  Combining the two signals helps identify the
    fundamental period.  The weight is a transparent teaching heuristic, not a
    universal statistical optimum.
    """

    normalized = clean_text(ciphertext)
    if len(normalized) < 2:
        raise ValueError("ciphertext must contain at least two letters")
    if max_period <= 0:
        raise ValueError("max_period must be positive")
    if not 0 <= kasiski_weight <= 1:
        raise ValueError("kasiski_weight must lie in [0, 1]")

    _, distances = kasiski_distances(normalized, min_n, max_n)
    votes = factor_score(distances, max_period=max_period)
    ic_by_period = {
        period: average_column_ic(normalized, period)
        for period in range(1, max_period + 1)
    }

    maximum_votes = max(votes.values(), default=0)
    ic_excess = {
        period: max(0.0, value - RANDOM_IC)
        for period, value in ic_by_period.items()
    }
    maximum_excess = max(ic_excess.values(), default=0.0)

    evidence: list[PeriodEvidence] = []
    for period in range(1, max_period + 1):
        kasiski_component = votes[period] / maximum_votes if maximum_votes else 0.0
        ic_component = ic_excess[period] / maximum_excess if maximum_excess else 0.0
        combined = (
            kasiski_weight * kasiski_component
            + (1 - kasiski_weight) * ic_component
        )
        evidence.append(
            PeriodEvidence(
                period=period,
                kasiski_votes=votes[period],
                average_ic=ic_by_period[period],
                kasiski_component=kasiski_component,
                ic_component=ic_component,
                combined_score=combined,
            )
        )
    return sorted(evidence, key=lambda row: (-row.combined_score, row.period))


# ---------------------------------------------------------------------------
# Caesar-column recovery
# ---------------------------------------------------------------------------


def _frequency_vector(
    frequencies: Mapping[str, float] = ENGLISH_FREQUENCIES,
) -> list[float]:
    if set(frequencies) != set(ALPHABET):
        raise ValueError("frequency model must define every letter A--Z exactly once")
    vector = [float(frequencies[character]) for character in ALPHABET]
    if any(value <= 0 for value in vector):
        raise ValueError("all modeled letter probabilities must be positive")
    total = sum(vector)
    return [value / total for value in vector]


def chi_squared_stat(
    observed_counts: Sequence[int],
    sample_size: int,
    frequencies: Mapping[str, float] = ENGLISH_FREQUENCIES,
) -> float:
    """Return Pearson's chi-squared statistic against a language model."""

    if len(observed_counts) != ALPHABET_SIZE:
        raise ValueError("observed_counts must contain 26 entries")
    if sample_size <= 0 or sum(observed_counts) != sample_size:
        raise ValueError("sample_size must be positive and equal the observed total")
    expected_probabilities = _frequency_vector(frequencies)
    statistic = 0.0
    for observed, probability in zip(observed_counts, expected_probabilities):
        expected = probability * sample_size
        statistic += (observed - expected) ** 2 / expected
    return statistic


def rank_shifts_for_column(
    column: str,
    frequencies: Mapping[str, float] = ENGLISH_FREQUENCIES,
) -> list[tuple[int, float]]:
    """Rank all 26 Caesar-key shifts for one Vigenere column."""

    normalized = clean_text(column)
    if not normalized:
        raise ValueError("column must contain at least one letter")
    cipher_counts = [0] * ALPHABET_SIZE
    for character in normalized:
        cipher_counts[A2I[character]] += 1

    ranking: list[tuple[int, float]] = []
    for shift in range(ALPHABET_SIZE):
        # Plaintext count at p equals ciphertext count at (p + shift) mod 26.
        deciphered_counts = cipher_counts[shift:] + cipher_counts[:shift]
        statistic = chi_squared_stat(deciphered_counts, len(normalized), frequencies)
        ranking.append((shift, statistic))
    return sorted(ranking, key=lambda item: (item[1], item[0]))


def best_shift_for_column(
    column: str,
    frequencies: Mapping[str, float] = ENGLISH_FREQUENCIES,
) -> int:
    """Return the minimum-chi-squared Caesar key shift for a column."""

    return rank_shifts_for_column(column, frequencies)[0][0]


def minimal_repeating_unit(value: str) -> str:
    """Return the shortest string whose repetitions produce ``value``."""

    if not value:
        raise ValueError("value must not be empty")
    for length in range(1, len(value) + 1):
        if len(value) % length == 0 and value == value[:length] * (len(value) // length):
            return value[:length]
    return value


def recover_key(
    ciphertext: str,
    period: int,
    frequencies: Mapping[str, float] = ENGLISH_FREQUENCIES,
    *,
    reduce_repeated: bool = False,
) -> str:
    """Recover a Vigenere key for a supplied candidate period."""

    columns = split_columns(ciphertext, period)
    if any(not column for column in columns):
        raise ValueError("period cannot exceed normalized ciphertext length")
    key = "".join(
        I2A[best_shift_for_column(column, frequencies)]
        for column in columns
    )
    return minimal_repeating_unit(key) if reduce_repeated else key


def frequency_analysis(
    ciphertext: str,
    key_len: int,
    text_freq: Mapping[str, int] | None = None,
    *,
    verbose: bool = False,
) -> str:
    """Compatibility wrapper using the stronger chi-squared method.

    The old implementation used the plaintext's own most-common letter, which
    leaked unavailable information to the attacker.  ``text_freq`` is accepted
    only for API compatibility and is intentionally ignored.
    """

    key = recover_key(ciphertext, key_len)
    if verbose:
        print(f"Recovered key candidate: {key}")
    return key


def break_vigenere(
    ciphertext: str,
    max_period: int = 20,
    min_n: int = 3,
    max_n: int = 5,
    *,
    kasiski_weight: float = 0.55,
) -> BreakResult:
    """Run period ranking, key recovery, and decryption end to end."""

    normalized = clean_text(ciphertext)
    ranking = rank_periods(
        normalized,
        max_period=max_period,
        min_n=min_n,
        max_n=max_n,
        kasiski_weight=kasiski_weight,
    )
    period = ranking[0].period
    key = recover_key(normalized, period, reduce_repeated=True)
    plaintext = vigenere_decrypt(normalized, key)
    distance_counter, _ = kasiski_distances(normalized, min_n, max_n)
    return BreakResult(
        period=len(key),
        key=key,
        plaintext=plaintext,
        period_ranking=tuple(ranking),
        distance_counts=tuple(distance_counter.most_common()),
    )


# ---------------------------------------------------------------------------
# Deterministic demonstration
# ---------------------------------------------------------------------------


def demo() -> BreakResult:
    """Attack the bundled English sample encrypted under the key ``MOUSE``."""

    input_path = Path(__file__).with_name("input-1-50.txt")
    plaintext = clean_text(input_path.read_text(encoding="utf-8"))
    true_key = "MOUSE"
    ciphertext = vigenere_encrypt(plaintext, true_key)
    result = break_vigenere(ciphertext, max_period=20)

    print("=== Kasiski / Vigenere teaching demonstration ===")
    print(f"Normalized ciphertext length: {len(ciphertext)}")
    print(f"True key:                    {true_key}")
    print(f"Recovered key:               {result.key}")
    print(f"Recovered period:            {result.period}")
    print(f"Friedman estimate:           {friedman_period_estimate(ciphertext):.2f}")
    print("\nTop repeated-sequence distances (distance, count):")
    print(list(result.distance_counts[:10]))
    print("\nTop combined period candidates:")
    for row in result.period_ranking[:10]:
        print(
            f"period={row.period:2d}  votes={row.kasiski_votes:4d}  "
            f"avgIC={row.average_ic:.4f}  score={row.combined_score:.3f}"
        )
    print(f"\nDecryption correct: {result.plaintext == plaintext}")

    assert result.key == true_key
    assert result.plaintext == plaintext
    return result


def main() -> None:
    """Run known-answer checks followed by the bundled demonstration."""

    assert vigenere_encrypt("ATTACK AT DAWN", "LEMON") == "LXFOPVEFRNHR"
    assert vigenere_decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"
    demo()


if __name__ == "__main__":
    main()
