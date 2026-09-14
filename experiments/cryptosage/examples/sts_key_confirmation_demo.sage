"""Run the STS-inspired, unauthenticated ECDH key-confirmation study."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/key_agreement/sts_key_confirmation.sage")

result = sts_key_confirmation_demo()
print("Shared keys equal:", result["keys_equal"])
print("Responder accepts confirmation:", result["responder_accepts"])
print("Peer identity authenticated:", result["authenticated_peer_identity"])

