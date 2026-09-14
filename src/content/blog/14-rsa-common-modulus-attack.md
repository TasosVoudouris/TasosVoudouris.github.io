---
title: 'RSA Deep Dive II: The Common-Modulus Attack'
description: If the same textbook RSA message is encrypted under one modulus with two coprime public exponents, Bézout coefficients can recover the plaintext without factoring the modulus.
pubDate: '2026-09-09'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Number Theory
tags:
- rsa
- common-modulus
- bezout
- extended-euclid
- cryptanalysis
- parameter-reuse
- cryptography-from-zero
difficulty: Intermediate
series: RSA Deep Dives
seriesOrder: 2
draft: false
---
This is exactly the kind of connection I wanted the Deep Dive series to make.

Back in Blog 02, we used the Extended Euclidean Algorithm to find numbers $a$ and $b$ such that:

$$
ax+by=\gcd(x,y).
$$

At the time, Bézout coefficients became useful because one of them could become a modular inverse.

Now the same identity is going to recover an RSA plaintext.

No factoring.

No private exponent.

No side channel.

Just two ciphertexts, one reused RSA modulus, and the equation:

$$
ae_1+be_2=1.
$$

If you want to refresh the prerequisites first:

- [Extended Euclid, Bézout, and modular inverses](/blog/02-extended-euclid-bezout-modular-inverse/)
- [RSA key generation from zero](/blog/12-rsa-key-generation/)
- [RSA Deep Dive I: Why textbook RSA fails](/blog/13-rsa-deep-dive-textbook-rsa-fails/)

![RSA common-modulus attack with Bézout coefficients](/images/blog/14-rsa-common-modulus.svg)

*Two textbook RSA encryptions of the same message share the same modulus. Coprime public exponents let Extended Euclid synthesize exponent $1$.*

---

## The dangerous setup

Suppose two RSA public keys reuse the same modulus:

$$
N=pq.
$$

But they use different public exponents:

$$
e_1
\qquad\text{and}\qquad
e_2.
$$

Now suppose the **same textbook message representative** $m$ is encrypted under both:

$$
c_1=m^{e_1}\bmod N,
$$

$$
c_2=m^{e_2}\bmod N.
$$

The attacker knows:

```text
N
e1
e2
c1
c2
```

because all of these are public or observable.

The attacker does **not** know:

```text
p
q
d1
d2
m
```

At first this still looks safe.

Each ciphertext separately is an RSA exponentiation.

But the pair contains a relation.

If:

$$
\gcd(e_1,e_2)=1,
$$

then Bézout tells us that there exist integers $a,b$ such that:

$$
ae_1+be_2=1.
$$

Now raise the two ciphertexts to those coefficients:

$$
c_1^a c_2^b
\equiv
(m^{e_1})^a(m^{e_2})^b
\pmod N.
$$

Combine the powers:

$$
c_1^a c_2^b
\equiv
m^{ae_1+be_2}
\pmod N.
$$

But:

$$
ae_1+be_2=1.
$$

Therefore:

$$
\boxed{
c_1^a c_2^b\equiv m\pmod N.
}
$$

That is the entire attack.

Extended Euclid has manufactured the exponent $1$ for us.

---

## A fully checked example from the old notes

Use:

$$
N=77.
$$

Let the plaintext representative be:

$$
m=9.
$$

Use two valid public exponents:

$$
e_1=7,
\qquad
e_2=11.
$$

The two textbook ciphertexts are:

$$
c_1=9^7\bmod77=37,
$$

and:

$$
c_2=9^{11}\bmod77=53.
$$

Now run Extended Euclid on the public exponents.

We obtain:

$$
8\cdot7-5\cdot11=1.
$$

So one convenient pair of Bézout coefficients is:

$$
a=8,
\qquad
b=-5.
$$

They are not unique. For example, Extended Euclid may just as naturally return:

$$
-3\cdot7+2\cdot11=1.
$$

Both pairs are correct. In general, once one solution $(a_0,b_0)$ is known, all solutions have the form:

$$
a=a_0+k e_2,
\qquad
b=b_0-k e_1.
$$

Starting from $(-3,2)$ and choosing $k=1$ gives:

$$
(-3+11,\;2-7)=(8,-5).
$$

I keep $(8,-5)$ here because it makes the negative-exponent step line up with the checked example from the older notes.

Substitute into the attack:

$$
m
\equiv
37^8\cdot53^{-5}
\pmod{77}.
$$

The only slightly unusual part is the negative exponent.

But we already know what that means.

A negative modular exponent means:

$$
53^{-5}
=
(53^{-1})^5
\pmod{77}.
$$

Compute the inverse:

$$
53^{-1}\equiv16\pmod{77},
$$

because:

$$
53\cdot16=848\equiv1\pmod{77}.
$$

So:

$$
37^8\bmod77=53,
$$

and:

$$
16^5\bmod77=67.
$$

Finally:

$$
53\cdot67\bmod77=9.
$$

Therefore:

$$
\boxed{m=9}.
$$

The plaintext is recovered.

We never computed:

$$
p
$$

or:

$$
q.
$$

We never recovered either private exponent.

The hidden factorization was simply irrelevant to this failure mode.

---

## Write the attack almost exactly like the proof

A useful helper is signed modular exponentiation:

```python
def pow_signed(base, exponent, modulus):
    if exponent >= 0:
        return pow(base, exponent, modulus)

    inverse = pow(base, -1, modulus)
    return pow(inverse, -exponent, modulus)
```

Then the attack is almost one line after Extended Euclid:

```python
a, b = bezout(e1, e2)

message = (
    pow_signed(c1, a, N)
    * pow_signed(c2, b, N)
) % N
```

For our example:

```text
a = 8
b = -5
recovered message = 9
```

This is one of the cleanest examples I know of mathematics mapping directly into cryptanalysis.

The proof says:

$$
ae_1+be_2=1.
$$

The implementation literally computes those coefficients and plugs them into the ciphertexts.

---

## Why the negative exponent condition matters

There is a technical condition hidden inside:

$$
c_2^{-5}.
$$

To compute:

$$
c_2^{-1}\pmod N,
$$

we need:

$$
\gcd(c_2,N)=1.
$$

In our example:

$$
\gcd(53,77)=1,
$$

so the inverse exists.

But there is an interesting RSA twist.

Suppose instead:

$$
\gcd(c_2,N)
$$

is neither $1$ nor $N$.

Then the attacker has already found a non-trivial factor of the RSA modulus.

So the "inverse does not exist" case can itself expose the factorization.

This is another recurring pattern in RSA:

> failure to invert modulo a composite integer is often not just an error—it may reveal secret factor structure.

For ordinary randomly encoded RSA representatives, being non-invertible is extremely unlikely for large balanced RSA primes, but the mathematical distinction is still worth understanding.

---

## What conditions does this attack actually need?

The simple Bézout recovery needs several things at once.

### Same modulus

Both ciphertexts must use:

$$
N.
$$

If:

$$
N_1\neq N_2,
$$

this derivation does not work.

### Same underlying representative

We need:

$$
c_1=m^{e_1}\bmod N
$$

and:

$$
c_2=m^{e_2}\bmod N
$$

for the same $m$.

If two randomized encryption encodings transform the same application message into two unrelated representatives:

$$
EM_1\neq EM_2,
$$

then the simple equation disappears.

This is another reason randomized encoding such as OAEP matters.

### Coprime public exponents

We used:

$$
\gcd(e_1,e_2)=1.
$$

If instead:

$$
\gcd(e_1,e_2)=g>1,
$$

Extended Euclid gives:

$$
ae_1+be_2=g,
$$

and the same manipulation recovers:

$$
m^g
$$

rather than automatically recovering $m$.

That may or may not be exploitable depending on the rest of the structure.

So the clean textbook attack is specifically the coprime-exponent case.

---

## A subtle correction: there are two "common modulus" disasters

While revisiting the old notes, I noticed that the phrase **common-modulus attack** often gets used for two related but distinct failures.

The one we just built is:

```text
same N
same textbook message
different coprime public exponents
        ↓
Bézout combination of ciphertexts
        ↓
recover m
```

This can be understood from public information alone.

But there is another, even more fundamental design failure.

Imagine a system where many users share one RSA modulus $N$, while each user receives a different valid public/private exponent pair:

$$
(e_i,d_i).
$$

A user who knows one valid private exponent for that shared modulus has enough information to attack the hidden factorization of $N$.

Once $N$ is factored, every user's RSA key built on that modulus is compromised.

Dan Boneh highlights this shared-modulus design as an elementary RSA misuse in his classic survey:

**Dan Boneh, "Twenty Years of Attacks on the RSA Cryptosystem," Notices of the AMS, 1999.**

[Read the survey from Stanford](https://crypto.stanford.edu/~dabo/abstracts/RSAattack-survey.html)

So there are really two lessons:

```text
do not reuse one RSA modulus as if it were a global DH parameter

and

do not send the same raw RSA representative under related common-modulus keys
```

RSA moduli belong to RSA keys.

They are not shared domain parameters.

---

## Mitigate: key isolation and randomized encoding

The structural mitigation is simple to state:

> independently generated RSA keys should have independently generated moduli.

Do not design:

```text
global N
user 1: e1,d1
user 2: e2,d2
user 3: e3,d3
```

as if $N$ were a reusable public system parameter.

Each independently generated RSA key pair should have its own hidden factorization.

And for encryption, we already learned the second protection in Deep Dive I:

```text
application message
        ↓
fresh randomized encoding
        ↓
RSA representative
        ↓
RSAEP
```

With OAEP, encrypting the same application message twice should produce different encoded representatives because of fresh randomness.

That breaks the exact:

$$
m^{e_1},
\qquad
m^{e_2}
$$

same-representative structure this toy attack requires.

But the strongest mental rule is broader:

> do not depend on one defense to compensate for a structurally bad key architecture.

Use independent keys **and** a secure standardized encryption scheme.

---

## Why I wanted this post immediately after the foundations

This attack makes the whole earlier route feel justified.

We started with:

$$
\gcd(a,b).
$$

Then:

$$
ax+by=\gcd(a,b).
$$

Then modular inverses.

Then RSA key generation.

And now:

$$
ae_1+be_2=1
$$

turns two ciphertexts into:

$$
m.
$$

So the progression is:

```text
Euclidean division
        ↓
GCD
        ↓
Extended Euclid
        ↓
Bézout coefficients
        ↓
modular inverse
        ↓
RSA
        ↓
common-modulus cryptanalysis
```

Nothing was filler.

The same algebra kept changing roles.

That is exactly the point of CryptoCave.

---

Run the companion demo:

```powershell
python chapters/14_rsa_common_modulus/demo.py
```

It prints:

```text
N  = 77
m  = 9

e1 = 7
c1 = 37

e2 = 11
c2 = 53

Bezout:
8*7 + (-5)*11 = 1

inverse of c2 mod N = 16

recovered message = 9
```

Then try changing the exponents.

Ask:

1. Are both valid RSA public exponents for this modulus?
2. Are they coprime to each other?
3. What Bézout coefficients do you get?
4. Which ciphertext needs an inverse?
5. What happens if that inverse does not exist?
6. What happens when $\gcd(e_1,e_2)>1$?

That last question is particularly useful because it forces us to distinguish:

```text
recover m
```

from:

```text
recover m^g.
```

---

Our RSA attack map now has another branch:

```text
RSA
├── raw primitive misuse
│   ├── determinism
│   └── multiplicative malleability
│
└── bad / reused parameters
    └── common modulus
        └── Bézout plaintext recovery
```

The next RSA failure looks similar at first—but uses a completely different tool.

Instead of:

```text
same modulus
different exponents
```

we will have:

```text
different coprime moduli
same small exponent
same plaintext
```

CRT will reconstruct the integer power before modular reduction.

And if that power is still small enough, an ordinary integer root recovers the message.

So Blog 10 comes back next.

**Next RSA Deep Dive:** *Håstad's Broadcast Attack: When CRT Reconstructs the Plaintext's Small Power.*
