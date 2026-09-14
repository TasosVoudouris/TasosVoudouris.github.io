"""Example 7: distribute and verify shares with Feldman commitments."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.feldman import FeldmanVSS


def main() -> None:
    vss = FeldmanVSS.educational(
        num_parties=5,
        threshold=3,
        rng=random.Random(31),
    )
    distribution = vss.share(17)

    print("Feldman VSS: 3-out-of-5")
    print("Scalar field: F_41")
    print("Commitment subgroup: order 41 modulo 83")
    print("Generator:", vss.parameters.generator)
    print("Public commitments:", distribution.commitments.values)
    print()

    for share in distribution.sharing.shares:
        verification = vss.verify_share(share, distribution.commitments)
        print(
            f"participant {share.x}: share={share.y:2d}, "
            f"accepted={verification.accepted}"
        )

    chosen = distribution.sharing.shares[1:4]
    result = vss.reconstruct_verified(chosen, distribution.commitments)
    print("\nChosen verified participants:", [share.x for share in chosen])
    print("Reconstructed secret:", result.secret)


if __name__ == "__main__":
    main()
