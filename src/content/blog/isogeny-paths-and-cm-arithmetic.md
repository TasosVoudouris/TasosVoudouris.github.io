---
title: "Elliptic Curve Mathematics XIII: Isogenies, Modular Polynomials, and CM Arithmetic"
description: "A compact analysis of modular polynomials, isogeny neighborhoods and paths, and complex-multiplication-related arithmetic used in isogeny computations."
pubDate: "2025-05-27"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Post-Quantum Cryptography"
- "Mathematical Foundations"
tags:
- "isogenies"
- "modular-polynomials"
- "complex-multiplication"
- "cm"
- "isogeny-graphs"
difficulty: "Advanced"
series: "Elliptic Curve Mathematics"
seriesOrder: 13
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
The script `src/IsogenyPaths.sage` provides a computational framework for analyzing isogeny graphs and related arithmetic in the context of elliptic curves over finite fields. It leverages modular polynomials $\Phi_\ell(X, Y)$ for small primes $\ell$ to compute isogeny neighbors, verify adjacency of $j$-invariants, and explore isogeny paths. Additionally, it integrates methods from complex multiplication (CM) theory, such as solving norm equations, finding split primes, computing class numbers of imaginary quadratic fields, and constructing quadratic forms representing primes.

These tools serve foundational roles in isogeny-based cryptography, elliptic curve cryptography (ECC), and number-theoretic constructions of cryptographic relevance.

## Modular Polynomials $\Phi_\ell(X, Y)$

The modular polynomial $\Phi_\ell(X, Y)$ encodes the relation between $j$-invariants of elliptic curves connected via an isogeny of degree $\ell$. That is, two curves $E_1$ and $E_2$ are $\ell$-isogenous if and only if

$$
\Phi_\ell(j(E_1), j(E_2)) = 0.
$$

For small primes $\ell \in \{2, 3, 5, 7\}$, explicit expressions for $\Phi_\ell$ are hardcoded and used to efficiently identify isogenous neighbors. These polynomials define the edges in an $\ell$-isogeny graph.

## Core Functions and Their Cryptographic Roles

Below we gonna briefly analyze the core functions of the script: 


### `expand_roots`

```python
def expand_roots(r):
    return reduce(lambda x, y: x + y, map(lambda x: [x[0] for i in xrange(0, x[1])], r))
```

*Expands roots with multiplicities into a flat list.* This function is a utility to simplify the root structure of polynomial solutions.

### `isogeny_nbrs(ell, j, xj=None)`

Given a prime $\ell$ and a $j$-invariant $j$, this function computes all $\ell$-isogenous neighbors of $j$ by solving $\Phi_\ell(X, j) = 0$. If a root $x_j$ is known a priori (e.g., the source of the isogeny), it is excluded from the result.

This operation is fundamental for constructing isogeny graphs and performing walks in isogeny-based cryptographic protocols such as SIDH and CSIDH.

### `isogeny_path(ell, j_0, j_1, n)`

Constructs a sequence of $\ell$-isogenies of total length $n$ connecting the given $j$-invariants $j_0$ and $j_1$, if such a path exists. This is critical in isogeny-based protocols that depend on hard problems over supersingular isogeny graphs.

### `isogeny_is_nbr(ell, j_1, j_2)`

Determines whether two $j$-invariants $j_1$ and $j_2$ are directly connected by an isogeny of degree $\ell$, by evaluating $\Phi_\ell(j_1, j_2)$. This serves as an adjacency test in the corresponding isogeny graph.

### `norm_equation(D, p)`

Solves the norm equation

$$
4p = t^2 - v^2 D
$$

for integers $t, v$, where $D < 0$ is a fundamental discriminant and $p$ is a (probable) prime. The existence of a solution implies that the prime $p$ splits in the imaginary quadratic field $\mathbb{Q}(\sqrt{D})$, which is essential for constructing elliptic curves with complex multiplication by $\mathcal{O}_D$.

### `next_split_prime(D, t_0)`

Searches for the smallest prime $p$ such that $4p = t^2 - v^2 D$ holds for some $t > t_0$. This is used in CM constructions to ensure the existence of primes where the Hilbert class polynomial splits, enabling curve generation over $\mathbb{F}_p$.


### `class_number(D)`

Computes the class number of the imaginary quadratic field $\mathbb{Q}(\sqrt{D})$, i.e., the number of distinct ideal classes in its maximal order. The class number plays a crucial role in the enumeration of isomorphism classes of CM elliptic curves.

### `prime_form(D, p)`

Attempts to find a binary quadratic form $(p, b, c)$ such that

$$
b^2 - 4pc = D,
$$

i.e., a form of discriminant $D$ representing the prime $p$. Such forms correspond to ideals in the ring of integers of $\mathbb{Q}(\sqrt{D})$ and are used to link algebraic and geometric representations of CM.

## Wrap-up

This script offers a comprehensive computational toolkit for analyzing isogeny relations and complex multiplication (CM) structures in the context of elliptic curves. It provides functionality for evaluating modular polynomials $\Phi_\ell(X, Y)$ for small primes $\ell$, identifying isogeny neighbors, constructing isogeny paths between $j$-invariants, solving norm equations central to CM theory, locating split primes suitable for CM curve generation, computing class numbers of imaginary quadratic fields, and constructing quadratic forms representing primes.

These capabilities serve a broad range of applications in modern cryptography. In isogeny-based cryptographic protocols such as SIDH, SIKE, and CSIDH, the arithmetic underlying isogeny graphs is essential for both security and implementation. In classical elliptic curve cryptography (ECC), understanding isogeny classes and endomorphism rings enhances curve validation and parameter selection. Moreover, from the perspective of number theory, the integration of CM techniques enables the explicit construction of elliptic curves with prescribed endomorphism rings via Hilbert class polynomials.
