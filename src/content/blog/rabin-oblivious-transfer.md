---
title: "Rabin Oblivious Transfer: A 50% Transfer from Square Roots and Factoring"
description: "Derive Rabin's original oblivious-transfer idea from square roots modulo an RSA modulus, explain the exact 1/2 success probability, and separate the honest-party toy protocol from malicious-security requirements."
pubDate: "2025-05-14"
updatedDate: "2026-09-12"
topics:
  - "MPC"
  - "Public-Key Cryptography"
  - "Number Theory"
  - "Cryptography Fundamentals"
tags:
  - "oblivious-transfer"
  - "rabin-ot"
  - "factoring"
  - "quadratic-residues"
  - "rsa"
difficulty: "Intermediate"
series: "Oblivious Transfer"
seriesOrder: 1
sourcePath: "experiments/oblivious-transfer"
status: "Validated"
draft: false
---
Oblivious transfer is one of the foundational primitives of secure computation. Rabin's original form has an unusual goal: the receiver learns a secret with probability $1/2$, while the sender does not learn whether the transfer succeeded.

This is **not yet 1-out-of-2 OT**. It is the earlier probabilistic primitive from which later equivalent formulations were developed.

## The square-root fact behind the protocol

Let

$$
n=pq
$$

for distinct odd primes. If $x\in\mathbb Z_n^*$, then the quadratic residue

$$
a=x^2\pmod n
$$

has four square roots modulo $n$ under the usual semiprime conditions.

Two are $\pm x$. The other pair, say $\pm y$, differs in one CRT sign component. If

$$
y\not\equiv \pm x\pmod n,
$$

then

$$
\gcd(x-y,n)
$$

reveals a non-trivial factor of $n$.

That is the algebraic engine of Rabin OT.

## Protocol

Let Alice be the sender and Bob the receiver.

### 1. Sender setup

Alice chooses primes $p,q$, sets $n=pq$, and publishes a public-key encryption context based on the factorization hardness of $n$. She encrypts the secret message $m$ as a ciphertext $C$.

### 2. Receiver challenge

Bob chooses random

$$
x\in\mathbb Z_n^*
$$

and sends

$$
a=x^2\pmod n.
$$

### 3. Sender response

Because Alice knows $p$ and $q$, she can compute all four square roots of $a$. She chooses one root $y$ uniformly and sends it to Bob.

### 4. Receiver outcome

If

$$
y\equiv x\quad\text{or}\quad y\equiv -x\pmod n,
$$

Bob learns no factor.

If $y$ is one of the other two roots, then a GCD such as

$$
g=\gcd(x-y,n)
$$

returns $p$ or $q$. Bob can then factor $n$ and recover the encrypted secret.

## Why the probability is exactly one half

Among the four square roots:

- two are congruent to $\pm x$ and give no new factor;
- two are nontrivially related and reveal a factor.

If Alice's root choice is uniform, Bob succeeds with probability

$$
\frac{2}{4}=\frac12.
$$

Alice does not know which square root Bob originally used, so in the honest execution she cannot tell whether the returned root was useful to him.

## Security-model caveat

The simple argument assumes Bob generated his challenge honestly as a square of a value he knows. Historical work observed that a malicious receiver might try to send a specially prepared quadratic residue instead.

A robust formulation therefore needs a proof that Bob knows an appropriate square root, or another protocol transformation that closes the malicious-receiver gap.

This is an important recurring lesson: **an algebraically correct honest-party transcript is not automatically a malicious-secure protocol**.

## Why the message is often encrypted separately

The square-root exchange transfers the **ability to factor the modulus** with probability $1/2$. To transfer an arbitrary message, Alice can encrypt the message under a key whose inversion becomes possible after factoring.

That separates two layers:

1. probabilistically reveal the trapdoor;
2. use the trapdoor to recover the payload.

## Executable toy experiment

The companion code uses tiny fixed primes and enumerates the four roots of a square. It verifies that exactly two of the four roots produce a non-trivial factor:

```bash
python experiments/oblivious-transfer/test_ot.py
```

The parameters are intentionally insecure. The point is to make the CRT/factoring relation executable.

## Why OT matters beyond this protocol

Rabin OT and 1-out-of-2 OT are known to be closely related/equivalent under protocol transformations, and oblivious transfer is a complete primitive for general secure multiparty computation in standard models.

That is why a seemingly odd "learn a secret with probability one half" construction became a central building block in modern MPC.
