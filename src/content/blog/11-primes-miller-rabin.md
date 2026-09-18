---
title: "Prime Numbers for Cryptographers: From Trial Division to Miller-Rabin"
description: "Why cryptography needs large primes, why trial division stops scaling, how Fermat pseudoprimes fool naive tests, and how Miller-Rabin turns modular structure into a practical probable-prime test."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Number Theory"
  - "Public-Key Cryptography"
tags:
  - "primes"
  - "primality-testing"
  - "fermat"
  - "miller-rabin"
  - "rsa"
  - "cryptography-from-zero"
difficulty: "Introductory"
series: "Cryptography From Zero"
seriesOrder: 12
draft: false
---

We have been using prime numbers almost from the beginning of this series.

Modulo a prime, every nonzero residue has an inverse.

Diffie-Hellman often works inside groups of large prime order.

RSA begins by generating large primes.

Later, finite fields, elliptic curves, and several post-quantum constructions will make us think carefully about primes again.

So eventually one question becomes unavoidable:

> If a candidate prime contains hundreds or thousands of bits, how do we know that it is actually prime?

For a small number, we can simply try divisors.

For a cryptographic-size number, that strategy quickly becomes useless.

Primality testing therefore becomes its own computational problem.

And the practical solution is interesting because it does not begin by trying harder to factor the number.

Instead, it asks:

> **Does this number behave in a way that every prime is forced to behave?**

That takes us from trial division to Fermat's little theorem, pseudoprimes, Carmichael numbers, and finally the Miller-Rabin primality test.

![Fermat versus Miller-Rabin on the Carmichael number 561](/images/blog/11-miller-rabin-561.svg)

*The composite number $561$ passes the simple Fermat test to base $2$, but its Miller-Rabin squaring chain reveals behavior that cannot occur modulo a prime.*

---

## Why trial division stops scaling

An integer $n>1$ is prime if its only positive divisors are

$$
1
\qquad\text{and}\qquad
n.
$$

So the most direct primality test is to search for a divisor:

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

Why do we stop once

$$
d>\sqrt n?
$$

Suppose $n$ is composite:

$$
n=ab.
$$

If both $a$ and $b$ were larger than $\sqrt n$, then

$$
ab>n,
$$

which is impossible.

Therefore, any composite $n$ must have at least one factor satisfying

$$
d\le\sqrt n.
$$

For small numbers, trial division is perfectly reasonable.

The problem becomes obvious when we think in terms of **bit length**.

A $k$-bit integer has magnitude roughly

$$
2^k.
$$

Its square root therefore has magnitude roughly

$$
2^{k/2}.
$$

So a method that may need to test divisors up to $\sqrt n$ requires work exponential in the bit length of the input.

For a cryptographic-size candidate, we need a fundamentally different approach.

---

## Fermat gives a test — but not a proof

Let $p$ be prime.

If

$$
\gcd(a,p)=1,
$$

then Fermat's little theorem tells us that

$$
a^{p-1}\equiv1\pmod p.
$$

That immediately suggests a primality test.

Given an odd candidate $n$, choose a base $a$ and compute

$$
a^{n-1}\bmod n.
$$

If

$$
a^{n-1}\not\equiv1\pmod n,
$$

then we know something definitive:

$$
\boxed{
n\text{ is composite.}
}
$$

So a failure of the Fermat congruence is a **certificate of compositeness**.

The problem is the opposite direction.

If

$$
a^{n-1}\equiv1\pmod n,
$$

we cannot conclude that $n$ is prime.

Some composite integers behave like primes for particular bases.

These are called **Fermat pseudoprimes**.

A classic example is

$$
561=3\cdot11\cdot17.
$$

It is obviously composite.

Yet

$$
2^{560}\equiv1\pmod{561}.
$$

So the base-$2$ Fermat test says, in effect:

```text
no compositeness detected
```

even though

```text
561 = 3 × 11 × 17
```

is composite.

And $561$ is even more interesting than an ordinary pseudoprime.

It is the smallest **Carmichael number**.

For every integer $a$ satisfying

$$
\gcd(a,561)=1,
$$

we have

$$
a^{560}\equiv1\pmod{561}.
$$

So simply repeating the basic Fermat test using many coprime bases does not repair the fundamental weakness.

The lesson is important:

> **Passing a necessary condition for primality is not the same thing as proving primality.**

We need a test that checks more structure.

---

## Miller-Rabin looks inside the exponentiation

The Miller-Rabin test begins from the same general world as Fermat's theorem but examines the modular exponentiation much more carefully.

Take an odd candidate $n>2$.

Factor all powers of two out of $n-1$:

$$
n-1=2^s d,
$$

where $d$ is odd.

For

$$
n=561,
$$

we have

$$
560=2^4\cdot35.
$$

Therefore,

$$
s=4,
\qquad
d=35.
$$

Now choose the base

$$
a=2.
$$

The simple Fermat test asks only whether

$$
2^{560}\equiv1\pmod{561}.
$$

Miller-Rabin starts much earlier.

First compute

$$
x_0
=
2^{35}\bmod561.
$$

This gives

$$
x_0=263.
$$

Then repeatedly square:

$$
x_1
=
263^2\bmod561
=
166,
$$

$$
x_2
=
166^2\bmod561
=
67,
$$

and

$$
x_3
=
67^2\bmod561
=
1.
$$

So the chain is:

| Step | Value modulo $561$ |
| ---: | ---: |
| $2^{35}$ | $263$ |
| $263^2$ | $166$ |
| $166^2$ | $67$ |
| $67^2$ | $1$ |

The interesting value that never appears is

$$
-1\equiv560\pmod{561}.
$$

That is what exposes the compositeness.

Miller-Rabin therefore rejects $561$ for base $2$, even though the ordinary Fermat test accepts it.

$$
\boxed{
561\text{ is composite.}
}
$$

---

## Why is reaching $1$ this way suspicious?

This is where our earlier study of modular arithmetic becomes useful.

If $p$ is prime, then

$$
\mathbb Z_p
$$

is a field.

Suppose some nonzero value $x$ satisfies

$$
x^2\equiv1\pmod p.
$$

Then

$$
x^2-1\equiv0\pmod p.
$$

Factor:

$$
(x-1)(x+1)\equiv0\pmod p.
$$

A field has no nonzero zero divisors.

Therefore at least one factor must vanish:

$$
x-1\equiv0\pmod p
$$

or

$$
x+1\equiv0\pmod p.
$$

Thus,

$$
x\equiv1\pmod p
$$

or

$$
x\equiv-1\pmod p.
$$

So modulo a prime,

$$
\boxed{
x^2\equiv1\pmod p
\quad\Longrightarrow\quad
x\equiv\pm1\pmod p.
}
$$

These are the only square roots of $1$ modulo a prime.

That structural fact is exactly what Miller-Rabin exploits.

For a prime candidate, the repeated-squaring chain must behave in a restricted way.

Starting from

$$
x_0=a^d\bmod n,
$$

a Miller-Rabin round accepts the base if either

$$
x_0=1,
$$

or

$$
x_0=-1\pmod n,
$$

or one of the later squarings reaches

$$
-1\pmod n.
$$

If instead the chain reaches

$$
1
$$

from some residue other than

$$
\pm1,
$$

then we have found a **nontrivial square root of $1$**.

That cannot happen modulo a prime.

So the candidate must be composite.

This gives a useful chain of reasoning:

```text
prime modulus
      ↓
field
      ↓
no zero divisors
      ↓
only ±1 can square to 1
      ↓
restricted squaring chain
      ↓
Miller-Rabin witness
```

This is exactly why learning the algebra first pays off.

A basic structural property of fields has become a practical primality test.

---

## Implementing Miller-Rabin

A compact randomized implementation is:

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

The algorithm deliberately has asymmetric conclusions.

If it returns

```text
False
```

then the number is definitely composite.

If it returns

```text
True
```

the correct interpretation is:

```text
the candidate passed all tested Miller-Rabin rounds
```

or, more compactly,

```text
probable prime
```

—not:

```text
mathematically proven prime
```

That distinction is part of the algorithm.

### One round conceptually

For each chosen base $a$:

1. write
   $$
   n-1=2^s d
   $$
   with $d$ odd;

2. compute
   $$
   x=a^d\bmod n;
   $$

3. accept the round immediately if
   $$
   x=1
   $$
   or
   $$
   x=n-1;
   $$

4. otherwise repeatedly square $x$;

5. if one of those squarings produces
   $$
   n-1,
   $$
   the round passes;

6. if not, $a$ is a witness that $n$ is composite.

So Miller-Rabin does not merely ask whether the final Fermat equation holds.

It inspects the route toward that final value.

---

## How much confidence do repeated rounds give us?

For any fixed odd composite integer $n$, at most one quarter of the possible Miller-Rabin bases are strong liars.

Therefore, if bases are selected independently and appropriately, the probability that the same fixed composite survives $k$ independent rounds is bounded by

$$
\left(\frac14\right)^k.
$$

For example:

$$
k=1
\quad\Rightarrow\quad
\le\frac14,
$$

$$
k=8
\quad\Rightarrow\quad
\le2^{-16},
$$

and

$$
k=16
\quad\Rightarrow\quad
\le2^{-32}.
$$

But the wording matters.

The statement

$$
\Pr[
\text{a fixed composite survives }k\text{ rounds}
]
\le4^{-k}
$$

is **not automatically the same statement** as

$$
\Pr[
n\text{ is composite}
\mid
n\text{ survived }k\text{ rounds}
].
$$

Those are different conditional probabilities.

The second quantity also depends on how candidate integers were generated and on the prior distribution of primes and composites in that candidate population.

For ordinary learning, the $4^{-k}$ bound is the important algorithmic result.

For cryptographic key generation and standards, the probability analysis is handled more carefully.

---

## Standards and research connection

Miller-Rabin is not merely a textbook algorithm.

### NIST and RSA prime generation

**NIST FIPS 186-5**, the Digital Signature Standard, includes probabilistic primality testing as part of RSA prime generation.

Its procedures use Miller-Rabin testing and specify how primality testing fits into the larger process of generating acceptable RSA primes.

This is a useful reminder that generating an RSA key is not simply:

```text
pick a large odd number
        ↓
run one prime test
        ↓
done
```

Prime generation is an engineering pipeline containing candidate generation, filtering, probabilistic testing, and additional RSA-specific requirements.

### Miller and Rabin

The historical development is also interesting.

**Gary L. Miller**, in 1976, gave a deterministic polynomial-time primality test under an unproven number-theoretic assumption.

**Michael O. Rabin**, in 1980, transformed the central idea into the unconditional probabilistic algorithm that became the practical Miller-Rabin test.

A classic reference is:

**Michael O. Rabin**,  
*Probabilistic Algorithm for Testing Primality*,  
Journal of Number Theory, 12(1), 1980.

This is a good example of an algorithm that deliberately exchanges absolute deterministic certainty in one execution for extraordinary practical efficiency and a controllably tiny error probability.

---

## Primality testing is not factorization

There is another distinction worth making explicit.

Testing whether

$$
n
$$

is prime is not the same computational problem as factoring

$$
n.
$$

Miller-Rabin may quickly tell us:

```text
composite
```

without revealing any useful factor.

For example, a Miller-Rabin witness can prove that $561$ is composite without directly handing us

$$
561=3\cdot11\cdot17.
$$

This distinction matters enormously in cryptography.

RSA relies on the presumed difficulty of factoring a carefully generated composite modulus

$$
N=pq.
$$

It does **not** rely on primality testing being difficult.

In fact, primality testing is known to be solvable in deterministic polynomial time.

The AKS result established that

$$
\boxed{
\mathrm{PRIMES}\in\mathbf P.
}
$$

That does not imply that integer factorization is known to be efficiently solvable on classical computers.

So we should keep the two problems separate:

```text
PRIMALITY TESTING

"Is n prime?"
```

versus:

```text
INTEGER FACTORIZATION

"If n is composite,
what are its factors?"
```

They live close together in elementary number theory but have very different roles in cryptography.

---

## A small experiment

A useful experiment is to compare three levels of primality testing:

```text
trial division
      ↓
Fermat test
      ↓
Miller-Rabin
```

Try the following values:

```text
17
19
21
341
561
1105
1729
```

For each number, record:

| Value | Actual status | Fermat base 2 | Miller-Rabin base 2 |
| ---: | --- | --- | --- |
| $17$ | prime | ? | ? |
| $19$ | prime | ? | ? |
| $21$ | composite | ? | ? |
| $341$ | composite | ? | ? |
| $561$ | composite | ? | ? |
| $1105$ | composite | ? | ? |
| $1729$ | composite | ? | ? |

For these tiny educational examples, you may also factor the composites separately so that you know the ground truth.

Especially inspect $561$.

The purpose is not to memorize lists of pseudoprimes or Carmichael numbers.

The point is to see that each stronger test examines more mathematical structure.

### Reader checkpoint

You should now be able to explain:

1. Why trial division only needs to test up to $\sqrt n$.
2. Why that still becomes infeasible for cryptographic-size integers.
3. What Fermat's little theorem guarantees for primes.
4. Why passing a Fermat test does not prove primality.
5. What a pseudoprime is.
6. Why Carmichael numbers are particularly troublesome for naive Fermat testing.
7. Why Miller-Rabin writes
   $$
   n-1=2^s d.
   $$
8. Why nontrivial square roots of $1$ reveal compositeness.
9. Why `False` means definitely composite while `True` means probable prime in our randomized implementation.
10. Why primality testing and integer factorization are different computational problems.

If those distinctions are clear, then the algorithm is much easier to remember than if we treat Miller-Rabin as a block of mysterious code.

---

## Where we are going

We now know how to take a large candidate integer and test whether it behaves like a prime with extremely high confidence.

That finally allows us to ask the RSA question properly:

> How do we actually generate the primes used inside an RSA key?

Not merely:

```text
pick p
pick q
multiply them
```

but:

- How large should $p$ and $q$ be?
- How are prime candidates sampled?
- Why are candidates usually forced to be odd?
- Which primality tests are applied?
- What restrictions should hold relative to the public exponent $e$?
- How do we construct the private exponent $d$?
- Why do implementations store CRT parameters?
- What happens if randomness fails?
- What happens if two independent RSA keys accidentally share a prime?

At that point all of the pieces we have built separately begin to meet:

$$
\text{randomness}
\rightarrow
\text{prime generation}
\rightarrow
\gcd
\rightarrow
\text{modular inverse}
\rightarrow
\text{RSA modulus}
\rightarrow
\text{private exponent}.
$$

That takes us from primality testing to **RSA key generation itself**.

**Next: RSA Key Generation From Zero — Choosing $p$, $q$, $e$, and Building the Private Exponent.**