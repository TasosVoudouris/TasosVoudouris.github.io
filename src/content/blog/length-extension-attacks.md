---
title: "Length-Extension Attacks"
description: "Understand why secret-prefix MACs built from Merkle–Damgård hashes are vulnerable, derive SHA-256 glue padding, reproduce the attack from an exposed digest state, distinguish cryptographic feasibility from parser exploitability, and see why HMAC avoids this failure mode."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
  - "Implementation Security"
tags:
  - "length-extension"
  - "sha256"
  - "mac"
  - "hmac"
  - "merkle-damgard"
  - "secret-prefix-mac"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 5
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [From a Secure Hash to an Insecure MAC](#from-a-secure-hash-to-an-insecure-mac)
- [Glue Padding and the Exposed Chaining State](#glue-padding-and-the-exposed-chaining-state)
- [The Attack as a Continuation of SHA-256](#the-attack-as-a-continuation-of-sha-256)
- [End-to-End Reproducible Laboratory](#end-to-end-reproducible-laboratory)
- [Which Hashes and Constructions Are Affected?](#which-hashes-and-constructions-are-affected)
- [Why HMAC Avoids the Secret-Prefix Failure](#why-hmac-avoids-the-secret-prefix-failure)
- [Protocol Engineering Lessons](#protocol-engineering-lessons)
- [Conclusion](#conclusion)
- [References](#references)

---

## From a Secure Hash to an Insecure MAC

The previous article ended with an important structural fact about SHA-256:

$$
\operatorname{SHA256}(M)
$$

is the final chaining state of a Merkle–Damgård iteration.

That observation is not, by itself, a weakness in SHA-256.

It becomes dangerous when an application invents the wrong keyed construction.

Suppose a server holds a secret key $K$ and authenticates an attacker-visible message $M$ using

$$
t
=
\operatorname{SHA256}(K\|M).
$$

This is often called a **secret-prefix MAC**.

It may look reasonable:

```text
secret key
   ||
message
   |
 SHA-256
   |
  tag
```

but it is not HMAC and does not inherit HMAC's security analysis.

For Merkle–Damgård hashes such as SHA-256, the construction exposes enough state for an attacker to continue hashing.

The attacker can transform a valid pair

$$
(M,t)
$$

into a different message

$$
M'
=
M
\|
P(K\|M)
\|
X
$$

and compute a corresponding valid tag

$$
t'
=
\operatorname{SHA256}
(
K
\|
M
\|
P(K\|M)
\|
X
),
$$

without learning the bytes of $K$.

Here:

- $P(\cdot)$ is the SHA-256 padding that the legitimate hash already processed;
- $X$ is an attacker-chosen suffix.

The attack is possible because the original digest $t$ is the state reached **after** the server has processed

$$
K\|M\|P(K\|M).
$$

The attacker resumes from that state and processes the suffix as if they were the hash implementation continuing normally.

### What is actually being broken?

The attack does **not** find:

- a SHA-256 collision,
- a preimage of the digest,
- a second preimage,
- the secret key.

Instead, it wins a **MAC forgery game** against an insecure composition.

The primitive can remain secure according to its standard collision and preimage claims while the surrounding protocol fails.

That distinction is exactly why the earlier articles separated:

$$
\text{hash security}
$$

from:

$$
\text{protocol security}.
$$

### What the attacker needs

The classical attack needs:

- the visible message $M$;
- a valid tag $t=\operatorname{SHA256}(K\|M)$;
- a chosen suffix $X$;
- knowledge of the hash algorithm and encoding;
- the byte length of $K$, or a manageable set of plausible lengths.

The actual key bytes are not needed.

If the length is unknown but lies in a small range, the attacker can try:

```text
8 bytes
9 bytes
10 bytes
...
32 bytes
```

Each guessed length creates:

- different glue padding,
- a different continued state length,
- a different candidate forged tag.

If a verifier reveals which candidate is accepted, the correct key length is discovered indirectly.

### Key length is metadata, not key recovery

Suppose the attacker determines:

$$
|K|=15.
$$

This does not reveal any of the 15 secret bytes.

It only tells the attacker where SHA-256's original message ended in the logical byte stream.

That is enough to reconstruct the correct padding.

The attack therefore exploits the **length and state interface** of the hash construction, not confidentiality failure of the key.

---

## Glue Padding and the Exposed Chaining State

To understand the attack precisely, we need to reconstruct the padding that SHA-256 applied to the unknown-prefixed message.

Let:

$$
L=|K|+|M|
$$

be the original byte length.

SHA-256 appends:

```text
80 || 00 ... 00 || big_endian_64(8L)
```

such that the total padded length is a multiple of 64 bytes.

The padding length is:

$$
1+z+8
$$

bytes, where $z$ is chosen so that:

$$
L+1+z\equiv56\pmod{64}.
$$

Equivalently:

$$
z
=
(56-(L+1)\bmod64)\bmod64.
$$

### Concrete example

Use:

```python
server_secret = b"server-side-key"
original = b"comment=hello&role=user"
```

The secret is:

$$
|K|=15
$$

bytes.

The visible message is:

$$
|M|=23
$$

bytes.

Therefore:

$$
L=15+23=38.
$$

SHA-256 padding begins with:

```text
80
```

and then needs 17 zero bytes because:

$$
38+1+17=56.
$$

The final 8-byte length field encodes:

$$
8L
=
304
=
\texttt{0x130}
$$

bits.

So the full glue padding is:

```text
80
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00
00 00 00 00 00 00 01 30
```

That is:

- 1 byte `0x80`,
- 17 zero bytes,
- 8 length bytes,

for:

$$
26
$$

padding bytes.

The original secret-prefixed stream therefore occupies:

$$
38+26=64
$$

bytes after padding.

The digest published by the server is the chaining state after exactly one 64-byte block has been processed.

### Computing glue padding without the key bytes

The attacker only needs a guessed key length:

```python
def sha256_padding(length_bytes):
    bit_length = length_bytes * 8

    padding = b"\x80"

    zero_count = (
        56
        - (length_bytes + 1) % 64
    ) % 64

    padding += b"\x00" * zero_count

    padding += bit_length.to_bytes(
        8,
        "big",
    )

    return padding
```

For the example:

```python
glue = sha256_padding(
    15 + len(original)
)

assert len(glue) == 26
assert len(server_secret + original + glue) == 64
```

The attacker then sends:

```text
original
||
glue
||
suffix
```

as the forged visible message.

### Why those strange bytes matter

The forged message is not usually a clean printable string.

It contains:

```text
0x80
0x00
...
length bytes
```

between the original message and the appended suffix.

So cryptographic feasibility is only half of the story.

The application parser must also interpret the resulting byte string in a useful way.

For example, if a vulnerable application treats:

```text
comment=hello&role=user
<binary glue>
&role=admin
```

in a way that gives the appended field semantic effect, the attack may become exploitable.

Another parser may reject the non-printable padding bytes before any useful interpretation occurs.

Therefore:

$$
\boxed{
\text{cryptographic forgery}
\neq
\text{guaranteed application exploit}
}
$$

The parser and message format are part of the threat model.

### The digest is eight SHA-256 state words

A SHA-256 digest is 32 bytes:

$$
256\text{ bits}.
$$

Internally, that is:

$$
8\times32
$$

state bits grouped as:

$$
h_0,h_1,\ldots,h_7.
$$

So a published digest can be parsed as:

```python
def digest_to_state(digest):
    if len(digest) != 32:
        raise ValueError(
            "SHA-256 digest must be 32 bytes"
        )

    return struct.unpack(
        ">8I",
        digest,
    )
```

The attacker now has the exact state from which the legitimate hash would continue.

That is the central mechanism of the attack.

---

## The Attack as a Continuation of SHA-256

Write the original padded secret-prefixed message as:

$$
B_1,B_2,\ldots,B_r.
$$

The legitimate server computes:

$$
h_0=IV,
$$

$$
h_i=f(h_{i-1},B_i),
$$

and publishes:

$$
t=h_r.
$$

The attacker learns:

$$
h_r
$$

directly from the tag.

Now choose suffix $X$.

The attacker computes the final padding required for the **extended logical message length**, splits:

$$
X\|P'
$$

into blocks:

$$
C_1,C_2,\ldots,C_s,
$$

and continues:

$$
h_{r+1}
=
f(h_r,C_1),
$$

$$
h_{r+2}
=
f(h_{r+1},C_2),
$$

and so on until:

$$
t'
=
h_{r+s}.
$$

The new tag is therefore calculated without:

- $K$,
- the original compression history before $h_r$,
- inversion of $f$.

The attacker simply uses the forward compression function.

### Why the logical byte count matters

After the original glue padding, the hash state corresponds to a message length that is already block aligned.

For the running example:

$$
|K|+|M|+|P(K\|M)|
=
64.
$$

If the suffix is:

```python
suffix = b"&role=admin"
```

then SHA-256 must eventually encode the total logical length:

$$
64+|X|
$$

before the final extension padding is added.

The continuation algorithm must therefore know:

```text
current state = published digest
already processed = 64 bytes
new bytes = suffix
```

If it incorrectly pads the suffix as if it were a fresh independent message, it produces the wrong tag.

### Why this is not normal `hashlib` usage

A high-level API such as:

```python
hashlib.sha256(...)
```

starts from the standard SHA-256 IV.

The attacker instead needs:

```text
start from arbitrary state t
with a nonzero processed byte count
```

Ordinary safe hash APIs generally do not expose that low-level interface.

An educational compression implementation does, which is why the previous article built SHA-256 from its internal state transition.

### State continuation pseudocode

Conceptually:

```text
state = parse_digest(known_tag)

processed = guessed_key_length
            + len(original)
            + len(glue_padding)

data = suffix
       + final_padding(
           processed + len(suffix)
         )

for each 64-byte block in data:
    state = compress(state, block)

forged_tag = serialize(state)
```

The forged message sent to the server is:

```text
original || glue_padding || suffix
```

The server computes:

```text
SHA256(
    secret
    || original
    || glue_padding
    || suffix
)
```

and reaches exactly the same state.

### A state diagram

```text
Legitimate computation
----------------------

IV
 |
 f(K || M || first padded block)
 |
 t  <---------------- published tag


Attacker continuation
---------------------

t
 |
 f(suffix || final padding)
 |
 t'


Server on forged message
------------------------

IV
 |
 f(K || M || original glue padding)
 |
 t
 |
 f(suffix || final padding)
 |
 t'
```

The middle state is identical.

That is the complete attack.

---

## End-to-End Reproducible Laboratory

The repository experiment:

[`code/length_extension_demo.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/length_extension_demo.py)

models both the vulnerable server and the attacker.

The server holds:

```python
server_secret = b"server-side-key"

original = b"comment=hello&role=user"

published_tag = hashlib.sha256(
    server_secret + original
).digest()
```

The attacker sees:

```text
original
published_tag
```

but not:

```text
server_secret
```

and wants to append:

```python
suffix = b"&role=admin"
```

### SHA-256 continuation primitive

Using the educational compression routine from the previous article:

```python
def continue_sha256_from_digest(
    known_digest,
    suffix,
    processed_length,
):
    state = digest_to_state(
        known_digest
    )

    final_length = (
        processed_length
        + len(suffix)
    )

    continuation = (
        suffix
        + sha256_padding(final_length)
    )

    if len(continuation) % 64 != 0:
        raise AssertionError(
            "continuation must be block aligned"
        )

    for offset in range(
        0,
        len(continuation),
        64,
    ):
        state = compress(
            state,
            continuation[
                offset:offset + 64
            ],
        )

    return state_to_digest(state)
```

The critical parameter is:

```python
processed_length
```

which is the number of bytes already represented by the published chaining state.

### Forgery routine

```python
def forge_sha256_secret_prefix_mac(
    original,
    known_tag,
    suffix,
    guessed_secret_length,
):
    original_secret_prefixed_length = (
        guessed_secret_length
        + len(original)
    )

    glue = sha256_padding(
        original_secret_prefixed_length
    )

    forged_message = (
        original
        + glue
        + suffix
    )

    processed_length = (
        original_secret_prefixed_length
        + len(glue)
    )

    forged_tag = (
        continue_sha256_from_digest(
            known_tag,
            suffix,
            processed_length,
        )
    )

    return forged_message, forged_tag
```

Notice what is absent from the attacker API:

```text
server_secret
```

The only secret-related input is:

```text
guessed_secret_length
```

### Vulnerable verifier

```python
def vulnerable_verify(
    secret,
    message,
    tag,
):
    expected = hashlib.sha256(
        secret + message
    ).digest()

    return hmac.compare_digest(
        expected,
        tag,
    )
```

The server still computes an ordinary full SHA-256 from the beginning.

It does not know or care that the attacker produced the tag by state continuation.

### Brute-force a plausible key-length range

```python
accepted = None

for guess in range(1, 33):
    forged_message, forged_tag = (
        forge_sha256_secret_prefix_mac(
            original=original,
            known_tag=published_tag,
            suffix=suffix,
            guessed_secret_length=guess,
        )
    )

    if vulnerable_verify(
        server_secret,
        forged_message,
        forged_tag,
    ):
        accepted = (
            guess,
            forged_message,
            forged_tag,
        )

        break

assert accepted is not None

guess, forged_message, forged_tag = accepted

assert guess == 15
```

The correct guess is:

```text
15 bytes
```

exactly matching:

```python
len(b"server-side-key")
```

### Important intermediate values

For this experiment:

```text
secret length       = 15
visible message     = 23 bytes
secret || message   = 38 bytes
glue padding        = 26 bytes
processed prefix    = 64 bytes
suffix              = 11 bytes
```

The forged message is therefore:

```text
23 visible bytes
+ 26 glue-padding bytes
+ 11 suffix bytes
= 60 transmitted bytes
```

while the server internally hashes:

```text
15-byte secret
+ 60-byte forged message
= 75 bytes
```

before SHA-256 adds the final extension padding.

### The forged tag is valid

The essential assertion is:

```python
assert vulnerable_verify(
    server_secret,
    forged_message,
    forged_tag,
)
```

The attacker has created a valid authentication tag for a message that the server never previously authenticated.

That is a successful MAC forgery.

### The wrong key-length guess fails

If the attacker guesses:

```text
14
```

instead of:

```text
15,
```

the glue padding encodes the wrong original length.

The attacker and server no longer reach the same state boundary.

The candidate tag fails verification.

This is why a response oracle can reveal the correct key length by trial.

### HMAC rejects the same trick

Now replace the ad-hoc construction with:

```python
def hmac_tag(secret, message):
    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).digest()
```

The length-extension-generated `forged_tag` is not a valid HMAC tag:

```python
assert not hmac.compare_digest(
    hmac_tag(
        server_secret,
        forged_message,
    ),
    forged_tag,
)
```

This is not because HMAC somehow "hides SHA-256 padding."

It uses a different keyed construction whose outer structure prevents the published tag from serving as the directly reusable inner chaining state needed for this attack.

---

## Which Hashes and Constructions Are Affected?

Length extension is not a universal property of all hash functions.

It depends on the construction and on how much internal state the digest exposes.

### MD5, SHA-1, and SHA-256

Classic Merkle–Damgård hashes with exposed final chaining state are the standard examples.

When misused as:

$$
H(K\|M),
$$

the direct continuation attack applies.

That includes the usual exposed-state forms of:

- MD5,
- SHA-1,
- SHA-256.

The details differ in:

- block size,
- word size,
- padding,
- digest format,

but the structural reason is the same.

### SHA-512

SHA-512 is also an iterated SHA-2 construction and exposes its complete chaining state through its 512-bit digest.

The same general secret-prefix continuation issue applies when it is misused as:

$$
\operatorname{SHA512}(K\|M).
$$

The mechanics differ because SHA-512 uses:

- 1024-bit blocks,
- 64-bit words,
- a 128-bit message-length field.

So an implementation cannot simply reuse SHA-256 glue-padding code.

### SHA-224 and SHA-384

SHA-224 and SHA-384 truncate the state exposed by their underlying SHA-2-style compression designs.

Therefore the direct attack is not identical.

For example, an attacker does not receive all internal state words needed to resume compression immediately.

That distinction should be stated carefully:

> state truncation changes the continuation problem; it does not imply that every imaginable keyed use is automatically secure.

Use a standardized MAC rather than relying on accidental protection from hidden state words.

### SHA-3

SHA-3 is based on Keccak's sponge construction rather than Merkle–Damgård.

A SHA3-256 digest exposes only an output portion derived from a much larger internal state; it does not reveal the entire 1600-bit state needed to continue the sponge in the same manner.

Therefore the classic Merkle–Damgård length-extension attack described here does not apply directly to SHA3-256.

But:

$$
\operatorname{SHA3\!-\!256}(K\|M)
$$

should still not be invented as an application MAC.

NIST already defines keyed SHA-3-derived constructions such as KMAC.

### KMAC

KMAC is defined in NIST SP 800-185 using the Keccak family.

It provides:

- keyed authentication,
- variable output length,
- customization/domain separation support.

It is a standardized keyed construction, not "SHA-3 with a secret concatenated somewhere."

### BLAKE2

BLAKE2 defines a native keyed mode.

Applications using BLAKE2 for authentication should invoke the specified keyed interface rather than constructing:

```text
BLAKE2(key || message)
```

by hand.

### A useful classification

| Construction | Classic SHA-256-style length extension? |
|---|---|
| `SHA256(K || M)` | Yes |
| `SHA1(K || M)` | Yes |
| `MD5(K || M)` | Yes |
| `SHA512(K || M)` | Same structural issue |
| SHA-224 / SHA-384 prefix construction | Direct attack altered by state truncation |
| SHA3-256 | No direct Merkle–Damgård continuation |
| HMAC-SHA-256 | No secret-prefix length-extension forgery |
| KMAC | Different standardized keyed construction |
| BLAKE2 keyed mode | Different standardized keyed mode |

The table should not be interpreted as a recommendation to invent keyed variants of the entries in the middle column.

The safe rule is simpler:

$$
\boxed{
\text{use a standardized MAC construction}
}
$$

---

## Why HMAC Avoids the Secret-Prefix Failure

HMAC does not authenticate a message by computing:

$$
H(K\|M).
$$

Its structure is:

$$
\operatorname{HMAC}_K(M)
=
H
\left(
(K_0\oplus\text{opad})
\|
H(
(K_0\oplus\text{ipad})
\|
M
)
\right),
$$

where:

- $K_0$ is the normalized block-sized key,
- `ipad` is byte `0x36` repeated to the hash block size,
- `opad` is byte `0x5c` repeated to the hash block size.

For SHA-256, the block size is:

$$
B=64\text{ bytes}.
$$

### Key normalization

If:

$$
|K|>B,
$$

HMAC first hashes the key:

$$
K'=H(K).
$$

If the resulting key is shorter than $B$, it is padded with zeros to make the block-sized $K_0$.

The inner hash is:

$$
H(
(K_0\oplus\text{ipad})
\|
M
).
$$

The outer hash then authenticates that inner digest:

$$
H(
(K_0\oplus\text{opad})
\|
\text{inner digest}
).
$$

### Why the published HMAC tag is different

The secret-prefix attack relied on the published value being exactly the state after hashing:

$$
K\|M\|\operatorname{pad}(K\|M).
$$

HMAC does not publish that inner state.

Instead, the published tag is the final output of a second keyed outer hash.

Conceptually:

```text
secret-derived ipad
      ||
    message
      |
   inner hash
      |
 inner digest
      |
secret-derived opad
      ||
 inner digest
      |
   outer hash
      |
 published HMAC
```

The attacker cannot treat the published tag as the state corresponding to:

```text
(K0 xor ipad) || M
```

because it is not that value.

It is the output of the **outer** keyed hash.

### Why "just extend the outer hash" does not create another HMAC

An attacker could imagine continuing the outer SHA-256 state represented by the HMAC tag.

But the result would represent something structurally like:

$$
H(
(K_0\oplus\text{opad})
\|
\text{inner}
\|
\operatorname{pad}
\|
X
).
$$

That is not the HMAC definition for any forged message $M'$, because a legitimate HMAC must have the outer input:

$$
(K_0\oplus\text{opad})
\|
H(
(K_0\oplus\text{ipad})
\|
M'
).
$$

The nested keyed structure breaks the simple continuation equivalence.

This is only the intuitive explanation.

HMAC's actual security analysis is deeper and should be understood through the formal results and standards governing HMAC rather than through the slogan:

> "double hashing fixes length extension."

The specific construction matters.

### HMAC in current standards

RFC 2104 remains the foundational HMAC specification.

NIST FIPS 198-1 is still listed as the current final NIST HMAC standard as of September 2026, although NIST has proposed withdrawing it and moving the specification into SP 800-224.

SP 800-224 remains an **initial public draft** at this time, so it should not be cited as though it were already the final replacement standard.

That distinction is useful when writing current cryptographic guidance:

```text
FIPS 198-1     current final publication
SP 800-224     proposed/draft successor
```

---

## Protocol Engineering Lessons

The attack is short enough to fit in a few dozen lines of Python, but the engineering lessons are much broader.

### Use a real MAC

Do not use:

$$
H(K\|M)
$$

as a homemade MAC.

Use a standardized construction such as:

- HMAC,
- KMAC,
- CMAC,
- a protocol-defined authentication mechanism.

NIST currently lists HMAC, KMAC, and CMAC as general-purpose approved MAC families.

### Prefer AEAD when confidentiality is also needed

If the protocol needs both:

- secrecy,
- integrity/authentication,

use an authenticated-encryption construction such as the protocol's approved AEAD rather than designing:

```text
encryption + homemade hash tag
```

by hand.

### Authenticate canonical bytes

A MAC authenticates bytes, not abstract application objects.

The protocol must define:

- field order,
- field lengths,
- encoding,
- normalization,
- versioning,
- domain labels.

Otherwise two endpoints may interpret the same bytes differently or serialize equivalent objects differently.

### Include context

Security-relevant context may include:

- protocol name,
- protocol version,
- sender/receiver direction,
- message type,
- algorithm identifier,
- sequence number,
- session identifier.

If the protocol does not already separate these domains, they should be included in the authenticated transcript using an unambiguous encoding.

### Verify before acting

Do not:

```text
parse privileged action
then verify MAC
```

Prefer:

```text
receive bytes
verify authentication
only then act
```

The exact parser architecture depends on the protocol, but unauthenticated semantic effects should not occur before authenticity is established.

### Constant-time tag comparison

Use a comparison API intended for authentication tags, such as:

```python
hmac.compare_digest(
    expected,
    received,
)
```

rather than naive early-exit byte comparison.

This reduces avoidable timing leakage in tag verification.

### MAC validity is not freshness

A captured valid message and valid tag remain valid cryptographically.

Replay prevention requires protocol state such as:

- sequence numbers,
- nonces,
- timestamps with policy,
- replay windows,
- session identifiers.

The MAC binds these values if they are authenticated.

It does not remember whether the message has already been processed.

### Separate keys by purpose

Do not reuse one raw secret across unrelated roles such as:

```text
encryption key
MAC key
database secret
hash prefix
API token
```

Protocols should define key separation, often through a KDF with context labels.

### Do not rely on message secrecy to save a broken MAC

Sometimes an application assumes the authenticated message will remain hidden.

That is not a robust MAC security model.

Protocol metadata is often:

- partially known,
- predictable,
- attacker-controlled,
- leaked elsewhere.

The authentication construction should remain secure even when messages are visible and chosen adversarially within the protocol's allowed model.

### Frequent misconceptions

The most important misconceptions can be reduced to five statements.

- **"The SHA-256 length field prevents extension."**  
  No. It enables unambiguous original padding and the classical collision argument, but the attacker can compute that same padding from the message-length guess.

- **"The attacker must know the secret key."**  
  No. The direct attack needs the key length, not the key bytes.

- **"This is a SHA-256 collision."**  
  No. The forged message has a new correctly computed tag. No equal-digest pair is required.

- **"SHA-512 fixes it automatically."**  
  No. Full SHA-512 has the same exposed-state iterative issue when misused as a secret-prefix MAC.

- **"Hiding the message makes the construction secure."**  
  No. Security should come from a keyed authentication construction, not from obscurity of the message.

---

## Conclusion

Length extension is one of the clearest demonstrations of a core cryptographic principle:

$$
\boxed{
\text{a secure primitive can be used in an insecure construction}
}
$$

SHA-256 can remain secure as a collision- and preimage-resistant hash while:

$$
\operatorname{SHA256}(K\|M)
$$

fails as a MAC.

The attack works because three facts line up:

1. SHA-256 is Merkle–Damgård based;
2. the digest exposes the final chaining state;
3. SHA-256 padding is determined by message length.

Given:

$$
t
=
\operatorname{SHA256}(K\|M),
$$

the attacker guesses:

$$
|K|,
$$

constructs:

$$
P(K\|M),
$$

parses $t$ as the eight SHA-256 state words, and continues the compression function over an attacker-chosen suffix $X$.

The forged message is:

$$
M'
=
M
\|
P(K\|M)
\|
X,
$$

and the attacker computes the correct tag for:

$$
K\|M'.
$$

No key recovery occurs.

No collision occurs.

No preimage attack occurs.

The attacker simply exploits the fact that the application exposed a reusable internal state through the wrong keyed construction.

For the running experiment:

```text
secret length       = 15 bytes
visible message     = 23 bytes
original total      = 38 bytes
glue padding        = 26 bytes
processed boundary  = 64 bytes
suffix              = 11 bytes
```

and the correct 15-byte key-length guess produces a valid forged secret-prefix tag.

Replacing the construction with HMAC changes the structure:

$$
H(K\|M)
\quad\longrightarrow\quad
H(
(K_0\oplus\text{opad})
\|
H(
(K_0\oplus\text{ipad})
\|
M
)
).
$$

The public tag is no longer the directly reusable chaining state of the secret-prefixed message that the attacker needs.

That is the conceptual bridge to the next stages of the series.

We now understand:

$$
\text{hash function}
\rightarrow
\text{iterated construction}
\rightarrow
\text{structural misuse}
\rightarrow
\text{need for a standardized MAC}.
$$

The next article moves to the other major modern hash architecture—**sponge constructions, Keccak, and SHA-3**—where the internal state and output interface are designed very differently from Merkle–Damgård.

Previous: [Merkle–Damgård and SHA-256](/blog/merkle-damgard-sha256/).

Next: [Sponge, Keccak, and SHA-3](/blog/sponge-keccak-sha3/).

---

## References

1. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**.  
   https://doi.org/10.6028/NIST.FIPS.180-4

2. H. Krawczyk, M. Bellare, and R. Canetti, **RFC 2104: HMAC: Keyed-Hashing for Message Authentication**, February 1997.  
   https://www.rfc-editor.org/rfc/rfc2104

3. National Institute of Standards and Technology, **FIPS 198-1: The Keyed-Hash Message Authentication Code (HMAC)**, July 2008.  
   https://doi.org/10.6028/NIST.FIPS.198-1

4. National Institute of Standards and Technology, **SP 800-224: Keyed-Hash Message Authentication Code (HMAC): Specification of HMAC and Recommendations for Message Authentication**, Initial Public Draft, June 2024.  
   https://doi.org/10.6028/NIST.SP.800-224.ipd

5. National Institute of Standards and Technology, **SP 800-185: SHA-3 Derived Functions: cSHAKE, KMAC, TupleHash, and ParallelHash**, December 2016.  
   https://doi.org/10.6028/NIST.SP.800-185

6. M. Bellare, R. Canetti, and H. Krawczyk, **Keying Hash Functions for Message Authentication**, CRYPTO 1996.

7. National Institute of Standards and Technology, **Message Authentication Codes Project**, current status and approved MAC families.  
   https://csrc.nist.gov/projects/message-authentication-codes
