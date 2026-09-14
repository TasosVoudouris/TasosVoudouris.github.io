"""Example 10: distribute and verify Pedersen share pairs."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.pedersen import PedersenVSS


def main() -> None:
    vss = PedersenVSS.educational(rng=random.Random(51))
    distribution = vss.share(17)

    print("Pedersen VSS: 3-out-of-5")
    print("Secret field: F_41")
    print("Commitment subgroup: order 41 modulo 83")
    print("Value generator g:", vss.parameters.value_generator)
    print("Blinding generator h:", vss.parameters.blinding_generator)
    print("Public commitments:", distribution.commitments.values)
    print()

    for share in distribution.shares:
        result = vss.verify_share(share, distribution.commitments)
        print(
            f"participant {share.x}: value={share.value:2d}, "
            f"blinding={share.blinding:2d}, accepted={result.accepted}"
        )

    selected = distribution.subset([1, 3, 5])
    opened = vss.reconstruct_verified(selected, distribution.commitments)
    print("\nReconstructed secret:", opened.secret)


if __name__ == "__main__":
    main()
