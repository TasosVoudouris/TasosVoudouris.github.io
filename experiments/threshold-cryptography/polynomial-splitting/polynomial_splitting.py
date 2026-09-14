"""Horner evaluation and radix-2 polynomial splitting over F_433."""

Q = 433
OMEGA4 = 179


def horner_evaluate(coeffs: list[int], point: int) -> int:
    result = 0
    for coef in reversed(coeffs):
        result = (coef + point * result) % Q
    return result


if __name__ == "__main__":
    roots = [pow(OMEGA4, e, Q) for e in range(4)]
    assert roots == [1, 179, 432, 254]

    a_coeffs = [1, 2, 3, 4]
    a = lambda x: horner_evaluate(a_coeffs, x)

    b_coeffs = a_coeffs[0::2]
    c_coeffs = a_coeffs[1::2]

    b = lambda x: horner_evaluate(b_coeffs, x)
    c = lambda x: horner_evaluate(c_coeffs, x)

    squared = [(w * w) % Q for w in roots]
    recombined = [
        (b(v) + w * c(v)) % Q
        for w, v in zip(roots, squared)
    ]

    assert recombined == [a(w) for w in roots]
    assert [a(w) for w in roots] == [10, 73, 431, 356]

    print("roots:", roots)
    print("values:", recombined)
    print("polynomial-splitting checks passed")
