---
title: "Discrete Logarithms III: Pohlig–Hellman"
description: "A focused treatment of the Pohlig–Hellman algorithm and why smooth group order changes the effective difficulty of the discrete logarithm problem."
pubDate: "2025-05-26"
updatedDate: '2026-09-18'
topics:
  - "Discrete Logarithms"
  - "Cryptanalysis"
  - "Number Theory"
tags:
  - "pohlig-hellman"
  - "smooth-order"
  - "dlp"
  - "crt"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 3
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---

## Table of Contents

- [Why Group Order Matters](#why-group-order-matters)
- [Smooth Numbers and the Real DLP Modulus](#smooth-numbers-and-the-real-dlp-modulus)
- [Prime-Power DLP and Base-$q$ Digit Lifting](#prime-power-dlp-and-base-qqq-digit-lifting)
- [The General Pohlig–Hellman Algorithm](#the-general-pohlighellman-algorithm)
- [Worked Example Modulo 337](#worked-example-modulo-337)
- [Chinese Remainder Reconstruction](#chinese-remainder-reconstruction)
- [Complexity and What “Largest Prime Factor” Really Means](#complexity-and-what-largest-prime-factor-really-means)
- [Pohlig–Hellman on Elliptic-Curve Groups](#pohlighellman-on-elliptic-curve-groups)
- [Executable Implementation](#executable-implementation)
- [Cryptographic Engineering Lessons](#cryptographic-engineering-lessons)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why Group Order Matters

The previous article introduced Baby-Step Giant-Step, a generic algorithm with complexity:

$$
O(\sqrt N)
$$

for a cyclic subgroup of order:

$$
N.
$$

That complexity statement assumes we treat the subgroup as one indivisible object.

Pohlig–Hellman asks a more structural question:

> What if the subgroup order factors into small prime powers?

Suppose:

$$
G=\langle g\rangle
$$

and:

$$
N=\operatorname{ord}(g).
$$

Write the prime-power factorization:

$$
\boxed{
N
=
\prod_{i=1}^{r}
q_i^{e_i}.
}
$$

If the factors:

$$
q_i
$$

are small, then solving one DLP of size $N$ is unnecessary.

Instead, Pohlig–Hellman recovers:

$$
x
\pmod{q_i^{e_i}}
$$

for every prime-power factor and then reconstructs:

$$
x\pmod N
$$

with the Chinese Remainder Theorem.

The key lesson is:

$$
\boxed{
\text{DLP hardness depends strongly on the factorization of the subgroup order.}
}
$$

A large group order can still be weak if it is too smooth.

### The problem we actually solve

Let:

$$
h=g^x.
$$

The discrete logarithm is defined modulo:

$$
N=\operatorname{ord}(g).
$$

So the relevant factorization is the factorization of:

$$
\boxed{
\operatorname{ord}(g),
}
$$

not automatically the size of some larger ambient group.

If $g$ generates all of $G$, then:

$$
\operatorname{ord}(g)=|G|.
$$

If $g$ generates only a proper subgroup, Pohlig–Hellman works with the order of that subgroup.

This distinction is essential in both finite-field and elliptic-curve cryptography.

---

## Smooth Numbers and the Real DLP Modulus

A positive integer $N$ is called **$B$-smooth** if every prime divisor of $N$ is at most $B$.

For example:

$$
2^{10}3^4 5^2
$$

is $5$-smooth.

By contrast:

$$
2^4\cdot 3\cdot 1000003
$$

is not smooth with respect to a small bound because of the large prime factor:

$$
1000003.
$$

### Why smoothness matters

Suppose:

$$
N
=
q_1^{e_1}
q_2^{e_2}
\cdots
q_r^{e_r}.
$$

Pohlig–Hellman transforms:

$$
g^x=h
$$

into separate congruences:

$$
x\equiv x_1\pmod{q_1^{e_1}},
$$

$$
x\equiv x_2\pmod{q_2^{e_2}},
$$

$$
\vdots
$$

$$
x\equiv x_r\pmod{q_r^{e_r}}.
$$

Then CRT reconstructs the unique solution modulo:

$$
N.
$$

The hard work is therefore moved into DLPs associated with the prime divisors $q_i$.

If every $q_i$ is small, the full logarithm can be recovered efficiently.

### What “largest prime factor” means

It is common to summarize Pohlig–Hellman by saying:

> DLP security is controlled by the largest prime factor of the group order.

That is useful intuition, but it should not be interpreted as an exact runtime formula.

The actual cost also depends on:

- the exponents $e_i$;
- the number of prime-power factors;
- the DLP algorithm used inside each order-$q_i$ subgroup;
- group-operation cost;
- factorization availability.

Still, when the inner DLP uses a square-root algorithm, the dominant term is typically associated with the largest prime divisor:

$$
q_{\max}.
$$

That is why cryptographic groups are designed to contain a very large prime-order subgroup.

---

<p align="center">
  <img src="/images/ready/pohlig-hellman/pohlig.PNG" alt="Pohlig–Hellman Illustration">
</p>

---

## Prime-Power DLP and Base-$q$ Digit Lifting

The heart of Pohlig–Hellman is the prime-power case.

Assume:

$$
G=\langle g\rangle
$$

has order:

$$
q^e,
$$

where $q$ is prime.

Given:

$$
h=g^x,
$$

we want:

$$
x\pmod{q^e}.
$$

### Expand the unknown logarithm in base $q$

Every:

$$
0\le x<q^e
$$

has a unique base-$q$ expansion:

$$
\boxed{
x
=
x_0
+
x_1q
+
x_2q^2
+\cdots+
x_{e-1}q^{e-1},
}
$$

where every digit satisfies:

$$
x_j\in\{0,\ldots,q-1\}.
$$

Pohlig–Hellman recovers these digits one at a time.

### A subgroup of order $q$

Because $g$ has order $q^e$, the element:

$$
\gamma
=
g^{q^{e-1}}
$$

has order exactly:

$$
q.
$$

Indeed:

$$
\gamma^q
=
g^{q^e}
=
1,
$$

and no smaller positive exponent annihilates it.

This means each unknown base-$q$ digit can be recovered by solving a tiny DLP in:

$$
\langle\gamma\rangle,
$$

which has only $q$ elements.

### Recover the first digit

Start from:

$$
h=g^x.
$$

Raise both sides to:

$$
q^{e-1}.
$$

Then:

$$
h^{q^{e-1}}
=
g^{xq^{e-1}}.
$$

Substitute:

$$
x
=
x_0+x_1q+\cdots.
$$

Every term involving $q$ beyond $x_0$ contributes an exponent divisible by:

$$
q^e,
$$

so it vanishes modulo the group order.

Therefore:

$$
h^{q^{e-1}}
=
\gamma^{x_0}.
$$

Solve:

$$
\boxed{
\gamma^{x_0}
=
h^{q^{e-1}}
}
$$

inside the order-$q$ subgroup.

That gives the least-significant base-$q$ digit.

### Recover the second digit

Now remove the known contribution:

$$
g^{x_0}.
$$

Compute:

$$
hg^{-x_0}.
$$

Because:

$$
h=g^x,
$$

we have:

$$
hg^{-x_0}
=
g^{x-x_0}.
$$

But:

$$
x-x_0
=
q(x_1+x_2q+\cdots).
$$

Raise this to:

$$
q^{e-2}.
$$

Then:

$$
(hg^{-x_0})^{q^{e-2}}
=
\gamma^{x_1}.
$$

So $x_1$ is again a DLP in the same order-$q$ subgroup.

### General digit step

Suppose we have already recovered:

$$
x^{(j)}
=
x_0+x_1q+\cdots+x_{j-1}q^{j-1}.
$$

Compute the residual:

$$
h g^{-x^{(j)}}.
$$

Then raise it to:

$$
q^{e-1-j}.
$$

The higher unknown digits disappear, leaving:

$$
\boxed{
\left(
h g^{-x^{(j)}}
\right)^{q^{e-1-j}}
=
\gamma^{x_j}.
}
$$

Solve that order-$q$ DLP to recover:

$$
x_j.
$$

Update:

$$
x^{(j+1)}
=
x^{(j)}+x_jq^j.
$$

Repeat until all $e$ digits are known.

### Prime-power pseudocode

```text
Input:
    generator g of order q^e
    target h = g^x

Output:
    x mod q^e

gamma <- g^(q^(e-1))
x <- 0

for j = 0, ..., e-1:

    residual <- h * g^(-x)

    c <- residual^(q^(e-1-j))

    solve gamma^d = c
    for d in {0, ..., q-1}

    x <- x + d*q^j

return x
```

The same subgroup generator:

$$
\gamma
$$

is reused for every digit.

---

## The General Pohlig–Hellman Algorithm

Now return to a cyclic group:

$$
G=\langle g\rangle
$$

of order:

$$
N
=
\prod_{i=1}^{r}
q_i^{e_i}.
$$

Given:

$$
h=g^x,
$$

we want:

$$
x\pmod N.
$$

### Project into each prime-power subgroup

For each factor:

$$
n_i=q_i^{e_i},
$$

define:

$$
M_i
=
\frac{N}{n_i}.
$$

Then compute:

$$
g_i=g^{M_i},
$$

$$
h_i=h^{M_i}.
$$

The element $g_i$ has order:

$$
n_i.
$$

Also:

$$
h_i
=
h^{M_i}
=
(g^x)^{M_i}
=
g_i^x.
$$

Therefore the projected DLP reveals:

$$
\boxed{
x_i
\equiv
x
\pmod{n_i}.
}
$$

### Solve each prime-power component

Use the digit-lifting routine to compute:

$$
x_i
\pmod{q_i^{e_i}}.
$$

After processing all factors, we have:

$$
x\equiv x_1\pmod{q_1^{e_1}},
$$

$$
x\equiv x_2\pmod{q_2^{e_2}},
$$

and so on.

Because the moduli:

$$
q_i^{e_i}
$$

are pairwise coprime, CRT gives one unique solution:

$$
x\pmod N.
$$

### General pseudocode

```text
Input:
    g of order N
    h = g^x

1. Factor:
       N = product(q_i^e_i)

2. For each prime-power n_i = q_i^e_i:

       M_i <- N / n_i

       g_i <- g^M_i
       h_i <- h^M_i

       x_i <- prime_power_dlog(
                    g_i,
                    h_i,
                    q_i,
                    e_i
              )

3. Reconstruct x with CRT:

       x = CRT(
              x_i mod n_i
           )

4. Verify:
       g^x == h

5. Return x mod N
```

This is the entire architecture of Pohlig–Hellman.

The algorithm is conceptually a composition of:

$$
\boxed{
\text{subgroup projection}
+
\text{base-}q\text{ digit lifting}
+
\text{CRT}.
}
$$

---

## Worked Example Modulo 337

Take the multiplicative group:

$$
\mathbb F_{337}^{\times}.
$$

Because $337$ is prime:

$$
|\mathbb F_{337}^{\times}|
=
336.
$$

Factor:

$$
336
=
2^4\cdot3\cdot7.
$$

So the group order is very smooth.

Choose the generator:

$$
g=10.
$$

For this example:

$$
\operatorname{ord}_{337}(10)=336.
$$

Let the secret logarithm be:

$$
x=233.
$$

Compute:

$$
h
=
10^{233}
\bmod337.
$$

This gives:

$$
\boxed{
h=166.
}
$$

The attacker is given:

$$
g=10,
\qquad
h=166,
\qquad
N=336.
$$

The goal is to recover 233.

### Component modulo $16$

Take:

$$
n_1=16.
$$

Then:

$$
M_1
=
\frac{336}{16}
=
21.
$$

Project:

$$
g_1
=
g^{21}
\bmod337,
$$

$$
h_1
=
h^{21}
\bmod337.
$$

The prime-power routine solves:

$$
g_1^{x_1}=h_1
$$

inside a subgroup of order 16 and obtains:

$$
\boxed{
x_1\equiv9\pmod{16}.
}
$$

Indeed:

$$
233\bmod16=9.
$$

### Component modulo $3$

Now:

$$
n_2=3,
$$

$$
M_2
=
\frac{336}{3}
=
112.
$$

Projection gives a subgroup of order 3, and the DLP yields:

$$
\boxed{
x_2\equiv2\pmod3.
}
$$

Indeed:

$$
233\bmod3=2.
$$

### Component modulo $7$

Finally:

$$
n_3=7,
$$

$$
M_3
=
\frac{336}{7}
=
48.
$$

The projected DLP gives:

$$
\boxed{
x_3\equiv2\pmod7.
}
$$

Again:

$$
233\bmod7=2.
$$

### The information recovered

We now know:

$$
x\equiv9\pmod{16},
$$

$$
x\equiv2\pmod3,
$$

$$
x\equiv2\pmod7.
$$

The original 336-element DLP has been replaced by very small problems with moduli:

$$
16,\ 3,\ 7.
$$

CRT performs the final reconstruction.

---

## Chinese Remainder Reconstruction

We need to solve:

$$
x\equiv9\pmod{16},
$$

$$
x\equiv2\pmod3,
$$

$$
x\equiv2\pmod7.
$$

The combined modulus is:

$$
16\cdot3\cdot7
=
336.
$$

### General CRT formula

Suppose:

$$
x\equiv a_i\pmod{n_i}
$$

with pairwise coprime $n_i$.

Define:

$$
N
=
\prod_i n_i,
$$

$$
N_i
=
\frac{N}{n_i}.
$$

Let:

$$
u_i
\equiv
N_i^{-1}
\pmod{n_i}.
$$

Then:

$$
\boxed{
x
\equiv
\sum_i
a_iN_iu_i
\pmod N.
}
$$

### Apply it

For:

$$
n_1=16,
$$

$$
N_1=21.
$$

Since:

$$
21\equiv5\pmod{16},
$$

and:

$$
5^{-1}\equiv13\pmod{16},
$$

we have:

$$
u_1=13.
$$

For:

$$
n_2=3,
$$

$$
N_2=112
\equiv1\pmod3,
$$

so:

$$
u_2=1.
$$

For:

$$
n_3=7,
$$

$$
N_3=48
\equiv6\pmod7,
$$

and:

$$
6^{-1}\equiv6\pmod7.
$$

Thus:

$$
u_3=6.
$$

Therefore:

$$
x
\equiv
9\cdot21\cdot13
+
2\cdot112
+
2\cdot48\cdot6
\pmod{336}.
$$

Reducing:

$$
\boxed{
x\equiv233\pmod{336}.
}
$$

Finally verify:

$$
10^{233}
\equiv166
\pmod{337}.
$$

So the reconstructed logarithm is correct.

---

## Complexity and What “Largest Prime Factor” Really Means

Suppose:

$$
N
=
\prod_i q_i^{e_i}.
$$

For each prime power, Pohlig–Hellman recovers $e_i$ base-$q_i$ digits.

Each digit requires a DLP in a subgroup of order:

$$
q_i.
$$

If Baby-Step Giant-Step is used for these inner DLPs, one digit costs approximately:

$$
O(\sqrt{q_i}).
$$

So a rough group-operation model is:

$$
\boxed{
O\left(
\sum_i
e_i
\left(
\log N+\sqrt{q_i}
\right)
\right),
}
$$

where the $\log N$ term represents exponentiation/scalar-multiplication overhead at a high level.

Ignoring polynomial/logarithmic factors, this is often summarized as being dominated by:

$$
\sqrt{q_{\max}},
$$

where:

$$
q_{\max}
=
\max_i q_i.
$$

### Completely smooth order

If every prime divisor is small, Pohlig–Hellman is extremely effective.

For example:

$$
N
=
2^{40}3^{20}5^{10}
$$

is huge as an integer.

But the inner DLPs have orders only:

$$
2,\ 3,\ 5.
$$

The exponent sizes $e_i$ require repeated lifting, but no enormous generic search remains.

### One large prime factor

Now suppose:

$$
N
=
2^{20}\cdot q
$$

where:

$$
q\approx2^{236}
$$

is prime.

Pohlig–Hellman quickly solves the $2^{20}$ part, but the remaining DLP modulo $q$ still costs approximately:

$$
\sqrt q
\approx
2^{118}
$$

generic operations.

So the large prime factor remains the real security barrier.

### Why modern groups use prime-order subgroups

A simple way to avoid smooth-order collapse is to work directly in a subgroup of large prime order:

$$
q.
$$

Then Pohlig–Hellman has nothing substantial to decompose:

$$
q
$$

is already prime.

Generic attacks remain near:

$$
O(\sqrt q).
$$

This is why finite-field and elliptic-curve standards specify subgroup orders carefully.

---

## Pohlig–Hellman on Elliptic-Curve Groups

Pohlig–Hellman is not a finite-field-specific algorithm.

It works in any finite cyclic group where the required operations are available.

For ECDLP, suppose:

$$
Q=[x]P
$$

and:

$$
N=\operatorname{ord}(P)
=
\prod_i q_i^{e_i}.
$$

For each:

$$
n_i=q_i^{e_i},
$$

compute:

$$
P_i
=
\left[
\frac{N}{n_i}
\right]P,
$$

$$
Q_i
=
\left[
\frac{N}{n_i}
\right]Q.
$$

Then:

$$
Q_i
=
[x]P_i.
$$

The point:

$$
P_i
$$

has order:

$$
n_i.
$$

So solving:

$$
Q_i=[x_i]P_i
$$

reveals:

$$
x_i
\equiv
x
\pmod{n_i}.
$$

The same base-$q_i$ lifting logic applies, replacing:

- exponentiation by scalar multiplication;
- multiplication by point addition;
- inversion by point negation.

### Security implication for ECC

An elliptic curve can have a large total number of points and still be unsuitable if the selected base point $P$ has an order with only small prime factors.

The relevant quantity is:

$$
\boxed{
\operatorname{ord}(P).
}
$$

This reinforces the lesson from Part 01:

> cryptographic security lives in the subgroup actually used by the protocol.

### Cofactors

Many standardized curves have group order:

$$
|E(\mathbb F_q)|=h\cdot n,
$$

where:

- $n$ is a large prime subgroup order;
- $h$ is a small cofactor.

The secret scalar operations are intended to live in the large prime-order subgroup.

Small cofactors must still be handled correctly in protocols, but Pohlig–Hellman does not reduce the prime-order DLP merely because the ambient curve group contains a small cofactor.

---

## Executable Implementation

The implementation below is deliberately educational and targets multiplicative groups modulo a prime.

The same decomposition works for elliptic curves with the group operations replaced accordingly.

### Factorization helper

For toy examples:

```python
def factor_integer(n):
    factors = {}
    d = 2

    while d * d <= n:
        while n % d == 0:
            factors[d] = (
                factors.get(d, 0) + 1
            )

            n //= d

        d += 1

    if n > 1:
        factors[n] = (
            factors.get(n, 0) + 1
        )

    return factors
```

This trial-division helper is only for small educational inputs.

Real cryptographic parameter validation should not depend on naive factorization of arbitrary huge integers.

### Small subgroup discrete log

For each base-$q$ digit, use a tiny brute-force solver:

```python
def dlog_small(
    g,
    h,
    p,
    order,
):
    value = 1

    for x in range(order):
        if value == h:
            return x

        value = (
            value * g
        ) % p

    return None
```

For larger prime factors, this inner solver can be replaced by BSGS or Pollard rho.

That modularity is important:

$$
\boxed{
\text{Pohlig–Hellman is a reduction framework,
not the only inner DLP solver}.
}
$$

### Prime-power lifting

```python
def pohlig_prime_power(
    g,
    h,
    p,
    q,
    e,
):
    order = q ** e

    gamma = pow(
        g,
        q ** (e - 1),
        p,
    )

    x = 0

    for j in range(e):
        gx = pow(
            g,
            x,
            p,
        )

        residual = (
            h
            * pow(
                gx,
                -1,
                p,
            )
        ) % p

        c = pow(
            residual,
            q ** (e - 1 - j),
            p,
        )

        digit = dlog_small(
            gamma,
            c,
            p,
            q,
        )

        if digit is None:
            raise ValueError(
                "digit DLP failed"
            )

        x += (
            digit
            * (q ** j)
        )

    return x % order
```

This routine assumes:

$$
g
$$

has order exactly:

$$
q^e.
$$

The general algorithm first projects into such a subgroup.

### CRT

```python
def crt(residues, moduli):
    N = math.prod(moduli)
    x = 0

    for a, n in zip(
        residues,
        moduli,
    ):
        N_i = N // n

        inv = pow(
            N_i,
            -1,
            n,
        )

        x += (
            a
            * N_i
            * inv
        )

    return x % N
```

### Full Pohlig–Hellman

```python
def pohlig_hellman(
    g,
    h,
    p,
    order,
):
    factors = factor_integer(
        order
    )

    residues = []
    moduli = []

    for q, e in factors.items():
        n_i = q ** e
        cofactor = order // n_i

        g_i = pow(
            g,
            cofactor,
            p,
        )

        h_i = pow(
            h,
            cofactor,
            p,
        )

        x_i = pohlig_prime_power(
            g_i,
            h_i,
            p,
            q,
            e,
        )

        residues.append(x_i)
        moduli.append(n_i)

    x = crt(
        residues,
        moduli,
    )

    if pow(g, x, p) != h % p:
        raise ValueError(
            "recovered log failed validation"
        )

    return x
```

### Deterministic test

For:

```python
p = 337
g = 10
x = 233
h = pow(g, x, p)
```

the expected result is:

```text
h = 166
recovered x = 233
```

The intermediate congruences are:

```text
x = 9 mod 16
x = 2 mod 3
x = 2 mod 7
```

and CRT reconstructs:

```text
x = 233 mod 336
```

### Test the entire toy group

Because:

$$
N=336
$$

is small, we can do stronger validation than a handful of random trials:

```python
for x in range(336):
    h = pow(
        g,
        x,
        p,
    )

    assert (
        pohlig_hellman(
            g,
            h,
            p,
            336,
        )
        == x
    )
```

An exhaustive test across every canonical exponent is a much stronger correctness check for the educational implementation.

It is still not a security proof.

---

## Cryptographic Engineering Lessons

Pohlig–Hellman teaches several lessons that matter far beyond this one algorithm.

### Group size is not enough

A statement such as:

> "this group has 256 bits"

does not tell us the DLP security.

We need:

$$
\operatorname{ord}(g)
$$

and its factorization.

### The subgroup order must be known

Security analysis requires knowing the exact subgroup where the protocol operates.

For finite-field cryptography, that means checking the order of the selected generator.

For elliptic curves, that means checking the order of the base point.

### Smooth orders are dangerous

If:

$$
\operatorname{ord}(g)
$$

is smooth, the DLP decomposes into small pieces.

The total order may look enormous while the effective difficulty is much smaller.

### Prime-order subgroups simplify the story

If:

$$
\operatorname{ord}(g)=q
$$

with $q$ a large prime, Pohlig–Hellman cannot split the logarithm into easier prime-power components.

Then generic attacks such as BSGS and Pollard rho remain the main baseline.

### Public-key validation matters

Protocols must often ensure that received public elements actually lie in the intended subgroup.

Otherwise an attacker may force computations into small subgroups and exploit information modulo small factors.

That is a protocol attack distinct from running Pohlig–Hellman directly, but it is driven by the same group-order structure.

The number-theoretic lesson and the engineering lesson are therefore tightly connected.

---

## Conclusion

Pohlig–Hellman changes the way we think about DLP complexity.

The discrete logarithm:

$$
g^x=h
$$

is not controlled only by the numerical size of the group.

If:

$$
N=\operatorname{ord}(g)
$$

factors as:

$$
N
=
\prod_i
q_i^{e_i},
$$

then the logarithm can be recovered modulo each prime power:

$$
x_i
\equiv
x
\pmod{q_i^{e_i}}.
$$

For each prime-power component, write:

$$
x
=
x_0+x_1q+\cdots+x_{e-1}q^{e-1}.
$$

The digits are recovered one at a time from DLPs in a subgroup of order:

$$
q.
$$

The final congruences are recombined by CRT.

So the complete architecture is:

$$
\boxed{
\text{factor subgroup order}
\rightarrow
\text{project to prime powers}
\rightarrow
\text{recover base-}q\text{ digits}
\rightarrow
\text{CRT}.
}
$$

The worked example:

$$
\mathbb F_{337}^{\times}
$$

has order:

$$
336=2^4\cdot3\cdot7.
$$

Instead of treating the DLP as one 336-element search, Pohlig–Hellman recovers:

$$
x\equiv9\pmod{16},
$$

$$
x\equiv2\pmod3,
$$

$$
x\equiv2\pmod7,
$$

and CRT reconstructs:

$$
\boxed{
x=233\pmod{336}.
}
$$

The deeper lesson is:

$$
\boxed{
\text{large group order}
\neq
\text{hard DLP}.
}
$$

A cryptographically useful subgroup should contain a large prime factor—and in many modern designs the subgroup order itself is prime.

This also explains why parameter specifications publish not only field or curve sizes but subgroup orders.

The next generic algorithm in the series is **Pollard rho for discrete logarithms**, which attacks large prime-order subgroups in roughly:

$$
O(\sqrt N)
$$

expected group operations while using dramatically less memory than Baby-Step Giant-Step.


---

## References

1. Stephen C. Pohlig and Martin E. Hellman, **An Improved Algorithm for Computing Logarithms over GF(p) and Its Cryptographic Significance**, IEEE Transactions on Information Theory, 1978.

2. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, sections on Pohlig–Hellman and discrete logarithms.

3. Victor Shoup, **A Computational Introduction to Number Theory and Algebra**, chapters on cyclic groups, CRT, and discrete logarithms.

4. Henri Cohen, **A Course in Computational Algebraic Number Theory**, for computational number-theory background.

5. National Institute of Standards and Technology, **SP 800-56A Rev. 3**, for subgroup-order and discrete-logarithm-based key-establishment context.
