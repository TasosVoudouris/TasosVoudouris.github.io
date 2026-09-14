"""Example 9: Feldman commitments are binding but not hiding."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.feldman import FeldmanVSS


def main() -> None:
    first = FeldmanVSS.educational(rng=random.Random(33)).share(9)
    second = FeldmanVSS.educational(rng=random.Random(34)).share(9)
    different = FeldmanVSS.educational(rng=random.Random(35)).share(10)

    first_c0 = first.commitments.public_secret_commitment
    second_c0 = second.commitments.public_secret_commitment
    different_c0 = different.commitments.public_secret_commitment

    print("First sharing of secret 9:  C0 =", first_c0)
    print("Second sharing of secret 9: C0 =", second_c0)
    print("Sharing of secret 10:       C0 =", different_c0)
    print("\nSame secret gives same C0?", first_c0 == second_c0)
    print("Different secret gives different C0?", first_c0 != different_c0)
    print("\nVersion 0.3 Pedersen VSS adds a blinding polynomial; run")
    print("pedersen_hiding_demo.py next to compare the two constructions.")


if __name__ == "__main__":
    main()
