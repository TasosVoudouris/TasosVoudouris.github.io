---
title: "Discrete Logarithms IV: Pollard’s Rho for ECDLP"
description: "A detailed exploration of Pollard’s rho method for elliptic-curve discrete logarithms, including partitions, random walks, collision equations, and implementation."
pubDate: "2025-05-26"
updatedDate: '2026-09-18'
topics:
  - "Discrete Logarithms"
  - "Elliptic-Curve Cryptography"
  - "Cryptanalysis"
  - "Cryptographic Engineering"
tags:
  - "pollard-rho"
  - "ecdlp"
  - "random-walk"
  - "collision-search"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 4
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---

## Table of Contents

- [Why Pollard Rho Matters After BSGS and Pohlig–Hellman](#why-pollard-rho-matters-after-bsgs-and-pohlighellman)
- [The ECDLP State Invariant](#the-ecdlp-state-invariant)
- [Building a Pseudorandom Walk](#building-a-pseudorandom-walk)
- [Cycle Detection and the Birthday Phenomenon](#cycle-detection-and-the-birthday-phenomenon)
- [Recovering the Discrete Logarithm from a Collision](#recovering-the-discrete-logarithm-from-a-collision)
- [A Correct Pollard-Rho Implementation](#a-correct-pollard-rho-implementation)
- [Worked Example on a Prime-Order Toy Curve](#worked-example-on-a-prime-order-toy-curve)
- [Failures, Restarts, and Composite-Order Caveats](#failures-restarts-and-composite-order-caveats)
- [Complexity, Parallelism, and Distinguished Points](#complexity-parallelism-and-distinguished-points)
- [Executable Experiments](#executable-experiments)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why Pollard Rho Matters After BSGS and Pohlig–Hellman

The previous articles developed two important ideas.

**Baby-Step Giant-Step** showed that a discrete logarithm in a cyclic group of order $n$ can be solved generically in:

$$
O(\sqrt n)
$$

group operations, but at the cost of:

$$
O(\sqrt n)
$$

stored group elements.

**Pohlig–Hellman** showed that if the subgroup order factors as:

$$
n=\prod_i q_i^{e_i},
$$

then the DLP can be reduced to smaller DLPs in the prime-power factors.

That means the hardest generic case is usually a subgroup of large prime order.

Pollard's rho algorithm is designed precisely for this setting.

Let:

$$
P\in E(\mathbb F_p)
$$

generate a cyclic subgroup of prime order:

$$
n.
$$

Given:

$$
Q=[k]P,
$$

the goal is to recover:

$$
k\in\{0,\ldots,n-1\}.
$$

Pollard rho solves this in expected:

$$
\boxed{
O(\sqrt n)
}
$$

group operations while using only a small amount of memory in its simplest cycle-detection form.

That is its central advantage over BSGS.

### The generic attack picture

For a prime-order ECDLP subgroup:

```text
Brute force
    time  ~ n
    space ~ 1

Baby-Step Giant-Step
    time  ~ sqrt(n)
    space ~ sqrt(n)

Pollard rho
    expected time  ~ sqrt(n)
    space           ~ constant / very small
```

This is why Pollard rho is one of the main generic classical benchmarks for ECDLP security.

### Why "rho"?

The algorithm generates a deterministic walk on a finite set.

Because the set is finite, the walk eventually enters a cycle.

If we draw the path from the starting point to the cycle and then the cycle itself, its shape resembles the Greek letter:

$$
\rho.
$$

The algorithm exploits a collision in this walk to recover a linear relation involving the unknown discrete logarithm.

---

## The ECDLP State Invariant

The key implementation idea is that every point visited by the walk is tracked together with two coefficients.

Maintain a state:

$$
(R,a,b)
$$

satisfying:

$$
\boxed{
R=[a]P+[b]Q.
}
$$

Since:

$$
Q=[k]P,
$$

we also have:

$$
R=[a+bk]P.
$$

The walk changes $R$, but we always update $a,b$ consistently so this identity remains true.

This invariant is what eventually converts a point collision into an equation for $k$.

### Why the coefficients matter

If we only generated points:

$$
R_0,R_1,R_2,\ldots
$$

and found:

$$
R_i=R_j,
$$

we would know that the walk collided, but we would not know how that collision relates to $P$ and $Q$.

Tracking:

$$
a_i,\ b_i
$$

gives:

$$
R_i=[a_i]P+[b_i]Q,
$$

$$
R_j=[a_j]P+[b_j]Q.
$$

Then a collision yields a solvable modular relation.

So the real Pollard-rho state is not just the curve point.

It is:

$$
\boxed{
(R_i,a_i,b_i).
}
$$

---

## Building a Pseudorandom Walk

Pollard rho needs an iteration function:

$$
f:E(\mathbb F_p)\rightarrow E(\mathbb F_p)
$$

that behaves sufficiently like a random mapping over the subgroup.

The traditional pedagogical construction partitions the group into a few subsets and assigns a different group action to each subset.

### Three-way partition

Partition the subgroup into:

$$
S_0,\ S_1,\ S_2.
$$

A simple teaching walk can use:

$$
R\in S_0:
\qquad
R' = R+P,
$$

$$
R\in S_1:
\qquad
R' = [2]R,
$$

$$
R\in S_2:
\qquad
R' = R+Q.
$$

Because:

$$
R=[a]P+[b]Q,
$$

the coefficient updates are immediate.

### Case 1: add $P$

If:

$$
R'=R+P,
$$

then:

$$
R'
=
[a+1]P+[b]Q.
$$

So:

$$
\boxed{
a'\equiv a+1\pmod n,
\qquad
b'\equiv b\pmod n.
}
$$

### Case 2: double

If:

$$
R'=[2]R,
$$

then:

$$
R'
=
[2a]P+[2b]Q.
$$

So:

$$
\boxed{
a'\equiv2a\pmod n,
\qquad
b'\equiv2b\pmod n.
}
$$

### Case 3: add $Q$

If:

$$
R'=R+Q,
$$

then:

$$
R'
=
[a]P+[b+1]Q.
$$

Thus:

$$
\boxed{
a'\equiv a\pmod n,
\qquad
b'\equiv b+1\pmod n.
}
$$

### The partition need not be cryptographically secret

The partition function is public.

Its purpose is not to protect the walk.

It only needs to map points deterministically into subsets with reasonably balanced behavior.

The original code used MD5 over a float serialization of point coordinates. That is unnecessary and potentially awkward:

- cryptographic collision resistance is irrelevant here;
- floating-point serialization is not a canonical representation of field elements;
- the point at infinity requires special handling;
- implementation portability becomes worse.

For educational code, a simple deterministic rule is easier to audit.

For example:

```python
def partition(R):
    if R is None:
        return 0

    x, y = R

    return x % 3
```

This is not claimed to be an optimal production rho partition.

It is a transparent deterministic toy rule.

For more serious implementations, one often uses more partitions or precomputed random step tables to improve walk behavior.

### The walk is deterministic, not invertible

A subtle correction is important.

The iteration function is deterministic once the partition is fixed.

It does **not** need to be invertible.

In fact, cycle-finding relies on the walk behaving like a many-to-one random mapping over a finite state space.

So the useful property is not "invertibility."

It is:

$$
\boxed{
\text{deterministic reproducibility + sufficiently random-looking mixing}.
}
$$

---

## Cycle Detection and the Birthday Phenomenon

A finite subgroup contains:

$$
n
$$

points.

If a sequence of points behaves roughly like random samples from that set, the birthday phenomenon suggests that a collision should occur after about:

$$
O(\sqrt n)
$$

steps.

More precisely, after $t$ independent uniform samples, the collision probability is approximately:

$$
1-
\exp\left(
-\frac{t(t-1)}{2n}
\right).
$$

When:

$$
t\approx\sqrt n,
$$

the exponent becomes a constant.

That square-root collision scale is the reason Pollard rho has expected:

$$
O(\sqrt n)
$$

running time.

### We do not store all visited points

If we stored every point until a duplicate appeared, we would recreate a birthday-search table with large memory.

Pollard rho instead uses a cycle-finding algorithm.

The classic choice is **Floyd's tortoise-and-hare algorithm**.

Maintain two states:

- tortoise: one step per iteration;
- hare: two steps per iteration.

If:

$$
f^i(R_0)=f^{2i}(R_0),
$$

the two walkers have met in the eventual cycle.

### State synchronization matters

The tortoise and hare must each carry their own coefficient pair.

So we evolve:

$$
(R_T,a_T,b_T)
$$

one step, and:

$$
(R_H,a_H,b_H)
$$

two steps.

A robust implementation should update the entire triplet with a single step function.

That prevents the point update and coefficient update from drifting out of sync.

Instead of separate functions such as:

```text
get_nextR(...)
get_next_a_and_b(...)
```

use:

```python
def step(state, P, Q, n):
    R, a, b = state
    ...
    return R2, a2, b2
```

The invariant:

$$
R=[a]P+[b]Q
$$

can then be checked mechanically after every step in tests.

---

## Recovering the Discrete Logarithm from a Collision

Suppose the tortoise and hare collide:

$$
R_1=R_2.
$$

Their tracked representations are:

$$
R_1=[a_1]P+[b_1]Q,
$$

$$
R_2=[a_2]P+[b_2]Q.
$$

Since:

$$
Q=[k]P,
$$

equality implies:

$$
[a_1+b_1k]P
=
[a_2+b_2k]P.
$$

Because $P$ has order $n$:

$$
a_1+b_1k
\equiv
a_2+b_2k
\pmod n.
$$

Rearrange:

$$
(b_1-b_2)k
\equiv
a_2-a_1
\pmod n.
$$

Therefore, if:

$$
b_1-b_2
\not\equiv0
\pmod n
$$

and $n$ is prime, the denominator is invertible and:

$$
\boxed{
k
\equiv
(a_2-a_1)
(b_1-b_2)^{-1}
\pmod n.
}
$$

This is the exact collision equation.

### Why prime order simplifies everything

If $n$ is prime, every nonzero value modulo $n$ is invertible.

So there are only two possibilities:

1. 

   $$
   b_1-b_2\not\equiv0\pmod n
   $$

   and the collision yields $k$;

2. 

   $$
   b_1-b_2\equiv0\pmod n
   $$

   and then the collision is useless for recovery.

In the second case, restart with a different walk seed or partition salt.

### Always verify the candidate

After computing:

$$
k,
$$

verify:

$$
[k]P=Q.
$$

This is mandatory in educational code.

A collision equation can fail because of:

- degenerate denominator;
- composite-order ambiguity;
- implementation bugs;
- corrupted coefficient tracking;
- incorrect subgroup order.

The final scalar multiplication is cheap compared with the attack and provides a strong correctness check.

---

## A Correct Pollard-Rho Implementation

We now build a small dependency-free ECDLP implementation.

The objective is not performance.

The objective is to expose exactly what the algorithm tracks.

### Exact integer state

Represent a walk state as:

```python
(R, a, b)
```

with invariant:

```text
R = aP + bQ
```

all coefficients reduced modulo:

$$
n.
$$

### Step function

```python
def rho_step(
    state,
    P,
    Q,
    n,
    point_add,
    point_mul,
):
    R, a, b = state

    if R is None:
        bucket = 0
    else:
        bucket = R[0] % 3

    if bucket == 0:
        # R <- R + P
        R = point_add(
            R,
            P,
        )

        a = (a + 1) % n

    elif bucket == 1:
        # R <- 2R
        R = point_add(
            R,
            R,
        )

        a = (2 * a) % n
        b = (2 * b) % n

    else:
        # R <- R + Q
        R = point_add(
            R,
            Q,
        )

        b = (b + 1) % n

    return R, a, b
```

The `point_mul` parameter is not needed by this particular step rule, but scalar multiplication is useful for initialization and invariant checks.

### Randomized restart seed

A fixed seed such as:

$$
R_0=P
$$

can fall into an unhelpful short cycle for a poor partition.

A more robust toy implementation chooses random:

$$
a_0,b_0\in\mathbb Z_n
$$

and constructs:

$$
R_0=[a_0]P+[b_0]Q.
$$

This does not change the mathematics.

It merely starts the walk from a different location.

### Floyd cycle search

```python
def pollard_rho_ecdlp(
    P,
    Q,
    n,
    point_add,
    point_mul,
    rng,
    max_restarts=32,
    max_steps=None,
):
    if Q is None:
        return 0

    if max_steps is None:
        max_steps = (
            10 * math.isqrt(n)
            + 100
        )

    for _ in range(max_restarts):
        a0 = rng.randrange(n)
        b0 = rng.randrange(n)

        R0 = point_add(
            point_mul(a0, P),
            point_mul(b0, Q),
        )

        tortoise = (R0, a0, b0)
        hare = (R0, a0, b0)

        for _ in range(max_steps):
            tortoise = rho_step(
                tortoise,
                P,
                Q,
                n,
                point_add,
                point_mul,
            )

            hare = rho_step(
                hare,
                P,
                Q,
                n,
                point_add,
                point_mul,
            )

            hare = rho_step(
                hare,
                P,
                Q,
                n,
                point_add,
                point_mul,
            )

            if tortoise[0] != hare[0]:
                continue

            _, a1, b1 = tortoise
            _, a2, b2 = hare

            numerator = (
                a2 - a1
            ) % n

            denominator = (
                b1 - b2
            ) % n

            if denominator == 0:
                break

            k = (
                numerator
                * pow(
                    denominator,
                    -1,
                    n,
                )
            ) % n

            if (
                point_mul(k, P)
                == Q
            ):
                return k

            break

    raise RuntimeError(
        "rho failed; retry with another walk"
    )
```

This version fixes several issues common in first implementations:

- the point and coefficients are updated together;
- division is modular inversion, not ordinary `/`;
- the identity target maps canonically to $0$;
- the scalar is sampled modulo the subgroup order;
- useless collisions trigger a restart;
- the final candidate is verified.

---

## Worked Example on a Prime-Order Toy Curve

Reuse the curve from the BSGS article:

$$
E:
y^2=x^3+2x+2
\pmod{17}.
$$

Take:

$$
P=(5,1).
$$

We previously verified:

$$
\operatorname{ord}(P)=19.
$$

Because:

$$
19
$$

is prime, the subgroup is ideal for demonstrating the simple Pollard-rho collision equation.

Choose:

$$
k=16.
$$

Then:

$$
Q=[16]P=(10,11).
$$

The algorithm knows:

$$
P,
\qquad
Q,
\qquad
n=19,
$$

but not $k$.

### A reproducible collision

For a deterministic demonstration, start from:

$$
a_0=4,
\qquad
b_0=7.
$$

So:

$$
R_0=[4]P+[7]Q.
$$

Under the three-way walk used in this article, Floyd's algorithm eventually reaches a collision between two tracked states.

One valid collision obtained by the executable test is:

$$
R_T=R_H.
$$

The associated coefficients satisfy:

$$
(a_T-a_H)
+
(b_T-b_H)k
\equiv0
\pmod{19}.
$$

The implementation computes:

$$
k
\equiv
(a_H-a_T)
(b_T-b_H)^{-1}
\pmod{19},
$$

and recovers:

$$
\boxed{k=16}.
$$

Finally:

$$
[16]P=(10,11)=Q.
$$

### Why this is more than cycle detection

The repeated point is only half the attack.

The essential information is that the same point has two different known linear representations:

$$
R
=
[a_1]P+[b_1]Q
$$

and:

$$
R
=
[a_2]P+[b_2]Q.
$$

That creates a linear congruence in the unknown $k$.

This is the same structural pattern that appears throughout cryptanalysis:

$$
\boxed{
\text{collision}
+
\text{tracked algebraic representation}
\rightarrow
\text{secret relation}.
}
$$

---

## Failures, Restarts, and Composite-Order Caveats

Pollard rho is randomized or pseudorandomized.

One run is not guaranteed to succeed.

### Degenerate collision

Suppose:

$$
R_1=R_2
$$

but:

$$
b_1-b_2
\equiv0
\pmod n.
$$

Then the collision equation becomes:

$$
0\cdot k
\equiv
a_2-a_1
\pmod n.
$$

In a prime-order group, a valid collision then also forces:

$$
a_2-a_1
\equiv0
\pmod n,
$$

so the two representations are algebraically identical and reveal nothing.

The right response is:

$$
\boxed{\text{restart}.}
$$

### Composite-order subgroup

If $n$ is composite, the denominator:

$$
d=b_1-b_2
$$

may be nonzero but not invertible.

Then:

$$
dk
\equiv
c
\pmod n
$$

is a linear congruence.

Let:

$$
g=\gcd(d,n).
$$

A solution exists only if:

$$
g\mid c.
$$

If it does, there are $g$ residue classes modulo $n$.

Additional validation may distinguish them.

However, in cryptographic practice, Pohlig–Hellman should normally be applied first to split a composite order into prime-power components.

Pollard rho is then run in the large prime-order factor.

That gives a much cleaner attack structure.

### Wrong random-scalar range

The original notes sampled:

```python
k = random.randint(
    0,
    prime,
)
```

where `prime` was the field modulus.

That is not the correct scalar domain.

The discrete logarithm is defined modulo:

$$
n=\operatorname{ord}(P).
$$

So the canonical test range is:

$$
\boxed{
0\le k<n.
}
$$

The field size $p$ and subgroup order $n$ are different quantities.

### Partition quality matters

A poor walk function can produce:

- very short cycles;
- uneven subset occupancy;
- excessive degenerate collisions.

The textbook three-part rule is excellent for learning, but optimized implementations usually use better iteration functions.

This is an engineering issue, not a change in the underlying collision equation.

---

## Complexity, Parallelism, and Distinguished Points

The birthday heuristic gives expected:

$$
O(\sqrt n)
$$

group operations.

The exact constant depends on the walk and collision method.

For a random mapping, the expected collision scale is on the order of:

$$
\sqrt{\frac{\pi n}{2}}.
$$

Pollard rho therefore has the same asymptotic time as BSGS but much smaller memory in its basic form.

### Why this matters for 256-bit ECC

If:

$$
n\approx2^{256},
$$

then:

$$
\sqrt n
\approx
2^{128}.
$$

So a generic attack still requires an infeasible amount of work.

Pollard rho does not "break" standard 256-bit elliptic curves.

It explains why their generic classical security is around 128 bits.

### Negation-map optimization

Elliptic curves satisfy:

$$
-(x,y)
=
(x,-y).
$$

Some Pollard-rho variants identify:

$$
R
$$

and:

$$
-R
$$

to reduce the effective search space and improve constants.

Such optimizations are important in high-performance ECDLP implementations, but they complicate coefficient tracking and cycle behavior.

They are best studied after the basic algorithm is fully understood.

### Distinguished points

Floyd's algorithm is excellent for a single-machine explanation.

Large distributed rho computations often use **distinguished points** instead.

Define a recognizable rare property, for example:

```text
the first t bits of the x-coordinate are zero
```

Each worker performs an independent walk and stores only points satisfying that condition.

When two walks arrive at the same distinguished point, their tracked coefficients can reveal a collision.

This has several advantages:

- parallel workers;
- sparse storage;
- easier collision sharing;
- no need to retain entire trajectories.

### Parallel rho

Pollard rho is naturally parallelizable through many independent walks.

The total generic work remains governed by the square-root barrier, but wall-clock time can be reduced by distributing that work.

This is why generic ECDLP security estimates consider large-scale parallel collision search rather than only one serial implementation.

---

## Executable Experiments

The companion lab should verify three things:

1. the walk invariant;
2. collision-based recovery;
3. repeated success across all toy logarithms.

### Toy elliptic-curve arithmetic

Use:

$$
E:
y^2=x^3+2x+2
\pmod{17}.
$$

The point:

$$
P=(5,1)
$$

has order:

$$
19.
$$

The same arithmetic code from Part 02 can be reused:

- `point_add`;
- `point_neg`;
- `point_mul`.

### Invariant test

For every state:

$$
(R,a,b),
$$

verify:

$$
R=[a]P+[b]Q.
$$

In code:

```python
def check_state(
    state,
    P,
    Q,
):
    R, a, b = state

    expected = point_add(
        point_mul(a, P),
        point_mul(b, Q),
    )

    return R == expected
```

The step function should preserve this property.

### Deterministic rho implementation

A reproducible test can seed Python's local PRNG:

```python
rng = random.Random(
    0xD10C
)
```

Then:

```python
recovered = pollard_rho_ecdlp(
    P,
    Q,
    19,
    point_add,
    point_mul,
    rng,
)

assert recovered == k
```

### Exhaustive toy validation

Because there are only 19 canonical logs, test all of them:

```python
for k in range(19):
    Q = point_mul(
        k,
        P,
    )

    recovered = pollard_rho_ecdlp(
        P,
        Q,
        19,
        point_add,
        point_mul,
        random.Random(
            1000 + k
        ),
    )

    assert recovered == k
```

This is stronger than selecting random integers from the field-modulus range.

It verifies every ECDLP instance in the toy subgroup.

### Compare with BSGS

On this tiny group both algorithms finish immediately.

Their value is conceptual:

```text
BSGS:
    deterministic
    sqrt(n) time
    sqrt(n) memory

Pollard rho:
    randomized walk
    expected sqrt(n) time
    tiny memory
```

That distinction becomes critical at realistic group sizes.

---

## Conclusion

Pollard rho is one of the most important generic attacks on the elliptic-curve discrete logarithm problem.

Given:

$$
Q=[k]P
$$

in a cyclic subgroup of prime order:

$$
n,
$$

the algorithm performs a pseudorandom walk while maintaining:

$$
\boxed{
R_i=[a_i]P+[b_i]Q.
}
$$

A collision:

$$
R_1=R_2
$$

gives:

$$
[a_1]P+[b_1]Q
=
[a_2]P+[b_2]Q.
$$

Since:

$$
Q=[k]P,
$$

we obtain:

$$
(b_1-b_2)k
\equiv
a_2-a_1
\pmod n.
$$

For prime $n$ and a nonzero denominator:

$$
\boxed{
k
\equiv
(a_2-a_1)
(b_1-b_2)^{-1}
\pmod n.
}
$$

The collision is expected after roughly square-root work because of the birthday phenomenon:

$$
\boxed{
T=O(\sqrt n).
}
$$

Unlike Baby-Step Giant-Step, the simplest Pollard-rho form does not require storing:

$$
O(\sqrt n)
$$

group elements.

That makes it the more important generic benchmark for large prime-order ECDLP groups.

This article also corrects several common implementation mistakes:

- partition hashing need not be cryptographically secure;
- field elements should not be serialized through floating-point coordinates;
- the walk does not need to be invertible;
- the point and coefficients must be updated together;
- modular division requires an inverse;
- the secret scalar lives modulo $\operatorname{ord}(P)$, not modulo the field prime;
- degenerate collisions require a restart;
- every recovered candidate should be checked with:

  $$
  [k]P=Q.
  $$

Together, the first four articles now establish a useful generic DLP toolkit:

```text
Part 01
    DLP / ECDLP foundations

Part 02
    Baby-Step Giant-Step
    -> square-root time with square-root memory

Part 03
    Pohlig–Hellman
    -> exploit smooth subgroup order

Part 04
    Pollard rho
    -> square-root expected time with tiny memory
```

The next natural step is to leave purely generic collision algorithms and study methods that exploit the representation of finite-field elements.

That leads to **Index Calculus**, where factor bases and multiplicative relations produce a fundamentally different, subexponential attack strategy for finite-field DLP.


---

## References

1. John M. Pollard, **Monte Carlo Methods for Index Computation (mod p)**, *Mathematics of Computation*, Vol. 32, No. 143, 1978.

2. Paul C. van Oorschot and Michael J. Wiener, **Parallel Collision Search with Cryptanalytic Applications**, *Journal of Cryptology*, 1999.

3. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, sections on Pollard rho and elliptic-curve discrete logarithms.

4. Victor Shoup, **Lower Bounds for Discrete Logarithms and Related Problems**, EUROCRYPT 1997.

5. Darrel Hankerson, Alfred Menezes, and Scott Vanstone, **Guide to Elliptic Curve Cryptography**, Springer, 2004.
