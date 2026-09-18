---
title: "Hash Functions: A Primer"
description: "A rigorous practical introduction to cryptographic hash functions, their security properties, generic attack costs, Python usage, avalanche behavior, and deliberately weak constructions that show why preimage, second-preimage, and collision resistance are distinct."
pubDate: "2025-04-19"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptographic Engineering"
tags:
  - "hash-functions"
  - "sha256"
  - "sha3"
  - "sha1"
  - "md5"
  - "preimage-resistance"
  - "second-preimage-resistance"
  - "collision-resistance"
  - "birthday-bound"
  - "avalanche-effect"
difficulty: "Introductory"
series: "Hash Functions & MACs"
seriesOrder: 1
draft: false
---

## Table of Contents

- [What a Cryptographic Hash Function Is](#what-a-cryptographic-hash-function-is)
- [The Three Core Security Properties](#the-three-core-security-properties)
- [Practical Hashing with Python](#practical-hashing-with-python)
- [Learning from Deliberately Weak Constructions](#learning-from-deliberately-weak-constructions)
- [Collisions, the Birthday Bound, and Broken Hashes](#collisions-the-birthday-bound-and-broken-hashes)
- [Engineering Lessons and Common Misconceptions](#engineering-lessons-and-common-misconceptions)
- [Conclusion](#conclusion)
- [References](#references)

---

## What a Cryptographic Hash Function Is

A cryptographic hash function maps a message of arbitrary practical length to a fixed-length digest.

For an \(n\)-bit hash function we write

\[
H:\{0,1\}^{*}\rightarrow\{0,1\}^{n},
\]

where

\[
\{0,1\}^{*}
\]

denotes all finite bit strings and

\[
\{0,1\}^{n}
\]

is the set of all \(n\)-bit outputs.

For SHA-256,

\[
n=256.
\]

Thus SHA-256 always returns exactly

\[
256\text{ bits}=32\text{ bytes},
\]

whether the input is:

```text
A
```

or

```text
a multi-gigabyte file
```

or a long protocol transcript.

This compression property immediately gives us one important mathematical fact:

> **Collisions must exist.**

The domain is vastly larger than the codomain. By the pigeonhole principle, many different inputs must map to the same digest.

Therefore collision resistance never means

> "two different messages cannot have the same hash."

That would be impossible for a fixed-length hash with an unrestricted input domain.

Instead, the cryptographic requirement is computational:

> it should be infeasible to **find** such a pair.

That distinction between mathematical existence and computational feasibility is one of the central ideas in modern cryptography.

### Hashing is deterministic

A cryptographic hash function has no ordinary secret key.

For the same exact input bytes,

\[
H(M)=H(M)
\]

every time.

For example,

```python
import hashlib

assert (
    hashlib.sha256(b"Hello").digest()
    ==
    hashlib.sha256(b"Hello").digest()
)
```

This determinism is useful for:

- integrity checks,
- digital signatures,
- commitment-like constructions,
- Merkle trees,
- content addressing,
- key derivation building blocks,
- MAC constructions such as HMAC,
- many zero-knowledge and proof-system components.

But determinism also means that an ordinary hash is **not encryption**. There is no decryption key and no expectation that the original message can be reconstructed from the digest.

### Fixed output does not mean fixed security for every property

An \(n\)-bit digest does not automatically imply \(n\)-bit resistance to every attack.

For an ideal \(n\)-bit hash:

\[
\text{preimage work}\approx 2^n,
\]

\[
\text{second-preimage work}\approx 2^n,
\]

but generic collision search requires only about

\[
2^{n/2}
\]

hash evaluations because of the birthday phenomenon.

For SHA-256, the idealized generic scales are therefore roughly:

\[
2^{256}
\]

for preimage search and

\[
2^{128}
\]

for collision search.

This is why a 256-bit digest is commonly associated with about 128 bits of generic collision security rather than 256 bits.

### Hash functions, checksums, MACs, and encryption are different objects

These terms are often mixed together:

**Checksum.** Designed primarily to detect accidental errors. It may be easy for an adversary to manipulate.

**Cryptographic hash.** Unkeyed deterministic function designed to provide strong preimage and collision properties.

**MAC.** A keyed authenticator. Only someone with the secret key should be able to generate a valid tag.

**Encryption.** Protects plaintext confidentiality and is normally reversible with the correct key.

A plain hash does **not** authenticate a message against an active attacker if the attacker is free to modify both the message and the hash value stored beside it.

For example:

```text
message || SHA256(message)
```

can detect accidental corruption when the digest is trusted independently.

But if an attacker can replace both fields, they can simply compute:

```text
modified_message || SHA256(modified_message)
```

No cryptographic hash property prevents that.

This distinction prepares the way for HMAC later in this series.

---

## The Three Core Security Properties

The classical security properties are:

1. preimage resistance,
2. second-preimage resistance,
3. collision resistance.

They are related, but they are not interchangeable.

### Preimage resistance

Given a target digest

\[
y,
\]

it should be computationally infeasible to find **any** message \(x\) such that

\[
H(x)=y.
\]

Formally, the adversary receives \(y\) and wants:

\[
x\leftarrow H^{-1}(y).
\]

For an ideal \(n\)-bit hash, generic exhaustive search requires approximately

\[
2^n
\]

trials in the worst-order sense, with the exact expected work depending on the search model and target distribution.

The key point is that the target digest is fixed **before** the search.

### Second-preimage resistance

Here the attacker is given a particular message \(x\) and must find a different message

\[
x'\neq x
\]

such that

\[
H(x')=H(x).
\]

The challenge is:

\[
x
\longrightarrow
\text{find }x'\neq x
\text{ with equal digest}.
\]

For an ideal fixed-length hash, the generic scale is again about

\[
2^n.
\]

This property matters when one specific committed or signed object already exists.

Imagine a signed document \(M\) whose signature covers

\[
H(M).
\]

If an attacker could cheaply construct a different document \(M'\) satisfying

\[
H(M')=H(M),
\]

the same digest would represent two different contents.

### Collision resistance

For collision resistance, the attacker is free to choose **both** inputs.

The goal is to find

\[
x\neq x'
\]

such that

\[
H(x)=H(x').
\]

This freedom makes generic collision search much easier than preimage search.

For an ideal \(n\)-bit function, a collision appears after roughly

\[
2^{n/2}
\]

samples rather than \(2^n\).

### The differences at a glance

| Property | Given to attacker | Goal | Ideal generic scale for \(n\)-bit hash |
|---|---|---|---:|
| Preimage | digest \(y\) | find \(x\) with \(H(x)=y\) | \(2^n\) |
| Second preimage | message \(x\) | find \(x'\neq x\) with \(H(x')=H(x)\) | \(2^n\) |
| Collision | nothing fixed | find any \(x\neq x'\) with equal digest | \(2^{n/2}\) |

The distinction is easier to remember in question form:

```text
Preimage:
"Given the output, can I find an input?"

Second preimage:
"Given this exact input, can I find another input with the same output?"

Collision:
"Can I choose two different inputs that collide?"
```

### Why one broken property does not automatically imply every other property is broken equally

MD5 is the classic example.

MD5's collision resistance is practically broken. But that does not mean that given an arbitrary 128-bit MD5 value, one can instantly recover a corresponding message.

Collision attacks and preimage attacks solve different computational problems.

That is why security discussions should say precisely which property has failed instead of simply saying:

> "the hash is reversible."

For most cryptographic hashes, collision weakness does not imply literal efficient inversion.

### Avalanche behavior

A desirable cryptographic hash exhibits strong diffusion: changing one input bit should cause a complicated-looking change across the digest.

A common experiment is:

```python
import hashlib

m1 = b"Hash functions are interesting."
m2 = b"hash functions are interesting."

h1 = hashlib.sha256(m1).digest()
h2 = hashlib.sha256(m2).digest()

distance = sum(
    (a ^ b).bit_count()
    for a, b in zip(h1, h2)
)

print(distance)
```

For a 256-bit digest, unrelated-looking outputs often differ in roughly half the positions.

This is associated with the **avalanche effect**.

But avalanche behavior is not a replacement for the three formal properties above.

A deliberately bad function can exhibit dramatic-looking output changes while still having exploitable collisions or structural weaknesses.

Visual randomness is not a security proof.

---

## Practical Hashing with Python

Python's standard `hashlib` module gives a compact way to study real hash functions.

### MD5

```python
import hashlib

msg = b"Hello"

digest = hashlib.md5(msg).digest()

print(digest)
print(digest.hex())
```

Output:

```text
b"\x8b\x1a\x99S\xc4a\x12\x96\xa8'\xab\xf8\xc4x\x04\xd7"
8b1a9953c4611296a827abf8c47804d7
```

MD5 returns:

\[
128\text{ bits}=16\text{ bytes}.
\]

MD5 is retained here because it is historically important and useful for studying failures. It should not be selected for new cryptographic applications that require collision resistance.

### SHA-1

```python
import hashlib

msg = b"Hello"

digest = hashlib.sha1(msg).hexdigest()

print(digest)
```

Output:

```text
f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0
```

SHA-1 returns:

\[
160\text{ bits}=20\text{ bytes}.
\]

SHA-1 is also no longer an appropriate choice for new collision-resistant applications.

### SHA-256

```python
import hashlib

msg = b"Hello"

digest = hashlib.sha256(msg).hexdigest()

print(digest)
```

Output:

```text
185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969
```

SHA-256 returns:

\[
256\text{ bits}=32\text{ bytes}.
\]

### SHA-3

Python also exposes the standardized SHA-3 family:

```python
import hashlib

msg = b"Hello"

print(hashlib.sha3_256(msg).hexdigest())
```

SHA3-256 also returns 256 bits, but SHA-256 and SHA3-256 are not the same algorithm.

They come from different design families:

- SHA-256 belongs to the SHA-2 family and uses an iterative compression-function structure;
- SHA3-256 is based on Keccak and a permutation-based sponge construction.

The identical digest length does not make the constructions interchangeable internally.

### Output lengths

```python
import hashlib

msg = b"Hello"

assert len(hashlib.md5(msg).digest()) == 16
assert len(hashlib.sha1(msg).digest()) == 20
assert len(hashlib.sha256(msg).digest()) == 32
assert len(hashlib.sha512(msg).digest()) == 64
assert len(hashlib.sha3_256(msg).digest()) == 32
assert len(hashlib.sha3_512(msg).digest()) == 64
```

A useful table is:

| Algorithm | Digest length |
|---|---:|
| MD5 | 128 bits |
| SHA-1 | 160 bits |
| SHA-224 | 224 bits |
| SHA-256 | 256 bits |
| SHA-384 | 384 bits |
| SHA-512 | 512 bits |
| SHA3-256 | 256 bits |
| SHA3-512 | 512 bits |

Output length alone does not establish security. MD5 demonstrates this perfectly: a 128-bit output does not rescue a construction whose collision resistance has been cryptanalytically broken.

### `digest()` vs `hexdigest()`

These functions return the same digest in different encodings.

```python
h = hashlib.sha256(b"Hello")

raw = h.digest()
text = h.hexdigest()

print(len(raw))   # 32 bytes
print(len(text))  # 64 hexadecimal characters
```

Each byte requires two hexadecimal characters, so a 32-byte digest becomes a 64-character hex string.

The hexadecimal string is a representation of the digest, not a different hash value.

### Strings must become bytes

Hash functions operate on bytes.

```python
message = "Hello"

digest = hashlib.sha256(
    message.encode("utf-8")
).hexdigest()
```

Encoding is part of the input definition.

These two strings may look similar to a human while producing different bytes under different normalization or encoding rules.

Protocols must therefore define the exact byte serialization that is hashed.

### Streaming large files

A file does not need to be loaded fully into memory.

```python
import hashlib

def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)

    return h.hexdigest()
```

The incremental API computes exactly the same SHA-256 digest as hashing the concatenation of all chunks at once.

This is possible because real hash functions are designed to process long messages incrementally.

### A filename is not file content

If we compute:

```python
with open("report.pdf", "rb") as f:
    h = hashlib.sha256(f.read()).hexdigest()
```

the hash depends on the bytes **inside** `report.pdf`.

Renaming:

```text
report.pdf
```

to:

```text
final.pdf
```

without changing the file bytes does not change the digest.

Likewise, merely changing a filename extension does not transform the file contents.

Actually converting a JPEG to PNG does change the underlying bytes and therefore changes the digest.

### Current algorithm choices

For new general-purpose cryptographic hashing, SHA-2 and SHA-3 family functions are the mainstream standardized choices.

SHA-1 remains historically important, but NIST has announced a transition away from SHA-1 for all applications, with the transition target ending on December 31, 2030.

MD5 remains useful for historical study and some non-adversarial error-detection contexts, but it is not suitable where collision resistance is a security requirement.

The phrase "MD5 is broken" should therefore be read precisely as:

> its cryptographic collision resistance is broken strongly enough that it should not be used for new security constructions requiring that property.

---

## Learning from Deliberately Weak Constructions

The original primer contained several deliberately weak examples. They are pedagogically useful, but they also reveal another important lesson:

> Some "toy hash functions" fail so early that they do not even satisfy the structural definition of a modern fixed-output hash function.

We keep the examples, but classify them precisely.

### An invertible affine transformation

Consider:

\[
H(x)=ax+b.
\]

If \(a\neq0\), then:

\[
x=\frac{H(x)-b}{a}.
\]

So the map is directly invertible.

Using:

```python
def H(x, a, b):
    return a * x + b

def reverse_H(h, a, b):
    return (h - b) // a

a = 11
b = -977
x = 1337

h = H(x, a, b)
x_recovered = reverse_H(h, a, b)

print(h)
print(x_recovered)
```

we get:

```text
13730
1337
```

This demonstrates lack of preimage resistance.

But there is an even more basic issue.

As written,

\[
H(x)=ax+b
\]

does **not** have fixed-length output. Its output magnitude grows with \(x\).

So this is better described as an **invertible toy transformation** than as a proper cryptographic hash function.

That makes the example more useful, not less: it teaches us that "hard to reverse" is not the only requirement. A cryptographic hash first needs the right function shape.

### Caesar encryption pretending to be a hash

Suppose we define:

\[
H(x)=\operatorname{CaesarEncrypt}_{17}(x).
\]

Then:

```text
a     -> r
lower -> cfnvi
```

Given:

```text
cfnvi
```

we can simply apply the inverse Caesar shift and recover:

```text
lower
```

Therefore the map is not preimage resistant.

Again, the construction also fails the structural hash definition: output length equals input length.

A Caesar cipher is a reversible permutation over text symbols, not a compression function.

This gives a clean conceptual separation:

```text
encryption:
    reversible with key

hashing:
    compressing, deterministic, no decryption operation
```

### An order-independent character-sum checksum

Now consider:

\[
H(x)=\sum_{c\in x}\operatorname{ord}(c).
\]

For `"hello"`:

\[
104+101+108+108+111=532.
\]

So:

\[
H(\text{"hello"})=532.
\]

Any permutation of the characters gives the same value:

\[
H(\text{"hello"})
=
H(\text{"ehllo"})
=
H(\text{"helol"}).
\]

The original example also uses a completely different string:

```text
kbqgA.
```

whose character codes also sum to 532.

This immediately destroys second-preimage resistance.

```python
def H(x):
    return sum(ord(c) for c in x)

assert H("hello") == 532
assert H("ehllo") == 532
assert H("helol") == 532
assert H("kbqgA.") == 532
```

The same phenomenon appears with:

```python
x1 = "crypto"
x2 = "crptoy"
x3 = "ytcopr"

assert H(x1) == H(x2) == H(x3)
```

all producing:

```text
0x2a1
```

This construction is fundamentally order-insensitive because addition is commutative.

If a hash is intended to distinguish:

```text
ABC
```

from:

```text
CBA
```

then simply summing independent character contributions cannot work.

There is again a structural caveat: the raw sum is not fixed-length as message length grows.

We can force fixed length, for example:

\[
H_{16}(x)
=
\left(
\sum_{c\in x}\operatorname{ord}(c)
\right)
\bmod 2^{16},
\]

but that makes the function only more obviously collision-prone; it does not repair the cryptographic design.

### Bytewise AND with a constant

Consider the transformation:

\[
H(x)=x\;\&\;0xAD
\]

applied independently to each byte.

For:

```python
def H(x):
    return bytes(
        b & 0xAD
        for b in x
    )

x = b"f1nd_m3"

print(H(x))
```

the output is:

```text
b'$!,$\r-!'
```

The mapping discards every input bit corresponding to a zero bit in:

```text
0xAD = 10101101₂
```

Many distinct bytes therefore map to the same output byte.

The original second preimage is:

```python
x1 = b"f1nd_m3"
x2 = b"vs~v_\x7fs"

assert x1 != x2
assert H(x1) == H(x2)
```

Both map to:

```text
b'$!,$\r-!'
```

This shows extreme second-preimage weakness.

But, like the Caesar example, this transformation preserves message length. It is not a fixed-output hash function.

The broader lesson is that **local lossy operations are not enough**. A secure hash must spread dependencies globally across the internal state rather than process every byte independently with the same trivial map.

### What these examples teach together

These toy constructions fail for different reasons:

| Construction | Main failure |
|---|---|
| \(ax+b\) | directly invertible; not fixed-output |
| Caesar transform | reversible; not compressing |
| character sum | order independent; trivial second preimages; not fixed-output |
| bytewise AND | discards independent bits; trivial second preimages; not fixed-output |

This is a stronger pedagogical conclusion than simply labeling them all "bad hashes."

Before asking whether a function has 128-bit or 256-bit security, we should ask whether its structure even resembles a cryptographic hash construction.

---

## Collisions, the Birthday Bound, and Broken Hashes

Collision resistance is where output size and probability interact most visibly.

### Why collisions appear after about \(2^{n/2}\) samples

Suppose a hash has \(N=2^n\) possible outputs and we hash \(q\) independently distributed messages.

The probability of **no collision** is approximately:

\[
\Pr[\text{no collision}]
\approx
\exp\left(
-\frac{q(q-1)}{2N}
\right).
\]

Therefore the collision probability is approximately:

\[
\Pr[\text{collision}]
\approx
1-
\exp\left(
-\frac{q(q-1)}{2N}
\right).
\]

The probability becomes substantial when:

\[
q^2
\approx
N,
\]

so:

\[
q
\approx
\sqrt{N}
=
2^{n/2}.
\]

More precisely, a collision probability near one half appears around:

\[
q
\approx
\sqrt{
2N\ln 2
}
\approx
1.1774\cdot 2^{n/2}.
\]

For a 16-bit digest:

\[
2^{16}=65536
\]

possible values, and the 50% collision scale is only about:

\[
1.1774\cdot2^8
\approx
301
\]

samples.

That is why a two-byte truncated digest is so easy to collide.

### A true fixed-output toy: two-byte truncated MD5

Define:

```python
import hashlib

def H(x):
    return hashlib.md5(x).digest()[:2]
```

The output space contains only:

\[
2^{16}
\]

possible digests.

A generic collision search is:

```python
import hashlib

def H(x):
    return hashlib.md5(x).digest()[:2]

hashes_seen = {}

i = 0

while True:
    candidate = f"input_{i}".encode()
    current_hash = H(candidate)

    if current_hash in hashes_seen:
        previous_input = hashes_seen[current_hash]

        print("Collision Found!")
        print("Hash:", current_hash.hex())
        print("Input 1:", previous_input)
        print("Input 2:", candidate)

        break

    hashes_seen[current_hash] = candidate
    i += 1
```

With this deterministic sequence, the first collision is:

```text
H(b"input_105") = f064
H(b"input_323") = f064
```

so:

\[
H(\texttt{input\_105})
=
H(\texttt{input\_323}).
\]

The search needs only a few hundred messages, exactly the scale predicted by the birthday bound.

### The important correction: this demonstration is mainly about truncation

MD5 itself has serious collision weaknesses.

But the experiment above should **not** be interpreted as:

> "We broke MD5 in 323 trials."

We deliberately reduced the digest to only 16 bits.

The same generic birthday phenomenon occurs if we truncate a modern hash.

For example:

```python
import hashlib

def H16_SHA256(x):
    return hashlib.sha256(x).digest()[:2]
```

The sequential inputs:

```text
input_135
input_473
```

already satisfy:

```text
H16_SHA256(input_135)
=
H16_SHA256(input_473)
=
ae85
```

This does **not** demonstrate a weakness in SHA-256.

It demonstrates that a 16-bit digest has only 16-bit output space and therefore roughly 8-bit generic collision security.

This is one of the cleanest examples of why digest truncation must be analyzed quantitatively.

### Real MD5 collision resistance is broken

Separate from the truncation experiment, real full-length MD5 collisions have been demonstrated.

The repository contains a classic visual collision example:

| Plane | Ship |
|---|---|
| ![Plane](/images/ready/hash-functions-primer/plane.jpg) | ![Ship](/images/ready/hash-functions-primer/ship.jpg) |

The two files are distinct but the original experiment records the same MD5 digest:

```text
plane hash: 253dd04e87492e4fc3471de5e776bc3d
ship hash:  253dd04e87492e4fc3471de5e776bc3d
```

The intended check is:

```python
import hashlib

with open("plane.jpg", "rb") as f:
    plane_hash = hashlib.md5(
        f.read()
    ).hexdigest()

with open("ship.jpg", "rb") as f:
    ship_hash = hashlib.md5(
        f.read()
    ).hexdigest()

print("plane:", plane_hash)
print("ship :", ship_hash)

assert plane_hash == ship_hash
```

This is a qualitatively different phenomenon from merely truncating MD5.

Here the complete 128-bit MD5 outputs collide.

That is why MD5 should not be used in new constructions where collision resistance is a security requirement.

### Collision attacks are not preimage attacks

Suppose an attacker can efficiently generate a pair:

\[
M\neq M'
\]

with:

\[
H(M)=H(M').
\]

That does not mean the attacker can take an arbitrary target digest:

\[
y
\]

and efficiently solve:

\[
H(x)=y.
\]

The first is a collision problem.

The second is a preimage problem.

Cryptanalytic results should always be classified according to the property they actually break.

---

## Engineering Lessons and Common Misconceptions

The introductory examples now give us enough material to correct several recurring misconceptions.

### "A hash uniquely identifies every message"

Not mathematically.

A fixed-size hash has fewer outputs than possible messages, so collisions necessarily exist.

A secure hash aims to make those collisions computationally difficult to find.

### "Hashing is encryption without a decryption function"

Not really.

Encryption is designed as a keyed reversible transformation.

Hashing is designed as an unkeyed compression function with computational one-way and collision properties.

The constructions, interfaces, and security goals are different.

### "If the output looks random, the function is secure"

No.

Security is evaluated by attack models and measurable properties.

A function can create visually chaotic output and still contain an exploitable structural weakness.

Avalanche behavior is desirable, but it is not a substitute for cryptanalysis.

### "A longer digest is automatically a better hash"

Not by itself.

Output size places an upper bound on generic attack complexity, but the construction must still resist structural attacks.

MD5 and SHA-1 are examples where cryptanalysis beats the ideal collision-security expectation substantially.

### "SHA-256 and SHA3-256 are basically the same"

They both output 256 bits, but their internal constructions differ fundamentally.

SHA-2 uses an iterative compression-function design.

SHA-3 uses the Keccak sponge construction.

They are different algorithms with the same nominal digest length.

### "SHA-1 is fine because it still has 160 output bits"

Output length does not restore broken collision resistance.

SHA-1 has practical collision attacks and is being phased out from remaining NIST-approved uses.

For new designs, use an appropriate SHA-2 or SHA-3 family function unless a protocol specifies something else.

### "MD5 is useless for everything"

That statement is too broad.

MD5 is inappropriate for new cryptographic designs requiring collision resistance.

It may still appear in non-adversarial file-identification or accidental-error contexts where cryptographic collision resistance is not the security goal.

The required property must always be stated explicitly.

### "Hashing a password with SHA-256 is password hashing"

A general-purpose hash function is usually designed to be **fast**.

Password storage needs deliberately expensive password-based functions that slow down brute-force guessing and incorporate salts.

Examples include dedicated password hashing or password-based key-derivation constructions.

Therefore:

```python
sha256(password)
```

is not a modern password-storage design merely because SHA-256 itself is cryptographically strong.

This topic belongs to a later application-level discussion, but the distinction should be clear from the beginning.

### "A hash provides message authentication"

An ordinary hash is unkeyed.

If an attacker can alter both the message and the stored digest, they can simply recompute the digest.

Authentication requires a secret or asymmetric verification mechanism.

In this series, the direct next step is HMAC:

\[
\operatorname{HMAC}_K(M),
\]

which uses a cryptographic hash inside a keyed construction designed for message authentication.

Naively inventing a keyed hash by writing something like:

\[
H(K\|M)
\]

should not be assumed secure for every hash construction. Standardized MAC designs exist precisely so that these composition details do not need to be reinvented.

### A preview of SHA-2 versus SHA-3 structure

This primer deliberately focuses on hash security properties rather than full internal designs, but one structural preview is useful.

SHA-256 belongs to the family of iterated hashes built around a compression function. At a very high level:

```text
message
  |
padding
  |
fixed-size blocks
  |
compression iteration
  |
digest
```

SHA-3 uses a sponge construction:

```text
message
  |
absorb into state
  |
Keccak permutation
  |
squeeze output
```

The distinction becomes important later when we discuss:

- length-extension behavior,
- HMAC,
- sponge capacity,
- SHAKE extendable-output functions,
- domain separation.

### Current standards perspective

NIST's current hash-function material recognizes SHA-2 and SHA-3 family algorithms as modern approved alternatives.

FIPS 180-4 currently contains SHA-1 and SHA-2 specifications, but NIST has decided that its revision will remove the SHA-1 specification.

FIPS 202 specifies:

- SHA3-224,
- SHA3-256,
- SHA3-384,
- SHA3-512,
- SHAKE128,
- SHAKE256.

NIST has also decided to update FIPS 202, with the currently announced work focused in part on editorial modernization and related SHA-3-derived guidance.

For practical new designs, the important lesson is simple:

> treat MD5 and SHA-1 primarily as historical and cryptanalytic study material; use modern standardized algorithms appropriate to the protocol and required security strength.

---

## Conclusion

A cryptographic hash function is much more than a program that transforms bytes into a hexadecimal string.

Its mathematical interface is:

\[
H:\{0,1\}^{*}\rightarrow\{0,1\}^{n},
\]

and its classical security goals are:

\[
\boxed{
\text{preimage resistance}
}
\]

\[
\boxed{
\text{second-preimage resistance}
}
\]

\[
\boxed{
\text{collision resistance}
}
\]

These goals have different attack models and different generic complexities.

For an ideal \(n\)-bit hash:

\[
\text{preimage}\sim2^n,
\]

\[
\text{second preimage}\sim2^n,
\]

\[
\text{collision}\sim2^{n/2}.
\]

The deliberately weak examples make the distinctions concrete.

The affine map:

\[
H(x)=ax+b
\]

is invertible.

The Caesar transformation is reversible and does not compress.

The character-sum function ignores order and admits trivial second preimages.

The bytewise AND transformation destroys information independently in each byte and makes alternate inputs easy to construct.

The 16-bit truncated MD5 experiment demonstrates the birthday bound:

\[
\texttt{input\_105}
\neq
\texttt{input\_323}
\]

yet:

\[
H(\texttt{input\_105})
=
H(\texttt{input\_323})
=
\texttt{f064}.
\]

Repeating the same experiment with truncated SHA-256 produces a collision just as quickly because the weakness in that experiment is the **16-bit output size**, not the underlying full hash.

The full MD5 collision example is different: it demonstrates real failure of MD5's 128-bit collision resistance.

Finally, practical cryptographic engineering requires us to keep the primitive's role clear.

A hash:

- does not encrypt,
- does not by itself authenticate an attacker-controlled message,
- is not automatically suitable for password storage,
- does not guarantee unique digests,
- and is not secure merely because its output looks random.

Those distinctions are exactly what make the next step natural.

The next article in **Hash Functions & MACs** can move from:

\[
\boxed{\text{unkeyed hashing}}
\]

to:

\[
\boxed{\text{keyed authentication}}
\]

and study why HMAC is constructed the way it is rather than simply prepending a secret key to a message.

---

## References

1. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**.  
   https://doi.org/10.6028/NIST.FIPS.180-4

2. National Institute of Standards and Technology, **FIPS 202: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions**.  
   https://doi.org/10.6028/NIST.FIPS.202

3. National Institute of Standards and Technology, **NIST Policy on Hash Functions**.  
   https://csrc.nist.gov/Projects/Hash-Functions/NIST-Policy-on-Hash-Functions

4. S. Turner and L. Chen, **RFC 6151: Updated Security Considerations for the MD5 Message-Digest and the HMAC-MD5 Algorithms**, March 2011.  
   https://www.rfc-editor.org/rfc/rfc6151

5. M. Stevens et al., **The First Collision for Full SHA-1**, CRYPTO 2017.

6. Python Software Foundation, **`hashlib` — Secure hashes and message digests**.  
   https://docs.python.org/3/library/hashlib.html
