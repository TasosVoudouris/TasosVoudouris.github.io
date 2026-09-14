"""Demonstrate factor recovery when two RSA moduli share a prime."""

from math import gcd


def recover_shared_factor(modulus_1: int, modulus_2: int) -> int:
    """Return a nontrivial shared factor or raise when none is exposed."""

    if modulus_1 <= 1 or modulus_2 <= 1:
        raise ValueError("moduli must be greater than one")
    factor = gcd(modulus_1, modulus_2)
    if factor == 1:
        raise ValueError("the moduli do not share a factor")
    if factor in (modulus_1, modulus_2):
        raise ValueError("the moduli are equal or one divides the other")
    return factor


def main() -> None:
    """Run a deterministic toy example."""

    shared_prime = 101
    modulus_1 = shared_prime * 113
    modulus_2 = shared_prime * 127
    recovered = recover_shared_factor(modulus_1, modulus_2)

    print(f"first modulus:  {modulus_1}")
    print(f"second modulus: {modulus_2}")
    print(f"shared factor:  {recovered}")


if __name__ == "__main__":
    main()
