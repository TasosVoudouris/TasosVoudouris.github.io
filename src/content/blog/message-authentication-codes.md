---
title: "Message Authentication Codes: HMAC, CBC-MAC, and KMAC"
description: "Develop the unforgeability goal for message authentication codes, connect PRF reasoning to forgery probability, derive CBC-MAC's variable-length failure, study HMAC and KMAC, and build robust rules for truncation, encoding, replay protection, verification, and key separation."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Symmetric Cryptography"
  - "Implementation Security"
tags:
  - "mac"
  - "hmac"
  - "cbc-mac"
  - "cmac"
  - "kmac"
  - "authentication"
  - "euf-cma"
  - "tag-truncation"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 7
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [From Integrity to Keyed Authenticity](#from-integrity-to-keyed-authenticity)
- [Unforgeability, PRFs, and Tag Length](#unforgeability-prfs-and-tag-length)
- [CBC-MAC: Where the Security Boundary Really Is](#cbc-mac-where-the-security-boundary-really-is)
- [HMAC: Nested Hashing Done Deliberately](#hmac-nested-hashing-done-deliberately)
- [KMAC, CMAC, GMAC, Poly1305, and Other Standardized Choices](#kmac-cmac-gmac-poly1305-and-other-standardized-choices)
- [Encoding, Replay, Verification, and Key Separation](#encoding-replay-verification-and-key-separation)
- [Reproducible Labs and Test Vectors](#reproducible-labs-and-test-vectors)
- [Conclusion](#conclusion)
- [References](#references)

---

## From Integrity to Keyed Authenticity

A cryptographic hash can detect modification only when the verifier already trusts the expected digest.

If an attacker can replace both

```text
message
```

and

```text
hash(message)
```

then an unkeyed hash does not authenticate the message.

A **message authentication code (MAC)** introduces a shared secret key and gives the verifier a way to distinguish valid key-generated tags from attacker-generated guesses.

A MAC scheme consists conceptually of three algorithms:

\[
\mathsf{KeyGen}(1^\lambda)\rightarrow K,
\]

\[
\mathsf{Tag}_K(M)\rightarrow T,
\]

\[
\mathsf{Verify}_K(M,T)\rightarrow\{0,1\}.
\]

Correctness requires that honestly generated tags verify:

\[
\Pr[
\mathsf{Verify}_K(
M,
\mathsf{Tag}_K(M)
)=1
]
=
1,
\]

apart from any explicitly modeled failure probability in a randomized construction.

![MAC generation and verification](/images/hash-functions/message-authentication-codes/maccomponents.png)

For a deterministic MAC such as HMAC-SHA-256, the same message under the same key produces the same tag every time.

### What does the secret key add?

Without a key:

\[
T=H(M)
\]

is computable by everyone.

With a MAC:

\[
T=\operatorname{MAC}_K(M),
\]

an attacker who does not know \(K\) should not be able to produce a valid tag for a fresh message except with negligible probability.

The security goal is therefore not:

> "the attacker cannot calculate hashes."

It is:

> "even after seeing valid message-tag pairs, the attacker still cannot create a new accepted pair."

### MACs provide symmetric authenticity

The sender and verifier normally share the same secret key.

Therefore every party capable of verifying a MAC can normally also generate one.

A MAC does **not** provide non-repudiation.

If Alice and Bob both know \(K\), then a valid tag cannot prove to a third party that Alice rather than Bob generated it.

For public verifiability, use a digital signature or another asymmetric authentication mechanism.

### What a MAC does not provide

A MAC provides a form of integrity and source authentication **among parties sharing the key**, but several other properties remain separate.

A MAC does not automatically provide:

- confidentiality,
- freshness,
- replay protection,
- public verifiability,
- canonical message interpretation,
- key management,
- authorization.

A valid pair:

```text
(message, tag)
```

can be replayed unless the protocol authenticates freshness data and maintains state to reject duplicates.

Likewise, two applications may authenticate the same bytes but interpret them differently.

The MAC protects the authenticated byte string.

The protocol must define what those bytes mean.

---

## Unforgeability, PRFs, and Tag Length

The standard baseline security goal is **existential unforgeability under chosen-message attack**, abbreviated:

\[
\text{EUF-CMA}.
\]

### The EUF-CMA game

A simplified game is:

1. The challenger samples:

   \[
   K\leftarrow\mathsf{KeyGen}(1^\lambda).
   \]

2. The adversary may adaptively request tags:

   \[
   T_i=\mathsf{Tag}_K(M_i)
   \]

   for messages of its choice.

3. Eventually it outputs:

   \[
   (M^*,T^*).
   \]

4. It wins if:

   \[
   \mathsf{Verify}_K(M^*,T^*)=1
   \]

   and:

   \[
   M^*
   \notin
   \{M_1,\ldots,M_q\}.
   \]

![MAC unforgeability game](/images/hash-functions/message-authentication-codes/macgame.png)

This model is stronger than merely observing a few legitimate protocol messages.

The adversary may deliberately choose messages designed to reveal weaknesses.

That is why a construction that survives chosen-message analysis gives a much stronger foundation than one tested only on passive traffic.

### The adversary does not need the key

A successful MAC attack need not recover:

\[
K.
\]

It is enough to produce one fresh accepted pair.

Likewise, the forged message does not need to have human-readable semantic value in the mathematical game.

Practical exploitability may require additional control over message syntax, but formal unforgeability asks whether **any** fresh accepted pair can be generated.

![A message/tag pair sent to the verifier](/images/hash-functions/message-authentication-codes/shortmessagemac.png)

### Strong unforgeability

**Strong unforgeability under chosen-message attack**, or SUF-CMA, strengthens the game.

It also counts as a forgery a **new valid tag for an already queried message**.

For deterministic, canonical-tag MACs where each message has one valid tag, this distinction is usually invisible.

It matters more for randomized or multi-tag constructions and protocols that care about tag uniqueness.

### Verification oracles exist in real systems

Even if an API does not expose:

```text
verify(message, tag) -> true/false
```

a service may still reveal validity through:

- status codes,
- response timing,
- error type,
- retries,
- state changes,
- database writes,
- side effects.

That behavior becomes an effective verification oracle.

When evaluating tag truncation or online guessing, the total number of observable verification attempts matters.

### PRF-to-MAC intuition

Suppose:

\[
F_K:\mathcal{M}\rightarrow\{0,1\}^{t}
\]

behaves like a secure pseudorandom function over the allowed message domain.

Define:

\[
\mathsf{Tag}_K(M)=F_K(M).
\]

For a fresh message \(M^*\), the tag should look approximately like an independent random \(t\)-bit string to an attacker.

So a blind guess succeeds with probability:

\[
2^{-t}.
\]

After \(v\) independent attempts, the exact blind-guess success probability is:

\[
1-(1-2^{-t})^v.
\]

When:

\[
v\ll 2^t,
\]

this is approximately:

\[
\frac{v}{2^t}.
\]

This is the origin of the familiar forgery term.

A real security bound also includes construction-specific and primitive-specific terms.

### This is not the birthday bound

For an unkeyed collision search, the attacker wins if **any two** digests collide.

That gives the birthday scale:

\[
2^{t/2}.
\]

For tag forgery, the attacker is normally trying to match the correct tag for a particular fresh message.

That is a fixed-target problem.

The simple guessing scale is:

\[
2^t,
\]

not:

\[
2^{t/2}.
\]

This distinction is crucial when deciding whether a truncated tag is acceptable.

### Tag truncation

Suppose a full HMAC-SHA-256 output is truncated to:

\[
t
\]

bits.

The verifier must define exactly which \(t\) bits are accepted and require exactly that tag length.

For blind guessing:

\[
\Pr[\text{success after }v\text{ attempts}]
\approx
\frac{v}{2^t}.
\]

For example, a 64-bit tag does not provide "128-bit collision strength" in the MAC game.

Its blind online forgery barrier is approximately:

\[
2^{64}
\]

per fresh target under the idealized model, before accounting for query volume and construction-specific bounds.

A short tag may be appropriate in a tightly controlled protocol, but the decision should include:

- verification attempts per key,
- number of users,
- number of records,
- protocol lifetime,
- online rate limits,
- consequences of one forgery.

### Do not accept variable-length prefixes

A dangerous verifier is:

```python
expected.startswith(received)
```

or:

```python
expected[:len(received)] == received
```

because the attacker may choose a trivially short tag.

The protocol should specify one accepted length.

Then verification should reject malformed lengths before comparison.

---

## CBC-MAC: Where the Security Boundary Really Is

CBC-MAC is valuable pedagogically because it shows how a construction can be secure under one message-domain assumption and insecure when that assumption is silently removed.

Let:

\[
E_K:\{0,1\}^n\rightarrow\{0,1\}^n
\]

be a block cipher.

For a message of \(\ell\) blocks:

\[
M=M_1\|M_2\|\cdots\|M_\ell,
\]

define:

\[
C_0=0^n,
\]

\[
C_i
=
E_K(
C_{i-1}\oplus M_i
),
\]

and:

\[
T=C_\ell.
\]

![CBC-MAC chaining](/images/hash-functions/message-authentication-codes/cbcconstruction.png)

### The IV must be fixed

CBC encryption commonly uses a fresh IV.

That intuition must **not** be copied into basic CBC-MAC.

The classical CBC-MAC construction starts from a fixed public value, conventionally:

\[
IV=0^n.
\]

A random attacker-controllable IV creates additional malleability and does not define the standard fixed-IV security theorem.

This is a good example of why:

```text
CBC encryption
```

and:

```text
CBC-MAC
```

must not be treated as the same mode with a different final step.

### Fixed-length security

Under standard assumptions, CBC-MAC can be secure when every authenticated message has the **same fixed number of blocks**.

The message length is part of the domain restriction.

If the application begins accepting arbitrary lengths without modifying the construction, that theorem no longer applies.

### Explicit variable-length forgery

Suppose the adversary requests tags for two block-aligned messages:

\[
M=M_1\|\cdots\|M_\ell
\]

and:

\[
N=N_1\|\cdots\|N_k.
\]

Let:

\[
T=\operatorname{CBCMAC}_K(M)
\]

and:

\[
U=\operatorname{CBCMAC}_K(N).
\]

Now construct:

\[
F
=
M_1\|\cdots\|M_\ell
\|
(N_1\oplus T)
\|
N_2\|\cdots\|N_k.
\]

After processing \(M\), the CBC-MAC chaining state is exactly:

\[
T.
\]

The next compression input becomes:

\[
T\oplus(N_1\oplus T)
=
N_1.
\]

So the state after that block is:

\[
E_K(N_1),
\]

which is exactly the state reached after the first block of \(N\) when CBC-MAC starts from zero.

The remainder then follows the same chain as \(N\).

Therefore:

\[
\boxed{
\operatorname{CBCMAC}_K(F)=U
}
\]

even though the attacker never asked the oracle to authenticate \(F\).

That is an existential forgery.

### Why the attack disappears in the fixed-length domain

The forged message \(F\) is longer than \(M\).

If the MAC is defined only for exactly \(\ell\)-block messages, the forged string is outside the allowed message domain and therefore is not a valid attack against that restricted scheme.

Once variable lengths are admitted, it becomes valid.

This illustrates a recurring cryptographic principle:

\[
\boxed{
\text{security theorem}
+
\text{changed domain}
\neq
\text{same security theorem}
}
\]

### Do not patch CBC-MAC casually

It is tempting to invent:

```text
CBC-MAC(length || message)
```

or:

```text
CBC-MAC(message || delimiter)
```

and assume the problem is solved.

Some length-binding variants can be analyzed securely, but production protocol design should not improvise.

Use a standardized variable-length MAC such as **CMAC**.

### CMAC

CMAC is a block-cipher-based MAC standardized by NIST.

It retains the CBC-MAC chaining idea but treats the last block with derived subkeys.

At a high level:

1. compute:

   \[
   L=E_K(0^n);
   \]

2. derive subkeys \(K_1,K_2\) by finite-field doubling;
3. use one subkey if the last message block is complete;
4. use another subkey with a defined padding rule if the last block is partial;
5. process the resulting blocks under the standardized CBC-MAC-style chain.

This creates a secure arbitrary-length construction under its specified assumptions.

The exact subkey derivation is part of the standard and should not be replaced by a homemade delimiter scheme.

### Separate encryption and MAC keys

Do not reuse one AES key for:

```text
CBC encryption
```

and:

```text
CBC-MAC / CMAC
```

simply because both use AES.

Use protocol-defined key separation.

A KDF can derive distinct subkeys:

\[
K_{\text{enc}}
=
\operatorname{KDF}(K_{\text{master}},\texttt{"enc"}),
\]

\[
K_{\text{mac}}
=
\operatorname{KDF}(K_{\text{master}},\texttt{"mac"}).
\]

Purpose separation reduces cross-protocol and cross-mode interactions.

---

## HMAC: Nested Hashing Done Deliberately

The previous length-extension article showed why:

\[
H(K\|M)
\]

is a poor ad-hoc MAC when \(H\) is an exposed-state Merkle–Damgård hash such as SHA-256.

HMAC uses a carefully designed nested construction instead.

For a hash \(H\) with internal block size \(B\), define a normalized block-sized key \(K_0\).

Then:

\[
\operatorname{HMAC}_K(M)
=
H
\left(
(K_0\oplus\operatorname{opad})
\|
H(
(K_0\oplus\operatorname{ipad})
\|
M
)
\right).
\]

The pad bytes are:

```text
ipad = 0x36 repeated B times
opad = 0x5c repeated B times
```

![Nested HMAC structure](/images/hash-functions/message-authentication-codes/hmac.png)

### Key normalization

If:

\[
|K|>B,
\]

first compute:

\[
K'=H(K).
\]

Otherwise:

\[
K'=K.
\]

Then append zeros until:

\[
|K_0|=B.
\]

For SHA-256:

\[
B=64\text{ bytes},
\]

while the digest size is:

\[
32\text{ bytes}.
\]

Those two values are not interchangeable.

### Why `ipad` and `opad` exist

The inner and outer computations operate in two separated keyed domains:

\[
K_0\oplus\operatorname{ipad}
\]

and:

\[
K_0\oplus\operatorname{opad}.
\]

They should not be described as two independently random keys.

They are deterministically derived from the same normalized key.

Their role is structural separation inside the HMAC construction.

### Why the simple length-extension attack fails

The attacker observes the **outer** digest:

\[
H(
(K_0\oplus opad)
\|
\text{inner digest}
).
\]

Extending that outer hash would produce something like:

\[
H(
(K_0\oplus opad)
\|
\text{inner digest}
\|
\operatorname{pad}
\|
X
).
\]

But a legitimate HMAC of an extended message \(M'\) must be:

\[
H
\left(
(K_0\oplus opad)
\|
H(
(K_0\oplus ipad)
\|
M'
)
\right).
\]

Those are different structures.

The published HMAC tag is not the exposed inner chaining state needed to continue:

\[
(K_0\oplus ipad)\|M.
\]

So the direct secret-prefix continuation trick does not transfer.

![Conceptual nested keyed-hash construction](/images/hash-functions/message-authentication-codes/twokeynest.png)

### Collision resistance and HMAC security are not identical claims

A collision attack against the underlying unkeyed hash does not mechanically become an HMAC forgery.

HMAC security analyses are based on stronger and more construction-specific properties than the simple statement:

```text
underlying hash is collision resistant
```

This is one reason historical collision weaknesses in a hash and practical HMAC forgery are different claims.

For new systems, however, that is not an argument for choosing obsolete hashes.

Use the approved hash and HMAC profile required by the protocol.

### A direct implementation for study

```python
import hashlib


def hmac_sha256_educational(
    key,
    message,
):
    B = 64

    if len(key) > B:
        key = hashlib.sha256(
            key
        ).digest()

    key = key.ljust(
        B,
        b"\x00",
    )

    ipad = bytes(
        [0x36] * B
    )

    opad = bytes(
        [0x5C] * B
    )

    inner_key = bytes(
        a ^ b
        for a, b in zip(
            key,
            ipad,
        )
    )

    outer_key = bytes(
        a ^ b
        for a, b in zip(
            key,
            opad,
        )
    )

    inner = hashlib.sha256(
        inner_key + message
    ).digest()

    return hashlib.sha256(
        outer_key + inner
    ).digest()
```

This code is educational.

Production code should use:

```python
hmac.new(...)
```

or the maintained cryptographic API provided by the platform.

---

## KMAC, CMAC, GMAC, Poly1305, and Other Standardized Choices

There is no single MAC primitive that is best for every protocol.

The surrounding cryptographic ecosystem matters.

### HMAC

HMAC is a hash-based MAC with broad deployment and extensive analysis.

With SHA-256:

```text
HMAC-SHA-256
```

is a common choice where the relevant protocol or standard specifies it.

### KMAC

KMAC belongs to the SHA-3/Keccak family and is standardized in NIST SP 800-185.

It is built from cSHAKE-related constructions rather than by applying the HMAC template to SHA-3.

KMAC provides:

- keyed authentication,
- pseudorandom-function use,
- variable output length,
- a customization string.

This makes domain separation an explicit interface rather than something an application must invent through raw concatenation.

Conceptually:

\[
\operatorname{KMAC}(K,M,L,S),
\]

where:

- \(K\) is the key,
- \(M\) is the message,
- \(L\) is the requested output length,
- \(S\) is an optional customization string.

### CMAC

CMAC is the standardized block-cipher-based descendant of CBC-MAC for arbitrary-length messages.

For modern block sizes, it is commonly instantiated with AES.

Use the full standardized construction rather than basic CBC-MAC with improvised padding.

### GMAC

GMAC is the authentication-only specialization associated with GCM.

Its security depends critically on nonce handling.

Nonce reuse can destroy the algebraic authentication assumptions.

Therefore "GMAC is a MAC" is not enough information for safe use; the protocol must specify nonce uniqueness and key-usage constraints.

### Poly1305

Poly1305 is a universal-hash-based authenticator designed around a one-time key.

In modern protocols it is commonly used inside:

\[
\text{ChaCha20-Poly1305}
\]

with the one-time Poly1305 key derived correctly for each nonce.

Reusing the same one-time authentication key violates the construction's security assumptions.

### Keyed BLAKE2

BLAKE2 includes a native keyed mode.

Applications should use that defined keyed interface rather than invent:

```text
BLAKE2(key || message)
```

and assuming it has equivalent security.

### Current NIST MAC landscape

As of September 2026, NIST's Message Authentication Codes project lists three approved general-purpose MAC algorithm families:

- HMAC,
- KMAC,
- CMAC.

For HMAC, FIPS 198-1 remains listed as a final publication, while NIST has proposed withdrawing it and moving the specification into SP 800-224.

SP 800-224 remains an **Initial Public Draft** at this time.

For CMAC, SP 800-38B remains the current final recommendation in its 2016-updated form, while NIST has announced a future revision.

KMAC remains specified in the final SP 800-185 publication.

This standards status matters because:

```text
proposed replacement
```

is not the same as:

```text
current final standard.
```

---

## Encoding, Replay, Verification, and Key Separation

A strong MAC primitive can still fail at the protocol layer.

The authenticated byte string must correspond unambiguously to the application's intended message.

### Raw concatenation is ambiguous

Consider:

```text
"ab" || "c"
```

and:

```text
"a" || "bc".
```

Both become:

```text
abc
```

after raw concatenation.

A MAC cannot distinguish two semantic objects that were serialized into exactly the same byte string.

That is not a MAC forgery.

It is an encoding failure.

### Length-delimited encoding

One simple building block is:

```python
def field(data):
    return (
        len(data).to_bytes(
            4,
            "big",
        )
        + data
    )
```

Then:

```python
encoded = (
    b"CryptoCave/API-request/v1\x00"
    + field(method)
    + field(path)
    + field(body)
)
```

Now:

```text
("ab", "c")
```

and:

```text
("a", "bc")
```

encode differently.

A real protocol may use:

- TLS-style framing,
- protobuf with canonical rules,
- CBOR deterministic encoding,
- ASN.1 DER,
- another explicitly specified format.

The important property is unambiguity.

### Authenticate context, not only payload

Security-relevant context may include:

- protocol name,
- protocol version,
- sender/receiver direction,
- algorithm identifier,
- message type,
- session identifier,
- counter,
- nonce,
- timestamp,
- method/path,
- headers affecting semantics.

If a field changes how the receiver interprets the message, it often belongs inside the authenticated data.

### Replay protection requires state

Suppose the authenticated object contains:

```text
sequence = 42
```

and the tag is valid.

An attacker can still replay the exact same pair:

```text
(sequence=42, message, tag)
```

unless the receiver remembers that sequence 42 has already been accepted.

Therefore:

\[
\text{authenticated sequence number}
+
\text{replay state}
\]

provides freshness.

The MAC alone does not.

### Verification order

A robust verification pipeline is conceptually:

1. parse only enough outer framing to identify the trusted algorithm/key context;
2. reject malformed tag lengths consistently;
3. reconstruct the canonical authenticated bytes;
4. recompute the expected tag;
5. compare using a constant-time equality function;
6. reject on failure;
7. only then execute authenticated semantics;
8. apply replay/state transitions atomically.

The exact parsing architecture depends on the protocol.

The principle is:

> unauthenticated bytes should not trigger privileged effects before authenticity is established.

### Constant-time comparison

Python provides:

```python
hmac.compare_digest(
    expected,
    received,
)
```

This avoids a common early-exit timing leak in tag equality.

It does not repair:

- a weak MAC,
- a short tag,
- an exposed key,
- ambiguous encoding,
- replay,
- nonce misuse,
- side channels elsewhere.

Constant-time comparison solves one narrow implementation problem.

### Uniform errors

A verifier should avoid returning secret-dependent distinctions such as:

```text
wrong first byte
wrong last byte
correct tag but wrong key version
```

when those differences help an attacker refine guesses.

Externally uniform authentication failure is often a safer interface.

Operational logs can retain richer internal diagnostic detail if access is appropriately controlled.

### Key generation

MAC keys should come from:

- a cryptographically secure random source,
- or an approved KDF deriving them from higher-level key material.

Do not derive keys from:

```text
username
timestamp
device serial
```

without a real key-derivation design.

### Key separation

Use distinct keys for distinct cryptographic roles.

For example:

\[
K_{\text{client-mac}}
\neq
K_{\text{server-mac}}
\neq
K_{\text{encryption}}.
\]

A KDF with explicit context can derive these from one master secret.

Direction-specific keys prevent reflection and cross-direction confusion in bidirectional protocols.

### Rotation and key identifiers

A practical authenticated format may carry a non-secret key identifier:

```text
key_id = 7
```

so the verifier knows which stored key to try.

The identifier itself should be authenticated as part of the message or bound through trusted framing.

During rotation, verification may accept a small set of historical keys while new messages are tagged only with the current key.

### MAC versus AEAD

If the application needs:

- confidentiality,
- integrity,
- authenticity,

an AEAD construction is usually a better primitive than manually composing:

```text
encryption
+
MAC
```

unless the protocol explicitly specifies and analyzes that composition.

A standalone MAC remains appropriate when the message is intentionally public but must be authenticated.

---

## Reproducible Labs and Test Vectors

The repository example:

[`code/mac_examples.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/mac_examples.py)

focuses on canonical input encoding and HMAC verification.

This article adds three reproducible checkpoints:

1. an official HMAC-SHA-256 known-answer test;
2. the variable-length CBC-MAC forgery;
3. an authenticated structured-request example.

### Lab A: RFC 4231 HMAC-SHA-256 vector

RFC 4231 test case 1 uses:

```text
key =
0b repeated 20 times

data =
"Hi There"
```

Expected HMAC-SHA-256:

```text
b0344c61d8db38535ca8afceaf0bf12b
881dc200c9833da726e9376c2e32cff7
```

Using Python:

```python
import hashlib
import hmac


key = bytes.fromhex(
    "0b" * 20
)

message = b"Hi There"

tag = hmac.new(
    key,
    message,
    hashlib.sha256,
).digest()

assert tag.hex() == (
    "b0344c61d8db38535ca8afceaf0bf12b"
    "881dc200c9833da726e9376c2e32cff7"
)
```

The educational HMAC implementation from the previous section should produce the same result.

This is stronger correctness evidence than merely checking that:

```text
tag(message) verifies.
```

A known-answer test checks interoperability with the published construction.

### Lab B: CBC-MAC variable-length forgery

Let AES be the block cipher and use the basic fixed-IV CBC-MAC definition.

Suppose we query:

```text
M = one 16-byte block
N = two 16-byte blocks
```

and obtain:

\[
T=\operatorname{CBCMAC}_K(M),
\]

\[
U=\operatorname{CBCMAC}_K(N).
\]

Construct:

\[
F
=
M
\|
(N_1\oplus T)
\|
N_2.
\]

Then:

\[
\operatorname{CBCMAC}_K(F)=U.
\]

The forged message is three blocks long and was never queried.

The attack works because the verifier admitted arbitrary lengths under raw CBC-MAC.

A standardized CMAC implementation does not use this insecure variable-length definition.

### Lab C: canonical request authentication

A robust request encoding can be:

```python
import hashlib
import hmac


DOMAIN = (
    b"CryptoCave/API-request/v1\x00"
)


def encode_field(data):
    return (
        len(data).to_bytes(
            4,
            "big",
        )
        + data
    )


def encode_request(
    method,
    path,
    body,
):
    return (
        DOMAIN
        + encode_field(
            method.encode("ascii")
        )
        + encode_field(
            path.encode("utf-8")
        )
        + encode_field(body)
    )


def tag_request(
    key,
    method,
    path,
    body,
):
    encoded = encode_request(
        method,
        path,
        body,
    )

    return hmac.new(
        key,
        encoded,
        hashlib.sha256,
    ).digest()


def verify_request(
    key,
    method,
    path,
    body,
    received_tag,
):
    if len(received_tag) != 32:
        return False

    expected = tag_request(
        key,
        method,
        path,
        body,
    )

    return hmac.compare_digest(
        expected,
        received_tag,
    )
```

Example:

```python
key = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    * 2
)

body = (
    b'{"amount":100,"currency":"EUR"}'
)

tag = tag_request(
    key,
    "POST",
    "/transfer",
    body,
)

assert verify_request(
    key,
    "POST",
    "/transfer",
    body,
    tag,
)

assert not verify_request(
    key,
    "POST",
    "/transfer",
    body + b" ",
    tag,
)

assert not verify_request(
    key,
    "GET",
    "/transfer",
    body,
    tag,
)
```

The method and path are authenticated because they affect request semantics.

Changing either one invalidates the tag.

### What these labs prove

The HMAC known-answer vector checks conformance.

The CBC-MAC lab demonstrates a real construction-level forgery under the wrong variable-length domain.

The request example demonstrates engineering discipline:

- domain separation,
- canonical encoding,
- exact tag length,
- constant-time comparison.

None of these labs alone proves a complete production protocol secure.

They test specific properties.

---

## Conclusion

This article moves the series from **hashing** into **keyed authentication**.

The defining MAC security question is not:

> "Can the attacker recover the key?"

It is:

\[
\boxed{
\text{Can the attacker create a fresh accepted message-tag pair?}
}
\]

EUF-CMA captures that goal while allowing the attacker to request tags on chosen messages.

The PRF viewpoint explains the first-order forgery intuition:

\[
t\text{-bit tag}
\Rightarrow
\text{blind guess probability }2^{-t}.
\]

After \(v\) attempts:

\[
\Pr[\text{success}]
\approx
\frac{v}{2^t}
\]

when the ratio is small, plus construction-specific terms.

CBC-MAC then demonstrates why the message domain matters.

For fixed-length messages:

\[
C_i
=
E_K(
C_{i-1}\oplus M_i
)
\]

can form a secure MAC under the appropriate assumptions.

For arbitrary lengths, the simple construction permits splicing:

\[
M
\|
(N_1\oplus T)
\|
N_2\|\cdots
\]

that inherits another valid tag.

The correct response is not to invent a delimiter.

It is to use a standardized construction such as CMAC.

HMAC solves a different composition problem.

Instead of:

\[
H(K\|M),
\]

it uses:

\[
H
\left(
(K_0\oplus opad)
\|
H(
(K_0\oplus ipad)
\|
M
)
\right).
\]

The published outer digest does not expose the inner secret-prefixed state needed by the classical length-extension attack.

KMAC provides a SHA-3-derived alternative with standardized keying, customization, and variable output.

CMAC provides a block-cipher-based alternative.

The broader lesson is that selecting a good primitive is only the beginning.

A complete authentication design must define:

- what bytes are authenticated,
- how fields are encoded,
- how the protocol domain is separated,
- how freshness is represented,
- how replays are rejected,
- how tag lengths are fixed,
- how keys are derived and rotated,
- how failures are reported,
- how verification is implemented.

A secure MAC over the wrong bytes can still authenticate the wrong meaning.

That is why the final engineering rule is:

\[
\boxed{
\text{authenticate an unambiguous protocol transcript, not an informal message description}
}
\]

The next article moves into a more specialized direction: **Griffin and algebraic hash functions**, where the design target is not only conventional software efficiency but also efficient evaluation inside arithmetic proof systems.

Previous: [Sponge, Keccak, and SHA-3](/blog/sponge-keccak-sha3/).

Next: [Griffin and Algebraic Hashes](/blog/griffin-algebraic-hashes/).

---

## References

1. H. Krawczyk, M. Bellare, and R. Canetti, **RFC 2104: HMAC: Keyed-Hashing for Message Authentication**, February 1997.  
   https://www.rfc-editor.org/rfc/rfc2104

2. M. Nystrom, **RFC 4231: Identifiers and Test Vectors for HMAC-SHA-224, HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512**, December 2005.  
   https://www.rfc-editor.org/rfc/rfc4231

3. National Institute of Standards and Technology, **FIPS 198-1: The Keyed-Hash Message Authentication Code (HMAC)**, July 2008.  
   https://doi.org/10.6028/NIST.FIPS.198-1

4. National Institute of Standards and Technology, **SP 800-224: Keyed-Hash Message Authentication Code (HMAC): Specification of HMAC and Recommendations for Message Authentication**, Initial Public Draft, June 2024.  
   https://doi.org/10.6028/NIST.SP.800-224.ipd

5. National Institute of Standards and Technology, **SP 800-38B: Recommendation for Block Cipher Modes of Operation: The CMAC Mode for Authentication**, updated October 2016.  
   https://doi.org/10.6028/NIST.SP.800-38B

6. National Institute of Standards and Technology, **SP 800-185: SHA-3 Derived Functions: cSHAKE, KMAC, TupleHash and ParallelHash**, December 2016.  
   https://doi.org/10.6028/NIST.SP.800-185

7. M. Bellare, R. Canetti, and H. Krawczyk, **Keying Hash Functions for Message Authentication**, CRYPTO 1996.

8. M. Bellare, **New Proofs for NMAC and HMAC: Security Without Collision-Resistance**, CRYPTO 2006.

9. National Institute of Standards and Technology, **Message Authentication Codes Project**.  
   https://csrc.nist.gov/projects/message-authentication-codes
