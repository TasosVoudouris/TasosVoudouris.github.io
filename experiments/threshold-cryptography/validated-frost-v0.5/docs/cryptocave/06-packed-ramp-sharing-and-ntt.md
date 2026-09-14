# Packed Ramp Sharing and the NTT

The original `fft.py` contains more than an FFT exercise. Its final construction
packs three secrets into one polynomial and distributes eight evaluations. The
correct parameter profile is:

| Quantity | Value |
|---|---:|
| Field | $\mathbb F_{433}$ |
| Packed secrets | 3 |
| Random masks | 4 |
| Output shares | 8 |
| Perfect-privacy bound | Any 4 shares |
| Full reconstruction | Any 7 shares |

## Construction

Let $\alpha$ be a public anchor, let $u_1,u_2,u_3$ be secret points, and let
$r_1,\ldots,r_4$ be randomness points. Choose the unique degree-at-most-seven
polynomial satisfying

$$
f(\alpha)=0,
\qquad
f(u_j)=s_j\quad(1\leq j\leq3),
$$

and

$$
f(r_j)=\rho_j\quad(1\leq j\leq4),
$$

where the $\rho_j$ are uniform field elements. Output shares are evaluations at
eight different share points.

The public anchor is one known point. Seven output shares supply seven more,
giving eight total constraints and therefore determining the degree-seven
polynomial. The original `reconstruct()` unnecessarily required all eight
output shares; Version 0.1 accepts any seven and uses an eighth as a consistency
check when present.

## Why this is a ramp scheme

A perfect threshold scheme reveals nothing below one threshold and the whole
secret at the reconstruction threshold. A ramp scheme has an intermediate
region in which coalitions learn partial linear information.

For this construction:

| Coalition size | Independent relations learned about the three secrets |
|---:|---:|
| 0–4 | 0 |
| 5 | 1 |
| 6 | 2 |
| 7 or more | 3, hence complete reconstruction |

Version 0.1 computes these dimensions by finite-field matrix rank. Its tests
exhaustively check every coalition of sizes four through seven, not merely one
example coalition.

## Role of the NTT

The old implementation uses roots of unity of orders eight and nine in
$\mathbb F_{433}$. A number-theoretic transform evaluates polynomial
coefficients at successive powers of a root:

$$
A_j=\sum_{k=0}^{N-1}a_k\omega^{jk}\pmod{433}.
$$

Because $433-1=432$ is divisible by both eight and nine, the field contains the
needed roots. Version 0.1 provides a transparent quadratic-time NTT so that the
definition can be inspected directly. The recursive radix-two and radix-three
algorithms from the original archive remain valuable optimization material for
a later version.

Packed sharing amortizes communication across several values, but it also
changes the privacy semantics. Saying only “threshold seven” would hide the fact
that five and six shares learn partial information.

Next: [Security boundaries and roadmap](07-security-boundaries-and-roadmap.md).
