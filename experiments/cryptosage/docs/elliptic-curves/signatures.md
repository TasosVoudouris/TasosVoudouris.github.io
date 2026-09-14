---
sidebar_position: 5
---

# Elliptic-curve keys and signatures

The elliptic-curve examples use the supplied `prime192v1` parameters, also known
as `secp192r1`. They remain useful for tracing group operations but provide only
about 96 bits of classical security and should not be selected for a new system.

## Key generation

For generator $P$ of prime order $n$, a private key is sampled from
$\{1,\ldots,n-1\}$ and the public key is $Q=dP$:

```python
d = randint(1, n - 1)
Q = d * P
```

## ECDSA

ECDSA computes

$$
r=x(kP)\bmod n,\qquad
s=k^{-1}(H(m)+dr)\bmod n.
$$

The revised loop samples a fresh nonce whenever either component is zero. The
verifier first checks $1\le r,s<n$, validates the public key, and rejects the
point at infinity before comparing the reconstructed $x$-coordinate.

The random nonce is acceptable for an educational demonstration, but a real
implementation needs a cryptographically secure RNG or deterministic nonce
generation such as RFC 6979.

## EC-KCDSA

The supplied signing equation was consistent with the EC-KCDSA convention
$Q=d^{-1}P$, not with the generic key generator's $Q=dP$. A dedicated key
generator now makes that convention explicit:

```python
Q = Integer(Fn(d) ** (-1)) * P
```

The verification relation then reconstructs the ephemeral point:

$$
sQ+wP=d(k-w)d^{-1}P+wP=kP.
$$
