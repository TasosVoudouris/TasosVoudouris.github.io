"""Recover a textbook-RSA representative from a reused modulus.

The code uses synthetic values and demonstrates one specific failure. It is not
a decryption utility and does not implement RSA-OAEP.
"""

from math import gcd


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) such that ax + by = g = gcd(a, b)."""

    old_r, remainder = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while remainder:
        quotient = old_r // remainder
        old_r, remainder = remainder, old_r - quotient * remainder
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    return old_r, old_x, old_y


def signed_power(value: int, exponent: int, modulus: int) -> int:
    """Compute a modular power, interpreting a negative exponent as an inverse."""

    if exponent >= 0:
        return pow(value, exponent, modulus)
    try:
        inverse = pow(value, -1, modulus)
    except ValueError as error:
        factor = gcd(value, modulus)
        raise ValueError(
            "negative exponent requires an invertible ciphertext; "
            f"gcd(ciphertext, n)={factor}"
        ) from error
    return pow(inverse, -exponent, modulus)


def recover_plaintext(
    ciphertext_1: int,
    ciphertext_2: int,
    exponent_1: int,
    exponent_2: int,
    modulus: int,
) -> int:
    """Recover the shared representative when the public exponents are coprime."""

    if modulus <= 1:
        raise ValueError("modulus must be greater than one")
    for ciphertext in (ciphertext_1, ciphertext_2):
        if not 0 <= ciphertext < modulus:
            raise ValueError("each ciphertext must satisfy 0 <= c < n")
    if exponent_1 <= 1 or exponent_2 <= 1:
        raise ValueError("public exponents must be greater than one")

    divisor, coefficient_1, coefficient_2 = extended_gcd(
        exponent_1, exponent_2
    )
    if divisor != 1:
        raise ValueError(
            "the basic common-modulus attack requires coprime exponents"
        )

    part_1 = signed_power(ciphertext_1, coefficient_1, modulus)
    part_2 = signed_power(ciphertext_2, coefficient_2, modulus)
    return (part_1 * part_2) % modulus


def main() -> None:
    """Run a deterministic toy example."""

    modulus = 101 * 113
    message = 42
    exponent_1 = 17
    exponent_2 = 13
    ciphertext_1 = pow(message, exponent_1, modulus)
    ciphertext_2 = pow(message, exponent_2, modulus)

    recovered = recover_plaintext(
        ciphertext_1,
        ciphertext_2,
        exponent_1,
        exponent_2,
        modulus,
    )
    print(f"message:   {message}")
    print(f"recovered: {recovered}")


if __name__ == "__main__":
    main()
