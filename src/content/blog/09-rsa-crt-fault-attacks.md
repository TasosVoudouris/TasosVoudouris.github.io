---
title: "Fault Attacks From Zero: How One Wrong RSA Computation Can Reveal a Prime Factor"
description: "CRT makes RSA private operations faster—but if a fault corrupts only one branch, a single incorrect result can expose a factor of the modulus through a GCD."
pubDate: "2026-09-08"
category: "Public-Key Cryptography"
tags:
  - rsa
  - crt
  - fault-attacks
  - bellcore
  - implementation-security
  - cryptography-from-zero
difficulty: "Intermediate"
series: "Cryptography From Zero"
draft: false
---

In the previous post, the implementation leaked information because its execution pattern depended on secret bits.

This time the implementation does something different.

It computes the **wrong answer**.

At first that sounds less dangerous.

If a signature is wrong, verification should fail. So what?

But CRT-RSA has a beautiful—and slightly terrifying—failure mode:

> if one CRT branch is correct and the other is faulty, the wrong output may contain enough algebraic structure to factor the RSA modulus.

One incorrect computation.

One GCD.

One prime factor.

This is one of the cleanest examples I know of why implementation correctness is not only a reliability issue.

It can be a security boundary.

![CRT-RSA fault attack](/images/blog/09-crt-rsa-fault.svg)

*CRT-RSA computes independently modulo $p$ and $q$. A fault in only one branch creates an output that is still correct modulo one secret prime—and that asymmetry is exactly what the attacker exploits.*

---

## Why RSA uses CRT in the first place

Let:

$$
N=pq
$$

be an RSA modulus.

A private RSA operation computes something like:

$$
S=M^d\bmod N.
$$

Instead of doing one large exponentiation modulo $N$, an implementation that knows $p$ and $q$ can compute separately:

$$
S_p=M^d\bmod p
$$

and:

$$
S_q=M^d\bmod q.
$$

Then the Chinese Remainder Theorem reconstructs the unique value:

$$
S\bmod N
$$

satisfying:

$$
S\equiv S_p\pmod p
$$

and:

$$
S\equiv S_q\pmod q.
$$

This is much faster because the arithmetic happens modulo the smaller primes.

So CRT-RSA is not some strange insecure variant.

It is an optimization.

The security problem appears when we add a fault model.

---

Take a tiny RSA example:

$$
p=11,\qquad q=13.
$$

Then:

$$
N=143.
$$

Choose:

$$
e=7
$$

and:

$$
d=43,
$$

because:

$$
7\cdot43\equiv1\pmod{60}.
$$

Let the encoded message representative be:

$$
M=42.
$$

The correct RSA private operation gives:

$$
S=42^{43}\bmod143=3.
$$

And indeed:

$$
3^7\bmod143=42.
$$

The two CRT branches are:

$$
S_p=42^{43}\bmod11=3
$$

and:

$$
S_q=42^{43}\bmod13=3.
$$

Everything agrees.

Now imagine that during one execution, the computation modulo $p$ is corrupted.

Instead of:

$$
S_p=3,
$$

the device obtains:

$$
\widetilde S_p=4.
$$

But the $q$ branch remains correct:

$$
\widetilde S_q=3.
$$

CRT recombination now returns a faulty signature:

$$
\widetilde S=81.
$$

So:

$$
\widetilde S\equiv4\pmod{11},
$$

but:

$$
\widetilde S\equiv3\pmod{13}.
$$

The key fact is that the correct and faulty signatures still agree modulo one secret prime.

---

## The GCD suddenly becomes a factorization tool

Compare:

$$
S=3
$$

with:

$$
\widetilde S=81.
$$

Their difference is:

$$
S-\widetilde S=-78.
$$

Because the correct $q$ branch survived,

$$
S\equiv\widetilde S\pmod q.
$$

Therefore:

$$
q\mid(S-\widetilde S).
$$

But the $p$ branch was corrupted, so generally:

$$
p\nmid(S-\widetilde S).
$$

Now compute:

$$
\gcd(S-\widetilde S,N).
$$

For our example:

$$
\gcd(3-81,143)
=
\gcd(-78,143)
=
13.
$$

We have recovered:

$$
\boxed{q=13}.
$$

Then:

$$
p=\frac{143}{13}=11.
$$

RSA is factored.

The private key is gone.

In Python, the attack is almost absurdly short:

```python
from math import gcd

N = 143

correct = 3
faulty = 81

factor = gcd(correct - faulty, N)

print(factor)  # 13
```

This is exactly the kind of attack that changed how I think about the phrase:

> "The output was only wrong once."

One wrong output can be enough.

---

### An even stronger version: the correct signature may not be needed

There is another elegant observation associated with Arjen Lenstra's 1996 memo.

For a valid RSA signature:

$$
S^e\equiv M\pmod N.
$$

For our faulty result:

$$
\widetilde S=81.
$$

Public verification gives:

$$
81^7\bmod143=16,
$$

which is wrong globally.

But because the $q$ branch was still correct:

$$
\widetilde S^e\equiv M\pmod q.
$$

So:

$$
q\mid(\widetilde S^e-M).
$$

Compute:

$$
\gcd(\widetilde S^e-M,N).
$$

In our toy example:

$$
\gcd(16-42,143)
=
\gcd(-26,143)
=
13.
$$

Again:

$$
\boxed{q=13}.
$$

So in this variant, the attacker needs:

- the public RSA key,
- the message representative,
- one faulty signature.

The public verification equation itself helps expose the factor.

That is a very powerful lesson:

> public verifiability can become part of an attack when the implementation releases a structurally faulty result.

---

> **Research connection — the Bellcore fault-attack line.**  
> Boneh, DeMillo, and Lipton showed that faults can break cryptographic implementations even when the underlying mathematics remains sound. Their EUROCRYPT '97 work, *On the Importance of Checking Cryptographic Protocols for Faults*, includes the famous CRT-RSA setting where a faulty computation can reveal a factor of the modulus.
>
> [Boneh–DeMillo–Lipton publication page](https://crypto.stanford.edu/~dabo/abstracts/faults.html)
>
> Arjen Lenstra's 1996 memo, *RSA Signature Generation in the Presence of Faults*, described the particularly strong verification-based variant that can use a message and a single faulty CRT-RSA signature.

The important wording here is not:

```text
CRT is insecure
```

It is:

```text
CRT creates independent secret-modulus branches
        ↓
one-branch fault creates asymmetric correctness
        ↓
asymmetry exposes a common divisor
        ↓
GCD factors N
```

That is a much more precise cryptographic statement.

---

## Mitigate: never release an unchecked private result

The most obvious lesson is:

> do not let a faulty private computation escape as if it were valid.

For a signature, one conceptual countermeasure is to verify the result before returning it.

If:

$$
S=M^d\bmod N,
$$

then check the public relation:

$$
S^e\bmod N\stackrel{?}=M.
$$

If verification fails:

```text
do not output the signature
```

That simple idea directly targets the attack we just built.

Real fault-resistant implementations can use additional techniques as well:

- redundant computations,
- consistency checks between CRT branches,
- infective countermeasures,
- hardened recombination,
- hardware-level fault detection,
- temporal or spatial redundancy.

But, as with side channels, there is no magical one-line universal defense.

The countermeasure has to match the fault model.

And the implementation has to be analysed under faults, not only under normal execution.

---

This attack also connects several posts in the series in a way I really like.

We first learned the GCD as:

$$
\gcd(48,18)=6.
$$

Then we used it to decide whether inverses exist.

Then we saw shared-prime RSA failures.

Now the same operation becomes:

$$
\gcd(S-\widetilde S,N)
$$

and extracts a secret prime from a faulted cryptographic computation.

So the GCD never really disappeared.

We just kept changing the context around it.

That is one of the main reasons I wanted to build this series from the foundations instead of beginning with finished APIs.

---

A good toy experiment for the repository is:

```text
1. generate tiny RSA parameters
2. compute a correct CRT-RSA result
3. deliberately corrupt exactly one CRT branch
4. recombine the faulty result
5. confirm verification fails
6. compute gcd(correct - faulty, N)
7. recover one factor
```

Then repeat the experiment using only:

```text
message
faulty signature
public exponent
N
```

and compute:

$$
\gcd(\widetilde S^e-M,N).
$$

The result should make the fault mechanism almost impossible to forget.

---

We have now seen two implementation-level failures with very different shapes:

```text
side channel:
correct output
+ observable execution behavior
→ secret leakage

fault attack:
incorrect computation
+ algebraic structure
→ secret-key recovery
```

Both leave the underlying hard mathematical problem untouched.

That distinction matters.

The cryptosystem is not merely:

```text
the theorem
```

or:

```text
the formula
```

It is the formula running on a real machine under an attacker model.

For the next post, I want to step back from attacks for a moment and build another foundational tool that has already appeared implicitly several times:

**the Chinese Remainder Theorem itself.**

We used CRT inside RSA.

We used CRT to combine subgroup leakage residues.

Now it is time to understand why reconstruction from several modular views works at all.

**Next:** *The Chinese Remainder Theorem: Reconstructing One Secret From Several Modular Worlds.*
