---
sidebar_position: 1
---

# SageMath cryptography examples

This collection connects cryptographic definitions to small SageMath programs.
It is organized by mathematical family rather than by the names of the original
files, so a reader can move from foundations to schemes and then to protocols.

| Category | Topics | Status |
| --- | --- | --- |
| Foundations | Hashing, integer encoding, KDFs, EC point serialization | Executable helpers |
| Factoring-based cryptography | RSA key generation, Paillier encryption | Executable demonstrations |
| Elliptic-curve cryptography | Keys, ECDSA, EC-KCDSA, ECIES, PSEC | Executable; legacy curve warning |
| Key agreement | ECMQV, STS-inspired key confirmation | Executable studies; protocol caveats |
| Pairing-based cryptography | Elliptic-curve arithmetic and Miller functions | Small educational example |
| Identity-based encryption | RFC 5091 draft | Archived and non-runnable |

The examples expose intermediate mathematical objects so that readers can
inspect them. This visibility is valuable for learning but inappropriate for a
production cryptographic library, where secret-dependent values and intermediate
states must not be logged.

## Suggested reading order

1. [Getting started](getting-started.md)
2. [Foundations and helpers](foundations/index.md)
3. [RSA and Paillier](integer-factorization/rsa-and-paillier.md)
4. [Elliptic-curve keys and signatures](elliptic-curves/signatures.md)
5. [Elliptic-curve encryption](elliptic-curves/encryption.md)
6. [Key agreement](key-agreement/index.md)
7. [Pairings and identity-based cryptography](pairings/index.md)
8. [Security and implementation status](security-status.md)
