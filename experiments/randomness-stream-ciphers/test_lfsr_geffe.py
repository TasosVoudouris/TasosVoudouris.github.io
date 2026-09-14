from lfsr_geffe import LFSR, agreement, geffe


def main() -> None:
    # Three maximal-ish toy registers with different lengths.
    a = LFSR((1, 0, 1), [1, 0, 0])
    b = LFSR((1, 1, 0, 1), [1, 0, 0, 1])
    c = LFSR((1, 0, 1, 0, 1), [1, 0, 1, 1, 0])
    sa, sb, sc, out = [], [], [], []
    for _ in range(2000):
        x, y, z = a.bit(), b.bit(), c.bit()
        sa.append(x); sb.append(y); sc.append(z)
        out.append(geffe(x, y, z))
    # For the Geffe combiner, the output is correlated with the two data
    # registers; finite toy sequences need only be clearly above chance.
    assert agreement(out, sb) > 0.65
    assert agreement(out, sc) > 0.65
    print("LFSR/Geffe correlation experiment: PASS")


if __name__ == "__main__":
    main()
