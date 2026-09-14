---
title: "From Base OT to Modern OT Extension: Naor–Pinkas, IKNP, and the MPC View"
description: "Place Rabin and 1-out-of-2 OT in the larger MPC landscape, correct a mislabeled old Naor-Pinkas implementation, and explain why practical systems separate expensive base OT from high-volume OT extension."
pubDate: "2025-05-14"
updatedDate: "2026-09-12"
topics:
  - "MPC"
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
  - "Post-Quantum Cryptography"
tags:
  - "oblivious-transfer"
  - "naor-pinkas"
  - "iknp"
  - "ot-extension"
  - "secure-computation"
difficulty: "Advanced"
series: "Oblivious Transfer"
seriesOrder: 3
status: "Reference"
draft: false
---
The most useful way to understand oblivious transfer today is not as one isolated RSA trick but as an **interface** used by secure-computation protocols.

A system may need thousands or millions of transfers of the form

$$
(m_0,m_1;b)\longmapsto m_b
$$

while hiding $b$ from the sender and $m_{1-b}$ from the receiver. Repeating a heavy public-key protocol for every transfer is usually too expensive.

## Naor–Pinkas context

Naor and Pinkas developed efficient protocols for 1-out-of-$N$, $k$-out-of-$N$, and adaptive oblivious transfer. Their work belongs in the progression from basic OT to efficient selection from larger databases.

One file in the recovered Part 2 archive was labeled **"Naor–Pinkas scheme"**, but the implementation actually combined RSA exponentiation with polynomial interpolation in a way that does not faithfully identify the standard Naor–Pinkas construction. I have therefore **not** published that code as a Naor–Pinkas implementation.

This is an example of why consolidation must include technical relabeling, not just moving files.

## Base OT

A **base OT** is a relatively small number of expensive public-key OTs used to establish correlated secret material.

The exact primitive can be built from classical assumptions such as Diffie–Hellman/trapdoor permutations or from post-quantum assumptions, depending on the system.

## OT extension

OT extension turns a modest number of base OTs into a much larger number of OTs using mostly symmetric operations such as hashes, pseudorandom expansion, matrix transposition, and XOR.

The IKNP construction is the canonical historical example of this idea. Later protocols add active/malicious security and reduce communication further.

The high-level architecture is therefore:

```text
expensive public-key base OTs
            ↓
small correlated seed material
            ↓
symmetric-key OT extension
            ↓
very many application OTs
```

This separation is why OT became practical as a workhorse for MPC.

## OT and secure computation

OT is powerful enough to support general secure computation. Informally, once parties can perform hidden-choice transfers securely, they can build protocols where one party supplies encrypted labels/values and another obtains only the branch corresponding to its private input.

Different MPC families use OT differently, but the primitive repeatedly appears in:

- garbled circuits;
- private set operations;
- secure inference and private analytics;
- preprocessing for arithmetic/Boolean MPC;
- correlated randomness generation.

## Malicious security

A semi-honest OT proof assumes both parties follow the protocol while trying to infer extra information. Malicious security must additionally detect or tolerate malformed messages and inconsistent behavior.

That often requires consistency checks, correlation-robust hashing assumptions, commitments, or zero-knowledge techniques depending on the protocol.

So the phrase "OT works" is incomplete without a model:

- semi-honest or malicious?
- static or adaptive corruption?
- random OT, correlated OT, chosen-message OT?
- classical or post-quantum assumptions?

## Post-quantum direction

Modern OT research can instantiate base OT from lattice/LWE-style assumptions and then use symmetric-key extension on top. This is conceptually separate from simply replacing RSA with "some lattice trapdoor" in the educational 1-out-of-2 transcript; a secure post-quantum OT needs a construction and proof designed for that setting.

## What was kept from the old material

The Part 2 source bundle is preserved in the FULL master for provenance, but the mislabeled polynomial/RSA code is not part of the active GitHub experiment tree. The canonical site keeps:

- the correct Rabin OT algebra;
- the correct 1-out-of-2 trapdoor-permutation intuition;
- a research-oriented map from base OT to OT extension;
- an explicit warning where the recovered naming was not reliable.

That is more useful than preserving a misleading directory name.

## References

- Even, Goldreich, Lempel, early 1-out-of-2 OT from trapdoor permutations.
- Naor and Pinkas, *Computationally Secure Oblivious Transfer*.
- Ishai, Kilian, Nissim, Petrank (IKNP), OT extension.
