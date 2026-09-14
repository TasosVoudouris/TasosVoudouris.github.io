# Consistency and Robust Reconstruction

Shamir shares form a Reed–Solomon codeword: they are evaluations of a bounded-
degree polynomial at public points. This coding interpretation explains both
availability and robustness.

Let the reconstruction threshold be $\tau$, let $e$ received shares be wrong,
and let $s$ expected shares be missing. Unique decoding requires

$$
n \geq \tau + 2e + s.
$$

Equivalently, among the shares that actually arrive, at least $\tau+2e$ are
needed to correct $e$ unknown errors. One erasure costs one unit of redundancy;
one unknown error costs two because the decoder must both locate and correct it.

For the Version 0.1 parameters $n=10$ and $\tau=5$:

- with no missing shares, at most two bad shares can be uniquely corrected;
- with one missing share, at most two bad shares still fit exactly at the bound;
- with two missing shares, at most one bad share can be corrected.

## Detection versus correction

Exactly five received shares always interpolate a degree-four polynomial. There
is no way to tell from those five values alone whether one was corrupted.

With a sixth share, Version 0.1 can interpolate from five and verify whether the
sixth lies on the same polynomial. This detects inconsistency but does not by
itself identify which participant was wrong.

## The educational decoder

`robust_reconstruct` tries every threshold-size subset, evaluates the candidate
polynomial against all received shares, and keeps the unique polynomial with
enough support. This is easy to inspect and works for the small ten-party
example.

It is combinatorial rather than scalable. Later versions should use a genuine
Reed–Solomon decoder, such as a Berlekamp–Welch-style formulation, and should
separate errors, erasures, complaints, and authenticated protocol messages.

## Robust reconstruction is not VSS

Error correction handles malformed values at reconstruction time. It does not
prove that the original dealer distributed consistent shares, and it does not
bind a participant to a share during a network protocol.

Verifiable secret sharing adds commitments and verification during sharing.
Authenticated communication binds protocol messages to participants and
sessions. Robust reconstruction, VSS, and transport authentication solve
different problems and are all needed in stronger systems.

Next: [Packed ramp sharing and the NTT](06-packed-ramp-sharing-and-ntt.md).
