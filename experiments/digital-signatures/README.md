# Digital-signature companion experiments

This directory contains deliberately educational code supporting the CryptoCave Digital Signatures series.

- `ecdsa_nonce_reuse_demo.py` implements enough secp256k1/ECDSA algebra to demonstrate the catastrophic effect of nonce reuse.
- `schnorr_toy.py` demonstrates the Schnorr verification equation in a tiny subgroup.

These programs are not constant-time, do not implement production key serialization, and must not be used as cryptographic libraries.
