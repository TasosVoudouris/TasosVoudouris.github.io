---
title: "Beaver Triples: Secure Multiplication and Offline/Online Preprocessing"
description: "Derive Beaver multiplication from first principles, prove why opening masked differences is safe in the passive model, and implement the offline/online split that powers many arithmetic MPC protocols."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Secret Sharing"
tags:
  - "beaver-triples"
  - "preprocessing"
  - "secure-multiplication"
  - "offline-online"
  - "arithmetic-mpc"
difficulty: "Intermediate"
status: "Validated"
series: "Secure Multiparty Computation"
seriesOrder: 2
sourcePath: "experiments/mpc/beaver-triples"
draft: false
---
Addition of secret shares is easy. Multiplication is the first gate that forces us to confront interaction.

Beaver triples solve this with a remarkably simple algebraic identity.

## 1. Preprocessed correlation

Before private inputs are known, obtain secret sharings

$$
[a],\quad[b],\quad[c]
$$

such that

$$
c=ab.
$$

The triple values themselves must remain hidden from the parties according to the protocol's corruption threshold.

In our educational companion, a trusted dealer generates them. Production systems generate them with cryptographic protocols.

## 2. Online multiplication

Suppose parties hold $[x]$ and $[y]$.

Compute locally

$$
[e]=[x]-[a],
$$

$$
[f]=[y]-[b].
$$

Then **open** $e$ and $f$.

Because $a$ and $b$ are random masks unknown to the adversary, these openings do not reveal $x$ and $y$ in the passive trusted-preprocessing model.

Now form

$$
[z]=[c]+e[b]+f[a]+ef.
$$

The last term is public, so depending on the sharing convention it can be added to one share or represented as a public-shared constant.

## 3. Correctness proof

Substitute

$$
e=x-a,
$$

$$
f=y-b.
$$

Then

$$
\begin{aligned}
c+eb+fa+ef
&=ab+(x-a)b+(y-b)a+(x-a)(y-b)\\
&=ab+xb-ab+ya-ab+xy-xb-ya+ab\\
&=xy.
\end{aligned}
$$

Therefore the result is a valid sharing of the product.

## 4. What gets revealed

The protocol intentionally reveals

$$
e=x-a
$$

and

$$
f=y-b.
$$

The security argument depends on $a$ and $b$ being random, secret, fresh, and generated independently of $x,y$.

Reusing a triple destroys that masking argument. Triples are consumable one-time correlated randomness.

## 5. One round, many gates

If many independent multiplication gates are ready at the same circuit layer, parties can batch their $e,f$ openings.

This is why MPC performance depends heavily on **multiplicative depth**, not only total multiplication count.

Many products can be opened in one network round; dependent products require additional rounds.

## 6. The recovered toy and its limits

The archive contained code resembling:

```python
a, b, c = generate_mul_triple()
alpha = (x - a).reconstruct()
beta  = (y - b).reconstruct()
return alpha * beta + alpha * b + a * beta + c
```

The algebra is Beaver multiplication.

But several versions generated $a,b,c$ centrally **inside the multiplication method**. That is useful as a simulation but it hides the protocol boundary:

- the dealer sees the triple;
- no distributed preprocessing is implemented;
- no active-security checks authenticate the triple;
- `reconstruct()` is a local function, not a network opening protocol.

We retain the toy only with those assumptions explicit.

## 7. Additive and Shamir variants

The Beaver identity does not require one specific linear sharing scheme. What matters is that parties can:

- add/subtract shared values;
- multiply a share by a public scalar;
- open a shared value;
- obtain a correctly shared triple.

It can therefore sit on top of additive sharing, Shamir sharing, replicated sharing, and authenticated-sharing variants.

## 8. Malicious parties change the story

A malicious party can send a false opening share or use malformed correlated randomness.

So maliciously secure protocols add mechanisms such as:

- MAC-authenticated shares;
- VSS/commitments;
- sacrifice checks on triples;
- consistency checks;
- robust broadcast/abort rules.

SPDZ is important precisely because it turns the elegant Beaver-style online arithmetic into an actively secure protocol using authenticated secret sharing and secure preprocessing.

## 9. Takeaway

The Beaver trick is one of the most reusable equations in MPC:

$$
\boxed{xy=c+(x-a)b+(y-b)a+(x-a)(y-b).}
$$

The cryptography lies in making $a,b,c$ secret, correct, authenticated, fresh, and available before the online inputs arrive.
