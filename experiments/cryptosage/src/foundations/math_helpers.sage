"""Encoding, KDF, padding, and elliptic-curve validation helpers."""

import hashlib
import hmac

try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except ImportError:
    AES = None
    get_random_bytes = None


def require_pycryptodome():
    """Fail with a useful message when an AES example lacks PyCryptodome."""

    if AES is None or get_random_bytes is None:
        raise ImportError(
            "PyCryptodome is required; install it with "
            "`sage -pip install pycryptodome`."
        )


def i2osp(integer, length):
    """Encode a non-negative integer in exactly ``length`` big-endian bytes."""

    value = Integer(integer)
    if value < 0:
        raise ValueError("I2OSP cannot encode a negative integer")
    if value >= 256 ** length:
        raise ValueError("integer is too large for the requested length")
    return int(value).to_bytes(int(length), byteorder="big")


# Compatibility alias used in the supplied source and in standards literature.
I2OSP = i2osp


def point_to_bytes(point, coordinate_size):
    """Encode an affine EC point as fixed-width ``x || y`` coordinates."""

    if point.is_zero():
        raise ValueError("the point at infinity has no affine encoding here")
    x_coordinate, y_coordinate = point.xy()
    return i2osp(x_coordinate, coordinate_size) + i2osp(
        y_coordinate, coordinate_size
    )


# Compatibility alias for the old helper name.
point2str = point_to_bytes


def xor_integers(left, right):
    """XOR two non-negative integers without using Sage's ``^`` operator."""

    left = Integer(left)
    right = Integer(right)
    if left < 0 or right < 0:
        raise ValueError("XOR inputs must be non-negative")
    # In a .sage file, ^ is preparsed as exponentiation; this identity is XOR.
    return (left | right) - (left & right)


xor = xor_integers


def kdf(secret, output_length, context=b""):
    """Expand ``secret`` with SHA-256 counter mode and explicit context.

    This is a compact educational KDF, not a replacement for standardized HKDF.
    """

    if output_length < 0:
        raise ValueError("output_length must be non-negative")
    secret = to_bytes(secret)
    context = to_bytes(context)
    output = bytearray()
    counter = 1
    while len(output) < output_length:
        block = hashlib.sha256(
            secret + i2osp(counter, 4) + context
        ).digest()
        output.extend(block)
        counter += 1
    return bytes(output[:output_length])


KDF = kdf


def pkcs7_pad(message, block_size=16):
    """Apply PKCS#7 padding to a byte string."""

    message = to_bytes(message)
    padding_length = block_size - (len(message) % block_size)
    return message + bytes([padding_length]) * padding_length


def pkcs7_unpad(padded_message, block_size=16):
    """Validate and remove PKCS#7 padding."""

    if not padded_message or len(padded_message) % block_size != 0:
        raise ValueError("invalid padded message length")
    padding_length = padded_message[-1]
    if padding_length < 1 or padding_length > block_size:
        raise ValueError("invalid PKCS#7 padding length")
    expected = bytes([padding_length]) * padding_length
    if not hmac.compare_digest(padded_message[-padding_length:], expected):
        raise ValueError("invalid PKCS#7 padding bytes")
    return padded_message[:-padding_length]


def coordinate_size_bytes(curve):
    """Return the fixed byte length of one base-field coordinate."""

    field_size = Integer(curve.base_field().cardinality())
    return (field_size.nbits() + 7) // 8


def validate_subgroup_point(point, curve, subgroup_order):
    """Return whether ``point`` is a nonzero point in the expected subgroup."""

    try:
        normalized = curve(point)
    except (TypeError, ValueError):
        return False
    if normalized.is_zero():
        return False
    return Integer(subgroup_order) * normalized == curve(0)


def point_hat(point, subgroup_order):
    """Compute the half-length MQV reduction of a point's x-coordinate."""

    if point.is_zero():
        raise ValueError("MQV reduction is undefined for the point at infinity")
    x_coordinate, _ = point.xy()
    order_bits = Integer(subgroup_order).nbits()
    reduction_bits = (order_bits + 1) // 2
    power = Integer(2) ** reduction_bits
    return power + (Integer(x_coordinate) % power)

