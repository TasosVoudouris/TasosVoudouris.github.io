---
title: "Fast Modular Exponentiation: From Square-and-Multiply to the First Side-Channel Leak"
description: "Binary exponentiation makes huge cryptographic powers practical—but a secret-dependent execution trace can also reveal information. We build the algorithm, inspect the trace, and harden the mental model."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Cryptographic Engineering"
  - "Implementation Security"
  - "Public-Key Cryptography"
tags:
  - "modular-exponentiation"
  - "square-and-multiply"
  - "side-channels"
  - "timing-attacks"
  - "rsa"
  - "cryptography-from-zero"
difficulty: "Intermediate"
series: "Cryptography From Zero"
seriesOrder: 9
draft: false
---

There is a line of Python we have already used many times:

```python
pow(g, e, n)
```

It looks almost too simple.

But underneath that line sits one of the most important computational routines in classical public-key cryptography.

RSA repeatedly computes powers modulo a large composite integer.

Finite-field Diffie-Hellman computes powers modulo a large prime.

Primality tests such as Miller-Rabin perform modular exponentiation again and again.

And in all of these cases, the exponent may contain hundreds or thousands of bits.

So an obvious question appears:

> Are we literally multiplying the base by itself $e$ times?

Fortunately, no.

Efficient modular exponentiation exploits the **binary representation of the exponent**.

That reduces an impossibly large computation to a sequence whose length is proportional to the number of bits in the exponent.

But the moment we make that sequence explicit, another question appears:

> If the sequence of operations depends on secret exponent bits, can observing the computation reveal those bits?

That is our first side-channel question.

![Square-and-multiply trace leaking exponent structure](/images/blog/08-square-multiply-sidechannel.svg)

*The optimization is mathematically correct. The implementation problem appears when secret-dependent operation patterns become observable through timing, power consumption, cache activity, electromagnetic leakage, or another side channel.*

---

## Table of Contents

- [Why naive exponentiation is too slow](#why-naive-exponentiation-is-too-slow)
- [Square-and-multiply](#square-and-multiply)
- [When the execution trace leaks structure](#when-the-execution-trace-leaks-structure)
- [From toy traces to real side channels](#from-toy-traces-to-real-side-channels)
- [A classic research connection](#a-classic-research-connection)
- [Mitigation: regularity, constant time, and blinding](#mitigation-regularity-constant-time-and-blinding)
- [Experiment with the trace](#experiment-with-the-trace)
- [Papers and further reading](#papers-and-further-reading)
- [What we have learned so far](#what-we-have-learned-so-far)

---

## Why naive exponentiation is too slow

Suppose we want to compute

$$
7^{13}\bmod 23.
$$

A direct implementation could repeatedly multiply by $7$:

```python
def pow_naive(base, exponent, modulus):
    result = 1

    for _ in range(exponent):
        result = (result * base) % modulus

    return result
```

For

$$
e=13,
$$

this is perfectly manageable.

But imagine instead that the exponent is a 2048-bit RSA private exponent.

Its numerical value may be on the order of

$$
2^{2048}.
$$

Performing one multiplication for every integer step up to that exponent is completely impossible.

The important observation is that the exponent can be represented in binary.

For example,

$$
13=(1101)_2.
$$

Equivalently,

$$
13=8+4+1.
$$

Therefore,

$$
7^{13}
=
7^8\cdot7^4\cdot7.
$$

The powers

$$
7,\quad
7^2,\quad
7^4,\quad
7^8,\quad
7^{16},\ldots
$$

are easy to generate because each one is obtained by squaring the previous value.

That changes the complexity dramatically.

If the exponent $e$ has bit length

$$
\ell=\lfloor\log_2 e\rfloor+1,
$$

then square-and-multiply performs work proportional to roughly

$$
O(\ell)=O(\log e)
$$

modular multiplications rather than $O(e)$.

That is the reason modular exponentiation remains practical even when the exponent itself is enormous.

---

## Square-and-multiply

A simple left-to-right implementation is:

```python
def square_and_multiply(base, exponent, modulus):
    result = 1

    for bit in bin(exponent)[2:]:
        result = (result * result) % modulus

        if bit == "1":
            result = (result * base) % modulus

    return result
```

Take:

```python
base = 7
exponent = 13
modulus = 23
```

Since

$$
13=(1101)_2,
$$

the algorithm processes the bit string:

```text
1101
```

Rather than making each bit a large subsection, it is easier to inspect the entire computation as one trace:

| Bit | Operation(s) | Result modulo $23$ |
| ---: | --- | ---: |
| `1` | square $1^2$, then multiply by $7$ | $7$ |
| `1` | square $7^2=49\equiv3$, then multiply by $7$ | $21$ |
| `0` | square $21^2=441\equiv4$ | $4$ |
| `1` | square $4^2=16$, then multiply by $7$ | $20$ |

Thus,

$$
\boxed{
7^{13}\equiv20\pmod{23}
}
$$

and Python confirms it:

```python
assert square_and_multiply(7, 13, 23) == 20
assert pow(7, 13, 23) == 20
```

So mathematically everything is correct.

The interesting part appears when we stop looking only at the final value and instead inspect **how the value was computed**.

---

## When the execution trace leaks structure

Instrument the algorithm:

```python
def traced_square_and_multiply(base, exponent, modulus):
    result = 1
    trace = []

    for bit in bin(exponent)[2:]:
        result = (result * result) % modulus
        trace.append("S")

        if bit == "1":
            result = (result * base) % modulus
            trace.append("M")

    return result, trace
```

For

$$
e=13=(1101)_2,
$$

the operation trace is:

```text
S M | S M | S | S M
```

That immediately exposes structure.

Each exponent bit always causes a square:

```text
bit 0 → S
bit 1 → S M
```

So the observed trace

```text
S M | S M | S | S M
```

maps directly back to

```text
1 1 0 1
```

in this deliberately simplified implementation.

This gives us a new kind of failure.

The final mathematical answer can remain completely correct while the **computation leaks information about the secret**.

Nothing is wrong with

$$
7^{13}\bmod23.
$$

Nothing is wrong with binary exponentiation as mathematics.

The dangerous part is the implementation rule:

```python
if bit == "1":
    multiply()
```

when `bit` belongs to a secret exponent.

The secret influences the execution path:

$$
\boxed{
\text{secret bit}
\longrightarrow
\text{different operation pattern}
}
$$

and if the operation pattern becomes observable, information about the secret may become observable as well.

### The Hamming weight connection

For this particular implementation, every exponent bit produces one squaring.

The number of additional multiplications is equal to the number of `1` bits in the exponent.

If

$$
\operatorname{wt}(e)
$$

denotes the Hamming weight of the binary representation of $e$, then

$$
N_M=\operatorname{wt}(e).
$$

For

$$
13=(1101)_2,
$$

we have

$$
\operatorname{wt}(13)=3,
$$

so the trace contains three additional multiplications.

This does **not** mean that a real timing measurement simply returns the Hamming weight of a private key.

It means that the algorithm contains a secret-dependent structural difference that a physical or microarchitectural channel may potentially expose.

That is the important observation.

---

## From toy traces to real side channels

Our trace is intentionally unrealistically clean.

We directly record whether the algorithm performed:

```text
S
```

or:

```text
S M
```

for every bit.

A real attacker normally cannot inspect the victim's Python list of operations.

Instead, the secret-dependent execution may influence some measurable physical or microarchitectural quantity.

Examples include:

- total execution time,
- power consumption,
- electromagnetic emissions,
- cache accesses,
- branch prediction behavior,
- memory-access patterns.

Real implementations are also much more complicated than our educational function.

They may contain:

- multiple big-integer multiplication algorithms,
- Montgomery reduction,
- sliding-window exponentiation,
- precomputation tables,
- CPU caches,
- compiler optimizations,
- branch predictors,
- operating-system scheduling,
- network noise.

So practical side-channel cryptanalysis is not usually:

```text
observe one trace
        ↓
read private key
```

It is often a statistical inference problem.

The attacker collects observations, builds hypotheses about secret-dependent behavior, and tests which hypotheses best explain the measurements.

But the security problem begins exactly where our tiny implementation reveals it:

$$
\text{secret state}
\longrightarrow
\text{observable behavior}.
$$

This is the point where implementation details become part of the cryptographic threat model.

---

## A classic research connection

One of the foundational papers in this area is Paul Kocher's 1996 work:

**Paul C. Kocher, _Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems_.**

The central insight is remarkably powerful: even when an attacker cannot directly inspect the secret exponent, differences in the running time of private-key operations may reveal information about it.

The paper helped establish timing behavior as a serious cryptanalytic channel rather than merely a performance characteristic.

A later and especially striking result was:

**David Brumley and Dan Boneh, _Remote Timing Attacks Are Practical_, USENIX Security 2003.**

Their work demonstrated that timing differences could be exploited remotely against an OpenSSL-based server in a suitable network environment.

That connection is one of the reasons this tiny line:

```python
if bit == "1":
```

is worth studying carefully.

A small implementation decision can sit at the beginning of a path that eventually leads to practical private-key recovery research.

---

## Mitigation: regularity, constant time, and blinding

The immediate reaction is usually:

> Remove the branch.

That is directionally correct, but it is not a complete solution.

The real objective is broader:

$$
\boxed{
\text{secret data should not create exploitable attacker-observable variation}
}
$$

For secret-dependent arithmetic, we therefore care about more than source-code branches.

Relevant properties include:

```text
control flow
memory accesses
table indexes
operation sequence
arithmetic latency
compiler transformations
microarchitectural behavior
```

### Regular exponentiation

One useful design direction is to use an exponentiation strategy where every secret bit follows a regular high-level schedule.

A Montgomery-ladder-style pattern, for example, maintains two accumulators and performs a fixed pattern of multiplication and squaring for every bit.

Conceptually:

```text
for each secret bit:

    one multiplication
    one squaring
```

rather than:

```text
always square

if bit == 1:
    multiply
```

The important word is **conceptually**.

A regular operation count does not automatically produce constant-time machine code.

If the implementation still performs:

- secret-dependent conditional swaps,
- secret-dependent memory accesses,
- variable-time arithmetic,
- secret-indexed table lookups,

then leakage may remain.

Likewise, a naive "square-and-multiply-always" design can still leak through power analysis if the physical signatures of its operations remain distinguishable.

So we should avoid reducing side-channel security to the rule:

> "Every branch is bad; no branch means constant time."

The real property is much stronger.

### Constant-time programming

In production cryptographic software, constant-time programming attempts to ensure that attacker-observable execution behavior is independent of secret values, within an appropriate model.

This commonly means avoiding:

- secret-dependent branches,
- secret-dependent memory addresses,
- variable-time comparison,
- secret-dependent table indexing,
- data-dependent early termination.

But even carefully written source code is not enough by itself.

Compiler behavior, architecture-specific instructions, cache effects, and microarchitecture may matter.

That is why constant-time cryptography is an engineering discipline of its own.

### Blinding

Another classical mitigation, especially important for RSA, is **blinding**.

Instead of repeatedly applying the private-key operation directly to attacker-controlled inputs, the implementation randomizes the computation.

The goal is to decorrelate observable behavior from the fixed private operation.

Conceptually:

```text
attacker-controlled input
        ↓
randomize / blind
        ↓
private-key operation
        ↓
remove blinding
        ↓
correct result
```

We will study RSA blinding in detail when we reach RSA private operations.

For now the important lesson is that side-channel defenses often combine several techniques:

```text
regular algorithms
        +
constant-time implementation
        +
blinding
        +
careful memory behavior
        +
testing on the real platform
```

not merely one syntactic trick.

### A note about Python

Python's built-in:

```python
pow(base, exponent, modulus)
```

is excellent for our mathematical experiments.

But ordinary Python big-integer arithmetic should **not** be treated as a constant-time production cryptographic implementation.

Our educational repository has a different objective.

We deliberately expose:

- algorithmic structure,
- intermediate values,
- branches,
- traces.

That makes the mathematics easier to understand.

A production cryptographic library has almost the opposite requirement: secret-dependent internal structure should be as difficult to observe as possible.

---

## Experiment with the trace

Change:

```python
exponent = 13
```

to:

```python
exponent = 9
```

Since

$$
9=(1001)_2,
$$

predict the trace before running the program.

It should have the form:

```text
S M | S | S | S M
```

because only the first and final bits are `1`.

Then try:

```python
exponent = 15
```

with

$$
15=(1111)_2.
$$

Now every bit causes both operations:

```text
S M | S M | S M | S M
```

Compare the following quantities:

| Exponent | Binary | Bit length | Hamming weight | Extra multiplies |
| ---: | --- | ---: | ---: | ---: |
| $9$ | `1001` | 4 | 2 | 2 |
| $13$ | `1101` | 4 | 3 | 3 |
| $15$ | `1111` | 4 | 4 | 4 |

The number of squarings remains tied to the bit length.

The number of conditional multiplications follows the Hamming weight.

Again, this table is a **teaching model**, not a complete model of a real timing attack.

Its purpose is to reveal the dependency:

$$
\text{secret exponent}
\rightarrow
\text{operation schedule}.
$$

### Reader checkpoint

At this point you should be able to explain:

1. Why repeated multiplication takes $O(e)$ work.
2. Why binary exponentiation takes only $O(\log e)$ modular operations.
3. Why the binary representation of the exponent controls square-and-multiply.
4. Why a `1` bit produces an extra multiplication in the simple implementation.
5. Why secret-dependent control flow creates a potential side channel.
6. Why a fixed number of operations does not automatically imply constant-time behavior.
7. Why Python's `pow()` is appropriate for our experiments but should not be treated as a constant-time cryptographic guarantee.

The conceptual progression is:

```text
efficient algorithm
        ↓
secret-dependent trace
        ↓
observable variation
        ↓
side-channel information
```

---

## Papers and further reading

### Kocher — timing attacks

**Paul C. Kocher**,  
*Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems*,  
CRYPTO 1996.

This is one of the foundational papers showing that execution-time measurements can expose information about private-key computations.

### Brumley and Boneh — remote timing

**David Brumley and Dan Boneh**,  
*Remote Timing Attacks Are Practical*,  
12th USENIX Security Symposium, 2003.

This work is especially important because it demonstrated that timing attacks were not necessarily restricted to an attacker physically attached to the device.

### Kocher, Jaffe, and Jun — differential power analysis

**Paul Kocher, Joshua Jaffe, and Benjamin Jun**,  
*Differential Power Analysis*,  
CRYPTO 1999.

Power analysis expands the same general lesson beyond execution time: physical measurements correlated with secret-dependent computation can reveal cryptographic secrets.

### Coron — RSA side-channel countermeasures

**Jean-Sébastien Coron**,  
*Resistance Against Differential Power Analysis for Elliptic Curve Cryptosystems*,  
CHES 1999.

Although focused on elliptic-curve scalar multiplication, this work is useful for seeing how regularization and randomization techniques arise as explicit cryptographic countermeasures.

---

## What we have learned so far

We have now attacked our cryptographic constructions at four different layers:

```text
mathematical hardness
        ↓
tiny-group discrete logarithm

protocol authentication
        ↓
man-in-the-middle attack

group and input validation
        ↓
small-subgroup leakage

implementation behavior
        ↓
side-channel leakage
```

This is an important point in the series.

At the beginning, "implementation details" may sound like something that comes **after** the cryptography.

But that separation is misleading.

A secure mathematical construction implemented with secret-dependent leakage can become insecure.

So:

$$
\boxed{
\text{the implementation is part of the cryptographic system}
}
$$

The next article stays close to modular exponentiation but changes the failure model.

Instead of learning something from the execution trace, imagine that an attacker causes one private computation to produce the **wrong answer**.

With CRT-RSA, a single faulty signature can be enough to reveal a prime factor of the RSA modulus through one GCD computation.

That takes us from side channels to **fault attacks**.

**Next: Fault Attacks From Zero — How One Wrong RSA Computation Can Reveal a Prime Factor.**
