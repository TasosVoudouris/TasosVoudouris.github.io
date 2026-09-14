---
title: "Hash Security Properties and Attack Models"
description: "Preimage, second-preimage, and collision resistance; generic attack costs; small-domain caveats; and how to reason about a hash function’s actual security claim."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
tags:
  - "hash-functions"
  - "preimage"
  - "second-preimage"
  - "collision-resistance"
  - "attack-models"
difficulty: "Intermediate"
series: "Hash Functions & MACs"
seriesOrder: 2
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. From compression to a security claim

A fixed-output cryptographic hash function is a deterministic map

\[
H:\{0,1\}^{*}\rightarrow\{0,1\}^{n}.
\]

It accepts an arbitrary finite byte string and produces an (n)-bit digest. Because the input domain is larger than the output range, collisions must exist. Security therefore never means *collision-free*. It means that a precisely defined adversarial task should require infeasible resources.

A digest is not encryption: it has no decryption operation and provides no confidentiality. It is not automatically a proof of origin either: if anyone can replace a message, that person can normally replace its unkeyed digest as well.

## 2. Three core resistance properties

### 2.1 Preimage resistance

Given a target (y\in\{0,1\}^{n}), find any (x) such that (H(x)=y).

For an ideal (n)-bit hash, a classical generic search needs about (2^n) evaluations. The target is fixed before the search.

### 2.2 Second-preimage resistance

Given a particular message (x), find a different (x'\ne x) such that (H(x')=H(x)).

The generic cost is also about (2^n) for an ideal hash. This is not a collision search: the attacker does not get to choose both endpoints freely. Iterated constructions can have subtleties for extremely long target messages, so a real analysis must include the construction and message length rather than quoting only the output size.

### 2.3 Collision resistance

Find any pair (x\ne x') for which (H(x)=H(x')).

An ideal (n)-bit function offers only about (n/2) bits of classical collision strength. The birthday effect lets the attacker choose both messages and find a match after approximately (2^{n/2}) evaluations and comparable storage in the simplest table attack.

| Task | What is fixed? | Generic classical work for an ideal (n)-bit output |
|---|---|---:|
| Preimage | Digest (y) | (2^n) |
| Second preimage | Message (x) | (2^n) |
| Collision | Neither message | (2^{n/2}) |

These are generic upper bounds, not proofs that a named algorithm reaches them. Cryptanalysis can find structure-specific attacks that are cheaper. SHA-1 is the central example: it has a 160-bit digest, but practical collisions have been computed far below the ideal (2^{80}) work factor.

## 3. Supporting design properties

Terms such as *avalanche*, *diffusion*, and *uniform-looking output* are valuable design and testing intuitions, but they do not replace the three games above.

- **Avalanche behavior:** changing one input bit should typically change about half the digest bits. A function can pass avalanche tests and still be cryptographically broken.
- **Regularity resistance:** biased or algebraically related outputs can reveal non-random structure.
- **Domain separation:** the same primitive should not confuse values used for different purposes. Hash `context || encoded_data`, where `context` is unique and the encoding is unambiguous.
- **Indifferentiability or random-oracle-style arguments:** some constructions support stronger composition claims, but only under their stated model and query bounds.
- **Side-channel resistance:** a public, unkeyed hash often processes public data, but keyed modes and password schemes handle secrets. Their implementations must avoid secret-dependent timing and memory access where the threat model requires it.

## 4. The digest length is not the whole security level

Truncating a secure digest to (t) bits caps generic preimage strength near (t) bits and collision strength near (t/2) bits. A 128-bit digest therefore provides at most roughly 64-bit collision resistance; it should not be described as “128-bit collision security.”

For an online (t)-bit authentication tag, a simple blind guess succeeds with probability (2^{-t}) per verification attempt. After (v) independent attempts, the success probability is approximately (v/2^t) while (v\ll2^t). Rate limits and the number of protected records are therefore part of a truncation decision.

Quantum search changes asymptotic query counts in idealized models: Grover search gives a square-root improvement for preimages, while generic quantum collision algorithms have different time–memory assumptions. Translating query complexity into a deployable quantum attack is nontrivial. Parameter selection should follow the current standard governing the application, not an isolated asymptotic slogan.

## 5. Attack taxonomy

| Attack | Attacker's goal | Does it break the full hash? |
|---|---|---|
| Brute-force preimage | Invert a fixed digest | Only at the claimed generic cost |
| Dictionary attack | Search a small, predictable input domain | No; it exploits low input entropy |
| Birthday collision | Find any match in a small/truncated output | No if truncation is intentionally tiny; it illustrates the generic bound |
| Differential collision cryptanalysis | Construct colliding messages using internal structure | Yes, for collision-resistance uses of that algorithm |
| Length extension | Continue certain iterated hashes from a digest | Breaks constructions such as a secret-prefix MAC, not collision resistance |
| Multicollision/herding | Exploit iteration to connect many messages or chosen commitments | Reveals structural limits beyond a random-function intuition |
| Side channel | Recover secrets through timing, power, cache, or faults | Attacks an implementation and usage mode |
| Protocol/encoding confusion | Make different semantic objects share authenticated bytes | Attacks composition, often without cryptanalyzing the primitive |

The most important diagnostic question is: **which security game did the attacker win?** A collision is not automatically a preimage. A length-extension forgery is not a collision. Recovering a six-character password does not invert SHA-256 over arbitrary inputs.

## 6. Small-domain inputs and password hashing

Suppose a database stores

\[
d=\operatorname{SHA256}(\text{username}\mathbin\|\texttt{"_"}\mathbin\|\text{password})
\]

and both fields come from lists of 500 likely values. The candidate domain has only (500^2=250{,}000) pairs. An attacker can enumerate it quickly even though SHA-256 itself remains preimage resistant over its full domain. A separator does not add entropy; if fields can contain the separator, it may not even give a unique encoding.

Password verification deliberately needs a *slow, salted, tunable* password-hashing scheme:

1. Generate a fresh random salt for each password record.
2. Apply an approved password-hashing scheme with a recorded cost parameter.
3. Raise the cost over time as hardware improves.
4. Rate-limit online authentication independently; salts do not stop online guessing.
5. Optionally protect the verifier with a separately stored server secret (“pepper”) if the architecture and recovery plan support it.

An ordinary fast SHA-256/SHA-3 digest is unsuitable. HMAC alone is also not a password-hashing scheme: it is designed to authenticate high-entropy-keyed messages efficiently. See current [NIST SP 800-63B-4](https://csrc.nist.gov/pubs/sp/800/63/b/4/final) and the password scheme required by the application's platform.

## 7. Lab A: collision versus preimage

[`code/birthday_collision.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/birthday_collision.py) truncates SHA-256 to a teaching-sized output. It exposes two different experiments:

```python
collision = find_collision(bits=16)
candidate, evaluations = find_preimage(target=0x1234, bits=16)
```

The collision search retains a digest table and normally finishes after hundreds of evaluations. A fixed-target preimage search normally needs tens of thousands. Both use the same underlying SHA-256; only the attacker's freedom changes.

## 8. Lab B: the historical SHA-1 collision

[`code/sha1_collision_demo.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha1_collision_demo.py) verifies two published, distinct 320-byte messages:

```text
SHA-1(message 1) = f92d74e3874587aaf443d1db961d4e26dde13e9c
SHA-1(message 2) = f92d74e3874587aaf443d1db961d4e26dde13e9c
```

Their SHA-256 digests differ. The code **verifies** a known collision; it does not reproduce the expensive differential search that found it.

The 2017 SHAttered work produced the first practical public collision for full SHA-1. A collision lets an attacker prepare two documents with the same digest before a victim authenticates one. It does not let the attacker take an arbitrary already-hashed document and find a matching replacement at will. The later chosen-prefix result is stronger: it allows two attacker-chosen prefixes to be completed into colliding messages, making protocol abuse much more flexible. See [The First Collision for Full SHA-1](https://shattered.io/static/shattered.pdf) and [SHA-1 is a Shambles](https://eprint.iacr.org/2020/014).

## 9. Practical selection checklist

- Use a currently approved algorithm and mode for the exact application.
- Choose digest/tag length from the needed *security strength*, data lifetime, query volume, and multi-user setting.
- Authenticate downloads through a trusted signature or authenticated channel; a checksum posted beside a compromised file is replaceable.
- Serialize structured inputs canonically and include a versioned domain label.
- Never invent a keyed hash construction when HMAC, KMAC, CMAC, keyed BLAKE2, or an application standard already specifies one.
- Do not use SHA-1 for new collision-sensitive applications.
- Treat a proof-system hash as a protocol-specific primitive, not as a universal replacement for conventional hashes.

Next: [The Birthday Bound](/blog/birthday-attacks-hash-functions/).
