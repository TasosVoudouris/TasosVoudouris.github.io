---
title: 'RSA Deep Dive X: Bleichenbacher From Zero — From a Validity Predicate to Adaptive Interval Narrowing'
description: 'Bleichenbacher''s 1998 result showed that a one-bit RSA decryption validity signal can become a powerful adaptive oracle. We derive the PKCS #1 v1.5 interval, combine it with RSA multiplicativity, and show how each positive predicate response narrows the possible plaintext interval.'
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Implementation Security
tags:
- rsa
- bleichenbacher
- pkcs1-v1-5
- padding-oracle
- chosen-ciphertext
- interval-arithmetic
- cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 10
draft: false
---
The previous RSA deep dives were mostly algebraic.

We exploited:

- repeated messages,
- related messages,
- small roots,
- polynomial relations,
- special parameter regimes.

This post changes the model.

The ciphertext itself does not expose a useful polynomial relation.

Instead, imagine that after decrypting a modified ciphertext, a receiver reveals only one tiny fact:

```text
valid encoding
```

or:

```text
invalid encoding
```

That looks like almost no information.

Bleichenbacher's 1998 result showed that under the right RSA encoding and oracle model, this single predicate can be queried adaptively until the possible plaintext range collapses.

The core scientific transition is:

```text
one validity bit
        ↓
one modular interval constraint
        ↓
intersect with previous constraints
        ↓
smaller candidate set
        ↓
repeat adaptively
```

![Bleichenbacher validity predicate to interval narrowing](/images/blog/22-rsa-bleichenbacher.svg)

*The oracle never needs to reveal the plaintext. A positive answer tells us that a transformed plaintext lies inside a narrow numerical interval.*

Relevant prerequisites:

- [Modular Arithmetic From Zero](/blog/03-modular-arithmetic-units-zero-divisors/)
- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Textbook RSA and Malleability](/blog/13-rsa-deep-dive-textbook-rsa-fails/)
- [Franklin–Reiter From Zero](/blog/20-rsa-franklin-reiter/)

---

## 1. The PKCS #1 v1.5 encoding interval

For RSAES-PKCS1-v1_5, RFC 8017 encodes a message as:

```text
EM = 0x00 || 0x02 || PS || 0x00 || M
```

where:

- `PS` consists of non-zero octets;
- `PS` has length at least eight octets;
- the total encoded message has exactly $k$ octets, where $k$ is the RSA modulus length in octets.

Now define:

$$
B=2^{8(k-2)}.
$$

Any encoded integer beginning with:

```text
0x00 0x02
```

must lie in the interval:

$$
\boxed{
2B\le m<3B.
}
$$

Why?

Because:

$$
2B
$$

is the integer whose leading bytes are:

```text
0x00 0x02 0x00 ... 0x00
```

while:

$$
3B
$$

starts at:

```text
0x00 0x03 0x00 ... 0x00.
```

So every integer beginning with `0x00 0x02` lies numerically between them.

This interval is the arithmetic entry point.

The full PKCS #1 v1.5 validity condition checks more than those first two octets.

But for understanding the interval mathematics, the prefix condition gives the essential numerical constraint:

$$
m\in[2B,3B-1].
$$

---

## 2. The oracle as a mathematical predicate

Define an idealized predicate:

$$
\mathcal O(c)
=
\begin{cases}
1,&\text{if the RSA decryption of }c\text{ lies in }[2B,3B-1],\\
0,&\text{otherwise.}
\end{cases}
$$

This is deliberately simpler than a complete PKCS #1 v1.5 decoder.

Its purpose is to isolate the mathematical mechanism.

The important point is that:

$$
\mathcal O(c)=1
$$

does **not** reveal the plaintext.

It reveals only membership in an interval.

That is one bit of information.

But because RSA is multiplicative, we can ask that question about controlled multiplicative transformations of the unknown plaintext.

That is what makes the oracle useful.

---

## 3. RSA multiplicativity gives controlled transformations

Let:

$$
c\equiv m^e\pmod N.
$$

Choose an integer multiplier:

$$
s.
$$

Construct:

$$
c'
\equiv
c\cdot s^e
\pmod N.
$$

Then:

$$
c'
\equiv
m^e s^e
\equiv
(ms)^e
\pmod N.
$$

So RSA decryption of $c'$ produces:

$$
m'
\equiv
ms
\pmod N.
$$

This is the same multiplicative structure we already studied in the textbook RSA malleability post.

But now we do not ask for $m'$.

We ask only whether:

$$
m'\in[2B,3B-1].
$$

A positive answer tells us:

$$
2B
\le
ms\bmod N
\le
3B-1.
$$

The modular reduction means that for some integer $r$:

$$
\boxed{
2B
\le
ms-rN
\le
3B-1.
}
$$

This is the fundamental Bleichenbacher inequality.

Everything that follows is interval arithmetic.

---

## 4. Turn one positive response into a bound on $m$

Starting from:

$$
2B
\le
ms-rN
\le
3B-1,
$$

add $rN$:

$$
2B+rN
\le
ms
\le
3B-1+rN.
$$

Divide by positive $s$:

$$
\frac{2B+rN}{s}
\le
m
\le
\frac{3B-1+rN}{s}.
$$

Because $m$ is an integer:

$$
\boxed{
\left\lceil
\frac{2B+rN}{s}
\right\rceil
\le
m
\le
\left\lfloor
\frac{3B-1+rN}{s}
\right\rfloor.
}
$$

So one positive oracle response creates one or more candidate intervals, depending on which integer values of $r$ are possible.

The current interval for $m$ is intersected with all compatible intervals.

That is the narrowing step.

---

## 5. How do we know which $r$ values are possible?

Suppose before the new oracle response we already know:

$$
m\in[a,b].
$$

If the transformed value is valid, then:

$$
2B
\le
ms-rN
\le
3B-1.
$$

Because:

$$
a\le m\le b,
$$

the possible $r$ values must satisfy:

$$
as-(3B-1)
\le
rN
\le
bs-2B.
$$

Therefore:

$$
\boxed{
\left\lceil
\frac{as-(3B-1)}{N}
\right\rceil
\le
r
\le
\left\lfloor
\frac{bs-2B}{N}
\right\rfloor.
}
$$

This is important.

The algorithm does not guess arbitrary wrap counts.

The current plaintext interval restricts which modular wraps are possible.

For each admissible $r$, we form:

$$
\left[
\left\lceil\frac{2B+rN}{s}\right\rceil,
\left\lfloor\frac{3B-1+rN}{s}\right\rfloor
\right]
$$

and intersect it with:

$$
[a,b].
$$

The result becomes the next candidate set.

---

## 6. A small fixed model

Use the fixed RSA modulus:

$$
p=60\,013,
$$

$$
q=61\,027,
$$

so:

$$
N=pq
=
3\,662\,413\,351.
$$

This modulus is four octets long.

Therefore:

$$
k=4,
$$

and:

$$
B=2^{8(4-2)}
=
2^{16}
=
65\,536.
$$

The simplified valid-prefix interval is:

$$
2B
=
131\,072
$$

through:

$$
3B-1
=
196\,607.
$$

Choose a fixed educational representative:

$$
m=150\,000.
$$

It lies inside the interval:

$$
131\,072
\le
150\,000
\le
196\,607.
$$

Choose:

$$
e=17.
$$

The corresponding toy ciphertext is:

$$
c
=
150\,000^{17}\bmod N
=
151\,296\,758.
$$

The following calculations use only this fixed toy model.

No network protocol is involved.

---

## 7. First positive transformed predicate

Take the fixed multiplier:

$$
s_1=24\,417.
$$

The transformed plaintext representative is:

$$
m s_1\bmod N
=
136\,649.
$$

This lies in the valid interval:

$$
131\,072
\le
136\,649
\le
196\,607.
$$

So our idealized predicate returns:

$$
\mathcal O(c_1')=1.
$$

In ordinary integer arithmetic:

$$
m s_1
=
150\,000\cdot24\,417
=
3\,662\,550\,000.
$$

Since:

$$
N=3\,662\,413\,351,
$$

we have:

$$
m s_1-N
=
136\,649.
$$

So here:

$$
r=1.
$$

Now apply the interval formula:

$$
\left\lceil
\frac{2B+N}{24\,417}
\right\rceil
\le
m
\le
\left\lfloor
\frac{3B-1+N}{24\,417}
\right\rfloor.
$$

This gives:

$$
\boxed{
150\,000
\le
m
\le
150\,002.
}
$$

One positive response has reduced the candidate set from:

$$
65\,536
$$

possible integers to only:

$$
3.
$$

This dramatic reduction happens because the toy parameters are intentionally tiny.

In a real cryptographic-size analysis the interval evolution is much larger and the original paper studies an adaptive sequence of many oracle queries.

The arithmetic mechanism, however, is the same.

---

## 8. A second positive predicate collapses the toy interval

Now the candidate interval is:

$$
m\in[150\,000,150\,002].
$$

Take another fixed multiplier:

$$
s_2=195\,330.
$$

For the true hidden value:

$$
150\,000\cdot195\,330
=
29\,299\,500\,000.
$$

Subtract eight copies of $N$:

$$
29\,299\,500\,000
-
8(3\,662\,413\,351)
=
193\,192.
$$

So:

$$
r=8
$$

and:

$$
m s_2\bmod N
=
193\,192.
$$

Again:

$$
131\,072
\le
193\,192
\le
196\,607.
$$

The predicate is positive.

Now intersect:

$$
[150\,000,150\,002]
$$

with the interval implied by:

$$
s_2=195\,330,
\qquad
r=8.
$$

The only surviving integer is:

$$
\boxed{
m=150\,000.
}
$$

So our fixed toy progression is:

```text
initial information
[131072, 196607]
65536 candidates

        ↓ positive predicate for s1 = 24417

[150000, 150002]
3 candidates

        ↓ positive predicate for s2 = 195330

[150000, 150000]
1 candidate
```

That is adaptive interval narrowing in its simplest visible form.

---

## 9. What “adaptive” means

The word **adaptive** is important.

It means that the next query can depend on the information learned from previous responses.

Mathematically:

```text
current candidate interval
        ↓
choose next multiplier
        ↓
query validity predicate
        ↓
update interval
        ↓
choose next multiplier using the new interval
```

The original Bleichenbacher algorithm contains carefully designed search phases for the multiplier $s$ and interval set.

Our toy model does not reproduce those operational search procedures.

Instead, it fixes two known-positive multipliers and checks the interval mathematics directly.

That is enough for the scientific point of this post:

> a validity predicate can be converted into exact inequalities on an otherwise hidden RSA plaintext representative.

---

## 10. Why one bit becomes powerful

A single predicate response seems tiny:

$$
\mathcal O(c')\in\{0,1\}.
$$

But the query is not passive.

We control the multiplier $s$.

So each query asks a different mathematical question:

$$
\text{Does }ms\bmod N
\text{ lie in }[2B,3B)?
$$

The combination of:

1. controlled transformation;
2. modular wrap structure;
3. a narrow validity interval;
4. adaptive repetition;

turns binary responses into progressively tighter inequalities.

This is an important general cryptographic lesson.

The amount of information in one response is not the whole story.

What matters is whether the adversary can choose **which predicate is evaluated next**.

---

## 11. Full PKCS #1 v1.5 validity is richer than the toy predicate

The real RSAES-PKCS1-v1_5 encoding is:

```text
0x00 || 0x02 || PS || 0x00 || M
```

with structural requirements on `PS` and the separator.

Therefore a real conforming/non-conforming response contains information about more than the two-byte prefix.

The original Bleichenbacher setting exploits a conformance oracle for the encoding.

For the interval derivation, however, every conforming block necessarily satisfies:

$$
2B\le m<3B.
$$

That is why the interval is useful even though it captures only part of the full encoding structure.

Our companion script intentionally models only:

$$
\boxed{
2B\le m'<3B
}
$$

as the predicate.

This keeps the mathematics transparent without pretending to implement an actual PKCS #1 decoder.

---

## 12. The security lesson is about error behavior

The underlying RSA exponentiation has not changed.

The receiver still computes the mathematically correct private operation.

The weakness comes from observable behavior after decryption.

If one class of decoded plaintexts causes one externally distinguishable behavior and another class causes a different one, that distinction may become an oracle.

This matches the broader principle already present in the mature CryptoBible RSA notes:

$$
\boxed{
\text{decryption errors are part of the attack surface}.
}
$$

RFC 8017 explicitly warns implementers to avoid error distinctions that let an opponent distinguish different RSAES-PKCS1-v1_5 decoding failures.

The engineering requirement is therefore not merely:

```text
check the encoding correctly
```

but also:

```text
do not reveal which internal validity condition failed
```

through:

- different messages,
- different protocol states,
- timing differences,
- other observable behavior.

---

## 13. Bleichenbacher versus the RSA attacks we already studied

It is useful to place this result beside the previous deep dives.

### Håstad

Exploits:

$$
\text{same low-degree message across several moduli}.
$$

Tool:

$$
\text{CRT}.
$$

### Franklin–Reiter

Exploits:

$$
\text{known algebraic relation between messages}.
$$

Tool:

$$
\text{polynomial GCD}.
$$

### Coppersmith

Exploits:

$$
\text{small modular root}.
$$

Tool:

$$
\text{lattice reduction}.
$$

### Bleichenbacher

Exploits:

$$
\text{adaptive validity information after decryption}.
$$

Tools:

$$
\text{RSA multiplicativity + modular interval arithmetic}.
$$

That is a different cryptanalytic layer.

The weakness is not primarily in the RSA parameters or plaintext algebra.

It is in the interface between:

$$
\text{decryption}
$$

and:

$$
\text{observable protocol behavior}.
$$

---

## 14. What I want to remember

For a $k$-octet RSA modulus define:

$$
B=2^{8(k-2)}.
$$

A PKCS #1 v1.5 block beginning with:

```text
00 02
```

lies in:

$$
2B\le m<3B.
$$

RSA multiplicativity gives:

$$
c'
=
c s^e
\bmod N
$$

and therefore:

$$
m'
=
ms
\bmod N.
$$

A positive validity predicate implies that for some integer $r$:

$$
2B
\le
ms-rN
\le
3B-1.
$$

Hence:

$$
\boxed{
\left\lceil
\frac{2B+rN}{s}
\right\rceil
\le
m
\le
\left\lfloor
\frac{3B-1+rN}{s}
\right\rfloor.
}
$$

Intersect that interval with the current candidate set.

Repeat adaptively.

The whole mental model is:

```text
validity predicate
        ↓
known numerical interval
        ↓
controlled RSA multiplier
        ↓
modular wrap integer r
        ↓
new plaintext interval
        ↓
intersection
        ↓
repeat
```

That is the mathematical heart of Bleichenbacher's result.

---

## References

1. Daniel Bleichenbacher, **“Chosen Ciphertext Attacks Against Protocols Based on the RSA Encryption Standard PKCS #1”**, *CRYPTO '98*, LNCS 1462, pp. 1–12, 1998.  
   https://doi.org/10.1007/BFb0055716

2. K. Moriarty, B. Kaliski, J. Jonsson, A. Rusch, **“PKCS #1: RSA Cryptography Specifications Version 2.2”**, RFC 8017, November 2016.  
   https://www.rfc-editor.org/rfc/rfc8017

3. James Manger, **“A Chosen Ciphertext Attack on RSA Optimal Asymmetric Encryption Padding (OAEP) as Standardized in PKCS #1 v2.0”**, *CRYPTO 2001*, LNCS 2139, pp. 230–238, 2001.  
   https://doi.org/10.1007/3-540-44647-8_14

---

Bleichenbacher gives us a new way to think about RSA security:

```text
the primitive may be mathematically correct
        +
the encoding may contain redundancy
        +
the implementation may reveal one validity distinction
        =
adaptive information channel
```

The natural next step is Manger's result.

There the encoding is OAEP rather than PKCS #1 v1.5, and the useful predicate changes.

The deeper question remains the same:

> what exact numerical information does one decoding distinction reveal?

**Next RSA Deep Dive:** *Manger From Zero — How an OAEP Validity Boundary Becomes a Numerical Oracle.*
