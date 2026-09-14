---
title: "Classical Cryptanalysis I: Caesar, Substitution, Vigenère, and Frequency Analysis"
description: "A compact but rigorous path from shift/substitution ciphers to frequency analysis and Vigenère, showing how language redundancy creates exploitable statistical structure."
pubDate: "2024-10-15"
updatedDate: "2026-09-12"
topics:
  - "Classical Cryptography"
  - "Cryptanalysis"
  - "Mathematical Foundations"
tags:
  - "caesar"
  - "vigenere"
  - "frequency-analysis"
  - "substitution-cipher"
difficulty: "Introductory"
series: "Classical Cryptanalysis"
seriesOrder: 1
status: "Reviewed"
sourcePath: "experiments/classical-cryptanalysis"
draft: false
---
Classical ciphers are not secure cryptography, but they are unusually good teaching tools because the attack surface is visible. The ciphertext still carries statistical structure from the language, and the cryptanalyst's job is to identify what the transformation failed to hide.

## Caesar as modular arithmetic

Map letters to integers in $\mathbb{Z}_{26}$. A Caesar shift by key $k$ is

$$
E_k(x)=x+k\pmod{26},
$$

with decryption

$$
D_k(y)=y-k\pmod{26}.
$$

There are only 26 possible shifts, so exhaustive search is already enough. Frequency analysis gives another route by exploiting the fact that a shift permutes symbol labels but preserves symbol counts.

## Monoalphabetic substitution

A general substitution cipher replaces the simple shift with a permutation of the alphabet. The key space becomes enormous compared with Caesar, but the cipher still preserves many language statistics:

- single-letter frequencies,
- repeated letters,
- common digrams and trigrams,
- word-length patterns,
- repeated-word structure.

A large key space does not rescue a construction that leaks strong structure.

## Frequency analysis

For ciphertext $C$, count how often each symbol appears. If $N$ alphabetic characters are present and symbol $a$ appears $n_a$ times, its empirical frequency is

$$
\hat p(a)=\frac{n_a}{N}.
$$

The cryptanalyst compares that distribution with expected language statistics, then tests candidate mappings using higher-order context.

The companion `frequency_analysis.py` intentionally does only counting and ranking. It does not pretend that "the most frequent letter is E" is a complete substitution solver; real solving combines several constraints.

## Vigenère changes the statistical problem

Vigenère uses a repeating key of length $\ell$. If the key letters are $k_0,\ldots,k_{\ell-1}$, then

$$
C_i=P_i+k_{i\bmod\ell}\pmod{26}.
$$

The same plaintext letter may encrypt to different ciphertext letters depending on position, so ordinary single-distribution frequency analysis is weakened.

But the repeating period creates another structural leak. Once the period is estimated, positions with the same index modulo $\ell$ can be separated into columns, and each column behaves like a Caesar cipher.

That observation leads directly to the Kasiski examination in the next article.

## The broader lesson

Classical cryptanalysis teaches a principle that survives into modern cryptography: attackers exploit **structure that the construction failed to randomize or authenticate**. Modern schemes use formal security models rather than language statistics, but the habit of asking "what relation survives encryption?" remains central.

## Companion experiment

`experiments/classical-cryptanalysis/frequency_analysis.py` provides a dependency-free letter-counting helper suitable for Caesar and substitution exercises.
