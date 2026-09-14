# Qualification, public-key derivation, and audit

The two central DKG consistency questions are: “Did everyone include the same
dealer contributions?” and “Does the public key correspond to the distributed
private shares?” Version 0.4 makes both checks explicit.

## 1. Why the qualified set is part of the key

Consider two honest participants using different sets $Q$ and $Q'$. Their local
key-share polynomials are

$$
F(X)=\sum_{i\in Q}f_i(X)
$$

and

$$
F'(X)=\sum_{i\in Q'}f_i(X).
$$

Even when every individual dealer sharing is valid, $F$ and $F'$ generally have
different constants, shares, and public keys. A participant identifier alone is
therefore insufficient context for a key share; the DKG session and common
qualified set must also be bound.

`MultiDealerDKG` records one view for every participant. All views must equal the
computed tuple exactly. The final transcript binds that tuple, every dealer's
sub-transcript digest, both commitment vectors, and the public key.

## 2. Public key without scalar reconstruction

For dealer contribution $z_i=a_{i,0}$, the constant value commitment is

$$
Y_i=A_{i,0}=g^{z_i}.
$$

The group public key is

$$
Y=\prod_{i\in Q}Y_i
=\prod_{i\in Q}g^{z_i}
=g^{\sum_{i\in Q}z_i}
=g^x.
$$

Only group multiplication is needed. The scalar $x$ never appears as an input to
the calculation.

The final value commitment vector also verifies each distributed key share:

$$
g^{x_j}
\stackrel{?}{=}
\prod_{k=0}^{\tau-1}A_k^{j^k}.
$$

The constant entry $A_0$ is exactly $Y$.

## 3. Why the value commitments are acceptable here

Feldman commitments reveal equality and permit guessing when a committed value
has low entropy. In DKG, every honest dealer's constant and nonconstant
coefficients are sampled uniformly from the scalar field. The constant value
commitments are also required to form the public key.

This does not make the toy group secure. It explains why publishing $g^{z_i}$
has a different purpose and leakage profile than applying Feldman directly to a
password, diagnosis, pixel, or class label.

## 4. Normal path versus audit path

Normal `run()` performs:

```text
private deliveries → verification → common Q → group products → key shares
```

It never interpolates the final secret. The test suite replaces both Shamir
reconstruction methods with functions that raise an exception and confirms that
an honest DKG still completes.

`audit_reconstruct_field_element()` exists only to validate the educational
equation. Given any $\tau$ final shares, it reconstructs $x$ and checks

$$
Y\stackrel{?}{=}g^x.
$$

The method is deliberately named `audit_...` and kept out of the normal example.
Real threshold signing or decryption must consume the distributed shares without
calling it.

## 5. All threshold subsets

For the 3-out-of-5 example there are

$$
\binom{5}{3}=10
$$

threshold coalitions. The tests reconstruct in audit mode from every coalition,
confirm that all ten produce the same field element, and confirm that its group
commitment equals the DKG public key.

This establishes algebraic consistency for the toy execution. It is not a
security proof against a network adversary.

## 6. Transcript fields

The public `DKGTranscript` contains:

- protocol/version and global session identifier;
- participant identifiers and threshold;
- the minimum-qualified-dealer policy;
- the common qualified set;
- every dealer's VSS digest and public commitment vectors;
- every dealer outcome and reason;
- both aggregate commitment vectors;
- the group public key.

It excludes the final private key shares and all blinding shares. The SHA-256
digest binds these public fields canonically, but it is not a digital signature.

Next: [DKG failure cases and adversarial lessons](20-dkg-failure-cases.md).
