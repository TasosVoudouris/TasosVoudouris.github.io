---
title: "Linear Cryptanalysis of Block Ciphers: Matsui’s Algorithms"
description: "A rigorous executable treatment of linear approximations, LAT and Walsh conventions, mask propagation, the piling-up lemma, Matsui Algorithms 1 and 2, and partial last-round subkey recovery on a teaching SPN."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Cryptanalysis"
  - "Mathematical Foundations"
tags:
  - "linear-cryptanalysis"
  - "matsui"
  - "lat"
  - "walsh"
  - "spn"
  - "sbox"
  - "linear-hulls"
difficulty: "Advanced"
series: "Symmetric Cryptography"
seriesOrder: 6
sourcePath: "experiments/cryptanalysis/matsui-linear"
status: "Validated"
draft: false
---

> A rigorous, executable introduction to linear approximations, linear trails,
> Matsui's algorithms, and partial subkey recovery on a teaching SPN.

This is the final article in the **Symmetric Cryptography** series. The previous parts built block ciphers from the design side: first a toy SPN, then DES and the Feistel structure, AES, classical modes of operation, and finally authenticated encryption and AEAD. We now turn the perspective around.

Instead of asking:

> How should a cipher be constructed?

we ask:

> What statistical structure would a cryptanalyst try to exploit, and how do modern designs suppress that structure?

Linear cryptanalysis is one of the clearest ways to answer that question. It connects Boolean functions, S-box design, Walsh spectra, diffusion, key addition, probability, statistical hypothesis testing, and partial key recovery in one coherent framework.

The examples are intentionally small. That is a feature, not a weakness: on a 4-bit S-box or a 16-bit teaching SPN we can exhaustively verify every claim, reproduce every table, and inspect the exact signal used by the attack. The same experiment is **not** evidence that AES or another modern full-round cipher can be attacked with comparable effort.

The companion implementation is available in [`matsui1.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/matsui1.py), with regression checks in [`test.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/test.py).

## Table of Contents

- [Foundations and Attack Model](#foundations-and-attack-model)
- [S-box Approximations and Linear Statistics](#s-box-approximations-and-linear-statistics)
- [\beta\cdot S(x)
}](#betacdot-sx)
- [2^${n-1}](#2n-1)
- [From Local Relations to Multi-Round Trails](#from-local-relations-to-multi-round-trails)
- [Matsui’s Algorithms](#matsuis-algorithms)
- [End-to-End Partial Subkey Recovery](#end-to-end-partial-subkey-recovery)
- [Complexity, Resistance, and Reproducibility](#complexity-resistance-and-reproducibility)
- [Series Synthesis and Conclusion](#series-synthesis-and-conclusion)
- [References](#references)

---

## Foundations and Attack Model

Linear cryptanalysis was introduced by Mitsuru Matsui as a statistical cryptanalytic method for block ciphers. In its classical form the attacker works in a **known-plaintext setting**: many plaintext-ciphertext pairs are available under one fixed unknown secret key, and the cipher design is public.

The attack does not attempt to replace the cipher by an exact linear function. Instead, it searches for Boolean linear or affine relations that hold with probability measurably different from one half.

For masks \(\alpha\), \(\beta\), and a key mask \(\kappa\), a useful whole-cipher relation may have the form

\[
\alpha\cdot M
\oplus
\beta\cdot C
\oplus
\kappa\cdot K
=
0
\]

with probability

\[
\Pr[
\alpha\cdot M
\oplus
\beta\cdot C
\oplus
\kappa\cdot K
=
0
]
=
\frac12+\epsilon,
\]

where

\[
\epsilon\neq 0
\]

is the **bias**.

If the probability were exactly \(1/2\), that particular relation would look balanced and would provide no statistical preference for either parity value.

The high-level attack logic is therefore:

1. find useful approximations for nonlinear components;
2. propagate masks correctly through linear components;
3. combine compatible approximations across rounds;
4. obtain an observable relation involving plaintext, ciphertext, and selected key bits;
5. collect enough data to measure the bias;
6. infer a key parity or rank subkey candidates.

The attack is statistical. One pair proves essentially nothing. The key is kept fixed while data is collected, and the exact approximation depends on the actual S-boxes, diffusion layer, round order, and key schedule.

### Linear and affine Boolean functions

A Boolean map

\[
f:\mathrm{GF}(2)^n\rightarrow \mathrm{GF}(2)
\]

is linear when

\[
f(x\oplus y)=f(x)\oplus f(y)
\]

for every \(x,y\).

Every such function can be written as

\[
f(x)=a\cdot x,
\]

where \(a\) is a fixed bit mask.

An affine Boolean function permits one additional constant:

\[
f(x)=a\cdot x\oplus b,
\qquad
b\in\{0,1\}.
\]

This small distinction matters in linear cryptanalysis. A negative correlation often means that the complementary affine equation is the one that holds more frequently.

For example, the nonlinear Boolean function

\[
f(x_1,x_2)=x_1\land x_2
\]

equals zero on three of four inputs. Thus the approximation

\[
f(x_1,x_2)\approx 0
\]

has

\[
p=\frac34,
\qquad
\epsilon=\frac14,
\qquad
C=2\epsilon=\frac12.
\]

The function is still nonlinear. "Linear approximation" means statistical correlation, not equality on every input.

### Masks and binary inner products

For two \(n\)-bit values \(x\) and \(\alpha\),

\[
\alpha\cdot x
=
\bigoplus_{i=0}^{n-1}\alpha_i x_i
=
\operatorname{parity}(\alpha\mathbin{\&}x).
\]

A `1` in the mask selects a bit. A `0` ignores it.

```python
def bit_parity(x: int) -> int:
    return x.bit_count() & 1

def dot(x: int, mask: int) -> int:
    return bit_parity(x & mask)

assert bit_parity(0b1011) == 1
assert dot(0b1011, 0b1001) == 0
```

This article uses **zero-based, most-significant-bit-first** positions in prose and P-box helpers. For a 4-bit word

\[
x=x_1x_2x_3x_4,
\]

code position `0` denotes \(x_1\), the most significant bit.

Thus the hexadecimal mask

```text
0x9 = 1001₂
```

selects

\[
x_1\oplus x_4.
\]

Bit conventions must be stated explicitly. A trail copied from a paper using least-significant-bit-first numbering can become wrong even when the hexadecimal masks still look plausible.

For the following diagram, let

\[
\alpha=1001_2,
\qquad
\beta=0001_2.
\]

Then

\[
\alpha\cdot X=x_1\oplus x_4
\]

and

\[
\beta\cdot S(X)=y_4.
\]

![A masked S-box approximation](/images/cryptanalysis/matsui/linearapprox.png)

The candidate approximation is therefore

\[
x_1\oplus x_4=y_4.
\]

Its value is not determined by appearance. We must count how often it holds over the complete S-box domain.

---

## S-box Approximations and Linear Statistics

Let

\[
S:\mathrm{GF}(2)^n\rightarrow\mathrm{GF}(2)^m.
\]

For masks \(\alpha\) and \(\beta\), define

\[
Z_{\alpha,\beta}(x)
=
\alpha\cdot x
\oplus
\beta\cdot S(x).
\]

The approximation is satisfied when

\[
Z_{\alpha,\beta}(x)=0.
\]

For a small S-box this can be measured exhaustively:

```python
def count_matches(alpha, beta, sbox, width):
    return sum(
        dot(x, alpha) == dot(sbox[x], beta)
        for x in range(1 << width)
    )

def probability(alpha, beta, sbox, width):
    return count_matches(alpha, beta, sbox, width) / (1 << width)
```

Consider the PRESENT 4-bit S-box

```python
PRESENT_SBOX = [
    12, 5, 6, 11,
    9, 0, 10, 13,
    3, 14, 15, 8,
    4, 7, 1, 2,
]
```

For

\[
\alpha=9,
\qquad
\beta=1,
\]

the relation matches on 12 of 16 inputs:

\[
p=\frac{12}{16}=\frac34,
\]

\[
\epsilon
=
p-\frac12
=
\frac14,
\]

\[
C=2\epsilon=\frac12.
\]

For

\[
\alpha=1,
\qquad
\beta=5,
\]

it matches on only 4 of 16 inputs:

\[
p=\frac14,
\qquad
\epsilon=-\frac14,
\qquad
C=-\frac12.
\]

A negative correlation is not "bad" for the attacker. It is just a signal with the opposite sign.

### The Linear Approximation Table

Different books and programs use different LAT conventions. This article stores **centered match counts**:

\[
\operatorname{LAT}[\alpha,\beta]
=
\#\{
x:
\alpha\cdot x
=
\beta\cdot S(x)
\}
-
2^{n-1}.
\]

If we call the centered entry \(B\), then

\[
\text{matches}=2^{n-1}+B,
\]

\[
p=\frac12+\frac{B}{2^n},
\]

\[
\epsilon=\frac{B}{2^n},
\]

\[
W=2B,
\]

and

\[
C
=
\frac{W}{2^n}
=
\frac{B}{2^{n-1}}
=
2\epsilon.
\]

This conversion is worth keeping visible because factor-of-two errors are common when one source prints Walsh coefficients and another prints centered LAT values.

```python
def linear_approximation_table(sbox, width):
    size = 1 << width
    center = size // 2

    return [
        [
            count_matches(a, b, sbox, width) - center
            for b in range(size)
        ]
        for a in range(size)
    ]

lat = linear_approximation_table(PRESENT_SBOX, 4)

assert lat[0x9][0x1] == 4
assert lat[0x1][0x5] == -4
```

The trivial entry

\[
(\alpha,\beta)=(0,0)
\]

always matches and has centered value \(2^{n-1}\). It must be excluded when ranking useful approximations.

For a bijective \(n\times n\) S-box:

\[
\operatorname{LAT}[0,\beta]=0
\quad
\text{for }\beta\neq0,
\]

and

\[
\operatorname{LAT}[\alpha,0]=0
\quad
\text{for }\alpha\neq0.
\]

A zero LAT entry means that this exact component relation is balanced. It does **not** prove that the entire cipher is resistant to linear cryptanalysis.

### Walsh coefficients and S-box nonlinearity

A common vectorial linearity measure is

\[
\operatorname{Lin}(S)
=
\max_{(\alpha,\beta)\neq(0,0)}
|W_S(\alpha,\beta)|.
\]

One associated vectorial nonlinearity definition is

\[
\operatorname{NL}(S)
=
2^{n-1}
-
\frac{\operatorname{Lin}(S)}{2}.
\]

Lower maximum absolute correlation, or equivalently higher nonlinearity under this measure, is one ingredient in resistance to linear cryptanalysis.

It is not sufficient by itself.

A cipher also needs a diffusion layer that forces many S-boxes to become active across multiple rounds.

![A second 4-bit S-box example](/images/cryptanalysis/matsui/lat2.png)

The picture above is useful precisely because it visualizes a point that can get lost in the formulas: one S-box may contain many candidate approximations, with different signs and magnitudes. Cryptanalysis is not about finding "the linear approximation." It is about selecting and connecting statistically useful mask transitions under the exact structure of the cipher.

---

## From Local Relations to Multi-Round Trails

An S-box approximation becomes cryptanalytically useful only after we understand what happens when key addition and diffusion are inserted between S-box layers.

### Key addition

Suppose

\[
Y=S(X\oplus K).
\]

Define

\[
U=X\oplus K.
\]

If the keyless relation

\[
\alpha\cdot U
\oplus
\beta\cdot S(U)
=
0
\]

holds with probability \(1/2+\epsilon\), then

\[
\alpha\cdot X
\oplus
\beta\cdot Y
=
\alpha\cdot K
\]

holds with the same probability.

The AddRoundKey operation contributes a **fixed key parity**.

![Key addition before an S-box](/images/cryptanalysis/matsui/addkey.png)

For

\[
\alpha=1001_2,
\qquad
\beta=0001_2,
\]

the relation becomes

\[
x_1\oplus x_4\oplus y_4
=
k_1\oplus k_4.
\]

The key does not change the magnitude of the correlation for a fixed trail. It can change its sign by complementing the relevant Boolean relation.

This becomes more subtle for a **linear hull**, where several trails with key-dependent signs may reinforce or cancel.

### Propagating a mask through a linear layer

Let

\[
Y=L(X)
\]

for a binary linear map \(L\).

Then

\[
\beta\cdot Y
=
\beta\cdot L(X)
=
(L^T\beta)\cdot X.
\]

Therefore the corresponding input mask is obtained through the transpose relation.

Depending on whether a source uses row vectors, column vectors, forward masks, or backward masks, the formula may be written differently. The safest implementation check is not to memorize notation but to verify the invariant:

\[
\operatorname{dot}(L(x),\beta)
=
\operatorname{dot}(x,\alpha)
\]

for all \(x\), or at least over a basis.

```python
input_mask = propagate_mask_backwards(
    output_mask,
    pbox,
)

assert all(
    dot(
        permute(x, pbox, 16),
        output_mask,
    )
    ==
    dot(
        x,
        input_mask,
    )
    for x in range(1 << 16)
)
```

This point is crucial.

The output mask of one S-box layer is **not automatically** the input mask of the next S-box layer. The diffusion layer must transport it.

### Chaining approximations: the piling-up lemma

Suppose two compatible Boolean expressions \(Z_1\) and \(Z_2\) have biases

\[
\epsilon_1,
\qquad
\epsilon_2.
\]

If the relevant variables are independent, then

\[
\Pr[Z_1\oplus Z_2=0]
=
p_1p_2
+
(1-p_1)(1-p_2)
\]

and therefore

\[
\Pr[Z_1\oplus Z_2=0]
=
\frac12
+
2\epsilon_1\epsilon_2.
\]

For \(r\) independent expressions,

\[
\epsilon_{\text{total}}
=
2^{r-1}
\prod_{i=1}^{r}\epsilon_i.
\]

Since

\[
C_i=2\epsilon_i,
\]

the correlation form is cleaner:

\[
C_{\text{total}}
=
\prod_{i=1}^{r}C_i,
\]

\[
\epsilon_{\text{total}}
=
\frac{C_{\text{total}}}{2}.
\]

For example,

\[
\epsilon_1=+\frac14,
\qquad
\epsilon_2=-\frac14
\]

gives

\[
\epsilon_{\text{total}}
=
2
\left(\frac14\right)
\left(-\frac14\right)
=
-\frac18.
\]

Thus

\[
p
=
\frac12-\frac18
=
\frac38.
\]

![Two chained S-box approximations](/images/cryptanalysis/matsui/moresbox.png)

The independence assumption must not be hidden.

Internal variables in a real cipher may share dependencies. Trails can overlap, the key schedule may introduce structure, and many compatible trails may connect the same external masks. The piling-up lemma gives the correlation estimate for the modeled combination; exact reduced-cipher experiments are valuable precisely because they show when the model and measured behavior diverge.

### Linear trails and linear hulls

A **linear trail** fixes the intermediate masks through every round.

Its estimated correlation is the signed product of the active component correlations, with exact propagation through each linear layer.

A **linear hull** fixes only the external masks \((\alpha,\beta)\). Every compatible trail between those masks contributes.

For a fixed key \(K\),

\[
C_K(\alpha,\beta)
=
\sum_{\tau:\alpha\leadsto\beta}
C_K(\tau).
\]

This is a **signed sum**, not a sum of magnitudes.

Trails may cancel or reinforce.

The resulting **linear hull effect** explains why the locally strongest trail is not guaranteed to be the strongest externally observable approximation.

A disciplined search therefore needs to:

- define the LAT convention,
- retain signs,
- propagate every mask exactly,
- count active S-boxes,
- estimate trail correlations,
- search for other trails with the same endpoints,
- validate promising approximations empirically when feasible.

---

## Matsui’s Algorithms

Matsui's work turns linear approximations into concrete key information.

The two classical algorithms use the same statistical structure in different ways.

### Matsui Algorithm 1: recover a key parity

Suppose a whole-cipher approximation gives

\[
\alpha\cdot M
\oplus
\beta\cdot C
=
\kappa\cdot K
\]

with known nonzero correlation sign.

For every known plaintext-ciphertext pair, compute

\[
q_i
=
\alpha\cdot M_i
\oplus
\beta\cdot C_i.
\]

Let:

\[
T_0
=
\#\{i:q_i=0\},
\]

\[
T_1
=
\#\{i:q_i=1\}.
\]

If the keyless approximation has positive correlation, the majority value estimates

\[
\kappa\cdot K.
\]

If the correlation is negative, the interpretation is complemented.

Algorithm 1 therefore recovers **one parity relation on key bits**, not necessarily the complete key.

A minimal interface is:

```python
result = matsui1_details(
    messages,
    ciphertexts,
    alpha,
    beta,
    correlation_sign=+1,
)

print(
    result.key_parity,
    result.t0,
    result.t1,
)
```

For the PRESENT S-box example,

```python
key = 0xA
messages = list(range(16))
ciphertexts = [
    PRESENT_SBOX[m ^ key]
    for m in messages
]

result = matsui1_details(
    messages,
    ciphertexts,
    0x9,
    0x1,
    +1,
)

assert result.key_parity == dot(key, 0x9)
```

Because the entire 4-bit domain is available, this is an exact toy experiment rather than a noisy large-domain sample.

![A two-S-box cipher used to illustrate Algorithm 1](/images/cryptanalysis/matsui/matsui1example.png)

Several independent key-parity equations can be assembled into a linear system over

\[
\mathrm{GF}(2).
\]

The rank of that system determines how many independent key bits are constrained. Any remaining entropy still requires additional cryptanalysis or search.

### Matsui Algorithm 2: guess outer-round key bits

Algorithm 2 is often more directly useful for key ranking.

Instead of requiring an approximation to cross the final nonlinear layer, it stops at an internal state and guesses the last-round subkey bits needed to expose that state.

Suppose the final layer has the form

\[
C=S(U)\oplus K_f.
\]

For a candidate subkey \(k\),

\[
U_k
=
S^{-1}(C\oplus k).
\]

Then compute the candidate-dependent statistic

\[
q_i(k)
=
\alpha\cdot M_i
\oplus
\beta\cdot U_{k,i}.
\]

For each candidate define

\[
D(k)
=
T_0(k)-T_1(k).
\]

If the sign is not independently known for the guessed outer-key relation, a natural ranking statistic is

\[
|D(k)|.
\]

A correct guess should preserve the targeted correlation more strongly than typical wrong guesses.

![Matsui Algorithm 2: guess an outer-round subkey and expose an internal state](/images/cryptanalysis/matsui/matsui2.png)

![A three-S-box toy cipher for Algorithm 2](/images/cryptanalysis/matsui/matsui2example.png)

```python
scores = matsui2(
    messages,
    ciphertexts,
    alpha,
    beta,
    inverse_sbox(sbox),
)

ranking = rank_key_guesses(scores)

print(ranking[:5])
```

The usual phrase **wrong-key randomization** should be understood as a heuristic model, not a magical theorem saying that every wrong key produces exactly uniform statistics.

On a tiny 4-bit domain there are only 16 distinct plaintexts. Different subkey guesses can form equivalent or strongly correlated classes. Repeating the same known pair thousands of times does not create thousands of independent samples.

That is why the larger 16-bit experiment matters.

---

## End-to-End Partial Subkey Recovery

We now return to the teaching SPN introduced at the beginning of the series.

The cipher has:

- a 16-bit block,
- four parallel 4-bit S-boxes,
- three rounds of `AddKey -> S-box -> P-box`,
- one final `AddKey -> S-box`,
- a final whitening key,
- a 32-bit master key,
- five overlapping 16-bit round keys.

The S-box is

```python
TOY_SPN_SBOX = [
    14, 4, 13, 1,
    2, 15, 11, 8,
    3, 10, 6, 12,
    5, 9, 0, 7,
]
```

and the P-box is

```python
TOY_SPN_PBOX = [
    0, 4, 8, 12,
    1, 5, 9, 13,
    2, 6, 10, 14,
    3, 7, 11, 15,
]
```

with the convention:

> output bit position `i` receives input bit position `pbox[i]`.

The implementation computes an inverse permutation explicitly during decryption instead of assuming that every P-box is self-inverse.

### Selected three-round trail

We approximate the first three rounds from plaintext mask

```text
0x0B00
```

to the input of the final S-box layer with mask

```text
0x0505
```

using:

| Round | S-box input mask | S-box output mask | After P | Active transitions | Correlation |
|---:|---:|---:|---:|---|---:|
| 1 | `0x0B00` | `0x0400` | `0x0400` | `B -> 4` | \(+1/2\) |
| 2 | `0x0400` | `0x0500` | `0x0404` | `4 -> 5` | \(-1/2\) |
| 3 | `0x0404` | `0x0505` | `0x0505` | two copies of `4 -> 5` | \(+1/4\) |

There are four active S-box transitions in total.

Their signed correlation product is

\[
C_{\text{trail}}
=
\left(\frac12\right)
\left(-\frac12\right)
\left(-\frac12\right)^2
=
-\frac1{16}.
\]

The corresponding bias estimate is

\[
\epsilon_{\text{trail}}
=
\frac{C_{\text{trail}}}{2}
=
-\frac1{32}.
\]

A common heuristic says that detecting bias \(\epsilon\) requires data on the scale

\[
N\sim\frac{1}{\epsilon^2}.
\]

Here that gives

\[
N\sim1024.
\]

This is only a scale estimate. Real key-ranking success also depends on the number of candidates, trail/hull effects, score variance, and the desired success probability.

### Which subkey bits are guessed?

The endpoint mask

```text
0x0505
```

activates the second and fourth 4-bit S-box positions of the last layer.

Therefore Algorithm 2 needs only the corresponding nibbles of the final whitening key.

For master key

```text
0x3A94D63F
```

the toy schedule gives:

```text
K1 = 3A94
K2 = A94D
K3 = 94D6
K4 = 4D63
K5 = D63F
```

The attacked nibbles of the final key are:

```text
6
F
```

which are packed as candidate

```text
0x6F
```

for the ranking experiment.

This detail is easy to get wrong: `0x6F` is **not** simply a contiguous byte extracted from the master key. It is a compact representation of two selected whitening-key nibbles.

### Reproducible Matsui-2 experiment

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

cipher = SPN(
    TOY_SPN_SBOX,
    TOY_SPN_PBOX,
)

master_key = 0x3A94D63F

rng = Random(0xC0DEC0DE)

messages = rng.sample(
    range(1 << 16),
    8_192,
)

ciphertexts = [
    cipher.encrypt(m, master_key)
    for m in messages
]

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

This experiment performs

\[
256\times8192
=
2,097,152
\]

candidate/pair partial-decryption evaluations.

The deterministic seed is not intended to hide randomness. It exists so that documentation, tests, and future refactoring can reproduce the same result.

### What has actually been recovered?

The experiment recovers **eight selected bits of the final whitening key**.

It does not directly recover:

- the complete 16-bit final round key,
- the 32-bit master key,
- every internal round key.

To extend the attack, one could:

1. select additional approximations terminating at other final S-boxes;
2. obtain rankings for more key nibbles;
3. combine the statistics carefully;
4. map round-key constraints backward through the key schedule;
5. enumerate remaining master-key candidates;
6. verify surviving keys on independent known pairs.

This distinction is essential. A successful partial-key experiment should never be advertised as "full key recovery" unless the remaining search and verification steps are actually performed.

---

## Complexity, Resistance, and Reproducibility

### Data, time, and memory

For a fixed nonzero bias, statistical detection typically has a scale

\[
N=\Theta(\epsilon^{-2})
=
\Theta(C^{-2}),
\]

up to convention-dependent constants.

Writing

\[
N=\frac1{\epsilon^2}
\]

as though it were an exact theorem is too strong.

The required constant depends on:

- desired success probability,
- bias versus correlation convention,
- number of key candidates,
- ranking statistic,
- dependence between approximations,
- signal-to-noise behavior,
- attack advantage.

If \(k\) subkey bits are guessed over \(N\) pairs, a direct Algorithm 2 implementation costs roughly

\[
O(2^kN)
\]

partial operations and stores approximately

\[
O(2^k)
\]

candidate scores.

More advanced attacks use partial-sum and FFT techniques to reorganize the computation, trading time, memory, and implementation complexity.

### How modern designs resist linear cryptanalysis

A block cipher does not defeat linear cryptanalysis merely by choosing an S-box with no obvious relation.

Resistance is systemic.

Useful design principles include:

- low maximum absolute S-box correlation,
- strong diffusion that activates many S-boxes,
- enough rounds for correlations to decay,
- analysis of entire trails and hulls,
- key schedules that avoid harmful symmetries and relations,
- conservative security margins,
- automated search plus independent cryptanalysis.

If each active S-box contributes a correlation magnitude below one, forcing more active S-boxes tends to make a single trail's correlation product rapidly shrink.

That is one reason diffusion criteria such as branch number matter: they are not merely aesthetic measures of "mixing." They can be used to prove lower bounds on the number of active nonlinear components across rounds.

This observation closes a loop with the earlier AES article. AES's S-box properties and its wide-trail diffusion strategy are meaningful partly because they make both differential and linear trails accumulate enough active nonlinear components that useful probabilities or correlations decay rapidly across rounds.

### Beyond one linear approximation

The single-trail, single-counter experiments are the beginning rather than the end of linear cryptanalysis.

Important extensions include:

**Multiple linear cryptanalysis.** Several approximations are combined to improve discrimination or key ranking.

**Multidimensional linear cryptanalysis.** A vector space of approximations is modeled jointly rather than as independent scalar relations.

**Linear-hull analysis.** All compatible trails between fixed endpoints are considered, including key-dependent signs.

**Zero-correlation linear cryptanalysis.** Structural approximations that have exactly zero correlation across a specified number of rounds are exploited by guessing outer rounds and looking for deviations.

**Partial-sum and FFT techniques.** Candidate evaluation is reorganized to reduce attack time.

These techniques require more careful statistics, but the core vocabulary remains the same:

\[
\boxed{
\text{masks}
\rightarrow
\text{correlations}
\rightarrow
\text{propagation}
\rightarrow
\text{statistics}
\rightarrow
\text{key ranking}
}
\]

### Experimental discipline

Reduced-cipher experiments are easy to overinterpret.

A reliable workflow should:

- keep the secret key fixed within one attack,
- use distinct plaintext-ciphertext pairs,
- sample without replacement when the domain permits it,
- state the random seed,
- repeat performance studies across several keys and seeds,
- report true-key rank rather than only a single success/failure result,
- distinguish signed and absolute scores,
- verify encryption/decryption round trips,
- independently verify selected LAT entries,
- document bit order, LAT convention, P-box semantics, and key-schedule rules.

For the current project:

```bash
python matsui1.py
python -m unittest -v test.py
```

Expected checkpoints include:

```text
PRESENT_SBOX:
    LAT[9][1] =  4
    LAT[1][5] = -4

piling-up:
    +0.25 and -0.25 -> -0.125 bias

toy SPN:
    encrypt/decrypt round trip passes

selected trail:
    correlation = -1/16
    bias        = -1/32

Matsui-2 experiment:
    actual packed subkey = 0x6F
    rank(actual)         = 1
```

The notebook [`Linear Cryptanalysis.ipynb`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/Linear%20Cryptanalysis.ipynb) provides a shorter interactive route through the same material.

---

## Series Synthesis and Conclusion

This article closes the **Symmetric Cryptography** series by returning to the architecture with the perspective of an analyst.

The series began with a toy SPN. At that point, substitution, permutation, repeated rounds, and key addition were introduced as construction principles.

Then DES showed a different architecture:

\[
\text{Feistel network}
\]

where round-function invertibility is not required.

AES returned to the SPN family with much stronger algebraic structure:

\[
\text{SubBytes}
\rightarrow
\text{ShiftRows}
\rightarrow
\text{MixColumns}
\rightarrow
\text{AddRoundKey}.
\]

The modes article then moved one level upward:

\[
\text{block cipher}
\rightarrow
\text{message encryption},
\]

showing that even a strong primitive can be misused through ECB leakage, CBC malleability, or CTR nonce reuse.

AEAD added the next missing property:

\[
\text{confidentiality}
+
\text{authentication},
\]

and explained why modern cryptographic interfaces should reject tampered ciphertext before releasing plaintext.

Linear cryptanalysis now takes us back inside the block cipher.

The key lesson is that **nonlinearity and diffusion are not vague design slogans**.

They can be measured.

An S-box exposes a Walsh spectrum and an LAT. A diffusion layer transports masks and forces more S-boxes to become active. Repeated rounds multiply small correlations until a single trail becomes weak enough to be impractical. Multiple trails can still form a hull, so serious analysis must consider more than the locally strongest component relation.

Matsui's algorithms then show how a tiny surviving statistical bias can become actual key information:

\[
\boxed{
\text{S-box approximation}
\rightarrow
\text{multi-round relation}
\rightarrow
\text{statistical bias}
\rightarrow
\text{subkey ranking}
}
\]

That is the connection worth carrying forward.

Cryptographic design and cryptanalysis are not separate subjects. Each explains the other.

We design S-boxes with low correlation because cryptanalysts measure linear correlations. We design strong diffusion because cryptanalysts count active S-boxes. We add rounds because trail probabilities and correlations must decay below useful levels. We validate implementations because a theorem about a cipher says nothing about code that implements a different bit ordering or permutation by mistake.

The final 16-bit experiment deliberately remains small enough to understand completely:

\[
K=\texttt{3A94D63F},
\]

\[
K_5=\texttt{D63F},
\]

\[
C_{\text{trail}}=-\frac1{16},
\]

\[
\epsilon_{\text{trail}}=-\frac1{32},
\]

and the selected final-key nibbles are correctly ranked as

\[
\boxed{\texttt{0x6F}}.
\]

The number itself is not the important result.

The important result is that every step between the Boolean approximation and the ranked subkey is visible, testable, and reproducible.

That is exactly the level at which a cryptographic construction should be studied.

### Ethical use

The implementations in this article are designed for education, research, and reduced teaching ciphers. Apply cryptanalytic techniques only to systems, implementations, and data that you own or are explicitly authorized to test.

---

## References

1. M. Matsui, “Linear Cryptanalysis Method for DES Cipher,” *Advances in Cryptology — EUROCRYPT '93*, LNCS 765, pp. 386–397, 1994.  
   https://doi.org/10.1007/3-540-48285-7_33

2. M. Matsui, “The First Experimental Cryptanalysis of the Data Encryption Standard,” *Advances in Cryptology — CRYPTO '94*, LNCS 839, pp. 1–11, 1994.  
   https://doi.org/10.1007/3-540-48658-5_1

3. K. Nyberg, “Linear Approximation of Block Ciphers,” *Advances in Cryptology — EUROCRYPT '94*, LNCS 950, pp. 439–444, 1995.  
   https://doi.org/10.1007/BFb0053460

4. E. Biham, “On Matsui's Linear Cryptanalysis,” *Advances in Cryptology — EUROCRYPT '94*, LNCS 950, pp. 341–355, 1995.  
   https://doi.org/10.1007/BFb0053449

5. B. S. Kaliski Jr. and M. J. B. Robshaw, “Linear Cryptanalysis Using Multiple Approximations,” *Advances in Cryptology — CRYPTO '94*, LNCS 839, 1994.  
   https://doi.org/10.1007/3-540-48658-5_4

6. J. Y. Cho, M. Hermelin, and K. Nyberg, “A New Technique for Multidimensional Linear Cryptanalysis with Applications on Reduced Round Serpent,” *ICISC 2008*, LNCS 5461, pp. 383–398, 2009.  
   https://doi.org/10.1007/978-3-642-00730-9_24

7. A. Bogdanov and V. Rijmen, “Linear Hulls with Correlation Zero and Linear Cryptanalysis of Block Ciphers,” *Designs, Codes and Cryptography*, vol. 70, pp. 369–383, 2014.  
   https://doi.org/10.1007/s10623-012-9697-z

The accompanying [`references.bib`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/matsui-linear/references.bib) contains machine-readable BibTeX entries.
