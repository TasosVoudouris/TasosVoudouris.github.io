---
title: "From Verifiable Secret Sharing to Distributed Key Generation"
description: "Explain what a DKG must produce, why ordinary sharing is insufficient, how multi-dealer aggregation removes a trusted dealer, and where historical pitfalls enter."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Threshold Cryptography"
  - "Secret Sharing"
  - "Public-Key Cryptography"
tags:
  - "vss"
  - "dkg"
  - "threshold-cryptography"
difficulty: "Advanced"
series: "Threshold Cryptography Engineering"
seriesOrder: 9
sourcePath: "experiments/threshold-cryptography/validated-frost-v0.5"
status: "Validated"
draft: false
---
Verifiable secret sharing still begins with one dealer who knows the secret.
Distributed key generation removes that point of trust: several participants
contribute randomness, and their accepted contributions define a secret key that
is already shared when the protocol ends.

Version 0.4 makes this transition visible without claiming a production DKG.

## 1. What a DKG should produce

For a prime-order group $G=\langle g\rangle$ of order $q$, a successful DKG
should produce:

- one public key $Y=g^x$ known to everyone;
- one private Shamir key share $x_j=F(j)$ for every participant $P_j$;
- one degree-at-most-$(\tau-1)$ polynomial $F$ with $F(0)=x$;
- no normal protocol step that reconstructs or gives one party the scalar $x$.

The classical security requirements described by Gennaro, Jarecki, Krawczyk,
and Rabin include a unique shared secret, agreement on the corresponding public
key, and the required distribution of the generated secret. Their analysis also
shows why apparently natural “everyone shares a random value and we add them”
protocols require careful commitment and qualification ordering.

Primary reference: Rosario Gennaro, Stanisław Jarecki, Hugo Krawczyk, and Tal
Rabin, “Secure Distributed Key Generation for Discrete-Log Based
Cryptosystems,” *Journal of Cryptology* 20, 51–83 (2007),
[DOI: 10.1007/s00145-006-0347-3](https://doi.org/10.1007/s00145-006-0347-3).

## 2. Why ordinary Shamir sharing is insufficient

Suppose every $P_i$ privately sends values from a polynomial $f_i$. If those
values are accepted without VSS, different recipients may hold inconsistent
points. Adding them locally would produce incompatible final shares.

Each dealer contribution therefore needs the Version 0.3 properties:

1. one committed polynomial per dealer;
2. one explicitly labelled private delivery per recipient;
3. participant verification;
4. complaints and a qualification outcome;
5. a common view of the public commitments and dealer result.

DKG does not replace VSS. It composes several VSS instances.

## 3. Multi-dealer aggregation

Every participant $P_i$ acts as a dealer and samples a random polynomial

$$
f_i(X)=a_{i,0}+a_{i,1}X+\cdots+a_{i,\tau-1}X^{\tau-1}.
$$

Let $Q$ be the common set of qualified dealers. Define

$$
F(X)=\sum_{i\in Q}f_i(X)\pmod q.
$$

The distributed secret is the constant term

$$
x=F(0)=\sum_{i\in Q}a_{i,0}\pmod q,
$$

and participant $P_j$ obtains it in shared form by adding only its own received
values:

$$
x_j=F(j)=\sum_{i\in Q}f_i(j)\pmod q.
$$

No interpolation occurs. The key is born distributed.

## 4. Why at least one honest contribution matters

If one included dealer selects $a_{i,0}$ uniformly and keeps it unknown from the
adversary while the qualified set is fixed independently of its value, then its
sum with any fixed adversarial contributions remains uniform in $\mathbb F_q$.

This statement has conditions. An adversary must not inspect contributions and
then selectively decide which honest dealer is included. The parties must also
agree on the same set $Q$. These are protocol properties, not consequences of
the final addition equation.

The Version 0.4 `minimum_qualified_dealers` setting is only an educational
availability policy. Requiring three dealer sessions to survive does not prove
that one of those dealers is honest, nor does it define a Byzantine fault model.

## 5. The historical pitfall

A basic joint-Feldman construction publishes $g^{a_{i,0}}$ while forming the
qualified set. The GJKR analysis shows that the resulting key distribution can
be biased by an adversary even though the output secret may remain difficult to
compute. This distinction matters: “the attacker does not know the key” is not
the same claim as “the key has the required uniform distribution.”

The fuller construction first uses hiding Pedersen VSS commitments to fix the
dealer contributions and qualified set, then extracts the public-key information
through a Feldman-style round tied to the same polynomials.

## 6. Version 0.4 scope

Version 0.4 follows that high-level separation:

1. hidden Pedersen qualification;
2. one agreed qualified set;
3. value-commitment verification for the same secret shares;
4. aggregation of shares, commitments, and public key.

It does not reproduce the complete GJKR fault model, broadcasts, proof, or
public reconstruction after a value-round complaint. A late value-round failure
causes conservative global abort.

This means the code is an executable map of the protocol dependencies, not a
drop-in implementation of the paper.

Next: [The Version 0.4 multi-dealer construction](/series/threshold-cryptography-engineering/).
