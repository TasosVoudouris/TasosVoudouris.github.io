---
title: "Lattices & Lattice-Based Cryptography VIII: NTRU, Polynomial Rings, and the Geometry of the NTRU Lattice"
description: "NTRU from ring arithmetic to lattice geometry: key generation, encryption/decryption conventions, correctness, the public NTRU lattice, short secret vectors, and reduction attacks."
pubDate: "2025-05-31"
updatedDate: "2026-09-13"
topics:
- "Public-Key Cryptography"
- "Lattice Theory"
- "Post-Quantum Cryptography"
- "Cryptanalysis"
tags:
- "ntru"
- "ntru-lattice"
- "polynomial-rings"
- "lll"
- "bkz"
- "post-quantum"
difficulty: "Advanced"
status: "Reviewed"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 8
sourcePath: "experiments/lattices/ntru"
draft: false
---
NTRU is one of the oldest practical lattice-based public-key designs. Its arithmetic is performed in a polynomial quotient ring, while its security can be visualized geometrically through a highly structured $2N$-dimensional lattice containing the secret key as a short vector.

The scheme is historically important because it shows, very concretely, how polynomial algebra and lattice geometry can describe the same cryptographic object.

## 1. Ring setting

A classical presentation works in

$$
R=\mathbb Z[x]/(x^N-1)
$$

with two coprime moduli:

- a small plaintext modulus $p$;
- a much larger ciphertext modulus $q$.

Write

$$
R_p=(\mathbb Z/p\mathbb Z)[x]/(x^N-1),
\qquad
R_q=(\mathbb Z/q\mathbb Z)[x]/(x^N-1).
$$

Secret polynomials are sampled from small distributions, historically sparse ternary distributions.

## 2. Key generation

Choose small $f,g\in R$ such that $f$ is invertible in both $R_p$ and $R_q$.

Let

$$
f_p^{-1}=f^{-1}\pmod p,
\qquad
f_q^{-1}=f^{-1}\pmod q.
$$

One common convention defines

$$
h=p g f_q^{-1}\pmod q.
$$

The public key is $h$; the private key contains $f$ and the inverse information needed for decryption.

![One classical NTRU convention for key generation, encryption, and decryption](/images/blog/ntru/ntru_gen.png)

Some implementations instead define $h=g f_q^{-1}$ and place the factor $p$ in encryption. These conventions are algebraically equivalent after accounting for where the scaling factor is placed; mixing them without saying so is a common source of incorrect toy implementations.

## 3. Encryption

For message $m\in R_p$, sample a fresh small polynomial $r$ and compute

$$
e=rh+m\pmod q.
$$

With the alternative public-key convention $h=g f_q^{-1}$, write instead

$$
e=p r h+m\pmod q.
$$

In either form, $r$ randomizes the ciphertext and all arithmetic occurs in the quotient ring.

## 4. Decryption

Multiply by the secret polynomial:

$$
a=f e\pmod q.
$$

Under the first convention,

$$
f e=p r g+f m\pmod q.
$$

Center-lift the coefficients of $a$ to representatives near zero. If no coefficient has wrapped around modulo $q$, reduction modulo $p$ removes the $prg$ term:

$$
a\equiv f m\pmod p.
$$

Finally,

$$
m=f_p^{-1}a\pmod p.
$$

Correctness is therefore a **size condition**: the relevant integer coefficients must remain inside the centered interval before the reduction modulo $q$ destroys information.

## 5. The public NTRU lattice

Let $T_h$ denote the circulant matrix representing multiplication by $h$ in the coefficient embedding. A standard public lattice basis has block form

$$
B_h=
\begin{pmatrix}
I & T_h\\
0 & qI
\end{pmatrix}.
$$

![Block basis of the public NTRU lattice](/images/blog/ntru/lattice.png)

This spans a $2N$-dimensional lattice with determinant

$$
\det L_h=q^N.
$$

The exact signs and block orientation vary with row/column conventions. What matters is the congruence relation encoded by the basis.

## 6. Why the secret appears as a short vector

Because

$$
f h\equiv p g\pmod q,
$$

the coefficient vectors derived from $f$ and $pg$ satisfy the public modular relation. Since both secret polynomials are sampled small, the corresponding vector is much shorter than a typical vector in the public lattice.

This turns key recovery into a geometric problem:

> Find the unusually short structured vector hidden in the NTRU lattice.

For toy parameters, LLL can reveal it directly. Real parameter sets are chosen so that the required reduction quality and search cost are infeasible.

## 7. LLL, BKZ, and heuristic geometry

The security discussion therefore uses:

- the lattice determinant;
- norms of the secret vectors;
- Gaussian-heuristic length estimates;
- LLL/BKZ reduction quality;
- enumeration/sieving cost after reduction.

It is not enough to say “SVP is hard.” A structured lattice may contain secrets significantly shorter than random-lattice heuristics predict, so parameter selection must account for the best known structured and generic attacks.

## 8. NTRU is not ML-KEM

NTRU and Module-LWE systems belong to the same broad lattice-based family but rely on different algebraic structures and security assumptions.

Modern NIST's primary standardized lattice KEM is **ML-KEM**, derived from CRYSTALS-Kyber and based on Module-LWE. NTRU remains historically and mathematically important, and NTRU-family ideas also appear in lattice signature constructions and structured trapdoor techniques.

## 9. From scheme to research structure

The source material for this chapter also contained work on exact and optimized Gram–Schmidt decompositions for structured NTRU bases. That material is retained separately as a research note rather than mixed into the core cryptosystem explanation:

[NTRU Structured Gram–Schmidt: Symplectic and Isometric Shortcuts](/blog/ntru-structured-gram-schmidt/).
