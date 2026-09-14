# Chapter 17 — Coppersmith From Zero

Executable companion to:

> **RSA Deep Dive V: Coppersmith From Zero**

The goal is not to wrap SageMath's `small_roots()`.

The chapter exposes the mechanism:

```text
small modular root
-> shifted polynomial relations
-> variable scaling by X
-> coefficient lattice
-> exact LLL
-> short polynomial
-> divisibility + norm bound
-> integer zero
-> root recovery
```

## Toy RSA instance

```text
p = 30011
q = 35027

N = 1051195297
e = 3

known prefix = 12000
hidden x0    = 37
message      = 12037

X = 100
ciphertext = 100336930
```

Build:

```text
f(x) = (12000+x)^3 - ciphertext.
```

Then:

```text
f(37) = 0 mod N
```

while:

```text
f(37) != 0 over Z.
```

## Lattice

For:

```text
degree(f) = 3
m = 2
t = 1
```

the seven shift polynomials are:

```text
N^2
N^2*x
N^2*x^2
N*f
N*x*f
N*x^2*f
f^2
```

All evaluate to multiples of:

```text
N^2
```

at the hidden root.

The variable substitution:

```text
x -> X*x
```

weights degree `i` coefficients by `X^i`.

## LLL

`lll.py` implements a tiny exact LLL reducer using:

```python
fractions.Fraction
```

for Gram-Schmidt arithmetic.

No Sage, `fpylll`, or SymPy lattice reduction is used.

The implementation is intentionally educational and should not be used for
large cryptanalytic lattices.

## Run

```powershell
python chapters/17_rsa_coppersmith_from_zero/demo.py
```

Tests:

```powershell
pytest chapters/17_rsa_coppersmith_from_zero/test_attack.py -q
```

## Scope

This is a fixed local toy experiment.

It does not scan public RSA keys, collect ciphertexts, attack certificates, or
target deployed infrastructure.

## Research references

- Don Coppersmith, "Finding a Small Root of a Univariate Modular Equation,"
  EUROCRYPT 1996, LNCS 1070, pp. 155–165.
- Don Coppersmith, "Small Solutions to Polynomial Equations, and Low Exponent
  RSA Vulnerabilities," Journal of Cryptology 10(4), 1997, pp. 233–260.
- Nick Howgrave-Graham, "Finding Small Roots of Univariate Modular Equations
  Revisited," Cryptography and Coding 1997, LNCS 1355, pp. 131–142.
- A. K. Lenstra, H. W. Lenstra Jr., L. Lovász, "Factoring Polynomials with
  Rational Coefficients," Mathematische Annalen 261, 1982, pp. 515–534.
