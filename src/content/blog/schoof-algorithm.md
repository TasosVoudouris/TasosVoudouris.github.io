---
title: "Elliptic Curve Mathematics XII: Schoof’s Algorithm and Frobenius Point Counting"
description: "A focused analysis of Schoof’s deterministic polynomial-time point-counting algorithm: Frobenius endomorphisms, division polynomials, symbolic torsion arithmetic, trace computation modulo small primes, and CRT reconstruction."
pubDate: "2025-05-27"
updatedDate: "2026-09-17"

topics:
  - "Elliptic Curve Theory"
  - "Elliptic-Curve Cryptography"
  - "Number Theory"
  - "Cryptographic Engineering"

tags:
  - "schoof"
  - "point-counting"
  - "frobenius"
  - "elliptic-curves"
  - "division-polynomials"
  - "chinese-remainder-theorem"

difficulty: "Advanced"
status: "Reviewed"
series: "Elliptic Curve Mathematics"
seriesOrder: 12
sourcePath: "experiments/ready-material/elliptic-curves"
draft: false
---

In Chapter VI we introduced the central point-counting identity

$$
\boxed{
\#E(\mathbb F_q)=q+1-t,
}
$$

where

$$
t
$$

is the **trace of Frobenius**.

Hasse's theorem tells us that

$$
\boxed{
|t|\leq2\sqrt q.
}
$$

In Chapter X we then developed division polynomials and saw how

$$
\psi_\ell
$$

provides an algebraic description of the $\ell$-torsion subgroup

$$
E[\ell].
$$

Schoof's algorithm combines these ideas.

Instead of enumerating points, it computes

$$
\boxed{
t\bmod\ell
}
$$

for several small primes $\ell$, reconstructs $t$ using the Chinese Remainder Theorem, and finally uses Hasse's bound to identify the unique integer trace.

This was a major breakthrough:

$$
\boxed{
\text{elliptic-curve point counting became deterministic polynomial time in }\log q.
}
$$

The algorithm is also an excellent example of how many apparently separate parts of elliptic-curve mathematics fit together:

$$
\boxed{
\text{Frobenius}
\rightarrow
\text{torsion}
\rightarrow
\text{division polynomials}
\rightarrow
\text{quotient rings}
\rightarrow
\text{CRT}
\rightarrow
\#E(\mathbb F_q).
}
$$

---

## Table of Contents

- [1. The point-counting problem](#1-the-point-counting-problem)
- [2. Why naive enumeration is not enough](#2-why-naive-enumeration-is-not-enough)
- [3. Hasse reduces the problem to computing $t$](#3-hasse-reduces-the-problem-to-computing-ttt)
- [4. The Frobenius endomorphism](#4-the-frobenius-endomorphism)
- [5. Frobenius characteristic equation](#5-frobenius-characteristic-equation)
- [6. Restricting Frobenius to $E\[\ell\]$](#6-restricting-frobenius-to-eℓeelleℓ)
- [7. Why computing $t\bmod\ell$ is enough](#7-why-computing-tmodℓtbmodelltmodℓ-is-enough)
- [8. Division polynomials as symbolic torsion](#8-division-polynomials-as-symbolic-torsion)
- [9. The quotient coordinate algebra](#9-the-quotient-coordinate-algebra)
- [10. Representing a generic $\ell$-torsion point](#10-representing-a-generic-ℓellℓ-torsion-point)
- [11. Computing Frobenius symbolically](#11-computing-frobenius-symbolically)
- [12. Solving for $t\bmod\ell$](#12-solving-for-tmodℓtbmodelltmodℓ)
- [13. The special case $\ell=2$](#13-the-special-case-ℓ2ell2ℓ2)
- [14. Zero divisors and factor discovery](#14-zero-divisors-and-factor-discovery)
- [15. Chinese Remainder reconstruction](#15-chinese-remainder-reconstruction)
- [16. Why $M>4\sqrt q$ is sufficient](#16-why-m4qm4sqrt-qm4q-is-sufficient)
- [17. Complete Schoof workflow](#17-complete-schoof-workflow)
- [18. Structure of the Sage implementation](#18-structure-of-the-sage-implementation)
- [19. The `trace_mod` routine](#19-the-trace_mod-routine)
- [20. The `Schoof` routine](#20-the-schoof-routine)
- [21. Testing and validation](#21-testing-and-validation)
- [22. Complexity](#22-complexity)
- [23. Why pure Schoof is mainly a reference implementation](#23-why-pure-schoof-is-mainly-a-reference-implementation)

---

## 1. The point-counting problem

Let

$$
E/\mathbb F_q
$$

be an elliptic curve.

We want to compute

$$
\boxed{
N=\#E(\mathbb F_q).
}
$$

For cryptographic curves this number is fundamental.

Once $N$ is known, we can factor it as

$$
N=hr,
$$

where $r$ may be a large prime subgroup order and $h$ the cofactor.

This information determines:

* subgroup sizes;
* possible point orders;
* cofactors;
* whether the group has cryptographically useful structure;
* whether special weak cases occur.

Point counting is therefore part of **curve parameter generation and validation**, rather than merely an abstract number-theoretic exercise.

---

<a id="naive-enumeration"></a>

## 2. Why naive enumeration is not enough

For

$$
E:
y^2=x^3+Ax+B,
$$

one could iterate through every

$$
x\in\mathbb F_q
$$

and test whether

$$
x^3+Ax+B
$$

has a square root.

For small fields this is perfectly reasonable.

But the algorithm requires roughly

$$
O(q)
$$

field-scale work.

The input $q$, however, occupies only

$$
O(\log q)
$$

bits.

Therefore enumeration is exponential in the bit length of the field size.

For a cryptographic-sized prime field, this is hopeless.

Schoof's key achievement was to replace dependence polynomial in $q$ with dependence polynomial in

$$
\boxed{
\log q.
}
$$

---

<a id="hasse-trace"></a>

## 3. Hasse reduces the problem to computing $t$

Define

$$
\boxed{
t=q+1-\#E(\mathbb F_q).
}
$$

Then

$$
\boxed{
\#E(\mathbb F_q)=q+1-t.
}
$$

Hasse's theorem gives

$$
\boxed{
|t|\leq2\sqrt q.
}
$$

Therefore

$$
t
$$

lies in the interval

$$
[-2\sqrt q,2\sqrt q].
$$

Instead of counting all points, Schoof computes enough modular information to determine which integer in this interval is the true trace.

This changes the problem fundamentally.

---

<a id="frobenius"></a>

## 4. The Frobenius endomorphism

Define the $q$-power Frobenius map

$$
\boxed{
\pi:E\rightarrow E
}
$$

by

$$
\boxed{
\pi(x,y)
=
(x^q,y^q).
}
$$

Because the curve coefficients lie in

$$
\mathbb F_q,
$$

Frobenius preserves the curve equation.

A point is rational over the base field exactly when

$$
\pi(P)=P.
$$

Therefore

$$
\boxed{
E(\mathbb F_q)
=
\ker(\pi-[1])
}
$$

in the appropriate algebraic-geometric sense.

Point counting is therefore naturally tied to the structure of Frobenius.

---

<a id="frobenius-equation"></a>

## 5. Frobenius characteristic equation

The Frobenius endomorphism satisfies

$$
\boxed{
\pi^2-[t]\pi+[q]=0
}
$$

inside

$$
\operatorname{End}(E).
$$

This notation is important.

The term

$$
[q]
$$

means the multiplication-by-$q$ endomorphism, not merely the integer $q$.

Applying the equation to a point $P$,

$$
\boxed{
\pi^2(P)+[q]P
=
[t]\pi(P).
}
$$

This equation is the computational heart of Schoof's algorithm.

If we can determine $t$ modulo enough small primes, we can reconstruct $t$ completely.

---

<a id="frobenius-torsion"></a>

## 6. Restricting Frobenius to $E[\ell]$

Take a small prime

$$
\ell\neq\operatorname{char}(\mathbb F_q).
$$

Then

$$
\boxed{
E[\ell]
\cong
(\mathbb Z/\ell\mathbb Z)^2.
}
$$

For every

$$
P\in E[\ell],
$$

we have

$$
[\ell]P=\mathcal O.
$$

Therefore integer scalar multiplication on $E[\ell]$ depends only on the scalar modulo $\ell$.

So

$$
[t]P
$$

depends only on

$$
t\bmod\ell.
$$

Likewise,

$$
[q]P
=
[q\bmod\ell]P.
$$

Hence the Frobenius equation on $E[\ell]$ becomes

$$
\boxed{
\pi^2(P)
+
[q\bmod\ell]P
=
[t\bmod\ell]\pi(P).
}
$$

This converts the global trace problem into a collection of small modular problems.

---

<a id="trace-mod-ell"></a>

## 7. Why computing $t\bmod\ell$ is enough

Choose distinct small primes

$$
\ell_1,\ldots,\ell_s
$$

and compute

$$
t_i
\equiv
t
\pmod{\ell_i}.
$$

Let

$$
M
=
\prod_{i=1}^{s}\ell_i.
$$

The Chinese Remainder Theorem determines a unique residue

$$
t\bmod M.
$$

If

$$
M>4\sqrt q,
$$

then only one representative of that residue can lie inside the Hasse interval

$$
[-2\sqrt q,2\sqrt q].
$$

Thus the exact trace is recovered.

This gives the high-level Schoof architecture:

$$
\boxed{
t\bmod\ell_1
}
$$

$$
\boxed{
t\bmod\ell_2
}
$$

$$
\vdots
$$

$$
\boxed{
t\bmod\ell_s
}
$$

$$
\Downarrow
$$

$$
\boxed{
\text{CRT}
}
$$

$$
\Downarrow
$$

$$
\boxed{
t
}
$$

$$
\Downarrow
$$

$$
\boxed{
\#E(\mathbb F_q)=q+1-t.
}
$$

---

<a id="division-polynomials"></a>

## 8. Division polynomials as symbolic torsion

Chapter X introduced the $\ell$-division polynomial

$$
\psi_\ell.
$$

For odd

$$
\ell\neq\operatorname{char}(\mathbb F_q),
$$

its roots are the $x$-coordinates of the nonzero $\ell$-torsion points.

Thus

$$
\boxed{
\psi_\ell(x)=0
}
$$

represents the condition

$$
\boxed{
[\ell]P=\mathcal O.
}
$$

Instead of explicitly constructing every torsion point in a large extension field, Schoof works modulo

$$
\psi_\ell.
$$

This allows us to manipulate a **generic $\ell$-torsion point symbolically**.

That is the central computational trick.

---

<a id="quotient-algebra"></a>

## 9. The quotient coordinate algebra

Let

$$
h(x)=\psi_\ell(x).
$$

We can work in

$$
\boxed{
R_x
=
\mathbb F_q[x]/(h(x)).
}
$$

Inside this quotient,

$$
h(x)=0.
$$

Thus the formal element $x$ behaves like the $x$-coordinate of a generic $\ell$-torsion point.

To retain the $y$-coordinate, impose

$$
y^2=x^3+Ax+B.
$$

Conceptually we work in

$$
\boxed{
R
=
\mathbb F_q[x,y]
/
\left(
h(x),
y^2-x^3-Ax-B
\right).
}
$$

Every expression can then be reduced to the form

$$
\boxed{
a(x)+b(x)y.
}
$$

This representation is particularly useful because every higher power of $y$ can be reduced using

$$
y^2=x^3+Ax+B.
$$

---

<a id="generic-torsion-point"></a>

## 10. Representing a generic $\ell$-torsion point

The implementation represents symbolic point coordinates using elements of the quotient algebra.

A typical coordinate has the form

$$
a(x)+b(x)y.
$$

For symmetry reasons, many expressions separate naturally into:

* an $x$-part in $R_x$;
* a $y$-part of the form $b(x)y$.

Thus the generic point can be manipulated symbolically without ever finding a concrete root of

$$
\psi_\ell.
$$

This distinction matters:

> We are not literally enumerating $E[\ell]$.

Instead,

$$
\boxed{
\text{we compute identities that hold simultaneously on the roots of }\psi_\ell.
}
$$

That is what makes the approach polynomial-time.

---

<a id="symbolic-frobenius"></a>

## 11. Computing Frobenius symbolically

For the generic point

$$
P=(x,y),
$$

Frobenius gives

$$
\boxed{
\pi(P)
=
(x^q,y^q).
}
$$

All of this arithmetic is reduced modulo

$$
\psi_\ell(x).
$$

Thus

$$
x^q
$$

is computed as

$$
x^q\bmod\psi_\ell(x).
$$

For the $y$-coordinate,

$$
y^q
=
y(y^2)^{(q-1)/2}
$$

when $q$ is odd.

Using

$$
y^2=x^3+Ax+B,
$$

we obtain

$$
\boxed{
y^q
=
y
\left(
x^3+Ax+B
\right)^{(q-1)/2}.
}
$$

Again the polynomial factor is reduced modulo

$$
\psi_\ell.
$$

The second Frobenius iteration is

$$
\boxed{
\pi^2(P)
=
(x^{q^2},y^{q^2}).
}
$$

Repeated modular exponentiation allows these expressions to be computed without constructing the enormous exponents explicitly.

---

<a id="solve-trace"></a>

## 12. Solving for $t\bmod\ell$

On $E[\ell]$,

$$
\pi^2-[t]\pi+[q]=0.
$$

Thus for a generic $\ell$-torsion point $P$,

$$
\boxed{
\pi^2(P)+[q]P
=
[t]\pi(P).
}
$$

Reduce

$$
q
$$

modulo $\ell$:

$$
q_\ell
=
q\bmod\ell.
$$

Then compute

$$
\pi^2(P)+[q_\ell]P.
$$

Now test candidate values

$$
\tau\in\mathbb Z/\ell\mathbb Z
$$

until

$$
\boxed{
[\tau]\pi(P)
=
\pi^2(P)+[q_\ell]P.
}
$$

The successful value satisfies

$$
\boxed{
\tau\equiv t\pmod\ell.
}
$$

Since $\ell$ is deliberately small, trying candidate residues is feasible.

More refined formulations reduce the number of cases or exploit additional algebraic structure, but this is the central idea.

---

<a id="ell-two"></a>

## 13. The special case $\ell=2$

The prime $2$ is usually handled separately.

Recall that nontrivial $2$-torsion points have

$$
y=0.
$$

Therefore they correspond to roots of

$$
\boxed{
x^3+Ax+B.
}
$$

A rational nontrivial $2$-torsion point exists exactly when this cubic has a root in

$$
\mathbb F_q.
$$

This reveals the parity of

$$
\#E(\mathbb F_q).
$$

Since

$$
\#E(\mathbb F_q)=q+1-t,
$$

we can determine

$$
\boxed{
t\bmod2.
}
$$

For odd $q$, this becomes the first modular trace component used in reconstruction.

---

<a id="zero-divisors"></a>

## 14. Zero divisors and factor discovery

There is an implementation subtlety that deserves careful explanation.

The ring

$$
\mathbb F_q[x]/(\psi_\ell)
$$

is not necessarily a field.

If

$$
\psi_\ell
$$

is reducible, the quotient may contain zero divisors.

Suppose a group-law computation requires division by some polynomial

$$
d(x).
$$

An inverse exists only if

$$
\gcd(d(x),\psi_\ell(x))=1.
$$

If the inverse fails to exist, this does not merely mean:

> “Something went wrong.”

Instead, computing

$$
\boxed{
g(x)
=
\gcd(d(x),\psi_\ell(x))
}
$$

may reveal a nontrivial factor

$$
1<\deg g<\deg\psi_\ell.
$$

The computation can then continue on a smaller factor.

This is the mathematical reason the reference script contains logic for failed modular inversion and gcd-based reduction.

So a `ZeroDivisionError` in this symbolic context can expose algebraic information about the division polynomial.

It is not analogous to an arbitrary floating-point software failure.

---

<a id="crt"></a>

## 15. Chinese Remainder reconstruction

Suppose we know

$$
t\equiv a\pmod M
$$

and compute

$$
t\equiv b\pmod\ell,
$$

with

$$
\gcd(M,\ell)=1.
$$

We want the combined residue modulo

$$
M\ell.
$$

One convenient construction is

$$
\boxed{
t'
=
a
+
M
\left(
(b-a)M^{-1}\bmod\ell
\right).
}
$$

Then

$$
t'\equiv a\pmod M
$$

and

$$
t'\equiv b\pmod\ell.
$$

Reduce $t'$ modulo

$$
M\ell
$$

and update

$$
M\leftarrow M\ell.
$$

This process is repeated for every small prime.

---

<a id="crt-bound"></a>

## 16. Why $M>4\sqrt q$ is sufficient

The trace lies in

$$
[-2\sqrt q,2\sqrt q].
$$

The width of this interval is

$$
4\sqrt q.
$$

Suppose two distinct integers

$$
t_1,t_2
$$

inside the interval had the same residue modulo $M$.

Then

$$
M\mid(t_1-t_2).
$$

But

$$
|t_1-t_2|
\leq4\sqrt q.
$$

If

$$
\boxed{
M>4\sqrt q,
}
$$

the only multiple of $M$ with magnitude at most $4\sqrt q$ is zero.

Therefore

$$
t_1=t_2.
$$

So the residue modulo $M$ uniquely determines $t$.

This is the precise reason behind Schoof's stopping condition.

---

<a id="schoof-workflow"></a>

## 17. Complete Schoof workflow

We can now state the entire algorithm conceptually.

### Input

An elliptic curve

$$
E/\mathbb F_q.
$$

### Output

$$
\#E(\mathbb F_q).
$$

### Procedure

1. Define

   $$
   t=q+1-\#E(\mathbb F_q).
   $$

2. Use Hasse:

   $$
   |t|\leq2\sqrt q.
   $$

3. Initialize

   $$
   M=1.
   $$

4. Iterate through small primes

   $$
   \ell\neq\operatorname{char}\mathbb F_q.
   $$

5. Compute

   $$
   \psi_\ell.
   $$

6. Work symbolically on

   $$
   E[\ell].
   $$

7. Compute Frobenius:

   $$
   \pi(P),
   \qquad
   \pi^2(P).
   $$

8. Use

   $$
   \pi^2(P)+[q]P=[t]\pi(P)
   $$

   to determine

   $$
   t\bmod\ell.
   $$

9. Merge the residue using CRT.

10. Update

    $$
    M\leftarrow M\ell.
    $$

11. Continue until

    $$
    M>4\sqrt q.
    $$

12. Choose the unique centered representative satisfying

    $$
    |t|\leq2\sqrt q.
    $$

13. Return

    $$
    \boxed{
    \#E(\mathbb F_q)=q+1-t.
    }
    $$

This is Schoof's algorithm at its conceptual core.

---

<a id="sage-structure"></a>

## 18. Structure of the Sage implementation

The companion script

```text
src/schoofs_algorithm.sage
```

implements the same mathematical pipeline.

Its helper routines correspond to distinct pieces of elliptic-curve arithmetic.

---

### `add(P, Q, A, f)`

This performs symbolic point addition modulo a polynomial $f$.

Conceptually,

$$
\boxed{
P,Q
\longmapsto
P+Q
}
$$

inside the quotient coordinate algebra.

Any required inverse is computed modulo $f$.

If the denominator is not invertible, the implementation can inspect its gcd with $f$.

---

### `dbl(P, A, f)`

This computes

$$
\boxed{
[2]P
}
$$

symbolically.

The affine slope is

$$
\lambda
=
\frac{3x^2+A}{2y}.
$$

But all arithmetic is interpreted inside the quotient algebra associated with the torsion polynomial.

Again, failure to invert a denominator may reveal a factor of $f$.

---

### `smul(n, P, A, f)`

This computes

$$
\boxed{
[n]P
}
$$

using double-and-add.

So even though Schoof is a point-counting algorithm, ordinary scalar multiplication remains one of its internal primitives.

---

### Symbolic endomorphism helpers

Additional helpers manipulate the symbolic Frobenius representation and its compositions.

The important mathematical distinction is that the quotient-ring pairs are **coordinate representations of symbolic points or images of points**.

They should not be confused with arbitrary elements of the abstract endomorphism ring

$$
\operatorname{End}(E)
$$

itself.

The actual endomorphisms of interest are maps such as

$$
\pi,
\qquad
\pi^2,
\qquad
[n].
$$

The quotient-ring representation lets us evaluate those maps on generic torsion points.

---

<a id="trace-mod-routine"></a>

## 19. The `trace_mod` routine

The central subroutine has the conceptual interface

```python
trace_mod(E, ell)
```

and returns

$$
\boxed{
t\bmod\ell.
}
$$

Its mathematical workflow is:

### Step 1 — Division polynomial

Compute

$$
\psi_\ell.
$$

Set

$$
h(x)=\psi_\ell(x).
$$

---

### Step 2 — Quotient algebra

Construct arithmetic modulo

$$
h(x).
$$

This represents generic $\ell$-torsion $x$-coordinates.

---

### Step 3 — Frobenius

Compute

$$
\pi(P)
=
(x^q,y^q)
$$

and

$$
\pi^2(P)
=
(x^{q^2},y^{q^2}).
$$

---

### Step 4 — Scalar $q\bmod\ell$

Compute

$$
[q\bmod\ell]P.
$$

---

### Step 5 — Frobenius equation

Form

$$
\pi^2(P)+[q]P.
$$

Find

$$
\tau\in\mathbb Z/\ell\mathbb Z
$$

such that

$$
[\tau]\pi(P)
=
\pi^2(P)+[q]P.
$$

Then

$$
\boxed{
\tau=t\bmod\ell.
}
$$

---

### Step 6 — Factor handling

If a denominator becomes a zero divisor modulo $h$, compute a gcd.

When a nontrivial factor is found, the symbolic calculation may continue modulo the smaller factor.

This is an implementation strategy for handling reducible division-polynomial components.

---

<a id="schoof-routine"></a>

## 20. The `Schoof` routine

The top-level routine

```python
Schoof(E)
```

combines all modular traces.

Conceptually:

```text
M = 1
T = 0

for small primes ell != characteristic:
    t_ell = trace_mod(E, ell)

    combine:
        T ≡ old T       (mod M)
        T ≡ t_ell       (mod ell)

    M = M * ell

    if M > 4*sqrt(q):
        stop
```

Finally choose the representative of $T\bmod M$ satisfying

$$
\boxed{
|T|\leq2\sqrt q.
}
$$

The curve cardinality is then

$$
\boxed{
q+1-T.
}
$$

---

<a id="testing"></a>

## 21. Testing and validation

A reference implementation should always be checked against an independent implementation.

For example:

```python
FF = GF(next_prime(2^80))

E = EllipticCurve(
    FF,
    [FF(314159), FF(2781828)]
)

t_reference = E.trace_of_frobenius()
t_schoof = Schoof(E)

print("Sage trace:", t_reference)
print("Our trace:", t_schoof)

assert t_reference == t_schoof
assert E.cardinality() == FF.order() + 1 - t_schoof
```

For development, smaller fields are preferable because:

* failures are easier to inspect;
* division polynomials remain manageable;
* intermediate traces can be checked manually;
* execution times remain reasonable.

Useful test sizes include primes around:

$$
2^8,
\quad
2^{16},
\quad
2^{32},
$$

before attempting larger experiments.

---

### A large-field stress experiment

The original script also contains experiments of the form:

```python
FF = GF(next_prime(2^256))

E = EllipticCurve(
    FF,
    [FF(3141), FF(2781828)]
)

time t = Schoof(E)

print(t)
```

This is useful as a **stress test or research experiment**.

It should not be interpreted as evidence that the educational pure-Schoof implementation is a competitive production point counter for arbitrary 256-bit curves.

That distinction matters.

---

<a id="complexity"></a>

## 22. Complexity

The central theoretical result is:

$$
\boxed{
\text{Schoof runs in deterministic polynomial time in }\log q.
}
$$

Why?

The primes $\ell$ required are small.

Since

$$
\prod\ell>4\sqrt q,
$$

the relevant primes are only of size polynomial in

$$
\log q.
$$

For each $\ell$,

$$
\deg\psi_\ell
=
O(\ell^2).
$$

Thus the quotient-ring computations also have degree polynomial in

$$
\log q.
$$

The exact complexity depends strongly on the model used for:

* integer multiplication;
* polynomial multiplication;
* modular composition;
* finite-field arithmetic.

With straightforward classical arithmetic, a traditional bound commonly quoted for Schoof is roughly

$$
\boxed{
O(\log^8 q)
}
$$

bit operations.

With fast integer and polynomial arithmetic, the complexity can be reduced to approximately

$$
\boxed{
\widetilde O(\log^5 q),
}
$$

with logarithmic factors suppressed.

The key point is not the exact exponent.

The historical breakthrough is:

$$
\boxed{
\text{polynomial in }\log q.
}
$$

So the earlier claim

$$
O(\log^3 q)
$$

should not be used for this implementation.

---

<a id="practicality"></a>

## 23. Why pure Schoof is mainly a reference implementation

Schoof's algorithm is extraordinarily important theoretically.

But the original algorithm is not generally the preferred point-counting method for modern large-prime cryptographic curves.

Why?

Because working modulo the full division polynomial

$$
\psi_\ell
$$

means manipulating polynomials of degree approximately

$$
\frac{\ell^2}{2}.
$$

That becomes expensive.

So the pure algorithm is particularly valuable for:

* education;
* mathematical verification;
