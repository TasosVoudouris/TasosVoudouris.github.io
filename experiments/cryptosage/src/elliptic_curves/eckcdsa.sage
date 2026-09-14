"""Educational EC-KCDSA-style signing with the correct key convention."""


def eckcdsa_keygen(base_point=P, subgroup_order=n):
    """Generate ``Q = d^(-1)P``, the convention required by this variant."""

    private_key = Integer(randint(1, subgroup_order - 1))
    public_key = Integer(inverse_mod(private_key, subgroup_order)) * base_point
    return public_key, private_key


def _eckcdsa_challenge(r, message, certificate_data, subgroup_order):
    """Combine the point hash with a domain-separated message hash."""

    encoded = b"EC-KCDSA|" + to_bytes(certificate_data) + b"|" + to_bytes(message)
    message_hash = Integer(digest(encoded))
    return Integer(xor_integers(r, message_hash) % subgroup_order)


def eckcdsa_sign(private_key, message, certificate_data=b"", base_point=P, subgroup_order=n):
    """Create an EC-KCDSA-style signature ``(r, s)``."""

    private_key = Integer(private_key)
    if private_key < 1 or private_key >= subgroup_order:
        raise ValueError("private key must satisfy 1 <= d < n")

    while True:
        nonce = Integer(randint(1, subgroup_order - 1))
        ephemeral_point = nonce * base_point
        x_coordinate, _ = ephemeral_point.xy()
        r = Integer(digest(Integer(x_coordinate)))
        challenge = _eckcdsa_challenge(
            r, message, certificate_data, subgroup_order
        )
        s = (private_key * (nonce - challenge)) % subgroup_order
        if r != 0 and s != 0:
            return r, Integer(s)


def eckcdsa_verify(
    public_key,
    message,
    r,
    s,
    certificate_data=b"",
    base_point=P,
    subgroup_order=n,
    curve=E,
):
    """Return whether an EC-KCDSA-style signature is valid."""

    r = Integer(r)
    s = Integer(s)
    if r <= 0 or not (1 <= s < subgroup_order):
        return False
    if not validate_subgroup_point(public_key, curve, subgroup_order):
        return False

    challenge = _eckcdsa_challenge(r, message, certificate_data, subgroup_order)
    reconstructed = Integer(s) * public_key + challenge * base_point
    if reconstructed.is_zero():
        return False
    x_coordinate, _ = reconstructed.xy()
    return Integer(digest(Integer(x_coordinate))) == r

