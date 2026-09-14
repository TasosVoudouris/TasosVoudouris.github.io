"""Reviewed PSEC-style elliptic-curve encryption demonstration.

The algebraic transform follows the supplied educational source, while the
symmetric layer uses explicit AES-CBC, PKCS#7, and HMAC-SHA-256.
"""

import hashlib
import hmac


def _psec_seed_material(seed, coordinate_size):
    seed_bytes = i2osp(seed, coordinate_size)
    return kdf(seed_bytes, 96, b"CryptoSage-PSEC-seed")


def _psec_point_mask(ephemeral_point, shared_point, coordinate_size):
    ephemeral_bytes = point_to_bytes(ephemeral_point, coordinate_size)
    shared_bytes = point_to_bytes(shared_point, coordinate_size)
    mask = kdf(ephemeral_bytes, coordinate_size, shared_bytes)
    return Integer(int.from_bytes(mask, byteorder="big"))


def psec_encrypt(
    public_key,
    message,
    base_point=P,
    subgroup_order=n,
    curve=E,
):
    """Return the PSEC-style tuple ``(R, iv || ciphertext, s, tag)``."""

    require_pycryptodome()
    if not validate_subgroup_point(public_key, curve, subgroup_order):
        raise ValueError("invalid recipient public key")
    coordinate_size = coordinate_size_bytes(curve)

    # A rare zero derived scalar is handled by resampling the seed.
    while True:
        seed = Integer(randint(1, subgroup_order - 1))
        material = _psec_seed_material(seed, coordinate_size)
        ephemeral_scalar = Integer(
            int.from_bytes(material[:32], byteorder="big") % subgroup_order
        )
        if ephemeral_scalar != 0:
            break

    encryption_key = material[32:64]
    mac_key = material[64:96]
    ephemeral_point = ephemeral_scalar * base_point
    shared_point = ephemeral_scalar * public_key
    mask = _psec_point_mask(ephemeral_point, shared_point, coordinate_size)
    masked_seed = xor_integers(seed, mask)

    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv=iv)
    encrypted_body = iv + cipher.encrypt(pkcs7_pad(message, AES.block_size))
    transcript = (
        point_to_bytes(ephemeral_point, coordinate_size)
        + i2osp(masked_seed, coordinate_size)
        + encrypted_body
    )
    tag = hmac.new(mac_key, transcript, hashlib.sha256).digest()
    return ephemeral_point, encrypted_body, masked_seed, tag


def psec_decrypt(
    ephemeral_point,
    encrypted_body,
    masked_seed,
    tag,
    private_key,
    subgroup_order=n,
    base_point=P,
    curve=E,
):
    """Validate, authenticate, and decrypt a PSEC-style ciphertext."""

    require_pycryptodome()
    private_key = Integer(private_key)
    if private_key < 1 or private_key >= subgroup_order:
        raise ValueError("invalid PSEC private key")
    if not validate_subgroup_point(ephemeral_point, curve, subgroup_order):
        raise ValueError("invalid PSEC ephemeral point")
    if len(encrypted_body) < 2 * AES.block_size:
        raise ValueError("PSEC ciphertext body is too short")

    coordinate_size = coordinate_size_bytes(curve)
    shared_point = private_key * ephemeral_point
    mask = _psec_point_mask(ephemeral_point, shared_point, coordinate_size)
    seed = xor_integers(Integer(masked_seed), mask)
    if seed < 1 or seed >= subgroup_order:
        raise ValueError("invalid recovered PSEC seed")

    material = _psec_seed_material(seed, coordinate_size)
    ephemeral_scalar = Integer(
        int.from_bytes(material[:32], byteorder="big") % subgroup_order
    )
    if ephemeral_scalar == 0 or ephemeral_scalar * base_point != ephemeral_point:
        raise ValueError("PSEC ephemeral point consistency check failed")

    encryption_key = material[32:64]
    mac_key = material[64:96]
    transcript = (
        point_to_bytes(ephemeral_point, coordinate_size)
        + i2osp(masked_seed, coordinate_size)
        + encrypted_body
    )
    expected_tag = hmac.new(mac_key, transcript, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_tag, tag):
        raise ValueError("PSEC authentication failed")

    iv = encrypted_body[: AES.block_size]
    ciphertext = encrypted_body[AES.block_size :]
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv=iv)
    return pkcs7_unpad(cipher.decrypt(ciphertext), AES.block_size)

