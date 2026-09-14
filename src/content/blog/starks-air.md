---
title: "STARKs: Execution Traces, AIR, Composition Polynomials, and Transparency"
description: "Build a transparent STARK architecture from execution traces and AIR constraints through low-degree extensions, composition polynomials, Merkle commitments, Fiat–Shamir challenges, and FRI-based low-degree testing."
pubDate: "2025-03-04"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Finite Fields"
  - "Hash Functions"
  - "Cryptographic Engineering"
tags:
  - "stark"
  - "air"
  - "execution-trace"
  - "composition-polynomial"
  - "merkle-tree"
  - "transparent-proof"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 10
sourcePath: "experiments/zero-knowledge/fri"
draft: false
---
A STARK-style system takes a very different route from pairing-based SNARKs. Instead of encoding polynomial evaluations in elliptic-curve groups with a secret structured setup, it builds an **oracle proof** from finite-field algebra, error-correcting-code proximity, Merkle commitments, and hash-derived challenges.

The result is **transparent**: there is no toxic-waste trapdoor ceremony.

## 1. Start with an execution trace

Suppose a computation evolves state

$$
s_0,s_1,\ldots,s_{T-1}.
$$

Arrange these states as rows of a trace table. Each column tracks one register/value across time.

For a Fibonacci-style toy computation,

$$
a_{i+2}=a_{i+1}+a_i,
$$

one can store consecutive values and later prove that every transition obeys the recurrence.

## 2. Algebraic Intermediate Representation (AIR)

AIR expresses the computation using polynomial constraints.

Two common classes are:

- **transition constraints**, relating neighboring trace rows;
- **boundary constraints**, fixing public input/output or initial/final conditions.

For the Fibonacci relation, a transition constraint could be

$$
T(i+2)-T(i+1)-T(i)=0.
$$

After placing the trace over a multiplicative evaluation domain, this becomes a polynomial identity over field evaluations.

## 3. Interpolate the trace

Each trace column is viewed as evaluations of a low-degree polynomial on a subgroup/domain.

The prover extends it to a larger domain: a **low-degree extension (LDE)**.

This is Reed–Solomon encoding in evaluation form. Redundancy is crucial because later spot checks can detect inconsistent data with meaningful probability.

## 4. Constraint polynomials and zerofiers

Transition constraints should vanish on the subset of trace-domain points where they apply.

If a constraint polynomial $C(X)$ vanishes on a set with vanishing polynomial $Z(X)$, then a valid trace makes

$$
Q(X)=\frac{C(X)}{Z(X)}
$$

a polynomial of controlled degree.

Boundary constraints are handled similarly, often with interpolation polynomials that encode required values at selected points.

## 5. Composition polynomial

A real computation has many constraints. Proving each one separately would be expensive.

The verifier derives random coefficients

$$
\alpha_1,\ldots,\alpha_k
$$

and the prover combines normalized constraint expressions into one **composition polynomial**:

$$
C_{\text{comp}}(X)=\sum_{j=1}^{k}\alpha_j Q_j(X).
$$

If any underlying constraint is invalid, a random linear combination makes it difficult for errors to cancel systematically.

## 6. Commit to evaluation oracles

The prover evaluates relevant polynomials on the extended domain and Merkle-commits to those vectors.

The verifier later requests selected positions and receives:

- trace/composition values;
- neighboring values needed for local checks;
- Merkle authentication paths.

This gives authenticated random access without transmitting the full trace.

## 7. Low degree is the global consistency condition

Local transition checks are not enough. A cheating prover might answer a few sampled positions consistently while the full oracle is arbitrary.

The verifier must also know that the committed evaluation vector is close to a low-degree polynomial.

This is the job of **FRI**, studied in the next chapter.

## 8. Fiat–Shamir makes the protocol non-interactive

The conceptual STARK is an interactive oracle protocol. In deployment, Merkle roots and opened values are absorbed into a transcript and verifier challenges/query positions are hash-derived.

This removes interaction in a random-oracle-style security model.

Transcript binding and challenge order therefore matter just as much here as in PLONK.

## 9. Transparent does not mean assumption-free

STARKs avoid structured trusted setup, but they still rely on assumptions and parameter choices:

- collision/preimage properties of cryptographic hashes;
- soundness of the underlying IOP/FRI analysis;
- adequate field/domain sizes and query counts;
- secure Fiat–Shamir compilation;
- correct implementation of Merkle openings and constraint evaluation.

"Transparent" means no secret setup trapdoor is required; it does not mean "no cryptography."

## 10. STARK does not automatically mean zero knowledge

The acronym expands to **Scalable Transparent Argument of Knowledge**. The word "zero-knowledge" is not part of STARK itself.

A bare trace commitment can reveal witness information. A zk-STARK adds masking/randomization so that the oracle data and openings do not leak private trace values beyond the statement.

This correction is important because several educational STARK implementations in the uploaded source focus on computational integrity and low-degree checks, not a complete zero-knowledge layer.

## 11. Post-quantum perspective

Hash-based transparent systems avoid elliptic-curve discrete-log and pairing assumptions. They are therefore commonly considered attractive for post-quantum settings.

That does not make parameters unchanged in a quantum threat model: generic quantum search changes effective hash-security margins, so digest sizes/query parameters must be selected accordingly.

## 12. Source-code caution

The source batch contained a didactic STARK script and multiple older proof-of-concept implementations. Some upstream READMEs explicitly warn that the protocols are educational and may be broken.

CryptoCave keeps the mathematical architecture and a small verified FRI-folding companion rather than bundling those repositories as if they were audited STARK libraries.

### Primary reference

E. Ben-Sasson, I. Bentov, Y. Horesh, M. Riabzev, *Scalable, transparent, and post-quantum secure computational integrity*, 2018.
