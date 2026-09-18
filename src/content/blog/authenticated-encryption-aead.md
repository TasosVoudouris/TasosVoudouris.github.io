---
title: "Authenticated Encryption and AEAD: From Encrypt-then-MAC to GCM and ChaCha20-Poly1305"
description: "Why confidentiality without integrity is insufficient, how encryption and authentication compose, what the AEAD interface guarantees, and how AES-GCM and ChaCha20-Poly1305 work internally and should be used."
pubDate: "2025-02-28"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Hash Functions"
  - "Implementation Security"
  - "Cryptographic Engineering"
tags:
  - "authenticated-encryption"
  - "aead"
  - "encrypt-then-mac"
  - "aes-gcm"
  - "ghash"
  - "chacha20-poly1305"
  - "poly1305"
  - "nonce-reuse"
  - "associated-data"
difficulty: "Intermediate"
series: "Symmetric Cryptography"
seriesOrder: 5
status: "Reviewed"
draft: false
---

## Table of Contents

- [Why Authenticated Encryption Exists](#why-authenticated-encryption-exists)
- [The AEAD Contract](#the-aead-contract)
- [From Encryption Plus MAC to AEAD](#from-encryption-plus-mac-to-aead)
- [AES-GCM: Counter Encryption and Polynomial Authentication](#aes-gcm-counter-encryption-and-polynomial-authentication)
- [ChaCha20-Poly1305: Stream Encryption and One-Time Authentication](#chacha20-poly1305-stream-encryption-and-one-time-authentication)
- [Engineering Rules, Misuse, and Comparison](#engineering-rules-misuse-and-comparison)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why Authenticated Encryption Exists

The previous article studied ECB, CBC, CFB, OFB, and CTR. Those modes answer a confidentiality question:

> Can an observer recover the plaintext from the ciphertext without the secret key?

That is only part of what a real protocol needs.

A receiver must also ask:

> Has the ciphertext, header, sequence number, or other security-relevant metadata been modified?

A confidentiality-only mode does not necessarily answer that question. In fact, several classical modes are intentionally easy to modify algebraically.

For CTR,

$$
C=P\oplus S,
$$

where $S$ is the generated keystream. If an attacker changes the ciphertext to

$$
C'=C\oplus\Delta,
$$

then the receiver obtains

$$
P'
=
C'\oplus S
=
P\oplus\Delta.
$$

The attacker does not know the plaintext or the key, yet can induce a selected XOR difference in the decrypted plaintext.

For CBC,

$$
P_i=D_K(C_i)\oplus C_{i-1}.
$$

Changing $C_{i-1}$ changes $P_i$ in a predictable XOR fashion. The previous article also showed why observable padding validity can turn unauthenticated CBC into a padding-oracle problem.

These are not failures of AES. They are consequences of using **confidentiality without ciphertext integrity**.

Authenticated encryption addresses both properties at once:

$$
\boxed{
\text{confidentiality}
+
\text{ciphertext integrity/authenticity}
}
$$

and **Authenticated Encryption with Associated Data (AEAD)** additionally authenticates selected data that deliberately remains visible.

A typical network packet may conceptually contain:

```text
visible header | nonce | ciphertext | authentication tag
```

The header may need to stay readable for routing or protocol processing, while still being protected against undetected modification. That is the role of **Associated Authenticated Data (AAD)**.

Examples of AAD include:

- protocol version,
- content type,
- packet sequence number,
- sender or channel identifier,
- algorithm identifier,
- record length,
- routing metadata that must remain visible,
- context binding information.

AAD is **authenticated but not encrypted**.

If

```text
AAD = b"version=2;seq=17"
```

then an eavesdropper may read those bytes. But changing the authenticated bytes to

```text
version=2;seq=18
```

must make authentication fail.

This distinction is fundamental:

$$
\text{confidential} \neq \text{authenticated}.
$$

### Integrity, authenticity, and what AEAD does not prove

With a symmetric AEAD key, a valid tag demonstrates that the ciphertext is consistent with the secret key, nonce, AAD, and ciphertext under the algorithm.

It does **not** automatically provide:

- public verifiability,
- digital-signature-style non-repudiation,
- sender identity when several parties share the same symmetric key,
- replay protection,
- authorization,
- secure nonce generation by itself.

Replay is especially easy to misunderstand. If an attacker records a valid tuple

$$
(N,A,C,T)
$$

and sends the exact same tuple again, the authentication tag is still valid.

Preventing replay normally requires protocol state such as:

- monotonically increasing sequence numbers,
- replay windows,
- session identifiers,
- counters stored by the receiver.

A sequence number can be placed in AAD so that it is cryptographically bound to the ciphertext, but the receiver must still remember which sequence numbers are acceptable.

So AEAD is a powerful primitive, but it is still one component of a protocol.

---

## The AEAD Contract

RFC 5116 provides a useful abstract interface for authenticated encryption with associated data.

Conceptually, encryption receives

$$
(K,N,P,A),
$$

where:

- $K$ is the secret key,
- $N$ is a nonce,
- $P$ is plaintext,
- $A$ is associated authenticated data.

We can write the encryption operation as

$$
(C,T)
\leftarrow
\operatorname{Seal}(K,N,P,A),
$$

where $C$ is ciphertext and $T$ is an authentication tag.

Decryption is conceptually

$$
\operatorname{Open}(K,N,C,A,T)
\rightarrow
P
\quad\text{or}\quad
\bot.
$$

The symbol

$$
\bot
$$

means authentication failure.

That atomic interface is one of the most important conceptual improvements over manually combining an encryption mode with separate parsing and MAC logic.

The receiver should not see:

```text
decrypt -> unauthenticated plaintext -> inspect -> maybe verify later
```

but rather:

```text
open/authenticate
       |
       +--> valid plaintext
       |
       +--> authentication failure
```

### What security are we trying to obtain?

At a high level, a secure nonce-respecting AEAD aims to provide two properties.

**Confidentiality.** An attacker should not be able to distinguish protected plaintexts beyond what is inherently revealed by lengths, nonces, visible AAD, and the surrounding protocol.

**Ciphertext integrity.** An attacker should not be able to construct a fresh ciphertext/tag/AAD/nonce combination that the receiver accepts.

Formal cryptographic literature gives these properties names such as privacy under chosen-plaintext attack and ciphertext integrity, often written using notions such as IND-CPA and INT-CTXT. Under appropriate definitions and assumptions, combining privacy and ciphertext integrity also gives strong protection against chosen-ciphertext attacks.

The exact formal model matters, especially around nonce misuse, but the operational intuition is simple:

> The attacker should neither learn the protected plaintext nor create a new accepted protected message.

### Nonces: public but security-critical

A nonce is normally **not secret**.

It may be:

- stored next to the ciphertext,
- transmitted in a packet,
- reconstructed from a sequence number,
- built from a device identifier and message counter.

RFC 5116 emphasizes nonce uniqueness for nonce-based AEAD algorithms: distinct encryption invocations under one key must use distinct nonces unless an algorithm is explicitly specified with a different model.

That gives us the central invariant

$$
(K,N)
$$

must not be accidentally reused in algorithms such as AES-GCM and ChaCha20-Poly1305.

A nonce does not need to be unpredictable merely because it is called a nonce.

For example, a counter

```text
000000000001
000000000002
000000000003
...
```

is predictable but can be perfectly suitable when the algorithm and protocol require uniqueness.

The correct requirement is **algorithm-specific**.

### AAD is byte-exact protocol context

Authentication is performed over bytes, not over abstract semantic objects.

Suppose one endpoint authenticates:

```text
{"user":7,"admin":false}
```

while another endpoint reconstructs semantically equivalent but differently encoded data:

```text
{"admin":false,"user":7}
```

The byte strings differ.

Therefore protocol designs need a canonical encoding for AAD.

This issue appears with:

- JSON serialization,
- integer endianness,
- optional fields,
- Unicode normalization,
- omitted/default values,
- length encodings,
- version negotiation.

Correct cryptography cannot repair an ambiguous application-level encoding.

### Tags and verification

An authentication tag is not a checksum.

It is computed using secret-key-dependent state. A tag forgery should succeed only with a probability bounded by the construction's security guarantees and usage limits.

Tag length matters.

A $t$-bit tag gives only a $2^{-t}$-scale naive guessing barrier per independent attempt, and real security bounds also depend on:

- total messages,
- total authenticated data,
- nonce behavior,
- construction-specific limits,
- whether tags are truncated.

For this reason, tag truncation must follow the named specification rather than application convenience.

### Authentication failure must be terminal

A robust application should treat tag failure as a single cryptographic failure:

```python
try:
    plaintext = aead.decrypt(nonce, ciphertext_and_tag, aad)
except InvalidTag:
    # Reject. Do not parse or act on plaintext.
    ...
```

Do not:

- return partial plaintext,
- reveal which internal check failed,
- distinguish "wrong AAD" from "wrong tag" to an attacker,
- parse attacker-controlled decrypted data before authentication completes.

The precise API varies by library, but the logical contract should remain:

$$
\boxed{
\text{plaintext or failure}
}
$$

not "plaintext plus a boolean that the caller may forget to check."

---

## From Encryption Plus MAC to AEAD

Authenticated encryption did not appear by simply naming a new primitive. Historically, systems often combined:

1. a confidentiality mechanism such as CBC or CTR,
2. a Message Authentication Code (MAC), such as HMAC.

The order of these operations matters.

Let

$$
Enc_{K_E}
$$

be an encryption algorithm and

$$
MAC_{K_M}
$$

a MAC using an independent key.

Three generic composition patterns are commonly discussed.

### Encrypt-and-MAC

Compute

$$
C=Enc_{K_E}(P)
$$

and separately

$$
T=MAC_{K_M}(P).
$$

Output

$$
(C,T).
$$

This authenticates the plaintext rather than the ciphertext.

Depending on the exact primitives and protocol, this can expose information that a designer did not intend. For example, a deterministic MAC may reveal equality relationships between repeated plaintexts even if the encryption itself is randomized.

The important point is not that every encrypt-and-MAC system is automatically broken. The point is that generic composition security is subtle and should not be improvised.

### MAC-then-Encrypt

Compute

$$
T=MAC_{K_M}(P)
$$

and then

$$
C=Enc_{K_E}(P\|T).
$$

The receiver decrypts before it can verify the MAC.

That ordering can make implementation behavior especially important because malformed ciphertext reaches decryption, padding, and parsing logic before authenticity has been established.

Historical protocol failures around padding and detailed decryption errors illustrate why this interface deserves caution.

Again, carefully designed MAC-then-encrypt constructions can have security arguments in particular settings; the problem is treating the pattern itself as automatically safe.

### Encrypt-then-MAC

Compute

$$
C=Enc_{K_E}(P)
$$

and then authenticate the ciphertext and relevant context:

$$
T=
MAC_{K_M}
(
N\|A\|C
).
$$

The receiver first checks

$$
T\stackrel{?}{=}MAC_{K_M}(N\|A\|C)
$$

and only then decrypts.

This gives the clean operational sequence:

```text
receive
   |
verify authentication
   |
   +-- failure -> reject
   |
   +-- success -> decrypt -> release plaintext
```

Under suitable assumptions and proper key separation, Encrypt-then-MAC has a particularly clean generic composition theorem.

That is why it is the best conceptual bridge from classical modes to AEAD.

### Key separation

A manual composition should not casually use the same key for unrelated primitives.

A better structure is:

$$
K_E,K_M
\leftarrow
\operatorname{KDF}(K_{\text{master}},\text{context}).
$$

Then:

- $K_E$ is used only for encryption,
- $K_M$ is used only for authentication.

This is **key separation**.

The labels and protocol context supplied to the KDF should also separate different uses.

For example, conceptually:

```text
K_E = KDF(master, "encryption")
K_M = KDF(master, "authentication")
```

rather than reusing one opaque byte string everywhere.

Standard AEAD algorithms already define their internal use of key material. Applications should not invent extra internal subkeys unless the specification requires it.

### Why standardized AEAD is preferable

It is easy to write something that looks like:

```text
AES-CBC + HMAC
```

and still make a protocol mistake:

- MAC the wrong fields,
- omit the IV from the authenticated transcript,
- compare tags incorrectly,
- decrypt before verification,
- reuse keys,
- mishandle padding errors,
- serialize AAD inconsistently,
- truncate the MAC too far.

A standardized AEAD packages the cryptographic composition into one reviewed primitive with a narrow interface.

That does not eliminate all mistakes—nonce reuse alone can still be catastrophic—but it removes an entire class of composition errors.

---

## AES-GCM: Counter Encryption and Polynomial Authentication

Galois/Counter Mode (GCM) combines two ideas:

1. **CTR-like encryption** for confidentiality,
2. **GHASH**, a polynomial authenticator over $GF(2^{128})$.

NIST SP 800-38D specifies GCM and the authentication-only specialization GMAC.

The result is an AEAD construction:

$$
(K,IV,P,A)
\longrightarrow
(C,T).
$$

The most common and efficient IV size is 96 bits.

### The high-level construction

Let AES under key $K$ be denoted $E_K$.

First derive the **hash subkey**

$$
H=E_K(0^{128}).
$$

For a 96-bit IV, GCM constructs

$$
J_0
=
IV\|0^{31}\|1.
$$

Encryption begins from the incremented counter value. Conceptually,

$$
C_i
=
P_i
\oplus
E_K(\operatorname{inc32}^{\,i}(J_0)).
$$

The authentication side computes GHASH over:

- the AAD,
- zero padding to block boundaries,
- the ciphertext,
- zero padding,
- encoded bit lengths of AAD and ciphertext.

The resulting authentication value is masked using an AES output derived from $J_0$.

A schematic tag equation is

$$
T
=
E_K(J_0)
\oplus
\operatorname{GHASH}_H(A,C),
$$

with the exact standardized formatting of $A$, $C$, padding, and lengths understood.

This formula is extremely useful conceptually because it shows the two independent-looking halves of GCM:

```text
CTR-like encryption  -> confidentiality
GHASH + tag mask      -> authentication
```

### GHASH as polynomial arithmetic

GHASH works over

$$
GF(2^{128}),
$$

defined using the polynomial

$$
x^{128}+x^7+x^2+x+1.
$$

Let the formatted GHASH input be split into 128-bit blocks

$$
X_1,X_2,\dots,X_m.
$$

Set

$$
Y_0=0
$$

and iterate

$$
Y_i
=
(Y_{i-1}\oplus X_i)\cdot H.
$$

Then

$$
\operatorname{GHASH}_H(X_1,\dots,X_m)
=
Y_m.
$$

Expanding the recurrence gives a polynomial in the secret hash subkey $H$:

$$
Y_m
=
X_1H^m
\oplus
X_2H^{m-1}
\oplus
\cdots
\oplus
X_mH.
$$

This is why GCM's authentication is called a polynomial hash.

GHASH is **not** intended to be a standalone unkeyed cryptographic hash function. Its security role exists inside GCM with the secret-derived subkey $H$ and the final encrypted tag mask.

### What exactly is authenticated?

GCM binds:

- ciphertext,
- AAD,
- their lengths,
- the IV/nonce through the construction.

An attacker who changes authenticated input should not be able to produce a valid tag except within the construction's forgery probability bounds.

The plaintext itself is indirectly authenticated because changing the ciphertext changes what would decrypt.

### A standard AES-GCM known-answer vector

For:

```text
AES key   = 00000000000000000000000000000000
IV        = 000000000000000000000000
plaintext = 00000000000000000000000000000000
AAD       = empty
```

the standardized result is:

```text
ciphertext = 0388dace60b6a392f328c2b971b2fe78
tag        = ab6e47d42cec13bdf53a67b21257bddf
```

This gives an excellent implementation test because it checks both encryption and authentication.

Using Python's `cryptography` library:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex(
    "00000000000000000000000000000000"
)

nonce = bytes.fromhex(
    "000000000000000000000000"
)

plaintext = bytes.fromhex(
    "00000000000000000000000000000000"
)

aesgcm = AESGCM(key)

ciphertext_and_tag = aesgcm.encrypt(
    nonce,
    plaintext,
    b"",
)

assert ciphertext_and_tag.hex() == (
    "0388dace60b6a392f328c2b971b2fe78"
    "ab6e47d42cec13bdf53a67b21257bddf"
)

recovered = aesgcm.decrypt(
    nonce,
    ciphertext_and_tag,
    b"",
)

assert recovered == plaintext
```

This API returns

```text
ciphertext || tag
```

as one byte string.

### AAD example

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=128)
nonce = os.urandom(12)

aad = b"protocol=v2;sequence=17"
plaintext = b"transfer=100"

aesgcm = AESGCM(key)

sealed = aesgcm.encrypt(
    nonce,
    plaintext,
    aad,
)

opened = aesgcm.decrypt(
    nonce,
    sealed,
    aad,
)

assert opened == plaintext
```

If the receiver changes even one authenticated header byte:

```python
bad_aad = b"protocol=v2;sequence=18"

aesgcm.decrypt(
    nonce,
    sealed,
    bad_aad,
)
```

authentication fails.

### Why GCM nonce reuse is severe

GCM's encryption half behaves like CTR.

If the same key and nonce are reused, the same counter-derived keystream is reused.

For two plaintexts,

$$
C=P\oplus S,
$$

$$
C'=P'\oplus S,
$$

so

$$
C\oplus C'
=
P\oplus P'.
$$

That already damages confidentiality.

But GCM has a second problem.

With the same nonce, $J_0$ repeats, so the tag mask

$$
E_K(J_0)
$$

also repeats.

For two messages,

$$
T_1
=
E_K(J_0)
\oplus
GHASH_H(A_1,C_1),
$$

$$
T_2
=
E_K(J_0)
\oplus
GHASH_H(A_2,C_2).
$$

XOR the equations:

$$
T_1\oplus T_2
=
GHASH_H(A_1,C_1)
\oplus
GHASH_H(A_2,C_2).
$$

The secret mask disappears.

What remains is an algebraic relation in the GHASH key $H$.

Because GHASH is polynomial evaluation in $GF(2^{128})$, nonce reuse can expose polynomial equations whose unknown is $H$. Depending on message structure, known data, number of reused records, and tag information, those equations can reduce the possible authentication state enough to enable forgeries.

This family of failures is often called the **GCM forbidden attack**.

So GCM nonce reuse can threaten both:

$$
\boxed{
\text{confidentiality}
\quad\text{and}\quad
\text{authenticity}
}
$$

without breaking AES itself.

### The 96-bit IV fast path

GCM supports more general IV lengths in SP 800-38D, but 96 bits has a special construction:

$$
J_0=IV\|0^{31}\|1.
$$

Other IV lengths require an additional GHASH-based derivation of $J_0$.

The 96-bit form is therefore both operationally common and mathematically cleaner.

Modern protocols commonly standardize a 96-bit GCM nonce and define an explicit way to construct it from connection-specific values and sequence numbers.

### Tag lengths and the current NIST revision

The 2007 edition of SP 800-38D permits several tag lengths, including short tags under special constraints.

NIST has since decided to revise the publication and announced that the revision will remove support for tags shorter than 96 bits.

As of September 2026, that revision process is still ongoing rather than a finalized SP 800-38D Rev. 1. NIST's June 2026 pre-draft work is also considering a wider GCM-family construction for a proposed 256-bit-block Rijndael variant.

For ordinary educational and application examples, a full 128-bit GCM tag is the clearest default unless a protocol standard explicitly specifies otherwise.

The distinction between a **current final standard** and a **planned revision** matters: implementation guidance should not silently treat pre-draft proposals as already standardized.

---

## ChaCha20-Poly1305: Stream Encryption and One-Time Authentication

ChaCha20-Poly1305 approaches AEAD differently.

Instead of AES plus a polynomial hash over $GF(2^{128})$, it combines:

- the ChaCha20 stream cipher,
- the Poly1305 one-time authenticator.

RFC 8439 specifies the IETF AEAD construction with:

- a 256-bit key,
- a 96-bit nonce,
- arbitrary-length plaintext,
- arbitrary-length AAD,
- a 128-bit authentication tag.

Conceptually:

```text
key + nonce
    |
    +--> ChaCha20 block 0 --> Poly1305 one-time key
    |
    +--> ChaCha20 blocks 1,2,... --> encryption keystream
                                      |
AAD + ciphertext --------------------+
                                      |
                                 Poly1305
                                      |
                                     tag
```

### ChaCha20 state and counters

ChaCha20 produces 64-byte keystream blocks.

Its block function takes:

- a 256-bit key,
- a 32-bit block counter,
- a 96-bit nonce.

The internal state consists of sixteen 32-bit words and is transformed by repeated **quarter rounds** using:

- modular addition modulo $2^{32}$,
- XOR,
- fixed rotations.

The cryptographic design therefore relies heavily on ARX operations:

$$
\text{Addition} + \text{Rotation} + \text{XOR}.
$$

That makes ChaCha20 structurally very different from AES's S-box and finite-field linear layer.

### How the one-time Poly1305 key is derived

The AEAD construction first runs the ChaCha20 block function with:

```text
counter = 0
```

and the message nonce.

From that block, the first 256 bits are used as the Poly1305 one-time key.

Then plaintext encryption starts at:

```text
counter = 1
```

so the keystream bytes used to derive the MAC key are not reused as message-encryption keystream.

This separation is part of the standardized construction.

### Poly1305 in one equation

Poly1305 uses a one-time 256-bit key commonly viewed as two 128-bit values:

$$
(r,s).
$$

The $r$ value is **clamped** by clearing and fixing certain bits according to the algorithm.

The message is split into blocks and interpreted algebraically modulo

$$
2^{130}-5.
$$

At a high level, the accumulator has the form

$$
h_i
=
(h_{i-1}+m_i)r
\pmod{2^{130}-5}.
$$

After all blocks are processed, the second key component $s$ is added and the low 128 bits form the tag.

The important design idea is that the Poly1305 key is **one-time**.

ChaCha20-Poly1305 safely derives a fresh Poly1305 key from the long-term ChaCha20 key and the per-message nonce.

### What exactly does Poly1305 authenticate?

RFC 8439 constructs the MAC input as

```text
AAD
|| pad16(AAD)
|| ciphertext
|| pad16(ciphertext)
|| len(AAD)_64
|| len(ciphertext)_64
```

where the two lengths are encoded as 64-bit little-endian integers.

This formatting prevents ambiguity between the AAD and ciphertext regions and binds their lengths into authentication.

The tag is then:

$$
T
=
Poly1305_{\text{one-time key}}
(
\text{formatted AAD and ciphertext}
).
$$

Notice that the MAC is computed over the **ciphertext**, not the plaintext.

That gives ChaCha20-Poly1305 an Encrypt-then-MAC-like structure internally.

### Python example

```python
from cryptography.hazmat.primitives.ciphers.aead import (
    ChaCha20Poly1305,
)
import os

key = ChaCha20Poly1305.generate_key()
nonce = os.urandom(12)

aad = b"protocol=v2;sequence=17"
plaintext = b"transfer=100"

aead = ChaCha20Poly1305(key)

sealed = aead.encrypt(
    nonce,
    plaintext,
    aad,
)

opened = aead.decrypt(
    nonce,
    sealed,
    aad,
)

assert opened == plaintext
```

As with the `AESGCM` API, the returned value contains ciphertext plus tag.

Changing any authenticated input should cause decryption to fail:

```python
tampered = bytearray(sealed)
tampered[0] ^= 1

aead.decrypt(
    nonce,
    bytes(tampered),
    aad,
)
```

must raise authentication failure.

### Why nonce reuse is also dangerous here

With the same ChaCha20 key and nonce:

1. the same ChaCha20 keystream sequence repeats,
2. the same Poly1305 one-time key is derived.

The first problem creates the familiar stream-cipher relation

$$
C\oplus C'
=
P\oplus P'.
$$

The second violates Poly1305's one-time-key assumption.

Thus nonce uniqueness is not a cosmetic API requirement; it is fundamental to both halves of the construction.

RFC 8439 requires the 96-bit nonce to be different for each invocation with the same key.

A counter-based nonce allocation is often easier to reason about than "generate random nonces and hope collisions never occur," especially in long-lived systems.

The hard part is distributed state: if multiple devices or processes encrypt under the same key, they must coordinate nonce allocation or use a design that avoids shared-key nonce collisions.

---

## Engineering Rules, Misuse, and Comparison

AES-GCM and ChaCha20-Poly1305 solve the same high-level problem, but they do so using different internal machinery.

| Property | AES-GCM | ChaCha20-Poly1305 |
|---|---|---|
| Encryption primitive | AES in counter mode | ChaCha20 stream cipher |
| Authentication primitive | GHASH over $GF(2^{128})$ | Poly1305 |
| Common nonce size | 96 bits | 96 bits |
| Common tag size | 128 bits | 128 bits |
| Key size | AES-128/192/256 depending profile/API | 256 bits |
| AAD | Yes | Yes |
| Padding needed | No | No |
| Parallelizable encryption | Yes | ChaCha blocks can be independently generated from counters |
| Main catastrophic misuse | nonce reuse | nonce reuse |
| Arithmetic style | AES + binary-field multiplication | ARX + arithmetic modulo $2^{130}-5$ for MAC |

This table is architectural, not a ranking. Choice in a real protocol depends on:

- protocol specification,
- hardware support,
- library availability,
- interoperability,
- deployment environment,
- key-management constraints,
- side-channel-resistant implementation support.

### Hardware and software considerations

AES-GCM is especially efficient on platforms with dedicated AES and carry-less multiplication instructions.

ChaCha20-Poly1305 was designed to perform well using ordinary integer operations and has been attractive on platforms where dedicated AES acceleration is unavailable or undesirable.

Those are implementation observations, not reasons to replace a protocol-mandated algorithm.

If TLS, QUIC, IPsec, or another protocol defines cipher-suite negotiation, use the protocol's approved suites and mature implementation rather than inventing a local policy from microbenchmarks.

### Nonce allocation is a system problem

The cryptographic library sees:

```python
encrypt(key, nonce, plaintext, aad)
```

but it cannot always know whether the same nonce was used yesterday by another process.

Therefore nonce safety may require:

- persistent counters,
- per-device nonce prefixes,
- key rotation,
- session-specific keys,
- crash-safe state,
- coordination between encryptors,
- clear limits on messages per key.

The nonce problem exists **above** the primitive API.

A beautiful implementation of AES-GCM still fails if two machines sharing one key accidentally emit the same nonce.

### Do not conflate randomness and uniqueness

Suppose a system needs one million nonces.

One strategy is:

```text
random 96-bit nonce each time
```

Another is:

```text
fixed per-key prefix || monotonic counter
```

The first is probabilistic collision avoidance.

The second can provide deterministic uniqueness if state is managed correctly.

Which construction is appropriate depends on the named AEAD and protocol.

The rule should come from the specification, not from the vague instruction "IVs should be random."

### Key rotation does not repair a repeated nonce after the fact

If two GCM messages were already encrypted under the same

$$
(K,N),
$$

rotating the key later does not erase the information already exposed in those ciphertexts and tags.

Rotation reduces future exposure; it does not retroactively restore confidentiality or authenticity.

### AAD should bind protocol meaning

AAD is particularly useful when a field must be visible but cryptographically tied to the encrypted payload.

For example:

```text
version       = 2
connection_id = 0x4381
sequence      = 1042
content_type  = application-data
```

can be serialized canonically and authenticated as AAD.

Then the ciphertext cannot be validly transplanted into a different sequence number or content type without recomputing the tag.

This is **context binding**.

But remember: if the protocol accepts the same valid sequence number twice, AEAD alone has not implemented replay detection.

### Length still leaks

AEAD generally does not hide ciphertext length.

An observer can often infer:

- approximate plaintext length,
- record boundaries,
- timing,
- message frequency.

If traffic-analysis resistance matters, padding and record-shaping must be designed at a higher layer.

AEAD protects contents and authenticated context; it is not an anonymity system.

### Failure handling should be uniform

From the application's point of view:

```text
wrong key
wrong nonce
wrong AAD
changed ciphertext
changed tag
```

should all converge to authentication failure.

Libraries may expose one exception type such as `InvalidTag`.

Avoid turning these cases into externally distinguishable protocol errors unless a protocol explicitly requires behavior that has been analyzed for side-channel consequences.

### Test both success and failure

A useful AEAD test suite should not only verify:

```python
decrypt(encrypt(P)) == P
```

but also confirm that every authenticated component is actually bound.

For example:

```python
from cryptography.exceptions import InvalidTag

def must_fail(fn):
    try:
        fn()
    except InvalidTag:
        return
    raise AssertionError("tampered input was accepted")
```

Then test:

```text
flip one ciphertext bit     -> fail
flip one tag bit            -> fail
change AAD                  -> fail
change nonce                -> fail
use wrong key               -> fail
```

Known-answer vectors should additionally be used so that an implementation cannot hide two matching bugs in its encryption and decryption paths.

### AES-GCM misuse resistance is a separate design question

Standard AES-GCM is **not nonce-misuse resistant**.

RFC 8452 specifies AES-GCM-SIV, a different AEAD construction designed to fail much less catastrophically when a nonce is accidentally reused.

That does not mean nonce reuse becomes a recommended operating mode. It means the construction provides a stronger robustness model when uniqueness cannot be guaranteed perfectly.

AES-GCM-SIV should be treated as its own standardized construction, not as a flag that can be added to ordinary GCM.

This distinction is useful because "AEAD" is a family of interfaces, not one universal security guarantee under every misuse pattern.

### A compact decision model

For a protocol designer, the reasoning should look more like this:

```text
Do I need confidentiality only?
    |
    +-- usually no: real messages also need integrity
    |
Use standardized AEAD
    |
Follow exact algorithm nonce rules
    |
Bind visible security metadata as AAD
    |
Reject before releasing plaintext
    |
Enforce replay policy at protocol layer
    |
Respect message/key usage limits
```

not:

```text
pick AES
-> choose some mode
-> add a hash
-> invent an IV format
-> hope the pieces compose
```

That change in abstraction is one of the biggest advances in practical symmetric cryptographic engineering.

---

## Conclusion

The previous article ended with classical confidentiality modes. This article adds the missing property: **authentication**.

The progression is now clear:

$$
\text{block cipher}
\rightarrow
\text{confidentiality mode}
\rightarrow
\text{authenticated encryption}
\rightarrow
\text{AEAD}.
$$

The AEAD interface can be summarized as

$$
(C,T)
\leftarrow
\operatorname{Seal}(K,N,P,A)
$$

and

$$
P
\leftarrow
\operatorname{Open}(K,N,C,A,T)
$$

or authentication failure.

Its four inputs have sharply different roles:

$$
\boxed{
\begin{array}{ll}
K & \text{secret key}\\
N & \text{nonce / per-invocation value}\\
P & \text{plaintext to encrypt and authenticate}\\
A & \text{visible data to authenticate}
\end{array}
}
$$

AES-GCM realizes this interface by combining counter-mode encryption with GHASH:

$$
H=E_K(0^{128}),
$$

$$
C=P\oplus \text{GCTR keystream},
$$

$$
T
=
E_K(J_0)
\oplus
GHASH_H(A,C).
$$

ChaCha20-Poly1305 reaches the same interface through different mathematics:

$$
\text{ChaCha20}
\rightarrow
\begin{cases}
\text{one-time Poly1305 key}\\
\text{message keystream}
\end{cases}
$$

followed by Poly1305 authentication of AAD, ciphertext, padding, and lengths.

The most important implementation lesson is not a particular equation.

It is the contract:

$$
\boxed{
\text{never release unauthenticated plaintext}
}
$$

together with:

$$
\boxed{
\text{respect the nonce rules of the named AEAD}
}
$$

and:

$$
\boxed{
\text{authenticate the protocol context that gives the ciphertext meaning}
}
$$

A strong primitive cannot compensate for repeated nonces, ambiguous AAD serialization, replay-blind protocol logic, or a caller that ignores authentication failure.

That is exactly why AEAD should be treated as a protocol-facing primitive rather than as "encryption plus a checksum."

The next part of the symmetric-cryptography series can now move from **construction and safe use** into **cryptanalysis**: differential and linear techniques, active S-boxes, trails, biases, and the design principles that explain why modern block ciphers are structured the way they are.

---

## References

1. D. McGrew, **RFC 5116: An Interface and Algorithms for Authenticated Encryption**, January 2008.  
   https://www.rfc-editor.org/rfc/rfc5116

2. M. Dworkin, **NIST SP 800-38D: Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC**, November 2007.  
   https://doi.org/10.6028/NIST.SP.800-38D

3. NIST, **Second Pre-Draft Call for Comments on SP 800-38D Rev. 1**, June 2026.  
   https://csrc.nist.gov/pubs/sp/800/38/d/r1/2prd

4. Y. Nir and A. Langley, **RFC 8439: ChaCha20 and Poly1305 for IETF Protocols**, June 2018.  
   https://www.rfc-editor.org/rfc/rfc8439

5. S. Gueron, A. Langley, and Y. Lindell, **RFC 8452: AES-GCM-SIV: Nonce Misuse-Resistant Authenticated Encryption**, April 2019.  
   https://www.rfc-editor.org/rfc/rfc8452

6. NIST, **IR 8459: Report on the Block Cipher Modes of Operation in the NIST SP 800-38 Series**, September 2024.  
   https://doi.org/10.6028/NIST.IR.8459

7. M. Bellare and C. Namprempre, **Authenticated Encryption: Relations among Notions and Analysis of the Generic Composition Paradigm**, ASIACRYPT 2000.
