"""
Bleichenbacher interval-narrowing scientific model check.

This script uses one fixed toy RSA instance and two preselected positive
multipliers. It models only the idealized numerical prefix predicate

    2B <= m' <= 3B-1

and does NOT implement a network oracle, PKCS #1 parser, oracle discovery,
or a generic adaptive search procedure.
"""

from math import gcd, ceil, floor

P = 60013
Q = 61027
N = P * Q
E = 17
PHI = (P - 1) * (Q - 1)
D = pow(E, -1, PHI)

K_BYTES = (N.bit_length() + 7) // 8
B = 2 ** (8 * (K_BYTES - 2))
VALID_LO = 2 * B
VALID_HI = 3 * B - 1

M = 150000
C = pow(M, E, N)

S_VALUES = [24417, 195330]


def interval_predicate(plaintext_rep):
    """Idealized prefix interval only, not full PKCS #1 v1.5 conformance."""
    return VALID_LO <= plaintext_rep <= VALID_HI


def transformed_plaintext(s):
    return (M * s) % N


def transformed_ciphertext(s):
    return C * pow(s, E, N) % N


def decrypt(c):
    return pow(c, D, N)


def compatible_wraps(a, b, s):
    r_min = ceil((a * s - VALID_HI) / N)
    r_max = floor((b * s - VALID_LO) / N)
    return range(r_min, r_max + 1)


def refine(intervals, s):
    out = []

    for a, b in intervals:
        for r in compatible_wraps(a, b, s):
            lo = max(a, ceil((VALID_LO + r * N) / s))
            hi = min(b, floor((VALID_HI + r * N) / s))

            if lo <= hi:
                out.append((lo, hi, r))

    return out


def main():
    print("=" * 82)
    print("Bleichenbacher interval-narrowing scientific model check")
    print("=" * 82)

    assert gcd(E, PHI) == 1

    print(f"p              = {P}")
    print(f"q              = {Q}")
    print(f"N              = {N}")
    print(f"e              = {E}")
    print(f"k bytes        = {K_BYTES}")
    print(f"B              = {B}")
    print(f"valid interval = [{VALID_LO}, {VALID_HI}]")
    print()

    print(f"hidden toy m   = {M}")
    print(f"ciphertext c   = {C}")
    print(f"initial valid? = {interval_predicate(M)}")

    assert interval_predicate(M)

    intervals = [(VALID_LO, VALID_HI)]

    print()
    print(f"initial candidate count = {VALID_HI - VALID_LO + 1}")

    for index, s in enumerate(S_VALUES, start=1):
        c_prime = transformed_ciphertext(s)
        m_prime = decrypt(c_prime)
        direct = transformed_plaintext(s)

        assert m_prime == direct
        assert interval_predicate(m_prime)

        true_r = (M * s - m_prime) // N

        print()
        print("-" * 82)
        print(f"positive predicate #{index}")
        print(f"s                  = {s}")
        print(f"c'                 = {c_prime}")
        print(f"m*s mod N          = {m_prime}")
        print(f"wrap r             = {true_r}")
        print(f"predicate          = {interval_predicate(m_prime)}")

        refined = refine(intervals, s)

        print("compatible refined pieces:")
        for lo, hi, r in refined:
            print(f"  r={r:2d} -> [{lo}, {hi}]")

        intervals = [(lo, hi) for lo, hi, _ in refined]

        candidate_count = sum(hi - lo + 1 for lo, hi in intervals)
        print(f"candidate count    = {candidate_count}")

    print()
    print("=" * 82)
    print("final intervals")
    print("=" * 82)
    print(intervals)

    assert intervals == [(M, M)]

    print()
    print("All interval identities verified.")
    print("No adaptive multiplier search or external oracle was implemented.")


if __name__ == "__main__":
    main()
