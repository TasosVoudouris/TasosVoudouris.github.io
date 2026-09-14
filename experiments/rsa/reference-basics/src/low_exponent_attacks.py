"""Exact-root and Håstad broadcast demonstrations for textbook RSA.

All inputs are synthetic. Correctly encoded RSA-OAEP ciphertexts do not satisfy
the identical-representative assumptions used here.
"""

from math import gcd, prod


def integer_nth_root(value: int, degree: int) -> tuple[int, bool]:
    """Return (floor(value ** (1/degree)), is_exact) using integer arithmetic."""

    if value < 0:
        raise ValueError("value must be nonnegative")
    if degree < 2:
        raise ValueError("degree must be at least two")

    lower, upper = 0, 1
    while upper**degree <= value:
        lower, upper = upper, upper * 2

    while lower + 1 < upper:
        middle = (lower + upper) // 2
        if middle**degree <= value:
            lower = middle
        else:
            upper = middle

    return lower, lower**degree == value


def recover_unreduced(ciphertext: int, exponent: int) -> int:
    """Recover m when a textbook ciphertext is the ordinary integer m**e."""

    root, exact = integer_nth_root(ciphertext, exponent)
    if not exact:
        raise ValueError("ciphertext is not an exact integer power")
    return root


def chinese_remainder(residues: list[int], moduli: list[int]) -> int:
    """Return the canonical CRT solution for pairwise-coprime moduli."""

    if not residues or len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same nonzero length")
    for index, modulus in enumerate(moduli):
        if modulus <= 1:
            raise ValueError("every modulus must be greater than one")
        if not 0 <= residues[index] < modulus:
            raise ValueError("each residue must satisfy 0 <= residue < modulus")
        for previous in moduli[:index]:
            if gcd(modulus, previous) != 1:
                raise ValueError("CRT moduli must be pairwise coprime")

    combined_modulus = prod(moduli)
    result = 0
    for residue, modulus in zip(residues, moduli):
        partial = combined_modulus // modulus
        result += residue * partial * pow(partial, -1, modulus)
    return result % combined_modulus


def hastad_broadcast(
    ciphertexts: list[int], moduli: list[int], exponent: int
) -> int:
    """Recover one raw representative broadcast under a small exponent."""

    if exponent < 2:
        raise ValueError("exponent must be at least two")
    if len(ciphertexts) < exponent:
        raise ValueError("the canonical attack requires at least e ciphertexts")

    raised_message = chinese_remainder(ciphertexts, moduli)
    message, exact = integer_nth_root(raised_message, exponent)
    if not exact:
        raise ValueError(
            "CRT result is not an exact e-th power; the attack assumptions failed"
        )
    return message


def main() -> None:
    """Run deterministic exact-root and broadcast examples."""

    small_message = 1234
    unreduced_ciphertext = small_message**3
    print("exact-root recovery:", recover_unreduced(unreduced_ciphertext, 3))

    message = 123
    exponent = 3
    moduli = [101 * 107, 113 * 131, 137 * 149]
    ciphertexts = [pow(message, exponent, modulus) for modulus in moduli]
    print("broadcast recovery:", hastad_broadcast(ciphertexts, moduli, exponent))


if __name__ == "__main__":
    main()
