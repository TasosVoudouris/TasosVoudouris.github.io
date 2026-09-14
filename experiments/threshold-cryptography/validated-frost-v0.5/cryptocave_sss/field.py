"""Very small helpers for arithmetic in a prime field.

The original archive used arithmetic modulo ``Q`` directly.  This module keeps
that style, but puts the validation and signed encoding in one place.
"""

from __future__ import annotations


def is_prime(number: int) -> bool:
    """Return ``True`` when ``number`` is prime.

    Trial division is intentionally used because the educational examples use
    small fixed moduli.  Real systems use reviewed parameter sets and do not
    generate their cryptographic fields with this function.
    """

    if number < 2:
        return False
    if number in (2, 3):
        return True
    if number % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def require_prime(modulus: int) -> None:
    """Raise ``ValueError`` unless ``modulus`` defines a prime field."""

    if not is_prime(modulus):
        raise ValueError("the modulus must be prime")


def inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of ``value`` modulo ``modulus``."""

    require_prime(modulus)
    value %= modulus
    if value == 0:
        raise ZeroDivisionError("zero has no multiplicative inverse")

    # Python's three-argument pow computes a modular inverse for exponent -1.
    return pow(value, -1, modulus)


def divide(numerator: int, denominator: int, modulus: int) -> int:
    """Compute ``numerator / denominator`` inside the prime field."""

    return (numerator % modulus) * inverse(denominator, modulus) % modulus


def encode_signed(value: int, modulus: int) -> int:
    """Encode a possibly negative integer as a field element."""

    require_prime(modulus)
    return value % modulus


def decode_signed(value: int, modulus: int) -> int:
    """Return the centered integer representative of a field element.

    For the odd primes used here, the output lies in
    ``[-(p-1)/2, (p-1)/2]``.
    """

    require_prime(modulus)
    value %= modulus
    midpoint = modulus // 2
    return value if value <= midpoint else value - modulus


def demo() -> None:
    """Run a tiny field-arithmetic lesson when this file is executed directly."""

    modulus = 41
    encoded = encode_signed(-5, modulus)
    print("Field: F_41")
    print("-5 encoded modulo 41:", encoded)
    print("36 decoded as a centered integer:", decode_signed(encoded, modulus))
    print("Inverse of 7 modulo 41:", inverse(7, modulus))
    print("Check 7 * inverse(7) mod 41:", 7 * inverse(7, modulus) % modulus)


if __name__ == "__main__":
    demo()
