---
title: "Computational Number Theory VII: Integer Factorization from Fermat and Pollard to ECM, QS, and NFS"
description: "A mathematical map of classical integer-factorization algorithms, their structural assumptions, and how their asymptotic roles differ."
pubDate: "2025-05-07"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Number Theory"
- "Cryptanalysis"
tags:
- "integer-factorization"
- "fermat-factorization"
- "pollard-rho"
- "pollard-p-1"
- "ecm"
- "quadratic-sieve"
- "number-field-sieve"
difficulty: "Advanced"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 7
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
Integer factorization is one problem with several algorithmic regimes. A useful taxonomy separates methods that exploit special structure in a factor from general-purpose algorithms that depend primarily on the size of the integer.

## 1. Fermat factorization

For odd $N=pq$ with $p\le q$,
$$
N=a^2-b^2=(a-b)(a+b).
$$
If $p$ and $q$ are close, then
$$
a=\frac{p+q}{2}
$$
is close to $\sqrt N$, so searching upward from $\lceil\sqrt N\rceil$ can quickly find a square $a^2-N=b^2$.

Fermat is therefore a **close-factor** method, not a competitive general factorizer.

## 2. Pollard rho

Pollard's rho generates a pseudorandom sequence modulo $N$ and uses the birthday phenomenon to create a collision modulo an unknown factor $p$.

If
$$
x_i\equiv x_j\pmod p,
$$
then
$$
p\mid(x_i-x_j),
$$
so
$$
\gcd(x_i-x_j,N)
$$
can reveal $p$.

Its expected work is roughly $O(\sqrt p)$ group-style steps for the smallest prime factor, making it useful for finding relatively small factors.

## 3. Pollard $p-1$

If $p\mid N$ and $p-1$ is $B$-smooth, choose an exponent $M$ divisible by many small prime powers. Fermat's theorem gives
$$
a^M\equiv1\pmod p,
$$
so
$$
\gcd(a^M-1,N)
$$
may reveal $p$.

The weakness is smoothness of $p-1$, not closeness of $p$ and $q$.

## 4. Elliptic Curve Method

Lenstra's ECM replaces the multiplicative group modulo $p$ with a randomly chosen elliptic-curve group $E(\mathbb F_p)$. Different curves have different group orders, so repeated random curves give repeated chances that
$$
\#E(\mathbb F_p)
$$
is smooth.

ECM is one of the best methods for finding medium-size prime factors even when the composite cofactor is enormous.

## 5. Quadratic Sieve

QS searches for many values whose residues are smooth over a factor base and combines them to obtain
$$
x^2\equiv y^2\pmod N.
$$
If $x\not\equiv\pm y\pmod N$, then
$$
\gcd(x-y,N)
$$
produces a nontrivial factor.

Its asymptotic complexity is subexponential.

## 6. General Number Field Sieve

GNFS generalizes the congruence-of-squares strategy using algebraic number fields and is asymptotically the fastest known classical algorithm for factoring large general integers.

Its heuristic complexity is
$$
L_N\!\left[\frac13,\left(\frac{64}{9}\right)^{1/3}\right],
$$
where
$$
L_N[\alpha,c]=\exp\!\left((c+o(1))(\log N)^\alpha(\log\log N)^{1-\alpha}\right).
$$

## 7. Why CryptoCave has two factorization articles

This article is the **pure computational-number-theory map**. The RSA Deep Dive on structured-prime factorization is security-oriented: it asks how key-generation choices create exploitable structure. Keeping those goals separate avoids forcing every number-theory algorithm into an RSA narrative.
