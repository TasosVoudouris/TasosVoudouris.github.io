---
title: "The Geffe Generator: How Correlation Breaks a Nonlinear Combination of LFSRs"
description: "Construct the Geffe combiner, derive its 3/4 input correlations, interpret the bias through Boolean-function and Walsh viewpoints, compare naive and divide-and-conquer search costs, and show why nonlinearity without correlation immunity is insufficient."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Randomness & Entropy"
  - "Cryptanalysis"
  - "Symmetric Cryptography"
  - "Mathematical Foundations"
tags:
  - "geffe-generator"
  - "correlation-attack"
  - "lfsr"
  - "stream-cipher"
  - "correlation-immunity"
  - "boolean-functions"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 4
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---

## Table of Contents

- [From Linear Registers to a Nonlinear Combiner](#from-linear-registers-to-a-nonlinear-combiner)
- [Truth Table, Algebraic Normal Form, and the 3/4 Correlations](#truth-table-algebraic-normal-form-and-the-34-correlations)
- [Correlation Attacks as Divide-and-Conquer Cryptanalysis](#correlation-attacks-as-divide-and-conquer-cryptanalysis)
- [How Much Keystream Is Needed?](#how-much-keystream-is-needed)
- [Period: LCM, Product Conditions, and a Common Overstatement](#period-lcm-product-conditions-and-a-common-overstatement)
- [Correlation Immunity and Boolean-Function Design](#correlation-immunity-and-boolean-function-design)
- [Executable Toy Attack](#executable-toy-attack)
- [Conclusion](#conclusion)
- [References](#references)

---

## From Linear Registers to a Nonlinear Combiner

The previous article showed why a raw LFSR fails as a cryptographic keystream generator.

Even when its connection polynomial is primitive and its period is

$$
2^L-1,
$$

its output obeys a short linear recurrence over

$$
\mathbb F_2.
$$

That suggests an apparently natural repair:

> use several LFSRs and combine their output bits through a nonlinear Boolean function.

The **Geffe generator** is a classic example of why that idea is not enough by itself.

Let three LFSRs produce one bit each at time $i$:

$$
x_i,\qquad y_i,\qquad z_i.
$$

The Geffe combining function is

$$
F(x,y,z)
=
xy
\oplus
(1\oplus x)z.
$$

Equivalently,

$$
F(x,y,z)
=
xy
\oplus
z
\oplus
xz.
$$

The output keystream bit is:

$$
k_i=F(x_i,y_i,z_i).
$$

### Selector interpretation

The easiest way to understand the function is not through its algebraic normal form but as a multiplexer:

- if $x=1$, output $y$;
- if $x=0$, output $z$.

Indeed, when $x=1$,

$$
F(1,y,z)
=
y
\oplus
0
=
y.
$$

When $x=0$,

$$
F(0,y,z)
=
0
\oplus
z
=
z.
$$

So $x$ is a selector and $y,z$ are the two data inputs.

Conceptually:

```text
                 x
                 |
            +----+----+
            | selector |
            +----+----+
               /   \
              /     \
             y       z
              \     /
               \   /
                output
```

### Why this looks promising at first

The function is nonlinear because its algebraic normal form contains degree-two terms:

$$
xy
$$

and:

$$
xz.
$$

That means the combined keystream is no longer a simple XOR of the three input sequences.

A direct Berlekamp–Massey attack on one component recurrence no longer reconstructs the full output in the obvious way.

That is progress.

But cryptography does not ask only:

> is the function nonlinear?

It asks whether the output leaks **statistically exploitable information** about the component sequences.

For Geffe, the answer is yes.

---

## Truth Table, Algebraic Normal Form, and the 3/4 Correlations

Assume for the moment that:

$$
X,Y,Z
$$

are independent uniformly random bits.

The Geffe output is:

$$
G=F(X,Y,Z).
$$

Its complete truth table is:

| $x$ | $y$ | $z$ | $F(x,y,z)$ |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 0 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |
| 1 | 1 | 1 | 1 |

The table makes the selector interpretation obvious:

```text
x = 0 -> F = z
x = 1 -> F = y
```

### Correlation with $Y$

Condition on the selector bit.

When:

$$
X=1,
$$

the output equals $Y$ exactly:

$$
F=Y.
$$

So:

$$
\Pr[F=Y\mid X=1]=1.
$$

When:

$$
X=0,
$$

the output is:

$$
F=Z.
$$

Since $Y$ and $Z$ are independent unbiased bits,

$$
\Pr[Z=Y]=\frac12.
$$

Therefore:

$$
\Pr[F=Y]
=
\Pr[X=1]\cdot1
+
\Pr[X=0]\cdot\frac12.
$$

With unbiased $X$:

$$
\Pr[X=1]
=
\Pr[X=0]
=
\frac12,
$$

so:

$$
\Pr[F=Y]
=
\frac12
+
\frac14
=
\boxed{\frac34}.
$$

### Correlation with $Z$

The argument is symmetric.

When:

$$
X=0,
$$

we have:

$$
F=Z
$$

with probability 1.

When:

$$
X=1,
$$

the output equals $Y$, which matches $Z$ with probability $1/2$.

Thus:

$$
\boxed{
\Pr[F=Z]=\frac34.
}
$$

### Correlation with the selector $X$

Now compare $F$ with $X$.

Under independent unbiased inputs:

$$
\Pr[F=X]
=
\frac12.
$$

So there is no analogous first-order bias toward the selector bit.

This is why the direct correlation attack targets the $y$- and $z$-registers first.

### Bias versus correlation coefficient

It is useful to distinguish two related quantities.

The **agreement probability** with $Y$ is:

$$
p=\frac34.
$$

The **bias** above random guessing is:

$$
\epsilon
=
p-\frac12
=
\frac14.
$$

Another common cryptanalytic quantity is the $\{-1,+1\}$ correlation coefficient:

$$
\rho
=
\mathbb E[
(-1)^{F\oplus Y}
].
$$

If $F=Y$, the exponent is 0 and contributes $+1$.

If $F\ne Y$, it contributes $-1$.

Therefore:

$$
\rho
=
\Pr[F=Y]
-
\Pr[F\ne Y].
$$

So:

$$
\rho
=
\frac34-\frac14
=
\boxed{\frac12}.
$$

The same holds for $Z$.

The relationships are:

$$
\rho=2\epsilon
$$

when $\epsilon$ is defined as agreement probability minus $1/2$, and:

$$
\Pr[F=Y]
=
\frac{1+\rho}{2}.
$$

### Walsh-spectrum viewpoint

For a Boolean function:

$$
f:\mathbb F_2^n\rightarrow\mathbb F_2,
$$

the Walsh transform at mask $a$ is:

$$
W_f(a)
=
\sum_{u\in\mathbb F_2^n}
(-1)^{f(u)\oplus a\cdot u}.
$$

For $n=3$, the correlation with a single input bit is visible directly in the Walsh coefficient associated with that coordinate.

For Geffe:

$$
W_F(e_y)=4,
$$

$$
W_F(e_z)=4,
$$

while:

$$
W_F(e_x)=0.
$$

Since there are:

$$
2^3=8
$$

input triples,

$$
\frac{W_F(e_y)}{8}
=
\frac12
$$

is exactly the correlation coefficient derived above.

This spectral viewpoint becomes important in the study of Boolean combining functions because correlation immunity can be characterized by vanishing low-weight Walsh coefficients.

### Balanced output does not save the design

The Geffe output itself is balanced:

$$
\Pr[F=0]
=
\Pr[F=1]
=
\frac12.
$$

So a simple frequency test sees no obvious bias.

That is a very important lesson.

The output can be perfectly balanced while still leaking substantial information about internal component sequences.

Thus:

$$
\boxed{
\text{balanced output}
\neq
\text{correlation immunity}.
}
$$

---

## Correlation Attacks as Divide-and-Conquer Cryptanalysis

Suppose the three LFSRs have state lengths:

$$
L_x,\qquad L_y,\qquad L_z.
$$

Assume their connection polynomials are known and their initial nonzero states are secret.

A naive attacker could enumerate the complete joint state:

$$
(x\text{-state},y\text{-state},z\text{-state}).
$$

The nominal search space is approximately:

$$
2^{L_x+L_y+L_z}.
$$

For maximal LFSRs, the exact nonzero-state count is:

$$
(2^{L_x}-1)
(2^{L_y}-1)
(2^{L_z}-1),
$$

but powers of two are sufficient for exponent-level intuition.

### The correlation changes the attack structure

Because:

$$
\Pr[F=Y]=\frac34,
$$

the attacker can search the $y$-register **independently**.

For each candidate initial state $s_y$:

1. generate the candidate LFSR sequence:

   $$
   Y^{(s_y)}_1,\ldots,Y^{(s_y)}_N;
   $$

2. compare it with the observed Geffe keystream:

   $$
   F_1,\ldots,F_N;
   $$

3. compute the agreement count:

   $$
   A_y(s_y)
   =
   \sum_{i=1}^{N}
   \mathbf 1[
   Y^{(s_y)}_i=F_i
   ].
   $$

For the correct state, the expected score is:

$$
\mathbb E[A_y]
\approx
\frac34N.
$$

For an unrelated wrong state, the agreement behaves approximately like:

$$
\frac12N.
$$

The true state should therefore stand out statistically.

### Search the $z$-register independently

Exactly the same attack works against $z$:

$$
\Pr[F=Z]=\frac34.
$$

So the attacker performs another search over:

$$
2^{L_z}
$$

states rather than searching $y$ and $z$ jointly.

### Recover the selector last

Once $y$ and $z$ are known, the remaining selector sequence can be attacked separately.

At positions where:

$$
y_i\ne z_i,
$$

the output determines $x_i$ exactly.

If:

$$
F_i=y_i,
$$

then:

$$
x_i=1.
$$

If:

$$
F_i=z_i,
$$

then:

$$
x_i=0.
$$

At positions where:

$$
y_i=z_i,
$$

the output does not reveal the selector because both branches produce the same bit.

One can therefore:

- derive partial selector information and solve for its LFSR state;
- or simply enumerate $2^{L_x}$ selector states and test which reproduces the full output.

For a toy attack, exhaustive search over the final selector state is very clear.

### Complexity comparison

Naive joint search:

$$
\boxed{
O(
N2^{L_x+L_y+L_z}
)
}
$$

bit-comparison work.

Simple correlation divide-and-conquer:

$$
\boxed{
O(
N(
2^{L_y}
+
2^{L_z}
+
2^{L_x}
)
)
}
$$

in the direct exhaustive-ranking version.

The exponential security exponent has changed dramatically.

If:

$$
L_x=L_y=L_z=L,
$$

then naive search is approximately:

$$
2^{3L},
$$

while the divide-and-conquer attack is roughly:

$$
3\cdot2^L
$$

candidate streams, times the amount of observed data.

That is not a small optimization.

It is an exponential collapse.

### Why "nonlinear" was not enough

The Geffe function has algebraic degree:

$$
2.
$$

So it is genuinely nonlinear.

But it leaks:

$$
\Pr[F=Y]
=
\Pr[F=Z]
=
\frac34.
$$

Cryptographic Boolean functions are evaluated along several dimensions simultaneously:

- balancedness;
- nonlinearity;
- correlation immunity;
- algebraic degree;
- algebraic immunity;
- resilience.

Optimizing only one property can leave another attack surface exposed.

---

## How Much Keystream Is Needed?

A correlation attack needs enough observed output to distinguish:

$$
p=\frac34
$$

from:

$$
p=\frac12.
$$

The exact data complexity depends on:

- register length;
- number of candidates;
- correlation structure of the sequences;
- decision threshold;
- acceptable false-positive probability;
- attack algorithm.

Still, a simple independent-Bernoulli model provides useful intuition.

### Correct-state score

For the correct $y$-state, idealize the agreement count as:

$$
A_{\text{true}}
\sim
\operatorname{Binomial}
\left(
N,\frac34
\right).
$$

Then:

$$
\mathbb E[A_{\text{true}}]
=
\frac34N,
$$

and:

$$
\operatorname{Var}(A_{\text{true}})
=
N\frac34\frac14
=
\frac{3N}{16}.
$$

So the standard deviation is:

$$
\sigma_{\text{true}}
=
\frac{\sqrt{3N}}{4}.
$$

### Wrong-state score

For an approximately unrelated wrong candidate:

$$
A_{\text{wrong}}
\sim
\operatorname{Binomial}
\left(
N,\frac12
\right).
$$

Then:

$$
\mathbb E[A_{\text{wrong}}]
=
\frac12N,
$$

$$
\sigma_{\text{wrong}}
=
\frac{\sqrt N}{2}.
$$

The expected score gap is:

$$
\frac14N.
$$

The gap grows linearly in $N$, while standard deviations grow only as:

$$
\sqrt N.
$$

So the signal-to-noise separation improves as more keystream is observed.

### A simple threshold

Take the midpoint:

$$
\tau
=
\frac58.
$$

Accept a candidate if its agreement fraction exceeds:

$$
\frac58.
$$

For the correct state, this threshold is:

$$
\frac18
$$

below its mean probability $3/4$.

For a wrong state, it is:

$$
\frac18
$$

above $1/2$.

Hoeffding's inequality gives the rough bound:

$$
\Pr[
A_{\text{wrong}}\ge \tfrac58N
]
\le
e^{-N/32}.
$$

Similarly:

$$
\Pr[
A_{\text{true}}\le \tfrac58N
]
\le
e^{-N/32}.
$$

If there are about:

$$
2^L
$$

wrong states, a crude union bound gives:

$$
2^Le^{-N/32}
$$

for at least one wrong state crossing the threshold.

To make this small, one would like roughly:

$$
N
\gtrsim
32(
L\ln2+\ln(1/\delta)
).
$$

This is **not** an exact Geffe attack theorem.

It treats candidate sequences as independent Bernoulli trials, which real LFSR sequences are not.

Its purpose is to explain why a fixed $1/4$ bias can be detected with a manageable amount of data.

### Bias is a resource

The attack is possible because:

$$
\epsilon
=
\frac14
$$

is large.

For weaker biases, more data is required.

Roughly speaking, many statistical distinguishers need data scaling like:

$$
O(\epsilon^{-2})
$$

to resolve a bias $\epsilon$.

This idea appears repeatedly in stream-cipher cryptanalysis.

Tiny biases may still matter if:

- enough keystream is available;
- many sessions can be aggregated;
- the same bias repeats under many keys/nonces;
- the adversary can average noise away.

RC4, later in the series, will provide a famous real-world example.

---

## Period: LCM, Product Conditions, and a Common Overstatement

Older descriptions of the Geffe generator often write its period as:

$$
(2^{L_x}-1)
(2^{L_y}-1)
(2^{L_z}-1).
$$

That expression requires assumptions.

### Component periods

Let the three LFSR periods be:

$$
T_x,\qquad T_y,\qquad T_z.
$$

The joint internal state:

$$
(X_i,Y_i,Z_i)
$$

must repeat after a number of clocks divisible by all three component periods.

Therefore the joint-state period is:

$$
\boxed{
\operatorname{lcm}
(
T_x,T_y,T_z
)
}
$$

assuming each component begins on a cycle of the stated period.

### Output period

The output is a deterministic function of the joint state.

Therefore the Geffe output period must **divide** the joint-state period:

$$
T_F
\mid
\operatorname{lcm}
(
T_x,T_y,T_z
).
$$

It can equal that value, but equality is not automatic.

A combining function can collapse multiple joint states into identical output behavior and create a shorter output period.

### When does the product appear?

If:

$$
T_x,T_y,T_z
$$

are pairwise coprime, then:

$$
\operatorname{lcm}
(
T_x,T_y,T_z
)
=
T_xT_yT_z.
$$

For maximal LFSRs:

$$
T_x=2^{L_x}-1,
$$

$$
T_y=2^{L_y}-1,
$$

$$
T_z=2^{L_z}-1.
$$

A useful identity is:

$$
\gcd(
2^a-1,
2^b-1
)
=
2^{\gcd(a,b)}-1.
$$

Therefore if the register lengths are pairwise coprime:

$$
\gcd(L_i,L_j)=1,
$$

then their maximal periods are pairwise coprime.

In that case the **joint state** has product period.

The output may also achieve that period for nondegenerate choices, but it should still be checked rather than asserted from the lengths alone.

### Period is still not the security argument

Even if the combined period is enormous, the correlation attack may recover component states with far less than exhaustive joint search.

This repeats a lesson from both LCGs and raw LFSRs:

$$
\boxed{
\text{large period}
\neq
\text{large cryptanalytic work factor}.
}
$$

---

## Correlation Immunity and Boolean-Function Design

The Geffe generator motivated a broader design criterion: **correlation immunity**.

Let:

$$
f:\mathbb F_2^n\rightarrow\mathbb F_2.
$$

Informally, $f$ is correlation immune of order $t$ if its output is statistically independent of every subset of at most $t$ input variables when the inputs are uniform.

### First-order correlation immunity

For order 1, the output must be independent of every single input coordinate.

That means observing:

$$
f(X_1,\ldots,X_n)
$$

must not provide statistical information about any one:

$$
X_i.
$$

The Geffe function fails immediately because:

$$
\Pr[F=Y]
=
\frac34
$$

and:

$$
\Pr[F=Z]
=
\frac34.
$$

It is therefore not first-order correlation immune.

The fact that:

$$
\Pr[F=X]
=
\frac12
$$

does not help.

Correlation immunity of order 1 requires independence from **all** individual inputs, not merely one of them.

### Balancedness and resiliency

A Boolean function is **balanced** when it outputs zero and one equally often.

A function that is both:

- balanced;
- correlation immune of order $t$;

is commonly called **$t$-resilient**.

Geffe is balanced but not 1-resilient.

### Walsh characterization

Correlation immunity can be studied through the Walsh spectrum.

For a correlation-immune function of order $t$, the Walsh coefficients associated with masks of Hamming weight:

$$
1,\ldots,t
$$

must vanish.

Geffe has nonzero Walsh coefficients for the $y$- and $z$-coordinate masks, revealing the weakness immediately.

This is a much more systematic design tool than checking a few conditional probabilities by hand.

### The Siegenthaler tradeoff

Boolean-function design contains unavoidable tradeoffs.

For an $n$-variable Boolean function with algebraic degree $d$ and correlation immunity order $t$, classical bounds constrain how large both quantities can be.

For balanced resilient functions, a standard Siegenthaler-type bound is:

$$
d+t\le n-1
$$

for the nontrivial cases.

For Geffe:

$$
n=3,
$$

$$
d=2.
$$

So a balanced degree-2 function cannot simultaneously have:

$$
t\ge1
$$

under that bound.

That is consistent with the explicit correlation we already found.

This does not mean "high degree is bad" or "correlation immunity is bad."

It means Boolean combining-function design is a multi-objective cryptographic problem.

### Correlation immunity is not the end of the story

Even a combiner designed to suppress low-order correlations may face other attacks:

- algebraic attacks;
- fast correlation attacks using parity checks;
- divide-and-conquer attacks;
- attacks exploiting low linear complexity;
- distinguishing attacks;
- side-channel or implementation attacks.

Historical LFSR-based stream ciphers therefore became increasingly sophisticated.

Modern designs such as ChaCha20 take a very different architectural route instead of relying on a few small LFSRs behind a Boolean combiner.

---

## Executable Toy Attack

The companion experiment is intentionally small and fully reproducible.

It uses three maximal-period toy LFSRs under the recurrence convention from the previous article.

### Toy registers

Selector register:

$$
L_x=5
$$

with recurrence:

$$
x_{i+5}
=
x_i\oplus x_{i+2}.
$$

Data register $y$:

$$
L_y=7
$$

with:

$$
y_{i+7}
=
y_i\oplus y_{i+1}.
$$

Data register $z$:

$$
L_z=6
$$

with:

$$
z_{i+6}
=
z_i\oplus z_{i+1}.
$$

Under the chosen convention, these toy recurrences have periods:

$$
31,\qquad127,\qquad63.
$$

The periods are pairwise coprime, so the joint state period is:

$$
31\cdot127\cdot63
=
248031.
$$

For the selected seeds, the generated Geffe output also has that full toy period.

### Generator code

```python
def lfsr_sequence(
    length,
    coeffs,
    state,
    count,
):
    bits = [
        (
            state
            >> (length - 1 - i)
        ) & 1
        for i in range(length)
    ]

    output = []

    for _ in range(count):
        output.append(bits[0])

        feedback = 0

        for bit, coeff in zip(
            bits,
            coeffs,
        ):
            if coeff:
                feedback ^= bit

        bits = bits[1:] + [feedback]

    return output


def geffe(x, y, z):
    return (
        (x & y)
        ^ ((1 ^ x) & z)
    )
```

### Deterministic states

Use:

```python
x_state = 21
y_state = 83
z_state = 43
```

and generate:

```python
N = 4096
```

keystream bits.

The observed empirical agreement rates are approximately:

```text
F vs X : 0.4976
F vs Y : 0.7563
F vs Z : 0.7375
```

That is exactly the pattern predicted by the theory:

$$
\Pr[F=X]=\frac12,
$$

$$
\Pr[F=Y]=\Pr[F=Z]=\frac34.
$$

Finite sequences fluctuate around the theoretical probabilities.

### Rank candidate $y$-states

For every nonzero 7-bit state:

$$
s\in\{1,\ldots,127\},
$$

generate its candidate sequence and compute:

$$
A(s)
=
\#\{i:Y_i^{(s)}=F_i\}.
$$

The correct state:

```text
83
```

obtains:

```text
3098 / 4096
```

agreements:

$$
0.75635.
$$

The next-best wrong candidate is near:

$$
0.509.
$$

So the correct state ranks first by a large margin.

### Rank candidate $z$-states

Repeat over the 63 nonzero 6-bit states.

The correct state:

```text
43
```

obtains:

```text
3021 / 4096
```

agreements:

$$
0.73755.
$$

Again it ranks first.

### Recover $x$

Once $y$ and $z$ are known, enumerate the 31 nonzero selector states.

For each candidate $x$, regenerate:

$$
F_i^{(x)}
=
x_iy_i
\oplus
(1\oplus x_i)z_i.
$$

The correct state:

```text
21
```

matches:

```text
4096 / 4096
```

observed bits.

So the full toy state is recovered.

### Attack code

```python
def agreement(a, b):
    return sum(
        x == y
        for x, y in zip(a, b)
    )


def rank_states(
    length,
    coeffs,
    observed,
):
    ranked = []

    for state in range(
        1,
        1 << length,
    ):
        candidate = lfsr_sequence(
            length,
            coeffs,
            state,
            len(observed),
        )

        ranked.append(
            (
                agreement(
                    candidate,
                    observed,
                ),
                state,
            )
        )

    ranked.sort(reverse=True)

    return ranked
```

Then:

```python
rank_y = rank_states(
    7,
    Y_COEFFS,
    observed,
)

rank_z = rank_states(
    6,
    Z_COEFFS,
    observed,
)

recovered_y = rank_y[0][1]
recovered_z = rank_z[0][1]
```

The selector can then be tested exhaustively against the recombined output.

### Naive versus correlation search in the toy setup

Naive joint state count:

$$
31\cdot127\cdot63
=
248031.
$$

Simple divide-and-conquer candidate count:

$$
127+63+31
=
221.
$$

The actual work also includes generating and comparing $N$ bits for each candidate, but the collapse in state-combination search is already obvious.

The attack is deliberately tiny.

Its purpose is not to target a deployed cipher.

It demonstrates exactly how a statistical correlation turns a seemingly nonlinear combined state space into separate smaller searches.

---

## Conclusion

The Geffe generator is a perfect next step after the raw LFSR.

A single LFSR fails because its output is linear.

The Geffe generator tries to fix that by using the nonlinear Boolean function:

$$
F(x,y,z)
=
xy
\oplus
(1\oplus x)z.
$$

Its algebraic degree is:

$$
2.
$$

Its output is balanced.

Its component registers can all have maximal periods.

Yet:

$$
\boxed{
\Pr[F=Y]
=
\Pr[F=Z]
=
\frac34.
}
$$

The output leaks a large statistical bias toward two internal sequences.

That lets an attacker replace one joint search of approximate size:

$$
2^{L_x+L_y+L_z}
$$

with independent searches whose dominant work is closer to:

$$
2^{L_x}
+
2^{L_y}
+
2^{L_z},
$$

times the observed-keystream length and scoring cost.

The key cryptanalytic idea is therefore:

$$
\boxed{
\text{statistical dependence}
\Rightarrow
\text{divide-and-conquer state recovery}.
}
$$

This article also corrects another recurring misconception.

The combined period is governed first by the component periods:

$$
\operatorname{lcm}
(
T_x,T_y,T_z
),
$$

not automatically by their product.

The product appears when those periods are pairwise coprime, and even then the output period should be checked because it can be a divisor of the joint-state period.

Most importantly, Geffe demonstrates that:

$$
\boxed{
\text{nonlinearity alone is not a security criterion}.
}
$$

A useful combining function must be judged simultaneously by properties such as:

- balancedness;
- nonlinearity;
- correlation immunity;
- algebraic degree;
- resiliency;
- algebraic immunity.

For Geffe, the failure is visible in both elementary probability and the Walsh spectrum.

The generator therefore gives us the third major lesson of the series:

```text
LCG
    -> affine structure leaks recurrence

LFSR
    -> linear structure leaks recurrence

Geffe
    -> nonlinear output still leaks correlation
```

The next historical case moves beyond small LFSR combiners.

**RC4** uses a large byte permutation and highly nonlinear-looking state updates, yet its keystream contains measurable structural biases.

That will show that even when obvious linearity is gone, pseudorandomness can still fail in subtler statistical ways.


---

## References

1. P. R. Geffe, **How to Protect Data with Ciphers That Are Really Hard to Break**, *Electronics*, Vol. 46, No. 1, pp. 99–101, January 1973.

2. Thomas Siegenthaler, **Correlation-Immunity of Nonlinear Combining Functions for Cryptographic Applications**, *IEEE Transactions on Information Theory*, Vol. 30, No. 5, pp. 776–780, 1984.  
   DOI: 10.1109/TIT.1984.1056949

3. Willi Meier and Othmar Staffelbach, **Fast Correlation Attacks on Certain Stream Ciphers**, *Journal of Cryptology*, Vol. 1, No. 3, pp. 159–176, 1989.  
   DOI: 10.1007/BF02252874

4. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, Chapter 6, material on LFSR-based stream ciphers and correlation attacks.

5. Thomas W. Cusick and Pantelimon Stănică, **Cryptographic Boolean Functions and Applications**, for Walsh spectra, correlation immunity, resiliency, and Boolean-function design criteria.
