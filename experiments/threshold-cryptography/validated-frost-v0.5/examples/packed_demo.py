"""Example 5: the three-secret packed ramp scheme from the old fft.py."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.packed import PackedRampScheme


def main() -> None:
    scheme = PackedRampScheme.original_parameters(random.Random(7))
    sharing = scheme.share([10, 20, 30])

    print("Packed secrets: [10, 20, 30]")
    print("Number of output shares:", len(sharing.shares))
    print("Perfect-privacy coalition size:", scheme.privacy_threshold)
    print("Reconstruction threshold:", scheme.reconstruction_threshold)
    print("Recovered from seven shares:", sharing.reveal(sharing.shares[:7]))

    print("\nExact information learned by coalitions:")
    for size in range(4, 8):
        coalition = [share.x for share in sharing.shares[:size]]
        dimension = scheme.coalition_leakage_dimension(coalition)
        print(f"  {size} shares learn {dimension} independent secret relation(s)")


if __name__ == "__main__":
    main()
