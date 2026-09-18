---
title: "Padding and Encryption Modes"
description: "A construction-oriented study of PKCS#7 padding and the classical block-cipher confidentiality modes ECB, CBC, CFB, OFB, and CTR, including formal definitions, IV and nonce requirements, error propagation, malleability, implementation pitfalls, and executable AES examples."
pubDate: "2025-04-11"
updatedDate: "2026-09-17"
topics:
  - "Symmetric Cryptography"
  - "Implementation Security"
  - "Cryptographic Engineering"
tags:
  - "pkcs7"
  - "ecb"
  - "cbc"
  - "cfb"
  - "ofb"
  - "ctr"
  - "padding"
  - "iv"
  - "nonce"
  - "block-cipher-modes"
difficulty: "Intermediate"
series: "Symmetric Cryptography"
seriesOrder: 4
draft: false
---

## Padding and Encryption Modes

The previous article built the AES-128 block primitive from the inside. That primitive accepts exactly one 128-bit input block and, under a fixed key, returns exactly one 128-bit output block.

Real messages do not naturally arrive as isolated 16-byte objects.

They may be:

- shorter than one AES block,
- longer than one block,
- not aligned to a block boundary,
- streamed over time,
- stored in files,
- repeated,
- truncated,
- reordered,
- modified by an adversary.

A **mode of operation** defines how repeated invocations of a block cipher are composed to process a longer message.

This article studies the five classical confidentiality modes standardized in NIST SP 800-38A:

- ECB — Electronic Codebook,
- CBC — Cipher Block Chaining,
- CFB — Cipher Feedback,
- OFB — Output Feedback,
- CTR — Counter mode.

Before the modes themselves, we need one more low-level issue: **padding**.

> **Important scope boundary.** ECB, CBC, CFB, OFB, and CTR are confidentiality mechanisms. By themselves, they do **not** authenticate ciphertexts. Modern protocol design normally prefers an authenticated-encryption construction such as an AEAD mode. We will study that next; here the goal is to understand the classical modes precisely.

---

## 1. From a Block Cipher to a Message Cipher

Let

\[
E_K : \{0,1\}^n \rightarrow \{0,1\}^n
\]

be a block cipher under key \(K\), with inverse

\[
D_K = E_K^{-1}.
\]

For AES,

\[
n=128.
\]

Thus a single AES invocation maps

\[
P_i \in \{0,1\}^{128}
\]

to

\[
C_i = E_K(P_i).
\]

For a long message,

\[
M = P_1 \| P_2 \| \cdots \| P_\ell,
\]

we need a rule that says:

- what enters each block-cipher invocation,
- whether blocks depend on previous blocks,
- whether an IV or nonce is required,
- whether encryption can run in parallel,
- whether the final block must be padded,
- what happens when ciphertext is modified,
- what security property the resulting construction actually provides.

That rule is the **mode of operation**.

### 1.1 The mode is not the cipher

AES and CBC are not interchangeable terms.

- **AES** is a block cipher.
- **CBC** is a mode that can use a block cipher such as AES.
- **AES-CBC** means AES instantiated inside CBC mode.

The same distinction applies to AES-CTR, AES-CFB, AES-OFB, and AES-ECB.

---

## 2. Why Padding Exists

ECB and CBC require plaintext input consisting of complete cipher blocks.

For AES, each block contains 16 bytes.

If the plaintext length is already a multiple of 16, block parsing is straightforward:

![Aligned plaintext blocks](/images/ready/padding-and-encryption-modes/image.png)

If the final block is incomplete, a padding rule can extend it to a full block:

![Plaintext requiring padding](/images/ready/padding-and-encryption-modes/image-1.png)

Stream-like modes such as CFB, OFB, and CTR can process a partial final segment or block and therefore do **not inherently require PKCS#7 padding**.

This distinction is important:

| Mode | PKCS#7 normally required? |
|---|---|
| ECB | Yes, for arbitrary byte-length messages |
| CBC | Yes, unless a scheme such as ciphertext stealing is used |
| CFB | No |
| OFB | No |
| CTR | No |

---

# 3. PKCS#7-Style Padding

The padding convention commonly called **PKCS#7 padding** appends \(p\) bytes, each with value \(p\), where

\[
p = B - (|M| \bmod B)
\]

and \(B\) is the block size in bytes.

For AES,

\[
B=16.
\]

The rule has one subtle but essential consequence:

> **Padding is always added.**

If the plaintext length is already a multiple of 16, then an entire block of

```text
10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10
```

is appended.

This is what makes unpadding unambiguous.

The modern CMS specification in RFC 5652 describes this padding rule for block-oriented content encryption.

---

## 3.1 Example: `"Welcome"`

The byte string

```text
Welcome
```

contains 7 bytes.

Therefore

\[
p = 16-7=9.
\]

The padding byte is

\[
09_{16}.
\]

The padded message is

```text
Welcome 09 09 09 09 09 09 09 09 09
```

or in Python notation:

```python
b"Welcome\x09\x09\x09\x09\x09\x09\x09\x09\x09"
```

---

## 3.2 Example: a message exactly one block long

```python
b"This is padding!"
```

contains exactly 16 bytes.

It still receives a complete padding block:

```text
10 10 10 10 10 10 10 10
10 10 10 10 10 10 10 10
```

Without the extra block, the receiver could not reliably distinguish data bytes from padding in the general case.

---

## 3.3 Python implementation

Using PyCryptodome:

```python
from Crypto.Util.Padding import pad, unpad

m = b"Welcome"

padded = pad(m, 16)

print(padded)
print(unpad(padded, 16))
```

A clearer hexadecimal inspection is:

```python
print(padded.hex())
```

which ends in:

```text
090909090909090909
```

---

## 3.4 Preserve the original examples

```python
from Crypto.Util.Padding import pad

print(pad(b"This is padding!", 16))
print(pad(b"Custom", 16))
print(pad(b"AES is cool", 16))
```

The padding lengths are:

- `"This is padding!"`: 16 bytes of `0x10`,
- `"Custom"`: 10 bytes of `0x0a`,
- `"AES is cool"`: 5 bytes of `0x05`.

The second output may visually contain newline characters because byte value `0x0a` is newline.

---

## 3.5 What padding does not provide

Padding provides **length alignment**, not:

- confidentiality,
- authenticity,
- integrity,
- tamper detection,
- replay protection.

Padding must not be treated as a security layer.

When unauthenticated CBC decryption exposes whether padding is valid, the padding parser itself can become an attack oracle.

---

# 4. Security Vocabulary for Modes

Before studying the modes one by one, it helps to separate several properties.

## 4.1 Deterministic encryption

A deterministic encryption construction maps the same plaintext under the same key to the same ciphertext.

ECB has this property block by block.

Determinism leaks equality information and is generally incompatible with modern indistinguishability goals for ordinary message encryption.

---

## 4.2 Randomized or nonce-based encryption

Other modes incorporate an additional public value:

- an **IV**,
- a **nonce**,
- or a **counter block**.

The extra input makes repeated encryptions of the same plaintext produce different ciphertexts when used correctly.

This value usually does **not** need to be secret.

Its required property depends on the mode:

- unpredictable,
- unique,
- nonrepeating,
- or generated according to a specific format.

These requirements are not interchangeable.

---

## 4.3 Confidentiality is not integrity

A mode may hide plaintext while still allowing an adversary to modify the ciphertext in a meaningful way.

That property is called **malleability**.

CBC, CFB, OFB, and CTR are all malleable when used without authentication.

> **"The plaintext is encrypted" does not imply "the ciphertext cannot be safely modified."**

---

# 5. Electronic Codebook — ECB

ECB is the simplest block-cipher mode.

For each plaintext block \(P_i\),

\[
C_i = E_K(P_i).
\]

Decryption is

\[
P_i = D_K(C_i).
\]

There is:

- no IV,
- no nonce,
- no chaining,
- no interaction between blocks.

![ECB structure](/images/ready/padding-and-encryption-modes/image-3.png)

---

## 5.1 Parallelism

Because every block is independent:

**Encryption:** yes.

**Decryption:** yes.

All blocks may be processed simultaneously.

---

## 5.2 The structural problem

If

\[
P_i=P_j,
\]

then

\[
C_i=C_j.
\]

The block cipher may be excellent, yet ECB exposes equality relationships at the message layer.

This is why the classic image demonstration remains useful:

![ECB pattern leakage](/images/ready/padding-and-encryption-modes/penguin.PNG)

ECB does not reveal the plaintext bytes directly, but repeated plaintext blocks become repeated ciphertext blocks.

---

## 5.3 Repeated-block experiment

```python
from Crypto.Cipher import AES

KEY = b"some secret key1"

m = (
    b"a" * 16 +
    b"b" * 16 +
    b"a" * 16
)

cipher = AES.new(KEY, AES.MODE_ECB)
c = cipher.encrypt(m)

C1 = c[0:16]
C2 = c[16:32]
C3 = c[32:48]

print(C1 == C3)  # True
```

This preserves the original project's pattern-leakage experiment.

---

## 5.4 ECB and padding

For arbitrary byte-length input:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

key = b"some secret key1"
message = b"Symmetric crypto is fun!"

padded = pad(message, 16)

cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(padded)

cipher = AES.new(key, AES.MODE_ECB)
recovered_padded = cipher.decrypt(ciphertext)

recovered = unpad(recovered_padded, 16)

assert recovered == message
```

For the 24-byte message

```text
Symmetric crypto is fun!
```

PKCS#7 appends eight bytes of `0x08`, producing two AES blocks:

```text
Block 1 = b"Symmetric crypto "
Block 2 = b"is fun!\x08\x08\x08\x08\x08\x08\x08\x08"
```

![ECB block processing](/images/ready/padding-and-encryption-modes/image-4.png)

---

## 5.5 ECB security summary

ECB has useful engineering properties:

- trivial implementation,
- full parallelism,
- random access to blocks,
- no IV state.

But for general confidential message encryption its determinism is a fundamental weakness.

It also provides no integrity. Ciphertext blocks can be removed, duplicated, replaced, or reordered without any cryptographic authentication failure because there is no authentication mechanism at all.

This is more precise than calling ECB specifically a "man-in-the-middle attack." The core issue is **deterministic pattern leakage plus lack of integrity**.

> **Practical rule:** do not select ECB for general data confidentiality. NIST has announced that its revision of SP 800-38A is intended to restrict ECB approval to narrowly specified uses.

---

# 6. Cipher Block Chaining — CBC

CBC introduces a dependency between adjacent blocks.

Let

\[
C_0 = IV.
\]

Encryption is:

\[
C_i = E_K(P_i \oplus C_{i-1}).
\]

Decryption is:

\[
P_i = D_K(C_i)\oplus C_{i-1}.
\]

For the first block:

\[
C_1=E_K(P_1\oplus IV),
\]

\[
P_1=D_K(C_1)\oplus IV.
\]

![CBC overview](/images/ready/padding-and-encryption-modes/image-5.png)

---

## 6.1 What the IV does

If two messages begin with the same first plaintext block but use independent appropriate IVs, the inputs to the first AES invocation differ.

For CBC, NIST SP 800-38A specifies that the IV must be **unpredictable** for a particular encryption execution. In engineering practice it should also be freshly generated rather than reused.

The IV:

- is one block long,
- does not need to be secret,
- is normally transmitted with the ciphertext,
- must be handled according to the mode's security requirements.

---

## 6.2 Why encryption is sequential

To compute

\[
C_i,
\]

we need

\[
C_{i-1}.
\]

Therefore CBC encryption forms a dependency chain:

```text
P1 -> C1 -> C2 -> C3 -> ...
```

Encryption cannot naturally process all blocks in parallel.

---

## 6.3 Why decryption can be parallelized

Each block satisfies

\[
P_i=D_K(C_i)\oplus C_{i-1}.
\]

All ciphertext blocks are already available to the receiver.

Thus the expensive block-cipher decryptions can be evaluated in parallel and then XORed with the corresponding previous ciphertext blocks.

---

## 6.4 CBC example

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

message = b"IVs are pretty cool!"

key = os.urandom(16)
iv = os.urandom(16)

padded = pad(message, 16)

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
ciphertext = cipher.encrypt(padded)

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
recovered_padded = cipher.decrypt(ciphertext)

recovered = unpad(recovered_padded, 16)

assert recovered == message

print("iv :", iv.hex())
print("ct :", ciphertext.hex())
print("pt :", recovered)
```

---

## 6.5 Patterned CBC experiment

```python
from Crypto.Cipher import AES
import os

KEY = b"some secret key1"
IV = os.urandom(16)

m = (
    b"a" * 16 +
    b"b" * 16 +
    b"a" * 16
)

cipher = AES.new(KEY, AES.MODE_CBC, iv=IV)
c = cipher.encrypt(m)

print(c[:16] == c[-16:])  # overwhelmingly expected to be False
```

Although the first and third plaintext blocks are identical, their chaining inputs differ.

![CBC patterned message](/images/ready/padding-and-encryption-modes/image-7.png)

---

## 6.6 CBC is malleable

CBC provides confidentiality, not integrity.

Recall:

\[
P_i = D_K(C_i)\oplus C_{i-1}.
\]

If an attacker flips a bit in \(C_{i-1}\), the corresponding bit of \(P_i\) flips predictably.

Let

\[
C'_{i-1}=C_{i-1}\oplus\Delta.
\]

Then

\[
P'_i
=
D_K(C_i)\oplus C'_{i-1}
=
P_i\oplus\Delta.
\]

The preceding plaintext block is also disturbed because the modified ciphertext block itself is decrypted, but the next plaintext block receives a controlled XOR difference.

The IV behaves like \(C_0\). Therefore modifying the IV allows controlled modifications of the first plaintext block unless the IV is authenticated.

---

## 6.7 CBC padding oracles

CBC commonly uses padding.

Suppose a receiver:

1. decrypts attacker-controlled ciphertext,
2. checks PKCS#7 padding,
3. reveals through errors, timing, status codes, or network behavior whether the padding was valid.

Then the adversary may obtain a **padding oracle**.

The attack does not require breaking AES.

Instead, it exploits:

- CBC's XOR structure,
- attacker-controlled ciphertext,
- and an observable validity predicate.

The stronger design lesson is:

> Authenticate ciphertext before exposing decryption-dependent validity information, or use an AEAD construction whose interface already binds confidentiality and integrity.

---

# 7. Cipher Feedback — CFB

CFB uses the **encryption** function of the block cipher to produce a keystream segment from previous ciphertext.

For full-block CFB, also called CFB128 for AES, let

\[
C_0 = IV.
\]

Encryption:

\[
C_i = P_i \oplus E_K(C_{i-1}).
\]

Decryption:

\[
P_i = C_i \oplus E_K(C_{i-1}).
\]

Notice that \(D_K\) is not required.

Both directions use \(E_K\).

![CFB diagram](/images/ready/padding-and-encryption-modes/cfb.PNG)

---

## 7.1 CFB as a self-synchronizing stream mode

For full-block CFB:

```text
feedback = IV
keystream = E_K(feedback)
ciphertext_block = plaintext_block XOR keystream
feedback = ciphertext_block
```

The ciphertext itself becomes the next feedback value.

This is why CFB is called **self-synchronizing**.

---

## 7.2 Segment size matters

CFB is not defined only at the full 128-bit block size.

NIST defines CFB with a segment size \(s\). Examples include:

- CFB8,
- CFB128.

This matters directly in PyCryptodome.

If we use the full-block equations above, the code should make that explicit:

```python
AES.new(
    key,
    AES.MODE_CFB,
    iv=iv,
    segment_size=128,
)
```

This corrects an ambiguity in the original implementation examples.

---

## 7.3 CFB does not require PKCS#7 padding

```python
from Crypto.Cipher import AES
import os

key = os.urandom(16)
iv = os.urandom(16)

message = b"a message secret longer than 128 bits"

cipher = AES.new(
    key,
    AES.MODE_CFB,
    iv=iv,
    segment_size=128,
)
ciphertext = cipher.encrypt(message)

cipher = AES.new(
    key,
    AES.MODE_CFB,
    iv=iv,
    segment_size=128,
)
recovered = cipher.decrypt(ciphertext)

assert recovered == message
assert len(ciphertext) == len(message)
```

No padding is required.

---

## 7.4 CFB parallelism

For full-block CFB:

**Encryption:** sequential.

To compute \(C_i\), we need \(C_{i-1}\).

**Decryption:** block-cipher invocations can be parallelized once the ciphertext is available, because each plaintext block uses known values \(C_i\) and \(C_{i-1}\).

---

## 7.5 IV requirement

NIST SP 800-38A specifies an **unpredictable IV** for CFB.

The IV does not need to be secret.

The original draft described a chosen-IV oracle experiment. That experiment is useful, but its security meaning must be stated carefully: it demonstrates failure when an interface lets an attacker select or manipulate the IV in a way that violates the intended IV-generation assumptions. Merely learning a correctly generated IV after generation is not the same attack.

---

## 7.6 Chosen-IV demonstration

Suppose an API improperly lets an attacker request CFB encryption using arbitrary IVs.

For a target ciphertext,

\[
C_1,C_2,\dots
\]

we have

\[
P_2=C_2\oplus E_K(C_1).
\]

If the attacker asks the service to encrypt the all-zero block using

\[
IV'=C_1,
\]

then the first returned ciphertext block is

\[
C'_1
=
0\oplus E_K(C_1)
=
E_K(C_1).
\]

Therefore:

\[
P_2=C_2\oplus C'_1.
\]

The block cipher is not broken. The API has exposed the exact keystream block needed to decrypt part of the target ciphertext.

A compact educational implementation is:

```python
from Crypto.Cipher import AES
import os

KEY = b"some secret key1"
IV = os.urandom(16)

target = b"some trash inputSUPER SECRET STUFF HERE"

cipher = AES.new(
    KEY,
    AES.MODE_CFB,
    iv=IV,
    segment_size=128,
)
c = cipher.encrypt(target)

oracle = AES.new(
    KEY,
    AES.MODE_CFB,
    iv=c[:16],
    segment_size=128,
)

E_of_C1 = oracle.encrypt(bytes(16))

recovered_second_block = bytes(
    a ^ b
    for a, b in zip(E_of_C1, c[16:32])
)

print(recovered_second_block)
```

This preserves the conceptual experiment from the original article while making the chosen-IV assumption explicit.

---

## 7.7 CFB malleability and error propagation

CFB is unauthenticated and therefore malleable.

In full-block CFB, changing one ciphertext block:

- introduces a controlled XOR change in the corresponding plaintext block,
- also corrupts the following plaintext block because the modified ciphertext becomes the input to the next block-cipher invocation,
- then synchronization resumes.

For smaller segment sizes, error propagation follows the feedback-register structure and should be analyzed at the segment level.

---

# 8. Output Feedback — OFB

OFB turns the block cipher into a synchronous keystream generator.

Let

\[
O_0 = IV.
\]

Then:

\[
O_i = E_K(O_{i-1}),
\]

\[
C_i = P_i \oplus O_i.
\]

Decryption is identical:

\[
P_i = C_i \oplus O_i.
\]

![OFB mode](/images/ready/padding-and-encryption-modes/ofb.png)

The crucial difference from CFB is the feedback value:

- CFB feeds back **ciphertext**,
- OFB feeds back **block-cipher output**.

---

## 8.1 OFB keystream is independent of the message

The recurrence

\[
O_i=E_K(O_{i-1})
\]

depends only on:

- the key,
- the IV,
- previous keystream state.

It does not depend on plaintext or ciphertext.

This means the keystream can be generated before message bytes are available.

---

## 8.2 OFB does not require padding

The original draft imported `pad` and `unpad` and later displayed a padded plaintext even though the shown `encrypt(m)` call did not actually pad the message.

The corrected example is:

```python
from Crypto.Cipher import AES
import os

key = os.urandom(16)
iv = os.urandom(16)

message = b"a message secret longer than 128 bits"

cipher = AES.new(key, AES.MODE_OFB, iv=iv)
ciphertext = cipher.encrypt(message)

cipher = AES.new(key, AES.MODE_OFB, iv=iv)
recovered = cipher.decrypt(ciphertext)

assert recovered == message
assert len(ciphertext) == len(message)
```

---

## 8.3 OFB parallelism

The OFB recurrence is sequential:

\[
O_i=E_K(O_{i-1}).
\]

Therefore generating block \(i\) requires block \(i-1\).

**Encryption:** not naturally parallelizable.

**Decryption:** not naturally parallelizable.

However, because the keystream is message-independent, it can be **precomputed sequentially** once the key and IV are known.

Precomputation is not the same thing as parallel computation.

---

## 8.4 IV reuse is catastrophic

If the same key and IV are reused, the same OFB keystream is generated.

For two messages:

\[
C=P\oplus O,
\]

\[
C'=P'\oplus O.
\]

Then:

\[
C\oplus C'
=
P\oplus P'.
\]

The keystream disappears.

NIST SP 800-38A requires unique IVs for OFB.

---

## 8.5 Bit flipping

Because

\[
P=C\oplus O,
\]

if an attacker flips one ciphertext bit,

\[
C'=C\oplus\Delta,
\]

then

\[
P'=P\oplus\Delta.
\]

The same bit flips in the recovered plaintext.

There is no authentication failure because OFB itself has no authentication mechanism.

---

# 9. Counter Mode — CTR

CTR is structurally one of the cleanest classical modes.

Instead of feeding output or ciphertext back into the block cipher, CTR encrypts a sequence of distinct **counter blocks**.

Let the counter blocks be

\[
T_1,T_2,\dots,T_\ell,
\]

with the fundamental requirement:

\[
T_i \neq T_j
\]

for every block-cipher invocation under the same key.

Generate the keystream:

\[
S_i=E_K(T_i).
\]

Then:

\[
C_i=P_i\oplus S_i.
\]

Decryption is identical:

\[
P_i=C_i\oplus S_i.
\]

![CTR mode](/images/ready/padding-and-encryption-modes/image-8.png)

---

## 9.1 Nonce and counter layout

A common layout is:

\[
T_i = N \| \operatorname{ctr}_i,
\]

where:

- \(N\) is a per-message nonce,
- \(\operatorname{ctr}_i\) is a block counter.

The exact partition is protocol-specific.

The security condition is stronger and more precise than saying "use a random IV":

> The same block-cipher input must never be repeated under the same key.

A nonce may therefore be random, sequential, stateful, or otherwise generated—provided the construction guarantees nonrepetition within the allowed usage limits.

---

## 9.2 CTR padding

CTR does not require padding.

For a final short block, only the necessary number of keystream bytes are XORed.

Thus:

\[
|C|=|P|.
\]

---

## 9.3 Full parallelism

Unlike CBC, CFB, and OFB, the CTR input blocks can be generated independently:

\[
T_i=N\|\operatorname{ctr}_i.
\]

Therefore all values

\[
E_K(T_i)
\]

can be computed in parallel.

**Encryption:** parallelizable.

**Decryption:** parallelizable.

**Keystream generation:** parallelizable.

CTR also naturally supports random access if the counter construction makes the block index computable directly.

---

## 9.4 PyCryptodome example

Use a nonce that leaves a comfortable counter field rather than a 15-byte nonce with a one-byte counter.

```python
from Crypto.Cipher import AES
import os

message = b"a message secret longer than 128 bits"

key = os.urandom(16)
nonce = os.urandom(8)

cipher = AES.new(
    key,
    AES.MODE_CTR,
    nonce=nonce,
)
ciphertext = cipher.encrypt(message)

cipher = AES.new(
    key,
    AES.MODE_CTR,
    nonce=nonce,
)
recovered = cipher.decrypt(ciphertext)

assert recovered == message
assert len(ciphertext) == len(message)

print("nonce:", nonce.hex())
print("ct   :", ciphertext.hex())
```

---

## 9.5 Explicit counter construction

```python
from Crypto.Cipher import AES
from Crypto.Util import Counter
import os

key = os.urandom(16)
nonce = os.urandom(8)
message = b"a message secret longer than 128 bits"

ctr = Counter.new(
    64,
    prefix=nonce,
    initial_value=0,
    little_endian=False,
)

cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
ciphertext = cipher.encrypt(message)

ctr = Counter.new(
    64,
    prefix=nonce,
    initial_value=0,
    little_endian=False,
)

cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
recovered = cipher.decrypt(ciphertext)

assert recovered == message
```

The 8-byte nonce plus the 8-byte counter forms one 16-byte AES input block.

---

## 9.6 Counter reuse: the two-time-pad failure

Suppose two plaintext streams use the same key and the same counter-block sequence:

\[
C=P\oplus S,
\]

\[
C'=P'\oplus S.
\]

Then:

\[
C\oplus C'
=
P\oplus P'.
\]

If part of one plaintext is known or predictable, the corresponding part of the other plaintext can immediately be derived.

A compact demonstration:

```python
from Crypto.Cipher import AES

key = b"some secret key1"
nonce = b"12345678"

m1 = b"Attack at dawn!!"
m2 = b"Retreat at noon!"

c1 = AES.new(
    key,
    AES.MODE_CTR,
    nonce=nonce,
).encrypt(m1)

c2 = AES.new(
    key,
    AES.MODE_CTR,
    nonce=nonce,
).encrypt(m2)

xor_ciphertexts = bytes(
    a ^ b
    for a, b in zip(c1, c2)
)

xor_plaintexts = bytes(
    a ^ b
    for a, b in zip(m1, m2)
)

assert xor_ciphertexts == xor_plaintexts
```

The cryptographic failure is caused by keystream reuse, not by a weakness in AES.

---

## 9.7 CTR bit flipping

CTR is malleable for the same XOR reason as OFB.

If:

\[
C'=C\oplus\Delta,
\]

then:

\[
P'=P\oplus\Delta.
\]

An attacker does not need the key to induce a selected difference in the decrypted plaintext.

Authentication is the missing property.

---

# 10. Error Propagation

Modes differ sharply in how transmission errors or deliberate ciphertext changes propagate.

For full-block variants:

| Mode | Modify one ciphertext block/segment | Effect on recovered plaintext |
|---|---|---|
| ECB | corrupted block | corresponding plaintext block becomes unpredictable |
| CBC | modify \(C_i\) | \(P_i\) becomes unpredictable; \(P_{i+1}\) gets predictable XOR difference |
| CFB128 | modify \(C_i\) | \(P_i\) gets predictable XOR difference; \(P_{i+1}\) becomes corrupted |
| OFB | modify bit in \(C_i\) | same bit flips in \(P_i\) only |
| CTR | modify bit in \(C_i\) | same bit flips in \(P_i\) only |

These are not "integrity features." They are descriptions of malleability and error propagation.

---

# 11. Parallelism and Random Access

| Mode | Encrypt parallel? | Decrypt parallel? | Random access? | Padding? |
|---|---:|---:|---:|---:|
| ECB | Yes | Yes | Yes | Yes for arbitrary lengths |
| CBC | No | Yes | Decryption with previous block | Usually yes |
| CFB128 | No | Yes | Requires previous ciphertext | No |
| OFB | No | No | Not naturally | No |
| CTR | Yes | Yes | Yes | No |

CTR's engineering profile is one reason it became so influential.

But high performance is not enough. Correct nonce/counter management is non-negotiable.

---

# 12. IV and Nonce Requirements Are Mode-Specific

One of the most common implementation errors is treating every public auxiliary value as though it obeyed the same rule.

It does not.

## 12.1 CBC

NIST SP 800-38A requires the IV to be **unpredictable**.

A fresh random IV is the standard practical pattern.

---

## 12.2 CFB

NIST SP 800-38A likewise requires an **unpredictable IV**.

For PyCryptodome, also specify the intended `segment_size` so the code and mathematical model match.

---

## 12.3 OFB

The IV must be **unique** for each encryption under the key according to SP 800-38A.

Reuse regenerates the same keystream.

---

## 12.4 CTR

The critical requirement is that the **counter blocks never repeat under a key**.

If the counter block is constructed as

\[
nonce \| counter,
\]

then the nonce/counter allocation policy must ensure the entire 128-bit block sequence is unique.

This includes preventing wraparound.

---

## 12.5 Secrecy is usually not the requirement

IVs and nonces are usually transmitted openly with ciphertext.

The security property comes from proper generation and nonrepetition/unpredictability rules, not from trying to hide these public values.

---

# 13. Deterministic vs Randomized / Nonce-Based Behavior

### ECB

Under a fixed key, encryption is deterministic block by block.

Repeated plaintext blocks are visibly repeated.

### CBC / CFB

The encryption result depends on the IV.

With correctly generated IVs, repeated messages do not deterministically map to the same ciphertext.

### OFB / CTR

The plaintext is XORed with a keystream determined by an IV/nonce/counter schedule.

If that schedule repeats, the keystream repeats and confidentiality can fail dramatically.

---

# 14. A Controlled ECB vs CBC Experiment

```python
from Crypto.Cipher import AES
import os

key = os.urandom(16)
iv = os.urandom(16)

P = (
    b"A" * 16 +
    b"B" * 16 +
    b"A" * 16
)

ecb = AES.new(key, AES.MODE_ECB)
C_ecb = ecb.encrypt(P)

cbc = AES.new(key, AES.MODE_CBC, iv=iv)
C_cbc = cbc.encrypt(P)

print(
    "ECB first == third:",
    C_ecb[:16] == C_ecb[32:48],
)

print(
    "CBC first == third:",
    C_cbc[:16] == C_cbc[32:48],
)
```

Expected structural behavior:

```text
ECB first == third: True
CBC first == third: False
```

This experiment teaches exactly what chaining changes.

It does **not** imply that CBC automatically supplies integrity or that CBC should be preferred over modern AEAD.

---

# 15. Why Padding Oracles Matter So Much

Suppose CBC decryption returns two visibly different responses:

```text
ERROR: bad padding
```

versus

```text
ERROR: valid padding but malformed message
```

That one bit of information can be queried repeatedly.

An attacker may then adapt ciphertext bytes until the decrypted suffix accidentally satisfies a valid PKCS#7 pattern.

The oracle leaks whether a manipulated intermediate value has a selected relation with the previous ciphertext block.

Repeated carefully, this can reveal plaintext bytes.

The key lesson is architectural:

```text
decrypt
  -> parse
  -> report detailed failure
```

is dangerous when unauthenticated attacker-controlled ciphertext reaches the decryptor.

Authenticated-encryption APIs instead aim for:

```text
authenticate + decrypt
  -> valid plaintext
  -> or one authentication failure
```

without releasing unauthenticated plaintext to the application.

---

# 16. Why Encrypt-then-MAC Was Historically Important

If a system must use a confidentiality-only mode such as CBC or CTR, adding an independent MAC can provide integrity.

The clean classical composition is:

\[
C = Enc_{K_E}(M),
\]

\[
T = MAC_{K_M}(metadata \| C),
\]

and the receiver verifies the MAC before accepting/decrypting the ciphertext.

This is the **Encrypt-then-MAC** pattern.

The encryption key and MAC key should be distinct cryptographic keys, typically derived from key material using an appropriate KDF.

Modern AEAD schemes package confidentiality and authenticity into one standardized construction, reducing the opportunity for composition mistakes.

---

# 17. Classical Modes vs AEAD

NIST SP 800-38A defines ECB, CBC, CFB, OFB, and CTR as **confidentiality modes**.

NIST SP 800-38D defines GCM as an authenticated-encryption mode with associated data.

The distinction is conceptual:

```text
Classical confidentiality mode:
plaintext -> ciphertext
```

versus

```text
AEAD:
plaintext + associated data + nonce
             |
             v
       ciphertext + tag
```

The authentication tag lets the receiver reject modified data.

Without such authentication, the malleability discussed throughout this article remains relevant.

---

# 18. Modern Status of the NIST Modes

The five classical modes remain foundational and are still specified in NIST SP 800-38A.

However, NIST has decided to revise SP 800-38A. The revision goals include:

- limiting ECB approval to uses specifically permitted elsewhere,
- clarifying IV and counter-block requirements,
- emphasizing authentication,
- incorporating the CBC ciphertext-stealing addendum.

NIST IR 8459, published in 2024, reviews research and implementation issues across the SP 800-38 series.

This is an important historical transition:

> the classical modes remain essential to understand, but modern cryptographic engineering increasingly treats unauthenticated confidentiality as an incomplete interface.

---

# 19. Comparison Table

| Property | ECB | CBC | CFB128 | OFB | CTR |
|---|---|---|---|---|---|
| Uses block encryption \(E_K\) | Yes | Yes | Yes | Yes | Yes |
| Uses block decryption \(D_K\) for message decryption | Yes | Yes | No | No | No |
| IV / nonce | None | IV | IV | IV | counter-block scheme |
| Auxiliary-value requirement | — | unpredictable fresh IV | unpredictable fresh IV | unique IV | nonrepeating counter blocks |
| Padding normally needed | Yes | Yes | No | No | No |
| Encryption parallel | Yes | No | No | No | Yes |
| Decryption parallel | Yes | Yes | Yes | No | Yes |
| Repeated plaintext block leaks directly | Yes | Not directly | Not directly | Not directly | Not directly |
| Ciphertext malleable without authentication | Yes / block substitution | Yes | Yes | Yes | Yes |
| Good default for new application encryption? | No | Generally no | Generally no | Generally no | Not alone; authenticate it |
| Main educational lesson | deterministic leakage | chaining + padding | ciphertext feedback | synchronous keystream | counters + nonce discipline |

---

# 20. Common Mistakes to Avoid

## 20.1 "AES-128 has a 128-bit block, AES-256 has a 256-bit block"

False.

AES always has a 128-bit block size.

AES-128, AES-192, and AES-256 refer to key sizes.

---

## 20.2 "Every AES mode needs padding"

False.

ECB and CBC operate on complete blocks and usually use padding for arbitrary-length messages.

CFB, OFB, and CTR can process non-block-aligned input.

---

## 20.3 "An IV must be secret"

Usually false.

For the modes here, the IV/nonce is ordinarily public.

What matters is satisfying the required generation property.

---

## 20.4 "Unique and unpredictable mean the same thing"

False.

A counter is predictable but can be unique.

A random value can be unpredictable but, without proper bounds and state management, uniqueness is not logically guaranteed.

Mode specifications deliberately distinguish these concepts.

---

## 20.5 "CBC fixes ECB, so CBC is secure"

Incomplete.

CBC fixes ECB's direct repeated-block equality leakage when its IV is correctly generated.

CBC is still:

- unauthenticated,
- malleable,
- padding-dependent in the usual form,
- vulnerable to padding-oracle-style failures when applications expose decryption feedback.

---

## 20.6 "CTR is safe because AES is secure"

Incomplete.

CTR security depends on never repeating its counter-block sequence under the same key.

AES can remain perfectly secure while the CTR construction fails catastrophically because of nonce reuse.

---

## 20.7 "CFB with a known IV is broken"

Too broad.

The IV does not need to be secret.

The standard requires the CFB IV to be unpredictable. A known IV after generation is normal. The chosen-IV oracle experiment demonstrates what happens when an interface violates the IV assumptions.

---

## 20.8 "OFB precomputation means OFB is parallel"

False.

The keystream may be prepared before the message arrives, but each OFB state depends on the preceding state.

CTR is the mode here whose keystream blocks are independently computable from their counters.

---

# 21. One Unified Python Demonstration

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os


KEY = os.urandom(16)
MESSAGE = b"Symmetric cryptography modes are structural wrappers."


# ECB
ecb = AES.new(KEY, AES.MODE_ECB)
ecb_ct = ecb.encrypt(pad(MESSAGE, 16))

ecb = AES.new(KEY, AES.MODE_ECB)
ecb_pt = unpad(ecb.decrypt(ecb_ct), 16)

assert ecb_pt == MESSAGE


# CBC
cbc_iv = os.urandom(16)

cbc = AES.new(KEY, AES.MODE_CBC, iv=cbc_iv)
cbc_ct = cbc.encrypt(pad(MESSAGE, 16))

cbc = AES.new(KEY, AES.MODE_CBC, iv=cbc_iv)
cbc_pt = unpad(cbc.decrypt(cbc_ct), 16)

assert cbc_pt == MESSAGE


# CFB128
cfb_iv = os.urandom(16)

cfb = AES.new(
    KEY,
    AES.MODE_CFB,
    iv=cfb_iv,
    segment_size=128,
)
cfb_ct = cfb.encrypt(MESSAGE)

cfb = AES.new(
    KEY,
    AES.MODE_CFB,
    iv=cfb_iv,
    segment_size=128,
)
cfb_pt = cfb.decrypt(cfb_ct)

assert cfb_pt == MESSAGE


# OFB
ofb_iv = os.urandom(16)

ofb = AES.new(KEY, AES.MODE_OFB, iv=ofb_iv)
ofb_ct = ofb.encrypt(MESSAGE)

ofb = AES.new(KEY, AES.MODE_OFB, iv=ofb_iv)
ofb_pt = ofb.decrypt(ofb_ct)

assert ofb_pt == MESSAGE


# CTR
ctr_nonce = os.urandom(8)

ctr = AES.new(KEY, AES.MODE_CTR, nonce=ctr_nonce)
ctr_ct = ctr.encrypt(MESSAGE)

ctr = AES.new(KEY, AES.MODE_CTR, nonce=ctr_nonce)
ctr_pt = ctr.decrypt(ctr_ct)

assert ctr_pt == MESSAGE


print("ECB:", ecb_ct.hex())
print("CBC:", cbc_ct.hex())
print("CFB:", cfb_ct.hex())
print("OFB:", ofb_ct.hex())
print("CTR:", ctr_ct.hex())
```

The ciphertexts differ because the modes transform block-cipher calls differently and, where applicable, use independent IVs/nonces.

The fact that every decryption succeeds only proves functional correctness of the experiment. It does not mean every mode is equally suitable for a new protocol.

---

# 22. What We Preserved and What We Corrected

The original article already contained the right broad progression:

```text
padding
  ->
ECB
  ->
CBC
  ->
CFB
  ->
OFB
  ->
CTR
```

and that structure is preserved.

It also already included:

- PKCS#7 examples,
- ECB single- and multi-block examples,
- the ECB repeated-block experiment,
- CBC equations,
- CBC random-IV examples,
- a patterned CBC experiment,
- CFB encryption/decryption,
- a chosen-IV CFB demonstration,
- OFB keystream reasoning,
- CTR equations,
- CTR nonce-reuse reasoning,
- practical PyCryptodome code.

The important corrections were:

1. **Padding is not required for every mode.**
2. **CFB code must specify `segment_size=128` when we use CFB128 equations.**
3. **The CFB oracle example requires attacker control/manipulation of IV selection; merely knowing a correct IV is not the attack.**
4. **OFB does not need PKCS#7 padding.**
5. **OFB precomputation is not parallel generation.**
6. **CBC IVs require unpredictability, not merely casual uniqueness.**
7. **CTR's true condition is nonrepetition of the full counter blocks under one key.**
8. **A 15-byte CTR nonce leaves only a one-byte counter in a common nonce/counter split and is a poor general teaching default for multi-block data.**
9. **ECB's weakness is better described as deterministic pattern leakage and lack of integrity rather than generically as a MITM vulnerability.**
10. **None of these confidentiality-only modes should be confused with authenticated encryption.**

---

# 23. Conclusion

A block cipher encrypts one fixed-size block.

A mode of operation decides how that primitive behaves over an actual message.

The differences are structural:

### ECB

\[
C_i=E_K(P_i).
\]

Simple and parallel, but deterministic and pattern-leaking.

### CBC

\[
C_i=E_K(P_i\oplus C_{i-1}).
\]

Chaining hides direct equality patterns but introduces sequential encryption, IV requirements, malleability, and the practical complexity of padding.

### CFB

\[
C_i=P_i\oplus E_K(C_{i-1}).
\]

Turns the block cipher into a self-synchronizing stream-like construction.

### OFB

\[
O_i=E_K(O_{i-1}),
\qquad
C_i=P_i\oplus O_i.
\]

Generates a message-independent synchronous keystream; IV reuse repeats that keystream.

### CTR

\[
C_i=P_i\oplus E_K(T_i).
\]

Uses distinct counter blocks, supports full parallelism and arbitrary-length input, but counter reuse creates a two-time-pad failure.

The deeper lesson is that the mode is part of the cryptographic construction.

A secure primitive used under the wrong mode, with the wrong IV rule, with nonce reuse, without authentication, or with unsafe decryption error handling can produce an insecure system without any weakness in AES itself.

That observation leads directly to the next stage of the series:

\[
\boxed{
\text{confidentiality}
\quad\longrightarrow\quad
\text{authenticated encryption}
}
\]

where we will study authentication tags, AEAD, AES-GCM, and the precise security role of nonces and associated data.

---

## References

1. National Institute of Standards and Technology, **SP 800-38A: Recommendation for Block Cipher Modes of Operation: Methods and Techniques**, December 2001.  
   https://doi.org/10.6028/NIST.SP.800-38A

2. National Institute of Standards and Technology, **Decision to Revise SP 800-38A**, April 2023.  
   https://csrc.nist.gov/News/2023/decision-to-revise-nist-sp-800-38a

3. National Institute of Standards and Technology, **IR 8459: Report on the Block Cipher Modes of Operation in the NIST SP 800-38 Series**, September 2024.  
   https://doi.org/10.6028/NIST.IR.8459

4. National Institute of Standards and Technology, **SP 800-38A Addendum: Three Variants of Ciphertext Stealing for CBC Mode**, October 2010.  
   https://doi.org/10.6028/NIST.SP.800-38A-Add

5. R. Housley, **RFC 5652: Cryptographic Message Syntax (CMS)**, September 2009, Section 6.3.  
   https://www.rfc-editor.org/rfc/rfc5652

6. National Institute of Standards and Technology, **SP 800-38D: Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC**, November 2007.  
   https://doi.org/10.6028/NIST.SP.800-38D

7. PyCryptodome documentation, **Classic modes of operation for symmetric block ciphers**.  
   https://pycryptodome.readthedocs.io/
