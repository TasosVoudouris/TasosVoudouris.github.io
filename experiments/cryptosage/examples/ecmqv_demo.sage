"""Run both sides of the explicit-state ECMQV study."""

load("src/elliptic_curves/curves/prime192v1.sage")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/key_agreement/ecmqv.sage")

result = mqv_exchange_demo()
print("Shared keys equal:", result["keys_equal"])
print("Alice accepts Bob's confirmation:", result["alice_accepts"])
print("Bob accepts Alice's confirmation:", result["bob_accepts"])

