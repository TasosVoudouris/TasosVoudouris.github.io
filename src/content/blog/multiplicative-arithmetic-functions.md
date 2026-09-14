---
title: "Computational Number Theory I: Multiplicative Functions and Dirichlet Convolution"
description: "Divisor functions, Euler phi, Möbius mu, multiplicativity on prime powers, and Dirichlet convolution as the algebra of arithmetic functions."
pubDate: "2025-05-25"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Number Theory"
tags:
- "multiplicative-functions"
- "dirichlet-convolution"
- "mobius-function"
- "euler-phi"
- "divisor-functions"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 1
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
Arithmetic functions take positive integers as input and encode number-theoretic structure. The most useful ones are often multiplicative, which means that prime factorization reduces their computation to prime powers.

## 1. Multiplicative versus completely multiplicative

An arithmetic function $f:\mathbb N\to\mathbb C$ is **multiplicative** if
$$
f(1)=1
$$
and
$$
f(ab)=f(a)f(b)
$$
whenever $\gcd(a,b)=1$.

This is weaker than **complete multiplicativity**, which requires the product rule for all $a,b$.

## 2. Prime-power reduction

If
$$
n=\prod_{p}p^{e_p},
$$
then multiplicativity gives
$$
f(n)=\prod_p f(p^{e_p}).
$$
So the mathematical problem becomes: understand the function on prime powers.

### Number of divisors

For $n=\prod p_i^{e_i}$,
$$
\tau(n)=\prod_i(e_i+1).
$$

### Sum of divisors

$$
\sigma(n)=\prod_i\frac{p_i^{e_i+1}-1}{p_i-1}.
$$

### Euler totient

$$
\varphi(n)=n\prod_{p\mid n}\left(1-\frac1p\right).
$$

### Möbius function

$$
\mu(n)=
\begin{cases}
0,&p^2\mid n\text{ for some prime }p,\\
(-1)^r,&n\text{ is a product of }r\text{ distinct primes}.
\end{cases}
$$

## 3. Dirichlet convolution

For arithmetic functions $f,g$, define
$$
(f*g)(n)=\sum_{d\mid n}f(d)g(n/d).
$$

This operation is associative and commutative, and the identity is
$$
\varepsilon(n)=
\begin{cases}
1,&n=1,\\
0,&n>1.
\end{cases}
$$

The constant function $\mathbf1(n)=1$ has inverse $\mu$:
$$
\mathbf1*\mu=\varepsilon.
$$

That identity is the engine behind Möbius inversion.

## 4. Classical convolution identities

If $\operatorname{id}(n)=n$, then
$$
\sigma=\mathbf1*\operatorname{id}.
$$

Also
$$
\varphi*\mathbf1=\operatorname{id},
$$
so Möbius inversion gives
$$
\varphi=\operatorname{id}*\mu.
$$

These are not merely elegant formulas: they explain why so many arithmetic functions inherit multiplicativity.

## 5. Computational pattern

The companion implementation factors $n$ once and evaluates $\tau$, $\sigma$, $\varphi$, and $\mu$ from the prime-power decomposition. This is cleaner than scanning all possible divisors for every function.

For cryptographic-scale integers, of course, *factoring itself* is the hard step. The formulas are efficient only when a factorization is already known.
