# Arithmetic on Shared Values

Shamir sharing is linear. If parties hold evaluations of $f$ and $g$, they can
add their local values:

$$
h(x_i)=f(x_i)+g(x_i).
$$

Then $h(0)=f(0)+g(0)$ and

$$
\deg h\leq\max(\deg f,\deg g).
$$

Subtraction and multiplication by a public scalar have the same property. This
is why secret sharing naturally supports linear models and the linear portions
of larger MPC computations.

## Why direct multiplication changes the threshold

Parties can multiply corresponding shares:

$$
h(x_i)=f(x_i)g(x_i).
$$

The value at zero is the desired product, but the degree changes:

$$
\deg(fg)\leq \deg f+\deg g.
$$

For two degree-four sharings,

$$
\deg(fg)\leq8,
$$

so nine shares are needed. The original code multiplied locally but then tried
to use the old five-share assumption. Version 0.1 records the new degree and
refuses to open the product with too few shares.

```python
product = x * y
print(product.degree_bound)              # 8
print(product.reconstruction_threshold)  # 9
```

Pointwise multiplication is a correct algebraic observation, but by itself it
is not a reusable MPC multiplication protocol: repeated multiplications keep
increasing the degree.

## Beaver multiplication

A Beaver triple consists of shared random values

$$
[a],\quad[b],\quad[c],
\qquad c=ab.
$$

To multiply private $x$ and $y$, parties open masked differences

$$
d=x-a,
\qquad
e=y-b,
$$

and compute

$$
[xy]=[c]+d[b]+e[a]+de.
$$

Expanding the right side yields

$$
ab+(x-a)b+(y-b)a+(x-a)(y-b)=xy.
$$

Only multiplications by public values occur online, so the result remains at the
original Shamir degree.

Version 0.1 implements this equation in `mpc.py`, but generates triples through
one trusted local function. This is an educational passive-model demonstration,
not SPDZ. A real malicious-secure system must generate and authenticate triples,
verify openings, prevent reuse, and run between independently isolated parties.

## A strict one-time rule

The same triple must never be reused. If two multiplications reveal $x-a$ and
$x'-a$ with the same mask $a$, their difference reveals $x-x'$. Production
protocols therefore treat preprocessing material as single-use state.

Next: [Consistency and robust reconstruction](05-consistency-and-robust-reconstruction.md).
