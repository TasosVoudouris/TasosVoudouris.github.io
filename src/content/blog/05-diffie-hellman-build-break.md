---
title: "Diffie-Hellman From Scratch: Build It, Share a Secret, Then Break the Toy Version"
description: "A complete toy Diffie-Hellman exchange from the group algebra to the shared secret, followed immediately by a brute-force discrete-log attack that shows why parameters matter."
pubDate: "2026-09-08"
category: "Public-Key Cryptography"
tags:
  - diffie-hellman
  - key-exchange
  - discrete-logarithm
  - groups
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

This is the first post in the series where I feel we can finally say:

> We are building a cryptographic protocol.

Not a helper function. Not a number-theory identity. A protocol.

Two people will communicate over a public channel and end up with the same secret value without ever sending that final secret directly.

That idea is still remarkable to me even after seeing Diffie-Hellman many times.

And because the whole purpose of this project is not to treat cryptography as a black box, I want to do two things in the same post:

```text
BUILD the protocol
        ↓
prove why it works
        ↓
BREAK the tiny version
```

The break is just as important as the build.

A protocol can be mathematically correct and still be completely insecure if the parameters make the hard problem easy.

![Toy Diffie-Hellman exchange and brute-force attack](/images/blog/05-diffie-hellman-build-break.svg)

*Alice and Bob derive the same group element. Eve sees the public values. With tiny parameters, she can simply search the exponent space.*

---

## Build: how can two people compute the same secret?

From the previous post we already have the right language.

Let

$$
G=\langle g
angle
$$

be a cyclic group of order $q$.

Alice secretly chooses an exponent:

$$
a\in\mathbb Z_q.
$$

She computes:

$$
A=g^a
$$

and sends $A$ publicly.

Bob independently chooses:

$$
b\in\mathbb Z_q,
$$

computes:

$$
B=g^b,
$$

and sends $B$.

Everything sent across the channel is public:

```text
group parameters
g
A = g^a
B = g^b
```

The secret exponents `a` and `b` stay private.

Now Alice receives $B$ and computes:

$$
Z_A=B^a.
$$

Bob receives $A$ and computes:

$$
Z_B=A^b.
$$

Why should these be equal?

Because:

$$
B^a=(g^b)^a=g^{ba},
$$

while:

$$
A^b=(g^a)^b=g^{ab}.
$$

And since integer multiplication satisfies $ab=ba$, both sides obtain:

$$
oxed{Z_A=Z_B=g^{ab}.}
$$

That is the entire correctness argument.

The agreement is not a lucky accident of the numbers we choose. It follows from the group operation.

What I find useful here is to separate two questions that are easy to mix together:

> **Correctness:** Why do Alice and Bob get the same value?
>
> **Security:** Why should somebody who sees $g$, $g^a$, and $g^b$ be unable to recover the secret?

The group algebra answers the first question. A computational hardness assumption is needed for the second.

Let us make everything tiny enough that we can inspect every number.

Use:

$$
p=23,\qquad g=5.
$$

We work inside the multiplicative group modulo $23$.

Alice chooses:

$$
a=6.
$$

Bob chooses:

$$
b=15.
$$

Alice's public value is:

$$
A=5^6mod23=8.
$$

Bob's public value is:

$$
B=5^{15}mod23=19.
$$

Now Alice computes:

$$
Z_A=19^6mod23=2.
$$

Bob computes:

$$
Z_B=8^{15}mod23=2.
$$

So:

$$
oxed{Z_A=Z_B=2.}
$$

In Python:

```python
p = 23
g = 5

alice_secret = 6
bob_secret = 15

A = pow(g, alice_secret, p)
B = pow(g, bob_secret, p)

alice_shared = pow(B, alice_secret, p)
bob_shared = pow(A, bob_secret, p)

print(A)             # 8
print(B)             # 19
print(alice_shared)  # 2
print(bob_shared)    # 2

assert alice_shared == bob_shared
```

That is a complete toy Diffie-Hellman exchange.

And at this point, if I only showed the code, it would be very tempting to think:

> Great. Alice and Bob have a shared secret. Done.

But now we should look at the same protocol from Eve's side.

---

## Break: the tiny discrete logarithm is not hard at all

Eve sees:

$$
p=23,\quad g=5,\quad A=8,\quad B=19.
$$

She does not know $a=6$ or $b=15$.

The problem of recovering $a$ from

$$
A=g^a
$$

is a **discrete logarithm problem**.

In our example:

$$
5^a\equiv8\pmod{23}.
$$

For real cryptographic parameters, we want this problem to be computationally infeasible.

But our group is tiny, so Eve can just try every exponent:

```python
def brute_force_discrete_log(g, target, p):
    for candidate in range(p - 1):
        if pow(g, candidate, p) == target:
            return candidate

    return None
```

Run:

```python
recovered_a = brute_force_discrete_log(
    g=5,
    target=8,
    p=23,
)

print(recovered_a)
```

and we obtain:

```text
6
```

Alice's secret exponent is recovered.

Now Eve computes:

```python
recovered_shared = pow(B, recovered_a, p)
```

and gets:

```text
2
```

The exact same shared value Alice and Bob computed.

So our protocol is:

```text
mathematically correct   ✓
cryptographically secure ✗
```

And that distinction is one of the most important things I want to keep repeating in this series.

### What exactly did we break?

We did **not** discover some flaw in the Diffie-Hellman algebra.

The equality

$$
B^a=A^b=g^{ab}
$$

still holds perfectly.

What failed was the assumption that recovering the exponent should be hard.

Our search space is tiny.

For this toy group, looping over every possible exponent takes essentially no effort.

So increasing the size of the secret integer alone is not enough. The actual subgroup in which $g$ lives must have appropriately large order, and the representation must resist known discrete-log algorithms.

This is why the previous post spent time distinguishing:

```text
modulus size
group order
element order
generated subgroup
```

Those were not abstract-algebra decorations. They are already part of the security story.

The older notes I wrote on this topic eventually go much further into baby-step–giant-step, Pollard rho, Pohlig-Hellman, safe-prime groups, subgroup validation, and man-in-the-middle attacks.

We are not going there all at once.

For now the important lesson is simpler:

> "The exponent is hidden" is not a mathematical fact. It is a computational claim whose truth depends on the group and its parameters.

---

## One more correction: the shared group element is not yet a session key

There is another simplification in our toy code.

We called

$$
Z=g^{ab}
$$

the "shared secret."

That is fine while learning the algebra.

But in a real protocol we normally do **not** take the raw encoded group element and use it directly as an AES key.

Instead, the agreed secret material is processed through an appropriate key-derivation step together with protocol context.

Conceptually:

```text
Diffie-Hellman shared value Z
        ↓
KDF + transcript/context
        ↓
actual symmetric keying material
```

We will come back to that when we start composing primitives into complete protocols.

For the moment, it is enough to keep the terminology precise:

> Diffie-Hellman is a **key-agreement mechanism**, not bulk encryption by itself.

The original public paper is still worth reading here:

**Whitfield Diffie and Martin E. Hellman, "New Directions in Cryptography," IEEE Transactions on Information Theory, 22(6), 644–654, 1976.**

[Read the original paper from Stanford](https://ee.stanford.edu/~hellman/publications/24.pdf)

What I like about reading it at this point in the series is that we now have enough mathematical vocabulary to recognize what is happening instead of simply admiring the final formula.

Run the companion toy-DH material from the repository and reproduce this sequence:

```text
1. choose tiny p and g
2. choose secret a and b
3. compute A and B
4. verify both shared values match
5. give Eve only p, g, A, B
6. brute-force one exponent
7. recover the shared value
```

Try changing Alice's secret. Try changing Bob's secret. Then try a different small prime.

The point is to develop the attacker mindset:

> What information is public?  
> What information is supposed to remain hidden?  
> What computational problem separates the two?

There is still a much more serious problem with the protocol we just built.

Suppose Eve does **not** try to solve the discrete logarithm at all.

Suppose instead she stands between Alice and Bob and replaces their public values.

Alice may establish a secret with Eve. Bob may establish a different secret with Eve. Both computations can be perfectly valid Diffie-Hellman sessions.

The problem is that neither side knows **who** is actually on the other end.

That is the first protocol-level attack in the series.

**Next:** *Breaking Diffie-Hellman Without Solving the Discrete Log: The Man-in-the-Middle Attack.*
