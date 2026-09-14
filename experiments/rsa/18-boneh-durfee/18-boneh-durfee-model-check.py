"""
Scientific model check for the Boneh-Durfee small-inverse formulation.

This script does NOT implement generic RSA key recovery.
It starts from fixed toy factors and an intentionally abnormal textbook
private exponent, constructs the Boneh-Durfee variables, and verifies all
algebraic identities used in the accompanying article.
"""

from math import gcd, isqrt, log


P = 30011
Q = 35027
D = 263


def main():
    N = P * Q
    phi = (P - 1) * (Q - 1)

    assert gcd(D, phi) == 1
    e = pow(D, -1, phi)

    k = (e * D - 1) // phi
    assert e * D - 1 == k * phi

    A = (N + 1) // 2
    x0 = 2 * k
    y0 = -(P + Q) // 2

    f_value = 1 + x0 * (A + y0)

    print("=" * 76)
    print("Boneh-Durfee scientific model check")
    print("=" * 76)
    print(f"p             = {P}")
    print(f"q             = {Q}")
    print(f"N             = {N}")
    print(f"phi(N)        = {phi}")
    print(f"d             = {D}")
    print(f"e             = {e}")
    print(f"k             = {k}")
    print()
    print(f"A             = {A}")
    print(f"x0 = 2k       = {x0}")
    print(f"y0            = {y0}")
    print()
    print(f"f(x0,y0)      = {f_value}")
    print(f"e*d           = {e * D}")
    print(f"f mod e       = {f_value % e}")

    assert f_value == e * D
    assert f_value % e == 0

    delta = log(D, N)
    n_quarter = N ** 0.25
    n_bd = N ** 0.292

    print()
    print("Exponent scales")
    print(f"log_N(d)      = {delta:.12f}")
    print(f"N^(1/4)       = {n_quarter:.6f}")
    print(f"N^(0.292)     = {n_bd:.6f}")
    print(f"d             = {D}")
    print(f"N^(1/4) < d?  = {n_quarter < D}")
    print(f"d < N^0.292?  = {D < n_bd}")

    S = -2 * y0
    discriminant = S * S - 4 * N
    r = isqrt(discriminant)

    print()
    print("Reconstruction from the model root")
    print(f"p+q           = {S}")
    print(f"Delta         = {discriminant}")
    print(f"sqrt(Delta)   = {r}")

    assert r * r == discriminant

    p2 = (S - r) // 2
    q2 = (S + r) // 2

    print(f"recovered p   = {p2}")
    print(f"recovered q   = {q2}")

    assert p2 * q2 == N
    assert {p2, q2} == {P, Q}

    phi2 = N - S + 1
    d2 = (1 + k * phi2) // e

    print(f"recovered phi = {phi2}")
    print(f"recovered d   = {d2}")

    assert phi2 == phi
    assert d2 == D

    print()
    print("All identities verified.")


if __name__ == "__main__":
    main()
