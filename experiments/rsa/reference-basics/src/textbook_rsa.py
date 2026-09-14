"""Dependency-free textbook RSA arithmetic for study and tests.

This module intentionally omits random prime generation, OAEP, PSS, secure key
storage, side-channel defenses, and every other requirement of production RSA.
It accepts tiny, caller-supplied primes so the mathematics is reproducible.
"""

from dataclasses import dataclass
from math import gcd, isqrt, lcm


@dataclass(frozen=True)
class PublicKey:
    """The public textbook-RSA parameters."""

    n: int
    e: int


@dataclass(frozen=True)
class PrivateKey:
    """Private parameters retained to demonstrate CRT exponentiation."""

    n: int
    d: int
    p: int
    q: int


def is_prime(value: int) -> bool:
    """Return whether a small integer is prime by trial division.

    This deliberately simple helper is appropriate only for the tiny examples
    in this directory. It is not a cryptographic prime generator or validator.
    """

    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    for divisor in range(3, isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


def make_keypair(p: int, q: int, e: int = 65537) -> tuple[PublicKey, PrivateKey]:
    """Construct a toy key pair from distinct, caller-supplied primes."""

    if not is_prime(p) or not is_prime(q):
        raise ValueError("p and q must be prime")
    if p == q:
        raise ValueError("p and q must be distinct")

    modulus = p * q
    group_exponent = lcm(p - 1, q - 1)
    if not 1 < e < group_exponent:
        raise ValueError("e must satisfy 1 < e < lambda(n)")
    if gcd(e, group_exponent) != 1:
        raise ValueError("e must be coprime to lambda(n)")

    d = pow(e, -1, group_exponent)
    return PublicKey(modulus, e), PrivateKey(modulus, d, p, q)


def _check_representative(value: int, modulus: int) -> None:
    if not isinstance(value, int):
        raise TypeError("the RSA representative must be an integer")
    if not 0 <= value < modulus:
        raise ValueError("the RSA representative must satisfy 0 <= value < n")


def public_operation(value: int, key: PublicKey) -> int:
    """Apply the raw RSA public primitive to one integer representative."""

    _check_representative(value, key.n)
    return pow(value, key.e, key.n)


def private_operation(value: int, key: PrivateKey) -> int:
    """Apply the raw RSA private primitive using CRT recombination."""

    _check_representative(value, key.n)

    modulo_p = pow(value, key.d % (key.p - 1), key.p)
    modulo_q = pow(value, key.d % (key.q - 1), key.q)
    q_inverse = pow(key.q, -1, key.p)
    correction = (q_inverse * (modulo_p - modulo_q)) % key.p
    result = modulo_q + correction * key.q

    if not 0 <= result < key.n:
        raise AssertionError("CRT recombination produced an invalid representative")
    return result


def main() -> None:
    """Reproduce the small numerical example from the RSA foundations note."""

    public, private = make_keypair(p=61, q=53, e=17)
    message = 65
    ciphertext = public_operation(message, public)
    recovered = private_operation(ciphertext, private)

    print(f"public key:  n={public.n}, e={public.e}")
    print(f"private exponent: d={private.d}")
    print(f"message:      {message}")
    print(f"ciphertext:   {ciphertext}")
    print(f"recovered:    {recovered}")


if __name__ == "__main__":
    main()
