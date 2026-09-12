---
title: "RSA Key Generation From Zero: Choosing p, q, e, and Building the Private Exponent"
description: "We finally assemble primes, GCDs, modular inverses, Carmichael's function, and CRT into a complete toy RSA key pair—and see why key generation itself is part of RSA security."
pubDate: "2026-09-08"
category: "Public-Key Cryptography"
tags:
  - rsa
  - key-generation
  - carmichael-function
  - modular-inverse
  - primes
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

We have reached a point where almost every ingredient needed for RSA is already on the table.

We know how to:

- test candidate primes,
- compute GCDs,
- construct modular inverses,
- work modulo composite integers,
- exponentiate efficiently,
- and reconstruct with CRT.

So instead of introducing RSA as:

```text
here is a formula
```

I want to build the key from the pieces we already understand.

That is much more satisfying to me, because RSA stops looking like a mysterious algorithm invented all at once.

It becomes a chain:

```text
prime generation
      ↓
p, q
      ↓
N = pq
      ↓
λ(N)
      ↓
choose e
      ↓
gcd(e, λ(N)) = 1
      ↓
modular inverse
      ↓
d = e⁻¹ mod λ(N)
```

And suddenly Blog 01, Blog 02, Blog 10, and Blog 11 are all inside one construction.

![RSA key generation from primes to public and private keys](/images/blog/12-rsa-keygen.svg)

*RSA key generation is a composition of number-theory operations we have already built individually.*

---

## Start with two secret primes

For a toy example, choose:

$$
p=61,
\qquad
q=53.
$$

They must be distinct.

Then the RSA modulus is:

$$
N=pq.
$$

So:

$$
N=61\cdot53=3233.
$$

This value becomes public.

The factorization:

$$
3233=61\cdot53
$$

must remain secret.

That is the trapdoor structure.

Anyone can see:

$$
N=3233.
$$

The private-key holder knows the hidden decomposition into $p$ and $q$.

For our tiny example, of course, factoring $3233$ is trivial.

The numbers are here only so that every step can be checked by hand.

---

Now we need the arithmetic cycle length that connects the public and private exponents.

For two distinct primes:

$$
\lambda(N)
=
\operatorname{lcm}(p-1,q-1).
$$

Here:

$$
p-1=60,
$$

and:

$$
q-1=52.
$$

Therefore:

$$
\lambda(3233)
=
\operatorname{lcm}(60,52)
=
780.
$$

This is Carmichael's function for our RSA modulus.

The public exponent $e$ must satisfy:

$$
\gcd(e,\lambda(N))=1.
$$

For the toy example choose:

$$
e=17.
$$

Check:

$$
\gcd(17,780)=1.
$$

That is exactly the condition from Blog 02.

Why do we care?

Because if $17$ is coprime to $780$, then it has a modular inverse modulo $780$.

And that inverse becomes the private exponent.

---

## The private key is an Extended-Euclid result

We want:

$$
ed\equiv1\pmod{\lambda(N)}.
$$

So:

$$
17d\equiv1\pmod{780}.
$$

The Extended Euclidean Algorithm gives:

$$
d=413.
$$

Check:

$$
17\cdot413
=
7021.
$$

And:

$$
7021
=
9\cdot780+1.
$$

Therefore:

$$
\boxed{
17\cdot413\equiv1\pmod{780}.
}
$$

So our keys are now:

$$
\boxed{
\text{public key }(N,e)=(3233,17)
}
$$

and conceptually:

$$
\boxed{
\text{private key }(N,d)=(3233,413).
}
$$

But a practical private RSA key normally stores more than only $d$.

Because we know the factors, we can also precompute:

$$
d_P=d\bmod(p-1),
$$

$$
d_Q=d\bmod(q-1),
$$

and:

$$
q_{\text{inv}}=q^{-1}\bmod p.
$$

These values support the CRT optimization from Blog 09.

So the hidden factorization is useful twice:

```text
p, q
  ↓
construct d

and later

p, q
  ↓
accelerate private operations with CRT
```

---

### A correction I want to preserve from my older notes

Many introductory RSA explanations use Euler's totient:

$$
\varphi(N)
=
(p-1)(q-1).
$$

For our example:

$$
\varphi(3233)
=
60\cdot52
=
3120.
$$

If we compute:

$$
17^{-1}\pmod{3120},
$$

we obtain:

$$
d=2753.
$$

This is the famous textbook value for the $61,53,17$ example.

And it works.

But:

$$
2753\equiv413\pmod{780}.
$$

So both private exponents satisfy the underlying RSA cycle relation.

The more precise PKCS #1 key definition uses:

$$
\boxed{
ed\equiv1\pmod{\lambda(N)}.
}
$$

That is why I prefer:

$$
d=413
$$

for the standards-facing version of this example.

This is a useful example of something I keep finding while revisiting old notes:

> the older explanation was not necessarily wrong; sometimes there is simply a cleaner or more precise formulation underneath it.

---

## Does the key actually work?

Take a toy message representative:

$$
m=65.
$$

The public RSA operation is:

$$
c=m^e\bmod N.
$$

So:

$$
c=65^{17}\bmod3233.
$$

This gives:

$$
\boxed{c=2790}.
$$

Now apply the private exponent:

$$
m'=2790^{413}\bmod3233.
$$

The result is:

$$
\boxed{m'=65}.
$$

So:

$$
m'=m.
$$

In Python:

```python
from math import gcd, lcm

p = 61
q = 53
e = 17

N = p * q
lambda_N = lcm(p - 1, q - 1)

assert gcd(e, lambda_N) == 1

d = pow(e, -1, lambda_N)

public_key = (N, e)
private_key = (N, d)

message = 65

ciphertext = pow(message, e, N)
recovered = pow(ciphertext, d, N)

print(public_key)   # (3233, 17)
print(private_key)  # (3233, 413)
print(ciphertext)   # 2790
print(recovered)    # 65

assert recovered == message
```

This is the first complete RSA key pair we have built from the arithmetic underneath it.

But there is an important warning.

This is still **textbook RSA arithmetic**.

The expression:

$$
c=m^e\bmod N
$$

is an RSA primitive.

It is **not yet a secure modern encryption scheme**.

No OAEP.

No encoding.

No randomized encryption layer.

No production key generation.

So the code belongs in our educational repository, not in a real application.

---

## Real key generation is much more than "pick two primes"

This is where key generation becomes a security topic rather than just setup.

In production, we do not write:

```python
p = 61
q = 53
```

We need unpredictable prime candidates generated from a cryptographically suitable random source.

Then we test them.

And the resulting primes must satisfy the parameter policy of the scheme or standard we are implementing.

For example, current RSA specifications impose constraints on:

- the number and sizes of the primes,
- distinctness of $p$ and $q$,
- the public exponent,
- the distance between the prime factors,
- the random-bit generator,
- private-exponent properties,
- and key validation.

For modern NIST RSA signature key generation, FIPS 186-5 requires two prime factors and an odd public exponent satisfying:

$$
2^{16}<e<2^{256}.
$$

The familiar choice:

$$
e=65537=2^{16}+1
$$

is therefore extremely common.

It is public.

It does not need to be random.

And choosing a much larger public exponent does not automatically make RSA "more secure."

The secret structure lives in the factorization and private exponent.

> **Standards connection.**  
> PKCS #1 v2.2 defines a valid RSA public key using distinct odd prime factors and
>
> $$
> \gcd(e,\lambda(N))=1,
> $$
>
> and defines the private exponent by
>
> $$
> ed\equiv1\pmod{\lambda(N)}.
> $$
>
> [RFC 8017 — PKCS #1 v2.2](https://www.rfc-editor.org/rfc/rfc8017)
>
> NIST FIPS 186-5 gives concrete RSA signature key-generation procedures, including approved randomness, probable-prime testing, exponent constraints, and separation conditions for $p$ and $q$.
>
> [NIST FIPS 186-5](https://doi.org/10.6028/NIST.FIPS.186-5)

There is another current detail worth recording: NIST SP 800-56B Rev. 2, which specifies RSA-based key-establishment schemes, was reaffirmed by NIST as current on January 6, 2026.

That does **not** make RSA post-quantum secure.

It only describes the current classical standardization status for those uses.

---

## BREAK: bad randomness can destroy RSA before encryption even begins

This is where Blog 01 comes back.

Imagine two RSA moduli:

$$
N_1=pq_1
$$

and:

$$
N_2=pq_2.
$$

If broken randomness accidentally causes both devices to reuse the same secret prime $p$, then:

$$
\gcd(N_1,N_2)=p.
$$

Both public keys are immediately factored.

No side channel.

No quantum computer.

No sophisticated number-field sieve.

Just:

```python
gcd(N1, N2)
```

That is why secure prime generation is part of RSA security.

Not housekeeping before the "real algorithm."

> **Research connection — key generation failed in the wild.**  
> Heninger, Durumeric, Wustrow, and Halderman's 2012 USENIX Security paper *Mining Your Ps and Qs* studied widespread weak RSA keys caused by insufficient entropy and found public moduli sharing nontrivial prime factors.
>
> [USENIX Security 2012 — Mining Your Ps and Qs](https://www.usenix.org/conference/usenixsecurity12/technical-sessions/presentation/heninger)

I like this connection because we encountered the GCD attack near the very beginning of the series.

Now we understand **where the repeated prime came from**:

the failure happened during key generation.

---

A more realistic educational pipeline for the repository should therefore look like:

```text
generate random odd candidate
        ↓
small-prime trial division
        ↓
Miller-Rabin
        ↓
candidate prime p

repeat for q
        ↓
check p != q
check key-generation constraints
        ↓
N = pq
λ(N) = lcm(p-1, q-1)
        ↓
choose fixed e
        ↓
check gcd(e, λ(N)) = 1
        ↓
d = e⁻¹ mod λ(N)
        ↓
derive CRT parameters
        ↓
validate the key pair
```

For the toy blog we deliberately skip most production constraints so every line remains visible.

But now we know what is missing.

That distinction matters.

---

At this point, RSA key generation no longer feels like:

```text
pick two primes and somehow get a key
```

It is a composition of ideas we already understand:

$$
\boxed{
\text{primes}
+
\text{GCD}
+
\text{LCM}
+
\text{modular inverse}
+
\text{CRT}
=
\text{RSA trapdoor structure}.
}
$$

And I think that is the right place to stop for this post.

Because the next temptation is immediate:

> We have a public key. Why not just encrypt a message with $m^e\bmod N$?

That works mathematically.

Cryptographically, it is a disaster.

The same message always gives the same ciphertext.

The algebra is multiplicative.

And an attacker can exploit both facts.

**Next:** *Why Textbook RSA Is Not Encryption: Determinism, Malleability, and the Need for OAEP.*
