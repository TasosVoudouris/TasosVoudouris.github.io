from lcg import lcg_step, recover_parameters


def main() -> None:
    m, a, c, s0 = 2**31 - 1, 48271, 12345, 987654
    s1 = lcg_step(s0, a, c, m)
    s2 = lcg_step(s1, a, c, m)
    ar, cr = recover_parameters(s0, s1, s2, m)
    assert (ar, cr) == (a, c)
    assert lcg_step(s2, ar, cr, m) == lcg_step(s2, a, c, m)
    print("LCG parameter recovery: PASS")


if __name__ == "__main__":
    main()
