"""Example 26: a signer validates application content before signing."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import (
    FrostCoordinator,
    FrostSigner,
    MessageRejectedError,
)


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="message-policy-dkg")
    result = dkg.run(
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    )

    # This small policy stands in for real transaction, authorization, or
    # document validation.  It examines the application payload, not a digest.
    def permits_release(package) -> bool:
        return package.message.startswith(b"APPROVED:")

    coordinator = FrostCoordinator.from_dkg(result)
    signers = [
        FrostSigner.from_dkg(
            result,
            i,
            message_validator=permits_release if i == 1 else None,
        )
        for i in (1, 2, 3)
    ]
    commitments = [
        signer.commit(
            "message-policy-signing",
            1,
            random.Random(1_200 + signer.participant_id).randbytes,
        )
        for signer in signers
    ]
    package = coordinator.create_signing_package(
        session_id="message-policy-signing",
        counter=1,
        application_context="CryptoCave release policy",
        message=b"DENIED: release artifact",
        commitments=commitments,
    )
    try:
        signers[0].sign(package)
    except MessageRejectedError as error:
        print("Participant 1 refused to sign:", error)
        print("Its nonce pair was deleted:", signers[0].pending_nonce_count == 0)


if __name__ == "__main__":
    main()
