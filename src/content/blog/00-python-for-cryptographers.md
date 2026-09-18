---
title: "Python for Cryptographers: The Minimum Python You Need to Start"
description: "A beginner-first introduction to the small subset of Python needed to turn cryptographic mathematics into executable code."
pubDate: "2026-09-08"
updatedDate: "2026-09-14"
topics:
  - "Cryptography Fundamentals"
  - "Cryptographic Engineering"
tags:
  - "python"
  - "cryptography"
  - "beginners"
  - "cryptography-from-zero"
difficulty: "Introductory"
series: "Cryptography From Zero"
seriesOrder: 1
draft: false
---

Cryptography can look intimidating for two completely different reasons.

The first is **mathematics**. We eventually meet modular arithmetic, groups, finite fields, elliptic curves, polynomials, lattices, probability, and several other mathematical structures.

The second is **implementation**. Even when the mathematics is clear on paper, we still need a way to represent it, execute it, inspect intermediate values, test identities, deliberately break assumptions, and verify that the code actually implements the mathematics we intended.

This article is about that second problem.

It is **not a complete Python course**.

You do not need to become an expert Python programmer before studying cryptography. For the first part of CryptoCave, we need only a relatively small vocabulary:

- integers and arithmetic,
- variables and functions,
- conditions and loops,
- lists and tuples,
- text, bytes, hexadecimal, and Base64,
- bitwise operations,
- modular arithmetic,
- randomness,
- assertions and executable tests.

That is already enough to begin turning cryptographic mathematics into code.

Later, when a cryptographic construction requires a new programming concept, we will introduce it at the point where it becomes useful.

---

## Table of Contents

- [1. Mathematics becomes executable objects](#1-mathematics-becomes-executable-objects)
- [2. Numbers, variables, and arithmetic](#2-numbers-variables-and-arithmetic)
- [3. Functions, conditions, and loops](#3-functions-conditions-and-loops)
- [4. Representing mathematical objects](#4-representing-mathematical-objects)
- [5. Text, bytes, and encodings](#5-text-bytes-and-encodings)
- [6. Bits and bitwise operations](#6-bits-and-bitwise-operations)
- [7. Modular arithmetic in Python](#7-modular-arithmetic-in-python)
- [8. Randomness: random versus secrets](#8-randomness-random-versus-secrets)
- [9. Assertions and executable invariants](#9-assertions-and-executable-invariants)
- [10. Two small cryptographic experiments](#10-two-small-cryptographic-experiments)
- [11. Common beginner mistakes](#11-common-beginner-mistakes)
- [12. What you do not need to know yet](#12-what-you-do-not-need-to-know-yet)
- [13. Practice lab and reader checkpoint](#13-practice-lab-and-reader-checkpoint)
- [14. Where this is going](#14-where-this-is-going)
- [Run the companion code](#run-the-companion-code)
- [Next](#next)

---

## 1. Mathematics becomes executable objects

Suppose a textbook gives us

\[
p=17,\qquad g=3,\qquad x=7.
\]

On paper, these are mathematical objects.

In Python, we can represent them immediately:

```python
p = 17
g = 3
x = 7
```

Now they are values that a program can manipulate.

That sounds almost trivial, but it is the central idea behind the entire **Cryptography From Zero** series:

> We repeatedly take a mathematical object, choose a representation for it in code, implement its operations, test the relevant identities, and eventually place those operations inside cryptographic constructions.

The progression will gradually look something like this:

```text
integer
   ↓
modular integer
   ↓
group element
   ↓
elliptic-curve point
   ↓
polynomial
   ↓
finite-field element
   ↓
ring element
   ↓
lattice vector
```

The objective is not to hide the mathematics behind a library.

The objective is to make the mathematics visible in code.

That distinction will matter throughout CryptoCave. Mature cryptographic libraries are indispensable in real systems, but when we are learning a construction, calling a single high-level function often hides exactly the mechanism we are trying to understand.

---

## 2. Numbers, variables, and arithmetic

A Python variable simply gives a name to a value:

```python
prime = 17
generator = 3
secret = 7
```

We can inspect those values:

```python
print(prime)
print(generator)
print(secret)
```

which produces:

```text
17
3
7
```

Python also lets us inspect their type:

```python
print(type(prime))
```

Output:

```text
<class 'int'>
```

For now, the types we will encounter most often are:

| Type | Meaning |
| --- | --- |
| `int` | Integer |
| `bool` | `True` or `False` |
| `str` | Unicode text |
| `bytes` | Raw byte sequence |
| `list` | Mutable ordered sequence |
| `tuple` | Fixed-style ordered sequence |

We will introduce more sophisticated objects only when the mathematics requires them.

### Arbitrary-precision integers

Python integers are especially convenient for cryptography because they support **arbitrary precision**.

For example:

```python
x = 2 ** 500

print(x)
```

Python keeps the complete integer.

We are not restricted to ordinary 32-bit or 64-bit machine integers.

That is extremely useful because cryptography routinely works with integers containing hundreds or thousands of bits.

RSA, for example, may use a modulus containing thousands of bits, while elliptic-curve and finite-field algorithms routinely operate on integers much larger than native processor words.

There is an important caveat:

> Python's arbitrary-precision arithmetic is excellent for education and experimentation, but ordinary Python operations should not automatically be considered suitable for production cryptography.

Production implementations must additionally consider issues such as:

- constant-time execution,
- side channels,
- memory handling,
- validated parameter handling,
- hardened arithmetic libraries.

For now, however, Python integers let us concentrate on the mathematics.

### Basic arithmetic

Start with ordinary arithmetic:

```python
a = 17
b = 5

print(a + b)
print(a - b)
print(a * b)
print(a ** b)
```

The important operators are:

```text
+    addition
-    subtraction
*    multiplication
**   exponentiation
```

Thus:

```python
3 ** 4
```

means

\[
3^4=81.
\]

Two additional operators appear constantly in number theory:

```text
//   integer quotient
%    remainder
```

For example:

```python
a = 17
b = 5

q = a // b
r = a % b

print(q)
print(r)
```

gives:

```text
3
2
```

because

\[
17=3\cdot5+2.
\]

We can immediately turn that mathematical identity into an executable check:

```python
assert 17 == 5 * (17 // 5) + (17 % 5)
```

This is one of the habits we will repeatedly develop:

\[
\boxed{
\text{mathematical statement}
\longrightarrow
\text{executable invariant}
}
\]

---

## 3. Functions, conditions, and loops

Cryptographic algorithms are built from reusable operations.

Python functions let us convert mathematical maps directly into executable objects.

Suppose

\[
f(x)=x^2.
\]

We can write:

```python
def square(x):
    return x * x
```

and evaluate:

```python
print(square(5))
```

which returns:

```text
25
```

A slightly more relevant example is modular addition:

```python
def mod_add(a, b, modulus):
    return (a + b) % modulus
```

Then:

```python
print(mod_add(11, 9, 17))
```

returns:

```text
3
```

because

\[
11+9=20\equiv3\pmod{17}.
\]

### Type hints

You will often see functions written as:

```python
def mod_add(a: int, b: int, modulus: int) -> int:
    return (a + b) % modulus
```

The annotations

```text
: int
-> int
```

are **type hints**.

They help humans, editors, linters, and static-analysis tools understand what a function expects and returns.

They do not change the mathematics.

For cryptographic code they are useful because the distinction between

```text
integer
bytes
field element
point
scalar
```

can become security-relevant.

### Conditions

A program often needs to ask mathematical questions.

Python uses `if`:

```python
x = 10

if x % 2 == 0:
    print("even")
else:
    print("odd")
```

The expression

```python
x % 2 == 0
```

asks whether the remainder after division by two is zero.

Soon our questions become more cryptographic:

```text
Is gcd(a, n) equal to 1?

Is this number prime?

Does this modular inverse exist?

Is this element inside the required range?

Is this point on the elliptic curve?

Does this signature verify?

Is this ciphertext well formed?
```

The Python syntax remains simple.

The mathematics behind the condition becomes increasingly sophisticated.

### Loops

A `for` loop repeats an operation:

```python
for x in range(5):
    print(x)
```

Output:

```text
0
1
2
3
4
```

Many of our earliest cryptographic experiments will intentionally use loops even when a much faster algorithm exists.

Suppose we want to inspect a small search space:

```python
for candidate in range(1, 17):
    print(candidate)
```

This is inefficient as cryptanalysis of a real key space.

Pedagogically, however, it is excellent.

We can literally see what exhaustive search means.

Later we will replace brute force with mathematics.

### Powers modulo a prime

Consider:

```python
value = 1

for exponent in range(16):
    print(exponent, value)
    value = (value * 3) % 17
```

This computes

\[
3^0,3^1,3^2,\ldots
\]

modulo \(17\).

The same tiny experiment will later help us understand:

- multiplicative groups,
- element order,
- generators,
- Diffie-Hellman,
- discrete logarithms.

### `while` loops

A `while` loop repeats for as long as a condition remains true:

```python
x = 20

while x > 0:
    print(x)
    x -= 5
```

The Euclidean algorithm will soon have the same structure:

```text
while remainder != 0:
    update values
```

A basic programming construct therefore becomes a number-theoretic algorithm.

---

## 4. Representing mathematical objects

Cryptography is full of structured objects.

Before creating sophisticated classes, it is useful to see how ordinary Python containers can represent them.

### Lists

A list stores an ordered collection:

```python
numbers = [3, 1, 4]
```

Entries are accessed by index:

```python
print(numbers[0])
print(numbers[1])
```

Python indexing begins at zero:

```text
numbers[0] → 3
numbers[1] → 1
numbers[2] → 4
```

Lists are particularly useful for introducing polynomials.

Consider

\[
f(x)=3+x+4x^2.
\]

We can represent it as:

```python
coefficients = [3, 1, 4]
```

where position \(i\) stores the coefficient of \(x^i\):

```text
index 0 → coefficient of x^0
index 1 → coefficient of x^1
index 2 → coefficient of x^2
```

Later we may create a proper `Polynomial` abstraction.

For now, the list makes the representation completely transparent.

### Tuples

A tuple is similar:

```python
P = (5, 1)
```

This can represent the point

\[
P=(5,1).
\]

When we reach elliptic curves we will eventually need a more sophisticated point object, including:

- point addition,
- scalar multiplication,
- point-at-infinity representation,
- coordinate validation.

But starting from a tuple lets us see the coordinates before hiding them behind an abstraction.

### Dictionaries

A dictionary maps keys to values:

```python
person = {
    "name": "Alice",
    "public_key": 17,
}
```

Access:

```python
print(person["name"])
```

Dictionaries later become useful for:

- protocol messages,
- transcripts,
- configuration,
- benchmark results,
- parameter sets,
- test vectors.

You do not need to master them yet.

The more important lesson is that choosing a data representation is part of implementing mathematics.

---

## 5. Text, bytes, and encodings

One of the most important practical distinctions in cryptographic programming is the difference between **text** and **bytes**.

Consider:

```python
text = "hello"
raw = b"hello"
```

They look almost identical.

They are not the same object:

```python
print(type(text))
print(type(raw))
```

Output:

```text
<class 'str'>
<class 'bytes'>
```

A Python `str` represents Unicode text.

A Python `bytes` object represents a sequence of byte values between \(0\) and \(255\).

Cryptographic algorithms ultimately operate on representations such as:

- bytes,
- integers,
- bit strings,
- field elements,
- elliptic-curve points,
- structured protocol encodings.

They do not operate directly on the abstract human concept of "text".

So conversion must be explicit.

### UTF-8 encoding

```python
text = "hello"

data = text.encode("utf-8")

print(data)
```

Output:

```text
b'hello'
```

Convert back:

```python
recovered = data.decode("utf-8")

print(recovered)
```

The important lesson is:

\[
\boxed{
\text{encoding is a representation rule}
}
\]

UTF-8 specifies how Unicode characters become bytes.

It is not encryption.

### `ord()` and `chr()`

Python also exposes Unicode code points:

```python
print(ord("A"))
```

returns:

```text
65
```

and:

```python
print(chr(65))
```

returns:

```text
A
```

A useful precision is that `ord()` and `chr()` operate on **Unicode code points**, not just ASCII.

ASCII occupies the familiar low portion of Unicode, which is why:

\[
A=65=0x41
\]

works as expected.

### Indexing strings and bytes

Consider:

```python
text = "ABC"
data = b"ABC"

print(text[0])
print(data[0])
```

Output:

```text
A
65
```

Why?

`text[0]` returns a one-character string.

`data[0]` returns the integer value of the first byte.

For ASCII:

\[
A=65=0x41.
\]

This becomes very useful when inspecting cryptographic messages byte by byte.

### Hexadecimal

Binary values become difficult to inspect quickly.

For example:

```python
message = b"hello"

print(message.hex())
```

Output:

```text
68656c6c6f
```

Hexadecimal uses sixteen symbols:

```text
0 1 2 3 4 5 6 7 8 9 a b c d e f
```

One byte contains \(8\) bits.

One hexadecimal digit represents \(4\) bits.

Therefore,

\[
1\text{ byte}=2\text{ hexadecimal digits}.
\]

This is why keys, hashes, signatures, ciphertexts, nonces, and test vectors are commonly displayed in hexadecimal.

Converting back is easy:

```python
data = bytes.fromhex("414243")

print(data)
```

Output:

```text
b'ABC'
```

because:

```text
0x41 = A
0x42 = B
0x43 = C
```

### Integers and bytes

Cryptographic code constantly moves between integer and byte-string representations.

Convert bytes to an integer:

```python
data = b"ABC"

value = int.from_bytes(data, "big")

print(value)
```

Convert back:

```python
recovered = value.to_bytes(3, "big")

print(recovered)
```

Output:

```text
b'ABC'
```

The argument `"big"` specifies **big-endian byte order**: the most significant byte appears first.

Later, protocol specifications will make byte order extremely important.

For now, remember the bridge:

\[
\boxed{
\text{bytes}
\longleftrightarrow
\text{integer}
}
\]

### Base64

Base64 frequently appears around cryptographic material because binary values often need to pass through text-oriented systems.

Example:

```python
import base64

data = b"hello"

encoded = base64.b64encode(data)
decoded = base64.b64decode(encoded)

print(encoded)
print(decoded)
```

But Base64 provides **no confidentiality**.

Anyone can decode it.

Keep the categories separate:

```text
hex      → representation

Base64   → encoding

AES      → encryption

SHA-256  → hashing

HMAC     → message authentication
```

These operations solve completely different problems.

---

## 6. Bits and bitwise operations

Cryptographic constructions frequently operate below the byte level.

Python lets us write binary values directly:

```python
x = 0b1010
y = 0b1100
```

The prefix:

```text
0b
```

means binary.

You can inspect a number in binary using:

```python
print(bin(x))
```

### XOR

XOR means **exclusive OR**.

Python uses the operator:

```python
^
```

Example:

```python
x = 0b1010
y = 0b1100

print(bin(x ^ y))
```

Bit by bit:

```text
1 XOR 1 = 0
0 XOR 1 = 1
1 XOR 0 = 1
0 XOR 0 = 0
```

Thus:

```text
1010
1100
----
0110
```

XOR appears throughout cryptography:

- one-time pads,
- stream ciphers,
- block ciphers,
- AES,
- masks,
- hash constructions,
- finite fields of characteristic two.

One fundamental identity is:

\[
x\oplus y\oplus y=x.
\]

In Python:

```python
x = 123
y = 77

assert (x ^ y) ^ y == x
```

### AND and OR

Python also provides:

```text
&    bitwise AND
|    bitwise OR
```

Example:

```python
x = 0b1010
y = 0b1100

print(bin(x & y))
print(bin(x | y))
```

These become useful when:

- extracting bit fields,
- applying masks,
- parsing encodings,
- implementing byte-oriented algorithms.

We will postpone a detailed treatment of bitwise NOT (`~`) because Python integers do not behave like fixed-width 8-bit registers unless we explicitly impose a width or mask.

That distinction matters in cryptographic implementations.

### Bit shifts

Python supports:

```python
x = 0b0011

print(bin(x << 1))
print(bin(x >> 1))
```

`<<` shifts left.

`>>` shifts right.

Bit shifts appear later in:

- byte parsing,
- packing and unpacking,
- finite-field multiplication,
- AES internals,
- hash functions,
- implementation optimizations.

---

## 7. Modular arithmetic in Python

Modular arithmetic is one of the main bridges between elementary Python and cryptography.

Consider:

```python
20 % 17
```

The result is:

```text
3
```

because

\[
20\equiv3\pmod{17}.
\]

Later we will repeatedly compute expressions such as:

\[
a+b\pmod n,
\]

\[
ab\pmod n,
\]

and

\[
a^e\pmod n.
\]

The `%` operator is therefore not merely a programming convenience.

It is our first computational entrance into arithmetic in

\[
\mathbb Z_n.
\]

### Efficient modular exponentiation

Suppose we want to compute:

\[
3^{100}\pmod{17}.
\]

We could write:

```python
(3 ** 100) % 17
```

but Python offers a much better operation:

```python
pow(3, 100, 17)
```

The three-argument form:

```python
pow(base, exponent, modulus)
```

performs modular exponentiation efficiently without first constructing the complete enormous integer \(3^{100}\).

This pattern will later appear everywhere:

- RSA,
- Diffie-Hellman,
- Fermat's theorem,
- Miller-Rabin,
- discrete-logarithm experiments,
- finite-field arithmetic.

It is worth becoming comfortable with it immediately.

---

## 8. Randomness: `random` versus `secrets`

This distinction is security-critical.

Python's standard:

```python
random
```

module is useful for:

- simulations,
- games,
- reproducible experiments,
- randomized testing,
- general programming.

It is **not intended for generating cryptographic secrets**.

For example:

```python
import random

rng1 = random.Random(12345)
rng2 = random.Random(12345)

print(rng1.randrange(1000))
print(rng2.randrange(1000))
```

Both generators begin from the same seed and therefore produce the same pseudorandom sequence.

That is extremely useful when we want reproducible scientific experiments.

It is dangerous when the value is supposed to remain secret from an adversary.

For application-level cryptographic randomness, Python provides:

```python
import secrets

secret_value = secrets.randbelow(1000)
random_bytes = secrets.token_bytes(32)
```

The `secrets` module delegates to the operating system's cryptographic randomness facilities.

A useful working rule is:

```text
simulation / reproducible experiment → random

secret cryptographic material        → secrets
```

You may also encounter:

```python
import os

data = os.urandom(32)
```

This also obtains random bytes from the operating system.

For normal application code, `secrets` often communicates the programmer's cryptographic intent more clearly and provides convenient helpers.

This is only the programming-level distinction.

Randomness is deep enough to deserve its own article, where we examine:

- entropy,
- CSPRNGs,
- operating-system randomness,
- reseeding,
- state compromise,
- nonce requirements.

---

## 9. Assertions and executable invariants

An assertion means:

> This property must hold. If it does not, stop.

Example:

```python
assert (3 + 5) % 7 == 1
```

If the expression is false, Python raises an `AssertionError`.

This habit is central to **Cryptography From Zero**.

Whenever we implement a mathematical relation, we should ask:

> What property must always hold if this implementation is correct?

Then we encode that property as a test.

Examples we will encounter later include:

\[
\gcd(a,b)
=
\gcd(b,a\bmod b),
\]

\[
a\cdot a^{-1}
\equiv
1
\pmod n,
\]

\[
D_K(E_K(m))=m,
\]

\[
\operatorname{INTT}
(
\operatorname{NTT}(a)
)
=
a,
\]

and eventually for a KEM:

\[
\operatorname{Decaps}(dk,c)=K.
\]

Cryptographic code should never be trusted merely because it "looks mathematically reasonable."

We test invariants.

That distinction will become particularly important later when we debug cryptographic implementations that run without crashing but implement subtly incorrect equations.

---

## 10. Two small cryptographic experiments

We now have enough Python to perform experiments that already resemble the beginning of real cryptographic mathematics.

### Experiment 1: powers modulo 17

Consider:

```python
p = 17
g = 3

value = 1

for exponent in range(16):
    print(
        f"{g}^{exponent:2d} mod {p} = {value:2d}"
    )

    value = (value * g) % p
```

We begin from:

\[
3^0=1.
\]

At each step:

\[
3^{k+1}=3^k\cdot3,
\]

and then reduce the result modulo \(17\).

This tiny experiment will later help us understand:

- cyclic groups,
- multiplicative order,
- generators,
- Diffie-Hellman,
- discrete logarithms.

Notice the workflow:

```text
mathematical question
        ↓
Python representation
        ↓
iteration
        ↓
modular arithmetic
        ↓
observable experiment
```

That pattern will repeat throughout CryptoCave.

### Experiment 2: representing a polynomial

Take:

\[
f(x)=3+x+4x^2.
\]

Represent the coefficients as:

```python
f = [3, 1, 4]
```

Now inspect them:

```python
for degree, coefficient in enumerate(f):
    print(
        f"coefficient of x^{degree} = {coefficient}"
    )
```

Output:

```text
coefficient of x^0 = 3
coefficient of x^1 = 1
coefficient of x^2 = 4
```

This innocent representation eventually leads surprisingly far:

```text
coefficient lists
        ↓
polynomial arithmetic
        ↓
finite fields
        ↓
AES GF(2^8)
        ↓
quotient rings
        ↓
NTT
        ↓
Ring-LWE
        ↓
Module-LWE
        ↓
ML-KEM
```

That is why we are learning only the programming structures that connect directly to cryptography.

---

## 11. Common beginner mistakes

Several small mistakes appear repeatedly when someone first begins implementing cryptographic mathematics.

They are worth collecting in one place.

### Text and bytes are not the same thing

This is false as a Python statement:

```text
"hello" == b"hello"
```

The two objects represent related information, but they have different types and different semantics.

Use explicit encoding and decoding.

### Base64 and hexadecimal are not encryption

Encoding changes representation.

Encryption introduces a security transformation controlled by a key.

For:

```text
hex
Base64
```

there is no secret key.

Anyone can reverse the representation.

### Do not generate real keys with `random`

Avoid:

```python
random.randint(...)
```

for real secret key material.

Use an interface intended for cryptographic randomness.

### Remember the modulus

In ordinary integer arithmetic:

```python
a * b
```

and:

```python
(a * b) % q
```

are different operations.

When working inside

\[
\mathbb Z_q,
\]

the reduction is part of the operation.

### `/` and `//` mean different things

Python:

```python
17 / 5
```

returns:

```text
3.4
```

whereas:

```python
17 // 5
```

returns:

```text
3
```

The distinction is important in number-theoretic algorithms.

### Modular division is not ordinary division

Later we will encounter expressions such as:

\[
\frac{a}{b}\pmod n.
\]

This does not mean ordinary real-number division.

When \(b\) is invertible modulo \(n\), it means:

\[
a\cdot b^{-1}\pmod n.
\]

And the inverse:

\[
b^{-1}
\]

may not exist.

Understanding exactly when modular inverses exist will become one of our first major number-theoretic steps.

---

## 12. What you do not need to know yet

At this stage you do **not** need to master:

- object-oriented programming,
- decorators,
- Python generators,
- asynchronous Python,
- metaclasses,
- web frameworks,
- advanced package management,
- NumPy,
- SageMath,
- cryptographic libraries.

We will introduce abstractions when they solve an actual cryptographic or mathematical problem.

The learning strategy is not:

> Become a Python expert and then begin cryptography.

It is:

> Learn exactly enough Python to make each new piece of cryptographic mathematics executable.

That keeps programming subordinate to the cryptography rather than allowing the programming language to become a prerequisite wall.

---

## 13. Practice lab and reader checkpoint

The exercises below deliberately stay small.

The objective is not to solve a difficult cryptographic problem yet.

The objective is to make the basic programming operations natural enough that, in the next article, our attention can shift toward the mathematics.

### A. Arithmetic and modular operations

#### Exercise 1 — Even numbers

Write:

```python
def is_even(n):
    ...
```

It should return `True` exactly when \(n\) is even.

Hint:

```python
n % 2
```

Ask yourself what the remainder must be when \(n\) is divisible by two.

#### Exercise 2 — Modular subtraction

Implement:

```python
def mod_sub(a, b, modulus):
    ...
```

and verify:

\[
3-5\equiv5\pmod7.
\]

Your function should work not only when \(a>b\), but also when ordinary subtraction produces a negative number.

#### Exercise 3 — Modular exponentiation

Compute:

\[
7^{12345}\pmod{65537}
\]

using:

```python
pow(...)
```

Do not first construct the complete value \(7^{12345}\).

Then compare:

```python
pow(7, 12345, 65537)
```

with:

```python
(7 ** 12345) % 65537
```

and verify that the mathematical result is the same.

### B. Bytes and bit operations

#### Exercise 4 — Bytes to integers

Write:

```python
def bytes_to_integer_list(data):
    ...
```

such that:

```python
bytes_to_integer_list(b"ABC")
```

returns:

```python
[65, 66, 67]
```

This exercise should make the representation chain explicit:

\[
\text{text}
\rightarrow
\text{bytes}
\rightarrow
\text{integers}.
\]

#### Exercise 5 — XOR

Write:

```python
def xor_integers(a, b):
    ...
```

and verify:

```python
assert xor_integers(
    0b1010,
    0b1100
) == 0b0110
```

Then verify the cancellation identity:

```python
x = 123
mask = 77

assert xor_integers(
    xor_integers(x, mask),
    mask
) == x
```

Explain why the second XOR removes the same mask.

### C. Representation is not cryptography

Take:

```python
message = b"cryptography"
```

Convert it to:

1. hexadecimal,
2. Base64.

Then recover the original bytes from both representations.

While doing this, ask:

> Where is the secret key?

There is none.

Therefore neither transformation is encryption.

### Reader checkpoint

You do not need to memorize every syntax detail in this article.

You should, however, be comfortable answering the following questions.

**Python and representation**

- What is the difference between `//` and `%`?
- What is the difference between `str` and `bytes`?
- Why does `b"ABC"[0]` return `65` rather than `"A"`?
- What does `^` mean in Python?
- Why is `pow(a, e, n)` useful for cryptography?
- Why should real cryptographic secrets not be generated with `random`?
- What does an `assert` allow us to express?
- What does `"big"` mean in `int.from_bytes(..., "big")`?

**Cryptographic thinking**

- Why do we repeatedly reduce values modulo \(n\)?
- Why can brute force still be useful in a teaching implementation?
- Why are bytes more fundamental to cryptographic code than human-readable text?
- Why are hexadecimal and Base64 representations rather than cryptography?
- Why is converting a mathematical identity into an executable assertion useful?
- What is the difference between representing a mathematical object correctly and implementing it securely?

If an answer still feels vague, modify one of the examples.

Change an input.

Break an assertion deliberately.

Print intermediate values.

Experimenting with the representation is often more useful than rereading the same paragraph.

---

## 14. Where this is going

We now have enough Python to begin turning basic number theory into executable mathematics.

The next step is:

\[
\boxed{
\text{integers}
\rightarrow
\text{division}
\rightarrow
\text{divisibility}
\rightarrow
\gcd
}
\]

Then:

\[
\gcd
\rightarrow
\text{Extended Euclidean Algorithm}
\rightarrow
\text{Bézout coefficients}
\rightarrow
\text{modular inverses}.
\]

From there, the path expands dramatically:

```text
integers
   ↓
modular arithmetic
   ↓
groups
   ↓
Diffie-Hellman
   ↓
RSA
```

while another branch eventually leads toward:

```text
polynomials
   ↓
finite fields
   ↓
AES
   ↓
NTT
   ↓
Ring-LWE
   ↓
Module-LWE
   ↓
ML-KEM
```

and another toward:

```text
finite fields
   ↓
elliptic curves
   ↓
ECDH
   ↓
ECDSA / Schnorr
   ↓
threshold signatures
```

We are starting with extremely small programming ideas.

We are not staying small.

---

## Run the companion code

Inside the **Cryptography From Zero** companion material, run:

```powershell
python chapters/00_python_for_cryptographers/examples.py
```

Then open:

```text
chapters/00_python_for_cryptographers/exercises.py
```

and complete the exercises.

The examples are intentionally simple enough that you should be able to modify them freely.

Try changing:

- the modulus,
- the base,
- the loop range,
- the input bytes,
- the polynomial coefficients,
- the XOR mask.

The point is not merely to obtain the expected output.

The point is to develop the habit of asking:

> What mathematical object am I representing, and what property should remain true?

---

## Next

**Blog 01 — Integers, Division, and Why Cryptography Starts Here**

That is where the Python vocabulary from this chapter begins turning into number theory.
