---
title: "Prime Numbers II: Primality Testing"
description: "A detailed progression from trial division and sieving to Fermat, Solovay–Strassen, Miller–Rabin, pseudoprimes, witnesses, error bounds, and practical probable-prime testing."
pubDate: "2025-05-05"
updatedDate: "2026-09-16"
topics:
  - "Number Theory"
  - "Cryptanalysis"
  - "Cryptographic Engineering"
tags:
  - "primality-testing"
  - "miller-rabin"
  - "fermat-test"
  - "solovay-strassen"
  - "sieve"
  - "pseudoprimes"
difficulty: "Intermediate"
series: "Elementary Number Theory Reference"
seriesOrder: 7
sourcePath: "experiments/ready-material/primes"
draft: false
---

In Part I, we separated several questions that are easy to confuse:

```text
prime structure
prime distribution
primality testing
integer factorization
```

We now focus on the third one.

Given an integer

\[
n,
\]

how do we determine whether \(n\) is prime?

For a tiny integer, we can try possible divisors.

For a cryptographic candidate containing hundreds or thousands of bits, exhaustive division is not a serious strategy.

The key conceptual transition is therefore:

\[
\boxed{
\text{search for factors}
\longrightarrow
\text{test structural properties forced by primality}.
}
\]

This leads to several increasingly powerful approaches:

\[
\text{trial division}
\rightarrow
\text{Fermat}
\rightarrow
\text{Euler/Jacobi}
\rightarrow
\text{Miller-Rabin}.
\]

The progression is important.

Each test does not merely "try harder."

Each one examines **more mathematical structure** than the previous one.

---

## Table of Contents

- [What does a primality test need to decide?](#what-does-a-primality-test-need-to-decide)
- [Trial division](#trial-division)
- [Why checking up to (\sqrt n) is enough](#why-checking-up-to-sqrt-n-is-enough)
- [The Sieve of Eratosthenes](#the-sieve-of-eratosthenes)
- [Sieve versus primality test](#sieve-versus-primality-test)
- [Probable-prime tests](#probable-prime-tests)
- [Fermat’s primality test](#fermats-primality-test)
- [Pseudoprimes and Carmichael numbers](#pseudoprimes-and-carmichael-numbers)
- [Why a stronger test is possible](#why-a-stronger-test-is-possible)
- [Solovay-Strassen](#solovay-strassen)
- [Miller-Rabin](#miller-rabin)
- [Why Miller-Rabin works](#why-miller-rabin-works)
- [The (561) example](#the-561-example)
- [A compact Miller-Rabin implementation](#a-compact-miller-rabin-implementation)
- [Why Miller-Rabin is stronger](#why-miller-rabin-is-stronger)
- [Error probability](#error-probability)
- [Witnesses and liars](#witnesses-and-liars)
- [Deterministic Miller-Rabin on bounded inputs](#deterministic-miller-rabin-on-bounded-inputs)
- [Why random bases still matter](#why-random-bases-still-matter)
- [Binary modular exponentiation](#binary-modular-exponentiation)
- [A verbose Miller-Rabin trace](#a-verbose-miller-rabin-trace)
- [Solovay-Strassen in Python](#solovay-strassen-in-python)
- [The role of Carmichael numbers](#the-role-of-carmichael-numbers)
- [Strong pseudoprimes](#strong-pseudoprimes)
- [Primality testing versus proof of primality](#primality-testing-versus-proof-of-primality)
- [AKS and the complexity perspective](#aks-and-the-complexity-perspective)
- [A small experimental comparison](#a-small-experimental-comparison)
- [A note on prime races](#a-note-on-prime-races)
- [Cryptographic prime-generation pipeline](#cryptographic-prime-generation-pipeline)
- [Implementation caution](#implementation-caution)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Next](#next)
- [Next](#next-1)

---

## What does a primality test need to decide?

A primality test receives an integer \(n\) and asks:

\[
\boxed{
n\text{ prime?}
}
\]

There are two possible mathematical realities:

```text
prime
```

or:

```text
composite
```

But not every algorithm returns the answer with the same logical strength.

A deterministic primality test may return:

```text
prime
```

or:

```text
composite
```

with mathematical certainty.

A probabilistic probable-prime test typically behaves asymmetrically:

```text
composite
```

means:

> compositeness has been proved by a witness;

whereas:

```text
probably prime
```

means:

> no witness was found in the rounds performed.

That asymmetry is fundamental.

We should never silently replace:

```text
probable prime
```

with:

```text
proved prime
```

unless the algorithm and parameter regime justify that conclusion.

---

## Trial division

The most direct primality test follows immediately from the definition.

If

\[
n>1
\]

is composite, then:

\[
n=ab
\]

for some nontrivial integers \(a,b\).

Therefore, we can search for a divisor.

A deliberately naive implementation is:

```python
def is_prime_bruteforce(n):
    if n < 2:
        return False

    for d in range(2, n):
        if n % d == 0:
            return False

    return True
```

This is mathematically correct.

Computationally, it is terrible.

If \(n\) is prime, the loop checks almost every integer below \(n\).

---

## Why checking up to \(\sqrt n\) is enough

Suppose:

\[
n=ab
\]

is composite.

If both:

\[
a>\sqrt n
\]

and:

\[
b>\sqrt n,
\]

then:

\[
ab>n,
\]

contradicting:

\[
ab=n.
\]

Therefore every composite integer has at least one factor satisfying:

\[
\boxed{
d\le\sqrt n.
}
\]

So trial division only needs to search up to the square root.

A cleaner implementation avoids floating-point square roots entirely:

```python
def is_prime_trial(n):
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    d = 3

    while d * d <= n:
        if n % d == 0:
            return False

        d += 2

    return True
```

We first eliminate even numbers and then test only odd divisors.

### Complexity perspective

Let \(n\) be approximately a \(k\)-bit integer:

\[
n\approx2^k.
\]

Then:

\[
\sqrt n
\approx
2^{k/2}.
\]

So trial division still requires work exponential in the bit length \(k\).

That is why:

\[
\boxed{
\text{trial division is useful for small factors,}
}
\]

but:

\[
\boxed{
\text{it is not a cryptographic-size primality strategy.}
}
\]

---

## The Sieve of Eratosthenes

Trial division answers:

> Is this particular number prime?

The Sieve of Eratosthenes solves a different problem:

> What are all the primes up to some bound \(N\)?

Start with:

\[
2,3,4,\ldots,N.
\]

Then repeatedly remove multiples of each prime:

```text
remove multiples of 2
remove multiples of 3
remove multiples of 5
remove multiples of 7
...
```

Once the sieving prime exceeds:

\[
\sqrt N,
\]

every remaining unmarked number is prime.

A compact implementation is:

```python
def sieve(limit):
    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)

    is_prime[0] = False
    is_prime[1] = False

    p = 2

    while p * p <= limit:
        if is_prime[p]:
            for multiple in range(
                p * p,
                limit + 1,
                p,
            ):
                is_prime[multiple] = False

        p += 1

    return [
        n
        for n, flag in enumerate(is_prime)
        if flag
    ]
```

For example:

```python
print(sieve(50))
```

returns:

```text
[2, 3, 5, 7, 11, 13, 17, 19,
 23, 29, 31, 37, 41, 43, 47]
```

### Why start at \(p^2\)?

When processing a prime \(p\), the smaller multiples:

\[
2p,3p,\ldots,(p-1)p
\]

have already been removed by smaller prime factors.

So the first new composite that needs to be marked is:

\[
p^2.
\]

### Complexity

The classical sieve runs in roughly:

\[
O(N\log\log N)
\]

time with:

\[
O(N)
\]

logical storage.

Actual memory consumption depends strongly on the implementation.

For example, a Python:

```python
list
```

of booleans does **not** store one raw bit per entry; Python objects and references add substantial overhead.

For large sieves, specialized bit arrays or segmented sieves are much more memory efficient.

---

## Sieve versus primality test

The distinction is useful:

```text
SIEVE

generate many primes
up to a bounded range
```

versus:

```text
PRIMALITY TEST

classify one potentially huge integer
```

If we need every prime below one million, sieving is excellent.

If we need to determine whether one random \(2048\)-bit candidate is prime, constructing a sieve up to its square root would be absurd.

Different computational problem.

Different algorithm.

---

## Probable-prime tests

Instead of searching for factors, modern probable-prime tests exploit identities that every prime must satisfy.

A chosen value \(a\) is called a **witness** when it demonstrates that \(n\) cannot be prime.

If no witness is found, the candidate survives that round.

The crucial logical pattern is:

\[
\boxed{
\text{witness found}
\Longrightarrow
\text{definitely composite}.
}
\]

But:

\[
\boxed{
\text{no witness found}
\not\Longrightarrow
\text{proved prime}.
}
\]

Different tests define different kinds of witnesses and have very different liar sets.

That distinction matters enormously.

---

## Fermat's primality test

Fermat's little theorem states that if \(p\) is prime and:

\[
\gcd(a,p)=1,
\]

then:

\[
\boxed{
a^{p-1}\equiv1\pmod p.
}
\]

Therefore, if for some candidate \(n\) and some \(a\) we obtain:

\[
a^{n-1}\not\equiv1\pmod n,
\]

then \(n\) cannot be prime.

The base \(a\) is a **Fermat witness**.

### Algorithm

For odd \(n>3\):

1. choose:
   \[
   2\le a\le n-2;
   \]

2. compute:
   \[
   g=\gcd(a,n);
   \]

3. if:
   \[
   g>1,
   \]
   return composite;

4. compute:
   \[
   a^{n-1}\bmod n;
   \]

5. if the result is not \(1\), return composite;

6. otherwise, the candidate passes this Fermat round.

A basic implementation is:

```python
from math import gcd
import secrets


def fermat_round(n, a):
    g = gcd(a, n)

    if g != 1:
        return False

    return pow(a, n - 1, n) == 1


def fermat_test(n, rounds=16):
    if n in (2, 3):
        return True

    if n < 2 or n % 2 == 0:
        return False

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2

        if not fermat_round(n, a):
            return False

    return True
```

If this returns:

```text
False
```

the number is composite.

If it returns:

```text
True
```

it merely passed the selected Fermat bases.

---

## Pseudoprimes and Carmichael numbers

The weakness of Fermat testing is that some composite numbers imitate prime behavior.

For example:

\[
341=11\cdot31
\]

satisfies:

\[
2^{340}\equiv1\pmod{341}.
\]

So \(341\) is a **Fermat pseudoprime to base \(2\)**.

Even worse are Carmichael numbers.

A Carmichael number is a composite integer \(n\) satisfying:

\[
\boxed{
a^{n-1}\equiv1\pmod n
}
\]

for every:

\[
\gcd(a,n)=1.
\]

The smallest is:

\[
561
=
3\cdot11\cdot17.
\]

For every base coprime to \(561\):

\[
a^{560}
\equiv1\pmod{561}.
\]

Thus, repeated Fermat testing with coprime bases cannot rescue the algorithm.

This is a structural failure, not simply bad luck.

That is the key limitation of Fermat testing.

---

## Why a stronger test is possible

Fermat only checks the final equality:

\[
a^{n-1}\stackrel{?}{\equiv}1\pmod n.
\]

But there is more information hidden inside the exponentiation.

For a prime modulus, intermediate powers must satisfy additional algebraic constraints.

That observation gives us stronger tests.

---

## Solovay-Strassen

Solovay-Strassen strengthens Fermat testing by combining modular exponentiation with quadratic-residue information.

For an odd prime \(p\), Euler's criterion states:

\[
\boxed{
a^{(p-1)/2}
\equiv
\left(\frac ap\right)
\pmod p,
}
\]

where:

\[
\left(\frac ap\right)
\]

is the Legendre symbol.

For an odd candidate \(n\), Solovay-Strassen replaces the Legendre symbol with the Jacobi symbol:

\[
\left(\frac an\right).
\]

If \(n\) is prime, then:

\[
a^{(n-1)/2}
\equiv
\left(\frac an\right)
\pmod n.
\]

Therefore, a mismatch proves compositeness.

### One Solovay-Strassen round

Choose:

\[
2\le a\le n-2.
\]

If:

\[
\gcd(a,n)>1,
\]

then \(n\) is composite.

Otherwise compute:

\[
r
=
a^{(n-1)/2}\bmod n
\]

and:

\[
J
=
\left(\frac an\right).
\]

Because \(J\in\{-1,0,1\}\), compare:

\[
r
\]

with:

\[
J\bmod n.
\]

If they differ, \(a\) is an Euler-Jacobi witness and \(n\) is composite.

### Why it is better than Fermat

For every odd composite \(n\), at least half of the admissible bases expose compositeness under the Solovay-Strassen criterion.

So after \(k\) independent random rounds, the survival probability of a fixed composite is at most:

\[
\left(\frac12\right)^k.
\]

That is already a much stronger universal guarantee than Fermat's test provides.

Historically, Solovay-Strassen was important.

In modern practical implementations, Miller-Rabin is generally preferred because it gives a stronger witness condition with a better worst-case bound.

---

## Miller-Rabin

Miller-Rabin examines the structure of repeated squaring much more closely.

Let:

\[
n>2
\]

be odd.

Write:

\[
\boxed{
n-1
=
2^s d,
}
\]

where \(d\) is odd.

For a chosen base:

\[
2\le a\le n-2,
\]

compute:

\[
x
=
a^d\bmod n.
\]

If \(n\) is prime, the structure of square roots of \(1\) forces a restricted pattern.

A Miller-Rabin round passes if:

\[
x=1
\]

or:

\[
x=n-1.
\]

Otherwise square repeatedly:

\[
x
\leftarrow
x^2\bmod n.
\]

Do this at most:

\[
s-1
\]

times.

If at any point:

\[
x=n-1,
\]

the base passes.

If not, the base is a **strong witness** proving that \(n\) is composite.

---

## Why Miller-Rabin works

The central fact is extremely simple.

Let \(p\) be prime.

Suppose:

\[
x^2\equiv1\pmod p.
\]

Then:

\[
x^2-1
\equiv0\pmod p.
\]

Factor:

\[
(x-1)(x+1)
\equiv0\pmod p.
\]

Because:

\[
\mathbb Z_p
\]

is a field, it has no nonzero zero divisors.

Therefore:

\[
x\equiv1\pmod p
\]

or:

\[
x\equiv-1\pmod p.
\]

Thus:

\[
\boxed{
\text{the only square roots of }1
\text{ modulo a prime are }\pm1.
}
\]

This is the structural property Miller-Rabin exploits.

---

## The \(561\) example

Consider:

\[
n=561.
\]

We know:

\[
561
=
3\cdot11\cdot17.
\]

But suppose we do not know the factors.

Write:

\[
560
=
2^4\cdot35.
\]

So:

\[
s=4,
\qquad
d=35.
\]

Choose:

\[
a=2.
\]

Compute:

\[
x_0
=
2^{35}\bmod561
=
263.
\]

Now square:

\[
x_1
=
263^2\bmod561
=
166,
\]

\[
x_2
=
166^2\bmod561
=
67,
\]

\[
x_3
=
67^2\bmod561
=
1.
\]

The chain is:

| Step | Value |
| ---: | ---: |
| \(2^{35}\) | \(263\) |
| square | \(166\) |
| square | \(67\) |
| square | \(1\) |

Notice what happened.

We reached:

\[
1
\]

from:

\[
67,
\]

but:

\[
67\not\equiv\pm1\pmod{561}.
\]

So \(67\) behaves like a nontrivial square root of \(1\).

That cannot happen modulo a prime.

Therefore:

\[
\boxed{
561\text{ is composite}.
}
\]

Fermat testing looked only at:

\[
2^{560}\equiv1\pmod{561}
\]

and missed the problem.

Miller-Rabin inspected the squaring chain and exposed it.

---

## A compact Miller-Rabin implementation

```python
from math import gcd
import secrets


def miller_rabin_round(n, a):
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

The wrapper handles easy cases and chooses independent random bases:

```python
def is_probable_prime(n, rounds=16):
    if n in (2, 3):
        return True

    if n < 2 or n % 2 == 0:
        return False

    # Cheap small-prime filtering.
    small_primes = (
        3, 5, 7, 11, 13,
        17, 19, 23, 29, 31,
        37,
    )

    for p in small_primes:
        if n == p:
            return True

        if n % p == 0:
            return False

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2

        if not miller_rabin_round(n, a):
            return False

    return True
```

Examples:

```python
assert is_probable_prime(17)
assert is_probable_prime(19)

assert not is_probable_prime(21)
assert not is_probable_prime(341)
assert not is_probable_prime(561)
assert not is_probable_prime(1105)
```

For large candidates:

```python
candidate = 2**521 - 1

print(
    is_probable_prime(
        candidate,
        rounds=32,
    )
)
```

Again, the meaning of `True` is:

```text
passed the selected Miller-Rabin rounds
```

unless we are using a deterministic base set for a proven bounded range.

---

## Why Miller-Rabin is stronger

We can think of the three tests as examining progressively more structure.

### Fermat

Checks:

\[
a^{n-1}
\stackrel{?}{\equiv}
1
\pmod n.
\]

It inspects only the final exponentiation result.

### Solovay-Strassen

Checks:

\[
a^{(n-1)/2}
\]

against:

\[
\left(\frac an\right).
\]

So it also examines quadratic-residue structure.

### Miller-Rabin

Factors:

\[
n-1=2^s d
\]

and examines the full repeated-squaring chain:

\[
a^d,
\quad
a^{2d},
\quad
a^{4d},
\quad
\ldots
\]

looking for behavior incompatible with a prime modulus.

Conceptually:

```text
Fermat
   ↓
final exponentiation identity

Solovay-Strassen
   ↓
Euler/Jacobi structure

Miller-Rabin
   ↓
strong repeated-squaring structure
```

This explains why the liar sets shrink as the tests become stronger.

---

## Error probability

For any fixed odd composite \(n\), Miller-Rabin has a powerful universal bound:

\[
\boxed{
\text{at most one quarter of the bases
can be strong liars}.
}
\]

Therefore, if independent random bases are chosen, the probability that the same fixed composite survives \(k\) rounds is at most:

\[
\boxed{
\left(\frac14\right)^k.
}
\]

For example:

| Rounds \(k\) | Upper bound |
| ---: | ---: |
| \(1\) | \(2^{-2}\) |
| \(8\) | \(2^{-16}\) |
| \(16\) | \(2^{-32}\) |
| \(32\) | \(2^{-64}\) |
| \(64\) | \(2^{-128}\) |

This is a bound on:

\[
\Pr[
\text{survives }k\text{ rounds}
\mid
\text{candidate is composite}
].
\]

It is **not** automatically:

\[
\Pr[
\text{candidate is composite}
\mid
\text{candidate survived}
].
\]

Those are different conditional probabilities.

The latter also depends on how candidates are sampled and how common primes are in that population.

This distinction matters when formal standards assign concrete confidence levels to prime-generation procedures.

---

## Witnesses and liars

For a composite \(n\), a Miller-Rabin base \(a\) is a **strong witness** when it exposes compositeness.

A base that allows the composite to pass one round is called a **strong liar**.

Thus:

```text
strong witness
    ↓
proves composite

strong liar
    ↓
one round fails to expose composite
```

The strength of Miller-Rabin comes from the fact that, for a fixed odd composite, the liar set is provably small.

This is fundamentally different from Fermat testing, where Carmichael numbers can fool **every coprime base**.

---

## Deterministic Miller-Rabin on bounded inputs

Miller-Rabin is probabilistic in the general unbounded setting.

But if the input range is bounded, carefully chosen fixed bases can make it deterministic over that entire range.

For unsigned \(64\)-bit integers, one well-known sufficient base set is:

```text
2
325
9375
28178
450775
9780504
179526502
```

Using those bases, Miller-Rabin correctly classifies every integer below:

\[
2^{64}.
\]

The bases need not themselves be prime.

Each one is simply reduced modulo \(n\) during testing.

A bounded deterministic implementation can therefore use:

```python
MR_BASES_64 = (
    2,
    325,
    9375,
    28178,
    450775,
    9780504,
    179526502,
)
```

and test every relevant base instead of sampling randomly.

The important lesson is:

\[
\boxed{
\text{deterministic for a bounded domain}
\neq
\text{universally deterministic}.
}
\]

The correctness guarantee depends on the proven input range and chosen base set.

---

## Why random bases still matter

For arbitrary large integers, random-base Miller-Rabin remains extremely useful.

Prime generation commonly combines:

```text
random odd candidate
        ↓
small-prime filtering
        ↓
several Miller-Rabin rounds
        ↓
probable prime
```

Additional tests or proof-producing methods may be used depending on the standard and application.

The point is not that Miller-Rabin magically proves arbitrary primes.

The point is that:

\[
\boxed{
\text{its one-sided error can be made negligibly small}
}
\]

with very little computational work.

---

## Binary modular exponentiation

Miller-Rabin depends heavily on computing expressions such as:

\[
a^d\bmod n
\]

efficiently.

A naive exponentiation is inappropriate.

Instead, implementations use binary modular exponentiation, also called:

- exponentiation by squaring,
- square-and-multiply.

A simple version is:

```python
def powmod_binary(base, exponent, modulus):
    result = 1
    base %= modulus

    while exponent > 0:
        if exponent & 1:
            result = (
                result * base
            ) % modulus

        base = (
            base * base
        ) % modulus

        exponent >>= 1

    return result
```

Its operation count is:

\[
O(\log e)
\]

rather than:

\[
O(e).
\]

In normal Python code:

```python
pow(base, exponent, modulus)
```

already performs efficient modular exponentiation and should normally be preferred.

---

## A verbose Miller-Rabin trace

For educational purposes, it is useful to expose the squaring chain.

```python
def miller_rabin_trace(n, a):
    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    x = pow(a, d, n)

    trace = [x]

    for _ in range(s - 1):
        x = pow(x, 2, n)
        trace.append(x)

    return s, d, trace
```

For:

```python
s, d, trace = miller_rabin_trace(
    561,
    2,
)

print(s)
print(d)
print(trace)
```

we obtain:

```text
4
35
[263, 166, 67, 1]
```

That trace contains more information than the simple Fermat result:

```python
pow(2, 560, 561)
```

which returns:

```text
1
```

This is a nice example of a general cryptographic theme:

> The final output may hide structure that becomes visible when we inspect the intermediate algebra.

---

## Solovay-Strassen in Python

For historical completeness, we can also implement Solovay-Strassen.

Assume a `jacobi(a, n)` function returning:

```text
-1, 0, or 1
```

for odd positive \(n\).

```python
from math import gcd


def solovay_strassen_round(n, a, jacobi):
    if gcd(a, n) != 1:
        return False

    lhs = pow(
        a,
        (n - 1) // 2,
        n,
    )

    rhs = jacobi(a, n) % n

    return lhs == rhs
```

The `% n` on the Jacobi result matters.

If:

\[
\left(\frac an\right)=-1,
\]

then modular comparison means:

\[
-1
\equiv
n-1
\pmod n.
\]

This is a good example of the difference between an integer-valued symbol and its residue-class interpretation.

---

## The role of Carmichael numbers

Carmichael numbers illustrate a useful hierarchy.

A Carmichael number defeats naive Fermat testing for every coprime base.

But that does **not** mean it defeats Miller-Rabin for every base.

For example:

\[
561
\]

passes Fermat base \(2\):

\[
2^{560}
\equiv1\pmod{561},
\]

yet Miller-Rabin base \(2\) exposes compositeness immediately.

Thus:

\[
\boxed{
\text{Fermat pseudoprime}
\not\Rightarrow
\text{strong pseudoprime}.
}
\]

This is exactly why the stronger test exists.

---

## Strong pseudoprimes

A composite integer \(n\) that passes Miller-Rabin for a particular base \(a\) is called a **strong pseudoprime to base \(a\)**.

This does not contradict the correctness of Miller-Rabin.

The algorithm is designed around the fact that some liars exist.

Its strength comes from bounding how many there can be.

So:

```text
composite + one passing base
```

is possible.

But:

```text
composite + many independent passing bases
```

becomes increasingly unlikely under random-base testing.

The next article can study deliberately constructed pseudoprimes and adversarial base sets in much greater depth.

---

## Primality testing versus proof of primality

At this stage, it is useful to distinguish three levels.

### Composite witness

A single witness may prove:

\[
\boxed{
n\text{ composite}.
}
\]

### Probable prime

Repeated Miller-Rabin tests may establish overwhelming practical confidence:

\[
\boxed{
n\text{ is a probable prime}.
}
\]

### Primality proof

Some algorithms produce or support a proof that:

\[
\boxed{
n\text{ is definitely prime}.
}
\]

Examples of the broader landscape include:

- deterministic algorithms such as AKS,
- certificate-based methods,
- elliptic-curve primality proving methods,
- specialized tests for structured integers.

Miller-Rabin occupies a particularly useful practical position because it is:

- simple,
- fast,
- easy to implement correctly,
- supported by strong error bounds,
- extremely effective in prime-generation pipelines.

---

## AKS and the complexity perspective

A major theoretical breakthrough established that primality testing belongs to deterministic polynomial time.

The AKS algorithm showed:

\[
\boxed{
\mathrm{PRIMES}\in\mathbf P.
}
\]

This result is conceptually important because it proves that primality testing is not inherently a hard problem in the classical complexity-theoretic sense.

But polynomial-time does not automatically mean fastest in practice.

For ordinary cryptographic prime generation, highly optimized probable-prime testing is usually much more practical.

So there is an important distinction:

```text
THEORETICAL RESULT

primality has a deterministic
polynomial-time algorithm
```

versus:

```text
ENGINEERING CHOICE

Miller-Rabin and related procedures
are extremely efficient in practice
```

---

## A small experimental comparison

A good repository experiment is to compare:

```text
trial division
Fermat
Solovay-Strassen
Miller-Rabin
```

using values such as:

```text
17
19
21
341
561
1105
1729
2465
2821
6601
```

For each number, record:

| \(n\) | Actual status | Fermat base 2 | Solovay-Strassen base 2 | Miller-Rabin base 2 |
| ---: | --- | --- | --- | --- |
| \(17\) | prime | ? | ? | ? |
| \(341\) | composite | ? | ? | ? |
| \(561\) | composite | ? | ? | ? |
| \(1105\) | composite | ? | ? | ? |
| \(1729\) | composite | ? | ? | ? |

The purpose is not to memorize pseudoprimes.

The point is to observe:

\[
\boxed{
\text{each stronger test examines more structure}.
}
\]

---

## A note on prime races

Prime distribution contains many interesting statistical phenomena that are separate from primality testing.

For example, among odd primes we may compare:

\[
p\equiv1\pmod4
\]

with:

\[
p\equiv3\pmod4.
\]

Dirichlet's theorem implies that asymptotically the two residue classes receive equal prime density.

Yet over finite ranges there can be noticeable biases, such as the classical **Chebyshev bias**.

More subtle correlations also occur between residue classes of consecutive primes.

These phenomena are fascinating, but they concern the **distribution of primes**, not the problem of deciding whether one candidate is prime.

That distinction is exactly why we keep prime distribution and primality testing conceptually separate.

---

## Cryptographic prime-generation pipeline

We can now refine the pipeline from Part I.

A simplified educational version is:

```text
cryptographically random bits
        ↓
force required bit length
        ↓
force oddness
        ↓
small-prime trial division
        ↓
Miller-Rabin rounds
        ↓
additional scheme-specific checks
        ↓
probable prime accepted
```

For RSA, we repeat this process independently to generate:

\[
p
\]

and:

\[
q.
\]

The primality test is therefore only one component of secure key generation.

Other requirements include:

- entropy quality,
- prime size,
- independence,
- parameter constraints,
- key validation.

A mathematically correct primality test cannot rescue a broken random-number generator.

---

## Implementation caution

The Python implementations in this article are designed to expose the mathematics.

They are not intended to replace vetted cryptographic libraries.

Production implementations also need to consider:

- randomness quality,
- parameter validation,
- timing behavior,
- denial-of-service inputs,
- arbitrary-precision arithmetic behavior,
- standard-specific round counts,
- deterministic versus probabilistic guarantees.

That distinction should remain explicit throughout this reference series:

\[
\boxed{
\text{educational implementation}
\neq
\text{production cryptographic implementation}.
}
\]

---

## Practice and checkpoint

### Exercise 1 — Trial division

Implement a primality test using:

```python
d * d <= n
```

rather than:

```python
sqrt(n)
```

Verify it on:

\[
2,3,4,17,21,97,121.
\]

### Exercise 2 — Sieve

Generate every prime below:

\[
1000.
\]

Verify that there are:

\[
168
\]

primes satisfying:

\[
p\le1000.
\]

### Exercise 3 — Fermat pseudoprime

Verify:

\[
341=11\cdot31
\]

and:

\[
2^{340}
\equiv1\pmod{341}.
\]

Explain why base-\(2\) Fermat testing fails.

### Exercise 4 — Carmichael number

Verify that:

\[
561
=
3\cdot11\cdot17.
\]

Test several bases coprime to \(561\) and confirm:

\[
a^{560}
\equiv1\pmod{561}.
\]

### Exercise 5 — Miller-Rabin trace

For:

\[
n=561,
\qquad
a=2,
\]

derive:

\[
560=2^4\cdot35
\]

and reproduce:

\[
263
\rightarrow
166
\rightarrow
67
\rightarrow
1.
\]

Explain exactly why \(67\) proves compositeness.

### Exercise 6 — Strong pseudoprimes

Search for a composite integer that passes one Miller-Rabin base.

Then test additional bases.

Observe that:

```text
passes base a
```

does not imply:

```text
prime
```

for a single round.

### Exercise 7 — Error bounds

Compute:

\[
4^{-10},
\]

\[
4^{-20},
\]

and:

\[
4^{-64}.
\]

Express the results approximately as powers of \(2\).

### Exercise 8 — Conditional probability

Explain why:

\[
\Pr(
\text{passes}\mid\text{composite}
)
\]

is not the same as:

\[
\Pr(
\text{composite}\mid\text{passes}
).
\]

What additional information is needed for the second quantity?

### Exercise 9 — Bounded deterministic testing

Implement the \(64\)-bit Miller-Rabin base set:

```python
(
    2,
    325,
    9375,
    28178,
    450775,
    9780504,
    179526502,
)
```

and compare the results against a trusted library for randomly sampled values below:

\[
2^{64}.
\]

### Reader checkpoint

You should now be able to explain:

1. Why trial division only needs to search up to \(\sqrt n\).
2. Why that is still exponential in the bit length.
3. The difference between a sieve and a primality test.
4. What a compositeness witness is.
5. Why Fermat's test has one-sided logical value.
6. What a Fermat pseudoprime is.
7. Why Carmichael numbers fundamentally defeat naive repeated Fermat testing.
8. What additional structure Solovay-Strassen tests.
9. Why Miller-Rabin factors
   \[
   n-1=2^s d.
   \]
10. Why a prime modulus has only the square roots
    \[
    \pm1
    \]
    of \(1\).
11. What a strong witness is.
12. What a strong liar is.
13. Why Miller-Rabin has a worst-case \(1/4\) liar bound per random round.
14. Why
    \[
    4^{-k}
    \]
    is not automatically the posterior probability that a surviving candidate is composite.
15. Why bounded fixed-base Miller-Rabin can be deterministic.
16. Why deterministic bounded testing does not imply a universal fixed finite base set.
17. Why primality testing and integer factorization are computationally different.
18. Why practical prime generation still depends on secure randomness.

If these points are clear, we now understand not only how to test candidate primes, but also why increasingly sophisticated primality tests work.

---

## References and further reading

**Michael O. Rabin**,  
*Probabilistic Algorithm for Testing Primality*,  
Journal of Number Theory, 1980.

The foundational probabilistic formulation associated with the modern Miller-Rabin test.

**Gary L. Miller**,  
*Riemann's Hypothesis and Tests for Primality*,  
Journal of Computer and System Sciences, 1976.

The deterministic precursor underlying the Miller-Rabin construction.

**Robert Solovay and Volker Strassen**,  
*A Fast Monte-Carlo Test for Primality*,  
SIAM Journal on Computing, 1977.

The classical Euler-Jacobi probable-prime test.

**Manindra Agrawal, Neeraj Kayal, and Nitin Saxena**,  
*PRIMES is in P*,  
Annals of Mathematics, 2004.

The landmark deterministic polynomial-time primality-testing result.

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

A comprehensive reference for primality testing, pseudoprimes, prime generation, and computational number theory.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

An excellent bridge between the underlying group theory and efficient algorithms.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Provides the cryptographic context for prime generation, probable-prime testing, and modular arithmetic.

---

## Next

Miller-Rabin gives us an extraordinarily effective practical test.

But it also introduces a natural adversarial question:

> Can we deliberately construct composite numbers that fool chosen primality-test bases?

That takes us from ordinary pseudoprimes into:

- strong pseudoprimes,
- simultaneous pseudoprimes to several bases,
- adversarial constructions,
- the limits of fixed-base testing,
- and deeper questions about how liar sets are structured.

That is the natural final stage of this prime-number sequence.

## Next

Primality testing asked whether a candidate integer satisfies the arithmetic structure expected from a prime.

The next step changes the question.

Instead of deciding whether an integer is prime, we begin solving equations inside modular arithmetic itself:

\[
f(x)\equiv0\pmod m.
\]

We will start with linear congruences and their connection to Bézout identities and Diophantine equations, then move to higher-degree polynomial congruences, prime-power moduli, Hensel lifting, and reconstruction through the Chinese Remainder Theorem.

This brings together several tools developed throughout the series:

\[
\text{GCD}
\rightarrow
\text{modular inverses}
\rightarrow
\text{CRT}
\rightarrow
\text{prime powers}
\rightarrow
\text{polynomial congruences}.
\]

**Next: Solving Polynomial Congruences I.**
