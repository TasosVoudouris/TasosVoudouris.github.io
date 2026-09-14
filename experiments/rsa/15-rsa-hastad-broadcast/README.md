# Chapter 15 — RSA Håstad Broadcast Attack

This chapter is the executable companion to:

> **RSA Deep Dive III: Håstad's Broadcast Attack**

It demonstrates the simple textbook broadcast setting:

\[
c_i = m^e \bmod N_i
\]

for the **same raw message representative** \(m\), the same small exponent
\(e=3\), and pairwise-coprime RSA moduli.

The chapter implements from scratch:

- pairwise-GCD validation;
- the constructive Chinese Remainder Theorem;
- exact integer \(n\)-th roots using integer-only binary search;
- the simple Håstad broadcast recovery;
- negative tests showing when the simple recovery assumptions are not met.

## Run

From the repository root:

```powershell
python chapters/15_rsa_hastad_broadcast/demo.py
```

Tests:

```powershell
pytest chapters/15_rsa_hastad_broadcast/test_attack.py -q
```

## Checked toy data

```text
m  = 100
e  = 3

N1 = 187
N2 = 667
N3 = 1927

c1 = 111
c2 = 167
c3 = 1814
```

CRT reconstructs:

```text
C = 1,000,000 = 100^3
```

and the exact cube root yields:

```text
m = 100
```

Using only the first two ciphertexts gives:

```text
CRT result = 2168
```

which is not an exact cube, so the simple attack correctly rejects that case.

## Scope

Educational toy only.

This chapter does not scan for RSA keys, collect real ciphertexts, or target
deployed systems.  Its purpose is to make the algebra of the broadcast attack
explicit and reproducible.

## Important historical nuance

The simple same-message CRT attack is the standard introductory form associated
with Håstad's broadcast result.

Håstad's 1988 paper is stronger: it studies simultaneous low-degree polynomial
congruences and shows that predictable algebraic padding/relations can also be
dangerous for low-exponent RSA.

That stronger lattice-based direction is deferred until the project develops
LLL and Coppersmith-style small-root methods.
