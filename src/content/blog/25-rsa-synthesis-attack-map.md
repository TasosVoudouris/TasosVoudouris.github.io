---
title: 'RSA Synthesis: From Number Theory to Cryptanalytic Failure Modes'
description: 'A final map of the RSA branch of Cryptography From Zero: the mathematical
  foundations, key construction, algebraic cryptanalysis, small-root and lattice methods,
  validity oracles, implementation failures, structured key generation, and the boundaries
  that belong in later series.'
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
tags:
- rsa
- cryptanalysis
- attack-map
- coppersmith
- implementation-security
- public-key-cryptography
- cryptography-from-zero
difficulty: Intermediate
series: RSA Deep Dives
seriesOrder: 14
draft: false
---
When we started this series, RSA could be written in one line:

$$
c=m^e\bmod N.
$$

That line is mathematically correct.

It is also nowhere near enough to understand RSA.

After building the arithmetic from zero and then following the different failure modes one by one, I now see RSA less as a single algorithm and more as a stack:

```text
integer arithmetic
        ↓
prime generation
        ↓
modular groups and inverses
        ↓
RSA key relation
        ↓
modular exponentiation
        ↓
encoding / scheme design
        ↓
implementation
        ↓
protocol behavior
        ↓
attacker model
```

A weakness at any one of those layers can produce a completely different cryptanalytic problem.

That is the point of this final RSA post.

Not another attack.

A map.

![RSA scientific synthesis and cryptanalytic attack map](/images/blog/25-rsa-synthesis-map.svg)

*“RSA is broken” is almost never a useful scientific statement. We have to say which layer, which assumption, which parameter regime, which encoding, or which implementation behavior is being studied.*

---

## 1. The mathematical core

The basic two-prime RSA construction begins with:

$$
N=pq.
$$

For modern RSA notation, define:

$$
\lambda(N)
=
\operatorname{lcm}(p-1,q-1).
$$

Choose the public exponent $e$ so that:

$$
\gcd(e,\lambda(N))=1.
$$

Then compute:

$$
d=e^{-1}\pmod{\lambda(N)}.
$$

The public and private maps are modular exponentiations:

$$
m\mapsto m^e\bmod N,
$$

and:

$$
c\mapsto c^d\bmod N.
$$

But even this compact construction already depends on most of the mathematical foundations we built earlier:

```text
integer division
    -> Euclidean algorithm
    -> GCD
    -> Bézout
    -> modular inverse
    -> modular arithmetic
    -> multiplicative groups
    -> element order
    -> primes
    -> CRT
    -> fast modular exponentiation
    -> RSA
```

That dependency chain matters because the later cryptanalysis repeatedly reuses exactly the same objects.

The GCD that first appeared as:

$$
\gcd(48,18)
$$

later became a factor-recovery operation after an RSA fault.

Bézout coefficients that first constructed modular inverses later combined public exponents in the common-modulus setting.

CRT first reconstructed integers from residues, then accelerated RSA, then created an implementation fault surface.

The same mathematics keeps returning in different roles.

---

## 2. The RSA map: what each result actually exploits

The most useful way to organize everything we studied is by **failure layer**, not by attack name.

| Layer | Extra structure or leakage | Main mathematical tool | Representative deep dive |
|---|---|---|---|
| Primitive / textbook scheme | deterministic public map, multiplicativity | modular arithmetic | [Textbook RSA](/blog/13-rsa-deep-dive-textbook-rsa-fails/) |
| Reused parameters | same modulus, different coprime exponents | Bézout + modular inverses | [Common Modulus](/blog/14-rsa-common-modulus-attack/) |
| Repeated low-degree message | same message, small $e$, different moduli | CRT + integer root | [Håstad](/blog/15-rsa-hastad-broadcast-attack/) |
| Small private exponent | unusually small $d$ | continued fractions | [Wiener](/blog/16-rsa-wiener-attack/) |
| Small algebraic unknown | bounded modular root | coefficient lattices + LLL | [Coppersmith](/blog/17-rsa-coppersmith-from-zero/) |
| Larger small-$d$ regime | bivariate small-root structure | Coppersmith-style lattices | [Boneh–Durfee](/blog/18-rsa-boneh-durfee/) |
| Partial secret information | known factor/key bits | divisor small roots | [Partial Key Exposure](/blog/19-rsa-partial-key-exposure/) |
| Related plaintexts | known affine message relation | polynomial GCD | [Franklin–Reiter](/blog/20-rsa-franklin-reiter/) |
| Small unknown relation | short pad difference | resultant + Coppersmith + polynomial GCD | [Short-Pad RSA](/blog/21-rsa-short-pad/) |
| Decoder behavior | PKCS #1 v1.5 validity distinction | modular interval arithmetic | [Bleichenbacher](/blog/22-rsa-bleichenbacher/) |
| Decoder boundary | OAEP partial validity information | boundary placement + interval narrowing | [Manger](/blog/23-rsa-manger/) |
| Key generation | primes from restricted algebraic family | subgroup fingerprint + small-root reconstruction | [ROCA](/blog/24-rsa-roca/) |
| Private implementation | secret-dependent execution | side-channel reasoning | [Fast Modular Exponentiation](/blog/08-fast-modular-exponentiation-side-channels/) |
| Private implementation | inconsistent CRT branch | GCD + CRT structure | [CRT Faults](/blog/09-rsa-crt-fault-attacks/) |

This table is the RSA branch in one view.

The attacks do not all challenge the same assumption.

That is the first thing I would want a reader to remember.

---

## 3. The deep connections between the branches

The posts look different, but several long chains connect them.

### Euclid keeps returning

We began with:

$$
\gcd(a,b).
$$

Then:

```text
Euclid
    -> Extended Euclid
    -> Bézout coefficients
    -> modular inverses
```

Those same ideas later become:

```text
common modulus
    -> combine public exponents

CRT fault
    -> GCD reveals a factor

Franklin–Reiter
    -> Euclid again, now on polynomials
```

So there is really one recurring algorithmic idea appearing over different algebraic objects.

### CRT has two opposite roles

CRT is a perfect example of why a mathematical tool is not “secure” or “insecure” by itself.

It gives us:

```text
residue reconstruction
    -> correctness tool

CRT-RSA
    -> performance optimization
```

but the independent $p$ and $q$ branches also mean:

```text
one corrupted branch
    + one correct branch
    -> algebraic inconsistency
    -> factor-revealing GCD
```

The theorem is not the problem.

The computational architecture changes the attacker model.

### Coppersmith is a language, not one attack

After the dedicated Coppersmith article, several apparently unrelated RSA results became instances of the same modelling pattern:

```text
known plaintext prefix
    -> small unknown suffix

known prime prefix
    -> small unknown factor suffix

small private exponent
    -> bivariate bounded unknowns

short random padding
    -> small unknown relation
```

The important question became:

> Can I turn the available information into a polynomial congruence with an unusually small root?

That is much more useful than memorizing a list of named lattice attacks.

### Oracles change the layer completely

Bleichenbacher and Manger do something different.

They do not primarily exploit an unusual RSA key.

They exploit an observable predicate after private-key computation.

The structure is:

$$
c' = c\,s^e\bmod N
$$

or:

$$
c_f=c\,f^e\bmod N,
$$

combined with a decoder response that leaks numerical information about:

$$
ms\bmod N
$$

or:

$$
mf\bmod N.
$$

The primitive is mathematically correct.

The information channel appears in the surrounding implementation behavior.

### ROCA moves the problem all the way back to key generation

ROCA closes the loop.

Instead of asking how RSA is used, it asks where $p$ and $q$ came from.

A prime can be large and pass primality testing while still belonging to an algebraically restricted family.

So RSA security begins **before**:

$$
N=pq.
$$

It begins with the distribution from which $p$ and $q$ are sampled.

---

## 4. What secure RSA actually requires

After all of these posts, I would not summarize RSA security as:

> factoring $N$ is hard.

Factoring is obviously central.

If an adversary factors:

$$
N=pq,
$$

the trapdoor is lost.

But a secure RSA deployment needs several layers to be correct simultaneously.

### Key generation

The primes must be:

- independently generated;
- appropriately distributed;
- produced from a cryptographically sound random source;
- large enough;
- free from dangerous structural restrictions.

ROCA showed why the last point cannot be replaced by a bit-length check.

### Parameters

The exponents must satisfy the required number-theoretic relations.

Private parameters must not be chosen inside known abnormal regimes such as Wiener's or Boneh–Durfee's small-$d$ regions.

RSA moduli must not be casually reused across independent key pairs.

### Encoding

The map:

$$
m\mapsto m^e\bmod N
$$

is the RSA primitive.

It is not a secure encryption scheme.

Randomized, standardized encoding changes the mathematical object presented to the RSA primitive and removes the direct textbook relations exploited by many classical examples.

### Error behavior

A decoder must not turn internal validity checks into distinguishable external behavior.

Bleichenbacher and Manger show why even apparently tiny predicates can become adaptive information channels.

### Private computation

Secret-dependent timing, cache behavior, power, electromagnetic leakage, or faults can expose information even when the output equation is mathematically correct.

CRT improves performance but introduces branch consistency obligations.

### Composition

RSA should not be imagined as a bulk-data cipher.

The system-level pattern is closer to:

```text
public-key mechanism
        ↓
compact secret / keying material
        ↓
key derivation / schedule
        ↓
authenticated symmetric encryption
```

So security belongs to the complete construction, not to one exponentiation.

---

## 5. What we are deliberately moving elsewhere

This synthesis closes the **RSA primitive, encryption, implementation, and cryptanalysis branch** of Cryptography From Zero.

There are still RSA-related subjects, but they belong in other conceptual homes.

### RSA signatures

RSASSA-PSS, signature encoding, signature security notions, and signature-specific failures belong in the future **Digital Signatures** branch.

I do not want to mix:

```text
RSA encryption
```

with:

```text
RSA signatures
```

just because both eventually call modular exponentiation.

They are different schemes with different security goals.

### RSA-KEM and hybrid encryption

RSA-based key encapsulation and the broader KEM–DEM architecture belong with **Hybrid Encryption and KEMs**.

That will also give us a cleaner bridge to modern post-quantum KEMs.

### Certificates and PKI

RSA key representation, certificate binding, trust chains, and PKI lifecycle belong in the future **PKI / Certificates** branch.

### Quantum cryptanalysis

Shor's algorithm changes the asymptotic status of integer factorization on a sufficiently capable fault-tolerant quantum computer.

But the full derivation belongs in the quantum part of the project rather than being compressed into an RSA appendix.

So the RSA branch is not ending because there is nothing left to say.

It is ending because the remaining topics have better conceptual homes.

---

## 6. The final RSA mental model

If I had to compress everything into one picture, it would be this:

```text
                    RSA
                     |
        +------------+-------------+
        |            |             |
    mathematics   construction  implementation
        |            |             |
   N = p*q       prime generation  exponentiation
   inverses      parameters        CRT
   CRT           encoding          errors
        |            |             |
        +------------+-------------+
                     |
                 protocol
                     |
             observable behavior
                     |
                  security
```

And the cryptanalytic questions become:

```text
Is a parameter unusually small?
Is a modulus or message reused?
Is part of a secret already known?
Do two plaintexts satisfy a relation?
Is there a small polynomial root?
Does a decoder leak a predicate?
Does private computation leak behavior?
Did key generation restrict the prime distribution?
```

Different answers lead to different mathematics.

That is the real RSA attack map.

---

## 7. Where we go next

This RSA branch started from:

$$
\gcd(48,18)
$$

and eventually reached:

- continued fractions,
- polynomial rings,
- LLL lattices,
- Coppersmith small roots,
- resultants,
- adaptive interval oracles,
- subgroup fingerprints,
- implementation faults.

That progression is exactly what I wanted from **Cryptography From Zero**.

Not:

```text
learn RSA API
        ↓
move on
```

but:

```text
build the mathematics
        ↓
build the primitive
        ↓
study its assumptions
        ↓
change one assumption
        ↓
observe what fails
        ↓
understand the cryptanalysis
        ↓
understand the mitigation
```

So I am comfortable closing RSA here.

The next public-key family should now feel different rather than repetitive.

Diffie–Hellman already introduced the discrete-logarithm world.

A natural continuation is to turn that same group structure into encryption:

$$
\boxed{\text{ElGamal}}
$$

and then move from finite-field groups toward:

$$
\boxed{\text{elliptic-curve cryptography}}.
$$

But before adding another cryptographic primitive, the site itself now has enough material that it deserves to be organized properly.

**Next:** build the CryptoCave site around the complete Cryptography From Zero foundation and RSA series.
