"""Educational implementations of Matsui-style linear cryptanalysis.

The module deliberately uses small substitution-permutation networks so that
every table and experiment can be checked exhaustively.  It is teaching code,
not a cryptanalytic framework and not production cryptography.

Conventions
-----------
* ``dot(x, mask)`` is the binary inner product (parity of ``x & mask``).
* A LAT entry is the *centered match count* ``matches - 2**(n - 1)``.
* Walsh coefficient ``W = 2 * LAT[a][b]``.
* Correlation ``C = W / 2**n`` and bias ``epsilon = C / 2``.
* Bit positions used by ``get_bit_msb`` and P-boxes are zero-based, MSB first.

Run ``python matsui1.py`` for deterministic demonstrations and
``python -m unittest -v test.py`` for the verification suite.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from random import Random
from typing import Iterable, Sequence


PRESENT_SBOX = [12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2]
COMPANION_SBOX = [15, 14, 11, 12, 6, 13, 7, 8, 0, 3, 9, 10, 4, 2, 1, 5]
TOY_SPN_SBOX = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
TOY_SPN_PBOX = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]


# ---------------------------------------------------------------------------
# Bit, S-box, and P-box helpers
# ---------------------------------------------------------------------------


def get_bit_msb(x: int, position: int, width: int) -> int:
    """Return a bit using zero-based, most-significant-bit-first indexing."""
    if not 0 <= position < width:
        raise ValueError("position must be in range(width)")
    return (x >> (width - 1 - position)) & 1


def set_bit_msb(x: int, position: int, width: int, value: int) -> int:
    """Set a bit using zero-based, most-significant-bit-first indexing."""
    if not 0 <= position < width:
        raise ValueError("position must be in range(width)")
    if value not in (0, 1):
        raise ValueError("value must be 0 or 1")
    bit = 1 << (width - 1 - position)
    return (x | bit) if value else (x & ~bit)


def bit_parity(x: int) -> int:
    """Return the XOR of all set bits of a non-negative integer."""
    if x < 0:
        raise ValueError("x must be non-negative")
    return x.bit_count() & 1


def dot(x: int, mask: int) -> int:
    """Return the binary inner product: ``parity(x & mask)``."""
    if x < 0 or mask < 0:
        raise ValueError("x and mask must be non-negative")
    return bit_parity(x & mask)


def _infer_sbox_width(sbox: Sequence[int]) -> int:
    size = len(sbox)
    if size < 2 or size & (size - 1):
        raise ValueError("S-box length must be a power of two")
    width = size.bit_length() - 1
    if sorted(sbox) != list(range(size)):
        raise ValueError("S-box must be a permutation of range(len(sbox))")
    return width


def inverse_sbox(sbox: Sequence[int]) -> list[int]:
    """Return the inverse of a bijective S-box."""
    _infer_sbox_width(sbox)
    inverse = [0] * len(sbox)
    for x, y in enumerate(sbox):
        inverse[y] = x
    return inverse


def substitute(
    x: int,
    sbox: Sequence[int],
    width: int,
    chunks: int | None = None,
) -> int:
    """Apply an S-box independently to fixed-width chunks of ``x``.

    ``chunks`` should be supplied for block-cipher operations so leading zero
    chunks are retained.  Automatic inference is convenient for tiny examples.
    """
    actual_width = _infer_sbox_width(sbox)
    if width != actual_width:
        raise ValueError(f"width={width} does not match this {actual_width}-bit S-box")
    if x < 0:
        raise ValueError("x must be non-negative")
    if chunks is None:
        chunks = max(1, (x.bit_length() + width - 1) // width)
    if chunks <= 0 or x >= 1 << (chunks * width):
        raise ValueError("x does not fit in the requested number of chunks")

    chunk_mask = (1 << width) - 1
    result = 0
    for shift in range(chunks - 1, -1, -1):
        result = (result << width) | sbox[(x >> (shift * width)) & chunk_mask]
    return result


def _validate_pbox(pbox: Sequence[int], width: int) -> None:
    if len(pbox) != width or sorted(pbox) != list(range(width)):
        raise ValueError("P-box must be a permutation of range(width)")


def permute(x: int, pbox: Sequence[int], width: int) -> int:
    """Permute a word where output bit ``i`` receives input bit ``pbox[i]``.

    Both positions use zero-based, MSB-first indexing.
    """
    _validate_pbox(pbox, width)
    if not 0 <= x < 1 << width:
        raise ValueError("x must fit within width bits")
    result = 0
    for source_position in pbox:
        result = (result << 1) | get_bit_msb(x, source_position, width)
    return result


def inverse_pbox(pbox: Sequence[int]) -> list[int]:
    """Return the inverse permutation for the convention used by ``permute``."""
    _validate_pbox(pbox, len(pbox))
    inverse = [0] * len(pbox)
    for output_position, input_position in enumerate(pbox):
        inverse[input_position] = output_position
    return inverse


def propagate_mask_backwards(output_mask: int, pbox: Sequence[int]) -> int:
    """Move a mask backwards through a P-box.

    If ``y = permute(x, pbox, n)``, the returned mask ``input_mask`` obeys
    ``dot(y, output_mask) == dot(x, input_mask)`` for every ``x``.
    """
    return permute(output_mask, inverse_pbox(pbox), len(pbox))


# ---------------------------------------------------------------------------
# LAT, Walsh, bias, and correlation
# ---------------------------------------------------------------------------


def count_matches(alpha: int, beta: int, sbox: Sequence[int], width: int) -> int:
    """Count inputs satisfying ``alpha·x == beta·S(x)``."""
    if _infer_sbox_width(sbox) != width:
        raise ValueError("width does not match S-box size")
    size = 1 << width
    if not 0 <= alpha < size or not 0 <= beta < size:
        raise ValueError("masks must fit within width bits")
    return sum(dot(x, alpha) == dot(sbox[x], beta) for x in range(size))


def linear_approximation_table(sbox: Sequence[int], width: int) -> list[list[int]]:
    """Return the LAT using centered match counts.

    ``LAT[a][b] = #matches(a,b) - 2**(width-1)``.  This convention has
    integer entries and is exactly half the Walsh coefficient.
    """
    if _infer_sbox_width(sbox) != width:
        raise ValueError("width does not match S-box size")
    size = 1 << width
    center = size // 2
    return [
        [count_matches(a, b, sbox, width) - center for b in range(size)]
        for a in range(size)
    ]


def walsh_coefficient(alpha: int, beta: int, sbox: Sequence[int], width: int) -> int:
    """Return ``sum_x (-1)**(alpha·x XOR beta·S(x))``."""
    return 2 * (count_matches(alpha, beta, sbox, width) - (1 << (width - 1)))


def approximation_bias(alpha: int, beta: int, sbox: Sequence[int], width: int) -> float:
    """Return ``Pr[alpha·x = beta·S(x)] - 1/2``."""
    return (count_matches(alpha, beta, sbox, width) / (1 << width)) - 0.5


def approximation_correlation(
    alpha: int, beta: int, sbox: Sequence[int], width: int
) -> float:
    """Return the normalized correlation, which equals twice the bias."""
    return walsh_coefficient(alpha, beta, sbox, width) / (1 << width)


def sbox_linearity(sbox: Sequence[int]) -> int:
    """Return the largest absolute non-trivial Walsh coefficient."""
    width = _infer_sbox_width(sbox)
    size = 1 << width
    return max(
        abs(walsh_coefficient(a, b, sbox, width))
        for a in range(size)
        for b in range(size)
        if (a, b) != (0, 0)
    )


def sbox_nonlinearity(sbox: Sequence[int]) -> int:
    """Return vectorial nonlinearity: ``2**(n-1) - linearity/2``."""
    width = _infer_sbox_width(sbox)
    return (1 << (width - 1)) - sbox_linearity(sbox) // 2


def format_lat(table: Sequence[Sequence[int]]) -> str:
    """Format a square LAT as an aligned, dependency-free text table."""
    size = len(table)
    if size == 0 or any(len(row) != size for row in table):
        raise ValueError("table must be a non-empty square matrix")
    mask_width = max(1, (size - 1).bit_length() // 4 + bool((size - 1).bit_length() % 4))
    value_width = max(2, max(len(str(value)) for row in table for value in row))
    head = " " * (mask_width + 2) + " ".join(f"{b:>{value_width}X}" for b in range(size))
    rows = [head]
    rows.extend(
        f"{a:0{mask_width}X}: " + " ".join(f"{value:>{value_width}d}" for value in row)
        for a, row in enumerate(table)
    )
    return "\n".join(rows)


def piling_up_bias(biases: Iterable[float]) -> float:
    """Combine independent Boolean-expression biases.

    For ``r`` independent expressions, ``epsilon = 2**(r-1) * product(epsilon_i)``.
    Independence is an assumption of the lemma, not something this function can
    establish for a cipher trail.
    """
    values = list(biases)
    if not values:
        raise ValueError("at least one bias is required")
    product = 1.0
    for value in values:
        if not -0.5 <= value <= 0.5:
            raise ValueError("each bias must lie in [-0.5, 0.5]")
        product *= value
    return (2 ** (len(values) - 1)) * product


def pilling_up_lemma(eps_list: Iterable[float]) -> float:
    """Backward-compatible alias for the formerly misspelled function name."""
    return piling_up_bias(eps_list)


def estimate_data_complexity(bias: float, constant: float = 1.0) -> int:
    """Return the heuristic ``ceil(constant / bias**2)``.

    The constant depends on the desired success probability, number of guessed
    keys, decision rule, and whether an author parameterizes by bias or
    correlation.  Therefore this is an order-of-growth estimate, not a promise.
    """
    if bias == 0 or not -0.5 <= bias <= 0.5:
        raise ValueError("bias must be non-zero and lie in [-0.5, 0.5]")
    if constant <= 0:
        raise ValueError("constant must be positive")
    return ceil(constant / (bias * bias))


# ---------------------------------------------------------------------------
# Matsui's Algorithm 1 and Algorithm 2
# ---------------------------------------------------------------------------


def _validate_pairs(messages: Sequence[int], ciphertexts: Sequence[int]) -> None:
    if len(messages) != len(ciphertexts):
        raise ValueError("messages and ciphertexts must have equal length")
    if not messages:
        raise ValueError("at least one plaintext-ciphertext pair is required")


@dataclass(frozen=True)
class Matsui1Result:
    """Counters and recovered key-parity bit from Algorithm 1."""

    key_parity: int
    t0: int
    t1: int

    @property
    def signed_score(self) -> int:
        """Return ``T0 - T1``."""
        return self.t0 - self.t1


def matsui1_details(
    messages: Sequence[int],
    ciphertexts: Sequence[int],
    alpha: int,
    beta: int,
    correlation_sign: int = 1,
) -> Matsui1Result:
    """Recover one parity of key material using Matsui's Algorithm 1.

    ``correlation_sign`` is the sign of the keyless approximation.  A negative
    sign complements the majority decision.  A tie is reported as an error
    because the supplied data contains no preference.
    """
    _validate_pairs(messages, ciphertexts)
    if correlation_sign not in (-1, 1):
        raise ValueError("correlation_sign must be -1 or +1")
    t0 = sum(dot(m, alpha) ^ dot(c, beta) == 0 for m, c in zip(messages, ciphertexts))
    t1 = len(messages) - t0
    if t0 == t1:
        raise ValueError("the statistic is tied; more independent data is needed")
    majority = 0 if t0 > t1 else 1
    key_parity = majority if correlation_sign > 0 else majority ^ 1
    return Matsui1Result(key_parity, t0, t1)


def matsui1(
    messages: Sequence[int],
    ciphertexts: Sequence[int],
    alpha: int,
    beta: int,
    correlation_sign: int = 1,
) -> int:
    """Compatibility wrapper returning only Algorithm 1's parity decision."""
    return matsui1_details(messages, ciphertexts, alpha, beta, correlation_sign).key_parity


def matsui2(
    messages: Sequence[int],
    ciphertexts: Sequence[int],
    alpha: int,
    beta: int,
    sbox_inverse: Sequence[int],
    key_bits: int = 4,
) -> list[int]:
    """Score final-round subkey guesses for a one-S-box last round.

    For guess ``k``, compute ``u = S^-1(c XOR k)`` and return the signed
    statistic ``T0 - T1`` for ``alpha·m == beta·u``.  Unless the relevant key
    parity and correlation sign are already known, rank guesses by magnitude.
    """
    _validate_pairs(messages, ciphertexts)
    width = _infer_sbox_width(sbox_inverse)
    if key_bits != width:
        raise ValueError("this helper guesses exactly one complete S-box subkey")
    scores: list[int] = []
    for guess in range(1 << key_bits):
        t0 = 0
        for message, ciphertext in zip(messages, ciphertexts):
            partial = sbox_inverse[ciphertext ^ guess]
            t0 += dot(message, alpha) == dot(partial, beta)
        scores.append(2 * t0 - len(messages))
    return scores


def rank_key_guesses(scores: Sequence[int]) -> list[int]:
    """Return candidate indices ordered by descending absolute score."""
    return sorted(range(len(scores)), key=lambda key: (-abs(scores[key]), key))


def _guess_to_round_key_mask(guess: int, nibble_shifts: Sequence[int]) -> int:
    """Map packed guessed nibbles to their positions in a round key."""
    mask = 0
    count = len(nibble_shifts)
    for index, shift in enumerate(nibble_shifts):
        nibble = (guess >> (4 * (count - 1 - index))) & 0xF
        mask |= nibble << shift
    return mask


def extract_round_key_nibbles(round_key: int, nibble_shifts: Sequence[int]) -> int:
    """Pack selected round-key nibbles in the same order used by the attack."""
    packed = 0
    for shift in nibble_shifts:
        packed = (packed << 4) | ((round_key >> shift) & 0xF)
    return packed


def matsui2_spn(
    messages: Sequence[int],
    ciphertexts: Sequence[int],
    alpha: int,
    beta: int,
    sbox_inverse: Sequence[int],
    nibble_shifts: Sequence[int] = (8, 0),
    block_size: int = 16,
) -> list[int]:
    """Score guesses for selected nibbles of an SPN's final whitening key.

    The default attacks the second and fourth nibbles of the 16-bit teaching
    SPN, matching ``beta = 0x0505``.  Other nibbles are irrelevant only when
    ``beta`` is zero on them.
    """
    _validate_pairs(messages, ciphertexts)
    if block_size % 4:
        raise ValueError("block_size must be a multiple of four")
    if not nibble_shifts:
        raise ValueError("at least one nibble shift is required")
    if len(set(nibble_shifts)) != len(nibble_shifts):
        raise ValueError("nibble shifts must be distinct")
    for shift in nibble_shifts:
        if shift % 4 or not 0 <= shift <= block_size - 4:
            raise ValueError("nibble shifts must be aligned positions in the block")

    attacked_mask = sum(0xF << shift for shift in nibble_shifts)
    if beta & ~attacked_mask:
        raise ValueError("beta selects a nibble whose key is not being guessed")

    chunks = block_size // 4
    scores: list[int] = []
    for guess in range(1 << (4 * len(nibble_shifts))):
        key_mask = _guess_to_round_key_mask(guess, nibble_shifts)
        t0 = 0
        for message, ciphertext in zip(messages, ciphertexts):
            before_last_sbox = substitute(
                ciphertext ^ key_mask, sbox_inverse, 4, chunks
            )
            t0 += dot(message, alpha) == dot(before_last_sbox, beta)
        scores.append(2 * t0 - len(messages))
    return scores


def matsui2_big(
    M_list: Sequence[int],
    C_list: Sequence[int],
    alpha: int,
    beta: int,
    S_inv: Sequence[int],
    key_bits: int = 8,
    sbox_input_size: int = 4,
    block_size: int = 16,
) -> list[int]:
    """Compatibility wrapper for the original two-nibble SPN example."""
    if key_bits != 8 or sbox_input_size != 4:
        raise ValueError("the teaching example guesses two 4-bit nibbles")
    return matsui2_spn(M_list, C_list, alpha, beta, S_inv, (8, 0), block_size)


# ---------------------------------------------------------------------------
# Four-round 16-bit teaching SPN
# ---------------------------------------------------------------------------


class SPN:
    """Four-round 16-bit SPN used in standard linear-cryptanalysis tutorials.

    Three rounds contain AddKey, four parallel S-boxes, and a P-box.  The last
    round contains AddKey, S-boxes, and final whitening.  Five overlapping
    16-bit round keys are extracted from a 32-bit master key at offsets
    16, 12, 8, 4, and 0.
    """

    def __init__(
        self,
        sbox: Sequence[int],
        pbox: Sequence[int],
        block_size: int = 16,
        sbox_input_size: int = 4,
    ) -> None:
        if block_size != 16 or sbox_input_size != 4:
            raise ValueError("this teaching SPN is defined for 16-bit blocks and 4-bit S-boxes")
        if _infer_sbox_width(sbox) != sbox_input_size:
            raise ValueError("S-box size does not match sbox_input_size")
        _validate_pbox(pbox, block_size)
        self.sbox = list(sbox)
        self.sbox_inv = inverse_sbox(sbox)
        self.pbox = list(pbox)
        self.pbox_inv = inverse_pbox(pbox)
        self.block_size = block_size
        self.l = sbox_input_size

    def key_schedule(self, master_key: int) -> list[int]:
        """Return five overlapping 16-bit round keys from a 32-bit key."""
        if not 0 <= master_key < 1 << 32:
            raise ValueError("master_key must be a 32-bit non-negative integer")
        return [(master_key >> shift) & 0xFFFF for shift in (16, 12, 8, 4, 0)]

    def encrypt(self, message: int, master_key: int) -> int:
        """Encrypt one 16-bit block."""
        if not 0 <= message < 1 << self.block_size:
            raise ValueError("message must be a 16-bit integer")
        round_keys = self.key_schedule(master_key)
        state = message
        for round_key in round_keys[:3]:
            state ^= round_key
            state = substitute(state, self.sbox, self.l, 4)
            state = permute(state, self.pbox, self.block_size)
        state ^= round_keys[3]
        state = substitute(state, self.sbox, self.l, 4)
        return state ^ round_keys[4]

    def decrypt(self, ciphertext: int, master_key: int) -> int:
        """Decrypt one 16-bit block."""
        if not 0 <= ciphertext < 1 << self.block_size:
            raise ValueError("ciphertext must be a 16-bit integer")
        round_keys = self.key_schedule(master_key)
        state = ciphertext ^ round_keys[4]
        state = substitute(state, self.sbox_inv, self.l, 4)
        state ^= round_keys[3]
        for round_key in reversed(round_keys[:3]):
            state = permute(state, self.pbox_inv, self.block_size)
            state = substitute(state, self.sbox_inv, self.l, 4)
            state ^= round_key
        return state


# ---------------------------------------------------------------------------
# Deterministic demonstrations
# ---------------------------------------------------------------------------


def demo_matsui1() -> Matsui1Result:
    """Run Algorithm 1 over the complete 4-bit codebook."""
    key = 0xA
    alpha, beta = 0x9, 0x1
    messages = list(range(16))
    ciphertexts = [PRESENT_SBOX[m ^ key] for m in messages]
    result = matsui1_details(messages, ciphertexts, alpha, beta, correlation_sign=1)
    assert result.key_parity == dot(key, alpha)
    return result


def demo_spn_partial_attack(sample_count: int = 8_192) -> tuple[int, int, int]:
    """Return ``(best_guess, actual_guess, actual_rank)`` for the toy SPN."""
    if not 1 <= sample_count <= 1 << 16:
        raise ValueError("sample_count must be between 1 and 65536")
    cipher = SPN(TOY_SPN_SBOX, TOY_SPN_PBOX)
    master_key = 0x3A94D63F
    rng = Random(0xC0DEC0DE)
    messages = rng.sample(range(1 << 16), sample_count)
    ciphertexts = [cipher.encrypt(m, master_key) for m in messages]
    scores = matsui2_spn(
        messages,
        ciphertexts,
        alpha=0x0B00,
        beta=0x0505,
        sbox_inverse=cipher.sbox_inv,
        nibble_shifts=(8, 0),
    )
    ranking = rank_key_guesses(scores)
    actual = extract_round_key_nibbles(cipher.key_schedule(master_key)[-1], (8, 0))
    return ranking[0], actual, ranking.index(actual) + 1


def main() -> None:
    """Print concise, reproducible checks used by the written chapter."""
    lat = linear_approximation_table(PRESENT_SBOX, 4)
    print("PRESENT S-box LAT (centered match counts):")
    print(format_lat(lat))
    print(f"\nLAT[9][1] = {lat[9][1]} (bias +0.25, correlation +0.50)")
    print(f"LAT[1][5] = {lat[1][5]} (bias -0.25, correlation -0.50)")

    result = demo_matsui1()
    print(
        "\nAlgorithm 1 complete-codebook check: "
        f"T0={result.t0}, T1={result.t1}, recovered parity={result.key_parity}"
    )

    best, actual, rank = demo_spn_partial_attack()
    print(
        "SPN partial last-round attack: "
        f"best={best:02X}, actual={actual:02X}, actual rank={rank}"
    )


if __name__ == "__main__":
    main()
