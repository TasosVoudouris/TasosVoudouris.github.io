"""
RSA Deep Dive III — Håstad Broadcast Attack.

Fixed toy experiment:

    m  = 100
    e  = 3
    N1 = 187  = 11 * 17
    N2 = 667  = 23 * 29
    N3 = 1927 = 41 * 47

Every individual ciphertext wraps modulo its own modulus.
Three pairwise-coprime views let CRT reconstruct m^3 exactly.

Educational local arithmetic only.
"""

from math import gcd, prod

from attack import (
    crt,
    hastad_broadcast_recover,
    integer_nth_root,
)


MESSAGE = 100
E = 3

MODULI = [187, 667, 1927]
CIPHERTEXTS = [
    pow(MESSAGE, E, n)
    for n in MODULI
]


def heading(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


heading("1. Public broadcast data")

print("message (hidden from attacker) =", MESSAGE)
print("public exponent               =", E)

for i, (n, c) in enumerate(zip(MODULI, CIPHERTEXTS), start=1):
    print(f"N{i} = {n:4d}   c{i} = {c:4d}")

assert CIPHERTEXTS == [111, 167, 1814]


heading("2. Every individual ciphertext really wrapped")

integer_cube = MESSAGE ** E

print("m^3 =", integer_cube)

for i, n in enumerate(MODULI, start=1):
    print(f"m^3 > N{i}? {integer_cube > n}")

assert all(integer_cube > n for n in MODULI)


heading("3. Check the CRT precondition")

for i in range(len(MODULI)):
    for j in range(i + 1, len(MODULI)):
        g = gcd(MODULI[i], MODULI[j])
        print(f"gcd(N{i+1}, N{j+1}) = {g}")
        assert g == 1


heading("4. Reconstruct the common cube with CRT")

C, P = crt(CIPHERTEXTS, MODULI)

print("product P      =", P)
print("CRT result C   =", C)
print("actual m^3     =", integer_cube)
print("m^3 < P?       =", integer_cube < P)
print("C == m^3?      =", C == integer_cube)

assert P == 240_352_783
assert C == 1_000_000
assert C == integer_cube


heading("5. Take an exact integer cube root")

root, exact = integer_nth_root(C, E)

print("root  =", root)
print("exact =", exact)

assert root == MESSAGE
assert exact


heading("6. Full attack helper")

recovered = hastad_broadcast_recover(
    CIPHERTEXTS,
    MODULI,
    E,
)

print("recovered message =", recovered)

assert recovered == MESSAGE


heading("7. Remove one recipient: simple recovery fails here")

two_C, two_P = crt(
    CIPHERTEXTS[:2],
    MODULI[:2],
)

two_root, two_exact = integer_nth_root(two_C, E)

print("N1*N2                =", two_P)
print("m^3                  =", integer_cube)
print("CRT using two views  =", two_C)
print("floor cube root      =", two_root)
print("exact cube?          =", two_exact)

assert two_P == 124_729
assert integer_cube > two_P
assert two_C == 2168
assert not two_exact

try:
    hastad_broadcast_recover(
        CIPHERTEXTS[:2],
        MODULI[:2],
        E,
    )
except ValueError as exc:
    print("attack helper rejected the case:")
    print(" ", exc)
else:
    raise AssertionError("expected insufficient-data case to fail")


heading("8. Summary")

print("The attack used only:")
print("  - public moduli")
print("  - public exponent")
print("  - public ciphertexts")
print("  - CRT")
print("  - an exact integer cube root")
print()
print("No modulus was factored and no private exponent was recovered.")
