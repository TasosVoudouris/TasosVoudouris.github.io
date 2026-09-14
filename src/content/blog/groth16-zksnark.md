---
title: "Groth16: Pairing-Based Preprocessing zk-SNARKs from QAPs"
description: "Follow the Groth16 architecture from QAP witness polynomials through a circuit-specific CRS, three-group-element proofs, pairing verification, public-input handling, zero-knowledge randomization, and trusted-setup risk."
pubDate: "2025-03-02"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Elliptic-Curve Cryptography"
tags:
  - "groth16"
  - "zk-snark"
  - "qap"
  - "pairings"
  - "trusted-setup"
  - "crs"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 8
draft: false
---
Groth16 is one of the clearest examples of how a modern-looking succinct proof can emerge from the older QAP/pairing blueprint.

Its headline result is striking: for an arithmetic-circuit statement, the proof contains only **three group elements**. But that compact surface hides a substantial amount of preprocessing, algebra, and security structure.

## 1. Start from the QAP relation

From the previous chapter, a valid witness gives polynomials satisfying

$$
A_w(X)B_w(X)-C_w(X)=h(X)t(X).
$$

The prover should convince the verifier that this divisibility relation holds while keeping the private witness hidden.

The basic obstacle is that sending all polynomial coefficients would destroy succinctness.

## 2. Structured reference string

Groth16 samples secret setup scalars that are commonly denoted using symbols such as

$$
\tau,\alpha,\beta,\gamma,\delta.
$$

The CRS contains carefully selected group encodings of QAP-related values evaluated at $\tau$.

The verifier sees group elements such as powers/linear combinations encoded in $G_1$ and $G_2$, but should never learn the trapdoor scalars themselves.

This is a **preprocessing SNARK**: the proving/verifying material depends on the circuit/QAP.

## 3. Why two pairing groups appear

Use an asymmetric bilinear pairing

$$
e:G_1\times G_2\to G_T.
$$

Bilinearity gives

$$
e(aP,bQ)=e(P,Q)^{ab}.
$$

This lets the verifier check multiplicative relations among hidden scalar expressions using only group elements.

Groth16 exploits this structure so that a large QAP relation becomes one compact pairing-product equation.

## 4. Public inputs are separated from private witness terms

The verifying key contains encodings corresponding to public-input coefficients.

For public input vector

$$
(1,x_1,\ldots,x_\ell),
$$

the verifier forms one linear combination in $G_1$ from the verification-key elements.

Private witness contributions are absorbed into the prover's proof elements instead of being revealed.

This is why the R1CS/QAP compiler must agree exactly about which wires are public.

## 5. Proof shape

A Groth16 proof is conventionally written

$$
\pi=(A,B,C),
$$

with

$$
A\in G_1,\qquad B\in G_2,\qquad C\in G_1.
$$

This is the source of the famous three-group-element proof size.

The notation is unfortunately overloaded with the earlier QAP polynomials $A(X),B(X),C(X)$; the group proof elements are related to those polynomials but are not literally the same objects.

## 6. Verification equation

At a high level the verifier checks a pairing identity of the form

$$
e(A,B)
=
e(\alpha_1,\beta_2)
\cdot e(\text{public-input combination},\gamma_2)
\cdot e(C,\delta_2).
$$

The exact signs/notation vary between additive and multiplicative presentations, but the architecture is stable:

- one term binds the proof to the setup constants;
- one term accounts for public inputs;
- one term binds the residual private-witness/QAP quotient information.

The verifier therefore performs a small fixed number of pairing operations rather than re-evaluating the original circuit.

## 7. Where zero knowledge comes from

A proof that merely encodes deterministic witness expressions can leak information.

Groth16 adds prover randomness, usually represented by random scalars such as $r,s$, into $A,B,C$ so that witness-dependent encodings are randomized while the pairing identity remains valid.

This distinction is essential:

> QAP satisfaction gives correctness; the Groth16 randomization layer is what supports the zero-knowledge property.

An educational implementation that reproduces the pairing algebra but omits those randomizers should not be called a complete zk-SNARK implementation.

## 8. Trusted setup and toxic waste

The circuit-specific setup is Groth16's most visible operational cost.

If an adversary learns enough trapdoor state from the CRS generation, it may be able to construct false proofs. Setup ceremonies therefore try to guarantee that no participant knows the final toxic waste.

Multi-party ceremonies reduce trust by composing contributions: security can survive if at least one contributor behaves honestly and destroys its secret state.

But this does not make the setup "transparent"; it is still a structured trusted setup model.

## 9. Phase 1 and Phase 2 intuition

Practical ceremonies often separate setup conceptually into:

- a generic powers-of-tau style phase that is reusable up to a degree/capacity;
- a circuit-specific specialization phase producing the final proving/verifying keys.

This separation improves ceremony reuse, but the final Groth16 parameters remain tied to the circuit.

## 10. Why Groth16 remains important

Groth16 is valuable pedagogically because it forces every layer to be explicit:

```text
computation
  ↓
R1CS
  ↓
QAP divisibility
  ↓
CRS encodes evaluations at hidden trapdoors
  ↓
prover randomizes witness-dependent group elements
  ↓
verifier checks one compact pairing product equation
```

Its proof/verifier efficiency remains a benchmark against which other systems are compared.

## 11. What the uploaded code contributes

The source batch contained several Groth16/Pinocchio educational repositories and a long "under the hood" notebook collection. They are useful references, but they are third-party teaching code with different assumptions, libraries, and completeness levels.

The canonical CryptoCave article therefore preserves the mathematics and architecture without copying those repositories wholesale or presenting them as audited implementations.

### Primary reference

J. Groth, *On the Size of Pairing-Based Non-interactive Arguments*, EUROCRYPT 2016. The construction gives a preprocessing SNARK for arithmetic-circuit satisfiability with a proof of three group elements and a constant-size pairing verification equation.
