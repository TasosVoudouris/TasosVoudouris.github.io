from fractions import Fraction

from coppersmith import (
    build_lattice_basis,
    recover_small_root,
)
from lll import gram_schmidt, lll_reduce
from polynomial import (
    add,
    evaluate,
    mul,
    power,
    sub,
)


P = 30_011
Q = 35_027
N = P * Q
E = 3

KNOWN_PREFIX = 12_000
UNKNOWN = 37
MESSAGE = KNOWN_PREFIX + UNKNOWN
CIPHERTEXT = pow(MESSAGE, E, N)

F = sub(
    power([KNOWN_PREFIX, 1], E),
    [CIPHERTEXT],
)


def test_polynomial_arithmetic():
    assert add([1, 2], [3, 4, 5]) == [4, 6, 5]
    assert mul([1, 1], [1, 1]) == [1, 2, 1]
    assert power([1, 1], 3) == [1, 3, 3, 1]
    assert evaluate([1, 2, 3], 2) == 17


def test_rsa_polynomial_has_hidden_modular_root():
    assert evaluate(F, UNKNOWN) % N == 0
    assert evaluate(F, UNKNOWN) != 0


def test_basis_shape_and_divisibility():
    shifts, basis = build_lattice_basis(
        f=F,
        N=N,
        X=100,
        m=2,
        t=1,
    )

    assert len(basis) == 7
    assert all(len(row) == 7 for row in basis)

    for g in shifts:
        assert evaluate(g, UNKNOWN) % (N ** 2) == 0


def test_gram_schmidt_is_exact():
    basis = [
        [1, 1],
        [1, 0],
    ]

    _, mu, norms = gram_schmidt(basis)

    assert mu[1][0] == Fraction(1, 2)
    assert norms[0] == 2
    assert norms[1] == Fraction(1, 2)


def test_lll_reduces_simple_basis():
    reduced, _ = lll_reduce([
        [1, 1],
        [1, 0],
    ])

    assert sorted(
        sum(v * v for v in row)
        for row in reduced
    ) == [1, 1]


def test_coppersmith_recovers_unknown_suffix():
    trace = recover_small_root(
        f=F,
        N=N,
        X=100,
        m=2,
        t=1,
    )

    assert trace["roots"] == [37]


def test_short_vector_meets_integer_zero_bound():
    trace = recover_small_root(
        f=F,
        N=N,
        X=100,
        m=2,
        t=1,
    )

    assert (
        trace["dimension"]
        * trace["norm_squared"]
        <
        N ** 4
    )


def test_recovered_polynomial_is_zero_at_root():
    trace = recover_small_root(
        f=F,
        N=N,
        X=100,
        m=2,
        t=1,
    )

    assert evaluate(
        trace["h"],
        UNKNOWN,
    ) == 0


def test_reconstruct_plaintext():
    trace = recover_small_root(
        f=F,
        N=N,
        X=100,
        m=2,
        t=1,
    )

    recovered = KNOWN_PREFIX + trace["roots"][0]

    assert recovered == MESSAGE
    assert pow(recovered, E, N) == CIPHERTEXT


def test_wrong_root_bound_rejects_actual_root():
    trace = recover_small_root(
        f=F,
        N=N,
        X=30,
        m=2,
        t=1,
    )

    assert trace["roots"] == []
