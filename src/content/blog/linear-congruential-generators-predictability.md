---
title: "Linear Congruential Generators: Periods, Parameter Recovery, and Why Statistical Quality Is Not Security"
description: "Derive the LCG recurrence, recover its parameters from outputs, explain invertibility caveats, and show why a fast simulation PRNG is not a cryptographic generator."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Randomness & Entropy"
  - "Cryptanalysis"
  - "Number Theory"
  - "Cryptographic Engineering"
tags:
  - "lcg"
  - "prng"
  - "state-recovery"
  - "modular-arithmetic"
  - "predictability"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 2
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---
A linear congruential generator is one of the clearest examples of the difference between **pseudorandom-looking output** and **cryptographic unpredictability**.

Its recurrence is

$$
S_{i+1}=aS_i+c\pmod m,
$$

with modulus $m$, multiplier $a$, increment $c$, and initial state $S_0$.

LCGs are historically important and still useful in simulation contexts, but their algebra is so rigid that a few outputs can reveal the recurrence.

## Recovering the parameters when the modulus is known

Assume an observer knows three consecutive states

$$
S_0,S_1,S_2.
$$

Then

$$
S_1\equiv aS_0+c\pmod m,
$$

$$
S_2\equiv aS_1+c\pmod m.
$$

Subtracting eliminates $c$:

$$
S_2-S_1\equiv a(S_1-S_0)\pmod m.
$$

If $S_1-S_0$ is invertible modulo $m$, then

$$
\boxed{a\equiv(S_2-S_1)(S_1-S_0)^{-1}\pmod m}.
$$

After recovering $a$,

$$
\boxed{c\equiv S_1-aS_0\pmod m}.
$$

This corrects an indexing typo in the older note, which accidentally wrote the second recurrence with $aS_3$ instead of $aS_2$.

## The modular inverse caveat

The simple formula requires

$$
\gcd(S_1-S_0,m)=1.
$$

If that difference is not invertible, the recovery problem becomes a modular linear-congruence problem rather than a single multiplication by an inverse. There may be multiple candidate multipliers or additional observations may be required.

That caveat matters because modular arithmetic is not ordinary division.

## Predicting future states

Once $a$ and $c$ are known, every later state is deterministic:

$$
S_{i+1}=aS_i+c\pmod m.
$$

No cryptographic hardness assumption remains. An adversary who reconstructs the state can compute future output exactly.

If an application creates a stream cipher by XORing plaintext with LCG output, known plaintext can expose keystream values and therefore the generator state or parameters.

## Period is not security

An LCG can be configured for a long period. For mixed LCGs, the Hull-Dobell conditions characterize when the period reaches the full modulus $m$.

But a long period only says the generator does not repeat quickly. It says nothing about state-recovery resistance.

The distinction is important:

| Property | Simulation value | Cryptographic value |
|---|---:|---:|
| Long period | useful | insufficient |
| Fast generation | useful | useful |
| Uniform-looking histograms | useful | insufficient |
| State-recovery resistance | optional | essential |
| Next-output unpredictability | optional | essential |

## What if the modulus is unknown?

With enough consecutive outputs, differences of differences produce integer multiples of the hidden modulus. GCD techniques can then recover a candidate $m$ in many practical cases. The exact derivation depends on the observed sequence and divisibility conditions, but the broader lesson is the same: the recurrence leaves strong algebraic fingerprints.

## Executable experiment

The companion implementation recovers $a$ and $c$ from three states when $m$ is known and the required difference is invertible.

```bash
python experiments/randomness-stream-ciphers/test_lcg.py
```

The test verifies that recovered parameters predict the same next state as the original generator.

## Security lesson

An LCG is not a CSPRNG. Its failure is not that it produces obviously patterned decimal numbers; its failure is that the relation between states is **efficiently solvable**.

This is the first recurring theme of the series: linear structure is easy to implement, but cryptography must assume that an adversary will exploit every exposed equation.
