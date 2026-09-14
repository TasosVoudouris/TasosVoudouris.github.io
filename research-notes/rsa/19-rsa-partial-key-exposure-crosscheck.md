# RSA Deep Dive VII — Partial Key Exposure Cross-Check

## Scope

This is a site-first scientific article about **information-to-algebra modelling**.

It does not model how key bits are physically acquired and does not contain
generic target-oriented RSA recovery code.

The full worked derivation is:

```text
known high bits of p
-> p = p0 + x
-> x is bounded
-> f(x) = p0 + x
-> f(x0) = 0 mod p, where p | N
-> divisor small-root theorem
-> quarter-power scale for balanced RSA.
```

The private-exponent partial-exposure result is included only as a research
connection after the simpler partial-factor case is understood.

---

## User-source cross-check

The user's existing Coppersmith article already records:

```text
Partial prime exposure:
p = p0 + x
```

as one of the next natural Coppersmith applications.

It also states the correct general principle:

```text
structured RSA information
-> polynomial relation
-> unusually small unknown
-> Coppersmith modelling
-> lattice reduction
-> root recovery.
```

This article expands exactly that item rather than introducing a disconnected
new topic.

The mature user-authored RSA material also classifies Coppersmith methods as
special-structure cryptanalysis rather than generic factoring.

---

## Primary literature checked

### Coppersmith, EUROCRYPT 1996

"Finding a Small Root of a Bivariate Integer Equation; Factoring with High
Bits Known"

The abstract states that factors of:

```text
N = P*Q
```

can be found given the high-order:

```text
(1/4) * log2(N)
```

bits of `P`.

Bibliography:

```text
EUROCRYPT 1996
LNCS 1070
pp. 178-189
DOI 10.1007/3-540-68339-9_16
```

### Boneh RSA survey, 1999

The survey states the classical theorem in the convenient `n`-bit form:

```text
N = p*q, N is n bits

given:
- n/4 least significant bits of p, or
- n/4 most significant bits of p

one can efficiently reconstruct the factorization.
```

The same survey also explains the Boneh-Durfee-Frankel partial-private-key
result.

### Boneh, Durfee, Frankel, ASIACRYPT 1998

"An Attack on RSA Given a Small Fraction of the Private Key Bits"

For low public exponent RSA, the paper shows that a fraction of the private
exponent bits can suffice to reconstruct the full private key.

The public article deliberately avoids collapsing all parameter regimes into
one universal fraction.

---

## The divisor-root statement

The article uses a modern informal fixed-degree form:

```text
p | N
p >= N^beta
f monic, degree delta
f(x0) = 0 mod p
```

with recoverable root scale roughly:

```text
|x0| <= N^(beta^2/delta)
```

subject to the usual asymptotic slack and theorem parameters.

For balanced RSA:

```text
beta = 1/2
```

and for:

```text
f(x) = p0 + x
```

we have:

```text
delta = 1.
```

Hence:

```text
|x0| roughly below N^(1/4).
```

The article does not present the boundary as an exact finite-size cliff.

---

## Fixed toy model

Chosen primes:

```text
p = 60013
q = 61027
```

Then:

```text
N = 3662413351
```

and:

```text
bit_length(N) = 32
bit_length(p) = 16
bit_length(q) = 16.
```

Binary `p`:

```text
1110101001101101
```

Expose the high nine bits:

```text
111010100???????
```

This defines:

```text
p0 = 59904
x0 = 109
```

so:

```text
p = p0 + x0.
```

The polynomial:

```text
f(x) = 59904 + x
```

satisfies:

```text
f(109) = 60013 = p
```

and therefore:

```text
f(109) = 0 mod p.
```

Quarter-power scale:

```text
N^(1/4) ~= 246.0038
```

and:

```text
x0 = 109 < N^(1/4).
```

The toy model exposes slightly more prefix information than the asymptotic
quarter-bit statement so that the finite numerical example remains visibly
inside the small-root scale.

---

## Partial-d wording

The article uses the classical equation:

```text
e*d - k*phi(N) = 1
```

and explains only the structural reduction:

```text
known low bits of d
-> partial information about e*d
-> candidate factor-bit information
-> Coppersmith factor reconstruction.
```

It does not implement a generic partial-d recovery procedure.

It also explicitly says that parameter conditions depend on the public
exponent and that later results are more nuanced than a universal
"quarter of d always determines the rest" slogan.

---

## Important scientific distinction

"Partial key exposure" is treated as an **input model**.

The article separates:

```text
how information becomes available
```

from:

```text
what number theory can reconstruct from that information.
```

This prevents side-channel acquisition, memory recovery, and mathematical
reconstruction from being conflated into one process.

---

## Publication checklist

Verify:

- Is `p = p0 + x` introduced before Coppersmith terminology?
- Is the bit bound converted explicitly into `x < 2^t`?
- Is the congruence modulo the unknown divisor `p` made explicit?
- Is this distinguished from roots modulo the full known modulus `N`?
- Is the role of `p >= N^beta` explained?
- Does balanced RSA give `beta = 1/2`?
- Does degree one give the `N^(1/4)` scale?
- Is the quarter-bit interpretation derived rather than memorized?
- Is the toy root visibly within the numerical bound?
- Is brute force distinguished from polynomial-time lattice reconstruction?
- Is the private-`d` result presented as a connection, not oversimplified?
- Is partial exposure separated from the mechanism that created the leak?
- Does the article avoid real-system targeting?
- Is the next Franklin-Reiter transition natural?

Any "no" means another revision.
