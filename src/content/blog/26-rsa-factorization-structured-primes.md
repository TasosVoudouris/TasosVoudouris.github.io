---
title: "RSA Deep Dive XIII: Factorization When the Prime Structure Helps — Fermat, Pollard p−1, Williams p+1, and ECM"
description: "A comparative RSA factorization deep dive showing how close primes, smooth p−1 or p+1, and favorable elliptic-curve group orders can turn generic factoring into a structure-exploiting attack."
pubDate: "2025-02-24"
updatedDate: "2026-09-12"
topics:
  - "Public-Key Cryptography"
  - "Cryptanalysis"
  - "Number Theory"
  - "Elliptic-Curve Cryptography"
tags:
  - "rsa"
  - "factorization"
  - "fermat-factorization"
  - "pollard-p-minus-1"
  - "williams-p-plus-1"
  - "ecm"
difficulty: "Advanced"
series: "RSA Deep Dives"
seriesOrder: 13
status: "Validated"
sourcePath: "experiments/rsa/factorization-methods"
draft: false
---
Most of the RSA Deep Dive series attacks something more specific than generic integer factorization: repeated moduli, small exponents, related messages, partial key exposure, padding oracles, or structured prime generation.

This article returns to the core assumption

$$
N=pq
$$

and asks a more precise question:

> When does the *structure around* $p$ or $q$ make factorization much easier than for a generic semiprime of the same size?

The recovered Part1 folder contained several separate scripts for Fermat factorization, Pollard $p-1$, Williams $p+1$, and Lenstra's elliptic-curve method. They belong together conceptually rather than as four disconnected "RSA attacks."

## 1. Fermat factorization: exploit close primes

For odd $N=pq$, write

$$
N=a^2-b^2=(a-b)(a+b).
$$

If $p$ and $q$ are close, then

$$
a=\frac{p+q}{2}
$$

lies close to $\sqrt N$, so searching upward from $\lceil\sqrt N\rceil$ can quickly find an $a$ for which

$$
a^2-N=b^2
$$

is a perfect square.

Then

$$
p=a-b,\qquad q=a+b.
$$

Fermat's method is therefore not "fast RSA factoring" in general. It is a structural attack on moduli whose prime factors are too close.

## 2. Pollard p−1: exploit smooth multiplicative-group order

Suppose one prime factor $p$ has

$$
p-1
$$

composed only of small prime powers. Choose a bound $B$ and an exponent $M$ divisible by those powers. For a base $a$ not divisible by $p$,

$$
a^M\equiv1\pmod p.
$$

Therefore $p$ divides

$$
a^M-1.
$$

If the same congruence does not also hold modulo $q$, then

$$
\gcd(a^M-1,N)
$$

reveals $p$.

The attack succeeds because the order of $a$ modulo $p$ divides a smooth number.

## 3. Williams p+1: a related smoothness target

Williams' $p+1$ method uses Lucas sequences rather than the ordinary multiplicative group and is effective for primes where a suitable value related to $p+1$ is smooth.

The lesson is broader than the exact recurrence: factoring methods can move to a different algebraic object whose group/order structure is favorable for one unknown factor.

## 4. Lenstra ECM: vary the group instead of hoping p−1 is smooth

Pollard $p-1$ gives one main group order to exploit for each prime factor. Lenstra's Elliptic Curve Method (ECM) instead chooses elliptic curves modulo $N$.

Modulo an unknown prime factor $p$, each curve has a group order

$$
\#E(\mathbb{F}_p)
$$

that varies with the chosen curve. If that order happens to be sufficiently smooth, scalar multiplication eventually requires an inversion of a denominator that is non-invertible modulo $N$. Computing a gcd with $N$ can then reveal a nontrivial factor.

The conceptual advantage is that ECM can try many curves, effectively sampling many group orders until one is favorable.

## 5. Why an inversion failure can reveal a factor

Over the field $\mathbb{F}_p$, every nonzero denominator has an inverse. Over the composite ring $\mathbb{Z}_N$, a denominator $d$ may satisfy

$$
1<\gcd(d,N)<N.
$$

Then the failed inversion itself contains the factorization signal.

This is a beautiful connection between elliptic-curve arithmetic and integer factorization: an operation that should be legal in a field becomes a diagnostic when performed modulo a composite.

## Comparative view

| Method | Structural weakness | Main signal |
| --- | --- | --- |
| Fermat | $p$ and $q$ unusually close | $a^2-N$ becomes a square quickly |
| Pollard $p-1$ | $p-1$ is smooth | $\gcd(a^M-1,N)$ |
| Williams $p+1$ | suitable $p+1$ Lucas structure is smooth | Lucas-sequence gcd |
| ECM | some $\#E(\mathbb{F}_p)$ is smooth | failed inversion / gcd during EC arithmetic |

None of these should be described as a universal polynomial-time break of RSA.

## Key-generation implications

Secure RSA key generation does not merely ask for two large primes. It uses mature generation procedures intended to avoid obvious structural defects and to meet the security profile's size and statistical requirements.

The existence of these methods is one reason cryptographic software should use established key-generation implementations rather than home-grown prime selection rules.

## Companion experiment

`factorization.py` contains dependency-free implementations of Fermat factorization and stage-1 Pollard $p-1$ on deliberately vulnerable toy moduli. They are executable explanations, not competitive factoring software.

The recovered Sage ECM code remains archived in the Part1 source bundle rather than being presented as a newly validated implementation.

## Where this sits in the RSA map

This deep dive belongs near the end of the series because it complements the other failure classes:

- algebraic message structure,
- weak private exponents,
- partial key information,
- oracle behavior,
- structured prime generation,
- and now factorization-friendly prime structure.

The final synthesis article follows this one and places all of these conditions into one attack map.
