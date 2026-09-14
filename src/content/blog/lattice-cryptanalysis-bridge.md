---
title: "Lattices & Lattice-Based Cryptography XI: Lattice Cryptanalysis — HNP, Small Roots, Nonce Leakage, and LWE Attacks"
description: "A synthesis of lattice reduction as an attack technique: hidden-number problems, biased nonces, Coppersmith small roots, RSA partial exposure, NTRU short secrets, and LWE primal/dual attacks."
pubDate: "2026-09-13"
topics:
- "Cryptanalysis"
- "Lattice Methods"
- "Implementation Security"
tags:
- "lattice-cryptanalysis"
- "hidden-number-problem"
- "ecdsa"
- "coppersmith"
- "boneh-durfee"
- "lwe-attacks"
- "babai"
- "bkz"
difficulty: "Advanced"
status: "Reviewed"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 11
draft: false
---
Lattices are not only a source of post-quantum assumptions. They are also one of the most versatile **cryptanalytic modeling tools** in classical public-key cryptography.

The recurring pattern is:

1. translate partial information, modular equations, or approximation constraints into integer linear relations;
2. build a lattice in which the unknown relation corresponds to an unusually short or unusually close vector;
3. reduce the basis with LLL/BKZ;
4. recover the hidden algebraic information from the reduced vectors.

This chapter is a map. The detailed RSA and ECDSA derivations remain in their existing dedicated CryptoCave series instead of being duplicated here.

## 1. Hidden Number Problems

Suppose observations reveal approximate modular relations of the form

$$
t_i s-u_i\equiv \varepsilon_i\pmod q
$$

where $s$ is secret and the errors $\varepsilon_i$ are known to be small.

This is the **Hidden Number Problem (HNP)** pattern. The modular equations can be embedded into a lattice so that the vector containing the small errors and the secret has anomalously small norm.

This abstraction explains why tiny biases or leaked nonce bits can become devastating in signature schemes.

## 2. ECDSA/DSA nonce leakage

For ECDSA,

$$
s_i\equiv k_i^{-1}(h_i+r_i d)\pmod n.
$$

Rearranging gives

$$
k_i\equiv s_i^{-1}(h_i+r_i d)\pmod n.
$$

If many nonces $k_i$ are partially known, biased, or generated from a restricted range, each signature gives an approximate modular equation in the private key $d$.

The resulting HNP instance can be attacked with lattice reduction when the leakage is strong enough.

The dedicated signature chapter develops the easier exact nonce-reuse case first:

[ECDSA Nonce Reuse, Bias, and Verification Failures](/blog/ecdsa-nonce-failures/).

## 3. Coppersmith: lattices for polynomial small roots

Coppersmith's method transforms a modular polynomial equation

$$
f(x_0)\equiv0\pmod N
$$

with a promised small root $|x_0|<X$ into a lattice of polynomial coefficient vectors.

LLL finds short combinations whose coefficients are small enough that modular vanishing can be promoted to ordinary integer vanishing under the required bounds.

The detailed construction is here:

[Coppersmith From Zero: Small Modular Roots with LLL](/blog/17-rsa-coppersmith-from-zero/).

## 4. RSA partial information

Once small-root machinery exists, many RSA weaknesses become lattice problems:

- partially known plaintexts;
- partially known prime factors;
- small private exponents;
- stereotyped messages;
- partial key exposure.

CryptoCave keeps those cases in the RSA series because the cryptanalytic insight is not merely “run LLL.” The lattice must be constructed from the algebra of each RSA failure mode.

See:

- [Boneh–Durfee](/blog/18-rsa-boneh-durfee/)
- [Partial Key Exposure](/blog/19-rsa-partial-key-exposure/)
- [RSA Attack Map](/blog/25-rsa-synthesis-attack-map/)

## 5. Babai and nearest-plane decoding

After basis reduction, a CVP-like problem is often approximated with **Babai's nearest-plane algorithm**.

Babai is efficient but not an exact CVP solver. Its success depends strongly on basis quality. This makes a common attack pipeline:

$$
\text{structured lattice}
\rightarrow
\text{LLL/BKZ reduction}
\rightarrow
\text{Babai / enumeration}
\rightarrow
\text{candidate secret}.
$$

The NTRU material in the source batch included an experimental message-recovery attack with exactly this pattern. It is retained as provenance/research material but not promoted as a generic break of secure NTRU parameter sets.

## 6. Attacking LWE itself

LWE is designed around lattice hardness, but concrete instances must still be sized against the best known attacks.

### Primal attacks

Embed the LWE equations into a lattice where the error/secret vector becomes a short or unique short vector. Reduce with BKZ and then use enumeration or sieving models to estimate the remaining cost.

### Dual attacks

Search for a short vector in a suitable dual q-ary lattice. Such a vector produces a linear combination of LWE samples in which the secret term cancels or becomes statistically distinguishable.

### Hybrid attacks

Guess some secret coordinates or exploit secret sparsity, then solve a smaller lattice problem.

### BKW

BKW is combinatorial rather than a direct lattice-reduction algorithm. It eliminates blocks of coordinates to create low-dimensional noisy relations and then performs statistical recovery.

## 7. Why attack estimates are parameter-specific

It is misleading to judge a lattice scheme by dimension alone. Concrete cost depends on:

- modulus $q$;
- dimension/module rank;
- secret distribution;
- error distribution;
- number of samples;
- BKZ block size;
- root-Hermite factor/GSA modeling;
- memory and sieving assumptions;
- algebraic structure.

Modern parameter selection therefore relies on dedicated estimators and continual cryptanalytic review.

## 8. Separation of construction and attack code

The uploaded source collection contained several third-party attack repositories. They are useful references, but copying all of them into the canonical CryptoCave tree would create duplicate, difficult-to-maintain code.

The canonical repository therefore keeps:

- our reviewed conceptual articles;
- our existing RSA/Coppersmith experiments;
- small self-contained lattice demonstrations;
- provenance in the cleanup ledger.

Large external toolkits and old attack repositories remain **reference-only**, not active CryptoCave code.
