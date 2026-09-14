"""Example 1: N-out-of-N additive secret sharing."""

import random
import sys
from pathlib import Path

# Allow both:
#   python -m examples.additive_demo
#   python additive_demo.py   (from inside the examples folder)
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.additive import (
    AdditiveSecret,
    additive_reconstruct,
    additive_share,
    explain_missing_share,
)


def main() -> None:
    modulus = 41
    num_parties = 4

    # A fixed seed makes this printed lesson repeatable.  Normal package use
    # omits rng=..., which selects operating-system randomness instead.
    shares = additive_share(5, num_parties, modulus, rng=random.Random(1))
    print("Secret: 5")
    print("Shares:", shares)
    print("Reconstructed field element:", additive_reconstruct(shares, modulus))

    # If one share is missing, every possible secret still has an explanation.
    known_shares = shares[:-1]
    print("\nThe first three parties cannot identify the secret:")
    for guess in (0, 5, 17, 40):
        missing = explain_missing_share(known_shares, guess, modulus)
        print(f"guess {guess:2d} is possible if the missing share is {missing:2d}")

    x = AdditiveSecret.from_secret(5, num_parties, modulus, random.Random(2))
    y = AdditiveSecret.from_secret(8, num_parties, modulus, random.Random(3))
    print("\n5 + 8 =", (x + y).reveal())
    print("5 - 8 =", (x - y).reveal())


if __name__ == "__main__":
    main()
