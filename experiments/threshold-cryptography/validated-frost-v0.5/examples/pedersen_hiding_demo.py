"""Example 11: compare Feldman leakage with Pedersen hiding."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.feldman import FeldmanVSS
from cryptocave_sss.pedersen import PedersenVSS


def main() -> None:
    left_feldman = FeldmanVSS.educational(rng=random.Random(61)).share(9)
    right_feldman = FeldmanVSS.educational(rng=random.Random(62)).share(9)
    left_pedersen = PedersenVSS.educational(rng=random.Random(61)).share(9)
    right_pedersen = PedersenVSS.educational(rng=random.Random(62)).share(9)

    print("Two independent sharings of the same secret 9")
    print("Feldman C_0 values:")
    print(" ", left_feldman.commitments.public_secret_commitment)
    print(" ", right_feldman.commitments.public_secret_commitment)
    print("Feldman exposes equality?", (
        left_feldman.commitments.public_secret_commitment
        == right_feldman.commitments.public_secret_commitment
    ))
    print()
    print("Pedersen C_0 values:")
    print(" ", left_pedersen.commitments.blinded_secret_commitment)
    print(" ", right_pedersen.commitments.blinded_secret_commitment)
    print("Pedersen exposes equality in this run?", (
        left_pedersen.commitments.blinded_secret_commitment
        == right_pedersen.commitments.blinded_secret_commitment
    ))
    print("The blinding constant makes C_0 uniformly distributed in the subgroup.")


if __name__ == "__main__":
    main()
