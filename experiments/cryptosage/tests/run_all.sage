"""Assertion-based checks for the reviewed CryptoSage demonstrations."""

print("[1/8] RSA key arithmetic")
load("src/integer_factorization/rsa_keygen.sage")
rsa_public, rsa_private = rsa_keygen(prime_bits=64)
rsa_n, rsa_e = rsa_public
rsa_p, rsa_q, rsa_d = rsa_private
assert rsa_p != rsa_q
assert gcd(rsa_e, (rsa_p - 1) * (rsa_q - 1)) == 1
sample_message = Integer(42)
assert power_mod(power_mod(sample_message, rsa_e, rsa_n), rsa_d, rsa_n) == sample_message

print("[2/8] Paillier encryption and homomorphism")
load("src/integer_factorization/paillier.sage")
paillier_public, paillier_private = paillier_keygen(prime_bits=64)
message_1 = Integer(17)
message_2 = Integer(29)
ciphertext_1 = paillier_encrypt(message_1, paillier_public)
ciphertext_2 = paillier_encrypt(message_2, paillier_public)
assert paillier_decrypt(ciphertext_1, paillier_public, paillier_private) == message_1
assert paillier_decrypt(ciphertext_2, paillier_public, paillier_private) == message_2
ciphertext_sum = paillier_ciphertext_add(ciphertext_1, ciphertext_2, paillier_public)
assert paillier_decrypt(ciphertext_sum, paillier_public, paillier_private) == message_1 + message_2

print("[3/8] Curve parameter seed consistency")
load("src/foundations/digest.sage")
load("src/foundations/math_helpers.sage")
load("src/elliptic_curves/curve_generation.sage")
small_prime = Integer(2) ** 31 - 1
seed, curve_a, curve_b = ecc_curve_gen(small_prime)
assert verify_ecc_curve(small_prime, seed, curve_a, curve_b)
assert not verify_ecc_curve(small_prime, seed, curve_a, (curve_b + 1) % small_prime)

print("[4/8] ECDSA and EC-KCDSA signatures")
load("src/elliptic_curves/curves/prime192v1.sage")
load("src/elliptic_curves/key_generation.sage")
load("src/elliptic_curves/ecdsa.sage")
load("src/elliptic_curves/eckcdsa.sage")
ec_public, ec_private = ec_keygen()
signature_r, signature_s = ecdsa_sign(ec_private, b"test message")
assert ecdsa_verify(ec_public, b"test message", signature_r, signature_s)
assert not ecdsa_verify(ec_public, b"changed message", signature_r, signature_s)
kcdsa_public, kcdsa_private = eckcdsa_keygen()
kcdsa_r, kcdsa_s = eckcdsa_sign(
    kcdsa_private, b"test message", b"certificate context"
)
assert eckcdsa_verify(
    kcdsa_public,
    b"test message",
    kcdsa_r,
    kcdsa_s,
    b"certificate context",
)
assert not eckcdsa_verify(
    kcdsa_public,
    b"changed message",
    kcdsa_r,
    kcdsa_s,
    b"certificate context",
)

print("[5/8] ECIES and PSEC authenticated encryption")
load("src/elliptic_curves/ecies.sage")
load("src/elliptic_curves/psec.sage")
plaintext = b"authenticated encryption test"
ecies_point, ecies_body, ecies_tag = ecies_encrypt(ec_public, plaintext)
assert ecies_decrypt(ecies_point, ecies_body, ecies_tag, ec_private) == plaintext
tampered_ecies_tag = ecies_tag[:-1] + bytes([ecies_tag[-1] ^ 1])
try:
    ecies_decrypt(ecies_point, ecies_body, tampered_ecies_tag, ec_private)
    raise AssertionError("tampered ECIES tag was accepted")
except ValueError:
    pass
psec_point, psec_body, psec_seed, psec_tag = psec_encrypt(ec_public, plaintext)
assert psec_decrypt(
    psec_point, psec_body, psec_seed, psec_tag, ec_private
) == plaintext

print("[6/8] ECMQV shared point and confirmation")
load("src/key_agreement/ecmqv.sage")
mqv_result = mqv_exchange_demo()
assert mqv_result["keys_equal"]
assert mqv_result["alice_accepts"] and mqv_result["bob_accepts"]

print("[7/8] STS-inspired key confirmation")
load("src/key_agreement/sts_key_confirmation.sage")
sts_result = sts_key_confirmation_demo()
assert sts_result["keys_equal"]
assert sts_result["responder_accepts"]
assert not sts_result["authenticated_peer_identity"]

print("[8/8] Small Miller-function example")
load("src/pairings/miller_pairing_demo.sage")
pairing_value = pairing_quotient_demo()
assert pairing_value == PAIRING_FIELD(473)

print("All reviewed CryptoSage checks passed.")
