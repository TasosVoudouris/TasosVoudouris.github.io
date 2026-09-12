---
title: "Prime Numbers for Cryptographers: From Trial Division to Miller-Rabin"
description: "Why cryptography needs large primes, why trial division stops scaling, how Fermat pseudoprimes fool naive tests, and how Miller-Rabin turns modular structure into a practical probable-prime test."
pubDate: "2026-09-08"
category: "Number Theory"
tags:
  - primes
  - primality-testing
  - fermat
  - miller-rabin
  - rsa
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

We have been using prime numbers almost from the beginning of this series.

Modulo a prime, every non-zero residue has an inverse.

Diffie-Hellman likes prime-order groups.

RSA starts by generating two large primes.

And later, finite fields will depend on primes again.

So at some point the obvious question becomes unavoidable:

> If the prime is hundreds or thousands of bits long, how do we know it is actually prime?

For a small number, I can try divisors.

For a cryptographic number, that idea falls apart very quickly.

This is where primality testing becomes its own computational problem.

And one thing I find especially interesting is that the practical solution does not begin by trying harder to factor the number.

It asks a different question:

> Does this number behave the way a prime is forced to behave?

That takes us from Fermat's little theorem to pseudoprimes and finally to Miller-Rabin.

![Fermat versus Miller-Rabin on the Carmichael number 561](/images/blog/11-miller-rabin-561.svg)

*The composite number $561$ passes the simple Fermat test to base $2$, but its Miller-Rabin squaring chain exposes behavior that cannot occur modulo a prime.*

---

## Why trial division stops being a serious plan

An integer $n>1$ is prime if its only positive divisors are:

$$
1
\quad\text{and}\quad
n.
$$

A direct test is therefore:

```python
def is_prime_naive(n):
    if n < 2:
        return False

    d = 2

    while d * d <= n:
        if n % d == 0:
            return False

        d += 1

    return True
```

Why stop at:

$$
d\le\sqrt n?
$$

Because if:

$$
n=ab
$$

and both factors were larger than $\sqrt n$, then:

$$
ab>n,
$$

which is impossible.

For small examples, this is perfectly fine.

But now think in terms of **bit length**.

A $k$-bit integer is roughly the size of:

$$
2^k.
$$

Its square root is roughly:

$$
2^{k/2}.
$$

So trial division up to $\sqrt n$ is exponential in the bit length.

For cryptographic-size inputs, we need a completely different idea.

---

## Fermat gives a test — but not a proof

If $p$ is prime and:

$$
\gcd(a,p)=1,
$$

then Fermat's little theorem tells us:

$$
a^{p-1}\equiv1\pmod p.
$$

That suggests an algorithm.

Given an odd candidate $n$, choose a base $a$ and test:

$$
a^{n-1}\stackrel{?}\equiv1\pmod n.
$$

If the answer is **not** $1$, then:

$$
\boxed{n\text{ is definitely composite}.}
$$

That part is excellent.

The problem is the other direction.

If:

$$
a^{n-1}\equiv1\pmod n,
$$

we cannot conclude that $n$ is prime.

Some composite numbers imitate prime behavior.

They are **pseudoprimes**.

And one of the best examples is:

$$
561=3\cdot11\cdot17.
$$

It is obviously composite.

Yet:

$$
2^{560}\equiv1\pmod{561}.
$$

So a base-$2$ Fermat test says:

```text
looks prime
```

even though:

```text
561 = 3 * 11 * 17
```

is sitting right in front of us.

It gets worse.

$561$ is the smallest **Carmichael number**.

For every base $a$ coprime to $561$:

$$
a^{560}\equiv1\pmod{561}.
$$

So simply repeating Fermat's test with many coprime bases does not fix the fundamental problem.

This is the first lesson:

> Passing a necessary condition for primality is not the same thing as proving primality.

---

## Miller-Rabin looks inside the exponentiation

This is where Miller-Rabin becomes much more interesting than "Fermat, repeated."

Take an odd candidate $n$ and factor the powers of $2$ out of:

$$
n-1.
$$

Write:

$$
n-1=2^s d,
$$

where $d$ is odd.

For:

$$
n=561,
$$

we have:

$$
560=2^4\cdot35.
$$

So:

$$
s=4,
\qquad
d=35.
$$

Now choose base:

$$
a=2.
$$

Instead of computing only:

$$
2^{560}\bmod561,
$$

Miller-Rabin starts earlier:

$$
x_0=2^{35}\bmod561.
$$

This gives:

$$
x_0=263.
$$

Now square repeatedly:

$$
x_1=263^2\bmod561=166,
$$

$$
x_2=166^2\bmod561=67,
$$

$$
x_3=67^2\bmod561=1.
$$

So the chain is:

```text
263 → 166 → 67 → 1
```

Notice what never appeared:

$$
-1\equiv560\pmod{561}.
$$

That is the witness.

Miller-Rabin declares:

$$
\boxed{561\text{ composite}.}
$$

Even though the simpler Fermat test passed.

---

### Why is reaching $1$ this way suspicious?

This is where Blog 03 comes back.

Modulo a prime $p$, we are working in a field.

Suppose:

$$
x^2\equiv1\pmod p.
$$

Then:

$$
x^2-1\equiv0\pmod p.
$$

Factor:

$$
(x-1)(x+1)\equiv0\pmod p.
$$

Because a field has no non-zero zero divisors, one of those factors must vanish:

$$
x\equiv1\pmod p
$$

or:

$$
x\equiv-1\pmod p.
$$

So modulo a prime, the only square roots of $1$ are:

$$
\boxed{\pm1}.
$$

That is the structural fact Miller-Rabin exploits.

For a prime candidate, the repeated-squaring chain must behave in a very restricted way.

Either the initial value is already:

$$
1
$$

or:

$$
-1,
$$

or one of the later squarings reaches:

$$
-1
$$

before the final $1$.

If instead we reach $1$ through some other residue without encountering $-1$, we have exposed behavior incompatible with a prime modulus.

This is exactly why I like building the foundations first.

The fact that:

```text
prime modulus
→ field
→ no zero divisors
→ only ±1 square to 1
```

has now turned into a primality test.

---

A compact implementation is:

```python
from math import gcd
import secrets


def is_probable_prime(n, rounds=16):
    if n in (2, 3):
        return True

    if n < 2 or n % 2 == 0:
        return False

    # Write n - 1 = 2^s * d with d odd.
    d = n - 1
    s = 0

    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2

        if gcd(a, n) > 1:
            return False

        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)

            if x == n - 1:
                break
        else:
            return False

    return True
```

The output is deliberately asymmetric:

```text
False
```

means:

> definitely composite.

But:

```text
True
```

means:

> passed the tested Miller-Rabin rounds; probable prime.

That distinction is important.

---

## How much confidence do repeated rounds give us?

For an odd composite $n$, at most one quarter of the relevant bases can be strong Miller-Rabin liars.

So if we independently choose random bases, a fixed composite number survives $k$ rounds with probability at most:

$$
\left(\frac14\right)^k.
$$

That is the familiar bound.

But I want to be careful with the wording.

It does **not** automatically mean:

> "After $k$ rounds, the probability that my candidate is composite is exactly $4^{-k}$."

Those are different conditional probabilities.

The standards literature is careful about this distinction too.

NIST FIPS 186-5 explicitly warns that:

```text
probability a composite survives t rounds
```

is not the same quantity as:

```text
probability that a candidate which survived t rounds is composite
```

when analysing RSA prime generation.

That may sound like probability-theory bookkeeping, but it matters when standards choose concrete round counts.

---

> **Standards connection — this is not only a textbook algorithm.**  
> NIST FIPS 186-5 includes Miller-Rabin as a probabilistic primality test for RSA prime generation. It permits optional trial division first, followed by either repeated Miller-Rabin testing or Miller-Rabin followed by a Lucas test, with round counts chosen according to candidate size and the target error analysis.
>
> [NIST FIPS 186-5 — Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.186-5)

And historically, the algorithm has an interesting lineage.

Gary Miller's 1976 work gave a deterministic polynomial-time primality test under the Extended Riemann Hypothesis.

Michael Rabin's 1980 paper turned the core idea into the unconditional probabilistic test that became the practical Miller-Rabin algorithm.

**Michael O. Rabin, "Probabilistic Algorithm for Testing Primality," Journal of Number Theory, 12(1), 1980.**

[DOI: 10.1016/0022-314X(80)90084-0](https://doi.org/10.1016/0022-314X(80)90084-0)

---

There is another distinction worth keeping.

Testing whether:

$$
n
$$

is prime is not the same problem as factoring:

$$
n.
$$

Miller-Rabin may tell us quickly:

```text
composite
```

without telling us the factors.

For example, a compositeness witness does not necessarily hand us:

$$
561=3\cdot11\cdot17.
$$

This is important cryptographically because RSA depends on the difficulty of factoring a carefully generated composite modulus, not on primality testing itself being difficult.

In fact, deterministic polynomial-time primality testing exists.

The famous AKS result showed that:

$$
\text{PRIMES}\in\mathbf P.
$$

Practical cryptographic implementations still often prefer highly efficient probable-prime generation pipelines rather than using AKS.

So:

```text
primality testing
≠
integer factorization
```

Again, two nearby-looking number-theory problems with very different computational status.

---

A good experiment for the repository is to compare three layers:

```text
trial division
Fermat test
Miller-Rabin
```

Try:

```text
17
19
21
341
561
1105
1729
```

For each number record:

```text
actual factorization for the toy experiment
Fermat base-2 result
Miller-Rabin base-2 trace
```

Especially inspect $561$.

The point is not to memorize a list of pseudoprimes.

The point is to see why each stronger algorithm checks more mathematical structure than the previous one.

---

We now understand how to test candidate primes.

That finally lets us ask the next cryptographic question properly:

> How do we actually generate the primes used inside RSA?

Not just "pick two primes."

How large?

How random?

What checks must hold?

Why should $p$ and $q$ not be too close?

What happens if random-number generation fails and two devices accidentally share a prime?

That takes us from primality testing to **RSA key generation itself**.

**Next:** *RSA Key Generation From Zero: Choosing $p$, $q$, $e$, and Building the Private Exponent.*
