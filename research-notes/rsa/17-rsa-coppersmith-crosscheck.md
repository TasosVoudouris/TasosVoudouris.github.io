# RSA Deep Dive V — Coppersmith From Zero Cross-Check

## User-source status

The user's mature RSA material already classifies:

```text
small-root structure
-> polynomial relations with unusually small unknowns
-> Coppersmith-style attacks
```

and explicitly schedules:
- Coppersmith;
- Boneh–Durfee;
- related RSA cryptanalysis

for later full derivations.

Thus this Deep Dive fills a planned gap rather than replacing an existing
complete derivation.

Relevant mature-source framing:

```text
Wiener -> unusually small d
Boneh-Durfee -> lattice extension
Coppersmith -> broader small-root toolbox
```

This taxonomy is retained.

---

## Primary-source verification

### Coppersmith 1996

Don Coppersmith:

```text
Finding a Small Root of a Univariate Modular Equation
EUROCRYPT 1996
LNCS 1070
pp. 155-165
DOI 10.1007/3-540-68339-9_14
```

The paper states a univariate monic modular small-root result at the conceptual
scale:

```text
|x0| < N^(1/k)
```

for degree `k`, and gives exponent-3 RSA applications including known
high-order plaintext bits.

### Coppersmith 1997

```text
Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities
Journal of Cryptology 10(4)
233-260
```

Broadens and consolidates the small-solution framework and RSA applications.

### Howgrave-Graham 1997

```text
Finding Small Roots of Univariate Modular Equations Revisited
Cryptography and Coding 1997
LNCS 1355
131-142
DOI 10.1007/BFb0024458
```

Provides an alternative practical univariate modular small-root formulation and
comparison with Coppersmith's approach.

### LLL

Lenstra, Lenstra, Lovasz:

```text
Factoring Polynomials with Rational Coefficients
Mathematische Annalen 261
1982
515-534
```

introduces the LLL basis-reduction algorithm.

---

## Worked RSA example

Toy primes:

```text
p = 30011
q = 35027
N = 1051195297
```

Both support toy public exponent:

```text
e = 3
```

because:

```text
gcd(3, (p-1)(q-1)) = 1.
```

Plaintext structure:

```text
M0 = 12000
x0 = 37
M  = 12037
```

Ciphertext:

```text
c = M^3 mod N = 100336930.
```

Importantly:

```text
M^3 = 1744033334653 > N.
```

Therefore ordinary integer cube-root recovery is impossible.

---

## Polynomial

```text
f(x) = (12000+x)^3 - 100336930
```

expands to:

```text
x^3
+ 36000*x^2
+ 432000000*x
+ 1727899663070.
```

Checked:

```text
f(37) = 0 mod N
```

but:

```text
f(37) != 0 over Z.
```

---

## Root scale

```text
N^(1/3) ~= 1016.78
```

The teaching attack uses:

```text
X = 100
x0 = 37.
```

Hence the example lies well inside the small-root regime.

This is deliberate: the tutorial explains mechanics rather than optimizing
parameters to the theoretical boundary.

---

## Lattice construction

Chosen parameters:

```text
degree delta = 3
m = 2
t = 1
```

Shift family:

```text
N^2
N^2*x
N^2*x^2
N*f
N*x*f
N*x^2*f
f^2
```

Every shift satisfies:

```text
g_i(x0) = 0 mod N^2.
```

After:

```text
x -> X*x
```

the seven coefficient vectors form a square 7-dimensional integer lattice
basis.

---

## Why scaling matters

For:

```text
h(x) = sum h_i x^i
|x0| <= X,
```

the vector:

```text
(h_0, h_1*X, ..., h_d*X^d)
```

controls the value at the root.

Cauchy-Schwarz gives:

```text
|h(x0)|
<= sqrt(d+1) * || h(X*x) ||_2.
```

Thus if:

```text
||h(X*x)||_2 < N^m / sqrt(d+1)
```

and:

```text
N^m divides h(x0),
```

then:

```text
|h(x0)| < N^m
```

forces:

```text
h(x0) = 0 over the integers.
```

This is the central integer-zero argument.

---

## LLL output

The custom exact LLL implementation returns first reduced vector:

```text
[
 23407270775993751,
-33360151994489800,
-34621233503770000,
-59988908020000000,
-115518764200000000,
-215529700000000000,
 145700000000000000
]
```

LLL loop count:

```text
126
```

Norm approximately:

```text
2.958e17.
```

Threshold:

```text
N^2/sqrt(7) ~= 4.177e17.
```

Hence the smallness condition holds.

---

## Integer polynomial

Undoing `X^i` scaling gives:

```text
145700*x^6
- 21552970*x^5
- 1155187642*x^4
- 59988908020*x^3
- 3462123350377*x^2
- 333601519944898*x
+ 23407270775993751.
```

Checked:

```text
h(37) = 0.
```

The polynomial contains integer factor:

```text
x - 37.
```

The educational code recovers roots by bounded integer checking after the
lattice step instead of depending on a symbolic factoring package.

---

## LLL implementation

The package includes a from-scratch small exact LLL implementation.

It uses:
- `Fraction` Gram-Schmidt;
- exact mu coefficients;
- size reduction;
- Lovasz swaps;
- `delta = 3/4`.

This is intentionally inefficient but avoids numerical ambiguity in the
7-dimensional teaching example.

Production or research-scale Coppersmith code should use optimized lattice
libraries.

---

## Failure case

Re-run with claimed:

```text
X = 30
```

while actual:

```text
x0 = 37.
```

The promised root interval is false.

The recovery layer rejects the hidden root and returns no accepted root.

This demonstrates that `X` is part of the mathematical attack model, not merely
a tuning parameter.

---

## Important scope corrections

The article does NOT claim:

```text
LLL breaks RSA.
```

Correct pipeline:

```text
structured RSA information
-> polynomial relation
-> unusually small unknown
-> Coppersmith modelling
-> lattice reduction
-> root recovery.
```

It also does NOT claim all multivariate Coppersmith variants have one clean,
fully proved universal root bound.

The univariate monic case is singled out as unusually clean.

---

## Why this comes before Boneh-Durfee

Boneh-Durfee converts the small-private-exponent RSA equation into a
multivariate small-root / lattice problem.

Without understanding:
- shifted polynomials;
- variable scaling;
- lattice coefficients;
- LLL shortness;
- modular-to-integer zero conversion,

a Boneh-Durfee implementation would be a black box.

Thus the intended order is:

```text
Wiener
-> Coppersmith / LLL foundation
-> Boneh-Durfee
```

---

## Companion package

```text
repo/chapters/17_rsa_coppersmith_from_zero/
├── README.md
├── polynomial.py
├── lll.py
├── coppersmith.py
├── demo.py
└── test_attack.py
```

No SageMath, SymPy, fpylll, or cryptographic external library is required for
the core demo.

---

## Publication checklist

Verify:

- Is the exact problem `f(x0)=0 mod N` stated first?
- Is the known-prefix RSA mapping fully derived?
- Is trivial integer-root RSA explicitly ruled out?
- Are all seven shift polynomials motivated?
- Is every basis polynomial shown to vanish modulo N^2?
- Is `x -> Xx` scaling explained geometrically?
- Are lattice vectors tied directly to polynomial coefficients?
- Is LLL explained as a short-vector approximation algorithm rather than magic?
- Is the Cauchy-Schwarz / integer-zero step explicit?
- Is the actual short-vector norm checked against the threshold?
- Is the recovered integer polynomial printed?
- Is `h(37)=0` checked?
- Is a false root bound shown to fail?
- Is the simple univariate theorem distinguished from multivariate heuristics?
- Is Coppersmith positioned as modelling + LLL, not "LLL attacks RSA"?
- Does the transition to Boneh-Durfee now feel earned?

Any "no" means another revision.
