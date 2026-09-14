from rabin_ot import four_square_roots, recover_factor
from egl_ot import make_toy_key, receiver_request, sender_response, receiver_open


def test_rabin() -> None:
    p, q = 499, 547  # both 3 mod 4
    n = p * q
    x = 12345
    a = pow(x, 2, n)
    roots = four_square_roots(a, p, q)
    assert len(roots) == 4
    success = [r for r in roots if recover_factor(x, r, n)]
    assert len(success) == 2


def test_egl() -> None:
    key = make_toy_key()
    x0, x1 = 1234, 5678
    m0, m1 = 11111, 22222
    for choice, k in [(0, 321), (1, 777)]:
        v = receiver_request(key, x0, x1, choice, k)
        masked = sender_response(key, x0, x1, v, m0, m1)
        got = receiver_open(key, masked, choice, k)
        assert got == (m0, m1)[choice]


def main() -> None:
    test_rabin(); test_egl()
    print("Oblivious-transfer toy checks: PASS")


if __name__ == "__main__":
    main()
