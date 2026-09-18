---
title: "Breaking Diffie-Hellman Without Solving the Discrete Log: The Man-in-the-Middle Attack"
description: "Bare Diffie-Hellman can be mathematically correct and still connect you to the wrong person. A step-by-step man-in-the-middle attack shows why key agreement needs authentication."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Public-Key Cryptography"
  - "Key Exchange"
  - "Discrete Logarithms"
  - "Cryptanalysis"
tags:
  - "diffie-hellman"
  - "man-in-the-middle"
  - "authenticated-key-exchange"
  - "protocol-security"
  - "cryptography-from-zero"
difficulty: "Introductory"
series: "Cryptography From Zero"
seriesOrder: 7
draft: false
---

In the previous article, Eve broke our toy Diffie-Hellman exchange by recovering Alice's secret exponent with brute force.

That attack worked because the group was tiny.

The mathematics of Diffie-Hellman remained perfectly correct, but the supposedly hard discrete-logarithm problem was easy at that scale.

Now we consider a much more interesting failure.

This time Eve does **not** solve a discrete logarithm.

She does not recover Alice's secret exponent.

She does not recover Bob's secret exponent.

She does not defeat modular exponentiation.

Instead, she makes Alice and Bob perform two perfectly valid Diffie-Hellman exchanges — each with Eve rather than with one another.

The distinction is fundamental:

```text
Do we share a secret?
        ≠
Do I know who I share it with?
```

Diffie-Hellman can solve the first problem.

Bare Diffie-Hellman does not solve the second.

![Man-in-the-middle attack against bare Diffie-Hellman](/images/blog/06-dh-mitm.svg)

*Eve does not need to defeat the group mathematics. She replaces the public Diffie-Hellman values and establishes two independent shared secrets.*

---

## The attack

Reuse the same toy parameters:

$$
p=23,
\qquad
g=5.
$$

Alice chooses

$$
a=6
$$

and computes

$$
A=g^a
=
5^6\bmod 23
=
8.
$$

Bob chooses

$$
b=15
$$

and computes

$$
B=g^b
=
5^{15}\bmod 23
=
19.
$$

Without an attacker, Alice would compute

$$
B^a
=
19^6\bmod 23
=
2,
$$

while Bob would compute

$$
A^b
=
8^{15}\bmod 23
=
2.
$$

Thus the honest execution gives

$$
\boxed{
g^{ab}=2
}
$$

to both participants.

Now place Eve between them.

Alice attempts to send

$$
A=8
$$

to Bob.

Eve intercepts it.

Bob never receives Alice's real Diffie-Hellman share.

Instead, Eve chooses her own secret exponent for the session with Bob:

$$
e_B=7.
$$

She computes

$$
E_B
=
g^{e_B}
=
5^7\bmod 23
=
17
$$

and sends $E_B$ to Bob while pretending that it came from Alice.

At the same time, Bob attempts to send

$$
B=19
$$

to Alice.

Again Eve intercepts the message.

For her session with Alice, Eve chooses a second secret exponent:

$$
e_A=3,
$$

and computes

$$
E_A
=
g^{e_A}
=
5^3\bmod 23
=
10.
$$

She sends $E_A$ to Alice while pretending that it came from Bob.

The network now looks like this:

```text
Alice             Eve              Bob

  A = g^a  ----X

             E_B = g^eB --------->

             <--------- B = g^b

  <--------- E_A = g^eA
```

The important point is that Alice and Bob have no authenticated way to distinguish Eve's substituted values from genuine Diffie-Hellman shares.

### Alice's session

Alice receives

$$
E_A=10
$$

and computes

$$
K_{AE}
=
E_A^a
=
10^6\bmod 23
=
6.
$$

Eve knows $e_A=3$, so using Alice's genuine public value $A=8$, she computes

$$
A^{e_A}
=
8^3\bmod 23
=
6.
$$

Therefore,

$$
\boxed{
K_{AE}=6
}
$$

is shared between Alice and Eve.

### Bob's session

Bob receives

$$
E_B=17
$$

and computes

$$
K_{BE}
=
E_B^b
=
17^{15}\bmod 23
=
15.
$$

Eve knows $e_B=7$, so using Bob's genuine public value $B=19$, she computes

$$
B^{e_B}
=
19^7\bmod 23
=
15.
$$

Therefore,

$$
\boxed{
K_{BE}=15
}
$$

is shared between Bob and Eve.

The actual situation is:

```text
Alice  ←────────→  Eve  ←────────→  Bob

       KAE = 6        KBE = 15
```

Alice thinks the peer is Bob.

Bob thinks the peer is Alice.

But Alice and Bob do not share a secret with each other at all.

Every Diffie-Hellman equation executed successfully.

The failure is not algebraic.

It is a failure of **authentication**.

---

## Reproducing the attack in Python

The entire attack can be reproduced directly:

```python
p = 23
g = 5

# Alice and Bob
alice_secret = 6
bob_secret = 15

A = pow(g, alice_secret, p)
B = pow(g, bob_secret, p)

# Eve creates one DH secret for each side
eve_for_alice = 3
eve_for_bob = 7

E_A = pow(g, eve_for_alice, p)
E_B = pow(g, eve_for_bob, p)

# Alice believes E_A came from Bob
alice_key = pow(E_A, alice_secret, p)

# Eve derives the same key using Alice's genuine public value
eve_with_alice = pow(A, eve_for_alice, p)

# Bob believes E_B came from Alice
bob_key = pow(E_B, bob_secret, p)

# Eve derives Bob's key using Bob's genuine public value
eve_with_bob = pow(B, eve_for_bob, p)

assert alice_key == eve_with_alice
assert bob_key == eve_with_bob

assert alice_key != bob_key

print("Alice ↔ Eve:", alice_key)
print("Eve ↔ Bob:  ", bob_key)
```

Output:

```text
Alice ↔ Eve: 6
Eve ↔ Bob:   15
```

The most important test is:

```python
assert alice_key != bob_key
```

Alice and Bob do not agree with each other.

Yet neither participant sees a mathematical failure.

Each has completed a valid Diffie-Hellman computation.

That is precisely why this attack is conceptually more interesting than simply brute-forcing the toy discrete logarithm.

---

## Why Eve can read and modify the communication

Suppose Alice and Bob now derive symmetric encryption keys from the values they believe came from their Diffie-Hellman exchange.

Alice derives a key from

$$
K_{AE}=6.
$$

Eve knows exactly the same value.

Bob derives a different key from

$$
K_{BE}=15.
$$

Again, Eve knows exactly the same value.

Suppose Alice sends:

```text
"meet at 18:00"
```

The traffic can flow like this:

```text
Alice
  │
  │ Encrypt with key derived from KAE
  ▼
ciphertext
  │
  ▼
Eve
  │
  ├── decrypt with Alice-facing key
  │
  ├── read plaintext
  │
  ├── optionally modify plaintext
  │
  └── encrypt with Bob-facing key
  ▼
new ciphertext
  │
  ▼
Bob
```

Bob successfully decrypts the message with his own session key.

If the protocol contains no mechanism authenticating the peer or the handshake transcript, neither side necessarily realizes that the encrypted communication has been terminated and re-created by Eve.

This gives us an important lesson:

$$
\boxed{
\text{encrypted}
\neq
\text{authenticated}
}
$$

An encrypted channel answers:

> Who can understand these ciphertexts?

Authentication answers a different question:

> Who am I actually communicating with?

The phrase *secure connection* usually requires both questions to be addressed.

---

## Passive and active attackers

The previous toy discrete-log attack can be viewed as a passive attack.

Eve observes:

$$
g,\qquad g^a,\qquad g^b
$$

and tries to infer the secret.

Conceptually:

```text
Alice ------------------------ Bob
               ↑
              Eve
            observes
```

A properly parameterized Diffie-Hellman group should make the relevant computational problem infeasible for such an observer.

The man-in-the-middle attacker is stronger.

Eve controls the communication channel:

```text
Alice  ←────────→  Eve  ←────────→  Bob
```

She may:

- intercept messages,
- replace values,
- inject new messages,
- delay messages,
- reorder messages,
- replay previous messages.

This is an **active attacker**.

Bare Diffie-Hellman does not authenticate the exchanged public values, so nothing prevents Eve from substituting her own.

This is also why increasing the modulus does not solve the problem.

Suppose instead of our tiny group we use an enormous group where solving the discrete logarithm would require an infeasible amount of computation.

Eve still does not need to solve it.

She chooses her own values:

$$
E_A=g^{e_A},
\qquad
E_B=g^{e_B}
$$

and substitutes them exactly as before.

Moving from finite-field DH to elliptic-curve Diffie-Hellman does not automatically solve the problem either.

Instead of

$$
A=g^a,
$$

an elliptic-curve protocol may use

$$
A=aG.
$$

Eve can still replace $A$ with

$$
E=eG
$$

unless the protocol authenticates the public values.

So the problem is not:

```text
our Diffie-Hellman group was too weak
```

but rather:

```text
Alice cannot prove that the value she received belongs to Bob

Bob cannot prove that the value he received belongs to Alice
```

---

## From key agreement to authenticated key agreement

The mitigation is therefore not simply **stronger Diffie-Hellman**.

We need to connect the ephemeral key agreement to some authenticated information.

Conceptually:

```text
Diffie-Hellman values
        +
participant identity
        +
credentials / authentication key
        +
handshake transcript
        ↓
authenticated key exchange
```

One possibility is to use digital signatures.

Suppose Bob possesses a long-term signing key

$$
sk_B
$$

whose corresponding public key

$$
pk_B
$$

Alice already trusts through some authenticated mechanism.

Bob could authenticate his ephemeral Diffie-Hellman contribution.

But even here, the simple statement

> "Sign the DH public key"

is not enough as a general protocol-design rule.

A real protocol must specify **exactly what is signed or otherwise authenticated**.

For example, we may want the authentication to cover:

$$
\text{protocol identifier},
$$

$$
\text{Alice identity},
$$

$$
\text{Bob identity},
$$

$$
A,
$$

$$
B,
$$

and additional handshake information.

Conceptually:

$$
\sigma_B
=
\operatorname{Sign}_{sk_B}
\left(
H(
\text{context}
\parallel
A
\parallel
B
\parallel
\text{transcript}
)
\right).
$$

Alice verifies:

$$
\operatorname{Verify}_{pk_B}(\sigma_B,\ldots).
$$

Now Eve cannot simply replace Bob's contribution with

$$
E_A
$$

unless she can also produce a valid authentication value corresponding to Bob's trusted credentials.

This is the beginning of **authenticated key exchange**, or AKE.

The important idea is not merely that a signature appears somewhere.

It is that the authentication mechanism is cryptographically bound to the **specific handshake being executed**.

This is often called **transcript binding**.

---

## Why the transcript matters

Imagine a protocol that authenticates only one isolated public value without binding enough surrounding context.

Values from one execution might potentially be:

- copied into another session,
- replayed,
- reflected,
- associated with the wrong identity,
- interpreted under different protocol parameters.

A transcript gives structure to the session.

For example:

$$
T
=
H(
\text{protocol}
\parallel
\text{Alice}
\parallel
\text{Bob}
\parallel
A
\parallel
B
\parallel
\text{parameters}
).
$$

Authentication can then bind the parties to

$$
T
$$

rather than to an isolated number.

This is a recurring design principle in modern cryptography:

$$
\boxed{
\text{authenticate the context, not merely a value}
}
$$

We will encounter the same principle again in:

- digital-signature protocols,
- TLS,
- zero-knowledge proofs,
- Fiat-Shamir transforms,
- threshold signatures,
- domain separation,
- distributed key generation.

---

## A modern example: TLS 1.3

TLS 1.3 gives us a useful architectural example.

We are **not** going to study the entire TLS handshake here, but its structure shows how real protocols separate several jobs that our toy exchange merged together.

Very approximately:

```text
(EC)DHE
   ↓
establish shared secret material

authentication
   ↓
authenticate the peer and handshake

transcript
   ↓
bind messages to this session

Finished messages
   ↓
confirm the completed handshake

HKDF key schedule
   ↓
derive traffic keys
```

The Diffie-Hellman component contributes ephemeral shared secret material.

Authentication mechanisms bind credentials to the handshake.

The transcript binds the exchanged messages together.

A key schedule derives separate cryptographic keys for specific purposes.

This is very different from the toy model:

```text
compute g^(ab)
       ↓
call it "the key"
       ↓
done
```

Real protocol security comes from composing several cryptographic mechanisms correctly.

That is why **protocol design is not simply a collection of secure primitives**.

A protocol may contain perfectly secure primitives and still be insecure if those primitives are connected incorrectly.

---

## What exactly failed?

It is useful to compare this attack with the previous one.

### Previous article: weak parameters

The adversary observes:

$$
A=g^a
$$

and recovers:

$$
a.
$$

The failure is:

$$
\boxed{
\text{the computational problem is too easy}
}
$$

because the group is tiny.

### This article: missing authentication

The adversary does not recover:

$$
a
$$

or

$$
b.
$$

Instead she substitutes:

$$
A\rightarrow E_B
$$

and

$$
B\rightarrow E_A.
$$

The failure is:

$$
\boxed{
\text{the protocol does not authenticate the peer}
}
$$

These are fundamentally different classes of failure.

We can summarize them as:

```text
mathematical correctness
        ↓
not enough

hard computational problem
        ↓
not enough

secure parameters
        ↓
not enough

authentication and protocol context
        ↓
required for authenticated communication
```

This is one of the most important transitions in learning cryptography.

At first it is natural to think:

> If the underlying mathematical problem is hard, the protocol must be secure.

But protocol security asks more questions:

- Who generated this value?
- Which session does it belong to?
- Has it been modified?
- Has it been replayed?
- Are the parties using the same transcript?
- Are the keys bound to the intended identities?
- Has the peer actually demonstrated possession of the corresponding secret?

Those questions cannot be answered by the discrete-logarithm assumption alone.

---

## Reproduce the attack

Run the experiment and print the different views explicitly:

```text
ALICE THINKS

peer   = Bob
shared = 6
```

```text
EVE KNOWS

with Alice = 6
with Bob   = 15
```

```text
BOB THINKS

peer   = Alice
shared = 15
```

Then answer these questions:

1. Did Eve solve a discrete logarithm?
2. Did any Diffie-Hellman equation fail?
3. Do Alice and Bob actually share the same value?
4. Why does Alice accept Eve's public value?
5. Why does Bob accept Eve's public value?
6. Why would using a much larger prime not prevent this attack?
7. Would switching to elliptic-curve Diffie-Hellman alone prevent it?
8. What additional property is missing from the protocol?

If those answers are clear, the important lesson has landed.

---

## Papers and standards

### Diffie and Hellman — the original key-agreement paper

**Whitfield Diffie and Martin E. Hellman**,  
*New Directions in Cryptography*,  
IEEE Transactions on Information Theory, 22(6), 1976.

The original paper is worth revisiting after seeing the difference between the mathematical key-agreement mechanism and the larger authentication problem.

### Station-to-Station protocol

**Whitfield Diffie, Paul C. van Oorschot, and Michael J. Wiener**,  
*Authentication and Authenticated Key Exchanges*,  
Designs, Codes and Cryptography, 2, 1992.

This is particularly relevant after this article because the Station-to-Station protocol was designed specifically to combine Diffie-Hellman-style key establishment with authentication.

### Bellare and Rogaway — formal key-exchange analysis

**Mihir Bellare and Phillip Rogaway**,  
*Entity Authentication and Key Distribution*,  
CRYPTO 1993.

This work is part of the development of formal models for reasoning about authentication and key establishment rather than relying only on informal protocol intuition.

### Canetti and Krawczyk — authenticated key exchange

**Ran Canetti and Hugo Krawczyk**,  
*Analysis of Key-Exchange Protocols and Their Use for Building Secure Channels*,  
EUROCRYPT 2001.

This is a useful bridge toward modern formal reasoning about authenticated key exchange and secure channels.

### SIGMA protocols

**Hugo Krawczyk**,  
*SIGMA: The 'SIGn-and-MAc' Approach to Authenticated Diffie-Hellman and Its Use in the IKE Protocols*,  
CRYPTO 2003.

SIGMA is particularly relevant to the design problem we have just encountered: how to authenticate Diffie-Hellman exchanges while correctly binding identities and session information.

### TLS 1.3

**Eric Rescorla**,  
*The Transport Layer Security (TLS) Protocol Version 1.3*,  
RFC 8446, 2018.

TLS 1.3 is an important real-world example of ephemeral key agreement, transcript authentication, key derivation, and handshake confirmation being composed into an authenticated secure channel.

---

## Next

We have now broken our Diffie-Hellman experiments in two completely different ways.

First:

```text
tiny group
    ↓
discrete logarithm becomes easy
    ↓
recover the secret exponent
```

Then:

```text
no authentication
    ↓
do not attack the discrete logarithm at all
    ↓
replace the public values
    ↓
create two independent sessions
```

Now suppose we fix both problems.

Assume:

- the discrete logarithm is hard,
- the peer is authenticated,
- the attacker cannot simply replace the handshake.

Can accepting the **wrong kind of group element** still leak information?

Yes.

If an implementation accepts a value from a small subgroup, the resulting shared value may lie in a tiny set.

Repeated interactions can then reveal information about a secret exponent.

That takes us from protocol authentication back into the internal structure of the group itself.

**Next: Small-Subgroup Attacks — When the Group Is Large but the Secret Leaks Through a Tiny Subgroup.**