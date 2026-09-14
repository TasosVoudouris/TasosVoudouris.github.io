"""Small dependency-free radix-2 NTT demonstration over F_97."""
from __future__ import annotations

Q = 97
N = 16


def primitive_nth_root(n: int) -> int:
    if (Q - 1) % n:
        raise ValueError("n must divide q-1")
    for w in range(2, Q):
        if pow(w, n, Q) != 1:
            continue
        # n is power of two here: primitive iff w^(n/2) != 1
        if pow(w, n // 2, Q) != 1:
            return w
    raise RuntimeError("no primitive root found")


def bit_reverse_permute(a: list[int]) -> list[int]:
    n = len(a)
    bits = n.bit_length() - 1
    out = [0] * n
    for i, v in enumerate(a):
        r = int(f"{i:0{bits}b}"[::-1], 2)
        out[r] = v % Q
    return out


def ntt(values: list[int], inverse: bool = False) -> list[int]:
    n = len(values)
    if n == 0 or n & (n - 1):
        raise ValueError("length must be a nonzero power of two")
    w = primitive_nth_root(n)
    if inverse:
        w = pow(w, -1, Q)
    a = bit_reverse_permute(values)
    length = 2
    while length <= n:
        step = pow(w, n // length, Q)
        for start in range(0, n, length):
            omega = 1
            half = length // 2
            for j in range(half):
                u = a[start + j]
                v = a[start + j + half] * omega % Q
                a[start + j] = (u + v) % Q
                a[start + j + half] = (u - v) % Q
                omega = omega * step % Q
        length *= 2
    if inverse:
        ninv = pow(n, -1, Q)
        a = [x * ninv % Q for x in a]
    return a


def direct_dft(values: list[int]) -> list[int]:
    n = len(values)
    w = primitive_nth_root(n)
    return [sum(values[j] * pow(w, j * k, Q) for j in range(n)) % Q for k in range(n)]


def main() -> None:
    coeffs = [3, 1, 4, 1, 5, 9, 2, 6] + [0] * 8
    fast = ntt(coeffs)
    slow = direct_dft(coeffs)
    assert fast == slow
    assert ntt(fast, inverse=True) == [x % Q for x in coeffs]
    w = primitive_nth_root(N)
    assert pow(w, N, Q) == 1 and pow(w, N // 2, Q) != 1
    print(f"PASS: radix-2 NTT/INTT over F_{Q}, n={N}, primitive root={w}.")


if __name__ == "__main__":
    main()
