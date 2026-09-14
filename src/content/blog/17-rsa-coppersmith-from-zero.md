---
title: 'RSA Deep Dive V: Coppersmith From Zero'
description: 'How a small modular root becomes a lattice problem: from a known-prefix RSA message to shifted polynomials, coefficient scaling, exact LLL reduction, an integer-zero argument, and recovery of the unknown plaintext suffix.'
pubDate: '2026-09-09'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Lattice Methods
tags:
- rsa
- coppersmith
- lll
- lattices
- small-roots
- partial-plaintext
- cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 5
draft: false
---
This is probably the first post in the series where one line of SageMath could hide almost everything I actually want to understand.

You may have seen code like:

```python
f.small_roots(X=...)
```

and then:

```text
[37]
```

That is useful when the goal is to solve a challenge.

It is terrible if the goal is to understand why Coppersmith's method works.

So this post will deliberately avoid that black box.

We are going to build the attack from the inside:

```text
small modular root
        ↓
many polynomials sharing that modular root
        ↓
coefficient vectors
        ↓
integer lattice
        ↓
LLL finds a short combination
        ↓
short enough + divisible by N^m
        ↓
must equal 0 over the integers
        ↓
ordinary integer root recovery
```

The important conceptual jump is this:

> Coppersmith does not somehow "take a root modulo an unknown composite."  
> It constructs a new polynomial whose value at the hidden root is both highly divisible and provably too small to be a non-zero multiple of that modulus.

That sentence is the heart of the method.

If you want the prerequisites first:

- [Modular arithmetic and zero divisors](/blog/03-modular-arithmetic-units-zero-divisors/)
- [Fast modular exponentiation](/blog/08-fast-modular-exponentiation-side-channels/)
- [The Chinese Remainder Theorem](/blog/10-chinese-remainder-theorem/)
- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Håstad's Broadcast Attack](/blog/15-rsa-hastad-broadcast-attack/)
- [Wiener's Attack](/blog/16-rsa-wiener-attack/)

![Coppersmith small-root pipeline from RSA polynomial to LLL](/images/blog/17-rsa-coppersmith.svg)

*We manufacture many polynomial relations that vanish modulo a high power of $N$ at the hidden root, encode them as a lattice, and use LLL to find a short relation that must vanish over the integers.*

---

## 1. The problem Coppersmith solves

Let:

$$
f(x)\in\mathbb Z[x]
$$

be a monic polynomial of degree:

$$
\delta.
$$

Suppose we know that some unknown integer:

$$
x_0
$$

satisfies:

$$
f(x_0)\equiv0\pmod N.
$$

If $N$ is a large composite of unknown factorization, solving arbitrary polynomial equations modulo $N$ can be hard.

But now add one extra piece of information:

$$
|x_0|<X
$$

for a sufficiently small bound $X$.

Coppersmith's univariate method shows that sufficiently small roots can be recovered efficiently.

The classical scale to remember for a monic degree-$\delta$ polynomial is:

$$
\boxed{
|x_0|\lesssim N^{1/\delta}.
}
$$

For degree:

$$
\delta=3,
$$

the important scale is therefore:

$$
N^{1/3}.
$$

I am writing $\lesssim$ deliberately.

The precise theorem, asymptotic slack, and practical lattice parameters deserve more care than the slogan:

```text
root < N^(1/delta)
```

But that is the correct conceptual boundary for the monic univariate case.

And unlike Håstad's attack, we do **not** need several moduli.

One modulus can be enough if enough of the unknown is already constrained.

---

## 2. RSA application: most of the plaintext is known

Take textbook RSA with:

$$
e=3.
$$

Suppose the plaintext integer has the form:

$$
M=M_0+x_0,
$$

where:

- $M_0$ is known,
- $x_0$ is unknown,
- $x_0$ is small.

The ciphertext is:

$$
c\equiv(M_0+x_0)^3\pmod N.
$$

Move the ciphertext to the left:

$$
(M_0+x_0)^3-c\equiv0\pmod N.
$$

Define:

$$
\boxed{
f(x)=(M_0+x)^3-c.
}
$$

Then the unknown suffix is exactly a modular root:

$$
\boxed{
f(x_0)\equiv0\pmod N.
}
$$

This is now a Coppersmith problem.

The RSA vocabulary has disappeared.

We are looking for a small root of a known polynomial modulo a known composite.

---

## 3. A complete toy RSA instance

Choose two toy RSA primes:

$$
p=30011,
$$

$$
q=35027.
$$

Then:

$$
N=pq=1{,}051{,}195{,}297.
$$

Use:

$$
e=3.
$$

For these primes:

$$
\gcd(3,\varphi(N))=1,
$$

so $e=3$ is a valid toy RSA public exponent.

Now suppose the actual plaintext representative is:

$$
M=12037.
$$

The attacker knows the prefix:

$$
M_0=12000
$$

but does not know the final offset:

$$
x_0=37.
$$

We deliberately assume only:

$$
|x_0|<100.
$$

So set:

$$
X=100.
$$

The ciphertext is:

$$
c=12037^3\bmod N.
$$

Numerically:

$$
\boxed{
c=100{,}336{,}930.
}
$$

And notice:

$$
12037^3
=
1{,}744{,}033{,}334{,}653
>
N.
$$

So this is **not** the trivial low-exponent failure where the attacker simply takes the integer cube root of the ciphertext.

Modular reduction really happened.

---

## 4. Build the polynomial

Our polynomial is:

$$
f(x)
=
(12000+x)^3
-
100{,}336{,}930.
$$

Expand:

$$
(12000+x)^3
=
x^3
+
36000x^2
+
432{,}000{,}000x
+
1{,}728{,}000{,}000{,}000.
$$

Therefore:

$$
\boxed{
f(x)
=
x^3
+
36000x^2
+
432{,}000{,}000x
+
1{,}727{,}899{,}663{,}070.
}
$$

Check the hidden root:

$$
f(37)\equiv0\pmod N.
$$

But importantly:

$$
f(37)\ne0
$$

as an ordinary integer.

It is only zero **modulo $N$**.

That distinction is the entire problem.

Ordinary polynomial factoring cannot simply reveal $37$ from $f$.

We need to manufacture another polynomial.

---

## 5. The first strange idea: create more polynomials with the same modular root

If:

$$
f(x_0)\equiv0\pmod N,
$$

then for some integer $u$:

$$
f(x_0)=Nu.
$$

Therefore:

$$
Nf(x_0)
$$

is divisible by:

$$
N^2.
$$

Also:

$$
f(x_0)^2
$$

is divisible by:

$$
N^2.
$$

And obviously:

$$
N^2
$$

itself is divisible by:

$$
N^2.
$$

Multiplying by powers of $x_0$ does not change that divisibility.

So we can manufacture several polynomials $g_i(x)$ such that:

$$
\boxed{
g_i(x_0)\equiv0\pmod{N^2}.
}
$$

For our first transparent construction choose:

$$
m=2.
$$

Because:

$$
\delta=\deg f=3,
$$

take the seven polynomials:

$$
g_0(x)=N^2,
$$

$$
g_1(x)=N^2x,
$$

$$
g_2(x)=N^2x^2,
$$

$$
g_3(x)=Nf(x),
$$

$$
g_4(x)=Nxf(x),
$$

$$
g_5(x)=Nx^2f(x),
$$

$$
g_6(x)=f(x)^2.
$$

Every one satisfies:

$$
g_i(x_0)\equiv0\pmod{N^2}.
$$

Therefore **every integer linear combination**:

$$
h(x)
=
a_0g_0(x)+\cdots+a_6g_6(x)
$$

also satisfies:

$$
\boxed{
h(x_0)\equiv0\pmod{N^2}.
}
$$

This gives us an entire lattice of valid modular relations.

The only missing ingredient is:

> Which linear combination should we choose?

We want one whose coefficients are unusually small.

That is where LLL enters.

---

## 6. Why we replace $x$ with $Xx$

This scaling is easy to see in code and easy to misunderstand mathematically.

Suppose:

$$
h(x)
=
h_0+h_1x+h_2x^2+\cdots+h_dx^d.
$$

At a root satisfying:

$$
|x_0|<X,
$$

the term:

$$
h_ix_0^i
$$

can be as large as roughly:

$$
|h_i|X^i.
$$

So the raw coefficient vector:

$$
(h_0,h_1,\ldots,h_d)
$$

does not measure the size of $h(x_0)$ fairly.

Higher-degree coefficients need larger weight.

Instead consider:

$$
h(Xx).
$$

Its coefficient vector is:

$$
\boxed{
(h_0,\ h_1X,\ h_2X^2,\ldots,h_dX^d).
}
$$

Now Euclidean length in coefficient space reflects the maximum root scale $X$.

This is the geometric reason for the substitution:

$$
x\mapsto Xx.
$$

It is not cosmetic scaling.

It encodes the assumption:

$$
|x_0|<X
$$

into the lattice geometry.

---

## 7. Turn polynomials into lattice vectors

Our largest polynomial degree is:

$$
6.
$$

So every scaled polynomial:

$$
g_i(Xx)
$$

has seven coefficients.

Map:

$$
a_0+a_1x+\cdots+a_6x^6
$$

to:

$$
(a_0,a_1,\ldots,a_6)\in\mathbb Z^7.
$$

The seven coefficient vectors form a $7$-dimensional integer lattice basis.

For the first three rows the structure is especially clear.

Because:

$$
N^2
=
1{,}105{,}011{,}552{,}434{,}918{,}209,
$$

we get:

$$
g_0(Xx)
=
N^2,
$$

so:

$$
b_0=
(
N^2,0,0,0,0,0,0
).
$$

For:

$$
N^2x
$$

after substituting:

$$
x\mapsto100x,
$$

we obtain:

$$
b_1=
(
0,100N^2,0,0,0,0,0
).
$$

And:

$$
b_2=
(
0,0,10000N^2,0,0,0,0
).
$$

The remaining rows contain the coefficients of:

$$
Nf(100x),
$$

$$
100Nx f(100x),
$$

$$
10000Nx^2f(100x),
$$

and:

$$
f(100x)^2.
$$

The exact matrix is included and printed by the companion code.

This is now a standard integer lattice problem:

> find a non-zero short vector in the lattice generated by these rows.

---

## 8. What does LLL actually promise?

An integer lattice has infinitely many vectors:

$$
v=z_1b_1+\cdots+z_nb_n,
\qquad
z_i\in\mathbb Z.
$$

Finding the exact shortest non-zero vector is generally difficult.

The Lenstra–Lenstra–Lovász algorithm does something weaker but extremely useful:

> It transforms a basis into a reduced basis containing relatively short, relatively orthogonal vectors in polynomial time.

For a basis:

$$
B=(b_1,\ldots,b_n),
$$

LLL repeatedly performs two ideas:

### Size reduction

Make Gram–Schmidt coefficients small:

$$
|\mu_{i,j}|\le\frac12.
$$

### Lovász condition

Prevent later basis vectors from being too badly aligned with earlier ones.

For the standard parameter:

$$
\delta=\frac34,
$$

the condition is:

$$
\|\widetilde b_k\|^2
\ge
\left(
\delta-\mu_{k,k-1}^2
\right)
\|\widetilde b_{k-1}\|^2.
$$

If it fails, swap basis vectors and continue.

The companion code implements this directly with exact rational Gram–Schmidt arithmetic.

No `fpylll`.

No Sage `LLL()` call.

For our tiny seven-dimensional example, this is completely practical.

---

## 9. Why a short lattice vector gives a useful polynomial

Suppose LLL returns a short vector:

$$
v=
(v_0,v_1,\ldots,v_6).
$$

Because it is an integer combination of the lattice basis rows, it corresponds to a polynomial:

$$
h(Xx)
=
v_0+v_1x+\cdots+v_6x^6.
$$

Undo the scaling:

$$
h(x)
=
v_0
+
\frac{v_1}{X}x
+
\frac{v_2}{X^2}x^2
+
\cdots
+
\frac{v_6}{X^6}x^6.
$$

Because every basis polynomial was divisible by:

$$
N^2
$$

at $x_0$, their integer combination is too:

$$
\boxed{
N^2\mid h(x_0).
}
$$

So far this gives only another modular relation.

We need one more step to turn:

$$
h(x_0)\equiv0\pmod{N^2}
$$

into:

$$
h(x_0)=0
$$

over the integers.

This is the central smallness argument.

---

## 10. Divisible and too small means zero

Write:

$$
h(x)=\sum_{i=0}^{d}h_ix^i.
$$

Assume:

$$
|x_0|\le X.
$$

Then:

$$
|h(x_0)|
=
\left|
\sum_{i=0}^{d}h_ix_0^i
\right|.
$$

Write:

$$
y=\frac{x_0}{X},
\qquad
|y|\le1.
$$

Then:

$$
h(x_0)
=
\sum_{i=0}^{d}
(h_iX^i)y^i.
$$

By Cauchy–Schwarz:

$$
|h(x_0)|
\le
\sqrt{d+1}
\left\|
(h_0,h_1X,\ldots,h_dX^d)
\right\|_2.
$$

But that vector is exactly the scaled coefficient vector produced by the lattice.

So if LLL gives us a vector satisfying:

$$
\left\|
h(Xx)
\right\|_2
<
\frac{N^2}{\sqrt{d+1}},
$$

then:

$$
|h(x_0)|<N^2.
$$

At the same time:

$$
N^2\mid h(x_0).
$$

The only multiple of $N^2$ with absolute value strictly smaller than $N^2$ is:

$$
0.
$$

Therefore:

$$
\boxed{
h(x_0)=0
}
$$

as an ordinary integer equality.

This is the conceptual miracle of Coppersmith-style lattice constructions:

```text
modular zero
+
high divisibility
+
short coefficient vector
+
small root bound
=
integer zero
```

After that, ordinary algebra can recover the root.

---

## 11. Check the inequality numerically

For our lattice:

$$
d=6.
$$

The first reduced vector produced by our exact LLL implementation is:

```text
(
 23407270775993751,
-33360151994489800,
-34621233503770000,
-59988908020000000,
-115518764200000000,
-215529700000000000,
 145700000000000000
)
```

Its Euclidean norm is approximately:

$$
\boxed{
2.958\times10^{17}.
}
$$

The integer-zero threshold is:

$$
\frac{N^2}{\sqrt7}
\approx
\boxed{
4.177\times10^{17}.
}
$$

So:

$$
2.958\times10^{17}
<
4.177\times10^{17}.
$$

The shortness condition is satisfied.

Therefore the corresponding polynomial vanishes at $x_0$ over the integers.

This is not:

```text
LLL guessed 37
```

LLL produced a short relation.

The divisibility-plus-smallness argument converts that relation into an integer polynomial equation.

---

## 12. Undo the scaling

Divide the $i$-th coefficient by:

$$
X^i=100^i.
$$

The resulting polynomial is:

$$
\begin{aligned}
h(x)=\;&
145700x^6
-21552970x^5
-1155187642x^4\\
&-59988908020x^3
-3462123350377x^2\\
&-333601519944898x
+23407270775993751.
\end{aligned}
$$

Now evaluate:

$$
h(37)=0.
$$

In fact, over the integers:

$$
\boxed{
x-37
}
$$

is a factor of $h(x)$.

The lattice has turned a hidden modular root into an ordinary integer root.

That is the point where the cryptanalysis becomes almost boring again.

We simply recover:

$$
x_0=37.
$$

Then reconstruct the plaintext:

$$
M=M_0+x_0.
$$

So:

$$
\boxed{
M=12000+37=12037.
}
$$

---

## 13. From-scratch polynomial representation

The companion code does not rely on a symbolic algebra system for the attack mechanics.

A polynomial:

$$
a_0+a_1x+\cdots+a_dx^d
$$

is stored as:

```python
[a0, a1, ..., ad]
```

in low-to-high coefficient order.

We implement:

```text
addition
multiplication
integer scaling
x^j shifting
polynomial powers
evaluation
x -> Xx coefficient scaling
```

For example:

```python
def poly_eval(poly, value):
    result = 0

    for coefficient in reversed(poly):
        result = result * value + coefficient

    return result
```

That is Horner's rule.

Then:

```python
f = poly_sub(
    poly_pow([M0, 1], 3),
    [ciphertext],
)
```

constructs:

$$
(M_0+x)^3-c.
$$

Again, code mirrors the algebra.

---

## 14. From-scratch exact LLL

For educational implementations, floating-point Gram–Schmidt can obscure failures caused by numerical precision.

Our tiny lattice is small enough to avoid that problem completely.

The repository's:

```text
lll.py
```

uses Python's:

```python
fractions.Fraction
```

for exact rational arithmetic.

At every LLL step it:

1. computes Gram–Schmidt vectors;
2. computes exact:
   $$
   \mu_{i,j};
   $$
3. size-reduces using nearest integers;
4. checks the Lovász condition;
5. swaps when required.

For this basis the reduction completes in:

```text
126 LLL loop iterations
```

and deterministically recovers a short polynomial with root $37$.

That implementation is not meant to compete with `fplll`.

Its job is to expose the algorithm.

Later, when we move to realistic lattices, we will switch to optimized libraries and explain why.

---

## 15. Build the Coppersmith lattice in code

The exact polynomial family is:

```python
for i in range(m):
    for j in range(delta):
        g = (
            x^j
            * N^(m-i)
            * f(x)^i
        )
```

followed by a final set:

```python
x^j * f(x)^m
```

For our:

$$
m=2,
\qquad
\delta=3,
\qquad
t=1,
$$

this gives:

```text
N²
N²x
N²x²
Nf
Nxf
Nx²f
f²
```

Then every polynomial is transformed by:

$$
x\mapsto Xx.
$$

Its coefficients become one lattice row.

This is an important point:

> the lattice basis is not arbitrary.

Every row was engineered to satisfy **two properties at once**:

1. it vanishes modulo $N^m$ at $x_0$;
2. its coefficient geometry contains the root bound $X$.

Coppersmith is a modelling problem before it is an LLL problem.

---

## 16. Why $m=2$ here?

The parameter:

$$
m
$$

controls how much modular divisibility we manufacture.

For:

$$
m=2,
$$

we aim for:

$$
N^2\mid h(x_0).
$$

Larger $m$ creates higher powers of $f$ and $N$, increases lattice dimension, and can improve the root range—but also makes the lattice larger and more expensive.

Real Coppersmith implementations choose:

```text
m
t
X
```

through determinant bounds and optimization arguments.

For this post, I deliberately choose:

$$
m=2,
\quad
t=1,
\quad
X=100
$$

because the entire construction stays visible.

We are not trying to sit exactly on the theoretical boundary.

We are trying to understand the mechanism.

---

## 17. How small is our root relative to the theorem scale?

Our modulus is:

$$
N=1{,}051{,}195{,}297.
$$

So:

$$
N^{1/3}
\approx
1016.8.
$$

Our assumed bound is only:

$$
X=100.
$$

And the actual hidden root is:

$$
x_0=37.
$$

So:

$$
37<100\ll1016.8.
$$

We are comfortably inside the degree-$3$ small-root regime.

This is intentional.

A first implementation should demonstrate the mechanism robustly before we start tuning lattice parameters near the asymptotic limit.

---

## 18. Failure experiment: the bound is part of the attack input

Now lie to the attack.

Tell it:

$$
X=30.
$$

But the real root is:

$$
x_0=37.
$$

Then:

$$
|x_0|<X
$$

is false.

The lattice is now scaled around the wrong root range.

Our recovery routine only accepts integer roots inside:

$$
[-X,X].
$$

So the attack returns:

```text
None
```

This does not mean Coppersmith's theorem was wrong.

It means our attack model was wrong.

The small-root bound is not metadata.

It is part of the mathematical construction.

This is exactly the kind of failure condition I want every Deep Dive to expose.

---

## 19. Why not just brute-force 100 possibilities?

For this toy example, of course we could.

Try:

```python
for x in range(100):
    if pow(12000 + x, 3, N) == c:
        print(x)
```

and we recover $37$.

But that is not the point.

In a real small-root application the unknown may be, for example:

```text
hundreds of bits constrained below N^(1/delta)
```

which is exponentially too large for brute force in the bit length.

Coppersmith's theorem is important because the running time is polynomial in the relevant input size for the proven small-root regime.

The toy bound is deliberately small only so we can inspect and test every internal object.

---

## 20. This is not "LLL breaks RSA"

Another dangerous slogan.

LLL receives no special knowledge of RSA.

It receives an integer lattice.

The RSA weakness appears earlier, when protocol or message structure gives us a polynomial relation:

$$
f(x_0)\equiv0\pmod N
$$

with unusually small unknown:

$$
x_0.
$$

The attack pipeline is:

```text
RSA / protocol structure
        ↓
small polynomial unknown
        ↓
Coppersmith lattice construction
        ↓
LLL
        ↓
short integer polynomial
        ↓
root recovery
```

So when somebody says:

> "Coppersmith breaks RSA,"

the correct response is:

> Which polynomial relation? Which unknown? What bound? Which modulus power? What lattice parameters?

Without those, the statement means almost nothing.

---

## 21. The original RSA connection is exactly this kind of example

Coppersmith's EUROCRYPT '96 univariate paper states the core result for a monic polynomial of degree $k$ modulo $N$ with a sufficiently small root, and explicitly gives low-exponent RSA applications.

One of them is directly related to our example:

> for RSA exponent $3$, knowing a large enough high-order portion of the plaintext can leave a small unknown suffix that becomes a root of
>
> $$
> (B+x)^3-c\equiv0\pmod N.
> $$

The paper shows that this is not just a toy observation—it leads to polynomial-time recovery in the small-root regime.

**Don Coppersmith, "Finding a Small Root of a Univariate Modular Equation," EUROCRYPT '96, LNCS 1070, pp. 155–165.**

A broader treatment appears in:

**Don Coppersmith, "Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities," Journal of Cryptology 10(4), 1997, pp. 233–260.**

This is the bridge from RSA arithmetic to lattice cryptanalysis.

---

## 22. Where Howgrave-Graham fits

Many practical explanations of univariate Coppersmith today use the formulation developed by Nick Howgrave-Graham.

The useful conceptual lemma is exactly the one we exploited:

```text
polynomial value divisible by a large modulus power
+
coefficient norm small enough for |x0| <= X
→
polynomial value must be zero over the integers
```

Howgrave-Graham's 1997 paper revisited univariate modular small roots and gave an alternative lattice formulation with practical advantages.

**Nick Howgrave-Graham, "Finding Small Roots of Univariate Modular Equations Revisited," Cryptography and Coding 1997, LNCS 1355, pp. 131–142.**

Our educational construction is closest in spirit to this modern lattice-and-smallness explanation.

---

## 23. Where LLL came from

The lattice reducer itself predates these RSA attacks.

The LLL algorithm was introduced by:

**A. K. Lenstra, H. W. Lenstra Jr., and L. Lovász, "Factoring Polynomials with Rational Coefficients," Mathematische Annalen 261, 1982, pp. 515–534.**

The original paper used lattice basis reduction as part of a polynomial-factorization algorithm.

Later cryptanalysis repeatedly discovered that:

> if secret information can be encoded as an unusually short lattice vector, basis reduction may reveal it.

That same pattern now appears across:

- RSA small-root attacks,
- subset-sum cryptanalysis,
- hidden-number problems,
- lattice-based cryptography itself,
- approximation and decoding attacks.

So LLL is not "the Coppersmith algorithm."

It is one powerful subroutine inside a much broader modelling framework.

---

## 24. The code verifies the proof condition, not only the root

The companion demo prints:

```text
root bound X
N^(1/3)
basis dimension
LLL iterations
short-vector norm
N^2 / sqrt(7)
```

and explicitly checks:

$$
\|v\|_2
<
\frac{N^2}{\sqrt7}.
$$

Then it verifies:

$$
N^2\mid h(x_0)
$$

and:

$$
h(x_0)=0.
$$

Finally it checks:

$$
f(37)\equiv0\pmod N.
$$

That sequence matters.

If we only printed:

```text
recovered x = 37
```

we would have reproduced the `small_roots()` black box in slower Python.

The point is to validate the mathematical path that made the recovery possible.

---

## 25. Companion chapter

The repository package is:

```text
chapters/17_rsa_coppersmith_from_zero/
├── README.md
├── polynomial.py
├── lll.py
├── coppersmith.py
├── demo.py
└── test_attack.py
```

Run:

```powershell
python chapters/17_rsa_coppersmith_from_zero/demo.py
```

Then:

```powershell
pytest chapters/17_rsa_coppersmith_from_zero/test_attack.py -q
```

The tests cover:

1. polynomial arithmetic;
2. exact Gram–Schmidt / LLL invariants;
3. construction of the seven basis polynomials;
4. divisibility by $N^2$ at the hidden root;
5. the short-vector inequality;
6. integer-polynomial recovery;
7. recovery of:
   $$
   x_0=37;
   $$
8. reconstruction of:
   $$
   M=12037;
   $$
9. failure when the supplied root bound is too small.

---

## 26. What Coppersmith gives us next

This post is not the end of one attack.

It is the beginning of an entire language.

Once we understand:

```text
small unknown
+
polynomial modular relation
+
lattice construction
=
recoverable secret
```

many RSA attacks stop looking unrelated.

### Partial plaintext exposure

Known message structure:

$$
M=M_0+x.
$$

### Partial prime exposure

Known high bits of:

$$
p=p_0+x.
$$

### Related messages

Two RSA plaintexts connected by:

$$
m_2=am_1+b.
$$

### Short padding

Unknown random differences smaller than the modulus scale.

### Small private exponent extensions

Boneh–Durfee rewrites the RSA key equation into a multivariate small-root problem and uses lattice techniques to go beyond Wiener's continued fractions.

This is why Coppersmith had to come before Boneh–Durfee.

Otherwise Boneh–Durfee would just look like mysterious Sage syntax.

---

## 27. One important boundary: univariate is the clean case

The monic univariate theorem is unusually clean.

Once we move to two or more variables, the story becomes harder.

For multivariate modular polynomial systems, there is no single universal theorem saying:

```text
if every variable is below this obvious bound,
LLL always recovers the root.
```

Many practical bivariate constructions rely on heuristics about algebraic independence of the short polynomials produced by lattice reduction.

That is one reason cryptanalytic papers spend so much effort on:

- lattice selection,
- determinant bounds,
- shift sets,
- algebraic independence,
- Gröbner/resultant post-processing,
- empirical success regions.

We will not hide that complexity when we reach Boneh–Durfee.

---

## 28. The mental model

If I had to retain Coppersmith in one diagram:

```text
f(x0) = 0 mod N
|x0| < X
        ↓
manufacture g_i with
g_i(x0) = 0 mod N^m
        ↓
encode g_i(Xx)
as lattice vectors
        ↓
LLL gives short h(Xx)
        ↓
N^m divides h(x0)
but |h(x0)| < N^m
        ↓
h(x0) = 0 over Z
        ↓
ordinary root finding
        ↓
x0
```

There are really two worlds:

```text
modular world
```

and:

```text
integer world.
```

The lattice is the bridge.

The divisibility condition anchors us in the modular world.

The norm bound pulls us into the integer world.

And once the hidden root crosses that bridge, ordinary algebra finishes the attack.

That, more than the syntax of LLL, is Coppersmith's idea.

---

Now we are finally ready for the attack that the previous post deliberately postponed.

Wiener showed that very small $d$ creates a one-dimensional rational approximation.

Boneh–Durfee shows that a larger—but still abnormally small—private exponent can be attacked by turning the RSA key equation into a **bivariate small-root problem**.

This time continued fractions are no longer enough.

The Coppersmith machinery we just built becomes essential.

**Next RSA Deep Dive:** *Boneh–Durfee From Zero: Turning the RSA Private-Key Equation Into a Lattice Attack.*
