---
title: "Python for Cryptographers: The Minimum Python You Need to Start"
description: "A beginner-first introduction to the small subset of Python needed to turn cryptographic mathematics into executable code."
pubDate: "2026-09-08"
category: "Implementations"
tags:
  - python
  - cryptography
  - beginners
  - cryptography-from-zero
difficulty: "Introductory"
series: "Cryptography From Zero"
draft: false
---

Cryptography can look intimidating for two completely different reasons.

The first reason is **mathematics**. You will eventually meet modular arithmetic, groups, finite fields, elliptic curves, polynomials, lattices, and probability.

The second reason is **implementation**. Even if you understand the mathematics on paper, you still need a way to turn it into code, test it, break it, and inspect what is happening internally.

This article is about that second problem.

It is **not a complete Python course**.

You do not need to master Python before learning cryptography. You only need a small working vocabulary:

- integers,
- arithmetic,
- functions,
- conditions,
- loops,
- lists and tuples,
- bytes and hexadecimal,
- bitwise operations,
- modular exponentiation,
- randomness,
- assertions.

That is enough to begin.

Later, whenever cryptography requires something new, we will learn it exactly at the moment it becomes useful.

---

## 1. The first mental model: mathematics becomes executable objects

Suppose a textbook gives you:

$$
p = 17,\qquad g = 3,\qquad x = 7.
$$

On paper, these are mathematical objects.

In Python, we can immediately create them:

```python
p = 17
g = 3
x = 7
```

Now they are values that a program can manipulate.

That sounds trivial, but it is the central idea of this whole series:

> We will repeatedly take a mathematical object, decide how to represent it in Python, implement its operations, test those operations, and then use them inside cryptographic constructions.

For example:

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
ring element
   ↓
lattice vector
```

We are not trying to hide the mathematics behind libraries.

We are trying to make the mathematics visible in code.

---

# 2. Variables and values

A variable gives a name to a value.

```python
prime = 17
generator = 3
secret = 7
```

You can inspect them:

```python
print(prime)
print(generator)
print(secret)
```

Output:

```text
17
3
7
```

Python also lets us inspect the type:

```python
print(type(prime))
```

Output:

```text
<class 'int'>
```

For now, the most important types are:

```text
int      integer
bool     True or False
str      text
bytes    raw byte data
list     mutable sequence
tuple    fixed-style sequence
```

We will meet more types later.

---

# 3. Python integers are unusually convenient for cryptography

Python integers have **arbitrary precision**.

That means Python does not restrict normal integers to 32 or 64 bits in the way low-level machine integer types often do.

You can write:

```python
x = 2 ** 500
print(x)
```

and Python will keep the full integer.

This is extremely convenient because cryptography routinely works with very large numbers.

For example, later an RSA modulus may contain thousands of bits.

At the educational level, Python lets us focus on the mathematics first.

That does **not** mean ordinary Python integer operations are automatically safe for production cryptography. Timing behavior, memory behavior, constant-time implementation, and hardened big-integer libraries are separate engineering questions.

For now, Python integers are ideal for learning.

---

# 4. Arithmetic operators

Start with ordinary arithmetic:

```python
a = 17
b = 5

print(a + b)
print(a - b)
print(a * b)
print(a ** b)
```

The operators mean:

```text
+   addition
-   subtraction
*   multiplication
**  exponentiation
```

So:

```python
3 ** 4
```

means:

$$
3^4 = 81.
$$

Two other operators will appear everywhere in cryptography:

```text
//   integer quotient
%    remainder / modulo
```

Example:

```python
a = 17
b = 5

q = a // b
r = a % b

print(q)
print(r)
```

Output:

```text
3
2
```

because:

$$
17 = 3\cdot 5 + 2.
$$

That identity is so important that we should test it:

```python
assert 17 == 5 * (17 // 5) + (17 % 5)
```

This is our first example of a mathematical statement becoming an executable test.

---

## Why `%` matters so much

Consider:

```python
20 % 17
```

The result is:

```text
3
```

So:

$$
20 \equiv 3 \pmod{17}.
$$

Later we will perform almost every classical cryptographic operation inside modular arithmetic:

$$
a+b \pmod n,
$$

$$
ab \pmod n,
$$

$$
a^e \pmod n.
$$

The `%` operator is therefore not a small Python detail.

It is one of the bridges from ordinary integer arithmetic to cryptography.

---

# 5. Functions: turning formulas into reusable operations

Mathematics uses functions and maps.

For example:

$$
f(x)=x^2.
$$

Python gives us a direct computational analogue:

```python
def square(x):
    return x * x
```

Now:

```python
print(square(5))
```

returns:

```text
25
```

A cryptographic example:

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

because:

$$
11+9=20\equiv3\pmod{17}.
$$

---

## Type hints

You may also see:

```python
def mod_add(a: int, b: int, modulus: int) -> int:
    return (a + b) % modulus
```

The `: int` and `-> int` parts are **type hints**.

They help humans and development tools understand what the function expects.

They do not change the mathematics.

We will use them because cryptographic code becomes much easier to read when the intended data types are explicit.

---

# 6. Conditions: cryptographic code constantly asks questions

Python uses `if` when a program must choose based on a condition.

```python
x = 10

if x % 2 == 0:
    print("even")
else:
    print("odd")
```

The condition:

```python
x % 2 == 0
```

asks whether the remainder after division by 2 is zero.

Later our conditions become more cryptographic:

```text
Is gcd(a, n) equal to 1?
Is this number prime?
Is this element invertible?
Is this point on the elliptic curve?
Is this signature valid?
Does this ciphertext pass validation?
```

The syntax stays simple.

The mathematical meaning becomes deeper.

---

# 7. Loops: making the search space visible

A `for` loop repeats an operation.

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

Why are loops useful in a cryptography-from-zero course?

Because many of our first algorithms will deliberately be inefficient.

For example, suppose we want to search through possible secret values:

```python
for candidate in range(1, 17):
    print(candidate)
```

This lets us literally see the search space.

Later we will replace brute-force approaches with better mathematics.

But the slow version is often the best teaching version because it exposes what the algorithm is actually doing.

---

## Example: powers modulo 17

```python
value = 1

for exponent in range(16):
    print(exponent, value)
    value = (value * 3) % 17
```

This generates:

$$
3^0,3^1,3^2,\ldots
$$

modulo 17.

We will later use exactly this kind of experiment when studying:

- multiplicative groups,
- element order,
- generators,
- Diffie-Hellman,
- discrete logarithms.

---

# 8. `while` loops

A `while` loop repeats while a condition remains true.

```python
x = 20

while x > 0:
    print(x)
    x -= 5
```

Later the Euclidean algorithm will naturally use this pattern:

```text
while remainder != 0:
    update values
```

So even a basic loop will soon become number theory.

---

# 9. Lists: a simple first representation for mathematical objects

A list stores an ordered collection.

```python
numbers = [3, 1, 4]
```

You can access entries:

```python
print(numbers[0])
print(numbers[1])
```

Python starts indexing at zero.

So:

```text
numbers[0] → 3
numbers[1] → 1
numbers[2] → 4
```

Lists will be especially useful for polynomials.

The polynomial:

$$
3+x+4x^2
$$

can be represented as:

```python
coefficients = [3, 1, 4]
```

where index `i` stores the coefficient of $x^i$.

So:

```text
index 0 → coefficient of x^0
index 1 → coefficient of x^1
index 2 → coefficient of x^2
```

Later we will replace this raw list with a proper `Polynomial` class.

But the list representation makes the idea transparent.

---

# 10. Tuples: useful for fixed mathematical coordinates

A tuple looks similar:

```python
P = (5, 1)
```

This can represent a point:

$$
P=(5,1).
$$

Later, when we study elliptic curves, we will create a proper point object.

But starting with a tuple lets us focus on the coordinates first.

---

# 11. Dictionaries: useful, but not essential yet

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

Dictionaries become useful for:

- configuration,
- protocol transcripts,
- benchmark results,
- parameter sets.

You do not need to master them yet.

---

# 12. Text is not bytes

This distinction is one of the most important practical ideas in cryptographic programming.

Consider:

```python
text = "hello"
raw = b"hello"
```

These look similar.

They are not the same type:

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

A Python `bytes` object represents a sequence of byte values from 0 to 255.

Cryptographic algorithms eventually operate on:

- bytes,
- integers,
- field elements,
- bit strings,
- structured encodings.

They do not directly operate on the abstract human concept of "text".

So we need explicit conversion.

---

# 13. Encoding text into bytes

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

The important point is that **encoding is a representation rule**.

UTF-8 tells us how Unicode text becomes bytes.

It is not encryption.

---

# 14. ASCII, Unicode, `ord()` and `chr()`

You may encounter:

```python
print(ord("A"))
```

which returns:

```text
65
```

and:

```python
print(chr(65))
```

which returns:

```text
A
```

A useful precision:

> `ord()` and `chr()` operate on Unicode code points, not only ASCII.

ASCII occupies the familiar low range of Unicode, so examples such as `"A" -> 65` work exactly as expected.

For basic cryptographic byte examples, ASCII characters are convenient because their values are simple and familiar.

---

# 15. Indexing `str` and `bytes` behaves differently

This surprises many beginners.

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

$$
A = 65 = 0x41.
$$

This distinction becomes extremely useful when inspecting binary cryptographic data.

---

# 16. Hexadecimal: a human-friendly view of bytes

Binary data quickly becomes unreadable.

For example:

```python
message = b"hello"
print(message.hex())
```

Output:

```text
68656c6c6f
```

Hexadecimal uses 16 symbols:

```text
0 1 2 3 4 5 6 7 8 9 a b c d e f
```

One byte contains 8 bits.

One hexadecimal digit represents 4 bits.

Therefore:

$$
1\text{ byte}=2\text{ hex digits}.
$$

This is why cryptographic keys, hashes, ciphertexts, and test vectors are so often shown in hex.

---

## Hex back to bytes

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

---

# 17. Integers and bytes

Cryptography constantly moves between integers and byte strings.

Python already provides the tools we need.

## Bytes to integer

```python
data = b"ABC"

value = int.from_bytes(data, "big")

print(value)
```

## Integer back to bytes

```python
recovered = value.to_bytes(3, "big")

print(recovered)
```

Output:

```text
b'ABC'
```

The word `"big"` means **big-endian byte order**: the most significant byte comes first.

We will discuss endianness more carefully when protocols and standards require it.

For now, remember:

```text
bytes ↔ integer
```

is one of the most common representation bridges in cryptographic code.

---

# 18. Bits and binary notation

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

You can inspect a number in binary:

```python
print(bin(x))
```

---

# 19. XOR: one of the most important operations in cryptography

XOR means **exclusive OR**.

Python uses:

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

So:

```text
1010
1100
----
0110
```

XOR appears everywhere:

- stream ciphers,
- block ciphers,
- AES state operations,
- masks,
- hash constructions,
- finite fields of characteristic 2.

One useful property is:

$$
x\oplus y\oplus y=x.
$$

In Python:

```python
x = 123
y = 77

assert (x ^ y) ^ y == x
```

---

# 20. AND and OR

Python also provides:

```text
&   bitwise AND
|   bitwise OR
```

Example:

```python
x = 0b1010
y = 0b1100

print(bin(x & y))
print(bin(x | y))
```

We will use these later when:

- extracting bits,
- testing masks,
- implementing byte-oriented cryptography.

We will postpone a detailed discussion of bitwise NOT (`~`) because Python integers do not behave like fixed-width 8-bit registers unless we explicitly apply a mask. That distinction matters.

---

# 21. Shifts

```python
x = 0b0011

print(bin(x << 1))
print(bin(x >> 1))
```

`<<` shifts left.

`>>` shifts right.

These become important when we implement:

- byte parsing,
- finite-field multiplication,
- AES operations,
- packing and unpacking.

---

# 22. Modular exponentiation: use three-argument `pow`

Suppose we want:

$$
3^{100}\pmod{17}.
$$

We could write:

```python
(3 ** 100) % 17
```

But Python provides a much better form:

```python
pow(3, 100, 17)
```

This computes modular exponentiation efficiently without first constructing the enormous integer $3^{100}$.

This pattern will appear constantly:

```python
pow(base, exponent, modulus)
```

Later it becomes the computational core of:

- RSA,
- Diffie-Hellman,
- Fermat tests,
- Miller-Rabin,
- many number-theoretic experiments.

---

# 23. Randomness: `random` and `secrets` are not interchangeable

This distinction is security-critical.

Python's:

```python
random
```

module is designed for simulations, games, randomized testing, and general programming.

It is **not** intended for generating cryptographic secrets.

Example:

```python
import random

rng1 = random.Random(12345)
rng2 = random.Random(12345)

print(rng1.randrange(1000))
print(rng2.randrange(1000))
```

The same seed reproduces the same pseudorandom sequence.

That is useful for experiments.

It is dangerous for secret-key generation.

For cryptographic application-level randomness, Python provides:

```python
import secrets

secret_value = secrets.randbelow(1000)
random_bytes = secrets.token_bytes(32)
```

The `secrets` module uses the operating system's cryptographically secure random source.

Later we will study randomness as its own security topic.

For now:

```text
simulation / reproducible experiment → random
secret material                  → secrets
```

---

## What about `os.urandom()`?

You may also see:

```python
import os

data = os.urandom(32)
```

This also obtains random bytes from the operating system.

For normal application code, `secrets` makes the cryptographic intent clearer and provides convenient helpers.

---

# 24. Assertions: turn mathematical claims into executable checks

An assertion says:

> This must be true. If it is not true, stop.

Example:

```python
assert (3 + 5) % 7 == 1
```

If the expression is false, Python raises an error.

This habit is fundamental to this series.

Every time we implement a mathematical relation, we should ask:

> What property must always hold?

Then test it.

Examples we will eventually use:

$$
\gcd(a,b)=\gcd(b,a\bmod b),
$$

$$
a\cdot a^{-1}\equiv1\pmod n,
$$

$$
D_K(E_K(m))=m,
$$

$$
\operatorname{INTT}(\operatorname{NTT}(a))=a,
$$

$$
\operatorname{Decaps}(dk,c)=K.
$$

Cryptographic code should not be trusted because it "looks right".

We test invariants.

---

# 25. Base64: useful encoding, not encryption

Base64 often appears near cryptographic material because binary data sometimes needs to travel through text-oriented systems.

Example:

```python
import base64

data = b"hello"

encoded = base64.b64encode(data)
decoded = base64.b64decode(encoded)

print(encoded)
print(decoded)
```

But Base64 does **not** provide confidentiality.

Anyone can decode it.

So:

```text
hex      → representation
Base64   → encoding
AES      → encryption
SHA-256  → hashing
HMAC     → message authentication
```

These are different operations with different security goals.

Keeping these categories separate will prevent many beginner mistakes.

---

# 26. A small cryptographic-style Python experiment

Let us combine several ideas.

We will compute powers of 3 modulo 17:

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

What is happening?

We start with:

$$
3^0=1.
$$

Each step multiplies by 3:

$$
3^{k+1}=3^k\cdot3.
$$

But after every multiplication we reduce modulo 17.

This experiment will later help us understand:

- cyclic groups,
- order,
- generators,
- Diffie-Hellman,
- discrete logarithms.

For now, just notice the workflow:

```text
mathematical question
        ↓
Python representation
        ↓
loop
        ↓
modular arithmetic
        ↓
observable experiment
```

That workflow is the foundation of this entire project.

---

# 27. A simple polynomial representation

Take:

$$
f(x)=3+x+4x^2.
$$

Represent it:

```python
f = [3, 1, 4]
```

Inspect coefficients:

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

Much later, those innocent coefficient lists will lead us to:

```text
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

That is why we are learning only the Python structures that connect directly to cryptography.

---

# 28. Common beginner mistakes

## Mistake 1: thinking text and bytes are the same

Wrong mental model:

```text
"hello" == b"hello"
```

They represent related information, but they are different Python types.

Use explicit encoding and decoding.

---

## Mistake 2: treating Base64 as encryption

Base64 only changes representation.

There is no secret key.

---

## Mistake 3: generating keys with `random`

Do not use:

```python
random.randint(...)
```

for real secret material.

Use a cryptographic randomness interface.

---

## Mistake 4: forgetting modular reduction

This:

```python
a * b
```

and this:

```python
(a * b) % q
```

are different operations when we are working in $\mathbb Z_q$.

---

## Mistake 5: using `/` when you mean integer division

Python:

```python
17 / 5
```

returns:

```text
3.4
```

while:

```python
17 // 5
```

returns:

```text
3
```

In number theory, the distinction matters.

---

## Mistake 6: assuming mathematical division always exists modulo $n$

Later we will learn that:

$$
a/b \pmod n
$$

does not mean ordinary division.

It means multiplication by an inverse:

$$
a\cdot b^{-1}\pmod n,
$$

and that inverse may not exist.

That will be one of our first major cryptographic lessons.

---

# 29. What you do NOT need to know yet

You do not need to master:

- object-oriented programming,
- decorators,
- generators,
- asynchronous Python,
- metaclasses,
- web frameworks,
- advanced package management,
- NumPy,
- SageMath,
- cryptographic libraries.

We will introduce abstraction only when it solves a real problem.

The goal is not:

> Become a Python expert and then study cryptography.

The goal is:

> Learn exactly enough Python to make each new piece of cryptographic mathematics executable.

---

# 30. Mini exercises

Try these before reading the next article.

## Exercise 1 — Even numbers

Write:

```python
def is_even(n):
    ...
```

It should return `True` when $n$ is even.

Hint:

```python
n % 2
```

---

## Exercise 2 — Modular subtraction

Write:

```python
def mod_sub(a, b, modulus):
    ...
```

Example:

$$
3-5\equiv5\pmod7.
$$

---

## Exercise 3 — Bytes to integer values

Write a function:

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

---

## Exercise 4 — XOR

Write:

```python
def xor_integers(a, b):
    ...
```

and verify:

```python
assert xor_integers(0b1010, 0b1100) == 0b0110
```

---

## Exercise 5 — Modular exponentiation

Compute:

$$
7^{12345}\pmod{65537}
$$

using:

```python
pow(...)
```

Do not first compute the full value $7^{12345}$.

---

## Exercise 6 — Encoding is not encryption

Take:

```python
message = b"cryptography"
```

Convert it to:

1. hex,
2. Base64,

then recover the original bytes.

Ask yourself:

> Where is the secret key?

There is none.

Therefore neither conversion is encryption.

---

# 31. Reader checkpoint

Before moving on, you should be able to answer these questions.

### Python

- What is the difference between `//` and `%`?
- What is the difference between `str` and `bytes`?
- Why does `b"ABC"[0]` return `65`?
- What does `^` mean?
- Why is `pow(a, e, n)` useful?
- Why should cryptographic secrets not come from `random`?
- What does an `assert` do?

### Cryptographic thinking

- Why do we reduce values modulo $n$?
- Why might a brute-force loop still be useful for learning?
- Why are bytes more fundamental to cryptographic code than human-readable text?
- Why is Base64 not encryption?
- Why are executable invariants important?

If any answer still feels vague, experiment with the examples before continuing.

---

# 32. Where this is going

The next articles will begin turning these Python operations into mathematics.

First:

$$
\boxed{
\text{integers}
\rightarrow
\text{division}
\rightarrow
\text{divisibility}
\rightarrow
\gcd
}
$$

Then:

$$
\gcd
\rightarrow
\text{Extended Euclid}
\rightarrow
\text{modular inverses}
$$

and from there the path expands into:

```text
RSA
Diffie-Hellman
elliptic curves
finite fields
polynomials
AES
NTT
LWE
Ring-LWE
Module-LWE
ML-KEM
```

We are starting with very small Python ideas.

We are not staying small.

---

# 33. Run the companion code

Inside the **Cryptography From Zero** repository:

```powershell
python chapters/00_python_for_cryptographers/examples.py
```

Then open:

```text
chapters/00_python_for_cryptographers/exercises.py
```

and complete the TODOs.

---

## Next

**Blog 01 — Integers, Division, and Why Cryptography Starts Here**

That is where Python syntax begins turning into number theory.
