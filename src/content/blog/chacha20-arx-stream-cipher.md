---
title: "ChaCha20: ARX Design, Quarter Rounds, Counters, and Nonce Discipline"
description: "Build the RFC 8439 ChaCha20 block function from modular addition, rotation, and XOR; derive the quarter-round and double-round schedule; verify official vectors; and connect counter/nonce discipline to stream-cipher and AEAD security."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Symmetric Cryptography"
  - "Cryptographic Engineering"
  - "Randomness & Entropy"
tags:
  - "chacha20"
  - "arx"
  - "rfc-8439"
  - "stream-cipher"
  - "nonce"
  - "quarter-round"
  - "counter"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 6
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---

## Table of Contents

- [Why ChaCha20 Looks Different from the Earlier Generators](#why-chacha20-looks-different-from-the-earlier-generators)
- [The RFC 8439 State Layout](#the-rfc-8439-state-layout)
- [The Quarter Round: Addition, XOR, and Rotation](#the-quarter-round-addition-xor-and-rotation)
- [Column Rounds, Diagonal Rounds, and the 20-Round Block Function](#column-rounds-diagonal-rounds-and-the-20-round-block-function)
- [From Block Function to Stream Cipher](#from-block-function-to-stream-cipher)
- [Nonce and Counter Discipline](#nonce-and-counter-discipline)
- [Raw ChaCha20 versus ChaCha20-Poly1305](#raw-chacha20-versus-chacha20-poly1305)
- [Executable RFC 8439 Implementation and Test Vectors](#executable-rfc-8439-implementation-and-test-vectors)
- [Security Perspective and Engineering Lessons](#security-perspective-and-engineering-lessons)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why ChaCha20 Looks Different from the Earlier Generators

The previous articles deliberately studied generators whose structure becomes exploitable:

```text
LCG
    -> affine recurrence modulo m

LFSR
    -> linear recurrence over GF(2)

Geffe
    -> nonlinear combiner with exploitable correlation

RC4
    -> state permutation with measurable keystream biases
```

ChaCha20 represents a different design philosophy.

Its core is built from only three operation families:

\[
\boxed{
\text{Addition}
+
\text{Rotation}
+
\text{XOR}
}
\]

which gives the common abbreviation:

\[
\boxed{\text{ARX}}.
\]

There are:

- no lookup-table S-boxes;
- no LFSR recurrence;
- no RC4-style key-scheduled byte permutation;
- no secret-dependent memory accesses in the abstract algorithm.

The state is sixteen 32-bit words, and the same small **quarter-round** transformation is applied repeatedly in a carefully arranged schedule.

### Why ARX is interesting

Two of the three operations are linear over bit vectors:

- XOR;
- rotation.

Modular addition is different.

The operation:

\[
a+b\pmod{2^{32}}
\]

creates carry bits.

Those carries make addition nonlinear over:

\[
\mathbb F_2.
\]

So ChaCha20 combines:

- XOR for mixing;
- rotations for moving bit influence across positions;
- modular addition for carry-based nonlinearity.

The result is a compact software-oriented design whose security does not depend on hiding its structure.

### A modern security claim is more than "it is nonlinear"

The Geffe article already showed that nonlinearity alone is not enough.

ChaCha20's confidence comes from a much stronger combination:

- deliberately designed diffusion;
- 20-round structure;
- extensive public cryptanalysis;
- fixed parameters;
- explicit key/nonce/counter interface;
- standardized test vectors;
- well-defined protocol integration.

The goal is not merely to make output *look complicated*.

The goal is to make distinguishing, key recovery, and useful prediction computationally infeasible under the specified model.

### RFC 8439 scope

This article follows the IETF/CFRG variant specified by RFC 8439:

\[
\text{key}=256\text{ bits},
\]

\[
\text{nonce}=96\text{ bits},
\]

\[
\text{block counter}=32\text{ bits}.
\]

Older ChaCha descriptions used other layouts, including a 64-bit nonce with a 64-bit counter.

Those are different variants.

For this series, **ChaCha20 means the RFC 8439 layout unless explicitly stated otherwise**.

---

## The RFC 8439 State Layout

The ChaCha20 block function operates on sixteen unsigned 32-bit words:

\[
x_0,x_1,\ldots,x_{15}.
\]

They are displayed as a \(4\times4\) matrix:

\[
\begin{bmatrix}
x_0 & x_1 & x_2 & x_3\\
x_4 & x_5 & x_6 & x_7\\
x_8 & x_9 & x_{10} & x_{11}\\
x_{12} & x_{13} & x_{14} & x_{15}
\end{bmatrix}.
\]

For RFC 8439, the layout is:

\[
\boxed{
\begin{bmatrix}
c_0&c_1&c_2&c_3\\
k_0&k_1&k_2&k_3\\
k_4&k_5&k_6&k_7\\
ctr&n_0&n_1&n_2
\end{bmatrix}
}
\]

where:

- \(c_0,\ldots,c_3\) are fixed constants;
- \(k_0,\ldots,k_7\) are the 256-bit key;
- \(ctr\) is the 32-bit block counter;
- \(n_0,n_1,n_2\) are the 96-bit nonce.

### Constants

The first 16 bytes are the ASCII string:

```text
expand 32-byte k
```

Parsed as four little-endian 32-bit words, they become:

\[
c_0=\texttt{0x61707865},
\]

\[
c_1=\texttt{0x3320646e},
\]

\[
c_2=\texttt{0x79622d32},
\]

\[
c_3=\texttt{0x6b206574}.
\]

These constants are public.

They help define the ChaCha20 function domain and state format; they are not secret key material.

### Key words

The 32-byte key is split into eight groups of four bytes.

Each group is interpreted little-endian.

For example, the first four key bytes:

```text
00 01 02 03
```

become:

\[
k_0=\texttt{0x03020100}.
\]

This byte order matters.

A big-endian implementation can have the correct-looking round structure and still fail every RFC vector.

### Counter

Word \(12\) is the 32-bit block counter.

Each block function invocation produces:

\[
64\text{ bytes}
\]

of keystream.

So the counter identifies which 64-byte keystream block is being generated.

### Nonce

Words \(13,14,15\) contain the 96-bit nonce.

The nonce is parsed as three little-endian 32-bit words.

The nonce is public, but under RFC 8439 it:

\[
\boxed{
\text{MUST NOT repeat for the same key}.
}
\]

This is not a recommendation to keep it secret.

It is a uniqueness requirement.

---

## The Quarter Round: Addition, XOR, and Rotation

The quarter round is the basic transformation of ChaCha20.

It takes four 32-bit words:

\[
(a,b,c,d)
\]

and updates them in place.

The sequence is:

```text
a += b; d ^= a; d <<<= 16
c += d; b ^= c; b <<<= 12
a += b; d ^= a; d <<<=  8
c += d; b ^= c; b <<<=  7
```

All additions are modulo:

\[
2^{32}.
\]

### Formal definition

Write:

\[
\operatorname{ROTL}_r(x)
\]

for 32-bit left rotation by \(r\) positions.

Then:

\[
a\leftarrow a+b\pmod{2^{32}},
\]

\[
d\leftarrow\operatorname{ROTL}_{16}(d\oplus a),
\]

\[
c\leftarrow c+d\pmod{2^{32}},
\]

\[
b\leftarrow\operatorname{ROTL}_{12}(b\oplus c),
\]

\[
a\leftarrow a+b\pmod{2^{32}},
\]

\[
d\leftarrow\operatorname{ROTL}_{8}(d\oplus a),
\]

\[
c\leftarrow c+d\pmod{2^{32}},
\]

\[
b\leftarrow\operatorname{ROTL}_{7}(b\oplus c).
\]

The rotation distances are therefore:

\[
16,\ 12,\ 8,\ 7.
\]

### Why mask to 32 bits

In a language with fixed-width unsigned 32-bit arithmetic, overflow naturally reduces modulo \(2^{32}\).

Python integers do not overflow.

So an educational implementation must mask:

```python
MASK32 = 0xffffffff
```

after modular additions.

For example:

```python
a = (a + b) & MASK32
```

Without the mask, the implementation is no longer ChaCha20.

### Rotation

A 32-bit left rotation can be written:

```python
def rotl32(x, n):
    return (
        ((x << n) & 0xffffffff)
        | (x >> (32 - n))
    )
```

Unlike a left shift, rotation does not discard the high bits.

They wrap around into the low positions.

### Why addition changes the algebra

XOR satisfies:

\[
(x\oplus y)\oplus z
=
x\oplus(y\oplus z)
\]

inside a vector space over \(\mathbb F_2\).

Rotation is also a linear permutation of bit positions.

But modular addition introduces carry propagation.

For example:

```text
01111111
+00000001
---------
10000000
```

One low-order input change can alter several higher bits through carries.

Repeated interaction among addition, rotation, and XOR spreads such effects across words and bit positions.

### RFC quarter-round vector

RFC 8439 gives:

\[
a=\texttt{0x11111111},
\]

\[
b=\texttt{0x01020304},
\]

\[
c=\texttt{0x9b8d6f43},
\]

\[
d=\texttt{0x01234567}.
\]

After one quarter round:

\[
a=\texttt{0xea2a92f4},
\]

\[
b=\texttt{0xcb1cf8ce},
\]

\[
c=\texttt{0x4581472e},
\]

\[
d=\texttt{0x5881c4bb}.
\]

That small vector is extremely valuable because it isolates:

- addition;
- masking;
- XOR;
- rotation directions;
- rotation distances.

If the quarter-round vector fails, there is no reason to debug the full block function yet.

---

## Column Rounds, Diagonal Rounds, and the 20-Round Block Function

ChaCha20 does not apply the quarter round to four consecutive words repeatedly.

It alternates between **column** and **diagonal** groupings so information moves across the entire \(4\times4\) state.

### Column round

The four column quarter rounds are:

\[
QR(0,4,8,12),
\]

\[
QR(1,5,9,13),
\]

\[
QR(2,6,10,14),
\]

\[
QR(3,7,11,15).
\]

Graphically:

```text
 0   1   2   3
 |   |   |   |
 4   5   6   7
 |   |   |   |
 8   9  10  11
 |   |   |   |
12  13  14  15
```

Each vertical group is transformed independently during that round.

### Diagonal round

Then the grouping changes:

\[
QR(0,5,10,15),
\]

\[
QR(1,6,11,12),
\]

\[
QR(2,7,8,13),
\]

\[
QR(3,4,9,14).
\]

This causes words that interacted only within one column to interact across new positions.

### Double round

One column round plus one diagonal round is commonly called a **double round**.

ChaCha20 performs:

\[
10
\]

double rounds.

That is:

\[
20
\]

rounds total.

Since every round contains four quarter rounds, the complete transformation performs:

\[
20\cdot4
=
80
\]

quarter rounds.

### Why alternate column and diagonal structure

If the algorithm repeatedly mixed only columns, each column would remain an independent subsystem.

The diagonal round breaks that separation.

After repeated alternation, input differences diffuse across:

- words;
- rows;
- columns;
- bit positions.

This is the central structural reason for the schedule.

### Feed-forward addition

After the 20 rounds, ChaCha20 does **not** serialize the transformed state directly.

Let the initial state be:

\[
X
\]

and the state after 20 rounds be:

\[
X'.
\]

The block function computes:

\[
Y_i
=
X'_i+X_i
\pmod{2^{32}}
\]

for all sixteen words.

Then \(Y\) is serialized little-endian.

This feed-forward step is essential.

It is part of the ChaCha20 block function, not an optional postprocessing step.

### 64-byte block

The sixteen final words are each 32 bits:

\[
16\cdot32
=
512\text{ bits}.
\]

Therefore the block output is:

\[
64\text{ bytes}.
\]

The words are serialized one by one in little-endian byte order.

---

## From Block Function to Stream Cipher

The block function maps:

\[
(K,\operatorname{counter},N)
\]

to one 64-byte keystream block.

Write:

\[
KS_j
=
\operatorname{ChaCha20Block}
(
K,j,N
).
\]

For a message longer than 64 bytes, increment the block counter:

\[
KS_j,
KS_{j+1},
KS_{j+2},
\ldots
\]

and concatenate the blocks.

Encryption is:

\[
C=P\oplus KS.
\]

Decryption is identical:

\[
P=C\oplus KS.
\]

### Partial final block

The plaintext length need not be a multiple of 64 bytes.

If the final plaintext block has only \(r<64\) bytes, generate one complete keystream block but use only its first \(r\) bytes.

The unused keystream bytes are discarded.

No padding is inherently required by ChaCha20 itself.

### Counter progression

If the initial counter is \(j_0\), the message blocks use:

\[
j_0,
j_0+1,
j_0+2,
\ldots
\]

without wrapping modulo \(2^{32}\) within one encryption context.

Once the counter space would wrap, that key/nonce context must not continue.

### Key/nonce/counter determine keystream

At a fixed block position:

\[
(K,N,j)
\]

determines the keystream block completely.

Therefore repeating the same triple gives the same block:

\[
\operatorname{ChaCha20Block}(K,N,j)
=
\operatorname{ChaCha20Block}(K,N,j).
\]

That sounds trivial, but it is the operational heart of stream-cipher safety.

---

## Nonce and Counter Discipline

ChaCha20 is secure only when its operational contract is respected.

The most important rule is:

\[
\boxed{
\text{do not repeat a nonce under the same key}.
}
\]

RFC 8439 states this requirement explicitly.

### Why nonce reuse is catastrophic

Suppose two plaintexts are encrypted using the same key, nonce, and overlapping counter positions.

Then they receive the same keystream:

\[
C_1=P_1\oplus KS,
\]

\[
C_2=P_2\oplus KS.
\]

XORing gives:

\[
\boxed{
C_1\oplus C_2
=
P_1\oplus P_2.
}
\]

This is exactly the two-time-pad failure studied earlier in the series.

ChaCha20's strong round function cannot rescue nonce reuse.

### The nonce is not a password

A 96-bit nonce does not need to remain secret.

It can be transmitted with the ciphertext.

Its role is to make the block-function input unique under one key.

### Deterministic uniqueness is often preferable

If the protocol can maintain persistent state, a monotonically increasing nonce or structured counter allocation can prevent accidental repeats.

This can be easier to reason about than sampling random nonces and relying on collision probability.

RFC 8439 discusses partitioning nonce space when multiple senders share a key, for example by reserving part of the nonce for a sender identifier and using the remaining part as a counter.

The exact scheme belongs to the protocol.

### Counter limit

The RFC 8439 variant has a 32-bit block counter.

Since each block is 64 bytes, the raw addressable block space per key/nonce pair is:

\[
2^{32}\cdot64
=
2^{38}
\text{ bytes}
=
256\text{ GiB}.
\]

Operationally, the counter must not wrap.

If a construction reserves counter value 0 for another purpose—as ChaCha20-Poly1305 does when deriving the Poly1305 one-time key—then payload encryption starts at counter 1 and one block of the theoretical counter space is unavailable for plaintext.

### Multi-sender systems

Nonce uniqueness is harder when several machines share one key.

If every sender independently begins at:

```text
nonce = 0
```

the system immediately repeats nonce values.

Possible strategies include:

- partitioning nonce space by sender;
- assigning disjoint persistent ranges;
- using a protocol-level sequence number;
- deriving separate keys per sender.

The important requirement is global uniqueness under the effective key.

### Reboot, rollback, and cloning

A counter strategy can fail after:

- VM snapshot rollback;
- device cloning;
- database restore;
- lost persistent state;
- process restart;
- multiple nodes reusing one key.

So nonce discipline is partly systems engineering.

This is the same lesson seen throughout the series:

\[
\boxed{
\text{strong primitive}
+
\text{broken state management}
=
\text{broken protocol}.
}
\]

---

## Raw ChaCha20 versus ChaCha20-Poly1305

ChaCha20 by itself is a stream cipher.

It provides confidentiality under its security assumptions.

It does **not** authenticate:

- ciphertext;
- headers;
- associated metadata;
- sender intent.

### Malleability

Suppose:

\[
C=P\oplus KS.
\]

An attacker sends:

\[
C'=C\oplus\Delta.
\]

The receiver decrypts:

\[
P'
=
C'\oplus KS
=
P\oplus\Delta.
\]

So an attacker can induce chosen bit flips without knowing the key.

This is inherent to unauthenticated stream encryption.

### ChaCha20-Poly1305

RFC 8439 also defines the AEAD construction:

\[
\text{ChaCha20-Poly1305}.
\]

At a high level:

1. use ChaCha20 block counter 0 to derive a one-time Poly1305 key;
2. encrypt plaintext using ChaCha20 beginning with counter 1;
3. authenticate:
   - associated data;
   - ciphertext;
   - lengths;
4. output ciphertext plus a 128-bit Poly1305 tag.

The AEAD construction therefore adds integrity/authenticity to the confidentiality provided by ChaCha20.

### Counter 0 has a special AEAD role

This is why RFC 8439 notes that a standalone ChaCha20 initial counter may often be 0 or 1.

In the AEAD construction, block counter 0 is used for key derivation, and actual message encryption begins at:

\[
1.
\]

That distinction is protocol-specific and should not be hidden inside a generic "ChaCha20" helper without documentation.

### Associated data

AEAD can authenticate metadata without encrypting it.

Examples include:

- protocol headers;
- sequence numbers;
- routing context.

That is fundamentally different from raw ChaCha20, which simply transforms plaintext bytes with XOR.

---

## Executable RFC 8439 Implementation and Test Vectors

The educational implementation should be small enough to audit but exact enough to reproduce the RFC.

### 32-bit rotation

```python
MASK32 = 0xffffffff


def rotl32(x, n):
    x &= MASK32

    return (
        ((x << n) & MASK32)
        | (x >> (32 - n))
    )
```

### Quarter round

```python
def quarter_round(a, b, c, d):
    a = (a + b) & MASK32
    d ^= a
    d = rotl32(d, 16)

    c = (c + d) & MASK32
    b ^= c
    b = rotl32(b, 12)

    a = (a + b) & MASK32
    d ^= a
    d = rotl32(d, 8)

    c = (c + d) & MASK32
    b ^= c
    b = rotl32(b, 7)

    return a, b, c, d
```

### Quarter-round known-answer test

```python
assert quarter_round(
    0x11111111,
    0x01020304,
    0x9b8d6f43,
    0x01234567,
) == (
    0xea2a92f4,
    0xcb1cf8ce,
    0x4581472e,
    0x5881c4bb,
)
```

This is the RFC 8439 Section 2.1.1 vector.

### Apply a quarter round to state words

```python
def qr_state(
    state,
    a,
    b,
    c,
    d,
):
    (
        state[a],
        state[b],
        state[c],
        state[d],
    ) = quarter_round(
        state[a],
        state[b],
        state[c],
        state[d],
    )
```

### One double round

```python
def double_round(state):
    # Columns
    qr_state(state, 0, 4, 8, 12)
    qr_state(state, 1, 5, 9, 13)
    qr_state(state, 2, 6, 10, 14)
    qr_state(state, 3, 7, 11, 15)

    # Diagonals
    qr_state(state, 0, 5, 10, 15)
    qr_state(state, 1, 6, 11, 12)
    qr_state(state, 2, 7, 8, 13)
    qr_state(state, 3, 4, 9, 14)
```

### Construct the RFC state

```python
import struct


CONSTANTS = (
    0x61707865,
    0x3320646e,
    0x79622d32,
    0x6b206574,
)


def words_le(data):
    return list(
        struct.unpack(
            "<" + "I" * (len(data) // 4),
            data,
        )
    )


def chacha20_block(
    key,
    counter,
    nonce,
):
    if len(key) != 32:
        raise ValueError(
            "ChaCha20 key must be 32 bytes"
        )

    if len(nonce) != 12:
        raise ValueError(
            "RFC 8439 nonce must be 12 bytes"
        )

    if not 0 <= counter < 2**32:
        raise ValueError(
            "counter must fit in 32 bits"
        )

    initial = (
        list(CONSTANTS)
        + words_le(key)
        + [counter]
        + words_le(nonce)
    )

    working = initial.copy()

    for _ in range(10):
        double_round(working)

    final = [
        (x + y) & MASK32
        for x, y in zip(
            working,
            initial,
        )
    ]

    return b"".join(
        struct.pack("<I", word)
        for word in final
    )
```

### RFC 8439 block-function test vector

The Section 2.3.2 inputs are:

```text
key:
00 01 02 03 04 05 06 07
08 09 0a 0b 0c 0d 0e 0f
10 11 12 13 14 15 16 17
18 19 1a 1b 1c 1d 1e 1f

counter:
1

nonce:
00 00 00 09
00 00 00 4a
00 00 00 00
```

The expected 64-byte block is:

```text
10 f1 e7 e4 d1 3b 59 15
50 0f dd 1f a3 20 71 c4
c7 d1 f4 c7 33 c0 68 03
04 22 aa 9a c3 d4 6c 4e
d2 82 64 46 07 9f aa 09
14 c2 d7 05 d9 8b 02 a2
b5 12 9c d1 de 16 4e b9
cb d0 83 e8 a2 50 3c 4e
```

### Stream encryption wrapper

```python
def chacha20_encrypt(
    key,
    nonce,
    initial_counter,
    plaintext,
):
    output = bytearray()

    blocks = (
        len(plaintext) + 63
    ) // 64

    if initial_counter + blocks > 2**32:
        raise ValueError(
            "ChaCha20 counter would wrap"
        )

    for block_index in range(blocks):
        counter = (
            initial_counter
            + block_index
        )

        keystream = chacha20_block(
            key,
            counter,
            nonce,
        )

        chunk = plaintext[
            64 * block_index:
            64 * (block_index + 1)
        ]

        output.extend(
            p ^ k
            for p, k in zip(
                chunk,
                keystream,
            )
        )

    return bytes(output)
```

This explicitly checks that the 32-bit counter does not wrap.

### Full encryption vector

RFC 8439 also provides a multi-block encryption test using the plaintext beginning:

```text
Ladies and Gentlemen of the class of '99...
```

with:

- the same incremental 256-bit key;
- nonce `000000000000004a00000000`;
- initial counter 1.

Testing the complete encryption vector is useful because it validates:

- block 1;
- block 2;
- counter increment;
- partial final block;
- XOR logic.

### What a passing vector proves

A known-answer test provides strong evidence of **implementation compatibility**.

It does not prove ChaCha20 secure.

Security confidence comes from the design and cryptanalysis.

The vector tells us that our code is actually implementing the intended function rather than a nearby accidental variant.

---

## Security Perspective and Engineering Lessons

ChaCha20 is an instructive contrast with every generator studied earlier in the series.

### Unlike an LCG

There is no recurrence such as:

\[
S_{i+1}=aS_i+c\pmod m
\]

whose parameters can be solved from a few output words.

### Unlike a raw LFSR

The keystream does not satisfy a small exposed linear recurrence over:

\[
\mathbb F_2.
\]

### Unlike Geffe

The design is not a tiny Boolean combiner whose output has an obvious \(3/4\) correlation with one internal source.

### Unlike RC4

There is no byte-level KSA followed by immediate output from a biased permutation process.

Instead, every block begins from a fully specified state containing:

- key;
- nonce;
- counter;
- constants;

and passes through 20 rounds of ARX diffusion before feed-forward and serialization.

### Reduced-round analysis matters

Cryptanalysts often study reduced-round ChaCha variants.

That is not evidence that full ChaCha20 is broken.

Reduced-round attacks help measure how much security margin the full 20-round construction has beyond the best known attack.

This is how modern cipher evaluation works:

\[
\boxed{
\text{study weaker round counts}
\rightarrow
\text{understand margin of full design}.
}
\]

### Constant-time engineering

ChaCha20 has an implementation advantage: its abstract operations do not require secret-indexed lookup tables.

That makes constant-time software easier to implement than many table-based designs.

But "ARX" does not automatically make every implementation side-channel safe.

Real code still has to avoid:

- secret-dependent branches;
- accidental compiler transformations;
- unsafe key handling;
- nonce reuse;
- API misuse.

### A strong cipher does not replace protocol design

Even perfect implementation of ChaCha20 does not give:

- authentication;
- replay protection;
- nonce allocation;
- key rotation;
- domain separation.

Those remain protocol responsibilities.

For most modern applications, use a reviewed **AEAD API** rather than directly assembling raw ChaCha20 encryption.

---

## Conclusion

ChaCha20 marks a major shift in the series.

The earlier generators taught us how simple structure leaks information:

\[
\text{LCG}
\rightarrow
\text{affine predictability},
\]

\[
\text{LFSR}
\rightarrow
\text{linear recurrence recovery},
\]

\[
\text{Geffe}
\rightarrow
\text{correlation attack},
\]

\[
\text{RC4}
\rightarrow
\text{keystream bias}.
\]

ChaCha20 uses a carefully designed ARX transformation:

\[
\boxed{
\text{addition}
+
\text{rotation}
+
\text{XOR}.
}
\]

Its RFC 8439 state is:

\[
\begin{bmatrix}
\text{constants}\\
\text{256-bit key}\\
\text{32-bit counter + 96-bit nonce}
\end{bmatrix}
\]

organized as sixteen 32-bit words.

The quarter round repeatedly applies:

\[
16,\ 12,\ 8,\ 7
\]

bit rotations around modular additions and XORs.

Four column quarter rounds followed by four diagonal quarter rounds form a double round.

Ten double rounds give:

\[
20
\]

rounds and:

\[
80
\]

quarter rounds.

Finally, the transformed state is added to the original state and serialized little-endian into:

\[
64
\]

keystream bytes.

The stream-cipher interface is then simple:

\[
KS_j
=
\operatorname{ChaCha20Block}(K,j,N),
\]

\[
C=P\oplus KS.
\]

But that simplicity leaves one operational rule non-negotiable:

\[
\boxed{
\text{never repeat a nonce under the same key}.
}
\]

If keystream overlaps, the old two-time-pad identity returns:

\[
C_1\oplus C_2
=
P_1\oplus P_2.
\]

ChaCha20 itself provides confidentiality only.

ChaCha20-Poly1305 adds authentication and associated-data protection and is therefore the form normally exposed by modern protocol APIs.

The deeper lesson is that modern stream-cipher security comes from several layers working together:

\[
\boxed{
\text{well-analyzed core}
+
\text{fixed parameters}
+
\text{exact serialization}
+
\text{nonce discipline}
+
\text{counter discipline}
+
\text{authenticated protocol use}.
}
\]

That is a very different mindset from:

> "take a PRNG and XOR its output with the message."

The next article can now turn from a trusted modern design to a very different generator-security story: **Dual_EC_DRBG**, where the central issue is not an obvious statistical bias or linear recurrence, but parameter trust and the possibility of a hidden mathematical trapdoor.


---

## References

1. Y. Nir and A. Langley, **RFC 8439: ChaCha20 and Poly1305 for IETF Protocols**, June 2018.  
   https://www.rfc-editor.org/rfc/rfc8439

2. D. J. Bernstein, **ChaCha, a Variant of Salsa20**, Workshop Record of SASC 2008.

3. J.-P. Aumasson, S. Fischer, S. Khazaei, W. Meier, and C. Rechberger, **New Features of Latin Dances: Analysis of Salsa, ChaCha, and Rumba**, Fast Software Encryption, 2008.

4. Z. Shi, B. Zhang, D. Feng, and W. Wu, **Improved Key Recovery Attacks on Reduced-Round Salsa20 and ChaCha**, ICISC 2012.

5. Y. Nir and A. Langley, **RFC 7539: ChaCha20 and Poly1305 for IETF Protocols**, May 2015 — obsolete; superseded by RFC 8439.
