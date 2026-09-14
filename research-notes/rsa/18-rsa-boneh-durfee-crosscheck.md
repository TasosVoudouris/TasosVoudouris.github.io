# RSA Deep Dive VI — Boneh–Durfee Cross-Check

## Scope

This package is intentionally **site-first and scientific**.

The public article explains the Boneh–Durfee small-private-exponent result as a
mathematical modelling problem:

```text
RSA key equation
-> bounded hidden variables
-> bivariate modular polynomial
-> shifted polynomial lattice
-> LLL short relations
-> algebraic root extraction
-> exact RSA validation
```

It does **not** include a generic RSA recovery utility, key scanner, network
logic, certificate harvesting, or target-oriented workflow.

The companion script only verifies the mathematics on one fixed toy parameter
set.

---

## Sources cross-checked

### Existing Cryptography From Zero material

The article continues directly from:

- RSA Deep Dive IV — Wiener's attack;
- RSA Deep Dive V — Coppersmith from zero;
- the earlier RSA key-generation article.

The previous Coppersmith article explicitly required the next Boneh–Durfee
article to preserve the distinction between:

```text
univariate Coppersmith
```

and:

```text
multivariate small-root constructions
```

where algebraic independence and post-processing require additional care.

### Existing user-authored research material

The saved lattice-cryptanalysis chapter states the central result carefully:

- Coppersmith shifts turn modular root information into short coefficient
  vectors;
- Boneh–Durfee uses bivariate small-root machinery;
- the classical small-private-exponent exponent is about `0.292`;
- this must not be presented as a generic RSA factorization algorithm;
- multivariate polynomial independence / resultant / Groebner details must be
  audited rather than assumed away.

That framing is preserved.

### External literature

Cross-checked against:

1. Boneh & Durfee, IEEE Transactions on Information Theory 46(4), 2000.
2. Herrmann & May, PKC 2010.
3. Coppersmith, Journal of Cryptology 10(4), 1997.
4. Howgrave-Graham, Cryptography and Coding 1997.
5. NIST FIPS 186-5.

---

## Important mathematical decisions

### 1. Polynomial normalization

The article uses the scaled form

```text
A  = (N+1)/2
x0 = 2k
y0 = -(p+q)/2
f(x,y) = 1 + x(A+y)
```

because then

```text
f(x0,y0)
= 1 + k*phi(N)
= e*d
= 0 mod e.
```

This is compatible with the standard small-inverse formulation and avoids
fractional hidden variables for odd RSA primes.

### 2. Root bounds

For balanced primes and `e ≈ N`:

```text
|x0| = O(N^delta)
|y0| = O(N^1/2)
```

when:

```text
d < N^delta.
```

The article deliberately says `O(...)` / approximate scaling rather than
pretending the omitted constants are irrelevant in finite experiments.

### 3. The 0.292 exponent

The article gives:

```text
delta < 1 - 1/sqrt(2)
      ≈ 0.292893.
```

It explicitly labels this as an **asymptotic** Boneh–Durfee range.

It does not claim that every finite instance below the decimal succeeds or
that every instance above it fails.

### 4. Algebraic-independence caveat

This is deliberately prominent.

LLL may produce multiple short vectors, but two variables require enough
algebraically independent polynomial relations for resultant / Groebner
post-processing.

The article therefore avoids the false implication:

```text
short vectors -> automatic bivariate root.
```

### 5. Herrmann-May interpretation

The article introduces:

```text
u = xy + 1
```

so that:

```text
f(x,y) = 1 + Ax + xy
```

becomes:

```text
f_bar(u,x) = u + Ax
```

while retaining the quotient relation:

```text
xy = u - 1.
```

The article correctly presents this as a lattice-organization / determinant
simplification, not as elimination of the original nonlinear structure.

---

## Fixed toy parameter study

The article and companion use:

```text
p   = 30011
q   = 35027
N   = 1051195297
phi = 1051130260

d   = 263
e   = 1047133567
k   = 262
```

Checked:

```text
e*d - 1 = k*phi.
```

Boneh-Durfee variables:

```text
A  = 525597649
x0 = 524
y0 = -32519
```

Then:

```text
f(x0,y0)
= 1 + x0*(A+y0)
= 275396128121
= e*d
```

and therefore:

```text
f(x0,y0) = 0 mod e.
```

Scale check:

```text
N^(1/4)  ≈ 180.0615
d        = 263
N^0.292  ≈ 430.8554
```

So the toy value lies numerically between the two familiar exponent scales.

This is used **only as a pedagogical scale comparison**.

It is not presented as a finite-size proof of practical lattice success.

---

## Reconstruction validation

From:

```text
y0 = -(p+q)/2
```

we get:

```text
S = p+q = 65038.
```

Then:

```text
Delta = S^2 - 4N
      = 25160256
      = 5016^2.
```

Hence:

```text
p = (S-5016)/2 = 30011
q = (S+5016)/2 = 35027.
```

Finally:

```text
phi(N) = N-S+1
d = (1 + k*phi(N))/e = 263.
```

All checks are exact.

---

## Standards wording

The article scopes the FIPS statement specifically to **RSA signature key
generation**.

FIPS 186-5 requires:

```text
d > 2^(nlen/2)
```

and:

```text
d = e^(-1) mod LCM(p-1,q-1).
```

The article does not present this as a universal rule for every historical RSA
API or as if the inequality existed solely because of Boneh–Durfee.

It is used only to show the enormous separation between standardized private
exponent sizes and the classical small-secret-exponent asymptotic region.

---

## Publication checklist

Before publishing, verify:

- Does the reader see the exact RSA equation before any lattice terminology?
- Is the transformation to `f(x,y)` derived line by line?
- Are `x0` and `y0` defined explicitly?
- Are the small-root bounds motivated rather than asserted?
- Does the toy model verify `f(x0,y0)=ed` exactly?
- Is the article clear that the toy model is not a finite-size success proof?
- Is the transition from Wiener to Coppersmith to Boneh–Durfee explicit?
- Are shifted polynomials explained through divisibility by `e^m`?
- Is the need for more than one independent polynomial explicit?
- Is unravelled linearization explained together with `xy=u-1`?
- Is the `0.292` result labelled asymptotic?
- Is algebraic independence treated as a genuine scientific caveat?
- Is reconstruction from `(x0,y0)` validated by the discriminant?
- Is the FIPS statement scoped to RSA signatures?
- Does the article avoid target-oriented or “break a real key” framing?

Any “no” means another revision.
