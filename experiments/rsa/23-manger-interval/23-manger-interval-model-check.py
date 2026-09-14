"""
Manger interval-narrowing scientific model check.

Fixed toy RSA values only.

This script reproduces the three mathematical phases from Manger's 2001
analysis against the idealized boundary oracle

    O(f) = [(m*f mod N) < B].

It does not implement network communication, OAEP parsing, timing analysis,
or oracle discovery.
"""

from math import gcd, ceil, floor

P = 60013
Q = 61027
N = P * Q
PHI = (P - 1) * (Q - 1)

E = 17
D = pow(E, -1, PHI)

K = (N.bit_length() + 7) // 8
B = 2 ** (8 * (K - 1))

M = 12345678
C = pow(M, E, N)


def oracle_for_multiplier(f):
    """Idealized Manger boundary predicate."""
    return (M * f) % N < B


def transformed_plaintext(f):
    return (M * f) % N


def transformed_ciphertext(f):
    return C * pow(f, E, N) % N


def decrypt(c):
    return pow(c, D, N)


def phase1():
    f1 = 2
    trace = []

    while True:
        result = oracle_for_multiplier(f1)
        trace.append((f1, transformed_plaintext(f1), result))

        if not result:
            return f1, trace

        f1 *= 2


def phase2(f1):
    half = f1 // 2

    f2 = ((N + B) // B) * half
    trace = []

    while True:
        result = oracle_for_multiplier(f2)
        trace.append((f2, transformed_plaintext(f2), result))

        if result:
            return f2, trace

        f2 += half


def phase3(f2):
    lo = ceil(N / f2)
    hi = floor((N + B - 1) / f2)

    trace = []

    while lo < hi:
        width = hi - lo

        ftmp = max(1, (2 * B) // max(1, width))
        i = (ftmp * lo) // N

        if i == 0:
            i = 1

        f3 = ceil(i * N / lo)

        reduced = transformed_plaintext(f3)
        result = reduced < B

        old_lo, old_hi = lo, hi

        if result:
            hi = min(
                hi,
                floor((i * N + B - 1) / f3),
            )
        else:
            lo = max(
                lo,
                ceil((i * N + B) / f3),
            )

        trace.append(
            {
                "f3": f3,
                "i": i,
                "oracle_lt_B": result,
                "reduced": reduced,
                "before": (old_lo, old_hi),
                "after": (lo, hi),
            }
        )

        if not (lo <= M <= hi):
            raise AssertionError("interval update lost the hidden toy value")

    return (lo, hi), trace


def main():
    print("=" * 86)
    print("Manger scientific model check")
    print("=" * 86)

    assert gcd(E, PHI) == 1
    assert 2 * B < N
    assert M < B

    print(f"p              = {P}")
    print(f"q              = {Q}")
    print(f"N              = {N}")
    print(f"e              = {E}")
    print(f"d              = {D}")
    print(f"k bytes        = {K}")
    print(f"B              = {B}")
    print(f"2B < N?        = {2*B < N}")
    print()
    print(f"hidden toy m   = {M}")
    print(f"m < B?         = {M < B}")
    print(f"ciphertext c   = {C}")

    print()
    print("=" * 86)
    print("PHASE 1")
    print("=" * 86)

    f1, trace1 = phase1()

    for f, reduced, result in trace1:
        print(
            f"f={f:<8d} m*f mod N={reduced:<12d} "
            f"oracle={'< B' if result else '>= B'}"
        )

    half = f1 // 2

    assert B / 2 <= half * M < B

    print()
    print(f"first boundary-crossing f1 = {f1}")
    print(f"half multiplier            = {half}")
    print(
        f"known interval from phase1 = "
        f"[ceil(B/(2*half)), floor((B-1)/half)]"
    )

    print()
    print("=" * 86)
    print("PHASE 2")
    print("=" * 86)

    f2, trace2 = phase2(f1)

    print(f"phase-2 start multiplier = {trace2[0][0]}")
    print(f"number of phase-2 queries = {len(trace2)}")
    print("last six phase-2 observations:")

    for f, reduced, result in trace2[-6:]:
        print(
            f"f={f:<8d} m*f mod N={reduced:<12d} "
            f"oracle={'< B' if result else '>= B'}"
        )

    raw = f2 * M
    assert N <= raw < N + B

    lo2 = ceil(N / f2)
    hi2 = floor((N + B - 1) / f2)

    print()
    print(f"successful f2      = {f2}")
    print(f"f2*m               = {raw}")
    print(f"f2*m - N           = {raw-N}")
    print(f"phase-2 interval   = [{lo2}, {hi2}]")
    print(f"candidate count    = {hi2-lo2+1}")

    print()
    print("=" * 86)
    print("PHASE 3")
    print("=" * 86)

    final_interval, trace3 = phase3(f2)

    for idx, row in enumerate(trace3, start=1):
        response = "< B" if row["oracle_lt_B"] else ">= B"
        print(
            f"{idx:02d}. f3={row['f3']:<9d} "
            f"i={row['i']:<7d} "
            f"oracle={response:<4s} "
            f"{row['before']} -> {row['after']}"
        )

    print()
    print(f"phase-3 updates = {len(trace3)}")
    print(f"final interval  = {final_interval}")

    assert final_interval == (M, M)

    print()
    print("All Manger interval identities verified.")
    print("No external oracle, OAEP endpoint, or network workflow was used.")


if __name__ == "__main__":
    main()
