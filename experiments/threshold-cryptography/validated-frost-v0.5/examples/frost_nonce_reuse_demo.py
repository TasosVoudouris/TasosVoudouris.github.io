"""Example 23: show that a round-one nonce pair can be used only once."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import FrostCoordinator, FrostSigner, NonceReuseError


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="nonce-reuse-dkg")
    result = dkg.run(
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    )
    coordinator = FrostCoordinator.from_dkg(result)
    signers = [FrostSigner.from_dkg(result, i) for i in (1, 2, 3)]
    commitments = [
        signer.commit(
            "nonce-reuse-signing",
            1,
            random.Random(900 + signer.participant_id).randbytes,
        )
        for signer in signers
    ]
    package = coordinator.create_signing_package(
        session_id="nonce-reuse-signing",
        counter=1,
        application_context="CryptoCave nonce lesson",
        message=b"each nonce pair signs exactly one package",
        commitments=commitments,
    )

    first_share = signers[0].sign(package)
    print("First response:", first_share)
    print("Pending nonce pairs after signing:", signers[0].pending_nonce_count)
    try:
        signers[0].sign(package)
    except NonceReuseError as error:
        print("Second attempt rejected:", error)


if __name__ == "__main__":
    main()
