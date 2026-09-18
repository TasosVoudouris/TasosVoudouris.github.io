---
title: "Merkle–Damgård and SHA-256"
description: "Build the Merkle–Damgård iteration from compression functions, follow SHA-256 padding, message scheduling, rounds and feed-forward, and connect the construction to collision preservation, length extension, multicollisions, and practical implementation discipline."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptographic Engineering"
  - "Mathematical Foundations"
tags:
  - "merkle-damgard"
  - "sha256"
  - "compression-function"
  - "davies-meyer"
  - "length-extension"
  - "message-schedule"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 4
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [From Fixed-Size Compression to Arbitrary-Length Hashing](#from-fixed-size-compression-to-arbitrary-length-hashing)
- [Merkle–Damgård Strengthening and Collision Preservation](#merkledamgård-strengthening-and-collision-preservation)
- [Structural Consequences of Iterated Hashing](#structural-consequences-of-iterated-hashing)
- [Davies–Meyer and Compression-Function Design](#daviesmeyer-and-compression-function-design)
- [SHA-256 from Padding to the 64-Round Compression Function](#sha-256-from-padding-to-the-64-round-compression-function)
- [Educational Implementation and Verification](#educational-implementation-and-verification)
- [Engineering Lessons and the Bridge to Length Extension](#engineering-lessons-and-the-bridge-to-length-extension)
- [Conclusion](#conclusion)
- [References](#references)

---

## From Fixed-Size Compression to Arbitrary-Length Hashing

A practical cryptographic hash must accept messages of arbitrary length, but its internal primitive cannot usually process an unbounded message all at once.

The standard solution is **iteration**.

Let

\[
f:\{0,1\}^{n}\times\{0,1\}^{b}\rightarrow\{0,1\}^{n}
\]

be a compression function.

It receives:

- an \(n\)-bit chaining value,
- one \(b\)-bit message block,

and produces a new \(n\)-bit chaining value.

After padding the message into blocks

\[
M_1,M_2,\ldots,M_\ell,
\]

define

\[
h_0=IV
\]

and iteratively compute

\[
h_i=f(h_{i-1},M_i)
\]

for:

\[
1\le i\le\ell.
\]

The final digest is:

\[
H(M)=h_\ell.
\]

![Merkle–Damgård iteration](/images/hash-functions/merkle-damgard-sha256/merkle.png)

This is the core idea of the **Merkle–Damgård paradigm**.

The arbitrary-length message problem becomes a sequence of fixed-size compression calls:

```text
message
   |
padding
   |
M1   M2   M3   ...   Ml
 |    |    |           |
IV -> f -> f -> f -> ... -> digest
```

The chaining state carries information from every processed block forward into the next block.

### Why an IV is needed

The first compression call has no previous message-derived state.

So the construction defines a fixed initial value:

\[
h_0=IV.
\]

The IV is part of the hash-function specification.

Changing it changes the function.

For SHA-256, the eight 32-bit initial words are:

```text
6a09e667
bb67ae85
3c6ef372
a54ff53a
510e527f
9b05688c
1f83d9ab
5be0cd19
```

These values are not secret.

FIPS 180-4 specifies them from fractional parts of square roots of the first eight prime numbers.

This is an example of **nothing-up-my-sleeve constants**: the values are reproducible from a transparent rule rather than appearing as unexplained magic numbers.

### The construction is stateful but the hash function is deterministic

The internal computation evolves through states:

\[
h_0,h_1,\ldots,h_\ell.
\]

But for a fixed message \(M\), padding rule, IV, and compression function, the final value is uniquely determined:

\[
H(M)=h_\ell.
\]

The implementation may stream blocks incrementally, but the hash itself remains deterministic.

### Streaming follows naturally

One of Merkle–Damgård's major engineering advantages is that the implementation does not need the entire message in memory.

It only needs:

- the current chaining state,
- a partial block,
- the total message length needed for final padding.

Conceptually:

```python
state = IV

for each complete block:
    state = compress(state, block)

process final padded block(s)

return state
```

This is why APIs such as Python's `hashlib` can expose:

```python
h = hashlib.sha256()

h.update(chunk1)
h.update(chunk2)
h.update(chunk3)

digest = h.digest()
```

and obtain exactly the same result as:

```python
hashlib.sha256(
    chunk1 + chunk2 + chunk3
).digest()
```

### Compression is not the same as hashing

It is important to distinguish:

\[
f(h,m)
\]

from:

\[
H(M).
\]

The compression function has fixed-size inputs.

The full hash adds:

- an IV,
- padding,
- message parsing,
- iteration,
- final output rules.

A strong compression function is necessary for many classical iterated designs, but the outer construction can introduce additional structural behavior.

That distinction will become important when we discuss:

- length extension,
- multicollisions,
- herding,
- long-message second-preimage attacks.

---

## Merkle–Damgård Strengthening and Collision Preservation

The padding rule is not a minor encoding detail.

It is part of the cryptographic construction.

### Why padding exists

Suppose a block hash processes:

\[
b\text{-bit blocks}.
\]

Most messages are not exact multiples of \(b\).

The hash therefore needs an injective or suitably structured transformation:

\[
M
\longrightarrow
\operatorname{pad}(M)
\]

such that the padded message can be parsed unambiguously into fixed-size blocks.

A poor padding rule can invalidate security arguments.

### Merkle–Damgård strengthening

The classical strengthening rule appends:

1. a `1` bit;
2. enough `0` bits;
3. a fixed-width encoding of the original message length.

Conceptually:

\[
M
\|
1
\|
0^k
\|
\operatorname{len}(M).
\]

The exact field widths depend on the hash function.

The length field makes the encoding sensitive to the original message boundary.

### SHA-256 padding

SHA-256 processes 512-bit blocks.

For a byte-aligned message of length \(L\) bytes:

1. append `0x80`;
2. append enough zero bytes so that the current length is congruent to 56 modulo 64;
3. append the original bit length \(8L\) as an unsigned 64-bit big-endian integer.

Thus:

\[
\operatorname{pad}(M)
=
M
\|
\texttt{80}
\|
\texttt{00}\cdots\texttt{00}
\|
\operatorname{BE64}(8L).
\]

The final length is always a positive multiple of:

\[
64\text{ bytes}=512\text{ bits}.
\]

### Boundary examples

These boundary cases are worth memorizing because they catch many incorrect implementations.

#### Empty message

For:

\[
L=0,
\]

SHA-256 appends:

```text
80
55 zero bytes
8-byte zero length
```

for one complete 64-byte block.

#### 55-byte message

A 55-byte input has room for:

- `0x80`,
- the 8-byte length field.

So it remains one padded block:

\[
55+1+8=64.
\]

#### 56-byte message

Now:

\[
56+1+8=65.
\]

The padding no longer fits in one block.

The hash needs two blocks, so the message receives:

\[
72
\]

padding bytes in total.

This boundary is one of the best regression tests for a SHA-256 implementation.

#### 64-byte message

Even though the message already occupies exactly one complete data block, padding still needs another full block.

SHA-256 padding is never optional.

### Padding implementation

A compact byte-oriented helper is:

```python
def sha256_padding(message_length_bytes):
    bit_length = message_length_bytes * 8

    padding = b"\x80"

    zero_count = (
        56
        - (message_length_bytes + 1) % 64
    ) % 64

    padding += b"\x00" * zero_count

    padding += bit_length.to_bytes(
        8,
        "big",
    )

    return padding
```

Then:

```python
assert len(
    b"" + sha256_padding(0)
) == 64

assert len(
    b"A" * 55 + sha256_padding(55)
) == 64

assert len(
    b"A" * 56 + sha256_padding(56)
) == 128

assert len(
    b"A" * 64 + sha256_padding(64)
) == 128
```

### Why the length field matters to collision preservation

The classical Merkle–Damgård theorem says, roughly:

> if the compression function is collision resistant and the padding satisfies the required strengthening/prefix- or suffix-freeness conditions, then the iterated hash inherits collision resistance.

The length encoding is central to that argument.

Suppose:

\[
M\neq M'
\]

but:

\[
H(M)=H(M').
\]

After padding, we get two block sequences:

\[
M_1,\ldots,M_\ell
\]

and:

\[
M'_1,\ldots,M'_{\ell'}.
\]

Start from the equal final hash states and compare the chains backward.

If the final compression inputs differ but produce the same output, we have found a collision in:

\[
f.
\]

If the final blocks are the same, move backward.

Eventually, because the padded encodings differ and cannot silently represent the same valid message ending, one must encounter distinct compression inputs producing the same chaining output.

That yields a reduction:

\[
\text{collision in }H
\Longrightarrow
\text{collision in }f.
\]

### What the theorem does not say

This theorem is specifically about collision resistance under its assumptions.

It does **not** mean:

\[
\text{Merkle–Damgård hash}
=
\text{ideal random oracle}.
\]

It does not automatically provide:

- length-extension resistance,
- multicollision resistance matching an ideal random function,
- herding resistance identical to a random oracle,
- the strongest possible second-preimage bounds for extremely long messages.

This is one of the most important conceptual lessons in hash design:

> a construction can preserve one formal property while still expose additional structure relevant to other attack models.

---

## Structural Consequences of Iterated Hashing

Merkle–Damgård iteration has a very recognizable structure.

That structure creates both engineering advantages and cryptanalytic consequences.

### Streaming and incremental computation

The positive side is immediate:

\[
h_i=f(h_{i-1},M_i).
\]

Only the previous state is required.

This supports:

- streaming large files,
- incremental network processing,
- low-memory hashing,
- checkpointed implementations.

### Sequential dependency

Inside a single message chain:

\[
h_i
\]

cannot be computed before:

\[
h_{i-1}.
\]

So classical Merkle–Damgård iteration is inherently sequential for one message.

Independent messages can of course be processed in parallel.

This is different from tree-hash constructions that deliberately expose parallelism across message chunks.

### Length extension

For many Merkle–Damgård hashes, the digest directly reveals the final chaining state:

\[
H(M)=h_\ell.
\]

If an attacker knows:

- \(H(M)\),
- the message length or enough information to infer the padding,

the attacker can continue the compression chain on additional blocks.

Conceptually:

\[
H(M)
\]

becomes a valid starting state for hashing:

\[
X.
\]

This permits computation of a digest corresponding to:

\[
M
\|
\operatorname{pad}(M)
\|
X
\]

without knowing the original message bytes in the ordinary way a fresh hash API would require.

This is **length extension**.

The crucial point is:

> the SHA-256 padding length field does not prevent this.

The strengthening rule helps collision preservation, but the exposed final chaining state still enables continuation.

That distinction is easy to miss.

### Why length extension matters for naive MAC design

Suppose someone invents:

\[
\operatorname{Tag}
=
\operatorname{SHA256}(K\|M).
\]

If an attacker knows:

- the tag,
- the message,
- or enough about the encoded message,
- and can infer or guess \(|K|\),

then the attacker may be able to continue from the exposed SHA-256 state and construct a valid tag for:

\[
K
\|
M
\|
\operatorname{pad}(K\|M)
\|
X.
\]

No SHA-256 collision is required.

No preimage is recovered.

The problem is the **composition**.

This is one of the motivations for HMAC.

The next article can study this attack directly.

### Multicollisions

Suppose we find one compression-function collision from state \(h_0\):

```text
M0 ----\
        -> h1
M0' ---/
```

Then find another collision from \(h_1\):

```text
M1 ----\
        -> h2
M1' ---/
```

Now any choice from the first pair can be combined with any choice from the second:

```text
M0  || M1
M0  || M1'
M0' || M1
M0' || M1'
```

giving four colliding messages.

Continue for \(k\) stages and obtain:

\[
2^k
\]

colliding messages.

Joux showed that this can be assembled at cost roughly:

\[
k\cdot 2^{n/2}
\]

compression work under idealized assumptions, rather than the much larger cost one might expect for a random function producing a \(2^k\)-way collision.

This does not mean that finding one SHA-256 collision is currently easy.

It means that **if** the iterated structure provides one-stage collisions, they compose in a way that differs from an ideal variable-length random oracle.

### Herding and expandable messages

Herding attacks construct a network of internal chaining states that eventually converge.

A simplified intuition is:

```text
many possible internal states
        \ | /
         \|/
       diamond
         |
       final state
```

Later, an attacker may try to connect a chosen prefix into one of the prepared states.

This can support commitment-style attacks under suitable conditions.

Expandable-message techniques use similar ideas to create many different message lengths that reach the same chaining state.

Again, the lesson is structural:

\[
\text{iterated construction}
\neq
\text{perfect random oracle}.
\]

### Long-message second-preimage attacks

For extremely long target messages, generic structural second-preimage attacks on Merkle–Damgård can beat the naive:

\[
2^n
\]

expectation.

This does not imply that ordinary short-message SHA-256 second preimages are practical.

It does show why security statements should specify:

- construction,
- message length,
- attack model,

rather than quote only digest length.

---

## Davies–Meyer and Compression-Function Design

Merkle–Damgård tells us **how to iterate** a compression function.

It does not tell us how to construct the compression function itself.

One classical approach builds a compression function from a block cipher.

### Davies–Meyer

The Davies–Meyer construction is:

\[
f(h,m)
=
E_m(h)\oplus h.
\]

Interpretation:

- \(m\) acts as the block-cipher key;
- \(h\) acts as the block-cipher plaintext;
- the output is XORed with \(h\).

![Davies–Meyer compression](/images/hash-functions/merkle-damgard-sha256/daviesmeyer.png)

The XOR is called **feed-forward**.

Without it, a construction such as:

\[
f(h,m)=E_m(h)
\]

would inherit the block cipher's easy invertibility with respect to the data input when \(m\) is known.

Feed-forward removes that direct inversion path.

### Why the arrangement matters

A block cipher is not automatically a secure compression function under every wiring pattern.

Given:

\[
E_K(P),
\]

we can choose which quantity becomes:

- key,
- block input,
- feed-forward source.

Different arrangements have very different security properties.

The Preneel–Govaerts–Vandewalle analysis studies one-call block-cipher-based compression constructions in the ideal-cipher model and classifies which patterns have meaningful security.

This is another recurring cryptographic theme:

> secure primitives do not automatically compose securely under arbitrary wiring.

### SHA-256 is not literally Davies–Meyer over AES

SHA-256 is specified directly as a dedicated compression function.

It does not call AES or another external standardized block cipher.

However, its structure contains a useful Davies–Meyer-like intuition:

1. start from an eight-word chaining state;
2. transform it through 64 rounds controlled by the message schedule and constants;
3. add the original state words back into the result.

That final word-by-word modular addition is a feed-forward step.

The transformation is closely related to the SHACAL-2 block cipher construction, but this is best treated as structural context.

The SHA-256 API is still:

\[
\text{message}
\rightarrow
\text{digest},
\]

not "encrypt the chaining state with a separately exposed cipher."

---

## SHA-256 from Padding to the 64-Round Compression Function

We now move from generic Merkle–Damgård structure into the exact SHA-256 mechanics.

SHA-256 uses:

| Parameter | Value |
|---|---:|
| Digest | 256 bits |
| Chaining state | eight 32-bit words |
| Message block | 512 bits |
| Initial block words | sixteen 32-bit words |
| Expanded message schedule | sixty-four 32-bit words |
| Compression rounds | 64 |
| Length encoding | 64 bits |
| Word byte order | big-endian |

The maximum message length represented by the SHA-256 padding field is:

\[
<2^{64}\text{ bits}.
\]

### The eight-word state

At the beginning of a compression call, the chaining state is:

\[
(H_0,H_1,H_2,H_3,H_4,H_5,H_6,H_7).
\]

These are copied into working variables:

\[
(a,b,c,d,e,f,g,h).
\]

The compression rounds mutate the working variables.

After round 63, the original input state is added back word-by-word.

### Parsing one block

A 64-byte block is interpreted as sixteen 32-bit big-endian words:

\[
W_0,W_1,\ldots,W_{15}.
\]

For example:

```python
import struct

words = list(
    struct.unpack(
        ">16I",
        block,
    )
)
```

The `>` means big-endian.

Using little-endian parsing would define a different algorithm.

### Message schedule expansion

The original sixteen words expand to:

\[
W_0,\ldots,W_{63}.
\]

For:

\[
16\le t<64,
\]

compute:

\[
W_t
=
\sigma_1(W_{t-2})
+
W_{t-7}
+
\sigma_0(W_{t-15})
+
W_{t-16}
\pmod{2^{32}}.
\]

The small sigma functions are:

\[
\sigma_0(x)
=
\operatorname{ROTR}^7(x)
\oplus
\operatorname{ROTR}^{18}(x)
\oplus
\operatorname{SHR}^3(x),
\]

\[
\sigma_1(x)
=
\operatorname{ROTR}^{17}(x)
\oplus
\operatorname{ROTR}^{19}(x)
\oplus
\operatorname{SHR}^{10}(x).
\]

### Rotation versus shift

This distinction is easy to implement incorrectly.

For rotation:

\[
\operatorname{ROTR}^r(x)
\]

bits shifted off the right end re-enter on the left.

For logical right shift:

\[
\operatorname{SHR}^r(x),
\]

the left side is filled with zeros and the rightmost bits are discarded.

They are not interchangeable.

A 32-bit rotation helper is:

```python
MASK32 = 0xFFFFFFFF

def rotr(x, r):
    return (
        (x >> r)
        |
        (x << (32 - r))
    ) & MASK32
```

while logical shift is simply:

```python
x >> r
```

for a nonnegative 32-bit integer.

### Message schedule purpose

The first sixteen schedule words come directly from the message block.

The remaining 48 mix earlier words through:

- rotations,
- shifts,
- modular addition.

The goal is to spread each message block's influence across many rounds.

The schedule is not a cryptographic hash by itself.

It is one component of the compression design.

### Choice and Majority

SHA-256 uses two nonlinear Boolean functions.

Choice:

\[
\operatorname{Ch}(x,y,z)
=
(x\land y)
\oplus
(\neg x\land z).
\]

Bitwise interpretation:

- if a bit of \(x\) is 1, choose the corresponding bit of \(y\);
- otherwise choose the bit of \(z\).

An equivalent Boolean form is:

\[
\operatorname{Ch}(x,y,z)
=
z\oplus(x\land(y\oplus z)).
\]

Majority:

\[
\operatorname{Maj}(x,y,z)
=
(x\land y)
\oplus
(x\land z)
\oplus
(y\land z).
\]

For each bit position, this returns the majority bit among \(x,y,z\).

### Big Sigma functions

SHA-256 also defines:

\[
\Sigma_0(x)
=
\operatorname{ROTR}^{2}(x)
\oplus
\operatorname{ROTR}^{13}(x)
\oplus
\operatorname{ROTR}^{22}(x),
\]

\[
\Sigma_1(x)
=
\operatorname{ROTR}^{6}(x)
\oplus
\operatorname{ROTR}^{11}(x)
\oplus
\operatorname{ROTR}^{25}(x).
\]

These use rotations only.

Do not confuse:

\[
\sigma_0,\sigma_1
\]

from the message schedule with:

\[
\Sigma_0,\Sigma_1
\]

from the round function.

### One compression round

At round \(t\):

\[
T_1
=
h
+
\Sigma_1(e)
+
\operatorname{Ch}(e,f,g)
+
K_t
+
W_t
\pmod{2^{32}},
\]

\[
T_2
=
\Sigma_0(a)
+
\operatorname{Maj}(a,b,c)
\pmod{2^{32}}.
\]

Then:

\[
h\leftarrow g,
\]

\[
g\leftarrow f,
\]

\[
f\leftarrow e,
\]

\[
e\leftarrow d+T_1\pmod{2^{32}},
\]

\[
d\leftarrow c,
\]

\[
c\leftarrow b,
\]

\[
b\leftarrow a,
\]

\[
a\leftarrow T_1+T_2\pmod{2^{32}}.
\]

This happens for:

\[
t=0,1,\ldots,63.
\]

![SHA-256 structure](/images/hash-functions/merkle-damgard-sha256/sha256.png)

### Feed-forward

After the 64 rounds, the working words are not returned directly.

Instead:

\[
H_0'
=
H_0+a
\pmod{2^{32}},
\]

\[
H_1'
=
H_1+b
\pmod{2^{32}},
\]

and so on through:

\[
H_7'
=
H_7+h
\pmod{2^{32}}.
\]

The result becomes the next chaining state.

For the final message block, concatenating the eight words gives the SHA-256 digest.

### Round constants

The 64 constants:

\[
K_0,\ldots,K_{63}
\]

come from the fractional parts of cube roots of the first 64 prime numbers.

Like the IV values, these constants are:

- public,
- deterministic,
- reproducible,
- not keys.

Their purpose is to break symmetries and provide fixed round differentiation.

### Why addition matters

SHA-256 mixes several operation families:

- XOR,
- AND,
- NOT,
- rotations,
- logical shifts,
- addition modulo \(2^{32}\).

Modular addition is nonlinear with respect to bitwise XOR because carries propagate between bit positions.

This is one reason SHA-256 should not be thought of as a purely linear bit-mixing system.

---

## Educational Implementation and Verification

A useful educational SHA-256 implementation should be auditable rather than optimized.

The component boundaries should match the specification:

```text
sha256_padding(length)
        |
        v
parse 64-byte blocks
        |
        v
message schedule W[0..63]
        |
        v
64-round compression
        |
        v
feed-forward
        |
        v
next chaining state
```

The repository implementation:

[`code/sha256_educational.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha256_educational.py)

is organized around this structure.

### Keep messages as byte strings

One subtle but important implementation lesson is:

> do not convert the complete message to one integer and later try to recover its original byte representation.

For example:

```python
int.from_bytes(
    b"\x00abc",
    "big",
)
```

produces the same integer value as:

```python
int.from_bytes(
    b"abc",
    "big",
)
```

because the leading zero byte does not affect the integer.

But the two messages have different lengths:

```text
00 61 62 63
61 62 63
```

and therefore require different SHA-256 padding.

Padding is defined over the exact bit string.

So messages should remain byte strings until individual fixed-width words are parsed.

### A complete minimal SHA-256 implementation

The following implementation is intentionally direct.

```python
import struct


MASK32 = 0xFFFFFFFF


IV = (
    0x6A09E667,
    0xBB67AE85,
    0x3C6EF372,
    0xA54FF53A,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
    0x5BE0CD19,
)


K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
    0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
    0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC,
    0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7,
    0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
    0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3,
    0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5,
    0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
    0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)


def rotr(x, r):
    return (
        (x >> r)
        |
        (x << (32 - r))
    ) & MASK32


def ch(x, y, z):
    return (
        (x & y)
        ^ ((~x) & z)
    ) & MASK32


def maj(x, y, z):
    return (
        (x & y)
        ^ (x & z)
        ^ (y & z)
    ) & MASK32


def big_sigma0(x):
    return (
        rotr(x, 2)
        ^ rotr(x, 13)
        ^ rotr(x, 22)
    )


def big_sigma1(x):
    return (
        rotr(x, 6)
        ^ rotr(x, 11)
        ^ rotr(x, 25)
    )


def small_sigma0(x):
    return (
        rotr(x, 7)
        ^ rotr(x, 18)
        ^ (x >> 3)
    )


def small_sigma1(x):
    return (
        rotr(x, 17)
        ^ rotr(x, 19)
        ^ (x >> 10)
    )


def padding(length_bytes):
    bit_length = length_bytes * 8

    result = b"\x80"

    result += b"\x00" * (
        (
            56
            - (length_bytes + 1) % 64
        )
        % 64
    )

    result += bit_length.to_bytes(
        8,
        "big",
    )

    return result


def schedule(block):
    if len(block) != 64:
        raise ValueError(
            "SHA-256 compression needs 64 bytes"
        )

    w = list(
        struct.unpack(
            ">16I",
            block,
        )
    )

    for t in range(16, 64):
        value = (
            small_sigma1(w[t - 2])
            + w[t - 7]
            + small_sigma0(w[t - 15])
            + w[t - 16]
        ) & MASK32

        w.append(value)

    return w


def compress(state, block):
    w = schedule(block)

    a, b, c, d, e, f, g, h = state

    for t in range(64):
        t1 = (
            h
            + big_sigma1(e)
            + ch(e, f, g)
            + K[t]
            + w[t]
        ) & MASK32

        t2 = (
            big_sigma0(a)
            + maj(a, b, c)
        ) & MASK32

        h = g
        g = f
        f = e
        e = (d + t1) & MASK32
        d = c
        c = b
        b = a
        a = (t1 + t2) & MASK32

    return tuple(
        (
            old + new
        ) & MASK32
        for old, new in zip(
            state,
            (a, b, c, d, e, f, g, h),
        )
    )


def sha256(message):
    data = (
        message
        + padding(len(message))
    )

    state = IV

    for offset in range(
        0,
        len(data),
        64,
    ):
        state = compress(
            state,
            data[offset:offset + 64],
        )

    return b"".join(
        word.to_bytes(
            4,
            "big",
        )
        for word in state
    )
```

### Standard known-answer checks

The most famous SHA-256 test vector is:

\[
M=\texttt{"abc"}.
\]

Expected digest:

```text
ba7816bf8f01cfea414140de5dae2223
b00361a396177a9cb410ff61f20015ad
```

So:

```python
assert sha256(b"abc").hex() == (
    "ba7816bf8f01cfea414140de5dae2223"
    "b00361a396177a9cb410ff61f20015ad"
)
```

The empty-string vector is:

```text
e3b0c44298fc1c149afbf4c8996fb924
27ae41e4649b934ca495991b7852b855
```

These vectors are essential because they verify interoperability against the actual SHA-256 specification.

### Boundary tests

A good test suite should include:

```python
messages = [
    b"",
    b"abc",
    b"A" * 55,
    b"A" * 56,
    b"A" * 64,
    b"A" * 1000,
]
```

For every message:

```python
assert (
    sha256(message)
    ==
    hashlib.sha256(message).digest()
)
```

Why these lengths?

- `0`: empty-message vector,
- `3`: standard `"abc"` vector,
- `55`: last message length that keeps padding in one block,
- `56`: first length requiring an additional padding block,
- `64`: exact full message block plus padding block,
- `1000`: multi-block iteration.

### Known-answer testing is stronger than round trip

Unlike an encryption primitive, a hash does not have decryption.

So the common cipher test:

```text
decrypt(encrypt(m)) == m
```

does not exist here.

For hashes, correctness testing relies heavily on:

- published vectors,
- independent implementations,
- boundary cases,
- internal checkpoint values where available.

Comparing our implementation against `hashlib.sha256` is useful regression evidence.

It is not an independent security proof.

### The educational state interface

For the next article, it is useful to expose:

```python
digest_to_state(digest)
```

and:

```python
continue_from_state(
    state,
    suffix,
    previous_length,
)
```

not because production code should expose these interfaces, but because they make length extension visible.

A SHA-256 digest is exactly:

\[
8\times32=256
\]

bits of final chaining state.

That observation is the bridge to the next attack.

---

## Engineering Lessons and the Bridge to Length Extension

SHA-256 is widely used, but using it correctly depends on the surrounding protocol.

### Use maintained implementations

The educational implementation above exists to make:

- padding,
- schedule expansion,
- rounds,
- feed-forward,

auditable.

Production software should use a maintained cryptographic library or platform implementation.

Reasons include:

- optimized constant handling,
- tested endianness,
- platform acceleration,
- API safety,
- validation requirements,
- maintenance.

### A digest is not authentication

If a software vendor publishes:

```text
file.zip
SHA256(file.zip)
```

on the same compromised server, an attacker who replaces the file can replace the digest too.

A digest verifies integrity only when the expected value arrives through a trusted or authenticated channel.

For adversarial authenticity, use:

- a digital signature,
- a MAC,
- an authenticated protocol.

### Do not invent secret-prefix MACs

Avoid:

\[
\operatorname{SHA256}(K\|M)
\]

as an ad-hoc MAC.

Because SHA-256 is Merkle–Damgård based and exposes its final chaining state, this pattern is vulnerable to length extension under common conditions.

Use:

\[
\operatorname{HMAC\!-\!SHA256}_K(M)
\]

or the protocol's specified authentication primitive.

### Do not use SHA-256 directly for passwords

SHA-256 is deliberately fast.

Password verification requires a salted password-hashing scheme with tunable cost.

The hash primitive can be part of such a construction, but:

```text
SHA256(password)
```

is not a modern password-storage design.

### Canonical encoding still matters

Suppose structured data is serialized ambiguously before hashing.

Then the application can create semantic collisions even if SHA-256 itself is cryptographically strong.

Use:

- fixed field encodings,
- explicit lengths,
- canonical serialization,
- domain separation labels.

### Collision strength is not digest length

SHA-256 outputs:

\[
256
\]

bits.

Its ideal generic collision strength is therefore approximately:

\[
128
\]

bits, not 256.

The previous birthday article derived exactly why.

### SHA-256 and current standards

As of September 2026, the current final NIST Secure Hash Standard remains **FIPS 180-4**, which specifies the SHA-2 family including SHA-256.

NIST decided in 2023 to revise FIPS 180-4. The announced revision will remove the SHA-1 specification, incorporate suitable guidance from SP 800-107, improve editorial quality, and update references.

That planned revision does not mean SHA-256 has been withdrawn or replaced.

SHA-256 remains a current standardized hash algorithm.

The distinction between:

```text
current final standard
```

and:

```text
planned future revision
```

should remain explicit.

### Why the next article is length extension

We now have all the pieces needed for the attack.

We know that:

1. SHA-256 is an iterated hash;
2. the digest is the final chaining state;
3. padding is computable from message length;
4. compression can continue from an arbitrary internal state;
5. a naive secret-prefix MAC may expose a digest of:

\[
K\|M.
\]

Therefore the next question is immediate:

> If an attacker knows the final chaining state and can reconstruct the padding length, can the attacker continue hashing without knowing the secret prefix?

The answer is yes for the relevant Merkle–Damgård setting.

Importantly, this does **not** break:

- SHA-256 collision resistance,
- SHA-256 preimage resistance,
- the compression function directly.

It breaks an insecure **composition**.

That distinction is exactly why this series first established attack models before introducing the internal construction.

Previous: [Birthday Attacks](/blog/birthday-attacks-hash-functions/).

Next: [Length-Extension Attacks](/blog/length-extension-attacks/).

---

## Conclusion

Merkle–Damgård solves a fundamental engineering problem:

\[
\text{fixed-size compression}
\rightarrow
\text{arbitrary-length hash}.
\]

Its iteration is:

\[
h_0=IV,
\]

\[
h_i=f(h_{i-1},M_i),
\]

\[
H(M)=h_\ell.
\]

With an appropriate strengthening rule, collision resistance of the compression function can be transferred to the full iterated hash under the theorem's assumptions.

SHA-256 instantiates this general pattern with:

- 512-bit blocks,
- eight 32-bit state words,
- a 64-word schedule,
- 64 compression rounds,
- modular addition,
- Boolean functions,
- rotations and shifts,
- feed-forward into the chaining state.

The message schedule uses:

\[
\sigma_0,
\qquad
\sigma_1,
\]

while the round function uses:

\[
\Sigma_0,
\qquad
\Sigma_1,
\]

together with:

\[
\operatorname{Ch},
\qquad
\operatorname{Maj}.
\]

The construction is strong, practical, incremental, and standardized.

But its structure is visible.

That visible structure explains why we can discuss:

- length extension,
- multicollisions,
- herding,
- long-message second-preimage phenomena,

without claiming that SHA-256 itself is generally broken.

This is the main conceptual result of the article:

\[
\boxed{
\text{security of the compression function}
\neq
\text{every possible security property of the iterated construction}
}
\]

and:

\[
\boxed{
\text{security of the hash}
\neq
\text{security of every protocol that uses the hash}
}
\]

Those distinctions lead directly to the next chapter, where the Merkle–Damgård state interface is no longer merely an implementation detail—it becomes the mechanism behind a concrete **length-extension attack**.

---

## References

1. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**, August 2015.  
   https://doi.org/10.6028/NIST.FIPS.180-4

2. National Institute of Standards and Technology, **Decision to Revise FIPS 180-4, Secure Hash Standard**, March 2023.  
   https://csrc.nist.gov/news/2023/decision-to-revise-fips-180-4

3. I. Damgård, **A Design Principle for Hash Functions**, CRYPTO '89.

4. R. C. Merkle, **One Way Hash Functions and DES**, CRYPTO '89.

5. B. Preneel, R. Govaerts, and J. Vandewalle, **Hash Functions Based on Block Ciphers: A Synthetic Approach**, CRYPTO '93.

6. A. Joux, **Multicollisions in Iterated Hash Functions: Application to Cascaded Constructions**, CRYPTO 2004.

7. J. Kelsey and B. Schneier, **Second Preimages on n-bit Hash Functions for Much Less than \(2^n\) Work**, EUROCRYPT 2005.

8. J. Kelsey and T. Kohno, **Herding Hash Functions and the Nostradamus Attack**, EUROCRYPT 2006.

9. Python Software Foundation, **`hashlib` — Secure hashes and message digests**.  
   https://docs.python.org/3/library/hashlib.html
