---
title: "SNARKs, STARKs, and the Zero-Knowledge Proof-System Design Space"
description: "Synthesize the ZK series into a decision map: arithmetizations, commitment backends, trusted versus transparent setup, proof/verifier cost, recursion, post-quantum assumptions, and the difference between succinctness and zero knowledge."
pubDate: "2025-03-07"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Polynomial Commitments"
  - "Cryptographic Engineering"
  - "Post-Quantum Cryptography"
tags:
  - "snark"
  - "stark"
  - "groth16"
  - "plonk"
  - "fri"
  - "kzg"
  - "ipa"
  - "proof-system-comparison"
difficulty: "Advanced"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 13
draft: false
---
There is no single axis called "better ZK." Modern proof systems combine several largely independent design choices:

1. how computation is arithmetized;
2. how prover data is committed;
3. how polynomial/constraint identities are tested;
4. how interaction is removed;
5. how privacy is added;
6. what setup/cryptographic assumptions are accepted;
7. whether recursion is a primary goal.

This final chapter turns the previous twelve articles into one map.

## 1. Layered architecture

A useful generic picture is:

```text
program / relation
      ↓
arithmetization
      ↓
polynomial / oracle identities
      ↓
commitment layer
      ↓
interactive challenge protocol
      ↓
Fiat-Shamir transcript
      ↓
proof object
```

Zero-knowledge masking/randomization intersects several of these layers; it is not always one final switch.

## 2. Arithmetization choices

Different proof systems begin with different representations.

### R1CS/QAP

Natural for Groth16-style preprocessing SNARKs:

$$
(Aw)\circ(Bw)=Cw
$$

then

$$
A_wB_w-C_w=h t.
$$

### PLONKish

Witness columns over an evaluation domain plus selector/custom-gate identities and permutation/lookup arguments.

### AIR

Execution traces plus transition/boundary constraints, especially natural for VM/state-machine style computation.

### Other families

Multilinear, Boolean, binary-field, lookup-heavy, folding-oriented, and specialized arithmetizations all change prover/verifier tradeoffs.

So "SNARK" does not identify one circuit language.

## 3. Commitment backend choices

### KZG

- pairing-based;
- structured reference string;
- very small commitments/openings;
- efficient batching;
- not naturally post-quantum.

### IPA-based

- ordinary discrete-log group;
- no KZG-style toxic-waste trapdoor;
- logarithmic folding proofs;
- attractive for some recursive constructions;
- not post-quantum under discrete-log assumptions.

### Merkle + FRI

- hash/coding-theoretic transparent design;
- larger oracle/query proof objects in many practical parameter regimes;
- no structured secret setup;
- attractive for post-quantum-oriented designs with appropriately sized hash security.

## 4. Representative systems

| System family | Typical arithmetization | Commitment / low-degree backend | Setup | Succinct verification | PQ-oriented? |
|---|---|---|---|---|---|
| Groth16 | R1CS → QAP | pairing/QAP encodings | circuit-specific structured CRS | very strong | No |
| PLONK + KZG | PLONKish | KZG | universal/updatable structured SRS | strong | No |
| IPA/Halo-style | arithmetic/PLONK-like variants | IPA-based PCS | no KZG toxic-waste setup | design-dependent, recursion-friendly | No |
| STARK | AIR | Merkle + FRI/IOP | transparent | polylog/query-based | Yes, hash-based assumptions |

The table is architectural, not a performance benchmark. Real performance depends on circuit shape, implementation, field/curve, proof batching, hardware, lookup use, recursion depth, and security parameters.

## 5. Proof size is only one metric

A three-group-element Groth16 proof is exceptionally compact, but choosing a proof system also requires considering:

- setup ceremony cost/risk;
- prover memory;
- FFT/NTT/MSM/hash workload;
- verifier pairings versus hash/field work;
- public-input size;
- proof-generation latency;
- batching/aggregation;
- recursion cost;
- hardware/GPU parallelism;
- post-quantum assumptions.

A larger proof may be the better system if transparency or prover scalability dominates the application.

## 6. "Trusted setup" has multiple meanings

At least three distinct cases should be separated:

1. **circuit-specific setup** — new parameters for each exact circuit/QAP;
2. **universal/updatable structured setup** — reusable within capacity, but still contains structured trapdoor relations;
3. **transparent setup** — parameters derive from public randomness/hash constants without secret toxic waste.

Calling both (1) and (2) merely "trusted setup" hides an important operational difference.

## 7. Zero knowledge is not guaranteed by the acronym

Common mistakes include:

- assuming any SNARK is zero knowledge;
- assuming a STARK is automatically zero knowledge;
- assuming a polynomial commitment hides the polynomial;
- assuming Merkle commitment hides trace values;
- assuming an educational prover that verifies one equation implements the full privacy theorem.

Always locate the **blinding/masking mechanism** and the corresponding simulator/security definition.

## 8. Fiat–Shamir is another independent layer

Most practical systems are presented as non-interactive proofs, but their conceptual protocols often contain verifier challenges.

Those challenges are generated from a transcript hash.

Therefore implementation security depends on:

- canonical transcript serialization;
- domain separation;
- inclusion of public statements/parameters;
- challenge ordering;
- correct random-oracle/QROM theorem for the protocol.

This is why transcript code deserves the same review discipline as field arithmetic.

## 9. ZK-friendly hashes connect two series

Hash choice can dominate proving cost in Merkle-heavy or in-circuit hashing workloads.

General-purpose SHA-2/SHA-3 remain excellent byte-oriented hashes, but field-native proof systems may prefer algebraic permutations such as Poseidon-, Rescue-, or Griffin-style designs when their reviewed parameter sets match the arithmetization.

CryptoCave's [Griffin article](/blog/griffin-algebraic-hashes/) explains this design pressure from the hash-function side.

## 10. Mathematical prerequisites connect across CryptoCave

The ZK path is not isolated. It reuses earlier material:

- [finite fields](/series/finite-fields-polynomial-arithmetic/);
- [linear algebra](/series/linear-algebra-foundations/);
- interpolation and FFT/NTT ideas from [secret sharing and polynomial tools](/series/secret-sharing-polynomial-tools/);
- elliptic-curve pairings from [elliptic-curve mathematics](/series/elliptic-curve-mathematics/);
- hashes/Merkle structures from [Hash Functions & MACs](/series/hash-functions-macs/).

This is exactly why the site was reorganized into prerequisite series rather than one flat list of cryptographic techniques.

## 11. A practical selection checklist

Before choosing a proof system, write down:

### Trust model

- Is a structured setup acceptable?
- Must setup be transparent?
- Is an updatable ceremony operationally acceptable?

### Computation shape

- arithmetic-heavy or bit-heavy?
- huge repeated trace or one static circuit?
- many lookups?
- dynamic program/VM?

### Performance priority

- prover latency?
- proof bytes?
- verifier latency?
- on-chain gas/cost?
- memory?

### Composition

- recursion required?
- aggregation only?
- incremental computation?

### Long-term assumptions

- pairing/discrete-log assumptions acceptable?
- post-quantum target?
- hash-only transparency preferred?

There is no universally correct answer.

## 12. What was retained from the uploaded ZKP archive

The source batch contained valuable educational experiments around:

- Fiat–Shamir identification;
- R1CS/QAP and Pinocchio/Groth16;
- PLONK;
- STARK/FRI;
- Merkle-based oracle tutorials;
- several modern research repositories.

The canonical site does **not** copy those repositories or bundled PDFs. Their useful concepts were merged into this ordered series, while provenance is recorded in the ZKP cleanup ledger.

The result is one coherent reference path instead of a directory of unrelated proof-system experiments.
