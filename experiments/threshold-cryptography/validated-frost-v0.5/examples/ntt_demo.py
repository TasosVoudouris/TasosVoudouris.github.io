"""Example 6: the transparent NTT behind the packed scheme."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.ntt import inverse_ntt, ntt


def main() -> None:
    coefficients = [1, 2, 3, 4, 5, 6, 7, 8]
    values = ntt(coefficients, root=354, modulus=433)
    recovered = inverse_ntt(values, root=354, modulus=433)

    print("Coefficients:", coefficients)
    print("NTT values:  ", values)
    print("Recovered:   ", recovered)


if __name__ == "__main__":
    main()
