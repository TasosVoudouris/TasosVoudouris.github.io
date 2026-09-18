---
title: "Sponge Construction, Keccak, and SHA-3"
description: "Study sponge absorb/squeeze mechanics, Keccak-f[1600], SHA-3/SHAKE domain separation, the role of rate and capacity, the five Keccak round steps, and why sponge-based hashing differs structurally from Merkle–Damgård."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptographic Engineering"
  - "Mathematical Foundations"
tags:
  - "sha3"
  - "keccak"
  - "sponge"
  - "shake"
  - "keccak-f1600"
  - "domain-separation"
  - "fips-202"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 6
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [From Merkle–Damgård to the Sponge Paradigm](#from-merkledamgård-to-the-sponge-paradigm)
- [Absorb, Squeeze, Rate, and Capacity](#absorb-squeeze-rate-and-capacity)
- [Padding, Domain Separation, and the Standard SHA-3 Instances](#padding-domain-separation-and-the-standard-sha-3-instances)
- [Inside Keccak-f\[1600\]](#inside-keccak-f1600)
- [Why SHA-3 Does Not Expose the Same Length-Extension Interface](#why-sha-3-does-not-expose-the-same-length-extension-interface)
- [SHA-3, SHAKE, cSHAKE, KMAC, TupleHash, and ParallelHash](#sha-3-shake-cshake-kmac-tuplehash-and-parallelhash)
- [Educational Implementation and Verification](#educational-implementation-and-verification)
- [Engineering Lessons and Conclusion](#engineering-lessons-and-conclusion)
- [References](#references)

---

## From Merkle–Damgård to the Sponge Paradigm

The previous articles studied SHA-256 as a Merkle–Damgård hash.

Its high-level structure was:

\[
h_i=f(h_{i-1},M_i),
\]

where each message block is processed by a compression function and the final chaining value becomes the digest.

SHA-3 is built very differently.

It is not:

> SHA-2 with a different constant table or more rounds.

The SHA-3 family is based on **Keccak**, whose central abstraction is a **sponge construction** driven by a public fixed-width permutation.

The state does not shrink from:

\[
n+b
\]

bits down to:

\[
n
\]

bits after every block as in a compression function.

Instead, the sponge maintains one fixed-width internal state:

\[
S\in\{0,1\}^{b}
\]

and repeatedly applies a permutation:

\[
f:\{0,1\}^{b}\rightarrow\{0,1\}^{b}.
\]

For Keccak-f[1600],

\[
b=1600.
\]

The state is split conceptually into:

\[
b=r+c,
\]

where:

- \(r\) is the **rate**;
- \(c\) is the **capacity**.

Only the rate portion directly absorbs message bits or exposes output bits.

The capacity remains internal.

![Sponge absorption and squeezing](/images/hash-functions/sponge-keccak-sha3/sponge.png)

This one architectural change has several consequences:

- input and output use the same internal permutation;
- arbitrary output lengths become natural;
- the output does not reveal the complete internal state;
- rate and capacity explicitly trade throughput against generic security bounds;
- domain separation can define several functions over the same underlying permutation.

### Compression-function hashing versus permutation-based hashing

A useful structural comparison is:

| Property | SHA-256 style | SHA-3 style |
|---|---|---|
| Core primitive | compression function | permutation |
| Internal state exposed as digest? | final chaining state is exposed | only part of sponge state is output |
| Message processing | compression iteration | absorb into rate, permute |
| Output | fixed digest | fixed digest or extendable output |
| Padding family | MD strengthening | multi-rate `pad10*1` plus domain suffix |
| Typical direct length extension | structurally relevant | same direct attack does not transfer |
| Main standard | FIPS 180-4 | FIPS 202 |

This does not make one family universally "better."

It means their internal security interfaces are different.

### Why use a permutation?

A permutation maps the state bijectively:

\[
f:\{0,1\}^{1600}\rightarrow\{0,1\}^{1600}.
\]

There is no compression inside \(f\).

Compression happens because the sponge:

- injects only \(r\) message bits per absorption block,
- hides \(c\) bits,
- returns only the requested output.

The security of the construction comes from the permutation plus the way input and output are restricted by the sponge interface.

This is a subtle but important shift.

In Merkle–Damgård, we reason about:

\[
\text{compression function}
+
\text{iteration}.
\]

In a sponge, we reason about:

\[
\text{permutation}
+
\text{rate/capacity interface}
+
\text{domain separation}.
\]

---

## Absorb, Squeeze, Rate, and Capacity

A sponge has two main phases:

\[
\boxed{\text{absorb}}
\]

followed by:

\[
\boxed{\text{squeeze}}.
\]

### Absorption

Initialize the full state to zero:

\[
S_0=0^b.
\]

Pad the message and divide it into \(r\)-bit blocks:

\[
M_1,M_2,\ldots,M_q.
\]

For each block:

\[
S_i
=
f
\left(
S_{i-1}
\oplus
(M_i\|0^c)
\right).
\]

Only the first \(r\) bits—the rate portion—receive the message block.

The capacity portion is not directly XORed with message data.

Conceptually:

```text
rate                     capacity
+------------------+------------------+
|  message block   |       hidden     |
+------------------+------------------+
         XOR into state
                |
                v
          permutation f
```

### Squeezing

After the final absorb permutation, read output from the rate portion.

If the caller needs at most \(r\) bits, no extra permutation is needed.

If more output is required:

1. emit the current rate portion;
2. apply \(f\);
3. emit another rate portion;
4. continue until enough bits have been produced.

This is why the same sponge architecture naturally supports an **extendable-output function**.

The output length is not necessarily fixed by the primitive.

### SHAKE is not "a digest with no fixed size"

For SHAKE, the caller chooses how many output bytes to request:

```python
hashlib.shake_256(message).digest(32)
hashlib.shake_256(message).digest(64)
hashlib.shake_256(message).digest(200)
```

These are three different output lengths from the same XOF invocation.

So the phrase:

> "the SHAKE256 digest"

is incomplete without an output length.

A better statement is:

```text
SHAKE256(message, 64 bytes)
```

or:

```text
SHAKE256(message, 512 output bits)
```

### Rate

The rate controls how many bits can be absorbed or emitted per permutation call.

For SHA3-256:

\[
r=1088.
\]

That is:

\[
136\text{ bytes}.
\]

So one Keccak-f[1600] permutation can absorb up to 136 padded message bytes at a time.

A larger rate generally means higher throughput because more data is handled per permutation.

### Capacity

For SHA3-256:

\[
c=512.
\]

Since:

\[
r+c=1600,
\]

we have:

\[
1088+512=1600.
\]

The capacity is deliberately not directly exposed.

At a high level, larger capacity gives stronger generic resistance bounds but leaves fewer rate bits and therefore reduces throughput.

This is one of the cleanest security/performance tradeoffs in hash construction design.

### Why capacity matters

If the entire 1600-bit state were directly visible after every operation, an attacker would have much more information about the permutation state.

The hidden capacity creates uncertainty about the full state.

For many sponge security arguments, the capacity determines the scale at which generic attacks or distinguishing behavior become relevant.

A useful intuition is:

\[
\text{larger }c
\Rightarrow
\text{more hidden state}
\Rightarrow
\text{stronger generic bound}.
\]

But the exact formal bound depends on:

- the construction,
- query model,
- output length,
- attack type.

It should not be reduced to one slogan.

### Fixed output adds another limit

Suppose a sponge construction returns only \(d\) output bits.

Then generic collision resistance cannot exceed:

\[
2^{d/2}
\]

regardless of capacity.

For SHA3-256:

\[
d=256,
\]

so the output length alone caps generic collision security at:

\[
2^{128}.
\]

This agrees with its intended classical collision strength.

### A sponge is not automatically a hash

The sponge is a general construction pattern.

By choosing:

- permutation,
- rate,
- capacity,
- suffix/domain,
- output length,

we can instantiate different functions.

That is exactly what FIPS 202 and SP 800-185 do.

---

## Padding, Domain Separation, and the Standard SHA-3 Instances

Keccak uses **multi-rate padding**, commonly written:

\[
\operatorname{pad10^*1}.
\]

At the bit level, this means:

1. append a `1`;
2. append zero or more `0` bits;
3. append a final `1`;

so that the padded input length is a multiple of the rate.

### Domain separation is part of the function

The standardized SHA-3 and SHAKE functions also use domain-separation suffixes.

In byte-oriented implementations, the familiar delimited suffix values are:

| Function family | Delimited suffix |
|---|---:|
| SHA3 fixed-output | `0x06` |
| SHAKE XOF | `0x1f` |

The final rate byte also receives the high padding bit:

```text
0x80
```

through XOR.

A compact byte-level final block looks like:

```python
block[len(remainder)] ^= suffix
block[-1] ^= 0x80
```

This represents the function's domain suffix together with the final `pad10*1` rule.

### Why raw Keccak-256 differs from SHA3-256

Raw Keccak-256 and standardized SHA3-256 can use:

- the same Keccak-f[1600] permutation,
- the same rate,
- the same capacity,

yet still produce different digests.

The reason is domain separation and padding conventions.

The standardized SHA3-256 function uses the SHA-3 domain suffix.

Therefore:

\[
\operatorname{Keccak256}(M)
\neq
\operatorname{SHA3\!-\!256}(M)
\]

in general.

This is not an implementation bug.

They are different functions.

That distinction is especially important in ecosystems where APIs use the names:

```text
keccak256
```

and:

```text
sha3_256
```

as separate primitives.

### FIPS 202 instances

The standardized instances are:

| Function | Rate \(r\) | Capacity \(c\) | Output |
|---|---:|---:|---:|
| SHA3-224 | 1152 | 448 | 224 bits |
| SHA3-256 | 1088 | 512 | 256 bits |
| SHA3-384 | 832 | 768 | 384 bits |
| SHA3-512 | 576 | 1024 | 512 bits |
| SHAKE128 | 1344 | 256 | variable |
| SHAKE256 | 1088 | 512 | variable |

For the fixed-output SHA-3 functions, the usual ideal generic collision strengths are:

\[
112,\ 128,\ 192,\ 256
\]

bits respectively.

### XOF output length still matters

SHAKE256 has a 512-bit capacity and is designed for up to a 256-bit security strength in the relevant generic sense.

But if an application asks for only:

\[
64
\]

output bits, the output itself cannot provide 256-bit collision or preimage security.

For a \(d\)-bit XOF output:

\[
\text{generic preimage ceiling}\le 2^d,
\]

\[
\text{generic collision ceiling}\le 2^{d/2}.
\]

So choosing an XOF does not remove the need to choose an appropriate output length.

### Rate boundary example for SHA3-256

SHA3-256 has:

\[
r=136\text{ bytes}.
\]

Therefore message lengths around:

```text
135 bytes
136 bytes
137 bytes
```

are excellent implementation tests.

A 135-byte message leaves one byte in the current rate block for suffix/padding interaction.

A 136-byte message fills one complete absorb block and requires a new padding block.

A 137-byte message crosses the boundary by one byte.

These cases catch many incorrect absorb and padding implementations.

---

## Inside Keccak-f[1600]

Keccak-f[1600] permutes a 1600-bit state.

The state is arranged as:

\[
A[x,y,z],
\]

where:

\[
x,y\in\{0,1,2,3,4\},
\]

and:

\[
z\in\{0,\ldots,63\}.
\]

For fixed \(x,y\), the 64 bits indexed by \(z\) form a **lane**.

So the 1600-bit state consists of:

\[
5\times5=25
\]

lanes, each 64 bits wide.

![Keccak state terminology](/images/hash-functions/sponge-keccak-sha3/state.png)

A convenient implementation stores:

```text
25 unsigned 64-bit integers
```

with coordinate flattening such as:

\[
\text{index}=x+5y.
\]

### Endianness

Each 64-bit lane is serialized little-endian.

This is a frequent implementation trap because SHA-256 uses big-endian 32-bit message words.

So these two articles deliberately use different parsing conventions:

```text
SHA-256:
    big-endian 32-bit words

Keccak/SHA-3:
    little-endian 64-bit lanes
```

Copying SHA-256-style byte order into SHA-3 code produces a structurally plausible but incompatible implementation.

### Twenty-four rounds

Keccak-f[1600] uses:

\[
24
\]

rounds.

Each round applies five named steps in this order:

\[
\boxed{
\theta
\rightarrow
\rho
\rightarrow
\pi
\rightarrow
\chi
\rightarrow
\iota
}
\]

The functional-composition notation may be written:

\[
\iota\circ\chi\circ\pi\circ\rho\circ\theta.
\]

The order matters.

---

### Theta: column-parity diffusion

Theta computes the parity of each state column.

In 64-bit lane notation:

\[
C[x]
=
A[x,0]
\oplus
A[x,1]
\oplus
A[x,2]
\oplus
A[x,3]
\oplus
A[x,4].
\]

Then:

\[
D[x]
=
C[x-1]
\oplus
\operatorname{ROTL}_1(C[x+1]),
\]

with \(x\) interpreted modulo 5.

Finally:

\[
A[x,y]
\leftarrow
A[x,y]\oplus D[x]
\]

for every lane.

![Theta diffusion](/images/hash-functions/sponge-keccak-sha3/keccak-theta.png)

Theta is linear over:

\[
\mathrm{GF}(2).
\]

Its role is diffusion.

A difference affecting one column parity influences neighboring columns after the update.

Because the same \(D[x]\) is XORed into all five lanes of a column, the state quickly develops inter-lane dependencies.

### Rho: coordinate-dependent rotations

Rho rotates each 64-bit lane by a fixed offset:

\[
A[x,y]
\longrightarrow
\operatorname{ROTL}_{r[x,y]}(A[x,y]).
\]

![Rho lane rotation](/images/hash-functions/sponge-keccak-sha3/rho.png)

The offsets depend on coordinates.

For example:

\[
r[0,0]=0.
\]

The lane at \((0,0)\) is therefore not rotated.

Other lanes use distinct offsets designed to distribute bit positions across subsequent rounds.

Rotation preserves all bits but changes their positions within the lane.

### Pi: lane permutation

Pi rearranges lane coordinates.

One common convention is:

\[
B[
y,\,
2x+3y
]
=
A[x,y],
\]

with coordinates modulo 5.

When Rho and Pi are implemented together:

\[
B[
y,\,
2x+3y
]
=
\operatorname{ROTL}_{r[x,y]}
(
A[x,y]
).
\]

![Pi lane movement](/images/hash-functions/sponge-keccak-sha3/pi.png)

Pi itself is a permutation of lane positions.

It does not alter lane bits.

Its purpose is to move information into different row/column relationships before Chi.

### Chi: nonlinear row mixing

Chi is the only nonlinear step of a Keccak round.

For each row:

\[
A'[x,y]
=
B[x,y]
\oplus
\left(
(\neg B[x+1,y])
\land
B[x+2,y]
\right).
\]

![Chi nonlinear propagation](/images/hash-functions/sponge-keccak-sha3/keccak-chi.png)

The Boolean structure:

\[
a\oplus((\neg b)\land c)
\]

introduces nonlinearity through the AND operation.

That nonlinearity is crucial.

If the entire permutation consisted only of XORs, rotations, and coordinate permutations, it would remain affine over the bit space and would not provide the required cryptographic behavior.

### Chi implementation trap

All output lanes in a row must be computed from the **old row values**.

This is wrong:

```python
for x in range(5):
    row[x] ^= (
        (~row[(x + 1) % 5])
        & row[(x + 2) % 5]
    )
```

because later iterations reuse already-updated values.

Instead:

```python
old = row.copy()

for x in range(5):
    row[x] = (
        old[x]
        ^ (
            (~old[(x + 1) % 5])
            & old[(x + 2) % 5]
        )
    )
```

In languages such as Python with unbounded integers, the complement should also be masked back to 64 bits.

### Iota: round asymmetry

Iota XORs a round constant into lane:

\[
A[0,0].
\]

For round \(i\):

\[
A[0,0]
\leftarrow
A[0,0]
\oplus
RC_i.
\]

Only one lane is modified directly.

The purpose is not diffusion—other round steps already provide that.

Iota breaks symmetries that could otherwise persist because every round uses the same structural transformations.

### Why the five-step design works together

The roles can be summarized as:

| Step | Main role |
|---|---|
| Theta | global-ish column parity diffusion |
| Rho | move bit positions within lanes |
| Pi | rearrange lanes |
| Chi | nonlinear row interaction |
| Iota | break round symmetry |

No single step should be evaluated in isolation.

Keccak's security comes from repeated interaction of all five transformations over 24 rounds.

---

## Why SHA-3 Does Not Expose the Same Length-Extension Interface

The previous article showed that SHA-256 secret-prefix constructions are vulnerable because:

\[
\operatorname{SHA256}(K\|M)
\]

publishes the complete final chaining state.

An attacker can parse that digest into eight words and continue the public compression function.

SHA3-256 behaves differently.

Its full internal state is:

\[
1600
\]

bits.

The function exposes only:

\[
256
\]

digest bits.

For SHA3-256:

\[
r=1088,
\qquad
c=512.
\]

The digest is output from the rate side, but the full post-permutation state is not published.

In particular, the attacker does not learn the hidden capacity bits.

Therefore the SHA-256 continuation procedure:

```text
digest
-> parse complete internal state
-> continue from that state
```

does not transfer directly to SHA3-256.

### This is not a recommendation for `SHA3-256(K || M)`

The conclusion is only:

> the classic exposed-state Merkle–Damgård length-extension mechanism does not apply in the same way.

That does not prove every improvised keyed sponge construction is secure.

For message authentication using the SHA-3 family, use a standardized keyed construction such as:

\[
\operatorname{KMAC}.
\]

The same lesson from the previous article still applies:

\[
\boxed{
\text{absence of one attack}
\neq
\text{proof of a custom MAC}
}
\]

### Hidden capacity as the structural difference

In SHA-256, the digest is enough to reconstruct:

\[
100\%
\]

of the chaining state.

In SHA3-256, the digest does not reveal the complete sponge state.

The missing internal information is not an accidental implementation detail.

It is fundamental to the sponge interface.

This is one of the clearest structural differences between the two hash families.

---

## SHA-3, SHAKE, cSHAKE, KMAC, TupleHash, and ParallelHash

FIPS 202 standardizes:

- four fixed-output SHA-3 hash functions;
- two SHAKE XOFs.

NIST SP 800-185 builds additional functions from the SHA-3/Keccak framework.

### SHA3-\(d\)

The fixed-output functions are:

\[
\operatorname{SHA3\!-\!224},
\]

\[
\operatorname{SHA3\!-\!256},
\]

\[
\operatorname{SHA3\!-\!384},
\]

\[
\operatorname{SHA3\!-\!512}.
\]

The output size is part of the function definition.

### SHAKE128 and SHAKE256

SHAKE functions are XOFs.

The caller chooses the output length.

For example:

```python
hashlib.shake_256(b"abc").digest(32)
```

and:

```python
hashlib.shake_256(b"abc").digest(200)
```

both use SHAKE256 but request different output sizes.

The longer result is not produced by concatenating independent SHAKE calls.

It is obtained by continuing the squeezing phase of one sponge invocation.

### cSHAKE

cSHAKE adds standardized customization.

It can incorporate:

- a function-name string;
- a customization string.

This is much stronger protocol engineering than informally writing:

```text
SHAKE(label || message)
```

without a formal encoding rule.

When its function-name and customization inputs are empty, cSHAKE is defined consistently with SHAKE behavior under SP 800-185.

### KMAC

KMAC is a keyed function built from cSHAKE-related encodings.

It supports:

- message authentication;
- pseudorandom-function use;
- variable output lengths;
- customization strings.

The key is not introduced by naive concatenation.

Its encoding and domain are defined by the standard.

This avoids the exact class of ad-hoc composition reasoning that motivated the length-extension article.

### TupleHash

Raw concatenation can be ambiguous:

```text
("ab", "c")
```

and:

```text
("a", "bc")
```

both become:

```text
abc
```

if field boundaries are discarded.

TupleHash defines encodings for tuples so that tuple structure is preserved.

It solves an application-level problem that a collision-resistant primitive alone cannot solve:

\[
\text{unambiguous structured hashing}.
\]

### ParallelHash

Traditional single-chain iterative hashes are sequential across one message.

ParallelHash defines a tree-like approach suitable for processing long inputs in parallel.

This illustrates the flexibility of the Keccak ecosystem:

```text
same underlying permutation family
different standardized outer constructions
different interfaces and goals
```

### Standards status as of September 2026

The current final SHA-3 standard remains:

**FIPS 202**, published in 2015.

NIST announced in March 2025 that it intends to update FIPS 202. The current FIPS 202 page still identifies the 2015 document as final and notes the planned update.

Likewise, **SP 800-185** remains the current final specification for cSHAKE, KMAC, TupleHash, and ParallelHash, while NIST has announced plans to revise it.

A planned update should not be described as though a new final revision has already replaced the current publications.

---

## Educational Implementation and Verification

The repository implementation:

[`code/sha3_educational.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha3_educational.py)

implements the complete educational path:

```text
bytes
  |
domain suffix + pad10*1
  |
absorb at rate
  |
Keccak-f[1600]
  |
squeeze
  |
SHA3 / SHAKE output
```

A correct implementation must get several details right simultaneously:

- 25 lanes;
- 64-bit arithmetic;
- little-endian lane serialization;
- 24 round constants;
- Theta;
- Rho;
- Pi;
- Chi;
- Iota;
- correct rate;
- correct suffix;
- repeated squeezing for long XOF output.

### Keccak-f[1600] constants

```python
MASK64 = (1 << 64) - 1

ROUND_CONSTANTS = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
]
```

The rotation table, indexed as `ROT[x][y]`, is:

```python
ROT = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
]
```

### Keccak permutation

```python
def rol64(x, n):
    if n == 0:
        return x & MASK64

    return (
        (x << n)
        | (x >> (64 - n))
    ) & MASK64


def keccak_f1600(state):
    A = list(state)

    for rc in ROUND_CONSTANTS:
        # Theta
        C = [
            A[x]
            ^ A[x + 5]
            ^ A[x + 10]
            ^ A[x + 15]
            ^ A[x + 20]
            for x in range(5)
        ]

        D = [
            C[(x - 1) % 5]
            ^ rol64(
                C[(x + 1) % 5],
                1,
            )
            for x in range(5)
        ]

        for y in range(5):
            for x in range(5):
                A[x + 5 * y] ^= D[x]

        # Rho + Pi
        B = [0] * 25

        for y in range(5):
            for x in range(5):
                B[
                    y
                    + 5 * (
                        (2 * x + 3 * y)
                        % 5
                    )
                ] = rol64(
                    A[x + 5 * y],
                    ROT[x][y],
                )

        # Chi
        for y in range(5):
            row = B[
                5 * y:
                5 * y + 5
            ]

            for x in range(5):
                A[x + 5 * y] = (
                    row[x]
                    ^ (
                        (~row[(x + 1) % 5])
                        & row[(x + 2) % 5]
                    )
                ) & MASK64

        # Iota
        A[0] ^= rc

    return A
```

This code deliberately uses a temporary `B` array for Rho/Pi and a copied row for Chi.

Those are correctness choices, not stylistic preferences.

### Generic byte-oriented sponge

```python
def sponge(
    message,
    rate_bytes,
    suffix,
    output_length,
):
    state = [0] * 25

    offset = 0

    # Absorb complete rate blocks.
    while (
        offset + rate_bytes
        <= len(message)
    ):
        block = message[
            offset:
            offset + rate_bytes
        ]

        for i in range(
            rate_bytes // 8
        ):
            state[i] ^= int.from_bytes(
                block[
                    8 * i:
                    8 * i + 8
                ],
                "little",
            )

        state = keccak_f1600(state)

        offset += rate_bytes

    # Final partial block + suffix + pad10*1.
    remainder = message[offset:]

    block = bytearray(rate_bytes)

    block[:len(remainder)] = remainder

    block[len(remainder)] ^= suffix
    block[-1] ^= 0x80

    for i in range(
        rate_bytes // 8
    ):
        state[i] ^= int.from_bytes(
            block[
                8 * i:
                8 * i + 8
            ],
            "little",
        )

    state = keccak_f1600(state)

    # Squeeze.
    output = bytearray()

    while len(output) < output_length:
        rate_output = b"".join(
            lane.to_bytes(
                8,
                "little",
            )
            for lane in state[
                :rate_bytes // 8
            ]
        )

        needed = (
            output_length
            - len(output)
        )

        output += rate_output[
            :min(
                needed,
                rate_bytes,
            )
        ]

        if len(output) < output_length:
            state = keccak_f1600(state)

    return bytes(output)
```

### SHA3-256 wrapper

For SHA3-256:

\[
r=1088
\]

bits:

\[
136
\]

bytes.

The suffix is:

```text
0x06
```

and output is:

\[
32
\]

bytes.

```python
def sha3_256_educational(message):
    return sponge(
        message=message,
        rate_bytes=136,
        suffix=0x06,
        output_length=32,
    )
```

### SHAKE256 wrapper

SHAKE256 uses the same 136-byte rate and 512-bit capacity, but a different domain suffix:

```text
0x1f
```

and caller-selected output length:

```python
def shake256_educational(
    message,
    output_length,
):
    return sponge(
        message=message,
        rate_bytes=136,
        suffix=0x1F,
        output_length=output_length,
    )
```

### Known-answer vector

For:

```text
abc
```

SHA3-256 must return:

```text
3a985da74fe225b2045c172d6bd390bd
855f086e3e9d525b46bfe24511431532
```

So:

```python
assert (
    sha3_256_educational(
        b"abc"
    ).hex()
    ==
    "3a985da74fe225b2045c172d6bd390bd"
    "855f086e3e9d525b46bfe24511431532"
)
```

### Boundary tests

The most useful test inputs include:

```python
messages = [
    b"",
    b"abc",
    b"A" * 135,
    b"A" * 136,
    b"A" * 137,
    b"A" * 1000,
]
```

For each:

```python
assert (
    sha3_256_educational(message)
    ==
    hashlib.sha3_256(
        message
    ).digest()
)
```

These specifically exercise the 136-byte rate boundary.

### Multi-block SHAKE output

A 200-byte SHAKE256 output is longer than one 136-byte rate block.

So it verifies that the implementation correctly performs:

```text
squeeze rate block
-> permute
-> squeeze again
```

rather than returning only the first state extraction.

```python
assert (
    shake256_educational(
        b"",
        200,
    )
    ==
    hashlib.shake_256(
        b""
    ).digest(200)
)
```

### What the original implementation mistakes teach

The earlier project notes identified several instructive mistakes:

- using a 512-bit rate for SHA3-256;
- converting the complete message through a big-endian integer;
- extracting ambiguous halves of a large squeezed integer;
- mixing SHA-256-style endianness into Keccak state serialization.

These errors are useful because each one demonstrates an important rule:

\[
\boxed{
\text{cryptographic parameters are part of the algorithm}
}
\]

An implementation that uses the wrong rate is not "a slightly different SHA3-256."

It is a different function.

Likewise, changing lane byte order or domain suffix changes interoperability completely.

---

## Engineering Lessons and Conclusion

The sponge model completes the structural comparison that began with SHA-256.

Merkle–Damgård gave us:

\[
\text{compression function}
\rightarrow
\text{chaining state}
\rightarrow
\text{final digest}.
\]

Keccak gives us:

\[
\text{fixed-width permutation}
\rightarrow
\text{absorb}
\rightarrow
\text{squeeze}.
\]

The central parameter split is:

\[
b=r+c.
\]

For Keccak-f[1600]:

\[
b=1600.
\]

The rate \(r\) controls how much data interacts with the state per permutation call.

The capacity \(c\) provides hidden internal state and underlies generic security bounds.

For SHA3-256:

\[
r=1088,
\qquad
c=512.
\]

Its digest size is:

\[
256
\]

bits, giving the expected ideal generic collision scale:

\[
2^{128}.
\]

The permutation itself is built from:

\[
\theta
\rightarrow
\rho
\rightarrow
\pi
\rightarrow
\chi
\rightarrow
\iota
\]

over 24 rounds.

Theta spreads column parity.

Rho rotates lane bits.

Pi relocates lanes.

Chi introduces nonlinearity.

Iota breaks symmetry.

The standardized function is not defined by the permutation alone.

It also depends on:

- rate,
- capacity,
- input encoding,
- domain suffix,
- padding,
- output length.

That is why:

\[
\operatorname{Keccak256}
\neq
\operatorname{SHA3\!-\!256}.
\]

It is also why SHAKE needs an explicit output length.

The previous article's length-extension attack gives us perhaps the clearest structural contrast.

SHA-256 publishes its complete chaining state.

SHA3-256 does not publish its full 1600-bit sponge state, and the hidden capacity prevents the same direct continuation interface from being reconstructed from the digest alone.

But the lesson remains the same:

\[
\boxed{
\text{do not turn structural observations into ad-hoc protocol designs}
}
\]

The absence of Merkle–Damgård length extension is not a reason to invent:

\[
\operatorname{SHA3\!-\!256}(K\|M)
\]

as a custom MAC.

The SHA-3 ecosystem already provides standardized constructions:

\[
\operatorname{KMAC},
\]

\[
\operatorname{cSHAKE},
\]

\[
\operatorname{TupleHash},
\]

\[
\operatorname{ParallelHash}.
\]

These functions exist precisely because keying, domain separation, structured hashing, and parallelism deserve explicit construction rules.

The educational implementation now gives us a verified executable model of:

- all 24 Keccak-f[1600] rounds;
- little-endian lanes;
- SHA3-256 absorption;
- SHAKE256 repeated squeezing;
- correct FIPS 202 domain suffixes;
- rate-boundary handling.

That completes the transition from the classical SHA-2 world to the permutation-based SHA-3 world.

The next article can move upward again from **hash construction** to **message authentication codes**: what a MAC security game is, why a hash digest is not a tag, how forgery probability is measured, and where HMAC, KMAC, and CMAC fit into the larger symmetric-authentication landscape.

Previous: [Length-Extension Attacks](/blog/length-extension-attacks/).

Next: [Message Authentication Codes](/blog/message-authentication-codes/).

---

## References

1. National Institute of Standards and Technology, **FIPS 202: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions**, August 2015.  
   https://doi.org/10.6028/NIST.FIPS.202

2. National Institute of Standards and Technology, **SP 800-185: SHA-3 Derived Functions: cSHAKE, KMAC, TupleHash and ParallelHash**, December 2016.  
   https://doi.org/10.6028/NIST.SP.800-185

3. G. Bertoni, J. Daemen, M. Peeters, and G. Van Assche, **The Keccak Reference**, Keccak Team.

4. G. Bertoni, J. Daemen, M. Peeters, and G. Van Assche, **Cryptographic Sponge Functions**, Keccak Team.

5. National Institute of Standards and Technology, **SHA-3 Project and Standardization Resources**.  
   https://csrc.nist.gov/projects/hash-functions/sha-3-project

6. Python Software Foundation, **`hashlib` — Secure hashes and message digests**.  
   https://docs.python.org/3/library/hashlib.html
