# From Shamir Sharing to Verifiable Secret Sharing

Ordinary Shamir sharing assumes that the dealer honestly constructs one
polynomial and privately gives every participant the corresponding evaluation.
Its privacy and reconstruction arguments are correct under that assumption, but
the shares contain no evidence that the dealer behaved honestly.

Suppose the intended polynomial is

$$
f(X)=s+a_1X+\cdots+a_{\tau-1}X^{\tau-1}.
$$

A malicious or faulty dealer can instead send values that do not lie on one
degree-at-most-$\tau-1$ polynomial. Each participant sees only its own value and
cannot detect the global inconsistency. The problem may appear only later, when
honest coalitions reconstruct different values or fail to reconstruct at all.

## What VSS adds

Verifiable secret sharing adds a public consistency mechanism to the private
distribution of shares. Informally, after an accepted sharing phase:

1. honest parties' accepted shares are bound to one well-defined secret;
2. a faulty dealer cannot make different honest reconstruction coalitions open
   different values without being detected or disqualified;
3. unauthorized coalitions still do not learn the secret beyond the stated
   security model.

These statements are protocol properties, not merely properties of a formula.
They depend on the adversary model, communication assumptions, broadcast
mechanism, complaint rules, and reconstruction procedure.

## The local consistency problem

The first step is to let participant $P_i$ verify a relation of the form

$$
\operatorname{Commit}(f(x_i))
=
\operatorname{EvaluateCommitments}(x_i).
$$

Feldman VSS realizes this relation with exponentiation in a cyclic group. The
participant verifies its share without learning the other shares and without
the dealer publishing the polynomial coefficients.

Version 0.2 implements this local verification equation correctly and connects
it directly to the Version 0.1 Shamir code. It also simulates filtering invalid
shares before reconstruction.

## What Version 0.2 deliberately does not claim

A local Python process gives every participant the same commitment object by
construction. A real protocol must ensure that a malicious dealer cannot send
different commitment vectors to different participants. It must also specify
what happens when a participant complains, when a dealer refuses to answer,
when a participant lies about receiving an invalid share, or when too many
parties abort.

Therefore, Version 0.2 is the **Feldman sharing and verification layer** needed
inside a VSS protocol. The network-level agreement and complaint layer is the
next step, not an unstated assumption.

Next: [Feldman verifiable secret sharing](09-feldman-vss.md).
