---
title: "Discrete Logarithms V: Index Calculus in Finite Fields"
description: "Why finite-field DLPs admit subexponential index-calculus attacks: factor bases, smooth relations, linear algebra, and individual logarithms."
pubDate: "2025-05-21"
updatedDate: '2026-09-13'
topics:
  - "Discrete Logarithms"
  - "Number Theory"
  - "Finite Fields"
  - "Cryptanalysis"
tags:
  - "index-calculus"
  - "discrete-logarithm"
  - "factor-base"
  - "smoothness"
  - "finite-fields"
difficulty: "Advanced"
status: "Reference"
series: "Discrete Logarithm Algorithms"
seriesOrder: 5
sourcePath: "experiments/mathematics/number-theory"
draft: false
---

## Table of Contents

- [Why Index Calculus Is Fundamentally Different](#why-index-calculus-is-fundamentally-different)
- [Factor Bases and Smoothness](#factor-bases-and-smoothness)
- [Relation Collection](#relation-collection)
- [Linear Algebra for Factor-Base Logarithms](#linear-algebra-for-factor-base-logarithms)
- [Worked Example in a Prime-Order Subgroup](#worked-example-in-a-prime-order-subgroup)
- [The Individual Logarithm Phase](#the-individual-logarithm-phase)
- [Why the Algorithm Can Be Subexponential](#why-the-algorithm-can-be-subexponential)
- [Why the Same Strategy Does Not Transfer to Generic ECDLP](#why-the-same-strategy-does-not-transfer-to-generic-ecdlp)
- [From Classical Index Calculus to NFS and Function-Field Methods](#from-classical-index-calculus-to-nfs-and-function-field-methods)
- [Executable Experiment](#executable-experiment)
- [\[
x
\equiv
\ell_${17}
+
\ell_${23}](#xequivell_17ell_23)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why Index Calculus Is Fundamentally Different

The previous algorithms in this series were largely **generic**.

Baby-Step Giant-Step and Pollard rho treat group elements as opaque objects.

They only need operations such as:

- multiplication or point addition;
- inversion or point negation;
- equality testing.

They do not care whether a group element is:

- an integer modulo a prime;
- an elliptic-curve point;
- an element of some other cyclic group.

That genericity leads to the familiar square-root barrier:

\[
O(\sqrt n)
\]

for a subgroup of order \(n\).

Index calculus takes a completely different approach.

In a multiplicative finite field, elements have an arithmetic representation.

An element of:

\[
\mathbb F_p^\times
\]

can be represented by an integer:

\[
1,\ldots,p-1.
\]

Those integers can factor.

That extra structure allows the algorithm to ask:

> Can this group element be expressed as a product of small, reusable building blocks?

If enough such factorizations are found, the DLP becomes a large linear-algebra problem.

This is the central idea of **index calculus**.

### Generic versus representation-specific attacks

The distinction is:

\[
\boxed{
\text{generic attack}
\Rightarrow
\text{uses only the group law}
}
\]

whereas:

\[
\boxed{
\text{index calculus}
\Rightarrow
\text{uses the arithmetic representation of field elements}.
}
\]

That difference is one of the deepest reasons finite-field DLP and ECDLP have different classical security-per-bit.

---

## Factor Bases and Smoothness

Let:

\[
G=\langle g\rangle
\subseteq
\mathbb F_p^\times
\]

be a cyclic subgroup of order:

\[
n.
\]

Given:

\[
h=g^x,
\]

the goal is to recover:

\[
x\pmod n.
\]

Index calculus starts by choosing a **factor base**:

\[
\mathcal B
=
\{q_1,q_2,\ldots,q_m\}.
\]

In a classical prime-field example, these are usually small primes or other small algebraic objects.

### Smoothness

An integer representative \(y\) is **\(\mathcal B\)-smooth** if it factors completely over the factor base:

\[
\boxed{
y
=
\prod_{i=1}^{m}
q_i^{e_i}.
}
\]

For example, with:

\[
\mathcal B=\{2,3,5,7\},
\]

the integer:

\[
1890
=
2\cdot3^3\cdot5\cdot7
\]

is factor-base smooth.

But:

\[
1891
\]

would not be smooth if its factorization contains a prime outside the factor base.

### Smoothness is the scarce resource

The algorithm repeatedly produces field elements and hopes that their integer representatives factor entirely over:

\[
\mathcal B.
\]

Most candidates may fail.

The probability of smoothness depends on:

- the size of the candidate integers;
- the largest factor-base element;
- the size of the factor base;
- the field representation.

Choosing the factor-base bound is therefore a tradeoff.

A larger factor base gives:

- more smooth relations;

but also:

- more unknown logarithms;
- a larger relation matrix;
- more expensive linear algebra.

A smaller factor base gives:

- fewer unknowns;

but:

- rarer smooth relations.

That balance drives the complexity analysis.

### Subgroup caveat

If \(g\) generates only a subgroup:

\[
G\subsetneq\mathbb F_p^\times,
\]

then:

\[
\log_g(q_i)
\]

exists only when:

\[
q_i\in G.
\]

So a subgroup-based implementation must ensure its factor-base elements lie in the subgroup being attacked.

This subtlety disappears when \(g\) generates the entire multiplicative group.

It is important enough that our executable example will check it explicitly.

---

## Relation Collection

Choose an exponent:

\[
k\in\mathbb Z_n.
\]

Compute:

\[
y=g^k\bmod p.
\]

Interpret \(y\) using a chosen integer representative.

If \(y\) is factor-base smooth:

\[
y
=
\prod_i q_i^{e_i},
\]

then, as an equality in:

\[
\mathbb F_p^\times,
\]

we have:

\[
g^k
=
\prod_i q_i^{e_i}.
\]

Take discrete logarithms to base \(g\):

\[
k
\equiv
\sum_i
e_i\log_g(q_i)
\pmod n.
\]

Define the unknown factor-base logs:

\[
\ell_i
=
\log_g(q_i).
\]

Every smooth relation gives one linear equation:

\[
\boxed{
e_1\ell_1
+
e_2\ell_2
+\cdots+
e_m\ell_m
\equiv
k
\pmod n.
}
\]

### Relation vector

The smooth factorization:

\[
y
=
q_1^{e_1}\cdots q_m^{e_m}
\]

is encoded as the exponent vector:

\[
(e_1,\ldots,e_m).
\]

If enough independent relation vectors are collected, we obtain a matrix system:

\[
A\ell
\equiv
b
\pmod n,
\]

where:

\[
\ell
=
\begin{bmatrix}
\ell_1\\
\vdots\\
\ell_m
\end{bmatrix}.
\]

The relation-collection phase therefore transforms discrete logarithms into linear algebra.

### Independence matters

Collecting exactly \(m\) smooth relations does not guarantee success.

The matrix may be rank deficient.

Implementations usually gather more relations than the bare minimum and select or process a full-rank subsystem.

So the real goal is:

\[
\boxed{
\text{enough independent smooth relations},
}
\]

not merely "one relation per factor-base element."

---

## Linear Algebra for Factor-Base Logarithms

Once enough relations have been collected, solve:

\[
A\ell
\equiv
b
\pmod n.
\]

If:

\[
n
\]

is prime, arithmetic takes place in the field:

\[
\mathbb F_n,
\]

and ordinary Gaussian elimination works cleanly.

Every nonzero pivot is invertible.

### Composite modulus problem

If the relevant group order is composite, then:

\[
\mathbb Z/n\mathbb Z
\]

is not a field.

A nonzero pivot may fail to have an inverse.

For example, modulo 12:

\[
6\ne0
\]

but:

\[
6^{-1}\pmod{12}
\]

does not exist.

Therefore a naive matrix routine that assumes every nonzero pivot is invertible can fail.

This was an important point in the original notes.

### Robust approaches

Common approaches include:

- factor the group order;
- solve modulo prime powers;
- recombine solutions with the Chinese Remainder Theorem;
- use linear-algebra machinery designed for modules over composite rings.

In educational code, a prime-order subgroup is especially convenient because the relation system can be solved over an actual finite field.

That is what we use below.

---

## Worked Example in a Prime-Order Subgroup

Consider:

\[
p=1019.
\]

Since:

\[
1019-1
=
1018
=
2\cdot509,
\]

the quadratic-residue subgroup has prime order:

\[
q=509.
\]

Take:

\[
g=3.
\]

We verify:

\[
\operatorname{ord}_{1019}(3)=509.
\]

So the DLP lives in:

\[
G=\langle3\rangle
\]

with:

\[
|G|=509.
\]

### Choose a factor base

Use:

\[
\boxed{
\mathcal B
=
\{3,5,11,17,23,31\}.
}
\]

Each of these elements lies in:

\[
G.
\]

Because \(509\) is prime and none of them is the identity, each has order 509.

Let:

\[
\ell_3=\log_3 3,
\]

\[
\ell_5=\log_3 5,
\]

and similarly for the others.

### Six smooth relations

A small relation search finds:

\[
3^{16}
\bmod1019
=
85
=
5\cdot17,
\]

so:

\[
\ell_5+\ell_{17}
\equiv16
\pmod{509}.
\]

Next:

\[
3^{17}
\bmod1019
=
255
=
3\cdot5\cdot17,
\]

hence:

\[
\ell_3+\ell_5+\ell_{17}
\equiv17.
\]

Also:

\[
3^{21}
\bmod1019
=
275
=
5^2\cdot11,
\]

so:

\[
2\ell_5+\ell_{11}
\equiv21.
\]

Further:

\[
3^{50}
\bmod1019
=
69
=
3\cdot23,
\]

giving:

\[
\ell_3+\ell_{23}
\equiv50.
\]

Then:

\[
3^{102}
\bmod1019
=
51
=
3\cdot17,
\]

giving:

\[
\ell_3+\ell_{17}
\equiv102.
\]

Finally:

\[
3^{130}
\bmod1019
=
775
=
5^2\cdot31,
\]

so:

\[
2\ell_5+\ell_{31}
\equiv130.
\]

### Matrix form

With unknown vector:

\[
\ell
=
\begin{bmatrix}
\ell_3\\
\ell_5\\
\ell_{11}\\
\ell_{17}\\
\ell_{23}\\
\ell_{31}
\end{bmatrix},
\]

we obtain:

\[
\begin{bmatrix}
0&1&0&1&0&0\\
1&1&0&1&0&0\\
0&2&1&0&0&0\\
1&0&0&0&1&0\\
1&0&0&1&0&0\\
0&2&0&0&0&1
\end{bmatrix}
\ell
\equiv
\begin{bmatrix}
16\\
17\\
21\\
50\\
102\\
130
\end{bmatrix}
\pmod{509}.
\]

Gaussian elimination modulo 509 gives:

\[
\boxed{
\ell_3=1,
}
\]

\[
\boxed{
\ell_5=424,
}
\]

\[
\boxed{
\ell_{11}=191,
}
\]

\[
\boxed{
\ell_{17}=101,
}
\]

\[
\boxed{
\ell_{23}=49,
}
\]

\[
\boxed{
\ell_{31}=300.
}
\]

These values can be verified independently:

\[
3^{424}
\equiv5
\pmod{1019},
\]

\[
3^{191}
\equiv11
\pmod{1019},
\]

and so on.

At this point, the expensive precomputation phase is complete.

The factor-base logarithms can now be reused for many target logarithms in the same group.

---

## The Individual Logarithm Phase

Suppose the target is:

\[
h=g^x.
\]

Once the factor-base logarithms are known, the goal is to make the target smooth.

Choose a randomizer:

\[
r\in\mathbb Z_n
\]

and compute:

\[
hg^r\bmod p.
\]

If:

\[
hg^r
=
\prod_i q_i^{e_i},
\]

then:

\[
\log_g(hg^r)
\equiv
\sum_i e_i\ell_i
\pmod n.
\]

But:

\[
\log_g(hg^r)
\equiv
x+r
\pmod n.
\]

Therefore:

\[
\boxed{
x
\equiv
\sum_i e_i\ell_i-r
\pmod n.
}
\]

### Worked target

Let:

\[
x=137.
\]

Then:

\[
h
=
3^{137}
\bmod1019
=
328.
\]

Try:

\[
r=13.
\]

We obtain:

\[
hg^{13}
\bmod1019
=
391.
\]

But:

\[
391
=
17\cdot23.
\]

Therefore:

\[
x+13
\equiv
\ell_{17}
+
\ell_{23}
\pmod{509}.
\]

Using the precomputed logs:

\[
x+13
\equiv
101+49
=
150
\pmod{509}.
\]

Hence:

\[
\boxed{
x
\equiv
150-13
=
137
\pmod{509}.
}
\]

The target discrete logarithm has been recovered without a square-root search over all 509 possibilities.

For this tiny toy group that distinction is not practically important.

For large finite fields, this **precomputation + individual logarithm** architecture is central.

---

## Why the Algorithm Can Be Subexponential

The runtime is governed by a tradeoff between:

- factor-base size;
- smoothness probability;
- relation-collection cost;
- linear-algebra cost;
- individual-logarithm smoothness search.

If the factor base is too small, smooth relations are extremely rare.

If it is too large, the matrix becomes expensive.

Optimizing this balance leads to subexponential complexity.

### \(L\)-notation

Subexponential algorithms are often described using:

\[
L_N[\alpha,c]
=
\exp\left(
(c+o(1))
(\ln N)^\alpha
(\ln\ln N)^{1-\alpha}
\right).
\]

This notation sits between polynomial and fully exponential behavior.

For:

\[
0<\alpha<1,
\]

the function is:

- faster than \(N^\varepsilon\) for every fixed \(\varepsilon>0\);
- slower than any fixed power of \(\log N\).

Classical index-calculus variants in prime fields achieve subexponential behavior under smoothness heuristics.

The exact constant and exponent depend on the algorithm and field model.

### Why smoothness probabilities matter

The crucial number-theoretic fact is that sufficiently large random-looking integers occasionally factor entirely into comparatively small primes.

Those rare events generate relations.

The algorithm does not need every residue to be smooth.

It only needs enough smooth residues to span the factor-base logarithms.

That is why:

\[
\boxed{
\text{smoothness probability}
}
\]

is the central resource of index calculus.

---

## Why the Same Strategy Does Not Transfer to Generic ECDLP

An elliptic-curve point:

\[
P=(x,y)
\]

does not factor multiplicatively into "small points" in the same natural way that an integer representative factors into small primes.

There is no direct analogue of:

\[
y
=
\prod_i q_i^{e_i}
\]

that turns a generic elliptic-curve point into a sparse linear relation among reusable small building blocks.

That blocks the classical index-calculus strategy.

### Generic ECDLP remains square-root

For well-chosen ordinary elliptic curves over large prime fields, the principal generic attacks remain algorithms such as:

- Pollard rho;
- Baby-Step Giant-Step.

Their complexity is roughly:

\[
O(\sqrt n)
\]

for subgroup order \(n\).

No general classical subexponential algorithm analogous to finite-field index calculus is known for standard prime-field ECDLP.

### Important nuance

This does **not** mean every elliptic curve is immune to special attacks.

Certain curve families or parameter choices may admit:

- pairing-based reductions;
- transfer attacks;
- anomalous-curve attacks;
- special-field reductions.

So the precise statement is:

\[
\boxed{
\text{generic standard ECDLP lacks the finite-field factorization structure
used by classical index calculus}.
}
\]

That structural difference is one major reason elliptic curves can use much smaller parameters for comparable classical security.

---

## From Classical Index Calculus to NFS and Function-Field Methods

Classical index calculus is the conceptual ancestor of more advanced finite-field DLP algorithms.

The recurring architecture remains recognizable:

\[
\boxed{
\text{factor base}
\rightarrow
\text{relation collection}
\rightarrow
\text{linear algebra}
\rightarrow
\text{individual logarithm}.
}
\]

The modern algorithms become much more sophisticated in how they generate relations.

### Number Field Sieve for discrete logarithms

For large prime fields, Number Field Sieve methods dominate asymptotically at cryptographic sizes.

Instead of factoring only ordinary residues directly, NFS constructs relations using arithmetic in carefully chosen number fields.

The linear algebra is still there.

The factor base is still there.

Smoothness is still there.

But the relation-generation mechanism is much more powerful.

For prime-field DLP, the asymptotic complexity of NFS-style methods is commonly expressed in the form:

\[
L_p
\left[
\frac13,
\left(\frac{64}{9}\right)^{1/3}
\right]
\]

for the classical large-prime-field setting, up to variant-specific refinements.

### Function-field methods

For extension fields, especially particular characteristic regimes, function-field and specialized finite-field algorithms exploit polynomial structure.

Again, the implementation details differ dramatically, but the conceptual DNA remains index-calculus-like:

- find relations among small algebraic objects;
- solve for their logarithms;
- descend a target into those objects.

### Individual logarithm as descent

In advanced methods, the target is not always made smooth in one lucky step.

Instead, the algorithm may recursively rewrite the target into progressively smaller or simpler elements.

This is often called a **descent**.

So the simple equation:

\[
hg^r
=
\prod_i q_i^{e_i}
\]

is the elementary form of a much broader strategy.

---

## Executable Experiment

The following toy implementation uses the prime-order subgroup from the worked example.

It is intentionally small and transparent.

### Parameters

```python
p = 1019
order = 509
g = 3

factor_base = [
    3,
    5,
    11,
    17,
    23,
    31,
]
```

Every factor-base element is checked to satisfy:

\[
q_i^{509}\equiv1\pmod{1019}.
\]

### Smooth factorization

```python
def smooth_factor(
    value,
    factor_base,
):
    exponents = []
    remaining = value

    for q in factor_base:
        e = 0

        while remaining % q == 0:
            remaining //= q
            e += 1

        exponents.append(e)

    if remaining != 1:
        return None

    return exponents
```

### Relation collection

```python
def collect_relations(
    g,
    p,
    order,
    factor_base,
):
    relations = []

    for k in range(
        1,
        order,
    ):
        value = pow(
            g,
            k,
            p,
        )

        exponents = smooth_factor(
            value,
            factor_base,
        )

        if exponents is not None:
            relations.append(
                (
                    exponents,
                    k,
                    value,
                )
            )

    return relations
```

A realistic implementation would sample more strategically and stop after obtaining enough independent relations.

The exhaustive scan is used here only because the toy subgroup is tiny.

### Gaussian elimination modulo a prime

Because:

\[
509
\]

is prime, the linear system is over:

\[
\mathbb F_{509}.
\]

```python
def solve_linear_mod_prime(
    A,
    b,
    modulus,
):
    rows = [
        [
            x % modulus
            for x in row
        ]
        + [rhs % modulus]
        for row, rhs in zip(
            A,
            b,
        )
    ]

    r = 0
    cols = len(A[0])
    pivots = []

    for c in range(cols):
        pivot = None

        for i in range(
            r,
            len(rows),
        ):
            if rows[i][c] != 0:
                pivot = i
                break

        if pivot is None:
            continue

        rows[r], rows[pivot] = (
            rows[pivot],
            rows[r],
        )

        inv = pow(
            rows[r][c],
            -1,
            modulus,
        )

        rows[r] = [
            x * inv % modulus
            for x in rows[r]
        ]

        for i in range(len(rows)):
            if (
                i == r
                or rows[i][c] == 0
            ):
                continue

            factor = rows[i][c]

            rows[i] = [
                (
                    x
                    - factor * y
                ) % modulus
                for x, y in zip(
                    rows[i],
                    rows[r],
                )
            ]

        pivots.append(c)
        r += 1

        if r == cols:
            break

    if r < cols:
        raise ValueError(
            "relation matrix is rank deficient"
        )

    solution = [0] * cols

    for row_index, col in enumerate(
        pivots[:cols]
    ):
        solution[col] = (
            rows[row_index][-1]
        )

    return solution
```

### Deterministic relation set

For the article's six relations:

```python
A = [
    [0, 1, 0, 1, 0, 0],
    [1, 1, 0, 1, 0, 0],
    [0, 2, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0],
    [1, 0, 0, 1, 0, 0],
    [0, 2, 0, 0, 0, 1],
]

b = [
    16,
    17,
    21,
    50,
    102,
    130,
]
```

The solver returns:

```text
log_3(3)  = 1
log_3(5)  = 424
log_3(11) = 191
log_3(17) = 101
log_3(23) = 49
log_3(31) = 300
```

Every value is verified by checking:

\[
3^{\ell_i}
\equiv
q_i
\pmod{1019}.
\]

### Individual logarithm

For:

```python
secret = 137
h = pow(g, secret, p)
```

we get:

```text
h = 328
```

Searching for a smooth randomization finds:

```text
r = 13
h * g^r mod p = 391 = 17 * 23
```

Then:

\[
x
\equiv
\ell_{17}
+
\ell_{23}
-
13
\pmod{509},
\]

which gives:

\[
\boxed{
x=137.
}
\]

### What this experiment proves

The toy lab verifies the entire logical pipeline:

```text
choose factor base
    ↓
collect smooth relations
    ↓
solve factor-base logarithms
    ↓
randomize target
    ↓
obtain smooth target relation
    ↓
recover individual logarithm
```

It does not demonstrate cryptographic-scale performance.

The asymptotic advantage appears only when the smoothness/linear-algebra tradeoff is tuned for much larger fields.

---

## Conclusion

Index calculus marks the point where this series leaves purely generic DLP algorithms.

Baby-Step Giant-Step and Pollard rho work because every cyclic group supports:

- exponentiation or scalar multiplication;
- inverses;
- equality;
- collisions.

Index calculus works because finite-field elements provide something extra:

\[
\boxed{
\text{factorization structure}.
}
\]

Choose a factor base:

\[
\mathcal B
=
\{q_1,\ldots,q_m\}.
\]

Search for exponents \(k\) such that:

\[
g^k\bmod p
\]

is \(\mathcal B\)-smooth:

\[
g^k
=
\prod_i
q_i^{e_i}.
\]

Every such event yields:

\[
k
\equiv
\sum_i
e_i\log_g(q_i)
\pmod n.
\]

Enough independent relations produce a linear system whose solution reveals the factor-base logarithms.

Then an individual target:

\[
h=g^x
\]

is randomized until:

\[
hg^r
\]

is smooth, giving:

\[
\boxed{
x
\equiv
\sum_i
e_i\log_g(q_i)
-r
\pmod n.
}
\]

The important computational resource is smoothness.

That is what enables subexponential algorithms in finite-field DLP settings.

The structural lesson is even more important:

\[
\boxed{
\text{the best DLP attack depends on the representation of the group}.
}
\]

For a generic prime-order group, square-root algorithms dominate.

For multiplicative finite fields, arithmetic structure opens the door to index calculus and its descendants.

For standard prime-field elliptic curves, the same direct factorization strategy is unavailable, which is one major reason ECDLP provides more classical security per bit.

At this point the algorithmic picture is becoming complete:

```text
DLP / ECDLP foundations
    ↓
Baby-Step Giant-Step
    generic square-root time-memory tradeoff
    ↓
Pohlig–Hellman
    exploit smooth subgroup order
    ↓
Pollard rho
    generic square-root time with tiny memory
    ↓
Index Calculus
    exploit finite-field representation
    ↓
NFS / function-field descendants
    advanced subexponential finite-field attacks
```

The central question has shifted from:

> How large is the group?

to the more useful question:

\[
\boxed{
\text{What mathematical structure can an attacker exploit?}
}
\]

---

## References

1. Leonard M. Adleman, **A Subexponential Algorithm for the Discrete Logarithm Problem with Applications to Cryptography**, FOCS, 1979.

2. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, sections on index-calculus methods.

3. Victor Shoup, **A Computational Introduction to Number Theory and Algebra**, chapters on discrete logarithms and computational number theory.

4. Arjen K. Lenstra and Hendrik W. Lenstra Jr., eds., **The Development of the Number Field Sieve**, Lecture Notes in Mathematics 1554, Springer.

5. Oliver Schirokauer, **Discrete Logarithms and Local Units**, for number-field-sieve discrete-logarithm techniques.

6. Antoine Joux and related work on finite-field discrete logarithms in extension fields and small-characteristic settings.
