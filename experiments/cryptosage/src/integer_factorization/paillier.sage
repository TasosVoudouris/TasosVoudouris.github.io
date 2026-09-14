"""Paillier encryption with the common choice g = n + 1."""


def paillier_keygen(prime_bits=512):
    """Return ``(public_key, private_key)`` for an educational Paillier key."""

    prime_bits = Integer(prime_bits)
    if prime_bits < 16:
        raise ValueError("prime_bits is too small even for a demonstration")
    lower = Integer(2) ** (prime_bits - 1)
    upper = Integer(2) ** prime_bits - 1

    while True:
        p = random_prime(upper, lbound=lower)
        q = random_prime(upper, lbound=lower)
        if p == q:
            continue
        modulus = p * q
        private_exponent = lcm(p - 1, q - 1)
        if gcd(private_exponent, modulus) == 1:
            break

    modulus_squared = modulus ** 2
    generator = modulus + 1
    value = power_mod(generator, private_exponent, modulus_squared)
    l_value = (value - 1) // modulus
    mu = inverse_mod(l_value, modulus)
    return (modulus, generator), (private_exponent, mu)


def paillier_encrypt(message, public_key):
    """Encrypt an integer ``message`` in ``Z_n`` using a fresh unit randomizer."""

    modulus, generator = public_key
    message = Integer(message)
    if message < 0 or message >= modulus:
        raise ValueError("Paillier plaintext must be in the range 0 <= m < n")

    # Paillier requires r in the multiplicative group Z_n^*.
    while True:
        randomizer = Integer(randint(1, modulus - 1))
        if gcd(randomizer, modulus) == 1:
            break

    modulus_squared = modulus ** 2
    return Integer(
        power_mod(generator, message, modulus_squared)
        * power_mod(randomizer, modulus, modulus_squared)
        % modulus_squared
    )


def paillier_decrypt(ciphertext, public_key, private_key):
    """Decrypt a valid Paillier ciphertext to an integer in ``Z_n``."""

    modulus, _ = public_key
    private_exponent, mu = private_key
    modulus_squared = modulus ** 2
    ciphertext = Integer(ciphertext)
    if ciphertext <= 0 or ciphertext >= modulus_squared:
        raise ValueError("ciphertext must be a nonzero residue modulo n^2")
    if gcd(ciphertext, modulus_squared) != 1:
        raise ValueError("ciphertext must belong to the unit group modulo n^2")

    value = power_mod(ciphertext, private_exponent, modulus_squared)
    l_value = (value - 1) // modulus
    return Integer((l_value * mu) % modulus)


def paillier_ciphertext_add(left, right, public_key):
    """Homomorphically add plaintexts by multiplying ciphertexts modulo n^2."""

    modulus, _ = public_key
    return Integer((Integer(left) * Integer(right)) % (modulus ** 2))


# Compatibility name used by the supplied test.
paillier_keygen_simple = paillier_keygen

