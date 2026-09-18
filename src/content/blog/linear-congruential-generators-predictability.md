---
title: "Linear Congruential Generators: Periods, Parameter Recovery, and Why Statistical Quality Is Not Security"
description: "Derive the LCG recurrence, recover parameters from observed states with and without modular inverses, reconstruct an unknown modulus from algebraic fingerprints, study full-period conditions, and show why statistical quality and long period do not imply cryptographic unpredictability."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Randomness & Entropy"
  - "Cryptanalysis"
  - "Number Theory"
  - "Cryptographic Engineering"
tags:
  - "lcg"
  - "prng"
  - "state-recovery"
  - "modular-arithmetic"
  - "predictability"
  - "hull-dobell"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 2
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---

## Table of Contents

- [The LCG Recurrence and What It Really Guarantees](#the-lcg-recurrence-and-what-it-really-guarantees)
- [Recovering Parameters When the Modulus Is Known](#recovering-parameters-when-the-modulus-is-known)
- [When the Modular Inverse Does Not Exist](#when-the-modular-inverse-does-not-exist)
- [Recovering an Unknown Modulus](#recovering-an-unknown-modulus)
- [\[
t_it_${i+2}](#t_it_i2)
- [t_it_${i+2}](#t_it_i2-1)
- [Periods, Hull–Dobell, and Why Period Is Not Security](#periods-hulldobell-and-why-period-is-not-security)
- [From State Recovery to Keystream Prediction](#from-state-recovery-to-keystream-prediction)
- [Executable Experiments](#executable-experiments)
- [Conclusion](#conclusion)
- [\[
\boxed${
t_it_${i+2}](#boxedt_it_i2)
- [References](#references)

---

## The LCG Recurrence and What It Really Guarantees

A linear congruential generator is one of the clearest examples of the difference between **pseudorandom-looking output** and **cryptographic unpredictability**.

Its state evolves according to

\[
S_{i+1}
=
aS_i+c
\pmod m,
\]

where:

- \(m\) is the modulus;
- \(a\) is the multiplier;
- \(c\) is the increment;
- \(S_0\) is the initial state or seed.

The recurrence is extremely cheap to evaluate.

That simplicity made LCGs historically attractive for simulation and general-purpose pseudorandom number generation.

But the same algebraic simplicity makes them unsuitable as cryptographic generators when their raw or sufficiently informative state is exposed.

### Determinism is not the problem

Every deterministic PRNG has a recurrence of some kind.

The problem with an LCG is not merely that it is deterministic.

The problem is that the recurrence is **affine and efficiently solvable**.

Once an attacker learns enough information about the state sequence, the unknown parameters can often be recovered by elementary modular arithmetic.

The distinction is:

\[
\boxed{
\text{deterministic}
\neq
\text{cryptographically weak}
}
\]

but:

\[
\boxed{
\text{easily solvable state relation}
\Rightarrow
\text{predictability}
}
\]

### One-dimensional affine dynamics

The map

\[
T(x)=ax+c\pmod m
\]

is an affine transformation on the residue ring

\[
\mathbb Z_m.
\]

Repeated application gives

\[
S_1=T(S_0),
\]

\[
S_2=T(T(S_0)),
\]

and so on.

If \(a-1\) is invertible modulo \(m\), one can even write the closed form

\[
S_n
\equiv
a^nS_0
+
c
\frac{a^n-1}{a-1}
\pmod m.
\]

But this geometric-series expression is not universally valid in that form because division by \(a-1\) requires invertibility modulo \(m\).

A safer recurrence-based statement is enough for cryptanalysis:

\[
S_{i+1}-S_i
\equiv
a(S_i-S_{i-1})
\pmod m.
\]

The first differences therefore follow a multiplicative congruence.

That simple relation is the beginning of parameter recovery.

### Raw state versus transformed output

A crucial modeling distinction is often omitted in toy discussions.

The attack

\[
S_0,S_1,S_2
\longrightarrow
a,c
\]

assumes the observer sees **consecutive internal states**, or output values equal to those states.

A practical generator might instead expose

\[
Y_i=g(S_i)
\]

for some transformation \(g\), perhaps:

- truncation;
- bit extraction;
- permutation;
- tempering;
- output mixing.

Then the same three-value formula does not necessarily apply directly.

That does not make the construction secure.

It means the cryptanalysis must model the output function as well as the state transition.

Throughout this article, unless stated otherwise, the observed outputs are the full raw LCG states.

---

## Recovering Parameters When the Modulus Is Known

Assume the attacker knows:

\[
m
\]

and observes three consecutive states:

\[
S_0,S_1,S_2.
\]

The recurrence gives:

\[
S_1
\equiv
aS_0+c
\pmod m,
\]

\[
S_2
\equiv
aS_1+c
\pmod m.
\]

Subtract the equations:

\[
S_2-S_1
\equiv
a(S_1-S_0)
\pmod m.
\]

Define:

\[
\Delta_0=S_1-S_0,
\]

\[
\Delta_1=S_2-S_1.
\]

Then:

\[
\Delta_1
\equiv
a\Delta_0
\pmod m.
\]

### The invertible case

If:

\[
\gcd(\Delta_0,m)=1,
\]

then \(\Delta_0\) has a unique multiplicative inverse modulo \(m\).

Multiply both sides by:

\[
\Delta_0^{-1}.
\]

We obtain:

\[
\boxed{
a
\equiv
\Delta_1
\Delta_0^{-1}
\pmod m
}
\]

or explicitly:

\[
\boxed{
a
\equiv
(S_2-S_1)
(S_1-S_0)^{-1}
\pmod m.
}
\]

Once \(a\) is known, recover \(c\) from:

\[
S_1
\equiv
aS_0+c
\pmod m,
\]

so:

\[
\boxed{
c
\equiv
S_1-aS_0
\pmod m.
}
\]

This corrects a common indexing mistake in informal notes: the second recurrence must be based on \(S_1\),

\[
S_2\equiv aS_1+c\pmod m,
\]

not on some later state.

### Why only three states are enough

The unknowns are:

\[
a,\qquad c.
\]

Two transition equations supply two modular constraints:

\[
S_1-aS_0-c\equiv0\pmod m,
\]

\[
S_2-aS_1-c\equiv0\pmod m.
\]

Subtracting removes \(c\), leaving one equation for \(a\).

If the relevant coefficient is invertible, the solution is unique modulo \(m\).

So the cryptanalytic weakness is not a subtle statistical bias.

It is direct algebra.

### Example

Take:

\[
m=2^{31},
\]

\[
a=1103515245,
\]

\[
c=12345,
\]

and some unknown seed.

Suppose three consecutive full states are visible.

The attacker computes:

\[
\Delta_0=S_1-S_0,
\]

\[
\Delta_1=S_2-S_1.
\]

When \(\Delta_0\) is invertible modulo \(m\),

\[
a
=
\Delta_1\Delta_0^{-1}\bmod m.
\]

Then:

\[
c
=
S_1-aS_0\bmod m.
\]

Every future state follows deterministically.

### Parameter recovery is state recovery in practice

Once \(a,c,m\) are known and one current state \(S_i\) is known,

\[
S_{i+1}=aS_i+c\pmod m
\]

predicts the future exactly.

There is no remaining computational hardness assumption.

The attacker does not need to brute-force the original seed.

Current state plus recovered recurrence is enough.

---

## When the Modular Inverse Does Not Exist

The formula

\[
a
\equiv
\Delta_1\Delta_0^{-1}
\pmod m
\]

silently assumes:

\[
\gcd(\Delta_0,m)=1.
\]

If:

\[
g=
\gcd(\Delta_0,m)
>
1,
\]

then ordinary modular division is invalid.

But parameter recovery does not necessarily fail.

Instead, we must solve the linear congruence:

\[
\Delta_0 a
\equiv
\Delta_1
\pmod m.
\]

### Solvability condition

The congruence:

\[
Ax\equiv B\pmod m
\]

has a solution if and only if:

\[
\gcd(A,m)\mid B.
\]

So define:

\[
g=\gcd(\Delta_0,m).
\]

A multiplier \(a\) exists only if:

\[
g\mid\Delta_1.
\]

For a genuine LCG trace this consistency condition should hold, assuming the observations are correct.

### Reduce the congruence

Divide by \(g\):

\[
\frac{\Delta_0}{g}a
\equiv
\frac{\Delta_1}{g}
\pmod{\frac{m}{g}}.
\]

Now:

\[
\gcd
\left(
\frac{\Delta_0}{g},
\frac{m}{g}
\right)
=
1,
\]

so the reduced coefficient is invertible.

Let:

\[
m'=\frac{m}{g},
\]

\[
A'=\frac{\Delta_0}{g},
\]

\[
B'=\frac{\Delta_1}{g}.
\]

Then one solution is:

\[
a_0
\equiv
B'(A')^{-1}
\pmod{m'}.
\]

But this is not necessarily unique modulo \(m\).

### Multiple multiplier candidates

The original congruence has exactly \(g\) residue-class solutions modulo \(m\):

\[
\boxed{
a
=
a_0+km',
\qquad
k=0,\ldots,g-1.
}
\]

Each candidate multiplier determines a candidate increment:

\[
c
\equiv
S_1-aS_0
\pmod m.
\]

Additional observed states can be used to test which candidates reproduce the sequence.

However, extra observations do **not** guarantee immediate uniqueness. Two parameter pairs can remain observationally equivalent on the particular orbit being observed, especially when the states occupy a restricted residue class. In that case, more data may still leave several equivalent candidates, and the attacker may not need to distinguish them if every surviving candidate predicts the same future outputs on that orbit.

So the correct lesson is not:

> "if the inverse does not exist, recovery is impossible."

It is:

> "the simple one-line inverse formula becomes a modular-congruence problem with potentially multiple, sometimes observationally equivalent, candidates."

### Why powers-of-two moduli make this common

Many historical LCGs use:

\[
m=2^w.
\]

Then an integer is invertible modulo \(m\) if and only if it is odd.

So whenever:

\[
S_1-S_0
\]

is even, the simple inverse does not exist.

That makes the caveat operationally important, not merely theoretical.

### Additional observations remove ambiguity

Suppose candidate pairs are:

\[
(a_1,c_1),
\ldots,
(a_g,c_g).
\]

Given another observed state \(S_3\), test:

\[
S_3
\stackrel{?}{\equiv}
a_jS_2+c_j
\pmod m.
\]

Wrong candidates are discarded.

A few more observations usually collapse the candidate set rapidly.

This is a recurring theme in state-recovery attacks:

\[
\boxed{
\text{non-uniqueness from one equation}
+
\text{more observations}
\rightarrow
\text{unique recurrence}
}
\]

---

## Recovering an Unknown Modulus

The known-modulus attack is already devastating.

But even when \(m\) is hidden, the LCG recurrence leaves strong integer divisibility fingerprints.

Assume several consecutive full states are visible:

\[
S_0,S_1,S_2,\ldots
\]

but \(a,c,m\) are unknown.

### First differences

Define:

\[
t_i
=
S_{i+1}-S_i
\]

as ordinary integers.

From the recurrence:

\[
S_{i+1}
\equiv
aS_i+c
\pmod m,
\]

we get:

\[
S_{i+2}-S_{i+1}
\equiv
a(S_{i+1}-S_i)
\pmod m.
\]

Therefore:

\[
t_{i+1}
\equiv
at_i
\pmod m.
\]

### Eliminate the multiplier

We have:

\[
t_{i+1}\equiv at_i\pmod m,
\]

and:

\[
t_{i+2}\equiv at_{i+1}\pmod m.
\]

Multiply the first relation by \(t_{i+1}\):

\[
t_{i+1}^2
\equiv
at_it_{i+1}
\pmod m.
\]

Multiply the second by \(t_i\):

\[
t_it_{i+2}
\equiv
at_it_{i+1}
\pmod m.
\]

Subtract:

\[
t_it_{i+2}
-
t_{i+1}^2
\equiv
0
\pmod m.
\]

Define:

\[
z_i
=
t_it_{i+2}
-
t_{i+1}^2.
\]

Then:

\[
\boxed{
m\mid z_i.
}
\]

Every nonzero \(z_i\) is an integer multiple of the hidden modulus.

### Use a GCD

Compute several such values:

\[
z_0,z_1,z_2,\ldots
\]

and then:

\[
g
=
\gcd(
|z_0|,
|z_1|,
|z_2|,
\ldots
).
\]

Because every \(z_i\) is divisible by \(m\),

\[
m\mid g.
\]

In favorable traces, the GCD collapses to:

\[
g=m.
\]

In other cases it may yield:

- a multiple of \(m\);
- zero for degenerate observations;
- a value requiring factorization or validation.

So the GCD method is a candidate-modulus recovery method, not a magical theorem that every trace returns \(m\) immediately.

### Validate the candidate

Once a candidate modulus \(\hat m\) is obtained:

1. recover candidate \(a,c\);
2. check that all observed states satisfy

   \[
   S_{i+1}
   \equiv
   aS_i+c
   \pmod{\hat m};
   \]

3. reject factors or multiples that do not reproduce the complete trace;
4. if necessary, gather more outputs.

This is a good general cryptanalytic workflow:

\[
\text{derive algebraic invariant}
\rightarrow
\text{recover candidate}
\rightarrow
\text{validate globally}.
\]

### Degenerate cases

The method can fail or become ambiguous when:

- some \(z_i=0\);
- too few outputs are available;
- outputs are truncated;
- the generator output is transformed;
- observations contain errors;
- the recurrence is not actually an LCG.

Those are modeling constraints, not cryptographic salvation.

### Why hiding the modulus is not a security boundary

The important lesson is:

\[
\boxed{
\text{secret parameters}
\neq
\text{secure generator}
}
\]

if those parameters are algebraically recoverable from output.

Cryptography should remain secure even when the algorithm and public parameters are known.

Security should reside in a secret key/state protected by a hard problem or well-analyzed construction—not in hoping the attacker never identifies the recurrence.

---

## Periods, Hull–Dobell, and Why Period Is Not Security

An LCG lives in a finite state space of size:

\[
m.
\]

Therefore every sequence must eventually repeat.

The maximum possible period is:

\[
m.
\]

For a **mixed LCG** with:

\[
c\neq0,
\]

the Hull–Dobell theorem characterizes exactly when every seed lies on a full-period cycle of length \(m\).

The recurrence:

\[
S_{i+1}=aS_i+c\pmod m
\]

has full period \(m\) if and only if all three conditions hold:

1. 

   \[
   \gcd(c,m)=1;
   \]

2. every prime factor \(p\) of \(m\) divides:

   \[
   a-1;
   \]

3. if:

   \[
   4\mid m,
   \]

   then:

   \[
   4\mid(a-1).
   \]

These conditions are elegant and useful.

They are **not a cryptographic security theorem**.

### Example for a power-of-two modulus

Let:

\[
m=2^w.
\]

The only prime factor is:

\[
2.
\]

For a full-period mixed LCG:

- \(c\) must be odd;
- \(a-1\) must be divisible by \(4\) when \(w\ge2\).

Equivalently:

\[
a\equiv1\pmod4,
\]

\[
c\equiv1\pmod2.
\]

That can give a period of:

\[
2^w.
\]

But the recurrence remains affine.

An attacker who recovers the state still predicts every future value.

### Period and unpredictability are different axes

| Property | Useful in simulation? | Sufficient for cryptography? |
|---|---:|---:|
| Long period | yes | no |
| Fast generation | yes | no |
| Uniform-looking histogram | yes | no |
| Low-order statistical quality | yes | no |
| State-recovery resistance | not always required | essential |
| Next-output unpredictability | not always required | essential |

A sequence can visit every state before repeating and still be completely predictable.

### Low bits can be especially structured

For power-of-two moduli, low-order bits of LCGs often have much shorter periods than the full state.

For example, modulo \(2\), the recurrence reduces to:

\[
S_{i+1}
\equiv
aS_i+c
\pmod2.
\]

That tiny recurrence can be highly regular even when the complete 32-bit or 64-bit state has a long period.

This is one historical reason some libraries returned higher state bits rather than low bits.

But extracting "better-looking" bits does not turn an LCG into a CSPRNG.

It merely changes the attack surface.

### Spectral structure

LCG outputs also exhibit lattice structure in higher-dimensional tuples.

Points such as

\[
\left(
\frac{S_i}{m},
\frac{S_{i+1}}{m},
\ldots
\right)
\]

do not fill the continuous cube arbitrarily.

They lie on families of parallel hyperplanes.

The spectral test measures aspects of this structure and is important for simulation-quality analysis.

Again, this is a statistical/geometric quality issue.

Cryptographic state recovery is an even stronger objection: the recurrence itself is solvable.

---

## From State Recovery to Keystream Prediction

Suppose someone builds a stream cipher by taking LCG states as keystream words:

\[
KS_i=S_i.
\]

Encryption is:

\[
C_i=P_i\oplus KS_i.
\]

This immediately combines two weaknesses:

1. XOR encryption reveals keystream under known plaintext;
2. LCG keystream reveals its recurrence from enough full states.

### Known plaintext exposes keystream

If the attacker knows \(P_i\) and observes \(C_i\), then:

\[
KS_i=C_i\oplus P_i.
\]

So known plaintext can reveal generator outputs.

This is not special to LCGs.

Any synchronous stream cipher exposes keystream wherever plaintext is known.

A secure stream cipher remains safe because its keystream does not reveal the key/state efficiently.

An LCG does not have that protection.

### Three recovered state words may be enough

If:

\[
KS_0=S_0,
\quad
KS_1=S_1,
\quad
KS_2=S_2
\]

are recovered and \(m\) is known, then in the invertible-difference case:

\[
a
\equiv
(S_2-S_1)
(S_1-S_0)^{-1}
\pmod m,
\]

\[
c
\equiv
S_1-aS_0
\pmod m.
\]

Then:

\[
KS_3
=
aS_2+c
\pmod m.
\]

The attacker predicts the next keystream block.

### Predictability breaks semantic security

A stream cipher should make ciphertext computationally indistinguishable from appropriate random-looking encryption under its security model.

If the attacker can predict future keystream, then future plaintext follows:

\[
P_i=C_i\oplus KS_i.
\]

The failure is fundamental.

No amount of histogram testing repairs it.

### Secret parameters do not fix the design

One might try to hide:

\[
a,\ c,\ m.
\]

But as the previous section showed, the modulus itself may be recoverable, and then \(a,c\) can follow.

"Security by secret algorithm parameters" is not a substitute for a keyed cryptographic design.

### Output truncation changes the attack, not the principle

If only part of each state is exposed, direct recovery may require:

- more outputs;
- lattice methods;
- constraint solving;
- brute force over hidden bits.

This can make cryptanalysis more sophisticated.

It does not create a general proof of cryptographic security.

The correct conclusion is:

> raw-state LCGs are trivially predictable, and transformed/truncated LCG variants require separate analysis rather than being presumed secure.

---

## Executable Experiments

The companion lab can make three different points:

1. recover \(a,c\) when \(m\) is known and the state difference is invertible;
2. enumerate multiplier candidates when the inverse does not exist;
3. reconstruct an unknown modulus from several outputs.

### Lab A: known modulus, invertible difference

```python
from math import gcd


def lcg_step(state, a, c, m):
    return (
        a * state + c
    ) % m


def recover_known_modulus(
    s0,
    s1,
    s2,
    m,
):
    d0 = (s1 - s0) % m
    d1 = (s2 - s1) % m

    if gcd(d0, m) != 1:
        raise ValueError(
            "difference is not invertible"
        )

    a = (
        d1
        * pow(d0, -1, m)
    ) % m

    c = (
        s1 - a * s0
    ) % m

    return a, c
```

A test should verify:

```python
recovered_a, recovered_c = (
    recover_known_modulus(
        states[0],
        states[1],
        states[2],
        m,
    )
)

assert recovered_a == a
assert recovered_c == c

assert (
    lcg_step(
        states[2],
        recovered_a,
        recovered_c,
        m,
    )
    ==
    states[3]
)
```

The final assertion is important.

Parameter recovery matters because it predicts unseen output.

### Lab B: non-invertible difference

A general linear-congruence solver can return all candidates:

```python
from math import gcd


def solve_multiplier_candidates(
    d0,
    d1,
    m,
):
    d0 %= m
    d1 %= m

    g = gcd(d0, m)

    if d1 % g != 0:
        return []

    d0_reduced = d0 // g
    d1_reduced = d1 // g
    m_reduced = m // g

    a0 = (
        d1_reduced
        * pow(
            d0_reduced,
            -1,
            m_reduced,
        )
    ) % m_reduced

    return [
        (
            a0
            + k * m_reduced
        ) % m
        for k in range(g)
    ]
```

Each candidate \(a\) yields:

\[
c=S_1-aS_0\pmod m.
\]

Use later observations to filter. The deterministic example used for this article deliberately produces two multiplier candidates that both survive one more observed transition, which is a useful reminder that parameter uniqueness and output predictability are different questions.

This experiment demonstrates why modular arithmetic requires more care than replacing division with `/`.

### Lab C: unknown modulus

```python
from functools import reduce
from math import gcd


def recover_modulus_candidate(
    states,
):
    diffs = [
        states[i + 1] - states[i]
        for i in range(
            len(states) - 1
        )
    ]

    multiples = []

    for i in range(
        len(diffs) - 2
    ):
        z = (
            diffs[i]
            * diffs[i + 2]
            -
            diffs[i + 1] ** 2
        )

        if z != 0:
            multiples.append(
                abs(z)
            )

    if not multiples:
        raise ValueError(
            "insufficient nondegenerate data"
        )

    return reduce(
        gcd,
        multiples,
    )
```

For a favorable raw-state trace, the result may equal \(m\) exactly.

If it yields a multiple of \(m\), candidate factors can be tested against the complete sequence.

### Deterministic test parameters

A small reproducible experiment can use:

\[
m=2^{31}-1,
\]

with chosen \(a,c,S_0\) satisfying the test conditions.

The goal is not to imitate a production PRNG.

The goal is to make the algebra visible and mechanically verifiable.

### What the tests prove

These labs demonstrate:

- correctness of the recovery equations;
- ambiguity when modular inverses do not exist;
- divisibility fingerprints when the modulus is hidden;
- exact next-state prediction after recovery.

They do **not** prove that every truncated or transformed LCG can be broken with exactly three outputs.

The observation model matters.

That qualification is part of doing cryptanalysis correctly.

---

## Conclusion

A linear congruential generator is mathematically elegant:

\[
S_{i+1}
=
aS_i+c
\pmod m.
\]

Its simplicity is useful for teaching because nearly every important distinction in pseudorandomness becomes visible.

With known modulus and three full consecutive states:

\[
S_0,S_1,S_2,
\]

subtracting the recurrence gives:

\[
S_2-S_1
\equiv
a(S_1-S_0)
\pmod m.
\]

When the first difference is invertible:

\[
\boxed{
a
\equiv
(S_2-S_1)
(S_1-S_0)^{-1}
\pmod m
}
\]

and:

\[
\boxed{
c
\equiv
S_1-aS_0
\pmod m.
}
\]

When the inverse does not exist, recovery becomes a modular linear-congruence problem with potentially several candidate multipliers rather than a dead end.

When the modulus is unknown, first differences satisfy:

\[
t_{i+1}
\equiv
at_i
\pmod m,
\]

which implies:

\[
\boxed{
t_it_{i+2}
-
t_{i+1}^2
\equiv0
\pmod m.
}
\]

GCDs of these integer multiples can reveal a candidate modulus.

The Hull–Dobell theorem can guarantee a maximal period for a mixed LCG under precise arithmetic conditions.

That is valuable for simulation.

It is not cryptographic security.

The central distinction is:

\[
\boxed{
\text{long cycle}
\neq
\text{hard-to-predict sequence}
}
\]

and the attack reason is structural:

\[
\boxed{
\text{the recurrence is efficiently solvable}.
}
\]

This makes the LCG the ideal first weak generator for the series.

The next step is more interesting.

An LFSR can also have an enormous period, but instead of affine arithmetic modulo \(m\), its structure lives in:

\[
\mathbb F_2.
\]

That brings us to:

- characteristic polynomials;
- primitive polynomials;
- maximal-length sequences;
- linear complexity;
- Berlekamp–Massey;
- reconstruction of a binary recurrence from observed bits.

The mathematics becomes richer, but the cryptographic lesson remains familiar:

\[
\boxed{
\text{linearity leaves equations for the attacker}.
}
\]


---

## References

1. D. H. Lehmer, **Mathematical Methods in Large-Scale Computing Units**, Proceedings of the Second Symposium on Large-Scale Digital Calculating Machinery, 1951.

2. T. E. Hull and A. R. Dobell, **Random Number Generators**, SIAM Review, Vol. 4, No. 3, 1962.

3. Donald E. Knuth, **The Art of Computer Programming, Volume 2: Seminumerical Algorithms**, sections on random-number generation.

4. Pierre L'Ecuyer, work on random-number generators, lattice structure, and statistical quality of linear generators.

5. Oded Goldreich, **Foundations of Cryptography, Volume 1**, for the distinction between statistical properties and computational pseudorandomness.
