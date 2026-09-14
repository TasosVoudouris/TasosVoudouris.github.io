---
title: "NTT Engineering for Secret Sharing: Roots of Unity, Iterative/Recursive Transforms, and Packed Domains"
description: "Connect finite-field NTT implementations to packed secret sharing, explain transform-domain assumptions, compare recursive and iterative butterflies, and audit the recovered q=12289 implementation and its tests."
pubDate: "2025-05-21"
updatedDate: "2026-09-14"
topics:
  - "Secret Sharing"
  - "MPC"
  - "Mathematical Foundations"
  - "Cryptographic Engineering"
tags:
  - "ntt"
  - "fft"
  - "roots-of-unity"
  - "packed-secret-sharing"
  - "polynomial-arithmetic"
  - "butterfly"
difficulty: "Advanced"
status: "Validated"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 8
sourcePath: "experiments/secret-sharing/ntt-engineering"
draft: false
---
The recovered archive contained three generations of finite-field transform code: a small `py_ntt_intt` experiment, FFT-style sharing code, and a much more complete iterative/recursive NTT package targeting the prime

$$
q=12289.
$$

The useful lesson is not that secret sharing "requires an NTT". It is that packed sharing and batched polynomial protocols become dramatically more efficient when the evaluation domain has the right algebraic structure.

## 1. FFT versus NTT

The complex FFT evaluates a polynomial on complex roots of unity. The Number Theoretic Transform performs the analogous operation in a finite field.

For a primitive $n$-th root of unity $\omega\in\mathbb F_q$,

$$
\omega^n=1
$$

and

$$
\omega^k\ne1\qquad 0<k<n.
$$

For

$$
f(X)=\sum_{j=0}^{n-1}a_jX^j,
$$

the transform is

$$
\widehat f_k=f(\omega^k).
$$

The inverse transform reconstructs the coefficient vector using $\omega^{-1}$ and $n^{-1}\bmod q$.

## 2. Why the modulus matters

To have an $n$-th root of unity in $\mathbb F_q^*$, we need

$$
n\mid(q-1).
$$

The recovered implementation uses

$$
12289-1=12288=3\cdot2^{12},
$$

which supplies large power-of-two subgroups.

This is why cryptographic implementations deliberately choose NTT-friendly moduli rather than arbitrary primes.

## 3. The butterfly

The radix-2 decomposition splits

$$
f(X)=f_0(X^2)+Xf_1(X^2),
$$

where $f_0$ contains even-indexed coefficients and $f_1$ odd-indexed coefficients.

At paired roots $\omega^k$ and $-\omega^k$:

$$
f(\omega^k)=f_0(\omega^{2k})+\omega^k f_1(\omega^{2k}),
$$

$$
f(-\omega^k)=f_0(\omega^{2k})-\omega^k f_1(\omega^{2k}).
$$

That two-output computation is the butterfly.

![Divide-and-conquer NTT evaluation structure](/images/secret-sharing/ntt-divide-and-conquer.png)

*The recovered thesis diagram makes the recursive even/odd split visible: each layer evaluates smaller coefficient subsets on progressively squared root-of-unity domains.*

Repeated recursively, the cost drops from naive $O(n^2)$ evaluation to

$$
O(n\log n).
$$

## 4. Recursive implementation

The recovered recursive implementation makes the mathematical decomposition especially visible:

```python
f0, f1 = f[::2], f[1::2]
f0_ntt = self.ntt(f0)
f1_ntt = self.ntt(f1)
return self.merge_ntt([f0_ntt, f1_ntt])
```

This form is excellent for understanding the recurrence.

Its inverse explicitly performs the reverse split and uses the inverse of $2$ in the field.

## 5. Iterative implementation

The iterative version performs the same butterflies in staged loops. It avoids recursive function overhead and naturally matches table-driven twiddle-factor implementations.

Conceptually:

```text
stage 0: blocks of size 2
stage 1: blocks of size 4
stage 2: blocks of size 8
...
```

The recovered package precomputes roots in the order required by the butterfly schedule.

This is a cryptographic-engineering tradeoff: precomputation consumes memory but can reduce repeated exponentiation and indexing work.

## 6. Why this matters for packed secret sharing

Packed sharing frequently represents many secrets as values of one polynomial on a structured domain.

If the secret/evaluation points form a root-of-unity domain, conversion between

$$
\text{coefficients}
\quad\leftrightarrow\quad
\text{evaluations}
$$

can use the NTT.

That can accelerate:

- interpolation;
- polynomial multiplication;
- batch encoding;
- Reed--Solomon style operations;
- packed MPC subprotocols.

But the transform is an **optimization layer**. The privacy argument still comes from the sharing construction and its random degrees of freedom.

## 7. Negacyclic versus ordinary transforms

The recovered `Super NTT` code is written for polynomial arithmetic modulo

$$
X^n+1,
$$

not merely an arbitrary Shamir evaluation domain. That is a negacyclic setting familiar from lattice cryptography.

This is useful reusable arithmetic, but it should not be presented as if every Shamir scheme works in $\mathbb F_q[X]/(X^n+1)$.

For secret sharing, what matters is selecting suitable distinct evaluation points and, for FFT acceleration, a compatible multiplicative subgroup/coset.

For ring-based lattice cryptography, the quotient-ring interpretation is central.

Same transform machinery, different protocol semantics.

## 8. Test audit of the recovered package

The archive contained a mature test suite. Four core groups run cleanly after setting the package path:

```text
15 tests passed
38 subtests passed
```

covering:

- iterative NTT/INTT;
- recursive NTT/INTT;
- polynomial arithmetic;
- utility routines.

One additional `test_vectors.py` fails **during test collection**, not because the transform output is wrong, but because importing the vector-generation module immediately writes to a relative path that does not exist in the extracted environment.

That is a packaging/test-isolation bug. Generating fixtures should be an explicit script action, not an import-time side effect.

The canonical companion implementation therefore keeps the educational transform and tests separate from vector generation.

## 9. Integer growth and delayed reduction

The iterative source also experiments with postponing modular reductions for $q=12289$.

That can be a real performance technique, but the bounds are parameter-specific. Comments such as

```text
THIS WORKS FOR Q OF THE SIZE OF FALCON Q=12289
```

are important: the optimization must not silently be generalized to unrelated fields or word sizes.

## 10. The connection to our lattice series

The same NTT ideas reappear in Ring-LWE, Module-LWE, NTRU, ML-KEM, and ML-DSA.

The difference is context:

- here: efficient finite-field evaluation/interpolation and packed sharing;
- there: fast multiplication in structured quotient rings.

That cross-link is intentional. CryptoCave should reuse mathematics without pretending the surrounding cryptographic objects are identical.

## 11. Takeaway

An NTT is not a secret-sharing scheme. It is a fast algebraic engine.

$$
\boxed{\text{sharing gives privacy; the NTT gives structured polynomial speed.}}
$$

Keeping those layers separate prevents both security overclaims and implementation confusion.
