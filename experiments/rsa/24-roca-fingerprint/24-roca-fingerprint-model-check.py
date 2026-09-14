"""
ROCA scientific fingerprint model-check.

Fixed toy values only.

This script demonstrates:
- primorial M,
- subgroup <65537> modulo M,
- fixed structured primes of the ROCA-style algebraic form,
- inheritance of the subgroup fingerprint by N = p*q,
- one fixed unrelated comparison modulus outside the subgroup.

It does not implement generic RSA factorization, dataset scanning, or a
production ROCA detector.
"""

from math import gcd

M = 30030
G = 65537

# Fixed structured toy parameters.
A = 1
B_EXP = 5
K = 11
L = 11

P = 335807
Q = 338777

# Fixed comparison primes.
P2 = 330017
Q2 = 342449


def phi(n):
    result = n
    x = n
    p = 2

    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            result -= result // p
        p += 1

    if x > 1:
        result -= result // x

    return result


def multiplicative_order(g, modulus):
    if gcd(g, modulus) != 1:
        raise ValueError("g must be a unit modulo modulus")

    x = 1
    for order in range(1, phi(modulus) + 1):
        x = (x * g) % modulus
        if x == 1:
            return order

    raise RuntimeError("order not found")


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2

    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2

    return True


def subgroup(g, modulus):
    order = multiplicative_order(g, modulus)
    return [pow(g, i, modulus) for i in range(order)]


def main():
    print("=" * 82)
    print("ROCA subgroup-fingerprint scientific model check")
    print("=" * 82)

    order = multiplicative_order(G, M)
    H = subgroup(G, M)
    units = phi(M)

    print(f"M                  = {M}")
    print(f"g                  = {G}")
    print(f"g mod M            = {G % M}")
    print(f"phi(M)             = {units}")
    print(f"ord_M(g)           = {order}")
    print(f"|<g>| / phi(M)     = {order}/{units}")
    print()
    print("subgroup residues:")
    print(H)

    assert order == 12
    assert len(H) == 12
    assert len(set(H)) == 12

    rp = pow(G, A, M)
    rq = pow(G, B_EXP, M)

    p_constructed = K * M + rp
    q_constructed = L * M + rq

    print()
    print("=" * 82)
    print("Structured toy primes")
    print("=" * 82)
    print(f"a                  = {A}")
    print(f"k                  = {K}")
    print(f"g^a mod M          = {rp}")
    print(f"k*M + residue      = {p_constructed}")
    print(f"p prime?           = {is_prime(p_constructed)}")
    print()
    print(f"b                  = {B_EXP}")
    print(f"l                  = {L}")
    print(f"g^b mod M          = {rq}")
    print(f"l*M + residue      = {q_constructed}")
    print(f"q prime?           = {is_prime(q_constructed)}")

    assert p_constructed == P
    assert q_constructed == Q
    assert is_prime(P)
    assert is_prime(Q)

    N = P * Q
    expected_residue = pow(G, A + B_EXP, M)
    actual_residue = N % M

    print()
    print("=" * 82)
    print("Public modulus fingerprint")
    print("=" * 82)
    print(f"N = p*q            = {N}")
    print(f"N mod M            = {actual_residue}")
    print(f"g^(a+b) mod M      = {expected_residue}")
    print(f"residue in <g>?    = {actual_residue in set(H)}")

    assert actual_residue == expected_residue
    assert actual_residue in set(H)

    N2 = P2 * Q2
    comparison_residue = N2 % M

    print()
    print("=" * 82)
    print("Fixed comparison modulus")
    print("=" * 82)
    print(f"p2                 = {P2}")
    print(f"q2                 = {Q2}")
    print(f"p2 prime?          = {is_prime(P2)}")
    print(f"q2 prime?          = {is_prime(Q2)}")
    print(f"N2                 = {N2}")
    print(f"N2 mod M           = {comparison_residue}")
    print(f"residue in <g>?    = {comparison_residue in set(H)}")

    assert is_prime(P2)
    assert is_prime(Q2)
    assert comparison_residue not in set(H)

    print()
    print("All toy fingerprint identities verified.")
    print("No RSA factorization or external key scanning was performed.")


if __name__ == "__main__":
    main()
