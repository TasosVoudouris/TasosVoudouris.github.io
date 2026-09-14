---
title: "Griffin and Arithmetization-Oriented Hash Functions"
description: "Explain why proof systems favor field-native permutations, study Griffin’s algebraic design at a high level, and contrast proof-oriented hashes with SHA-2 and SHA-3."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Zero-Knowledge Proofs"
  - "Cryptographic Engineering"
tags:
  - "griffin"
  - "algebraic-hash"
  - "arithmetization"
  - "zkp"
  - "sponge"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 8
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. Why SHA-256 can be expensive inside a proof

Conventional hashes are optimized for CPUs and hardware instructions built from bitwise rotations, XOR, AND, and modular addition. A zero-knowledge proof system often represents computation as constraints over a large prime field (\mathbb F_p). Emulating 32-bit words and bit operations inside that field can require many constraints.

An **arithmetization-oriented** or **ZK-friendly** hash instead works natively on field elements and uses low-degree algebraic operations. The aim is not necessarily to outrun SHA-256 on a laptop. The aim is to reduce the prover/verifier cost of expressing the hash inside a particular proof arithmetization.

This creates an important boundary:

- SHA-256/SHA-3 are mature general-purpose byte hashes with widely standardized encodings.
- Griffin is a family of field permutations and modes with protocol-specific parameters and field-element serialization.
- “Fewer constraints” does not imply “safe under arbitrary parameters.”

## 2. Griffin's setting

The supplied SageMath experiment instantiates Griffin over the Goldilocks prime field

\[
p=2^{64}-2^{32}+1.
\]

Its state contains (t=12) elements of (\mathbb F_p). The experiment reserves (c=4) elements as capacity, so the rate is

\[
r=t-c=8
\]

field elements per absorption step. Because each field element is smaller than (2^{64}), “eight field elements” must not be silently equated with an arbitrary 64-byte string: the byte-to-field encoding and rejection/reduction rules are protocol decisions.

The script targets a 128-bit security level and derives its round count and constants deterministically. These parameters are educational. A deployed protocol should use the exact instance and test vectors selected by its reviewed specification.

## 3. Permutation structure

Griffin combines three layers per round:

1. a nonlinear layer over (\mathbb F_p);
2. an invertible linear diffusion layer;
3. additive round constants (omitted in the final round by this design).

For state (x=(x_0,\ldots,x_{t-1})), the nonlinear layer first applies inverse power and power maps:

\[
x_0\leftarrow x_0^{d^{-1}},\qquad x_1\leftarrow x_1^d,
\]

where (\gcd(d,p-1)=1) and (dd^{-1}\equiv1\pmod{p-1}). That condition makes (x\mapsto x^d) a permutation of the field.

For later coordinates, define a linear expression using the first two updated words and a previous word. In the implementation:

\[
L_i(z_0,z_1,z_2)=(i-1)z_0+z_1+z_2.
\]

Then multiply (x_i) by a quadratic polynomial:

\[
x_i\leftarrow x_i\big(L_i^2+\alpha_iL_i+\beta_i\big).
\]

The exact indices and constants must follow the design. Rearranging in-place updates or taking coefficients from a different parameter set changes the permutation.

## 4. Linear diffusion

The next layer multiplies the state vector by an invertible (t\times t) matrix over (\mathbb F_p):

\[
x\leftarrow Mx.
\]

For widths 3 and 4, the reference construction uses compact explicit matrices. For larger widths supported by the lab, the matrix is assembled from 4-by-4 components and a circulant-like block structure. The purpose is to spread differences among coordinates while remaining efficient in the target arithmetization.

Checking matrix invertibility in the exact field is essential. A matrix that is invertible over integers or another prime field need not be the same object modulo (p).

## 5. Round constants and parameter generation

The lab builds a seed string from

```text
Griffin(p,t,capacity,security_level)
```

and expands it with SHAKE256. Chunks are interpreted as integers and mapped into (\mathbb F_p) to derive (\alpha), (\beta), and additive round constants. Deterministic generation prevents hidden, hand-selected constants and lets independent implementations reproduce an instance.

Determinism alone is not a security proof. The parser, endianness, chunk length, reduction rule, and exact seed format are all consensus-critical. A single changed comma or capitalization creates different constants.

The included `get_number_of_rounds` function estimates resistance to a stated Gröbner-basis attack model, imposes a minimum, and adds a 20% margin. This is a parameter-generation heuristic from the supplied implementation, not a universal theorem that covers every future attack. Use the latest analysis and official parameter recommendations from the Griffin authors/protocol.

## 6. Sponge mode over a field

The lab wraps the permutation in a field-element sponge:

1. initialize (t) field elements to zero;
2. add up to (r=t-c) message elements into the rate part;
3. apply the Griffin permutation;
4. repeat until the padded input is absorbed;
5. output rate elements, permuting again if more are required.

Padding appends field element (1) and then zeroes when the input is not already rate-aligned. The code also sets the first capacity register to (1) in that case. These details distinguish the mode from a bit-oriented Keccak sponge and must match the intended Griffin specification.

The original function appended padding directly to `input_sequence`. Hashing should not alter the caller's message. The corrected version copies the sequence first and contains a regression assertion verifying that the input remains unchanged.

## 7. Field elements are not bytes

A general-purpose hash has a byte-string interface. A proof-system hash often begins with field elements. Mapping external data requires a specification covering:

- byte order;
- how many bytes form one candidate field element;
- whether values (\ge p) are rejected, reduced, or split;
- length and type encoding;
- domain separation for leaves, internal nodes, transcripts, and commitments;
- whether multiple field elements represent one logical object;
- output serialization and canonicality.

Naively reducing arbitrary 64-bit chunks modulo (p) can introduce bias because (p<2^{64}). Whether that matters and how it is handled depends on the protocol. Ambiguous packing can create semantic collisions even if the permutation remains cryptographically sound.

## 8. Security model and deployment caution

The Griffin paper analyzes its proposed structure against algebraic, statistical, differential, and related attacks and compares constraint costs with other ZK-friendly designs. That analysis applies to specified families and assumptions. It does not justify:

- reducing the round count because tests still “look random”;
- changing matrix or constants without reanalysis;
- replacing the field with one convenient to a different proof system;
- using the sponge padding for a different data type without domain separation;
- substituting Griffin for a conventional password hash, KDF, MAC, or file hash;
- assuming every proof-system implementation agrees on serialization.

Arithmetization-oriented hashes are a rapidly analyzed design area. Pin the paper revision, implementation commit, parameter set, serialization rules, and known-answer tests used by the protocol.

## 9. Corrected SageMath lab

Run:

```bash
sage code/griffin.sage
```

The file [`code/griffin.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/griffin.sage):

- generates constants using `hashlib.shake_256` instead of carrying a duplicated SHAKE source file;
- retains the supplied power, nonlinear, linear, constant, permutation, and sponge structure;
- copies the input before padding;
- converts absorbed values explicitly into (\mathbb F_p);
- rejects negative output lengths;
- replaces random demonstrations with three deterministic inputs;
- asserts that hashing did not mutate those inputs.

SageMath was not bundled into this package. The Python cryptographic labs are fully executable with the standard library; the Griffin file should be run in a SageMath environment and its printed values committed as test vectors if this module is integrated into an exact protocol.

## 10. Reading Griffin beside SHA-2 and SHA-3

| Dimension | SHA-256 | SHA3-256 | Griffin experiment |
|---|---|---|---|
| Native data unit | 32-bit words/bytes | 64-bit lanes/bytes | Elements of (\mathbb F_p) |
| Core | Compression iteration | Keccak-f[1600] sponge | Algebraic permutation + field sponge |
| Output in this module | 256 bits | 256 bits | 4 field elements in demo |
| Main optimization target | Conventional software/hardware | Broad software/hardware and permutation versatility | Constraint cost in proof systems |
| Standardization | FIPS 180-4 | FIPS 202 | Research design/protocol-specific adoption |
| Drop-in general hash? | Yes where approved | Yes where approved | No |

## 11. Further reading

The primary source is Lorenzo Grassi et al., *Horst Meets Fluid-SPN: Griffin for Zero-Knowledge Applications*, CRYPTO 2023. The IACR record includes the revision history and BibTeX: [ePrint 2022/403](https://eprint.iacr.org/2022/403).

Before using any ZK-friendly hash in a real proof system, also study the proof system's transcript/commitment specification, implementation audit, and field encoding. Primitive analysis cannot compensate for a mismatched protocol interface.

Previous: [Message Authentication Codes](/blog/message-authentication-codes/).

Return to the [module index](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/README.md).
