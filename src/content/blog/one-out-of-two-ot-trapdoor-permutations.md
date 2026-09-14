---
title: "1-out-of-2 Oblivious Transfer: Choice Privacy from an RSA Trapdoor Permutation"
description: "Work through the classic 1-out-of-2 OT pattern where a receiver learns one of two sender messages without revealing the choice bit, and state the honest/semi-honest security boundary precisely."
pubDate: "2025-05-14"
updatedDate: "2026-09-12"
topics:
  - "MPC"
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
tags:
  - "oblivious-transfer"
  - "1-out-of-2-ot"
  - "egl"
  - "trapdoor-permutation"
  - "rsa"
difficulty: "Intermediate"
series: "Oblivious Transfer"
seriesOrder: 2
sourcePath: "experiments/oblivious-transfer"
status: "Validated"
draft: false
---
The form of oblivious transfer used most often in MPC is **1-out-of-2 OT**.

Alice holds two messages

$$
m_0,m_1,
$$

while Bob holds a choice bit

$$
b\in\{0,1\}.
$$

The target properties are:

- Bob learns $m_b$;
- Bob should not learn $m_{1-b}$;
- Alice should not learn $b$.

The recovered notes implement the classic trapdoor-permutation pattern often associated with Even, Goldreich, and Lempel. RSA gives an intuitive concrete instantiation.

## Setup

Alice creates an RSA modulus

$$
n=pq
$$

and exponents

$$
ed\equiv1\pmod{\varphi(n)}.
$$

She also samples two public random values

$$
x_0,x_1\in\mathbb Z_n.
$$

Bob sees $(n,e,x_0,x_1)$ but not $d$.

## Bob hides the choice

Bob selects a random $k$ and computes

$$
v=x_b+k^e\pmod n.
$$

He sends only $v$.

From Alice's perspective, either $x_0$ or $x_1$ may have been used as the offset.

## Alice creates two candidate masks

Alice uses the trapdoor exponent $d$ to compute

$$
k_0=(v-x_0)^d\pmod n,
$$

$$
k_1=(v-x_1)^d\pmod n.
$$

For the selected index $b$,

$$
v-x_b=k^e,
$$

so

$$
k_b=k.
$$

Alice masks the messages, in a toy integer model, as

$$
c_i=m_i+k_i\pmod n
$$

and returns $(c_0,c_1)$.

## Bob opens one message

Bob knows $k$, so

$$
m_b=c_b-k\pmod n.
$$

He does not know the other RSA preimage $k_{1-b}$.

The algebra therefore explains correctness immediately.

## What the toy arithmetic hides

A production construction cannot casually treat arbitrary messages as integers modulo $n$ and call addition a secure one-time pad. Real protocols need an explicit encoding/KDF layer and a security proof for the exact trapdoor-permutation transformation.

Likewise, the simple transcript is best understood in an honest/semi-honest educational setting. Malicious security requires handling deviations such as malformed values, adaptive behavior, inconsistent messages, or attempts to learn both branches.

This corrects the old report's overstatement that "semantic security of masked values" follows automatically from standard RSA assumptions. The security argument depends on the complete OT construction, not just on the fact that RSA inversion is hard.

## Sender and receiver privacy are different claims

**Receiver privacy** asks whether Alice can distinguish whether Bob formed $v$ from $x_0$ or $x_1$.

**Sender privacy** asks whether Bob can derive both trapdoor preimages and therefore both messages.

A complete proof treats these as separate games/reductions.

## Executable toy implementation

The companion code uses tiny fixed RSA parameters and checks both choice bits:

```bash
python experiments/oblivious-transfer/test_ot.py
```

It is deliberately not production cryptography. Its purpose is to expose the algebraic roles of $v$, the two trapdoor inversions, and Bob's single known preimage.

## From base OT to practical MPC

Public-key OT is expensive if executed once for every wire/value in a large secure computation. Modern systems therefore use a small number of **base OTs** and then expand them with symmetric-key techniques. The next chapter places Naor–Pinkas-style selection protocols and OT extension in that broader evolution.
