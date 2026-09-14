---
title: "When Schnorr Worked Only Half the Time: Debugging Our Distributed BIP340 Prototype"
description: "A forensic reconstruction of our three-party Schnorr experiment: what the code was trying to do, why it was not yet FROST, the verifier/transcript/parity bugs that caused intermittent failures, and a corrected BIP340-compatible n-of-n implementation with reproducible tests."
pubDate: "2026-09-14"
updatedDate: "2026-09-14"
heroImage: "/images/blog/schnorr-js-api-architecture.png"
topics:
  - "Threshold Cryptography"
  - "Digital Signatures"
  - "Cryptographic Engineering"
  - "Implementation Security"
tags:
  - "schnorr"
  - "bip340"
  - "distributed-signing"
  - "multisignature"
  - "frost"
  - "musig2"
  - "secp256k1"
  - "noble-curves"
  - "debugging"
  - "nonce"
  - "parity"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 18
sourcePath: "experiments/threshold-cryptography/schnorr-js-debug"
status: "Validated"
draft: false
---
This chapter documents a real failed experiment rather than presenting a protocol that was correct from the beginning.

A friend and I were trying to build a distributed Schnorr-signature prototype around `secp256k1` and the Noble JavaScript libraries. The idea looked simple:

1. every peer owns a Schnorr key;
2. add the public keys;
3. every peer generates a nonce point;
4. add the nonce points;
5. every peer computes a partial response;
6. add the responses; and
7. verify one final BIP340-style signature.

At the algebraic level, that idea looks almost embarrassingly straightforward:

$$
X=\sum_i X_i,
\qquad
R=\sum_i R_i,
\qquad
s_i=k_i+e x_i,
\qquad
s=\sum_i s_i.
$$

Then

$$
\begin{aligned}
sG
&=\sum_i(k_i+e x_i)G\\
&=\sum_i k_iG+e\sum_i x_iG\\
&=R+eX.
\end{aligned}
$$

And yet our implementation behaved as if it were haunted: some versions failed almost always, and after several fixes we observed a particularly confusing symptom in which signing seemed to work only about half the time.

That behavior was not random noise. It exposed several different mistakes sitting on top of one another:

- a verifier that interpreted the signature's $r$ coordinate as a secret scalar;
- signer and verifier hashing different transcripts;
- failure to normalize the **aggregate public key** to BIP340's even-$y$ representative;
- failure to normalize the **aggregate nonce point** to the even-$y$ representative;
- a nonce commitment that was computed but never enforced as a protocol round;
- nonce-generation semantics that were not clearly separated from preprocessing;
- no defense against rogue-key registration;
- and, most importantly, a conceptual naming problem: the experiment was an **$n$-of-$n$ aggregate Schnorr signature**, not yet a threshold-signature scheme such as FROST.

This chapter reconstructs the project line by line, explains why each bug matters mathematically, and finishes with a cleaned implementation and reproducible tests.

> **Scope.** The corrected code at the end is an educational, registered-key, $n$-of-$n$ aggregate Schnorr demonstration that produces BIP340-compatible signatures. It is deliberately **not** presented as a production multisignature protocol. For BIP340 multisignatures, use a reviewed MuSig2 implementation conforming to BIP327. For threshold Schnorr, use a reviewed FROST implementation such as an RFC 9591 construction.

## 1. The architecture we were trying to build

The project evolved through several sketches. That evolution is itself useful because it shows that the cryptographic core and the network architecture were being designed at the same time.

### 1.1 Early peer/server sketch

Our first drawing had a browser client, a server, and several peers communicating inside a peer group:

![Original peer/server sketch from our experiment. It captures the intended distributed topology, but the TypeScript signing code discussed in this chapter actually ran sequentially inside one process.](/images/blog/schnorr-js-original-network-sketch.png)

The drawing suggests a genuine distributed protocol, but the TypeScript file did not yet implement this network. There were no API calls, session identifiers, authenticated peer messages, coordinator state, or persistent nonce state in the signing code itself.

### 1.2 A parallel FROST/Python design

We were also thinking about a threshold version with three parties plus a client/server challenge component:

![Parallel FROST/Python scenario sketch. This belongs conceptually to threshold Schnorr, not to the naive aggregate Schnorr code reconstructed below.](/images/blog/schnorr-js-frost-python-sketch.png)

That architecture is much closer to the threshold-signature direction developed later in the FROST chapters. It should not be confused with the JavaScript experiment.

### 1.3 The Schnorr/JavaScript API sketch

The most relevant diagram is the two-sided API design:

![The Schnorr-JS architecture we were aiming for: peer state containing shares, commitments and signatures, with a central API/client interaction. The original TypeScript file implemented only the local cryptographic experiment, not this complete network service.](/images/blog/schnorr-js-api-architecture.png)

This is the design we eventually wanted. The recovered code, however, should be understood first as a **single-process cryptographic simulator**.

That distinction is important throughout the chapter:

```text
architecture we wanted
        !=
protocol actually implemented
        !=
security properties of FROST or MuSig2
```

## 2. What the code actually implemented

The recovered program creates three completely independent Schnorr secret keys:

```ts
const numParticipants = 3;
const participants = [];

for (let i = 0; i < numParticipants; i++) {
  participants.push(SchnorrSignatures.generateKeyPair());
}
```

If the private scalars are

$$
x_1,x_2,x_3,
$$

then each party publishes

$$
X_i=x_iG.
$$

The code then computes

$$
X=X_1+X_2+X_3.
$$

That is **key aggregation**.

It is not Shamir secret sharing. There is no polynomial $f$, no common secret $x=f(0)$, no threshold $t$, no Lagrange coefficient $\lambda_i$, and no subset of size $t$ capable of signing.

All three signers are required.

So the correct conceptual description is:

$$
\boxed{\text{3-of-3 aggregate Schnorr experiment}}
$$

not

$$
\boxed{\text{2-of-3 or }t\text{-of-}n\text{ threshold Schnorr}}.
$$

This difference will matter when we compare the experiment with FROST later.

## 3. BIP340 details that look cosmetic but are not

Most of the intermittent failures came from one fact: BIP340 uses **x-only public keys**.

For a secp256k1 point

$$
P=(x,y),
$$

the point

$$
-P=(x,p-y)
$$

has exactly the same $x$ coordinate.

Therefore a 32-byte x-only encoding does not by itself distinguish $P$ from $-P$.

BIP340 resolves the ambiguity by selecting a canonical representative: the point with **even $y$**.

We can write

$$
\operatorname{lift\_x}(x)
$$

for the operation that reconstructs the unique curve point with coordinate $x$ and even $y$.

This is why BIP340 signing sometimes negates a secret scalar. If

$$
P=dG
$$

has odd $y$, the effective scalar becomes

$$
d'=n-d.
$$

Then

$$
d'G=-P,
$$

which has the same $x$ coordinate but even $y$.

The same issue occurs for the final nonce point $R$.

These sign changes are not presentation details. They change the scalar equation used by the signer.

## 4. The original helper code understood individual parity

One thing we had actually done correctly was normalizing **individual** public keys.

The recovered helper contained logic equivalent to:

```ts
const d = normPrivateKeyToScalar(privateKey);
const X = Point.fromPrivateKey(d);

return {
  scalar: X.hasEvenY() ? d : modN(-d),
  bytes: pointToBytes(X),
};
```

If $X_i$ was odd, the returned scalar became

$$
n-x_i.
$$

That means each x-only participant public key was internally associated with its even-$y$ representative.

So far, so good.

The first subtle error appeared one level later.

## 5. Bug I — aggregate-key parity was never normalized

The key aggregation routine added the reconstructed participant points:

```ts
publicKeys
  .map((key) => lift_x(bytesToNumberBE(key)))
  .reduce((aggregate, current) => aggregate.add(current), Point.ZERO)
```

Then it immediately discarded the $y$ coordinate and returned the aggregate $x$ coordinate.

Let

$$
X=\sum_i X_i.
$$

Even when every individual $X_i$ has even $y$, there is no rule saying that the sum $X$ also has even $y$.

Approximately half of ordinary aggregate points will have odd $y$.

Suppose the true sum is an odd-$y$ point $X$. The program stores only $x(X)$.

Later, the verifier executes

$$
\operatorname{lift\_x}(x(X)),
$$

which returns

$$
-X,
$$

not $X$.

The signing shares, however, were computed from the scalars whose points sum to $X$.

So signer and verifier disagree about the group key.

### Correct global key normalization

After key aggregation, we need one additional group-wide sign decision:

$$
X^*=\begin{cases}
X,&y(X)\text{ even},\\
-X,&y(X)\text{ odd}.
\end{cases}
$$

If negation occurs, **every signing scalar contribution must be negated**:

$$
x_i^*=\begin{cases}
x_i,&y(X)\text{ even},\\
n-x_i\pmod n,&y(X)\text{ odd}.
\end{cases}
$$

Then

$$
\sum_i x_i^*G=X^*.
$$

That final equality is the invariant the original code was missing.

## 6. Bug II — aggregate-nonce parity created the “about 50%” failure

Every signer generated a nonce scalar

$$
k_i
$$

and corresponding nonce point

$$
R_i=k_iG.
$$

The code then computed

$$
R=\sum_iR_i.
$$

Again, the program immediately encoded only $x(R)$.

And again, $R$ can have either parity.

If $R$ has odd $y$, a BIP340 verifier reconstructing the x-only value sees

$$
-R.
$$

But the response was still calculated using

$$
\sum_i k_i.
$$

So the final scalar satisfies

$$
sG=R+eX
$$

while the verifier expects

$$
sG=-R+eX.
$$

The correct fix is exactly analogous to the group-key fix:

$$
R^*=\begin{cases}
R,&y(R)\text{ even},\\
-R,&y(R)\text{ odd},
\end{cases}
$$

and if $R$ is negated then each signer uses

$$
k_i^*=n-k_i.
$$

Now

$$
\sum_i k_i^*G=R^*.
$$

### Why this looks like a 50% bug

Assume the group key is fixed and already normalized correctly.

Each signing session generates a fresh aggregate nonce $R$. Its $y$ parity is essentially balanced.

Therefore, if everything else is fixed but aggregate-nonce normalization is omitted,

$$
\Pr[\text{verification succeeds}]\approx\frac12.
$$

We reproduced this symptom with a dependency-free secp256k1 reference model included with this chapter.

One run produced:

```text
corrected implementation: 40/40 verified
aggregate-nonce parity fix removed: 54/100 verified
```

That is the “haunted” behavior explained mathematically.

If both aggregate-key parity and aggregate-nonce parity are left uncontrolled while keys are regenerated every execution, the expected success probability is closer to

$$
\frac12\cdot\frac12=\frac14.
$$

So the exact observed percentage also tells us something about which bugs had already been fixed in a particular historical revision.

## 7. Bug III — the verifier treated $r=x(R)$ as though it were the nonce scalar

This was the most direct mathematical error in the recovered verifier.

The signature format is

$$
\sigma=(r,s)
$$

where

$$
r=x(R).
$$

The recovered code did this:

```ts
const r = bytesToNumberBE(sig.subarray(0, 32));
const R = Point.BASE.multiply(r);
```

That computes

$$
rG.
$$

But $r$ is **not** the discrete logarithm of $R$.

It is the x-coordinate of $R$.

In general,

$$
\boxed{x(kG)G\ne kG.}
$$

Recovering $k$ from $R=kG$ would itself be the elliptic-curve discrete logarithm problem.

### Correct BIP340 verification

The verifier does not reconstruct $R$ as $rG$.

It computes

$$
R'=sG-eP.
$$

Then it checks:

1. $R'$ is not the point at infinity;
2. $R'$ has even $y$; and
3. $x(R')=r$.

So verification is:

$$
\boxed{
R'=sG-eP,
\qquad
\operatorname{evenY}(R'),
\qquad
x(R')=r.
}
$$

The generic BIP340 helper that we had copied earlier in the project actually implemented this correctly. The later custom verifier accidentally replaced it with the invalid $rG$ reconstruction.

This is a good engineering lesson: rewriting a correct cryptographic verifier “for clarity” can silently destroy an invariant that is not obvious from the serialization format.

## 8. Bug IV — signer and verifier hashed different transcripts

The signing code computed its challenge in the BIP340 order:

```ts
challenge(R_x, X_x, message)
```

corresponding to

$$
e=H_{\text{BIP0340/challenge}}(r\|P_x\|m).
$$

But the custom verifier used a different order:

```ts
challenge(message, R, P)
```

corresponding roughly to

$$
e'=H(m\|R\|P).
$$

These are unrelated hash inputs.

A cryptographic hash is not commutative:

$$
H(A\|B\|C)\ne H(C\|A\|B).
$$

So even a perfectly correct signature equation cannot survive this mismatch.

This also tells us something about the historical “50%” observation. **The exact verifier recovered in our final snapshot should not succeed 50% of the time.** With both the $rG$ bug and the transcript-order bug present, it should fail essentially all legitimate signatures.

Therefore the 50% phase almost certainly came from an earlier intermediate revision in which the verifier had already been repaired and the remaining error was aggregate parity.

That is consistent with the bug sequence we reconstructed.

## 9. Bug V — the code computed nonce commitments but did not implement a commitment round

Nonce generation returned both $R_i$ and

```ts
commitment = SHA256(R_i)
```

which is a reasonable beginning.

But later aggregation ignored the commitment hashes and directly consumed the revealed points.

So the actual flow was:

```text
make R_i
   ↓
print H(R_i)
   ↓
ignore H(R_i)
   ↓
aggregate R_i
```

That is not commit/reveal.

A real round structure is:

```text
ROUND 1 — COMMIT
A -> C_A = H(session || A || R_A)
B -> C_B = H(session || B || R_B)
C -> C_C = H(session || C || R_C)

Only after every commitment is fixed:

ROUND 2 — REVEAL
A -> R_A
B -> R_B
C -> R_C

Coordinator checks
H(session || i || R_i) == C_i
for every signer.
```

The session identifier and signer identifier matter. Without them, a byte-for-byte valid commitment can be replayed into the wrong session or attributed ambiguously.

Our corrected demo implements this separation.

## 10. Bug VI — nonce generation was neither ordinary BIP340 nor explicit preprocessing

The original single-party BIP340 helper derived a nonce from data including

$$
\text{secret-derived material}\|P_x\|m.
$$

The distributed experiment changed this to something closer to

```ts
H_BIP340/nonce(t_i)
```

without the message or aggregate key.

That is not necessarily incorrect if the goal is **preprocessed random nonces**. FROST and MuSig-style protocols do not require a nonce to be deterministically derived from the message.

But the semantics must be explicit:

- the nonce is generated independently before signing;
- it is stored as secret one-time state;
- it is bound to exactly one signing session; and
- it is destroyed after use.

If a signer reuses one $k_i$ for two challenges,

$$
s_{i,1}=k_i+e_1x_i
$$

and

$$
s_{i,2}=k_i+e_2x_i,
$$

then

$$
s_{i,1}-s_{i,2}=(e_1-e_2)x_i
$$

and therefore

$$
\boxed{
x_i=(s_{i,1}-s_{i,2})(e_1-e_2)^{-1}\pmod n.
}
$$

A reused nonce destroys that participant's secret.

The corrected code therefore stores a `used` flag and refuses a second partial signature from the same nonce object.

Production implementations should make secret nonce reuse structurally difficult rather than relying on developer discipline.

## 11. Bug VII — this was vulnerable to rogue-key registration

The aggregate public key was simply

$$
X=\sum_i X_i.
$$

If arbitrary unauthenticated public keys are accepted, an attacker can choose a key algebraically related to honest participants and manipulate the aggregate key.

This is the classic reason why a real BIP340 multisignature protocol is more complicated than “sum the keys and sign.”

MuSig2, standardized in BIP327, uses key-aggregation coefficients and a carefully specified nonce/signing flow rather than plain addition.

For our educational reconstruction, we choose a narrower model:

- every signer registers its key first;
- registration includes a normal BIP340 proof of possession;
- only registered keys participate in the experiment.

This blocks the simple “submit a point whose discrete logarithm you do not know” rogue-key strategy in the demo.

It still does **not** turn our construction into MuSig2, and we make no claim of a MuSig2-equivalent security proof.

## 12. Why this still is not threshold Schnorr

After all those corrections, the construction is still $n$-of-$n$.

We have independent secrets:

$$
x_1,x_2,x_3
$$

and group key

$$
X=X_1+X_2+X_3.
$$

If Peer B disappears, Peers A and C cannot produce a valid signature for the same group key.

FROST instead begins from shares of one common secret:

$$
x_i=f(i),
\qquad
x=f(0).
$$

A selected signer set $S$ of size at least $t$ reconstructs the secret **in the exponent** using Lagrange weights:

$$
x=\sum_{i\in S}\lambda_i x_i.
$$

A FROST response includes terms such as

$$
\lambda_i x_i c,
$$

and the signing protocol additionally uses two nonces plus signer-specific binding factors.

RFC 9591 specifies this two-round threshold structure and explicitly treats nonce reuse as a security-critical failure condition.

So our repaired JavaScript experiment belongs in the curriculum **before FROST**:

```text
ordinary Schnorr
      ↓
naive n-of-n aggregation
      ↓
BIP340 parity / transcript / nonce lessons
      ↓
why multisignature protocols need more structure
      ↓
why threshold Schnorr needs Shamir + Lagrange
      ↓
FROST
```

## 13. The corrected protocol state machine

The repaired educational implementation uses four conceptual stages.

### Stage A — key registration

Each signer creates a BIP340 keypair and registers:

- signer identifier;
- x-only public key; and
- proof-of-possession signature.

Each individual key is represented by its BIP340 even-$y$ scalar representative.

The coordinator computes

$$
Q=\sum_iP_i.
$$

If $Q$ is odd,

$$
Q\leftarrow -Q
$$

and records

```text
keyNegated = true
```

so that every signer later negates its effective secret contribution.

### Stage B — nonce commitment

For one session identifier `sid`, signer $i$ samples fresh

$$
k_i\in\mathbb Z_n^*
$$

and computes

$$
R_i=k_iG.
$$

Internally the protocol transports the **full compressed point**, not an x-only point. This preserves its parity during aggregation.

The signer sends only

$$
C_i=H(\text{domain}\|\text{sid}\|i\|Q_x\|H(m)\|\operatorname{enc}(R_i)).
$$

### Stage C — nonce reveal and group normalization

After all commitments are frozen, every signer reveals $R_i$.

The coordinator checks every commitment and computes

$$
R=\sum_iR_i.
$$

If $R$ has odd $y$,

$$
R\leftarrow -R
$$

and every signer uses

$$
k_i^*=n-k_i.
$$

Otherwise

$$
k_i^*=k_i.
$$

The aggregate-key sign is handled identically:

$$
x_i^*=\begin{cases}
x_i,&Q\text{ even},\\
n-x_i,&Q\text{ odd}.
\end{cases}
$$

### Stage D — partial signing and aggregation

Every signer derives exactly the same BIP340 challenge

$$
e=H_{\text{BIP0340/challenge}}
\left(x(R)\|x(Q)\|m\right)\bmod n.
$$

Then

$$
s_i=k_i^*+e x_i^*\pmod n.
$$

The coordinator sums

$$
s=\sum_i s_i\pmod n
$$

and emits

$$
\sigma=x(R)\|s.
$$

Correctness is immediate:

$$
\begin{aligned}
sG
&=\sum_i(k_i^*+ex_i^*)G\\
&=\sum_i k_i^*G+e\sum_i x_i^*G\\
&=R+eQ.
\end{aligned}
$$

Because both $R$ and $Q$ are their even-$y$ representatives, the output is compatible with an ordinary BIP340 verifier.

## 14. Correct verifier

The corrected implementation does not invent another verifier. It ultimately asks Noble's BIP340 implementation to verify the final 64-byte signature.

Conceptually, the equivalent verifier is:

```ts
const P = lift_x(publicKeyX);
const r = int(signature.slice(0, 32));
const s = int(signature.slice(32, 64));
const e = challenge(rBytes, publicKeyX, message);

const R = s * G - e * P;

return (
  R !== infinity &&
  hasEvenY(R) &&
  x(R) === r
);
```

The two most important differences from the broken verifier are:

```diff
- R = r * G
+ R = s * G - e * P
```

and

```diff
- challenge(message, R, P)
+ challenge(rBytes, publicKeyX, message)
```

## 15. Migrating from old Noble internals to the current API

The original project was written against a Noble v1-era API. Names such as these appear in the recovered source:

```text
ProjectivePoint
randomPrivateKey
normPrivateKeyToScalar
toRawBytes
hasEvenY
multiplyAndAddUnsafe
```

Current `@noble/curves` v2 uses a cleaner API and is ESM-only. The project documentation lists changes such as:

```text
ProjectivePoint       -> Point
randomPrivateKey      -> randomSecretKey
normPrivateKeyToScalar -> Point.Fn.fromBytes / explicit scalar conversion
toRawBytes            -> toBytes
```

and some convenience methods such as `hasEvenY` and `multiplyAndAddUnsafe` were removed.

The cleaned example therefore avoids depending on those old internals. It uses:

```ts
import { secp256k1, schnorr } from '@noble/curves/secp256k1.js';
import {
  bytesToNumberBE,
  concatBytes,
  equalBytes,
  numberToBytesBE,
} from '@noble/curves/utils.js';
import { sha256 } from '@noble/hashes/sha2.js';
```

and ordinary point methods:

```ts
Point.BASE.multiply(k)
P.add(Q)
P.negate()
P.toBytes(true)
P.x
P.y
```

The companion project pins:

```json
{
  "@noble/curves": "2.4.0",
  "@noble/hashes": "2.4.0"
}
```

so that future API changes do not silently mutate the experiment again.

## 16. The cleaned Noble implementation

The complete file is available at:

```text
experiments/threshold-cryptography/schnorr-js-debug/fixed-noble-v2.mjs
```

The core signing loop is intentionally small:

```ts
let d = signer.d;
let k = nonce.k;

if (keyAgg.keyNegated)
  d = N - d;

if (nonceNegated)
  k = N - k;

const s_i = modN(k + e * d);
```

and aggregation is simply:

```ts
const s = partials.reduce(
  (acc, partial) => modN(acc + partial.s_i),
  0n,
);

const signature = concatBytes(
  rX,
  numberToBytesBE(s, 32),
);
```

The cryptographic complexity is not in that final addition. It is in making sure that every signer has derived the **same authenticated session state** before executing it.

## 17. Reproducing the parity bug independently of Noble

To make the result reproducible even if the JavaScript library changes again, this chapter also ships a dependency-free model:

```text
experiments/threshold-cryptography/schnorr-js-debug/reference-model.mjs
```

It implements only the secp256k1 arithmetic and BIP340 equations needed for this experiment using Node's built-in SHA-256 and randomness.

Run:

```bash
node reference-model.mjs
```

A validation run during this cleanup produced:

```text
corrected implementation: 40/40 verified
aggregate-nonce parity fix removed: 54/100 verified (deterministic sample; expected rate ≈50%)
```

This is stronger evidence than saying “parity looks suspicious.” It recreates the actual statistical symptom from the underlying equations.

## 18. Running the fixed current-Noble version

The experiment is self-contained inside its own subdirectory, so Noble does not become a dependency of the Astro website itself.

```bash
cd experiments/threshold-cryptography/schnorr-js-debug
npm install
npm run demo
npm test
```

The expected invariant is:

```text
fixed: 100/100
```

The test suite then intentionally disables only aggregate-nonce parity correction. With a fixed aggregate public key, the success rate should fluctuate around one half.

That second result is not a flaky test of the final implementation. It is a controlled regression experiment that recreates the old bug.

## 19. What we deliberately did not “fix” into this example

There is a dangerous temptation during debugging to keep adding patches until a toy protocol starts resembling a production protocol. We stop before that point.

The cleaned demo does **not** claim:

- $t$-of-$n$ signing;
- Shamir-shared secret keys;
- DKG;
- FROST security;
- MuSig2 security;
- malicious-participant robustness;
- identifiable abort;
- protection against every concurrent-session attack;
- production side-channel resistance; or
- production network authentication.

It is a controlled bridge between ordinary Schnorr algebra and the real distributed protocols that follow in this series.

### If the goal is multisignature

Use a reviewed MuSig2 implementation following BIP327.

MuSig2 adds, among other machinery:

- explicit key aggregation coefficients;
- two nonce components per signer;
- session-bound nonce aggregation;
- aggregate-key parity handling;
- aggregate-nonce parity handling;
- partial-signature verification; and
- carefully specified serialization/transcript rules.

The fact that BIP327 has explicit algorithms for secret-key negation and nonce negation is a useful confirmation that the parity issue we encountered is a real protocol concern, not an artifact of our code style.

### If the goal is threshold signatures

Use FROST.

FROST changes the key model entirely. Participants hold shares of one common signing secret, and a threshold subset signs using Lagrange interpolation and binding factors.

That is the subject of the next threshold-Schnorr chapters.

## 20. A compact bug table

| Problem | Original behavior | Consequence | Correction |
|---|---|---|---|
| Signature $r$ treated as scalar | `R = r * G` | Verifier reconstructs the wrong point | Compute $R=sG-eP$ |
| Challenge ordering mismatch | signer hashes `R || P || m`, verifier hashes `m || R || P` | Different $e$ values | Use exact BIP340 transcript |
| Aggregate key parity ignored | x-only encode $\sum X_i$ directly | verifier may see $-X$ | global key sign + negate all secret contributions |
| Aggregate nonce parity ignored | x-only encode $\sum R_i$ directly | roughly 50% failure for fixed group key | global nonce sign + negate every $k_i$ |
| Hash commitment unused | commitment only logged | no actual commit/reveal round | freeze commitments, then reveal and check |
| Preprocessed nonce not marked one-use | nonce semantics implicit | reuse can reveal secret share | session state + consume-once nonce |
| Raw key summation | no registration protection | rogue-key risk | PoP in demo; MuSig2 in production |
| Every signer required | all partials summed | not threshold | FROST + Shamir/Lagrange for $t$-of-$n$ |
| Old Noble internals | v1 API names | current install can fail before crypto runs | pin current v2 API |
| `aggregateCommitments` naming | function aggregates points, not hashes | hides protocol gap | separate commitment/reveal/point aggregation |

## 21. What we learned

The most interesting lesson from this experiment is not “remember to check even $y$.”

It is that the apparently simple Schnorr identity

$$
sG=R+eX
$$

is only the final line of a distributed signing protocol.

Before that line is safe to evaluate, every participant must agree on:

- which keys are participating;
- which representation of the aggregate key is canonical;
- which session is being signed;
- which nonce commitments belong to that session;
- which nonce points were revealed;
- which canonical aggregate nonce is used;
- which exact byte transcript is hashed;
- whether any one-time nonce has already been consumed; and
- how malformed or malicious participant messages are handled.

The equation is easy.

The protocol state around the equation is the hard part.

Our “50% bug” was a particularly useful demonstration of that difference because the mathematical error was tiny—a missing global sign—but its behavior looked probabilistic and network-related.

Once that distinction is clear, the motivation for MuSig2 and FROST becomes much easier to understand.

## 22. Reproducibility files

This chapter preserves the original and corrected work side by side:

```text
experiments/threshold-cryptography/schnorr-js-debug/
├── original-snapshot.ts
├── fixed-noble-v2.mjs
├── test-noble.mjs
├── reference-model.mjs
├── package.json
└── README.md
```

The original snapshot is intentionally kept as evidence. It is not imported by the corrected code.

The reference model requires no external package and is part of CryptoCave's local validation. The Noble implementation targets the currently documented v2 API and is isolated from the website dependencies.

## References

- Bitcoin Improvement Proposal 340, **Schnorr Signatures for secp256k1**: <https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki>
- BIP340 test vectors and reference logic: <https://github.com/bitcoin/bips/blob/master/bip-0340/test-vectors.py>
- Bitcoin Improvement Proposal 327, **MuSig2 for BIP340-compatible Multi-Signatures**: <https://bips.dev/327/>
- RFC 9591, **The Flexible Round-Optimized Schnorr Threshold (FROST) Protocol**: <https://www.rfc-editor.org/rfc/rfc9591.html>
- Noble Curves documentation: <https://www.npmjs.com/package/@noble/curves>
