---
title: "Prime Numbers III: Strong Pseudoprimes and Fixed-Base Miller–Rabin"
description: "An advanced study of strong pseudoprimes, adversarial fixed-base Miller–Rabin testing, the Arnault construction, Carmichael structure, and the limits of probable-prime testing."
pubDate: "2025-05-05"
updatedDate: "2026-09-16"
topics:
  - "Number Theory"
  - "Cryptanalysis"
  - "Cryptographic Engineering"
tags:
  - "miller-rabin"
  - "strong-pseudoprime"
  - "carmichael-numbers"
  - "arnault"
  - "primality-testing"
difficulty: "Advanced"
series: "Elementary Number Theory Reference"
seriesOrder: 9
sourcePath: "experiments/ready-material/primes"
draft: false
---

In Part II of our study of primes, we developed the Miller-Rabin primality test and saw why it is dramatically stronger than a simple Fermat test.

For an odd composite integer \(n\), a random Miller-Rabin base detects compositeness with high probability.

More precisely, the set of strong-liar bases is bounded by a fraction of the available bases.

That naturally raises a more adversarial question:

> What if the bases are not random?

Suppose an implementation always tests:

\[
a_1,a_2,\ldots,a_t
\]

and those bases are publicly known.

Can we deliberately construct a composite integer \(N\) that is a strong pseudoprime to every one of those particular bases?

The answer is yes.

This does **not** break the mathematical guarantee of randomized Miller-Rabin.

Instead, it exposes a different security model:

\[
\boxed{
\text{random candidate + random bases}
}
\]

is not the same problem as:

\[
\boxed{
\text{adversarial candidate + predictable fixed bases}.
}
\]

The distinction is the central subject of this article.

We will study:

- strong pseudoprimes,
- fixed versus random bases,
- Carmichael structure,
- quadratic characters,
- the construction associated with François Arnault,
- the role of the Chinese Remainder Theorem,
- and why none of this contradicts the standard Miller-Rabin error bound.

---

## Table of Contents

- [Strong pseudoprimes](#strong-pseudoprimes)
- [Random bases versus fixed bases](#random-bases-versus-fixed-bases)
- [A small fixed-base counterexample](#a-small-fixed-base-counterexample)
- [Testing a fixed base in Python](#testing-a-fixed-base-in-python)
- [Historical context](#historical-context)
- [Why Carmichael numbers are not enough](#why-carmichael-numbers-are-not-enough)
- [Korselt’s criterion](#korselts-criterion)
- [The structural idea behind Arnault’s construction](#the-structural-idea-behind-arnaults-construction)
- [Controlling quadratic characters](#controlling-quadratic-characters)
- [Translating conditions onto (p_1)](#translating-conditions-onto-p_1)
- [Why the (k_i) are chosen carefully](#why-the-k_i-are-chosen-carefully)
- [From local residue conditions to CRT](#from-local-residue-conditions-to-crt)
- [Constructing the prime factors](#constructing-the-prime-factors)
- [The construction pipeline](#the-construction-pipeline)
- [Why the resulting number is Carmichael](#why-the-resulting-number-is-carmichael)
- [Why selected Miller-Rabin bases can become liars](#why-selected-miller-rabin-bases-can-become-liars)
- [Verification comes last](#verification-comes-last)
- [Research implementation architecture](#research-implementation-architecture)
- [A safer experimental target](#a-safer-experimental-target)
- [Bleichenbacher and adversarial primality testing](#bleichenbacher-and-adversarial-primality-testing)
- [What this does not break](#what-this-does-not-break)
- [Fixed bases are not automatically wrong](#fixed-bases-are-not-automatically-wrong)
- [Bounded deterministic Miller-Rabin](#bounded-deterministic-miller-rabin)
- [Why adding more fixed bases is not a complete argument](#why-adding-more-fixed-bases-is-not-a-complete-argument)
- [Random versus adversarial candidate generation](#random-versus-adversarial-candidate-generation)
- [Related approach: Bleichenbacher’s construction](#related-approach-bleichenbachers-construction)
- [Meet-in-the-middle subset search](#meet-in-the-middle-subset-search)
- [Why this belongs after polynomial congruences](#why-this-belongs-after-polynomial-congruences)
- [The security lesson](#the-security-lesson)
- [Production guidance](#production-guidance)
- [Practice and checkpoint](#practice-and-checkpoint)
- [Reader checkpoint](#reader-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Closing the prime-number sequence](#closing-the-prime-number-sequence)
- [Closing the Elementary Number Theory Reference](#closing-the-elementary-number-theory-reference)

---

## Strong pseudoprimes

Recall the Miller-Rabin condition.

Let:

\[
n>2
\]

be odd, and write:

\[
n-1
=
2^s d,
\]

where \(d\) is odd.

For a base \(a\) satisfying:

\[
\gcd(a,n)=1,
\]

a Miller-Rabin round accepts if either:

\[
a^d
\equiv1
\pmod n,
\]

or if for some:

\[
0\le r<s,
\]

we have:

\[
a^{2^r d}
\equiv-1
\pmod n.
\]

If \(n\) is prime, every admissible base satisfies this condition.

If \(n\) is composite but still satisfies the condition for a particular base \(a\), then \(n\) is called a:

\[
\boxed{
\text{strong pseudoprime to base }a.
}
\]

We may write informally:

\[
\operatorname{spsp}(n,a).
\]

The important phrase is:

> **to base \(a\)**.

Strong pseudoprimality is not an intrinsic binary property of the composite integer alone.

It depends on the chosen base.

A composite may pass base \(2\) and fail base \(3\).

Another may pass:

\[
2,3,5,7
\]

but fail base \(11\).

---

## Random bases versus fixed bases

The standard probabilistic interpretation of Miller-Rabin assumes that bases are selected independently from an appropriate distribution.

For every fixed odd composite \(n\), the strong-liar set is small.

In the usual formulation:

\[
\boxed{
\Pr[
\text{random base is a strong liar}
]
\le
\frac14.
}
\]

Thus \(k\) independent random rounds give the familiar upper bound:

\[
\boxed{
\Pr[
\text{fixed composite survives all }k\text{ rounds}
]
\le
4^{-k}.
}
\]

But suppose an implementation always uses:

\[
A
=
\{
2,3,5,7
\}.
\]

Then the adversary does not need to find a composite that fools a random base.

The task becomes:

\[
\boxed{
\text{find composite }N
\text{ that fools every }a\in A.
}
\]

That is a completely different construction problem.

The \(1/4\) theorem does not say that every set containing four particular bases must expose every composite.

It says that, for each fixed composite, most possible bases are witnesses.

A carefully chosen composite may nevertheless contain a specific finite set of bases entirely inside its liar set.

---

## A small fixed-base counterexample

Consider:

\[
N
=
3215031751.
\]

It is composite:

\[
\boxed{
3215031751
=
151
\cdot
751
\cdot
28351.
}
\]

Yet it is a strong pseudoprime to each of the bases:

\[
2,3,5,7.
\]

So a primality routine consisting only of:

```text
Miller-Rabin base 2
Miller-Rabin base 3
Miller-Rabin base 5
Miller-Rabin base 7
```

would accept this composite.

But base \(11\) exposes it.

This is the correct mental model:

```text
passes bases 2,3,5,7
        ≠
prime
```

unless we also have a proven theorem saying that those bases are sufficient over the **specific bounded input range** being tested.

---

## Testing a fixed base in Python

We can expose the strong probable-prime condition directly:

```python
from math import gcd


def is_sprp_base(n, a):
    """
    Return True if n passes a Miller-Rabin
    strong probable-prime test to base a.
    """
    if n == 2:
        return True

    if n < 2 or n % 2 == 0:
        return False

    a %= n

    if a in (0, 1):
        return True

    if gcd(a, n) != 1:
        return False

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    x = pow(a, d, n)

    if x in (1, n - 1):
        return True

    for _ in range(s - 1):
        x = pow(x, 2, n)

        if x == n - 1:
            return True

        if x == 1:
            return False

    return False
```

Now:

```python
N = 3215031751

for a in (2, 3, 5, 7, 11):
    print(
        a,
        is_sprp_base(N, a),
    )
```

gives the pattern:

```text
2   True
3   True
5   True
7   True
11  False
```

This example is enough to establish the basic phenomenon.

We do not need any sophisticated construction yet.

---

## Historical context

The study of deliberately constructed strong pseudoprimes predates modern cryptographic software.

### François Arnault

In 1995, François Arnault published work constructing composite integers that pass Rabin-Miller testing for several predetermined bases.

The goal was precisely to demonstrate that a test using a known fixed list of bases can be fooled by carefully structured composite inputs.

Later in the same year, Arnault published a more general treatment of constructing Carmichael numbers that are strong pseudoprimes to several bases.

The relevant idea is therefore a **1990s number-theoretic construction**, not a result originating in 2018.

### Bleichenbacher

In 2005, Daniel Bleichenbacher demonstrated why this issue can become a protocol problem rather than merely a number-theory curiosity.

A primality test in GNU Crypto used a predictable fixed base strategy.

Bleichenbacher constructed pseudoprime parameters that passed the implementation's checks and used the resulting weakness in an attack on the library's SRP implementation.

The important lesson was not:

> Miller-Rabin is broken.

It was:

> A primality test may be mathematically sound in one threat model and unsafe when implemented with predictable tests against adversarially supplied inputs.

### Prime and Prejudice

In 2018, Martin Albrecht, Jake Massimo, Kenneth Paterson, and Juraj Somorovsky systematically studied **primality testing under adversarial conditions**.

Their work analyzed how implementations behave when the value being tested is not a randomly generated candidate but may instead have been deliberately selected to exploit the testing strategy.

They reused and extended classical pseudoprime-construction techniques, including Arnault-style methods, to study real software.

So the historical line is:

\[
\boxed{
\text{Arnault}
\rightarrow
\text{constructed fixed-base strong pseudoprimes}
}
\]

\[
\boxed{
\text{Bleichenbacher}
\rightarrow
\text{demonstrated protocol consequences}
}
\]

\[
\boxed{
\text{Albrecht et al.}
\rightarrow
\text{systematic adversarial analysis}
}
\]

---

## Why Carmichael numbers are not enough

A Carmichael number \(N\) satisfies:

\[
a^{N-1}
\equiv1
\pmod N
\]

for every:

\[
\gcd(a,N)=1.
\]

So Carmichael numbers defeat ordinary Fermat testing.

But Miller-Rabin examines more structure.

Therefore:

\[
\boxed{
\text{Carmichael}
\not\Rightarrow
\text{strong pseudoprime to every base}.
}
\]

In fact, no odd composite integer can be a strong pseudoprime to every admissible base.

The strong-liar fraction is bounded.

So there is no direct Miller-Rabin analogue of a Carmichael number that fools **all** bases.

Instead, the construction problem is:

> Given a finite set of bases \(A\), construct a Carmichael number that is also a strong pseudoprime to every \(a\in A\).

This extra condition is where quadratic characters and the structure of the prime factors become important.

---

## Korselt's criterion

Recall that a composite integer \(N\) is Carmichael if and only if:

1. \(N\) is square-free;
2. for every prime divisor:
   \[
   p\mid N,
   \]
   we have:
   \[
   p-1\mid N-1.
   \]

Thus, if:

\[
N
=
p_1p_2\cdots p_h
\]

with distinct primes \(p_i\), then we want:

\[
\boxed{
p_i-1
\mid
N-1
}
\]

for every \(i\).

This provides the first structural constraint in an Arnault-style construction.

---

## The structural idea behind Arnault's construction

Let:

\[
A
=
\{
a_1,\ldots,a_t
\}
\]

be the finite set of Miller-Rabin bases that we want the final composite to pass.

We aim to construct:

\[
\boxed{
N
=
p_1p_2\cdots p_h
}
\]

where the \(p_i\) are distinct primes.

Arnault-style constructions relate the prime factors by equations of the form:

\[
\boxed{
p_i
=
k_i(p_1-1)+1,
}
\]

with:

\[
k_1=1.
\]

Thus:

\[
p_i-1
=
k_i(p_1-1).
\]

The values:

\[
k_2,\ldots,k_h
\]

are chosen as part of the construction.

However, the relation

\[
p_i=k_i(p_1-1)+1
\]

**by itself is not sufficient** to prove that \(N\) is Carmichael.

Additional congruence constraints are imposed so that:

\[
p_i-1\mid N-1
\]

holds for every factor.

That distinction is important.

The construction is not merely:

```text
choose some k_i
generate related primes
multiply them
```

It is a coordinated system of:

- primality conditions,
- Carmichael conditions,
- quadratic-character conditions,
- and simultaneous congruences.

---

## Controlling quadratic characters

Suppose we want a selected base:

\[
a\in A
\]

to behave in a particular way modulo every prime factor \(p_i\).

One useful sufficient condition is to control its Legendre symbol:

\[
\left(
\frac{a}{p_i}
\right).
\]

For example, we may require:

\[
\boxed{
\left(
\frac{a}{p_i}
\right)
=
-1
}
\]

for every prime factor \(p_i\).

That means \(a\) is a quadratic non-residue modulo every \(p_i\).

Quadratic reciprocity allows this condition to be translated into congruence conditions on \(p_i\).

For a fixed prime base \(a\), define a set of acceptable residue classes:

\[
S_a
\subseteq
\mathbb Z_{4a}
\]

such that primes in those residue classes have the desired quadratic-character behavior.

Conceptually:

\[
\boxed{
p\bmod4a
\in S_a
\Longrightarrow
\left(\frac ap\right)=-1.
}
\]

The exact computation of \(S_a\) follows from quadratic reciprocity.

---

## Translating conditions onto \(p_1\)

Since:

\[
p_i
=
k_i(p_1-1)+1,
\]

requiring:

\[
p_i\bmod4a
\in S_a
\]

gives:

\[
k_i(p_1-1)+1
\in S_a
\pmod{4a}.
\]

Rearrange:

\[
k_i p_1
\in
S_a+k_i-1
\pmod{4a}.
\]

When \(k_i\) is invertible modulo \(4a\), this becomes:

\[
\boxed{
p_1
\bmod4a
\in
k_i^{-1}
\left(
S_a+k_i-1
\right).
}
\]

We need this to hold for every \(i\).

Therefore:

\[
\boxed{
p_1\bmod4a
\in
\bigcap_{i=1}^{h}
k_i^{-1}
\left(
S_a+k_i-1
\right).
}
\]

This intersection is the important object.

If it is empty, the chosen \(k_i\) values are incompatible with that base.

If it is nonempty, we may select one admissible residue:

\[
z_a.
\]

Repeat this process for every:

\[
a\in A.
\]

---

## Why the \(k_i\) are chosen carefully

We want:

\[
k_i^{-1}\pmod{4a}
\]

to exist.

Therefore:

\[
\gcd(k_i,4a)=1.
\]

A convenient strategy for a set of prime bases is to choose \(k_i\) as small odd primes distinct from all selected bases.

This is a construction convenience, not a cryptographic requirement.

The mathematical requirement is invertibility with respect to the moduli appearing in the constraint system.

---

## From local residue conditions to CRT

For every selected base \(a_j\), suppose we have chosen:

\[
p_1
\equiv
z_{a_j}
\pmod{4a_j}.
\]

We now have many simultaneous congruence conditions:

\[
\begin{aligned}
p_1
&\equiv
z_{a_1}
\pmod{4a_1},\\
p_1
&\equiv
z_{a_2}
\pmod{4a_2},\\
&\vdots\\
p_1
&\equiv
z_{a_t}
\pmod{4a_t}.
\end{aligned}
\]

Additional conditions arise from enforcing the Carmichael property.

For the common three-factor setting:

\[
N=p_1p_2p_3,
\]

one obtains additional congruence restrictions involving:

\[
k_2
\]

and:

\[
k_3.
\]

A typical form is:

\[
p_1
\equiv
k_3^{-1}
\pmod{k_2},
\]

and:

\[
p_1
\equiv
k_2^{-1}
\pmod{k_3}.
\]

With pairwise compatible moduli, CRT combines everything into one arithmetic progression:

\[
\boxed{
p_1
\equiv
z
\pmod L.
}
\]

The modulus \(L\) is built from the relevant:

\[
4a_j
\]

and:

\[
k_i
\]

constraints.

Schematically:

\[
L
=
\operatorname{lcm}
(
4a_1,\ldots,4a_t,
k_2,\ldots,k_h
).
\]

So a complicated set of local restrictions becomes:

\[
\boxed{
p_1=z+jL.
}
\]

That is exactly the kind of local-to-global reconstruction for which CRT is designed.

---

## Constructing the prime factors

Once the CRT stage gives:

\[
p_1
\equiv
z
\pmod L,
\]

we search the arithmetic progression:

\[
p_1
=
z+jL.
\]

For each candidate \(p_1\), define:

\[
p_i
=
k_i(p_1-1)+1.
\]

We then require:

\[
p_1,p_2,\ldots,p_h
\]

all to be prime.

If that happens, define:

\[
\boxed{
N
=
\prod_{i=1}^{h}
p_i.
}
\]

The resulting \(N\) is certainly composite.

If the Carmichael and quadratic-character conditions were constructed correctly, it also has the desired pseudoprime behavior.

---

## The construction pipeline

At a high level:

```text
choose target Miller-Rabin bases A
              ↓
choose coefficients k_i
              ↓
derive quadratic-character residue sets
              ↓
intersect allowable classes for p_1
              ↓
add Carmichael congruence constraints
              ↓
CRT
              ↓
p_1 ≡ z mod L
              ↓
search p_1 = z + jL
              ↓
p_i = k_i(p_1 - 1) + 1
              ↓
require every p_i prime
              ↓
N = ∏ p_i
              ↓
verify Korselt
              ↓
verify strong pseudoprimality
for every target base
```

Notice how many earlier topics from this series have now reappeared:

\[
\text{primes}
\]

\[
\text{Legendre symbols}
\]

\[
\text{modular inverses}
\]

\[
\text{CRT}
\]

\[
\text{Carmichael numbers}
\]

\[
\text{Miller-Rabin}.
\]

This is exactly why the construction makes a good final article in the prime-number sequence.

---

## Why the resulting number is Carmichael

Suppose:

\[
N
=
p_1p_2\cdots p_h
\]

with all \(p_i\) distinct.

To establish Carmichael behavior, we do **not** merely test several Fermat bases.

We verify Korselt's criterion.

First:

\[
N
\]

must be square-free.

That is automatic if all the \(p_i\) are distinct primes.

Then verify:

\[
\boxed{
p_i-1
\mid
N-1
}
\]

for every \(i\).

A validation function can express the theorem directly:

```python
from math import prod


def verify_korselt(prime_factors):
    if len(set(prime_factors)) != len(prime_factors):
        return False

    N = prod(prime_factors)

    for p in prime_factors:
        if (N - 1) % (p - 1) != 0:
            return False

    return True
```

For a research implementation, this is preferable to merely observing that a number passes many Fermat tests.

We verify the structural theorem.

---

## Why selected Miller-Rabin bases can become liars

Being Carmichael gives:

\[
a^{N-1}
\equiv1
\pmod N
\]

for every unit \(a\).

But for strong pseudoprimality, we additionally need the repeated-squaring chain to have the correct shape.

The carefully chosen quadratic-character constraints synchronize how the selected bases behave modulo the different prime factors.

The goal is to make every:

\[
a\in A
\]

satisfy the strong probable-prime condition modulo \(N\).

Thus:

\[
\boxed{
N
\text{ is composite}
}
\]

while simultaneously:

\[
\boxed{
\operatorname{MR}(N,a)
=
\text{pass}
\qquad
\forall a\in A.
}
\]

This is an **adversarially engineered liar set**.

It does not make \(N\) a strong pseudoprime to every possible base.

Many other bases will still expose its compositeness.

---

## Verification comes last

A construction should never be accepted merely because its derivation suggests that it works.

We verify independently.

```python
def passes_fixed_bases(n, bases):
    return all(
        is_sprp_base(n, a)
        for a in bases
    )
```

Then:

```python
assert verify_korselt(
    prime_factors
)

assert passes_fixed_bases(
    N,
    target_bases,
)
```

And finally verify:

```python
assert N == math.prod(
    prime_factors
)
```

together with independent primality tests on every claimed factor.

The experimental principle is:

\[
\boxed{
\text{construct}
\rightarrow
\text{verify independently}.
}
\]

---

## Research implementation architecture

The companion implementation in this repository explores the construction algorithmically.

A clean implementation can be divided into separate stages.

### 1. Strong probable-prime verifier

```text
is_sprp_base(n, a)
```

implements one Miller-Rabin base.

### 2. Quadratic-character constraints

```text
build_nonresidue_classes(a)
```

constructs the residue classes associated with the required Legendre-symbol behavior.

### 3. Coefficient selection

```text
choose_k_values(...)
```

chooses candidate \(k_i\) values satisfying the required coprimality conditions.

### 4. Intersection

For every base \(a\):

\[
\bigcap_i
k_i^{-1}
(S_a+k_i-1)
\]

is computed.

Empty intersections reject the current \(k_i\) choice.

### 5. CRT reconstruction

Selected residue classes are combined with the additional Carmichael constraints.

The output is:

\[
p_1
\equiv
z
\pmod L.
\]

### 6. Prime search

Search:

\[
p_1=z+jL.
\]

For each candidate, construct:

\[
p_i=k_i(p_1-1)+1.
\]

Accept only if all \(p_i\) are prime.

### 7. Independent validation

Verify:

- primality of all factors,
- Korselt's criterion,
- the exact factorization of \(N\),
- every selected Miller-Rabin base.

The implementation should treat each one as a separate invariant.

---

## A safer experimental target

For understanding the phenomenon, we do not need to generate thousand-bit adversarial inputs.

Small known examples expose the same logical issue.

For example:

\[
3215031751
=
151\cdot751\cdot28351
\]

passes bases:

\[
2,3,5,7.
\]

A simple experiment is:

```python
N = 3215031751

bases = [2, 3, 5, 7]

assert all(
    is_sprp_base(N, a)
    for a in bases
)

assert not is_sprp_base(
    N,
    11,
)
```

This controlled experiment demonstrates the core weakness of an unjustified fixed-base strategy without requiring the full Arnault search.

The construction code can then be studied as the advanced version of the same idea.

---

## Bleichenbacher and adversarial primality testing

The difference between a mathematical curiosity and a security problem appears when an attacker can influence the candidate being tested.

Suppose a protocol accepts a supposedly prime modulus supplied by an untrusted peer.

If validation uses a predictable and insufficient fixed-base test, the attacker may search specifically for a composite that survives those checks.

The threat model is therefore:

```text
attacker knows validation algorithm
              +
attacker chooses candidate input
              ↓
candidate can be engineered
for that exact validation rule
```

Bleichenbacher demonstrated this principle against an actual cryptographic implementation.

The result is important because it changes the way we interpret primality-testing guarantees.

---

## What this does not break

The existence of fixed-base pseudoprimes does **not** imply:

```text
Miller-Rabin is unreliable.
```

It implies something much more precise.

### Randomized Miller-Rabin remains different

For any fixed odd composite \(N\), most bases are witnesses.

An adversarially constructed \(N\) may contain:

\[
2,3,5,7,11
\]

inside its strong-liar set.

But it cannot make every possible base a liar.

Selecting bases unpredictably after \(N\) has been chosen changes the adversarial problem.

### The \(1/4\) bound still applies

The strong-liar bound is a theorem about the fraction of possible bases for a fixed composite.

Constructing a number that fools a chosen finite base set does not contradict it.

The attacker has deliberately selected a few points from inside the liar set.

That is very different from a fresh random draw from the entire admissible base space.

---

## Fixed bases are not automatically wrong

This is another important distinction.

A statement such as:

> Fixed Miller-Rabin bases are insecure.

is too broad.

For bounded integer ranges, there are proven fixed base sets that classify every input correctly.

For example, for unsigned \(64\)-bit integers, a widely used sufficient set is:

```python
MR_BASES_64 = (
    2,
    325,
    9375,
    28178,
    450775,
    9780504,
    1795265022,
)
```

The important condition is:

\[
\boxed{
n<2^{64}.
}
\]

Here the fixed bases are not being used probabilistically.

They form a deterministic classifier over a proven finite domain.

Therefore:

```text
fixed bases
```

can describe two very different situations.

---

## Bounded deterministic Miller-Rabin

### Situation A — Proven bounded base set

We know mathematically or by exhaustive verification that a chosen base set correctly classifies every:

\[
n<B.
\]

Then the procedure is deterministic over that range.

### Situation B — Arbitrary fixed bases

An implementation chooses:

```text
2, 3, 5, 7, ...
```

and applies them to integers of unrestricted or much larger size without a theorem covering that domain.

Then specially constructed strong pseudoprimes may defeat it.

So the real rule is:

\[
\boxed{
\text{fixed bases require a proven input bound}.
}
\]

Without that bound, "we tested many small bases" is not a proof of primality.

---

## Why adding more fixed bases is not a complete argument

Suppose we test:

\[
2,3,5,7,11.
\]

A counterexample may exist.

So we add:

\[
13,17,19,23,29.
\]

This moves the first counterexample farther away.

But unless we establish a theorem of the form:

\[
n<B
\Longrightarrow
\text{these bases suffice},
\]

we have not obtained a deterministic primality proof.

We have merely changed the finite liar target.

This is exactly what adversarial pseudoprime constructions exploit.

---

## Random versus adversarial candidate generation

There is another subtle distinction.

In ordinary RSA key generation, candidates are generated internally from cryptographically secure randomness.

The environment looks roughly like:

```text
internal random candidate
        ↓
primality testing
```

An attacker generally does not get to solve:

> Which candidate should I send so that the exact bases used by the implementation all lie in its liar set?

But in a protocol that receives parameters from an untrusted party:

```text
attacker-selected candidate
        ↓
victim primality validation
```

the situation is completely different.

This is why primality testing should always be discussed together with its **input model**.

---

## Related approach: Bleichenbacher's construction

Bleichenbacher considered a related fixed-base pseudoprime construction built around Carmichael numbers.

Start with an integer:

\[
M
\]

having many divisors.

Consider primes \(r\) satisfying:

\[
r-1\mid M.
\]

Let \(R\) denote a collection of such primes.

If we find a subset:

\[
T\subseteq R
\]

whose product:

\[
C
=
\prod_{r\in T}r
\]

satisfies:

\[
\boxed{
C\equiv1\pmod M,
}
\]

then for every:

\[
r\in T,
\]

we have:

\[
r-1\mid M
\]

and:

\[
M\mid C-1.
\]

Therefore:

\[
r-1\mid C-1.
\]

If the factors are distinct, Korselt's criterion gives a Carmichael number.

The remaining construction problem is then to choose the factors so that the desired fixed Miller-Rabin bases also satisfy the appropriate strong-pseudoprime conditions.

This is another example of the same broad strategy:

\[
\boxed{
\text{engineer algebraic structure first}
\rightarrow
\text{make the test accept it}.
}
\]

---

## Meet-in-the-middle subset search

One computational subproblem is:

\[
\prod_{r\in T}r
\equiv1
\pmod M.
\]

A naive search over every subset of \(R\) requires:

\[
2^{|R|}
\]

possibilities.

A meet-in-the-middle strategy splits:

\[
R
=
R_1\cup R_2.
\]

Compute subset products from \(R_1\):

\[
P_1
=
\prod_{r\in T_1}r
\bmod M.
\]

For each one, store:

\[
P_1^{-1}\pmod M.
\]

Then enumerate subset products:

\[
P_2
=
\prod_{r\in T_2}r
\bmod M
\]

from \(R_2\).

If:

\[
P_2
=
P_1^{-1}
\pmod M,
\]

then:

\[
P_1P_2
\equiv1
\pmod M.
\]

The union:

\[
T=T_1\cup T_2
\]

therefore satisfies the required condition.

This reduces the search conceptually from:

\[
2^{|R|}
\]

toward roughly two collections of size:

\[
2^{|R|/2}.
\]

It is a standard time-memory tradeoff.

---

## Why this belongs after polynomial congruences

At first glance, `Solving Polynomial Congruences I` appearing between Prime II and Prime III looked strange.

But mathematically it actually helps.

This construction repeatedly uses simultaneous congruences of the form:

\[
p_1
\equiv
z_i
\pmod{m_i}.
\]

We then use CRT to collapse them into:

\[
p_1
\equiv
z
\pmod L.
\]

So Part VIII gave us exactly the tool needed here.

The progression is now:

\[
\text{Prime I}
\rightarrow
\text{prime structure},
\]

\[
\text{Prime II}
\rightarrow
\text{recognizing primes},
\]

\[
\text{Polynomial Congruences}
\rightarrow
\text{solving modular constraints},
\]

\[
\boxed{
\text{Prime III}
\rightarrow
\text{engineering composites around those constraints}.
}
\]

That is actually a strong mathematical narrative.

---

## The security lesson

The most important result of this article is not a particular pseudoprime.

It is the distinction between three forms of testing.

### Randomized probable-prime testing

Fresh independent bases are selected.

The Miller-Rabin error bound applies in its standard probabilistic form.

### Deterministic bounded testing

A fixed base set is backed by a theorem or exhaustive result covering:

\[
n<B.
\]

The routine is deterministic on that domain.

### Ad-hoc fixed-base testing

A predictable set is used outside any proven bound:

```text
2, 3, 5, 7, 11, ...
```

with the implicit belief that "enough bases" must imply primality.

This is the dangerous case under adversarial input.

The problem is not that the bases are numerically small.

The problem is that the acceptance predicate is predictable and lacks a theorem covering the input space.

---

## Production guidance

A cryptographic implementation should not invent its own primality-testing policy.

Prime generation and parameter validation should follow the relevant protocol and standard.

Depending on the application, that may involve:

- trial division by small primes,
- specified Miller-Rabin rounds,
- appropriately selected or random bases,
- Lucas-style tests,
- primality certificates,
- or standardized generation procedures.

The correct choice depends on whether:

- the candidate is generated internally,
- the candidate is attacker-controlled,
- deterministic proof is required,
- the integer size is bounded,
- or the protocol standard specifies a particular procedure.

The security question is therefore broader than:

> How many Miller-Rabin rounds do we run?

We must also ask:

\[
\boxed{
\text{Who chooses }n?
}
\]

and:

\[
\boxed{
\text{Who knows or controls the bases?}
}
\]

---

## Practice and checkpoint

### Exercise 1 — Strong pseudoprime

Write:

\[
N-1
=
2^sd
\]

for:

\[
N=3215031751.
\]

Then verify computationally that \(N\) passes Miller-Rabin for:

\[
2,3,5,7.
\]

Finally verify that base \(11\) rejects it.

---

### Exercise 2 — Factorization

Verify:

\[
3215031751
=
151\cdot751\cdot28351.
\]

Check whether the number satisfies Korselt's criterion.

Is it a Carmichael number?

Do not infer the answer merely from its Miller-Rabin behavior.

---

### Exercise 3 — Liar-set thinking

For a small odd composite \(n\), enumerate every admissible base:

\[
2\le a\le n-2
\]

with:

\[
\gcd(a,n)=1.
\]

Partition the bases into:

```text
strong witnesses
```

and:

```text
strong liars.
```

Calculate the liar fraction experimentally.

---

### Exercise 4 — Random versus fixed

Suppose an implementation always tests:

\[
A=\{2,3,5\}.
\]

Explain the difference between:

1. choosing a random composite and asking whether it survives \(A\);
2. searching deliberately for a composite known to survive \(A\).

Why are these different probability experiments?

---

### Exercise 5 — Korselt verification

Given distinct primes:

\[
p_1,p_2,p_3,
\]

set:

\[
N=p_1p_2p_3.
\]

Write code that verifies:

\[
p_i-1\mid N-1
\]

for all \(i\).

Do not test Carmichael behavior by sampling Fermat bases.

Use Korselt's theorem.

---

### Exercise 6 — CRT constraint system

Suppose:

\[
p_1
\equiv3\pmod8,
\]

\[
p_1
\equiv5\pmod7,
\]

and:

\[
p_1
\equiv2\pmod5.
\]

Use CRT to find:

\[
p_1
\equiv z
\pmod L.
\]

Then enumerate several members of the resulting arithmetic progression.

---

### Exercise 7 — Bounded fixed bases

Explain why a fixed base set may be perfectly valid for:

\[
n<2^{64}
\]

while the same argument cannot automatically be extended to arbitrary-precision integers.

What information is missing once the proven upper bound is removed?

---

### Exercise 8 — Threat model

Compare:

```text
RSA prime generated internally
```

with:

```text
DH modulus supplied by an untrusted peer.
```

Why is adversarial primality testing more relevant in the second setting?

---

## Reader checkpoint

You should now be able to explain:

1. What a strong pseudoprime to base \(a\) is.
2. Why strong pseudoprimality is base-dependent.
3. Why passing several fixed bases does not generally prove primality.
4. Why this does not contradict the Miller-Rabin \(1/4\) bound.
5. The difference between random-base and fixed-base testing.
6. Why Carmichael numbers automatically defeat Fermat testing but not Miller-Rabin for every base.
7. Why no composite can be a strong pseudoprime to every admissible Miller-Rabin base.
8. How Arnault-style constructions target a finite chosen base set.
9. Why relations such as
   \[
   p_i=k_i(p_1-1)+1
   \]
   are only one component of the construction.
10. Why additional Korselt congruences are necessary.
11. How Legendre symbols create modular restrictions on the prime factors.
12. Why quadratic reciprocity converts these restrictions into congruence classes.
13. Why CRT is central to combining the resulting conditions.
14. Why the construction ultimately searches an arithmetic progression
   \[
   p_1=z+jL.
   \]
15. Why every claimed factor must still be prime.
16. Why independent verification of Korselt's criterion is important.
17. Why known fixed base sets can nevertheless be deterministic on bounded domains.
18. Why adversarially supplied parameters change the security model of primality testing.

If these distinctions are clear, then Miller-Rabin should no longer be viewed merely as an algorithm with an "error probability."

Its security interpretation depends critically on **how candidates and bases are selected**.

---

## References and further reading

**François Arnault**,  
*Rabin-Miller Primality Test: Composite Numbers Which Pass It*,  
Mathematics of Computation, 64(209), 1995, pp. 355–361.

An early explicit study of composites engineered to pass predetermined Rabin-Miller bases.

**François Arnault**,  
*Constructing Carmichael Numbers Which Are Strong Pseudoprimes to Several Bases*,  
Journal of Symbolic Computation, 20(2), 1995, pp. 151–161.

A central reference for the construction of Carmichael numbers that are strong pseudoprimes to selected bases.

**Michael O. Rabin**,  
*Probabilistic Algorithm for Testing Primality*,  
Journal of Number Theory, 1980.

Provides the probabilistic foundation underlying the Miller-Rabin test.

**Louis Monier**,  
*Evaluation and Comparison of Two Efficient Probabilistic Primality Testing Algorithms*,  
Theoretical Computer Science, 1980.

Develops the strong-liar bounds underlying the reliability analysis of strong probable-prime testing.

**Daniel Bleichenbacher**,  
*Breaking a Cryptographic Protocol with Pseudoprimes*,  
Public Key Cryptography — PKC 2005, pp. 9–15.

Demonstrates how an incorrectly designed fixed-base primality test can become a practical protocol weakness.

**Martin R. Albrecht, Jake Massimo, Kenneth G. Paterson, and Juraj Somorovsky**,  
*Prime and Prejudice: Primality Testing Under Adversarial Conditions*,  
ACM CCS 2018, pp. 281–298.

A systematic study of primality tests when inputs may be deliberately chosen to exploit the validation procedure.

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

A comprehensive reference for pseudoprimes, primality testing, Carmichael numbers, and computational number theory.

---

## Closing the prime-number sequence

The three prime-number articles now form a complete progression.

### Prime Numbers I

We asked:

\[
\boxed{
\text{What are primes structurally?}
}
\]

We developed:

- unique factorization,
- Euclid's lemma,
- prime distribution,
- factorization,
- and cryptographic prime generation.

### Prime Numbers II

We asked:

\[
\boxed{
\text{How can we recognize primes computationally?}
}
\]

We developed:

- trial division,
- Fermat testing,
- pseudoprimes,
- Solovay-Strassen,
- Miller-Rabin,
- witnesses and liars.

### Prime Numbers III

We asked:

\[
\boxed{
\text{What happens when the candidate is deliberately chosen to fool the test?}
}
\]

We encountered:

- strong pseudoprimes,
- fixed-base weaknesses,
- Carmichael structure,
- quadratic reciprocity,
- CRT constraints,
- Arnault-style constructions,
- and adversarial primality testing.

The progression is therefore:

\[
\boxed{
\text{prime structure}
\rightarrow
\text{prime recognition}
\rightarrow
\text{adversarial pseudoprimality}.
}
\]

That closes the prime-number subseries while leaving us with a broader lesson that will recur throughout cryptography:

> A mathematical algorithm cannot be evaluated independently of the model in which its inputs, randomness, and parameters are chosen.

## Closing the Elementary Number Theory Reference

This article closes the **Elementary Number Theory Reference** series.

Across these nine references, we moved from the elementary arithmetic of the integers to increasingly structured computational number theory:

\[
\text{integers and divisibility}
\rightarrow
\text{modular arithmetic}
\rightarrow
\text{CRT}
\rightarrow
\text{groups}
\rightarrow
\text{Euler's totient and orders}
\]

\[
\rightarrow
\text{prime structure}
\rightarrow
\text{primality testing}
\rightarrow
\text{polynomial congruences}
\rightarrow
\text{adversarial pseudoprimality}.
\]

The progression was deliberately cumulative.

Divisibility gave us the GCD.

The GCD and Bézout identity gave us modular inverses.

Modular inverses led naturally to arithmetic in residue classes.

CRT showed how local modular information can be reconstructed globally.

Finite groups gave us the language of units, orders, generators, and exponentiation.

Prime numbers then connected this algebraic structure to factorization, primality testing, pseudoprimes, and cryptographic hardness assumptions.

Finally, polynomial congruences and adversarial primality testing brought many of these tools back together:

\[
\gcd,
\quad
\mathbb Z_n^\times,
\quad
\operatorname{ord}_n(a),
\quad
\varphi(n),
\quad
\lambda(n),
\quad
\text{CRT},
\quad
\text{quadratic characters},
\quad
\text{prime structure}.
\]

The purpose of this series was not to exhaust number theory.

It was to build a sufficiently rigorous computational foundation that later cryptographic material can use these objects without treating them as black boxes.

From here, CryptoCave moves into more specialized mathematical and cryptographic topics, where these foundations will repeatedly reappear in different forms.
