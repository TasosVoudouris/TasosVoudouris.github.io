"""Example 8: show what Feldman detects and what it does not solve."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.feldman import FeldmanVSS
from cryptocave_sss.shamir import Share


def main() -> None:
    vss = FeldmanVSS.educational(rng=random.Random(32))
    distribution = vss.share(12)

    honest = distribution.sharing.shares[0]
    changed = Share(honest.x, (honest.y + 1) % vss.shamir.modulus)

    honest_result = vss.verify_share(honest, distribution.commitments)
    changed_result = vss.verify_share(changed, distribution.commitments)

    print("Honest share:", honest)
    print("Honest share accepted?", honest_result.accepted)
    print("Changed share:", changed)
    print("Changed share accepted?", changed_result.accepted)

    received = [changed, *distribution.sharing.shares[1:]]
    reconstruction = vss.reconstruct_verified(
        received,
        distribution.commitments,
    )
    print("\nRejected IDs:", [share.x for share in reconstruction.report.rejected])
    print("Accepted IDs:", [share.x for share in reconstruction.report.accepted])
    print("Reconstructed from accepted shares:", reconstruction.secret)

    print("\nStill missing from this local simulation:")
    print("- reliable broadcast of one common commitment vector")
    print("- complaint and dispute resolution")
    print("- authenticated participant messages")


if __name__ == "__main__":
    main()
