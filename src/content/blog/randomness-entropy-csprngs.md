---
title: "Randomness in Cryptography: Entropy, CSPRNGs, and Operating-System Randomness"
description: "Understand what entropy actually measures, how physical uncertainty becomes cryptographic randomness, how CSPRNGs expand secure state, and why different cryptographic values require different randomness properties."
pubDate: "2025-05-21"
updatedDate: "2026-09-14"
topics:
  - "Randomness & Entropy"
  - "Cryptography Fundamentals"
  - "Cryptographic Engineering"
tags:
  - "entropy"
  - "min-entropy"
  - "csprng"
  - "randomness"
  - "operating-system"
  - "nonce"
  - "secrets"
difficulty: "Introductory"
series: "Cryptography Primer"
seriesOrder: 4
draft: false
---

Cryptography repeatedly asks us to generate values that an adversary must not be able to predict.

A private key must be chosen from a sufficiently large space. A signature nonce may have to remain secret and never repeat. An authentication challenge must be fresh. An IV may need unpredictability, uniqueness, or both depending on the construction. A salt does not even need to be secret, but it should normally be unique.

All of these are often described casually as *random values*, but that phrase hides several different ideas.

A computer does not normally obtain every cryptographic key directly from some continuously flowing source of perfect physical randomness. Instead, real systems form a pipeline:

\[
\boxed{
\text{physical uncertainty}
\longrightarrow
\text{entropy source}
\longrightarrow
\text{conditioning}
\longrightarrow
\text{seed/state}
\longrightarrow
\text{CSPRNG}
\longrightarrow
\text{cryptographic values}
}
\]

Understanding randomness therefore requires us to separate **entropy**, **random physical observations**, and **pseudorandom generation**.

That distinction is not merely terminology. Many catastrophic cryptographic failures have occurred even when the encryption or signature algorithm itself was mathematically correct, because the surrounding randomness assumptions were not.

## Entropy is uncertainty, not simply "random-looking data"

Suppose \(X\) is a random variable taking values \(x\) with probabilities \(p(x)\).

One classical measure of uncertainty is **Shannon entropy**:

\[
H(X)
=
-\sum_x p(x)\log_2 p(x).
\]

Shannon entropy measures the *average* information obtained when the outcome becomes known.

If \(X\) is uniformly distributed over \(2^k\) possible outcomes, then

\[
H(X)=k.
\]

A fair eight-sided die therefore contains

\[
\log_2 8 = 3
\]

bits of Shannon entropy.

But cryptography often cares about a more adversarial question:

> What is the probability that the attacker guesses the value correctly on the first attempt?

That leads naturally to **min-entropy**:

\[
H_\infty(X)
=
-\log_2
\left(
\max_x p(x)
\right).
\]

Min-entropy is controlled entirely by the most likely outcome.

Consider a source with four possible outcomes:

\[
\Pr[X=0]=\frac12,
\qquad
\Pr[X=1]=\frac14,
\qquad
\Pr[X=2]=\frac18,
\qquad
\Pr[X=3]=\frac18.
\]

Its Shannon entropy is

\[
H(X)
=
\frac12(1)
+
\frac14(2)
+
\frac18(3)
+
\frac18(3)
=
1.75
\text{ bits}.
\]

But an attacker can simply guess \(X=0\) and succeed with probability \(1/2\). Therefore,

\[
H_\infty(X)
=
-\log_2(1/2)
=
1
\text{ bit}.
\]

This difference is extremely important.

Shannon entropy tells us something about average uncertainty. Min-entropy tells us much more directly how concentrated the distribution is around its most likely value.

For cryptographic key generation and entropy extraction, this worst-case concentration is often the more relevant quantity.

There is another subtlety: entropy must be considered relative to what the adversary already knows.

Suppose a machine generates a 128-bit value, but an attacker already knows all except 20 uncertain bits. The representation is still 128 bits long, yet the attacker's effective uncertainty may be only around

\[
20\text{ bits}.
\]

This is why **bit length is not entropy**.

A 256-bit string does not automatically contain 256 bits of entropy.

For example, suppose a program chooses a value from only \(2^{20}\) possibilities and then hashes it with SHA-256:

\[
x
\in
\{0,\ldots,2^{20}-1\},
\]

\[
y=\operatorname{SHA256}(x).
\]

The output \(y\) is 256 bits long and will probably *look* random.

But an attacker still has only about

\[
2^{20}
\]

candidate inputs to test.

The hash has rearranged and compressed the uncertainty. It has not magically created another 236 bits of entropy.

More generally, deterministic processing cannot manufacture fresh uncertainty that was not present in its inputs.

That distinction will appear repeatedly in cryptographic engineering:

\[
\boxed{
\text{output size}
\neq
\text{entropy}
\neq
\text{security level}
}
\]

### Where does entropy come from?

Eventually, some uncertainty must enter the machine from outside its deterministic computation.

Potential noise sources include timing variations, oscillator jitter, device events, hardware random-number generators, thermal or electrical noise, and specially designed physical random generators.

But raw physical measurements are rarely suitable for direct use as keys.

A physical source may be:

- biased,
- correlated over time,
- partially predictable,
- affected by temperature or hardware state,
- observable by an attacker,
- or simply broken.

So the real process is closer to

\[
\text{noise source}
\rightarrow
\text{measurement}
\rightarrow
\text{health testing}
\rightarrow
\text{conditioning}
\rightarrow
\text{entropy estimate}.
\]

The purpose of conditioning is to transform imperfect source data into a representation that is more suitable for use by the random-bit-generation system.

This does **not** mean that a hash function somehow creates entropy. Rather, a secure conditioning function can compress and distribute the uncertainty already present in the source.

A simplified example might be

\[
s
=
H(
\text{domain}
\parallel
x_1
\parallel
x_2
\parallel
\cdots
\parallel
x_k
),
\]

where the \(x_i\) are measurements collected from one or more entropy sources.

How much entropy may safely be credited to \(s\) depends on the statistical model of those sources, their dependencies, the conditioning construction, and what information might be available to the adversary.

This is why serious random-number-generator design includes **entropy estimation and source validation**, rather than simply hashing some timestamps and declaring the result random.

## From a small amount of entropy to a long random stream

Once a system has obtained sufficiently unpredictable seed material, it normally does not request a new physical measurement for every key byte.

Instead it initializes a **cryptographically secure pseudorandom number generator**, or CSPRNG.

Conceptually,

\[
S_0
\leftarrow
\operatorname{Instantiate}(\text{entropy},\text{nonce},\text{personalization}),
\]

and subsequent calls evolve an internal state:

\[
(S_{i+1},R_i)
\leftarrow
G(S_i),
\]

where \(R_i\) is pseudorandom output.

The crucial word is **pseudorandom**.

Once \(S_0\) is fixed, the generator is deterministic. Running the same algorithm from exactly the same state produces exactly the same outputs.

That is not a defect.

The cryptographic requirement is that, without knowledge of the secret state, an efficient adversary should not be able to distinguish the generator's output from suitably random data or predict future outputs with useful advantage.

So we deliberately use:

\[
\boxed{
\text{small amount of high-quality uncertainty}
\rightarrow
\text{secret CSPRNG state}
\rightarrow
\text{large amount of pseudorandom output}
}
\]

rather than demanding a physical random event for every generated bit.

This also explains why ordinary pseudorandom generators are not sufficient.

A generator may have excellent statistical properties and still be cryptographically predictable.

The Mersenne Twister, for example, is extremely useful for simulation. Its output is statistically good for many scientific purposes, but the generator was not designed to resist an attacker who observes outputs and attempts to recover its internal state.

Cryptographic randomness requires an adversarial security model, not merely a good-looking histogram.

In Python, application code should therefore prefer facilities such as:

```python
import secrets

private_material = secrets.token_bytes(32)
nonce = secrets.token_bytes(12)
x = secrets.randbelow(q)
```

rather than using a simulation-oriented PRNG for secrets.

The important architectural idea is that `secrets` does not invent its own entropy model. It delegates the problem to operating-system cryptographic randomness facilities.

## The operating system is the randomness boundary for most applications

Modern operating systems maintain a kernel-level random generator.

At a high level the kernel:

1. collects environmental and hardware input,
2. maintains internal entropy/randomness state,
3. initializes a cryptographically secure generator,
4. continually evolves that state,
5. exposes random bytes to applications through controlled interfaces.

On modern Linux, `getrandom()` is the preferred direct system interface for many uses. Importantly, the normal interface waits for the kernel random source to be initialized before returning cryptographic output.

This initialization boundary matters most during unusual conditions such as very early boot, highly constrained embedded systems, freshly cloned virtual machines, or systems with poor access to environmental entropy.

The old folklore distinction

> "`/dev/random` is secure while `/dev/urandom` is insecure"

is therefore not a good model of modern Linux randomness.

For normal application development, the better rule is much simpler:

> Use the operating system's cryptographic randomness API through a reputable library, and do not build a private entropy pool inside the application.

A program should not try to create "extra entropy" by concatenating values such as

```text
current timestamp
process identifier
username
MAC address
CPU counter
```

and hashing them.

These values may add diversity, but many of them are predictable or observable. Without a defensible entropy model, counting them as secret randomness can give a completely false security estimate.

### Multiple sources and hedging

Combining several entropy sources can still be valuable.

Suppose

\[
X_1,X_2,\ldots,X_n
\]

are independent or partially independent sources and we derive

\[
S
=
H(
X_1\parallel X_2\parallel\cdots\parallel X_n
).
\]

Intuitively, we would like the system to remain safe even if several sources turn out to be weak, provided at least one contributes sufficient uncertainty unknown to the attacker.

This goal is usually called **hedging**.

But simply concatenating and hashing arbitrary sources does not automatically prove the desired property. Sources can be correlated, attacker-controlled, repeated, or observed. Robust random-generator constructions therefore care about *how* entropy is accumulated, when it is credited, and how compromise is recovered from.

This is one reason designs such as **Yarrow** and later **Fortuna** introduced explicit architectures for entropy accumulation and reseeding, and why later cryptographic work studied random generators under formal state-compromise models.

## Randomness has a state, and states can be compromised

Thinking only about initial seeding is not enough.

Suppose an attacker compromises the CSPRNG state at time \(t\).

Several different security questions now arise.

**Can the attacker recover outputs generated before the compromise?**

A well-designed generator aims to provide **backtracking resistance**: knowledge of the current state should not simply reveal earlier generator outputs.

Conceptually, if state evolution uses a one-way transformation,

\[
S_{i+1}=F(S_i),
\]

then learning \(S_{i+1}\) should not make recovering \(S_i\) easy.

**Can the attacker predict future outputs?**

Immediately after complete state compromise, usually yes: if the attacker knows the full current state, deterministic evolution can often be followed.

The system therefore needs fresh entropy.

After new unpredictable input is incorporated,

\[
S'
=
\operatorname{Reseed}(S,E),
\]

we want the attacker eventually to lose knowledge of the state again.

This property is related to **prediction resistance** and **state-compromise recovery**.

Reseeding therefore does not exist because a CSPRNG somehow "uses up" randomness.

Instead, it allows the generator to recover from compromise, imperfect initialization, long-running operation, or environmental failures.

A related systems problem appears with process and virtual-machine cloning.

Imagine a virtual machine whose CSPRNG state is

\[
S.
\]

If a snapshot is cloned into two machines, both may initially contain the same state:

\[
S_A=S_B=S.
\]

If nothing distinguishes them, they may begin producing identical streams:

\[
R_{A,1}=R_{B,1},
\quad
R_{A,2}=R_{B,2},
\quad\ldots
\]

Modern systems therefore need to consider fork detection, reseeding, hardware events, and other mechanisms that prevent long-lived duplicate generator state.

Randomness is thus not simply a function:

\[
\operatorname{randomBytes}(32).
\]

It is a **stateful security subsystem**.

## Different cryptographic values require different randomness properties

One of the easiest mistakes in cryptographic engineering is to describe every special value as "a random nonce."

The actual requirement depends on the primitive.

| Cryptographic value | Main requirement |
| --- | --- |
| Long-term private key | Secret and sampled from the required distribution |
| Ephemeral DH secret | Secret, correctly sampled, never reused where prohibited |
| ECDSA/DSA nonce | Must not repeat and must not become predictable; deterministic generation can remove dependence on fresh randomness |
| Schnorr signing nonce | Protocol-specific secure nonce derivation; reuse can reveal the signing key |
| AES-GCM nonce | Uniqueness under a fixed key is critical |
| CBC IV | Unpredictability is required in the usual security model |
| Password salt | Uniqueness is important; secrecy is not |
| Authentication challenge | Freshness, and often unpredictability |
| Blinding factor | Usually secret and correctly sampled from the required group/field |
| One-time-pad key | Truly uniform, as long as the message, secret, and used exactly once |

This distinction has practical consequences.

### Signature nonces

Consider the simplified ECDSA equation

\[
s
=
k^{-1}(H(m)+rx)
\pmod n.
\]

If the signing nonce \(k\) becomes known,

\[
x
=
r^{-1}(sk-H(m))
\pmod n,
\]

so the private key can be recovered.

If the same \(k\) is reused across two signatures,

\[
s_1
=
k^{-1}(H(m_1)+rx)
\]

and

\[
s_2
=
k^{-1}(H(m_2)+rx),
\]

then subtraction eliminates the private key term and allows recovery of the nonce:

\[
k
=
\frac{H(m_1)-H(m_2)}
{s_1-s_2}
\pmod n.
\]

Once \(k\) is recovered, \(x\) follows.

This is why signature nonce generation is not a minor implementation detail.

Standards such as RFC 6979 instead derive DSA/ECDSA nonces deterministically from the private key and message, avoiding dependence on fresh operating-system randomness for every signature while still producing the required secret nonce value.

### Nonces for authenticated encryption

For AES-GCM, the principal requirement is different.

The nonce does not need to be secret, but reuse of a nonce under the same key can catastrophically violate the construction's security assumptions.

Thus "use random bytes" is only one possible strategy for achieving the real requirement:

\[
\boxed{\text{nonce uniqueness under a fixed key}}
\]

and the system must reason about collision probability, counters, crash recovery, distributed senders, and key rotation.

This is a good example of why cryptographic specifications should state the **property required**, not merely label a field "random."

## When randomness fails, the surrounding protocol fails

Weak randomness has caused some of the most practical failures in otherwise strong cryptography.

The general patterns recur:

\[
\text{insufficient entropy}
\rightarrow
\text{small key space}
\rightarrow
\text{search becomes feasible},
\]

or

\[
\text{nonce reuse}
\rightarrow
\text{algebraic relation}
\rightarrow
\text{secret-key recovery},
\]

or

\[
\text{state cloning}
\rightarrow
\text{repeated output}
\rightarrow
\text{cross-session failures}.
\]

This is important because randomness sits underneath almost every later topic in cryptography.

When we study RSA, elliptic-curve signatures, secret sharing, zero-knowledge proofs, threshold signatures, or post-quantum cryptography, the mathematical construction nearly always assumes that certain values were generated according to some distribution.

If that assumption is violated, the theorem describing the primitive may no longer describe the implementation.

The correct engineering question is therefore not merely

> "Where do I call the random-number generator?"

but

> **"Which values require uncertainty, how much uncertainty do they require, what does the adversary know, how is the generator initialized and recovered, and what happens if randomness fails?"**

For ordinary application code, the practical rule remains simple:

- obtain cryptographic randomness from the operating system through a reputable cryptographic library;
- do not design a private PRNG;
- do not confuse output length with entropy;
- do not assume hashing creates entropy;
- distinguish uniqueness, unpredictability, secrecy, and uniform sampling;
- follow the nonce-generation requirements of the protocol being implemented;
- treat early boot, embedded systems, VM cloning, process forking, and state compromise as explicit engineering concerns.

But underneath those simple rules lies a surprisingly deep subject involving information theory, extractors, stateful cryptography, operating-system design, and adversarial models.

That is why randomness deserves to be treated as a cryptographic primitive in its own right.

---

## Papers and standards

The following are useful starting points for going deeper.

1. **Claude E. Shannon**, *A Mathematical Theory of Communication*, Bell System Technical Journal, 1948.  
   The foundational information-theoretic treatment of entropy.

2. **D. Eastlake, J. Schiller, S. Crocker**, *Randomness Requirements for Security*, RFC 4086, 2005.  
   A practical discussion of why statistically random-looking data is not necessarily suitable for security.

3. **Elaine Barker and John Kelsey**, *Recommendation for Random Number Generation Using Deterministic Random Bit Generators*, NIST SP 800-90A Rev. 1, 2015.  
   Specifies Hash_DRBG, HMAC_DRBG, and CTR_DRBG constructions.

4. **Meltem Sönmez Turan, Elaine Barker, John Kelsey, Kerry McKay, Mary Baish, Mike Boyle**, *Recommendation for the Entropy Sources Used for Random Bit Generation*, NIST SP 800-90B, 2018.  
   Particularly relevant for entropy estimation, noise sources, conditioning, and health testing.

5. **Elaine Barker, John Kelsey, Kerry McKay, Allen Roginsky, Meltem Sönmez Turan**, *Recommendation for Random Bit Generator Constructions*, NIST SP 800-90C, 2025.  
   Connects entropy sources and deterministic generators into complete random-bit-generator constructions.

6. **John Kelsey, Bruce Schneier, Niels Ferguson**, *Yarrow-160: Notes on the Design and Analysis of the Yarrow Cryptographic Pseudorandom Number Generator*, Selected Areas in Cryptography, 1999.  
   An influential design discussion of cryptographic PRNGs, entropy accumulation, reseeding, and practical failure modes.

7. **Yevgeniy Dodis, David Pointcheval, Sylvain Ruhault, Damien Vergnaud, Daniel Wichs**, *Security Analysis of Pseudo-Random Number Generators with Input: /dev/random Is Not Robust*, ACM CCS, 2013.  
   DOI: 10.1145/2508859.2516653.

8. **Yevgeniy Dodis, Adi Shamir, Noah Stephens-Davidowitz, Daniel Wichs**, *How to Eat Your Entropy and Have It Too: Optimal Recovery Strategies for Compromised RNGs*, CRYPTO 2014; later Algorithmica 79(4), 2017.  
   DOI: 10.1007/s00453-016-0239-3.

9. **Thomas Pornin**, *Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA)*, RFC 6979, 2013.  
   A concrete example of avoiding fragile per-signature dependence on fresh randomness.

---

This article closes the **Cryptography Primer**.

The purpose of the primer was not to cover cryptography in depth, but to establish a common vocabulary: representations and bit operations, computational tools, basic cryptographic thinking, and finally the randomness assumptions underneath real cryptographic systems.

From this point onward, CryptoCave branches into the more specialized series, where these foundations are used rather than reintroduced.