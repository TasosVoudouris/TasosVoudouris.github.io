---
title: "Fast Modular Exponentiation: From Square-and-Multiply to the First Side-Channel Leak"
description: "Binary exponentiation makes huge cryptographic powers practical—but a secret-dependent execution trace can also reveal information. We build the algorithm, inspect the trace, and harden the mental model."
pubDate: "2026-09-08"
category: "Implementations"
tags:
  - modular-exponentiation
  - square-and-multiply
  - side-channels
  - timing-attacks
  - rsa
  - cryptography-from-zero
difficulty: "Intermediate"
series: "Cryptography From Zero"
draft: false
---

There is a line of Python we have already used many times:

```python
pow(g, e, n)
```

It looks almost too simple.

But underneath that line sits one of the most important computational routines in classical public-key cryptography.

RSA needs powers modulo a large composite integer.

Finite-field Diffie-Hellman needs powers modulo a large prime.

Primality tests repeatedly compute modular powers.

And the exponent may be hundreds or thousands of bits long.

So at some point I had to ask the question I should probably have asked earlier:

> Are we literally multiplying the base by itself $e$ times?

Fortunately, no.

The algorithm uses the **binary representation of the exponent**.

And that gives us an enormous speedup.

But the moment I implemented it step by step, another question appeared:

> If the control flow depends on the secret exponent bits, can the execution itself reveal them?

That is our first side-channel question.

![Square-and-multiply trace leaking exponent structure](/images/blog/08-square-multiply-sidechannel.svg)

*The optimization is mathematically correct. The problem is that a secret-dependent operation pattern may become observable through timing, power, cache behavior, electromagnetic leakage, or another side channel.*

---

## Build: do not multiply $e$ times

Suppose we want:

$$
7^{13}\bmod23.
$$

The naive idea is:

```python
def pow_naive(base, exponent, modulus):
    result = 1

    for _ in range(exponent):
        result = (result * base) % modulus

    return result
```

For exponent $13$, that is fine.

For a cryptographic exponent containing hundreds or thousands of bits, it is useless.

The important observation is that:

$$
13=(1101)_2.
$$

Or equivalently:

$$
13=8+4+1.
$$

Therefore:

$$
7^{13}
=
7^8\cdot7^4\cdot7.
$$

And powers of two are easy to obtain by repeated squaring:

$$
7,
$$

$$
7^2,
$$

$$
7^4,
$$

$$
7^8,
$$

$$
7^{16},
$$

and so on.

Instead of performing work proportional to the **numerical value** of the exponent, we perform work proportional to its **bit length**.

For an exponent $e$, that means roughly:

$$
O(\log e)
$$

modular multiplications.

This is why modular exponentiation remains practical even when the exponent itself is enormous.

---

A left-to-right square-and-multiply implementation is:

```python
def square_and_multiply(base, exponent, modulus):
    result = 1

    for bit in bin(exponent)[2:]:
        result = (result * result) % modulus

        if bit == "1":
            result = (result * base) % modulus

    return result
```

For:

```python
base = 7
exponent = 13
modulus = 23
```

the exponent bits are:

```text
1101
```

Now trace the operations.

### Bit 1

Square:

$$
1^2\equiv1\pmod{23}.
$$

The bit is $1$, so multiply:

$$
1\cdot7\equiv7\pmod{23}.
$$

### Bit 1

Square:

$$
7^2=49\equiv3\pmod{23}.
$$

Multiply:

$$
3\cdot7=21\pmod{23}.
$$

### Bit 0

Square:

$$
21^2=441\equiv4\pmod{23}.
$$

No multiply.

### Bit 1

Square:

$$
4^2=16\pmod{23}.
$$

Multiply:

$$
16\cdot7=112\equiv20\pmod{23}.
$$

So:

$$
\boxed{
7^{13}\equiv20\pmod{23}.
}
$$

Python agrees:

```python
assert square_and_multiply(7, 13, 23) == 20
assert pow(7, 13, 23) == 20
```

So far this is simply a good algorithm.

Now print the trace.

---

## Break: the operation pattern knows the exponent bits

Let us instrument the code:

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

For exponent:

```text
1101
```

we get:

```text
S M | S M | S | S M
```

That is suspicious.

Each exponent bit causes a square.

But only a $1$ bit causes the extra multiply.

So the toy operation trace directly reflects the secret bit pattern:

```text
bit 1 → S M
bit 1 → S M
bit 0 → S
bit 1 → S M
```

or:

```text
1101
```

This is the first time in the series where the **answer can remain perfectly correct while the way we computed it leaks secret information**.

Nothing is wrong with:

$$
7^{13}\bmod23.
$$

Nothing is wrong with square-and-multiply as mathematics.

The issue is the implementation rule:

```python
if bit == "1":
    multiply()
```

when `bit` is secret.

---

### Does this mean timing immediately reveals the private key?

No.

That would be too simple.

Our trace is an intentionally clean teaching model where we can see the branch directly.

A real attacker may observe only an indirect physical or microarchitectural signal:

- total execution time,
- power consumption,
- electromagnetic radiation,
- cache accesses,
- branch behavior,
- memory-access patterns.

Real implementations also contain:

- different multiplication algorithms,
- modular reductions,
- precomputation tables,
- CPU caches,
- compiler optimizations,
- noise,
- network latency.

So practical side-channel cryptanalysis is a statistical and implementation-specific problem.

But the dangerous dependency is already visible here:

$$
\text{secret bit}
\longrightarrow
\text{different execution behavior}.
$$

That is enough to change how we should think about implementation security.

---

> **Research connection — timing became cryptanalysis.**  
> Paul Kocher's 1996 paper *Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems* showed that timing measurements of private-key operations can reveal secret information in vulnerable implementations.
>
> [Read Kocher's paper](https://www.paulkocher.com/doc/TimingAttacks.pdf)
>
> And in 2003, David Brumley and Dan Boneh went further with *Remote Timing Attacks Are Practical*: they demonstrated private-key extraction against an OpenSSL-based server across a local network.
>
> [USENIX Security 2003 — Remote Timing Attacks Are Practical](https://www.usenix.org/conference/12th-usenix-security-symposium/remote-timing-attacks-are-practical)

This is one of the papers I like connecting back to simple code.

You can start with:

```python
if bit == "1":
```

and eventually arrive at a real remote key-recovery attack.

That is exactly the kind of path I want this blog to preserve.

---

## Mitigate: regularity matters, but "same number of operations" is not the whole story

The first instinct is:

> Then just remove the branch.

That is directionally correct, but implementation hardening is more subtle than writing one branchless-looking Python function.

For secret-dependent arithmetic, we want to avoid observable behavior that depends on secret values.

That usually means thinking about:

```text
control flow
memory accesses
table lookups
operation sequence
arithmetic timing
compiler transformations
microarchitecture
```

One useful conceptual pattern is a **regular exponentiation algorithm**, where each secret bit follows the same high-level schedule.

For example, a Montgomery-ladder-style idea maintains two accumulators and performs a regular pair of operations per bit.

At a high level:

```text
for every secret bit:
    one multiply
    one square
```

rather than:

```text
always square
multiply only for bit 1
```

But there is an important warning:

> A constant operation count is not automatically a constant-time implementation.

If the operations themselves behave differently depending on secret values, or secret-dependent memory accesses remain, leakage may still exist.

Similarly, a naive "square-and-multiply-always" implementation can still leak through power analysis if the two operation roles remain distinguishable.

So the real goal is broader:

$$
\boxed{
\text{secret data should not create attacker-observable variation}.
}
$$

That is a much better mental model than simply "remove the `if`."

---

For RSA, another classical defense is **blinding**.

Instead of directly performing the private operation on attacker-controlled input, the implementation randomizes the computation so that repeated observations are decorrelated from the fixed private key operation.

We will implement RSA blinding properly when we reach RSA private operations.

For now, remember the design pattern:

```text
secret-dependent operation
        ↓
ask what an attacker can observe
        ↓
remove / mask / randomize exploitable dependence
        ↓
test the implementation, not only the formula
```

And one more practical point for our Python repository:

> Python's built-in `pow(base, exponent, modulus)` is excellent for our mathematical experiments, but we should not treat ordinary Python big-integer code as a constant-time production cryptographic implementation.

Our repository is designed to expose the algorithm.

Production cryptographic libraries have a different engineering burden.

---

Try this experiment yourself.

Change:

```python
exponent = 13
```

to:

```python
exponent = 9
```

Binary:

```text
1001
```

What trace do you expect?

Then try:

```python
exponent = 15
```

Binary:

```text
1111
```

Compare:

```text
number of S operations
number of M operations
Hamming weight of the exponent
```

You should notice:

$$
\#M
=
\text{number of 1-bits in the exponent}.
$$

That does **not** mean a real timing measurement simply returns the Hamming weight.

It means our implementation contains a secret-dependent structural difference that a physical or microarchitectural channel may amplify.

That is the point of the exercise.

---

We have now attacked cryptography at four different layers:

```text
mathematical hardness
    → tiny DLP

protocol authentication
    → MITM

group/input validation
    → small-subgroup attack

implementation behavior
    → side-channel leakage
```

And I think this is the moment where "implementation details" stops sounding like the boring part after the cryptography.

The implementation **is part of the cryptography**.

Next I want to stay with modular exponentiation for one more step, but move from leakage to a different physical failure.

What if the computation does not merely reveal information?

What if we make it compute the **wrong answer on purpose**?

With CRT-RSA, one faulty modular exponentiation can be enough to recover a prime factor of the RSA modulus with a single GCD.

**Next:** *Fault Attacks From Zero: How One Wrong RSA Computation Can Reveal a Prime Factor.*
