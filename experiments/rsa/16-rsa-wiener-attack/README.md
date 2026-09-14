# Chapter 16 — Wiener's RSA Attack

Executable companion to:

> **RSA Deep Dive IV: Wiener's Attack From Zero**

The chapter derives and implements the classical continued-fraction attack on
RSA with an abnormally small private exponent.

## Structure

```text
continued_fraction.py
    Euclidean algorithm
    -> continued-fraction terms
    -> convergents

attack.py
    convergents k/d
    -> candidate phi(N)
    -> candidate p+q
    -> quadratic discriminant
    -> factor validation

demo.py
    vulnerable key
    -> full convergent trace
    -> d recovery
    -> factor recovery
    -> RSA decryption check
    -> normal-sized-d failure experiment

test_attack.py
    unit and end-to-end tests
```

## Vulnerable toy key

```text
p   = 379
q   = 239
N   = 90581
phi = 89964

d   = 5
e   = 17993
```

The public ratio is:

```text
e/N = 17993/90581
```

with continued fraction:

```text
[0, 5, 29, 4, 1, 3, 2, 4, 3]
```

One convergent is:

```text
1/5
```

which equals:

```text
k/d.
```

Validation reconstructs:

```text
phi = 89964
p+q = 618
Delta = 19600 = 140^2
p = 379
q = 239
```

## Run

From the repository root:

```powershell
python chapters/16_rsa_wiener_attack/demo.py
```

Tests:

```powershell
pytest chapters/16_rsa_wiener_attack/test_attack.py -q
```

## Scope

This is fixed toy arithmetic for education.

It does not fetch public keys, scan certificates, target remote systems, or
attempt to attack deployed RSA infrastructure.

## Historical note

Wiener's 1990 attack uses continued fractions to exploit a small private
exponent.  The standard clean teaching theorem assumes balanced primes and a
private exponent below a constant times `N^(1/4)`.

Later lattice-based attacks, especially Boneh–Durfee, extend the vulnerable
small-private-exponent region.

Those require Coppersmith/LLL machinery and are deliberately deferred.
