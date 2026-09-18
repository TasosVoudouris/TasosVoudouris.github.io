---
title: "Pseudorandom Generators and Stream Ciphers: From Deterministic Expansion to Secure Keystreams"
description: "Build the security vocabulary for PRGs, CSPRNGs, DRBGs, keystream generators, stream ciphers, and nonce discipline before studying linear generators, RC4, ChaCha20, and historical generator failures."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Randomness & Entropy"
  - "Symmetric Cryptography"
  - "Cryptography Fundamentals"
  - "Cryptographic Engineering"
tags:
  - "prg"
  - "csprng"
  - "drbg"
  - "stream-cipher"
  - "keystream"
  - "nonce"
  - "pseudorandomness"
  - "entropy"
difficulty: "Introductory"
series: "Randomness & Stream Ciphers"
seriesOrder: 1
status: "Reviewed"
draft: false
---

## Table of Contents

- [Deterministic Expansion and Computational Randomness](#deterministic-expansion-and-computational-randomness)
- [PRG, PRNG, CSPRNG, and DRBG: Similar Names, Different Roles](#prg-prng-csprng-and-drbg-similar-names-different-roles)
- [From Pseudorandomness to Stream-Cipher Keystreams](#from-pseudorandomness-to-stream-cipher-keystreams)
- [Nonce Discipline and the Catastrophe of Keystream Reuse](#nonce-discipline-and-the-catastrophe-of-keystream-reuse)
- [Next-Bit Unpredictability, State Compromise, and Statistical Tests](#next-bit-unpredictability-state-compromise-and-statistical-tests)
- [Small Experiments: Looking Random Is Not Being Secure](#small-experiments-looking-random-is-not-being-secure)
- [Series Roadmap and Engineering Rules](#series-roadmap-and-engineering-rules)
- [Conclusion](#conclusion)
- [References](#references)

---

## Deterministic Expansion and Computational Randomness

A cryptographic generator is usually **deterministic once its internal state is fixed**.

That sounds contradictory only if we use the word "random" too loosely.

The purpose of a pseudorandom generator is not to create information-theoretic randomness from nothing. It is to take a shorter secret or unpredictable state and deterministically expand it into a longer output that is computationally indistinguishable from the random distribution expected by the surrounding protocol.

The basic pseudorandom-generator abstraction is

$$
G:\{0,1\}^{s}\rightarrow\{0,1\}^{\ell},
\qquad
\ell>s.
$$

The input is an $s$-bit seed.

The output is an $\ell$-bit string.

Because the domain contains only

$$
2^s
$$

possible seeds, the range of $G$ can contain at most

$$
2^s
$$

different outputs.

But the complete set

$$
\{0,1\}^{\ell}
$$

contains

$$
2^\ell
$$

strings.

Since $s<\ell$, we have

$$
2^s<2^\ell.
$$

Therefore a deterministic PRG output cannot be uniformly distributed over all $\ell$-bit strings in an information-theoretic sense.

This is not a flaw. It is the reason the security definition must be **computational**.

### Computational indistinguishability

Let $U_s$ denote a uniformly random $s$-bit seed, and $U_\ell$ a uniformly random $\ell$-bit string.

A distinguisher $D$ receives one $\ell$-bit string and tries to determine whether it came from $G(U_s)$ or from $U_\ell$.

Its distinguishing advantage can be written

$$
\operatorname{Adv}^{\mathrm{prg}}_G(D)
=
\left|
\Pr[D(G(U_s))=1]
-
\Pr[D(U_\ell)=1]
\right|.
$$

A secure PRG requires this advantage to be negligible for every efficient adversary in the intended model.

The phrase "the output looks random" is therefore too weak. The real claim is that no efficient test, including tests crafted specifically for the generator, can exploit the output distribution with meaningful advantage.

### Statistical distance and computational distance are different

A PRG output distribution can be statistically far from uniform. Because it is supported on at most $2^s$ points out of $2^\ell$, an unbounded adversary with full knowledge of the range could distinguish it from uniform.

Cryptographic security relies on the assumption that efficiently recognizing that range is infeasible.

This is one of the central ideas in modern cryptography:

$$
\boxed{
\text{mathematical difference}
\neq
\text{efficiently exploitable difference}
}
$$

### Entropy is not created by deterministic expansion

Suppose a generator receives only $s$ bits of unknown seed state.

Expanding that seed into one megabyte does not create one megabyte of fresh entropy. Every output bit remains a deterministic function of the state.

If the state is recovered, the attacker may be able to reconstruct or predict outputs according to the generator's state-evolution design.

That gives a useful hierarchy:

```text
entropy source
    -> unpredictable physical/system input

DRBG / CSPRNG
    -> deterministic state expansion

stream cipher
    -> deterministic keystream from key + nonce/counter
```

### Why systems combine entropy and deterministic generation

Real systems need unpredictable values for keys, ephemeral secrets, randomized protocol values, and other security-critical state.

Obtaining fresh physical entropy for every requested bit would be inconvenient and inefficient. Practical systems therefore collect entropy, initialize a cryptographic internal state, expand it deterministically, and reseed according to the generator design.

Applications should normally consume the operating system's cryptographic randomness interface rather than create a generator from timestamps, process IDs, LCGs, or ad-hoc hashes.

---

## PRG, PRNG, CSPRNG, and DRBG: Similar Names, Different Roles

The terminology is overloaded, so the first article should distinguish the layers clearly.

### PRG: the theoretical primitive

In complexity-based cryptography, a pseudorandom generator is usually modeled as

$$
G:\{0,1\}^s\rightarrow\{0,1\}^{\ell},
\qquad
\ell>s,
$$

together with a computational indistinguishability requirement.

It is primarily a mathematical object used in definitions and reductions.

### PRNG: a broad practical category

A pseudorandom number generator may optimize for:

- speed,
- long period,
- reproducibility,
- statistical quality,
- equidistribution.

Those are useful properties for simulation, games, testing, and randomized algorithms.

They do not imply cryptographic security.

A generator can have an enormous period and excellent statistical behavior while still being completely predictable after enough state information is exposed.

Period length and adversarial unpredictability are different properties.

### CSPRNG: cryptographic pseudorandom generation

A cryptographically secure PRNG is intended for an adversarial environment.

A useful stateful abstraction is

$$
(S_i,\operatorname{input}_i)
\longmapsto
(S_{i+1},\operatorname{output}_i).
$$

The security questions now include:

- can future output be predicted?
- can the internal state be recovered?
- what does current-state compromise reveal?
- when does fresh entropy restore unpredictability?
- are outputs distinguishable from the target random distribution?

Different CSPRNG designs provide different compromise-recovery and backtracking properties, so those terms should always be tied to an explicit model.

### DRBG: a standardized deterministic random-bit generator

NIST uses the term deterministic random bit generator, or DRBG, for standardized stateful deterministic mechanisms.

The current final NIST SP 800-90A Rev. 1 specifies:

- Hash_DRBG,
- HMAC_DRBG,
- CTR_DRBG.

The controversial Dual_EC_DRBG mechanism was removed in Revision 1.

A DRBG standard defines more than a mathematical expansion function. It specifies operations such as:

- instantiation,
- generation,
- reseeding,
- state update,
- optional additional input,
- request and reseed limits.

### The NIST SP 800-90 architecture

The NIST framework is usefully divided into three layers.

**SP 800-90A** defines deterministic DRBG mechanisms.

**SP 800-90B** addresses entropy sources and entropy assessment.

**SP 800-90C** defines complete random-bit-generator constructions that combine entropy sources with DRBG mechanisms.

SP 800-90C became final in September 2025.

This gives a useful conceptual decomposition:

$$
\boxed{
\text{entropy source}
+
\text{deterministic generator}
+
\text{system construction}
}
$$

### Current standards status

As of September 2026:

- SP 800-90A Rev. 1 remains the current final DRBG recommendation;
- SP 800-90A Rev. 2 is in pre-draft development;
- SP 800-90B is final;
- SP 800-90C is final.

A standard being under revision does not make the current final document disappear.

### Summary table

| Term | Typical role | Secret state? | Main concern |
|---|---|---:|---|
| PRG | theoretical expansion primitive | yes | computational indistinguishability |
| PRNG | general deterministic generator | maybe | often period/statistics |
| CSPRNG | practical cryptographic generator | yes | prediction/state compromise |
| DRBG | standardized deterministic bit generator | yes | specification-defined state security |
| Entropy source | supplies unpredictability | source-dependent | entropy estimation/health |
| Stream cipher | produces key-dependent keystream | key secret | confidentiality under nonce/key rules |

These categories overlap conceptually, but they are not synonyms.

---

## From Pseudorandomness to Stream-Cipher Keystreams

A synchronous stream cipher encrypts by XORing plaintext with a generated keystream.

Let $P$ be the plaintext and $KS$ the keystream.

Encryption is

$$
C=P\oplus KS.
$$

Decryption is

$$
P=C\oplus KS
$$

because

$$
x\oplus y\oplus y=x.
$$

The XOR operation itself provides no deep cryptographic protection. Security lives in the keystream generation and in the rule that the same keystream must not be reused across different plaintexts.

### From one-time pad to computational stream cipher

The one-time pad uses a keystream that is:

- uniformly random,
- as long as the plaintext,
- secret,
- used once.

A modern stream cipher replaces that huge random pad with a short secret key and deterministic expansion.

Conceptually:

$$
KS=G(K,N,\operatorname{counter}),
$$

where:

- $K$ is secret;
- $N$ is usually a public nonce;
- the counter selects a particular keystream block.

The design goal is that an adversary who does not know $K$ cannot distinguish the generated keystream from the required random distribution or exploit it to recover useful plaintext information, under the primitive's nonce rules.

### The nonce is usually public

A nonce normally does not provide secrecy. Its job is to keep encryption contexts distinct under a fixed key.

The receiver needs the nonce to reproduce the keystream, so a transmitted object may look conceptually like

```text
nonce || ciphertext
```

rather than trying to hide the nonce.

### Unique does not necessarily mean random

Many stream-cipher constructions require nonce uniqueness, not unpredictability.

A counter can therefore be an excellent nonce strategy:

```text
0, 1, 2, 3, ...
```

provided it is never repeated under the same key.

The exact contract is construction-specific.

Do not silently replace "must be unique" with "should be random."

### ChaCha20 preview

The IETF ChaCha20 construction specified by RFC 8439 uses:

- a 256-bit key;
- a 96-bit nonce;
- a 32-bit block counter.

The nonce must not repeat for two encryptions under the same key.

ChaCha20 produces 64-byte keystream blocks from the key, nonce, and block counter.

Later in the series we will study how its ARX structure—addition, rotation, XOR—differs from linear recurrences such as LCGs and LFSRs.

### Stream encryption alone does not authenticate

A bare stream cipher gives confidentiality, not integrity.

If

$$
C=P\oplus KS
$$

and an attacker sends

$$
C'=C\oplus\Delta,
$$

then the receiver obtains

$$
P'
=
C'\oplus KS
=
P\oplus\Delta.
$$

The attacker can therefore induce controlled plaintext bit flips without knowing the key.

Modern protocols usually use authenticated encryption such as ChaCha20-Poly1305 instead of bare ChaCha20.

---

## Nonce Discipline and the Catastrophe of Keystream Reuse

The most important operational invariant for a synchronous stream cipher is

$$
\boxed{
\text{never repeat the same keystream for different plaintexts}
}
$$

Suppose

$$
C_1=P_1\oplus KS
$$

and

$$
C_2=P_2\oplus KS.
$$

Then

$$
C_1\oplus C_2
=
P_1\oplus P_2\oplus KS\oplus KS.
$$

Since

$$
KS\oplus KS=0,
$$

we obtain

$$
\boxed{
C_1\oplus C_2=P_1\oplus P_2.
}
$$

The keystream disappears.

### Why that relation is useful to an attacker

Natural language, file formats, network packets, and structured application messages are redundant.

If part of one plaintext becomes known, then the corresponding keystream portion follows:

$$
KS=C_1\oplus P_1.
$$

Then

$$
P_2=C_2\oplus KS.
$$

This is the classical two-time-pad failure.

### Key reuse is not necessarily keystream reuse

Modern nonce-based stream ciphers are designed so that one secret key can encrypt many messages as long as every encryption uses an acceptable distinct nonce/counter context.

So the practical rule is not "never reuse a stream-cipher key."

It is:

> never reuse a key/nonce/counter context in a way that repeats keystream.

### Random nonces can collide

If a $96$-bit nonce is sampled independently at random for each encryption, then after $q$ encryptions under one key the approximate collision probability is

$$
1-\exp\left(
-\frac{q(q-1)}{2^{97}}
\right).
$$

A large nonce space can make this probability tiny, but "96 bits is large" is not a nonce-management design by itself.

### Counter rollback and distributed systems

A deterministic counter avoids random collision only if system state is reliable.

Nonce uniqueness can fail after:

- virtual-machine snapshot rollback,
- database restore,
- device cloning,
- counter reset,
- concurrent processes sharing one key,
- key reuse across devices.

A distributed protocol must allocate nonce space globally, not merely per process.

Nonce discipline is therefore a systems problem as much as a cryptographic one.

---

## Next-Bit Unpredictability, State Compromise, and Statistical Tests

A useful intuition for pseudorandom generation is next-bit unpredictability.

Suppose an adversary sees

$$
y_1,\ldots,y_i.
$$

It should not predict

$$
y_{i+1}
$$

with probability meaningfully better than $1/2$ for a one-bit output.

For standard efficiently computable PRG definitions, next-bit unpredictability is tightly connected to pseudorandomness: a useful next-bit predictor can be transformed into a distinguisher, and the standard next-bit characterization works in the other direction as well.

This is why "can I predict the next bit?" is such a useful security intuition.

### State compromise changes the question

Suppose an attacker learns current state $S_i$.

Now ask separately:

**Future security:** can the attacker predict outputs generated from later states?

**Past security:** can the attacker reconstruct outputs produced before compromise?

**Recovery:** if fresh entropy is mixed in later, when does the generator become unpredictable again?

Terms such as prediction resistance, backtracking resistance, and forward security are used in related but not always identical ways. A rigorous discussion should define the exact compromise game.

### Statistical tests are narrower

Suppose a generator produces:

```text
500,031 zeros
499,969 ones
```

in one million bits.

That balance is consistent with a good generator.

It is also consistent with many insecure generators.

Frequency, run-length, and autocorrelation tests can detect obvious defects. They do not prove resistance to state recovery or prediction.

A generator may pass large statistical suites and remain insecure because its recurrence is algebraically recoverable.

### Questions cryptographic analysis should ask

Instead of only asking whether output "looks random," ask:

- Can the internal state be reconstructed?
- Are future outputs predictable?
- Are outputs correlated or biased?
- Are there short cycles?
- What happens after state compromise?
- Is the seed space large enough?
- Are nonces unique under the key?
- Does the design have an explicit adversarial security argument?

These questions organize the rest of the series.

---

## Small Experiments: Looking Random Is Not Being Secure

A few toy experiments make the distinction concrete.

### A simple LCG

A linear congruential generator uses

$$
x_{i+1}=ax_i+c\pmod m.
$$

For example:

```python
def lcg(
    state,
    a=1664525,
    c=1013904223,
    m=2**32,
):
    return (
        a * state + c
    ) % m
```

Starting from one seed, the sequence is completely deterministic.

If the parameters and exact state are known, every future state is known.

Yet the numerical sequence can look irregular to a casual observer.

### Frequency can look fine

Consider only the high bit of each state:

```python
def lcg_bits(seed, count):
    x = seed
    bits = []

    for _ in range(count):
        x = lcg(x)

        bits.append(
            (x >> 31) & 1
        )

    return bits
```

A large sample can contain close to equal zeros and ones.

That does not hide the recurrence.

### Exact-state prediction

```python
seed = 0x12345678

x1 = lcg(seed)
x2 = lcg(x1)
x3 = lcg(x2)

predicted_x3 = lcg(x2)

assert predicted_x3 == x3
```

Given the state and parameters, the prediction succeeds exactly.

No statistical test can convert that predictable recurrence into a cryptographic generator.

### Keystream reuse identity

Take:

```python
p1 = b"attack at dawn"
p2 = b"attack at dusk"
```

and reuse one keystream:

```python
ks = bytes.fromhex(
    "00112233445566778899aabbccdd"
)
```

Encrypt:

```python
def xor_bytes(a, b):
    return bytes(
        x ^ y
        for x, y in zip(a, b)
    )

c1 = xor_bytes(p1, ks)
c2 = xor_bytes(p2, ks)
```

Then:

```python
assert (
    xor_bytes(c1, c2)
    ==
    xor_bytes(p1, p2)
)
```

This attack does not depend on the keystream generator being weak.

Even a perfect keystream is unsafe when reused.

So stream-cipher security has two independent requirements:

1. a secure generator;
2. correct key/nonce/counter management.

---

## Series Roadmap and Engineering Rules

This series will move from intentionally weak deterministic generators toward modern stream-cipher design.

### Linear congruential generators

LCGs expose the affine recurrence

$$
x_{i+1}=ax_i+c\pmod m.
$$

They make algebraic state prediction and parameter recovery easy to study.

### Linear feedback shift registers

LFSRs move the analysis into

$$
\mathbb F_2.
$$

They can have excellent periods and elegant polynomial theory while remaining linear enough that output can expose the recurrence.

That connects to linear complexity and Berlekamp-Massey.

### Combining LFSRs

Combining several linear generators can introduce nonlinearity, but poor combining functions can retain exploitable correlations.

This introduces correlation attacks, Boolean functions, resilience, and algebraic degree.

### RC4

RC4 shows that a large state and nonlinear-looking permutation update do not guarantee unbiased keystream.

Its historical biases and protocol failures provide a bridge from toy recurrences to deployed stream-cipher cryptanalysis.

### ChaCha20

ChaCha20 represents the modern direction.

Its ARX operations are:

- addition modulo $2^{32}$,
- rotation,
- XOR.

The series will study its state layout, quarter round, column/diagonal rounds, counter, nonce, keystream generation, and relation to ChaCha20-Poly1305.

### Dual_EC_DRBG

Dual_EC_DRBG provides a different lesson: parameter trust.

NIST removed it from SP 800-90A Rev. 1.

It remains an important historical case study in how parameter generation and hidden mathematical relationships can matter even when a construction appears sophisticated.

### Engineering rules

Carry these rules throughout the series:

1. Do not use simulation PRNGs for cryptographic secrets.
2. Do not seed cryptographic generators from timestamps or other low-entropy values.
3. Use the operating system's cryptographic randomness facility for application randomness.
4. Treat nonce uniqueness as a protocol invariant when the primitive requires it.
5. Do not infer cryptographic security from statistical tests alone.
6. Do not confuse long period with unpredictability.
7. Do not use unauthenticated stream encryption when active tampering is in scope.
8. Pin exact standards, parameters, limits, nonce rules, and test vectors.

---

## Conclusion

A pseudorandom generator is deterministic.

That is not a contradiction.

Its security comes from the computational difficulty of distinguishing its output from the intended random distribution or predicting useful future output without secret state.

The idealized model is

$$
G:\{0,1\}^{s}\rightarrow\{0,1\}^{\ell},
\qquad
\ell>s.
$$

Because only $2^s$ outputs can arise from $2^s$ seeds, deterministic expansion cannot create information-theoretic uniformity over all $2^\ell$ possible strings.

The claim is computational.

Practical generators add state, reseeding, entropy acquisition, and compromise behavior.

Modern random-bit-generation engineering separates

$$
\text{entropy source}
$$

from

$$
\text{deterministic generator}
$$

and from

$$
\text{complete system construction}.
$$

For a stream cipher, deterministic expansion becomes a keystream:

$$
KS=G(K,N,\operatorname{counter}).
$$

Encryption is

$$
C=P\oplus KS.
$$

That simplicity makes one invariant critical:

$$
\boxed{
\text{the same keystream must not encrypt two different plaintexts}
}
$$

because otherwise

$$
C_1\oplus C_2=P_1\oplus P_2.
$$

We also established that:

- statistical balance is not cryptographic security;
- long period is not state secrecy;
- nonces are commonly public;
- nonce uniqueness may matter more than unpredictability;
- state compromise is a distinct security dimension;
- stream encryption alone does not authenticate.

The conceptual progression of the new series begins here:

$$
\boxed{
\text{entropy}
\rightarrow
\text{state}
\rightarrow
\text{deterministic expansion}
\rightarrow
\text{pseudorandomness}
\rightarrow
\text{keystream}
\rightarrow
\text{nonce discipline}
\rightarrow
\text{stream-cipher security}
}
$$

The next articles will deliberately break pieces of that chain.

LCGs fail because their recurrence is algebraically visible.

LFSRs fail because linearity exposes structure over $\mathbb F_2$.

Poor LFSR combinations leak correlation.

RC4 demonstrates structural keystream bias in a real deployed design.

Dual_EC_DRBG demonstrates why parameter trust can be security-critical.

ChaCha20 shows what a modern high-performance keystream generator looks like after those lessons are taken seriously.

---

## References

1. National Institute of Standards and Technology, **SP 800-90A Rev. 1: Recommendation for Random Number Generation Using Deterministic Random Bit Generators**, June 2015.  
   https://doi.org/10.6028/NIST.SP.800-90Ar1

2. National Institute of Standards and Technology, **SP 800-90B: Recommendation for the Entropy Sources Used for Random Bit Generation**, January 2018.  
   https://doi.org/10.6028/NIST.SP.800-90B

3. National Institute of Standards and Technology, **SP 800-90C: Recommendation for Random Bit Generator (RBG) Constructions**, September 2025.  
   https://doi.org/10.6028/NIST.SP.800-90C

4. Y. Nir and A. Langley, **RFC 8439: ChaCha20 and Poly1305 for IETF Protocols**, June 2018.  
   https://www.rfc-editor.org/rfc/rfc8439

5. Oded Goldreich, **Foundations of Cryptography, Volume 1**, for computational indistinguishability and pseudorandomness.

6. Andrew C. Yao, **Theory and Applications of Trapdoor Functions**, FOCS 1982, for the foundational next-bit characterization of pseudorandom generation.
