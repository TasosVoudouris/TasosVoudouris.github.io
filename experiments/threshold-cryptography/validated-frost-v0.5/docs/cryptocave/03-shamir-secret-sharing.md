# Shamir Secret Sharing

A $\tau$-out-of-$n$ Shamir scheme stores the secret as the constant term of a
random polynomial of degree at most $\tau-1$:

$$
f(X)=s+a_1X+\cdots+a_{\tau-1}X^{\tau-1},
$$

where $a_1,\ldots,a_{\tau-1}$ are independently uniform in $\mathbb F_p$. Party
$i$ receives the labelled share

$$
(x_i,f(x_i)),
$$

for a distinct, nonzero identifier $x_i$.

## The main correction to the original code

The original scripts defined `T = 4` and sampled four random coefficients above
the secret. Therefore `T` was the polynomial degree, not the reconstruction
threshold. A degree-four polynomial requires five points:

$$
\deg f=4,
\qquad
\tau=\deg f+1=5.
$$

Version 0.1 says this directly:

```python
scheme = ShamirScheme(
    modulus=41,
    num_parties=10,
    threshold=5,
)

assert scheme.degree == 4
```

## Correctness

Any five valid shares give five points on a degree-at-most-four polynomial.
Lagrange interpolation recovers $f(0)=s$. The tests enumerate all

$$
\binom{10}{5}=252
$$

five-share coalitions and confirm that every one reconstructs.

## Privacy below the threshold

Four shares give only four constraints on a polynomial with five coefficients.
For every guessed secret $s'\in\mathbb F_p$, there is exactly one degree-at-most
four polynomial passing through $(0,s')$ and the four observed points.
Consequently, those shares are compatible with every secret. The random
coefficients make all candidates equally likely.

This is information-theoretic privacy: it does not depend on a computational
hardness assumption. It does depend on correct independent randomness and an
honest sharing procedure.

## Why labels matter

A share is not just a field value. Its $x$-coordinate determines its Lagrange
coefficient. Treating list position as party identity can silently reconstruct
the wrong value after reordering, deletion, or transmission.

Version 0.1 uses:

```python
Share(x=3, y=27)
```

It rejects duplicate, zero, and unknown identifiers. Shares may be safely
reordered because interpolation uses their labels.

## Privacy is not robustness

Five received values always define some degree-four polynomial. If one of those
values was changed, the decoder has no redundancy with which to detect it. More
shares allow a consistency check, but locating and correcting bad shares needs
coding-theoretic decoding and a sufficient distance bound.

Shamir sharing alone also cannot prove that a malicious dealer gave all honest
participants shares of one polynomial. Versions 0.2 and 0.3 add Feldman and
Pedersen verification layers for that lesson.

Next: [Arithmetic and multiplication](04-arithmetic-and-multiplication.md).
