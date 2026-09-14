"""Example 2: five-out-of-ten Shamir secret sharing."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.shamir import ShamirScheme


def main() -> None:
    scheme = ShamirScheme(
        modulus=41,
        num_parties=10,
        threshold=5,
        rng=random.Random(4),
    )

    sharing = scheme.share(17)
    print("Polynomial degree:", scheme.degree)
    print("Reconstruction threshold:", scheme.threshold)
    print("Shares:")
    for share in sharing.shares:
        print(f"  participant {share.x:2d} receives {share.y:2d}")

    chosen = sharing.shares[1:6]
    print("\nChosen participants:", [share.x for share in chosen])
    print("Reconstructed secret:", sharing.reveal(chosen))

    try:
        sharing.reveal(sharing.shares[:4])
    except ValueError as error:
        print("Four-share attempt rejected:", error)


if __name__ == "__main__":
    main()
