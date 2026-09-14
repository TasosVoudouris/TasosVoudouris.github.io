---
title: "Arithmetization I: Arithmetic Circuits, Witnesses, and R1CS"
description: "Translate computation into finite-field constraints, derive Rank-1 Constraint Systems, inspect public/private witness layout, and understand what R1CS does—and does not—provide to a proof system."
pubDate: "2025-02-27"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Finite Fields"
  - "Linear Algebra"
  - "Cryptographic Engineering"
tags:
  - "arithmetization"
  - "r1cs"
  - "arithmetic-circuit"
  - "witness"
  - "constraints"
  - "finite-field"
difficulty: "Intermediate"
status: "Validated"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 5
sourcePath: "experiments/zero-knowledge/r1cs"
draft: false
---
General-purpose proof systems need a language in which "the computation was correct" can be expressed algebraically. One of the most influential such languages is the **Rank-1 Constraint System (R1CS)**.

R1CS is **not itself a zero-knowledge proof system**. It is an arithmetization: a way to encode computation as equations over a field.

## 1. Start with an arithmetic circuit

Take the relation

$$
x^3+4x^2-xz+4=y.
$$

Suppose $y$ is public while $x,z$ are private. Introduce intermediate wires

$$
x_2=x^2,\qquad x_3=x^3.
$$

Then the computation can be written as multiplication constraints:

$$
\begin{aligned}
x\cdot x &= x_2,\\
x_2\cdot x &= x_3,\\
(-x)\cdot z &= y-x_3-4x_2-4.
\end{aligned}
$$

All arithmetic is performed in a finite field $\mathbb F_p$.

## 2. The witness vector

Collect a constant wire plus all values into

$$
w=(1,x,x_2,x_3,z,y).
$$

The system designer decides which coordinates are public and which are private. The prover supplies a full satisfying witness; the proof system later exposes only the intended public inputs.

## 3. Rank-1 form

Each constraint has the shape

$$
\langle A_i,w\rangle\cdot\langle B_i,w\rangle
=
\langle C_i,w\rangle.
$$

Here $A_i,B_i,C_i$ are field vectors selecting linear combinations of witness entries.

Stacking all constraints gives matrices

$$
A,B,C\in\mathbb F_p^{m\times n}.
$$

The witness is valid exactly when, componentwise,

$$
(Aw)\circ(Bw)=Cw.
$$

The symbol $\circ$ denotes Hadamard (elementwise) multiplication.

## 4. Why this is useful

R1CS turns arbitrary arithmetic computation into a uniform algebraic condition:

- linear combinations are cheap to describe;
- every nonlinear constraint contains one multiplication;
- the same backend can prove many different programs after compilation.

This is the bridge from source-level computation to polynomial proof machinery.

## 5. Constraint cost is not CPU cost

A native CPU instruction that is cheap outside a proof may require many field constraints inside one.

Bitwise operations are a standard example. To prove that a value is a bit, one can constrain

$$
b(b-1)=0.
$$

A 32-bit word operation may therefore require dozens or hundreds of field-level constraints depending on the arithmetization.

This is why [arithmetization-oriented hash functions](/blog/griffin-algebraic-hashes/) can be attractive in proof systems: they replace bit-heavy logic with low-degree field operations.

## 6. Public inputs versus witness values

A frequent implementation mistake is to confuse "present in the witness vector" with "private."

The complete witness may be arranged as

$$
w=(1,\text{public inputs},\text{private inputs},\text{intermediate wires}).
$$

The proof backend treats the public prefix differently during verification. This layout is a protocol/compiler convention and must match the proving/verifying key.

## 7. Field wraparound changes the relation

If the source program intended integer arithmetic but the circuit works over $\mathbb F_p$, then

$$
p+1=1.
$$

Range constraints are required whenever wraparound would change the intended semantics.

For example, proving that an integer lies in $[0,2^{32})$ requires a bit/range decomposition or another range-proof technique. Merely storing the value in a large field does not enforce its integer range.

## 8. R1CS is only the arithmetization layer

A satisfying witness proves nothing to an external verifier until a proof protocol is placed on top.

R1CS alone does not provide:

- soundness against a cheating prover;
- zero knowledge;
- succinctness;
- commitment to witness values;
- non-interactivity.

Those properties arrive from later layers such as QAP-based SNARKs, polynomial commitments, transcript challenges, and proof-system-specific randomization.

## 9. Other arithmetizations exist

Modern systems may use:

- PLONKish custom gates;
- AIR transition constraints;
- lookup arguments;
- multilinear extensions;
- Boolean or binary-field constraint systems.

R1CS remains valuable because it makes the central idea of arithmetization unusually explicit.

### Companion experiment

```bash
python experiments/zero-knowledge/r1cs/r1cs_demo.py
```

It checks the example relation over $\mathbb F_{97}$ and confirms that modifying the public output invalidates the witness.
