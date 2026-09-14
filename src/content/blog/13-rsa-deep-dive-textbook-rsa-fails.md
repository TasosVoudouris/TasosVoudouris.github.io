---
title: 'RSA Deep Dive I: Why Textbook RSA Fails'
description: RSA's raw modular exponentiation is deterministic and multiplicatively malleable. We exploit both properties in a toy example, then see why secure RSA encryption needs randomized encoding such as OAEP.
pubDate: '2026-09-08'
topics:
- Public-Key Cryptography
- Cryptanalysis
tags:
- rsa
- textbook-rsa
- malleability
- chosen-ciphertext
- oaep
- cryptanalysis
- cryptography-from-zero
difficulty: Intermediate
series: RSA Deep Dives
seriesOrder: 1
draft: false
---
This is the first post where I want to change the pace of the series.

Up to now, we have been building the foundations almost linearly.

Now we have enough machinery to take one cryptosystem and stay with it until we understand not only how it works, but **how it fails**.

So this is the first RSA deep dive.

If any of the arithmetic below feels too fast, the earlier posts are now our reference layer:

- [modular inverses and Extended Euclid](/blog/02-extended-euclid-bezout-modular-inverse/),
- [fast modular exponentiation](/blog/08-fast-modular-exponentiation-side-channels/),
- [CRT](/blog/10-chinese-remainder-theorem/),
- [RSA key generation](/blog/12-rsa-key-generation/).

We do not need to rebuild those ideas every time.

We can use them.

And the first thing I want to attack is the most tempting version of RSA:

$$
c=m^e\bmod N.
$$

It is mathematically correct.

It is also **not a secure encryption scheme**.

![Why textbook RSA fails](/images/blog/13-textbook-rsa-fails.svg)

*The raw RSA map is deterministic and multiplicatively malleable. OAEP inserts randomized structured encoding before the RSA primitive.*

---

## Break 1: encryption is deterministic

Reuse the toy key from the previous post:

$$
N=3233,
\qquad
e=17,
\qquad
d=413.
$$

Take:

$$
m=42.
$$

Textbook RSA encryption gives:

$$
c=42^{17}\bmod3233=2557.
$$

Now encrypt $42$ again.

We get:

$$
2557.
$$

And again:

$$
2557.
$$

There is no fresh randomness anywhere in:

$$
c=m^e\bmod N.
$$

So the mapping is deterministic:

$$
m\longmapsto c.
$$

In code:

```python
def textbook_rsa_encrypt(m, e, n):
    return pow(m, e, n)


c1 = textbook_rsa_encrypt(42, 17, 3233)
c2 = textbook_rsa_encrypt(42, 17, 3233)

assert c1 == c2 == 2557
```

Why is that a security problem?

Suppose an attacker knows the message comes from a tiny set:

```text
YES
NO
```

or:

```text
0
1
```

or a small command dictionary.

The public key is public.

So the attacker can encrypt every candidate themselves:

```text
guess m0
→ compute m0^e mod N

guess m1
→ compute m1^e mod N

compare with observed ciphertext
```

The attacker does not need the private key.

They do not need to factor $N$.

They simply exploit equality.

This already destroys the privacy notion we expect from modern public-key encryption.

If the attacker chooses two distinct messages:

$$
m_0,\qquad m_1
$$

and receives an encryption of one of them, they can compute both public encryptions and compare.

So textbook RSA cannot provide ordinary randomized encryption security.

The failure is not:

```text
RSA exponentiation is mathematically wrong
```

It is:

```text
the primitive exposes too much structure when used directly as encryption
```

---

## Break 2: RSA ciphertexts are multiplicatively malleable

The older notes I wrote on RSA called this its "multiplicative homomorphism."

The equation is correct:

$$
E(m_1m_2)
\equiv
E(m_1)E(m_2)
\pmod N.
$$

Because:

$$
(m_1m_2)^e
=
m_1^e m_2^e.
$$

But for **textbook encryption**, the first security lesson should not be:

> Great, RSA gives us homomorphic encryption.

The first lesson should be:

> An attacker can transform a ciphertext into a related ciphertext without knowing the plaintext.

That property is called **malleability**.

Let:

$$
c=m^e\bmod N.
$$

An attacker chooses some invertible multiplier:

$$
r\in\mathbb Z_N^\times.
$$

Because the public key is known, the attacker can compute:

$$
r^e\bmod N.
$$

Now construct:

$$
c'
=
c\cdot r^e
\bmod N.
$$

Substitute $c=m^e$:

$$
c'
=
m^e r^e
=
(mr)^e
\pmod N.
$$

Therefore, when the private key decrypts $c'$:

$$
(c')^d
\equiv
mr
\pmod N.
$$

The attacker changed the encrypted plaintext in a predictable algebraic way.

No decryption key was needed to create the modification.

That is malleability.

---

Let us make it concrete.

Use:

$$
m=42.
$$

We already have:

$$
c=2557.
$$

Choose:

$$
r=2.
$$

The attacker computes:

$$
2^{17}\bmod3233=1752.
$$

Then:

$$
c'
=
2557\cdot1752
\bmod3233
=
2159.
$$

The receiver decrypts:

$$
2159^{413}\bmod3233=84.
$$

And:

$$
84=42\cdot2.
$$

Exactly as predicted.

In Python:

```python
N = 3233
e = 17
d = 413

m = 42
r = 2

c = pow(m, e, N)

modified = (
    c * pow(r, e, N)
) % N

decrypted_modified = pow(
    modified,
    d,
    N,
)

print(c)                   # 2557
print(modified)            # 2159
print(decrypted_modified)  # 84

assert decrypted_modified == (m * r) % N
```

This is a much more useful way for me to remember RSA multiplicativity.

Not as an isolated algebraic curiosity.

As:

$$
\boxed{
\text{ciphertext algebra}
\rightarrow
\text{controlled plaintext algebra}.
}
$$

---

## Push it one step further: a textbook chosen-ciphertext break

Now suppose the attacker has access to some system that decrypts ciphertexts, but refuses to decrypt the exact target ciphertext $c$.

That sounds like a meaningful restriction.

With textbook RSA, it is not enough.

The attacker sends:

$$
c'
=
c\cdot r^e
\bmod N.
$$

Since:

$$
c'\neq c,
$$

the oracle may accept it.

The oracle returns:

$$
m'
=
mr\bmod N.
$$

If:

$$
\gcd(r,N)=1,
$$

then $r$ has an inverse.

So the attacker computes:

$$
r^{-1}\pmod N
$$

and recovers:

$$
m
=
m'r^{-1}
\bmod N.
$$

For our example:

$$
r=2.
$$

Its inverse modulo $3233$ is:

$$
2^{-1}\equiv1617\pmod{3233}.
$$

The oracle returned:

$$
m'=84.
$$

Therefore:

$$
84\cdot1617\bmod3233=42.
$$

The original plaintext is recovered.

In code:

```python
r_inverse = pow(r, -1, N)

recovered = (
    decrypted_modified * r_inverse
) % N

assert recovered == 42
```

Notice what we did **not** do:

- factor $3233$,
- recover $d$,
- attack modular exponentiation,
- exploit a side channel.

We attacked the **scheme design**.

Or more accurately: the lack of one.

Textbook RSA gives us a trapdoor arithmetic primitive.

It does not automatically give us chosen-ciphertext-secure encryption.

---

## So what is OAEP actually fixing?

This is where the word "padding" can be misleading.

It sounds cosmetic:

```text
message
+ some extra bytes
```

But secure encoding changes the cryptographic object that enters RSA.

PKCS #1 does not define RSA encryption as:

```text
message
→ RSA exponentiation
```

Instead, the model is:

```text
message
      ↓
randomized encoding
      ↓
encoded message representative
      ↓
RSAEP
      ↓
ciphertext
```

For RSAES-OAEP, fresh randomness participates in the encoding.

So encrypting the same message twice should produce different encoded representatives and therefore different ciphertexts.

Conceptually:

```text
same M + seed₁ → EM₁ → C₁
same M + seed₂ → EM₂ → C₂

C₁ ≠ C₂
```

That immediately removes the deterministic equality test we exploited above.

But OAEP is doing more than merely "adding randomness."

Its hash-and-mask structure defines how the message becomes a valid RSA representative, and decoding validates that structure.

So the correct lesson is:

> secure encoding is part of the encryption scheme, not formatting placed around RSA afterward.

PKCS #1 v2.2 specifies two RSA encryption schemes:

- RSAES-OAEP,
- legacy RSAES-PKCS1-v1_5.

For new applications, the specification requires support for RSAES-OAEP and retains PKCS #1 v1.5 for compatibility.

**Reference:** [RFC 8017 — PKCS #1 v2.2](https://www.rfc-editor.org/rfc/rfc8017)

OAEP comes from Bellare and Rogaway's work on combining trapdoor permutations with randomized encoding:

**Mihir Bellare and Phillip Rogaway, _Optimal Asymmetric Encryption_, EUROCRYPT '94.**

[DOI: 10.1007/BFb0053428](https://doi.org/10.1007/BFb0053428)

---

### One thing I do not want to oversimplify

I do not want this post to end with:

> "Use OAEP and RSA is solved."

That would repeat the same mistake at a higher level.

The security history of OAEP is more nuanced than that slogan.

And even a sound encoding construction can become vulnerable if the implementation reveals information through decoding failures.

We already saw the general pattern:

```text
mathematics
+
implementation behavior
=
actual attack surface
```

This becomes extremely important in RSA.

Bleichenbacher's attack against PKCS #1 v1.5 and Manger's attack against vulnerable OAEP decoding behavior are both examples of tiny validity signals becoming powerful chosen-ciphertext oracles.

We will give those attacks their own deep dives rather than compress them into one paragraph here.

---

## RSA is also not a bulk-data cipher

There is one more old habit worth correcting.

Even with OAEP, RSA is not the natural tool for encrypting a large file block by block.

For a $2048$-bit RSA modulus with SHA-256, OAEP can encode at most:

$$
256-2(32)-2
=
190
$$

message bytes.

That number comes from the OAEP encoding bound:

$$
m_{\max}=k-2h-2.
$$

But the deeper systems lesson is not:

> split a file into 190-byte pieces and RSA-encrypt every piece.

The usual architecture is closer to:

```text
public-key mechanism
      ↓
protect / establish compact secret material
      ↓
KDF / key schedule
      ↓
symmetric AEAD for actual data
```

Public-key crypto solves the key-establishment problem.

Fast symmetric authenticated encryption handles the data.

This separation will become even more important when we later reach KEM–DEM and post-quantum KEMs.

---

## What from the old CryptoCave survives here?

Quite a lot.

The old RSA notes already had the correct algebra:

$$
E(m_1m_2)
=
E(m_1)E(m_2)
\pmod N.
$$

They also ended with the right warning:

```text
never use raw textbook RSA for encryption
```

What changes in this version is the interpretation.

Instead of presenting multiplicativity primarily as a useful "homomorphic encryption" property, we place it where it belongs for this topic:

```text
textbook RSA encryption
      ↓
algebraic malleability
      ↓
chosen-ciphertext failure
```

The algebra stayed.

Our understanding of what it means became sharper.

That is exactly why I wanted these Deep Dive posts.

---

Run the companion demo:

```powershell
python chapters/13_rsa_textbook_failures/demo.py
```

It performs both failures:

```text
1. same message encrypted twice
   → same ciphertext

2. modify c with r^e
   → receiver decrypts m*r
   → invert r
   → recover original m
```

The demo is deliberately toy-only.

It is there to expose the algebra, not to attack deployed RSA systems.

---

At this point we have established the first layer of the RSA attack map:

```text
TEXTBOOK RSA
├── deterministic
│   └── equality / dictionary attacks
│
└── multiplicatively malleable
    └── algebraic chosen-ciphertext attack
```

Now we can move to failures where the encoding itself is no longer the main problem.

Suppose several users use RSA correctly as modular arithmetic, but they accidentally reuse the **same modulus** with different public exponents.

If the same message is encrypted under both keys and the exponents are coprime, Extended Euclid can recover the plaintext without factoring $N$.

That is exactly where our very first Bézout identity comes back.

**Next RSA Deep Dive:** *The Common-Modulus Attack: Recovering an RSA Message With Bézout Instead of Factoring.*
