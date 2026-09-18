---
title: "Elliptic Curve Mathematics III: Why the Group Law Is Associative"
description: "A careful explanation of the hardest group axiom for elliptic curves, from chord-and-tangent geometry to divisors, principal divisors, and the Picard group."
pubDate: "2025-05-21"
updatedDate: "2026-09-17"

topics:
  - "Mathematical Foundations"
  - "Algebraic Geometry"
  - "Elliptic Curve Theory"
  - "Abstract Algebra"

tags:
  - "elliptic-curves"
  - "associativity"
  - "group-law"
  - "divisors"
  - "picard-group"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 3
sourcePath: "experiments/mathematics/elliptic-curves"
draft: false
---

In the previous chapter, the chord-and-tangent construction gave us a natural addition law on an elliptic curve.

For

$$
P,Q\in E,
$$

draw the line through \(P\) and \(Q\), find its third intersection \(R\), and define

$$
P+Q=-R.
$$

Identity, inverses, and commutativity are geometrically convincing.

Associativity is different.

We need

$$
\boxed{
(P+Q)+R=P+(Q+R)
}
$$

for **every** triple of points.

Nothing in the elementary picture makes this obvious.

And although the equality can be proved by expanding the coordinate formulas, that calculation gives almost no insight into why associativity should exist in the first place.

The deeper explanation is that the elliptic-curve group law is not an arbitrary operation imposed on a cubic.

It comes from an already-existing abelian group:

$$
\boxed{
\operatorname{Pic}^0(E).
}
$$

The chord-and-tangent construction is simply the geometric manifestation of addition inside that group.

---

## Table of Contents

- [1. The associativity problem](#1-the-associativity-problem)
- [2. The geometric group law](#2-the-geometric-group-law)
- [3. Why coordinate algebra is unsatisfying](#3-why-coordinate-algebra-is-unsatisfying)
- [4. Divisors on a curve](#4-divisors-on-a-curve)
- [5. Zeros, poles, and principal divisors](#5-zeros-poles-and-principal-divisors)
- [6. Degree and divisor classes](#6-degree-and-divisor-classes)
- [7. The Picard group](#7-the-picard-group)
- [8. Why (E) is identified with (\operatorname${Pic}^0(E))](#8-why-e-is-identified-with-operatornamepic0e)
- [9. A line through three points](#9-a-line-through-three-points)
- [10. Recovering the chord-and-tangent law](#10-recovering-the-chord-and-tangent-law)
- [11. Why reflection gives the inverse](#11-why-reflection-gives-the-inverse)
- [12. Associativity now becomes automatic](#12-associativity-now-becomes-automatic)
- [13. Tangencies and intersection multiplicity](#13-tangencies-and-intersection-multiplicity)
- [14. What the proof is really saying](#14-what-the-proof-is-really-saying)
- [15. The bigger picture](#15-the-bigger-picture)
- [Further reading](#further-reading)

---

<a id="associativity-problem"></a>

## 1. The associativity problem

Let

$$
E:
y^2=x^3+ax+b
$$

be a nonsingular elliptic curve over a field of characteristic different from \(2\) and \(3\).

From the previous chapter we already know how to define

$$
P+Q.
$$

For ordinary affine points,

$$
P=(x_1,y_1),
\qquad
Q=(x_2,y_2),
$$

we compute the slope

$$
\lambda,
$$

then

$$
x_3=\lambda^2-x_1-x_2,
$$

and

$$
y_3=\lambda(x_1-x_3)-y_1.
$$

This certainly defines an operation.

But defining an operation is not enough.

To obtain a group we must prove:

$$
(P+Q)+R=P+(Q+R).
$$

Associativity is especially important computationally.

Without it, expressions such as

$$
P+P+P+P
$$

would be ambiguous.

For example,

$$
((P+P)+P)+P
$$

might differ from

$$
(P+P)+(P+P).
$$

Then scalar multiplication

$$
[n]P
$$

would not even be well defined.

So associativity is not a technical luxury.

It is what makes elliptic-curve arithmetic coherent.

---

<a id="geometric-group-law"></a>

## 2. The geometric group law

Recall the geometric construction.

Let a line intersect the cubic \(E\) at

$$
P,\quad Q,\quad R,
$$

counting multiplicities.

Then the group law is defined so that

$$
\boxed{
P+Q=-R.
}
$$

Equivalently,

$$
\boxed{
P+Q+R=\mathcal O.
}
$$

This notation is extremely suggestive.

Three collinear points sum to the identity.

If \(P=Q\), the line is the tangent at \(P\), and the intersection at \(P\) is counted twice.

If

$$
Q=-P,
$$

the line is vertical and its third projective intersection is

$$
\mathcal O.
$$

So the same principle handles:

* ordinary addition;
* doubling;
* inverses;
* the point at infinity.

But associativity remains hidden.

---

<a id="coordinate-proof"></a>

## 3. Why coordinate algebra is unsatisfying

In principle, we could prove associativity directly.

Compute

$$
P+Q,
$$

substitute its coordinates into the addition formula again to obtain

$$
(P+Q)+R,
$$

then independently compute

$$
Q+R
$$

and finally

$$
P+(Q+R).
$$

One could then simplify both rational expressions until they match.

This approach is valid.

But several problems immediately appear.

We need separate cases for:

* \(P=Q\);
* \(Q=R\);
* \(P=-Q\);
* \(Q=-R\);
* vertical lines;
* points with \(y=0\);
* the point \(\mathcal O\);
* denominators that vanish.

Even in the generic case, the resulting rational expressions are unpleasant.

A computer algebra system such as Sage can verify the generic symbolic identity.

That is useful as computational evidence.

But it does not explain **why** the identity is true.

The algebraic-geometric proof reveals the structure hidden behind the formulas.

---

<a id="divisors"></a>

## 4. Divisors on a curve

Let \(E\) be a smooth projective curve.

A **divisor** on \(E\) is a finite formal integer combination of points:

$$
\boxed{
D=\sum_{P\in E}n_P[P],
}
$$

where

$$
n_P\in\mathbb Z
$$

and all but finitely many \(n_P\) are zero.

For example,

$$
D
=
2[P]
-
[Q]
+
3[R]
$$

is a divisor.

The collection of all divisors forms an abelian group under coefficient-wise addition:

$$
\operatorname{Div}(E).
$$

For example,

$$
([P]-[Q])
+
([Q]-[R])
=
[P]-[R].
$$

This addition is obviously associative because ordinary integer addition is associative.

Already we have found an algebraic object with a built-in abelian-group structure.

The next question is how functions on the curve create special divisors.

---

<a id="principal-divisors"></a>

## 5. Zeros, poles, and principal divisors

Let

$$
f\in K(E)^\times
$$

be a nonzero rational function on the curve.

At each point \(P\), the function has an integer order

$$
\operatorname{ord}_P(f).
$$

Roughly:

* if \(f\) has a zero of multiplicity \(m\) at \(P\),

$$
\operatorname{ord}_P(f)=m;
$$

* if \(f\) has a pole of order \(m\),

$$
\operatorname{ord}_P(f)=-m;
$$

* if \(f\) is nonzero and finite at \(P\),

$$
\operatorname{ord}_P(f)=0.
$$

The **divisor of \(f\)** is

$$
\boxed{
\operatorname{div}(f)
=
\sum_P
\operatorname{ord}_P(f)[P].
}
$$

Such divisors are called **principal divisors**.

For two rational functions,

$$
f,g\in K(E)^\times,
$$

we have

$$
\operatorname{div}(fg)
=
\operatorname{div}(f)
+
\operatorname{div}(g).
$$

So multiplication of functions becomes addition of divisors.

This is one of the basic bridges between algebraic functions and geometry.

---

<a id="degree-divisor-classes"></a>

## 6. Degree and divisor classes

The degree of

$$
D=\sum_P n_P[P]
$$

is

$$
\boxed{
\deg D
=
\sum_P n_P.
}
$$

For example,

$$
\deg([P]-[Q])=0.
$$

An important theorem states that every principal divisor has degree zero:

$$
\boxed{
\deg\operatorname{div}(f)=0.
}
$$

Intuitively, a rational function on a complete smooth curve has as many zeros as poles when multiplicities are counted correctly.

Thus principal divisors live inside the degree-zero divisor group

$$
\operatorname{Div}^0(E).
$$

Two divisors are called **linearly equivalent** if their difference is principal:

$$
D_1\sim D_2
$$

when

$$
D_1-D_2
=
\operatorname{div}(f)
$$

for some rational function \(f\).

So instead of distinguishing divisors that differ only by the zeros and poles of a rational function, we place them in the same equivalence class.

---

<a id="picard-group"></a>

## 7. The Picard group

The degree-zero Picard group is

$$
\boxed{
\operatorname{Pic}^0(E)
=
\operatorname{Div}^0(E)/
\operatorname{Prin}(E),
}
$$

where

$$
\operatorname{Prin}(E)
$$

is the subgroup of principal divisors.

An element is therefore an equivalence class

$$
[D].
$$

Addition is inherited from divisor addition:

$$
[D_1]+[D_2]
=
[D_1+D_2].
$$

Because divisor addition is associative,

$$
([D_1]+[D_2])+[D_3]
=
[D_1]+([D_2]+[D_3]).
$$

Therefore,

$$
\boxed{
\operatorname{Pic}^0(E)
\text{ is an abelian group}.
}
$$

Associativity is built in.

The remarkable fact about an elliptic curve is that the curve itself can be identified with this group.

---

<a id="elliptic-picard-identification"></a>

## 8. Why \(E\) is identified with \(\operatorname{Pic}^0(E)\)

Fix the distinguished point

$$
\mathcal O.
$$

For every point

$$
P\in E,
$$

consider the degree-zero divisor

$$
[P]-[\mathcal O].
$$

This gives a map

$$
\boxed{
\Phi:
E
\longrightarrow
\operatorname{Pic}^0(E)
}
$$

defined by

$$
\boxed{
\Phi(P)
=
[P-\mathcal O].
}
$$

For a smooth projective genus-one curve, this map is an isomorphism.

That is a profound fact.

It means every degree-zero divisor class can be represented uniquely in the form

$$
[P]-[\mathcal O].
$$

So instead of working with arbitrary divisor classes, we can label them by actual points of the curve.

---

### Why genus one matters

Very roughly, the Riemann-Roch theorem shows that every degree-zero divisor \(D\) satisfies

$$
D+[\mathcal O]
\sim
[P]
$$

for some point \(P\).

Hence

$$
D
\sim
[P]-[\mathcal O].
$$

The genus-one condition is exactly what makes this representation behave so cleanly.

Thus

$$
\operatorname{Pic}^0(E)
$$

is not merely related to the elliptic curve.

For an elliptic curve,

$$
\boxed{
E\cong\operatorname{Pic}^0(E).
}
$$

This object is also the **Jacobian** of \(E\):

$$
\boxed{
E\cong\operatorname{Jac}(E).
}
$$

Elliptic curves are special because they are canonically isomorphic, once the origin is chosen, to their own Jacobians.

---

<a id="line-divisor"></a>

## 9. A line through three points

Now return to projective geometry.

Suppose a projective line

$$
L
$$

meets the elliptic curve at

$$
P,Q,R,
$$

counting intersection multiplicity.

Let its homogeneous linear equation be

$$
\ell(X,Y,Z)=0.
$$

The line at infinity is

$$
Z=0.
$$

Consider the rational function on \(E\)

$$
\frac{\ell}{Z}.
$$

Its zeros occur where

$$
\ell=0,
$$

namely at the intersections

$$
P,Q,R.
$$

Its poles occur where

$$
Z=0.
$$

For a Weierstrass cubic,

$$
Z=0
$$

meets \(E\) only at

$$
\mathcal O=(0:1:0)
$$

with total intersection multiplicity \(3\).

Therefore,

$$
\boxed{
\operatorname{div}\left(\frac{\ell}{Z}\right)
=
[P]+[Q]+[R]-3[\mathcal O].
}
$$

Since this is a principal divisor,

$$
[P]+[Q]+[R]-3[\mathcal O]
\sim0.
$$

Rearranging,

$$
([P]-[\mathcal O])
+
([Q]-[\mathcal O])
+
([R]-[\mathcal O])
=
0
$$

inside

$$
\operatorname{Pic}^0(E).
$$

Thus

$$
\boxed{
\Phi(P)+\Phi(Q)+\Phi(R)=0.
}
$$

This is the algebraic-geometric form of the familiar statement:

$$
\boxed{
P+Q+R=\mathcal O
}
$$

when \(P,Q,R\) are collinear.

---

<a id="recover-group-law"></a>

## 10. Recovering the chord-and-tangent law

Suppose the line through \(P\) and \(Q\) meets the cubic a third time at \(R\).

From the divisor relation,

$$
\Phi(P)+\Phi(Q)+\Phi(R)=0.
$$

Therefore,

$$
\Phi(P)+\Phi(Q)
=
-\Phi(R).
$$

But what point corresponds to

$$
-\Phi(R)?
$$

The answer is exactly the reflected point

$$
-R.
$$

Thus

$$
\Phi(P)+\Phi(Q)
=
\Phi(-R).
$$

Because \(\Phi\) is an isomorphism,

$$
\boxed{
P+Q=-R.
}
$$

So the familiar chord-and-tangent rule was not invented separately.

It is exactly the point-level translation of divisor-class addition.

The geometry and the algebra agree.

---

<a id="reflection-inverse"></a>

## 11. Why reflection gives the inverse

There is another beautiful divisor relation explaining why

$$
-(x,y)=(x,-y).
$$

Let

$$
R=(x_R,y_R).
$$

Then

$$
-R=(x_R,-y_R).
$$

Consider the rational function

$$
x-x_R.
$$

Its zeros occur at

$$
R
$$

and

$$
-R.
$$

At the point at infinity, \(x\) has a pole of order \(2\).

Therefore,

$$
\boxed{
\operatorname{div}(x-x_R)
=
[R]+[-R]-2[\mathcal O].
}
$$

Since this divisor is principal,

$$
([R]-[\mathcal O])
+
([-R]-[\mathcal O])
=
0.
$$

Thus

$$
\boxed{
\Phi(-R)
=
-\Phi(R).
}
$$

This proves algebraically that reflection across the \(x\)-axis corresponds exactly to group inversion.

So even the visual reflection rule is encoded naturally in divisor theory.

---

<a id="associativity-proof"></a>

## 12. Associativity now becomes automatic

We finally return to the original problem.

Take

$$
P,Q,R\in E.
$$

Under the map

$$
\Phi(P)=[P-\mathcal O],
$$

curve addition corresponds exactly to addition in

$$
\operatorname{Pic}^0(E).
$$

Therefore,

$$
\Phi((P+Q)+R)
=
\Phi(P+Q)+\Phi(R).
$$

Because \(\Phi\) respects addition,

$$
=
(\Phi(P)+\Phi(Q))+\Phi(R).
$$

But addition in

$$
\operatorname{Pic}^0(E)
$$

is associative:

$$
(\Phi(P)+\Phi(Q))+\Phi(R)
=
\Phi(P)+(\Phi(Q)+\Phi(R)).
$$

Therefore,

$$
=
\Phi(P)+\Phi(Q+R).
$$

Hence,

$$
=
\Phi(P+(Q+R)).
$$

Since \(\Phi\) is injective,

$$
\boxed{
(P+Q)+R
=
P+(Q+R).
}
$$

That is the conceptual proof.

The reason associativity holds is simply:

$$
\boxed{
\text{elliptic-curve addition}
=
\text{divisor-class addition}.
}
$$

And divisor-class addition is associative by construction.

---

<a id="tangencies"></a>

## 13. Tangencies and intersection multiplicity

The divisor argument automatically includes point doubling.

Suppose the tangent line at \(P\) intersects \(E\) again at \(R\).

The tangent has intersection multiplicity \(2\) at \(P\).

Therefore the zero divisor contributed by the line is

$$
2[P]+[R].
$$

Hence

$$
\boxed{
2[P]+[R]-3[\mathcal O]
}
$$

is principal.

Inside

$$
\operatorname{Pic}^0(E),
$$

this gives

$$
2([P]-[\mathcal O])
+
([R]-[\mathcal O])
=
0.
$$

So

$$
2\Phi(P)
=
-\Phi(R)
=
\Phi(-R).
$$

Therefore,

$$
\boxed{
2P=-R.
}
$$

This is exactly the tangent construction from Chapter II.

No new rule is required.

Intersection multiplicity automatically handles the repeated point.

---

### Flex points

An especially interesting case occurs when the tangent intersects the cubic with multiplicity \(3\) at the same point \(P\).

Then

$$
3[P]-3[\mathcal O]
$$

is principal.

Therefore,

$$
3([P]-[\mathcal O])=0.
$$

So

$$
\boxed{
3P=\mathcal O.
}
$$

Such a point is a \(3\)-torsion point.

This provides a beautiful connection between local intersection geometry and the algebraic order of a point.

---

<a id="conceptual-picture"></a>

## 14. What the proof is really saying

We can now compare the elementary and advanced viewpoints.

### Elementary viewpoint

Take two points:

$$
P,Q.
$$

Draw the line through them.

Find the third intersection:

$$
R.
$$

Reflect:

$$
P+Q=-R.
$$

This tells us **how to compute** the sum.

---

### Divisor viewpoint

A line gives the principal divisor

$$
[P]+[Q]+[R]-3[\mathcal O].
$$

Therefore,

$$
[P-\mathcal O]
+
[Q-\mathcal O]
+
[R-\mathcal O]
=
0.
$$

Hence,

$$
[P-\mathcal O]
+
[Q-\mathcal O]
=
[-R-\mathcal O].
$$

This tells us **why the operation is a group law**.

The two viewpoints answer different questions.

The chord-and-tangent picture explains the algorithm.

Divisor theory explains the structure.

---

### Why this is deeper than the coordinate formulas

The coordinate formulas depend on a particular Weierstrass equation.

Divisor theory does not.

Even if the curve is written in another coordinate system, the group structure remains.

Thus the true mathematical object is not the slope formula

$$
\lambda
=
\frac{y_2-y_1}{x_2-x_1}.
$$

That formula is merely one coordinate representation of a much more intrinsic operation.

The deeper structure is

$$
\boxed{
E
\cong
\operatorname{Pic}^0(E).
}
$$

---

<a id="bigger-picture"></a>

## 15. The bigger picture

We can now see the complete logical progression.

Start with a smooth projective cubic \(E\) and a distinguished point

$$
\mathcal O.
$$

Construct the degree-zero divisor group:

$$
\operatorname{Div}^0(E).
$$

Identify divisors differing by principal divisors:

$$
\operatorname{Pic}^0(E)
=
\operatorname{Div}^0(E)/
\operatorname{Prin}(E).
$$

For a genus-one curve with base point \(\mathcal O\),

$$
\boxed{
P
\longmapsto
[P-\mathcal O]
}
$$

gives

$$
\boxed{
E\cong\operatorname{Pic}^0(E).
}
$$

Now let a line meet the cubic at

$$
P,Q,R.
$$

Its divisor relation gives

$$
\boxed{
[P]+[Q]+[R]-3[\mathcal O]
\sim0.
}
$$

Therefore,

$$
\boxed{
P+Q+R=\mathcal O.
}
$$

Hence,

$$
\boxed{
P+Q=-R.
}
$$

And because this operation is inherited from the abelian group

$$
\operatorname{Pic}^0(E),
$$

we obtain

$$
\boxed{
(P+Q)+R=P+(Q+R).
}
$$

So the complete chain is

$$
\boxed{
\text{rational functions}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{principal divisors}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\operatorname{Pic}^0(E)
}
$$

$$
\Downarrow
$$

$$
\boxed{
E\cong\operatorname{Pic}^0(E)
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{chord-and-tangent group law}
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{associativity}.
}
$$

This is the deeper reason elliptic-curve addition works.

The group law is not an arbitrary geometric trick.

It is the visible form of a natural algebraic structure already attached to every smooth projective genus-one curve with a chosen rational point.

---

## Further reading

For a deeper treatment of the mathematics behind this chapter:

* Joseph H. Silverman, **The Arithmetic of Elliptic Curves**.
* Robin Hartshorne, **Algebraic Geometry**.
* William Fulton, **Algebraic Curves**.
* David A. Cox, John Little, and Donal O'Shea, **Ideals, Varieties, and Algorithms**.
* Lawrence C. Washington, **Elliptic Curves: Number Theory and Cryptography**.
* Jeffrey Hoffstein, Jill Pipher, and Joseph H. Silverman, **An Introduction to Mathematical Cryptography**.

---

The next chapter can now return to computation with a much stronger foundation.

We know not only **how** points add, but **why** their addition forms an abelian group.

The next natural setting is the finite field

$$
\mathbb F_p.
$$

There, the continuous real curve disappears and we obtain a finite abelian group

$$
E(\mathbb F_p).
$$

That raises a new collection of questions:

* How many points does the curve have?
* Why is the number close to \(p+1\)?
* What does Hasse's theorem tell us?
* What are point orders and subgroups?
* When is the group cyclic?
* How do we compute inside \(E(\mathbb F_p)\)?

Those questions lead directly from algebraic geometry toward the mathematics used in elliptic-curve cryptography.
