---
title: "RSA Key Generation From Zero: Choosing p, q, e, and Building the Private Exponent"
description: "We assemble primes, GCDs, modular inverses, Carmichael's function, and CRT into a complete toy RSA key pair—and see why secure key generation is part of RSA security."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Public-Key Cryptography"
  - "Cryptographic Engineering"
tags:
  - "rsa"
  - "key-generation"
  - "carmichael-function"
  - "modular-inverse"
  - "primes"
  - "cryptography-from-zero"
difficulty: "Introductory"
series: "Cryptography From Zero"
seriesOrder: 13
draft: false
---

We have reached a point where almost every ingredient needed to construct an RSA key is already on the table.

We know how to:

- generate and test candidate primes,
- compute GCDs,
- compute modular inverses,
- work modulo composite integers,
- perform fast modular exponentiation,
- and reconstruct values with the Chinese Remainder Theorem.

So rather than introducing RSA as a mysterious collection of formulas, we can now build it from pieces we already understand.

The construction is essentially:

```text
generate secret primes
        ↓
       p, q
        ↓
      N = pq
        ↓
λ(N) = lcm(p - 1, q - 1)
        ↓
choose public exponent e
        ↓
gcd(e, λ(N)) = 1
        ↓
compute modular inverse
        ↓
d = e⁻¹ mod λ(N)
        ↓
derive CRT parameters
```

The same number theory that looked elementary several articles ago is now becoming a complete public-key construction.

![RSA key generation from primes to public and private keys](/images/blog/12-rsa-keygen.svg)

*RSA key generation is a composition of number-theoretic operations that we have already studied individually.*

---

## Table of Contents

- [Start with two secret primes](#start-with-two-secret-primes)
- [From the primes to the public and private exponents](#from-the-primes-to-the-public-and-private-exponents)
- [Euler’s totient versus Carmichael’s function](#eulers-totient-versus-carmichaels-function)
- [Does the key actually work?](#does-the-key-actually-work)
- [Practical RSA keys and CRT parameters](#practical-rsa-keys-and-crt-parameters)
- [Real key generation is a security problem](#real-key-generation-is-a-security-problem)
- [Standards perspective](#standards-perspective)
- [When randomness fails: shared-prime RSA keys](#when-randomness-fails-shared-prime-rsa-keys)
- [A complete educational pipeline](#a-complete-educational-pipeline)
- [Reader checkpoint](#reader-checkpoint)
- [Next](#next)
- [Closing Cryptography From Zero](#closing-cryptography-from-zero)

---

## Start with two secret primes

For our toy example, choose two distinct primes:

\[
p=61,
\qquad
q=53.
\]

The RSA modulus is

\[
N=pq.
\]

Therefore,

\[
N=61\cdot53=3233.
\]

The modulus

\[
N=3233
\]

becomes public.

Its factorization

\[
3233=61\cdot53
\]

must remain secret.

For this tiny example, factoring \(3233\) is easy. We use small numbers only so that every step can be checked manually.

In a real RSA key, \(N\) is large enough that recovering its prime factors is intended to be computationally infeasible for a classical attacker.

Knowledge of the factorization gives the private-key holder information that is unavailable from the public modulus alone.

That hidden factorization will allow us to construct the private exponent.

---

## From the primes to the public and private exponents

For an RSA modulus composed of two distinct primes,

\[
N=pq,
\]

Carmichael's function is

\[
\lambda(N)
=
\operatorname{lcm}(p-1,q-1).
\]

For our example,

\[
p-1=60
\]

and

\[
q-1=52.
\]

Therefore,

\[
\lambda(3233)
=
\operatorname{lcm}(60,52)
=
780.
\]

Now choose the public exponent \(e\).

It must satisfy

\[
\gcd(e,\lambda(N))=1.
\]

For our toy example, choose

\[
e=17.
\]

Indeed,

\[
\gcd(17,780)=1.
\]

Why is this condition important?

Because it guarantees that \(e\) has a multiplicative inverse modulo \(\lambda(N)\).

That inverse becomes the private exponent \(d\).

We require

\[
ed\equiv1\pmod{\lambda(N)}.
\]

So in our example,

\[
17d\equiv1\pmod{780}.
\]

The Extended Euclidean Algorithm gives

\[
d=413.
\]

Check:

\[
17\cdot413=7021,
\]

and

\[
7021=9\cdot780+1.
\]

Therefore,

\[
\boxed{
17\cdot413\equiv1\pmod{780}.
}
\]

Our basic RSA key pair is now:

\[
\boxed{
\text{public key }(N,e)=(3233,17)
}
\]

and

\[
\boxed{
\text{private exponent }d=413.
}
\]

Conceptually, the simplest representation of the private key is

\[
(N,d)=(3233,413).
\]

So one of the main RSA relationships is simply:

\[
\boxed{
d=e^{-1}\pmod{\lambda(N)}.
}
\]

This is exactly the modular-inverse machinery we developed earlier.

---

## Euler's totient versus Carmichael's function

Many introductory RSA examples use Euler's totient:

\[
\varphi(N)
=
(p-1)(q-1).
\]

For our example,

\[
\varphi(3233)
=
60\cdot52
=
3120.
\]

If we compute

\[
17^{-1}\pmod{3120},
\]

we obtain

\[
d=2753.
\]

This is the classic private exponent often shown for the textbook parameters

\[
p=61,
\qquad
q=53,
\qquad
e=17.
\]

And it works.

But compare the two private exponents:

\[
2753\bmod780=413.
\]

Therefore,

\[
2753\equiv413\pmod{\lambda(N)}.
\]

Both satisfy the essential RSA relation

\[
ed\equiv1\pmod{\lambda(N)}.
\]

The difference comes from using two related quantities:

\[
\varphi(N)
=
(p-1)(q-1),
\]

versus

\[
\lambda(N)
=
\operatorname{lcm}(p-1,q-1).
\]

For two primes,

\[
\lambda(N)\mid\varphi(N).
\]

So choosing

\[
ed\equiv1\pmod{\varphi(N)}
\]

also implies the necessary relation modulo \(\lambda(N)\).

The \(\varphi(N)\)-based explanation is therefore not wrong.

But the more precise RSA key relation is naturally expressed using Carmichael's function:

\[
\boxed{
ed\equiv1\pmod{\lambda(N)}.
}
\]

This is the formulation used by PKCS #1 for the basic \((N,d)\) private-key representation.

This is also a useful lesson in revisiting old cryptography notes:

> An older explanation may be mathematically valid while a more precise formulation reveals the underlying structure more clearly.

For the rest of this article, we use

\[
d=413.
\]

---

## Does the key actually work?

Take a small message representative:

\[
m=65.
\]

The public RSA operation is

\[
c=m^e\bmod N.
\]

So:

\[
c
=
65^{17}\bmod3233.
\]

The result is

\[
\boxed{
c=2790.
}
\]

Now apply the private exponent:

\[
m'
=
2790^{413}\bmod3233.
\]

We recover

\[
\boxed{
m'=65.
}
\]

Therefore,

\[
m'=m.
\]

In Python:

```python
from math import gcd, lcm

p = 61
q = 53
e = 17

N = p * q

lambda_N = lcm(
    p - 1,
    q - 1,
)

assert gcd(e, lambda_N) == 1

d = pow(
    e,
    -1,
    lambda_N,
)

public_key = (N, e)
private_key = (N, d)

message = 65

ciphertext = pow(
    message,
    e,
    N,
)

recovered = pow(
    ciphertext,
    d,
    N,
)

print(public_key)   # (3233, 17)
print(private_key)  # (3233, 413)
print(ciphertext)   # 2790
print(recovered)    # 65

assert recovered == message
```

We have now constructed a complete toy RSA key pair from the number theory underneath it.

But there is an extremely important warning.

The expression

\[
c=m^e\bmod N
\]

is the mathematical RSA primitive.

It is **not a complete modern encryption scheme**.

Our toy example has:

```text
no secure message encoding
no randomized encryption layer
no OAEP
no production-size modulus
no production prime generation
no side-channel protection
```

So this code belongs in an educational cryptography repository.

It does not belong in a real application.

---

## Practical RSA keys and CRT parameters

A practical RSA private key commonly stores more than just

\[
N
\]

and

\[
d.
\]

Because the private-key holder already knows

\[
p
\]

and

\[
q,
\]

it can precompute CRT parameters.

The first two are the reduced private exponents:

\[
d_P=d\bmod(p-1),
\]

\[
d_Q=d\bmod(q-1).
\]

For our example,

\[
d_P
=
413\bmod60
=
53,
\]

and

\[
d_Q
=
413\bmod52
=
49.
\]

Another useful value is

\[
q_{\text{inv}}
=
q^{-1}\bmod p.
\]

Here,

\[
q_{\text{inv}}
=
53^{-1}\bmod61
=
38.
\]

So our complete toy parameter set is:

| Parameter | Value | Role |
| --- | ---: | --- |
| \(p\) | \(61\) | First secret prime |
| \(q\) | \(53\) | Second secret prime |
| \(N\) | \(3233\) | Public modulus |
| \(\lambda(N)\) | \(780\) | RSA exponent cycle |
| \(e\) | \(17\) | Public exponent |
| \(d\) | \(413\) | Private exponent |
| \(d_P\) | \(53\) | Private exponent modulo \(p-1\) |
| \(d_Q\) | \(49\) | Private exponent modulo \(q-1\) |
| \(q_{\text{inv}}\) | \(38\) | \(q^{-1}\bmod p\) |

In Python:

```python
d_P = d % (p - 1)
d_Q = d % (q - 1)
q_inv = pow(q, -1, p)

assert d_P == 53
assert d_Q == 49
assert q_inv == 38

assert (q * q_inv) % p == 1
```

These values allow private RSA operations to use the Chinese Remainder Theorem:

```text
private operation modulo N
        ↓
split into two smaller computations
        ↓
modulo p
modulo q
        ↓
CRT recombination
```

This is considerably faster than performing the entire private operation directly modulo \(N\).

So the hidden factorization is useful in two connected ways:

```text
p, q
 ↓
construct λ(N)
 ↓
derive d
```

and later:

```text
p, q
 ↓
derive CRT parameters
 ↓
accelerate private operations
```

This is also the same CRT structure that produced the fault attack we studied earlier.

An optimization and an attack surface can arise from exactly the same mathematical structure.

---

## Real key generation is a security problem

Our toy key began with:

```python
p = 61
q = 53
```

Real RSA key generation obviously cannot work like that.

The primes must be generated from unpredictable candidate values using a cryptographically appropriate random source.

Those candidates must then pass primality testing and the additional requirements of the relevant RSA specification.

At a high level, real key generation must reason about:

- prime size,
- prime randomness,
- primality testing,
- distinctness of \(p\) and \(q\),
- the relationship between the primes,
- the public exponent,
- the private exponent,
- CRT parameters,
- key validation,
- random-number-generator quality.

Current NIST RSA signature key generation uses two prime factors, and modern approved RSA signature moduli are at least 2048 bits.

For the public exponent, FIPS 186-5 requires an odd \(e\) satisfying

\[
2^{16}<e<2^{256}.
\]

The overwhelmingly common choice is

\[
e=65537=2^{16}+1.
\]

Why \(65537\)?

It is large enough to avoid historical issues associated with extremely small exponents, while its binary representation is sparse:

\[
65537=2^{16}+1.
\]

That makes public exponentiation efficient.

Importantly, \(e\) is public.

It does not need to be random or secret.

Choosing a larger public exponent does not automatically make RSA more secure.

The private security of RSA lies elsewhere: in the hidden factorization, private exponent, key-generation process, and secure implementation.

---

## Standards perspective

It is useful to distinguish what our toy construction teaches from what a real specification requires.

### PKCS #1

PKCS #1 v2.2 defines an RSA public key using:

\[
(N,e)
\]

with \(N\) constructed from distinct odd prime factors and

\[
\gcd(e,\lambda(N))=1.
\]

For the simple private-key representation, the private exponent satisfies

\[
ed\equiv1\pmod{\lambda(N)}.
\]

It also defines the CRT representation using values corresponding to

\[
p,
\quad
q,
\quad
d_P,
\quad
d_Q,
\quad
q_{\text{inv}}.
\]

That is essentially the parameter set we have just reconstructed by hand.

### NIST FIPS 186-5

FIPS 186-5 gives concrete procedures for RSA keys used for digital signatures, including requirements around:

- modulus sizes,
- generation of \(p\) and \(q\),
- probable-prime testing,
- public exponent selection,
- random-bit generation,
- validation conditions.

So production RSA key generation is not just the mathematical relation

\[
N=pq.
\]

It is a specified generation procedure.

### RSA key establishment

NIST SP 800-56B Rev. 2 specifies RSA-based integer-factorization key-establishment mechanisms.

As of 2026, NIST has reaffirmed that publication as current.

That says something about RSA's present **classical standardization status**.

It does not change the fact that RSA is not post-quantum secure.

A sufficiently capable cryptographically relevant quantum computer running Shor's algorithm would fundamentally change the security assumption behind RSA.

---

## When randomness fails: shared-prime RSA keys

This brings us back to the randomness discussion from much earlier in the series.

Suppose two independently generated RSA public moduli are

\[
N_1=pq_1
\]

and

\[
N_2=pq_2.
\]

Normally, their prime factors should be independently generated.

But suppose a failure in random-number generation causes both keys to reuse the same prime \(p\).

Then:

\[
\gcd(N_1,N_2)
=
\gcd(pq_1,pq_2).
\]

Assuming the other primes are distinct,

\[
\boxed{
\gcd(N_1,N_2)=p.
}
\]

The shared secret factor falls out immediately.

No discrete logarithm.

No side channel.

No fault injection.

No general-purpose integer factorization algorithm.

Just:

```python
from math import gcd

shared_factor = gcd(N1, N2)
```

Once \(p\) is known,

\[
q_1=\frac{N_1}{p}
\]

and

\[
q_2=\frac{N_2}{p}.
\]

Both RSA moduli are factored.

This is why randomness during key generation is not merely setup before the "real cryptography."

It is part of RSA security itself.

### A real research connection

A particularly important study is:

**Nadia Heninger, Zakir Durumeric, Eric Wustrow, and J. Alex Halderman**,  
*Mining Your Ps and Qs: Detection of Widespread Weak Keys in Network Devices*,  
USENIX Security 2012.

The researchers analysed large populations of public keys and found RSA keys sharing nontrivial prime factors, among other weak-key phenomena.

The attack is mathematically simple:

\[
\gcd(N_i,N_j).
\]

The interesting question was why supposedly independent keys ever shared secret primes.

The answer led back to weaknesses in key generation and entropy availability, particularly in constrained devices.

This connects several earlier pieces of the series:

```text
poor entropy
    ↓
prime reuse
    ↓
RSA moduli share a factor
    ↓
GCD
    ↓
factorization
    ↓
private-key recovery
```

The GCD once again becomes cryptanalysis.

---

## A complete educational pipeline

A more realistic educational RSA key-generation pipeline should therefore look something like this:

```text
cryptographic random source
        ↓
generate odd prime candidate
        ↓
small-prime filtering
        ↓
Miller-Rabin
        ↓
candidate p
        ↓

repeat independently
        ↓
candidate q
        ↓

check p ≠ q
        ↓
check required parameter conditions
        ↓
N = pq
        ↓
λ(N) = lcm(p - 1, q - 1)
        ↓
choose public exponent e
        ↓
check gcd(e, λ(N)) = 1
        ↓
d = e⁻¹ mod λ(N)
        ↓
derive dP, dQ, qInv
        ↓
validate key pair
```

The toy article deliberately leaves out many production requirements so that every mathematical step remains visible.

But now we know what has been simplified.

That distinction is important.

We are not pretending that:

```python
p = generate_prime()
q = generate_prime()
```

is the whole RSA key-generation problem.

We are using a transparent model to understand the structure that real implementations must build securely.

---

## Reader checkpoint

At this point you should be able to explain:

1. Why RSA begins with two distinct secret primes.
2. Why the modulus
   \[
   N=pq
   \]
   is public while its factorization remains secret.
3. Why \(e\) must satisfy
   \[
   \gcd(e,\lambda(N))=1.
   \]
4. Why the private exponent is
   \[
   d=e^{-1}\pmod{\lambda(N)}.
   \]
5. Why using \(\varphi(N)\) in the classic textbook construction also works.
6. Why \(\lambda(N)\) gives the more precise cycle relation.
7. What \(d_P\), \(d_Q\), and \(q_{\text{inv}}\) are used for.
8. Why the raw operation
   \[
   m^e\bmod N
   \]
   is not yet secure RSA encryption.
9. Why poor randomness during prime generation can completely destroy an RSA key.
10. Why two public RSA moduli sharing a secret prime can be factored with one GCD.

The entire construction can now be summarized as:

\[
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
\text{RSA key structure}.
}
\]

That is the point I wanted to reach before treating RSA as a complete cryptographic system.

---

## Next

We now possess a public key:

\[
(N,e)
\]

and a private key.

The obvious temptation is:

> Why not simply encrypt a message using
> \[
> c=m^e\bmod N?
> \]

Mathematically, it works.

But as encryption, textbook RSA is deeply inadequate.

The same message always produces the same ciphertext.

Its algebra is multiplicatively malleable.

Small or structured message spaces can be dangerous.

And there is no randomness protecting repeated encryptions.

So the next step is not another key-generation detail.

It is to understand the difference between a **mathematical trapdoor permutation** and a **secure encryption scheme**.

## Closing Cryptography From Zero

This article closes the **Cryptography From Zero** series.

We started with basic Python and elementary integer arithmetic and gradually built the mathematical and implementation vocabulary needed to understand real cryptographic constructions:

\[
\text{integers}
\rightarrow
\text{GCD}
\rightarrow
\text{modular inverses}
\rightarrow
\text{modular arithmetic}
\rightarrow
\text{groups}
\rightarrow
\text{Diffie-Hellman}
\rightarrow
\text{CRT}
\rightarrow
\text{primes}
\rightarrow
\text{RSA key generation}.
\]

The purpose was never to cover every cryptographic primitive. It was to build enough foundations that the articles that follow no longer need to treat the underlying mathematics as a black box.

From here, CryptoCave branches into more specialized series.

For RSA, the natural continuation is **RSA Deep Dives**, beginning with a question that immediately appears after constructing an RSA key:

> Why can we not simply encrypt with \(c=m^e\bmod N\)?

**Continue with RSA Deep Dives: _Why Textbook RSA Is Not Encryption — Determinism, Malleability, and the Need for OAEP._**
