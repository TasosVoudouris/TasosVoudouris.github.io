---
title: "Auditing Toy Polynomial Commitments: Pedersen Coefficients, Fake Pairings, and KZG Pitfalls"
description: "Use recovered Pedersen, IPA, and KZG experiments as a code-audit case study: distinguish vector commitments from succinct polynomial commitments, identify unsafe generator derivation and fake pairing logic, and separate a real KZG equation from a toy that only resembles one."
pubDate: "2025-05-21"
updatedDate: "2026-09-14"
topics:
  - "Polynomial Commitments"
  - "Zero-Knowledge Proofs"
  - "Cryptographic Engineering"
tags:
  - "pedersen-commitment"
  - "kzg"
  - "ipa"
  - "pairings"
  - "code-audit"
  - "hash-to-curve"
difficulty: "Advanced"
status: "Research Note"
draft: false
---
The secret-sharing archive also contained a collection of Pedersen, IPA, and KZG experiments. They do **not** form another secret-sharing series. Their natural home is the polynomial-commitment side of CryptoCave.

They are particularly useful as a code-audit lesson because several snippets look cryptographically sophisticated while implementing a weaker or simply different object.

## 1. Coefficient-wise Pedersen commitments

Suppose

$$
f(X)=\sum_{i=0}^d f_iX^i.
$$

One experiment commits separately to coefficients:

$$
C_i=f_iG+\gamma_iH.
$$

Then anyone can form

$$
\sum_i u^iC_i
=
f(u)G+\left(\sum_i\gamma_i u^i\right)H.
$$

This is a valid linear relation and can support an evaluation check if the blinding evaluation is revealed appropriately.

But it is **not a succinct KZG-style polynomial commitment**. The commitment contains $O(d)$ group elements rather than one constant-size group element.

Calling every commitment to polynomial coefficients a "polynomial commitment scheme" without stating its size/interface hides this distinction.

## 2. A concrete generator bug

One recovered Pedersen helper constructed `vector_len + 1` generators, then used

```python
random_points[vector_len - 1]
```

for the blinding factor.

That reuses the same generator as the final vector coordinate instead of using the extra independent generator at index `vector_len`.

Conceptually the commitment should look like

$$
C=\sum_{i=0}^{n-1}v_iG_i+rH
$$

with $H$ independent of all $G_i$.

Generator independence is not cosmetic: accidental known relations can destroy binding/hiding properties.

## 3. Naive hash-to-curve is not a standard hash-to-curve

The helper generated candidate points by hashing a string to an $x$ coordinate and incrementing until $x^3+b$ had a square root.

That can produce points, but it is not a substitute for a standardized hash-to-curve construction. A real implementation must consider:

- uniformity;
- domain separation;
- subgroup/cofactor handling;
- canonical encodings;
- curve-specific map requirements.

For educational fixed generators, explicitly deriving them with a reviewed hash-to-curve suite is preferable.

## 4. The "KZG with field multiplication" experiment

The Sage `KZG.sage` experiment defines a function named `e` roughly as multiplication in $\mathbb F_p$.

That is not a cryptographic bilinear pairing between source groups

$$
e:G_1\times G_2\to G_T.
$$

Therefore an equation that syntactically resembles KZG verification does not become KZG merely because the function is called `e`.

This is the most important cleanup decision for that file: **retain it as a negative teaching example, not as a KZG implementation**.

## 5. What real KZG needs

For an SRS based on hidden $\tau$, a commitment is conceptually

$$
C=[f(\tau)]_1.
$$

To open $f(z)=y$, define

$$
q(X)=\frac{f(X)-y}{X-z}
$$

and prove

$$
\pi=[q(\tau)]_1.
$$

A pairing checks

$$
e(C-[y]_1,[1]_2)
=
e(\pi,[\tau-z]_2).
$$

The cryptographic content lies in the group encodings, pairing properties, SRS/trapdoor assumptions, subgroup validation, and transcript/serialization rules.

## 6. The more faithful pairing-based Python experiment

Another recovered implementation uses BLS12-381 operations and actual pairings. It is much closer to KZG algebra and even supports multi-point quotient openings.

But it remains an educational prototype because its setup:

- samples the trapdoor locally;
- uses general-purpose pseudorandomness rather than a ceremony;
- keeps setup generation in the same process;
- does not address serialization/subgroup/network boundaries;
- is explicitly marked "not audited" in its own source.

That is a healthy warning and we preserve it.

## 7. Toxic waste really matters

One experiment intentionally retains `alpha` and then explores forging behavior.

That is exactly the right lesson: if the KZG trapdoor remains known, binding can collapse because the adversary can exploit knowledge of the hidden evaluation point.

A trusted setup is not secure because the parameters "look random". It is secure only under the assumption that the toxic-waste secret is unavailable after setup, or under an updatable ceremony where at least one contribution remains unknown.

## 8. IPA language cleanup

The archive also labels several vector-commitment experiments as "inner product commitment" or "Bulletproof-style".

We should distinguish:

- a Pedersen vector commitment;
- an inner-product relation;
- an inner-product **argument** with logarithmic recursive folding;
- a full Bulletproof construction;
- an IPA-based polynomial commitment.

Sharing vocabulary does not make the protocols interchangeable.

## 9. Where these experiments belong

The cleaned taxonomy is:

- VSS/Feldman/Pedersen sharing commitments → **Threshold Cryptography Engineering**;
- KZG/IPA polynomial commitments → **Zero-Knowledge Proof Systems**;
- these flawed/partial code samples → this **Cryptographic Engineering research note**;
- secret sharing itself → **Secret Sharing & Polynomial Tools**.

## 10. Takeaway

Cryptographic code often fails at the boundary between "the algebraic equation seems to work" and "the implemented object has the security definition we are naming."

The audit checklist is:

```text
What primitive is claimed?
What is the formal interface?
What are the groups/fields?
Are generators independent?
Is hash-to-curve standard?
Is the pairing real and type-correct?
What trapdoor/setup assumptions exist?
What exactly was tested?
```

That discipline prevents a toy equality check from being mistaken for a production polynomial-commitment scheme.
