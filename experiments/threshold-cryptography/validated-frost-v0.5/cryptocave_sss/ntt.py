"""A direct number-theoretic transform for the packed-sharing examples."""

from __future__ import annotations

from collections.abc import Sequence

if __package__:
    from .field import inverse, require_prime
else:
    from field import inverse, require_prime


def validate_root(root: int, order: int, modulus: int) -> None:
    """Check that ``root`` has exactly the requested multiplicative order."""

    require_prime(modulus)
    if order < 1 or (modulus - 1) % order != 0:
        raise ValueError("order must divide modulus - 1")
    if pow(root, order, modulus) != 1:
        raise ValueError("root^order must equal one")
    if any(pow(root, exponent, modulus) == 1 for exponent in range(1, order)):
        raise ValueError("root is not primitive for the requested order")


def ntt(values: Sequence[int], root: int, modulus: int) -> list[int]:
    """Evaluate a coefficient vector at successive powers of ``root``.

    This transparent O(n^2) version is used before introducing recursive FFT
    optimizations.  It computes the same transform as the working core of the
    original ``fft.py``.
    """

    order = len(values)
    if order == 0:
        raise ValueError("the input cannot be empty")
    validate_root(root, order, modulus)
    return [
        sum(
            coefficient * pow(root, index * degree, modulus)
            for degree, coefficient in enumerate(values)
        )
        % modulus
        for index in range(order)
    ]


def inverse_ntt(values: Sequence[int], root: int, modulus: int) -> list[int]:
    """Invert ``ntt``."""

    order = len(values)
    inverse_root = inverse(root, modulus)
    inverse_order = inverse(order, modulus)
    return [entry * inverse_order % modulus for entry in ntt(values, inverse_root, modulus)]


def demo() -> None:
    """Run an order-eight transform and its inverse."""

    coefficients = [1, 2, 3, 4, 5, 6, 7, 8]
    transformed = ntt(coefficients, root=354, modulus=433)
    recovered = inverse_ntt(transformed, root=354, modulus=433)
    print("Coefficients:", coefficients)
    print("NTT values:", transformed)
    print("Recovered coefficients:", recovered)


if __name__ == "__main__":
    demo()
