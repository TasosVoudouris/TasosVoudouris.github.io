"""Example 22: use the small convenience function for both FROST rounds."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import FrostCoordinator, FrostSigner, run_frost_signing


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="frost-simple-dkg")
    dkg_result = dkg.run(
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    )
    coordinator = FrostCoordinator.from_dkg(dkg_result)
    signers = [FrostSigner.from_dkg(dkg_result, i) for i in (2, 4, 5)]

    run = run_frost_signing(
        coordinator,
        signers,
        session_id="frost-simple-signing",
        counter=1,
        application_context="CryptoCave document approval",
        message=b"publish the reviewed threshold-signature chapter",
        random_byte_sources={
            i: random.Random(800 + i).randbytes for i in (2, 4, 5)
        },
    )

    print("Package digest:", run.package.digest)
    print("Participants:", run.package.participant_ids)
    print("Signature:", run.result.signature)
    print("Verified:", run.result.transcript.final_verified)


if __name__ == "__main__":
    main()
