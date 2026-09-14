---
sidebar_position: 6
---

# Elliptic-curve encryption

ECIES is a hybrid construction: ephemeral elliptic-curve Diffie–Hellman creates
a shared point, a KDF separates symmetric keys, encryption protects
confidentiality, and a MAC protects integrity.

For recipient public key $Q=dP$, the sender samples $k$ and computes

$$
R=kP,\qquad Z=hkQ.
$$

The recipient obtains the same point as $Z=hdR$. The reviewed demonstration
derives 64 bytes and splits them into an AES-256 key and an HMAC-SHA-256 key:

```python
key_material = kdf(x_bytes, 64, point_to_bytes(R, coordinate_size))
encryption_key = key_material[:32]
mac_key = key_material[32:]
```

AES-CBC now uses a random IV and PKCS#7 padding. The IV is included in the MAC,
and the tag is compared before decryption. This fixes the supplied code's
implicit ECB mode, ambiguous zero padding, implicit HMAC digest, and diagnostic
printing of key material.

The PSEC-style example retains its original algebraic transform but uses the
same explicit symmetric protection and point validation. It is included for
historical study; use a standardized, maintained ECIES/HPKE implementation for
new applications.
