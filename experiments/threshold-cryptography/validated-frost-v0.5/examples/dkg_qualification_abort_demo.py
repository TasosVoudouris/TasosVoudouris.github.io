"""Example 19: abort when participants disagree on the qualified set."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import (
    MultiDealerDKG,
    QualificationDisagreementError,
)


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="dkg-example-view-abort")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(230 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]
    views = {
        participant_id: (1, 2, 3, 4, 5)
        for participant_id in dkg.shamir.participant_ids
    }
    views[5] = (2, 3, 4, 5)

    try:
        dkg.run(packages, qualification_views=views)
    except QualificationDisagreementError as error:
        print("Participant 1 view:", views[1])
        print("Participant 5 view:", views[5])
        print("Final DKG state:", dkg.state.value)
        print("Reason:", error)


if __name__ == "__main__":
    main()
