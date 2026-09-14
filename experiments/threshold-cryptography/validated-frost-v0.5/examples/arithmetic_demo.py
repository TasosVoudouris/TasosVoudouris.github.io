"""Example 3: local arithmetic and the multiplication-degree problem."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.mpc import beaver_multiply, generate_beaver_triple
from cryptocave_sss.shamir import ShamirScheme


def main() -> None:
    scheme = ShamirScheme(41, 10, 5, rng=random.Random(5))
    x = scheme.share(7)
    y = scheme.share(6)

    print("x + y =", (x + y).reveal((x + y).shares[:5]))
    print("x - y =", (x - y).reveal((x - y).shares[:5]))

    direct_product = x * y
    print("\nDirect pointwise product degree:", direct_product.degree_bound)
    print("Shares needed to open it:", direct_product.reconstruction_threshold)
    print(
        "7 * 6 modulo 41 =",
        direct_product.reveal_field_element(direct_product.shares[:9]),
    )

    # A trusted dealer makes the triple in this educational demonstration.
    triple = generate_beaver_triple(scheme)
    beaver_product = beaver_multiply(x, y, triple)
    print("\nAfter Beaver multiplication:")
    print("Degree:", beaver_product.degree_bound)
    print("Shares needed:", beaver_product.reconstruction_threshold)
    print("Result modulo 41:", beaver_product.reveal_field_element(beaver_product.shares[:5]))


if __name__ == "__main__":
    main()
