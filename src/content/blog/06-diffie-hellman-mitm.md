---
title: "Breaking Diffie-Hellman Without Solving the Discrete Log: The Man-in-the-Middle Attack"
description: "Bare Diffie-Hellman can be mathematically correct and still connect you to the wrong person. A step-by-step man-in-the-middle attack shows why key agreement needs authentication."
pubDate: "2026-09-08"
category: "Public-Key Cryptography"
tags:
  - diffie-hellman
  - man-in-the-middle
  - authenticated-key-exchange
  - protocol-security
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

In the previous post, Eve broke our toy Diffie-Hellman exchange by brute-forcing the secret exponent.

That was useful because it showed something basic:

> correct mathematics does not rescue bad parameters.

But there is a much more interesting attack.

This time Eve does **not** solve a discrete logarithm.

She does not recover Alice's secret exponent.

She does not recover Bob's secret exponent.

She does not break modular exponentiation.

She simply makes Alice and Bob perform two perfectly valid Diffie-Hellman exchanges — both with the wrong person.

This is the point where I had to separate two ideas that are very easy to merge mentally:

```text
Do we share a secret?
        ≠
Do I know who I share it with?
```

Diffie-Hellman answers the first question.

Bare Diffie-Hellman does not answer the second.

![Man-in-the-middle attack against bare Diffie-Hellman](/images/blog/06-dh-mitm.svg)

*Eve does not need to defeat the group mathematics. She replaces the public values and creates two independent, valid shared secrets.*

---

## The protocol still works — just not between Alice and Bob

Let us reuse the same tiny public parameters:

$$
p=23,\qquad g=5.
$$

Alice chooses:

$$
a=6
$$

and computes:

$$
A=5^6\bmod23=8.
$$

Bob chooses:

$$
b=15
$$

and computes:

$$
B=5^{15}\bmod23=19.
$$

Without an attacker, Alice and Bob would exchange $A$ and $B$ and derive:

$$
Z=g^{ab}=2.
$$

Now place Eve between them.

Alice tries to send:

$$
A=8
$$

to Bob.

Eve intercepts it.

Bob never receives $A$.

Instead, Eve chooses her own secret exponent for the Bob-facing session:

$$
e_B=7,
$$

computes:

$$
E_B=5^7\bmod23=17,
$$

and sends $17$ to Bob while pretending it came from Alice.

At the same time, Bob tries to send:

$$
B=19
$$

to Alice.

Eve intercepts that too.

For the Alice-facing session, Eve chooses:

$$
e_A=3,
$$

computes:

$$
E_A=5^3\bmod23=10,
$$

and sends $10$ to Alice while pretending it came from Bob.

Now look at what happens.

Alice computes:

$$
K_{AE}=E_A^a=10^6\bmod23=6.
$$

Eve can compute the same value from Alice's real public value:

$$
A^{e_A}=8^3\bmod23=6.
$$

So Alice and Eve share:

$$
\boxed{K_{AE}=6}.
$$

Bob computes:

$$
K_{BE}=E_B^b=17^{15}\bmod23=15.
$$

Eve computes:

$$
B^{e_B}=19^7\bmod23=15.
$$

So Bob and Eve share:

$$
\boxed{K_{BE}=15}.
$$

Alice believes she shares a secret with Bob.

Bob believes he shares a secret with Alice.

But the real picture is:

```text
Alice  ←→  Eve  ←→  Bob
  K=6       K=15
```

There is **no Alice–Bob shared secret at all**.

And every Diffie-Hellman computation above is mathematically valid.

That is what makes this attack so useful pedagogically.

The cryptographic primitive did not malfunction.

The protocol failed to authenticate the peer.

---

If we wrote the attack as a tiny simulation, it would look roughly like this:

```python
p = 23
g = 5

alice_secret = 6
bob_secret = 15

A = pow(g, alice_secret, p)
B = pow(g, bob_secret, p)

eve_for_alice = 3
eve_for_bob = 7

E_A = pow(g, eve_for_alice, p)
E_B = pow(g, eve_for_bob, p)

alice_key = pow(E_A, alice_secret, p)
eve_with_alice = pow(A, eve_for_alice, p)

bob_key = pow(E_B, bob_secret, p)
eve_with_bob = pow(B, eve_for_bob, p)

assert alice_key == eve_with_alice
assert bob_key == eve_with_bob

assert alice_key != bob_key
```

The final line is the important one:

```python
assert alice_key != bob_key
```

Alice and Bob do not agree with each other.

Yet each one has successfully completed a valid Diffie-Hellman computation.

---

## Why Eve can now read and modify traffic

Suppose we later derive encryption keys from these two shared values.

Alice encrypts a message using the key derived from:

$$
K_{AE}=6.
$$

Eve knows that keying material too.

So Eve can:

```text
decrypt Alice's message
        ↓
read it
        ↓
modify it if she wants
        ↓
encrypt a new version using Bob's key
        ↓
forward it to Bob
```

Bob decrypts using the key derived from:

$$
K_{BE}=15.
$$

Everything may look perfectly normal from Bob's perspective.

The network can still be encrypted.

The problem is that it is encrypted in **two separate attacker-controlled sessions**.

This is one of the places where the phrase "encrypted connection" can be dangerously incomplete.

The real question is:

> Encrypted to whom?

---

This also explains the difference between a **passive** and an **active** attacker.

A passive Eve only listens:

```text
Alice  --------  Bob
          ↑
        listens
```

For properly chosen Diffie-Hellman parameters, passive observation should not reveal the shared secret.

But an active Eve controls the channel:

```text
Alice  ←→  Eve  ←→  Bob
```

She can:

- intercept,
- replace,
- delay,
- inject,
- reorder.

Bare Diffie-Hellman was never enough to stop this attacker.

The missing property is **authentication**.

---

## The mitigation is not "stronger Diffie-Hellman"

This is another distinction I find important.

Making $p$ larger does not solve this attack.

Using a harder discrete-log group does not solve this attack.

Switching from finite-field DH to elliptic-curve DH does not automatically solve this attack.

Why?

Because Eve never tried to solve the hard problem.

The problem is not:

```text
the discrete log was too easy
```

It is:

```text
Alice has no authenticated evidence that B came from Bob
Bob has no authenticated evidence that A came from Alice
```

So we need to bind the key exchange to identity and session context.

At a high level:

```text
ephemeral key exchange values
        +
identity / credentials
        +
authenticated transcript
        ↓
authenticated key exchange
```

Digital signatures are one way to do this when the protocol has authenticated public keys or certificates.

But I want to phrase the lesson carefully.

It is not enough to think:

> "Just sign some public number."

A real protocol must define **exactly what is authenticated**.

Typically that includes enough handshake context to stop values from being copied, substituted, or replayed into another session.

This is why modern protocols talk about **transcript binding**.

---

### A modern connection: TLS 1.3

TLS 1.3 is a useful example because the pieces are visible.

Conceptually, it separates:

```text
(EC)DHE
    ↓
establish shared secret material

CertificateVerify / PSK authentication
    ↓
authenticate the peer and handshake context

Finished
    ↓
confirm handshake integrity / key possession

HKDF key schedule
    ↓
derive traffic keys
```

The TLS 1.3 specification describes its handshake as an **Authenticated Key Exchange (AKE)** protocol.

It also authenticates the handshake transcript rather than treating the Diffie-Hellman public value as an isolated object.

**Reference:** [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446)

We are not implementing TLS here.

The point is only to see how the missing property from our toy protocol appears in a real architecture:

> key agreement and authentication are separate jobs that must be composed correctly.

---

Run the companion attack demo when we add it to the repository:

```powershell
python chapters/06_dh_mitm/demo.py
```

A good experiment is to print all three views:

```text
ALICE THINKS:
peer = Bob
shared = 6

EVE KNOWS:
with Alice = 6
with Bob   = 15

BOB THINKS:
peer = Alice
shared = 15
```

Then ask:

1. Did Eve solve a discrete logarithm?
2. Did any Diffie-Hellman equality fail?
3. Do Alice and Bob actually share the same key?
4. What piece of information did neither side authenticate?
5. Why would a larger prime not fix this attack?

If those five answers are clear, then the protocol-level lesson has landed.

---

At this point we have broken Diffie-Hellman in two completely different ways:

```text
Blog 05:
tiny group
    ↓
hard problem becomes easy
    ↓
recover secret exponent

Blog 06:
no authentication
    ↓
hard problem never attacked
    ↓
replace public values
```

Those are fundamentally different failure modes.

And that distinction is exactly what I want this project to teach.

The next question is more subtle.

Even if the peer is authenticated, what if we accidentally accept a public value that lives in the wrong subgroup?

Could an attacker force the computation into a tiny set and learn information about the secret a few bits at a time?

That takes us to our first structural parameter-validation attack.

**Next:** *Small-Subgroup Attacks: When the Group Is Large but the Secret Leaks Through a Tiny Subgroup.*
