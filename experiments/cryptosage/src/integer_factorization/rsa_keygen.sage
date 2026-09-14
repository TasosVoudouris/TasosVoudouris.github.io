"""Educational RSA key generation with basic arithmetic validation."""


def rsa_keygen(prime_bits=1024, public_exponent=65537):
    """Generate a modulus of approximately ``2 * prime_bits`` bits.

    The function demonstrates RSA key arithmetic. It does not provide raw RSA
    encryption or signing because those operations require standardized padding.
    """

    prime_bits = Integer(prime_bits)
    e = Integer(public_exponent)
    if prime_bits < 16:
        raise ValueError("prime_bits is too small even for a demonstration")
    if e <= 2 or e % 2 == 0:
        raise ValueError("the public exponent must be an odd integer greater than 2")

    lower = Integer(2) ** (prime_bits - 1)
    upper = Integer(2) ** prime_bits - 1

    # Repeat until the two primes are distinct and e has an inverse modulo phi.
    while True:
        p = random_prime(upper, lbound=lower)
        q = random_prime(upper, lbound=lower)
        phi = (p - 1) * (q - 1)
        if p != q and gcd(e, phi) == 1:
            break

    modulus = p * q
    private_exponent = inverse_mod(e, phi)
    public_key = (modulus, e)
    private_key = (p, q, private_exponent)
    return public_key, private_key


def print_rsa_key_summary(public_key, private_key):
    """Print sizes and consistency data without dumping the secret primes."""

    modulus, public_exponent = public_key
    p, q, private_exponent = private_key
    phi = (p - 1) * (q - 1)
    print("RSA modulus bits:", Integer(modulus).nbits())
    print("Public exponent:", public_exponent)
    print("Private exponent bits:", Integer(private_exponent).nbits())
    print("Inverse relation valid:", (public_exponent * private_exponent) % phi == 1)

