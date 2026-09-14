"""Tiny SIS demonstration. Parameters are deliberately insecure."""
from itertools import product
from math import sqrt

q = 11
A = (
    (2, 5, 7, 1),
    (4, 3, 8, 6),
)


def mat_vec_mod(A, z, q):
    return tuple(sum(a * b for a, b in zip(row, z)) % q for row in A)


def norm2(z):
    return sqrt(sum(x * x for x in z))


def find_sis(bound=2):
    best = None
    for z in product(range(-bound, bound + 1), repeat=len(A[0])):
        if all(v == 0 for v in z):
            continue
        if mat_vec_mod(A, z, q) == (0, 0):
            if best is None or norm2(z) < norm2(best):
                best = z
    return best


if __name__ == "__main__":
    z = find_sis()
    assert z is not None
    assert mat_vec_mod(A, z, q) == (0, 0)
    print("A =", A)
    print("short kernel vector z =", z)
    print("||z||_2 =", norm2(z))
