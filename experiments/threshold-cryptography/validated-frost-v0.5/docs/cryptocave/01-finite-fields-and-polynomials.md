# Finite Fields and Polynomials

Secret-sharing arithmetic is performed in a finite field rather than over
ordinary integers. Version 0.1 uses a prime field

$$
\mathbb F_p = \{0,1,\ldots,p-1\},
$$

where addition, subtraction, and multiplication are reduced modulo the prime
$p$. Every nonzero element has a multiplicative inverse, so division by a
nonzero field element is well defined.

The original demonstrations use $p=41$. For example,

$$
-5 \equiv 36 \pmod{41}, \qquad 7\cdot 6 \equiv 1 \pmod{41}.
$$

The field contains residues, not intrinsically signed integers. The function
`decode_signed` chooses the centered representative. Thus `36` is displayed as
`-5`, while the underlying field element remains `36`.

## Polynomial representation

A polynomial of degree at most $d$ has the form

$$
f(X)=a_0+a_1X+\cdots+a_dX^d,
$$

with coefficients in $\mathbb F_p$. The code stores coefficients from lowest
degree to highest degree:

```python
coefficients = [1, 2, 3]  # 1 + 2x + 3x^2
```

Horner's rule evaluates this polynomial using the recurrence

$$
r \leftarrow a_i + xr,
$$

starting from the highest coefficient. It avoids computing every power of $x$
separately:

```python
def evaluate(coefficients, point, modulus):
    result = 0
    for coefficient in reversed(coefficients):
        result = (coefficient + point * result) % modulus
    return result
```

## Lagrange interpolation

Any $d+1$ points with distinct $x$-coordinates determine one polynomial of
degree at most $d$. Given points $(x_i,y_i)$, its value at a target $x$ is

$$
f(x)=\sum_{i=1}^{m} y_i\lambda_i(x),
\qquad
\lambda_i(x)=\prod_{j\ne i}\frac{x-x_j}{x_i-x_j}.
$$

For Shamir reconstruction, the desired target is $x=0$ because the secret is
stored as $f(0)$. All denominators must be nonzero. This is why participant
identifiers must be distinct modulo $p$.

Version 0.1 explicitly rejects duplicated points and inversion of zero. The
original code could otherwise produce a misleading value or fail deep inside
the arithmetic.

## Parameters are not security parameters yet

The small fields $\mathbb F_{41}$ and $\mathbb F_{433}$ make examples easy to
inspect. They are not appropriate production parameters. Even a mathematically
correct protocol can be insecure because of its field size, group choice,
random-number generator, serialization, network protocol, or implementation.

In this version, the field layer teaches the algebra. Later threshold-signature
code must use the scalar field required by its chosen group and standard rather
than reusing $41$ merely because the Shamir example uses it.

Next: [Additive secret sharing](02-additive-secret-sharing.md).
