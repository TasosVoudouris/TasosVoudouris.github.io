---
title: "Elliptic Curve Mathematics VII: Models, Isomorphisms, and the j-Invariant"
description: "A study of elliptic-curve models over different fields, the j-invariant, rational points, torsion structure, and computational exploration."
pubDate: "2025-05-25"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Mathematical Foundations"
tags:
- "elliptic-curves"
- "j-invariant"
- "torsion"
- "rational-points"
difficulty: "Advanced"
series: "Elliptic Curve Mathematics"
seriesOrder: 7
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---
## The $j$-Invariant

The **$j$-invariant** is a fundamental quantity in the theory of elliptic curves. It classifies elliptic curves up to isomorphism over the algebraic closure $\overline{k}$. That is:

> Two elliptic curves are isomorphic over $\overline{k}$ **if and only if** they share the same $j$-invariant.

Formally, for an elliptic curve given in Weierstrass form:

$$
E: y^2 = x^3 + ax + b,
$$

the $j$-invariant is computed as:

$$
j = 1728 \cdot \frac{4a^3}{4a^3 + 27b^2}.
$$

This invariant encapsulates the "shape" of the elliptic curve (up to isomorphism) and plays a crucial role in moduli problems, complex multiplication theory, and more.

Moreover, given a $j$-invariant, we can explicitly reconstruct (up to isomorphism) an elliptic curve that realizes it:

$$
E: y^2 = x^3 - 3j(j - 1728)x - 2j(j - 1728)^2.
$$

This formula is especially useful for generating elliptic curves with a prescribed $j$-invariant.

```python
E = EllipticCurve([1, -1])
print(E)
print(E.j_invariant())
print(EllipticCurve_from_j(6912/31))
```



---

## Elliptic Curves over $\mathbb{Q}$

When working over the rational numbers $\mathbb{Q}$, elliptic curves can be studied with rich arithmetic structure. Of particular interest is the **torsion subgroup**, which consists of points $P \in E(\mathbb{Q})$ such that $mP = \mathcal{O}$ for some positive integer $m$. Here, $\mathcal{O}$ denotes the point at infinity.

```python
# Define elliptic curve over QQ
E = EllipticCurve([1, 2])
print("Elliptic Curve:", E)

# Torsion subgroup order and points
m = E.torsion_order()
Em_points = E.torsion_points()
print("Torsion order:", m)
print("Torsion points:", Em_points)

# Verify that m * P = 0 for each torsion point P
for p in Em_points:
    print(f"{m} * {p} =", m * p)
```

We can also visualize these torsion points on the real plane:

```python
# Plot the elliptic curve and highlight torsion points (excluding point at infinity)
g = E.plot()
for p in Em_points:
    if not p.is_zero():  # Exclude the point at infinity
        g += p.plot(color='red', pointsize=40)

# Save the plot to a file
g.save("elliptic_curve_torsion.png")  # or .pdf, .svg, etc.

```


### Elliptic Curves over Finite Fields $\mathbb{F}_p$

In the previous section, we discussed elliptic curves defined over finite fields $\mathbb{F}_p$, especially in the context of **point counting**—that is, determining the number of $\mathbb{F}_p$-rational points on the curve. This is a central problem in number theory and cryptography.

In practice, for small prime fields, we can directly compute the number of points using:

```python
E.cardinality()
```

However, for large primes (e.g., in cryptographic applications), we typically use **Schoof’s algorithm**, which computes the number of points in polynomial time using modular arithmetic and division polynomials. Be careful not to call the `E.cardinality()` on the above example, e.g. defined over $\mathbb{Q}$. Need to be defined over a finite field, because on the rational numbers cardinality is infinity!


### Supersingular and Ordinary Elliptic Curves

Let $E$ be an elliptic curve defined over a finite field $\mathbb{F}_p$, where $p$ is the characteristic of the field. The nature of the curve—whether it is *ordinary* or *supersingular*—depends on the structure of its $p$-torsion subgroup, denoted $E[p]$.

> Let $E$ be an elliptic curve over $\mathbb{F}_p$.
>
> * If $E[p] \cong \mathbb{Z}/p\mathbb{Z}$, then $E$ is called **ordinary**.
> * If $E[p] = \{ \mathcal{O} \}$ (i.e., the zero subgroup), then $E$ is called **supersingular**.

This classification has important implications for both the arithmetic and the geometry of elliptic curves, as well as for their applications in cryptography. For example, supersingular curves behave differently in isogeny-based protocols such as SIDH/SIKE, and are rare compared to ordinary curves.

A more computationally practical criterion applies when the curve is defined over $\mathbb{F}_q$, where $q = p^r$. In this case:

> **Criterion:**
> Let $E/\mathbb{F}_q$ be an elliptic curve. Then
>
> $$
> E \text{ is supersingular} \iff p \mid (q + 1 - \#E(\mathbb{F}_q)),
> $$
>
> where $\#E(\mathbb{F}_q)$ denotes the number of $\mathbb{F}_q$-rational points on $E$.

This is particularly simple to verify when $q = p$ and $p > 5$. In such cases, a supersingular curve satisfies:

$$
\#E(\mathbb{F}_p) = p + 1.
$$

This relation can be used directly to test for supersingularity, and is implemented in SageMath via:

```python
E.is_supersingular()
```

Below is an example of an ordinary curve and continue with the supersingular case:

```python
q = 13^2  # q = 13^r for an ordinary curve
k.<a> = GF(q)
p = k.characteristic()
E = EllipticCurve(k, [1, 0])
print(E)

print(E.cardinality())
```

We can check if the curve is *supersingular* like this for example: 
```python
print((q + 1 - E.cardinality()) % p == 0)  # True if supersingular
print(E.is_supersingular())
```

### Torsion Subgroups and Division Points

Another important concept is the *torsion subgroup* $E[n]$, which consists of all points $P \in E$ such that $nP = \mathcal{O}$, the identity element (point at infinity). Over algebraically closed fields of characteristic not dividing $n$, the structure of $E[n]$ is well understood:

> *Structure Theorem:* If $\text{char}(\mathbb{F}) \nmid n$, then
>
> $$
> E[n] \cong \mathbb{Z}/n\mathbb{Z} \times \mathbb{Z}/n\mathbb{Z}.
> $$

That is, the $n$-torsion subgroup is a product of two cyclic groups of order $n$, and it can be generated by two independent points $P$ and $Q$. Any $n$-torsion point can then be written as:

$$
E[n] = \langle P, Q \rangle = \{ aP + bQ \mid a, b \in \mathbb{Z}/n\mathbb{Z} \}.
$$

In SageMath, we can compute and visualize torsion points or division points (i.e., solutions to $nQ = P$) using methods such as:

```python

### add at the end of the previous example ########

# Division points of the identity
O = E(0)  # Point at infinity
print("p-division points of O:")
print(O.division_points(p))

```

These notions are not only mathematically rich but also essential in cryptographic constructions like pairing-based protocols and isogeny-based encryption schemes.

Below, we will extend our discussion by exploring *different families of elliptic curves* and studying their defining characteristics, such as special models (e.g., Montgomery, Edwards) and their computational advantages.


## Montgomery Curves

A *Montgomery curve* is an alternative model for representing elliptic curves, particularly useful in computational and cryptographic settings due to its efficiency in certain operations such as scalar multiplication.

A Montgomery curve over a field $K$ is defined by the equation:

$$
M_{A,B}: \quad By^2 = x^3 + Ax^2 + x
$$

for constants $A, B \in K$, with the condition $B(A^2 - 4) \ne 0$. This ensures the curve is non-singular.

In *projective coordinates*, the curve becomes:

$$
BY^2Z = X^3 + AX^2Z + XZ^2 \subseteq \mathbb{P}^2
$$

with the point at infinity $\mathcal{O} = (0 : 1 : 0)$ serving as the identity element.

### Group Law

Montgomery curves support a group structure with the following properties:

* *Identity*: $\mathcal{O}$ acts as the neutral element (zero of the group).
* *Negation*: For a point $P = (x, y)$, its inverse is $-P = (x, -y)$.
* *Addition*: For $P \ne Q$, the addition formula is given by:

$$
x_{R} = B\lambda^2 - (x_P + x_Q) - A
$$

$$
y_{R} = \lambda(x_P - x_R) - y_P
$$

where the slope $\lambda$ is defined as:

$$
\lambda =
\begin{cases}
\frac{y_Q - y_P}{x_Q - x_P}, & \text{if } P \ne Q, P \ne -Q \\
\frac{3x_P^2 + 2Ax_P + 1}{2By_P}, & \text{if } P = Q
\end{cases}
$$

These operations mirror those of the Weierstrass model but are typically more efficient in implementations restricted to $x$-coordinate arithmetic, such as those used in Diffie–Hellman key exchange.

### x-coordinate Arithmetic: Pseudo-Operations

Montgomery curves are especially useful in scenarios that operate solely on $x$-coordinates, such as:

* *Diffie–Hellman key exchange over elliptic curves (ECDH)*
* *Montgomery ladder scalar multiplication*

Costello and Smith [ePrint 2017/212](https://eprint.iacr.org/2017/212.pdf) describe efficient *pseudo-addition* and *pseudo-doubling* formulas that compute:

* $x(P + Q)$, given $x(P), x(Q), x(P - Q)$ — `xADD`
* $x([2]P)$, given $x(P)$ — `xDBL`

These formulas avoid dealing with $y$-coordinates altogether, improving efficiency and side-channel resistance in cryptographic implementations.


The *$j$-invariant* of a Montgomery curve $M_{A, B}$ is:

$$
j(M_{A,B}) = \frac{256(A^2 - 3)^3}{A^2 - 4}
$$

Note that the isomorphism class over an algebraic closure $\overline{K}$ depends only on $A$, not $B$. This reflects the fact that different choices of $B$ scale the curve but do not alter its isomorphism class over $\overline{K}$.


### Relation to Short Weierstrass Form

While the short Weierstrass form:

$$
E_{a,b}: \quad y^2 = x^3 + ax + b
$$

is standard and broadly applicable, Montgomery curves offer specialized benefits. A change of variables allows certain Montgomery curves to be transformed into Weierstrass curves:

$$
(x, y) \mapsto \left(t, v\right) = \left(\frac{x}{B} + \frac{A}{3B}, \frac{y}{B}\right)
$$

with resulting coefficients:

$$
a = \frac{3 - A^2}{3B^2}, \quad b = \frac{2A^3 - 9A}{27B^3}
$$

### Conditions for Inverse Transformation

Not every Weierstrass curve can be converted into a Montgomery form. For the reverse transformation $E_{a,b} \rightarrow M_{A,B}$ to exist, the following conditions must hold:

1. The curve $E_{a,b}$ must have a point of order 4.
2. The cubic $x^3 + ax + b = 0$ must have at least one root $\alpha \in K$.
3. $3\alpha^2 + a$ must be a quadratic residue in $K$.

These conditions restrict the class of Weierstrass curves that are equivalent to a Montgomery model but enable the reverse mapping when satisfied.


| Feature               | Montgomery Curve $By^2 = x^3 + Ax^2 + x$     | Weierstrass Curve $y^2 = x^3 + ax + b$      |
| --------------------- | -------------------------------------------- | ------------------------------------------- |
| Parameters            | $A, B \in K$, $B(A^2 - 4) \ne 0$             | $a, b \in K$, $4a^3 + 27b^2 \ne 0$          |
| Identity              | $(0 : 1 : 0)$                                | $\mathcal{O}$, vertical line at infinity    |
| Group Law             | Efficient, can use x-only arithmetic         | Full affine formulas for $(x, y)$           |
| Scalar Multiplication | Very efficient via xDBL/xADD                 | Standard double-and-add                     |
| Applications          | Montgomery Ladder, ECDH                      | General ECC, digital signatures             |
| x-only formulas       | Available (pseudo-ops)                       | Not directly usable                         |
| Conversion            | Maps to Weierstrass under certain conditions | Reverse map only possible under constraints |

A full implementantion of montgomery curves is in `src\montgomery.py`.
