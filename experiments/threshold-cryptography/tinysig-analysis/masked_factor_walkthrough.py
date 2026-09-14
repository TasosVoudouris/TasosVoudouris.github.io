"""Dependency-free algebra check for the masking identities used by TinySig.

This is not TinySig and not a threshold-ECDSA implementation.  It is a tiny
finite-field model of the cancellation that makes the online signing formula
work.  The numbers are intentionally small and insecure.
"""

Q = 23                  # toy prime field
H = 5                   # primitive root modulo 23
ORDER = Q - 1           # exponent arithmetic for Z_q^*


def inv(a: int, modulus: int) -> int:
    return pow(a % modulus, -1, modulus)


def hpow(exponent: int) -> int:
    return pow(H, exponent % ORDER, Q)


def main() -> None:
    # Toy ECDSA-scalar values.  We model only the scalar equation
    #     s = k^{-1}(m + r*x) mod q
    # and TinySig's multiplicative masks, not the elliptic-curve computation of r.
    x = 7
    k = 9
    m = 11
    r_sig = 4

    # Independent mask exponents in Z_{q-1}.
    lam_x = 3
    lam_k = 8
    lam_1 = 13
    lam_2 = 6

    # <x>_lam = x * h^{-lam}.
    masked_x = x * hpow(-lam_x) % Q
    masked_k = k * hpow(-lam_k) % Q

    # TinySig uses <k>^{-1} = k^{-1} h^{lam_k}, which is the masked
    # representation of k^{-1} under mask exponent -lam_k.
    masked_k_inv = inv(masked_k, Q)
    expected_masked_k_inv = inv(k, Q) * hpow(lam_k) % Q
    assert masked_k_inv == expected_masked_k_inv

    # The preprocessing bookkeeping used in the prototype.
    lam_m = (lam_1 + lam_k) % ORDER
    lam_gap = (-lam_k - lam_2 + lam_x) % ORDER

    # Client masks the message before the online round.
    masked_message = m * hpow(-(lam_m + lam_gap)) % Q

    # The two encrypted/plaintext-linear terms that the signers evaluate.
    # In TinySig h^{lam_1} and h^{lam_2} are themselves additively shared,
    # encrypted under the client's Paillier public key, and scaled homomorphically.
    term_m = hpow(lam_1) * masked_k_inv * masked_message % Q
    term_rx = hpow(lam_2) * masked_k_inv * r_sig * masked_x % Q
    masked_s = (term_m + term_rx) % Q

    # Client removes the remaining gap mask.
    recovered_s = masked_s * hpow(lam_gap) % Q
    direct_s = inv(k, Q) * (m + r_sig * x) % Q

    print(f"q={Q}, h={H}")
    print(f"masked x      = {masked_x}")
    print(f"masked k      = {masked_k}")
    print(f"masked k^-1   = {masked_k_inv}")
    print(f"lambda_m      = {lam_m}")
    print(f"lambda_gap    = {lam_gap}")
    print(f"masked message= {masked_message}")
    print(f"masked s      = {masked_s}")
    print(f"recovered s   = {recovered_s}")
    print(f"direct s      = {direct_s}")

    assert recovered_s == direct_s
    print("PASS: TinySig mask exponents cancel to the ECDSA scalar equation.")


if __name__ == "__main__":
    main()
