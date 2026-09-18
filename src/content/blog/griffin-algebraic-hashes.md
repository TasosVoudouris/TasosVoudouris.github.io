---
title: "Griffin and Arithmetization-Oriented Hash Functions"
description: "Explain why proof systems favor field-native permutations, study Griffin’s nonlinear and linear layers, distinguish field-element hashing from byte hashing, update Griffin’s security picture after later algebraic cryptanalysis, and place arithmetization-oriented hashes in the broader hash-function landscape."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Zero-Knowledge Proofs"
  - "Cryptographic Engineering"
  - "Mathematical Foundations"
tags:
  - "griffin"
  - "algebraic-hash"
  - "arithmetization"
  - "zkp"
  - "sponge"
  - "finite-fields"
  - "algebraic-cryptanalysis"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 8
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [Why Proof Systems Change the Hash-Function Cost Model](#why-proof-systems-change-the-hash-function-cost-model)
- [Griffin as a Field-Native Permutation](#griffin-as-a-field-native-permutation)
- [Nonlinearity, Diffusion, and Deterministic Parameters](#nonlinearity-diffusion-and-deterministic-parameters)
- [From a Permutation to a Hash: Sponge and Compression Modes](#from-a-permutation-to-a-hash-sponge-and-compression-modes)
- [Field Elements Are Not Byte Strings](#field-elements-are-not-byte-strings)
- [Security Analysis and the Post-Griffin Cryptanalysis](#security-analysis-and-the-post-griffin-cryptanalysis)
- [Educational Lab, Reproducibility, and What We Can Verify](#educational-lab-reproducibility-and-what-we-can-verify)
- [From SHA-256 to Griffin: What the Entire Series Teaches](#from-sha-256-to-griffin-what-the-entire-series-teaches)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why Proof Systems Change the Hash-Function Cost Model

A conventional hash function is normally evaluated on a CPU, GPU, microcontroller, or dedicated hardware engine.

In that world, operations such as

- XOR,
- bit rotations,
- fixed-width addition,
- table-free Boolean logic,

are extremely natural.

SHA-256 is built around exactly those operations.

Inside a zero-knowledge proof system, however, the cost model can be completely different.

A SNARK or STARK often expresses computation as algebraic constraints over a finite field

\[
\mathbb F_p.
\]

The prover is not merely asked to *run* SHA-256.

The prover must demonstrate that every relevant intermediate computation satisfies the proof system's arithmetic constraints.

That changes what "efficient" means.

### Native execution cost versus arithmetization cost

Consider the SHA-256 operation

\[
\operatorname{ROTR}^{13}(x).
\]

A processor can implement a 32-bit rotation directly or through a small number of machine instructions.

An arithmetic circuit over a large prime field does not naturally contain a "rotate 32-bit word" gate.

Instead, the circuit may need to:

1. range-constrain \(x\) to 32 bits;
2. decompose \(x\) into bits or limbs;
3. rearrange those bits;
4. reconstruct another field element;
5. constrain all intermediate relations.

Likewise, a Boolean operation such as

\[
x\land y
\]

is cheap in ordinary binary hardware but may require many constraints when the proof system's native object is a field element.

So the cost of a primitive depends on **where it is being evaluated**.

A useful distinction is:

\[
\boxed{
\text{native runtime}
\neq
\text{proof-system constraint cost}
}
\]

### Arithmetization-oriented primitives

An **arithmetization-oriented (AO)** or **ZK-friendly** hash design tries to work with the proof system rather than against it.

Instead of emulating bit operations, the primitive works directly with field elements and low-degree polynomial relations.

Typical ingredients include:

- exponentiation maps such as \(x\mapsto x^d\);
- inverse exponent maps;
- additions and multiplications in \(\mathbb F_p\);
- sparse or structured linear layers;
- sponge or compression modes over field elements.

The objective is not necessarily:

> beat SHA-256 in ordinary software.

The objective is closer to:

> minimize the cost of proving that the hash computation was executed correctly.

That cost depends on the proof system.

For example:

- an R1CS circuit cares heavily about multiplication constraints;
- a PLONK-style system may exploit custom gates;
- a STARK may care about polynomial degree, trace width, and AIR structure;
- lookup-enabled systems change the economics of some nonlinear operations.

Therefore even the phrase:

> "Griffin is cheaper than SHA-256"

is incomplete.

The meaningful question is:

> cheaper in which arithmetization, for which field, state width, mode, output size, and proof system?

### Why general-purpose hashes still matter

An AO hash does not automatically replace SHA-256 or SHA-3.

SHA-256 and SHA-3 have mature byte-string interfaces and extensive standardization.

A field-native primitive such as Griffin begins with objects in

\[
\mathbb F_p.
\]

That difference affects:

- serialization,
- domain separation,
- interoperability,
- protocol assumptions,
- collision interpretation,
- test vectors.

The right mental model is:

```text
SHA-256 / SHA-3:
    general-purpose standardized byte hashes

Griffin / other AO designs:
    field-native research/protocol primitives
    optimized for algebraic proof cost
```

The latter category requires much tighter parameter discipline.

---

## Griffin as a Field-Native Permutation

Griffin was proposed as an arithmetization-oriented family for zero-knowledge applications.

Its core object is a permutation

\[
G_\pi:\mathbb F_p^t\rightarrow\mathbb F_p^t.
\]

The state consists of

\[
t
\]

field elements.

The original design supports:

\[
t=3
\]

or:

\[
t\in\{4,8,12,16,20,24\}.
\]

The permutation combines:

1. an algebraic nonlinear layer;
2. a structured invertible linear layer;
3. additive round constants.

The design was motivated by reducing algebraic proof cost while still providing diffusion and resistance to known statistical and algebraic attacks.

### The Goldilocks field used in the educational lab

The supplied experiment uses the prime

\[
p=2^{64}-2^{32}+1.
\]

Numerically,

\[
p=18446744069414584321.
\]

This is often called the **Goldilocks prime**.

It is close to \(2^{64}\), making it attractive in some STARK-oriented systems because field elements fit naturally into machine-word-oriented implementations while still providing useful algebraic structure.

The state in the supplied experiment has:

\[
t=12.
\]

The original lab reserves:

\[
c=4
\]

state elements as capacity, leaving:

\[
r=t-c=8
\]

rate elements.

So one absorb step handles eight field elements.

But an important correction is needed:

> eight field elements are **not automatically equivalent to an arbitrary 64-byte string**.

Each canonical field element satisfies:

\[
0\le x<p<2^{64}.
\]

The map from arbitrary 64-bit strings to \(\mathbb F_p\) must therefore specify how values at least \(p\) are handled.

### The field size is almost, but not exactly, 64 bits

We have:

\[
\log_2 p
\approx
63.9999999996641.
\]

That is extremely close to 64 bits, but cryptographic parameter inequalities are exact statements.

For a sponge targeting \(\kappa\) bits under the original Griffin paper's capacity condition,

\[
c
\ge
\left\lceil
\frac{2\kappa}{\log_2 p}
\right\rceil.
\]

For:

\[
\kappa=128,
\]

the right-hand side is:

\[
\left\lceil
\frac{256}{63.9999999996641}
\right\rceil
=
5.
\]

So a **four-element Goldilocks capacity does not literally satisfy that exact 128-bit sponge inequality**, even though it falls short by an almost negligible fractional amount in a continuous-bit approximation.

This means the educational lab's:

\[
t=12,\quad c=4,\quad r=8
\]

should be described as a pedagogical/experimental parameter choice, not as a formally validated 128-bit Griffin sponge solely on the basis of the original capacity formula.

If a text wants to claim the original paper's bound literally, it must use parameters satisfying the exact inequality and then separately account for later cryptanalysis.

This is a good example of why:

\[
\boxed{
\text{"approximately 64-bit field"}
\neq
\text{"every exact 64-bit bound"}
}
\]

### Griffin is a permutation family, not one universal hash

The phrase "Griffin hash" can hide several choices:

- field \(p\);
- state width \(t\);
- exponent parameter \(d\);
- round count \(R\);
- linear matrix \(M\);
- round constants;
- sponge versus compression mode;
- rate/capacity split;
- input encoding;
- output encoding.

A protocol must pin all of them.

Changing any of these can define a different primitive instance.

---

## Nonlinearity, Diffusion, and Deterministic Parameters

Griffin's round structure is algebraic.

At a high level, a round applies:

\[
x
\overset{S}{\longmapsto}
S(x)
\overset{M}{\longmapsto}
M S(x)
\overset{+c^{(i)}}{\longmapsto}
M S(x)+c^{(i)}.
\]

The final round omits the additive constant in the original construction.

### Power and inverse-power maps

The nonlinear layer chooses

\[
d\in\{3,5,7,11\}
\]

as the smallest value satisfying:

\[
\gcd(d,p-1)=1.
\]

Why?

The nonzero field elements form a multiplicative group of order:

\[
p-1.
\]

The map

\[
x\mapsto x^d
\]

is a permutation of \(\mathbb F_p\) when exponentiation by \(d\) is invertible modulo \(p-1\).

That happens exactly when:

\[
\gcd(d,p-1)=1.
\]

Then there exists:

\[
d^{-1}
\]

such that:

\[
dd^{-1}\equiv1\pmod{p-1},
\]

and the inverse power map is:

\[
x\mapsto x^{d^{-1}}.
\]

For the Goldilocks field:

\[
p-1=2^{64}-2^{32}.
\]

We have:

\[
\gcd(3,p-1)=3,
\]

\[
\gcd(5,p-1)=5,
\]

\[
\gcd(7,p-1)=1.
\]

So the smallest allowed choice from the design set is:

\[
\boxed{d=7}.
\]

Its inverse exponent modulo \(p-1\) is:

\[
d^{-1}
=
10540996611094048183,
\]

because:

\[
7\cdot10540996611094048183
\equiv
1
\pmod{p-1}.
\]

This large exponent should not be interpreted as "perform ten quintillion multiplications."

Implementations use an addition chain or another efficient exponentiation strategy, and proof systems reason about the algebraic constraints appropriate to the chosen representation.

### The first nonlinear coordinates

Following the Griffin specification, the first two coordinates use inverse/forward power maps:

\[
y_0=x_0^{1/d},
\]

\[
y_1=x_1^d.
\]

The notation:

\[
1/d
\]

means exponentiation by the multiplicative inverse of \(d\) modulo \(p-1\), not ordinary real-number division.

That distinction matters.

We are working in a finite field, not over the reals.

### The Horst-style multiplicative layer

For later coordinates, Griffin uses the already transformed first coordinates and a previous state word.

Define:

\[
L_i(z_0,z_1,z_2)
=
\gamma_i z_0+z_1+z_2,
\]

with distinct nonzero coefficients \(\gamma_i\), for example:

\[
\gamma_i=i-1.
\]

Then for \(i\ge2\), a later coordinate has the form:

\[
y_i
=
x_i
\left(
L_i^2
+
\alpha_i L_i
+
\beta_i
\right),
\]

with the \(i=2\) case using a zero in place of the previous coordinate where specified.

This form is central to Griffin's design philosophy.

It combines:

- multiplication,
- low-degree polynomials,
- dependencies on earlier transformed coordinates.

The design was intended to produce useful nonlinear algebraic structure at relatively low proof cost.

### Why the quadratic factor must not vanish unexpectedly

The constants satisfy a condition of the form:

\[
\alpha_i^2-4\beta_i
\]

being a quadratic nonresidue in \(\mathbb F_p\).

Intuitively, this prevents the quadratic factor

\[
L^2+\alpha_i L+\beta_i
\]

from having roots in the field.

That matters because multiplying \(x_i\) by a factor that could become zero for ordinary field inputs would complicate invertibility.

The exact parameter-generation rule is therefore part of the permutation definition.

### In-place updates are dangerous

The nonlinear layer has explicit data dependencies.

If an implementation accidentally uses:

```text
new x_i
```

where the specification required:

```text
old x_i
```

or vice versa, the resulting function changes.

This is similar in spirit to the Chi implementation trap in Keccak:

> algebraically simple formulas can still be order-sensitive in code.

A safe implementation should make state dependencies explicit.

### Linear diffusion

After the nonlinear layer, Griffin multiplies the state by an invertible matrix:

\[
x\leftarrow Mx.
\]

For small widths, the design gives compact matrices.

For larger widths divisible by four, it builds the diffusion layer from structured \(4\times4\) components.

The objective is to spread influence across state coordinates without paying the full cost of an arbitrary dense matrix.

For \(t\ge8\), the original design uses a structure assembled from repeated \(M_4\) blocks and a circulant-like outer matrix.

This reduces linear-layer arithmetic from a naive quadratic pattern toward a structure with roughly linear scaling in \(t\).

### Invertibility must be checked in the target field

The matrix must be invertible over:

\[
\mathbb F_p.
\]

It is not sufficient to check that the same integer matrix has nonzero determinant over:

\[
\mathbb Z
\]

or over a different field.

The relevant condition is:

\[
\det(M)\not\equiv0\pmod p.
\]

Field choice is part of the primitive.

### Round constants

The original Griffin design derives round constants and nonlinear coefficients pseudo-randomly using SHAKE-based generation.

This is valuable for reproducibility.

It helps avoid arbitrary hand-picked constants.

But deterministic generation only solves one problem:

\[
\text{reproducibility}.
\]

It does not prove:

\[
\text{security}.
\]

The following details are consensus-critical:

- seed string;
- capitalization;
- separators;
- field identifier;
- width;
- security parameter;
- byte order;
- SHAKE output length;
- integer parsing;
- reduction/rejection rule.

Changing one character in the seed can change the entire parameter set.

So a protocol should not say merely:

> "generate Griffin constants deterministically."

It should specify the byte-exact derivation.

---

## From a Permutation to a Hash: Sponge and Compression Modes

A permutation is not yet a variable-length hash function.

It must be wrapped in a mode.

The Griffin paper discusses both:

- a sponge-style hash;
- a feed-forward compression function.

These serve different use cases.

### Griffin sponge

Let the state contain:

\[
t=r+c
\]

field elements.

The rate contains:

\[
r
\]

elements and the capacity contains:

\[
c.
\]

At a high level:

1. initialize the state according to the mode specification;
2. absorb \(r\) message field elements into the rate portion;
3. apply the Griffin permutation;
4. repeat;
5. expose output field elements from the rate, permuting again if necessary.

This resembles the sponge architecture studied in the SHA-3 article, but the **data domain is different**.

Keccak absorbs bits/bytes.

Griffin's field sponge absorbs elements of:

\[
\mathbb F_p.
\]

### An important correction to the supplied lab's sponge wrapper

The supplied project notes describe a lab wrapper that:

- appends a field element \(1\) when the input is not rate-aligned;
- pads with zeros;
- also sets a capacity element to \(1\).

That may be a useful custom educational convention, but it should **not be silently presented as the canonical sponge mode from the Griffin paper**.

The Griffin paper's sponge description uses a different length-binding approach: the message is zero-padded to a multiple of the rate, while the capacity-side IV incorporates the message length.

Therefore the revised article distinguishes:

```text
Griffin permutation
```

from:

```text
the particular educational sponge wrapper in this repository.
```

If the lab is intended to reproduce the paper exactly, its padding/IV rules should be brought into byte-for-byte/field-element-for-field-element agreement with the selected Griffin specification and accompanied by test vectors.

If it is intentionally custom, it should be labeled custom.

### Why mode details matter

A cryptographically strong permutation can be weakened by a bad mode.

This series has already seen the same principle repeatedly:

- SHA-256 + secret-prefix keying produced length extension;
- a block cipher + variable-length CBC-MAC produced forgery;
- Keccak-f[1600] requires correct domain separation to define SHA-3/SHAKE.

The lesson is universal:

\[
\boxed{
\text{secure primitive}
+
\text{unspecified mode}
\neq
\text{secure protocol}
}
\]

### Griffin compression

The original paper also studies a permutation-based compression map with feed-forward and truncation.

At a high level:

\[
C(x)
=
\operatorname{Trn}
(
P(x)+x
).
\]

This is conceptually related to the feed-forward principle we saw earlier with Davies–Meyer.

The intended application includes fixed-arity compression such as Merkle-tree nodes, where a single permutation call may be more efficient than maintaining extra sponge capacity.

This is a useful reminder that:

> the most efficient mode can depend on the exact protocol task.

A variable-length transcript hash and a 2-to-1 Merkle-tree compression function need not use the same wrapper.

---

## Field Elements Are Not Byte Strings

This is one of the most important sections for any proof-oriented hash article.

A general-purpose hash usually exposes an API like:

```python
digest = H(bytes_message)
```

A field-native primitive may expose something closer to:

```text
H(x0, x1, ..., x_{m-1})
```

with:

\[
x_i\in\mathbb F_p.
\]

The conversion between these worlds is not automatic.

### Canonical encoding

Suppose one candidate field element is represented by 8 bytes.

Because:

\[
p<2^{64},
\]

there are 64-bit strings that do not encode canonical field elements.

For example:

\[
p
\]

itself fits in 64 bits but represents:

\[
0
\]

after reduction modulo \(p\).

If both encodings are accepted:

```text
00...00
```

and:

```text
encoding of p
```

they can represent the same field element.

That is a canonicality failure.

### Reduction can create many-to-one mappings

If external integers are simply reduced:

\[
x\mapsto x\bmod p,
\]

then:

\[
x
\]

and:

\[
x+p
\]

map to the same field element whenever both are in the external input range.

This may be acceptable in a carefully specified hash-to-field construction.

It is dangerous if a protocol mistakenly assumes that distinct serialized messages remain distinct after packing.

### Rejection sampling

One canonical approach for a fixed-width candidate is:

1. parse an integer \(x\);
2. accept only if:

   \[
   0\le x<p;
   \]

3. otherwise reject or obtain more pseudorandom material according to the specification.

This avoids modular-reduction bias and noncanonical representations.

But it may not be the most efficient choice for every protocol.

The key point is:

> the conversion rule must be explicit.

### Length and type binding

Suppose an application hashes:

```text
field sequence [1, 2]
```

and:

```text
field sequence [1, 2, 0]
```

under a mode whose trailing zeros can be absorbed ambiguously.

Without a length-binding rule, distinct logical messages may map into the same padded field sequence.

That is why the original Griffin sponge mode incorporates message length in its initialization.

Likewise, a Merkle tree should normally separate:

```text
leaf
```

from:

```text
internal node.
```

A transcript should distinguish:

```text
commitment
challenge
response
```

domains.

### Domain separation

A proof system may use one permutation for:

- Merkle-tree leaves;
- Merkle-tree internal nodes;
- Fiat-Shamir transcripts;
- commitments;
- random-oracle challenges;
- lookup-table digests.

Those are different domains.

A robust protocol binds the purpose through explicit capacity/IV values, prefixes, tags, or another specified domain-separation mechanism.

Do not rely on:

```text
"these objects have different lengths"
```

unless the specification proves that the encodings remain disjoint.

### Output canonicality

If Griffin outputs field elements, the protocol must define:

- how many output elements;
- their order;
- canonical byte encoding;
- whether leading zeros are retained;
- whether outputs are later truncated or packed.

A "four-field-element digest" is not the same thing as a standardized 256-bit byte digest unless the field and encoding make that equivalence precise.

---

## Security Analysis and the Post-Griffin Cryptanalysis

This is the section that most needs updating beyond the original notes.

The Griffin paper provided a broad security analysis against:

- differential attacks;
- rebound attacks;
- interpolation attacks;
- Gröbner-basis attacks;
- other statistical/algebraic techniques.

Its round selection included margins based on the attack models known at the time.

That historical analysis remains important.

But it is no longer the end of the security story.

### Security claims age

Arithmetization-oriented designs are relatively young compared with SHA-2 and SHA-3.

They deliberately expose low-degree algebraic structure because that structure is what makes them efficient in proof systems.

That creates a tension:

\[
\boxed{
\text{proof-friendly algebra}
\quad\text{is also}\quad
\text{cryptanalyst-visible algebra}
}
\]

The optimization target can become the attack surface.

### The CICO problem

A central cryptanalytic object for AO permutations is the **constrained-input constrained-output (CICO)** problem.

Very roughly, the attacker imposes constraints on parts of the permutation input and output and tries to solve the resulting polynomial system.

If that system can be solved substantially faster than the design anticipated, the security margin can be lower than the original parameter-generation model predicts.

This is why Gröbner-basis complexity, resultants, elimination structure, and algebraic degree are not merely mathematical curiosities for AO hashes.

They are direct cryptanalytic tools.

### The 2024 Algebraic FreeLunch attack

Later work introduced the **Algebraic FreeLunch** technique.

The key observation was that for some AO constructions, a carefully chosen monomial ordering can make the natural polynomial system much easier to solve than earlier analyses suggested.

For Griffin, the authors combined this approach with a round-bypassing technique.

Their reported practical result recovered a CICO solution for:

\[
7
\]

out of:

\[
10
\]

Griffin rounds in under four hours on one CPU core for the investigated setting.

More importantly, their complexity analysis showed that some full-round Griffin instances provided significantly fewer security bits than originally claimed.

This was not merely a toy reduced-round distinguisher.

It materially changed the parameter-security discussion.

### The 2025 improved resultant attack

Subsequent work improved the algebraic attack framework again using resultants.

For Griffin, the authors reported practical CICO solutions for:

\[
8
\]

out of:

\[
10
\]

rounds and concluded that most analyzed Griffin variants did not reach their originally claimed security level.

This reinforces the main engineering conclusion:

> the original Griffin round-count heuristic should not be treated as current deployment guidance in isolation.

### What this does and does not mean

It would be too crude to summarize this as:

> "Griffin is broken, therefore every Griffin-based system is broken."

The relevant questions include:

- which exact field?
- which state width?
- which round count?
- which mode?
- which output constraints?
- what protocol property depends on the primitive?
- which attack complexity applies?
- has the protocol changed parameters after later cryptanalysis?

But the reverse claim is also inappropriate:

> "the 2023 paper claims 128 bits, therefore this lab is 128-bit secure."

That statement is no longer defensible without accounting for post-publication cryptanalysis.

### How to write the status correctly

For an educational article in 2026, a careful description is:

> Griffin is an important arithmetization-oriented design and an excellent case study in ZK-friendly permutation engineering, but its original parameter-security picture was challenged by substantial 2024–2025 algebraic cryptanalysis. Experimental code should therefore be treated as research/educational material unless a protocol has independently selected updated parameters based on current analysis.

That is both more accurate and more educational.

### Why this is actually a useful ending for the series

The final lesson is not pessimistic.

It demonstrates cryptography working as intended:

1. designers propose a construction;
2. designers publish rationale and security analysis;
3. cryptanalysts find stronger techniques;
4. parameter claims are revised;
5. future designs learn from the attack.

That cycle is the scientific method applied to cryptographic design.

---

## Educational Lab, Reproducibility, and What We Can Verify

The supplied lab is:

[`code/griffin.sage`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/griffin.sage)

and is intended to explore:

- finite-field state arithmetic;
- power maps;
- Griffin's nonlinear structure;
- structured diffusion;
- deterministic parameter generation;
- a field-element sponge wrapper.

### SageMath requirement

The implementation depends on SageMath's finite-field and matrix functionality.

This environment does not currently contain SageMath, so the full `griffin.sage` program was **not executed here**.

That limitation should remain explicit.

A cryptographic article should not say:

```text
validated
```

and then imply that a Sage implementation ran when it did not.

What we *can* validate independently are structural arithmetic facts about the supplied Goldilocks instance.

### Verified Goldilocks facts

For:

\[
p=2^{64}-2^{32}+1,
\]

we verified:

```text
p is prime: True
```

and:

```text
gcd(3, p-1)  = 3
gcd(5, p-1)  = 5
gcd(7, p-1)  = 1
gcd(11,p-1)  = 1
```

Therefore the first admissible exponent from:

\[
\{3,5,7,11\}
\]

is:

\[
d=7.
\]

We also verified:

\[
7d^{-1}\equiv1\pmod{p-1}
\]

for:

\[
d^{-1}=10540996611094048183.
\]

### A direct power-map round trip

For any:

\[
x\in\mathbb F_p,
\]

the permutation property predicts:

\[
\left(x^d\right)^{d^{-1}}=x.
\]

A simple Python field check is:

```python
p = 2**64 - 2**32 + 1
d = 7
d_inv = pow(d, -1, p - 1)

x = 123456789

assert pow(
    pow(x, d, p),
    d_inv,
    p,
) == x
```

Testing many random field values gives the same result.

This does not validate the full Griffin permutation.

It validates the exponent-invertibility condition.

### Capacity check

For the same field:

```python
import math

capacity_needed = math.ceil(
    256 / math.log2(p)
)
```

returns:

```text
5
```

for the original paper's exact \(2\kappa/\log_2 p\) sponge-capacity formula with:

\[
\kappa=128.
\]

This is why the lab's `capacity = 4` must not be described as literally satisfying that formula.

### What a reproducible Griffin lab should commit

A research-quality repository should record:

- exact SageMath version;
- exact paper revision;
- implementation commit;
- field prime;
- state width;
- exponent;
- inverse exponent;
- round count;
- capacity/rate;
- matrix;
- constants;
- seed string;
- sponge/compression mode;
- input encoding;
- output encoding;
- deterministic test vectors.

A useful test vector should look like:

```text
instance:
    field = ...
    t = ...
    rounds = ...
    mode = ...

input:
    [x0, x1, ...]

output:
    [y0, y1, ...]
```

This is much more valuable than printing three random runs.

### Input mutation

The original notes correctly identify a software-engineering bug class: a hash function should not mutate the caller's input sequence while padding.

Prefer:

```python
work = list(input_sequence)
```

before appending padding.

Then test:

```python
before = list(message)
_ = hash_function(message)
assert message == before
```

Correct cryptographic arithmetic is not enough if the API silently changes application data.

---

## From SHA-256 to Griffin: What the Entire Series Teaches

This is the final article in **Hash Functions & MACs**, so it is useful to close the loop.

The series began with a simple question:

> What is a cryptographic hash function?

It ends with a much stronger question:

> What does it mean for a hash construction to be secure, correctly instantiated, correctly encoded, and appropriate for the computational environment in which it is used?

Those are very different levels of understanding.

### Part 01 — Hash Functions: A Primer

We began with:

\[
H:\{0,1\}^*\rightarrow\{0,1\}^n.
\]

The first conceptual distinction was that collisions must exist mathematically.

Security means they should be hard to find.

We separated:

- preimage resistance;
- second-preimage resistance;
- collision resistance.

### Part 02 — Security Properties and Attack Models

Then the focus moved from informal terminology to explicit adversarial tasks.

We learned that:

\[
\text{"hash broken"}
\]

is not precise enough.

We should ask:

\[
\boxed{
\text{Which security game did the attacker win?}
}
\]

A collision is not a preimage.

A dictionary attack is not generic inversion.

A length-extension forgery is not a collision.

### Part 03 — Birthday Attacks

The birthday bound explained why an \(n\)-bit digest gives only about:

\[
n/2
\]

bits of ideal generic collision strength.

The key combinatorial fact was:

\[
\binom q2
\approx
\frac{q^2}{2}.
\]

Collision search is cheaper because the attacker accepts any matching pair.

### Part 04 — Merkle–Damgård and SHA-256

We then moved inside a real hash construction.

SHA-256 showed how:

\[
\text{fixed-size compression}
\]

becomes:

\[
\text{arbitrary-length hashing}.
\]

Padding, state chaining, message scheduling, round functions, and feed-forward became concrete implementation objects.

### Part 05 — Length Extension

Once the internal state was visible, we saw that a secure hash could be composed insecurely.

The construction:

\[
\operatorname{SHA256}(K\|M)
\]

failed as an improvised MAC even though SHA-256 itself remained unbroken.

That produced one of the central lessons of the series:

\[
\boxed{
\text{secure primitive}
\neq
\text{secure composition}
}
\]

### Part 06 — Sponge, Keccak, and SHA-3

SHA-3 showed that Merkle–Damgård is not the only architecture.

The sponge model introduced:

\[
b=r+c,
\]

absorption, squeezing, hidden capacity, domain separation, and XOFs.

The same word "hash" can therefore describe primitives with very different internal interfaces.

### Part 07 — Message Authentication Codes

The series then returned to protocol goals.

A MAC changed the question from:

```text
Did the bytes change?
```

to:

```text
Could an attacker without the key create a fresh accepted tag?
```

HMAC, CBC-MAC, CMAC, and KMAC illustrated again that:

- message domain matters;
- tag length matters;
- encoding matters;
- replay state matters;
- key separation matters.

### Part 08 — Griffin and AO Hashes

Finally, Griffin changes the cost model itself.

A construction efficient on a processor may be expensive to prove.

A field-native algebraic permutation may be dramatically easier to arithmetize.

But the same algebraic simplicity that helps the prover can help the cryptanalyst.

This creates the final conceptual progression:

\[
\boxed{
\text{interface}
\rightarrow
\text{security game}
\rightarrow
\text{generic bounds}
\rightarrow
\text{construction}
\rightarrow
\text{composition}
\rightarrow
\text{implementation}
\rightarrow
\text{application-specific cost model}
\rightarrow
\text{cryptanalysis}
}
\]

That is a much more complete understanding of hashing than:

> "SHA-256 turns input into 32 bytes."

---

## Conclusion

Griffin is a useful final case study because it forces us to combine nearly every lesson from the series.

It is a field-native permutation:

\[
G_\pi:\mathbb F_p^t\rightarrow\mathbb F_p^t
\]

designed for a computational environment where proof constraints matter.

Its nonlinear layer uses invertible power maps and low-degree multiplicative relations.

Its linear layer uses structured diffusion.

Its constants are deterministically generated.

Its hash modes operate on field elements rather than arbitrary bytes.

Every one of those design choices has consequences.

The Goldilocks experiment illustrates the details:

\[
p=2^{64}-2^{32}+1,
\]

\[
t=12,
\]

and the first valid Griffin exponent from the design set is:

\[
d=7.
\]

But even apparently small parameter statements need precision.

For the original paper's exact sponge-capacity inequality and a 128-bit target, the Goldilocks field gives:

\[
\left\lceil
\frac{256}{\log_2 p}
\right\rceil
=
5,
\]

so a four-element capacity should be treated as an educational approximation/custom choice rather than advertised as literally satisfying that condition.

Likewise, the supplied sponge wrapper should be distinguished from the paper's specific length-binding sponge mode.

And most importantly, the original security analysis must be read in light of later work.

The 2024 Algebraic FreeLunch attack and the 2025 improved resultant attack substantially strengthened the algebraic cryptanalysis of Griffin and related AO primitives.

That does not erase Griffin's importance.

It changes how we should use it:

\[
\boxed{
\text{important research design}
\neq
\text{unchanging deployment recommendation}
}
\]

This is a fitting place to finish the series.

Cryptography is not a collection of algorithms whose names are enough.

It is the study of:

- exact functions;
- exact domains;
- exact security games;
- exact parameter bounds;
- exact encodings;
- exact protocol composition;
- exact implementation assumptions;
- continuously updated cryptanalysis.

The complete **Hash Functions & MACs** path is therefore:

```text
Part 01 — Hash Functions: A Primer
Part 02 — Hash Security Properties and Attack Models
Part 03 — Birthday Attacks on Hash Functions
Part 04 — Merkle–Damgård and SHA-256
Part 05 — Length-Extension Attacks
Part 06 — Sponge Construction, Keccak, and SHA-3
Part 07 — Message Authentication Codes: HMAC, CBC-MAC, and KMAC
Part 08 — Griffin and Arithmetization-Oriented Hash Functions
```

The series began with the fixed-output map:

\[
H:\{0,1\}^*\rightarrow\{0,1\}^n.
\]

It ends with the recognition that the symbol \(H\) hides an enormous amount of engineering and mathematics.

That is the real lesson:

\[
\boxed{
\text{Never ask only "Which hash?"}
}
\]

Ask:

\[
\boxed{
\text{Which construction, which parameters, which encoding, which security goal, and which threat model?}
}
\]

That is where cryptographic reasoning actually begins.

Previous: [Message Authentication Codes](/blog/message-authentication-codes/).

Return to the [Hash Functions & MACs module index](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/README.md).

---

## References

1. Lorenzo Grassi, Yonglin Hao, Christian Rechberger, Markus Schofnegger, Roman Walch, and Qingju Wang, **Horst Meets Fluid-SPN: Griffin for Zero-Knowledge Applications**, Cryptology ePrint Archive, Paper 2022/403; major revision of the CRYPTO 2023 publication.  
   https://eprint.iacr.org/2022/403

2. Augustin Bariant, Aurélien Boeuf, Axel Lemoine, Irati Manterola Ayala, Morten Øygarden, Léo Perrin, and Håvard Raddum, **The Algebraic FreeLunch: Efficient Gröbner Basis Attacks Against Arithmetization-Oriented Primitives**, CRYPTO 2024.  
   https://eprint.iacr.org/2024/347

3. Augustin Bariant, Aurélien Boeuf, Pierre Briaud, Maël Hostettler, Morten Øygarden, and Håvard Raddum, **Improved Resultant Attack against Arithmetization-Oriented Primitives**, CRYPTO 2025.  
   https://eprint.iacr.org/2025/259

4. Eli Ben-Sasson, Lior Goldberg, and David Levit, **STARK Friendly Hash – Survey and Recommendation**, Cryptology ePrint Archive, Paper 2020/948.

5. Lorenzo Grassi et al., related work on arithmetization-oriented symmetric primitives and proof-oriented cost models.

6. Guido Bertoni, Joan Daemen, Michaël Peeters, and Gilles Van Assche, **Cryptographic Sponge Functions**, for the generic sponge model used as background.

7. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**, for SHA-2 comparison.

8. National Institute of Standards and Technology, **FIPS 202: SHA-3 Standard**, for permutation/sponge comparison.
