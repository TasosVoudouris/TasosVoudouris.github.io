---
title: "Lattices & Lattice-Based Cryptography X: From Module-LWE to ML-KEM and ML-DSA"
description: "The bridge from LWE and Module-LWE theory to standardized post-quantum cryptography: ML-KEM, ML-DSA, their algebraic foundations, security roles, implementation structure, and the status of FN-DSA."
pubDate: "2026-09-13"
updatedDate: "2026-09-16"

topics:
  - "Post-Quantum Cryptography"
  - "Public-Key Cryptography"
  - "Lattice Theory"
  - "Cryptographic Engineering"

tags:
  - "ml-kem"
  - "kyber"
  - "ml-dsa"
  - "dilithium"
  - "module-lwe"
  - "module-sis"
  - "fips-203"
  - "fips-204"
  - "post-quantum"

difficulty: "Advanced"
status: "Reviewed"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 10
draft: false
---

The previous chapters developed a progression:

$$
\text{lattices}
\rightarrow
\text{SIS}
\rightarrow
\text{LWE}
\rightarrow
\text{Ring-LWE}
\rightarrow
\text{Module-LWE}.
$$

These are not merely theoretical constructions.

Their descendants now appear inside standardized post-quantum cryptography.

As of September 2026, two central finalized NIST lattice-based standards are:

* **FIPS 203 — ML-KEM**, derived from CRYSTALS-Kyber;
* **FIPS 204 — ML-DSA**, derived from CRYSTALS-Dilithium.

They use related module-lattice mathematics, but they solve fundamentally different cryptographic problems.

ML-KEM establishes a shared secret:

$$
\boxed{
\text{public key}
\rightarrow
\text{ciphertext}
+
\text{shared secret}.
}
$$

ML-DSA authenticates data:

$$
\boxed{
\text{message}
+
\text{private key}
\rightarrow
\text{digital signature}.
}
$$

They should therefore not be thought of as two interfaces around the same cryptographic construction.

Their common foundation is module-lattice arithmetic.

Their mechanisms are different.

---

## Contents

- [1. From Module-LWE to standards](#1-from-module-lwe-to-standards)
- [2. The common polynomial-ring setting](#2-the-common-polynomial-ring-setting)
- [3. Why module structure is practical](#3-why-module-structure-is-practical)
- [4. ML-KEM: what a KEM actually does](#4-ml-kem-what-a-kem-actually-does)
- [5. The Module-LWE core of ML-KEM](#5-the-module-lwe-core-of-ml-kem)
- [6. From noisy equations to encryption](#6-from-noisy-equations-to-encryption)
- [7. Why K-PKE decryption works](#7-why-k-pke-decryption-works)
- [8. From the PKE component to ML-KEM](#8-from-the-pke-component-to-ml-kem)
- [9. Decapsulation and implicit rejection](#9-decapsulation-and-implicit-rejection)
- [10. ML-KEM parameter sets](#10-ml-kem-parameter-sets)
- [11. ML-DSA: a different cryptographic problem](#11-ml-dsa-a-different-cryptographic-problem)
- [12. ML-DSA key generation](#12-ml-dsa-key-generation)
- [13. Fiat-Shamir with aborts](#13-fiat-shamir-with-aborts)
- [14. ML-DSA signing](#14-ml-dsa-signing)
- [15. Why ML-DSA verification works](#15-why-ml-dsa-verification-works)
- [16. Why rejection sampling matters](#16-why-rejection-sampling-matters)
- [17. Hints, compression, and high bits](#17-hints-compression-and-high-bits)
- [18. ML-DSA parameter sets](#18-ml-dsa-parameter-sets)
- [19. MLWE, MSIS, and SelfTargetMSIS](#19-mlwe-msis-and-selftargetmsis)
- [20. Same ring shape, different arithmetic choices](#20-same-ring-shape-different-arithmetic-choices)
- [21. From mathematics to a FIPS implementation](#21-from-mathematics-to-a-fips-implementation)
- [22. What about Falcon and FN-DSA?](#22-what-about-falcon-and-fn-dsa)
- [23. Current NIST status](#23-current-nist-status)
- [24. The abstraction boundary](#24-the-abstraction-boundary)
- [25. The bigger picture](#25-the-bigger-picture)
- [Further reading](#further-reading)

---

## 1. From Module-LWE to standards

The underlying mathematical idea remains the one developed in the earlier LWE chapters.

Start with

$$
b=As+e.
$$

Replace scalar entries modulo \(q\) by elements of a polynomial quotient ring

$$
R_q.
$$

Then use vectors and matrices over that ring:

$$
A\in R_q^{k\times \ell},
\qquad
s\in R_q^\ell,
\qquad
e\in R_q^k.
$$

The noisy relation becomes

$$
\boxed{
b=As+e.
}
$$

This is Module-LWE-style arithmetic.

At first sight, the formula has barely changed.

But every entry now represents an entire polynomial containing hundreds of modular coefficients.

So a small matrix over \(R_q\) implicitly represents a much larger structured linear transformation over \(\mathbb Z_q\).

This is the bridge between the theory of LWE and practical post-quantum cryptography.

---

## 2. The common polynomial-ring setting

Both ML-KEM and ML-DSA use degree-\(256\) negacyclic polynomial arithmetic.

Conceptually, their rings have the form

$$
R_q
=
\mathbb Z_q[X]/(X^{256}+1).
$$

Thus

$$
X^{256}=-1.
$$

Polynomial multiplication is therefore negacyclic.

But the two standards use different moduli.

For ML-KEM,

$$
\boxed{
q=3329.
}
$$

For ML-DSA,

$$
\boxed{
q=8380417.
}
$$

So even though both schemes operate using \(256\)-coefficient polynomial objects, they do not use the same finite arithmetic environment.

This is important.

Statements such as

> “Kyber and Dilithium use the same ring”

are only approximately true at the structural level.

More precisely, both use quotient rings of the form

$$
\mathbb Z_q[X]/(X^{256}+1),
$$

but with different \(q\), different distributions, different module dimensions, and different cryptographic operations.

---

## 3. Why module structure is practical

Suppose an ordinary LWE construction used an unstructured matrix

$$
A\in\mathbb Z_q^{N\times N}.
$$

Explicitly storing \(A\) could require approximately

$$
N^2\log_2q
$$

bits.

Module-lattice cryptography avoids this cost in two ways.

First, ring multiplication compresses large structured transformations into polynomial elements.

Second, the public matrices themselves can often be generated pseudorandomly from a short seed.

Thus an implementation need not transmit every coefficient of \(A\).

Instead:

$$
\boxed{
\text{short seed}
\rightarrow
\text{XOF}
\rightarrow
A.
}
$$

The public key can therefore contain:

* a seed defining \(A\);
* a much smaller set of module elements carrying the actual noisy public relation.

This is one of the engineering reasons module lattices became practical.

We gain:

$$
\text{compact public material},
$$

$$
\text{fast NTT arithmetic},
$$

and

$$
\text{small module dimensions}.
$$

The cryptographic assumptions, however, are now assumptions about **module lattices**, not arbitrary unstructured LWE matrices.

---

# Part I — ML-KEM

## 4. ML-KEM: what a KEM actually does

ML-KEM is a **key-encapsulation mechanism**.

It is not a general file-encryption algorithm.

A KEM has three main algorithms:

$$
\operatorname{KeyGen},
\qquad
\operatorname{Encaps},
\qquad
\operatorname{Decaps}.
$$

### Key generation

One party generates:

$$
(ek,dk)
\leftarrow
\operatorname{KeyGen}().
$$

Here:

* \(ek\) is the **encapsulation key** and may be public;
* \(dk\) is the **decapsulation key** and must remain secret.

---

### Encapsulation

A sender uses \(ek\):

$$
(c,K)
\leftarrow
\operatorname{Encaps}(ek).
$$

The sender obtains:

* a ciphertext \(c\);
* a shared secret \(K\).

The ciphertext is transmitted.

The shared secret is not.

---

### Decapsulation

The receiver computes

$$
K'
=
\operatorname{Decaps}(dk,c).
$$

For a valid ciphertext produced by encapsulation,

$$
K'=K
$$

with overwhelming probability.

The parties can then feed the resulting shared secret into symmetric cryptography.

Conceptually,

$$
\boxed{
\text{ML-KEM}
\rightarrow
\text{shared key establishment}
}
$$

followed by something such as

$$
\boxed{
\text{AEAD / symmetric protocol}
}
$$

for actual bulk-data protection.

That is the correct abstraction.

---

## 5. The Module-LWE core of ML-KEM

Strip away the byte encodings, hashing, compression, and KEM transformation for a moment.

The underlying public-key structure resembles

$$
\boxed{
t=As+e.
}
$$

Here

$$
A\in R_q^{k\times k},
$$

while

$$
s,e\in R_q^k
$$

are small module vectors.

The matrix \(A\) is pseudorandomly generated.

The secret \(s\) and error \(e\) are sampled from small distributions.

Thus the public relation is precisely the Module-LWE picture developed in the previous chapters:

$$
\boxed{
\text{apparently random module equations}
+
\text{small hidden secret/error}.
}
$$

ML-KEM uses

$$
R_q
=
\mathbb Z_{3329}[X]/(X^{256}+1).
$$

Its parameter sets use module ranks

$$
k=2,\;3,\;4.
$$

So the public relation becomes increasingly large as the parameter set increases.

---

## 6. From noisy equations to encryption

The internal encryption component can be understood through a beautifully simple algebraic derivation.

Suppose the public relation is

$$
t=As+e.
$$

To encrypt an encoded message \(\mu\), sample another short vector \(y\), together with small errors

$$
e_1,
\qquad
e_2.
$$

Compute approximately

$$
u
=
A^Ty+e_1
$$

and

$$
v
=
t^Ty+e_2+\mu.
$$

The ciphertext contains compressed representations of

$$
(u,v).
$$

Now substitute

$$
t=As+e.
$$

Then

$$
v
=
(As+e)^Ty+e_2+\mu.
$$

Therefore,

$$
v
=
s^TA^Ty
+
e^Ty
+
e_2
+
\mu.
$$

The receiver knows \(s\), so compute

$$
v-s^Tu.
$$

Since

$$
u=A^Ty+e_1,
$$

we obtain

$$
s^Tu
=
s^TA^Ty+s^Te_1.
$$

Subtracting,

$$
v-s^Tu
=
\mu
+
e^Ty
+
e_2
-
s^Te_1.
$$

Thus

$$
\boxed{
v-s^Tu
=
\mu
+
\text{small accumulated noise}.
}
$$

This is the same idea we saw in basic LWE encryption.

The large secret-dependent terms cancel.

Only the encoded message plus small noise remains.

That is the algebraic heart of Kyber-style encryption.

---

## 7. Why K-PKE decryption works

If the total noise

$$
e^Ty+e_2-s^Te_1
$$

remains inside the decoding region, the receiver can identify the encoded message.

In the real scheme there is additional approximation noise caused by compression and decompression.

So the effective error is better thought of as

$$
\boxed{
\text{LWE noise}
+
\text{compression noise}.
}
$$

Parameters must guarantee that this total perturbation very rarely crosses a decoding boundary.

This creates the same security/correctness tension that appeared in ordinary LWE:

$$
\boxed{
\text{enough uncertainty for security}
}
$$

while still ensuring

$$
\boxed{
\text{sufficiently small total error for decoding}.
}
$$

ML-KEM therefore has an extremely small but nonzero theoretical decapsulation-failure probability.

This is not an implementation crash.

It is the probability that valid encapsulation and decapsulation mathematically derive different secrets because the accumulated noise crosses the decoding threshold.

---

## 8. From the PKE component to ML-KEM

The previous equations describe the public-key encryption component underlying ML-KEM.

FIPS 203 calls this component **K-PKE**.

But there is an essential distinction:

$$
\boxed{
\text{K-PKE}
\neq
\text{approved standalone encryption scheme}.
}
$$

K-PKE exists only as an internal component of ML-KEM.

The standardized object is the KEM.

Why is another layer required?

Because basic public-key encryption security is not enough for a modern network protocol.

In particular, a KEM must resist active attacks involving maliciously constructed ciphertexts.

ML-KEM therefore applies a Fujisaki–Okamoto-style transformation around its underlying encryption mechanism.

The conceptual progression is

$$
\boxed{
\text{Module-LWE encryption}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{deterministic encryption under derived randomness}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{re-encryption validation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{CCA-secure KEM design}.
}
$$

This wrapper is not an implementation detail.

It is part of the security construction.

---

## 9. Decapsulation and implicit rejection

ML-KEM decapsulation illustrates why a standardized cryptographic algorithm contains substantially more machinery than the equation

$$
t=As+e.
$$

Given ciphertext \(c\), decapsulation first obtains a candidate internal message

$$
m'.
$$

It then deterministically derives:

$$
(K',r')
$$

from \(m'\) and public-key-related data.

Using \(r'\), it recomputes the ciphertext that *should* have been produced:

$$
c'
=
\operatorname{K\!-\!PKE.Encrypt}(ek,m',r').
$$

Then compare:

$$
c'
\stackrel{?}{=}
c.
$$

### Valid path

If

$$
c'=c,
$$

the candidate shared secret is retained.

### Invalid path

If

$$
c'\neq c,
$$

ML-KEM performs **implicit rejection**.

Instead of returning an explicit failure signal, it derives an alternative secret from secret fallback material and the ciphertext.

Conceptually:

$$
\boxed{
c=c'
\Rightarrow
K_{\text{real}}
}
$$

whereas

$$
\boxed{
c\neq c'
\Rightarrow
K_{\text{fallback}}.
}
$$

The attacker therefore does not receive a direct decryption-validity oracle.

This is a critical distinction from a toy LWE decryptor.

A real ML-KEM implementation must reproduce this behavior correctly.

---

## 10. ML-KEM parameter sets

All standardized ML-KEM parameter sets use

$$
n=256,
\qquad
q=3329.
$$

The remaining parameters change.

| Parameter     | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
| ------------- | ---------: | ---------: | ----------: |
| \(k\)         |          2 |          3 |           4 |
| \(\eta_1\)    |          3 |          2 |           2 |
| \(\eta_2\)    |          2 |          2 |           2 |
| \(d_u\)       |         10 |         10 |          11 |
| \(d_v\)       |          4 |          4 |           5 |
| NIST category |          1 |          3 |           5 |

The names

$$
512,\;768,\;1024
$$

are **parameter-set names**.

They are not RSA-style modulus sizes.

The corresponding standardized object sizes are:

| Parameter set | Encapsulation key | Decapsulation key | Ciphertext | Shared secret |
| ------------- | ----------------: | ----------------: | ---------: | ------------: |
| ML-KEM-512    |             800 B |            1632 B |      768 B |          32 B |
| ML-KEM-768    |            1184 B |            2400 B |     1088 B |          32 B |
| ML-KEM-1024   |            1568 B |            3168 B |     1568 B |          32 B |

The standard also reports theoretical decapsulation-failure estimates of approximately

$$
2^{-138.8},
\qquad
2^{-164.8},
\qquad
2^{-174.8}
$$

for the three parameter sets respectively.

So ML-KEM correctness should not be described as literally probability-one correctness.

It is **overwhelming-probability correctness**.

---

# Part II — ML-DSA

## 11. ML-DSA: a different cryptographic problem

ML-DSA is not an encryption scheme.

It is a digital-signature algorithm.

Its purpose is to provide:

* message integrity;
* signer authentication;
* resistance to signature forgery.

The standardized scheme is derived from CRYSTALS-Dilithium.

At a high level, ML-DSA belongs to the **Fiat-Shamir with aborts** family and is Schnorr-like in structure.

The broad pattern is:

$$
\boxed{
\text{commit}
\rightarrow
\text{challenge}
\rightarrow
\text{short response}.
}
$$

This should feel familiar from identification protocols and Schnorr signatures.

What changes is that all operations now occur over module lattices.

---

## 12. ML-DSA key generation

ML-DSA works over

$$
R_q
=
\mathbb Z_{8380417}[X]/(X^{256}+1).
$$

Generate a pseudorandom matrix

$$
A\in R_q^{k\times\ell}.
$$

Sample short secret vectors

$$
s_1\in R_q^\ell
$$

and

$$
s_2\in R_q^k.
$$

The central public relation is

$$
\boxed{
t=As_1+s_2.
}
$$

This should immediately look familiar.

It is an MLWE-style relation.

The public value \(t\), however, is not stored directly.

Instead it is decomposed:

$$
t
=
2^d t_1+t_0.
$$

The high part

$$
t_1
$$

is placed in the public key.

The low part

$$
t_0
$$

is retained in the private key.

Thus the public key is essentially

$$
\boxed{
(\rho,t_1),
}
$$

where \(\rho\) is the seed used to regenerate \(A\).

The private key contains the information needed for signing, including

$$
s_1,
\qquad
s_2,
\qquad
t_0,
$$

and cryptographic seeds.

Again we see the same engineering principle:

$$
\boxed{
\text{do not transmit }A;
\text{ transmit a short seed defining }A.
}
$$

---

## 13. Fiat-Shamir with aborts

To understand ML-DSA, ignore encoding details temporarily.

The signer wants to prove knowledge of short vectors related to

$$
t=As_1+s_2
$$

without revealing them.

Sample a temporary masking vector

$$
y.
$$

Compute

$$
w=Ay.
$$

The high-order part of \(w\) acts as the commitment:

$$
w_1
=
\operatorname{HighBits}(w).
$$

Now derive a challenge by hashing the message representative together with the commitment:

$$
\widetilde c
=
H(\mu\parallel w_1).
$$

From this hash, derive a sparse challenge polynomial

$$
c.
$$

Finally compute the response

$$
\boxed{
z=y+c s_1.
}
$$

This looks extremely similar to a Schnorr response:

$$
z
=
r+c x.
$$

But there is a problem.

The distribution of

$$
z=y+c s_1
$$

may depend subtly on the secret \(s_1\).

If every candidate response were released, repeated signatures could reveal information about the secret.

This is why ML-DSA does something that ordinary textbook Schnorr does not:

$$
\boxed{
\text{it sometimes aborts and resamples}.
}
$$

---

## 14. ML-DSA signing

A simplified signing round is:

### 1. Sample masking vector

Choose a moderately short

$$
y\in R_q^\ell.
$$

### 2. Form commitment

Compute

$$
w=Ay.
$$

Extract

$$
w_1=\operatorname{HighBits}(w).
$$

### 3. Compute challenge

Hash the message representation and \(w_1\):

$$
\widetilde c
=
H(\mu\parallel w_1).
$$

Derive from \(\widetilde c\) a sparse challenge polynomial

$$
c.
$$

Its coefficients lie in

$$
\{-1,0,1\}
$$

and its Hamming weight is controlled by the parameter \(\tau\).

### 4. Form response

Compute

$$
\boxed{
z=y+c s_1.
}
$$

### 5. Check bounds

The signer verifies that \(z\) and several low-order quantities remain inside carefully selected bounds.

For example, one central condition is conceptually

$$
\|z\|_\infty
<
\gamma_1-\beta.
$$

If a condition fails:

$$
\boxed{
\text{discard this attempt and start again}.
}
$$

### 6. Construct hint

The signer computes a compact hint

$$
h
$$

that helps the verifier recover the correct high-order bits despite the compressed public key.

The resulting signature essentially contains

$$
\boxed{
(\widetilde c,z,h).
}
$$

---

## 15. Why ML-DSA verification works

The public relation is

$$
t=As_1+s_2.
$$

Since

$$
t
=
2^d t_1+t_0,
$$

we have

$$
2^d t_1
=
t-t_0.
$$

The signer produced

$$
z=y+c s_1.
$$

The verifier computes

$$
w'
=
Az-c\,2^dt_1.
$$

Substitute \(z\):

$$
w'
=
A(y+c s_1)-c\,2^dt_1.
$$

Therefore,

$$
w'
=
Ay
+
cAs_1
-
c(t-t_0).
$$

Using

$$
t=As_1+s_2,
$$

we obtain

$$
w'
=
Ay
+
cAs_1
-
cAs_1
-
cs_2
+
ct_0.
$$

Hence

$$
\boxed{
w'
=
w-cs_2+ct_0.
}
$$

This equation is the heart of ML-DSA verification.

The large secret-dependent \(As_1\) contribution cancels.

What remains is the original commitment

$$
w=Ay
$$

plus controlled small corrections.

The hint \(h\) enables the verifier to reconstruct the same relevant high-order information

$$
w_1
$$

that the signer used.

Then the verifier recomputes

$$
\widetilde c'
=
H(\mu\parallel w_1')
$$

and checks

$$
\boxed{
\widetilde c'=\widetilde c.
}
$$

It also verifies the required norm bounds on \(z\).

That is the module-lattice analogue of the familiar Schnorr verification mechanism.

---

## 16. Why rejection sampling matters

The equation

$$
z=y+c s_1
$$

contains the private vector \(s_1\).

Even though \(y\) acts as a mask, the resulting distribution can be statistically influenced by the secret near the boundaries of the allowed region.

Therefore the signer must not release every computed response.

Instead, it releases only responses satisfying carefully designed conditions.

Conceptually:

$$
y
\rightarrow
z=y+c s_1
$$

followed by

$$
\boxed{
\text{distribution-safe?}
}
$$

If not:

$$
\boxed{
\text{reject and resample }y.
}
$$

This is why the scheme is known as **Fiat-Shamir with aborts**.

The abort is not an error condition.

It is part of normal signature generation.

Its purpose is to ensure that the distribution of released signatures does not reveal useful information about the signing secret.

---

## 17. Hints, compression, and high bits

ML-DSA contains two related forms of decomposition.

During key generation,

$$
t
=
2^dt_1+t_0.
$$

Only \(t_1\) is included in the public key.

This reduces public-key size.

During signing, quantities such as

$$
w
$$

are also decomposed into high and low parts.

Why?

Because signature verification does not need all exact coefficients of \(w\).

It needs a stable coarse representation.

The signer computes

$$
w_1
=
\operatorname{HighBits}(w).
$$

But the verifier computes a nearby quantity

$$
w'
=
w-cs_2+ct_0.
$$

Those small corrections can occasionally push coefficients across a high-bit rounding boundary.

The hint

$$
h
$$

records just enough information for the verifier to resolve these boundary cases.

Thus the signature does not transmit the entire missing low-order information.

It transmits only a compact correction signal.

The conceptual mechanism is:

$$
\boxed{
\text{compressed public data}
+
\text{small hint}
\rightarrow
\text{correct high-bit reconstruction}.
}
$$

This is an excellent example of cryptographic engineering and mathematical design interacting directly.

---

## 18. ML-DSA parameter sets

ML-DSA provides three standardized parameter sets:

$$
\text{ML-DSA-44},
\qquad
\text{ML-DSA-65},
\qquad
\text{ML-DSA-87}.
$$

Unlike ML-KEM's names, these labels expose the matrix dimensions.

For ML-DSA-\(k\ell\),

$$
A\in R_q^{k\times\ell}.
$$

Thus:

| Parameter set | \((k,\ell)\) | NIST category |
| ------------- | -----------: | ------------: |
| ML-DSA-44     |    \((4,4)\) |             2 |
| ML-DSA-65     |    \((6,5)\) |             3 |
| ML-DSA-87     |    \((8,7)\) |             5 |

All use

$$
q=8380417
$$

and polynomial degree

$$
n=256.
$$

Their standardized encoded sizes are:

| Parameter set | Public key | Private key | Signature |
| ------------- | ---------: | ----------: | --------: |
| ML-DSA-44     |     1312 B |      2560 B |    2420 B |
| ML-DSA-65     |     1952 B |      4032 B |    3309 B |
| ML-DSA-87     |     2592 B |      4896 B |    4627 B |

Several other parameters control the scheme, including:

$$
\eta,
\qquad
\tau,
\qquad
\gamma_1,
\qquad
\gamma_2,
\qquad
\beta,
\qquad
\omega.
$$

They regulate quantities such as:

* secret coefficient ranges;
* challenge weight;
* mask ranges;
* rejection thresholds;
* low-bit decomposition;
* maximum hint weight.

So increasing an ML-DSA security level is not simply “make \(q\) larger.”

In fact, \(q\) remains fixed.

The security/performance profile changes through the complete parameter set.

---

## 19. MLWE, MSIS, and SelfTargetMSIS

This is an important point where simplified descriptions often become inaccurate.

It is reasonable pedagogically to say that ML-DSA combines:

$$
\text{LWE-style hidden secrets}
$$

with

$$
\text{SIS-style short relations}.
$$

But the standardized security discussion is more precise.

FIPS 204 states that ML-DSA security is based on:

$$
\boxed{
\text{MLWE}
}
$$

and a nonstandard Module-SIS-related problem called

$$
\boxed{
\text{SelfTargetMSIS}.
}
$$

So we should distinguish three layers.

### Generic intuition

$$
\text{MLWE}
\leftrightarrow
\text{noisy hidden structure}.
$$

$$
\text{MSIS}
\leftrightarrow
\text{short modular relations}.
$$

### Scheme-specific security argument

ML-DSA does not simply assume arbitrary textbook MSIS.

The signature security proof gives rise to the more specialized

$$
\operatorname{SelfTargetMSIS}
$$

problem.

### Why both viewpoints appear

The public key

$$
t=As_1+s_2
$$

has MLWE structure.

Meanwhile, producing forged short response relations naturally leads toward short-vector/module-SIS-style hardness.

This is precisely why learning SIS before LWE was useful.

The two families reappear together inside real signature security arguments.

---

## 20. Same ring shape, different arithmetic choices

ML-KEM and ML-DSA both use

$$
X^{256}+1.
$$

But their NTT arithmetic is not identical.

### ML-KEM

$$
q=3329.
$$

Since

$$
3329-1
=
3328
=
13\cdot256,
$$

we have

$$
256\mid(q-1)
$$

but

$$
512\nmid(q-1).
$$

Thus \(\mathbb F_{3329}\) does not contain the primitive \(512\)-th root required for complete linear splitting of

$$
X^{256}+1.
$$

As discussed in the Ring-LWE chapter, ML-KEM therefore uses its characteristic incomplete-NTT / quadratic-component structure.

### ML-DSA

For ML-DSA,

$$
q=8380417.
$$

The standard uses a primitive \(512\)-th root of unity modulo \(q\).

Thus its NTT structure differs.

This is another reason that one should not write generic code saying

> “both are degree-256 lattice schemes, therefore their polynomial arithmetic is interchangeable.”

The quotient polynomial may have the same form.

The modular arithmetic does not.

---

## 21. From mathematics to a FIPS implementation

At the mathematical level, ML-KEM may be summarized by

$$
t=As+e.
$$

ML-DSA may be summarized by

$$
t=As_1+s_2
$$

and

$$
z=y+c s_1.
$$

None of those equations is remotely enough to produce a conforming or secure implementation.

A standardized implementation also depends on exact definitions of:

* byte encoding;
* bit ordering;
* polynomial encoding;
* compression and decompression;
* rejection sampling;
* XOF domain separation;
* seed expansion;
* matrix generation;
* NTT representation;
* coefficient bounds;
* public-key validation;
* ciphertext validation;
* signature-length validation;
* hint encoding;
* destruction of sensitive intermediate values;
* randomness generation;
* deterministic versus hedged signing behavior.

For ML-KEM, one must additionally implement:

$$
\text{re-encryption checking}
$$

and

$$
\text{implicit rejection}.
$$

For ML-DSA, one must correctly implement:

$$
\text{Fiat-Shamir with aborts}
$$

and the associated high-bit/low-bit/hint machinery.

Thus:

$$
\boxed{
\text{mathematical equivalence}
\neq
\text{implementation equivalence}.
}
$$

This is the abstraction boundary between understanding the mathematics and implementing the standard.

---

### ML-DSA signing modes

FIPS 204 provides a default **hedged** signing mode.

Fresh randomness is mixed into the generation of the signing mask.

There is also an optional deterministic form.

Conceptually:

$$
\boxed{
\text{hedged}
=
\text{private state}
+
\text{message}
+
\text{fresh randomness}
}
$$

whereas deterministic signing derives the signing randomness without fresh external randomness.

The hedged form provides additional robustness against certain failures of deterministic state or derivation mechanisms.

The standard also specifies **HashML-DSA**, a pre-hash form.

However, when direct signing is appropriate, the ordinary “pure” ML-DSA form is the preferred construction.

These details again show why

$$
z=y+c s_1
$$

is only the beginning of the implementation story.

---

## 22. What about Falcon and FN-DSA?

Falcon provides a useful contrast.

It is also a lattice-based digital signature scheme.

But it does not follow the Dilithium/ML-DSA route.

Falcon uses structured **NTRU lattices** and a trapdoor-based hash-and-sign construction involving discrete Gaussian sampling.

Very roughly:

$$
\boxed{
\text{ML-DSA}
:
\text{module-lattice Fiat-Shamir with aborts}
}
$$

whereas

$$
\boxed{
\text{Falcon/FN-DSA}
:
\text{NTRU lattice}
+
\text{trapdoor sampling}
+
\text{hash-and-sign}.
}
$$

This connects directly back to the NTRU chapters.

The NTRU lattice is no longer merely an object to attack.

It can also be used as a trapdoor structure by the legitimate signer.

Falcon is known for compact signatures and fast verification, but its sampling and implementation requirements are considerably more intricate than ML-DSA's relatively simple integer/module arithmetic.

NIST selected Falcon for standardization under the name **FN-DSA**.

The intended standard is FIPS 206.

As of September 2026, it is still under development and has not become a final FIPS.

Therefore we should distinguish carefully between:

$$
\boxed{
\text{Falcon as the selected cryptographic design}
}
$$

and

$$
\boxed{
\text{FN-DSA as the eventual NIST-standardized specification}.
}
$$

Until FIPS 206 is finalized, one should not assume that every Falcon implementation detail will necessarily be identical to the eventual standard.

---

## 23. Current NIST status

As checked in September 2026:

### FIPS 203

**ML-KEM**

Status:

$$
\boxed{
\text{Final}
}
$$

Published:

$$
13\text{ August }2024.
$$

It specifies:

$$
\text{ML-KEM-512},
\quad
\text{ML-KEM-768},
\quad
\text{ML-KEM-1024}.
$$

NIST has subsequently published an errata/potential-updates notice identifying material intended for correction in a future revision.

---

### FIPS 204

**ML-DSA**

Status:

$$
\boxed{
\text{Final}
}
$$

Published:

$$
13\text{ August }2024.
$$

It specifies:

$$
\text{ML-DSA-44},
\quad
\text{ML-DSA-65},
\quad
\text{ML-DSA-87}.
$$

NIST has also published an errata/potential-updates notice containing several minor issues intended for correction in a future revision.

---

### SP 800-227

NIST has also finalized

**SP 800-227 — Recommendations for Key-Encapsulation Mechanisms**.

This document addresses the broader operational use of KEMs.

That distinction is useful:

$$
\boxed{
\text{FIPS 203}
=
\text{ML-KEM algorithm specification}
}
$$

whereas

$$
\boxed{
\text{SP 800-227}
=
\text{general KEM usage guidance}.
}
$$

---

### FIPS 206

**FN-DSA**, derived from Falcon.

Status as of September 2026:

$$
\boxed{
\text{under development}
}
$$

rather than a finalized FIPS.

This status should be checked again whenever this article is updated.

---

## 24. The abstraction boundary

One of the most common mistakes when learning lattice cryptography is to jump directly from

$$
b=As+e
$$

to

> “I implemented Kyber.”

That skips almost the entire cryptographic construction.

The correct hierarchy is:

$$
\boxed{
\text{Euclidean lattice geometry}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{hard lattice problems}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{SIS / LWE}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Ring / Module structure}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{primitive construction}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{KEM or signature transformation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{encoding + compression + hashes + validation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{standardized algorithm}.
}
$$

For ML-KEM:

$$
\text{MLWE}
\rightarrow
\text{module PKE}
\rightarrow
\text{FO-style KEM}
\rightarrow
\text{FIPS 203}.
$$

For ML-DSA:

$$
\text{MLWE / short relations}
\rightarrow
\text{Fiat-Shamir with aborts}
\rightarrow
\text{compression + hints}
\rightarrow
\text{FIPS 204}.
$$

Every level solves a different problem.

Skipping those levels makes both the mathematics and the implementation much harder to reason about correctly.

---

## 25. The bigger picture

The complete journey through the series is now becoming visible.

We began with lattices as geometric objects:

$$
L=B\mathbb Z^n.
$$

Then q-ary lattices gave us modular structure.

SIS introduced short modular relations:

$$
Az\equiv0\pmod q,
\qquad
\|z\|\text{ small}.
$$

LWE introduced hidden noisy relations:

$$
b=As+e.
$$

Ring-LWE introduced polynomial structure:

$$
b=as+e.
$$

Module-LWE generalized this to small matrices over polynomial rings:

$$
b=As+e,
\qquad
A\in R_q^{k\times\ell}.
$$

NTRU showed another structured-lattice path:

$$
fh\equiv g\pmod q.
$$

And now standardized cryptography combines these ideas into complete protocols.

For ML-KEM:

$$
\boxed{
\text{Module-LWE}
}
$$

$$
\Downarrow
$$

$$
\boxed{
t=As+e
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{noisy module encryption}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{CCA-secure KEM transformation}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{ML-KEM / FIPS 203}.
}
$$

For ML-DSA:

$$
\boxed{
\text{MLWE + short-relation hardness}
}
$$

$$
\Downarrow
$$

$$
\boxed{
t=As_1+s_2
}
$$

$$
\Downarrow
$$

$$
\boxed{
z=y+c s_1
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{Fiat-Shamir with aborts + hints}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{ML-DSA / FIPS 204}.
}
$$

This is the main lesson of the chapter:

> **modern post-quantum standards are not isolated algorithms. They are the final engineering layer of a long mathematical chain beginning with lattice geometry, passing through average-case hardness assumptions, structured algebra, and carefully designed cryptographic transformations.**

Understanding the equation

$$
b=As+e
$$

is therefore necessary.

But it is not sufficient.

The real transition from lattice theory to production cryptography happens when we understand how that equation interacts with:

$$
\text{sampling},
$$

$$
\text{compression},
$$

$$
\text{rounding},
$$

$$
\text{hashing},
$$

$$
\text{rejection},
$$

$$
\text{encoding},
$$

and

$$
\text{validation}.
$$

That is where a hardness problem becomes a cryptographic standard.

---

## Further reading

The principal standards and references for this chapter are:

* NIST, **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard**, 2024.
* NIST, **FIPS 204: Module-Lattice-Based Digital Signature Standard**, 2024.
* NIST, **SP 800-227: Recommendations for Key-Encapsulation Mechanisms**, 2025.
* Roberto Avanzi et al., **CRYSTALS-Kyber Algorithm Specifications and Supporting Documentation**.
* Shi Bai et al., **CRYSTALS-Dilithium Algorithm Specifications and Supporting Documentation**.
* Adeline Langlois and Damien Stehlé, **Worst-Case to Average-Case Reductions for Module Lattices**.
* NIST, **Post-Quantum Cryptography Standardization Project**.

For FN-DSA, the authoritative reference should remain the current NIST material until FIPS 206 is finalized.

---

The next natural question is no longer:

> how do these schemes use lattices?

We now know that.

The next question is:

> **how do we analyze their concrete security against lattice reduction?**

That brings us back to the machinery glimpsed in the toy NTRU attack:

$$
\text{Gram-Schmidt}
\rightarrow
\text{LLL}
\rightarrow
\text{BKZ}
\rightarrow
\text{GSO profiles}
\rightarrow
\text{root-Hermite factors}
\rightarrow
\text{enumeration and sieving}.
$$

Those tools explain what a statement such as

> “this parameter set resists lattice attacks”

actually means computationally.
