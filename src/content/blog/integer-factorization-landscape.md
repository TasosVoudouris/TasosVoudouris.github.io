---
title: "Computational Number Theory VII: Integer Factorization from Fermat and Pollard to ECM, QS, and NFS"
description: "A computational map of classical integer-factorization algorithms, the structure each method exploits, and the transition from special-purpose techniques to subexponential general-purpose factorization."
pubDate: "2025-05-07"
updatedDate: "2026-09-16"
topics:
  - "Mathematical Foundations"
  - "Number Theory"
  - "Cryptanalysis"
tags:
  - "integer-factorization"
  - "fermat-factorization"
  - "pollard-rho"
  - "pollard-p-1"
  - "ecm"
  - "quadratic-sieve"
  - "number-field-sieve"
difficulty: "Advanced"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 7
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

Integer factorization asks for the decomposition:

\[
\boxed{
N
=
p_1^{e_1}\cdots p_r^{e_r}
}
\]

of a positive integer into primes.

The statement of the problem is simple.

Its computational behavior is not.

Different algorithms succeed for completely different reasons.

Some exploit the geometry of the factors:

\[
p\approx q.
\]

Some exploit arithmetic structure:

\[
p-1
\text{ is smooth}.
\]

Some replace the multiplicative group with randomly selected elliptic-curve groups.

And the strongest general-purpose classical algorithms construct enormous collections of smooth relations and solve sparse linear-algebra problems.

So integer factorization should not be understood as one algorithmic problem with one algorithm.

It is a landscape:

\[
\boxed{
\text{factor structure}
\rightarrow
\text{algorithm choice}
\rightarrow
\text{different complexity regime}.
}
\]

A useful high-level distinction is:

\[
\boxed{
\text{special-purpose factorization}
}
\]

versus:

\[
\boxed{
\text{general-purpose factorization}.
}
\]

The first category becomes powerful when an unknown factor has exploitable structure.

The second is designed for large integers without assuming such structure.

---

## Table of Contents

- [Factorization as a computational problem](#factorization-as-a-computational-problem)
- [Fermat factorization and close factors](#fermat-factorization-and-close-factors)
- [Pollard rho and Pollard p minus 1](#pollard-rho-and-pollard-p-minus-1)
- [The Elliptic Curve Method](#the-elliptic-curve-method)
- [The Quadratic Sieve](#the-quadratic-sieve)
- [The Number Field Sieve](#the-number-field-sieve)
- [Choosing the right factorization regime](#choosing-the-right-factorization-regime)
- [Why CryptoCave keeps separate factorization articles](#why-cryptocave-keeps-separate-factorization-articles)
- [The structural picture](#the-structural-picture)
- [Practice and checkpoint](#practice-and-checkpoint)
- [References and further reading](#references-and-further-reading)
- [Closing the Computational Number Theory Series](#closing-the-computational-number-theory-series)

---

## Factorization as a computational problem

Suppose:

\[
N>1
\]

is composite.

The computational goal is to find a nontrivial divisor:

\[
\boxed{
1<d<N.
}
\]

Once one factor is found:

\[
N=dm,
\]

the process can be applied recursively to:

\[
d
\]

and:

\[
m
\]

until the complete prime factorization is obtained.

---

### Input size matters

If \(N\) is represented in binary, its input length is approximately:

\[
\boxed{
n=\log_2N.
}
\]

Therefore an algorithm requiring:

\[
O(\sqrt N)
\]

operations is not polynomial-time in the input length.

Since:

\[
\sqrt N
=
2^{n/2},
\]

such an algorithm is exponential in \(n\).

This distinction is fundamental.

Whenever computational-number-theory algorithms are compared, complexity should be interpreted in terms of:

\[
\boxed{
\log N,
}
\]

not \(N\) itself.

---

### Trial division

The most direct factorization algorithm tests potential divisors:

\[
2,3,5,\ldots
\]

up to:

\[
\sqrt N.
\]

If \(N\) has no factor below \(\sqrt N\), then \(N\) is prime.

For small integers this is perfectly reasonable.

For large integers the cost becomes prohibitive.

The conceptual lesson is nevertheless important:

\[
\boxed{
\text{a composite integer has a factor }\le\sqrt N.
}
\]

Most advanced factoring algorithms succeed by avoiding explicit enumeration of all such candidates.

---

### Remove trivial structure first

Practical factorization pipelines usually begin with cheap preprocessing:

- remove powers of small primes;
- detect perfect powers;
- run primality or probable-prime tests;
- then invoke increasingly expensive factorization methods.

This prevents a sophisticated algorithm from wasting effort on structure that could have been detected almost immediately.

---

### Factorization is not primality testing

Primality testing asks:

\[
\boxed{
\text{Is }N\text{ prime?}
}
\]

Factorization asks:

\[
\boxed{
\text{What are its prime factors?}
}
\]

These are different computational problems.

Deterministic polynomial-time primality testing is known.

No polynomial-time classical algorithm is known for general integer factorization.

So:

\[
\boxed{
\text{primality testing}
\neq
\text{integer factorization}.
}
\]

---

## Fermat factorization and close factors

Fermat's factorization method begins with the identity:

\[
\boxed{
a^2-b^2
=
(a-b)(a+b).
}
\]

Suppose:

\[
N=pq
\]

with odd factors:

\[
p\le q.
\]

Then:

\[
p=a-b,
\]

\[
q=a+b.
\]

Adding:

\[
p+q=2a,
\]

so:

\[
\boxed{
a=\frac{p+q}{2}.
}
\]

Similarly:

\[
\boxed{
b=\frac{q-p}{2}.
}
\]

Therefore:

\[
\boxed{
N=a^2-b^2.
}
\]

---

### The algorithm

Start at:

\[
a=\lceil\sqrt N\rceil.
\]

Compute:

\[
b^2=a^2-N.
\]

If:

\[
a^2-N
\]

is a perfect square, then:

\[
\boxed{
N=(a-b)(a+b).
}
\]

Otherwise increment:

\[
a\leftarrow a+1
\]

and repeat.

---

### Example

Take:

\[
N=5959.
\]

We have:

\[
\sqrt{5959}\approx77.19.
\]

Start:

\[
a=78.
\]

Then:

\[
78^2-5959
=
6084-5959
=
125,
\]

not a square.

Try:

\[
a=79.
\]

Then:

\[
79^2-5959
=
6241-5959
=
282.
\]

Continue.

Eventually:

\[
a=80
\]

gives:

\[
80^2-5959
=
6400-5959
=
441
=
21^2.
\]

Therefore:

\[
5959
=
(80-21)(80+21).
\]

Hence:

\[
\boxed{
5959=59\cdot101.
}
\]

The factors are relatively close:

\[
101-59=42.
\]

---

### Why close factors help

Recall:

\[
a
=
\frac{p+q}{2}.
\]

Compare this with:

\[
\sqrt{N}
=
\sqrt{pq}.
\]

Their difference is:

\[
\frac{p+q}{2}-\sqrt{pq}.
\]

Writing:

\[
p=u^2,
\qquad
q=v^2
\]

formally at the real-number level gives:

\[
\frac{p+q}{2}-\sqrt{pq}
=
\frac{(\sqrt q-\sqrt p)^2}{2}.
\]

Therefore if \(p\) and \(q\) are close, the correct \(a\) lies close to:

\[
\sqrt N.
\]

That is exactly the regime in which Fermat's search becomes effective.

So Fermat factorization is fundamentally a:

\[
\boxed{
\text{close-factor algorithm}.
}
\]

It is not a competitive general-purpose factorizer.

---

### Minimal implementation

```python
from math import isqrt


def fermat_factor(n: int):
    if n <= 0:
        raise ValueError(
            "n must be positive"
        )

    if n % 2 == 0:
        return 2, n // 2

    a = isqrt(n)

    if a * a < n:
        a += 1

    while True:
        b2 = a * a - n
        b = isqrt(b2)

        if b * b == b2:
            return (
                a - b,
                a + b,
            )

        a += 1
```

For:

```python
print(
    fermat_factor(5959)
)
```

we obtain:

```text
(59, 101)
```

---

## Pollard rho and Pollard p minus 1

Pollard introduced two very different factorization ideas.

Their names are similar.

Their mathematical mechanisms are not.

---

### Pollard rho

Suppose:

\[
p\mid N
\]

is an unknown prime factor.

Choose an iteration such as:

\[
\boxed{
x_{k+1}
=
f(x_k)
\bmod N,
}
\]

commonly with:

\[
f(x)=x^2+c.
\]

Although the computation is performed modulo \(N\), we can conceptually reduce the sequence modulo the unknown factor \(p\).

Modulo \(p\), the sequence behaves approximately like a pseudorandom walk on:

\[
\mathbb Z/p\mathbb Z.
\]

---

### The birthday phenomenon

After roughly:

\[
\sqrt p
\]

pseudorandom samples, collisions become plausible.

Suppose:

\[
x_i
\equiv
x_j
\pmod p.
\]

Then:

\[
p
\mid
x_i-x_j.
\]

Therefore:

\[
\gcd(
x_i-x_j,
N
)
\]

contains \(p\).

If the difference is not also divisible by every factor of \(N\), the gcd reveals a proper divisor:

\[
\boxed{
1<
\gcd(
x_i-x_j,
N
)
<N.
}
\]

---

### Why the name rho?

The sequence eventually enters a cycle.

Its graph resembles the Greek letter:

\[
\rho.
\]

Cycle-detection algorithms such as Floyd's method allow collisions to be detected using constant memory.

Brent-style variants often improve practical performance.

---

### Basic rho implementation

```python
from math import gcd


def pollard_rho(
    n: int,
    x0: int = 2,
    c: int = 1,
):
    if n % 2 == 0:
        return 2

    def f(x):
        return (
            x * x + c
        ) % n

    x = x0
    y = x0
    d = 1

    while d == 1:
        x = f(x)
        y = f(f(y))

        d = gcd(
            abs(x - y),
            n,
        )

    if d == n:
        return None

    return d
```

This is educational code rather than a high-performance factorizer.

---

### Expected regime

For an unknown prime factor \(p\), the heuristic birthday-scale work is roughly:

\[
\boxed{
O(\sqrt p)
}
\]

modular iterations.

So Pollard rho is especially useful for finding relatively small prime factors.

The relevant size is primarily the size of the factor being discovered, not merely the total size of \(N\).

---

### Pollard \(p-1\)

Pollard's \(p-1\) method exploits an entirely different property.

Suppose:

\[
p\mid N
\]

and:

\[
p-1
\]

factors entirely into small prime powers.

We say that:

\[
p-1
\]

is **smooth**.

---

### Smoothness

An integer is \(B\)-smooth if all its prime factors are at most:

\[
B.
\]

For example:

\[
2^5\cdot3^2\cdot5
\]

is \(5\)-smooth.

Suppose:

\[
p-1
\]

is \(B\)-smooth.

Choose an exponent \(M\) divisible by all sufficiently large prime powers up to \(B\), for example conceptually:

\[
\boxed{
M
=
\operatorname{lcm}(1,2,\ldots,B).
}
\]

Then:

\[
p-1\mid M.
\]

---

### Fermat's theorem exposes the factor

If:

\[
\gcd(a,p)=1,
\]

then:

\[
a^{p-1}
\equiv1
\pmod p.
\]

Since:

\[
p-1\mid M,
\]

we obtain:

\[
a^M
\equiv1
\pmod p.
\]

Therefore:

\[
p
\mid
a^M-1.
\]

So:

\[
\boxed{
\gcd(
a^M-1,
N
)
}
\]

may reveal \(p\).

---

### What \(p-1\) actually exploits

Fermat factorization asks:

\[
\boxed{
\text{Are }p\text{ and }q\text{ close?}
}
\]

Pollard \(p-1\) asks:

\[
\boxed{
\text{Is }p-1\text{ smooth?}
}
\]

Pollard rho asks neither.

It relies on collision search.

This illustrates why "factorization algorithm" is too broad a description to explain expected performance.

The hidden structure matters.

---

## The Elliptic Curve Method

Lenstra's **Elliptic Curve Method (ECM)** can be viewed as a conceptual generalization of Pollard \(p-1\).

Pollard \(p-1\) works inside:

\[
\mathbb F_p^\times,
\]

whose order is fixed:

\[
p-1.
\]

If that particular group order is not smooth, the method fails.

ECM replaces this one group with many possible elliptic-curve groups.

---

### Reduction modulo an unknown factor

Suppose:

\[
p\mid N.
\]

Choose an elliptic curve:

\[
E
\]

and a point:

\[
P.
\]

The arithmetic is carried out modulo \(N\), but conceptually the computation can be reduced modulo each unknown prime factor.

Modulo \(p\), we obtain:

\[
E(\mathbb F_p).
\]

Its group order is:

\[
\#E(\mathbb F_p).
\]

Hasse's theorem gives:

\[
\boxed{
p+1-2\sqrt p
\le
\#E(\mathbb F_p)
\le
p+1+2\sqrt p.
}
\]

---

### The crucial difference from Pollard \(p-1\)

Pollard \(p-1\) receives exactly one candidate group order:

\[
p-1.
\]

ECM can select many random curves.

Each curve produces a potentially different group order:

\[
\#E(\mathbb F_p).
\]

So even if one curve order is not smooth, another might be.

This gives repeated independent-looking opportunities to encounter favorable smoothness.

Schematically:

\[
\boxed{
p-1
\quad\longrightarrow\quad
\#E_1(\mathbb F_p),
\#E_2(\mathbb F_p),
\ldots
}
\]

---

### How a factor becomes visible

Elliptic-curve addition requires arithmetic modulo \(N\).

In affine formulations, this includes denominator inversion.

Suppose a required denominator:

\[
d
\]

is not invertible modulo \(N\).

Then:

\[
\gcd(d,N)
\neq1.
\]

If:

\[
1<
\gcd(d,N)
<N,
\]

we have discovered a factor.

Practical ECM implementations use more sophisticated coordinate systems and arithmetic, but the underlying principle remains:

\[
\boxed{
\text{arithmetic succeeds modulo one factor and degenerates modulo another}.
}
\]

That mismatch exposes a gcd with \(N\).

---

### What determines ECM performance?

ECM is primarily sensitive to the size of the prime factor:

\[
p
\]

that we are trying to discover.

It is much less sensitive to the total size of the composite cofactor.

This makes ECM particularly useful when:

\[
N
\]

is enormous but contains a factor of moderate size.

Heuristically, its expected running-time scale for finding a factor \(p\) is often written:

\[
\boxed{
L_p
\left[
\frac12,
\sqrt2
\right].
}
\]

Thus ECM occupies a distinct algorithmic regime between small-factor methods and large general-purpose factorization.

---

## The Quadratic Sieve

The **Quadratic Sieve (QS)** changes strategy completely.

Instead of searching directly for a factor, it tries to construct a nontrivial congruence of squares:

\[
\boxed{
X^2
\equiv
Y^2
\pmod N.
}
\]

Then:

\[
N
\mid
(X-Y)(X+Y).
\]

If:

\[
X
\not\equiv
\pm Y
\pmod N,
\]

then:

\[
\boxed{
\gcd(X-Y,N)
}
\]

or:

\[
\boxed{
\gcd(X+Y,N)
}
\]

can reveal a nontrivial factor.

---

### Where the square congruence comes from

Take values:

\[
x
\]

close to:

\[
\sqrt N
\]

and compute:

\[
\boxed{
Q(x)=x^2-N.
}
\]

Then:

\[
x^2
\equiv
Q(x)
\pmod N.
\]

Now search for \(Q(x)\) values that factor completely over a small set of primes called the **factor base**.

Such values are called smooth.

---

### Smooth relations

Suppose:

\[
Q(x_i)
=
\prod_{j=1}^{k}
p_j^{e_{ij}}.
\]

For square construction, only exponent parity matters.

Associate the vector:

\[
\boxed{
(
e_{i1},
\ldots,
e_{ik}
)
\bmod2
}
\]

to every relation.

These vectors live in:

\[
\mathbb F_2^k.
\]

Once enough relations have been collected, linear algebra guarantees a dependency:

\[
\sum_i
\mathbf e_i
=
0
\pmod2.
\]

That means the product:

\[
\prod_iQ(x_i)
\]

has every prime exponent even.

Therefore it is a square:

\[
\boxed{
\prod_iQ(x_i)
=
Y^2.
}
\]

Meanwhile:

\[
\left(
\prod_i x_i
\right)^2
\equiv
\prod_iQ(x_i)
\pmod N.
\]

Setting:

\[
X=\prod_i x_i,
\]

we obtain:

\[
\boxed{
X^2\equiv Y^2\pmod N.
}
\]

---

### The real architecture of QS

Quadratic Sieve is therefore not simply a "sieving trick".

Its structure is:

\[
\boxed{
\text{smoothness search}
\rightarrow
\text{relation collection}
\rightarrow
\text{linear algebra over }\mathbb F_2
\rightarrow
\text{congruence of squares}
\rightarrow
\gcd.
}
\]

This architecture will reappear in the Number Field Sieve.

---

### Complexity

The heuristic complexity of QS is commonly expressed as:

\[
\boxed{
L_N
\left[
\frac12,
1
\right].
}
\]

Here:

\[
\boxed{
L_N[\alpha,c]
=
\exp
\left(
(c+o(1))
(\log N)^\alpha
(\log\log N)^{1-\alpha}
\right).
}
\]

For:

\[
0<\alpha<1,
\]

this is **subexponential** in \(\log N\).

It is faster asymptotically than algorithms exponential in the bit length, but slower than polynomial time.

---

## The Number Field Sieve

The **General Number Field Sieve (GNFS)** is the major general-purpose classical algorithm for factoring sufficiently large integers.

Its basic objective is still familiar:

\[
\boxed{
X^2\equiv Y^2\pmod N.
}
\]

But it constructs the required square relation using arithmetic simultaneously in:

\[
\mathbb Z
\]

and in an algebraic number field.

---

### From integers to number fields

Choose a polynomial:

\[
f(x)\in\mathbb Z[x]
\]

and an integer:

\[
m
\]

such that:

\[
\boxed{
f(m)\equiv0\pmod N.
}
\]

Let:

\[
\alpha
\]

be a formal root of:

\[
f.
\]

Then computations are performed on two related sides:

\[
a-bm
\]

in the rational/integer side, and:

\[
a-b\alpha
\]

in the algebraic number-field side.

The polynomial relation eventually allows information from both sides to be mapped back modulo \(N\).

---

### Relation collection

As in QS, the algorithm searches for smooth values.

But now smoothness is required simultaneously in two different arithmetic settings.

Very roughly:

\[
\boxed{
\text{rational smoothness}
}
\]

and:

\[
\boxed{
\text{algebraic smoothness}.
}
\]

Successful pairs:

\[
(a,b)
\]

generate relations.

Large-scale sieving is used to find huge numbers of these relations efficiently.

---

### Sparse linear algebra

The accumulated relation exponent vectors are again reduced modulo \(2\).

One searches for dependencies in a huge sparse matrix over:

\[
\mathbb F_2.
\]

This produces products that are squares on both sides.

So the architecture remains:

\[
\boxed{
\text{sieving}
\rightarrow
\text{relations}
\rightarrow
\text{linear algebra}
\rightarrow
\text{square construction}.
}
\]

---

### Square root step

After a dependency is found, the algorithm constructs corresponding square roots:

\[
X
\]

and:

\[
Y
\]

such that:

\[
\boxed{
X^2
\equiv
Y^2
\pmod N.
}
\]

Then:

\[
\gcd(X-Y,N)
\]

is tested.

If necessary, other dependencies are tried.

---

### GNFS complexity

The heuristic asymptotic complexity is:

\[
\boxed{
L_N
\left[
\frac13,
\left(
\frac{64}{9}
\right)^{1/3}
\right].
}
\]

That is:

\[
\boxed{
\exp
\left(
\left(
\left(
\frac{64}{9}
\right)^{1/3}
+o(1)
\right)
(\log N)^{1/3}
(\log\log N)^{2/3}
\right).
}
\]

The important structural comparison is:

\[
\boxed{
L_N[1/3,c]
}
\]

versus the Quadratic Sieve's:

\[
\boxed{
L_N[1/2,1].
}
\]

As \(N\) becomes sufficiently large, the smaller exponent:

\[
\frac13
\]

wins asymptotically.

---

### General versus special NFS

The word **general** matters.

Some integers have special algebraic forms that admit better polynomial selection.

For these, the **Special Number Field Sieve (SNFS)** can be faster.

So the proper statement is:

\[
\boxed{
\text{GNFS is the principal asymptotically fastest known classical method for large general integers}.
}
\]

Special-form integers may admit more favorable algorithms.

---

### NFS is much more than one formula

The \(L\)-notation complexity can make NFS look deceptively simple.

Real implementations require sophisticated engineering in:

- polynomial selection;
- factor-base construction;
- lattice or line sieving;
- large-prime variants;
- relation filtering;
- sparse linear algebra;
- algebraic square-root computation.

So:

\[
\boxed{
L_N[1/3,c]
}
\]

describes asymptotic behavior.

It does not communicate the full complexity of implementing NFS.

---

## Choosing the right factorization regime

The factorization algorithms in this article should not be ranked as though one simply replaces another.

They solve different structural regimes.

| Method | Main structure exploited | Cost depends mainly on | Typical role |
| --- | --- | --- | --- |
| Trial division | very small factor | factor size | preprocessing |
| Fermat | factors close together | factor separation | structured composites |
| Pollard rho | birthday collision modulo \(p\) | smallest factor \(p\) | small factors |
| Pollard \(p-1\) | smooth \(p-1\) | smoothness bound | special factors |
| ECM | smooth random \(\#E(\mathbb F_p)\) | factor size \(p\) | medium-size factors |
| QS | smooth values near \(\sqrt N\) | size of \(N\) | general medium/large integers |
| GNFS | rational + algebraic smoothness | size of \(N\) | very large general integers |

The choice therefore depends on what is known or suspected about:

\[
N.
\]

---

### Special-purpose versus general-purpose

A useful classification is:

\[
\boxed{
\text{special-purpose}
}
\]

for methods whose success depends strongly on some property of an unknown factor, such as:

\[
p\approx q,
\]

\[
p-1\text{ smooth},
\]

or:

\[
p\text{ moderately sized}.
\]

By contrast:

\[
\boxed{
\text{general-purpose}
}
\]

methods such as QS and GNFS are designed primarily around the overall size of:

\[
N.
\]

---

### Smoothness is the recurring hidden variable

Pollard \(p-1\) uses smoothness of:

\[
p-1.
\]

ECM uses smoothness of:

\[
\#E(\mathbb F_p).
\]

QS searches for smooth values of:

\[
x^2-N.
\]

NFS searches for simultaneous smoothness in rational and algebraic norms.

So an enormous part of classical factorization can be summarized by one recurring question:

\[
\boxed{
\text{Can we manufacture enough smooth arithmetic objects?}
}
\]

That is one of the deepest computational themes connecting these apparently different algorithms.

---

### Congruences of squares are the other recurring theme

Fermat begins directly with:

\[
N=a^2-b^2.
\]

QS constructs:

\[
X^2\equiv Y^2\pmod N.
\]

NFS constructs the same type of congruence through a far more sophisticated algebraic route.

Thus another major progression is:

\[
\boxed{
\text{Fermat}
\rightarrow
\text{QS}
\rightarrow
\text{NFS}
}
\]

as increasingly sophisticated ways of producing useful square relations.

---

### Factorization and classical cryptography

Integer factorization became especially prominent in cryptography because certain public-key constructions use a modulus:

\[
N=pq
\]

while keeping:

\[
p,q
\]

secret.

The relevant security question is not simply whether a mathematical factorization exists.

It always does.

The question is the computational cost of recovering it from:

\[
N
\]

alone.

That cost depends on:

- the size of \(N\);
- the sizes of its factors;
- any special structure in those factors;
- the available algorithms;
- the computational model.

This is why secure parameter generation must avoid accidentally introducing structure favorable to specialized algorithms.

---

### Classical versus quantum factorization

Everything above concerns **classical** algorithms.

In the quantum computational model, Shor's algorithm gives polynomial-time algorithms for integer factorization and discrete logarithms on an ideal fault-tolerant quantum computer.

Thus:

\[
\boxed{
\text{classical hardness}
}
\]

and:

\[
\boxed{
\text{quantum hardness}
}
\]

are different questions.

The existence of Shor's algorithm is one of the central motivations for post-quantum cryptography.

But it does not change the classical algorithmic taxonomy developed here.

---

## Why CryptoCave keeps separate factorization articles

Factorization can be studied from at least two distinct perspectives.

This article asks:

\[
\boxed{
\text{What are the mathematical and algorithmic regimes of integer factorization?}
}
\]

Its focus is computational number theory.

A security-oriented RSA article instead asks questions such as:

\[
\boxed{
\text{What key-generation choices accidentally create exploitable structure?}
}
\]

That changes the emphasis toward:

- parameter generation;
- structural weaknesses;
- implementation assumptions;
- concrete security consequences.

Keeping the two viewpoints separate is useful.

The same algorithm can therefore appear twice for different reasons without the two articles becoming duplicates.

---

## The structural picture

The factorization landscape can be organized around the property being exploited.

Fermat uses:

\[
\boxed{
p\approx q.
}
\]

Pollard rho uses:

\[
\boxed{
\text{collisions modulo }p.
}
\]

Pollard \(p-1\) uses:

\[
\boxed{
p-1\text{ smooth}.
}
\]

ECM replaces one fixed group order with random elliptic-curve group orders:

\[
\boxed{
\#E(\mathbb F_p).
}
\]

Quadratic Sieve seeks:

\[
\boxed{
\text{smooth quadratic residues}
}
\]

and turns them into:

\[
X^2\equiv Y^2\pmod N.
\]

Number Field Sieve expands the same relation-building philosophy into:

\[
\boxed{
\text{algebraic number fields}.
}
\]

So the progression is:

\[
\boxed{
\text{factor geometry}
\rightarrow
\text{group structure}
\rightarrow
\text{smoothness}
\rightarrow
\text{sieving}
\rightarrow
\text{linear algebra}
\rightarrow
\text{algebraic number fields}.
}
\]

A remarkably broad collection of algorithms ultimately reduces to a small set of recurring ideas:

\[
\boxed{
\gcd,
\quad
\text{smoothness},
\quad
\text{collisions},
\quad
\text{relations},
\quad
\text{linear algebra}.
}
\]

---

## Practice and checkpoint

### Exercise 1 — Complexity and input size

Suppose:

\[
N
\]

has:

\[
n
\]

bits.

Show that:

\[
O(\sqrt N)
\]

operations corresponds to approximately:

\[
O(2^{n/2})
\]

operations.

Why is this exponential in the input length?

---

### Exercise 2 — Fermat factorization

Use Fermat's method to factor:

\[
5959.
\]

Start from:

\[
\lceil\sqrt{5959}\rceil.
\]

Find:

\[
a^2-N=b^2.
\]

---

### Exercise 3 — Close factors

Suppose:

\[
N=pq
\]

with \(p<q\).

Show:

\[
a-\sqrt N
=
\frac{
(\sqrt q-\sqrt p)^2
}{2},
\]

where:

\[
a=\frac{p+q}{2}.
\]

Explain why this determines Fermat's useful regime.

---

### Exercise 4 — Pollard rho collision

Suppose:

\[
p\mid N
\]

and:

\[
x_i\equiv x_j\pmod p.
\]

Show:

\[
p
\mid
x_i-x_j.
\]

Why can:

\[
\gcd(x_i-x_j,N)
\]

reveal \(p\)?

---

### Exercise 5 — Birthday scale

Why should a pseudorandom walk modulo a prime \(p\) begin producing collisions on a scale of approximately:

\[
\sqrt p?
\]

Relate this to the birthday paradox.

---

### Exercise 6 — Pollard \(p-1\)

Suppose:

\[
p-1
\mid M.
\]

Use Fermat's theorem to show:

\[
a^M\equiv1\pmod p
\]

when:

\[
p\nmid a.
\]

Explain why:

\[
\gcd(a^M-1,N)
\]

may expose \(p\).

---

### Exercise 7 — ECM intuition

Explain why replacing:

\[
\mathbb F_p^\times
\]

with many groups:

\[
E(\mathbb F_p)
\]

gives ECM more chances to encounter a smooth group order than Pollard \(p-1\).

---

### Exercise 8 — Congruence of squares

Suppose:

\[
X^2\equiv Y^2\pmod N.
\]

Show:

\[
N
\mid
(X-Y)(X+Y).
\]

Why is the condition:

\[
X\not\equiv\pm Y\pmod N
\]

important?

---

### Exercise 9 — QS exponent vectors

Suppose a factor base is:

\[
\{2,3,5,7\}.
\]

Represent:

\[
2^3\cdot3^2\cdot5\cdot7^4
\]

by its exponent-parity vector over:

\[
\mathbb F_2.
\]

Why do linear dependencies among such vectors create squares?

---

### Exercise 10 — L-notation

Compare:

\[
L_N[1/2,1]
\]

with:

\[
L_N[1/3,c].
\]

Why does the latter eventually dominate asymptotically as \(N\) grows?

---

### Exercise 11 — Algorithm selection

For each situation, identify the structural feature suggesting a useful algorithm:

1. \(N=pq\) and \(p,q\) are extremely close.
2. One unknown factor \(p\) has very smooth \(p-1\).
3. \(N\) contains a moderately sized factor while the cofactor is enormous.
4. No useful structure is known and \(N\) is a large general integer.

Explain your reasoning in terms of the underlying mathematics rather than merely naming algorithms.

---

### Exercise 12 — Smoothness across algorithms

Explain the role of smoothness in:

\[
\text{Pollard }p-1,
\]

\[
\text{ECM},
\]

\[
\text{QS},
\]

and:

\[
\text{NFS}.
\]

What object is required to be smooth in each case?

---

### Reader checkpoint

You should now be able to explain:

1. Why factorization complexity must be measured against:
   \[
   \log N.
   \]
2. Why primality testing and factorization are different computational problems.
3. What structure Fermat factorization exploits.
4. Why close factors make Fermat effective.
5. How Pollard rho converts collisions modulo an unknown factor into a gcd.
6. Why the birthday phenomenon gives a:
   \[
   \sqrt p
   \]
   scale.
7. What \(B\)-smoothness means.
8. Why Pollard \(p-1\) succeeds when:
   \[
   p-1
   \]
   has favorable smoothness.
9. Why ECM can be regarded conceptually as a group-order generalization of Pollard \(p-1\).
10. Why ECM depends strongly on the size of the factor being found.
11. How failed modular inversion can expose a factor in elliptic-curve arithmetic modulo a composite.
12. What a congruence of squares is.
13. Why:
    \[
    X^2\equiv Y^2\pmod N
    \]
    can lead to a factor.
14. What a factor base is.
15. Why QS searches for smooth values.
16. Why parity vectors lead naturally to linear algebra over:
    \[
    \mathbb F_2.
    \]
17. Why QS is subexponential.
18. What:
    \[
    L_N[\alpha,c]
    \]
    notation means.
19. Why GNFS introduces an algebraic number field.
20. Why NFS still ultimately constructs a congruence of squares.
21. Why sparse linear algebra is central to large-scale factorization.
22. The difference between GNFS and special-form NFS.
23. Why the fastest algorithm depends on the structure and scale of the input.
24. Why smoothness is a recurring hidden variable throughout classical factorization.
25. Why the computational-number-theory view of factorization should remain distinct from a security-specific RSA analysis.
26. Why classical and quantum factorization belong to different complexity landscapes.

Integer factorization is not a sequence of increasingly clever trial-division algorithms.

Each major method changes the representation of the problem.

That is the deeper progression:

\[
\boxed{
\text{search for divisors}
\rightarrow
\text{search for collisions}
\rightarrow
\text{search for smooth group orders}
\rightarrow
\text{search for smooth relations}
\rightarrow
\text{solve algebraic dependencies}.
}
\]

---

## References and further reading

**Richard Crandall and Carl Pomerance**,  
*Prime Numbers: A Computational Perspective.*

A major reference for primality testing, Pollard methods, ECM, quadratic sieving, and the Number Field Sieve.

**Carl Pomerance**,  
*The Quadratic Sieve Factoring Algorithm.*

A foundational source for the Quadratic Sieve and the smooth-relation viewpoint.

**Hendrik W. Lenstra Jr.**,  
*Factoring Integers with Elliptic Curves.*

The foundational paper introducing the Elliptic Curve Method.

**Arjen K. Lenstra and Hendrik W. Lenstra Jr., editors**,  
*The Development of the Number Field Sieve.*

A foundational collection on the mathematics and development of NFS.

**Peter L. Montgomery**,  
*A Block Lanczos Algorithm for Finding Dependencies over GF(2).*

Important for understanding the sparse linear-algebra stage appearing in large factorization computations.

**Victor Shoup**,  
*A Computational Introduction to Number Theory and Algebra.*

An excellent algorithmic reference for modular arithmetic, factoring methods, smoothness, and computational complexity.

**Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone**,  
*Handbook of Applied Cryptography.*

Useful for the classical cryptographic context of integer factorization and public-key parameter sizes.

---

## Closing the Computational Number Theory Series

This article closes the **Computational Number Theory** series.

The seven articles deliberately moved between arithmetic structure and computation.

We began with arithmetic functions:

\[
\boxed{
\tau,
\quad
\sigma,
\quad
\varphi,
\quad
\mu.
}
\]

Multiplicativity reduced their evaluation to prime powers:

\[
n
=
\prod p_i^{e_i},
\]

while Dirichlet convolution revealed an algebra of arithmetic functions:

\[
\boxed{
\mathbf 1*\mu=\varepsilon.
}
\]

Part II moved from individual integers to the global distribution of primes:

\[
\boxed{
\pi(x)
\sim
\frac{x}{\log x}.
}
\]

This introduced a distinction that remained important throughout the series:

\[
\boxed{
\text{finite computation}
\neq
\text{heuristic}
\neq
\text{asymptotic theorem}.
}
\]

Part III enlarged the integers to:

\[
\boxed{
\mathbb Z[i].
}
\]

There the norm:

\[
N(a+bi)=a^2+b^2
\]

turned nearest-lattice-point geometry into a Euclidean algorithm.

Prime splitting then connected:

\[
p\bmod4,
\]

\[
x^2\equiv-1\pmod p,
\]

\[
p=a^2+b^2,
\]

and factorization inside:

\[
\mathbb Z[i].
\]

Parts IV and V replaced individual residue calculations by characters.

Gauss sums connected:

\[
\boxed{
\text{multiplicative characters}
}
\]

with:

\[
\boxed{
\text{additive Fourier structure}.
}
\]

Jacobi sums then encoded cyclotomic correlations and transformed finite-field equations into point-counting problems:

\[
\boxed{
\text{character sums}
\rightarrow
\text{Frobenius traces}.
}
\]

Part VI returned to integral arithmetic through binary quadratic forms:

\[
ax^2+bxy+cy^2.
\]

Reduction turned infinitely many equivalent forms into finite canonical representatives.

Gauss composition turned those classes into:

\[
\boxed{
\operatorname{Cl}(\Delta),
}
\]

and ideal theory explained why that group exists.

Finally, Part VII returned to factorization itself.

The progression:

\[
\text{Fermat}
\rightarrow
\text{Pollard}
\rightarrow
\text{ECM}
\rightarrow
\text{QS}
\rightarrow
\text{NFS}
\]

showed how increasingly sophisticated mathematical structures are converted into algorithms.

So the complete series can be summarized as:

\[
\boxed{
\text{arithmetic functions}
\rightarrow
\text{prime distribution}
\rightarrow
\text{quadratic extensions}
\rightarrow
\text{characters}
\rightarrow
\text{class groups}
\rightarrow
\text{factorization}.
}
\]

The recurring lesson is that computational number theory is not simply number theory executed faster by a computer.

The algorithm usually appears only after the correct mathematical structure has been exposed.

A multiplicative function becomes efficient after prime-power decomposition.

A Gaussian gcd becomes possible after discovering a Euclidean norm.

Character sums become useful after exploiting orthogonality.

Class-group computation becomes finite after reduction.

Factorization becomes competitive after replacing divisor search by:

\[
\boxed{
\text{smoothness},
\quad
\text{collisions},
\quad
\text{relations},
\quad
\text{linear algebra}.
}
\]

That is the central theme of the series:

\[
\boxed{
\text{structure first}
\rightarrow
\text{algorithm second}.
}
\]
