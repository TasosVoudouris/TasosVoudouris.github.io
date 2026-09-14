"""Example 18: abort when a qualified dealer fails public-key extraction."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import DKGAbortError, MultiDealerDKG
from cryptocave_sss.field import inverse
from cryptocave_sss.pedersen import PedersenShare


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="dkg-example-extraction-abort")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(220 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]

    # The tiny group has h = g^17.  Changing both components this way preserves
    # Pedersen verification, but the secret component no longer matches the
    # dealer's separate value commitment vector.
    received = list(packages[0].distribution.shares)
    honest = received[0]
    received[0] = PedersenShare(
        honest.x,
        honest.value + 1,
        honest.blinding - inverse(17, 41),
    )

    try:
        dkg.run(packages, received_overrides={1: received})
    except DKGAbortError as error:
        outcome = dkg.outcomes[0]
        print("Pedersen qualification passed?", outcome.pedersen_qualified)
        print("Value commitment round passed?", outcome.value_commitments_accepted)
        print("Qualified set was already fixed:", dkg.computed_qualified_dealers)
        print("Final DKG state:", dkg.state.value)
        print("Reason:", error)


if __name__ == "__main__":
    main()
