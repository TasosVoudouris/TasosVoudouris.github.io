---
title: "Linear Feedback Shift Registers: Finite-Field Recurrences, Periods, and State Recovery"
description: "Model LFSRs over GF(2), distinguish primitive-polynomial maximal periods from generic periods, explain linear complexity, and recover a recurrence from observed bits."
pubDate: "2025-04-05"
updatedDate: "2026-09-12"
topics:
  - "Randomness & Entropy"
  - "Mathematical Foundations"
  - "Cryptanalysis"
  - "Symmetric Cryptography"
tags:
  - "lfsr"
  - "gf2"
  - "linear-complexity"
  - "berlekamp-massey"
  - "stream-cipher"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 3
sourcePath: "experiments/randomness-stream-ciphers"
status: "Reviewed"
draft: false
---
A Linear Feedback Shift Register is a finite-state generator whose update rule is linear over $\mathbb F_2$. This makes it elegant, fast, and mathematically analyzable—and, by itself, unsuitable as a cryptographic keystream generator.

## Recurrence model

For an order-$m$ binary LFSR, let the connection coefficients be

$$
p_0,p_1,\ldots,p_{m-1}\in\mathbb F_2.
$$

The generated sequence satisfies

$$
\boxed{s_{m+i}=\sum_{j=0}^{m-1}p_j s_{i+j}\pmod 2}.
$$

Because addition in $\mathbb F_2$ is XOR, the feedback circuit is literally a collection of selected taps XORed together.

A common polynomial representation is

$$
P(X)=X^m+p_{m-1}X^{m-1}+\cdots+p_1X+p_0.
$$

Conventions differ about tap order and whether the register shifts left or right, so implementation diagrams must always be read together with the recurrence.

## The all-zero state

The all-zero state is **absorbing**:

$$
(0,\ldots,0)\mapsto(0,\ldots,0).
$$

It is therefore excluded when studying maximal-length LFSRs. The stronger old statement that an LFSR "cannot output zero" was incorrect; zero bits are perfectly normal. What is forbidden for a maximal-length sequence is the **entire zero state**.

## Period

An $m$-bit state machine has at most $2^m$ states, and a nonzero LFSR has at most

$$
2^m-1
$$

nonzero states in a cycle.

But an arbitrary degree-$m$ connection polynomial does **not** automatically achieve that period. The maximal period $2^m-1$ occurs when the connection polynomial is primitive over $\mathbb F_2$ and the initial state is nonzero.

That correction matters: "an $m$-stage LFSR has period $2^m-1$" is false without the primitive-polynomial condition.

## Recovering the recurrence from bits

If the order $m$ is known and enough consecutive output bits are observed, the unknown coefficients satisfy a linear system over $\mathbb F_2$.

For example,

$$
\begin{bmatrix}
s_0&s_1&\cdots&s_{m-1}\\
s_1&s_2&\cdots&s_m\\
\vdots&\vdots&&\vdots\\
s_{m-1}&s_m&\cdots&s_{2m-2}
\end{bmatrix}
\begin{bmatrix}p_0\\p_1\\\vdots\\p_{m-1}\end{bmatrix}
=
\begin{bmatrix}s_m\\s_{m+1}\\\vdots\\s_{2m-1}\end{bmatrix}.
$$

If the matrix has sufficient rank, Gaussian elimination over $\mathbb F_2$ recovers the tap vector.

When the shortest recurrence length is not known, the **Berlekamp–Massey algorithm** recovers the minimal linear recurrence of a finite sequence and therefore its linear complexity.

## Linear complexity

The linear complexity $L(s)$ of a sequence is the length of the shortest LFSR that can generate it. A long period does not automatically imply high cryptographic security: if the observed sequence has low linear complexity, a compact linear recurrence exists and can be reconstructed.

## Combining LFSRs

Historical stream-cipher designs often fed several LFSRs into a Boolean combining function

$$
z_i=f(x_i^{(1)},\ldots,x_i^{(r)}).
$$

This introduces nonlinearity, but **nonlinearity alone is not enough**. The older note claimed a very broad formula obtained by replacing XORs with addition and products with multiplication in the Boolean function. Such linear-complexity formulas require specific assumptions on the component sequences and combining function; they are not a universal rule.

The next chapter studies the classic Geffe generator, where a nonlinear Boolean combiner still leaves strong correlations with two component LFSRs.

## Executable experiment

The companion code contains a small LFSR class and the Geffe experiment used in the next chapter:

```bash
python experiments/randomness-stream-ciphers/test_lfsr_geffe.py
```

The point is not to build a real cipher. It is to expose the exact linear structure cryptanalysis sees.
---
title: "Linear Feedback Shift Registers: Finite-Field Recurrences, Periods, and State Recovery"
description: "Model LFSRs over GF(2), distinguish maximal-period primitive-polynomial behavior from generic periods, derive linear-complexity recovery, implement Berlekamp–Massey, and show why linear structure makes raw LFSRs unsuitable as cryptographic keystream generators."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Randomness & Entropy"
  - "Mathematical Foundations"
  - "Cryptanalysis"
  - "Symmetric Cryptography"
tags:
  - "lfsr"
  - "gf2"
  - "linear-complexity"
  - "berlekamp-massey"
  - "stream-cipher"
  - "primitive-polynomial"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 3
sourcePath: "experiments/randomness-stream-ciphers"
status: "Reviewed"
draft: false
---

## Table of Contents

- [LFSRs as Linear Dynamical Systems over GF(2)](#lfsrs-as-linear-dynamical-systems-over-gf2)
- [Connection Polynomials, State Conventions, and the Zero State](#connection-polynomials-state-conventions-and-the-zero-state)
- [Periods, Primitive Polynomials, and m-Sequences](#periods-primitive-polynomials-and-m-sequences)
- [Recovering the Recurrence from Observed Bits](#recovering-the-recurrence-from-observed-bits)
- [Linear Complexity and Berlekamp–Massey](#linear-complexity-and-berlekampmassey)
- [Why Raw LFSRs Fail as Cryptographic Keystream Generators](#why-raw-lfsrs-fail-as-cryptographic-keystream-generators)
- [Combining LFSRs and the Limits of “Just Add Nonlinearity”](#combining-lfsrs-and-the-limits-of-just-add-nonlinearity)
- [Executable Experiments](#executable-experiments)
- [Conclusion](#conclusion)
- [References](#references)

---

## LFSRs as Linear Dynamical Systems over GF(2)

A **Linear Feedback Shift Register (LFSR)** is a finite-state generator whose update rule is linear over the binary field

$$
\mathbb F_2=\{0,1\}.
$$

Its arithmetic is:

$$
1+1=0,
$$

so addition is exactly XOR.

That makes the implementation cheap:

- store $m$ state bits;
- XOR selected taps;
- shift the register;
- insert the feedback bit.

The same simplicity also makes the generator mathematically transparent.

An LFSR can have:

- a very long period;
- excellent balance properties;
- elegant finite-field structure;

and still be unsuitable as a cryptographic keystream generator by itself because its outputs satisfy a low-degree linear recurrence.

### Recurrence model

For an order-$m$ binary LFSR, let

$$
p_0,p_1,\ldots,p_{m-1}\in\mathbb F_2
$$

be the recurrence coefficients.

A sequence

$$
s_0,s_1,s_2,\ldots
$$

satisfies

$$
\boxed{
s_{i+m}
=
\sum_{j=0}^{m-1}
p_j s_{i+j}
\pmod 2.
}
$$

Because arithmetic is in $\mathbb F_2$, this is equivalent to XORing the selected previous bits.

If, for example,

$$
m=4
$$

and the recurrence is

$$
s_{i+4}
=
s_i
\oplus
s_{i+1},
$$

then:

$$
p_0=1,\quad p_1=1,\quad p_2=p_3=0.
$$

### The state as a vector

Define the state at time $i$ as:

$$
X_i
=
\begin{bmatrix}
s_i\\
s_{i+1}\\
\vdots\\
s_{i+m-1}
\end{bmatrix}
\in\mathbb F_2^m.
$$

Then the entire update can be written as:

$$
X_{i+1}=AX_i,
$$

where $A$ is a companion-style binary matrix.

For the recurrence

$$
s_{i+m}
=
p_0s_i+p_1s_{i+1}+\cdots+p_{m-1}s_{i+m-1},
$$

one convenient state-transition matrix is

$$
A=
\begin{bmatrix}
0&1&0&\cdots&0\\
0&0&1&\cdots&0\\
\vdots&\vdots&\vdots&\ddots&\vdots\\
0&0&0&\cdots&1\\
p_0&p_1&p_2&\cdots&p_{m-1}
\end{bmatrix}.
$$

This matrix viewpoint is important because it makes the linearity explicit:

$$
A(X+Y)=AX+AY.
$$

The generator is not merely "implemented with XOR."

Its entire state evolution is a linear dynamical system over $\mathbb F_2$.

### Why this matters cryptographically

If an attacker observes enough output bits and those bits are directly related to the state, then every observation contributes a linear equation.

Cryptanalysis becomes:

$$
\text{recover unknown state/recurrence}
$$

by solving a linear system.

No brute-force search over all $2^m$ states is required in the basic raw-output model.

That is the central weakness.

---

## Connection Polynomials, State Conventions, and the Zero State

A recurrence is often represented by a **connection polynomial**.

For

$$
s_{i+m}
=
p_0s_i+p_1s_{i+1}+\cdots+p_{m-1}s_{i+m-1},
$$

a common convention is

$$
P(X)
=
X^m
+
p_{m-1}X^{m-1}
+\cdots+
p_1X
+p_0.
$$

The leading coefficient is $1$, so the polynomial is monic.

### Conventions differ

LFSR literature contains several equally valid conventions.

Authors may differ in:

- whether the output bit is taken from the left or right end;
- whether the register shifts left or right;
- whether taps are indexed from the input or output side;
- whether polynomial coefficients are written in reverse register order;
- whether the implementation is Fibonacci or Galois form.

Therefore a statement such as:

```text
taps = [4, 1]
```

is not self-describing.

A correct implementation must be read together with:

- the recurrence;
- the shift direction;
- the output convention;
- the polynomial convention.

This is especially important when comparing test vectors.

### Fibonacci and Galois forms

Two common LFSR organizations are:

**Fibonacci LFSR**

- compute one XOR feedback bit from selected taps;
- shift the whole register;
- inject feedback at one end.

**Galois LFSR**

- shift the register;
- conditionally distribute the outgoing bit into selected positions.

Under matching polynomial conventions, these can generate related sequences and often implement the same underlying recurrence more efficiently.

But their tap masks are not interchangeable without conversion.

### The all-zero state

Because the recurrence is linear,

$$
0+0+\cdots+0=0.
$$

Therefore:

$$
(0,\ldots,0)
\longmapsto
(0,\ldots,0).
$$

The all-zero state is an absorbing fixed point.

This is why maximal-length LFSRs exclude it.

The correct statement is:

> a maximal-length LFSR cycles through all $2^m-1$ nonzero states.

It is **not** correct to say:

> an LFSR cannot output zero.

Individual output bits are frequently zero.

What is special is the complete state:

$$
X_i=0^m.
$$

Once reached, it never leaves.

### Why zero cannot appear inside an m-sequence state cycle

Suppose a maximal-length nonzero state cycle ever reached:

$$
0^m.
$$

Then every subsequent state would remain zero.

So the sequence could never return to the previous nonzero state.

That contradicts the existence of a nonzero cycle.

Hence:

$$
0^m
$$

is outside the maximal nonzero orbit.

---

## Periods, Primitive Polynomials, and m-Sequences

An $m$-bit register has:

$$
2^m
$$

possible states.

Because the zero state is absorbing, a nonzero cycle can contain at most:

$$
2^m-1
$$

states.

But an arbitrary degree-$m$ LFSR does **not** automatically achieve that maximum.

### Maximum possible period

The maximum nonzero period is:

$$
\boxed{
2^m-1.
}
$$

An LFSR achieving this period is called a **maximal-length LFSR**, and its output sequence is commonly called an **m-sequence**.

The key algebraic condition is that the connection polynomial be **primitive over $\mathbb F_2$**.

### Irreducible is not enough

A degree-$m$ polynomial may be irreducible over $\mathbb F_2$ without being primitive.

Primitive is stronger.

If $\alpha$ is a root of an irreducible polynomial of degree $m$, then:

$$
\alpha\in\mathbb F_{2^m}.
$$

The nonzero elements of that field form a multiplicative group of order:

$$
2^m-1.
$$

The polynomial is primitive if its root has multiplicative order exactly:

$$
2^m-1.
$$

Equivalently, $\alpha$ generates:

$$
\mathbb F_{2^m}^{\times}.
$$

That full multiplicative order is what produces the maximal state period.

### Primitive-polynomial test

Let

$$
N=2^m-1.
$$

For an irreducible degree-$m$ polynomial $P(X)$, primitiveness can be tested by verifying that for every prime divisor $q$ of $N$,

$$
X^{N/q}\not\equiv1\pmod{P(X)},
$$

while:

$$
X^N\equiv1\pmod{P(X)}.
$$

The exact computational method is polynomial arithmetic over $\mathbb F_2$.

This is a finite-field order test, not a visual property of the generated bits.

### Example: $x^4+x+1$

The polynomial

$$
P(X)=X^4+X+1
$$

is primitive over $\mathbb F_2$.

A nonzero state under a matching LFSR convention therefore has period:

$$
2^4-1=15.
$$

So all 15 nonzero states occur before the register repeats.

### Example: a nonprimitive polynomial

A degree-$m$ polynomial that is reducible or irreducible-but-nonprimitive may produce a shorter cycle.

Thus the statement:

$$
\text{"m-stage LFSR has period }2^m-1"
$$

is false without the primitive-polynomial and nonzero-seed conditions.

### m-sequence balance property

Over one full period of an m-sequence:

- the number of $1$ bits is:

  $$
  2^{m-1};
  $$

- the number of $0$ bits is:

  $$
  2^{m-1}-1.
  $$

So the sequence is almost perfectly balanced.

That sounds attractive statistically.

It is still completely generated by a length-$m$ linear recurrence.

This is an ideal example of the distinction:

$$
\boxed{
\text{excellent statistics}
\neq
\text{cryptographic unpredictability}.
}
$$

### Run and autocorrelation properties

m-sequences also have strong classical pseudorandom-looking properties, including regular run distributions and a two-valued periodic autocorrelation.

These properties made LFSRs useful in:

- spread-spectrum systems;
- coding theory;
- test-pattern generation;
- synchronization;
- older communication systems.

But cryptographic security asks a stronger question:

> Can the recurrence or state be reconstructed efficiently from output?

For a raw LFSR, the answer is yes.

---

## Recovering the Recurrence from Observed Bits

Suppose the LFSR order $m$ is known.

The recurrence is:

$$
s_{i+m}
=
\sum_{j=0}^{m-1}
p_js_{i+j}
\pmod2.
$$

The unknowns are:

$$
p_0,p_1,\ldots,p_{m-1}.
$$

Every new observed output bit provides a linear equation over $\mathbb F_2$.

### Matrix formulation

Using $2m$ consecutive bits:

$$
s_0,s_1,\ldots,s_{2m-1},
$$

we can write:

$$
\begin{bmatrix}
s_0&s_1&\cdots&s_{m-1}\\
s_1&s_2&\cdots&s_m\\
\vdots&\vdots&&\vdots\\
s_{m-1}&s_m&\cdots&s_{2m-2}
\end{bmatrix}
\begin{bmatrix}
p_0\\
p_1\\
\vdots\\
p_{m-1}
\end{bmatrix}
=
\begin{bmatrix}
s_m\\
s_{m+1}\\
\vdots\\
s_{2m-1}
\end{bmatrix}
$$

over:

$$
\mathbb F_2.
$$

Call this:

$$
Ap=b.
$$

If:

$$
\operatorname{rank}(A)=m,
$$

then the recurrence coefficients are uniquely determined.

### Gaussian elimination over GF(2)

Ordinary Gaussian elimination adapts perfectly to $\mathbb F_2$.

The arithmetic rules are:

```text
1 + 1 = 0
1 - 1 = 0
1 * 1 = 1
```

so row addition is XOR.

A row-reduction implementation can represent each binary row as an integer bitmask and use XOR for elimination.

This is often dramatically faster than generic matrix arithmetic for binary systems.

### Rank deficiency

The $2m$-bit observation window does **not** automatically guarantee a unique recurrence of order exactly $m$.

The matrix may be rank deficient.

That can happen when:

- the actual linear complexity is below $m$;
- the sequence fragment is degenerate;
- the assumed order is larger than necessary.

So the correct statement is:

> $2m$ consecutive bits can provide $m$ linear equations for the $m$ coefficients, and recovery succeeds uniquely when the resulting system has full rank.

This rank caveat is important.

### State recovery once recurrence is known

If the recurrence has order $m$, then any $m$ consecutive bits form enough state to generate the future sequence.

For example, after recovering $p$, store:

$$
(s_i,\ldots,s_{i+m-1}).
$$

Then compute:

$$
s_{i+m}
$$

from the recurrence, shift, and repeat.

Thus recurrence recovery implies next-bit prediction.

---

## Linear Complexity and Berlekamp–Massey

Often the attacker does **not** know the LFSR order.

Then the natural question becomes:

> What is the shortest linear recurrence consistent with the observed sequence?

The answer is captured by **linear complexity**.

### Definition

The linear complexity $L(s)$ of a finite or periodic binary sequence is the length of the shortest LFSR capable of generating it.

If:

$$
L(s)=L,
$$

then there exists a degree-$L$ connection polynomial

$$
C(X)
=
1+c_1X+\cdots+c_LX^L
$$

such that the sequence obeys the corresponding recurrence.

No shorter LFSR can generate the same observed sequence.

### Why linear complexity matters

A long period does not imply high linear complexity.

A sequence might repeat only after an enormous number of steps but still obey a relatively short linear recurrence.

If the linear complexity is $L$, then roughly $2L$ consecutive sequence bits are sufficient for Berlekamp–Massey to recover the minimal recurrence in the standard exact setting.

That gives the core cryptanalytic lesson:

$$
\boxed{
\text{low linear complexity}
\Rightarrow
\text{efficient recurrence recovery}.
}
$$

### Berlekamp–Massey intuition

Berlekamp–Massey processes the sequence one bit at a time.

It maintains a candidate connection polynomial.

At each position, it computes a **discrepancy**:

$$
d_n
=
s_n
+
\sum_{i=1}^{L}
c_i s_{n-i}
\pmod2.
$$

If:

$$
d_n=0,
$$

the current recurrence correctly predicts that bit.

If:

$$
d_n=1,
$$

the current recurrence failed, so the algorithm updates the connection polynomial using information from a previous discrepancy.

The clever part is that it does this while maintaining a shortest recurrence consistent with all bits processed so far.

### Binary Berlekamp–Massey

A direct implementation is:

```python
def berlekamp_massey(bits):
    n = len(bits)

    C = [0] * (n + 1)
    B = [0] * (n + 1)

    C[0] = 1
    B[0] = 1

    L = 0
    m = 1

    for N in range(n):
        d = bits[N]

        for i in range(1, L + 1):
            d ^= C[i] & bits[N - i]

        if d == 0:
            m += 1
            continue

        T = C.copy()

        for j in range(
            0,
            n + 1 - m,
        ):
            C[j + m] ^= B[j]

        if 2 * L <= N:
            L = N + 1 - L
            B = T
            m = 1
        else:
            m += 1

    return L, C[:L + 1]
```

For a true order-$m$ maximal LFSR sequence, sufficiently many exact output bits should recover:

$$
L=m.
$$

### Recurrence convention

If Berlekamp–Massey returns:

$$
C(X)
=
1+c_1X+\cdots+c_LX^L,
$$

then the sequence satisfies:

$$
s_n
=
c_1s_{n-1}
\oplus
c_2s_{n-2}
\oplus\cdots\oplus
c_Ls_{n-L}
$$

under the convention used by the implementation.

Polynomial orientation matters.

Always verify recovered coefficients by regenerating held-out sequence bits.

### Why held-out prediction is the decisive test

It is easy to fit a recurrence to the same data used to derive it.

The meaningful experiment is:

1. use the first $N$ bits for recovery;
2. reconstruct the recurrence;
3. predict later unseen bits;
4. compare with the generator.

If the predictions match, the attack has crossed from model fitting into genuine next-output prediction.

---

## Why Raw LFSRs Fail as Cryptographic Keystream Generators

Suppose a raw LFSR output is used as a keystream:

$$
KS_i=s_i.
$$

The stream cipher computes:

$$
C_i=P_i\oplus s_i.
$$

If the attacker learns enough keystream bits through known plaintext:

$$
s_i=C_i\oplus P_i,
$$

then the linear recurrence can be reconstructed.

After that, future keystream bits are predictable.

### Attack chain

The full attack path is:

$$
\text{known plaintext}
$$

$$
\Downarrow
$$

$$
\text{recover keystream bits}
$$

$$
\Downarrow
$$

$$
\text{solve linear recurrence}
$$

$$
\Downarrow
$$

$$
\text{recover linear complexity/state}
$$

$$
\Downarrow
$$

$$
\text{predict future keystream}
$$

$$
\Downarrow
$$

$$
\text{recover future plaintext}.
$$

The weakness is not that an LFSR "looks repetitive."

A good maximal LFSR can look statistically excellent.

The failure is:

$$
\boxed{
\text{the keystream lies in a low-dimensional linear model}.
}
$$

### Huge period does not save it

Suppose:

$$
m=128.
$$

A primitive polynomial gives period:

$$
2^{128}-1.
$$

That is astronomically large.

Yet the state contains only:

$$
128
$$

bits and the output satisfies a length-128 linear recurrence.

Under the direct-output model, a modest amount of exact output can recover that structure.

So:

$$
\boxed{
2^{128}\text{-scale period}
\neq
128\text{-bit cryptographic security}.
}
$$

Period measures when a sequence repeats.

Cryptographic security measures what an efficient adversary can infer before repetition.

### State size is not automatically security level

An $m$-bit LFSR has $m$ state bits.

But if its output exposes enough linear information to solve for those state bits in polynomial time, then the attack cost is nowhere near:

$$
2^m.
$$

State-space size matters only when exhaustive search is the best attack.

For raw LFSRs, it is not.

---

## Combining LFSRs and the Limits of “Just Add Nonlinearity”

Historical stream-cipher designs often combined several LFSRs.

Let the component sequences be:

$$
x_i^{(1)},x_i^{(2)},\ldots,x_i^{(r)}.
$$

A Boolean combining function produces:

$$
z_i
=
f(
x_i^{(1)},
x_i^{(2)},
\ldots,
x_i^{(r)}
).
$$

If $f$ is nonlinear, then $z_i$ is no longer a simple linear combination of the register outputs.

That is an improvement over one raw LFSR.

It is not automatically secure.

### Nonlinearity is only one property

A Boolean combining function can be nonlinear but still correlate strongly with one input.

For example, suppose:

$$
\Pr[
f(X_1,\ldots,X_r)=X_1
]
=
\frac34.
$$

Then the output leaks statistical information about $X_1$.

An attacker can exploit enough output bits to identify candidate states of the first LFSR.

This is a **correlation attack**.

### Algebraic degree is not enough

A combining function may have high algebraic degree but poor correlation immunity.

Or it may be correlation immune but have poor algebraic properties for another attack model.

Relevant criteria include:

- balancedness;
- nonlinearity;
- correlation immunity;
- resiliency;
- algebraic degree;
- algebraic immunity.

There are tradeoffs among these properties.

So "use a nonlinear Boolean function" is not a design theorem.

### Linear-complexity formulas need assumptions

Older notes sometimes suggest that one can compute the combined sequence's linear complexity by mechanically replacing XOR with addition and AND with multiplication in the Boolean expression.

That is not a universal rule.

Exact linear-complexity formulas depend on:

- periods of component sequences;
- coprimality conditions;
- characteristic polynomials;
- combining-function algebra;
- independence assumptions.

The safe educational statement is:

> nonlinear combination can increase linear complexity, but the result must be analyzed under explicit assumptions.

### The Geffe generator

The next article studies a classic example:

$$
z
=
(x_1\land x_2)
\oplus
(\neg x_1\land x_3).
$$

This is a nonlinear multiplexer-like function.

Yet the output is correlated with two component sequences.

That makes the Geffe generator an ideal demonstration that:

$$
\boxed{
\text{nonlinear}
\neq
\text{correlation resistant}.
}
$$

---

## Executable Experiments

The companion lab can verify four different claims:

1. a primitive degree-4 recurrence reaches period 15;
2. the zero state is absorbing;
3. Gaussian elimination recovers a known-order recurrence;
4. Berlekamp–Massey recovers the minimal recurrence and predicts held-out bits.

### Lab A: a simple Fibonacci LFSR

Use the recurrence:

$$
s_{i+4}
=
s_i\oplus s_{i+1},
$$

corresponding to:

$$
P(X)=X^4+X+1.
$$

A direct sequence generator is:

```python
def generate_lfsr(
    initial_bits,
    coeffs,
    count,
):
    m = len(coeffs)

    if len(initial_bits) != m:
        raise ValueError(
            "initial state length mismatch"
        )

    seq = list(initial_bits)

    while len(seq) < count:
        i = len(seq) - m

        new_bit = 0

        for j, c in enumerate(coeffs):
            if c:
                new_bit ^= seq[i + j]

        seq.append(new_bit)

    return seq[:count]
```

For:

```python
coeffs = [1, 1, 0, 0]
seed   = [1, 0, 0, 0]
```

the recurrence is:

$$
s_{i+4}=s_i\oplus s_{i+1}.
$$

### Lab B: detect the state period

```python
def state_period(
    initial_state,
    coeffs,
    limit=10000,
):
    state = tuple(initial_state)
    initial = state

    for period in range(
        1,
        limit + 1,
    ):
        feedback = 0

        for bit, c in zip(
            state,
            coeffs,
        ):
            if c:
                feedback ^= bit

        state = (
            state[1:]
            + (feedback,)
        )

        if state == initial:
            return period

    raise RuntimeError(
        "period limit exceeded"
    )
```

For the primitive degree-4 recurrence and nonzero seed:

$$
\text{period}=15.
$$

For:

```python
[0, 0, 0, 0]
```

the state immediately maps to itself.

### Lab C: recover coefficients with Gaussian elimination

Build the system:

$$
Ap=b
$$

from $2m$ observed bits.

One compact GF(2) solver is:

```python
def solve_gf2(A, b):
    A = [
        row[:] + [rhs]
        for row, rhs in zip(A, b)
    ]

    rows = len(A)
    cols = len(A[0]) - 1

    pivot_row = 0
    pivots = []

    for col in range(cols):
        pivot = None

        for r in range(
            pivot_row,
            rows,
        ):
            if A[r][col]:
                pivot = r
                break

        if pivot is None:
            continue

        A[pivot_row], A[pivot] = (
            A[pivot],
            A[pivot_row],
        )

        for r in range(rows):
            if (
                r != pivot_row
                and A[r][col]
            ):
                A[r] = [
                    x ^ y
                    for x, y in zip(
                        A[r],
                        A[pivot_row],
                    )
                ]

        pivots.append(col)
        pivot_row += 1

    if len(pivots) < cols:
        raise ValueError(
            "system does not have a unique solution"
        )

    solution = [0] * cols

    for r, col in enumerate(pivots):
        solution[col] = A[r][-1]

    return solution
```

The recovered coefficients should equal:

```text
[1, 1, 0, 0]
```

for the selected convention.

### Lab D: Berlekamp–Massey

Generate more sequence bits and run:

```python
L, connection = (
    berlekamp_massey(bits)
)
```

For the degree-4 m-sequence we expect:

$$
L=4.
$$

Then use the recovered recurrence to predict bits that were not passed to Berlekamp–Massey.

The attack is successful only if those held-out bits match.

### Why deterministic tests matter

The point of the lab is not to show an animation of a shift register.

It is to test the precise mathematical claims:

```text
primitive recurrence -> maximal period
zero state           -> absorbing
known order          -> linear solve
unknown order        -> Berlekamp–Massey
recovered recurrence -> unseen-bit prediction
```

That is the bridge from finite-field theory to cryptanalysis.

---

## Conclusion

An LFSR is one of the cleanest examples of elegant mathematics and poor standalone cryptographic security.

Its sequence satisfies:

$$
\boxed{
s_{i+m}
=
\sum_{j=0}^{m-1}
p_js_{i+j}
\pmod2.
}
$$

Its state transition is linear:

$$
X_{i+1}=AX_i.
$$

A primitive degree-$m$ connection polynomial and a nonzero seed can produce the maximal period:

$$
\boxed{
2^m-1.
}
$$

Such m-sequences have excellent classical statistical properties.

But those properties do not hide the recurrence.

When the order is known, enough observed bits produce a linear system over:

$$
\mathbb F_2.
$$

When the shortest order is unknown, Berlekamp–Massey recovers the minimal recurrence and its linear complexity.

This creates the key distinction:

$$
\boxed{
\text{long period}
\neq
\text{high linear complexity}
\neq
\text{cryptographic security}.
}
$$

For a raw LFSR, linear complexity is small by construction.

Once the recurrence and one state window are known, the future sequence is deterministic.

That makes raw LFSRs unsuitable as standalone keystream generators even when:

- the state is large;
- the period is maximal;
- zeros and ones are balanced;
- autocorrelation looks excellent.

The attack does not require spotting a visible pattern.

It uses the exact algebra the generator was designed around.

This is the second major failure mode in the series:

```text
LCG:
    affine recurrence modulo m

LFSR:
    linear recurrence over GF(2)
```

Both teach the same principle:

$$
\boxed{
\text{if the output exposes enough solvable equations,
the generator is predictable}.
}
$$

The next article makes the problem subtler.

Instead of exposing one raw linear sequence, the **Geffe generator** combines three LFSRs with a nonlinear Boolean function.

The output is no longer linearly generated in the obvious sense.

Yet statistical correlation survives.

That leads to a new cryptanalytic idea:

$$
\boxed{
\text{correlation attacks}.
}
$$


---

## References

1. Solomon W. Golomb, **Shift Register Sequences**, Holden-Day, 1967; revised editions and reprints.

2. James L. Massey, **Shift-Register Synthesis and BCH Decoding**, IEEE Transactions on Information Theory, 1969.

3. Elwyn R. Berlekamp, **Algebraic Coding Theory**, McGraw-Hill, 1968, for the algorithmic foundations later adapted by Massey.

4. Rudolf Lidl and Harald Niederreiter, **Finite Fields**, for irreducible and primitive polynomials over finite fields.

5. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone, **Handbook of Applied Cryptography**, sections on stream ciphers, LFSRs, and linear complexity.
