---
title: "Block Cipher Design: Substitution–Permutation Networks"
description: "A construction-oriented deep dive into block ciphers, confusion and diffusion, round functions, key schedules, S-boxes, permutation layers, reversibility, and a complete educational SPN implementation."
pubDate: "2025-04-12"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Cryptographic Engineering"
tags:
  - "block-cipher"
  - "spn"
  - "sbox"
  - "pbox"
  - "confusion"
  - "diffusion"
  - "key-schedule"
  - "cryptanalysis"
difficulty: "Intermediate"
series: "Symmetric Cryptography"
seriesOrder: 1
sourcePath: "experiments/ready-material/spn"
draft: false
---

## Table of Contents

- [1. Why Start with an SPN?](#1-why-start-with-an-spn)
- [2. What Is a Block Cipher?](#2-what-is-a-block-cipher)
- [3. Confusion and Diffusion](#3-confusion-and-diffusion)
- [4. Cryptanalytic Cost: Time, Memory, Data, and Success Probability](#4-cryptanalytic-cost-time-memory-data-and-success-probability)
- [5. Two Major Construction Paradigms](#5-two-major-construction-paradigms)
- [6. Designing an Iterated Block Cipher](#6-designing-an-iterated-block-cipher)
- [7. A Formal SPN Model](#7-a-formal-spn-model)
- [8. The Educational 16-bit SPN](#8-the-educational-16-bit-spn)
- [9. The S-box](#9-the-s-box)
- [10. The P-box](#10-the-p-box)
- [11. Bit-Level Utilities](#11-bit-level-utilities)
- [12. Generalized Substitution and Permutation Functions](#12-generalized-substitution-and-permutation-functions)
- [13. Full Encryption Walkthrough](#13-full-encryption-walkthrough)
- [14. Decryption and Inverse Layers](#14-decryption-and-inverse-layers)
- [15. Complete Functional Implementation](#15-complete-functional-implementation)
- [16. Object-Oriented SPN Implementation](#16-object-oriented-spn-implementation)
- [17. Tests and Known-Answer Checks](#17-tests-and-known-answer-checks)
- [18. Measuring Diffusion Instead of Merely Claiming It](#18-measuring-diffusion-instead-of-merely-claiming-it)
- [19. What This Toy Cipher Teaches — and What It Does Not](#19-what-this-toy-cipher-teaches--and-what-it-does-not)
- [20. Connection to AES](#20-connection-to-aes)
- [21. Design Lessons](#21-design-lessons)
- [22. Conclusion](#22-conclusion)
- [23. References and Further Reading](#23-references-and-further-reading)

---

## 1. Why Start with an SPN?

A block cipher can look intimidating when we first meet a real construction such as AES. There are byte substitutions, linear transformations, round keys, finite-field arithmetic, a key schedule, and a carefully chosen number of rounds. If we begin directly with all of those details, it is easy to learn the mechanics without understanding the design logic.

A small **Substitution–Permutation Network (SPN)** is therefore one of the best models for learning how modern block-cipher design works.

The central idea is simple:

1. mix secret key material into the internal state,
2. apply a **nonlinear substitution layer**,
3. spread local changes across the state with a **diffusion layer**,
4. repeat this process for several rounds.

The important point is not that one S-box or one permutation is magically secure. Security is intended to emerge from the **iterated composition** of carefully designed components.

In this article we will build a complete 16-bit educational SPN from first principles. We will preserve the same S-box, P-box, plaintext, master key, and round-key structure throughout so that the exact same toy cipher can later be reused when studying:

- differential cryptanalysis,
- linear cryptanalysis,
- S-box design criteria,
- avalanche behavior,
- active S-boxes,
- trail probabilities,
- key-recovery experiments.

The construction is intentionally small enough to inspect by hand, but structurally rich enough to expose the mechanisms used in serious symmetric cryptography.

> **Important:** the cipher in this article is an educational object. A 16-bit block and a 32-bit master key are far too small for real security.

---

## 2. What Is a Block Cipher?

A **block cipher** is a keyed family of transformations that maps fixed-size plaintext blocks to ciphertext blocks of the same size.

Modern standardized block ciphers commonly use 128-bit blocks. AES, for example, always operates on 128-bit blocks and supports keys of 128, 192, or 256 bits.

### 2.1 Formal definition

Let

$$
\mathcal{K}
$$

be the key space and let the block size be $n$ bits. Encryption is a function

$$
E : \mathcal{K} \times \{0,1\}^{n} \rightarrow \{0,1\}^{n}.
$$

For a fixed key $K$, define

$$
E_K(x) = E(K,x).
$$

A valid block cipher requires $E_K$ to be a **permutation** of the $2^n$ possible blocks. In other words, for every fixed key:

$$
E_K : \{0,1\}^{n} \rightarrow \{0,1\}^{n}
$$

must be bijective.

Why?

Because decryption must exist. There must be a unique inverse transformation

$$
D_K = E_K^{-1}
$$

such that

$$
D_K(E_K(x)) = x
$$

for every plaintext block $x$.

This permutation viewpoint is fundamental. A block cipher is not merely a complicated function. It is a **key-selected permutation** over the block space.

### 2.2 Block size and key size are different security parameters

Two sizes characterize a block cipher:

- **block size $n$** — how many bits are transformed at one time,
- **key size $k$** — how many bits determine the secret key.

These parameters play different roles.

If the key is uniformly sampled from a $k$-bit space, exhaustive key search can require up to

$$
2^k
$$

candidate keys, with about

$$
2^{k-1}
$$

trials on average if the correct key is equally likely to appear anywhere in the search order.

The block size controls a different phenomenon: the cipher only has $2^n$ possible inputs and outputs. In many modes and protocols, collision-style effects become relevant around the birthday scale

$$
2^{n/2}.
$$

This is one reason a tiny educational block size such as $n=16$ is useful for experiments but completely inappropriate for deployment.

---

## 3. Confusion and Diffusion

The classical language of **confusion** and **diffusion** comes from Claude Shannon's foundational work on secrecy systems.

These terms are still extremely useful, but they are sometimes taught too loosely. We will use them carefully.

### 3.1 Confusion

Confusion aims to make the relationship between the secret key and the ciphertext sufficiently complicated that an attacker cannot exploit simple algebraic or statistical dependencies.

In an SPN, the main source of this complexity is the **nonlinear S-box layer**.

If every operation in a cipher were linear or affine over $\mathbb{F}_2$, then the complete cipher would remain linear or affine. The attacker could then represent encryption using systems of linear equations and recover structure that a secure cipher must hide.

The S-box breaks this linearity.

### 3.2 Diffusion

Diffusion spreads local information across the state.

Suppose one S-box changes four output bits, but those four bits simply feed the same S-box position in every subsequent round. Then the cipher decomposes into nearly independent small components. That structure is dangerous.

A diffusion layer instead routes bits so that outputs from one S-box influence several S-boxes in the next round. After enough rounds, a small change in the plaintext can affect a large fraction of the internal state.

This is the purpose of the P-box in our toy SPN.

### 3.3 What the key XOR does — and does not do

A common oversimplification is:

> the S-box and P-box are public, while XOR with the secret key is what provides the security.

That is not an accurate model of block-cipher design.

Key addition is essential because it makes the transformation depend on secret material. However, XOR with a fixed key is only an affine transformation:

$$
x \mapsto x \oplus K.
$$

By itself, it provides no nonlinear complexity.

Likewise, a public S-box and a public diffusion layer are not supposed to be secret. Modern cryptography assumes the adversary knows the algorithm. Security should depend on the key, not on hiding the design.

The intended strength comes from the **composition**

$$
\text{key mixing}
\;\rightarrow\;
\text{nonlinearity}
\;\rightarrow\;
\text{diffusion}
\;\rightarrow\;
\text{repetition}.
$$

This is a direct application of Kerckhoffs-style design thinking: the mechanism may be public; only the key needs to remain secret.

---

## 4. Cryptanalytic Cost: Time, Memory, Data, and Success Probability

When we evaluate an attack against a block cipher, we should not describe its complexity using only one number.

At minimum, we usually care about:

- **time complexity** — number of computations or primitive operations,
- **memory complexity** — storage required by the attack,
- **data complexity** — number and type of plaintext/ciphertext observations required,
- **success probability** — probability that the attack succeeds under the stated resources.

The data model also matters. An attack may require:

- ciphertext-only data,
- known plaintext/ciphertext pairs,
- chosen plaintexts,
- chosen ciphertexts,
- adaptively selected queries.

Key recovery is an important cryptanalytic objective, but it is not the only one. Depending on the security notion, an adversary may instead seek to:

- distinguish the cipher from an idealized random object,
- predict information about plaintexts,
- recover partial key information,
- construct high-probability differential trails,
- identify linear correlations,
- exploit structural weaknesses.

A strong practical cipher should not admit attacks that substantially outperform the intended security level under realistic resource assumptions.

For our 32-bit toy key, generic exhaustive search is trivial by modern standards. That is acceptable because the construction exists for study, not deployment.

---

## 5. Two Major Construction Paradigms

Two major iterative structures appear repeatedly in classical block-cipher design.

### 5.1 Feistel networks

A Feistel network divides the state into two parts, often written

$$
(L_r,R_r).
$$

A typical round has the form

$$
L_{r+1} = R_r,
$$

$$
R_{r+1} = L_r \oplus F(R_r,K_r).
$$

The important structural property is that the round function $F$ itself does **not** need to be invertible. The Feistel structure guarantees invertibility of the complete round.

DES is the classical example.

### 5.2 Substitution–Permutation Networks

An SPN transforms the **entire state** using invertible layers.

A typical round combines:

1. round-key addition,
2. parallel S-box substitution,
3. a permutation or more general linear diffusion layer.

AES follows an SPN-style design philosophy, although its diffusion layer is richer than a simple bit permutation: it combines `ShiftRows` and `MixColumns` with the nonlinear `SubBytes` layer and `AddRoundKey`.

The key structural difference is that an SPN normally builds the whole round from individually invertible state transformations.

---

## 6. Designing an Iterated Block Cipher

An iterated block cipher repeatedly applies a round transformation to an internal state.

Two components deserve separate attention:

1. the **round function**,
2. the **key schedule**.

### 6.1 The key schedule

Let the master key be

$$
K.
$$

A key schedule derives round keys

$$
K^1,K^2,\ldots,K^t.
$$

![Key Schedule Overview](/images/ready/block-cipher-design-spn/keyschedule.PNG)

A real key schedule is not merely a formatting convenience. Its design influences resistance to:

- related-key attacks,
- slide-like structure,
- weak-key classes,
- symmetry across rounds,
- implementation constraints.

Different ciphers make different tradeoffs. Some schedules are deliberately simple; others use nonlinear operations, rotations, round constants, or recursive expansion.

Our toy cipher uses a deliberately simple overlapping-window schedule because it is transparent enough to compute by hand. We should **not** interpret that schedule as a generally secure design recommendation.

### 6.2 The round function

Let $w^{r-1}$ be the state entering round $r$. A generic keyed round can be written as

$$
w^r = g(w^{r-1},K^r).
$$

Repeated rounds produce

$$
w^0
\xrightarrow{K^1}
w^1
\xrightarrow{K^2}
w^2
\xrightarrow{K^3}
\cdots
\xrightarrow{K^t}
w^t.
$$

The design objective is not merely to make $g$ look complicated. We want repeated rounds to destroy exploitable local structure while remaining efficiently invertible for legitimate decryption.

### 6.3 Reversibility

For an SPN, each state transformation must be invertible if we want to reverse the round directly.

For a round transformation $g$, we require an inverse $g^{-1}$ such that

$$
g^{-1}(g(w,K),K)=w.
$$

That implies, for our construction:

- the S-box must be bijective,
- the bit permutation must be bijective,
- XOR with a round key is automatically invertible because

$$
(x\oplus K)\oplus K=x.
$$

A Feistel network is different: its internal $F$ function can be non-invertible because the Feistel wiring itself remains reversible.

---

## 7. A Formal SPN Model

We now formalize the structure used throughout the rest of the article.

### 7.1 State decomposition

Let

$$
l,m\in\mathbb{Z}_{>0}
$$

and define the block size

$$
n=lm.
$$

The plaintext and ciphertext spaces are

$$
\mathcal{M}=\mathcal{C}=\{0,1\}^{n}.
$$

We split the state into $m$ chunks of $l$ bits:

$$
x=x_0\|x_1\|\cdots\|x_{m-1},
\qquad x_i\in\{0,1\}^{l}.
$$

For the toy cipher:

$$
l=4,\qquad m=4,\qquad n=16.
$$

So each 16-bit state is interpreted as four 4-bit nibbles.

### 7.2 S-box layer

Let

$$
\pi_S:\{0,1\}^{l}\rightarrow\{0,1\}^{l}
$$

be a bijective nonlinear S-box.

The parallel substitution layer is

$$
S(x_0\|x_1\|\cdots\|x_{m-1})
=
\pi_S(x_0)\|\pi_S(x_1)\|\cdots\|\pi_S(x_{m-1}).
$$

Each S-box is local, but all $m$ copies operate in parallel.

### 7.3 Permutation layer

Let

$$
P:\{0,1\}^{n}\rightarrow\{0,1\}^{n}
$$

be a permutation of bit positions.

The P-layer is linear over $\mathbb{F}_2$, but it rearranges where S-box outputs travel before the next round.

This is what connects otherwise local S-box computations into a network.

### 7.4 Key addition

For a round key $K^r\in\{0,1\}^{n}$, define

$$
A_{K^r}(x)=x\oplus K^r.
$$

Since XOR is its own inverse,

$$
A_{K^r}^{-1}=A_{K^r}.
$$

### 7.5 The round ordering used in this article

There are several equivalent-looking diagram conventions in textbooks, so the exact ordering must be stated explicitly.

The implementation in this article uses, for the first three rounds,

$$
u^r=w^{r-1}\oplus K^r,
$$

$$
v^r=S(u^r),
$$

$$
w^r=P(v^r).
$$

The final round omits the P-layer:

$$
u^4=w^3\oplus K^4,
$$

$$
v^4=S(u^4),
$$

$$
y=v^4\oplus K^5.
$$

So the complete toy cipher is

$$
E_K
=
A_{K^5}
\circ S
\circ A_{K^4}
\circ P
\circ S
\circ A_{K^3}
\circ P
\circ S
\circ A_{K^2}
\circ P
\circ S
\circ A_{K^1}.
$$

This ordering is chosen to match the executable code exactly.

![SPN Layered Architecture](/images/ready/block-cipher-design-spn/sp.PNG)

![SPN Round-by-Round Detail](/images/ready/block-cipher-design-spn/encryption.PNG)

> **Diagram note:** SPN diagrams are often drawn with key mixing before or after a visual round boundary. The equations and code above define the convention used here and remove any ambiguity.

---

## 8. The Educational 16-bit SPN

### 8.1 Parameters

Our fixed educational construction uses:

| Parameter | Value |
|---|---:|
| Block size | 16 bits |
| S-box width | 4 bits |
| S-boxes per layer | 4 |
| Main rounds | 4 |
| Round keys | 5 × 16 bits |
| Master key | 32 bits |
| Diffusion layer | 16-bit permutation |

The final round contains substitution and final key addition but no P-box.

This is a common pedagogical structure because it makes later differential and linear cryptanalysis easier to express.

### 8.2 Master key and round keys

We preserve the original 32-bit master key:

```python
K = 0b0011_1010_1001_0100_1101_0110_0011_1111
```

In hexadecimal,

$$
K=\texttt{0x3A94D63F}.
$$

We derive five 16-bit round keys by sliding a 16-bit window four bits at a time across the 32-bit master key:

$$
K^1=\texttt{0x3A94},
$$

$$
K^2=\texttt{0xA94D},
$$

$$
K^3=\texttt{0x94D6},
$$

$$
K^4=\texttt{0x4D63},
$$

$$
K^5=\texttt{0xD63F}.
$$

In binary:

```text
K1 = 0011 1010 1001 0100
K2 = 1010 1001 0100 1101
K3 = 1001 0100 1101 0110
K4 = 0100 1101 0110 0011
K5 = 1101 0110 0011 1111
```

The overlap is useful pedagogically because the derivation is immediately visible from the master key.

However, we should be precise about what this means:

- overlap does **not** automatically make a key schedule secure,
- overlap does **not** by itself guarantee good diffusion,
- this schedule is intentionally simple,
- a production cipher requires a key schedule justified against the relevant attack models.

### 8.3 Plaintext

We preserve the original 16-bit plaintext:

```python
m = 0b0010_0110_1011_0111
```

or

$$
m=\texttt{0x26B7}.
$$

This same plaintext will be traced through every round.

---

## 9. The S-box

### 9.1 Mapping

The 4-bit S-box is:

| $z$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $\pi_S(z)$ | E | 4 | D | 1 | 2 | F | B | 8 | 3 | A | 6 | C | 5 | 9 | 0 | 7 |

In Python:

```python
S = [14, 4, 13, 1, 2, 15, 11, 8,
     3, 10, 6, 12, 5, 9, 0, 7]
```

For example,

$$
\pi_S(0)=E,
\qquad
\pi_S(1)=4,
\qquad
\pi_S(F)=7.
$$

For the 16-bit value

$$
\texttt{0x0123},
$$

parallel substitution gives

$$
0\mapsto E,
\quad
1\mapsto 4,
\quad
2\mapsto D,
\quad
3\mapsto 1,
$$

therefore

$$
S(\texttt{0x0123})=\texttt{0xE4D1}.
$$

### 9.2 Why the S-box must be nonlinear

Suppose instead that the S-box were an affine map

$$
S(x)=Ax\oplus b
$$

over $\mathbb{F}_2$.

The P-box is linear, and key XOR is affine. A composition of affine maps is still affine. Therefore a multi-round cipher made only from affine operations would collapse into one global affine transformation:

$$
E_K(x)=Mx\oplus c_K.
$$

That would expose enormous algebraic structure.

The S-box exists specifically to prevent that collapse.

For an invertible SPN, it must also be a permutation of the 16 possible nibble values. Our S-box contains every value from $0$ to $15$ exactly once, so its inverse exists.

### 9.3 First quantitative look: DDT and LAT

S-box quality cannot be assessed merely by looking at the table.

Two central cryptanalytic tools are:

- the **Difference Distribution Table (DDT)**,
- the **Linear Approximation Table (LAT)**.

For an input difference $\Delta x$ and output difference $\Delta y$, the DDT entry is

$$
\operatorname{DDT}[\Delta x,\Delta y]
=
\#\left\{
 x:\pi_S(x)\oplus\pi_S(x\oplus\Delta x)=\Delta y
\right\}.
$$

For this S-box, the largest nontrivial DDT entry is

$$
8.
$$

Thus its maximum single-S-box differential probability is

$$
\frac{8}{16}=\frac12.
$$

That is intentionally weak by modern design standards, but useful for teaching differential cryptanalysis because high-probability trails are easy to observe.

For linear cryptanalysis, define

$$
\operatorname{LAT}[a,b]
=
\sum_{x\in\{0,1\}^4}
(-1)^{\langle a,x\rangle\oplus\langle b,\pi_S(x)\rangle}.
$$

For nonzero input and output masks, this S-box reaches

$$
|\operatorname{LAT}[a,b]|=12.
$$

Since there are 16 inputs, that corresponds to a strong linear bias for some mask pairs. Again, this is valuable for pedagogy but not evidence of a modern secure S-box.

We will derive and visualize complete DDT and LAT tables later in the cryptanalysis parts of this series.

---

## 10. The P-box

### 10.1 Mapping

The 16-bit permutation is

| output position $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| source position | 0 | 4 | 8 | 12 | 1 | 5 | 9 | 13 | 2 | 6 | 10 | 14 | 3 | 7 | 11 | 15 |

In Python:

```python
P = [0, 4, 8, 12,
     1, 5, 9, 13,
     2, 6, 10, 14,
     3, 7, 11, 15]
```

### 10.2 Why this permutation creates inter-S-box diffusion

Before the P-layer, the S-box layer produces four 4-bit outputs:

```text
S0: bits  0  1  2  3
S1: bits  4  5  6  7
S2: bits  8  9 10 11
S3: bits 12 13 14 15
```

The P-layer redistributes those bits so that bits entering one S-box in the next round originate from several different S-boxes in the previous round.

Conceptually:

```text
one active S-box output
        |
        v
bits are separated by P
   /    |    |    \
  v     v    v     v
multiple next-round S-boxes
```

That is the mechanism by which local nonlinear activity can spread across the state.

A permutation alone does not increase the number of changed bits. It only **moves** them. Its value appears across rounds because it changes which S-boxes become active next.

### 10.3 A subtle implementation convention

There are two common ways to write a permutation table:

1. **source-to-destination:** input bit $i$ moves to position $P(i)$,
2. **destination-to-source:** output bit $i$ is read from input position $P[i]$.

Our `permute()` function uses the second convention.

That distinction often causes silent bugs.

For this particular P-box, however,

$$
P^{-1}=P.
$$

The permutation is an **involution**. This means the same table can be used in both directions, which is why a mistaken assumption about inverse permutation can remain hidden in a toy implementation.

We will still compute the inverse explicitly in code because the implementation should remain correct for arbitrary permutation tables.

---

## 11. Bit-Level Utilities

The original implementation included several small bit helpers. We retain them because they are useful both for construction and for later cryptanalysis.

```python
def bit_parity(x: int) -> int:
    """Return the XOR of all bits of x."""
    return x.bit_count() & 1


def get_bit(x: int, i: int, n: int) -> int:
    """
    Return bit i of an n-bit word, indexing from the left.

    Example:
        x = 1010
        i = 0123

        get_bit(0b1010, 1, 4) == 0
    """
    if not 0 <= i < n:
        raise IndexError("bit index outside the word")
    return (x >> (n - 1 - i)) & 1


def set_bit(x: int, i: int, n: int, b: int) -> int:
    """Set bit i of an n-bit word to 0 or 1."""
    if not 0 <= i < n:
        raise IndexError("bit index outside the word")
    if b not in (0, 1):
        raise ValueError("b must be 0 or 1")

    mask = 1 << (n - 1 - i)
    if b:
        return x | mask
    return x & ~mask
```

The parity function is not needed by encryption itself. We deliberately keep it because linear cryptanalysis repeatedly evaluates mask parities such as

$$
\langle a,x\rangle
=
\operatorname{parity}(a\land x).
$$

Basic checks:

```python
assert bit_parity(0b1010) == 0
assert bit_parity(0b1011) == 1

assert get_bit(0b1010, 1, 4) == 0
assert set_bit(0b1010, 1, 4, 1) == 0b1110
assert set_bit(0b1010, 2, 4, 0) == 0b1000
```

---

## 12. Generalized Substitution and Permutation Functions

The earlier version of `substitute()` implicitly assumed that

$$
\text{block size}=2^l.
$$

For $l=4$, this happens to give 16 and therefore works for our toy cipher. But the S-box width and block size are conceptually independent parameters.

We correct that here.

```python
def validate_sbox(sbox: list[int]) -> None:
    size = len(sbox)

    if size == 0 or size & (size - 1):
        raise ValueError("S-box length must be a power of two")

    if sorted(sbox) != list(range(size)):
        raise ValueError("S-box must be a permutation")


def inverse_sbox(sbox: list[int]) -> list[int]:
    validate_sbox(sbox)
    inv = [0] * len(sbox)
    for x, y in enumerate(sbox):
        inv[y] = x
    return inv


def substitute(
    x: int,
    sbox: list[int],
    sbox_bits: int,
    block_size: int,
) -> int:
    """Apply the S-box independently to each sbox_bits-wide chunk."""
    validate_sbox(sbox)

    if len(sbox) != 1 << sbox_bits:
        raise ValueError("S-box length does not match sbox_bits")

    if block_size % sbox_bits != 0:
        raise ValueError("block_size must be divisible by sbox_bits")

    if not 0 <= x < (1 << block_size):
        raise ValueError("x does not fit in block_size bits")

    mask = (1 << sbox_bits) - 1
    y = 0

    for shift in range(block_size - sbox_bits, -1, -sbox_bits):
        chunk = (x >> shift) & mask
        y = (y << sbox_bits) | sbox[chunk]

    return y
```

For permutation:

```python
def validate_pbox(pbox: list[int], n: int) -> None:
    if len(pbox) != n:
        raise ValueError("P-box length must equal the block size")

    if sorted(pbox) != list(range(n)):
        raise ValueError("P-box must contain each bit position exactly once")


def inverse_pbox(pbox: list[int]) -> list[int]:
    n = len(pbox)
    validate_pbox(pbox, n)

    inv = [0] * n
    for output_pos, source_pos in enumerate(pbox):
        inv[source_pos] = output_pos

    return inv


def permute(x: int, pbox: list[int], n: int) -> int:
    """
    Destination-to-source convention:
    output bit i is copied from input bit pbox[i].
    """
    validate_pbox(pbox, n)

    if not 0 <= x < (1 << n):
        raise ValueError("x does not fit in n bits")

    y = 0
    for source_pos in pbox:
        y = (y << 1) | get_bit(x, source_pos, n)

    return y
```

Now the interfaces express exactly what the operations require.

We can verify the original example:

```python
S = [14, 4, 13, 1, 2, 15, 11, 8,
     3, 10, 6, 12, 5, 9, 0, 7]

P = [0, 4, 8, 12,
     1, 5, 9, 13,
     2, 6, 10, 14,
     3, 7, 11, 15]

assert substitute(0x0123, S, 4, 16) == 0xE4D1
assert inverse_pbox(P) == P
```

---

## 13. Full Encryption Walkthrough

Now we encrypt

$$
m=\texttt{0x26B7}
$$

under

$$
K=\texttt{0x3A94D63F}.
$$

The derived round keys are

```text
K1 = 3A94
K2 = A94D
K3 = 94D6
K4 = 4D63
K5 = D63F
```

### 13.1 Round 1 in detail

The input state is

$$
w^0=\texttt{0x26B7}.
$$

#### Step 1: Add the first round key

$$
u^1=w^0\oplus K^1.
$$

So

```text
  26B7
⊕ 3A94
------
  1C23
```

Hence

$$
u^1=\texttt{0x1C23}.
$$

#### Step 2: Substitute each nibble

Split

$$
\texttt{1C23}
$$

to

$$
1\|C\|2\|3.
$$

Apply the S-box:

$$
1\mapsto4,
\quad
C\mapsto5,
\quad
2\mapsto D,
\quad
3\mapsto1.
$$

Therefore

$$
v^1=\texttt{0x45D1}.
$$

#### Step 3: Permute the 16 output bits

Apply the P-box:

$$
w^1=P(v^1)=\texttt{0x2E07}.
$$

That state enters round 2.

### 13.2 All rounds

The complete execution is:

| Round | Input $w^{r-1}$ | Round key | After XOR $u^r$ | After S-box $v^r$ | After P / Final output |
|---:|---:|---:|---:|---:|---:|
| 1 | `26B7` | `3A94` | `1C23` | `45D1` | `2E07` |
| 2 | `2E07` | `A94D` | `874A` | `3826` | `41B8` |
| 3 | `41B8` | `94D6` | `D56E` | `9FB0` | `E46E` |
| 4 | `E46E` | `4D63` | `A90D` | `6AE9` | `BCD6` after XOR with `D63F` |

Thus the ciphertext is

$$
\boxed{\texttt{0xBCD6}}.
$$

In binary:

$$
\boxed{1011\;1100\;1101\;0110}.
$$

This gives us a useful **known-answer test** for every future refactoring of the implementation.

---

## 14. Decryption and Inverse Layers

Encryption is a composition of invertible functions, so decryption applies their inverses in reverse order.

From

$$
y=v^4\oplus K^5,
$$

we recover

$$
v^4=y\oplus K^5.
$$

Then

$$
u^4=S^{-1}(v^4),
$$

and

$$
w^3=u^4\oplus K^4.
$$

For each earlier full round we undo:

1. the permutation,
2. the substitution,
3. the round-key XOR.

So for round $r$, in reverse:

$$
v^r=P^{-1}(w^r),
$$

$$
u^r=S^{-1}(v^r),
$$

$$
w^{r-1}=u^r\oplus K^r.
$$

The inverse S-box is computed mechanically:

```python
S_inv = inverse_sbox(S)
```

and the inverse P-box is

```python
P_inv = inverse_pbox(P)
```

For this particular permutation,

```python
P_inv == P
```

is `True`, but our decryption code must not rely on that special case.

---

## 15. Complete Functional Implementation

The following is the corrected, self-contained functional version.

```python
from __future__ import annotations


# -----------------------------------------------------------------------------
# Bit utilities
# -----------------------------------------------------------------------------

def bit_parity(x: int) -> int:
    """Return the XOR of all bits of x."""
    return x.bit_count() & 1


def get_bit(x: int, i: int, n: int) -> int:
    """Return bit i of an n-bit word, indexing from the left."""
    if not 0 <= i < n:
        raise IndexError("bit index outside the word")
    return (x >> (n - 1 - i)) & 1


def set_bit(x: int, i: int, n: int, b: int) -> int:
    """Set bit i of an n-bit word to b in {0,1}."""
    if not 0 <= i < n:
        raise IndexError("bit index outside the word")
    if b not in (0, 1):
        raise ValueError("b must be 0 or 1")

    mask = 1 << (n - 1 - i)
    return (x | mask) if b else (x & ~mask)


# -----------------------------------------------------------------------------
# S-box helpers
# -----------------------------------------------------------------------------

def validate_sbox(sbox: list[int]) -> None:
    size = len(sbox)

    if size == 0 or size & (size - 1):
        raise ValueError("S-box length must be a power of two")

    if sorted(sbox) != list(range(size)):
        raise ValueError("S-box must be a permutation")


def inverse_sbox(sbox: list[int]) -> list[int]:
    validate_sbox(sbox)

    inv = [0] * len(sbox)
    for x, y in enumerate(sbox):
        inv[y] = x

    return inv


def substitute(
    x: int,
    sbox: list[int],
    sbox_bits: int,
    block_size: int,
) -> int:
    """Apply sbox independently to each sbox_bits-wide chunk."""
    validate_sbox(sbox)

    if len(sbox) != 1 << sbox_bits:
        raise ValueError("S-box length does not match sbox_bits")

    if block_size % sbox_bits != 0:
        raise ValueError("block_size must be divisible by sbox_bits")

    if not 0 <= x < (1 << block_size):
        raise ValueError("x does not fit in block_size bits")

    mask = (1 << sbox_bits) - 1
    y = 0

    for shift in range(block_size - sbox_bits, -1, -sbox_bits):
        chunk = (x >> shift) & mask
        y = (y << sbox_bits) | sbox[chunk]

    return y


# -----------------------------------------------------------------------------
# P-box helpers
# -----------------------------------------------------------------------------

def validate_pbox(pbox: list[int], n: int) -> None:
    if len(pbox) != n:
        raise ValueError("P-box length must equal the block size")

    if sorted(pbox) != list(range(n)):
        raise ValueError("P-box must contain each bit position exactly once")


def inverse_pbox(pbox: list[int]) -> list[int]:
    n = len(pbox)
    validate_pbox(pbox, n)

    inv = [0] * n
    for output_pos, source_pos in enumerate(pbox):
        inv[source_pos] = output_pos

    return inv


def permute(x: int, pbox: list[int], n: int) -> int:
    """
    Apply a destination-to-source bit permutation.

    Output bit i is copied from input bit pbox[i].
    """
    validate_pbox(pbox, n)

    if not 0 <= x < (1 << n):
        raise ValueError("x does not fit in n bits")

    y = 0
    for source_pos in pbox:
        y = (y << 1) | get_bit(x, source_pos, n)

    return y


# -----------------------------------------------------------------------------
# Educational key schedule
# -----------------------------------------------------------------------------

def key_schedule(
    master_key: int,
    *,
    master_key_bits: int = 32,
    block_size: int = 16,
    step: int = 4,
    round_key_count: int = 5,
) -> list[int]:
    """
    Derive overlapping block_size-bit windows from the master key.

    This is a pedagogical schedule, not a production recommendation.
    """
    if not 0 <= master_key < (1 << master_key_bits):
        raise ValueError("master key does not fit master_key_bits")

    required = block_size + step * (round_key_count - 1)
    if required > master_key_bits:
        raise ValueError("master key is too short for this schedule")

    mask = (1 << block_size) - 1
    keys = []

    for r in range(round_key_count):
        shift = master_key_bits - block_size - r * step
        keys.append((master_key >> shift) & mask)

    return keys


# -----------------------------------------------------------------------------
# Encryption / decryption
# -----------------------------------------------------------------------------

def spn_encrypt(
    plaintext: int,
    master_key: int,
    sbox: list[int],
    pbox: list[int],
    *,
    block_size: int = 16,
    sbox_bits: int = 4,
    verbose: bool = False,
) -> int:
    """Encrypt one block with the educational 4-round SPN."""
    if not 0 <= plaintext < (1 << block_size):
        raise ValueError("plaintext does not fit in one block")

    round_keys = key_schedule(master_key)
    w = plaintext

    # Three full rounds: AddRoundKey -> S -> P
    for r in range(len(round_keys) - 2):
        u = w ^ round_keys[r]
        v = substitute(u, sbox, sbox_bits, block_size)
        w_next = permute(v, pbox, block_size)

        if verbose:
            print(
                f"r={r + 1}  "
                f"K={round_keys[r]:04X}  "
                f"w={w:04X}  "
                f"u={u:04X}  "
                f"v={v:04X}  "
                f"P(v)={w_next:04X}"
            )

        w = w_next

    # Final round: AddRoundKey -> S -> final AddRoundKey
    u = w ^ round_keys[-2]
    v = substitute(u, sbox, sbox_bits, block_size)
    ciphertext = v ^ round_keys[-1]

    if verbose:
        print(
            f"r={len(round_keys) - 1}  "
            f"K={round_keys[-2]:04X}  "
            f"w={w:04X}  "
            f"u={u:04X}  "
            f"v={v:04X}  "
            f"K_final={round_keys[-1]:04X}  "
            f"c={ciphertext:04X}"
        )

    return ciphertext


def spn_decrypt(
    ciphertext: int,
    master_key: int,
    sbox: list[int],
    pbox: list[int],
    *,
    block_size: int = 16,
    sbox_bits: int = 4,
) -> int:
    """Decrypt one block encrypted by spn_encrypt()."""
    if not 0 <= ciphertext < (1 << block_size):
        raise ValueError("ciphertext does not fit in one block")

    round_keys = key_schedule(master_key)
    sbox_inv = inverse_sbox(sbox)
    pbox_inv = inverse_pbox(pbox)

    # Undo final key addition, final S layer, and penultimate key addition.
    w = ciphertext ^ round_keys[-1]
    w = substitute(w, sbox_inv, sbox_bits, block_size)
    w ^= round_keys[-2]

    # Undo the three full rounds in reverse order.
    for r in range(len(round_keys) - 3, -1, -1):
        w = permute(w, pbox_inv, block_size)
        w = substitute(w, sbox_inv, sbox_bits, block_size)
        w ^= round_keys[r]

    return w
```

Define the fixed cipher parameters:

```python
S = [14, 4, 13, 1, 2, 15, 11, 8,
     3, 10, 6, 12, 5, 9, 0, 7]

P = [0, 4, 8, 12,
     1, 5, 9, 13,
     2, 6, 10, 14,
     3, 7, 11, 15]

m = 0b0010_0110_1011_0111
K = 0b0011_1010_1001_0100_1101_0110_0011_1111

c = spn_encrypt(m, K, S, P, verbose=True)
print(f"ciphertext = {c:04X}")

recovered = spn_decrypt(c, K, S, P)
print(f"recovered  = {recovered:04X}")
```

Expected result:

```text
ciphertext = BCD6
recovered  = 26B7
```

One earlier version of this material stated that `spn_network()` returned the bit length of the master key. That was a textual error: the encryption function returns the ciphertext block.

---

## 16. Object-Oriented SPN Implementation

The functional version is ideal for studying the transformations one at a time. It is also useful to keep an object-oriented form that encapsulates the cipher parameters.

The key correction here is that methods must use `self.sbox`, not a global variable named `S`, and decryption should compute the true inverse P-box instead of silently assuming the P-box is self-inverse.

```python
class SPN:
    """Educational 16-bit substitution-permutation network."""

    def __init__(
        self,
        sbox: list[int],
        pbox: list[int],
        *,
        block_size: int = 16,
        sbox_bits: int = 4,
    ) -> None:
        validate_sbox(sbox)
        validate_pbox(pbox, block_size)

        if len(sbox) != 1 << sbox_bits:
            raise ValueError("S-box size and sbox_bits disagree")

        if block_size % sbox_bits != 0:
            raise ValueError("block_size must be divisible by sbox_bits")

        self.sbox = list(sbox)
        self.sbox_inv = inverse_sbox(sbox)
        self.pbox = list(pbox)
        self.pbox_inv = inverse_pbox(pbox)
        self.block_size = block_size
        self.sbox_bits = sbox_bits

    def key_schedule(self, master_key: int) -> list[int]:
        return key_schedule(master_key)

    def encrypt(self, plaintext: int, master_key: int) -> int:
        return spn_encrypt(
            plaintext,
            master_key,
            self.sbox,
            self.pbox,
            block_size=self.block_size,
            sbox_bits=self.sbox_bits,
        )

    def decrypt(self, ciphertext: int, master_key: int) -> int:
        return spn_decrypt(
            ciphertext,
            master_key,
            self.sbox,
            self.pbox,
            block_size=self.block_size,
            sbox_bits=self.sbox_bits,
        )
```

Usage:

```python
spn = SPN(S, P)

c = spn.encrypt(m, K)
assert c == 0xBCD6

recovered = spn.decrypt(c, K)
assert recovered == m
```

The class does not make the mathematics different. It simply packages the same verified transformations into a reusable interface.

---

## 17. Tests and Known-Answer Checks

A cryptographic implementation should not be trusted because the output “looks random.” We want explicit invariants and known-answer tests.

### Helper-function tests

```python
def test_bit_helpers():
    assert bit_parity(0b1010) == 0
    assert bit_parity(0b1011) == 1
    assert get_bit(0b1010, 1, 4) == 0
    assert set_bit(0b1010, 1, 4, 1) == 0b1110
    assert set_bit(0b1010, 2, 4, 0) == 0b1000
```

### S-box inverse test

```python
def test_sbox_inverse():
    inv = inverse_sbox(S)

    for x in range(16):
        assert inv[S[x]] == x
```

### P-box inverse test

```python
def test_pbox_inverse():
    inv = inverse_pbox(P)

    for x in range(1 << 16):
        assert permute(permute(x, P, 16), inv, 16) == x
```

For this specific P-box, we can additionally verify:

```python
assert inverse_pbox(P) == P
```

### Known-answer encryption test

```python
def test_known_answer():
    assert spn_encrypt(m, K, S, P) == 0xBCD6
```

### Round-trip test

```python
def test_round_trip():
    c = spn_encrypt(m, K, S, P)
    assert spn_decrypt(c, K, S, P) == m
```

### Exhaustive plaintext round trip

Because the block size is only 16 bits, we can go further and test every possible plaintext for this fixed key:

```python
def test_all_plaintexts_for_fixed_key():
    for plaintext in range(1 << 16):
        ciphertext = spn_encrypt(plaintext, K, S, P)
        recovered = spn_decrypt(ciphertext, K, S, P)
        assert recovered == plaintext
```

Passing this test demonstrates that our implemented encryption/decryption pair is mutually inverse for the entire 16-bit domain under the chosen key.

It does **not** prove cryptographic security. Correct invertibility and security are separate properties.

---

## 18. Measuring Diffusion Instead of Merely Claiming It

It is common to say that a multi-round SPN has an “avalanche effect.” A more scientific approach is to measure what actually happens.

For a fixed key $K$, take a plaintext $x$ and flip one input bit:

$$
x' = x\oplus 2^i.
$$

Encrypt both values and measure the output Hamming distance:

$$
d_H(E_K(x),E_K(x')).
$$

For an idealized 16-bit output in which each output bit changes independently with probability $1/2$, the expected Hamming distance is

$$
16\cdot\frac12=8.
$$

We can measure this exhaustively for our tiny cipher:

```python
def hamming_distance(x: int, y: int) -> int:
    return (x ^ y).bit_count()


def average_plaintext_avalanche(master_key: int) -> float:
    # Precompute the complete 16-bit codebook once. This keeps the exhaustive
    # experiment practical while preserving exactly the same measurement.
    ciphertexts = [
        spn_encrypt(plaintext, master_key, S, P)
        for plaintext in range(1 << 16)
    ]

    total_distance = 0
    experiments = 0

    for bit in range(16):
        mask = 1 << bit

        for plaintext in range(1 << 16):
            c1 = ciphertexts[plaintext]
            c2 = ciphertexts[plaintext ^ mask]

            total_distance += hamming_distance(c1, c2)
            experiments += 1

    return total_distance / experiments


print(average_plaintext_avalanche(K))
```

For the fixed key used in this article, the exhaustive average is approximately

$$
7.9352
$$

changed ciphertext bits out of 16.

That is close to the idealized average of 8, but we must interpret the result correctly.

It tells us that the toy construction spreads single-bit plaintext changes reasonably well **under this particular metric**. It does not imply resistance to differential cryptanalysis, linear cryptanalysis, key recovery, or structural attacks.

In fact, as we already saw, the S-box has strong individual differential and linear biases. Avalanche behavior is therefore a useful engineering diagnostic, not a standalone security proof.

---

## 19. What This Toy Cipher Teaches — and What It Does Not

The construction is valuable precisely because we can inspect everything.

It teaches:

- why block-cipher encryption must be invertible,
- how key mixing changes the keyed permutation,
- why nonlinear S-boxes are required,
- how a P-layer creates cross-S-box interaction,
- why several rounds are needed,
- how a key schedule feeds round-dependent material,
- how decryption reverses composition order,
- how to build executable tests around the mathematics.

However, it is not secure enough for real use.

### The key is far too small

A 32-bit key space has only

$$
2^{32}
$$

possible keys.

That is completely inadequate against modern exhaustive search.

### The block is far too small

A 16-bit block contains only

$$
2^{16}=65,536
$$

possible values.

Repeated use would very quickly reveal collisions and structural behavior.

### The S-box is pedagogical

Its maximum differential probability is $1/2$, and it has strong linear correlations. These properties make cryptanalysis visible in small experiments, which is exactly why the S-box is useful here.

### The key schedule is pedagogical

Sliding overlapping windows are easy to understand, but the schedule was not designed as a modern production key expansion.

### A block cipher is not a complete encryption protocol

Even a secure block cipher does not tell us how to encrypt arbitrary-length messages safely.

Real systems require a mode or authenticated-encryption construction with correct handling of:

- nonces or IVs,
- message lengths,
- authentication,
- replay considerations,
- misuse conditions.

We will study those separately rather than mixing mode-of-operation issues into the internal design of the primitive.

---

## 20. Connection to AES

The toy network is not AES, but the conceptual bridge is important.

AES operates on a 128-bit state and repeatedly combines:

- `SubBytes` — a nonlinear byte-wise S-box,
- `ShiftRows` — a byte permutation,
- `MixColumns` — an invertible linear diffusion transformation,
- `AddRoundKey` — XOR with round-key material.

The final AES round omits `MixColumns`, just as many pedagogical SPNs omit the main diffusion layer in the final round.

The important progression is therefore:

```text
Toy SPN
  |
  |-- small S-boxes
  |-- simple bit permutation
  |-- simple key schedule
  |-- few rounds
  v
Modern SPN-style cipher
  |
  |-- carefully designed nonlinear layer
  |-- stronger linear diffusion
  |-- analyzed key schedule
  |-- explicit security margin
  v
AES / Rijndael design logic
```

The toy cipher strips away engineering scale so that we can see the architecture clearly.

---

## 21. Design Lessons

Several design lessons are worth carrying forward.

**First, security is compositional.** No single component should be credited with “providing the security.” Key mixing, nonlinearity, diffusion, round count, and key scheduling work together.

**Second, public components are normal.** S-boxes and diffusion layers are normally public. Their properties should withstand open analysis.

**Third, invertibility is structural.** An SPN must be designed so that the complete encryption transformation is a permutation for each key.

**Fourth, notation must match implementation.** A diagram saying `S → P → key` while code performs `key → S → P` is more than a cosmetic inconsistency. Cryptographic reasoning depends on exact layer boundaries.

**Fifth, permutation conventions matter.** `P[i] = destination` and `P[i] = source` are different conventions even when a self-inverse table accidentally hides the difference.

**Sixth, testing correctness is not testing security.** `decrypt(encrypt(m)) == m` proves a round-trip property. It does not establish resistance to cryptanalysis.

**Seventh, metrics need interpretation.** A near-ideal average avalanche measurement can coexist with exploitable differential or linear structure.

---

## 22. Conclusion

We have constructed a complete educational Substitution–Permutation Network while preserving the original architecture and examples and tightening the mathematics and implementation around them.

The cipher uses:

- a 16-bit state,
- four parallel 4-bit S-boxes,
- a 16-bit diffusion permutation,
- a 32-bit master key,
- five overlapping 16-bit round keys,
- three full `AddRoundKey → S → P` rounds,
- one final `AddRoundKey → S → AddRoundKey` round.

For the fixed test vector

$$
m=\texttt{0x26B7},
\qquad
K=\texttt{0x3A94D63F},
$$

we obtain

$$
\boxed{E_K(m)=\texttt{0xBCD6}}.
$$

The implementation now makes all inverse operations explicit, removes dependence on global S-box state, separates block size from S-box width, validates substitution and permutation tables, and provides both known-answer and exhaustive round-trip tests.

More importantly, we now have a stable experimental object for the rest of the symmetric-cryptography series.

The next natural questions are no longer merely “how does the cipher encrypt?” They are:

- how good is the S-box against differences?
- how strong are its linear approximations?
- how many S-boxes become active across rounds?
- how do differential and linear trails propagate through the P-layer?
- how much security do additional rounds buy?
- what changes when we replace a bit permutation with a stronger linear diffusion matrix?

Those questions take us from **construction** into **cryptanalysis and design criteria**.

---

## 23. References and Further Reading

1. C. E. Shannon, “Communication Theory of Secrecy Systems,” *Bell System Technical Journal*, vol. 28, no. 4, pp. 656–715, 1949. DOI: `10.1002/j.1538-7305.1949.tb00928.x`.

2. H. M. Heys, “A Tutorial on Linear and Differential Cryptanalysis,” *Cryptologia*, vol. 26, no. 3, pp. 189–221, 2002. DOI: `10.1080/0161-110291890885`.

3. H. M. Heys and S. E. Tavares, “The Design of Substitution-Permutation Networks Resistant to Differential and Linear Cryptanalysis,” *Proceedings of the 2nd ACM Conference on Computer and Communications Security*, pp. 148–155, 1994. DOI: `10.1145/191177.191206`.

4. H. M. Heys and S. E. Tavares, “Substitution-Permutation Networks Resistant to Differential and Linear Cryptanalysis,” *Journal of Cryptology*, vol. 9, no. 1, pp. 1–19, 1996. DOI: `10.1007/BF02254789`.

5. National Institute of Standards and Technology, *Advanced Encryption Standard (AES)*, FIPS PUB 197, 2001; editorial update 2023. DOI: `10.6028/NIST.FIPS.197`.

6. J. Daemen and V. Rijmen, *The Design of Rijndael: AES — The Advanced Encryption Standard*. Springer, 2002.
