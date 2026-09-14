"""
RSA Deep Dive II — Common-Modulus Attack.

Educational toy only.

Scenario:
    Same RSA modulus N.
    Same textbook message representative m.
    Two different coprime public exponents e1 and e2.

Given only:
    N, e1, e2, c1, c2

we use Extended Euclid / Bezout coefficients to recover m.

This is a local arithmetic demonstration, not a production attack tool.
"""

from math import gcd


def xgcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) such that a*x + b*y = g = gcd(a,b)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    return old_r, old_s, old_t


def shift_bezout_solution(
    a0: int,
    b0: int,
    e1: int,
    e2: int,
    k: int,
) -> tuple[int, int]:
    """
    If a0*e1 + b0*e2 = 1, then every pair

        a = a0 + k*e2
        b = b0 - k*e1

    is also a valid Bezout solution.
    """
    return a0 + k * e2, b0 - k * e1


def pow_signed(base: int, exponent: int, modulus: int) -> int:
    """
    Modular exponentiation supporting negative exponents.

    Negative exponents require the base to be invertible modulo the modulus.
    """
    if exponent >= 0:
        return pow(base, exponent, modulus)

    inverse = pow(base, -1, modulus)
    return pow(inverse, -exponent, modulus)


def common_modulus_recover(
    n: int,
    e1: int,
    e2: int,
    c1: int,
    c2: int,
) -> tuple[int, int, int]:
    """
    Recover the same textbook RSA message when gcd(e1,e2)=1.

    Returns:
        (message, bezout_a, bezout_b)
    """
    g, a, b = xgcd(e1, e2)

    if g != 1:
        raise ValueError(
            f"simple attack needs gcd(e1,e2)=1, got {g}"
        )

    part1 = pow_signed(c1, a, n)
    part2 = pow_signed(c2, b, n)

    return (part1 * part2) % n, a, b


def heading(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


# Checked example retained from the user's mature RSA lesson.
N = 77
MESSAGE = 9
E1 = 7
E2 = 11

C1 = pow(MESSAGE, E1, N)
C2 = pow(MESSAGE, E2, N)


heading("Public observations")

print("N  =", N)
print("m  =", MESSAGE, "(hidden from attacker)")
print("e1 =", E1)
print("e2 =", E2)
print("c1 =", C1)
print("c2 =", C2)

assert C1 == 37
assert C2 == 53


heading("Extended Euclid on the public exponents")

g, a0, b0 = xgcd(E1, E2)

print("gcd(e1,e2) =", g)
print("xgcd returned:")
print("a0 =", a0)
print("b0 =", b0)
print(f"{a0}*{E1} + ({b0})*{E2} =", a0 * E1 + b0 * E2)

assert g == 1
assert a0 * E1 + b0 * E2 == 1

# Match the convenient coefficients used in the article/older checked notes.
a, b = shift_bezout_solution(a0, b0, E1, E2, k=1)

print()
print("Shift to another valid Bezout pair:")
print("a =", a)
print("b =", b)
print(f"{a}*{E1} + ({b})*{E2} =", a * E1 + b * E2)

assert (a, b) == (8, -5)
assert a * E1 + b * E2 == 1


heading("Handle the negative exponent")

print("gcd(c2,N) =", gcd(C2, N))

c2_inverse = pow(C2, -1, N)

print("c2^(-1) mod N =", c2_inverse)

assert gcd(C2, N) == 1
assert c2_inverse == 16


heading("Recover the plaintext using the (8,-5) pair")

part1 = pow_signed(C1, a, N)
part2 = pow_signed(C2, b, N)
recovered = (part1 * part2) % N

print("c1^8 mod N       =", part1)
print("c2^(-5) mod N    =", part2)
print("recovered message =", recovered)
print("original message  =", MESSAGE)

assert part1 == 53
assert part2 == 67
assert recovered == MESSAGE


heading("The generic recovery helper also works")

recovered_generic, ga, gb = common_modulus_recover(
    N, E1, E2, C1, C2
)

print("generic xgcd coefficients =", (ga, gb))
print("generic recovered message =", recovered_generic)

assert recovered_generic == MESSAGE


heading("Why gcd(e1,e2)=1 matters")

bad_e1 = 6
bad_e2 = 10
bad_g = gcd(bad_e1, bad_e2)

print("example exponents:", bad_e1, bad_e2)
print("gcd =", bad_g)
print("Bezout can synthesize exponent", bad_g, "rather than exponent 1.")

assert bad_g == 2

print()
print("Recovered m using only N, e1, e2, c1, c2.")
print("No factorization and no private exponent were used.")
