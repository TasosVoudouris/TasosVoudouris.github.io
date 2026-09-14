"""Educational, reproducible EC parameter generation from a public seed.

This is not an implementation of a named standards procedure. It replaces the
supplied file's contradictory generation/verification conditions with a small,
internally consistent study of seed-derived coefficients and subgroup choice.
"""

import hashlib


def _seed_coefficient(field_prime, seed, label):
    """Derive one field element from a seed and a domain-separation label."""

    width = (Integer(field_prime).nbits() + 7) // 8
    encoded_seed = i2osp(Integer(seed), width)
    value = hashlib.sha256(label + encoded_seed).digest()
    return Integer(int.from_bytes(value, byteorder="big") % field_prime)


def ecc_curve_gen(field_prime, max_attempts=1000):
    """Generate seed-derived coefficients for a nonsingular short Weierstrass curve."""

    field_prime = Integer(field_prime)
    if field_prime <= 3 or not field_prime.is_prime():
        raise ValueError("field_prime must be an odd prime greater than 3")

    for _ in range(max_attempts):
        seed = Integer(randint(1, field_prime - 1))
        a_coefficient = _seed_coefficient(field_prime, seed, b"curve-a|")
        b_coefficient = _seed_coefficient(field_prime, seed, b"curve-b|")
        discriminant_term = (
            4 * a_coefficient ** 3 + 27 * b_coefficient ** 2
        ) % field_prime
        if discriminant_term != 0:
            return seed, a_coefficient, b_coefficient
    raise RuntimeError("failed to derive a nonsingular curve within max_attempts")


def verify_ecc_curve(field_prime, seed, a_coefficient, b_coefficient):
    """Verify that the coefficients match the seed and define a nonsingular curve."""

    field_prime = Integer(field_prime)
    expected_a = _seed_coefficient(field_prime, seed, b"curve-a|")
    expected_b = _seed_coefficient(field_prime, seed, b"curve-b|")
    discriminant_term = (
        4 * Integer(a_coefficient) ** 3 + 27 * Integer(b_coefficient) ** 2
    ) % field_prime
    return (
        Integer(a_coefficient) == expected_a
        and Integer(b_coefficient) == expected_b
        and discriminant_term != 0
    )


def parameter_set_gen(field_prime, minimum_subgroup_bits, max_attempts=100):
    """Find a seed-derived curve with a sufficiently large prime subgroup.

    The function factors the curve order and is therefore intended for small
    experiments. It also rejects embedding degrees up to 20 as a basic study of
    the MOV condition; that check alone is not a complete security assessment.
    """

    field_prime = Integer(field_prime)
    minimum_subgroup_bits = Integer(minimum_subgroup_bits)

    for _ in range(max_attempts):
        seed, a_coefficient, b_coefficient = ecc_curve_gen(field_prime)
        curve = EllipticCurve(
            FiniteField(field_prime), [a_coefficient, b_coefficient]
        )
        curve_order = Integer(curve.order())
        prime_factors = [
            Integer(prime_factor)
            for prime_factor, _ in factor(curve_order)
        ]
        candidates = [
            candidate
            for candidate in prime_factors
            if candidate.nbits() >= minimum_subgroup_bits
        ]
        if not candidates:
            continue
        subgroup_order = max(candidates)
        if any(
            power_mod(field_prime, degree, subgroup_order) == 1
            for degree in range(1, 21)
        ):
            continue

        cofactor = curve_order // subgroup_order
        for _ in range(100):
            generator = cofactor * curve.random_point()
            if not generator.is_zero() and subgroup_order * generator == curve(0):
                return {
                    "field_prime": field_prime,
                    "seed": seed,
                    "a": a_coefficient,
                    "b": b_coefficient,
                    "curve": curve,
                    "generator": generator,
                    "subgroup_order": subgroup_order,
                    "cofactor": cofactor,
                }
    raise RuntimeError("no suitable parameter set found within max_attempts")


# Compatibility name for the original entry point.
param_gen = parameter_set_gen
