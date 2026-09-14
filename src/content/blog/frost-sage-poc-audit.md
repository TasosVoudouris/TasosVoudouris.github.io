---
title: "FROST in SageMath: A Working secp256k1 Proof of Concept, Line by Line"
description: "A complete audit of a collaborator's working SageMath FROST prototype: distributed key generation, Feldman VSS, nonce preprocessing, binding factors, Lagrange interpolation, signature-share verification, aggregation, RFC 9591 differences, and a hardened educational rewrite."
pubDate: "2026-09-14"
updatedDate: "2026-09-14"
heroImage: "/images/blog/frost-sage-poc-flow.svg"
topics:
  - "Threshold Cryptography"
  - "Cryptographic Engineering"
  - "Secret Sharing"
  - "Digital Signatures"
tags:
  - "frost"
  - "threshold-schnorr"
  - "sage"
  - "sagemath"
  - "secp256k1"
  - "vss"
  - "dkg"
  - "lagrange-interpolation"
  - "nonce-preprocessing"
  - "rfc-9591"
  - "code-audit"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 22
sourcePath: "experiments/threshold-cryptography/frost-sage-poc"
status: "Reviewed"
draft: false
---

This article is a different kind of code review from the broken distributed
Schnorr case study that precedes it in this series.

There, the code failed intermittently and the job was to discover why.
Here, a collaborator supplied a compact SageMath implementation of FROST that
**did run consistently**. The interesting question is therefore not simply
"where is the bug?" It is:

> **What exactly is this program doing, why does the mathematics work, which
> parts are genuinely FROST, which parts are an educational simplification,
> and which details would have to change before we could call it an RFC 9591
> implementation?**

The answer is encouraging. The core signing algebra is correct. The program
captures the central FROST construction very clearly:

- Shamir/Feldman-style distributed key material;
- public verification shares;
- two one-time nonces per signer;
- binding factors;
- a group commitment;
- Lagrange interpolation over the selected signing subset;
- per-signer Schnorr responses;
- public verification of every signature share; and
- aggregation into a single Schnorr-style signature.

At the same time, the audit found several important engineering and
standards-conformance gaps. None of them explains a mysterious 50% failure like
our previous Schnorr experiment, because the honest-path algebra here is
coherent. They matter when we move from **"working proof of concept"** to
**"robust threshold-signature implementation."**

![The complete flow of the collaborator's SageMath proof of concept.](/images/blog/frost-sage-poc-flow.svg)

---

## 1. What the uploaded program contains

The file combines three logically distinct protocols in one compact script:

1. **multi-dealer distributed key generation**;
2. **offline nonce preprocessing**; and
3. **FROST signing and aggregation**.

That distinction is important because RFC 9591 standardizes the FROST signing
protocol and its ciphersuites, but it does not standardize this exact
multi-dealer DKG front-end. The uploaded program therefore contains **more than
FROST signing itself**.

At the bottom of the file the concrete group is secp256k1:

```python
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
Kp = GF(p)
E = EllipticCurve(Kp, (0, 7))

G = E(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)

q = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
E.set_order(q)
Kq = GF(q)
```

So we have two different finite fields in play:

- \(\mathbb F_p\) for **curve coordinates**; and
- \(\mathbb F_q\) for **secret scalars**.

That distinction should always remain explicit. In elliptic-curve signature
code, confusing the coordinate field and scalar field is one of the easiest
ways to create subtle mistakes.

The demonstration uses:

```python
t = 4
n = 5
π = len(messages)
a = n
```

Conceptually:

- \(t=4\) is the threshold;
- \(n=5\) is the total number of parties;
- \(\pi\) is the number of nonce pairs to preprocess; and
- `a` is the number of parties selected for signing.

Notice immediately that the demo sets:

\[
a=n=5.
\]

So although the key sharing has threshold \(4\), the actual demonstration
always signs with **all five participants**. We will return to this because it
is one of the most useful improvements we can make.

---

# Part I — Distributed key generation

## 2. Every participant becomes a dealer

Each `Participant` samples a polynomial:

```python
self.poly = [Kq.random_element() for _ in range(t)]
```

For threshold \(t\), this creates \(t\) coefficients:

\[
f_i(X)
=
 a_{i,0}
 + a_{i,1}X
 + \cdots
 + a_{i,t-1}X^{t-1}.
\]

The degree is at most \(t-1\).

Each participant's local constant term

\[
a_{i,0}=f_i(0)
\]

is that dealer's contribution to the eventual group secret.

This is the first major conceptual point:

> **There is no single dealer who chooses the final secret key.**

Instead, every party contributes secret entropy, and the effective group secret
is the sum of all dealer contributions:

\[
x
=
\sum_{j=1}^{n} a_{j,0}
\pmod q.
\]

No honest participant needs to reconstruct this \(x\).

---

## 3. Shares

The helper

```python
def generate_share(self, x):
    return (x, self._f(x))
```

computes a Shamir point:

\[
(x, f_i(x)).
\]

Dealer \(i\) sends Party \(j\):

\[
f_i(j).
\]

Once all dealers have distributed their values, Party \(j\) holds:

\[
f_1(j), f_2(j), \ldots, f_n(j).
\]

Its final private signing share becomes:

\[
s_j
=
\sum_{i=1}^{n} f_i(j)
\pmod q.
\]

This is exactly the right distributed-key intuition.

Define the aggregate polynomial:

\[
F(X)
=
\sum_{i=1}^{n}f_i(X).
\]

Then:

\[
s_j=F(j)
\]

and the hidden group secret is:

\[
x=F(0).
\]

Because every \(f_i\) has degree at most \(t-1\), so does \(F\). Therefore any
set of at least \(t\) valid points \((j,s_j)\) can interpolate \(F(0)\).

The important thing is that FROST uses that interpolation **inside the signature
calculation**, rather than reconstructing \(x\) in one place.

---

## 4. Feldman coefficient commitments

The code publishes:

```python
self.C = [G * int(coeff) for coeff in self.poly]
```

so for dealer \(i\):

\[
C_{i,k}=a_{i,k}G.
\]

These are Feldman-style polynomial commitments.

If Party \(j\) receives share

\[
s_{i\to j}=f_i(j),
\]

it can verify:

\[
s_{i\to j}G
\stackrel{?}{=}
\sum_{k=0}^{t-1}j^k C_{i,k}.
\]

Why?

\[
\begin{aligned}
\sum_{k=0}^{t-1}j^k C_{i,k}
&=
\sum_{k=0}^{t-1}j^k(a_{i,k}G)\\
&=
\left(\sum_{k=0}^{t-1}a_{i,k}j^k\right)G\\
&=
f_i(j)G.
\end{aligned}
\]

The uploaded implementation contains exactly this equation:

```python
verified = (
    G * self.shares[l][1]
    == sum(
        party.C[k] * (self.id**k)
        for k in range(t)
    )
)
```

That is mathematically correct.

---

## 5. Proof of knowledge of the constant coefficient

The script also gives each dealer a Schnorr-style proof that it knows the
discrete logarithm of its first coefficient commitment.

Dealer \(i\) has:

\[
C_{i,0}=a_{i,0}G.
\]

It samples \(k\), publishes:

\[
R_i=kG,
\]

computes challenge:

\[
c_i=H(i\parallel \Phi\parallel C_{i,0}\parallel R_i),
\]

and response:

\[
\mu_i=k+a_{i,0}c_i.
\]

Verification checks:

\[
R_i
\stackrel{?}{=}
\mu_iG-c_iC_{i,0}.
\]

Indeed:

\[
\begin{aligned}
\mu_iG-c_iC_{i,0}
&=(k+a_{i,0}c_i)G-c_i(a_{i,0}G)\\
&=kG\\
&=R_i.
\end{aligned}
\]

Again, the core algebra is correct.

### Why have this proof?

It demonstrates that a participant publishing \(C_{i,0}\) actually knows its
underlying scalar contribution. That is useful in distributed key-generation
designs to prevent a participant from injecting an arbitrary public point
without knowing the corresponding secret contribution.

However, the exact challenge construction in this Sage script is a local
educational choice. It is not the encoding/transcript definition of RFC 9591.

---

## 6. Deriving the group key

The code computes:

```python
self.groupY += party.C[0]
```

so:

\[
Y
=
\sum_i C_{i,0}
=
\sum_i a_{i,0}G
=
\left(\sum_i a_{i,0}\right)G
=xG.
\]

This is exactly what we want.

Each participant also computes its public verification share:

```python
self.Y = G * self.si
```

or:

\[
Y_i=s_iG.
\]

Those \(Y_i\) values become essential later when the coordinator verifies each
FROST signature share without learning \(s_i\).

---

# Part II — Offline preprocessing

## 7. Why FROST uses two nonce scalars

The collaborator's implementation generates, for every future signature:

```python
dj, ej = [sample() for _ in range(2)]
Dj, Ej = G*dj, G*ej
```

So signer \(i\) gets two secret scalars:

\[
d_i,e_i\in\mathbb Z_q
\]

and public commitments:

\[
D_i=d_iG,
\qquad
E_i=e_iG.
\]

The code stores both:

```python
self.L.append((Dj, Ej))
self.nonce_commitment_pairs.append(
    [(dj, Dj), (ej, Ej)]
)
```

The public pair \((D_i,E_i)\) can be announced in round one.
The scalars \((d_i,e_i)\) remain private.

### Why two?

A simple distributed Schnorr protocol might seem to require only one nonce per
participant. FROST introduces a second nonce so that each participant's final
nonce contribution can be **bound to the entire signing transcript**.

The effective nonce contribution is:

\[
R_i=D_i+\rho_iE_i,
\]

where \(\rho_i\) depends on the message and the complete commitment list.

This prevents a malicious coordinator or participant from freely rearranging
nonce commitments across sessions without changing the effective nonce.

---

## 8. One-time use is handled correctly

The code comments say:

```python
# one nonce pair per signature
# once a pair is used for a signature, discard it
```

and `compute_z()` executes:

```python
(di, _), (ei, _) = self.nonce_commitment_pairs.pop(0)
```

This is one of the most security-critical details in Schnorr-style signature
schemes.

If the same private nonce contribution were reused with two different
challenges, the corresponding signing share could leak the participant's secret
share.

So the **consume-once** model is conceptually correct.

The engineering caveat is that the private nonces and public commitment list are
held in two separate Python lists and consumed in two different functions. A
production system should represent a signing nonce as one session-bound state
object with an explicit lifecycle such as:

```text
FRESH → COMMITTED → SIGNED → DESTROYED
```

rather than relying on two matching list positions.

---

# Part III — Signing

## 9. Selecting the signing subset

The original script chooses:

```python
self.signers = self.parties[:self.a]
```

and with:

```python
a = n
```

that means all five parties.

For a real \(t=4,n=5\) demonstration, we should explicitly sign with different
four-party subsets such as:

```text
{1,2,3,4}
{1,2,4,5}
{1,3,4,5}
{2,3,4,5}
```

This is not merely cosmetic. It demonstrates the exact threshold property we
claim:

- any \(4\) valid shares should work;
- \(3\) shares should not.

The audited companion model now tests exactly that.

---

## 10. Commitment list

The selected signers publish:

\[
B=
[(i,D_i,E_i)]_{i\in S}.
\]

The code constructs:

```python
B = [
    (signer.id, signer.L[0][0], signer.L[0][1])
    for signer in self.signers
]
```

and serializes this list into `Bencoded`.

That serialization is then hashed when computing the binding factors.

The idea is correct:

> every signer should derive its binding factor from the same canonical view of
> the complete round-one commitment list.

But the exact encoding used by the prototype deserves improvement; we discuss
that in the audit section.

---

## 11. Binding factors

For signer \(i\), the program computes a value we will denote:

\[
\rho_i.
\]

In the source:

```python
self.binding_values = [
    H1(str(B[l][0]).encode(), m, Bencoded)
    for l in range(len(B))
]
```

The group commitment is then:

\[
R
=
\sum_{i\in S}
\left(D_i+\rho_iE_i\right).
\]

This is recognizably the FROST group-commitment construction.

The important distinction is that the **prototype's hash transcript is not the
RFC 9591 transcript**.

RFC 9591 derives binding factors from data equivalent to:

\[
\operatorname{enc}(Y)
\parallel H_4(m)
\parallel H_5(B)
\parallel \operatorname{enc}(i).
\]

The Sage program instead hashes:

\[
i\parallel m\parallel B.
\]

That is sufficient for the internal algebra to be self-consistent, but it is a
standards-conformance difference and loses some transcript/domain separation.

---

## 12. Challenge

Once the group commitment is known, the code computes:

```python
self.challenge = H2(
    encode_point(R),
    encode_point(groupY),
    m
)
```

Conceptually:

\[
c=H_2(\operatorname{enc}(R)\parallel\operatorname{enc}(Y)\parallel m).
\]

This is the right **structural** Schnorr challenge.

The ciphersuite-level implementation of \(H_2\) is where the prototype differs
from RFC 9591.

---

## 13. Lagrange coefficient

The code computes:

```python
λ *= Kq(signer.id) / Kq(signer.id - self.id)
```

For signer \(i\):

\[
\lambda_i
=
\prod_{j\in S, j\neq i}
\frac{j}{j-i}.
\]

This is exactly the interpolation coefficient for evaluating the Shamir
polynomial at zero.

Therefore:

\[
\boxed{
\sum_{i\in S}\lambda_i s_i=x
}
\]

for every valid signing set \(S\) with at least \(t\) members.

This is the heart of threshold Schnorr.

No signer reconstructs \(x\), but the signature equation behaves **as if** the
group secret \(x\) had been used.

---

## 14. Signature share

The most important line in the entire file is:

```python
self.z = (
    di
    + (ei * self.binding_values[i])
    + self.λ * self.si * self.challenge
)
```

Mathematically:

\[
\boxed{
z_i=d_i+\rho_i e_i+\lambda_i s_i c.}
\]

This is the FROST signature-share equation.

Define:

\[
R_i=D_i+\rho_iE_i.
\]

Because:

\[
D_i=d_iG,
\qquad
E_i=e_iG,
\qquad
Y_i=s_iG,
\]

we obtain:

\[
\begin{aligned}
z_iG
&=
(d_i+\rho_i e_i+\lambda_i s_i c)G\\
&=d_iG+\rho_i e_iG+\lambda_i c(s_iG)\\
&=D_i+\rho_iE_i+\lambda_i cY_i\\
&=R_i+\lambda_i cY_i.
\end{aligned}
\]

That is exactly what the coordinator verifies:

```python
assert G * signer.z == (
    Ri[i]
    + signer.Y * (challenge * signer.λ)
)
```

**This part is correct.**

![The equation behind FROST signature-share verification and aggregation.](/images/blog/frost-sage-poc-equation.svg)

---

## 15. Aggregation

The coordinator computes:

\[
z=
\sum_{i\in S} z_i.
\]

Expand it:

\[
\begin{aligned}
z
&=
\sum_i
\left(d_i+\rho_i e_i+\lambda_i s_i c\right)\\
&=
\sum_i(d_i+\rho_i e_i)
+c\sum_i\lambda_i s_i.
\end{aligned}
\]

But:

\[
R
=
\sum_i(D_i+\rho_iE_i)
=
\left(\sum_i(d_i+\rho_i e_i)\right)G
\]

and:

\[
\sum_i\lambda_i s_i=x.
\]

Therefore:

\[
\boxed{
zG=R+cY.}
\]

This is an ordinary Schnorr verification equation under the group public key:

\[
Y=xG.
\]

This is why FROST's final output can be verified as a single signature rather
than as a bundle of participant signatures.

---

# Part IV — Audit: what is right, what is simplified, and what should change

## 16. Executive audit table

| Area | Verdict | Why |
|---|---|---|
| Shamir threshold structure | **Correct core** | Aggregate polynomial and Lagrange interpolation are sound. |
| Feldman share verification | **Correct core** | Checks \(f_i(j)G=\sum_kj^kC_{i,k}\). |
| DKG PoK algebra | **Correct core** | Schnorr-style proof relation is valid. |
| Group public key | **Correct core** | \(Y=\sum_iC_{i,0}\). |
| Verification shares | **Correct core** | \(Y_i=s_iG\). |
| Two-nonce preprocessing | **Correct core** | Matches FROST's hiding/binding nonce structure. |
| Lagrange coefficient | **Correct** | Correct interpolation at zero. |
| Signature-share equation | **Correct** | Core FROST equation is implemented. |
| Signature-share verification | **Correct** | Public verification relation is implemented. |
| Aggregation | **Correct algebra** | \(z=\sum_i z_i\) is right. |
| Final aggregate verification | **Missing** | Original returns \((R,z)\) without checking \(zG=R+cY\). |
| Hash-to-scalar | **Needs correction** | Digest integers are not explicitly reduced to \(\mathbb Z_q\). |
| Binding transcript | **Non-RFC** | Does not use RFC 9591's group-key/H4/H5 structure. |
| DKG failure policy | **Real engineering bug** | Invalid proofs/shares print errors but protocol continues. |
| Threshold demo | **Incomplete demonstration** | \(t=4,n=5\), but demo signs 5-of-5. |
| Configuration isolation | **Real engineering bug** | Class instance parameters coexist with hidden globals. |
| Random scalar generation | **Educational only** | `randrange` / Sage RNG is not the RFC nonce-generation construction. |
| Commitment encoding | **Needs hardening** | Decimal identifiers are not canonical scalar encodings. |
| Session state | **Prototype-level** | Mutable signer fields are not isolated per concurrent signing session. |
| `assert` for validation | **Needs correction** | Security checks should explicitly abort/raise, not rely on assertions. |
| RFC 9591 wire compatibility | **No** | Correct conceptual FROST, different ciphersuite/encoding details. |

The correct summary is therefore:

> **The collaborator's implementation has a mathematically sound honest-path
> FROST core, but it is an educational FROST-like SageMath prototype rather
> than an RFC 9591-conformant production implementation.**

That is a much stronger result than "it runs, therefore it must be correct,"
and also more accurate than calling the entire program wrong because a few
standardization details differ.

---

# Part V — Specific issues found in the source

## 17. Issue 1: hash outputs are not converted into canonical scalars

The program defines:

```python
def H1(*args):
    return hash256(*args)
```

and:

```python
def H2(*args):
    H = SHA512.new()
    ...
    return b2l(H.digest()[:32])
```

Those functions return ordinary Python integers in approximately a 256-bit
range.

FROST requires the relevant transcript hashes to produce elements of the scalar
field:

\[
\mathbb Z_q.
\]

The program's elliptic-curve multiplications effectively reduce large integers
modulo the group order, which is one reason the equations still work.

But the scalar state itself is not canonical.

For example:

```python
self.z = di + rho_i * ei + lambda_i * si * c
```

is not explicitly reduced mod \(q\), and neither is:

```python
z = sum(signer.z for signer in self.signers)
```

A standard implementation should instead maintain:

\[
z_i
=
(d_i+\rho_i e_i+\lambda_i s_i c)mod q
\]

and:

\[
z=\left(\sum_i z_i\right)\bmod q.
\]

### Why did the original still work?

Because group multiplication satisfies:

\[
(a+kq)G=aG.
\]

So the verification equations can pass even with an oversized integer.

But serialization and standards conformance require a canonical scalar.

**Verdict:** honest-path algebra survives; representation is noncanonical.

---

## 18. Issue 2: the binding-factor transcript is not RFC 9591

Original code:

```python
rho_i = H1(str(id).encode(), m, Bencoded)
```

The standardized FROST construction binds \(\rho_i\) to more structured data,
including the group public key and fixed-length hashes of the message and
commitment list.

Why is that better?

Because \(\rho_i\) should be unambiguously tied to:

- this exact FROST group;
- this exact message;
- this exact commitment list; and
- this exact participant identifier.

The original program still gives every honest party the same \(\rho_i\), so the
signature equation works. It is simply not the RFC transcript.

**Verdict:** not an algebra bug; a conformance/security-domain-separation gap.

---

## 19. Issue 3: no final signature verification

This is the most important missing correctness check.

The program verifies every individual share:

```python
G * signer.z == Ri[i] + signer.Y * (challenge * signer.λ)
```

but after computing:

```python
z = sum(signer.z for signer in self.signers)
```

it immediately returns:

```python
return (R, z)
```

without checking:

\[
\boxed{zG\stackrel{?}{=}R+cY.}
\]

### Why does this matter if all shares passed?

Mathematically, valid shares should aggregate to a valid signature.

But software can fail between those two facts:

- wrong signer subset;
- stale \(\lambda_i\);
- different challenge view;
- aggregation bug;
- corrupted state;
- accidental mix of sessions;
- malformed scalar; or
- implementation regression.

The coordinator should not publish the result before final verification.

The audited version adds exactly this check.

**Verdict:** real missing verification boundary.

---

## 20. Issue 4: verification failures only print and continue

During DKG:

```python
if not verified:
    print("[-] ... could not verify ...")
```

The protocol then continues.

That is acceptable for a classroom printout but not for protocol logic.

If a dealer's proof of knowledge fails, or a Feldman share fails, the local
state is no longer trustworthy.

At minimum the implementation must:

```text
fail verification
      ↓
abort this DKG session
```

A more sophisticated DKG may enter a complaint/qualification phase, but **doing
nothing is not a valid policy**.

The audited implementation raises immediately.

**Verdict:** real protocol-engineering bug outside the all-honest execution.

---

## 21. Issue 5: constructor parameters are partly ignored

The class says:

```python
class FROST:
    def __init__(self, t, n, a):
        self.t = t
        self.n = n
        self.a = a
```

which strongly suggests we can instantiate arbitrary parameters.

But several functions use module globals directly:

```python
range(1, n+1)
range(t)
modulo q
assert len(B) == a
```

rather than:

```python
self.n
self.t
self.a
```

or explicit configuration passed to each participant.

With the one configuration at the bottom of the file, nothing goes wrong.

But this can silently break:

```python
frost2 = FROST(3, 7, 3)
```

because internal methods may still use the original global `t`, `n`, or `a`.

This is a **real code bug**, even though it is invisible in the provided run.

The audited rewrite removes those hidden dependencies.

---

## 22. Issue 6: the program never demonstrates 4-of-5

The configuration advertises:

\[
t=4,
\qquad
n=5.
\]

But:

```python
a = n
```

and:

```python
self.signers = self.parties[:self.a]
```

select all five participants.

So every successful signature demonstrates:

\[
5\text{-of-}5
\]

participation on a key that happens to have threshold 4.

That does **not** demonstrate that arbitrary 4-person subsets can sign.

The companion reference model now explicitly tests:

```text
1,2,3,4   PASS
1,2,4,5   PASS
1,3,4,5   PASS
2,3,4,5   PASS
1,2,3,4,5 PASS
```

and rejects:

```text
1,2,3     FAIL: not enough signers
```

This is a much better threshold test.

---

## 23. Issue 7: `assert` is being used as protocol validation

The source includes checks such as:

```python
assert m and ...
```

and:

```python
assert G * signer.z == ...
```

Assertions are useful while debugging.

They should not be the security boundary of a cryptographic protocol.

In Python-family environments, assertions can be disabled. More importantly,
an explicit protocol failure deserves an explicit error path.

Prefer:

```python
if not valid:
    raise ValueError("invalid signature share")
```

or a typed protocol error.

**Verdict:** engineering hardening required.

---

## 24. Issue 8: empty messages are rejected accidentally

The line:

```python
assert m and ...
```

means:

```python
m = b""
```

fails.

But an empty byte string is a perfectly legitimate message for a signature
scheme.

Message validation should validate **type and encoding**, not Python
truthiness.

**Verdict:** small real bug.

---

## 25. Issue 9: commitment-list encoding is not canonical enough

The source serializes each tuple with:

```python
str(_id).encode() + encode_point(Di) + encode_point(Ei)
```

The point encodings are fixed-length compressed secp256k1 encodings, which is
nice.

The identifier is a decimal ASCII string:

```text
1
2
10
11
...
```

That is not a canonical scalar encoding and has variable length.

A robust implementation should encode identifiers as fixed-width scalars or use
an unambiguous framed encoding.

RFC 9591 specifies canonical ciphersuite serialization for this reason.

**Verdict:** harmless in this five-party demo, inappropriate as a general wire
format.

---

## 26. Issue 10: randomness is educational, not production FROST randomness

The original helper is:

```python
def sample():
    return randrange(2, q-1)
```

There are two issues.

First, the range excludes valid nonzero scalars such as \(1\) and \(q-1\).
That is a tiny statistical issue in a field this large, but unnecessary.

Second, more importantly, RFC 9591 defines nonce generation so that fresh
randomness is hashed together with the signing share. This hedges against some
RNG failures and provides the ciphersuite's required domain separation.

For a classroom PoC, direct random nonzero scalars are understandable.
For production, use the specified nonce-generation procedure.

**Verdict:** educational simplification, not a reason the demo fails.

---

## 27. Issue 11: multi-dealer DKG is outside the RFC signing core

It would be easy to look at the file name and conclude:

> "This entire script is RFC 9591 FROST."

That is too strong.

The signing phase closely follows the FROST construction. The preceding
multi-dealer DKG is an additional protocol layer.

RFC 9591 gives key-generation background and a trusted-dealer reference method,
but interoperable deployment of an actual distributed DKG requires its own
protocol definition:

- authenticated channels;
- consistent broadcast;
- complaint handling;
- qualification/disqualification;
- session identifiers;
- transcript binding; and
- recovery/abort policy.

The CryptoCave threshold series covers those separately.

**Verdict:** good educational composition, not an RFC-defined end-to-end DKG +
FROST stack.

---

# Part VI — The audited rewrite

## 28. Preserve the original first

The exact uploaded program is retained unchanged as:

```text
experiments/threshold-cryptography/frost-sage-poc/
└── original-poc.sage
```

We never want an audit to destroy the artifact being audited.

The same directory contains:

```text
audited-poc.sage
reference_model.py
README.md
```

---

## 29. What `audited-poc.sage` changes

The hardened educational rewrite keeps the same architecture but adds:

### Explicit scalar normalization

Every scalar state is kept in:

\[
\mathbb Z_q.
\]

For example:

```python
z_i = scalar(
    d + e * rho_i + lambda_i * s_i * c
)
```

and:

```python
z = scalar(sum(shares.values()))
```

### Explicit configuration

Participants receive:

```python
Participant(identifier, threshold, participant_count)
```

rather than reading hidden module globals.

### Abort semantics

Invalid PoK, invalid Feldman share, invalid signature share, identity commitment,
or insufficient signer count raises an error immediately.

### Arbitrary signer subsets

The API becomes:

```python
frost.sign(message, signer_ids)
```

instead of always choosing the first `a` parties.

### Consumed nonce state

A nonce pair and its public commitments are consumed together.

### Final signature verification

Before returning:

\[
zG\stackrel{?}{=}R+cY.
\]

### Better transcript framing

The teaching transcript now includes the group key and fixed framing.

It is intentionally still labelled **educational**, because it uses a compact
hash-to-scalar helper instead of implementing RFC 9591's full ciphersuite
`hash_to_field` machinery.

That distinction is deliberate. We should not create fake standards compliance
merely by naming our functions `H1` and `H2`.

---

# Part VII — Independent algebraic reproduction

## 30. Why add a dependency-free reference model?

This environment did not contain SageMath, so simply saying:

> "the original runs on my collaborator's machine"

would not be enough for an audit.

I therefore translated the essential algorithm into a small dependency-free
Python secp256k1 model.

It independently verifies:

1. multi-dealer polynomial sharing;
2. Feldman share checks;
3. group public-key derivation;
4. participant verification shares;
5. nonce commitment pairs;
6. binding factors;
7. arbitrary threshold subsets;
8. every individual FROST signature share; and
9. the final aggregate Schnorr equation.

Run:

```bash
python experiments/threshold-cryptography/frost-sage-poc/reference_model.py
```

The audited run produced:

```text
PASS round=1 signers=[1, 2, 3, 4]
PASS round=2 signers=[1, 2, 4, 5]
PASS round=3 signers=[1, 3, 4, 5]
PASS round=4 signers=[2, 3, 4, 5]
PASS round=5 signers=[1, 2, 3, 4, 5]
PASS rejected 3-of-5 attempt: not enough signers
```

This matters because it demonstrates that the **threshold algebra itself is not
dependent on the original all-five-signers execution path**.

---

# Part VIII — Running the SageMath versions

## 31. Original

The original source imports PyCryptodome:

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Hash import SHA256, SHA512
```

so its Sage Python environment must have that package available.

Then:

```bash
sage original-poc.sage
```

The program performs key generation, precomputes enough nonce pairs for the
message list, and signs every message.

Its output prints successful participant checks and the final `(R, z)` pair for
each message.

---

## 32. Audited educational version

The hardened version removes the PyCryptodome hash dependency and uses Python's
standard `hashlib` and `secrets` in addition to Sage itself:

```bash
sage audited-poc.sage
```

It deliberately signs with different 4-of-5 subsets and verifies every final
signature before returning it.

Again, it is a **corrected teaching implementation**, not a claim of RFC 9591
wire interoperability.

---

# Part IX — What would true RFC 9591 conformance require?

## 33. Ciphersuite functions

For `FROST(secp256k1, SHA-256)`, the standard specifies ciphersuite-specific
serialization and domain-separated hash functions.

In particular, the standardized \(H_1\) and \(H_2\) are scalar-producing
hash-to-field operations rather than simply:

```python
int(SHA256(...))
```

or:

```python
int(SHA512(...)[0:32])
```

The binding-factor transcript must follow the standard's canonical structure,
and messages/commitments are hashed through the specified \(H_4\) and \(H_5\)
functions.

---

## 34. Canonical serialization

Every protocol value needs a canonical encoding:

- participant identifier;
- scalar;
- group element;
- commitment list; and
- final signature.

The original's in-memory Sage points are excellent for understanding the
mathematics but do not define an interoperable wire protocol.

---

## 35. Nonce generation

A conformant implementation should use the ciphersuite nonce-generation
procedure and enforce that every nonce pair is used at most once.

In a network system this means durable nonce state, not only `pop(0)` from a
process-local list.

A crash-recovery design must never accidentally resurrect a nonce marked as
unused before the crash.

---

## 36. Coordinator and participant validation

The coordinator must validate:

- participant identifiers;
- commitment-list order;
- duplicate identifiers;
- element deserialization;
- scalar deserialization;
- signer count;
- signature shares; and
- the final signature.

Signers must ensure they are signing the exact commitment list/message/session
that they intended.

---

## 37. Network assumptions

The one-file Sage script has no network adversary.

A distributed deployment additionally needs:

- authenticated participants;
- consistent coordinator messages;
- replay protection;
- session identifiers;
- timeout/abort behavior;
- duplicate-message handling;
- concurrency isolation; and
- durable one-time nonce management.

Those concerns are not defects in a compact mathematical PoC; they are simply
outside its model.

---

# Part X — Comparing our three Schnorr/FROST code artifacts

## 38. Broken JS Schnorr experiment

The previous case study had several direct cryptographic bugs:

- `r` was treated as a scalar;
- signer/verifier challenge transcripts differed;
- aggregate-key parity was mishandled; and
- aggregate-nonce parity was mishandled.

It was not threshold FROST.

---

## 39. This SageMath PoC

This implementation is much stronger mathematically:

- Shamir-style threshold shares exist;
- public verification shares exist;
- FROST uses two nonces;
- binding factors exist;
- Lagrange interpolation is correct;
- partial signatures satisfy the correct verification equation; and
- aggregation is mathematically correct.

The weaknesses are mainly around:

- standards transcripts;
- field canonicalization;
- failure handling;
- configuration hygiene;
- session engineering; and
- final validation.

That is why it ran reliably.

---

## 40. The validated CryptoCave FROST implementation

The next article in this series studies the larger validated implementation
already maintained in CryptoCave.

That version adds much of the engineering missing here:

- immutable group information;
- explicit signing packages;
- session identifiers;
- public transcript digests;
- commitment-reuse protection;
- one-time nonce state;
- validation boundaries;
- final verification; and
- a larger regression suite.

So these two codebases serve different educational purposes:

```text
collaborator Sage PoC
        ↓
see the mathematics in one file
        ↓
understand the exact FROST equations
        ↓
identify prototype/standards gaps
        ↓
validated engineering implementation
```

That progression is more useful than replacing the smaller code with the larger
one.

---

# Part XI — Final verdict

## 41. Is there a fatal cryptographic mistake?

**No, not in the core honest-path signing algebra.**

The central FROST equations are correctly represented.

Specifically:

\[
R_i=D_i+\rho_iE_i,
\]

\[
z_i=d_i+\rho_i e_i+\lambda_i s_i c,
\]

\[
z_iG=R_i+\lambda_i cY_i,
\]

and:

\[
z=\sum_i z_i
\]

are the right structure.

The Lagrange coefficient is also correct.

The Feldman share verification is correct.

The group key and public verification shares are derived correctly.

This is consistent with the observation that the code ran normally under honest
execution.

---

## 42. Are there real problems?

**Yes.**

The most important are:

1. protocol scalars are not explicitly reduced modulo \(q\);
2. the binding-factor and challenge functions are not the RFC 9591 secp256k1
   ciphersuite definitions;
3. the final aggregate signature is not verified;
4. invalid DKG proofs/shares do not abort;
5. configuration uses hidden globals despite class parameters;
6. the demonstration does not actually exercise the 4-of-5 property;
7. security validation uses `assert`;
8. nonce generation is not the RFC nonce-generation procedure;
9. commitment-list encoding is not canonical enough for a wire protocol; and
10. signing-session state is not isolated for concurrency/crash recovery.

These are significant if the goal is deployment or RFC conformance.

They do **not** invalidate the main pedagogical value of the implementation.

---

## 43. The most useful lesson

This program is a good example of an important distinction in cryptographic
engineering:

> **A protocol can have the correct equations and still be incomplete as a
> secure distributed system.**

The equations tell us why the signature is mathematically possible.

The engineering layers tell us whether:

- everyone hashed the same transcript;
- values were encoded canonically;
- invalid actors were excluded;
- nonces can never repeat;
- sessions cannot be mixed;
- threshold policy is enforced; and
- the final output is actually validated.

Both levels matter.

For studying FROST from first principles, the collaborator's compact SageMath
program is valuable precisely because the equations are visible.

For implementation work, the audited version and the following RFC/conformance
articles show what must be added around those equations.

---

## Reproducibility checklist

From the repository root:

```bash
python experiments/threshold-cryptography/frost-sage-poc/reference_model.py
```

With SageMath installed:

```bash
cd experiments/threshold-cryptography/frost-sage-poc
sage original-poc.sage
sage audited-poc.sage
```

Then continue with the next articles in the series:

1. the validated educational FROST implementation;
2. nonce/replay/failure boundaries;
3. the RFC 9591 conformance map; and
4. the production security boundary.

The objective is not merely to obtain the word `PASS`.

It is to know exactly **why** the equation passes, **what assumptions made the
run succeed**, and **which guarantees are still missing** before the code leaves
the laboratory.
