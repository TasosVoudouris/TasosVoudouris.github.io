---
title: 'RSA Deep Dive VI: Boneh–Durfee From Zero — Small Private Exponents as a Bivariate Lattice Problem'
description: Boneh–Durfee pushes the study of unusually small RSA private exponents beyond Wiener's continued fractions by turning the RSA key equation into a bivariate small-root problem. We derive the polynomial, connect it to Coppersmith and LLL, explain the 0.292 bound, and separate proved structure from heuristic multivariate recovery.
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Lattice Methods
tags:
- rsa
- boneh-durfee
- coppersmith
- lll
- lattices
- small-private-exponent
- cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 6
draft: false
---
The previous two RSA deep dives were deliberately arranged in this order.

First, Wiener showed us that an unusually small private exponent can leak through a rational approximation:

$$
\frac{k}{d}
\approx
\frac{e}{N}.
$$

Then Coppersmith forced us to learn a more general language:

```text
small unknown
+
modular polynomial relation
+
lattice reduction
=
recoverable algebraic information
```

Now the two paths meet.

Boneh and Durfee ask a very specific scientific question:

> If the RSA private exponent is too small for ordinary key generation, but no longer small enough for Wiener's continued-fraction argument, can the RSA key equation still be converted into a tractable small-root problem?

The answer is yes in an important asymptotic regime.

Their classical result extends the small-private-exponent analysis from the quarter-power region toward

$$
d < N^{0.292\ldots}.
$$

But the number `0.292` is not the interesting part by itself.

The real point is the modelling step:

```text
RSA key equation
        ↓
two small unknowns
        ↓
bivariate modular polynomial
        ↓
shifted polynomial lattice
        ↓
LLL
        ↓
small integer relations
        ↓
candidate root recovery
```

That is what I want to understand here.

If you want the prerequisites first:

- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Wiener's Attack From Zero](/blog/16-rsa-wiener-attack/)
- [Coppersmith From Zero](/blog/17-rsa-coppersmith-from-zero/)

![Boneh–Durfee scientific pipeline from the RSA key equation to a bivariate lattice problem](/images/blog/18-rsa-boneh-durfee.svg)

*Boneh–Durfee does not begin with “LLL breaks RSA.” It begins by rewriting one exact RSA relation until the hidden quantities appear as a small modular root.*

---

## 1. Start from the RSA key equation

For a textbook two-prime RSA modulus

$$
N=pq,
$$

Euler's totient is

$$
\varphi(N)
=
(p-1)(q-1)
=
N-p-q+1.
$$

In the classical small-$d$ analysis we write

$$
ed\equiv1\pmod{\varphi(N)}.
$$

Therefore there exists an integer $k$ such that

$$
ed-k\varphi(N)=1.
$$

Equivalently,

$$
ed=1+k\varphi(N).
$$

Substitute

$$
\varphi(N)=N+1-(p+q):
$$

$$
ed
=
1+k\bigl(N+1-(p+q)\bigr).
$$

Now define

$$
A=\frac{N+1}{2},
$$

and introduce two unknowns

$$
x_0=2k,
\qquad
y_0=-\frac{p+q}{2}.
$$

Then

$$
A+y_0
=
\frac{N+1-(p+q)}{2}
=
\frac{\varphi(N)}{2}.
$$

Therefore

$$
1+x_0(A+y_0)
=
1+2k\frac{\varphi(N)}{2}
=
1+k\varphi(N)
=
ed.
$$

Reduce modulo the public exponent $e$:

$$
\boxed{
1+x_0(A+y_0)\equiv0\pmod e.
}
$$

So define the bivariate polynomial

$$
\boxed{
f(x,y)=1+x(A+y).
}
$$

The hidden pair $(x_0,y_0)$ satisfies

$$
f(x_0,y_0)\equiv0\pmod e.
$$

This is the central transformation.

We have not solved RSA.

We have changed the representation of the problem.

That distinction matters.

---

## 2. Why are both unknowns small?

A polynomial congruence is not automatically useful.

Coppersmith-style reasoning becomes interesting when the hidden root is small relative to the modulus.

Suppose the private exponent satisfies

$$
d<N^\delta.
$$

For balanced RSA primes,

$$
p\approx q\approx\sqrt N,
$$

so

$$
p+q=O(\sqrt N).
$$

Hence

$$
|y_0|
=
\frac{p+q}{2}
=
O(N^{1/2}).
$$

Now consider $k$.

From

$$
ed=1+k\varphi(N),
$$

we have

$$
k=\frac{ed-1}{\varphi(N)}.
$$

For ordinary balanced RSA,

$$
\varphi(N)\approx N.
$$

In the small-private-exponent setting considered by Boneh–Durfee, the public exponent is of the same order as $N$:

$$
e\approx N.
$$

So, ignoring constant factors,

$$
k\approx d.
$$

Therefore

$$
|x_0|=|2k|=O(N^\delta).
$$

The problem has now become:

$$
f(x_0,y_0)\equiv0\pmod e,
$$

with approximate bounds

$$
|x_0|<X\approx e^\delta,
$$

and

$$
|y_0|<Y\approx e^{1/2}.
$$

This is the **small inverse problem** that sits behind Boneh–Durfee.

It is already a major conceptual step.

Wiener used one unusually good rational approximation.

Boneh–Durfee exposes **two bounded algebraic unknowns**.

---

## 3. A small parameter study before touching lattices

I want one completely auditable example before the high-dimensional part.

Take the deliberately tiny research parameters

$$
p=30\,011,
\qquad
q=35\,027.
$$

Then

$$
N=pq=1\,051\,195\,297,
$$

and

$$
\varphi(N)
=
(p-1)(q-1)
=
1\,051\,130\,260.
$$

Choose the intentionally abnormal private exponent

$$
d=263.
$$

Its inverse modulo $\varphi(N)$ gives

$$
e=1\,047\,133\,567.
$$

Indeed,

$$
ed-1
=
k\varphi(N)
$$

with

$$
k=262.
$$

So the Boneh–Durfee variables are

$$
x_0=2k=524,
$$

and

$$
y_0=-\frac{p+q}{2}
=-32\,519.
$$

Also,

$$
A=\frac{N+1}{2}
=
525\,597\,649.
$$

Now evaluate the polynomial:

$$
f(x_0,y_0)
=
1+524(525\,597\,649-32\,519).
$$

The result is

$$
275\,396\,128\,121.
$$

But

$$
ed
=
1\,047\,133\,567\cdot263
=
275\,396\,128\,121.
$$

Therefore

$$
\boxed{
f(x_0,y_0)=ed
}
$$

and hence

$$
\boxed{
f(x_0,y_0)\equiv0\pmod e.
}
$$

The model is exact.

Now compare scales.

For this toy modulus,

$$
N^{1/4}\approx180.06,
$$

while

$$
N^{0.292}\approx430.86.
$$

Our chosen exponent is

$$
d=263.
$$

So numerically,

$$
N^{1/4}<d<N^{0.292}.
$$

This is why it is a useful teaching point: it sits outside the simple quarter-power picture but inside the famous Boneh–Durfee exponent range.

That is **not** a claim that a finite toy lattice must automatically succeed at exactly this boundary.

The $0.292$ result is asymptotic.

That distinction will become important soon.

A small companion script in the package checks these identities directly. It is a **model-check script**, not generic recovery code.

---

## 4. Why Wiener's continued fractions are no longer the right object

Wiener's reasoning starts from

$$
ed-k\varphi(N)=1,
$$

and turns it into an approximation of the form

$$
\frac{k}{d}
\approx
\frac{e}{N}.
$$

If $d$ is sufficiently small, continued fractions are forced to reveal $k/d$ as a convergent of $e/N$.

That is beautifully low-dimensional.

But once $d$ grows, the approximation is no longer strong enough to force the correct denominator into the convergent sequence.

Boneh–Durfee keeps more of the RSA equation instead of compressing everything into one fraction.

The hidden information becomes

$$
(x_0,y_0)
=
\left(
2k,
-\frac{p+q}{2}
\right),
$$

inside

$$
f(x,y)=1+x(A+y).
$$

So the scientific transition is:

```text
Wiener
one rational approximation
continued fractions
roughly quarter-power regime

            ↓

Boneh–Durfee
two bounded unknowns
bivariate polynomial
higher-dimensional lattice reduction
larger asymptotic small-d regime
```

This is not “a stronger version of continued fractions” in a superficial sense.

It is a different mathematical model of the same RSA key relation.

---

## 5. Reusing the Coppersmith idea

From the previous deep dive, our basic Coppersmith pattern was:

$$
f(x_0)\equiv0\pmod N
$$

plus a small bound on $x_0$.

Then we manufactured polynomials that vanished modulo a higher power of the modulus, scaled the variables, encoded coefficients as lattice vectors, and used LLL to search for a sufficiently short integer combination.

Boneh–Durfee uses the same philosophy, but now the polynomial has **two variables**.

Let

$$
f(x,y)=1+x(A+y).
$$

Because

$$
f(x_0,y_0)\equiv0\pmod e,
$$

we can construct shifted polynomials such as

$$
g_{i,j}(x,y)
=
x^i f(x,y)^j e^{m-j}.
$$

At the hidden root,

$$
f(x_0,y_0)^j
$$

contains a factor $e^j$.

Therefore

$$
g_{i,j}(x_0,y_0)
\equiv0\pmod{e^m}.
$$

We may also introduce carefully selected $y$-shifts of the same basic form.

The exact shift set is where the cryptanalytic design work begins.

Now scale the unknowns:

$$
x\mapsto Xx,
\qquad
y\mapsto Yy,
$$

with

$$
X\approx e^\delta,
\qquad
Y\approx e^{1/2}.
$$

Each shifted polynomial becomes a coefficient vector.

Those vectors form a lattice basis.

LLL then searches for short integer combinations.

The hope is that a sufficiently short combination corresponds to a polynomial $h(x,y)$ for which:

1. $e^m$ divides $h(x_0,y_0)$;
2. the coefficient norm is small enough to force

$$
|h(x_0,y_0)|<e^m.
$$

The only integer divisible by $e^m$ with absolute value below $e^m$ is zero.

So we obtain

$$
\boxed{
h(x_0,y_0)=0
}
$$

over the integers.

That is the same modular-to-integer bridge we built in the previous article.

The new difficulty is that one integer polynomial in two variables is not normally enough.

---

## 6. The multivariate difficulty: one short vector is not enough

This is one of the places where I do not want to hide behind a library call.

Suppose LLL gives one polynomial

$$
h_1(x,y)
$$

such that

$$
h_1(x_0,y_0)=0.
$$

That describes an algebraic curve.

It does not uniquely determine one pair $(x_0,y_0)$.

We need additional independent information.

Ideally LLL gives another polynomial

$$
h_2(x,y)
$$

with

$$
h_2(x_0,y_0)=0.
$$

If $h_1$ and $h_2$ are algebraically independent enough, we can eliminate one variable with a resultant or use a Gröbner-basis style computation.

Conceptually:

$$
h_1(x,y)=0,
$$

$$
h_2(x,y)=0
$$

lead to

$$
\operatorname{Res}_y(h_1,h_2)=0.
$$

That gives a univariate polynomial in $x$.

Recover a candidate $x_0$.

Substitute it back.

Recover $y_0$.

Then validate everything against the original RSA equations.

But here is the scientific caveat:

> LLL producing several short vectors does not automatically prove that the corresponding polynomials are algebraically independent.

This is one of the main differences between the very clean univariate Coppersmith theorem and practical multivariate constructions.

The lattice geometry can tell us that short combinations exist.

The algebraic post-processing still needs enough independent relations.

That is why multivariate Coppersmith claims must always state their assumptions carefully.

---

## 7. Herrmann–May: unravel the nonlinear monomial

The original Boneh–Durfee lattice analysis is subtle.

A particularly useful later reformulation is due to Herrmann and May.

Expand

$$
f(x,y):
$$

$$
f(x,y)
=
1+Ax+xy.
$$

The awkward part is the product

$$
xy.
$$

Introduce a new variable

$$
\boxed{
u=xy+1.
}
$$

Then

$$
f(x,y)
=
u+Ax.
$$

So define

$$
\boxed{
\bar f(u,x)=u+Ax.
}
$$

At first this looks suspiciously easy.

We turned a bivariate nonlinear polynomial into a linear polynomial.

But we did **not** delete the old structure.

The substitution also creates the relation

$$
\boxed{
xy=u-1.
}
$$

That relation has to be respected whenever monomials are reduced.

Herrmann–May use this “unravelled linearization” to organize the shift lattice in a cleaner way.

Typical $x$-shifts have the form

$$
\bar g_{i,k}(u,x)
=
x^i\bar f(u,x)^k e^{m-k},
$$

and selected $y$-shifts are added to improve the attainable bound.

Whenever terms such as $xy$ appear, the quotient relation

$$
xy=u-1
$$

is used to rewrite them.

The point is not that linearization magically solves the problem.

The point is that it makes the monomial structure and determinant analysis much more manageable.

This is a recurring theme in lattice cryptanalysis:

```text
algebraic modelling
        ↓
choose useful monomials
        ↓
choose useful shifts
        ↓
control lattice volume
        ↓
make LLL's guarantee strong enough
```

The lattice is designed.

It is not merely “sent to LLL.”

---

## 8. Where the famous $0.292$ comes from

Now we can finally interpret the number.

Assume the usual balanced-RSA small-secret-exponent setting with

$$
e\approx N,
$$

and write

$$
d<N^\delta.
$$

Then the root bounds behave asymptotically like

$$
X\approx e^\delta,
$$

and

$$
Y\approx e^{1/2}.
$$

The lattice is parameterized by an integer $m$ and a number of selected $y$-shifts $t$.

Write asymptotically

$$
t=\tau m.
$$

In the Herrmann–May style analysis, the determinant condition is optimized by choosing

$$
\tau=1-2\delta.
$$

After inserting the root bounds into the asymptotic determinant inequality, the relevant condition reduces to

$$
-\frac13\delta^2
+
\frac23\delta
-
\frac16
<0.
$$

Multiply by $-6$ and reverse the inequality:

$$
2\delta^2-4\delta+1>0.
$$

The smaller root is

$$
\delta
=
1-\frac{1}{\sqrt2}.
$$

Therefore the interesting range is

$$
\boxed{
\delta
<
1-\frac{1}{\sqrt2}
\approx
0.292893.
}
$$

So the famous slogan becomes

$$
\boxed{
d<N^{0.292\ldots}.
}
$$

There was also a simpler Boneh–Durfee lattice analysis giving a weaker exponent near $0.284$.

The refined sublattice analysis reaches the better-known $0.292$ value.

### But do not read this as a hard finite-size cliff

The statement

```text
delta = 0.291  -> always easy
delta = 0.293  -> always impossible
```

is wrong.

The bound is asymptotic.

Practical behavior depends on:

- lattice dimension,
- shift selection,
- scaling,
- basis conditioning,
- reduction quality,
- finite-size constants,
- algebraic independence of the recovered polynomials,
- root-extraction strategy.

Close to the theoretical exponent, the required lattice dimensions can become very large.

So the correct interpretation is:

> $0.292$ describes the asymptotic small-secret-exponent region achieved by the Boneh–Durfee analysis under its stated modelling assumptions. It is not a universal practical threshold for every finite RSA instance.

That sentence is much more useful than memorizing `0.292`.

---

## 9. If the small root is known, RSA reconstruction is elementary

The lattice stage is the sophisticated part.

Once the correct root is available, the remaining algebra is simple.

Recall

$$
x_0=2k,
$$

so

$$
k=\frac{x_0}{2}.
$$

And

$$
y_0=-\frac{p+q}{2},
$$

so

$$
S=p+q=-2y_0.
$$

Then

$$
\varphi(N)
=
N-S+1.
$$

Because

$$
ed=1+k\varphi(N),
$$

we recover

$$
\boxed{
d=
\frac{1+k\varphi(N)}{e}.
}
$$

The prime factors are roots of

$$
z^2-Sz+N=0.
$$

Its discriminant is

$$
\Delta=S^2-4N.
$$

For a valid RSA factorization, $\Delta$ must be a perfect square and

$$
p,q
=
\frac{S\pm\sqrt\Delta}{2}.
$$

Return to our toy model.

We had

$$
y_0=-32\,519.
$$

Therefore

$$
S=65\,038.
$$

Then

$$
\Delta
=
65\,038^2
-
4(1\,051\,195\,297)
=
25\,160\,256.
$$

And

$$
25\,160\,256
=
5\,016^2.
$$

So

$$
\frac{65\,038+5\,016}{2}
=
35\,027,
$$

and

$$
\frac{65\,038-5\,016}{2}
=
30\,011.
$$

The original factors return exactly.

This gives us a strong validation rule:

```text
candidate small root
        ↓
candidate p + q
        ↓
perfect-square discriminant
        ↓
p*q == N
        ↓
candidate phi(N)
        ↓
ed == 1 mod phi(N)
```

A cryptanalytic result should always end with exact algebraic validation.

LLL output by itself is not proof that the right secret was found.

---

## 10. Wiener versus Boneh–Durfee

It is useful to put the two ideas side by side.

| Question | Wiener | Boneh–Durfee |
|---|---|---|
| Starting relation | $ed-k\varphi(N)=1$ | Same |
| Main representation | Rational approximation | Bivariate modular polynomial |
| Hidden object | $k/d$ | $(k,p+q)$ or scaled equivalents |
| Main tool | Continued fractions | Coppersmith-style lattice + LLL |
| Geometry | Essentially low-dimensional | High-dimensional |
| Classical exponent scale | quarter-power region | asymptotically about $N^{0.292}$ |
| Post-processing | convergent validation | multiple polynomial relations + elimination |
| Main subtlety | approximation bound | lattice design + algebraic independence |

The progression is now much clearer:

```text
Euclidean algorithm
        ↓
continued fractions
        ↓
Wiener
        ↓
polynomial modular roots
        ↓
coefficient lattices
        ↓
LLL
        ↓
Coppersmith
        ↓
Boneh–Durfee
```

Nothing arrived from nowhere.

That is exactly why I did not want to begin this topic with a Sage function.

---

## 11. A standards connection

The scientific result also explains why modern key-generation rules do not treat the private exponent as a free performance knob.

For RSA signature key generation, **FIPS 186-5** requires the private signature exponent to satisfy

$$
d>2^{\mathrm{nlen}/2},
$$

together with

$$
d=e^{-1}
\pmod{\operatorname{lcm}(p-1,q-1)}.
$$

For an `nlen`-bit modulus,

$$
N^{0.292}
\approx
2^{0.292\,\mathrm{nlen}},
$$

while the FIPS lower bound is

$$
2^{0.5\,\mathrm{nlen}}.
$$

Those scales are enormously separated.

This should not be interpreted as saying that the FIPS inequality exists only because of Boneh–Durfee.

The more useful lesson is broader:

> mature key-generation standards encode structural constraints that prevent private parameters from drifting into cryptanalytically abnormal regimes.

Also remember the notation nuance from the Wiener article.

Modern PKCS #1 represents valid RSA private exponents using

$$
\lambda(N)
=
\operatorname{lcm}(p-1,q-1),
$$

whereas the classical Wiener/Boneh–Durfee derivations are commonly presented through $\varphi(N)$.

For studying the original mathematics, using the classical $\varphi(N)$ equation makes the derivation transparent.

For implementing modern RSA, follow the standard.

Those are different purposes.

---

## 12. What I actually want to remember

If I strip away every implementation detail, Boneh–Durfee is this chain:

$$
ed-k\varphi(N)=1
$$

with

$$
\varphi(N)=N+1-(p+q)
$$

gives

$$
f(x_0,y_0)\equiv0\pmod e
$$

for

$$
f(x,y)=1+x(A+y).
$$

The hidden root satisfies approximately

$$
|x_0|\lesssim e^\delta,
$$

$$
|y_0|\lesssim e^{1/2}.
$$

Then:

```text
small bivariate modular root
        ↓
carefully selected shifts
        ↓
scale by X and Y
        ↓
coefficient lattice
        ↓
LLL
        ↓
short integer polynomials
        ↓
algebraic elimination
        ↓
candidate (x0,y0)
        ↓
p + q
        ↓
factor validation
        ↓
d
```

And the refined asymptotic analysis reaches

$$
\delta
<
1-\frac{1}{\sqrt2}
\approx0.292893.
$$

But there is one final sentence I want attached to that bound permanently:

> multivariate Coppersmith is not the same clean theorem as the univariate case; lattice shortness and algebraic root extraction are separate parts of the argument.

That distinction is scientifically more important than the decimal.

---

## 13. A small experiment for the repository

For this post I would keep the executable companion deliberately narrow.

Not a generic recovery tool.

Just a reproducible mathematical model-check:

```text
1. choose tiny balanced primes p and q
2. choose an intentionally small textbook d
3. compute e = d^(-1) mod phi(N)
4. compute k = (ed - 1)/phi(N)
5. construct A, x0, y0
6. verify f(x0,y0) = 0 mod e
7. compare d with N^(1/4) and N^(0.292)
8. reconstruct p and q from y0
9. verify every RSA relation exactly
```

That is enough to make the modelling concrete without pretending that the full multivariate lattice machinery is a one-page Python exercise.

A full research implementation should separately expose:

- shift generation,
- monomial ordering,
- variable scaling,
- lattice dimension,
- determinant estimate,
- LLL parameters,
- extracted short polynomials,
- resultant or Gröbner post-processing,
- candidate validation,
- finite-size success experiments.

Those deserve their own experimental notebook rather than being hidden inside a blog code block.

---

## References

1. Dan Boneh and Glenn Durfee, **“Cryptanalysis of RSA with Private Key $d$ Less than $N^{0.292}$”**, *IEEE Transactions on Information Theory*, 46(4), 1339–1349, July 2000. Extended abstract in EUROCRYPT '99.  
   https://crypto.stanford.edu/~dabo/pubs/abstracts/lowRSAexp.html

2. Mathias Herrmann and Alexander May, **“Maximizing Small Root Bounds by Linearization and Applications to Small Secret Exponent RSA”**, PKC 2010, LNCS 6056, 53–69.  
   https://doi.org/10.1007/978-3-642-13013-7_4

3. Don Coppersmith, **“Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities”**, *Journal of Cryptology*, 10(4), 233–260, 1997.

4. Nick Howgrave-Graham, **“Finding Small Roots of Univariate Modular Equations Revisited”**, Cryptography and Coding, 1997, 131–142.  
   https://doi.org/10.1007/BFB0024458

5. NIST, **FIPS 186-5 — Digital Signature Standard (DSS)**, February 2023.  
   https://csrc.nist.gov/pubs/fips/186-5/final

---

The next natural step is not another unrelated RSA formula.

Now that we understand how the private exponent becomes a bounded polynomial unknown, we can look at a broader question:

> what if the secret is not globally small, but **some of its bits are known**?

That leads directly to another major Coppersmith family.

**Next RSA Deep Dive:** *Partial Key Exposure From Zero — Turning Known RSA Bits Into a Small-Root Problem.*
