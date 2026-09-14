---
title: 'RSA Deep Dive XII: ROCA From Zero — When Prime Generation Leaves a Public Algebraic Fingerprint'
description: ROCA showed that an RSA modulus can have the expected size and still be weak because its secret primes come from a severely restricted algebraic family. We derive the subgroup fingerprint, reproduce it on a fixed toy generator, and connect the entropy loss to Coppersmith-style reconstruction.
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Implementation Security
- Lattice Methods
tags:
- rsa
- roca
- key-generation
- structured-primes
- coppersmith
- subgroup
- implementation-security
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 12
draft: false
---
Most of the RSA failures we have studied so far happened **after** the primes had already been generated.

We changed:

- the plaintext structure,
- the exponent regime,
- the encoding,
- the oracle behavior,
- the implementation path.

ROCA is different.

The problem begins earlier:

```text
prime generation
        ↓
restricted algebraic family
        ↓
loss of entropy
        ↓
public modulus inherits a fingerprint
        ↓
specialized factor-recovery method becomes possible
```

That is why I think ROCA is a very good final RSA deep dive.

It forces us to ask a more fundamental question:

> What does it actually mean to say that an RSA prime was generated “randomly enough”?

A prime can be:

- large,
- mathematically prime,
- distinct from the other factor,
- compatible with the RSA exponent,

and still come from a dangerously small structured family.

![ROCA: structured RSA primes leave a subgroup fingerprint in the public modulus](/images/blog/24-rsa-roca.svg)

*ROCA is fundamentally a key-generation failure. The modulus inherits algebraic structure from the distribution used to construct the secret primes.*

Relevant earlier posts:

- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Multiplicative Groups, Orders, and Generators](/blog/04-multiplicative-groups-orders-generators/)
- [Coppersmith From Zero](/blog/17-rsa-coppersmith-from-zero/)
- [Partial Key Exposure From Zero](/blog/19-rsa-partial-key-exposure/)

---

## 1. The prime family discovered in ROCA

Nemec, Sýs, Švenda, Klinec, and Matyáš analyzed RSA keys produced by a cryptographic library used in Infineon hardware.

They recovered a striking structure.

The generated primes had the form:

$$
\boxed{
p
=
kM
+
\left(
65537^a\bmod M
\right),
}
$$

where:

- $M$ is a known primorial,
- $k$ is an integer,
- $a$ is an integer,
- $65537$ is a fixed generator-like value used by the construction.

A primorial is a product of consecutive small primes:

$$
M
=
2\cdot3\cdot5\cdot7\cdots P_n.
$$

Reduce the prime equation modulo $M$:

$$
p
\equiv
65537^a
\pmod M.
$$

So the residue of $p$ is not arbitrary.

It must belong to the subgroup:

$$
\boxed{
G=\langle65537\rangle
\subseteq
\mathbb Z_M^\times.
}
$$

This is already the structural weakness.

Instead of allowing the prime residue modulo $M$ to range through the full unit group, the construction restricts it to one comparatively small cyclic subgroup.

---

## 2. Why the public modulus inherits the fingerprint

Let:

$$
N=pq.
$$

Suppose both primes have the structured form:

$$
p
\equiv
65537^a
\pmod M,
$$

and:

$$
q
\equiv
65537^b
\pmod M.
$$

Multiply:

$$
N
=
pq
\equiv
65537^a65537^b
\pmod M.
$$

Therefore:

$$
\boxed{
N
\equiv
65537^{a+b}
\pmod M.
}
$$

So:

$$
N\bmod M
$$

also lies in:

$$
G=\langle65537\rangle.
$$

That means the secret prime structure becomes testable from the **public modulus alone**.

This is the fingerprint.

The factorization does not have to be known.

The private exponent does not have to be known.

The public key already contains evidence about the distribution from which its hidden factors were generated.

---

## 3. Why subgroup membership is such a strong signal

Normally, a random invertible residue modulo $M$ can lie anywhere in:

$$
\mathbb Z_M^\times.
$$

The number of such residues is:

$$
\varphi(M).
$$

But a ROCA-style modulus is constrained to:

$$
G=\langle65537\rangle,
$$

whose size is:

$$
\operatorname{ord}_M(65537).
$$

If:

$$
|G|
\ll
\varphi(M),
$$

then membership in $G$ is rare for an unrelated random modulus.

The fingerprint test is conceptually:

```text
compute r = N mod M

ask:
r in <65537> mod M ?
```

Equivalently, one may ask whether a discrete logarithm base $65537$ exists inside that subgroup.

The original ROCA work exploited the fact that the subgroup order is smooth enough for efficient discrete-log computation using Pohlig–Hellman.

This creates a fascinating inversion of our earlier Diffie–Hellman story.

There we wanted a large subgroup whose discrete logarithm was hard.

Here the subgroup induced by key generation is deliberately structured and smooth enough that its membership can be recognized efficiently.

---

## 4. A tiny subgroup model

For the real ROCA construction, $M$ is large.

For a hand-auditable model, use the much smaller primorial:

$$
M
=
2\cdot3\cdot5\cdot7\cdot11\cdot13
=
30\,030.
$$

Take:

$$
g=65\,537.
$$

Modulo $M$:

$$
g\bmod M
=
5\,477.
$$

The multiplicative order is:

$$
\boxed{
\operatorname{ord}_M(g)=12.
}
$$

So the subgroup:

$$
G=\langle g\rangle
$$

contains only twelve residues.

Explicitly:

```text
1
5477
27589
24023
12541
8447
18019
11483
9571
18017
529
14453
```

Meanwhile:

$$
\varphi(30\,030)=5\,760.
$$

So only:

$$
\frac{12}{5760}
=
\frac1{480}
$$

of the unit residues belong to this toy subgroup.

Already the fingerprint is very selective.

---

## 5. Construct two fixed structured toy primes

Take:

$$
a=1,
\qquad
k=11.
$$

Then:

$$
g^1\bmod M
=
5\,477.
$$

Construct:

$$
p
=
11M+5\,477.
$$

Thus:

$$
p
=
335\,807.
$$

This number is prime.

Now choose:

$$
b=5,
\qquad
\ell=11.
$$

We have:

$$
g^5\bmod M
=
8\,447.
$$

So:

$$
q
=
11M+8\,447
=
338\,777.
$$

This is also prime.

The toy RSA modulus is:

$$
N=pq
=
113\,763\,688\,039.
$$

Now reduce modulo $M$:

$$
N\bmod M
=
18\,019.
$$

But:

$$
g^{a+b}
=
g^6
\equiv
18\,019
\pmod M.
$$

Therefore:

$$
\boxed{
N\bmod M
=
g^6\bmod M.
}
$$

The public modulus carries exactly the predicted subgroup fingerprint.

---

## 6. Compare with an unrelated modulus

Now take two unrelated toy primes of a similar size:

$$
p'=330\,017,
$$

$$
q'=342\,449.
$$

Their product is:

$$
N'
=
113\,013\,991\,633.
$$

Reduce it modulo $M$:

$$
N'\bmod M
=
20\,563.
$$

But:

$$
20\,563
\notin
G.
$$

So the toy detector reports:

```text
structured modulus:
fingerprint present

comparison modulus:
fingerprint absent
```

Nothing was factored.

We only computed:

$$
N\bmod M
$$

and checked subgroup membership.

That is the scientific essence of ROCA fingerprinting.

---

## 7. Where the entropy disappeared

The prime equation is:

$$
p=kM+g^a\bmod M.
$$

Once $M$ is fixed, the prime is controlled by only:

- the integer $k$,
- the subgroup exponent $a$.

That is much more restrictive than selecting an arbitrary prime of the same bit length.

The original ROCA paper gives a concrete example for 512-bit RSA.

There the hidden prime has roughly:

$$
256
$$

bits.

But the corresponding construction parameters contain only about:

- $37$ bits for $k$,
- $62$ bits for $a$.

So the effective candidate family is on the order of:

$$
2^{99}
$$

rather than the full generic 256-bit prime space.

The important point is not simply:

```text
less randomness
```

but:

```text
less randomness
+
known algebraic organization
```

That combination is what makes the loss exploitable.

---

## 8. Why this is not the same as a weak RNG

This distinction matters.

Several historical RSA failures came from weak randomness:

```text
bad seed
        ↓
predictable prime candidates
```

or:

```text
insufficient entropy
        ↓
different keys accidentally share a prime
        ↓
GCD factors both moduli
```

ROCA is different.

The researchers explicitly emphasized that the weakness did **not** depend on a faulty random-number generator.

Even perfectly random choices of the internal construction variables still produce primes inside the restricted algebraic family:

$$
p=kM+g^a\bmod M.
$$

So the randomness can be perfectly healthy **inside the wrong sample space**.

That is a much deeper key-generation lesson.

---

## 9. Fingerprinting is not yet factorization

This is another distinction worth keeping very clear.

From:

$$
N\bmod M
\in
\langle65537\rangle,
$$

we can infer that the public modulus is consistent with the structured generation family.

But this does not immediately hand us:

$$
p
$$

and:

$$
q.
$$

The full ROCA factorization method uses additional structure.

Conceptually, once candidate residue information about a factor is sufficiently constrained, the factor can be written in a form like:

$$
p=r+kM',
$$

where:

- $r$ is drawn from a restricted known family,
- $M'$ is a carefully selected divisor of the original primorial,
- the remaining unknown $k$ is small enough relative to the modulus.

Now the problem starts to resemble the partial-factor Coppersmith problem we studied earlier:

$$
p=p_0+x.
$$

The ROCA researchers developed a specialized Coppersmith/Howgrave-Graham strategy and an alternative prime representation that made the reconstruction computationally feasible for affected key sizes.

So the conceptual bridge is:

```text
subgroup fingerprint
        ↓
restricted candidate residues
        ↓
rewrite hidden prime with small remaining uncertainty
        ↓
Coppersmith-style factor reconstruction
```

The companion experiment in this article intentionally stops before the last step.

We have already built Coppersmith separately.

The new scientific idea here is the **structured key distribution and public fingerprint**.

---

## 10. ROCA reconnects to several earlier posts

ROCA looks like one isolated 2017 vulnerability.

Mathematically it connects a surprising amount of the series.

### Multiplicative groups

We need:

$$
\langle g\rangle
\subseteq
\mathbb Z_M^\times.
$$

### Element order

The fingerprint space has size:

$$
\operatorname{ord}_M(g).
$$

### Pohlig–Hellman

A smooth subgroup order makes discrete logarithms efficient enough for fingerprinting.

### Partial-factor Coppersmith

Once enough residue information is known, the remaining factor uncertainty becomes a small-root problem.

### RSA key generation

The final failure exists because key generation sampled primes from a restricted family.

So:

```text
groups
+ orders
+ smoothness
+ prime generation
+ Coppersmith
=
ROCA
```

This is exactly why I wanted the series to begin with elementary algebra rather than start directly from RSA APIs.

---

## 11. A large modulus is not automatically a strong RSA key

This is probably the single sentence I want to keep from ROCA.

Suppose somebody shows us:

```text
N is 2048 bits
```

That tells us the size of the integer.

It does **not** tell us that its hidden primes were drawn from a cryptographically appropriate distribution.

Security depends on much more:

- prime generation procedure,
- entropy,
- structural constraints,
- independence,
- implementation,
- validation,
- surrounding protocol.

The mature CryptoBible version of this idea is:

> a 2048-bit modulus is not automatically a 2048-bit-quality RSA key.

ROCA is perhaps the clearest real-world example of that statement.

The bit length looked normal.

The distribution did not.

---

## 12. Detection as a defensive consequence of structure

There is one interesting consequence of the public fingerprint.

The same feature that makes vulnerable keys identifiable also makes remediation easier.

If the family leaves a distinctive public residue property, one can test one's own public keys for membership in the affected family without accessing private key material.

The original researchers released detectors specifically for this defensive purpose.

This is a rare case where:

$$
\boxed{
\text{public cryptanalytic fingerprint}
}
$$

also becomes a practical inventory and migration tool.

For our article, however, the detector remains deliberately toy-sized and fixed.

It simply demonstrates subgroup membership on two hard-coded mathematical examples.

---

## 13. What the companion experiment checks

The site package includes one small Python experiment.

It does not factor RSA keys.

It checks only:

```text
1. build toy primorial M
2. compute ord_M(65537)
3. enumerate the tiny subgroup <65537>
4. construct two fixed structured primes
5. verify p mod M and q mod M lie in the subgroup
6. construct N = p*q
7. verify N mod M = 65537^(a+b) mod M
8. verify the public fingerprint is present
9. compare with one fixed unrelated modulus
10. verify its residue is outside the subgroup
```

The output makes the distinction visible:

```text
structured generation
        -> subgroup residue

ordinary comparison pair
        -> residue outside subgroup
```

That is enough to understand the fingerprint mechanism completely.

---

## 14. What I want to remember

ROCA begins with a prime-generation rule:

$$
p=kM+g^a\bmod M,
$$

where:

$$
g=65537.
$$

Therefore:

$$
p\bmod M\in\langle g\rangle.
$$

For:

$$
N=pq,
$$

we get:

$$
\boxed{
N\bmod M
\in
\langle g\rangle.
}
$$

More precisely:

$$
N
\equiv
g^{a+b}
\pmod M.
$$

So:

```text
secret prime structure
        ↓
survives multiplication
        ↓
appears in public N mod M
        ↓
subgroup-membership fingerprint
```

The factorization stage then uses the restricted family to reduce the remaining factor uncertainty until Coppersmith-style machinery becomes effective.

The deepest lesson is:

$$
\boxed{
\text{prime}
\neq
\text{cryptographically well-generated prime}.
}
$$

And:

$$
\boxed{
\text{correct RSA arithmetic}
\neq
\text{secure RSA key generation}.
}
$$

---

## References

1. Matúš Nemec, Marek Sýs, Petr Švenda, Dušan Klinec, Vashek Matyáš, **“The Return of Coppersmith's Attack: Practical Factorization of Widely Used RSA Moduli”**, *ACM CCS 2017*, pp. 1631–1648, 2017.  
   https://doi.org/10.1145/3133956.3133969

2. CRoCS, Masaryk University, **“ROCA: Vulnerable RSA generation (CVE-2017-15361)”**.  
   https://crocs.fi.muni.cz/public/papers/rsa_ccs17

3. Don Coppersmith, **“Finding a Small Root of a Univariate Modular Equation”**, *EUROCRYPT '96*, LNCS 1070, pp. 155–165, 1996.

4. Nick Howgrave-Graham, **“Finding Small Roots of Univariate Modular Equations Revisited”**, *Cryptography and Coding 1997*, LNCS 1355, pp. 131–142.

---

At this point the RSA deep-dive map is genuinely broad:

```text
textbook algebra
        -> determinism / malleability

reused structure
        -> common modulus / Håstad

small private exponent
        -> Wiener / Boneh–Durfee

small algebraic unknowns
        -> Coppersmith / partial exposure / short pad

related messages
        -> Franklin–Reiter

decoding predicates
        -> Bleichenbacher / Manger

key-generation structure
        -> ROCA

implementation computation
        -> timing / CRT fault
```

That is enough RSA to stop treating it as one formula:

$$
c=m^e\bmod N.
$$

We now have a much better picture:

> RSA security is an ecosystem of number theory, parameter generation, encoding, implementation behavior, and protocol composition.

A natural final RSA post would now be a short **RSA Synthesis and Attack Map**, collecting the entire branch into one visual taxonomy before moving to ElGamal/ECC.
