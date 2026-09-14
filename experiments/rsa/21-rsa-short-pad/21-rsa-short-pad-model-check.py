"""
RSA short-pad scientific model check.

Fixed toy arithmetic only.

Verifies:
1. two short-padded representatives of one message,
2. the explicit e=3 resultant polynomial,
3. Delta as a small modular root,
4. Franklin-Reiter polynomial GCD once Delta is supplied,
5. exact recovery of the original message by removing the suffix.

This is a mathematical reproducibility script, not a generic RSA tool.
"""

from math import gcd

P = 68719476713
Q = 68719476731
N = P * Q
E = 3

PAD_BITS = 8
MESSAGE = 12345678901234567
R1 = 37
R2 = 110

M1 = (MESSAGE << PAD_BITS) + R1
M2 = (MESSAGE << PAD_BITS) + R2
DELTA = R2 - R1

C1 = pow(M1, E, N)
C2 = pow(M2, E, N)


def trim(poly):
    poly = [c % N for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_sub(a, b):
    out = [0] * max(len(a), len(b))
    for i, c in enumerate(a):
        out[i] = (out[i] + c) % N
    for i, c in enumerate(b):
        out[i] = (out[i] - c) % N
    return trim(out)


def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % N
    return trim(out)


def poly_pow(base, exponent):
    result = [1]
    base = trim(base)
    while exponent:
        if exponent & 1:
            result = poly_mul(result, base)
        base = poly_mul(base, base)
        exponent >>= 1
    return result


def poly_scale(poly, scalar):
    return trim([(scalar * c) % N for c in poly])


def poly_eval(poly, x):
    value = 0
    for c in reversed(poly):
        value = (value * x + c) % N
    return value


def poly_divmod(numer, denom):
    numer = trim(numer[:])
    denom = trim(denom[:])

    if denom == [0]:
        raise ZeroDivisionError

    lead = denom[-1]
    g = gcd(lead, N)
    if g != 1:
        raise ArithmeticError(
            f"non-unit leading coefficient {lead}; gcd with N is {g}"
        )

    inv = pow(lead, -1, N)
    quotient = [0] * max(1, len(numer) - len(denom) + 1)

    while numer != [0] and len(numer) >= len(denom):
        shift = len(numer) - len(denom)
        coeff = numer[-1] * inv % N
        quotient[shift] = coeff
        term = [0] * shift + poly_scale(denom, coeff)
        numer = poly_sub(numer, term)

    return trim(quotient), trim(numer)


def monic(poly):
    poly = trim(poly)
    lead = poly[-1]
    g = gcd(lead, N)
    if g != 1:
        raise ArithmeticError(
            f"cannot normalize non-unit leading coefficient; gcd={g}"
        )
    return poly_scale(poly, pow(lead, -1, N))


def poly_gcd(a, b):
    a = trim(a)
    b = trim(b)
    while b != [0]:
        _, r = poly_divmod(a, b)
        a, b = b, r
    return monic(a)


def resultant_e3(c1, c2):
    coeffs = [0] * 10
    coeffs[0] = pow((c1 - c2) % N, 3, N)
    coeffs[3] = 3 * (c1*c1 + 7*c1*c2 + c2*c2) % N
    coeffs[6] = 3 * (c1 - c2) % N
    coeffs[9] = 1
    return coeffs


def main():
    print("=" * 82)
    print("RSA short-pad scientific model check")
    print("=" * 82)

    phi = (P - 1) * (Q - 1)
    assert gcd(E, phi) == 1

    print(f"p              = {P}")
    print(f"q              = {Q}")
    print(f"N              = {N}")
    print(f"bit_length(N)  = {N.bit_length()}")
    print(f"e              = {E}")
    print()

    print(f"message M      = {MESSAGE}")
    print(f"pad bits       = {PAD_BITS}")
    print(f"r1             = {R1}")
    print(f"r2             = {R2}")
    print(f"M1             = {M1}")
    print(f"M2             = {M2}")
    print(f"Delta          = {DELTA}")

    assert M2 - M1 == DELTA
    assert 0 <= R1 < (1 << PAD_BITS)
    assert 0 <= R2 < (1 << PAD_BITS)

    print()
    print(f"C1             = {C1}")
    print(f"C2             = {C2}")

    root_scale = N ** (1 / 9)

    print()
    print("Small-root scale")
    print(f"N^(1/9)        = {root_scale:.12f}")
    print(f"|Delta|        = {abs(DELTA)}")
    print(f"inside bound?  = {abs(DELTA) < root_scale}")

    assert abs(DELTA) < root_scale

    h = resultant_e3(C1, C2)

    print()
    print("Resultant h(Y), low-to-high coefficients")
    print(h)
    print(f"h(Delta) mod N = {poly_eval(h, DELTA)}")

    assert poly_eval(h, DELTA) == 0

    print()
    print("Franklin-Reiter stage after Delta is known")

    g1 = trim([-C1, 0, 0, 1])
    g2 = poly_sub(poly_pow([DELTA, 1], 3), [C2])

    assert poly_eval(g1, M1) == 0
    assert poly_eval(g2, M1) == 0

    G = poly_gcd(g1, g2)
    expected = [(-M1) % N, 1]

    print(f"monic gcd       = {G}")
    print(f"expected        = {expected}")

    assert G == expected

    recovered_m1 = (-G[0]) % N
    recovered_M = recovered_m1 >> PAD_BITS
    recovered_r1 = recovered_m1 & ((1 << PAD_BITS) - 1)

    print()
    print("Exact reconstruction")
    print(f"recovered M1   = {recovered_m1}")
    print(f"recovered M    = {recovered_M}")
    print(f"recovered r1   = {recovered_r1}")

    assert recovered_m1 == M1
    assert recovered_M == MESSAGE
    assert recovered_r1 == R1

    print()
    print("All short-pad model checks passed.")


if __name__ == "__main__":
    main()
