---
title: "BFV Homomorphic Encryption: Ring-LWE, Ciphertext Multiplication, Relinearization, and Noise"
description: "A corrected derivation of the BFV/BFV-style homomorphic-encryption workflow: RLWE keys, plaintext scaling, encryption/decryption, homomorphic addition and multiplication, relinearization, and noise growth."
pubDate: "2025-06-01"
updatedDate: "2026-09-13"
topics:
- "Homomorphic Encryption"
- "Lattice Theory"
- "Post-Quantum Cryptography"
- "Cryptographic Engineering"
tags:
- "bfv"
- "ring-lwe"
- "homomorphic-encryption"
- "relinearization"
- "noise-budget"
- "rlwe"
difficulty: "Advanced"
status: "Reviewed"
series: "Homomorphic Encryption"
seriesOrder: 11
sourcePath: "experiments/homomorphic/bfv"
draft: false
---
The Brakerski/Fan–Vercauteren family of schemes turns Ring-LWE-style noisy polynomial relations into encryption that supports exact modular arithmetic on ciphertexts.

The central tension is the same one that appears throughout lattice homomorphic encryption:

> noise is essential for security, but decryption remains correct only while that noise stays below a parameter-dependent threshold.

This chapter keeps the detailed intuition from the original BFV notebook, while separating pedagogical toy formulas from production parameterization.

## 1. Rings for plaintexts and ciphertexts

Take

$$
R=\mathbb Z[x]/(x^N+1),
$$

usually with $N$ a power of two.

Plaintexts live modulo a small modulus $t$:

$$
R_t=R/tR,
$$

while ciphertext arithmetic uses a much larger modulus $q$:

$$
R_q=R/qR.
$$

![Homomorphic computation on encrypted data](/images/blog/bfv/he.png)

The polynomial modulus imposes negacyclic arithmetic:

$$
x^N\equiv -1.
$$

For example,

$$
x^{N+1}\equiv -x.
$$

Production implementations choose $N,t,q$ according to security, multiplicative depth, batching requirements, and implementation constraints. Tiny parameters are useful only for understanding the algebra.

![A visual coefficient-space view of quotient-ring polynomials](/images/blog/bfv/polynomial-torus.png)

## 2. Centered representatives

Coefficients modulo $q$ can be represented in $\{0,1,\dots,q-1\}$ or by centered representatives near zero.

![Modular coefficients viewed on a clock](/images/blog/bfv/modular-numbers.png)

For odd $q$, a convenient centered interval is

$$
\left[-\frac{q-1}{2},\frac{q-1}{2}\right].
$$

Noise analysis is much clearer in this centered representation because “small” means small absolute coefficient or small canonical-embedding norm rather than an integer numerically close to $q$.

## 3. Secret and public keys

A simplified BFV-style presentation samples a small secret polynomial

$$
s\leftarrow\chi_s
$$

and public uniform polynomial

$$
a\leftarrow R_q.
$$

Sample a small error

$$
e\leftarrow\chi_e
$$

and define

$$
b=-as+e\pmod q.
$$

The public key is

$$
\operatorname{pk}=(b,a),
$$

and the secret key is $s$.

The relation

$$
b+as=e
$$

is exactly an RLWE-style noisy relation: knowing $(a,b)$ does not expose $s$ because the equation is perturbed by a small unknown error.

## 4. Scaling the plaintext

Let

$$
\Delta=\left\lfloor\frac qt\right\rfloor.
$$

A plaintext $m\in R_t$ is embedded into ciphertext space approximately as

$$
\Delta m\in R_q.
$$

This spacing creates room between neighboring plaintext representatives. Decryption can tolerate noise as long as it does not move a coefficient across the relevant rounding boundary.

## 5. Encryption

Sample a fresh small mask $u$ and fresh error polynomials $e_1,e_2$. Compute

$$
c_0=bu+e_1+\Delta m\pmod q,
$$

$$
c_1=au+e_2\pmod q.
$$

The ciphertext is

$$
c=(c_0,c_1).
$$

The same plaintext encrypts differently because $u,e_1,e_2$ are freshly sampled.

## 6. Decryption

Form

$$
v=c_0+c_1s\pmod q.
$$

Expanding gives

$$
\begin{aligned}
v
&=(-as+e)u+e_1+\Delta m+(au+e_2)s\\
&=\Delta m+eu+e_1+e_2s.
\end{aligned}
$$

So

$$
v=\Delta m+\nu
$$

for a noise polynomial

$$
\nu=eu+e_1+e_2s.
$$

After centered lifting, scale back and round:

$$
m\approx\left\lfloor\frac tq v\right\rceil\pmod t.
$$

Correctness holds while the effective noise remains far enough from a rounding boundary.

## 7. Homomorphic addition

Given encryptions of $m_1$ and $m_2$,

$$
c^{(1)}=(c_0^{(1)},c_1^{(1)}),
\qquad
c^{(2)}=(c_0^{(2)},c_1^{(2)}),
$$

add component-wise:

$$
c^{(+)}=
(c_0^{(1)}+c_0^{(2)},
 c_1^{(1)}+c_1^{(2)}).
$$

Decryption gives approximately

$$
\Delta(m_1+m_2)+(\nu_1+\nu_2).
$$

Addition therefore grows noise roughly additively.

![Toy coefficient-noise experiment for repeated BFV-style addition](/images/blog/bfv/addition-noise.png)

## 8. Ciphertext multiplication

Write decryption abstractly as evaluating a ciphertext polynomial in the secret:

$$
c(s)=c_0+c_1s.
$$

Multiplying two fresh ciphertexts gives

$$
(c_0+c_1s)(d_0+d_1s)
=
 c_0d_0+(c_0d_1+c_1d_0)s+c_1d_1s^2.
$$

So the raw product naturally has **three components**:

$$
(e_0,e_1,e_2).
$$

The extra $s^2$ term is the reason multiplication is fundamentally more complicated than addition.

BFV also needs a scale-management step so that plaintext multiplication remains in the intended $t$-modular space. Exact formulas differ among BFV descriptions and implementation variants, so one should not mix a textbook scaling formula with a library's RNS implementation without checking conventions.

## 9. Relinearization

A ciphertext of growing length is expensive to store and process. **Relinearization** uses an evaluation key derived from the secret to transform the $s^2$ contribution back into a two-component ciphertext.

Conceptually, the evaluation key provides an encryption-compatible representation of $s^2$ that lets us rewrite

$$
e_2s^2
$$

as additional contributions to the constant and linear-in-$s$ components.

The result returns to

$$
(c'_0,c'_1)
$$

without decrypting the message.

This is a form of key switching.

## 10. Noise after multiplication

Multiplication combines existing errors with messages, secrets, and other errors. Noise therefore grows much faster than under addition.

A toy coefficient experiment from the original notebook illustrates why multiplication is much more aggressive than addition:

![Toy coefficient-noise experiment for BFV-style multiplication](/images/blog/bfv/multiplication-noise.png)

That produces the basic **noise budget** picture:

$$
\text{fresh ciphertext}
\rightarrow
\text{addition: modest growth}
\rightarrow
\text{multiplication: large growth}
\rightarrow
\text{relinearization/key switching: extra growth}
\rightarrow
\text{eventual decryption failure if the budget is exhausted}.
$$

Leveled HE chooses parameters large enough for a predetermined multiplicative depth. Fully homomorphic constructions add bootstrapping or related refresh mechanisms so computation can continue beyond a fixed depth.

## 11. BFV versus BGV and CKKS

These schemes share a lattice/RLWE foundation but target different arithmetic models.

- **BFV:** exact modular integer/polynomial arithmetic;
- **BGV:** exact modular arithmetic with a different modulus/noise-management architecture;
- **CKKS:** approximate arithmetic for real/complex values using encoded scale management.

Calling all three simply “Ring-LWE encryption” hides the most important engineering differences.

## 12. What the original notebook got right—and what needed correction

The original material had strong geometric intuition for polynomial rings, scaling, ciphertext growth, and noise. The canonical version corrects several points:

- $x^N+1$ is used for cyclotomic/negacyclic structure, not because it is automatically irreducible modulo every $q$;
- production BFV parameter sizes cannot be inferred from toy brute-force counts such as $3^N$ alone;
- ciphertext multiplication and rescaling/relinearization conventions vary across BFV descriptions;
- security comes from RLWE hardness with carefully specified distributions, not merely from “a huge secret search space.”

For the underlying hardness assumption, read:

[Ring-LWE, Module-LWE, Canonical Embeddings, and Structured Arithmetic](/blog/ring-module-lwe/).
