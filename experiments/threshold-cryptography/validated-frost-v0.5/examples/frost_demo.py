"""Example 21: perform the two FROST rounds explicitly."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.dkg import MultiDealerDKG
from cryptocave_sss.frost import FrostCoordinator, FrostSigner


def main() -> None:
    # Version 0.4 first creates one public key and five private key shares.
    dkg = MultiDealerDKG.educational(session_id="frost-demo-dkg")
    dealer_packages = [
        dkg.create_dealer_package(i, rng=random.Random(500 + i))
        for i in dkg.shamir.participant_ids
    ]
    dkg_result = dkg.run(dealer_packages)

    # Any threshold-size subset can now sign.  These objects represent three
    # separate share holders even though this lesson runs in one process.
    coordinator = FrostCoordinator.from_dkg(dkg_result)
    signers = [FrostSigner.from_dkg(dkg_result, i) for i in (1, 3, 5)]

    # Round 1: each signer keeps two nonce scalars private and publishes only
    # the two corresponding group commitments.
    commitments = [
        signer.commit(
            "frost-demo-signing",
            1,
            random.Random(700 + signer.participant_id).randbytes,
        )
        for signer in signers
    ]

    # The coordinator sorts and validates the commitments, then binds them to
    # the exact session, counter, purpose, DKG output, signer set, and payload.
    package = coordinator.create_signing_package(
        session_id="frost-demo-signing",
        counter=1,
        application_context="CryptoCave release approval",
        message=b"approve CryptoCave Version 0.5",
        commitments=commitments,
    )

    # Round 2: each signer validates the same package and emits one scalar z_i.
    signature_shares = [signer.sign(package) for signer in signers]
    for signature_share in signature_shares:
        check = coordinator.verify_signature_share(package, signature_share)
        print(
            f"participant {signature_share.participant_id}: "
            f"z_i={signature_share.value:2d}, valid={check.accepted}"
        )

    # Aggregation verifies all z_i values, sums them, and verifies the ordinary
    # Schnorr signature under the one group public key.
    result = coordinator.aggregate(package, signature_shares)
    print("\nSelected signers:", package.participant_ids)
    print("Group public key:", dkg_result.public_key)
    print("Signature (R, z):", result.signature)
    print("Ordinary Schnorr verification:", result.transcript.final_verified)
    print("Signing transcript:", result.transcript.digest)
    print("The group secret was never reconstructed.")


if __name__ == "__main__":
    main()
