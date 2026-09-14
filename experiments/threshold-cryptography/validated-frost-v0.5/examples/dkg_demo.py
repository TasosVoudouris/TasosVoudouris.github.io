"""Example 16: complete an honest multi-dealer DKG."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="dkg-example-honest")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(200 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]
    result = dkg.run(packages)

    print("Educational DKG: 3-out-of-5")
    print("Qualified dealers:", result.qualified_dealers)
    print("Group public key:", result.public_key)
    print("Transcript digest:", result.transcript.digest)
    print()
    for share in result.participant_shares:
        verification = result.verify_share(share)
        print(
            f"participant {share.participant_id}: "
            f"private key share={share.secret_share:2d}, "
            f"accepted={verification.accepted}"
        )
    print("\nThe group secret was not reconstructed during this run.")


if __name__ == "__main__":
    main()
