"""Tiny Search-LWE recovery by exhaustive search. Deliberately insecure."""
from itertools import product

q = 23
secret = (4, 7)
A = [
    (1, 3), (4, 8), (9, 5), (2, 11), (7, 6),
    (10, 1), (3, 14), (12, 4), (8, 9), (5, 13),
]
errors = (0, 1, -1, 1, 0, -1, 1, 0, -1, 0)


def centered(x, q=q):
    x %= q
    return x - q if x > q // 2 else x


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


b = [(dot(a, secret) + e) % q for a, e in zip(A, errors)]


def score(candidate):
    residuals = [centered(bi - dot(ai, candidate)) for ai, bi in zip(A, b)]
    return sum(r * r for r in residuals), max(abs(r) for r in residuals)


def recover():
    candidates = list(product(range(q), repeat=2))
    return min(candidates, key=score)


if __name__ == "__main__":
    recovered = recover()
    assert recovered == secret, (recovered, secret, score(recovered))
    print("secret   =", secret)
    print("recovered=", recovered)
    print("residuals=", [centered(bi - dot(ai, recovered)) for ai, bi in zip(A, b)])
