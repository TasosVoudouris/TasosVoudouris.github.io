---
title: "PLONK: Gate Polynomials, Permutation Arguments, and Universal Structured Reference Strings"
description: "Derive the PLONKish arithmetization: selector polynomials, witness columns, copy constraints through the permutation grand product, quotient identities, transcript challenges, and KZG-backed universal/updatable setup."
pubDate: "2025-03-03"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Finite Fields"
tags:
  - "plonk"
  - "permutation-argument"
  - "grand-product"
  - "lagrange-basis"
  - "kzg"
  - "universal-setup"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 9
draft: false
---
PLONK changed the practical SNARK landscape by separating **circuit arithmetization** from a reusable structured reference string more cleanly than circuit-specific preprocessing systems such as Groth16.

The core ideas are worth studying independently of any one implementation.

## 1. Witness columns over an evaluation domain

Choose a multiplicative subgroup/domain

$$
H=\{1,\omega,\omega^2,\ldots,\omega^{n-1}\}
$$

of a finite field.

For each row $i$, the circuit has witness values

$$
a_i,b_i,c_i.
$$

Rather than thinking only in coefficient form, PLONK works naturally with polynomials whose evaluations on $H$ are these columns:

$$
a(\omega^i)=a_i,\qquad b(\omega^i)=b_i,\qquad c(\omega^i)=c_i.
$$

This is one reason the Lagrange/evaluation-basis viewpoint is so central.

## 2. Selector polynomials encode gate types

A common basic PLONK gate equation is

$$
q_L a+q_R b+q_M ab+q_O c+q_C=0.
$$

Each selector $q_*(X)$ is a polynomial whose value at row $i$ chooses the active gate coefficients.

This single template can express addition, multiplication, constants, and many mixed arithmetic relations.

Modern "PLONKish" systems extend this idea with custom gates and lookup arguments, but the selector-polynomial model remains the conceptual foundation.

## 3. Gate constraints alone are not enough

A circuit also needs **copy constraints**: the value on one wire must equal the value reused elsewhere.

Naively checking every equality would destroy the elegance of the polynomial protocol.

PLONK instead encodes wire-copy structure as a permutation of all wire positions.

## 4. The permutation argument

Assign each wire position an identity label. Let the permutation map each occurrence of a logical variable to the next occurrence in its copy cycle.

The prover must show that the multiset of witness values tagged by original identities equals the multiset tagged by permuted identities.

Random challenges $\beta,\gamma$ compress these relations into products such as

$$
\prod_i(a_i+\beta\,\mathrm{id}_{a,i}+\gamma)
$$

versus corresponding factors using permutation labels.

## 5. Grand-product polynomial

Rather than reveal/check the whole product directly, PLONK builds an accumulator polynomial $Z(X)$ satisfying a row-to-row recurrence.

Schematically,

$$
Z(\omega^{i+1})
=
Z(\omega^i)
\frac{\prod\text{original-tag factors}}
     {\prod\text{permuted-tag factors}}.
$$

Boundary conditions such as

$$
Z(1)=1
$$

and the final wraparound force consistency of the accumulated product.

This **grand-product argument** is one of PLONK's defining techniques.

## 6. Combine constraints with verifier randomness

Gate identities, permutation identities, and boundary terms are combined using a fresh transcript challenge often denoted $\alpha$.

The prover forms a quotient polynomial by dividing the combined constraint polynomial by the vanishing polynomial of the evaluation domain:

$$
Z_H(X)=X^n-1.
$$

For a valid witness, the numerator vanishes on every point of $H$, so it is divisible by $Z_H(X)$.

The pattern should now look familiar from QAPs: many local constraints become one global divisibility relation.

## 7. Evaluation challenge

After committing to the relevant witness/quotient/permutation polynomials, the transcript derives a random evaluation point $\zeta$.

The prover opens committed polynomials at $\zeta$ and often at the shifted point

$$
\zeta\omega.
$$

These evaluations let the verifier check the polynomial identities without reading the full polynomials.

## 8. Polynomial commitment backend

Classic PLONK is commonly explained with KZG commitments.

This gives:

- succinct polynomial commitments/openings;
- efficient batching of many evaluations;
- a structured reference string containing powers of a hidden trapdoor.

The critical setup improvement over Groth16 is that the SRS can be **universal and updatable** for circuits up to a configured size/degree rather than regenerated for each exact circuit.

Universal does not mean unbounded: the SRS still has a maximum supported degree and fixed cryptographic parameters.

## 9. Where zero knowledge enters

The algebraic gate/permutation checks provide soundness structure, not automatically privacy.

PLONK-style provers add **blinding/randomization polynomials** so that committed witness polynomials do not reveal private information through their degree-limited structure or openings.

This matters for the uploaded source material: one educational `py_plonk` README explicitly says that privacy-preserving parts were intentionally omitted. That code can teach polynomial/permutation verification, but it must not be presented as a complete zero-knowledge PLONK implementation.

## 10. Fiat–Shamir transcript order

A non-interactive PLONK proof derives several challenges from successive commitments:

```text
commit witness polynomials
  ↓
β, γ
  ↓
commit permutation accumulator
  ↓
α
  ↓
commit quotient pieces
  ↓
ζ
  ↓
submit evaluations
  ↓
aggregation/opening challenges
```

The exact transcript depends on the protocol variant. Reordering commitments or omitting public inputs from challenge derivation changes the protocol and may break security.

## 11. PLONK versus "PLONKish"

Today many systems are described as PLONKish while adding:

- custom gates;
- lookup arguments;
- different polynomial commitment schemes;
- different permutation/lookup accumulators;
- recursion-oriented curve/field choices.

The canonical article therefore focuses on the enduring structure rather than equating every modern PLONK-derived system with the 2019 paper line-by-line.

### Primary reference

A. Gabizon, Z. J. Williamson, O. Ciobotaru, *PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge*, 2019.
