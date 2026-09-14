"""STS-inspired ephemeral ECDH key-confirmation study.

This is deliberately not called a Station-to-Station implementation: it has no
long-term signing keys and therefore does not authenticate peer identities.
"""

import hashlib
import hmac


def _confirmation_material(shared_point, initiator_point, responder_point, curve):
    coordinate_size = coordinate_size_bytes(curve)
    shared_x, _ = shared_point.xy()
    transcript = (
        point_to_bytes(initiator_point, coordinate_size)
        + point_to_bytes(responder_point, coordinate_size)
    )
    key = kdf(
        i2osp(shared_x, coordinate_size),
        32,
        b"CryptoSage-STS-inspired|" + transcript,
    )
    return key, transcript


def sts_initiator_start(base_point=P, subgroup_order=n):
    """Create the initiator's ephemeral state and outbound point."""

    private_scalar = Integer(randint(1, subgroup_order - 1))
    public_point = private_scalar * base_point
    return {"private": private_scalar, "public": public_point}


def sts_responder_reply(
    initiator_point,
    base_point=P,
    subgroup_order=n,
    cofactor=h,
    curve=E,
):
    """Create the responder point and its direction-separated confirmation tag."""

    if not validate_subgroup_point(initiator_point, curve, subgroup_order):
        raise ValueError("invalid initiator point")
    private_scalar = Integer(randint(1, subgroup_order - 1))
    responder_point = private_scalar * base_point
    shared_point = Integer(cofactor) * private_scalar * initiator_point
    key, transcript = _confirmation_material(
        shared_point, initiator_point, responder_point, curve
    )
    tag = hmac.new(
        key, b"responder|" + transcript, hashlib.sha256
    ).digest()
    state = {
        "key": key,
        "transcript": transcript,
        "responder_point": responder_point,
    }
    return responder_point, tag, state


def sts_initiator_finish(
    initiator_state,
    responder_point,
    responder_tag,
    subgroup_order=n,
    cofactor=h,
    curve=E,
):
    """Verify the responder tag and return the initiator confirmation tag."""

    if not validate_subgroup_point(responder_point, curve, subgroup_order):
        raise ValueError("invalid responder point")
    shared_point = (
        Integer(cofactor)
        * Integer(initiator_state["private"])
        * responder_point
    )
    key, transcript = _confirmation_material(
        shared_point, initiator_state["public"], responder_point, curve
    )
    expected = hmac.new(
        key, b"responder|" + transcript, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(expected, responder_tag):
        raise ValueError("responder key confirmation failed")
    initiator_tag = hmac.new(
        key, b"initiator|" + transcript, hashlib.sha256
    ).digest()
    return initiator_tag, key


def sts_responder_finish(responder_state, initiator_tag):
    """Return whether the initiator proved possession of the same ECDH key."""

    expected = hmac.new(
        responder_state["key"],
        b"initiator|" + responder_state["transcript"],
        hashlib.sha256,
    ).digest()
    return hmac.compare_digest(expected, initiator_tag)


def sts_key_confirmation_demo():
    """Run the full unauthenticated ECDH key-confirmation flow."""

    initiator_state = sts_initiator_start()
    responder_point, responder_tag, responder_state = sts_responder_reply(
        initiator_state["public"]
    )
    initiator_tag, initiator_key = sts_initiator_finish(
        initiator_state, responder_point, responder_tag
    )
    responder_accepts = sts_responder_finish(responder_state, initiator_tag)
    return {
        "keys_equal": initiator_key == responder_state["key"],
        "responder_accepts": responder_accepts,
        "authenticated_peer_identity": False,
    }

