"""Example 4: detect and correct corrupted Shamir shares."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.robust import check_consistency, robust_reconstruct
from cryptocave_sss.shamir import Share, ShamirScheme


def main() -> None:
    scheme = ShamirScheme(41, 10, 5, rng=random.Random(6))
    sharing = scheme.share(12)

    received = list(sharing.shares)
    received[1] = Share(received[1].x, (received[1].y + 3) % 41)
    received[7] = Share(received[7].x, (received[7].y + 5) % 41)

    print("All shares consistent?", check_consistency(scheme, received))
    result = robust_reconstruct(scheme, received, max_errors=2)
    print("Recovered secret:", result.secret)
    print("Rejected participant IDs:", [share.x for share in result.rejected_shares])

    print(
        "\nWhy correction is possible: for threshold 5 and two errors, "
        "the bound requires at least 5 + 2*2 = 9 received shares. We have 10."
    )


if __name__ == "__main__":
    main()
