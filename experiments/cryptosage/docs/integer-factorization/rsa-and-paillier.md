---
sidebar_position: 4
---

# RSA and Paillier

RSA and Paillier both construct a modulus $n=pq$, but use it differently. RSA
relies on exponentiation modulo $n$ and inversion modulo $\varphi(n)$; Paillier
works modulo $n^2$ and provides additive homomorphism.

## RSA key generation

The RSA demonstration generates distinct fixed-size primes and repeats until
$e=65537$ is invertible modulo $\varphi(n)$:

```python
while True:
    p = random_prime(upper, lbound=lower)
    q = random_prime(upper, lbound=lower)
    if p != q and gcd(e, (p - 1) * (q - 1)) == 1:
        break

phi = (p - 1) * (q - 1)
d = inverse_mod(e, phi)
```

The file demonstrates key arithmetic only. It deliberately does not expose a
textbook RSA encryption API, because raw RSA without OAEP or a standardized
signature encoding is unsafe.

## Paillier encryption

With $g=n+1$, encryption of $m\in\mathbb{Z}_n$ is

$$
c=g^m r^n \bmod n^2,
$$

where $r$ must belong to $\mathbb{Z}_n^*$. The corrected randomizer loop is:

```python
while True:
    r = randint(1, n - 1)
    if gcd(r, n) == 1:
        break
```

Multiplying two ciphertexts adds their plaintexts:

$$
D(c_1c_2 \bmod n^2)=m_1+m_2 \bmod n.
$$

The test suite checks decryption and this homomorphic identity. The example does
not implement threshold Paillier, proofs of plaintext knowledge, chosen-
ciphertext protection, or production key storage.
