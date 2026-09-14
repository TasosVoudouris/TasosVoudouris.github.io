"""Example 12: show why Pedersen generator setup matters."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.field import inverse
from cryptocave_sss.pedersen import PedersenParameters


def main() -> None:
    parameters = PedersenParameters.educational()

    # These tiny teaching parameters satisfy h = g^17.  A secure deployment
    # must arrange that no participant knows the corresponding discrete log.
    relation = 17
    value, blinding = 9, 12
    original = parameters.commit(value, blinding)

    changed_value = value + 1
    changed_blinding = blinding - inverse(relation, 41)
    changed = parameters.commit(changed_value, changed_blinding)

    print("Original opening:", (value, blinding))
    print("Changed opening:", (changed_value % 41, changed_blinding % 41))
    print("Original commitment:", original)
    print("Changed commitment:", changed)
    print("Same commitment?", original == changed)
    print("Conclusion: tiny known-relation parameters are educational only.")


if __name__ == "__main__":
    main()
