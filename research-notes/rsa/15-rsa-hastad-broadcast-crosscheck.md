# RSA Deep Dive III — Håstad Broadcast Attack Cross-Check

## New depth standard

The user supplied the Delfr article:

```text
Bitcoin – ECDSA signature
```

as a reference for desired technical depth and exposition.

The relevant structural qualities adopted for CryptoCave Deep Dives are:

```text
prerequisites
-> formal construction / attack model
-> mathematical derivation
-> correctness / why-it-works argument
-> explicit worked example
-> from-scratch Python implementation
-> edge/failure cases
-> security interpretation
-> historical/research context
-> mitigation
```

No text or prose is copied from Delfr.

The reference is used only as a benchmark for depth and self-containedness.

---

## User material cross-check

### Mature Cryptography I Lesson 09

The user's mature lesson states the simple broadcast attack correctly:

```text
same unrandomized message m
at least e recipients
same small exponent e
pairwise-coprime moduli
c_i = m^e mod N_i
```

CRT reconstructs:

```text
C = m^e mod product(N_i).
```

When:

```text
m^e < product(N_i)
```

the canonical CRT representative is the integer `m^e`, and the attacker takes
the integer `e`-th root.

This is preserved as the core derivation.

---

## Mature CryptoBible framing

The current RSA attack map places:

```text
Håstad broadcast
common modulus
low-exponent cases
```

under:

```text
bad / reused parameters
```

and explicitly warns against the oversimplified slogan:

```text
e=3 is insecure
```

The mature wording is:

```text
low-exponent textbook structure
+
message reuse
+
missing randomized encoding
=
exploitable algebra.
```

That framing is retained and expanded.

---

## Worked example

The public article intentionally uses an example where every individual
ciphertext undergoes modular reduction.

Message:

```text
m = 100
e = 3
m^3 = 1,000,000
```

Toy RSA moduli:

```text
N1 = 11*17 = 187
N2 = 23*29 = 667
N3 = 41*47 = 1927
```

For each modulus, `e=3` is coprime to the corresponding Carmichael value:

```text
lambda(N1) = 80
lambda(N2) = 308
lambda(N3) = 920
```

Ciphertexts:

```text
c1 = 100^3 mod 187  = 111
c2 = 100^3 mod 667  = 167
c3 = 100^3 mod 1927 = 1814
```

Pairwise GCDs are all 1.

Combined modulus:

```text
P = N1*N2*N3 = 240,352,783
```

and:

```text
m^3 = 1,000,000 < P.
```

CRT returns:

```text
C = 1,000,000.
```

Exact cube root:

```text
m = 100.
```

All values were computationally checked.

---

## Constructive CRT intermediates

For pedagogical transparency:

```text
P1 = P/N1 = 1,285,309
P2 = P/N2 =   360,349
P3 = P/N3 =   124,729
```

Inverses:

```text
P1^(-1) mod N1 = 158
P2^(-1) mod N2 = 371
P3^(-1) mod N3 = 1154
```

The article exposes these rather than treating CRT as a library call.

---

## Why e ciphertexts are sufficient

If the same representative satisfies:

```text
m < N_i
```

for each of `e` recipients, then:

```text
m^e < product_{i=1}^e N_i.
```

Hence `e` pairwise-coprime views suffice for the elementary broadcast attack.

The article explicitly states that `e` is a sufficient count, not always a
necessary one.

The actual condition is:

```text
m^e < product(observed moduli).
```

If the message is smaller, fewer ciphertexts can sometimes suffice.

---

## Failure experiment

Using only:

```text
N1 = 187
N2 = 667
```

gives:

```text
N1*N2 = 124,729
```

while:

```text
m^3 = 1,000,000.
```

CRT reconstructs:

```text
2168
```

which is not an exact cube:

```text
12^3 = 1728
13^3 = 2197.
```

The attack helper therefore raises an error instead of returning a false
plaintext.

This is deliberately included because the new Deep Dive standard should show
when an attack's assumptions fail.

---

## Pairwise-coprime nuance

If two RSA moduli are not coprime, the implementation rejects the CRT path.

More importantly, if:

```text
gcd(N_i,N_j)
```

is a non-trivial factor, the attacker has found shared-prime key-generation
failure and can factor the affected RSA moduli.

The article connects this to the earlier GCD/shared-prime lesson.

---

## Integer-root implementation

The code does not use:

```python
round(C ** (1 / e))
```

because cryptographic integers exceed reliable floating-point precision.

It implements an integer-only binary-search `integer_nth_root()` and returns:

```text
(root, exact)
```

The exactness flag is part of the attack validation.

---

## Historical precision

The public article distinguishes:

### Elementary same-message broadcast attack

```text
c_i = m^e mod N_i
-> CRT
-> exact integer root
```

### Håstad's stronger 1988 result

Håstad's paper:

```text
Solving Simultaneous Modular Equations of Low Degree
SIAM Journal on Computing 17(2), 1988, 336–341
DOI: 10.1137/0217019
```

studies systems:

```text
P_i(x) = 0 mod N_i
```

for low-degree polynomials and relatively prime moduli.

Its result is broader than the simple identical-message cube example and uses
lattice techniques.

The article does not pretend the elementary CRT argument proves the full Håstad
theorem.

---

## Modern mitigation

The article does NOT claim:

```text
simply replace e=3 with e=65537 and raw RSA becomes secure.
```

Instead:

```text
randomized standardized encoding
```

is the structural defense against same-representative broadcast algebra.

RSAES-OAEP maps repeated application messages to independently randomized
encoded representatives before RSAEP.

The conventional exponent `65537` is discussed as additional parameter context,
not a substitute for secure encoding.

---

## Companion code

Package adds:

```text
repo/chapters/15_rsa_hastad_broadcast/
├── README.md
├── attack.py
├── demo.py
└── test_attack.py
```

The code contains:

- pairwise-coprime checking;
- CRT;
- exact integer n-th root;
- simple broadcast recovery;
- verification that the recovered root reproduces every ciphertext;
- insufficient-data rejection;
- non-coprime-modulus rejection.

---

## Safety scope

All data are fixed tiny educational values.

No network scanning, deployed-key harvesting, ciphertext collection, or remote
targeting is implemented.

---

## Next RSA Deep Dive

Recommended:

```text
Wiener's Attack
-> unusually small private exponent d
-> ed - k*phi(N) = 1
-> k/d approximates e/phi(N) ~ e/N
-> continued fractions
-> candidate d validation
```

This will reconnect a new mathematical foundation—continued fractions—to RSA
cryptanalysis.

---

## Publication checklist

Before publication verify:

- Is the difference between the trivial no-wrap attack and broadcast attack clear?
- Does the reader understand why every individual ciphertext can wrap while the attack still works?
- Is the CRT uniqueness proof explicit?
- Can the reader reproduce all numerical CRT steps?
- Is the integer-root operation exact and integer-only?
- Does the two-recipient failure case explain the inequality condition?
- Is pairwise coprimality connected to shared-prime factoring?
- Is `e` ciphertexts described as sufficient rather than always necessary?
- Is the simple broadcast attack distinguished from Håstad's stronger theorem?
- Is `e=3 is broken` explicitly rejected as an oversimplification?
- Is randomized encoding presented as the structural mitigation?
- Does the code mirror the mathematical proof?

Any "no" means another revision.
