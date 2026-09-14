"""Run every active example in its intended learning order."""

import importlib
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


EXAMPLES = [
    "additive_demo",
    "shamir_demo",
    "arithmetic_demo",
    "robust_demo",
    "packed_demo",
    "ntt_demo",
    "feldman_demo",
    "feldman_tampering_demo",
    "feldman_leakage_demo",
    "pedersen_demo",
    "pedersen_hiding_demo",
    "pedersen_toy_trapdoor_demo",
    "vss_session_demo",
    "vss_complaint_demo",
    "vss_abort_demo",
    "dkg_demo",
    "dkg_bad_dealer_demo",
    "dkg_extraction_abort_demo",
    "dkg_qualification_abort_demo",
    "dkg_audit_demo",
    "frost_demo",
    "frost_simple_api_demo",
    "frost_nonce_reuse_demo",
    "frost_bad_share_demo",
    "frost_context_binding_demo",
    "frost_message_policy_demo",
]


def main() -> None:
    for name in EXAMPLES:
        print("\n" + "=" * 72)
        print(name)
        print("=" * 72)
        module = importlib.import_module(f"examples.{name}")
        module.main()


if __name__ == "__main__":
    main()
