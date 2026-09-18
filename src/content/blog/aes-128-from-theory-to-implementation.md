---
title: "AES-128: From Theory to Full Implementation"
description: "A construction-oriented deep dive into AES-128: state representation, GF(2^8), the algebraic S-box, ShiftRows, the MixColumns MDS layer, key expansion, encryption, decryption, round traces, testing, and implementation caveats."
pubDate: "2025-05-09"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Cryptographic Engineering"
  - "Mathematical Foundations"
tags:
  - "aes"
  - "rijndael"
  - "gf-2-8"
  - "sbox"
  - "subbytes"
  - "shiftrows"
  - "mixcolumns"
  - "mds"
  - "key-expansion"
difficulty: "Advanced"
series: "Symmetric Cryptography"
seriesOrder: 3
sourcePath: "experiments/ready-material/aes"
draft: false
---

## AES-128: From Theory to Full Implementation

The previous two parts of this series introduced the two structural ideas that dominate classical block-cipher design. We first built a small **Substitution-Permutation Network (SPN)** and then studied **DES** as the canonical historical Feistel cipher. AES now lets us return to the SPN paradigm at full scale.

The **Advanced Encryption Standard (AES)** is not merely "a cipher with an S-box." It is a carefully structured composition of four different kinds of operations:

1. **non-linear byte substitution** through `SubBytes`,
2. **byte transposition** through `ShiftRows`,
3. **linear diffusion over a finite field** through `MixColumns`,
4. **key injection** through `AddRoundKey`.

For AES-128 these operations are driven by eleven 128-bit round keys derived from one 128-bit master key.

This article keeps the original implementation-oriented spirit of the project, but tightens the mathematics and corrects several subtle points that are easy to get wrong in educational AES implementations: state orientation, the exact source of S-box non-linearity, finite-field multiplication, the distinction between AES and ECB, and the relationship between the key schedule and the round function.

> **Scope.** We implement the AES-128 **block primitive**. That means exactly one 128-bit block under one 128-bit key. A secure application still needs a mode or AEAD construction such as GCM. The code below is deliberately transparent and is **not** intended as a constant-time production implementation.

---

## 1. Standardization and Parameters

AES was standardized by NIST in **FIPS 197**. The standard specifies three parameterizations:

| Variant | Key length | Block length | $N_k$ | $N_b$ | Rounds $N_r$ |
|---|---:|---:|---:|---:|---:|
| AES-128 | 128 bits | 128 bits | 4 | 4 | 10 |
| AES-192 | 192 bits | 128 bits | 6 | 4 | 12 |
| AES-256 | 256 bits | 128 bits | 8 | 4 | 14 |

The block length is always **128 bits**. The variant name refers to the **key length**, not the block length.

This article focuses only on AES-128:

$$
E_K : \{0,1\}^{128} \to \{0,1\}^{128},
\qquad
K \in \{0,1\}^{128}.
$$

For every fixed key $K$, AES encryption is a permutation of the $2^{128}$ possible blocks.

### 1.1 Round structure

AES-128 uses:

- one initial `AddRoundKey`,
- nine full rounds,
- one final round without `MixColumns`.

Formally, if $X_0$ is the plaintext state and $K_0,\dots,K_{10}$ are the round keys,

$$
X_0' = X_0 \oplus K_0,
$$

and for $r=1,\dots,9$,

$$
X_r =
\operatorname{ARK}_{K_r}
\circ
\operatorname{MC}
\circ
\operatorname{SR}
\circ
\operatorname{SB}
(X_{r-1}).
$$

The final round is

$$
X_{10} =
\operatorname{ARK}_{K_{10}}
\circ
\operatorname{SR}
\circ
\operatorname{SB}
(X_9).
$$

There are therefore **10 rounds total**, not "9 rounds." The number 9 refers only to the number of *full* rounds that contain `MixColumns`.

![AES-128 structure](/images/ready/aes-128-from-theory-to-implementation/aes128.PNG)

![AES workflow](/images/ready/aes-128-from-theory-to-implementation/alltogetherAES.PNG)

---

## 2. The AES State: The First Place Implementations Go Wrong

A 128-bit block is sixteen bytes:

$$
(a_0,a_1,\dots,a_{15}).
$$

FIPS 197 loads these bytes into a $4\times4$ state in **column-major order**:

$$
s_{r,c} = a_{4c+r}.
$$

Thus

$$
\begin{bmatrix}
a_0 & a_4 & a_8 & a_{12}\\
a_1 & a_5 & a_9 & a_{13}\\
a_2 & a_6 & a_{10} & a_{14}\\
a_3 & a_7 & a_{11} & a_{15}
\end{bmatrix}.
$$

For the standard plaintext

```text
00112233445566778899aabbccddeeff
```

the mathematical AES state is

$$
\begin{bmatrix}
00 & 44 & 88 & cc\\
11 & 55 & 99 & dd\\
22 & 66 & aa & ee\\
33 & 77 & bb & ff
\end{bmatrix}.
$$

### 2.1 Our Python representation

The original code used:

```python
def bytes_to_matrix(text):
    return [list(text[i:i + 4]) for i in range(0, len(text), 4)]
```

This is valid, but there is an important naming subtlety: the four inner lists are most naturally interpreted as the **four AES columns**, not as the four printed matrix rows.

We therefore make the convention explicit:

```python
state[c][r] == s[r,c]
```

and use the clearer name `bytes_to_state()`.

```python
def bytes_to_state(block: bytes):
    if len(block) != 16:
        raise ValueError("AES operates on exactly 16-byte blocks")
    return [list(block[i:i + 4]) for i in range(0, 16, 4)]

def state_to_bytes(state):
    return bytes(sum(state, []))
```

For `b"Some 16byte text"` this representation becomes:

```text
[
    [83, 111, 109, 101],   # column 0: "Some"
    [32, 49, 54, 98],      # column 1: " 16b"
    [121, 116, 101, 32],   # column 2: "yte "
    [116, 101, 120, 116],  # column 3: "text"
]
```

Flattening these columns reproduces the original 16 bytes exactly.

This convention is the reason the original `ShiftRows` code indexed values such as `s[0][1], s[1][1], s[2][1], s[3][1]`: it was traversing a logical **row across four stored columns**.

---

## 3. AddRoundKey: Where the Secret Enters the State

`AddRoundKey` XORs the state with a 128-bit round key:

$$
s_{r,c} \leftarrow s_{r,c} \oplus k_{r,c}.
$$

XOR is its own inverse:

$$
(x\oplus k)\oplus k=x.
$$

Hence the same operation is used in encryption and decryption.

![AES AddRoundKey](/images/ready/aes-128-from-theory-to-implementation/AES-AddRoundKey.png)

```python
def add_round_key(state, round_key):
    for c in range(4):
        for r in range(4):
            state[c][r] ^= round_key[c][r]
```

A conceptual point matters here. `AddRoundKey` is the only AES state transformation that directly depends on secret key material. But **XOR itself is not the source of AES security**. Security comes from repeated composition of key addition with a non-linear substitution layer and a strong diffusion layer.

---

## 4. Arithmetic in $GF(2^8)$

AES treats bytes not merely as integers from 0 to 255, but as elements of the finite field

$$
GF(2^8)
\cong
GF(2)[x]/(m(x)),
$$

where

$$
m(x)=x^8+x^4+x^3+x+1.
$$

The binary representation of this polynomial is `0x11B`.

A byte

$$
b_7b_6\cdots b_1b_0
$$

represents the polynomial

$$
b_7x^7+b_6x^6+\cdots+b_1x+b_0.
$$

For example,

$$
\texttt{0xC2}=11000010_2
$$

represents

$$
x^7+x^6+x.
$$

### 4.1 Addition

Field addition is coefficient-wise addition modulo two, which is exactly XOR:

$$
a(x)+b(x) \longleftrightarrow a\oplus b.
$$

### 4.2 Multiplication

Multiplication is polynomial multiplication followed by reduction modulo $m(x)$.

The especially important operation is multiplication by $x$, or equivalently multiplication by `0x02`. AES implementations traditionally call this operation `xtime`.

If the high bit is zero, a left shift is sufficient. If the high bit is one, the shift creates an $x^8$ term, so reduction modulo $m(x)$ is required:

```python
def xtime(a):
    return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)
```

Why `0x1B` rather than `0x11B`? Because after the 8-bit left shift, the implicit $x^8$ coefficient is discarded; the lower eight coefficients of the modulus are

$$
x^4+x^3+x+1 = \texttt{0x1B}.
$$

### 4.3 A general field multiplication helper

For experiments, a general multiplier is useful:

```python
def gf_mul(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = xtime(a)
        b >>= 1
    return result
```

This makes the algebra underlying both the S-box and MixColumns explicit.

---

## 5. SubBytes and the AES S-box

`SubBytes` applies the same byte permutation

$$
S:GF(2^8)\to GF(2^8)
$$

independently to all sixteen state bytes.

![AES SubBytes](/images/ready/aes-128-from-theory-to-implementation/AESSubBytes.png)

The S-box is **not arbitrary**. It is constructed algebraically in two stages:

1. multiplicative inversion in $GF(2^8)$,
2. an affine transformation over $GF(2)$.

The inversion stage is responsible for the essential non-linearity.

### 5.1 Step 1: multiplicative inverse

For nonzero $a\in GF(2^8)$,

$$
b=a^{-1},
$$

with

$$
a\cdot b\equiv1\pmod{m(x)}.
$$

AES defines

$$
0^{-1}:=0
$$

for S-box construction.

Take the original example:

$$
a=\texttt{0xC2}.
$$

Its inverse is

$$
a^{-1}=\texttt{0x2F},
$$

and indeed

$$
\texttt{0xC2}\cdot\texttt{0x2F}=1
$$

inside the AES field.

### 5.2 Step 2: affine transformation

The inverse byte is then transformed by an affine map over $GF(2)$:

$$
S(a)=A\,a^{-1}\oplus c,
$$

where $A$ is a fixed invertible $8\times8$ binary matrix and

$$
c=\texttt{0x63}.
$$

Equivalently, with indices modulo eight,

$$
s_i =
b_i\oplus b_{i+4}\oplus b_{i+5}
\oplus b_{i+6}\oplus b_{i+7}\oplus c_i.
$$

For the example above,

$$
S(\texttt{C2})=\texttt{25}.
$$

### 5.3 An important correction: affine does not add non-linearity

An affine map is, by definition, linear plus a constant. Therefore the affine stage is **not itself nonlinear**. The multiplicative inverse supplies the non-linearity; the affine layer changes the representation and helps avoid undesirable simple algebraic structure such as fixed and opposite-fixed points.

This distinction matters because "non-linearity" has a precise meaning in cryptanalysis.

### 5.4 Useful S-box properties

The AES S-box is an invertible $8\times8$ S-box. Among its useful properties:

- it has no fixed points $S(x)=x$,
- it has no opposite fixed points $S(x)=x\oplus\texttt{FF}$,
- its maximum differential count is 4, giving maximum single-S-box differential probability

$$
\frac{4}{256}=2^{-6},
$$

- its Boolean component functions have nonlinearity 112,
- its maximum absolute Walsh coefficient is 32.

These local properties do not by themselves prove the security of AES. Their value appears when combined with the diffusion layer and many rounds.

**AES S-box**

|     | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x0 | 63 | 7C | 77 | 7B | F2 | 6B | 6F | C5 | 30 | 01 | 67 | 2B | FE | D7 | AB | 76 |
| 0x1 | CA | 82 | C9 | 7D | FA | 59 | 47 | F0 | AD | D4 | A2 | AF | 9C | A4 | 72 | C0 |
| 0x2 | B7 | FD | 93 | 26 | 36 | 3F | F7 | CC | 34 | A5 | E5 | F1 | 71 | D8 | 31 | 15 |
| 0x3 | 04 | C7 | 23 | C3 | 18 | 96 | 05 | 9A | 07 | 12 | 80 | E2 | EB | 27 | B2 | 75 |
| 0x4 | 09 | 83 | 2C | 1A | 1B | 6E | 5A | A0 | 52 | 3B | D6 | B3 | 29 | E3 | 2F | 84 |
| 0x5 | 53 | D1 | 00 | ED | 20 | FC | B1 | 5B | 6A | CB | BE | 39 | 4A | 4C | 58 | CF |
| 0x6 | D0 | EF | AA | FB | 43 | 4D | 33 | 85 | 45 | F9 | 02 | 7F | 50 | 3C | 9F | A8 |
| 0x7 | 51 | A3 | 40 | 8F | 92 | 9D | 38 | F5 | BC | B6 | DA | 21 | 10 | FF | F3 | D2 |
| 0x8 | CD | 0C | 13 | EC | 5F | 97 | 44 | 17 | C4 | A7 | 7E | 3D | 64 | 5D | 19 | 73 |
| 0x9 | 60 | 81 | 4F | DC | 22 | 2A | 90 | 88 | 46 | EE | B8 | 14 | DE | 5E | 0B | DB |
| 0xA | E0 | 32 | 3A | 0A | 49 | 06 | 24 | 5C | C2 | D3 | AC | 62 | 91 | 95 | E4 | 79 |
| 0xB | E7 | C8 | 37 | 6D | 8D | D5 | 4E | A9 | 6C | 56 | F4 | EA | 65 | 7A | AE | 08 |
| 0xC | BA | 78 | 25 | 2E | 1C | A6 | B4 | C6 | E8 | DD | 74 | 1F | 4B | BD | 8B | 8A |
| 0xD | 70 | 3E | B5 | 66 | 48 | 03 | F6 | 0E | 61 | 35 | 57 | B9 | 86 | C1 | 1D | 9E |
| 0xE | E1 | F8 | 98 | 11 | 69 | D9 | 8E | 94 | 9B | 1E | 87 | E9 | CE | 55 | 28 | DF |
| 0xF | 8C | A1 | 89 | 0D | BF | E6 | 42 | 68 | 41 | 99 | 2D | 0F | B0 | 54 | BB | 16 |

**AES inverse S-box**

|     | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x0 | 52 | 09 | 6A | D5 | 30 | 36 | A5 | 38 | BF | 40 | A3 | 9E | 81 | F3 | D7 | FB |
| 0x1 | 7C | E3 | 39 | 82 | 9B | 2F | FF | 87 | 34 | 8E | 43 | 44 | C4 | DE | E9 | CB |
| 0x2 | 54 | 7B | 94 | 32 | A6 | C2 | 23 | 3D | EE | 4C | 95 | 0B | 42 | FA | C3 | 4E |
| 0x3 | 08 | 2E | A1 | 66 | 28 | D9 | 24 | B2 | 76 | 5B | A2 | 49 | 6D | 8B | D1 | 25 |
| 0x4 | 72 | F8 | F6 | 64 | 86 | 68 | 98 | 16 | D4 | A4 | 5C | CC | 5D | 65 | B6 | 92 |
| 0x5 | 6C | 70 | 48 | 50 | FD | ED | B9 | DA | 5E | 15 | 46 | 57 | A7 | 8D | 9D | 84 |
| 0x6 | 90 | D8 | AB | 00 | 8C | BC | D3 | 0A | F7 | E4 | 58 | 05 | B8 | B3 | 45 | 06 |
| 0x7 | D0 | 2C | 1E | 8F | CA | 3F | 0F | 02 | C1 | AF | BD | 03 | 01 | 13 | 8A | 6B |
| 0x8 | 3A | 91 | 11 | 41 | 4F | 67 | DC | EA | 97 | F2 | CF | CE | F0 | B4 | E6 | 73 |
| 0x9 | 96 | AC | 74 | 22 | E7 | AD | 35 | 85 | E2 | F9 | 37 | E8 | 1C | 75 | DF | 6E |
| 0xA | 47 | F1 | 1A | 71 | 1D | 29 | C5 | 89 | 6F | B7 | 62 | 0E | AA | 18 | BE | 1B |
| 0xB | FC | 56 | 3E | 4B | C6 | D2 | 79 | 20 | 9A | DB | C0 | FE | 78 | CD | 5A | F4 |
| 0xC | 1F | DD | A8 | 33 | 88 | 07 | C7 | 31 | B1 | 12 | 10 | 59 | 27 | 80 | EC | 5F |
| 0xD | 60 | 51 | 7F | A9 | 19 | B5 | 4A | 0D | 2D | E5 | 7A | 9F | 93 | C9 | 9C | EF |
| 0xE | A0 | E0 | 3B | 4D | AE | 2A | F5 | B0 | C8 | EB | BB | 3C | 83 | 53 | 99 | 61 |
| 0xF | 17 | 2B | 04 | 7E | BA | 77 | D6 | 26 | E1 | 69 | 14 | 63 | 55 | 21 | 0C | 7D |

The implementation is simply:

```python
def sub_bytes(state, box=S_BOX):
    for c in range(4):
        for r in range(4):
            state[c][r] = box[state[c][r]]
```

Decryption uses the inverse lookup table.

---

## 6. ShiftRows: Moving Bytes Between Columns

`SubBytes` is byte-local. If every byte stayed in the same column forever, the four columns would remain much more separable than we want.

`ShiftRows` moves bytes across columns.

![AES ShiftRows](/images/ready/aes-128-from-theory-to-implementation/AESShiftRows.png)

For logical row $r$:

- row 0 is unchanged,
- row 1 is rotated left by one byte,
- row 2 by two bytes,
- row 3 by three bytes.

If the state is written in the conventional row-by-column matrix,

$$
\begin{bmatrix}
a_0&a_4&a_8&a_{12}\\
a_1&a_5&a_9&a_{13}\\
a_2&a_6&a_{10}&a_{14}\\
a_3&a_7&a_{11}&a_{15}
\end{bmatrix},
$$

then after `ShiftRows`,

$$
\begin{bmatrix}
a_0&a_4&a_8&a_{12}\\
a_5&a_9&a_{13}&a_1\\
a_{10}&a_{14}&a_2&a_6\\
a_{15}&a_3&a_7&a_{11}
\end{bmatrix}.
$$

With our `state[column][row]` representation:

```python
def shift_rows(state):
    for r in range(1, 4):
        row = [state[c][r] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            state[c][r] = row[c]
```

The inverse rotates each row to the right by the same offset.

`ShiftRows` is a permutation only. It creates no non-linearity and does not change byte values. Its purpose is to route bytes into different columns so that subsequent `MixColumns` operations spread dependencies across the full state.

---

## 7. MixColumns: Linear Diffusion over $GF(2^8)$

`MixColumns` applies the same linear transformation to each 4-byte column.

![AES MixColumns](/images/ready/aes-128-from-theory-to-implementation/AESMixColumns.png)

For one column

$$
\begin{bmatrix}
a_0\\a_1\\a_2\\a_3
\end{bmatrix},
$$

AES computes

$$
\begin{bmatrix}
b_0\\b_1\\b_2\\b_3
\end{bmatrix}
=
\begin{bmatrix}
02&03&01&01\\
01&02&03&01\\
01&01&02&03\\
03&01&01&02
\end{bmatrix}
\begin{bmatrix}
a_0\\a_1\\a_2\\a_3
\end{bmatrix},
$$

where every multiplication and addition is in $GF(2^8)$.

Hence

$$
b_0=(02\cdot a_0)\oplus(03\cdot a_1)\oplus a_2\oplus a_3.
$$

Because

$$
03\cdot a=(02\cdot a)\oplus a,
$$

`xtime()` is enough to implement the entire forward matrix efficiently.

### 7.1 Worked FIPS-style example

For

```text
db 13 53 45
```

the output is

```text
8e 4d a1 bc
```

For the first byte:

$$
\begin{aligned}
b_0
&=(02\cdot db)\oplus(03\cdot13)\oplus53\oplus45\\
&=ad\oplus35\oplus53\oplus45\\
&=8e.
\end{aligned}
$$

### 7.2 Why this matrix is important

The MixColumns matrix is an **MDS** diffusion matrix. Its branch number is 5. Informally, for every nonzero input difference to one column,

$$
\operatorname{wt}(\Delta x)
+
\operatorname{wt}(M\Delta x)
\ge5,
$$

where the weight counts active bytes.

This gives a precise way to reason about how many S-boxes must become active across consecutive rounds. `ShiftRows` distributes bytes among columns, and `MixColumns` forces strong intra-column diffusion. Their composition is central to the Rijndael **wide-trail strategy**.

A more precise statement than "one input bit immediately affects all ciphertext bits" is therefore:

> MixColumns spreads changes among bytes of one column; ShiftRows moves these bytes into different columns; repeated rounds cause this influence to propagate across the full state.

The avalanche behavior is an emergent multi-round property, not a guarantee of a single `MixColumns` call.

### 7.3 Inverse MixColumns

Decryption uses

$$
M^{-1}=
\begin{bmatrix}
0e&0b&0d&09\\
09&0e&0b&0d\\
0d&09&0e&0b\\
0b&0d&09&0e
\end{bmatrix}.
$$

Our implementation uses a standard algebraic optimization that pre-processes each column and then reuses the forward `mix_columns()` routine.

---

## 8. Putting the Round Layers Together

A full AES-128 middle round is:

```text
state
  |
SubBytes
  |
ShiftRows
  |
MixColumns
  |
AddRoundKey(K_r)
  |
next state
```

The final round omits `MixColumns`:

```text
SubBytes
  |
ShiftRows
  |
AddRoundKey(K_10)
```

The omission is part of the AES specification. It does **not** mean the last round is "incomplete"; security analysis treats the cipher exactly as specified.

---

## 9. AES-128 Key Expansion

AES-128 starts with four 32-bit key words:

$$
w_0,w_1,w_2,w_3.
$$

It expands them into 44 words:

$$
w_0,w_1,\dots,w_{43}.
$$

Every four consecutive words form one 128-bit round key:

$$
K_r=(w_{4r},w_{4r+1},w_{4r+2},w_{4r+3}),
\qquad
0\le r\le10.
$$

### 9.1 The recurrence

For $i\ge4$,

$$
w_i=
\begin{cases}
w_{i-4}\oplus
\operatorname{SubWord}(
\operatorname{RotWord}(w_{i-1})
)
\oplus
\operatorname{Rcon}_{i/4},
& i\equiv0\pmod4,\\[1ex]
w_{i-4}\oplus w_{i-1},
& \text{otherwise}.
\end{cases}
$$

The three special operations are:

**RotWord**

$$
[a_0,a_1,a_2,a_3]
\mapsto
[a_1,a_2,a_3,a_0].
$$

**SubWord**

Apply the AES S-box independently to each of the four bytes.

**Rcon**

$$
\operatorname{Rcon}_i=
[x^{i-1},00,00,00]
$$

in $GF(2^8)$.

For AES-128 the required constants are:

```text
01 02 04 08 10 20 40 80 1b 36
```

### 9.2 Standard example

For the master key

```text
000102030405060708090a0b0c0d0e0f
```

the first three round keys are

```text
K0 = 000102030405060708090a0b0c0d0e0f
K1 = d6aa74fdd2af72fadaa678f1d6ab76fe
K2 = b692cf0b643dbdf1be9bc5006830b3fe
```

and the final round key is

```text
K10 = 13111d7fe3944a17f307a78b4d2b30c5
```

### 9.3 Is the key schedule invertible?

For AES-128, yes: the word recurrence can be run backward, so a complete round key determines the master key.

This should **not** be interpreted as eleven independent 128-bit secrets. The eleven round keys together contain no more independent secret entropy than the original 128-bit master key. They are deterministically related.

The original draft described invertibility as though its purpose were to make every round key carry independent entropy. That is too strong. It is better to treat invertibility as a structural property of the AES-128 recurrence.

---

## 10. A Complete Standard Encryption Trace

Use the well-known AES-128 test vector:

```text
Key       = 000102030405060708090a0b0c0d0e0f
Plaintext = 00112233445566778899aabbccddeeff
```

After the initial `AddRoundKey`:

```text
00102030405060708090a0b0c0d0e0f0
```

### Round 1

After `SubBytes`:

```text
63cab7040953d051cd60e0e7ba70e18c
```

After `ShiftRows`:

```text
6353e08c0960e104cd70b751bacad0e7
```

After `MixColumns`:

```text
5f72641557f5bc92f7be3b291db9f91a
```

After `AddRoundKey(K1)`:

```text
89d810e8855ace682d1843d8cb128fe4
```

The same process continues through round 9.

### Final round

Immediately before the last key addition:

```text
SubBytes  = 7a9f102789d5f50b2beffd9f3dca4ea7
ShiftRows = 7ad5fda789ef4e272bca100b3d9ff59f
```

After `AddRoundKey(K10)`:

```text
69c4e0d86a7b0430d8cdb78070b4c55a
```

Therefore

$$
\boxed{
\texttt{00112233445566778899aabbccddeeff}
\xrightarrow[K]{\mathrm{AES\text{-}128}}
\texttt{69c4e0d86a7b0430d8cdb78070b4c55a}
}
$$

This is a far stronger validation target than merely checking that our own decryption reverses our own encryption: a matched standardized known-answer vector detects errors that symmetric bugs could otherwise hide.

---

## 11. Complete Educational AES-128 Implementation

The following implementation preserves the structure of the original project while removing ambiguity and global-variable dependencies.

```python
S_BOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
)

INV_S_BOX = [0] * 256
for x, y in enumerate(S_BOX):
    INV_S_BOX[y] = x
INV_S_BOX = tuple(INV_S_BOX)

RCON = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10,
        0x20, 0x40, 0x80, 0x1B, 0x36)


def bytes_to_state(block: bytes) -> list[list[int]]:
    """
    AES state represented as four columns.

    state[c][r] corresponds to the AES specification byte s[r,c].
    """
    if len(block) != 16:
        raise ValueError("AES operates on exactly 16-byte blocks")
    return [list(block[i:i + 4]) for i in range(0, 16, 4)]


def state_to_bytes(state: list[list[int]]) -> bytes:
    return bytes(sum(state, []))


def add_round_key(state, round_key):
    for c in range(4):
        for r in range(4):
            state[c][r] ^= round_key[c][r]


def sub_bytes(state, box=S_BOX):
    for c in range(4):
        for r in range(4):
            state[c][r] = box[state[c][r]]


def shift_rows(state):
    # state is stored as columns, so a logical row is state[c][r]
    # while c varies from 0 to 3.
    for r in range(1, 4):
        row = [state[c][r] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            state[c][r] = row[c]


def inv_shift_rows(state):
    for r in range(1, 4):
        row = [state[c][r] for c in range(4)]
        row = row[-r:] + row[:-r]
        for c in range(4):
            state[c][r] = row[c]


def xtime(a: int) -> int:
    """
    Multiply a field element by x (equivalently 0x02) in
    GF(2^8) modulo x^8 + x^4 + x^3 + x + 1.
    """
    return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
    # Algebraically equivalent to multiplication by the AES MDS matrix.
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)


def mix_columns(state):
    for c in range(4):
        mix_single_column(state[c])


def inv_mix_columns(state):
    # Standard optimization: pre-transform each column and reuse MixColumns.
    for c in range(4):
        u = xtime(xtime(state[c][0] ^ state[c][2]))
        v = xtime(xtime(state[c][1] ^ state[c][3]))
        state[c][0] ^= u
        state[c][1] ^= v
        state[c][2] ^= u
        state[c][3] ^= v
    mix_columns(state)


def expand_key_128(master_key: bytes) -> list[list[list[int]]]:
    """
    Expand one 128-bit AES key into 11 128-bit round keys.
    Each 4-byte list is one 32-bit word / state column.
    """
    if len(master_key) != 16:
        raise ValueError("AES-128 requires a 16-byte key")

    words = [list(master_key[i:i + 4]) for i in range(0, 16, 4)]
    rcon_index = 1

    while len(words) < 44:
        temp = words[-1].copy()

        if len(words) % 4 == 0:
            # RotWord
            temp = temp[1:] + temp[:1]

            # SubWord
            temp = [S_BOX[b] for b in temp]

            # Rcon
            temp[0] ^= RCON[rcon_index]
            rcon_index += 1

        # w_i = w_(i-4) XOR temp
        temp = [a ^ b for a, b in zip(temp, words[-4])]
        words.append(temp)

    return [words[4*i:4*(i + 1)] for i in range(11)]


class AES128:
    """
    Educational AES-128 block primitive.

    This class implements only one-block AES encryption/decryption.
    It does not provide a mode of operation, padding, authentication,
    nonce handling, or side-channel resistance.
    """

    def __init__(self, key: bytes):
        self.round_keys = expand_key_128(key)

    def encrypt_block(self, plaintext: bytes) -> bytes:
        state = bytes_to_state(plaintext)

        # Initial key addition.
        add_round_key(state, self.round_keys[0])

        # Rounds 1..9.
        for rnd in range(1, 10):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self.round_keys[rnd])

        # Round 10: no MixColumns.
        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self.round_keys[10])

        return state_to_bytes(state)

    def decrypt_block(self, ciphertext: bytes) -> bytes:
        state = bytes_to_state(ciphertext)

        add_round_key(state, self.round_keys[10])

        for rnd in range(9, 0, -1):
            inv_shift_rows(state)
            sub_bytes(state, INV_S_BOX)
            add_round_key(state, self.round_keys[rnd])
            inv_mix_columns(state)

        inv_shift_rows(state)
        sub_bytes(state, INV_S_BOX)
        add_round_key(state, self.round_keys[0])

        return state_to_bytes(state)

```

---

## 12. Validation

### 12.1 NIST/FIPS known-answer vector

```python
key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
expected = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")

aes = AES128(key)

ciphertext = aes.encrypt_block(plaintext)

assert ciphertext == expected
assert aes.decrypt_block(ciphertext) == plaintext

print(ciphertext.hex())
```

Expected output:

```text
69c4e0d86a7b0430d8cdb78070b4c55a
```

### 12.2 Preserve the original project test

The original article used:

```python
key = b"some 16 byte key"
plaintext = b"some 16 byte msg"
```

Our corrected implementation retains the same result:

```text
ce4236c54ac0be177704de7a7197b5ca
```

and decryption returns

```text
b"some 16 byte msg"
```

### 12.3 Optional comparison with PyCryptodome

A library comparison remains useful as an independent implementation check:

```python
from Crypto.Cipher import AES as PyCryptoAES

key = b"some 16 byte key"
plaintext = b"some 16 byte msg"

ours = AES128(key).encrypt_block(plaintext)

reference = PyCryptoAES.new(
    key,
    PyCryptoAES.MODE_ECB,
).encrypt(plaintext)

assert ours == reference
```

There is an important terminology correction here:

> `AES128.encrypt_block()` is the raw AES block primitive. It is not itself "ECB mode." If we apply that primitive independently to every block of a multi-block message, **that composition is ECB**.

This distinction matters because ECB is a mode of operation, whereas AES is the block cipher.

---

## 13. Inverse Cipher

Each AES transformation used in encryption is invertible:

| Encryption | Inverse |
|---|---|
| `SubBytes` | `InvSubBytes` |
| `ShiftRows` | `InvShiftRows` |
| `MixColumns` | `InvMixColumns` |
| `AddRoundKey` | `AddRoundKey` |

The encryption round is

$$
K_r\oplus
M(SR(SB(X))).
$$

To undo a transformation composition, reverse the order:

$$
SB^{-1}
\circ
SR^{-1}
\circ
ARK_{K_r}
\circ
MC^{-1}
$$

with the exact ordering determined by where we are in the decryption schedule.

In code, after the initial addition of $K_{10}$, each middle inverse round executes:

```text
InvShiftRows
InvSubBytes
AddRoundKey
InvMixColumns
```

and the final inverse round omits `InvMixColumns`.

---

## 14. What Was Corrected from the Original Draft

The original material already contained nearly all of the right conceptual pieces: state conversion, the forward and inverse S-boxes, `ShiftRows`, `MixColumns`, key expansion, a full encryption/decryption class, and a PyCryptodome comparison. The following changes tighten correctness without discarding that material.

### 14.1 State orientation is now explicit

The original `bytes_to_matrix()` returned four consecutive 4-byte lists and called the result a matrix. That representation is perfectly workable, but those inner lists are **columns** under the AES standard mapping.

We now state the convention explicitly:

```text
state[c][r] = s[r,c]
```

This removes one of the most common AES implementation confusions.

### 14.2 "9, 11, or 13 rounds" is clarified

AES-128/192/256 have **10/12/14 total rounds**. The numbers 9/11/13 count only the full middle rounds between the initial key addition and the final round.

### 14.3 The affine S-box step is not nonlinear

The original text attributed additional non-linearity to the affine transformation. An affine map is not nonlinear. The field inversion supplies the non-linearity; the affine stage reshapes it and removes undesirable simple structure.

### 14.4 MixColumns does not instantly diffuse one bit across the entire state

One `MixColumns` application affects one four-byte column. Global diffusion arises through repeated interaction with `ShiftRows`.

### 14.5 The key schedule is scoped specifically to AES-128

The old `expand_key()` mixed generic 128/192/256 handling with an AES-128 class and relied in places on external globals such as `N_ROUNDS` or `n_rounds`. The revised `expand_key_128()` is deliberately narrower and self-contained.

### 14.6 Unused integer polynomial-looking code was removed from the cipher path

The original full listing contained a `lookup_function()` using ordinary Python integer multiplication and exponentiation. Those operations are **not automatically arithmetic in $GF(2^8)$**, so such an expression must not be presented as a direct AES S-box implementation without an explicit field representation. The lookup table or a correct finite-field construction should be used instead.

### 14.7 ECB terminology is separated from AES

A one-block implementation behaves like the block transform used inside ECB, but the primitive itself is not "ECB." ECB exists only when blocks of a longer message are independently encrypted under the same key.

### 14.8 Round-trip testing is not enough

The property

```python
decrypt(encrypt(m)) == m
```

is necessary but not sufficient. Two mutually compatible bugs can still satisfy it. We therefore keep the round-trip test **and** add the standardized known-answer vector.

---

## 15. Cryptanalytic Structure

Understanding the construction means understanding what an analyst sees.

### 15.1 Differential behavior

For an S-box difference $\Delta x$, define the distribution

$$
D_{\Delta x,\Delta y}
=
\#\{x:
S(x)\oplus S(x\oplus\Delta x)=\Delta y
\}.
$$

For the AES S-box, every nonzero input difference has entries bounded by 4. Thus no single differential transition through one AES S-box has probability greater than

$$
2^{-6}.
$$

The wide-trail strategy then uses the diffusion layer to force many active S-boxes across multiple rounds.

### 15.2 Linear behavior

For masks $a,b\in GF(2)^8$, linear analysis studies

$$
a\cdot x
=
b\cdot S(x)
$$

and asks how far the probability deviates from $1/2$.

The AES S-box has maximum absolute Walsh magnitude 32, corresponding to strong resistance at the individual S-box level.

Again, the point is not that an S-box alone "makes AES secure." The security argument depends on how many S-boxes a trail must activate and how local biases or differential probabilities multiply across the trail.

### 15.3 Algebraic structure

The AES S-box has a compact algebraic description because it is derived from inversion in a finite field. That makes AES unusually elegant mathematically, but it also means that algebraic structure is visible to an analyst.

The design does not attempt to hide that structure. Instead, the cipher combines non-linearity, an MDS diffusion layer, key injection, and enough rounds to build a security margin against known forms of cryptanalysis.

---

## 16. Avalanche as an Experiment

Rather than asserting "AES has avalanche," we can measure how the block difference develops.

```python
def hamming_distance(a: bytes, b: bytes) -> int:
    return sum((x ^ y).bit_count() for x, y in zip(a, b))

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
p1 = bytes.fromhex("00112233445566778899aabbccddeeff")

p2 = bytearray(p1)
p2[0] ^= 0x01
p2 = bytes(p2)

aes = AES128(key)

c1 = aes.encrypt_block(p1)
c2 = aes.encrypt_block(p2)

print("Input difference :", hamming_distance(p1, p2))
print("Output difference:", hamming_distance(c1, c2))
```

One input bit has been changed. For a secure 128-bit permutation family, we expect the final output differences, over many trials, to behave roughly like differences between unrelated 128-bit strings: around half of the bits changed on average.

That observation is statistical. A single sample is not a proof of security.

---

## 17. Why the Final Round Omits MixColumns

A common beginner question is whether omitting `MixColumns` weakens the final round.

The omission is part of Rijndael's construction and makes encryption/decryption structure more convenient without simply deleting all diffusion from the end of the cipher. By the time the final round is reached, the preceding rounds have already produced extensive diffusion.

It is also useful to remember that a fixed invertible linear transformation at the very end can often be algebraically moved or absorbed into nearby key material when reasoning about the structure. The security margin must therefore be studied at the level of the whole cipher, not by counting operations in isolation.

---

## 18. AES Is a Primitive, Not a Complete Encryption Protocol

The class in this article accepts exactly one 16-byte block:

```python
ciphertext = aes.encrypt_block(block)
```

Real messages can be longer, shorter, streamed, repeated, reordered, or modified by an adversary. A block cipher alone does not specify how to handle those issues.

A production system normally uses a standardized mode or AEAD construction, for example:

- AES-GCM,
- AES-CCM,
- AES-GCM-SIV in environments where that construction is appropriate,
- other protocol-specific constructions with well-defined nonce and authentication rules.

The naive pattern

```python
for block in message_blocks:
    encrypt_block(block)
```

is ECB and leaks equality patterns between repeated plaintext blocks.

That is why the article deliberately stops at the **block primitive boundary**.

---

## 19. Implementation Security Is Different from Algorithmic Correctness

The Python implementation can be byte-for-byte correct and still be unsuitable for secret production data.

### 19.1 Table lookups

`S_BOX[state_byte]` performs a data-dependent memory access. In low-level implementations, cache behavior can leak information about secret-dependent accesses.

### 19.2 Timing and microarchitecture

Constant-time behavior is a property of the compiled implementation and hardware execution environment, not just of the mathematical algorithm.

### 19.3 Hardware instructions

Modern processors commonly provide dedicated AES instructions. Well-engineered libraries use platform-specific implementations designed for performance and side-channel resistance.

### 19.4 Do not replace mature libraries with educational code

The value of from-scratch AES is transparency: every byte transformation can be inspected. The value of a production cryptographic library is that implementation details, side channels, parameter validation, and mode semantics have already received specialized engineering attention.

---

## 20. Tests Worth Keeping with the Code

A useful educational test suite should include at least:

```python
def test_known_vector():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    p = bytes.fromhex("00112233445566778899aabbccddeeff")
    c = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")

    aes = AES128(key)
    assert aes.encrypt_block(p) == c
    assert aes.decrypt_block(c) == p


def test_original_example():
    key = b"some 16 byte key"
    p = b"some 16 byte msg"
    expected = bytes.fromhex("ce4236c54ac0be177704de7a7197b5ca")

    aes = AES128(key)
    assert aes.encrypt_block(p) == expected
    assert aes.decrypt_block(expected) == p


def test_sbox_inverse():
    for x in range(256):
        assert INV_S_BOX[S_BOX[x]] == x


def test_mixcolumns_inverse():
    test_state = bytes_to_state(bytes(range(16)))
    original = [col[:] for col in test_state]
    mix_columns(test_state)
    inv_mix_columns(test_state)
    assert test_state == original
```

A stronger development setup can additionally generate random keys and blocks and compare every result against a trusted library.

---

## 21. From the Toy SPN to AES

The first article in this series built a toy SPN with

```text
AddRoundKey -> S-box layer -> bit permutation
```

and repeated that structure for several rounds.

AES follows the same high-level philosophy but replaces the toy pieces with carefully engineered transformations:

| Toy SPN concept | AES realization |
|---|---|
| fixed-size state | 128-bit / 16-byte state |
| S-box layer | sixteen parallel 8-bit AES S-boxes |
| permutation / diffusion | ShiftRows + MixColumns |
| round-key XOR | AddRoundKey |
| toy key schedule | AES key expansion |
| repeated rounds | 10 rounds for AES-128 |

The crucial conceptual upgrade is that AES diffusion is not merely a bit permutation. It is an algebraically designed linear layer over $GF(2^8)$.

That is the bridge from a classroom SPN to a modern standardized block cipher.

---

## 22. From DES to AES

DES and AES also illustrate two different construction philosophies.

| Property | DES | AES-128 |
|---|---|---|
| Structure | Feistel | SPN |
| Block size | 64 bits | 128 bits |
| Effective key size | 56 bits | 128 bits |
| Rounds | 16 | 10 |
| Main nonlinear layer | 8 S-boxes, 6→4 bits | 16 S-boxes, 8→8 bits |
| Round-function invertibility required? | No | AES layers are individually invertible |
| Main diffusion | E/P permutations + Feistel iteration | ShiftRows + MDS MixColumns |

This is why placing DES immediately before AES in the series is useful: the reader sees that secure block-cipher design does not require one universal network architecture.

---

## 23. What the Tests Establish — and What They Do Not

When

```python
AES128(key).encrypt_block(plaintext)
```

matches the standardized ciphertext, we have strong evidence that:

- state loading is correct,
- `SubBytes` is correct,
- `ShiftRows` uses the intended orientation,
- `MixColumns` is correct,
- key expansion is correct,
- round ordering is correct,
- the last-round special case is correct.

When decryption also recovers the input, we additionally validate the inverse path.

These tests do **not** establish:

- resistance to side-channel leakage,
- secure multi-block encryption,
- correct nonce management,
- authentication,
- constant-time execution,
- formal proof of the implementation,
- security of an application protocol using the primitive.

Correct cryptographic engineering requires keeping those layers separate.

---

## 24. Conclusion

AES is an unusually good cipher to study because the design connects several mathematical ideas directly to executable code.

At the byte level, the S-box starts from inversion in

$$
GF(2^8).
$$

At the column level, diffusion is matrix multiplication in the same field. At the state level, `ShiftRows` couples those local column transformations across rounds. At the key level, the key schedule generates deterministic round material through `RotWord`, `SubWord`, `Rcon`, and XOR recurrences.

The complete AES-128 encryption path is therefore:

$$
\boxed{
P
\xrightarrow{\oplus K_0}
\left[
SB\rightarrow SR\rightarrow MC\rightarrow\oplus K_r
\right]^9
\rightarrow
SB\rightarrow SR\rightarrow\oplus K_{10}
\rightarrow C
}
$$

and the reference example gives

$$
\boxed{
\texttt{00112233445566778899aabbccddeeff}
\mapsto
\texttt{69c4e0d86a7b0430d8cdb78070b4c55a}
}.
$$

The implementation in this article is intentionally transparent enough to inspect every intermediate value. That makes it a useful base for the next level of analysis: differential propagation, linear approximations, active S-box bounds, implementation trade-offs, and eventually authenticated modes built on top of the AES primitive.

---

## References

1. National Institute of Standards and Technology, **FIPS 197: Advanced Encryption Standard (AES)**, updated May 9, 2023.  
   https://doi.org/10.6028/NIST.FIPS.197-upd1

2. Joan Daemen and Vincent Rijmen, **The Design of Rijndael: AES — The Advanced Encryption Standard**, Springer.

3. NIST Cryptographic Standards and Guidelines, **Block Cipher Techniques**.  
   https://csrc.nist.gov/projects/block-cipher-techniques

4. PyCryptodome documentation, **AES**.  
   https://pycryptodome.readthedocs.io/
