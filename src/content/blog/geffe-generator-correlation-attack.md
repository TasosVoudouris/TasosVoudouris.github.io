---
title: "The Geffe Generator: How Correlation Breaks a Nonlinear Combination of LFSRs"
description: "Construct the Geffe combiner, derive its 3/4 correlations, compare exhaustive-search costs, and show why nonlinearity without correlation immunity is insufficient."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Randomness & Entropy"
  - "Cryptanalysis"
  - "Symmetric Cryptography"
tags:
  - "geffe-generator"
  - "correlation-attack"
  - "lfsr"
  - "stream-cipher"
  - "correlation-immunity"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 4
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---
A natural response to the weakness of a single LFSR is to combine several LFSRs through a nonlinear Boolean function. The **Geffe generator** is a classic example showing why that idea must be analyzed very carefully.

Let three LFSRs produce bits $x,y,z$. Define

$$
F(x,y,z)=xy\oplus(1\oplus x)z.
$$

Equivalently, $x$ acts as a selector:

- if $x=1$, output $y$;
- if $x=0$, output $z$.

The function is nonlinear, but its output is strongly correlated with both data inputs.

## Correlation calculation

Assume $x,y,z$ behave as independent unbiased bits.

For the output $F$ and $y$:

- when $x=1$, $F=y$ with probability $1$;
- when $x=0$, $F=z$, and $z=y$ with probability $1/2$.

Therefore

$$
\Pr[F=y]=\frac12\cdot1+\frac12\cdot\frac12=\frac34.
$$

Similarly,

$$
\Pr[F=z]=\frac34.
$$

The selector $x$ itself has no corresponding $3/4$ agreement:

$$
\Pr[F=x]=\frac12
$$

under the same idealized assumptions.

## Attack idea

Suppose the attacker observes a sufficiently long output sequence $F_1,F_2,\ldots$. For each candidate initial state of the $y$-register, generate its candidate sequence and compute the agreement rate with the observed output.

The correct state should stand out around the expected $3/4$ correlation while wrong states hover around $1/2$.

Repeat for the $z$-register. Once those two states are known, search the smaller selector register $x$ and check which candidate reproduces the complete keystream.

## Complexity intuition

If the register state lengths are $L_x,L_y,L_z$, naive joint search costs roughly

$$
2^{L_x+L_y+L_z}.
$$

Correlation search instead behaves more like

$$
2^{L_y}+2^{L_z}+2^{L_x},
$$

plus the data required to distinguish a $3/4$ correlation from chance.

This is an exponential reduction in the natural security exponent.

## Period correction

The old notes wrote the overall period as the product

$$
(2^{L_x}-1)(2^{L_y}-1)(2^{L_z}-1).
$$

That product is achieved only under additional coprimality and maximal-period conditions. In general, the period of a combined sequence divides a quantity related to the **least common multiple** of the component periods; it should not be asserted as the raw product without assumptions.

## Correlation immunity

The broader design concept is **correlation immunity**: a Boolean combining function should avoid leaking statistically useful correlation with small subsets of its inputs.

But correlation immunity competes with other desirable Boolean-function properties such as nonlinearity and algebraic degree. Historical combiner-generator design therefore became a genuine cryptographic design problem, not simply "XOR several LFSRs."

Modern ciphers such as ChaCha20 use a very different architecture rather than relying on a small set of LFSRs and a Boolean selector.

## Executable experiment

The companion test generates toy Geffe output and verifies that the observed sequence has strong empirical agreement with the two selected data registers:

```bash
python experiments/randomness-stream-ciphers/test_lfsr_geffe.py
```

This is deliberately a toy demonstration. It exists to make the statistical weakness visible, not to attack a deployed system.
