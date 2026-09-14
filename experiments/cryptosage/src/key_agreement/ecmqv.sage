"""Explicit-state ECMQV study with two-sided key confirmation."""

import hashlib
import hmac


def mqv_key_pair(base_point=P, subgroup_order=n):
    """Generate one static or ephemeral MQV key pair."""

    private_scalar = Integer(randint(1, subgroup_order - 1))
    return private_scalar, private_scalar * base_point


def mqv_shared_point(
    own_static_private,
    own_ephemeral_private,
    own_ephemeral_public,
    peer_static_public,
    peer_ephemeral_public,
    base_point=P,
    subgroup_order=n,
    cofactor=h,
    curve=E,
):
    """Compute one party's ECMQV shared point."""

    for point in (
        own_ephemeral_public,
        peer_static_public,
        peer_ephemeral_public,
    ):
        if not validate_subgroup_point(point, curve, subgroup_order):
            raise ValueError("invalid MQV public point")

    own_reduction = point_hat(own_ephemeral_public, subgroup_order)
    peer_reduction = point_hat(peer_ephemeral_public, subgroup_order)
    combined_private = (
        Integer(own_ephemeral_private)
        + own_reduction * Integer(own_static_private)
    ) % subgroup_order
    peer_combined_public = (
        peer_ephemeral_public + peer_reduction * peer_static_public
    )
    shared_point = Integer(cofactor) * combined_private * peer_combined_public
    if shared_point.is_zero():
        raise ValueError("MQV produced the point at infinity")
    return shared_point


def mqv_confirmation_key(
    shared_point,
    alice_static,
    bob_static,
    alice_ephemeral,
    bob_ephemeral,
    curve=E,
):
    """Derive a transcript-bound confirmation key from the shared point."""

    coordinate_size = coordinate_size_bytes(curve)
    shared_x, _ = shared_point.xy()
    transcript = b"".join(
        point_to_bytes(point, coordinate_size)
        for point in (
            alice_static,
            bob_static,
            alice_ephemeral,
            bob_ephemeral,
        )
    )
    key = kdf(
        i2osp(shared_x, coordinate_size),
        32,
        b"CryptoSage-ECMQV|" + transcript,
    )
    return key, transcript


def mqv_exchange_demo():
    """Execute both ECMQV calculations and return inspectable result data."""

    alice_static_private, alice_static_public = mqv_key_pair()
    bob_static_private, bob_static_public = mqv_key_pair()
    alice_ephemeral_private, alice_ephemeral_public = mqv_key_pair()
    bob_ephemeral_private, bob_ephemeral_public = mqv_key_pair()

    alice_shared = mqv_shared_point(
        alice_static_private,
        alice_ephemeral_private,
        alice_ephemeral_public,
        bob_static_public,
        bob_ephemeral_public,
    )
    bob_shared = mqv_shared_point(
        bob_static_private,
        bob_ephemeral_private,
        bob_ephemeral_public,
        alice_static_public,
        alice_ephemeral_public,
    )
    if alice_shared != bob_shared:
        raise AssertionError("the two ECMQV shared points differ")

    alice_key, transcript = mqv_confirmation_key(
        alice_shared,
        alice_static_public,
        bob_static_public,
        alice_ephemeral_public,
        bob_ephemeral_public,
    )
    bob_key, _ = mqv_confirmation_key(
        bob_shared,
        alice_static_public,
        bob_static_public,
        alice_ephemeral_public,
        bob_ephemeral_public,
    )
    bob_tag = hmac.new(
        bob_key, b"bob-confirmation|" + transcript, hashlib.sha256
    ).digest()
    alice_accepts = hmac.compare_digest(
        bob_tag,
        hmac.new(
            alice_key, b"bob-confirmation|" + transcript, hashlib.sha256
        ).digest(),
    )
    alice_tag = hmac.new(
        alice_key, b"alice-confirmation|" + transcript, hashlib.sha256
    ).digest()
    bob_accepts = hmac.compare_digest(
        alice_tag,
        hmac.new(
            bob_key, b"alice-confirmation|" + transcript, hashlib.sha256
        ).digest(),
    )
    return {
        "shared_point": alice_shared,
        "keys_equal": alice_key == bob_key,
        "alice_accepts": alice_accepts,
        "bob_accepts": bob_accepts,
    }

