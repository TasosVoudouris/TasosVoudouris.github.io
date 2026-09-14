---
title: "Merkle–Damgård and SHA-256"
description: "Build the Merkle–Damgård iteration from compression functions, follow SHA-256 padding, schedule and rounds, and connect the construction to its structural security consequences."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Cryptographic Engineering"
tags:
  - "merkle-damgard"
  - "sha256"
  - "compression-function"
  - "davies-meyer"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 4
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. The fixed-input-length problem

Cryptographic permutations, block ciphers, and compression functions operate on fixed-size states and blocks, while applications hash messages of arbitrary length. The Merkle–Damgård paradigm turns a fixed-input-length compression function into an iterated hash.

Let

\[
f:\{0,1\}^{n}\times\{0,1\}^{b}\rightarrow\{0,1\}^{n}
\]

take an (n)-bit chaining value and a (b)-bit message block. After padding a message into (M_1,\ldots,M_\ell), define

\[
h_0=IV,\qquad h_i=f(h_{i-1},M_i),\qquad H(M)=h_\ell.
\]

![Merkle–Damgård iteration](/images/hash-functions/merkle-damgard-sha256/merkle.png)

The initial value (IV) and the padding rule are part of the function definition. Changing either defines a different hash.

## 2. MD strengthening and padding

A safe statement of the classical collision-preservation theorem needs a suffix-free or appropriately length-encoding padding rule. *MD strengthening* appends a `1` bit, enough zero bits, and a fixed-width representation of the original message length. This makes the padded block sequence encode where the message ended.

For SHA-256, a byte-aligned message of length (L) bytes is padded as:

1. append byte `0x80` (the `1` bit followed by seven zero bits);
2. append zero bytes until the length is congruent to 56 modulo 64;
3. append the original bit length (8L) as an unsigned 64-bit big-endian integer.

The padded length is a positive multiple of 64 bytes. Thus:

- a 55-byte message receives 9 padding bytes and ends in one block;
- a 56-byte message receives 72 padding bytes and needs a second block;
- an empty message receives one full 64-byte padded block.

The length field supports unambiguous iteration and the collision-reduction argument. It does **not** hide the internal state and does **not** prevent length-extension attacks.

## 3. Why collision resistance can be inherited

Assume the compression function is collision resistant and the padding makes no valid padded message a suffix of another in the way required by the reduction. Suppose two distinct messages (M\ne M') yield the same final digest.

Compare their padded block chains backward from the equal final state:

- If the last blocks differ while the prior chaining values are equal, the final compression inputs form a collision in (f).
- If the last blocks agree, move one step backward. Continue until the first differing compression input is located.
- Length encoding prevents one valid chain from being silently treated as the tail of another without eventually exposing such a difference.

Therefore, a collision for the iterated hash can be converted into a collision for the compression function. This is a reduction under explicit assumptions, not a statement that every property of an ideal variable-length random oracle is inherited.

## 4. Structural consequences of iteration

Merkle–Damgård hashing has useful and dangerous structure:

- **Streaming:** retain only the chaining state and a partial block.
- **Fixed-size digest:** storage is independent of message length.
- **Parallel limitation:** a single chain is inherently sequential, although implementations can parallelize independent messages.
- **Length extension:** the digest exposes the final chaining value for many constructions, so an attacker can process suffix blocks.
- **Multicollisions:** Joux showed that a (2^k)-way multicollision can be assembled from (k) ordinary collision stages, much more cheaply than for an ideal random function with the same output length.
- **Herding/expandable-message techniques:** chosen intermediate states can support commitment-style attacks under particular conditions.
- **Long-message second preimages:** generic structural attacks can beat the naive (2^n) estimate for extremely long target messages.

These results do not mean SHA-256 is generally broken. They mean “an iterated hash behaves exactly like a random oracle in every protocol” is too strong an assumption.

## 5. Davies–Meyer as a compression pattern

A common block-cipher-based compression mode is Davies–Meyer:

\[
f(h,m)=E_m(h)\oplus h,
\]

where the message block (m) acts as the block-cipher key, (h) is the block input, and feed-forward XOR prevents direct inversion of the block cipher from directly inverting the compression function.

![Davies–Meyer compression](/images/hash-functions/merkle-damgard-sha256/daviesmeyer.png)

Calling a component a “block cipher” does not automatically make every arrangement secure. The placement of the key, message, chaining value, and feed-forward operation matters. The PGV analysis classifies many one-call constructions in an ideal-cipher model.

SHA-256's compression can be viewed as Davies–Meyer-like feed-forward around a 64-round keyed transformation related to SHACAL-2: the old state is added word-by-word to the round output. FIPS 180-4, however, specifies SHA-256 directly; describing it as literally invoking a separately standardized block cipher is a conceptual model, not the algorithm's API.

## 6. SHA-256 parameters

| Parameter | SHA-256 value |
|---|---:|
| Digest/chaining state | 256 bits = eight 32-bit words |
| Message block | 512 bits = sixteen 32-bit words |
| Expanded schedule | sixty-four 32-bit words |
| Rounds per block | 64 |
| Length field | 64 bits |
| Maximum specified message length | less than (2^{64}) bits |
| Word byte order | big-endian |

The eight initial words are fractional parts derived from square roots of the first eight primes; the 64 round constants are derived from cube roots of the first 64 primes. These derivations make the constants reproducible, not secret.

## 7. Message schedule

Parse one block into (W_0,\ldots,W_{15}). For (16\le t<64), compute

\[
W_t=\sigma_1(W_{t-2})+W_{t-7}+\sigma_0(W_{t-15})+W_{t-16}\pmod{2^{32}},
\]

where

\[
\sigma_0(x)=\operatorname{ROTR}^7(x)\oplus\operatorname{ROTR}^{18}(x)\oplus\operatorname{SHR}^3(x),
\]

\[
\sigma_1(x)=\operatorname{ROTR}^{17}(x)\oplus\operatorname{ROTR}^{19}(x)\oplus\operatorname{SHR}^{10}(x).
\]

Rotation preserves all bits but changes positions. Logical right shift inserts zeroes and discards bits; substituting one for the other changes the algorithm.

## 8. Round function

Initialize working words (a,b,c,d,e,f,g,h) from the current chaining state. Define

\[
\operatorname{Ch}(x,y,z)=(x\land y)\oplus(\neg x\land z),
\]

\[
\operatorname{Maj}(x,y,z)=(x\land y)\oplus(x\land z)\oplus(y\land z),
\]

\[
\Sigma_0(x)=\operatorname{ROTR}^2(x)\oplus\operatorname{ROTR}^{13}(x)\oplus\operatorname{ROTR}^{22}(x),
\]

\[
\Sigma_1(x)=\operatorname{ROTR}^6(x)\oplus\operatorname{ROTR}^{11}(x)\oplus\operatorname{ROTR}^{25}(x).
\]

At round (t):

\[
T_1=h+\Sigma_1(e)+\operatorname{Ch}(e,f,g)+K_t+W_t\pmod{2^{32}},
\]

\[
T_2=\Sigma_0(a)+\operatorname{Maj}(a,b,c)\pmod{2^{32}}.
\]

Then shift the working registers and set the new (a=T_1+T_2) and (e=d+T_1), modulo (2^{32}). After 64 rounds, add each working word to its corresponding input-state word modulo (2^{32}). That feed-forward produces the next chaining state.

![SHA-256 structure](/images/hash-functions/merkle-damgard-sha256/sha256.png)

## 9. Educational implementation

[`code/sha256_educational.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha256_educational.py) separates the algorithm into auditable operations:

- `sha256_padding(length)` operates on an explicit byte length and preserves empty or leading-zero messages;
- `_schedule(block)` parses exactly 64 bytes into big-endian words;
- `compress(state, block)` performs one FIPS 180-4 compression;
- `sha256(message)` applies the standard IV and padding;
- `digest_to_state` and `continue_from_digest` intentionally expose the state interface needed by the next chapter.

The implementation avoids the original integer-conversion trap: `bytes_to_long(b"\x00abc")` loses the leading zero and cannot recover the original byte length. Cryptographic padding is defined over the exact bit string, so byte strings remain byte strings until words are parsed.

Validation compares the educational function with `hashlib.sha256` for:

```text
""
"abc"
55, 56, and 64 repeated bytes
1,000 repeated bytes
```

This tests the standard vector and both sides of the padding-block boundary. It is necessary regression coverage, not an independent security certification.

## 10. Using SHA-256 correctly

- Use the platform's maintained SHA-256 implementation, not this lab, in production.
- A plain digest can detect accidental changes only when the expected digest arrives through a trusted channel.
- For message authentication, use HMAC-SHA-256 or the protocol's standardized MAC—not `SHA256(key || message)`.
- For password storage, use a dedicated salted password-hashing scheme.
- Hash structured data only after defining canonical encoding and domain separation.
- Do not assume a 256-bit digest means 256-bit collision security; the generic collision level is about 128 bits.

Primary algorithm source: [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final).

Previous: [Birthday Attacks](/blog/birthday-attacks-hash-functions/).

Next: [Length-Extension Attacks](/blog/length-extension-attacks/).
