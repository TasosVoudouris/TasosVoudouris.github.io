---
title: 'Linear Cryptanalysis of Block Ciphers: Matsui’s Algorithms'
description: A rigorous executable treatment of linear approximations, LAT/Walsh conventions,
  the piling-up lemma, Matsui Algorithms 1 and 2, and partial last-round subkey recovery
  on a teaching SPN.
pubDate: '2026-08-12'
updatedDate: '2026-09-12'
topics:
- Symmetric Cryptography
- Cryptanalysis
- Mathematical Foundations
tags:
- linear-cryptanalysis
- matsui
- lat
- walsh
- spn
- sbox
difficulty: Advanced
series: Symmetric Cryptography
seriesOrder: 6
sourcePath: experiments/cryptanalysis/matsui-linear
status: Validated
draft: false
---
> A rigorous, executable introduction to linear approximations, linear trails,
> Matsui's algorithms, and partial subkey recovery on a teaching SPN.

This chapter develops the original material from first principles and keeps its
progression: masks, S-box approximations, key addition, several rounds, the
piling-up lemma, Matsui's Algorithm 1, Matsui's Algorithm 2, and a 16-bit SPN.
All code used here is available in [`matsui1.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/matsui1.py), and its expected
results are checked by [`test.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/test.py).

The examples are intentionally tiny. They make exhaustive checking possible,
but they are **not** evidence that a modern, correctly designed block cipher can
be attacked with the same small amount of work.

## Contents

1. [Scope and attack model](#1-scope-and-attack-model)
2. [Notation and bit conventions](#2-notation-and-bit-conventions)
3. [Linear and affine Boolean functions](#3-linear-and-affine-boolean-functions)
4. [Masks and binary inner products](#4-masks-and-binary-inner-products)
5. [Approximating an S-box](#5-approximating-an-s-box)
6. [The LAT, Walsh coefficients, bias, and correlation](#6-the-lat-walsh-coefficients-bias-and-correlation)
7. [Adding key material](#7-adding-key-material)
8. [Moving masks through an SPN](#8-moving-masks-through-an-spn)
9. [Chaining approximations and the piling-up lemma](#9-chaining-approximations-and-the-piling-up-lemma)
10. [Linear trails and linear hulls](#10-linear-trails-and-linear-hulls)
11. [Matsui's Algorithm 1](#11-matsuis-algorithm-1)
12. [Matsui's Algorithm 2](#12-matsuis-algorithm-2)
13. [Partial last-round subkey recovery on a 16-bit SPN](#13-partial-last-round-subkey-recovery-on-a-16-bit-spn)
14. [Complexity and experimental discipline](#14-complexity-and-experimental-discipline)
15. [What the attack does and does not recover](#15-what-the-attack-does-and-does-not-recover)
16. [Design resistance and advanced directions](#16-design-resistance-and-advanced-directions)
17. [Reproducing the results](#17-reproducing-the-results)
18. [References](#18-references)

---

## 1. Scope and attack model

Linear cryptanalysis was introduced by Mitsuru Matsui as a statistical attack
on block ciphers. The classic setting is a **known-plaintext attack**: the
attacker knows many plaintext-ciphertext pairs produced under one fixed secret
key and knows the cipher design, but not the key.

The high-level strategy is:

1. approximate nonlinear parts of the cipher with Boolean linear expressions;
2. connect compatible approximations across rounds;
3. obtain a relation involving selected plaintext, ciphertext, and key bits;
4. detect a small deviation from random behaviour; and
5. use that deviation either to infer a key parity or to rank subkey guesses.

For masks $\alpha$, $\beta$, and $\kappa$, the target relation has the form

$$
\alpha \cdot M \oplus \beta \cdot C \oplus \kappa \cdot K = 0
$$

with probability

$$
\Pr[\alpha \cdot M \oplus \beta \cdot C \oplus \kappa \cdot K = 0]
= \frac{1}{2} + \epsilon,
$$

where $\epsilon \ne 0$ is the **bias**. If the probability were exactly
$1/2$, this particular statistic would not distinguish the cipher from a
random permutation or reveal the targeted key relation.

### Important boundaries

- The attack is statistical; one plaintext-ciphertext pair does not establish a
  key relation.
- The secret key is fixed while data is collected.
- The approximations depend on the exact S-boxes, linear layer, round structure,
  and key schedule.
- A reduced teaching cipher is not a substitute for analysis of AES, PRESENT,
  DES, or another real design.
- Linear cryptanalysis is not limited to SPNs, but the examples here use SPNs
  because their mask propagation is easy to see.

---

## 2. Notation and bit conventions

| Symbol | Meaning |
|---|---|
| $M$, $C$ | plaintext and ciphertext |
| $K$, $K_r$ | master key and round key |
| $X$, $Y$ | input and output of a component |
| $S$ | S-box |
| $L$ or $P$ | linear or bit-permutation layer |
| $\alpha$, $\beta$, $\gamma$ | input, output, or intermediate masks |
| $\oplus$ | XOR, addition in $\mathrm{GF}(2)$ |
| $\alpha \cdot X$ | binary inner product |
| $p$ | probability that an approximation equals zero |
| $\epsilon=p-1/2$ | bias |
| $C=2\epsilon$ | normalized correlation |
| $W$ | Walsh coefficient |

### Bit numbering

This project uses **zero-based, most-significant-bit-first** positions in prose
and P-box functions. For a 4-bit word

$$
x=x_1x_2x_3x_4,
$$

the code positions are `0, 1, 2, 3`; position `0` is $x_1$, the most
significant bit. Integer masks retain their normal hexadecimal meaning. Thus
`0b1001` selects $x_1$ and $x_4$.

```python
from matsui1 import get_bit_msb

x = 0b01010
assert [get_bit_msb(x, i, 5) for i in range(5)] == [0, 1, 0, 1, 0]
```

Stating the convention matters. A trail copied from a paper that numbers bits
least-significant first can be wrong even when its hexadecimal masks appear
plausible.

---

## 3. Linear and affine Boolean functions

A map $f:\mathrm{GF}(2)^n\rightarrow\mathrm{GF}(2)$ is **linear** when

$$
f(x \oplus y)=f(x)\oplus f(y)
$$

for every $x,y$. Every Boolean linear function can be written as

$$
f(x)=a\cdot x
$$

for a fixed mask $a$. An **affine** Boolean function additionally permits a
constant:

$$
f(x)=a\cdot x\oplus b,\qquad b\in\{0,1\}.
$$

The distinction is small but important: a nonzero constant makes a function
affine, not linear. In linear cryptanalysis, the sign of a correlation is
equivalent to whether the better affine approximation uses constant zero or
one.

### Why nonlinear components matter

XOR with a constant key and a fixed bit permutation are affine/linear over
$\mathrm{GF}(2)$ and can be followed exactly. In a conventional SPN, S-boxes
are the nonlinear components that must be approximated.

That statement is architecture-specific. In an ARX cipher, addition modulo
$2^n$ is nonlinear relative to bitwise XOR because of carries. Other designs
may contain nonlinear finite-field operations or data-dependent layers.

### A one-bit example: AND

For $f(x_1,x_2)=x_1\land x_2$, the approximation $f(x)\approx 0$ is correct on
three of four inputs. Its probability is $3/4$, bias is $1/4$, and correlation
is $1/2$. The function is still nonlinear; “approximation” means statistically
related, not equal on every input.

---

## 4. Masks and binary inner products

For two $n$-bit values $x$ and $\alpha$, define

$$
\alpha\cdot x
=\bigoplus_{i=0}^{n-1}\alpha_i x_i
=\operatorname{parity}(\alpha\mathbin{\&}x).
$$

A `1` in a mask selects a bit; a `0` ignores it.

```python
from matsui1 import bit_parity, dot

assert bit_parity(0b1011) == 1
assert dot(0b1011, 0b1001) == 0  # 1 XOR 1
assert dot(0b1101, 0b1100) == 0  # 1 XOR 1
```

For the diagram below, $\alpha=1001_2$ and $\beta=0001_2$, so

$$
\alpha\cdot X=x_1\oplus x_4,
\qquad
\beta\cdot S(X)=y_4.
$$

![A masked S-box approximation](/images/cryptanalysis/matsui/linearapprox.png)

The approximation is therefore

$$
x_1\oplus x_4 = y_4.
$$

It need not hold for every input. The useful quantity is how far its success
probability is from $1/2$.

---

## 5. Approximating an S-box

Let $S:\mathrm{GF}(2)^n\rightarrow\mathrm{GF}(2)^m$. For masks $\alpha$ and
$\beta$, study the Boolean expression

$$
Z_{\alpha,\beta}(x)=\alpha\cdot x\oplus\beta\cdot S(x).
$$

The approximation “holds” when $Z_{\alpha,\beta}(x)=0$. Exhaustive evaluation
is practical for the small S-boxes used in block ciphers.

```python
from matsui1 import count_matches

def probability(alpha, beta, sbox, width):
    return count_matches(alpha, beta, sbox, width) / (1 << width)
```

For the PRESENT 4-bit S-box

```python
S = [12, 5, 6, 11, 9, 0, 10, 13,
     3, 14, 15, 8, 4, 7, 1, 2]
```

the masks $\alpha=9$ and $\beta=1$ match on 12 of 16 inputs:

$$
p=\frac{12}{16}=\frac34,
\quad
\epsilon=\frac14,
\quad
C=\frac12.
$$

For $\alpha=1$ and $\beta=5$, only 4 of 16 inputs match:

$$
p=\frac{4}{16}=\frac14,
\quad
\epsilon=-\frac14,
\quad
C=-\frac12.
$$

A negative bias is just as useful as a positive bias. It says the complementary
affine equation holds more often. The sign must be retained when trails are
combined or a parity is inferred.

---

## 6. The LAT, Walsh coefficients, bias, and correlation

Different books store different quantities in a “linear approximation table.”
This project uses **centered match counts**:

$$
\operatorname{LAT}[\alpha,\beta]
=\#\{x:\alpha\cdot x=\beta\cdot S(x)\}-2^{n-1}.
$$

For an $n$-bit S-box, the related conventions are:

| Quantity | Definition from the centered LAT entry $B$ |
|---|---:|
| matches | $2^{n-1}+B$ |
| probability | $p=1/2+B/2^n$ |
| bias | $\epsilon=B/2^n$ |
| Walsh coefficient | $W=2B$ |
| normalized correlation | $C=W/2^n=B/2^{n-1}=2\epsilon$ |

This conversion table prevents a common factor-of-two error. A paper may print
Walsh coefficients where this code prints centered biases.

```python
from matsui1 import PRESENT_SBOX, linear_approximation_table

lat = linear_approximation_table(PRESENT_SBOX, 4)
assert lat[9][1] == 4
assert lat[1][5] == -4
```

The complete implementation is deliberately direct:

```python
def linear_approximation_table(sbox, width):
    size = 1 << width
    center = size // 2
    return [
        [count_matches(a, b, sbox, width) - center
         for b in range(size)]
        for a in range(size)
    ]
```

### Trivial and zero-mask entries

- $(\alpha,\beta)=(0,0)$ is trivial and always matches. Its centered entry is
  $2^{n-1}$.
- For a bijective S-box, `LAT[0][beta]` is zero for every nonzero `beta`.
- `LAT[alpha][0]` is zero for every nonzero `alpha`.
- A zero entry means this exact component approximation has probability $1/2$;
  it does not prove that the whole cipher is secure.

### S-box linearity and nonlinearity

For a vectorial $n\times n$ S-box, one common definition is

$$
\operatorname{Lin}(S)=
\max_{(\alpha,\beta)\ne(0,0)}|W_S(\alpha,\beta)|.
$$

Its vectorial nonlinearity is

$$
\operatorname{NL}(S)=2^{n-1}-\frac{\operatorname{Lin}(S)}{2}.
$$

Lower maximum absolute correlation, equivalently higher nonlinearity, is one
component of resistance to linear cryptanalysis. It is not sufficient alone;
the diffusion layer and the number of active S-boxes also matter.

![A second 4-bit S-box example](/images/cryptanalysis/matsui/lat2.png)

For the second S-box in that figure, the centered LAT contains
`LAT[9][2] = -6` and `LAT[D][D] = -6`. These mean

$$
p=\frac{2}{16}=\frac18,
\quad \epsilon=-\frac38,
\quad C=-\frac34.
$$

---

## 7. Adding key material

Suppose one keyed S-box layer is

$$
Y=S(X\oplus K).
$$

Set $U=X\oplus K$. If the keyless approximation

$$
\alpha\cdot U\oplus\beta\cdot S(U)=0
$$

holds with probability $1/2+\epsilon$, then linearity of XOR gives

$$
\alpha\cdot X\oplus\beta\cdot Y
=\alpha\cdot K
$$

with that same probability. The input mask is also the mask on this AddKey:
$\kappa=\alpha$.

![Key addition before an S-box](/images/cryptanalysis/matsui/addkey.png)

For $\alpha=1001_2$ and $\beta=0001_2$,

$$
x_1\oplus x_4\oplus y_4=k_1\oplus k_4.
$$

The equation can return `False` on an individual input because it is a
statistical approximation. Across the complete 4-bit input space, the exact
frequency equals the corresponding LAT-derived probability.

### Keys change signs, not magnitudes

XOR with fixed key material contributes a fixed parity. It may complement the
Boolean relation and therefore flip the correlation sign, but it does not
change the absolute correlation of that fixed trail. Across many trails in a
linear hull, different key-dependent signs can reinforce or cancel, so the
hull magnitude itself may depend on the key.

---

## 8. Moving masks through an SPN

An SPN alternates key addition, nonlinear substitution, and linear diffusion.
Masks move differently through these layers.

### AddKey

If $Y=X\oplus K$, then

$$
\beta\cdot Y=\beta\cdot X\oplus\beta\cdot K.
$$

The state mask is unchanged; a key-parity term is introduced.

### S-box layer

An input mask and output mask are connected statistically through an LAT entry.
Parallel S-box correlations multiply only under the usual independence model.

### Linear layer

Let $Y=L(X)$ for a binary linear map $L$. Then

$$
\beta\cdot Y=\beta\cdot L(X)=(L^T\beta)\cdot X.
$$

Therefore the mask propagated backward through the layer is $L^T\beta$.
Depending on whether a source defines masks as row or column vectors, the same
rule may be written using an inverse transpose. The safe method is to verify

$$
\operatorname{dot}(L(x),\beta)
=\operatorname{dot}(x,\alpha)
$$

for all $x$ or for a basis of $x$ values.

```python
from matsui1 import dot, permute, propagate_mask_backwards

input_mask = propagate_mask_backwards(output_mask, pbox)
assert all(
    dot(permute(x, pbox, 16), output_mask) == dot(x, input_mask)
    for x in range(1 << 16)
)
```

The intermediate mask after one S-box is **not automatically** the input mask
of the next S-box when a diffusion layer lies between them. It must first be
transported through that layer.

---

## 9. Chaining approximations and the piling-up lemma

Consider two compatible Boolean expressions $Z_1$ and $Z_2$ with biases
$\epsilon_1$ and $\epsilon_2$. If they are independent, their XOR is zero when
both expressions agree: both are zero or both are one. Thus

$$
\Pr[Z_1\oplus Z_2=0]
=p_1p_2+(1-p_1)(1-p_2)
=\frac12+2\epsilon_1\epsilon_2.
$$

For $r$ independent expressions, the **piling-up lemma** gives

$$
\epsilon_{\text{total}}
=2^{r-1}\prod_{i=1}^{r}\epsilon_i.
$$

Because $C_i=2\epsilon_i$, the correlation form is simpler:

$$
C_{\text{total}}=\prod_{i=1}^{r}C_i,
\qquad
\epsilon_{\text{total}}=\frac{C_{\text{total}}}{2}.
$$

```python
from matsui1 import piling_up_bias

assert piling_up_bias([0.25, -0.25]) == -0.125
```

Here $p_1=3/4$ and $p_2=1/4$, so the combined probability is
$1/2-1/8=3/8$.

![Two chained S-box approximations](/images/cryptanalysis/matsui/moresbox.png)

### Independence is an assumption

Piling up local biases is a model for a selected trail. Internal variables in a
real cipher are not automatically independent. Shared variables, overlapping
S-box inputs, the key schedule, and multiple trails with the same endpoints can
make the observed correlation differ from the single-trail estimate. Exact
enumeration on reduced ciphers and experiments across several keys are valuable
checks.

---

## 10. Linear trails and linear hulls

These terms should not be used interchangeably.

### Linear trail

A **linear trail** (or linear characteristic) fixes every intermediate mask.
Its estimated correlation is the signed product of the active component
correlations, with masks transported exactly through linear layers.

### Linear hull

A **linear hull** fixes only the external input and output masks. All compatible
trails between those endpoints contribute. For a fixed key $K$,

$$
C_K(\alpha,\beta)
=\sum_{\tau:\alpha\leadsto\beta} C_K(\tau).
$$

This is a signed sum, not a sum of magnitudes. Trails may cancel or reinforce.
The phenomenon is the **linear hull effect**. A locally best trail is therefore
not always the best overall distinguisher.

### Practical trail-search checklist

1. compute and label the LAT convention;
2. exclude the trivial zero-mask relation when ranking entries;
3. retain signs as well as magnitudes;
4. propagate masks through every linear layer using its exact transpose rule;
5. count active S-boxes and multiply their correlations for a trail estimate;
6. search other trails with the same endpoints; and
7. validate selected approximations by exact enumeration when the block size
   permits it, or by reproducible experiments over several independent keys.

---

## 11. Matsui's Algorithm 1

Algorithm 1 uses a whole-cipher approximation to recover **one parity of key
bits**. Suppose

$$
\alpha\cdot M\oplus\beta\cdot C
=\kappa\cdot K
$$

with a known nonzero correlation sign.

For each known pair, compute

$$
q_i=\alpha\cdot M_i\oplus\beta\cdot C_i.
$$

Let $T_0$ count $q_i=0$ and $T_1$ count $q_i=1$.

- If the keyless correlation is positive, the majority value estimates
  $\kappa\cdot K$.
- If it is negative, complement the majority value.
- If $T_0=T_1$, the current data gives no preference.

```python
from matsui1 import matsui1_details

result = matsui1_details(
    messages,
    ciphertexts,
    alpha,
    beta,
    correlation_sign=+1,
)
print(result.key_parity, result.t0, result.t1)
```

### Complete 4-bit demonstration

For `PRESENT_SBOX`, `alpha = 0x9`, and `beta = 0x1`, the keyless bias is
positive. With a fixed key and all 16 distinct plaintexts:

```python
from matsui1 import PRESENT_SBOX, dot, matsui1_details

key = 0xA
messages = list(range(16))
ciphertexts = [PRESENT_SBOX[m ^ key] for m in messages]

result = matsui1_details(messages, ciphertexts, 0x9, 0x1, +1)
assert result.key_parity == dot(key, 0x9)
```

The result is one linear combination of key bits, not the complete key.
Independent approximations can provide additional equations.

![A two-S-box cipher used to illustrate Algorithm 1](/images/cryptanalysis/matsui/matsui1example.png)

For the second S-box, `LAT[D][D] = -6`. Chaining the same approximation over
two S-boxes gives a positive estimated correlation because two negative signs
multiply. Key parities from every crossed AddKey must be included.

---

## 12. Matsui's Algorithm 2

Algorithm 2 does not require a useful approximation to cross the final round.
Instead it guesses selected outer-round key bits, partially encrypts or decrypts
the data, and tests an approximation covering the remaining rounds.

Suppose the approximation ends at an internal value $U$ immediately before a
final S-box and final whitening key:

$$
C=S(U)\oplus K_f.
$$

For each candidate $k$:

1. partially decrypt $U_k=S^{-1}(C\oplus k)$;
2. compute $q_i(k)=\alpha\cdot M_i\oplus\beta\cdot U_{k,i}$;
3. count $T_0(k)$ and $T_1(k)$; and
4. score $D(k)=T_0(k)-T_1(k)$.

The default ranking statistic is

$$
|D(k)|=|T_0(k)-T_1(k)|,
$$

not merely `D(k)`. An unknown key parity or negative trail correlation can flip
the sign without destroying the signal.

![Matsui Algorithm 2: guess an outer-round subkey and expose an internal state](/images/cryptanalysis/matsui/matsui2.png)

![A three-S-box toy cipher for Algorithm 2](/images/cryptanalysis/matsui/matsui2example.png)

```python
from matsui1 import inverse_sbox, matsui2, rank_key_guesses

scores = matsui2(messages, ciphertexts, alpha, beta, inverse_sbox(sbox))
ranking = rank_key_guesses(scores)  # descending abs(T0 - T1)
print(ranking[:5])
```

### Wrong-key randomization is an approximation

The common heuristic says wrong subkey guesses produce nearly random internal
values, while the correct guess preserves the selected correlation. On a tiny
4-bit permutation, the full codebook contains only 16 distinct plaintexts and
several guesses can form equivalent or strongly correlated classes. Therefore
the small example demonstrates scoring and ranking; it must not claim unique
key recovery.

Repeating a known 4-bit pair does not create new evidence. For a fixed key, use
the 16 distinct pairs. If a Monte Carlo experiment varies keys, say so
explicitly and aggregate separate experiments rather than pretending repeated
tiny-domain samples are independent data.

---

## 13. Partial last-round subkey recovery on a 16-bit SPN

The larger example uses a four-round, 16-bit SPN with four parallel 4-bit
S-boxes per layer:

- rounds 1–3: AddKey, S-box layer, P-box;
- round 4: AddKey, S-box layer;
- final whitening AddKey;
- a 32-bit master key expanded into five overlapping 16-bit round keys.

```python
from matsui1 import SPN, TOY_SPN_PBOX, TOY_SPN_SBOX

cipher = SPN(TOY_SPN_SBOX, TOY_SPN_PBOX)
```

The P-box is

```text
[0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
```

with the convention that output position `i` receives input position
`pbox[i]`. The implementation computes and uses the inverse P-box during
decryption; assuming that every P-box is self-inverse would be a bug.

### The selected three-round trail

We approximate the first three rounds from plaintext mask `0x0B00` to the input
of the final S-box layer with mask `0x0505`.

| Round | S input | S output | After P | Transitions | $C$ |
|---:|---:|---:|---:|---|---:|
| 1 | `0x0B00` | `0x0400` | `0x0400` | `B -> 4` | $+1/2$ |
| 2 | `0x0400` | `0x0500` | `0x0404` | `4 -> 5` | $-1/2$ |
| 3 | `0x0404` | `0x0505` | `0x0505` | two copies of `4 -> 5` | $(-1/2)^2=+1/4$ |

The four active S-box correlations multiply to

$$
C_{\text{trail}}
=\left(\frac12\right)
 \left(-\frac12\right)
 \left(-\frac12\right)^2
=-\frac1{16}.
$$

Hence the trail bias estimate is

$$
\epsilon_{\text{trail}}=\frac{C_{\text{trail}}}{2}=-\frac1{32}.
$$

The heuristic scale $1/\epsilon^2$ is $1024$ pairs, but a reliable key-ranking
experiment can require a larger constant because 256 candidates are compared,
wrong candidates are not perfectly independent, a hull may be present, and a
specific success probability is desired.

### Which key bits are guessed?

The endpoint mask `0x0505` activates the second and fourth 4-bit S-boxes of the
last layer. Consequently Algorithm 2 guesses the corresponding nibbles of the
final whitening key: shifts 8 and 0.

For master key `0x3A94D63F`, the round keys are

```text
3A94, A94D, 94D6, 4D63, D63F
```

and the two attacked final-key nibbles are `6` and `F`, packed as candidate
`0x6F`. They are not the contiguous byte `(master_key >> 8) & 0xFF`.

### Reproducible attack

```python
from random import Random
from matsui1 import (
    SPN,
    TOY_SPN_PBOX,
    TOY_SPN_SBOX,
    extract_round_key_nibbles,
    matsui2_spn,
    rank_key_guesses,
)

cipher = SPN(TOY_SPN_SBOX, TOY_SPN_PBOX)
master_key = 0x3A94D63F

# Distinct known plaintexts sampled without replacement.
rng = Random(0xC0DEC0DE)
messages = rng.sample(range(1 << 16), 8_192)
ciphertexts = [cipher.encrypt(m, master_key) for m in messages]

scores = matsui2_spn(
    messages,
    ciphertexts,
    alpha=0x0B00,
    beta=0x0505,
    sbox_inverse=cipher.sbox_inv,
    nibble_shifts=(8, 0),
)
ranking = rank_key_guesses(scores)

actual = extract_round_key_nibbles(
    cipher.key_schedule(master_key)[-1],
    (8, 0),
)

assert actual == 0x6F
assert ranking[0] == actual
```

This example performs $256\times8192$ partial decryptions. The fixed seed makes
the result reproducible; it is not meant to conceal the experimental choices.

---

## 14. Complexity and experimental discipline

### Data complexity

For a fixed nonzero bias, statistical detection generally has order

$$
N=\Theta(\epsilon^{-2})=\Theta(C^{-2}).
$$

Writing $N=1/\epsilon^2$ is only a heuristic scale. The constant depends on:

- desired success probability;
- whether bias $\epsilon$ or correlation $C=2\epsilon$ is used;
- the number of key candidates;
- the score and threshold;
- signal-to-noise assumptions;
- dependence between approximations; and
- the advantage assigned to the attacker.

### Time and memory

If $k$ subkey bits are guessed and $N$ pairs are processed, the direct
Algorithm 2 loop costs approximately

$$
O(2^kN)
$$

partial operations. The basic counter implementation uses $O(2^k)$ scores.
Partial-sum and FFT techniques can reduce time for structured attacks, but add
implementation and memory complexity.

### Reliable experiments

1. keep the secret key fixed within one attack;
2. avoid counting duplicate tiny-domain pairs as fresh evidence;
3. sample without replacement when enough distinct plaintexts exist;
4. use deterministic seeds for regression tests;
5. repeat performance studies over many independent keys and seeds;
6. report the true-key rank, not only whether it was first;
7. compare signed and absolute scores deliberately;
8. validate encryption/decryption round trips;
9. verify selected LAT entries independently; and
10. state the LAT, bit-ordering, P-box, and key-schedule conventions.

---

## 15. What the attack does and does not recover

The SPN example recovers **eight selected bits of the final whitening key**. It
does not directly recover the full 16-bit final round key or the 32-bit master
key.

To move toward complete master-key recovery, an analyst can:

1. select additional approximations activating other final-round S-boxes;
2. obtain and combine rankings for more subkey nibbles;
3. account for dependencies when combining statistics;
4. use the key schedule to map recovered round-key constraints to the master
   key;
5. enumerate remaining master-key candidates; and
6. verify each surviving candidate against independent known pairs.

Algorithm 1 similarly gives one key parity per useful independent equation.
Several parity equations can be solved as a linear system, but only up to their
rank; remaining key entropy still requires other analysis or search.

---

## 16. Design resistance and advanced directions

### Defensive design principles

A cipher resists basic linear cryptanalysis by combining:

- S-boxes with low maximum absolute correlation;
- diffusion that forces many active S-boxes across several rounds;
- enough rounds that useful correlations decay below exploitable levels;
- a key schedule that avoids damaging relations and symmetries;
- analysis of hulls, not only individual trails; and
- conservative security margins supported by automated trail searches and
  independent cryptanalysis.

More active S-boxes usually make the product of component correlations approach
zero in magnitude. Saying the distribution “becomes less uniform” would reverse
the intended security intuition: a secure design aims to make externally
visible linear relations closer to uniform.

### Beyond a single approximation

- **Multiple linear cryptanalysis** combines several approximations to improve
  key ranking.
- **Multidimensional linear cryptanalysis** studies the joint distribution of a
  vector space of approximations rather than treating each independently.
- **Linear-hull analysis** sums all compatible trail correlations for fixed
  endpoints and accounts for key-dependent signs.
- **Zero-correlation linear cryptanalysis** exploits structural approximations
  whose correlation is exactly zero over all keys for a specified number of
  rounds; deviations after guessed outer rounds can rank keys.
- **Partial-sum and FFT attacks** reorganize candidate evaluation to reduce time.

These methods require more careful statistical models than the single-counter
examples in this chapter, but they grow from the same masks, correlations, and
partial-decryption ideas.

---

## 17. Reproducing the results

Python 3.10 or newer is sufficient; the project uses only the standard library.

```bash
python matsui1.py
python -m unittest -v test.py
```

Expected checkpoints include:

- `PRESENT_SBOX`: `LAT[9][1] = 4` and `LAT[1][5] = -4`;
- second S-box: `LAT[9][2] = -6` and `LAT[D][D] = -6`;
- two biases `+0.25` and `-0.25` pile up to `-0.125`;
- the SPN encrypt/decrypt tests round-trip;
- the selected trail has correlation `-1/16` and bias `-1/32`; and
- the deterministic SPN attack ranks packed subkey `0x6F` first.

The notebook [`Linear Cryptanalysis.ipynb`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/Linear%20Cryptanalysis.ipynb)
provides a shorter interactive route through the same checked implementation.

---

## 18. References

The accompanying [`references.bib`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/references.bib) contains machine-readable
BibTeX entries.

1. M. Matsui, “Linear Cryptanalysis Method for DES Cipher,” *Advances in
   Cryptology—EUROCRYPT '93*, LNCS 765, pp. 386–397, 1994.
   <https://doi.org/10.1007/3-540-48285-7_33>
2. M. Matsui, “The First Experimental Cryptanalysis of the Data Encryption
   Standard,” *Advances in Cryptology—CRYPTO '94*, LNCS 839, pp. 1–11, 1994.
   <https://doi.org/10.1007/3-540-48658-5_1>
3. K. Nyberg, “Linear Approximation of Block Ciphers,” *Advances in
   Cryptology—EUROCRYPT '94*, LNCS 950, pp. 439–444, 1995.
   <https://doi.org/10.1007/BFb0053460>
4. E. Biham, “On Matsui's Linear Cryptanalysis,” *Advances in
   Cryptology—EUROCRYPT '94*, LNCS 950, pp. 341–355, 1995.
   <https://doi.org/10.1007/BFb0053449>
5. B. S. Kaliski Jr. and M. J. B. Robshaw, “Linear Cryptanalysis Using Multiple
   Approximations,” *Advances in Cryptology—CRYPTO '94*, LNCS 839, 1994.
   <https://doi.org/10.1007/3-540-48658-5_4>
6. J. Y. Cho, M. Hermelin, and K. Nyberg, “A New Technique for Multidimensional
   Linear Cryptanalysis with Applications on Reduced Round Serpent,” ICISC
   2008, LNCS 5461, pp. 383–398, 2009.
   <https://doi.org/10.1007/978-3-642-00730-9_24>
7. A. Bogdanov and V. Rijmen, “Linear Hulls with Correlation Zero and Linear
   Cryptanalysis of Block Ciphers,” *Designs, Codes and Cryptography*, vol. 70,
   pp. 369–383, 2014.
   <https://doi.org/10.1007/s10623-012-9697-z>

---

### Ethical use

Use these techniques only on systems and data you own or are explicitly
authorized to test. The code is designed for education and reduced ciphers.
