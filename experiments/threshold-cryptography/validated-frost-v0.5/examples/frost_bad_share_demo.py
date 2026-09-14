"""Example 24: identify one invalid signature share and abort."""

import random
import sys
from dataclasses import replace
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import FrostAbortError, FrostCoordinator, FrostSigner


def main() -> None:
    dkg = MultiDealerDKG.educational(session_id="bad-share-dkg")
    result = dkg.run(
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    )
    coordinator = FrostCoordinator.from_dkg(result)
    signers = [FrostSigner.from_dkg(result, i) for i in (1, 2, 3)]
    commitments = [
        signer.commit(
            "bad-share-signing",
            1,
            random.Random(1_000 + signer.participant_id).randbytes,
        )
        for signer in signers
    ]
    package = coordinator.create_signing_package(
        session_id="bad-share-signing",
        counter=1,
        application_context="CryptoCave identifiable-abort lesson",
        message=b"an invalid partial must not reach the final signature",
        commitments=commitments,
    )
    shares = [signer.sign(package) for signer in signers]

    # Simulate participant 2 sending z_2 + 1 instead of z_2.
    q = coordinator.group_info.suite.scalar_modulus
    shares[1] = replace(shares[1], value=(shares[1].value + 1) % q)
    check = coordinator.verify_signature_share(package, shares[1])
    print("Participant 2 accepted:", check.accepted)
    print("Verification equation sides:", check.left, check.right)
    try:
        coordinator.aggregate(package, shares)
    except FrostAbortError as error:
        print("Aggregation aborted:", error)


if __name__ == "__main__":
    main()
