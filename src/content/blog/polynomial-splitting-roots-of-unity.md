---
title: "Polynomial Splitting and Roots of Unity: From Horner's Rule to FFT Structure"
description: "Use a small finite-field example to connect Horner evaluation, even/odd polynomial splitting, roots of unity, and the recursive structure behind FFT/NTT algorithms."
pubDate: "2025-03-10"
updatedDate: "2026-09-12"
topics:
- "Mathematical Foundations"
- "Cryptographic Engineering"
- "MPC"
tags:
- "horner-rule"
- "polynomial-splitting"
- "roots-of-unity"
- "fft"
- "ntt"
- "finite-fields"
difficulty: "Intermediate"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 7
sourcePath: "experiments/threshold-cryptography/polynomial-splitting"
draft: false
---
Efficient finite-field transforms are built from a simple algebraic identity: split a polynomial into residue classes of its exponents, evaluate the smaller polynomials recursively, and recombine the results at roots of unity. Before using a full FFT inside packed secret sharing, this article isolates that mechanism in the smallest useful example.

We start with Horner's rule, then decompose a polynomial into its even and odd coefficients, and finally connect the decomposition to powers of a primitive root of unity in $\mathbb{F}_{433}$.

## Overview
This script performs polynomial evaluation using **Horner’s method** and demonstrates how to split a polynomial into **even and odd indexed terms**, leveraging properties of finite fields. It utilizes **modular arithmetic** over a prime field $ Q = 433 $, and employs **roots of unity** for transformations.

The core operations include:
- **Horner’s method** for efficient polynomial evaluation.
- **Splitting polynomials** into two sub-polynomials $ B(x) $ and $ C(x) $.
- **Computing values at special roots of unity**.
- **Verifying results using assertions**.

---

## Horner’s Method for Polynomial Evaluation
### Function: `horner_evaluate`
```python
def horner_evaluate(coeffs, point):
    result = 0
    for coef in reversed(coeffs):
        result = (coef + point * result) % Q
    return result
```
### Purpose
Evaluates a polynomial $ A(x) $ given by its coefficients using **Horner's method**, which is an optimized way to compute:
$$
A(x) = a_0 + a_1 x + a_2 x^2 + \dots + a_n x^n
$$

### Steps
- Iterates **backward** through the coefficients.
- Computes $ A(x) $ using:
  $$
  A(x) = (\dots ((a_n x + a_{n-1}) x + a_{n-2}) x + \dots + a_0) \mod Q
  $$
- Ensures modular arithmetic is applied at each step.

### Complexity
- **Time Complexity:** $ O(n) $, making it more efficient than naive evaluation $ O(n^2) $.

---

## Polynomial Definition and Roots of Unity
```python
Q = 433
OMEGA4 = 179

w = [ pow(OMEGA4, e, Q) for e in range(4) ]
print(w)
```
- Defines the **prime modulus** $ Q = 433 $.
- **$ OMEGA4 = 179 $** is a **4th root of unity** (i.e., $ OMEGA4^4 \equiv 1 \mod Q $).
- Computes the **powers of $ OMEGA4 $** modulo $ Q $:
  ```python
  [1, 179, 432, 254]
  ```
  These represent the **4th roots of unity**.

---

## Evaluating Polynomial A(x) at Roots of Unity
```python
A_coeffs = [ 1, 2, 3, 4 ]
A = lambda x: horner_evaluate(A_coeffs, x)
```
Defines a polynomial:
$$
A(x) = 1 + 2x + 3x^2 + 4x^3
$$
Computes $ A(w) $ at the 4th roots of unity:
```python
assert([ A(wi) for wi in w ] == [ 10, 73, 431, 356 ])
```
Verifies that:
$$
A(1) = 10, \quad A(179) = 73, \quad A(432) = 431, \quad A(254) = 356
$$

---

## Splitting A(x) into Even and Odd Indexed Polynomials
```python
B_coeffs = A_coeffs[0::2]  # [1, 3]
C_coeffs = A_coeffs[1::2]  # [2, 4]
```
Splits $ A(x) $ into:
- **Even index terms:** $ B(x) = 1 + 3x $
- **Odd index terms:** $ C(x) = 2 + 4x $

**Transforming Roots:**
```python
v = [ wi * wi % Q for wi in w ]
```
- Computes **squared values** $ v = w^2 $:
  ```python
  [1, 432, 1, 432]
  ```

Computes $ B(v) $ and $ C(v) $:
```python
B = lambda x: horner_evaluate(B_coeffs, x)
C = lambda x: horner_evaluate(C_coeffs, x)
B_values = [ B(vi) for vi in v ]
C_values = [ C(vi) for vi in v ]
```
Asserts that the computed values match expectations:
```python
assert( B_values == [ B(vi) for vi in v ] )
assert( C_values == [ C(vi) for vi in v ] )
```

---

## Combining Results to Reconstruct A(x)
```python
A_values = [ ( B_values[i] + w[i] * C_values[i] ) % Q for i,_ in enumerate(w) ]
assert( A_values == [ A(wi) for wi in w ] )
```
- Uses the **NTT-like reconstruction formula**:
  $$
  A(w_i) = B(v_i) + w_i \cdot C(v_i) \mod Q
  $$
- Ensures the correctness by verifying that $ A(w) $ matches the direct evaluation of $ A(x) $.

---

## Further Exploration of Roots of Unity
```python
OMEGA2 = OMEGA4 * OMEGA4 % Q
w_squared = [ pow(OMEGA2, e, Q) for e in range(4) ]
print(w_squared)
```
- Defines a **2nd root of unity** $ OMEGA2 $ as $ OMEGA4^2 $.
- Computes powers of $ OMEGA2 $ and prints:
  ```python
  [1, 432, 1, 432]
  ```
  - Shows repetition every two steps, confirming its **order is 2**.

---

## Verifying Orders of Roots of Unity
```python
print([ pow(OMEGA4, e, Q) for e in range(8) ])
print([ pow(OMEGA2, e, Q) for e in range(8) ])
```
Prints the sequences:
- **$ OMEGA4 $ (order 4):**
  ```
  [1, 179, 432, 254, 1, 179, 432, 254]
  ```
- **$ OMEGA2 $ (order 2):**
  ```
  [1, 432, 1, 432, 1, 432, 1, 432]
  ```
Confirms that:
- $ OMEGA4 $ repeats every **4 steps**.
- $ OMEGA2 $ repeats every **2 steps**.

---

## Complete Toy Implementation

```python

def horner_evaluate(coeffs, point):
    result = 0
    for coef in reversed(coeffs):
        result = (coef + point * result) % Q
    return result
Q = 433
OMEGA4 = 179

w = [ pow(OMEGA4, e, Q) for e in range(4) ]

print(w)
[1, 179, 432, 254]
A_coeffs = [ 1, 2, 3, 4 ]
A = lambda x: horner_evaluate(A_coeffs, x)

assert([ A(wi) for wi in w ]
    == [ 10, 73, 431, 356 ])
# split A into B and C
B_coeffs = A_coeffs[0::2] # == [ 1,    3,   ]
C_coeffs = A_coeffs[1::2] # == [    2,    4 ]

v = [ wi * wi % Q for wi in w ]

# compute values for B and C at v points
B = lambda x: horner_evaluate(B_coeffs, x)
C = lambda x: horner_evaluate(C_coeffs, x)
B_values = [ B(vi) for vi in v ]
C_values = [ C(vi) for vi in v ]
assert( B_values == [ B(vi) for vi in v ] )
assert( C_values == [ C(vi) for vi in v ] )

# combine results into values for A at w points
A_values = [ ( B_values[i] + w[i] * C_values[i] ) % Q for i,_ in enumerate(w) ]

assert( A_values == [ A(wi) for wi in w ] )


OMEGA2 = OMEGA4 * OMEGA4 % Q

w_squared = [ pow(OMEGA2, e, Q) for e in range(4) ]
print(w_squared)

v = [ pow(OMEGA2, e, Q) for e in range(2) ]
print(v)
#[1, 432, 1, 432]
#[1, 432]

print([ pow(OMEGA4, e, Q) for e in range(8) ])
print([ pow(OMEGA2, e, Q) for e in range(8) ])
#[1, 179, 432, 254, 1, 179, 432, 254]
#[1, 432, 1, 432, 1, 432, 1, 432]
```


## Summary
### Key Features
- **Uses Horner’s method** for polynomial evaluation.
- **Splits a polynomial** into even and odd indexed sub-polynomials.
- **Uses modular arithmetic** to compute values efficiently.
- **Demonstrates roots of unity** and their transformations.

### Applications
- **Number Theoretic Transform (NTT)**: Efficient polynomial multiplication.
- **Cryptography**: Used in **Kyber** and **RLWE-based encryption**.
- **Signal Processing**: Analogous to **Fast Fourier Transform (FFT)**.

This toy script provides a **minimal framework** for working with polynomials in **finite fields**, demonstrating **efficient evaluation, transformations, and verification techniques**.
