"""Example 20: reconstruct only to audit the educational public key equation."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="dkg-example-audit")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(240 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]
    result = dkg.run(packages)

    selected = [1, 3, 5]
    reconstructed = result.audit_reconstruct_field_element(selected)
    expected_public_key = result.value_parameters.commit(reconstructed)

    print("Audit participants:", selected)
    print("Audit-only reconstructed field element:", reconstructed)
    print("g^x from audit reconstruction:", expected_public_key)
    print("DKG public key:", result.public_key)
    print("Public key equation matches?", expected_public_key == result.public_key)
    print("Normal DKG and threshold-signature operation must not reconstruct x.")


if __name__ == "__main__":
    main()
