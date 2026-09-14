---
title: "Message Authentication Codes: HMAC, CBC-MAC, and KMAC"
description: "Develop the unforgeability goal for MACs, compare PRF-based reasoning, CBC-MAC boundaries, HMAC, KMAC, truncation, encoding, and verification engineering."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Symmetric Cryptography"
  - "Implementation Security"
tags:
  - "mac"
  - "hmac"
  - "cbc-mac"
  - "kmac"
  - "authentication"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 7
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. Integrity becomes authenticity only with a key

An unkeyed digest can reveal a change only when the verifier already trusts the expected digest. A message authentication code (MAC) uses a shared secret to let a verifier distinguish messages produced by a key holder from attacker-generated data.

A MAC scheme consists of:

\[
\mathsf{KeyGen}(1^\lambda)\rightarrow K,
\]

\[
\mathsf{Tag}_K(M)\rightarrow T,
\]

\[
\mathsf{Verify}_K(M,T)\rightarrow\{0,1\}.
\]

Correctness requires

\[
\Pr[\mathsf{Verify}_K(M,\mathsf{Tag}_K(M))=1]=1
\]

for valid inputs (allowing any explicitly modeled failure probability for randomized schemes).

![MAC generation and verification](/images/hash-functions/message-authentication-codes/maccomponents.png)

The same shared key usually enables both tagging and verification. Consequently, a MAC does not provide non-repudiation: every verifier who knows the key can create a valid tag. Publicly verifiable origin requires a digital signature.

## 2. The chosen-message forgery experiment

The standard baseline is existential unforgeability under chosen-message attack (EUF-CMA):

1. Challenger samples (K\leftarrow\mathsf{KeyGen}(1^\lambda)).
2. Adversary adaptively asks for tags on messages (M_1,\ldots,M_q).
3. Adversary outputs ((M^*,T^*)).
4. It wins if verification accepts and (M^*\notin\{M_1,\ldots,M_q\}).

![MAC unforgeability game](/images/hash-functions/message-authentication-codes/macgame.png)

The adversary need not recover the key or tag an attacker-selected “meaningful” message; producing any fresh accepted message is enough. Security bounds depend on query counts, tag length, key length, construction, primitive advantage, and sometimes total processed blocks.

**Strong unforgeability** (SUF-CMA) also treats a new valid tag for a previously queried message as a forgery. The distinction matters for randomized or multi-tag schemes and protocols that assume one canonical tag.

A separate verification oracle may be modeled in some settings. Real services often reveal acceptance through status, timing, side effects, or error messages even when no explicit oracle API exists.

![A message/tag pair sent to the verifier](/images/hash-functions/message-authentication-codes/shortmessagemac.png)

## 3. What a MAC does not provide

- **No confidentiality:** the message remains readable.
- **No freshness:** a recorded valid `(message, tag)` can be replayed unless a nonce, counter, timestamp, transaction identifier, or replay window is authenticated.
- **No public verifiability:** all shared-key verifiers can forge.
- **No semantic agreement:** two components may parse the same authenticated bytes differently.
- **No key management:** keys still need secure generation, distribution, storage, rotation, and destruction.

## 4. PRF-to-MAC intuition

If (F_K:\mathcal M\rightarrow\{0,1\}^t) is a secure pseudorandom function over the allowed message domain, define

\[
\mathsf{Tag}_K(M)=F_K(M)
\]

and accept exactly when the supplied tag equals the recomputed tag. A fresh tag should then look like an independent uniform (t)-bit value. After (v) blind verification attempts, a basic guessing term is roughly (v/2^t).

The domain restriction matters. A construction secure on exactly one fixed message length may fail when naively extended to arbitrary-length inputs.

## 5. CBC-MAC and its boundary

With block cipher (E_K), fixed IV (C_0=0^n), and equal-length block messages (M_1,\ldots,M_\ell):

\[
C_i=E_K(C_{i-1}\oplus M_i),\qquad T=C_\ell.
\]

CBC-MAC has a security theorem for fixed-length messages under standard assumptions. If variable lengths are admitted without a length-binding construction, extension-style forgeries become possible. Knowing tags for selected messages can let an adversary splice a block adjusted by a previous tag into a new chain.

![CBC-MAC chaining](/images/hash-functions/message-authentication-codes/cbcconstruction.png)

Do not “fix” CBC-MAC by inventing a delimiter. Use a standardized arbitrary-length construction such as CMAC, whose subkey processing handles final-block cases. Also do not reuse the same block-cipher key for CBC encryption and CBC-MAC merely because both invoke the same primitive.

## 6. HMAC construction

For a hash (H) with internal block size (B):

1. If (|K|>B), set (K'=H(K)); otherwise (K'=K).
2. Zero-pad (K') to exactly (B) bytes, obtaining (K_0).
3. Define `ipad` as byte `0x36` repeated (B) times and `opad` as `0x5c` repeated (B) times.
4. Compute

\[
\operatorname{HMAC}_K(M)=
H\left((K_0\oplus\text{opad})\mathbin\|
H((K_0\oplus\text{ipad})\mathbin\|M)\right).
\]

The pads create separated inner and outer keyed domains. They are not two independent random keys, although security explanations sometimes denote the derived values as (K_1) and (K_2).

For SHA-256, (B=64) bytes and the full tag is 32 bytes. The block size is not the digest size.

![Nested HMAC structure](/images/hash-functions/message-authentication-codes/hmac.png)

## 7. Why HMAC resists the simple length-extension attack

The attacker observes the final *outer* digest. Extending that hash would append bytes after a completed input of the form

```text
(K0 xor opad) || inner_digest
```

but a valid HMAC tag always recomputes a new inner digest over the message and feeds exactly that fixed-size value to a fresh outer evaluation. The extended outer string is not a valid HMAC input for any extended message. HMAC has formal analyses that account for more than this structural intuition.

Collision attacks on a hash do not transfer mechanically into HMAC forgeries. The underlying hash's properties still matter, and obsolete hashes should not be selected for new systems, but “a collision exists” and “HMAC is forgeable” are different claims.

![Conceptual nested keyed-hash construction](/images/hash-functions/message-authentication-codes/twokeynest.png)

## 8. KMAC and other standardized choices

- **HMAC:** broadly available and built from an approved hash where specified.
- **KMAC:** SHA-3-derived MAC/PRF with customization and variable output, specified in NIST SP 800-185.
- **CMAC:** block-cipher-based MAC that safely handles variable-length messages according to its specification.
- **GMAC:** authentication component derived from GCM; nonce uniqueness and protocol constraints are critical.
- **Poly1305:** one-time universal-hash authenticator normally used inside a standardized AEAD construction with correctly derived one-time keys.
- **Keyed BLAKE2:** native keyed hashing defined by the BLAKE2 specification.

Algorithm choice is not only a primitive choice. The protocol must specify key size, output length, input encoding, nonce/counter rules, allowed algorithms, and failure behavior.

## 9. Tag truncation and verification volume

Truncating a full tag can be legitimate when the construction and protocol permit it, but it raises forgery probability. If a verifier accepts a (t)-bit tag and exposes (v) attempts under one key, the blind-guess contribution is approximately

\[
\Pr[\text{success}]\lesssim\frac{v}{2^t}

\]

for small (v/2^t), plus construction-specific terms. In multi-user systems, total opportunities may scale with users, keys, records, and time. Rate limiting mitigates online guessing but does not restore bits removed from a tag.

Truncate explicitly to a protocol-fixed number of bits or bytes, and verify exactly that length. Silently accepting variable-length prefixes is a serious bug.

## 10. Encode what the application means

Raw concatenation is ambiguous:

```text
"ab" || "c"  =  "a" || "bc"
```

An attacker does not need to break HMAC if two components assign different meanings to the same authenticated byte string. Define a canonical encoding with:

- a protocol/version/domain label;
- field identifiers or a fixed schema;
- explicit lengths or a canonical structured format;
- one character encoding and normalization policy;
- deterministic integer, timestamp, and path representation;
- all security-relevant headers and context;
- a direction/role label when the same keying material could appear on both sides of a protocol.

[`code/mac_examples.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/mac_examples.py) length-prefixes method, path, and body beneath the domain `CryptoCave/API-request/v1\0` before computing HMAC-SHA-256.

## 11. Verification engineering

Correct verification is more than `expected == received`:

1. Reject malformed encodings and incorrect tag lengths consistently.
2. Reconstruct the exact canonical bytes.
3. Select the key and algorithm from trusted context, not an attacker-controlled downgrade.
4. Recompute the expected tag.
5. Compare using a constant-time function such as Python's `hmac.compare_digest`.
6. Only then parse/act on authenticated content where the protocol permits.
7. Apply replay checks and state transitions atomically.
8. Return errors that do not leak secret-dependent distinctions.

Constant-time comparison prevents an early-exit timing leak in tag equality. It cannot repair a weak tag length, exposed key, ambiguous encoding, replayable protocol, or non-constant-time MAC implementation.

## 12. Key management

- Generate MAC keys from a cryptographically secure random source or an approved KDF.
- A 32-byte random key is a conventional choice for HMAC-SHA-256; protocol standards may specify another size.
- Separate keys by purpose and direction. Use a KDF with explicit context rather than copying one key into unrelated roles.
- Do not hard-code secrets in source control or examples copied into deployment.
- Rotate keys with a versioned verification strategy when historical messages must remain verifiable.
- Bound usage per key according to the construction and application.
- Erase retired key material where the platform makes meaningful erasure possible.

## 13. Code example

```python
key = bytes.fromhex("00112233445566778899aabbccddeeff" * 2)
body = b'{"amount":100,"currency":"EUR"}'

tag = tag_request(key, "POST", "/transfer", body)
assert verify_request(key, "POST", "/transfer", body, tag)
assert not verify_request(key, "POST", "/transfer", body + b" ", tag)
```

Run the complete example:

```bash
python code/mac_examples.py
```

Python's `hmac.digest` delegates the cryptographic operation to the maintained standard-library implementation. The surrounding code exists to teach input design and verification behavior.

## 14. Common errors

| Error | Consequence | Correction |
|---|---|---|
| Plain `Hash(message)` used as authentication | Attacker recomputes the digest | Use a MAC with a secret key |
| `Hash(key || message)` with SHA-256 | Length-extension forgery | Use HMAC/KMAC/standardized keyed mode |
| CBC-MAC on varying lengths | Splicing/extension forgeries | Use CMAC or another arbitrary-length MAC |
| HMAC used for password storage | Fast offline guessing | Use a salted password-hashing scheme |
| Same key reused for several roles | Cross-protocol interactions | Derive separated subkeys with context |
| String concatenation without a schema | Semantic collisions | Canonical, length-delimited encoding |
| Ordinary equality on secret tags | Timing leakage | Constant-time comparison |
| MAC without nonce/counter state | Replay remains possible | Authenticate freshness data and enforce it |
| Very short truncated tag | Feasible online guessing | Choose length from total attempt budget |

Primary specifications: [RFC 2104](https://www.rfc-editor.org/info/rfc2104), [NIST FIPS 198-1 status page](https://csrc.nist.gov/pubs/fips/198-1/final), and [NIST SP 800-185](https://csrc.nist.gov/pubs/sp/800/185/final).

Previous: [Sponge, Keccak, and SHA-3](/blog/sponge-keccak-sha3/).

Next: [Griffin and Algebraic Hashes](/blog/griffin-algebraic-hashes/).
