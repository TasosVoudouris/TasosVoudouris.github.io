---
title: "Discrete Logarithms II: Baby-Step Giant-Step for ECDLP"
description: "A step-by-step implementation-oriented explanation of Shanks’s baby-step giant-step method for solving small elliptic-curve discrete logarithms."
pubDate: "2025-05-26"
updatedDate: '2026-09-18'
topics:
  - "Discrete Logarithms"
  - "Elliptic-Curve Cryptography"
  - "Cryptanalysis"
  - "Cryptographic Engineering"
tags:
  - "bsgs"
  - "baby-step-giant-step"
  - "ecdlp"
  - "shanks"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 2
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---

## Table of Contents

- [From Brute Force to a Square-Root Search](#from-brute-force-to-a-square-root-search)
- [Baby-Step Giant-Step in a Multiplicative Group](#baby-step-giant-step-in-a-multiplicative-group)
- [Baby-Step Giant-Step for the ECDLP](#baby-step-giant-step-for-the-ecdlp)
- [Worked Example on (E/\mathbb F_${17})](#worked-example-on-emathbb-f_17)
- [Correct Implementation, Edge Cases, and Validation](#correct-implementation-edge-cases-and-validation)
- [Time-Memory Tradeoff and Practical Limits](#time-memory-tradeoff-and-practical-limits)
- [Executable Experiments](#executable-experiments)
- [Conclusion](#conclusion)
- [References](#references)

---

## From Brute Force to a Square-Root Search

The first article defined the discrete logarithm problem in a cyclic group:

\[
G=\langle g\rangle,
\]

with:

\[
N=\operatorname{ord}(g).
\]

Given:

\[
h=g^x,
\]

the goal is to recover:

\[
x\in\{0,\ldots,N-1\}.
\]

The most direct algorithm is brute force:

\[
1,g,g^2,g^3,\ldots
\]

until the target \(h\) appears.

In the worst case this requires:

\[
O(N)
\]

group operations.

For an elliptic-curve group the analogous brute-force search is:

\[
\mathcal O,\ P,\ [2]P,\ [3]P,\ldots
\]

until:

\[
[x]P=Q.
\]

Again, the cost is linear in the subgroup order.

Baby-Step Giant-Step changes the structure of the search.

Instead of scanning one long list of \(N\) candidates, it writes the unknown exponent as the sum of two smaller pieces.

Choose:

\[
m=\left\lceil\sqrt N\right\rceil.
\]

Because:

\[
N\le m^2,
\]

every:

\[
0\le x<N
\]

can be written as:

\[
\boxed{
x=im+j
}
\]

with:

\[
0\le i<m,
\]

\[
0\le j<m.
\]

The DLP is therefore transformed from one search over roughly \(N\) exponents into a collision between two sets of roughly:

\[
\sqrt N
\]

group elements.

That is the entire conceptual idea behind Shanks's **Baby-Step Giant-Step (BSGS)** algorithm.

### Why "square-root" is the correct complexity statement

BSGS requires approximately:

\[
O(\sqrt N)
\]

group operations and:

\[
O(\sqrt N)
\]

stored group elements.

It is therefore a **square-root algorithm** in the group order.

If the subgroup order has bit length:

\[
\lambda=\log_2N,
\]

then brute force costs approximately:

\[
2^\lambda,
\]

while BSGS costs approximately:

\[
2^{\lambda/2}.
\]

So it is reasonable to say that BSGS halves the exponent relative to brute force when complexity is measured in the bit length of the group order.

But the clean group-operation statement is:

\[
\boxed{
O(N)
\longrightarrow
O(\sqrt N).
}
\]

This distinction becomes important when comparing algorithms later in the series.

---

## Baby-Step Giant-Step in a Multiplicative Group

Let:

\[
G=\langle g\rangle
\]

be a cyclic group of order:

\[
N.
\]

Suppose:

\[
h=g^x.
\]

Choose:

\[
m=\lceil\sqrt N\rceil.
\]

Write:

\[
x=im+j,
\]

with:

\[
0\le i,j<m.
\]

Then:

\[
h
=
g^{im+j}.
\]

Split the exponent:

\[
h
=
g^{im}g^j.
\]

Multiply by:

\[
g^{-im}.
\]

We obtain:

\[
\boxed{
hg^{-im}=g^j.
}
\]

The left side depends on \(i\).

The right side depends on \(j\).

So BSGS searches for a collision between these two expressions.

### Baby steps

Precompute:

\[
g^0,g^1,\ldots,g^{m-1}.
\]

Store them in a dictionary:

\[
g^j\mapsto j.
\]

Conceptually:

```text
1       -> 0
g       -> 1
g^2     -> 2
...
g^(m-1) -> m-1
```

A hash table gives expected constant-time lookup.

### Giant-step factor

Compute:

\[
g^{-m}.
\]

One way is:

\[
g^{-m}
=
(g^m)^{-1}.
\]

Initialize:

\[
\gamma=h.
\]

At giant step \(i\):

\[
\gamma
=
hg^{-im}.
\]

If:

\[
\gamma
\]

appears in the baby-step table as:

\[
g^j,
\]

then:

\[
hg^{-im}=g^j.
\]

Multiply by \(g^{im}\):

\[
h=g^{im+j}.
\]

Therefore:

\[
\boxed{
x=im+j.
}
\]

### Iterative giant steps

It would be wasteful to recompute:

\[
g^{-im}
\]

from scratch for each \(i\).

Instead, update:

\[
\gamma
\leftarrow
\gamma g^{-m}.
\]

Thus the giant-step phase uses one group multiplication per iteration.

### Generic multiplicative pseudocode

```python
m = ceil(sqrt(N))

baby = {}

value = identity

for j in range(m):
    baby[value] = j
    value = value * g

factor = inverse(g**m)

gamma = h

for i in range(m):
    if gamma in baby:
        j = baby[gamma]
        return i * m + j

    gamma = gamma * factor
```

The same structure works in any cyclic multiplicative group as long as we can:

- multiply group elements;
- invert them;
- compare them;
- store them in a lookup table.

### Modular-integer version

For:

\[
g^x\equiv h\pmod p,
\]

the giant-step factor is:

\[
g^{-m}\pmod p.
\]

In Python:

```python
factor = pow(
    pow(g, m, p),
    -1,
    p,
)
```

and the giant-step update is:

```python
gamma = (
    gamma * factor
) % p
```

### Correctness proof

Because:

\[
0\le x<N\le m^2,
\]

Euclidean division by \(m\) gives:

\[
x=im+j
\]

for some:

\[
0\le j<m
\]

and:

\[
0\le i<m.
\]

Therefore one of the giant-step values is:

\[
hg^{-im}
=
g^j,
\]

and \(g^j\) is present in the baby-step table.

So if:

- \(h\in\langle g\rangle\);
- \(N=\operatorname{ord}(g)\) is known;

the algorithm will find a representative of the discrete logarithm modulo \(N\).

---

## Baby-Step Giant-Step for the ECDLP

Now move from multiplicative notation to elliptic-curve point addition.

Let:

\[
P\in E(\mathbb F_q)
\]

have order:

\[
N.
\]

Suppose:

\[
Q=[x]P.
\]

The ECDLP asks us to recover:

\[
x\in\{0,\ldots,N-1\}.
\]

Again choose:

\[
m=\lceil\sqrt N\rceil
\]

and write:

\[
x=im+j.
\]

Then:

\[
Q
=
[im+j]P.
\]

Using distributivity of scalar multiplication:

\[
Q
=
[i m]P+[j]P.
\]

Rearrange:

\[
\boxed{
Q-[i m]P=[j]P.
}
\]

This is exactly the additive analogue of:

\[
hg^{-im}=g^j.
\]

### Baby steps

Precompute:

\[
[0]P,
[P],
[2]P,
\ldots,
[m-1]P.
\]

More explicitly:

\[
\mathcal O,
P,
[2]P,
\ldots,
[m-1]P.
\]

Store:

\[
[j]P\mapsto j.
\]

The identity element:

\[
\mathcal O
\]

must be included because:

\[
j=0
\]

is a valid baby step.

### Giant step

Compute:

\[
[m]P.
\]

Then define:

\[
G=-[m]P.
\]

Initialize:

\[
\gamma=Q.
\]

At giant-step index \(i\):

\[
\gamma
=
Q-[im]P.
\]

If:

\[
\gamma=[j]P
\]

appears in the baby-step table, then:

\[
Q=[im+j]P,
\]

and:

\[
\boxed{
x=im+j.
}
\]

### Efficient iterative version

Do not compute:

\[
[i m]P
\]

from scratch for every \(i\).

Instead:

\[
\gamma_0=Q
\]

and:

\[
\gamma_{i+1}
=
\gamma_i-[m]P.
\]

So once:

\[
[m]P
\]

has been computed, each giant step requires only one point addition.

This is substantially cleaner than code such as:

```python
Q - (i * m) * P
```

inside every loop iteration.

That version is mathematically correct, but it may perform a scalar multiplication repeatedly.

The iterative form exposes the intended:

\[
O(\sqrt N)
\]

group-operation structure more directly.

### ECDLP pseudocode

```python
m = ceil(sqrt(N))

baby = {}

R = O

for j in range(m):
    baby[R] = j
    R = R + P

step = -(m * P)
gamma = Q

for i in range(m):
    if gamma in baby:
        j = baby[gamma]

        x = i * m + j

        if x < N:
            return x

    gamma = gamma + step
```

### Point representation in the table

For a real implementation, baby-step keys need a canonical representation.

Possible choices include:

- the curve library's immutable/hashable point object;
- affine coordinate tuples;
- canonical compressed point encodings.

Do not use an ambiguous representation.

In SageMath, elliptic-curve points can be used directly in the relevant structures.

In custom Python code, affine tuples are simple for educational curves.

---

## Worked Example on \(E/\mathbb F_{17}\)

The original experiment uses:

\[
E:
y^2=x^3+2x+2
\pmod{17}.
\]

Take:

\[
P=(5,1).
\]

The point has order:

\[
\boxed{
N=19.
}
\]

So:

\[
\langle P\rangle
\]

contains 19 points including the point at infinity.

Because 19 is prime, every non-identity point in this subgroup is also a generator.

### The target

Take:

\[
x=16.
\]

Then:

\[
Q=[16]P.
\]

Direct scalar multiplication gives:

\[
\boxed{
Q=(10,11).
}
\]

We now recover 16 using BSGS.

### Step 1: choose \(m\)

\[
m
=
\lceil\sqrt{19}\rceil
=
5.
\]

Every:

\[
x\in\{0,\ldots,18\}
\]

can be written:

\[
x=5i+j
\]

with:

\[
0\le i,j<5.
\]

For:

\[
x=16,
\]

the hidden decomposition is:

\[
16
=
3\cdot5+1.
\]

The algorithm does not know this in advance.

### Step 2: baby table

Compute:

\[
[0]P=\mathcal O,
\]

\[
[1]P=(5,1),
\]

\[
[2]P=(6,3),
\]

\[
[3]P=(10,6),
\]

\[
[4]P=(3,1).
\]

Store:

| \(j\) | \([j]P\) |
|---:|---|
| 0 | \(\mathcal O\) |
| 1 | \((5,1)\) |
| 2 | \((6,3)\) |
| 3 | \((10,6)\) |
| 4 | \((3,1)\) |

### Step 3: giant step

First compute:

\[
[5]P=(9,16).
\]

So:

\[
-[5]P=(9,1).
\]

Start with:

\[
\gamma_0=Q=(10,11).
\]

The giant-step values are:

\[
\gamma_0
=
Q
=
(10,11),
\]

\[
\gamma_1
=
Q-[5]P
=
(13,10),
\]

\[
\gamma_2
=
Q-[10]P
=
(16,13),
\]

\[
\gamma_3
=
Q-[15]P
=
(5,1).
\]

But:

\[
(5,1)=P=[1]P.
\]

So at:

\[
i=3
\]

we obtain:

\[
j=1.
\]

Therefore:

\[
x
=
im+j
=
3\cdot5+1
=
\boxed{16}.
\]

### Why the collision proves the answer

The collision is:

\[
Q-[15]P=P.
\]

Add:

\[
[15]P
\]

to both sides:

\[
Q=[16]P.
\]

So this is not a heuristic match.

It is an exact group identity.

---

## Correct Implementation, Edge Cases, and Validation

The original SageMath notes had the right central BSGS idea, but several details deserve correction.

### Identity target should return \(0\), not \(N\)

If:

\[
Q=\mathcal O,
\]

then:

\[
Q=[0]P.
\]

Also:

\[
Q=[N]P,
\]

\[
Q=[2N]P,
\]

and so on.

But when the DLP is represented canonically as:

\[
x\in\{0,\ldots,N-1\},
\]

the correct answer is:

\[
\boxed{x=0}.
\]

Returning:

\[
P.\operatorname{order}()
\]

for the identity gives an equivalent exponent but not the canonical residue.

This matters because an implementation should define exactly which representative it returns.

### The original randomized test hid this issue

The earlier test sampled:

```python
x = random.randint(2, 19)
```

on a point of order 19.

So when:

```text
x = 19
```

the target became:

\[
Q=[19]P=\mathcal O.
\]

The function then returned 19, allowing:

```python
assert recovered == x
```

to pass.

But mathematically:

\[
19\equiv0\pmod{19}.
\]

A cleaner test samples canonical exponents:

```python
x in range(0, 19)
```

and expects:

```python
Q = O -> x = 0
```

### Verify subgroup membership

BSGS solves the DLP in:

\[
\langle P\rangle.
\]

If:

\[
Q\notin\langle P\rangle,
\]

no solution exists.

When \(P\) has order \(N\), a useful necessary membership check is:

\[
[N]Q=\mathcal O.
\]

For a prime-order subgroup inside a larger curve group, this confirms that \(Q\) lies in the \(N\)-torsion subgroup, though library-level validation still matters.

For the tiny curve used here:

\[
P
\]

has order 19 and the entire curve happens to contain 19 points, so:

\[
\langle P\rangle=E(\mathbb F_{17}).
\]

Every curve point is in the subgroup.

That special property should not be generalized to arbitrary curves.

### Validate the returned logarithm

After recovering a candidate:

\[
x,
\]

always verify:

\[
[x]P=Q.
\]

This costs one scalar multiplication and catches:

- implementation bugs;
- representation errors;
- wrong subgroup orders;
- table-collision mistakes;
- convention mistakes.

For educational code, explicit validation is worth the small overhead.

### Avoid floating-point square roots

For cryptographic-size integers, code such as:

```python
ceil(sqrt(N))
```

may accidentally invoke floating-point arithmetic.

A safer integer construction is:

```python
from math import isqrt


m = isqrt(N)

if m * m < N:
    m += 1
```

This computes:

\[
\lceil\sqrt N\rceil
\]

exactly for arbitrarily large integers.

### Deterministic tests are better than random-only tests

Random tests are useful.

They should supplement, not replace, deterministic known cases.

For the curve:

\[
E/\mathbb F_{17},
\]

we can test **every** canonical exponent:

\[
x=0,1,\ldots,18.
\]

There are only 19.

That is a stronger unit test than 100 random draws from almost the same tiny space.

A complete exhaustive test is:

```python
for x in range(P.order()):
    Q = x * P

    assert (
        bsgs_ecdlp(P, Q)
        == x
    )
```

If all 19 pass, the implementation covers:

- identity;
- \(P\);
- all intermediate multiples;
- \(-P=[18]P\).

---

## Time-Memory Tradeoff and Practical Limits

BSGS is dramatically better than brute force, but its memory cost is substantial.

For subgroup order:

\[
N,
\]

the baby table stores approximately:

\[
\sqrt N
\]

group elements.

So:

\[
\boxed{
T=O(\sqrt N),
\qquad
M=O(\sqrt N).
}
\]

### A 256-bit prime-order elliptic-curve group

Suppose:

\[
N\approx2^{256}.
\]

Then:

\[
\sqrt N
\approx
2^{128}.
\]

BSGS would require roughly:

\[
2^{128}
\]

baby steps.

Even if each stored entry used an unrealistically compact 32 bytes, storage alone would be:

\[
2^{128}\cdot32
=
2^{133}
\]

bytes.

That is approximately:

\[
1.09\times10^{40}
\]

bytes.

So BSGS does not make real 256-bit ECDLP instances practical.

It explains the generic square-root security level.

### Why this corresponds to roughly 128-bit security

A prime-order elliptic-curve subgroup of size near:

\[
2^{256}
\]

faces generic attacks near:

\[
2^{128}
\]

group operations.

That is the origin of the rough classical 128-bit security interpretation of standard 256-bit prime-order elliptic-curve groups.

The mapping is not because:

\[
256/2=128
\]

by convention.

It follows from square-root generic attacks.

### BSGS versus Pollard rho

Pollard rho for discrete logarithms has approximately the same expected square-root time:

\[
O(\sqrt N),
\]

but its memory usage can be essentially constant or very small.

This makes Pollard rho much more important for large generic DLP/ECDLP targets.

So BSGS is not normally the preferred full-scale attack on a standard elliptic curve.

Its advantages are:

- determinism;
- conceptual simplicity;
- straightforward implementation;
- excellent performance on small and moderate groups;
- useful bounded-range variants;
- clear time-memory tradeoff.

This gives the natural transition to the next article.

### Generic-group significance

Square-root algorithms are not merely accidents of BSGS and Pollard rho.

In the generic-group model, discrete logarithms have lower bounds showing that generic algorithms require on the order of:

\[
\sqrt N
\]

group operations.

So for groups without exploitable special structure, square-root complexity is the natural generic barrier.

This is one reason the distinction between:

- generic attacks;
- representation-specific attacks;

is so important.

Finite-field DLP admits additional structure and eventually index-calculus methods.

Standard prime-field ECDLP does not currently have a comparable general subexponential classical method.

---

## Executable Experiments

The companion implementation should contain both multiplicative and elliptic-curve versions.

### Multiplicative BSGS

```python
from math import isqrt


def ceil_sqrt(n):
    m = isqrt(n)

    if m * m < n:
        m += 1

    return m


def bsgs_mod(
    g,
    h,
    modulus,
    order,
):
    m = ceil_sqrt(order)

    baby = {}

    value = 1

    for j in range(m):
        baby.setdefault(
            value,
            j,
        )

        value = (
            value * g
        ) % modulus

    g_m = pow(
        g,
        m,
        modulus,
    )

    factor = pow(
        g_m,
        -1,
        modulus,
    )

    gamma = h % modulus

    for i in range(m):
        if gamma in baby:
            x = (
                i * m
                + baby[gamma]
            )

            if (
                x < order
                and pow(
                    g,
                    x,
                    modulus,
                ) == h % modulus
            ):
                return x

        gamma = (
            gamma * factor
        ) % modulus

    return None
```

For the earlier example:

\[
2^x\equiv5\pmod{11},
\]

with:

\[
\operatorname{ord}(2)=10,
\]

the algorithm returns:

\[
\boxed{x=4}.
\]

### Minimal educational elliptic curve

For a dependency-free lab, define the curve:

\[
E:
y^2=x^3+2x+2
\pmod{17}.
\]

Represent:

\[
\mathcal O
\]

as:

```python
None
```

and affine points as:

```python
(x, y)
```

Point addition can then be implemented directly for educational purposes.

### ECDLP BSGS

```python
def bsgs_ecdlp(
    P,
    Q,
    order,
    point_add,
    point_mul,
    point_neg,
):
    if Q is None:
        return 0

    m = ceil_sqrt(order)

    baby = {}

    R = None

    for j in range(m):
        baby.setdefault(
            R,
            j,
        )

        R = point_add(
            R,
            P,
        )

    mP = point_mul(
        m,
        P,
    )

    giant_step = point_neg(
        mP,
    )

    gamma = Q

    for i in range(m):
        if gamma in baby:
            x = (
                i * m
                + baby[gamma]
            )

            if (
                x < order
                and point_mul(
                    x,
                    P,
                ) == Q
            ):
                return x

        gamma = point_add(
            gamma,
            giant_step,
        )

    return None
```

### Exhaustive toy test

For:

\[
P=(5,1),
\qquad
\operatorname{ord}(P)=19,
\]

test:

```python
for x in range(19):
    Q = point_mul(
        x,
        P,
    )

    recovered = bsgs_ecdlp(
        P,
        Q,
        19,
        point_add,
        point_mul,
        point_neg,
    )

    assert recovered == x
```

This verifies all possible canonical discrete logarithms in the toy subgroup.

### Original sample points

The original notes included several outputs.

They are all consistent with the curve and point:

\[
E:
y^2=x^3+2x+2
\pmod{17},
\]

\[
P=(5,1).
\]

For example:

\[
[8]P=(13,7),
\]

\[
[9]P=(7,6),
\]

\[
[10]P=(7,11),
\]

\[
[13]P=(16,4),
\]

\[
[15]P=(3,16),
\]

\[
[16]P=(10,11),
\]

\[
[17]P=(6,14).
\]

And:

\[
[19]P=\mathcal O.
\]

The only conceptual correction is that:

\[
19
\]

and:

\[
0
\]

represent the same scalar modulo the point order.

For a canonical DLP solver:

\[
\mathcal O
\longmapsto
0.
\]

---

## Conclusion

Baby-Step Giant-Step is the first major algorithmic improvement over direct exhaustive search in the discrete-logarithm series.

Let:

\[
G=\langle g\rangle
\]

have order:

\[
N.
\]

Choose:

\[
m=\lceil\sqrt N\rceil.
\]

Every logarithm:

\[
0\le x<N
\]

can be decomposed as:

\[
x=im+j
\]

with:

\[
0\le i,j<m.
\]

In a multiplicative group:

\[
h=g^x
\]

becomes:

\[
\boxed{
hg^{-im}=g^j.
}
\]

In an elliptic-curve group:

\[
Q=[x]P
\]

becomes:

\[
\boxed{
Q-[im]P=[j]P.
}
\]

That transforms one search over \(N\) possibilities into a collision search involving roughly:

\[
\sqrt N
\]

baby steps and:

\[
\sqrt N
\]

giant steps.

The result is:

\[
\boxed{
T=O(\sqrt N),
\qquad
M=O(\sqrt N).
}
\]

The algorithm is exact, deterministic, and generic.

It does not exploit special finite-field or elliptic-curve structure beyond the group operations themselves.

The worked curve:

\[
E:
y^2=x^3+2x+2
\pmod{17}
\]

with:

\[
P=(5,1)
\]

has:

\[
\operatorname{ord}(P)=19.
\]

For:

\[
Q=[16]P=(10,11),
\]

we choose:

\[
m=5.
\]

The giant step:

\[
Q-[15]P
\]

collides with baby step:

\[
P=[1]P.
\]

Therefore:

\[
x
=
3\cdot5+1
=
16.
\]

The implementation also teaches several important engineering details:

- use the order of \(P\), not an unrelated curve-size value;
- return \(0\) for the identity in the canonical range;
- use exact integer square roots;
- include \(\mathcal O\) in the baby table;
- iterate giant steps instead of repeatedly recomputing scalar multiples;
- validate the returned logarithm;
- test all values when the toy group is small enough.

Most importantly, BSGS explains why a 256-bit prime-order elliptic-curve group provides only about a 128-bit generic security level:

\[
\sqrt{2^{256}}
=
2^{128}.
\]

But BSGS pays for that speed with enormous memory.

That leads directly to the next algorithm:

\[
\boxed{
\text{Pollard rho for discrete logarithms}.
}
\]

Pollard rho keeps essentially the same square-root expected running time while replacing the huge lookup table with a low-memory collision search.


---

## References

1. Daniel Shanks, **Class Number, a Theory of Factorization, and Genera**, 1969, work associated with the Baby-Step Giant-Step method.

2. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, sections on generic discrete-logarithm algorithms.

3. Victor Shoup, **A Computational Introduction to Number Theory and Algebra**, sections on cyclic groups and discrete logarithms.

4. John M. Pollard, **Monte Carlo Methods for Index Computation (mod p)**, *Mathematics of Computation*, 1978.

5. Victor Shoup, **Lower Bounds for Discrete Logarithms and Related Problems**, EUROCRYPT 1997, for generic-group lower bounds.

6. National Institute of Standards and Technology, **SP 800-56A Rev. 3**, for discrete-logarithm-based key-establishment context.
