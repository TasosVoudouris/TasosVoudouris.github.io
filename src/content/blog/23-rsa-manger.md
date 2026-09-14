---
title: 'RSA Deep Dive XI: Manger From Zero — How an OAEP Boundary Becomes a Numerical Oracle'
description: Manger's 2001 result shows how a decoding distinction that reveals whether an RSA plaintext representative is below a byte boundary can become an adaptive numerical oracle. We derive the three phases, reproduce the interval narrowing on a fixed toy model, and connect the result to modern OAEP error-handling requirements.
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Implementation Security
tags:
- rsa
- manger
- oaep
- padding-oracle
- chosen-ciphertext
- interval-arithmetic
- implementation-security
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 11
draft: false
---
The previous post studied Bleichenbacher's PKCS #1 v1.5 result.

There, a positive validity response implied that a transformed RSA plaintext lay inside:

$$
[2B,3B).
$$

Manger's 2001 result looks similar from far away:

```text
modify ciphertext
        ↓
receiver decrypts
        ↓
one small validity distinction leaks
        ↓
use it repeatedly
        ↓
narrow the hidden plaintext
```

But the numerical predicate is different.

For OAEP, the encoded message begins with a zero octet:

```text
EM = 0x00 || maskedSeed || maskedDB
```

If the RSA modulus occupies $k$ octets, define:

$$
\boxed{
B=2^{8(k-1)}.
}
$$

Then an encoded integer whose first octet is `0x00` satisfies:

$$
\boxed{
0\le m<B.
}
$$

Manger asks what happens if an implementation accidentally reveals whether the RSA-decrypted representative is below that boundary.

That tiny distinction is enough.

![Manger attack scientific pipeline: OAEP boundary to interval narrowing](/images/blog/23-rsa-manger.svg)

*The cryptanalytic object is not “OAEP is weak.” The object is a numerical oracle that leaks whether a transformed RSA plaintext is below one fixed boundary.*

Relevant prerequisites:

- [Textbook RSA and Malleability](/blog/13-rsa-deep-dive-textbook-rsa-fails/)
- [Bleichenbacher From Zero](/blog/22-rsa-bleichenbacher/)

---

## 1. The OAEP boundary

Current RSAES-OAEP represents the encoded message as:

```text
EM = Y || maskedSeed || maskedDB
```

with:

```text
Y = 0x00.
```

For a $k$-octet encoded message, all integers beginning with that zero byte satisfy:

$$
m<2^{8(k-1)}.
$$

Define:

$$
B=2^{8(k-1)}.
$$

Then every correctly formed OAEP representative satisfies the necessary condition:

$$
\boxed{
m<B.
}
$$

This is not the full OAEP validity condition.

OAEP also verifies the label hash and delimiter structure after unmasking.

But Manger's numerical insight needs only a distinction correlated with the leading-octet boundary.

So for this article define the idealized oracle:

$$
\mathcal O(c)=
\begin{cases}
0,&m<B,\\
1,&m\ge B,
\end{cases}
$$

where:

$$
m=c^d\bmod N.
$$

The labels `< B` and `>= B` are more useful here than “valid” and “invalid” because they describe exactly what information the mathematical model exposes.

---

## 2. RSA multiplicativity lets us move the hidden number

Suppose the target ciphertext is:

$$
c=m^e\bmod N.
$$

For a public multiplier $f$, construct:

$$
c_f
=
c\,f^e\bmod N.
$$

After RSA decryption:

$$
c_f^d
\equiv
mf
\pmod N.
$$

So the oracle answers the numerical question:

$$
\boxed{
mf\bmod N<B\;?
}
$$

The original plaintext is hidden.

But we can move it around the modular circle by choosing $f$.

That is the entire source of leverage.

The same RSA multiplicativity appeared in the textbook chosen-ciphertext example.

Here the receiver does not reveal the transformed plaintext.

It reveals only which side of one boundary the transformed value lands on.

---

## 3. Why the condition $2B<N$ is convenient

Manger's main presentation assumes:

$$
\boxed{
2B<N.
}
$$

For an RSA modulus with an exact byte-aligned bit length, this is normally true by a large margin.

Why is it useful?

If:

$$
0\le m<B
$$

and we multiply by $2$, then:

$$
0\le2m<2B<N.
$$

So before the first modular wrap occurs, asking whether:

$$
2m<B
$$

really tells us which half of:

$$
[0,B)
$$

contains $m$.

The first phase therefore behaves almost like locating the most significant non-zero bit of $m$.

If $N<2B$, modular wrap can occur earlier and the interval bookkeeping becomes more complicated.

The original paper discusses that case separately.

For our scientific model we remain in the clean:

$$
2B<N
$$

regime.

---

## 4. Phase 1 — find the scale of $m$

Initially:

$$
m\in[0,B).
$$

Set:

$$
f_1=2.
$$

Query whether:

$$
f_1m\bmod N<B.
$$

As long as the answer is `< B`, double:

$$
f_1\leftarrow2f_1.
$$

Eventually the oracle returns:

$$
\ge B.
$$

Because no modular wrap has occurred in this phase, that first negative boundary response tells us:

$$
B
\le
f_1m
<
2B.
$$

Equivalently:

$$
\frac B2
\le
\frac{f_1}{2}m
<
B.
$$

So if:

$$
f_{\text{half}}=\frac{f_1}{2},
$$

then we know:

$$
\boxed{
\frac B2
\le
f_{\text{half}}m
<
B.
}
$$

That places $m$ within a factor-of-two scale.

### Toy value

Use:

$$
N=3\,662\,413\,351.
$$

Since $N$ is four octets:

$$
k=4.
$$

Therefore:

$$
B=2^{24}=16\,777\,216.
$$

Choose the hidden toy representative:

$$
m=12\,345\,678.
$$

It satisfies:

$$
m<B.
$$

Try:

$$
f_1=2.
$$

Then:

$$
2m=24\,691\,356.
$$

So:

$$
2m\ge B.
$$

The very first query crosses the boundary.

Hence:

$$
f_{\text{half}}=1,
$$

and we learn:

$$
\frac B2
\le
m
<
B.
$$

Numerically:

$$
8\,388\,608
\le
m
<
16\,777\,216.
$$

The original OAEP-style condition gave an interval of width about $B$.

Phase 1 has already located the hidden number in its upper half.

---

## 5. Phase 2 — force exactly one modular wrap

Now we know:

$$
f_{\text{half}}m
\in
[B/2,B).
$$

The goal of phase 2 is different.

We want a multiplier $f_2$ for which:

$$
f_2m
$$

has just crossed $N$, while the reduced value remains below $B$.

In other words:

$$
\boxed{
N\le f_2m<N+B.
}
$$

Then:

$$
f_2m\bmod N
=
f_2m-N
<
B.
$$

Manger starts from:

$$
f_2
=
\left\lfloor
\frac{N+B}{B}
\right\rfloor
f_{\text{half}}
$$

and increases it in steps of:

$$
f_{\text{half}}
$$

until the oracle returns `< B`.

For our toy case:

$$
f_{\text{half}}=1.
$$

Also:

$$
\left\lfloor
\frac{N+B}{B}
\right\rfloor
=
219.
$$

So phase 2 starts at:

$$
f_2=219.
$$

For:

$$
f_2=219,220,\ldots,296,
$$

the reduced values remain:

$$
\ge B.
$$

At:

$$
\boxed{
f_2=297,
}
$$

we obtain:

$$
297m
=
3\,666\,666\,366.
$$

Subtract one modulus:

$$
297m-N
=
4\,253\,015.
$$

And:

$$
4\,253\,015<B.
$$

So the `< B` response proves:

$$
N\le297m<N+B.
$$

Therefore:

$$
\boxed{
\left\lceil\frac N{297}\right\rceil
\le
m
\le
\left\lfloor\frac{N+B-1}{297}\right\rfloor.
}
$$

Numerically:

$$
\boxed{
12\,331\,359
\le
m
\le
12\,387\,847.
}
$$

The interval width is now only about:

$$
56\,489
$$

integers.

---

## 6. Phase 3 — place one boundary inside the current interval

Now suppose we know:

$$
m\in[m_{\min},m_{\max}].
$$

Phase 3 chooses a multiplier so that the image:

$$
f_3[m_{\min},m_{\max}]
$$

has width about:

$$
2B
$$

and crosses exactly one boundary of the form:

$$
iN+B.
$$

Then one oracle bit chooses approximately one half of the current interval.

A convenient construction from Manger's presentation is:

$$
f_{\text{tmp}}
=
\left\lfloor
\frac{2B}{m_{\max}-m_{\min}}
\right\rfloor.
$$

Choose the nearby wrap index:

$$
i
=
\left\lfloor
\frac{f_{\text{tmp}}m_{\min}}{N}
\right\rfloor.
$$

Then choose:

$$
\boxed{
f_3
=
\left\lceil
\frac{iN}{m_{\min}}
\right\rceil.
}
$$

The transformed interval is arranged to straddle:

$$
iN+B.
$$

Now there are two cases.

### Oracle says `< B`

Then the transformed true value lies in:

$$
[iN,iN+B).
$$

So update the upper bound:

$$
\boxed{
m_{\max}
\leftarrow
\left\lfloor
\frac{iN+B-1}{f_3}
\right\rfloor.
}
$$

### Oracle says `>= B`

Then the true value lies in:

$$
[iN+B,iN+2B).
$$

So update the lower bound:

$$
\boxed{
m_{\min}
\leftarrow
\left\lceil
\frac{iN+B}{f_3}
\right\rceil.
}
$$

Unlike the simplified Bleichenbacher interval experiment from the previous post, **both oracle responses are immediately useful**.

Each tells us which side of the boundary contains the hidden value.

---

## 7. Run phase 3 on the fixed toy model

After phase 2:

$$
m\in
[12\,331\,359,\,
12\,387\,847].
$$

The first phase-3 construction gives:

$$
f_3=594,
$$

with:

$$
i=2.
$$

For the true hidden value:

$$
594m\bmod N
=
8\,506\,030.
$$

Since:

$$
8\,506\,030<B,
$$

the response is `< B`.

The upper half is removed and the interval becomes:

$$
[12\,331\,359,\,
12\,359\,602].
$$

The next selected multiplier is:

$$
f_3=1188.
$$

Now:

$$
1188m\bmod N
=
17\,012\,060.
$$

That is:

$$
\ge B.
$$

So this time the lower portion is removed:

$$
[12\,345\,481,\,
12\,359\,602].
$$

Continue the same procedure.

For this fixed toy model, phase 3 takes fifteen such interval updates before reaching:

$$
\boxed{
[12\,345\,678,\,
12\,345\,678].
}
$$

The hidden representative has become the only surviving integer.

The companion script prints every interval so the narrowing can be inspected rather than hidden.

---

## 8. The whole toy trace

The key phase-3 interval evolution is:

```text
[12331359, 12387847]
        ↓ f=594, oracle < B
[12331359, 12359602]
        ↓ f=1188, oracle >= B
[12345481, 12359602]
        ↓ f=2374, oracle < B
[12345481, 12348813]
        ↓
...
        ↓
[12345678, 12345679]
        ↓
[12345678, 12345678]
```

The multipliers grow while the plaintext interval shrinks.

Geometrically, each query rescales the current interval until one known boundary lies inside its image.

Then the one-bit oracle tells us which side contains the hidden point.

That is much closer to a modular binary search than the sparse “wait for another valid block” intuition associated with PKCS #1 v1.5.

---

## 9. Why Manger could be much more query-efficient

The original paper observes that phases 1 and 3 roughly halve the uncertainty repeatedly.

Their combined query count is therefore on the order of:

$$
\log_2 B.
$$

Phase 2 adds a comparatively small search.

For the byte-aligned RSA moduli considered in the paper, the phase-2 search is bounded by roughly:

$$
\left\lceil\frac NB\right\rceil
\le256
$$

queries.

Manger reported approximate totals of:

- about 1100 oracle queries for a 1024-bit RSA key;
- about 2200 for a 2048-bit RSA key.

Those are historical analytical figures from the 2001 paper, not measurements of modern implementations.

The important reason for the efficiency is structural:

> the Manger predicate divides a broad numerical range at a simple boundary, and both sides of the answer carry information.

---

## 10. Why this does not mean “OAEP is broken”

This distinction is essential.

RSAES-OAEP is a cryptographic encoding scheme with formal security results in the appropriate model.

Manger's result does not say:

```text
OAEP mathematics is useless
```

or:

```text
OAEP ciphertexts can simply be decrypted algebraically
```

It says that an **implementation exposing partial information about the encoded message during decryption** can create a chosen-ciphertext oracle.

Current RFC 8017 is explicit about this.

OAEP decryption returns one generic:

```text
decryption error
```

and its implementation note warns that an opponent must not be able to distinguish internal decoding failures through error messages, timing, or other partial information about the encoded message.

The RFC cites Manger directly in that warning.

So the correct lesson is:

$$
\boxed{
\text{secure scheme}
+
\text{leaky decoder behavior}
\not\Rightarrow
\text{secure implementation}.
}
$$

That is an implementation-security theorem lesson, not an indictment of the abstract encoding alone.

---

## 11. Bleichenbacher versus Manger

These two results belong beside each other, but their predicates are different.

| Property | Bleichenbacher model | Manger model |
|---|---|---|
| Encoding context | PKCS #1 v1.5 | OAEP implementation boundary |
| Numerical region | $[2B,3B)$ | $[0,B)$ |
| Oracle meaning | conformance-style positive response | below/above byte boundary |
| RSA transformation | multiply ciphertext by $s^e$ | multiply ciphertext by $f^e$ |
| Interval structure | may become several intervals | clean presentation keeps one main interval |
| Useful responses | positive responses drive narrowing | both responses can narrow |
| Core arithmetic | wrap integer + interval intersection | boundary placement + interval halving |

The common principle is:

```text
RSA multiplicativity
+
observable decoding predicate
+
adaptive chosen transformations
=
plaintext information
```

The exact predicate determines the geometry.

---

## 12. What I want to remember

For a $k$-octet RSA representative define:

$$
B=2^{8(k-1)}.
$$

OAEP's leading zero octet gives the necessary condition:

$$
m<B.
$$

A leaky implementation supplies:

$$
\mathcal O(c_f)
=
[mf\bmod N<B].
$$

Manger organizes the information in three stages.

### Phase 1

Double:

$$
f_1=2,4,8,\ldots
$$

until the boundary is crossed.

This locates the scale of $m$.

### Phase 2

Find:

$$
f_2
$$

such that:

$$
N\le f_2m<N+B.
$$

This gives a narrow initial interval:

$$
\frac N{f_2}
\lesssim
m
<
\frac{N+B}{f_2}.
$$

### Phase 3

Choose $f_3$ so the current interval crosses one boundary:

$$
iN+B.
$$

Then:

```text
oracle < B
    -> keep lower transformed half

oracle >= B
    -> keep upper transformed half
```

Repeat until one integer remains.

So the scientific mental model is:

```text
leading-zero boundary
        ↓
numerical predicate m < B
        ↓
RSA multiplicative transformations
        ↓
move interval across chosen boundary
        ↓
one bit selects a side
        ↓
repeat
```

That is Manger's central idea.

---

## References

1. James Manger, **“A Chosen Ciphertext Attack on RSA Optimal Asymmetric Encryption Padding (OAEP) as Standardized in PKCS #1 v2.0”**, *CRYPTO 2001*, LNCS 2139, pp. 230–238, 2001.  
   https://doi.org/10.1007/3-540-44647-8_14

2. K. Moriarty, B. Kaliski, J. Jonsson, A. Rusch, **“PKCS #1: RSA Cryptography Specifications Version 2.2”**, RFC 8017, November 2016.  
   https://www.rfc-editor.org/rfc/rfc8017

3. Eiichiro Fujisaki, Tatsuaki Okamoto, David Pointcheval, Jacques Stern, **“RSA-OAEP Is Secure under the RSA Assumption”**, *CRYPTO 2001*, LNCS 2139, pp. 260–274, 2001.  
   https://doi.org/10.1007/3-540-44647-8_16

---

With Manger, the RSA oracle branch is essentially complete:

```text
PKCS #1 v1.5 validity distinction
        -> Bleichenbacher

OAEP boundary / decoding distinction
        -> Manger
```

The remaining major RSA deep-dive branch is no longer message algebra or oracle behavior.

It is **key generation structure**.

A modulus can have the right bit length, pass ordinary RSA arithmetic checks, and still come from a dangerously restricted prime-generation family.

That leads naturally to:

**Next RSA Deep Dive:** *ROCA From Zero — When Prime Generation Leaves a Detectable Algebraic Fingerprint.*
