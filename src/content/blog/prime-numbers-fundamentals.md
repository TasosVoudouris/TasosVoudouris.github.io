---
title: "Prime Numbers I: Factorization and Structure"
description: "A detailed reference on prime numbers, Euclid's lemma, unique factorization, p-adic valuations, prime distribution, computational factorization, and the role of primes in cryptography."
pubDate: "2025-04-28"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Cryptographic Engineering"
tags:
  - "primes"
  - "factorization"
  - "fundamental-theorem-of-arithmetic"
  - "prime-number-theorem"
  - "python"
difficulty: "Intermediate"
series: "Elementary Number Theory Reference"
seriesOrder: 6
sourcePath: "experiments/ready-material/primes"
draft: false
---

Prime numbers sit at an unusual intersection of simple definitions and deep structure.

A prime is easy to define.

An integer

\[
p>1
\]

is prime when its only positive divisors are

\[
1
\qquad\text{and}\qquad
p.
\]

Yet primes control the multiplicative structure of all integers.

For example,

\[
100=2^2\cdot5^2,
\]

\[
986=2\cdot17\cdot29,
\]

and

\[
10001=73\cdot137.
\]

These are not merely possible decompositions.

They are essentially the **only** prime decompositions of those integers.

That fact is the Fundamental Theorem of Arithmetic.

It tells us that primes are the multiplicative building blocks of the integers.

But it immediately creates a computational tension that matters enormously in cryptography:

\[
\boxed{
\text{a factorization exists uniquely}
\not\Rightarrow
\text{the factorization is easy to find}.
}
\]

This distinction lies behind RSA and the classical integer-factorization problem.

At the same time, primes exhibit a remarkable global distribution: although the next prime may be difficult to predict locally, the Prime Number Theorem describes their asymptotic density with surprising precision.

So in this first prime-number reference we will connect three viewpoints:

\[
\boxed{
\text{algebraic structure}
+
\text{distribution}
+
\text{computation}.
}
\]

---

## Table of Contents

- [Prime and composite integers](#prime-and-composite-integers)
- [Prime versus irreducible](#prime-versus-irreducible)
- [Euclid’s lemma](#euclids-lemma)
- [The Fundamental Theorem of Arithmetic](#the-fundamental-theorem-of-arithmetic)
- [Why a prime factorization exists](#why-a-prime-factorization-exists)
- [Why the factorization is unique](#why-the-factorization-is-unique)
- [Consequences of unique factorization](#consequences-of-unique-factorization)
- [The (p)-adic valuation](#the-p-adic-valuation)
- [There are infinitely many primes](#there-are-infinitely-many-primes)
- [Prime gaps](#prime-gaps)
- [The Prime Number Theorem](#the-prime-number-theorem)
- [\[
\frac${B}${\ln B}](#fracbln-b)
- [A note on the Riemann Hypothesis](#a-note-on-the-riemann-hypothesis)
- [Prime density and cryptographic prime generation](#prime-density-and-cryptographic-prime-generation)
- [Generating candidates in Python](#generating-candidates-in-python)
- [Using PyCryptodome](#using-pycryptodome)
- [Using SageMath](#using-sagemath)
- [Factorization as a computational problem](#factorization-as-a-computational-problem)
- [Input size matters](#input-size-matters)
- [Primality testing is a different problem](#primality-testing-is-a-different-problem)
- [Classical and quantum factorization](#classical-and-quantum-factorization)
- [Historical factoring challenges](#historical-factoring-challenges)
- [Python and SageMath experiments](#python-and-sagemath-experiments)
- [Why this matters in cryptography](#why-this-matters-in-cryptography)
- [The central distinction](#the-central-distinction)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)

---

## Prime and composite integers

An integer

\[
p>1
\]

is **prime** if its only positive divisors are

\[
1
\]

and

\[
p.
\]

An integer

\[
n>1
\]

that is not prime is **composite**.

Equivalently, \(n\) is composite if it can be written as

\[
n=ab
\]

with

\[
1<a<n
\]

and

\[
1<b<n.
\]

The integer

\[
1
\]

is neither prime nor composite.

The first few primes are

\[
2,3,5,7,11,13,17,19,23,29,31,37,\ldots
\]

while the first few composite numbers are

\[
4,6,8,9,10,12,14,15,16,18,20,21,\ldots
\]

The prime \(2\) is special because it is the only even prime.

Every integer

\[
n>2
\]

that is even is divisible by \(2\), and therefore composite.

---

## Prime versus irreducible

Inside the ordinary integers, we often move freely between two descriptions of a prime.

One description is based on factorization.

A positive integer \(p>1\) is irreducible when

\[
p=ab
\]

forces one factor to be a unit.

Inside \(\mathbb Z\), the units are

\[
\pm1.
\]

Another description is based on divisibility.

A nonzero nonunit \(p\) is a **prime element** when:

\[
p\mid ab
\quad\Longrightarrow\quad
p\mid a
\text{ or }
p\mid b.
\]

In the integers,

\[
\boxed{
\text{prime}
\iff
\text{irreducible}.
}
\]

This equivalence is one of the structural reasons unique factorization works so cleanly in \(\mathbb Z\).

But it is not true in every integral domain.

### Why the distinction matters

Consider the ring

\[
\mathbb Z[\sqrt{-5}]
=
\{
a+b\sqrt{-5}:
a,b\in\mathbb Z
\}.
\]

Inside this ring,

\[
6
=
2\cdot3
\]

but also:

\[
6
=
(1+\sqrt{-5})
(1-\sqrt{-5}).
\]

These are genuinely different factorizations into irreducible elements.

The norm

\[
N(a+b\sqrt{-5})
=
a^2+5b^2
\]

helps show that the relevant factors cannot be decomposed further into nonunits.

So unique factorization can fail outside \(\mathbb Z\).

This distinction eventually leads into deeper algebraic number theory, ideals, and class groups.

For the present reference, however, we work primarily inside:

\[
\mathbb Z,
\]

where prime factorization is unique.

---

## Euclid's lemma

One of the key properties distinguishing primes is the following.

### Euclid's Lemma

If \(p\) is prime and

\[
p\mid ab,
\]

then:

\[
\boxed{
p\mid a
\quad\text{or}\quad
p\mid b.
}
\]

This is stronger than simply saying that \(p\) has no nontrivial factors.

It tells us how primes interact with products.

### Proof using Bézout's identity

Suppose:

\[
p\mid ab.
\]

If:

\[
p\mid a,
\]

we are done.

Otherwise:

\[
p\nmid a.
\]

Since \(p\) is prime, the only possible positive common divisors of \(p\) and \(a\) are \(1\) and \(p\).

But \(p\nmid a\), so:

\[
\gcd(p,a)=1.
\]

Bézout's identity therefore gives integers \(u,v\) satisfying:

\[
up+va=1.
\]

Multiply everything by \(b\):

\[
ubp+vab=b.
\]

Now:

\[
p\mid ubp,
\]

and because:

\[
p\mid ab,
\]

we also have:

\[
p\mid vab.
\]

Therefore \(p\) divides their sum:

\[
p\mid b.
\]

Thus:

\[
\boxed{
p\mid ab
\Longrightarrow
p\mid a
\text{ or }
p\mid b.
}
\]

### More than two factors

By induction:

\[
p\mid a_1a_2\cdots a_k
\]

implies:

\[
p\mid a_i
\]

for at least one index \(i\).

This apparently small lemma is the key to proving uniqueness of prime factorization.

---

## The Fundamental Theorem of Arithmetic

The Fundamental Theorem of Arithmetic states that every integer greater than \(1\) can be expressed as a product of primes, and that this decomposition is unique up to the ordering of the factors.

More precisely, every integer

\[
n>1
\]

can be written uniquely as:

\[
\boxed{
n
=
p_1^{\alpha_1}
p_2^{\alpha_2}
\cdots
p_r^{\alpha_r}
}
\]

where:

\[
p_1<p_2<\cdots<p_r
\]

are distinct primes and:

\[
\alpha_i\ge1.
\]

For a nonzero integer \(z\), we may include the sign as a unit:

\[
z
=
u
p_1^{\alpha_1}
\cdots
p_r^{\alpha_r},
\qquad
u\in\{-1,1\}.
\]

The theorem has two logically separate parts:

\[
\boxed{
\text{existence}
+
\text{uniqueness}.
}
\]

---

## Why a prime factorization exists

Let:

\[
n>1.
\]

If \(n\) is prime, then it is already a product of primes.

If it is composite, then:

\[
n=ab
\]

for integers satisfying:

\[
1<a<n,
\qquad
1<b<n.
\]

If \(a\) and \(b\) are prime, we are done.

If one is composite, factor it again.

Every factor produced is smaller than the composite integer from which it came.

Since positive integers cannot decrease forever, the process must eventually terminate.

At termination, every remaining factor is prime.

Therefore every integer:

\[
n>1
\]

has at least one prime factorization.

---

## Why the factorization is unique

Suppose \(n\) has two prime factorizations:

\[
n
=
p_1p_2\cdots p_r
=
q_1q_2\cdots q_s.
\]

Because:

\[
p_1
\mid
q_1q_2\cdots q_s,
\]

Euclid's lemma tells us that:

\[
p_1\mid q_j
\]

for some \(j\).

But both \(p_1\) and \(q_j\) are prime.

Therefore:

\[
p_1=q_j.
\]

After reordering the second factorization, cancel the common prime.

We obtain a smaller equality of prime products.

Repeating the argument eventually matches every prime factor on both sides.

Thus the two factorizations differ only in ordering.

Therefore:

\[
\boxed{
\text{prime factorization in }\mathbb Z
\text{ is unique}.
}
\]

This is one of the fundamental structural properties of the integers.

---

## Consequences of unique factorization

Prime factorization allows many arithmetic questions to become questions about exponents.

Suppose:

\[
a
=
\prod_p
p^{\alpha_p}
\]

and:

\[
b
=
\prod_p
p^{\beta_p},
\]

where all but finitely many exponents are zero.

### Divisibility

Then:

\[
\boxed{
a\mid b
\iff
\alpha_p\le\beta_p
\text{ for every prime }p.
}
\]

For example:

\[
12
=
2^2\cdot3
\]

divides:

\[
360
=
2^3\cdot3^2\cdot5
\]

because:

\[
2\le3
\]

for the exponent of \(2\), and:

\[
1\le2
\]

for the exponent of \(3\).

### Greatest common divisor

The GCD takes the minimum exponent of every prime:

\[
\boxed{
\gcd(a,b)
=
\prod_p
p^{\min(\alpha_p,\beta_p)}.
}
\]

### Least common multiple

The LCM takes the maximum:

\[
\boxed{
\operatorname{lcm}(a,b)
=
\prod_p
p^{\max(\alpha_p,\beta_p)}.
}
\]

That immediately explains:

\[
\gcd(a,b)
\operatorname{lcm}(a,b)
=
|ab|.
\]

### Perfect squares

An integer is a perfect square exactly when every prime exponent is even.

For example:

\[
3600
=
2^4\cdot3^2\cdot5^2
\]

is a square because every exponent is even.

Indeed:

\[
3600=60^2.
\]

### Square-free integers

A positive integer is **square-free** when no square of a prime divides it.

Equivalently:

\[
n
=
p_1p_2\cdots p_r
\]

with every prime appearing with exponent exactly \(1\).

For example:

\[
30
=
2\cdot3\cdot5
\]

is square-free.

But:

\[
12
=
2^2\cdot3
\]

is not.

Square-free structure will reappear in Korselt's criterion for Carmichael numbers.

---

## The \(p\)-adic valuation

Unique factorization lets us isolate the exponent of one particular prime.

Let \(p\) be prime and let:

\[
n\neq0.
\]

The **\(p\)-adic valuation** of \(n\), written:

\[
v_p(n),
\]

is the exponent of \(p\) in the prime factorization of \(n\).

Equivalently:

\[
\boxed{
v_p(n)
=
\max
\{
k\ge0:
p^k\mid n
\}.
}
\]

For example:

\[
360
=
2^3\cdot3^2\cdot5,
\]

so:

\[
v_2(360)=3,
\]

\[
v_3(360)=2,
\]

\[
v_5(360)=1,
\]

and:

\[
v_7(360)=0.
\]

The valuation converts multiplication into addition:

\[
\boxed{
v_p(ab)
=
v_p(a)+v_p(b).
}
\]

Likewise:

\[
v_p(a^m)
=
m\,v_p(a).
\]

And:

\[
v_p(\gcd(a,b))
=
\min
\{
v_p(a),v_p(b)
\}.
\]

These identities are simply unique factorization written locally at one prime.

Later, valuations become useful in:

- divisibility arguments,
- prime-power arithmetic,
- factorials,
- lifting exponent arguments,
- algebraic number theory.

---

## There are infinitely many primes

Prime factorization would be much less interesting if only finitely many primes existed.

Euclid proved that this cannot happen.

### Euclid's proof

Assume there are only finitely many primes:

\[
p_1,p_2,\ldots,p_k.
\]

Construct:

\[
N
=
p_1p_2\cdots p_k+1.
\]

Clearly:

\[
N>1.
\]

Therefore \(N\) has some prime divisor \(q\).

But for every \(p_i\),

\[
N
\equiv1
\pmod{p_i}.
\]

So none of the primes:

\[
p_1,\ldots,p_k
\]

divides \(N\).

Therefore \(q\) is a prime that was not on our supposedly complete list.

Contradiction.

Hence:

\[
\boxed{
\text{there are infinitely many primes}.
}
\]

A subtle point is worth remembering.

The number:

\[
p_1p_2\cdots p_k+1
\]

does **not** itself need to be prime.

It merely has a prime divisor that was absent from the original list.

That is enough.

---

## Prime gaps

Although there are infinitely many primes, primes do not appear at fixed intervals.

In fact, there are arbitrarily long runs of consecutive composite integers.

Given any positive integer \(k\), consider:

\[
(k+1)!+2,
\]

\[
(k+1)!+3,
\]

\[
\ldots,
\]

\[
(k+1)!+(k+1).
\]

For every:

\[
j\in\{2,\ldots,k+1\},
\]

the number:

\[
(k+1)!+j
\]

is divisible by \(j\).

Therefore all \(k\) numbers are composite.

So:

\[
\boxed{
\text{prime gaps can be arbitrarily large}.
}
\]

This does not contradict the fact that primes have a regular global density.

Local irregularity and global statistical structure coexist.

---

## The Prime Number Theorem

Let:

\[
\pi(x)
\]

denote the number of primes satisfying:

\[
p\le x.
\]

The **Prime Number Theorem** states:

\[
\boxed{
\pi(x)
\sim
\frac{x}{\ln x}.
}
\]

Equivalently:

\[
\lim_{x\rightarrow\infty}
\frac{\pi(x)}
{x/\ln x}
=
1.
\]

So near a large number \(x\), the rough density of primes is:

\[
\frac1{\ln x}.
\]

This does not predict exactly where the next prime is located.

Instead, it gives an asymptotic description of how frequently primes occur.

For example, a rough estimate for the number of primes in:

\[
[A,B]
\]

is:

\[
\frac{B}{\ln B}
-
\frac{A}{\ln A}.
\]

For better numerical estimates one can use the logarithmic integral:

\[
\operatorname{Li}(x).
\]

The important conceptual lesson is:

\[
\boxed{
\text{primes look irregular locally}
\quad\text{but}\quad
\text{their global density is highly structured}.
}
\]

---

## A note on the Riemann Hypothesis

The Riemann Hypothesis is deeply connected to the distribution of primes, but it should not be described as a formula that predicts the next prime.

Very roughly, the zeros of the Riemann zeta function govern fluctuations in prime-counting formulas.

The Prime Number Theorem gives the leading approximation:

\[
\pi(x)
\sim
\frac{x}{\ln x}.
\]

The Riemann Hypothesis would imply much stronger control over the error between prime-counting functions and their approximations.

So the connection is:

\[
\boxed{
\text{zeta zeros}
\longleftrightarrow
\text{fine structure in prime distribution}.
}
\]

We do not need that analytic machinery for cryptographic prime generation, but it shows how deep the study of primes eventually becomes.

---

## Prime density and cryptographic prime generation

The Prime Number Theorem also explains something practical.

Suppose we search for a \(k\)-bit prime.

A \(k\)-bit integer has size roughly:

\[
2^k.
\]

Near that size, the probability that a random integer is prime is approximately:

\[
\frac{1}{\ln(2^k)}
=
\frac{1}{k\ln2}.
\]

But except for \(2\), every prime is odd.

If we generate **only odd candidates**, the approximate prime density doubles:

\[
\boxed{
\Pr[
\text{random odd }k\text{-bit candidate is prime}
]
\approx
\frac{2}{k\ln2}.
}
\]

So the expected number of odd candidates before encountering a prime is approximately:

\[
\boxed{
\frac{k\ln2}{2}.
}
\]

For example, around \(2048\) bits this is roughly:

\[
\frac{2048\ln2}{2}
\approx
710.
\]

This does **not** mean prime generation requires trial division against every possible factor.

Instead, cryptographic prime generation typically follows a pipeline like:

```text
cryptographic random bits
        ↓
force required bit length
        ↓
force oddness
        ↓
cheap small-prime filtering
        ↓
strong primality testing
        ↓
candidate accepted as prime
```

The next prime-number reference will study that primality-testing step in detail.

---

## Generating candidates in Python

A candidate should come from a cryptographically suitable random source.

For example:

```python
import secrets


def random_odd_candidate(bits):
    if bits < 2:
        raise ValueError(
            "bits must be at least 2"
        )

    candidate = secrets.randbits(bits)

    # Force the most significant bit:
    # candidate really has 'bits' bits.
    candidate |= 1 << (bits - 1)

    # Force oddness.
    candidate |= 1

    return candidate
```

Now:

```python
candidate = random_odd_candidate(128)

print(candidate)
print(candidate.bit_length())

assert candidate.bit_length() == 128
assert candidate % 2 == 1
```

This gives us a **prime candidate**.

It does not prove that the candidate is prime.

That distinction matters:

```text
random odd candidate
        ≠
prime
```

The candidate still needs primality testing.

---

## Using PyCryptodome

For experiments where we want the library to handle prime generation:

```python
from Crypto.Util.number import getPrime

p = getPrime(128)

print(p)
print(p.bit_length())

assert p.bit_length() == 128
```

Likewise:

```python
p = getPrime(768)

assert p.bit_length() == 768
```

For production cryptography, we should generally use the key-generation facilities of the relevant cryptographic library rather than manually assembling cryptographic keys from standalone primes.

The purpose here is to inspect the number-theoretic object itself.

---

## Using SageMath

SageMath can generate primes in a chosen range:

```python
p = random_prime(
    2**128 - 1,
    lbound=2**127,
)

print(p)
print(p.nbits())

assert p.nbits() == 128
```

It can also enumerate small primes:

```python
prime_range(10, 50)
```

which gives:

```text
[11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

These utilities hide the primality-testing machinery.

Later we will unpack what "is prime" means computationally.

---

## Factorization as a computational problem

The Fundamental Theorem of Arithmetic tells us that the prime factorization exists uniquely.

It does **not** give us an efficient algorithm for finding it.

Take:

\[
1275.
\]

By elementary divisibility:

\[
1275
=
3\cdot425
\]

and:

\[
425
=
5\cdot85.
\]

Then:

\[
85
=
5\cdot17.
\]

So:

\[
\boxed{
1275
=
3\cdot5^2\cdot17.
}
\]

A different sequence of divisions must eventually reach the same prime factors because factorization is unique.

For small integers, this is easy.

For carefully generated cryptographic semiprimes, the computational problem is entirely different.

---

## Input size matters

Suppose the integer to be factored is \(N\).

The natural input size is not \(N\) itself.

It is approximately the number of bits required to represent it:

\[
\boxed{
\ell
=
\lfloor\log_2N\rfloor+1.
}
\]

An algorithm performing:

\[
O(N)
\]

operations is therefore exponential in the input length.

Even trial division up to:

\[
\sqrt N
\]

requires approximately:

\[
2^{\ell/2}
\]

candidate-scale work for an \(\ell\)-bit number.

That is why trial division becomes useless for cryptographic RSA moduli.

More sophisticated classical algorithms exist, including:

- Pollard's \(\rho\),
- Pollard's \(p-1\),
- the quadratic sieve,
- the general number field sieve.

They exploit much deeper mathematical structure than trial division.

We will study these separately rather than compressing all of integer factorization into this foundational article.

---

## Primality testing is a different problem

A very important distinction is:

\[
\boxed{
\text{primality testing}
\neq
\text{integer factorization}.
}
\]

Suppose we are given:

\[
N.
\]

The primality-testing problem asks:

> Is \(N\) prime?

The factorization problem asks:

> If \(N\) is composite, what are its prime factors?

A primality test can prove or provide overwhelming evidence that a number is composite without giving us its factors.

For example:

```text
N is composite
```

is much less information than:

```text
N = pq
```

with explicit \(p\) and \(q\).

This distinction is especially important cryptographically.

Primality testing is known to admit deterministic polynomial-time algorithms.

The AKS result established:

\[
\boxed{
\mathrm{PRIMES}\in\mathbf P.
}
\]

No polynomial-time classical algorithm is currently known for general integer factorization.

So RSA does **not** rely on it being difficult to determine whether an integer is prime.

RSA relies on the difficulty of recovering the secret factors of a specially generated composite modulus.

---

## Classical and quantum factorization

For classical computation, efficient general factorization of large RSA-style integers remains a hard computational problem.

Quantum computation changes the theoretical situation.

Shor's algorithm gives a polynomial-time quantum algorithm for integer factorization.

This means that a sufficiently large, fault-tolerant quantum computer capable of executing Shor's algorithm at cryptographic scale would break the mathematical hardness assumption underlying RSA.

It is worth separating theory from experimental demonstrations.

In 2001, an NMR-based quantum experiment demonstrated a small instance of Shor's algorithm by factoring:

\[
15=3\cdot5.
\]

That experiment was historically important as a demonstration of quantum-control techniques.

It was not evidence that cryptographic-size RSA moduli could then be factored, and the experiment itself did not establish scalability to such sizes.

That distinction remains essential whenever small demonstrations of quantum factoring are discussed.

---

## Historical factoring challenges

RSA Laboratories historically published a sequence of large semiprimes as the **RSA Factoring Challenge**.

The purpose was to provide concrete benchmarks for progress in integer-factorization algorithms.

Researchers succeeded in factoring a number of those challenge integers, and the results helped demonstrate practical advances in algorithms and large-scale computation.

The challenge program itself was discontinued in 2007.

So the old challenge numbers remain valuable historical benchmarks, but they should not be interpreted as an active prize program.

The lesson that remains relevant is broader:

\[
\boxed{
\text{factorization security depends on}
\text{ parameter size}
+
\text{ algorithmic progress}
+
\text{ computational resources}.
}
\]

This is why cryptographic key sizes cannot be chosen simply by saying that a number "looks large."

---

## Python and SageMath experiments

For small educational integers, we can implement trial factorization directly.

```python
def trial_factor(n):
    if n < 2:
        return []

    factors = []

    d = 2

    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d

        d += 1

    if n > 1:
        factors.append(n)

    return factors
```

Examples:

```python
assert trial_factor(36) == [2, 2, 3, 3]

assert trial_factor(986) == [
    2,
    17,
    29,
]

assert trial_factor(1275) == [
    3,
    5,
    5,
    17,
]
```

This implementation exposes the mathematics clearly.

It is not a serious cryptographic factorization algorithm.

### SageMath factorization

SageMath makes small and moderate experiments convenient:

```python
factor(1275)
```

returns:

```text
3 * 5^2 * 17
```

Likewise:

```python
factor(2007)
```

returns:

```text
3^2 * 223
```

We can inspect the structured result:

```python
F = factor(1275)

for p, exponent in F:
    print(p, exponent)
```

This directly exposes the representation:

\[
n
=
\prod_i
p_i^{e_i}.
\]

### Prime versus composite

For small experiments:

```python
for n in range(10, 30):
    print(
        n,
        is_prime(n),
    )
```

In SageMath, `is_prime` handles the primality-testing machinery for us.

That is useful for computation.

But understanding how such testing works is the subject of the next stage.

---

## Why this matters in cryptography

Prime structure appears throughout cryptography, but in several different roles.

### RSA

RSA generates secret primes:

\[
p
\qquad\text{and}\qquad
q
\]

and publishes:

\[
N=pq.
\]

Multiplication is trivial.

Recovering:

\[
p,q
\]

from \(N\) is intended to be computationally hard.

So RSA depends directly on the gap between:

\[
\boxed{
\text{easy multiplication}
}
\]

and:

\[
\boxed{
\text{hard factor recovery}.
}
\]

### Modular groups

When \(p\) is prime:

\[
\mathbb Z_p
\]

is a field.

Therefore every nonzero element has an inverse.

Its multiplicative group has order:

\[
p-1.
\]

That simple fact supports:

- finite-field arithmetic,
- Diffie-Hellman groups,
- primitive roots,
- Fermat's little theorem,
- quadratic residues.

### Prime-order subgroups

Many cryptographic protocols deliberately work inside groups of prime order:

\[
q.
\]

Prime order gives particularly clean subgroup structure.

By Lagrange's theorem, a group of prime order has no nontrivial proper subgroups.

That property is extremely useful when reasoning about cryptographic group behavior.

### Prime generation

RSA and many other constructions require large primes that are:

- correctly sized,
- generated from sufficient entropy,
- tested appropriately,
- compatible with the surrounding protocol requirements.

So prime generation itself becomes part of the cryptographic security boundary.

---

## The central distinction

At this stage, four different tasks should no longer be conflated:

```text
PRIME STRUCTURE

What properties do primes have?
```

```text
PRIME DISTRIBUTION

How frequently do primes occur?
```

```text
PRIMALITY TESTING

Given n, is n prime?
```

```text
FACTORIZATION

Given composite n,
what are its prime factors?
```

They are deeply related mathematically.

But computationally, they are different problems.

That distinction is one of the most important lessons to carry forward.

---

## Practice and checkpoint

### Exercise 1 — Prime or composite

Classify:

\[
1,\quad2,\quad17,\quad21,\quad97,\quad121.
\]

For every composite value, give a nontrivial factorization.

### Exercise 2 — Euclid's lemma

Suppose:

\[
7\mid ab
\]

and:

\[
7\nmid a.
\]

Use Bézout's identity to explain why:

\[
7\mid b.
\]

Do not merely quote Euclid's lemma.

Reconstruct its proof.

### Exercise 3 — Unique factorization

Factor:

\[
7560
\]

into primes.

Then express:

\[
\gcd(7560,3600)
\]

and:

\[
\operatorname{lcm}(7560,3600)
\]

directly from the prime exponents.

### Exercise 4 — Perfect squares

Without computing a square root directly, determine whether:

\[
2^8 3^4 5^2 7^6
\]

is a perfect square.

Now change the exponent of \(7\) from \(6\) to \(5\).

What changes?

### Exercise 5 — Valuations

Compute:

\[
v_2(3600),
\]

\[
v_3(3600),
\]

and:

\[
v_5(3600).
\]

Then verify:

\[
v_2(3600^3)
=
3v_2(3600).
\]

### Exercise 6 — Arbitrarily long composite runs

Construct five consecutive composite integers using the factorial argument.

Verify the divisibility of each one.

### Exercise 7 — Prime density

Using the Prime Number Theorem, estimate:

\[
\pi(10^6).
\]

Then compare the approximation with the actual value using SageMath.

### Exercise 8 — Cryptographic candidate density

For \(k=1024\), estimate:

\[
\frac{2}{k\ln2}.
\]

Interpret the result as the approximate probability that a random odd \(1024\)-bit integer is prime.

Then estimate the expected number of candidates before finding a prime.

### Exercise 9 — Factorization versus primality

Explain why the statement:

```text
N is composite
```

does not solve the problem:

```text
find p and q such that N = pq
```

even though the two problems clearly interact.

### Reader checkpoint

You should now be able to explain:

1. The difference between prime and composite integers.
2. Why prime and irreducible elements coincide in \(\mathbb Z\).
3. Why that equivalence need not hold in arbitrary rings.
4. Euclid's lemma and its connection to Bézout's identity.
5. The existence and uniqueness parts of the Fundamental Theorem of Arithmetic.
6. Why prime exponent vectors determine divisibility.
7. Why GCD uses minimum exponents and LCM uses maximum exponents.
8. What \(v_p(n)\) measures.
9. Euclid's proof that infinitely many primes exist.
10. Why arbitrarily long prime gaps can occur.
11. What
    \[
    \pi(x)\sim\frac{x}{\ln x}
    \]
    means.
12. Why the Prime Number Theorem makes random prime search practical.
13. Why a random odd candidate is not automatically prime.
14. Why primality testing and integer factorization are distinct computational problems.
15. Why RSA depends on factor recovery rather than on primality testing being hard.
16. Why Shor's algorithm fundamentally changes the theoretical factoring landscape for scalable quantum computers.

If these ideas are clear, we have separated the **structure of primes** from the algorithms needed to recognize them.

That is exactly where the next topic begins.

---

## References and further reading

**G. H. Hardy and E. M. Wright**,  
*An Introduction to the Theory of Numbers.*

A classical reference for primes, unique factorization, prime distribution, and elementary number theory.

**Tom M. Apostol**,  
*Introduction to Analytic Number Theory.*

A strong bridge from elementary prime structure to the Prime Number Theorem and analytic number theory.

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

Especially valuable for primality testing, factorization, prime generation, and computational number theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

A useful computational treatment of primes, modular arithmetic, algorithms, and algebraic structure.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Connects prime generation and integer factorization directly to public-key cryptography.

**Peter W. Shor**,  
*Algorithms for Quantum Computation: Discrete Logarithms and Factoring*,  
1994.

The foundational quantum algorithm showing that integer factorization and discrete logarithms admit polynomial-time quantum algorithms.

**Lieven M. K. Vandersypen et al.**,  
*Experimental Realization of Shor's Quantum Factoring Algorithm Using Nuclear Magnetic Resonance*,  
Nature, 2001.

A historically important experimental demonstration using the small instance:

\[
15=3\cdot5.
\]

---

## Next

We now know what a prime **is**, why prime factorization exists uniquely, and why finding factors is not the same problem as recognizing primality.

The next computational question is therefore:

> Given a large candidate \(n\), how do we actually decide whether it is prime?

Trial division works for tiny examples.

For cryptographic-size candidates, it does not.

That takes us into:

\[
\text{Fermat tests}
\rightarrow
\text{pseudoprimes}
\rightarrow
\text{Carmichael numbers}
\rightarrow
\text{Miller-Rabin}
\rightarrow
\text{practical prime generation}.
\]

**Next: Prime Numbers II — Primality Testing and Probable Primes.**
