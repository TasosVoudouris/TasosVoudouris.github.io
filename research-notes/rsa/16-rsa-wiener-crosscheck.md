# RSA Deep Dive IV — Wiener's Attack Cross-Check

## Deep Dive standard

This post follows the newly adopted CryptoCave long-form standard inspired by
the user's preferred Delfr technical style:

```text
prerequisites
formal mathematics
derivation
proof mechanism
checked numerical example
from-scratch code
intermediate values
candidate validation
success case
failure case
modern standard context
research history
next-topic bridge
```

The reference influences depth and structure only; no Delfr prose is copied.

---

## User material retained

The user's mature CryptoBible RSA notes classify Wiener under:

```text
small private exponent
```

and explicitly distinguish it from:

```text
low public exponent
common modulus
Hastad broadcast
padding/oracles
fault attacks
```

The notes also correctly identify Boneh–Durfee as the later lattice-based
extension and Coppersmith as the broader small-root framework.

This taxonomy is preserved.

---

## Primary literature

Michael J. Wiener:

```text
Cryptanalysis of Short RSA Secret Exponents
IEEE Transactions on Information Theory
36(3), May 1990, pp. 553-558
DOI 10.1109/18.54902
```

Wiener's abstract describes:
- short RSA secret exponents;
- continued fractions;
- using public `e` and `pq` to estimate a fraction involving `d`;
- recovery of sufficiently short secret exponents;
- roughly quarter-modulus-bit-length behavior under typical assumptions.

---

## Bound precision

The article deliberately avoids the careless claim:

```text
Wiener theorem = d < N^(1/4)
```

A standard clean sufficient theorem, e.g. in Boneh's RSA attack survey, is:

```text
N = p*q
q < p < 2q
e < phi(N)
d < (1/3) * N^(1/4)
ed = 1 mod phi(N)
```

under which `d` can be efficiently recovered.

Later research refines the exact constant/boundary.

Therefore the article distinguishes:
- heuristic quarter-power scale;
- one classical sufficient theorem;
- later refined bounds.

---

## Core approximation derivation

Classical RSA relation:

```text
e*d - k*phi(N) = 1.
```

Hence:

```text
| e/phi(N) - k/d |
= 1 / (d*phi(N)).
```

For balanced primes:

```text
phi(N) = N - (p+q) + 1
```

and:

```text
|N - phi(N)| = p+q-1 = O(sqrt(N)).
```

The public ratio `e/N` is therefore close to `k/d`.

When `d` satisfies the classical small-exponent bound, the error is below the
Legendre threshold:

```text
| e/N - k/d | < 1/(2d^2),
```

forcing `k/d` to be a continued-fraction convergent of `e/N`.

---

## Vulnerable example

Checked key:

```text
p   = 379
q   = 239
N   = 90581
phi = 89964

d = 5
e = 17993
k = 1
```

Check:

```text
e*d - k*phi
= 17993*5 - 89964
= 1.
```

Prime balance:

```text
239 < 379 < 2*239.
```

Classical sufficient scale:

```text
N^(1/4)/3 ≈ 5.7828.
```

Hence:

```text
d = 5
```

lies inside the clean teaching bound.

---

## Continued-fraction values

Public ratio:

```text
17993 / 90581
```

continued fraction:

```text
[0, 5, 29, 4, 1, 3, 2, 4, 3]
```

convergents:

```text
0/1
1/5
29/146
117/589
146/735
555/2794
1256/6323
5579/28086
17993/90581
```

The second convergent is:

```text
1/5 = k/d.
```

---

## Candidate validation

For a candidate `(k,d)`:

```text
phi_candidate = (e*d - 1) / k
```

if divisible.

Then:

```text
S = N - phi_candidate + 1 = p+q.
```

The primes are roots of:

```text
x^2 - S*x + N = 0.
```

So:

```text
Delta = S^2 - 4N
```

must be a perfect square.

For the valid candidate:

```text
phi   = 89964
S     = 618
Delta = 19600
sqrt  = 140

p = (618+140)/2 = 379
q = (618-140)/2 = 239
```

This validation is stronger than "try decrypting one message."

---

## Failure experiment

Same toy modulus and `phi`, but:

```text
e = 65537
d = e^(-1) mod phi = 26801.
```

This controlled textbook key has:

```text
d >> N^(1/4)/3.
```

The exact same continued-fraction attack returns:

```text
None.
```

This demonstrates that continued fractions do not generically break RSA.

---

## phi versus lambda nuance

Modern PKCS #1 represents RSA private exponents with:

```text
e*d = 1 mod lambda(N).
```

The classical Wiener proof is usually expressed with:

```text
e*d = 1 mod phi(N).
```

The tutorial intentionally uses a textbook `phi`-based vulnerable key so the
historical proof maps exactly into executable arithmetic.

The article explicitly states that switching to `lambda(N)` is not a defense
against intentionally tiny private exponents.

---

## Current standards connection

RFC 8017:
- defines valid RSA private exponent `d` through `lambda(N)`.

NIST FIPS 186-5 RSA signature key generation:
- selects `e` first;
- computes `d = e^(-1) mod LCM(p-1,q-1)`;
- requires:
  `d > 2^(nlen/2)`.

This lower bound is vastly above the Wiener quarter-power scale:

```text
N^(1/4) ~ 2^(nlen/4).
```

The article mentions this only as RSA signature key-generation standards
context, not as a universal statement about every RSA ecosystem.

---

## Later cryptanalysis

The article accurately positions:

```text
Wiener
-> continued fractions
```

before:

```text
Boneh-Durfee
-> lattice / Coppersmith-style small-root machinery
-> classical asymptotic d < N^0.292 region
```

It does not claim `0.292` is a universal finite-size break condition.

---

## Companion code

Added:

```text
repo/chapters/16_rsa_wiener_attack/
├── README.md
├── continued_fraction.py
├── attack.py
├── demo.py
└── test_attack.py
```

Implementation deliberately avoids external continued-fraction libraries.

It implements:
- Euclidean continued-fraction expansion;
- recurrence-based convergents;
- candidate `phi` reconstruction;
- discriminant/factor validation;
- complete Wiener search.

---

## Safety scope

Only fixed toy values are used.

No certificate scanning, public-key harvesting, network interaction, or
deployed-system targeting is included.

---

## Next Deep Dive

Before Boneh–Durfee, introduce the machinery:

```text
Coppersmith From Zero
-> small modular roots
-> shifted polynomials
-> coefficient lattices
-> LLL intuition
-> when modular equality becomes integer equality
```

Then use that foundation for:
- Boneh–Durfee;
- partial-factor recovery;
- short-pad / related-message cases.

---

## Publication checklist

Verify:

- Is continued-fraction construction derived from Euclid?
- Are convergents defined and computed explicitly?
- Is Legendre's approximation criterion stated?
- Is the RSA approximation derived rather than asserted?
- Are prime-balance assumptions visible?
- Is the `1/3*N^(1/4)` theorem separated from the loose `N^(1/4)` slogan?
- Can every number in the vulnerable example be reproduced?
- Does candidate validation recover both `d` and the factorization?
- Does the failure experiment use the same attack unchanged?
- Is phi-vs-lambda handled explicitly?
- Is the FIPS claim scoped to RSA signature key generation?
- Is Boneh–Durfee deferred until lattice/Coppersmith foundations exist?

Any "no" means another revision.
