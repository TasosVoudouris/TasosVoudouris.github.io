# Hash Functions and Message Authentication Codes

An in-depth CryptoCave module on cryptographic hashing, generic and structural attacks, SHA-2, SHA-3/Keccak, message authentication, and arithmetization-oriented hashes.

> **Scope.** The code is written for learning and cryptanalysis experiments. It intentionally exposes internal state and uses tiny security parameters in some labs. For production systems, use maintained cryptographic libraries and a reviewed protocol.

## Learning path

| Order | Chapter | Main question | Lab |
|---:|---|---|---|
| 1 | [Security properties and attack models](docs/01-security-properties/Hash-Security-Properties.md) | What do preimage, second-preimage, and collision resistance actually promise? | Truncated-digest attacks; historical SHA-1 collision |
| 2 | [The birthday bound](docs/02-birthday-attacks/Birthday-Attacks.md) | Why do collisions cost about the square root of the output space? | Exact probability and table-based collision search |
| 3 | [Merkle–Damgård and SHA-256](docs/03-merkle-damgard-sha2/Merkle-Damgard-and-SHA-256.md) | How does a fixed-size compression function hash an arbitrary-length message? | Tested educational SHA-256 core |
| 4 | [Length-extension attacks](docs/04-length-extension/Length-Extension-Attacks.md) | How can a digest become a resumable chaining state? | End-to-end secret-prefix-MAC forgery |
| 5 | [Sponge, Keccak, and SHA-3](docs/05-sponge-keccak-sha3/Sponge-Keccak-and-SHA-3.md) | How does a permutation-based hash differ from SHA-2? | SHA3-256 and SHAKE256 from Keccak-f[1600] |
| 6 | [Message authentication codes](docs/06-message-authentication-codes/Message-Authentication-Codes.md) | How does a secret key turn integrity into authenticity? | HMAC generation, encoding, and constant-time verification |
| 7 | [Griffin and algebraic hashes](docs/07-algebraic-hashes/Griffin-and-Algebraic-Hashes.md) | Why do proof systems need hashes native to finite fields? | Corrected SageMath Griffin experiment |

## What this module distinguishes

A recurring source of security bugs is asking one primitive to provide a property it was not designed to provide.

| Need | Appropriate primitive | What is insufficient |
|---|---|---|
| Detect accidental corruption | Checksum or ordinary hash | A hash cannot identify an active attacker |
| Authenticate data shared by two parties | MAC such as HMAC, CMAC, or KMAC | `Hash(key || message)` is an improvised construction |
| Publicly verifiable origin | Digital signature | A MAC is forgeable by every verifier holding the shared key |
| Confidentiality and integrity | Authenticated encryption (AEAD) | Encryption alone, or a MAC without encryption |
| Store passwords | Dedicated, salted password-hashing/KDF scheme | Fast SHA-256, SHA-3, or HMAC alone |
| Commit to structured data | A protocol-defined commitment with canonical encoding and domain separation | Concatenating ambiguous fields and hashing them |

## Run the examples

Python 3.10 or later is sufficient for every Python lab:

```bash
python -m unittest discover -s tests -v
python code/birthday_collision.py
python code/sha1_collision_demo.py
python code/length_extension_demo.py
python code/sha3_educational.py
python code/mac_examples.py
```

The Griffin experiment additionally requires SageMath:

```bash
sage code/griffin.sage
```

No Python package installation or network access is required.

## Notation

- (\{0,1\}^n) is the set of all (n)-bit strings.
- (x \mathbin\| y) is unambiguous concatenation of encoded byte strings.
- (x \oplus y) is bitwise exclusive-or.
- (x \xleftarrow{\$} S) means that (x) is sampled uniformly from (S).
- (q) is commonly the number of oracle queries or attack trials.
- (n) is commonly a digest or tag length; each chapter defines local notation before using it.

## Safety and reproducibility

- Attack code operates on local data, toy digest lengths, or published historical vectors.
- The collision and SHA implementations are deterministic and covered by regression tests.
- Examples never download password lists or contact a service.
- Timing-safe comparison uses `hmac.compare_digest`.
- The exact bytes authenticated by a MAC are length-prefixed and domain-separated.
- Security levels and algorithm status are stated with links to primary standards or papers.

See [REVIEW_NOTES.md](REVIEW_NOTES.md) for the audit trail and [REFERENCES.md](REFERENCES.md) for primary sources.
