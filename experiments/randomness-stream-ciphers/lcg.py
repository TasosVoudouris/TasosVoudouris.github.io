"""Educational linear congruential generator and parameter recovery.

Not a CSPRNG.  The recovery routine assumes the modulus is known and that the
required modular inverse exists.
"""
from math import gcd


def lcg_step(state: int, multiplier: int, increment: int, modulus: int) -> int:
    return (multiplier * state + increment) % modulus


def recover_parameters(s0: int, s1: int, s2: int, modulus: int) -> tuple[int, int]:
    delta1 = (s1 - s0) % modulus
    delta2 = (s2 - s1) % modulus
    if gcd(delta1, modulus) != 1:
        raise ValueError("s1-s0 is not invertible modulo the modulus")
    a = (delta2 * pow(delta1, -1, modulus)) % modulus
    c = (s1 - a * s0) % modulus
    return a, c
