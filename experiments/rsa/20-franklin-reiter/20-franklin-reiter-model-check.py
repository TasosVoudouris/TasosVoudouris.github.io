"""
Franklin-Reiter scientific model check.

Fixed toy arithmetic only.

Implements polynomial Euclid over Z_N[X] carefully enough to expose the
composite-ring issue: a leading coefficient may be non-invertible modulo N.
"""

from math import gcd

P = 30011
Q = 35027
N = P * Q
E = 3

M = 12037
OFFSET = 1
M2 = M + OFFSET

C1 = pow(M, E, N)
C2 = pow(M2, E, N)


def trim(poly):
    poly = [c % N for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_add(a, b):
    out = [0] * max(len(a), len(b))
    for i, c in enumerate(a):
        out[i] = (out[i] + c) % N
    for i, c in enumerate(b):
        out[i] = (out[i] + c) % N
    return trim(out)


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


def poly_eval(poly, x):
    result = 0
    for c in reversed(poly):
        result = (result * x + c) % N
    return result


def poly_scale(poly, scalar):
    return trim([(scalar * c) % N for c in poly])


def poly_divmod(numer, denom):
    numer = trim(numer[:])
    denom = trim(denom[:])

    if denom == [0]:
        raise ZeroDivisionError("polynomial division by zero")

    leading = denom[-1]
    g = gcd(leading, N)

    if g != 1:
        raise ArithmeticError(
            f"leading coefficient {leading} is not a unit modulo N; "
            f"gcd(leading, N) = {g}"
        )

    leading_inv = pow(leading, -1, N)

    if len(numer) < len(denom):
        return [0], numer

    quotient = [0] * (len(numer) - len(denom) + 1)

    while numer != [0] and len(numer) >= len(denom):
        shift = len(numer) - len(denom)
        coeff = numer[-1] * leading_inv % N
        quotient[shift] = coeff

        term = [0] * shift + poly_scale(denom, coeff)
        numer = poly_sub(numer, term)

    return trim(quotient), trim(numer)


def monic(poly):
    poly = trim(poly)
    if poly == [0]:
        return poly

    leading = poly[-1]
    g = gcd(leading, N)
    if g != 1:
        raise ArithmeticError(
            f"cannot normalize: leading coefficient {leading} is not a unit; "
            f"gcd = {g}"
        )

    return poly_scale(poly, pow(leading, -1, N))


def poly_gcd(a, b, trace=False):
    a = trim(a)
    b = trim(b)
    step = 0

    while b != [0]:
        q, r = poly_divmod(a, b)

        if trace:
            print(f"step {step}")
            print("  A =", a)
            print("  B =", b)
            print("  Q =", q)
            print("  R =", r)

        a, b = b, r
        step += 1

    return monic(a)


def main():
    print("=" * 82)
    print("Franklin-Reiter scientific model check")
    print("=" * 82)

    print(f"p    = {P}")
    print(f"q    = {Q}")
    print(f"N    = {N}")
    print(f"e    = {E}")
    print()
    print(f"m1   = {M}")
    print(f"m2   = {M2}")
    print(f"c1   = {C1}")
    print(f"c2   = {C2}")

    # g1(X) = X^3 - c1
    g1 = trim([-C1, 0, 0, 1])

    # g2(X) = (X+1)^3 - c2
    g2 = poly_sub(poly_pow([OFFSET, 1], E), [C2])

    print()
    print("Polynomials, low-to-high coefficient order")
    print("g1 =", g1)
    print("g2 =", g2)

    print()
    print("Shared-root checks")
    print("g1(m) mod N =", poly_eval(g1, M))
    print("g2(m) mod N =", poly_eval(g2, M))

    assert poly_eval(g1, M) == 0
    assert poly_eval(g2, M) == 0

    print()
    print("Polynomial Euclidean algorithm")
    G = poly_gcd(g1, g2, trace=True)

    print()
    print("monic gcd =", G)

    expected = [(-M) % N, 1]
    print("expected  =", expected)

    assert G == expected

    recovered = (-G[0]) % N
    print(f"recovered m = {recovered}")
    assert recovered == M

    print()
    print("Independent hand-elimination check")
    inv3 = pow(3, -1, N)
    t = ((C2 - C1 - 1) % N) * inv3 % N
    denominator = (t + 1) % N
    denominator_gcd = gcd(denominator, N)

    print(f"t = {t}")
    print(f"m^2 + m mod N = {(M*M + M) % N}")
    print(f"gcd(t+1, N) = {denominator_gcd}")

    assert t == (M * M + M) % N
    assert denominator_gcd == 1

    recovered2 = ((C1 + t) % N) * pow(denominator, -1, N) % N
    print(f"recovered m from direct formula = {recovered2}")

    assert recovered2 == M

    print()
    print("All Franklin-Reiter model checks passed.")


if __name__ == "__main__":
    main()
