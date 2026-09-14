---
title: "Recursive Proofs: Composition, Accumulation, IPA Commitments, and Halo"
description: "Understand proof recursion as proving verification itself, distinguish recursion from aggregation and batching, study curve/field compatibility, and explain Halo's path to practical recursive composition without a trusted setup."
pubDate: "2025-03-06"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Elliptic-Curve Cryptography"
tags:
  - "recursion"
  - "recursive-proofs"
  - "halo"
  - "ipa"
  - "accumulation"
  - "proof-composition"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 12
draft: false
---
A proof system becomes dramatically more composable when it can efficiently prove statements about **other proofs**.

The key idea is simple to state:

> instead of verifying proof $\pi_0$ externally, build a circuit that runs the verifier for $\pi_0$, then prove that this verification circuit accepted.

That is recursive proof composition.

## 1. Verification becomes a circuit

Suppose a verifier computes

$$
V(x,\pi)=1.
$$

Construct an arithmetic circuit $C_V$ implementing $V$.

A new prover can then produce

$$
\pi_1\;\text{ proving }\;C_V(x,\pi_0)=1.
$$

If $\pi_1$ is itself verifiable inside the same or a compatible proof system, the process can continue recursively.

## 2. Why recursion is useful

Recursion enables patterns such as:

- compressing a long chain of state transitions into one final proof;
- incremental verifiable computation;
- rollup/block aggregation;
- proof-carrying data;
- private programs that repeatedly update authenticated state.

Instead of verifier cost growing with every historical step, one final proof can attest to the accumulated computation.

## 3. Recursion is not the same as aggregation

These terms are often blurred.

- **Batch verification**: verify many proofs together more cheaply than independently.
- **Aggregation**: combine evidence from many proofs into a smaller object/check.
- **Recursion**: one proof system proves that another proof verifier accepted.
- **Accumulation/folding**: maintain a compact accumulator/relaxed relation whose correctness is periodically or finally proven.

A scheme can support one without supporting all the others.

## 4. The field mismatch problem

A proof verifier performs arithmetic in some scalar/base fields. To verify that proof *inside a circuit*, those operations must themselves be efficiently representable in the outer circuit field.

For pairing-based systems, recursively checking pairings can be expensive.

One classical strategy uses **cycles of elliptic curves** where the scalar field of one curve matches the base field needed by the other. That makes alternating recursion more natural, but finding secure efficient curve cycles is restrictive.

## 5. Why succinct verification matters

If verifying one proof inside a circuit costs more than simply re-executing the original computation, recursion provides little benefit.

The recursion threshold is therefore governed by:

- verifier circuit size;
- commitment-opening verification cost;
- non-native field arithmetic;
- transcript hashing inside the circuit;
- curve operations/pairings;
- proof size and witness-generation overhead.

This is why polynomial commitment design strongly affects recursive-proof engineering.

## 6. Halo's key direction

Halo demonstrated practical recursive proof composition **without a trusted setup** using an inner-product-based polynomial commitment approach rather than pairing-based KZG.

Its central insight avoids forcing the recursive circuit to redo a large linear-time verifier operation for every proof. Instead, expensive operations can be represented through an accumulation/amortization mechanism and checked across proofs.

This made ordinary prime-order curve cycles practical for recursive composition without pairing-friendly curves or a KZG toxic-waste setup.

## 7. IPA commitments and recursion

In an IPA-style commitment, opening verification recursively folds vectors/group relations.

The proof is larger and verification tradeoffs differ from constant-size KZG openings, but the absence of pairings and the structure of the verifier can be attractive for recursion.

The correct comparison is therefore not simply:

```text
KZG = small, IPA = large
```

but rather:

```text
which verifier arithmetic must be embedded inside the recursive circuit?
```

## 8. Accumulation and folding as a broader pattern

Modern recursive systems increasingly use **folding/accumulation** ideas: instead of producing a fully succinct proof after every step, combine several relation instances into one relaxed/accumulated instance and defer expensive compression.

Conceptually:

$$
\text{instance}_1+\text{instance}_2
\longrightarrow
\text{one folded instance}.
$$

Repeated folding can make incremental computation efficient, followed by a final succinct proof.

Specific systems differ substantially in security model and algebra, so "folding" should not be treated as one universal protocol.

## 9. Zero knowledge across recursion

If inner proofs contain private witnesses, recursion must preserve the desired privacy definition.

Potential leakage can arise from:

- unblinded intermediate commitments;
- public accumulator state;
- deterministic transcripts;
- exposing verifier inputs that were assumed private;
- reusing randomness across recursive steps.

Recursion compresses verification; it does not automatically strengthen zero knowledge.

## 10. Trusted setup is also backend-dependent

"Recursive SNARK" does not imply either trusted or transparent setup.

A recursive system may use:

- circuit-specific pairing SNARKs;
- universal KZG-based PLONKish systems;
- IPA-based commitments;
- FRI/STARK-style transparent proofs;
- hybrid recursion layers.

The setup property comes from the chosen protocol/PCS, not from recursion itself.

## 11. A useful architecture diagram

```text
step computation
    ↓
proof π0
    ↓
verify π0 inside next circuit
    ↓
proof π1
    ↓
verify π1 inside next circuit
    ↓
...
    ↓
one final proof
```

Folding systems modify the middle by accumulating several steps before final compression, but the goal remains the same: keep externally visible verification small as the computation grows.

### Primary reference

S. Bowe, J. Grigg, D. Hopwood, *Recursive Proof Composition without a Trusted Setup (Halo)*, 2019.
