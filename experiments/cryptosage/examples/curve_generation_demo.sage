"""Derive a small nonsingular curve from a public seed and verify it."""

load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/curve_generation.sage")

# This small Mersenne prime keeps the demonstration fast; it is not secure.
field_prime = Integer(2) ** 31 - 1
seed, a_coefficient, b_coefficient = ecc_curve_gen(field_prime)

print("Public seed:", seed)
print("Curve equation: y^2 = x^3 + (%s)x + (%s)" % (
    a_coefficient, b_coefficient
))
print("Seed verification:", verify_ecc_curve(
    field_prime, seed, a_coefficient, b_coefficient
))

