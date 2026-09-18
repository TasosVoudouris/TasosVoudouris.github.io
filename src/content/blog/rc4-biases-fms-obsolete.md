---
title: "RC4: KSA, PRGA, Keystream Biases, the FMS Attack, and Why the Cipher Is Obsolete"
description: "Study RC4 as a historical stream cipher: derive its key scheduling and keystream generation, examine early-byte statistical biases, explain the WEP/FMS related-key failure mode, and understand why RC4 was formally prohibited in TLS."
pubDate: "2025-04-05"
updatedDate: "2026-09-18"
topics:
  - "Symmetric Cryptography"
  - "Cryptanalysis"
  - "Implementation Security"
  - "Randomness & Entropy"
tags:
  - "rc4"
  - "arc4"
  - "fms"
  - "wep"
  - "stream-cipher"
  - "keystream-bias"
  - "ksa"
  - "prga"
difficulty: "Intermediate"
series: "Randomness & Stream Ciphers"
seriesOrder: 5
sourcePath: "experiments/randomness-stream-ciphers"
status: "Validated"
draft: false
---

## Table of Contents

- [Why RC4 Still Deserves Study](#why-rc4-still-deserves-study)
- [RC4 State, KSA, and PRGA](#rc4-state-ksa-and-prga)
- [From Permutation Updates to Keystream Biases](#from-permutation-updates-to-keystream-biases)
- [The FMS Attack and WEP’s Related-Key Failure](#the-fms-attack-and-weps-related-key-failure)
- [Why Dropping Early Bytes Was Not a Real Long-Term Fix](#why-dropping-early-bytes-was-not-a-real-long-term-fix)
- [RC4 in TLS and Its Formal Deprecation](#rc4-in-tls-and-its-formal-deprecation)
- [Executable Historical Labs](#executable-historical-labs)
- [What Replaced RC4](#what-replaced-rc4)
- [Conclusion](#conclusion)
- [References](#references)

---

## Why RC4 Still Deserves Study

RC4 is worth studying because it is **simple enough to understand completely and weak enough to teach several cryptographic lessons at once**.

Its design contains no S-box tables, no block structure, and no large algebraic machinery.

Instead, it maintains a permutation of the byte values

\[
0,1,\ldots,255
\]

and updates that permutation using only:

- byte addition modulo \(256\);
- swaps;
- table lookups.

The algorithm has two phases:

1. the **Key Scheduling Algorithm (KSA)**, which maps a variable-length key into an initial key-dependent permutation;
2. the **Pseudo-Random Generation Algorithm (PRGA)**, which updates that permutation and emits one keystream byte at a time.

Encryption is then:

\[
C_i=P_i\oplus Z_i,
\]

where \(Z_i\) is the \(i\)-th RC4 keystream byte.

This compact design made RC4 extremely attractive historically.

It was:

- fast in software;
- easy to implement;
- stateful but lightweight;
- deployed in major protocols and products.

The historical problem is that RC4's output is **not distributed like an ideal random byte stream**.

Its failure is not one single catastrophic algebraic relation like an LCG, nor one obvious linear recurrence like an LFSR.

Instead, RC4 accumulated:

- KSA weaknesses;
- early-output biases;
- long-range biases;
- related-key weaknesses;
- protocol-level amplification attacks.

That makes it the perfect next step in this series.

The progression so far is:

```text
LCG
    -> affine recurrence is directly solvable

LFSR
    -> linear recurrence over GF(2) is recoverable

Geffe
    -> nonlinear combination still leaks correlation

RC4
    -> nonlinear-looking permutation process still leaks statistical bias
```

This is a more subtle type of pseudorandomness failure.

---

## RC4 State, KSA, and PRGA

RC4 maintains:

- a 256-byte permutation \(S\);
- two byte-sized indices \(i,j\).

At every point:

\[
S
\]

is a permutation of:

\[
\{0,\ldots,255\}.
\]

So RC4's permutation state alone has:

\[
256!
\]

possible arrangements.

That is an enormous state space.

But a huge state space does not imply ideal pseudorandom output.

### Key Scheduling Algorithm

Let the secret key be:

\[
K[0],K[1],\ldots,K[\ell-1].
\]

Initialize:

\[
S[i]=i
\]

for:

\[
0\le i<256.
\]

Set:

\[
j=0.
\]

Then for:

\[
i=0,1,\ldots,255,
\]

compute:

\[
j
\leftarrow
(j+S[i]+K[i\bmod\ell])
\bmod256,
\]

and swap:

\[
S[i]
\leftrightarrow
S[j].
\]

Pseudocode:

```python
def rc4_ksa(key):
    S = list(range(256))
    j = 0

    for i in range(256):
        j = (
            j
            + S[i]
            + key[i % len(key)]
        ) % 256

        S[i], S[j] = S[j], S[i]

    return S
```

### What KSA is trying to do

The identity permutation:

```text
0, 1, 2, 3, ..., 255
```

is maximally structured.

The KSA attempts to scramble that structure using the secret key.

After 256 swaps, the permutation is key dependent.

A naive intuition might be:

> 256 key-dependent swaps should make the result "random enough."

That intuition is exactly what cryptanalysis tests rather than assumes.

The KSA does not sample a uniform random permutation.

Its output distribution retains detectable structure related to:

- early KSA steps;
- key bytes;
- permutation positions.

Those deviations matter because the PRGA begins immediately from the KSA result.

### Pseudo-Random Generation Algorithm

After KSA, initialize:

\[
i=0,\qquad j=0.
\]

For each output byte:

\[
i
\leftarrow
(i+1)\bmod256,
\]

\[
j
\leftarrow
(j+S[i])\bmod256.
\]

Swap:

\[
S[i]
\leftrightarrow
S[j].
\]

Then output:

\[
\boxed{
Z
=
S[
(S[i]+S[j])\bmod256
].
}
\]

Pseudocode:

```python
def rc4_prga(S, count):
    i = 0
    j = 0

    out = bytearray()

    for _ in range(count):
        i = (i + 1) % 256
        j = (j + S[i]) % 256

        S[i], S[j] = S[j], S[i]

        t = (S[i] + S[j]) % 256

        out.append(S[t])

    return bytes(out)
```

### Complete historical RC4 encryption

```python
def rc4(key, plaintext):
    S = rc4_ksa(key)
    keystream = rc4_prga(
        S,
        len(plaintext),
    )

    return bytes(
        p ^ z
        for p, z in zip(
            plaintext,
            keystream,
        )
    )
```

The function is compact.

That compactness was one of RC4's strengths operationally and one reason it spread so widely.

### Decryption

Because encryption is XOR:

\[
C=P\oplus Z,
\]

decryption is:

\[
P=C\oplus Z.
\]

So the same function can decrypt when given the same key.

That also means RC4 inherits the ordinary malleability of unauthenticated stream encryption.

Changing:

\[
C_i
\]

by:

\[
\Delta_i
\]

changes the recovered plaintext by the same amount:

\[
P_i'
=
P_i\oplus\Delta_i.
\]

RC4 by itself therefore provides no message authentication.

---

## From Permutation Updates to Keystream Biases

An ideal stream cipher should produce keystream that is computationally indistinguishable from uniform under the relevant key/nonce model.

For a random byte:

\[
Z_i\in\{0,\ldots,255\},
\]

the ideal probability of any fixed value is:

\[
\frac1{256}.
\]

RC4 violates this ideal model in many measurable ways.

### Bias does not mean a byte is predictable with certainty

A keystream bias is a statistical deviation such as:

\[
\Pr[Z_i=v]
\neq
\frac1{256}.
\]

The attacker may still be wrong most of the time.

For example, a probability changing from:

\[
\frac1{256}
\]

to approximately:

\[
\frac2{256}
\]

is tiny in absolute terms.

But it is **twice the uniform probability**.

If the same plaintext position is encrypted many times under independent or related RC4 keys, the attacker can aggregate evidence.

This is exactly the same statistical principle introduced in the Geffe article:

\[
\boxed{
\text{small bias}
+
\text{many samples}
=
\text{usable information}.
}
\]

### The famous second-byte bias

One of RC4's best-known biases is associated with its second output byte.

For independent random keys, the event:

\[
Z_2=0
\]

occurs with probability close to:

\[
\frac{2}{256}
=
\frac1{128},
\]

rather than the ideal:

\[
\frac1{256}.
\]

This is commonly associated with the Mantin-Shamir analysis.

So the second byte has an elevated probability of being zero.

The difference per session is small.

Across many sessions, it becomes statistically measurable.

### Quantifying the bias

Under the ideal model, for \(N\) independent samples:

\[
X_{\text{uniform}}
\sim
\operatorname{Binomial}
\left(
N,\frac1{256}
\right).
\]

The expected count is:

\[
\mathbb E[X_{\text{uniform}}]
=
\frac{N}{256}.
\]

Under an approximate \(2/256\) RC4 bias:

\[
\mathbb E[X_{\text{RC4}}]
\approx
\frac{2N}{256}.
\]

For:

\[
N=100000,
\]

the ideal expected count is about:

\[
390.625,
\]

while the biased expectation is about:

\[
781.25.
\]

That gap is large compared with ordinary binomial fluctuations.

This is why tiny-looking probability differences can be cryptographically serious when large data sets are available.

### Early bytes are especially problematic

RC4's early keystream is particularly structured because the PRGA begins immediately after KSA.

The KSA does not produce a perfectly uniform permutation, and the earliest PRGA steps retain information about that structure.

This motivated historical proposals such as:

```text
RC4-drop[n]
```

where the first \(n\) output bytes were discarded.

That can reduce some early biases.

It does not transform RC4 into a modern, well-analyzed cipher.

### Biases are not confined to one byte

Over time, researchers identified many classes of RC4 biases involving:

- individual output bytes;
- pairs of consecutive bytes;
- relationships between output and permutation values;
- long-term positions;
- key-dependent events.

So the right historical conclusion is not:

> "RC4 has one bad second byte."

It is:

> the RC4 keystream distribution contains a broad family of exploitable nonuniformities.

### Why protocol repetition matters

A bias in one encryption may reveal almost nothing.

But protocols can accidentally give an adversary many samples of related information.

Examples include situations where:

- a secret cookie appears at the same plaintext offset across many TLS connections;
- repeated packets encrypt related headers;
- related per-packet keys are generated from one long-term secret.

The protocol converts a weak statistical signal into an attack by allowing averaging.

This is another recurring engineering principle:

\[
\boxed{
\text{primitive weakness}
\times
\text{protocol repetition}
=
\text{practical attack surface}.
}
\]

---

## The FMS Attack and WEP’s Related-Key Failure

The Fluhrer-Mantin-Shamir attack is historically important because it showed how RC4's KSA weakness could interact disastrously with WEP's key construction.

The attack should be described precisely.

It is **not** simply:

> "RC4 is broken whenever someone concatenates an IV with a key."

The vulnerable structure was much more specific.

### WEP per-packet keying

Classic WEP used a public 24-bit IV together with a long-term secret key.

Conceptually, the RC4 key was formed as:

\[
K_{\text{packet}}
=
IV
\|
K_{\text{secret}}.
\]

Because the IV was transmitted openly, an attacker knew the first bytes of each packet's RC4 key.

Different packets therefore used **related RC4 keys** sharing the same unknown secret suffix.

This created a setting where the attacker could collect many KSA executions whose first key bytes were known and controlled by the public IV.

### Why early KSA steps matter

Recall:

\[
j
\leftarrow
j+S[i]+K[i]\pmod{256}.
\]

At early KSA positions, the permutation has undergone only a few swaps.

Under certain IV patterns, the state remains simple enough that the attack can approximate relationships between:

- known IV bytes;
- early permutation positions;
- the first PRGA output byte;
- an unknown secret-key byte.

Some IVs make those relationships especially informative.

These became known as **weak IVs** in the WEP/FMS context.

### Statistical key-byte recovery

A single packet does not reveal a secret key byte with certainty.

Instead, each suitably structured packet contributes a **vote** for a candidate key byte.

The attacker:

1. collects many packets with useful IV patterns;
2. extracts the first RC4 keystream byte from known or predictable plaintext structure;
3. computes a candidate value for one secret-key byte;
4. accumulates votes across packets;
5. selects the most strongly supported candidate;
6. proceeds to later key bytes using previously recovered bytes.

This is statistical cryptanalysis.

The attack succeeds because the correct candidate is slightly more likely than incorrect ones under the weak-IV conditions.

### Why known plaintext was available

WEP packets had predictable protocol structure.

If:

\[
C=P\oplus Z,
\]

and enough of \(P\) is known or guessed, then:

\[
Z=C\oplus P.
\]

Thus the attacker obtains early RC4 keystream bytes.

That transforms a protocol packet into information about the KSA state.

### FMS is a related-key attack

The key lesson is not merely:

```text
RC4 has bad statistics.
```

It is the combination:

```text
public IV
    +
shared long-term secret
    +
concatenated per-packet RC4 key
    +
KSA weakness
    +
known plaintext
    +
many packets
```

that creates the FMS attack environment.

So the correct statement is:

\[
\boxed{
\text{FMS exploits RC4 KSA under WEP-style related keys}.
}
\]

It should not be generalized mechanically to every API that happens to concatenate two byte strings.

### Later WEP attacks improved on FMS

FMS was not the end of WEP cryptanalysis.

Later work refined key-recovery techniques and reduced the amount of traffic needed.

The important historical point for this series is that RC4's key scheduling could leak exploitable information when the protocol repeatedly exposed carefully related keys.

WEP therefore demonstrates that:

\[
\boxed{
\text{key derivation and nonce processing are part of cipher security}.
}
\]

A protocol cannot simply feed structured public material into a cipher's key input and assume the primitive will behave like an ideal related-key-secure object.

---

## Why Dropping Early Bytes Was Not a Real Long-Term Fix

Once early RC4 biases became known, a natural mitigation was:

> discard the beginning of the keystream.

Variants were commonly described as:

```text
RC4-drop[n]
```

or:

```text
ARC4-drop[n].
```

### Why dropping helps at all

The earliest RC4 output is heavily influenced by KSA structure.

Allowing the PRGA to evolve the permutation before using output can weaken some early biases.

For example:

```python
S = rc4_ksa(key)

_ = rc4_prga(
    S,
    drop_count,
)

keystream = rc4_prga(
    S,
    message_length,
)
```

### Why this is not a modern security argument

RC4 accumulated more than one class of early-byte bias.

Later analyses found:

- biases beyond the earliest output;
- pairwise biases;
- long-term biases;
- protocol attacks exploiting large numbers of samples.

Discarding a fixed prefix therefore treats symptoms rather than providing a modern reduction or strong security argument.

The safe conclusion today is not:

> "choose a large enough drop value."

It is:

\[
\boxed{
\text{do not deploy RC4}.
}
\]

### Compatibility archaeology versus design choice

There is still value in implementing RC4 for:

- historical protocol analysis;
- file-format archaeology;
- reproducing published vectors;
- teaching stream-cipher cryptanalysis.

That is different from selecting it for a new cryptographic system.

The code in this article is therefore explicitly **historical/educational**.

---

## RC4 in TLS and Its Formal Deprecation

RC4 was once widely deployed in SSL/TLS.

For years it was attractive because:

- it was fast;
- it avoided CBC padding-oracle concerns;
- hardware/software support was broad.

But increasing cryptanalytic evidence showed that the keystream biases were incompatible with modern confidentiality requirements.

### Repeated-session bias attacks

TLS can create many independent RC4 sessions containing repeated application secrets at similar plaintext positions.

Examples include HTTP cookies and authentication tokens.

If an attacker can observe many encryptions of the same secret byte position under many RC4 keys, keystream biases can be averaged statistically.

This turns a small nonuniformity into plaintext recovery information.

The important attack model is therefore different from FMS:

```text
FMS/WEP:
    related per-packet keys + KSA weakness

TLS bias attacks:
    many sessions + RC4 keystream biases
```

They share RC4 as the primitive but exploit different structures.

### RFC 7465

RFC 7465, published in February 2015, formally prohibits RC4 cipher suites in TLS.

It requires:

- TLS clients to never offer RC4 cipher suites;
- TLS servers to never select RC4 cipher suites.

So RC4 should be treated as:

\[
\boxed{
\text{deprecated cryptographic history}
}
\]

rather than a fallback algorithm.

### Why historical compatibility is dangerous

A system may retain RC4 support because of old peers.

But weak-algorithm compatibility can create downgrade or negotiation risk if policy is not strict.

Modern protocol configurations should not expose RC4 as an optional "legacy" cipher suite unless an isolated historical-analysis environment explicitly requires it.

For real TLS deployment, the correct direction is modern AEAD suites.

---

## Executable Historical Labs

The companion implementation should do two things:

1. reproduce a known RC4 test vector;
2. make one keystream bias visible statistically.

Passing either test does **not** imply RC4 is secure.

It shows that the implementation matches the historical algorithm closely enough for study.

### Lab A: classic `Key` / `Plaintext` vector

Use:

```text
key:
    Key

plaintext:
    Plaintext
```

Expected ciphertext:

```text
BBF316E8D940AF0AD3
```

Python:

```python
key = b"Key"
plaintext = b"Plaintext"

ciphertext = rc4(
    key,
    plaintext,
)

assert ciphertext.hex().upper() == (
    "BBF316E8D940AF0AD3"
)
```

Decrypting with the same RC4 operation recovers:

```text
Plaintext
```

because stream encryption is XOR-based.

### Intermediate keystream

For the same vector:

\[
Z=P\oplus C.
\]

The first nine keystream bytes are:

```text
EB 9F 77 81 B7 34 CA 72 A7
```

This can be checked independently from the ciphertext and known plaintext.

### Lab B: second-byte zero bias

Generate many independent random 16-byte keys.

For each key:

1. run KSA;
2. generate the first two PRGA bytes;
3. record whether:

   \[
   Z_2=0.
   \]

For an ideal byte stream:

\[
\Pr[Z_2=0]
=
\frac1{256}
\approx
0.00390625.
\]

RC4 is expected to show a frequency closer to:

\[
\frac2{256}
=
0.0078125.
\]

A deterministic experiment can use a seeded noncryptographic PRNG to generate the *test keys*, because the purpose here is reproducibility, not secret-key generation.

```python
import random


rng = random.Random(
    0x524334
)

hits = 0
samples = 100000

for _ in range(samples):
    key = bytes(
        rng.randrange(256)
        for _ in range(16)
    )

    S = rc4_ksa(key)

    z = rc4_prga(
        S,
        2,
    )

    if z[1] == 0:
        hits += 1

frequency = hits / samples
```

A typical run should produce a value near the biased expectation rather than the ideal uniform probability.

### Statistical caution

One finite experiment is not a proof of the exact asymptotic probability.

Its role is to make the bias visible.

Theoretical analysis and large-scale experiments establish the cryptanalytic result.

The toy lab simply connects the formula to code.

### Run

The historical test can live in:

```text
experiments/randomness-stream-ciphers/test_rc4.py
```

and run with:

```bash
python experiments/randomness-stream-ciphers/test_rc4.py
```

The expected checks are:

```text
historical vector passes
round trip passes
second-byte zero frequency > uniform expectation
```

Again:

\[
\boxed{
\text{implementation consistency}
\neq
\text{security}.
}
\]

---

## What Replaced RC4

Modern stream-cipher design has moved far away from RC4's key-scheduled permutation.

The next article studies **ChaCha20**.

ChaCha20 uses a 512-bit state consisting of:

- constants;
- a 256-bit key;
- a block counter;
- a nonce.

Its round function uses ARX operations:

\[
\text{Addition}
+
\text{Rotation}
+
\text{XOR}.
\]

It does not rely on RC4-style byte permutation scheduling.

### ChaCha20 has an explicit nonce/counter interface

Instead of feeding an IV into the key scheduler, the IETF construction separates:

- secret key;
- public nonce;
- counter.

Conceptually:

\[
Z_{\text{block}}
=
\operatorname{ChaCha20Block}
(
K,
N,
\operatorname{counter}
).
\]

That is a much cleaner protocol interface than treating public nonce material as part of an ad-hoc related key.

### Modern protocols use authentication too

Bare ChaCha20 is still only a stream cipher.

Modern protocols normally use:

\[
\text{ChaCha20-Poly1305}
\]

to obtain authenticated encryption.

That provides both:

- confidentiality;
- integrity/authenticity.

So the transition from RC4 to ChaCha20 is not merely:

```text
old stream cipher
    ->
new stream cipher
```

It is also a transition toward explicit nonce semantics and AEAD-oriented protocol design.

---

## Conclusion

RC4 is one of the most useful historical stream ciphers to study because its design is compact but its failure modes are layered.

The cipher begins with a key-scheduled permutation:

\[
S:\{0,\ldots,255\}
\rightarrow
\{0,\ldots,255\}.
\]

The KSA updates:

\[
j
\leftarrow
j+S[i]+K[i\bmod|K|]
\pmod{256}
\]

and swaps:

\[
S[i]\leftrightarrow S[j].
\]

The PRGA then repeatedly updates \(i,j\), swaps two permutation entries, and outputs:

\[
Z
=
S[
(S[i]+S[j])\bmod256
].
\]

This looks highly irregular.

But the keystream is not ideal.

RC4 exhibits statistically measurable biases, including the famous elevated probability that its second output byte is zero.

That yields the first major lesson:

\[
\boxed{
\text{complex-looking state updates}
\neq
\text{ideal pseudorandomness}.
}
\]

WEP adds a second lesson.

Its public IV was combined with a long-term secret to create related per-packet RC4 keys.

The FMS attack exploited:

- early KSA structure;
- weak IV patterns;
- known plaintext;
- repeated related keys;
- statistical key-byte voting.

So:

\[
\boxed{
\text{key/nonce processing is part of cipher security}.
}
\]

TLS adds a third lesson.

Even without WEP's exact related-key structure, repeated RC4 sessions exposed enough biased keystream samples for plaintext-recovery attacks to become realistic research targets.

RFC 7465 therefore prohibited RC4 cipher suites in TLS.

Dropping early bytes was not a durable answer.

The correct modern conclusion is:

\[
\boxed{
\text{RC4 is obsolete and should not be deployed}.
}
\]

That makes RC4 a natural bridge to the next article.

So far the series has shown:

```text
LCG
    -> affine predictability

LFSR
    -> linear recurrence recovery

Geffe
    -> correlation leakage

RC4
    -> statistical keystream bias
```

The next question is:

> what does a modern software-oriented stream cipher look like after these lessons?

That leads directly to **ChaCha20**:

- ARX structure;
- quarter rounds;
- strong diffusion;
- explicit nonce/counter separation;
- modern protocol use;
- integration into ChaCha20-Poly1305.


---

## References

1. Ronald L. Rivest, **RC4**, historical proprietary design later publicly analyzed as ARC4-compatible implementations.

2. Scott Fluhrer, Itsik Mantin, and Adi Shamir, **Weaknesses in the Key Scheduling Algorithm of RC4**, Selected Areas in Cryptography, 2001.

3. Itsik Mantin and Adi Shamir, **A Practical Attack on Broadcast RC4**, Fast Software Encryption, 2001.

4. Andreas Klein, **Attacks on the RC4 Stream Cipher**, Designs, Codes and Cryptography, 2008.

5. Mathy Vanhoef and Frank Piessens, **All Your Biases Belong to Us: Breaking RC4 in WPA-TKIP and TLS**, USENIX Security, 2015.

6. Andrei Popov, **RFC 7465: Prohibiting RC4 Cipher Suites**, February 2015.  
   https://www.rfc-editor.org/rfc/rfc7465

7. Kenneth G. Paterson, Nadhem J. AlFardan, and related work on practical RC4/TLS bias exploitation.

8. Y. Nir and A. Langley, **RFC 8439: ChaCha20 and Poly1305 for IETF Protocols**, June 2018.  
   https://www.rfc-editor.org/rfc/rfc8439
