"""Small educational building blocks for threshold cryptography.

Version 0.5 contains the Version 0.1 mathematical foundation, the Version 0.2
Feldman layer, Version 0.3 Pedersen VSS/session state, the Version 0.4 offline
multi-dealer DKG simulator, and a two-round educational FROST signing model.

The package is designed for study and experiments.  It is not a production
cryptographic library.
"""

if __package__:
    from .additive import AdditiveSecret, additive_reconstruct, additive_share
    from .field import decode_signed, encode_signed, inverse
    from .dkg import (
        DealerOutcome,
        DKGAbortError,
        DKGDealerCommitments,
        DKGDealerPackage,
        DKGDealerRecord,
        DKGParticipantShare,
        DKGResult,
        DKGShareVerification,
        DKGState,
        DKGTranscript,
        MultiDealerDKG,
        QualificationDisagreementError,
    )
    from .feldman import (
        FeldmanCommitments,
        FeldmanDistribution,
        FeldmanParameters,
        FeldmanVSS,
        ShareVerification,
        VerificationReport,
        VerifiedReconstruction,
    )
    from .frost import (
        FrostAbortError,
        FrostCoordinator,
        FrostError,
        FrostGroupInfo,
        FrostSignature,
        FrostSignatureShare,
        FrostSignatureShareVerification,
        FrostSigner,
        FrostSigningPackage,
        FrostSigningResult,
        FrostSigningRun,
        FrostSigningTranscript,
        FrostVerifyingShare,
        MessageRejectedError,
        NonceCommitment,
        NonceReuseError,
        ToyFROSTSuite,
        compute_binding_factors,
        compute_challenge,
        compute_group_commitment,
        derive_interpolating_value,
        encode_group_commitment_list,
        run_frost_signing,
        verify_schnorr_signature,
    )
    from .mpc import BeaverTriple, beaver_multiply, generate_beaver_triple
    from .pedersen import (
        PedersenCommitments,
        PedersenDistribution,
        PedersenParameters,
        PedersenShare,
        PedersenShareVerification,
        PedersenVerificationReport,
        PedersenVerifiedReconstruction,
        PedersenVSS,
    )
    from .packed import PackedRampScheme, PackedSharing
    from .polynomial import evaluate, interpolate
    from .robust import RobustResult, check_consistency, robust_reconstruct
    from .shamir import Share, ShamirScheme, Sharing
    from .vss_session import (
        BroadcastEquivocationError,
        Complaint,
        DealerResponse,
        ParticipantStatus,
        ReliableCommitmentBoard,
        SessionState,
        SessionTranscript,
        VSSSession,
    )
else:
    # This branch exists only so ``python __init__.py`` gives a useful result
    # when the learner runs every file individually from this folder.
    from additive import AdditiveSecret, additive_reconstruct, additive_share
    from field import decode_signed, encode_signed, inverse
    from dkg import (
        DealerOutcome,
        DKGAbortError,
        DKGDealerCommitments,
        DKGDealerPackage,
        DKGDealerRecord,
        DKGParticipantShare,
        DKGResult,
        DKGShareVerification,
        DKGState,
        DKGTranscript,
        MultiDealerDKG,
        QualificationDisagreementError,
    )
    from feldman import (
        FeldmanCommitments,
        FeldmanDistribution,
        FeldmanParameters,
        FeldmanVSS,
        ShareVerification,
        VerificationReport,
        VerifiedReconstruction,
    )
    from frost import (
        FrostAbortError,
        FrostCoordinator,
        FrostError,
        FrostGroupInfo,
        FrostSignature,
        FrostSignatureShare,
        FrostSignatureShareVerification,
        FrostSigner,
        FrostSigningPackage,
        FrostSigningResult,
        FrostSigningRun,
        FrostSigningTranscript,
        FrostVerifyingShare,
        MessageRejectedError,
        NonceCommitment,
        NonceReuseError,
        ToyFROSTSuite,
        compute_binding_factors,
        compute_challenge,
        compute_group_commitment,
        derive_interpolating_value,
        encode_group_commitment_list,
        run_frost_signing,
        verify_schnorr_signature,
    )
    from mpc import BeaverTriple, beaver_multiply, generate_beaver_triple
    from pedersen import (
        PedersenCommitments,
        PedersenDistribution,
        PedersenParameters,
        PedersenShare,
        PedersenShareVerification,
        PedersenVerificationReport,
        PedersenVerifiedReconstruction,
        PedersenVSS,
    )
    from packed import PackedRampScheme, PackedSharing
    from polynomial import evaluate, interpolate
    from robust import RobustResult, check_consistency, robust_reconstruct
    from shamir import Share, ShamirScheme, Sharing
    from vss_session import (
        BroadcastEquivocationError,
        Complaint,
        DealerResponse,
        ParticipantStatus,
        ReliableCommitmentBoard,
        SessionState,
        SessionTranscript,
        VSSSession,
    )

__all__ = [
    "AdditiveSecret",
    "BeaverTriple",
    "BroadcastEquivocationError",
    "Complaint",
    "DealerResponse",
    "DealerOutcome",
    "DKGAbortError",
    "DKGDealerCommitments",
    "DKGDealerPackage",
    "DKGDealerRecord",
    "DKGParticipantShare",
    "DKGResult",
    "DKGShareVerification",
    "DKGState",
    "DKGTranscript",
    "FeldmanCommitments",
    "FeldmanDistribution",
    "FeldmanParameters",
    "FeldmanVSS",
    "FrostAbortError",
    "FrostCoordinator",
    "FrostError",
    "FrostGroupInfo",
    "FrostSignature",
    "FrostSignatureShare",
    "FrostSignatureShareVerification",
    "FrostSigner",
    "FrostSigningPackage",
    "FrostSigningResult",
    "FrostSigningRun",
    "FrostSigningTranscript",
    "FrostVerifyingShare",
    "MessageRejectedError",
    "NonceCommitment",
    "NonceReuseError",
    "PackedRampScheme",
    "PackedSharing",
    "ParticipantStatus",
    "MultiDealerDKG",
    "PedersenCommitments",
    "PedersenDistribution",
    "PedersenParameters",
    "PedersenShare",
    "PedersenShareVerification",
    "PedersenVerificationReport",
    "PedersenVerifiedReconstruction",
    "PedersenVSS",
    "ReliableCommitmentBoard",
    "QualificationDisagreementError",
    "Share",
    "ShareVerification",
    "ShamirScheme",
    "Sharing",
    "SessionState",
    "SessionTranscript",
    "ToyFROSTSuite",
    "VSSSession",
    "VerificationReport",
    "VerifiedReconstruction",
    "additive_reconstruct",
    "additive_share",
    "beaver_multiply",
    "check_consistency",
    "compute_binding_factors",
    "compute_challenge",
    "compute_group_commitment",
    "decode_signed",
    "encode_signed",
    "encode_group_commitment_list",
    "evaluate",
    "derive_interpolating_value",
    "interpolate",
    "inverse",
    "generate_beaver_triple",
    "robust_reconstruct",
    "run_frost_signing",
    "verify_schnorr_signature",
    "RobustResult",
]

__version__ = "0.5.0"


if __name__ == "__main__":
    print("CryptoCave educational secret-sharing package")
    print("Version:", __version__)
    print("Run the individual files in this folder or the scripts in ../examples.")
