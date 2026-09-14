"""FFT-based packed secret sharing on fixed toy finite-field domains.

The small fixed field keeps the example reproducible and fast:
- F_433
- radix-2 domain of size 16
- radix-3 domain of size 27

This is educational code, not a production MPC implementation.
"""
from __future__ import annotations

import secrets

Q = 433
ORDER2 = 16
ORDER3 = 27
OMEGA2 = 238  # primitive 16th root of unity mod 433
OMEGA3 = 17  # primitive 27th root of unity mod 433

N = ORDER3 - 1
T = N // 2
K = ORDER2 - T - 1

assert K == 2
assert pow(OMEGA2, ORDER2, Q) == 1
assert all(pow(OMEGA2, e, Q) != 1 for e in range(1, ORDER2))
assert pow(OMEGA3, ORDER3, Q) == 1
assert all(pow(OMEGA3, e, Q) != 1 for e in range(1, ORDER3))


def fft2(values: list[int], omega: int) -> list[int]:
    n = len(values)
    if n == 1:
        return values.copy()
    if n % 2:
        raise ValueError("radix-2 FFT needs a power-of-two length")

    even = fft2(values[0::2], pow(omega, 2, Q))
    odd = fft2(values[1::2], pow(omega, 2, Q))

    out = [0] * n
    point = 1
    half = n // 2
    for i in range(half):
        term = (point * odd[i]) % Q
        out[i] = (even[i] + term) % Q
        out[i + half] = (even[i] - term) % Q
        point = (point * omega) % Q
    return out


def ifft2(values: list[int]) -> list[int]:
    n_inv = pow(len(values), -1, Q)
    omega_inv = pow(OMEGA2, -1, Q)
    return [(x * n_inv) % Q for x in fft2(values, omega_inv)]


def fft3(values: list[int], omega: int) -> list[int]:
    n = len(values)
    if n == 1:
        return values.copy()
    if n % 3:
        raise ValueError("radix-3 FFT needs a power-of-three length")

    a0 = fft3(values[0::3], pow(omega, 3, Q))
    a1 = fft3(values[1::3], pow(omega, 3, Q))
    a2 = fft3(values[2::3], pow(omega, 3, Q))

    out = [0] * n
    third = n // 3
    cube_root = pow(omega, third, Q)
    point = 1

    for i in range(third):
        x0 = point
        x1 = (x0 * cube_root) % Q
        x2 = (x1 * cube_root) % Q

        for offset, x in enumerate((x0, x1, x2)):
            out[i + offset * third] = (
                a0[i] + x * a1[i] + (x * x % Q) * a2[i]
            ) % Q
        point = (point * omega) % Q
    return out


def ifft3(values: list[int]) -> list[int]:
    n_inv = pow(len(values), -1, Q)
    omega_inv = pow(OMEGA3, -1, Q)
    return [(x * n_inv) % Q for x in fft3(values, omega_inv)]


def share(secrets_: list[int]) -> list[int]:
    if len(secrets_) != K:
        raise ValueError(f"expected exactly {K} packed secrets")

    small_values = [0] + [s % Q for s in secrets_]
    small_values += [secrets.randbelow(Q) for _ in range(T)]
    assert len(small_values) == ORDER2

    small_coeffs = ifft2(small_values)
    large_coeffs = small_coeffs + [0] * (ORDER3 - ORDER2)
    large_values = fft3(large_coeffs, OMEGA3)
    return large_values[1:]


def reconstruct(shares: list[int]) -> list[int]:
    if len(shares) != N:
        raise ValueError(f"this FFT reconstruction expects all {N} shares")

    large_values = [0] + [x % Q for x in shares]
    large_coeffs = ifft3(large_values)
    if any(large_coeffs[ORDER2:]):
        raise ValueError("received values are inconsistent with the encoded degree bound")

    small_values = fft2(large_coeffs[:ORDER2], OMEGA2)
    return small_values[1:1 + K]


def _self_test() -> None:
    coeffs2 = list(range(ORDER2))
    assert ifft2(fft2(coeffs2, OMEGA2)) == coeffs2

    coeffs3 = list(range(ORDER3))
    assert ifft3(fft3(coeffs3, OMEGA3)) == coeffs3

    secret_vector = [7, 31]
    shares = share(secret_vector)
    assert reconstruct(shares) == secret_vector

    print(f"Q={Q}, K={K}, T={T}, N={N}")
    print("FFT packed-sharing checks passed")


if __name__ == "__main__":
    _self_test()
