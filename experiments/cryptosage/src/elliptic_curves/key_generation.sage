"""Generic EC key generation over an already-loaded prime-order subgroup."""


def ec_keygen(base_point=P, subgroup_order=n):
    """Return public point ``Q = dP`` and private scalar ``d``."""

    private_key = Integer(randint(1, subgroup_order - 1))
    public_key = private_key * base_point
    return public_key, private_key

