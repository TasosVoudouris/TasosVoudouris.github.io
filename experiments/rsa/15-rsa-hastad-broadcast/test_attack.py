from math import prod

import pytest

from attack import (
    check_pairwise_coprime,
    crt,
    hastad_broadcast_recover,
    integer_nth_root,
)


def test_integer_nth_root_exact():
    root, exact = integer_nth_root(1_000_000, 3)

    assert root == 100
    assert exact is True


def test_integer_nth_root_non_exact():
    root, exact = integer_nth_root(2168, 3)

    assert root == 12
    assert exact is False


def test_crt_reconstructs_exact_cube():
    moduli = [187, 667, 1927]
    ciphertexts = [111, 167, 1814]

    C, P = crt(ciphertexts, moduli)

    assert P == 240_352_783
    assert C == 1_000_000


def test_hastad_broadcast_recovers_message():
    message = 100
    exponent = 3
    moduli = [187, 667, 1927]
    ciphertexts = [
        pow(message, exponent, n)
        for n in moduli
    ]

    recovered = hastad_broadcast_recover(
        ciphertexts,
        moduli,
        exponent,
    )

    assert recovered == message


def test_two_views_are_insufficient_for_chosen_example():
    message = 100
    exponent = 3
    moduli = [187, 667]
    ciphertexts = [
        pow(message, exponent, n)
        for n in moduli
    ]

    with pytest.raises(ValueError, match="not an exact"):
        hastad_broadcast_recover(
            ciphertexts,
            moduli,
            exponent,
        )


def test_non_coprime_moduli_are_rejected():
    with pytest.raises(ValueError, match="not pairwise coprime"):
        check_pairwise_coprime([77, 91, 143])


def test_crt_result_matches_every_residue():
    residues = [111, 167, 1814]
    moduli = [187, 667, 1927]

    C, _ = crt(residues, moduli)

    for residue, modulus in zip(residues, moduli):
        assert C % modulus == residue
