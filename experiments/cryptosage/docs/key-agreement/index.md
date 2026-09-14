---
sidebar_position: 7
---

# Elliptic-curve key agreement

## ECMQV

MQV combines each party's static and ephemeral private contributions. If
Alice has $(a,A)$ and ephemeral $(x,X)$, define

$$
s_A=x+\bar{x}a\pmod n,
$$

where $\bar{x}$ is a reduction derived from the $x$-coordinate of $X$. Alice
computes

$$
Z_A=hs_A(Y+\bar{y}B),
$$

and Bob symmetrically computes

$$
Z_B=hs_B(X+\bar{x}A).
$$

The demo asserts $Z_A=Z_B$ and derives a transcript-bound key. The original file
called functions before defining them and relied on assignments to local
variables as if they were shared state; the reviewed code passes all state
explicitly.

## STS-inspired key confirmation

The supplied “STS” program did not contain signatures or long-term
authentication keys. It therefore could not provide Station-to-Station
authentication and was vulnerable to an active man-in-the-middle.

The reviewed file accurately presents the retained idea: two peers perform
ephemeral ECDH and exchange direction-separated HMAC confirmation tags. This
confirms possession of the same ephemeral secret, but it does not establish who
the peers are. Implementing actual STS requires signatures over the ephemeral
exchange and validated long-term public keys.
