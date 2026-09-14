---
title: "Zero-Knowledge Foundations: Relations, Witnesses, Soundness, and Simulation"
description: "Build the formal vocabulary of zero-knowledge proofs: NP relations, witnesses, completeness, soundness, arguments of knowledge, simulators, and the distinctions that modern SNARK/STARK terminology often hides."
pubDate: "2025-02-23"
updatedDate: "2026-09-14"
topics:
  - "Zero-Knowledge Proofs"
  - "Mathematical Foundations"
  - "Cryptography Fundamentals"
tags:
  - "zero-knowledge"
  - "interactive-proofs"
  - "simulation"
  - "soundness"
  - "proof-of-knowledge"
  - "np-relations"
difficulty: "Intermediate"
status: "Reviewed"
series: "Zero-Knowledge Proof Systems"
seriesOrder: 1
draft: false
---
Zero knowledge is not a synonym for "privacy technology," and a zk-SNARK is not merely a short encrypted proof. The clean way to begin is with a **relation**.

Let $R(x,w)$ be an efficiently computable predicate. The public value $x$ is the **statement** (or instance) and $w$ is a **witness**. We define the language

$$
L_R=\{x:\exists w\text{ such that }R(x,w)=1\}.
$$

A prover wants to convince a verifier that $x\in L_R$ without revealing the witness $w$.

## 1. Public statement versus private witness

Examples make the abstraction concrete:

- $x$ may be a public group element and $w$ its discrete logarithm;
- $x$ may be a public commitment and $w$ an opening;
- $x$ may contain a hash digest and $w$ a preimage satisfying extra constraints;
- $x$ may describe an arithmetic computation and $w$ all private inputs plus intermediate wire values.

The statement itself is normally **not hidden** by the definition of zero knowledge. A protocol can prove a public fact while hiding only the witness. If the application also wants to hide parts of the statement, they must be encoded as witness data or protected by another mechanism.

## 2. Completeness

An honest prover with a valid witness should convince an honest verifier:

$$
R(x,w)=1\quad\Longrightarrow\quad
\Pr[V\text{ accepts after interacting with }P(w)]\approx 1.
$$

Some protocols have perfect completeness; others permit a negligible completeness error.

Completeness is the easy property. It says the system works when everybody follows the protocol.

## 3. Soundness: false statements should not be provable

Soundness asks what happens when $x\notin L_R$. Even a malicious prover $P^*$ should not convince the verifier except with small probability:

$$
\Pr[V\leftrightarrow P^*\text{ accepts }x\notin L_R]\leq \varepsilon.
$$

Here an important vocabulary distinction appears.

A **proof system** usually has information-theoretic soundness against an unbounded cheating prover. An **argument system** may rely on computational assumptions, so soundness is required only against efficient adversaries.

Most practical SNARKs are therefore **arguments**, despite the casual phrase "ZK proof."

## 4. Knowledge soundness is stronger

Ordinary soundness says a false statement should not be accepted. A **proof/argument of knowledge** aims at a stronger intuition: if a prover convinces the verifier, then in an appropriate formal sense the prover must "know" a witness.

This is modeled using an **extractor**. Roughly, for every successful efficient prover there should exist an extractor that can recover a witness $w$ satisfying

$$
R(x,w)=1.
$$

Extraction is not necessarily a normal algorithm that watches one production transcript. It is part of the security definition and may rewind or otherwise interact with the adversary depending on the model.

The "K" in **SNARK** stands for *knowledge* only when the construction satisfies the corresponding knowledge-soundness definition.

## 5. What zero knowledge actually means

The central definition is simulation.

A verifier should not learn anything from the real interaction that it could not have generated without the witness. Formally, there exists a simulator $S$ whose output is indistinguishable from the verifier's real view.

We distinguish:

- **perfect zero knowledge** — simulated and real distributions are identical;
- **statistical zero knowledge** — they are statistically close;
- **computational zero knowledge** — efficient distinguishers cannot tell them apart under computational assumptions.

The simulator is why the slogan "the proof reveals nothing" has mathematical content. We do not inspect a transcript and merely decide that it *looks* harmless; we compare the real protocol with a distribution that does not use the secret witness.

## 6. Honest-verifier ZK is not full ZK

Many three-move protocols are easy to simulate when the verifier's challenge is honestly sampled. This is called **honest-verifier zero knowledge (HVZK)**.

HVZK is weaker than security against an arbitrary malicious verifier. A malicious verifier may choose challenges as a function of previous messages, use malformed parameters, or correlate multiple sessions.

This distinction becomes important in the next chapter on Sigma protocols.

## 7. Zero knowledge is independent of succinctness

Several properties are often bundled together in modern terminology, but they are logically separate:

| Property | Question |
|---|---|
| Completeness | Does an honest valid witness verify? |
| Soundness | Can a false statement be accepted? |
| Knowledge soundness | Does convincing behavior imply knowledge of a witness? |
| Zero knowledge | Does the verifier learn anything about the witness? |
| Non-interactivity | Is the proof sent in one prover message? |
| Succinctness | Is the proof/verifier much smaller/faster than redoing the computation? |
| Transparency | Can setup avoid secret trapdoor material? |

A protocol can be zero knowledge but not succinct. It can be succinct but not zero knowledge. It can be transparent but interactive. The acronyms do not make these distinctions disappear.

## 8. Proofs versus arguments versus SNARKs and STARKs

A useful reading map is:

- **ZK proof/argument**: focuses on privacy plus soundness;
- **NIZK**: non-interactive zero-knowledge proof/argument in a model with setup or another source of public randomness;
- **SNARG**: succinct non-interactive argument;
- **SNARK**: succinct non-interactive argument of knowledge;
- **zk-SNARK**: a SNARK additionally satisfying a zero-knowledge property;
- **STARK**: a scalable transparent argument of knowledge; zero knowledge is an additional property achieved by appropriate masking/randomization, not by the acronym alone.

## 9. Historical anchor

Goldwasser, Micali, and Rackoff introduced the formal notion of knowledge complexity and zero knowledge in the 1980s. Goldreich, Micali, and Wigderson then demonstrated the remarkable generality of zero-knowledge proofs for NP under cryptographic assumptions.

Modern systems look very different operationally, but the same core questions remain: **what is the relation, why is cheating hard, where is the witness knowledge enforced, and what simulator explains privacy?**

## 10. What comes next

The next article studies **Sigma protocols**, where these abstract properties become concrete algebra. They are the cleanest place to understand three ideas that reappear throughout proof systems:

1. commitment to prover randomness;
2. unpredictable verifier challenge;
3. a response whose algebra can be both verified and extracted.

### Primary references

- S. Goldwasser, S. Micali, C. Rackoff, *The Knowledge Complexity of Interactive Proof-Systems*, STOC 1985.
- O. Goldreich, S. Micali, A. Wigderson, *Proofs that Yield Nothing But their Validity and a Methodology of Cryptographic Protocol Design*, FOCS 1986.
