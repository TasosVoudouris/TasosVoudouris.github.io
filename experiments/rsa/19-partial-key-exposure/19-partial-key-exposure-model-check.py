"""
Scientific model check for the partial-factor-exposure formulation.

This is not a generic factor-recovery implementation.
It verifies one fixed toy instance used in the accompanying article.
"""

from math import isqrt

P = 60013
Q = 61027
KNOWN_HIGH_BITS = 9


def main():
    N = P * Q

    p_bits = P.bit_length()
    q_bits = Q.bit_length()
    n_bits = N.bit_length()

    unknown_bits = p_bits - KNOWN_HIGH_BITS
    prefix = P >> unknown_bits
    p0 = prefix << unknown_bits
    x0 = P - p0

    print("=" * 78)
    print("Partial RSA factor exposure — scientific model check")
    print("=" * 78)
    print(f"p                  = {P}")
    print(f"q                  = {Q}")
    print(f"N                  = {N}")
    print(f"bit_length(N)      = {n_bits}")
    print(f"bit_length(p)      = {p_bits}")
    print(f"bit_length(q)      = {q_bits}")
    print()
    print(f"p in binary        = {P:0{p_bits}b}")
    print(f"known prefix bits  = {prefix:0{KNOWN_HIGH_BITS}b}")
    print(f"unknown low bits   = {unknown_bits}")
    print(f"p0                 = {p0}")
    print(f"x0                 = {x0}")
    print(f"p0 + x0            = {p0 + x0}")

    assert p0 + x0 == P
    assert 0 <= x0 < (1 << unknown_bits)

    f_x0 = p0 + x0

    print()
    print("Polynomial model")
    print(f"f(x)               = {p0} + x")
    print(f"f(x0)              = {f_x0}")
    print(f"f(x0) mod p        = {f_x0 % P}")
    print(f"N mod p            = {N % P}")

    assert f_x0 == P
    assert f_x0 % P == 0
    assert N % P == 0

    quarter_scale = N ** 0.25

    print()
    print("Small-root scale")
    print(f"N^(1/4)            = {quarter_scale:.6f}")
    print(f"x0                 = {x0}")
    print(f"x0 < N^(1/4)?      = {x0 < quarter_scale}")

    assert x0 < quarter_scale

    recovered_p = p0 + x0
    recovered_q = N // recovered_p

    print()
    print("Exact reconstruction once the mathematical root is supplied")
    print(f"recovered p        = {recovered_p}")
    print(f"recovered q        = {recovered_q}")
    print(f"recovered p*q      = {recovered_p * recovered_q}")

    assert recovered_p == P
    assert recovered_q == Q
    assert recovered_p * recovered_q == N

    print()
    print("All model identities verified.")


if __name__ == "__main__":
    main()
