---
title: "Arithmetic on Shamir Shares: Linearity, Degree Growth, and Why Multiplication Changes the Game"
description: "Derive what can be computed locally on Shamir shares, show exactly why multiplication doubles polynomial degree, and explain degree reduction, resharing, and the bridge from secret sharing to MPC."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "Secret Sharing"
  - "MPC"
  - "Mathematical Foundations"
tags:
  - "shamir"
  - "homomorphic-secret-sharing"
  - "degree-growth"
  - "resharing"
  - "degree-reduction"
  - "mpc"
difficulty: "Intermediate"
status: "Validated"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 3
sourcePath: "experiments/secret-sharing/shamir-arithmetic"
draft: false
---
Shamir sharing is linear. That simple sentence explains both why it is so useful and why a common first implementation can be dangerously misleading.

The recovered notes contained code of the form

```python
z_i = x_i * y_i
```

and then described the result as secure multiplication of two Shamir-shared values. The pointwise product is mathematically meaningful, but it changes the polynomial degree. That distinction is the bridge from **secret sharing** to **secure multiparty computation**.

## 1. Shamir sharing as a polynomial

Let the field be $\mathbb F_q$. A secret $s$ is the constant term of a random polynomial

$$
f(X)=s+a_1X+\cdots+a_dX^d,
$$

with degree at most $d$. Party $i$ receives

$$
[s]_i=f(\alpha_i).
$$

The reconstruction threshold is normally $d+1$ points. This is one place where old code often overloads the word `T`: sometimes it means polynomial degree, sometimes the number of parties needed to reconstruct. We use

$$
t=d+1
$$

for the reconstruction threshold.

## 2. Addition is local and free

Suppose $x=f(0)$ and $y=g(0)$, with shares

$$
x_i=f(\alpha_i),\qquad y_i=g(\alpha_i).
$$

Every party can compute

$$
z_i=x_i+y_i.
$$

These are evaluations of

$$
h(X)=f(X)+g(X).
$$

Therefore

$$
h(0)=x+y
$$

and

$$
\deg h\le \max(\deg f,\deg g).
$$

No communication is required. Subtraction and multiplication by a **public scalar** work for the same reason.

This is the precise sense in which Shamir sharing is linearly homomorphic.

## 3. Why local share multiplication is different

Now let every party compute

$$
w_i=x_i y_i.
$$

Then

$$
w_i=f(\alpha_i)g(\alpha_i)=h(\alpha_i)
$$

for

$$
h(X)=f(X)g(X).
$$

The secret is indeed

$$
h(0)=xy.
$$

So the old implementation was not nonsense. The problem is

$$
\deg h\le \deg f+\deg g.
$$

If both inputs have degree $d$, then

$$
\deg h\le 2d.
$$

The reconstruction threshold has therefore changed from

$$
d+1
$$

to as much as

$$
2d+1.
$$

After another multiplication it can become $4d$, then $8d$, and so on.

## 4. A concrete example

Take $n=5$ parties and a threshold $t=3$. We use degree-$2$ polynomials.

Two secrets are represented by

$$
f(X)=x+aX+bX^2,
$$

$$
g(X)=y+cX+dX^2.
$$

Their product is degree at most $4$:

$$
f(X)g(X)=xy+\cdots+bdX^4.
$$

Five evaluations are enough to reconstruct a degree-$4$ polynomial, so a **single** multiplication can still work with all five parties.

But the result is no longer a degree-$2$ Shamir sharing. It cannot simply be fed into another multiplication gate while pretending the original threshold structure was preserved.

That is the subtle bug behind many toy MPC implementations.

## 5. Degree reduction

After multiplication, an MPC protocol wants a fresh degree-$d$ sharing of the same product $xy$.

Conceptually, we need a transformation

$$
[h]_{2d}\longrightarrow [h(0)]_d.
$$

There are several ways to realize this depending on the security model.

A simple pedagogical approach is:

1. reconstruct the product to a trusted dealer;
2. Shamir-share it again with degree $d$.

This demonstrates the invariant but is obviously **not secure MPC** because the dealer learns the product.

A distributed resharing protocol instead lets parties contribute fresh random degree-$d$ sharings whose combined constant term is the desired secret. Robust versions require VSS, complaints, and adversarial handling.

## 6. Why Beaver triples are so important

A different route avoids directly multiplying the two secret-sharing polynomials online.

Preprocess a triple

$$
[a],\ [b],\ [c]
$$

such that

$$
c=ab.
$$

For private values $[x]$ and $[y]$, open only the masks

$$
e=x-a,
$$

$$
f=y-b.
$$

Then compute

$$
[xy]=[c]+e[b]+f[a]+ef.
$$

To verify the identity, expand:

$$
\begin{aligned}
c+eb+fa+ef
&=ab+(x-a)b+(y-b)a+(x-a)(y-b)\\
&=xy.
\end{aligned}
$$

Now the expensive nonlinear work has been moved into preprocessing. This is the gateway to the MPC series that follows this secret-sharing track.

## 7. What the recovered Shamir class got right

The old class tracked a `degree` field and used

```python
z.degree = x.degree + y.degree
```

for multiplication. That is exactly the correct warning sign.

The problem was the surrounding prose, which sometimes jumped from

> pointwise multiplication reconstructs to the product

straight to

> therefore this is an MPC implementation.

The first statement is correct. The second needs a degree-reduction protocol, preprocessing, or another multiplication mechanism.

## 8. Threshold terminology cleanup

If a polynomial has degree $d$, it needs $d+1$ points to reconstruct.

So code such as

```python
T = 4
coefs = [secret] + [random.randrange(Q) for _ in range(T)]
```

creates a degree-$4$ polynomial and therefore a **5-share reconstruction threshold**.

Calling `T=4` the threshold is off by one. In the cleaned companion implementation we name the parameter `threshold` and generate exactly `threshold - 1` random coefficients.

## 9. Security boundary

The companion code proves these algebraic facts. It is not a network protocol and it deliberately includes a trusted resharing helper to visualize degree reduction.

A maliciously secure distributed multiplication protocol additionally needs:

- authenticated or verifiable shares;
- robust opening;
- complaint/abort behavior;
- secure triple generation or another multiplication primitive;
- session separation and fresh randomness.

Those belong to **Secure Multiparty Computation** and **Threshold Cryptography Engineering**, not to basic Shamir sharing.

## 10. Takeaway

The key invariant is:

$$
\boxed{\text{linear operations preserve the sharing degree; multiplication does not.}}
$$

That one fact explains why Shamir sharing is an excellent foundation for MPC, but is not by itself a complete MPC protocol.
