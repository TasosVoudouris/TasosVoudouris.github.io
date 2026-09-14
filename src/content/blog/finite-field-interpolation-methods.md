---
title: "Finite-Field Polynomial Interpolation: Lagrange, Newton, Barycentric, and FFT Methods"
description: "Compare four interpolation strategies used around secret sharing, explain when each applies, and connect recorded benchmarks to their algebraic assumptions."
pubDate: "2025-05-17"
updatedDate: "2026-09-12"
topics:
- "Mathematical Foundations"
- "Secret Sharing"
- "MPC"
- "Cryptographic Engineering"
tags:
- "polynomial-interpolation"
- "lagrange"
- "newton"
- "barycentric"
- "fft"
- "finite-fields"
- "benchmarks"
difficulty: "Intermediate"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 4
sourcePath: "experiments/threshold-cryptography/interpolation-benchmarks"
draft: false
---
Polynomial interpolation is not a side detail in secret sharing: it is the computational mechanism behind reconstruction. Shamir sharing reconstructs a polynomial value from points, packed sharing uses interpolation to encode several secrets into one polynomial, and FFT-based constructions accelerate the same evaluation/interpolation problem when the domain has roots-of-unity structure.

This research note compares four approaches implemented in the accompanying SageMath/Python experiments:

- standard **Lagrange interpolation**,
- **Newton interpolation** through divided differences,
- the **barycentric** form of Lagrange interpolation,
- finite-field **Fourier/FFT interpolation** on a structured evaluation domain.

The goal is not to declare one universal winner. The algorithms solve closely related interpolation tasks under different assumptions, and their practical cost depends heavily on whether points are arbitrary, reused, or chosen as roots of unity.

## 1. The Interpolation Problem

Let

$$
(x_0,y_0),\ldots,(x_{n-1},y_{n-1})\in\mathbb{F}_q^2
$$

have pairwise-distinct $x_i$. There is a unique polynomial $f\in\mathbb{F}_q[x]$ of degree below $n$ satisfying

$$
f(x_i)=y_i,\qquad i=0,\ldots,n-1.
$$

A secret-sharing protocol may need one of two related operations:

1. recover only a distinguished value such as $f(0)$, or
2. recover the entire coefficient vector of $f$.

Those are not computationally identical tasks. A method that is excellent for evaluating $f(0)$ from many fixed points may not be the best choice when all coefficients are required.

## 2. Standard Lagrange Interpolation

The direct Lagrange formula is

$$
f(x)=\sum_{i=0}^{n-1} y_i L_i(x),
$$

where

$$
L_i(x)=\prod_{\substack{0\le j<n\\j\ne i}}
\frac{x-x_j}{x_i-x_j}.
$$

For a single target point $x^\star$, precomputing the coefficients $L_i(x^\star)$ makes repeated reconstruction attractive. Without precomputation, constructing a full interpolating polynomial in a straightforward way becomes expensive as $n$ grows.

This is why the phrase "Lagrange interpolation is $O(n)$" needs qualification: **evaluating one precomputed interpolation formula at one target point** can be linear, while naive construction of the full polynomial is typically quadratic.

## 3. Newton Interpolation

Newton interpolation writes the polynomial in nested form,

$$
f(x)=c_0+c_1(x-x_0)+c_2(x-x_0)(x-x_1)+\cdots,
$$

with coefficients obtained from divided differences. It is particularly useful when interpolation points arrive incrementally because a new point can extend the representation without rebuilding the entire basis from scratch.

Over a finite field, every division means multiplication by a field inverse, so the algorithm remains algebraic rather than numerical.

## 4. Barycentric Interpolation

The barycentric form rewrites Lagrange interpolation using precomputed weights

$$
w_i=\left(\prod_{j\ne i}(x_i-x_j)\right)^{-1}.
$$

For a target $x$ distinct from all nodes,

$$
f(x)=
\frac{\displaystyle\sum_i \frac{w_i y_i}{x-x_i}}
{\displaystyle\sum_i \frac{w_i}{x-x_i}}.
$$

In floating-point numerical analysis, barycentric interpolation is famous for stability. In finite fields the motivation is different: there is no floating-point roundoff, but **precomputed weights can make repeated evaluations at the same node set much cheaper**.

## 5. Fourier Interpolation over Finite Fields

The FFT route is fundamentally different because it requires a structured domain. Suppose $n\mid(q-1)$ and $\omega\in\mathbb{F}_q$ is a primitive $n$-th root of unity. If

$$
y_j=f(\omega^j),
$$

then the coefficient vector of $f$ can be recovered by an inverse discrete Fourier transform:

$$
a_k = n^{-1}\sum_{j=0}^{n-1} y_j \omega^{-jk}.
$$

A radix-2 FFT evaluates this transform in $O(n\log n)$ field operations when $n$ is a power of two. Similar decompositions exist for other smooth radices.

The speed comes with a restriction: **the points are no longer arbitrary**. They must lie on a compatible roots-of-unity domain.

## 6. What the Experiments Measure

The companion code contains several benchmark cases. The most useful comparison reconstructs the same finite-field polynomial value with standard Lagrange, Newton, barycentric, and Fourier methods while increasing the number of shares.

The recorded results are implementation-specific and should be read as an engineering experiment, not as a formal complexity proof. Python/Sage overhead, precomputation, memory layout, and the exact reconstruction target all affect the timings.

### Standard Lagrange scaling

![Recorded standard-Lagrange interpolation timings](/images/threshold/interpolation-case1-lagrange.png)

The direct implementation grows quickly as the number of shares increases. This is expected for a straightforward full interpolation path.

### Newton, barycentric, and Fourier comparison

![Recorded Newton, barycentric, and Fourier timings](/images/threshold/interpolation-case1-nbf.png)

The experiment shows why implementation strategy matters. Newton and barycentric interpolation improve the practical cost substantially, while the Fourier path exploits the special structure of the evaluation points.

### Combined comparison

![Recorded Lagrange, Newton, barycentric, and Fourier timings](/images/threshold/interpolation-case3-all.png)

For the largest sizes in this recorded experiment, the Fourier method is dramatically faster than the general-purpose interpolation routines. That result is consistent with the $O(n\log n)$ transform structure, but it should not be generalized to arbitrary interpolation domains where an FFT is unavailable.

## 7. Why This Matters for Secret Sharing

The choice of interpolation method changes the engineering profile of a sharing scheme:

| Setting | Natural method |
| --- | --- |
| Small number of arbitrary shares | Direct Lagrange |
| Repeated reconstruction at one target | Precomputed Lagrange/barycentric weights |
| Incrementally changing point set | Newton form |
| Large structured roots-of-unity domain | FFT/NTT |
| Adversarially corrupted shares | Error-correcting decoding, not plain interpolation |

This last row is important. Faster interpolation does **not** make a scheme robust against malicious shares. Robust secret sharing is a decoding problem, which is why the later Gao-decoding article introduces Reed-Solomon structure instead of merely optimizing Lagrange interpolation.

## 8. Reproducibility Notes

The benchmark implementation uses SageMath finite fields together with Python timing and plotting code. The plots included here are preserved from the original experiment. Because runtime measurements depend on hardware and software versions, they should be regenerated before using them as publication-grade performance claims.

The companion folder contains the Lagrange, Newton, barycentric, Fourier, benchmark-case, plotting, and utility modules so the experiment can be inspected and rerun.
