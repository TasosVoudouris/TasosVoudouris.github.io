---
title: "Computational Number Theory II: Prime Counting, the Prime Number Theorem, and Prime Gaps"
description: "A computational study of pi(x), x/log x, li(x), prime gaps, and what asymptotic statements do—and do not—say at finite scales."
pubDate: "2025-05-25"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Number Theory"
tags:
- "prime-counting-function"
- "prime-number-theorem"
- "logarithmic-integral"
- "prime-gaps"
- "riemann-hypothesis"
difficulty: "Intermediate"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 2
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
Prime numbers become sparser, but not randomly sparse. The prime-counting function
$$
\pi(x)=|\{p\le x:p\text{ prime}\}|
$$
turns that qualitative observation into a measurable function.

## 1. Prime Number Theorem

The Prime Number Theorem states
$$
\pi(x)\sim\frac{x}{\log x},
$$
meaning
$$
\lim_{x\to\infty}\frac{\pi(x)}{x/\log x}=1.
$$

This does **not** mean that $\pi(x)=x/\log x$, nor that the graph is close at small $x$. It is an asymptotic ratio statement.

An equivalent density heuristic is
$$
\frac{\pi(x)}x\sim\frac1{\log x}.
$$
Around a large number $x$, the rough chance that an integer behaves like a prime candidate is therefore about $1/\log x$.

## 2. Logarithmic integral

A better first-order approximation is
$$
\operatorname{Li}(x)=\int_2^x\frac{dt}{\log t}.
$$
Empirically, $\operatorname{Li}(x)$ tracks $\pi(x)$ more closely than $x/\log x$ over wide ranges, even though the difference changes sign eventually.

## 3. Riemann Hypothesis and the error term

A classical result of von Koch says that the Riemann Hypothesis is equivalent to an error bound of the shape
$$
\pi(x)=\operatorname{Li}(x)+O(\sqrt{x}\log x).
$$

The uploaded note stated this as though it were an unconditional approximation. The canonical version must keep the condition explicit: this sharp error term is tied to the Riemann Hypothesis.

## 4. Prime gaps

Let
$$
p_1<p_2<p_3<\cdots
$$
be the primes. The $n$th prime gap is
$$
g_n=p_{n+1}-p_n.
$$

Except for $3-2=1$, all prime gaps are even because all primes beyond $2$ are odd.

The gaps are unbounded, yet many small gaps recur frequently. The twin-prime conjecture asks whether
$$
g_n=2
$$
infinitely often.

## 5. Why plots can mislead

Histograms over primes up to $10^6$ are useful exploratory tools, but they are finite samples. Observing strong peaks at multiples of $6$ reflects congruence restrictions, not a proof about the limiting distribution of gaps.

This distinction—**computation suggests, theorem proves**—is especially important in computational number theory.
