"""ECDSA signing and verification for the loaded EC domain parameters."""


def ecdsa_sign(private_key, message, base_point=P, subgroup_order=n):
    """Create an educational ECDSA signature ``(r, s)``.

    A fresh random nonce is sampled on every retry. Production software should
    use an audited secure RNG or deterministic RFC 6979 nonce generation.
    """

    private_key = Integer(private_key)
    if private_key < 1 or private_key >= subgroup_order:
        raise ValueError("private key must satisfy 1 <= d < n")
    hashed_message = Integer(digest(message))

    while True:
        nonce = Integer(randint(1, subgroup_order - 1))
        ephemeral_point = nonce * base_point
        x_coordinate, _ = ephemeral_point.xy()
        r = Integer(x_coordinate) % subgroup_order
        if r == 0:
            continue
        s = (
            inverse_mod(nonce, subgroup_order)
            * (hashed_message + private_key * r)
        ) % subgroup_order
        if s != 0:
            return Integer(r), Integer(s)


def ecdsa_verify(
    public_key,
    message,
    r,
    s,
    base_point=P,
    subgroup_order=n,
    curve=E,
):
    """Return whether ``(r, s)`` is a valid ECDSA signature."""

    r = Integer(r)
    s = Integer(s)
    if not (1 <= r < subgroup_order and 1 <= s < subgroup_order):
        return False
    if not validate_subgroup_point(public_key, curve, subgroup_order):
        return False

    hashed_message = Integer(digest(message))
    inverse_s = inverse_mod(s, subgroup_order)
    u1 = (hashed_message * inverse_s) % subgroup_order
    u2 = (r * inverse_s) % subgroup_order
    reconstructed = Integer(u1) * base_point + Integer(u2) * public_key
    if reconstructed.is_zero():
        return False
    x_coordinate, _ = reconstructed.xy()
    return Integer(x_coordinate) % subgroup_order == r

