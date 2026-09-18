---
title: "Hash Security Properties and Attack Models"
description: "A rigorous treatment of preimage, second-preimage, and collision resistance; generic attack costs; truncation and birthday bounds; length extension, multicollisions, small-domain attacks, password hashing, and how to state exactly what a hash-security result means."
pubDate: "2026-08-12"
updatedDate: "2026-09-17"
topics:
  - "Hash Functions"
  - "Cryptanalysis"
  - "Mathematical Foundations"
tags:
  - "hash-functions"
  - "preimage"
  - "second-preimage"
  - "collision-resistance"
  - "birthday-bound"
  - "attack-models"
  - "length-extension"
  - "multicollision"
  - "password-hashing"
  - "sha1"
difficulty: "Intermediate"
series: "Hash Functions & MACs"
seriesOrder: 2
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---

## Table of Contents

- [From Compression to a Security Game](#from-compression-to-a-security-game)
- [Preimages, Second Preimages, and Collisions](#preimages-second-preimages-and-collisions)
- [Digest Length, Truncation, and Generic Attack Costs](#digest-length-truncation-and-generic-attack-costs)
- [Attack Taxonomy: What Exactly Was Broken?](#attack-taxonomy-what-exactly-was-broken)
- [Small Domains, Passwords, and Entropy](#small-domains-passwords-and-entropy)
- [Reproducible Labs: Collision, Preimage, and SHA-1](#reproducible-labs-collision-preimage-and-sha-1)
- [Practical Reasoning Checklist](#practical-reasoning-checklist)
- [Conclusion](#conclusion)
- [References](#references)

---

## From Compression to a Security Game

The first article in this series introduced a cryptographic hash as a deterministic fixed-output map

$$
H:\{0,1\}^{*}\rightarrow\{0,1\}^{n}.
$$

That definition tells us what the primitive **does**.

It does not yet tell us what it means for the primitive to be **secure**.

Because the message domain is effectively unbounded while the output space contains only

$$
2^n
$$

possible digests, collisions necessarily exist. A statement such as

> "this hash is secure because it has no collisions"

cannot literally be true.

The useful cryptographic question is instead:

> **Which task is the attacker trying to solve, what information is fixed before the attack starts, and how much work should that task require?**

This shift from an informal property to an explicit **security game** is important throughout cryptography.

A hash may resist one attack class while failing another.

For example:

- a practical collision does not automatically give a preimage attack;
- recovering a six-character password does not invert SHA-256 on arbitrary inputs;
- length extension does not produce a hash collision;
- finding a collision in a 16-bit truncation does not break the full 256-bit function.

The phrase

> "the hash was broken"

is therefore incomplete unless we say **what security claim failed**.

### Computational security, not impossibility

Modern cryptographic properties are normally computational.

For a secure hash we do **not** demand that a preimage, second preimage, or collision be mathematically impossible.

We demand that every feasible attacker have only negligible success probability unless it spends an infeasible amount of time, memory, or queries.

That means the security level depends on several things:

- output length,
- internal construction,
- attacker capabilities,
- number of oracle queries,
- available memory,
- target message length,
- whether many users or keys are attacked simultaneously,
- protocol context.

A single number such as "256-bit hash" is therefore a starting point, not a complete security analysis.

### A hash is not encryption or origin authentication

A digest is not encryption:

$$
H(M)
$$

has no normal decryption algorithm.

A digest also does not, by itself, prove who created a message.

If an attacker can replace both

```text
message
```

and

```text
hash(message)
```

then an unkeyed digest provides no authenticity.

That distinction becomes important later when we move from hashes to HMAC and other MACs.

### Idealized model versus named algorithms

When we say:

$$
\text{preimage cost}\approx2^n
$$

or

$$
\text{collision cost}\approx2^{n/2},
$$

we are describing the expected generic behavior of an idealized $n$-bit hash or random function model.

A named construction may have cryptanalytic structure that lowers the cost.

SHA-1 is the canonical example.

SHA-1 outputs 160 bits, so ideal collision resistance would suggest a generic scale around

$$
2^{80}.
$$

Practical SHA-1 collisions were nevertheless demonstrated using structure-specific differential cryptanalysis at significantly lower cost.

So generic bounds are not proofs that an algorithm achieves those bounds.

---

## Preimages, Second Preimages, and Collisions

The three classical resistance notions differ mainly in **what the attacker is allowed to choose**.

That distinction changes the generic cost dramatically.

### Preimage resistance

The attacker is given a target digest

$$
y\in\{0,1\}^{n}.
$$

The goal is to find any $x$ such that

$$
H(x)=y.
$$

The target is fixed before the search begins.

For an ideal $n$-bit hash, each independent trial has probability

$$
2^{-n}
$$

of hitting that exact target.

After $q$ independent trials, the success probability is approximately

$$
1-(1-2^{-n})^q.
$$

For

$$
q\ll2^n,
$$

we can approximate this as

$$
\Pr[\text{success}]
\approx
\frac{q}{2^n}.
$$

To obtain a constant success probability, the attacker therefore needs work on the scale

$$
2^n.
$$

For SHA-256, that idealized classical scale is roughly

$$
2^{256}.
$$

### Second-preimage resistance

Now the attacker is given a particular message

$$
x
$$

and must find a different message

$$
x'\neq x
$$

such that

$$
H(x')=H(x).
$$

The digest target is induced by a fixed existing message.

This is **not** the same as a collision problem because the attacker does not get to choose both endpoints freely.

For an ideal random $n$-bit hash, the generic second-preimage scale is again roughly

$$
2^n.
$$

This property is important when a specific object already exists.

Suppose a signature authenticates:

$$
H(M).
$$

If an attacker could cheaply construct

$$
M'\neq M
$$

with

$$
H(M')=H(M),
$$

then the digest would no longer uniquely bind the signature to the intended content in a computational sense.

### A subtlety: very long target messages

For ideal random functions, the simple $2^n$ intuition is appropriate.

For some **iterated hash constructions**, however, exceptionally long target messages can enable dedicated second-preimage techniques that beat the naive $2^n$ bound.

This is one reason real analysis cannot always stop at:

```text
digest length = n
therefore second preimage = 2^n
```

Construction details and message length can matter.

The practical takeaway for this series is not that ordinary files suddenly invalidate SHA-256 second-preimage resistance. It is that a precise cryptographic claim should specify the model rather than treating all hash constructions as ideal random functions.

### Collision resistance

For a collision, the attacker chooses both messages.

The goal is:

$$
x\neq x'
$$

such that:

$$
H(x)=H(x').
$$

That freedom creates the birthday phenomenon.

The attacker does not need to hit a particular digest.

Any matching pair is acceptable.

For an ideal $n$-bit hash, the generic collision scale is approximately

$$
2^{n/2}.
$$

For SHA-256:

$$
2^{128}.
$$

This is why a 256-bit digest provides at most about 128 bits of generic classical collision strength.

### Side-by-side comparison

| Security task | What is fixed before the search? | Goal | Ideal classical work |
|---|---|---|---:|
| Preimage | digest $y$ | find $x$ with $H(x)=y$ | $2^n$ |
| Second preimage | message $x$ | find $x'\neq x$ with $H(x')=H(x)$ | $2^n$ |
| Collision | neither message | find any $x\neq x'$ with equal digest | $2^{n/2}$ |

A useful mental model is:

```text
Preimage:
    fixed output

Second preimage:
    fixed first input

Collision:
    nothing fixed
```

The more freedom the attacker has, the cheaper the generic attack can become.

### Collision does not imply preimage

Suppose an attacker can efficiently produce:

$$
M_1\neq M_2
$$

with:

$$
H(M_1)=H(M_2).
$$

That says nothing immediate about whether the attacker can solve:

$$
H(X)=Y
$$

for an arbitrary externally chosen digest $Y$.

Collision cryptanalysis and preimage cryptanalysis solve different games.

This distinction is essential when discussing MD5 and SHA-1.

### Classical collision versus chosen-prefix collision

An ordinary collision attack allows the attacker to search for two complete colliding messages.

A **chosen-prefix collision** is more flexible.

The attacker starts from two chosen prefixes:

$$
P_1,
\qquad
P_2,
$$

and searches for suffixes $S_1,S_2$ such that:

$$
H(P_1\|S_1)
=
H(P_2\|S_2).
$$

This is much more useful in protocol abuse because the two messages can begin with meaningfully different attacker-selected content.

The progression is conceptually:

```text
collision
    -> find any two colliding messages

chosen-prefix collision
    -> choose two meaningful prefixes,
       then complete them into a collision
```

That distinction explains why later SHA-1 chosen-prefix results were more operationally threatening than a bare collision demonstration.

---

## Digest Length, Truncation, and Generic Attack Costs

The output length constrains generic security, but the relationship depends on the property.

### The birthday derivation

Assume a hash has:

$$
N=2^n
$$

possible outputs.

Hash $q$ distinct messages.

The probability that every digest is different is:

$$
\Pr[\text{no collision}]
=
\prod_{i=0}^{q-1}
\left(
1-\frac{i}{N}
\right).
$$

For

$$
q\ll N,
$$

using

$$
1-x\approx e^{-x},
$$

we obtain:

$$
\Pr[\text{no collision}]
\approx
\exp
\left(
-\frac{q(q-1)}{2N}
\right).
$$

Therefore:

$$
\Pr[\text{collision}]
\approx
1-
\exp
\left(
-\frac{q(q-1)}{2N}
\right).
$$

Setting the collision probability to approximately one half gives:

$$
q
\approx
\sqrt{2N\ln2}.
$$

Since

$$
N=2^n,
$$

we get:

$$
q
\approx
1.1774\cdot2^{n/2}.
$$

For a 16-bit output:

$$
q
\approx
1.1774\cdot256
\approx
301.
$$

So a collision after only a few hundred trials is exactly what generic probability predicts.

### Digest truncation

Suppose we compute SHA-256 but retain only the first $t$ bits:

$$
H_t(M)
=
\operatorname{Trunc}_t(
\operatorname{SHA256}(M)
).
$$

Even if full SHA-256 behaves ideally, the truncated function has at most:

$$
t
$$

bits of generic preimage resistance and:

$$
\frac{t}{2}
$$

bits of generic collision resistance.

For example:

| Digest kept | Preimage ceiling | Collision ceiling |
|---:|---:|---:|
| 256 bits | 256 bits | 128 bits |
| 192 bits | 192 bits | 96 bits |
| 128 bits | 128 bits | 64 bits |
| 64 bits | 64 bits | 32 bits |
| 16 bits | 16 bits | 8 bits |

So the statement:

> "This is SHA-256, therefore it has 128-bit collision security"

is false if only 64 output bits are actually stored or compared.

The security claim belongs to the **effective digest length**, not just the name of the underlying primitive.

### Authentication tags are a related but different case

Suppose a keyed authentication tag has length $t$.

A blind online forgery guess succeeds with probability:

$$
2^{-t}
$$

per independent attempt.

After $v$ attempts, for small $v/2^t$,

$$
\Pr[\text{at least one successful guess}]
\approx
\frac{v}{2^t}.
$$

This is not the birthday collision bound.

Why?

Because the attacker is trying to match a **specific valid tag**, not find any pair of equal tags.

This is another example of why the exact security game matters.

### Multi-target effects

If an attacker can target many independent digests at once, the effective attack cost can change.

Suppose there are $r$ target digests.

Each random candidate has probability roughly:

$$
\frac{r}{2^n}
$$

of matching one of them.

Large systems therefore need to consider:

- number of users,
- number of stored hashes,
- number of targets,
- number of protocol records,
- total attack lifetime.

Security strength is not always a single-user property.

### Quantum search: useful asymptotics, difficult engineering

In an idealized oracle model, Grover's algorithm can reduce generic preimage search from roughly

$$
2^n
$$

classical queries to roughly

$$
2^{n/2}
$$

quantum queries.

Generic quantum collision algorithms can also improve asymptotic query complexity beyond the classical birthday bound; a commonly cited idealized query scale is around:

$$
2^{n/3}.
$$

These asymptotic query counts should not be converted casually into statements such as:

> "SHA-256 has only 128-bit security against all quantum attacks."

Real quantum cost depends on:

- circuit depth,
- reversible implementation cost,
- qubit count,
- memory model,
- parallelism,
- error correction,
- physical runtime.

For engineering choices, use the security strength and algorithm profiles specified by current standards rather than relying only on an asymptotic slogan.

---

## Attack Taxonomy: What Exactly Was Broken?

A mature hash analysis should classify the attack before drawing conclusions.

| Attack type | Goal | What it demonstrates |
|---|---|---|
| Brute-force preimage | hit fixed digest | generic inversion cost |
| Second-preimage search | replace fixed target message | binding weakness if feasible |
| Birthday collision | find any equal pair | generic collision bound |
| Differential collision cryptanalysis | exploit internal structure | algorithm-specific collision weakness |
| Chosen-prefix collision | collide two chosen semantic prefixes | stronger collision control |
| Dictionary attack | search small input space | low input entropy |
| Length extension | continue certain iterated hashes | composition weakness |
| Multicollision | generate many colliding messages | structural property of iteration |
| Herding / expandable-message attack | connect commitments and suffixes | iterated-hash structural limitation |
| Side channel | exploit timing/cache/power/faults | implementation leakage |
| Encoding ambiguity | hash ambiguous serialization | protocol composition failure |

The diagnostic question is:

$$
\boxed{
\text{Which security game did the attacker actually win?}
}
$$

### Dictionary attacks do not break preimage resistance

Suppose a system stores:

$$
d
=
\operatorname{SHA256}(
\text{username}
\|
\texttt{"\_"}
\|
\text{password}
).
$$

Assume both username and password come from lists of only 500 likely values.

Then the total candidate space contains only:

$$
500^2
=
250{,}000
$$

pairs.

The attacker does not need to invert SHA-256 over its enormous full input domain.

They simply enumerate all likely candidates:

```python
for username in likely_usernames:
    for password in likely_passwords:
        candidate = sha256(
            username + b"_" + password
        )

        if candidate == target:
            return username, password
```

This may finish quickly while SHA-256 itself remains perfectly consistent with its preimage-security claim.

The weakness is:

$$
\text{low entropy of the input distribution}.
$$

### Encoding ambiguity is not cryptanalysis

Suppose we encode two fields by simple concatenation:

```text
ab || c
```

and:

```text
a || bc
```

Both become:

```text
abc
```

before hashing.

Then:

$$
H(\texttt{"ab"}\|\texttt{"c"})
=
H(\texttt{"a"}\|\texttt{"bc"})
$$

because the underlying byte strings are literally identical.

That is not a collision in the cryptanalytic sense.

The hash function received the same input.

The failure is ambiguous serialization.

Use a canonical encoding with:

- explicit lengths,
- structured serialization,
- domain labels,
- unambiguous field boundaries.

For example:

$$
H(
\texttt{"USERREC-v1"}
\|
\operatorname{len}(u)
\|
u
\|
\operatorname{len}(p)
\|
p
).
$$

### Domain separation

Suppose the same hash function is used for two logically different purposes:

```text
H(public_key_bytes)
```

and:

```text
H(transaction_bytes)
```

If their byte encodings overlap semantically, a protocol may accidentally accept a digest from one domain in another.

Domain separation prefixes the use case:

$$
H(
\texttt{"PUBLIC-KEY"}
\|
X
)
$$

versus:

$$
H(
\texttt{"TRANSACTION"}
\|
X
).
$$

The label should be:

- distinct,
- stable,
- unambiguous,
- included inside the hashed input.

Modern sponge-based constructions and functions such as cSHAKE and KMAC also provide standardized mechanisms for customization and domain separation.

### Length extension

Certain Merkle-Damgård-style hashes expose a useful internal chaining value as the final digest.

Given:

$$
H(M)
$$

and the length of $M$, an attacker can sometimes compute:

$$
H(
M
\|
\operatorname{pad}(M)
\|
X
)
$$

without knowing $M$.

This does **not** mean the attacker found:

- a collision,
- a preimage,
- or a second preimage.

The attacker has exploited the iterative structure to continue hashing from the exposed chaining state.

This becomes dangerous when someone invents a naive MAC such as:

$$
\operatorname{Tag}
=
H(K\|M)
$$

with a length-extension-vulnerable hash family.

An attacker who knows the tag and can infer the key length may be able to create a valid tag for an extended message.

This is one of the reasons standardized HMAC exists.

HMAC was designed specifically so that the obvious Merkle-Damgård length-extension interface does not turn into this forgery.

This connection makes length extension especially important in the **Hash Functions & MACs** series: it is the bridge between "a hash is secure" and "a composition using that hash is secure."

### Multicollisions and iterated structure

For an ideal random $n$-bit function, finding a large set of messages with one common digest might appear exponentially harder than finding one collision.

Iterated hash structures can behave differently.

Joux's multicollision technique showed that if a Merkle-Damgård hash permits a collision at one compression stage, those choices can be chained.

Conceptually:

```text
state_0
  |
 two colliding blocks
 / \
state_1
  |
 two colliding blocks
 / \
state_2
 ...
```

After $k$ collision-building stages, the attacker can obtain approximately:

$$
2^k
$$

different messages sharing one final hash, at cost closer to $k$ collision searches than to an independent $2^k$-way random-function search.

This does not automatically make the underlying hash unusable.

It demonstrates that an iterated construction can have structural properties that differ from a perfect random oracle.

### Herding and expandable messages

Herding attacks and expandable-message techniques exploit similar structural ideas.

The attacker may construct a large internal state structure first and later connect a chosen prefix or suffix into it.

These attacks are useful conceptually because they show why:

> "the compression function seems strong"

is not enough to characterize the security of the full iterated hash.

The outer construction matters.

### Side channels

Hash functions are often unkeyed and operate on public data.

But hashes are also used inside:

- HMAC,
- KDFs,
- signatures,
- password hashing,
- proof systems,
- secret-dependent protocols.

Once secret material enters the computation, implementation leakage can matter.

A side-channel attack may exploit:

- timing,
- memory access,
- power consumption,
- electromagnetic leakage,
- faults.

That is an implementation attack, not a mathematical collision or preimage attack.

---

## Small Domains, Passwords, and Entropy

Small-domain examples deserve their own section because they are often misdiagnosed as hash failures.

### The size of the candidate set dominates

Suppose a six-digit PIN is hashed with SHA-256.

There are only:

$$
10^6
$$

possible PINs.

An attacker who learns the digest can compute SHA-256 for every PIN.

The attack cost is not:

$$
2^{256}.
$$

It is approximately one million candidate evaluations.

Preimage resistance assumes a sufficiently large and unpredictable input domain.

It cannot manufacture entropy that the message never had.

### Salts

A password salt is a public per-record value.

Conceptually:

$$
V
=
\operatorname{PasswordHash}
(
P,
S,
\text{cost}
).
$$

The salt $S$ prevents an attacker from precomputing one reusable lookup table that works efficiently across many password records.

If Alice and Bob choose the same password but use different salts, their stored verifiers should differ.

A salt is:

- not a password,
- not normally secret,
- not a replacement for a slow password-hashing scheme.

### Why fast hashes are wrong for password storage

General-purpose hashes such as SHA-256 are intentionally fast.

For normal cryptographic hashing, that is a feature.

For password verification after a database breach, it is a problem.

An offline attacker can test guesses extremely quickly.

Password hashing therefore deliberately adds cost.

A password-hashing scheme typically takes:

$$
(P,S,c)
$$

where:

- $P$ is the password,
- $S$ is the salt,
- $c$ is a cost parameter.

The goal is to make **every guess expensive**.

Current NIST SP 800-63B-4 requires centrally verified passwords to be salted and hashed using a suitable password-hashing scheme and recommends choosing the cost factor as high as practical without harming verifier performance, increasing it over time as computing power improves.

This means:

```text
SHA256(password)
```

is not a complete password-storage design.

### Salt versus pepper

A **salt** is stored beside the verifier.

A **pepper** is an additional secret held separately from the password database.

Conceptually:

```text
database:
    salt
    password verifier
    algorithm parameters

separate protected secret:
    pepper / verifier-side key
```

If the password database leaks but the separate secret remains protected, offline cracking can become harder.

A pepper is not a substitute for:

- proper salts,
- password hashing cost,
- access control,
- rate limiting,
- breach response.

It is an additional architectural defense.

### Online versus offline guessing

Online guessing:

```text
attacker -> login server -> one guess
```

can be controlled by:

- rate limiting,
- lockout policies,
- risk controls,
- MFA.

Offline guessing after a verifier database breach:

```text
attacker owns verifier data
-> guesses locally
```

cannot be rate-limited by the server.

That is why password-verifier cost and salt design matter even if the login endpoint already rate-limits requests.

---

## Reproducible Labs: Collision, Preimage, and SHA-1

The original project includes two useful labs.

They illustrate not only attacks, but how to report them correctly.

### Lab A: same hash, different attack freedom

The script:

[`code/birthday_collision.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/birthday_collision.py)

truncates SHA-256 to a teaching-sized output.

A minimal local version is:

```python
import hashlib

def H16(data: bytes) -> int:
    return int.from_bytes(
        hashlib.sha256(data).digest()[:2],
        "big",
    )
```

Now compare two experiments.

#### Collision search

```python
def find_collision():
    seen = {}

    i = 0

    while True:
        candidate = f"input_{i}".encode()
        h = H16(candidate)

        if h in seen:
            return (
                seen[h],
                candidate,
                h,
                i + 1,
            )

        seen[h] = candidate
        i += 1
```

The deterministic sequence finds:

```text
input_135
input_473
```

with digest:

```text
0xae85
```

after 474 candidate evaluations.

That is exactly the expected "few hundred" birthday scale for a 16-bit output.

#### Fixed-target preimage search

Now fix a target first:

$$
y=\texttt{0x1234}.
$$

```python
def find_preimage(target):
    i = 0

    while True:
        candidate = f"preimage_{i}".encode()

        if H16(candidate) == target:
            return candidate, i + 1

        i += 1
```

For the deterministic input sequence used in this article, the first hit occurs after many more evaluations than the collision experiment.

That is the lesson:

```text
same underlying SHA-256
same 16-bit truncation
different attacker's freedom
different generic complexity
```

Collision:

$$
\approx2^8
$$

work.

Fixed-target preimage:

$$
\approx2^{16}
$$

work.

### Exact probability intuition

For a 16-bit target, one trial succeeds with probability:

$$
\frac{1}{65536}.
$$

The expected number of geometric trials is:

$$
65536.
$$

A particular deterministic sequence can hit sooner or later. The expectation is a distributional statement, not a guarantee that the $65,536$-th candidate succeeds.

### Lab B: historical SHA-1 collisions

The project also contains:

[`code/sha1_collision_demo.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha1_collision_demo.py)

which verifies two published distinct 320-byte messages:

```text
SHA-1(message 1)
= f92d74e3874587aaf443d1db961d4e26dde13e9c

SHA-1(message 2)
= f92d74e3874587aaf443d1db961d4e26dde13e9c
```

while their SHA-256 digests differ.

The program **verifies** a known collision.

It does not reproduce the expensive cryptanalytic search that originally created the pair.

That wording matters.

Verification is easy:

```python
sha1(m1) == sha1(m2)
```

Collision construction is the difficult cryptanalytic achievement.

### SHAttered

In 2017, the SHAttered project demonstrated the first practical public collision for full SHA-1 using two distinct PDF files.

This result broke SHA-1's practical collision-resistance claim.

It did **not** give an efficient general procedure for:

$$
\text{given arbitrary }y,
\quad
\text{find }x\text{ with SHA1}(x)=y.
$$

So SHA-1 collision resistance was broken without a corresponding general preimage break.

### Chosen-prefix SHA-1

Later work demonstrated practical chosen-prefix collisions for SHA-1.

The attacker can begin from two different chosen prefixes and generate suffixes that make the full messages collide.

That is a stronger capability for protocol manipulation.

A useful progression is:

$$
\text{collision}
\rightarrow
\text{chosen-prefix collision}
$$

but neither should be mislabeled as arbitrary second-preimage recovery.

### Current standards context

NIST has announced a transition away from SHA-1 for all applications by December 31, 2030 and recommends moving to SHA-2 or SHA-3.

NIST has also decided that the next revision of FIPS 180 will remove the SHA-1 specification.

So SHA-1 belongs in this article because it is an exceptionally instructive cryptanalytic case study, not because it should be selected for new collision-sensitive protocol designs.

---

## Practical Reasoning Checklist

A hash security statement should answer several questions before it is trusted.

### What function and construction are we discussing?

Not merely:

```text
SHA
```

but:

```text
SHA-256
SHA3-256
SHAKE256 with 256 output bits
HMAC-SHA-256
truncated SHA-256 to 128 bits
```

The construction and output length matter.

### What security property is required?

Do we need:

- preimage resistance?
- second-preimage resistance?
- collision resistance?
- keyed authentication?
- password-verifier resistance?
- random-oracle-like behavior in a proof?
- domain separation?

Different applications require different properties.

### What is the attacker given?

Ask explicitly:

```text
fixed digest?
fixed message?
neither?
many targets?
oracle access?
chosen prefixes?
```

This often determines the correct generic complexity immediately.

### What is the effective output length?

If SHA-256 is truncated to 96 bits:

$$
\text{preimage ceiling}\approx96\text{ bits},
$$

$$
\text{collision ceiling}\approx48\text{ bits}.
$$

Do not quote the security of the untruncated primitive.

### How much entropy does the input have?

A 256-bit hash does not turn a six-digit PIN into a 256-bit secret.

Security is bounded by the smaller effective search space.

### Is the encoding unambiguous?

Use:

- length prefixes,
- fixed-width fields,
- canonical serialization,
- domain labels.

Do not rely on visual interpretation of concatenated strings.

### Is the hash being used as a MAC?

If yes, stop and ask why a standardized keyed construction such as HMAC or KMAC is not being used.

Do not assume:

$$
H(K\|M)
$$

or:

$$
H(M\|K)
$$

has the properties of a well-analyzed MAC.

### Is password storage involved?

Use a suitable password-hashing scheme with:

- a per-record salt,
- a cost parameter,
- migration metadata,
- rate limiting at the online layer,
- optionally a separately protected verifier-side secret where architecture permits.

Do not use one fast SHA-256 call as the password verifier.

### Is the algorithm still approved for the application?

For new work:

- avoid SHA-1 for collision-sensitive uses,
- prefer algorithms and profiles approved by the protocol or current standard,
- do not infer approval solely from the presence of an implementation in a software library.

### What did the experiment actually prove?

A toy experiment might demonstrate:

- the birthday bound,
- truncation behavior,
- a known published collision,
- a composition flaw,
- a low-entropy attack.

State exactly that.

Do not turn:

```text
I found a collision in 16-bit truncated SHA-256
```

into:

```text
I broke SHA-256.
```

That precision is part of cryptographic methodology.

---

## Conclusion

Hash security is not one monolithic property.

A useful analysis begins with the exact attack game.

For an $n$-bit ideal hash:

$$
\boxed{
\text{preimage}\sim2^n
}
$$

$$
\boxed{
\text{second preimage}\sim2^n
}
$$

$$
\boxed{
\text{collision}\sim2^{n/2}
}
$$

because the attacker has different freedom in each problem.

Digest truncation changes those ceilings immediately.

A $t$-bit truncation provides at most:

$$
t
$$

bits of generic preimage security and:

$$
\frac{t}{2}
$$

bits of generic collision security.

Small-domain attacks remind us that the entropy of the input can dominate the hash output size.

Length extension, multicollisions, herding, and chosen-prefix attacks show a second lesson:

> the internal construction and the surrounding protocol matter.

A hash may remain preimage resistant while a naive MAC built from it fails.

A 160-bit output may exist while practical collision attacks beat the generic birthday estimate.

A password database may fall to a dictionary search without revealing any weakness in SHA-256.

That leads to a useful diagnostic rule:

$$
\boxed{
\text{Always name the security game that failed.}
}
$$

Instead of saying:

```text
"the hash is broken"
```

say:

```text
"collision resistance is broken"
```

or:

```text
"the protocol is vulnerable to length extension"
```

or:

```text
"the password domain is small enough to enumerate"
```

or:

```text
"the digest was truncated to a collision-inadequate length."
```

That precision is not cosmetic. It tells us which defense is actually needed.

The next articles in the series can now build on this vocabulary: the birthday bound in greater depth, hash construction internals, and eventually HMAC—where we will see how a secure hash is turned into a secure keyed authenticator without falling into the composition traps described here.

---

## References

1. National Institute of Standards and Technology, **FIPS 180-4: Secure Hash Standard (SHS)**.  
   https://doi.org/10.6028/NIST.FIPS.180-4

2. National Institute of Standards and Technology, **NIST Policy on Hash Functions**.  
   https://csrc.nist.gov/Projects/Hash-Functions/NIST-Policy-on-Hash-Functions

3. National Institute of Standards and Technology, **Decision to Revise FIPS 180-4, Secure Hash Standard**, March 2023.  
   https://csrc.nist.gov/news/2023/decision-to-revise-fips-180-4

4. National Institute of Standards and Technology, **SP 800-63B-4: Digital Identity Guidelines — Authentication and Authenticator Management**, July 2025.  
   https://doi.org/10.6028/NIST.SP.800-63b-4

5. M. Stevens et al., **The First Collision for Full SHA-1**, CRYPTO 2017.

6. G. Leurent and T. Peyrin, **SHA-1 is a Shambles: First Chosen-Prefix Collision on SHA-1 and Application to the PGP Web of Trust**, USENIX Security 2020.

7. A. Joux, **Multicollisions in Iterated Hash Functions: Application to Cascaded Constructions**, CRYPTO 2004.

8. J. Kelsey and B. Schneier, **Second Preimages on n-bit Hash Functions for Much Less than $2^n$ Work**, EUROCRYPT 2005.

9. J. Kelsey and T. Kohno, **Herding Hash Functions and the Nostradamus Attack**, EUROCRYPT 2006.
