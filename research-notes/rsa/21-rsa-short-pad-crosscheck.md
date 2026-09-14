# RSA Deep Dive IX — Short-Pad RSA Cross-Check

## Scope

This article is site-first and scientific.

It studies the classical short-pad result as a composition:

```text
resultant
-> Coppersmith small-root recovery
-> Franklin-Reiter related-message recovery
```

The companion verifies one fixed mathematical model. It does not provide a
generic workflow for deployed systems.

## Existing user-material cross-check

The user's Coppersmith article explicitly listed:

```text
Short padding
-> unknown random differences smaller than the modulus scale
```

as a later application.

The Franklin-Reiter article established:

```text
known affine relation
-> shared modular root
-> polynomial gcd
```

The new article combines exactly those two earlier branches.

## Primary literature

The article cross-checks:

- Don Coppersmith, *Small Solutions to Polynomial Equations, and Low Exponent
  RSA Vulnerabilities*, Journal of Cryptology 10(4), 1997.
- Coppersmith, Franklin, Patarin, Reiter, *Low-Exponent RSA with Related
  Messages*, EUROCRYPT 1996.
- Dan Boneh, *Twenty Years of Attacks on the RSA Cryptosystem*, Notices AMS,
  1999.
- Franklin and Reiter, *A Linear Protocol Failure for RSA with Exponent Three*,
  CRYPTO '95 Rump Session.

Boneh's survey gives the clean proof architecture:

```text
g1(x,y) = x^e - C1
g2(x,y) = (x+y)^e - C2
Delta = r2-r1
resultant in x -> h(y)
deg h <= e^2
small Delta -> Coppersmith
known Delta -> Franklin-Reiter
```

## Resultant for e = 3

For:

```text
g1(X)   = X^3 - C1
g2(X,Y) = (X+Y)^3 - C2
```

the resultant is:

```text
h(Y) =
Y^9
+ 3(C1-C2)Y^6
+ 3(C1^2 + 7*C1*C2 + C2^2)Y^3
+ (C1-C2)^3
```

modulo `N`.

Thus:

```text
deg h = 9 = e^2.
```

## Fixed toy model

```text
p = 68719476713
q = 68719476731
N = 4722366480945499865203
bit_length(N) = 72
e = 3
```

The primes satisfy the textbook RSA exponent condition.

Padding:

```text
s = 8
r1 = 37
r2 = 110
Delta = 73
```

Message:

```text
M = 12345678901234567
```

Padded representatives:

```text
M1 = 3160493798716049189
M2 = 3160493798716049262
```

Ciphertexts:

```text
C1 = 2864700865949590458710
C2 = 2517680417894642341351
```

Scale:

```text
N^(1/9) ~= 255.999999988410
Delta = 73
```

so the fixed model is comfortably inside the conceptual ninth-root regime.

## Important theorem wording

The article avoids treating `n/e^2` as an exact finite-size cliff.

The primary condition is the small-root inequality on `Delta`; the bit-count
statement is its asymptotic translation.

Likewise:

```text
outside the standard root bound
```

is not equated with:

```text
provably hard.
```

## Why LLL is not duplicated

The earlier Coppersmith chapter already develops:

- shift construction,
- scaling,
- coefficient lattices,
- LLL,
- the divisibility-plus-smallness argument.

The new scientific content is the resultant elimination that creates a
univariate polynomial in the small pad difference.

## Padding terminology

The article distinguishes naive suffix padding:

```text
2^s M + r
```

from RSAES-OAEP.

The conclusion is not that randomized encoding is ineffective. The conclusion
is that a very short appended random suffix may preserve exploitable algebraic
structure in textbook RSA.

## Publication checklist

Verify:

- Is `Delta=r2-r1` derived before any lattice language?
- Is `|Delta|<2^s` explicit?
- Are `g1` and `g2` explicit?
- Is the resultant explained as variable elimination?
- Is the degree-nine resultant written out?
- Is `9=e^2` connected to the root scale?
- Is the `n/e^2` bit interpretation derived rather than memorized?
- Does the 72-bit toy model align cleanly with the 8-bit scale?
- Is the exact resultant root verified?
- Is Coppersmith reused rather than re-taught?
- Is Franklin-Reiter applied only after Delta is known?
- Is the theorem boundary described as sufficient, not necessary?
- Is naive suffix padding distinguished from OAEP?
- Does the transition to validity-oracle cryptanalysis clearly change layers?

Any "no" means another revision.
