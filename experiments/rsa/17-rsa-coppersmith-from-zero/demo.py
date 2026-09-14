"""
RSA Deep Dive V — Coppersmith From Zero.

Known-prefix textbook RSA example:

    p = 30011
    q = 35027
    N = p*q
    e = 3

    actual message = 12037
    known prefix   = 12000
    unknown x0     = 37
    promised |x0| < 100

Polynomial:

    f(x) = (12000 + x)^3 - c

The hidden x0 is a small root modulo N.

The demo:
- builds the polynomial shifts;
- builds a 7D coefficient lattice;
- runs a local exact LLL implementation;
- checks the divisibility/smallness inequality;
- obtains an integer polynomial h with h(37)=0;
- recovers x0 and the plaintext.
"""

from math import isqrt

from coppersmith import (
    build_lattice_basis,
    recover_small_root,
)
from polynomial import (
    evaluate,
    power,
    pretty,
    sub,
)


P = 30_011
Q = 35_027
N = P * Q
E = 3

KNOWN_PREFIX = 12_000
UNKNOWN = 37
MESSAGE = KNOWN_PREFIX + UNKNOWN

X = 100
M = 2
T = 1

CIPHERTEXT = pow(MESSAGE, E, N)

# f(x) = (KNOWN_PREFIX + x)^3 - ciphertext
F = sub(
    power([KNOWN_PREFIX, 1], E),
    [CIPHERTEXT],
)


def heading(title: str) -> None:
    print()
    print("=" * 88)
    print(title)
    print("=" * 88)


heading("1. RSA instance")

print("p             =", P)
print("q             =", Q)
print("N             =", N)
print("e             =", E)
print("message       =", MESSAGE)
print("known prefix  =", KNOWN_PREFIX)
print("hidden x0     =", UNKNOWN)
print("bound X       =", X)
print("ciphertext    =", CIPHERTEXT)
print()
print("message^3     =", MESSAGE ** 3)
print("message^3 > N =", MESSAGE ** 3 > N)

assert N == 1_051_195_297
assert CIPHERTEXT == 100_336_930
assert MESSAGE ** 3 > N


heading("2. Build f(x) = (M0+x)^3 - c")

print("f(x) =", pretty(F))
print("f(37) mod N =", evaluate(F, UNKNOWN) % N)

assert F == [
    1_727_899_663_070,
    432_000_000,
    36_000,
    1,
]
assert evaluate(F, UNKNOWN) % N == 0
assert evaluate(F, UNKNOWN) != 0


heading("3. Root scale")

# Integer approximation used only for display.
print("N^(1/3) approximately =", N ** (1 / 3))
print("X                      =", X)
print("x0                     =", UNKNOWN)

assert UNKNOWN < X
assert X < N ** (1 / 3)


heading("4. Build shift polynomials and scaled lattice")

shifts, basis = build_lattice_basis(
    f=F,
    N=N,
    X=X,
    m=M,
    t=T,
)

print("basis dimension =", len(basis))
print()

for i, row in enumerate(basis):
    print(f"b{i} =", row)

assert len(basis) == 7
assert all(len(row) == 7 for row in basis)


heading("5. Verify every basis polynomial vanishes mod N^2 at x0")

modulus_power = N ** M

for i, g in enumerate(shifts):
    value = evaluate(g, UNKNOWN)
    remainder = value % modulus_power
    print(f"g{i}(x0) mod N^2 =", remainder)
    assert remainder == 0


heading("6. Run exact LLL and inspect the shortest vector")

trace = recover_small_root(
    f=F,
    N=N,
    X=X,
    m=M,
    t=T,
)

shortest = trace["shortest_vector"]
h = trace["h"]

print("LLL iterations =", trace["lll_iterations"])
print("shortest scaled vector:")
print(shortest)
print()
print("unscaled h(x):")
print(pretty(h))

assert trace["lll_iterations"] == 126
assert shortest == [
    23_407_270_775_993_751,
    -33_360_151_994_489_800,
    -34_621_233_503_770_000,
    -59_988_908_020_000_000,
    -115_518_764_200_000_000,
    -215_529_700_000_000_000,
    145_700_000_000_000_000,
]


heading("7. Check the smallness threshold")

# Condition:
#   ||v|| < N^m / sqrt(dimension)
#
# Avoid floating point:
#   dimension * ||v||^2 < N^(2m)

norm_squared = trace["norm_squared"]
dimension = trace["dimension"]

left = dimension * norm_squared
right = N ** (2 * M)

print("dimension * ||v||^2 =", left)
print("N^(2m)               =", right)
print("inequality holds?    =", left < right)

assert left < right


heading("8. Modular zero becomes integer zero")

h_at_root = evaluate(h, UNKNOWN)

print("h(37) =", h_at_root)
print("h(37) mod N^2 =", h_at_root % (N ** M))

assert h_at_root == 0


heading("9. Recover the unknown suffix")

print("roots inside [-X, X] =", trace["roots"])

assert trace["roots"] == [UNKNOWN]

recovered_message = KNOWN_PREFIX + trace["roots"][0]

print("recovered x0      =", trace["roots"][0])
print("recovered message =", recovered_message)

assert recovered_message == MESSAGE
assert pow(recovered_message, E, N) == CIPHERTEXT


heading("10. Failure experiment: lie about the root bound")

bad_trace = recover_small_root(
    f=F,
    N=N,
    X=30,
    m=M,
    t=T,
)

print("claimed X        = 30")
print("actual x0        =", UNKNOWN)
print("accepted roots   =", bad_trace["roots"])

assert bad_trace["roots"] == []


heading("11. Summary")

print("The attack recovered x0 without:")
print("  - factoring N")
print("  - knowing p or q")
print("  - recovering the RSA private exponent")
print("  - brute-forcing the realistic small-root regime")
print()
print("The key step was:")
print("  modular divisibility + LLL shortness -> integer polynomial zero")
