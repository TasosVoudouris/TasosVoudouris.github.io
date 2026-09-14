---
title: "Why Threshold ECDSA Is Hard: Nonlinearity, Nonces, and Preprocessing"
description: "Derive the obstacle behind threshold ECDSA, show why naively signing with Shamir shares fails, and build the conceptual bridge from ECDSA's inverse-and-product equation to MPC, homomorphic encryption, masked factors, and preprocessing."
pubDate: "2026-09-14"
updatedDate: "2026-09-14"
topics:
  - "Threshold Cryptography"
  - "Digital Signatures"
  - "MPC"
  - "Implementation Security"
tags:
  - "threshold-ecdsa"
  - "ecdsa"
  - "mpc"
  - "paillier"
  - "preprocessing"
  - "nonces"
  - "masked-factors"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 19
sourcePath: "experiments/threshold-cryptography/tinysig-analysis"
status: "Reviewed"
draft: false
---
Threshold Schnorr is surprisingly clean. Threshold ECDSA is not.

That difference is easy to underestimate when the two schemes are viewed only
through their public APIs: both ultimately output a pair of scalars that a
normal verifier can check. Internally, however, their signing equations have
very different algebraic structure.

This chapter develops that distinction carefully. It also explains a common
implementation trap that appeared in our recovered notes: **Shamir-share the
ECDSA private key, let each share sign independently, and Lagrange-interpolate
the resulting signatures.** That construction looks plausible, but it does not
produce threshold ECDSA.

The next chapter uses these ideas to dissect the TinySig prototype line by line.

## 1. Start from ordinary ECDSA

Let an elliptic-curve subgroup have prime order $q$, generator $G$, private key
$x\in\mathbb Z_q$, and public key

$$
Y=xG.
$$

To sign a message $M$, let

$$
m=H(M)\bmod q.
$$

The signer samples a fresh nonzero nonce $k\in\mathbb Z_q^*$, computes

$$
R=kG,
$$

sets

$$
r=x(R)\bmod q,
$$

and computes

$$
s=k^{-1}(m+rx)\bmod q.
$$

The important expression is therefore

$$
\boxed{s=k^{-1}m+k^{-1}rx\pmod q.}
$$

The secret-dependent computation contains:

- an **inverse** of the nonce $k$;
- a **product** involving $k^{-1}$ and $x$; and
- a value $r$ that itself depends on the common nonce point $R=kG$.

Those operations are exactly where the distributed problem begins.

## 2. What Shamir sharing gives us

Suppose the signing secret is shared with a Shamir polynomial $f$:

$$
x_i=f(i),\qquad x=f(0).
$$

For a selected signing set $S$, Lagrange interpolation gives

$$
x=\sum_{i\in S}\lambda_i x_i\pmod q.
$$

This is a **linear** identity. It means any expression that is linear in $x$
can often be distributed elegantly.

For example,

$$
cx=c\sum_i\lambda_i x_i
   =\sum_i c\lambda_i x_i.
$$

That is why Schnorr is naturally threshold-friendly.

But Shamir sharing does not magically provide

$$
[x^{-1}],
$$

nor does it let parties locally multiply two independently shared secrets and
obtain a sharing of their product without additional machinery.

In general,

$$
\left(\sum_i a_i\right)^{-1}
\neq
\sum_i a_i^{-1}
$$

and

$$
\left(\sum_i a_i\right)
\left(\sum_i b_i\right)
\neq
\sum_i a_i b_i.
$$

Those two facts are the essence of the threshold-ECDSA difficulty.

## 3. The tempting but wrong construction

The uploaded `Threshold Python.zip` contained a useful anti-example in
`tECDSA/tECDSA.py`. Its intended workflow is approximately:

1. generate an ordinary ECDSA private key $x$;
2. Shamir-share $x$ into $x_i$;
3. treat each $x_i$ as an independent ECDSA private key;
4. ask each participant to produce a normal ECDSA signature;
5. interpolate the resulting $s_i$ values using the same Lagrange coefficients.

The code even contains the comment:

```text
In ECDSA, r is the same across partial signatures
```

but the implementation does not create a shared nonce. Each invocation of the
ECDSA library signs independently, so participant $i$ effectively obtains a
fresh nonce $k_i$ and therefore

$$
R_i=k_iG,
\qquad
r_i=x(R_i)\bmod q.
$$

Its signature scalar is

$$
s_i=k_i^{-1}(m+r_i x_i)\pmod q.
$$

Now interpolate:

$$
\sum_i\lambda_i s_i
=
\sum_i\lambda_i k_i^{-1}m
+
\sum_i\lambda_i k_i^{-1}r_i x_i.
$$

There is no reason for this to equal

$$
k^{-1}\left(m+r\sum_i\lambda_i x_i\right)
$$

for any common ECDSA nonce $k$ and common $r$.

The failure is structural, not a Python bug.

### What would have to be common?

A threshold ECDSA protocol needs the participants to cooperate on a nonce $k$
so that everyone is contributing to the same

$$
R=kG
$$

and therefore the same

$$
r=x(R)\bmod q.
$$

But even after obtaining a distributed $k$, the parties still need the inverse
$k^{-1}$ and the product $k^{-1}x$ without reconstructing either $k$ or $x$.
That requires secure multiparty computation or equivalent preprocessing.

## 4. Contrast with threshold Schnorr

Ordinary Schnorr can be written as

$$
z=r+cx\pmod q,
$$

where $R=rG$ and $c$ is the challenge.

With Shamir shares $x_i$ and signer-specific nonces $r_i$, a threshold response
can take the form

$$
z_i=r_i+c\lambda_i x_i.
$$

Adding the shares gives

$$
z=\sum_i z_i
 =\sum_i r_i+c\sum_i\lambda_i x_i
 =r+cx.
$$

Everything in the secret key term is linear.

FROST has additional machinery—two nonces, binding factors, commitment lists,
participant validation, nonce lifecycle rules—but the core response remains
linear in the secret shares.

ECDSA instead asks the MPC layer to realize

$$
k^{-1}m+k^{-1}rx.
$$

That is a qualitatively different task.

| Property | Schnorr / FROST | ECDSA |
|---|---|---|
| Secret-key term | Linear | Multiplied by $k^{-1}r$ |
| Nonce operation | Addition | Inversion + multiplication |
| Local share responses | Naturally additive | Not naturally additive |
| Main distributed tool | Shamir interpolation | MPC / HE / MtA / preprocessing |
| Naive interpolation of ordinary signatures | Not the construction, but linear structure helps | Fundamentally invalid |

## 5. Why multiplication of shares is expensive

Suppose two secrets are additively shared:

$$
a=\sum_i a_i,
\qquad
b=\sum_i b_i.
$$

Their product is

$$
ab
=
\left(\sum_i a_i\right)
\left(\sum_j b_j\right)
=
\sum_i a_i b_i
+
\sum_{i\neq j}a_i b_j.
$$

The cross terms are missing if every participant simply multiplies its own
shares locally.

This is why secure multiplication commonly introduces extra tools such as:

- Beaver-style correlated randomness;
- multiplication-to-addition (MtA) protocols;
- additively homomorphic encryption such as Paillier;
- oblivious-transfer-based MPC; or
- specialized preprocessing that turns the online phase into mostly linear
  operations.

Threshold ECDSA protocols differ substantially in how they solve this problem.
One should therefore avoid talking about “the threshold ECDSA protocol” as if
there were one obvious Shamir extension of ECDSA.

## 6. A useful change of viewpoint: sum of products

Rewrite ECDSA as

$$
s=
\underbrace{k^{-1}m}_{\text{term 1}}
+
\underbrace{k^{-1}rx}_{\text{term 2}}.
$$

This form is useful because it looks like a small arithmetic circuit: two
products followed by an addition.

The TinySig technical report takes exactly this viewpoint. Instead of trying to
make ECDSA itself linear, it uses an MPC primitive for evaluating
**sum-of-products expressions** with preprocessing.

The key idea is to represent a nonzero secret $a\in\mathbb Z_q^*$ as a masked
factor

$$
\langle a\rangle_{\lambda}
=
 a h^{-\lambda}\pmod q,
$$

where $h$ generates the multiplicative group $\mathbb Z_q^*$ and the mask
exponent

$$
\lambda\in\mathbb Z_{q-1}
$$

is additively shared.

Why exponent arithmetic modulo $q-1$? Because Fermat's theorem makes the
exponent group of $\mathbb Z_q^*$ live modulo $q-1$.

## 7. The masked-factor trick

Suppose

$$
\langle a\rangle_{\lambda_a}=a h^{-\lambda_a}
$$

and

$$
\langle b\rangle_{\lambda_b}=b h^{-\lambda_b}.
$$

Then their product is

$$
\langle a\rangle_{\lambda_a}
\langle b\rangle_{\lambda_b}
=
 ab h^{-(\lambda_a+\lambda_b)}.
$$

Multiplication of masked values corresponds to **addition of mask exponents**.
That is the algebraic feature TinySig exploits.

Even inversion behaves conveniently:

$$
\left(\langle k\rangle_{\lambda_k}\right)^{-1}
=
\left(k h^{-\lambda_k}\right)^{-1}
=
 k^{-1}h^{\lambda_k}.
$$

This is a representation of $k^{-1}$ whose mask exponent has changed sign.
The hard inverse can therefore be performed locally on the opened masked factor
without exposing the underlying nonce $k$.

That is much more subtle than “invert each additive share.”

## 8. Client-server preprocessing

The Nillion threshold-ECDSA report uses a client-server model. At a high level:

- a set of signers stores masked/encrypted state associated with the signing key;
- the client owns the secret key of an additively homomorphic encryption scheme;
- signer-side preprocessing can happen before the message is known;
- a short client preprocessing step reveals only mask combinations needed by the
  client; and
- the online phase requires no signer-to-signer communication in the model.

The report separates signing into three phases:

1. **signer preprocessing**;
2. **client preprocessing**; and
3. **online signing**.

The design target is therefore not merely “threshold ECDSA.” It is specifically
threshold ECDSA with a very light message-dependent online path.

## 9. Why Paillier appears

TinySig uses Paillier encryption because it is additively homomorphic.
Schematically,

$$
\operatorname{Enc}(a)\oplus\operatorname{Enc}(b)
=
\operatorname{Enc}(a+b)
$$

and multiplying a ciphertext by a public scalar gives an encryption of a
scaled plaintext.

This lets nodes manipulate encrypted mask-share terms while only the client can
decrypt the final combinations.

It is important not to confuse the roles:

- elliptic-curve arithmetic defines the **ECDSA public key and nonce point**;
- arithmetic modulo $q$ defines the **ECDSA signature scalar equation**;
- arithmetic modulo $q-1$ tracks **mask exponents**;
- Paillier protects selected exponent/share values from the signers while
  retaining linear operations on ciphertexts.

Four different algebraic domains are therefore visible in a small prototype.
That alone explains why the code can initially feel much harder to read than a
FROST implementation.

## 10. What TinySig is trying to avoid

A straightforward generic MPC implementation could evaluate the ECDSA equation,
but the online cost may involve multiple rounds among signers.

TinySig's masked-factor/preprocessing strategy moves much of the difficult work
earlier. The report's online phase is designed so that the client sends the
message-dependent masked value and the signers can locally evaluate their
pieces without communicating with one another before returning them.

That design should be read as a **preprocessing tradeoff**:

$$
\text{more prepared correlated state}
\quad\Longrightarrow\quad
\text{less interaction when the message arrives}.
$$

The prepared state must therefore be generated, protected, consumed correctly,
and not accidentally reused.

## 11. A security-engineering warning about nonces

ECDSA nonce mistakes are catastrophic even without threshold cryptography.
Threshold implementations add more nonce-related state:

- nonce shares;
- masks for nonce-related quantities;
- encrypted preprocessing material;
- session identifiers; and
- deletion/one-time-use requirements.

A correct algebraic derivation is not enough. A production threshold-ECDSA
implementation also needs robust guarantees around:

- cryptographically secure randomness;
- atomic consumption of preprocessing records;
- crash recovery without nonce reuse;
- participant/session binding;
- authenticated messages;
- malicious-party checks;
- side-channel resistance; and
- explicit abort semantics.

This is one reason educational prototypes must not be treated as wallet-ready
implementations.

## 12. What the recovered `tECDSA.py` teaches us

The failed toy implementation is actually worth keeping as a lesson because it
exposes three misconceptions clearly.

### Misconception 1: a key share is itself a signing key

A Shamir share $x_i$ is an encoding of one point on a secret-sharing polynomial.
It is not automatically a private key for a compatible partial-signature
scheme.

### Misconception 2: ECDSA signatures interpolate like Shamir shares

A normal ECDSA signature is not a linear share of another ECDSA signature.
Lagrange coefficients reconstruct the shared secret because the secret-sharing
polynomial is linear under interpolation. They do not create linearity in an
arbitrary cryptographic algorithm.

### Misconception 3: all participants automatically obtain the same $r$

They obtain the same $r$ only if the protocol deliberately constructs a common
nonce point $R=kG$. Independent calls to an ECDSA signing function almost
certainly use independent nonces and independent $r$ values.

## 13. The conceptual bridge to TinySig

The transition can now be summarized as:

```text
naive idea
share x -> independently sign -> interpolate signatures
                           X invalid

actual problem
share x + jointly manage k
        + compute k^{-1}
        + compute k^{-1}x
        + preserve one common r
        + reveal neither x nor k

TinySig direction
masked factors + additive shares
        + homomorphic encryption
        + signer/client preprocessing
        + light online sum-of-products evaluation
```

The next chapter follows that construction through the actual TinySig API and
through the recovered repository snapshot.

## 14. Takeaways

The key points to retain are:

1. Shamir sharing only gives linear reconstruction; ECDSA's signing equation is
   not linear in the distributed secrets.
2. Independent ECDSA signatures under key shares cannot be combined by
   interpolating their $s$ values.
3. A valid threshold protocol must coordinate the nonce and securely realize
   inversion and multiplication involving shared secrets.
4. Schnorr/FROST is algebraically friendlier because its response equation is
   linear in the signing key.
5. TinySig attacks the ECDSA difficulty with masked multiplicative factors,
   additive secret sharing, homomorphic encryption, and preprocessing.
6. Understanding those layers first makes the TinySig source code far less
   mysterious.

## References

- Nillion, *Technical Report on Threshold ECDSA in the Preprocessing Setup*, 2023: <https://nillion.pub/threshold-ecdsa-preprocessing-setup.pdf>
- TinySig 0.1.0 package: <https://pypi.org/project/tinysig/>
- CryptoCave, *Schnorr Algebra and Threshold Interpolation*.
- CryptoCave, *FROST and RFC 9591: The Two-Round Threshold Schnorr Protocol*.
