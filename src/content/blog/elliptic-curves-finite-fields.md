---
title: "Elliptic Curve Mathematics VI: Curves over Finite Fields, Hasse, and Frobenius"
description: "A transition from real curves to finite fields, covering point enumeration, group structure, the trace of Frobenius, and finite-field point arithmetic."
pubDate: "2025-05-25"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Number Theory"
- "Public-Key Cryptography"
tags:
- "elliptic-curves"
- "finite-fields"
- "frobenius"
- "point-counting"
difficulty: "Intermediate"
series: "Elliptic Curve Mathematics"
seriesOrder: 6
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
To study elliptic curves in the context of cryptography and number theory, we often move from the real or complex field to finite fields, where all operations are performed modulo a prime $p$. This discretization makes the group of points finite, enabling secure cryptographic constructions.

Let $p > 3$ be a prime, and define an elliptic curve over the finite field $\mathbb{F}_p$ by the simplified **Weierstrass equation**:

$$
E : y^2 = x^3 + ax + b \quad \text{where} \quad a, b \in \mathbb{F}_p
$$

The curve must satisfy the **non-singularity condition**:

$$
4a^3 + 27b^2 \not\equiv 0 \mod p
$$

This ensures the curve has no cusps or self-intersections and defines a proper group structure.

## From Real Curves to Finite Fields

In the classical setting (e.g., $\mathbb{R}$ or $\mathbb{C}$), elliptic curves are continuous smooth manifolds. However, when working over $\mathbb{F}_p$, we are interested in the **set of solutions** $(x, y) \in \mathbb{F}_p \times \mathbb{F}_p$ that satisfy the equation, along with a special identity element denoted $\mathcal{O}$, the **point at infinity**.

This transition involves:

* **Reducing coefficients** $a, b$ modulo $p$,
* **Restricting the domain** to elements in $\mathbb{F}_p$,
* **Adapting the group law** to modular arithmetic (point addition and doubling are redefined using modular inverses).

Despite working over a discrete set, the algebraic structure remains intact: the points on the curve still form an abelian group under the defined addition operation.


## The Elliptic Curve Group

Let $E(\mathbb{F}_p)$ denote the set of all points $(x, y) \in \mathbb{F}_p \times \mathbb{F}_p$ satisfying the equation $y^2 = x^3 + ax + b \mod p$, along with the identity element $\mathcal{O}$. This set forms a **finite abelian group** under point addition.

If $e > 1$, one may also consider curves over extension fields $\mathbb{F}_{p^e}$, which are particularly useful in pairing-based cryptography and supersingular curve constructions.


## Point Counting and the Trace of Frobenius

Unlike over $\mathbb{R}$, where curves contain infinitely many points, over $\mathbb{F}_p$, the number of points on a curve is finite. An important result that bounds this count is **Hasse's Theorem**, which states:

$$
\left| \, |E(\mathbb{F}_p)| - (p + 1) \, \right| \leq 2\sqrt{p}
$$

This means the number of points lies in the interval:

$$
p + 1 - 2\sqrt{p} \leq |E(\mathbb{F}_p)| \leq p + 1 + 2\sqrt{p}
$$

The deviation from $p + 1$ is encoded in an integer:

$$
t = p + 1 - |E(\mathbb{F}_p)|
$$

This integer $t$ is called the **trace of Frobenius**, and it plays a central role in point counting algorithms (e.g., Schoof's algorithm) and in determining the security level of elliptic curve cryptosystems. Below is a SageMath example: 

```python

### Sagemath ###
q = 101
E = EllipticCurve(GF(q), [1, -1])
print(E.cardinality()) # number of points on the curve
print(bool(E.trace_of_frobenius() < 2 * sqrt(q))) # check inequality
print(E.trace_of_frobenius(), q + 1 - E.cardinality() ) # Trace of frobenius
```


---

## The Group Law over $\mathbb{F}_p$

Just as with elliptic curves over the real numbers, we can define an addition operation on points of a curve $E/\mathbb{F}_p$. This operation turns the set $E(\mathbb{F}_p)$ into an abelian group, with the *point at infinity* $\mathcal{O}$ serving as the identity element.

However, key distinctions emerge when transitioning from continuous fields to finite ones:

* Over $\mathbb{R}$, lines intersect curves smoothly, and division by real numbers is always defined (except at singularities). Over $\mathbb{F}_p$, all operations must be performed modulo $p$, and division must be replaced with multiplication by modular inverses.
* The graphical interpretation of drawing lines and reflecting intersection points across the x-axis still holds *formally*, but it loses its intuitive meaning, since points are no longer ordered nor geometrically positioned on a curve as in $\mathbb{R}^2$.

### Point Addition over $\mathbb{F}_p$

Let $P = (x_1, y_1)$ and $Q = (x_2, y_2)$ be two distinct points on $E(\mathbb{F}_p)$, with $P \ne \pm Q$. Then the sum $R = P + Q = (x_3, y_3)$ is computed via:

$$
\lambda = \frac{y_2 - y_1}{x_2 - x_1} \mod p, \quad
x_3 = \lambda^2 - x_1 - x_2 \mod p, \quad
y_3 = \lambda(x_1 - x_3) - y_1 \mod p
$$

If $P = Q$, we apply the *doubling formula*:

$$
\lambda = \frac{3x_1^2 + a}{2y_1} \mod p
$$

This requires computing modular inverses for $x_2 - x_1$ or $2y_1$. If these values are zero modulo $p$, the operation is undefined, corresponding to vertical lines in the real case, and the sum is defined to be the identity element $\mathcal{O}$.

### Special Cases

* If $P = -Q$, meaning $x_1 = x_2$ and $y_1 = -y_2 \mod p$, then $P + Q = \mathcal{O}$.
* If $P = \mathcal{O}$, then $P + Q = Q$. Similarly, $Q + \mathcal{O} = P$.
* If $P = Q$ and $y_1 = 0$, then $2P = \mathcal{O}$, since the tangent line is vertical.

These rules mirror the geometric constructions over $\mathbb{R}$, but rely on modular arithmetic rather than actual intersections or slopes in Euclidean space.


| Feature          | Over $\mathbb{R}$               | Over $\mathbb{F}_p$                                          |
| ---------------- | ------------------------------- | ------------------------------------------------------------ |
| Domain           | Continuous                      | Discrete (modulo $p$)                                        |
| Point addition   | Intersections and reflections   | Modular arithmetic and inverses                              |
| Identity element | Point at infinity $\mathcal{O}$ | Same symbol $\mathcal{O}$, abstract identity                 |
| Visualization    | Geometric curve                 | Algebraic set of pairs in $\mathbb{F}_p \times \mathbb{F}_p$ |
| Group size       | Infinite                        | Finite (bounded by Hasse's theorem)                          |

In both settings, the group operation is associative, has an identity, and every point has an inverse, preserving the group axioms. However, the move to $\mathbb{F}_p$ introduces computational challenges and algebraic techniques not visible in the real case.


### Point Multiplication and Cryptographic Relevance

Let $E/\mathbb{F}_p$ be an elliptic curve and let $P \in E(\mathbb{F}_p)$. For any integer $n$, we define *scalar multiplication*:

$$
[n]P = P + P + \dots + P \quad \text{(n times)}
$$

This operation is the elliptic curve analogue of exponentiation in modular arithmetic. Efficient computation of $[n]P$ is essential for cryptographic applications and is typically performed using **double-and-add** or **Montgomery ladder** algorithms.


A small detour, we gonna analyze it more in the future. The security of elliptic curve cryptosystems rests on the presumed difficulty of the following problem:

> Given points $P, Q \in E(\mathbb{F}_p)$, find an integer $n$ such that $Q = [n]P$.

This is known as the *elliptic curve discrete logarithm problem (ECDLP)*. Unlike traditional DLP in $\mathbb{Z}_p^*$, no subexponential algorithm is known for generic elliptic curves, making ECC attractive for achieving strong security with relatively small key sizes.


## Why Count Points on an Elliptic Curve?

Back on track now, with a very important task. When defining a secure cryptographic system over an elliptic curve, it's crucial to:

* Ensure the group $E(\mathbb{F}_p)$ has *large prime order* or contains a large *prime-order subgroup*.
* Avoid curves where the group order is vulnerable to attacks (e.g., anomalous curves or small-order subgroups).

Thus, computing the number of points $|E(\mathbb{F}_p)|$ is a fundamental step in elliptic curve construction. And we present the magnificent tool that will help us with our task below. 


### Schoof’s Algorithm 

Schoof's algorithm was the first *polynomial-time* algorithm (1985) for determining $\#E(\mathbb{F}_p)$. It avoids naive enumeration, which becomes infeasible for large $p$, and instead leverages *modular arithmetic* and *division polynomials* to compute the *trace of Frobenius* modulo small primes.

Let $t = p + 1 - |E(\mathbb{F}_p)|$ be the *trace of Frobenius*. Schoof's algorithm computes $t \mod \ell$ for a series of small primes $\ell$, then reconstructs $t \mod L$ via the CRT, where $L$ exceeds $4\sqrt{p}$ (by Hasse's bound).

**Steps of the algorithm:**

1. For each small prime $\ell$, compute $t \mod \ell$ by analyzing the action of the Frobenius endomorphism $\pi$ on the $\ell$-torsion subgroup $E[\ell]$.

2. Use *division polynomials* $\psi_\ell(x) \in \mathbb{F}_p[x]$ to define the $\ell$-torsion points.

3. Reduce modulo $\psi_\ell$ to work over the finite algebra $\mathbb{F}_p[x]/(\psi_\ell(x))$, which represents the x-coordinates of $E[\ell]$.

4. Solve the characteristic equation of Frobenius:

   $$
   \pi^2 - t\pi + p = 0 \mod \ell
   $$

5. Reconstruct $t \mod L$ from its reductions via the *Chinese Remainder Theorem*.

6. Finally, compute $|E(\mathbb{F}_p)| = p + 1 - t$.

You might already have encountered a few unfamiliar terms, such as division polynomials and torsion points. Don't worry—everything will become clear in the next section. For now, we simply needed to mention these concepts to present the algorithm in its complete form. After all, the algorithm’s goal is "just" to count the number of points on an elliptic curve defined over a finite field.

Schoof’s algorithm runs in time $\tilde{O}(\log^8 p)$, which is polynomial in the size of $p$, a breakthrough compared to the exponential-time naive count.

Schoof’s algorithm was later improved:

* **Schoof–Elkies–Atkin (SEA)**: Extends Schoof by distinguishing between Elkies and Atkin primes to accelerate computation of $t \mod \ell$.
* **Satoh–Araki**, **Kedlaya**, and **Harley** algorithms: Use $p$-adic or cohomological methods for point counting over large fields, especially when $p$ is small and the field extension $\mathbb{F}_{p^k}$ is large.


| Task           | Real Curves $\mathbb{R}$   | Finite Fields $\mathbb{F}_p$   |
| -------------- | -------------------------- | ------------------------------ |
| Point addition | Geometric with lines       | Modular formulas               |
| Visualization  | Continuous and smooth      | Discrete; no visual continuity |
| Multiplication | Defined, but less relevant | Crucial for cryptography       |
| Point counting | Infinite                   | Bounded and essential          |
| Tool           | Geometry and calculus      | Algebra and number theory      |
| Algorithms     | Not required               | Schoof, SEA, Kedlaya, etc.     |



I think this is a good point to pause and take the time to absorb all the new concepts we've introduced. In the next section, we’ll continue with a different class of elliptic curves and explore their unique characteristics.
