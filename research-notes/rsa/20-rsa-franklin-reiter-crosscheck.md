# RSA Deep Dive VIII — Franklin–Reiter Cross-Check

## Scope

This package is site-first and purely scientific.

The article studies the classical Franklin–Reiter related-message result as
an algebraic phenomenon in textbook RSA:

```text
known affine relation
-> two modular polynomial equations
-> common root
-> common polynomial factor
-> Euclidean polynomial GCD.
```

The fixed companion script contains no network interaction, key collection,
certificate parsing, or generic target logic.

---

## Existing user-material cross-check

The user's Coppersmith article already scheduled:

```text
Related messages:
m2 = a*m1 + b
```

as one of the natural continuations after small-root RSA.

The mature Håstad article also explicitly mentioned Franklin–Reiter as part of
the larger low-degree RSA landscape.

The new article preserves that continuity but makes one important correction:

```text
classical Franklin–Reiter affine related-message recovery
does NOT require Coppersmith / LLL.
```

The common root is recovered by polynomial GCD.

Coppersmith becomes relevant again in broader settings such as short unknown
padding or small unknown relations.

---

## Primary-source verification

### Franklin & Reiter, CRYPTO '95 Rump Session

The bibliographic entry in the EUROCRYPT '96 paper identifies:

```text
M. K. Franklin and M. K. Reiter
"A linear protocol failure for RSA with exponent three"
Presented at the CRYPTO '95 Rump Session
August 1995.
```

### Coppersmith–Franklin–Patarin–Reiter, EUROCRYPT '96

Verified publication:

```text
Low-Exponent RSA with Related Messages
EUROCRYPT 1996
LNCS 1070
pp. 1-9
DOI 10.1007/3-540-68339-9_1
```

The paper states that its results were influenced by the Franklin–Reiter case:

```text
k = 2
e = 3
degree of relation = 1
```

and then generalizes:

- exponent;
- relation degree;
- number of messages.

The paper explicitly describes computing:

```text
gcd(z^e - c1, (alpha*z + beta)^e - c2)
```

over `Z/N[z]`, expecting a linear polynomial `z-m` outside exceptional cases.

---

## Fixed toy instance

Reused educational modulus:

```text
p = 30011
q = 35027
N = 1051195297
e = 3
```

Plaintexts:

```text
m1 = 12037
m2 = m1 + 1 = 12038
```

Ciphertexts:

```text
c1 = 100336930
c2 = 535041149
```

Polynomials:

```text
g1(X) = X^3 - c1
g2(X) = (X+1)^3 - c2
```

Both satisfy:

```text
g1(12037) = 0 mod N
g2(12037) = 0 mod N.
```

The Euclidean polynomial GCD is:

```text
X - 12037
```

represented modulo `N` by:

```text
[1051183260, 1].
```

---

## Direct e=3 elimination cross-check

From:

```text
c2-c1 = 3m^2 + 3m + 1 mod N
```

define:

```text
t = (c2-c1-1) / 3 mod N.
```

For the toy values:

```text
t = 144901406
  = m^2 + m.
```

Then:

```text
m^3 = m(t+1)-t mod N.
```

Since:

```text
m^3 = c1 mod N,
```

we obtain:

```text
m = (c1+t) * (t+1)^(-1) mod N.
```

The denominator is invertible in the fixed example and the formula returns:

```text
m = 12037.
```

This confirms the polynomial-GCD result through independent algebra.

---

## Composite-coefficient-ring caveat

The article explicitly distinguishes:

```text
F_p[X]
```

from:

```text
Z_N[X], N composite.
```

Polynomial long division requires inversion of the current divisor's leading
coefficient.

That inversion exists only if:

```text
gcd(lc, N) = 1.
```

If instead:

```text
1 < gcd(lc, N) < N,
```

the non-unit coefficient itself exposes a non-trivial factor of `N`.

The companion implementation therefore tests invertibility explicitly.

This is not treated as an implementation nuisance; it is part of the algebra.

---

## Taxonomy corrections

The article distinguishes:

### Håstad

```text
different moduli
related / repeated low-degree messages
CRT + low-degree recovery
```

### Franklin–Reiter

```text
same modulus and exponent
known affine related messages
polynomial GCD
```

### Coppersmith

```text
one modular polynomial
small unknown root
lattice reduction
```

These are related cryptanalytic ideas but not interchangeable algorithms.

---

## Modern encoding connection

The article explains that the model acts on textbook RSA representatives.

Randomized encodings such as OAEP alter the message representation before
RSA exponentiation, so a simple application-level relation such as:

```text
M2 = M1 + 1
```

does not normally imply:

```text
EM2 = EM1 + 1.
```

This is presented as a structural reason why textbook RSA analysis must not be
confused with a complete modern encryption scheme.

---

## Publication checklist

Verify:

- Is the affine relation introduced before the word GCD?
- Are both ciphertext equations converted into explicit polynomials?
- Is the shared-root argument obvious?
- Is the special `m2=m+1`, `e=3` case derived by hand?
- Are all toy ciphertexts reproducible?
- Does the polynomial GCD equal `X-12037`?
- Is integer Euclid connected to polynomial Euclid?
- Is `Z_N` correctly identified as a ring rather than a field?
- Are non-unit leading coefficients handled explicitly?
- Is Franklin–Reiter distinguished from Håstad?
- Is Franklin–Reiter distinguished from Coppersmith?
- Is the 1995 rump-session origin separated from the 1996 generalization?
- Is OAEP described as destroying the required representative-level relation?
- Is the next short-pad transition mathematically natural?

Any "no" means another revision.
