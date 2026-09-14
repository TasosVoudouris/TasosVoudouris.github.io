import pytest

from attack import validate_rsa_candidate, wiener_attack
from continued_fraction import continued_fraction, convergents


N = 90_581
E = 17_993
D = 5
P = 379
Q = 239
PHI = 89_964


def test_continued_fraction_terms():
    assert continued_fraction(E, N) == [
        0, 5, 29, 4, 1, 3, 2, 4, 3
    ]


def test_convergents_include_secret_fraction():
    conv = list(convergents(
        continued_fraction(E, N)
    ))

    assert conv == [
        (0, 1),
        (1, 5),
        (29, 146),
        (117, 589),
        (146, 735),
        (555, 2794),
        (1256, 6323),
        (5579, 28086),
        (17993, 90581),
    ]

    assert (1, 5) in conv


def test_candidate_validation_recovers_factors():
    validated = validate_rsa_candidate(
        N,
        E,
        1,
        5,
    )

    assert validated is not None

    p, q, phi = validated

    assert {p, q} == {P, Q}
    assert phi == PHI


def test_wiener_attack_recovers_private_key():
    result = wiener_attack(N, E)

    assert result is not None
    assert result.d == D
    assert result.k == 1
    assert {result.p, result.q} == {P, Q}
    assert result.phi == PHI
    assert result.convergent_index == 1


def test_recovered_d_decrypts():
    result = wiener_attack(N, E)
    assert result is not None

    for message in [2, 42, 12_345, N - 1]:
        ciphertext = pow(message, E, N)
        recovered = pow(ciphertext, result.d, N)

        assert recovered == message


def test_invalid_candidate_is_rejected():
    assert validate_rsa_candidate(
        N,
        E,
        29,
        146,
    ) is None


def test_normal_sized_d_is_not_recovered():
    safeish_e = 65_537
    safeish_d = pow(safeish_e, -1, PHI)

    assert safeish_d == 26_801
    assert wiener_attack(N, safeish_e) is None


def test_zero_denominator_rejected():
    with pytest.raises(ZeroDivisionError):
        continued_fraction(1, 0)
