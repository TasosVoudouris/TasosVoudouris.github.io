---
title: "Authenticated Secret Sharing: The SPDZ MAC Invariant"
description: "Explain the global MAC key behind SPDZ authenticated shares, derive local MAC shares and opening checks, and show why a Beaver-triple toy is not yet maliciously secure SPDZ."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Secret Sharing"
  - "Cryptographic Engineering"
tags:
  - "spdz"
  - "authenticated-secret-sharing"
  - "information-theoretic-mac"
  - "malicious-security"
  - "mac-check"
difficulty: "Advanced"
status: "Validated"
series: "Secure Multiparty Computation"
seriesOrder: 3
sourcePath: "experiments/mpc/spdz-mac-toy"
draft: false
---
The recovered `SPDZprotocol.md` correctly introduced additive shares and Beaver triples, but then called the resulting passive toy **SPDZ**. That skips the property that makes SPDZ qualitatively different: values are not merely shared; they are **authenticated while shared**.

## 1. The global MAC key

Let the parties jointly hold a secret global authentication key

$$
\alpha.
$$

No single party should learn the whole $\alpha$. Instead it is itself shared:

$$
\alpha=\sum_i\alpha_i.
$$

A secret value $x$ is represented by value shares

$$
x=\sum_i x_i
$$

and MAC shares

$$
\gamma=\sum_i\gamma_i
$$

such that

$$
\boxed{\gamma=\alpha x.}
$$

This invariant is the heart of SPDZ-style authenticated sharing.

## 2. Why authentication helps

Without authentication, a malicious party opening $x$ can send

$$
x_i'\ne x_i
$$

and bias the reconstructed value.

With authenticated shares, changing the opened value also requires changing the corresponding MAC relation consistently with the unknown global key $\alpha$.

The attacker does not know enough about $\alpha$ to forge that relation except with small probability determined by the field size and exact checking procedure.

## 3. Linearity survives

Authentication is compatible with the linear operations we want.

If

$$
\gamma_x=\alpha x
$$

and

$$
\gamma_y=\alpha y,
$$

then

$$
\gamma_x+\gamma_y=\alpha(x+y).
$$

Likewise, for public $c$:

$$
c\gamma_x=\alpha(cx).
$$

Therefore additions and public-scalar multiplications remain local on both the value shares and the MAC shares.

## 4. Opening an authenticated value

Conceptually, parties reveal their $x_i$ shares and reconstruct

$$
x=\sum_i x_i.
$$

They must then check that their MAC shares are consistent with that public $x$ and the shared MAC key.

A naive educational check could reconstruct

$$
\gamma=\sum_i\gamma_i
$$

and $\alpha$, then test $\gamma=\alpha x$.

But reconstructing $\alpha$ would destroy the long-term authentication key. Real SPDZ protocols therefore perform a **distributed MAC check** without revealing $\alpha$.

Our companion code deliberately has both modes:

- a transparent centralized check to expose the invariant;
- a warning that this is not the production distributed MAC-check protocol.

## 5. Authenticated Beaver triples

For multiplication, preprocessing must provide not merely

$$
[a],[b],[c],\qquad c=ab,
$$

but authenticated sharings of those values under the same global MAC key.

Then the online Beaver computation preserves authenticated shares of the product.

If preprocessing is maliciously generated, additional checks are needed to ensure the triple relation is correct.

## 6. Why the recovered "SPDZ" toy was only a precursor

The old document used:

- two-party additive sharing;
- a trusted crypto provider;
- Beaver triples;
- honest-but-curious parties.

That is a perfectly useful **preprocessing-model MPC toy**.

But it omitted:

- global MAC-key shares;
- MAC shares attached to every secret;
- authenticated openings;
- final MAC checks;
- malicious preprocessing validation.

Calling that code "SPDZ" hid exactly the security machinery students need to understand.

## 7. Security is not a boolean label

It is better to describe the construction in layers:

| Layer | Property |
|---|---|
| additive sharing | privacy against non-colluding observers |
| Beaver triple | efficient private multiplication in preprocessing model |
| authenticated shares | detect inconsistent malicious openings |
| checked triples | prevent malformed preprocessing |
| distributed MAC check | preserve global MAC-key secrecy |
| full protocol | combines these with network/session/abort rules |

## 8. Takeaway

SPDZ is not "secret sharing plus triples".

The defining mental model is:

$$
\boxed{\text{every secret value carries an authentication relation under a hidden global MAC key}.}
$$

That invariant is what lets the online arithmetic remain efficient while moving from passive to active security.
