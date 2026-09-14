# BFV toy experiment

A deliberately small exact-arithmetic script illustrating:

- RLWE-style public keys,
- plaintext scaling by `floor(q/t)`,
- encryption/decryption,
- homomorphic addition,
- the raw ciphertext-product shape growing from two to three components.

The script deliberately stops before the BFV-specific scale-down/relinearization step rather than pretending a naive modular rescale is production-correct.

It does **not** implement production RNS BFV, relinearization keys, batching, or secure
parameter selection.
