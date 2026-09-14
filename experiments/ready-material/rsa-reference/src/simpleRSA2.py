import random
from collections import namedtuple


def get_primes(start, stop):
    """Return a list of prime numbers in the interval [start, stop]."""
    if start >= stop:
        return []

    primes = [2]
    for n in range(3, stop + 1, 2):
        for p in primes:
            if n % p == 0:
                break
        else:
            primes.append(n)

    # Filter out primes below 'start'
    return [p for p in primes if p >= start]


def are_relatively_prime(a, b):
    """Return True if a and b are relatively prime."""
    return all((a % n != 0 or b % n != 0) for n in range(2, min(a, b) + 1))


def make_key_pair(length):
    """
    Create a public-private RSA key pair where 'n' has the given bit length.
    Returns (PublicKey, PrivateKey).
    """
    if length < 4:
        raise ValueError(f"cannot generate a key of length less than 4 (got {length!r})")

    # Determine n range for the desired bit length
    n_min = 1 << (length - 1)
    n_max = (1 << length) - 1

    # Choose primes p, q of approximately half the bit length
    start = 1 << ((length // 2) - 1)
    stop = 1 << ((length // 2) + 1)
    primes = get_primes(start, stop)

    for p in random.sample(primes, len(primes)):
        q_candidates = [q for q in primes if n_min <= p * q <= n_max and q != p]
        if not q_candidates:
            continue
        q = random.choice(q_candidates)
        n = p * q
        phi = (p - 1) * (q - 1)

        # Select public exponent e
        for e in range(3, phi, 2):
            if are_relatively_prime(e, phi):
                break
        else:
            continue

        # Compute private exponent d
        for d in range(3, phi, 2):
            if (d * e) % phi == 1:
                return PublicKey(n, e), PrivateKey(n, d)

    raise AssertionError(f"cannot generate key pair of length={length}")


class PublicKey(namedtuple('PublicKey', 'n e')):
    __slots__ = ()

    def encrypt(self, x):
        """Encrypt an integer x under the public key."""
        if x < 2:
            return x
        return pow(x, self.e, self.n)


class PrivateKey(namedtuple('PrivateKey', 'n d')):
    __slots__ = ()

    def decrypt(self, x):
        """Decrypt an integer x under the private key."""
        if x < 2:
            return x
        return pow(x, self.d, self.n)


if __name__ == '__main__':
    # Example test with known constants
    public = PublicKey(n=2534665157, e=7)
    private = PrivateKey(n=2534665157, d=1810402843)

    assert public.encrypt(123) == 2463995467
    assert public.encrypt(456) == 2022084991
    assert public.encrypt(123456) == 1299565302

    assert private.decrypt(2463995467) == 123
    assert private.decrypt(2022084991) == 456
    assert private.decrypt(1299565302) == 123456

    # Randomized tests
    for length in range(4, 17):
        pub, priv = make_key_pair(length)
        assert pub.n == priv.n
        assert len(bin(pub.n)) - 2 == length

        x = random.randrange(pub.n - 1)
        c = pub.encrypt(x)
        assert priv.decrypt(c) == x

        # Edge cases: encrypt/decrypt 0, 1, n-1, n
        for val in (0, 1, pub.n - 1, pub.n):
            assert pub.encrypt(val) == val % pub.n
            assert priv.decrypt(val) == val % pub.n

    print("All tests passed.")
