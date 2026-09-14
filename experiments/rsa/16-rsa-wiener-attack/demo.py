"""
RSA Deep Dive IV — Wiener's Attack From Zero.

Vulnerable example:
    p   = 379
    q   = 239
    N   = 90581
    phi = 89964
    d   = 5
    e   = 17993

The public ratio e/N has convergent 1/5, revealing k/d.

Comparison example:
    same N and phi
    e = 65537
    d = 26801  (inverse modulo phi)

The continued-fraction attack does not recover that normal-sized d.
"""

from math import isqrt

from attack import (
    validate_rsa_candidate,
    wiener_attack,
)
from continued_fraction import (
    continued_fraction,
    convergents,
)


P = 379
Q = 239
N = P * Q
PHI = (P - 1) * (Q - 1)

VULNERABLE_D = 5
VULNERABLE_E = 17_993

SAFEISH_E = 65_537
SAFEISH_D = pow(SAFEISH_E, -1, PHI)


def heading(title: str) -> None:
    print()
    print("=" * 82)
    print(title)
    print("=" * 82)


heading("1. Vulnerable textbook RSA key")

print("p   =", P)
print("q   =", Q)
print("N   =", N)
print("phi =", PHI)
print("e   =", VULNERABLE_E)
print("d   =", VULNERABLE_D)
print()
print("e*d - 1 =", VULNERABLE_E * VULNERABLE_D - 1)
print("(e*d - 1) / phi =", (VULNERABLE_E * VULNERABLE_D - 1) // PHI)

assert N == 90_581
assert PHI == 89_964
assert VULNERABLE_E * VULNERABLE_D - PHI == 1


heading("2. Continued fraction of e/N")

terms = continued_fraction(VULNERABLE_E, N)
conv = list(convergents(terms))

print("continued fraction:")
print(terms)
print()
print(f"{'i':>2} {'k':>8} {'d':>8} {'candidate':>12}")
print("-" * 36)

for i, (candidate_k, candidate_d) in enumerate(conv):
    valid = validate_rsa_candidate(
        N,
        VULNERABLE_E,
        candidate_k,
        candidate_d,
    )

    marker = "VALID" if valid is not None else "-"
    print(f"{i:>2} {candidate_k:>8} {candidate_d:>8} {marker:>12}")

assert terms == [0, 5, 29, 4, 1, 3, 2, 4, 3]
assert conv[1] == (1, 5)


heading("3. Inspect the successful candidate")

candidate_k, candidate_d = conv[1]

candidate_phi = (
    VULNERABLE_E * candidate_d - 1
) // candidate_k

S = N - candidate_phi + 1
delta = S * S - 4 * N
sqrt_delta = isqrt(delta)

candidate_p = (S + sqrt_delta) // 2
candidate_q = (S - sqrt_delta) // 2

print("k             =", candidate_k)
print("d             =", candidate_d)
print("candidate phi =", candidate_phi)
print("S = p+q       =", S)
print("delta         =", delta)
print("sqrt(delta)   =", sqrt_delta)
print("p             =", candidate_p)
print("q             =", candidate_q)

assert candidate_phi == PHI
assert S == 618
assert delta == 19_600
assert sqrt_delta == 140
assert {candidate_p, candidate_q} == {P, Q}


heading("4. Run the complete attack")

result = wiener_attack(N, VULNERABLE_E)

print(result)

assert result is not None
assert result.d == VULNERABLE_D
assert result.k == 1
assert {result.p, result.q} == {P, Q}
assert result.phi == PHI


heading("5. Verify recovered d on actual RSA arithmetic")

message = 12_345
ciphertext = pow(message, VULNERABLE_E, N)
recovered_message = pow(ciphertext, result.d, N)

print("message           =", message)
print("ciphertext        =", ciphertext)
print("decrypted with d  =", recovered_message)

assert recovered_message == message


heading("6. Compare with a normal-sized textbook d")

print("e =", SAFEISH_E)
print("d =", SAFEISH_D)

# The familiar classical sufficient scale.
wiener_scale = (N ** 0.25) / 3

print("N^(1/4)/3 ≈", wiener_scale)
print("d / scale  ≈", SAFEISH_D / wiener_scale)

assert SAFEISH_D == 26_801
assert SAFEISH_D > wiener_scale

comparison = wiener_attack(N, SAFEISH_E)

print("Wiener result =", comparison)

assert comparison is None


heading("7. Summary")

print("Vulnerable key:")
print("  public (N,e) =", (N, VULNERABLE_E))
print("  recovered d  =", result.d)
print("  recovered p  =", result.p)
print("  recovered q  =", result.q)
print()
print("Comparison key:")
print("  public (N,e) =", (N, SAFEISH_E))
print("  actual d     =", SAFEISH_D)
print("  Wiener attack returned None")
