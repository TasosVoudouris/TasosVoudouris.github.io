---
title: "DES: From Feistel Structure to a Complete Implementation"
description: "A construction-oriented study of the Data Encryption Standard: Feistel structure, permutations, key scheduling, S-boxes, round mechanics, test vectors, implementation, and security analysis."
pubDate: "2025-04-12"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Cryptographic Engineering"
  - "Cryptanalysis"
tags:
  - "des"
  - "feistel"
  - "sbox"
  - "pbox"
  - "key-schedule"
  - "block-cipher"
  - "differential-cryptanalysis"
  - "linear-cryptanalysis"
difficulty: "Intermediate"
series: "Symmetric Cryptography"
seriesOrder: 2
sourcePath: "experiments/ready-material/des"
draft: false
---

## Table of Contents

- [DES at a glance](#des-at-a-glance)
- [The 64-bit key and the 56-bit effective key](#the-64-bit-key-and-the-56-bit-effective-key)
- [From SPNs to Feistel networks](#from-spns-to-feistel-networks)
- [The complete DES pipeline](#the-complete-des-pipeline)
- [Bit-level infrastructure](#bit-level-infrastructure)
- [Permutation boxes in DES](#permutation-boxes-in-des)
- [The DES key schedule](#the-des-key-schedule)
- [DES S-boxes](#des-s-boxes)
- [The DES round function](#the-des-round-function)
- [Why the Feistel network is invertible](#why-the-feistel-network-is-invertible)
- [One complete round by hand](#one-complete-round-by-hand)
- [A full 16-round trace](#a-full-16-round-trace)
- [A clean DES implementation from scratch](#a-clean-des-implementation-from-scratch)
- [Object-oriented wrapper](#object-oriented-wrapper)
- [Tests](#tests)
- [What was wrong in the earlier exploratory implementation](#what-was-wrong-in-the-earlier-exploratory-implementation)
- [Security analysis](#security-analysis)
- [DES, 3DES, and AES](#des-3des-and-aes)
- [Text encryption as an educational demo](#text-encryption-as-an-educational-demo)
- [What DES teaches us about cipher design](#what-des-teaches-us-about-cipher-design)
- [Conclusion](#conclusion)
- [References](#references)

---

## DES at a glance

DES is a symmetric block cipher with the following structural parameters:

| Property | DES value |
|---|---:|
| Block size | 64 bits |
| External key representation | 64 bits |
| Effective secret key bits | 56 bits |
| Parity bits | 8 bits |
| Number of Feistel rounds | 16 |
| Left/right half size | 32 bits |
| Round-key size | 48 bits |
| Round-function input | 32 bits |
| Expansion output | 48 bits |
| Number of S-boxes | 8 |
| S-box input | 6 bits |
| S-box output | 4 bits |

At a high level:

```text
64-bit plaintext
      |
      v
Initial Permutation (IP)
      |
      v
  L0 || R0
      |
      v
16 Feistel rounds
      |
      v
  R16 || L16
      |
      v
Final Permutation (IP^-1)
      |
      v
64-bit ciphertext
```

For round $i$,

$$
L_i = R_{i-1},
$$

and

$$
R_i = L_{i-1} \oplus F(R_{i-1}, K_i),
$$

where $K_i$ is the 48-bit round key and $F$ is the DES round function.

The important point is that the round function $F$ does **not** need to be invertible. The Feistel structure itself gives us invertibility.

---

## The 64-bit key and the 56-bit effective key

A common source of confusion is the statement that DES uses both a "64-bit key" and a "56-bit key".

Both statements refer to different layers of the same representation.

The DES key is supplied as 64 bits:

$$
K = k_1k_2\cdots k_{64}.
$$

However, eight positions are parity bits. In the traditional DES representation, every eighth bit is used for parity checking:

$$
8,\ 16,\ 24,\ 32,\ 40,\ 48,\ 56,\ 64.
$$

The **Permuted Choice 1** operation, usually written PC-1, discards these parity positions and permutes the remaining bits.

Therefore,

$$
64 \text{ supplied bits}
\longrightarrow
56 \text{ effective key bits}.
$$

The size of the actual key search space is therefore

$$
2^{56},
$$

not $2^{64}$.

The parity bits are not secret entropy.

This distinction matters later when we discuss brute-force resistance.

---

## From SPNs to Feistel networks

The previous article used an SPN. In an SPN, the whole internal state is repeatedly transformed by invertible layers such as:

$$
\text{AddRoundKey}
\rightarrow
\text{Substitution}
\rightarrow
\text{Permutation}.
$$

DES instead splits the state:

$$
X = L \parallel R.
$$

A Feistel step transforms the pair using

$$
(L,R)
\mapsto
(R,\ L \oplus F(R,K)).
$$

This looks asymmetric: $F$ is applied only to the right half.

After the transformation, the halves exchange roles. Therefore, over multiple rounds, both sides repeatedly enter the round function.

This construction has a major architectural advantage:

> $F$ may be nonlinear, lossy, and non-invertible, while the complete Feistel transformation remains invertible.

This is one of the deepest structural lessons in classical block-cipher design.

---

## The complete DES pipeline

A standards-faithful DES encryption can be described as follows.

Let

$$
P \in \{0,1\}^{64}
$$

be the plaintext block.

First apply the initial permutation:

$$
X_0 = IP(P).
$$

Split:

$$
X_0 = L_0 \parallel R_0,
$$

with

$$
L_0,R_0 \in \{0,1\}^{32}.
$$

For $i=1,\ldots,16$,

$$
L_i = R_{i-1},
$$

$$
R_i = L_{i-1} \oplus F(R_{i-1},K_i).
$$

After round 16, DES forms the **preoutput**

$$
R_{16}\parallel L_{16},
$$

and applies the inverse initial permutation:

$$
C = IP^{-1}(R_{16}\parallel L_{16}).
$$

The final swap is not an arbitrary implementation trick. It is part of the standard representation of the DES transformation.

---

## Bit-level infrastructure

The exploratory implementation used helper functions for binary conversion, circular shifts, character conversion, and modular arithmetic. Some of those helpers were useful while experimenting, but only a subset is part of the DES core.

For a clean DES implementation, we need four primitive operations:

1. fixed-width integer formatting,
2. table-driven bit permutation,
3. fixed-width rotation,
4. splitting/combining words.

A string-based helper remains useful for learning:

```python
def int_to_bin(number: int, block_size: int) -> str:
    if not 0 <= number < (1 << block_size):
        raise ValueError(f"value does not fit in {block_size} bits")
    return format(number, f"0{block_size}b")
```

A direct permutation on bit strings is even clearer:

```python
def permute_bits(bits: str, table: list[int]) -> str:
    return "".join(bits[i - 1] for i in table)
```

The convention is:

$$
\text{output}[j] = \text{input}[\text{table}[j]-1].
$$

This representation avoids an ambiguity that appeared in the original generic `PBox` class, where mappings were stored as input-to-output dictionaries.

For a cryptographic specification, the table itself should directly describe the output ordering.

### A generic P-box abstraction

If we still want the original object-oriented style, we can retain it in a safer form:

```python
class PBox:
    def __init__(self, table: list[int], input_size: int):
        self.table = tuple(table)
        self.input_size = input_size

        if any(i < 1 or i > input_size for i in self.table):
            raise ValueError("permutation table contains an invalid index")

    @property
    def output_size(self) -> int:
        return len(self.table)

    def apply(self, bits: str) -> str:
        if len(bits) != self.input_size:
            raise ValueError(
                f"expected {self.input_size} input bits, got {len(bits)}"
            )
        return "".join(bits[i - 1] for i in self.table)

    def is_bijection(self) -> bool:
        return (
            self.output_size == self.input_size
            and sorted(self.table) == list(range(1, self.input_size + 1))
        )

    def inverse(self) -> "PBox":
        if not self.is_bijection():
            raise ValueError("this P-box is not invertible")

        inverse_table = [0] * self.input_size
        for out_pos, in_pos in enumerate(self.table, start=1):
            inverse_table[in_pos - 1] = out_pos

        return PBox(inverse_table, self.input_size)
```

This distinguishes three different ideas:

- a true permutation,
- an expansion,
- a selection/compression.

Not every DES table is invertible.

That distinction is essential.

---

## Permutation boxes in DES

DES contains several fixed bit rearrangements. They do **not** introduce secrecy: the tables are public and deterministic.

Their role is structural.

The main tables are:

- initial permutation $IP$,
- final permutation $IP^{-1}$,
- expansion $E$,
- round permutation $P$,
- key permutation PC-1,
- key selection PC-2.

### Initial and final permutations

The initial permutation is:

```python
IP = [
    58, 50, 42, 34, 26, 18, 10,  2,
    60, 52, 44, 36, 28, 20, 12,  4,
    62, 54, 46, 38, 30, 22, 14,  6,
    64, 56, 48, 40, 32, 24, 16,  8,
    57, 49, 41, 33, 25, 17,  9,  1,
    59, 51, 43, 35, 27, 19, 11,  3,
    61, 53, 45, 37, 29, 21, 13,  5,
    63, 55, 47, 39, 31, 23, 15,  7,
]
```

The inverse permutation is:

```python
FP = [
    40,  8, 48, 16, 56, 24, 64, 32,
    39,  7, 47, 15, 55, 23, 63, 31,
    38,  6, 46, 14, 54, 22, 62, 30,
    37,  5, 45, 13, 53, 21, 61, 29,
    36,  4, 44, 12, 52, 20, 60, 28,
    35,  3, 43, 11, 51, 19, 59, 27,
    34,  2, 42, 10, 50, 18, 58, 26,
    33,  1, 41,  9, 49, 17, 57, 25,
]
```

They satisfy

$$
FP = IP^{-1}.
$$

These permutations are part of the standard, but they are not the source of DES's cryptographic strength.

If we define

$$
Y = IP(X),
$$

then

$$
FP(Y) = X.
$$

### Expansion permutation

The right half has 32 bits, but the round key has 48 bits.

DES therefore expands

$$
R \in \{0,1\}^{32}
$$

to

$$
E(R) \in \{0,1\}^{48}.
$$

The table is:

```python
E = [
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1,
]
```

Notice that some input positions are repeated.

Therefore $E$ is not a permutation in the strict bijective sense.

It is an **expansion mapping**.

Its purpose is not merely to "make the sizes match". The overlapping six-bit groups cause neighboring S-box inputs to share boundary bits, helping propagate local changes across adjacent nonlinear components over multiple rounds.

### The round permutation

After the eight S-boxes reduce 48 bits back to 32 bits, DES applies:

```python
P = [
    16,  7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26,  5, 18, 31, 10,
     2,  8, 24, 14, 32, 27,  3,  9,
    19, 13, 30,  6, 22, 11,  4, 25,
]
```

This is a true 32-bit permutation.

The S-boxes provide nonlinearity, while $P$ redistributes their outputs so that bits produced by one S-box influence different S-boxes in the next round.

The security effect comes from the **composition**:

$$
E
\rightarrow
\oplus K_i
\rightarrow
S_1,\ldots,S_8
\rightarrow
P
$$

repeated across many rounds.

### PC-1 and PC-2

The first key operation is PC-1:

```python
PC1 = [
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4,
]
```

It maps 64 bits to 56 bits and removes the parity positions.

The second operation, PC-2, selects 48 bits from the rotated 56-bit key state:

```python
PC2 = [
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]
```

It is important to state precisely what this means.

PC-2 does **not** combine multiple bits into one output position. It simply selects and reorders 48 of the 56 available positions.

So the operation is not an "overwriting compression" operation.

It is better viewed as a **selection permutation**:

$$
\{0,1\}^{56}
\longrightarrow
\{0,1\}^{48}.
$$

Because eight key-state bits are omitted for a particular round, PC-2 is not invertible.

---

## The DES key schedule

Let the 64-bit supplied key be $K$.

First,

$$
K^+ = PC1(K),
$$

where

$$
K^+ \in \{0,1\}^{56}.
$$

Then split:

$$
K^+ = C_0 \parallel D_0,
$$

with

$$
|C_0|=|D_0|=28.
$$

This point is critical: the halves are **28 bits**, not 32 bits.

For each round $i$, rotate both halves:

$$
C_i = \operatorname{ROL}_{28}(C_{i-1},s_i),
$$

$$
D_i = \operatorname{ROL}_{28}(D_{i-1},s_i).
$$

The DES rotation schedule is:

$$
(1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1).
$$

Equivalently, rounds

$$
1,\ 2,\ 9,\ 16
$$

rotate by one bit; all other rounds rotate by two.

Finally,

$$
K_i = PC2(C_i\parallel D_i),
$$

where

$$
K_i \in \{0,1\}^{48}.
$$

A compact implementation is:

```python
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

def rol28(x: int, shift: int) -> int:
    mask = (1 << 28) - 1
    return ((x << shift) & mask) | (x >> (28 - shift))

def generate_subkeys(key64: int) -> list[int]:
    key56 = permute_int(key64, PC1, 64)

    c = (key56 >> 28) & 0x0FFFFFFF
    d = key56 & 0x0FFFFFFF

    subkeys = []

    for shift in SHIFTS:
        c = rol28(c, shift)
        d = rol28(d, shift)

        cd = (c << 28) | d
        subkeys.append(permute_int(cd, PC2, 56))

    return subkeys
```

For the classic test key

$$
K=\texttt{0x133457799BBCDFF1},
$$

the first round key is

$$
K_1=\texttt{0x1B02EFFC7072}.
$$

The final round key is

$$
K_{16}=\texttt{0xCB3D8B0E17F5}.
$$

---

## DES S-boxes

The DES S-boxes are the nonlinear core of the round function.

Each S-box maps

$$
S_i:\{0,1\}^{6}\to\{0,1\}^{4}.
$$

There are eight different S-boxes:

$$
S_1,S_2,\ldots,S_8.
$$

A 48-bit word is divided into eight six-bit blocks:

$$
B_1\parallel B_2\parallel\cdots\parallel B_8.
$$

Then

$$
S(B_1,\ldots,B_8)
=
S_1(B_1)\parallel\cdots\parallel S_8(B_8),
$$

producing 32 bits.

### Row and column extraction

Let

$$
B=b_1b_2b_3b_4b_5b_6.
$$

The row uses the outer bits:

$$
r=(b_1b_6)_2.
$$

The column uses the middle four:

$$
c=(b_2b_3b_4b_5)_2.
$$

For example, take

```text
011000
```

Then

```text
row bits    = 00  -> 0
column bits = 1100 -> 12
```

If this block is entering $S_1$, we look at row 0, column 12.

Since

$$
S_1[0][12]=5,
$$

the four-bit output is

```text
0101
```

A safe implementation is:

```python
def sbox_lookup(box: list[list[int]], six_bits: int) -> int:
    if not 0 <= six_bits < 64:
        raise ValueError("S-box input must fit in 6 bits")

    row = ((six_bits & 0b100000) >> 4) | (six_bits & 0b000001)
    col = (six_bits >> 1) & 0b1111

    return box[row][col]
```

### All eight DES S-boxes

```python
SBOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]
```

The S-boxes are not interchangeable decorative tables. Their nonlinear behavior is central to DES's resistance against classical statistical attacks.

---

## The DES round function

The DES round function is

$$
F:\{0,1\}^{32}\times\{0,1\}^{48}\to\{0,1\}^{32}.
$$

It has four steps:

$$
F(R,K)
=
P\Big(
S\big(
E(R)\oplus K
\big)
\Big).
$$

Expanded:

1. **Expansion**
   $$
   R\in\{0,1\}^{32}
   \longrightarrow
   E(R)\in\{0,1\}^{48}
   $$

2. **Key mixing**
   $$
   X=E(R)\oplus K
   $$

3. **S-box substitution**
   $$
   X\in\{0,1\}^{48}
   \longrightarrow
   Y\in\{0,1\}^{32}
   $$

4. **P permutation**
   $$
   F(R,K)=P(Y)
   $$

A direct integer implementation is:

```python
def des_f(right32: int, round_key48: int) -> int:
    expanded = permute_int(right32, E, 32)
    mixed = expanded ^ round_key48

    substituted = 0

    for i in range(8):
        six = (mixed >> (42 - 6 * i)) & 0x3F
        value = sbox_lookup(SBOXES[i], six)
        substituted = (substituted << 4) | value

    return permute_int(substituted, P, 32)
```

Notice the operation used to combine the expanded right half with the round key:

$$
\boxed{\oplus}
$$

It is XOR.

It is **not** modular reduction.

That correction is essential because replacing XOR by `%` produces a reversible toy Feistel transformation, but it does not produce DES.

---

## Why the Feistel network is invertible

Consider one Feistel round:

$$
L' = R,
$$

$$
R' = L\oplus F(R,K).
$$

Suppose we know $L'$ and $R'$.

From the first equation,

$$
R=L'.
$$

Substitute into the second:

$$
R' = L\oplus F(L',K).
$$

Therefore,

$$
L=R'\oplus F(L',K).
$$

So the original pair is recovered as

$$
(L,R)
=
\big(
R'\oplus F(L',K),
L'
\big).
$$

No inverse of $F$ is needed.

This is why a Feistel construction can safely use S-box layers that map 6 bits to 4 bits and are therefore individually non-invertible.

### The mixer as an involution

The original notes separated a "Mixer" from a "Swapper".

Define only the mixer:

$$
M_K(L,R)
=
(L\oplus F(R,K),R).
$$

Applying it twice gives

$$
M_K(M_K(L,R))
=
((L\oplus F(R,K))\oplus F(R,K),R)
=
(L,R).
$$

Thus

$$
M_K^{-1}=M_K.
$$

The swap operation

$$
S(L,R)=(R,L)
$$

is also self-inverse.

A complete Feistel round can be viewed as a composition of these two simple transformations.

This is the rigorous explanation behind the original `Mixer` and `Swapper` abstractions.

---

## One complete round by hand

Use the standard test values:

$$
P=\texttt{0x0123456789ABCDEF},
$$

$$
K=\texttt{0x133457799BBCDFF1}.
$$

After the initial permutation:

$$
IP(P)=\texttt{0xCC00CCFFF0AAF0AA}.
$$

Therefore,

$$
L_0=\texttt{0xCC00CCFF},
$$

$$
R_0=\texttt{0xF0AAF0AA}.
$$

The first subkey is

$$
K_1=\texttt{0x1B02EFFC7072}.
$$

### Step 1: expand $R_0$

$$
E(R_0)
=
\texttt{0x7A15557A1555}.
$$

### Step 2: XOR with the subkey

$$
E(R_0)\oplus K_1
=
\texttt{0x6117BA866527}.
$$

Split this into eight six-bit words.

For the first block:

$$
B_1=\texttt{011000}.
$$

Its row is

$$
00_2=0,
$$

and its column is

$$
1100_2=12.
$$

So

$$
S_1(B_1)=S_1[0][12]=5.
$$

The eight S-box outputs concatenate to

$$
\texttt{0x5C82B597}.
$$

### Step 3: apply $P$

$$
P(\texttt{0x5C82B597})
=
\texttt{0x234AA9BB}.
$$

Thus

$$
F(R_0,K_1)
=
\texttt{0x234AA9BB}.
$$

### Step 4: construct the next state

$$
L_1=R_0
=
\texttt{0xF0AAF0AA}.
$$

And

$$
R_1
=
L_0\oplus F(R_0,K_1).
$$

Therefore,

$$
R_1
=
\texttt{0xCC00CCFF}
\oplus
\texttt{0x234AA9BB}
=
\texttt{0xEF4A6544}.
$$

So after round 1:

$$
(L_1,R_1)
=
(
\texttt{F0AAF0AA},
\texttt{EF4A6544}
).
$$

This is the exact point where the abstract Feistel equations become executable state transitions.

---

## A full 16-round trace

For the same test vector, the round keys and states are:

| Round | $K_i$ | $L_i$ | $R_i$ |
|---:|---|---|---|
| 1 | `1B02EFFC7072` | `F0AAF0AA` | `EF4A6544` |
| 2 | `79AED9DBC9E5` | `EF4A6544` | `CC017709` |
| 3 | `55FC8A42CF99` | `CC017709` | `A25C0BF4` |
| 4 | `72ADD6DB351D` | `A25C0BF4` | `77220045` |
| 5 | `7CEC07EB53A8` | `77220045` | `8A4FA637` |
| 6 | `63A53E507B2F` | `8A4FA637` | `E967CD69` |
| 7 | `EC84B7F618BC` | `E967CD69` | `064ABA10` |
| 8 | `F78A3AC13BFB` | `064ABA10` | `D5694B90` |
| 9 | `E0DBEBEDE781` | `D5694B90` | `247CC67A` |
| 10 | `B1F347BA464F` | `247CC67A` | `B7D5D7B2` |
| 11 | `215FD3DED386` | `B7D5D7B2` | `C5783C78` |
| 12 | `7571F59467E9` | `C5783C78` | `75BD1858` |
| 13 | `97C5D1FABA41` | `75BD1858` | `18C3155A` |
| 14 | `5F43B7F2E73A` | `18C3155A` | `C28C960D` |
| 15 | `BF918D3D3F0A` | `C28C960D` | `43423234` |
| 16 | `CB3D8B0E17F5` | `43423234` | `0A4CD995` |

The preoutput is

$$
R_{16}\parallel L_{16}
=
\texttt{0x0A4CD99543423234}.
$$

After the final permutation:

$$
\boxed{
C=\texttt{0x85E813540F0AB405}
}
$$

which matches the standard DES known-answer vector.

---

## A clean DES implementation from scratch

The following implementation uses integers internally. This avoids ambiguity in string slicing while keeping every operation close to the standard.

```python
IP = [
    58, 50, 42, 34, 26, 18, 10,  2,
    60, 52, 44, 36, 28, 20, 12,  4,
    62, 54, 46, 38, 30, 22, 14,  6,
    64, 56, 48, 40, 32, 24, 16,  8,
    57, 49, 41, 33, 25, 17,  9,  1,
    59, 51, 43, 35, 27, 19, 11,  3,
    61, 53, 45, 37, 29, 21, 13,  5,
    63, 55, 47, 39, 31, 23, 15,  7,
]

FP = [
    40,  8, 48, 16, 56, 24, 64, 32,
    39,  7, 47, 15, 55, 23, 63, 31,
    38,  6, 46, 14, 54, 22, 62, 30,
    37,  5, 45, 13, 53, 21, 61, 29,
    36,  4, 44, 12, 52, 20, 60, 28,
    35,  3, 43, 11, 51, 19, 59, 27,
    34,  2, 42, 10, 50, 18, 58, 26,
    33,  1, 41,  9, 49, 17, 57, 25,
]

E = [
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1,
]

P = [
    16,  7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26,  5, 18, 31, 10,
     2,  8, 24, 14, 32, 27,  3,  9,
    19, 13, 30,  6, 22, 11,  4, 25,
]

PC1 = [
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4,
]

PC2 = [
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]

SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

SBOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]


def permute_int(value: int, table: list[int], input_width: int) -> int:
    out = 0

    for position in table:
        bit = (value >> (input_width - position)) & 1
        out = (out << 1) | bit

    return out


def rol28(value: int, shift: int) -> int:
    mask = (1 << 28) - 1
    return ((value << shift) & mask) | (value >> (28 - shift))


def sbox_lookup(box: list[list[int]], six_bits: int) -> int:
    row = ((six_bits & 0x20) >> 4) | (six_bits & 0x01)
    col = (six_bits >> 1) & 0x0F
    return box[row][col]


def generate_subkeys(key64: int) -> list[int]:
    key56 = permute_int(key64, PC1, 64)

    c = (key56 >> 28) & 0x0FFFFFFF
    d = key56 & 0x0FFFFFFF

    subkeys = []

    for shift in SHIFTS:
        c = rol28(c, shift)
        d = rol28(d, shift)

        cd = (c << 28) | d
        subkeys.append(permute_int(cd, PC2, 56))

    return subkeys


def des_f(right32: int, round_key48: int) -> int:
    expanded = permute_int(right32, E, 32)
    mixed = expanded ^ round_key48

    substituted = 0

    for i in range(8):
        six = (mixed >> (42 - 6 * i)) & 0x3F
        value = sbox_lookup(SBOXES[i], six)
        substituted = (substituted << 4) | value

    return permute_int(substituted, P, 32)


def des_crypt_block(block64: int, subkeys: list[int]) -> int:
    state = permute_int(block64, IP, 64)

    left = (state >> 32) & 0xFFFFFFFF
    right = state & 0xFFFFFFFF

    for round_key in subkeys:
        left, right = right, left ^ des_f(right, round_key)

    preoutput = (right << 32) | left
    return permute_int(preoutput, FP, 64)


def des_encrypt_block(plaintext64: int, key64: int) -> int:
    return des_crypt_block(plaintext64, generate_subkeys(key64))


def des_decrypt_block(ciphertext64: int, key64: int) -> int:
    subkeys = generate_subkeys(key64)
    return des_crypt_block(ciphertext64, subkeys[::-1])
```

There are several reasons to prefer this version as the reference implementation.

First, it implements the actual DES operation:

$$
E(R)\oplus K_i.
$$

Second, it splits the 56-bit key state correctly into two 28-bit halves.

Third, it includes the initial and final permutations.

Fourth, encryption and decryption use the same block function with the subkey order reversed.

---

## Object-oriented wrapper

The original material used classes for `PBox`, `SBox`, `Mixer`, `Swapper`, `Round`, and `DES`.

That architecture is pedagogically useful because it makes the components visible as objects.

After validating the primitive functions, however, the top-level class can remain small:

```python
class DES:
    def __init__(self, key: int):
        if not 0 <= key < (1 << 64):
            raise ValueError("DES key must fit in 64 bits")

        self.key = key
        self.subkeys = generate_subkeys(key)

    def encrypt_block(self, plaintext: int) -> int:
        if not 0 <= plaintext < (1 << 64):
            raise ValueError("plaintext must fit in 64 bits")

        return des_crypt_block(plaintext, self.subkeys)

    def decrypt_block(self, ciphertext: int) -> int:
        if not 0 <= ciphertext < (1 << 64):
            raise ValueError("ciphertext must fit in 64 bits")

        return des_crypt_block(ciphertext, self.subkeys[::-1])
```

This gives us a clean boundary:

```python
des = DES(0x133457799BBCDFF1)

ciphertext = des.encrypt_block(0x0123456789ABCDEF)
plaintext = des.decrypt_block(ciphertext)
```

The lower-level functions still expose every internal transformation for experimentation.

---

## Tests

A cryptographic implementation should not be trusted merely because

```python
decrypt(encrypt(m)) == m
```

holds.

A symmetric bug can exist in encryption and decryption and still pass a round-trip test.

We therefore want several levels of validation.

### Known-answer test

The standard educational vector is:

```python
key = 0x133457799BBCDFF1
plaintext = 0x0123456789ABCDEF
expected = 0x85E813540F0AB405

ciphertext = des_encrypt_block(plaintext, key)

assert ciphertext == expected
assert des_decrypt_block(ciphertext, key) == plaintext
```

The expected ciphertext is:

```text
85E813540F0AB405
```

This test is far more informative than testing only internal reversibility.

### Round-trip tests

We can still add randomized round trips:

```python
import random

for _ in range(1000):
    key = random.getrandbits(64)
    plaintext = random.getrandbits(64)

    ciphertext = des_encrypt_block(plaintext, key)
    recovered = des_decrypt_block(ciphertext, key)

    assert recovered == plaintext
```

This checks the implementation over many state/key combinations.

It does not replace the known-answer test.

### Parity-bit invariance

Because PC-1 drops the eight parity positions, changing only those positions must leave the effective DES key unchanged.

We can test this property directly.

The low bit of each byte is a parity position in the conventional 64-bit representation. The mask

```python
0x0101010101010101
```

flips those eight bits.

```python
key1 = 0x133457799BBCDFF1
key2 = key1 ^ 0x0101010101010101

plaintext = 0x0123456789ABCDEF

assert generate_subkeys(key1) == generate_subkeys(key2)
assert des_encrypt_block(plaintext, key1) == des_encrypt_block(plaintext, key2)
```

This is a useful structural test because it verifies the role of PC-1 rather than just the final output.

---

## What was wrong in the earlier exploratory implementation

The earlier material contains many useful ideas and abstractions, so we keep its structure. But several points needed correction before the code could be described as DES.

### 1. The round function used modulo instead of XOR

The exploratory `Mixer.des_mixer()` used a function equivalent to

```python
lambda a, b: a % b
```

for the interaction between the expanded right half and the round key.

DES requires

```python
a ^ b
```

because the specification uses bitwise exclusive-or.

The `%` version can be studied as a toy Feistel network, but it is not DES.

### 2. PC-1 output was split incorrectly

PC-1 outputs 56 bits.

Those bits must be split into

$$
28+28.
$$

The original code split at bit 32:

```python
l, r = self.key[0:32], self.key[32:]
```

which gives $32+24$.

The correct split is:

```python
c, d = key56[:28], key56[28:]
```

or the equivalent integer representation.

### 3. The full cipher omitted IP and FP

The earlier `DES.encrypt()` iterated over rounds directly.

A standards-faithful DES implementation must apply:

$$
IP
$$

before the Feistel rounds and

$$
IP^{-1}
$$

after the final preoutput swap.

### 4. "Compression P-box" was modeled as overwriting

The original toy example allowed multiple input symbols to target the same output slot and described the result as compression.

That is not how PC-2 works.

PC-2 simply chooses 48 of 56 positions.

No XOR, merge, addition, or overwrite occurs.

### 5. P-box invertibility was tested only by length

A mapping is not invertible merely because input and output lengths match.

A true permutation must contain each input position exactly once.

The proper condition is bijectivity.

### 6. The S-box toy example had inconsistent output widths

The earlier custom S-box was instantiated with `block_size=2` while returning values such as 5, 6, 7, and 8.

Those values do not fit in two bits.

The pedagogical lesson is useful, but width validation should be explicit.

### 7. `SBox.__call__` silently returned the input on an invalid lookup

For cryptographic code, silent fallback is dangerous.

Invalid input should cause a clear exception.

### 8. The explanation of Feistel invertibility was too compressed

The swap operation alone does not explain why Feistel is invertible.

The exact equations do:

$$
L'=R,
\qquad
R'=L\oplus F(R,K).
$$

From these equations, the inverse follows algebraically.

### 9. The text-encryption helper encrypted characters independently

That is useful for demonstrating repeated block calls, but it is not a secure way to encrypt messages.

It behaves like an especially transparent form of independent-block encryption and leaks repeated values and structure.

We keep it only as an educational demonstration later.

---

## Security analysis

DES is historically important partly because it illustrates the difference between a cipher being structurally sophisticated and a cipher having enough security margin for modern computation.

### Exhaustive key search

The effective key space is

$$
2^{56}
=
72{,}057{,}594{,}037{,}927{,}936.
$$

The expected work to find a uniformly random key by exhaustive search is roughly half the key space:

$$
2^{55}
$$

trials on average.

That number was once large.

It is not large enough today.

In 1998, the Electronic Frontier Foundation's dedicated **Deep Crack** hardware recovered a DES challenge key in roughly 56 hours. In 1999, a combined distributed.net/EFF effort solved another DES challenge in about 22 hours.

These demonstrations made the key-length problem concrete: a well-designed internal round function does not compensate for insufficient key entropy.

### Differential cryptanalysis

Differential cryptanalysis studies how input differences propagate through a cipher.

If two inputs differ by

$$
\Delta X=X\oplus X',
$$

we examine the distribution of

$$
\Delta Y=F(X)\oplus F(X').
$$

For an S-box, one can build a **difference distribution table (DDT)**.

DES is especially important historically because its S-boxes were not arbitrary lookup tables. Their properties were chosen to resist statistical structure that would otherwise make differential attacks much stronger.

The public development of differential cryptanalysis by Biham and Shamir later provided a systematic framework for studying this behavior.

We will treat differential cryptanalysis in detail later in this series.

### Linear cryptanalysis

Linear cryptanalysis searches for approximate affine relationships between selected plaintext, ciphertext, and key bits.

An ideal nonlinear component should not admit strong linear approximations.

Matsui's work showed that DES could be attacked using carefully accumulated linear biases with large amounts of known plaintext.

Again, the important lesson is not that DES has "bad S-boxes". Quite the opposite: the DES S-boxes are an early and influential example of deliberate nonlinear design.

### Weak and semi-weak keys

DES has special keys for which the subkey schedule develops unusual symmetry.

For a **weak key**, all round keys are identical.

This implies the unusual property

$$
E_K(E_K(P))=P.
$$

There are four standard weak DES keys.

DES also has six pairs of **semi-weak keys**. For a semi-weak pair $K_1,K_2$,

$$
E_{K_1}(E_{K_2}(P))=P
$$

under the corresponding relationship between their round-key schedules.

There are also keys traditionally classified as possibly weak.

These sets occupy an extremely small fraction of the full key space, but they are mathematically interesting because they expose structure in the key schedule.

### The complementation property

DES has a useful algebraic property.

If

$$
E_K(P)=C,
$$

then

$$
E_{\overline K}(\overline P)
=
\overline C,
$$

where the bar denotes bitwise complement.

This is called the **DES complementation property**.

It follows from the way complementing both the data and the key interacts with expansion, XOR, the fixed S-box input pattern, and the Feistel structure.

The property does not make DES trivially insecure, but it creates symmetry in exhaustive-search analysis and is another example of structure that cryptanalysts study.

### The 64-bit block size

Even if DES had a much larger key, its 64-bit block size would still be small by modern standards.

A block cipher with $n$-bit blocks begins to experience substantial collision probability after on the order of

$$
2^{n/2}
$$

random blocks because of the birthday phenomenon.

For DES,

$$
2^{64/2}=2^{32}
$$

blocks.

The exact security consequence depends on the mode of operation and protocol, but the central lesson is general:

> block size and key size are independent security parameters.

A long key does not automatically repair a small block size.

---

## DES, 3DES, and AES

DES's 56-bit key eventually became too small, but replacing deployed infrastructure takes time.

A natural transitional idea was to apply the DES primitive multiple times.

The best-known construction is Triple DES / TDEA.

A common three-key form is:

$$
C
=
E_{K_3}
\big(
D_{K_2}
(
E_{K_1}(P)
)
\big).
$$

The middle decryption step is historical and supports compatibility conventions; the construction is usually called EDE.

TDEA extended the useful lifetime of DES-based systems, but it retained the 64-bit DES block size and became a legacy algorithm as well.

NIST withdrew SP 800-67 Rev. 2, the TDEA recommendation, on January 1, 2024, and TDEA is no longer approved by NIST for applying new cryptographic protection.

Modern systems should use contemporary authenticated-encryption constructions based on ciphers such as AES or ChaCha20, depending on the protocol and environment.

The architectural transition is useful to understand:

```text
DES
  |
  |  key length became insufficient
  v
TDEA / 3DES
  |
  |  legacy block size, performance, modern transition
  v
AES and modern AEAD designs
```

DES therefore sits at a crucial historical point between classical cipher engineering and modern symmetric cryptography.

---

## Text encryption as an educational demo

The original implementation included helpers that encrypted each character separately.

We can preserve that experiment while labeling it correctly.

```python
def encrypt_demo_text(text: str, des: DES) -> list[int]:
    return [des.encrypt_block(ord(ch)) for ch in text]


def decrypt_demo_text(blocks: list[int], des: DES) -> str:
    return "".join(chr(des.decrypt_block(block)) for block in blocks)
```

Example:

```python
des = DES(0x133457799BBCDFF1)

message = "We did it!"

ciphertext_blocks = encrypt_demo_text(message, des)
recovered = decrypt_demo_text(ciphertext_blocks, des)

assert recovered == message
```

This preserves uppercase letters and punctuation.

However, this is **not a secure message-encryption mode**.

If the same character appears twice, the same 64-bit input block is encrypted under the same key, producing the same output block.

This leaks equality patterns.

Real message encryption requires a properly specified mode or, preferably for modern applications, an authenticated-encryption scheme.

The correct lesson from this helper is therefore:

> a block cipher encrypts one fixed-size block; a complete message-encryption system needs additional construction.

That distinction will become important in the later article on modes of operation and AEAD.

---

## What DES teaches us about cipher design

DES is obsolete as a modern confidentiality primitive, but it remains exceptionally rich as a design case study.

Several lessons survive far beyond DES itself.

### 1. Structure matters

The Feistel construction shows that a cipher can remain invertible even when its internal round function is not.

That is an architectural result, not an implementation detail.

### 2. Nonlinearity and diffusion must cooperate

The S-boxes provide nonlinearity.

The expansion and P permutation distribute dependencies between neighboring S-boxes across rounds.

Neither idea should be evaluated in isolation.

### 3. Key schedules are part of the cipher

The key schedule determines how one master key becomes sixteen round keys.

Weak-key phenomena remind us that the schedule can introduce mathematical structure of its own.

### 4. Correct implementation is not the same as invertibility

A wrong Feistel network may still decrypt itself perfectly.

Therefore:

$$
\text{round-trip test}
\not\Rightarrow
\text{standards conformance}.
$$

Known-answer vectors are essential.

### 5. Key size is an independent security parameter

DES's internal design survived much longer intellectually than its 56-bit key size survived operationally.

A strong round function cannot rescue a brute-forceable key space.

### 6. Block size matters independently too

Even increasing the key size does not remove the birthday limitations associated with a 64-bit block.

### 7. Cryptanalysis informs design

Differential and linear cryptanalysis are not separate from cipher design.

They tell us what properties nonlinear layers, diffusion layers, and round counts need in order to create security margins.

This is why DES remains useful preparation for later study of AES, modern S-box design, differential trails, linear approximations, and authenticated encryption.

---

## Conclusion

In this article we reconstructed DES as an actual cryptographic system rather than as a collection of tables.

We began with the Feistel equations

$$
L_i=R_{i-1},
$$

$$
R_i=L_{i-1}\oplus F(R_{i-1},K_i),
$$

and then built the complete round function

$$
F(R,K)
=
P(S(E(R)\oplus K)).
$$

We examined:

- the difference between the 64-bit supplied key and the 56-bit effective key,
- parity-bit removal through PC-1,
- the 28-bit key-schedule halves,
- the DES rotation schedule,
- PC-2 selection,
- expansion from 32 to 48 bits,
- XOR key mixing,
- all eight 6-to-4-bit S-boxes,
- the P permutation,
- Feistel invertibility,
- the initial and final permutations,
- a full round worked by hand,
- a complete 16-round trace,
- a standards-faithful implementation,
- a class wrapper,
- known-answer and structural tests,
- and the main reasons DES is now obsolete.

The central standard vector

$$
\texttt{0x0123456789ABCDEF}
$$

under

$$
\texttt{0x133457799BBCDFF1}
$$

produces

$$
\boxed{\texttt{0x85E813540F0AB405}}.
$$

More importantly, we now understand **why**.

The next steps in the symmetric-cryptography series can build directly on this foundation: stronger analysis of S-boxes, differential and linear cryptanalysis, and eventually the transition from Feistel design to AES and modern authenticated encryption.

---

## References

1. National Institute of Standards and Technology, **FIPS PUB 46-3: Data Encryption Standard (DES)**, 1999. Withdrawn May 19, 2005.  
   <https://csrc.nist.gov/pubs/fips/46-3/final>

2. National Institute of Standards and Technology, **Withdrawal of FIPS 46-3, FIPS 74 and FIPS 81**, 2005.  
   <https://csrc.nist.gov/news/2005/withdrawal-of-fips-46-3-fips-74-and-fips-81>

3. National Institute of Standards and Technology, **SP 800-67 Rev. 2: Recommendation for the Triple Data Encryption Algorithm (TDEA) Block Cipher**, 2017. Withdrawn January 1, 2024.  
   <https://csrc.nist.gov/pubs/sp/800/67/r2/final>

4. E. Biham and A. Shamir, **Differential Cryptanalysis of the Data Encryption Standard**, Springer, 1993.

5. M. Matsui, **Linear Cryptanalysis Method for DES Cipher**, EUROCRYPT 1993.

6. D. Coppersmith, **The Data Encryption Standard (DES) and Its Strength Against Attacks**, IBM Journal of Research and Development, 38(3), 1994.

7. Electronic Frontier Foundation, **Cracking DES**, O'Reilly Media, 1998.

8. National Institute of Standards and Technology, **FIPS PUB 197: Advanced Encryption Standard (AES)**.
