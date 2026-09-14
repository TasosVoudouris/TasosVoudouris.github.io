"""Small R1CS example for x^3 + 4x^2 - xz + 4 = y over F_p."""
P = 97

# Witness ordering: [1, x, x^2, x^3, z, y]
A = [
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, -1, 0, 0, 0, 0],
]
B = [
    [0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0],
]
C = [
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [-4, 0, -4, -1, 0, 1],
]


def dot(row, w):
    return sum(a * b for a, b in zip(row, w)) % P


def check(w):
    return all((dot(a, w) * dot(b, w) - dot(c, w)) % P == 0
               for a, b, c in zip(A, B, C))


def self_test():
    x, z, y = 7, 2, 529
    w = [1, x, x*x, x*x*x, z, y]
    w = [v % P for v in w]
    assert check(w)
    bad = w.copy(); bad[-1] = (bad[-1] + 1) % P
    assert not check(bad)
    print("R1CS witness: PASS")
    print("invalid witness rejection: PASS")


if __name__ == "__main__":
    self_test()
