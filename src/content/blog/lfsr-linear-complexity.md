---
title: "Linear Feedback Shift Registers: Finite-Field Recurrences, Periods, and State Recovery"
description: "Model LFSRs over GF(2), distinguish primitive-polynomial maximal periods from generic periods, explain linear complexity, and recover a recurrence from observed bits."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Randomness & Entropy"
  - "Mathematical Foundations"
  - "Cryptanalysis"
  - "Symmetric Cryptography"
tags:
  - "lfsr"
  - "gf2"
  - "linear-complexity"
  - "berlekamp-massey"
  - "stream-cipher"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 3
sourcePath: "experiments/randomness-stream-ciphers"
status: "Reviewed"
draft: false
---
A Linear Feedback Shift Register is a finite-state generator whose update rule is linear over $\mathbb F_2$. This makes it elegant, fast, and mathematically analyzable—and, by itself, unsuitable as a cryptographic keystream generator.

## Recurrence model

For an order-$m$ binary LFSR, let the connection coefficients be

$$
p_0,p_1,\ldots,p_{m-1}\in\mathbb F_2.
$$

The generated sequence satisfies

$$
\boxed{s_{m+i}=\sum_{j=0}^{m-1}p_j s_{i+j}\pmod 2}.
$$

Because addition in $\mathbb F_2$ is XOR, the feedback circuit is literally a collection of selected taps XORed together.

A common polynomial representation is

$$
P(X)=X^m+p_{m-1}X^{m-1}+\cdots+p_1X+p_0.
$$

Conventions differ about tap order and whether the register shifts left or right, so implementation diagrams must always be read together with the recurrence.

## The all-zero state

The all-zero state is **absorbing**:

$$
(0,\ldots,0)\mapsto(0,\ldots,0).
$$

It is therefore excluded when studying maximal-length LFSRs. The stronger old statement that an LFSR "cannot output zero" was incorrect; zero bits are perfectly normal. What is forbidden for a maximal-length sequence is the **entire zero state**.

## Period

An $m$-bit state machine has at most $2^m$ states, and a nonzero LFSR has at most

$$
2^m-1
$$

nonzero states in a cycle.

But an arbitrary degree-$m$ connection polynomial does **not** automatically achieve that period. The maximal period $2^m-1$ occurs when the connection polynomial is primitive over $\mathbb F_2$ and the initial state is nonzero.

That correction matters: "an $m$-stage LFSR has period $2^m-1$" is false without the primitive-polynomial condition.

## Recovering the recurrence from bits

If the order $m$ is known and enough consecutive output bits are observed, the unknown coefficients satisfy a linear system over $\mathbb F_2$.

For example,

$$
\begin{bmatrix}
s_0&s_1&\cdots&s_{m-1}\\
s_1&s_2&\cdots&s_m\\
\vdots&\vdots&&\vdots\\
s_{m-1}&s_m&\cdots&s_{2m-2}
\end{bmatrix}
\begin{bmatrix}p_0\\p_1\\\vdots\\p_{m-1}\end{bmatrix}
=
\begin{bmatrix}s_m\\s_{m+1}\\\vdots\\s_{2m-1}\end{bmatrix}.
$$

If the matrix has sufficient rank, Gaussian elimination over $\mathbb F_2$ recovers the tap vector.

When the shortest recurrence length is not known, the **Berlekamp–Massey algorithm** recovers the minimal linear recurrence of a finite sequence and therefore its linear complexity.

## Linear complexity

The linear complexity $L(s)$ of a sequence is the length of the shortest LFSR that can generate it. A long period does not automatically imply high cryptographic security: if the observed sequence has low linear complexity, a compact linear recurrence exists and can be reconstructed.

## Combining LFSRs

Historical stream-cipher designs often fed several LFSRs into a Boolean combining function

$$
z_i=f(x_i^{(1)},\ldots,x_i^{(r)}).
$$

This introduces nonlinearity, but **nonlinearity alone is not enough**. The older note claimed a very broad formula obtained by replacing XORs with addition and products with multiplication in the Boolean function. Such linear-complexity formulas require specific assumptions on the component sequences and combining function; they are not a universal rule.

The next chapter studies the classic Geffe generator, where a nonlinear Boolean combiner still leaves strong correlations with two component LFSRs.

## Executable experiment

The companion code contains a small LFSR class and the Geffe experiment used in the next chapter:

```bash
python experiments/randomness-stream-ciphers/test_lfsr_geffe.py
```

The point is not to build a real cipher. It is to expose the exact linear structure cryptanalysis sees.
