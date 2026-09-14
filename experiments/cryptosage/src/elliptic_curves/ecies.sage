"""Reviewed ECIES-style hybrid-encryption demonstration."""

import hashlib
import hmac


def _ecies_key_material(shared_point, ephemeral_point, curve):
    """Derive independent AES and HMAC keys from the shared EC point."""

    coordinate_size = coordinate_size_bytes(curve)
    shared_x, _ = shared_point.xy()
    secret = i2osp(shared_x, coordinate_size)
    context = b"CryptoSage-ECIES|" + point_to_bytes(
        ephemeral_point, coordinate_size
    )
    material = kdf(secret, 64, context)
    return material[:32], material[32:], context


def ecies_encrypt(
    public_key,
    message,
    base_point=P,
    subgroup_order=n,
    cofactor=h,
    curve=E,
):
    """Encrypt bytes and return ``(R, iv || ciphertext, tag)``."""

    require_pycryptodome()
    if not validate_subgroup_point(public_key, curve, subgroup_order):
        raise ValueError("invalid recipient public key")

    nonce = Integer(randint(1, subgroup_order - 1))
    ephemeral_point = nonce * base_point
    shared_point = Integer(cofactor) * nonce * public_key
    if shared_point.is_zero():
        raise ValueError("invalid all-zero ECIES shared point")

    encryption_key, mac_key, context = _ecies_key_material(
        shared_point, ephemeral_point, curve
    )
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv=iv)
    encrypted_body = iv + cipher.encrypt(pkcs7_pad(message, AES.block_size))
    tag = hmac.new(
        mac_key, context + encrypted_body, hashlib.sha256
    ).digest()
    return ephemeral_point, encrypted_body, tag


def ecies_decrypt(
    ephemeral_point,
    encrypted_body,
    tag,
    private_key,
    subgroup_order=n,
    cofactor=h,
    curve=E,
):
    """Authenticate and decrypt an ECIES-style ciphertext."""

    require_pycryptodome()
    private_key = Integer(private_key)
    if private_key < 1 or private_key >= subgroup_order:
        raise ValueError("invalid ECIES private key")
    if not validate_subgroup_point(ephemeral_point, curve, subgroup_order):
        raise ValueError("invalid ephemeral point")
    if len(encrypted_body) < 2 * AES.block_size:
        raise ValueError("ECIES ciphertext body is too short")

    shared_point = Integer(cofactor) * private_key * ephemeral_point
    encryption_key, mac_key, context = _ecies_key_material(
        shared_point, ephemeral_point, curve
    )
    expected_tag = hmac.new(
        mac_key, context + encrypted_body, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(expected_tag, tag):
        raise ValueError("ECIES authentication failed")

    iv = encrypted_body[: AES.block_size]
    ciphertext = encrypted_body[AES.block_size :]
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv=iv)
    return pkcs7_unpad(cipher.decrypt(ciphertext), AES.block_size)

