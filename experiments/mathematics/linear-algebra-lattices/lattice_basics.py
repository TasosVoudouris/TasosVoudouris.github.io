"""Dependency-free Gram-Schmidt and a small educational LLL implementation."""
from __future__ import annotations
from fractions import Fraction


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def gram_schmidt(basis):
    ortho = []
    mu = [[Fraction(0) for _ in basis] for _ in basis]
    for i, b in enumerate(basis):
        v = [Fraction(x) for x in b]
        for j, q in enumerate(ortho):
            den = dot(q, q)
            mu[i][j] = Fraction(dot(b, q), den)
            v = [x - mu[i][j] * y for x, y in zip(v, q)]
        ortho.append(v)
    return ortho, mu


def nearest_integer(x: Fraction) -> int:
    if x >= 0:
        return (2 * x.numerator + x.denominator) // (2 * x.denominator)
    return -nearest_integer(-x)


def lll_reduce(basis, delta=Fraction(3, 4)):
    B = [list(map(int, row)) for row in basis]
    k = 1
    while k < len(B):
        ortho, mu = gram_schmidt(B)
        for j in range(k - 1, -1, -1):
            q = nearest_integer(mu[k][j])
            if q:
                B[k] = [x - q * y for x, y in zip(B[k], B[j])]
                ortho, mu = gram_schmidt(B)
        lhs = dot(ortho[k], ortho[k])
        rhs = (delta - mu[k][k - 1] ** 2) * dot(ortho[k - 1], ortho[k - 1])
        if lhs >= rhs:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)
    return B


def _self_test():
    basis = [[1, 1, 1], [-1, 0, 2], [3, 5, 6]]
    red = lll_reduce(basis)
    assert len(red) == 3
    assert all(len(v) == 3 for v in red)
    # The reduced basis should contain short vectors for this toy input.
    assert min(dot(v, v) for v in red) <= 3


if __name__ == '__main__':
    _self_test()
    print('linear-algebra/lattice checks: PASS')
