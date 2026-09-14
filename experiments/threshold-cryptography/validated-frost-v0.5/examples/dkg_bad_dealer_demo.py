"""Example 17: exclude one dealer during hidden VSS qualification."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.pedersen import PedersenShare


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="dkg-example-bad-dealer")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(210 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]

    # Dealer 2 gives participant 1 a changed secret component and never repairs
    # it.  The other dealer sessions are independent and remain usable.
    received = list(packages[1].distribution.shares)
    honest = received[0]
    received[0] = PedersenShare(
        honest.x,
        honest.value + 1,
        honest.blinding,
    )
    result = dkg.run(packages, received_overrides={2: received})

    print("Dealer outcomes:")
    for outcome in dkg.outcomes:
        print(
            f"  dealer {outcome.dealer_id}: "
            f"qualified={outcome.qualified}, reason={outcome.reason}"
        )
    print("Common qualified set:", result.qualified_dealers)
    print("Final DKG state:", dkg.state.value)
    print("All aggregate key shares verify:", all(
        verification.accepted for verification in result.verify_all()
    ))


if __name__ == "__main__":
    main()
