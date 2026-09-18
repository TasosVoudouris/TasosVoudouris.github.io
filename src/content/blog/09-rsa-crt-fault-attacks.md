---
title: "Fault Attacks From Zero: How One Wrong RSA Computation Can Reveal a Prime Factor"
description: "CRT makes RSA private operations faster—but if a fault corrupts only one branch, a single incorrect result can expose a factor of the modulus through a GCD."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Public-Key Cryptography"
  - "Cryptanalysis"
  - "Implementation Security"
tags:
  - "rsa"
  - "crt"
  - "fault-attacks"
  - "bellcore"
  - "implementation-security"
  - "cryptography-from-zero"
difficulty: "Intermediate"
series: "Cryptography From Zero"
seriesOrder: 10
draft: false
---

In the previous article, the implementation leaked information even though the final mathematical result was correct.

This time the failure is different.

The implementation computes the **wrong answer**.

At first that sounds less dangerous.

If a signature is wrong, verification should fail. So what?

But CRT-RSA has a remarkably clean — and slightly terrifying — failure mode:

> If one CRT branch remains correct while the other is corrupted, a single faulty RSA result can contain enough algebraic structure to reveal a prime factor of the modulus.

One faulty computation.

One GCD.

One secret prime.

This is one of the clearest examples of why implementation correctness is not merely a reliability concern.

It is a cryptographic security boundary.

![CRT-RSA fault attack](/images/blog/09-crt-rsa-fault.svg)

*CRT-RSA computes independently modulo \(p\) and \(q\). If a fault corrupts only one branch, the final output may remain correct modulo one secret prime. That asymmetry is exactly what the attacker exploits.*

---

## Table of Contents

- [Why RSA uses the Chinese Remainder Theorem](#why-rsa-uses-the-chinese-remainder-theorem)
- [Injecting one faulty CRT branch](#injecting-one-faulty-crt-branch)
- [Why one GCD reveals a prime factor](#why-one-gcd-reveals-a-prime-factor)
- [The stronger single-fault variant](#the-stronger-single-fault-variant)
- [Why the attack works](#why-the-attack-works)
- [What kind of fault are we assuming?](#what-kind-of-fault-are-we-assuming)
- [Mitigation: verify before releasing](#mitigation-verify-before-releasing)
- [A connection back to the GCD](#a-connection-back-to-the-gcd)
- [Reproduce the attack](#reproduce-the-attack)
- [Papers and further reading](#papers-and-further-reading)
- [What we have learned](#what-we-have-learned)
- [Next](#next)

---

## Why RSA uses the Chinese Remainder Theorem

Let

\[
N=pq
\]

be an RSA modulus constructed from two secret primes \(p\) and \(q\).

A private RSA operation computes a value of the form

\[
S=M^d\bmod N,
\]

where:

- \(M\) is an encoded message representative,
- \(d\) is the private exponent.

A direct exponentiation modulo \(N\) is possible.

But an implementation that knows the factorization

\[
N=pq
\]

can perform the computation more efficiently by working separately modulo the two smaller primes.

It computes

\[
S_p=M^d\bmod p
\]

and

\[
S_q=M^d\bmod q.
\]

The Chinese Remainder Theorem then reconstructs the unique value

\[
S\bmod N
\]

satisfying

\[
S\equiv S_p\pmod p
\]

and

\[
S\equiv S_q\pmod q.
\]

Conceptually:

```text
                     M
                     │
          +----------+----------+
          │                     │
          ▼                     ▼

     exponentiate            exponentiate
       modulo p                modulo q

          │                     │
          ▼                     ▼

         Sp                    Sq

          +----------+----------+
                     │
                     ▼

              CRT recombination

                     │
                     ▼

                  S mod N
```

This is not an exotic RSA variant.

CRT-based private operations are a standard optimization.

The security problem appears when we introduce a **fault model**.

---

## Injecting one faulty CRT branch

Take a deliberately tiny RSA instance:

\[
p=11,
\qquad
q=13.
\]

Then

\[
N=pq=143.
\]

Choose the public exponent

\[
e=7.
\]

For these primes,

\[
\lambda(N)
=
\operatorname{lcm}(p-1,q-1)
=
\operatorname{lcm}(10,12)
=
60.
\]

Choose

\[
d=43
\]

because

\[
7\cdot43
=
301
\equiv1\pmod{60}.
\]

So \(d\) is a valid RSA private exponent modulo the Carmichael value

\[
\lambda(N)=60.
\]

Notice that

\[
\varphi(N)
=
(p-1)(q-1)
=
120,
\]

so here we are explicitly using the condition

\[
ed\equiv1\pmod{\lambda(N)},
\]

which is sufficient for RSA.

Let the encoded message representative be

\[
M=42.
\]

The correct RSA private operation gives

\[
S
=
42^{43}\bmod143
=
3.
\]

Public verification recovers the message representative:

\[
S^e
=
3^7
\equiv42\pmod{143}.
\]

So the correct result is

\[
\boxed{
S=3
}
\]

and the signature equation holds.

### The two CRT branches

Modulo \(p=11\),

\[
S_p
=
42^{43}\bmod11
=
3.
\]

Modulo \(q=13\),

\[
S_q
=
42^{43}\bmod13
=
3.
\]

Thus the correct result satisfies

\[
S\equiv3\pmod{11}
\]

and

\[
S\equiv3\pmod{13}.
\]

Everything is consistent.

Now introduce a fault.

Suppose something corrupts only the computation modulo \(p\).

Instead of

\[
S_p=3,
\]

the device obtains

\[
\widetilde S_p=4.
\]

The computation modulo \(q\) remains correct:

\[
\widetilde S_q=3.
\]

CRT recombination now produces a faulty result

\[
\widetilde S=81.
\]

Indeed,

\[
81\equiv4\pmod{11},
\]

while

\[
81\equiv3\pmod{13}.
\]

This is the crucial structure:

```text
correct result S

mod p → correct
mod q → correct
```

but:

```text
faulty result S~

mod p → wrong
mod q → still correct
```

The faulty value is globally incorrect modulo \(N\), but it remains correct modulo **one secret factor**.

That is exactly what the attacker needs.

---

## Why one GCD reveals a prime factor

Compare the correct result

\[
S=3
\]

with the faulty result

\[
\widetilde S=81.
\]

Their difference is

\[
S-\widetilde S
=
3-81
=
-78.
\]

Because the \(q\)-branch survived the fault,

\[
S\equiv\widetilde S\pmod q.
\]

Therefore,

\[
q\mid(S-\widetilde S).
\]

But the result is not normally correct modulo \(p\), so in the useful fault case,

\[
p\nmid(S-\widetilde S).
\]

The difference therefore contains one prime factor of \(N\), but not the other.

Compute:

\[
\gcd(S-\widetilde S,N).
\]

For our values,

\[
\gcd(3-81,143)
=
\gcd(-78,143)
=
13.
\]

Thus,

\[
\boxed{
q=13
}
\]

and the second factor follows immediately:

\[
p
=
\frac{N}{q}
=
\frac{143}{13}
=
11.
\]

The RSA modulus is factored.

Once

\[
p
\]

and

\[
q
\]

are known, the attacker can reconstruct the private key.

The entire attack in Python is almost absurdly short:

```python
from math import gcd

N = 143

correct = 3
faulty = 81

factor = gcd(correct - faulty, N)

print(factor)
```

Output:

```text
13
```

One incorrect RSA output was enough.

That is why the sentence

> "The signature was wrong only once"

is not reassuring.

For a cryptographic implementation, one structurally wrong output can be catastrophic.

---

## The stronger single-fault variant

The previous attack assumed that the attacker possesses both:

\[
S
\]

and

\[
\widetilde S.
\]

But there is an even stronger observation.

For a correct RSA signature,

\[
S^e\equiv M\pmod N.
\]

The faulty signature

\[
\widetilde S=81
\]

does not satisfy this relation globally.

Indeed,

\[
81^7\bmod143
=
16
\neq42.
\]

So public verification fails.

But remember: the computation remained correct modulo \(q\).

Therefore,

\[
\widetilde S
\equiv
S
\pmod q.
\]

Raising both sides to the public exponent gives

\[
\widetilde S^e
\equiv
S^e
\pmod q.
\]

Since the correct signature satisfies

\[
S^e\equiv M\pmod q,
\]

we obtain

\[
\widetilde S^e
\equiv
M
\pmod q.
\]

Therefore,

\[
q
\mid
(\widetilde S^e-M).
\]

Now compute:

\[
\gcd(\widetilde S^e-M,N).
\]

In the toy example,

\[
\widetilde S^e\bmod N
=
81^7\bmod143
=
16.
\]

So:

\[
\gcd(16-42,143)
=
\gcd(-26,143)
=
13.
\]

Again,

\[
\boxed{
q=13
}
\]

is recovered.

This version requires only:

- the public modulus \(N\),
- the public exponent \(e\),
- the message representative \(M\),
- one faulty RSA signature \(\widetilde S\).

The correct signature is unnecessary.

That is a particularly striking result.

A public verification equation, normally designed to confirm signatures, becomes part of the attack because the faulty output remains correct modulo one hidden prime.

---

## Why the attack works

The important statement is **not**

```text
CRT is insecure
```

and it is not:

```text
RSA mathematics is broken
```

The real structure is:

```text
CRT-RSA
   ↓
two computations modulo secret primes
   ↓
fault corrupts only one branch
   ↓
one branch remains algebraically correct
   ↓
faulty output agrees with the correct result
modulo exactly one secret factor
   ↓
difference has a nontrivial common divisor with N
   ↓
GCD reveals the factor
```

Algebraically, if the \(q\)-branch remains correct,

\[
S\equiv\widetilde S\pmod q.
\]

Hence

\[
S-\widetilde S
\equiv0\pmod q.
\]

Therefore,

\[
q\mid(S-\widetilde S).
\]

But if the \(p\)-branch is genuinely corrupted,

\[
S\not\equiv\widetilde S\pmod p
\]

in the useful fault case.

Thus:

\[
\gcd(S-\widetilde S,pq)=q.
\]

The GCD acts as a detector for the hidden modular agreement.

This is why CRT creates such an elegant fault attack.

The faulty output remembers which secret modular branch remained correct.

---

## What kind of fault are we assuming?

Our toy experiment simply changes

\[
S_p=3
\]

into

\[
\widetilde S_p=4.
\]

A real attacker obviously does not normally edit an internal Python variable by hand.

Physical and hardware fault attacks instead attempt to disturb a device during computation.

Depending on the target, faults may be induced through mechanisms such as:

- voltage glitches,
- clock glitches,
- electromagnetic injection,
- laser fault injection,
- temperature manipulation,
- memory corruption,
- rowhammer-style effects in appropriate settings,
- naturally occurring hardware errors.

The resulting fault model matters enormously.

An attacker might cause:

- a random branch result,
- one skipped instruction,
- one corrupted register,
- one corrupted memory word,
- one incorrect modular multiplication,
- one branch of a redundant computation to fail.

Our article uses the cleanest model:

\[
\boxed{
\text{one CRT branch wrong, one CRT branch correct}
}
\]

because it makes the underlying mathematics completely visible.

Real fault analysis asks whether an attacker can create a fault close enough to this model reliably enough to exploit it.

---

## Mitigation: verify before releasing

The most immediate defense follows directly from the attack:

> Do not release a faulty private RSA result.

If a private operation computes

\[
S=M^d\bmod N,
\]

the implementation can verify the public RSA relation before returning the value:

\[
S^e\bmod N
\stackrel{?}{=}
M.
\]

Conceptually:

```text
private CRT computation
        ↓
candidate signature S
        ↓
public verification
        ↓
S^e mod N == M ?
        │
     +--+--+
     │     │
    yes    no
     │     │
     ▼     ▼
 return   abort
```

Our faulty signature gives

\[
81^7\bmod143=16,
\]

while

\[
M=42.
\]

So verification immediately detects the fault.

The signature must not be released.

### Why this directly stops our attack

Both GCD attacks require the attacker to obtain

\[
\widetilde S.
\]

If the implementation detects the inconsistency internally and refuses to output the faulty result, the simple attack loses its crucial input.

This leads to a broad implementation principle:

\[
\boxed{
\text{check secret-dependent results before exposing them}
}
\]

when the threat model requires such protection.

### Other countermeasure families

Fault-resistant implementations may also use:

- redundant computation,
- CRT consistency checks,
- duplicated exponentiations,
- checksum or residue techniques,
- hardened CRT recombination,
- infective countermeasures,
- temporal redundancy,
- spatial redundancy,
- hardware-level fault sensors.

Some approaches attempt to **detect** a fault and abort.

Others attempt to make a faulty computation unusable to the attacker.

The details matter.

As with side-channel resistance, there is no universal one-line defense.

The countermeasure must be evaluated against the relevant fault model.

A defense against a single random transient error may not protect against an attacker who can inject multiple carefully timed faults.

---

## A connection back to the GCD

This attack is also a nice example of why building cryptography from elementary mathematics is useful.

We first encountered the GCD as something simple:

\[
\gcd(48,18)=6.
\]

Then we used it to determine whether an element is invertible modulo \(n\):

\[
\gcd(a,n)=1.
\]

Later we will use the extended Euclidean algorithm to construct modular inverses.

In RSA, the same operation suddenly becomes:

\[
\gcd(S-\widetilde S,N)
\]

and extracts a secret prime from a faulty private-key computation.

Or, in the single-fault version:

\[
\gcd(\widetilde S^e-M,N).
\]

The GCD never disappeared.

The cryptographic context around it changed.

That is one of the reasons for building this series from elementary number theory instead of beginning with high-level APIs.

A simple operation can reappear much later as the core of a devastating attack.

---

## Reproduce the attack

A good exercise is to implement the entire sequence rather than hard-code the final faulty value.

Start with:

```python
from math import gcd

p = 11
q = 13

N = p * q

e = 7
d = 43

M = 42
```

Compute the correct private operation:

```python
S = pow(M, d, N)

assert S == 3
assert pow(S, e, N) == M
```

Then compute the two CRT branches:

```python
S_p = pow(M, d, p)
S_q = pow(M, d, q)

assert S_p == 3
assert S_q == 3
```

Now deliberately corrupt only one branch:

```python
faulty_S_p = 4
faulty_S_q = S_q
```

For this tiny example, search for the unique CRT recombination:

```python
faulty = None

for candidate in range(N):
    if (
        candidate % p == faulty_S_p
        and candidate % q == faulty_S_q
    ):
        faulty = candidate
        break

assert faulty == 81
```

Confirm that verification fails:

```python
assert pow(faulty, e, N) != M
```

### Attack 1 — correct and faulty outputs

```python
factor_1 = gcd(S - faulty, N)

print(factor_1)

assert factor_1 in (p, q)
```

Output:

```text
13
```

### Attack 2 — one faulty output only

```python
verification_value = pow(faulty, e, N)

factor_2 = gcd(
    verification_value - M,
    N,
)

print(factor_2)

assert factor_2 in (p, q)
```

Again:

```text
13
```

Finally:

```python
other_factor = N // factor_2

print(other_factor)

assert {factor_2, other_factor} == {p, q}
```

The complete factorization has been recovered.

### Reader checkpoint

Make sure you can explain:

1. Why CRT-RSA uses two independent modular computations.
2. Why the faulty result remains correct modulo \(q\).
3. Why this implies
   \[
   q\mid(S-\widetilde S).
   \]
4. Why the GCD does not normally return all of \(N\).
5. Why knowing one factor immediately reveals the other.
6. Why the stronger variant does not need the correct signature.
7. Why verifying the private result before release blocks this simple attack.
8. Why CRT itself is not "broken."

The essential structure is:

\[
\boxed{
\text{partial correctness}
\rightarrow
\text{hidden divisibility relation}
\rightarrow
\gcd
\rightarrow
\text{factorization}
}
\]

---

## Papers and further reading

### Boneh, DeMillo, and Lipton

**Dan Boneh, Richard A. DeMillo, and Richard J. Lipton**,  
*On the Importance of Checking Cryptographic Protocols for Faults*,  
EUROCRYPT 1997.

This work is one of the foundational references showing that faults in cryptographic computations can lead to catastrophic key recovery even when the underlying mathematical primitive remains secure.

The CRT-RSA setting is the classic example.

### Lenstra's RSA fault observation

**Arjen K. Lenstra**,  
*Memo on RSA Signature Generation in the Presence of Faults*, 1996.

Lenstra observed the particularly strong form of the RSA fault attack in which the public verification equation can be combined with one faulty signature to recover a factor without needing the corresponding correct signature.

### Bellcore terminology

This family of attacks is often informally referred to as the **Bellcore attack**, reflecting the environment in which the early fault-attack work was developed.

The important lesson is broader than the historical name:

\[
\boxed{
\text{faults must be included in the implementation threat model}
}
\]

for systems where an attacker may influence physical computation.

---

## What we have learned

The previous article and this one expose two very different implementation failures.

A side channel gives:

```text
correct computation
        +
observable implementation behavior
        ↓
information leakage
```

A fault attack gives:

```text
incorrect computation
        +
remaining algebraic structure
        ↓
key recovery
```

Neither attack requires breaking the underlying hard mathematical problem.

For timing attacks, RSA is not broken because modular exponentiation became mathematically easy.

For the CRT fault attack, factoring is not solved generically.

Instead, the implementation accidentally gives the attacker a value containing a hidden factorization relation.

This leads to an increasingly important view of cryptography:

```text
cryptographic security
        ≠
only the theorem

cryptographic security
        =
mathematics
+
protocol
+
parameters
+
implementation
+
attacker model
```

The machine executing the formula is part of the cryptographic system.

---

## Next

We have already used the Chinese Remainder Theorem several times without stopping to build it carefully.

It appeared here because CRT allows RSA to perform two smaller private computations and reconstruct one result.

It appeared earlier when several small-subgroup leaks revealed:

\[
d\bmod3,
\qquad
d\bmod4,
\qquad
d\bmod5,
\]

and CRT combined those modular views into one value.

So before continuing deeper into RSA and cryptanalysis, it is worth understanding the theorem itself.

Why can several congruences describe one unique number modulo a product?

How do we reconstruct that number?

And why does coprimality matter?

**Next: The Chinese Remainder Theorem — Reconstructing One Value From Several Modular Worlds.**
