"""Example 25: inspect the exact application envelope that is signed."""

import random
import sys
from dataclasses import replace
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import FrostCoordinator, FrostSigner, run_frost_signing


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="context-binding-dkg")
    result = dkg.run(
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    )
    coordinator = FrostCoordinator.from_dkg(result)
    signers = [FrostSigner.from_dkg(result, i) for i in (1, 2, 3)]
    run = run_frost_signing(
        coordinator,
        signers,
        session_id="context-binding-signing",
        counter=1,
        application_context="CryptoCave model-release approval",
        message=b"release model artifact 7",
        random_byte_sources={
            i: random.Random(1_100 + i).randbytes for i in (1, 2, 3)
        },
    )

    changed = replace(run.package, message=b"release model artifact 8")
    print("Original package verifies:", coordinator.verify_final(run.package, run.result.signature))
    print("Changed package verifies:", coordinator.verify_final(changed, run.result.signature))
    print("Raw payload bytes:", run.package.message)
    print("Bound message length:", len(run.package.message_to_sign(coordinator.group_info.suite)))
    print("Bound fields include the session, counter, context, DKG, signer set, and payload.")


if __name__ == "__main__":
    main()
